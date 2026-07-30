Để chuyển đổi cơ sở dữ liệu từ SQLite sang PostgreSQL trong kiến trúc 3 tầng, điểm tuyệt vời nhất là bạn **không cần sửa bất kỳ một dòng code nào** ở Tầng Logic (`CrawlerEngine`, `ExporterEngine`) hay Tầng Hiển thị (`CLIViewer`).

Tất cả những gì chúng ta cần làm là chỉnh sửa **Tầng Dữ liệu (Data Tier)** bằng cách thay đổi các câu lệnh SQL thuần cho phù hợp với cú pháp của PostgreSQL và thay thế thư viện kết nối.

Dưới đây là các bước chi tiết để cấu hình và chuyển đổi hệ thống sang PostgreSQL.

* * *

🛠️ 1. Chuẩn bị môi trường & Thư viện

Trước tiên, bạn cần cài đặt thư viện kết nối PostgreSQL chuẩn của Python:

bash
    
    
    pip install psycopg2-binary
    

Hãy thận trọng khi sử dụng mã.

* * *

🏛️ 2. Cập nhật Data Tier: Điểm thay đổi cốt lõi

Cú pháp SQL thuần của SQLite và PostgreSQL có một vài điểm khác biệt nhỏ:

  * **Ký hiệu giữ chỗ (Placeholder):** SQLite dùng dấu chấm hỏi `?`, còn PostgreSQL dùng `%s`.
  * **Tự động tăng ID (Autoincrement):** SQLite dùng `INTEGER PRIMARY KEY AUTOINCREMENT`, PostgreSQL dùng kiểu dữ liệu `SERIAL PRIMARY KEY`.
  * **Từ khóa chèn trùng lặp:** SQLite dùng `INSERT OR IGNORE`, PostgreSQL dùng cú pháp chuẩn `INSERT INTO ... ON CONFLICT (url) DO NOTHING`.



Bước A: Cấu hình lại kết nối tập trung (`database/db_manager.py`)

Thay vì khai báo file `.db` cục bộ, chúng ta cấu hình kết nối tới PostgreSQL Server.

python
    
    
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    class DBManager:
        def __init__(self):
            # Cấu hình thông tin kết nối tới PostgreSQL Server của bạn
            self.config = {
                "dbname": "comic_crawler_db",
                "user": "postgres",
                "password": "your_password",
                "host": "localhost",
                "port": "5432"
            }
            self.init_db()
    
        def get_connection(self):
            """Trả về một kết nối mới tới PostgreSQL Server"""
            return psycopg2.connect(**self.config)
    
        def init_db(self):
            """Khởi tạo cấu trúc bảng bằng SQL thuần của PostgreSQL"""
            query_stories = """
            CREATE TABLE IF NOT EXISTS stories (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                author TEXT,
                source TEXT,
                status TEXT DEFAULT 'Đang ra'
            );
            """
            query_chapters = """
            CREATE TABLE IF NOT EXISTS chapters (
                id SERIAL PRIMARY KEY,
                story_id INTEGER REFERENCES stories(id) ON DELETE CASCADE,
                chapter_number NUMERIC(6, 2), -- Chứa số chương chính xác hơn REAL
                title TEXT,
                content TEXT
            );
            """
            query_logs = """
            CREATE TABLE IF NOT EXISTS crawler_error_logs (
                id SERIAL PRIMARY KEY,
                story_id INTEGER,
                chapter_number NUMERIC(6, 2),
                chapter_url TEXT,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'PENDING'
            );
            """
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query_stories)
                    cursor.execute(query_chapters)
                    cursor.execute(query_logs)
                conn.commit()
    

Hãy thận trọng khi sử dụng mã.

* * *

Bước B: Cập nhật Cú pháp SQL trong các Repository

Chúng ta sẽ sửa đổi file `StoryRepository` và `ChapterRepository` để khớp với thư viện `psycopg2` mới.

**Cập nhật file:** `database/story_repository.py`

python
    
    
    import psycopg2
    from typing import List, Optional
    from database.db_manager import DBManager
    from database.models import StoryModel
    
    class StoryRepository:
        def __init__(self):
            self.db_manager = DBManager()
    
        def insert_story(self, story: StoryModel) -> int:
            """Sử dụng cú pháp PostgreSQL thuần để chèn và lấy ID ngay lập tức"""
            # Thay thế 'INSERT OR IGNORE' bằng 'ON CONFLICT DO NOTHING'
            # Thêm 'RETURNING id' để lấy ID về trực tiếp mà không cần chạy câu lệnh SELECT thứ hai
            query = """
            INSERT INTO stories (title, url, author, source, status) 
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING
            RETURNING id;
            """
            
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (story.title, story.url, story.author, story.source, story.status))
                    result = cursor.fetchone()
                    
                    if result:
                        conn.commit()
                        return result[0] # Trả về ID vừa tạo
                    
                    # Nếu truyện đã tồn tại (conflict), tìm lại ID cũ để trả về
                    cursor.execute("SELECT id FROM stories WHERE url = %s;", (story.url,))
                    return cursor.fetchone()[0]
    
        def get_all_stories(self) -> List[StoryModel]:
            """Lấy toàn bộ danh sách truyện với cú pháp %s của PostgreSQL"""
            query = "SELECT id, title, url, author, source, status FROM stories ORDER BY id DESC;"
            stories = []
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    for row in cursor.fetchall():
                        stories.append(StoryModel(
                            id=row[0], title=row[1], url=row[2], 
                            author=row[3], source=row[4], status=row[5]
                        ))
            return stories
    

Hãy thận trọng khi sử dụng mã.

**Cập nhật file:** `database/chapter_repository.py`

python
    
    
    import psycopg2
    from typing import List
    from database.db_manager import DBManager
    from database.models import ChapterModel
    
    class ChapterRepository:
        def __init__(self):
            self.db_manager = DBManager()
    
        def insert_chapter(self, chapter: ChapterModel) -> bool:
            """Ghi chương truyện chữ dung lượng lớn vào PostgreSQL"""
            query = """
            INSERT INTO chapters (story_id, chapter_number, title, content)
            VALUES (%s, %s, %s, %s);
            """
            cleaned_text = chapter.clean_content()
            try:
                with self.db_manager.get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(query, (
                            chapter.story_id, 
                            chapter.chapter_number, 
                            chapter.title, 
                            cleaned_text
                        ))
                    conn.commit()
                    return True
            except psycopg2.Error as e:
                print(f"[-] Lỗi PostgreSQL khi lưu chương {chapter.chapter_number}: {e}")
                return False
    
        def check_chapter_exists(self, story_id: int, chapter_number: float) -> bool:
            """Kiểm tra chương tồn tại dùng cú pháp LIMIT 1 chuẩn"""
            query = "SELECT 1 FROM chapters WHERE story_id = %s AND chapter_number = %s LIMIT 1;"
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (story_id, chapter_number))
                    return cursor.fetchone() is not None
    

Hãy thận trọng khi sử dụng mã.

* * *

🎯 Tại sao đây lại là minh chứng rõ ràng cho sức mạnh của Kiến trúc 3 tầng?

Hãy nhìn lại toàn bộ hệ thống của bạn sau khi đổi sang PostgreSQL:

  1. Bạn đã thay đổi hệ thống lưu trữ cốt lõi từ file máy tính sang hệ quản trị cơ sở dữ liệu Client-Server mạnh mẽ.
  2. File chạy giao diện `main.py`, hệ thống điều phối `crawler_engine.py` và module bóc tách `source_a.py` **hoàn toàn giữ nguyên, không cần chỉnh sửa hay biên dịch lại một chữ nào**.
  3. Do tầng Logic chỉ giao tiếp thông qua giao ước là các hàm của `Repository` (như `.insert_story()`), việc bên trong repository đó gọi đến SQLite hay PostgreSQL là chuyện "nội bộ" riêng tư của Tầng Dữ liệu.



Hệ thống của bạn bây giờ đã sẵn sàng để triển khai lên các máy chủ đám mây (Cloud Server) và chạy cào quy mô lớn.

Để vận hành một hệ thống lớn như vậy một cách ổn định, bạn có muốn tìm hiểu về **Cơ chế cấu hình biến môi trường (Environment Variables - file`.env`)** nhằm bảo mật thông tin tài khoản Database, hay giải pháp **Quản lý danh sách Proxy bằng SQL thuần** để framework tự động thay đổi địa chỉ mạng tránh bị website chặn IP không?

