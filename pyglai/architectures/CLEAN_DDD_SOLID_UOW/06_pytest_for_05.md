Dưới đây là hướng dẫn viết Unit Test sử dụng `pytest` cho dự án crawl truyện của bạn.

Điểm đặc biệt ở đây là nhờ áp dụng triệt để nguyên lý D (Dependency Inversion) và cấu trúc Clean Architecture, bạn có thể kiểm thử toàn bộ logic của tầng `Application` (Use Case) mà không cần tạo file SQLite thật và không cần kết nối Internet. Chúng ta sẽ tạo ra các bản "giả lập" (Fake/Mock) chạy hoàn toàn trên bộ nhớ RAM, giúp bài test chạy cực nhanh (chỉ mất vài phần mười giây).

## 🛠️ Chuẩn bị môi trường

Trước tiên, hãy cài đặt `pytest` bằng lệnh:
    
    
    pip install pytest
    

* * *

## 💻 Triển khai Code Unit Test

Tạo một file có tên `test_crawl_use_case.py` để kiểm thử tính năng cào và lưu truyện.
    
    
    # test_crawl_use_case.py
    import pytest
    from typing import Optional, List
    
    # --- IMPORT CÁC THÀNH PHẦN TRỪU TƯỢNG (INTERFACES) TỪ LAYER APPLICATION/DOMAIN ---
    from src.domain.models import Story
    from src.domain.repositories import StoryRepository, CrawlService
    from src.application.unit_of_work import AbstractUnitOfWork
    from src.application.use_cases import CrawlStoryUseCase
    
    
    # --- 1. TẠO CÁC LỚP GIẢ LẬP (FAKE OBJECTS) CHẠY TRÊN RAM ---
    # Các lớp này tuân thủ nguyên lý D (SOLID), kế thừa Interface để thay thế SQLite và Network thật.
    
    class FakeStoryRepository(StoryRepository):
        """Giả lập kho lưu trữ truyện bằng một từ điển (dict) thuần Python trong RAM."""
        def __init__(self):
            self.saved_stories = {}
    
        def save(self, story: Story) -> None:
            self.saved_stories[story.story_id] = story
    
        def get_by_id(self, story_id: str) -> Optional[Story]:
            return self.saved_stories.get(story_id)
    
        def list_all(self) -> List[Story]:
            return list(self.saved_stories.values())
    
    
    class FakeUnitOfWork(AbstractUnitOfWork):
        """Giả lập Unit of Work. Quản lý transaction trên RAM, theo dõi xem đã commit chưa."""
        def __init__(self):
            self.stories = FakeStoryRepository()
            self.committed = False
    
        def commit(self):
            self.committed = True
    
        def rollback(self):
            pass
    
    
    class FakeCrawlService(CrawlService):
        """Giả lập Crawler. Trả về dữ liệu cố định mà không cần cào qua HTTP."""
        def fetch_story_details(self, url: str) -> Story:
            story = Story(story_id="test-id-123", title="Truyện Test SOLID", author="Tác Giả AI", url=url)
            story.add_chapter("Chương 1", "Nội dung chương 1 giả lập...")
            return story
    
    
    # --- 2. VIẾT CÁC BÀI UNIT TEST VỚI PYTEST ---
    
    def test_crawl_story_use_case_success():
        """
        Kịch bản: Người dùng truyền vào một đường dẫn truyện hợp lệ.
        Kỳ vọng: 
        1. Hàm execute trả về đúng ID của truyện.
        2. Truyện được lưu thành công vào kho (Repository).
        3. Dữ liệu của truyện và các chương phải chính xác.
        4. Unit of Work phải kích hoạt lệnh commit().
        """
        # Arrange (Chuẩn bị các thành phần phụ thuộc dạng Fake)
        fake_uow = FakeUnitOfWork()
        fake_crawler = FakeCrawlService()
        
        # Khởi tạo Use Case thực tế cần test, tiêm các bản Fake vào (Dependency Injection)
        use_case = CrawlStoryUseCase(uow=fake_uow, crawler=fake_crawler)
        test_url = "https://truyen-gia-lap.com"
    
        # Act (Thực thi hành động)
        returned_id = use_case.execute(test_url)
    
        # Assert (Kiểm tra kết quả xem có đúng như kỳ vọng không)
        assert returned_id == "test-id-123"
        assert fake_uow.committed is True  # Đảm bảo dữ liệu đã được ra lệnh commit an toàn
        
        # Truy vấn lại từ kho lưu trữ RAM xem dữ liệu có toàn vẹn không
        saved_story = fake_uow.stories.get_by_id(returned_id)
        assert saved_story is not None
        assert saved_story.title == "Truyện Test SOLID"
        assert saved_story.author == "Tác Giả AI"
        assert len(saved_story.chapters) == 1
        assert saved_story.chapters[0].title == "Chương 1"
        assert saved_story.chapters[0].content == "Nội dung chương 1 giả lập..."
    
    
    def test_crawl_story_use_case_rollback_on_error():
        """
        Kịch bản: Quá trình lưu truyện vào Database xảy ra lỗi hệ thống bất ngờ.
        Kỳ vọng: 
        1. Hệ thống ném ra lỗi ngoại lệ.
        2. Unit of Work KHÔNG được phép gọi lệnh commit() để bảo vệ dữ liệu.
        """
        # Arrange
        fake_uow = FakeUnitOfWork()
        fake_crawler = FakeCrawlService()
        
        # Cố tình phá hoại: Ghi đè hàm save của Repository để nó luôn ném ra lỗi
        def raise_db_error(story):
            raise RuntimeError("SQLite bị khóa hoặc đầy ổ cứng!")
        fake_uow.stories.save = raise_db_error
    
        use_case = CrawlStoryUseCase(uow=fake_uow, crawler=fake_crawler)
    
        # Act & Assert
        # Kiểm tra xem Use Case có ném ra lỗi như kịch bản không
        with pytest.raises(RuntimeError, match="SQLite bị khóa hoặc đầy ổ cứng!"):
            use_case.execute("https://any-url.com")
    
        # Quan trọng nhất: Vì lỗi xảy ra bên trong khối `with uow:`, lệnh commit KHÔNG được chạy
        assert fake_uow.committed is False
    

* * *

## 🚀 Cách chạy Test

Bạn mở Terminal tại thư mục chứa file test và gõ lệnh:
    
    
    pytest test_crawl_use_case.py -v
    

Kết quả màn hình sẽ hiển thị xanh (Passed) tương tự như sau:
    
    
    =========================== test session starts ===========================
    collected 2 items
    
    test_crawl_use_case.py::test_crawl_story_use_case_success PASSED     [ 50%]
    test_crawl_use_case.py::test_crawl_story_use_case_rollback_on_error PASSED [100%]
    
    ============================ 2 passed in 0.03s ============================
    

## 🧠 Lợi ích lớn từ kiến trúc này mang lại cho việc Test:

  1. Tốc độ ánh sáng: Hãy nhìn vào dòng `2 passed in 0.03s` (chỉ mất 0.03 giây). Nếu bạn mở kết nối Internet để cào và tạo file `.db` thật trên ổ cứng cho mỗi bài test, thời gian có thể mất từ vài giây đến vài chục giây. Khi dự án có hàng nghìn bài test, sự khác biệt này là khổng lồ.
  2. Kiểm thử độc lập: Bạn đang test logic của Use Case, nên bạn không cần lo lắng về việc mạng internet bị rớt hay file SQLite bị phân mảnh. Bài test chỉ tập trung chứng minh: _"Nếu Crawler trả về dữ liệu A, thì Use Case phải xử lý và đưa vào UoW đúng quy trình B"_.



Bạn có muốn phát triển tiếp bằng cách chuyển đổi lớp `FakeCrawlService` thành một lớp Crawler thật sử dụng `BeautifulSoup` để cào dữ liệu từ một trang web cụ thể không?