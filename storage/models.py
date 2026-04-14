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

ALL_TABLES = [
    CREATE_ITEMS_TABLE,
    CREATE_PRICE_RECORDS_TABLE,
    CREATE_ALERT_LOGS_TABLE,
    CREATE_EXTREME_TRACK_SNAPSHOTS_TABLE,
    CREATE_IDX_SNAPSHOT,
    CREATE_EXTREME_TRACK_ALERTS_TABLE,
]
