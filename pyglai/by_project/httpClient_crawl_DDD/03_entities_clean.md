Dưới đây là cách xây dựng lớp Domain Models & Entities cho ứng dụng crawl truyện chữ theo triết lý Domain-Driven Design (DDD).

Trong DDD, Domain layer là trung tâm của ứng dụng, hoàn toàn cô lập với cơ sở dữ liệu (Database) hay các thư viện crawl (HTTPX, BeautifulSoup). Mọi quy tắc nghiệp vụ (Business Rules) như làm sạch nội dung chương, chuẩn hóa tiêu đề, hay kiểm tra tính hợp lệ của truyện đều nằm tại đây.

* * *

## 1\. Kiến trúc thư mục Domain
    
    
    src/domain/story/
    ├── __init__.py
    ├── value_objects.py   # Chứa các thuộc tính không định danh (Url, ChapterContent)
    └── entities.py        # Chứa các đối tượng có định danh riêng (Novel, Chapter)
    

* * *

## 2\. Triển khai Mã nguồn

## Lớp Value Objects (`domain/story/value_objects.py`)

Value Object không có định danh (`id`), tính bất biến (Immutable), và dùng để đóng gói logic xác thực hoặc biến đổi dữ liệu thô.
    
    
    import re
    from dataclasses import dataclass
    
    @dataclass(frozen=True)
    class StoryUrl:
        """Value Object quản lý và chuẩn hóa URL của truyện/chương."""
        value: str
    
        def __post_init__(self):
            # Validate định dạng URL cơ bản
            if not self.value.startswith(("http://", "https://")):
                raise ValueError(f"URL không hợp lệ: {self.value}")
    
        @property
        def domain(self) -> str:
            """Trích xuất domain để phục vụ nhận diện nguồn crawler."""
            match = re.search(r"https?://([^/]+)", self.value)
            return match.group(1) if match else ""
    
    
    @dataclass(frozen=True)
    class ChapterContent:
        """Value Object quản lý nội dung chữ của chương truyện, tự động làm sạch (Clean text)."""
        raw_html: str
    
        @property
        def clean_text(self) -> str:
            """Loại bỏ mã HTML rác, quảng cáo và chuẩn hóa khoảng trắng."""
            text = self.raw_html
            
            # 1. Thay thế các thẻ xuống dòng phổ biến bằng dấu xuống dòng thực tế
            text = re.sub(r"<br\s*/?>|</p>", "\n", text)
            
            # 2. Xóa bỏ tất cả các thẻ HTML còn lại
            text = re.sub(r"<[^>]+>", "", text)
            
            # 3. Loại bỏ các dòng quảng cáo thường gặp ở các web truyện chữ
            ad_keywords = [
                r"truyenfull", r"đọc truyện tại", r"chúc bạn đọc truyện vui vẻ", 
                r"nguồn:", r"vào nhóm facebook", r"tải app"
            ]
            lines = text.split("\n")
            cleaned_lines = []
            for line in lines:
                line_strip = line.strip()
                # Bỏ qua dòng nếu chứa từ khóa quảng cáo
                if any(re.search(kw, line_strip, re.IGNORECASE) for kw in ad_keywords):
                    continue
                cleaned_lines.append(line_strip)
                
            # 4. Gộp các dòng trống liên tiếp và xóa khoảng trắng thừa
            final_text = "\n".join([l for l in cleaned_lines if l])
            return final_text
    

## Lớp Entities & Aggregate Root (`domain/story/entities.py`)

Entity là các đối tượng có định danh duy nhất (`id`). Ở đây `Novel` đóng vai trò là Aggregate Root (Gốc tổng hợp) để quản lý vòng đời của các `Chapter`.
    
    
    from typing import List, Optional
    from domain.story.value_objects import StoryUrl, ChapterContent
    
    class Chapter:
        """Entity đại diện cho một chương truyện."""
        
        def __init__(self, chapter_id: str, number: float, title: str, content: Optional[ChapterContent] = None):
            self.id = chapter_id          # Định danh duy nhất (ví dụ: mã băm hoặc uuid)
            self.number = number          # Số chương (dùng float hỗ trợ chương 1.5, 100.2)
            self.title = title.strip()
            self.content = content
    
        def update_content(self, raw_html: str) -> None:
            """Hành vi nghiệp vụ: Cập nhật nội dung thô cho chương."""
            self.content = ChapterContent(raw_html=raw_html)
    
        def is_downloaded(self) -> bool:
            """Kiểm tra chương đã có nội dung chữ chưa."""
            return self.content is not None and len(self.content.clean_text) > 0
    
    
    class Novel:
        """Aggregate Root đại diện cho một bộ truyện chữ."""
        
        def __init__(self, novel_id: str, title: str, author: str, url: StoryUrl):
            self.id = novel_id
            self.title = title.strip()
            self.author = author.strip()
            self.url = url
            self._chapters: List[Chapter] = []  # Danh sách chương nội bộ
    
        @property
        def chapters(self) -> List[Chapter]:
            """Trả về bản sao danh sách chương để bảo vệ tính đóng gói (Encapsulation)."""
            return self._chapters.copy()
    
        def add_chapter(self, chapter: Chapter) -> None:
            """Hành vi nghiệp vụ: Thêm chương mới vào bộ truyện và kiểm tra trùng lặp."""
            if any(c.id == chapter.id or c.number == chapter.number for c in self._chapters):
                # Có thể log hoặc bỏ qua nếu chương đã tồn tại
                return
            self._chapters.append(chapter)
            # Sắp xếp chương theo thứ tự tăng dần
            self._chapters.sort(key=lambda c: c.number)
    
        def get_total_chapters(self) -> int:
            return len(self._chapters)
    
        def get_undownloaded_chapter_urls(self, base_crawler_mapping_func) -> List[dict]:
            """Lấy danh sách các chương chưa cào nội dung để đưa vào Queue Crawl."""
            undownloaded = []
            for c in self._chapters:
                if not c.is_downloaded():
                    # Hàm callback từ infrastructure sẽ tính toán URL thực tế dựa trên số chương và domain truyện
                    chapter_url = base_crawler_mapping_func(self.url.value, c.number)
                    undownloaded.append({"chapter_id": c.id, "url": chapter_url})
            return undownloaded
    

* * *

## 3\. Cách Vận hành trong UseCase / Application Service

Đây là cách phối hợp giữa HTTP Client (đã làm ở bước trước) và Domain Models để thực hiện nghiệp vụ tải một chương truyện.
    
    
    # ví dụ chạy ứng dụng tại lớp Application / UseCase
    from domain.story.entities import Novel, Chapter
    from domain.story.value_objects import StoryUrl
    
    # 1. Khởi tạo thực thể bộ truyện từ Domain
    novel_url = StoryUrl("https://truyen-kiem-hiep.com")
    novel = Novel(novel_id="novel_001", title="Tiếu Ngạo Giang Hồ", author="Kim Dung", url=novel_url)
    
    # 2. Giả lập việc parse danh sách chương từ trang Index và đưa vào Domain
    chapter_1 = Chapter(chapter_id="ch_01", number=1.0, title="Chương 1: Diệt Môn")
    novel.add_chapter(chapter_1)
    
    # 3. Tiến hành cào nội dung chương bằng HTTP Client
    raw_html_from_web = """
    <div id="content">
        <p>TruyenFull xin chào độc giả.</p>
        <p>Lệnh Hồ Xung đang ngồi uống rượu một mình bên bờ sông...</p>
        <br/>
        <p>Đọc truyện tại truyen-kiem-hiep.com để ủng hộ nhóm dịch.</p>
    </div>
    """
    
    # Tìm đúng thực thể chương trong Domain và ra lệnh cập nhật nội dung
    for chapter in novel.chapters:
        if chapter.id == "ch_01":
            chapter.update_content(raw_html_from_web)
            
            # In kết quả kiểm tra
            print(f"--- {novel.title} - {chapter.title} ---")
            print("[Nội dung thô ban đầu]:", repr(chapter.content.raw_html))
            print("\n[Nội dung SẠCH sau khi xử lý bởi Domain]:")
            print(chapter.content.clean_text)
    

## 💡 Điểm cốt lõi đạt được theo đúng DDD:

  1. Tính đóng gói tối đa (Encapsulation): Thuộc tính `_chapters` của `Novel` được ẩn đi (`private`). Bạn không thể thực hiện thao tác thô như `novel.chapters.append()` từ bên ngoài, bắt buộc phải đi qua phương thức nghiệp vụ `novel.add_chapter()`. Điều này đảm bảo danh sách chương luôn được kiểm tra trùng lặp và tự động sắp xếp.
  2. Logic nghiệp vụ tự chứa (Rich Domain Model): Việc làm sạch văn bản quảng cáo và tách thẻ HTML (`clean_text`) là trách nhiệm của dữ liệu (`ChapterContent`). Nó không nằm ở tầng lưu trữ hay giao diện, giúp bạn dễ dàng viết Unit Test độc lập cho phần làm sạch chữ này mà không cần bật mạng hay bật database.



Để khép kín chu trình lưu trữ dữ liệu sau khi cào sạch, bạn có muốn chúng ta xây dựng tiếp lớp Repository Pattern để lưu bộ truyện này vào Database (SQLite/MongoDB sử dụng Motor async) hay lưu trực tiếp thành tệp tin TXT / EPUB không?