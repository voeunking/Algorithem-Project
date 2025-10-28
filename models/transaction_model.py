import sqlite3
from datetime import datetime

class TransactionModel:
    @staticmethod
    def connect():
        """Create a database connection with row access as dictionary-like."""
        conn = sqlite3.connect('library.db')
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def create_table():
        """Create the transactions table if it doesn't exist."""
        conn = TransactionModel.connect()
        cur = conn.cursor()
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
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        """Return all transactions with member and book names."""
        conn = TransactionModel.connect()
        cur = conn.cursor()
        cur.execute('''
            SELECT t.id, m.full_name AS member_name, b.title AS book_title,
                   t.issue_date, t.return_date
            FROM transactions t
            JOIN members m ON t.member_id = m.id
            JOIN books b ON t.book_id = b.id
        ''')
        data = cur.fetchall()
        conn.close()
        return data

    @staticmethod
    def get_by_id(transaction_id):
        """Get a single transaction by ID."""
        conn = TransactionModel.connect()
        cur = conn.cursor()
        cur.execute('SELECT * FROM transactions WHERE id=?', (transaction_id,))
        data = cur.fetchone()
        conn.close()
        return data

    @staticmethod
    def issue_book(member_id, book_id, issue_date=None):
        """Insert a new transaction (issue a book)."""
        if issue_date is None:
            issue_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = TransactionModel.connect()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO transactions (member_id, book_id, issue_date)
            VALUES (?, ?, ?)
        ''', (member_id, book_id, issue_date))
        conn.commit()
        conn.close()

    @staticmethod
    def return_book(transaction_id):
        """Mark a transaction as returned and set return_date."""
        conn = TransactionModel.connect()
        cur = conn.cursor()
        cur.execute('''
            UPDATE transactions
            SET return_date = ?
            WHERE id = ?
        ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), transaction_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_transaction(transaction_id):
        """Delete a transaction by ID."""
        conn = TransactionModel.connect()
        cur = conn.cursor()
        cur.execute('DELETE FROM transactions WHERE id=?', (transaction_id,))
        conn.commit()
        conn.close()
