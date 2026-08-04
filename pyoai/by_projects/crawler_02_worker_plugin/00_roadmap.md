> bạn là lập trình viên python chuyên nghiệp, dạy tôi từng bước xây dựng crawl-worker và crawler-plugin cho ứng dụng cào truyện và đọc truyện. dạng framework có thể test mỗi công đoạn bằng cli


Chúng ta sẽ xây dựng **một framework crawl truyện chuyên nghiệp**, tách rõ:

```
Crawler Framework
│
├── crawl-worker          (bộ máy chạy job)
│
├── crawler-plugin        (plugin từng nguồn truyện)
│
├── parser-engine         (phân tích HTML)
│
├── repository            (lưu database)
│
├── database-manager      (quản lý SQLite)
│
├── cli                   (test từng công đoạn)
│
└── scheduler             (lập lịch crawl)
```

Mục tiêu cuối:

Ví dụ:

```bash
# liệt kê plugin
$ crawler plugin list

novelbin
truyenfull
tangthuvien


# test lấy thông tin truyện
$ crawler test novelbin book https://xxx.com/truyen-a


# crawl truyện
$ crawler crawl novelbin --book-id 100


# crawl chương
$ crawler crawl novelbin --chapter 1-100


# debug parser
$ crawler debug novelbin chapter url
```

---

# Roadmap xây dựng Crawl Framework

## Giai đoạn 1 — Kiến trúc nền tảng

### Buổi 1. Thiết kế kiến trúc Crawl Framework

### Buổi 2. Tạo project structure

### Buổi 3. Xây dựng Core Model

### Buổi 4. Thiết kế Plugin Interface

### Buổi 5. Plugin Loader

### Buổi 6. Crawl Context

### Buổi 7. Request Client

### Buổi 8. Parser Engine

---

# Giai đoạn 2 — Crawler Plugin

### Buổi 9. Thiết kế Novel Plugin

### Buổi 10. Book Parser

### Buổi 11. Chapter Parser

### Buổi 12. Content Parser

### Buổi 13. Image Parser

### Buổi 14. Metadata Parser

### Buổi 15. Plugin Versioning

---

# Giai đoạn 3 — Crawl Worker

### Buổi 16. Worker Architecture

### Buổi 17. Job Queue

### Buổi 18. Crawl Task

### Buổi 19. Retry Mechanism

### Buổi 20. Error Handling

### Buổi 21. Logging

### Buổi 22. Progress Tracking

---

# Giai đoạn 4 — Database Layer

### Buổi 23. Database Manager

### Buổi 24. Repository Pattern

### Buổi 25. SQLite Schema

### Buổi 26. Migration

### Buổi 27. Transaction

### Buổi 28. Cache

---

# Giai đoạn 5 — CLI Framework

### Buổi 29. Click CLI

### Buổi 30. Command Architecture

### Buổi 31. Debug Command

### Buổi 32. Test Command

### Buổi 33. Crawl Command

---

# Giai đoạn 6 — Production

### Buổi 34. Async Worker

### Buổi 35. Multi Source Crawl

### Buổi 36. Plugin Marketplace

### Buổi 37. Monitoring

### Buổi 38. Deployment

---

# Bắt đầu Buổi 1

# Thiết kế kiến trúc Crawl Framework

## 1. Tư duy thiết kế

Một ứng dụng cào truyện không nên viết:

```
main.py

requests.get()
parse()
insert()
```

vì sau này:

* thêm nguồn mới khó
* sửa parser ảnh hưởng toàn bộ
* không test riêng được
* khó debug

Chúng ta thiết kế kiểu:

```
SOURCE WEBSITE

      |
      |
      v

Crawler Plugin

      |
      |
      v

Crawler Engine

      |
      |
      v

Repository

      |
      |
      v

SQLite
```

---

# 2. Vai trò từng thành phần

## Crawl Worker

Là thằng chạy nhiệm vụ.

Ví dụ:

```
Worker nhận:

Task:
crawl book id=100


Worker:

1. gọi plugin
2. lấy dữ liệu
3. validate
4. lưu database
5. ghi log
```

Nó không biết:

* truyenfull là gì
* novelbin là gì

Nó chỉ biết interface.

---

# 3. Crawler Plugin

Mỗi website là một plugin.

Ví dụ:

```
plugins/

├── novelbin/
│
│   ├── plugin.py
│   ├── parser.py
│   └── config.py
│


├── truyenfull/
│
│   ├── plugin.py
│   ├── parser.py
│
```

Plugin chịu trách nhiệm:

```
URL
 |
 |
 HTML
 |
 |
 Parser
 |
 |
 Model
```

---

# 4. Core Model

Không lưu HTML.

Chúng ta tạo model:

```
Book

id
title
author
description
cover


Chapter

id
book_id
title
content
order


Image

id
chapter_id
url

```

Ví dụ:

```python
from dataclasses import dataclass


@dataclass
class Book:

    title:str
    author:str
    description:str
    cover:str
```

---

# 5. Plugin Interface

Đây là phần quan trọng.

Tất cả plugin phải tuân theo:

```python
from abc import ABC, abstractmethod


class CrawlerPlugin(ABC):


    @abstractmethod
    def get_book(self,url):
        pass


    @abstractmethod
    def get_chapters(self,url):
        pass


    @abstractmethod
    def get_content(self,url):
        pass

```

Sau này:

```python
NovelBinPlugin

TruyenFullPlugin

TangThuVienPlugin

```

đều implement.

---

# 6. Worker dùng plugin như thế nào?

Ví dụ:

```python
class CrawlWorker:


    def __init__(
        self,
        plugin
    ):
        self.plugin = plugin



    def crawl_book(
        self,
        url
    ):

        book = self.plugin.get_book(url)

        chapters = self.plugin.get_chapters(url)


        return book, chapters
```

Worker không quan tâm:

```
if novelbin:

    xpath 1


if truyenfull:

    xpath 2
```

Đó là nhiệm vụ plugin.

---

# 7. CLI Test từng tầng

Chúng ta sẽ tạo:

```
cli/


├── main.py


commands/


├── plugin.py

├── crawl.py

├── debug.py

├── database.py

```

Ví dụ:

## Test plugin

```bash
crawler plugin list
```

Output:

```
Available plugins:

[1] novelbin
[2] truyenfull
```

---

## Test parser

```bash
crawler debug parse novelbin book URL
```

Output:

```
Title:
Author:
Cover:
```

---

## Test database

```bash
crawler database check
```

Output:

```
Book table OK
Chapter table OK
```

---

# 8. Cấu trúc project đầu tiên

Tạo:

```
novel_crawler/


├── app/


│
├── core/
│   ├── models/
│   ├── plugin/
│   ├── worker/
│
│
├── plugins/
│   └── novelbin/
│
│
├── database/
│
│
├── cli/
│
│
├── tests/
│
│
└── main.py

```

---

# 9. Nguyên tắc thiết kế

Framework này sẽ tuân thủ:

## Single Responsibility

Plugin:

```
parse website
```

Worker:

```
execute job
```

Repository:

```
save data
```

CLI:

```
control system
```

---

## Dependency Injection

Không:

```python
worker = CrawlWorker()
worker.connect_sqlite()
```

Mà:

```python
worker = CrawlWorker(
    plugin,
    repository
)
```

---

## Test được từng phần

Ví dụ:

Test parser:

```bash
crawler debug parser novelbin
```

không cần database.

Test database:

```bash
crawler database test
```

không cần internet.

---

# Bài tập Buổi 1

Thiết kế cây thư mục:

```
novel_crawler/
```

và tạo:

```
core/
    models/
    plugin/
    worker/


plugins/


database/


cli/


tests/
```

---

Buổi tiếp theo:

# Buổi 2 — Xây dựng Project Structure + Package Architecture

Chúng ta sẽ viết:

* `pyproject.toml`
* package layout chuẩn Python
* import system
* tạo CLI command đầu tiên
* chạy:

```bash
python -m crawler --help
```

để framework bắt đầu hoạt động.


