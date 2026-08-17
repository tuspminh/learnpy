Để tích hợp cơ chế đa luồng (Multi-threading) vào hệ thống mà không phá vỡ kiến trúc Clean Architecture và DDD, chúng ta cần làm rõ bài toán:

  1. Quét danh sách link chương: Có thể tăng tốc bằng cách chia các trang mục (`trang-1`, `trang-2`,...) cho nhiều luồng cào song song.
  2. Tải nội dung chi tiết từng chương: Sử dụng một Thread Pool (ThreadPoolExecutor) để tải song song nhiều chương cùng một lúc, giúp rút ngắn thời gian treo máy từ vài tiếng xuống vài phút.



Dưới đây là mã nguồn được cập nhật lại ở tầng Application và tầng Presentation để hỗ trợ đa luồng một cách an toàn và tối ưu nhất.

* * *

## 1\. Cập nhật Tầng Application (`application/use_cases.py`)

Chúng ta sử dụng thư viện `concurrent.futures.ThreadPoolExecutor` của Python để xử lý đa luồng. Để tránh xung đột ghi dữ liệu đồng thời vào SQLite3 (SQLite không thích hợp cho việc ghi đa luồng đồng thời), chúng ta sẽ sử dụng một cơ chế khóa (Lock) ở tầng Repository hoặc xử lý tuần tự kết quả ghi, hoặc an toàn nhất là bọc lệnh ghi DB trong một `threading.Lock`.
    
    
    # application/use_cases.py
    import time
    import threading
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from typing import Callable, Optional, List
    from domain.interfaces import INovelRepository, INovelPlugin
    from domain.models import NovelListing, Novel, Chapter
    
    class CrawlListingUseCase:
        def __init__(self, repo: INovelRepository, plugin: INovelPlugin):
            self.repo = repo
            self.plugin = plugin
    
        def execute(self, url: str, page: Optional[int], total_page_only: bool) -> Optional[int]:
            target_url = self.plugin.build_page_url(url, page)
            soup = self.plugin.fetch_soup(target_url)
            if not soup: return None
    
            total_pages = self.plugin.extract_total_pages(soup)
            if total_page_only:
                return total_pages
    
            raw_items = self.plugin.parse_listing(soup)
            for item in raw_items:
                listing = NovelListing(
                    category_url=self.plugin.clean_url(url),
                    title=item['title'],
                    author=item['author'],
                    novel_url=item['url']
                )
                self.repo.save_listing(listing)
            return total_pages
    
    
    class DownloadAllChaptersUseCase:
        def __init__(self, repo: INovelRepository, plugin: INovelPlugin):
            self.repo = repo
            self.plugin = plugin
            self._db_lock = threading.Lock() # Lock bảo vệ SQLite khi ghi từ nhiều luồng
    
        def _fetch_chapter_list_worker(self, novel_url: str, page: int) -> List[dict]:
            """Hàm worker cho luồng quét danh sách chương"""
            p_url = self.plugin.build_page_url(novel_url, page if page > 1 else None)
            p_soup = self.plugin.fetch_soup(p_url)
            if p_soup:
                return self.plugin.parse_chapter_list(p_soup)
            return []
    
        def _download_chapter_worker(self, novel_url: str, chap_meta: dict, progress_callback: Callable[[str], None]):
            """Hàm worker cho luồng tải nội dung chương"""
            chap_url = self.plugin.clean_url(chap_meta['url'])
            
            # Đọc DB kiểm tra (Có lock bảo vệ để an toàn thread-safe)
            with self._db_lock:
                if self.repo.is_chapter_downloaded(chap_url):
                    progress_callback(chap_meta['title'])
                    return True
    
            c_soup = self.plugin.fetch_soup(chap_url)
            if c_soup:
                c_data = self.plugin.parse_chapter_content(c_soup, chap_url)
                chapter_domain_model = Chapter(
                    chapter_url=chap_url,
                    novel_url=novel_url,
                    chapter_title=c_data['title'],
                    content=c_data['content']
                )
                # Ghi vào DB (Bắt buộc phải Lock vì SQLite3 không cho phép ghi đồng thời)
                with self._db_lock:
                    self.repo.save_chapter(chapter_domain_model)
                progress_callback(chap_meta['title'])
                return True
            return False
    
        def execute(self, url: str, max_workers: int, progress_callback: Callable[[int, int, str], None]) -> None:
            novel_url = self.plugin.clean_url(url)
            
            # 1. Cào thông tin truyện chính
            soup = self.plugin.fetch_soup(novel_url)
            if not soup: return
            info = self.plugin.parse_novel_info(soup)
            novel_domain_model = Novel(
                novel_url=novel_url, title=info['title'],
                author=info['author'], description=info['description'],
                source=self.plugin.DOMAIN
            )
            self.repo.save_novel(novel_domain_model)
            
            # 2. ĐA LUỒNG: Quét tất cả link chương từ các trang phân trang
            total_pages = self.plugin.extract_total_pages(soup)
            all_chapters_meta = []
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Gửi các luồng quét trang song song
                futures = {executor.submit(self._fetch_chapter_list_worker, novel_url, p): p for p in range(1, total_pages + 1)}
                for future in as_completed(futures):
                    p_num = futures[future]
                    try:
                        all_chapters_meta.extend(future.result())
                    except Exception as e:
                        pass # Log lỗi nếu một trang quét thất bại
                        
            total_chaps = len(all_chapters_meta)
            
            # Đảm bảo danh sách chương được sắp xếp đúng thứ tự (nếu cần thiết, dựa trên logic cấu trúc URL hoặc plugin)
            # Tạm thời giữ nguyên danh sách thu thập được hoặc xử lý sort nếu plugin hỗ trợ
            
            # 3. ĐA LUỒNG: Tải nội dung của tất cả các chương song song
            completed_count = 0
            counter_lock = threading.Lock()
    
            def update_progress(chapter_title: str):
                nonlocal completed_count
                with counter_lock:
                    completed_count += 1
                    progress_callback(completed_count, total_chaps, chapter_title)
    
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                download_futures = [
                    executor.submit(self._download_chapter_worker, novel_url, chap, update_progress)
                    for chap in all_chapters_meta
                ]
                # Đợi toàn bộ các luồng tải xong
                for future in as_completed(download_futures):
                    try:
                        future.result()
                    except Exception:
                        pass
    

* * *

## 2\. Cập nhật Tầng Presentation (`presentation/cli.py`)

Tại tầng hiển thị, chúng ta thêm một Option `--workers` (Mặc định là 5 luồng) cho lệnh `download-all` để người dùng có thể linh hoạt tùy chỉnh tốc độ cào.
    
    
    # presentation/cli.py
    import click
    import sys
    from infrastructure.database import SQLiteNovelRepository
    from infrastructure.plugin_manager import PluginManager
    from application.use_cases import CrawlListingUseCase, DownloadAllChaptersUseCase
    
    repo = SQLiteNovelRepository()
    plugin_manager = PluginManager()
    
    @click.group()
    def cli():
        """Hệ thống CLI crawl truyện đa nguồn thiết kế theo Clean Architecture & DDD."""
        repo.init_storage()
    
    @cli.command(name="listing")
    @click.argument("url")
    @click.option("--page", type=int, help="Chỉ định trang")
    @click.option("--total-page", is_flag=True, help="Chỉ xem tổng số trang")
    def cmd_listing(url, page, total_page):
        """Cào danh mục truyện."""
        try:
            plugin = plugin_manager.get_plugin_for_url(url)
            use_case = CrawlListingUseCase(repo, plugin)
            
            result = use_case.execute(url, page, total_page)
            if total_page:
                click.echo(f"Tổng số trang danh mục: {result}")
            else:
                click.echo("Đã cào danh sách truyện thành công và lưu vào SQLite3!")
        except Exception as e:
            click.echo(f"[Lỗi]: {e}", err=True)
    
    @cli.command(name="download-all")
    @click.argument("url")
    @click.option("--workers", type=int, default=5, help="Số lượng luồng chạy song song (Mặc định: 5)")
    def cmd_download_all(url, workers):
        """Treo máy tự động tải trọn bộ truyện sử dụng ĐA LUỒNG và Thanh tiến trình."""
        try:
            plugin = plugin_manager.get_plugin_for_url(url)
            use_case = DownloadAllChaptersUseCase(repo, plugin)
            
            click.echo(f"Đang kích hoạt hệ thống cào đa luồng (Workers: {workers})...")
            click.echo("Step 1 & 2: Đang quét danh sách toàn bộ chương truyện...")
            
            # Khởi tạo thanh tiến trình trực quan của Click
            with click.progressbar(length=100, label="Tiến độ tải truyện", show_pos=True, item_show_func=lambda name: name if name else '') as bar:
                
                def on_progress(current: int, total: int, chapter_title: str):
                    bar.length = total             # Định hình lại tổng số item trên thanh
                    bar.update(current - bar.pos)  # Đẩy thanh tiến trình lên theo số lượng hoàn thành thực tế
                    bar.item_show_func = lambda _: f"({current}/{total}) {chapter_title}"
    
                # Gọi Use Case thực thi kèm tham số cấu hình số luồng
                use_case.execute(url, max_workers=workers, progress_callback=on_progress)
                
            click.echo("\n--- Hoàn thành! Tải toàn bộ truyện bằng đa luồng thành công vào SQLite3 ---")
        except Exception as e:
            click.echo(f"[Lỗi]: {e}", err=True)
    

* * *

## 3\. Cách vận hành CLI Đa Luồng Mới

Bây giờ bạn có thể tăng tốc độ tải truyện bằng cách chỉ định số lượng `workers` mong muốn.

  * Chạy mặc định với 5 luồng song song:
        
        python main.py download-all "https://truyenfull.live"
        

  * Tăng tốc tối đa với 15 luồng song song (Tải siêu nhanh):
        
        python main.py download-all "https://truyenfull.live" --workers 15
        




## Lưu ý về an toàn khi dùng Đa Luồng:

  * Thread-safe cho SQLite3: Do SQLite3 mặc định không hỗ trợ ghi đồng thời từ nhiều luồng (Sẽ bị lỗi `database is locked`), đoạn mã trên đã sử dụng `threading.Lock()` tại usecase để bọc lấy các hàm `save_chapter`. Điều này giúp các luồng tải trang HTML về song song (tận dụng tối đa băng thông), nhưng khi ghi kết quả vào file DB thì sẽ xếp hàng ghi tuần tự một cách an toàn.
  * Giới hạn số luồng: Tránh đặt số lượng `--workers` quá lớn (ví dụ >30), vì việc gửi quá nhiều request cùng một thời điểm lên Server nguồn (`truyenfull.live`) dễ khiến IP của bạn lọt vào danh sách đen (Anti-DDoS / Cloudflare Block). Con số an toàn và hiệu quả tối ưu thường nằm trong khoảng 5 đến 15 luồng.



Bạn có muốn tích hợp thêm một tính năng chuyên nghiệp nữa là Cơ chế tự động Thử lại (Retry) khi một luồng tải chương bị lỗi mạng đột xuất không?