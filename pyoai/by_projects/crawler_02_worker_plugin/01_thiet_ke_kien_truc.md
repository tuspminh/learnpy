
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
