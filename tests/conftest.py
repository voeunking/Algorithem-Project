import pytest
import sqlite3
from app import app as flask_app
from models.book_model import BookModel
from models.member_model import MemberModel
from models.transaction_model import TransactionModel
from models.user_model import UserModel

@pytest.fixture(scope='session')
def test_app(tmp_path, monkeypatch):
    """Create a Flask app with a temporary SQLite DB for model operations.

    This fixture monkeypatches the `connect` methods for the sqlite-backed models
    to use a temporary file-based SQLite DB under pytest's tmp_path. It also stubs
    a few UserModel methods to avoid MySQL calls during tests.
    """
    db_path = tmp_path / "test_library.db"
    db_path_str = str(db_path)

    def connect_factory():
        conn = sqlite3.connect(db_path_str)
        conn.row_factory = sqlite3.Row
        return conn

    # Monkeypatch the models to use the temporary DB
    monkeypatch.setattr(BookModel, 'connect', staticmethod(connect_factory))
    monkeypatch.setattr(MemberModel, 'connect', staticmethod(connect_factory))
    monkeypatch.setattr(TransactionModel, 'connect', staticmethod(connect_factory))

    # Stub UserModel DB interactions so tests don't require MySQL
    monkeypatch.setattr(UserModel, 'get_profile_image', staticmethod(lambda uid: None))
    monkeypatch.setattr(UserModel, 'ensure_profile_image_column', staticmethod(lambda: None))

    # Create tables in the temporary DB
    BookModel.create_table()
    MemberModel.create_table()
    TransactionModel.create_table()

    flask_app.config['TESTING'] = True
    yield flask_app

@pytest.fixture
def client(test_app):
    with test_app.test_client() as client:
        with test_app.app_context():
            yield client
