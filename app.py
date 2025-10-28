from flask import Flask, render_template, redirect, url_for, session, jsonify, request, flash
from werkzeug.utils import secure_filename

# Import Blueprints
from routes.auth_routes import auth_bp               # Optional authentication routes
from routes.book_routes import book_bp               # Book management routes
from routes.member_routes import member_bp           # Member management routes
from routes.transaction_routes import transaction_bp # Transaction routes
from routes.report_routes import report_bp            # Reports routes

# Import Models
from models.book_model import BookModel
from models.member_model import MemberModel
from models.transaction_model import TransactionModel
from models.user_model import UserModel
import os

# =======================
# INITIALIZE APP
# =======================
app = Flask(__name__)
app.secret_key = "library_secret_key"  # For session handling security
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'avatars')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4 MB limit

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Ensure users table has profile_image column
try:
    UserModel.ensure_profile_image_column()
except Exception:
    pass

# =======================
# CREATE DATABASE TABLES
# =======================
BookModel.create_table()
MemberModel.create_table()
TransactionModel.create_table()

# =======================
# REGISTER BLUEPRINTS
# =======================
if 'auth_bp' in globals():
    app.register_blueprint(auth_bp, url_prefix='/auth')  # Optional
app.register_blueprint(book_bp, url_prefix='/books')
app.register_blueprint(member_bp, url_prefix='/members')
app.register_blueprint(transaction_bp, url_prefix='/transactions')
app.register_blueprint(report_bp)

# =======================
# HOME PAGE
# =======================
@app.route('/')
def index():
    """Home page — redirect to login if not authenticated, else show dashboard links."""
    if 'user_name' in session:
        return render_template('index.html', user=session['user_name'])
    # Fallback if auth_bp is not available
    return redirect(url_for('auth_bp.login')) if 'auth_bp' in globals() else """
        <h1>Library Management System</h1>
        <p>
            <a href='/books'>Books</a> |
            <a href='/members'>Members</a> |
            <a href='/transactions'>Transactions</a>
        </p>
    """

# =======================
# NAVIGATION ROUTES
# =======================
@app.route('/books_page')
def books_page():
    return redirect(url_for('book_bp.view_books'))

@app.route('/members_page')
def members_page():
    return redirect(url_for('member_bp.view_members'))

@app.route('/transactions_page')
def transactions_page():
    return redirect(url_for('transaction_bp.view_transactions'))

# =======================
# PROFILE PAGE AND API
# =======================
@app.route('/profile')
def profile_page():
    return render_template('profile.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/api/profile')
def api_profile():
    user = {
        "name": session.get('user_name', 'Guest')
    }
    avatar_rel = None
    uid = session.get('user_id')
    if uid:
        try:
            avatar_rel = UserModel.get_profile_image(uid)
        except Exception:
            avatar_rel = None
    # Aggregate counts
    bconn = BookModel.connect()
    bcur = bconn.cursor()
    bcur.execute('SELECT COUNT(*) as c FROM books')
    total_books = bcur.fetchone()[0]
    bconn.close()

    mconn = MemberModel.connect()
    mcur = mconn.cursor()
    mcur.execute('SELECT COUNT(*) as c FROM members')
    total_members = mcur.fetchone()[0]
    mconn.close()

    tconn = TransactionModel.connect()
    tcur = tconn.cursor()
    tcur.execute("SELECT COUNT(*) FROM transactions WHERE return_date IS NULL")
    active_loans = tcur.fetchone()[0]
    tcur.execute('''
        SELECT m.full_name AS member_name, b.title AS book_title, t.issue_date
        FROM transactions t
        JOIN members m ON m.id = t.member_id
        JOIN books b ON b.id = t.book_id
        ORDER BY t.issue_date DESC
        LIMIT 10
    ''')
    recent = [
        {"member": r[0], "book": r[1], "issue_date": r[2]} for r in tcur.fetchall()
    ]
    tconn.close()

    return jsonify({
        "user": {
            **user,
            "avatarUrl": (url_for('static', filename=avatar_rel) if avatar_rel else None)
        },
        "stats": {
            "totalBooks": total_books,
            "totalMembers": total_members,
            "activeLoans": active_loans
        },
        "recentTransactions": recent
    })

# =======================
# AVATAR UPLOAD
# =======================
@app.route('/profile/upload', methods=['POST'])
def upload_avatar():
    if 'user_id' not in session:
        flash('Please log in to upload an avatar.', 'warning')
        return redirect(url_for('auth_bp.login')) if 'auth_bp' in globals() else redirect(url_for('index'))

    if 'avatar' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('profile_page'))

    file = request.files['avatar']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('profile_page'))

    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()
    if ext not in {'.png', '.jpg', '.jpeg', '.gif', '.webp'}:
        flash('Invalid file type. Allowed: png, jpg, jpeg, gif, webp', 'danger')
        return redirect(url_for('profile_page'))

    # Save as user_id.ext to avoid duplicates
    new_name = f"{session['user_id']}{ext}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
    file.save(save_path)

    # Store relative path from static/ to use with url_for('static')
    rel_path = os.path.join('uploads', 'avatars', new_name).replace('\\', '/')
    try:
        UserModel.set_profile_image(session['user_id'], rel_path)
        flash('Avatar updated successfully.', 'success')
    except Exception as e:
        flash('Failed to save avatar.', 'danger')

    return redirect(url_for('profile_page'))

# =======================
# LOGOUT FUNCTIONALITY
# =======================

@app.route('/logout')
def logout():
    """Global logout route that works whether auth blueprint is present or not."""
    if 'auth_bp' in globals():
        return redirect(url_for('auth_bp.logout'))
    session.clear()
    return redirect(url_for('index'))

# =======================
# API ENDPOINTS
# =======================

@app.route('/api/dashboard_stats')
def api_dashboard_stats():
    # Aggregate counts
    bconn = BookModel.connect()
    bcur = bconn.cursor()
    bcur.execute('SELECT COUNT(*) as c FROM books')
    total_books = bcur.fetchone()[0]
    bconn.close()

    mconn = MemberModel.connect()
    mcur = mconn.cursor()
    mcur.execute('SELECT COUNT(*) as c FROM members')
    total_members = mcur.fetchone()[0]
    mconn.close()

    tconn = TransactionModel.connect()
    tcur = tconn.cursor()
    tcur.execute("SELECT COUNT(*) FROM transactions WHERE return_date IS NULL")
    books_issued = tcur.fetchone()[0]

    tcur.execute('''
        SELECT b.title AS book_title, COUNT(*) AS count
        FROM transactions t
        JOIN books b ON b.id = t.book_id
        GROUP BY b.id
        ORDER BY count DESC
        LIMIT 5
    ''')
    popular_books = [{"title": r[0], "count": r[1]} for r in tcur.fetchall()]

    tcur.execute('''
        SELECT m.full_name AS member_name, b.title AS book_title, t.issue_date
        FROM transactions t
        JOIN members m ON m.id = t.member_id
        JOIN books b ON b.id = t.book_id
        ORDER BY t.issue_date DESC
        LIMIT 5
    ''')
    recent_transactions = [
        {"member": r[0], "book": r[1], "issue_date": r[2]} for r in tcur.fetchall()
    ]
    tconn.close()

    data = {
        "totalBooks": total_books,
        "totalMembers": total_members,
        "booksIssued": books_issued,
        "popularBooks": popular_books,
        "recentTransactions": recent_transactions
    }
    return jsonify(data)

# =======================
# RUN FLASK APP
# =======================
if __name__ == '__main__':
    app.run(debug=True)
