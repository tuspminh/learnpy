Nếu cấu trúc dự án của bạn là kiến trúc phẳng (flat directory)—nghĩa là tất cả các file/thư mục như `domain/`, `infrastructure/`, `main.py` nằm ngay ở thư mục gốc của dự án chứ không được bọc bên trong thư mục `src/`—thì tại `main.py` bạn chỉ cần truyền chuỗi rỗng `""` hoặc không truyền gì cả (để mặc định) vào hàm `setup_logger()`.

Khi bạn truyền một chuỗi rỗng `""`, Python sẽ cấu hình cho Root Logger (Logger gốc của toàn bộ hệ thống). Theo cơ chế lan truyền log (Propagate) của Python, tất cả các logger được khởi tạo bằng `logging.getLogger(__name__)` ở bất kỳ thư mục con nào (`domain`, `infrastructure`) đều sẽ tự động thừa hưởng cấu hình ghi file và console từ Root Logger này.

Dưới đây là cách điều chỉnh mã nguồn cho cấu trúc dự án flat:

## 🔧 1. Cập Nhật Hàm Khởi Tạo Logger (`infrastructure/logging/logger.py`)

Cập nhật lại một chút để nếu truyền chuỗi rỗng hoặc không truyền tên, nó sẽ lấy Root Logger của Python làm đích cấu hình.
    
    
    # infrastructure/logging/logger.py
    import logging
    import os
    import sys
    from logging.handlers import RotatingFileHandler
    from config.settings import settings
    
    def setup_logger(name: str = "") -> logging.Logger:
        """
        Cấu hình bộ Logger tập trung cho toàn bộ ứng dụng flat.
        Nếu không truyền name hoặc truyền "", hàm sẽ cấu hình thẳng cho Root Logger.
        """
        # Lấy logger dựa trên tên hoặc lấy Root Logger nếu name là ""
        logger = logging.getLogger(name) if name else logging.getLogger()
        
        if logger.handlers:
            return logger
    
        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
        log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(log_level)
    
        # Handler 1: Console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
        # Handler 2: Rotating File
        try:
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            log_file_path = os.path.join(log_dir, "crawler.log")
            
            file_handler = RotatingFileHandler(
                filename=log_file_path,
                maxBytes=5 * 1024 * 1024, 
                backupCount=3,
                encoding="utf-8"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.warning(f"⚠️ Không thể khởi tạo File Logger: {e}")
    
        return logger
    

* * *

## 🎮 2. Điểm Khởi Chạy Mới (`main.py`)

Tại file chạy chính nằm ở thư mục gốc, bạn chỉ cần gọi `setup_logger()` mà không cần truyền tham số:
    
    
    # main.py (File nằm ngay thư mục gốc của dự án phẳng)
    from config.settings import settings
    from infrastructure.logging.logger import setup_logger
    
    from infrastructure.http_client import RequestsHttpClient
    from infrastructure.parsers.factory import ParserFactory
    from infrastructure.repositories.sqlite_uow import SqliteUnitOfWork
    from infrastructure.image_downloader import LocalImageDownloader
    from domain.services import NovelCrawlerService
    
    def main():
        # Khởi tạo logger hệ thống cho Root Logger (Mọi module khác sẽ tự bắt được cấu hình)
        setup_logger() 
        
        shared_client = RequestsHttpClient()
        
        app = NovelCrawlerService(
            http_client=shared_client,
            parser_factory=ParserFactory(),
            uow=SqliteUnitOfWork(db_path=settings.SQLITE_DB_PATH),
            image_downloader=LocalImageDownloader(http_client=shared_client)
        )
        
        app.crawl_novel_workflow("https://truyenfull.vn")
    
    if __name__ == "__main__":
        main()
    

## 💡 Lưu ý về `import` trong cấu trúc Flat:

Khi chuyển sang cấu trúc phẳng, hãy nhớ xóa toàn bộ tiền tố `src.` trong tất cả các câu lệnh `import` của dự án (Ví dụ: từ `from src.domain.models import ...` sửa thành `from domain.models import ...`).

Bạn đã hoàn tất việc dọn dẹp sự phụ thuộc của Domain Core sang lớp Hạ tầng rồi. Bạn có muốn chúng ta hoàn thiện nốt phần Factory Pattern để tự động nhận diện và bóc tách dữ liệu theo trang cho cấu trúc Flat này không?