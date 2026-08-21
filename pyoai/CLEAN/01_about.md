# Buổi 1 — Clean Architecture là gì?

Hôm nay chúng ta **chưa code nhiều**. Mục tiêu là thay đổi cách bạn nhìn một project Python.

Sau buổi này, bạn phải hiểu được:

* Architecture thực sự là gì?
* Vì sao một project chạy đúng vẫn có thể có architecture tệ?
* Coupling và Cohesion là gì?
* Dependency là gì?
* Vì sao Clean Architecture quan tâm đến **hướng dependency**?
* "Framework độc lập", "Database độc lập" nghĩa là gì?
* Clean Architecture thực sự đang bảo vệ điều gì?

---

# 1. Trước hết: Architecture là gì?

Khi mới học Python, chúng ta thường nghĩ architecture là:

```text
project/
├── models/
├── services/
├── repositories/
├── controllers/
└── utils/
```

Đây **không phải bản chất của architecture**.

Đó chỉ là **cách tổ chức code**.

Architecture thực sự trả lời những câu hỏi như:

> Nếu tôi thay SQLite bằng PostgreSQL thì phần nào phải thay đổi?

> Nếu tôi bỏ CLI và chuyển sang FastAPI thì business logic có phải viết lại không?

> Nếu tôi bỏ PySide6 và dùng Flet thì domain có bị ảnh hưởng không?

> Nếu API bên ngoài thay đổi thì phần nào bị ảnh hưởng?

> Nếu database chết thì business rule có thể test được không?

Đây mới là architectural questions.

---

# 2. Một ví dụ Python rất quen thuộc

Giả sử chúng ta xây ứng dụng quản lý truyện.

Ban đầu bạn viết:

```python
import sqlite3


def create_story(title: str):
    if not title:
        raise ValueError("Title cannot be empty")

    conn = sqlite3.connect("story.db")

    conn.execute(
        "INSERT INTO stories(title) VALUES (?)",
        (title,),
    )

    conn.commit()
    conn.close()
```

Code này:

* chạy được
* đơn giản
* dễ hiểu
* thậm chí có thể đưa production

Nhưng architecture có vấn đề.

Tại sao?

Vì một function đang làm quá nhiều việc:

```text
create_story()
    │
    ├── Business Rule
    │     └── title không được empty
    │
    ├── Database
    │     └── sqlite3
    │
    ├── SQL
    │
    └── Transaction
```

Business logic bị dính trực tiếp vào SQLite.

---

# 3. Vấn đề xuất hiện khi requirement thay đổi

Giả sử ngày mai:

```text
SQLite
   ↓
PostgreSQL
```

Bạn phải sửa:

```python
sqlite3.connect(...)
```

Nếu code có hàng trăm function kiểu này thì sao?

Rất khó.

---

Hoặc:

```text
CLI
 ↓
FastAPI
```

Bạn muốn:

```http
POST /stories
```

thay cho:

```bash
story create "One Piece"
```

Nếu business logic nằm trong CLI command thì bạn lại phải copy logic sang API.

---

Hoặc:

```text
PySide6
   ↓
Flet
```

Nếu logic nằm trong button callback:

```python
def on_create_clicked():
    ...
```

thì UI trở thành nơi chứa business rules.

Đây chính là thứ Clean Architecture muốn tránh.

---

# 4. Coupling

Một khái niệm cực kỳ quan trọng.

**Coupling = mức độ phụ thuộc giữa các thành phần.**

Ví dụ:

```text
StoryService
      │
      ▼
   SQLite
```

`StoryService` phụ thuộc trực tiếp vào SQLite.

Ta nói:

```text
StoryService
    ↓
SQLite
```

có coupling.

Nếu:

```python
class StoryService:

    def create(self, title):
        conn = sqlite3.connect("story.db")
```

thì `StoryService` biết:

* SQLite tồn tại
* connection hoạt động thế nào
* database filename
* SQL
* transaction

Nó biết quá nhiều về infrastructure.

---

# 5. Coupling cao

Ví dụ:

```python
class StoryService:

    def create(self, title):
        conn = sqlite3.connect("story.db")

        conn.execute(
            "INSERT INTO stories(title) VALUES (?)",
            (title,),
        )

        conn.commit()
```

Ta có:

```text
StoryService
      │
      ├── sqlite3
      ├── SQL
      ├── connection
      └── transaction
```

Nếu đổi database:

```text
SQLite
  ↓
PostgreSQL
```

`StoryService` bị ảnh hưởng.

Đây gọi là **high coupling**.

---

# 6. Cohesion

Ngược lại với coupling là một khái niệm rất quan trọng:

**Cohesion = các thành phần trong cùng một module có liên quan chặt chẽ với nhau đến mức nào.**

Ví dụ tốt:

```python
class Email:
    ...
```

chứa logic liên quan đến email.

Tốt.

Nhưng:

```python
class Utils:
    validate_email()
    resize_image()
    calculate_tax()
    connect_database()
    send_email()
    parse_html()
```

Đây là một module có cohesion rất thấp.

Nó giống một cái túi:

```text
utils.py
   │
   ├── random thing
   ├── another thing
   ├── another thing
   └── ...
```

---

# 7. Mục tiêu kiến trúc

Một architecture tốt thường hướng tới:

```text
HIGH COHESION
+
LOW COUPLING
```

Nói đơn giản:

> Những thứ có cùng trách nhiệm nên ở gần nhau.

và:

> Những thứ không cần biết về nhau thì đừng để chúng phụ thuộc trực tiếp vào nhau.

---

# 8. Dependency là gì?

Trong Python, dependency rất dễ thấy.

```python
import sqlite3
```

Function/class của bạn đang phụ thuộc vào:

```text
sqlite3
```

Ví dụ:

```python
class StoryRepository:

    def __init__(self):
        self.connection = sqlite3.connect("story.db")
```

Ta có:

```text
StoryRepository
       │
       ▼
    sqlite3
```

Nhưng dependency không chỉ là `import`.

Ví dụ:

```python
class StoryService:

    def create(self, repository):
        repository.save(...)
```

`StoryService` phụ thuộc vào khái niệm:

```text
repository
```

Đây là **conceptual dependency**.

---

# 9. Một câu hỏi rất quan trọng

Giả sử:

```text
Business Rule
     ↓
SQLite
```

và:

```text
Business Rule
     ↓
HTTP API
```

Điều gì xảy ra nếu SQLite thay đổi?

Business rule bị ảnh hưởng.

Điều gì xảy ra nếu API thay đổi?

Business rule bị ảnh hưởng.

Điều đó nghĩa là:

> **Chi tiết bên ngoài đang điều khiển business logic.**

Clean Architecture muốn đảo ngược điều này.

---

# 10. Stable vs Volatile

Một trong những tư duy quan trọng nhất của Clean Architecture là phân biệt:

### Stable

Những thứ tương đối ổn định:

```text
Business Rules
Domain
Use Cases
```

### Volatile

Những thứ thường xuyên thay đổi:

```text
Database
Web framework
GUI framework
HTTP library
CLI framework
External API
File system
```

Ví dụ:

```text
Domain

Story
Book
Author
Chapter
```

thường ổn định hơn:

```text
SQLite
PostgreSQL
MongoDB
```

---

# 11. Tại sao database không nên nằm ở trung tâm?

Một architecture truyền thống rất dễ trở thành:

```text
             DATABASE
                 ↑
                 │
        ┌────────┴────────┐
        │                 │
      Service           API
        │                 │
        └────────┬────────┘
                 │
                UI
```

Mọi thứ xoay quanh database.

Đây là **database-centric architecture**.

Khi đó developer thường bắt đầu suy nghĩ:

> Database schema là model của application.

Nhưng điều này không nhất thiết đúng.

---

# 12. Domain mới là trung tâm

Clean Architecture muốn:

```text
              DOMAIN
                 ↑
                 │
           APPLICATION
                 ↑
                 │
       ┌─────────┴─────────┐
       │                   │
 DATABASE                WEB
       │                   │
       └───────┬───────────┘
               │
              UI
```

Hay hiểu theo dependency:

```text
Infrastructure ──────► Application ──────► Domain
```

Chúng ta sẽ học cực kỳ kỹ vấn đề này ở **Buổi 2 — Dependency Rule**.

---

# 13. Clean Architecture không phải chỉ có 4 folder

Bạn sẽ thường thấy:

```text
domain/
application/
infrastructure/
presentation/
```

Nhưng đừng hiểu:

> "Clean Architecture = 4 folders."

Không phải.

Bạn có thể có:

```text
src/
├── domain/
├── application/
├── infrastructure/
└── presentation/
```

nhưng vẫn có architecture rất tệ.

Ví dụ:

```python
# domain/story.py

import sqlite3
import requests
from fastapi import HTTPException
```

Folder đúng.

Architecture sai.

Tại sao?

Vì:

```text
Domain
 ├── SQLite
 ├── requests
 └── FastAPI
```

Domain đang phụ thuộc vào outer details.

---

# 14. Clean Architecture bảo vệ Business Rules

Đây là câu quan trọng nhất của Buổi 1:

> **Clean Architecture tồn tại để bảo vệ business rules khỏi những chi tiết dễ thay đổi.**

Ví dụ hệ thống truyện của chúng ta có rule:

```text
Một Story phải có title.
Một Chapter phải thuộc một Story.
Chapter phải có số thứ tự > 0.
Không được publish Story chưa có chapter.
```

Đó là business rules.

Chúng ta không muốn những rule này phụ thuộc vào:

```text
SQLite
HTTP
BeautifulSoup
Playwright
PySide6
Flet
Typer
FastAPI
```

---

# 15. Ví dụ kiến trúc tốt hơn

Thay vì:

```python
def create_story(title):
    conn = sqlite3.connect(...)
    conn.execute(...)
```

ta bắt đầu suy nghĩ:

```text
                CreateStory
                    │
                    ▼
                 Domain
                    │
                    ▼
              Repository
                    │
                    ▼
                 SQLite
```

Trong đó:

```text
CreateStory
```

không cần biết SQLite tồn tại.

Nó chỉ biết:

```text
StoryRepository
```

---

# 16. Dependency Inversion bắt đầu xuất hiện

Ta có thể định nghĩa abstraction:

```python
from typing import Protocol


class StoryRepository(Protocol):

    def save(self, story):
        ...
```

Use Case:

```python
class CreateStory:

    def __init__(self, repository: StoryRepository):
        self.repository = repository

    def execute(self, title: str):
        ...
```

SQLite implementation:

```python
class SQLiteStoryRepository:

    def save(self, story):
        ...
```

Bây giờ:

```text
CreateStory
     │
     ▼
StoryRepository
     ▲
     │
SQLiteStoryRepository
```

Đây là một bước cực kỳ quan trọng.

---

# 17. Control Flow vs Dependency

Một điểm rất hay của Clean Architecture:

**Control flow** có thể đi từ ngoài vào trong.

Ví dụ:

```text
CLI
 ↓
Controller
 ↓
Use Case
 ↓
Repository
 ↓
SQLite
```

Nhưng **dependency direction** không nhất thiết đi như vậy.

Ta muốn:

```text
Infrastructure
      ↓
Application
      ↓
Domain
```

Tức là:

```text
Runtime flow:

CLI → Use Case → Repository → SQLite


Dependency:

SQLite implementation
        ↓
   Application
        ↓
      Domain
```

Đây là một trong những điểm khó nhất của Clean Architecture.

Buổi 2 chúng ta sẽ đào rất sâu vào nó.

---

# 18. Một ví dụ đời thường

Hãy tưởng tượng:

```text
Bạn
 ↓
Người giao hàng
 ↓
Kho
```

Bạn không cần biết kho dùng:

```text
Excel
MySQL
PostgreSQL
MongoDB
```

Bạn chỉ cần một contract:

```text
"Đơn hàng của tôi đã được xử lý."
```

Infrastructure có thể thay đổi.

Business expectation không nên thay đổi.

---

# 19. Framework Independence

Một architecture sạch không muốn:

```python
from fastapi import FastAPI
```

xuất hiện trong domain.

Tương tự:

```python
from PySide6.QtWidgets import QWidget
```

không nên xuất hiện trong domain.

Hay:

```python
import typer
```

không nên trở thành dependency của business logic.

Framework là **delivery mechanism**.

Ví dụ:

```text
             Business Logic
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
      CLI       FastAPI    PySide6
```

Một business rule có thể được gọi từ cả ba.

---

# 20. Database Independence

Tương tự:

```text
                 Application
                     │
                     ▼
             StoryRepository
                ▲    ▲    ▲
                │    │    │
             SQLite PG  Memory
```

Use Case không cần biết implementation nào.

Điều này đặc biệt hữu ích cho testing.

---

# 21. Testing là một hệ quả rất lớn

Nếu business logic phụ thuộc SQLite:

```text
Test
 ↓
SQLite
 ↓
Database setup
 ↓
Data cleanup
```

Test trở nên nặng.

Nhưng nếu:

```text
Use Case
   ↓
FakeRepository
```

ta có thể test rất nhanh.

Ví dụ:

```python
class InMemoryStoryRepository:

    def __init__(self):
        self.stories = []

    def save(self, story):
        self.stories.append(story)
```

Use Case không cần biết đây là:

```text
SQLite
```

hay:

```text
Memory
```

---

# 22. Architecture tốt giúp thay đổi dễ hơn

Hãy tưởng tượng project của chúng ta hôm nay:

```text
CLI
SQLite
requests
```

Ngày mai:

```text
FastAPI
PostgreSQL
httpx
```

Ngày kia:

```text
PySide6
Redis
Playwright
```

Nếu business logic bị trộn với infrastructure:

```text
Change
  ↓
Rewrite
```

Nếu architecture tốt:

```text
Change Infrastructure
        ↓
Replace Adapter
        ↓
Business Logic vẫn giữ nguyên
```

Đây là giá trị rất lớn.

---

# 23. Nhưng Clean Architecture không miễn phí

Đây là điều tôi muốn bạn hiểu ngay từ đầu.

Code:

```python
def create_story(title):
    sqlite3.connect(...)
```

rất ngắn.

Clean Architecture có thể thành:

```text
Story
StoryRepository
StoryRepositoryImpl
CreateStory
CreateStoryRequest
CreateStoryResponse
Controller
Mapper
Database
Factory
Composition Root
```

Rất nhiều code hơn.

Vậy tại sao dùng?

Vì architecture là **trade-off**.

Không phải project nào cũng cần Clean Architecture đầy đủ.

---

# 24. Khi nào không nên dùng Clean Architecture?

Ví dụ:

```text
hello.py
```

hoặc:

```text
convert_image.py
```

100 dòng.

Không cần:

```text
Domain
Application
Infrastructure
Repository
UseCase
DI
Factory
```

Nếu làm vậy thì bạn đang:

> **Over-engineering.**

---

# 25. Khi nào Clean Architecture đáng giá?

Khi project có:

```text
Business logic phức tạp
+
Nhiều interface
+
Nhiều infrastructure
+
Test nhiều
+
Project sống lâu
+
Nhiều developer
```

Ví dụ hệ thống crawler của bạn rất phù hợp:

```text
Crawler
Reading
Story
Chapter
Source
Queue
Worker
Database
CLI
GUI
HTTP
```

Có rất nhiều thứ có thể thay đổi.

Đó là lúc architecture trở nên quan trọng.

---

# 26. Bài tập 1

Cho đoạn code:

```python
import sqlite3


def register_user(username, password):

    if len(username) < 3:
        raise ValueError("Username too short")

    if len(password) < 8:
        raise ValueError("Password too short")

    conn = sqlite3.connect("app.db")

    conn.execute(
        "INSERT INTO users(username, password) VALUES (?, ?)",
        (username, password),
    )

    conn.commit()
    conn.close()
```

Hãy phân tích:

### Câu 1

Function này đang có bao nhiêu responsibility?

### Câu 2

Business rule nào đang nằm trong function?

### Câu 3

Infrastructure nào đang nằm trong function?

### Câu 4

Coupling nằm ở đâu?

### Câu 5

Nếu đổi:

```text
SQLite → PostgreSQL
```

thì phần nào bị ảnh hưởng?

### Câu 6

Nếu muốn sử dụng logic `register_user()` từ:

```text
CLI
FastAPI
PySide6
```

thì code hiện tại có vấn đề gì?

---

# 27. Bài tập 2 — tư duy architecture

Hãy tưởng tượng hệ thống:

```text
Story Application
```

Có các chức năng:

```text
Create Story
Add Chapter
Delete Chapter
Start Crawl
Pause Crawl
Resume Crawl
Read Chapter
```

Infrastructure:

```text
SQLite
HTTP
Playwright
File System
Redis
```

Presentation:

```text
CLI
PySide6
FastAPI
```

Hãy trả lời:

> Thành phần nào nên là **stable core**?

và:

> Thành phần nào nên là **volatile details**?

---

# 28. Bài tập 3 — quan trọng nhất

Đừng code.

Hãy vẽ dependency graph cho architecture sau:

```text
CLI
FastAPI
PySide6
   ↓
StoryService
   ↓
SQLite
```

Sau đó hãy suy nghĩ:

> Nếu tôi muốn thay SQLite bằng PostgreSQL mà không sửa `StoryService`, tôi cần thay đổi dependency như thế nào?

Đây chính là câu hỏi dẫn chúng ta sang **Buổi 2 — Dependency Rule Deep Dive**.

---

# 29. Tóm tắt Buổi 1

Bạn chỉ cần nhớ 7 ý:

```text
1. Architecture ≠ folder structure

2. Architecture quyết định dependency

3. Coupling thấp là tốt

4. Cohesion cao là tốt

5. Business rules nên ổn định

6. Database / Framework / UI là details

7. Clean Architecture bảo vệ business rules
   khỏi những details dễ thay đổi
```

Và câu quan trọng nhất:

> **Đừng hỏi "tôi nên tạo bao nhiêu folder?" Hãy hỏi "thành phần này được phép phụ thuộc vào thành phần nào?"**

**Buổi 2** chúng ta sẽ đi thẳng vào phần khó nhất: **Dependency Rule + Dependency Inversion + Dependency Direction**, rồi dùng Python `Protocol`, `ABC`, constructor injection để chứng minh bằng code tại sao kiến trúc có thể **đảo ngược dependency**.
