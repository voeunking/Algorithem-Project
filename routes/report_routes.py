from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, timedelta
import sqlite3

report_bp = Blueprint('report_bp', __name__)

def connect_db():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn


def parse_dates(start, end):
    try:
        start_dt = datetime.strptime(start, '%Y-%m-%d') if start else datetime.now() - timedelta(days=30)
    except Exception:
        start_dt = datetime.now() - timedelta(days=30)
    try:
        end_dt = datetime.strptime(end, '%Y-%m-%d') if end else datetime.now()
    except Exception:
        end_dt = datetime.now()
    if end_dt < start_dt:
        start_dt, end_dt = end_dt, start_dt
    return start_dt, end_dt


@report_bp.route('/reports')
def reports_page():
    return render_template('reports.html')


@report_bp.route('/api/reports')
def api_reports():
    rtype = request.args.get('type', 'summary')
    start = request.args.get('start')
    end = request.args.get('end')
    start_dt, end_dt = parse_dates(start, end)
    start_s = start_dt.strftime('%Y-%m-%d 00:00:00')
    end_s = end_dt.strftime('%Y-%m-%d 23:59:59')

    conn = connect_db()
    cur = conn.cursor()

    if rtype == 'summary':
        cur.execute("SELECT COUNT(*) FROM books")
        total_books = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM members")
        total_members = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM transactions WHERE issue_date BETWEEN ? AND ?", (start_s, end_s))
        issued = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM transactions WHERE return_date BETWEEN ? AND ?", (start_s, end_s))
        returned = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM transactions WHERE return_date IS NULL")
        active_loans = cur.fetchone()[0]
        data = {
            'range': {'start': start_dt.strftime('%Y-%m-%d'), 'end': end_dt.strftime('%Y-%m-%d')},
            'totals': {
                'books': total_books,
                'members': total_members,
                'issued': issued,
                'returned': returned,
                'activeLoans': active_loans
            }
        }
        conn.close()
        return jsonify(data)

    if rtype == 'popular_books':
        limit = int(request.args.get('limit', 10))
        cur.execute(
            '''
            SELECT b.title, COUNT(*) AS c
            FROM transactions t
            JOIN books b ON b.id = t.book_id
            WHERE t.issue_date BETWEEN ? AND ?
            GROUP BY b.id
            ORDER BY c DESC
            LIMIT ?
            ''', (start_s, end_s, limit)
        )
        rows = cur.fetchall()
        conn.close()
        return jsonify({'items': [{'title': r['title'], 'count': r['c']} for r in rows]})

    if rtype == 'transactions_by_day':
        cur.execute(
            '''
            SELECT substr(issue_date, 1, 10) AS day, COUNT(*) AS c
            FROM transactions
            WHERE issue_date BETWEEN ? AND ?
            GROUP BY day
            ORDER BY day ASC
            ''', (start_s, end_s)
        )
        issued = {r['day']: r['c'] for r in cur.fetchall()}
        cur.execute(
            '''
            SELECT substr(return_date, 1, 10) AS day, COUNT(*) AS c
            FROM transactions
            WHERE return_date BETWEEN ? AND ?
            GROUP BY day
            ORDER BY day ASC
            ''', (start_s, end_s)
        )
        returned = {r['day']: r['c'] for r in cur.fetchall()}
        conn.close()
        days = []
        cur_day = start_dt.date()
        while cur_day <= end_dt.date():
            days.append(cur_day.strftime('%Y-%m-%d'))
            cur_day += timedelta(days=1)
        series = {
            'labels': days,
            'issued': [issued.get(d, 0) for d in days],
            'returned': [returned.get(d, 0) for d in days]
        }
        return jsonify(series)

    conn.close()
    return jsonify({'error': 'unknown report type'}), 400
