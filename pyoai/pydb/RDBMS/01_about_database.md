Version:0.9 StartHTML:00000097 EndHTML:00068813 StartFragment:00000131 EndFragment:00068777 

# Làm chủ Cơ sở dữ liệu quan hệ (Relational Database)

# Buổi 1: Database là gì? Vì sao cần Database? DBMS - RDBMS - SQL - ACID

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ hiểu:
> 
>   * Database là gì. 
>   * Tại sao phải dùng Database thay vì lưu file. 
>   * DBMS là gì. 
>   * RDBMS là gì. 
>   * SQL là gì. 
>   * ACID là gì. 
>   * Kiến trúc tổng quan của một hệ quản trị CSDL. 
>   * Quy trình một câu lệnh SQL được thực thi. 
>   * Tạo và thao tác với cơ sở dữ liệu đầu tiên bằng SQLite và Python. 
> 


* * *

# Phần 1. Thế giới trước khi có Database

Khoảng những năm 1960, hầu hết dữ liệu được lưu dưới dạng:

  * File Text (.txt) 
  * CSV 
  * Excel 
  * Binary file 



Ví dụ:
    
    
    students.txt
    
    Nguyen Van A
    18
    CNTT
    
    Tran Thi B
    19
    Kinh Te

Hoặc
    
    
    students.csv
    
    id,name,age,class
    1,An,18,CNTT
    2,Binh,19,CNTT

Lúc đầu điều này rất tiện.

Nhưng khi dữ liệu tăng lên...

100 sinh viên

↓

10.000 sinh viên

↓

10 triệu sinh viên

↓

100 triệu khách hàng

↓

1 tỷ giao dịch

...

mọi thứ bắt đầu trở nên tồi tệ.

* * *

# Ví dụ thực tế

Giả sử bạn viết ứng dụng quản lý học sinh bằng Python.

Bạn lưu như sau:
    
    
    students.csv

Có:
    
    
    100.000 dòng

Muốn tìm:
    
    
    Tên = "Nguyễn Văn A"

Python phải làm gì?
    
    
    Mở file
    
    ↓
    
    Đọc từng dòng
    
    ↓
    
    So sánh
    
    ↓
    
    Đọc tiếp
    
    ↓
    
    So sánh
    
    ↓
    
    ...
    
    ↓
    
    Hết file

Đây gọi là:
    
    
    Linear Scan

Độ phức tạp:
    
    
    O(n)

Nếu:
    
    
    100 triệu dòng

thì sẽ cực kỳ chậm.

* * *

# Một vấn đề khác

Giả sử có hai người cùng sửa file.
    
    
    User A
    
    ↓
    
    students.csv
    
    ↑
    
    User B

Điều gì xảy ra?

Có thể:

  * ghi đè 
  * mất dữ liệu 
  * file hỏng 



* * *

# Thêm một vấn đề

Bạn muốn tìm:
    
    
    Sinh viên
    
    Tuổi >18
    
    Khoa CNTT
    
    Điểm >8
    
    Tên bắt đầu bằng "N"

Với file CSV bạn phải:
    
    
    for từng dòng:
    
    if ...
    
    if ...
    
    if ...
    
    if ...

Rất chậm.

* * *

# Thêm nữa...

Nếu điện bị mất giữa lúc ghi file.

File có thể:
    
    
    abc....
    
    abc....
    
    abc....
    
    ab

Dữ liệu hỏng.

* * *

# Tổng kết

Lưu file phù hợp khi:

  * cấu hình (config) 
  * log nhỏ 
  * dữ liệu ít 



Không phù hợp khi:

  * nhiều người truy cập 
  * dữ liệu lớn 
  * tìm kiếm nhanh 
  * giao dịch 
  * bảo mật 



* * *

# Phần 2. Database ra đời

Database sinh ra để giải quyết:

✔ Lưu dữ liệu

✔ Tìm kiếm nhanh

✔ Truy cập đồng thời

✔ Không mất dữ liệu

✔ Quan hệ giữa dữ liệu

Ví dụ
    
    
    Khách hàng
    
    ↓
    
    Đơn hàng
    
    ↓
    
    Chi tiết đơn hàng
    
    ↓
    
    Thanh toán

Tất cả liên kết với nhau.

* * *

# Database là gì?

**Database (Cơ sở dữ liệu)** là tập hợp dữ liệu được tổ chức có cấu trúc để dễ dàng:

  * lưu trữ 
  * tìm kiếm 
  * cập nhật 
  * xóa 
  * quản lý 
  * bảo vệ 
  * mở rộng 



Ví dụ:
    
    
    Database
    
    School

Bên trong
    
    
    Students
    
    Teachers
    
    Courses
    
    Scores
    
    Classes

* * *

# Phần 3. Ví dụ thực tế

Facebook

Có:
    
    
    Users
    
    Posts
    
    Comments
    
    Likes
    
    Friends
    
    Messages

Đó chính là Database.

* * *

Shopee

Có:
    
    
    Products
    
    Orders
    
    Users
    
    Payments
    
    Warehouse

* * *

Ngân hàng

Có:
    
    
    Customers
    
    Accounts
    
    Transactions
    
    Loans

* * *

# Phần 4. Database không phải là Excel

Nhiều người mới học thường nghĩ:
    
    
    Database = Excel

Sai.

Excel là bảng tính.

Database là hệ thống quản lý dữ liệu.

Ví dụ:

Excel:
    
    
    100.000 dòng

đã rất nặng.

Database:
    
    
    10 tỷ dòng

vẫn có thể hoạt động hiệu quả nếu được thiết kế và tối ưu đúng.

* * *

# Phần 5. DBMS là gì?

DBMS

(Database Management System)

Là phần mềm quản lý Database.

Ví dụ:
    
    
    Python
    
    ↓
    
    sqlite3
    
    ↓
    
    SQLite Engine
    
    ↓
    
    Database

Hoặc
    
    
    Python
    
    ↓
    
    psycopg
    
    ↓
    
    PostgreSQL
    
    ↓
    
    Database

DBMS chịu trách nhiệm:

  * đọc dữ liệu 
  * ghi dữ liệu 
  * tạo bảng 
  * khóa dữ liệu 
  * phân quyền 
  * sao lưu 
  * phục hồi 
  * tối ưu truy vấn 



* * *

# Một số DBMS phổ biến

DBMS| Miễn phí| Mã nguồn mở| Phù hợp  
---|---|---|---  
SQLite| ✔| ✔| Ứng dụng nhỏ, di động  
PostgreSQL| ✔| ✔| Hệ thống doanh nghiệp  
MySQL| ✔| ✔| Web, CMS  
MariaDB| ✔| ✔| Thay thế MySQL  
Oracle Database| ✖| Một phần| Doanh nghiệp lớn  
Microsoft SQL Server| Có bản miễn phí| ✖| Hệ sinh thái Microsoft  
  
* * *

# Phần 6. RDBMS là gì?

RDBMS

(Relational Database Management System)

Là DBMS sử dụng **mô hình dữ liệu quan hệ**.

Ví dụ:
    
    
    Students
    
    id
    name
    class_id
    
    
    Classes
    
    id
    name

Quan hệ:
    
    
    Students.class_id
    
    ↓
    
    Classes.id

Đó gọi là:
    
    
    Relationship

Hay:
    
    
    Foreign Key

Chúng ta sẽ học rất kỹ ở các buổi sau.

* * *

# Phần 7. SQL là gì?

SQL

Structured Query Language

Là ngôn ngữ dùng để làm việc với cơ sở dữ liệu quan hệ.

SQL không phải ngôn ngữ lập trình tổng quát.

Nó chuyên dùng để:

  * tạo cơ sở dữ liệu 
  * tạo bảng 
  * truy vấn dữ liệu 
  * cập nhật dữ liệu 
  * xóa dữ liệu 
  * phân quyền 
  * quản lý giao dịch 



Ví dụ:
    
    
    SELECT *
    FROM students;

Hoặc:
    
    
    INSERT INTO students(name, age)
    VALUES ('An', 20);

* * *

# Phần 8. Một câu SQL được xử lý như thế nào?

Khi bạn viết:
    
    
    SELECT *
    FROM students
    WHERE age > 18;

Bên trong DBMS sẽ diễn ra:
    
    
    SQL
    
    ↓
    
    Parser
    (kiểm tra cú pháp)
    
    ↓
    
    Optimizer
    (chọn kế hoạch tối ưu)
    
    ↓
    
    Executor
    (thực thi)
    
    ↓
    
    Storage Engine
    (đọc dữ liệu)
    
    ↓
    
    Kết quả

Đây là nền tảng để học tối ưu truy vấn sau này.

* * *

# Phần 9. ACID là gì?

ACID là bốn tính chất quan trọng của giao dịch (Transaction) trong cơ sở dữ liệu.

## A – Atomicity (Tính nguyên tử)

Một giao dịch hoặc thực hiện toàn bộ, hoặc không thực hiện gì cả.

Ví dụ:

Chuyển 100.000₫ từ tài khoản A sang B:
    
    
    A -100.000
    
    ↓
    
    B +100.000

Nếu hệ thống lỗi sau khi trừ tiền của A nhưng chưa cộng cho B thì sao?

Không được phép!

Database sẽ hoàn tác (Rollback) để A vẫn giữ nguyên số dư ban đầu.

* * *

## C – Consistency (Tính nhất quán)

Dữ liệu trước và sau giao dịch luôn phải hợp lệ.

Ví dụ:

Không thể tạo đơn hàng tham chiếu đến một khách hàng không tồn tại.

* * *

## I – Isolation (Tính cô lập)

Hai giao dịch đồng thời không được làm hỏng dữ liệu của nhau.

Ví dụ:

Hai nhân viên cùng cập nhật số lượng hàng tồn kho, hệ thống phải đảm bảo kết quả cuối cùng nhất quán.

* * *

## D – Durability (Tính bền vững)

Sau khi giao dịch được xác nhận (Commit), dữ liệu phải được lưu bền vững, kể cả khi mất điện hoặc hệ thống khởi động lại.

* * *

# Phần 10. Thực hành với Python và SQLite

SQLite đi kèm với Python, không cần cài đặt thêm.
    
    
    import sqlite3
    
    # Kết nối (nếu chưa có file sẽ tự tạo)
    conn = sqlite3.connect("school.db")
    
    # Tạo đối tượng để thực thi SQL
    cursor = conn.cursor()
    
    # Tạo bảng
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER
    )
    """)
    
    # Thêm dữ liệu
    cursor.execute(
        "INSERT INTO students(name, age) VALUES (?, ?)",
        ("Nguyễn Văn A", 20)
    )
    
    # Lưu thay đổi
    conn.commit()
    
    # Đọc dữ liệu
    cursor.execute("SELECT * FROM students")
    
    for row in cursor.fetchall():
        print(row)
    
    # Đóng kết nối
    conn.close()

**Kết quả:**
    
    
    (1, 'Nguyễn Văn A', 20)

* * *

# Tổng kết buổi 1

Sau buổi học này bạn đã nắm được:

  * Vì sao lưu dữ liệu bằng file có nhiều hạn chế. 
  * Database là gì và vai trò của nó trong các hệ thống hiện đại. 
  * Phân biệt DBMS và RDBMS. 
  * SQL là ngôn ngữ làm việc với cơ sở dữ liệu quan hệ. 
  * Quy trình xử lý một câu lệnh SQL từ Parser → Optimizer → Executor → Storage Engine. 
  * Bốn tính chất ACID và ý nghĩa của chúng trong giao dịch. 
  * Cách tạo và thao tác với cơ sở dữ liệu SQLite đầu tiên bằng Python. 



* * *

# Bài tập thực hành

  1. Giải thích bằng lời của bạn sự khác nhau giữa lưu dữ liệu bằng **CSV** và **Database**. 
  2. Cài đặt (hoặc kiểm tra) môi trường Python và chạy thành công ví dụ SQLite ở trên. 
  3. Tạo cơ sở dữ liệu `library.db`. 
  4. Tạo bảng `books` với các cột: 
     * `id`
     * `title`
     * `author`
     * `price`
  5. Thêm ít nhất **5 cuốn sách** vào bảng. 
  6. Viết chương trình Python đọc toàn bộ dữ liệu và in ra màn hình. 
  7. Thử xóa file `library.db`, chạy lại chương trình và quan sát điều gì xảy ra. 



* * *

## Kiến thức sẽ học ở Buổi 2

Buổi tiếp theo chúng ta sẽ đi vào **Mô hình dữ liệu (Data Model)** , gồm:

  * Entity là gì? 
  * Attribute là gì? 
  * Relationship là gì? 
  * Business Rule là gì? 
  * Phân tích yêu cầu thực tế để xây dựng mô hình dữ liệu. 
  * Vẽ sơ đồ ERD đầu tiên cho một hệ thống quản lý trường học. 



Đây là bước quan trọng nhất trước khi viết bất kỳ câu lệnh SQL nào, vì một thiết kế tốt sẽ quyết định hiệu năng và khả năng mở rộng của toàn bộ hệ thống.

