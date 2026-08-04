# Buổi 40. Mini Project tổng hợp Python Intermediate

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Áp dụng toàn bộ kiến thức Python Intermediate vào một dự án thực tế.
> * Biết cách tổ chức cấu trúc project chuyên nghiệp.
> * Kết hợp:
>
>   * Module
>   * Package
>   * Virtual Environment
>   * File handling
>   * CSV
>   * JSON
>   * Datetime
>   * Logging
>   * Regex
>   * Iterator
>   * Generator
>   * Decorator
>   * Closure
>   * Context Manager
>   * Typing
>   * Dataclass
>   * Enum
>   * NamedTuple
>   * Pathlib
>
> Dự án:
>
> # 📚 Mini Project: Personal Library Management System

---

# 1. Giới thiệu dự án

Chúng ta xây dựng một ứng dụng quản lý thư viện cá nhân.

Chức năng:

```
Library Manager

├── Thêm sách
├── Xóa sách
├── Tìm kiếm sách
├── Mượn sách
├── Trả sách
├── Lưu dữ liệu
├── Xuất CSV
├── Import JSON
└── Ghi log hoạt động
```

---

# 2. Kiến trúc Project

Cấu trúc:

```
library_manager/

│
├── main.py
├── requirements.txt
│
├── app/
│   │
│   ├── models/
│   │   ├── book.py
│   │   ├── user.py
│   │   └── status.py
│   │
│   ├── services/
│   │   ├── library.py
│   │   └── search.py
│   │
│   ├── repositories/
│   │   └── storage.py
│   │
│   ├── utils/
│   │   ├── logger.py
│   │   ├── decorators.py
│   │   └── files.py
│   │
│   └── config.py
│
├── data/
│   ├── books.json
│   └── books.csv
│
└── logs/
    └── app.log
```

---

# 3. Module và Package

Package:

```
app/
```

Các module:

```
book.py
user.py
storage.py
```

Ví dụ:

```python
from app.models.book import Book
```

---

# 4. Virtual Environment

Tạo môi trường:

```bash
python -m venv venv
```

Kích hoạt:

Windows:

```bash
venv\Scripts\activate
```

Linux:

```bash
source venv/bin/activate
```

---

# 5. Model với Dataclass

File:

```
models/book.py
```

---

```python
from dataclasses import dataclass
from datetime import datetime
from .status import BookStatus


@dataclass(slots=True)
class Book:
    id: int
    title: str
    author: str
    status: BookStatus = BookStatus.AVAILABLE
    created_at: datetime = datetime.now()
```

---

Vấn đề:

```python
created_at: datetime = datetime.now()
```

Không tốt.

Vì giá trị được tạo một lần.

Sửa:

```python
from dataclasses import field


@dataclass(slots=True)
class Book:
    id: int
    title: str
    author: str
    status: BookStatus = BookStatus.AVAILABLE

    created_at: datetime = field(default_factory=datetime.now)
```

Áp dụng:

* Dataclass
* Field
* Default Factory

---

# 6. Enum quản lý trạng thái

File:

```
models/status.py
```

---

```python
from enum import StrEnum


class BookStatus(StrEnum):
    AVAILABLE = "available"

    BORROWED = "borrowed"

    LOST = "lost"
```

---

Sử dụng:

```python
book.status = BookStatus.BORROWED
```

Không dùng:

```python
book.status = "abc"
```

---

# 7. NamedTuple cho kết quả tìm kiếm

File:

```
services/search.py
```

---

```python
from typing import NamedTuple


class SearchResult(NamedTuple):
    count: int
    keyword: str
```

---

Ví dụ:

```python
result = SearchResult(10, "python")
```

---

# 8. Repository Pattern

File:

```
repositories/storage.py
```

---

Repository chịu trách nhiệm:

```
Database/File
       |
       |
 Repository
       |
       |
 Service
```

---

```python
from pathlib import Path
import json


class JsonStorage:
    def __init__(self, path: Path):
        self.path = path

    def save(self, data):

        self.path.write_text(json.dumps(data), encoding="utf-8")

    def load(self):

        if not self.path.exists():
            return []

        return json.loads(self.path.read_text(encoding="utf-8"))
```

---

Áp dụng:

* Pathlib
* JSON
* File

---

# 9. Context Manager

Tạo quản lý file.

File:

```
utils/files.py
```

---

```python
class FileManager:
    def __init__(self, path):

        self.path = path

    def __enter__(self):

        self.file = open(self.path, "r", encoding="utf-8")

        return self.file

    def __exit__(self, exc_type, exc, tb):

        self.file.close()
```

---

Sử dụng:

```python
with FileManager("data.txt") as f:
    print(f.read())
```

---

# 10. Decorator Logging

File:

```
utils/decorators.py
```

---

```python
import logging
from functools import wraps


def log_action(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        logging.info(f"Running {func.__name__}")

        result = func(*args, **kwargs)

        logging.info("Finished")

        return result

    return wrapper
```

---

Sử dụng:

```python
@log_action
def add_book(book): ...
```

---

Áp dụng:

* Decorator
* Logging

---

# 11. Logging System

File:

```
utils/logger.py
```

---

```python
import logging


logging.basicConfig(
    filename="logs/app.log", level=logging.INFO, format="%(asctime)s %(message)s"
)
```

---

Log:

```
2026-08-01 Added book
```

---

# 12. Regex tìm kiếm sách

Ví dụ:

Tìm sách theo:

```
python
Python
PYTHON
```

---

```python
import re


def search(text, keyword):

    return re.search(keyword, text, re.I)
```

---

Áp dụng:

* Regex

---

# 13. Generator đọc sách

Giả sử có 1 triệu sách.

Không load toàn bộ:

Sai:

```python
books = json.load(file)
```

Đúng:

```python
def read_books(path):

    for line in path.open():
        yield line
```

---

Lợi ích:

* Tiết kiệm RAM.
* Lazy loading.

Áp dụng:

* Generator
* Iterator

---

# 14. Iterator tùy chỉnh

Tạo:

```python
class BookIterator:
    def __init__(self, books):

        self.books = books
        self.index = 0

    def __next__(self):

        if self.index >= len(self.books):
            raise StopIteration

        book = self.books[self.index]

        self.index += 1

        return book
```

---

# 15. Closure tạo bộ lọc

Ví dụ:

```python
def create_filter(keyword):

    def filter_book(book):

        return keyword.lower() in (book.title.lower())

    return filter_book
```

---

Sử dụng:

```python
python_filter = create_filter("python")
```

---

# 16. Typing đầy đủ

Ví dụ:

```python
from typing import Iterable


def search_books(books: Iterable[Book]) -> list[Book]: ...
```

---

Áp dụng:

* Type Hint
* Iterable
* Generic

---

# 17. CSV Export

File:

```
export.py
```

---

```python
import csv


def export_csv(books):

    with open("books.csv", "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(["id", "title"])

        for book in books:
            writer.writerow([book.id, book.title])
```

---

Áp dụng:

* CSV
* File

---

# 18. Main Application

`main.py`

```python
from app.models.book import Book
from app.models.status import BookStatus


book = Book(1, "Python Advanced", "David")


print(book)
```

Output:

```
Book(
id=1,
title='Python Advanced',
author='David'
)
```

---

# 19. Luồng hoạt động

```
User
 |
 |
main.py
 |
 |
Service
 |
 |
Repository
 |
 |
JSON / CSV
 |
 |
File System
```

---

# 20. Áp dụng toàn bộ kiến thức Intermediate

| Chủ đề          | Áp dụng           |
| --------------- | ----------------- |
| Module          | app package       |
| Package         | project structure |
| Virtual Env     | venv              |
| File            | storage           |
| CSV             | export            |
| JSON            | database          |
| Datetime        | created_at        |
| Logging         | action log        |
| Regex           | search            |
| Iterator        | book iterator     |
| Generator       | large file        |
| Decorator       | logging           |
| Closure         | filter            |
| Context Manager | file              |
| Typing          | API               |
| Dataclass       | Model             |
| Enum            | Status            |
| NamedTuple      | Result            |
| Pathlib         | File path         |

---

# 21. Cải tiến Version 2

Có thể nâng cấp:

## Database

Thay:

```
JSON
```

bằng:

```
SQLite
```

---

## CLI

Thêm:

```
click
```

hoặc:

```
argparse
```

Ví dụ:

```bash
library add book.json

library search python
```

---

## REST API

Dùng:

```
FastAPI
```

---

## GUI

Dùng:

```
PySide6
```

---

# 22. Bài tập cuối khóa Python Intermediate

## Nhiệm vụ:

Xây dựng:

# Personal Note Manager

Chức năng:

```
Note Manager

├── Create note
├── Update note
├── Delete note
├── Search note
├── Export CSV
├── Backup JSON
└── Logging
```

Yêu cầu:

* Dataclass cho Note.
* Enum cho Status.
* Pathlib quản lý file.
* JSON lưu dữ liệu.
* CSV export.
* Regex tìm kiếm.
* Generator đọc note.
* Decorator log.
* Context Manager.
* Type Hint đầy đủ.

---

# Kết thúc Python Intermediate

Bạn đã hoàn thành roadmap:

```
Python Intermediate

21 Module
22 Package
23 Virtual Environment
24 File
25 CSV
26 JSON
27 Datetime
28 Logging
29 Regex
30 Iterator
31 Generator
32 Decorator
33 Closure
34 Context Manager
35 Typing
36 Dataclass
37 Enum
38 NamedTuple
39 Pathlib
40 Mini Project
```

---

## Bước tiếp theo

Sau Python Intermediate, lộ trình tiếp theo nên là:

# Python Advanced

Gồm:

1. Memory Management
2. Garbage Collector
3. Descriptor
4. Metaclass
5. Abstract Base Class nâng cao
6. Protocol
7. Generic nâng cao
8. Async Programming
9. Multiprocessing
10. Threading
11. Profiling
12. Packaging nâng cao
13. Testing chuyên sâu
14. Design Pattern
15. Architecture
16. Framework Design
17. Build Library Production

Đây là giai đoạn chuyển từ **Python Developer → Python Engineer**.
