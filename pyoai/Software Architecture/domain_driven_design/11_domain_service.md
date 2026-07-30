# Domain-Driven Design Deep Dive

# Buổi 11: Domain Service — Khi nghiệp vụ không thuộc về một Entity nào

Sau buổi 10, chúng ta đã có:

  * Entity 
  * Value Object 
  * Aggregate 
  * Aggregate Root 
  * Repository 



Bây giờ xuất hiện một vấn đề:

> Có những business rule không tự nhiên thuộc về một Entity nào cả. Chúng ta đặt nó ở đâu?

Câu trả lời:

# Domain Service

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

✅ **Buổi 11: Domain Service**

⬜ Buổi 12: Domain Event

⬜ Buổi 13: Factory

⬜ Buổi 14: Specification Pattern

* * *

# 1\. Vấn đề: Không phải logic nào cũng thuộc Entity

Một nguyên tắc DDD:

> Behavior nên đặt gần dữ liệu mà nó tác động.

Ví dụ:
    
    
    class Order:
    
        def pay(self):
            ...

Rất hợp lý.

Vì:

  * Order có trạng thái. 
  * Order biết khi nào được thanh toán. 



* * *

Nhưng có những trường hợp khác.

Ví dụ:

"Tính giá cuối cùng của đơn hàng"

Cần:

  * Product 
  * Customer 
  * Promotion 
  * Membership 
  * Coupon 



Ai chịu trách nhiệm?
    
    
    Order?
    Product?
    Customer?
    Coupon?

Không có Entity nào thực sự sở hữu logic này.

* * *

# 2\. Domain Service là gì?

Định nghĩa:

> Domain Service là một object chứa nghiệp vụ quan trọng nhưng không thuộc tự nhiên về một Entity hoặc Value Object cụ thể.

* * *

Ví dụ:
    
    
    PricingService
    
    PaymentService
    
    RecommendationService
    
    ShippingCalculator
    
    ExchangeRateService

* * *

# 3\. Domain Service khác Application Service

Đây là điểm rất quan trọng.

Nhiều người nhầm:
    
    
    Service = Service

Nhưng DDD phân biệt.

* * *

## Application Service

Nhiệm vụ:

  * Điều phối use case. 
  * Gọi Repository. 
  * Gọi Domain Model. 



Ví dụ:
    
    
    class CreateOrderUseCase:
    
        def execute(self):
    
            order = Order()
    
            repository.save(order)

* * *

Application Service không chứa business rule.

* * *

## Domain Service

Nhiệm vụ:

  * Chứa business rule. 



Ví dụ:
    
    
    class PriceCalculator:
    
        def calculate(self, order):
            ...

* * *

# 4\. Ví dụ: Chuyển tiền ngân hàng

Có:
    
    
    Account A
    
    Account B

* * *

Ta muốn:
    
    
    A chuyển 1.000.000đ cho B

Logic này thuộc Account nào?

Không hợp lý:
    
    
    account_a.transfer(account_b)

Vì:

Account A không nên biết mọi logic giao dịch.

* * *

Tạo:
    
    
    TransferService

* * *
    
    
    class TransferService:
    
    
        def transfer(
            self,
            source,
            target,
            amount
        ):
    
            source.withdraw(amount)
    
            target.deposit(amount)

* * *

Đây là Domain Service.

* * *

# 5\. Đặc điểm của Domain Service

Một Domain Service tốt:

## 1\. Có tên theo nghiệp vụ

Sai:
    
    
    HelperService
    CommonService
    Utils

* * *

Đúng:
    
    
    PaymentAuthorizationService
    
    PricingService
    
    RecommendationService

* * *

Tên phải thuộc Ubiquitous Language.

* * *

## 2\. Không có state

Domain Service thường stateless.

Ví dụ:
    
    
    class DiscountCalculator:
    
        def calculate():
            ...

Không:
    
    
    class DiscountCalculator:
    
        self.current_discount

* * *

## 3\. Làm việc với Domain Object

Không:
    
    
    calculate(dict)

* * *

Đúng:
    
    
    calculate(Order)

* * *

# 6\. Ví dụ: Pricing Service

Hệ thống bán hàng:

Rule:

  * Khách VIP giảm 10% 
  * Đơn trên 1 triệu giảm thêm 5% 



* * *

Sai:

Đặt vào Product:
    
    
    product.calculate_price()

Vì Product không biết:

  * Customer 
  * Order 



* * *

Sai:

Đặt vào Customer:
    
    
    customer.calculate_order_price()

Customer không sở hữu Order.

* * *

Đúng:
    
    
    PricingService

* * *

Code:
    
    
    class PricingService:
    
    
        def calculate(
            self,
            order,
            customer
        ):
    
            total = order.total()
    
    
            if customer.is_vip:
    
                total = total * 0.9
    
    
            return total

* * *

# 7\. Domain Service trong App Cào Truyện

Bây giờ áp dụng vào dự án của bạn.

* * *

## Trường hợp 1: Recommendation

Bạn muốn:

"Gợi ý truyện cho người dùng"

Cần:

  * Lịch sử đọc 
  * Thể loại yêu thích 
  * Rating 
  * Trending 



* * *

Logic này thuộc:
    
    
    Reader?
    Novel?
    History?

Không.

* * *

Tạo:
    
    
    RecommendationService

* * *
    
    
    class RecommendationService:
    
    
        def recommend(
            self,
            reader,
            novels
        ):
    
            result = []
    
            for novel in novels:
    
                if (
                    novel.category
                    in reader.favorite_categories
                ):
                    result.append(novel)
    
            return result

* * *

Đây là Domain Service.

* * *

# 8\. Trường hợp 2: Chapter Merge Service

Giả sử crawler lấy chapter từ nhiều nguồn:
    
    
    Source A
    
    Chapter 1
    Chapter 2
    
    
    Source B
    
    Chapter 1
    Chapter 2

Cần:

  * So sánh nội dung. 
  * Loại duplicate. 
  * Chọn bản tốt nhất. 



* * *

Logic này không thuộc:
    
    
    Chapter
    Source
    Novel

* * *

Tạo:
    
    
    ChapterMergeService

* * *
    
    
    class ChapterMergeService:
    
    
        def merge(
            self,
            chapters
        ):
    
            unique = {}
    
            for chapter in chapters:
    
                unique[
                    chapter.number
                ] = chapter
    
            return list(
                unique.values()
            )

* * *

# 9\. Trường hợp 3: Crawler Scheduling

Hệ thống cào truyện:

Cần quyết định:

  * Khi nào crawl? 
  * Source nào ưu tiên? 
  * Crawl lại hay không? 



* * *

Không thuộc:
    
    
    Source Entity

* * *

Tạo:
    
    
    CrawlPlanningService

* * *
    
    
    class CrawlPlanningService:
    
    
        def should_crawl(
            self,
            source
        ):
    
            return (
                source.last_crawl
                >
                24
            )

* * *

# 10\. Khi nào dùng Domain Service?

Dùng khi:

## Rule liên quan nhiều Entity

Ví dụ:
    
    
    Money Exchange
    
    Payment
    
    Recommendation

* * *

## Không có Entity nào sở hữu tự nhiên

Ví dụ:
    
    
    Pricing

* * *

## Logic là một khái niệm nghiệp vụ riêng

Ví dụ:
    
    
    Fraud Detection
    
    Shipping Calculation

* * *

# 11\. Khi nào KHÔNG dùng Domain Service?

Đừng tạo:
    
    
    UserService
    OrderService
    NovelService

rồi nhét tất cả vào.

Ví dụ:

Sai:
    
    
    class NovelService:
    
        create()
    
        update()
    
        delete()
    
        publish()
    
        rename()

* * *

DDD muốn:
    
    
    Novel Entity
    
        |
        +-- rename()
    
        +-- publish()

* * *

# 12\. So sánh Entity vs Domain Service

Ví dụ:

## Order
    
    
    order.pay()

Tại sao?

Vì:

  * Order biết trạng thái. 
  * Order biết rule. 



=> Entity.

* * *

## Transfer
    
    
    transfer_service.transfer(
        account1,
        account2
    )

Vì:

  * Hai Account tham gia. 
  * Không Account nào sở hữu. 



=> Domain Service.

* * *

# 13\. Domain Service và Repository

Domain Service có thể dùng Repository không?

Thông thường:

Không nên.

Ví dụ:

Sai:
    
    
    class RecommendationService:
    
    
        def recommend(self):
    
            novels = repository.get_all()

* * *

Repository thuộc Application boundary.

* * *

Nên:

Application lấy dữ liệu:
    
    
    novels = repository.get_all()
    
    recommendation_service.recommend(
        reader,
        novels
    )

* * *

Luồng:
    
    
    Application Service
    
            |
            |
            v
    
    Repository
            |
            |
            v
    
    Domain Service

* * *

# 14\. Domain Service và Dependency Injection

Ví dụ:
    
    
    class ReadingSuggestionService:
    
    
        def __init__(
            self,
            ranking_engine
        ):
            self.engine = ranking_engine

* * *

Application:
    
    
    service = ReadingSuggestionService(
        engine
    )

* * *

Dễ test.

* * *

# 15\. Test Domain Service

Ví dụ:
    
    
    def test_discount():
    
        service = PricingService()
    
        result = service.calculate(
            order,
            vip_customer
        )
    
        assert result == 900000

* * *

Không cần:

  * Database 
  * API 
  * UI 



* * *

# 16\. Cấu trúc project

Sau buổi này:
    
    
    domain/
    
        novels/
    
            entities/
    
            value_objects/
    
            services/
    
                recommendation.py
                chapter_merge.py
    
    
        orders/
    
            entities/
    
            services/
    
                pricing.py

* * *

# 17\. Ví dụ hoàn chỉnh: Recommendation Domain Service

## Entity
    
    
    class Reader:
    
    
        def __init__(
            self,
            reader_id,
            favorite_categories
        ):
    
            self.id = reader_id
            self.favorite_categories = (
                favorite_categories
            )

* * *

## Entity Novel
    
    
    class Novel:
    
    
        def __init__(
            self,
            title,
            category
        ):
    
            self.title = title
            self.category = category

* * *

## Domain Service
    
    
    class RecommendationService:
    
    
        def recommend(
            self,
            reader,
            novels
        ):
    
            return [
                novel
                for novel in novels
                if novel.category
                in reader.favorite_categories
            ]

* * *

Sử dụng:
    
    
    reader = Reader(
        1,
        ["Fantasy"]
    )
    
    
    novels = [
        Novel(
            "Đấu Phá",
            "Fantasy"
        ),
        Novel(
            "Trinh Thám",
            "Detective"
        )
    ]
    
    
    service = RecommendationService()
    
    
    result = service.recommend(
        reader,
        novels
    )

* * *

# 18\. Domain Service trong kiến trúc tổng thể

Bây giờ hệ thống DDD:
    
    
                  Application
    
                       |
                       |
    
                  Domain Layer
    
            -----------------------
    
            Entity
    
            Value Object
    
            Aggregate
    
            Domain Service
    
            Domain Event
    
            Repository Interface
    
    
                       |
    
                 Infrastructure

* * *

# 19\. Checklist Domain Service

Một Domain Service tốt:

✅ Có tên nghiệp vụ
    
    
    PricingService

* * *

✅ Stateless

* * *

✅ Không thay thế Entity

* * *

✅ Chứa logic liên quan nhiều object

* * *

✅ Không chứa SQL/API

* * *

# Bài tập

## Bài 1

Trong App Cào Truyện, xác định cái nào là Domain Service:

  1. Đổi tên truyện. 
  2. Gợi ý truyện. 
  3. Merge chapter từ nhiều nguồn. 
  4. Lưu truyện xuống SQLite. 
  5. Tính điểm xếp hạng truyện. 



* * *

## Bài 2

Viết:
    
    
    ChapterRankingService

Rule:

  * Chapter mới hơn điểm cao hơn. 
  * Chapter nhiều lượt đọc điểm cao hơn. 



* * *

## Bài 3

Refactor:
    
    
    class NovelService:
    
        crawl()
    
        parse()
    
        save()
    
        recommend()
    
        publish()

thành kiến trúc DDD.

* * *

# Tổng kết Buổi 11

Cần nhớ:

  * Domain Service chứa nghiệp vụ không thuộc Entity nào. 
  * Không biến mọi thứ thành Service. 
  * Entity giữ behavior của chính nó. 
  * Domain Service xử lý logic liên quan nhiều Aggregate/Entity. 
  * Domain Service không biết Database. 
  * Tên Domain Service phải thuộc ngôn ngữ nghiệp vụ. 



* * *

Buổi tiếp theo (**Buổi 12**) chúng ta sẽ học **Domain Event** :

  * Event trong DDD khác Message Queue thế nào? 
  * Khi nào phát sinh Domain Event? 
  * Event giúp các Aggregate giao tiếp ra sao? 
  * Thiết kế Event Bus cho App Cào Truyện: 
    * `NovelCreated`
    * `ChapterPublished`
    * `ReadingCompleted`
    * `SourceCrawlFinished`

