# Buổi 1 — Thiết kế kiến trúc Framework

## Mục tiêu

Sau buổi này bạn sẽ hiểu:

* Vì sao phải xây dựng theo dạng framework
* Kiến trúc tổng thể của ứng dụng
* Luồng dữ liệu từ CLI đến Database
* Vai trò của Model, Repository, DatabaseManager
* Tại sao chia nhiều SQLite
* Chuẩn bị cấu trúc project để bắt đầu lập trình

> **Hôm nay chưa viết nhiều code**, mục tiêu là thiết kế đúng. Một framework tốt thường dành nhiều thời gian cho thiết kế hơn là viết code.

---

# 1. Bài toán

Giả sử bạn muốn cào truyện từ:

```
TruyenFull
↓

BachNgocSach
↓

TangThuVien
↓

Metruyen
↓

WikiDich
↓

...
```

Mỗi website có:

* HTML khác nhau
* URL khác nhau
* Pagination khác nhau
* Encoding khác nhau
* Cấu trúc chương khác nhau

Nhưng khi lưu vào máy, dữ liệu đều giống nhau.

Ví dụ:

```
Story

id
title
author
cover
description

Chapter

id
story_id
title
content
order
```

=> Phần **Crawler khác nhau**, nhưng **Database giống nhau**.

Đó là lý do phải tách hai phần.

```
Crawler
↓

Repository
↓

Database
```

---

# 2. Kiến trúc tổng thể

```
                  CLI
                   │
        ┌──────────┴──────────┐
        │                     │
     Command             Plugin Test
        │                     │
        └──────────┬──────────┘
                   │
             Repository Layer
                   │
      ┌────────────┴─────────────┐
      │                          │
 StoryRepository          ChapterRepository
      │                          │
      └────────────┬─────────────┘
                   │
            DatabaseManager
                   │
        ┌──────────┴──────────┐
        │                     │
     manager.db          truyenfull.db
```

---

# 3. Vì sao phải có Repository?

Nhiều người mới học sẽ viết như sau:

```python
import sqlite3

conn = sqlite3.connect("story.db")

conn.execute(
    """
INSERT INTO story(title)
VALUES(?)
""",
    ("One Piece",),
)
```

Ban đầu rất đơn giản.

Nhưng sau này:

```
GUI

Crawler

REST API

CLI

Reader
```

đều phải viết SQL.

Kết quả:

```
GUI

SQL

Crawler

SQL

API

SQL

CLI

SQL
```

SQL xuất hiện khắp nơi.

Đây là thiết kế rất khó bảo trì.

---

## Repository giải quyết vấn đề

Thay vì:

```
GUI

↓

SQL
```

ta sẽ:

```
GUI

↓

StoryRepository

↓

SQLite
```

Ví dụ:

```python
story_repo.add(story)

story_repo.update(story)

story_repo.delete(id)

story_repo.find(id)

story_repo.search(keyword)
```

Không có nơi nào khác biết SQL.

---

# 4. Model là gì?

Model chỉ biểu diễn dữ liệu.

Ví dụ:

```
Story

id

title

author

cover

status

description
```

Model **không** biết SQL.

Model **không** biết sqlite.

Model **không** biết CLI.

Model chỉ là dữ liệu.

Ví dụ:

```python
Story(title="Đấu Phá Thương Khung", author="Thiên Tằm Thổ Đậu")
```

Đó là toàn bộ nhiệm vụ của Model.

---

# 5. DatabaseManager

Nếu project chỉ có:

```
story.db
```

thì không cần.

Nhưng chúng ta có:

```
manager.db

truyenfull.db

bachngocsach.db

metruyen.db

wikidich.db
```

Ai sẽ mở đúng database?

Không thể để Repository tự mở.

Ta cần:

```
DatabaseManager
```

Ví dụ:

```
StoryRepository

↓

DatabaseManager

↓

truyenfull.db
```

hoặc

```
SourceRepository

↓

DatabaseManager

↓

manager.db
```

Repository không cần biết file nằm ở đâu.

---

# 6. Vì sao chia nhiều SQLite?

Giả sử:

```
100 website
```

Mỗi website

```
100.000 truyện

500 chương/truyện
```

=> Khoảng:

```
50.000.000 chapter
```

Nếu tất cả nằm trong:

```
story.db
```

SQLite sẽ rất lớn.

Nếu chia:

```
manager.db

50 KB
```

```
truyenfull.db

800 MB
```

```
bachngocsach.db

500 MB
```

```
wikidich.db

2 GB
```

Mỗi database độc lập.

Muốn xóa một nguồn:

```
Delete file
```

là xong.

---

# 7. Manager Database chứa gì?

**Không lưu truyện.**

Chỉ lưu thông tin quản lý.

Ví dụ:

```
Source

id

name

plugin

database

enabled

last_crawl

version
```

Ví dụ dữ liệu:

| id | name       | plugin            | database      |
| -- | ---------- | ----------------- | ------------- |
| 1  | truyenfull | plugin_truyenfull | truyenfull.db |
| 2  | wikidich   | plugin_wikidich   | wikidich.db   |

---

# 8. Database của từng nguồn

Ví dụ:

```
truyenfull.db
```

```
Story

Chapter

Author

Category

Tag

Bookmark

History
```

Không chứa:

```
Plugin

Source

Version
```

Những thứ đó thuộc:

```
manager.db
```

---

# 9. Luồng dữ liệu

Ví dụ CLI:

```
python app.py story add
```

Luồng xử lý:

```
CLI

↓

StoryCommand

↓

StoryRepository

↓

DatabaseManager

↓

SQLite

↓

Story Table
```

Không có tầng nào được bỏ qua.

Sai:

```
CLI

↓

SQLite
```

Sai:

```
GUI

↓

SQLite
```

Sai:

```
Crawler

↓

SQLite
```

Mọi truy cập dữ liệu đều phải đi qua Repository.

---

# 10. Cấu trúc project

Hôm nay chúng ta chỉ tạo cấu trúc thư mục.

```
story_framework/
│
├── app.py
├── settings.py
│
├── framework/
│   ├── __init__.py
│   │
│   ├── cli/
│   │   └── __init__.py
│   │
│   ├── db/
│   │   └── __init__.py
│   │
│   ├── model/
│   │   └── __init__.py
│   │
│   ├── repository/
│   │   └── __init__.py
│   │
│   └── plugin/
│       └── __init__.py
│
├── databases/
│
├── plugins/
│
├── tests/
│
└── README.md
```

Đến cuối buổi, bạn chỉ cần tạo đúng cấu trúc này.

---

# 11. Tư duy Framework

Mỗi tầng chỉ có **một trách nhiệm**:

| Thành phần      | Trách nhiệm                          | Không làm gì                     |
| --------------- | ------------------------------------ | -------------------------------- |
| Model           | Biểu diễn dữ liệu                    | Không truy cập DB                |
| Repository      | CRUD và truy vấn dữ liệu             | Không biết CLI, không parse HTML |
| DatabaseManager | Quản lý kết nối và nhiều file SQLite | Không chứa logic nghiệp vụ       |
| Plugin          | Cào dữ liệu từ từng website          | Không ghi SQL trực tiếp          |
| CLI             | Nhận lệnh và điều phối               | Không truy cập DB trực tiếp      |

---

# Bài tập thực hành

## Bài 1

Tạo đầy đủ cấu trúc thư mục như trên.

---

## Bài 2

Tạo các file rỗng:

```
app.py

settings.py

README.md
```

---

## Bài 3

Trong `README.md`, mô tả ngắn kiến trúc:

```
CLI
    ↓
Repository
    ↓
DatabaseManager
    ↓
SQLite
```

và giải thích vai trò của từng tầng bằng lời của chính bạn.

---

# Kết quả đạt được sau buổi 1

Bạn sẽ nắm được:

* Tư duy thiết kế framework theo nhiều tầng (layered architecture).
* Lý do sử dụng **Repository Pattern** để cô lập SQL.
* Vai trò riêng biệt của **Model**, **Repository** và **DatabaseManager**.
* Chiến lược **một cơ sở dữ liệu quản lý (`manager.db`) + một cơ sở dữ liệu cho mỗi nguồn truyện**.
* Cấu trúc thư mục nền tảng cho toàn bộ dự án.

Ở **Buổi 2**, chúng ta sẽ bắt đầu thiết kế **Database Schema** một cách bài bản: xác định các bảng, khóa chính/khóa ngoại, chỉ mục (index), quan hệ giữa các bảng và quy ước đặt tên để có một nền tảng dữ liệu dễ mở rộng và tối ưu cho việc cào cũng như đọc truyện.
