# Buổi 8 — Query Builder Deep Dive

> Đây là buổi quan trọng nhất của tầng Repository. Sau buổi này chúng ta sẽ xây dựng **Query Builder** theo phong cách Fluent Interface, làm nền tảng cho toàn bộ hệ thống ORM của framework cào truyện.

Đây cũng là thành phần mà hầu hết các ORM lớn đều có:

* Django ORM
* SQLAlchemy
* Peewee
* Laravel Eloquent
* Doctrine

---

# Mục tiêu

Sau buổi này bạn sẽ xây dựng được:

```text
Novel.query()
     │
     ▼
 QueryBuilder
     │
     ├── select()
     ├── where()
     ├── or_where()
     ├── where_in()
     ├── order_by()
     ├── group_by()
     ├── having()
     ├── limit()
     ├── offset()
     ├── join()
     ├── first()
     ├── all()
     ├── count()
     └── delete()
```

Toàn bộ SQL sẽ được sinh tự động.

---

# Vì sao cần Query Builder?

Không dùng Query Builder:

```python
sql = """
SELECT *
FROM novel
WHERE author=?
AND status=?
ORDER BY updated_at DESC
LIMIT 20
"""

rows = db.query(sql, ("ABC", 1))
```

Mỗi truy vấn đều phải viết SQL.

Khó đọc.

Khó tái sử dụng.

---

Muốn viết

```python
rows = (
    Novel.query()
    .where(author="ABC")
    .where(status=1)
    .order_by("updated_at", desc=True)
    .limit(20)
    .all()
)
```

Dễ đọc hơn rất nhiều.

---

# Kiến trúc

```text
Application

      │

      ▼

QueryBuilder

      │

      ▼

SQLBuilder

      │

      ▼

DatabaseManager

      │

      ▼

SQLite
```

QueryBuilder không chạy SQL.

Nó chỉ xây dựng truy vấn.

---

# QueryBuilder là Immutable hay Mutable?

Có hai cách.

Mutable

```python
qb.where(...)
```

sửa chính object.

---

Immutable

```python
qb2 = qb.where(...)
```

tạo object mới.

---

Framework của chúng ta sẽ dùng **Mutable** vì:

* đơn giản
* dễ học
* nhanh

Sau này có thể chuyển sang Immutable.

---

# Thiết kế QueryBuilder

```python
class QueryBuilder:

    def __init__(

        self,

        repository

    ):

        self.repository = repository
```

---

Các thành phần

```text
QueryBuilder

select

where

join

order

group

having

limit

offset
```

---

# Lưu trạng thái

Ví dụ

```python
self._where = []

self._params = []

self._order = None

self._limit = None

self._offset = None
```

Builder chỉ lưu trạng thái.

---

# select()

Ví dụ

```python
Novel.query()

.select(

    "title",

    "author"

)
```

↓

```sql
SELECT

title,

author
```

---

Thiết kế

```python
def select(

    self,

    *fields

):

    self._select = list(fields)

    return self
```

---

# where()

Ví dụ

```python
.where(
    title="ABC"
)
```

↓

```sql
WHERE

title=?
```

---

Builder

```python
self._where.append(
    "title=?"
)

self._params.append(
    "ABC"
)
```

---

Hỗ trợ nhiều field

```python
.where(

    title="ABC",

    author="XYZ"
)
```

↓

```sql
WHERE

title=?

AND

author=?
```

---

Code

```python
for key, value in kwargs.items():

    self._where.append(

        f"{key}=?"

    )

    self._params.append(
        value
    )
```

---

# or_where()

Ví dụ

```python
.or_where(

    author="A"
)
```

↓

```sql
OR
```

---

Lưu

```python
("OR", sql)
```

---

Hoặc

```text
_where

↓

[
 ("AND",...),

 ("OR",...)
]
```

Đây là cách dễ mở rộng.

---

# Toán tử so sánh

Không chỉ

```sql
=
```

Cần

```text
>

<

>=

<=

!=

LIKE
```

---

API

```python
.where(

    "rating",

    ">=",

    8
)
```

↓

```sql
rating>=?
```

---

Hoặc

```python
.where_gt(

    rating=8
)
```

Tùy thiết kế.

---

# where_in()

Ví dụ

```python
.where_in(

    "id",

    [1,2,3]
)
```

↓

```sql
id

IN

(

?,

?,

?

)
```

---

Builder

```python
placeholders = ",".join(
    "?"
)
```

---

Params

```python
1

2

3
```

---

# where_like()

Ví dụ

```python
.where_like(

    "title",

    "%đấu%"
)
```

↓

```sql
LIKE
```

---

# order_by()

Ví dụ

```python
.order_by(

    "updated_at"
)
```

↓

```sql
ORDER BY

updated_at
```

---

DESC

```python
.order_by(

    "updated_at",

    desc=True
)
```

↓

```sql
DESC
```

---

# group_by()

Ví dụ

```python
.group_by(

    "author"
)
```

↓

```sql
GROUP BY
```

---

# having()

Ví dụ

```python
.group_by("author")

.having(

    "COUNT(*)",

    ">",

    10
)
```

↓

```sql
HAVING
```

---

# limit()

```python
.limit(
    20
)
```

↓

```sql
LIMIT 20
```

---

# offset()

```python
.offset(
    100
)
```

↓

```sql
OFFSET 100
```

---

# Pagination

```python
.page(
    3,

    20
)
```

↓

```text
LIMIT 20

OFFSET 40
```

---

# join()

Ví dụ

```python
.join(

    "author",

    "novel.author_id=author.id"
)
```

↓

```sql
INNER JOIN
```

---

LEFT JOIN

```python
.left_join(...)
```

↓

```sql
LEFT JOIN
```

---

# Sinh SQL

Builder

↓

```text
SELECT

↓

FROM

↓

JOIN

↓

WHERE

↓

GROUP

↓

HAVING

↓

ORDER

↓

LIMIT

↓

OFFSET
```

---

Ví dụ

```python
sql = []

sql.append(...)
```

Cuối cùng

```python
"\n".join(sql)
```

---

# Lazy SQL Generation

Điều quan trọng.

Builder KHÔNG sinh SQL ngay.

Ví dụ

```python
Novel.query()

.where(...)
```

Chỉ lưu:

```text
where

params
```

---

Đến

```python
.all()
```

mới sinh SQL.

---

Đó gọi là

```text
Lazy Evaluation
```

---

# all()

```python
.all()
```

↓

```text
build_sql()

↓

DatabaseManager.query()

↓

rows

↓

mapper

↓

models
```

---

# first()

```python
.first()
```

↓

Tự thêm

```sql
LIMIT 1
```

---

Trả về

```python
Novel
```

hoặc

```python
None
```

---

# count()

```python
.count()
```

↓

```sql
SELECT COUNT(*)
```

Không load Model.

---

# delete()

Ví dụ

```python
Novel.query()

.where(

    status=0

)

.delete()
```

↓

```sql
DELETE
```

---

# update()

Ví dụ

```python
Novel.query()

.where(

    id=10

)

.update(

    status=1
)
```

↓

```sql
UPDATE
```

---

# Query Clone

Ví dụ

```python
base = Novel.query()

active = base.where(status=1)

popular = base.where(rating=10)
```

Nếu Mutable sẽ bị lỗi.

Sau này nên hỗ trợ:

```python
clone()
```

để sao chép trạng thái truy vấn.

---

# SQL Injection

Sai

```python
sql = (

"WHERE title='"

+ title

+ "'"

)
```

---

Đúng

```python
WHERE

title=?
```

↓

params.

QueryBuilder tuyệt đối **không nối dữ liệu người dùng vào SQL**.

---

# Kiến trúc hoàn chỉnh

```text
Novel.query()

      │

      ▼

QueryBuilder

      │

build()

      │

      ▼

SQL

      │

      ▼

DatabaseManager

      │

      ▼

SQLite

      │

      ▼

Rows

      │

      ▼

Mapper

      │

      ▼

Model
```

---

# Áp dụng cho Framework Cào Truyện

Ví dụ

Tìm truyện

```python
Novel.query()

.where(

    source="truyenfull"

)

.where(

    status="completed"

)

.order_by(

    "updated_at",

    desc=True

)

.limit(

    50

)

.all()
```

Không cần SQL.

---

Tìm chapter

```python
Chapter.query()

.where(

    novel_id=100

)

.order_by(

    "chapter_no"

)

.all()
```

---

Search

```python
Novel.query()

.where_like(

    "title",

    "%đấu%"

)

.limit(

    20

)

.all()
```

---

# Tách QueryBuilder thành nhiều lớp

Khi framework lớn lên, không nên để một lớp làm mọi việc.

```text
orm/
│
├── query/
│     ├── builder.py
│     ├── compiler.py
│     ├── expressions.py
│     ├── conditions.py
│     ├── joins.py
│     ├── ordering.py
│     ├── pagination.py
│     └── result_mapper.py
│
├── repository/
├── model/
└── database/
```

`QueryBuilder` chỉ lưu trạng thái, còn `SQLCompiler` chịu trách nhiệm biến trạng thái thành SQL. Thiết kế này dễ mở rộng cho nhiều hệ quản trị cơ sở dữ liệu.

---

# Bài tập thực hành

## Bài 1

Xây dựng `QueryBuilder` hỗ trợ:

* `select()`
* `where()`
* `order_by()`
* `limit()`
* `offset()`

---

## Bài 2

Viết `build_sql()` sinh câu lệnh `SELECT` hoàn chỉnh.

---

## Bài 3

Thêm:

* `where_in()`
* `where_like()`
* `where(operator=...)`

để hỗ trợ nhiều điều kiện hơn.

---

## Bài 4

Cài đặt:

* `all()`
* `first()`
* `count()`

và dùng `Repository` để ánh xạ kết quả thành `Model`.

---

## Bài 5

Tách phần sinh SQL sang `SQLCompiler` và để `QueryBuilder` chỉ quản lý trạng thái truy vấn.

---

# Buổi tiếp theo

**Buổi 9 — Expression Tree & SQL AST Deep Dive**

Đây là buổi nâng cấp Query Builder lên kiến trúc của các ORM chuyên nghiệp. Chúng ta sẽ không còn lưu điều kiện dưới dạng chuỗi mà xây dựng **Expression Tree (AST)**.

Nội dung sẽ gồm:

* `Expression`
* `BinaryExpression`
* `ComparisonExpression`
* `LogicalExpression`
* `Column`
* `Value`
* `Function`
* `Alias`
* `OrderExpression`
* `Expression Compiler`

Sau buổi này, Query Builder của bạn sẽ có khả năng biểu diễn và tối ưu các truy vấn phức tạp, hỗ trợ mở rộng sang nhiều hệ quản trị cơ sở dữ liệu mà không cần thay đổi API phía người dùng.
