# Clean Architecture Deep Dive

# Buổi 5: Architectural Boundaries (Ranh giới kiến trúc)

Đến buổi này, chúng ta đã có nền tảng:

  * Buổi 1: Clean Architecture là gì 
  * Buổi 2: Coupling & Cohesion 
  * Buổi 3: SOLID 
  * Buổi 4: Dependency Rule 



Hôm nay chúng ta học một chủ đề mà nhiều lập trình viên bỏ qua:

> **Boundary (Ranh giới kiến trúc).**

Thực tế, rất nhiều project có đủ các thư mục:
    
    
    domain/
    application/
    infrastructure/
    presentation/

nhưng vẫn **không phải Clean Architecture**.

Lý do là:

> **Ranh giới giữa các tầng bị phá vỡ.**

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Boundary là gì? 
  * Vì sao Boundary quan trọng hơn cả thư mục 
  * Data đi qua các tầng như thế nào 
  * DTO là gì? 
  * Mapper là gì? 
  * Vì sao Entity không nên đi khắp ứng dụng 
  * Boundary trong dự án cào truyện 



* * *

# 1\. Boundary là gì?

Boundary nghĩa là:

> **Đường ranh giới giữa hai tầng.**

Ví dụ:
    
    
    Presentation
    
    ==================
    
    Application
    
    ==================
    
    Domain
    
    ==================
    
    Infrastructure

Dấu "=" chính là Boundary.

Boundary quy định:

  * Dữ liệu nào được đi qua 
  * Ai được gọi ai 
  * Ai không được biết ai 



* * *

# Ví dụ đời thực

Ngân hàng.

Bạn ra quầy giao dịch.
    
    
    Khách hàng
    
    ↓
    
    Nhân viên
    
    ↓
    
    Hệ thống ngân hàng
    
    ↓
    
    Database

Bạn không bao giờ được:
    
    
    Khách hàng
    
    ↓
    
    Database

Nhân viên chính là Boundary.

* * *

# Trong phần mềm

Sai:
    
    
    PySide
    
    ↓
    
    SQLite

Button click:
    
    
    conn.execute(...)

UI đang xuyên thủng Boundary.

* * *

Đúng:
    
    
    PySide
    
    ↓
    
    CreateStoryUseCase
    
    ↓
    
    Repository
    
    ↓
    
    SQLite

UI không biết Database.

* * *

# Vì sao cần Boundary?

Ví dụ.

Mai đổi
    
    
    PySide
    
    ↓
    
    FastAPI

Nếu UI gọi SQLite trực tiếp.

Bạn phải sửa:

  * UI 
  * Database 
  * Logic 



Nếu UI chỉ gọi UseCase.

Bạn chỉ thay Presentation.

Boundary bảo vệ Application.

* * *

# Luồng dữ liệu

Một request chuẩn.
    
    
    UI
    
    ↓
    
    Controller
    
    ↓
    
    UseCase
    
    ↓
    
    Repository
    
    ↓
    
    SQLite

Dữ liệu quay lại.
    
    
    SQLite
    
    ↓
    
    Repository
    
    ↓
    
    UseCase
    
    ↓
    
    Presenter
    
    ↓
    
    UI

Đây chính là Boundary.

* * *

# Ví dụ app cào truyện

Người dùng nhập URL.
    
    
    https://truyenfull.vn/...

Luồng:
    
    
    MainWindow
    
    ↓
    
    DownloadStoryController
    
    ↓
    
    DownloadStoryUseCase
    
    ↓
    
    SourcePlugin
    
    ↓
    
    HTML
    
    ↓
    
    Parser
    
    ↓
    
    Story Entity
    
    ↓
    
    Repository
    
    ↓
    
    SQLite

Mỗi tầng chỉ biết tầng kế tiếp.

* * *

# Sai lầm phổ biến

Nhiều người làm thế này.
    
    
    MainWindow
    
    ↓
    
    Requests
    
    ↓
    
    BeautifulSoup
    
    ↓
    
    SQLite

MainWindow biết tất cả.

Không còn Boundary.

* * *

# DTO là gì?

DTO

=

Data Transfer Object

Nó chỉ dùng để truyền dữ liệu.

Ví dụ.

Entity
    
    
    from dataclasses import dataclass
    
    
    @dataclass(slots=True)
    class Story:
        id: int
        title: str
        author: str

DTO
    
    
    from dataclasses import dataclass
    
    
    @dataclass(slots=True)
    class CreateStoryInput:
        title: str
        author: str

Khác nhau.

Entity

↓

Business

DTO

↓

Communication

* * *

# Tại sao không truyền Entity?

Ví dụ.

UI.
    
    
    story.title = ""

Hoặc
    
    
    story.id = -999

UI đang sửa Business Object.

Không tốt.

* * *

Đúng.

UI tạo DTO.
    
    
    dto = CreateStoryInput(
        title="Đấu Phá Thương Khung",
        author="Thiên Tằm Thổ Đậu"
    )

UseCase nhận DTO.
    
    
    use_case.execute(dto)

UseCase quyết định tạo Entity.

* * *

# Mapper

Mapper là bộ chuyển đổi.

Ví dụ.

DTO

↓

Entity
    
    
    class StoryMapper:
    
        @staticmethod
        def to_entity(dto):
            return Story(
                id=0,
                title=dto.title,
                author=dto.author,
            )

Ngược lại.

Entity

↓

DTO
    
    
    class StoryMapper:
    
        @staticmethod
        def to_output(story):
            return StoryResponse(
                id=story.id,
                title=story.title,
                author=story.author,
            )

Mapper chính là Boundary giữa hai tầng.

* * *

# Một ví dụ hoàn chỉnh

UI
    
    
    dto = CreateStoryInput(
        title="One Piece",
        author="Oda"
    )
    
    use_case.execute(dto)

UseCase
    
    
    entity = mapper.to_entity(dto)
    
    repo.save(entity)

Repository
    
    
    INSERT ...

Không tầng nào phá Boundary.

* * *

# Entity không nên đi khắp ứng dụng

Đây là lỗi rất phổ biến.

Sai.
    
    
    Entity
    
    ↓
    
    UI
    
    ↓
    
    JSON
    
    ↓
    
    API
    
    ↓
    
    Database
    
    ↓
    
    Redis

Entity xuất hiện khắp nơi.

Mai sửa Entity.

Toàn project lỗi.

* * *

Đúng.
    
    
    Entity
    
    ↓
    
    UseCase
    
    ↓
    
    DTO
    
    ↓
    
    Presentation

Entity chỉ sống trong Domain và Application.

* * *

# Output Boundary

UseCase không trả:
    
    
    QTableWidget

Không trả:
    
    
    QPixmap

Không trả:
    
    
    HTML

Chỉ trả DTO.

Ví dụ.
    
    
    @dataclass
    class StoryOutput:
    
        id: int
        title: str

Presentation quyết định hiển thị.

* * *

# Controller

Controller nhận Input.
    
    
    dto = CreateStoryInput(...)

Gọi.
    
    
    use_case.execute(dto)

Controller không parse HTML.

Không lưu DB.

Không tạo UI.

* * *

# Presenter

Presenter nhận Output DTO.

Ví dụ.
    
    
    StoryOutput

Nó chuyển thành.
    
    
    QTableWidgetItem

Hoặc.
    
    
    JSON

Hoặc.
    
    
    CLI Text

Đây chính là Boundary.

* * *

# Ví dụ với FastAPI

Sai.
    
    
    @app.post("/story")
    def create_story():
    
        sqlite.save(...)

API biết SQLite.

* * *

Đúng.
    
    
    @app.post("/story")
    def create_story():
    
        dto = CreateStoryInput(...)
    
        use_case.execute(dto)

* * *

# Ví dụ với PySide6

Sai.
    
    
    button.clicked.connect(save_sqlite)

Đúng.
    
    
    button.clicked.connect(controller.save_story)

Controller gọi UseCase.

* * *

# Boundary trong Plugin

Sai.

Plugin.
    
    
    def fetch():
    
        sqlite.save(...)

Plugin biết Database.

* * *

Đúng.

Plugin.
    
    
    def fetch():
    
        return Story(...)

UseCase lưu.

Plugin không biết DB.

* * *

# Boundary trong Celery

Sai.

Worker.
    
    
    download()
    
    save()
    
    update_ui()

Worker biết UI.

* * *

Đúng.
    
    
    Worker
    
    ↓
    
    UseCase

Worker chỉ kích hoạt UseCase.

* * *

# Boundary trong Repository

Sai.
    
    
    repo.save()
    
    ↓
    
    QMessageBox()

Repository biết UI.

* * *

Đúng.

Repository chỉ.
    
    
    SQL

Không hơn.

* * *

# Ví dụ hoàn chỉnh của ứng dụng cào truyện
    
    
                     USER
    
                      │
                      ▼
    
              MainWindow (Presentation)
    
                      │
    
          DownloadStoryController
    
                      │
    
            DownloadStoryUseCase
    
                      │
    
          StoryRepository (Interface)
    
                      │
    
           SQLiteStoryRepository
    
                      │
    
                  SQLite

Nếu muốn chuyển sang Web:
    
    
    FastAPI
    
    ↓
    
    DownloadStoryController
    
    ↓
    
    DownloadStoryUseCase

Không phải sửa Domain.

* * *

# Một project Python chuẩn
    
    
    story_app/
    
    ├── domain/
    │   ├── entities/
    │   ├── value_objects/
    │   ├── repositories/
    │   └── services/
    │
    ├── application/
    │   ├── dto/
    │   ├── use_cases/
    │   ├── mappers/
    │   └── ports/
    │
    ├── infrastructure/
    │   ├── database/
    │   ├── http/
    │   ├── cache/
    │   ├── parser/
    │   └── plugins/
    │
    ├── presentation/
    │   ├── cli/
    │   ├── gui/
    │   ├── api/
    │   ├── controllers/
    │   └── presenters/
    │
    └── main.py

Đây là cấu trúc thường thấy trong các dự án Python quy mô lớn, đặc biệt khi kết hợp với Repository Pattern, Plugin Architecture và Dependency Injection.

* * *

# Những hiểu lầm phổ biến

## Hiểu lầm 1

> Chỉ cần chia thư mục là có Clean Architecture.

Sai.

Điều quan trọng là **luồng phụ thuộc** và **Boundary** , không phải tên thư mục.

* * *

## Hiểu lầm 2

> Entity có thể dùng để trả JSON trực tiếp.

Không nên.

Entity là Business Model.

API nên trả Response DTO.

* * *

## Hiểu lầm 3

> DTO chỉ dành cho Web API.

Sai.

DTO rất hữu ích cho:

  * PySide6 
  * CLI 
  * Celery 
  * Plugin 
  * Unit Test 



Bất cứ nơi nào dữ liệu đi qua Boundary.

* * *

# Checklist

Khi review code, hãy tự hỏi:

  * UI có đang gọi database trực tiếp không? 
  * Entity có bị trả ra ngoài Presentation không? 
  * Có DTO ở đầu vào và đầu ra UseCase không? 
  * Có Mapper chuyển đổi giữa DTO và Entity không? 
  * Repository có chứa code UI hoặc HTTP không? 
  * Plugin có biết Database hoặc GUI không? 



Nếu tất cả câu trả lời đều là **không** , ranh giới kiến trúc của bạn đang được giữ tốt.

* * *

# Bài tập

## Bài 1

Thiết kế luồng dữ liệu cho chức năng:

> "Người dùng nhập URL truyện → tải thông tin → lưu cơ sở dữ liệu → hiển thị kết quả"

Xác định rõ:

  * Controller 
  * Input DTO 
  * UseCase 
  * Mapper 
  * Entity 
  * Repository 
  * Output DTO 
  * Presenter 



* * *

## Bài 2

Viết hai lớp:
    
    
    @dataclass(slots=True)
    class CreateStoryInput:
        title: str
        author: str

và
    
    
    @dataclass(slots=True)
    class StoryOutput:
        id: int
        title: str
        author: str

Sau đó viết `StoryMapper` để chuyển đổi giữa DTO và `Story`.

* * *

## Bài 3

Xem lại dự án cào truyện của bạn và trả lời:

  * Những module nào đang **xuyên Boundary** (ví dụ: UI gọi database, plugin lưu SQLite, parser cập nhật progress bar)? 
  * Nếu đưa toàn bộ nghiệp vụ vào **UseCase** , bạn sẽ loại bỏ được bao nhiêu phụ thuộc? 



* * *

## Tổng kết giai đoạn 1

Đến đây bạn đã nắm được **5 nền tảng quan trọng nhất của Clean Architecture** :

  1. Mục tiêu của Clean Architecture. 
  2. Coupling & Cohesion. 
  3. SOLID. 
  4. Dependency Rule. 
  5. Architectural Boundaries. 



Đây là phần "tư duy kiến trúc". Từ **Buổi 6** , chúng ta sẽ bắt đầu đi sâu vào **Domain Layer** , bắt đầu với **Entity** : cách thiết kế Entity giàu nghiệp vụ (Rich Domain Model), cách bảo vệ invariant, tránh Anemic Domain Model, và xây dựng các Entity đủ mạnh để làm nền tảng cho toàn bộ hệ thống cào truyện của bạn.

