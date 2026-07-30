Version:0.9 StartHTML:0000000105 EndHTML:0000031199 StartFragment:0000000141 EndFragment:0000031163 

Q:

thêm module này 
    
    
    plugins/
    └── truyenfull/ 
    	├── source.py ← Điều phối 
    	├── parser.py 
    	├── navigator.py 
    	├── config.py 
    	├── selectors.json 
    	└── manifest.json
    

GLAI:

Để tích hợp module `plugins/truyenfull/` vào hệ thống core HTTP Client đã dựng sẵn, chúng ta sẽ áp dụng mô hình **Data-Driven Scraping** (Cào dữ liệu dựa trên cấu hình). Toàn bộ selector HTML sẽ được tách rời vào file JSON giúp bạn dễ dàng bảo trì khi giao diện web thay đổi mà không cần sửa code Python.

Dưới đây là mã nguồn chi tiết cho từng file trong cấu trúc của bạn:

* * *

**📄 plugins/truyenfull/manifest.json**

Định nghĩa thông tin meta của plugin để hệ thống core có thể quản lý, bật/tắt hoặc gọi động.

json
    
    
    {
      "plugin_id": "truyenfull",
      "name": "TruyenFull Scraper",
      "version": "1.0.0",
      "description": "Plugin cào dữ liệu truyện từ nguồn TruyenFull",
      "author": "Developer",
      "enabled": true
    }
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/truyenfull/selectors.json**

Lưu trữ toàn bộ các mẫu CSS Selector dùng để bóc tách dữ liệu. Nếu web đổi giao diện, bạn chỉ cần sửa file này.

json
    
    
    {
      "search": {
        "novel_item": "div.list-truyen div.row",
        "novel_title": "h3.truyen-title a",
        "novel_url": "h3.truyen-title a",
        "novel_author": "span.author"
      },
      "novel_detail": {
        "title": "h3.title",
        "author": "a[itemprop='author']",
        "status": "span.text-success, span.text-primary",
        "genres": "a[itemprop='genre']",
        "description": "div.desc-text",
        "chapter_item": "ul.list-chapter li a",
        "chapter_url": ""
      },
      "chapter_detail": {
        "title": "a.chapter-title, h2.chapter-title",
        "content": "div.chapter-c"
      },
      "pagination": {
        "next_page": "ul.pagination li.active + li a"
      }
    }
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/truyenfull/config.py**

Quản lý các cấu hình tĩnh, hằng số và nạp file cấu hình JSON.

python
    
    
    import os
    import json
    
    BASE_URL = "https://truyenfull.io"  # Thay đổi domain tương ứng nếu website đổi tên miền
    
    # Lấy đường dẫn tuyệt đối đến file selectors.json cùng thư mục
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _selectors_path = os.path.join(_current_dir, "selectors.json")
    
    # Nạp cấu hình CSS Selectors
    with open(_selectors_path, "r", encoding="utf-8") as f:
        SELECTORS = json.load(f)
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/truyenfull/parser.py**

Đảm nhận nhiệm vụ duy nhất: Nhận vào đối tượng `BeautifulSoup` và trích xuất dữ liệu sạch dựa trên `SELECTORS`. Không chứa logic mạng (HTTP).

python
    
    
    from bs4 import BeautifulSoup
    from .config import SELECTORS
    
    class TruyenFullParser:
        @staticmethod
        def parse_novel_detail(soup: BeautifulSoup) -> dict:
            """Trích xuất thông tin chi tiết của một bộ truyện"""
            selectors = SELECTORS["novel_detail"]
            
            title_tag = soup.select_one(selectors["title"])
            author_tag = soup.select_one(selectors["author"])
            status_tag = soup.select_one(selectors["status"])
            desc_tag = soup.select_one(selectors["description"])
            
            genres = [g.text.strip() for g in soup.select(selectors["genres"])]
            
            # Lấy danh sách chương ở trang hiện tại
            chapters = []
            for ch_tag in soup.select(selectors["chapter_item"]):
                chapters.append({
                    "title": ch_tag.text.strip(),
                    "url": ch_tag.get("href", "")
                })
                
            return {
                "title": title_tag.text.strip() if title_tag else "Không rõ",
                "author": author_tag.text.strip() if author_tag else "Không rõ",
                "status": status_tag.text.strip() if status_tag else "Không rõ",
                "genres": genres,
                "description": desc_tag.text.strip() if desc_tag else "",
                "chapters": chapters
            }
    
        @staticmethod
        def parse_chapter_detail(soup: BeautifulSoup) -> dict:
            """Trích xuất tiêu đề và nội dung chữ của một chương truyện"""
            selectors = SELECTORS["chapter_detail"]
            
            title_tag = soup.select_one(selectors["title"])
            content_tag = soup.select_one(selectors["content"])
            
            # Xử lý làm sạch nội dung truyện (loại bỏ quảng cáo chèn bên trong nếu có)
            content_text = ""
            if content_tag:
                # Loại bỏ các thẻ script, style hoặc div quảng cáo nếu truyenfull chèn vào
                for ads in content_tag.select("script, style, .ads-holder, .ads-chapter"):
                    ads.decompose()
                content_text = content_tag.get_text(separator="\n").strip()
    
            return {
                "title": title_tag.text.strip() if title_tag else "Không rõ",
                "content": content_text
            }
    
        @staticmethod
        def parse_next_page(soup: BeautifulSoup) -> str | None:
            """Kiểm tra xem có nút 'Trang tiếp theo' hay không để phục vụ phân trang"""
            next_tag = soup.select_one(SELECTORS["pagination"]["next_page"])
            return next_tag.get("href") if next_tag else None
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/truyenfull/navigator.py**

Xử lý logic duyệt/chuyển trang (Pagination). Do danh sách chương của TruyenFull trải dài qua nhiều trang, `Navigator` giúp thu thập cạn kiệt toàn bộ link chương.

python
    
    
    from bs4 import BeautifulSoup
    from plugins.base.http_client import HTTPClient
    from .parser import TruyenFullParser
    
    class Navigator:
        def __init__(self, client: HTTPClient):
            self.client = client
    
        def get_all_chapters(self, novel_url: str) -> list[dict]:
            """Duyệt qua tất cả các trang phân trang để gom đủ danh sách chương"""
            all_chapters = []
            current_url = novel_url
            
            while current_url:
                print(f"-> Đang quét danh sách chương tại: {current_url}")
                response = self.client.get(current_url)
                
                # Parse thông tin ở trang hiện tại
                parsed_data = TruyenFullParser.parse_novel_detail(response.soup)
                all_chapters.extend(parsed_data["chapters"])
                
                # Tìm link trang kế tiếp (Phân trang của danh sách chương)
                current_url = TruyenFullParser.parse_next_page(response.soup)
                
            return all_chapters
    

Hãy thận trọng khi sử dụng mã.

**📄 plugins/truyenfull/source.py**

Bộ điều phối trung tâm (Orchestrator). Nhận cấu hình từ hệ thống, sử dụng `HTTPClient` để tải trang, dùng `Navigator` để định hướng và dùng `TruyenFullParser` để gom dữ liệu cuối cùng thành một cấu trúc Python Dict hoàn chỉnh.

python
    
    
    from plugins.base.http_client import HTTPClient
    from .config import BASE_URL
    from .parser import TruyenFullParser
    from .navigator import Navigator
    
    class TruyenFullSource:
        def __init__(self, client: HTTPClient | None = None):
            # Nếu không truyền client từ ngoài vào, tự tạo một client mặc định
            self.client = client or HTTPClient(delay_range=(1.5, 3.0), max_retries=3)
            self.navigator = Navigator(self.client)
    
        def crawl_novel(self, novel_slug: str) -> dict:
            """Hàm API chính: Cào toàn bộ thông tin truyện và toàn bộ nội dung từng chương"""
            # Đảm bảo đường dẫn chuẩn định dạng
            if novel_slug.startswith("http"):
                novel_url = novel_slug
            else:
                novel_url = f"{BASE_URL}/{novel_slug.strip('/')}/"
    
            print(f"[+] Bắt đầu thu thập truyện: {novel_url}")
            
            # 1. Cào trang chính để lấy thông tin tổng quan (Tên, tác giả...)
            main_response = self.client.get(novel_url)
            novel_data = TruyenFullParser.parse_novel_detail(main_response.soup)
            
            # 2. Sử dụng Navigator để lấy kiệt cùng tất cả các chương (xử lý phân trang)
            print("[+] Đang quét phân trang thu thập link toàn bộ chương...")
            full_chapter_list = self.navigator.get_all_chapters(novel_url)
            novel_data["chapters"] = full_chapter_list
            print(f"[+] Tổng số chương tìm thấy: {len(full_chapter_list)}")
    
            # 3. Duyệt qua từng chương để cào nội dung chi tiết (Ví dụ demo 2 chương đầu để tránh overload)
            # Bạn có thể bỏ `[:2]` để cào full bộ truyện khi chạy thực tế
            chapters_content = []
            for index, ch_info in enumerate(full_chapter_list[:2], start=1):
                print(f"   -> [{index}/{len(full_chapter_list)}] Đang cào nội dung chương: {ch_info['title']}")
                try:
                    ch_response = self.client.get(ch_info["url"])
                    ch_data = TruyenFullParser.parse_chapter_detail(ch_response.soup)
                    chapters_content.append({
                        "title": ch_data["title"],
                        "url": ch_info["url"],
                        "content": ch_data["content"]
                    })
                except Exception as e:
                    print(f"      [Lỗi] Không thể cào chương {ch_info['title']}: {e}")
                    continue
    
            # Thay thế danh sách link chương bằng danh sách có kèm nội dung chi tiết
            novel_data["chapters_content"] = chapters_content
            return novel_data
    

Hãy thận trọng khi sử dụng mã.

* * *

**🚀 Hướng dẫn Test chạy thử nghiệm toàn bộ hệ thống**

Tạo file `main.py` ở **thư mục gốc** (bên cạnh thư mục `plugins/`):

python
    
    
    # main.py
    import json
    from plugins.base.http_client import HTTPClient
    from plugins.truyenfull.source import TruyenFullSource
    
    def main():
        # 1. Khởi tạo HTTP Client dùng chung (có thể cấu hình proxy ở đây nếu muốn)
        client = HTTPClient(delay_range=(1.0, 2.0), max_retries=3)
        
        try:
            # 2. Truyền client vào module TruyenFull
            scraper = TruyenFullSource(client=client)
            
            # 3. Tiến hành cào thử một slug truyện (ví dụ: 'truyen-chu-tien')
            # Bạn có thể điền slug hoặc điền full URL đều được
            novel_result = scraper.crawl_novel("truyen-chu-tien")
            
            # 4. In kết quả thu hoạch được
            print("\n=== KẾT QUẢ CÀO TRUYỆN THÀNH CÔNG ===")
            print(f"Tên truyện: {novel_result['title']}")
            print(f"Tác giả: {novel_result['author']}")
            print(f"Thể loại: {', '.join(novel_result['genres'])}")
            print(f"Số lượng chương đã tải nội dung: {len(novel_result['chapters_content'])}")
            
            # Lưu kết quả ra file JSON xem cho đẹp
            with open("novel_output.json", "w", encoding="utf-8") as f:
                json.dump(novel_result, f, ensure_ascii=False, indent=4)
            print("[+] Đã xuất dữ liệu demo ra file 'novel_output.json'")
    
        finally:
            # Nhất định phải đóng client để giải phóng session mạng
            client.close()
    
    if __name__ == "__main__":
        main()
    

Hãy thận trọng khi sử dụng mã.

Bước tiếp theo, bạn có muốn xây dựng thêm một bộ **Save Manager** để tự động lưu dữ liệu truyện đã cào này trực tiếp vào **Cơ sở dữ liệu (SQLite/MongoDB)** hay xuất ra định dạng **Epub/Text** luôn không?

