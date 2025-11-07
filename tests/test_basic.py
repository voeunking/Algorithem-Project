def test_api_dashboard_stats(client):
    # Import here so the monkeypatch in conftest has already run
    from models.book_model import BookModel
    from models.member_model import MemberModel
    from models.transaction_model import TransactionModel

    # Add a book and a member
    BookModel.add_book('Test Book', 'Author Name', 'Pub', '2025', 'General', 3, 3)
    member_id = MemberModel.add_member('Jane Tester', 'jane@example.com', '555-0100', '123 Test St')

    books = BookModel.get_all()
    assert len(books) >= 1
    book_id = books[0]['id']

    # Issue the book
    TransactionModel.issue_book(member_id, book_id)

    # Call the API
    resp = client.get('/api/dashboard_stats')
    assert resp.status_code == 200
    data = resp.get_json()

    assert 'totalBooks' in data and data['totalBooks'] >= 1
    assert 'totalMembers' in data and data['totalMembers'] >= 1
    assert 'booksIssued' in data and data['booksIssued'] >= 1
