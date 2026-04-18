"""数据库表结构定义."""

# 饰品基础信息表
CREATE_ITEMS_TABLE = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_hash_name TEXT UNIQUE NOT NULL,
    display_name TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 价格记录表（普通监控）
CREATE_PRICE_RECORDS_TABLE = """
CREATE TABLE IF NOT EXISTS price_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_hash_name TEXT NOT NULL,
    platform TEXT NOT NULL,
    price REAL NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (market_hash_name) REFERENCES items(market_hash_name)
);
"""

# 告警记录表（普通监控）
CREATE_ALERT_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS alert_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_hash_name TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    current_price REAL,
    baseline_price REAL,
    change_percent REAL,
    notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 极致追踪快照表
CREATE_EXTREME_TRACK_SNAPSHOTS_TABLE = """
CREATE TABLE IF NOT EXISTS extreme_track_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_hash_name TEXT NOT NULL,
    platform TEXT NOT NULL,
    price REAL,
    quantity INTEGER,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_IDX_SNAPSHOT = """
CREATE INDEX IF NOT EXISTS idx_snapshot_item_time
    ON extreme_track_snapshots(market_hash_name, platform, recorded_at DESC);
"""

# 极致追踪告警记录表
CREATE_EXTREME_TRACK_ALERTS_TABLE = """
CREATE TABLE IF NOT EXISTS extreme_track_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_hash_name TEXT NOT NULL,
    platform TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    prev_price REAL,
    curr_price REAL,
    price_change_percent REAL,
    prev_quantity INTEGER,
    curr_quantity INTEGER,
    quantity_change_percent REAL,
    notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 监控清单表（从 config.py 迁移）
CREATE_WATCHLIST_TABLE = """
CREATE TABLE IF NOT EXISTS watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_hash_name TEXT UNIQUE NOT NULL,
    display_name TEXT,
    threshold_percent REAL DEFAULT 5.0,
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_IDX_WATCHLIST_ENABLED = """
CREATE INDEX IF NOT EXISTS idx_watchlist_enabled
    ON watchlist(enabled);
"""

# 极致追踪配置表（从 config.py 迁移）
CREATE_EXTREME_TRACK_CONFIG_TABLE = """
CREATE TABLE IF NOT EXISTS extreme_track_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_hash_name TEXT NOT NULL,
    platform TEXT NOT NULL,
    interval_seconds INTEGER DEFAULT 60,
    enabled INTEGER DEFAULT 1,
    price_track_enabled INTEGER DEFAULT 1,
    price_change_mode TEXT DEFAULT 'any',
    price_threshold_percent REAL DEFAULT 0.0,
    quantity_track_enabled INTEGER DEFAULT 1,
    quantity_change_mode TEXT DEFAULT 'any',
    quantity_threshold_percent REAL DEFAULT 0.0,
    alert_cooldown_seconds INTEGER DEFAULT 0,
    quiet_hours_start TEXT,
    quiet_hours_end TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(market_hash_name, platform)
);
"""

CREATE_IDX_EXTREME_ENABLED = """
CREATE INDEX IF NOT EXISTS idx_extreme_enabled
    ON extreme_track_config(enabled);
"""

# 系统配置表
CREATE_SYSTEM_CONFIG_TABLE = """
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 价格归档表（90 天以上历史数据按天聚合归档）
CREATE_ARCHIVED_PRICES_TABLE = """
CREATE TABLE IF NOT EXISTS archived_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_hash_name TEXT NOT NULL,
    platform TEXT NOT NULL,
    date TEXT NOT NULL,
    avg_price REAL NOT NULL,
    min_price REAL,
    max_price REAL,
    record_count INTEGER NOT NULL,
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(market_hash_name, platform, date)
);
"""

ALL_TABLES = [
    CREATE_ITEMS_TABLE,
    CREATE_PRICE_RECORDS_TABLE,
    CREATE_ALERT_LOGS_TABLE,
    CREATE_EXTREME_TRACK_SNAPSHOTS_TABLE,
    CREATE_IDX_SNAPSHOT,
    CREATE_EXTREME_TRACK_ALERTS_TABLE,
    CREATE_WATCHLIST_TABLE,
    CREATE_IDX_WATCHLIST_ENABLED,
    CREATE_EXTREME_TRACK_CONFIG_TABLE,
    CREATE_IDX_EXTREME_ENABLED,
    CREATE_SYSTEM_CONFIG_TABLE,
    CREATE_ARCHIVED_PRICES_TABLE,
]
