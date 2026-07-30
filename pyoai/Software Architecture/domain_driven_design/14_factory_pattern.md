# Domain-Driven Design Deep Dive

# Buổi 14: Factory Pattern trong DDD

Sau buổi 13, chúng ta đã học:

  * Domain Event 
  * Aggregate phát sinh Event 
  * Event Bus 
  * Event Handler 
  * Event-driven Architecture 



Hôm nay chúng ta quay lại một vấn đề rất quan trọng trong việc xây dựng Domain Model:

> Làm sao tạo một Domain Object phức tạp mà luôn ở trạng thái hợp lệ?

Câu trả lời:

# Factory Pattern trong DDD

* * *

# 1\. Vấn đề của việc tạo Object trực tiếp

Ví dụ đơn giản:
    
    
    novel = Novel(
        id="123",
        title="Đấu Phá Thương Khung",
        status="draft"
    )

Có vẻ ổn.

Nhưng hệ thống lớn hơn:

Một Novel cần:

  * NovelId 
  * Title 
  * Source 
  * Author 
  * Category 
  * CreatedAt 
  * Initial Status 
  * Domain Event 



Constructor sẽ thành:
    
    
    class Novel:
    
        def __init__(
            self,
            novel_id,
            title,
            source_id,
            author,
            category,
            created_at,
            status,
            events
        ):
            ...

* * *

Vấn đề:

## 1\. Khó đọc
    
    
    Novel(
        "abc",
        "xxx",
        10,
        "author",
        "fantasy",
        datetime.now(),
        "draft",
        []
    )

Không biết tham số nào là gì.

* * *

## 2\. Dễ tạo object sai

Ví dụ:
    
    
    novel = Novel(
        id="123",
        title="ABC",
        status="published"
    )

Một truyện mới tạo lại đã publish.

* * *

## 3\. Logic tạo bị rải rác

Nơi này:
    
    
    Novel(...)

Nơi kia:
    
    
    Novel(...)

Mỗi nơi tạo một kiểu.

* * *

DDD giải quyết:
    
    
    Factory
    
        |
        v
    
    Domain Object hợp lệ

* * *

# 2\. Factory trong DDD là gì?

Định nghĩa:

> Factory là một đối tượng chịu trách nhiệm tạo Entity, Aggregate hoặc Value Object phức tạp.

Factory không chỉ là "hàm tạo object".

Nó đảm bảo:

  * Validation ban đầu. 
  * Tạo Identity. 
  * Thiết lập trạng thái mặc định. 
  * Tạo các object con. 
  * Bảo vệ invariant. 



* * *

# 3\. Factory thuộc Layer nào?

Factory thuộc:
    
    
    Domain Layer

Vì nó hiểu:

  * Business Rule. 
  * Domain Object. 



Cấu trúc:
    
    
    domain/
    
        novels/
    
            entities/
                novel.py
    
            factories/
                novel_factory.py

* * *

# 4\. Factory Method vs Factory Object

DDD thường dùng hai kiểu.

* * *

# Kiểu 1: Factory Method

Factory nằm trong chính Entity.

Ví dụ:
    
    
    class Novel:
    
        @classmethod
        def create(
            cls,
            title
        ):
    
            return cls(
                id=generate_id(),
                title=title
            )

Sử dụng:
    
    
    novel = Novel.create(
        "Truyện ABC"
    )

* * *

Ưu điểm:

  * Đơn giản. 
  * Ít class hơn. 



Nhược điểm:

  * Khi logic phức tạp sẽ phình to. 



* * *

# Kiểu 2: Factory Object

Tách riêng:
    
    
    class NovelFactory:
    
        def create(
            self,
            title
        ):
            ...

Sử dụng:
    
    
    factory = NovelFactory()
    
    novel = factory.create(
        "Truyện ABC"
    )

* * *

Ưu điểm:

  * Dễ mở rộng. 
  * Dễ test. 
  * Có thể inject dependency. 



* * *

# 5\. Factory bảo vệ Invariant

Nhắc lại:

Invariant:

> Điều kiện luôn phải đúng trong suốt vòng đời Aggregate.

Ví dụ:

Novel:

  * Không có title rỗng. 
  * Status ban đầu phải là draft. 
  * Phải có Source. 



* * *

Không dùng Factory:
    
    
    novel = Novel(
        title=""
    )

Có thể xảy ra.

* * *

Dùng Factory:
    
    
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

# 6\. Ví dụ hoàn chỉnh: Novel Aggregate

## Entity
    
    
    from datetime import datetime
    
    
    class Novel:
    
    
        def __init__(
            self,
            novel_id,
            title,
            source_id,
            created_at,
            status
        ):
    
            self.id = novel_id
            self.title = title
            self.source_id = source_id
            self.created_at = created_at
            self.status = status
    
    
        def publish(self):
    
            if self.status == "published":
    
                raise Exception(
                    "Already published"
                )
    
    
            self.status = "published"

* * *

## Factory
    
    
    import uuid
    from datetime import datetime
    
    
    class NovelFactory:
    
    
        def create(
            self,
            title,
            source_id
        ):
    
            if len(title) < 3:
                raise ValueError(
                    "Title too short"
                )
    
    
            return Novel(
                novel_id=str(
                    uuid.uuid4()
                ),
    
                title=title,
    
                source_id=source_id,
    
                created_at=datetime.now(),
    
                status="draft"
            )

* * *

Sử dụng:
    
    
    factory = NovelFactory()
    
    
    novel = factory.create(
        "Đấu Phá Thương Khung",
        100
    )

* * *

Kết quả:
    
    
    novel.status
    
    # draft

* * *

# 7\. Factory và Aggregate

Một Aggregate phức tạp:
    
    
    Novel Aggregate
    
    
    Novel
    
     |
     + Chapter
    
     |
     + Author
    
     |
     + Category

* * *

Không nên:
    
    
    Novel(
        Chapter(),
        Chapter(),
        Author(),
        Category()
    )

* * *

Factory:
    
    
    class NovelFactory:
    
    
        def create(
            self,
            data
        ):
    
            author = Author.create(
                data.author
            )
    
    
            chapters = []
    
            for item in data.chapters:
    
                chapters.append(
                    Chapter.create(item)
                )
    
    
            return Novel(
                author,
                chapters
            )

* * *

Factory hiểu cách lắp ráp Aggregate.

* * *

# 8\. Factory và Value Object

Ví dụ:

Money:
    
    
    from dataclasses import dataclass
    
    
    @dataclass(frozen=True)
    class Money:
    
        amount: int
        currency: str

* * *

Không muốn:
    
    
    Money(
        -10000,
        "VND"
    )

* * *

Factory:
    
    
    class MoneyFactory:
    
    
        def create(
            self,
            amount
        ):
    
            if amount < 0:
    
                raise ValueError(
                    "Invalid amount"
                )
    
    
            return Money(
                amount,
                "VND"
            )

* * *

# 9\. Factory trong App Cào Truyện

Đây là phần quan trọng.

Hệ thống crawler của bạn:
    
    
    Crawler System
    
    
    Source
    
     |
     + TruyenFull
    
     |
     + TruyenYY
    
     |
     + NovelToon

* * *

Không nên:
    
    
    plugin = TruyenFullPlugin(
        HttpClient(),
        Parser(),
        Config(),
        Database()
    )

* * *

Vì:

  * UI biết implementation. 
  * Khó thêm source mới. 



* * *

Dùng Factory:
    
    
    plugin = CrawlerPluginFactory.create(
        "truyenfull"
    )

* * *

# 10\. CrawlerPluginFactory

Ví dụ:
    
    
    class CrawlerPluginFactory:
    
    
        def create(
            self,
            source_name
        ):
    
            if source_name == "truyenfull":
    
                return TruyenFullPlugin()
    
    
            if source_name == "truyenyy":
    
                return TruyenYYPlugin()
    
    
            raise ValueError(
                "Unknown source"
            )

* * *

Sử dụng:
    
    
    crawler = factory.create(
        "truyenfull"
    )
    
    crawler.crawl()

* * *

Bên ngoài không biết:
    
    
    Parser nào?
    HTTP Client nào?
    Config nào?

* * *

# 11\. Factory + Dependency Injection

Factory tốt không tự tạo dependency.

Ví dụ xấu:
    
    
    class NovelFactory:
    
    
        def create():
    
            database = SQLite()

* * *

Vì Domain biết Infrastructure.

* * *

Đúng:
    
    
    class NovelFactory:
    
    
        def __init__(
            self,
            id_generator,
            clock
        ):
    
            self.id_generator = id_generator
            self.clock = clock

* * *

Test:
    
    
    factory = NovelFactory(
        FakeIdGenerator(),
        FakeClock()
    )

* * *

# 12\. Factory và Repository khác nhau

Rất nhiều người nhầm.

* * *

## Factory

Tạo object mới:
    
    
    Input
    
        |
        v
    
    Factory
    
        |
        v
    
    New Aggregate

* * *

## Repository

Lấy object đã tồn tại:
    
    
    Database
    
        |
        v
    
    Repository
    
        |
        v
    
    Existing Aggregate

* * *

Ví dụ:

Tạo truyện:
    
    
    novel = factory.create(
        title
    )

Load truyện:
    
    
    novel = repository.get_by_id(
        id
    )

* * *

# 13\. Factory và Domain Event

Factory có thể tạo Event.

Ví dụ:

Khi tạo Novel:
    
    
    class NovelFactory:
    
    
        def create(
            self,
            title
        ):
    
            novel = Novel(...)
    
    
            novel.add_event(
                NovelCreated(
                    novel.id
                )
            )
    
    
            return novel

* * *

Luồng:
    
    
    Factory
    
      |
      v
    
    Novel
    
      |
      v
    
    NovelCreated Event

* * *

# 14\. Factory trong Clean Architecture

Cấu trúc:
    
    
    src/
    
    domain/
    
        novels/
    
            entities/
                novel.py
    
            factories/
                novel_factory.py
    
    
    application/
    
        use_cases/
    
            create_novel.py
    
    
    infrastructure/
    
        repositories/

* * *

Use Case:
    
    
    class CreateNovelUseCase:
    
    
        def execute(
            self,
            title
        ):
    
            novel = factory.create(
                title
            )
    
    
            repository.save(
                novel
            )

* * *

# 15\. Khi nào KHÔNG cần Factory?

Không phải object nào cũng cần Factory.

Không cần:
    
    
    UserName("abc")

nếu đơn giản.

* * *

Cần Factory khi:

✅ Aggregate phức tạp.  
✅ Nhiều rule khi tạo.  
✅ Nhiều dependency.  
✅ Muốn che giấu quá trình tạo.  
✅ Có nhiều loại implementation.

* * *

# 16\. Những lỗi thường gặp

## Lỗi 1: Factory chứa business process

Sai:
    
    
    class OrderFactory:
    
        def pay_order():
            ...

Thanh toán không phải tạo object.

* * *

Đúng:
    
    
    OrderFactory.create()
    
    Order.pay()

* * *

## Lỗi 2: Factory gọi Database

Sai:
    
    
    Factory.create_from_database()

Đó là Repository.

* * *

## Lỗi 3: Factory trả Dictionary

Sai:
    
    
    {
    "title":"ABC"
    }

Đúng:
    
    
    Novel(...)

* * *

# 17\. Kiến trúc sau Buổi 14

Hiện tại Domain của chúng ta:
    
    
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
  * Username >= 3 ký tự. 
  * Status mặc định ACTIVE. 



* * *

## Bài 2

Viết:
    
    
    NovelFactory

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

# Tổng kết Buổi 14

Cần nhớ:

✅ Factory tạo Domain Object hợp lệ.  
✅ Factory thuộc Domain Layer.  
✅ Factory bảo vệ invariant lúc khởi tạo.  
✅ Factory khác Repository.  
✅ Factory rất hữu ích cho Aggregate phức tạp.  
✅ Factory kết hợp tốt với Dependency Injection.  
✅ Plugin Architecture + Factory là một cặp thiết kế rất mạnh.

* * *

Buổi tiếp theo theo roadmap:

# Buổi 15: Specification Pattern trong DDD

Nội dung:

  * Business Rule dưới dạng Object. 
  * Thay thế hàng loạt `if/else`. 
  * Composite Specification. 
  * AND / OR / NOT. 
  * Áp dụng: 
    * User đủ điều kiện VIP. 
    * Novel được phép publish. 
    * Source được phép crawl. 
    * Chapter hợp lệ để import.

