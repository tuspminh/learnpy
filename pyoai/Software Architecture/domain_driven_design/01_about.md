# Buổi 1

# Domain-Driven Design là gì?

DDD là phương pháp thiết kế phần mềm được giới thiệu bởi:

**Eric Evans**

trong cuốn sách nổi tiếng

> Domain-Driven Design: Tackling Complexity in the Heart of Software

năm 2003.

DDD không phải framework.

DDD không phải design pattern.

DDD là **một cách tư duy thiết kế hệ thống**.

* * *

## Ví dụ

Có hai lập trình viên.

Người thứ nhất viết như sau
    
    
    class Book:
        pass
    
    class User:
        pass
    
    class Database:
        pass

Ứng dụng chạy.

Không lỗi.

Nhưng sau 2 năm...

Không ai hiểu code.

* * *

Người thứ hai
    
    
    class Novel:
        pass
    
    class Chapter:
        pass
    
    class Author:
        pass
    
    class Reader:
        pass
    
    class ReadingHistory:
        pass

Chỉ nhìn class đã hiểu nghiệp vụ.

Đó là tinh thần của DDD.

* * *

# Domain là gì?

Đây là khái niệm quan trọng nhất.

Domain nghĩa là

> Lĩnh vực nghiệp vụ.

Ví dụ

Ngân hàng

Domain là
    
    
    Account
    
    Transaction
    
    Interest
    
    Transfer
    
    Loan

* * *

Bệnh viện
    
    
    Patient
    
    Doctor
    
    Prescription
    
    Appointment

* * *

Shopee
    
    
    Order
    
    Cart
    
    Voucher
    
    Payment
    
    Shipping

* * *

Ứng dụng cào truyện
    
    
    Novel
    
    Chapter
    
    Source
    
    Crawler
    
    Reader
    
    Bookmark
    
    Category

Đây chính là Domain.

* * *

# Business Logic

DDD quan tâm nhất đến

Business Logic

không phải

GUI

không phải

Database

không phải

API

* * *

Ví dụ

Một người đọc truyện.

Có luật
    
    
    Một Chapter luôn thuộc đúng một Novel.

Đó là Business Rule.

* * *
    
    
    Novel phải có tên.

Business Rule.

* * *
    
    
    Một chương không được đánh số âm.

Business Rule.

* * *

DDD đặt những luật này vào Domain.

Không đặt vào Controller.

Không đặt vào SQL.

* * *

# Vì sao DDD ra đời?

Ngày xưa người ta viết
    
    
    GUI
    
    ↓
    
    Controller
    
    ↓
    
    SQL
    
    ↓
    
    Database

Business Logic nằm rải rác khắp nơi.

Ví dụ
    
    
    Controller
    
    ↓
    
    validate
    
    ↓
    
    Repository
    
    ↓
    
    validate
    
    ↓
    
    SQL Trigger
    
    ↓
    
    validate

Không ai biết luật nằm ở đâu.

* * *

DDD nói rằng
    
    
    Business Rule
    
    ↓
    
    Domain Model

Mọi luật nghiệp vụ đều ở Domain.

* * *

# Ví dụ không dùng DDD
    
    
    class UserController:
    
        def register(self, username):
    
            if len(username) < 3:
                raise ValueError()
    
            database.save(username)

Logic nằm trong Controller.

* * *

Sau này

API

Desktop

CLI

Web

đều phải copy.

* * *

# Theo DDD
    
    
    class User:
    
        def __init__(self, username):
    
            if len(username) < 3:
                raise ValueError()
    
            self.username = username

Bất kỳ nơi nào tạo User

đều phải tuân theo luật.

* * *

# Ví dụ với App cào truyện

Không nên
    
    
    def add_chapter(chapter):
    
        if chapter.index < 1:
            raise Exception()

Nên
    
    
    class Chapter:
    
        def __init__(self, index):
    
            if index < 1:
                raise ValueError(
                    "Chapter index must be >=1"
                )
    
            self.index = index

Luật luôn nằm trong Domain.

* * *

# Một sai lầm phổ biến

Nhiều người nghĩ DDD là
    
    
    Model
    
    ↓
    
    Repository
    
    ↓
    
    Service

Sai.

DDD không nói về folder.

DDD nói về

> Mô hình hóa nghiệp vụ.

* * *

# DDD tập trung vào cái gì?

Ví dụ
    
    
    App bán hàng

DDD không hỏi
    
    
    SQLite?
    
    MySQL?
    
    FastAPI?
    
    Flask?
    
    PySide?

DDD hỏi
    
    
    Khách hàng là ai?
    
    Đơn hàng là gì?
    
    Voucher hoạt động ra sao?
    
    Khi nào đơn hàng hợp lệ?
    
    Thanh toán có những trạng thái nào?

* * *

# So sánh

Không dùng DDD
    
    
    Database
    
    ↓
    
    Entity
    
    ↓
    
    CRUD
    
    ↓
    
    Done

DDD
    
    
    Business
    
    ↓
    
    Model
    
    ↓
    
    Rule
    
    ↓
    
    Behavior
    
    ↓
    
    Persistence

Business luôn đứng trước Database.

* * *

# Ví dụ lớn

Giả sử xây app ngân hàng.

Không dùng DDD
    
    
    balance -= money

* * *

DDD
    
    
    account.withdraw(money)

Bên trong
    
    
    class Account:
    
        def withdraw(self, amount):
    
            if amount <= 0:
                raise InvalidAmount()
    
            if amount > self.balance:
                raise NotEnoughMoney()
    
            self.balance -= amount

Business Rule nằm trong Entity.

* * *

# Một ví dụ khác

Không dùng DDD
    
    
    cursor.execute("""
    UPDATE account
    SET balance = balance - 100
    """)

SQL đang chứa Business.

Khó test.

Khó tái sử dụng.

* * *

DDD
    
    
    account.withdraw(100)
    
    repository.save(account)

Repository chỉ lưu dữ liệu.

Entity quyết định luật.

* * *

# Kiến trúc tổng quát của DDD
    
    
    Presentation
    
            │
    
    Application
    
            │
    
    -----------------
    
    Domain
    
    -----------------
    
    Infrastructure

Trong đó:

  * **Presentation** : giao diện (CLI, Web, Desktop, API). 
  * **Application** : điều phối các use case. 
  * **Domain** : trái tim của hệ thống, chứa nghiệp vụ. 
  * **Infrastructure** : cơ sở dữ liệu, HTTP, file, Redis, message queue,... 



Mọi lớp bên ngoài đều **phụ thuộc vào Domain** , còn Domain không phụ thuộc vào chúng.

* * *

# Ví dụ thư mục Python
    
    
    src/
    │
    ├── application/
    │
    ├── domain/
    │   ├── entities/
    │   ├── value_objects/
    │   ├── repositories/
    │   ├── services/
    │   ├── events/
    │   └── exceptions.py
    │
    ├── infrastructure/
    │   ├── sqlite/
    │   ├── crawler/
    │   └── cache/
    │
    └── presentation/
        ├── cli/
        ├── api/
        └── gui/

Lưu ý: đây chỉ là **một cách tổ chức phổ biến** , không phải quy định bắt buộc của DDD.

* * *

# Bài tập

## Bài 1

Với ứng dụng cào truyện, hãy liệt kê các Domain Object mà bạn nghĩ cần có, ví dụ:

  * Novel 
  * Chapter 
  * Author 
  * Category 
  * Source 
  * Bookmark 
  * ReadingHistory 
  * ... 



Hãy thử bổ sung thêm các đối tượng khác nếu cần.

* * *

## Bài 2

Với ứng dụng quản lý thư viện, hãy xác định:

  * Business Rule là gì? 
  * Điều gì chỉ là dữ liệu? 
  * Điều gì là hành vi (behavior)? 



Ví dụ:

  * "Một cuốn sách không thể được mượn nếu đang ở trạng thái đã được mượn." → Business Rule. 
  * "Tiêu đề sách." → Dữ liệu. 
  * `borrow()` hoặc `return_book()` → Hành vi. 



* * *

# Tổng kết

Sau buổi đầu tiên, bạn cần nắm được các ý cốt lõi:

  * DDD là **một phương pháp thiết kế phần mềm** , không phải framework hay design pattern. 
  * Trọng tâm của DDD là **Domain (nghiệp vụ)** chứ không phải database hay giao diện. 
  * **Business Rule phải nằm trong Domain Model** , không rải rác ở Controller, SQL hay UI. 
  * Entity không chỉ chứa dữ liệu mà còn **đóng gói hành vi và bảo vệ các quy tắc nghiệp vụ**. 
  * Repository có nhiệm vụ lưu/truy xuất dữ liệu, **không chứa business logic**. 



Trong **Buổi 2** , chúng ta sẽ học **Ubiquitous Language** — nền tảng giúp lập trình viên và chuyên gia nghiệp vụ sử dụng cùng một "ngôn ngữ chung", từ đó xây dựng các mô hình Domain chính xác và dễ bảo trì. Đây là bước đầu tiên để thiết kế một hệ thống DDD chuyên nghiệp.

