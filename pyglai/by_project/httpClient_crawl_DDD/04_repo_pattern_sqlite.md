Dưới đây là cách triển khai Repository Pattern sử dụng thư viện `sqlite3` có sẵn của Python, viết bằng SQL thuần (Raw SQL) và chạy ở cơ chế đồng bộ (Sync), bám sát cấu trúc hạ tầng độc lập của Clean Architecture và DDD.

* * *

## 1\. Kiến trúc thư mục lớp Persistence
    
    
    src/
    ├── domain/story/
    │   └── repositories.py   # Port: Interface định nghĩa các hàm lưu trữ dữ liệu
    └── infrastructure/persistence/
        └── sqlite_repository.py # Adapter: Triển khai lưu trữ xuống SQLite bằng SQL thuần
    

* * *

## 2\. Triển khai Mã nguồn

## Lớp Domain Interface (`domain/story/repositories.py`)

Domain chỉ đưa ra yêu cầu: "Tôi cần lưu một bộ truyện (`Novel`) và cần tải lại thông tin truyện từ ổ cứng". Nó không quan tâm cơ sở dữ liệu bên dưới là gì.
    
    
    from abc import ABC, abstractmethod
    from typing import Optional
    from domain.story.entities import Novel
    
    class BaseNovelRepository(ABC):
        """Port: Interface quy định các thao tác lưu trữ dữ liệu của bộ truyện."""
    
        @abstractmethod
        def save(self, novel: Novel) -> None:
            """Lưu hoặc cập nhật thông tin toàn bộ Aggregate Root (Novel + Chapters)."""
            pass
    
        @abstractmethod
        def find_by_id(self, novel_id: str) -> Optional[Novel]:
            """Tìm kiếm bộ truyện dựa trên ID."""
            pass
    

## Lớp Infrastructure Implementation (`infrastructure/persistence/sqlite_repository.py`)

Mọi chi tiết về kết nối SQLite, tạo bảng, viết các câu lệnh `INSERT`, `UPDATE`, `SELECT` thô và ánh xạ dữ liệu (Data Mapping) ngược trở lại Domain Entity đều nằm trọn vẹn ở đây.
    
    
    import sqlite3
    from typing import Optional
    from domain.story.repositories import BaseNovelRepository
    from domain.story.entities import Novel, Chapter
    from domain.story.value_objects import StoryUrl, ChapterContent
    
    class SqliteNovelRepository(BaseNovelRepository):
        """Adapter: Triển khai Repository bằng SQLite3 thuần SQL."""
    
        def __init__(self, connection: sqlite3.Connection):
            self.conn = connection
            self._create_tables()
    
        def _create_tables(self) -> None:
            """Khởi tạo cấu trúc bảng nếu chưa tồn tại (Dùng SQL thuần)."""
            with self.conn:
                # Bảng chứa thông tin bộ truyện
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS novels (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        author TEXT NOT NULL,
                        url TEXT NOT NULL
                    );
                """)
                # Bảng chứa danh sách chương, liên kết khóa ngoại với bảng novels
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS chapters (
                        id TEXT PRIMARY KEY,
                        novel_id TEXT NOT NULL,
                        number REAL NOT NULL,
                        title TEXT NOT NULL,
                        raw_html TEXT,
                        FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
                    );
                """)
    
        def save(self, novel: Novel) -> None:
            """Lưu toàn bộ Aggregate Root theo cơ chế Unit of Work thủ công (Transaction)."""
            cursor = self.conn.cursor()
            try:
                # 1. Lưu hoặc đè thông tin Novel (Upsert)
                cursor.execute("""
                    INSERT INTO novels (id, title, author, url)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        title=excluded.title,
                        author=excluded.author,
                        url=excluded.url;
                """, (novel.id, novel.title, novel.author, novel.url.value))
    
                # 2. Lưu danh sách chương trực thuộc bộ truyện
                for chapter in novel.chapters:
                    raw_html = chapter.content.raw_html if chapter.content else None
                    cursor.execute("""
                        INSERT INTO chapters (id, novel_id, number, title, raw_html)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            number=excluded.number,
                            title=excluded.title,
                            raw_html=excluded.raw_html;
                    """, (chapter.id, novel.id, chapter.number, chapter.title, raw_html))
                
                # Commit toàn bộ nếu thành công
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                print(f"[Database Error] Lỗi khi lưu dữ liệu truyện: {e}")
                raise e
    
        def find_by_id(self, novel_id: str) -> Optional[Novel]:
            """Tải dữ liệu thô từ DB lên và khởi tạo (Map) lại thành các Domain Objects."""
            cursor = self.conn.cursor()
            
            # 1. Truy vấn thông tin Novel
            cursor.execute("SELECT id, title, author, url FROM novels WHERE id = ?", (novel_id,))
            novel_row = cursor.fetchone()
            if not novel_row:
                return None
    
            # Khởi tạo lại Aggregate Root Novel từ dữ liệu thô
            novel = Novel(
                novel_id=novel_row[0],
                title=novel_row[1],
                author=novel_row[2],
                url=StoryUrl(novel_row[3])
            )
    
            # 2. Truy vấn danh sách chương thuộc về bộ truyện đó
            cursor.execute("SELECT id, number, title, raw_html FROM chapters WHERE novel_id = ?", (novel_id,))
            chapter_rows = cursor.fetchall()
    
            for ch_row in chapter_rows:
                chapter = Chapter(
                    chapter_id=ch_row[0],
                    number=ch_row[1],
                    title=ch_row[2]
                )
                # Nếu chương đã được crawl nội dung HTML, khôi phục lại trạng thái cho nó
                if ch_row[3] is not None:
                    chapter.content = ChapterContent(raw_html=ch_row[3])
                
                # Thêm chương ngược lại vào Novel thông qua hàm nghiệp vụ
                novel.add_chapter(chapter)
    
            return novel
    

* * *

## 3\. Quy trình kết hợp Chạy Thử nghiệm (`main.py`)

Kịch bản dưới đây thể hiện luồng đi hoàn chỉnh: Khởi tạo DB → Khởi tạo Domain → Lưu xuống DB → Truy vấn lại DB để kiểm tra tính toàn vẹn của dữ liệu sạch.
    
    
    import sqlite3
    from domain.story.entities import Novel, Chapter
    from domain.story.value_objects import StoryUrl
    from infrastructure.persistence.sqlite_repository import SqliteNovelRepository
    
    if __name__ == "__main__":
        # 1. Khởi tạo kết nối vật lý tới file SQLite (hoặc dùng bộ nhớ tạm :memory:)
        db_connection = sqlite3.connect("crawler_stories.db")
        
        # Kích hoạt tính năng Foreign Key Check của SQLite
        db_connection.execute("PRAGMA foreign_keys = ON;")
        
        # 2. Khởi tạo Repository Adapter
        novel_repo = SqliteNovelRepository(connection=db_connection)
    
        print("--- 1. TẠO DỮ LIỆU CRAWL & LƯU XUỐNG DATABASE ---")
        # Khởi tạo cấu trúc truyện ở tầng Domain
        my_novel = Novel(
            novel_id="novel_phong_than", 
            title="Phong Thần Diễn Nghĩa", 
            author="Hứa Trọng Lâm", 
            url=StoryUrl("https://truyen-co-dien.com")
        )
        
        # Tạo chương và cập nhật nội dung chữ thô dính mã HTML quảng cáo
        chapter_1 = Chapter(chapter_id="ch_pt_01", number=1.0, title="Chương 1: Trụ Vương tế Nữ Oa")
        chapter_1.update_content("<div><p>Trụ Vương nhìn thấy tượng Nữ Oa liền sinh lòng tà niệm...</p><p>Nguồn truyện: truyen-co-dien</p></div>")
        
        my_novel.add_chapter(chapter_1)
    
        # Đẩy xuống tầng lưu trữ thông qua Repository
        novel_repo.save(my_novel)
        print("Đã lưu bộ truyện và chương 1 vào SQLite thành công.")
    
        print("\n--- 2. TRUY VẤN LẠI TỪ DATABASE LÊN DOMAIN ---")
        # Đọc lại dữ liệu từ DB lên thành một thực thể độc lập hoàn toàn mới
        loaded_novel = novel_repo.find_by_id("novel_phong_than")
        
        if loaded_novel:
            print(f"Bộ truyện tìm thấy: {loaded_novel.title} - Tác giả: {loaded_novel.author}")
            print(f"Tổng số chương hiện có: {loaded_novel.get_total_chapters()}")
            
            for ch in loaded_novel.chapters:
                print(f"\n[{ch.title}]")
                # Domain Entity tự động dọn sạch quảng cáo khi gọi thuộc tính clean_text
                print("Nội dung sau khi phục hồi và làm sạch:")
                print(ch.content.clean_text if ch.content else "Chưa có nội dung")
                
        # Đóng kết nối database khi kết thúc ứng dụng
        db_connection.close()
    

## 💡 Điểm mấu chốt đạt chuẩn Clean & DDD:

  1. Tách biệt cơ chế map dữ liệu (Data Mapping Separation): Bạn có thể nhận thấy các thuộc tính thô nằm ở DB như `raw_html` kiểu chuỗi văn bản (String/Text), khi đưa vào lớp `SqliteNovelRepository` khôi phục lại đã biến đổi thành cấu trúc Object chuyên biệt của Domain là `ChapterContent`. Tầng DB hoàn toàn không can thiệp vào logic này.
  2. Đảm bảo tính toàn vẹn (Transaction Boundary): Toàn bộ thực thể `Novel` và danh sách `Chapter` trực thuộc đều được lưu trong cùng một khối xử lý (Transaction). Nếu một chương bị lỗi cấu trúc dữ liệu, lệnh `self.conn.rollback()` sẽ hủy bỏ toàn bộ phiên làm việc, đảm bảo không bao giờ xảy ra tình trạng truyện lưu thành công mà chương bị mất hoặc lưu sót.



Hiện tại bạn đã có đủ 3 trụ cột: HTTP Client Manager (Async), Domain Models, và Repository (Sync/Sqlite). Bạn có muốn kết hợp tất cả chúng lại thành một Application Service (Use Case) hoàn chỉnh để quản lý toàn bộ vòng lặp: Đọc danh sách link cần cào → Dispatch Task tải Async → Lưu tuần tự (Sync) vào SQLite không?