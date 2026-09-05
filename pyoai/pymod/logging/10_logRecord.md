# Buổi 10 — `LogRecord` Deep Dive

Đây là một buổi **rất quan trọng** trong Logging Deep Dive.

Nếu ở các buổi trước ta học:

```text
Logger
   ↓
Handler
   ↓
Formatter
   ↓
Output
```

thì hôm nay ta đi vào **đối tượng nằm giữa Logger và Handler**:

```text
logger.info(...)
      │
      ▼
 ┌─────────────┐
 │  LogRecord  │
 └─────────────┘
      │
      ├── name
      ├── level
      ├── message
      ├── pathname
      ├── lineno
      ├── funcName
      ├── process
      ├── thread
      ├── exc_info
      └── extra
      │
      ▼
   Handler
```

---

# 1. `LogRecord` là gì?

`LogRecord` là **object chứa toàn bộ thông tin của một log event**.

Ví dụ:

```python
logger.info("Downloaded chapter %s", 10)
```

Python không đơn giản tạo ra một string:

```text
Downloaded chapter 10
```

Thay vào đó, nó tạo một `LogRecord` gần giống:

```python
LogRecord(
    name="storycrawler.crawler",
    levelno=20,
    levelname="INFO",
    msg="Downloaded chapter %s",
    args=(10,),
    ...
)
```

Sau đó:

```text
Logger
   │
   │ tạo LogRecord
   ▼
LogRecord
   │
   ▼
Handler
   │
   ▼
Formatter
   │
   ▼
"2026-09-05 16:00:00 | INFO | storycrawler.crawler | Downloaded chapter 10"
```

---

# 2. Tạo `LogRecord` thực tế

Ta có thể tự tạo một handler để quan sát record.

```python
import logging


class DebugHandler(logging.Handler):

    def emit(self, record):
        print("name:", record.name)
        print("levelno:", record.levelno)
        print("levelname:", record.levelname)
        print("msg:", record.msg)
        print("args:", record.args)
        print("message:", record.getMessage())
        print("pathname:", record.pathname)
        print("filename:", record.filename)
        print("module:", record.module)
        print("lineno:", record.lineno)
        print("funcName:", record.funcName)
        print()
```

Sử dụng:

```python
logger = logging.getLogger("storycrawler")
logger.setLevel(logging.DEBUG)

logger.addHandler(DebugHandler())

logger.info("Downloaded chapter %s", 10)
```

Có thể nhận được:

```text
name: storycrawler
levelno: 20
levelname: INFO

msg: Downloaded chapter %s
args: (10,)
message: Downloaded chapter 10

pathname: C:\project\crawler.py
filename: crawler.py
module: crawler
lineno: 15
funcName: download_chapter
```

---

# 3. `msg` khác `message`

Đây là điểm cực kỳ quan trọng.

Khi viết:

```python
logger.info("Downloaded chapter %s", 10)
```

`LogRecord` sẽ chứa:

```python
record.msg
```

là:

```text
Downloaded chapter %s
```

và:

```python
record.args
```

là:

```python
(10,)
```

Trong khi:

```python
record.getMessage()
```

cho:

```text
Downloaded chapter 10
```

---

# 4. Vì sao Python không format ngay?

Đây là một trong những lý do logging sử dụng:

```python
logger.info("Downloaded chapter %s", chapter_id)
```

thay vì:

```python
logger.info(f"Downloaded chapter {chapter_id}")
```

Logging giữ:

```text
msg = "Downloaded chapter %s"
args = (chapter_id,)
```

cho đến khi cần format.

Ví dụ:

```python
logger.setLevel(logging.WARNING)

logger.debug(
    "Downloaded chapter %s",
    chapter_id,
)
```

Nếu `DEBUG` bị disable, Python không cần tạo/format message theo cách thông thường.

Trong khi:

```python
logger.debug(
    f"Downloaded chapter {chapter_id}"
)
```

thì f-string đã được xử lý trước khi logging quyết định có ghi log hay không.

---

# 5. `record.getMessage()`

Bên trong Formatter, logging sẽ thực hiện tương đương:

```python
record.getMessage()
```

Logic khái quát:

```python
message = str(record.msg)

if record.args:
    message = message % record.args
```

Ví dụ:

```python
record.msg = "User %s downloaded %s"
record.args = ("alice", 10)
```

Kết quả:

```python
record.getMessage()
```

là:

```text
User alice downloaded 10
```

---

# 6. Các field quan trọng của `LogRecord`

Một `LogRecord` có khá nhiều metadata.

## Identity

```python
record.name
```

Ví dụ:

```text
storycrawler.crawler
```

---

## Level

```python
record.levelno
record.levelname
```

Ví dụ:

```text
20
INFO
```

---

## Message

```python
record.msg
record.args
record.getMessage()
```

---

## Source location

```python
record.pathname
record.filename
record.module
record.lineno
record.funcName
```

Ví dụ:

```text
pathname = C:\project\storycrawler\crawler.py
filename = crawler.py
module = crawler
lineno = 42
funcName = download_chapter
```

---

# 7. Process information

Logging cũng có thể chứa thông tin process:

```python
record.process
record.processName
```

Ví dụ:

```text
process = 12480
processName = MainProcess
```

Điều này cực kỳ hữu ích khi sử dụng:

```text
multiprocessing
ProcessPoolExecutor
Celery
worker processes
```

Ví dụ:

```text
INFO | process=12480 | crawler | Download chapter 10
INFO | process=12520 | crawler | Download chapter 11
```

Ta biết chính xác process nào tạo log.

---

# 8. Thread information

Tương tự:

```python
record.thread
record.threadName
```

Ví dụ:

```text
thread = 140735
threadName = ThreadPoolExecutor-0_1
```

Đặc biệt hữu ích với:

```python
ThreadPoolExecutor
```

Ví dụ:

```python
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)


def download(chapter):
    logger.info("Downloading chapter %s", chapter)


with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(download, range(1, 5))
```

Formatter:

```python
"%(asctime)s | %(threadName)s | %(levelname)s | %(message)s"
```

Có thể tạo:

```text
16:20:01 | ThreadPoolExecutor-0_0 | INFO | Downloading chapter 1
16:20:01 | ThreadPoolExecutor-0_1 | INFO | Downloading chapter 2
16:20:01 | ThreadPoolExecutor-0_2 | INFO | Downloading chapter 3
16:20:01 | ThreadPoolExecutor-0_3 | INFO | Downloading chapter 4
```

---

# 9. `created`

```python
record.created
```

Là timestamp khi LogRecord được tạo.

Ví dụ:

```python
print(record.created)
```

Có thể là:

```text
1788592801.123
```

Thường ta không sử dụng trực tiếp mà để Formatter xử lý:

```python
"%(asctime)s"
```

---

# 10. `exc_info`

Đây là field cực kỳ quan trọng khi logging exception.

Ví dụ:

```python
try:
    result = 10 / 0
except Exception:
    logger.exception("Calculation failed")
```

`LogRecord` sẽ chứa thông tin exception trong:

```python
record.exc_info
```

Dạng khái quát:

```text
(
    exception_type,
    exception_value,
    traceback
)
```

Ví dụ:

```text
<class 'ZeroDivisionError'>
division by zero
<traceback object>
```

Formatter sau đó có thể sử dụng thông tin này để in traceback.

---

# 11. `stack_info`

Có một khái niệm khác:

```python
stack_info=True
```

Ví dụ:

```python
logger.info(
    "Starting crawler",
    stack_info=True,
)
```

Khi đó logging có thể ghi **call stack hiện tại**.

Điểm cần phân biệt:

```text
exc_info
    ↓
Thông tin exception + traceback

stack_info
    ↓
Call stack hiện tại
```

Ví dụ:

```text
main()
  ↓
run()
  ↓
crawl()
  ↓
download()
```

`stack_info=True` giúp ta nhìn được đường gọi hiện tại ngay cả khi **không có exception**.

---

# 12. `extra` — thêm dữ liệu vào `LogRecord`

Đây là một tính năng cực kỳ quan trọng.

Ví dụ:

```python
logger.info(
    "Chapter downloaded",
    extra={
        "chapter_id": 123,
        "story_id": 456,
    },
)
```

Logging sẽ đưa thêm:

```python
record.chapter_id
record.story_id
```

Ta có thể truy cập:

```python
class DebugHandler(logging.Handler):

    def emit(self, record):
        print("message:", record.getMessage())
        print("chapter_id:", record.chapter_id)
        print("story_id:", record.story_id)
```

Kết quả:

```text
message: Chapter downloaded
chapter_id: 123
story_id: 456
```

---

# 13. `extra` cực kỳ hữu ích cho production

Thay vì:

```python
logger.info(
    f"Downloaded story={story_id} chapter={chapter_id}"
)
```

ta có thể:

```python
logger.info(
    "Chapter downloaded",
    extra={
        "story_id": story_id,
        "chapter_id": chapter_id,
    },
)
```

Bây giờ dữ liệu log được tách thành:

```text
message
    Chapter downloaded

metadata
    story_id = 100
    chapter_id = 25
```

Đây chính là nền tảng của:

```text
Structured Logging
Contextual Logging
JSON Logging
Correlation ID
Observability
```

mà chúng ta sẽ học ở các buổi sau.

---

# 14. Một vấn đề quan trọng với `extra`

Nếu Formatter yêu cầu:

```python
"%(story_id)s"
```

nhưng log không truyền:

```python
extra={"story_id": ...}
```

sẽ xảy ra lỗi formatting.

Ví dụ:

```python
formatter = logging.Formatter(
    "%(levelname)s | story=%(story_id)s | %(message)s"
)
```

Nhưng:

```python
logger.info("Hello")
```

không có:

```python
story_id
```

→ Formatter không thể lấy field đó.

Do đó `extra` cần được thiết kế cẩn thận.

---

# 15. `stacklevel` — cực kỳ quan trọng khi viết wrapper

Giả sử ta tạo helper:

```python
def log_info(message):
    logger.info(message)
```

Sau đó:

```python
def download():
    log_info("Downloading chapter")
```

Logging có thể báo:

```text
helper.py:2
```

thay vì:

```text
crawler.py:5
```

Vì logging nhìn thấy caller trực tiếp là:

```python
log_info()
```

---

## `stacklevel`

Ta có thể viết:

```python
def log_info(message):
    logger.info(
        message,
        stacklevel=2,
    )
```

Bây giờ logging bỏ qua một stack frame.

Kết quả:

```text
crawler.py:5
```

thay vì:

```text
helper.py:2
```

---

# 16. Tại sao `stacklevel` quan trọng?

Nó đặc biệt hữu ích khi xây:

```text
Logging helper
Framework
Library
Decorator
Utility function
API wrapper
```

Ví dụ:

```python
def log_debug(message):
    logger.debug(
        message,
        stacklevel=2,
    )
```

Application:

```python
log_debug("Crawler started")
```

Log vẫn trỏ về code của application.

---

# 17. Nhìn toàn bộ lifecycle của `LogRecord`

Bây giờ ta có thể hiểu sâu hơn:

```text
logger.info(
    "Downloaded %s",
    chapter_id
)
        │
        ▼
Logger.isEnabledFor(INFO)
        │
        ▼
Logger.makeRecord(...)
        │
        ▼
┌──────────────────────────────┐
│          LogRecord           │
│                              │
│ name                         │
│ levelno                      │
│ levelname                    │
│ msg                          │
│ args                         │
│ pathname                     │
│ filename                     │
│ lineno                       │
│ funcName                     │
│ process                      │
│ thread                       │
│ exc_info                     │
│ stack_info                   │
│ extra                        │
└──────────────────────────────┘
        │
        ▼
Filter
        │
        ▼
Handler
        │
        ▼
Formatter
        │
        ▼
Output
```

Đây là một trong những mental model quan trọng nhất của Python Logging.

---

# 18. Tự inspect toàn bộ `LogRecord`

Ta có thể viết:

```python
import logging


class InspectHandler(logging.Handler):

    def emit(self, record):
        print(vars(record))


logger = logging.getLogger("demo")
logger.setLevel(logging.DEBUG)

logger.addHandler(InspectHandler())

logger.info(
    "Downloaded chapter %s",
    10,
    extra={
        "story_id": 100,
        "chapter_id": 10,
    },
)
```

`vars(record)` sẽ cho một dictionary kiểu:

```python
{
    'name': 'demo',
    'msg': 'Downloaded chapter %s',
    'args': (10,),
    'levelname': 'INFO',
    'levelno': 20,
    'pathname': '...',
    'filename': '...',
    'module': '...',
    'lineno': 15,
    'funcName': '<module>',
    'created': ...,
    'msecs': ...,
    'relativeCreated': ...,
    'thread': ...,
    'threadName': 'MainThread',
    'processName': 'MainProcess',
    'process': ...,
    'story_id': 100,
    'chapter_id': 10,
}
```

Đây chính là **payload nội bộ của một log event**.

---

# 19. `LogRecord` và Formatter

Formatter không cần biết logger gọi thế nào.

Nó chỉ nhận:

```python
record
```

Ví dụ:

```python
class MyFormatter(logging.Formatter):

    def format(self, record):
        return (
            f"{record.levelname} | "
            f"{record.name} | "
            f"{record.getMessage()}"
        )
```

Sau đó:

```text
INFO | storycrawler.crawler | Downloaded chapter 10
```

---

# 20. Một ví dụ production-style

Giả sử crawler:

```python
def download_chapter(story_id, chapter_id):
    logger.info(
        "Chapter downloaded",
        extra={
            "story_id": story_id,
            "chapter_id": chapter_id,
        },
    )
```

Ta có:

```text
LogRecord
│
├── name = storycrawler.crawler
├── levelname = INFO
├── message = Chapter downloaded
├── story_id = 100
├── chapter_id = 25
├── process = 12000
├── threadName = MainThread
├── filename = crawler.py
├── lineno = 42
└── funcName = download_chapter
```

Formatter có thể biến nó thành:

```text
2026-09-05 16:30:01 |
INFO |
storycrawler.crawler |
story=100 |
chapter=25 |
Chapter downloaded
```

Hoặc JSON:

```json
{
    "level": "INFO",
    "logger": "storycrawler.crawler",
    "message": "Chapter downloaded",
    "story_id": 100,
    "chapter_id": 25
}
```

Và đây chính là cầu nối sang **Structured Logging**.

---

# 21. Một quy tắc quan trọng

Không nên biến tất cả metadata thành message:

❌

```python
logger.info(
    f"Downloaded story={story_id} "
    f"chapter={chapter_id} "
    f"url={url}"
)
```

Tốt hơn:

```python
logger.info(
    "Chapter downloaded",
    extra={
        "story_id": story_id,
        "chapter_id": chapter_id,
        "url": url,
    },
)
```

Vì sau này chúng ta có thể:

```text
LogRecord
    ↓
JSON Formatter
    ↓
ELK / Loki / OpenSearch / Cloud logging
```

và query:

```text
chapter_id = 123
```

thay vì phải parse string.

---

# 22. Một điểm rất quan trọng: `extra` không phải context tự động

Ví dụ:

```python
logger.info(
    "Downloaded",
    extra={"story_id": 100},
)

logger.info(
    "Parsing",
)
```

Log thứ hai **không tự động có**:

```python
story_id
```

`extra` chỉ áp dụng cho **LogRecord hiện tại**.

Muốn metadata tự động xuất hiện trên nhiều log:

```text
story_id
chapter_id
request_id
worker_id
user_id
```

thì chúng ta cần những kỹ thuật như:

```text
LoggerAdapter
Filter
contextvars
LogRecordFactory
```

Đó chính là các chủ đề sắp tới.

---

# 23. Kiến trúc Logging đến thời điểm hiện tại

Ta đã đi từ:

### Buổi 1

```text
Logger
Handler
Formatter
```

### Buổi 2

```text
Logger Hierarchy
propagate
effectiveLevel
```

### Buổi 3

```text
Handler
StreamHandler
FileHandler
```

### Buổi 4

```text
Formatter
LogRecord fields
```

### Buổi 5

```text
basicConfig
```

### Buổi 6

```text
dictConfig
```

### Buổi 7

```text
fileConfig
```

### Buổi 8–9

```text
Library
Application
NullHandler
```

### Buổi 10

Ta đã đi sâu vào:

```text
                 ┌───────────────┐
logger.info(...) │               │
────────────────►│  LogRecord    │
                 │               │
                 │ msg           │
                 │ args          │
                 │ name          │
                 │ level         │
                 │ pathname      │
                 │ lineno        │
                 │ funcName      │
                 │ process       │
                 │ thread        │
                 │ exc_info      │
                 │ stack_info    │
                 │ extra         │
                 └───────┬───────┘
                         │
                         ▼
                      Handler
                         │
                         ▼
                     Formatter
                         │
                         ▼
                       Output
```

---

# 24. Bài tập Buổi 10

## Bài 1 — Inspect `LogRecord`

Tạo:

```python
InspectHandler
```

và in:

```python
record.name
record.levelname
record.msg
record.args
record.getMessage()
record.filename
record.lineno
record.funcName
record.threadName
record.processName
```

---

## Bài 2 — `extra`

Tạo:

```python
logger.info(
    "Chapter downloaded",
    extra={
        "story_id": 100,
        "chapter_id": 25,
    },
)
```

Formatter:

```text
%(levelname)s |
story=%(story_id)s |
chapter=%(chapter_id)s |
%(message)s
```

Kết quả mong muốn:

```text
INFO | story=100 | chapter=25 | Chapter downloaded
```

---

## Bài 3 — `stacklevel`

Tạo:

```python
def log_info(message):
    logger.info(message)
```

Quan sát `filename` và `lineno`.

Sau đó sửa thành:

```python
def log_info(message):
    logger.info(
        message,
        stacklevel=2,
    )
```

Quan sát sự khác biệt.

---

## Bài 4 — Crawler LogRecord

Thiết kế log cho:

```python
download_chapter(
    story_id=100,
    chapter_id=25,
    url="https://example.com/chapter/25",
)
```

Không nhét metadata vào message.

Hãy dùng:

```python
extra={
    ...
}
```

Thiết kế LogRecord sao cho có:

```text
story_id
chapter_id
url
```

và các metadata mặc định:

```text
logger
level
filename
lineno
function
thread
process
```

---

## Bài 5 — Mental Model

Hãy tự giải thích chuỗi sau bằng lời của bạn:

```text
logger.info(...)
       ↓
isEnabledFor()
       ↓
LogRecord
       ↓
Filter
       ↓
Handler
       ↓
Formatter
       ↓
Output
```

Nếu bạn hiểu được chuỗi này thật chắc, thì từ **Buổi 11 — Filter Deep Dive** trở đi sẽ dễ hơn rất nhiều.

**Buổi tiếp theo: Buổi 11 — `Filter` Deep Dive**, nơi chúng ta sẽ học cách **lọc LogRecord theo logger, level, metadata, module, story_id, chapter_id...** và bắt đầu xây logging có context cho crawler.
