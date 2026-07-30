# Domain-Driven Design Deep Dive

# Buổi 9: Aggregate Root — Người bảo vệ luật nghiệp vụ

Trong buổi 8 chúng ta học:

  * Aggregate là một nhóm Entity + Value Object. 
  * Aggregate tạo ra ranh giới bảo vệ Domain. 
  * Bên ngoài không được tùy tiện thay đổi các object bên trong. 



Nhưng còn một câu hỏi:

> Nếu Aggregate có nhiều Entity, ai là người chịu trách nhiệm kiểm soát?

Câu trả lời:

# Aggregate Root

* * *

# Roadmap

✅ Buổi 1: DDD là gì

✅ Buổi 2: Ubiquitous Language

✅ Buổi 3: Domain & Subdomain

✅ Buổi 4: Bounded Context

✅ Buổi 5: Context Mapping

✅ Buổi 6: Entity

✅ Buổi 7: Value Object

✅ Buổi 8: Aggregate

✅ **Buổi 9: Aggregate Root**

⬜ Buổi 10: Repository

⬜ Buổi 11: Domain Service

⬜ Buổi 12: Domain Event

* * *

# 1\. Aggregate Root là gì?

Định nghĩa:

> Aggregate Root là Entity chính đại diện cho một Aggregate và là điểm truy cập duy nhất từ bên ngoài.

Nói đơn giản:

> Aggregate Root là "cửa chính" của Aggregate.

* * *

Ví dụ:

Một căn nhà:
    
    
    +-----------------------+
    
            House
            (Root)
    
         Door
         Room
         Furniture
    
    +-----------------------+

Bạn không vào nhà bằng cách:
    
    
    Furniture → Room → House

Bạn đi qua:
    
    
    Door → House

* * *

Trong DDD:
    
    
    Outside World
    
          |
          v
    
    Aggregate Root
    
          |
          |
          +---- Entity con
          |
          +---- Value Object

* * *

# 2\. Ví dụ Order Aggregate

Một đơn hàng:
    
    
    Order
    
     |
     +-- OrderItem
    
     |
     +-- ShippingAddress
    
     |
     +-- Money

Ai chịu trách nhiệm?
    
    
    Order

là Root.

* * *

Không được:
    
    
    order_item.quantity = 100

* * *

Phải:
    
    
    order.change_quantity(
        item_id=10,
        quantity=100
    )

* * *

# 3\. Vì sao cần Aggregate Root?

Không có Root:

Mọi nơi đều có thể:
    
    
    item.price = -500

hoặc:
    
    
    order.status = "PAID"

hoặc:
    
    
    order.items.clear()

Hệ thống mất kiểm soát.

* * *

Aggregate Root đảm bảo:

  * Business Rule luôn đúng. 
  * State luôn hợp lệ. 
  * Transaction có ranh giới rõ ràng. 



* * *

# 4\. Ví dụ đời thực: Ngân hàng

Sai thiết kế:
    
    
    BankAccount
    
    Transaction
    
    Money

Ai cũng sửa:
    
    
    money.amount = -100000

* * *

Đúng:
    
    
    BankAccount Aggregate
    
    
    BankAccount (Root)
    
          |
          |
          +-- Balance
          |
          +-- Transaction

* * *

Bên ngoài:
    
    
    account.withdraw(
        100000
    )

Không:
    
    
    account.balance -= 100000

* * *

# 5\. Aggregate Root chứa Invariant

Một khái niệm rất quan trọng:

# Invariant

là:

> Luật luôn phải đúng trong mọi thời điểm.

* * *

Ví dụ Order:

Luật:
    
    
    Order đã thanh toán
    không được thêm sản phẩm

* * *

Sai:
    
    
    order.status = "PAID"
    
    order.items.append(item)

* * *

Đúng:
    
    
    order.add_item(item)

và bên trong:
    
    
    def add_item(self, item):
    
        if self.status == "PAID":
            raise Exception(
                "Cannot modify paid order"
            )
    
        self.items.append(item)

* * *

# 6\. Aggregate Root kiểm soát Entity con

Ví dụ:
    
    
    class OrderItem:
    
        def __init__(
            self,
            product_id,
            quantity
        ):
            self.product_id = product_id
            self.quantity = quantity

* * *

Không nên cho:
    
    
    item.quantity = -1

* * *

Thay đổi thông qua Order:
    
    
    class Order:
    
        def update_quantity(
            self,
            item_id,
            quantity
        ):
    
            if quantity <= 0:
                raise ValueError()
    
            item = self.find_item(item_id)
    
            item.change_quantity(quantity)

* * *

# 7\. Entity bên trong Aggregate có Repository không?

Câu trả lời:

Không.

Ví dụ:
    
    
    Order Aggregate
    
    
    Order
     |
     +-- OrderItem
     |
     +-- Money

Chỉ có:
    
    
    OrderRepository

* * *

Không có:
    
    
    OrderItemRepository

* * *

Vì:

OrderItem không tồn tại độc lập.

* * *

# 8\. Ví dụ Python hoàn chỉnh

## Money Value Object
    
    
    from dataclasses import dataclass
    
    
    @dataclass(frozen=True)
    class Money:
    
        amount: int
        currency: str = "VND"
    
    
        def add(self, other):
    
            if self.currency != other.currency:
                raise ValueError(
                    "Currency mismatch"
                )
    
            return Money(
                self.amount + other.amount,
                self.currency
            )

* * *

# OrderItem Entity
    
    
    class OrderItem:
    
    
        def __init__(
            self,
            item_id,
            product_id,
            price,
            quantity
        ):
    
            self.id = item_id
            self.product_id = product_id
            self.price = price
            self.quantity = quantity
    
    
        def change_quantity(
            self,
            quantity
        ):
    
            if quantity <= 0:
                raise ValueError(
                    "Invalid quantity"
                )
    
            self.quantity = quantity
    
    
        def subtotal(self):
    
            return Money(
                self.price.amount *
                self.quantity,
                self.price.currency
            )

* * *

# Order Aggregate Root
    
    
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
                    "Order locked"
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
    
    
    
        def total(self):
    
            result = Money(0)
    
            for item in self.items:
                result = result.add(
                    item.subtotal()
                )
    
            return result

* * *

# Sử dụng
    
    
    order = Order(1)
    
    
    item = OrderItem(
        1,
        100,
        Money(50000),
        2
    )
    
    
    order.add_item(item)
    
    
    order.pay()
    
    
    print(
        order.total()
    )

* * *

# 9\. Những thứ bị cấm

Trong DDD:

## Cấm truy cập Entity con trực tiếp

Sai:
    
    
    order.items[0].quantity = 10

* * *

Đúng:
    
    
    order.change_quantity(
        item_id=1,
        quantity=10
    )

* * *

## Cấm thay đổi trạng thái Root trực tiếp

Sai:
    
    
    order.status = "PAID"

* * *

Đúng:
    
    
    order.pay()

* * *

# 10\. Aggregate Root trong App Cào Truyện

Bây giờ áp dụng vào hệ thống của bạn.

* * *

## Novel Aggregate

Có:
    
    
    Novel
    
     |
     +-- NovelId
    
     |
     +-- Title
    
     |
     +-- Status

Root:
    
    
    Novel

* * *

Behavior:
    
    
    novel.publish()
    
    novel.rename()
    
    novel.archive()

* * *

Không:
    
    
    novel.status = "published"

* * *

# 11\. Chapter có nên nằm trong Novel Aggregate?

Đây là câu hỏi thiết kế quan trọng.

Sai:
    
    
    Novel
    
     |
     +-- Chapter 1
    
     |
     +-- Chapter 2
    
     |
     +-- Chapter 3000

* * *

Vì:

  * Một truyện có hàng nghìn chapter. 
  * Load quá lớn. 
  * Transaction quá lớn. 



* * *

Thiết kế tốt hơn:
    
    
    Novel Aggregate
    
    
    Novel
     |
     +-- NovelId
     +-- Title
     +-- Status
    
    
    
    Chapter Aggregate
    
    
    Chapter
     |
     +-- ChapterId
     +-- NovelId
     +-- Content

* * *

Novel giữ:
    
    
    chapter_ids

hoặc chỉ biết:
    
    
    novel_id

* * *

# 12\. ReadingProgress Aggregate

Một thiết kế hợp lý:
    
    
    ReadingProgress Aggregate
    
    
    ReadingProgress (Root)
    
     |
     +-- ReaderId
    
     |
     +-- NovelId
    
     |
     +-- ChapterId
    
     |
     +-- Position

* * *

Behavior:
    
    
    progress.read_to(
        chapter_id
    )

Không:
    
    
    progress.chapter_id = 100

* * *

# 13\. Aggregate Root và Repository

DDD:

Repository chỉ làm việc với Root.

Ví dụ:
    
    
    class OrderRepository:
    
        def save(
            self,
            order: Order
        ):
            pass

* * *

Không:
    
    
    class OrderItemRepository:
        pass

* * *

Vì:

OrderItem không có đời sống độc lập.

* * *

# 14\. Aggregate Root và Database Transaction

Ví dụ:
    
    
    order.pay()
    
    repository.save(order)

Transaction:
    
    
    BEGIN
    
    update order
    
    update order_items
    
    COMMIT

* * *

Toàn bộ Aggregate được lưu cùng nhau.

* * *

# 15\. Aggregate Root và Event

Root thường phát sinh Domain Event.

Ví dụ:
    
    
    class Order:
    
    
        def pay(self):
    
            self.status = (
                OrderStatus.PAID
            )
    
            self.events.append(
                OrderPaid(
                    self.id
                )
            )

* * *

Sau đó:
    
    
    OrderPaid Event
    
           |
           |
           +---- Inventory
    
           +---- Email
    
           +---- Statistics

* * *

# 16\. Quy tắc chọn Aggregate Root

Hỏi:

## Ai có lifecycle?

Ví dụ:

Order:
    
    
    Created
    Paid
    Cancelled
    Completed

=> Root

* * *

## Ai chịu trách nhiệm luật?

Ví dụ:

"Không được thêm item sau thanh toán"

Ai kiểm soát?

=> Order

* * *

## Entity nào tồn tại độc lập?

Ví dụ:

OrderItem:

Không.

=> Entity con

* * *

# 17\. Sai lầm phổ biến

## Sai lầm 1

Mọi Entity đều là Root.

Ví dụ:
    
    
    Order
    OrderItem
    Money
    Address

đều Repository.

Sai.

* * *

## Sai lầm 2

Aggregate quá lớn.

Ví dụ:
    
    
    User
    
     |
     +-- Orders
    
     |
     +-- Payments
    
     |
     +-- Reading History
    
     |
     +-- Notifications

* * *

## Sai lầm 3

Root chỉ là CRUD.

Ví dụ:
    
    
    order.update()

Không có business behavior.

* * *

# 18\. Thiết kế cuối cùng cho App Cào Truyện

Một phiên bản hợp lý:
    
    
    Source Aggregate
    
    Source
     |
     +-- Url
     +-- PluginInfo
    
    
    
    Novel Aggregate
    
    Novel
     |
     +-- NovelId
     +-- Title
     +-- Status
    
    
    
    Chapter Aggregate
    
    Chapter
     |
     +-- ChapterId
     +-- ChapterNumber
     +-- Content
    
    
    
    Reader Aggregate
    
    Reader
     |
     +-- Email
     +-- Preferences
    
    
    
    ReadingProgress Aggregate
    
    ReadingProgress
     |
     +-- ReaderId
     +-- NovelId
     +-- ChapterId

Mỗi cái có:

  * Root riêng. 
  * Repository riêng. 
  * Business rule riêng. 



* * *

# Bài tập

## Bài 1

Thiết kế Aggregate Root cho:

### Blog

Có:

  * Blog 
  * Post 
  * Comment 
  * Like 



Xác định:

  * Root 
  * Entity con 
  * Value Object 



* * *

## Bài 2

Với App Cào Truyện:

Hãy trả lời:

  1. Novel có nên chứa Chapter không? 
  2. Bookmark có nên nằm trong Reader Aggregate không? 
  3. ReadingHistory nên là Entity hay Aggregate Root? 



* * *

## Bài 3

Viết Python:

Thiết kế:
    
    
    Library

với rule:

  * Không thể thêm truyện trùng ID. 
  * Không thể xóa truyện đang đọc. 
  * Chỉ Library được phép sửa danh sách truyện. 



* * *

# Tổng kết Buổi 9

Cần nhớ:

  * Aggregate Root là cửa duy nhất vào Aggregate. 
  * Root chịu trách nhiệm bảo vệ Invariant. 
  * Entity con không có Repository riêng. 
  * Bên ngoài không sửa trực tiếp Entity bên trong. 
  * Aggregate Root thường là nơi phát sinh Domain Event. 
  * Một Aggregate tốt phải nhỏ và có ranh giới rõ. 



* * *

Ở **Buổi 10** , chúng ta sẽ học **Repository trong DDD** :

  * Repository khác DAO như thế nào? 
  * Vì sao Repository chỉ làm việc với Aggregate Root? 
  * Thiết kế Repository Interface trong Domain. 
  * Repository Implementation ở Infrastructure. 
  * Ví dụ hoàn chỉnh với Python + SQLite cho App Cào Truyện.

