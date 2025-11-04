# Library Management System - Developer Guide

## Overview
បច្ចុប្បន្នភាពនៃ Library Management System ត្រូវបានបង្កើតឡើងដោយប្រើ Python Flask និង MySQL។ ឯកសារនេះរៀបរាប់លម្អិតអំពីរបៀបដែលប្រព័ន្ធដំណើរការ និងរបៀបអភិវឌ្ឍន៍បន្ថែម។

## មុខងារសំខាន់ៗ (Core Functions)

### 1. ការគ្រប់គ្រងអ្នកប្រើប្រាស់ (User Management)

#### a. ការបង្កើតគណនី (Registration)
```python
@auth_bp.route('/register', methods=['POST'])
```
- **គោលបំណង**: បង្កើតគណនីថ្មីសម្រាប់បណ្ណារក្ស
- **ការងារ**:
  - ផ្ទៀងផ្ទាត់ពាក្យសម្ងាត់
  - បង្កើតគណនីក្នុងទិន្នន័យ
  - រក្សាទុកពាក្យសម្ងាត់ដោយសុវត្ថិភាព

#### b. ការចូលប្រើ (Login)
```python
@auth_bp.route('/login', methods=['POST'])
```
- **គោលបំណង**: ផ្ទៀងផ្ទាត់អ្នកប្រើប្រាស់
- **ការងារ**:
  - ត្រួតពិនិត្យអ៊ីមែល
  - ផ្ទៀងផ្ទាត់ពាក្យសម្ងាត់
  - បង្កើត session សម្រាប់អ្នកប្រើប្រាស់

### 2. ការគ្រប់គ្រងសៀវភៅ (Book Management)

#### a. បន្ថែមសៀវភៅ (Add Book)
```python
@book_bp.route('/add', methods=['POST'])
```
- **គោលបំណង**: បន្ថែមសៀវភៅថ្មី
- **ទិន្នន័យត្រូវការ**:
  - ចំណងជើង
  - អ្នកនិពន្ធ
  - ប្រភេទ
  - ចំនួនច្បាប់

#### b. ស្វែងរកសៀវភៅ (Search Books)
```python
@book_bp.route('/api', methods=['GET'])
```
- **គោលបំណង**: ស្វែងរកសៀវភៅ
- **លក្ខណៈពិសេស**:
  - ស្វែងរកតាមចំណងជើង/អ្នកនិពន្ធ
  - តម្រងតាមប្រភេទ
  - តម្រៀបលំដាប់លទ្ធផល

### 3. ការគ្រប់គ្រងសមាជិក (Member Management)

#### a. បន្ថែមសមាជិក (Add Member)
```python
@member_bp.route('/add', methods=['POST'])
```
- **គោលបំណង**: ចុះឈ្មោះសមាជិកថ្មី
- **ទិន្នន័យត្រូវការ**:
  - ឈ្មោះពេញ
  - អ៊ីមែល
  - លេខទូរស័ព្ទ
  - អាសយដ្ឋាន

#### b. កែប្រែព័ត៌មានសមាជិក (Edit Member)
```python
@member_bp.route('/edit/<int:id>', methods=['POST'])
```
- **គោលបំណង**: កែប្រែព័ត៌មានសមាជិក
- **ការងារ**:
  - ធ្វើបច្ចុប្បន្នភាពព័ត៌មានទំនាក់ទំនង
  - កែប្រែស្ថានភាពសមាជិក

### 4. ការគ្រប់គ្រងការខ្ចី-សង (Transaction Management)

#### a. ការខ្ចីសៀវភៅ (Issue Book)
```python
@transaction_bp.route('/issue', methods=['POST'])
```
- **គោលបំណង**: កត់ត្រាការខ្ចីសៀវភៅ
- **ការងារ**:
  - ពិនិត្យស្ថានភាពសៀវភៅ
  - បង្កើតកំណត់ត្រាការខ្ចី
  - កែប្រែចំនួនសៀវភៅដែលមាន

#### b. ការសងសៀវភៅ (Return Book)
```python
@transaction_bp.route('/return/<int:transaction_id>')
```
- **គោលបំណង**: កត់ត្រាការសងសៀវភៅ
- **ការងារ**:
  - កែប្រែស្ថានភាពការខ្ចី
  - បន្ថែមចំនួនសៀវភៅដែលមាន
  - កត់ត្រាកាលបរិច្ឆេទសង

## ការរៀបចំទិន្នន័យ (Database Structure)

### 1. តារាងអ្នកប្រើប្រាស់ (users)
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    password VARCHAR(255)
);
```

### 2. តារាងសៀវភៅ (books)
```sql
CREATE TABLE books (
    id INT PRIMARY KEY,
    title VARCHAR(255),
    author VARCHAR(255),
    category VARCHAR(100),
    total_copies INT,
    available_copies INT
);
```

### 3. តារាងសមាជិក (members)
```sql
CREATE TABLE members (
    id INT PRIMARY KEY,
    full_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT
);
```

### 4. តារាងការខ្ចី-សង (transactions)
```sql
CREATE TABLE transactions (
    id INT PRIMARY KEY,
    member_id INT,
    book_id INT,
    issue_date DATE,
    return_date DATE,
    status VARCHAR(20)
);
```

## គំរូកូដសំខាន់ៗ (Code Examples)

### 1. ការខ្ចីសៀវភៅ (Issue Book)
```python
def issue_book(member_id, book_id):
    # ពិនិត្យស្ថានភាពសៀវភៅ
    book = BookModel.get_by_id(book_id)
    if book['available_copies'] < 1:
        raise Exception("សៀវភៅអស់ពីស្តុក")
    
    # បង្កើតការខ្ចី
    issue_date = datetime.now()
    transaction_id = TransactionModel.issue_book(
        member_id, 
        book_id, 
        issue_date
    )
    
    # កែប្រែចំនួនសៀវភៅ
    BookModel.decrease_available(book_id)
    
    return transaction_id
```

### 2. ការស្វែងរកសៀវភៅ (Search Books)
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

## ការគ្រប់គ្រងកំហុស (Error Handling)

```python
try:
    # កូដប្រតិបត្តិការ
    result = perform_operation()
except DatabaseError as e:
    flash("មានបញ្ហាជាមួយមូលដ្ឋានទិន្នន័យ", "danger")
    log_error(e)
except ValidationError as e:
    flash(str(e), "warning")
except Exception as e:
    flash("មានបញ្ហាកើតឡើង", "danger")
    log_error(e)
```

## គោលការណ៍អភិវឌ្ឍន៍ (Development Guidelines)

### 1. រចនាបថកូដ (Code Style)
- អនុវត្តតាម PEP 8
- ប្រើឈ្មោះអថេរដែលមានន័យ
- សរសេរ docstrings
- បន្ថែមកំណត់ចំណាំលើកូដស្មុគស្មាញ

### 2. ប្រតិបត្តិការទិន្នន័យ (Database Operations)
- ប្រើ parameterized queries ជានិច្ច
- បិទការតភ្ជាប់ទិន្នន័យ
- គ្រប់គ្រង transaction rollbacks

### 3. សុវត្ថិភាព (Security)
- អ៊ិនគ្រីបពាក្យសម្ងាត់ជាមួយ bcrypt
- ផ្ទៀងផ្ទាត់ទិន្នន័យបញ្ចូល
- ប្រើ CSRF protection
- សម្អាតទិន្នន័យមុនបង្ហាញ

### 4. ការធ្វើតេស្ត (Testing)
- សរសេរតេស្តឯកតា
- ធ្វើតេស្ត API endpoints
- ផ្ទៀងផ្ទាត់ការបញ្ជូនទម្រង់

## ឧទាហរណ៍ API Endpoints

### 1. សៀវភៅ (Books)
```python
# បង្ហាញសៀវភៅទាំងអស់
GET /books/api

# បង្ហាញសៀវភៅពេញនិយម
GET /books/api/popular

# បង្ហាញប្រភេទសៀវភៅ
GET /books/api/categories
```

### 2. សមាជិក (Members)
```python
# បន្ថែមសមាជិកថ្មី
POST /members/api/add

# បង្ហាញសមាជិកដែលហួសកាលកំណត់
GET /members/api/overdue
```

### 3. ការផ្ទៀងផ្ទាត់ (Authentication)
```python
# ចូលប្រើប្រាស់
POST /auth/login

# ចុះឈ្មោះ
POST /auth/register

# កែប្រែព័ត៌មានផ្ទាល់ខ្លួន
POST /auth/update_profile
```

## ការដំឡើង និងការរៀបចំ (Installation & Setup)

### 1. តម្រូវការមុន (Prerequisites)
- Python 3.10+
- MySQL Server
- pip (Python package manager)

### 2. ដំឡើងកម្មវិធី (Installation)
```bash
# Clone repository
git clone https://github.com/voeunking/library_management.git
cd library_management

# ដំឡើង dependencies
pip install -r requirements.txt

# រៀបចំមូលដ្ឋានទិន្នន័យ
mysql -u root -p < database_setup.sql
```

### 3. ការកំណត់រចនាសម្ព័ន្ធ (Configuration)
បង្កើតឯកសារ `config.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'library_db'
}
```

### 4. ដំណើរការកម្មវិធី (Run Application)
```bash
python app.py
```

## ការថែទាំ និងការធ្វើបច្ចុប្បន្នភាព (Maintenance & Updates)

### 1. ការធ្វើបច្ចុប្បន្នភាពមូលដ្ឋានទិន្នន័យ (Database Updates)
- បង្កើត backup មុនធ្វើការផ្លាស់ប្តូរ
- ប្រើ database migrations
- ធ្វើតេស្តលើទិន្នន័យសាកល្បង

### 2. ការថែទាំកូដ (Code Maintenance)
- ធ្វើឱ្យកូដមានសណ្តាប់ធ្នាប់
- កែលម្អដំណើរការ
- ធ្វើបច្ចុប្បន្នភាព dependencies

### 3. ការត្រួតពិនិត្យសុវត្ថិភាព (Security Checks)
- ពិនិត្យមើលភាពងាយរងគ្រោះ
- ធ្វើបច្ចុប្បន្នភាពកញ្ចប់សុវត្ថិភាព
- ត្រួតពិនិត្យ logs