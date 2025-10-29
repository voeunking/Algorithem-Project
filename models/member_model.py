import sqlite3

class MemberModel:
    @staticmethod
    def connect():
        """Create a connection to the SQLite database."""
        conn = sqlite3.connect('library.db')
        conn.row_factory = sqlite3.Row  # Allows dict-like access
        return conn

    @staticmethod
    def create_table():
        """Create the members table if it doesn't exist."""
        conn = MemberModel.connect()
        cur = conn.cursor()
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
        # Ensure additional columns exist (SQLite allows adding columns)
        cur.execute("PRAGMA table_info(members)")
        existing_cols = {row[1] for row in cur.fetchall()}
        columns_to_add = [
            ("first_name", "TEXT"),
            ("last_name", "TEXT"),
            ("date_of_birth", "TEXT"),
            ("gender", "TEXT"),
            ("city", "TEXT"),
            ("state", "TEXT"),
            ("postal_code", "TEXT"),
            ("member_type", "TEXT"),
            ("membership_date", "TEXT"),
            ("institution", "TEXT"),
            ("emergency_contact_name", "TEXT"),
            ("emergency_contact_phone", "TEXT"),
            ("notes", "TEXT"),
            ("terms_agreed", "INTEGER")
        ]
        for col_name, col_type in columns_to_add:
            if col_name not in existing_cols:
                cur.execute(f"ALTER TABLE members ADD COLUMN {col_name} {col_type}")
        conn.commit()
        conn.close()

    @staticmethod
    def add_member(full_name, email, phone, address,
                   first_name=None, last_name=None, date_of_birth=None, gender=None,
                   city=None, state=None, postal_code=None,
                   member_type=None, membership_date=None, institution=None,
                   emergency_contact_name=None, emergency_contact_phone=None,
                   notes=None, terms_agreed=None):
        """Add a new member to the database."""
        conn = MemberModel.connect()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO members (
                full_name, email, phone, address,
                first_name, last_name, date_of_birth, gender,
                city, state, postal_code,
                member_type, membership_date, institution,
                emergency_contact_name, emergency_contact_phone,
                notes, terms_agreed,
                created_at
            )
            VALUES (
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?,
                datetime('now')
            )
        ''', (
            full_name, email, phone, address,
            first_name, last_name, date_of_birth, gender,
            city, state, postal_code,
            member_type, membership_date, institution,
            emergency_contact_name, emergency_contact_phone,
            notes, terms_agreed
        ))
        member_id = cur.lastrowid
        conn.commit()
        conn.close()
        return member_id

    @staticmethod
    def get_all():
        """Retrieve all members from the database."""
        conn = MemberModel.connect()
        cur = conn.cursor()
        cur.execute('SELECT * FROM members')
        data = cur.fetchall()
        conn.close()
        return data

    @staticmethod
    def update_member(member_id, full_name, email, phone, address):
        """Update an existing member's information."""
        conn = MemberModel.connect()
        cur = conn.cursor()
        cur.execute('''
            UPDATE members
            SET full_name = ?, email = ?, phone = ?, address = ?
            WHERE id = ?
        ''', (full_name, email, phone, address, member_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_member(member_id):
        """Delete a member from the database by ID."""
        conn = MemberModel.connect()
        cur = conn.cursor()
        cur.execute('DELETE FROM members WHERE id=?', (member_id,))
        conn.commit()
        conn.close()
