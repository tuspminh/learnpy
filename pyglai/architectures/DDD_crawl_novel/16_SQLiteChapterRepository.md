Dưới đây là mã nguồn hiện thực hoàn chỉnh cho `SQLiteChapterRepository` thuộc tầng _Infrastructure_.

Lớp này được thiết kế theo đúng tư duy tinh gọn mới: Không tự đóng/mở kết nối, không tự quản lý Transaction, mà nhận vào một `connection` dùng chung do `Unit of Work` cấp phát. Lớp này chứa đầy đủ các kỹ thuật tối ưu SQL nâng cao đã thảo luận bao gồm: `UPSERT (ON CONFLICT)`, `INSERT OR IGNORE`, và `Bulk Insert (executemany)`.

* * *

## Cập nhật Interface của Domain (`domain/repository.py`)

Trước khi viết code hạ tầng, ta cần định nghĩa các hành vi nghiệp vụ rõ ràng tại tầng Domain.
    
    
    from abc import ABC, abstractmethod
    from typing import Optional, List
    from .model import Chapter, ChapterId, ComicId
    
    class ChapterRepository(ABC):
        @abstractmethod
        def save_or_update(self, chapter: Chapter) -> None:
            """Lưu hoặc cập nhật nội dung chương (UPSERT)"""
            pass
    
        @abstractmethod
        def save_new_only_bulk(self, chapters: List[Chapter]) -> int:
            """Lưu hàng loạt chương chưa tồn tại, bỏ qua chương trùng (Bulk + IGNORE)"""
            pass
    
        @abstractmethod
        def get_by_id(self, chapter_id: ChapterId) -> Optional[Chapter]:
            """Lấy thông tin một chương theo ID"""
            pass
    
        @abstractmethod
        def list_by_comic(self, comic_id: ComicId) -> List[Chapter]:
            """Lấy danh sách toàn bộ chương của một bộ truyện (Dùng cho Domain Logic)"""
            pass
    

* * *

## Hiện thực lớp Hạ tầng (`infrastructure/sqlite_repository.py`)

Lớp này hiện thực interface trên bằng câu lệnh SQLite thuần SQL.
    
    
    import sqlite3
    from typing import Optional, List
    from datetime import datetime
    from domain.model import Chapter, ChapterId, ComicId
    from domain.repository import ChapterRepository
    
    class SQLiteChapterRepository(ChapterRepository):
        def __init__(self, connection: sqlite3.Connection):
            """
            Nhận kết nối duy nhất từ Unit of Work.
            Không tự conn.commit() hay conn.close() tại đây để đảm bảo nguyên lý SOLID.
            """
            self.connection = connection
    
        def save_or_update(self, chapter: Chapter) -> None:
            """Kỹ thuật 1: UPSERT (INSERT OR UPDATE) có chọn lọc cột"""
            cursor = self.connection.cursor()
            
            # Chỉ cập nhật tiêu đề và nội dung chữ, GIỮ NGUYÊN ngày tạo gốc (created_at)
            sql = """
                INSERT INTO chapters (id, comic_id, number, title, content, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    content = excluded.content;
            """
            
            cursor.execute(sql, (
                chapter.id.value,
                chapter.comic_id.value,
                chapter.number,
                chapter.title,
                chapter.content,
                chapter.created_at.isoformat()
            ))
    
        def save_new_only_bulk(self, chapters: List[Chapter]) -> int:
            """Kỹ thuật 2: Bulk INSERT kết hợp với hành vi IGNORE"""
            if not chapters:
                return 0
    
            cursor = self.connection.cursor()
            
            # Chuyển đổi danh sách Domain Entities thành list of tuples cho executemany trên RAM
            data_to_insert = [
                (
                    ch.id.value,
                    ch.comic_id.value,
                    ch.number,
                    ch.title,
                    ch.content,
                    ch.created_at.isoformat()
                )
                for ch in chapters
            ]
    
            # Thuần SQL: Nếu trùng ID, im lặng bỏ qua để đạt tốc độ tối đa khi quét diện rộng
            sql = """
                INSERT OR IGNORE INTO chapters (id, comic_id, number, title, content, created_at)
                VALUES (?, ?, ?, ?, ?, ?);
            """
            
            cursor.executemany(sql, data_to_insert)
            
            # Trả về số lượng chương thực sự được thêm mới (không bị trùng)
            return cursor.rowcount
    
        def get_by_id(self, chapter_id: ChapterId) -> Optional[Chapter]:
            """Kỹ thuật 3: SELECT và Map ngược lại thành Domain Object"""
            cursor = self.connection.cursor()
            
            sql = """
                SELECT id, comic_id, number, title, content, created_at 
                FROM chapters 
                WHERE id = ?
            """
            cursor.execute(sql, (chapter_id.value,))
            row = cursor.fetchone()
            
            if not row:
                return None
                
            # Tái cấu trúc (Map) dữ liệu thô từ DB thành Domain Entity
            return Chapter(
                id=ChapterId(row[0]),
                comic_id=ComicId(row[1]),
                number=row[2],
                title=row[3],
                content=row[4],
                created_at=datetime.fromisoformat(row[5])
            )
    
        def list_by_comic(self, comic_id: ComicId) -> List[Chapter]:
            """Kỹ thuật 4: Tải danh sách chương theo thứ tự tăng dần"""
            cursor = self.connection.cursor()
            
            sql = """
                SELECT id, comic_id, number, title, content, created_at 
                FROM chapters 
                WHERE comic_id = ? 
                ORDER BY number ASC
            """
            cursor.execute(sql, (comic_id.value,))
            rows = cursor.fetchall()
            
            return [
                Chapter(
                    id=ChapterId(row[0]),
                    comic_id=ComicId(row[1]),
                    number=row[2],
                    title=row[3],
                    content=row[4],
                    created_at=datetime.fromisoformat(row[5])
                )
                for row in rows
            ]
    

* * *

## Điểm tối ưu vượt trội của Repository này:

  1. Tinh gọn tuyệt đối (SRP): Hàm `save_new_only_bulk` không hề chứa các đoạn mã `BEGIN` hay `COMMIT TRANSACTION` nặng nề. Nhiệm vụ của nó chỉ là chuẩn bị dữ liệu và bắn lệnh `executemany`. Sự an toàn của Transaction được bao bọc hoàn toàn bởi lớp `SQLiteUnitOfWork` ở bên ngoài.
  2. Kiểm soát dòng bị ảnh hưởng (`cursor.rowcount`): Giúp tầng ứng dụng biết chính xác có bao nhiêu chương thực sự được thêm mới, từ đó ra quyết định có bắn Domain Event gửi Telegram hay không (nếu `rowcount = 0` tức là chương cũ bị trùng, hệ thống sẽ tự động im lặng, không gửi spam thông báo).
  3. Phân tách luồng đọc ghi rõ ràng (CQRS): Hàm `list_by_comic` ở đây chỉ dùng khi Domain cần kiểm tra logic nghiệp vụ nội bộ (ví dụ: kiểm tra xem truyện có bị nhảy chương, mất chương hay không). Đối với việc đọc truyện hiển thị ra cho User xem ở trang Web, hệ thống sẽ gọi qua dịch vụ `ComicQueryService` riêng biệt để đạt hiệu năng tối đa.



Để chạy thử nghiệm module này một cách trơn tru, bạn có muốn tôi viết tiếp file hiện thực cho `SQLiteComicRepository` (dùng để lưu thông tin gốc của bộ truyện) và cấu trúc mẫu của file `models.py` không?