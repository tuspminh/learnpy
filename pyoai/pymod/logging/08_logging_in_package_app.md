# Buổi 8 — Logging trong Package / Application

Buổi này rất quan trọng vì từ đây chúng ta chuyển từ:

```text
"Biết dùng logging"
```

sang:

```text
"Biết thiết kế logging cho Python package/application"
```

Đặc biệt cần hiểu một nguyên tắc:

> **Library không nên tự quyết định cách application ghi log.**

---

# 1. Hai thế giới khác nhau

Python code có thể thuộc hai loại:

### Application

Ví dụ:

```text
story_crawler/
├── cli/
├── crawler/
├── database/
├── service/
└── main.py
```

Đây là chương trình mà **bạn điều khiển toàn bộ**.

### Library / Package

Ví dụ bạn viết:

```text
storycrawler/
├── crawler/
├── parser/
└── database/
```

rồi người khác import:

```python
from storycrawler import Crawler
```

Lúc này:

```text
Library
   ↓
Application
```

Library **không nên áp đặt**:

```text
log file ở đâu?
log format thế nào?
INFO hay DEBUG?
ghi console hay file?
```

Application mới là nơi quyết định.

---

# 2. Sai lầm kinh điển của Library

Giả sử bạn viết:

```python
# crawler.py

import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename="crawler.log",
)
```

Sau đó người dùng:

```python
from storycrawler import Crawler
```

Ngay khi import:

```text
storycrawler
    ↓
basicConfig()
    ↓
application logging bị thay đổi
```

Đây là **design không tốt**.

Library không nên tự gọi:

```python
logging.basicConfig()
```

---

# 3. Vì sao?

Application có thể đã cấu hình:

```text
Console
    INFO+

app.log
    DEBUG+

error.log
    ERROR+
```

Nhưng library tự chạy:

```python
logging.basicConfig(
    filename="crawler.log",
    level=logging.DEBUG,
)
```

thì library đang can thiệp vào toàn bộ logging system.

Đặc biệt nguy hiểm nếu có nhiều package:

```text
Application
 │
 ├── httpx
 ├── database package
 ├── crawler package
 ├── parser package
 └── your package
```

Mỗi package tự cấu hình logging:

```text
💥 logging chaos
```

---

# 4. Nguyên tắc vàng

Library:

```text
Create Logger
     ↓
Emit Log
     ↓
STOP
```

Application:

```text
Configure Logging
     ↓
Handlers
     ↓
Formatters
     ↓
Output
```

Có thể nhớ:

```text
Library = "Tôi phát log"

Application = "Tôi quyết định log đi đâu"
```

---

# 5. Logger trong Package

Giả sử package:

```text
storycrawler/
│
├── __init__.py
├── crawler.py
├── parser.py
└── database.py
```

Trong `crawler.py`:

```python
import logging

logger = logging.getLogger(__name__)
```

Nếu module được import như:

```python
import storycrawler.crawler
```

thì:

```python
__name__
```

là:

```text
storycrawler.crawler
```

Logger:

```text
storycrawler.crawler
```

---

# 6. Logger hierarchy

Ta có:

```text
root
 │
 └── storycrawler
      │
      ├── crawler
      ├── parser
      └── database
```

Tương ứng:

```python
logging.getLogger("storycrawler")
```

```python
logging.getLogger("storycrawler.crawler")
```

```python
logging.getLogger("storycrawler.parser")
```

```python
logging.getLogger("storycrawler.database")
```

Đây là một trong những lý do nên dùng:

```python
logging.getLogger(__name__)
```

thay vì:

```python
logging.getLogger("app")
```

---

# 7. Package Logger

Ta có thể tạo:

```python
# storycrawler/__init__.py

import logging

logger = logging.getLogger(__name__)
```

Logger này là:

```text
storycrawler
```

Các module:

```text
storycrawler.crawler
storycrawler.parser
storycrawler.database
```

đều là children.

---

# 8. `NullHandler`

Đây là một khái niệm rất quan trọng khi viết **library**.

Python cung cấp:

```python
logging.NullHandler
```

Ví dụ:

```python
# storycrawler/__init__.py

import logging

logger = logging.getLogger(__name__)

logger.addHandler(logging.NullHandler())
```

Ý nghĩa:

```text
Library
   │
   ▼
NullHandler
   │
   └── không xuất log ra đâu cả
```

Library có thể phát log:

```python
logger.info("Crawler started")
```

nhưng nếu application chưa cấu hình logging thì library không tự ý tạo output.

---

# 9. Tại sao `NullHandler` hữu ích?

Giả sử người dùng:

```python
from storycrawler import Crawler

crawler = Crawler()
crawler.run()
```

Application không cấu hình logging.

Library vẫn có:

```python
logger.info(...)
```

Nhưng:

```text
Không có:
    app.log
    console
    error.log
```

Library không tự ý tạo file:

```text
crawler.log
```

Đây là behavior tốt.

---

# 10. Pattern chuẩn của Library

Một package có thể:

```python
# storycrawler/__init__.py

import logging

logging.getLogger(__name__).addHandler(
    logging.NullHandler()
)
```

Các module:

```python
# storycrawler/crawler.py

import logging

logger = logging.getLogger(__name__)


class Crawler:

    def crawl(self):
        logger.debug("Start crawling")
```

Không có:

```python
basicConfig()
```

Không có:

```python
FileHandler()
```

Không có:

```python
StreamHandler()
```

trong library.

---

# 11. `NullHandler` không có nghĩa là "tắt logging"

Đây là chỗ dễ hiểu nhầm.

```python
logger.addHandler(logging.NullHandler())
```

không có nghĩa:

```text
logger.disabled = True
```

Library vẫn tạo:

```python
logger.debug(...)
logger.info(...)
logger.warning(...)
logger.error(...)
```

Chỉ là nếu application chưa cung cấp logging configuration phù hợp thì `NullHandler` sẽ "ăn" record mà không xuất ra đâu.

---

# 12. Application sử dụng Library

Application:

```python
import logging.config

logging.config.dictConfig(LOGGING)
```

Sau đó:

```python
from storycrawler import Crawler

crawler = Crawler()
crawler.run()
```

Flow:

```text
                    Application
                         │
                  dictConfig()
                         │
                         ▼
                    root logger
                         │
                         ▼
                  storycrawler
                         │
               ┌─────────┼─────────┐
               ▼         ▼         ▼
            crawler    parser   database
```

Library không cần biết configuration nằm ở đâu.

---

# 13. `propagate` và Library

Giả sử:

```python
logger = logging.getLogger(
    "storycrawler.crawler"
)
```

và:

```python
logger.propagate = True
```

Record sẽ đi lên:

```text
storycrawler.crawler
        │
        ▼
storycrawler
        │
        ▼
root
        │
        ▼
handlers
```

Thông thường library nên để:

```python
propagate = True
```

để application có thể kiểm soát output.

---

# 14. Không nên làm điều này trong Library

❌:

```python
logger.propagate = False
```

rồi tự:

```python
handler = logging.FileHandler("crawler.log")
logger.addHandler(handler)
```

Kết quả:

```text
Application
    │
    X
storycrawler
    │
    ▼
crawler.log
```

Application không còn kiểm soát được log của library.

---

# 15. Khi nào Library có thể thêm Handler?

Trong phần lớn trường hợp:

> **Không cần.**

Exception điển hình là:

```python
NullHandler
```

cho library.

Architecture tốt:

```text
Library
   │
   └── Logger
         │
         │ propagate
         ▼
Application
   │
   ├── ConsoleHandler
   ├── FileHandler
   └── QueueHandler
```

---

# 16. Application nên cấu hình Logger Package

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

Khi đó:

```text
storycrawler
      │
      ├── crawler
      ├── parser
      └── database
```

đều chịu ảnh hưởng của:

```text
storycrawler
    DEBUG
```

---

# 17. Một điểm rất hay của hierarchy

Bạn có:

```text
storycrawler
│
├── crawler
├── parser
└── database
```

Muốn debug toàn bộ:

```python
"storycrawler": {
    "level": "DEBUG",
}
```

Muốn database chỉ INFO:

```python
"storycrawler.database": {
    "level": "INFO",
}
```

Architecture:

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

Đây là sức mạnh rất lớn của logger hierarchy.

---

# 18. Library nên log ở level nào?

Không nên tùy tiện dùng:

```python
logger.error()
```

cho mọi thứ.

Ví dụ crawler:

### DEBUG

```python
logger.debug(
    "Downloading URL %s",
    url,
)
```

### INFO

```python
logger.info(
    "Chapter %s downloaded",
    chapter_id,
)
```

### WARNING

```python
logger.warning(
    "Retrying URL %s",
    url,
)
```

### ERROR

```python
logger.error(
    "Failed to save chapter %s",
    chapter_id,
)
```

### Exception

```python
logger.exception(
    "Unexpected crawler failure"
)
```

---

# 19. Library không nên log quá nhiều

Sai:

```python
for character in text:
    logger.debug(character)
```

Nếu file có:

```text
1 MB
```

thì logging sẽ cực kỳ nhiều.

Nên log ở mức operation:

```python
logger.debug(
    "Parsing chapter %s",
    chapter_id,
)
```

Mental model:

```text
❌ Log every operation detail

✅ Log useful diagnostic information
```

---

# 20. Không log secret

Đặc biệt quan trọng với package/API client.

❌:

```python
logger.debug(
    "Request headers=%s",
    headers,
)
```

nếu `headers` có:

```text
Authorization
Cookie
API-Key
```

Không nên:

```python
logger.info(
    "Login user=%s password=%s",
    username,
    password,
)
```

Thay vào đó:

```python
logger.info(
    "Login successful for user=%s",
    username,
)
```

Và với token:

```text
Authorization: Bearer eyJ...
```

không được xuất thẳng vào log.

Phần Security Logging chúng ta sẽ học sâu hơn ở Buổi 42.

---

# 21. Application vs Library

|                                    | Library  | Application      |
| ---------------------------------- | -------- | ---------------- |
| `getLogger()`                      | ✅        | ✅                |
| `basicConfig()`                    | ❌        | Có thể           |
| `dictConfig()`                     | ❌        | ✅                |
| `FileHandler`                      | Thường ❌ | ✅                |
| `StreamHandler`                    | Thường ❌ | ✅                |
| `NullHandler`                      | ✅        | Thường không cần |
| quyết định output                  | ❌        | ✅                |
| quyết định format                  | ❌        | ✅                |
| quyết định log level toàn hệ thống | ❌        | ✅                |

---

# 22. Ví dụ thực tế: `storycrawler`

Giả sử package:

```text
storycrawler/
│
├── __init__.py
│
├── crawler/
│   ├── __init__.py
│   ├── http.py
│   └── crawler.py
│
├── parser/
│   └── parser.py
│
└── database/
    └── repository.py
```

Trong:

```python
# crawler.py

import logging

logger = logging.getLogger(__name__)


class Crawler:

    def crawl(self, url):
        logger.info("Start crawling %s", url)

        try:
            ...
        except Exception:
            logger.exception(
                "Crawler failed: %s",
                url,
            )
            raise
```

Không cần biết:

```text
log file
formatter
handler
console
JSON
rotation
```

---

# 23. Application

```text
myapp/
│
├── main.py
│
├── config/
│   └── logging.py
│
└── logs/
    ├── app.log
    └── error.log
```

`main.py`:

```python
from config.logging import setup_logging
from storycrawler import Crawler


def main():
    setup_logging()

    crawler = Crawler()
    crawler.run()


if __name__ == "__main__":
    main()
```

Đây là separation rất sạch:

```text
storycrawler
    = library

myapp
    = application
```

---

# 24. Logging trong Clean Architecture

Liên hệ trực tiếp với kiến trúc bạn đã học:

```text
┌─────────────────────────────┐
│       Presentation          │
├─────────────────────────────┤
│       Application           │
├─────────────────────────────┤
│          Domain             │
├─────────────────────────────┤
│       Infrastructure        │
└─────────────────────────────┘
```

Logging configuration:

```text
Infrastructure / Application startup
                │
                ▼
          dictConfig()
```

Business code:

```python
logger.info(...)
```

Không cần biết:

```text
FileHandler
RotatingFileHandler
QueueHandler
JSONFormatter
```

---

# 25. Một architecture production

Với crawler của bạn, có thể thiết kế:

```text
                         Application
                              │
                       setup_logging()
                              │
                              ▼
                       Python Logging
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   storycrawler            database              worker
        │                     │                     │
        ▼                     ▼                     ▼
     Logger                Logger                Logger
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                         Log Handlers
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
                 Console   app.log   error.log
```

Sau này khi học `QueueHandler`:

```text
Logger
   │
   ▼
QueueHandler
   │
   ▼
Queue
   │
   ▼
QueueListener
   │
   ├── FileHandler
   ├── ConsoleHandler
   └── ...
```

Đây sẽ là kiến trúc phù hợp cho crawler + worker + thread/process/asyncio.

---

# 26. Một quy tắc cực kỳ đáng nhớ

Khi viết Python package:

### Được

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Something happened")
```

### Có thể

```python
logger.addHandler(logging.NullHandler())
```

### Không nên

```python
logging.basicConfig(...)
```

### Không nên

```python
FileHandler(...)
```

### Không nên

```python
StreamHandler(...)
```

### Không nên

```python
logger.handlers.clear()
```

### Không nên

```python
logger.propagate = False
```

chỉ để ép application sử dụng cách logging của library.

---

# 27. Mental Model Buổi 8

Hãy nhớ mô hình này:

```text
                LIBRARY
                   │
                   ▼
          logging.getLogger()
                   │
                   ▼
             Logger API
                   │
                   │ propagate
                   ▼
              APPLICATION
                   │
             dictConfig()
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
     Console      File      Error
```

**Library phát log.**

**Application quản lý log.**

Đây là nguyên tắc quan trọng nhất của Buổi 8.

---

# Bài tập

Tạo package:

```text
storycrawler/
├── __init__.py
├── crawler.py
├── parser.py
└── database.py
```

và application:

```text
myapp/
├── main.py
├── logging_config.py
└── logs/
```

Yêu cầu:

1. Mọi module trong `storycrawler` dùng:

```python
logger = logging.getLogger(__name__)
```

2. `storycrawler` **không được** gọi `basicConfig()`.

3. `storycrawler` **không được** tạo `FileHandler`.

4. Package có `NullHandler`.

5. Application dùng `dictConfig()`.

6. Console nhận `INFO+`.

7. `app.log` nhận `DEBUG+`.

8. `error.log` nhận `ERROR+`.

9. Có thể cấu hình riêng:

```text
storycrawler.crawler  → DEBUG
storycrawler.parser   → DEBUG
storycrawler.database → INFO
```

10. Kiểm tra xem `propagate=True` hoạt động như thế nào.

---

## Tiếp theo — Buổi 9

**Library Logging vs Application Logging — Deep Dive**

Ta sẽ đi sâu hơn vào:

```text
NullHandler
     ↓
propagate
     ↓
package logger
     ↓
third-party logger
     ↓
root logger
     ↓
disable_existing_loggers
```

và xây một **Python package có logging đúng chuẩn**, sau đó mới chuyển sang **Buổi 10 — `LogRecord` Deep Dive**.
