## 1\. Domain Event là gì?

Trong kiến trúc DDD (Domain-Driven Design), Domain Event (Sự kiện Domain) là một khái niệm đại diện cho một điều gì đó quan trọng đã xảy ra trong quá khứ của hệ thống Domain và các phần khác cần biết.

  * Đặc điểm: Luôn được đặt tên ở thì quá khứ (Past tense) vì nó mô tả một sự kiện đã xảy ra và không thể thay đổi (Ví dụ: `NovelCrawled`, `ChapterParsed`, `CrawlFailed`).
  * Mục đích: Giúp các thành phần trong hệ thống giao tiếp lỏng lẻo (Decoupling) với nhau.
  * Ví dụ trong App Crawl Truyện: Khi cào xong một bộ truyện (`NovelCrawled`), hệ thống cần làm 3 việc:

    1. Gửi thông báo đến Telegram/Discord của admin.
    2. Tự động kích hoạt công cụ build file EPUB.
    3. Cập nhật trạng thái thống kê trên Dashboard.

Nếu không dùng Domain Event, code của lớp `Crawler` sẽ bị phình to (Wall of code) vì phải gọi trực tiếp module Telegram, module EPUB... Nếu dùng Domain Event, `Crawler` chỉ cần phát đi sự kiện `NovelCrawled`, các module khác tự lắng nghe và xử lý độc lập.



* * *

## 2\. Triển khai Domain Event như thế nào?

Chúng ta sẽ triển khai mô hình Pub/Sub (Publisher/Subscriber) nội bộ bằng Python thuần để tích hợp thẳng vào cấu trúc Async Crawler hiện tại.

## Bước 2.1: Định nghĩa các Base Classes (`domain/events/base.py`)

Tạo cấu trúc cơ bản cho Event và Event Bus (Bộ điều phối sự kiện).
    
    
    from abc import ABC
    from dataclasses import dataclass, field
    from datetime import datetime
    from typing import Callable, List, Dict, Type
    
    @dataclass
    class DomainEvent(ABC):
        """Lớp cơ sở cho mọi Domain Event"""
        occurred_on: datetime = field(default_factory=datetime.now)
    
    class DomainEventBus:
        """Bộ điều phối sự kiện tập trung (In-memory Event Bus)"""
        _subscribers: Dict[Type[DomainEvent], List[Callable]] = {}
    
        @classmethod
        def subscribe(cls, event_type: Type[DomainEvent], handler: Callable):
            """Đăng ký một hàm lắng nghe (Handler) cho một loại Event cụ thể"""
            if event_type not in cls._subscribers:
                cls._subscribers[event_type] = []
            cls._subscribers[event_type].append(handler)
    
        @classmethod
        async def publish(cls, event: DomainEvent):
            """Phát sự kiện đi, kích hoạt tất cả các Handler bất đồng bộ đang lắng nghe"""
            event_type = type(event)
            if event_type in cls._subscribers:
                for handler in cls._subscribers[event_type]:
                    try:
                        # Gọi handler dưới dạng async task
                        await handler(event)
                    except Exception as e:
                        print(f"[EventBus Error] Lỗi khi xử lý event {event_type.__name__}: {e}")
    

## Bước 2.2: Định nghĩa các Sự kiện Cụ thể (`domain/events/novel_events.py`)

Tạo các sự kiện thực tế diễn ra trong quá trình cào truyện.
    
    
    from dataclasses import dataclass
    from domain.events.base import DomainEvent
    
    @dataclass
    class ChapterDownloaded(DomainEvent):
        """Sự kiện xảy ra khi một chương được tải thành công"""
        novel_url: str
        chapter_number: float
        chapter_title: str
    
    @dataclass
    class NovelCrawlCompleted(DomainEvent):
        """Sự kiện xảy ra khi toàn bộ truyện được tải xong"""
        novel_url: str
        novel_title: str
        total_chapters: int
    

## Bước 2.3: Tích hợp Phát Event vào Lõi Crawler (`application/services/async_crawler.py`)

Crawler bây giờ không cần biết các hành động phụ phụ thuộc (Side effects) là gì, nó chỉ tập trung cào và gọi `DomainEventBus.publish()`.
    
    
    import asyncio
    import logging
    from domain.entities import Novel, Chapter
    from domain.services.interfaces import INovelFetcher
    from infrastructure.parsers.parser_factory import ParserFactory
    from domain.repositories import INovelRepository
    # Import Event Bus và Events
    from domain.events.base import DomainEventBus
    from domain.events.novel_events import ChapterDownloaded, NovelCrawlCompleted
    
    logger = logging.getLogger(__name__)
    
    class EventDrivenAsyncCrawler:
        def __init__(self, fetcher: INovelFetcher, repository: INovelRepository, max_workers: int = 5):
            self.fetcher = fetcher
            self.repository = repository
            self.semaphore = asyncio.Semaphore(max_workers)
    
        async def crawl_full_novel_async(self, start_url: str) -> Novel:
            parser = ParserFactory.get_parser(start_url)
            index_html = await self.fetcher.fetch_html(start_url)
            novel = parser.parse_novel_info(index_html, source_url=start_url)
            
            await asyncio.to_thread(self.repository.save_novel_meta, novel)
            
            tasks = [self._crawl_single_chapter(novel.source_url, chapter, parser) for chapter in novel.chapters]
            await asyncio.gather(*tasks)
            
            # 🔥 PHÁT EVENT: Toàn bộ truyện đã cào xong
            await DomainEventBus.publish(
                NovelCrawlCompleted(
                    novel_url=novel.source_url, 
                    novel_title=novel.title, 
                    total_chapters=len(novel.chapters)
                )
            )
            
            return await asyncio.to_thread(self.repository.find_by_url, novel.source_url)
    
        async def _crawl_single_chapter(self, novel_url: str, chapter: Chapter, parser):
            async with self.semaphore:
                try:
                    exists = await asyncio.to_thread(self.repository.is_chapter_exists, novel_url, chapter.number)
                    if exists:
                        return  
    
                    chapter_url = f"{novel_url}/chuong-{int(chapter.number)}"
                    chapter_html = await self.fetcher.fetch_html(chapter_url)
                    
                    parsed_chapter = parser.parse_chapter_content(chapter_html, chapter.number, chapter.title)
                    chapter.update_content(parsed_chapter.content)
                    
                    await asyncio.to_thread(self.repository.save_chapter, novel_url, chapter)
                    
                    # 🔥 PHÁT EVENT: Cào xong 1 chương đơn lẻ
                    await DomainEventBus.publish(
                        ChapterDownloaded(
                            novel_url=novel_url, 
                            chapter_number=chapter.number, 
                            chapter_title=chapter.title
                        )
                    )
                    
                except Exception as e:
                    logger.error(f"Lỗi tại {chapter.title}: {str(e)}")
    

## Bước 2.4: Đăng ký các Handler nhận Event ở tầng Infrastructure

Tạo các lớp xử lý ngoại vi độc lập nhận nhiệm vụ khi Event kích hoạt.
    
    
    # infrastructure/handlers/notification_handlers.py
    from domain.events.novel_events import NovelCrawlCompleted, ChapterDownloaded
    
    async def telegram_notification_handler(event: NovelCrawlCompleted):
        """Gửi tin nhắn Telegram khi cào xong truyện"""
        print(f"[Telegram Bot] 🚀 Đã cào xong truyện: {event.novel_title} ({event.total_chapters} chương)!")
    
    async def epub_exporter_handler(event: NovelCrawlCompleted):
        """Tự động kích hoạt build file EPUB khi truyện hoàn tất"""
        print(f"[Epub Exporter] 💾 Bắt đầu đóng gói file EPUB cho truyện tại nguồn: {event.novel_url}")
    
    async def progress_tracker_handler(event: ChapterDownloaded):
        """In tiến độ log real-time khi từng chương tải xong"""
        print(f"[Tracker] -> Đã lưu chương {event.chapter_number}: {event.chapter_title}")
    

## Bước 2.5: Khởi chạy và Liên kết hệ thống (`main.py`)
    
    
    import asyncio
    from infrastructure.fetchers.primp_fetcher import PrimpAsyncFetcher
    from infrastructure.repositories.sqlite_repository import SQLiteNovelRepository
    from domain.events.base import DomainEventBus
    from domain.events.novel_events import NovelCrawlCompleted, ChapterDownloaded
    
    # Import các Handlers độc lập
    from infrastructure.handlers.notification_handlers import (
        telegram_notification_handler, 
        epub_exporter_handler,
        progress_tracker_handler
    )
    
    async def main():
        # 1. Đăng ký (Subscribe) các Handler vào Event Bus TRƯỚC KHI CHẠY
        DomainEventBus.subscribe(NovelCrawlCompleted, telegram_notification_handler)
        DomainEventBus.subscribe(NovelCrawlCompleted, epub_exporter_handler)
        DomainEventBus.subscribe(ChapterDownloaded, progress_tracker_handler)
    
        # 2. Khởi tạo core app
        repo = SQLiteNovelRepository()
        fetcher = PrimpAsyncFetcher()
        crawler = EventDrivenAsyncCrawler(fetcher=fetcher, repository=repo, max_workers=3)
        
        # 3. Chạy tiến trình cào dữ liệu
        await crawler.crawl_full_novel_async("https://truyenfull.io")
    
    if __name__ == "__main__":
        asyncio.run(main())
    

Nếu bạn muốn nâng cấp sâu hơn về mặt kỹ thuật, hãy cho tôi biết:

  * Bạn có muốn hiện thực hóa phần code xử lý của `epub_exporter_handler` để xuất file EPUB thật sự từ Database SQLite không?
  * Hay bạn cần giải pháp chuyển giao diện Event Bus từ chạy nội bộ bộ nhớ (In-memory) sang hệ thống Message Queue độc lập như RabbitMQ hoặc Redis Pub/Sub để mở rộng quy mô chạy nhiều Worker?