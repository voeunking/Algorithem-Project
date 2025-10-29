import sqlite3

class BookModel:
    @staticmethod
    def connect():
        """Create a database connection with row factory."""
        conn = sqlite3.connect('library.db')
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def create_table():
        """Create the books table if it doesn't exist."""
        conn = BookModel.connect()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                publisher TEXT,
                year_published TEXT,
                category TEXT,
                total_copies INTEGER,
                available_copies INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def add_book(title, author, publisher, year_published, category, total_copies, available_copies):
        """Add a new book to the database."""
        conn = BookModel.connect()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO books (title, author, publisher, year_published, category, total_copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, author, publisher, year_published, category, total_copies, available_copies))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        """Retrieve all books from the database."""
        conn = BookModel.connect()
        cur = conn.cursor()
        cur.execute('SELECT * FROM books')
        books = cur.fetchall()
        conn.close()
        return books

    @staticmethod
    def get_by_id(book_id):
        """Retrieve a single book by its ID."""
        conn = BookModel.connect()
        cur = conn.cursor()
        cur.execute('SELECT * FROM books WHERE id = ?', (book_id,))
        row = cur.fetchone()
        conn.close()
        return row

    @staticmethod
    def delete_book(book_id):
        """Delete a book by its ID."""
        conn = BookModel.connect()
        cur = conn.cursor()
        cur.execute('DELETE FROM books WHERE id = ?', (book_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def decrease_available(book_id):
        """Decrease available copies for a book by 1, not going below 0."""
        conn = BookModel.connect()
        cur = conn.cursor()
        cur.execute('''
            UPDATE books
            SET available_copies = CASE
                WHEN available_copies > 0 THEN available_copies - 1
                ELSE 0
            END
            WHERE id = ?
        ''', (book_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def increase_available(book_id):
        """Increase available copies for a book by 1."""
        conn = BookModel.connect()
        cur = conn.cursor()
        cur.execute('''
            UPDATE books
            SET available_copies = available_copies + 1
            WHERE id = ?
        ''', (book_id,))
        conn.commit()
        conn.close()
