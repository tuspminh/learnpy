Để thêm tính năng lưu truyện ra file cục bộ (như JSON, TXT hoặc Markdown) bằng thần SQL/Python đồng bộ, chúng ta chỉ cần tạo thêm một lớp triển khai mới cho `NovelRepositoryInterface`.

Nhờ thiết kế tuân thủ nghiêm ngặt Open/Closed Principle (O) trong SOLID, bạn sẽ thấy chúng ta không cần sửa đổi bất kỳ dòng code nào trong lớp nghiệp vụ (Domain) mà chỉ cần bổ sung class mới ở lớp hạ tầng (Infrastructure) và cấu hình lại file chạy.

Dưới đây là mã nguồn chi tiết tích hợp thêm `FileLocalRepository`:

* * *

## 🧱 Kiến Trúc Thư Mục Cập Nhật
    
    
    src/
    │
    ├── config/
    │   └── settings.py          # Thêm cấu hình FILE_OUTPUT_DIR
    │
    ├── domain/
    │   ├── models.py            
    │   └── services.py          # Giữ nguyên UnitOfWork và Service đồng bộ
    │
    ├── infrastructure/
    │   ├── http_client.py
    │   ├── parsers.py
    │   └── repositories/        
    │       ├── sqlite_uow.py    
    │       ├── sqlite_repo.py   
    │       ├── mongo_repo.py    
    │       └── file_repo.py     # <-- THÊM MỚI: Lưu dữ liệu ra file local (JSON)
    │
    └── main.py                  # Lắp ghép hệ thống qua cấu hình mới
    

* * *

## 💻 Triển Khai Mã Nguồn Chi Tiết

## 1\. Cập Nhật Cấu Hình (`src/config/settings.py`)

Bổ sung thêm cấu hình thư mục đầu ra nếu người dùng chọn lưu file.
    
    
    # src/config/settings.py
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    class Settings:
        # Có thể chọn: "sqlite", "mongo", hoặc "file"
        DB_TYPE: str = os.getenv("DB_TYPE", "file") 
        SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "novel_database.db")
        MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "crawler_sync_db")
        
        # Đường dẫn thư mục lưu file truyện cục bộ
        FILE_OUTPUT_DIR: str = os.getenv("FILE_OUTPUT_DIR", "extracted_novels")
        LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    settings = Settings()
    

## 2\. Thêm Mới: File Cục Bộ Repository (`src/infrastructure/repositories/file_repo.py`)

Lớp này sẽ tự động tạo một thư mục riêng cho từng truyện và lưu thông tin chi tiết dưới dạng một file `json`. Định dạng này giúp cấu trúc phân cấp (Truyện -> Chương) được giữ nguyên vẹn tương tự như MongoDB.
    
    
    # src/infrastructure/repositories/file_repo.py
    import os
    import json
    import re
    from src.domain.services import NovelRepositoryInterface
    from src.domain.models import Novel, Chapter
    
    class FileLocalRepository(NovelRepositoryInterface):
        """Triển khai Repository lưu trữ truyện thành file JSON cục bộ (SOLID - L)"""
        def __init__(self, output_dir: str):
            self._output_dir = output_dir
            # Tự động tạo thư mục gốc nếu chưa có
            if not os.path.exists(self._output_dir):
                os.makedirs(self._output_dir)
    
        def _slugify(self, text: str) -> str:
            """Chuyển đổi tên truyện thành tên file hợp lệ (Ví dụ: "Truyện Chữ" -> "truyen-chu")"""
            text = text.lower()
            text = re.sub(r'[áàảãạăắằẳẵặâấầẩẫậ]', 'a', text)
            text = re.sub(r'[éèẻẽẹêếềểễệ]', 'e', text)
            text = re.sub(r'[óòỏõọôốồổỗộơớờởỡợ]', 'o', text)
            text = re.sub(r'[íìỉĩị]', 'i', text)
            text = re.sub(r'[úùủũụưứừửữự]', 'u', text)
            text = re.sub(r'[ýỳỷỹỵ]', 'y', text)
            text = re.sub(r'đ', 'd', text)
            text = re.sub(r'[^a-z0-9\s-]', '', text)
            return re.sub(r'[\s-]+', '-', text).strip('-')
    
        def save(self, novel: Novel, context=None) -> None:
            file_name = f"{self._slugify(novel.title)}.json"
            file_path = os.path.join(self._output_dir, file_name)
    
            # Chuyển đổi dữ liệu Domain Model sang Dictionary
            novel_data = {
                "title": novel.title,
                "author": novel.author,
                "chapters": [
                    {"title": ch.title, "content": ch.content, "url": ch.url} 
                    for ch in novel.chapters
                ]
            }
    
            # Ghi dữ liệu ra file với định dạng UTF-8 để không bị lỗi font tiếng Việt
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(novel_data, f, ensure_ascii=False, indent=4)
    
        def get_by_url(self, url: str) -> Novel | None:
            """Quét qua các file json hiện có xem URL chương này đã được cào chưa"""
            if not os.path.exists(self._output_dir):
                return None
    
            for file_name in os.listdir(self._output_dir):
                if not file_name.endswith(".json"):
                    continue
                    
                file_path = os.path.join(self._output_dir, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        
                    # Kiểm tra xem có chương nào trùng URL cần tìm không
                    for ch_data in data.get("chapters", []):
                        if ch_data.get("url") == url:
                            # Khôi phục ngược lại thành Domain Model
                            chapters = [
                                Chapter(title=ch["title"], content=ch["content"], url=ch["url"]) 
                                for ch in data["chapters"]
                            ]
                            return Novel(title=data["title"], author=data["author"], chapters=chapters)
                except Exception:
                    continue # Bỏ qua nếu file bị hỏng hoặc lỗi định dạng
                    
            return None
    

## 3\. Thiết Kế Lớp Bọc "Fake" Unit of Work Cho File/Mongo

Vì `FileLocalRepository` và `MongoNovelRepository` thao tác trên một lệnh đơn là lưu toàn bộ thực thể (Atomic ghi đè file/ghi đè document), chúng không cần cơ chế `BEGIN TRANSACTION` phức tạp như SQLite.

Để giữ nguyên kiến trúc nạp `uow` vào `NovelCrawlerService`, ta tạo một lớp bọc đơn giản (No-Op Unit of Work):
    
    
    # src/infrastructure/repositories/dummy_uow.py
    from src.domain.services import UnitOfWorkInterface, NovelRepositoryInterface
    
    class DummyUnitOfWork(UnitOfWorkInterface):
        """Lớp bọc Unit of Work dành cho NoSQL hoặc File System không cần SQL Transaction"""
        def __init__(self, repository: NovelRepositoryInterface):
            self._repository = repository
    
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass
        def commit(self): pass
        def rollback(self): pass
    
        @property
        def novels(self) -> NovelRepositoryInterface:
            return self._repository
    

## 4\. Cấu Hình và Khởi Chạy Ứng Dụng Linh Hoạt (`src/main.py`)

Bây giờ, tại file chạy chính, bạn có thể dễ dàng chuyển đổi qua lại giữa 3 loại lưu trữ: Hệ quản trị quan hệ SQL thuần (`sqlite`), Tài liệu (`mongo`), hoặc tệp tin cục bộ (`file`).
    
    
    # src/main.py
    from src.config.settings import settings
    from src.infrastructure.logging.logger import setup_logger
    from src.infrastructure.http_client import RequestsHttpClient
    from src.infrastructure.parsers import TruyenFullParser
    
    # Import các công cụ quản lý dữ liệu hạ tầng
    from src.infrastructure.repositories.sqlite_uow import SqliteUnitOfWork
    from src.infrastructure.repositories.mongo_repo import MongoNovelRepository
    from src.infrastructure.repositories.file_repo import FileLocalRepository
    from src.infrastructure.repositories.dummy_uow import DummyUnitOfWork
    
    from src.domain.services import NovelCrawlerService
    
    logger = setup_logger("MainApp")
    
    def main():
        logger.info("--- Khởi động Ứng dụng Crawler Đồng bộ theo DDD & SOLID ---")
        
        # 1. Khởi tạo Fetcher Client và Parser chung
        http_client = RequestsHttpClient(timeout=10)
        parser = TruyenFullParser()
        
        # 2. Lựa chọn Unit of Work/Repository linh hoạt dựa trên file .env
        if settings.DB_TYPE == "sqlite":
            logger.info(f"💾 Chế độ lưu trữ: SQLite3 (SQL thuần). File: {settings.SQLITE_DB_PATH}")
            uow = SqliteUnitOfWork(db_path=settings.SQLITE_DB_PATH)
            
        elif settings.DB_TYPE == "mongo":
            logger.info("🍃 Chế độ lưu trữ: MongoDB.")
            mongo_repo = MongoNovelRepository(connection_string=settings.MONGO_URI, db_name=settings.MONGO_DB_NAME)
            uow = DummyUnitOfWork(repository=mongo_repo)
            
        elif settings.DB_TYPE == "file":
            logger.info(f"📁 Chế độ lưu trữ: Thư mục File Cục Bộ. Thư mục: {settings.FILE_OUTPUT_DIR}")
            file_repo = FileLocalRepository(output_dir=settings.FILE_OUTPUT_DIR)
            uow = DummyUnitOfWork(repository=file_repo)
            
        else:
            logger.critical("❌ Loại DB_TYPE được cấu hình không hợp lệ!")
            return
        
        # 3. Inject Unit of Work đã chọn vào Service điều phối chính
        crawler = NovelCrawlerService(http_client=http_client, parser=parser, uow=uow)
        
        # 4. Tiến hành cào truyện
        target_url = "https://example-truyen.com"
        try:
            novel = crawler.crawl_and_save(target_url)
            logger.info(f"🎉 Hoàn thành! Truyện '{novel.title}' đã được lưu an toàn.")
        except Exception as e:
            logger.critical(f"💥 Quy trình thất bại nhưng dữ liệu hệ thống được toàn vẹn. Chi tiết: {e}")
    
    if __name__ == "__main__":
        main()
    

* * *

## 🎯 Điểm Cộng Kiến Trúc Lần Này

  * Liskov Substitution (L) hoàn hảo: Lớp `FileLocalRepository` đảm nhận đầy đủ nghĩa vụ của `NovelRepositoryInterface`. Bạn có thể thay thế việc ghi ổ đĩa cứng bằng ghi Database mà không cần đụng vào logic phân tích dữ liệu.
  * Mở rộng tối đa (O): Sau này nếu bạn muốn lưu truyện thành file định dạng `.epub` hay `.pdf` để copy vào máy đọc sách, bạn chỉ việc tạo ra một `EpubLocalRepository` tương tự mà không cần viết lại mã nguồn lõi.



Nếu bạn muốn nâng cấp sâu hơn cho ứng dụng này, hãy cho tôi biết:

  * Bạn có cần xây dựng thêm Cơ chế Retry (Tự động tải lại) khi việc đọc ghi file hoặc kết nối database bị lỗi mạng/nghẽn ổ đĩa không?
  * Bạn có muốn bổ sung thêm Cơ chế nén file (Zip/Tar) sau khi xuất dữ liệu ra file local không?