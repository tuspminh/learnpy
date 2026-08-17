Để có thể cào dữ liệu từ nhiều nguồn khác nhau (như `truyenfull.live`, `truyenchu.vn`, `tangthuvien.net`...), giải pháp tối ưu nhất là chuyển đổi mã nguồn sang cấu trúc Plugin (hoặc Adapter Pattern).

Với cấu trúc này, phần lõi CLI và Database sẽ giữ nguyên. Khi muốn thêm một trang web mới, bạn chỉ cần tạo một file plugin riêng cho trang đó và định nghĩa cách bóc tách HTML, hệ thống sẽ tự động nhận diện dựa trên Domain của URL truyền vào.

Dưới đây là cấu trúc thư mục và mã nguồn hoàn chỉnh của hệ thống.

* * *

## 1\. Cấu trúc thư mục dự án

Bạn hãy tạo các thư mục và file theo cấu trúc sau:
    
    
    novel_crawler/
    │
    ├── database.py         # Quản lý khởi tạo và lưu trữ SQLite3
    ├── crawler.py          # File chạy CLI chính (Core)
    │
    └── plugins/            # Thư mục chứa các plugin nguồn truyện
        ├── __init__.py     # File đánh dấu package và tự động load plugin
        ├── base_plugin.py  # Lớp cơ sở (Interface) định nghĩa các hàm bắt buộc
        └── truyenfull.py   # Plugin riêng cho trang truyenfull.live
    

* * *

## 2\. Mã nguồn chi tiết từng File

## File 1: `database.py` (Quản lý SQLite3)
    
    
    import sqlite3
    
    DB_NAME = "truyenfull.db"
    
    def init_db():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_url TEXT,
                title TEXT,
                author TEXT,
                novel_url TEXT UNIQUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS novels (
                novel_url TEXT PRIMARY KEY,
                title TEXT,
                author TEXT,
                description TEXT,
                source TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chapters (
                chapter_url TEXT PRIMARY KEY,
                novel_url TEXT,
                chapter_title TEXT,
                content TEXT,
                FOREIGN KEY (novel_url) REFERENCES novels (novel_url)
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_listing_item(category_url, title, author, novel_url):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT OR REPLACE INTO listings (category_url, title, author, novel_url) VALUES (?, ?, ?, ?)', 
                           (category_url, title, author, novel_url))
            conn.commit()
        except sqlite3.Error as e: print(f"Lỗi DB: {e}")
        finally: conn.close()
    
    def save_novel_info(novel_url, title, author, description, source):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT OR REPLACE INTO novels (novel_url, title, author, description, source) VALUES (?, ?, ?, ?, ?)', 
                           (novel_url, title, author, description, source))
            conn.commit()
        except sqlite3.Error as e: print(f"Lỗi DB: {e}")
        finally: conn.close()
    
    def save_chapter_item(novel_url, chapter_title, chapter_url, content=None):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            if content:
                cursor.execute('INSERT OR REPLACE INTO chapters (chapter_url, novel_url, chapter_title, content) VALUES (?, ?, ?, ?)', 
                               (chapter_url, novel_url, chapter_title, content))
            else:
                cursor.execute('''
                    INSERT INTO chapters (chapter_url, novel_url, chapter_title) VALUES (?, ?, ?)
                    ON CONFLICT(chapter_url) DO UPDATE SET chapter_title=excluded.chapter_title
                ''', (chapter_url, novel_url, chapter_title))
            conn.commit()
        except sqlite3.Error as e: print(f"Lỗi DB: {e}")
        finally: conn.close()
    

## File 2: `plugins/base_plugin.py` (Lớp Interface mẫu)
    
    
    import requests
    from bs4 import BeautifulSoup
    
    class BasePlugin:
        """Mọi plugin cào truyện bắt buộc phải kế thừa lớp này và cài đặt lại các hàm."""
        
        # Domain để core CLI nhận diện plugin (ví dụ: 'truyenfull.live')
        DOMAIN = "" 
    
        def __init__(self):
            self.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
    
        def get_soup(self, url):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return BeautifulSoup(response.text, 'html.parser')
                return None
            except Exception:
                return None
    
        def clean_url(self, url):
            if not url.endswith('/'): url += '/'
            return url
    
        def build_page_url(self, base_url, page_num):
            """Mỗi nguồn có kiểu phân trang khác nhau, cần cài đặt lại ở subclass."""
            raise NotImplementedError
    
        def extract_total_pages(self, soup):
            raise NotImplementedError
    
        def parse_listing(self, soup):
            """Trả về list các dict: [{'title':..., 'author':..., 'url':...}]"""
            raise NotImplementedError
    
        def parse_novel_info(self, soup):
            """Trả về dict: {'title':..., 'author':..., 'description':...}"""
            raise NotImplementedError
    
        def parse_chapter_list(self, soup):
            """Trả về list các dict: [{'title':..., 'url':...}]"""
            raise NotImplementedError
    
        def parse_chapter_content(self, soup, url):
            """Trả về dict: {'title':..., 'content':..., 'novel_url':...}"""
            raise NotImplementedError
    

## File 3: `plugins/truyenfull.py` (Plugin cho riêng truyenfull.live)
    
    
    import re
    from plugins.base_plugin import BasePlugin
    
    class TruyenFullPlugin(BasePlugin):
        DOMAIN = "truyenfull.live"
    
        def build_page_url(self, base_url, page_num):
            base_url = self.clean_url(base_url)
            return f"{base_url}trang-{page_num}/" if page_num else base_url
    
        def extract_total_pages(self, soup):
            if not soup: return 1
            pagination = soup.find('ul', class_='pagination')
            if not pagination: return 1
            
            last_page_li = pagination.find('li', class_='last')
            if last_page_li and last_page_li.find('a'):
                match = re.search(r'trang-(\d+)', last_page_li.find('a')['href'])
                if match: return int(match.group(1))
            
            pages = [int(match.group(1)) for a in pagination.find_all('a') if (match := re.search(r'trang-(\d+)', a.get('href', '')))]
            return max(pages) if pages else 1
    
        def parse_listing(self, soup):
            results = []
            items = soup.find_all('div', class_='row', itemtype='https://schema.org') or soup.select('.list-truyen .row')
            for item in items:
                title_element = item.find('h3', class_='truyen-title') or item.find('a')
                if not title_element: continue
                a_tag = title_element.find('a') if title_element.name != 'a' else title_element
                author_element = item.find('span', class_='author')
                
                results.append({
                    'title': a_tag.text.strip() if a_tag else "Không rõ",
                    'url': self.clean_url(a_tag['href']) if a_tag else "",
                    'author': author_element.text.strip() if author_element else "Không rõ"
                })
            return results
    
        def parse_novel_info(self, soup):
            title = soup.find('h3', class_='title').text.strip() if soup.find('h3', class_='title') else "Không rõ"
            info_div = soup.find('div', class_='info')
            author = info_div.find('a', itemtype='https://schema.org').text.strip() if (info_div and info_div.find('a', itemtype='https://schema.org')) else "Không rõ"
            desc_div = soup.find('div', class_='desc-text')
            
            return {
                'title': title,
                'author': author,
                'description': desc_div.text.strip() if desc_div else "Không có mô tả"
            }
    
        def parse_chapter_list(self, soup):
            results = []
            chapter_list_div = soup.find('ul', class_='list-chapter')
            if chapter_list_div:
                for li in chapter_list_div.find_all('li'):
                    a = li.find('a')
                    if a:
                        results.append({'title': a.text.strip(), 'url': self.clean_url(a['href'])})
            return results
    
        def parse_chapter_content(self, soup, url):
            title = soup.find('a', class_='chapter-title') or soup.find('span', class_='chapter-title')
            content_div = soup.find('div', class_='chapter-c') or soup.find('div', id='chapter-c')
            if content_div:
                for ads in content_div.find_all(['div', 'ins', 'script']): ads.decompose()
                content_text = content_div.get_text('\n').strip()
            else:
                content_text = "Không tìm thấy nội dung chương."
                
            novel_url = re.sub(r'chuong-[\d\.]+/$', '', url)
            return {
                'title': title.text.strip() if title else "Không rõ tên chương",
                'content': content_text,
                'novel_url': novel_url
            }
    

## File 4: `plugins/__init__.py` (Quản lý Load tự động)
    
    
    import os
    import importlib
    from urllib.parse import urlparse
    
    # Từ điển chứa toàn bộ các plugin được load thành công dạng: {'domain': PluginInstance}
    PLUGINS = {}
    
    def load_plugins():
        plugins_dir = os.path.dirname(__file__)
        for file in os.listdir(plugins_dir):
            if file.endswith('.py') and file != '__init__.py' and file != 'base_plugin.py':
                module_name = f"plugins.{file[:-3]}"
                module = importlib.import_module(module_name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    # Nếu là một class kế thừa từ BasePlugin và có cấu hình DOMAIN
                    if isinstance(attr, type) and hasattr(attr, 'DOMAIN') and attr.DOMAIN:
                        PLUGINS[attr.DOMAIN] = attr()
    
    def get_plugin_by_url(url):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')
        if domain in PLUGINS:
            return PLUGINS[domain]
        print(f"Lỗi: Chưa có plugin hỗ trợ cho nguồn truyện '{domain}' này.")
        return None
    
    # Tự động quét và kích hoạt plugin khi project khởi chạy
    load_plugins()
    

## File 5: `crawler.py` (Lõi điều hướng CLI chính)
    
    
    import argparse
    import sys
    import time
    import database as db
    from plugins import get_plugin_by_url
    
    def main():
        db.init_db()
        
        parser = argparse.ArgumentParser(description="CLI Crawl truyện đa nguồn dạng Plugin/Adapter")
        parser.add_argument("url", nargs="?", help="Đường dẫn (URL) cần crawl dữ liệu")
        parser.add_argument("--listing", action="store_true", help="Crawl danh sách truyện từ danh mục")
        parser.add_argument("--page", type=int, help="Chỉ định số trang cụ thể")
        parser.add_argument("--novel", action="store_true", help="Crawl thông tin truyện/chương")
        parser.add_argument("--chapter", action="store_true", help="Lấy nội dung chương cụ thể")
        parser.add_argument("--list-chapter", action="store_true", help="Lấy danh sách chương của bộ truyện")
        parser.add_argument("--total-page", action="store_true", help="Lấy tổng số trang")
        parser.add_argument("--all-chapters", action="store_true", help="Tự động cào TOÀN BỘ chương từ đầu đến cuối")
    
        args = parser.parse_args()
        if not args.url:
            parser.print_help()
            sys.exit(1)
    
        # 1. Tìm plugin tương ứng với domain của URL
        plugin = get_plugin_by_url(args.url)
        if not plugin: sys.exit(1)
    
        # 2. Xử lý logic CLI dựa trên Plugin đã chọn
        if args.listing:
            target_url = plugin.build_page_url(args.url, args.page)
            soup = plugin.get_soup(target_url)
            if not soup: return
    
            if args.total_page:
                print(f"Tổng số trang danh mục: {plugin.extract_total_pages(soup)}")
                return
    
            novels = plugin.parse_listing(soup)
            print(f"{'Tiêu đề':<50} | {'Tác giả':<20} | SQLite")
            print("-" * 90)
            for nv in novels:
                db.save_listing_item(plugin.clean_url(args.url), nv['title'], nv['author'], nv['url'])
                print(f"{nv['title']:<50} | {nv['author']:<20} | OK")
    
        elif args.novel:
            if args.chapter:
                # Lấy nội dung 1 chương cụ thể
                soup = plugin.get_soup(args.url)
                if not soup: return
                data = plugin.parse_chapter_content(soup, args.url)
                db.save_chapter_item(data['novel_url'], data['title'], plugin.clean_url(args.url), content=data['content'])
                print(f"--- Đã lưu: {data['title']} vào SQLite ---")
                
            elif args.all_chapters:
                # Treo máy cào toàn bộ chương liên tục
                novel_url = plugin.clean_url(args.url)
                print("Step 1: Đang lấy thông tin truyện...")
                soup = plugin.get_soup(novel_url)
                if not soup: return
                info = plugin.parse_novel_info(soup)
                db.save_novel_info(novel_url, info['title'], info['author'], info['description'], plugin.DOMAIN)
                
                total_pages = plugin.extract_total_pages(soup)
                print(f"Step 2: Bộ truyện có tổng cộng {total_pages} trang chương.")
                
                all_chapters = []
                print("Step 3: Đang quét danh sách link chương...")
                for p in range(1, total_pages + 1):
                    p_url = plugin.build_page_url(novel_url, p if p > 1 else None)
                    p_soup = plugin.get_soup(p_url)
                    if p_soup:
                        all_chapters.extend(plugin.parse_chapter_list(p_soup))
                    print(f"  > Đã quét xong trang {p}/{total_pages}", end="\r")
                
                total_chaps = len(all_chapters)
                print(f"\nTìm thấy {total_chaps} chương. Bắt đầu treo máy tải nội dung...")
                print("-" * 60)
                
                for index, chap in enumerate(all_chapters, 1):
                    print(f"[{index}/{total_chaps}] Đang tải: {chap['title']} ... ", end="", flush=True)
                    c_soup = plugin.get_soup(chap['url'])
                    if c_soup:
                        c_data = plugin.parse_chapter_content(c_soup, chap['url'])
                        db.save_chapter_item(novel_url, c_data['title'], chap['url'], content=c_data['content'])
                        print("Xong!")
                    else:
                        print("Thất bại!")
                    time.sleep(0.5)
                print("--- Hoàn thành tải toàn bộ truyện về SQLite3! ---")
                
            else:
                # Các lệnh lẻ: --novel, --list-chapter, --total-page
                target_url = plugin.build_page_url(args.url, args.page)
                soup = plugin.get_soup(target_url)
                if not soup: return
    
                if args.total_page:
                    print(f"Tổng số trang chương: {plugin.extract_total_pages(soup)}")
                elif args.list_chapter:
                    chapters = plugin.parse_chapter_list(soup)
                    print(f"{'Tên chương':<60} | SQLite")
                    print("-" * 80)
                    for ch in chapters:
                        db.save_chapter_item(plugin.clean_url(args.url), ch['title'], ch['url'])
                        print(f"{ch['title']:<60} | OK")
                else:
                    info = plugin.parse_novel_info(soup)
                    db.save_novel_info(plugin.clean_url(args.url), info['title'], info['author'], info['description'], plugin.DOMAIN)
                    print(f"Tiêu đề: {info['title']}\nTác giả: {info['author']}\nMô tả truyện đã được lưu vào SQLite.")
        else:
            print("Vui lòng cung cấp tham số đi kèm hợp lệ (--listing hoặc --novel).")
    
    if __name__ == "__main__":
        main()
    

* * *

## 3\. Cách thêm một nguồn truyện mới (Ví dụ: `truyenchu.vn`)

Khi bạn muốn mở rộng hệ thống để cào thêm trang web khác, bạn không cần động vào file `crawler.py` hay `database.py`. Bạn chỉ cần làm theo 2 bước đơn giản:

  1. Tạo một file mới nằm trong thư mục plugin: `plugins/truyenchu.py`
  2. Kế thừa class `BasePlugin`, khai báo thuộc tính `DOMAIN = "truyenchu.vn"` và viết quy tắc lấy thẻ HTML (`BeautifulSoup`) tương ứng với cấu trúc của trang đó.



Hệ thống core CLI khi chạy lệnh `python crawler.py "https://truyenchu.vn..."` sẽ tự động phân tích chuỗi URL, trích xuất ra domain `truyenchu.vn`, nạp file plugin mới của bạn vào và thực hiện cào dữ liệu bình thường.

Bạn có cần tôi viết demo cấu trúc cho một website truyện cụ thể nào khác (như TangThuvien hay TruyenChu) để bạn làm mẫu phát triển tiếp không?