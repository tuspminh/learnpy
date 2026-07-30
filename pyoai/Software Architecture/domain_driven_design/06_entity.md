# Domain-Driven Design Deep Dive

# Buổi 6: Entity — Đối tượng có Identity và Behavior

Đây là lúc chúng ta bước vào phần **Tactical Design** của DDD.

Nếu 5 buổi đầu chúng ta học cách:

  * Xác định Domain 
  * Chia Subdomain 
  * Tạo Bounded Context 
  * Thiết kế quan hệ giữa Context 



thì từ buổi này chúng ta bắt đầu xây dựng **Domain Model thật sự**.

* * *

# Roadmap

✅ Buổi 1: DDD là gì

✅ Buổi 2: Ubiquitous Language

✅ Buổi 3: Domain & Subdomain

✅ Buổi 4: Bounded Context

✅ Buổi 5: Context Mapping

✅ **Buổi 6: Entity**

⬜ Buổi 7: Value Object

⬜ Buổi 8: Aggregate

⬜ Buổi 9: Aggregate Root

...

* * *

# 1\. Entity là gì?

Định nghĩa của Eric Evans:

> Entity là một đối tượng được xác định không phải bởi thuộc tính của nó, mà bởi **identity (danh tính) của nó**.

Nói đơn giản:

> Entity là thứ có "căn cước riêng", dù dữ liệu bên trong thay đổi, nó vẫn là cùng một đối tượng.

* * *

# 2\. Ví dụ đời thực

## Con người

Hôm nay:
    
    
    Nguyễn Văn A
    Tuổi: 30
    Địa chỉ: Hà Nội

10 năm sau:
    
    
    Nguyễn Văn A
    Tuổi: 40
    Địa chỉ: TP.HCM

Thông tin thay đổi.

Nhưng vẫn là:
    
    
    Nguyễn Văn A

vì có:
    
    
    CCCD: 0123456789

Identity không đổi.

* * *

## Chiếc xe

Ban đầu:
    
    
    Xe Toyota
    Màu trắng

Sau đó:
    
    
    Sơn lại màu đen
    Thay động cơ

Nó vẫn là chiếc xe đó.

Vì:
    
    
    Biển số xe
    VIN

là identity.

* * *

# 3\. Entity trong phần mềm

Ví dụ:
    
    
    class User:
        id
        name
        email

Có thể:
    
    
    name thay đổi
    email thay đổi
    password thay đổi

nhưng:
    
    
    id

không đổi.

* * *
    
    
    user = User(
        id=1,
        name="Nam"
    )

Sau:
    
    
    user.name = "Minh"

vẫn là:
    
    
    User(id=1)

* * *

# 4\. Entity khác Data Object

Rất nhiều lập trình viên nhầm.

## Data Object

Chỉ chứa dữ liệu:
    
    
    class UserDTO:
    
        name: str
        email: str

Không có behavior.

* * *

## Entity

Có:

  * Identity 
  * Behavior 
  * Business Rule 



Ví dụ:
    
    
    class User:
    
        def change_email(self, email):
            ...

* * *

DDD không thích Entity kiểu:
    
    
    class User:
    
        id
        name
        email

rồi bên ngoài:
    
    
    user_service.change_email(user)

Vì business logic nằm ngoài.

* * *

# 5\. Entity phải chứa hành vi

Sai:
    
    
    class BankAccount:
    
        balance: int

Bên ngoài:
    
    
    account.balance -= 100

Ai cũng có thể sửa.

* * *

Đúng:
    
    
    class BankAccount:
    
        def withdraw(self, amount):
    
            if amount > self.balance:
                raise Exception()
    
            self.balance -= amount

Entity tự bảo vệ trạng thái của nó.

* * *

# 6\. Identity trong Python

Python không tự ép Entity có ID.

Chúng ta phải thiết kế.

Ví dụ:
    
    
    from dataclasses import dataclass
    
    
    @dataclass
    class User:
    
        id: int
        name: str
        email: str

* * *

Nhưng có vấn đề.

Dataclass mặc định so sánh tất cả field:
    
    
    user1 = User(
        1,
        "Nam",
        "a@gmail.com"
    )
    
    user2 = User(
        1,
        "Nam",
        "b@gmail.com"
    )

Hai object khác email.

Python:
    
    
    user1 == user2

ra:
    
    
    False

Nhưng trong DDD:

Hai User này cùng identity:
    
    
    id=1

phải là cùng Entity.

* * *

# 7\. Entity Equality

DDD nói:

Entity so sánh bằng Identity.

Ví dụ:
    
    
    class User:
    
        def __init__(
            self,
            user_id,
            name,
            email
        ):
            self.id = user_id
            self.name = name
            self.email = email
    
    
        def __eq__(self, other):
    
            if not isinstance(other, User):
                return False
    
            return self.id == other.id

* * *

Bây giờ:
    
    
    user1 == user2

kết quả:
    
    
    True

vì:
    
    
    identity giống nhau

* * *

# 8\. Entity trong App Cào Truyện

Bây giờ áp dụng vào dự án của bạn.

Trong Reader Context:

Có:
    
    
    Novel

* * *

Không nên:
    
    
    class Novel:
    
        title
        author
        chapters
        cover
        crawl_url
        parser_version
        rating

Vì đây là một "God Entity".

* * *

Trong Reader Context:
    
    
    class Novel:
    
        id
        title
        chapters

* * *

Trong Crawler Context:
    
    
    class Novel:
    
        id
        source_url
        crawl_status

Hai Novel khác nhau.

Đây là điều chúng ta học ở Bounded Context.

* * *

# 9\. Tạo Novel Entity

Ví dụ:
    
    
    from dataclasses import dataclass
    
    
    @dataclass
    class Novel:
    
        id: int
        title: str
        completed: bool = False
    
    
        def rename(self, new_title):
    
            if not new_title:
                raise ValueError(
                    "Title cannot empty"
                )
    
            self.title = new_title
    
    
        def complete(self):
    
            self.completed = True

* * *

Sử dụng:
    
    
    novel = Novel(
        id=1,
        title="Đấu Phá Thương Khung"
    )
    
    
    novel.rename(
        "Đấu Phá Thương Khung 2"
    )
    
    
    novel.complete()

Đây là ngôn ngữ nghiệp vụ:
    
    
    rename()
    
    complete()

* * *

Không phải:
    
    
    novel.update()

* * *

# 10\. Entity bảo vệ Business Rule

Ví dụ:

Một Chapter:

Luật:
    
    
    Số chapter phải >= 1

* * *

Sai:
    
    
    chapter.number = -10

* * *

Đúng:
    
    
    class Chapter:
    
        def __init__(
            self,
            number,
            title
        ):
    
            if number < 1:
                raise ValueError(
                    "Invalid chapter"
                )
    
            self.number = number
            self.title = title

* * *

Entity không cho trạng thái sai tồn tại.

* * *

# 11\. Lifecycle của Entity

Entity thường có vòng đời.

Ví dụ Novel:
    
    
    Created
      |
      v
    Publishing
      |
      v
    Published
      |
      v
    Completed
      |
      v
    Archived

* * *

Không nên:
    
    
    novel.status = 5

* * *

Nên:
    
    
    novel.publish()
    
    novel.complete()
    
    novel.archive()

* * *

# 12\. Entity có thể có State Machine

Ví dụ:
    
    
    from enum import Enum
    
    
    class NovelStatus(Enum):
    
        DRAFT = "draft"
        PUBLISHED = "published"
        COMPLETED = "completed"
        ARCHIVED = "archived"

* * *

Entity:
    
    
    class Novel:
    
    
        def publish(self):
    
            if self.status != NovelStatus.DRAFT:
                raise Exception(
                    "Cannot publish"
                )
    
            self.status = (
                NovelStatus.PUBLISHED
            )

* * *

# 13\. Entity và Repository

Entity không tự lưu database.

Sai:
    
    
    class Novel:
    
        def save(self):
            database.insert(...)

Vì:

Domain phụ thuộc Infrastructure.

* * *

Đúng:
    
    
    novel.complete()
    
    repository.save(novel)

* * *

Luồng:
    
    
    Application
    
    ↓
    
    Entity
    
    ↓
    
    Repository
    
    ↓
    
    Database

* * *

# 14\. Entity và Immutable?

Value Object thường immutable.

Entity thì thường mutable.

Ví dụ:

User:
    
    
    user.change_email()

Novel:
    
    
    novel.rename()

Có thay đổi trạng thái.

Đó là đặc điểm Entity.

* * *

# 15\. Entity trong Clean Architecture

Kết hợp:
    
    
    domain/
    
        entities/
    
            novel.py
    
            chapter.py
    
            reader.py
    
        repositories/
    
            novel_repository.py

* * *

Entity nằm ở trung tâm:
    
    
            Domain
    
               |
         --------------
         |            |
     Entity      Repository

* * *

# 16\. Ví dụ hoàn chỉnh: Novel Entity
    
    
    from dataclasses import dataclass
    from enum import Enum
    
    
    class NovelStatus(Enum):
    
        DRAFT = "draft"
        PUBLISHED = "published"
        COMPLETED = "completed"
    
    
    
    @dataclass
    class Novel:
    
        id: int
        title: str
        status: NovelStatus
    
    
        def publish(self):
    
            if self.status != NovelStatus.DRAFT:
                raise ValueError(
                    "Only draft can publish"
                )
    
            self.status = (
                NovelStatus.PUBLISHED
            )
    
    
        def complete(self):
    
            if self.status != NovelStatus.PUBLISHED:
                raise ValueError(
                    "Only published can complete"
                )
    
            self.status = (
                NovelStatus.COMPLETED
            )
    
    
        def rename(self, title):
    
            if len(title.strip()) == 0:
                raise ValueError(
                    "Empty title"
                )
    
            self.title = title

* * *

Sử dụng:
    
    
    novel = Novel(
        id=1,
        title="Truyện A",
        status=NovelStatus.DRAFT
    )
    
    
    novel.publish()
    
    novel.complete()

Đây là Domain Model đúng tinh thần DDD.

* * *

# 17\. Entity Checklist

Một Entity tốt:

✅ Có Identity
    
    
    id

* * *

✅ Có Behavior
    
    
    publish()
    
    borrow()
    
    withdraw()

* * *

✅ Bảo vệ Business Rule
    
    
    if invalid:
        raise error

* * *

✅ Không biết Database

Không có:
    
    
    save()
    query()
    insert()

* * *

✅ Dùng ngôn ngữ nghiệp vụ

Không dùng:
    
    
    process()
    update()
    execute()

* * *

# 18\. Những lỗi phổ biến

## Lỗi 1: Entity chỉ là DTO
    
    
    class User:
        name
        email

Không có behavior.

* * *

## Lỗi 2: Business Logic nằm trong Service
    
    
    UserService.change_email()

mọi luật nằm ngoài User.

* * *

## Lỗi 3: Entity phụ thuộc Framework

Ví dụ:
    
    
    from sqlalchemy import Column

Domain bị khóa vào ORM.

* * *

## Lỗi 4: Entity quá lớn
    
    
    User

chứa:

  * Payment 
  * Order 
  * Notification 
  * Permission 
  * Address 
  * Profile 



Đây là dấu hiệu sai Bounded Context.

* * *

# Bài tập

## Bài 1

Thiết kế Entity:
    
    
    Book

cho hệ thống thư viện.

Yêu cầu:

  * Có id 
  * Có title 
  * Có trạng thái 
  * Có behavior: 


    
    
    borrow()
    return_book()

* * *

## Bài 2

Thiết kế Entity:
    
    
    Chapter

cho App Cào Truyện.

Business Rule:

  * Chapter number >= 1 
  * Không thể publish chapter 2 lần 



* * *

## Bài 3

Hãy phân biệt:

Cái nào là Entity?

  1. Email 
  2. User 
  3. Money 
  4. Novel 
  5. Address 
  6. Chapter 



* * *

# Tổng kết Buổi 6

Sau buổi này cần nhớ:

  * Entity là đối tượng có **Identity** , không chỉ là dữ liệu. 
  * Hai Entity giống dữ liệu nhưng khác ID là hai Entity khác nhau. 
  * Entity chứa **behavior + business rules**. 
  * Entity bảo vệ trạng thái hợp lệ của chính nó. 
  * Entity không chứa database code. 
  * Trong DDD, một Entity tốt đọc giống ngôn ngữ nghiệp vụ. 



* * *

Buổi tiếp theo (**Buổi 7**) chúng ta sẽ học **Value Object** — khái niệm đối lập với Entity. Bạn sẽ hiểu vì sao `Money`, `Email`, `Address`, `DateRange` không nên có ID, tại sao chúng nên immutable, và cách thiết kế Value Object chuẩn trong Python.

