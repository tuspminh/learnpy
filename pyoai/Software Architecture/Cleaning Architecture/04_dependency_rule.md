# Clean Architecture Deep Dive

# Buổi 4: Dependency Rule – Luật quan trọng nhất của Clean Architecture

Đến đây chúng ta đã học:

  * Buổi 1: Clean Architecture là gì 
  * Buổi 2: Coupling & Cohesion 
  * Buổi 3: SOLID 



Hôm nay chúng ta sẽ học **linh hồn của Clean Architecture**.

> Nếu chỉ được nhớ **một quy tắc duy nhất** của Clean Architecture thì đó chính là **Dependency Rule**.

Nhiều lập trình viên biết vẽ sơ đồ Clean Architecture nhưng khi code lại **vi phạm Dependency Rule** , khiến kiến trúc nhanh chóng trở thành "Layered Architecture" hoặc "Spaghetti Architecture".

* * *

# Mục tiêu buổi học

Sau buổi này bạn sẽ hiểu:

  * Dependency là gì? 
  * Dependency Rule là gì? 
  * Tại sao mũi tên luôn hướng vào trong? 
  * Phụ thuộc khi import trong Python 
  * Circular Import xảy ra như thế nào? 
  * Cách tổ chức package Python đúng 
  * Áp dụng vào dự án cào truyện 



* * *

# 1\. Dependency là gì?

Dependency nghĩa là:

> **Module A cần Module B để hoạt động.**

Ví dụ:
    
    
    from pathlib import Path
    
    p = Path("demo.txt")

Sơ đồ:
    
    
    My Code
        │
        ▼
    pathlib.Path

Code của bạn phụ thuộc `Path`.

* * *

Ví dụ khác
    
    
    import sqlite3

Có nghĩa:
    
    
    Application
    
    ↓
    
    sqlite3

Application phụ thuộc sqlite3.

* * *

# Dependency trong Python

Có rất nhiều cách tạo dependency.

Ví dụ:

## Import
    
    
    from requests import Session

* * *

## Kế thừa
    
    
    class MyRepo(SQLiteRepository):
        ...

* * *

## Khởi tạo object
    
    
    repo = SQLiteRepository()

* * *

## Type Hint
    
    
    def foo(repo: SQLiteRepository):
        ...

Ngay cả type hint cũng tạo ra dependency (trừ khi dùng Protocol, forward reference hoặc `from __future__ import annotations` trong một số trường hợp).

* * *

# Dependency Rule

Luật:

> **Source code dependency chỉ được hướng vào trong.**

Hãy xem sơ đồ.
    
    
    +---------------------------+
    | Presentation              |
    +---------------------------+
    
                ↓
    
    +---------------------------+
    | Application               |
    +---------------------------+
    
                ↓
    
    +---------------------------+
    | Domain                    |
    +---------------------------+

Mọi mũi tên đều hướng vào Domain.

* * *

# Domain là trung tâm

Domain là nơi chứa:
    
    
    Story
    
    Chapter
    
    Author
    
    Category
    
    Value Objects
    
    Business Rules

Domain không biết:

  * SQLite 
  * Redis 
  * FastAPI 
  * PySide6 
  * Celery 
  * Requests 



Không biết gì cả.

* * *

# Ví dụ sai

Entity:
    
    
    from sqlite3 import connect
    
    
    class Story:
    
        def save(self):
            conn = connect("story.db")

Sơ đồ:
    
    
    Story
    
    ↓
    
    SQLite

Domain phụ thuộc Database.

Vi phạm Dependency Rule.

* * *

# Đúng
    
    
    from dataclasses import dataclass
    
    
    @dataclass
    class Story:
        id: int
        title: str

Không import gì ngoài thư viện chuẩn cần thiết để mô hình hóa dữ liệu.

* * *

# Application Layer

Ví dụ
    
    
    class SaveStoryUseCase:
    
        def execute(self, story):
            ...

UseCase biết:

  * Story 
  * Repository Interface 



Không biết:

  * SQLite 
  * PostgreSQL 
  * Redis 



* * *

# Infrastructure

Infrastructure mới là nơi biết:
    
    
    SQLite
    
    Requests
    
    BeautifulSoup
    
    Redis
    
    Celery
    
    Filesystem

Ví dụ:
    
    
    class SQLiteRepository(StoryRepository):
        ...

Infrastructure phụ thuộc Domain.

Domain không phụ thuộc Infrastructure.

* * *

# Vì sao mũi tên luôn hướng vào trong?

Giả sử hôm nay bạn dùng:
    
    
    SQLite

Mai đổi sang:
    
    
    PostgreSQL

Nếu Domain biết SQLite:
    
    
    Story
    
    ↓
    
    SQLite

Bạn phải sửa Domain.

* * *

Nếu Domain không biết SQLite:
    
    
    Story

Không phải sửa gì.

Chỉ sửa:
    
    
    SQLiteRepository
    
    ↓
    
    PostgresRepository

Business vẫn giữ nguyên.

* * *

# Một ví dụ hoàn chỉnh

Sai:
    
    
    class Story:
    
        def save(self):
            sqlite.save(self)

Đúng:
    
    
    @dataclass
    class Story:
        id: int
        title: str

UseCase:
    
    
    class SaveStoryUseCase:
    
        def __init__(self, repo):
            self.repo = repo
    
        def execute(self, story):
            self.repo.save(story)

SQLite:
    
    
    class SQLiteRepository:
    
        def save(self, story):
            print("Saved")

Luồng:
    
    
    UI
    
    ↓
    
    UseCase
    
    ↓
    
    Repository Interface
    
    ↓
    
    SQLiteRepository
    
    ↓
    
    SQLite

Không bao giờ:
    
    
    Story
    
    ↓
    
    SQLite

* * *

# Phụ thuộc bằng import

Đây là lỗi rất phổ biến.

Giả sử:
    
    
    domain/
        story.py
    
    presentation/
        window.py

Nếu:
    
    
    # story.py
    
    from presentation.window import MainWindow

Sơ đồ:
    
    
    Domain
    
    ↓
    
    Presentation

Sai hoàn toàn.

* * *

# Đúng

Presentation:
    
    
    from application.usecases import SaveStoryUseCase

Application:
    
    
    from domain.story import Story

Domain:
    
    
    # Không import presentation

Sơ đồ:
    
    
    Presentation
    
    ↓
    
    Application
    
    ↓
    
    Domain

* * *

# Circular Import

Đây là lỗi mà hầu như lập trình viên Python nào cũng từng gặp.

Ví dụ:
    
    
    # a.py
    
    from b import B
    
    
    # b.py
    
    from a import A

Kết quả:
    
    
    A
    
    ↓
    
    B
    
    ↓
    
    A

Python báo:
    
    
    ImportError
    
    cannot import partially initialized module

* * *

# Vì sao Circular Import xuất hiện?

Do vi phạm Dependency Rule.

Ví dụ:
    
    
    UI
    
    ↓
    
    Repository
    
    ↓
    
    Parser
    
    ↓
    
    UI

Hoặc:
    
    
    Parser
    
    ↓
    
    Repository
    
    ↓
    
    Parser

Đó là dấu hiệu các tầng đang biết quá nhiều về nhau.

* * *

# Cách giải quyết

Thay vì:
    
    
    Parser
    
    ↓
    
    Repository

Ta đưa Interface vào giữa.
    
    
    Parser
    
    ↓
    
    ParserOutput

UseCase nhận kết quả rồi quyết định lưu.

Parser không biết Repository.

* * *

# Package đúng trong Python

Một cấu trúc điển hình:
    
    
    project/
    
        domain/
            entities/
            repositories/
            services/
    
        application/
            dto/
            usecases/
    
        infrastructure/
            database/
            http/
            parser/
            cache/
    
        presentation/
            cli/
            gui/

Luật import:
    
    
    Presentation
    
    ↓
    
    Application
    
    ↓
    
    Domain

Infrastructure:
    
    
    Infrastructure
    
    ↓
    
    Domain

Không có:
    
    
    Domain
    
    ↓
    
    Infrastructure

* * *

# Áp dụng vào app cào truyện

Giả sử Plugin:

Sai:
    
    
    class TruyenFullPlugin:
    
        def fetch(self):
            ...
    
        def save_database(self):
            ...

Plugin biết Database.

* * *

Đúng:
    
    
    class TruyenFullPlugin:
    
        def fetch_story(self):
            return Story(...)

UseCase:
    
    
    story = plugin.fetch_story()
    
    repo.save(story)

Plugin không biết Database.

* * *

# Dependency Graph

Sai:
    
    
    Presentation
    
    ↓
    
    Application
    
    ↓
    
    Infrastructure
    
    ↓
    
    Domain
    
    ↓
    
    Infrastructure

Có vòng.

* * *

Đúng:
    
    
    Presentation
    
    ↓
    
    Application
    
    ↓
    
    Domain
    
    Infrastructure
    
    ↓
    
    Domain

Application và Infrastructure đều phụ thuộc Domain, nhưng Domain không biết hai tầng còn lại.

* * *

# Ví dụ thực tế với PySide6

Sai:
    
    
    class MainWindow(QMainWindow):
    
        def on_click(self):
            conn = sqlite3.connect(...)

UI biết Database.

* * *

Đúng:
    
    
    class MainWindow(QMainWindow):
    
        def on_click(self):
            self.save_story.execute(...)

UseCase quyết định làm gì.

* * *

# Ví dụ với Celery

Sai:

Task:
    
    
    sqlite.save()
    
    redis.publish()
    
    window.update()
    
    messagebox.show()

Task biết quá nhiều.

* * *

Đúng:
    
    
    task()
    
    ↓
    
    UseCase
    
    ↓
    
    Repository

Task chỉ là điểm vào (entry point).

* * *

# Dependency Rule và Plugin Architecture

Plugin:
    
    
    Plugin
    
    ↓
    
    Source Interface

Không:
    
    
    Plugin
    
    ↓
    
    SQLite
    
    ↓
    
    PySide
    
    ↓
    
    Redis

Nhờ đó plugin có thể tái sử dụng ở:

  * CLI 
  * PySide6 
  * FastAPI 
  * Worker Celery 



mà không cần sửa code.

* * *

# Phân tích dự án cào truyện của chúng ta

Đây là hướng tổ chức nên theo:
    
    
    story_scraper/
    
    ├── domain/
    │   ├── entities/
    │   ├── value_objects/
    │   ├── repositories/
    │   └── services/
    │
    ├── application/
    │   ├── dto/
    │   ├── use_cases/
    │   └── ports/
    │
    ├── infrastructure/
    │   ├── database/
    │   ├── http/
    │   ├── parser/
    │   ├── cache/
    │   └── plugins/
    │
    ├── presentation/
    │   ├── cli/
    │   ├── pyside/
    │   └── api/
    │
    └── main.py

Quy tắc import:

  * `presentation` → import `application`
  * `application` → import `domain`
  * `infrastructure` → import `domain` và hiện thực các interface 
  * `domain` → **không import** `application`, `presentation`, `infrastructure`



Nếu giữ được quy tắc này, bạn sẽ giảm đáng kể nguy cơ `circular import` và việc thay đổi framework hay cơ sở dữ liệu sẽ ít ảnh hưởng đến nghiệp vụ.

* * *

# Checklist tự kiểm tra

Mỗi khi viết code, hãy tự hỏi:

  * Domain có import `sqlite3`, `requests`, `PySide6` hay `redis` không? 
  * UseCase có đang khởi tạo `SQLiteRepository()` trực tiếp không? 
  * UI có đang truy cập database trực tiếp không? 
  * Có import ngược từ tầng trong ra tầng ngoài không? 
  * Có xuất hiện `circular import` không? 



Nếu có, hãy xem lại Dependency Rule trước khi tiếp tục.

* * *

# Bài tập

## Bài 1

Cho sơ đồ sau:
    
    
    UI
    ↓
    
    UseCase
    ↓
    
    SQLiteRepository
    ↓
    
    Story

Hãy chỉ ra Dependency Rule bị vi phạm ở đâu và vẽ lại sơ đồ đúng.

* * *

## Bài 2

Thiết kế package cho dự án cào truyện gồm:

  * Domain 
  * Application 
  * Infrastructure 
  * Presentation 



Sau đó ghi rõ **package nào được phép import package nào**.

* * *

## Bài 3

Trong dự án hiện tại của bạn, chọn một module (ví dụ `parser`, `repository` hoặc `plugin`) và kiểm tra:

  * Nó đang import những module nào? 
  * Có import từ tầng cao hơn không? 
  * Có thể thay bằng interface hoặc chuyển trách nhiệm sang UseCase để loại bỏ phụ thuộc không? 



* * *

Ở **Buổi 5** , chúng ta sẽ học **Architectural Boundaries (Ranh giới kiến trúc)**. Bạn sẽ hiểu cách xác định ranh giới giữa Domain, Application, Infrastructure và Presentation, cách dữ liệu đi qua các tầng bằng DTO/Mapper, và vì sao việc giữ ranh giới rõ ràng quan trọng không kém chính các tầng trong Clean Architecture. Đây là bước chuyển từ lý thuyết sang cách tổ chức một codebase Python lớn một cách chuyên nghiệp.

