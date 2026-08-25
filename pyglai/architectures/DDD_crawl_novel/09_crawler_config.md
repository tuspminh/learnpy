Để quản lý các công thức cào dữ liệu (XPath, CSS Selector, cấu hình Headers, Cookies) của từng trang web khác nhau (như TruyenFull, TangThuVien, NetTruyen), chúng ta cần thiết kế một Bounded Context mới hoặc một Aggregate mới trong Domain có tên là CrawlConfig (hoặc CrawlRule).

Dưới đây là cách thiết kế chi tiết Aggregate này theo chuẩn Domain-Driven Design (DDD) và triển khai bằng SQLite thuần SQL.

* * *

## 1\. Thiết kế Tầng Domain (`domain/crawler_config.py`)

Cấu hình cào truyện của một trang web thường có cấu trúc phân cấp phức tạp. Chúng ta sẽ định nghĩa một Aggregate Root tên là `CrawlConfig` kết hợp với các Value Objects để đóng gói toàn bộ công thức cào.
    
    
    from dataclasses import dataclass
    from typing import Dict, Optional
    
    # --- Value Objects ---
    @dataclass(frozen=True)
    class SiteId:
        value: str  # Ví dụ: "truyenfull.vn", "tangthuvien.vn"
    
    @dataclass(frozen=True)
    class ComicSelectors:
        """Các cấu trúc XPath/CSS để cào thông tin truyện"""
        title_selector: str
        author_selector: str
        description_selector: str
        chapter_list_selector: str
    
    @dataclass(frozen=True)
    class ChapterSelectors:
        """Các cấu trúc XPath/CSS để cào thông tin chương"""
        title_selector: str
        content_selector: str
    
    @dataclass(frozen=True)
    class HttpConfig:
        """Cấu hình kết nối HTTP để tránh bị chặn (Anti-bot)"""
        headers: Dict[str, str]
        timeout_seconds: int = 10
        use_proxy: bool = False
    
    # --- Aggregate Root ---
    class CrawlConfig:
        def __init__(
            self, 
            site_id: SiteId, 
            name: str, 
            comic_selectors: ComicSelectors, 
            chapter_selectors: ChapterSelectors,
            http_config: HttpConfig,
            is_active: bool = True
        ):
            self.site_id = site_id
            self.name = name
            self.comic_selectors = comic_selectors
            self.chapter_selectors = chapter_selectors
            self.http_config = http_config
            self.is_active = is_active
    
        def disable(self):
            """Domain Logic: Tạm dừng cấu hình cào của nguồn này nếu bị lỗi/đổi giao diện"""
            self.is_active = False
    
        def update_selectors(self, comic_sel: ComicSelectors, chapter_sel: ChapterSelectors):
            """Domain Logic: Cập nhật lại công thức cào khi web nguồn thay đổi giao diện"""
            self.comic_selectors = comic_sel
            self.chapter_selectors = chapter_sel
    

* * *

## 2\. Định nghĩa Interface Repository (`domain/config_repository.py`)
    
    
    from abc import ABC, abstractmethod
    from typing import Optional
    from .crawler_config import CrawlConfig, SiteId
    
    class CrawlConfigRepository(ABC):
        @abstractmethod
        def save(self, config: CrawlConfig) -> None:
            pass
    
        @abstractmethod
        def get_by_site(self, site_id: SiteId) -> Optional[CrawlConfig]:
            pass
    

* * *

## 3\. Tầng Infrastructure - Thiết kế Bảng & SQLite Thuần SQL

Vì cấu trúc của Value Objects (`HttpConfig` chứa Dictionary, `Selectors` chứa nhiều chuỗi), nếu tách thành quá nhiều bảng trong SQLite sẽ làm câu lệnh `JOIN` rất phức tạp.

Giải pháp tối ưu theo DDD khi dùng DB quan hệ cho Value Objects phức tạp là Serialize chúng thành JSON rồi lưu vào một cột văn bản (`TEXT`) trong SQLite. SQLite hỗ trợ các hàm xử lý JSON thuần SQL rất mạnh mẽ.

## Khởi tạo bảng (`infrastructure/database.py`)
    
    
    def init_config_db(cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crawl_configs (
                site_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                comic_selectors TEXT NOT NULL,   -- Lưu chuỗi JSON
                chapter_selectors TEXT NOT NULL, -- Lưu chuỗi JSON
                http_config TEXT NOT NULL,       -- Lưu chuỗi JSON
                is_active INTEGER NOT NULL DEFAULT 1
            )
        """)
    

## Triển khai Repository (`infrastructure/sqlite_config_repository.py`)

Sử dụng thư viện `json` của Python để chuyển đổi qua lại giữa Object và JSON trước khi chạy lệnh SQL.
    
    
    import sqlite3
    import json
    from typing import Optional
    from domain.crawler_config import CrawlConfig, SiteId, ComicSelectors, ChapterSelectors, HttpConfig
    from domain.config_repository import CrawlConfigRepository
    
    class SQLiteCrawlConfigRepository(CrawlConfigRepository):
        def __init__(self, db_path: str):
            self.db_path = db_path
    
        def _get_connection(self):
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            conn.execute("PRAGMA journal_mode=WAL;")
            return conn
    
        def save(self, config: CrawlConfig) -> None:
            conn = self._get_connection()
            cursor = conn.cursor()
    
            # Áp dụng kỹ thuật UPSERT (ON CONFLICT) đã học ở phần trước
            sql = """
                INSERT INTO crawl_configs (site_id, name, comic_selectors, chapter_selectors, http_config, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(site_id) DO UPDATE SET
                    name = excluded.name,
                    comic_selectors = excluded.comic_selectors,
                    chapter_selectors = excluded.chapter_selectors,
                    http_config = excluded.http_config,
                    is_active = excluded.is_active;
            """
    
            cursor.execute(sql, (
                config.site_id.value,
                config.name,
                json.dumps(config.comic_selectors.__dict__),     # Convert Object sang JSON String
                json.dumps(config.chapter_selectors.__dict__),   # Convert Object sang JSON String
                json.dumps(config.http_config.__dict__),          # Convert Object sang JSON String
                1 if config.is_active else 0
            ))
            conn.commit()
            conn.close()
    
        def get_by_site(self, site_id: SiteId) -> Optional[CrawlConfig]:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, comic_selectors, chapter_selectors, http_config, is_active FROM crawl_configs WHERE site_id = ?", 
                (site_id.value,)
            )
            row = cursor.fetchone()
            conn.close()
    
            if not row:
                return None
    
            # Parse dữ liệu JSON ngược lại thành các Domain Value Objects
            name, comic_json, chapter_json, http_json, is_active = row
            
            comic_data = json.loads(comic_json)
            chapter_data = json.loads(chapter_json)
            http_data = json.loads(http_json)
    
            return CrawlConfig(
                site_id=site_id,
                name=name,
                comic_selectors=ComicSelectors(**comic_data),
                chapter_selectors=ChapterSelectors(**chapter_data),
                http_config=HttpConfig(**http_data),
                is_active=bool(is_active)
            )
    

* * *

## 4\. Tách biệt logic và sử dụng trong Ứng dụng

Bây giờ, thay vì viết cứng (hardcode) các đoạn code BeautifulSoup cho từng trang web, bạn nạp cấu hình từ DB lên để cào dữ liệu một cách linh hoạt.
    
    
    from domain.crawler_config import SiteId, ComicSelectors, ChapterSelectors, HttpConfig, CrawlConfig
    from infrastructure.sqlite_config_repository import SQLiteCrawlConfigRepository
    import requests
    from bs4 import BeautifulSoup
    
    # 1. Cấu hình ban đầu cho trang TruyenFull và lưu vào DB
    config_repo = SQLiteCrawlConfigRepository("comics.db")
    
    truyenfull_config = CrawlConfig(
        site_id=SiteId("truyenfull.vn"),
        name="Truyện Full",
        comic_selectors=ComicSelectors(
            title_selector="h3.title",
            author_selector="a[itemprop='author']",
            description_selector="div.desc-text",
            chapter_list_selector="ul.list-chapter li a"
        ),
        chapter_selectors=ChapterSelectors(
            title_selector="a.chapter-title",
            content_selector="div.chapter-content"
        ),
        http_config=HttpConfig(
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
    )
    config_repo.save(truyenfull_config)
    
    
    # 2. Khi chạy Engine Crawler chính, ta chỉ cần gọi cấu hình động từ DB
    def crawl_engine(url: str):
        # Trích xuất domain từ URL để tìm cấu hình (ví dụ: https://truyenfull.vn -> truyenfull.vn)
        # Giả định lấy được domain_str = "truyenfull.vn"
        domain_str = "truyenfull.vn" 
        
        # Lấy cấu hình từ Domain Repository
        config = config_repo.get_by_site(SiteId(domain_str))
        if not config or not config.is_active:
            print("Không tìm thấy cấu hình cào hoặc cấu hình đã bị tắt!")
            return
    
        # Sử dụng cấu hình HTTP từ Domain Object
        response = requests.get(url, headers=config.http_config.headers, timeout=config.http_config.timeout_seconds)
        soup = BeautifulSoup(response.text, "html.parser")
    
        # Sử dụng các Selector động thuần SQL/JSON vừa lấy từ DB lên
        chapter_title = soup.select_one(config.chapter_selectors.title_selector).text
        chapter_content = soup.select_one(config.chapter_selectors.content_selector).text
    
        print(f"Đã cào thành công bằng Selector động: {chapter_title}")
    

## Giải pháp nâng cao: Truy vấn bằng hàm JSON thuần SQL của SQLite

Nhờ lưu trữ dưới dạng JSON, bạn có thể dùng các hàm build-in của SQLite để truy vấn trực tiếp vào bên trong cấu hình mà không cần nạp lên Python.  
Ví dụ: Bạn muốn tìm xem tất cả các site nào đang sử dụng proxy (`use_proxy = true`), bạn có thể chạy lệnh SQL sau:
    
    
    SELECT site_id, name FROM crawl_configs WHERE json_extract(http_config, '$.use_proxy') = 1;
    

Kiến trúc này giúp hệ thống crawl của bạn đạt mức độ bảo trì cực cao. Khi một trang web thay đổi giao diện, bạn không cần sửa code Python, không cần build lại hệ thống; bạn chỉ cần viết một câu lệnh `UPDATE` SQL cập nhật lại chuỗi JSON của `chapter_selectors` trong bảng `crawl_configs` là xong.

Để hoàn thiện toàn bộ hệ thống, bạn có muốn xây dựng tiếp cơ chế Crawl State / Progress Tracking (Lưu tiến độ cào) để nếu app đang cào dở bộ truyện 5000 chương mà bị mất mạng hoặc sập nguồn, khi bật lại nó sẽ tự động cào tiếp từ chương bị lỗi chứ không phải cào lại từ đầu không?