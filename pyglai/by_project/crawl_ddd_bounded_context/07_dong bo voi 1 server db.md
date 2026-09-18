Để đồng bộ dữ liệu truyện chữ từ file SQLite cục bộ (nơi Crawler lưu dữ liệu thô/sạch sau khi cào bulk) lên một Server MariaDB từ xa, chúng ta cần giải quyết bài toán cốt lõi: Đồng bộ hiệu năng cao (Bulk Sync), tiết kiệm băng thông mạng và đảm bảo không bị trùng lặp dữ liệu (Idempotency).

Áp dụng kiến trúc DDD, hành động đồng bộ này thuộc về một Application Service đóng vai trò là cầu nối liên Context (Integration Service). Dưới đây là chiến lược và phương pháp triển khai tối ưu bằng Python thuần SQL.

* * *

## 1\. Chiến lược Đồng bộ tối ưu (Sync Strategy)

Thay vì đồng bộ theo kiểu "đọc dòng nào, gọi API dòng đó" (gây nghẽn mạng do tạo hàng vạn HTTP request), ta sẽ dùng phương pháp Chế độ Bulk Batch + Đánh dấu trạng thái (State Tracking).

  1. Thêm cột trạng thái đồng bộ: Trong bảng `chapters` ở SQLite cục bộ, thêm cột `sync_status` (`0`: Chưa đồng bộ, `1`: Đã đồng bộ).
  2. Gom cụm dữ liệu (Batching): Quét từ SQLite các chương có `sync_status = 0`, gom thành các gói (ví dụ: 100 chương/gói).
  3. Nén và gửi (Payload Compression): Gửi gói dữ liệu qua một API Endpoint dạng `POST /api/v1/bulk-chapters`.
  4. Xử lý phía MariaDB (Server): Sử dụng lệnh `INSERT ... ON DUPLICATE KEY UPDATE` của MariaDB để ghi hàng loạt dữ liệu một cách an toàn.
  5. Xác nhận hoàn thành (Acknowledge): Nếu API Server trả về HTTP 200 (Thành công), cập nhật `sync_status = 1` cho các chương đó ở SQLite cục bộ.



* * *

## 2\. Thiết kế Cơ sở dữ liệu và API Payload

## Cập nhật Schema SQLite cục bộ:

Bạn chạy lệnh SQL này để bổ sung cột phục vụ đồng bộ:
    
    
    ALTER TABLE chapters ADD COLUMN sync_status INTEGER DEFAULT 0;
    CREATE INDEX IF NOT EXISTS idx_chapters_sync ON chapters(sync_status);
    

## Thiết kế cấu trúc JSON gửi lên Server (Payload):
    
    
    {
      "novel_id": "dau-pha-thuong-khung",
      "chapters": [
        {
          "chapter_number": 1.0,
          "title": "Chương 1: Tiêu Gia Thiên Tài",
          "content": "Nội dung chữ rất dài...",
          "crawled_source": "nguon1"
        },
        {
          "chapter_number": 2.0,
          "title": "Chương 2: Đấu Khí Đại Địa",
          "content": "Nội dung...",
          "crawled_source": "nguon1"
        }
      ]
    }
    

## Câu lệnh Thuần SQL phía Server (MariaDB) xử lý Bulk Insert:

Phía Server nhận mảng JSON, parse ra và thực thi câu lệnh SQL có cơ chế chống trùng lặp:
    
    
    INSERT INTO server_chapters (novel_id, chapter_number, title, content, crawled_source)
    VALUES (?, ?, ?, ?, ?)
    ON DUPLICATE KEY UPDATE 
        title = VALUES(title),
        content = VALUES(content);
    

* * *

## 3\. Triển khai Code Python Đồng bộ phía Cục bộ (Client Sync Service)

Sử dụng thư viện `sqlite3` kết hợp với `httpx` (hoặc `requests`) để tiến hành đồng bộ tuần tự/bất đồng bộ theo từng gói (batch).
    
    
    import sqlite3
    import httpx
    import time
    from typing import List, Dict, Any
    
    class SQLiteSyncRepository:
        def __init__(self, db_path: str = "truyen_chu.db"):
            self.db_path = db_path
    
        def _get_connection(self):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
        def get_un-synced_chapters(self, batch_size: int = 100) -> List[Dict[str, Any]]:
            """Lấy ra N chương chưa được đồng bộ lên Server"""
            sql = """
                SELECT id, novel_id, chapter_number, title, content, crawled_source 
                FROM chapters 
                WHERE sync_status = 0 
                LIMIT ?;
            """
            with self._get_connection() as conn:
                cursor = conn.execute(sql, (batch_size,))
                return [dict(row) for row in cursor.fetchall()]
    
        def mark_chapters_as_synced(self, local_ids: List[int]):
            """Cập nhật trạng thái thành ĐÃ ĐỒNG BỘ sau khi Server xác nhận nhận đủ"""
            sql = "UPDATE chapters SET sync_status = 1 WHERE id = ?;"
            with self._get_connection() as conn:
                conn.execute("BEGIN TRANSACTION;")
                conn.executemany(sql, [(l_id,) for l_id in local_ids])
                conn.execute("COMMIT;")
    
    
    class RemoteSyncService:
        def __init__(self, repo: SQLiteSyncRepository, api_url: str):
            self.repo = repo
            self.api_url = api_url
            self.client = httpx.Client(timeout=30.0) # Timeout dài vì nội dung text rất nặng
    
        def sync_loop(self, batch_size: int = 100):
            print("🚀 Bắt đầu tiến trình đồng bộ dữ liệu lên MariaDB Server...")
            
            while True:
                # 1. Đọc dữ liệu dở dang từ SQLite
                dirty_chapters = self.repo.get_un-synced_chapters(batch_size)
                if not dirty_chapters:
                    print("🎉 Đồng bộ hoàn tất! Tất cả dữ liệu local đã sạch.")
                    break
                
                # 2. Bóc tách ID cục bộ để cập nhật trạng thái sau này và format payload
                local_ids = [ch['id'] for ch in dirty_chapters]
                
                # Gom dữ liệu gửi đi (Loại bỏ trường 'id' cục bộ để giảm tải dung lượng mạng)
                payload = {
                    "chapters": [
                        {
                            "novel_id": ch["novel_id"],
                            "chapter_number": ch["chapter_number"],
                            "title": ch["title"],
                            "content": ch["content"],
                            "crawled_source": ch["crawled_source"]
                        } for ch in dirty_chapters
                    ]
                }
                
                # 3. Gửi Bulk Data qua API mạng
                try:
                    response = self.client.post(f"{self.api_url}/chapters/bulk-sync", json=payload)
                    
                    if response.status_code == 200:
                        # 4. Khi server báo OK, đánh dấu hoàn thành vào SQLite local ngay lập tức (Checkpoint)
                        self.repo.mark_chapters_as_synced(local_ids)
                        print(f"📦 Đã đồng bộ thành công cụm {len(dirty_chapters)} chương.")
                    else:
                        print(f"❌ Server trả về lỗi ({response.status_code}): {response.text}")
                        print("Tạm dừng đồng bộ để thử lại sau...")
                        time.sleep(5) # Tránh spam server khi đang lỗi
                        
                except Exception as e:
                    print(f"💥 Lỗi kết nối mạng: {e}")
                    time.sleep(10)
    

* * *

## 4\. Giải pháp nâng cao khi truyện quá nặng: Gzip Compression

Do nội dung chữ (`content`) chiếm tới 95% dung lượng gói JSON, nếu đồng bộ hàng trăm chương truyện cùng lúc, payload có thể lên tới vài chục Megabytes, dễ gây lỗi nghẽn mạng mạng hoặc quá tải bộ nhớ API Gateway.

Giải pháp: Hãy nén dữ liệu bằng `gzip` ngay trong Python trước khi gửi và cấu hình API Server giải nén tự động.
    
    
    import gzip
    import json
    
    # Thay thế phần gửi JSON thuần bằng gửi Byte đã nén:
    json_bytes = json.dumps(payload).encode('utf-8')
    compressed_data = gzip.compress(json_bytes)
    
    headers = {
        "Content-Encoding": "gzip",
        "Content-Type": "application/json"
    }
    
    response = self.client.post(f"{self.api_url}/chapters/bulk-sync", content=compressed_data, headers=headers)
    

_Tác dụng:_ Kỹ thuật này giúp giảm 70% - 85% dung lượng băng thông cần truyền tải, giúp tốc độ sync tăng lên gấp 3-4 lần.

Để hoàn thiện trọn vẹn mảnh ghép cuối cùng này, bạn có muốn xây dựng tiếp:

  * Phần code mẫu cho phía API Server nhận dữ liệu (ví dụ bằng FastAPI) để phân tích JSON và thực hiện câu lệnh Bulk Insert trực tiếp vào MariaDB?
  * Kỹ thuật đồng bộ cấu trúc Truyện (`novels`) trước khi đồng bộ Chương (`chapters`) để tránh bị lỗi khóa ngoại (Foreign Key Violation) trên MariaDB Server?