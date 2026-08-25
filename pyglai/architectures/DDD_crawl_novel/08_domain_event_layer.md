Dưới đây là cách thiết kế và tích hợp Domain Event vào ứng dụng crawl truyện theo chuẩn Domain-Driven Design (DDD).

Khi một chương mới được `INSERT` thành công (không bị `IGNORE`), hệ thống sẽ tự động kích hoạt một sự kiện (Event). Sự kiện này sẽ thông báo cho các thành phần khác xử lý các tác vụ phụ phụ như gửi thông báo Telegram, tải ảnh minh họa, hoặc lập chỉ mục tìm kiếm (Indexing) mà không làm ảnh hưởng đến logic crawl chính.

* * *

## 1\. Thiết kế Base Domain Event (`domain/base.py`)

Đầu tiên, ta tạo một cơ chế quản lý Event cơ bản ngay trong các Entity của Domain.
    
    
    from abc import ABC
    from datetime import datetime
    from typing import List
    
    class DomainEvent(ABC):
        """Lớp cơ sở cho mọi Domain Event"""
        def __init__(self):
            self.occurred_on = datetime.now()
    
    class AggregateRoot:
        """Các Entity đóng vai trò Gốc (như Comic) sẽ kế thừa lớp này để quản lý Event"""
        def __init__(self):
            self._domain_events: List[DomainEvent] = []
    
        def register_event(self, event: DomainEvent):
            self._domain_events.append(event)
    
        def pull_domain_events(self) -> List[DomainEvent]:
            """Lấy ra toàn bộ event đã tích lũy và xóa sạch bộ nhớ đệm"""
            events = self._domain_events.copy()
            self._domain_events.clear()
            return events
    

* * *

## 2\. Định nghĩa Event "Chương Mới Được Thêm" (`domain/events.py`)

Định nghĩa sự kiện cụ thể chứa các thông tin cần thiết (Payload) mà tầng ứng dụng hoặc hạ tầng cần dùng.
    
    
    from .base import DomainEvent
    from .model import ComicId, ChapterId
    
    class ChapterCreatedEvent(DomainEvent):
        """Sự kiện kích hoạt khi một chương truyện mới được chèn thành công"""
        def __init__(self, comic_id: ComicId, chapter_id: ChapterId, number: int, title: str):
            super().__init__()
            self.comic_id = comic_id
            self.chapter_id = chapter_id
            self.number = number
            self.title = title
    

Cập nhật lại Entity `Comic` trong file `domain/model.py` để kế thừa từ `AggregateRoot`:
    
    
    from .base import AggregateRoot
    from .events import ChapterCreatedEvent
    # ... các import khác giữ nguyên ...
    
    class Comic(AggregateRoot):
        def __init__(self, id: ComicId, title: str, source_url: str, chapters: List[Chapter] = None):
            super().__init__()
            self.id = id
            self.title = title
            self.source_url = source_url
            self.chapters = chapters or []
    
        def create_and_add_chapter(self, chapter_id: ChapterId, number: int, title: str, content: str):
            """Domain Method: Tạo chương mới và đăng ký Event"""
            chapter = Chapter(id=chapter_id, comic_id=self.id, number=number, title=title, content=content)
            self.chapters.append(chapter)
            
            # Đăng ký sự kiện chương mới được tạo
            self.register_event(
                ChapterCreatedEvent(
                    comic_id=self.id, 
                    chapter_id=chapter.id, 
                    number=chapter.number, 
                    title=chapter.title
                )
            )
            return chapter
    

* * *

## 3\. Tạo Event Bus / Dispatcher (`application/event_bus.py`)

Event Bus đóng vai trò là tổng đài trung gian, nhận Event từ Domain và chuyển đến các Handler (bộ xử lý) tương ứng.
    
    
    from typing import Dict, List, Callable, Type
    from domain.base import DomainEvent
    
    class EventBus:
        def __init__(self):
            self._listeners: Dict[Type[DomainEvent], List[Callable]] = {}
    
        def subscribe(self, event_type: Type[DomainEvent], listener: Callable):
            """Đăng ký một hàm lắng nghe cho một loại Event cụ thể"""
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            self._listeners[event_type].append(listener)
    
        def dispatch(self, events: List[DomainEvent]):
            """Phát các event đến toàn bộ listeners"""
            for event in events:
                event_type = type(event)
                if event_type in self._listeners:
                    for listener in self._listeners[event_type]:
                        try:
                            listener(event)
                        except Exception as e:
                            print(f"Lỗi khi xử lý event {event_type.__name__}: {e}")
    

* * *

## 4\. Viết các Handlers ở tầng Hạ tầng (`infrastructure/handlers.py`)

Đây là nơi bạn thực thi các tác vụ phụ (Side-effects) như gửi Telegram, tải ảnh.
    
    
    import time
    from domain.events import ChapterCreatedEvent
    
    def telegram_notification_handler(event: ChapterCreatedEvent):
        """Giả lập gửi thông báo đến nhóm Telegram của độc giả"""
        # Bạn có thể dùng requests.post("https://telegram.org...") ở đây
        print(f"[Telegram Bot] 🔔 Báo chương mới! Truyện '{event.comic_id.value}' vừa có '{event.title}'.")
    
    def image_downloader_handler(event: ChapterCreatedEvent):
        """Giả lập quét nội dung để tải ảnh minh họa truyện nếu có"""
        print(f"[Image Downloader] 🏞️ Đang quét và tải ảnh minh họa cho chương: {event.chapter_id.value}")
    

* * *

## 5\. Kết hợp vào Application Service (`application/crawler_service.py`)

Cập nhật tầng điều phối để sau khi `Repository` lưu thành công bằng SQL (không bị lỗi, không bị ignore), hệ thống sẽ lấy Event ra và phát đi qua `EventBus`.
    
    
    from domain.model import ComicId, ChapterId
    from domain.repository import ComicRepository, ChapterRepository
    from .event_bus import EventBus
    
    class CrawlerApplicationService:
        def __init__(self, comic_repo: ComicRepository, chapter_repo: ChapterRepository, event_bus: EventBus):
            self.comic_repo = comic_repo
            self.chapter_repo = chapter_repo
            self.event_bus = event_bus
    
        def crawl_and_process_chapter(self, comic_id: ComicId, chapter_num: int, raw_title: str, raw_content: str):
            # 1. Lấy thực thể Comic từ DB lên RAM
            comic = self.comic_repo.get_by_id(comic_id)
            if not comic:
                return
    
            # 2. Gọi Domain logic để tạo chương và kích hoạt Event
            chapter_slug = f"{comic_id.value}-chuong-{chapter_num}"
            chapter_id = ChapterId(chapter_slug)
            
            # Thêm chương mới vào tập hợp (Aggregate)
            chapter = comic.create_and_add_chapter(chapter_id, chapter_num, raw_title, raw_content)
    
            # 3. Sử dụng kỹ thuật INSERT OR IGNORE / UPSERT ở tầng Repo
            # Nếu repo trả về số dòng ảnh hưởng > 0 (tức là có chèn mới thật, không bị IGNORE)
            is_inserted = self.chapter_repo.save_if_new(chapter) 
    
            if is_inserted:
                # 4. Thu thập các sự kiện từ Domain và phát đi qua Event Bus
                events = comic.pull_domain_events()
                self.event_bus.dispatch(events)
    

_(Lưu ý: Trong`ChapterRepository`, hàm `save_if_new` sẽ chạy lệnh `INSERT OR IGNORE` và dùng `cursor.rowcount` hoặc `changes()` để trả về `True` nếu có dòng mới được chèn, `False` nếu bị bỏ qua)._

* * *

## 6\. Khởi chạy toàn bộ hệ thống (`main.py`)
    
    
    from application.event_bus import EventBus
    from domain.events import ChapterCreatedEvent
    from infrastructure.handlers import telegram_notification_handler, image_downloader_handler
    from application.crawler_service import CrawlerApplicationService
    from domain.model import ComicId, Comic
    # Giả lập các repo đã có từ phần trước
    from infrastructure.sqlite_repository import SQLiteComicRepository, SQLiteChapterRepository 
    
    def main():
        # 1. Khởi tạo cấu hình Event Bus (Tổng đài)
        event_bus = EventBus()
        
        # Đăng ký các dịch vụ phụ lắng nghe sự kiện có chương mới
        event_bus.subscribe(ChapterCreatedEvent, telegram_notification_handler)
        event_bus.subscribe(ChapterCreatedEvent, image_downloader_handler)
    
        # 2. Khởi tạo Service điều phối
        comic_repo = SQLiteComicRepository("comics.db")
        chapter_repo = SQLiteChapterRepository("comics.db")
        crawler_service = CrawlerApplicationService(comic_repo, chapter_repo, event_bus)
    
        # 3. Giả lập tiến trình crawl
        comic_id = ComicId("linh-vuc")
        
        print("--- LẦN CÀO 1: Chương hoàn toàn mới ---")
        crawler_service.crawl_process_chapter(comic_id, 15, "Chương 15: Thần Binh", "Nội dung...")
        # Kết quả: Sẽ lưu vào DB thành công -> Kích hoạt gửi Telegram + Tải ảnh.
    
        print("\n--- LẦN CÀO 2: Cào lại chương cũ (Quét trùng) ---")
        crawler_service.crawl_process_chapter(comic_id, 15, "Chương 15: Thần Binh", "Nội dung...")
        # Kết quả: SQLite dùng INSERT OR IGNORE nên bỏ qua -> Không kích hoạt Event, không spam Telegram.
    
    if __name__ == "__main__":
        main()
    

## Lợi ích kiến trúc này mang lại cho App Crawl của bạn:

  1. Loại bỏ liên kết lỏng (Decoupling): Code crawl truyện của bạn hoàn toàn không biết đến sự tồn tại của Telegram API hay thư viện tải ảnh. Nếu sau này bạn muốn đổi sang gửi thông báo qua Discord hay Email, bạn chỉ cần viết thêm Handler và `subscribe` vào Event Bus, không cần sửa lại 1 dòng code crawl hay SQL nào.
  2. Xử lý bất đồng bộ dễ dàng: Nếu việc gửi Telegram hoặc tải ảnh bị chậm/lỗi mạng, nó sẽ không làm nghẽn tiến trình crawl chính (Bạn có thể dễ dàng chuyển các hàm Handler này chạy trên một Thread riêng biệt trong Event Bus).



Bạn có muốn tối ưu sâu hơn về việc quản lý cấu trúc dữ liệu của cấu hình Crawler (Crawl Rules/Xpath) bằng DDD để lưu các công thức cào của từng trang web khác nhau vào SQLite không?