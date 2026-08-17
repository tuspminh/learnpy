Để xây dựng một công cụ CLI crawl dữ liệu từ trang `truyenfull.live` với các tính năng như bạn yêu cầu, chúng ta sẽ sử dụng ngôn ngữ Python.

Dưới đây là hướng dẫn chi tiết cách thiết lập dự án và mã nguồn hoàn chỉnh sử dụng thư viện `argparse` (để tạo CLI), `requests` (để tải trang) và `BeautifulSoup` (để bóc tách dữ liệu).

## 1\. Chuẩn bị môi trường

Tạo một thư mục mới, tạo file `crawler.py` và cài đặt các thư viện cần thiết bằng lệnh sau trong terminal:
    
    
    pip install requests beautifulsoup4
    

## 2\. Mã nguồn toàn chỉnh (`crawler.py`)
    
    
    import argparse
    import sys
    import re
    import requests
    from bs4 import BeautifulSoup
    
    BASE_URL = "https://truyenfull.live"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
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
    
    def extract_total_pages(soup):
        if not soup: return 1
        # Tìm thẻ phân trang cuối cùng hoặc tính từ nút 'Cuối'
        pagination = soup.find('ul', class_='pagination')
        if not pagination:
            return 1
        last_page_li = pagination.find('li', class_='last')
        if last_page_li and last_page_li.find('a'):
            href = last_page_li.find('a')['href']
            match = re.search(r'page=(\d+)', href)
            if match: return int(match.group(1))
        
        # Nếu không có nút 'Cuối', tìm số trang lớn nhất xuất hiện
        pages = []
        for a in pagination.find_all('a'):
            match = re.search(r'page=(\d+)', a.get('href', ''))
            if match: pages.append(int(match.group(1)))
        return max(pages) if pages else 1
    
    def crawl_listing(url, total_page=False, page=None):
        # Xử lý query page nếu có tham số --page
        if page:
            if "?" in url:
                url = f"{url}&page={page}"
            else:
                url = f"{url}?page={page}"
    
        soup = get_soup(url)
        if not soup: return
    
        if total_page:
            print(f"Tổng số trang: {extract_total_pages(soup)}")
            return
    
        # Lấy danh sách truyện trong trang listing
        # Cấu trúc truyenfull thường nằm trong div.list-truyen hoặc tương đương
        items = soup.find_all('div', class_='row', itemtype='https://schema.org')
        if not items:
            # Fallback thử cấu trúc khác nếu giao diện thay đổi
            items = soup.select('.list-truyen .row')
    
        print(f"{'Tiêu đề':<50} | {'Tác giả':<20} | {'Đường dẫn'}")
        print("-" * 100)
        for item in items:
            title_element = item.find('h3', class_='truyen-title') or item.find('a')
            if not title_element: continue
            
            a_tag = title_element.find('a') if title_element.name != 'a' else title_element
            title = a_tag.text.strip() if a_tag else "Không rõ"
            novel_url = a_tag['href'] if a_tag else ""
            
            author_element = item.find('span', class_='author')
            author = author_element.text.strip() if author_element else "Không rõ"
            
            print(f"{title:<50} | {author:<20} | {novel_url}")
    
    def crawl_novel_info(url, show_info=False, list_chapter=False, page=None, total_page=False):
        soup = get_soup(url)
        if not soup: return
    
        if show_info:
            title = soup.find('h3', class_='title').text.strip() if soup.find('h3', class_='title') else "Không rõ"
            
            # Tìm tác giả trong phần thông tin truyện
            info_div = soup.find('div', class_='info')
            author = "Không rõ"
            if info_div:
                a_author = info_div.find('a', itemtype='https://schema.org')
                if a_author: author = a_author.text.strip()
    
            desc_div = soup.find('div', class_='desc-text')
            description = desc_div.text.strip() if desc_div else "Không có mô tả"
            
            print(f"Tiêu đề: {title}")
            print(f"Tác giả: {author}")
            print(f"Mô tả:\n{description}")
            return
    
        # Tìm phân trang của danh sách chương truyện
        pagination = soup.find('ul', class_='pagination')
        
        if total_page:
            print(f"Tổng số trang chương: {extract_total_pages(soup)}")
            return
    
        if list_chapter:
            # Nếu yêu cầu xem trang cụ thể của danh sách chương
            if page:
                if "?" in url: url = f"{url}&page={page}"
                else: url = f"{url}?page={page}"
                soup = get_soup(url)
                if not soup: return
    
            # Lấy danh sách chương
            chapter_list_div = soup.find('ul', class_='list-chapter')
            if not chapter_list_div:
                print("Không tìm thấy danh sách chương.")
                return
                
            chapters = chapter_list_div.find_all('li')
            print(f"{'Số chương / Tên chương':<60} | {'Đường dẫn chương'}")
            print("-" * 100)
            for chap in chapters:
                a_tag = chap.find('a')
                if a_tag:
                    chap_title = a_tag.text.strip()
                    chap_url = a_tag['href']
                    print(f"{chap_title:<60} | {chap_url}")
    
    def crawl_chapter_content(url):
        soup = get_soup(url)
        if not soup: return
        
        title = soup.find('a', class_='chapter-title') or soup.find('span', class_='chapter-title')
        title_text = title.text.strip() if title else "Không rõ tên chương"
        
        content_div = soup.find('div', class_='chapter-c') or soup.find('div', id='chapter-c')
        if content_div:
            # Xóa bớt các thẻ quảng cáo nếu có trong nội dung
            for ads in content_div.find_all(['div', 'ins', 'script']):
                ads.decompose()
            content_text = content_div.get_text('\n').strip()
        else:
            content_text = "Không tìm thấy nội dung chương."
            
        print(f"--- {title_text} ---")
        print(content_text)
    
    def main():
        parser = argparse.ArgumentParser(description="CLI Crawl dữ liệu truyenfull.live")
        
        # Định nghĩa tham số vị trí chính: URL cần crawl
        parser.add_argument("url", nargs="?", help="Đường dẫn (URL) cần crawl dữ liệu")
        
        # Các tùy chọn cho listing truyện
        parser.add_argument("--listing", action="store_true", help="Crawl danh sách truyện từ URL phân mục")
        parser.add_argument("--page", type=int, help="Chỉ định số trang cụ thể cần lấy")
        
        # Các tùy chọn cho trang chi tiết truyện và chương
        parser.add_argument("--novel", action="store_true", help="Crawl thông tin hoặc danh sách chương của truyện")
        parser.add_argument("--chapter", action="store_true", help="Kết hợp với --novel để lấy nội dung chương cụ thể từ URL chương")
        parser.add_argument("--list-chapter", action="store_true", help="Kết hợp với --novel để lấy danh sách chương")
        parser.add_argument("--total-page", action="store_true", help="Lấy tổng số trang (dùng chung cho cả listing hoặc danh sách chương truyện)")
    
        args = parser.parse_args()
    
        if not args.url:
            parser.print_help()
            sys.exit(1)
    
        # 1. crawl url --listing
        if args.listing:
            crawl_listing(args.url, total_page=args.total_page, page=args.page)
            
        # 2. crawl url --novel
        elif args.novel:
            if args.chapter:
                # crawl url --novel --chapter (Lưu ý: url truyền vào lúc này phải là URL của chương truyện)
                crawl_chapter_content(args.url)
            elif args.list-chapter or args.page or args.total_page:
                # crawl url --novel --list-chapter [--page] [--total-page]
                crawl_novel_info(args.url, list_chapter=args.list_chapter, page=args.page, total_page=args.total_page)
            else:
                # crawl url --novel (Lấy title, author, description)
                crawl_novel_info(args.url, show_info=True)
                
        else:
            print("Vui lòng cung cấp tham số đi kèm hợp lệ (Ví dụ: --listing hoặc --novel). Sử dụng lệnh -h để xem hướng dẫn.")
    
    if __name__ == "__main__":
        main()
    

## 3\. Hướng dẫn sử dụng các câu lệnh (Đúng chuẩn yêu cầu)

Bạn hãy mở Terminal/Command Prompt lên và chạy thử các cú pháp sau:

  * Lấy danh sách truyện từ 1 trang danh mục/thể loại:
        
        python crawler.py "https://truyenfull.live" --listing
        

  * Xem tổng số trang của danh mục đó:
        
        python crawler.py "https://truyenfull.live" --listing --total-page
        

  * Lấy danh sách truyện tại một trang cụ thể (Ví dụ trang 3):
        
        python crawler.py "https://truyenfull.live" --listing --page 3
        

  * Lấy thông tin chi tiết một bộ truyện (Title, Author, Description):
        
        python crawler.py "https://truyenfull.live" --novel
        

  * Xem tổng số trang chứa danh sách chương của bộ truyện:
        
        python crawler.py "https://truyenfull.live" --novel --total-page
        

  * Lấy danh sách chương của bộ truyện ở trang mặc định:
        
        python crawler.py "https://truyenfull.live" --novel --list-chapter
        

  * Lấy danh sách chương của bộ truyện ở một trang cụ thể (Ví dụ trang 2):
        
        python crawler.py "https://truyenfull.live" --novel --list-chapter --page 2
        

  * Lấy nội dung chi tiết của một chương cụ thể:  
_(Lưu ý: Điền URL của chính chương đó vào vị trí URL)_
        
        python crawler.py "https://truyenfull.live" --novel --chapter
        




## Một số lưu ý quan trọng:

  * Vì trang `truyenfull.live` cấu trúc HTML hoặc Class có thể thay đổi nhẹ theo thời gian, nếu cấu trúc thẻ bóc tách bị lỗi, bạn hãy bấm `F12` trên trình duyệt tại trang đó để cập nhật lại các tên Class (`class_`) trong đoạn code `BeautifulSoup` cho chính xác.



Nếu bạn cần nâng cấp thêm tính năng tự động tải toàn bộ truyện về file text hoặc lưu vào dữ liệu JSON/CSV, hãy cho tôi biết cấu trúc file bạn muốn để tôi tối ưu thêm nhé!