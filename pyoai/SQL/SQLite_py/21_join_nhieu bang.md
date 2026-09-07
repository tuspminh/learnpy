# Buổi 21 — JOIN nhiều bảng

Ở buổi 20, bạn đã nắm `LEFT JOIN`. Hôm nay chúng ta nâng lên một bước rất quan trọng:

> **JOIN 3, 4 hoặc nhiều bảng trong cùng một query.**

Đây là kỹ năng bạn sẽ dùng rất nhiều khi xây **Repository cho app crawler/reader truyện**.

---

# 1. Tư duy cốt lõi

Ví dụ database của chúng ta:

```text id="1e6g8x"
novels
   │
   ├──────────────┐
   │              │
   ↓              ↓
chapters       novel_tags
                  │
                  ↓
                 tags
```

Ta có 4 bảng:

```text id="n2t5kq"
novels
chapters
tags
novel_tags
```

Trong đó:

```text id="v8c7m3"
novels 1 ─── N chapters

novels 1 ─── N novel_tags
tags   1 ─── N novel_tags
```

Do đó:

```text id="c8q2hz"
Novel
  ↓
NovelTag
  ↓
Tag
```

là một quan hệ Many-to-Many.

---

# 2. JOIN 3 bảng

Ví dụ:

> Lấy tên Novel và tên Tag.

Ta cần:

```text id="5n0r6e"
novels
   ↓
novel_tags
   ↓
tags
```

SQL:

```sql id="f4x1j8"
SELECT
    n.title AS novel_title,
    t.name AS tag_name
FROM novels AS n
INNER JOIN novel_tags AS nt
    ON nt.novel_id = n.id
INNER JOIN tags AS t
    ON t.id = nt.tag_id;
```

Có **2 JOIN**.

Đọc từ trên xuống:

```text id="2t8j3p"
FROM novels n

        ↓

JOIN novel_tags nt
        │
        │ nt.novel_id = n.id
        ↓

JOIN tags t
        │
        │ t.id = nt.tag_id
        ↓

SELECT kết quả
```

---

# 3. JOIN nhiều bảng thực chất chỉ là nối từng bước

Đừng nghĩ:

> "JOIN 3 bảng rất phức tạp."

Hãy nghĩ:

```text id="6m7v9a"
A → B
```

sau đó:

```text id="k4x0f1"
A → B → C
```

Ví dụ:

```text id="d1r6se"
novels
   ↓
novel_tags
```

đầu tiên:

```sql id="y2x7qd"
INNER JOIN novel_tags nt
    ON nt.novel_id = n.id
```

Sau đó:

```text id="g6h1kp"
novel_tags
   ↓
tags
```

thêm:

```sql id="c2f8wy"
INNER JOIN tags t
    ON t.id = nt.tag_id
```

---

# 4. Ví dụ dữ liệu

### novels

```text id="1j2r8v"
id | title
----------------
1  | Tiên Nghịch
2  | Đấu Phá
3  | Phàm Nhân
```

### tags

```text id="8p0k3x"
id | name
----------------
1  | Tiên Hiệp
2  | Huyền Huyễn
3  | Trọng Sinh
```

### novel_tags

```text id="6z5q1n"
novel_id | tag_id
------------------
1        | 1
1        | 2
2        | 2
2        | 3
```

Query:

```sql id="4f9w3d"
SELECT
    n.title,
    t.name
FROM novels n
INNER JOIN novel_tags nt
    ON nt.novel_id = n.id
INNER JOIN tags t
    ON t.id = nt.tag_id;
```

Kết quả:

```text id="2h7k0m"
Tiên Nghịch | Tiên Hiệp
Tiên Nghịch | Huyền Huyễn
Đấu Phá     | Huyền Huyễn
Đấu Phá     | Trọng Sinh
```

---

# 5. JOIN 4 bảng

Bây giờ lấy:

```text id="h6v2qs"
Novel
Chapter
Tag
```

Ta có:

```text id="k0z5mx"
novels
   │
   ├── chapters
   │
   └── novel_tags
          │
          └── tags
```

Nếu muốn lấy:

```text id="x7p4vc"
novel
chapter
tag
```

thì:

```sql id="1l3h9k"
SELECT
    n.title AS novel_title,
    c.chapter_number,
    c.title AS chapter_title,
    t.name AS tag_name
FROM novels AS n

INNER JOIN chapters AS c
    ON c.novel_id = n.id

INNER JOIN novel_tags AS nt
    ON nt.novel_id = n.id

INNER JOIN tags AS t
    ON t.id = nt.tag_id;
```

Đây là **JOIN 4 bảng**.

---

# 6. Nhưng hãy cẩn thận: JOIN có thể nhân số dòng

Đây là phần cực kỳ quan trọng.

Giả sử:

```text id="v7w2m8"
Tiên Nghịch
    │
    ├── Chapter 1
    ├── Chapter 2
    │
    ├── Tag: Tiên Hiệp
    └── Tag: Huyền Huyễn
```

Khi JOIN:

```text id="0q5s7d"
2 chapters
×
2 tags
```

có thể tạo:

```text id="9n1k4x"
Chapter 1 | Tiên Hiệp
Chapter 1 | Huyền Huyễn
Chapter 2 | Tiên Hiệp
Chapter 2 | Huyền Huyễn
```

Tổng cộng:

```text id="8s6m2p"
4 rows
```

Đây **không phải lỗi SQL**.

Đó là kết quả logic của việc JOIN hai quan hệ `1-N` độc lập cùng lúc.

---

# 7. Đây là Cartesian multiplication trong JOIN

Ta có:

```text id="4j8p0w"
Novel
 │
 ├── 2 Chapters
 │
 └── 3 Tags
```

JOIN cả hai:

```text id="n6f2yq"
2 × 3 = 6 rows
```

Ví dụ:

```text id="0u3c8m"
Chapter 1 | Tag A
Chapter 1 | Tag B
Chapter 1 | Tag C

Chapter 2 | Tag A
Chapter 2 | Tag B
Chapter 2 | Tag C
```

Vì vậy khi JOIN nhiều bảng, luôn phải hỏi:

> **Mối quan hệ giữa các bảng tạo ra bao nhiêu dòng?**

---

# 8. JOIN nhiều bảng + WHERE

Ví dụ:

> Lấy chapter của các Novel có tag `"Huyền Huyễn"`.

```sql id="b9x2kf"
SELECT
    n.title AS novel_title,
    c.chapter_number,
    c.title AS chapter_title
FROM novels AS n

INNER JOIN chapters AS c
    ON c.novel_id = n.id

INNER JOIN novel_tags AS nt
    ON nt.novel_id = n.id

INNER JOIN tags AS t
    ON t.id = nt.tag_id

WHERE t.name = ?
ORDER BY
    n.id,
    c.chapter_number;
```

Python:

```python id="q5m8va"
rows = conn.execute(
    """
    SELECT
        n.title AS novel_title,
        c.chapter_number,
        c.title AS chapter_title
    FROM novels AS n

    INNER JOIN chapters AS c
        ON c.novel_id = n.id

    INNER JOIN novel_tags AS nt
        ON nt.novel_id = n.id

    INNER JOIN tags AS t
        ON t.id = nt.tag_id

    WHERE t.name = ?
    ORDER BY
        n.id,
        c.chapter_number
    """,
    ("Huyền Huyễn",),
).fetchall()
```

---

# 9. JOIN nhiều bảng + GROUP BY

Một query rất thực tế:

> Với mỗi Novel, lấy số chapter và số tag.

Có thể viết:

```sql id="3v7x9q"
SELECT
    n.id,
    n.title,
    COUNT(DISTINCT c.id) AS chapter_count,
    COUNT(DISTINCT t.id) AS tag_count
FROM novels AS n

LEFT JOIN chapters AS c
    ON c.novel_id = n.id

LEFT JOIN novel_tags AS nt
    ON nt.novel_id = n.id

LEFT JOIN tags AS t
    ON t.id = nt.tag_id

GROUP BY
    n.id,
    n.title;
```

Tại sao cần:

```sql id="z8c4m1"
COUNT(DISTINCT c.id)
```

thay vì:

```sql id="0w7v3p"
COUNT(c.id)
```

?

Bởi vì:

```text id="x1k6d9"
2 chapters
×
3 tags
=
6 rows
```

Nếu:

```sql id="1r5q8z"
COUNT(c.id)
```

thì có thể đếm thành:

```text
6
```

thay vì:

```text
2
```

`DISTINCT` loại sự lặp lại do JOIN.

Đây là pattern cực kỳ quan trọng:

```sql id="v3m8s1"
COUNT(DISTINCT ...)
```

khi nhiều JOIN có thể nhân dòng.

---

# 10. LEFT JOIN nhiều bảng

Muốn:

> Lấy **tất cả Novel**, kể cả Novel chưa có Chapter hoặc Tag.

Dùng:

```sql id="4z9p6k"
SELECT
    n.id,
    n.title,
    c.chapter_number,
    t.name AS tag_name
FROM novels AS n

LEFT JOIN chapters AS c
    ON c.novel_id = n.id

LEFT JOIN novel_tags AS nt
    ON nt.novel_id = n.id

LEFT JOIN tags AS t
    ON t.id = nt.tag_id;
```

Mental model:

```text id="6c2n8v"
Novel
 │
 ├── có Chapter? ──→ lấy
 │                   không → NULL
 │
 └── có Tag? ──────→ lấy
                     không → NULL
```

---

# 11. LEFT JOIN nhiều bảng + COUNT

Dashboard crawler có thể cần:

> Hiển thị tất cả Novel, số chapter và số tag.

```sql id="m3q7xa"
SELECT
    n.id,
    n.title,
    COUNT(DISTINCT c.id) AS chapter_count,
    COUNT(DISTINCT t.id) AS tag_count
FROM novels AS n

LEFT JOIN chapters AS c
    ON c.novel_id = n.id

LEFT JOIN novel_tags AS nt
    ON nt.novel_id = n.id

LEFT JOIN tags AS t
    ON t.id = nt.tag_id

GROUP BY
    n.id,
    n.title

ORDER BY
    n.id;
```

Đây là query khá gần với nhu cầu của một **crawler dashboard**.

---

# 12. Tìm Novel có một Tag cụ thể

Ví dụ:

> Tìm tất cả Novel có tag `Huyền Huyễn`.

```sql id="5k3n9r"
SELECT
    n.id,
    n.title
FROM novels AS n

INNER JOIN novel_tags AS nt
    ON nt.novel_id = n.id

INNER JOIN tags AS t
    ON t.id = nt.tag_id

WHERE t.name = ?
ORDER BY n.title;
```

Python:

```python id="2v8x4m"
rows = conn.execute(
    """
    SELECT
        n.id,
        n.title
    FROM novels AS n
    INNER JOIN novel_tags AS nt
        ON nt.novel_id = n.id
    INNER JOIN tags AS t
        ON t.id = nt.tag_id
    WHERE t.name = ?
    ORDER BY n.title
    """,
    ("Huyền Huyễn",),
).fetchall()
```

---

# 13. Tìm Novel có nhiều Tag

Ví dụ:

> Tìm Novel có ít nhất 3 tag.

```sql id="7m1c5q"
SELECT
    n.id,
    n.title,
    COUNT(DISTINCT t.id) AS tag_count
FROM novels AS n

INNER JOIN novel_tags AS nt
    ON nt.novel_id = n.id

INNER JOIN tags AS t
    ON t.id = nt.tag_id

GROUP BY
    n.id,
    n.title

HAVING COUNT(DISTINCT t.id) >= 3;
```

Pipeline:

```text id="9v4x2m"
FROM
 ↓
JOIN
 ↓
JOIN
 ↓
GROUP BY
 ↓
COUNT(DISTINCT)
 ↓
HAVING
```

---

# 14. Một query Repository rất thực tế

Ta có thể xây:

```python id="5q8m2v"
class NovelRepository:

    def __init__(self, conn):
        self._conn = conn

    def list_with_statistics(self):
        return self._conn.execute(
            """
            SELECT
                n.id,
                n.title,
                n.status,

                COUNT(DISTINCT c.id)
                    AS chapter_count,

                COUNT(DISTINCT t.id)
                    AS tag_count

            FROM novels AS n

            LEFT JOIN chapters AS c
                ON c.novel_id = n.id

            LEFT JOIN novel_tags AS nt
                ON nt.novel_id = n.id

            LEFT JOIN tags AS t
                ON t.id = nt.tag_id

            GROUP BY
                n.id,
                n.title,
                n.status

            ORDER BY
                n.updated_at DESC
            """
        ).fetchall()
```

Application:

```python id="m9c3x7"
rows = novel_repo.list_with_statistics()

for row in rows:
    print(
        row["title"],
        row["chapter_count"],
        row["tag_count"],
    )
```

Đây chính là hướng:

```text id="z2p7ka"
Application
      ↓
NovelRepository
      ↓
SQL
      ↓
SQLite
```

---

# 15. JOIN nhiều bảng và Alias

Khi có nhiều bảng, alias gần như bắt buộc.

Không nên:

```sql id="a6j3w9"
SELECT
    novels.title,
    chapters.title,
    tags.name
FROM novels
INNER JOIN chapters ...
INNER JOIN novel_tags ...
INNER JOIN tags ...
```

Nên:

```sql id="9w2k5d"
SELECT
    n.title AS novel_title,
    c.title AS chapter_title,
    t.name AS tag_name
FROM novels AS n
INNER JOIN chapters AS c
    ON c.novel_id = n.id
INNER JOIN novel_tags AS nt
    ON nt.novel_id = n.id
INNER JOIN tags AS t
    ON t.id = nt.tag_id;
```

Quy ước rất dễ nhớ:

```text id="e4m7q1"
n  = novels
c  = chapters
t  = tags
nt = novel_tags
```

---

# 16. JOIN nhiều bảng + `SELECT *` nên tránh

Đừng:

```sql id="v8k3q2"
SELECT *
FROM novels n
JOIN chapters c ...
JOIN novel_tags nt ...
JOIN tags t ...;
```

Vì bạn sẽ nhận rất nhiều cột:

```text id
title
id
title
novel_id
tag_id
id
name
...
```

Có thể có:

```text id
title
```

lặp lại nhiều lần.

Thay vào đó:

```sql id="n5j8r2"
SELECT
    n.id AS novel_id,
    n.title AS novel_title,
    c.id AS chapter_id,
    c.chapter_number,
    c.title AS chapter_title,
    t.id AS tag_id,
    t.name AS tag_name
```

Khi chuyển sang Python `sqlite3.Row`, điều này đặc biệt quan trọng.

---

# 17. Cách suy nghĩ khi gặp bài JOIN nhiều bảng

Đừng viết SQL ngay.

Hãy làm 4 bước.

### Bước 1 — Xác định dữ liệu cần lấy

Ví dụ:

```text id="c3m8q1"
Novel title
Chapter number
Tag name
```

---

### Bước 2 — Xác định bảng chứa dữ liệu

```text id="h8v2m6"
Novel title
    ↓
novels

Chapter number
    ↓
chapters

Tag name
    ↓
tags
```

---

### Bước 3 — Tìm đường đi

```text id="z7n4p2"
novels
   ↓
chapters

novels
   ↓
novel_tags
   ↓
tags
```

---

### Bước 4 — Viết JOIN

```sql id="q2m6x8"
FROM novels n

JOIN chapters c
    ON c.novel_id = n.id

JOIN novel_tags nt
    ON nt.novel_id = n.id

JOIN tags t
    ON t.id = nt.tag_id
```

Sau đó mới thêm:

```text id="f1v9k4"
SELECT
WHERE
GROUP BY
HAVING
ORDER BY
LIMIT
```

Đây là cách tránh bị rối.

---

# 18. JOIN nhiều bảng: lỗi phổ biến nhất

### Lỗi 1 — Nối sai FK

Sai:

```sql id="s6p2m8"
ON c.id = n.id
```

Đúng:

```sql id="d3x7q1"
ON c.novel_id = n.id
```

---

### Lỗi 2 — Quên một điều kiện JOIN

Ví dụ:

```sql id="w5k9r3"
JOIN tags t
```

nhưng không có:

```sql id="j8m2x6"
ON t.id = nt.tag_id
```

Có thể tạo ra lượng dữ liệu khổng lồ.

---

### Lỗi 3 — Đếm sai vì JOIN nhân dòng

Sai:

```sql id="x4q7m1"
COUNT(c.id)
```

trong một query có nhiều quan hệ `1-N`.

Có thể cần:

```sql id="p9v3k5"
COUNT(DISTINCT c.id)
```

---

### Lỗi 4 — Dùng INNER JOIN khi cần giữ parent

Nếu Novel chưa có Chapter vẫn phải xuất hiện:

```sql id="j2m8q4"
LEFT JOIN
```

không phải:

```sql id="r6x1v9"
INNER JOIN
```

---

# 19. Tổng kết các loại JOIN đã học

Đến đây bạn có:

```text id="u7c3m9"
JOIN
 ↓
INNER JOIN
 ↓
LEFT JOIN
 ↓
JOIN nhiều bảng
```

Mental model:

```text id="b5n8q2"
INNER JOIN
→ chỉ lấy phần match

LEFT JOIN
→ giữ toàn bộ bên trái

Nhiều JOIN
→ đi qua graph quan hệ

COUNT(DISTINCT)
→ tránh đếm trùng do JOIN
```

---

# 20. Bài tập Buổi 21

Dùng schema:

```text id="r3m7x1"
novels
chapters
tags
novel_tags
```

## Bài 1

Viết query lấy:

```text
novel_title
tag_name
```

cho tất cả Novel.

---

## Bài 2

Viết query lấy:

```text
novel_title
chapter_number
chapter_title
tag_name
```

bằng 4 bảng.

---

## Bài 3

Tìm tất cả Novel có tag:

```text
"Huyền Huyễn"
```

---

## Bài 4

Tìm tất cả Novel có ít nhất:

```text
3 tags
```

Dùng:

```text
GROUP BY
COUNT(DISTINCT ...)
HAVING
```

---

## Bài 5 — Quan trọng

Một Novel có:

```text
10 chapters
5 tags
```

Nếu JOIN `chapters` và `tags` cùng lúc, tại sao có thể sinh:

```text
10 × 5 = 50 rows
```

?

---

## Bài 6 — Rất quan trọng

Viết query:

> Lấy tất cả Novel, số chapter và số tag của mỗi Novel, kể cả Novel chưa có Chapter hoặc Tag.

Gợi ý:

```text id="h4v8m2"
novels
LEFT JOIN chapters
LEFT JOIN novel_tags
LEFT JOIN tags
GROUP BY
COUNT(DISTINCT ...)
```

---

# 21. Kiến thức cần thuộc sau Buổi 21

Bạn nên có thể nhìn:

```text id="n6x2k8"
novels
   │
   ├── chapters
   │
   └── novel_tags
          │
          └── tags
```

và tự động chuyển thành:

```sql id="q9m4v7"
FROM novels n

LEFT JOIN chapters c
    ON c.novel_id = n.id

LEFT JOIN novel_tags nt
    ON nt.novel_id = n.id

LEFT JOIN tags t
    ON t.id = nt.tag_id
```

Đây là bước chuyển rất quan trọng từ **học SQL** sang **thiết kế query cho ứng dụng thực tế**.

### Roadmap tiếp theo

```text
18 JOIN                  ✅
19 INNER JOIN             ✅
20 LEFT JOIN              ✅
21 JOIN nhiều bảng        ✅
22 Subquery               ← tiếp theo
23 EXISTS
```

**Buổi 22 — Subquery** sẽ chuyển sang một kiểu tư duy khác: thay vì chỉ nối bảng bằng `JOIN`, chúng ta sẽ học cách **đặt một query bên trong một query khác**, ví dụ:

```sql
SELECT *
FROM novels
WHERE id IN (
    SELECT novel_id
    FROM chapters
    WHERE chapter_number >= 100
);
```

Đây là nền tảng rất tốt trước khi đi vào `EXISTS`, CTE và các query nâng cao.
