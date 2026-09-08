# Buổi 20 — LEFT JOIN

Đây là buổi **rất quan trọng** vì `LEFT JOIN` giải quyết một vấn đề mà `INNER JOIN` không giải quyết được:

> **Lấy tất cả bản ghi ở bảng bên trái, kể cả khi bảng bên phải không có dữ liệu tương ứng.**

Với app truyện của bạn, ví dụ:

> Lấy **tất cả Novel**, kể cả Novel **chưa có Chapter**.

---

# 1. Vấn đề của INNER JOIN

Giả sử database:

```text
novels
┌────┬─────────────┐
│ id │ title       │
├────┼─────────────┤
│ 1  │ Tiên Nghịch │
│ 2  │ Đấu Phá     │
│ 3  │ Phàm Nhân   │
└────┴─────────────┘
```

```text
chapters
┌────┬──────────┬────────────┐
│ id │ novel_id │ title      │
├────┼──────────┼────────────┤
│ 1  │ 1        │ Chương 1   │
│ 2  │ 1        │ Chương 2   │
│ 3  │ 2        │ Chương 1   │
└────┴──────────┴────────────┘
```

Nếu dùng:

```sql
SELECT
    n.id,
    n.title,
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

`Phàm Nhân` biến mất.

Bởi vì:

```text
Phàm Nhân
    ↓
không có chapter
    ↓
INNER JOIN
    ↓
LOẠI
```

---

# 2. LEFT JOIN giải quyết vấn đề này

Thay `INNER JOIN` bằng:

```sql
LEFT JOIN
```

```sql
SELECT
    n.id,
    n.title,
    c.title
FROM novels AS n
LEFT JOIN chapters AS c
    ON c.novel_id = n.id;
```

Kết quả:

```text
Tiên Nghịch | Chương 1
Tiên Nghịch | Chương 2
Đấu Phá     | Chương 1
Phàm Nhân   | NULL
```

Đây là bản chất của `LEFT JOIN`.

```text
LEFT JOIN

LEFT TABLE
    ↓
GIỮ TẤT CẢ
    ↓
RIGHT TABLE
    ↓
có match → dữ liệu
không match → NULL
```

---

# 3. Câu thần chú của LEFT JOIN

Hãy nhớ:

> **LEFT JOIN giữ nguyên tất cả dòng của bảng bên trái.**

Ví dụ:

```sql
FROM novels AS n
LEFT JOIN chapters AS c
```

thì:

```text
novels = LEFT
chapters = RIGHT
```

Do đó:

```text
novels
  ↓
GIỮ TẤT CẢ

chapters
  ↓
có match thì lấy
không match thì NULL
```

---

# 4. Đổi thứ tự bảng sẽ thay đổi ý nghĩa

Hai query:

```sql
FROM novels n
LEFT JOIN chapters c
    ON c.novel_id = n.id
```

và:

```sql
FROM chapters c
LEFT JOIN novels n
    ON n.id = c.novel_id
```

**không tương đương về tập kết quả**.

Query thứ nhất:

```text
Giữ tất cả novels
```

Query thứ hai:

```text
Giữ tất cả chapters
```

Vì vậy khi viết `LEFT JOIN`, hãy xác định:

> **Tôi muốn giữ toàn bộ bảng nào?**

Đặt bảng đó ở bên trái.

---

# 5. LEFT JOIN + IS NULL

Đây là một pattern cực kỳ quan trọng.

Muốn tìm:

> Novel chưa có chapter.

Ta viết:

```sql
SELECT
    n.id,
    n.title
FROM novels AS n
LEFT JOIN chapters AS c
    ON c.novel_id = n.id
WHERE c.id IS NULL;
```

Kết quả:

```text
Phàm Nhân
```

Tư duy:

```text
novel
   ↓
LEFT JOIN chapter
   ↓
chapter không tồn tại
   ↓
c.id = NULL
   ↓
WHERE c.id IS NULL
```

Pattern này thường được gọi là:

```text
LEFT JOIN ... IS NULL
```

---

# 6. Đây là một pattern rất quan trọng trong Repository

Ví dụ:

```python
class NovelRepository:
    def __init__(self, conn):
        self._conn = conn

    def get_novels_without_chapters(self):
        cursor = self._conn.execute(
            """
            SELECT
                n.id,
                n.title
            FROM novels AS n
            LEFT JOIN chapters AS c
                ON c.novel_id = n.id
            WHERE c.id IS NULL
            ORDER BY n.id
            """
        )

        return cursor.fetchall()
```

Application chỉ gọi:

```python
novels = repo.get_novels_without_chapters()
```

Không cần biết SQL bên trong.

---

# 7. LEFT JOIN + COUNT

Đây là chỗ cực kỳ quan trọng.

Ta muốn:

> Lấy **tất cả Novel** và số chapter của mỗi Novel.

Nếu dùng `INNER JOIN`:

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

Novel có 0 chapter sẽ biến mất.

Thay bằng:

```sql
SELECT
    n.id,
    n.title,
    COUNT(c.id) AS chapter_count
FROM novels AS n
LEFT JOIN chapters AS c
    ON c.novel_id = n.id
GROUP BY
    n.id,
    n.title;
```

Kết quả:

```text
Tiên Nghịch | 2
Đấu Phá     | 1
Phàm Nhân   | 0
```

Đây là một trong những ứng dụng quan trọng nhất của `LEFT JOIN`.

---

# 8. Tại sao phải COUNT(c.id)?

Chú ý:

```sql
COUNT(c.id)
```

chứ không nên viết:

```sql
COUNT(*)
```

Với `LEFT JOIN`:

```text
Phàm Nhân | NULL
```

`COUNT(c.id)`:

```text
COUNT(NULL)
=
0
```

nên kết quả là:

```text
Phàm Nhân | 0
```

Nhưng:

```sql
COUNT(*)
```

đếm dòng của kết quả JOIN.

Dòng:

```text
Phàm Nhân | NULL
```

vẫn là **một dòng**.

Do đó có thể cho:

```text
Phàm Nhân | 1
```

Đây là một lỗi SQL rất phổ biến.

### Với LEFT JOIN + đếm child:

```sql
COUNT(child.id)
```

thường là lựa chọn đúng.

---

# 9. LEFT JOIN + GROUP BY + HAVING

Ví dụ:

> Lấy tất cả Novel có ít nhất 10 chapter.

```sql
SELECT
    n.id,
    n.title,
    COUNT(c.id) AS chapter_count
FROM novels AS n
LEFT JOIN chapters AS c
    ON c.novel_id = n.id
GROUP BY
    n.id,
    n.title
HAVING COUNT(c.id) >= 10;
```

Ở đây:

```text
LEFT JOIN
    ↓
giữ tất cả Novel
    ↓
GROUP BY
    ↓
COUNT
    ↓
HAVING
    ↓
lọc group
```

Novel có 0 chapter cuối cùng bị `HAVING` loại ra vì:

```text
0 >= 10
```

là false.

---

# 10. LEFT JOIN + điều kiện WHERE: cái bẫy lớn

Đây là phần cực kỳ quan trọng.

Giả sử:

> Lấy tất cả Novel và chỉ lấy chapter có `chapter_number >= 100`.

Bạn có thể viết:

```sql
SELECT
    n.title,
    c.chapter_number
FROM novels AS n
LEFT JOIN chapters AS c
    ON c.novel_id = n.id
WHERE c.chapter_number >= 100;
```

Nhưng có vấn đề.

Novel không có chapter:

```text
Phàm Nhân | NULL
```

Sau đó:

```sql
WHERE c.chapter_number >= 100
```

mà:

```text
NULL >= 100
```

không phải TRUE.

Kết quả `Phàm Nhân` bị loại.

Về thực tế, query này làm `LEFT JOIN` có hành vi giống `INNER JOIN` đối với điều kiện đó.

---

# 11. Muốn giữ Novel chưa có Chapter thì đưa điều kiện vào ON

Viết:

```sql
SELECT
    n.title,
    c.chapter_number
FROM novels AS n
LEFT JOIN chapters AS c
    ON c.novel_id = n.id
   AND c.chapter_number >= 100;
```

Bây giờ:

```text
Novel có chapter >= 100
    → lấy chapter

Novel không có chapter >= 100
    → vẫn giữ Novel
    → chapter = NULL
```

Đây là một nguyên tắc rất quan trọng:

```text
ON
↓
xác định row nào được MATCH

WHERE
↓
lọc kết quả cuối cùng
```

---

# 12. So sánh ON và WHERE

Ví dụ:

### Cách 1

```sql
LEFT JOIN chapters c
    ON c.novel_id = n.id
WHERE c.chapter_number >= 100
```

Có thể loại Novel không có chapter.

### Cách 2

```sql
LEFT JOIN chapters c
    ON c.novel_id = n.id
   AND c.chapter_number >= 100
```

Vẫn giữ Novel không có chapter.

Mental model:

```text
ON
│
├── xác định chapter nào match Novel
│
└── không match → NULL

WHERE
│
└── lọc những dòng kết quả sau JOIN
```

---

# 13. LEFT JOIN trong app crawler

Đây là nơi kiến thức bắt đầu rất thực tế.

Dashboard crawler có thể cần:

> Hiển thị tất cả Novel và số chapter đã crawl.

Query:

```sql
SELECT
    n.id,
    n.title,
    n.status,
    COUNT(c.id) AS chapter_count
FROM novels AS n
LEFT JOIN chapters AS c
    ON c.novel_id = n.id
GROUP BY
    n.id,
    n.title,
    n.status
ORDER BY
    n.updated_at DESC;
```

Kết quả:

```text
Novel          Status       Chapters
------------------------------------
Tiên Nghịch    ongoing      1200
Đấu Phá        ongoing      900
Phàm Nhân      ongoing      0
```

Novel mới vừa được crawler phát hiện nhưng chưa crawl chapter vẫn xuất hiện.

Đây là lý do `LEFT JOIN` rất hữu ích cho dashboard.

---

# 14. LEFT JOIN + NULL để tìm dữ liệu chưa xử lý

Ví dụ crawler có:

```text
novels
chapters
```

Muốn tìm Novel chưa có Chapter:

```sql
SELECT
    n.id,
    n.title
FROM novels n
LEFT JOIN chapters c
    ON c.novel_id = n.id
WHERE c.id IS NULL;
```

Đây chính là:

```text
"Find parents without children"
```

Pattern tổng quát:

```sql
SELECT parent.*
FROM parent
LEFT JOIN child
    ON child.parent_id = parent.id
WHERE child.id IS NULL;
```

Bạn sẽ gặp pattern này rất nhiều trong SQL thực tế.

---

# 15. LEFT JOIN với Many-to-Many

Ví dụ:

```text
novels
   │
   ↓
novel_tags
   │
   ↓
tags
```

Nếu muốn:

> Lấy tất cả Novel, kể cả Novel chưa có Tag.

```sql
SELECT
    n.title,
    t.name AS tag_name
FROM novels AS n
LEFT JOIN novel_tags AS nt
    ON nt.novel_id = n.id
LEFT JOIN tags AS t
    ON t.id = nt.tag_id;
```

Novel chưa có tag:

```text
Tiên Nghịch | Huyền huyễn
Tiên Nghịch | Tiên hiệp
Đấu Phá     | Huyền huyễn
Phàm Nhân   | NULL
```

---

# 16. INNER JOIN vs LEFT JOIN

Hãy ghi nhớ bảng này:

|                                  | INNER JOIN      | LEFT JOIN      |
| -------------------------------- | --------------- | -------------- |
| Giữ tất cả bảng trái             | ❌               | ✅              |
| Cần match                        | ✅               | Không          |
| Không match                      | Bị loại         | `NULL`         |
| Parent không có child            | Không xuất hiện | Xuất hiện      |
| Tìm parent không có child        | Không phù hợp   | Rất phù hợp    |
| Dashboard thống kê tất cả parent | Có thể thiếu    | Thường phù hợp |

Mental model:

```text
INNER JOIN

A ──── MATCH ──── B
       ↓
    chỉ lấy match
```

```text
LEFT JOIN

A ──── MATCH ──── B
│
└── không match
       ↓
      NULL
```

---

# 17. Một ví dụ rất đáng nhớ

Có:

```text
novels

1 Tiên Nghịch
2 Đấu Phá
3 Phàm Nhân
```

```text
chapters

1 → novel 1
2 → novel 1
3 → novel 2
```

### INNER JOIN

```sql
SELECT n.title, c.id
FROM novels n
INNER JOIN chapters c
    ON c.novel_id = n.id;
```

Kết quả:

```text
Tiên Nghịch | 1
Tiên Nghịch | 2
Đấu Phá     | 3
```

### LEFT JOIN

```sql
SELECT n.title, c.id
FROM novels n
LEFT JOIN chapters c
    ON c.novel_id = n.id;
```

Kết quả:

```text
Tiên Nghịch | 1
Tiên Nghịch | 2
Đấu Phá     | 3
Phàm Nhân   | NULL
```

Chỉ khác một chữ:

```text
INNER
  ↓
LEFT
```

nhưng ý nghĩa nghiệp vụ có thể hoàn toàn khác.

---

# 18. Quy tắc chọn JOIN

Khi viết query, hãy hỏi:

### Câu hỏi 1

> Tôi có muốn giữ record không có quan hệ không?

Nếu **không**:

```text
INNER JOIN
```

Nếu **có**:

```text
LEFT JOIN
```

---

### Câu hỏi 2

> Bảng nào tôi muốn giữ toàn bộ?

Đặt nó bên trái:

```sql
FROM bảng_cần_giữ
LEFT JOIN bảng_liên_quan
```

---

### Câu hỏi 3

> Tôi muốn tìm những parent không có child?

Dùng:

```sql
LEFT JOIN
...
WHERE child.id IS NULL
```

---

# 19. Repository thực tế

Một Repository tốt có thể có:

```python
class NovelRepository:
    def __init__(self, conn):
        self._conn = conn

    def list_with_chapter_count(self):
        return self._conn.execute(
            """
            SELECT
                n.id,
                n.title,
                n.status,
                COUNT(c.id) AS chapter_count
            FROM novels AS n
            LEFT JOIN chapters AS c
                ON c.novel_id = n.id
            GROUP BY
                n.id,
                n.title,
                n.status
            ORDER BY
                n.updated_at DESC
            """
        ).fetchall()

    def list_without_chapters(self):
        return self._conn.execute(
            """
            SELECT
                n.id,
                n.title
            FROM novels AS n
            LEFT JOIN chapters AS c
                ON c.novel_id = n.id
            WHERE c.id IS NULL
            ORDER BY n.id
            """
        ).fetchall()
```

Application:

```python
novels = novel_repo.list_with_chapter_count()
```

hoặc:

```python
novels = novel_repo.list_without_chapters()
```

SQL vẫn nằm trong Repository.

---

# 20. Bài tập Buổi 20

Dùng:

```text
novels
chapters
tags
novel_tags
```

### Bài 1

Lấy **tất cả Novel** và chapter tương ứng bằng `LEFT JOIN`.

---

### Bài 2

Tìm tất cả Novel **chưa có Chapter**.

Gợi ý:

```sql
LEFT JOIN
+
IS NULL
```

---

### Bài 3

Lấy tất cả Novel và số chapter:

```text
novel_id
title
chapter_count
```

Phải đảm bảo Novel chưa có chapter vẫn xuất hiện với:

```text
chapter_count = 0
```

---

### Bài 4

Viết query:

> Tìm tất cả Novel có ít nhất 100 chapter.

Sử dụng:

```text
LEFT JOIN
COUNT
GROUP BY
HAVING
```

---

### Bài 5 — Quan trọng

Giải thích sự khác nhau:

```sql
LEFT JOIN chapters c
    ON c.novel_id = n.id
WHERE c.chapter_number >= 100;
```

và:

```sql
LEFT JOIN chapters c
    ON c.novel_id = n.id
   AND c.chapter_number >= 100;
```

Đặc biệt: **Novel chưa có chapter sẽ xảy ra chuyện gì?**

---

### Bài 6 — Repository

Viết:

```python
def list_novels_with_chapter_count(self): ...
```

Trả về:

```text
id
title
status
chapter_count
```

và:

```python
def list_novels_without_chapters(self): ...
```

---

# 21. Chốt Buổi 20

Ba pattern bạn cần thuộc:

### Tất cả parent + child nếu có

```sql
FROM parent p
LEFT JOIN child c
    ON c.parent_id = p.id
```

### Parent không có child

```sql
FROM parent p
LEFT JOIN child c
    ON c.parent_id = p.id
WHERE c.id IS NULL
```

### Tất cả parent + số lượng child

```sql
SELECT
    p.id,
    p.name,
    COUNT(c.id)
FROM parent p
LEFT JOIN child c
    ON c.parent_id = p.id
GROUP BY
    p.id,
    p.name;
```

Và một câu cần nhớ thật kỹ:

> **INNER JOIN = chỉ lấy những gì có quan hệ.**
> **LEFT JOIN = giữ tất cả bên trái, có quan hệ thì lấy dữ liệu, không có thì `NULL`.**

### Roadmap

```text
18 JOIN                  ✅
19 INNER JOIN             ✅
20 LEFT JOIN              ✅
21 JOIN nhiều bảng        ← tiếp theo
22 Subquery
23 EXISTS
```

Buổi 21 chúng ta sẽ ghép **3–4 bảng trong cùng một query**, đặc biệt với mô hình:

```text
Novel
  ↓
Chapter

Novel
  ↓
NovelTag
  ↓
Tag
```

để bắt đầu viết những query gần với **Repository thực tế của app crawler truyện**.
