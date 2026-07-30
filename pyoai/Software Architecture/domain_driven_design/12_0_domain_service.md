# Domain-Driven Design Deep Dive

# Buổi 12 (Roadmap cập nhật): Domain Service trong DDD

Sau buổi 11 chúng ta đã học:

  * Application Layer 
  * Use Case 
  * Repository 
  * Repository Interface 
  * Repository Implementation 



Bây giờ chúng ta đi vào một câu hỏi quan trọng:

> Có những nghiệp vụ không thuộc về một Entity nào. Vậy chúng ta đặt logic đó ở đâu?

Ví dụ:

  * Tính giá đơn hàng dựa trên nhiều yếu tố. 
  * Gợi ý truyện cho người đọc. 
  * Gộp chapter từ nhiều nguồn crawler. 
  * Kiểm tra mức độ tương đồng của nội dung. 



Không thể nhét tất cả vào Entity.

Giải pháp:

# Domain Service

* * *

# 1\. Domain Service là gì?

Định nghĩa DDD:

> Domain Service là một object chứa logic nghiệp vụ quan trọng nhưng không thuộc tự nhiên về một Entity hoặc Value Object nào.

Nói đơn giản:

  * Entity giữ hành vi của chính nó. 
  * Domain Service giữ nghiệp vụ liên quan nhiều đối tượng. 



* * *

Ví dụ:
    
    
    Novel
    
        rename()
        publish()
    
    
    PricingService
    
        calculate_price()

* * *

# 2\. Vị trí của Domain Service trong kiến trúc
    
    
                  Presentation
    
                       |
                       v
    
                 Application Layer
    
                  Use Case
    
                       |
                       v
    
                 Domain Layer
    
        +-----------------------------+
    
        Entity
    
        Value Object
    
        Aggregate
    
        Domain Service
    
        Domain Event
    
        +-----------------------------+
    
                       |
                       v
    
              Infrastructure

* * *

Domain Service thuộc:
    
    
    Domain Layer

vì nó chứa **business rule**.

* * *

# 3\. Entity và Domain Service khác nhau thế nào?

Đây là phần quan trọng nhất.

* * *

## Trường hợp Entity

Ví dụ:

Một Novel có thể:

  * Đổi tên. 
  * Publish. 
  * Archive. 



Logic này thuộc Novel.
    
    
    class Novel:
    
    
        def publish(self):
    
            if not self.chapters:
                raise Exception(
                    "Cannot publish empty novel"
                )
    
            self.status = "published"

* * *

Tại sao?

Vì:

Novel biết:

  * trạng thái của nó. 
  * chapter của nó. 
  * rule publish. 



* * *

## Trường hợp Domain Service

Ví dụ:

Tính điểm xếp hạng truyện:

Cần:

  * Novel. 
  * Rating. 
  * View. 
  * Comment. 
  * Trending. 



Ai sở hữu?
    
    
    Novel?
    Rating?
    Reader?

Không ai.

* * *

Tạo:
    
    
    RankingService

* * *

# 4\. Dấu hiệu cần tạo Domain Service

Dùng Domain Service khi:

## 1\. Logic liên quan nhiều Entity

Ví dụ:
    
    
    Account A
    
    Account B
    
    Transfer

Không thể đặt:
    
    
    account_a.transfer()

vì giao dịch liên quan hai Account.

* * *

## 2\. Không có Entity nào sở hữu tự nhiên

Ví dụ:
    
    
    Recommendation
    Pricing
    Ranking
    Matching

* * *

## 3\. Logic là một khái niệm nghiệp vụ riêng

Ví dụ:

Business nói:

> "Hệ thống cần tính mức độ phù hợp của truyện."

Đây là một khái niệm riêng:
    
    
    Recommendation Algorithm

* * *

# 5\. Ví dụ: Bank Transfer Service

Có:
    
    
    class Account:
    
    
        def withdraw(
            self,
            amount
        ):
            ...
    
    
        def deposit(
            self,
            amount
        ):
            ...

* * *

Chuyển tiền:
    
    
    class TransferService:
    
    
        def transfer(
            self,
            source,
            target,
            amount
        ):
    
            source.withdraw(
                amount
            )
    
            target.deposit(
                amount
            )

* * *

Tại sao không:
    
    
    account.transfer()

?

Vì:

  * Account A không sở hữu Account B. 
  * Giao dịch là một nghiệp vụ độc lập. 



* * *

# 6\. Domain Service vs Application Service

Đây là phần rất dễ nhầm.

* * *

# Application Service

Nó điều phối.

Ví dụ:
    
    
    class PublishNovelUseCase:
    
    
        def execute(
            self,
            novel_id
        ):
    
            novel = (
                repository.get_by_id(
                    novel_id
                )
            )
    
            novel.publish()
    
            repository.save(
                novel
            )

Nó làm:

  * Lấy dữ liệu. 
  * Gọi Domain. 
  * Lưu dữ liệu. 



* * *

# Domain Service

Nó quyết định nghiệp vụ.

Ví dụ:
    
    
    class RankingService:
    
    
        def calculate(
            self,
            novel
        ):
    
            score = (
                novel.views * 0.5
                +
                novel.likes * 0.3
            )
    
            return score

* * *

So sánh:

| Application Service| Domain Service  
---|---|---  
Layer| Application| Domain  
Chứa business rule| ❌| ✅  
Gọi Repository| ✅| Thường ❌  
Điều phối| ✅| ❌  
Tính toán nghiệp vụ| ❌| ✅  
  
* * *

# 7\. Domain Service không phải "Service class chứa tất cả"

Một lỗi phổ biến:
    
    
    class NovelService:
    
        create()
    
        update()
    
        delete()
    
        publish()
    
        recommend()
    
        crawl()

Đây là kiểu Service Layer cũ.

* * *

DDD không muốn:
    
    
    God Service

* * *

Thay vào đó:
    
    
    Novel Entity
    
    PricingService
    
    RecommendationService
    
    ChapterMergeService

* * *

# 8\. Domain Service trong App Cào Truyện

Bây giờ áp dụng vào dự án.

* * *

## 8.1 RecommendationService

Yêu cầu:

> Gợi ý truyện phù hợp với người đọc.

Cần:
    
    
    Reader
    
    Novel
    
    ReadingHistory
    
    Category

* * *

Không thuộc:
    
    
    Reader?
    Novel?

* * *

Tạo:
    
    
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

# 9\. ChapterMergeService

Đây là ví dụ rất thực tế với crawler.

Giả sử:

Nguồn A:
    
    
    Chapter 1
    Chapter 2
    Chapter 3

Nguồn B:
    
    
    Chapter 1
    Chapter 2
    Chapter 3

Cần:

  * loại duplicate. 
  * chọn nội dung tốt hơn. 



* * *

Không thuộc:
    
    
    Chapter
    Source
    Novel

* * *

Tạo:
    
    
    class ChapterMergeService:
    
    
        def merge(
            self,
            chapters
        ):
    
            result = {}
    
            for chapter in chapters:
    
                result[
                    chapter.number
                ] = chapter
    
    
            return list(
                result.values()
            )

* * *

# 10\. PricingService

Ví dụ thương mại:

Rule:

  * Khách VIP giảm 10%. 
  * Đơn trên 1.000.000 VNĐ giảm thêm. 



* * *

Không thuộc:
    
    
    Customer
    Order
    Product

* * *

Tạo:
    
    
    class PricingService:
    
    
        def calculate(
            self,
            order,
            customer
        ):
    
            price = order.total()
    
    
            if customer.is_vip:
    
                price *= 0.9
    
    
            if price > 1_000_000:
    
                price -= 50_000
    
    
            return price

* * *

# 11\. Domain Service và Value Object

Ví dụ:

Đổi tiền.

Ta có:
    
    
    class Money:
    
        amount
        currency

* * *

Logic:
    
    
    100.000 VNĐ
    
    sang
    
    USD

Cần:

  * Money A 
  * Money B 
  * Exchange Rate 



* * *

Không thuộc Money nào.

* * *

Tạo:
    
    
    class ExchangeService:
    
    
        def exchange(
            self,
            money,
            target_currency,
            rate
        ):
    
            return Money(
                money.amount * rate,
                target_currency
            )

* * *

# 12\. Domain Service nên Stateless

Sai:
    
    
    class RecommendationService:
    
    
        def __init__(self):
    
            self.current_user = None

* * *

Đúng:
    
    
    class RecommendationService:
    
    
        def recommend(
            self,
            reader,
            novels
        ):
            ...

* * *

Lý do:

  * Dễ test. 
  * Dễ scale. 
  * Không có trạng thái ẩn. 



* * *

# 13\. Domain Service và Repository

Câu hỏi:

> Domain Service có gọi Repository không?

Thông thường:

Không.

* * *

Sai:
    
    
    class RecommendationService:
    
    
        def recommend(
            self,
            reader_id
        ):
    
            novels = repository.get_all()

* * *

Vì Domain Service biết Infrastructure.

* * *

Đúng:

Application lấy dữ liệu:
    
    
    novels = repository.get_all()
    
    
    recommendation_service.recommend(
        reader,
        novels
    )

* * *

Luồng:
    
    
    Application
    
          |
          |
    Repository
    
          |
          |
    Domain Service
    
          |
          |
    Result

* * *

# 14\. Domain Service kết hợp Use Case

Ví dụ:

Use Case:
    
    
    class GenerateRecommendationUseCase:
    
    
        def execute(
            self,
            reader_id
        ):
    
            reader = (
                reader_repo.get_by_id(
                    reader_id
                )
            )
    
    
            novels = (
                novel_repo.get_all()
            )
    
    
            result = (
                recommendation_service
                .recommend(
                    reader,
                    novels
                )
            )
    
    
            return result

* * *

Ở đây:

Use Case:

  * lấy dữ liệu. 



Domain Service:

  * tính toán nghiệp vụ. 



* * *

# 15\. Testing Domain Service

Ví dụ:
    
    
    def test_recommendation():
    
    
        reader = Reader(
            categories=[
                "Fantasy"
            ]
        )
    
    
        novels = [
            Novel(
                "A",
                "Fantasy"
            ),
            Novel(
                "B",
                "Romance"
            )
        ]
    
    
        service = RecommendationService()
    
    
        result = service.recommend(
            reader,
            novels
        )
    
    
        assert len(result) == 1

* * *

Không cần:

  * Database. 
  * API. 
  * UI. 



* * *

# 16\. Cấu trúc thư mục
    
    
    domain/
    
    ├── novels/
    │
    │   ├── entities/
    │   │
    │   ├── value_objects/
    │   │
    │   └── services/
    │
    │       ├── recommendation.py
    │       ├── ranking.py
    │       └── chapter_merge.py

* * *

# 17\. Những lỗi thường gặp

## Lỗi 1: Entity quá nghèo

Sai:
    
    
    class Novel:
    
        title
        status

* * *

Đúng:
    
    
    class Novel:
    
        publish()
    
        rename()
    
        archive()

* * *

## Lỗi 2: Mọi thứ thành Service

Sai:
    
    
    UserService
    NovelService
    OrderService

* * *

## Lỗi 3: Domain Service chứa SQL

Sai:
    
    
    class RankingService:
    
        SELECT *

* * *

Database thuộc Infrastructure.

* * *

# 18\. Kiến trúc sau Buổi 12

Hiện tại:
    
    
    Presentation
    
          |
          v
    
    Application Layer
    
          |
          |
    Use Case
    
          |
          v
    
    Domain Layer
    
     + Entity
     + Value Object
     + Aggregate
     + Domain Service
     + Repository Interface
     + Domain Event
    
          |
          v
    
    Infrastructure
    
     + SQLite
     + HTTP
     + File

* * *

# Bài tập

## Bài 1

Phân loại:

Logic nào là Entity, logic nào là Domain Service?

  1. Novel đổi tên. 
  2. Novel publish. 
  3. Tính ranking truyện. 
  4. Merge chapter từ nhiều website. 
  5. Lưu truyện xuống SQLite. 
  6. Gợi ý truyện cho user. 



* * *

## Bài 2

Thiết kế:
    
    
    ChapterSimilarityService

Yêu cầu:

  * So sánh 2 chapter. 
  * Tính % giống nhau. 
  * Trả về kết quả. 



* * *

## Bài 3

Thiết kế cho App Cào Truyện:
    
    
    Domain Services:
    
    ?
    ?
    ?

Chọn ít nhất 3 service hợp lý.

* * *

# Tổng kết Buổi 12

Cần nhớ:

✅ Domain Service chứa nghiệp vụ không thuộc Entity.  
✅ Domain Service thuộc Domain Layer.  
✅ Không phải mọi logic đều tạo Service.  
✅ Entity giữ behavior của chính nó.  
✅ Application Service điều phối.  
✅ Domain Service xử lý business rule phức tạp.  
✅ Domain Service không phụ thuộc Database.

* * *

Buổi tiếp theo theo roadmap:

# Buổi 13: Domain Event trong DDD

Nội dung:

  * Event khác Command thế nào? 
  * Aggregate phát sinh Event. 
  * Event Bus. 
  * Event Handler. 
  * Thiết kế Event-driven cho App Cào Truyện: 
    * `NovelCreated`
    * `ChapterPublished`
    * `ReadingCompleted`
    * `CrawlFinished`

