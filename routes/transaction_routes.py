from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.transaction_model import TransactionModel
from models.book_model import BookModel
from models.member_model import MemberModel
from datetime import datetime

transaction_bp = Blueprint('transaction_bp', __name__, url_prefix='/transactions')

# =====================
# VIEW ALL TRANSACTIONS
# =====================
@transaction_bp.route('/')
def view_transactions():
    """Display all transactions with member and book info."""
    transactions = TransactionModel.get_all()
    total = len(transactions)
    issued = sum(1 for t in transactions if not t['return_date'])
    returned = total - issued
    members = MemberModel.get_all()
    books = BookModel.get_all()
    return render_template(
        'transactions.html',
        transactions=transactions,
        members=members,
        books=books,
        stats={"total": total, "issued": issued, "returned": returned}
    )

# =====================
# ISSUE A BOOK
# =====================
@transaction_bp.route('/issue', methods=['GET', 'POST'])
def issue_book():
    members = MemberModel.get_all()
    books = BookModel.get_all()

    if request.method == 'POST':
        member_id = request.form['member_id']
        book_id = request.form['book_id']
        issue_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if book is available
        book = BookModel.get_by_id(book_id)
        if book['available_copies'] < 1:
            flash("Book is not available for issue.", "danger")
            return redirect(url_for('transaction_bp.issue_book'))

        # Issue book
        TransactionModel.issue_book(member_id, book_id, issue_date)
        BookModel.decrease_available(book_id)
        flash("Book issued successfully.", "success")
        return redirect(url_for('transaction_bp.view_transactions'))

    today = datetime.today().strftime("%Y-%m-%d")
    return render_template('issue_book.html', members=members, books=books, today=today)

# =====================
# RETURN A BOOK
# =====================
@transaction_bp.route('/return/<int:transaction_id>')
def return_book(transaction_id):
    transaction = TransactionModel.get_by_id(transaction_id)
    if transaction and not transaction['return_date']:
        TransactionModel.return_book(transaction_id)
        BookModel.increase_available(transaction['book_id'])
        flash("Book returned successfully.", "success")
    return redirect(url_for('transaction_bp.view_transactions'))

# =====================
# DELETE A TRANSACTION
# =====================
@transaction_bp.route('/delete/<int:transaction_id>')
def delete_transaction(transaction_id):
    TransactionModel.delete_transaction(transaction_id)
    flash("Transaction deleted.", "info")
    return redirect(url_for('transaction_bp.view_transactions'))
