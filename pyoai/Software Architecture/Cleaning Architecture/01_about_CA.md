# Buổi 1

# Clean Architecture là gì?

Trước tiên hãy quên framework.

Quên SQLite.

Quên FastAPI.

Quên Django.

Quên PySide.

Quên Redis.

Quên Celery.

Clean Architecture nói rằng:

> **Business của bạn phải sống được dù mọi công nghệ bên ngoài thay đổi.**

Ví dụ.

Hôm nay
    
    
    PySide6

Mai
    
    
    FastAPI

Mốt
    
    
    Web

Business vẫn không đổi.

* * *

# Ví dụ

Ứng dụng quản lý truyện.

Business:
    
    
    Đăng nhập
    
    ↓
    
    Tìm truyện
    
    ↓
    
    Lấy chương
    
    ↓
    
    Lưu database
    
    ↓
    
    Đọc

Business này tồn tại.

Cho dù UI là
    
    
    PySide
    
    hay
    
    Web
    
    hay
    
    CLI

Business vẫn vậy.

* * *

# Kiến trúc truyền thống

Đa số project Python nhỏ đều như thế này.
    
    
    main.py
    
    ↓
    
    sqlite.py
    
    ↓
    
    requests.py
    
    ↓
    
    logic.py
    
    ↓
    
    UI.py

Mọi thứ gọi lẫn nhau.

Ví dụ
    
    
    button clicked
    
    ↓
    
    sqlite
    
    ↓
    
    requests
    
    ↓
    
    logic
    
    ↓
    
    print

Không có ranh giới.

* * *

# Hậu quả

Sau vài tháng.
    
    
    UI
    
    ↓
    
    Repository
    
    ↓
    
    Model
    
    ↓
    
    API
    
    ↓
    
    Parser
    
    ↓
    
    Logger
    
    ↓
    
    Cache
    
    ↓
    
    Email

Gọi chéo nhau.

Ví dụ
    
    
    Parser
    
    import UI

hoặc
    
    
    Repository
    
    import Requests

hoặc
    
    
    Entity
    
    import sqlite3

Đây gọi là

**Spaghetti Architecture**

* * *

# Clean Architecture giải quyết gì?

Nó chia ứng dụng thành các vòng tròn.
    
    
              +----------------------+
              | Framework & Drivers  |
              +----------------------+
    
                     ↓
    
              +----------------------+
              | Interface Adapters   |
              +----------------------+
    
                     ↓
    
              +----------------------+
              | Application          |
              +----------------------+
    
                     ↓
    
              +----------------------+
              | Domain               |
              +----------------------+

Quan trọng:

**Chỉ được phụ thuộc từ ngoài vào trong.**

Không bao giờ ngược lại.

* * *

# Domain là trái tim

Ví dụ ứng dụng truyện.

Domain chỉ biết:
    
    
    Story
    
    Chapter
    
    Author
    
    Category

Nó không biết:
    
    
    SQLite
    
    PySide
    
    Redis
    
    FastAPI
    
    Celery

Không biết gì hết.

* * *

Ví dụ Entity
    
    
    from dataclasses import dataclass
    
    
    @dataclass
    class Story:
        id: int
        title: str
        author: str

Đây là Domain.

Không có SQL.

Không có requests.

Không có UI.

* * *

# Sai lầm phổ biến

Nhiều người viết
    
    
    class Story:
    
        def save(self):
            ...

Hoặc
    
    
    class Story:
    
        def load(self):
            ...

Sai.

Vì
    
    
    Story
    
    ↓
    
    SQLite

Domain đã phụ thuộc Infrastructure.

* * *

Đúng phải là
    
    
    Story
    
    ↓
    
    không phụ thuộc ai

* * *

# Application Layer

Giả sử người dùng bấm
    
    
    Lưu truyện

Không phải UI lưu.

UI chỉ gửi yêu cầu.
    
    
    UI
    
    ↓
    
    CreateStoryUseCase
    
    ↓
    
    Repository
    
    ↓
    
    Database

UI không biết SQLite.

* * *

# Repository Interface

Application chỉ biết Interface.
    
    
    from abc import ABC, abstractmethod
    from typing import Optional
    
    
    class StoryRepository(ABC):
    
        @abstractmethod
        def save(self, story):
            ...
    
        @abstractmethod
        def get(self, story_id: int) -> Optional[object]:
            ...

Không có SQLite.

Không có MySQL.

* * *

# SQLite Repository

Infrastructure thực hiện interface.
    
    
    class SQLiteStoryRepository(StoryRepository):
    
        def save(self, story):
            print("Save SQLite")
    
        def get(self, story_id):
            ...

Mai đổi sang PostgreSQL.

Chỉ cần
    
    
    class PostgreSQLStoryRepository(StoryRepository):
        ...

Use Case không đổi.

* * *

# Use Case
    
    
    class CreateStoryUseCase:
    
        def __init__(self, repository: StoryRepository):
            self.repository = repository
    
        def execute(self, story):
            self.repository.save(story)

Không biết SQLite.

Không biết ORM.

Không biết UI.

* * *

# UI

Ví dụ PySide.
    
    
    story = Story(
        id=1,
        title="Đấu Phá Thương Khung",
        author="Thiên Tằm Thổ Đậu",
    )
    
    use_case.execute(story)

UI chỉ gọi Use Case.

* * *

# Dependency Rule

Đây là luật quan trọng nhất.
    
    
    UI
    
    ↓
    
    UseCase
    
    ↓
    
    Repository Interface
    
    ↓
    
    Entity

Không bao giờ
    
    
    Entity
    
    ↓
    
    UI

Không bao giờ
    
    
    Entity
    
    ↓
    
    SQLite

Không bao giờ
    
    
    Entity
    
    ↓
    
    Requests

* * *

# Ví dụ hoàn chỉnh
    
    
    app/
    
        domain/
    
            story.py
    
        application/
    
            create_story.py
    
        interfaces/
    
            repository.py
    
        infrastructure/
    
            sqlite_repo.py
    
        ui/
    
            main.py

Luồng chạy:
    
    
    Button
    
    ↓
    
    CreateStoryUseCase
    
    ↓
    
    StoryRepository
    
    ↓
    
    SQLiteRepository
    
    ↓
    
    SQLite

Entity hoàn toàn độc lập.

* * *

# Nếu đổi công nghệ thì sao?

Đổi
    
    
    SQLite

thành
    
    
    PostgreSQL

Chỉ sửa
    
    
    sqlite_repo.py

* * *

Đổi
    
    
    PySide6

thành
    
    
    FastAPI

Chỉ sửa
    
    
    ui/

* * *

Đổi
    
    
    requests

thành
    
    
    httpx

Chỉ sửa
    
    
    Infrastructure

Business không đổi.

Đó chính là mục tiêu lớn nhất của Clean Architecture.

* * *

# Liên hệ với dự án cào truyện của chúng ta

Clean Architecture đặc biệt phù hợp với hệ thống cào truyện mà bạn đang xây dựng. Một cấu trúc điển hình sẽ là:
    
    
    story_scraper/
    
    ├── domain/
    │   ├── entities/
    │   ├── value_objects/
    │   ├── repositories/
    │   └── services/
    │
    ├── application/
    │   ├── use_cases/
    │   ├── dto/
    │   └── ports/
    │
    ├── infrastructure/
    │   ├── database/
    │   ├── http/
    │   ├── parser/
    │   ├── cache/
    │   ├── queue/
    │   └── plugins/
    │
    ├── presentation/
    │   ├── pyside/
    │   ├── cli/
    │   └── api/
    │
    └── main.py

Với kiến trúc này:

  * Có thể thay **PySide6** bằng **FastAPI** mà không sửa Domain hay Use Case. 
  * Có thể thay **SQLite** bằng **PostgreSQL** chỉ bằng cách đổi Repository. 
  * Có thể bổ sung nguồn truyện mới (plugin) mà không ảnh hưởng đến logic nghiệp vụ. 
  * Có thể viết Unit Test cho Use Case mà không cần database thật. 



* * *

# Bài tập

## Bài 1

Vẽ lại sơ đồ phụ thuộc:
    
    
    Presentation
          ↓
    Application
          ↓
    Repository Interface
          ↓
    Domain

Giải thích vai trò của từng tầng bằng lời của bạn.

* * *

## Bài 2

Tạo cấu trúc thư mục:
    
    
    clean_architecture_demo/
    ├── domain/
    ├── application/
    ├── infrastructure/
    ├── presentation/
    └── main.py

Chưa cần viết code.

* * *

## Bài 3

Tự trả lời các câu hỏi sau:

  1. Tại sao `Story` không nên chứa `save()`? 
  2. Tại sao Use Case chỉ phụ thuộc vào `StoryRepository` (interface) mà không phụ thuộc `SQLiteStoryRepository`? 
  3. Nếu chuyển từ PySide6 sang FastAPI thì tầng nào thay đổi? Tầng nào giữ nguyên? 



* * *

Ở **Buổi 2** , chúng ta sẽ đi vào nền tảng quan trọng nhất của mọi kiến trúc phần mềm: **Coupling và Cohesion**. Bạn sẽ hiểu vì sao một số dự án càng phát triển càng khó sửa, trong khi những dự án khác vẫn dễ bảo trì sau nhiều năm. Đây là kiến thức cốt lõi để hiểu sâu Clean Architecture chứ không chỉ học thuộc sơ đồ.

