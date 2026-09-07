# Buổi 5 — UPDATE trong SQLite + Python

Hôm nay chúng ta học **UPDATE** thật chắc, vì trong app crawl truyện đây là thao tác xuất hiện liên tục:

* cập nhật trạng thái truyện
* cập nhật `updated_at`
* cập nhật URL
* cập nhật số chapter mới nhất
* đánh dấu chapter đã crawl
* cập nhật metadata sau khi crawl lại

---

# 1. UPDATE dùng để làm gì?

Cú pháp cơ bản:

```sql
UPDATE table_name
SET column = value
WHERE condition;
```

Ví dụ:

```sql
UPDATE novels
SET status = 'completed'
WHERE id = 5;
```

Nghĩa là:

> Tìm novel có `id = 5`, sau đó đổi `status` thành `completed`.

---

# 2. UPDATE với Python

Ví dụ:

```python
import sqlite3

conn = sqlite3.connect("novel.db")

cursor = conn.cursor()

cursor.execute(
    """
    UPDATE novels
    SET status = ?
    WHERE id = ?
    """,
    ("completed", 5),
)

conn.commit()
conn.close()
```

Luồng:

```text
Python
   ↓
cursor.execute()
   ↓
UPDATE
   ↓
SQLite
   ↓
commit()
```

---

# 3. Tuyệt đối chú ý WHERE

Đây là lỗi rất nguy hiểm:

```sql
UPDATE novels
SET status = 'completed';
```

Không có `WHERE`.

Nó có nghĩa:

> Cập nhật **tất cả các dòng**.

Ví dụ bảng:

```text
id   title                 status
1    Tiên Nghịch           ongoing
2    Phàm Nhân Tu Tiên     ongoing
3    Đấu Phá Thương Khung  ongoing
```

Sau:

```sql
UPDATE novels
SET status = 'completed';
```

thành:

```text
id   title                 status
1    Tiên Nghịch           completed
2    Phàm Nhân Tu Tiên     completed
3    Đấu Phá Thương Khung  completed
```

### Quy tắc quan trọng

> Khi UPDATE, luôn tự hỏi: **"WHERE của mình đang chọn những row nào?"**

---

# 4. UPDATE một record

Đây là pattern thường dùng trong Repository:

```python
cursor.execute(
    """
    UPDATE novels
    SET title = ?,
        author = ?
    WHERE id = ?
    """,
    (title, author, novel_id),
)
```

Ví dụ:

```python
title = "Tiên Nghịch"
author = "Nhĩ Căn"
novel_id = 10

cursor.execute(
    """
    UPDATE novels
    SET title = ?,
        author = ?
    WHERE id = ?
    """,
    (title, author, novel_id),
)

conn.commit()
```

---

# 5. UPDATE nhiều column

Không cần UPDATE từng column riêng biệt.

Không nên:

```python
cursor.execute(
    "UPDATE novels SET title = ? WHERE id = ?",
    (title, novel_id),
)

cursor.execute(
    "UPDATE novels SET author = ? WHERE id = ?",
    (author, novel_id),
)
```

Có thể viết:

```python
cursor.execute(
    """
    UPDATE novels
    SET title = ?,
        author = ?,
        status = ?,
        updated_at = ?
    WHERE id = ?
    """,
    (
        title,
        author,
        status,
        updated_at,
        novel_id,
    ),
)
```

Đây là cách sạch hơn.

---

# 6. UPDATE với điều kiện

Ví dụ chỉ cập nhật những truyện đang `ongoing`:

```sql
UPDATE novels
SET status = 'completed'
WHERE status = 'ongoing';
```

Có thể có nhiều row được thay đổi.

Ví dụ:

```text
id   status
1    ongoing
2    completed
3    ongoing
4    ongoing
```

Sau UPDATE:

```text
id   status
1    completed
2    completed
3    completed
4    completed
```

---

# 7. UPDATE kết hợp nhiều điều kiện

Ví dụ:

```sql
UPDATE novels
SET status = 'completed'
WHERE source = ?
  AND id = ?;
```

Python:

```python
cursor.execute(
    """
    UPDATE novels
    SET status = ?
    WHERE source = ?
      AND id = ?
    """,
    ("completed", "site_a", novel_id),
)
```

---

# 8. `cursor.rowcount`

Một kỹ thuật rất quan trọng:

```python
cursor.execute(
    """
    UPDATE novels
    SET status = ?
    WHERE id = ?
    """,
    ("completed", 10),
)

print(cursor.rowcount)
```

Có thể nhận:

```text
1
```

→ một row bị ảnh hưởng.

Hoặc:

```text
0
```

→ không có row nào phù hợp.

Ví dụ:

```python
if cursor.rowcount == 0:
    print("Novel không tồn tại")
else:
    print("Đã cập nhật")
```

---

# 9. Nhưng `rowcount == 0` cần hiểu cẩn thận

Ví dụ:

```text
id=10
status='completed'
```

Ta chạy:

```sql
UPDATE novels
SET status = 'completed'
WHERE id = 10;
```

Tùy cách SQLite/Python báo cáo số dòng, việc cập nhật giá trị giống hệt giá trị hiện tại có thể không cho bạn ý nghĩa "đã thực sự thay đổi dữ liệu" như bạn tưởng.

Vì vậy Repository nên phân biệt:

```text
row tồn tại?
        ↓
UPDATE
        ↓
rowcount
```

và không nên thiết kế business logic phức tạp chỉ dựa vào `rowcount`.

---

# 10. UPDATE và parameterized query

Sai:

```python
cursor.execute(
    f"""
    UPDATE novels
    SET title = '{title}'
    WHERE id = {novel_id}
    """
)
```

Đúng:

```python
cursor.execute(
    """
    UPDATE novels
    SET title = ?
    WHERE id = ?
    """,
    (title, novel_id),
)
```

Đây là quy tắc chúng ta đã học ở Buổi 3:

```text
SQL structure → viết trực tiếp
Data          → dùng ?
```

---

# 11. UPDATE trong transaction

UPDATE làm thay đổi database nên cần transaction.

```python
try:
    cursor.execute(
        """
        UPDATE novels
        SET status = ?
        WHERE id = ?
        """,
        ("completed", 10),
    )

    conn.commit()

except sqlite3.Error:
    conn.rollback()
    raise
```

Mental model:

```text
BEGIN
  │
  ├── UPDATE
  │
  ├── UPDATE
  │
  └── UPDATE
        │
        ├── thành công → COMMIT
        │
        └── lỗi       → ROLLBACK
```

---

# 12. Tại sao transaction rất quan trọng với crawler?

Giả sử crawler thực hiện:

```text
UPDATE novel
    ↓
INSERT chapter 101
    ↓
INSERT chapter 102
    ↓
INSERT chapter 103
```

Nếu chapter 103 lỗi:

```text
UPDATE novel        ✓
INSERT chapter 101  ✓
INSERT chapter 102  ✓
INSERT chapter 103  ✗
```

Nếu muốn toàn bộ operation thành công hoặc thất bại cùng nhau:

```python
try:
    cursor.execute(... UPDATE ...)

    cursor.execute(... INSERT chapter 101 ...)

    cursor.execute(... INSERT chapter 102 ...)

    cursor.execute(... INSERT chapter 103 ...)

    conn.commit()

except sqlite3.Error:
    conn.rollback()
    raise
```

Khi lỗi:

```text
ROLLBACK
   ↓
không giữ lại các thay đổi của transaction
```

Đây chính là nền tảng để sau này chúng ta học:

```text
Unit of Work
```

---

# 13. UPDATE số chapter mới nhất

Một ví dụ thực tế hơn với app truyện.

Giả sử:

```sql
novels
```

có:

```text
id
title
latest_chapter
updated_at
```

Ta có thể:

```python
cursor.execute(
    """
    UPDATE novels
    SET latest_chapter = ?,
        updated_at = ?
    WHERE id = ?
    """,
    (
        150,
        "2026-09-07T12:00:00",
        novel_id,
    ),
)
```

---

# 14. UPDATE chapter

Ví dụ bảng:

```sql
chapters
```

có:

```text
id
novel_id
chapter_number
title
content
is_crawled
```

Sau khi crawl thành công:

```python
cursor.execute(
    """
    UPDATE chapters
    SET content = ?,
        is_crawled = ?
    WHERE id = ?
    """,
    (
        content,
        1,
        chapter_id,
    ),
)
```

---

# 15. UPDATE theo business condition

Ví dụ muốn đánh dấu chapter chưa crawl:

```sql
UPDATE chapters
SET is_crawled = 1
WHERE novel_id = ?
  AND chapter_number = ?
  AND is_crawled = 0;
```

Python:

```python
cursor.execute(
    """
    UPDATE chapters
    SET is_crawled = 1
    WHERE novel_id = ?
      AND chapter_number = ?
      AND is_crawled = 0
    """,
    (novel_id, chapter_number),
)
```

Đây là một ví dụ rất tốt về:

```text
UPDATE
+
WHERE
+
business rule
```

---

# 16. UPDATE với biểu thức

`SET` không nhất thiết phải nhận một giá trị cố định.

Ví dụ:

```sql
UPDATE novels
SET view_count = view_count + 1
WHERE id = ?;
```

Python:

```python
cursor.execute(
    """
    UPDATE novels
    SET view_count = view_count + 1
    WHERE id = ?
    """,
    (novel_id,),
)
```

Đây là cách tốt hơn so với:

```python
# SELECT view_count
# cộng 1 trong Python
# UPDATE lại
```

Khi phép tính có thể thực hiện an toàn trong SQL, để database thực hiện thường hợp lý hơn.

---

# 17. UPDATE có thể kết hợp CASE

Ví dụ:

```sql
UPDATE novels
SET status = CASE
    WHEN latest_chapter >= 1000 THEN 'completed'
    ELSE 'ongoing'
END;
```

`CASE` chúng ta sẽ học sâu hơn ở phần SQL nâng cao.

Hiện tại chỉ cần biết:

```text
CASE
    WHEN condition THEN value
    ELSE value
END
```

---

# 18. Một pattern Repository rất quan trọng

Sau này chúng ta sẽ không viết SQL UPDATE trực tiếp trong Application.

Thay vào đó:

```python
class NovelRepository:

    def update_status(
        self,
        novel_id: int,
        status: str,
    ) -> None:

        self._cursor.execute(
            """
            UPDATE novels
            SET status = ?
            WHERE id = ?
            """,
            (status, novel_id),
        )
```

Application chỉ cần:

```python
repo.update_status(
    novel_id=10,
    status="completed",
)
```

Kiến trúc:

```text
Application
     ↓
NovelRepository
     ↓
UPDATE novels
     ↓
SQLite
```

Về sau:

```text
Application
     ↓
UnitOfWork
     ↓
NovelRepository
     ↓
Connection
     ↓
SQLite
```

Đó chính là hướng chúng ta đang xây dựng cho app crawl truyện.

---

# 19. Một lỗi thiết kế thường gặp

Đừng viết:

```python
def update_novel(novel):
    cursor.execute(
        f"""
        UPDATE novels
        SET title = '{novel.title}',
            author = '{novel.author}',
            status = '{novel.status}'
        WHERE id = {novel.id}
        """
    )
```

Vấn đề:

* SQL injection
* khó test
* khó kiểm soát transaction
* trộn domain object với SQL
* khó refactor

Tốt hơn:

```python
def update_novel(novel):
    cursor.execute(
        """
        UPDATE novels
        SET title = ?,
            author = ?,
            status = ?
        WHERE id = ?
        """,
        (
            novel.title,
            novel.author,
            novel.status,
            novel.id,
        ),
    )
```

Sau này còn tốt hơn nữa khi Repository quản lý việc này.

---

# 20. UPDATE checklist

Trước khi chạy UPDATE, hãy kiểm tra:

```text
☑ UPDATE đúng table?
☑ SET đúng column?
☑ Có WHERE?
☑ WHERE có đúng record không?
☑ Có parameterized query?
☑ Có transaction?
☑ Có cần kiểm tra rowcount?
☑ Có cần rollback nếu lỗi?
```

Đặc biệt:

> **UPDATE không có WHERE = cảnh báo đỏ.**

---

# 21. Bài tập Buổi 5

Giả sử có:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    status TEXT NOT NULL DEFAULT 'ongoing'
        CHECK (status IN ('ongoing', 'completed'))
);
```

### Bài 1

Đổi trạng thái novel `id = 5` thành:

```text
completed
```

---

### Bài 2

Đổi:

```text
title
author
```

của novel `id = 5`.

---

### Bài 3

Đổi tất cả novel:

```text
ongoing → completed
```

nhưng chỉ những novel có:

```text
id > 100
```

---

### Bài 4

Viết Python function:

```python
def update_novel_status(
    conn: sqlite3.Connection,
    novel_id: int,
    status: str,
) -> bool:
    ...
```

Yêu cầu:

```text
True  → update thành công
False → không tìm thấy novel
```

---

### Bài 5 — Transaction

Thực hiện:

```text
UPDATE novel
INSERT chapter
INSERT chapter
```

Nếu bất kỳ thao tác nào lỗi:

```text
ROLLBACK
```

Nếu tất cả thành công:

```text
COMMIT
```

---

# 22. Kiến thức cần nhớ sau Buổi 5

```text
UPDATE
   │
   ├── SET
   │
   ├── WHERE
   │
   ├── parameters
   │
   ├── rowcount
   │
   └── transaction
         ├── commit
         └── rollback
```

Và tư duy quan trọng nhất:

```text
UPDATE
   ↓
WHERE chọn những row nào?
   ↓
Có đúng business rule không?
   ↓
COMMIT
```

**Buổi 6** sẽ là **DELETE** — từ `DELETE ... WHERE`, soft delete vs hard delete, transaction, cascade và những lỗi rất nguy hiểm khi xóa dữ liệu.
