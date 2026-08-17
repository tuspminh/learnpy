Để treo máy crawl tự động toàn bộ chương của một bộ truyện từ chương 1 đến chương cuối, chúng ta cần một cơ chế thông minh: Lấy danh sách tất cả các chương từ phân trang trước, sau đó duyệt qua từng chương để cào nội dung text.

Tôi đã bổ sung thêm tính năng này vào CLI bằng cách thêm tham số `--all-chapters`. Lệnh này sẽ tự động lướt qua mọi trang chương của bộ truyện, thu thập toàn bộ URL chương và tải nội dung của từng chương về lưu trực tiếp vào file SQLite3.

## 1\. Mã nguồn Python CLI cập nhật đầy đủ tính năng (`crawler.py`)
    
    
    import argparse
    import sys
    import re
    import sqlite3
    import time
    import requests
    from bs4 import BeautifulSoup
    
    DB_NAME = "truyenfull.db"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
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
                description TEXT
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
            if content:
                cursor.execute('''
                    INSERT OR REPLACE INTO chapters (chapter_url, novel_url, chapter_title, content)
                    VALUES (?, ?, ?, ?)
                ''', (chapter_url, novel_url, chapter_title, content))
            else:
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
    
    def get_soup(url):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
            else:
                print(f"\nLỗi: Không thể truy cập {url}. Mã lỗi {response.status_code}")
                return None
        except Exception as e:
            print(f"\nĐã xảy ra lỗi kết nối: {e}")
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
            
            save_novel_info(original_url, title, author, description)
            print(f"Tiêu đề: {title}\nTác giả: {author}\nMô tả truyện đã được lưu.")
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
                    save_chapter_item(original_url, chap_title, chap_url)
                    print(f"{chap_title:<60} | OK")
    
    def crawl_chapter_content(url, silent=False):
        url = clean_url(url)
        soup = get_soup(url)
        if not soup: return None
        
        title = soup.find('a', class_='chapter-title') or soup.find('span', class_='chapter-title')
        title_text = title.text.strip() if title else "Không rõ tên chương"
        
        content_div = soup.find('div', class_='chapter-c') or soup.find('div', id='chapter-c')
        if content_div:
            for ads in content_div.find_all(['div', 'ins', 'script']):
                ads.decompose()
            content_text = content_div.get_text('\n').strip()
        else:
            content_text = "Không tìm thấy nội dung chương."
            
        novel_url = re.sub(r'chuong-[\d\.]+/$', '', url)
        save_chapter_item(novel_url, title_text, url, content=content_text)
        if not silent:
            print(f"--- Đã lưu: {title_text} vào SQLite ---")
        return title_text
    
    def crawl_all_chapters(novel_url):
        novel_url = clean_url(novel_url)
        print("Step 1: Đang lấy thông tin truyện...")
        crawl_novel_info(novel_url, show_info=True)
        
        first_soup = get_soup(novel_url)
        if not first_soup: return
        
        total_pages = extract_total_pages(first_soup)
        print(f"Step 2: Phát hiện bộ truyện có tổng cộng {total_pages} trang chương.")
        
        # Thu thập toàn bộ danh sách URL chương trước
        all_chapters = []
        print("Step 3: Đang quét danh sách link chương từ các trang...")
        for p in range(1, total_pages + 1):
            p_url = novel_url if p == 1 else f"{novel_url}trang-{p}/"
            soup = get_soup(p_url)
            if not soup: continue
            
            chapter_list_div = soup.find('ul', class_='list-chapter')
            if chapter_list_div:
                for li in chapter_list_div.find_all('li'):
                    a = li.find('a')
                    if a:
                        all_chapters.append({
                            'title': a.text.strip(),
                            'url': clean_url(a['href'])
                        })
            print(f"  > Đã quét xong trang {p}/{total_pages}", end="\r")
        
        total_chaps = len(all_chapters)
        print(f"\nTìm thấy tổng cộng {total_chaps} chương. Bắt đầu tải nội dung tự động...")
        print("-" * 60)
        
        # Duyệt qua từng chương và crawl nội dung text truyện
        for index, chap in enumerate(all_chapters, 1):
            print(f"[{index}/{total_chaps}] Đang tải: {chap['title']} ... ", end="", flush=True)
            
            # Gọi hàm cào nội dung chương
            chap_title = crawl_chapter_content(chap['url'], silent=True)
            if chap_title:
                print("Xong!")
            else:
                print("Thất bại (Lỗi tải trang)")
                
            # Giảm tải cho server, tránh bị block IP (chờ 0.5 - 1 giây mỗi chương)
            time.sleep(0.5)
    
        print("-" * 60)
        print("Chúc mừng! Đã hoàn thành tải toàn bộ truyện về SQLite3.")
    
    def main():
        init_db()
        
        parser = argparse.ArgumentParser(description="CLI Crawl truyenfull.live nâng cao tự động treo máy")
        parser.add_argument("url", nargs="?", help="Đường dẫn (URL) cần crawl dữ liệu")
        parser.add_argument("--listing", action="store_true", help="Crawl danh sách truyện từ danh mục")  
        parser.add_argument("--page", type=int, help="Chỉ định số trang cụ thể")  
        parser.add_argument("--novel", action="store_true", help="Crawl thông tin truyện/chương")  
        parser.add_argument("--chapter", action="store_true", help="Lấy nội dung chương cụ thể")  
        parser.add_argument("--list-chapter", action="store_true", help="Lấy danh sách chương của bộ truyện")  
        parser.add_argument("--total-page", action="store_true", help="Lấy tổng số trang")  
        # Tham số mới để treo máy crawl toàn bộ truyện  
        parser.add_argument("--all-chapters", action="store_true", help="Kết hợp với --novel để tự động cào TOÀN BỘ chương từ đầu đến cuối")

        args = parser.parse_args()

        if not args.url:  
            parser.print_help()  
            sys.exit(1)

        if args.listing:  
            crawl_listing(args.url, total_page=args.total_page, page=args.page)  
        elif args.novel:  
            if args.chapter:  
                crawl_chapter_content(args.url)  
            elif args.all_chapters:  
                # Lệnh treo máy cào tất cả chương  
                crawl_all_chapters(args.url)  
            else:  
                show_info = not (args.list_chapter or args.page or args.total_page)  
                crawl_novel_info(args.url, show_info=show_info, list_chapter=args.list_chapter, page=args.page, total_page=args.total_page)  
        else:  
            print("Vui lòng cung cấp tham số đi kèm hợp lệ (--listing hoặc --novel).")


if __name__ == "__main__":  
    main()


    
    
### 2. Cách chạy lệnh treo máy cào trọn bộ truyện

Bạn chỉ cần truyền đường dẫn gốc của truyện và thêm cờ `--novel --all-chapters`:

```bash
python crawler.py "https://truyenfull.live" --novel --all-chapters
    

Màn hình CLI sẽ hiển thị tiến trình chạy như sau:
    
    
    Step 1: Đang lấy thông tin truyện...
    Tiêu đề: Tên Truyện Hay
    Tác giả: Tác Giả A
    Mô tả truyện đã được lưu.
    Step 2: Phát hiện bộ truyện có tổng cộng 5 trang chương.
    Step 3: Đang quét danh sách link chương từ các trang...
    Tìm thấy tổng cộng 250 chương. Bắt đầu tải nội dung tự động...
    ------------------------------------------------------------
    [1/250] Đang tải: Chương 1: Khởi đầu ... Xong!
    [2/250] Đang tải: Chương 2: Gặp gỡ ... Xong!
    [3/250] Đang tải: Chương 3: Thử thách ... Xong!
    ...
    

## 3\. Cách lấy dữ liệu một bộ truyện hoàn chỉnh từ Database ra đọc

Nếu bạn muốn kết xuất (export) toàn bộ các chương đã cào của bộ truyện đó từ file SQLite3 ra thành một file văn bản `.txt` duy nhất gọn gàng để đọc offine hoặc nạp vào máy đọc sách, bạn có thể chạy một đoạn script ngắn sau:
    
    
    import sqlite3
    
    # Kết nối database
    conn = sqlite3.connect("truyenfull.db")
    cursor = conn.cursor()
    
    # Thay link truyện bạn muốn xuất file vào đây
    novel_url = "https://truyenfull.live"
    
    # Lấy thông tin tiêu đề truyện và tất cả chương
    cursor.execute("SELECT title FROM novels WHERE novel_url=?", (novel_url,))
    novel_title = cursor.fetchone()[0]
    
    cursor.execute("SELECT chapter_title, content FROM chapters WHERE novel_url=? AND content IS NOT NULL", (novel_url,))
    chapters = cursor.fetchall()
    
    # Ghi ra file TXT công bố bộ truyện
    with open(f"{novel_title}.txt", "w", encoding="utf-8") as f:
        f.write(f"=== {novel_title} ===\n\n")
        for chap_title, content in chapters:
            f.write(f"\n\n--- {chap_title} ---\n\n")
            f.write(content)
    
    print(f"Đã xuất file thành công: {novel_title}.txt")
    conn.close()
    

Bạn có muốn bổ sung thêm tính năng tự động phát hiện và cào tiếp (Resume) khi bị rớt mạng hay tắt máy giữa chừng không?