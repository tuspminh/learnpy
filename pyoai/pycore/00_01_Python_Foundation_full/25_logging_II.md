# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 25: Logging Chuyên nghiệp (Phần 2) - Rotating Log, Structured Logging, `logger.exception()`, Queue Logging và Logging Production

> **Đây là buổi học mà hầu hết lập trình viên Python mới không biết, nhưng các hệ thống production đều sử dụng.**

Nếu bạn mở mã nguồn của:

* Django
* FastAPI
* Celery
* Scrapy
* Uvicorn
* Gunicorn
* Airflow
* Home Assistant

bạn sẽ thấy họ đều xây dựng **một hệ thống logging hoàn chỉnh**, chứ không chỉ gọi:

```python
logging.info(...)
```

Buổi học này sẽ giúp bạn tiến gần hơn đến cách làm của các dự án Python chuyên nghiệp.

---

# Mục tiêu

Sau buổi này bạn sẽ:

* Hiểu vì sao cần xoay vòng log (Log Rotation).
* Thành thạo `RotatingFileHandler`.
* Thành thạo `TimedRotatingFileHandler`.
* Biết `logger.exception()`.
* Biết `LoggerAdapter`.
* Hiểu `Filter`.
* Hiểu Queue Logging.
* Hiểu Structured Logging.
* Biết thiết kế logging cho dự án thực tế.

---

# Phần I

# Vì sao phải xoay vòng Log?

Giả sử ứng dụng chạy:

```text
24 giờ/ngày
```

Mỗi phút ghi:

```text
500 log
```

Một tháng:

```text
app.log

↓

12 GB
```

Không thể:

* mở bằng editor
* backup
* upload
* tìm kiếm nhanh

Do đó phải:

> **Rotate Log**

---

# Log Rotation

Ví dụ:

```text
app.log
```

Đầy.

↓

Đổi tên:

```text
app.log.1
```

Tạo:

```text
app.log
```

mới.

---

# Phần II

# RotatingFileHandler

Import:

```python
from logging.handlers import RotatingFileHandler
```

Ví dụ:

```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler("app.log", maxBytes=1024, backupCount=3)

logger.addHandler(handler)
```

---

## Ý nghĩa

```python
maxBytes = 1024
```

↓

Nếu file vượt:

```text
1024 byte
```

↓

Rotate.

---

```python
backupCount = 3
```

Giữ:

```text
app.log

app.log.1

app.log.2

app.log.3
```

Cũ hơn sẽ bị xóa.

---

# Khi nào dùng?

Ví dụ:

* Desktop App
* PySide6
* CLI
* Worker
* IoT

---

# Phần III

# TimedRotatingFileHandler

Có khi không muốn xoay theo kích thước.

Muốn:

```text
Mỗi ngày
```

hoặc:

```text
Mỗi giờ
```

---

Ví dụ:

```python
from logging.handlers import TimedRotatingFileHandler
```

```python
handler = TimedRotatingFileHandler("app.log", when="midnight", backupCount=7)
```

↓

Mỗi ngày:

Sinh file mới.

Giữ:

7 ngày.

---

## Các lựa chọn

```text
S

Seconds
```

```text
M

Minutes
```

```text
H

Hours
```

```text
D

Days
```

```text
midnight
```

```text
W0

Monday
```

...

```text
W6

Sunday
```

---

# Ví dụ

```python
handler = TimedRotatingFileHandler("crawler.log", when="H", interval=1, backupCount=24)
```

↓

Mỗi giờ.

↓

Giữ:

24 file.

---

# Phần IV

# logger.exception()

Rất nhiều người viết:

```python
try:
    ...

except Exception as e:
    logger.error(e)
```

Sai.

---

Đúng:

```python
try:
    ...

except Exception:
    logger.exception("Download failed")
```

Kết quả:

```text
ERROR

Download failed

Traceback ...

...
```

Tự ghi:

* Stack Trace
* Exception

---

## Tương đương

```python
logger.error("Download failed", exc_info=True)
```

---

# Phần V

# LoggerAdapter

Giả sử:

Hệ thống:

```text
100 User
```

Muốn log:

```text
UserID
```

Ví dụ:

```text
User=1001

Login
```

---

```python
import logging

logger = logging.getLogger("app")

adapter = logging.LoggerAdapter(logger, {"user": "1001"})
```

Sau đó:

```python
adapter.info("Login")
```

Formatter:

```python
"%(user)s %(message)s"
```

↓

Kết quả:

```text
1001 Login
```

---

# Khi nào dùng?

* User ID
* Session ID
* Request ID
* Job ID
* Spider Name

Đây là kỹ thuật rất phổ biến trong Web API và hệ thống phân tán.

---

# Phần VI

# Filter

Filter quyết định:

Log nào được phép đi qua.

Ví dụ:

```python
class IgnoreHealthCheck(logging.Filter):
    def filter(self, record):

        return "health" not in record.msg
```

Gắn:

```python
handler.addFilter(IgnoreHealthCheck())
```

---

Ứng dụng:

Không ghi:

```text
GET /health
```

Mỗi giây.

Giảm log.

---

# Phần VII

# QueueHandler

Giả sử:

100 Thread.

↓

Cùng ghi:

```text
app.log
```

Có thể:

* chậm
* nghẽn
* ghi lẫn

Python có:

```python
QueueHandler
```

↓

Log

↓

Queue

↓

Thread riêng

↓

Ghi file.

---

Đây là chuẩn cho:

* Celery
* Gunicorn
* Worker
* Scraper nhiều luồng

---

# Phần VIII

# Structured Logging

Thay vì:

```text
User login
```

Hãy ghi:

```json
{
    "event":"login",
    "user":100,
    "ip":"127.0.0.1"
}
```

Dễ:

* ElasticSearch
* Loki
* Splunk
* Grafana

---

Ví dụ:

```python
logger.info("login", extra={"user": 100, "ip": "127.0.0.1"})
```

---

# Phần IX

# Logging Exception đúng cách

Sai:

```python
except Exception:

    print("Error")
```

---

Sai:

```python
logger.error(e)
```

---

Đúng:

```python
logger.exception("Database Error")
```

---

Nếu:

Không muốn Traceback.

↓

```python
logger.error("Database Error: %s", e)
```

---

# Phần X

# Logging trong Web Scraper

Ví dụ:

```text
Download Page

↓

Parse HTML

↓

Extract

↓

Save Database
```

Nên log:

```text
INFO

Download chapter 100
```

↓

```text
INFO

Extract 28 images
```

↓

```text
WARNING

Retry #2
```

↓

```text
ERROR

Connection timeout
```

↓

```text
INFO

Save completed
```

---

# Phần XI

# Logging trong Celery

Task:

```text
Send Email
```

↓

```text
Start
```

↓

```text
SMTP Connect
```

↓

```text
Success
```

↓

```text
Finished
```

Nếu lỗi:

↓

```python
logger.exception("Email task failed")
```

---

# Phần XII

# Logging trong PySide6

Không nên:

```python
print(button.text())
```

Nên:

```python
logger.info("Button clicked")
```

Nếu lỗi:

```python
logger.exception("Cannot load image")
```

---

# Phần XIII

# Logging theo kiến trúc

```text
config/

    logging_config.py
```

↓

```text
main.py
```

↓

```text
service/
```

↓

```text
repository/
```

↓

```text
api/
```

Mỗi module:

```python
logger = logging.getLogger(__name__)
```

Không gọi:

```python
basicConfig()
```

ở mọi nơi.

---

# Phần XIV

# Logging và Clean Architecture

```text
Presentation

↓

Application

↓

Domain

↓

Infrastructure
```

Nên log:

Presentation:

```text
User login
```

Infrastructure:

```text
SQL

HTTP

Redis
```

Domain:

Chỉ log khi thật cần thiết để tránh trộn lẫn logic nghiệp vụ với hạ tầng.

---

# Phần XV

# Những lỗi phổ biến

## Sai

```python
print(e)
```

---

## Sai

```python
except:
    pass
```

---

## Sai

Một file log:

```text
50 GB
```

Không Rotate.

---

## Sai

Ghi:

```text
Password
```

Không bao giờ ghi:

* Password
* Token
* JWT
* API Key
* Mã OTP
* Thông tin thẻ tín dụng

Nếu cần ghi để debug, hãy che bớt:

```text
token=abcd********
```

---

# Phần XVI

# Bài tập

## Bài 1

Tạo:

```python
RotatingFileHandler
```

↓

1 MB.

↓

Giữ:

5 file.

---

## Bài 2

Tạo:

```python
TimedRotatingFileHandler
```

↓

Mỗi ngày.

↓

Giữ:

14 ngày.

---

## Bài 3

Viết:

```python
logger.exception()
```

Khi:

```python
10 / 0
```

---

## Bài 4

Tạo:

```python
LoggerAdapter
```

↓

UserID.

---

## Bài 5

Viết Filter.

↓

Không ghi:

```text
Ping
```

---

## Bài 6

Thiết kế:

```text
logging_config.py
```

Cho một dự án nhiều module.

---

# Mini Project

# Logging Production cho Ứng dụng Cào Truyện

Đây là mini project sát với dự án bạn đã học ở các buổi về **Repository**, **Clean Architecture** và **DDD**.

Cấu trúc:

```text
story_crawler/
│
├── config/
│   └── logging_config.py
├── crawler/
│   ├── downloader.py
│   ├── parser.py
│   └── scheduler.py
├── repositories/
├── services/
├── database/
├── logs/
└── main.py
```

### Yêu cầu

* Dùng `TimedRotatingFileHandler` để tạo log mới mỗi ngày.
* Ghi log đồng thời ra console và file.
* Mỗi module dùng `logger = logging.getLogger(__name__)`.
* Ghi các sự kiện:

  * Bắt đầu crawl.
  * Tải URL.
  * Retry khi lỗi mạng.
  * Parse HTML.
  * Lưu database.
  * Hoàn thành chương.
* Dùng `logger.exception()` khi có ngoại lệ.
* Thêm `LoggerAdapter` để gắn:

  * `spider_name`
  * `job_id`
* Không ghi thông tin nhạy cảm (cookie, token đăng nhập...).

**Mở rộng:**

* Thêm `QueueHandler` để ghi log bất đồng bộ khi chạy nhiều worker.
* Chuẩn bị định dạng log theo JSON để tích hợp với ELK hoặc Grafana Loki.

---

# Tổng kết buổi 25

Hôm nay bạn đã học:

* ✅ `RotatingFileHandler`
* ✅ `TimedRotatingFileHandler`
* ✅ `logger.exception()`
* ✅ `LoggerAdapter`
* ✅ `Filter`
* ✅ `QueueHandler`
* ✅ Structured Logging
* ✅ Logging trong Web Scraper
* ✅ Logging trong Celery
* ✅ Logging trong PySide6
* ✅ Logging theo Clean Architecture

---

# Góc lập trình viên chuyên nghiệp

Đối với các hệ thống Python hiện đại, logging thường được chia thành hai loại:

### 1. Log dành cho con người (Human-readable)

Ví dụ:

```text
2026-08-01 10:30:15 | INFO | crawler.downloader | Download chapter 120 completed
```

Dùng khi:

* Đọc trực tiếp trên terminal.
* Kiểm tra file log.

---

### 2. Log dành cho máy (Machine-readable)

Ví dụ JSON:

```json
{
  "timestamp": "2026-08-01T10:30:15Z",
  "level": "INFO",
  "logger": "crawler.downloader",
  "event": "chapter_downloaded",
  "chapter_id": 120,
  "duration_ms": 853
}
```

Dùng để:

* ELK Stack
* Grafana Loki
* Splunk
* OpenSearch
* Cloud Logging

Các hệ thống lớn thường ghi **JSON log** để dễ tìm kiếm, thống kê và cảnh báo.

---

# Chuẩn bị cho Buổi 26

Ở **Buổi 26**, chúng ta sẽ bắt đầu một chủ đề cực kỳ quan trọng:

# **Testing trong Python (Phần 1)**

Bạn sẽ học:

* Vì sao phải viết Unit Test.
* `unittest`.
* Test Case.
* Test Fixture (`setUp`, `tearDown`).
* Assertion.
* Chạy test.
* Tổ chức thư mục `tests/`.
* Test cho các lớp, hàm và Repository.

Đây là kỹ năng giúp bạn xây dựng phần mềm **đáng tin cậy**, dễ refactor và tự động kiểm tra khi dự án ngày càng lớn. Đây cũng là nền tảng để sau này học **pytest**, **Mock**, **CI/CD** và kiểm thử cho các ứng dụng FastAPI, PySide6, Scrapy và hệ thống crawler chuyên nghiệp.
