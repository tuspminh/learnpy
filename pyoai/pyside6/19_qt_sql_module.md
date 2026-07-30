# Khóa học PySide6 từ A-Z

# Buổi 19: Qt SQL Module - Làm chủ QSqlDatabase, QSqlQuery, QSqlTableModel và QSqlQueryModel

> **Đây là buổi học giúp bạn hiểu cách Qt làm việc trực tiếp với cơ sở dữ liệu.**

Ở buổi 18, chúng ta dùng:
    
    
    PySide6
        ↓
    Repository
        ↓
    sqlite3
        ↓
    SQLite

Hôm nay chúng ta sẽ học cách Qt tự kết nối với cơ sở dữ liệu:
    
    
    PySide6
        ↓
    QSqlDatabase
        ↓
    SQLite

Sau buổi học này bạn sẽ:

  * Hiểu Qt SQL Module là gì. 
  * Kết nối SQLite bằng `QSqlDatabase`. 
  * Thực hiện CRUD bằng `QSqlQuery`. 
  * Hiểu `QSqlTableModel`. 
  * Hiểu `QSqlQueryModel`. 
  * Biết khi nào nên dùng Qt SQL và khi nào nên dùng `sqlite3`. 
  * Hiểu Transaction (`commit()` / `rollback()`). 
  * Chuẩn bị cho các dự án dùng PostgreSQL, MySQL. 



* * *

# 1\. Qt SQL Module là gì?

Qt có sẵn một module để làm việc với cơ sở dữ liệu:
    
    
    from PySide6.QtSql import *

Module này hỗ trợ rất nhiều hệ quản trị CSDL:

  * SQLite 
  * MySQL 
  * PostgreSQL 
  * Oracle 
  * ODBC 
  * SQL Server (qua ODBC hoặc driver phù hợp) 



Điểm mạnh nhất là **tích hợp trực tiếp với Model/View của Qt**.

* * *

# 2\. Các lớp quan trọng

Lớp| Chức năng  
---|---  
`QSqlDatabase`| Kết nối cơ sở dữ liệu  
`QSqlQuery`| Thực thi câu lệnh SQL  
`QSqlTableModel`| Model cho một bảng  
`QSqlQueryModel`| Model cho kết quả SELECT  
`QSqlRelationalTableModel`| Model có quan hệ khóa ngoại  
`QSqlRecord`| Đại diện cho một bản ghi  
`QSqlError`| Thông tin lỗi SQL  
  
* * *

# 3\. Kiến trúc Qt SQL
    
    
    QTableView
          │
          ▼
    QSqlTableModel
          │
          ▼
    QSqlDatabase
          │
          ▼
    SQLite

Qt sẽ tự đồng bộ dữ liệu giữa bảng và giao diện.

* * *

# 4\. Kết nối SQLite
    
    
    from PySide6.QtSql import QSqlDatabase
    
    db = QSqlDatabase.addDatabase("QSQLITE")
    
    db.setDatabaseName("students.db")

Mở kết nối:
    
    
    if not db.open():
        print("Không mở được database")

* * *

# 5\. Đóng kết nối
    
    
    db.close()

Nên đóng khi ứng dụng kết thúc.

* * *

# 6\. QSqlQuery

Thực thi SQL:
    
    
    from PySide6.QtSql import QSqlQuery
    
    query = QSqlQuery()

Ví dụ tạo bảng:
    
    
    query.exec("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER
    )
    """)

* * *

# 7\. INSERT
    
    
    query.prepare("""
    INSERT INTO students
    (name, age)
    VALUES (?, ?)
    """)

Truyền giá trị:
    
    
    query.addBindValue("An")
    query.addBindValue(20)

Thực thi:
    
    
    query.exec()

> `prepare()` kết hợp với `addBindValue()` giúp mã rõ ràng và tránh SQL Injection.

* * *

# 8\. SELECT
    
    
    query.exec("""
    SELECT *
    FROM students
    """)

Đọc kết quả:
    
    
    while query.next():
    
        print(
            query.value("name"),
            query.value("age")
        )

Có thể dùng tên cột hoặc chỉ số:
    
    
    query.value(0)

* * *

# 9\. UPDATE
    
    
    query.prepare("""
    UPDATE students
    
    SET age=?
    
    WHERE id=?
    """)
    
    query.addBindValue(22)
    query.addBindValue(1)
    
    query.exec()

* * *

# 10\. DELETE
    
    
    query.prepare("""
    DELETE
    
    FROM students
    
    WHERE id=?
    """)
    
    query.addBindValue(1)
    
    query.exec()

* * *

# 11\. Kiểm tra lỗi
    
    
    if not query.exec():
    
        print(query.lastError().text())

Đây là cách rất quan trọng để chẩn đoán lỗi SQL.

* * *

# 12\. QSqlTableModel

Đây là điểm mạnh nhất của Qt SQL.
    
    
    model = QSqlTableModel()

Kết nối bảng:
    
    
    model.setTable("students")

Lấy dữ liệu:
    
    
    model.select()

Hiển thị:
    
    
    table.setModel(model)

Không cần viết:
    
    
    QAbstractTableModel

Qt tự làm.

* * *

# 13\. Đổi tên cột
    
    
    model.setHeaderData(
        1,
        Qt.Horizontal,
        "Họ tên"
    )

Ví dụ:
    
    
    name

↓
    
    
    Họ tên

* * *

# 14\. Thêm dữ liệu bằng QSqlTableModel

Tạo dòng mới:
    
    
    row = model.rowCount()
    
    model.insertRow(row)

Gán dữ liệu:
    
    
    model.setData(
        model.index(row, 1),
        "An"
    )
    
    model.setData(
        model.index(row, 2),
        20
    )

Lưu:
    
    
    model.submitAll()

* * *

# 15\. Xóa dòng
    
    
    model.removeRow(row)

Lưu:
    
    
    model.submitAll()

* * *

# 16\. QSqlQueryModel

Khác với `QSqlTableModel`.

Nó chỉ dùng để hiển thị kết quả truy vấn.

Ví dụ:
    
    
    model = QSqlQueryModel()

Thực hiện:
    
    
    model.setQuery("""
    SELECT
    
    name,
    
    age
    
    FROM students
    """)

Hiển thị:
    
    
    table.setModel(model)

* * *

# 17\. Khác nhau giữa QSqlTableModel và QSqlQueryModel

QSqlTableModel| QSqlQueryModel  
---|---  
CRUD| Chủ yếu đọc dữ liệu  
Có sửa| Không sửa trực tiếp  
Một bảng| Truy vấn bất kỳ  
Có `submitAll()`| Không có  
  
* * *

# 18\. Filter

Ví dụ:
    
    
    model.setFilter(
        "age > 18"
    )

Sau đó:
    
    
    model.select()

Kết quả:
    
    
    Chỉ hiển thị
    tuổi >18

* * *

# 19\. Sort
    
    
    model.setSort(
        1,
        Qt.AscendingOrder
    )
    
    model.select()

* * *

# 20\. Edit Strategy

Qt có ba chiến lược lưu dữ liệu:

## OnFieldChange

Lưu ngay sau khi sửa từng ô.
    
    
    model.setEditStrategy(
        QSqlTableModel.OnFieldChange
    )

* * *

## OnRowChange

Lưu khi chuyển sang dòng khác.
    
    
    QSqlTableModel.OnRowChange

* * *

## OnManualSubmit

Chỉ lưu khi gọi:
    
    
    model.submitAll()

Đây là chế độ thường dùng nhất trong các ứng dụng chuyên nghiệp vì dễ kiểm soát và có thể kết hợp với giao dịch.

* * *

# 21\. Transaction

Ví dụ:
    
    
    Thêm sinh viên
    
    ↓
    
    Thêm học phí
    
    ↓
    
    Thêm tài khoản

Nếu bước 2 lỗi:

↓

Quay lại tất cả.

Qt hỗ trợ:
    
    
    db.transaction()

Thành công:
    
    
    db.commit()

Có lỗi:
    
    
    db.rollback()

Đây là nguyên tắc **ACID** của cơ sở dữ liệu.

* * *

# 22\. Khi nào dùng gì?

Công nghệ| Khi nào dùng  
---|---  
`sqlite3`| Muốn toàn quyền điều khiển SQL và kiến trúc Repository  
`QSqlDatabase` \+ `QSqlTableModel`| Ứng dụng CRUD đơn giản, tích hợp chặt với Qt  
`SQLAlchemy`| Ứng dụng lớn, nhiều loại CSDL, cần ORM mạnh  
`SQLModel`| Dự án hiện đại dùng type hint và tích hợp tốt với FastAPI  
  
* * *

# 23\. So sánh sqlite3 và Qt SQL

sqlite3| Qt SQL  
---|---  
Chuẩn Python| Chuẩn Qt  
Linh hoạt| Tích hợp GUI rất tốt  
Phù hợp Repository| Phù hợp Model/View  
Dễ kết hợp ORM| Dễ dùng với `QTableView`  
  
* * *

# 24\. Những lỗi người mới thường gặp

## Lỗi 1

Quên:
    
    
    model.select()

Sau khi:
    
    
    setTable()

↓

Không có dữ liệu.

* * *

## Lỗi 2

Sửa dữ liệu nhưng quên:
    
    
    submitAll()

Trong chế độ `OnManualSubmit`.

↓

Không lưu.

* * *

## Lỗi 3

Không kiểm tra:
    
    
    lastError()

↓

Khó tìm nguyên nhân lỗi.

* * *

## Lỗi 4

Dùng `QSqlQueryModel` rồi cố sửa dữ liệu.

↓

Không được.

Muốn sửa:

↓

`QSqlTableModel`.

* * *

## Lỗi 5

Mở nhiều kết nối không cần thiết.

Nên quản lý kết nối tập trung trong một lớp hoặc một module.

* * *

# Bài tập thực hành

## Bài 1

Tạo:
    
    
    students.db

Kết nối bằng:
    
    
    QSqlDatabase

* * *

## Bài 2

Dùng:
    
    
    QSqlQuery

Thực hiện:

  * INSERT 
  * UPDATE 
  * DELETE 
  * SELECT 



* * *

## Bài 3

Hiển thị bảng:
    
    
    QSqlTableModel

↓
    
    
    QTableView

* * *

## Bài 4

Thêm:

  * Filter theo tuổi. 
  * Sort theo tên. 



* * *

# Mini Project cuối buổi: Student Manager Qt SQL Edition

Tạo phiên bản mới của **Student Manager** sử dụng hoàn toàn Qt SQL.

### Chức năng

  * Hiển thị dữ liệu bằng `QSqlTableModel`. 
  * Thêm sinh viên. 
  * Sửa trực tiếp trên bảng. 
  * Xóa sinh viên. 
  * Lọc theo lớp. 
  * Tìm kiếm theo tên. 
  * Sắp xếp theo cột. 
  * Chỉ lưu thay đổi khi người dùng nhấn nút **Lưu** (`OnManualSubmit`). 



Hãy so sánh phiên bản này với phiên bản ở Buổi 18 (Repository + `sqlite3`) để thấy sự khác biệt về kiến trúc và mức độ kiểm soát.

* * *

# Tổng kết Buổi 19

Bạn đã học:

  * `QSqlDatabase` để quản lý kết nối cơ sở dữ liệu. 
  * `QSqlQuery` để thực thi SQL có tham số. 
  * `QSqlTableModel` để kết nối trực tiếp dữ liệu với `QTableView`. 
  * `QSqlQueryModel` để hiển thị kết quả truy vấn. 
  * `setFilter()`, `setSort()`, `submitAll()`. 
  * Transaction với `transaction()`, `commit()`, `rollback()`. 
  * Khi nào nên chọn `sqlite3`, Qt SQL, `SQLAlchemy` hoặc `SQLModel`. 



* * *

# Chuẩn bị cho Buổi 20

Ở **Buổi 20** , chúng ta sẽ học một chủ đề rất quan trọng trong phát triển ứng dụng chuyên nghiệp:

# Resource System (QRC), Theme và QSS

Bạn sẽ học:

  * `Qt Resource System (.qrc)`. 
  * Đóng gói icon, ảnh, font vào file thực thi. 
  * Viết giao diện bằng **Qt Style Sheet (QSS)**. 
  * Thiết kế Light Theme và Dark Theme. 
  * Tạo giao diện hiện đại theo phong cách Visual Studio Code, Telegram hoặc Discord. 
  * Tổ chức tài nguyên để khi đóng gói bằng `PyInstaller`, ứng dụng vẫn hoạt động ổn định mà không phụ thuộc vào các đường dẫn bên ngoài. 



Buổi này sẽ giúp ứng dụng PySide6 của bạn có giao diện chuyên nghiệp, dễ bảo trì và sẵn sàng phân phối cho người dùng.

