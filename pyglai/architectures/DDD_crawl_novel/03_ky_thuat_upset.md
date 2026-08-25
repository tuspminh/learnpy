UPSERT là một kỹ thuật trong SQL kết hợp giữa UPdate (Cập nhật) và inSERT (Thêm mới). Khi bạn ghi dữ liệu vào bảng:

  * Nếu dòng dữ liệu chưa tồn tại (không trùng khóa chính/khóa duy nhất) → Hệ thống sẽ thực hiện lệnh INSERT.
  * Nếu dòng dữ liệu đã tồn tại (trùng khóa chính/khóa duy nhất) → Hệ thống sẽ tự động chuyển thành lệnh UPDATE trên dòng đó.



Trong ứng dụng crawl truyện, kỹ thuật này cực kỳ quan trọng để chống trùng lặp dữ liệu khi bạn cào đi cào lại một bộ truyện, hoặc khi nhiều luồng (threads) ghi đè lên nhau.

* * *

## 2 cách viết UPSERT thuần SQL trong SQLite

SQLite hỗ trợ hai cú pháp chính để xử lý UPSERT tùy thuộc vào phiên bản và nhu cầu bài toán của bạn.

## Cách 1: Sử dụng mệnh đề `ON CONFLICT` (Khuyến khích - Chuẩn từ SQLite 3.24+)

Đây là cú pháp chuẩn SEO/tối ưu nhất, giúp bạn kiểm soát chi tiết cột nào sẽ bị ghi đè, cột nào sẽ được giữ nguyên (ví dụ: giữ nguyên ngày tạo `created_at` nhưng cập nhật nội dung truyện mới `content`).
    
    
    INSERT INTO chapters (id, comic_id, number, title, content, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        title = excluded.title,
        content = excluded.content;
    

  * `ON CONFLICT(id)`: Báo cho SQLite biết nếu xảy ra xung đột (trùng) tại cột khóa chính `id`.
  * `DO UPDATE SET`: Chỉ thị hành động sẽ cập nhật lại dữ liệu cũ thay vì báo lỗi.
  * Từ khóa `excluded`: Đại diện cho dữ liệu _mới_ mà bạn định chèn vào nhưng bị trùng. `content = excluded.content` nghĩa là: Lấy nội dung mới cào được ghi đè vào nội dung cũ trong DB.
  * Lợi ích: Cột `created_at` không được liệt kê trong `DO UPDATE SET` sẽ giữ nguyên thời gian lần đầu tiên crawl, không bị cập nhật lại.



## Cách 2: Sử dụng cú pháp rút gọn `INSERT OR REPLACE`

Cú pháp này ngắn gọn hơn nhưng có cơ chế hoạt động thô bạo hơn.
    
    
    INSERT OR REPLACE INTO chapters (id, comic_id, number, title, content, created_at)
    VALUES (?, ?, ?, ?, ?, ?);
    

  * Cơ chế: Nếu trùng `id`, SQLite sẽ XÓA hẳn dòng cũ (DELETE) và CHÈN một dòng hoàn toàn mới (INSERT).
  * Nhược điểm lớn: Vì nó xóa đi rồi chèn mới nên tất cả dữ liệu cũ của dòng đó (như ngày tạo `created_at`, số lượt đọc, trạng thái đã tải...) sẽ bị mất sạch và thay bằng dữ liệu mới truyền vào. Nếu bảng có khóa ngoại (Foreign Key) liên kết, hành động xóa này có thể gây lỗi dây chuyền (Cascade).



* * *

## Áp dụng thực tế vào Code Python (Thuần SQL)

Dưới đây là hàm `save` trong lớp `SQLiteChapterRepository` sử dụng kỹ thuật cú pháp `ON CONFLICT` để đảm bảo tối ưu tốc độ và toàn vẹn dữ liệu cho app crawl:
    
    
    import sqlite3
    from domain.model import Chapter
    
    class SQLiteChapterRepository:
        def __init__(self, db_path: str):
            self.db_path = db_path
    
        def save(self, chapter: Chapter) -> None:
            # 1. Kết nối DB với cấu hình tối ưu đa luồng
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute("PRAGMA journal_mode=WAL;") # Bật chế độ ghi log WAL
            cursor = conn.cursor()
            
            # 2. Câu lệnh SQL sử dụng UPSERT chuyên sâu
            query = """
                INSERT INTO chapters (id, comic_id, number, title, content, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    content = excluded.content
            """
            
            # 3. Thực thi lệnh
            cursor.execute(query, (
                chapter.id.value,       # Khóa chính để check trùng (Ví dụ: "linh-vuc-chuong-1")
                chapter.comic_id.value, 
                chapter.number, 
                chapter.title, 
                chapter.content,        # Nếu nội dung trên web cập nhật (sửa lỗi chính tả), DB sẽ tự cập nhật theo
                chapter.created_at.isoformat() # Nếu trùng, cột này SẼ KHÔNG bị ghi đè nhờ ON CONFLICT
            ))
            
            conn.commit()
            conn.close()
    

* * *

## Tại sao App Crawl truyện bắt buộc phải dùng UPSERT?

  1. Tăng tốc độ crawl gấp đôi: Nếu không dùng UPSERT, bạn sẽ phải chạy lệnh `SELECT` để xem chương đó có trong DB chưa, nếu chưa thì `INSERT`, nếu có rồi thì `UPDATE`. Việc này làm tốn 2 truy vấn cho 1 chương truyện. UPSERT gom lại chỉ còn 1 truy vấn duy nhất.
  2. An toàn khi chạy Đa luồng (Multi-threading): Trong môi trường cào truyện nhiều luồng, Luồng 1 và Luồng 2 có thể cùng cào trúng Chương 1 một lúc. Nếu dùng logic kiểm tra (`if không tồn tại thì insert`), cả 2 luồng sẽ thấy DB chưa có và cùng bắn lệnh `INSERT` → Gây lỗi `IntegrityError: UNIQUE constraint failed`. Với UPSERT, DB tự xếp hàng xử lý ghi đè an toàn.
  3. Cập nhật nội dung thông minh: Các website truyện thường xuyên sửa lỗi chính tả hoặc cập nhật lại chương lỗi. Khi bạn chạy crawl quét lại (Re-crawl), UPSERT giúp làm mới nội dung chữ (`content`) mà không làm xáo trộn cấu trúc hay ngày tạo của truyện trong hệ thống của bạn.



Bạn có muốn tối ưu sâu hơn về việc quản lý Transaction (giao dịch) khi UPSERT hàng loạt chương (Bulk Insert) để tăng tốc độ lưu từ 100 chương/giây lên 10,000 chương/giây không?