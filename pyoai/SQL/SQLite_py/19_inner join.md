# Buổi 19 — INNER JOIN

Ở buổi 18, bạn đã biết `JOIN` tổng quát. Hôm nay ta đi sâu vào **`INNER JOIN`**, vì đây là loại JOIN quan trọng nhất khi làm Repository và truy vấn dữ liệu quan hệ.

---

## 1. INNER JOIN là gì?

`INNER JOIN` chỉ trả về những dòng **có bản ghi khớp ở cả hai bảng**.

Ví dụ:

```text
novels
┌────┬─────────────┐
│ id │ title       │
├────┼─────────────┤
│ 1  │ Tiên Nghịch │
│ 2  │ Đấu Phá     │
│ 3  │ Phàm Nhân   │
└────┴─────────────┘

chapters
┌────┬──────────┬─────────────┐
│ id │ novel_id │ title       │
├────┼──────────┼─────────────┤
│ 1  │ 1        │ Chương 1    │
│ 2  │ 1        │ Chương 2    │
│ 3  │ 2        │ Chương 1    │
└────┴──────────┴─────────────┘
```

Nếu:

```sql
SELECT
    n.id,
    n.title,
    c.chapter_number,
    c.title
FROM novels AS n
INNER JOIN chapters AS c
    ON c.novel_id = n.id;
```

Kết quả:

```text
Tiên Nghịch | Chương 1
Tiên Nghịch | Chương 2
Đấu Phá     | Chương 1
```

`Phàm Nhân` không xuất hiện vì **không có chapter nào khớp**.

---

# 2. INNER JOIN hoạt động như thế nào?

Hãy nhớ:

```text
             INNER JOIN

novels                 chapters
   │                       │
   │                       │
   └────── matching ───────┘
             ↓
       chỉ lấy phần khớp
```

Điều kiện:

```sql
ON c.novel_id = n.id
```

nghĩa là:

```text
chapters.novel_id
        =
novels.id
```

Ví dụ:

```text
novels.id = 1

chapters:
novel_id = 1  ← match
novel_id = 1  ← match
novel_id = 2  ← không match
```

---

# 3. JOIN và INNER JOIN

Hai câu này tương đương:

```sql
SELECT *
FROM novels
JOIN chapters
    ON chapters.novel_id = novels.id;
```

và:

```sql
SELECT *
FROM novels
INNER JOIN chapters
    ON chapters.novel_id = novels.id;
```

Trong SQLite:

```sql
JOIN
```

mặc định được hiểu là:

```sql
INNER JOIN
```

Tuy nhiên tôi khuyến khích bạn viết:

```sql
INNER JOIN
```

khi đang học hoặc khi muốn làm rõ ý đồ.

---

# 4. Điều quan trọng nhất: INNER JOIN loại bỏ dữ liệu không match

Giả sử:

```text
novels

1 Tiên Nghịch
2 Đấu Phá
3 Phàm Nhân
4 Thần Mộ
```

và:

```text
chapters

novel_id
1
1
2
```

Query:

```sql
SELECT
    n.id,
    n.title
FROM novels AS n
INNER JOIN chapters AS c
    ON c.novel_id = n.id;
```

Kết quả về mặt logic:

```text
1 Tiên Nghịch
1 Tiên Nghịch
2 Đấu Phá
```

Có một điểm rất quan trọng:

> **INNER JOIN không trả về mỗi Novel một lần.**

Novel có bao nhiêu chapter match thì có thể xuất hiện bấy nhiêu dòng.

---

# 5. Vì sao Novel bị lặp?

Đây là bản chất của quan hệ `1-N`.

```text
Novel
  │
  ├── Chapter 1
  ├── Chapter 2
  └── Chapter 3
```

JOIN sẽ tạo:

```text
Novel       Chapter
────────────────────────
Tiên Nghịch Chương 1
Tiên Nghịch Chương 2
Tiên Nghịch Chương 3
```

Đây **không phải lỗi**.

Đó chính là kết quả chính xác của quan hệ:

```text
1 Novel → N Chapters
```

---

# 6. INNER JOIN + WHERE

Ví dụ lấy chapter của một Novel:

```sql
SELECT
    n.id,
    n.title AS novel_title,
    c.chapter_number,
    c.title AS chapter_title
FROM novels AS n
INNER JOIN chapters AS c
    ON c.novel_id = n.id
WHERE n.id = ?
ORDER BY c.chapter_number;
```

Python:

```python
cursor = conn.execute(
    """
    SELECT
        n.id,
        n.title AS novel_title,
        c.chapter_number,
        c.title AS chapter_title
    FROM novels AS n
    INNER JOIN chapters AS c
        ON c.novel_id = n.id
    WHERE n.id = ?
    ORDER BY c.chapter_number
    """,
    (novel_id,),
)

rows = cursor.fetchall()
```

---

# 7. INNER JOIN + điều kiện trên bảng Chapter

Ví dụ:

> Lấy các chapter có số chương >= 100.

```sql
SELECT
    n.title AS novel_title,
    c.chapter_number,
    c.title AS chapter_title
FROM novels AS n
INNER JOIN chapters AS c
    ON c.novel_id = n.id
WHERE c.chapter_number >= ?
ORDER BY c.chapter_number;
```

Python:

```python
rows = conn.execute(
    """
    SELECT
        n.title AS novel_title,
        c.chapter_number,
        c.title AS chapter_title
    FROM novels AS n
    INNER JOIN chapters AS c
        ON c.novel_id = n.id
    WHERE c.chapter_number >= ?
    ORDER BY c.chapter_number
    """,
    (100,),
).fetchall()
```

---

# 8. JOIN nhiều điều kiện

`ON` không nhất thiết chỉ có một điều kiện.

Ví dụ:

```sql
SELECT
    n.title,
    c.chapter_number,
    c.title
FROM novels AS n
INNER JOIN chapters AS c
    ON c.novel_id = n.id
   AND c.chapter_number >= 100;
```

Ở đây:

```sql
ON c.novel_id = n.id
AND c.chapter_number >= 100
```

có nghĩa là chỉ JOIN những chapter:

```text
đúng Novel
AND
chapter_number >= 100
```

Tuy nhiên về mặt tư duy, với các điều kiện lọc dữ liệu thông thường, bạn thường sẽ viết:

```sql
ON c.novel_id = n.id
WHERE c.chapter_number >= 100
```

Cách này dễ đọc hơn.

---

# 9. INNER JOIN + GROUP BY

Đây là pattern cực kỳ quan trọng.

> Lấy danh sách Novel và số lượng chapter.

```sql
SELECT
    n.id,
    n.title,
    COUNT(c.id) AS chapter_count
FROM novels AS n
INNER JOIN chapters AS c
    ON c.novel_id = n.id
GROUP BY
    n.id,
    n.title;
```

Kết quả:

```text
id | title        | chapter_count
---------------------------------
1  | Tiên Nghịch  | 1200
2  | Đấu Phá      | 1650
```

Nhưng hãy chú ý:

Nếu `Phàm Nhân` có **0 chapter**, nó sẽ không xuất hiện.

Tại sao?

Vì:

```text
INNER JOIN
```

đã loại nó ra **trước khi GROUP BY**.

Đây chính là lý do buổi sau chúng ta cần học:

```text
LEFT JOIN
```

---

# 10. INNER JOIN trong Repository

Ví dụ Repository:

```python
class ChapterRepository:

    def __init__(self, conn):
        self._conn = conn

    def list_with_novel(self):
        cursor = self._conn.execute(
            """
            SELECT
                c.id,
                c.chapter_number,
                c.title AS chapter_title,
                n.id AS novel_id,
                n.title AS novel_title
            FROM chapters AS c
            INNER JOIN novels AS n
                ON n.id = c.novel_id
            ORDER BY
                n.id,
                c.chapter_number
            """
        )

        return cursor.fetchall()
```

Repository đang che giấu SQL khỏi Application Layer.

```text
Application
      ↓
ChapterRepository
      ↓
INNER JOIN
      ↓
SQLite
```

Application không cần biết:

```sql
ON n.id = c.novel_id
```

---

# 11. Một lỗi JOIN rất nguy hiểm

Bạn có:

```sql
FROM novels AS n
INNER JOIN chapters AS c
```

nhưng quên:

```sql
ON c.novel_id = n.id
```

Đây có thể trở thành:

```text
CROSS JOIN
```

Ví dụ:

```text
3 novels
×
100 chapters

= 300 rows
```

Thay vì:

```text
100 rows
```

Đây là một lỗi rất nguy hiểm khi viết Repository vì query vẫn có thể chạy **mà không báo lỗi**.

---

# 12. Một lỗi khác: JOIN sai cột

Đúng:

```sql
ON c.novel_id = n.id
```

Sai:

```sql
ON c.id = n.id
```

Nếu viết sai logic JOIN, SQL vẫn có thể chạy bình thường nhưng dữ liệu trả về sai.

Đây là lý do khi debug JOIN, hãy kiểm tra:

```text
1. Hai bảng là gì?
2. Quan hệ giữa chúng là gì?
3. FK nằm ở đâu?
4. PK được reference là gì?
5. ON đang nối đúng PK ↔ FK chưa?
```

---

# 13. INNER JOIN với Many-to-Many

Nhắc lại:

```text
novels
   │
   ↓
novel_tags
   │
   ↓
tags
```

Query:

```sql
SELECT
    n.title AS novel_title,
    t.name AS tag_name
FROM novels AS n
INNER JOIN novel_tags AS nt
    ON nt.novel_id = n.id
INNER JOIN tags AS t
    ON t.id = nt.tag_id;
```

Ví dụ:

```text
Tiên Nghịch → Tiên Hiệp
Tiên Nghịch → Huyền Huyễn
Đấu Phá     → Huyền Huyễn
```

---

# 14. Tư duy quan trọng: JOIN theo graph

Đừng học JOIN bằng cách học thuộc cú pháp.

Hãy nhìn database như một graph:

```text
novels
  │
  │ 1-N
  ↓
chapters
```

hoặc:

```text
novels
  │
  ↓
novel_tags
  ↑
  │
tags
```

Sau đó hỏi:

> Tôi muốn đi từ bảng A đến bảng B bằng quan hệ nào?

Ví dụ:

```text
Novel
  ↓
Chapter
```

thì:

```sql
INNER JOIN chapters
    ON chapters.novel_id = novels.id
```

---

# 15. INNER JOIN vs FOREIGN KEY

Hai thứ này rất dễ bị nhầm.

### FOREIGN KEY

Bảo vệ **tính toàn vẹn dữ liệu**:

```sql
FOREIGN KEY (novel_id)
REFERENCES novels(id)
```

Nó nói:

> Chapter phải tham chiếu đến Novel tồn tại.

### INNER JOIN

Dùng để **lấy dữ liệu liên quan**:

```sql
INNER JOIN novels
    ON novels.id = chapters.novel_id
```

Nó nói:

> Hãy lấy thông tin Novel tương ứng với Chapter.

Có thể có:

```text
FOREIGN KEY + không JOIN
```

và cũng có thể viết:

```text
JOIN
```

giữa những bảng không khai báo FK.

Hai khái niệm khác nhau.

---

# 16. Pattern cần ghi nhớ

### Pattern 1 — Detail

```sql
SELECT ...
FROM parent AS p
INNER JOIN child AS c
    ON c.parent_id = p.id
WHERE p.id = ?;
```

### Pattern 2 — List

```sql
SELECT ...
FROM parent AS p
INNER JOIN child AS c
    ON c.parent_id = p.id
ORDER BY ...;
```

### Pattern 3 — Statistics

```sql
SELECT
    p.id,
    p.name,
    COUNT(c.id) AS total
FROM parent AS p
INNER JOIN child AS c
    ON c.parent_id = p.id
GROUP BY
    p.id,
    p.name;
```

### Pattern 4 — Many-to-Many

```sql
SELECT ...
FROM A
INNER JOIN A_B
    ON ...
INNER JOIN B
    ON ...;
```

---

# 17. Bài tập Buổi 19

Dùng schema:

```text
novels
chapters
tags
novel_tags
```

### Bài 1

Lấy:

```text
novel title
chapter number
chapter title
```

bằng `INNER JOIN`.

---

### Bài 2

Lấy toàn bộ chapter của Novel có:

```text
id = 3
```

Sắp xếp theo `chapter_number`.

---

### Bài 3

Lấy các chapter:

```text
chapter_number >= 500
```

kèm tên Novel.

---

### Bài 4

Đếm số chapter của từng Novel bằng:

```text
INNER JOIN
+
COUNT
+
GROUP BY
```

---

### Bài 5

Lấy:

```text
novel
tag
```

bằng:

```text
novels
→ novel_tags
→ tags
```

---

### Bài 6 — Debug

Query sau có vấn đề gì?

```sql
SELECT
    n.title,
    c.title
FROM novels n
INNER JOIN chapters c
    ON c.id = n.id;
```

Hãy giải thích tại sao nó **có thể chạy nhưng kết quả sai**.

---

## 18. Kiến thức cốt lõi của Buổi 19

Bạn chỉ cần nhớ 5 ý:

```text
INNER JOIN
    ↓
chỉ lấy row match ở cả hai phía

ON
    ↓
xác định cách hai bảng liên kết

1-N
    ↓
parent có thể lặp nhiều lần

INNER JOIN + GROUP BY
    ↓
rất hữu ích cho statistics

INNER JOIN
    ↓
loại bỏ parent không có child
```

Và đặc biệt:

```text
FOREIGN KEY
    = bảo vệ quan hệ

INNER JOIN
    = truy xuất quan hệ
```

### Roadmap tiếp theo

```text
18 JOIN                  ✅
19 INNER JOIN             ✅
20 LEFT JOIN              ← tiếp theo
21 JOIN nhiều bảng
22 Subquery
23 EXISTS
```

**Buổi 20 — LEFT JOIN** sẽ rất quan trọng vì nó giải quyết bài toán mà `INNER JOIN` không làm được:

> **“Lấy tất cả Novel, kể cả Novel chưa có Chapter.”**
