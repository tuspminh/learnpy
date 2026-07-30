# Domain-Driven Design Deep Dive

# Buổi 13: Factory Pattern trong DDD — Tạo Domain Object đúng cách

Sau buổi 12 chúng ta đã học:

  * Domain Event 
  * Event Bus 
  * Event-driven architecture 



Bây giờ quay lại một vấn đề nền tảng:

> Làm sao tạo một Aggregate phức tạp mà vẫn đảm bảo Business Rule?

Câu trả lời:

# Factory trong DDD

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

✅ Buổi 9: Aggregate Root

✅ Buổi 10: Repository

✅ Buổi 11: Domain Service

✅ Buổi 12: Domain Event

✅ **Buổi 13: Factory Pattern trong DDD**

⬜ Buổi 14: Specification Pattern

⬜ Buổi 15: CQRS trong DDD

* * *

# 1\. Vấn đề với constructor thông thường

Ví dụ:
    
    
    order = Order(
        id=1,
        customer_id=100,
        items=[],
        status="created",
        payment=None
    )

Nhìn đơn giản.

Nhưng trong thực tế:

Một Order có thể cần:

  * OrderId 
  * CustomerId 
  * Address 
  * Currency 
  * Initial Status 
  * Discount 
  * Event list 



* * *

Constructor sẽ thành:
    
    
    class Order:
    
        def __init__(
            self,
            order_id,
            customer_id,
            address,
            currency,
            discount,
            status,
            created_at,
            items,
            events
        ):
            ...

Rất khó đọc.

* * *

# 2\. Factory là gì?

Định nghĩa DDD:

> Factory là một object hoặc method chịu trách nhiệm tạo ra Domain Object phức tạp và đảm bảo nó ở trạng thái hợp lệ.

* * *

Nói đơn giản:

Factory là:

> Nhà máy sản xuất Aggregate.

* * *

Ví dụ:

Không:
    
    
    Order(...)

Mà:
    
    
    OrderFactory.create()

* * *

# 3\. Factory bảo vệ Invariant

Nhắc lại:

Invariant:

> Luật luôn phải đúng.

Ví dụ:

Một Order mới tạo:

Phải:
    
    
    status = CREATED
    items không null
    created_at có giá trị

* * *

Sai:
    
    
    order = Order(
        id=1,
        status="PAID"
    )

Một Order mới không thể tự nhiên đã thanh toán.

* * *

Factory kiểm soát:
    
    
    order = OrderFactory.create(
        customer_id=10
    )

Kết quả:
    
    
    status = CREATED

* * *

# 4\. Khi nào cần Factory?

Không phải lúc nào cũng dùng Factory.

Dùng khi:

* * *

## 1\. Object tạo phức tạp

Ví dụ:
    
    
    Order
    
     |
     + Customer
    
     |
     + Address
    
     |
     + Money
    
     |
     + Discount

* * *

## 2\. Có Business Rule khi tạo

Ví dụ:
    
    
    Không được tạo User không có email

* * *

## 3\. Cần che giấu quá trình khởi tạo

Ví dụ:
    
    
    CrawlerPluginFactory.create(
        "truyenfull"
    )

Người dùng không cần biết:
    
    
    TruyenFullParser()
    HttpClient()
    RateLimiter()

* * *

# 5\. Factory Method vs Factory Object

DDD thường dùng hai dạng.

* * *

# Dạng 1: Factory Method

Một method tạo object.

Ví dụ:
    
    
    class Order:
    
        @classmethod
        def create(
            cls,
            customer_id
        ):
            return cls(
                customer_id
            )

* * *

Sử dụng:
    
    
    order = Order.create(10)

* * *

# Dạng 2: Factory Object

Một class riêng.

Ví dụ:
    
    
    class OrderFactory:
    
        def create(
            self,
            customer_id
        ):
            return Order(...)

* * *

Dùng khi:

  * Logic tạo phức tạp. 
  * Có dependency. 
  * Có nhiều loại object. 



* * *

# 6\. Ví dụ Order Factory

## Entity
    
    
    from enum import Enum
    
    
    class OrderStatus(Enum):
    
        CREATED = "created"
        PAID = "paid"
    
    
    
    class Order:
    
        def __init__(
            self,
            order_id,
            customer_id
        ):
    
            self.id = order_id
            self.customer_id = customer_id
            self.status = (
                OrderStatus.CREATED
            )
            self.items = []

* * *

Nếu tạo trực tiếp:
    
    
    order = Order(
        1,
        100
    )

OK.

Nhưng ai tạo ID?

Ai tạo timestamp?

Ai validate?

* * *

# 7\. OrderFactory
    
    
    import uuid
    
    
    class OrderFactory:
    
    
        def create(
            self,
            customer_id
        ):
    
            order_id = str(
                uuid.uuid4()
            )
    
    
            order = Order(
                order_id,
                customer_id
            )
    
    
            return order

* * *

Sử dụng:
    
    
    factory = OrderFactory()
    
    
    order = factory.create(
        customer_id=100
    )

* * *

# 8\. Factory và Value Object

Ví dụ Money:
    
    
    from dataclasses import dataclass
    
    
    @dataclass(frozen=True)
    class Money:
    
        amount: int
        currency: str

* * *

Không muốn:
    
    
    Money(
        -100,
        "VND"
    )

* * *

Tạo Factory:
    
    
    class MoneyFactory:
    
    
        def create(
            self,
            amount
        ):
    
            if amount < 0:
                raise ValueError(
                    "Invalid money"
                )
    
    
            return Money(
                amount,
                "VND"
            )

* * *

# 9\. Factory trong App Cào Truyện

Đây là phần rất phù hợp với dự án của bạn.

Hệ thống có:
    
    
    Crawler Plugin
    Parser
    HTTP Client
    Database
    Scheduler

* * *

Không nên:
    
    
    plugin = TruyenFullPlugin(
        HttpClient(),
        Parser(),
        Database(),
        Config()
    )

* * *

Quá nhiều dependency.

* * *

Dùng:
    
    
    plugin = CrawlerPluginFactory.create(
        "truyenfull"
    )

* * *

# 10\. Crawler Plugin Factory

Ví dụ:
    
    
    class CrawlerPluginFactory:
    
    
        def create(
            self,
            source_name
        ):
    
            if source_name == "truyenfull":
    
                return TruyenFullPlugin(
                    HttpClient(),
                    TruyenFullParser()
                )
    
    
            raise ValueError(
                "Unknown source"
            )

* * *

Sử dụng:
    
    
    factory = CrawlerPluginFactory()
    
    
    crawler = factory.create(
        "truyenfull"
    )
    
    
    crawler.crawl()

* * *

Bên ngoài không biết:
    
    
    HttpClient
    Parser
    Configuration

* * *

# 11\. Factory tạo Aggregate

Một ví dụ quan trọng.

App truyện:

Một Novel mới cần:

  * NovelId 
  * Title 
  * Status 
  * CreatedAt 
  * SourceId 



* * *

Không:
    
    
    Novel(
        None,
        "",
        None,
        None
    )

* * *

Factory:
    
    
    class NovelFactory:
    
    
        def create(
            self,
            title,
            source_id
        ):
    
            if not title:
                raise ValueError(
                    "Title required"
                )
    
    
            return Novel(
                id=generate_id(),
                title=title,
                source_id=source_id,
                status="draft"
            )

* * *

# 12\. Factory và Repository

Một câu hỏi:

> Repository có tạo object không?

Câu trả lời:

Có thể.

Nhưng:

  * Factory tạo mới. 
  * Repository tái tạo từ database. 



* * *

Ví dụ:

Tạo mới:
    
    
    Factory
    
        |
        v
    
    Novel

* * *

Load:
    
    
    Database
    
        |
        v
    
    Repository
    
        |
        v
    
    Novel

* * *

# 13\. Factory và ORM

Một lỗi phổ biến:

Dùng ORM model làm Domain Entity.

Ví dụ:
    
    
    class NovelModel(SQLAlchemy):
    
        title = Column()

Sau đó:
    
    
    NovelModel(...)

đây không phải Domain Factory.

* * *

Kiến trúc tốt:
    
    
    Database Model
    
           |
    
    Mapper
    
           |
    
    Domain Entity

* * *

# 14\. Factory trong Clean Architecture

Cấu trúc:
    
    
    domain/
    
        novels/
    
            entities/
    
                novel.py
    
            factories/
    
                novel_factory.py
    
    
    application/
    
        use_cases/
    
    
    infrastructure/
    
        database/

* * *

Factory thuộc:
    
    
    Domain Layer

vì nó hiểu:

  * Business Rule 
  * Domain Object 



* * *

# 15\. Factory vs Builder

Hay bị nhầm.

* * *

## Factory

Mục tiêu:

"Tạo object hợp lệ"

Ví dụ:
    
    
    NovelFactory.create()

* * *

## Builder

Mục tiêu:

"Tạo object nhiều bước"

Ví dụ:
    
    
    OrderBuilder()
    
        .add_item()
    
        .set_address()
    
        .set_discount()
    
        .build()

* * *

Factory:
    
    
    Create

Builder:
    
    
    Assemble

* * *

# 16\. Abstract Factory trong DDD

Ví dụ:

Crawler có nhiều nguồn:
    
    
    TruyenFull
    
    TruyenCV
    
    NovelToon

* * *

Interface:
    
    
    class CrawlerFactory:
    
        def create():
            pass

* * *

Implementation:
    
    
    class VietnameseCrawlerFactory:
    
    
        def create(
            self,
            name
        ):
    
            ...

* * *

# 17\. Factory và Dependency Injection

Không nên:
    
    
    class OrderFactory:
    
        def create():
    
            repo = SQLite()

Factory không tự tạo Infrastructure.

* * *

Đúng:
    
    
    class OrderFactory:
    
    
        def __init__(
            self,
            id_generator
        ):
            self.id_generator = id_generator

* * *

Test dễ:
    
    
    factory = OrderFactory(
        FakeIdGenerator()
    )

* * *

# 18\. Ví dụ hoàn chỉnh: Novel Factory

## Entity
    
    
    class Novel:
    
    
        def __init__(
            self,
            novel_id,
            title,
            source_id
        ):
    
            self.id = novel_id
            self.title = title
            self.source_id = source_id
            self.status = "draft"
    
    
    
        def publish(self):
    
            self.status = "published"

* * *

## Factory
    
    
    import uuid
    
    
    class NovelFactory:
    
    
        def create(
            self,
            title,
            source_id
        ):
    
            if len(title) < 3:
                raise ValueError(
                    "Invalid title"
                )
    
    
            return Novel(
                str(uuid.uuid4()),
                title,
                source_id
            )

* * *

## Use Case
    
    
    class ImportNovelUseCase:
    
    
        def __init__(
            self,
            factory,
            repository
        ):
    
            self.factory = factory
            self.repository = repository
    
    
    
        def execute(
            self,
            title,
            source_id
        ):
    
            novel = self.factory.create(
                title,
                source_id
            )
    
    
            self.repository.save(
                novel
            )

* * *

# 19\. Những lỗi thường gặp

## Lỗi 1

Dùng Factory cho mọi thứ.

Không cần:
    
    
    UserFactory.create()

nếu:
    
    
    User(name,email)

đã đơn giản.

* * *

## Lỗi 2

Factory chứa business process.

Sai:
    
    
    OrderFactory.pay_order()

Payment là behavior.

Không phải creation.

* * *

## Lỗi 3

Factory gọi database.

Sai:
    
    
    Factory.create_from_database()

Đó là Repository.

* * *

## Lỗi 4

Factory trả về Dictionary.

Sai:
    
    
    {
    "title":"abc"
    }

Đúng:
    
    
    Novel(...)

* * *

# 20\. Kiến trúc DDD hiện tại

Sau 13 buổi:
    
    
    Domain Layer
    
    ├── Entity
    │
    ├── Value Object
    │
    ├── Aggregate
    │
    ├── Aggregate Root
    │
    ├── Repository Interface
    │
    ├── Domain Service
    │
    ├── Domain Event
    │
    └── Factory

* * *

# Bài tập

## Bài 1

Thiết kế:
    
    
    UserFactory

Rule:

  * Email bắt buộc. 
  * Username tối thiểu 3 ký tự. 
  * User mới có status ACTIVE. 



* * *

## Bài 2

Trong App Cào Truyện tạo:
    
    
    NovelFactory

Yêu cầu:

Input:
    
    
    title
    source_id

Output:
    
    
    Novel Aggregate

* * *

## Bài 3

Thiết kế:
    
    
    CrawlerPluginFactory

Hỗ trợ:
    
    
    truyenfull
    
    truyenyy
    
    noveltoon

* * *

# Tổng kết Buổi 13

Cần nhớ:

  * Factory tạo Domain Object hợp lệ. 
  * Factory bảo vệ invariant lúc khởi tạo. 
  * Factory thuộc Domain Layer. 
  * Factory khác Repository. 
  * Repository lấy object đã tồn tại. 
  * Factory tạo object mới. 
  * Factory rất hữu ích với Aggregate phức tạp và Plugin Architecture. 



* * *

Buổi tiếp theo (**Buổi 14**) chúng ta sẽ học:

# Specification Pattern trong DDD

Nội dung:

  * Business Rule dạng Specification. 
  * Composite Specification (AND / OR / NOT). 
  * Thay thế if-else khổng lồ. 
  * Ví dụ: 
    * User đủ điều kiện VIP. 
    * Novel được phép crawl. 
    * Chapter hợp lệ để publish. 
    * Filter truyện trong App Cào Truyện.

