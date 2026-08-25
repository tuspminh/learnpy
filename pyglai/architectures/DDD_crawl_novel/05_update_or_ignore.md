Trong SQLite thuần SQL, thuật ngữ chính xác là `INSERT OR IGNORE`. Tuy nhiên, khi kết hợp với logic crawl truyện, kỹ thuật này thường được áp dụng theo hai hướng: Bỏ qua nếu đã tồn tại (Ignore) hoặc Chỉ cập nhật một phần dữ liệu cụ thể.

Dưới đây là chi tiết về cách hoạt động và cách áp dụng hai kỹ thuật này vào ứng dụng crawl truyện của bạn.

* * *

## 1\. Kỹ thuật `INSERT OR IGNORE` (Thuần SQL)

Đây là cú pháp đặc trưng của SQLite. Cơ chế của nó là: Nếu trùng Khóa chính (Primary Key) hoặc Khóa duy nhất (Unique), SQLite sẽ im lặng bỏ qua (Ignore) dòng đó và chạy tiếp, không báo lỗi, không ghi đè dữ liệu cũ.

## Cú pháp SQL:
    
    
    INSERT OR IGNORE INTO chapters (id, comic_id, number, title, content, created_at)
    VALUES (?, ?, ?, ?, ?, ?);
    

## Ứng dụng tối ưu cho App Crawl:

Kỹ thuật này cực kỳ hữu ích khi bạn muốn tiết kiệm băng thông và tài nguyên hệ thống.

  * Kịch bản: Bạn crawl lại một bộ truyện có 1000 chương để check xem có chương mới không.
  * Cách xử lý: Luồng crawler chỉ cần lấy danh sách ID chương từ web, bắn thẳng lệnh `INSERT OR IGNORE` xuống DB. 950 chương cũ đã có trong DB sẽ bị SQLite bỏ qua ngay lập tức, chỉ có 50 chương mới là thực sự được chèn vào. Bạn không mất công chạy lệnh `SELECT` để kiểm tra trước.



* * *

## 2\. Kỹ thuật "Update if exists, Else Ignore" (Cập nhật có điều kiện)

Đôi khi, bạn gặp bài toán ngược lại: Nếu chương truyện ĐÃ CÓ trong DB thì tôi mới cập nhật thông tin mới (ví dụ: số lượt xem, trạng thái sửa lỗi), còn nếu chương đó CHƯA CÓ thì tôi KHÔNG THÊM MỚI (Ignore) vì có thể chương đó thuộc về một phân đoạn chưa được cào.

Để làm được việc này bằng thuần SQL, chúng ta sử dụng mệnh đề `UPDATE ... WHERE EXISTS`.

## Cú pháp SQL:
    
    
    UPDATE chapters 
    SET content = ?, title = ?
    WHERE id = ? 
      AND EXISTS (SELECT 1 FROM chapters WHERE id = ?);
    

_(Hoặc trong SQLite, bản thân câu lệnh`UPDATE` mặc định đã tự bỏ qua nếu không tìm thấy `id`, nên bạn chỉ cần viết `UPDATE chapters SET ... WHERE id = ?`. Nếu `id` không tồn tại, số dòng ảnh hưởng sẽ là 0 và không có lỗi nào xảy ra)._

* * *

## Áp dụng vào Kiến trúc DDD & Đa luồng Python

Hãy cập nhật file `infrastructure/sqlite_repository.py` để bổ sung hàm `save_only_new` (áp dụng `INSERT OR IGNORE` cho Bulk Insert) giúp tăng tốc độ quét truyện cũ.
    
    
    import sqlite3
    from typing import List
    from domain.model import Chapter
    
    class SQLiteChapterRepository:
        def __init__(self, db_path: str):
            self.db_path = db_path
    
        def _get_connection(self):
            conn = sqlite3.connect(self.db_path, timeout=30.0, isolation_level=None)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=OFF;")
            return conn
    
        def save_new_only_bulk(self, chapters: List[Chapter]) -> int:
            """
            Chỉ lưu những chương chưa từng tồn tại. 
            Nếu chương đã có trong DB -> Bỏ qua (Ignore), giữ nguyên dữ liệu cũ.
            Trả về số lượng chương thực sự được thêm mới.
            """
            if not chapters:
                return 0
    
            conn = self._get_connection()
            cursor = conn.cursor()
    
            data_to_insert = [
                (ch.id.value, ch.comic_id.value, ch.number, ch.title, ch.content, ch.created_at.isoformat())
                for ch in chapters
            ]
    
            # Thuần SQL: Sử dụng INSERT OR IGNORE
            sql = """
                INSERT OR IGNORE INTO chapters (id, comic_id, number, title, content, created_at)
                VALUES (?, ?, ?, ?, ?, ?);
            """
    
            try:
                cursor.execute("BEGIN TRANSACTION;")
                cursor.executemany(sql, data_to_insert)
                cursor.execute("COMMIT;")
                
                # Lấy số lượng dòng thực sự được thay đổi/thêm mới trong kết nối này
                cursor.execute("SELECT changes();")
                inserted_count = cursor.fetchone()[0]
                return inserted_count
                
            except Exception as e:
                cursor.execute("ROLLBACK;")
                raise e
            finally:
                conn.close()
    

* * *

## So sánh toàn diện: Khi nào dùng kỹ thuật nào?

Tiêu chí| `UPSERT (ON CONFLICT DO UPDATE)`| `INSERT OR IGNORE`  
---|---|---  
Hành vi khi trùng ID| Cập nhật các cột được chỉ định thành dữ liệu mới.| Bỏ qua hoàn toàn, giữ nguyên 100% dữ liệu cũ.  
Tốc độ ghi| Thao tác ghi đè tốn thêm tài nguyên ghi đĩa.| Cực nhanh vì SQLite chỉ check index, thấy trùng là bỏ qua ngay.  
Trường hợp áp dụng tốt nhất| Khi cần crawl cập nhật nội dung (sửa lỗi chính tả, đổi tiêu đề chương).| Khi quét lại truyện cũ (Re-crawl) để tìm chương mới mà không muốn ghi đè dữ liệu cũ.  
Ảnh hưởng `created_at`| Giữ nguyên được (nếu cấu hình loại trừ trong SQL).| Giữ nguyên 100%.  
  
Bằng cách kết hợp linh hoạt cả `UPSERT` và `INSERT OR IGNORE`, bạn có thể tối ưu hóa ứng dụng crawler của mình: Dùng `INSERT OR IGNORE` để bỏ qua nhanh các chương cũ khi quét diện rộng, và dùng `UPSERT` khi người dùng yêu cầu "Cào lại và sửa lỗi chương này".

Bạn có muốn thiết kế thêm tầng Domain Event để khi một chương mới được thêm vào (không bị Ignore), hệ thống sẽ tự động bắn thông báo (Webhook/Telegram) về máy của bạn không?