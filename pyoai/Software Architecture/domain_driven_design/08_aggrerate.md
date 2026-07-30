# Domain-Driven Design Deep Dive

# Buổi 8: Aggregate — Ranh giới bảo vệ Domain Model

Sau khi học:

  * Entity 
  * Value Object 



chúng ta bắt đầu gặp một vấn đề lớn:

> Nếu hệ thống có hàng nghìn Entity, làm sao kiểm soát việc chúng thay đổi lẫn nhau?

Đây chính là lý do DDD sinh ra khái niệm:

# Aggregate

* * *

# Roadmap

✅ Buổi 1: DDD là gì

✅ Buổi 2: Ubiquitous Language

✅ Buổi 3: Domain & Subdomain

✅ Buổi 4: Bounded Context

✅ Buổi 5: Context Mapping

✅ Buổi 6: Entity

✅ Buổi 7: Value Object

✅ **Buổi 8: Aggregate**

⬜ Buổi 9: Aggregate Root

⬜ Buổi 10: Repository

⬜ Buổi 11: Domain Service

⬜ Buổi 12: Domain Event

* * *

# 1\. Vấn đề khi chỉ có Entity

Giả sử hệ thống bán hàng:
    
    
    Order
    
    Customer
    
    Product
    
    Inventory
    
    Payment

* * *

Một lập trình viên có thể viết:
    
    
    order.items[0].product.stock -= 1

Hoặc:
    
    
    customer.orders.append(order)

Hoặc:
    
    
    product.price = -100

Bất kỳ nơi nào cũng có thể sửa Entity.

Kết quả:
    
    
    Trạng thái hệ thống bị phá vỡ

* * *

DDD đặt câu hỏi:

> Ai có quyền thay đổi Entity này?

* * *

# 2\. Aggregate là gì?

Định nghĩa:

> Aggregate là một nhóm các object Domain được gom lại thành một đơn vị thay đổi và nhất quán.

Nói đơn giản:

> Aggregate là một "cụm Entity + Value Object" được bảo vệ bởi một cửa vào duy nhất.

* * *

Ví dụ:
    
    
    Order Aggregate
    
    
            Order
              |
              |
        -------------
        |           |
     OrderItem   Address
        |
     ProductSnapshot

* * *

Bên ngoài không được tự ý sửa:
    
    
    OrderItem

mà phải thông qua:
    
    
    Order

* * *

# 3\. Aggregate giống như một cái hộp

Ví dụ:
    
    
    +--------------------------------+
    
                Order
    
        +----------------+
        | OrderItem      |
        +----------------+
    
        +----------------+
        | Money          |
        +----------------+
    
    +--------------------------------+

Bên ngoài:
    
    
    Order

là cửa duy nhất.

* * *

# 4\. Aggregate Root

Khái niệm này sẽ học sâu ở buổi 9.

Nhưng cần biết trước:

Aggregate luôn có một Entity đứng đầu.

Gọi là:
    
    
    Aggregate Root

Ví dụ:
    
    
    Order

là Root.

* * *

Không được:
    
    
    item.quantity = 0

Mà:
    
    
    order.change_quantity(
        item_id,
        3
    )

* * *

# 5\. Ví dụ đơn giản: Shopping Cart

Không có Aggregate:
    
    
    cart.items.append(product)

Ai cũng sửa được.

* * *

DDD:
    
    
    Cart Aggregate
    
    
    Cart
     |
     +-- CartItem
     |
     +-- Money

* * *

Code:
    
    
    class Cart:
    
        def __init__(self):
            self.items = []
    
    
        def add_item(
            self,
            product_id,
            quantity
        ):
    
            if quantity <= 0:
                raise ValueError(
                    "Invalid quantity"
                )
    
            item = CartItem(
                product_id,
                quantity
            )
    
            self.items.append(item)

* * *

Bên ngoài:

Sai:
    
    
    cart.items.append(
        CartItem(...)
    )

Đúng:
    
    
    cart.add_item(
        product_id=1,
        quantity=2
    )

* * *

# 6\. Aggregate bảo vệ Business Rule

Ví dụ:

Một Order không được thanh toán hai lần.

Sai:
    
    
    order.status = "paid"

Ai cũng làm được.

* * *

Đúng:
    
    
    class Order:
    
        def pay(self):
    
            if self.status == "PAID":
                raise Exception(
                    "Already paid"
                )
    
            self.status = "PAID"

* * *

Business Rule nằm trong Aggregate.

* * *

# 7\. Aggregate không phải quan hệ Database

Đây là lỗi phổ biến.

Nhiều người nghĩ:

Database:
    
    
    orders
    
    order_items

thì:
    
    
    Order Aggregate
    
    =
    Order + OrderItem

Không nhất thiết.

* * *

Aggregate là ranh giới nghiệp vụ.

Không phải ranh giới bảng.

* * *

Ví dụ:

Database:
    
    
    users
    
    orders
    
    products

Nhưng Domain:
    
    
    User Aggregate
    
    Order Aggregate
    
    Product Aggregate

* * *

# 8\. Ví dụ Order Aggregate hoàn chỉnh

## Entity Order
    
    
    from enum import Enum
    
    
    class OrderStatus(Enum):
    
        CREATED = "created"
        PAID = "paid"
        CANCELLED = "cancelled"
    
    
    
    class Order:
    
    
        def __init__(
            self,
            order_id
        ):
    
            self.id = order_id
            self.status = (
                OrderStatus.CREATED
            )
    
            self.items = []
    
    
        def add_item(
            self,
            item
        ):
    
            if self.status != OrderStatus.CREATED:
                raise Exception(
                    "Cannot modify order"
                )
    
            self.items.append(item)
    
    
        def pay(self):
    
            if not self.items:
                raise Exception(
                    "Empty order"
                )
    
            self.status = (
                OrderStatus.PAID
            )

* * *

## OrderItem
    
    
    class OrderItem:
    
    
        def __init__(
            self,
            product_id,
            quantity
        ):
    
            self.product_id = product_id
            self.quantity = quantity

* * *

Cách dùng:
    
    
    order = Order(1)
    
    
    order.add_item(
        OrderItem(
            100,
            2
        )
    )
    
    
    order.pay()

* * *

# 9\. Aggregate trong App Cào Truyện

Bây giờ áp dụng vào dự án của bạn.

Chúng ta có:
    
    
    Novel
    Chapter
    Reader
    Bookmark
    ReadingHistory

* * *

Một thiết kế sai:
    
    
    Novel
     |
     +-- tất cả Chapter
     |
     +-- tất cả Bookmark
     |
     +-- tất cả Reader

Vì:

Một truyện có thể có:
    
    
    5000 Chapter

Không thể load toàn bộ mỗi lần.

* * *

# 10\. Thiết kế tốt hơn

## Novel Aggregate
    
    
    Novel Aggregate
    
    
    Novel
     |
     +-- NovelId
     |
     +-- Title
     |
     +-- Status

* * *

Không chứa toàn bộ Chapter.

* * *

## Chapter Aggregate
    
    
    Chapter Aggregate
    
    
    Chapter
    
     |
     +-- ChapterNumber
     |
     +-- Content

* * *

## Reader Aggregate
    
    
    Reader Aggregate
    
    
    Reader
    
     |
     +-- Email
     |
     +-- ReadingPreference

* * *

## ReadingProgress Aggregate
    
    
    ReadingProgress
    
    
    ReaderId
    
    NovelId
    
    ChapterId
    
    Position

* * *

# 11\. Vì sao Chapter không nằm trong Novel?

Ví dụ:

Truyện:
    
    
    Đấu Phá Thương Khung

có:
    
    
    1648 chapter

Nếu:
    
    
    novel.chapters

chứa tất cả:
    
    
    1648 object

thì:

  * Load chậm 
  * Update khó 
  * Transaction lớn 



* * *

DDD khuyên:

Tách Aggregate.

* * *

# 12\. Aggregate nhỏ tốt hơn Aggregate lớn

Sai:
    
    
    Library Aggregate
    
    Library
     |
     +-- User
     |
     +-- All Novels
     |
     +-- All Chapters
     |
     +-- All Bookmark

Quá lớn.

* * *

Đúng:
    
    
    User Aggregate
    
    
    Novel Aggregate
    
    
    Chapter Aggregate
    
    
    Bookmark Aggregate

* * *

# 13\. Aggregate và Transaction

Một Aggregate thường là:
    
    
    một transaction boundary

Ví dụ:

Thanh toán Order:
    
    
    BEGIN TRANSACTION
    
    Order.status = PAID
    
    COMMIT

* * *

Không nên:

Một transaction sửa:
    
    
    Order
    
    Inventory
    
    Recommendation
    
    Statistics

cùng lúc.

* * *

Thay vào đó:
    
    
    Order Paid Event
    
            |
            |
            +---- Inventory cập nhật
    
            +---- Statistics cập nhật

* * *

# 14\. Aggregate và Domain Event

Ví dụ:

Order:
    
    
    def pay(self):
    
        self.status = PAID
    
        return OrderPaid(
            self.id
        )

* * *

Event:
    
    
    class OrderPaid:
    
        def __init__(
            self,
            order_id
        ):
            self.order_id = order_id

* * *

Các Context khác nghe:
    
    
    OrderPaid

và xử lý.

* * *

# 15\. Aggregate trong Clean Architecture

Cấu trúc:
    
    
    domain/
    
        order/
    
            entities/
    
                order.py
    
                order_item.py
    
            value_objects/
    
                money.py
    
            events/
    
                order_paid.py

* * *

Application:
    
    
    use case
    
        create_order
    
        pay_order

* * *

Infrastructure:
    
    
    repository
    
    database

* * *

# 16\. Aggregate Rule quan trọng

## Rule 1

Bên ngoài chỉ truy cập Aggregate Root.

Sai:
    
    
    order.items[0].quantity = 10

* * *

Đúng:
    
    
    order.change_quantity(
        item_id,
        10
    )

* * *

# Rule 2

Aggregate không tham chiếu trực tiếp Aggregate khác.

Sai:
    
    
    class Order:
    
        customer: Customer

* * *

Đúng:
    
    
    class Order:
    
        customer_id: CustomerId

* * *

Chỉ giữ ID.

* * *

# Rule 3

Aggregate phải nhỏ.

Không thiết kế:
    
    
    Company Aggregate
    
        |
        +-- Employee
        +-- Department
        +-- Project
        +-- Payroll

* * *

# 17\. Ví dụ App Cào Truyện: Aggregate Design
    
    
    Source Aggregate
    
    Source
     |
     +-- Url
     +-- PluginName
     +-- Status
    
    
    
    Novel Aggregate
    
    Novel
     |
     +-- NovelId
     +-- Title
     +-- Category
    
    
    
    Chapter Aggregate
    
    Chapter
     |
     +-- ChapterId
     +-- Number
     +-- Content
    
    
    
    Reading Aggregate
    
    ReadingProgress
     |
     +-- ReaderId
     +-- NovelId
     +-- ChapterId

* * *

Giao tiếp:
    
    
    Crawler
    
       |
       |
    NovelCreated Event
    
       |
       |
    Library
    
       |
       |
    Reader

* * *

# 18\. Khi nào tạo Aggregate mới?

Hỏi:

## 1\. Có cùng vòng đời không?

Ví dụ:

Order + OrderItem

Có.

* * *

## 2\. Có luôn thay đổi cùng nhau không?

Có.

* * *

## 3\. Có cùng transaction không?

Có.

* * *

Nếu không:

Tách.

* * *

# 19\. Lỗi thường gặp

## Lỗi 1

Mỗi bảng database = Aggregate.

Sai.

* * *

## Lỗi 2

Aggregate quá lớn.

Ví dụ:
    
    
    User
     |
     +-- Orders
     +-- Payments
     +-- Address
     +-- History

* * *

## Lỗi 3

Cho phép sửa Entity con trực tiếp.

Sai:
    
    
    chapter.title = "abc"

* * *

## Lỗi 4

Aggregate gọi database.

Sai:
    
    
    class Order:
    
        def save()

* * *

# Bài tập

## Bài 1

Thiết kế Aggregate cho:
    
    
    Blog System

Có:

  * User 
  * Post 
  * Comment 
  * Like 



Xác định:

  * Aggregate Root 
  * Entity bên trong 
  * Value Object 



* * *

## Bài 2

Thiết kế Aggregate cho App Cào Truyện:

Xác định:
    
    
    Novel
    Chapter
    Reader
    Bookmark
    History

cái nào cùng Aggregate.

* * *

## Bài 3

Refactor:
    
    
    class Novel:
    
        chapters: list[Chapter]
    
        bookmarks: list[Bookmark]
    
        readers: list[Reader]

thành các Aggregate hợp lý.

* * *

# Tổng kết Buổi 8

Cần nhớ:

  * Aggregate là nhóm Entity + Value Object có cùng mục đích nghiệp vụ. 
  * Aggregate tạo ra ranh giới bảo vệ Domain Model. 
  * Mỗi Aggregate có một **Aggregate Root**. 
  * Bên ngoài chỉ làm việc qua Root. 
  * Aggregate không phải là database table. 
  * Aggregate nên nhỏ. 
  * Các Aggregate giao tiếp qua Event hoặc ID, không tham chiếu trực tiếp. 



* * *

Buổi tiếp theo (**Buổi 9**) chúng ta sẽ đi sâu vào **Aggregate Root** :

  * Vì sao Root là "cửa duy nhất"? 
  * Cách thiết kế Root trong Python. 
  * Quy tắc invariant. 
  * Repository chỉ làm việc với Root. 
  * Thiết kế hoàn chỉnh `Order Aggregate` và `Novel Aggregate` theo DDD.

