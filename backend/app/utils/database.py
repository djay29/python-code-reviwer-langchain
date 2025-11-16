import sqlite3

def get_db_connection():
    db = sqlite3.connect("db.sqlite")
    conn = db.cursor()
    return db,conn

def create_db():
    db,conn = get_db_connection()
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sessions table
    db.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    db.execute('''
        CREATE TABLE IF NOT EXISTS job (
            job_id TEXT NOT NULL PRIMARY KEY,
            status TEXT NOT NULL,
            username TEXT NOT NULL,
            path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            result TEXT,
            error TEXT,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    
    db.commit()
    conn.close()