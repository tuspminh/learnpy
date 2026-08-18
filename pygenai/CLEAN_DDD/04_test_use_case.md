Kiểm thử Application Layer cho ứng dụng đọc/crawl truyện tập trung vào việc kiểm tra Use Case (`IngestChapterUseCase`) điều phối đúng logic nghiệp vụ giữa `ExternalStoryScraper` và `StoryRepository` mà không cần kết nối mạng hay Database thật.

Sử dụng `pytest-asyncio`, **Fake Repository** và **`AsyncMock`** để cô lập hoàn toàn Use Case:

```python
from unittest.mock import AsyncMock
import pytest

from domain.authoring.entities import Story
from application.interfaces.scraper import ScrapedChapterDTO
from application.ingestion.use_cases import IngestChapterUseCase


# 1. Fake Repository triển khai Async Interface
class FakeStoryRepository:
    def __init__(self):
        self.stories: dict[str, Story] = {}

    async def get_by_id(self, story_id: str) -> Story | None:
        return self.stories.get(story_id)

    async def save(self, story: Story) -> None:
        self.stories[story.id] = story


# 2. Test Case 1: Crawl và nạp chương thành công
@pytest.mark.asyncio
async def test_ingest_chapter_success():
    # Arrange
    story = Story(title="Đao Kiếm Thần Hoàng", author_id="author_123")
    story_repo = FakeStoryRepository()
    await story_repo.save(story)

    # Mock Scraper trả về DTO giả lập
    mock_scraper = AsyncMock()
    mock_scraper.fetch_chapter.return_value = ScrapedChapterDTO(
        title="Chương 1: Mở đầu",
        content_raw="Đây là nội dung chương đầu tiên của bộ truyện.",
        chapter_number=1
    )

    use_case = IngestChapterUseCase(scraper=mock_scraper, story_repo=story_repo)

    # Act
    await use_case.execute(story_id=story.id, source_url="https://example.com/chuong-1")

    # Assert
    updated_story = await story_repo.get_by_id(story.id)
    assert len(updated_story.chapters) == 1
    
    chapter = updated_story.chapters[0]
    assert chapter.title == "Chương 1: Mở đầu"
    assert chapter.content.body == "Đây là nội dung chương đầu tiên của bộ truyện."
    assert chapter.content.word_count == 10
    
    # Xác minh Scraper đã được gọi đúng URL
    mock_scraper.fetch_chapter.assert_awaited_once_with("https://example.com/chuong-1")


# 3. Test Case 2: Bắt lỗi nghiệp vụ khi nội dung cào về bị rỗng
@pytest.mark.asyncio
async def test_ingest_chapter_fails_on_empty_content():
    # Arrange
    story = Story(title="Tuyệt Thế Vũ Thần", author_id="author_456")
    story_repo = FakeStoryRepository()
    await story_repo.save(story)

    mock_scraper = AsyncMock()
    mock_scraper.fetch_chapter.return_value = ScrapedChapterDTO(
        title="Chương lỗi",
        content_raw="   ",  # Trả về khoảng trắng
        chapter_number=1
    )

    use_case = IngestChapterUseCase(scraper=mock_scraper, story_repo=story_repo)

    # Act & Assert (Lỗi do Domain Value Object ChapterContent ném ra)
    with pytest.raises(ValueError, match="Nội dung chương không được để trống"):
        await use_case.execute(story_id=story.id, source_url="https://example.com/empty")

```

---

### Điểm cốt lõi khi Unit Test Use Case

* **Test hành vi điều phối**: Kiểm tra xem Use Case có lấy dữ liệu từ Scraper, tạo đúng Domain Entity và gọi `save()` xuống Repository hay không.
* **Kiểm tra Business Constraints**: Kiểm tra xem lỗi ném ra từ Domain Layer (như nội dung rỗng, thiếu thông tin) có được Use Case xử lý đúng cách không.
* **Tốc độ thực thi tối đa**: Vì không gọi HTTP Request hay DB I/O thực sự, hàng trăm Unit Test dạng này sẽ chạy hoàn tất trong vài milisecond.