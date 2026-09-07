# Buổi 6 — DELETE trong SQLite + Python

Hôm nay chúng ta học **DELETE**. Đây là câu lệnh đơn giản về cú pháp nhưng **nguy hiểm nhất trong CRUD**, vì một câu `DELETE` sai có thể xóa hàng loạt dữ liệu.

Đặc biệt với app crawl truyện, chúng ta cần phân biệt rất rõ:

```text
DELETE thật sự
vs
Soft Delete
```

---

# 1. DELETE dùng để làm gì?

Cú pháp:

```sql
DELETE FROM table_name
WHERE condition;
```

Ví dụ:

```sql
DELETE FROM novels
WHERE id = 5;
```

Nghĩa là:

> Xóa novel có `id = 5`.

---

# 2. DELETE với Python

```python
import sqlite3

conn = sqlite3.connect("novel.db")

cursor = conn.cursor()

cursor.execute(
    """
    DELETE FROM novels
    WHERE id = ?
    """,
    (5,),
)

conn.commit()
conn.close()
```

Giống `UPDATE`, dữ liệu chỉ nên được thay đổi trong transaction.

---

# 3. Quy tắc vàng: DELETE phải có WHERE

Cực kỳ nguy hiểm:

```sql
DELETE FROM novels;
```

Câu này có nghĩa:

> Xóa **toàn bộ row trong bảng `novels`**.

Ví dụ:

```text
id   title
1    Tiên Nghịch
2    Phàm Nhân Tu Tiên
3    Đấu Phá Thương Khung
4    Đại Chúa Tể
```

Sau:

```sql
DELETE FROM novels;
```

thành:

```text
novels
└── empty
```

### Vì vậy:

```text
UPDATE không WHERE → nguy hiểm
DELETE không WHERE → CỰC KỲ nguy hiểm
```

Trong code production, bạn nên đặc biệt cẩn thận với `DELETE`.

---

# 4. DELETE một record

Ví dụ:

```python
cursor.execute(
    """
    DELETE FROM novels
    WHERE id = ?
    """,
    (10,),
)

conn.commit()
```

---

# 5. Kiểm tra `rowcount`

Sau DELETE:

```python
cursor.execute(
    """
    DELETE FROM novels
    WHERE id = ?
    """,
    (10,),
)

if cursor.rowcount == 0:
    print("Novel không tồn tại")
else:
    print("Đã xóa novel")

conn.commit()
```

Ý tưởng:

```text
DELETE
   ↓
rowcount
   ↓
0       → không có row phù hợp
1       → đã xóa một row
n       → đã xóa nhiều row
```

---

# 6. DELETE nhiều record

Ví dụ xóa các novel đã completed:

```sql
DELETE FROM novels
WHERE status = 'completed';
```

Hoặc:

```sql
DELETE FROM novels
WHERE status = ?
  AND id > ?;
```

Python:

```python
cursor.execute(
    """
    DELETE FROM novels
    WHERE status = ?
      AND id > ?
    """,
    ("completed", 100),
)
```

---

# 7. DELETE với nhiều điều kiện

Ví dụ:

```sql
DELETE FROM novels
WHERE source = ?
  AND status = ?
  AND id = ?;
```

Python:

```python
cursor.execute(
    """
    DELETE FROM novels
    WHERE source = ?
      AND status = ?
      AND id = ?
    """,
    ("site_a", "completed", 10),
)
```

Tư duy:

```text
WHERE
  source = site_a
      AND
  status = completed
      AND
  id = 10
```

Chỉ row thỏa **tất cả điều kiện** mới bị xóa.

---

# 8. DELETE và parameterized query

Không làm:

```python
cursor.execute(
    f"DELETE FROM novels WHERE id = {novel_id}"
)
```

Hãy làm:

```python
cursor.execute(
    """
    DELETE FROM novels
    WHERE id = ?
    """,
    (novel_id,),
)
```

Đây tiếp tục là nguyên tắc:

```text
SQL structure → cố định
Data          → parameter
```

---

# 9. DELETE trong transaction

Đây là pattern cơ bản:

```python
try:
    cursor.execute(
        """
        DELETE FROM novels
        WHERE id = ?
        """,
        (novel_id,),
    )

    conn.commit()

except sqlite3.Error:
    conn.rollback()
    raise
```

Nếu DELETE thành công:

```text
DELETE
  ↓
COMMIT
```

Nếu lỗi:

```text
DELETE
  ↓
ERROR
  ↓
ROLLBACK
```

---

# 10. Tại sao DELETE cần transaction?

Hãy tưởng tượng một novel có 100 chapters.

Ta muốn:

```text
DELETE novel
+
DELETE chapters
```

Nếu làm:

```text
DELETE chapters       ✓
DELETE novel          ✗
```

database có thể rơi vào trạng thái không mong muốn.

Ta muốn:

```text
BEGIN
   │
   ├── DELETE chapters
   │
   └── DELETE novel
          │
          ├── thành công → COMMIT
          │
          └── lỗi        → ROLLBACK
```

Đây là một trong những lý do **Unit of Work** sau này rất quan trọng.

---

# 11. Parent và Child

App truyện của chúng ta có quan hệ:

```text
Novel
  │
  ├── Chapter 1
  ├── Chapter 2
  ├── Chapter 3
  └── Chapter 4
```

Database:

```text
novels
   │
   │ 1
   ↓
chapters
   N
```

Ví dụ:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
);
```

Ở đây:

```text
novels.id
     ↑
     │
chapters.novel_id
```

---

# 12. Vấn đề khi DELETE Novel

Giả sử:

```text
Novel #10
   ├── Chapter #1
   ├── Chapter #2
   └── Chapter #3
```

Ta chạy:

```sql
DELETE FROM novels
WHERE id = 10;
```

Điều gì xảy ra?

Nếu chapters vẫn tham chiếu tới novel #10, database có thể **không cho phép xóa parent** khi foreign key đang được enforced.

Đây là lúc chúng ta cần hiểu:

```text
Foreign Key
Cascade
```

---

# 13. ON DELETE CASCADE

Có thể thiết kế:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
        ON DELETE CASCADE
);
```

Khi đó:

```sql
DELETE FROM novels
WHERE id = 10;
```

SQLite sẽ tự động:

```text
DELETE Novel #10
       │
       ├── Chapter #1 → DELETE
       ├── Chapter #2 → DELETE
       └── Chapter #3 → DELETE
```

Đây gọi là:

> **Cascade Delete**

---

# 14. Nhưng CASCADE rất mạnh

Hãy cẩn thận.

```sql
DELETE FROM novels
WHERE id = 10;
```

có thể dẫn tới:

```text
Novel
 ├── chapters
 │    ├── chapter 1
 │    ├── chapter 2
 │    └── chapter 3
 │
 └── metadata
      ├── ...
      └── ...
```

Nếu các quan hệ đều cascade:

```text
DELETE Novel
      ↓
DELETE rất nhiều dữ liệu liên quan
```

Vì vậy:

> `ON DELETE CASCADE` phải là quyết định thiết kế có chủ ý, không phải mặc định thêm vào mọi foreign key.

---

# 15. Hard Delete

**Hard delete** nghĩa là xóa row thật sự.

Ví dụ:

```sql
DELETE FROM novels
WHERE id = ?;
```

Sau đó:

```sql
SELECT *
FROM novels
WHERE id = ?;
```

→ không còn row.

Phù hợp với dữ liệu như:

```text
temporary data
cache
crawl job cũ
dữ liệu test
```

Nhưng với dữ liệu quan trọng thì cần cân nhắc.

---

# 16. Soft Delete

Thay vì:

```sql
DELETE FROM novels
WHERE id = 10;
```

ta có thể thêm:

```sql
is_deleted INTEGER NOT NULL DEFAULT 0
```

Sau đó:

```sql
UPDATE novels
SET is_deleted = 1
WHERE id = ?;
```

Dữ liệu vẫn còn:

```text
id   title          is_deleted
10   Tiên Nghịch    1
```

Nhưng application coi nó là đã xóa.

---

# 17. Soft Delete có lợi gì?

Ví dụ người dùng vô tình xóa novel:

```text
User
 ↓
Delete
 ↓
is_deleted = 1
```

Ta vẫn có thể khôi phục:

```sql
UPDATE novels
SET is_deleted = 0
WHERE id = ?;
```

Đây gọi là:

```text
Restore
```

Với app quản lý truyện, soft delete có thể rất hữu ích nếu bạn muốn giữ dữ liệu crawl cũ.

---

# 18. Query dữ liệu Soft Delete

Nếu sử dụng:

```text
is_deleted
```

thì query bình thường phải có:

```sql
SELECT id, title
FROM novels
WHERE is_deleted = 0;
```

Nếu không:

```sql
SELECT *
FROM novels;
```

bạn sẽ lấy cả dữ liệu đã "xóa".

Đây là một vấn đề rất hay gặp khi triển khai soft delete.

---

# 19. Hard Delete vs Soft Delete

|                            | Hard Delete  | Soft Delete        |
| -------------------------- | ------------ | ------------------ |
| Xóa row thật               | ✅            | ❌                  |
| Có thể restore             | ❌            | ✅                  |
| Database nhỏ hơn           | ✅            | ❌                  |
| Đơn giản                   | ✅            | ❌                  |
| Giữ lịch sử                | ❌            | ✅                  |
| Phù hợp dữ liệu quan trọng | Cần cân nhắc | Thường phù hợp hơn |

Không có lựa chọn nào luôn đúng.

---

# 20. Một pattern Repository

Sau này Repository có thể cung cấp:

```python
class NovelRepository:

    def delete(self, novel_id: int) -> None:
        self._cursor.execute(
            """
            DELETE FROM novels
            WHERE id = ?
            """,
            (novel_id,),
        )
```

Application:

```python
repo.delete(novel_id)
```

Application **không cần biết SQL**.

---

# 21. Soft Delete trong Repository

Nếu chọn soft delete:

```python
class NovelRepository:

    def delete(self, novel_id: int) -> None:
        self._cursor.execute(
            """
            UPDATE novels
            SET is_deleted = 1
            WHERE id = ?
            """,
            (novel_id,),
        )
```

Điểm thú vị:

```text
Application
     ↓
delete()
     ↓
Repository
     ↓
UPDATE is_deleted = 1
```

Application không cần quan tâm đó là hard delete hay soft delete.

Đây chính là sức mạnh của **Repository abstraction**.

---

# 22. DELETE + UoW sau này

Hiện tại:

```text
Connection
   ↓
Cursor
   ↓
DELETE
   ↓
commit()
```

Sau này:

```text
Application
      ↓
UnitOfWork
      ↓
NovelRepository
      ↓
ChapterRepository
      ↓
Connection
      ↓
SQLite
```

Ví dụ một operation:

```python
with uow:
    novel = uow.novels.get(novel_id)

    uow.chapters.delete_by_novel(novel_id)

    uow.novels.delete(novel_id)

    uow.commit()
```

Nếu có lỗi:

```text
ROLLBACK
```

Đây là lý do chúng ta đang học SQL trước rồi mới đi tới Repository/UoW.

---

# 23. Một nguyên tắc cực kỳ quan trọng

Trước khi DELETE:

```sql
DELETE FROM novels
WHERE id = ?;
```

Trong môi trường production, bạn nên kiểm tra:

```sql
SELECT id, title
FROM novels
WHERE id = ?;
```

Tư duy:

```text
SELECT
   ↓
Xác nhận đúng row
   ↓
DELETE
```

Đặc biệt với thao tác nguy hiểm.

---

# 24. DELETE an toàn hơn trong code

Ta có thể tạo function:

```python
def delete_novel(
    conn: sqlite3.Connection,
    novel_id: int,
) -> bool:

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM novels
        WHERE id = ?
        """,
        (novel_id,),
    )

    if cursor.rowcount == 0:
        return False

    conn.commit()
    return True
```

Sử dụng:

```python
deleted = delete_novel(conn, 10)

if deleted:
    print("Đã xóa")
else:
    print("Không tìm thấy novel")
```

---

# 25. Nhưng function trên còn một vấn đề

Nếu:

```python
conn.commit()
```

bị lỗi thì sao?

Hoặc tương lai chúng ta cần:

```text
DELETE chapter
DELETE novel
UPDATE something else
```

Function này sẽ bắt đầu trở nên phức tạp.

Đây chính là nơi **Unit of Work** sẽ giải quyết.

Chúng ta sẽ chưa triển khai UoW ngay.

Trước tiên cần nắm chắc SQL.

---

# 26. Bài tập Buổi 6

Giả sử:

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

Xóa novel:

```text
id = 10
```

---

### Bài 2

Xóa tất cả novel:

```text
status = completed
```

---

### Bài 3

Xóa novel:

```text
status = completed
AND id > 100
```

---

### Bài 4

Viết:

```python
def delete_novel(
    conn: sqlite3.Connection,
    novel_id: int,
) -> bool:
    ...
```

Yêu cầu:

```text
True  → đã xóa
False → không tồn tại
```

---

### Bài 5 — Transaction

Thực hiện:

```text
DELETE chapters
DELETE novel
```

Nếu thành công:

```text
COMMIT
```

Nếu lỗi:

```text
ROLLBACK
```

---

### Bài 6 — Tư duy thiết kế

Cho app crawl truyện:

```text
Novel
 ├── Chapter 1
 ├── Chapter 2
 ├── Chapter 3
 └── Chapter 4
```

Hãy suy nghĩ:

> Khi người dùng xóa một Novel, bạn muốn **hard delete**, **soft delete**, hay **cascade delete**?

Không cần code ngay. Quan trọng là giải thích **tại sao**.

---

# 27. Tổng kết 6 buổi đầu

Đến đây bạn đã có CRUD cơ bản:

```text
             SQL
              │
       ┌──────┼──────┐
       ↓      ↓      ↓
     INSERT SELECT UPDATE
                    ↓
                  DELETE
```

Hay đầy đủ hơn:

```text
CREATE TABLE
     ↓
INSERT
     ↓
SELECT
     ↓
UPDATE
     ↓
DELETE
```

Và phía Python:

```text
Python
  ↓
sqlite3.Connection
  ↓
Cursor
  ↓
execute()
  ↓
SQL
  ↓
SQLite
  ↓
commit / rollback
```

### Những nguyên tắc bạn phải thuộc

```text
1. Data → dùng parameter ?
2. UPDATE → cẩn thận WHERE
3. DELETE → đặc biệt cẩn thận WHERE
4. Thay đổi dữ liệu → transaction
5. Lỗi → rollback
6. Thành công → commit
7. Quan hệ parent/child → nghĩ đến FK
8. CASCADE → dùng có chủ đích
9. Dữ liệu quan trọng → cân nhắc Soft Delete
10. SQL không nên lan vào Application → Repository sau này
```

**Buổi 7** sẽ chuyển sang nhóm rất quan trọng: **SQL Operators + AND / OR / NOT + BETWEEN + IN + LIKE + IS NULL**, để chúng ta bắt đầu viết các câu `WHERE` phức tạp thực sự cho hệ thống truyện.
