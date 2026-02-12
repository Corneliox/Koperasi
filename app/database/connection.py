"""
Database Connection and Schema for Koperasi Brimob
Complete SQLite3 implementation with all required tables
"""
import sqlite3
import os
import sys
from datetime import datetime

def get_db_path():
    """Get persistent database path in AppData"""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        app_data = os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))
        db_dir = os.path.join(app_data, "KoperasiBrimob")
    else:
        # Running in development
        db_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        
    return os.path.join(db_dir, "koperasi_brimob.db")

DB_PATH = get_db_path()


def get_connection():
    """Get database connection with foreign keys enabled"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize all database tables and migrate old database if necessary"""
    # Migration: check if old DB exists in root directory and move it to new location
    old_db = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "koperasi_brimob.db")
    if os.path.exists(old_db) and old_db != DB_PATH:
        try:
            import shutil
            # If new DB doesn't exist, move old one
            if not os.path.exists(DB_PATH):
                shutil.copy2(old_db, DB_PATH)
                # Keep old as backup or rename? Rename to be safe.
                os.rename(old_db, old_db + ".bak")
                print(f"Migrated database from {old_db} to {DB_PATH}")
        except Exception as e:
            print(f"Migration failed: {e}")

    conn = get_connection()
    cursor = conn.cursor()
    
    # Users table for authentication
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Warehouse/Inventory table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS warehouse (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_type TEXT NOT NULL CHECK(category_type IN ('SEMBAKO', 'TAKTIKAL')),
            stock INTEGER DEFAULT 0,
            buy_price REAL DEFAULT 0,
            sell_price REAL DEFAULT 0,
            status TEXT DEFAULT 'Koperasi' CHECK(status IN ('Koperasi', 'Konsinyasi')),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Warehouse mutation table for tracking all stock changes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS warehouse_mutation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('IN', 'OUT', 'RETURN', 'CORRECTION')),
            qty INTEGER NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT,
            FOREIGN KEY (item_id) REFERENCES warehouse(id) ON DELETE CASCADE
        )
    """)
    
    # Members table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rank TEXT,
            unit TEXT,
            nrp TEXT UNIQUE,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            member_id INTEGER,
            qty INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            category_type TEXT NOT NULL,
            payment_method TEXT DEFAULT 'Tunai',
            FOREIGN KEY (item_id) REFERENCES warehouse(id) ON DELETE SET NULL,
            FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE SET NULL
        )
    """)
    
    # Loans table for member loans
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            principal REAL NOT NULL,
            interest_rate REAL DEFAULT 0,
            duration_months INTEGER DEFAULT 12,
            total_amount REAL NOT NULL,
            monthly_payment REAL DEFAULT 0,
            paid_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'Aktif' CHECK(status IN ('Aktif', 'Lunas', 'Macet')),
            due_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
        )
    """)
    
    # Add columns if they don't exist (for existing databases)
    try:
        cursor.execute("ALTER TABLE members ADD COLUMN membership_status TEXT DEFAULT 'Anggota Koperasi'")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE loans ADD COLUMN principal REAL DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE loans ADD COLUMN duration_months INTEGER DEFAULT 12")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE loans ADD COLUMN monthly_payment REAL DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE loans ADD COLUMN notes TEXT")
    except:
        pass
    
    # Loan payments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loan_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loan_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT DEFAULT 'Tunai',
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (loan_id) REFERENCES loans(id) ON DELETE CASCADE
        )
    """)
    
    # Add payment_method to loan_payments if not exists
    try:
        cursor.execute("ALTER TABLE loan_payments ADD COLUMN payment_method TEXT DEFAULT 'Tunai'")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE loan_payments ADD COLUMN notes TEXT")
    except:
        pass
    
    # Activity logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            action_type TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_warehouse_category ON warehouse(category_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mutation_item ON warehouse_mutation(item_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_loans_member ON loans(member_id)")
    
    # Insert default admin user if not exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', 'admin123', 'admin')
        )
    
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")


def log_activity(user: str, action_type: str, details: str):
    """Log an activity to the activity_logs table"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO activity_logs (user, action_type, details) VALUES (?, ?, ?)",
        (user, action_type, details)
    )
    conn.commit()
    conn.close()


def verify_login(username: str, password: str) -> bool:
    """Verify user login credentials"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None


if __name__ == "__main__":
    init_database()
