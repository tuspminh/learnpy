# Buổi 5 — SQL Schema Builder Deep Dive

> Đây là buổi đánh dấu bước chuyển từ **Model Framework** sang **ORM Framework**. Sau buổi này, model của chúng ta sẽ có khả năng **tự sinh SQL** giống như Django ORM, SQLAlchemy hay Peewee.

---

# Mục tiêu

Sau buổi này bạn sẽ xây dựng được:

```text
                 class Novel(Model)

                        │
                        ▼
                  Model Metadata

                        │
                        ▼
                 SQLSchemaBuilder

        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
   CREATE TABLE    CREATE INDEX     Constraints
        │               │                │
        └───────────────┼────────────────┘
                        ▼
                    SQLite SQL
                        │
                        ▼
                sqlite3.execute()
```

---

# Tại sao cần Schema Builder?

Giả sử model:

```python
class Novel(Model):
    id = IntegerField(primary_key=True)

    title = StringField(max_length=200, nullable=False)

    author = StringField()
```

Không muốn viết

```sql
CREATE TABLE novel(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT
);
```

thủ công.

Framework phải tự sinh.

---

# Metadata là nguồn dữ liệu

Field

```python
title = StringField(nullable=False, unique=True, default="", max_length=200)
```

↓

Metadata

```text
name = title

type = TEXT

nullable = False

unique = True

default = ""

max_length = 200
```

↓

Builder

↓

SQL

---

# Thiết kế SQLSchemaBuilder

```python
class SQLSchemaBuilder:
    def build(self, model):

        pass
```

---

Sử dụng

```python
builder = SQLSchemaBuilder()

sql = builder.build(Novel)

print(sql)
```

---

# Bước 1. Sinh tên bảng

Model

```python
Novel.__table_name__
```

↓

```text
novel
```

---

Builder

```python
table = model.__table_name__
```

---

SQL

```sql
CREATE TABLE novel
```

---

# Bước 2. Sinh từng cột

Model

```python
Novel.__fields__
```

↓

```text
id

title

author
```

---

Builder

```python
for field in model.__fields__.values():
    ...
```

---

# Bước 3. SQL Type

Field

```python
StringField
```

↓

```text
TEXT
```

---

```python
IntegerField
```

↓

```text
INTEGER
```

---

Ví dụ

```python
column = (field.name, field.sql_type)
```

↓

```text
title TEXT
```

---

# Bước 4. NOT NULL

Metadata

```python
nullable = False
```

↓

```sql
NOT NULL
```

---

Builder

```python
if not field.nullable:
    sql += " NOT NULL"
```

---

Ví dụ

```text
title TEXT NOT NULL
```

---

# Bước 5. UNIQUE

Metadata

```python
unique = True
```

↓

```sql
UNIQUE
```

---

Builder

```python
if field.unique:
    sql += " UNIQUE"
```

---

Kết quả

```text
slug TEXT UNIQUE
```

---

# Bước 6. DEFAULT

Metadata

```python
default = ""
```

↓

```sql
DEFAULT ''
```

---

Metadata

```python
default = 0
```

↓

```sql
DEFAULT 0
```

---

Builder

```python
if field.default is not None:
```

↓

thêm DEFAULT.

---

Ví dụ

```text
rating INTEGER DEFAULT 0
```

---

# Xử lý kiểu dữ liệu của DEFAULT

Không phải mọi giá trị đều được nối chuỗi giống nhau.

Ví dụ:

| Python  | SQLite  |
| ------- | ------- |
| `"abc"` | `'abc'` |
| `10`    | `10`    |
| `3.14`  | `3.14`  |
| `True`  | `1`     |
| `False` | `0`     |
| `None`  | `NULL`  |

Nên có một hàm:

```python
def format_default(value): ...
```

để chuyển đổi đúng kiểu.

---

# Bước 7. PRIMARY KEY

Metadata

```python
primary_key = True
```

↓

```sql
PRIMARY KEY
```

---

Builder

```python
if field.primary_key:
    sql += " PRIMARY KEY"
```

---

Kết quả

```text
id INTEGER PRIMARY KEY
```

---

# AUTOINCREMENT

SQLite

```sql
INTEGER PRIMARY KEY
```

đã tự tăng rowid.

Chỉ khi thật sự cần tránh tái sử dụng ID mới dùng:

```sql
INTEGER PRIMARY KEY AUTOINCREMENT
```

Field

```python
IntegerField(primary_key=True, autoincrement=True)
```

↓

```sql
INTEGER PRIMARY KEY AUTOINCREMENT
```

---

# Ghép cột

Ví dụ

```text
id INTEGER PRIMARY KEY

title TEXT NOT NULL

author TEXT
```

↓

```sql
CREATE TABLE novel(

id INTEGER PRIMARY KEY,

title TEXT NOT NULL,

author TEXT

);
```

---

Builder

```python
columns = []
```

↓

append từng cột

↓

```python
",".join(columns)
```

---

# Một Builder cơ bản

```python
class SQLSchemaBuilder:
    def build(self, model):

        columns = []

        for field in model.__fields__.values():
            sql = f"{field.name} {field.sql_type}"

            if field.primary_key:
                sql += " PRIMARY KEY"

            if not field.nullable:
                sql += " NOT NULL"

            if field.unique:
                sql += " UNIQUE"

            columns.append(sql)

        return f"CREATE TABLE {model.__table_name__}(\n" + ",\n".join(columns) + "\n);"
```

---

Kết quả

```sql
CREATE TABLE novel(

id INTEGER PRIMARY KEY,

title TEXT NOT NULL,

author TEXT

);
```

---

# Constraint riêng

SQLite còn cho phép

```sql
CONSTRAINT
```

Ví dụ

```sql
UNIQUE(title, author)
```

---

Metadata

```python
class Meta:
    unique_together = ("title", "author")
```

↓

Builder

↓

```sql
UNIQUE(title, author)
```

---

# Foreign Key

Model

```python
class Chapter(Model):
    novel_id = ForeignKey(Novel)
```

↓

SQL

```sql
FOREIGN KEY(novel_id)

REFERENCES novel(id)
```

---

Field

```python
ForeignKey(Novel)
```

↓

có thể tự biết

```text
table

pk
```

---

# Index

Metadata

```python
index = True
```

Không nằm trong CREATE TABLE.

SQLite cần

```sql
CREATE INDEX
```

---

Ví dụ

```sql
CREATE INDEX idx_title

ON novel(title);
```

---

Builder

```python
for field in fields:

    if field.index:
```

↓

Sinh SQL riêng.

---

Kết quả

```sql
CREATE TABLE ...

CREATE INDEX ...

CREATE INDEX ...
```

---

# Composite Index

Ví dụ

```python
class Meta:
    indexes = [("title", "author"), ("status", "updated_at")]
```

↓

```sql
CREATE INDEX

idx_title_author

ON novel(title,author);
```

---

# Check Constraint

Ví dụ

```python
rating = IntegerField(min_value=0, max_value=10)
```

↓

```sql
CHECK(

rating>=0

AND

rating<=10

)
```

---

# Enum Constraint

Ví dụ

```python
status = StringField(choices=["draft", "publish"])
```

↓

```sql
CHECK(

status IN (

'draft',

'publish'

)

)
```

---

# Sinh toàn bộ SQL

```text
CREATE TABLE novel

...

↓

CREATE INDEX idx_title

↓

CREATE INDEX idx_author

↓

Done
```

---

# Tách nhỏ Builder

Thay vì một hàm lớn:

```python
build()
```

nên chia:

```python
build_table()

build_columns()

build_indexes()

build_constraints()

build_foreign_keys()
```

Giúp dễ mở rộng và kiểm thử.

---

# Kiến trúc Builder

```text
                Model

                  │

                  ▼

          SQLSchemaBuilder

                  │

     ┌────────────┼───────────────┐

     ▼            ▼               ▼

 Columns     Constraints      Indexes

     │            │               │

     └────────────┼───────────────┘

                  ▼

            SQL Statements

                  ▼

         sqlite3.execute()
```

---

# Ví dụ hoàn chỉnh

Model

```python
class Novel(Model):
    id = IntegerField(primary_key=True)

    title = StringField(nullable=False, index=True)

    slug = StringField(unique=True)

    rating = IntegerField(default=0)
```

Builder sinh:

```sql
CREATE TABLE novel(

id INTEGER PRIMARY KEY,

title TEXT NOT NULL,

slug TEXT UNIQUE,

rating INTEGER DEFAULT 0

);

CREATE INDEX idx_novel_title
ON novel(title);
```

---

# Những điểm cần lưu ý khi thiết kế

1. **SQLite khác các hệ quản trị khác**:

   * Không có kiểu `BOOLEAN` thực sự (`INTEGER` 0/1).
   * Không thực thi giới hạn `VARCHAR(200)` như MySQL; `max_length` chủ yếu phục vụ validation ở tầng model.

2. **Không ghép chuỗi SQL từ dữ liệu người dùng**:

   * Schema Builder dùng metadata của framework nên an toàn.
   * Khi thao tác `INSERT`, `UPDATE`, `DELETE`, luôn dùng tham số (`?`) của `sqlite3`.

3. **Field nên chịu trách nhiệm mô tả chính nó**:

   * Ví dụ: `field.sql_type`, `field.primary_key`, `field.unique`.
   * Builder chỉ đọc metadata, không nên chứa logic nghiệp vụ của từng loại Field.

---

# Kiến trúc sau Buổi 5

```text
             Model

               │
               ▼

          ModelMeta
               │
               ▼
          __fields__
               │
               ▼
      SQLSchemaBuilder
               │
        ┌──────┼──────┐
        ▼      ▼      ▼
    CREATE   INDEX   FK
     TABLE
        │
        ▼
 DatabaseManager
        │
        ▼
 sqlite3.Database
```

---

# Bài tập thực hành

## Bài 1

Viết `SQLSchemaBuilder.build_table(model)` sinh câu lệnh `CREATE TABLE` từ metadata.

---

## Bài 2

Viết `format_default(value)` hỗ trợ:

* `str`
* `int`
* `float`
* `bool`
* `None`

để sinh đúng cú pháp `DEFAULT`.

---

## Bài 3

Thêm hỗ trợ:

* `AUTOINCREMENT`
* `CHECK`
* `UNIQUE`
* `DEFAULT`

vào từng cột.

---

## Bài 4

Viết `build_indexes(model)` trả về danh sách các câu lệnh `CREATE INDEX`.

---

## Bài 5

Thiết kế cấu trúc `Meta` cho model hỗ trợ:

* `unique_together`
* `indexes`

và cập nhật Builder để sinh SQL tương ứng.

---

# Buổi tiếp theo

**Buổi 6 — DatabaseManager & Connection Pool Deep Dive**

Đây là buổi bắt đầu làm việc trực tiếp với SQLite. Chúng ta sẽ xây dựng:

* `DatabaseManager`
* Quản lý kết nối SQLite
* Transaction (`BEGIN`, `COMMIT`, `ROLLBACK`)
* Context Manager (`with`)
* Connection Factory
* Multi-database (database chung + database riêng cho từng nguồn truyện)
* Thread Safety
* Repository tích hợp với `DatabaseManager`

Sau buổi này, framework của bạn sẽ có tầng quản lý cơ sở dữ liệu hoàn chỉnh, sẵn sàng cho việc triển khai Repository và Unit of Work.
