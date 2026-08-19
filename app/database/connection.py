"""
Database Connection and Schema for Sistem Koperasi
Complete SQLite3 implementation with all required tables (Offline / Local)
"""
import sqlite3
import os
import sys
import hashlib
import secrets
from datetime import datetime

def get_db_path():
    """Get persistent database path in AppData or local folder with auto-migration"""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        app_data = os.environ.get('APPDATA', os.path.expanduser('~\\AppData\\Roaming'))
        db_dir = os.path.join(app_data, "Koperasi")
        old_brimob_db = os.path.join(app_data, "KoperasiBrimob", "koperasi_brimob.db")
    else:
        # Running in development
        db_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        old_brimob_db = os.path.join(db_dir, "koperasi_brimob.db")
    
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    target_db = os.path.join(db_dir, "koperasi.db")
    
    # Seamless auto-migration from legacy database if target doesn't exist yet
    if not os.path.exists(target_db) and os.path.exists(old_brimob_db):
        try:
            import shutil
            shutil.copy2(old_brimob_db, target_db)
            print(f"Migrated legacy database from {old_brimob_db} to {target_db}")
        except Exception as e:
            print(f"Auto-migration failed: {e}")
            
    return target_db

DB_PATH = get_db_path()


def get_connection():
    """Get database connection with foreign keys enabled, WAL mode, and timeout for multi-thread stability"""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
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
            item_code TEXT,
            name TEXT NOT NULL,
            category_type TEXT NOT NULL CHECK(category_type IN ('SEMBAKO', 'TAKTIKAL')),
            stock INTEGER DEFAULT 0,
            buy_price REAL DEFAULT 0,
            sell_price REAL DEFAULT 0,
            status TEXT DEFAULT 'Koperasi' CHECK(status IN ('Koperasi', 'Titipan')),
            is_active INTEGER DEFAULT 1,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Add columns if they don't exist
    try:
        cursor.execute("ALTER TABLE warehouse ADD COLUMN item_code TEXT")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE warehouse ADD COLUMN is_active INTEGER DEFAULT 1")
    except:
        pass
    
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
            item_id INTEGER,
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
    
    # Check if transactions table has NOT NULL on item_id and migrate if needed
    try:
        cursor.execute("PRAGMA table_info(transactions)")
        t_cols = cursor.fetchall()
        item_id_info = next((c for c in t_cols if c[1] == 'item_id'), None)
        if item_id_info and item_id_info[3] == 1:  # notnull is 1
            cursor.execute("PRAGMA foreign_keys = OFF")
            cursor.execute("""
                CREATE TABLE transactions_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER,
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
            cursor.execute("""
                INSERT INTO transactions_new (id, item_id, member_id, qty, unit_price, total_price, date, category_type, payment_method)
                SELECT id, item_id, member_id, qty, unit_price, total_price, date, category_type, payment_method FROM transactions
            """)
            cursor.execute("DROP TABLE transactions")
            cursor.execute("ALTER TABLE transactions_new RENAME TO transactions")
            cursor.execute("PRAGMA foreign_keys = ON")
    except Exception:
        pass
    
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
        cursor.execute("UPDATE loans SET principal = amount WHERE (principal IS NULL OR principal = 0) AND amount IS NOT NULL")
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
    
    # Settings table for app version and other configs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    # Create indexes for better performance
    # Ensure users table has security and legacy recovery columns
    try:
        cursor.execute("PRAGMA table_info(users)")
        cols = [r['name'] for r in cursor.fetchall()]
        if 'security_question' not in cols:
            cursor.execute("ALTER TABLE users ADD COLUMN security_question TEXT")
        if 'security_answer' not in cols:
            cursor.execute("ALTER TABLE users ADD COLUMN security_answer TEXT")
        if 'recovery_pin' not in cols:
            cursor.execute("ALTER TABLE users ADD COLUMN recovery_pin TEXT")
        if 'is_legacy' not in cols:
            cursor.execute("ALTER TABLE users ADD COLUMN is_legacy INTEGER DEFAULT 0")
    except Exception as e:
        print(f"User table migration notice: {e}")

    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")


def hash_password(password: str, salt: str = None) -> str:
    """Hash password using SHA-256 with cryptographic salt"""
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify password supporting both salted hashes and legacy plaintext"""
    if not stored_password or not provided_password:
        return False
    if ":" in stored_password:
        salt, _ = stored_password.split(":", 1)
        return hash_password(provided_password, salt) == stored_password
    # Legacy plaintext check
    return stored_password == provided_password


def has_registered_users() -> bool:
    """Check if at least one user account exists in the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        return False


def register_user(username: str, password: str, full_name: str = "",
                  security_question: str = "", security_answer: str = "",
                  recovery_pin: str = "", role: str = "admin") -> dict:
    """
    Register a new user account in the local database with security question & PIN
    """
    username = username.strip()
    password = password.strip()
    security_question = security_question.strip()
    security_answer = security_answer.strip().lower()
    recovery_pin = recovery_pin.strip()
    
    if len(username) < 3:
        return {"success": False, "message": "Username minimal 3 karakter!"}
    if len(password) < 4:
        return {"success": False, "message": "Password minimal 4 karakter!"}
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        if cursor.fetchone():
            return {"success": False, "message": f"Username '{username}' sudah terdaftar!"}
        
        # If this is the very first user, guarantee admin role
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            role = "admin"
            
        hashed_pw = hash_password(password)
        hashed_ans = hash_password(security_answer) if security_answer else None
        hashed_pin = hash_password(recovery_pin) if recovery_pin else None
        
        cursor.execute(
            """INSERT INTO users 
               (username, password, role, security_question, security_answer, recovery_pin, is_legacy) 
               VALUES (?, ?, ?, ?, ?, ?, 0)""",
            (username, hashed_pw, role, security_question, hashed_ans, hashed_pin)
        )
        user_id = cursor.lastrowid
        conn.commit()
        
        log_activity(username, "REGISTER", f"Pendaftaran akun baru: {username} ({role})")
        return {"success": True, "message": "Akun berhasil didaftarkan!", "user_id": user_id}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"Gagal mendaftarkan akun: {str(e)}"}
    finally:
        conn.close()


def get_user_security_info(username: str) -> dict:
    """Get security question and legacy status for an account"""
    username = username.strip()
    if not username:
        return {"success": False, "message": "Username tidak boleh kosong"}
        
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, security_question, security_answer, recovery_pin, is_legacy FROM users WHERE LOWER(username) = LOWER(?)",
            (username,)
        )
        row = cursor.fetchone()
        if not row:
            return {"success": False, "message": f"Akun '{username}' tidak ditemukan!"}
            
        has_security = bool(row['security_question'] and row['security_answer'])
        has_pin = bool(row['recovery_pin'])
        is_legacy = bool(row['is_legacy'] or not has_security)
        
        return {
            "success": True,
            "username": row['username'],
            "security_question": row['security_question'] or "Belum diatur (Pengguna Versi Lama)",
            "has_security": has_security,
            "has_pin": has_pin,
            "is_legacy": is_legacy
        }
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()


def reset_password_with_security(username: str, security_answer: str, new_password: str) -> dict:
    """Reset user password using security answer verification"""
    username = username.strip()
    security_answer = security_answer.strip().lower()
    new_password = new_password.strip()
    
    if len(new_password) < 4:
        return {"success": False, "message": "Password baru minimal 4 karakter!"}
        
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, security_answer FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        row = cursor.fetchone()
        if not row:
            return {"success": False, "message": "Akun tidak ditemukan!"}
            
        stored_ans = row['security_answer']
        if not stored_ans:
            return {"success": False, "message": "Akun belum mengatur pertanyaan keamanan. Gunakan PIN atau pembaruan akun lama."}
            
        if not verify_password(stored_ans, security_answer):
            return {"success": False, "message": "Jawaban pertanyaan keamanan salah!"}
            
        new_hash = hash_password(new_password)
        cursor.execute("UPDATE users SET password = ?, is_legacy = 0 WHERE id = ?", (new_hash, row['id']))
        conn.commit()
        
        log_activity(username, "PASSWORD_RESET", f"Password direset via pertanyaan keamanan")
        return {"success": True, "message": "Password berhasil diperbarui! Silakan masuk dengan password baru."}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": str(e)}
    finally:
        conn.close()


def reset_password_with_pin(username: str, recovery_pin: str, new_password: str) -> dict:
    """Reset user password using 6-digit recovery PIN"""
    username = username.strip()
    recovery_pin = recovery_pin.strip()
    new_password = new_password.strip()
    
    if len(new_password) < 4:
        return {"success": False, "message": "Password baru minimal 4 karakter!"}
        
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, recovery_pin FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        row = cursor.fetchone()
        if not row:
            return {"success": False, "message": "Akun tidak ditemukan!"}
            
        stored_pin = row['recovery_pin']
        if not stored_pin or not verify_password(stored_pin, recovery_pin):
            return {"success": False, "message": "PIN Pemulihan salah!"}
            
        new_hash = hash_password(new_password)
        cursor.execute("UPDATE users SET password = ?, is_legacy = 0 WHERE id = ?", (new_hash, row['id']))
        conn.commit()
        
        log_activity(username, "PASSWORD_RESET", f"Password direset via PIN Pemulihan")
        return {"success": True, "message": "Password berhasil diperbarui! Silakan masuk dengan password baru."}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": str(e)}
    finally:
        conn.close()


def update_legacy_user_credentials(username: str, old_password: str, new_password: str,
                                   security_question: str, security_answer: str, recovery_pin: str = "") -> dict:
    """
    Allow legacy user to authenticate with old password and upgrade to new secure password + security questions
    """
    username = username.strip()
    old_password = old_password.strip()
    new_password = new_password.strip()
    security_question = security_question.strip()
    security_answer = security_answer.strip().lower()
    recovery_pin = recovery_pin.strip()
    
    if len(new_password) < 4:
        return {"success": False, "message": "Password baru minimal 4 karakter!"}
    if not security_question or not security_answer:
        return {"success": False, "message": "Pertanyaan dan jawaban keamanan wajib diisi!"}
        
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        row = cursor.fetchone()
        if not row:
            return {"success": False, "message": "Akun tidak ditemukan!"}
            
        user_id, stored_pw = row['id'], row['password']
        if not verify_password(stored_pw, old_password):
            return {"success": False, "message": "Password lama salah!"}
            
        new_pw_hash = hash_password(new_password)
        new_ans_hash = hash_password(security_answer)
        new_pin_hash = hash_password(recovery_pin) if recovery_pin else None
        
        cursor.execute(
            """UPDATE users SET 
               password = ?, 
               security_question = ?, 
               security_answer = ?, 
               recovery_pin = ?, 
               is_legacy = 0 
               WHERE id = ?""",
            (new_pw_hash, security_question, new_ans_hash, new_pin_hash, user_id)
        )
        conn.commit()
        
        log_activity(username, "SECURITY_UPDATE", f"Pembaruan kredensial dan keamanan akun versi lama")
        return {"success": True, "message": "Akun berhasil diperbarui dengan keamanan penuh!"}
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": str(e)}
    finally:
        conn.close()


def log_activity(user: str, action_type: str, details: str):
    """Log an activity to the activity_logs table"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO activity_logs (user, action_type, details) VALUES (?, ?, ?)",
            (user, action_type, details)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def verify_login(username: str, password: str) -> bool:
    """Verify user login credentials with automatic legacy hash upgrade"""
    res = verify_login_detailed(username, password)
    return res.get("success", False)


def verify_login_detailed(username: str, password: str) -> dict:
    """Verify login and return legacy upgrade status"""
    username = username.strip()
    if not username or not password:
        return {"success": False, "message": "Username dan password wajib diisi"}
        
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password, security_question, is_legacy, role FROM users WHERE LOWER(username) = LOWER(?)",
            (username,)
        )
        row = cursor.fetchone()
        if not row:
            return {"success": False, "message": "Username atau password salah!"}
            
        user_id, stored_pw = row['id'], row['password']
        if verify_password(stored_pw, password):
            # Check if this user needs to configure security question
            needs_security_setup = bool(not row['security_question'] or row['is_legacy'] == 1 or ":" not in stored_pw)
            
            # If stored password was plaintext, auto upgrade
            if ":" not in stored_pw:
                new_hash = hash_password(password)
                cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_hash, user_id))
                conn.commit()
                
            return {
                "success": True,
                "username": row['username'],
                "role": row['role'],
                "needs_security_setup": needs_security_setup
            }
        return {"success": False, "message": "Username atau password salah!"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        conn.close()


if __name__ == "__main__":
    init_database()
