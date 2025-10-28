# models/user_model.py
from config import get_db_connection
import bcrypt


class UserModel:
    @staticmethod
    def create_user(full_name, email, password):
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
            (full_name, email, hashed_pw)
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def find_by_email(email):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user

    @staticmethod
    def ensure_profile_image_column():
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SHOW COLUMNS FROM users LIKE 'profile_image'")
            exists = cursor.fetchone()
            if not exists:
                cursor.execute("ALTER TABLE users ADD COLUMN profile_image VARCHAR(255) NULL AFTER password")
                conn.commit()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_profile_image(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT profile_image FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row[0] if row else None

    @staticmethod
    def set_profile_image(user_id, relative_path):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET profile_image = %s WHERE id = %s", (relative_path, user_id))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row

    @staticmethod
    def update_profile(user_id, full_name, email):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET full_name = %s, email = %s WHERE id = %s", (full_name, email, user_id))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def verify_password(user_id, password_plain):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            return False
        stored = row[0] or ''
        return bcrypt.checkpw(password_plain.encode('utf-8'), stored.encode('utf-8'))

    @staticmethod
    def update_password(user_id, new_password):
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_pw, user_id))
        conn.commit()
        cursor.close()
        conn.close()
