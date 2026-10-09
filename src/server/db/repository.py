# src/server/db/repository.py

from typing import Any, Dict, List, Optional
from . import db


class AgentRepository:
    @staticmethod
    def upsert_agent(uuid: str, hostname: str, username: str, ip: str, port: int, os_type: str, arch: str):
        """Insert a new agent or update agent info and beacon timestamp if the agent exists."""
        sql = """
        INSERT INTO agents (uuid, hostname, username, ip_address, port, os_type, arch, first_seen, last_beacon, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'active')
        ON CONFLICT(uuid) DO UPDATE SET
            hostname = excluded.hostname,
            username = excluded.username,
            ip_address = excluded.ip_address,
            port = excluded.port,
            os_type = excluded.os_type,
            arch = excluded.arch,
            last_beacon = CURRENT_TIMESTAMP,
            status = 'active';
        """
        with db.get_connection() as conn:
            conn.execute(sql, (uuid, hostname, username, ip, int(port), os_type, arch))

    @staticmethod
    def update_beacon(uuid: str):
        """Update the agent's last beacon timestamp."""
        sql = "UPDATE agents SET last_beacon = CURRENT_TIMESTAMP, status = 'active' WHERE uuid = ?;"
        with db.get_connection() as conn:
            conn.execute(sql, (uuid,))

    @staticmethod
    def set_status(uuid: str, status: str):
        """Update agent status ('active', 'stale', 'dead')."""
        sql = "UPDATE agents SET status = ? WHERE uuid = ?;"
        with db.get_connection() as conn:
            conn.execute(sql, (status, uuid))

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Retrieve all agents, ordered by most recent beacon."""
        sql = "SELECT * FROM agents ORDER BY last_beacon DESC;"
        with db.get_connection() as conn:
            rows = conn.execute(sql).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_by_uuid(uuid: str) -> Optional[Dict[str, Any]]:
        """Retrieve details of a single agent by UUID."""
        sql = "SELECT * FROM agents WHERE uuid = ?;"
        with db.get_connection() as conn:
            row = conn.execute(sql, (uuid,)).fetchone()
            return dict(row) if row else None

    @staticmethod
    def delete_agent(uuid: str):
        """Delete an agent and associated tasks, results, and transfers (ON DELETE CASCADE)."""
        sql = "DELETE FROM agents WHERE uuid = ?;"
        with db.get_connection() as conn:
            conn.execute(sql, (uuid,))

    @staticmethod
    def delete_all():
        """Delete all agents from the database."""
        sql = "DELETE FROM agents;"
        with db.get_connection() as conn:
            conn.execute(sql)


class TaskRepository:
    @staticmethod
    def create_task(agent_uuid: str, command_type: str, payload: str) -> int:
        """Create a new task for an agent, returning the task id."""
        sql = "INSERT INTO tasks (agent_uuid, command_type, command_payload, status) VALUES (?, ?, ?, 'sent');"
        with db.get_connection() as conn:
            cursor = conn.execute(sql, (agent_uuid, command_type, str(payload)))
            return cursor.lastrowid

    @staticmethod
    def save_result(task_id: int, agent_uuid: str, output: str, return_code: int = 0):
        """Save the execution result of a specific task and mark status as completed."""
        sql = """
        INSERT OR REPLACE INTO task_results (task_id, agent_uuid, output, return_code, received_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP);
        """
        update_task_sql = "UPDATE tasks SET status = 'completed' WHERE id = ?;"
        with db.get_connection() as conn:
            conn.execute(sql, (task_id, agent_uuid, str(output), return_code))
            conn.execute(update_task_sql, (task_id,))

    @staticmethod
    def save_latest_result(agent_uuid: str, output: str, return_code: int = 0) -> Optional[int]:
        """
        Find the most recent task for the agent in 'sent' status and save its result.
        If no pending task is found, create an implicit task and save the result.
        """
        find_sql = "SELECT id FROM tasks WHERE agent_uuid = ? AND status = 'sent' ORDER BY id DESC LIMIT 1;"
        with db.get_connection() as conn:
            row = conn.execute(find_sql, (agent_uuid,)).fetchone()
            if row:
                task_id = row['id']
                conn.execute(
                    "INSERT OR REPLACE INTO task_results (task_id, agent_uuid, output, return_code, received_at) "
                    "VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP);",
                    (task_id, agent_uuid, str(output), return_code)
                )
                conn.execute("UPDATE tasks SET status = 'completed' WHERE id = ?;", (task_id,))
                return task_id
            else:
                # No prior task found, automatically generate a task to save result
                cursor = conn.execute(
                    "INSERT INTO tasks (agent_uuid, command_type, command_payload, status) VALUES (?, 'unknown', '', 'completed');",
                    (agent_uuid,)
                )
                new_task_id = cursor.lastrowid
                conn.execute(
                    "INSERT INTO task_results (task_id, agent_uuid, output, return_code, received_at) "
                    "VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP);",
                    (new_task_id, agent_uuid, str(output), return_code)
                )
                return new_task_id

    @staticmethod
    def get_history(agent_uuid: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve command and result history for a single agent or the entire system."""
        if agent_uuid:
            sql = """
            SELECT t.id, t.agent_uuid, t.command_type, t.command_payload, t.created_at, t.status,
                   r.output, r.return_code, r.received_at
            FROM tasks t
            LEFT JOIN task_results r ON t.id = r.task_id
            WHERE t.agent_uuid = ?
            ORDER BY t.created_at DESC
            LIMIT ?;
            """
            params = (agent_uuid, limit)
        else:
            sql = """
            SELECT t.id, t.agent_uuid, t.command_type, t.command_payload, t.created_at, t.status,
                   r.output, r.return_code, r.received_at
            FROM tasks t
            LEFT JOIN task_results r ON t.id = r.task_id
            ORDER BY t.created_at DESC
            LIMIT ?;
            """
            params = (limit,)

        with db.get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]


class FileTransferRepository:
    @staticmethod
    def record_transfer(agent_uuid: str, direction: str, remote_path: str, local_path: Optional[str], file_size: int, md5_hash: str = ""):
        """Record a file transfer history entry (Upload or Download)."""
        sql = """
        INSERT INTO file_transfers (agent_uuid, direction, remote_path, local_path, file_size, md5_hash, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
        """
        with db.get_connection() as conn:
            conn.execute(sql, (agent_uuid, direction, remote_path, local_path or "", file_size, md5_hash))

    @staticmethod
    def get_all(limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve the most recent file transfers."""
        sql = "SELECT * FROM file_transfers ORDER BY completed_at DESC LIMIT ?;"
        with db.get_connection() as conn:
            rows = conn.execute(sql, (limit,)).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_by_agent(agent_uuid: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve file transfers for a specific agent."""
        sql = "SELECT * FROM file_transfers WHERE agent_uuid = ? ORDER BY completed_at DESC LIMIT ?;"
        with db.get_connection() as conn:
            rows = conn.execute(sql, (agent_uuid, limit)).fetchall()
            return [dict(r) for r in rows]


class LogRepository:
    @staticmethod
    def add_log(level: str, message: str):
        """Record a system log entry into the audit_logs table."""
        sql = "INSERT INTO audit_logs (level, message, created_at) VALUES (?, ?, CURRENT_TIMESTAMP);"
        with db.get_connection() as conn:
            conn.execute(sql, (level, message))

    @staticmethod
    def get_recent(limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve the most recent activity logs."""
        sql = "SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?;"
        with db.get_connection() as conn:
            rows = conn.execute(sql, (limit,)).fetchall()
            return [dict(r) for r in rows]
