Khi cào bulk hàng loạt truyện chữ (với lượng text rất lớn từ 2 - 3 nguồn), SQLite3 là sự lựa chọn tuyệt vời nhờ tính nhỏ gọn, không cần cấu hình server, và tốc độ đọc/ghi file local cực kỳ nhanh nếu được tối chỉnh bằng Thuần SQL.

Áp dụng tư duy DDD, ta sẽ chia cơ sở dữ liệu làm 2 phần (bảng nghiệp vụ truyện và bảng quản lý trạng thái tác vụ cào) nằm trong cùng một file SQLite nhưng tách biệt về vai trò.

* * *

## 1\. Thiết kế Lược đồ Database (Schema Thuần SQL)

Dưới đây là file SQL khởi tạo cấu trúc dữ liệu (`schema.sql`). Chúng ta sẽ tận dụng triệt để các tính năng của SQLite như `ON CONFLICT` để đảm bảo tính Idempotency (không trùng lặp dữ liệu khi cào lại).
    
    
    -- Kích hoạt khóa ngoại (Mặc định SQLite tắt tính năng này)
    PRAGMA foreign_keys = ON;
    
    -- ==========================================
    -- BẢNG NGHIỆP VỤ (Novel & Chapter Entities)
    -- ==========================================
    
    -- 1. Bảng lưu thông tin tổng quan của Truyện
    CREATE TABLE IF NOT EXISTS novels (
        id TEXT PRIMARY KEY,               -- Unique ID dạng String (Ví dụ: slug 'dau-pha-thuong-khung')
        title TEXT NOT NULL,               -- Tên truyện
        author TEXT DEFAULT 'Ẩn danh',      -- Tác giả
        source_url TEXT,                   -- URL gốc của truyện để đối chiếu
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    
    -- 2. Bảng lưu nội dung các Chương (Quan hệ 1-N với Novels)
    CREATE TABLE IF NOT EXISTS chapters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        novel_id TEXT NOT NULL,
        chapter_number REAL NOT NULL,      -- Dùng REAL (float) để xử lý chương phụ dạng 100.5
        title TEXT NOT NULL,
        content TEXT NOT NULL,             -- Nội dung chữ của chương
        crawled_source TEXT NOT NULL,      -- Lưu nguồn cào (nguon1, nguon2) để biết lấy từ đâu
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
        -- Ràng buộc: Một truyện không thể có 2 chương trùng số hiệu từ cùng 1 nguồn
        UNIQUE(novel_id, chapter_number, crawled_source) 
    );
    
    -- Tạo Index để App đọc truyện sau này truy vấn mục lục và nội dung siêu tốc
    CREATE INDEX IF NOT EXISTS idx_chapters_novel_number 
    ON chapters(novel_id, chapter_number);
    
    
    -- ==========================================
    -- BẢNG QUẢN LÝ TIẾN ĐỘ (Ingestion Checkpoint Application State)
    -- ==========================================
    
    -- 3. Bảng quản lý hàng đợi URL cào dở dang
    CREATE TABLE IF NOT EXISTS crawl_checkpoints (
        url_hash TEXT PRIMARY KEY,         -- Mã băm MD5 của URL để kiểm tra cho nhanh
        novel_id TEXT NOT NULL,
        url TEXT NOT NULL,
        source TEXT NOT NULL,
        status TEXT CHECK(status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')) DEFAULT 'PENDING',
        retry_count INTEGER DEFAULT 0,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_checkpoints_status ON crawl_checkpoints(status);
    

* * *

## 2\. Tối ưu hóa SQLite3 cho việc Ghi hàng loạt (Bulk Insert)

Mặc định, SQLite rất chậm khi ghi từng dòng một (vì mỗi lệnh `INSERT` nó sẽ khóa file và ghi xuống ổ cứng). Để cào Bulk tốc độ cao, bắt buộc phải áp dụng 3 quy tắc vàng bằng Thuần SQL:

  1. Bật chế độ WAL (Write-Ahead Logging): Cho phép vừa đọc vừa ghi song song mà không bị khóa file (`PRAGMA journal_mode=WAL;`).
  2. Tắt đồng bộ ghi an toàn quá mức: Đẩy dữ liệu vào cache RAM trước rồi ghi xuống đĩa sau (`PRAGMA synchronous=NORMAL;`).
  3. Sử dụng Transaction (Giao dịch): Gom 50 - 100 chương vào một khối `BEGIN TRANSACTION; ... COMMIT;`.



* * *

## 3\. Mã nguồn Python triển khai Repository Tối ưu bằng Thuần SQL

Dưới đây là phần triển khai tầng Infrastructure (Database Adapter) bằng thư viện thư viện `sqlite3` có sẵn của Python, áp dụng các kỹ thuật tối ưu ở trên.
    
    
    import sqlite3
    import hashlib
    from typing import List, Dict, Any
    
    class SQLiteNovelRepository:
        def __init__(self, db_path: str = "truyen_chu.db"):
            self.db_path = db_path
            self._init_db()
    
        def _get_connection(self):
            conn = sqlite3.connect(self.db_path)
            # Cấu hình tối ưu Bulk Write ngay khi kết nối
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL; ")
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.row_factory = sqlite3.Row # Để lấy dữ liệu dạng Dict giống dữ liệu bóc tách
            return conn
    
        def _init_db(self):
            """Khởi tạo table từ file schema.sql"""
            # (Giả định bạn đã lưu đoạn script SQL ở mục 1 vào file schema.sql)
            with open("schema.sql", "r", encoding="utf-8") as f:
                schema_sql = f.read()
            
            with self._get_connection() as conn:
                conn.executescript(schema_sql)
    
        def _generate_hash(self, url: str) -> str:
            return hashlib.md5(url.encode('utf-8')).hexdigest()
    
        # ==========================================
        # CÁC CÂU LỆNH THUẦN SQL CHO HỆ THỐNG CÀO
        # ==========================================
    
        def save_discovered_urls(self, novel_id: str, source: str, urls: List[str]):
            """Giai đoạn Discovery: Lưu toàn bộ danh sách URL cần cào (nếu chưa có)"""
            sql = """
                INSERT INTO crawl_checkpoints (url_hash, novel_id, url, source, status)
                VALUES (?, ?, ?, ?, 'PENDING')
                ON CONFLICT(url_hash) DO NOTHING;
            """
            data = [(self._generate_hash(url), novel_id, url, source) for url in urls]
            
            with self._get_connection() as conn:
                conn.executemany(sql, data) # Thực hiện bulk insert siêu nhanh
    
        def get_pending_tasks(self, novel_id: str) -> List[Dict[str, Any]]:
            """Lấy danh sách các URL chưa cào hoặc cào lỗi để chạy tiếp"""
            sql = """
                SELECT url_hash, url, source, novel_id 
                FROM crawl_checkpoints 
                WHERE novel_id = ? AND status IN ('PENDING', 'FAILED') AND retry_count < 3;
            """
            with self._get_connection() as conn:
                cursor = conn.execute(sql, (novel_id,))
                return [dict(row) for row in cursor.fetchall()]
    
        def update_task_status(self, url_hash: str, status: str):
            """Cập nhật trạng thái tác vụ mạng (PENDING -> PROCESSING)"""
            sql = "UPDATE crawl_checkpoints SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE url_hash = ?;"
            with self._get_connection() as conn:
                conn.execute(sql, (status, url_hash))
    
        def save_chapters_bulk(self, chapters_data: List[Dict[str, Any]], completed_hashes: List[str]):
            """
            Ghi hàng loạt nội dung chương VÀ cập nhật Checkpoint thành COMPLETED.
            Sử dụng duy nhất 1 TRANSACTION để đảm bảo an toàn dữ liệu tuyệt đối.
            """
            insert_chapter_sql = """
                INSERT INTO chapters (novel_id, chapter_number, title, content, crawled_source)
                VALUES (:novel_id, :chapter_number, :title, :content, :crawled_source)
                ON CONFLICT(novel_id, chapter_number, crawled_source) DO UPDATE SET
                    title = excluded.title,
                    content = excluded.content;
            """
            
            update_checkpoint_sql = """
                UPDATE crawl_checkpoints 
                SET status = 'COMPLETED', updated_at = CURRENT_TIMESTAMP 
                WHERE url_hash = ?;
            """
    
            conn = self._get_connection()
            try:
                conn.execute("BEGIN TRANSACTION;")
                
                # 1. Ghi bulk danh sách chương sạch
                conn.executemany(insert_chapter_sql, chapters_data)
                
                # 2. Cập nhật trạng thái hoàn thành cho các checkpoint tương ứng
                conn.executemany(update_checkpoint_sql, [(u_hash,) for u_hash in completed_hashes])
                
                conn.execute("COMMIT;")
                print(f"[DB] Đã Bulk Insert thành công {len(chapters_data)} chương.")
            except Exception as e:
                conn.execute("ROLLBACK;")
                print(f"[DB Error] Lỗi ghi bulk, đã rollback toàn bộ: {e}")
                raise e
            finally:
                conn.close()
    
        def handle_task_failure(self, url_hash: str):
            """Đánh dấu lỗi và tăng số lần cấu hình thử lại"""
            sql = """
                UPDATE crawl_checkpoints 
                SET status = 'FAILED', retry_count = retry_count + 1, updated_at = CURRENT_TIMESTAMP 
                WHERE url_hash = ?;
            """
            with self._get_connection() as conn:
                conn.execute(sql, (url_hash,))
    

## 4\. Luồng tích hợp gọn gàng trong Application Service

Khi chạy chương trình cào, code ứng dụng sẽ kết hợp các hàm thuần SQL trên cực kỳ đơn giản:
    
    
    # Giả lập luồng xử lý trong worker sau khi gom đủ 50 chương
    async def flush_buffer_to_database(repo: SQLiteNovelRepository, buffer: list):
        chapters_to_save = []
        hashes_to_complete = []
        
        for item in buffer:
            # item bao gồm: { 'url_hash': ..., 'source_type': ..., 'novel_id': ..., 'clean_data': ChapterVO }
            vo = item['clean_data']
            chapters_to_save.append({
                "novel_id": vo.novel_id,
                "chapter_number": vo.chapter_num,
                "title": vo.title,
                "content": vo.content,
                "crawled_source": item['source_type']
            })
            hashes_to_complete.append(item['url_hash'])
            
        # Gọi hàm hạ tầng duy nhất
        repo.save_chapters_bulk(chapters_to_save, hashes_to_complete)
        buffer.clear()
    

Với cấu trúc SQLite thuần SQL này, bạn đã có một bộ khung lưu trữ rất mạnh mẽ cho bài toán Bulk Crawl. Tiếp theo, bạn có muốn tối ưu hóa câu lệnh SELECT SQL chuyên dụng cho App đọc truyện (ví dụ: lấy danh sách chương phân trang hoặc lấy tính năng đọc chương kế tiếp/chương trước đó nhanh nhất) không?