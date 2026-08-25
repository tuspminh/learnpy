Dưới đây là mã nguồn file `main.py` hoàn chỉnh, đóng vai trò là Entry Point kết nối tất cả các thành phần kiến trúc đã xây dựng từ đầu đến giờ: Domain Model, Tinh gọn Unit of Work, Lớp chống ô nhiễm dữ liệu (ACL), Đa luồng (Multi-threading), và Luồng Đọc (CQRS) độc lập.

Bạn chỉ cần tạo một thư mục, bỏ các file vào đúng vị trí và chạy duy nhất file `main.py` này để kiểm tra toàn bộ hệ thống hoạt động thực tế.

* * *

## Toàn bộ mã nguồn file `main.py`
    
    
    import os
    import time
    from concurrent.futures import ThreadPoolExecutor
    
    # --- 1. TẦNG DOMAIN (Mô hình nghiệp vụ cốt lõi) ---
    from domain.model import Comic, ComicId, ChapterId
    from domain.services import ContentSanitizer
    
    # --- 2. TẦNG HẠ TẦNG (SQLite Thuần SQL, UoW tinh gọn) ---
    from infrastructure.database import init_db
    from infrastructure.sqlite_uow import SQLiteUnitOfWork
    from infrastructure.context import SQLiteReadContext
    
    # --- 3. TẦNG ỨNG DỤNG (Điều phối & Truy vấn CQRS) ---
    from application.crawler_service import ResilientCrawlerApplicationService
    from application.comic_queries import SQLiteComicQueryService
    
    DB_PATH = "comics.db"
    
    def setup_environment():
        """Khởi tạo môi trường, xóa DB cũ để chạy thử nghiệm sạch nếu muốn"""
        if os.path.exists(DB_PATH):
            try:
                os.remove(DB_PATH)
                os.remove(f"{DB_PATH}-wal")
                os.remove(f"{DB_PATH}-shm")
            except:
                pass
        
        print("🛠️  1. Khởi tạo cấu trúc các bảng SQLite...")
        init_db(DB_PATH)
        print("✅ Cấu hình DB hoàn tất.")
    
    
    def simulate_web_source_payload(chapter_num: int) -> dict:
        """Giả lập dữ liệu thô 'rất bẩn' cào về từ Internet"""
        # Cố tình chèn mã độc, quảng cáo, link bẩn của website nguồn lậu
        dirty_html = f"""
        <p>Chương {chapter_num}: Khởi Đầu Mới</p>
        <script>evil_spyware_script();</script>
        <div class="ads">Đọc truyện miễn phí tại website truyenfull.vn nha các bạn!</div>
        <p>Luồng sức mạnh cuồn cuộn chảy trong huyết quản của Lâm Phong...</p>
        <a href="https://web-quang-cao-doc-hai.com">Nhấp vào đây nhận 100k</a>
        <p>--- Hết chương {chapter_num} tại tangthuvien.vn ---</p>
        """
        return {
            "raw_title": f"   CHƯƠNG   {chapter_num}: KHỞI ĐẦU   ",
            "raw_content": dirty_html
        }
    
    
    def main():
        # Bước 1: Khởi tạo dữ liệu cấu trúc bảng
        setup_environment()
    
        # Bước 2: Cấu hình các thành phần hệ thống theo đúng SOLID / DI
        sanitizer = ContentSanitizer()
        uow = SQLiteUnitOfWork(DB_PATH)
        crawler_service = ResilientCrawlerApplicationService(uow, sanitizer)
    
        comic_slug = "linh-vuc"
        comic_id = ComicId(comic_slug)
        job_id = "job-crawl-batch-01"
    
        # =========================================================================
        # NHÁNH 1: THỰC THI LUỒNG GHI (COMMAND) - CRAWL ĐA LUỒNG
        # =========================================================================
        print("\n🚀 2. Bắt đầu tiến trình Crawl truyện đa luồng (Command)...")
        start_time = time.time()
    
        # Tạo trước danh sách tác vụ cào từ chương 1 đến chương 20
        chapters_to_crawl = list(range(1, 21))
    
        # Hàm bọc để ThreadPoolExecutor gọi song song
        def worker(num: int):
            # Lấy dữ liệu thô giả lập
            web_data = simulate_web_source_payload(num)
            
            # Đẩy qua Service xử lý: Tự động chạy ACL -> Qua Domain -> Qua UoW ghi xuống SQLite
            crawler_service.crawl_and_process_chapter(
                comic_id=comic_id,
                job_id=job_id,
                chapter_num=num,
                raw_title=web_data["raw_title"],
                raw_content=web_data["raw_content"]
            )
    
        # Chạy 5 luồng ghi song song
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(worker, chapters_to_crawl)
    
        print(f"⏱️  Tiến trình crawl 20 chương hoàn tất trong: {time.time() - start_time:.4f} giây")
    
        # =========================================================================
        # NHÁNH 2: THỰC THI LUỒNG ĐỌC (QUERY) - CQRS TỐC ĐỘ CAO SONG SONG
        # =========================================================================
        print("\n📖 3. Vận hành luồng Đọc dữ liệu độc lập (Query Service)...")
        
        # Dùng Context đọc riêng biệt hoàn toàn, không dính dáng đến UoW
        read_context = SQLiteReadContext(DB_PATH)
        query_service = SQLiteComicQueryService(read_context)
    
        # Đọc chi tiết truyện gộp tổng số chương (Sử dụng lệnh COUNT thuần SQL tối ưu)
        comic_detail = query_service.get_comic_detail(comic_slug)
        if comic_detail:
            print(f"🔹 [UI] Tên Truyện: {comic_detail.title}")
            print(f"🔹 [UI] Tổng số chương hiện có trong hệ thống: {comic_detail.total_chapters}")
    
        # Đọc nhanh danh sách mục lục (Chỉ lấy cột tiêu đề, bỏ qua cột nội dung nặng)
        print("\n📌 [UI] Hiển thị nhanh mục lục 3 chương đầu tiên trên giao diện:")
        chapter_list = query_service.get_chapters_v2(comic_slug)
        for ch in chapter_list[:3]:
            print(f"  -> [{ch.number}] {ch.title}")
    
        # =========================================================================
        # KIỂM CHỨNG TÍNH TOÀN VẸN DỮ LIỆU SAU KHI QUA ACL (ANTI-CORRUPTION LAYER)
        # =========================================================================
        print("\n🔎 4. Kiểm tra ngẫu nhiên dữ liệu lưu trong SQLite để xác thực bộ lọc rác (ACL)...")
        # Lấy thông tin thô từ UoW (Sử dụng Repo để kiểm tra dữ liệu lõi)
        with uow:
            sample_chapter = uow.chapter_repo.get_by_id(ChapterId(f"{comic_slug}-chuong-1"))
            
            if sample_chapter:
                print(f"▪️ Tiêu đề chuẩn hóa: '{sample_chapter.title}'")
                print("▪️ Nội dung truyện đã lọc sạch mã độc và quảng cáo lậu:")
                print("-" * 60)
                print(sample_chapter.content)
                print("-" * 60)
    
    if __name__ == "__main__":
        main()
    

* * *

## 💡 Hướng dẫn cấu trúc thư mục để chạy ngay lập tức

Để chạy được đoạn code trên, bạn hãy tổ chức cây thư mục project của mình thành các file như sau:
    
    
    comic_crawler/
    │
    ├── domain/
    │   ├── __init__.py
    │   ├── base.py               # Chứa AggregateRoot, DomainEvent (ở mục số 5)
    │   ├── model.py              # Chứa Comic, Chapter Entities (ở mục số 11)
    │   ├── services.py           # Chứa ContentSanitizer (ở mục số 9)
    │   ├── repository.py         # Chứa Interface ComicRepo, ChapterRepo (ở mục số 10,11)
    │   ├── job_repository.py     # Chứa Interface CrawlJobRepository (ở mục số 8)
    │   └── unit_of_work.py       # Chứa AbstractUnitOfWork (ở mục số 10)
    │
    ├── infrastructure/
    │   ├── __init__.py
    │   ├── database.py           # Hàm khởi tạo init_db tạo 3 bảng (comics, chapters, jobs)
    │   ├── context.py            # Chứa SQLiteReadContext luồng đọc (ở mục số 10)
    │   ├── sqlite_uow.py         # Chứa SQLiteUnitOfWork luồng ghi (ở mục số 10)
    │   ├── sqlite_repository.py  # Chứa SQLiteComicRepository & SQLiteChapterRepository
    │   └── sqlite_job_repository.py # Chứa SQLiteCrawlJobRepository
    │
    ├── application/
    │   ├── __init__.py
    │   ├── dtos.py               # Chứa các Data Transfer Object luồng đọc (ở mục số 8)
    │   ├── crawler_service.py    # Chứa ResilientCrawlerApplicationService (Luồng ghi)
    │   └── comic_queries.py      # Chứa SQLiteComicQueryService (Luồng đọc)
    │
    └── main.py                   # File Entry Point ở trên
    

Khi chạy `python main.py`, bạn sẽ chứng kiến toàn bộ sức mạnh của kiến trúc:

  1. Hệ thống chạy cào 20 chương song song cực nhanh mà SQLite không hề bị lỗi `database is locked` nhờ cơ chế `WAL` mode cấu hình chuẩn trong UoW.
  2. Dữ liệu khi lọt vào DB đã sạch bóng quảng cáo và mã script nhờ lớp ACL can thiệp trước khi lưu.
  3. Luồng CQRS đọc dữ liệu lên UI lập tức một cách độc lập không đi qua Domain Model giúp giảm tải RAM.



Nếu bạn gặp khó khăn hay lỗi cú pháp ở bất kỳ file hạ tầng nào trong cấu trúc trên khi ráp code lại, hãy nói cho tôi biết để tôi hỗ trợ bạn sửa lỗi ngay lập tức!