# Clean Architecture Deep Dive

# Buổi 3: SOLID trong Clean Architecture

Ở buổi trước chúng ta đã học:

  * High Cohesion 
  * Low Coupling 



Hôm nay chúng ta sẽ học thứ gần như là **DNA của Clean Architecture**.

Nếu Coupling và Cohesion trả lời câu hỏi:

> "Kiến trúc tốt trông như thế nào?"

thì SOLID trả lời:

> "Làm sao để viết code tạo nên kiến trúc đó?"

* * *

# Mục tiêu buổi học

Sau buổi này bạn sẽ hiểu:

  * Vì sao SOLID sinh ra 
  * Vai trò của từng nguyên lý trong Clean Architecture 
  * Áp dụng SOLID vào app cào truyện 
  * Nhận biết các lỗi vi phạm SOLID 
  * Refactor từ code "xấu" sang code "sạch" 



* * *

# SOLID là gì?

SOLID gồm 5 nguyên lý:
    
    
    S — Single Responsibility Principle
    
    O — Open Closed Principle
    
    L — Liskov Substitution Principle
    
    I — Interface Segregation Principle
    
    D — Dependency Inversion Principle

Điều thú vị là:

> **Clean Architecture gần như được xây dựng trên SOLID.**

Nếu vi phạm SOLID thì rất khó xây dựng Clean Architecture đúng.

* * *

# S — Single Responsibility Principle (SRP)

Một class chỉ nên có **một lý do để thay đổi**.

Lưu ý:

Không phải là:

> Một method.

Không phải:

> Một chức năng.

Mà là:

> Một **trách nhiệm nghiệp vụ**.

* * *

## Ví dụ sai
    
    
    class StoryService:
    
        def download(self):
            ...
    
        def parse(self):
            ...
    
        def save_database(self):
            ...
    
        def export_epub(self):
            ...
    
        def send_email(self):
            ...

Class này có tới nhiều lý do thay đổi:

  * Website đổi HTML 
  * Database đổi 
  * EPUB đổi 
  * Email đổi 



Mỗi lần sửa một nơi đều phải mở class này.

* * *

## Refactor
    
    
    StoryDownloader
    
    ↓
    
    StoryParser
    
    ↓
    
    StoryRepository
    
    ↓
    
    EpubExporter
    
    ↓
    
    EmailService

Mỗi class một nhiệm vụ.

Đây là SRP.

* * *

## Trong app cào truyện

Plugin chỉ nên:
    
    
    Tải HTML

Parser chỉ nên:
    
    
    Parse HTML

Repository chỉ nên:
    
    
    Lưu dữ liệu

UseCase chỉ nên:
    
    
    Điều phối nghiệp vụ

* * *

# O — Open Closed Principle (OCP)

Nguyên lý:

> **Mở để mở rộng, đóng để sửa đổi.**

Nghe hơi khó.

Ví dụ.

Giả sử app hiện hỗ trợ:
    
    
    TruyenFull

Mai thêm:
    
    
    TangThuVien

Sai:
    
    
    if source == "truyenfull":
        ...
    
    elif source == "tangthuvien":
        ...
    
    elif source == "metruyen":
        ...

Mỗi lần thêm nguồn phải sửa file cũ.

Vi phạm OCP.

* * *

## Thiết kế đúng
    
    
    class BaseSource:
    
        def fetch_story(self, url):
            raise NotImplementedError

Plugin:
    
    
    class TruyenFullSource(BaseSource):
    
        def fetch_story(self, url):
            ...

Plugin khác:
    
    
    class TangThuVienSource(BaseSource):
    
        def fetch_story(self, url):
            ...

Muốn thêm website?

Tạo file mới.

Không sửa code cũ.

Đây là OCP.

* * *

# L — Liskov Substitution Principle (LSP)

Đây là nguyên lý bị hiểu sai nhiều nhất.

Định nghĩa:

> Class con phải thay thế được class cha.

* * *

## Ví dụ
    
    
    class StoryRepository:
    
        def save(self, story):
            ...

SQLite:
    
    
    class SQLiteRepository(StoryRepository):
    
        def save(self, story):
            ...

Postgres:
    
    
    class PostgreSQLRepository(StoryRepository):
    
        def save(self, story):
            ...

UseCase:
    
    
    repo.save(story)

Không cần biết repo nào.

Đây là LSP.

* * *

## Ví dụ vi phạm
    
    
    class Repository:
    
        def save(self, story):
            ...

SQLite:
    
    
    class SQLiteRepository(Repository):
    
        def save(self, story):
            raise Exception("Không hỗ trợ")

Hoặc:
    
    
    class SQLiteRepository(Repository):
    
        def save(self, story):
            return None

Trong khi Repository gốc cam kết luôn lưu thành công hoặc báo lỗi theo một quy ước khác.

Khi đó UseCase không thể thay thế Repository bằng SQLiteRepository một cách an toàn.

* * *

# I — Interface Segregation Principle (ISP)

Đừng bắt người dùng implement thứ họ không cần.

* * *

Ví dụ interface khổng lồ:
    
    
    class Repository:
    
        def save(self):
            ...
    
        def delete(self):
            ...
    
        def export_pdf(self):
            ...
    
        def send_email(self):
            ...
    
        def upload_s3(self):
            ...

Plugin phải implement tất cả.

Rất vô lý.

* * *

## Refactor
    
    
    class StoryReader:
    
        def get(self):
            ...
    
    
    class StoryWriter:
    
        def save(self):
            ...
    
    
    class StorySearcher:
    
        def search(self):
            ...

Interface nhỏ.

Dễ dùng.

Đó là ISP.

* * *

# D — Dependency Inversion Principle (DIP)

Đây là nguyên lý quan trọng nhất.

Định nghĩa:

> Module cấp cao không phụ thuộc module cấp thấp.

Cả hai cùng phụ thuộc abstraction.

* * *

## Sai
    
    
    UseCase
    
    ↓
    
    SQLiteRepository

UseCase biết SQLite.

* * *

## Đúng
    
    
    UseCase
    
    ↓
    
    StoryRepository (Interface)
    
    ↓
    
    SQLiteRepository

SQLite phụ thuộc Interface.

UseCase cũng phụ thuộc Interface.

Đó là DIP.

* * *

## Python
    
    
    class StoryRepository(ABC):
    
        @abstractmethod
        def save(self, story):
            ...

UseCase
    
    
    class SaveStoryUseCase:
    
        def __init__(self, repo: StoryRepository):
            self.repo = repo

SQLite
    
    
    class SQLiteRepository(StoryRepository):
    
        def save(self, story):
            print("Saved")

* * *

# SOLID trong Clean Architecture
    
    
    Presentation
    
    ↓
    
    UseCase
    
    ↓
    
    Repository Interface
    
    ↓
    
    Repository

SRP

↓

Mỗi tầng làm một việc.

* * *

OCP

↓

Thêm plugin mới.

Không sửa UseCase.

* * *

LSP

↓

SQLite

↓

Postgres

↓

Mongo

Có thể thay thế nhau.

* * *

ISP

↓

Repository nhỏ.

Không có interface khổng lồ.

* * *

DIP

↓

UseCase chỉ biết Interface.

* * *

# Ví dụ hoàn chỉnh

Sai:
    
    
    class StoryService:
    
        def crawl(self):
            ...
    
        def save(self):
            ...
    
        def parse(self):
            ...
    
        def login(self):
            ...
    
        def email(self):
            ...
    
        def export(self):
            ...

Vi phạm:

  * SRP 
  * DIP 
  * ISP 



* * *

Refactor
    
    
    StoryCrawler
    
    ↓
    
    StoryParser
    
    ↓
    
    StoryRepository
    
    ↓
    
    NotificationService
    
    ↓
    
    Exporter

UseCase

↓

Repository Interface

↓

SQLiteRepository

Tuân thủ đầy đủ SOLID.

* * *

# Áp dụng vào dự án cào truyện

Một cấu trúc phù hợp sẽ là:
    
    
    domain/
        entities/
        repositories/
        services/
    
    application/
        use_cases/
        dto/
    
    infrastructure/
        database/
        http/
        plugins/
    
    presentation/
        pyside/

Trong đó:

  * `Story`, `Chapter`, `Author` là Entity (SRP). 
  * `StoryRepository` là abstraction để áp dụng DIP. 
  * Mỗi website (`TruyenFullSource`, `TangThuVienSource`, ...) là một plugin mới, không sửa plugin cũ (OCP). 
  * Mọi `StoryRepository` đều có thể thay thế nhau mà UseCase không cần đổi (LSP). 
  * Interface được chia nhỏ theo nhu cầu (`StoryReader`, `StoryWriter`, `StorySearcher`) thay vì một interface khổng lồ (ISP). 



* * *

# Những hiểu lầm phổ biến

### Hiểu lầm 1

> "Mỗi class chỉ được có một method."

Sai.

Một Repository có thể có:
    
    
    save()
    update()
    delete()
    get_by_id()
    list()

Đó vẫn là **một trách nhiệm** : quản lý lưu trữ Story.

* * *

### Hiểu lầm 2

> "Dùng ABC là đã có SOLID."

Sai.

ABC chỉ là công cụ.

Nếu interface quá lớn hoặc thiết kế sai, bạn vẫn vi phạm ISP và DIP.

* * *

### Hiểu lầm 3

> "SOLID chỉ dành cho OOP."

Sai.

Ngay cả khi viết Python theo phong cách module hoặc functional, tư duy về trách nhiệm, phụ thuộc và khả năng mở rộng vẫn rất hữu ích.

* * *

# Checklist khi review code

Mỗi class hãy tự hỏi:

  1. Có hơn một lý do để thay đổi không? (SRP) 
  2. Muốn thêm tính năng mới có phải sửa class cũ không? (OCP) 
  3. Có thể thay implementation khác mà không làm hỏng UseCase không? (LSP) 
  4. Interface có đang ép người dùng implement những method không cần thiết không? (ISP) 
  5. Class có đang phụ thuộc trực tiếp vào SQLite, Redis, Requests... thay vì abstraction không? (DIP) 



Nếu câu trả lời cho các câu hỏi trên đều tích cực, bạn đang đi đúng hướng với Clean Architecture.

* * *

# Bài tập

## Bài 1

Cho đoạn code:
    
    
    class StoryService:
    
        def download(self):
            ...
    
        def parse(self):
            ...
    
        def save(self):
            ...
    
        def export_pdf(self):
            ...
    
        def send_email(self):
            ...

Hãy:

  * Chỉ ra nguyên lý SOLID nào đang bị vi phạm. 
  * Tách thành các class phù hợp. 



* * *

## Bài 2

Thiết kế một `StoryRepository` abstraction và viết hai implementation:

  * `SQLiteStoryRepository`
  * `MemoryStoryRepository`



Đảm bảo `SaveStoryUseCase` có thể hoạt động với cả hai mà không cần thay đổi mã nguồn.

* * *

## Bài 3

Trong dự án cào truyện của bạn, chọn một plugin hiện có và kiểm tra:

  * Plugin có đang vừa tải HTML, vừa parse, vừa lưu database không? 
  * Có đang import trực tiếp PySide6 hoặc SQLite không? 
  * Nếu có, hãy đề xuất cách tách theo SRP và DIP. 



* * *

Ở **Buổi 4** , chúng ta sẽ học **Dependency Rule** — nguyên tắc cốt lõi của Clean Architecture. Bạn sẽ hiểu vì sao các mũi tên phụ thuộc **chỉ được hướng vào trong** , cách tổ chức import giữa các package Python, và cách tránh `circular import` trong những dự án lớn. Đây là phần kết nối toàn bộ kiến thức về SOLID với kiến trúc thực tế.

