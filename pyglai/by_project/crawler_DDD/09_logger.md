Dưới đây là mã nguồn chi tiết cho lớp Logger tập trung (`src/infrastructure/logging/logger.py`) được thiết kế theo tiêu chuẩn cấu trúc của dự án, tuân thủ nguyên lý Single Responsibility (S).

Hệ thống này hỗ trợ ghi log song song ra cả Màn hình (Console) trực quan và File cục bộ (Rotate File) tự động cắt file theo dung lượng để tránh làm đầy ổ cứng.

## 💻 Triển khai mã nguồn Logger (`src/infrastructure/logging/logger.py`)
    
    
    # src/infrastructure/logging/logger.py
    import logging
    import os
    import sys
    from logging.handlers import RotatingFileHandler
    from src.config.settings import settings
    
    def setup_logger(name: str) -> logging.Logger:
        """
        Cấu hình bộ Logger tập trung cho toàn bộ ứng dụng (SOLID - S).
        Hỗ trợ xuất log ra Console và tự động xoay vòng File (Rotating File).
        """
        logger = logging.getLogger(name)
        
        # Tránh việc add trùng Handler nếu hàm này được gọi nhiều lần trên cùng một class
        if logger.handlers:
            return logger
    
        # 1. Định dạng chuẩn cho log (Timestamp | Cấp độ | Tên Module | Tin nhắn)
        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
        # 2. Cấu hình cấp độ Log dựa trên file .env (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(log_level)
    
        # 3. Handler 1: Ghi log ra Màn hình (Console)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
        # 4. Handler 2: Ghi log ra Tệp tin cục bộ (Tự động cắt/xoay vòng file)
        try:
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            log_file_path = os.path.join(log_dir, "crawler.log")
            
            # Cắt file khi đạt 5MB (maxBytes), lưu tối đa 3 file cũ (backupCount) để bảo vệ ổ đĩa
            file_handler = RotatingFileHandler(
                filename=log_file_path,
                maxBytes=5 * 1024 * 1024, 
                backupCount=3,
                encoding="utf-8"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            # Nếu không có quyền ghi file hệ thống, thông báo ra console nhưng không làm crash app
            logger.warning(f"⚠️ Không thể khởi tạo File Logger (Có thể do quyền truy cập thư mục): {e}")
    
        return logger
    

* * *

## ⚙️ Cập nhật File Cấu Hình (`src/config/settings.py`)

Đảm bảo file cấu hình của bạn có sẵn biến `LOG_LEVEL` để điều chỉnh nhanh môi trường làm việc (khi code thì dùng `DEBUG`, khi chạy thực tế trên server thì dùng `INFO` hoặc `WARNING` để tiết kiệm dung lượng).
    
    
    # src/config/settings.py (Bổ sung nếu chưa có)
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    class Settings:
        DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")
        SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "novel_database.db")
        # Cấu hình log nhận: "DEBUG", "INFO", "WARNING", "ERROR"
        LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO") 
    
    settings = Settings()
    

* * *

## 🎮 Cách sử dụng trong các Module khác

Bạn chỉ cần gọi hàm `setup_logger` và truyền vào tên của Module hiện tại (thường dùng `__name__` để biết chính xác lỗi phát ra từ file nào).
    
    
    # Ví dụ sử dụng tại src/infrastructure/parsers/truyenfull.py
    from src.infrastructure.logging.logger import setup_logger
    
    # Khởi tạo logger riêng cho file này
    logger = setup_logger(__name__)
    
    class TruyenFullParser:
        def parse_listing_page(self, source):
            logger.debug(f"Đang phân tích HTML của URL: {source.url}")
            try:
                # Logic bóc tách...
                pass
            except Exception as e:
                # Ghi nhận lỗi chi tiết
                logger.error(f"❌ Lỗi cấu trúc HTML tại trang Listing: {str(e)}")
                raise e
    

## 🎯 Điểm cộng của thiết kế Logger này:

  * Bảo vệ phần cứng: Việc sử dụng `RotatingFileHandler` giúp file log không bao giờ bị phình lên vô hạn (gây tràn ổ cứng server sau vài tháng cào truyện). File log sẽ tự động được chia nhỏ thành `crawler.log`, `crawler.log.1`, `crawler.log.2` khi vượt quá 5MB.
  * Độc lập luồng lỗi: Không chặn (block) tiến trình chính của Crawler nếu hệ thống lưu trữ file log gặp sự cố về quyền hạn (Permission Denied).



Bạn có muốn tích hợp thêm Cơ chế lưu log lỗi đặc biệt (Chỉ lưu log cấp độ ERROR vào một file riêng) để tiện theo dõi các trang truyện bị lỗi cấu trúc HTML không?