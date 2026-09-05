# Buổi 9 — Library Logging vs Application Logging — Deep Dive

Buổi này chúng ta sẽ **đóng khung lại toàn bộ kiến trúc logging trong Python package**.

Sau buổi này, bạn cần phân biệt rất rõ:

```text
Library
   ≠
Application
```

và hiểu chính xác vai trò của:

```text
NullHandler
propagate
package logger
root logger
disable_existing_loggers
third-party logger
```

---

# 1. Bài toán thực tế

Giả sử chúng ta có:

```text
myapp/
│
├── main.py
│
├── crawler/
│   ├── crawler.py
│   └── parser.py
│
├── database/
│   └── repository.py
│
└── config/
    └── logging.py
```

Trong đó:

```text
myapp
    ↓
sử dụng
    ↓
storycrawler
    ↓
sử dụng
    ↓
httpx
```

Ta có một logging hierarchy:

```text
root
│
├── myapp
│   ├── crawler
│   └── database
│
├── storycrawler
│   ├── crawler
│   └── parser
│
└── httpx
```

Câu hỏi:

> Ai quyết định log đi đâu?

**Application.**

---

# 2. Library chỉ phát LogRecord

Ví dụ package:

```python
# storycrawler/crawler.py

import logging

logger = logging.getLogger(__name__)


class Crawler:

    def crawl(self, url):
        logger.info("Start crawling %s", url)
```

Library chỉ nói:

```text
"Có một event xảy ra"
```

Nó không nói:

```text
"Ghi event này vào crawler.log"
```

Đó là hai trách nhiệm khác nhau.

---

# 3. Logging API vs Logging Configuration

Đây là một distinction cực kỳ quan trọng.

## Library sử dụng Logging API

```python
logger.debug(...)
logger.info(...)
logger.warning(...)
logger.error(...)
logger.exception(...)
```

## Application sử dụng Logging Configuration

```python
logging.config.dictConfig(...)
```

Architecture:

```text
              LIBRARY
                 │
                 │ logging API
                 ▼
              Logger
                 │
                 ▼
            LogRecord
                 │
                 │
                 ▼
           APPLICATION
                 │
          configuration
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
    Console     File      Error
```

---

# 4. `NullHandler` — hiểu chính xác

Một library có thể thêm:

```python
import logging

logging.getLogger(__name__).addHandler(
    logging.NullHandler()
)
```

`NullHandler` là:

```text
Handler
   │
   └── nhận LogRecord
          │
          └── không tạo output
```

Nó đặc biệt hữu ích cho library.

---

# 5. Vì sao Library cần `NullHandler`?

Giả sử user viết:

```python
from storycrawler import Crawler

Crawler().crawl()
```

và **không cấu hình logging**.

Library vẫn có:

```python
logger.info("Start crawling")
```

Ta không muốn library tự động:

```text
crawler.log
```

hoặc:

```text
Console output
```

`NullHandler` cung cấp một default behavior an toàn.

---

# 6. Package-level NullHandler

Một pattern phổ biến:

```python
# storycrawler/__init__.py

import logging

logging.getLogger(__name__).addHandler(
    logging.NullHandler()
)
```

Khi đó:

```text
storycrawler
    │
    ├── crawler
    ├── parser
    └── database
```

Logger package:

```text
storycrawler
```

có `NullHandler`.

Các child logger:

```text
storycrawler.crawler
storycrawler.parser
storycrawler.database
```

có thể propagate lên hierarchy.

---

# 7. Nhưng `NullHandler` không phải "solution cho mọi thứ"

Đây là nuance quan trọng.

Không nên nghĩ:

```text
Library
   ↓
NullHandler
   ↓
logging xong
```

Library vẫn phải phát log:

```python
logger.debug(...)
logger.info(...)
```

`NullHandler` chỉ là **fallback handler**.

Khi application cấu hình logging:

```text
Library
   │
   ▼
Logger
   │
   ▼
Application handlers
```

application mới quyết định output.

---

# 8. `propagate=True`

Mặc định:

```python
logger.propagate
```

thường là:

```python
True
```

Ví dụ:

```text
storycrawler.crawler
```

phát:

```python
logger.info("Downloaded chapter")
```

Record có thể đi:

```text
storycrawler.crawler
        │
        ▼
storycrawler
        │
        ▼
root
```

Sau đó các handler phù hợp sẽ xử lý.

---

# 9. Tại sao `propagate=True` thường phù hợp với Library?

Bởi vì application có thể kiểm soát:

```text
Library
    │
    ▼
Application
    │
    ├── Console
    ├── app.log
    └── error.log
```

Library không cần biết application đang dùng:

```text
FileHandler
RotatingFileHandler
QueueHandler
SysLogHandler
HTTP handler
JSON formatter
```

---

# 10. `propagate=False` có thể phá architecture

Ví dụ library:

```python
logger.propagate = False
```

và:

```python
handler = logging.FileHandler(
    "storycrawler.log"
)

logger.addHandler(handler)
```

Ta có:

```text
Application
    │
    X
storycrawler
    │
    ▼
storycrawler.log
```

Application muốn:

```text
JSON → stdout
```

nhưng library vẫn:

```text
storycrawler.log
```

Đây là coupling không cần thiết.

---

# 11. Package Logger

Một package lớn nên có namespace riêng.

Ví dụ:

```text
storycrawler
```

Các logger:

```text
storycrawler.crawler
storycrawler.parser
storycrawler.database
storycrawler.http
```

Điều này cho phép application cấu hình cả package:

```python
"storycrawler": {
    "level": "DEBUG",
    ...
}
```

hoặc từng subsystem:

```python
"storycrawler.database": {
    "level": "INFO",
    ...
}
```

---

# 12. Đây là lý do `__name__` rất quan trọng

Đừng viết:

```python
logger = logging.getLogger("app")
```

trong tất cả module.

Hãy:

```python
logger = logging.getLogger(__name__)
```

Ví dụ:

### crawler.py

```python
logger = logging.getLogger(__name__)
```

→

```text
storycrawler.crawler
```

### parser.py

```python
logger = logging.getLogger(__name__)
```

→

```text
storycrawler.parser
```

### repository.py

```python
logger = logging.getLogger(__name__)
```

→

```text
storycrawler.database.repository
```

Hierarchy được tạo tự nhiên.

---

# 13. Application có thể kiểm soát cả package

Ví dụ:

```python
LOGGING = {
    "version": 1,

    "disable_existing_loggers": False,

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
        }
    },

    "loggers": {
        "storycrawler": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        }
    },
}
```

Ta có:

```text
storycrawler
    DEBUG
       │
       ├── crawler
       ├── parser
       ├── database
       └── http
```

---

# 14. Override từng child

Ví dụ muốn database ít verbose hơn:

```python
"loggers": {
    "storycrawler": {
        "level": "DEBUG",
        "handlers": ["console"],
        "propagate": False,
    },

    "storycrawler.database": {
        "level": "INFO",
    },
}
```

Kết quả:

```text
storycrawler
    DEBUG
    │
    ├── crawler
    │     DEBUG
    │
    ├── parser
    │     DEBUG
    │
    └── database
          INFO
```

---

# 15. Third-party Logger

Đây là vấn đề bạn sẽ gặp rất nhiều khi làm project thực tế.

Ví dụ:

```text
myapp
 │
 ├── storycrawler
 │
 ├── httpx
 │
 ├── asyncio
 │
 └── another_library
```

Bạn không sở hữu code của:

```text
httpx
another_library
```

nhưng chúng vẫn có logger.

Ví dụ:

```python
logging.getLogger("httpx")
```

---

# 16. Không nên disable toàn bộ third-party logger

Trong configuration:

```python
"disable_existing_loggers": False
```

thường là lựa chọn an toàn hơn khi application có nhiều dependency.

Mental model:

```text
Application
 │
 ├── own loggers
 │
 └── third-party loggers
          │
          ├── httpx
          ├── ...
          └── ...
```

Ta không muốn configuration của mình vô tình làm chúng biến mất khỏi hệ thống logging.

---

# 17. Nhưng không phải cứ `False` là xong

Ta vẫn có thể cấu hình riêng:

```python
"loggers": {
    "httpx": {
        "level": "WARNING",
    }
}
```

Ví dụ:

```text
httpx
   WARNING+
```

trong khi:

```text
storycrawler
   DEBUG+
```

Kết quả:

```text
storycrawler.crawler
    DEBUG
    INFO
    WARNING
    ERROR

httpx
    WARNING
    ERROR
```

Điều này rất hữu ích khi third-party library quá verbose.

---

# 18. Production Logging Architecture

Một application thực tế có thể:

```text
                         Application
                              │
                       setup_logging()
                              │
                              ▼
                         dictConfig()
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
      myapp.*           storycrawler.*        third-party
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                           Handler
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
                 Console    app.log   error.log
```

Điểm quan trọng:

> Tất cả Logger có thể hội tụ về một hệ thống Handler do Application kiểm soát.

---

# 19. Application không nên tạo Logger cho từng module?

Không.

Application có thể cấu hình:

```text
package namespace
```

nhưng module vẫn tự tạo:

```python
logger = logging.getLogger(__name__)
```

Ví dụ:

```text
Configuration:

storycrawler
    DEBUG
```

Code:

```text
storycrawler/
├── crawler.py
├── parser.py
└── database.py
```

Tất cả tự động nằm dưới namespace:

```text
storycrawler.*
```

---

# 20. Một lỗi subtle: duplicate logs

Giả sử:

```text
storycrawler
    handler = console
```

và:

```text
root
    handler = console
```

Trong child:

```text
storycrawler.crawler
```

nếu:

```python
propagate = True
```

thì:

```text
storycrawler.crawler
       │
       ├── storycrawler handler
       │
       ▼
      root
       │
       └── root handler
```

Có thể thấy:

```text
INFO | Start crawling
INFO | Start crawling
```

---

# 21. Cách giải quyết

Nếu package có handler riêng:

```python
"storycrawler": {
    "handlers": ["console"],
    "propagate": False,
}
```

Nhưng đối với library, tốt hơn là:

```text
Library
    │
    └── không có handler thực sự
             │
             ▼
        propagate=True
             │
             ▼
        Application
```

Do đó duplicate log thường là dấu hiệu:

> **Handler đang được gắn ở quá nhiều tầng.**

---

# 22. Rule thiết kế Handler

Một architecture đơn giản và sạch:

```text
Library
  │
  └── Logger
        │
        │ propagate
        ▼
Application
  │
  └── Handlers
```

Thay vì:

```text
Library
  │
  ├── Handler
  │
  ▼
Application
  │
  └── Handler
```

---

# 23. `logger.handlers` vs `hasHandlers()`

Đây là kiến thức từ Buổi 2 nhưng giờ cần nhìn trong package.

```python
logger.handlers
```

chỉ trả về handler **gắn trực tiếp**.

Trong khi:

```python
logger.hasHandlers()
```

có thể tìm lên ancestor.

Ví dụ:

```text
root
 └── ConsoleHandler

storycrawler
 └── không có handler
```

thì:

```python
logger = logging.getLogger(
    "storycrawler.crawler"
)
```

có thể:

```python
logger.handlers
```

→

```text
[]
```

nhưng:

```python
logger.hasHandlers()
```

→

```text
True
```

vì root có handler.

---

# 24. Đừng dùng `hasHandlers()` để quyết định Library có nên tự add Handler

Đây là một anti-pattern phổ biến:

```python
if not logger.hasHandlers():
    logger.addHandler(...)
```

Tại sao nguy hiểm?

Vì:

```python
hasHandlers()
```

có thể thấy handler của root.

Sau đó behavior phụ thuộc vào toàn bộ application hierarchy.

Library không nên tự động tạo handler chỉ vì:

```python
hasHandlers() == False
```

Nếu cần default handler cho library:

```python
NullHandler
```

là lựa chọn đúng hơn.

---

# 25. Một package hoàn chỉnh

```text
storycrawler/
│
├── __init__.py
├── crawler.py
├── parser.py
└── database.py
```

### `__init__.py`

```python
import logging

logging.getLogger(__name__).addHandler(
    logging.NullHandler()
)
```

### `crawler.py`

```python
import logging

logger = logging.getLogger(__name__)


class Crawler:

    def crawl(self, url):
        logger.info("Start crawling %s", url)

        try:
            ...
        except Exception:
            logger.exception(
                "Crawler failed"
            )
            raise
```

### `parser.py`

```python
import logging

logger = logging.getLogger(__name__)


class Parser:

    def parse(self, html):
        logger.debug("Parsing HTML")
```

### `database.py`

```python
import logging

logger = logging.getLogger(__name__)


class Repository:

    def save(self, item):
        logger.debug("Saving item")
```

Không module nào biết:

```text
FileHandler
Formatter
log path
rotation
console
JSON
```

---

# 26. Application

```python
import logging.config

from storycrawler import Crawler


def setup_logging():
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "default": {
                "format": (
                    "%(asctime)s | "
                    "%(levelname)s | "
                    "%(name)s | "
                    "%(message)s"
                )
            }
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
            }
        },

        "loggers": {
            "storycrawler": {
                "level": "DEBUG",
                "handlers": ["console"],
                "propagate": False,
            }
        },
    })


def main():
    setup_logging()

    crawler = Crawler()
    crawler.crawl("https://example.com")
```

---

# 27. Flow cuối cùng

```text
                    main()
                      │
                      ▼
                setup_logging()
                      │
                      ▼
                 dictConfig()
                      │
                      ▼
             ┌──────────────────┐
             │ Application      │
             │ Logging Policy   │
             └────────┬─────────┘
                      │
                      ▼
              storycrawler
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       crawler      parser     database
          │           │           │
          └───────────┼───────────┘
                      ▼
                  LogRecord
                      │
                      ▼
                  Handler
                      │
                      ▼
                   Output
```

---

# 28. Library Logging Contract

Khi bạn viết một Python package, hãy coi đây là **contract**:

### Library SHOULD

```python
logger = logging.getLogger(__name__)
```

```python
logger.debug(...)
logger.info(...)
logger.warning(...)
logger.error(...)
logger.exception(...)
```

Có thể cung cấp:

```python
NullHandler
```

### Library SHOULD NOT

```python
logging.basicConfig(...)
```

```python
dictConfig(...)
```

```python
FileHandler(...)
```

```python
StreamHandler(...)
```

với mục đích ép application phải dùng cấu hình của library.

---

# 29. Application Logging Contract

Application thì ngược lại.

Application SHOULD:

```python
logging.config.dictConfig(...)
```

Application quyết định:

```text
✔ Log level
✔ Handler
✔ Formatter
✔ File path
✔ Rotation
✔ Console
✔ JSON
✔ Environment
✔ Third-party logging
✔ Security policy
```

---

# 30. Mental Model cuối Buổi 9

Hãy nhớ 3 tầng:

```text
┌─────────────────────────────┐
│          LIBRARY            │
│                             │
│ logging.getLogger(__name__) │
│ logger.info(...)            │
│ logger.error(...)           │
│                             │
│        NullHandler          │
└──────────────┬──────────────┘
               │
               │ propagate
               ▼
┌─────────────────────────────┐
│        APPLICATION          │
│                             │
│       dictConfig()          │
│                             │
│   Logger / Handler /        │
│   Formatter / Filter        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│           OUTPUT            │
│                             │
│ Console / File / Queue /    │
│ JSON / External system      │
└─────────────────────────────┘
```

### Một câu cần nhớ:

> **Library tạo log; Application cấu hình log.**

---

# Bài tập Buổi 9

Hãy tự thiết kế:

```text
storycrawler/
│
├── __init__.py
├── crawler.py
├── parser.py
└── repository.py
```

và:

```text
myapp/
│
├── main.py
└── logging_config.py
```

Yêu cầu:

```text
Library:
    ├── getLogger(__name__)
    ├── NullHandler
    ├── không basicConfig()
    ├── không FileHandler
    └── không dictConfig()

Application:
    ├── dictConfig()
    ├── Console INFO+
    ├── app.log DEBUG+
    └── error.log ERROR+
```

Sau đó thử cố tình đặt:

```python
propagate=False
```

ở `storycrawler` và quan sát sự khác biệt.

---

## Buổi 10 — `LogRecord` Deep Dive

Buổi tiếp theo sẽ đi xuống **bên trong Logging**:

```text
logger.info("Downloaded %s", chapter)
                 │
                 ▼
             LogRecord
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
      name    levelno   message
        │
        ├── pathname
        ├── lineno
        ├── funcName
        ├── process
        ├── thread
        ├── exc_info
        └── extra
```

Ta sẽ **tự inspect `LogRecord`**, hiểu nó được tạo như thế nào, `msg` khác `message` ra sao, `args`, `extra`, `stacklevel`, `exc_info`, và sau đó dùng kiến thức này để tiến tới **custom logging / contextual logging**.
