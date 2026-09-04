Để thiết kế một ứng dụng crawl truyện có cấu trúc phức tạp gồm Listing Novel (Danh sách truyện), Novel Detail (Chi tiết truyện), Chapter List (Danh sách chương) và Chapter Detail (Nội dung chương) theo chuẩn DDD (Domain-Driven Design), chúng ta cần phân chia hệ thống thành các Bounded Context rõ ràng, sau đó áp dụng SOLID để thiết kế các class.

Dưới đây là bản thiết kế chi tiết từ kiến trúc chiến lược (Strategic Design) đến mã nguồn triển khai bằng Python (đồng bộ, hỗ trợ SQL thuần, Mongo, File).

* * *

## 🗺️ 1. Thiết kế Bounded Context (DDD Strategic Design)

Đối với một hệ thống crawl, chúng ta sẽ chia làm 2 Bounded Context chính dựa trên ranh giới nghiệp vụ và dữ liệu:

  1. Crawl Catalog Context (Bối cảnh Danh mục truyện):

     * Nhiệm vụ: Tìm kiếm, quét danh sách truyện (`Listing Novel`) từ các trang nguồn và lấy thông tin tổng quan của từng truyện (`Novel Detail`).
     * Core Entities: `SourceSite`, `NovelMetadata`.

  2. Crawl Content Context (Bối cảnh Nội dung truyện):

     * Nhiệm vụ: Đi sâu vào một truyện cụ thể để cào danh sách chương (`Chapter List`) và nội dung chi tiết từng chương (`Chapter Detail`).
     * Core Entities: `ChapterMetadata`, `ChapterContent`.




> Mối quan hệ (Context Mapping): `Catalog Context` sẽ chạy trước để định danh truyện và lấy URL, sau đó đẩy thông tin (hoặc URL truyện) sang `Content Context` để cào chi tiết chương. Chúng giao tiếp với nhau qua Domain Events hoặc qua lớp Application Coordinator (Điều phối viên).

* * *

## 🧱 2. Kiến Trúc Thư Mục và Mã Nguồn Triển Khai (SOLID)

Để xử lý cấu trúc dữ liệu phân cấp lớn này, chúng ta sẽ tối ưu hóa Domain Models thành các thực thể nhỏ gọn để tránh việc load nguyên một cuốn truyện nặng hàng ngàn chương vào bộ nhớ cùng một lúc (gây nghẽn I/O và RAM).

## 📁 Cấu trúc thư mục
    
    
    src/
    ├── domain/
    │   ├── models.py            # Chứa các Domain Models (Listing, Detail, Chapter...)
    │   └── services.py          # Interfaces (HttpClient, Repository, UoW)
    ├── infrastructure/
    │   ├── http_client.py       # RequestsHttpClient
    │   ├── parsers.py           # Bộ phân tích HTML thành các đối tượng tương ứng
    │   └── repositories/
    │       ├── sqlite_repo.py   # Triển khai SQL thuần
    │       ├── mongo_repo.py    # Triển khai MongoDB
    │       └── file_repo.py     # Triển khai FileLocalRepository
    └── main.py
    

* * *

## 💻 Lớp Domain (`src/domain/models.py` & `services.py`)

Tuân thủ Single Responsibility (S) và Dependency Inversion (D). Các Model được chia nhỏ tương ứng với 4 thành phần bạn yêu cầu.
    
    
    # src/domain/models.py
    from dataclasses import dataclass
    from typing import List, Optional
    
    @dataclass(frozen=True)
    class PageSource:
        url: str
        content: str
    
    # 1. Listing Novel Model
    @dataclass(frozen=True)
    class NovelListItem:
        title: str
        novel_url: str
        cover_image_url: Optional[str] = None
    
    # 2. Novel Detail Model
    @dataclass
    class NovelDetail:
        title: str
        author: str
        description: str
        novel_url: str
        genres: List[str]
    
    # 3. Chapter List Model (Chỉ chứa thông tin định danh chương)
    @dataclass(frozen=True)
    class ChapterItem:
        title: str
        chapter_url: str
        order_index: int
    
    # 4. Chapter Detail Model (Chứa nội dung chữ rất nặng)
    @dataclass
    class ChapterDetail:
        novel_url: str
        chapter_url: str
        title: str
        content: str  # Nội dung chữ của truyện
    
    
    
    # src/domain/services.py
    from abc import ABC, abstractmethod
    from typing import List
    from src.domain.models import PageSource, NovelListItem, NovelDetail, ChapterItem, ChapterDetail
    
    class HttpClientInterface(ABC):
        @abstractmethod
        def fetch(self, url: str) -> PageSource: pass
    
    class NovelParserInterface(ABC):
        """Interface chịu trách nhiệm bóc tách HTML (SOLID - I)"""
        @abstractmethod
        def parse_listing(self, source: PageSource) -> List[NovelListItem]: pass
        
        @abstractmethod
        def parse_detail(self, source: PageSource) -> NovelDetail: pass
        
        @abstractmethod
        def parse_chapter_list(self, source: PageSource) -> List[ChapterItem]: pass
        
        @abstractmethod
        def parse_chapter_detail(self, source: PageSource) -> ChapterDetail: pass
    
    class NovelRepositoryInterface(ABC):
        """Bản hợp đồng lưu trữ dữ liệu (DDD - Repository)"""
        @abstractmethod
        def save_listing(self, items: List[NovelListItem]) -> None: pass
        @abstractmethod
        def save_novel_detail(self, detail: NovelDetail) -> None: pass
        @abstractmethod
        def save_chapters(self, novel_url: str, chapters: List[ChapterItem]) -> None: pass
        @abstractmethod
        def save_chapter_detail(self, detail: ChapterDetail) -> None: pass
    

* * *

## 💻 Lớp Hạ Tầng - Triển Khai Bộ Parser (`src/infrastructure/parsers.py`)

Mỗi hàm trong Parser chỉ giải quyết đúng một nhiệm vụ (Single Responsibility).
    
    
    # src/infrastructure/parsers.py
    from bs4 import BeautifulSoup
    from typing import List
    from src.domain.services import NovelParserInterface
    from src.domain.models import PageSource, NovelListItem, NovelDetail, ChapterItem, ChapterDetail
    
    class TruyenFullParser(NovelParserInterface):
        """Mẫu Parser cụ thể cho một Site truyện"""
        
        def parse_listing(self, source: PageSource) -> List[NovelListItem]:
            soup = BeautifulSoup(source.content, 'html.parser')
            items = []
            # Giả lập bóc tách danh sách truyện từ trang chủ/thể loại
            for row in soup.find_all('div', class_='row-novel') or []:
                items.append(NovelListItem(
                    title=row.find('h3').text.strip(),
                    novel_url=row.find('a')['href']
                ))
            return items
    
        def parse_detail(self, source: PageSource) -> NovelDetail:
            soup = BeautifulSoup(source.content, 'html.parser')
            return NovelDetail(
                title=soup.find('h3', class_='title').text.strip() if soup.find('h3', class_='title') else "Unknown",
                author="Tác giả X",
                description="Mô tả truyện...",
                novel_url=source.url,
                genres=["Tiên Hiệp", "Huyền Huyễn"]
            )
    
        def parse_chapter_list(self, source: PageSource) -> List[ChapterItem]:
            soup = BeautifulSoup(source.content, 'html.parser')
            chapters = []
            for idx, li in enumerate(soup.find_all('ul', class_='list-chapter') or []):
                chapters.append(ChapterItem(
                    title=li.find('a').text.strip(),
                    chapter_url=li.find('a')['href'],
                    order_index=idx + 1
                ))
            return chapters
    
        def parse_chapter_detail(self, source: PageSource) -> ChapterDetail:
            soup = BeautifulSoup(source.content, 'html.parser')
            return ChapterDetail(
                novel_url="https://site.com",
                chapter_url=source.url,
                title="Chương 1: Mở Đầu",
                content="Nội dung chữ rất dài của chương truyện cào được ở đây..."
            )
    

* * *

## 💻 Lớp Hạ Tầng - Triển Khai 3 Loại Repository (`src/infrastructure/repositories/`)

Nhờ tính chất Liskov Substitution (L), cả 3 kho lưu trữ dưới đây đều tuân thủ nghiêm ngặt cấu trúc dữ liệu mới mà không làm phá vỡ logic Core.

## 🔹 1. Triển Khai FileLocalRepository (Lưu cấu trúc thư mục)

Ghi dữ liệu thành dạng file cấu trúc phân cấp: `thư_mục_gốc/tên-truyen/detail.json`, `chapters.json`, và một thư mục con `chapters/` chứa nội dung chi tiết từng chương nhằm tối ưu dung lượng đọc/ghi ổ đĩa.
    
    
    # src/infrastructure/repositories/file_repo.py
    import os
    import json
    import re
    from src.domain.services import NovelRepositoryInterface
    from src.domain.models import NovelListItem, NovelDetail, ChapterItem, ChapterDetail
    
    class FileLocalRepository(NovelRepositoryInterface):
        def __init__(self, base_dir: str):
            self.base_dir = base_dir
            if not os.path.exists(base_dir): os.makedirs(base_dir)
    
        def _slugify(self, text: str) -> str:
            return re.sub(r'[\s-]+', '-', re.sub(r'[^a-z0-9\s-]', '', text.lower())).strip('-')
    
        def save_listing(self, items: List[NovelListItem]) -> None:
            path = os.path.join(self.base_dir, "listing_novels.json")
            data = [{"title": i.title, "url": i.novel_url} for i in items]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
    
        def save_novel_detail(self, detail: NovelDetail) -> None:
            novel_dir = os.path.join(self.base_dir, self._slugify(detail.title))
            os.makedirs(novel_dir, exist_ok=True)
            with open(os.path.join(novel_dir, "detail.json"), "w", encoding="utf-8") as f:
                json.dump(detail.__dict__, f, ensure_ascii=False, indent=4)
    
        def save_chapters(self, novel_url: str, chapters: List[ChapterItem]) -> None:
            # Trong thực tế sẽ tìm thư mục dựa trên novel_url, ở đây làm đơn giản hóa cấu trúc đặt tên
            novel_dir = os.path.join(self.base_dir, "cached-novel-by-url")
            os.makedirs(novel_dir, exist_ok=True)
            data = [{"title": c.title, "url": c.chapter_url, "index": c.order_index} for c in chapters]
            with open(os.path.join(novel_dir, "chapters_list.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
    
        def save_chapter_detail(self, detail: ChapterDetail) -> None:
            novel_dir = os.path.join(self.base_dir, "cached-novel-by-url", "chapters")
            os.makedirs(novel_dir, exist_ok=True)
            file_name = f"{self._slugify(detail.title)}.txt"
            with open(os.path.join(novel_dir, file_name), "w", encoding="utf-8") as f:
                f.write(f"--- {detail.title} ---\n\n{detail.content}")
    

## 🔹 2. Triển Khai SQLite3 (SQL Thuần với quan hệ bảng tách biệt)

Chia dữ liệu ra thành 4 bảng: `novel_listings`, `novels`, `chapter_metadata`, `chapter_contents` để thực hiện câu lệnh SQL thuần.
    
    
    # src/infrastructure/repositories/sqlite_repo.py
    import sqlite3
    from src.domain.services import NovelRepositoryInterface
    from src.domain.models import NovelListItem, NovelDetail, ChapterItem, ChapterDetail
    
    class SqliteNovelRepository(NovelRepositoryInterface):
        def __init__(self, db_path: str):
            self.db_path = db_path
            self._init_db()
    
        def _init_db(self):
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("CREATE TABLE IF NOT EXISTS novel_listings (title TEXT, url TEXT UNIQUE)")
                c.execute("CREATE TABLE IF NOT EXISTS novels (title TEXT, author TEXT, description TEXT, url TEXT UNIQUE)")
                c.execute("CREATE TABLE IF NOT EXISTS chapter_metadata (novel_url TEXT, title TEXT, url TEXT UNIQUE, idx INTEGER)")
                c.execute("CREATE TABLE IF NOT EXISTS chapter_contents (chapter_url TEXT UNIQUE, content TEXT)")
                conn.commit()
    
        def save_listing(self, items: List[NovelListItem]) -> None:
            with sqlite3.connect(self.db_path) as conn:
                conn.executemany(
                    "INSERT OR IGNORE INTO novel_listings VALUES (?, ?)",
                    [(i.title, i.novel_url) for i in items]
                )
    
        def save_novel_detail(self, detail: NovelDetail) -> None:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO novels VALUES (?, ?, ?, ?)",
                    (detail.title, detail.author, detail.description, detail.novel_url)
                )
    
        def save_chapters(self, novel_url: str, chapters: List[ChapterItem]) -> None:
            with sqlite3.connect(self.db_path) as conn:
                conn.executemany(
                    "INSERT OR IGNORE INTO chapter_metadata VALUES (?, ?, ?, ?)",
                    [(novel_url, c.title, c.chapter_url, c.order_index) for c in chapters]
                )
    
        def save_chapter_detail(self, detail: ChapterDetail) -> None:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO chapter_contents VALUES (?, ?)",
                    (detail.chapter_url, detail.content)
                )
    

## 🔹 3. Triển Khai MongoDB Repository

Lưu trữ dạng Document lồng nhau linh hoạt.
    
    
    # src/infrastructure/repositories/mongo_repo.py
    from pymongo import MongoClient
    from src.domain.services import NovelRepositoryInterface
    from src.domain.models import NovelListItem, NovelDetail, ChapterItem, ChapterDetail
    
    class MongoNovelRepository(NovelRepositoryInterface):
        def __init__(self, connection_string: str, db_name: str):
            self.client = MongoClient(connection_string)
            self.db = self.client[db_name]
    
        def save_listing(self, items: List[NovelListItem]):
            self.db["listings"].insert_many([i.__dict__ for i in items], ordered=False)
    
        def save_novel_detail(self, detail: NovelDetail):
            self.db["novels"].update_one({"novel_url": detail.novel_url}, {"$set": detail.__dict__}, upsert=True)
    
        def save_chapters(self, novel_url: str, chapters: List[ChapterItem]):
            list_data = [c.__dict__ for c in chapters]
            self.db["novels"].update_one({"novel_url": novel_url}, {"$set": {"chapters_list": list_data}}, upsert=True)
    
        def save_chapter_detail(self, detail: ChapterDetail):
            self.db["chapters_content"].update_one({"chapter_url": detail.chapter_url}, {"$set": detail.__dict__}, upsert=True)
    

* * *

## 🎮 3. Lớp Điều Phối Ứng Dụng (`src/main.py`)

Lớp dịch vụ ứng dụng kết nối tất cả các thành phần lại với nhau để chạy quy trình cào tuần tự từ Listing -> Detail -> Chapter List -> Chapter Detail.
    
    
    # src/main.py
    from src.infrastructure.http_client import RequestsHttpClient
    from src.infrastructure.parsers import TruyenFullParser
    from src.infrastructure.repositories.sqlite_repo import SqliteNovelRepository
    from src.infrastructure.repositories.file_repo import FileLocalRepository
    from src.domain.models import PageSource
    
    class SuperNovelCrawlerApp:
        """Ứng dụng điều phối quy trình cào toàn diện theo mô hình DDD"""
        def __init__(self, http_client, parser, repository):
            self.client = http_client
            self.parser = parser
            self.repo = repository
    
        def execute_full_crawl(self, seed_url: str):
            print(f"🕵️ Bắt đầu quét Listing từ: {seed_url}")
            # 1. Crawl & Save Listing
            source = self.client.fetch(seed_url)
            listings = self.parser.parse_listing(source)
            self.repo.save_listing(listings)
            
            if not listings:
                print("⚠️ Không tìm thấy danh sách truyện.")
                return
    
            # Lấy thử truyện đầu tiên trong danh sách để cào sâu vào chi tiết
            target_novel = listings[0]
            print(f"📖 Tiến hành cào thông tin chi tiết truyện: {target_novel.title}")
            
            # 2. Crawl Novel Detail
            detail_source = self.client.fetch(target_novel.novel_url)
            detail = self.parser.parse_detail(detail_source)
            self.repo.save_novel_detail(detail)
    
            # 3. Crawl Chapter List
            print(f"📜 Quét danh sách chương của truyện...")
            chapters_source = self.client.fetch(target_novel.novel_url + "/chapters")
            chapters = self.parser.parse_chapter_list(chapters_source)
            self.repo.save_chapters(detail.novel_url, chapters)
    
            # 4. Crawl Chapter Detail (Cào nội dung chương cụ thể)
            if chapters:
                target_chapter = chapters[0]
                print(f"📝 Đang tải nội dung: {target_chapter.title}")
                chapter_detail_source = self.client.fetch(target_chapter.chapter_url)
                chapter_detail = self.parser.parse_chapter_detail(chapter_detail_source)
                self.repo.save_chapter_detail(chapter_detail)
    
    if __name__ == "__main__":
        # Bạn có thể dễ dàng hoán đổi Repository tại đây (SOLID - O/L/D)
        # Cách 1: Lưu SQL thuần
        chosen_repo = SqliteNovelRepository(db_path="perfect_novel.db")
        
        # Cách 2: Lưu File cục bộ tách biệt
        # chosen_repo = FileLocalRepository(base_dir="novel_storage")
    
        app = SuperNovelCrawlerApp(
            http_client=RequestsHttpClient(),
            parser=TruyenFullParser(),
            repository=chosen_repo
        )
        
        # Chạy thử quy trình cào đồng bộ bảo mật toàn vẹn cấu trúc
        app.execute_full_crawl("https://truyenfull.vn")
        print("🚀 Quy trình cào dữ liệu theo cấu trúc DDD hoàn thành tốt đẹp!")
    

* * *

## 🏆 Điểm cốt lõi đạt được trong thiết kế này:

  1. Chia nhỏ Model để tối ưu hóa bộ nhớ: Thay vì gom tất cả chương và nội dung chữ vào một object `Novel` duy nhất như thiết kế ban đầu, hệ thống đã bóc tách thành `NovelDetail`, `ChapterItem` (chỉ chứa metadata nhẹ) và `ChapterDetail` (chứa nội dung chữ rất nặng). Việc này giúp ứng dụng không bị tràn RAM khi xử lý các bộ truyện dài hàng nghìn chương.
  2. Tuân thủ Bounded Context: Tách biệt rõ ràng luồng nghiệp vụ quét danh mục (`Listing/Detail`) khỏi luồng tải nội dung chuyên sâu (`Chapter Detail`). Bản hợp đồng `NovelRepositoryInterface` quản lý dữ liệu đầu ra riêng biệt, giúp bạn dễ dàng scale up ứng dụng sau này.



Nếu bạn cần mở rộng thêm các tính năng nâng cao, hãy cho tôi biết:

  * Bạn có muốn thêm cấu trúc Factory Pattern để tự động nhận diện URL và chọn đúng `Parser` tương ứng cho từng site truyện không?
  * Bạn có cần xây dựng thêm lớp DTO (Data Transfer Object) để validate dữ liệu HTML trước khi đưa vào Domain Model không?