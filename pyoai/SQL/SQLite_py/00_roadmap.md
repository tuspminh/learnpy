Được. Từ giờ tôi sẽ đóng vai **lập trình viên Python + giảng viên SQL/SQLite**, dạy bạn theo hướng **hiểu bản chất → thực hành → thiết kế → áp dụng vào project thực tế**.

Vì bạn đang xây các app Python có **Repository / Unit of Work / SQLite / crawler truyện**, tôi sẽ ưu tiên SQL và SQLite theo hướng production, không chỉ học cú pháp.

# Lộ trình SQL + SQLite + Python

## Phần I — SQL Foundation

**Buổi 1. SQL là gì? Database là gì? SQLite hoạt động thế nào?**

* Database
* Table
* Row
* Column
* Primary Key
* SQL vs SQLite
* SQLite file database
* `sqlite3` trong Python
* `Connection`
* `Cursor`

**Buổi 2. CREATE TABLE**

* `CREATE TABLE`
* Data types trong SQLite
* `INTEGER`
* `TEXT`
* `REAL`
* `BLOB`
* `NULL`
* Primary Key

**Buổi 3. INSERT**

* `INSERT INTO`
* Insert một record
* Insert nhiều record
* Parameterized query
* Vì sao không nối chuỗi SQL

**Buổi 4. SELECT**

* `SELECT`
* `WHERE`
* `ORDER BY`
* `LIMIT`
* `OFFSET`

**Buổi 5. UPDATE**

* `UPDATE`
* `SET`
* `WHERE`
* Update nhiều record
* Các lỗi nguy hiểm khi thiếu `WHERE`

**Buổi 6. DELETE**

* `DELETE`
* Xóa có điều kiện
* `DELETE` vs `DROP TABLE`

---

# Phần II — SQL thực chiến

**Buổi 7. Operators**

```sql
=
!=
>
<
>=
<=
BETWEEN
IN
LIKE
IS NULL
```

**Buổi 8. Logical Operators**

```sql
AND
OR
NOT
```

**Buổi 9. Aggregate**

```sql
COUNT()
SUM()
AVG()
MIN()
MAX()
```

**Buổi 10. GROUP BY**

**Buổi 11. HAVING**

**Buổi 12. DISTINCT**

**Buổi 13. CASE WHEN**

---

# Phần III — Relationship

Đây là phần cực kỳ quan trọng nếu bạn muốn thiết kế database cho app crawler.

**Buổi 14. Foreign Key**

```text
novel
  │
  ├── chapter
  ├── chapter
  └── chapter
```

**Buổi 15. One-to-One**

**Buổi 16. One-to-Many**

**Buổi 17. Many-to-Many**

**Buổi 18. JOIN**

```sql
INNER JOIN
LEFT JOIN
```

**Buổi 19. JOIN Deep Dive**

**Buổi 20. Subquery**

**Buổi 21. EXISTS**

---

# Phần IV — SQLite Deep Dive

**Buổi 22. SQLite Data Types & Affinity**

**Buổi 23. Constraints**

```sql
PRIMARY KEY
FOREIGN KEY
UNIQUE
NOT NULL
CHECK
DEFAULT
```

**Buổi 24. SQLite PRAGMA**

```sql
PRAGMA foreign_keys;
PRAGMA journal_mode;
PRAGMA synchronous;
```

**Buổi 25. Transactions**

```text
BEGIN
   ↓
INSERT
UPDATE
DELETE
   ↓
COMMIT
```

hoặc:

```text
BEGIN
   ↓
error
   ↓
ROLLBACK
```

**Buổi 26. WAL Mode**

**Buổi 27. SQLite Locking & Concurrency**

**Buổi 28. SQLite Performance**

```
Phần IV — SQLite Deep Dive

```text id="p4x7m1"
24 SQLite Type Affinity
25 Constraints Deep Dive
26 PRAGMA
27 Transaction Deep Dive
28 WAL
29 Locking & Concurrency
30 SQLite Performance
```


---
>Phần IV — SQLite Deep Dive

```text id="p4x7m1"
24 SQLite Type Affinity
25 Constraints Deep Dive
26 PRAGMA
27 Transaction Deep Dive
28 WAL
29 Locking & Concurrency
30 SQLite Performance
```
---

# Phần V — Index & Query Optimization

**Buổi 29. Index là gì?**

**Buổi 30. CREATE INDEX**

**Buổi 31. Composite Index**

**Buổi 32. UNIQUE Index**

**Buổi 33. EXPLAIN QUERY PLAN**

**Buổi 34. Query Optimization**

```
PART V — Index & Query Optimization

31. Index Fundamentals
32. B-Tree & SQLite Index Internals
33. Composite Index Deep Dive
34. Covering Index
35. Partial Index
36. Expression Index
37. Index + LIKE
38. Index + JOIN
39. Index + ORDER BY
40. EXPLAIN QUERY PLAN Deep Dive
41. Query Planner
42. ANALYZE & Statistics
43. N+1 Query
44. Keyset Pagination
45. Query Optimization thực chiến
```

---

# Phần VI — SQL nâng cao

**Buổi 35. CTE**

```sql
WITH ...
```

**Buổi 36. Recursive CTE**

**Buổi 37. Window Functions**

```sql
ROW_NUMBER()
RANK()
DENSE_RANK()
```

**Buổi 38. EXISTS / NOT EXISTS Deep Dive**

**Buổi 39. UPSERT**

```sql
INSERT ... ON CONFLICT ...
```

**Buổi 40. RETURNING**

---

# Phần VII — Python `sqlite3`

**Buổi 41. Python SQLite Connection**

```python
import sqlite3

conn = sqlite3.connect("app.db")
```

**Buổi 42. Cursor**

```python
cursor = conn.cursor()
```

**Buổi 43. Parameterized Query**

```python
cursor.execute(
    "SELECT * FROM novel WHERE id = ?",
    (novel_id,),
)
```

**Buổi 44. Row Factory**

```python
conn.row_factory = sqlite3.Row
```

**Buổi 45. Transaction trong Python**

**Buổi 46. Context Manager**

```python
with sqlite3.connect("app.db") as conn:
    ...
```

**Buổi 47. Error Handling**

**Buổi 48. Database Connection Manager**

---

# Phần VIII — SQL + Repository Pattern

Phần này sẽ nối trực tiếp với những gì bạn đã học trước đó.

```text
Application
     │
     ▼
Repository Interface
     │
     ▼
SQLite Repository
     │
     ▼
sqlite3
     │
     ▼
SQLite
```

**Buổi 49. Repository cơ bản**

**Buổi 50. Generic Repository**

**Buổi 51. NovelRepository**

**Buổi 52. ChapterRepository**

**Buổi 53. Mapping SQL Row → Domain Model**

**Buổi 54. Mapping Domain Model → SQL**

---

# Phần IX — Unit of Work

**Buổi 55. Transaction + Unit of Work**

```text
UnitOfWork
    │
    ├── novel_repo
    ├── chapter_repo
    └── ...
```

**Buổi 56. Commit / Rollback**

**Buổi 57. Repository dùng chung Connection**

**Buổi 58. Dummy Unit of Work**

**Buổi 59. SQLite UoW hoàn chỉnh**

---

# Phần X — Production SQLite

**Buổi 60. Database Migration**

**Buổi 61. Schema Versioning**

**Buổi 62. Seed Data**

**Buổi 63. Backup / Restore**

**Buổi 64. Testing SQLite**

**Buổi 65. In-memory SQLite**

```text
":memory:"
```

**Buổi 66. Test Repository**

**Buổi 67. Test Transaction**

---

# Phần XI — Project thực chiến

Cuối cùng chúng ta sẽ xây database cho **ứng dụng đọc/cào truyện**:

```text
                    Application
                         │
                         ▼
                  Unit of Work
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       NovelRepository      ChapterRepository
              │                     │
              └──────────┬──────────┘
                         ▼
                SQLite Connection
                         │
                         ▼
                     SQLite DB
```

Database dự kiến:

```text
novels
──────────────
id
source
url
slug
title
author
description
status
created_at
updated_at


chapters
──────────────
id
novel_id
chapter_number
title
url
content
created_at
updated_at
```

Sau đó sẽ tiến tới:

```text
Crawler
   │
   ▼
Application Service
   │
   ▼
Unit of Work
   │
   ├── NovelRepository
   │
   └── ChapterRepository
           │
           ▼
        SQLite
```

## Cách tôi sẽ dạy mỗi buổi

Mỗi bài sẽ theo cấu trúc:

```text
1. Concept
      ↓
2. SQL syntax
      ↓
3. SQLite behavior
      ↓
4. Python sqlite3
      ↓
5. Ví dụ
      ↓
6. Bài tập
      ↓
7. Debug / lỗi thường gặp
      ↓
8. Design insight
```

Đặc biệt, tôi sẽ **không cho bạn học thuộc SQL một cách rời rạc**. Mục tiêu là sau khóa này bạn có thể nhìn một yêu cầu như:

> "Lấy 20 chapter mới nhất của một novel, sắp xếp theo số chapter, đồng thời cập nhật trạng thái crawl."

và tự suy nghĩ được:

```text
Domain requirement
        ↓
SQL query
        ↓
Transaction
        ↓
Repository
        ↓
Unit of Work
        ↓
SQLite
```

---

# Bắt đầu — Buổi 1

## SQL, Database và SQLite

Trước tiên cần phân biệt 3 thứ:

```text
SQL
│
├── Ngôn ngữ truy vấn
│
SQLite
│
├── Database engine
│
Python sqlite3
│
└── Python interface để nói chuyện với SQLite
```

Ví dụ:

```python
import sqlite3

conn = sqlite3.connect("novel.db")
```

Ở đây:

```text
Python
   │
   │ sqlite3
   ▼
SQLite engine
   │
   ▼
novel.db
```

Sau đó:

```python
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE novels (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL
    )
""")

conn.commit()
conn.close()
```

Bạn vừa thực hiện:

```text
connect
   ↓
create table
   ↓
commit
   ↓
close
```

Đây chính là nền tảng mà sau này chúng ta sẽ nâng cấp thành:

```text
SQLiteConnectionManager
        ↓
UnitOfWork
        ↓
Repository
        ↓
Application Service
```

**Buổi 1 chúng ta sẽ học thật kỹ `Connection → Cursor → Execute → Commit → Rollback → Close`**, vì nếu nắm chắc 6 khái niệm này thì các phần Python + SQLite phía sau sẽ rất dễ nối lại với nhau.
