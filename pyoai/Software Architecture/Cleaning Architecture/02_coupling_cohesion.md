# Clean Architecture Deep Dive

# Buổi 2: Coupling và Cohesion – Nền móng của mọi kiến trúc phần mềm

Ở buổi trước chúng ta đã biết mục tiêu của Clean Architecture:

> **Business phải độc lập với công nghệ.**

Nhưng câu hỏi quan trọng là:

> **Làm sao biết một thiết kế tốt hay xấu?**

Câu trả lời nằm ở hai khái niệm mà mọi Software Architect đều phải thành thạo:

  * **Coupling (Độ phụ thuộc)**
  * **Cohesion (Độ gắn kết)**



Đây là hai thước đo chất lượng thiết kế, không chỉ trong Clean Architecture mà còn trong OOP, DDD, Hexagonal Architecture, Microservices,...

* * *

# Mục tiêu buổi học

Sau buổi này bạn sẽ hiểu:

  * Coupling là gì 
  * Cohesion là gì 
  * Vì sao High Cohesion + Low Coupling là mục tiêu 
  * Các loại Coupling 
  * Các loại Cohesion 
  * Cách nhận biết code "có mùi" (Code Smell) 
  * Áp dụng vào app cào truyện của chúng ta 



* * *

# 1\. Coupling là gì?

Coupling = **mức độ phụ thuộc giữa các module.**

Ví dụ:
    
    
    A
    ↓
    
    B

Nếu A chỉ hoạt động khi B tồn tại

→ A phụ thuộc B.

Nếu đổi B phải sửa A

→ Coupling cao.

* * *

Ví dụ:
    
    
    class SQLiteRepository:
    
        def save(self):
            print("Save")

UseCase:
    
    
    class CreateStoryUseCase:
    
        def __init__(self):
            self.repo = SQLiteRepository()

Sơ đồ:
    
    
    UseCase
        │
        ▼
    SQLiteRepository

Nếu đổi SQLite thành PostgreSQL:
    
    
    SQLiteRepository
    ↓
    
    PostgresRepository

Bạn phải sửa UseCase.

Đây là **High Coupling**.

* * *

# Dấu hiệu của High Coupling

Ví dụ:
    
    
    UI
    ↓
    
    Repository
    
    ↓
    
    HTTP
    
    ↓
    
    Parser
    
    ↓
    
    Logger
    
    ↓
    
    Redis
    
    ↓
    
    Config

Mỗi module import lẫn nhau.

Ví dụ:
    
    
    from ui.window import MainWindow

ở trong Parser.

Hoặc
    
    
    from repository import StoryRepository

ở trong UI.

Đây là dấu hiệu nguy hiểm.

* * *

# Low Coupling

Thay vào đó:
    
    
    UseCase
    
    ↓
    
    StoryRepository (Interface)
    
    ↓
    
    SQLiteRepository

UseCase chỉ biết Interface.

Không biết SQLite.

Không biết PostgreSQL.

Không biết MongoDB.

* * *

Ví dụ
    
    
    class StoryRepository(ABC):
    
        @abstractmethod
        def save(self, story):
            ...

UseCase
    
    
    class CreateStoryUseCase:
    
        def __init__(self, repo: StoryRepository):
            self.repo = repo

Không còn phụ thuộc SQLite.

Đây là **Low Coupling**.

* * *

# Ví dụ đời thực

Ổ điện.
    
    
    Laptop
    
    ↓
    
    Ổ cắm

Laptop không biết:
    
    
    Điện EVN
    
    Hay
    
    Máy phát điện
    
    Hay
    
    Pin dự phòng

Nó chỉ biết ổ cắm.

Interface chính là ổ cắm.

* * *

# Coupling trong app cào truyện

Sai:
    
    
    DownloadChapterUseCase
    
    ↓
    
    Requests
    
    ↓
    
    BeautifulSoup
    
    ↓
    
    SQLite

Nếu đổi:
    
    
    requests
    
    ↓
    
    httpx

UseCase phải sửa.

* * *

Đúng:
    
    
    DownloadChapterUseCase
    
    ↓
    
    ChapterGateway
    
    ↓
    
    RequestsAdapter

Mai đổi:
    
    
    RequestsAdapter
    
    ↓
    
    HttpxAdapter

UseCase không đổi.

* * *

# 2\. Cohesion là gì?

Cohesion =

**Một module có tập trung vào đúng một nhiệm vụ hay không.**

Ví dụ:
    
    
    Calculator

Chỉ làm toán.

→ Cohesion cao.

* * *

Nếu
    
    
    Calculator

làm:

  * cộng 
  * trừ 
  * upload FTP 
  * gửi email 
  * đọc SQLite 



→ Cohesion thấp.

* * *

Ví dụ xấu
    
    
    class StoryManager:
    
        def download_story(self):
            ...
    
        def save_database(self):
            ...
    
        def login(self):
            ...
    
        def send_email(self):
            ...
    
        def resize_image(self):
            ...
    
        def play_music(self):
            ...

Một class làm sáu việc.

Không liên quan nhau.

* * *

Đây gọi là

**God Object**

* * *

# Ví dụ tốt
    
    
    StoryDownloader
    
    StoryRepository
    
    EmailSender
    
    ImageProcessor
    
    MusicPlayer

Mỗi class đúng một nhiệm vụ.

* * *

# High Cohesion

Ví dụ
    
    
    StoryRepository

Chỉ làm
    
    
    CRUD Story

Không làm gì khác.

* * *
    
    
    Parser

Chỉ parse HTML.

Không lưu database.

Không gửi email.

Không log.

* * *
    
    
    ImageDownloader

Chỉ download ảnh.

* * *

# Low Cohesion

Ví dụ
    
    
    class Parser:
    
        def parse(self):
            ...
    
        def save_sqlite(self):
            ...
    
        def send_email(self):
            ...
    
        def cache(self):
            ...
    
        def export_pdf(self):
            ...

Đây là Low Cohesion.

* * *

# Quan hệ giữa Coupling và Cohesion

Mục tiêu:
    
    
    High Cohesion
    
    +
    
    Low Coupling

Ví dụ
    
    
    Parser
    
    ↓
    
    Interface
    
    ↓
    
    Repository

Parser chỉ parse.

Repository chỉ lưu.

Không biết nhau.

* * *

# Một ví dụ hoàn chỉnh

Giả sử app cào truyện.

Sai
    
    
    class StoryService:
    
        def crawl(self):
            ...
    
        def save(self):
            ...
    
        def login(self):
            ...
    
        def export_pdf(self):
            ...
    
        def send_email(self):
            ...
    
        def backup_database(self):
            ...
    
        def delete_story(self):
            ...

Lớn dần theo thời gian.

2000 dòng.

5000 dòng.

10000 dòng.

Rất khó sửa.

* * *

Đúng
    
    
    StoryCrawler
    
    ↓
    
    StoryParser
    
    ↓
    
    StoryRepository
    
    ↓
    
    StoryExporter
    
    ↓
    
    NotificationService
    
    ↓
    
    BackupService

Mỗi class khoảng 100–300 dòng.

* * *

# Code Refactoring

Ban đầu
    
    
    class StoryManager:
    
        def download(self):
            ...
    
        def parse(self):
            ...
    
        def save(self):
            ...

Refactor
    
    
    class Downloader:
        def download(self):
            ...
    
    
    class Parser:
        def parse(self):
            ...
    
    
    class Repository:
        def save(self):
            ...

Đây là tăng Cohesion.

* * *

# Dependency Graph

Thiết kế xấu
    
    
    A
    
    ↕︎
    
    B
    
    ↕︎
    
    C
    
    ↕︎
    
    D
    
    ↕︎
    
    A

Import vòng.

Circular Dependency.

* * *

Thiết kế tốt
    
    
    Presentation
    
    ↓
    
    Application
    
    ↓
    
    Domain

Một chiều.

* * *

# Ví dụ trong PySide6

Sai
    
    
    MainWindow
    
    ↓
    
    SQLite
    
    ↓
    
    Requests
    
    ↓
    
    Parser
    
    ↓
    
    Redis

MainWindow biết tất cả.

* * *

Đúng
    
    
    MainWindow
    
    ↓
    
    CreateStoryUseCase
    
    ↓
    
    Interface

MainWindow chỉ biết UseCase.

* * *

# Ví dụ trong Celery

Sai

Task

↓

SQLite

↓

Redis

↓

HTTP

↓

UI

* * *

Đúng

Task

↓

UseCase

↓

Repository Interface

* * *

# Ví dụ trong Plugin

Sai

Plugin

↓

SQLite

↓

PySide

↓

Redis

↓

Logger

↓

Everything

Plugin không tái sử dụng được.

* * *

Đúng

Plugin

↓

Source Interface

Plugin chỉ biết:
    
    
    class SourcePlugin:
    
        def fetch_story(self):
            ...

Thế là đủ.

* * *

# Phân tích dự án cào truyện của chúng ta

Giả sử có cấu trúc:
    
    
    plugins/
        truyenfull.py

Sai:
    
    
    class TruyenFull:
    
        def fetch(self):
            ...
    
        def save_sqlite(self):
            ...
    
        def show_messagebox(self):
            ...
    
        def update_progressbar(self):
            ...
    
        def export_epub(self):
            ...

Plugin đang:

  * Crawl 
  * Lưu DB 
  * Điều khiển UI 
  * Export EPUB 



=> Cohesion rất thấp và Coupling rất cao.

Thiết kế đúng:
    
    
    TruyenFullPlugin
            │
            ▼
    HTML
            │
            ▼
    StoryParser
            │
            ▼
    Story Entity
            │
            ▼
    SaveStoryUseCase
            │
            ▼
    StoryRepository

Plugin chỉ trả về dữ liệu đã parse. Việc lưu, hiển thị tiến trình hay xuất EPUB thuộc các tầng khác.

* * *

# Checklist tự đánh giá thiết kế

Mỗi khi viết một class, hãy tự hỏi:

  * Class này có đang làm **một nhiệm vụ chính** không? 
  * Nếu bỏ database, class này có còn hoạt động không? 
  * Nếu đổi framework UI, class này có cần sửa không? 
  * Có import quá nhiều module ở tầng khác không? 
  * Có xuất hiện `if source == ...` khắp nơi thay vì dùng đa hình (polymorphism) không? 
  * Một thay đổi nhỏ có buộc phải sửa nhiều file không? 



Nếu phần lớn câu trả lời là "có", rất có thể Coupling đang cao hoặc Cohesion đang thấp.

* * *

# Những "mùi code" thường gặp

Mùi code| Vấn đề  
---|---  
God Class| Một class làm quá nhiều việc  
Circular Import| Các module phụ thuộc lẫn nhau  
Long Method| Hàm quá dài, làm nhiều bước  
Feature Envy| Class thao tác dữ liệu của class khác nhiều hơn dữ liệu của chính nó  
Shotgun Surgery| Một thay đổi phải sửa rất nhiều file  
Divergent Change| Một class thường xuyên thay đổi vì nhiều lý do khác nhau  
  
* * *

# Tổng kết

Hai nguyên tắc quan trọng nhất hôm nay là:

  * **Low Coupling** : các module phụ thuộc vào nhau càng ít càng tốt, ưu tiên phụ thuộc vào abstraction (interface) thay vì implementation. 
  * **High Cohesion** : mỗi module, class hoặc hàm nên tập trung giải quyết một nhóm trách nhiệm liên quan chặt chẽ với nhau. 



Đây chính là nền tảng để áp dụng SOLID và Clean Architecture một cách hiệu quả.

* * *

# Bài tập

### Bài 1

Cho class sau:
    
    
    class StoryManager:
    
        def login(self):
            ...
    
        def download_story(self):
            ...
    
        def parse_story(self):
            ...
    
        def save_database(self):
            ...
    
        def export_epub(self):
            ...
    
        def send_email(self):
            ...

Hãy chia lại thành các class có **High Cohesion** , giải thích vì sao bạn tách như vậy.

* * *

### Bài 2

Thiết kế sơ đồ phụ thuộc cho ứng dụng cào truyện theo nguyên tắc:
    
    
    Presentation
        ↓
    Application
        ↓
    Domain

và xác định những thành phần nào nên nằm trong **Infrastructure**.

* * *

### Bài 3

Mở dự án cào truyện của bạn và chọn **một class** hiện có. Phân tích:

  * Class đang có bao nhiêu trách nhiệm? 
  * Coupling với những thành phần nào? 
  * Có thể tách thành những class nhỏ nào? 



Đây là bước đầu tiên để refactor dự án theo Clean Architecture.

Ở **Buổi 3** , chúng ta sẽ học **SOLID trong Clean Architecture** , không chỉ nhắc lại 5 nguyên lý mà sẽ phân tích cách từng nguyên lý tác động trực tiếp đến việc thiết kế Entity, Use Case, Repository và Plugin trong một ứng dụng Python thực tế.

