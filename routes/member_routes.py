from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import date
import sqlite3
from models.member_model import MemberModel

member_bp = Blueprint('member_bp', __name__, url_prefix='/members')

# =====================
# VIEW ALL MEMBERS
# =====================
@member_bp.route('/')
def view_members():
    """Display all members in the database."""
    members = MemberModel.get_all()
    return render_template('members.html', members=members)

# =====================
# ADD MEMBER
# =====================
# Show add member form
@member_bp.route('/add', methods=['GET'])
def show_add_member_form():
    return render_template('add_member.html', today=date.today().isoformat())

# Handle add member submission
@member_bp.route('/add', methods=['POST'])
def add_member():
    data = request.form
    first_name = (data.get('first_name') or '').strip()
    last_name = (data.get('last_name') or '').strip()
    full_name = (data.get('full_name') or '').strip() or f"{first_name} {last_name}".strip()
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')
    date_of_birth = data.get('date_of_birth')
    gender = data.get('gender')
    city = data.get('city')
    state = data.get('state')
    postal_code = data.get('postal_code')
    member_type = data.get('member_type')
    membership_date = data.get('membership_date')
    institution = data.get('institution')
    emergency_contact_name = data.get('emergency_contact_name')
    emergency_contact_phone = data.get('emergency_contact_phone')
    notes = data.get('notes')
    terms_agreed = 1 if data.get('terms_agreed') else 0

    if not full_name:
        flash("Full name is required.", "danger")
        return redirect(url_for('member_bp.show_add_member_form'))

    MemberModel.add_member(
        full_name, email, phone, address,
        first_name=first_name, last_name=last_name,
        date_of_birth=date_of_birth, gender=gender,
        city=city, state=state, postal_code=postal_code,
        member_type=member_type, membership_date=membership_date, institution=institution,
        emergency_contact_name=emergency_contact_name, emergency_contact_phone=emergency_contact_phone,
        notes=notes, terms_agreed=terms_agreed
    )
    flash("Member added successfully!", "success")
    return redirect(url_for('member_bp.view_members'))

# =====================
# ADD MEMBER (JSON API)
# =====================
@member_bp.route('/api/add', methods=['POST'])
def api_add_member():
    data = request.get_json(silent=True) or {}
    first_name = (data.get('first_name') or '').strip()
    last_name = (data.get('last_name') or '').strip()
    full_name = (data.get('full_name') or '').strip() or f"{first_name} {last_name}".strip()
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')
    date_of_birth = data.get('date_of_birth')
    gender = data.get('gender')
    city = data.get('city')
    state = data.get('state')
    postal_code = data.get('postal_code')
    member_type = data.get('member_type')
    membership_date = data.get('membership_date')
    institution = data.get('institution')
    emergency_contact_name = data.get('emergency_contact_name')
    emergency_contact_phone = data.get('emergency_contact_phone')
    notes = data.get('notes')
    terms_agreed = 1 if data.get('terms_agreed') else 0

    if not full_name:
        return jsonify({"success": False, "error": "full_name is required"}), 400

    new_id = MemberModel.add_member(
        full_name, email, phone, address,
        first_name=first_name, last_name=last_name,
        date_of_birth=date_of_birth, gender=gender,
        city=city, state=state, postal_code=postal_code,
        member_type=member_type, membership_date=membership_date, institution=institution,
        emergency_contact_name=emergency_contact_name, emergency_contact_phone=emergency_contact_phone,
        notes=notes, terms_agreed=terms_agreed
    )

    return jsonify({
        "success": True,
        "id": new_id,
        "message": "Member added successfully"
    }), 201

# =====================
# EDIT MEMBER
# =====================
# Show edit member form
@member_bp.route('/edit/<int:id>', methods=['GET'])
def show_edit_member_form(id):
    member = None
    members = MemberModel.get_all()
    for m in members:
        if m['id'] == id:
            member = m
            break
    if not member:
        flash("Member not found.", "danger")
        return redirect(url_for('member_bp.view_members'))

    return render_template('edit_member.html', member=member)

# Handle edit submission
@member_bp.route('/edit/<int:id>', methods=['POST'])
def edit_member(id):
    data = request.form
    full_name = data.get('full_name')
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')

    if not full_name:
        flash("Full name is required.", "danger")
        return redirect(url_for('member_bp.show_edit_member_form', id=id))

    MemberModel.update_member(id, full_name, email, phone, address)
    flash("Member updated successfully!", "success")
    return redirect(url_for('member_bp.view_members'))

# =====================
# DELETE MEMBER
# =====================
@member_bp.route('/delete/<int:id>')
def delete_member(id):
    MemberModel.delete_member(id)
    flash("Member deleted.", "info")
    return redirect(url_for('member_bp.view_members'))

# =====================
# OVERDUE MEMBERS
# =====================
@member_bp.route('/overdue', methods=['GET'])
def overdue_members_page():
    return render_template('overdue_members.html')

@member_bp.route('/api/overdue', methods=['GET'])
def api_overdue_members():
    """List overdue borrowings (unreturned beyond N days).
    Params: q (search member/book), days (min overdue days, default 14), sort (days_overdue|member|book|issue_date), order, page, per_page
    """
    q = (request.args.get('q') or '').strip()
    try:
        days = max(1, int(request.args.get('days', 14)))
    except Exception:
        days = 14
    sort = request.args.get('sort', 'days_overdue')
    order = request.args.get('order', 'desc')
    try:
        page = max(1, int(request.args.get('page', 1)))
    except Exception:
        page = 1
    try:
        per_page = min(100, max(1, int(request.args.get('per_page', 10))))
    except Exception:
        per_page = 10

    allowed_sort = {
        'days_overdue': 'days_overdue',
        'member': 'member_name',
        'book': 'book_title',
        'issue_date': 'issue_date'
    }
    sort_sql = allowed_sort.get(sort, 'days_overdue')
    order_sql = 'DESC' if order.lower() == 'desc' else 'ASC'

    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    where = ["t.return_date IS NULL", f"julianday('now') - julianday(t.issue_date) > ?"]
    params = [days]
    if q:
        where.append("(m.full_name LIKE ? OR b.title LIKE ?)")
        like = f"%{q}%"
        params.extend([like, like])
    where_sql = ' AND '.join(where)

    # Count total
    cur.execute(f'''
        SELECT COUNT(*)
        FROM transactions t
        JOIN members m ON m.id = t.member_id
        JOIN books b ON b.id = t.book_id
        WHERE {where_sql}
    ''', params)
    total = cur.fetchone()[0]

    offset = (page - 1) * per_page
    cur.execute(f'''
        SELECT 
            t.id as transaction_id,
            m.id as member_id,
            m.full_name as member_name,
            b.id as book_id,
            b.title as book_title,
            t.issue_date as issue_date,
            CAST(ROUND(julianday('now') - julianday(t.issue_date)) AS INTEGER) as days_overdue
        FROM transactions t
        JOIN members m ON m.id = t.member_id
        JOIN books b ON b.id = t.book_id
        WHERE {where_sql}
        ORDER BY {sort_sql} {order_sql}
        LIMIT ? OFFSET ?
    ''', params + [per_page, offset])
    rows = cur.fetchall()
    conn.close()

    items = []
    for r in rows:
        items.append({
            'transaction_id': r['transaction_id'],
            'member_id': r['member_id'],
            'member_name': r['member_name'],
            'book_id': r['book_id'],
            'book_title': r['book_title'],
            'issue_date': r['issue_date'],
            'days_overdue': r['days_overdue']
        })

    return jsonify({'total': total, 'page': page, 'per_page': per_page, 'days': days, 'items': items})
