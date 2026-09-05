# Buổi 7 — `fileConfig()` và Logging Configuration Architecture

Ở Buổi 6, chúng ta đã dùng:

```python
logging.config.dictConfig()
```

Đây là cách hiện đại và linh hoạt nhất trong Python standard library.

Hôm nay chúng ta học thêm:

```python
logging.config.fileConfig()
```

và quan trọng hơn là hiểu **kiến trúc configuration của Logging**.

---

# 1. `fileConfig()` là gì?

`fileConfig()` cho phép cấu hình logging từ một file dạng **INI**.

Thay vì:

```python
LOGGING = {
    "version": 1,
    ...
}
```

ta có:

```text
logging.ini
```

và:

```python
logging.config.fileConfig("logging.ini")
```

Kiến trúc:

```text
logging.ini
     │
     ▼
fileConfig()
     │
     ▼
Logging System
     │
     ├── Logger
     ├── Handler
     └── Formatter
```

---

# 2. Ví dụ đơn giản nhất

File:

```text
logging.ini
```

Nội dung:

```ini
[loggers]
keys=root

[handlers]
keys=console

[formatters]
keys=standard

[logger_root]
level=INFO
handlers=console

[handler_console]
class=StreamHandler
level=INFO
formatter=standard
args=(sys.stdout,)

[formatter_standard]
format=%(asctime)s | %(levelname)s | %(name)s | %(message)s
datefmt=%Y-%m-%d %H:%M:%S
```

Python:

```python
import logging
import logging.config

logging.config.fileConfig("logging.ini")

logger = logging.getLogger(__name__)

logger.info("Application started")
```

---

# 3. Cấu trúc của `logging.ini`

Có 3 phần khai báo chính:

```ini
[loggers]
...

[handlers]
...

[formatters]
...
```

Sau đó định nghĩa chi tiết:

```ini
[logger_root]
...

[logger_myapp]
...

[handler_console]
...

[formatter_standard]
...
```

Mental model:

```text
logging.ini
│
├── [loggers]
│       │
│       └── logger definitions
│
├── [handlers]
│       │
│       └── handler definitions
│
└── [formatters]
        │
        └── formatter definitions
```

---

# 4. `[loggers]`

Ví dụ:

```ini
[loggers]
keys=root,myapp
```

Có hai logger:

```text
root
myapp
```

Sau đó phải định nghĩa:

```ini
[logger_root]
...
```

và:

```ini
[logger_myapp]
...
```

---

# 5. Root logger

```ini
[logger_root]
level=INFO
handlers=console
```

Nghĩa là:

```text
root
 │
 └── level = INFO
     handler = console
```

---

# 6. Named logger

Ví dụ:

```ini
[logger_myapp]
level=DEBUG
handlers=console
qualname=myapp
propagate=0
```

Có 4 thành phần quan trọng:

```ini
level=DEBUG
```

Logger level.

```ini
handlers=console
```

Handler được gắn trực tiếp.

```ini
qualname=myapp
```

Tên logger.

```ini
propagate=0
```

Không propagate lên root.

---

# 7. `qualname`

Đây là điểm quan trọng trong `fileConfig()`.

```ini
qualname=myapp
```

tương ứng:

```python
logging.getLogger("myapp")
```

Nếu:

```ini
qualname=myapp.crawler
```

thì:

```python
logging.getLogger("myapp.crawler")
```

Hierarchy:

```text
root
 │
 └── myapp
      │
      └── crawler
```

---

# 8. `[handlers]`

Ví dụ:

```ini
[handlers]
keys=console,file
```

Ta khai báo hai handler:

```text
console
file
```

Sau đó:

```ini
[handler_console]
...
```

và:

```ini
[handler_file]
...
```

---

# 9. Console Handler

```ini
[handler_console]
class=StreamHandler
level=INFO
formatter=standard
args=(sys.stdout,)
```

Tương đương gần như:

```python
handler = logging.StreamHandler(sys.stdout)

handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
```

---

# 10. File Handler

```ini
[handler_file]
class=FileHandler
level=DEBUG
formatter=standard
args=("app.log", "a", "utf-8")
```

Tương đương:

```python
handler = logging.FileHandler(
    "app.log",
    mode="a",
    encoding="utf-8",
)
```

---

# 11. Formatter

Khai báo:

```ini
[formatters]
keys=standard
```

Sau đó:

```ini
[formatter_standard]
format=%(asctime)s | %(levelname)s | %(name)s | %(message)s
datefmt=%Y-%m-%d %H:%M:%S
```

Output:

```text
2026-09-05 22:20:10 | INFO | myapp.crawler | Start crawling
```

---

# 12. Configuration hoàn chỉnh

Bây giờ xây một cấu hình thực tế hơn.

```ini
[loggers]
keys=root,myapp

[handlers]
keys=console,file,error_file

[formatters]
keys=standard,detailed


[logger_root]
level=WARNING
handlers=console


[logger_myapp]
level=DEBUG
handlers=console,file,error_file
qualname=myapp
propagate=0


[handler_console]
class=StreamHandler
level=INFO
formatter=standard
args=(sys.stdout,)


[handler_file]
class=FileHandler
level=DEBUG
formatter=detailed
args=("app.log", "a", "utf-8")


[handler_error_file]
class=FileHandler
level=ERROR
formatter=detailed
args=("error.log", "a", "utf-8")


[formatter_standard]
format=%(asctime)s | %(levelname)s | %(name)s | %(message)s
datefmt=%Y-%m-%d %H:%M:%S


[formatter_detailed]
format=%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s
datefmt=%Y-%m-%d %H:%M:%S
```

Python:

```python
import logging
import logging.config

logging.config.fileConfig("logging.ini")

logger = logging.getLogger(__name__)

logger.debug("Debug")
logger.info("Info")
logger.warning("Warning")
logger.error("Error")
```

---

# 13. Architecture lúc này

```text
                         logging.ini
                              │
                              ▼
                       fileConfig()
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
              Logger       Handler      Formatter
                 │            │            │
                 └────────────┼────────────┘
                              ▼
                         LogRecord
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
              Console       app.log     error.log
```

---

# 14. `dictConfig()` vs `fileConfig()`

Đây là phần quan trọng nhất của Buổi 7.

## `dictConfig()`

Configuration nằm trong Python:

```python
LOGGING = {
    "version": 1,
    ...
}
```

Ưu điểm:

* rất linh hoạt
* dễ tạo configuration động
* hỗ trợ object/config phức tạp
* phù hợp application hiện đại
* dễ tích hợp với environment variables
* dễ quản lý trong code

---

## `fileConfig()`

Configuration nằm trong INI:

```text
logging.ini
```

Ưu điểm:

* configuration tách khỏi code
* đơn giản
* dễ đọc với người quen INI
* phù hợp legacy application

Nhược điểm:

* syntax cũ
* kém linh hoạt
* khó biểu diễn configuration phức tạp
* không mạnh bằng `dictConfig()`

---

# 15. So sánh

| Feature            | `basicConfig()` | `fileConfig()` | `dictConfig()` |
| ------------------ | --------------: | -------------: | -------------: |
| Dễ học             |           ⭐⭐⭐⭐⭐ |            ⭐⭐⭐ |            ⭐⭐⭐ |
| Script nhỏ         |               ✅ |             ⚠️ |             ⚠️ |
| INI config         |               ❌ |              ✅ |              ❌ |
| Dict config        |               ❌ |              ❌ |              ✅ |
| Nhiều handler      |              ⚠️ |              ✅ |              ✅ |
| Nhiều logger       |              ⚠️ |              ✅ |              ✅ |
| Configuration động |               ❌ |             ⚠️ |              ✅ |
| Production         |              ⚠️ |             ⚠️ |              ✅ |
| Modern Python      |               ⭐ |             ⭐⭐ |          ⭐⭐⭐⭐⭐ |

Nếu bắt đầu project mới:

> **Ưu tiên `dictConfig()`**

---

# 16. Một vấn đề với `fileConfig()`

Giả sử:

```python
logging.config.fileConfig("logging.ini")
```

sau đó application đã có logger từ thư viện khác.

`fileConfig()` có behavior liên quan đến việc disable các logger hiện có.

Có thể kiểm soát bằng:

```python
logging.config.fileConfig(
    "logging.ini",
    disable_existing_loggers=False,
)
```

Đây là option rất đáng nhớ.

Trong application có nhiều thư viện:

```text
myapp
 │
 ├── httpx
 ├── asyncio
 ├── sqlite
 └── third-party packages
```

thì thường cần đặc biệt chú ý `disable_existing_loggers`.

---

# 17. Tại sao không nên hard-code đường dẫn?

Không nên:

```python
logging.config.fileConfig(
    "/home/user/project/logging.ini"
)
```

Nên sử dụng `pathlib`.

```python
from pathlib import Path
import logging.config


BASE_DIR = Path(__file__).resolve().parent

logging.config.fileConfig(
    BASE_DIR / "logging.ini",
    disable_existing_loggers=False,
)
```

Nhưng với project lớn, ta thường đi xa hơn.

---

# 18. Logging configuration architecture

Ví dụ project:

```text
myapp/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── crawler/
│   │   ├── crawler.py
│   │   └── parser.py
│   │
│   ├── database/
│   │   └── repository.py
│   │
│   └── service/
│       └── story_service.py
│
├── config/
│   └── logging.py
│
└── logs/
    ├── app.log
    └── error.log
```

---

# 19. `config/logging.py`

Có thể viết:

```python
import logging.config
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(exist_ok=True)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    # ...
}


def setup_logging() -> None:
    logging.config.dictConfig(LOGGING)
```

Điểm quan trọng:

```text
Application
    │
    ▼
setup_logging()
    │
    ▼
dictConfig()
    │
    ▼
Logging infrastructure
```

---

# 20. Tách Environment

Production thường không muốn:

```text
development
    DEBUG

production
    INFO
```

dùng cùng một cấu hình.

Có thể:

```text
config/
│
├── logging.py
├── development.py
└── production.py
```

Hoặc dùng environment:

```bash
APP_ENV=development
```

Python:

```python
import os

environment = os.getenv(
    "APP_ENV",
    "development",
)
```

Sau đó:

```python
if environment == "production":
    ...
```

Tuy nhiên, với hệ thống lớn, ta sẽ học cách thiết kế configuration tốt hơn thay vì nhét quá nhiều `if/else` vào logging config.

---

# 21. Một architecture tốt hơn

```text
                 Environment
                      │
                      ▼
                Configuration
                      │
             ┌────────┴────────┐
             ▼                 ▼
       Development         Production
             │                 │
             └────────┬────────┘
                      ▼
                Logging Setup
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Console      App Log    Error Log
```

---

# 22. Module không biết configuration

Đây là nguyên tắc rất quan trọng.

`crawler.py`:

```python
import logging

logger = logging.getLogger(__name__)


class Crawler:

    def crawl(self):
        logger.info("Start crawling")
```

Crawler **không biết**:

```text
log file ở đâu
formatter là gì
handler nào
level nào
console hay file
```

Tất cả được quyết định bởi infrastructure.

```text
crawler.py
    │
    │ logger.info()
    ▼
logging infrastructure
    │
    ├── Console
    ├── app.log
    └── error.log
```

Đây chính là separation of concerns.

---

# 23. Liên hệ với Clean Architecture

Đây là chỗ kiến thức Logging bắt đầu kết nối với những thứ bạn đã học.

Ví dụ:

```text
Clean Architecture

Presentation
    │
Application
    │
Domain
    │
Infrastructure
```

Logging:

```text
Domain
    │
    │ logger.info()
    ▼
Python Logging API
    │
    ▼
Infrastructure configuration
    │
    ├── Console
    ├── File
    └── External logging system
```

Domain/application không nên biết:

```text
FileHandler
RotatingFileHandler
JSONFormatter
QueueHandler
```

Chúng thuộc infrastructure.

---

# 24. Một nguyên tắc rất quan trọng

### Logger là dependency nhẹ

Module chỉ cần:

```python
logger = logging.getLogger(__name__)
```

### Handler là infrastructure

Không nên:

```python
logger.addHandler(...)
```

trong business module.

### Formatter là presentation của log

Không nên để business logic quyết định:

```text
timestamp
JSON
file name
thread name
```

### Configuration thuộc application/infrastructure

```text
setup_logging()
```

được gọi ở application entry point.

---

# 25. Flow production

Một application tốt có flow:

```text
main()
 │
 ├── load configuration
 │
 ├── setup logging
 │
 ├── initialize database
 │
 ├── initialize services
 │
 └── run application
```

Cụ thể:

```python
def main():
    config = load_config()

    setup_logging(config)

    database = create_database(config)

    service = create_service(database)

    service.run()
```

Logging được setup **trước khi application bắt đầu chạy**.

---

# 26. Bài tập Buổi 7

Hãy tạo project:

```text
logging_demo/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── crawler.py
│   └── database.py
│
├── config/
│   └── logging.py
│
└── logs/
```

Yêu cầu:

### `crawler.py`

```python
logger = logging.getLogger(__name__)
```

Log:

```text
DEBUG
INFO
WARNING
ERROR
```

### `database.py`

Tương tự.

### Logging

```text
Console
    INFO+

app.log
    DEBUG+

error.log
    ERROR+
```

### Formatter console

```text
2026-09-05 22:30:00 | INFO | app.crawler | Start crawling
```

### Formatter file

```text
2026-09-05 22:30:00 | INFO | app.crawler | crawler.py:15 | Start crawling
```

### Đặc biệt

Không được viết:

```python
FileHandler(...)
```

trong:

```text
crawler.py
database.py
```

---

# 27. Bài tập nâng cao

Thử tạo:

```text
app
│
├── crawler
├── database
└── service
```

và cấu hình:

```text
myapp.crawler
    DEBUG

myapp.database
    INFO

myapp.service
    DEBUG
```

Sau đó quan sát:

```python
logging.getLogger(__name__)
```

tự động tạo hierarchy:

```text
root
 │
 └── app
      ├── crawler
      ├── database
      └── service
```

---

# 28. Kết luận Buổi 7

Ba cách cấu hình chúng ta đã biết:

```text
basicConfig()
     │
     └── đơn giản

fileConfig()
     │
     └── INI / legacy

dictConfig()
     │
     └── production / flexible
```

Nếu xây project Python mới, mental model nên là:

```text
                    Application
                         │
                         ▼
                  setup_logging()
                         │
                         ▼
                   dictConfig()
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
     Logger           Handler         Formatter
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                      Output
```

Và module application chỉ cần:

```python
import logging

logger = logging.getLogger(__name__)
```

**Không tự cấu hình Handler.**

---

## Buổi 8 — Logging trong Package / Application

Buổi tiếp theo chúng ta sẽ giải quyết một vấn đề rất thực tế:

```text
Python Package
       │
       ├── module A
       ├── module B
       ├── module C
       └── third-party libraries
```

Làm thế nào để **library không phá logging của application**, xử lý `NullHandler`, `propagate`, root logger, package logger và thiết kế logging API đúng chuẩn cho một Python package.
