Để quản lý log cho dự án lớn gồm nhiều file và nhiều module, cách tốt nhất là sử dụng cấu hình tập trung (qua file hoặc qua cấu hình `dict`) và tận dụng cơ chế phân cấp (Hierarchy) của Python Logger.

Dưới đây là giải pháp tối ưu giúp bạn vừa ghi log ra màn hình console để theo dõi nhanh, vừa ghi log ra file để lưu trữ lâu dài.

## 1\. Cấu trúc thư mục dự án mẫu
    
    
    my_project/
    │
    ├── main.py              # File chạy chính (Khởi tạo logger)
    ├── config_log.py        # File cấu hình logging tập trung
    ├── modules/
    │   ├── __init__.py
    │   ├── module_a.py      # Module xử lý chức năng A
    │   └── module_b.py      # Module xử lý chức năng B
    └── app.log              # File log tự động sinh ra
    

## 2\. Mã nguồn triển khai chi tiết

## Bước 1: Tạo file cấu hình `config_log.py`

Sử dụng `dictConfig` là cách chuẩn hóa tốt nhất cho dự án lớn, giúp tách biệt logic mã nguồn và cấu hình log.
    
    
    import logging
    import logging.config
    
    def setup_logging():
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                # Định dạng cho Console: Ngắn gọn, dễ nhìn
                "console_format": {
                    "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                    "datefmt": "%H:%M:%S"
                },
                # Định dạng cho File: Chi tiết để phục vụ debug sau này
                "file_format": {
                    "format": "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(name)s - %(message)s"
                }
            },
            "handlers": {
                # Handler 1: Ghi ra màn hình (Console)
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",             # Chỉ hiện các log từ INFO trở lên trên màn hình
                    "formatter": "console_format",
                    "stream": "ext://sys.stdout"
                },
                # Handler 2: Ghi vào file
                "file": {
                    "class": "logging.FileHandler",
                    "level": "DEBUG",            # Lưu toàn bộ log chi tiết (bao gồm cả DEBUG) vào file
                    "formatter": "file_format",
                    "filename": "app.log",       # Tên file log
                    "encoding": "utf-8"
                }
            },
            "loggers": {
                # Root Logger: Cấu hình mặc định cho toàn bộ hệ thống
                "": {
                    "handlers": ["console", "file"],
                    "level": "DEBUG",            # Mức log thấp nhất được tiếp nhận
                }
            }
        }
        logging.config.dictConfig(log_config)
    

## Bước 2: Khởi tạo tại file chạy chính `main.py`

Bạn chỉ cần gọi hàm thiết lập log một lần duy nhất tại file khởi chạy ứng dụng.
    
    
    import logging
    from config_log import setup_logging
    import modules.module_a as module_a
    import modules.module_b as module_b
    
    # 1. Gọi cấu hình log ngay khi chạy ứng dụng
    setup_logging()
    
    # 2. Tạo logger cho file main
    logger = logging.getLogger(__name__)
    
    def main():
        logger.info("--- ỨNG DỤNG BẮT ĐẦU CHẠY ---")
        
        # Gọi các hàm từ các module khác
        module_a.do_something()
        module_b.do_other_thing()
        
        logger.info("--- ỨNG DỤNG KẾT THÚC ---")
    
    if __name__ == "__main__":
        main()
    

## Bước 3: Sử dụng tại các module con (`modules/module_a.py`)

Tại các file vệ tinh, bạn không cần cấu hình lại. Chỉ cần gọi đúng một dòng `logging.getLogger(__name__)`.
    
    
    import logging
    
    # __name__ sẽ tự động lấy tên module dạng: "modules.module_a"
    logger = logging.getLogger(__name__)
    
    def do_something():
        logger.debug("Đây là log DEBUG từ Module A - chỉ xuất hiện trong file log.")
        logger.info("Đây là log INFO từ Module A - xuất hiện cả ở màn hình và file.")
        try:
            1 / 0
        except ZeroDivisionError:
            logger.error("Đã xảy ra lỗi chia cho 0 tại Module A!", exc_info=True) 
            # exc_info=True giúp ghi lại toàn bộ Traceback lỗi vào file log
    

## 3\. Điểm cộng lớn của cách làm này

  * Tự động phân cấp: Biến `__name__` giúp log tự động gắn thẻ tên module (Ví dụ: `modules.module_a`). Bạn sẽ biết chính xác dòng log đó sinh ra từ file nào.
  * Bộ lọc thông minh: Màn hình Console chỉ hiện các thông tin quan trọng (`INFO` trở lên) tránh bị rối mắt khi dev. Trong khi đó, file `app.log` sẽ lưu tất cả vết tích (`DEBUG` trở lên) để điều tra khi có sự cố.
  * Ghi vết lỗi (Traceback): Khi dùng `logger.error(..., exc_info=True)`, toàn bộ chi tiết lỗi của Python sẽ được in ra file log, cực kỳ hữu ích cho dự án lớn.



Nếu bạn muốn nâng cấp hệ thống log này, bạn có muốn tìm hiểu thêm về:

  * RotatingFileHandler: Tự động chia nhỏ file log theo ngày hoặc theo dung lượng (ví dụ file đầy 10MB sẽ tự tạo file mới) để tránh đầy ổ cứng?
  * ColorFormatter: Cách làm cho log trên màn hình console có màu sắc (đỏ cho error, vàng cho warning) để dễ quan sát?