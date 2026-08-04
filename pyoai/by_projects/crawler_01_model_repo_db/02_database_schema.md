# Buổi 2 — Thiết kế Database Schema

## Mục tiêu

Sau buổi này bạn sẽ:

* Biết cách thiết kế database trước khi viết code
* Thiết kế được `manager.db`
* Thiết kế được database cho từng nguồn truyện
* Hiểu Primary Key, Foreign Key, Index
* Biết bảng nào dùng chung, bảng nào riêng
* Sẵn sàng sang buổi 3 viết `DatabaseManager`

> Một sai lầm phổ biến là mở SQLite lên rồi tạo bảng ngay. Trong các dự án lớn, **schema được thiết kế trước, code được viết sau**.

---

# 1. Kiến trúc Database

Framework sẽ sử dụng hai loại database:

```text
                 DatabaseManager
                       │
        ┌──────────────┴──────────────┐
        │                             │
    manager.db                 source_xxx.db
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
              truyenfull.db   bachngocsach.db  wikidich.db
```

Trong đó:

* `manager.db` → quản lý framework
* `source.db` → lưu truyện của từng website

---

# 2. manager.db

Chỉ có nhiệm vụ quản lý.

Không lưu:

* truyện
* chương
* nội dung

Chỉ lưu:

* nguồn
* plugin
* database
* version
* trạng thái

---

## Các bảng

```text
manager.db

source
setting
migration
```

Sau này có thể thêm

```text
log
task
plugin
```

---

# 3. Bảng source

Đây là bảng quan trọng nhất.

```sql
CREATE TABLE source (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL UNIQUE,

    display_name TEXT NOT NULL,

    plugin TEXT NOT NULL,

    database_name TEXT NOT NULL,

    version TEXT,

    enabled INTEGER NOT NULL DEFAULT 1,

    last_crawl TEXT,

    created_at TEXT,

    updated_at TEXT
);
```

Ví dụ dữ liệu

| id | name       | plugin            | database      |
| -- | ---------- | ----------------- | ------------- |
| 1  | truyenfull | plugin_truyenfull | truyenfull.db |
| 2  | wikidich   | plugin_wikidich   | wikidich.db   |

---

# 4. setting

Framework cần lưu cấu hình.

Ví dụ

```text
theme

language

download_path

reader_font

reader_size
```

Schema

```sql
CREATE TABLE setting (

    key TEXT PRIMARY KEY,

    value TEXT

);
```

Ví dụ

| key       | value |
| --------- | ----- |
| theme     | dark  |
| font_size | 18    |
| language  | vi    |

---

# 5. migration

Để sau này tự nâng cấp database.

```sql
CREATE TABLE migration (

    version TEXT PRIMARY KEY,

    applied_at TEXT

);
```

Ví dụ

| version |
| ------- |
| 1.0.0   |
| 1.1.0   |

---

# 6. Database của từng nguồn

Ví dụ

```text
truyenfull.db
```

Sẽ gồm

```text
story

chapter

author

category

tag

story_category

story_tag

bookmark

history
```

---

# 7. Story

Đây là bảng trung tâm.

```sql
CREATE TABLE story (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    source_id TEXT,

    title TEXT NOT NULL,

    slug TEXT,

    author_id INTEGER,

    cover TEXT,

    description TEXT,

    status TEXT,

    total_chapters INTEGER DEFAULT 0,

    last_chapter TEXT,

    created_at TEXT,

    updated_at TEXT
);
```

Lưu ý:

`source_id`

là ID của website

Ví dụ

```text
https://truyenfull...

story/12345
```

thì

```text
source_id = 12345
```

Không phải khóa ngoại tới `manager.db`, vì hai cơ sở dữ liệu tách biệt.

---

# 8. Author

```sql
CREATE TABLE author (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    slug TEXT

);
```

---

# 9. Chapter

```sql
CREATE TABLE chapter (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    story_id INTEGER NOT NULL,

    source_id TEXT,

    chapter_no REAL,

    title TEXT,

    url TEXT,

    content TEXT,

    created_at TEXT
);
```

Quan hệ

```text
Story

1

↓

∞

Chapter
```

---

# 10. Category

```sql
CREATE TABLE category (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT,

    slug TEXT
);
```

---

# 11. Tag

```sql
CREATE TABLE tag (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT,

    slug TEXT
);
```

---

# 12. Quan hệ N-N

Một truyện có nhiều thể loại.

Một thể loại có nhiều truyện.

Không thể lưu trực tiếp.

Ta dùng bảng trung gian.

## story_category

```sql
CREATE TABLE story_category (

    story_id INTEGER,

    category_id INTEGER,

    PRIMARY KEY(

        story_id,

        category_id

    )

);
```

---

## story_tag

```sql
CREATE TABLE story_tag (

    story_id INTEGER,

    tag_id INTEGER,

    PRIMARY KEY(

        story_id,

        tag_id

    )

);
```

---

# 13. Bookmark

```sql
CREATE TABLE bookmark (

    story_id INTEGER PRIMARY KEY,

    created_at TEXT
);
```

---

# 14. Reading History

```sql
CREATE TABLE history (

    story_id INTEGER PRIMARY KEY,

    chapter_id INTEGER,

    last_read TEXT
);
```

---

# 15. Quan hệ tổng thể

```text
Author
   │
   │1
   │
   │∞
 Story
   │
   │1
   │
   │∞
Chapter

Story
   │∞
   │
   │∞
Category

Story
   │∞
   │
   │∞
Tag
```

---

# 16. Index

SQLite rất cần Index.

Ví dụ

Tìm theo tên truyện.

```sql
CREATE INDEX idx_story_title

ON story(title);
```

---

Tìm theo slug

```sql
CREATE INDEX idx_story_slug

ON story(slug);
```

---

Chapter

```sql
CREATE INDEX idx_chapter_story

ON chapter(story_id);
```

---

Bookmark

```sql
CREATE INDEX idx_bookmark

ON bookmark(created_at);
```

---

# 17. Những cột nên UNIQUE

```text
story.source_id

story.slug

chapter(source_id, story_id)

category.slug

tag.slug
```

---

# 18. Những cột nên INDEX

```text
story.title

story.slug

story.author_id

chapter.story_id

chapter.chapter_no

history.last_read

bookmark.created_at
```

---

# 19. Sơ đồ hoàn chỉnh

```text
manager.db

├── source
├── setting
└── migration



truyenfull.db

├── author
├── story
├── chapter
├── category
├── tag
├── story_category
├── story_tag
├── bookmark
└── history
```

---

# 20. Một số cải tiến để framework dễ mở rộng

Trước khi sang phần lập trình, tôi đề xuất bổ sung một vài bảng và cột để tránh phải sửa schema sau này.

## Thêm bảng `crawl_job`

Quản lý các lần cào dữ liệu:

```sql
CREATE TABLE crawl_job (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    message TEXT
);
```

Mỗi lần chạy crawler sẽ có một bản ghi, rất hữu ích khi debug.

### Thêm bảng `crawl_state`

Lưu trạng thái để hỗ trợ cào tiếp (resume):

```sql
CREATE TABLE crawl_state (
    key TEXT PRIMARY KEY,
    value TEXT
);
```

Ví dụ:

| key             | value |
| --------------- | ----- |
| last_story_page | 152   |
| last_story_id   | 87342 |

### Chuẩn hóa thời gian

Tất cả các cột thời gian (`created_at`, `updated_at`, `last_read`, `started_at`...) nên lưu theo chuẩn **UTC ISO 8601**, ví dụ:

```text
2026-08-03T10:15:42Z
```

Điều này giúp đồng bộ múi giờ và dễ chuyển sang các hệ quản trị cơ sở dữ liệu khác.

### Quy ước đặt tên

* Tên bảng: số ít (`story`, `chapter`, `author`)
* Tên cột: `snake_case`
* Khóa chính: `id`
* Khóa ngoại: `<table>_id` (ví dụ: `story_id`, `author_id`)
* Khóa định danh từ website: `source_id`

---

# Bài tập thực hành

## Bài 1

Vẽ lại sơ đồ ERD (Entity Relationship Diagram) của toàn bộ hệ thống bằng tay hoặc bằng một công cụ như draw.io.

## Bài 2

Viết toàn bộ các câu lệnh `CREATE TABLE` và `CREATE INDEX` vào một file:

```text
sql/schema.sql
```

Chưa cần chạy trên SQLite.

## Bài 3

Kiểm tra từng bảng theo các câu hỏi:

* Bảng này thuộc `manager.db` hay `source.db`?
* Có khóa chính không?
* Có cần chỉ mục (index) không?
* Có quan hệ với bảng nào?

---

# Kết quả sau buổi 2

Bạn đã có một thiết kế cơ sở dữ liệu đủ tốt để hỗ trợ:

* Quản lý nhiều nguồn truyện bằng các file SQLite độc lập.
* Mở rộng thêm plugin mà không phải thay đổi cấu trúc dữ liệu hiện có.
* Hỗ trợ đọc truyện, đánh dấu, lịch sử đọc và đồng bộ trạng thái cào.
* Chuẩn bị nền tảng để xây dựng **DatabaseManager**.

Ở **Buổi 3**, chúng ta sẽ bắt đầu lập trình thành phần đầu tiên của framework: **DatabaseManager**, chịu trách nhiệm quản lý nhiều file SQLite, mở/đóng kết nối, khởi tạo database mới và cung cấp giao diện thống nhất cho toàn bộ Repository.
