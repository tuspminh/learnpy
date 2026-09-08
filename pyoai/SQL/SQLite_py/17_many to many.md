# Buổi 17 — Many-to-Many (N–N) trong SQLite

Sau khi đã học:

```text
14. FOREIGN KEY
15. One-to-One
16. One-to-Many
17. Many-to-Many  ← hôm nay
```

ta đi đến loại quan hệ cuối cùng trong nhóm quan hệ cơ bản.

Đây cũng là nền tảng trực tiếp để học **JOIN ở Buổi 18**.

---

# 1. Many-to-Many là gì?

Many-to-Many nghĩa là:

> Một A có thể liên kết với nhiều B, và một B cũng có thể liên kết với nhiều A.

Ví dụ rất tự nhiên trong app truyện:

```text
Novel
  │
  ├──────── Tag
  │
  ├──────── Tag
  │
  └──────── Tag
```

Nhưng một Tag cũng có thể thuộc nhiều Novel:

```text
Tag: Tiên hiệp
   │
   ├── Tiên Nghịch
   ├── Phàm Nhân Tu Tiên
   ├── Đấu Phá Thương Khung
   └── ...
```

Do đó:

```text
Novel N ───── N Tag
```

---

# 2. Tại sao không thể đặt một FOREIGN KEY đơn giản?

Giả sử:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
```

Ta muốn:

```text
Novel 1
 ├── Tiên hiệp
 ├── Huyền huyễn
 └── Trọng sinh
```

Nếu thêm:

```sql
tag_id INTEGER
```

vào `novels`:

```text
novels
────────────────
id
title
tag_id
```

thì mỗi Novel chỉ có **một tag**.

Không đáp ứng được:

```text
Novel 1
 ├── Tag A
 ├── Tag B
 └── Tag C
```

---

Nếu ngược lại thêm:

```sql
novel_id INTEGER
```

vào `tags`:

```text
tags
────────────────
id
name
novel_id
```

thì mỗi Tag chỉ thuộc một Novel.

Cũng sai.

---

# 3. Giải pháp: Junction Table

Đây là pattern quan trọng nhất của Many-to-Many.

Ta tạo thêm một bảng trung gian:

```text
novels
   │
   │
   ▼
novel_tags
   ▲
   │
   │
tags
```

Hay đầy đủ:

```text
Novel
  │
  │ 1
  ▼
NovelTag
  ▲
  │ 1
  │
 Tag
```

Thực chất:

```text
Novel 1 ─── N NovelTag N ─── 1 Tag
```

Hai quan hệ 1–N kết hợp lại thành:

```text
Novel N ─── N Tag
```

Đây là một insight cực kỳ quan trọng:

> **SQL thường biểu diễn Many-to-Many bằng hai quan hệ One-to-Many thông qua một bảng trung gian.**

---

# 4. Thiết kế database

## Bảng novels

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);
```

## Bảng tags

```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
```

## Bảng trung gian

```sql
CREATE TABLE novel_tags (
    novel_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
        ON DELETE CASCADE,

    FOREIGN KEY (tag_id)
        REFERENCES tags(id)
        ON DELETE CASCADE,

    PRIMARY KEY (novel_id, tag_id)
);
```

Đây là một thiết kế rất chuẩn.

---

# 5. Tại sao `PRIMARY KEY (novel_id, tag_id)`?

Đây là:

```text
Composite Primary Key
```

Tức là khóa chính gồm **hai column**:

```sql
PRIMARY KEY (novel_id, tag_id)
```

Ví dụ:

```text
novel_id | tag_id
---------+-------
1        | 1
1        | 2
1        | 3
2        | 1
2        | 2
```

Hợp lệ.

Nhưng:

```text
1 | 1
1 | 1
```

không hợp lệ.

Database sẽ báo:

```text
UNIQUE constraint failed
```

vì cặp:

```text
(1, 1)
```

đã tồn tại.

---

# 6. Hãy nhìn nó như một graph

Giả sử:

```text
Novels:

1 = Tiên Nghịch
2 = Phàm Nhân Tu Tiên
3 = Đấu Phá Thương Khung
```

Tags:

```text
1 = Tiên hiệp
2 = Huyền huyễn
3 = Trọng sinh
```

`novel_tags`:

```text
novel_id | tag_id
---------+-------
1        | 1
1        | 2
1        | 3
2        | 1
2        | 2
3        | 2
```

Ta có:

```text
Tiên Nghịch
 ├── Tiên hiệp
 ├── Huyền huyễn
 └── Trọng sinh

Phàm Nhân Tu Tiên
 ├── Tiên hiệp
 └── Huyền huyễn

Đấu Phá Thương Khung
 └── Huyền huyễn
```

---

# 7. Python tạo database

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row

<<<<<<< HEAD
conn.execute("PRAGMA foreign_keys = ON")
=======
conn.execute(
    "PRAGMA foreign_keys = ON"
)
>>>>>>> a2efe0f3f956d1c15c851e4a1c1f5d840df958a4
```

Tạo schema:

```python
conn.executescript(
    """
    CREATE TABLE novels (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL
    );

    CREATE TABLE tags (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE novel_tags (
        novel_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,

        FOREIGN KEY (novel_id)
            REFERENCES novels(id)
            ON DELETE CASCADE,

        FOREIGN KEY (tag_id)
            REFERENCES tags(id)
            ON DELETE CASCADE,

        PRIMARY KEY (novel_id, tag_id)
    );
    """
)
```

---

# 8. Insert Novel

```python
cursor = conn.execute(
    """
    INSERT INTO novels (title)
    VALUES (?)
    """,
    ("Tiên Nghịch",),
)

novel_id = cursor.lastrowid
```

Ví dụ:

```text
novel_id = 1
```

---

# 9. Insert Tags

```python
conn.executemany(
    """
    INSERT INTO tags (name)
    VALUES (?)
    """,
    [
        ("Tiên hiệp",),
        ("Huyền huyễn",),
        ("Trọng sinh",),
    ],
)

conn.commit()
```

---

# 10. Tạo quan hệ Novel → Tag

Giả sử:

```text
Tiên hiệp = tag 1
Huyền huyễn = tag 2
Trọng sinh = tag 3
```

Ta insert:

```python
conn.executemany(
    """
    INSERT INTO novel_tags (
        novel_id,
        tag_id
    )
    VALUES (?, ?)
    """,
    [
        (1, 1),
        (1, 2),
        (1, 3),
    ],
)

conn.commit()
```

Database lúc này:

```text
novel_tags

1 | 1
1 | 2
1 | 3
```

---

# 11. Tại sao `novel_tags` không cần `id`?

Bạn có thể thiết kế:

```sql
CREATE TABLE novel_tags (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL
);
```

Nhưng nếu `novel_tags` chỉ đơn giản biểu diễn:

> Novel X được gắn Tag Y

thì:

```sql
PRIMARY KEY (novel_id, tag_id)
```

thường đẹp hơn.

Vì bản thân cặp:

```text
(novel_id, tag_id)
```

đã chính là identity của relationship.

---

# 12. Khi nào cần `id` riêng?

Nếu relationship có **dữ liệu riêng**, ví dụ:

```text
novel_tags
────────────────────
id
novel_id
tag_id
created_at
created_by
priority
```

thì có thể cần:

```sql
id INTEGER PRIMARY KEY
```

Ví dụ:

```sql
CREATE TABLE novel_tags (
    id INTEGER PRIMARY KEY,

    novel_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,

    priority INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id),

    FOREIGN KEY (tag_id)
        REFERENCES tags(id),

    UNIQUE (novel_id, tag_id)
);
```

Điểm quan trọng:

> Có `id` riêng không có nghĩa là bỏ `UNIQUE (novel_id, tag_id)`.

Vẫn cần đảm bảo một Novel không gắn cùng một Tag hai lần.

---

# 13. Thêm Tag cho Novel

Ta có:

```python
def add_tag_to_novel(
    conn: sqlite3.Connection,
    novel_id: int,
    tag_id: int,
) -> None:

    conn.execute(
        """
        INSERT INTO novel_tags (
            novel_id,
            tag_id
        )
        VALUES (?, ?)
        """,
        (novel_id, tag_id),
    )
```

Gọi:

```python
add_tag_to_novel(conn, 1, 1)
add_tag_to_novel(conn, 1, 2)
add_tag_to_novel(conn, 1, 3)

conn.commit()
```

---

# 14. Xóa Tag khỏi Novel

Đây là thao tác rất thường gặp.

```python
def remove_tag_from_novel(
    conn: sqlite3.Connection,
    novel_id: int,
    tag_id: int,
) -> None:

    conn.execute(
        """
        DELETE FROM novel_tags
        WHERE novel_id = ?
          AND tag_id = ?
        """,
        (novel_id, tag_id),
    )
```

Ví dụ:

```python
remove_tag_from_novel(conn, 1, 3)

conn.commit()
```

Kết quả:

```text
1 | 1
1 | 2
```

Novel vẫn tồn tại.

Tag vẫn tồn tại.

Chỉ **relationship** bị xóa.

Đây là điểm rất quan trọng.

---

# 15. Xóa Novel

Với:

```sql
FOREIGN KEY (novel_id)
REFERENCES novels(id)
ON DELETE CASCADE
```

nếu:

```sql
DELETE FROM novels
WHERE id = 1;
```

thì:

```text
Novel 1
   ↓
novel_tags
   ↓
mọi relationship của Novel 1
```

bị xóa.

Nhưng:

```text
tags
```

không bị xóa.

Ví dụ:

```text
Tiên Nghịch ❌

novel_tags
1 | 1 ❌
1 | 2 ❌
1 | 3 ❌

tags
Tiên hiệp ✅
Huyền huyễn ✅
Trọng sinh ✅
```

Đây chính là hành vi ta thường mong muốn.

---

# 16. Xóa Tag

Tương tự:

```sql
DELETE FROM tags
WHERE id = 2;
```

Với:

```sql
ON DELETE CASCADE
```

mọi relationship:

```text
novel_tags
novel_id | tag_id
---------+--------
1        | 2
2        | 2
3        | 2
```

sẽ bị xóa.

Nhưng:

```text
novels
```

không bị ảnh hưởng.

---

# 17. Một câu SQL rất quan trọng

Ta muốn:

> Tìm tất cả Tag của Novel có id = 1.

Hiện tại chưa học JOIN, nhưng hãy nhìn trước:

```sql
SELECT tag_id
FROM novel_tags
WHERE novel_id = ?;
```

Kết quả:

```text
1
2
3
```

Nhưng ta muốn:

```text
Tiên hiệp
Huyền huyễn
Trọng sinh
```

Để lấy được `tags.name`, ta sẽ cần **JOIN**.

Đó chính là lý do:

```text
Buổi 17
Many-to-Many
       ↓
Buổi 18
JOIN
```

---

# 18. Repository Design

Ta có thể tạo:

```text
NovelRepository
TagRepository
NovelTagRepository
```

Ví dụ:

```python
class NovelTagRepository:
<<<<<<< HEAD
=======

>>>>>>> a2efe0f3f956d1c15c851e4a1c1f5d840df958a4
    def __init__(
        self,
        conn: sqlite3.Connection,
    ):
        self._conn = conn

    def add(
        self,
        novel_id: int,
        tag_id: int,
    ) -> None:

        self._conn.execute(
            """
            INSERT INTO novel_tags (
                novel_id,
                tag_id
            )
            VALUES (?, ?)
            """,
            (novel_id, tag_id),
        )

    def remove(
        self,
        novel_id: int,
        tag_id: int,
    ) -> None:

        self._conn.execute(
            """
            DELETE FROM novel_tags
            WHERE novel_id = ?
              AND tag_id = ?
            """,
            (novel_id, tag_id),
        )
```

Repository này quản lý **relationship** chứ không quản lý Novel hay Tag.

Đây là một cách phân tách khá rõ ràng.

---

# 19. Một vấn đề thực tế: Tag đã tồn tại chưa?

Crawler có thể gặp:

```text
Novel:
Tiên Nghịch

Tags:
Tiên hiệp
Huyền huyễn
Trọng sinh
```

Nhưng:

```text
Tiên hiệp
```

có thể đã tồn tại.

Không nên mỗi lần crawler lại:

```sql
INSERT INTO tags (name)
VALUES ('Tiên hiệp');
```

vì:

```sql
name TEXT UNIQUE
```

sẽ gây lỗi.

Một pattern sau này chúng ta sẽ học sâu là:

```text
UPSERT
```

hoặc:

```sql
INSERT ... ON CONFLICT ...
```

Hiện tại chỉ cần hiểu vấn đề.

---

# 20. Một transaction hoàn chỉnh

Ví dụ crawler thêm Novel + Tags + relationships:

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

    # giả sử tag_id đã tồn tại
    conn.executemany(
        """
        INSERT INTO novel_tags (
            novel_id,
            tag_id
        )
        VALUES (?, ?)
        """,
        [
            (novel_id, 1),
            (novel_id, 2),
            (novel_id, 3),
        ],
    )

    conn.commit()

except Exception:
    conn.rollback()
    raise
```

Nếu relationship thứ ba thất bại:

```text
INSERT Novel
      ↓
INSERT relationship 1
      ↓
INSERT relationship 2
      ↓
INSERT relationship 3 ❌
      ↓
ROLLBACK
```

Toàn bộ transaction được hoàn tác.

---

# 21. Ba loại quan hệ cần thuộc lòng

Bây giờ bạn đã có một mental model hoàn chỉnh.

## 1–1

```text
Novel ───── NovelMetadata
  1              1
```

Schema:

```sql
novel_id INTEGER PRIMARY KEY
```

hoặc:

```sql
novel_id INTEGER UNIQUE
```

---

## 1–N

```text
Novel
  │
  ├── Chapter
  ├── Chapter
  └── Chapter
```

Schema:

```sql
chapters.novel_id
```

là FK.

Không UNIQUE.

---

## N–N

```text
Novel
  │
  N
  │
NovelTag
  │
  N
  │
Tag
```

Schema:

```text
novel_tags
├── novel_id FK
└── tag_id FK
```

và thường:

```sql
PRIMARY KEY (novel_id, tag_id)
```

---

# 22. Công thức cực kỳ quan trọng

Hãy nhớ:

```text
1–1
    FK + UNIQUE

1–N
    FK ở phía N

N–N
    Bảng trung gian
    + FK A
    + FK B
```

Hay:

```text
         1–1
    FK + UNIQUE

         1–N
    FK ở Many

         N–N
    Junction Table
```

---

# 23. Áp dụng vào app truyện

Database của chúng ta bây giờ có thể tiến tới:

```text
                         ┌──────────────┐
                         │    novels    │
                         │──────────────│
                         │ id           │
                         │ title        │
                         │ author       │
                         └──────┬───────┘
                                │
                           1    │    N
                                │
                         ┌──────▼───────┐
                         │   chapters   │
                         │──────────────│
                         │ id           │
                         │ novel_id     │
                         │ chapter_no   │
                         │ title        │
                         │ content      │
                         └──────────────┘


        ┌──────────────┐
        │    novels    │
        └──────┬───────┘
               │
              N│
               │
        ┌──────▼───────┐
        │  novel_tags  │
        └──────┬───────┘
               │
              N│
               │
        ┌──────▼───────┐
        │     tags     │
        └──────────────┘
```

Đây đã bắt đầu trở thành một **relational model thực sự**.

---

# 24. Bài tập Buổi 17

## Bài 1 — Schema

Tạo:

```text
novels
tags
novel_tags
```

với:

```text
Novel N ─── N Tag
```

Yêu cầu:

* `novels.id` PK
* `tags.id` PK
* `tags.name` UNIQUE
* `novel_tags.novel_id` FK
* `novel_tags.tag_id` FK
* `(novel_id, tag_id)` là PK
* cả hai FK có `ON DELETE CASCADE`

---

## Bài 2 — Dữ liệu

Tạo:

```text
Novel A
 ├── Tiên hiệp
 ├── Huyền huyễn
 └── Trọng sinh

Novel B
 ├── Tiên hiệp
 └── Huyền huyễn
```

Database phải có:

```text
novel_tags

A | Tiên hiệp
A | Huyền huyễn
A | Trọng sinh
B | Tiên hiệp
B | Huyền huyễn
```

---

## Bài 3 — Duplicate

Thử:

```sql
INSERT INTO novel_tags (novel_id, tag_id)
VALUES (1, 1);
```

hai lần.

Giải thích lỗi.

---

## Bài 4 — Xóa relationship

Xóa:

```text
Novel A — Trọng sinh
```

nhưng không được xóa:

```text
Novel A
Trọng sinh
```

Chỉ xóa row trong:

```text
novel_tags
```

---

## Bài 5 — Cascade

Xóa Novel A.

Kiểm tra:

```text
novels
novel_tags
tags
```

Sau khi xóa Novel A, bảng nào mất dữ liệu?

---

## Bài 6 — Thiết kế

Hãy trả lời:

> Tại sao không lưu `tag1`, `tag2`, `tag3` trong bảng `novels`?

Ví dụ:

```text
novels
────────────────
id
title
tag1
tag2
tag3
```

Tại sao thiết kế này không tốt?

Đây là bài rất quan trọng để hiểu **database normalization**.

---

# Tổng kết

Bạn hiện đã đi qua toàn bộ ba loại relationship cơ bản:

```text
14. FOREIGN KEY       ✅
15. One-to-One        ✅
16. One-to-Many       ✅
17. Many-to-Many      ✅
```

Mental model:

```text
1–1
Novel ─── Metadata

1–N
Novel ───< Chapter

N–N
Novel >──< Tag
      ↓
  novel_tags
```

Và pattern quan trọng nhất của hôm nay:

```text
Many-to-Many
      ↓
Junction / Association Table
      ↓
        ┌──────────┐
        │ A_id FK  │
        │ B_id FK  │
        └──────────┘
```

**Buổi 18 — JOIN** sẽ là bước ngoặt: chúng ta sẽ dùng `novels + chapters + tags + novel_tags` để thực hiện những query kiểu:

```text
"Lấy tất cả chapter của Tiên Nghịch"

"Lấy tất cả tag của Tiên Nghịch"

"Lấy tất cả novel có tag Tiên hiệp"

"Lấy novel + số chapter + danh sách tag"
```

và lúc đó bạn sẽ thấy **tại sao JOIN là trái tim của relational SQL**.
