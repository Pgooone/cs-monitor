# =============================================================================
# run-automation.ps1 - Automated Task Runner for CS2 Monitor (Windows)
# =============================================================================
# This script runs Claude Code multiple times in a loop to automatically
# complete tasks defined in task.json.
#
# Usage: .\run-automation.ps1 -Runs <number>
# Example: .\run-automation.ps1 -Runs 5
#
# WARNING: This mode is the most dangerous and prone to wasting resources.
# Only use it when you are away from the computer and want the AI to work.
# =============================================================================

param(
    [Parameter(Mandatory=$true)]
    [int]$Runs
)

# Log setup
$LogDir = ".\automation-logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogFile = Join-Path $LogDir "automation-$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-Log {
    param(
        [string]$Level,
        [string]$Message
    )
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp [$Level] $Message" | Out-File -Append -FilePath $LogFile

    switch ($Level) {
        "INFO"     { Write-Host "[INFO] $Message" -ForegroundColor Cyan }
        "SUCCESS"  { Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
        "WARNING"  { Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
        "ERROR"    { Write-Host "[ERROR] $Message" -ForegroundColor Red }
        "PROGRESS" { Write-Host "[PROGRESS] $Message" -ForegroundColor Magenta }
    }
}

function Count-RemainingTasks {
    if (Test-Path "task.json") {
        $Count = (Select-String -Path "task.json" -Pattern '"passes": false' -AllMatches).Matches.Count
        return $Count
    }
    return 0
}

function Test-Environment {
    if (-not (Test-Path "task.json")) {
        Write-Log "ERROR" "task.json not found! Please run this script from the project root."
        exit 1
    }
    if (-not (Test-Path "CLAUDE.md")) {
        Write-Log "ERROR" "CLAUDE.md not found! Please run this script from the project root."
        exit 1
    }
    if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
        Write-Log "ERROR" "claude command not found. Please install Claude Code CLI."
        exit 1
    }
}

# Banner
Write-Host ""
Write-Host "========================================"
Write-Host "  Claude Code Automation Runner"
Write-Host "  Project: CS2 Monitor"
Write-Host "========================================"
Write-Host ""

# Pre-flight checks
Test-Environment

Write-Log "INFO" "Starting automation with $Runs runs"
Write-Log "INFO" "Log file: $LogFile"

# Initial task count
$InitialTasks = Count-RemainingTasks
Write-Log "INFO" "Tasks remaining at start: $InitialTasks"

if ($InitialTasks -eq 0) {
    Write-Log "SUCCESS" "All tasks already completed!"
    exit 0
}

# Main loop
for ($Run = 1; $Run -le $Runs; $Run++) {
    Write-Host ""
    Write-Host "========================================"
    Write-Log "PROGRESS" "Run $Run of $Runs"
    Write-Host "========================================"

    $Remaining = Count-RemainingTasks
    if ($Remaining -eq 0) {
        Write-Log "SUCCESS" "All tasks completed! No more tasks to process."
        Write-Log "INFO" "Automation finished early after $($Run - 1) runs"
        exit 0
    }

    Write-Log "INFO" "Tasks remaining before this run: $Remaining"

    $RunStart = Get-Date
    $RunLog = Join-Path $LogDir "run-${Run}-$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

    Write-Log "INFO" "Starting Claude Code session..."
    Write-Log "INFO" "Run log: $RunLog"

    $PromptText = @"
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
"@

    # Write prompt to a temporary file because Start-Process only accepts file paths for redirection
    $PromptFile = [System.IO.Path]::GetTempFileName()
    $PromptText | Out-File -FilePath $PromptFile -Encoding UTF8

    # Run Claude with the prompt from stdin
    $Process = Start-Process -FilePath "claude" -ArgumentList "-p", "--dangerously-skip-permissions", "--allowed-tools", "Bash Edit Read Write Glob Grep Task WebSearch WebFetch" -RedirectStandardInput $PromptFile -RedirectStandardOutput $RunLog -RedirectStandardError $RunLog -PassThru -NoNewWindow
    $Process.WaitForExit()

    # Clean up temp prompt file
    Remove-Item -Path $PromptFile -Force -ErrorAction SilentlyContinue

    $RunEnd = Get-Date
    $RunDuration = [math]::Floor(($RunEnd - $RunStart).TotalSeconds)

    if ($Process.ExitCode -eq 0) {
        Write-Log "SUCCESS" "Run $Run completed in ${RunDuration} seconds"
    } else {
        Write-Log "WARNING" "Run $Run finished with exit code $($Process.ExitCode) after ${RunDuration} seconds"
    }

    # Also append run log content to main automation log for easy review
    if (Test-Path $RunLog) {
        Get-Content $RunLog | Out-File -Append -FilePath $LogFile
    } else {
        "[No run log generated]" | Out-File -Append -FilePath $LogFile
    }

    $RemainingAfter = Count-RemainingTasks
    $Completed = $Remaining - $RemainingAfter

    if ($Completed -gt 0) {
        Write-Log "SUCCESS" "Task(s) completed this run: $Completed"
    } else {
        Write-Log "WARNING" "No tasks marked as completed this run"
    }

    Write-Log "INFO" "Tasks remaining after run $Run`: $RemainingAfter"

    "" | Out-File -Append -FilePath $LogFile
    "----------------------------------------" | Out-File -Append -FilePath $LogFile
    "" | Out-File -Append -FilePath $LogFile

    if ($Run -lt $Runs) {
        Write-Log "INFO" "Waiting 5 seconds before next run..."
        Start-Sleep -Seconds 5
    }
}

# Final summary
Write-Host ""
Write-Host "========================================"
Write-Log "SUCCESS" "Automation completed!"
Write-Host "========================================"

$FinalRemaining = Count-RemainingTasks
$TotalCompleted = $InitialTasks - $FinalRemaining

Write-Log "INFO" "Summary:"
Write-Log "INFO" "  - Total runs: $Runs"
Write-Log "INFO" "  - Tasks completed: $TotalCompleted"
Write-Log "INFO" "  - Tasks remaining: $FinalRemaining"
Write-Log "INFO" "  - Log file: $LogFile"

if ($FinalRemaining -eq 0) {
    Write-Log "SUCCESS" "All tasks have been completed!"
} else {
    Write-Log "WARNING" "Some tasks remain. You may need to run more iterations."
}
