# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 21: OOP - Phần 6: Trừu tượng (Abstraction), SOLID, Dependency Injection và Tư duy Thiết kế Phần mềm

> **Đây là một trong những buổi học quan trọng nhất của toàn bộ khóa học.**
> 
> Sau buổi này, bạn sẽ không chỉ biết viết Class, mà còn biết **thiết kế hệ thống phần mềm** theo tư duy của lập trình viên chuyên nghiệp.

---

# Mục tiêu buổi học

Sau khi học xong bạn sẽ:

- Hiểu Abstraction (Trừu tượng)
- Phân biệt Abstraction và Encapsulation
- Hiểu Interface trong Python
- Hiểu Dependency Injection (DI)
- Hiểu Inversion of Control (IoC)
- Làm quen với 5 nguyên lý SOLID
- Biết cách thiết kế phần mềm dễ mở rộng
- Biết cách refactor code từ Procedural sang OOP

---

# Phần 1. Abstraction là gì?

Abstraction nghĩa là:

> **Chỉ cho người dùng thấy những gì cần thiết, còn chi tiết bên trong được che giấu.**

Ví dụ:

Bạn lái ô tô.

Bạn chỉ cần:

```text-x-trilium-auto
Đạp ga

↓

Xe chạy
```

Bạn không cần biết:

- ECU
- Hộp số
- Phun xăng
- Đánh lửa
- Turbo

Tất cả đều được **ẩn**.

Đó chính là Abstraction.

---

# Phần 2. Encapsulation khác Abstraction

Rất nhiều người nhầm hai khái niệm này.

## Encapsulation

Tập trung vào:

> **Bảo vệ dữ liệu**

Ví dụ:

```text-x-trilium-auto
class BankAccount:

    @property
    def balance(self):
        ...
```

Không cho sửa trực tiếp.

---

## Abstraction

Tập trung vào:

> **Ẩn cách hoạt động**

Ví dụ:

```text-x-trilium-auto
payment.pay(100)
```

Bạn không cần biết:

- HTTPS
- API
- Encryption
- Token

---

# Phần 3. Ví dụ thực tế

Giả sử:

```text-x-trilium-auto
payment.pay(100)
```

Bên trong có thể:

```text-x-trilium-auto
↓

Validate

↓

Encrypt

↓

Send API

↓

Receive Response

↓

Retry

↓

Logging
```

Người dùng chỉ thấy:

```text-x-trilium-auto
payment.pay(100)
```

---

# Phần 4. Interface trong Python

Python không có keyword:

```text-x-trilium-auto
interface
```

như Java.

Python dùng:

- ABC
- Protocol

để đóng vai trò Interface.

Ví dụ:

```text-x-trilium-auto
from abc import ABC, abstractmethod

class Storage(ABC):

    @abstractmethod
    def upload(self, file):
        pass
```

---

# Phần 5. Vì sao cần Interface?

Không dùng Interface:

```text-x-trilium-auto
class App:

    def __init__(self):

        self.storage = S3Storage()
```

App phụ thuộc chặt vào:

```text-x-trilium-auto
S3Storage
```

Muốn đổi:

```text-x-trilium-auto
Azure
```

↓

Phải sửa App.

---

# Phần 6. Dependency Injection (DI)

Thay vì:

```text-x-trilium-auto
class App:

    def __init__(self):

        self.storage = S3Storage()
```

Ta làm:

```text-x-trilium-auto
class App:

    def __init__(self, storage):

        self.storage = storage
```

Sử dụng:

```text-x-trilium-auto
app = App(S3Storage())
```

Hoặc:

```text-x-trilium-auto
app = App(LocalStorage())
```

Hoặc:

```text-x-trilium-auto
app = App(MockStorage())
```

App không cần biết cụ thể lớp nào được dùng.

---

# Phần 7. Lợi ích của DI

Ví dụ:

```text-x-trilium-auto
class EmailService:
```

Có thể thay bằng:

```text-x-trilium-auto
SMTP
```

↓

```text-x-trilium-auto
SendGrid
```

↓

```text-x-trilium-auto
Amazon SES
```

Mà không cần sửa App.

---

# Phần 8. Inversion of Control (IoC)

Thông thường:

```text-x-trilium-auto
App

↓

tự tạo

↓

Database
```

DI:

```text-x-trilium-auto
Database

↓

được truyền vào

↓

App
```

Quyền kiểm soát việc tạo đối tượng đã được đảo ngược.

Đó là **Inversion of Control**.

---

# Phần 9. Giới thiệu SOLID

SOLID gồm 5 nguyên lý.

Đây là nền tảng của hầu hết framework hiện đại.

---

# S — Single Responsibility Principle (SRP)

Một Class:

> Chỉ nên có **một lý do để thay đổi**.

Sai:

```text-x-trilium-auto
class User:

    save_database()

    send_email()

    export_excel()

    login()

    logout()
```

Một class làm quá nhiều việc.

Đúng:

```text-x-trilium-auto
User

↓

UserRepository

↓

EmailService

↓

ExcelExporter
```

---

# O — Open Closed Principle (OCP)

> Mở để mở rộng

> Đóng để sửa đổi

Ví dụ:

```text-x-trilium-auto
process(payment)
```

Sau này thêm:

```text-x-trilium-auto
Crypto
```

Không sửa:

```text-x-trilium-auto
process()
```

Chỉ thêm class mới.

---

# L — Liskov Substitution Principle (LSP)

Nếu:

```text-x-trilium-auto
Dog

là

Animal
```

Thì:

```text-x-trilium-auto
Animal
```

phải có thể thay bằng:

```text-x-trilium-auto
Dog
```

mà chương trình vẫn đúng.

---

# I — Interface Segregation Principle (ISP)

Không ép class phải cài đặt những phương thức không dùng.

Sai:

```text-x-trilium-auto
class Bird:

    fly()

    swim()
```

Chim cánh cụt?

Không bay.

Nên tách:

```text-x-trilium-auto
Flyable

Swimmable
```

---

# D — Dependency Inversion Principle (DIP)

Không phụ thuộc:

```text-x-trilium-auto
MySQL
```

Mà phụ thuộc:

```text-x-trilium-auto
Database
```

Interface.

Ví dụ:

```text-x-trilium-auto
class App:

    def __init__(self, db):
        self.db = db
```

---

# Phần 10. Ví dụ thực tế

Ví điện tử.

Sai:

```text-x-trilium-auto
class Wallet:

    def pay():

        if momo:

        if visa:

        if paypal:
```

Mỗi lần thêm cổng thanh toán phải sửa mã.

Đúng:

```text-x-trilium-auto
PaymentGateway
```

↓

```text-x-trilium-auto
Visa

Momo

Paypal

Crypto
```

Wallet chỉ biết:

```text-x-trilium-auto
gateway.pay()
```

---

# Phần 11. Refactor Procedural sang OOP

Code thủ tục:

```text-x-trilium-auto
def calculate_salary():
    ...
```

↓

```text-x-trilium-auto
def export_excel():
    ...
```

↓

```text-x-trilium-auto
def send_email():
    ...
```

↓

Tất cả nằm trong một file.

---

Refactor:

```text-x-trilium-auto
Employee
```

↓

```text-x-trilium-auto
SalaryCalculator
```

↓

```text-x-trilium-auto
ExcelExporter
```

↓

```text-x-trilium-auto
EmailService
```

Dễ bảo trì hơn nhiều.

---

# Phần 12. Thiết kế Module

Sai:

```text-x-trilium-auto
main.py

4000 dòng
```

Đúng:

```text-x-trilium-auto
project/

│

├── models/

├── services/

├── repositories/

├── utils/

├── config/

├── api/

├── database/

└── main.py
```

Đây là cấu trúc phổ biến của các dự án Python hiện đại.

---

# Phần 13. Clean Code

Đặt tên rõ ràng.

Sai:

```text-x-trilium-auto
x()

do()
```

Đúng:

```text-x-trilium-auto
calculate_total_price()
```

---

Không viết:

```text-x-trilium-auto
if...

if...

if...

if...

if...
```

Hãy dùng Polymorphism.

---

Không viết:

```text-x-trilium-auto
100
```

↓

```text-x-trilium-auto
MAX_LOGIN_RETRY = 5
```

Dùng hằng số có ý nghĩa thay vì "magic numbers".

---

# Phần 14. Kiến trúc thực tế

Ví dụ:

Ứng dụng thương mại điện tử.

```text-x-trilium-auto
Controller

↓

Service

↓

Repository

↓

Database
```

Mỗi tầng có nhiệm vụ riêng.

---

# Phần 15. Ví dụ AI hiện đại

```text-x-trilium-auto
Chat App

↓

AI Interface

↓

GPT

Claude

Gemini

Llama
```

Chat App không biết model nào.

Chỉ gọi:

```text-x-trilium-auto
generate()
```

---

# Phần 16. Ví dụ Cloud

```text-x-trilium-auto
Storage
```

↓

```text-x-trilium-auto
AWS

Azure

Google Cloud

Local
```

Ứng dụng chỉ cần:

```text-x-trilium-auto
storage.upload()
```

---

# Phần 17. Những lỗi phổ biến

## Lỗi 1

Mọi thứ nhét vào:

```text-x-trilium-auto
main.py
```

---

## Lỗi 2

Một class dài:

```text-x-trilium-auto
3000 dòng
```

---

## Lỗi 3

Không tách:

- Service
- Model
- Repository

---

## Lỗi 4

Không dùng Interface.

Sau này đổi Database rất khó.

---

# Phần 18. Bài tập thực hành

## Bài 1

Thiết kế:

```text-x-trilium-auto
Storage
```

↓

- LocalStorage
- CloudStorage

Sử dụng Dependency Injection để truyền loại lưu trữ vào ứng dụng.

---

## Bài 2

Thiết kế:

```text-x-trilium-auto
PaymentGateway
```

↓

- Visa
- PayPal
- Momo

Viết một lớp `CheckoutService` chỉ phụ thuộc vào giao diện `PaymentGateway`.

---

## Bài 3

Refactor:

```text-x-trilium-auto
process_order()
```

thành:

- Order
- OrderService
- EmailService

---

## Bài 4

Áp dụng SRP cho một lớp đang làm nhiều nhiệm vụ.

---

## Bài 5

Thiết kế:

```text-x-trilium-auto
Notification
```

↓

- Email
- SMS
- Push Notification

Không dùng:

```text-x-trilium-auto
if...
```

---

## Bài 6

Thiết kế hệ thống AI.

```text-x-trilium-auto
AIModel
```

↓

GPT

Claude

Gemini

DeepSeek

Viết:

```text-x-trilium-auto
chat(model)
```

sao cho có thể thêm mô hình mới mà không cần sửa hàm `chat()`.

---

# Mini Project: Hệ thống Thương mại Điện tử

Thiết kế kiến trúc:

```text-x-trilium-auto
models/
```

- Product
- Customer
- Order

```text-x-trilium-auto
repositories/
```

- ProductRepository
- OrderRepository

```text-x-trilium-auto
services/
```

- PaymentService
- OrderService
- EmailService

```text-x-trilium-auto
interfaces/
```

- PaymentGateway
- Storage

```text-x-trilium-auto
gateways/
```

- VisaGateway
- MomoGateway
- PayPalGateway

```text-x-trilium-auto
main.py
```

Yêu cầu:

- Sử dụng **ABC** cho các giao diện.
- Áp dụng **Dependency Injection** khi tạo `OrderService`.
- Không sử dụng `if...elif...` để chọn cổng thanh toán.
- Tuân thủ SRP và OCP.

---

# Tổng kết buổi 21

Hôm nay bạn đã học:

- ✅ Abstraction (Trừu tượng).
- ✅ Phân biệt Abstraction và Encapsulation.
- ✅ Interface trong Python.
- ✅ Dependency Injection (DI).
- ✅ Inversion of Control (IoC).
- ✅ 5 nguyên lý SOLID.
- ✅ Tổ chức module theo kiến trúc nhiều tầng.
- ✅ Refactor từ mã thủ tục sang OOP.
- ✅ Tư duy thiết kế hệ thống có khả năng mở rộng.

---

# Góc lập trình viên chuyên nghiệp

Đây là những khái niệm bạn sẽ gặp trong hầu hết các dự án Python lớn:

- **Django**: chia thành Model, View, Form, Service (ở nhiều dự án), Repository.
- **FastAPI**: thường kết hợp Dependency Injection với Pydantic để quản lý dữ liệu và phụ thuộc.
- **SQLAlchemy**: tách Entity, Session, Repository.
- **PySide6/Flet**: phân tách giao diện, logic nghiệp vụ và truy cập dữ liệu.

Điều quan trọng không phải là "dùng thật nhiều class", mà là **mỗi class có một trách nhiệm rõ ràng, phụ thuộc vào giao diện thay vì cài đặt cụ thể, và có thể mở rộng mà không phải sửa mã cũ**.

---

# Lộ trình tiếp theo

Đến đây, bạn đã hoàn thành **6 buổi cốt lõi về OOP**, đủ nền tảng để đọc và viết các dự án Python hiện đại.

Từ **Buổi 22**, chúng ta sẽ chuyển sang một chủ đề rất quan trọng đối với lập trình viên Python chuyên nghiệp:

# **Exception Handling & Logging**

Bạn sẽ học:

- Hệ thống Exception của Python.
- `try`, `except`, `else`, `finally`.
- `raise` và tạo Exception tùy chỉnh.
- Context Manager (`with`).
- Module `logging`.
- Ghi log theo chuẩn cho ứng dụng thực tế.
- Thiết kế cơ chế xử lý lỗi cho CLI, Web API và ứng dụng GUI.

Đây là bước giúp bạn viết những chương trình **ổn định, dễ gỡ lỗi và phù hợp để triển khai trong môi trường thực tế**.
