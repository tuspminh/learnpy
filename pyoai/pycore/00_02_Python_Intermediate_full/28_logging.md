# Buổi 28. Logging trong Python (Deep Dive)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu vì sao Logging quan trọng hơn `print()`.
> * Hiểu kiến trúc của module `logging`.
> * Thành thạo `Logger`, `Handler`, `Formatter`, `Filter`.
> * Sử dụng các mức log (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
> * Ghi log ra Console và File.
> * Sử dụng `RotatingFileHandler`, `TimedRotatingFileHandler`.
> * Tổ chức hệ thống logging cho dự án thực tế.

---

# 1. Logging là gì?

Logging là quá trình **ghi lại các sự kiện xảy ra trong chương trình**.

Ví dụ:

```text
2026-08-01 09:00:00 INFO Application started
2026-08-01 09:01:12 INFO User login
2026-08-01 09:01:13 ERROR Database connection failed
2026-08-01 09:02:01 INFO Retry connection...
```

---

## Tại sao không dùng `print()`?

Người mới học thường làm:

```python
print("Start program")
print("Download story")
print("Success")
```

Khi chương trình có:

* 100 module
* 30 thread
* chạy 24/7
* hàng triệu dòng log

thì `print()` hoàn toàn không đáp ứng được.

---

# 2. Logging vs Print

| Print              | Logging                   |
| ------------------ | ------------------------- |
| Chỉ in ra màn hình | Console, File, Network... |
| Không có mức độ    | Có Level                  |
| Không có timestamp | Có timestamp              |
| Không có formatter | Có formatter              |
| Không lọc được     | Lọc được                  |
| Không xoay log     | Có Rotating Log           |

---

# 3. Module `logging`

Python có sẵn:

```python
import logging
```

Không cần cài thêm.

---

# 4. Logging cơ bản

```python
import logging

logging.warning("Hello")
```

Output

```text
WARNING:root:Hello
```

---

# 5. Các Level

| Level    | Giá trị |
| -------- | ------- |
| DEBUG    | 10      |
| INFO     | 20      |
| WARNING  | 30      |
| ERROR    | 40      |
| CRITICAL | 50      |

---

## DEBUG

```python
logging.debug("Variable x = 10")
```

Dùng để debug.

---

## INFO

```python
logging.info("Server started")
```

Thông tin bình thường.

---

## WARNING

```python
logging.warning("Disk almost full")
```

Có vấn đề nhưng chương trình vẫn chạy.

---

## ERROR

```python
logging.error("Cannot connect database")
```

Có lỗi.

---

## CRITICAL

```python
logging.critical("System crash")
```

Lỗi nghiêm trọng.

---

# 6. Vì sao DEBUG không hiện?

```python
import logging

logging.debug("Hello")
```

Không có gì.

Lý do:

Mặc định level là

```text
WARNING
```

Nên

```text
DEBUG

INFO
```

đều bị bỏ qua.

---

# 7. `basicConfig()`

```python
import logging

logging.basicConfig(level=logging.DEBUG)

logging.debug("Debug")
logging.info("Info")
```

Output

```text
DEBUG:root:Debug
INFO:root:Info
```

---

# 8. Format Log

Mặc định

```text
INFO:root:Hello
```

Khó đọc.

Có thể format.

```python
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

logging.info("Server Start")
```

Ví dụ

```text
2026-08-01 13:45:21 INFO Server Start
```

---

# 9. Các Placeholder

| Placeholder      | Ý nghĩa   |
| ---------------- | --------- |
| `%(asctime)s`    | Thời gian |
| `%(levelname)s`  | Level     |
| `%(message)s`    | Nội dung  |
| `%(filename)s`   | File      |
| `%(lineno)d`     | Dòng      |
| `%(module)s`     | Module    |
| `%(funcName)s`   | Hàm       |
| `%(threadName)s` | Thread    |
| `%(process)d`    | Process   |

Ví dụ

```python
format = "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
```

---

# 10. Logger

Trong dự án thực tế

Không dùng

```python
logging.info(...)
```

Mà

```python
logger = logging.getLogger(__name__)
```

Ví dụ

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Application Start")
```

`__name__`

sẽ là

```text
crawler.parser

crawler.database

crawler.download
```

rất hữu ích để xác định nguồn log.

---

# 11. Logger Hierarchy

Ví dụ

```text
crawler

├── parser

├── downloader

└── database
```

Logger

```python
logging.getLogger("crawler")
```

cha của

```python
logging.getLogger("crawler.parser")
```

Đây gọi là

```text
Logger Hierarchy
```

Một trong những đặc điểm mạnh nhất của `logging`.

---

# 12. Handler

Logger

↓

Handler

↓

Nơi ghi log.

Có nhiều Handler.

```text
Console

File

Socket

SMTP

HTTP

Memory
```

---

# 13. Console Handler

```python
import logging

logger = logging.getLogger()

handler = logging.StreamHandler()

logger.addHandler(handler)
```

---

# 14. File Handler

```python
import logging

logger = logging.getLogger()

handler = logging.FileHandler("app.log", encoding="utf-8")

logger.addHandler(handler)
```

Log sẽ được ghi vào

```text
app.log
```

---

# 15. Formatter

```python
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
```

Gán

```python
handler.setFormatter(formatter)
```

---

# 16. Hoàn chỉnh

```python
import logging

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)

handler = logging.FileHandler("app.log", encoding="utf-8")

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

handler.setFormatter(formatter)

logger.addHandler(handler)

logger.info("Application Start")
```

---

# 17. Console + File

Có thể ghi nhiều nơi.

```python
logger = logging.getLogger()

logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()

file = logging.FileHandler("app.log", encoding="utf-8")

logger.addHandler(console)

logger.addHandler(file)
```

Một log

↓

Console

↓

File

đồng thời.

---

# 18. RotatingFileHandler

Nếu log quá lớn

```text
app.log

15 GB
```

Không ổn.

Dùng

```python
from logging.handlers import RotatingFileHandler
```

Ví dụ

```python
handler = RotatingFileHandler(
    "app.log", maxBytes=1024 * 1024, backupCount=5, encoding="utf-8"
)
```

Ý nghĩa

```text
1 MB

↓

Tạo app.log.1

↓

app.log.2

...

Tối đa 5 file
```

---

# 19. TimedRotatingFileHandler

Xoay log theo thời gian.

```python
from logging.handlers import TimedRotatingFileHandler
```

```python
handler = TimedRotatingFileHandler(
    "app.log", when="midnight", interval=1, backupCount=30, encoding="utf-8"
)
```

Mỗi ngày

↓

Tạo file mới.

---

# 20. Exception Logging

Sai

```python
try:
    ...
except Exception as e:
    print(e)
```

Đúng

```python
logger.exception("Download failed")
```

Ví dụ

```python
try:
    1 / 0

except Exception:
    logger.exception("Error")
```

Log

```text
Traceback...
```

đầy đủ.

---

# 21. Logging trong Crawler

```python
logger.info("Downloading %s", url)
```

Sau khi thành công

```python
logger.info("Downloaded %s", title)
```

Nếu lỗi

```python
logger.exception("Download failed")
```

---

# 22. Logging trong Repository

```python
logger.info("Insert Story id=%s", story.id)
```

---

# 23. Logging trong Service

```python
logger.info("Create User %s", username)
```

---

# 24. Logging trong CLI

```python
logger.info("Command: crawl")
```

---

# 25. Không dùng f-string trong Logging

Sai

```python
logger.info(f"Download {url}")
```

Đúng

```python
logger.info("Download %s", url)
```

Vì sao?

Logger chỉ format chuỗi khi cần ghi log. Nếu mức log bị bỏ qua, việc định dạng chuỗi cũng được bỏ qua, giúp tiết kiệm tài nguyên.

---

# 26. Filter

Filter cho phép quyết định log nào được ghi.

Ví dụ:

```python
import logging


class ErrorOnlyFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.ERROR
```

Áp dụng:

```python
handler.addFilter(ErrorOnlyFilter())
```

Kết quả:

* `INFO` → bỏ qua.
* `ERROR`, `CRITICAL` → được ghi.

---

# 27. Cấu trúc Logging trong dự án

```text
project/

├── logs/
│   ├── app.log
│   ├── app.log.1
│   └── app.log.2
│
├── utils/
│   └── logger.py
│
├── crawler/
│
├── parser/
│
└── main.py
```

**utils/logger.py**

```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler)
```

Các module khác:

```python
from utils.logger import logger

logger.info("Crawler started")
```

---

# 28. Best Practices

## ✔ Không dùng `print()`

Sai

```python
print("Database Error")
```

Đúng

```python
logger.error("Database Error")
```

---

## ✔ Dùng `logger = logging.getLogger(__name__)`

Giúp biết chính xác log phát sinh từ module nào.

---

## ✔ Dùng `logger.exception()`

Khi bắt ngoại lệ.

---

## ✔ Dùng `RotatingFileHandler`

Không để log tăng vô hạn.

---

## ✔ Dùng tham số của logger

Đúng

```python
logger.info("User %s login", username)
```

Sai

```python
logger.info(f"User {username} login")
```

---

## ✔ Một nơi cấu hình Logging

Toàn bộ cấu hình nên nằm trong:

```text
utils/logger.py
```

Không cấu hình lại ở nhiều module khác nhau.

---

# 29. Mini Project - Logging System

```
project/

├── logs/
│
├── utils/
│   └── logger.py
│
├── crawler.py
│
├── parser.py
│
└── main.py
```

Yêu cầu:

* Ghi log ra Console.
* Ghi log ra File.
* Xoay log khi đạt 1 MB.
* Định dạng:

```text
2026-08-01 13:30:20 | INFO | crawler | Download story...
```

Các module đều sử dụng:

```python
logger = logging.getLogger(__name__)
```

để log hiển thị đúng tên module.

---

# Tổng kết

Sau buổi học này, bạn đã nắm được:

* Vai trò của `logging` và lợi ích so với `print()`.
* Các thành phần chính: `Logger`, `Handler`, `Formatter`, `Filter`.
* Các mức log (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
* Ghi log ra Console và File.
* Xoay log với `RotatingFileHandler` và `TimedRotatingFileHandler`.
* Ghi ngoại lệ bằng `logger.exception()`.
* Các thực hành tốt khi xây dựng hệ thống logging cho ứng dụng thực tế.

# Bài tập thực hành

### Bài 1

Cấu hình logging để ghi cả ra Console và file `logs/app.log` với định dạng:

```text
%(asctime)s | %(levelname)s | %(name)s | %(message)s
```

### Bài 2

Tạo ba module:

* `database.py`
* `crawler.py`
* `parser.py`

Mỗi module sử dụng:

```python
logger = logging.getLogger(__name__)
```

và ghi ít nhất một log ở mức `INFO` và một log ở mức `ERROR`.

### Bài 3

Cấu hình `RotatingFileHandler` với:

* `maxBytes=100 * 1024` (100 KB)
* `backupCount=3`

Quan sát các file log được tạo khi kích thước vượt giới hạn.

### Bài 4

Viết một chương trình cố tình phát sinh `ZeroDivisionError`, bắt ngoại lệ và ghi bằng:

```python
logger.exception("Unexpected error")
```

Quan sát traceback được lưu trong file log.

### Bài 5

Viết `ErrorOnlyFilter` để chỉ ghi các log từ mức `ERROR` trở lên vào `errors.log`, trong khi `app.log` vẫn ghi tất cả các mức từ `INFO`.

### Bài 6 (Thử thách)

Thiết kế một module `logger.py` có hàm:

```python
def setup_logging(log_dir: str = "logs") -> logging.Logger:
    """Khởi tạo và trả về logger dùng chung cho toàn bộ ứng dụng."""
```

Yêu cầu:

* Tự tạo thư mục `logs` nếu chưa tồn tại.
* Ghi đồng thời ra Console và File.
* Sử dụng `RotatingFileHandler`.
* Định dạng thống nhất.
* Có thể tái sử dụng trong mọi dự án Python.

---

# Chuẩn bị cho buổi sau

Ở **Buổi 29**, chúng ta sẽ học **Regular Expression (Regex)**, bao gồm:

* Module `re`.
* `match()`, `search()`, `fullmatch()`, `findall()`, `finditer()`.
* `split()`, `sub()`, `subn()`.
* Nhóm bắt (`groups`), named groups.
* Lookahead, Lookbehind.
* Biên từ (`\b`), neo (`^`, `$`).
* Xây dựng biểu thức chính quy để kiểm tra email, số điện thoại, mật khẩu, URL và trích xuất dữ liệu từ văn bản. Đây là một trong những kỹ năng quan trọng trong xử lý dữ liệu và crawler.
