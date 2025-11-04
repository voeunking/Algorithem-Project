# Library Management System - Developer Documentation

## Table of Contents
1. [Authentication Module](#authentication-module)
2. [Book Management Module](#book-management-module)
3. [Member Management Module](#member-management-module)
4. [Transaction Management Module](#transaction-management-module)
5. [Database Models](#database-models)
6. [API Endpoints](#api-endpoints)

## Authentication Module

### Routes (`auth_routes.py`)

#### 1. User Registration
```python
@auth_bp.route('/register', methods=['GET', 'POST'])
```
- **Purpose**: Create new user accounts for librarians
- **Functions**:
  - Validates password matching
  - Creates user in database with hashed password
  - Redirects to login page after success

#### 2. User Login
```python
@auth_bp.route('/login', methods=['GET', 'POST'])
```
- **Purpose**: Authenticate users and create sessions
- **Functions**:
  - Verifies email existence
  - Checks password using bcrypt
  - Creates session with user ID and name
  - Handles error messages for invalid credentials

#### 3. Profile Management
```python
@auth_bp.route('/update_profile', methods=['POST'])
```
- **Purpose**: Update user profile information
- **Functions**:
  - Updates name and email
  - Validates input data
  - Updates session information

## Book Management Module

### Routes (`book_routes.py`)

#### 1. View Books
```python
@book_bp.route('/')
```
- **Purpose**: Display all books in the library
- **Functions**:
  - Renders books template
  - Data loaded via AJAX from API endpoint

#### 2. Books API
```python
@book_bp.route('/api', methods=['GET'])
```
- **Purpose**: Provide book data with filtering and pagination
- **Parameters**:
  - `q`: Search query
  - `category`: Filter by category
  - `sort`: Sort field
  - `order`: Sort direction
  - `page`: Page number
  - `per_page`: Items per page

#### 3. Popular Books
```python
@book_bp.route('/api/popular', methods=['GET'])
```
- **Purpose**: Track and display most borrowed books
- **Features**:
  - Date range filtering
  - Category filtering
  - Sorting by various metrics

## Member Management Module

### Routes (`member_routes.py`)

#### 1. Member Registration
```python
@member_bp.route('/add', methods=['POST'])
```
- **Purpose**: Add new library members
- **Required Fields**:
  - Full name
  - Email
  - Phone
  - Address
- **Optional Fields**:
  - Date of birth
  - Gender
  - Emergency contact

#### 2. Member Management
```python
@member_bp.route('/edit/<int:id>', methods=['POST'])
```
- **Purpose**: Update member information
- **Functions**:
  - Edit member details
  - Update contact information
  - Manage membership status

#### 3. Overdue Members API
```python
@member_bp.route('/api/overdue', methods=['GET'])
```
- **Purpose**: Track members with overdue books
- **Features**:
  - Days overdue calculation
  - Search functionality
  - Sorting and filtering

## Transaction Management Module

### Routes (`transaction_routes.py`)

#### 1. Issue Book
```python
@transaction_bp.route('/issue', methods=['POST'])
```
- **Purpose**: Handle book borrowing
- **Functions**:
  - Checks book availability
  - Creates transaction record
  - Updates book copy count
  - Records issue date

#### 2. Return Book
```python
@transaction_bp.route('/return/<int:transaction_id>')
```
- **Purpose**: Process book returns
- **Functions**:
  - Updates transaction status
  - Increases available copies
  - Records return date

#### 3. Transaction History
```python
@transaction_bp.route('/')
```
- **Purpose**: View all transactions
- **Features**:
  - Lists all transactions
  - Shows current status
  - Displays statistics

## Database Models

### Book Model
- **Table**: `books`
- **Fields**:
  - `id`: Primary key
  - `title`: Book title
  - `author`: Author name
  - `category`: Book category
  - `total_copies`: Total copies owned
  - `available_copies`: Currently available copies

### Member Model
- **Table**: `members`
- **Fields**:
  - `id`: Primary key
  - `full_name`: Member's full name
  - `email`: Contact email
  - `phone`: Contact phone
  - `address`: Residential address

### Transaction Model
- **Table**: `transactions`
- **Fields**:
  - `id`: Primary key
  - `member_id`: Foreign key to members
  - `book_id`: Foreign key to books
  - `issue_date`: Date of borrowing
  - `return_date`: Date of return (null if not returned)
  - `status`: Current status

## API Endpoints

### Books API
- `GET /books/api`: List all books
- `GET /books/api/popular`: Get popular books
- `GET /books/api/categories`: List book categories

### Members API
- `POST /members/api/add`: Add new member
- `GET /members/api/overdue`: List overdue members

### Authentication API
- `POST /auth/login`: User login
- `POST /auth/register`: User registration
- `POST /auth/update_profile`: Update user profile
- `POST /auth/change_password`: Change password

## Code Examples

### Issue Book Transaction
```python
def issue_book(member_id, book_id):
    # Check book availability
    book = BookModel.get_by_id(book_id)
    if book['available_copies'] < 1:
        raise Exception("Book not available")
    
    # Create transaction
    issue_date = datetime.now()
    transaction_id = TransactionModel.issue_book(
        member_id, 
        book_id, 
        issue_date
    )
    
    # Update book count
    BookModel.decrease_available(book_id)
    
    return transaction_id
```

### Search Books Function
```python
def search_books(query, category=None, page=1, per_page=10):
    offset = (page - 1) * per_page
    where = []
    params = []
    
    if query:
        where.append('(title LIKE ? OR author LIKE ?)')
        params.extend([f"%{query}%", f"%{query}%"])
    
    if category:
        where.append('category = ?')
        params.append(category)
        
    where_sql = ' WHERE ' + ' AND '.join(where) if where else ''
    
    return BookModel.execute_query(
        f"SELECT * FROM books {where_sql} LIMIT ? OFFSET ?",
        params + [per_page, offset]
    )
```

## Error Handling

The system implements consistent error handling:

```python
try:
    # Operation code
    result = perform_operation()
except DatabaseError as e:
    flash("Database error occurred", "danger")
    log_error(e)
except ValidationError as e:
    flash(str(e), "warning")
except Exception as e:
    flash("An unexpected error occurred", "danger")
    log_error(e)
```

## Development Guidelines

1. **Code Style**
   - Follow PEP 8 guidelines
   - Use meaningful variable names
   - Add docstrings to functions
   - Comment complex logic

2. **Database Operations**
   - Always use parameterized queries
   - Close database connections
   - Handle transaction rollbacks

3. **Security**
   - Hash passwords with bcrypt
   - Validate all user input
   - Use CSRF protection
   - Sanitize data before display

4. **Testing**
   - Write unit tests for models
   - Test API endpoints
   - Validate form submissions