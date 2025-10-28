from flask import Blueprint, render_template, request, redirect, url_for
from models.book_model import BookModel
from models.member_model import MemberModel

# =======================
# BLUEPRINTS
# =======================
book_bp = Blueprint('book_bp', __name__, url_prefix='/books')
member_bp = Blueprint('member_bp', __name__, url_prefix='/members')


# =======================
# BOOK ROUTES
# =======================
@book_bp.route('/')
def view_books():
    books = BookModel.get_all()
    return render_template('books.html', books=books)

@book_bp.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        data = request.form
        BookModel.add_book(
            data['isbn'],
            data['title'],
            data['author'],
            data['publisher'],
            data['year'],
            data['category'],
            data['total'],
            data['available']
        )
        return redirect(url_for('book_bp.view_books'))
    return render_template('add_book.html')

@book_bp.route('/delete/<int:id>')
def delete_book(id):
    BookModel.delete_book(id)
    return redirect(url_for('book_bp.view_books'))


# =======================
# MEMBER ROUTES
# =======================
@member_bp.route('/')
def view_members():
    members = MemberModel.get_all()
    return render_template('member.html', members=members)

@member_bp.route('/add', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        data = request.form
        MemberModel.add_member(
            data['full_name'],
            data['email'],
            data['phone'],
            data['address']
        )
        return redirect(url_for('member_bp.view_members'))
    return render_template('add_member.html')

@member_bp.route('/delete/<int:id>')
def delete_member(id):
    MemberModel.delete_member(id)
    return redirect(url_for('member_bp.view_members'))
