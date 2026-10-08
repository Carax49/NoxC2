# src/server/db/schema.py

import sqlite3

DDL_SCRIPT = """
CREATE TABLE IF NOT EXISTS agents (
    uuid            TEXT PRIMARY KEY,
    hostname        TEXT NOT NULL,
    username        TEXT NOT NULL,
    ip_address      TEXT NOT NULL,
    port            INTEGER NOT NULL,
    os_type         TEXT NOT NULL,
    arch            TEXT NOT NULL,
    first_seen      DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_beacon     DATETIME DEFAULT CURRENT_TIMESTAMP,
    status          TEXT DEFAULT 'active'
);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_last_beacon ON agents(last_beacon);

CREATE TABLE IF NOT EXISTS tasks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_uuid      TEXT NOT NULL,
    command_type    TEXT NOT NULL,
    command_payload TEXT NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    status          TEXT DEFAULT 'sent',
    FOREIGN KEY(agent_uuid) REFERENCES agents(uuid) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_tasks_agent ON tasks(agent_uuid);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);

CREATE TABLE IF NOT EXISTS task_results (
    task_id         INTEGER PRIMARY KEY,
    agent_uuid      TEXT NOT NULL,
    output          TEXT NOT NULL,
    return_code     INTEGER DEFAULT 0,
    received_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY(agent_uuid) REFERENCES agents(uuid) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_results_agent ON task_results(agent_uuid);

CREATE TABLE IF NOT EXISTS file_transfers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_uuid      TEXT NOT NULL,
    direction       TEXT NOT NULL,
    remote_path     TEXT NOT NULL,
    local_path      TEXT,
    file_size       INTEGER DEFAULT 0,
    md5_hash        TEXT,
    completed_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(agent_uuid) REFERENCES agents(uuid) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_transfers_agent ON file_transfers(agent_uuid);

CREATE TABLE IF NOT EXISTS audit_logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    level           TEXT NOT NULL,
    message         TEXT NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_logs_created ON audit_logs(created_at);
"""


def init_db(conn: sqlite3.Connection):
    """Thực thi DDL script để khởi tạo các bảng và indexes nếu chưa có."""
    conn.executescript(DDL_SCRIPT)
