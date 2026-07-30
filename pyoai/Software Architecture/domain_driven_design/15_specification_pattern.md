# Domain-Driven Design Deep Dive

# Buổi 15: Specification Pattern trong DDD

Sau buổi 14, chúng ta đã học:

  * Factory Pattern 
  * Aggregate Factory 
  * Factory vs Repository 
  * Factory trong Plugin Architecture 



Hôm nay chúng ta học một Pattern cực kỳ quan trọng trong DDD:

# Specification Pattern

Mục tiêu:

> Biến các Business Rule thành những object có thể tái sử dụng, kết hợp và kiểm thử độc lập.

* * *

# 1\. Vấn đề: Business Rule phức tạp

Ví dụ App Cào Truyện:

Muốn publish một Novel.

Rule:

Một truyện được publish nếu:

  * Có ít nhất 10 chapter. 
  * Không bị khóa. 
  * Có tác giả. 
  * Source đang active. 



Code truyền thống:
    
    
    def publish(novel):
    
        if (
            len(novel.chapters) >= 10
            and novel.author
            and novel.source.active
            and not novel.blocked
        ):
            novel.status = "published"

* * *

Ban đầu nhìn ổn.

Nhưng sau này:

Thêm rule:
    
    
    Novel phải có rating > 4.0
    
    Novel phải thuộc category cho phép
    
    User phải có quyền publish

Code thành:
    
    
    if (
        rule1
        and rule2
        and rule3
        and rule4
        and rule5
        and rule6
    ):
        ...

* * *

Vấn đề:

  * Khó đọc. 
  * Khó test. 
  * Không tái sử dụng. 
  * Business rule nằm rải rác. 



* * *

DDD đưa ra:

# Specification

* * *

# 2\. Specification là gì?

Định nghĩa:

> Specification là một object đại diện cho một Business Rule.

Ví dụ:

Thay vì:
    
    
    if novel.chapters >= 10:

Ta có:
    
    
    HasEnoughChaptersSpecification()

* * *

Code trở thành:
    
    
    if can_publish.is_satisfied_by(novel):
    
        novel.publish()

* * *

# 3\. Specification thuộc Layer nào?

Specification thuộc:
    
    
    Domain Layer

Vì nó chứa:

  * Business Rule. 
  * Domain Knowledge. 



Cấu trúc:
    
    
    domain/
    
        specifications/
    
            novel/
                can_publish.py
                has_chapters.py
    
            user/
                is_vip.py

* * *

# 4\. Specification cơ bản

Ta tạo interface:
    
    
    from abc import ABC, abstractmethod
    
    
    class Specification(ABC):
    
    
        @abstractmethod
        def is_satisfied_by(
            self,
            candidate
        ):
            pass

* * *

Mọi Specification phải trả về:
    
    
    True

hoặc
    
    
    False

* * *

# 5\. Ví dụ: Chapter Count Specification

Business Rule:

> Novel phải có ít nhất 10 chapter.

* * *

Entity:
    
    
    class Novel:
    
    
        def __init__(
            self,
            title,
            chapters
        ):
    
            self.title = title
            self.chapters = chapters

* * *

Specification:
    
    
    class HasEnoughChaptersSpecification:
    
    
        def __init__(
            self,
            minimum
        ):
            self.minimum = minimum
    
    
    
        def is_satisfied_by(
            self,
            novel
        ):
    
            return (
                len(novel.chapters)
                >= self.minimum
            )

* * *

Sử dụng:
    
    
    spec = HasEnoughChaptersSpecification(
        10
    )
    
    
    if spec.is_satisfied_by(novel):
    
        print("OK")

* * *

# 6\. Specification thay thế if-else

Trước:
    
    
    if (
        novel.chapters >= 10
        and novel.author
        and novel.status != "blocked"
    ):
        publish()

* * *

Sau:
    
    
    rule = (
        HasEnoughChapter()
        .and(
            HasAuthor()
        )
        .and(
            NotBlocked()
        )
    )
    
    
    if rule.is_satisfied_by(novel):
    
        publish()

* * *

Business đọc gần giống ngôn ngữ tự nhiên.

* * *

# 7\. Composite Specification

Đây là sức mạnh chính.

Một Specification có thể kết hợp:

  * AND 
  * OR 
  * NOT 



* * *

Ví dụ:
    
    
    Có thể publish nếu:
    
    Có 10 chapter
    
    AND
    
    Có author
    
    AND
    
    Không bị block

* * *

Biểu diễn:
    
    
    CanPublishNovel
    
          AND
    
    HasEnoughChapter
    
          AND
    
    HasAuthor
    
          AND
    
    NotBlocked

* * *

# 8\. Base Composite Specification
    
    
    class Specification:
    
    
        def is_satisfied_by(
            self,
            candidate
        ):
            raise NotImplementedError
    
    
    
        def and_spec(
            self,
            other
        ):
    
            return AndSpecification(
                self,
                other
            )
    
    
    
        def or_spec(
            self,
            other
        ):
    
            return OrSpecification(
                self,
                other
            )
    
    
    
        def not_spec(
            self
        ):
    
            return NotSpecification(
                self
            )

* * *

# 9\. AND Specification
    
    
    class AndSpecification:
    
    
        def __init__(
            self,
            left,
            right
        ):
    
            self.left = left
            self.right = right
    
    
    
        def is_satisfied_by(
            self,
            candidate
        ):
    
            return (
                self.left.is_satisfied_by(candidate)
                and
                self.right.is_satisfied_by(candidate)
            )

* * *

# 10\. OR Specification
    
    
    class OrSpecification:
    
    
        def __init__(
            self,
            left,
            right
        ):
    
            self.left = left
            self.right = right
    
    
    
        def is_satisfied_by(
            self,
            candidate
        ):
    
            return (
                self.left.is_satisfied_by(candidate)
                or
                self.right.is_satisfied_by(candidate)
            )

* * *

# 11\. NOT Specification
    
    
    class NotSpecification:
    
    
        def __init__(
            self,
            spec
        ):
    
            self.spec = spec
    
    
    
        def is_satisfied_by(
            self,
            candidate
        ):
    
            return not (
                self.spec
                .is_satisfied_by(candidate)
            )

* * *

# 12\. Ví dụ hoàn chỉnh: Publish Novel

## Các rule

* * *

## Rule 1:

Có chapter
    
    
    class HasChapterSpecification:
    
    
        def is_satisfied_by(
            self,
            novel
        ):
    
            return len(
                novel.chapters
            ) > 0

* * *

## Rule 2:

Không bị khóa
    
    
    class NotBlockedSpecification:
    
    
        def is_satisfied_by(
            self,
            novel
        ):
    
            return not novel.blocked

* * *

## Rule 3:

Có author
    
    
    class HasAuthorSpecification:
    
    
        def is_satisfied_by(
            self,
            novel
        ):
    
            return novel.author is not None

* * *

Kết hợp:
    
    
    can_publish = (
        HasChapterSpecification()
        .and_spec(
            HasAuthorSpecification()
        )
        .and_spec(
            NotBlockedSpecification()
        )
    )

* * *

Kiểm tra:
    
    
    if can_publish.is_satisfied_by(
        novel
    ):
    
        novel.publish()

* * *

# 13\. Specification trong Aggregate

Một câu hỏi:

> Specification có thay thế Entity method không?

Không.

Ví dụ:

Sai:
    
    
    novel.can_publish()

bỏ hết logic.

* * *

Đúng:
    
    
    class Novel:
    
    
        def publish(
            self,
            specification
        ):
    
            if not specification.is_satisfied_by(
                self
            ):
                raise Exception(
                    "Cannot publish"
                )
    
    
            self.status = "published"

* * *

Aggregate vẫn kiểm soát behavior.

Specification chỉ cung cấp rule.

* * *

# 14\. Specification trong App Cào Truyện

Đây là nơi Pattern này rất hữu ích.

* * *

# 14.1 Source có được crawl không?

Rule:

  * Source active. 
  * Không bị blacklist. 
  * Có parser. 



* * *

Specification:
    
    
    class CanCrawlSourceSpecification:
    
    
        def is_satisfied_by(
            self,
            source
        ):
    
            return (
                source.active
                and
                not source.blacklisted
                and
                source.parser_available
            )

* * *

Crawler:
    
    
    if can_crawl.is_satisfied_by(
        source
    ):
    
        crawler.start()

* * *

# 14.2 Chapter hợp lệ

Rule:

  * Có nội dung. 
  * Đúng số chapter. 
  * Không duplicate. 


    
    
    class ValidChapterSpecification:
    
    
        def is_satisfied_by(
            self,
            chapter
        ):
    
            return (
                chapter.content
                and
                chapter.number > 0
                and
                not chapter.duplicate
            )

* * *

# 14.3 User VIP

Rule:

VIP nếu:

  * Đăng ký > 1 năm. 
  * Có thanh toán. 
  * Không bị khóa. 



* * *
    
    
    class IsVipUserSpecification:
    
    
        def is_satisfied_by(
            self,
            user
        ):
    
            return (
                user.membership_years >= 1
                and user.payment_ok
                and not user.blocked
            )

* * *

# 15\. Specification và Use Case

Use Case sử dụng Specification.

Ví dụ:
    
    
    class PublishNovelUseCase:
    
    
        def __init__(
            self,
            repository,
            specification
        ):
    
            self.repository = repository
            self.specification = specification
    
    
    
        def execute(
            self,
            novel_id
        ):
    
            novel = (
                self.repository
                .get_by_id(novel_id)
            )
    
    
            if not self.specification
            .is_satisfied_by(novel):
    
                raise Exception(
                    "Cannot publish"
                )
    
    
            novel.publish()
    
    
            self.repository.save(
                novel
            )

* * *

# 16\. Specification vs Validation

Hai thứ khác nhau.

* * *

## Validation

Kiểm tra dữ liệu:
    
    
    email != ""

* * *

## Specification

Kiểm tra nghiệp vụ:
    
    
    User đủ điều kiện VIP

* * *

Ví dụ:
    
    
    Email rỗng
    
    =
    Validation
    
    
    User mua đủ 10 triệu để VIP
    
    =
    Specification

* * *

# 17\. Specification vs Policy

Nhiều hệ thống gọi:
    
    
    Business Policy

thay cho Specification.

Ví dụ:
    
    
    DiscountPolicy
    
    ShippingPolicy
    
    PublishingPolicy

Có thể implement bằng Specification.

* * *

# 18\. Specification và Database

Có thể dùng Specification để query.

Ví dụ:

Specification:
    
    
    ActiveNovelSpecification()

Có thể chuyển thành:
    
    
    WHERE status='active'

* * *

Nhưng đây là nâng cao:

  * Specification Visitor. 
  * Query Specification. 



* * *

# 19\. Cấu trúc Project
    
    
    domain/
    
    ├── specifications/
    
    │
    ├── base.py
    │
    ├── composite.py
    │
    └── novels/
    
        ├── can_publish.py
        ├── valid_chapter.py
        └── can_crawl.py

* * *

# 20\. Những lỗi thường gặp

## Lỗi 1: Nhét toàn bộ logic vào Specification

Sai:
    
    
    class NovelSpecification:
    
        create_novel()
    
        publish()
    
        delete()

Specification chỉ:
    
    
    True / False

* * *

## Lỗi 2: Specification truy cập Database

Sai:
    
    
    class VipUserSpecification:
    
        query_database()

Specification thuộc Domain.

* * *

## Lỗi 3: Tạo quá nhiều Specification nhỏ vô nghĩa

Không cần:
    
    
    HasTitleSpecification
    
    HasIdSpecification

nếu đó chỉ là validation đơn giản.

* * *

# 21\. Kiến trúc DDD sau Buổi 15

Domain Layer hiện tại:
    
    
    Domain
    
    ├── Entities
    │
    ├── Value Objects
    │
    ├── Aggregates
    │
    ├── Repository Interfaces
    │
    ├── Domain Services
    │
    ├── Domain Events
    │
    ├── Factories
    │
    └── Specifications

* * *

# Bài tập

## Bài 1

Thiết kế:
    
    
    CanImportChapterSpecification

Rule:

  * Chapter có title. 
  * Content không rỗng. 
  * Chapter chưa tồn tại. 



* * *

## Bài 2

Viết:
    
    
    CanPublishNovelSpecification

bằng cách kết hợp:
    
    
    HasEnoughChapter
    
    HasAuthor
    
    NotBlocked

* * *

## Bài 3

Trong App Cào Truyện, tìm 5 Business Rule phù hợp để biến thành Specification.

Gợi ý:

  * Source crawl. 
  * Chapter import. 
  * Novel publish. 
  * User đọc truyện. 
  * Recommendation. 



* * *

# Tổng kết Buổi 15

Cần nhớ:

✅ Specification biểu diễn Business Rule.  
✅ Specification thuộc Domain Layer.  
✅ Specification thay thế if/else phức tạp.  
✅ Có thể kết hợp AND / OR / NOT.  
✅ Specification không chứa Database.  
✅ Specification kết hợp tốt với Aggregate và Use Case.  
✅ Rất hữu ích cho hệ thống có nhiều luật nghiệp vụ.

* * *

Buổi tiếp theo theo roadmap:

# Buổi 16: CQRS trong DDD

Nội dung:

  * Command Query Responsibility Segregation. 
  * Vì sao tách Read và Write? 
  * Command Model. 
  * Query Model. 
  * Read Database. 
  * Áp dụng cho App Cào Truyện: 
    * Database ghi crawl. 
    * Search Index đọc truyện. 
    * Dashboard thống kê.

