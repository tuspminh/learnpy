Áp dụng CQRS (Command Query Responsibility Segregation) vào ứng dụng crawl truyện giúp bạn tách biệt hoàn toàn hai luồng dữ liệu có tính chất trái ngược nhau:

  * Luồng Ghi (Command): Cần Transaction phức tạp, chạy qua Unit of Work (UoW) và Aggregate Root để đảm bảo tính toàn vẹn dữ liệu khi crawl.
  * Luồng Đọc (Query): Chỉ cần lấy dữ liệu lên hiển thị (API, Web, Mobile), không cần ghi, không cần Transaction, không cần Domain Model. Luồng này yêu cầu tốc độ cực nhanh và cấu trúc phẳng (DTO - Data Transfer Object).



Dưới đây là cách thiết kế luồng Đọc (Query) sử dụng lại `SQLiteContext` tối ưu hiệu năng.

* * *

## 1\. Định nghĩa DTO - Data Transfer Object (`application/dtos.py`)

Trong CQRS, luồng Đọc không trả về các Domain Entity phức tạp (như `Comic` chứa thực thể `Chapter`). Chúng ta định nghĩa các `dataclass` phẳng, nhẹ để trả thẳng ra giao diện.
    
    
    from dataclasses import dataclass
    from typing import List
    
    @dataclass(frozen=True)
    class ChapterListItemDTO:
        """DTO cho danh sách chương (hiển thị ở trang mục lục)"""
        number: int
        title: str
    
    @dataclass(frozen=True)
    class ComicDetailDTO:
        """DTO cho trang chi tiết truyện"""
        id: str
        title: str
        source_url: str
        total_chapters: int
    

* * *

## 2\. Thiết kế Lớp Truy Vấn Đọc Dữ Liệu (`application/comic_queries.py`)

Thay vì dùng `Repository`, luồng Đọc sử dụng các lớp Query (Read Service). Lớp này nhận trực tiếp `SQLiteContext` để mở kết nối Read-Only, tối ưu hóa các câu lệnh SQL (`JOIN`, `COUNT`) để lấy dữ liệu nhanh nhất có thể.
    
    
    from abc import ABC, abstractmethod
    from typing import List, Optional
    from infrastructure.context import SQLiteContext
    from .dtos import ComicDetailDTO, ChapterListItemDTO
    
    class ComicQueryService(ABC):
        @abstractmethod
        def get_comic_detail(self, comic_id: str) -> Optional[ComicDetailDTO]:
            pass
    
        @abstractmethod
        def get_chapters_v2(self, comic_id: str) -> List[ChapterListItemDTO]:
            pass
    
    # --- Triển khai cụ thể bằng SQLite thuần SQL ---
    class SQLiteComicQueryService(ComicQueryService):
        def __init__(self, db_context: SQLiteContext):
            self.db_context = db_context
    
        def get_comic_detail(self, comic_id: str) -> Optional[ComicDetailDTO]:
            # Sử dụng Context Manager của SQLiteContext để mở kết nối
            with self.db_context as conn:
                cursor = conn.cursor()
                
                # Viết SQL tối ưu, dùng COUNT gộp thay vì load toàn bộ Object lên RAM
                sql = """
                    SELECT c.id, c.title, c.source_url, COUNT(ch.id) as total_chapters
                    FROM comics c
                    LEFT JOIN chapters ch ON c.id = ch.comic_id
                    WHERE c.id = ?
                    GROUP BY c.id
                """
                cursor.execute(sql, (comic_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                    
                return ComicDetailDTO(
                    id=row[0],
                    title=row[1],
                    source_url=row[2],
                    total_chapters=row[3]
                )
    
        def get_chapters_v2(self, comic_id: str) -> List[ChapterListItemDTO]:
            with self.db_context as conn:
                cursor = conn.cursor()
                
                # Chỉ lấy 2 cột cần thiết để hiển thị mục lục, bỏ qua cột content (nặng)
                sql = "SELECT number, title FROM chapters WHERE comic_id = ? ORDER BY number ASC"
                cursor.execute(sql, (comic_id,))
                rows = cursor.fetchall()
                
                return [ChapterListItemDTO(number=row[0], title=row[1]) for row in rows]
    

* * *

## 3\. Bản đồ Kiến trúc CQRS Tổng Thể

Lúc này, ứng dụng của bạn được chia thành hai nhánh độc lập hoàn toàn, dùng chung hạ tầng `SQLiteContext`:
    
    
                               ┌───────────────────────────┐
                               │      SQLiteContext        │
                               └─────────────┬─────────────┘
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      ▼                                             ▼
           [ LUỒNG GHI - COMMAND ]                        [ LUỒNG ĐỌC - QUERY ]
      Quản lý qua Unit of Work (Transaction)            Đọc trực tiếp qua Query Service
                      │                                             │
                      ▼                                             ▼
      SQLiteUnitOfWork (BEGIN/COMMIT)                 SQLiteComicQueryService (Read Only)
                      │                                             │
                      ▼                                             ▼
        Repositories (Comic/Chapter/Job)                 Trả về DTOs phẳng, tốc độ cao
                      │                                             │
                      ▼                                             ▼
       Lưu xuống Database (WAL mode)                  Hiển thị lên API / UI người dùng
    

* * *

## 4\. Khởi chạy và Sử dụng trong Ứng dụng (`main.py`)

Hãy xem sự khác biệt rõ rệt khi gọi hai luồng này ở tầng Giao diện hoặc Controller:
    
    
    from infrastructure.context import SQLiteContext
    from infrastructure.sqlite_uow import SQLiteUnitOfWork
    from infrastructure.sqlite_config_repository import SQLiteCrawlConfigRepository
    from application.crawler_service import CrawlerApplicationService
    from application.comic_queries import SQLiteComicQueryService
    
    DB_PATH = "comics.db"
    
    def main():
        # 1. Khởi tạo một Context duy nhất cho toàn bộ hệ thống
        db_context = SQLiteContext(DB_PATH)
    
        # =========================================================================
        # NHÁNH 1: LUỒNG GHI (COMMAND) - Phục vụ cho Tiến trình Crawler chạy ngầm
        # =========================================================================
        uow = SQLiteUnitOfWork(db_context)
        crawler_service = CrawlerApplicationService(uow)
        
        # Thực thi lệnh ghi dữ liệu (Crawl truyện)
        print("--- [Command] Đang chạy crawler ghi dữ liệu... ---")
        crawler_service.crawl_and_save_chapter(
            comic_id="linh-vuc", job_id="job-99", chapter_num=10, 
            title="Chương 10: Quy Khứ", content="Nội dung chữ rất dài..."
        )
    
        # =========================================================================
        # NHÁNH 2: LUỒNG ĐỌC (QUERY) - Phục vụ cho API / UI hiển thị cho User xem
        # =========================================================================
        query_service = SQLiteComicQueryService(db_context)
        
        print("\n--- [Query] Đọc dữ liệu nhanh hiển thị lên UI... ---")
        # Lấy thông tin chi tiết truyện để hiển thị trang chủ
        comic_info = query_service.get_comic_detail("linh-vuc")
        if comic_info:
            print(f"Truyện: {comic_info.title} | Tổng số chương: {comic_info.total_chapters}")
    
        # Lấy danh sách mục lục chương
        chapters = query_service.get_chapters_v2("linh-vuc")
        for ch in chapters:
            print(f" -> [{ch.number}] {ch.title}")
    
    if __name__ == "__main__":
        main()
    

## Tại sao App Crawl truyện áp dụng CQRS lại cực kỳ mạnh mẽ?

  1. Tối ưu hóa tài nguyên SQLite: SQLite có điểm yếu là chỉ cho phép 1 tiến trình Ghi tại một thời điểm, nhưng lại cho phép nhiều tiến trình Đọc đồng thời (nhờ chế độ `WAL`). Bằng cách tách biệt luồng Đọc, người dùng vào đọc truyện trên Web sẽ không bao giờ bị nghẽn (Block) bởi tiến trình Crawler đa luồng đang ghi hàng vạn chương ở phía sau.
  2. Tốc độ truy vấn vượt trội: Luồng Đọc không đi qua tầng Domain (không tốn tài nguyên khởi tạo Object, ép kiểu dữ liệu phức tạp). Nó chạy câu lệnh SQL thô, lấy đúng những cột cần hiển thị và map thẳng vào DTO phẳng, giảm tải bộ nhớ RAM tối đa.
  3. Dễ dàng Scale độc lập: Nếu sau này lượng người đọc tăng đột biến, bạn có thể bê nguyên luồng Đọc này sang một file SQLite nhân bản (Read Replica) hoặc bổ sung bộ nhớ đệm (Redis Cache) cho `ComicQueryService` mà hoàn toàn không làm ảnh hưởng đến code của công cụ Crawler.



Hệ thống kiến trúc DDD + SOLID hoàn chỉnh cho app crawl truyện của bạn đã được thiết lập rất vững chắc từ Core Domain, Hạ tầng SQL tối ưu, cho đến cơ chế kiểm soát lỗi và phân tách luồng dữ liệu.

Để vận hành an toàn trong thực tế, bạn có cần tôi hỗ trợ thiết kế cấu trúc chặn lỗi dữ liệu lỗi (Validation / Anti-Corruption Layer) để lọc sạch các nội dung rác (quảng cáo, link ẩn độc hại) từ web nguồn trước khi đưa vào Domain Object không?