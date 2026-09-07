# Buổi 14 — `FOREIGN KEY` trong SQLite + Python

Từ Buổi 1 → 13, chúng ta chủ yếu làm việc với **một bảng**.

Từ hôm nay, chúng ta bước sang phần cực kỳ quan trọng:

```text
DATABASE RELATIONSHIPS
```

Và bài đầu tiên là:

```sql
FOREIGN KEY
```

Đặc biệt với project crawler truyện của bạn, ta sẽ xây quan hệ:

```text
novels
   │
   └──────< chapters
```

Một novel có nhiều chapter.

---

# 1. Vì sao cần `FOREIGN KEY`?

Giả sử có:

```text
novels

id | title
---+----------------
1  | Tiên Nghịch
2  | Đấu Phá Thương Khung
```

và:

```text
chapters

id | novel_id | chapter_number
---+----------+---------------
1  | 1        | 1
2  | 1        | 2
3  | 1        | 3
4  | 2        | 1
```

Ta hiểu:

```text
chapter 1
   ↓
novel_id = 1
   ↓
Tiên Nghịch
```

`novel_id` trong `chapters` chính là:

```text
FOREIGN KEY
```

---

# 2. `FOREIGN KEY` là gì?

`FOREIGN KEY` là một constraint dùng để:

> **Đảm bảo giá trị ở bảng con tham chiếu đến một record hợp lệ ở bảng cha.**

Ví dụ:

```sql
FOREIGN KEY (novel_id)
REFERENCES novels(id)
```

Nghĩa là:

```text
chapters.novel_id
       ↓
   references
       ↓
novels.id
```

---

# 3. Parent và Child

Hai khái niệm này rất quan trọng.

```text
novels
```

là:

```text
Parent table
```

```text
chapters
```

là:

```text
Child table
```

Quan hệ:

```text
novels
  │
  │ 1
  │
  └──────────< chapters
                N
```

Nói cách khác:

> Một novel có nhiều chapter.

---

# 4. Tạo bảng `novels`

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);
```

Ví dụ:

```text
id | title
---+------------------
1  | Tiên Nghịch
2  | Đấu Phá Thương Khung
```

---

# 5. Tạo bảng `chapters`

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

Điểm quan trọng:

```sql
FOREIGN KEY (novel_id)
REFERENCES novels(id)
```

---

# 6. Ý nghĩa của constraint này

Sau khi có:

```text
novels
id
--
1
2
```

thì:

```text
chapters.novel_id
```

hợp lệ nếu:

```text
1
2
```

nhưng:

```text
999
```

không hợp lệ nếu novel `999` không tồn tại.

Database có thể ngăn dữ liệu mồ côi:

```text
chapter
   ↓
novel_id = 999
   ↓
???
```

Đây gọi là:

```text
orphan record
```

---

# 7. SQLite có một điểm rất quan trọng

Trong SQLite:

> **Foreign key enforcement không mặc định luôn được bật.**

Vì vậy khi dùng SQLite với Python, hãy bật:

```sql
PRAGMA foreign_keys = ON;
```

Ví dụ:

```python
conn = sqlite3.connect("novel.db")

conn.execute("PRAGMA foreign_keys = ON")
```

Đây là điều bạn cần đặc biệt nhớ khi xây project SQLite.

---

# 8. Kiểm tra Foreign Key

Có thể:

```python
row = conn.execute(
    "PRAGMA foreign_keys"
).fetchone()

print(row[0])
```

Nếu:

```text
1
```

→ đang bật.

Nếu:

```text
0
```

→ đang tắt.

---

# 9. Python Connection Manager

Về sau bạn không muốn viết:

```python
conn = sqlite3.connect(...)

conn.execute("PRAGMA foreign_keys = ON")
```

ở khắp nơi.

Ta có thể encapsulate:

```python
import sqlite3


class ConnectionManager:

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect("novel.db")

        conn.row_factory = sqlite3.Row

        conn.execute(
            "PRAGMA foreign_keys = ON"
        )

        return conn
```

Đây sẽ liên kết trực tiếp với những gì bạn đã học về:

```text
SQLite Connection Manager
Unit of Work
Repository
```

sau này.

---

# 10. Insert Parent trước

Đầu tiên:

```sql
INSERT INTO novels (title)
VALUES ('Tiên Nghịch');
```

Giả sử:

```text
novel_id = 1
```

Sau đó:

```sql
INSERT INTO chapters (
    novel_id,
    chapter_number,
    title
)
VALUES (?, ?, ?);
```

Python:

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
    (1, 1, "Chương 1"),
)
```

Hợp lệ vì:

```text
chapters.novel_id = 1
```

và:

```text
novels.id = 1
```

đang tồn tại.

---

# 11. Insert Child không tồn tại Parent

Thử:

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
    (999, 1, "Chương 1"),
)
```

Nếu:

```sql
PRAGMA foreign_keys = ON;
```

SQLite sẽ từ chối.

Thông thường sẽ nhận:

```text
sqlite3.IntegrityError
```

với lỗi dạng:

```text
FOREIGN KEY constraint failed
```

Đây chính là database đang bảo vệ tính toàn vẹn dữ liệu.

---

# 12. `FOREIGN KEY` là Database Invariant

Đây là cách tư duy quan trọng.

Nếu application có:

```python
if novel_exists(novel_id):
    insert_chapter()
```

thì vẫn có race condition hoặc bug logic nếu chỉ dựa vào Python.

Database constraint:

```sql
FOREIGN KEY (novel_id)
REFERENCES novels(id)
```

là lớp bảo vệ cuối cùng.

Ta có:

```text
Application validation
        ↓
Repository
        ↓
SQLite constraint
```

Database không nên hoàn toàn tin application.

---

# 13. `NOT NULL` rất quan trọng

Ta viết:

```sql
novel_id INTEGER NOT NULL
```

chứ không:

```sql
novel_id INTEGER
```

Nếu không có `NOT NULL`, có thể tồn tại:

```text
chapter
novel_id = NULL
```

Điều này có thể phá vỡ invariant:

> Chapter phải thuộc về một novel.

Do đó:

```sql
novel_id INTEGER NOT NULL
```

rất hợp lý.

---

# 14. `FOREIGN KEY` không tự tạo index

Đây là một điểm SQLite quan trọng.

Khi bạn viết:

```sql
FOREIGN KEY (novel_id)
REFERENCES novels(id)
```

không có nghĩa rằng:

```text
chapters.novel_id
```

tự động có index.

Trong project crawler, chúng ta thường query:

```sql
SELECT *
FROM chapters
WHERE novel_id = ?;
```

Do đó có thể tạo:

```sql
CREATE INDEX idx_chapters_novel_id
ON chapters(novel_id);
```

Phần index chúng ta sẽ học sâu hơn ở Part V.

---

# 15. Một constraint rất hữu ích cho Chapter

Giả sử:

```text
novel_id = 1
chapter_number = 1
```

không được xuất hiện hai lần.

Ta có:

```sql
UNIQUE (
    novel_id,
    chapter_number
)
```

Full schema:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,

    novel_id INTEGER NOT NULL,

    chapter_number INTEGER NOT NULL,

    title TEXT NOT NULL,

    content TEXT,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id),

    UNIQUE (
        novel_id,
        chapter_number
    )
);
```

Điều này tạo invariant:

```text
Một novel không thể có
hai chapter cùng chapter_number.
```

---

# 16. Đây là database design tốt

Ta có:

```text
novels
│
├── id PK
├── title
└── ...

chapters
│
├── id PK
├── novel_id FK
├── chapter_number
├── title
├── content
└── UNIQUE(novel_id, chapter_number)
```

Quan hệ:

```text
novels.id
    ↑
    │
chapters.novel_id
```

---

# 17. `ON DELETE`

Bây giờ có một vấn đề:

Nếu xóa:

```text
novel id = 1
```

thì chapter:

```text
novel_id = 1
```

sẽ thế nào?

Đây là nơi:

```sql
ON DELETE
```

xuất hiện.

---

# 18. `ON DELETE CASCADE`

Ta có thể viết:

```sql
FOREIGN KEY (novel_id)
    REFERENCES novels(id)
    ON DELETE CASCADE
```

Nghĩa là:

```text
DELETE novel
      ↓
DELETE tất cả chapters
      ↓
có novel_id tương ứng
```

Ví dụ:

```text
novels
1 Tiên Nghịch

chapters
1 → novel_id 1
2 → novel_id 1
3 → novel_id 1
```

Xóa:

```sql
DELETE FROM novels
WHERE id = 1;
```

thì:

```text
novel 1       → deleted
chapter 1     → deleted
chapter 2     → deleted
chapter 3     → deleted
```

---

# 19. Với app crawler truyện, `CASCADE` có hợp lý?

Thường là **có thể hợp lý** nếu:

> Chapter không có ý nghĩa độc lập khi novel bị xóa.

Mô hình:

```text
Novel
  └── Chapters
```

Chapter phụ thuộc mạnh vào Novel.

Do đó:

```sql
ON DELETE CASCADE
```

thường là lựa chọn hợp lý.

Nhưng phải hiểu rõ hậu quả.

Một:

```sql
DELETE novels
```

có thể xóa **hàng nghìn chapters**.

---

# 20. `ON DELETE RESTRICT`

Có thể chọn:

```sql
ON DELETE RESTRICT
```

Ý nghĩa:

> Không cho xóa parent nếu vẫn còn child.

Ví dụ:

```text
novel 1
  ├── chapter 1
  ├── chapter 2
  └── chapter 3
```

Thử:

```sql
DELETE FROM novels
WHERE id = 1;
```

→ bị từ chối.

Application phải xử lý chapters trước.

---

# 21. `ON DELETE SET NULL`

Một lựa chọn khác:

```sql
ON DELETE SET NULL
```

Khi parent bị xóa:

```text
novel
  ↓
deleted
```

thì:

```text
chapter.novel_id
```

trở thành:

```text
NULL
```

Nhưng nếu schema:

```sql
novel_id INTEGER NOT NULL
```

thì thiết kế này không phù hợp.

Đây là lý do các constraint phải được thiết kế **cùng nhau**.

---

# 22. Ba chiến lược quan trọng

| Action     | Ý nghĩa              |
| ---------- | -------------------- |
| `CASCADE`  | Xóa child            |
| `RESTRICT` | Không cho xóa parent |
| `SET NULL` | Child mất liên kết   |

Với:

```text
Novel → Chapter
```

thường ta sẽ cân nhắc:

```text
CASCADE
```

nếu chapter sống phụ thuộc novel.

---

# 23. `ON UPDATE`

SQLite cũng hỗ trợ:

```sql
ON UPDATE CASCADE
```

Ví dụ:

```sql
FOREIGN KEY (novel_id)
REFERENCES novels(id)
ON UPDATE CASCADE
ON DELETE CASCADE
```

Nhưng với:

```sql
id INTEGER PRIMARY KEY
```

thực tế chúng ta thường không thay đổi ID.

Do đó `ON UPDATE` ít quan trọng hơn `ON DELETE`.

---

# 24. Full schema cho project

Một phiên bản tốt:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,

    source TEXT NOT NULL,

    title TEXT NOT NULL,

    author TEXT,

    url TEXT NOT NULL,

    status TEXT NOT NULL
        DEFAULT 'ongoing'
        CHECK (
            status IN (
                'ongoing',
                'completed'
            )
        ),

    created_at TEXT NOT NULL,

    updated_at TEXT NOT NULL
);
```

Chapter:

```sql
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY,

    novel_id INTEGER NOT NULL,

    chapter_number INTEGER NOT NULL,

    title TEXT NOT NULL,

    content TEXT,

    created_at TEXT NOT NULL,

    updated_at TEXT NOT NULL,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
        ON DELETE CASCADE,

    UNIQUE (
        novel_id,
        chapter_number
    )
);
```

Đây đã là một schema khá tốt để bắt đầu project crawler.

---

# 25. Python tạo database

```python
import sqlite3


def create_database() -> sqlite3.Connection:
    conn = sqlite3.connect("novel.db")

    conn.row_factory = sqlite3.Row

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS novels (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS chapters (
            id INTEGER PRIMARY KEY,
            novel_id INTEGER NOT NULL,
            chapter_number INTEGER NOT NULL,
            title TEXT NOT NULL,

            FOREIGN KEY (novel_id)
                REFERENCES novels(id)
                ON DELETE CASCADE,

            UNIQUE (
                novel_id,
                chapter_number
            )
        );
        """
    )

    conn.commit()

    return conn
```

---

# 26. Insert Novel + Chapters

```python
conn = create_database()

cursor = conn.execute(
    """
    INSERT INTO novels (title)
    VALUES (?)
    """,
    ("Tiên Nghịch",),
)

novel_id = cursor.lastrowid
```

Sau đó:

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
    (novel_id, 1, "Chương 1"),
)
```

Tiếp:

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
    (novel_id, 2, "Chương 2"),
)
```

Cuối cùng:

```python
conn.commit()
```

---

# 27. Transaction rất quan trọng

Crawler có thể thực hiện:

```text
INSERT novel
      ↓
INSERT chapter 1
      ↓
INSERT chapter 2
      ↓
INSERT chapter 3
```

Nếu chapter 3 lỗi:

```text
❌
```

Ta không muốn:

```text
novel tồn tại
chapter 1 tồn tại
chapter 2 tồn tại
chapter 3 thất bại
```

nếu nghiệp vụ yêu cầu tất cả phải thành công cùng nhau.

Do đó:

```python
try:
    cursor = conn.execute(
        """
        INSERT INTO novels (title)
        VALUES (?)
        """,
        ("Tiên Nghịch",),
    )

    novel_id = cursor.lastrowid

    conn.execute(
        """
        INSERT INTO chapters (
            novel_id,
            chapter_number,
            title
        )
        VALUES (?, ?, ?)
        """,
        (novel_id, 1, "Chương 1"),
    )

    conn.execute(
        """
        INSERT INTO chapters (
            novel_id,
            chapter_number,
            title
        )
        VALUES (?, ?, ?)
        """,
        (novel_id, 2, "Chương 2"),
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
  ├── insert novel
  ├── insert chapter
  ├── insert chapter
  │
  ├── OK → COMMIT
  │
  └── ERROR → ROLLBACK
```

Đây chính là nền tảng của **Unit of Work** mà bạn đã học ở các phiên trước.

---

# 28. Kiểm tra quan hệ bằng Python

Sau khi insert:

```python
rows = conn.execute(
    """
    SELECT
        id,
        novel_id,
        chapter_number,
        title
    FROM chapters
    ORDER BY chapter_number
    """
).fetchall()
```

Ta có:

```python
for row in rows:
    print(
        row["novel_id"],
        row["chapter_number"],
        row["title"],
    )
```

---

# 29. Kiểm tra Foreign Key bằng PRAGMA

SQLite cung cấp:

```sql
PRAGMA foreign_key_list(chapters);
```

Python:

```python
rows = conn.execute(
    "PRAGMA foreign_key_list(chapters)"
).fetchall()
```

Nó giúp kiểm tra:

```text
chapters.novel_id
       ↓
novels.id
```

Đây là công cụ rất hữu ích khi debug schema.

---

# 30. Một lỗi thiết kế phổ biến

Không nên:

```text
chapters
---------
novel_title
```

thay vì:

```text
chapters
---------
novel_id
```

Ví dụ:

```text
chapter 1 | Tiên Nghịch
chapter 2 | Tiên Nghịch
chapter 3 | Tiên Nghịch
```

Tên novel bị lặp rất nhiều.

Nếu novel đổi tên:

```text
Tiên Nghịch
```

→

```text
Tiên Nghịch - Updated
```

phải update hàng nghìn rows.

Thiết kế tốt:

```text
novels
1 | Tiên Nghịch

chapters
1 | novel_id=1
2 | novel_id=1
3 | novel_id=1
```

---

# 31. Normalization bắt đầu xuất hiện

Đây chính là bước đầu của tư duy:

```text
DATA NORMALIZATION
```

Thay vì:

```text
chapter
chapter
chapter
```

lặp lại:

```text
novel title
novel author
novel url
```

ta tách:

```text
novels
   │
   └── chapters
```

và dùng:

```text
novel_id
```

để liên kết.

Phần normalization sẽ được đào sâu hơn sau khi chúng ta học JOIN và relationships.

---

# 32. Kiến trúc dữ liệu hiện tại

Bạn có thể hình dung:

```text
┌──────────────┐
│    novels    │
├──────────────┤
│ id PK        │
│ title        │
│ author       │
│ source       │
└──────┬───────┘
       │
       │ 1
       │
       │
       │ N
┌──────▼───────┐
│   chapters   │
├──────────────┤
│ id PK        │
│ novel_id FK  │
│ chapter_no   │
│ title        │
│ content      │
└──────────────┘
```

Đây chính là:

```text
One-to-Many
```

Nhưng **Buổi 15** chúng ta mới đi sâu vào bản chất của One-to-One / One-to-Many.

---

# 33. Bài tập Buổi 14

## Bài 1

Tạo:

```sql
novels
chapters
```

với:

```text
novels.id
      ↑
      │
chapters.novel_id
```

---

## Bài 2

Bật:

```sql
PRAGMA foreign_keys = ON;
```

Sau đó thử insert:

```text
novel_id = 999
```

vào `chapters`.

Quan sát exception.

---

## Bài 3

Thêm:

```sql
ON DELETE CASCADE
```

Sau đó:

```text
insert novel
insert 3 chapters
delete novel
```

Kiểm tra chapters.

Kỳ vọng:

```text
novel → deleted
chapters → deleted
```

---

## Bài 4

Thử tạo duplicate:

```text
novel_id = 1
chapter_number = 1
```

hai lần.

Với:

```sql
UNIQUE(novel_id, chapter_number)
```

hãy quan sát lỗi.

---

## Bài 5 — Python

Viết:

```python
def create_novel_with_chapters(
    conn: sqlite3.Connection,
    title: str,
    chapters: list[tuple[int, str]],
) -> int:
    ...
```

Ví dụ:

```python
novel_id = create_novel_with_chapters(
    conn,
    "Tiên Nghịch",
    [
        (1, "Chương 1"),
        (2, "Chương 2"),
        (3, "Chương 3"),
    ],
)
```

Yêu cầu:

```text
INSERT novel
     ↓
lastrowid
     ↓
INSERT chapters
     ↓
COMMIT
```

Nếu bất kỳ chapter nào lỗi:

```text
ROLLBACK
```

---

# 34. Bài tập tư duy quan trọng

Hãy trả lời:

### Câu 1

Tại sao:

```sql
chapters.novel_id
```

nên là:

```sql
INTEGER NOT NULL
```

?

### Câu 2

Tại sao cần:

```sql
FOREIGN KEY (novel_id)
REFERENCES novels(id)
```

?

### Câu 3

Tại sao:

```sql
UNIQUE(novel_id, chapter_number)
```

tốt hơn:

```sql
UNIQUE(chapter_number)
```

?

### Câu 4

Khi nào `ON DELETE CASCADE` nguy hiểm?

### Câu 5

Tại sao phải bật:

```sql
PRAGMA foreign_keys = ON
```

trong SQLite?

Nếu trả lời được 5 câu này, bạn đã hiểu khá chắc nền tảng Foreign Key.

---

# 35. Mental Model cuối buổi

```text
Parent
novels
   │
   │ PK
   ▼
novels.id
   ▲
   │ FK
   │
chapters.novel_id
   │
   ▼
Child
chapters
```

Database đảm bảo:

```text
Child FK
   ↓
phải tham chiếu
   ↓
Parent PK/UNIQUE hợp lệ
```

Và:

```text
FOREIGN KEY
+
NOT NULL
+
UNIQUE
+
ON DELETE
```

cho phép chúng ta biểu diễn **business/data invariants ngay trong database**.

---

## Roadmap

```text
PART III — Relationships

14  FOREIGN KEY                  ✅
15  One-to-One
16  One-to-Many
17  Many-to-Many
18  JOIN
19  INNER JOIN
20  LEFT JOIN
21  JOIN nhiều bảng
22  Subquery
23  EXISTS
```

**Buổi 15 — One-to-One** sẽ bắt đầu từ câu hỏi: *“Khi nào một record A chỉ có đúng một record B?”* và từ đó ta sẽ hiểu sâu hơn cách `UNIQUE + FOREIGN KEY` tạo ra quan hệ 1-1 trong SQLite.
