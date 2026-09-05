# Buổi 6 — `logging.config.dictConfig()` Deep Dive

Sau `basicConfig()`, đây là bước rất quan trọng để chuyển từ **logging đơn giản** sang **logging production**.

Ta sẽ học cách cấu hình toàn bộ hệ thống Logging bằng một `dict`:

```text
dictConfig
    │
    ├── formatters
    │      ├── simple
    │      └── detailed
    │
    ├── handlers
    │      ├── console
    │      ├── file
    │      └── error_file
    │
    └── loggers
           ├── myapp
           ├── myapp.crawler
           └── myapp.database
```

---

# 1. Vì sao cần `dictConfig()`?

Với `basicConfig()`:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
```

Rất tiện.

Nhưng khi ứng dụng lớn hơn:

```text
Console
    INFO+

app.log
    DEBUG+

error.log
    ERROR+

crawler.log
    DEBUG+

database.log
    INFO+
```

`basicConfig()` bắt đầu trở nên khó quản lý.

`dictConfig()` cho phép mô tả toàn bộ kiến trúc logging bằng configuration.

---

# 2. Import

```python
import logging
import logging.config
```

Sau đó:

```python
logging.config.dictConfig(config)
```

---

# 3. Cấu trúc cơ bản

Một configuration thường có:

```python
config = {
    "version": 1,

    "formatters": {
        ...
    },

    "handlers": {
        ...
    },

    "loggers": {
        ...
    },

    "root": {
        ...
    },
}
```

Có thể hình dung:

```text
dictConfig
    │
    ├── formatters
    │
    ├── handlers
    │
    ├── loggers
    │
    └── root
```

---

# 4. `version`

Bắt buộc:

```python
"version": 1
```

Ví dụ:

```python
config = {
    "version": 1,
}
```

Hiện tại giá trị sử dụng là:

```python
1
```

Nó không phải version của application.

---

# 5. Formatter

Ví dụ:

```python
"formatters": {
    "simple": {
        "format": "%(levelname)s | %(message)s"
    }
}
```

Ta đặt tên formatter:

```text
simple
```

Sau đó có thể dùng formatter này cho nhiều handler.

---

## Formatter development

```python
"formatters": {
    "detailed": {
        "format": (
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(filename)s:%(lineno)d | "
            "%(message)s"
        ),
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }
}
```

Output:

```text
2026-09-05 22:00:01 | INFO | myapp.crawler | crawler.py:42 | Start crawling
```

---

# 6. Handler

Ví dụ Console:

```python
"handlers": {
    "console": {
        "class": "logging.StreamHandler",
        "level": "INFO",
        "formatter": "detailed",
        "stream": "ext://sys.stdout",
    }
}
```

Có 4 phần quan trọng:

```python
"class": "logging.StreamHandler"
```

Handler type.

```python
"level": "INFO"
```

Handler nhận từ INFO trở lên.

```python
"formatter": "detailed"
```

Dùng formatter nào.

```python
"stream": "ext://sys.stdout"
```

Ghi ra stdout.

---

# 7. FileHandler

```python
"file": {
    "class": "logging.FileHandler",
    "level": "DEBUG",
    "formatter": "detailed",
    "filename": "app.log",
    "encoding": "utf-8",
}
```

Kết quả:

```text
app.log
```

sẽ nhận:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

---

# 8. Kết hợp Console + File

Đây là configuration rất thực tế:

```python
import logging
import logging.config


LOGGING = {
    "version": 1,

    "formatters": {
        "default": {
            "format": (
                "%(asctime)s | "
                "%(levelname)s | "
                "%(name)s | "
                "%(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },

        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "default",
            "filename": "app.log",
            "encoding": "utf-8",
        },
    },

    "root": {
        "level": "DEBUG",
        "handlers": [
            "console",
            "file",
        ],
    },
}


logging.config.dictConfig(LOGGING)
```

Sau đó:

```python
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Application started")
logger.warning("Something looks wrong")
logger.error("Something failed")
```

---

# 9. Cực kỳ quan trọng: Logger level vs Handler level

Đây là kiến thức phải nhớ từ các buổi trước.

Configuration:

```python
"root": {
    "level": "DEBUG",
    "handlers": ["console", "file"],
}
```

Console:

```python
"level": "INFO"
```

File:

```python
"level": "DEBUG"
```

Ta có:

```text
                 Root Logger
                    DEBUG
                      │
          ┌───────────┴───────────┐
          │                       │
      Console                   File
        INFO                    DEBUG
          │                       │
     INFO+ only              DEBUG+
```

Kết quả:

| Log      | Console | File |
| -------- | ------: | ---: |
| DEBUG    |       ❌ |    ✅ |
| INFO     |       ✅ |    ✅ |
| WARNING  |       ✅ |    ✅ |
| ERROR    |       ✅ |    ✅ |
| CRITICAL |       ✅ |    ✅ |

---

# 10. Named Logger

Ta không nhất thiết phải dùng root.

Ví dụ:

```python
"loggers": {
    "myapp": {
        "level": "DEBUG",
        "handlers": [
            "console",
            "file",
        ],
        "propagate": False,
    },
}
```

Sau đó:

```python
logger = logging.getLogger("myapp")
```

hoặc:

```python
logger = logging.getLogger("myapp.crawler")
```

---

# 11. Logger hierarchy

Ví dụ project:

```text
myapp
│
├── crawler
│   ├── http
│   └── parser
│
├── database
│   └── repository
│
└── service
```

Trong code:

```python
# crawler.py
logger = logging.getLogger("myapp.crawler")
```

```python
# parser.py
logger = logging.getLogger("myapp.crawler.parser")
```

```python
# repository.py
logger = logging.getLogger("myapp.database.repository")
```

Ta có:

```text
root
 │
 └── myapp
      │
      ├── crawler
      │    └── parser
      │
      ├── database
      │    └── repository
      │
      └── service
```

Đây chính là sức mạnh của named logger.

---

# 12. Cấu hình từng subsystem

Ví dụ:

```python
"loggers": {
    "myapp.crawler": {
        "level": "DEBUG",
        "handlers": ["console"],
        "propagate": False,
    },

    "myapp.database": {
        "level": "INFO",
        "handlers": ["console"],
        "propagate": False,
    },
}
```

Ta có thể điều khiển riêng:

```text
crawler
    DEBUG

database
    INFO
```

Ví dụ:

```python
crawler_logger.debug("Downloading chapter")
```

sẽ xuất hiện.

Nhưng:

```python
database_logger.debug("SQL query...")
```

sẽ không xuất hiện.

---

# 13. `propagate`

Đây là phần rất quan trọng.

Ví dụ:

```python
"loggers": {
    "myapp.crawler": {
        "level": "DEBUG",
        "handlers": ["console"],
        "propagate": False,
    }
}
```

Có nghĩa:

```text
myapp.crawler
      │
      ▼
   console
      X
      │
      X
    root
```

Log không đi tiếp lên root.

Nếu:

```python
"propagate": True
```

thì:

```text
myapp.crawler
      │
      ├── console
      │
      ▼
    root
      │
      └── handlers
```

Có thể dẫn đến duplicate log.

---

# 14. `root`

Root logger cấu hình như sau:

```python
"root": {
    "level": "WARNING",
    "handlers": ["console"],
}
```

Điều này nghĩa:

```text
root
 │
 └── WARNING+
```

Các logger không được cấu hình riêng có thể kế thừa cấu hình từ root.

---

# 15. `disable_existing_loggers`

Một option rất dễ gây hiểu nhầm:

```python
"disable_existing_loggers": False
```

Ví dụ:

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    ...
}
```

Trong application thực tế, thường nên cân nhắc:

```python
False
```

đặc biệt khi application sử dụng thư viện bên thứ ba.

Nếu:

```python
True
```

các logger đã tồn tại trước khi `dictConfig()` chạy có thể bị disable nếu không được cấu hình lại.

Ví dụ:

```text
application
    │
    ├── myapp
    │
    ├── httpx
    │
    ├── asyncio
    │
    └── third-party-library
```

Không nên vô tình làm logger của thư viện bị disable chỉ vì logging config.

---

# 16. Configuration hoàn chỉnh

Bây giờ xây một cấu hình gần production hơn:

```python
import logging
import logging.config


LOGGING = {
    "version": 1,

    "disable_existing_loggers": False,

    "formatters": {
        "standard": {
            "format": (
                "%(asctime)s | "
                "%(levelname)s | "
                "%(name)s | "
                "%(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },

        "detailed": {
            "format": (
                "%(asctime)s | "
                "%(levelname)s | "
                "%(name)s | "
                "%(filename)s:%(lineno)d | "
                "%(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },

        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "app.log",
            "encoding": "utf-8",
        },
    },

    "root": {
        "level": "DEBUG",
        "handlers": [
            "console",
            "file",
        ],
    },
}


logging.config.dictConfig(LOGGING)
```

Sau đó bất kỳ module nào:

```python
import logging

logger = logging.getLogger(__name__)
```

đều có thể sử dụng:

```python
logger.debug("Debug information")
logger.info("Application started")
logger.warning("Potential problem")
logger.error("Something failed")
```

---

# 17. Tách config khỏi code

Đây mới là hướng production.

Thay vì:

```text
main.py
    │
    ├── logging config
    ├── crawler
    ├── database
    └── service
```

nên:

```text
project/
│
├── app/
│   ├── crawler/
│   ├── database/
│   ├── service/
│   └── main.py
│
└── config/
    └── logging.py
```

Hoặc:

```text
config/
    logging_config.py
```

Trong đó:

```python
def setup_logging():
    logging.config.dictConfig(LOGGING)
```

`main.py`:

```python
from config.logging_config import setup_logging

setup_logging()
```

Sau đó mới:

```python
from app.crawler import Crawler
```

Một nguyên tắc rất tốt:

```text
Application startup
        │
        ▼
 setup_logging()
        │
        ▼
 import / create application
        │
        ▼
      run
```

---

# 18. Kiến trúc Logging trong project lớn

Với project crawler mà bạn đang học, ta có thể hướng tới:

```text
                    ┌───────────────┐
                    │ dictConfig()  │
                    └───────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          Formatter      Handler       Logger
                            │
                 ┌──────────┼──────────┐
                 ▼          ▼          ▼
              Console     app.log   error.log
```

Application:

```text
myapp
│
├── crawler
│   ├── http
│   └── parser
│
├── database
│   └── repository
│
├── worker
│
└── cli
```

Mỗi module:

```python
logger = logging.getLogger(__name__)
```

**Không tự tạo Handler.**

Chỉ:

```python
logger.info(...)
logger.debug(...)
logger.warning(...)
logger.error(...)
```

Configuration tập trung ở application startup.

---

# 19. Một sai lầm rất phổ biến

❌ Không nên:

```python
# crawler.py

logger = logging.getLogger(__name__)

handler = logging.FileHandler("crawler.log")
logger.addHandler(handler)
```

rồi:

```python
# database.py

logger = logging.getLogger(__name__)

handler = logging.FileHandler("database.log")
logger.addHandler(handler)
```

Khi project lớn:

```text
Module
 ├── Logger
 ├── Handler
 ├── Formatter
 └── configuration
```

Mỗi module tự quản lý logging → rất khó kiểm soát.

---

# 20. Pattern nên dùng

Module:

```python
import logging

logger = logging.getLogger(__name__)


class Crawler:

    def crawl(self):
        logger.info("Start crawling")

        try:
            ...
        except Exception:
            logger.exception("Crawler failed")
```

Application:

```python
def main():
    setup_logging()

    crawler = Crawler()
    crawler.crawl()
```

Tách:

```text
Module
   │
   │ logger.info()
   ▼
Logging System
   │
   ▼
Configuration
   │
   ├── Console
   ├── File
   └── Error File
```

Đây là architecture chúng ta sẽ tiếp tục xây dựng.

---

# 21. `dictConfig()` và `basicConfig()`

|                    | `basicConfig()` | `dictConfig()` |
| ------------------ | --------------- | -------------- |
| Dễ dùng            | ⭐⭐⭐⭐⭐           | ⭐⭐⭐            |
| Script nhỏ         | ✅               | Có thể         |
| CLI                | ✅               | ✅              |
| Nhiều Handler      | Hạn chế         | ✅              |
| Nhiều Logger       | ❌               | ✅              |
| Formatter phức tạp | Hạn chế         | ✅              |
| Production         | ⚠️              | ✅              |
| Centralized config | ⚠️              | ✅              |
| Architecture lớn   | ❌               | ✅              |

Mental model:

```text
basicConfig()
    ↓
Quick setup

dictConfig()
    ↓
Logging architecture
```

---

# 22. Bài tập Buổi 6

Hãy tự xây:

```text
myapp
│
├── crawler
├── database
└── service
```

Configuration yêu cầu:

### Console

```text
INFO+
```

### `app.log`

```text
DEBUG+
```

### `error.log`

```text
ERROR+
```

### Logger

```text
myapp
    DEBUG

myapp.crawler
    DEBUG

myapp.database
    INFO
```

### Formatter console

```text
2026-09-05 22:10:00 | INFO | myapp.crawler | Start crawling
```

### Formatter file

```text
2026-09-05 22:10:00 | INFO | myapp.crawler | crawler.py:25 | Start crawling
```

Và đặc biệt:

```python
logger = logging.getLogger(__name__)
```

**Không được tạo Handler bên trong `crawler.py`, `database.py`, `service.py`.**

---

# 23. Mục tiêu cần nắm sau Buổi 6

Bạn cần hiểu rõ chuỗi:

```text
dictConfig
    ↓
Logger
    ↓
LogRecord
    ↓
Handler
    ↓
Formatter
    ↓
Output
```

và phân biệt được:

```text
Logger level
      vs
Handler level
```

cũng như:

```text
logger.handlers
      vs
propagate
      vs
root
```

Đây là nền tảng để sang phần tiếp theo.

---

## Buổi 7 — `fileConfig()` và Logging Configuration Architecture

Ta sẽ đi sâu vào:

```text
fileConfig()
INI configuration
        ↓
logging config file
        ↓
application startup
```

và quan trọng hơn: **khi nào dùng `dictConfig()`, khi nào dùng `fileConfig()`, và cách thiết kế một `logging_config.py` production-ready.**
