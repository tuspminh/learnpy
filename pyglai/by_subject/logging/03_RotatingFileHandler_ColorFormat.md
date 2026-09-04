Dưới đây là mã cấu hình hoàn chỉnh tích hợp cả `RotatingFileHandler` (tự động chia nhỏ file khi đạt dung lượng lớn) và màu sắc trực quan trên màn hình console (Đỏ cho ERROR, Vàng cho WARNING, Xanh cho INFO).

Để có màu sắc trên Console một cách chuyên nghiệp và đa nền tảng (chạy được cả trên Windows/Linux), chúng ta sẽ cài đặt thêm thư viện `colorlog`.

## Bước 1: Cài đặt thư viện màu sắc

Bạn mở terminal và chạy lệnh sau:
    
    
    pip install colorlog
    

## Bước 2: Cập nhật lại file `config_log.py`

Thay thế toàn bộ nội dung file `config_log.py` bằng đoạn mã tối ưu dưới đây:
    
    
    import os
    import logging
    import logging.config
    
    def setup_logging():
        # Tạo thư mục chứa log nếu chưa tồn tại
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
        log_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                # 1. Định dạng CÓ MÀU SẮC cho Console
                "color_console_format": {
                    "()": "colorlog.ColoredFormatter",  # Sử dụng class của colorlog
                    "format": "%(log_color)s%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
                    "datefmt": "%H:%M:%S",
                    "log_colors": {
                        "DEBUG": "cyan",
                        "INFO": "green",
                        "WARNING": "yellow",
                        "ERROR": "red",
                        "CRITICAL": "bold_red",
                    }
                },
                # 2. Định dạng chuẩn cho File (không chứa mã màu để file text không bị lỗi hiển thị)
                "file_format": {
                    "format": "%(asctime)s - %(levelname)-8s - [%(filename)s:%(lineno)d] - %(name)s - %(message)s"
                }
            },
            "handlers": {
                # Handler Console: Có màu, mức INFO trở lên
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "color_console_format",
                    "stream": "ext://sys.stdout"
                },
                # Handler File: Tự động xoay/chia nhỏ file, mức DEBUG trở lên
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file_format",
                    "filename": os.path.join(log_dir, "app.log"),
                    "maxBytes": 10 * 1024 * 1024,  # 10 MB thì tự động đổi file
                    "backupCount": 5,             # Giữ tối đa 5 file log cũ (app.log.1, app.log.2,...)
                    "encoding": "utf-8"
                }
            },
            "loggers": {
                "": {  # Root logger áp dụng cho toàn dự án
                    "handlers": ["console", "rotating_file"],
                    "level": "DEBUG",
                }
            }
        }
        logging.config.dictConfig(log_config)
    

## Cách thức hoạt động của hệ thống mới:

  1. Quản lý dung lượng ổ cứng (`RotatingFileHandler`):

     * File log hiện tại luôn là `logs/app.log`.
     * Khi dung lượng `app.log` đạt đến 10MB, Python sẽ tự động đổi tên nó thành `app.log.1` và tạo một file `app.log` trống mới để ghi tiếp.
     * Quá trình này lặp lại và giữ tối đa 5 file cũ hệ thống (`app.log.1` đến `app.log.5`). File thứ 6 xuất hiện thì file cũ nhất sẽ bị xóa, đảm bảo ổ cứng của bạn không bao giờ bị đầy.

  2. Theo dõi trực quan (Color): Khi bạn chạy `main.py`, màn hình terminal sẽ sáng lên các màu Xanh/Vàng/Đỏ tương ứng với độ nghiêm trọng, giúp bạn phát hiện lỗi (ERROR) ngay lập tức mà không cần căng mắt đọc từng dòng chữ trắng đen.



Bạn có muốn tích hợp thêm tính năng gửi email thông báo tự động (qua `SMTPHandler`) mỗi khi hệ thống gặp lỗi mức `CRITICAL` hoặc `ERROR` không?