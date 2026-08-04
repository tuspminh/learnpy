# Buổi 7 — Repository Pattern Deep Dive

> Đây là buổi quan trọng nhất sau **Model**. Sau buổi này chúng ta sẽ hoàn thành tầng Repository của framework cào truyện.

Trong kiến trúc mà chúng ta đang xây dựng:

```
Application
      │
      ▼
Service Layer
      │
      ▼
Repository
      │
      ▼
DatabaseManager
      │
      ▼
SQLite
```

Từ bây giờ **mọi truy cập database đều phải đi qua Repository**.

---

# Mục tiêu

Sau buổi này bạn sẽ xây dựng được:

```text
                          Repository

      ┌─────────────────────────────────────────────┐
      │                                             │
      ▼                                             ▼
 BaseRepository<T>                        Custom Repository
      │                                             │
      ▼                                             ▼
CRUD Engine                           NovelRepository
Mapping                               ChapterRepository
SQL Builder                           AuthorRepository
Transaction                           CategoryRepository

                    │
                    ▼

              DatabaseManager

                    │
                    ▼

                  SQLite
```

Đây là kiến trúc mà Django ORM, Peewee và rất nhiều ORM hiện đại đều áp dụng (dù cách triển khai khác nhau).

---

# Repository Pattern là gì?

Repository là lớp **đóng gói toàn bộ logic truy cập dữ liệu**.

Thay vì:

```python
conn.execute(...)
```

hoặc

```python
cursor.execute(...)
```

khắp chương trình.

Ta chỉ dùng:

```python
novel_repo.find_by_id(10)
```

---

# Repository không làm gì?

Repository KHÔNG:

* validate business
* crawl web
* xử lý UI
* render dữ liệu

Repository chỉ:

> Đọc và ghi Model.

---

# Thiết kế BaseRepository

```text
BaseRepository

├── insert()

├── update()

├── delete()

├── save()

├── find_by_id()

├── find_one()

├── find_all()

├── count()

└── exists()
```

---

# Generic Repository

Ta không muốn

```python
NovelRepository

ChapterRepository

AuthorRepository
```

đều viết lại CRUD.

Ta dùng Generic.

```python
from typing import Generic, TypeVar

T = TypeVar("T")
```

---

Repository

```python
class BaseRepository(Generic[T]): ...
```

Sau này

```python
class NovelRepository(BaseRepository[Novel]):
    pass
```

---

# Repository biết Model nào?

Constructor

```python
class BaseRepository:
    def __init__(self, database, model):

        self.database = database

        self.model = model
```

---

Ví dụ

```python
repo = BaseRepository(db, Novel)
```

---

# INSERT

Model

```python
Novel

↓

fields
```

↓

SQL

```sql
INSERT INTO novel(...)
VALUES(...)
```

---

Builder

```python
fields = []
```

↓

```python
values = []
```

↓

```python
params = []
```

---

Ví dụ

Model

```python
title

author
```

↓

```sql
INSERT INTO novel(

title,

author

)

VALUES(

?,

?

)
```

---

Repository

```python
sql = ...

params = ...
```

↓

```python
db.execute(sql, params)
```

---

# UPDATE

Model

↓

Dirty Fields

↓

SQL

```sql
UPDATE novel

SET

title=?,

author=?

WHERE id=?
```

---

Tận dụng

```python
model.__dirty__
```

đã xây ở Buổi 3.

---

Ví dụ

```python
for field in model.__dirty__:
```

↓

chỉ update field đó.

---

Lợi ích

Nếu model có

```
50 field
```

chỉ sửa

```
title
```

↓

SQL

```sql
UPDATE

SET title=?
```

Không update cả 50 cột.

---

# DELETE

Repository

```python
delete(obj)
```

↓

```sql
DELETE
```

↓

```python
WHERE id=?
```

---

Hoặc

```python
delete_by_id(100)
```

---

# SAVE

Đây là hàm quan trọng nhất.

```python
repo.save(novel)
```

↓

Nếu

```text
id=None
```

↓

INSERT

---

Nếu

```text
id=20
```

↓

UPDATE

---

Ví dụ

```python
if obj.id is None:
    insert()

else:
    update()
```

---

# FIND BY ID

```python
find_by_id(10)
```

↓

```sql
SELECT *

FROM novel

WHERE id=?
```

---

Kết quả

↓

Model.

---

# Mapping Row → Model

SQLite

↓

```python
sqlite3.Row
```

↓

Model

---

Ví dụ

```python
row

↓

Novel()
```

---

Repository

```python
obj = self.model()
```

---

Sau đó

```python
for field in ...

    setattr(...)
```

---

Trả về

```python
Novel
```

không phải dict.

---

# Mapping Model → SQL

Ngược lại

```text
Model

↓

metadata

↓

params
```

---

Ví dụ

```python
Novel
```

↓

```python
[title, author, slug]
```

↓

```python
execute(sql, params)
```

---

# find_all()

```python
repo.find_all()
```

↓

```sql
SELECT *

FROM novel
```

↓

List

```python
[Novel(), Novel(), ...]
```

---

# find_one()

Ví dụ

```python
repo.find_one(title="ABC")
```

↓

```sql
WHERE

title=?
```

↓

Model.

---

Có thể thiết kế:

```python
find_one(**kwargs)
```

---

# exists()

```python
repo.exists(slug="abc")
```

↓

```sql
SELECT 1
```

↓

True

False

---

# count()

```python
repo.count()
```

↓

```sql
SELECT COUNT(*)
```

---

# Pagination

Crawler

↓

100000 truyện

Không thể

```python
find_all()
```

---

Repository

```python
find_page(page, size)
```

↓

```sql
LIMIT

OFFSET
```

---

Ví dụ

```sql
LIMIT 100

OFFSET 300
```

---

# Batch Insert

Crawler

↓

100 chapter

---

Không nên

```python
insert()
```

100 lần.

---

Dùng

```python
executemany()
```

↓

Nhanh hơn rất nhiều.

---

# Repository Lifecycle

save()

↓

before_validate()

↓

validate()

↓

before_save()

↓

INSERT

↓

after_save()

Repository là nơi điều phối lifecycle mà ta đã xây ở Buổi 2.

---

# Repository hoàn chỉnh

```text
Repository

│

├── insert()

├── update()

├── save()

├── delete()

├── delete_by_id()

├── find_by_id()

├── find_one()

├── find_all()

├── exists()

├── count()

├── page()

├── batch_insert()

└── map_row()
```

---

# Repository cho Framework Cào Truyện

Ví dụ

```
repository/

    base_repository.py

    novel_repository.py

    chapter_repository.py

    author_repository.py

    category_repository.py

    source_repository.py

    crawler_job_repository.py

    settings_repository.py
```

---

NovelRepository

Ngoài CRUD.

Có thể thêm

```python
find_by_slug()

find_by_author()

latest()

popular()

search()
```

---

ChapterRepository

```python
find_by_novel()

last_chapter()

chapter_count()

missing_chapters()
```

---

CrawlerJobRepository

```python
running_jobs()

failed_jobs()

pending_jobs()
```

---

Đó là Repository chuyên biệt.

---

# Không viết SQL trong UI

Sai

```python
cursor.execute(...)
```

ở PySide6.

---

Đúng

```python
repo.find_all()
```

UI không biết SQLite.

---

# Không viết SQL trong Spider

Sai

```python
crawler

↓

sqlite
```

---

Đúng

```python
crawler

↓

NovelRepository

↓

DatabaseManager
```

Spider chỉ tạo Model.

Repository lo lưu.

---

# Kiến trúc sau Buổi 7

```text
                    Service

                       │

                       ▼

                NovelRepository

                       │

             BaseRepository<T>

                       │

             DatabaseManager

                       │

                 sqlite3

                       │

                 SQLite File
```

---

# Kiến trúc cho dự án của bạn

```
src/

    core/

        database/

            database_manager.py

            registry.py

        orm/

            model.py

            field.py

            metadata.py

            repository.py

            schema_builder.py

    repositories/

        novel_repository.py

        chapter_repository.py

        author_repository.py

        category_repository.py

        source_repository.py

        crawler_job_repository.py
```

Đây là cấu trúc đủ lớn để phát triển thành framework ORM riêng.

---

# Những cải tiến nên có

Thay vì để `BaseRepository` tự sinh SQL bằng cách nối chuỗi, hãy tách riêng một lớp:

```text
Repository
      │
      ▼
SQLBuilder
      │
      ▼
DatabaseManager
```

Điều này giúp:

* Repository chỉ điều phối CRUD.
* SQLBuilder chịu trách nhiệm sinh SQL.
* Dễ hỗ trợ SQLite hôm nay, PostgreSQL hoặc MySQL trong tương lai.

Ngoài ra, Repository nên luôn làm việc với transaction khi thực hiện nhiều thao tác liên quan:

```python
with db.transaction():
    novel_repo.save(novel)
    chapter_repo.batch_insert(chapters)
```

---

# Bài tập thực hành

## Bài 1

Viết `BaseRepository[T]` với các phương thức:

* `insert()`
* `update()`
* `delete()`
* `save()`

---

## Bài 2

Viết bộ mapper:

* `row_to_model(row)`
* `model_to_params(model)`

để chuyển đổi hai chiều giữa `sqlite3.Row` và `Model`.

---

## Bài 3

Viết các phương thức truy vấn:

* `find_by_id()`
* `find_one(**kwargs)`
* `find_all()`
* `exists(**kwargs)`
* `count()`

---

## Bài 4

Thêm:

* `find_page(page, page_size)`
* `batch_insert(models)`

và tối ưu bằng `executemany()`.

---

## Bài 5

Tạo các repository chuyên biệt:

* `NovelRepository`
* `ChapterRepository`

Trong đó:

* `NovelRepository.find_by_slug(slug)`
* `NovelRepository.search(keyword)`
* `ChapterRepository.find_by_novel(novel_id)`
* `ChapterRepository.chapter_count(novel_id)`

---

# Buổi tiếp theo

**Buổi 8 — Query Builder Deep Dive**

Đây là buổi chúng ta sẽ loại bỏ việc viết SQL thủ công bằng cách xây dựng một **Query Builder** theo phong cách Fluent Interface:

```python
(
    Novel.query()
    .where(title="Đấu Phá")
    .where(author="Thiên Tàm")
    .order_by("updated_at", desc=True)
    .limit(20)
    .offset(40)
    .all()
)
```

Chúng ta sẽ xây dựng:

* Fluent Interface
* `where()`, `or_where()`
* `order_by()`
* `limit()`, `offset()`
* `select()`
* `join()`
* `group_by()`
* `having()`
* `count()`
* Lazy SQL generation
* Parameter Binding (`?`) để chống SQL Injection

Sau buổi này, framework của bạn sẽ có một tầng truy vấn hiện đại, dễ mở rộng và gần với trải nghiệm của các ORM chuyên nghiệp.
