# Buổi 16 — One-to-Many (1–N) trong SQLite

Đây là **quan hệ quan trọng nhất** đối với app crawl truyện của bạn.

Ta có:

```text
Novel
  │
  ├── Chapter 1
  ├── Chapter 2
  ├── Chapter 3
  ├── Chapter 4
  └── Chapter N
```

Tức là:

> Một `Novel` có nhiều `Chapter`, nhưng mỗi `Chapter` chỉ thuộc về một `Novel`.

---

# 1. One-to-Many là gì?

Ví dụ:

```text
novels
┌────┬─────────────────────┐
│ id │ title               │
├────┼─────────────────────┤
│ 1  │ Tiên Nghịch         │
│ 2  │ Phàm Nhân Tu Tiên   │
└────┴─────────────────────┘

chapters
┌────┬──────────┬───────────────┐
│ id │ novel_id │ title         │
├────┼──────────┼───────────────┤
│ 1  │ 1        │ Chương 1     │
│ 2  │ 1        │ Chương 2     │
│ 3  │ 1        │ Chương 3     │
│ 4  │ 2        │ Chương 1     │
│ 5  │ 2        │ Chương 2     │
└────┴──────────┴───────────────┘
```

Ta thấy:

```text
novel 1
  │
  ├── chapter 1
  ├── chapter 2
  └── chapter 3
```

và:

```text
novel 2
  │
  ├── chapter 1
  └── chapter 2
```

Đó là **1–N**.

---

# 2. FK nằm ở đâu?

Quy tắc cực kỳ quan trọng:

> Foreign Key nằm ở phía **Many**.

Ta có:

```text
Novel                 Chapter
  1                      N
  │                      │
  └──────────────────────┘
```

Vì `chapters` là phía N nên:

```sql
chapters.novel_id
```

là Foreign Key.

Schema:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);

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

---

# 3. Điểm khác biệt với One-to-One

Buổi trước:

```text
1–1
```

ta cần:

```sql
novel_id INTEGER NOT NULL UNIQUE
```

Nhưng 1–N:

```sql
novel_id INTEGER NOT NULL
```

**không được UNIQUE.**

Tại sao?

Vì ta muốn:

```text
novel_id = 1
novel_id = 1
novel_id = 1
novel_id = 1
```

hoàn toàn hợp lệ.

Mỗi giá trị đại diện cho một chapter khác nhau.

---

# 4. So sánh trực tiếp

## One-to-One

```sql
novel_id INTEGER NOT NULL UNIQUE
```

Cho phép:

```text
1 → metadata
```

nhưng không cho:

```text
1 → metadata A
1 → metadata B
```

---

## One-to-Many

```sql
novel_id INTEGER NOT NULL
```

Cho phép:

```text
1 → chapter A
1 → chapter B
1 → chapter C
1 → chapter D
```

Đây chính là khác biệt cốt lõi.

---

# 5. Tạo database thực tế

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row

conn.execute("PRAGMA foreign_keys = ON")
```

Tạo bảng:

```python
conn.executescript(
    """
    CREATE TABLE novels (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT
    );

    CREATE TABLE chapters (
        id INTEGER PRIMARY KEY,
        novel_id INTEGER NOT NULL,
        chapter_number INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT,

        FOREIGN KEY (novel_id)
            REFERENCES novels(id)
    );
    """
)
```

---

# 6. Insert Novel

```python
cursor = conn.execute(
    """
    INSERT INTO novels (title, author)
    VALUES (?, ?)
    """,
    ("Tiên Nghịch", "Nhĩ Căn"),
)

novel_id = cursor.lastrowid
```

Ví dụ:

```text
novel_id = 1
```

---

# 7. Insert nhiều Chapter

Bây giờ:

```python
chapters = [
    (novel_id, 1, "Chương 1", "Nội dung chương 1"),
    (novel_id, 2, "Chương 2", "Nội dung chương 2"),
    (novel_id, 3, "Chương 3", "Nội dung chương 3"),
]
```

Dùng:

```python
conn.executemany(
    """
    INSERT INTO chapters (
        novel_id,
        chapter_number,
        title,
        content
    )
    VALUES (?, ?, ?, ?)
    """,
    chapters,
)
```

Commit:

```python
conn.commit()
```

Database:

```text
novels

1 | Tiên Nghịch
```

```text
chapters

1 | 1 | Chương 1
2 | 1 | Chương 2
3 | 1 | Chương 3
```

---

# 8. Một Novel có thể có rất nhiều Chapter

Ví dụ:

```text
Novel
id = 1

        ↓

Chapter
novel_id = 1
chapter_number = 1

novel_id = 1
chapter_number = 2

novel_id = 1
chapter_number = 3

...

novel_id = 1
chapter_number = 1000
```

Không có vấn đề gì.

Đây chính là lý do **không được đặt UNIQUE riêng trên `novel_id`**.

---

# 9. Nhưng Chapter phải thuộc Novel tồn tại

Ta thử:

```python
conn.execute(
    """
    INSERT INTO chapters (
        novel_id,
        chapter_number,
        title
    )
    VALUES (?, ?, ?)
    """,
    (
        999,
        1,
        "Chapter không tồn tại",
    ),
)
```

Nếu:

```python
PRAGMA foreign_keys = ON
```

SQLite sẽ báo:

```text
sqlite3.IntegrityError:
FOREIGN KEY constraint failed
```

Bởi vì:

```text
novels.id = 999
```

không tồn tại.

Database đang bảo vệ invariant:

> Chapter không thể thuộc về một Novel không tồn tại.

---

# 10. Một invariant rất quan trọng: chapter_number

Có một vấn đề khác.

Ta không muốn:

```text
Novel 1

Chapter 1
Chapter 1
Chapter 2
```

Thông thường mỗi novel chỉ nên có một chapter số 1.

Vậy ta cần:

```sql
UNIQUE (novel_id, chapter_number)
```

Schema tốt hơn:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,

    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,

    title TEXT NOT NULL,
    content TEXT,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id),

    UNIQUE (novel_id, chapter_number)
);
```

---

# 11. Tại sao không UNIQUE chapter_number?

Không được viết:

```sql
chapter_number INTEGER NOT NULL UNIQUE
```

vì:

```text
Novel A
  Chapter 1

Novel B
  Chapter 1
```

hoàn toàn hợp lệ.

Nếu `chapter_number` global UNIQUE:

```text
Novel A → chapter 1
Novel B → chapter 1  ❌
```

Nhưng điều chúng ta muốn là:

```text
Novel A → chapter 1  ✅
Novel B → chapter 1  ✅
```

Do đó uniqueness phải là:

```text
(novel_id, chapter_number)
```

hay còn gọi là **composite UNIQUE constraint**.

---

# 12. Composite UNIQUE

```sql
UNIQUE (novel_id, chapter_number)
```

nghĩa là cặp:

```text
(novel_id, chapter_number)
```

không được trùng.

Ví dụ:

```text
(1, 1)  ✅
(1, 2)  ✅
(1, 3)  ✅

(2, 1)  ✅
(2, 2)  ✅

(1, 1)  ❌
```

Đây là một pattern cực kỳ quan trọng trong database.

---

# 13. ON DELETE CASCADE

Đối với app truyện, ta thường muốn:

```text
Xóa Novel
     ↓
Xóa toàn bộ Chapter
```

Schema:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,

    novel_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,

    title TEXT NOT NULL,
    content TEXT,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
        ON DELETE CASCADE,

    UNIQUE (novel_id, chapter_number)
);
```

Khi:

```sql
DELETE FROM novels
WHERE id = 1;
```

SQLite sẽ tự động:

```text
Novel 1
   │
   ├── Chapter 1
   ├── Chapter 2
   ├── Chapter 3
   └── Chapter 4

       ↓ DELETE

Novel 1 ❌
Chapter 1 ❌
Chapter 2 ❌
Chapter 3 ❌
Chapter 4 ❌
```

---

# 14. Đây chính là Aggregate Boundary mà bạn sẽ gặp lại ở DDD

Với app của chúng ta:

```text
Novel
 ├── Chapter
 ├── Chapter
 ├── Chapter
 └── Chapter
```

có thể xem:

```text
Novel
   ↓
Aggregate Root
```

và:

```text
Chapter
   ↓
Entity bên trong Aggregate
```

Khi đó:

```text
NovelRepository
```

có thể quản lý cả:

```text
Novel
Chapter
```

tùy thiết kế domain.

Điều này sẽ rất hữu ích khi chúng ta kết hợp:

```text
DDD
+
Repository
+
Unit of Work
+
SQLite
```

ở các phần sau.

---

# 15. Query tất cả Chapter của một Novel

Ta chưa học JOIN, nên hiện tại chỉ truy vấn một bảng:

```python
rows = conn.execute(
    """
    SELECT
        id,
        novel_id,
        chapter_number,
        title
    FROM chapters
    WHERE novel_id = ?
    ORDER BY chapter_number
    """,
    (novel_id,),
).fetchall()
```

Sau đó:

```python
for row in rows:
    print(
        row["chapter_number"],
        row["title"],
    )
```

Kết quả:

```text
1 Chương 1
2 Chương 2
3 Chương 3
```

---

# 16. Lấy Chapter mới nhất

Một query rất thực tế đối với crawler:

```sql
SELECT
    id,
    novel_id,
    chapter_number,
    title
FROM chapters
WHERE novel_id = ?
ORDER BY chapter_number DESC
LIMIT 1;
```

Python:

```python
row = conn.execute(
    """
    SELECT
        id,
        novel_id,
        chapter_number,
        title
    FROM chapters
    WHERE novel_id = ?
    ORDER BY chapter_number DESC
    LIMIT 1
    """,
    (novel_id,),
).fetchone()
```

Đây là query mà crawler sẽ dùng rất nhiều.

---

# 17. Đếm Chapter của Novel

```sql
SELECT COUNT(*)
FROM chapters
WHERE novel_id = ?;
```

Python:

```python
count = conn.execute(
    """
    SELECT COUNT(*)
    FROM chapters
    WHERE novel_id = ?
    """,
    (novel_id,),
).fetchone()[0]
```

Ví dụ:

```text
Novel: Tiên Nghịch
Chapter count: 1200
```

---

# 18. Repository

Đây là lúc kiến thức SQL bắt đầu kết nối với kiến trúc chúng ta đã học.

```python
class ChapterRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def add(
        self,
        novel_id: int,
        chapter_number: int,
        title: str,
        content: str,
    ) -> int:

        cursor = self._conn.execute(
            """
            INSERT INTO chapters (
                novel_id,
                chapter_number,
                title,
                content
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                novel_id,
                chapter_number,
                title,
                content,
            ),
        )

        return cursor.lastrowid

    def get_by_novel(
        self,
        novel_id: int,
    ):

        return self._conn.execute(
            """
            SELECT
                id,
                novel_id,
                chapter_number,
                title,
                content
            FROM chapters
            WHERE novel_id = ?
            ORDER BY chapter_number
            """,
            (novel_id,),
        ).fetchall()

    def count_by_novel(
        self,
        novel_id: int,
    ) -> int:

        return self._conn.execute(
            """
            SELECT COUNT(*)
            FROM chapters
            WHERE novel_id = ?
            """,
            (novel_id,),
        ).fetchone()[0]
```

---

# 19. Một transaction thực tế của crawler

Giả sử crawler phát hiện một novel mới:

```text
Crawler
   ↓
Create Novel
   ↓
Get novel_id
   ↓
Create Chapter 1
   ↓
Create Chapter 2
   ↓
Create Chapter 3
   ↓
COMMIT
```

Python:

```python
try:
    cursor = conn.execute(
        """
        INSERT INTO novels (title, author)
        VALUES (?, ?)
        """,
        ("Tiên Nghịch", "Nhĩ Căn"),
    )

    novel_id = cursor.lastrowid

    conn.executemany(
        """
        INSERT INTO chapters (
            novel_id,
            chapter_number,
            title,
            content
        )
        VALUES (?, ?, ?, ?)
        """,
        [
            (novel_id, 1, "Chương 1", "Content 1"),
            (novel_id, 2, "Chương 2", "Content 2"),
            (novel_id, 3, "Chương 3", "Content 3"),
        ],
    )

    conn.commit()

except Exception:
    conn.rollback()
    raise
```

Nếu Chapter 3 lỗi:

```text
Novel INSERT
    ↓
Chapter 1
    ↓
Chapter 2
    ↓
Chapter 3 ❌
    ↓
ROLLBACK
```

Kết quả:

```text
Novel ❌
Chapter 1 ❌
Chapter 2 ❌
```

Không xảy ra tình trạng dữ liệu nửa vời.

---

# 20. Một lỗi thiết kế rất phổ biến

Không nên lưu:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER,
    novel_title TEXT,
    chapter_number INTEGER
);
```

vì:

```text
novels
id = 1
title = "Tiên Nghịch"
```

và:

```text
chapters
novel_id = 1
novel_title = "Tiên Nghịch"
```

Ta đang lưu cùng một thông tin hai lần.

Nếu title thay đổi:

```text
novels.title
```

có thể thành:

```text
Tiên Nghịch - Updated
```

nhưng:

```text
chapters.novel_title
```

vẫn là:

```text
Tiên Nghịch
```

→ dữ liệu không nhất quán.

Thay vào đó:

```text
chapters.novel_id
       ↓
    novels.id
       ↓
    novels.title
```

Sau này JOIN sẽ giúp lấy title.

---

# 21. Mô hình chuẩn cho app của bạn

Hiện tại ta có:

```text
novels
────────────────────
id PK
source
title
author
url
status
created_at
updated_at

          │
          │ 1
          │
          │ N
          ▼

chapters
────────────────────
id PK
novel_id FK
chapter_number
title
content
created_at
updated_at

UNIQUE (
    novel_id,
    chapter_number
)
```

Đây là một schema nền tảng rất tốt cho hệ thống crawl truyện.

---

# 22. Mental Model cần nhớ

Khi gặp câu:

> "Một A có nhiều B"

hãy lập tức nghĩ:

```text
A = Parent
B = Child

B chứa FK → A
```

Ví dụ:

```text
Novel → Chapter
User → Order
Order → OrderItem
Category → Product
Author → Book
```

đều có thể là:

```text
Parent
   1
   │
   N
Child
```

---

# 23. Tổng kết Buổi 16

### Quy tắc số 1

> **FK nằm ở phía Many.**

```text
Novel 1 ───── N Chapter

chapters.novel_id
       ↓
   FK → novels.id
```

### Quy tắc số 2

1–N:

```sql
novel_id INTEGER NOT NULL
```

Không `UNIQUE`.

### Quy tắc số 3

Nếu cần chapter number duy nhất **trong từng novel**:

```sql
UNIQUE (novel_id, chapter_number)
```

### Quy tắc số 4

Nếu xóa Novel và muốn xóa Chapter:

```sql
ON DELETE CASCADE
```

### Quy tắc số 5

Bật FK:

```python
conn.execute("PRAGMA foreign_keys = ON")
```

---

## Bài tập Buổi 16

Hãy tự xây schema:

```text
novels
chapters
```

với các yêu cầu:

1. Một novel có nhiều chapter.
2. Chapter bắt buộc phải thuộc novel.
3. Không được có hai chapter cùng `chapter_number` trong cùng novel.
4. Xóa novel → xóa toàn bộ chapter.
5. Insert chapter với `novel_id` không tồn tại phải thất bại.

Sau đó viết 4 function:

```python
create_novel(...)
create_chapter(...)
get_chapters_by_novel(...)
get_latest_chapter(...)
```

và test trường hợp:

```text
Novel A
 ├── Chapter 1
 ├── Chapter 2
 └── Chapter 3

Novel B
 ├── Chapter 1
 └── Chapter 2
```

Đặc biệt hãy thử tạo:

```text
Novel A → Chapter 1
Novel A → Chapter 1
```

và quan sát `UNIQUE (novel_id, chapter_number)` bảo vệ database như thế nào.

---

### Roadmap hiện tại

```text
14 FOREIGN KEY          ✅
15 One-to-One           ✅
16 One-to-Many          ✅ ← hiện tại
17 Many-to-Many
18 JOIN
19 INNER JOIN
20 LEFT JOIN
21 JOIN nhiều bảng
22 Subquery
23 EXISTS
```

**Buổi 17 — Many-to-Many** sẽ rất đáng học vì ta sẽ gặp mô hình:

```text
Novel
  │
  │ N
  ▼
NovelTag
  ▲
  │ N
  │
Tag
```

và từ đó xuất hiện khái niệm **junction table / association table**, một pattern cực kỳ quan trọng trong SQL và Repository Pattern.
