Version:0.9 StartHTML:00000097 EndHTML:00069441 StartFragment:00000131 EndFragment:00069405 

# Làm chủ Cơ sở dữ liệu quan hệ (Relational Database)

# Buổi 2: Mô hình dữ liệu (Data Modeling) – Entity, Attribute, Relationship, Business Rule và ERD cơ bản

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu bản chất của mô hình dữ liệu. 
>   * Biết cách phân tích yêu cầu trước khi tạo Database. 
>   * Phân biệt Entity, Attribute, Relationship. 
>   * Hiểu Business Rule là gì. 
>   * Biết xác định khóa chính sơ bộ. 
>   * Vẽ được ERD đầu tiên. 
>   * Chuyển yêu cầu thực tế thành thiết kế CSDL. 
> 


* * *

# Phần 1. Tại sao phải thiết kế trước khi viết SQL?

Đây là lỗi phổ biến của người mới học:
    
    
    Viết SQL
    
    ↓
    
    Tạo bảng
    
    ↓
    
    Thêm cột
    
    ↓
    
    Sửa bảng
    
    ↓
    
    Xóa bảng
    
    ↓
    
    Làm lại

Trong doanh nghiệp, quy trình đúng là:
    
    
    Thu thập yêu cầu
    
    ↓
    
    Phân tích nghiệp vụ
    
    ↓
    
    Thiết kế mô hình dữ liệu
    
    ↓
    
    Vẽ ERD
    
    ↓
    
    Chuẩn hóa dữ liệu
    
    ↓
    
    Thiết kế bảng
    
    ↓
    
    Viết SQL
    
    ↓
    
    Lập trình

> **Nguyên tắc vàng:** SQL chỉ là công cụ. Thiết kế dữ liệu mới là nền tảng.

* * *

# Phần 2. Data Modeling là gì?

**Data Modeling (Mô hình hóa dữ liệu)** là quá trình xác định:

  * Cần lưu dữ liệu gì? 
  * Các dữ liệu liên quan với nhau như thế nào? 
  * Mỗi dữ liệu có những thuộc tính nào? 
  * Có những quy tắc nghiệp vụ nào cần đảm bảo? 



Ví dụ với hệ thống quản lý trường học:
    
    
    Học sinh
    
    ↓
    
    Lớp học
    
    ↓
    
    Môn học
    
    ↓
    
    Giáo viên
    
    ↓
    
    Điểm số

* * *

# Phần 3. Entity là gì?

**Entity (Thực thể)** là một đối tượng mà hệ thống cần lưu trữ thông tin.

Ví dụ:

Hệ thống thư viện:
    
    
    Sách
    
    Độc giả
    
    Phiếu mượn
    
    Nhân viên

Mỗi đối tượng trên đều là Entity.

* * *

Ví dụ thương mại điện tử:
    
    
    Khách hàng
    
    Sản phẩm
    
    Đơn hàng
    
    Thanh toán
    
    Kho hàng

* * *

Ví dụ mạng xã hội:
    
    
    Người dùng
    
    Bài viết
    
    Bình luận
    
    Tin nhắn
    
    Nhóm

* * *

## Cách nhận biết Entity

Hãy đọc yêu cầu nghiệp vụ và tìm các **danh từ**.

Ví dụ:

> "Sinh viên đăng ký nhiều môn học."

Danh từ:

  * Sinh viên ✅ 
  * Môn học ✅ 



Động từ:

  * đăng ký 



"Đăng ký" thường trở thành một Entity trung gian (sẽ học ở buổi sau).

* * *

# Phần 4. Attribute là gì?

Attribute là **thuộc tính** mô tả Entity.

Ví dụ Entity:
    
    
    Sinh viên

Có các thuộc tính:
    
    
    Mã sinh viên
    
    Họ tên
    
    Ngày sinh
    
    Giới tính
    
    Email
    
    Địa chỉ
    
    Số điện thoại

* * *

Ví dụ:

Entity
    
    
    Sản phẩm

Attribute
    
    
    Tên
    
    Giá
    
    Mô tả
    
    Số lượng
    
    Ngày tạo

* * *

Ví dụ:

Entity
    
    
    Khách hàng

Attribute
    
    
    Tên
    
    Email
    
    Ngày sinh
    
    Địa chỉ
    
    Điện thoại

* * *

# Phần 5. Identifier (Định danh)

Mỗi Entity cần có một thuộc tính để phân biệt từng bản ghi.

Ví dụ:
    
    
    Student
    
    id = 1
    
    id = 2
    
    id = 3

Không nên dùng tên để định danh vì có thể trùng.

Sai:
    
    
    Nguyễn Văn A
    
    Nguyễn Văn A

Đúng:
    
    
    id = 15
    
    Tên = Nguyễn Văn A

Trong các buổi sau chúng ta sẽ học chi tiết về:

  * Primary Key 
  * Candidate Key 
  * Composite Key 
  * Surrogate Key 
  * Natural Key 



* * *

# Phần 6. Relationship là gì?

Relationship là **mối quan hệ giữa các Entity**.

Ví dụ:
    
    
    Sinh viên
    
    ↓
    
    Lớp học

Một sinh viên thuộc một lớp.

* * *

Ví dụ:
    
    
    Khách hàng
    
    ↓
    
    Đơn hàng

Một khách hàng có nhiều đơn hàng.

* * *

Ví dụ:
    
    
    Đơn hàng
    
    ↓
    
    Chi tiết đơn hàng
    
    ↓
    
    Sản phẩm

* * *

# Các loại Relationship

## 1\. One-to-One (1-1)

Ví dụ:
    
    
    Công dân
    
    ↓
    
    CCCD

Một công dân chỉ có một CCCD.

* * *

## 2\. One-to-Many (1-N)

Ví dụ:
    
    
    Lớp
    
    ↓
    
    Sinh viên

Một lớp có nhiều sinh viên.

Mỗi sinh viên chỉ thuộc một lớp.

Đây là loại quan hệ phổ biến nhất.

* * *

## 3\. Many-to-Many (N-N)

Ví dụ:
    
    
    Sinh viên
    
    ↓
    
    Môn học

Một sinh viên học nhiều môn.

Một môn có nhiều sinh viên.

Quan hệ này không được tạo trực tiếp trong CSDL quan hệ mà cần một bảng trung gian. Chúng ta sẽ học kỹ ở các buổi sau.

* * *

# Phần 7. Business Rule là gì?

Business Rule (Quy tắc nghiệp vụ) là các quy định mà dữ liệu phải tuân theo.

Ví dụ:
    
    
    Một sinh viên chỉ thuộc một lớp.

* * *
    
    
    Một lớp tối đa 40 sinh viên.

* * *
    
    
    Điểm phải từ 0 đến 10.

* * *
    
    
    Email không được trùng.

* * *
    
    
    Tuổi phải lớn hơn hoặc bằng 18.

* * *

Các Business Rule sẽ được hiện thực bằng:

  * PRIMARY KEY 
  * FOREIGN KEY 
  * UNIQUE 
  * CHECK 
  * NOT NULL 
  * TRIGGER 
  * PROCEDURE 



* * *

# Phần 8. Phân tích yêu cầu thực tế

## Đề bài

Xây dựng hệ thống quản lý trường học.

Yêu cầu:

  * Trường có nhiều lớp. 
  * Mỗi lớp có nhiều sinh viên. 
  * Mỗi giáo viên dạy nhiều lớp. 
  * Sinh viên học nhiều môn. 
  * Mỗi môn có nhiều sinh viên. 



* * *

## Bước 1: Tìm Entity

Ta gạch chân các danh từ:
    
    
    Trường
    
    Lớp
    
    Sinh viên
    
    Giáo viên
    
    Môn học

Có thể xác định các Entity:
    
    
    School
    
    Class
    
    Student
    
    Teacher
    
    Subject

* * *

## Bước 2: Tìm Attribute

### Student
    
    
    id
    
    name
    
    birthday
    
    gender
    
    email
    
    phone

* * *

### Teacher
    
    
    id
    
    name
    
    degree
    
    email

* * *

### Subject
    
    
    id
    
    name
    
    credit

* * *

### Class
    
    
    id
    
    name
    
    room

* * *

# Phần 9. Vẽ ERD đầu tiên
    
    
    +----------------+
    |     CLASS      |
    +----------------+
    | id             |
    | name           |
    | room           |
    +----------------+
            |
            | 1
            |
            | N
    +----------------+
    |    STUDENT     |
    +----------------+
    | id             |
    | name           |
    | birthday       |
    | gender         |
    | email          |
    | phone          |
    +----------------+

Giải thích:

Một lớp có nhiều sinh viên.

Một sinh viên thuộc một lớp.

* * *

# Phần 10. Ví dụ thứ hai: Hệ thống bán hàng

Entity:
    
    
    Customer
    
    Product
    
    Order
    
    OrderDetail

ERD đơn giản:
    
    
    Customer
    
    |
    
    | 1
    
    |
    
    N
    
    Order
    
    |
    
    | 1
    
    |
    
    N
    
    OrderDetail
    
    |
    
    | N
    
    |
    
    1
    
    Product

Giải thích:

  * Một khách hàng có nhiều đơn hàng. 
  * Một đơn hàng có nhiều dòng chi tiết. 
  * Mỗi dòng chi tiết tham chiếu đến một sản phẩm. 



* * *

# Phần 11. Chuyển từ mô hình sang bảng

Ví dụ:

Entity:
    
    
    Student

Sau này sẽ thành bảng:
    
    
    CREATE TABLE students (
        id INTEGER PRIMARY KEY,
        name TEXT,
        birthday DATE,
        email TEXT
    );

Entity:
    
    
    Class

Thành:
    
    
    CREATE TABLE classes (
        id INTEGER PRIMARY KEY,
        name TEXT
    );

Mối quan hệ sẽ được biểu diễn bằng khóa ngoại (Foreign Key) ở các buổi tiếp theo.

* * *

# Phần 12. Thực hành phân tích yêu cầu

## Bài toán: Quản lý thư viện

Yêu cầu:

  * Thư viện có nhiều sách. 
  * Mỗi sách thuộc một thể loại. 
  * Một độc giả có thể mượn nhiều sách. 
  * Một sách có thể được nhiều độc giả mượn ở các thời điểm khác nhau. 
  * Nhân viên lập phiếu mượn. 



### Xác định Entity

  * Library 
  * Book 
  * Category 
  * Reader 
  * Staff 
  * BorrowSlip (Phiếu mượn) 
  * BorrowDetail (Chi tiết phiếu mượn) 



### Một số Attribute

**Book**

  * id 
  * title 
  * author 
  * publisher 
  * publish_year 
  * isbn 
  * price 



**Reader**

  * id 
  * full_name 
  * birthday 
  * phone 
  * email 



**BorrowSlip**

  * id 
  * borrow_date 
  * return_date 
  * status 



* * *

# Tổng kết buổi 2

Bạn đã học được:

  * Tư duy thiết kế trước khi viết SQL. 
  * Data Modeling là gì. 
  * Entity và cách xác định từ yêu cầu. 
  * Attribute và cách lựa chọn thuộc tính. 
  * Relationship và ba kiểu quan hệ cơ bản (1-1, 1-N, N-N). 
  * Business Rule và vai trò của nó trong việc đảm bảo tính đúng đắn của dữ liệu. 
  * Cách phân tích yêu cầu nghiệp vụ để xây dựng mô hình dữ liệu. 
  * Cách chuyển từ mô hình dữ liệu sang thiết kế bảng. 



* * *

# Bài tập thực hành

## Bài 1

Phân tích hệ thống **quản lý bệnh viện**.

Xác định:

  * Entity 
  * Attribute 
  * Relationship 



* * *

## Bài 2

Phân tích hệ thống **quản lý cửa hàng điện thoại**.

Xác định:

  * Entity 
  * Attribute 
  * Relationship 



* * *

## Bài 3

Phân tích hệ thống **ứng dụng gọi xe**.

Xác định:

  * Entity 
  * Attribute 
  * Relationship 



* * *

## Bài 4 (Nâng cao)

Thiết kế mô hình dữ liệu sơ bộ cho một **ứng dụng học ngoại ngữ** (tương tự HelloChinese hoặc Duolingo).

Hãy xác định:

  * Các Entity chính. 
  * Thuộc tính của từng Entity. 
  * Các mối quan hệ giữa chúng. 
  * Ít nhất **10 Business Rule** (ví dụ: một bài học thuộc đúng một khóa học, một người dùng có thể học nhiều khóa học, mỗi câu hỏi phải thuộc một bài học, ...). 



> **Chuẩn bị cho buổi 3:** Chúng ta sẽ đi sâu vào **Primary Key, Candidate Key, Composite Key, Surrogate Key và Natural Key** , đồng thời học cách lựa chọn khóa phù hợp để xây dựng cơ sở dữ liệu ổn định, hiệu quả và dễ mở rộng. Đây là một trong những chủ đề quan trọng nhất trong thiết kế cơ sở dữ liệu chuyên nghiệp.

