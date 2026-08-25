Dưới đây là tổng hợp toàn bộ các kỹ thuật INSERT trong SQLite thuần SQL, được phân loại theo từng kịch bản cụ thể khi phát triển ứng dụng crawl truyện bằng Python.

* * *

## Bảng so sánh nhanh các kỹ thuật INSERT

Tên kỹ thuật| Cú pháp SQL chính| Hành vi khi trùng Khóa chính (`id`)| Tốc độ| Kịch bản áp dụng tốt nhất  
---|---|---|---|---  
1\. Standard INSERT| `INSERT INTO ...`| Báo lỗi (`IntegrityError`) và sập luồng.| Chậm| Thêm mới hoàn toàn (ví dụ: tạo truyện mới).  
2\. INSERT OR IGNORE| `INSERT OR IGNORE INTO ...`| Bỏ qua, giữ nguyên 100% dữ liệu cũ.| Rất nhanh| Quét diện rộng để tìm chương mới (Re-crawl).  
3\. UPSERT (ON CONFLICT)| `INSERT INTO ... ON CONFLICT`| Cập nhật các cột được chỉ định cụ thể.| Trung bình| Cào cập nhật nội dung (sửa lỗi chính tả truyện).  
4\. INSERT OR REPLACE| `INSERT OR REPLACE INTO ...`| Xóa dòng cũ, chèn dòng hoàn toàn mới.| Chậm hơn| Ghi đè toàn bộ không cần giữ lại lịch sử.  
5\. Bulk INSERT| `executemany()` \+ Giao dịch thủ công| Phụ thuộc vào 1 trong 4 cú pháp trên.| Cực nhanh (vạn dòng/s)| Lưu hàng loạt chương truyện sau khi cào.  
  
* * *

## Chi tiết từng kỹ thuật & Code mẫu Python

## 1\. Standard INSERT (Chèn thông thường)

Đây là câu lệnh cơ bản nhất. Nếu dữ liệu đã tồn tại, SQLite sẽ ném ra lỗi `UNIQUE constraint failed`.

  * Kịch bản: Khi bạn tạo một bộ truyện mới (Comic) lần đầu tiên, nơi mà slug truyện bắt buộc phải là duy nhất.


    
    
    sql = "INSERT INTO comics (id, title, source_url) VALUES (?, ?, ?);"
    cursor.execute(sql, ("linh-vuc", "Linh Vực", "https://..."))
    

## 2\. INSERT OR IGNORE (Chèn hoặc Bỏ qua)

Nếu trùng khóa chính `id`, SQLite sẽ im lặng bỏ qua dòng đó mà không báo lỗi, không làm gián đoạn ứng dụng.

  * Kịch bản: Bạn crawl lại 1000 chương cũ của một bộ truyện để check xem có chương mới không. Gặp chương cũ thì bỏ qua ngay để tiết kiệm tài nguyên.


    
    
    sql = "INSERT OR IGNORE INTO chapters (id, comic_id, number, title, content) VALUES (?, ?, ?, ?, ?);"
    cursor.execute(sql, ("linh-vuc-1", "linh-vuc", 1, "Chương 1", "Nội dung..."))
    

## 3\. UPSERT / INSERT OR UPDATE (Chèn hoặc Cập nhật có chọn lọc)

Sử dụng mệnh đề `ON CONFLICT(id) DO UPDATE SET`. Kỹ thuật này cho phép bạn cập nhật nội dung chữ (`content`) của truyện nhưng giữ nguyên ngày tạo (`created_at`).

  * Kịch bản: Khi nguồn truyện sửa lại lỗi chính tả hoặc cập nhật lại chương bị lỗi, bạn muốn ghi đè nội dung mới vào DB.


    
    
    sql = """
        INSERT INTO chapters (id, comic_id, number, title, content, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            title = excluded.title,
            content = excluded.content; -- Giữ nguyên created_at gốc
    """
    cursor.execute(sql, (id, comic_id, number, title, content, created_at))
    

## 4\. INSERT OR REPLACE (Chèn hoặc Thay thế toàn bộ)

Cơ chế của lệnh này là XÓA hẳn dòng cũ (DELETE) nếu trùng ID, sau đó CHÈN một dòng hoàn toàn mới (INSERT).

  * Nhược điểm: Làm mất sạch các dữ liệu lịch sử không được truyền vào câu lệnh (như ngày tạo, số lượt đọc, trạng thái...).


    
    
    sql = "INSERT OR REPLACE INTO chapters (id, comic_id, number, title, content) VALUES (?, ?, ?, ?, ?);"
    cursor.execute(sql, (id, comic_id, number, title, content))
    

## 5\. Bulk INSERT (Chèn hàng loạt tối ưu hiệu năng)

Kỹ thuật tối thượng để đạt tốc độ 10,000+ chương/giây. Bạn kết hợp `executemany` (chạy trên RAM) với việc điều khiển Transaction thủ công (`BEGIN/COMMIT`) để chỉ ghi xuống đĩa cứng đúng 1 lần duy nhất cho cả một danh sách (Batch).

  * Kịch bản: Khi bạn cào một bộ truyện dài vài nghìn chương, bạn gom cứ 500 chương thành 1 Batch rồi bắn xuống DB.


    
    
    def save_bulk(db_path, chapters_list):
        # Tắt autocommit bằng isolation_level=None để tự quản lý Transaction
        conn = sqlite3.connect(db_path, isolation_level=None)
        conn.execute("PRAGMA journal_mode=WAL;")      # Bật ghi log đồng thời
        conn.execute("PRAGMA synchronous=OFF;")       # Tối ưu tốc độ ghi đĩa
        cursor = conn.cursor()
    
        # Có thể kết hợp với kỹ thuật số 2 (IGNORE) hoặc số 3 (UPSERT) ở đây
        sql = "INSERT OR IGNORE INTO chapters (id, comic_id, number, title, content) VALUES (?, ?, ?, ?, ?);"
        
        try:
            cursor.execute("BEGIN TRANSACTION;")      # Mở giao dịch
            cursor.executemany(sql, chapters_list)    # Đẩy toàn bộ danh sách vào RAM
            cursor.execute("COMMIT;")                 # Ghi 1 lần duy nhất xuống ổ cứng
        except Exception as e:
            cursor.execute("ROLLBACK;")               # Hủy bỏ nếu có lỗi để tránh lỗi DB
            raise e
        finally:
            conn.close()
    

* * *

## Lời khuyên thiết kế cho App Crawl theo DDD

Trong kiến trúc Domain-Driven Design, bạn nên tách biệt các kỹ thuật này thành các phương thức rõ ràng trong Repository Interface ở tầng Domain, ví dụ:

  * `save(chapter)`: Dùng UPSERT cho các thao tác lưu thông thường.
  * `save_new_only_bulk(chapters)`: Dùng Bulk + INSERT OR IGNORE khi chạy các tiến trình quét (scan) truyện cũ hàng ngày để đạt tốc độ tối đa.



Nếu bạn muốn, tôi có thể hướng dẫn thiết kế tiếp Tầng Domain Event để khi hệ thống thực hiện `INSERT` thành công một chương mới (không bị Ignore), nó sẽ tự động kích hoạt một hành động khác (như gửi thông báo Telegram hoặc tự động tải ảnh minh họa của chương đó)?