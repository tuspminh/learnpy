# Buổi 1 — SQL, SQLite và Python `sqlite3`

Hôm nay chúng ta xây **nền móng**. Chưa vội Repository hay Unit of Work. Mục tiêu là bạn phải hiểu rõ chuyện gì xảy ra từ lúc Python mở database cho tới lúc dữ liệu được lưu.

---

# 1. Database là gì?

Hãy tưởng tượng app đọc truyện của bạn có hàng nghìn truyện.

Ta cần lưu:

```text
Novel
────────────────────────
id
title
author
url
status
```

Ví dụ:

```text
1 | Đấu Phá Thương Khung | Thiên Tằm Thổ Đậu | ... | completed
2 | Phàm Nhân Tu Tiên     | Vong Ngữ          | ... | ongoing
```

Đây là **database**.

Database có thể chứa nhiều **table**.

```text
novel.db
│
├── novels
├── chapters
├── authors
└── crawl_tasks
```

Mỗi table chứa nhiều **row**.

Ví dụ:

```text
novels

id | title                  | author
---+------------------------+----------------
1  | Đấu Phá Thương Khung   | Thiên Tằm Thổ Đậu
2  | Phàm Nhân Tu Tiên      | Vong Ngữ
```

---

# 2. SQL là gì?

SQL là ngôn ngữ dùng để nói chuyện với database.

Ví dụ:

```sql
SELECT * FROM novels;
```

Nghĩa là:

> Lấy tất cả dữ liệu từ bảng `novels`.

Hoặc:

```sql
SELECT title
FROM novels
WHERE id = 1;
```

Nghĩa là:

> Lấy `title` của novel có `id = 1`.

SQL **không phải SQLite**.

Đây là điểm cần nhớ:

```text
SQL
│
└── Ngôn ngữ

SQLite
│
└── Database engine

Python sqlite3
│
└── Module giúp Python giao tiếp với SQLite
```

---

# 3. SQLite là gì?

SQLite là một database engine rất đặc biệt.

Thông thường ta có:

```text
Python
   │
   ▼
Database Server
   │
   ▼
PostgreSQL / MySQL
```

Ví dụ PostgreSQL thường có một server/database process riêng.

SQLite thì đơn giản hơn:

```text
Python
   │
   ▼
SQLite engine
   │
   ▼
novel.db
```

Database có thể chỉ đơn giản là **một file**:

```text
novel.db
```

Đây là lý do SQLite cực kỳ phù hợp với:

* desktop app
* CLI app
* tool cá nhân
* crawler
* ứng dụng đọc truyện
* prototype
* local cache
* testing

Đặc biệt với project Python + PySide6 + crawler của bạn, SQLite là lựa chọn rất hợp lý.

---

# 4. Python có sẵn `sqlite3`

Bạn **không cần cài package**.

Python đã có:

```python
import sqlite3
```

Kiểm tra:

```python
import sqlite3

print(sqlite3.sqlite_version)
```

Ví dụ:

```text
3.46.1
```

Phiên bản có thể khác trên máy bạn.

---

# 5. Connection là gì?

Đầu tiên:

```python
import sqlite3

conn = sqlite3.connect("novel.db")
```

Ta vừa tạo một **database connection**.

Hãy hình dung:

```text
Python
   │
   │ connection
   ▼
SQLite
   │
   ▼
novel.db
```

`conn` chính là đối tượng đại diện cho kết nối tới database.

```python
conn = sqlite3.connect("novel.db")
```

Nếu file:

```text
novel.db
```

chưa tồn tại, SQLite có thể tạo nó.

Sau đoạn code:

```python
import sqlite3

conn = sqlite3.connect("novel.db")
```

ta có:

```text
project/
│
├── main.py
└── novel.db
```

---

# 6. `:memory:`

SQLite còn có một database đặc biệt:

```python
conn = sqlite3.connect(":memory:")
```

Database này nằm trong memory.

```text
RAM
│
└── SQLite database
```

Khi connection đóng:

```python
conn.close()
```

database biến mất.

Điều này cực kỳ hữu ích cho testing sau này:

```python
def test_create_novel():
    conn = sqlite3.connect(":memory:")
```

Ta sẽ học kỹ vấn đề này ở phần Testing.

---

# 7. Cursor là gì?

Sau khi có connection:

```python
conn = sqlite3.connect("novel.db")
```

ta tạo cursor:

```python
cursor = conn.cursor()
```

Có thể hình dung:

```text
Connection
    │
    ▼
 Cursor
    │
    ▼
 execute SQL
```

Cursor là đối tượng giúp chúng ta thực thi SQL và lấy kết quả.

Ví dụ:

```python
cursor.execute("SELECT * FROM novels")
```

---

# 8. `execute()`

Đây là một trong những method quan trọng nhất:

```python
cursor.execute(...)
```

Ví dụ:

```python
cursor.execute("""
    CREATE TABLE novels (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL
    )
""")
```

SQL bên trong là:

```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);
```

Kết quả:

```text
database
│
└── novels
     ├── id
     └── title
```

---

# 9. Chương trình hoàn chỉnh đầu tiên

Tạo file:

```text
main.py
```

Nội dung:

```python
import sqlite3


conn = sqlite3.connect("novel.db")

cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE novels (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL
    )
""")

conn.commit()

conn.close()
```

Chạy:

```bash
python main.py
```

Sau đó:

```text
novel.db
```

được tạo.

---

# 10. `commit()` cực kỳ quan trọng

Đây là một khái niệm bạn cần hiểu thật kỹ.

Khi thực hiện:

```sql
INSERT
UPDATE
DELETE
```

thì thay đổi cần được **commit** để transaction được xác nhận.

Ví dụ:

```python
cursor.execute("""
    INSERT INTO novels (title)
    VALUES ('Đấu Phá Thương Khung')
""")

conn.commit()
```

Luồng:

```text
execute()
   │
   ▼
transaction
   │
   ▼
commit()
   │
   ▼
database
```

Nếu không commit, thay đổi có thể không được lưu như bạn mong muốn khi connection kết thúc.

---

# 11. `rollback()`

Ngược lại:

```python
conn.rollback()
```

có nghĩa:

> Hủy các thay đổi chưa commit trong transaction hiện tại.

Ví dụ:

```python
try:
    cursor.execute("""
        INSERT INTO novels (title)
        VALUES ('Novel A')
    """)

    cursor.execute("""
        INSERT INTO novels (title)
        VALUES ('Novel B')
    """)

    conn.commit()

except Exception:
    conn.rollback()
```

Luồng:

```text
                ┌── success ──→ COMMIT
transaction ────┤
                └── error ────→ ROLLBACK
```

Đây chính là nền móng của **Unit of Work** mà chúng ta sẽ học sau.

---

# 12. `close()`

Khi hoàn thành:

```python
conn.close()
```

đóng connection.

Một chương trình cơ bản:

```python
import sqlite3

conn = sqlite3.connect("novel.db")

cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE novels (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL
    )
""")

conn.commit()

conn.close()
```

Có 5 bước quan trọng:

```text
1. connect
      ↓
2. cursor
      ↓
3. execute
      ↓
4. commit
      ↓
5. close
```

Hãy ghi nhớ chuỗi này.

---

# 13. INSERT dữ liệu

Sau khi table tồn tại:

```python
cursor.execute("""
    INSERT INTO novels (title)
    VALUES ('Đấu Phá Thương Khung')
""")

conn.commit()
```

Thêm record thứ hai:

```python
cursor.execute("""
    INSERT INTO novels (title)
    VALUES ('Phàm Nhân Tu Tiên')
""")

conn.commit()
```

Database:

```text
novels

id | title
---+----------------------
1  | Đấu Phá Thương Khung
2  | Phàm Nhân Tu Tiên
```

---

# 14. SELECT dữ liệu

Bây giờ:

```python
cursor.execute("""
    SELECT *
    FROM novels
""")
```

Nhưng `execute()` chưa đưa kết quả ra màn hình.

Ta cần:

```python
rows = cursor.fetchall()
```

Sau đó:

```python
print(rows)
```

Ví dụ:

```text
[(1, 'Đấu Phá Thương Khung'),
 (2, 'Phàm Nhân Tu Tiên')]
```

---

# 15. `fetchone()`

Nếu chỉ muốn một row:

```python
cursor.execute("""
    SELECT *
    FROM novels
    WHERE id = 1
""")

row = cursor.fetchone()

print(row)
```

Kết quả:

```text
(1, 'Đấu Phá Thương Khung')
```

So sánh:

```text
fetchone()
    ↓
một row

fetchall()
    ↓
tất cả row
```

Sau này còn:

```python
cursor.fetchmany()
```

---

# 16. Một ví dụ hoàn chỉnh

```python
import sqlite3


conn = sqlite3.connect("novel.db")

cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS novels (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL
    )
""")

cursor.execute("""
    INSERT INTO novels (title)
    VALUES ('Đấu Phá Thương Khung')
""")

conn.commit()

cursor.execute("""
    SELECT *
    FROM novels
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
```

Ở đây có một điểm mới:

```sql
CREATE TABLE IF NOT EXISTS
```

Nó có nghĩa:

> Nếu table chưa tồn tại thì tạo; nếu đã tồn tại thì không báo lỗi.

Điều này rất hữu ích khi chạy chương trình nhiều lần.

---

# 17. Nhưng code trên có một lỗi thiết kế

Nếu chạy:

```bash
python main.py
```

10 lần, bạn sẽ có:

```text
Đấu Phá Thương Khung
Đấu Phá Thương Khung
Đấu Phá Thương Khung
Đấu Phá Thương Khung
...
```

Vì mỗi lần chạy đều:

```sql
INSERT
```

Đây là vấn đề mà sau này chúng ta sẽ giải quyết bằng:

* constraint
* UNIQUE
* UPSERT
* repository
* transaction

---

# 18. Một nguyên tắc cực kỳ quan trọng

**Không xây SQL bằng string interpolation.**

Không làm:

```python
title = "Đấu Phá Thương Khung"

cursor.execute(
    f"INSERT INTO novels (title) VALUES ('{title}')"
)
```

Đây là cách không an toàn.

Thay vào đó:

```python
cursor.execute(
    """
    INSERT INTO novels (title)
    VALUES (?)
    """,
    (title,)
)
```

Đây gọi là **parameterized query**.

Chúng ta sẽ dành riêng một buổi để học rất sâu vấn đề này.

---

# 19. Connection và Cursor khác nhau thế nào?

Đây là câu hỏi rất hay.

### Connection

Đại diện cho kết nối/database session:

```python
conn
```

Nó quản lý:

* transaction
* commit
* rollback
* connection state

### Cursor

Dùng để thực thi SQL và lấy kết quả:

```python
cursor
```

Ví dụ:

```python
cursor.execute(...)
cursor.fetchone()
cursor.fetchall()
```

Có thể hình dung:

```text
Connection
│
├── transaction
├── commit()
├── rollback()
└── cursor()
        │
        ▼
      Cursor
        │
        ├── execute()
        ├── fetchone()
        └── fetchall()
```

---

# 20. Mô hình tư duy quan trọng nhất của Buổi 1

Đừng chỉ nhớ code.

Hãy nhớ kiến trúc:

```text
Python
   │
   ▼
sqlite3
   │
   ▼
Connection
   │
   ▼
Cursor
   │
   ▼
SQL
   │
   ▼
SQLite Engine
   │
   ▼
novel.db
```

Với thao tác ghi:

```text
execute()
   │
   ▼
Transaction
   │
   ├── commit()
   │       ↓
   │     SAVE
   │
   └── rollback()
           ↓
         UNDO
```

Đây là nền tảng để sau này chúng ta xây:

```text
Application
     │
     ▼
Unit of Work
     │
     ▼
Repository
     │
     ▼
Connection
     │
     ▼
SQLite
```

---

# Bài tập Buổi 1

Hãy tự viết một chương trình `novel_db.py`.

### Yêu cầu

Tạo database:

```text
novel.db
```

Tạo table:

```text
novels
```

với:

```text
id
title
author
```

Trong đó:

```text
id     → INTEGER PRIMARY KEY
title  → TEXT
author → TEXT
```

Sau đó thêm 3 truyện:

```text
Đấu Phá Thương Khung
Phàm Nhân Tu Tiên
Tiên Nghịch
```

Mỗi truyện có author tương ứng.

Cuối cùng:

```python
SELECT * FROM novels
```

và in:

```text
1 | Đấu Phá Thương Khung | ...
2 | Phàm Nhân Tu Tiên     | ...
3 | Tiên Nghịch           | ...
```

### Thử thách thêm

Không viết:

```python
f"INSERT INTO ..."
```

Mà phải sử dụng:

```python
?
```

parameterized query.

---

## Checklist sau Buổi 1

Bạn cần tự giải thích được:

* [ ] SQL là gì?
* [ ] SQLite là gì?
* [ ] `sqlite3` là gì?
* [ ] Database file là gì?
* [ ] `Connection` là gì?
* [ ] `Cursor` là gì?
* [ ] `execute()` làm gì?
* [ ] `commit()` làm gì?
* [ ] `rollback()` làm gì?
* [ ] `close()` làm gì?
* [ ] `fetchone()` khác `fetchall()` thế nào?
* [ ] Vì sao không nối chuỗi SQL bằng f-string?
* [ ] `:memory:` dùng để làm gì?

**Buổi 2** chúng ta sẽ đi sâu vào **`CREATE TABLE` + kiểu dữ liệu SQLite + `PRIMARY KEY` + `NOT NULL` + `UNIQUE` + `DEFAULT` + `CHECK`**, và bắt đầu thiết kế schema cho `novels`/`chapters` thay vì chỉ dùng ví dụ đơn giản.
