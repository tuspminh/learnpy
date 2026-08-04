> bạn là lập trình viên python chuyên nghiệp, dạy tôi từng bước xây dựng model, model-repostory, database manager cho ứng dụng cào truyện và đọc truyện, tôi muốn có một database quản lý chung, và mỗi nguồn truyện một database riêng, dùng sqlite3 thuần sql. dạng framework để có thể test mỗi công đoạn bằng cli


Đây là một dự án rất hay vì nó gần với cách các framework crawler thực tế hoạt động. Nếu thiết kế tốt ngay từ đầu thì sau này bạn chỉ cần thêm plugin là có thể cào được hàng chục website khác nhau.

Tôi sẽ dạy theo hướng **xây dựng framework**, không phải chỉ viết một ứng dụng.

---

# Mục tiêu cuối khóa

Chúng ta sẽ xây dựng được framework có cấu trúc như sau:

```text
StoryFramework/
│
├── app.py                     # CLI chính
├── settings.py
│
├── framework/
│   ├── db/
│   │     database_manager.py
│   │     sqlite.py
│   │
│   ├── model/
│   │     base.py
│   │     source.py
│   │     story.py
│   │     chapter.py
│   │     author.py
│   │
│   ├── repository/
│   │     base_repository.py
│   │     source_repository.py
│   │     story_repository.py
│   │     chapter_repository.py
│   │
│   ├── plugin/
│   │
│   └── cli/
│
├── databases/
│      manager.db
│      truyenfull.db
│      bachngocsach.db
│      tangthuvien.db
│
├── plugins/
│      truyenfull/
│      bachngocsach/
│      tangthuvien/
│
└── tests/
```

Framework này sẽ đủ lớn để sau này:

* GUI PySide6
* API Flask
* Scraper
* Reader
* Mobile

đều dùng chung.

---

# Ý tưởng Database

Khác với nhiều project chỉ có một SQLite.

Chúng ta sẽ có:

```
Manager Database
```

quản lý toàn bộ nguồn.

Ví dụ

```
manager.db
```

chỉ lưu

```
Nguồn truyện

Website A
Website B
Website C

Database nào

truyenfull.db
bachngocsach.db

Plugin nào

plugin_truyenfull
plugin_bns

Có bao nhiêu truyện

Lần crawl cuối

Version
```

Trong khi đó

```
truyenfull.db
```

chỉ chứa

```
Story

Chapter

Author

Category

Tag

Bookmark

History
```

Tương tự

```
bachngocsach.db
```

hoàn toàn độc lập.

Đây là kiểu Database Sharding đơn giản.

---

# Vì sao tách DB?

Ví dụ

```
100 website
```

Nếu dùng một SQLite

```
Story

10 triệu bản ghi

Chapter

300 triệu bản ghi
```

SQLite sẽ rất nặng.

Trong khi tách

```
manager.db

100 KB
```

```
truyenfull.db

1 GB
```

```
bachngocsach.db

600 MB
```

Muốn xóa một nguồn

```
Delete file
```

là xong.

---

# Kiến trúc

```
CLI

↓

Repository

↓

DatabaseManager

↓

SQLite

↓

Database File
```

Không có Repository nào được phép gọi sqlite trực tiếp.

Tất cả phải đi qua

```
DatabaseManager
```

---

# Roadmap

Tôi đề xuất khóa học khoảng **50 buổi**.

## Phần I — Thiết kế tổng thể

### Buổi 1

Kiến trúc framework

### Buổi 2

Thiết kế Database

### Buổi 3

Database Manager

### Buổi 4

SQLite Wrapper

### Buổi 5

Connection Pool (SQLite)

### Buổi 6

Transaction

---

## Phần II — Model

### Buổi 7

BaseModel

### Buổi 8

Story Model

### Buổi 9

Chapter Model

### Buổi 10

Author Model

### Buổi 11

Category

### Buổi 12

Tag

### Buổi 13

Bookmark

### Buổi 14

Reading History

### Buổi 15

Source Model (Manager DB)

---

## Phần III — Repository

### Buổi 16

BaseRepository

### Buổi 17

StoryRepository

### Buổi 18

ChapterRepository

### Buổi 19

AuthorRepository

### Buổi 20

CategoryRepository

### Buổi 21

TagRepository

### Buổi 22

BookmarkRepository

### Buổi 23

HistoryRepository

### Buổi 24

SourceRepository

---

## Phần IV — Database Manager

### Buổi 25

Quản lý nhiều SQLite

### Buổi 26

Tự tạo database mới

### Buổi 27

Auto Migration

### Buổi 28

Version Database

### Buổi 29

Backup

### Buổi 30

Restore

---

## Phần V — CLI Framework

### Buổi 31

Click CLI

### Buổi 32

Command Pattern

### Buổi 33

Database Command

### Buổi 34

Model Command

### Buổi 35

Repository Command

---

## Phần VI — Plugin

### Buổi 36

Plugin Interface

### Buổi 37

Plugin Loader

### Buổi 38

Plugin Metadata

### Buổi 39

Plugin Database

### Buổi 40

Plugin Test CLI

---

## Phần VII — Thực chiến

### Buổi 41

Tạo plugin TruyenFull

### Buổi 42

Crawler đầu tiên

### Buổi 43

Lưu Database

### Buổi 44

Đọc truyện

### Buổi 45

Bookmark

### Buổi 46

Lịch sử đọc

### Buổi 47

Tìm kiếm

### Buổi 48

Export / Import

### Buổi 49

Đóng gói Framework

### Buổi 50

Hoàn thiện dự án

---

# Triết lý thiết kế

Chúng ta sẽ áp dụng các nguyên tắc sau ngay từ đầu:

* **Single Responsibility**: Model chỉ biểu diễn dữ liệu, Repository chỉ truy cập dữ liệu, DatabaseManager chỉ quản lý kết nối.
* **Dependency Inversion**: Repository phụ thuộc vào `DatabaseManager`, không phụ thuộc trực tiếp vào `sqlite3`.
* **Composition over Inheritance**: Ưu tiên ghép các thành phần hơn là tạo cây kế thừa phức tạp.
* **CLI-first**: Mọi chức năng đều phải chạy và kiểm thử được từ dòng lệnh trước khi tích hợp vào GUI hoặc API.
* **Thuần `sqlite3` + SQL**: Không sử dụng ORM như SQLAlchemy để hiểu rõ cách dữ liệu được lưu trữ và tối ưu truy vấn.

## Chiến lược kiểm thử theo từng công đoạn

Mỗi buổi học sẽ kết thúc bằng một lệnh CLI để xác minh phần vừa xây dựng hoạt động đúng. Ví dụ:

```bash
python app.py db init
python app.py db list
python app.py source create truyenfull
python app.py story add
python app.py story list
python app.py chapter count
python app.py plugin test truyenfull
```

Nhờ đó, mỗi lớp (Model, Repository, DatabaseManager, Plugin) đều có thể được kiểm tra độc lập mà không cần giao diện đồ họa.

---

Đây sẽ là một framework có kiến trúc đủ tốt để sau này bạn có thể mở rộng thêm:

* Hỗ trợ nhiều nguồn truyện chỉ bằng cách thêm plugin.
* Thay SQLite bằng PostgreSQL hoặc MariaDB với rất ít thay đổi ở tầng Repository.
* Tích hợp PySide6, Flask/FastAPI hoặc dịch vụ nền mà không phải viết lại tầng dữ liệu.
* Viết test tự động cho từng thành phần một cách dễ dàng.

Tôi khuyên nên đi theo phương pháp **xây dựng từ dưới lên**: **Database → DatabaseManager → Model → Repository → CLI → Plugin → Crawler → Reader**. Cách này giúp mỗi tầng đều ổn định trước khi tầng phía trên sử dụng, giảm đáng kể lỗi và giúp framework dễ bảo trì trong dài hạn.
