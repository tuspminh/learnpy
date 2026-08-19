Dưới đây là ví dụ thực tế về việc áp dụng trọn vẹn 5 nguyên lý SOLID vào một dự án viết công cụ cào truyện chữ (Crawl Novel) bằng Python.

Bài toán đặt ra: Hệ thống cần cào nội dung truyện từ các trang web khác nhau (như TruyenFull, TangThuVien), sau đó lưu dữ liệu lại dưới các định dạng mong muốn (như file Text thuần hoặc lưu thẳng vào Database).

* * *

## ❌ Thiết kế tồi: Vi phạm nghiêm trọng SOLID

Hãy xem một đoạn code viết theo kiểu "mì ăn liền" (tất cả gộp chung vào một Class):
    
    
    import requests
    from bs4 import BeautifulSoup
    
    class NovelCrawler:
        def __init__(self, url):
            self.url = url
    
        def fetch_and_parse(self):
            # Vi phạm S: Vừa tải HTML, vừa phân tách dữ liệu (Parsing)
            # Vi phạm O: Nếu cào trang khác có cấu trúc HTML khác, ta phải sửa hàm này
            response = requests.get(self.url)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('h3', class_='title').text
            content = soup.find('div', class_='chapter-c').text
            return {"title": title, "content": content}
    
        def save_to_txt(self, data):
            # Vi phạm S: Kiêm luôn nhiệm vụ lưu trữ file
            # Vi phạm D: Class cấp cao tự dính chặt vào chi tiết lưu file cục bộ (I/O)
            with open(f"{data['title']}.txt", "w", encoding="utf-8") as f:
                f.write(data['content'])
                
        def save_to_mysql(self, data):
            # Vi phạm I: Ép buộc lớp này phải biết cả các hàm lưu Database
            print("Lưu vào MySQL...")
    

* * *

## Thiết kế chuẩn: Áp dụng trọn vẹn SOLID

Để khắc phục, chúng ta sẽ phân rã mã nguồn thành các cấu trúc độc lập và hướng tới tính trừu tượng.

## 1\. S - Single Responsibility (Đơn nhiệm) & O - Open/Closed (Đóng/Mở)

  * Tạo một lớp dữ liệu thuần túy (`NovelChapter`).
  * Tách biệt logic cào của từng trang web ra thành các Class riêng biệt. Khi có trang web mới, ta chỉ cần viết thêm Class mới chứ không sửa code cũ.


    
    
    from abc import ABC, abstractmethod
    from dataclasses import dataclass
    import requests
    from bs4 import BeautifulSoup
    
    @dataclass
    class NovelChapter:
        title: str
        content: str
    
    # Interface dành cho việc cào dữ liệu (DIP / OCP)
    class NovelParser(ABC):
        @abstractmethod
        def parse(self, html_content: str) -> NovelChapter:
            pass
    
    # Triển khai cụ thể cho trang TruyenFull
    class TruyenFullParser(NovelParser):
        def parse(self, html_content: str) -> NovelChapter:
            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.find('a', class_='chapter-title').text.strip()
            content = soup.find('div', class_='chapter-c').text.strip()
            return NovelChapter(title=title, content=content)
    
    # Triển khai cụ thể cho trang TangThuVien (Dễ dàng mở rộng mà không sửa code cũ)
    class TangThuVienParser(NovelParser):
        def parse(self, html_content: str) -> NovelChapter:
            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.find('h1', class_='chap-title').text.strip()
            content = soup.find('div', class_='chap-content').text.strip()
            return NovelChapter(title=title, content=content)
    

## 2\. I - Interface Segregation (Phân tách Interface)

Thay vì tạo một Interface `Storage` chung chung bắt buộc vừa phải biết lưu File, vừa phải biết dọn dẹp bộ nhớ đệm hay kết nối mạng, ta chia nhỏ Interface theo đúng mục đích sử dụng.
    
    
    class TextStorage(ABC):
        @abstractmethod
        def save_text(self, chapter: NovelChapter) -> None:
            pass
    
    class DatabaseStorage(ABC):
        @abstractmethod
        def save_to_db(self, chapter: NovelChapter) -> None:
            pass
    
    # Một lớp lưu file Text chỉ triển khai đúng thứ nó cần
    class LocalFileSaver(TextStorage):
        def save_text(self, chapter: NovelChapter) -> None:
            with open(f"{chapter.title}.txt", "w", encoding="utf-8") as f:
                f.write(chapter.content)
            print(f" Saved {chapter.title} to TXT File.")
    

## 3\. L - Liskov Substitution (Thay thế Liskov)

Mọi Parser kế thừa từ `NovelParser` phải trả về đúng cấu trúc `NovelChapter` và không được phép quăng ra các lỗi làm sập luồng chính một cách bất ngờ, đảm bảo có thể thay thế cấu trúc cào của các trang web cho nhau một cách mượt mà.

## 4\. D - Dependency Inversion (Đảo ngược phụ thuộc) + DI

Class điều phối cốt lõi (`NovelCrawlerEngine`) là module cấp cao. Nó sẽ không tự tạo `requests`, không tự chọn trang web để cào, và không tự mở file để ghi.

Nó nhận mọi thứ thông qua Dependency Injection (Constructor Injection).
    
    
    class NovelCrawlerEngine:
        # DI: Bơm Parser (Tính trừu tượng) và Storage (Tính trừu tượng) vào qua init
        def __init__(self, parser: NovelParser, storage: TextStorage):
            self.parser = parser
            self.storage = storage
    
        def crawl(self, url: str) -> None:
            # 1. Tải HTML (Có thể tách riêng thành NetworkService nếu muốn chuẩn S nữa)
            response = requests.get(url)
            if response.status_code != 200:
                print("Lỗi tải trang!")
                return
    
            # 2. Xử lý dữ liệu thông qua Interface (DIP)
            chapter_data = self.parser.parse(response.text)
    
            # 3. Lưu trữ dữ liệu thông qua Interface (DIP)
            self.storage.save_text(chapter_data)
    

* * *

## Cấu hình và Vận hành linh hoạt

Nhờ áp dụng SOLID, việc kết hợp và thay đổi các thành phần của mã nguồn trở nên vô cùng trực quan và linh hoạt:
    
    
    if __name__ == "__main__":
        # TÌNH HUỐNG 1: Cào truyện từ TruyenFull và lưu thành file Text cục bộ
        truyen_full_url = "https://truyenfull.vn"
        
        engine1 = NovelCrawlerEngine(
            parser=TruyenFullParser(), 
            storage=LocalFileSaver()
        )
        # engine1.crawl(truyen_full_url)
    
    
        # TÌNH HUỐNG 2: Đổi sang cào TangThuVien, hệ thống chính GIỮ NGUYÊN CODE
        # Giả sử ta viết thêm lớp MongoSaver triển khai từ TextStorage/DatabaseStorage
        class MongoSaver(TextStorage):
            def save_text(self, chapter: NovelChapter) -> None:
                print(f" Inserting {chapter.title} into MongoDB...")
    
        tang_thu_vien_url = "https://tangthuvien.vn"
        
        engine2 = NovelCrawlerEngine(
            parser=TangThuVienParser(), # Đổi bộ cào mới
            storage=MongoSaver()        # Đổi cơ sở dữ liệu mới
        )
        # engine2.crawl(tang_thu_vien_url)
    

* * *

## Tổng kết lợi ích trong bài toán Crawl truyện

  1. Đối phó khi giao diện web thay đổi: Nếu trang TruyenFull đổi class HTML từ `chapter-c` thành `content-chap`, bạn chỉ cần vào đúng lớp `TruyenFullParser` sửa lại đúng 1 dòng code. Toàn bộ logic tải trang hay lưu file hoàn toàn không bị ảnh hưởng.
  2. Cào đa luồng (Async/Thread): Khi muốn nâng cấp `NovelCrawlerEngine` lên cào đa luồng để tăng tốc độ, bạn có thể tự tin sửa đổi lớp này mà không sợ làm hỏng logic bóc tách dữ liệu HTML của các trang web.



Nếu bạn muốn, tôi có thể hướng dẫn tiếp:

  * Cách viết Unit Test Mocking cho bộ cào truyện này để chạy test mà không cần gọi mạng thật.
  * Cách nâng cấp lớp `NovelCrawlerEngine` thành Bất đồng bộ (Asyncio) để cào hàng loạt chương truyện cùng một lúc.