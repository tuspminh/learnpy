Version:0.9 StartHTML:00000097 EndHTML:00074509 StartFragment:00000131 EndFragment:00074473 

# Làm chủ Cơ sở dữ liệu quan hệ (Relational Database)

# Buổi 5: Entity Relationship Diagram (ERD) chuyên sâu – Cardinality, Participation, Crow's Foot và Thiết kế CSDL chuyên nghiệp

> **Mục tiêu buổi học**
> 
> Sau buổi này, bạn sẽ:
> 
>   * Hiểu ERD là gì và tại sao nó quan trọng. 
>   * Đọc được ERD của bất kỳ hệ thống nào. 
>   * Vẽ được ERD theo chuẩn Crow's Foot. 
>   * Hiểu Cardinality và Participation. 
>   * Biết chuyển từ yêu cầu nghiệp vụ sang ERD. 
>   * Thiết kế được ERD cho các hệ thống thực tế. 
> 


* * *

# Phần 1. ERD là gì?

ERD (Entity Relationship Diagram) là **sơ đồ mô tả cấu trúc dữ liệu** của hệ thống.

Nếu SQL giống như bản thiết kế chi tiết của một ngôi nhà thì:

> **ERD chính là bản vẽ kiến trúc.**

Trong doanh nghiệp, quy trình luôn là:
    
    
    Yêu cầu khách hàng
    
    ↓
    
    Phân tích nghiệp vụ
    
    ↓
    
    ERD
    
    ↓
    
    Thiết kế Database
    
    ↓
    
    Viết SQL
    
    ↓
    
    Lập trình

Một DBA hoặc Database Architect có thể dành nhiều ngày chỉ để hoàn thiện ERD trước khi viết bất kỳ dòng SQL nào.

* * *

# Phần 2. ERD gồm những thành phần nào?

Một ERD gồm ba thành phần chính:
    
    
    Entity
    
    ↓
    
    Relationship
    
    ↓
    
    Attribute

Ví dụ:
    
    
    Student
    
    ↓
    
    Enroll
    
    ↓
    
    Subject

Trong đó:

  * `Student` là Entity. 
  * `Subject` là Entity. 
  * `Enroll` thể hiện mối quan hệ (sau này thường trở thành bảng trung gian). 



* * *

# Phần 3. Entity trong ERD

Entity được biểu diễn bằng hình chữ nhật.

Ví dụ:
    
    
    +-------------------+
    |     STUDENT       |
    +-------------------+
    | id                |
    | full_name         |
    | birthday          |
    | gender            |
    +-------------------+

* * *

Một Entity nên biểu diễn **một loại đối tượng**.

Ví dụ:
    
    
    Customer

Không nên là:
    
    
    CustomerAndOrder

Đó là dấu hiệu thiết kế sai.

* * *

# Phần 4. Attribute trong ERD

Thuộc tính nằm bên trong Entity.

Ví dụ:
    
    
    +----------------------+
    | PRODUCT              |
    +----------------------+
    | id                   |
    | product_name         |
    | price                |
    | stock_quantity       |
    | created_at           |
    +----------------------+

Thông thường:
    
    
    PK
    
    đặt ở trên cùng

Ví dụ:
    
    
    id (PK)
    
    ↓
    
    name
    
    ↓
    
    price
    
    ↓
    
    created_at

* * *

# Phần 5. Relationship

Relationship là đường nối giữa hai Entity.

Ví dụ:
    
    
    Customer
    
    ↓
    
    Order

Nó trả lời câu hỏi:
    
    
    Hai bảng liên quan với nhau như thế nào?

* * *

# Phần 6. Cardinality (Lực lượng quan hệ)

Cardinality trả lời câu hỏi:

> **Một bản ghi của bảng A có thể liên kết với bao nhiêu bản ghi của bảng B?**

Có ba loại cơ bản.

* * *

## One-to-One (1:1)

Ví dụ:
    
    
    Citizen
    
    ↓
    
    IdentityCard
    
    
    1 Công dân
    
    ↓
    
    1 CCCD

ERD:
    
    
    Citizen -------- IdentityCard
        1                 1

Ứng dụng:

  * Hộ chiếu. 
  * CCCD. 
  * Hồ sơ sức khỏe điện tử. 



* * *

## One-to-Many (1:N)

Đây là quan hệ phổ biến nhất.

Ví dụ:
    
    
    Department
    
    ↓
    
    Employees
    
    
    Một phòng ban
    
    ↓
    
    Nhiều nhân viên

ERD:
    
    
    Department
    
    1
    
    |
    
    |
    
    <
    
    Employees

* * *

Ví dụ khác:
    
    
    Customer
    
    ↓
    
    Orders

Một khách hàng

↓

Có nhiều đơn hàng.

* * *

## Many-to-Many (N:N)

Ví dụ:
    
    
    Student
    
    ↓
    
    Subject

Một sinh viên

↓

Nhiều môn.

Một môn

↓

Nhiều sinh viên.

ERD:
    
    
    Student
    
    >
    
    <
    
    Subject

Quan hệ N:N **không được triển khai trực tiếp trong cơ sở dữ liệu quan hệ**. Ta phải tạo bảng trung gian (junction table).

Ví dụ:
    
    
    Student
    
    ↓
    
    Enrollment
    
    ↓
    
    Subject

Trong đó:

  * `Enrollment` lưu: 
    * `student_id`
    * `subject_id`
    * `enroll_date`
    * `score`



* * *

# Phần 7. Crow's Foot Notation

Crow's Foot là chuẩn ký hiệu ERD được sử dụng rộng rãi.

Ký hiệu:
    
    
    |
    
    =
    
    1
    
    <
    
    =
    
    Many

Ví dụ:
    
    
    Customer
    
    |
    
    ------------<
    
    Order

Nghĩa là:
    
    
    1 Customer
    
    ↓
    
    Many Orders

* * *

# Phần 8. Participation (Mức độ tham gia)

Ngoài số lượng, còn phải xác định việc tham gia là **bắt buộc** hay **tùy chọn**.

Ví dụ:

### Mandatory (Bắt buộc)

Mỗi Order phải thuộc một Customer.
    
    
    Order
    
    ↓
    
    Customer
    
    Bắt buộc

Không thể có đơn hàng không có khách hàng.

* * *

### Optional (Tùy chọn)

Một nhân viên có thể chưa được phân công phòng làm việc.
    
    
    Employee
    
    ↓
    
    Office
    
    Optional

Khi đó khóa ngoại có thể cho phép `NULL`.

* * *

# Phần 9. Phân tích yêu cầu thực tế

## Bài toán

Xây dựng hệ thống quản lý trường học.

Yêu cầu:

  * Một trường có nhiều lớp. 
  * Một lớp có nhiều học sinh. 
  * Một giáo viên chủ nhiệm một lớp. 
  * Một giáo viên dạy nhiều môn. 
  * Một học sinh học nhiều môn. 
  * Một môn có nhiều học sinh. 



* * *

## Bước 1. Entity
    
    
    School
    
    Class
    
    Teacher
    
    Student
    
    Subject
    
    Enrollment

* * *

## Bước 2. Quan hệ
    
    
    School
    
    1
    
    ↓
    
    N
    
    Class

* * *
    
    
    Class
    
    1
    
    ↓
    
    N
    
    Student

* * *
    
    
    Teacher
    
    1
    
    ↓
    
    N
    
    Subject

* * *
    
    
    Student
    
    N
    
    ↓
    
    Enrollment
    
    ↓
    
    N
    
    Subject

* * *

# Phần 10. ERD hoàn chỉnh
    
    
    +----------------+
    | SCHOOL         |
    +----------------+
    | school_id (PK) |
    | school_name    |
    +----------------+
            |
            | 1
            |
            | N
    +----------------+
    | CLASS          |
    +----------------+
    | class_id (PK)  |
    | class_name     |
    | school_id (FK) |
    +----------------+
            |
            | 1
            |
            | N
    +----------------+
    | STUDENT        |
    +----------------+
    | student_id(PK) |
    | full_name      |
    | class_id (FK)  |
    +----------------+
    
    +----------------+
    | SUBJECT        |
    +----------------+
    | subject_id(PK) |
    | subject_name   |
    +----------------+
    
            ^             ^
            |             |
            |             |
            +-------------+
                  |
          ENROLLMENT
    +---------------------------+
    | student_id (FK)           |
    | subject_id (FK)           |
    | enroll_date               |
    | score                     |
    +---------------------------+
    PK(student_id, subject_id)

Đây là cách mô hình hóa quan hệ nhiều–nhiều đúng chuẩn.

* * *

# Phần 11. Ví dụ: Hệ thống thương mại điện tử

Entity:
    
    
    Customer
    
    Product
    
    Category
    
    Order
    
    OrderDetail
    
    Payment

ERD:
    
    
    Category
    
    1
    
    ↓
    
    N
    
    Product
    
    Customer
    
    1
    
    ↓
    
    N
    
    Order
    
    Order
    
    1
    
    ↓
    
    N
    
    OrderDetail
    
    Product
    
    1
    
    ↓
    
    N
    
    OrderDetail
    
    Order
    
    1
    
    ↓
    
    1
    
    Payment

* * *

# Phần 12. Quy trình thiết kế ERD chuyên nghiệp

### Bước 1

Đọc yêu cầu.

* * *

### Bước 2

Tìm tất cả danh từ.

Ví dụ:
    
    
    Khách hàng
    
    Sản phẩm
    
    Đơn hàng
    
    Thanh toán

* * *

### Bước 3

Tìm quan hệ.
    
    
    Khách hàng
    
    ↓
    
    Đơn hàng

* * *

### Bước 4

Xác định Cardinality.
    
    
    1
    
    ↓
    
    N

* * *

### Bước 5

Xác định khóa chính.
    
    
    id

* * *

### Bước 6

Thêm khóa ngoại.
    
    
    customer_id
    
    ↓
    
    Customer.id

* * *

### Bước 7

Chuẩn bị cho bước chuẩn hóa (Normalization), sẽ học ở các buổi tiếp theo.

* * *

# Phần 13. Công cụ vẽ ERD

Trong thực tế, bạn không cần vẽ bằng tay. Một số công cụ phổ biến:

Công cụ| Ưu điểm  
---|---  
**Draw.io (diagrams.net)**|  Miễn phí, dễ sử dụng  
**dbdiagram.io**|  Viết ERD bằng cú pháp đơn giản, hỗ trợ sinh SQL  
**DBeaver**|  Quản lý CSDL và xem ERD  
**MySQL Workbench**|  Thiết kế và quản lý MySQL  
**pgAdmin**|  Quản trị PostgreSQL, có khả năng xem phụ thuộc giữa các bảng  
**Visual Paradigm**|  Mạnh cho phân tích và thiết kế hệ thống  
  
Đối với người mới, mình khuyến nghị bắt đầu với **dbdiagram.io** hoặc **Draw.io** vì dễ học và trực quan.

* * *

# Những sai lầm phổ biến

## Sai lầm 1

Vẽ quan hệ N:N trực tiếp.
    
    
    Student
    
    >
    
    <
    
    Subject

❌ Sai.

Phải thêm bảng trung gian.

* * *

## Sai lầm 2

Không có Primary Key.

Mọi Entity trong CSDL quan hệ nên có khóa chính rõ ràng.

* * *

## Sai lầm 3

Đặt tất cả dữ liệu vào một bảng.

Ví dụ:
    
    
    Student
    
    Teacher
    
    Subject
    
    Score
    
    Department
    
    ...
    
    ↓
    
    Một bảng

Đây là nguyên nhân dẫn đến dữ liệu lặp và khó bảo trì.

* * *

## Sai lầm 4

Không xác định Business Rule trước khi vẽ ERD.

Điều này khiến sơ đồ không phản ánh đúng nghiệp vụ.

* * *

# Tổng kết buổi 5

Bạn đã học được:

  * ERD là gì và vai trò của nó trong quy trình phát triển hệ thống. 
  * Ba thành phần chính: Entity, Attribute và Relationship. 
  * Cardinality: 1:1, 1:N và N:N. 
  * Crow's Foot Notation. 
  * Mandatory và Optional Relationship. 
  * Quy trình phân tích yêu cầu và thiết kế ERD. 
  * Cách mô hình hóa hệ thống trường học và thương mại điện tử. 
  * Những lỗi thường gặp khi thiết kế ERD. 



* * *

# Bài tập thực hành

## Bài 1

Thiết kế ERD cho **hệ thống thư viện** với các Entity:

  * Book 
  * Author 
  * Category 
  * Reader 
  * BorrowSlip 
  * BorrowDetail 



Xác định:

  * Primary Key. 
  * Foreign Key. 
  * Cardinality. 
  * Quan hệ bắt buộc và tùy chọn. 



* * *

## Bài 2

Thiết kế ERD cho **ứng dụng gọi xe** :

  * Driver 
  * Passenger 
  * Vehicle 
  * Trip 
  * Payment 



Xác định đầy đủ các mối quan hệ và giải thích lựa chọn của bạn.

* * *

## Bài 3

Thiết kế ERD cho **ứng dụng mạng xã hội** :

  * User 
  * Post 
  * Comment 
  * Like 
  * FriendRequest 
  * Message 



Đặc biệt lưu ý các quan hệ nhiều–nhiều và cách tạo bảng trung gian.

* * *

## Bài 4 (Dự án nhỏ)

Thiết kế ERD hoàn chỉnh cho một **ứng dụng học ngoại ngữ** (HelloChinese/Duolingo), bao gồm tối thiểu các Entity:

  * User 
  * Course 
  * Lesson 
  * Vocabulary 
  * Grammar 
  * Question 
  * UserProgress 
  * LearningSession 
  * ReviewSchedule 



Với mỗi Entity, hãy xác định:

  * Primary Key. 
  * Các thuộc tính chính. 
  * Quan hệ với các Entity khác. 
  * Cardinality. 
  * Business Rule liên quan. 



* * *

# Chuẩn bị cho buổi 6

Ở buổi tiếp theo, chúng ta sẽ bắt đầu chủ đề cực kỳ quan trọng trong thiết kế cơ sở dữ liệu:

> **Chuẩn hóa dữ liệu (Database Normalization) – First Normal Form (1NF).**

Bạn sẽ hiểu:

  * Vì sao dữ liệu bị dư thừa. 
  * Các bất thường khi thêm, sửa, xóa dữ liệu (Insertion, Update, Deletion Anomalies). 
  * Khái niệm phụ thuộc hàm (Functional Dependency). 
  * Chuẩn 1NF và cách chuyển một bảng chưa chuẩn hóa thành bảng đạt 1NF. 



Đây là nền tảng để tiến tới 2NF, 3NF, BCNF và các chuẩn cao hơn trong những buổi tiếp theo.

