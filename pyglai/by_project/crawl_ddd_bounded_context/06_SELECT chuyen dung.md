Để phục vụ một App đọc truyện mượt mà, Database không chỉ cần ghi nhanh (Bulk Write) mà còn phải tối ưu cho việc đọc siêu tốc (Query Optimization). Truyện chữ thường có hàng nghìn chương, nếu không tối ưu, các câu lệnh chuyển chương hoặc tải mục lục sẽ gây lag máy.

Dưới đây là thiết kế các câu lệnh Thuần SQL nâng cao dành cho App đọc truyện, giúp tối ưu hóa UI/UX từ danh sách cho đến màn hình đọc.

* * *

## 1\. Thêm Index tối ưu (Bổ sung vào Schema)

Để các câu lệnh `SELECT` chạy dưới 1 mili-giây (O(log N)), bạn cần chạy câu lệnh tạo chỉ mục (Index) này trong SQLite:
    
    
    -- Index này giúp tìm chương tiếp theo / chương trước đó của một truyện cực nhanh
    CREATE INDEX IF NOT EXISTS idx_chapters_novel_navigation 
    ON chapters(novel_id, chapter_number);
    

* * *

## 2\. Các câu lệnh Thuần SQL chuyên dụng cho App Đọc Truyện

## A. Truy vấn Mục lục (Phân trang mượt mà)

Khi người dùng mở danh sách chương, app cần hiển thị tiêu đề và số chương. Đối với truyện dài (vài nghìn chương), bắt buộc phải phân trang (`LIMIT` và `OFFSET`).
    
    
    -- Lấy danh sách chương của truyện 'dau-pha-thuong-khung' từ nguồn 'nguon1' (Trang 1, mỗi trang 20 chương)
    SELECT id, chapter_number, title, crawled_source, created_at
    FROM chapters
    WHERE novel_id = 'dau-pha-thuong-khung' AND crawled_source = 'nguon1'
    ORDER BY chapter_number ASC
    LIMIT 20 OFFSET 0; -- Trang 2 sẽ là LIMIT 20 OFFSET 20
    

## B. Đọc Nội dung Chương hiện tại & Tự động tìm ID Chương kế tiếp / Chương trước

Đây là tính năng cốt lõi của màn hình đọc truyện. Khi người dùng đang đọc chương 10, thay vì để App phải chạy thêm lệnh phụ, ta dùng Cửa sổ hàm (Window Functions) hoặc Subquery trong một câu lệnh duy nhất để lấy nội dung chương hiện tại, đồng thời biết luôn ID của chương trước (`prev_id`) và chương sau (`next_id`) để bấm nút "Chương tiếp theo" chuyển trang ngay lập tức.
    
    
    -- Lấy nội dung chương hiện tại cùng liên kết điều hướng (Navigation)
    WITH ranked_chapters AS (
        SELECT 
            id, 
            chapter_number, 
            title, 
            content,
            LAG(id) OVER (ORDER BY chapter_number ASC) as prev_id,
            LEAD(id) OVER (ORDER BY chapter_number ASC) as next_id
        FROM chapters
        WHERE novel_id = 'dau-pha-thuong-khung' AND crawled_source = 'nguon1'
    )
    SELECT id, chapter_number, title, content, prev_id, next_id
    FROM ranked_chapters
    WHERE chapter_number = 10.0; -- Thay số chương hiện tại vào đây
    

_Gợi ý:_ Nếu không tìm thấy `prev_id` hoặc `next_id` (trả về `NULL`), App sẽ tự động làm mờ (disable) nút bấm tương ứng trên giao diện.

## C. Tìm kiếm Chương truyện (Search Feature)

Nếu App có tính năng cho phép người dùng gõ số chương hoặc từ khóa tiêu đề để nhảy nhanh đến chương đó:
    
    
    -- Tìm kiếm chương theo tiêu đề hoặc số hiệu gần đúng
    SELECT id, chapter_number, title
    FROM chapters
    WHERE novel_id = 'dau-pha-thuong-khung' 
      AND (title LIKE '%Đại kết cục%' OR chapter_number = 1200)
    ORDER BY chapter_number ASC
    LIMIT 5;
    

## D. Lấy Thống kê cho Màn hình chi tiết Truyện (Novel Detail)

Trước khi bấm vào đọc, người dùng cần xem truyện này có bao nhiêu chương và chương mới nhất được cập nhật vào lúc nào.
    
    
    SELECT 
        COUNT(id) as total_chapters,
        MAX(chapter_number) as latest_chapter_number,
        MAX(created_at) as last_updated
    FROM chapters
    WHERE novel_id = 'dau-pha-thuong-khung' AND crawled_source = 'nguon1';
    

* * *

## 3\. Triển khai vào Python Repository (App API / Local Reader Service)

Dưới đây là cách đóng gói các câu lệnh SQL trên thành các hàm xử lý dữ liệu sạch cho ứng dụng của bạn:
    
    
    import sqlite3
    from typing import Dict, Any, Optional
    
    class SQLiteReaderRepository:
        def __init__(self, db_path: str = "truyen_chu.db"):
            self.db_path = db_path
    
        def _get_connection(self):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row # Trả về dạng Dict để App dễ xài
            return conn
    
        def get_chapter_for_reading(self, novel_id: str, source: str, chapter_num: float) -> Optional[Dict[str, Any]]:
            """Lấy toàn bộ nội dung chương để đọc kèm liên kết chương trước/sau"""
            sql = """
                WITH ranked_chapters AS (
                    SELECT 
                        id, chapter_number, title, content,
                        LAG(id) OVER (ORDER BY chapter_number ASC) as prev_id,
                        LEAD(id) OVER (ORDER BY chapter_number ASC) as next_id
                    FROM chapters
                    WHERE novel_id = ? AND crawled_source = ?
                )
                SELECT id, chapter_number, title, content, prev_id, next_id
                FROM ranked_chapters
                WHERE chapter_number = ?;
            """
            with self._get_connection() as conn:
                cursor = conn.execute(sql, (novel_id, source, chapter_num))
                row = cursor.fetchone()
                return dict(row) if row else None
    
        def get_chapters_menu(self, novel_id: str, source: str, page: int = 1, per_page: int = 50) -> list:
            """Lấy danh sách mục lục phân trang"""
            offset = (page - 1) * per_page
            sql = """
                SELECT id, chapter_number, title 
                FROM chapters
                WHERE novel_id = ? AND crawled_source = ?
                ORDER BY chapter_number ASC
                LIMIT ? OFFSET ?;
            """
            with self._get_connection() as conn:
                cursor = conn.execute(sql, (novel_id, source, per_page, offset))
                return [dict(row) for row in cursor.fetchall()]
    

## 💡 Mẹo nhỏ khi phát triển App Đọc Truyện:

Do SQLite lưu toàn bộ text nội dung chương (`content`) dưới dạng một chuỗi văn bản lớn, khi lấy danh sách mục lục (Menu), tuyệt đối không chọn cột `content` (Tránh dùng `SELECT *`). Việc này giúp giải phóng RAM cực lớn cho thiết bị và tăng tốc độ truyền tải dữ liệu qua mạng nếu bạn làm App Client-Server.

Để hoàn thiện trọn vẹn toàn bộ ứng dụng này, bạn có muốn chúng ta đi tiếp vào:

  * Kỹ thuật viết Regex thông minh ở tầng Parser để bóc tách chính xác số chương `chapter_number` từ các chuỗi tiêu đề phức tạp (tránh bị lỗi ép kiểu khi gặp chương dạng "Chương 23.5" hoặc "Quyển 2 - Chương 5")?
  * Hay bạn muốn tìm hiểu phương pháp đồng bộ (Sync) dữ liệu từ file SQLite cục bộ này lên một Server API từ xa?