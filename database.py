import sqlite3
import hashlib
import os

DB_NAME = "users.db"

def init_db():
    """Initializes the SQLite database and creates the users table if it does not exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,
            salt BLOB NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password: str, salt: bytes = None) -> tuple:
    """Hashes a password using PBKDF2 HMAC SHA-256. Generates a new salt if none is provided."""
    if salt is None:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return pwd_hash, salt

def register_user(username, password):
    """Registers a new user in the SQLite database. Returns (success_bool, message_str)."""
    username = username.strip()
    if not username or not password:
        return False, "Username and password cannot be empty."
    
    init_db()
    pwd_hash, salt = hash_password(password)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, pwd_hash, salt)
        )
        conn.commit()
        return True, "Registration successful! You can now log in."
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose a different one."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"
    finally:
        conn.close()

def authenticate_user(username, password):
    """Verifies user credentials. Returns True if authentication succeeds, False otherwise."""
    username = username.strip()
    if not username or not password:
        return False
    
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return False
    
    db_hash, db_salt = row
    pwd_hash, _ = hash_password(password, db_salt)
    return pwd_hash == db_hash
