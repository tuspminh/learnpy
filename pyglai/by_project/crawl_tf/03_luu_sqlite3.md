Để lưu trữ dữ liệu crawl vào SQLite3, tôi sẽ cập nhật lại mã nguồn. Mỗi khi bạn chạy các lệnh crawl dữ liệu, công cụ sẽ tự động tạo một file cơ sở dữ liệu tên là `truyenfull.db` (nếu chưa có) và lưu thông tin vào các bảng tương ứng.

Hệ thống sẽ tự động tạo 3 bảng dữ liệu:

  1. `novels`: Lưu thông tin truyện (slug, tiêu đề, tác giả, mô tả).
  2. `chapters`: Lưu danh sách chương và nội dung chương liên kết với truyện.
  3. `listings`: Lưu danh sách truyện thu thập được từ các trang danh mục.



## 1\. Mã nguồn Python CLI cập nhật tích hợp SQLite3 (`crawler.py`)
    
    
    import argparse
    import sys
    import re
    import sqlite3
    import requests
    from bs4 import BeautifulSoup
    
    DB_NAME = "truyenfull.db"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # --- CẤU HÌNH DATABASE ---
    def init_db():
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Bảng lưu danh sách truyện từ mục listing
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_url TEXT,
                title TEXT,
                author TEXT,
                novel_url TEXT UNIQUE
            )
        ''')
        
        # Bảng lưu thông tin chi tiết truyện
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS novels (
                novel_url TEXT PRIMARY KEY,
                title TEXT,
                author TEXT,
                description TEXT
            )
        ''')
        
        # Bảng lưu danh sách và nội dung chương
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
            cursor.execute('''
                INSERT OR REPLACE INTO listings (category_url, title, author, novel_url)
                VALUES (?, ?, ?, ?)
            ''', (category_url, title, author, novel_url))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Lỗi DB: {e}")
        finally:
            conn.close()
    
    def save_novel_info(novel_url, title, author, description):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO novels (novel_url, title, author, description)
                VALUES (?, ?, ?, ?)
            ''', (novel_url, title, author, description))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Lỗi DB: {e}")
        finally:
            conn.close()
    
    def save_chapter_item(novel_url, chapter_title, chapter_url, content=None):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            # Nếu đã có chương, chỉ cập nhật nội dung content nếu có dữ liệu mới
            if content:
                cursor.execute('''
                    INSERT OR REPLACE INTO chapters (chapter_url, novel_url, chapter_title, content)
                    VALUES (?, ?, ?, ?)
                ''', (chapter_url, novel_url, chapter_title, content))
            else:
                # Lệnh bóc danh sách chương chưa có nội dung text truyện
                cursor.execute('''
                    INSERT INTO chapters (chapter_url, novel_url, chapter_title)
                    VALUES (?, ?, ?)
                    ON CONFLICT(chapter_url) DO UPDATE SET chapter_title=excluded.chapter_title
                ''', (chapter_url, novel_url, chapter_title))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Lỗi DB: {e}")
        finally:
            conn.close()
    
    # --- CHỨC NĂNG CRAWL ---
    def get_soup(url):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
            else:
                print(f"Lỗi: Không thể truy cập trang. Mã lỗi {response.status_code}")
                return None
        except Exception as e:
            print(f"Đã xảy ra lỗi kết nối: {e}")
            return None
    
    def clean_url(url):
        if not url.endswith('/'):
            url += '/'
        return url
    
    def extract_total_pages(soup):
        if not soup: return 1
        pagination = soup.find('ul', class_='pagination')
        if not pagination: return 1
        
        last_page_li = pagination.find('li', class_='last')
        if last_page_li and last_page_li.find('a'):
            href = last_page_li.find('a')['href']
            match = re.search(r'trang-(\d+)', href)
            if match: return int(match.group(1))
        
        pages = []
        for a in pagination.find_all('a'):
            match = re.search(r'trang-(\d+)', a.get('href', ''))
            if match: pages.append(int(match.group(1)))
        return max(pages) if pages else 1
    
    def crawl_listing(url, total_page=False, page=None):
        original_url = clean_url(url)
        target_url = original_url
        if page:
            target_url = f"{original_url}trang-{page}/"
    
        soup = get_soup(target_url)
        if not soup: return
    
        if total_page:
            print(f"Tổng số trang danh mục: {extract_total_pages(soup)}")
            return
    
        items = soup.find_all('div', class_='row', itemtype='https://schema.org')
        if not items:
            items = soup.select('.list-truyen .row')
    
        print(f"{'Tiêu đề':<50} | {'Tác giả':<20} | Đã lưu DB")
        print("-" * 90)
        for item in items:
            title_element = item.find('h3', class_='truyen-title') or item.find('a')
            if not title_element: continue
            
            a_tag = title_element.find('a') if title_element.name != 'a' else title_element
            title = a_tag.text.strip() if a_tag else "Không rõ"
            novel_url = clean_url(a_tag['href']) if a_tag else ""
            
            author_element = item.find('span', class_='author')
            author = author_element.text.strip() if author_element else "Không rõ"
            
            # Lưu vào bảng listings
            save_listing_item(original_url, title, author, novel_url)
            print(f"{title:<50} | {author:<20} | OK")
    
    def crawl_novel_info(url, show_info=False, list_chapter=False, page=None, total_page=False):
        original_url = clean_url(url)
        target_url = original_url
        if page:
            target_url = f"{original_url}trang-{page}/"
    
        soup = get_soup(target_url)
        if not soup: return
    
        if show_info:
            title = soup.find('h3', class_='title').text.strip() if soup.find('h3', class_='title') else "Không rõ"
            
            info_div = soup.find('div', class_='info')
            author = "Không rõ"
            if info_div:
                a_author = info_div.find('a', itemtype='https://schema.org')
                if a_author: author = a_author.text.strip()
    
            desc_div = soup.find('div', class_='desc-text')
            description = desc_div.text.strip() if desc_div else "Không có mô tả"
            
            # Lưu vào bảng novels
            save_novel_info(original_url, title, author, description)
            
            print(f"Tiêu đề: {title}")
            print(f"Tác giả: {author}")
            print(f"Mô tả đã được lưu thành công vào SQLite.")
            return
    
        if total_page:
            print(f"Tổng số trang chương: {extract_total_pages(soup)}")
            return
    
        if list_chapter:
            chapter_list_div = soup.find('ul', class_='list-chapter')
            if not chapter_list_div:
                print("Không tìm thấy danh sách chương.")
                return
                
            chapters = chapter_list_div.find_all('li')
            print(f"{'Tên chương':<60} | Đã lưu DB")
            print("-" * 80)
            for chap in chapters:
                a_tag = chap.find('a')
                if a_tag:
                    chap_title = a_tag.text.strip()
                    chap_url = clean_url(a_tag['href'])
                    
                    # Lưu vào bảng chapters (chưa có nội dung)
                    save_chapter_item(original_url, chap_title, chap_url)
                    print(f"{chap_title:<60} | OK")
    
    def crawl_chapter_content(url):
        url = clean_url(url)
        soup = get_soup(url)
        if not soup: return
        
        title = soup.find('a', class_='chapter-title') or soup.find('span', class_='chapter-title')
        title_text = title.text.strip() if title else "Không rõ tên chương"
        
        content_div = soup.find('div', class_='chapter-c') or soup.find('div', id='chapter-c')
        if content_div:
            for ads in content_div.find_all(['div', 'ins', 'script']):
                ads.decompose()
            content_text = content_div.get_text('\n').strip()
        else:
            content_text = "Không tìm thấy nội dung chương."
            
        # Trích xuất novel_url gốc từ đường dẫn chương (bỏ phần /chuong-x/)
        # Ví dụ: https://truyenfull.live -> https://truyenfull.live
        novel_url = re.sub(r'chuong-\d+/$', '', url)
            
        # Cập nhật nội dung chữ vào bảng chapters
        save_chapter_item(novel_url, title_text, url, content=content_text)
        print(f"--- Đã lưu: {title_text} vào SQLite ---")
    
    def main():
        init_db() # Khởi tạo database và bảng dữ liệu nếu chưa có
        
        parser = argparse.ArgumentParser(description="CLI Crawl truyenfull.live lưu SQLite3")
        parser.add_argument("url", nargs="?", help="Đường dẫn (URL) cần crawl dữ liệu")
        parser.add_argument("--listing", action="store_true", help="Crawl danh sách truyện từ danh mục")
        parser.add_argument("--page", type=int, help="Chỉ định số trang cụ thể")
        parser.add_argument("--novel", action="store_true", help="Crawl thông tin truyện/chương")
        parser.add_argument("--chapter", action="store_true", help="Lấy nội dung chương cụ thể")
        parser.add_argument("--list-chapter", action="store_true", help="Lấy danh sách chương của bộ truyện")
        parser.add_argument("--total-page", action="store_true", help="Lấy tổng số trang")
    
        args = parser.parse_args()
    
        if not args.url:
            parser.print_help()
            sys.exit(1)
    
        if args.listing:
            crawl_listing(args.url, total_page=args.total_page, page=args.page)
        elif args.novel:
            if args.chapter:
                crawl_chapter_content(args.url)
            else:
                show_info = not (args.list_chapter or args.page or args.total_page)
                crawl_novel_info(args.url, show_info=show_info, list_chapter=args.list_chapter, page=args.page, total_page=args.total_page)
        else:
            print("Vui lòng cung cấp tham số đi kèm hợp lệ (--listing hoặc --novel).")
    
    if __name__ == "__main__":
        main()
    

## 2\. Cách kiểm tra dữ liệu sau khi crawl

Mỗi khi bạn chạy lệnh, một file database cơ bản `truyenfull.db` sẽ xuất hiện ngay trong thư mục chạy script. Bạn có thể sử dụng các công cụ như DB Browser for SQLite hoặc dùng terminal chạy lệnh sau để xem nhanh dữ liệu:
    
    
    sqlite3 truyenfull.db "SELECT * FROM novels LIMIT 5;"
    

Bạn có muốn viết thêm script tự động quét toàn bộ từ chương 1 đến chương cuối của một bộ truyện để treo máy crawl tự động lưu vào file SQLite này luôn không?