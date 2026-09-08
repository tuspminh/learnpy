# Buổi 18 — JOIN trong SQLite

Hôm nay chúng ta bước sang một phần **cực kỳ quan trọng của SQL**:

> `JOIN` dùng để lấy dữ liệu liên quan từ **nhiều bảng** dựa trên mối quan hệ giữa chúng.

Sau Buổi 17, ta có mô hình:

```text
novels
   │
   ├── chapters
   │
   └── novel_tags
           │
           └── tags
```

`JOIN` chính là công cụ giúp chúng ta nối những bảng này lại để truy vấn dữ liệu có ý nghĩa.

---

# 1. Vì sao cần JOIN?

Giả sử `novels`:

```text
┌────┬─────────────────────┐
│ id │ title               │
├────┼─────────────────────┤
│ 1  │ Tiên Nghịch         │
│ 2  │ Phàm Nhân Tu Tiên   │
└────┴─────────────────────┘
```

`chapters`:

```text
┌────┬──────────┬────────────────┐
│ id │ novel_id │ title          │
├────┼──────────┼────────────────┤
│ 1  │ 1        │ Chương 1       │
│ 2  │ 1        │ Chương 2       │
│ 3  │ 1        │ Chương 3       │
│ 4  │ 2        │ Chương 1       │
└────┴──────────┴────────────────┘
```

Nếu chỉ:

```sql
SELECT *
FROM chapters;
```

ta biết:

```text
novel_id = 1
```

nhưng không biết:

```text
novel_id = 1 là "Tiên Nghịch"
```

Muốn lấy:

```text
Tiên Nghịch | Chương 1
Tiên Nghịch | Chương 2
Tiên Nghịch | Chương 3
```

ta cần `JOIN`.

---

# 2. JOIN về bản chất là gì?

Hãy nghĩ:

```text
novels.id
    │
    │ = 
    │
chapters.novel_id
```

`JOIN` nối hai dòng khi điều kiện này đúng.

SQL:

```sql
SELECT
    novels.title,
    chapters.title
FROM novels
JOIN chapters
    ON chapters.novel_id = novels.id;
```

Kết quả:

```text
┌───────────────────┬─────────────┐
│ novel_title       │ chapter     │
├───────────────────┼─────────────┤
│ Tiên Nghịch       │ Chương 1    │
│ Tiên Nghịch       │ Chương 2    │
│ Tiên Nghịch       │ Chương 3    │
│ Phàm Nhân Tu Tiên │ Chương 1    │
└───────────────────┴─────────────┘
```

Đây là ý tưởng cốt lõi của JOIN.

---

# 3. Cú pháp cơ bản

```sql
SELECT columns
FROM table_a
JOIN table_b
    ON condition;
```

Ví dụ:

```sql
SELECT
    novels.id,
    novels.title,
    chapters.chapter_number,
    chapters.title
FROM novels
JOIN chapters
    ON chapters.novel_id = novels.id;
```

---

# 4. `ON` là gì?

Đây là phần quan trọng nhất:

```sql
ON chapters.novel_id = novels.id
```

Nó nói với SQLite:

> Hãy ghép một row của `chapters` với một row của `novels` khi `chapters.novel_id` bằng `novels.id`.

Ta có:

```text
novels

id = 1
title = Tiên Nghịch
```

và:

```text
chapters

novel_id = 1
```

→ khớp.

---

# 5. JOIN dựa trên Foreign Key

Đây chính là nơi kiến thức Buổi 14–17 kết nối với nhau.

Ta đã có:

```text
novels.id
    ▲
    │
    │ FOREIGN KEY
    │
chapters.novel_id
```

Khi query:

```sql
JOIN chapters
ON chapters.novel_id = novels.id
```

ta sử dụng chính relationship đã thiết kế trong database.

Có thể hình dung:

```text
FOREIGN KEY
    ↓
mô tả relationship

JOIN
    ↓
khai thác relationship
```

Đây là một mental model rất quan trọng.

---

# 6. `JOIN` mặc định là INNER JOIN

Trong SQLite:

```sql
JOIN
```

thường tương đương:

```sql
INNER JOIN
```

Vì vậy:

```sql
SELECT ...
FROM novels
JOIN chapters
    ON chapters.novel_id = novels.id;
```

và:

```sql
SELECT ...
FROM novels
INNER JOIN chapters
    ON chapters.novel_id = novels.id;
```

có cùng ý nghĩa.

Chi tiết `INNER JOIN` chúng ta sẽ đào sâu ở **Buổi 19**.

Hôm nay tập trung vào bản chất JOIN trước.

---

# 7. JOIN + WHERE

Ví dụ:

> Lấy chapter của Novel có id = 1.

```sql
SELECT
    novels.title AS novel_title,
    chapters.chapter_number,
    chapters.title AS chapter_title
FROM novels
JOIN chapters
    ON chapters.novel_id = novels.id
WHERE novels.id = ?;
```

Python:

```python
rows = conn.execute(
    """
    SELECT
        novels.title AS novel_title,
        chapters.chapter_number,
        chapters.title AS chapter_title
    FROM novels
    JOIN chapters
        ON chapters.novel_id = novels.id
    WHERE novels.id = ?
    ORDER BY chapters.chapter_number
    """,
    (novel_id,),
).fetchall()
```

---

# 8. Alias — đặt tên ngắn cho bảng

Khi JOIN nhiều bảng, viết:

```sql
novels.title
chapters.title
```

có thể dài.

Ta dùng alias:

```sql
SELECT
    n.title AS novel_title,
    c.chapter_number,
    c.title AS chapter_title
FROM novels AS n
JOIN chapters AS c
    ON c.novel_id = n.id;
```

Có thể bỏ `AS`:

```sql
FROM novels n
JOIN chapters c
```

Kết quả tương tự.

---

# 9. Alias rất quan trọng khi hai bảng có cùng column name

Cả hai bảng đều có:

```text
id
title
```

Nếu viết:

```sql
SELECT title
FROM novels
JOIN chapters
    ON chapters.novel_id = novels.id;
```

SQLite có thể báo lỗi kiểu:

```text
ambiguous column name: title
```

Vì SQLite không biết:

```text
novels.title?
```

hay:

```text
chapters.title?
```

Do đó nên viết:

```sql
SELECT
    novels.title,
    chapters.title
FROM novels
JOIN chapters
    ON chapters.novel_id = novels.id;
```

Hoặc tốt hơn:

```sql
SELECT
    n.title AS novel_title,
    c.title AS chapter_title
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id;
```

---

# 10. Một JOIN có thể lấy dữ liệu từ cả hai bảng

Ví dụ:

```sql
SELECT
    n.id,
    n.title AS novel_title,
    n.author,
    c.chapter_number,
    c.title AS chapter_title,
    c.content
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id;
```

Ta lấy được:

```text
Novel
 ├── id
 ├── title
 └── author

Chapter
 ├── chapter_number
 ├── title
 └── content
```

trong **một result set**.

---

# 11. JOIN không tạo dữ liệu mới trong database

Điều này rất quan trọng.

`JOIN`:

```text
không INSERT
không UPDATE
không DELETE
```

Nó chỉ:

```text
đọc
↓
kết hợp
↓
trả result
```

Database vẫn giữ:

```text
novels
chapters
```

riêng biệt.

JOIN chỉ tạo ra **kết quả truy vấn tạm thời**.

---

# 12. Một Novel có nhiều Chapter → kết quả sẽ có nhiều dòng

Ví dụ:

```text
Novel 1
 ├── Chapter 1
 ├── Chapter 2
 └── Chapter 3
```

JOIN:

```sql
SELECT
    n.title,
    c.title
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id;
```

sẽ cho:

```text
Tiên Nghịch | Chương 1
Tiên Nghịch | Chương 2
Tiên Nghịch | Chương 3
```

Có vẻ như:

```text
Tiên Nghịch
```

bị lặp.

Nhưng thực ra **không phải dữ liệu trong bảng bị duplicate**.

JOIN đang trả:

```text
1 Novel
×
3 Chapters
=
3 result rows
```

Đây là đặc tính tự nhiên của quan hệ 1–N.

---

# 13. JOIN + ORDER BY

Ví dụ trang đọc truyện:

```sql
SELECT
    c.chapter_number,
    c.title,
    c.content
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id
WHERE n.id = ?
ORDER BY c.chapter_number ASC;
```

Kết quả:

```text
Chapter 1
Chapter 2
Chapter 3
Chapter 4
...
```

Crawler/reader app của bạn sẽ sử dụng kiểu query này rất thường xuyên.

---

# 14. JOIN + COUNT

Bây giờ kết hợp kiến thức:

```text
JOIN
+
COUNT
```

Ta muốn:

> Lấy số chapter của mỗi Novel.

```sql
SELECT
    n.id,
    n.title,
    COUNT(c.id) AS chapter_count
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id
GROUP BY
    n.id,
    n.title;
```

Kết quả:

```text
Tiên Nghịch         1200
Phàm Nhân Tu Tiên    900
```

Bạn đã kết hợp:

```text
Buổi 10
GROUP BY

Buổi 9
COUNT

Buổi 18
JOIN
```

Đây mới bắt đầu là SQL thực chiến.

---

# 15. JOIN + WHERE + GROUP BY

Ví dụ:

> Đếm chapter của một nguồn truyện.

Nếu `novels` có:

```text
source
```

ta có:

```sql
SELECT
    n.source,
    COUNT(c.id) AS chapter_count
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id
WHERE n.status = 'ongoing'
GROUP BY n.source;
```

Pipeline:

```text
FROM
 ↓
JOIN
 ↓
WHERE
 ↓
GROUP BY
 ↓
COUNT
```

---

# 16. JOIN Many-to-Many

Đây là lúc kiến thức Buổi 17 phát huy tác dụng.

Ta có:

```text
novels
   │
   │
novel_tags
   │
   │
tags
```

Muốn:

> Lấy tất cả tag của "Tiên Nghịch".

Ta cần nối **3 bảng**:

```sql
SELECT
    n.title,
    t.name AS tag_name
FROM novels n
JOIN novel_tags nt
    ON nt.novel_id = n.id
JOIN tags t
    ON t.id = nt.tag_id
WHERE n.id = ?;
```

Kết quả:

```text
Tiên Nghịch | Tiên hiệp
Tiên Nghịch | Huyền huyễn
Tiên Nghịch | Trọng sinh
```

Hãy nhìn relationship:

```text
n.id
  │
  ▼
nt.novel_id

nt.tag_id
  │
  ▼
t.id
```

Đây chính là cách JOIN Many-to-Many.

---

# 17. JOIN 3 bảng — mental model

Đừng cố nhớ câu SQL nguyên khối.

Hãy xây từng bước.

### Bước 1

```text
novels
   ↓
novel_tags
```

```sql
JOIN novel_tags nt
ON nt.novel_id = n.id
```

### Bước 2

```text
novel_tags
   ↓
tags
```

```sql
JOIN tags t
ON t.id = nt.tag_id
```

Cuối cùng:

```text
Novel
 ↓
NovelTag
 ↓
Tag
```

SQL:

```sql
SELECT
    n.title,
    t.name
FROM novels n
JOIN novel_tags nt
    ON nt.novel_id = n.id
JOIN tags t
    ON t.id = nt.tag_id;
```

---

# 18. Python sqlite3

Với `sqlite3.Row`:

```python
conn.row_factory = sqlite3.Row
```

ta có:

```python
rows = conn.execute(
    """
    SELECT
        n.title AS novel_title,
        c.chapter_number,
        c.title AS chapter_title
    FROM novels n
    JOIN chapters c
        ON c.novel_id = n.id
    WHERE n.id = ?
    ORDER BY c.chapter_number
    """,
    (novel_id,),
).fetchall()
```

Sử dụng:

```python
for row in rows:
    print(
        row["novel_title"],
        row["chapter_number"],
        row["chapter_title"],
    )
```

---

# 19. Repository thực tế

Ta có thể viết:

```python
class ChapterRepository:
    def __init__(self, conn):
        self._conn = conn

    def list_with_novel(
        self,
        novel_id: int,
    ):
        return self._conn.execute(
            """
            SELECT
                n.id AS novel_id,
                n.title AS novel_title,

                c.id AS chapter_id,
                c.chapter_number,
                c.title AS chapter_title

            FROM novels n

            JOIN chapters c
                ON c.novel_id = n.id

            WHERE n.id = ?

            ORDER BY c.chapter_number
            """,
            (novel_id,),
        ).fetchall()
```

Notice:

```text
Application
    ↓
ChapterRepository
    ↓
SQL JOIN
    ↓
SQLite
```

Application không cần biết cách JOIN.

---

# 20. JOIN và Repository Boundary

Đây là một điểm kiến trúc quan trọng.

Không phải cứ:

```text
NovelRepository
```

thì chỉ được query:

```text
novels
```

Repository phục vụ **use case/domain need**, không nhất thiết phải giới hạn đúng một table.

Ví dụ use case:

> Hiển thị danh sách Novel cùng số chapter.

Có thể Repository thực hiện:

```sql
novels
JOIN chapters
GROUP BY novels
```

và trả về một read model:

```python
@dataclass
class NovelSummary:
    novel_id: int
    title: str
    chapter_count: int
```

Đây sẽ kết nối rất đẹp với những gì bạn đã học về **DDD / Query Model / Repository**.

---

# 21. Một lỗi rất phổ biến

Không nên viết:

```sql
SELECT *
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id;
```

trong code production nếu không thực sự cần.

Vì:

```text
n.id
c.id
n.title
c.title
n.author
c.content
...
```

có thể gây:

* khó đọc
* trùng tên column
* mapping khó
* phụ thuộc schema
* khó refactor

Tốt hơn:

```sql
SELECT
    n.id AS novel_id,
    n.title AS novel_title,
    c.id AS chapter_id,
    c.chapter_number,
    c.title AS chapter_title
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id;
```

---

# 22. JOIN vs Foreign Key

Hai khái niệm này rất dễ bị nhầm.

### FOREIGN KEY

Là **constraint**:

```text
bảo vệ dữ liệu
```

Ví dụ:

```text
chapters.novel_id
        ↓
    novels.id
```

Nó ngăn:

```text
chapter → novel không tồn tại
```

---

### JOIN

Là **query operation**:

```text
lấy dữ liệu liên quan
```

Ví dụ:

```text
novels
  +
chapters
  ↓
result
```

Có thể nhớ:

```text
FOREIGN KEY
    ↓
maintain integrity

JOIN
    ↓
retrieve related data
```

---

# 23. JOIN không nhất thiết bắt buộc phải có FK

SQLite vẫn cho phép:

```sql
SELECT ...
FROM A
JOIN B
    ON A.x = B.y;
```

ngay cả khi database không khai báo FK.

Nhưng trong schema quan hệ chuẩn, nếu:

```text
A.x
```

thực sự tham chiếu:

```text
B.y
```

thì nên biểu diễn relationship bằng FK.

Nói cách khác:

```text
FK = database relationship/integrity
JOIN = query relationship
```

---

# 24. Bài tập thực hành

Dùng schema:

```sql
novels (
    id,
    title,
    author
)

chapters (
    id,
    novel_id,
    chapter_number,
    title,
    content
)

tags (
    id,
    name
)

novel_tags (
    novel_id,
    tag_id
)
```

## Bài 1

Viết query:

> Lấy title Novel + title Chapter.

---

## Bài 2

Lấy:

```text
Novel ID
Novel title
Chapter number
Chapter title
```

của:

```text
novel_id = 1
```

---

## Bài 3

Lấy tất cả chapter của Novel:

```text
"Tiên Nghịch"
```

thay vì dùng `novel_id`.

Gợi ý:

```sql
WHERE n.title = ?
```

---

## Bài 4

Đếm số chapter của từng Novel:

```text
Tiên Nghịch         1200
Phàm Nhân Tu Tiên    900
...
```

---

## Bài 5

Viết query 3 bảng:

```text
Novel
  ↓
NovelTag
  ↓
Tag
```

để lấy:

```text
Tiên Nghịch | Tiên hiệp
Tiên Nghịch | Huyền huyễn
...
```

---

## Bài 6 — Quan trọng

Tìm tất cả Novel có Tag:

```text
"Huyền huyễn"
```

Bạn sẽ phải suy nghĩ ngược:

```text
Tag
 ↓
NovelTag
 ↓
Novel
```

---

# 25. Mental Model cuối Buổi 18

Đừng học thuộc:

```sql
SELECT ...
FROM ...
JOIN ...
ON ...
```

Hãy suy nghĩ theo graph:

```text
novels
   │
   │ n.id = c.novel_id
   ▼
chapters
```

hoặc:

```text
novels
   │
   ▼
novel_tags
   │
   ▼
tags
```

Sau đó chuyển graph thành SQL:

```text
FROM
  ↓
JOIN
  ↓
JOIN
  ↓
WHERE
  ↓
GROUP BY
  ↓
HAVING
  ↓
ORDER BY
```

---

# Roadmap

Chúng ta hiện tại:

```text
14 FOREIGN KEY          ✅
15 One-to-One           ✅
16 One-to-Many          ✅
17 Many-to-Many         ✅
18 JOIN                 ✅ ← hôm nay
19 INNER JOIN
20 LEFT JOIN
21 JOIN nhiều bảng
22 Subquery
23 EXISTS
```

Điểm quan trọng nhất của Buổi 18:

```text
FOREIGN KEY
     ↓
xác định relationship

JOIN
     ↓
truy vấn relationship
```

Và với app truyện:

```text
Novel
   │
   ├───────────────┐
   │               │
   ▼               ▼
Chapter         NovelTag
                   │
                   ▼
                  Tag
```

**Buổi 19 — INNER JOIN** sẽ đào sâu chính loại `JOIN` chúng ta vừa dùng: điều gì xảy ra khi một bên không có record tương ứng, cách INNER JOIN loại bỏ dữ liệu không match, và đặc biệt là cách tránh những kết quả JOIN sai trong các query Repository thực tế.
