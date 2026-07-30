Rất sẵn lòng. Với vai trò là một lập trình viên Python chuyên nghiệp, mình sẽ dạy bạn **SQLite3 từ số 0 đến nâng cao**, theo hướng **vừa học SQL, vừa học cách sử dụng SQLite trong Python**.

Khóa học này sẽ khác các khóa học SQL thông thường:

- Giải thích cực kỳ dễ hiểu.
- Minh họa bằng nhiều ví dụ thực tế.
- Mọi kiến thức đều có ví dụ Python (`sqlite3`).
- Cuối khóa xây dựng một phần mềm quản lý hoàn chỉnh bằng Python + SQLite.
- Học theo tư duy của DBA và lập trình viên.

---

# Giáo trình SQLite3 từ A-Z

## Giai đoạn 1. Làm quen với CSDL quan hệ

### Buổi 1

- SQLite là gì?
- Database là gì?
- Hệ quản trị CSDL là gì?
- SQL là gì?
- SQLite khác MySQL, PostgreSQL ra sao?
- Cài đặt SQLite
- SQLite CLI
- SQLite Browser (DB Browser for SQLite)

---

### Buổi 2

Tạo database đầu tiên

- File .db
- Table
- Row
- Column
- Data Type
- PRIMARY KEY
- AUTOINCREMENT

Thực hành:

```text-x-trilium-auto
student.db
```

---

### Buổi 3

Các kiểu dữ liệu SQLite

- NULL
- INTEGER
- REAL
- TEXT
- BLOB

Affinity

Storage Class

---

### Buổi 4

Các câu lệnh SQL cơ bản

```text-x-trilium-auto
CREATE DATABASE
```

(với SQLite là tạo file)

```text-x-trilium-auto
CREATE TABLE
DROP TABLE
ALTER TABLE
```

---

### Buổi 5

INSERT

```text-x-trilium-auto
INSERT INTO
```

nhiều cách thêm dữ liệu.

---

### Buổi 6

SELECT

```text-x-trilium-auto
SELECT *
SELECT column
```

---

### Buổi 7

WHERE

```text-x-trilium-auto
=
>
<
>=
<=
<>
LIKE
IN
BETWEEN
```

---

### Buổi 8

ORDER BY

LIMIT

OFFSET

---

### Buổi 9

UPDATE

---

### Buổi 10

DELETE

---

# Giai đoạn 2. SQL nâng cao

### Buổi 11

Hàm

```text-x-trilium-auto
COUNT
SUM
AVG
MIN
MAX
```

---

### Buổi 12

GROUP BY

HAVING

---

### Buổi 13

DISTINCT

---

### Buổi 14

JOIN

- INNER
- LEFT
- RIGHT (không hỗ trợ trực tiếp)
- FULL (mô phỏng)

---

### Buổi 15

Subquery

---

### Buổi 16

View

---

### Buổi 17

Index

---

### Buổi 18

Transaction

```text-x-trilium-auto
BEGIN

COMMIT

ROLLBACK
```

---

### Buổi 19

Constraint

```text-x-trilium-auto
PRIMARY KEY

FOREIGN KEY

UNIQUE

CHECK

DEFAULT

NOT NULL
```

---

### Buổi 20

Trigger

---

# Giai đoạn 3. SQLite trong Python

### Buổi 21

Module sqlite3

```text-x-trilium-auto
import sqlite3
```

---

### Buổi 22

Connection

```text-x-trilium-auto
connect()

close()
```

---

### Buổi 23

Cursor

```text-x-trilium-auto
execute()

executemany()

executescript()
```

---

### Buổi 24

fetchone

fetchall

fetchmany

---

### Buổi 25

Parameter Query

```text-x-trilium-auto
?
```

Chống SQL Injection

---

### Buổi 26

Commit

Rollback

---

### Buổi 27

Row Factory

```text-x-trilium-auto
sqlite3.Row
```

---

### Buổi 28

Context Manager

```text-x-trilium-auto
with sqlite3.connect(...)
```

---

### Buổi 29

User Defined Function

---

### Buổi 30

Backup Database

---

# Giai đoạn 4. Thiết kế CSDL

### Buổi 31

Phân tích yêu cầu

---

### Buổi 32

ERD

Entity

Relationship

---

### Buổi 33

Chuẩn hóa

1NF

2NF

3NF

---

### Buổi 34

One To One

---

### Buổi 35

One To Many

---

### Buổi 36

Many To Many

---

### Buổi 37

Foreign Key

Cascade

---

### Buổi 38

Thiết kế Database chuyên nghiệp

---

# Giai đoạn 5. SQLite nâng cao

### Buổi 39

VACUUM

---

### Buổi 40

ANALYZE

---

### Buổi 41

EXPLAIN QUERY PLAN

---

### Buổi 42

Performance

---

### Buổi 43

WAL Mode

---

### Buổi 44

Journal Mode

---

### Buổi 45

Pragma

---

### Buổi 46

Import CSV

---

### Buổi 47

Export CSV

---

### Buổi 48

JSON trong SQLite

---

### Buổi 49

FTS5 (Full Text Search)

---

### Buổi 50

SQLite Encryption (khái niệm)

---

# Giai đoạn 6. Dự án thực tế

## Dự án 1

Quản lý sinh viên

Có các bảng:

```text-x-trilium-auto
Student

Class

Course

Score
```

---

## Dự án 2

Quản lý thư viện

```text-x-trilium-auto
Book

Author

Publisher

Borrow
```

---

## Dự án 3

Quản lý bán hàng

```text-x-trilium-auto
Customer

Product

Order

OrderDetail
```

---

## Dự án 4

Quản lý kho

```text-x-trilium-auto
Warehouse

Supplier

Import

Export
```

---

## Dự án 5

Xây dựng ORM mini bằng Python

Hiểu cách các thư viện như SQLAlchemy hoạt động.

---

# Mục tiêu sau khóa học

Sau khi hoàn thành khoảng **50 buổi**, bạn sẽ có thể:

- Hiểu rõ cách hoạt động của cơ sở dữ liệu quan hệ.
- Viết SQL thành thạo từ cơ bản đến nâng cao.
- Thiết kế cơ sở dữ liệu đúng chuẩn, tránh dư thừa dữ liệu.
- Sử dụng thư viện `sqlite3` trong Python để xây dựng ứng dụng.
- Tối ưu truy vấn bằng chỉ mục (Index) và phân tích kế hoạch thực thi.
- Thực hiện giao dịch (Transaction), đảm bảo tính toàn vẹn dữ liệu.
- Xây dựng các ứng dụng quản lý thực tế với Python và SQLite.
- Có nền tảng để chuyển sang các hệ quản trị lớn như **MySQL**, **PostgreSQL**, **SQL Server** hoặc **Oracle**, vì phần lớn kiến thức SQL và thiết kế cơ sở dữ liệu là tương đồng.

---

## Phương pháp học

Mỗi buổi học sẽ được trình bày theo cấu trúc cố định:

1. **Lý thuyết**: Giải thích khái niệm bằng ngôn ngữ dễ hiểu.
2. **Ví dụ trực quan**: Minh họa bằng các bảng và dữ liệu thực tế.
3. **Thực hành SQL**: Tự viết và chạy các câu lệnh.
4. **Thực hành Python**: Sử dụng module `sqlite3` để thao tác với cơ sở dữ liệu.
5. **Lỗi thường gặp**: Phân tích nguyên nhân và cách khắc phục.
6. **Bài tập**: Từ cơ bản đến nâng cao, giúp củng cố kiến thức.
7. **Thử thách**: Một bài toán thực tế để rèn luyện tư duy thiết kế và lập trình.

Khóa học sẽ ưu tiên giải thích bản chất, giúp bạn hiểu **vì sao** một câu lệnh hoạt động, chứ không chỉ học thuộc cú pháp. Điều này sẽ giúp bạn dễ dàng học thêm các hệ quản trị cơ sở dữ liệu khác trong tương lai.

Buổi tiếp theo chúng ta sẽ bắt đầu với **Buổi 1: SQLite là gì? Cơ sở dữ liệu quan hệ hoạt động như thế nào?**, trong đó mình sẽ giải thích trực quan bằng sơ đồ, ví dụ đời thực và thực hành tạo cơ sở dữ liệu đầu tiên.