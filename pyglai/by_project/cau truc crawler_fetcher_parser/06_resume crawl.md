Để tích hợp tính năng Resume Crawl (tiếp tục cào từ điểm bị ngắt quãng) vào cấu trúc DDD, chúng ta chỉ cần cập nhật logic điều phối của Crawler Engine ở tầng Application.

Nhờ cấu trúc bóc tách lớp (Decoupling) của DDD, chúng ta không cần sửa đổi tầng Domain hay tầng DB (SQLite Repository), mà chỉ cần tận dụng hàm `is_chapter_exists` đã viết ở bước trước để đưa ra quyết định bỏ qua (skip) chương cũ.

Dưới đây là mã nguồn nâng cấp chi tiết cho Crawler Engine hỗ trợ tính năng tự động bỏ qua chương cũ và tối ưu hóa luồng tải:

## 1\. Nâng cấp Crawler Engine (`application/services/novel_crawler.py`)
    
    
    import logging
    import time
    import random
    from domain.entities import Novel, Chapter
    from domain.services.interfaces import INovelFetcher
    from infrastructure.parsers.parser_factory import ParserFactory
    from domain.repositories import INovelRepository
    
    logger = logging.getLogger(__name__)
    
    class ResumableNovelCrawler:
        """Crawler Engine thông minh hỗ trợ Resume Crawl và Fault Tolerance"""
        
        def __init__(self, fetcher: INovelFetcher, repository: INovelRepository):
            self.fetcher = fetcher
            self.repository = repository
    
        def crawl_full_novel(self, start_url: str) -> Novel:
            logger.info(f"🔄 Đang kiểm tra tiến trình cào truyện tại: {start_url}")
            
            # BƯỚC 1: Xác định Parser tương ứng với trang web
            parser = ParserFactory.get_parser(start_url)
            
            # BƯỚC 2: Tải trang mục lục để lấy thông tin meta và danh sách chương thô
            index_html = self.fetcher.fetch_html(start_url)
            novel = parser.parse_novel_info(index_html, source_url=start_url)
            
            logger.info(f"📖 Truyện: {novel.title} | Tổng số chương trên nguồn: {len(novel.chapters)}")
            
            # BƯỚC 3: Lưu hoặc cập nhật thông tin tổng quan của truyện vào DB trước
            self.repository.save_novel_meta(novel)
    
            # Thống kê tiến độ crawl
            skipped_count = 0
            crawled_count = 0
    
            # BƯỚC 4: Vòng lặp tải nội dung chi tiết từng chương (Có kiểm tra Resume)
            for chapter in novel.chapters:
                try:
                    # ── KIỂM TRA RESUME CRUISE ──
                    # Nếu chương này đã tồn tại đầy đủ trong SQLite -> Bỏ qua không cào lại
                    if self.repository.is_chapter_exists(novel.source_url, chapter.number):
                        skipped_count += 1
                        continue
                    
                    # Giả định URL của chương được build từ domain nguồn
                    chapter_url = self._build_chapter_url(novel.source_url, chapter)
                    
                    logger.info(f"⏳ [Mới] Đang cào: {chapter.title} (Số: {chapter.number})")
                    
                    # Tải mã HTML của trang đọc truyện
                    chapter_html = self.fetcher.fetch_html(chapter_url)
                    
                    # Phân tích cú pháp lấy nội dung văn bản chữ sạch
                    parsed_chapter = parser.parse_chapter_content(
                        html_content=chapter_html, 
                        number=chapter.number, 
                        title=chapter.title
                    )
                    
                    # Cập nhật nội dung sạch vào entity
                    chapter.update_content(parsed_chapter.content)
                    
                    # Ghi nhận ngay vào SQLite để đánh dấu "đã cào thành công"
                    self.repository.save_chapter(novel.source_url, chapter)
                    crawled_count += 1
                    
                    # Giãn cách tải an toàn để tránh bị kích hoạt Cloudflare / Ban IP
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    logger.error(f"❌ Lỗi nghiêm trọng tại {chapter.title}: {str(e)}")
                    # Fault Tolerance: Lỗi chương này thì bỏ qua để cào tiếp chương sau, không làm sập cả app
                    continue
                    
            logger.info(f"🏁 Hoàn thành tiến trình: Đã bỏ qua {skipped_count} chương cũ | Tải mới thành công {crawled_count} chương.")
            
            # Trả về domain object hoàn chỉnh nạp ngược từ Database sau khi cào
            return self.repository.find_by_url(novel.source_url)
    
        def _build_chapter_url(self, novel_url: str, chapter: Chapter) -> str:
            # Tùy biến logic ghép link theo quy chuẩn của từng site nguồn
            if novel_url.endswith('/'):
                return f"{novel_url}chuong-{int(chapter.number)}"
            return f"{novel_url}/chuong-{int(chapter.number)}"
    

* * *

## 2\. Kịch bản vận hành thực tế (Cách hoạt động)

  * Lần chạy thứ 1: Bạn bắt đầu cào bộ truyện `A` gồm 100 chương. Hệ thống tải xong đến chương 45 thì mạng nhà bạn bị rớt, hoặc bạn chủ động tắt terminal bấm `Ctrl + C`. SQLite đã lưu chính xác 45 chương từ 1 đến 45.
  * Lần chạy thứ 2: Bạn bật lại terminal chạy đúng lệnh cũ với URL cũ.

    1. Bộ điều phối vẫn quét danh sách 100 chương thô từ nguồn về.
    2. Khi chạy vòng lặp, từ chương 1 đến chương 45, hàm `is_chapter_exists` check trong DB thấy kết quả là `True` -> Lập tức bỏ qua trong `0.001s` mà không gửi bất kỳ HTTP Request nào lên mạng.
    3. Đến chương 46, DB trả về `False` -> Hệ thống tự động kích hoạt Fetcher tải tiếp từ chương 46 cho đến hết.




Để tối ưu hóa toàn diện dự án này, bạn có muốn triển khai tiếp:

  * Cơ chế Asyncio (Bất đồng bộ) để tăng tốc độ cào (vừa hỗ trợ Resume vừa cào song song 5-10 chương cùng lúc)?
  * Tạo một lớp Export Service để tự động đóng gói dữ liệu trong SQLite thành định dạng EPUB / TXT?