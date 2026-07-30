# Khóa học PySide6 từ A-Z

# Buổi 18: SQLite + Repository Pattern - Xây dựng ứng dụng quản lý dữ liệu chuyên nghiệp

> **Đây là buổi học cực kỳ quan trọng.**
> 
> Từ buổi này trở đi, chúng ta sẽ chuyển từ việc tạo giao diện sang xây dựng **phần mềm thực tế**.

Sau buổi học này, bạn sẽ:

  * Hiểu cách tổ chức ứng dụng theo nhiều tầng (Layered Architecture). 
  * Kết nối PySide6 với SQLite. 
  * Xây dựng Repository Pattern. 
  * Thực hiện CRUD (Create, Read, Update, Delete). 
  * Kết hợp `QTableView` với `QAbstractTableModel`. 
  * Chuẩn bị nền tảng để sau này thay SQLite bằng PostgreSQL hoặc MySQL mà gần như không phải sửa giao diện. 



* * *

# 1\. Kiến trúc của một phần mềm chuyên nghiệp

Đến thời điểm này, **không nên viết tất cả trong`main.py`**.

Một ứng dụng quản lý sinh viên nên có cấu trúc:
    
    
    student_manager/
    │
    ├── main.py
    │
    ├── models/
    │   ├── student.py
    │   └── student_table_model.py
    │
    ├── repositories/
    │   └── student_repository.py
    │
    ├── services/
    │   └── student_service.py
    │
    ├── views/
    │   ├── main_window.py
    │   └── student_dialog.py
    │
    ├── controllers/
    │   └── student_controller.py
    │
    ├── database/
    │   ├── database.py
    │   └── schema.sql
    │
    └── resources/

Đây là cấu trúc được nhiều dự án PySide6 sử dụng.

* * *

# 2\. Kiến trúc hoạt động
    
    
    MainWindow
    
    ↓
    
    Controller
    
    ↓
    
    Repository
    
    ↓
    
    SQLite

Trong đó:

## View

Chỉ hiển thị giao diện.

Không viết SQL.

* * *

## Controller

Điều phối.

Ví dụ:
    
    
    Nhấn nút
    
    ↓
    
    Repository
    
    ↓
    
    Model
    
    ↓
    
    View

* * *

## Repository

Làm việc với SQLite.

Ví dụ:
    
    
    insert()
    
    update()
    
    delete()
    
    find()
    
    find_all()

* * *

## Database

Chỉ lưu dữ liệu.

* * *

# 3\. Vì sao cần Repository?

Sai:
    
    
    button.clicked.connect(
        lambda:
        cursor.execute(...)
    )

SQL nằm trong giao diện.

Sau này rất khó bảo trì.

* * *

Đúng:
    
    
    repository.add_student(...)

Repository tự xử lý SQL.

* * *

# 4\. Database đầu tiên
    
    
    import sqlite3
    
    conn = sqlite3.connect("students.db")

Tạo Cursor:
    
    
    cursor = conn.cursor()

* * *

# 5\. Tạo bảng
    
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
    
        id INTEGER PRIMARY KEY,
    
        name TEXT,
    
        age INTEGER,
    
        email TEXT,
    
        classroom TEXT
    
    )
    """)

Lưu:
    
    
    conn.commit()

* * *

# 6\. Student Entity
    
    
    class Student:
    
        def __init__(
            self,
            id,
            name,
            age,
            email,
            classroom
        ):
    
            self.id = id
    
            self.name = name
    
            self.age = age
    
            self.email = email
    
            self.classroom = classroom

Entity chỉ chứa dữ liệu.

Không chứa SQL.

* * *

# 7\. Database Class

Tạo:
    
    
    class Database:
    
        def __init__(self):
    
            self.conn = sqlite3.connect(
                "students.db"
            )
    
            self.cursor = self.conn.cursor()

Mọi Repository dùng chung.

* * *

# 8\. StudentRepository
    
    
    class StudentRepository:
    
        def __init__(self, db):
    
            self.db = db

* * *

# 9\. Thêm sinh viên
    
    
    def add(self, student):
    
        self.db.cursor.execute(
    
            """
            INSERT INTO students
    
            (name, age, email, classroom)
    
            VALUES (?, ?, ?, ?)
            """,
    
            (
                student.name,
    
                student.age,
    
                student.email,
    
                student.classroom
            )
    
        )
    
        self.db.conn.commit()

Lưu ý:

Dùng:
    
    
    ?

Không nối chuỗi.

* * *

# 10\. SQL Injection

Sai:
    
    
    sql = f"""
    INSERT INTO students
    
    VALUES('{name}')
    """

Nếu người dùng nhập:
    
    
    ' OR 1=1 --

Có thể gây lỗi hoặc tạo lỗ hổng bảo mật.

* * *

Đúng:
    
    
    execute(sql, values)

SQLite sẽ tự xử lý việc truyền tham số.

* * *

# 11\. Lấy toàn bộ dữ liệu
    
    
    cursor.execute(
    
        """
        SELECT *
    
        FROM students
        """
    )

Lấy:
    
    
    rows = cursor.fetchall()

Chuyển thành:
    
    
    Student(...)

* * *

# 12\. Repository trả về Entity

Không nên:
    
    
    return rows

Nên:
    
    
    return [
        Student(...)
    ]

Lợi ích:

  * Dễ đọc. 
  * Có gợi ý kiểu dữ liệu (type hints). 
  * Dễ đổi Database. 



* * *

# 13\. Update
    
    
    UPDATE students
    
    SET
    
    name=?,
    
    age=?,
    
    email=?,
    
    classroom=?
    
    WHERE id=?

Repository:
    
    
    update(student)

* * *

# 14\. Delete
    
    
    DELETE
    
    FROM students
    
    WHERE id=?

* * *

# 15\. Find by ID
    
    
    SELECT *
    
    FROM students
    
    WHERE id=?

Trả về:
    
    
    Student

hoặc
    
    
    None

* * *

# 16\. Search
    
    
    SELECT *
    
    FROM students
    
    WHERE name
    
    LIKE ?

Ví dụ:
    
    
    "%An%"

↓
    
    
    An
    
    Nguyễn An
    
    An Bình

* * *

# 17\. Controller

Ví dụ:
    
    
    def add_student():
    
        repository.add(...)

Sau đó:
    
    
    model.reload()

GUI không biết SQL.

* * *

# 18\. Reload Model

Repository:

↓

Danh sách Student mới.

↓
    
    
    model.students = repository.find_all()

↓
    
    
    beginResetModel()
    
    ...
    
    endResetModel()

`QTableView` tự cập nhật.

* * *

# 19\. Không nên làm

Sai:
    
    
    QTableWidget
    
    ↓
    
    SQLite

Không có lớp trung gian.

* * *

Đúng:
    
    
    SQLite
    
    ↓
    
    Repository
    
    ↓
    
    StudentModel
    
    ↓
    
    QTableView

* * *

# 20\. SQLite và Thread

Nếu sau này tải dữ liệu trong `QThread`:

Mỗi Worker nên có kết nối SQLite riêng.

Không nên chia sẻ cùng một đối tượng `Connection` giữa nhiều luồng.

* * *

# 21\. Những lỗi người mới thường gặp

## Lỗi 1

Quên:
    
    
    commit()

↓

Không lưu.

* * *

## Lỗi 2

Quên:
    
    
    close()

Khi ứng dụng kết thúc.

Nên đóng kết nối trong sự kiện đóng cửa sổ (`closeEvent`) hoặc sử dụng context manager khi phù hợp.

* * *

## Lỗi 3

SQL trong MainWindow.

Sai kiến trúc.

* * *

## Lỗi 4

Repository trả:
    
    
    tuple

Thay vì:
    
    
    Student

Khó mở rộng.

* * *

## Lỗi 5

Không dùng tham số `?`.

Dễ phát sinh lỗi và tiềm ẩn rủi ro bảo mật.

* * *

# 22\. Ví dụ luồng hoạt động
    
    
    Button "Thêm"
    
    ↓
    
    Controller
    
    ↓
    
    Repository
    
    ↓
    
    SQLite
    
    ↓
    
    Repository
    
    ↓
    
    Student
    
    ↓
    
    StudentModel
    
    ↓
    
    QTableView

Đây là kiến trúc mà chúng ta sẽ sử dụng trong các dự án lớn.

* * *

# Bài tập thực hành

## Bài 1

Tạo:
    
    
    students.db

Bảng:
    
    
    students

* * *

## Bài 2

Viết:
    
    
    StudentRepository

Gồm:

  * add 
  * update 
  * delete 
  * find_by_id 
  * find_all 



* * *

## Bài 3

Kết nối:
    
    
    Repository
    
    ↓
    
    StudentTableModel
    
    ↓
    
    QTableView

Hiển thị dữ liệu.

* * *

## Bài 4

Viết:
    
    
    search(name)

Sử dụng:
    
    
    LIKE

* * *

# Mini Project cuối buổi: Student Manager v2

Nâng cấp dự án **Student Manager**.

### Chức năng

  * Thêm sinh viên. 
  * Sửa sinh viên. 
  * Xóa sinh viên. 
  * Tìm kiếm theo tên. 
  * Hiển thị bằng `QTableView`. 
  * Dữ liệu lưu trong SQLite. 



### Cấu trúc thư mục
    
    
    student_manager/
    │
    ├── models/
    │
    ├── repositories/
    │
    ├── controllers/
    │
    ├── database/
    │
    ├── views/
    │
    ├── resources/
    │
    └── main.py

### Luồng dữ liệu
    
    
    MainWindow
    
    ↓
    
    Controller
    
    ↓
    
    Repository
    
    ↓
    
    SQLite
    
    ↓
    
    Student
    
    ↓
    
    StudentTableModel
    
    ↓
    
    QTableView

* * *

# Tổng kết Buổi 18

Trong buổi này, bạn đã học:

  * Tổ chức ứng dụng theo nhiều tầng. 
  * Kết nối SQLite với `sqlite3`. 
  * Xây dựng `Repository Pattern`. 
  * Thực hiện CRUD. 
  * Sử dụng Entity (`Student`) thay vì tuple. 
  * Kết hợp `QAbstractTableModel` với SQLite. 
  * Hiểu cách làm mới dữ liệu bằng `beginResetModel()` và `endResetModel()`. 



Đây là nền tảng để phát triển các ứng dụng quản lý dữ liệu thực tế.

* * *

# Chuẩn bị cho Buổi 19

Ở **Buổi 19** , chúng ta sẽ chuyển sang **Qt SQL Module** , một cách tích hợp cơ sở dữ liệu trực tiếp với Qt.

Bạn sẽ học:

  * `QSqlDatabase`. 
  * `QSqlQuery`. 
  * `QSqlTableModel`. 
  * `QSqlQueryModel`. 
  * Kết nối trực tiếp `QTableView` với cơ sở dữ liệu. 
  * Giao dịch (`Transaction`), `commit()`, `rollback()`. 
  * So sánh ưu và nhược điểm giữa: 
    * `sqlite3`. 
    * `QSqlDatabase`. 
    * `SQLAlchemy`. 
    * `SQLModel`. 



Ngoài ra, chúng ta sẽ thảo luận khi nào nên dùng từng công nghệ trong các dự án PySide6 thực tế để có hiệu năng, khả năng bảo trì và mở rộng tốt nhất.

