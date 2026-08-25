Kỹ thuật INSERT OR UPDATE (hay còn gọi là UPSERT) là giải pháp cốt lõi để đồng bộ dữ liệu truyện. Khi bạn crawl dữ liệu về:

  * Nếu chương truyện chưa có trong DB → Hệ thống tự động INSERT.
  * Nếu chương truyện đã có (trùng khóa chính `id`) → Hệ thống tự động UPDATE nội dung mới (ví dụ: cập nhật bản dịch mới, sửa lỗi chính tả).



Trong SQLite thuần SQL, chúng ta có 2 cách triển khai kỹ thuật này.

* * *

## 2 Cách Viết INSERT OR UPDATE Thuần SQL Trong SQLite

## Cách 1: Sử dụng cấu trúc `ON CONFLICT` (Chuẩn SEO & Tối ưu nhất)

Đây là cú pháp chuẩn của SQLite (từ bản 3.24+). Nó cho phép bạn chỉ định chính xác cột nào sẽ bị ghi đè, cột nào sẽ được giữ nguyên (ví dụ: giữ nguyên ngày tạo `created_at` nhưng cập nhật nội dung truyện `content`).
    
    
    INSERT INTO chapters (id, comic_id, number, title, content, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        title = excluded.title,
        content = excluded.content;
    

  * `ON CONFLICT(id)`: Phát hiện trùng lặp dựa trên khóa chính `id` (ví dụ: `linh-vuc-chuong-1`).
  * Từ khóa `excluded`: Đại diện cho dữ liệu _mới_ mà bạn vừa crawl về định chèn vào.
  * Ưu điểm: Cột `created_at` không nằm trong danh sách `SET` nên sẽ giữ nguyên thời gian lần đầu tiên crawl, không bị cập nhật lại.



## Cách 2: Sử dụng cú pháp `INSERT OR REPLACE` (Mạnh bạo)

Cú pháp này ngắn gọn hơn nhưng cơ chế hoạt động có phần "thô bạo" hơn.
    
    
    INSERT OR REPLACE INTO chapters (id, comic_id, number, title, content, created_at)
    VALUES (?, ?, ?, ?, ?, ?);
    

  * Cơ chế: Nếu trùng `id`, SQLite sẽ XÓA hẳn dòng cũ (DELETE) và CHÈN một dòng hoàn toàn mới (INSERT).
  * Nhược điểm lớn: Vì nó xóa dòng cũ đi rồi chèn mới nên tất cả dữ liệu lịch sử của dòng đó (như ngày tạo `created_at`, số lượt đọc, trạng thái đã tải...) sẽ bị mất sạch và thay hoàn toàn bằng dữ liệu mới truyền vào.



* * *

## Triển Khai Vào Mã Nguồn Python (Theo Chuẩn DDD)

Dưới đây là cách hiện thực hóa kỹ thuật `ON CONFLICT` vào tầng `Infrastructure` của bạn, kết hợp tối ưu hóa Transaction để đảm bảo tốc độ lưu cao.
    
    
    import sqlite3
    from domain.model import Chapter
    from domain.repository import ChapterRepository
    
    class SQLiteChapterRepository(ChapterRepository):
        def __init__(self, db_path: str):
            self.db_path = db_path
    
        def _get_connection(self):
            """Khởi tạo kết nối tối ưu cho app crawl đa luồng"""
            conn = sqlite3.connect(self.db_path, timeout=30.0, isolation_level=None)
            conn.execute("PRAGMA journal_mode=WAL;")  # Bật chế độ ghi log ghi đồng thời
            conn.execute("PRAGMA synchronous=NORMAL;") 
            return conn
    
        def save_or_update(self, chapter: Chapter) -> None:
            """Thực thi INSERT OR UPDATE cho một chương đơn lẻ"""
            conn = self._get_connection()
            cursor = conn.cursor()
            
            sql = """
                INSERT INTO chapters (id, comic_id, number, title, content, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    content = excluded.content
            """
            
            try:
                cursor.execute("BEGIN TRANSACTION;")
                cursor.execute(sql, (
                    chapter.id.value,       # Khóa chính dùng để kiểm tra trùng lặp
                    chapter.comic_id.value, 
                    chapter.number, 
                    chapter.title, 
                    chapter.content,        # Nếu nội dung chữ thay đổi, DB sẽ ghi đè nội dung mới
                    chapter.created_at.isoformat() # Nếu trùng, cột này KHÔNG bị ghi đè (giữ nguyên ngày tạo gốc)
                ))
                cursor.execute("COMMIT;")
            except Exception as e:
                cursor.execute("ROLLBACK;")
                raise e
            finally:
                conn.close()
    

* * *

## Tại Sao App Crawl Truyện Bắt Buộc Phải Dùng Kỹ Thuật Này?

  1. Tránh Lỗi Trùng Khóa Chính (`Unique Constraint`): Khi bạn crawl đa luồng, việc 2 luồng cùng cào trúng một chương hoặc bạn chạy lại một script crawl cũ là rất phổ biến. Nếu chỉ dùng lệnh `INSERT` thông thường, ứng dụng sẽ bị sập ngay lập tức do lỗi trùng ID.
  2. Tiết Kiệm Truy Vấn (I/O): Nếu không dùng `UPSERT`, code của bạn sẽ phải `SELECT` lên kiểm tra trước → `if` tồn tại thì gọi `UPDATE`, `else` thì gọi `INSERT`. Việc này tốn 2 truy vấn cho mỗi chương truyện. `UPSERT` rút gọn xuống chỉ còn 1 truy vấn duy nhất xử lý trực tiếp ở tầng database.
  3. Cập Nhật Dữ Liệu Thông Minh: Các nguồn truyện thường xuyên sửa lỗi chính tả, đổi tiêu đề hoặc bổ sung nội dung bị thiếu sau vài ngày. Kỹ thuật này giúp app của bạn luôn có nội dung mới nhất mà không làm xáo trộn cấu trúc DB.



Bạn có muốn tích hợp thêm tính năng theo dõi lịch sử thay đổi (Audit Log) để mỗi khi một chương truyện được `UPDATE` nội dung mới, hệ thống sẽ lưu lại bản dịch cũ phòng trường hợp nguồn truyện bị lỗi không?