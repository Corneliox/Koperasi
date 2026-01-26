"""
Immutable Audit Logging System
Records ALL changes with NO delete functionality
Stored in separate table for security
"""
import os
import json
from datetime import datetime
from app.database.connection import get_connection


def init_audit_log_table():
    """Initialize immutable audit log table"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create immutable audit log table - NO DELETE triggers allowed
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log_immutable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            user TEXT NOT NULL,
            action_category TEXT NOT NULL,
            action_type TEXT NOT NULL,
            entity_type TEXT,
            entity_id INTEGER,
            old_value TEXT,
            new_value TEXT,
            details TEXT,
            ip_address TEXT,
            session_id TEXT
        )
    """)
    
    # Create index for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
        ON audit_log_immutable(timestamp DESC)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_entity 
        ON audit_log_immutable(entity_type, entity_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_user 
        ON audit_log_immutable(user)
    """)
    
    conn.commit()
    conn.close()


def log_audit(user: str, action_category: str, action_type: str,
              entity_type: str = None, entity_id: int = None,
              old_value: dict = None, new_value: dict = None,
              details: str = None):
    """
    Log an immutable audit record
    
    :param user: Username performing action
    :param action_category: Category (INVENTORY, MEMBER, LOAN, TRANSACTION, SYSTEM)
    :param action_type: Type (CREATE, UPDATE, DELETE, LOGIN, LOGOUT, EXPORT, IMPORT)
    :param entity_type: Type of entity (warehouse, member, loan, etc)
    :param entity_id: ID of entity affected
    :param old_value: Previous value (dict, will be JSON serialized)
    :param new_value: New value (dict, will be JSON serialized)
    :param details: Additional details string
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Serialize dicts to JSON
    old_json = json.dumps(old_value, default=str) if old_value else None
    new_json = json.dumps(new_value, default=str) if new_value else None
    
    cursor.execute("""
        INSERT INTO audit_log_immutable 
        (user, action_category, action_type, entity_type, entity_id, 
         old_value, new_value, details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user, action_category, action_type, entity_type, entity_id,
          old_json, new_json, details))
    
    conn.commit()
    conn.close()


def get_audit_logs(limit: int = 500, user_filter: str = None,
                   category_filter: str = None, entity_type: str = None,
                   entity_id: int = None, start_date: str = None,
                   end_date: str = None) -> list:
    """
    Retrieve audit logs (READ ONLY - no delete available)
    
    :return: List of audit log entries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM audit_log_immutable WHERE 1=1"
    params = []
    
    if user_filter:
        query += " AND user = ?"
        params.append(user_filter)
    
    if category_filter:
        query += " AND action_category = ?"
        params.append(category_filter)
    
    if entity_type:
        query += " AND entity_type = ?"
        params.append(entity_type)
    
    if entity_id:
        query += " AND entity_id = ?"
        params.append(entity_id)
    
    if start_date:
        query += " AND DATE(timestamp) >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND DATE(timestamp) <= ?"
        params.append(end_date)
    
    query += f" ORDER BY timestamp DESC LIMIT {limit}"
    
    cursor.execute(query, params)
    logs = []
    for row in cursor.fetchall():
        log = dict(row)
        # Parse JSON fields
        if log.get('old_value'):
            try:
                log['old_value'] = json.loads(log['old_value'])
            except:
                pass
        if log.get('new_value'):
            try:
                log['new_value'] = json.loads(log['new_value'])
            except:
                pass
        logs.append(log)
    
    conn.close()
    return logs


def get_entity_history(entity_type: str, entity_id: int) -> list:
    """Get complete history for a specific entity"""
    return get_audit_logs(
        limit=1000,
        entity_type=entity_type,
        entity_id=entity_id
    )


def get_audit_statistics() -> dict:
    """Get audit log statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total logs
    cursor.execute("SELECT COUNT(*) FROM audit_log_immutable")
    total = cursor.fetchone()[0]
    
    # By category
    cursor.execute("""
        SELECT action_category, COUNT(*) as count 
        FROM audit_log_immutable 
        GROUP BY action_category
    """)
    by_category = {row['action_category']: row['count'] for row in cursor.fetchall()}
    
    # Today's logs
    cursor.execute("""
        SELECT COUNT(*) FROM audit_log_immutable 
        WHERE DATE(timestamp) = DATE('now', 'localtime')
    """)
    today = cursor.fetchone()[0]
    
    # Unique users
    cursor.execute("SELECT COUNT(DISTINCT user) FROM audit_log_immutable")
    unique_users = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_logs': total,
        'by_category': by_category,
        'today_logs': today,
        'unique_users': unique_users
    }


# Initialize table on import
init_audit_log_table()
