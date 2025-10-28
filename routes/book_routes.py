from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.book_model import BookModel
from models.member_model import MemberModel

# =====================
# BOOK BLUEPRINT
# =====================
book_bp = Blueprint('book_bp', __name__, url_prefix='/books')

# View all books
@book_bp.route('/')
def view_books():
    """Display all books in the database."""
    # Render page; data will be loaded via JS from /books/api
    return render_template('books.html')

# Books JSON API (list with filters/pagination)
@book_bp.route('/api', methods=['GET'])
def api_books_list():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    sort = request.args.get('sort', 'title')
    order = request.args.get('order', 'asc')
    try:
        page = max(1, int(request.args.get('page', 1)))
    except Exception:
        page = 1
    try:
        per_page = min(100, max(1, int(request.args.get('per_page', 10))))
    except Exception:
        per_page = 10

    allowed_sort = {'title','author','publisher','year_published','category','available_copies','total_copies','id'}
    if sort not in allowed_sort:
        sort = 'title'
    order_sql = 'DESC' if order.lower() == 'desc' else 'ASC'

    conn = BookModel.connect()
    cur = conn.cursor()
    where = []
    params = []
    if q:
        where.append('(title LIKE ? OR author LIKE ? OR publisher LIKE ? OR category LIKE ?)')
        like = f"%{q}%"
        params.extend([like, like, like, like])
    if category:
        where.append('category = ?')
        params.append(category)
    where_sql = ('WHERE ' + ' AND '.join(where)) if where else ''

    cur.execute(f'SELECT COUNT(*) FROM books {where_sql}', params)
    total = cur.fetchone()[0]

    offset = (page - 1) * per_page
    cur.execute(
        f'''SELECT id, title, author, publisher, year_published, category, total_copies, available_copies
            FROM books {where_sql}
            ORDER BY {sort} {order_sql}
            LIMIT ? OFFSET ?''',
        params + [per_page, offset]
    )
    rows = cur.fetchall()
    conn.close()
    items = [
        {
            'id': r['id'],
            'title': r['title'],
            'author': r['author'],
            'publisher': r['publisher'],
            'year_published': r['year_published'],
            'category': r['category'],
            'total_copies': r['total_copies'],
            'available_copies': r['available_copies']
        } for r in rows
    ]
    return jsonify({'total': total, 'page': page, 'per_page': per_page, 'items': items})

# Popular books page
@book_bp.route('/popular', methods=['GET'])
def popular_books_page():
    return render_template('popular_books.html')

# Popular books API
@book_bp.route('/api/popular', methods=['GET'])
def api_popular_books():
    from datetime import datetime, timedelta
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    sort = request.args.get('sort', 'count')
    order = request.args.get('order', 'desc')
    try:
        limit = max(1, min(100, int(request.args.get('limit', 20))))
    except Exception:
        limit = 20
    start = request.args.get('start')
    end = request.args.get('end')

    # Parse date range
    def parse_date(s, default):
        try:
            return datetime.strptime(s, '%Y-%m-%d') if s else default
        except Exception:
            return default
    end_dt = parse_date(end, datetime.now())
    start_dt = parse_date(start, end_dt - timedelta(days=30))
    if end_dt < start_dt:
        start_dt, end_dt = end_dt, start_dt
    start_s = start_dt.strftime('%Y-%m-%d 00:00:00')
    end_s = end_dt.strftime('%Y-%m-%d 23:59:59')

    conn = BookModel.connect()
    cur = conn.cursor()

    where = ['t.issue_date BETWEEN ? AND ?']
    params = [start_s, end_s]
    if q:
        where.append('(b.title LIKE ? OR b.author LIKE ? OR b.publisher LIKE ? OR b.category LIKE ?)')
        like = f"%{q}%"
        params.extend([like, like, like, like])
    if category:
        where.append('b.category = ?')
        params.append(category)
    where_sql = ' AND '.join(where)

    allowed_sort = {'count','title','available_copies','total_copies'}
    if sort not in allowed_sort:
        sort = 'count'
    order_sql = 'DESC' if order.lower() == 'desc' else 'ASC'

    cur.execute(f'''
        SELECT 
            b.id,
            b.title,
            b.author,
            b.publisher,
            b.category,
            b.total_copies,
            b.available_copies,
            COUNT(*) as count
        FROM transactions t
        JOIN books b ON b.id = t.book_id
        WHERE {where_sql}
        GROUP BY b.id
        ORDER BY {sort} {order_sql}
        LIMIT ?
    ''', params + [limit])
    rows = cur.fetchall()
    conn.close()

    items = []
    for r in rows:
        items.append({
            'id': r['id'],
            'title': r['title'],
            'author': r['author'],
            'publisher': r['publisher'],
            'category': r['category'],
            'total_copies': r['total_copies'],
            'available_copies': r['available_copies'],
            'count': r['count']
        })
    return jsonify({
        'range': {'start': start_dt.strftime('%Y-%m-%d'), 'end': end_dt.strftime('%Y-%m-%d')},
        'items': items
    })

# Categories endpoint for filters
@book_bp.route('/api/categories', methods=['GET'])
def api_books_categories():
    conn = BookModel.connect()
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT category FROM books WHERE category IS NOT NULL AND TRIM(category) != "" ORDER BY category ASC')
    cats = [r[0] for r in cur.fetchall()]
    conn.close()
    return jsonify({'categories': cats})

# Categories page (frontend)
@book_bp.route('/categories', methods=['GET'])
def categories_page():
    return render_template('categories.html')

# Categories stats API
@book_bp.route('/api/categories_stats', methods=['GET'])
def api_categories_stats():
    q = request.args.get('q', '').strip()
    sort = request.args.get('sort', 'category')
    order = request.args.get('order', 'asc')
    try:
        page = max(1, int(request.args.get('page', 1)))
    except Exception:
        page = 1
    try:
        per_page = min(100, max(1, int(request.args.get('per_page', 10))))
    except Exception:
        per_page = 10

    allowed_sort = {'category','total','available','authors','availability_pct'}
    if sort not in allowed_sort:
        sort = 'category'
    order_sql = 'DESC' if order.lower() == 'desc' else 'ASC'

    conn = BookModel.connect()
    cur = conn.cursor()
    where = ""
    params = []
    if q:
        where = "WHERE category LIKE ?"
        params.append(f"%{q}%")

    cur.execute(f'''SELECT COUNT(*) FROM (
        SELECT COALESCE(NULLIF(TRIM(category), ''), 'Uncategorized') AS c
        FROM books {where}
        GROUP BY c
    ) t''', params)
    total = cur.fetchone()[0]

    offset = (page - 1) * per_page
    # Build main query
    cur.execute(f'''
        SELECT 
            COALESCE(NULLIF(TRIM(category), ''), 'Uncategorized') AS category,
            COUNT(*) AS total,
            SUM(COALESCE(available_copies,0)) AS available,
            COUNT(DISTINCT COALESCE(author,'')) AS authors
        FROM books
        {where}
        GROUP BY category
        ORDER BY {sort} {order_sql}
        LIMIT ? OFFSET ?
    ''', params + [per_page, offset])
    rows = cur.fetchall()
    conn.close()

    items = []
    for r in rows:
        total_c = int(r['total']) if r['total'] is not None else 0
        avail_c = int(r['available']) if r['available'] is not None else 0
        pct = (avail_c / total_c * 100.0) if total_c > 0 else 0.0
        items.append({
            'category': r['category'],
            'total': total_c,
            'available': avail_c,
            'authors': int(r['authors']) if r['authors'] is not None else 0,
            'availability_pct': round(pct, 2)
        })

    return jsonify({'total': total, 'page': page, 'per_page': per_page, 'items': items})

# Add a new book
@book_bp.route('/add', methods=['GET', 'POST'])
def add_book():
    """Add a new book (form + insert)."""
    if request.method == 'POST':
        data = request.form
        title = data.get('title')
        author = data.get('author')
        publisher = data.get('publisher')
        year = data.get('year')
        category = data.get('category')
        total = data.get('total')
        available = data.get('available')

        BookModel.add_book(title, author, publisher, year, category, total, available)
        flash("Book added successfully!", "success")
        return redirect(url_for('book_bp.view_books'))

    return render_template('add_book.html')

# Delete a book
@book_bp.route('/delete/<int:id>')
def delete_book(id):
    """Delete a book by its ID."""
    BookModel.delete_book(id)
    flash("Book deleted successfully.", "info")
    return redirect(url_for('book_bp.view_books'))

# =====================
# MEMBER BLUEPRINT
# =====================
member_bp = Blueprint('member_bp', __name__, url_prefix='/members')

# View all members
@member_bp.route('/')
def view_members():
    """Display all members in the database."""
    members = MemberModel.get_all()
    return render_template('member.html', members=members)

# Show Add Member form
@member_bp.route('/add', methods=['GET'])
def show_add_member_form():
    """Render form to add new member."""
    return render_template('add_member.html')

# Add new member
@member_bp.route('/add', methods=['POST'])
def add_member():
    """Handle adding a new member to the database."""
    data = request.form
    MemberModel.add_member(
        data.get('full_name'),
        data.get('email'),
        data.get('phone'),
        data.get('address')
    )
    flash("Member added successfully!", "success")
    return redirect(url_for('member_bp.view_members'))

# Delete member
@member_bp.route('/delete/<int:id>')
def delete_member(id):
    """Delete a member by ID."""
    MemberModel.delete_member(id)
    flash("Member deleted successfully.", "info")
    return redirect(url_for('member_bp.view_members'))
