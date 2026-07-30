# Domain-Driven Design Deep Dive

# Buổi 7: Value Object — Đối tượng không có Identity nhưng có ý nghĩa nghiệp vụ

Trong buổi 6 chúng ta học **Entity** :

> Một đối tượng được xác định bởi Identity.

Hôm nay chúng ta học khái niệm đối lập:

> **Value Object được xác định bởi giá trị của nó, không phải Identity.**

Đây là một trong những khái niệm bị hiểu sai nhiều nhất khi học DDD.

* * *

# Roadmap

✅ Buổi 1: DDD là gì

✅ Buổi 2: Ubiquitous Language

✅ Buổi 3: Domain & Subdomain

✅ Buổi 4: Bounded Context

✅ Buổi 5: Context Mapping

✅ Buổi 6: Entity

✅ **Buổi 7: Value Object**

⬜ Buổi 8: Aggregate

⬜ Buổi 9: Aggregate Root

⬜ Buổi 10: Repository

...

* * *

# 1\. Value Object là gì?

Định nghĩa:

> Value Object là một object được xác định hoàn toàn bởi các thuộc tính của nó, không có Identity riêng.

Ví dụ:
    
    
    Email
    Money
    Address
    Color
    Date Range
    Coordinate

* * *

# 2\. So sánh Entity và Value Object

| Entity| Value Object  
---|---|---  
Identity| Có| Không  
Thay đổi| Mutable| Thường Immutable  
So sánh| Theo ID| Theo giá trị  
Ví dụ| User, Novel, Order| Email, Money, Address  
  
* * *

# 3\. Ví dụ đời thực

## Entity

Hai người:
    
    
    Nguyễn Văn A
    CCCD: 123

và
    
    
    Nguyễn Văn A
    CCCD: 456

Là hai người khác nhau.

Vì có Identity khác nhau.

* * *

## Value Object

Hai email:
    
    
    abc@gmail.com

và
    
    
    abc@gmail.com

Chúng giống nhau.

Không cần biết:
    
    
    Email số 1
    Email số 2

Email chỉ là giá trị.

* * *

# 4\. Ví dụ sai trong lập trình

Nhiều người viết:
    
    
    class Email:
    
        def __init__(self, id, value):
            self.id = id
            self.value = value

Sai.

Email không cần ID.

Bạn không quan tâm:
    
    
    Email #123
    Email #456

Bạn chỉ quan tâm:
    
    
    abc@gmail.com

* * *

# 5\. Value Object trong Python

Python rất phù hợp với Value Object vì có:

  * dataclass 
  * frozen=True 
  * type hint 



Ví dụ:
    
    
    from dataclasses import dataclass
    
    
    @dataclass(frozen=True)
    class Email:
    
        value: str

* * *

Sử dụng:
    
    
    email1 = Email(
        "user@gmail.com"
    )
    
    email2 = Email(
        "user@gmail.com"
    )
    
    
    print(email1 == email2)

Kết quả:
    
    
    True

Vì giá trị giống nhau.

* * *

# 6\. Vì sao Value Object nên immutable?

Immutable nghĩa là:

> Sau khi tạo ra, giá trị không thể thay đổi.

Ví dụ:
    
    
    email = Email(
        "a@gmail.com"
    )

Không cho phép:
    
    
    email.value = "b@gmail.com"

* * *

Tại sao?

Vì thay đổi giá trị có thể tạo ra trạng thái không hợp lệ.

* * *

Ví dụ:
    
    
    money = Money(100)

Nếu ai đó làm:
    
    
    money.amount = -500

Hệ thống lỗi.

* * *

# 7\. Value Object phải tự bảo vệ tính hợp lệ

Ví dụ Email:

Không nên:
    
    
    email = Email(
        "abc"
    )

vì email sai.

* * *

Đúng:
    
    
    from dataclasses import dataclass
    
    
    @dataclass(frozen=True)
    class Email:
    
        value: str
    
    
        def __post_init__(self):
    
            if "@" not in self.value:
                raise ValueError(
                    "Invalid email"
                )

* * *

Bây giờ:
    
    
    Email("abc")

sẽ lỗi.

* * *

Domain không cho dữ liệu sai tồn tại.

* * *

# 8\. Ví dụ Money

Tiền là Value Object.

Không nên:
    
    
    class Money:
    
        id
        amount

Tiền không có identity.

* * *

Thiết kế:
    
    
    from dataclasses import dataclass
    
    
    @dataclass(frozen=True)
    class Money:
    
        amount: int
        currency: str
    
    
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

Sử dụng:
    
    
    price1 = Money(
        100000,
        "VND"
    )
    
    price2 = Money(
        50000,
        "VND"
    )
    
    
    total = price1.add(price2)

Kết quả:
    
    
    150000 VND

* * *

# 9\. Value Object có Behavior

Một hiểu lầm:

> Value Object chỉ là data class.

Sai.

Value Object cũng có hành vi.

Ví dụ:

Money:
    
    
    money.add()
    money.subtract()
    money.multiply()

* * *

Email:
    
    
    email.domain()
    email.is_company_email()

* * *

Address:
    
    
    address.full_address()

* * *

# 10\. Ví dụ Address

Sai:
    
    
    class User:
    
        name: str
        city: str
        district: str
        street: str

User phình to.

* * *

Đúng:
    
    
    @dataclass(frozen=True)
    class Address:
    
        city: str
        district: str
        street: str

* * *

User:
    
    
    class User:
    
        def __init__(
            self,
            name,
            address
        ):
            self.name = name
            self.address = address

* * *

Bây giờ:
    
    
    user.address.city

rõ nghĩa hơn.

* * *

# 11\. Entity chứa Value Object

Đây là cách DDD thường dùng.

Ví dụ:
    
    
    class Reader:
    
        id: int
    
        email: Email
    
        address: Address

* * *

Reader:

Entity.

* * *

Email:

Value Object.

* * *

Address:

Value Object.

* * *

Quan hệ:
    
    
    Reader(Entity)
    
        |
        |
        +---- Email(Value Object)
    
        |
        |
        +---- Address(Value Object)

* * *

# 12\. Áp dụng vào App Cào Truyện

Trong Reader Context.

Chúng ta có:

Entity:
    
    
    Novel
    Reader
    Bookmark
    ReadingHistory

* * *

Value Object:
    
    
    NovelId
    ChapterNumber
    Url
    Rating
    ReadingPosition

* * *

Ví dụ ChapterNumber:

Business Rule:
    
    
    Chapter phải >= 1

* * *

Sai:
    
    
    chapter.number = -10

* * *

Tạo Value Object:
    
    
    from dataclasses import dataclass
    
    
    @dataclass(frozen=True)
    class ChapterNumber:
    
        value: int
    
    
        def __post_init__(self):
    
            if self.value < 1:
                raise ValueError(
                    "Invalid chapter number"
                )

* * *

Chapter:
    
    
    class Chapter:
    
        def __init__(
            self,
            number: ChapterNumber,
            title: str
        ):
            self.number = number
            self.title = title

* * *

Bây giờ:
    
    
    Chapter(
        ChapterNumber(0),
        "Chapter 1"
    )

bị chặn.

* * *

# 13\. URL cũng nên là Value Object

Trong Crawler Context:

Sai:
    
    
    class Novel:
    
        url: str

Vì:
    
    
    Novel(
        url="abc"
    )

có thể xảy ra.

* * *

Tạo:
    
    
    @dataclass(frozen=True)
    class Url:
    
        value: str
    
    
        def __post_init__(self):
    
            if not self.value.startswith(
                "http"
            ):
                raise ValueError(
                    "Invalid URL"
                )

* * *

Entity:
    
    
    class Source:
    
        url: Url

* * *

# 14\. Value Object giúp giảm Primitive Obsession

Đây là vấn đề rất phổ biến.

Ví dụ:
    
    
    def create_user(
        email: str,
        phone: str,
        money: int
    ):
        pass

Nhìn rất khó hiểu.

* * *

DDD thay bằng:
    
    
    def create_user(
        email: Email,
        phone: PhoneNumber,
        money: Money
    ):
        pass

Code tự giải thích chính nó.

* * *

# 15\. Primitive Obsession trong App Cào Truyện

Sai:
    
    
    def crawl(
        url: str,
        chapter: int,
        rating: float
    ):
        pass

* * *

Đúng:
    
    
    def crawl(
        url: Url,
        chapter: ChapterNumber,
        rating: Rating
    ):
        pass

* * *

# 16\. Value Object và Database

Một câu hỏi:

Value Object có bảng riêng không?

Câu trả lời:

Không bắt buộc.

Ví dụ:

Entity:
    
    
    Reader

Database:
    
    
    reader
    
    id
    email
    city
    district
    street

* * *

Nhưng Domain:
    
    
    Reader
    
    Email
    
    Address

Database không quyết định Domain Model.

* * *

# 17\. Value Object Nested

Ví dụ:
    
    
    @dataclass(frozen=True)
    class Money:
    
        amount: int
        currency: str
    
    
    
    @dataclass(frozen=True)
    class Price:
    
        money: Money
        discount: int

* * *

Có thể tạo:
    
    
    Order
    
        |
        |
        +-- Price
    
              |
              |
              +-- Money

* * *

# 18\. Entity hay Value Object?

Hãy phân tích.

* * *

## User

Có ID?

Có.

=> Entity

* * *

## Email

Có ID?

Không.

=> Value Object

* * *

## Novel

Có vòng đời?

Có:
    
    
    Draft
    Published
    Completed

=> Entity

* * *

## Money

Có trạng thái riêng?

Không.

=> Value Object

* * *

## Address

Có Identity?

Không.

=> Value Object

* * *

# 19\. Quy tắc thiết kế Value Object

Một Value Object tốt:

## 1\. Immutable
    
    
    @dataclass(frozen=True)

* * *

## 2\. Có Validation
    
    
    if invalid:
        raise ValueError()

* * *

## 3\. Có Behavior

Không chỉ:
    
    
    value

* * *

## 4\. Không có ID

Không:
    
    
    id

* * *

## 5\. Có thể thay thế bằng object khác cùng giá trị

Ví dụ:
    
    
    Money(
    100000,
    "VND"
    )

thay bằng:
    
    
    Money(
    100000,
    "VND"
    )

Không ảnh hưởng.

* * *

# 20\. Ví dụ hoàn chỉnh Domain Model
    
    
    from dataclasses import dataclass
    
    
    @dataclass(frozen=True)
    class NovelId:
    
        value: int
    
    
    
    @dataclass(frozen=True)
    class ChapterNumber:
    
        value: int
    
    
        def __post_init__(self):
    
            if self.value < 1:
                raise ValueError()
    
    
    
    class Chapter:
    
        def __init__(
            self,
            number: ChapterNumber,
            title: str
        ):
    
            self.number = number
            self.title = title
    
    
    
    class Novel:
    
        def __init__(
            self,
            novel_id: NovelId,
            title: str
        ):
    
            self.id = novel_id
            self.title = title
            self.chapters = []
    
    
        def add_chapter(
            self,
            chapter: Chapter
        ):
    
            self.chapters.append(
                chapter
            )

Ở đây:
    
    
    Novel
       |
       +-- NovelId
       |
       +-- Chapter
              |
              +-- ChapterNumber

Đây là Domain Model đúng tinh thần DDD.

* * *

# Bài tập

## Bài 1

Thiết kế các Value Object:
    
    
    Email
    
    Money
    
    Url
    
    ChapterNumber
    
    Rating

Mỗi cái cần:

  * validation 
  * immutable 
  * behavior phù hợp 



* * *

## Bài 2

Trong App Cào Truyện, hãy phân loại:

Entity hay Value Object?
    
    
    Novel
    Chapter
    SourceUrl
    AuthorName
    ReadingProgress
    Category
    NovelId

* * *

## Bài 3

Refactor:
    
    
    class Product:
    
        price: int
        currency: str

sang sử dụng Value Object `Money`.

* * *

# Tổng kết Buổi 7

Sau buổi này bạn cần nhớ:

  * **Entity có Identity, Value Object có Value.**
  * Value Object không có ID. 
  * Value Object nên immutable. 
  * Value Object chứa validation và behavior. 
  * Value Object giúp loại bỏ primitive obsession. 
  * Một Domain Model tốt thường là sự kết hợp: 


    
    
    Entity
       |
       +-- Value Object
       |
       +-- Value Object

* * *

Buổi tiếp theo (**Buổi 8**) chúng ta sẽ học **Aggregate** — một trong những phần khó nhất của DDD. Bạn sẽ hiểu vì sao Entity không thể tự do thay đổi lẫn nhau, tại sao cần một "ranh giới bảo vệ", và cách thiết kế Aggregate cho hệ thống thực tế như Order, Novel, Chapter.

