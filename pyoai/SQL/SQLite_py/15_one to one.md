# Buổi 15 — One-to-One (1–1) trong SQLite

Sau Buổi 14, ta đã biết **Foreign Key** giúp liên kết bảng. Nhưng có một điểm rất quan trọng:

> **FOREIGN KEY không tự biến quan hệ thành 1–1.**

Muốn có quan hệ **One-to-One**, ta cần thêm ràng buộc đảm bảo một bản ghi ở bảng con chỉ được liên kết với **tối đa một** bản ghi ở bảng cha.

---

# 1. One-to-One là gì?

Quan hệ 1–1 nghĩa là:

```text
Novel
  │
  │ 1
  │
  │ 1
  ▼
NovelMetadata
```

Mỗi `novel` có **tối đa một** `novel_metadata`.

Và mỗi `novel_metadata` thuộc về **chính xác một** `novel`.

Ví dụ:

```text
novels
┌────┬───────────────┐
│ id │ title         │
├────┼───────────────┤
│ 1  │ Tiên Nghịch   │
│ 2  │ Phàm Nhân Tu  │
└────┴───────────────┘

novel_metadata
┌──────────┬────────────┬──────────┐
│ novel_id │ rating     │ cover    │
├──────────┼────────────┼──────────┤
│ 1        │ 9.2        │ ...      │
│ 2        │ 8.8        │ ...      │
└──────────┴────────────┴──────────┘
```

Không được phép:

```text
novel_id = 1
novel_id = 1
```

xuất hiện hai lần trong `novel_metadata`.

---

# 2. FOREIGN KEY thôi chưa đủ

Đây là lỗi thiết kế rất dễ gặp.

Ta viết:

```sql
CREATE TABLE novel_metadata (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL,

    rating REAL,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
);
```

Nhìn có vẻ là 1–1.

Nhưng thực tế đây vẫn là:

```text
novels
  1
  │
  ├── metadata A
  ├── metadata B
  └── metadata C
```

Vì database cho phép:

```sql
INSERT INTO novel_metadata (novel_id, rating)
VALUES (1, 9.0);

INSERT INTO novel_metadata (novel_id, rating)
VALUES (1, 9.5);

INSERT INTO novel_metadata (novel_id, rating)
VALUES (1, 9.8);
```

Tất cả đều hợp lệ.

Do đó:

```text
FOREIGN KEY
```

chỉ đảm bảo:

> `novel_id` phải tồn tại trong `novels`.

Nó **không đảm bảo uniqueness**.

---

# 3. Muốn 1–1 → FOREIGN KEY + UNIQUE

Ta thêm:

```sql
UNIQUE (novel_id)
```

Ví dụ:

```sql
CREATE TABLE novel_metadata (
    id INTEGER PRIMARY KEY,

    novel_id INTEGER NOT NULL UNIQUE,

    rating REAL,
    cover_url TEXT,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
);
```

Bây giờ:

```text
novels
  1
  │
  └── metadata
```

Database không cho:

```sql
INSERT INTO novel_metadata (novel_id, rating)
VALUES (1, 9.0);

INSERT INTO novel_metadata (novel_id, rating)
VALUES (1, 9.5);
```

Lệnh thứ hai sẽ lỗi:

```text
UNIQUE constraint failed: novel_metadata.novel_id
```

Đây chính là:

```text
FOREIGN KEY
+
UNIQUE
=
One-to-One
```

---

# 4. Pattern quan trọng nhất: Shared Primary Key

Trong thiết kế 1–1, có một pattern rất đẹp:

```sql
CREATE TABLE novel_metadata (
    novel_id INTEGER PRIMARY KEY,

    rating REAL,
    cover_url TEXT,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
        ON DELETE CASCADE
);
```

Ở đây:

```text
novel_id
   │
   ├── PRIMARY KEY
   │
   └── FOREIGN KEY → novels.id
```

Một column đồng thời là:

```text
PRIMARY KEY
+
FOREIGN KEY
```

## Điều này có ý nghĩa gì?

`PRIMARY KEY` đảm bảo:

```text
novel_id không trùng
```

`FOREIGN KEY` đảm bảo:

```text
novel_id phải tồn tại trong novels
```

Do đó:

```text
novels.id = 1
       │
       ▼
novel_metadata.novel_id = 1
```

chỉ có thể xuất hiện **một lần**.

Đây là pattern tôi đặc biệt khuyến nghị khi bảng con có quan hệ 1–1 thật sự.

---

# 5. Shared Primary Key vs UNIQUE Foreign Key

Có hai cách phổ biến.

## Cách 1 — UNIQUE Foreign Key

```sql
CREATE TABLE novel_metadata (
    id INTEGER PRIMARY KEY,
    novel_id INTEGER NOT NULL UNIQUE,

    rating REAL,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
);
```

Quan hệ:

```text
novel_metadata.id
        │
        └── riêng

novel_metadata.novel_id
        │
        └── UNIQUE FK → novels.id
```

---

## Cách 2 — Shared Primary Key

```sql
CREATE TABLE novel_metadata (
    novel_id INTEGER PRIMARY KEY,

    rating REAL,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
);
```

Quan hệ:

```text
novels.id
    ▲
    │
    │ FK
    │
novel_metadata.novel_id
    │
    └── PRIMARY KEY
```

### Tôi thường ưu tiên cách 2 khi:

`novel_metadata` không có identity riêng.

Nó chỉ tồn tại để mở rộng `novel`.

---

# 6. Ví dụ thực tế với app truyện

Ta có bảng:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT
);
```

Sau đó muốn lưu thêm metadata:

```text
rating
cover_url
description
word_count
```

Có thể thiết kế:

```sql
CREATE TABLE novel_metadata (
    novel_id INTEGER PRIMARY KEY,

    rating REAL,
    cover_url TEXT,
    description TEXT,
    word_count INTEGER,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
        ON DELETE CASCADE
);
```

Kiến trúc:

```text
novels
────────────────────
id
title
author
        │
        │ 1
        │
        │ 1
        ▼
novel_metadata
────────────────────
novel_id
rating
cover_url
description
word_count
```

---

# 7. Insert dữ liệu

Trước tiên phải có `novel`.

```python
cursor.execute(
    """
    INSERT INTO novels (title, author)
    VALUES (?, ?)
    """,
    ("Tiên Nghịch", "Nhĩ Căn"),
)

novel_id = cursor.lastrowid
```

Sau đó:

```python
cursor.execute(
    """
    INSERT INTO novel_metadata (
        novel_id,
        rating,
        cover_url,
        description
    )
    VALUES (?, ?, ?, ?)
    """,
    (
        novel_id,
        9.2,
        "https://example.com/cover.jpg",
        "Một bộ tiên hiệp...",
    ),
)
```

Commit:

```python
conn.commit()
```

---

# 8. Thử vi phạm 1–1

Giả sử:

```text
novel_id = 1
```

đã có metadata.

Ta thử:

```python
cursor.execute(
    """
    INSERT INTO novel_metadata (
        novel_id,
        rating
    )
    VALUES (?, ?)
    """,
    (1, 9.8),
)
```

SQLite sẽ từ chối:

```text
sqlite3.IntegrityError:
UNIQUE constraint failed:
novel_metadata.novel_id
```

Đây là điều chúng ta muốn.

Database đang bảo vệ invariant:

> Một novel không thể có hai metadata record.

---

# 9. 1–1 có bắt buộc phải tồn tại không?

Đây là một vấn đề thiết kế rất quan trọng.

Có hai loại.

## Optional 1–1

```text
Novel
  │
  ├── Metadata
  │
  └── không có Metadata
```

Ví dụ:

```text
novels
1 Tiên Nghịch
2 Phàm Nhân Tu Tiên
3 Đấu Phá Thương Khung

metadata
1 → có
2 → có
3 → chưa có
```

Điều này hoàn toàn hợp lệ.

Bảng `novels` có thể tồn tại mà không có row tương ứng trong `novel_metadata`.

---

## Mandatory 1–1

Yêu cầu:

```text
Mỗi Novel bắt buộc phải có Metadata
```

Vấn đề là:

```sql
FOREIGN KEY
```

ở bảng `novel_metadata` **không tự đảm bảo điều này**.

Nó chỉ đảm bảo:

```text
metadata → novel
```

chứ không đảm bảo:

```text
novel → metadata
```

Đây là một điểm rất quan trọng trong thiết kế database.

SQLite không có một constraint đơn giản kiểu:

```text
"Mỗi row trong novels bắt buộc phải có đúng một row trong novel_metadata"
```

Do đó thường xử lý bằng:

* transaction
* application service
* trigger
* hoặc thiết kế lại schema.

---

# 10. ON DELETE CASCADE trong 1–1

Ta có:

```sql
FOREIGN KEY (novel_id)
REFERENCES novels(id)
ON DELETE CASCADE
```

Khi:

```sql
DELETE FROM novels
WHERE id = 1;
```

SQLite sẽ tự động:

```text
novels
   │
   └── id = 1
          │
          └── DELETE
                ↓
        novel_metadata
        novel_id = 1
                ↓
             DELETE
```

Tức là:

```text
DELETE Novel
      ↓
DELETE Metadata
```

Điều này rất hợp lý nếu metadata không có ý nghĩa độc lập.

---

# 11. Python + transaction

Nếu tạo novel và metadata cùng lúc:

```python
def create_novel(
    conn: sqlite3.Connection,
    title: str,
    author: str | None,
    rating: float | None,
) -> int:

    try:
        cursor = conn.execute(
            """
            INSERT INTO novels (title, author)
            VALUES (?, ?)
            """,
            (title, author),
        )

        novel_id = cursor.lastrowid

        conn.execute(
            """
            INSERT INTO novel_metadata (
                novel_id,
                rating
            )
            VALUES (?, ?)
            """,
            (novel_id, rating),
        )

        conn.commit()

        return novel_id

    except Exception:
        conn.rollback()
        raise
```

Nếu metadata insert thất bại:

```text
INSERT novel
       ↓
INSERT metadata
       ↓
ERROR
       ↓
ROLLBACK
       ↓
Novel cũng không tồn tại
```

Đây là lý do transaction rất quan trọng.

---

# 12. Repository

Trong kiến trúc Repository mà chúng ta đang học, có thể có:

```text
NovelRepository
       │
       └── novels

NovelMetadataRepository
       │
       └── novel_metadata
```

Ví dụ:

```python
class NovelMetadataRepository:
<<<<<<< HEAD
=======

>>>>>>> a2efe0f3f956d1c15c851e4a1c1f5d840df958a4
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def create(
        self,
        novel_id: int,
        rating: float | None,
        cover_url: str | None,
    ) -> None:

        self._conn.execute(
            """
            INSERT INTO novel_metadata (
                novel_id,
                rating,
                cover_url
            )
            VALUES (?, ?, ?)
            """,
            (
                novel_id,
                rating,
                cover_url,
            ),
        )

    def get_by_novel_id(
        self,
        novel_id: int,
    ):
        cursor = self._conn.execute(
            """
            SELECT
                novel_id,
                rating,
                cover_url
            FROM novel_metadata
            WHERE novel_id = ?
            """,
            (novel_id,),
        )

        return cursor.fetchone()
```

Repository chịu trách nhiệm SQL.

Application layer không cần biết:

```sql
INSERT INTO novel_metadata ...
```

---

# 13. Khi nào nên dùng 1–1?

Đừng nghĩ:

> "Có thể tách bảng thì cứ tách."

Không phải lúc nào 1–1 cũng tốt.

Ví dụ ban đầu:

```sql
novels (
    id,
    title,
    author,
    description,
    cover_url,
    rating
)
```

Hoàn toàn có thể giữ nguyên.

Không nhất thiết phải:

```text
novels
     ↓
novel_metadata
```

Chỉ nên tách khi có lý do.

### Trường hợp hợp lý

**1. Metadata là optional**

```text
Novel
  └── Metadata?
```

**2. Lifecycle khác nhau**

```text
Novel
```

tồn tại lâu dài, trong khi:

```text
CrawlState
```

có thể được tạo/xóa riêng.

**3. Có nhiều dữ liệu lớn**

Ví dụ:

```text
novels
    title
    author

novel_detail
    description
    large_text
```

**4. Access pattern khác nhau**

Phần lớn query chỉ cần:

```text
id
title
author
```

không cần load metadata.

**5. Muốn biểu diễn domain rõ ràng**

Ví dụ:

```text
Novel
 ├── basic information
 └── CrawlState
```

---

# 14. So sánh 1–1 và 1–N

Đây là phần cực kỳ quan trọng để tránh nhầm.

### One-to-Many

```text
Novel
  │
  ├── Chapter 1
  ├── Chapter 2
  ├── Chapter 3
  └── Chapter 4
```

Schema:

```sql
novel_id INTEGER NOT NULL
```

Không có `UNIQUE`.

---

### One-to-One

```text
Novel
  │
  └── Metadata
```

Schema:

```sql
novel_id INTEGER PRIMARY KEY
```

hoặc:

```sql
novel_id INTEGER NOT NULL UNIQUE
```

### Điểm khác biệt

```text
1-N:

FOREIGN KEY
    ↓
nhiều row được phép

1-1:

FOREIGN KEY + UNIQUE
    ↓
chỉ một row
```

Hãy ghi nhớ quy tắc này.

---

# 15. Kiểm tra schema

SQLite cho phép xem foreign key:

```python
<<<<<<< HEAD
rows = conn.execute("PRAGMA foreign_key_list(novel_metadata)").fetchall()
=======
rows = conn.execute(
    "PRAGMA foreign_key_list(novel_metadata)"
).fetchall()
>>>>>>> a2efe0f3f956d1c15c851e4a1c1f5d840df958a4

for row in rows:
    print(dict(row))
```

Kiểm tra foreign key:

```python
<<<<<<< HEAD
conn.execute("PRAGMA foreign_keys").fetchone()
=======
conn.execute(
    "PRAGMA foreign_keys"
).fetchone()
>>>>>>> a2efe0f3f956d1c15c851e4a1c1f5d840df958a4
```

Phải là:

```text
1
```

---

# 16. Mini project

Tạo database:

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

    CREATE TABLE novel_metadata (
        novel_id INTEGER PRIMARY KEY,
        rating REAL,
        cover_url TEXT,
        description TEXT,

        FOREIGN KEY (novel_id)
            REFERENCES novels(id)
            ON DELETE CASCADE
    );
    """
)
```

Insert:

```python
conn.execute(
    """
    INSERT INTO novels (title, author)
    VALUES (?, ?)
    """,
    ("Tiên Nghịch", "Nhĩ Căn"),
)
```

Lấy ID:

```python
<<<<<<< HEAD
novel_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
=======
novel_id = conn.execute(
    "SELECT last_insert_rowid()"
).fetchone()[0]
>>>>>>> a2efe0f3f956d1c15c851e4a1c1f5d840df958a4
```

Insert metadata:

```python
conn.execute(
    """
    INSERT INTO novel_metadata (
        novel_id,
        rating,
        cover_url,
        description
    )
    VALUES (?, ?, ?, ?)
    """,
    (
        novel_id,
        9.2,
        "cover.jpg",
        "Tiên hiệp...",
    ),
)

conn.commit()
```

Kiểm tra:

```python
row = conn.execute(
    """
    SELECT *
    FROM novel_metadata
    WHERE novel_id = ?
    """,
    (novel_id,),
).fetchone()

print(dict(row))
```

---

# 17. Bài tập Buổi 15

### Bài 1

Thiết kế:

```text
novels
novel_metadata
```

với quan hệ:

```text
Novel 1 ─── 1 NovelMetadata
```

Metadata gồm:

```text
novel_id
rating
cover_url
description
```

---

### Bài 2

Chứng minh rằng:

```sql
FOREIGN KEY
```

không đủ để tạo 1–1.

Hãy thử insert:

```text
novel_id = 1
novel_id = 1
```

hai lần.

---

### Bài 3

Sửa lại bằng:

```sql
UNIQUE
```

và quan sát lỗi.

---

### Bài 4

Thiết kế lại bằng:

```sql
novel_id INTEGER PRIMARY KEY
```

và giải thích tại sao nó đảm bảo 1–1.

---

### Bài 5

Test:

```text
DELETE novel
       ↓
metadata có bị xóa không?
```

với:

```sql
ON DELETE CASCADE
```

---

### Bài 6 — Bài quan trọng

Giải thích sự khác nhau:

```sql
novel_id INTEGER NOT NULL
```

```sql
novel_id INTEGER NOT NULL UNIQUE
```

```sql
novel_id INTEGER PRIMARY KEY
```

và:

```sql
FOREIGN KEY (novel_id)
REFERENCES novels(id)
```

Nếu hiểu rõ 4 thứ này thì nền tảng thiết kế quan hệ SQLite của bạn đã khá chắc.

---

## Tóm tắt Buổi 15

```text
FOREIGN KEY
    │
    └── đảm bảo "phải trỏ tới parent tồn tại"

FOREIGN KEY + UNIQUE
    │
    └── One-to-One

PRIMARY KEY + FOREIGN KEY
    │
    └── Shared Primary Key
        → pattern rất đẹp cho 1–1
```

Và nhớ:

```text
1–N:
FK nhưng không UNIQUE

1–1:
FK + UNIQUE
hoặc
PK + FK
```

**Buổi 16** tiếp theo sẽ là **One-to-Many** — đây là quan hệ quan trọng nhất đối với app truyện của bạn:

```text
Novel
  │
  ├── Chapter 1
  ├── Chapter 2
  ├── Chapter 3
  └── Chapter N
```

Sau đó chúng ta sẽ đi vào **Many-to-Many → JOIN**, lúc đó việc truy vấn `Novel + Chapter + metadata` sẽ bắt đầu trở nên rất thực chiến.
