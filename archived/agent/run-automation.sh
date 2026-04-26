#!/bin/bash

# =============================================================================
# run-automation.sh - Automated Task Runner for CS2 Monitor
# =============================================================================
# This script runs Claude Code multiple times in a loop to automatically
# complete tasks defined in task.json.
#
# Usage: ./run-automation.sh <number_of_runs>
# Example: ./run-automation.sh 5
#
# WARNING: This mode is the most dangerous and prone to wasting resources.
# Only use it when you are away from the computer and want the AI to work.
# =============================================================================

set -e

# Colors for logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Detect platform and set Python path for venv
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    VENV_PYTHON=".venv/Scripts/python.exe"
else
    VENV_PYTHON=".venv/bin/python"
fi

# Log file
LOG_DIR="./automation-logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/automation-$(date +%Y%m%d_%H%M%S).log"

# Function to log messages
log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" >> "$LOG_FILE"

    case $level in
        INFO)
            echo -e "${BLUE}[INFO]${NC} ${message}"
            ;;
        SUCCESS)
            echo -e "${GREEN}[SUCCESS]${NC} ${message}"
            ;;
        WARNING)
            echo -e "${YELLOW}[WARNING]${NC} ${message}"
            ;;
        ERROR)
            echo -e "${RED}[ERROR]${NC} ${message}"
            ;;
        PROGRESS)
            echo -e "${CYAN}[PROGRESS]${NC} ${message}"
            ;;
    esac
}

# Function to count remaining tasks
count_remaining_tasks() {
    if [ -f "task.json" ]; then
        local count=$(grep -c '"passes": false' task.json 2>/dev/null || echo "0")
        echo "$count"
    else
        echo "0"
    fi
}

# Function to check if environment is ready
check_environment() {
    if [ ! -f "task.json" ]; then
        log "ERROR" "task.json not found! Please run this script from the project root."
        exit 1
    fi

    if [ ! -f "CLAUDE.md" ]; then
        log "ERROR" "CLAUDE.md not found! Please run this script from the project root."
        exit 1
    fi

    if ! command -v claude &> /dev/null; then
        log "ERROR" "claude command not found. Please install Claude Code CLI."
        exit 1
    fi
}

# Check if number argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <number_of_runs>"
    echo "Example: $0 5"
    exit 1
fi

# Validate input is a number
if ! [[ "$1" =~ ^[0-9]+$ ]]; then
    echo "Error: Argument must be a positive integer"
    exit 1
fi

TOTAL_RUNS=$1

# Banner
echo ""
echo "========================================"
echo "  Claude Code Automation Runner"
echo "  Project: CS2 Monitor"
echo "========================================"
echo ""

# Pre-flight checks
check_environment

log "INFO" "Starting automation with $TOTAL_RUNS runs"
log "INFO" "Log file: $LOG_FILE"
log "INFO" "Python venv: $VENV_PYTHON"

# Initial task count
INITIAL_TASKS=$(count_remaining_tasks)
log "INFO" "Tasks remaining at start: $INITIAL_TASKS"

if [ "$INITIAL_TASKS" -eq 0 ]; then
    log "SUCCESS" "All tasks already completed!"
    exit 0
fi

# Main loop
for ((run=1; run<=TOTAL_RUNS; run++)); do
    echo ""
    echo "========================================"
    log "PROGRESS" "Run $run of $TOTAL_RUNS"
    echo "========================================"

    # Check remaining tasks before this run
    REMAINING=$(count_remaining_tasks)

    if [ "$REMAINING" -eq 0 ]; then
        log "SUCCESS" "All tasks completed! No more tasks to process."
        log "INFO" "Automation finished early after $((run-1)) runs"
        exit 0
    fi

    log "INFO" "Tasks remaining before this run: $REMAINING"

    # Run timestamp for this iteration
    RUN_START=$(date +%s)
    RUN_LOG="$LOG_DIR/run-${run}-$(date +%Y%m%d_%H%M%S).log"

    log "INFO" "Starting Claude Code session..."
    log "INFO" "Run log: $RUN_LOG"

    # Create a temporary file with the prompt
    PROMPT_FILE=$(mktemp)
    cat > "$PROMPT_FILE" << 'PROMPT_EOF'
IMPORTANT: You are starting a FRESH Claude Code session with a completely clean context window. Do not assume any prior conversation history.

To understand the current project state, you MUST read the following files IN ORDER:
1. CLAUDE.md - the workflow rules you must follow
2. task.json - the list of tasks; find the next one with "passes": false
3. progress.txt - what previous sessions have done
4. git log --oneline -20 - the recent code changes

Then follow the workflow in CLAUDE.md:
1. Run ./init.sh to initialize the environment
2. Read task.json and select the next task with passes: false
3. Implement the task following all steps
4. Test thoroughly (run unit tests with pytest, use py_compile for syntax checks)
5. Update progress.txt with your work
6. Commit all changes including task.json update in a single commit

Start by reading CLAUDE.md, then task.json to find your task.
Please complete only one task in this session, and stop once you are done or if you encounter an unresolvable issue.
PROMPT_EOF

    # Run Claude with the prompt from stdin
    # Using -p for print mode (non-interactive)
    # Using --dangerously-skip-permissions to bypass all permission checks
    if claude -p \
        --dangerously-skip-permissions \
        --allowed-tools "Bash Edit Read Write Glob Grep Task WebSearch WebFetch" \
        < "$PROMPT_FILE" 2>&1 | tee "$RUN_LOG"; then

        RUN_END=$(date +%s)
        RUN_DURATION=$((RUN_END - RUN_START))

        log "SUCCESS" "Run $run completed in ${RUN_DURATION} seconds"
    else
        RUN_END=$(date +%s)
        RUN_DURATION=$((RUN_END - RUN_START))

        log "WARNING" "Run $run finished with exit code $? after ${RUN_DURATION} seconds"
    fi

    # Clean up temp file
    rm -f "$PROMPT_FILE"

    # Check remaining tasks after this run
    REMAINING_AFTER=$(count_remaining_tasks)
    COMPLETED=$((REMAINING - REMAINING_AFTER))

    if [ "$COMPLETED" -gt 0 ]; then
        log "SUCCESS" "Task(s) completed this run: $COMPLETED"
    else
        log "WARNING" "No tasks marked as completed this run"
    fi

    log "INFO" "Tasks remaining after run $run: $REMAINING_AFTER"

    # Add separator in log
    echo "" >> "$LOG_FILE"
    echo "----------------------------------------" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"

    # Small delay between runs
    if [ $run -lt $TOTAL_RUNS ]; then
        log "INFO" "Waiting 5 seconds before next run..."
        sleep 5
    fi
done

# Final summary
echo ""
echo "========================================"
log "SUCCESS" "Automation completed!"
echo "========================================"

FINAL_REMAINING=$(count_remaining_tasks)
TOTAL_COMPLETED=$((INITIAL_TASKS - FINAL_REMAINING))

log "INFO" "Summary:"
log "INFO" "  - Total runs: $TOTAL_RUNS"
log "INFO" "  - Tasks completed: $TOTAL_COMPLETED"
log "INFO" "  - Tasks remaining: $FINAL_REMAINING"
log "INFO" "  - Log file: $LOG_FILE"

if [ "$FINAL_REMAINING" -eq 0 ]; then
    log "SUCCESS" "All tasks have been completed!"
else
    log "WARNING" "Some tasks remain. You may need to run more iterations."
fi
