Khi ứng dụng crawl và đọc truyện/sách của bạn tăng trưởng quy mô (ví dụ: lượng dữ liệu crawl về lên tới hàng triệu slide/chương, đồng thời có hàng vạn người dùng truy cập đọc truyện cùng lúc), cấu trúc hiện tại sẽ gặp một nút thắt cổ chai lớn: Sự xung đột giữa luồng Đọc và luồng Ghi trên cùng một mô hình dữ liệu (Domain Model) và cùng một Database (SQLite).

Để giải quyết bài toán này, CQRS (Command Query Responsibility Segregation - Kiến trúc phân tách trách nhiệm Đọc và Ghi) là giải pháp tối ưu nhất.

* * *

## 🧠 Ý tưởng cốt lõi của CQRS trong ứng dụng của bạn

Thay vì bắt một Model `Book` gánh vác cả 2 nhiệm vụ: vừa phải chứa các logic nghiệp vụ phức tạp để phục vụ việc ghi (Crawl, đóng gói ảnh, kiểm tra tính toàn vẹn Aggregate), vừa phải chứa các trường phục vụ hiển thị để đọc (Tìm kiếm, hiển thị danh sách trang, thống kê), CQRS chia ứng dụng thành 2 luồng độc lập tuyệt đối:
    
    
                                 ┌────────────────────────┐
                                 │   GIAO DIỆN (CLI/API)  │
                                 └────┬──────────────┬────┘
                                      │              │
            Gửi COMMAND (Crawl/Lưu)   │              │  Gửi QUERY (Đọc/Tìm kiếm)
                                      ▼              ▼
         ┌───────────────────────────────┐        ┌───────────────────────────────┐
         │         LUỒNG GHI (WRITE)     │        │         LUỒNG ĐỌC (READ)      │
         │                               │        │                               │
         │  - Command: CrawlBookCommand  │        │  - Query: GetBookCatalogQuery │
         │  - Nghiệp vụ: Domain Model    │        │  - Logic: Không có nghiệp vụ  │
         │  - Lưu trữ: Write DB (SQLite) │        │  - Lưu trữ: Read DB           │
         │  - Giao dịch: Unit of Work    │        │    (Dữ liệu thô / Flattened)  │
         └───────────────────────────────┘        └───────────────────────────────┘
    

  1. Luồng Ghi (Commands): Chỉ tập trung vào việc thay đổi trạng thái hệ thống (Crawl, Thêm, Sửa, Xóa). Luồng này bắt buộc dùng DDD và Unit of Work để bảo vệ tính toàn vẹn dữ liệu. Dữ liệu ghi có thể chuẩn hóa cao (Normalized - nhiều bảng liên kết với nhau).
  2. Luồng Đọc (Queries): Chỉ tập trung vào việc lấy dữ liệu ra để hiển thị nhanh nhất có thể. Luồng này bỏ qua hoàn toàn Domain Model, DDD, và Unit of Work. Nó dùng SQL thuần truy vấn thẳng vào Database (thậm chí là một View hoặc một bảng đã được dàn phẳng - Flattened/Denormalized) và trả về DTO luôn.



* * *

## 📂 Cấu trúc thư mục tối ưu theo CQRS

Dự án sẽ được chia rõ rệt thành hai phân vùng `commands` và `queries` bên trong tầng `application` và `infrastructure`:
    
    
    src/
    ├── domain/                         # CHỈ PHỤC VỤ LUỒNG GHI
    │   ├── models.py                   # Book (Aggregate Root) tinh gọn, chỉ chứa logic ghi
    │   └── repositories.py
    │
    ├── application/
    │   ├── commands/                   # [MỚI] Các tác vụ thay đổi trạng thái
    │   │   ├── handler.py              # Xử lý CrawlBookCommand
    │   │   └── messages.py             # Định nghĩa cấu trúc Command (Data class)
    │   ├── queries/                    # [MỚI] Các tác vụ lấy dữ liệu (Đọc)
    │   │   ├── handler.py              # Xử lý GetBookCatalogQuery / ReadPagesQuery
    │   │   └── dto.py                  # DTO trả về trực tiếp cho UI
    │   └── unit_of_work.py             # Chỉ dùng cho luồng Ghi
    │
    ├── infrastructure/
    │   ├── write_side/                 # Triển khai lưu trữ cho luồng Ghi
    │   │   ├── sqlite_write_repo.py
    │   │   └── unit_of_work.py
    │   └── read_side/                  # [MỚI] Triển khai truy vấn tốc độ cao cho luồng Đọc
    │       └── sqlite_read_service.py  # Đọc SQL thuần, tối ưu Index, không qua Domain
    │
    └── presentation/
        └── main.py                     # Điều hướng Command/Query từ CLI
    

* * *

## 💻 Triển khai mã nguồn Minh họa CQRS

## 1\. Luồng Ghi (Command Side)

Định nghĩa Command dưới dạng một "thông điệp" chứa dữ liệu, và một Handler để xử lý. Luồng này giữ nguyên các quy tắc Clean Architecture + DDD + UoW mạnh mẽ đã làm ở các phần trước.
    
    
    # src/application/commands/messages.py
    from dataclasses import dataclass
    
    @dataclass(frozen=True)
    class CrawlBookCommand:
        """Yêu cầu hệ thống thay đổi trạng thái bằng cách crawl một cuốn sách mới"""
        url: str
        export_pdf: bool
    
    # src/application/commands/handler.py
    from src.application.commands.messages import CrawlBookCommand
    from src.application.unit_of_work import AbstractUnitOfWork
    from src.domain.repositories import SlideShareClient
    
    class CrawlBookCommandHandler:
        def __init__(self, uow: AbstractUnitOfWork, crawler: SlideShareClient, storage):
            self.uow = uow
            self.crawler = crawler
            self.storage = storage
    
        def handle(self, command: CrawlBookCommand) -> str:
            # Thực thi logic nghiệp vụ có UoW bảo vệ (như thiết kế cũ)
            with self.uow:
                book = self.crawler.fetch_book_info(command.url)
                self.uow.books.save_metadata(book)
                # ... tiến hành tải ảnh ...
                return book.book_id
    

## 2\. Luồng Đọc (Query Side) - Điểm đột phá tối ưu của CQRS

Luồng này cắt bỏ hoàn toàn các lớp trung gian. Không cần qua `Domain Model`, không cần qua `Unit of Work`, không cần `Repository`. Một `ReadService` sẽ dùng SQL thuần với các kỹ thuật tối ưu như `JOIN` hoặc đọc từ `Bảng tối ưu sẵn` để trả về kết quả ngay lập tức.
    
    
    # src/application/queries/dto.py
    from dataclasses import dataclass
    from typing import List
    
    @dataclass
    class BookCatalogView:
        """DTO tối ưu cho màn hình hiển thị danh sách sách ngoài trang chủ"""
        book_id: str
        title: str
        total_slides: int  # Trường này được tính toán sẵn trong DB để đọc cho nhanh
    
    # src/infrastructure/read_side/sqlite_read_service.py
    import sqlite3
    from typing import List
    from src.application.queries.dto import BookCatalogView
    
    class SQLiteBookReadService:
        """Dịch vụ đọc dữ liệu thô, tối ưu hóa tối đa cho tốc độ hiển thị"""
        def __init__(self, db_path: str):
            self.db_path = db_path
    
        def get_book_catalog(self) -> List[BookCatalogView]:
            # Truy vấn trực tiếp bằng SQL thuần, sử dụng hàm gộp (COUNT) hoặc đọc bảng tối ưu
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            sql = """
                SELECT b.id, b.title, COUNT(s.id) as total_slides 
                FROM downloaded_books b
                LEFT JOIN slide_images s ON b.id = s.book_id
                GROUP BY b.id;
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            conn.close()
    
            # Ánh xạ (Map) thẳng ra DTO trả về cho giao diện, cực kỳ nhanh
            return [BookCatalogView(book_id=r[0], title=r[1], total_slides=r[2]) for r in rows]
    

## 3\. Tầng Presentation: Điều phối rõ rệt giữa Đọc và Ghi
    
    
    # src/presentation/main.py
    from src.infrastructure.unit_of_work import SQLiteBookUnitOfWork
    from src.infrastructure.crawler.slideshare import SlideShareHtmlCrawler
    from src.infrastructure.storage.file_storage import FileStorage
    from src.infrastructure.read_side.sqlite_read_service import SQLiteBookReadService
    
    from src.application.commands.messages import CrawlBookCommand
    from src.application.commands.handler import CrawlBookCommandHandler
    
    if __name__ == "__main__":
        DB_PATH = "slideshare_crawler.db"
    
        # --- 1. KHI NGƯỜI DÙNG MUỐN CRAWL (Ghi dữ liệu) ---
        # Sử dụng luồng Command: Có UoW, có Nghiệp vụ bảo vệ chặt chẽ
        uow = SQLiteBookUnitOfWork(DB_PATH)
        crawler = SlideShareHtmlCrawler()
        storage = FileStorage()
        
        command_handler = CrawlBookCommandHandler(uow, crawler, storage)
        
        # Phát một Lệnh ghi
        cmd = CrawlBookCommand(url="https://slideshare.net", export_pdf=True)
        book_id = command_handler.handle(cmd)
        print(f"Đã thực thi Lệnh ghi thành công cho Book ID: {book_id}")
    
    
        # --- 2. KHI NGƯỜI DÙNG TRUY CẬP ĐỌC SÁCH / XEM DANH SÁCH (Đọc dữ liệu) ---
        # Sử dụng luồng Query: Đi đường tắt thẳng vào DB, tốc độ ánh sáng
        read_service = SQLiteBookReadService(DB_PATH)
        
        # Thực thi Lệnh đọc
        catalog = read_service.get_book_catalog()
        print("\n--- DANH SÁCH SÁCH TRONG THƯ VIỆN (QUERY SIDE) ---")
        for item in catalog:
            print(f"📖 {item.title} - Tổng số slide: {item.total_slides}")
    

* * *

## 📈 Tầm nhìn quy mô lớn: Tách biệt Database (Advanced CQRS)

Khi ứng dụng của bạn đạt đến quy mô triệu người dùng, SQLite sẽ không chịu nổi vì cơ chế khóa file khi ghi. Lúc này, nhờ cấu trúc CQRS đã chia sẵn ở trên, bạn có thể nâng cấp hệ thống lên mức tối thượng vô cùng dễ dàng:

  1. Write DB (Database Ghi): Bạn chuyển sang dùng PostgreSQL để xử lý các giao dịch (Transaction) ghi một cách mạnh mẽ, an toàn.
  2. Read DB (Database Đọc): Bạn đồng bộ dữ liệu sang một Database chuyên phục vụ tìm kiếm/đọc nhanh như Elasticsearch hoặc Redis.
  3. Cơ chế đồng bộ (Eventual Consistency): Khi luồng Ghi tạo sách thành công, ứng dụng phát ra một Domain Event (như phần trước chúng ta đã làm). Một bộ lắng nghe (Listener) sẽ bắt lấy Event này và đẩy dữ liệu được dàn phẳng sang Elasticsearch. Khi người dùng đọc truyện, họ sẽ đọc hoàn toàn từ Elasticsearch với tốc độ mili-giây, giải phóng 100% tải cho PostgreSQL.



Kiến trúc CQRS đã hoàn thiện bức tranh hệ thống chuẩn doanh nghiệp lớn cho ứng dụng của bạn. Bạn muốn tiếp tục tối ưu phần nào cho hệ thống này:

  * Tìm hiểu cách triển khai Đồng bộ dữ liệu bất đồng bộ giữa Write DB và Read DB thông qua Domain Events?
  * Hoặc bọc toàn bộ cấu trúc CQRS này vào một framework Web thực tế như FastAPI để sẵn sàng làm server cho ứng dụng di động/web đọc truyện?