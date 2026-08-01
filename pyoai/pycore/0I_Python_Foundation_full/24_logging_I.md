# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 24: Logging Chuyên nghiệp (Phần 1) - Làm chủ module `logging`

> **Đây là một trong những kỹ năng tạo ra sự khác biệt giữa lập trình viên mới và lập trình viên chuyên nghiệp.**

Trong các dự án thực tế như:

* Django
* FastAPI
* Flask
* Scrapy
* Celery
* PySide6
* Microservices
* AI Agent

**Không ai dùng `print()` để debug hoặc theo dõi hệ thống trong môi trường production.**

Thay vào đó, tất cả đều sử dụng **Logging**.

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu Logging là gì.
* Biết tại sao không nên dùng `print()`.
* Thành thạo module `logging`.
* Hiểu Logger, Handler, Formatter.
* Hiểu Log Level.
* Ghi log ra Console.
* Ghi log ra File.
* Tổ chức Logging theo chuẩn dự án thực tế.

---

# Phần I

# Logging là gì?

Logging là quá trình:

> **Ghi lại những sự kiện xảy ra trong chương trình.**

Ví dụ:

```text
09:10:01 INFO User login

09:10:02 INFO Load profile

09:10:03 WARNING Cache miss

09:10:05 ERROR Database timeout
```

Đây gọi là Log.

---

# Vì sao cần Logging?

Ví dụ:

Khách hàng báo:

```text
Ứng dụng bị lỗi lúc 3 giờ sáng.
```

Bạn không có mặt.

Không có log.

↓

Không biết:

* Người dùng làm gì.
* Gọi API nào.
* SQL nào chạy.
* File nào mở.
* Exception gì.

Không thể sửa lỗi.

---

# Logging giống "hộp đen" của máy bay

Máy bay rơi.

Điều tra bằng:

```text
Black Box
```

Phần mềm cũng vậy.

Log chính là Black Box.

---

# Phần II

# Vì sao không dùng print()

Ví dụ:

```python
print("Connect DB")

print("Login")

print("Payment")
```

Có rất nhiều vấn đề.

---

## Không có thời gian

```text
Login
```

Xảy ra lúc nào?

Không biết.

---

## Không có mức độ

Không biết:

```text
INFO

WARNING

ERROR
```

---

## Không lưu file

Terminal đóng.

↓

Mất hết.

---

## Không lọc được

Muốn xem:

```text
ERROR
```

↓

Không được.

---

## Không thể ghi nhiều nơi

Muốn:

* Console
* File
* Database
* ElasticSearch

↓

print không làm được.

---

# Phần III

# Module logging

Python có sẵn:

```python
import logging
```

Không cần cài thêm.

---

# Log đầu tiên

```python
import logging

logging.warning("Disk almost full")
```

Kết quả:

```text
WARNING:root:Disk almost full
```

---

# Log INFO

```python
logging.info("User login")
```

Bạn sẽ ngạc nhiên:

Không hiện gì.

Tại sao?

---

# Log Level mặc định

Mặc định Python là:

```text
WARNING
```

Nghĩa là chỉ hiện:

```text
WARNING

ERROR

CRITICAL
```

Không hiện:

```text
DEBUG

INFO
```

---

# Thiết lập mức log

```python
import logging

logging.basicConfig(level=logging.INFO)

logging.info("Login")
```

Kết quả:

```text
INFO:root:Login
```

---

# Phần IV

# Log Level

Python có 5 mức chuẩn.

---

## DEBUG

Chi tiết nhất.

Ví dụ:

```python
logging.debug("SQL = SELECT * FROM users")
```

Dùng khi:

Debug.

---

## INFO

Thông tin bình thường.

```python
logging.info("User login")
```

---

## WARNING

Có vấn đề.

Nhưng chương trình vẫn chạy.

Ví dụ:

```python
logging.warning("Cache miss")
```

---

## ERROR

Có lỗi.

Một chức năng thất bại.

```python
logging.error("Cannot connect database")
```

---

## CRITICAL

Lỗi nghiêm trọng.

Ví dụ:

```python
logging.critical("Database corrupted")
```

---

# So sánh

```text
DEBUG
   ↓
INFO
   ↓
WARNING
   ↓
ERROR
   ↓
CRITICAL
```

Nếu:

```python
level = logging.WARNING
```

↓

Hiện:

```text
WARNING

ERROR

CRITICAL
```

---

# Phần V

# basicConfig()

Đây là hàm cấu hình nhanh.

```python
logging.basicConfig(level=logging.DEBUG)
```

---

## Định dạng log

```python
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
```

Kết quả:

```text
INFO Login
```

---

## Thêm thời gian

```python
format = "%(asctime)s %(levelname)s %(message)s"
```

Kết quả:

```text
2026-08-01 09:10:02 INFO Login
```

---

## Thêm tên file

```python
"%(filename)s"
```

Ví dụ:

```text
main.py
```

---

## Thêm số dòng

```python
"%(lineno)d"
```

Ví dụ:

```text
main.py:42
```

---

## Thêm tên hàm

```python
"%(funcName)s"
```

---

# Ví dụ đầy đủ

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format=("%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"),
)

logging.info("Application started")
```

Kết quả:

```text
2026-08-01 10:01:02 |
INFO |
main.py:15 |
Application started
```

---

# Phần VI

# Logger

Không nên dùng:

```python
logging.info(...)
```

Trong dự án lớn.

Nên:

```python
logger = logging.getLogger(__name__)
```

Ví dụ:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Login")
```

---

# Tại sao?

Nếu:

```text
app/

    user.py

    payment.py

    api.py
```

Mỗi module:

```python
logger = logging.getLogger(__name__)
```

Log sẽ biết:

```text
app.user

app.payment

app.api
```

Rất dễ theo dõi.

---

# Phần VII

# Handler

Logger:

↓

Sinh Log.

Handler:

↓

Quyết định:

Log đi đâu.

Ví dụ:

```text
Logger

↓

ConsoleHandler

↓

Terminal
```

---

Hoặc:

```text
Logger

↓

FileHandler

↓

app.log
```

---

Hoặc:

```text
Logger

↓

SocketHandler

↓

Server
```

---

# Console Handler

```python
handler = logging.StreamHandler()
```

---

# File Handler

```python
handler = logging.FileHandler("app.log")
```

Log sẽ lưu vào:

```text
app.log
```

---

# Phần VIII

# Formatter

Formatter quyết định:

Log hiển thị thế nào.

Ví dụ:

```python
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
```

---

Gắn Formatter

```python
handler.setFormatter(formatter)
```

---

Gắn Handler

```python
logger.addHandler(handler)
```

---

Ví dụ hoàn chỉnh

```python
import logging

logger = logging.getLogger("app")

logger.setLevel(logging.INFO)

handler = logging.StreamHandler()

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

handler.setFormatter(formatter)

logger.addHandler(handler)

logger.info("Hello")
```

---

# Phần IX

# Ghi log ra File

```python
handler = logging.FileHandler("application.log")
```

Sau đó:

```python
logger.addHandler(handler)
```

Log sẽ ghi:

```text
application.log
```

---

# Ghi đồng thời Console + File

```text
Logger

↓

ConsoleHandler

↓

FileHandler
```

Một log.

↓

Hiện Terminal.

↓

Lưu File.

---

# Ví dụ

```python
logger.addHandler(console_handler)

logger.addHandler(file_handler)
```

---

# Phần X

# Logger theo module

Ví dụ dự án:

```text
project/

    api/

    service/

    repository/

    database/
```

Trong mỗi file:

```python
logger = logging.getLogger(__name__)
```

Ví dụ:

```text
service.user
```

↓

```text
INFO Login success
```

---

# Phần XI

# Những lỗi phổ biến

## Sai

```python
print("Error")
```

---

## Sai

```python
logging.basicConfig()

...

logging.basicConfig()
```

`basicConfig()` chỉ nên gọi **một lần**, thường ở điểm khởi động ứng dụng (`main.py`).

---

## Sai

```python
logger = logging.getLogger()

logger = logging.getLogger()
```

Tạo nhiều logger không cần thiết.

---

## Sai

```python
logger.error(f"Error = {e}")
```

Ở các phiên bản Python hiện đại, nếu chỉ ghi chuỗi đơn giản thì không sao, nhưng với logging nên ưu tiên truyền tham số:

```python
logger.error("Error = %s", e)
```

Logging sẽ trì hoãn việc định dạng chuỗi nếu log đó không được ghi, giúp hiệu quả hơn.

---

# Phần XII

# Thực hành

## Bài 1

Viết:

```python
logging.info()

logging.warning()

logging.error()
```

---

## Bài 2

Định dạng:

```text
TIME

LEVEL

MESSAGE
```

---

## Bài 3

Lưu log vào:

```text
app.log
```

---

## Bài 4

Hiện log:

Console

*

File

---

## Bài 5

Tạo:

```python
logger = logging.getLogger(__name__)
```

Trong:

```text
user.py

payment.py

database.py
```

Quan sát sự khác biệt của tên logger.

---

## Bài 6

Viết chương trình:

```text
Login

↓

Read Config

↓

Connect DB

↓

Load User

↓

Logout
```

Ghi log cho từng bước với mức độ phù hợp (`INFO`, `WARNING`, `ERROR`...).

---

# Mini Project

# Logging cho ứng dụng Web Scraper

Đây là ví dụ rất gần với dự án **ứng dụng cào truyện** mà bạn đã và đang học thiết kế.

Cấu trúc:

```text
scraper/

    main.py

    spider.py

    parser.py

    downloader.py

    database.py
```

Yêu cầu:

* Mỗi module có một `logger = logging.getLogger(__name__)`.
* Ghi log khi:

  * Bắt đầu cào dữ liệu.
  * Tải một trang thành công.
  * Phân tích HTML.
  * Lưu dữ liệu vào cơ sở dữ liệu.
  * Gặp lỗi mạng hoặc lỗi phân tích.
* Ghi đồng thời ra:

  * Console.
  * `scraper.log`.

**Mở rộng:**

* Ghi thời gian thực thi của mỗi trang.
* Ghi số lượng truyện đã cào thành công và thất bại.

Đây là nền tảng để sau này kết hợp với **Celery**, **Dramatiq** hoặc các worker chạy nền.

---

# Tổng kết buổi 24

Hôm nay bạn đã học:

* ✅ Logging là gì.
* ✅ Vì sao không nên dùng `print()`.
* ✅ Module `logging`.
* ✅ `basicConfig()`.
* ✅ Log Level.
* ✅ `Logger`.
* ✅ `Handler`.
* ✅ `Formatter`.
* ✅ `FileHandler`.
* ✅ `StreamHandler`.
* ✅ Logger theo module.
* ✅ Tổ chức Logging trong dự án thực tế.

---

# Góc lập trình viên chuyên nghiệp

Trong các dự án Python lớn, logging thường được cấu hình theo một module riêng, ví dụ:

```text
project/
│
├── config/
│   └── logging_config.py
├── api/
├── services/
├── repositories/
└── main.py
```

`main.py` chỉ gọi một lần:

```python
from config.logging_config import setup_logging

setup_logging()
```

Sau đó **mọi module** đều chỉ cần:

```python
import logging

logger = logging.getLogger(__name__)
```

Điều này giúp:

* Không lặp lại cấu hình.
* Dễ thay đổi định dạng log.
* Dễ chuyển từ ghi file sang gửi log lên ELK, Grafana Loki hoặc dịch vụ cloud.
* Phù hợp với kiến trúc **Clean Architecture** và **Domain-Driven Design** mà bạn đã học.

---

# Chuẩn bị cho Buổi 25

Ở **Buổi 25**, chúng ta sẽ học **Logging nâng cao** với các nội dung mà hầu hết lập trình viên mới ít biết nhưng rất quan trọng trong production:

* `RotatingFileHandler`.
* `TimedRotatingFileHandler`.
* `QueueHandler` và `QueueListener` cho ứng dụng đa luồng.
* `LoggerAdapter`.
* `Filter`.
* Ghi đầy đủ stack trace bằng `logger.exception()`.
* Logging có cấu trúc (Structured Logging).
* Thiết kế hệ thống log cho ứng dụng CLI, Web API, GUI, Scraper và các worker Celery/Dramatiq.

Đây là bước giúp bạn xây dựng hệ thống logging **an toàn, hiệu quả và sẵn sàng cho môi trường production**.
