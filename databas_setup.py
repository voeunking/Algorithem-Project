import sqlite3

def create_tables():
    conn = sqlite3.connect("library.db")
    cur = conn.cursor()

    # ======================
    # BOOKS TABLE
    # ======================
    cur.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        publisher TEXT,
        year_published INTEGER,
        category TEXT,
        total_copies INTEGER,
        available_copies INTEGER,
        created_at TEXT
    )
    ''')

    # ======================
    # MEMBERS TABLE
    # ======================
    cur.execute('''
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        address TEXT,
        created_at TEXT
    )
    ''')

    # ======================
    # TRANSACTIONS TABLE
    # ======================
    cur.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        issue_date TEXT,
        return_date TEXT,
        FOREIGN KEY (member_id) REFERENCES members(id),
        FOREIGN KEY (book_id) REFERENCES books(id)
    )
    ''')

    # ======================
    # Ensure 'issue_date' and 'return_date' exist
    # ======================
    cur.execute("PRAGMA table_info(transactions)")
    columns = [col[1] for col in cur.fetchall()]

    if 'issue_date' not in columns:
        cur.execute("ALTER TABLE transactions ADD COLUMN issue_date TEXT")
    if 'return_date' not in columns:
        cur.execute("ALTER TABLE transactions ADD COLUMN return_date TEXT")

    conn.commit()
    conn.close()
    print("✅ All tables created and columns synced successfully.")

# ======================
# Run script
# ======================
if __name__ == "__main__":
    create_tables()
