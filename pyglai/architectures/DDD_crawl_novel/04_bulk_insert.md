Để tối ưu tốc độ lưu từ vài trăm chương lên hàng vạn chương/giây trong SQLite thuần SQL, bạn cần hiểu cơ chế thắt cổ chai của nó.

Mặc định, mỗi lệnh `cursor.execute()` đi kèm một lệnh `conn.commit()` sẽ ép SQLite phải mở file DB, ghi dữ liệu xuống đĩa cứng (I/O) rồi đóng lại. Việc này cực kỳ chậm. Để giải quyết, chúng ta sử dụng kỹ thuật Bulk Insert kết hợp kiểm soát Transaction (Giao dịch) thủ công.

* * *

## 3 Nguyên Tắc Vàng Để Đạt 10,000+ Records/Giây

  1. Gom nhóm (Batching): Không lưu từng chương một. Đợi cào đủ một nhóm (ví dụ: 100 hoặc 500 chương) rồi mới bắn xuống DB một lần.
  2. Quản lý Transaction thủ công: Tắt chế độ tự động commit của Python (`isolation_level=None`). Sử dụng lệnh `BEGIN TRANSACTION` trước khi nạp batch dữ liệu và `COMMIT` duy nhất một lần sau khi nạp xong. Lúc này, toàn bộ dữ liệu được ghi vào bộ nhớ RAM trước, sau đó chỉ tốn đúng 1 lần duy nhất ghi xuống ổ đĩa.
  3. Sử dụng `executemany`: Hàm này của thư viện `sqlite3` tối ưu hóa việc tái sử dụng cấu trúc câu lệnh SQL ở tầng low-level, nhanh hơn rất nhiều so với vòng lặp `for` chạy `execute` từng dòng.



* * *

## Thực Thi Trong Hệ Thống DDD

Chúng ta sẽ cập nhật interface `ChapterRepository` để hỗ trợ lưu hàng loạt, sau đó triển khai (implement) nó bằng SQLite thuần SQL.

## 1\. Cập nhật Interface (`domain/repository.py`)

Thêm phương thức `save_bulk` vào interface.
    
    
    from abc import ABC, abstractmethod
    from typing import List
    from .model import Chapter
    
    class ChapterRepository(ABC):
        # ... các hàm cũ giữ nguyên ...
    
        @abstractmethod
        def save_bulk(self, chapters: List[Chapter]) -> None:
            """Lưu hàng loạt chương truyện sử dụng Transaction để tối ưu tốc độ"""
            pass
    

## 2\. Triển khai Bulk UPSERT Thuần SQL (`infrastructure/sqlite_repository.py`)

Đây là nơi chứa toàn bộ logic tối ưu hiệu năng.
    
    
    import sqlite3
    from typing import List
    from domain.model import Chapter
    from domain.repository import ChapterRepository
    
    class SQLiteChapterRepository(ChapterRepository):
        def __init__(self, db_path: str):
            self.db_path = db_path
    
        def _get_connection(self):
            # Tắt autocommit bằng isolation_level=None để tự kiểm soát Transaction
            conn = sqlite3.connect(self.db_path, timeout=60.0, isolation_level=None)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=OFF;") # Tối ưu tối đa tốc độ ghi (bỏ qua đợi đĩa xác nhận hoàn toàn)
            return conn
    
        def save_bulk(self, chapters: List[Chapter]) -> None:
            if not chapters:
                return
    
            conn = self._get_connection()
            cursor = conn.cursor()
    
            # Chuẩn bị dữ liệu dưới dạng list of tuples để nạp vào executemany
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
    
            sql = """
                INSERT INTO chapters (id, comic_id, number, title, content, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    content = excluded.content;
            """
    
            try:
                # 1. Bắt đầu một Transaction duy nhất cho cả Batch
                cursor.execute("BEGIN TRANSACTION;")
                
                # 2. Thực thi ghi hàng loạt cực nhanh trên RAM
                cursor.executemany(sql, data_to_insert)
                
                # 3. Ghi toàn bộ dữ liệu xuống đĩa cứng trong 1 lần I/O duy nhất
                cursor.execute("COMMIT;")
            except Exception as e:
                # Nếu có bất kỳ lỗi gì xảy ra (ví dụ: mất điện, lỗi dữ liệu), hủy bỏ toàn bộ để tránh lỗi DB
                cursor.execute("ROLLBACK;")
                raise e
            finally:
                conn.close()
    

_Lưu ý về`PRAGMA synchronous=OFF;`: Kỹ thuật này đẩy tốc độ lên mức tối đa vì SQLite không bắt hệ điều hành đợi dữ liệu ghi hẳn xuống đĩa rồi mới chạy tiếp. Nếu ứng dụng bị sập, dữ liệu của batch đó có thể mất, nhưng file DB hoàn toàn không bị hỏng (corrupt) nhờ chế độ WAL._

* * *

## 3\. Tầng Điều Phối Ứng Dụng (`application/crawler_service.py`)

Cập nhật Service để gom các chương cào được vào một `Buffer` (hàng đợi bộ nhớ tạm). Khi Buffer đủ lớn, tiến hành gọi `save_bulk`.
    
    
    from typing import List
    from domain.model import Chapter, ChapterId, ComicId
    from domain.repository import ChapterRepository
    
    class BulkCrawlerApplicationService:
        def __init__(self, chapter_repo: ChapterRepository, batch_size: int = 500):
            self.chapter_repo = chapter_repo
            self.batch_size = batch_size
            self._buffer: List[Chapter] = []
    
        def queue_crawled_chapter(self, comic_id: ComicId, chapter_num: int, title: str, content: str):
            """Đẩy chương vừa cào vào bộ nhớ đệm, tự động lưu khi đủ kích thước Batch"""
            chapter_slug = f"{comic_id.value}-chuong-{chapter_num}"
            
            # Khởi tạo Domain Entity
            chapter = Chapter(
                id=ChapterId(chapter_slug),
                comic_id=comic_id,
                number=chapter_num,
                title=title,
                content=content
            )
    
            self._buffer.append(chapter)
    
            # Nếu bộ đệm đạt ngưỡng (ví dụ: 500 chương), thực hiện ghi xuống DB
            if len(self._buffer) >= self.batch_size:
                self.flush()
    
        def flush(self):
            """Ép buộc ghi toàn bộ dữ liệu còn lại trong bộ đệm xuống DB (Dùng khi kết thúc crawl)"""
            if self._buffer:
                print(self._buffer)
                self.chapter_repo.save_bulk(self._buffer)
                self._buffer.clear() # Xóa rỗng bộ đệm sau khi lưu thành công
    

* * *

## Quy Trình Chạy Chuẩn Trong `main.py`

Khi bạn sử dụng kiến trúc này, luồng đi của dữ liệu khi crawl hàng vạn chương sẽ như sau:
    
    
    # Giả lập vòng lặp cào dữ liệu lớn
    service = BulkCrawlerApplicationService(chapter_repo=sqlite_chapter_repo, batch_size=500)
    comic_id = ComicId("doc-co-cau-bai")
    
    for i in range(1, 10001): # Giả lập cào 10,000 chương
        # Cào dữ liệu từ Web...
        title = f"Chương {i}"
        content = "Nội dung truyện..."
        
        # Chỉ đẩy vào RAM Buffer, chạy mất < 0.001 giây
        service.queue_crawled_chapter(comic_id, i, title, content)
    
    # Đảm bảo những chương cuối cùng chưa đủ 500 dòng vẫn được lưu vào DB trước khi tắt App
    service.flush() 
    

Bằng cách đưa Transaction về chế độ thủ công kết hợp `executemany` và `UPSERT`, ứng dụng Python của bạn có thể xử lý việc lưu trữ dữ liệu crawl với tốc độ tiệm cận tốc độ xử lý của RAM, không còn lo SQLite trở thành nút thắt cổ chai nữa.

Bạn có muốn tích hợp thêm cơ chế Retry (thử lại) bằng code Python kết hợp SQL để khi mạng lỗi (khiến dữ liệu cào về bị rỗng) thì hệ thống tự động cào lại chương đó mà không làm hỏng Batch dữ liệu không?