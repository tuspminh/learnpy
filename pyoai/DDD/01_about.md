# Domain-Driven Design Deep Dive — Buổi 1

## DDD là gì và tại sao CRUD bắt đầu thất bại?

Hôm nay **chưa viết nhiều code**. Mục tiêu là thay đổi cách bạn nhìn một hệ thống phần mềm.

Nếu hiểu đúng Buổi 1, những bài sau như Entity, Value Object, Aggregate, Repository, Domain Service... sẽ dễ hiểu hơn rất nhiều.

---

# 1. DDD là gì?

**Domain-Driven Design (DDD)** là phương pháp thiết kế phần mềm lấy **domain — nghiệp vụ thực tế** làm trung tâm.

Nói đơn giản:

> Đừng bắt đầu bằng "database có những bảng nào?"
> Hãy bắt đầu bằng "business của hệ thống hoạt động như thế nào?"

Ví dụ bạn muốn xây:

> Ứng dụng cào truyện và đọc truyện.

Một cách tiếp cận thông thường:

```text
Database
    ↓
Story table
Chapter table
Source table
User table
    ↓
CRUD API
```

DDD đi theo hướng:

```text
Business
   ↓
Domain
   ↓
Business Rules
   ↓
Domain Model
   ↓
Application
   ↓
Infrastructure
   ↓
Database
```

Đây là một sự thay đổi rất lớn về tư duy.

---

# 2. Domain là gì?

**Domain = lĩnh vực nghiệp vụ mà phần mềm đang giải quyết.**

Ví dụ:

| Phần mềm    | Domain               |
| ----------- | -------------------- |
| Banking     | Ngân hàng            |
| Shopee      | E-commerce           |
| Hospital    | Y tế                 |
| Airline     | Hàng không           |
| Netflix     | Streaming            |
| GitHub      | Software development |
| App của bạn | Crawling + Reading   |

Domain không phải:

```text
Python
SQLite
FastAPI
PySide6
Redis
Docker
```

Đó là **technology**.

Domain là:

```text
Story
Chapter
Author
Crawler
Reading
User
Bookmark
ReadingProgress
```

và quan trọng hơn:

```text
Story có thể được publish.

Chapter thuộc về Story.

Crawler có thể phát hiện chapter mới.

User có thể đánh dấu chapter đã đọc.

ReadingProgress được cập nhật khi user đọc.
```

Đó mới là domain.

---

# 3. Business Logic là gì?

Đây là khái niệm cực kỳ quan trọng.

Ví dụ:

```python
class Story:
    def __init__(self, title):
        self.title = title
        self.chapters = []
```

Code này chỉ chứa **data**.

Nhưng domain thật có các rule.

Ví dụ:

> Không được thêm chapter có số thứ tự đã tồn tại.

Hoặc:

> Chapter phải thuộc một Story.

Hoặc:

> Story đã bị deleted thì không được thêm chapter mới.

Hoặc:

> Chapter phải có số thứ tự lớn hơn 0.

Đó là **business rules**.

---

# 4. CRUD không sai

Đây là một điểm rất quan trọng.

DDD **không chống CRUD**.

CRUD hoàn toàn tốt khi domain đơn giản.

Ví dụ application:

```text
Todo
```

Có:

```text
Create Todo
Read Todo
Update Todo
Delete Todo
```

Business rule:

```text
Todo có title
Todo có completed
```

Thế là gần như đủ.

Không cần DDD phức tạp.

Bạn có thể viết:

```python
todo = Todo(
    title="Learn Python",
    completed=False,
)
```

Database:

```text
todos
-----
id
title
completed
```

CRUD rất phù hợp.

---

# 5. Vấn đề xuất hiện khi domain phức tạp

Hãy tưởng tượng ứng dụng crawler của bạn ban đầu rất đơn giản.

Database:

```text
stories
chapters
```

Code:

```python
def create_story(...):
    ...

def add_chapter(...):
    ...

def delete_story(...):
    ...
```

Ban đầu rất ổn.

Nhưng sau một thời gian requirements tăng.

---

## Requirement 1

Một Story có nhiều Chapter.

```text
Story
 ├── Chapter 1
 ├── Chapter 2
 └── Chapter 3
```

---

## Requirement 2

Không được phép duplicate chapter.

---

## Requirement 3

Crawler phải phát hiện chapter mới.

---

## Requirement 4

Nếu chapter đã tồn tại thì phải update.

---

## Requirement 5

Một số website đánh số:

```text
Chapter 1
Chapter 2
Chapter 3
```

nhưng website khác:

```text
Chương 1
Chương 2
Chương 3
```

---

## Requirement 6

Một website có thể đổi URL chapter.

---

## Requirement 7

Crawler có trạng thái:

```text
Pending
Running
Paused
Completed
Failed
```

và không phải trạng thái nào cũng được chuyển sang trạng thái khác.

Ví dụ:

```text
Pending → Running
Running → Paused
Paused → Running
Running → Completed
Running → Failed
```

nhưng:

```text
Completed → Running
```

có thể không hợp lệ.

---

## Requirement 8

Khi crawler phát hiện chapter mới:

```text
ChapterDetected
```

thì:

```text
Save Chapter
      ↓
Update Story
      ↓
Update statistics
      ↓
Notify UI
      ↓
Update search index
```

Lúc này CRUD bắt đầu trở nên khó kiểm soát.

---

# 6. Vấn đề lớn nhất của CRUD architecture

Một hệ thống CRUD thường dễ dẫn đến:

```text
Controller
    ↓
Service
    ↓
Repository
    ↓
Database
```

Nhưng business logic dần dần chui vào `Service`.

Ví dụ:

```python
def add_chapter(story_id, chapter_number, title):
    story = repo.get(story_id)

    if chapter_number <= 0:
        raise ValueError(...)

    if repo.chapter_exists(story_id, chapter_number):
        raise ValueError(...)

    if story.status == "deleted":
        raise ValueError(...)

    ...
```

Sau đó một ngày khác:

```python
def update_chapter(...):
    ...
```

lại có:

```python
if chapter_number <= 0:
    ...

if story.status == "deleted":
    ...

if chapter_exists:
    ...
```

Rồi crawler cũng có:

```python
if chapter_number <= 0:
    ...

if story.status == "deleted":
    ...
```

Logic bị copy.

---

# 7. Business logic bị phân tán

Sau một thời gian:

```text
API
 └── business logic

CLI
 └── business logic

Crawler
 └── business logic

Worker
 └── business logic

GUI
 └── business logic
```

Đây là vấn đề rất nguy hiểm.

Ví dụ CLI kiểm tra:

```python
if chapter_number > 0:
```

nhưng crawler quên kiểm tra.

GUI lại kiểm tra theo cách khác.

Kết quả:

```text
CLI      → rule A
GUI      → rule B
Crawler  → rule C
Worker   → rule D
```

Hệ thống mất tính nhất quán.

---

# 8. DDD muốn giải quyết điều gì?

DDD muốn đưa **business rules về gần domain objects**.

Ví dụ thay vì:

```python
if story.status == "deleted":
    raise ...
```

ở khắp nơi, ta muốn:

```python
story.add_chapter(chapter)
```

và:

```python
class Story:
    def add_chapter(self, chapter):
        ...
```

`Story` biết:

> Tôi có được phép thêm Chapter này hay không?

Đây chính là tư duy **Rich Domain Model**.

---

# 9. Anemic Domain Model

Một anti-pattern rất nổi tiếng:

```python
class Story:
    id: int
    title: str
    status: str
    chapters: list
```

Class chỉ chứa data.

Logic nằm bên ngoài:

```python
class StoryService:

    def add_chapter(self, story, chapter):
        ...
```

Đây gọi là:

> **Anemic Domain Model**

Domain object gần như chỉ là một túi dữ liệu.

---

# 10. Rich Domain Model

DDD thường hướng tới model giàu behavior hơn:

```python
class Story:

    def add_chapter(self, chapter):
        if self.is_deleted:
            raise StoryDeletedError()

        if self.has_chapter(chapter.number):
            raise ChapterAlreadyExistsError()

        self.chapters.append(chapter)
```

Bây giờ:

```python
story.add_chapter(chapter)
```

chứ không phải:

```python
story.chapters.append(chapter)
```

Sự khác biệt nằm ở đây.

---

# 11. Encapsulation trở nên cực kỳ quan trọng

Không nên để code bên ngoài tự do phá domain:

```python
story.chapters.append(chapter)
```

Vì bất kỳ code nào cũng có thể làm:

```python
story.chapters.append(None)
story.chapters.append(duplicate)
story.status = "whatever"
```

Thay vào đó:

```python
story.add_chapter(chapter)
```

Domain kiểm soát trạng thái của chính nó.

---

# 12. DDD không có nghĩa là "mọi thứ phải là class"

Một hiểu lầm phổ biến:

> "DDD = tạo thật nhiều class."

Không phải.

DDD quan tâm tới:

```text
Business
Business language
Business rules
Model
Boundaries
Consistency
Behavior
```

Python hoàn toàn có thể dùng:

```text
class
dataclass
Enum
function
Protocol
```

tùy trường hợp.

---

# 13. Strategic DDD và Tactical DDD

DDD có hai tầng rất quan trọng.

## Strategic DDD

Trả lời:

> Chúng ta đang xây hệ thống cho domain nào?

Các khái niệm:

```text
Domain
Subdomain
Core Domain
Bounded Context
Context Map
Ubiquitous Language
```

---

## Tactical DDD

Trả lời:

> Chúng ta model domain đó bằng code như thế nào?

Các khái niệm:

```text
Entity
Value Object
Aggregate
Aggregate Root
Repository
Domain Service
Domain Event
Factory
Specification
```

Có thể hình dung:

```text
Strategic DDD
       ↓
"Chúng ta nên chia domain như thế nào?"

       ↓

Tactical DDD
       ↓
"Chúng ta code domain đó như thế nào?"
```

---

# 14. Một sai lầm rất phổ biến

Nhiều người học DDD theo kiểu:

```text
Hôm nay học Entity
Ngày mai học Repository
Ngày kia học Aggregate
```

rồi tạo:

```text
StoryEntity
StoryRepository
StoryService
StoryFactory
StoryManager
StoryController
```

nhưng không hiểu:

> Tại sao Story lại là Aggregate?

Đó **không phải DDD**.

Đó chỉ là:

> Áp dụng pattern theo checklist.

DDD phải bắt đầu từ **domain**.

---

# 15. Ví dụ: ứng dụng cào truyện

Hãy tạm bỏ database.

Bây giờ tôi hỏi:

> Hệ thống của bạn thực sự quản lý cái gì?

Có thể trả lời:

```text
Story
Chapter
Source
Crawler
CrawlerJob
ReadingProgress
User
```

Nhưng đây mới chỉ là danh từ.

DDD tiếp tục hỏi:

> Chúng làm gì?

Ví dụ:

```text
Story
    publish()
    add_chapter()
    remove_chapter()

CrawlerJob
    start()
    pause()
    resume()
    complete()
    fail()

ReadingProgress
    mark_read()
    update_position()
```

Đây mới bắt đầu trở thành **domain model**.

---

# 16. Tư duy "nouns → verbs"

Đây là một kỹ thuật rất hữu ích khi học DDD.

Ban đầu:

```text
Story
Chapter
Crawler
User
```

Đây là **nouns**.

Tiếp tục tìm **verbs**:

```text
Story
 ├── publish
 ├── add chapter
 └── remove chapter

Crawler
 ├── start
 ├── pause
 ├── resume
 └── complete

User
 ├── bookmark
 ├── start reading
 └── mark chapter as read
```

DDD đặc biệt quan tâm tới **behavior**.

---

# 17. Domain Model không phải Database Model

Đây là một trong những điều quan trọng nhất của khóa học.

Database:

```text
stories
----------------
id
title
status
created_at
updated_at
```

Domain:

```python
class Story:
    def publish(self):
        ...

    def add_chapter(self, chapter):
        ...

    def archive(self):
        ...
```

Database hỏi:

> Dữ liệu gồm những cột gì?

Domain hỏi:

> Business object có thể làm gì?

Hai thứ này **liên quan nhưng không giống nhau**.

---

# 18. Domain không nên biết SQLite

Ví dụ domain:

```python
class Story:

    def add_chapter(self, chapter):
        ...
```

Không nên có:

```python
class Story:

    def save_to_sqlite(self):
        ...
```

hoặc:

```python
class Story:

    def execute_sql(self):
        ...
```

Vì SQLite là infrastructure.

Sau này bạn có thể chuyển:

```text
SQLite
    ↓
PostgreSQL
```

mà domain không cần biết.

---

# 19. Bức tranh kiến trúc lớn

Sau này chúng ta sẽ hướng tới:

```text
                 Interface
              /     |      \
            CLI     GUI     API
              \      |      /
               Application
                    |
                 Domain
                    |
             Infrastructure
                    |
             SQLite / Redis
```

Dependency nên hướng về:

```text
Domain
  ↑
Application
  ↑
Infrastructure
  ↑
Interface
```

Chứ không phải:

```text
Domain
   ↓
SQLite
```

---

# 20. Một ví dụ hoàn chỉnh nhỏ

Không cần framework.

```python
class Chapter:
    def __init__(self, number, title):
        if number <= 0:
            raise ValueError("Invalid chapter number")

        self.number = number
        self.title = title


class Story:
    def __init__(self, title):
        if not title.strip():
            raise ValueError("Story title cannot be empty")

        self.title = title
        self.chapters = []

    def add_chapter(self, chapter):
        if any(
            item.number == chapter.number
            for item in self.chapters
        ):
            raise ValueError("Chapter already exists")

        self.chapters.append(chapter)
```

Sử dụng:

```python
story = Story("One Piece")

story.add_chapter(
    Chapter(1, "Chapter 1")
)
```

Thay vì:

```python
story.chapters.append(
    Chapter(1, "Chapter 1")
)
```

Ta đang bắt đầu đưa business rule vào domain.

---

# 21. Nhưng code trên vẫn chưa phải DDD hoàn chỉnh

Đừng vội nghĩ:

> "Tôi viết Entity như vậy là xong DDD."

Chưa.

Chúng ta còn phải trả lời:

```text
Story có phải Entity không?

Chapter có phải Entity không?

Story có phải Aggregate không?

Chapter có thuộc Story Aggregate không?

StoryId là gì?

ChapterNumber có phải Value Object không?

Crawler có cùng Bounded Context với Story không?

CrawlerJob có nên thuộc Story Aggregate không?

Repository nằm ở đâu?

Transaction boundary ở đâu?
```

Những câu hỏi đó sẽ được giải quyết dần trong các buổi tiếp theo.

---

# 22. Tư duy quan trọng nhất hôm nay

Khi xây phần mềm, đừng hỏi ngay:

> "Tôi cần tạo table nào?"

Hãy hỏi:

> "Business đang vận hành như thế nào?"

Đừng hỏi:

> "Tôi cần class nào?"

Hãy hỏi:

> "Business entity nào tồn tại?"

Đừng hỏi:

> "Tôi cần API nào?"

Hãy hỏi:

> "User/business actor muốn thực hiện hành động gì?"

Đừng hỏi:

> "Service này nên có method gì?"

Hãy hỏi:

> "Business rule này thuộc về object nào?"

---

# 23. Bài tập Buổi 1

Với **ứng dụng cào truyện và đọc truyện**, hãy tự phân tích.

### Bài 1 — Domain

Liệt kê khoảng 10–15 khái niệm thuộc domain.

Ví dụ:

```text
Story
Chapter
...
```

### Bài 2 — Behavior

Với mỗi object, tìm các hành động:

```text
Story
    ?

Chapter
    ?

Crawler
    ?

CrawlerJob
    ?

ReadingProgress
    ?
```

### Bài 3 — Business Rules

Tìm ít nhất 10 business rules.

Ví dụ:

```text
1. Chapter number phải > 0.
2. Một Story không được có hai Chapter cùng number.
3. ...
```

### Bài 4 — Phân biệt

Giải thích tại sao các thứ sau **không phải Domain**:

```text
SQLite
PySide6
Redis
HTTP
BeautifulSoup
```

### Bài 5 — CRUD vs Domain

Giả sử có:

```python
def add_chapter(story_id, number, title):
    ...
```

Hãy suy nghĩ:

> Business rule nào nên nằm trong `add_chapter()` và business rule nào nên nằm trong `Story`?

---

# 24. Tóm tắt Buổi 1

Bạn cần nhớ 7 ý:

```text
1. Domain = lĩnh vực nghiệp vụ.

2. DDD lấy domain làm trung tâm.

3. CRUD không sai; CRUD chỉ không đủ
   khi business logic trở nên phức tạp.

4. Business rule phải có một nơi sở hữu rõ ràng.

5. Rich Domain Model tập trung behavior vào domain.

6. Domain Model ≠ Database Model.

7. DDD bắt đầu từ business,
   không bắt đầu từ database hay framework.
```

Buổi tiếp theo chúng ta sẽ đi vào **Buổi 2 — Domain Discovery**, nơi tôi sẽ hướng dẫn bạn phân tích ứng dụng cào truyện từ đầu để tìm ra **Domain → Subdomain → Core Domain → Supporting Domain → Generic Domain**.
