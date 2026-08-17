Để áp dụng Clean Architecture và DDD (Domain-Driven Design) cho một dự án Crawler, chúng ta sẽ tách biệt hoàn toàn phần cốt lõi nghiệp vụ (Domain, Use Cases) khỏi các chi tiết công nghệ (Database, CLI, Network/BeautifulSoup).

Dự án sẽ được chia thành 4 tầng độc lập theo nguyên lý Dependency Inversion (Tầng bên trong không phụ thuộc vào tầng bên ngoài):

  1. Domain Layer (Core): Chứa các Entity, Value Object và định nghĩa các Interface (Repository, Plugin Service). Không phụ thuộc bất kỳ thư viện nào.
  2. Application Layer: Chứa các Use Case (Nghiệp vụ điều khiển luồng dữ liệu như: Cào danh mục, Tải trọn bộ truyện).
  3. Infrastructure Layer: Chứa phần cài đặt thực tế (SQLite Repository, Cơ chế quét/Nạp động Plugin từ file cấu hình).
  4. Presentation/Interface Layer: Điểm vào của ứng dụng (Giao diện CLI sử dụng `click`).



* * *

## 1\. Cấu trúc thư mục chuẩn DDD & Clean Architecture

Bạn hãy khởi tạo cấu trúc thư mục như sau:
    
    
    novel_crawler/
    │
    ├── domain/                    # 1. TẦNG DOMAIN (Nghiệp vụ cốt lõi)
    │   ├── __init__.py
    │   ├── models.py              # Entities & Value Objects (Novel, Chapter, Listing)
    │   └── interfaces.py          # Interfaces cho Repositories & Plugin Crawler
    │
    ├── application/               # 2. TẦNG APPLICATION (Các kịch bản Use Case)
    │   ├── __init__.py
    │   └── use_cases.py           # DownloadNovelUseCase, CrawlListingUseCase...
    │
    ├── infrastructure/            # 3. TẦNG INFRASTRUCTURE (Chi tiết kỹ thuật)
    │   ├── __init__.py
    │   ├── database.py            # SQLite Implementation
    │   └── plugin_manager.py      # Bộ quản lý và nạp động các Plugin
    │
    ├── presentation/              # 4. TẦNG PRESENTATION (Giao diện người dùng)
    │   ├── __init__.py
    │   └── cli.py                 # Định nghĩa Click CLI lệnh và Thanh tiến trình
    │
    ├── plugins/                   # Thư mục chứa các plugin cào nguồn (Chi tiết kỹ thuật bên ngoài)
    │   ├── __init__.py
    │   └── truyenfull.py          # Cài đặt cụ thể cách bóc tách cho truyenfull.live
    │
    └── main.py                    # File khởi tạo và chạy ứng dụng
    

* * *

## 2\. Mã nguồn chi tiết theo các tầng

## 2.1. Tầng Domain (`domain/models.py` & `domain/interfaces.py`)

Đây là trung tâm của hệ thống. Nó định nghĩa cấu trúc dữ liệu và các quy ước mà không quan tâm bạn dùng database nào hay cào bằng thư viện gì.
    
    
    # domain/models.py
    from dataclasses import dataclass
    from typing import Optional
    
    @dataclass
    class NovelListing:
        category_url: str
        title: str
        author: str
        novel_url: str
    
    @dataclass
    class Novel:
        novel_url: str
        title: str
        author: str
        description: str
        source: str
    
    @dataclass
    class Chapter:
        chapter_url: str
        novel_url: str
        chapter_title: str
        content: Optional[str] = None
    
    
    
    # domain/interfaces.py
    from abc import ABC, abstractmethod
    from typing import List, Optional
    from domain.models import NovelListing, Novel, Chapter
    
    class INovelRepository(ABC):
        """Bắt buộc tầng Infrastructure triển khai lưu trữ Database"""
        @abstractmethod
        def init_storage(self) -> None: pass
        @abstractmethod
        def save_listing(self, item: NovelListing) -> None: pass
        @abstractmethod
        def save_novel(self, novel: Novel) -> None: pass
        @abstractmethod
        def save_chapter(self, chapter: Chapter) -> None: pass
        @abstractmethod
        def is_chapter_downloaded(self, chapter_url: str) -> bool: pass
    
    class INovelPlugin(ABC):
        """Bắt buộc các Plugin nguồn truyện bên ngoài phải triển khai theo chuẩn này"""
        DOMAIN: str
        @abstractmethod
        def fetch_soup(self, url: str) -> Optional[any]: pass
        @abstractmethod
        def clean_url(self, url: str) -> str: pass
        @abstractmethod
        def build_page_url(self, base_url: str, page_num: Optional[int]) -> str: pass
        @abstractmethod
        def extract_total_pages(self, soup: any) -> int: pass
        @abstractmethod
        def parse_listing(self, soup: any) -> List[dict]: pass
        @abstractmethod
        def parse_novel_info(self, soup: any) -> dict: pass
        @abstractmethod
        def parse_chapter_list(self, soup: any) -> List[dict]: pass
        @abstractmethod
        def parse_chapter_content(self, soup: any, url: str) -> dict: pass
    

## 2.2. Tầng Application (`application/use_cases.py`)

Chứa các luồng nghiệp vụ lớn (Pure logic). Tầng này nhận vào các Repository và Plugin dưới dạng interface (Dependency Injection) để điều khiển luồng.
    
    
    # application/use_cases.py
    import time
    from typing import Callable, Optional
    from domain.interfaces import INovelRepository, INovelPlugin
    from domain.models import NovelListing, Novel, Chapter
    
    class CrawlListingUseCase:
        def __init__(self, repo: INovelRepository, plugin: INovelPlugin):
            self.repo = repo
            self.plugin = plugin
    
        def execute(self, url: str, page: Optional[int], total_page_only: bool) -> Optional[int]:
            target_url = self.plugin.build_page_url(url, page)
            soup = self.plugin.fetch_soup(target_url)
            if not soup: return None
    
            total_pages = self.plugin.extract_total_pages(soup)
            if total_page_only:
                return total_pages
    
            raw_items = self.plugin.parse_listing(soup)
            for item in raw_items:
                listing = NovelListing(
                    category_url=self.plugin.clean_url(url),
                    title=item['title'],
                    author=item['author'],
                    novel_url=item['url']
                )
                self.repo.save_listing(listing)
            return total_pages
    
    class DownloadAllChaptersUseCase:
        def __init__(self, repo: INovelRepository, plugin: INovelPlugin):
            self.repo = repo
            self.plugin = plugin
    
        def execute(self, url: str, progress_callback: Callable[[int, int, str], None]) -> None:
            novel_url = self.plugin.clean_url(url)
            
            # 1. Cào thông tin truyện
            soup = self.plugin.fetch_soup(novel_url)
            if not soup: return
            info = self.plugin.parse_novel_info(soup)
            novel_domain_model = Novel(
                novel_url=novel_url, title=info['title'],
                author=info['author'], description=info['description'],
                source=self.plugin.DOMAIN
            )
            self.repo.save_novel(novel_domain_model)
            
            # 2. Quét tất cả link chương từ các trang phân trang
            total_pages = self.plugin.extract_total_pages(soup)
            all_chapters_meta = []
            for p in range(1, total_pages + 1):
                p_url = self.plugin.build_page_url(novel_url, p if p > 1 else None)
                p_soup = self.plugin.fetch_soup(p_url)
                if p_soup:
                    all_chapters_meta.extend(self.plugin.parse_chapter_list(p_soup))
            
            total_chaps = len(all_chapters_meta)
            
            # 3. Tải nội dung từng chương (Tích hợp tính năng tự bỏ qua nếu đã tải - Resume)
            for index, chap_meta in enumerate(all_chapters_meta, 1):
                chap_url = self.plugin.clean_url(chap_meta['url'])
                
                # Thông báo trạng thái ra giao diện thông qua Callback
                progress_callback(index, total_chaps, chap_meta['title'])
                
                if self.repo.is_chapter_downloaded(chap_url):
                    time.sleep(0.05) # Lướt nhanh qua nếu đã có dữ liệu
                    continue
                    
                c_soup = self.plugin.fetch_soup(chap_url)
                if c_soup:
                    c_data = self.plugin.parse_chapter_content(c_soup, chap_url)
                    chapter_domain_model = Chapter(
                        chapter_url=chap_url,
                        novel_url=novel_url,
                        chapter_title=c_data['title'],
                        content=c_data['content']
                    )
                    self.repo.save_chapter(chapter_domain_model)
                time.sleep(0.3)
    

## 2.3. Tầng Infrastructure (`infrastructure/database.py` & `infrastructure/plugin_manager.py`)

Nơi cài đặt thực tế công nghệ SQLite3 và cách quét file tìm Plugin.
    
    
    # infrastructure/database.py
    import sqlite3
    from domain.interfaces import INovelRepository
    from domain.models import NovelListing, Novel, Chapter
    
    class SQLiteNovelRepository(INovelRepository):
        def __init__(self, db_name: str = "truyenfull.db"):
            self.db_name = db_name
    
        def init_storage(self) -> None:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS listings (id INTEGER PRIMARY KEY AUTOINCREMENT, category_url TEXT, title TEXT, author TEXT, novel_url TEXT UNIQUE)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS novels (novel_url TEXT PRIMARY KEY, title TEXT, author TEXT, description TEXT, source TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS chapters (chapter_url TEXT PRIMARY KEY, novel_url TEXT, chapter_title TEXT, content TEXT)''')
            conn.commit()
            conn.close()
    
        def save_listing(self, item: NovelListing) -> None:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO listings (category_url, title, author, novel_url) VALUES (?, ?, ?, ?)', 
                           (item.category_url, item.title, item.author, item.novel_url))
            conn.commit()
            conn.close()
    
        def save_novel(self, novel: Novel) -> None:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO novels (novel_url, title, author, description, source) VALUES (?, ?, ?, ?, ?)', 
                           (novel.novel_url, novel.title, novel.author, novel.description, novel.source))
            conn.commit()
            conn.close()
    
        def save_chapter(self, chapter: Chapter) -> None:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO chapters (chapter_url, novel_url, chapter_title, content) VALUES (?, ?, ?, ?)', 
                           (chapter.chapter_url, chapter.novel_url, chapter.chapter_title, chapter.content))
            conn.commit()
            conn.close()
    
        def is_chapter_downloaded(self, chapter_url: str) -> bool:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM chapters WHERE chapter_url = ? AND content IS NOT NULL', (chapter_url,))
            res = cursor.fetchone()
            conn.close()
            return res is not None
    
    
    
    # infrastructure/plugin_manager.py
    import os
    import importlib
    from urllib.parse import urlparse
    from domain.interfaces import INovelPlugin
    
    class PluginManager:
        def __init__(self):
            self._plugins = {}
            self._load_all_plugins()
    
        def _load_all_plugins(self):
            plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins')
            if not os.path.exists(plugins_dir): return
            
            for file in os.listdir(plugins_dir):
                if file.endswith('.py') and file != '__init__.py':
                    module_name = f"plugins.{file[:-3]}"
                    module = importlib.import_module(module_name)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, INovelPlugin) and attr.DOMAIN:
                            self._plugins[attr.DOMAIN] = attr()
    
        def get_plugin_for_url(self, url: str) -> INovelPlugin:
            domain = urlparse(url).netloc.replace('www.', '')
            if domain in self._plugins:
                return self._plugins[domain]
            raise ValueError(f"Không tìm thấy Plugin phù hợp cho nguồn: {domain}")
    

## 2.4. Phần Plugins bên ngoài (`plugins/truyenfull.py`)

File này kế thừa trực tiếp từ `INovelPlugin` của Domain Layer. Bạn có thể viết thêm các file tương tự cho các website khác tại thư mục này.
    
    
    # plugins/truyenfull.py
    import re
    import requests
    from bs4 import BeautifulSoup
    from domain.interfaces import INovelPlugin
    
    class TruyenFullPlugin(INovelPlugin):
        DOMAIN = "truyenfull.live"
    
        def fetch_soup(self, url: str):
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            try:
                res = requests.get(url, headers=headers, timeout=10)
                return BeautifulSoup(res.text, 'html.parser') if res.status_code == 200 else None
            except Exception: return None
    
        def clean_url(self, url: str) -> str:
            return url if url.endswith('/') else f"{url}/"
    
        def build_page_url(self, base_url: str, page_num: int) -> str:
            base_url = self.clean_url(base_url)
            return f"{base_url}trang-{page_num}/" if page_num else base_url
    
        def extract_total_pages(self, soup) -> int:
            if not soup: return 1
            pagination = soup.find('ul', class_='pagination')
            if not pagination: return 1
            last_li = pagination.find('li', class_='last')
            if last_li and last_li.find('a'):
                if match := re.search(r'trang-(\d+)', last_li.find('a')['href']): return int(match.group(1))
            pages = [int(m.group(1)) for a in pagination.find_all('a') if (m := re.search(r'trang-(\d+)', a.get('href', '')))]
            return max(pages) if pages else 1
    
        def parse_listing(self, soup):
            results = []
            items = soup.find_all('div', class_='row', itemtype='https://schema.org') or soup.select('.list-truyen .row')
            for item in items:
                title_el = item.find('h3', class_='truyen-title') or item.find('a')
                if not title_el: continue
                a_tag = title_el.find('a') if title_el.name != 'a' else title_el
                auth_el = item.find('span', class_='author')
                results.append({
                    'title': a_tag.text.strip() if a_tag else "Không rõ",
                    'url': self.clean_url(a_tag['href']) if a_tag else "",
                    'author': auth_el.text.strip() if auth_el else "Không rõ"
                })
            return results
    
        def parse_novel_info(self, soup):
            title = soup.find('h3', class_='title').text.strip() if soup.find('h3', class_='title') else "Không rõ"
            info_div = soup.find('div', class_='info')
            author = info_div.find('a', itemtype='https://schema.org').text.strip() if (info_div and info_div.find('a', itemtype='https://schema.org')) else "Không rõ"
            desc_div = soup.find('div', class_='desc-text')
            return {'title': title, 'author': author, 'description': desc_div.text.strip() if desc_div else "Không có mô tả"}
    
        def parse_chapter_list(self, soup):
            results = []
            if list_div := soup.find('ul', class_='list-chapter'):
                for li in list_div.find_all('li'):
                    if a := li.find('a'): results.append({'title': a.text.strip(), 'url': self.clean_url(a['href'])})
            return results
    
        def parse_chapter_content(self, soup, url):
            title = soup.find('a', class_='chapter-title') or soup.find('span', class_='chapter-title')
            content_div = soup.find('div', class_='chapter-c') or soup.find('div', id='chapter-c')
            if content_div:
                for ads in content_div.find_all(['div', 'ins', 'script']): ads.decompose()
                text = content_div.get_text('\n').strip()
            else: text = "Không tìm thấy nội dung."
            return {'title': title.text.strip() if title else "Không rõ", 'content': text, 'novel_url': re.sub(r'chuong-[\d\.]+/$', '', url)}
    

## 2.5. Tầng Presentation (`presentation/cli.py`)

Tầng này chỉ chịu trách nhiệm hiển thị UI (Click commands và progressbar) và gọi Use Case.
    
    
    # presentation/cli.py
    import click
    import sys
    from infrastructure.database import SQLiteNovelRepository
    from infrastructure.plugin_manager import PluginManager
    from application.use_cases import CrawlListingUseCase, DownloadAllChaptersUseCase
    
    # Khởi tạo các thành phần hạ tầng (Dependency Injection container thủ công)
    repo = SQLiteNovelRepository()
    plugin_manager = PluginManager()
    
    @click.group()
    def cli():
        """Hệ thống CLI crawl truyện thiết kế theo Clean Architecture & DDD."""
        repo.init_storage()
    
    @cli.command(name="listing")
    @click.argument("url")
    @click.option("--page", type=int, help="Chỉ định trang")
    @click.option("--total-page", is_flag=True, help="Chỉ xem tổng số trang")
    def cmd_listing(url, page, total_page):
        """Cào danh mục truyện."""
        try:
            plugin = plugin_manager.get_plugin_for_url(url)
            use_case = CrawlListingUseCase(repo, plugin)
            
            result = use_case.execute(url, page, total_page)
            if total_page:
                click.echo(f"Tổng số trang danh mục: {result}")
            else:
                click.echo("Đã cào danh sách truyện thành công và lưu vào SQLite3!")
        except Exception as e:
            click.echo(f"[Lỗi]: {e}", err=True)
    
    @cli.command(name="download-all")
    @click.argument("url")
    def cmd_download_all(url):
        """Treo máy tự động tải trọn bộ truyện với thanh tiến trình trực quan."""
        try:
            plugin = plugin_manager.get_plugin_for_url(url)
            use_case = DownloadAllChaptersUseCase(repo, plugin)
            
            click.echo("Đang phân tích cấu trúc truyện và khởi tạo tác vụ...")
            
            # Khởi tạo thanh tiến trình rỗng trước, cập nhật động qua hàm callback
            with click.progressbar(length=100, label="Tiến độ tải truyện", show_pos=True, item_show_func=lambda name: name if name else '') as bar:
                
                def on_progress(current: int, total: int, chapter_title: str):
                    bar.length = total             # Cập nhật tổng số chương thực tế
                    bar.update(current - bar.pos) # Tăng tiến trình dựa trên độ lệch vị trí
                    bar.item_show_func = lambda _: f"({current}/{total}) {chapter_title}"
    
                use_case.execute(url, progress_callback=on_progress)
                
            click.echo("\n--- Hoàn thành tác vụ tải truyện sạch sẽ, an toàn vào SQLite3! ---")
        except Exception as e:
            click.echo(f"[Lỗi]: {e}", err=True)
    

## 2.6. Điểm kích hoạt ứng dụng (`main.py`)
    
    
    # main.py
    from presentation.cli import cli
    
    if __name__ == "__main__":
        cli()
    

* * *

## 3\. Hướng dẫn chạy kiểm thử hệ thống mới

Tất cả các câu lệnh điều hướng giờ đây đã tuân theo cấu trúc phân rã Clean / DDD vô cùng tường minh:

  * Để cào dữ liệu Listing:
        
        python main.py listing "https://truyenfull.live"
        

  * Để xem tổng số trang Listing:
        
        python main.py listing "https://truyenfull.live" --total-page
        

  * Để kích hoạt Use Case tải trọn bộ (Có Resume + ProgressBar):
        
        python main.py download-all "https://truyenfull.live"
        




## Điểm mạnh của kiến trúc mới này:

  1. Dễ test độc lập: Bạn có thể viết Unit Test cho `DownloadAllChaptersUseCase` bằng cách truyền vào các MockRepository và MockPlugin (không cần mạng thật, không cần DB thật).
  2. Khả năng hoán đổi hạ tầng cao: Ngày mai nếu bạn không thích lưu SQLite3 mà muốn chuyển sang MongoDB hoặc PostgreSQL, bạn chỉ cần tạo file `infrastructure/postgres_database.py` kế thừa từ `INovelRepository` và thay thế nó ở file `cli.py` là xong. Phần Core Application giữ nguyên 100%.



Bạn có cần tôi hướng dẫn cách viết tiếp một file Unit Test mẫu để kiểm thử Use Case tải truyện bằng phương pháp Mocking nhằm làm chủ hoàn toàn tư duy Clean Architecture này không?