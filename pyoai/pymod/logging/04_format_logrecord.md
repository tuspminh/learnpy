# 🐍 Logging Deep Dive — Buổi 4

# Formatter + LogRecord Deep Dive

Buổi này rất quan trọng vì chúng ta sẽ đi xuống **bên trong một log event**.

Sau buổi này bạn sẽ hiểu:

```text
logger.info("Hello")
       │
       ▼
   LogRecord
       │
       ▼
   Formatter
       │
       ▼
"2026-09-05 08:20:15 | INFO | app.crawler | Hello"
```

Đặc biệt, chúng ta sẽ hiểu **`LogRecord` chứa gì** và cách tận dụng nó để tạo log production.

---

# 1. Formatter là gì?

Ở Buổi 3:

```text
Handler
   │
   ▼
Formatter
   │
   ▼
Output
```

`Formatter` chịu trách nhiệm biến `LogRecord` thành chuỗi text.

Ví dụ:

```python
import logging

formatter = logging.Formatter(
    "%(levelname)s | %(message)s"
)
```

Khi:

```python
logger.info("Crawler started")
```

output:

```text
INFO | Crawler started
```

Formatter **không tạo log**.

Nó chỉ quyết định:

> LogRecord sẽ được biểu diễn như thế nào.

---

# 2. LogRecord là trái tim của Logging

Khi bạn viết:

```python
logger.info("Crawler started")
```

Python không lập tức tạo:

```text
INFO | Crawler started
```

Mà tạo một object:

```text
LogRecord
```

Conceptually:

```text
LogRecord
├── name
├── levelno
├── levelname
├── pathname
├── filename
├── module
├── lineno
├── funcName
├── created
├── msecs
├── process
├── thread
├── message
└── ...
```

Formatter lấy các field này để tạo output.

---

# 3. `%(message)s`

Đây là field cơ bản nhất.

```python
formatter = logging.Formatter(
    "%(message)s"
)
```

Code:

```python
logger.info("Crawler started")
```

Output:

```text
Crawler started
```

Nếu:

```python
logger.error("Database connection failed")
```

output:

```text
Database connection failed
```

---

# 4. `%(levelname)s`

Tên level:

```python
"%(levelname)s"
```

Ví dụ:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

Formatter:

```python
formatter = logging.Formatter(
    "%(levelname)s | %(message)s"
)
```

Output:

```text
INFO | Crawler started
```

---

# 5. `%(levelno)d`

Đây là numeric level:

```text
DEBUG      10
INFO       20
WARNING    30
ERROR      40
CRITICAL   50
```

Ví dụ:

```python
"%(levelno)d"
```

output:

```text
20
```

Thông thường production log không cần field này, nhưng nó rất hữu ích khi debugging logging configuration.

---

# 6. `%(name)s`

Tên Logger.

Nếu:

```python
logger = logging.getLogger("app.crawler.parser")
```

thì:

```python
"%(name)s"
```

sẽ cho:

```text
app.crawler.parser
```

Ví dụ:

```python
formatter = logging.Formatter(
    "%(levelname)s | %(name)s | %(message)s"
)
```

Output:

```text
INFO | app.crawler.parser | Parsing chapter
```

Đây là một trong những field **rất nên có**.

---

# 7. `%(asctime)s`

Thời gian log.

```python
"%(asctime)s"
```

Ví dụ:

```text
2026-09-05 08:30:12,123
```

Formatter:

```python
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)
```

Output:

```text
2026-09-05 08:30:12,123 | INFO | Crawler started
```

---

# 8. Tùy chỉnh time format

Bạn có thể:

```python
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
```

Output:

```text
2026-09-05 08:30:12 | INFO | Crawler started
```

Không còn milliseconds.

---

# 9. `created`

`LogRecord` có:

```python
record.created
```

Đây là timestamp dạng Unix time.

Ví dụ conceptually:

```text
1788586212.123
```

Nó là số giây kể từ Unix epoch.

`asctime` được Formatter tạo ra dựa trên timestamp này.

---

# 10. `msecs`

`msecs` là milliseconds.

Ví dụ:

```text
123
```

Nếu:

```text
created = ...12.123
```

thì:

```text
msecs = 123
```

Bạn thường không cần truy cập trực tiếp, vì:

```python
%(asctime)s
```

đã có thể hiển thị phần milliseconds tùy format.

---

# 11. `relativeCreated`

Field này khá thú vị:

```python
%(relativeCreated)f
```

Nó biểu diễn thời gian tính từ khi logging module được load.

Ví dụ:

```text
1234.567
```

nghĩa khoảng 1234 ms kể từ lúc logging được khởi tạo.

Field này hữu ích khi debugging startup/performance.

---

# 12. `pathname`

Ví dụ file:

```text
/home/user/project/app/crawler/parser.py
```

Field:

```python
"%(pathname)s"
```

cho full path.

Ví dụ:

```text
/home/user/project/app/crawler/parser.py
```

---

# 13. `filename`

Khác với `pathname`.

```python
"%(filename)s"
```

chỉ lấy filename:

```text
parser.py
```

So sánh:

```text
pathname
/home/user/project/app/crawler/parser.py

filename
parser.py
```

---

# 14. `module`

Thông thường:

```text
parser
```

không có `.py`.

Ví dụ:

```python
"%(module)s"
```

→

```text
parser
```

---

# 15. `lineno`

Field rất hữu ích khi debugging:

```python
"%(lineno)d"
```

Ví dụ:

```text
INFO | parser.py:42 | Parsing chapter
```

Nó cho biết log được gọi tại dòng nào.

---

# 16. `funcName`

Tên function tạo log.

Ví dụ:

```python
def parse_chapter():
    logger.info("Parsing chapter")
```

Formatter:

```python
"%(funcName)s"
```

Output:

```text
parse_chapter
```

Có thể kết hợp:

```python
formatter = logging.Formatter(
    "%(levelname)s | %(filename)s:%(lineno)d | "
    "%(funcName)s | %(message)s"
)
```

Output:

```text
INFO | parser.py:42 | parse_chapter | Parsing chapter
```

Đây là format cực hữu ích khi development.

---

# 17. Process information

`LogRecord` còn chứa:

```python
%(process)d
```

PID của process.

Ví dụ:

```text
12345
```

Ngoài ra:

```python
%(processName)s
```

Ví dụ:

```text
MainProcess
```

Điều này đặc biệt hữu ích khi sử dụng:

```text
multiprocessing
ProcessPoolExecutor
Celery
worker processes
```

---

# 18. Thread information

Có:

```python
%(thread)d
```

thread ID.

Và:

```python
%(threadName)s
```

thread name.

Ví dụ:

```text
MainThread
```

Trong `ThreadPoolExecutor`, bạn có thể thấy:

```text
ThreadPoolExecutor-0_0
ThreadPoolExecutor-0_1
ThreadPoolExecutor-0_2
```

Rất hữu ích khi debug concurrent application.

---

# 19. Một formatter rất đầy đủ

```python
formatter = logging.Formatter(
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(filename)s:%(lineno)d | "
    "%(funcName)s | "
    "%(process)d | "
    "%(threadName)s | "
    "%(message)s"
)
```

Output có thể:

```text
2026-09-05 08:40:12,123 | INFO | app.crawler.parser |
parser.py:42 | parse_chapter | 12345 | MainThread |
Parsing chapter
```

Rất nhiều thông tin.

Nhưng...

**Không phải cứ nhiều field là tốt.**

---

# 20. Production formatter nên cân bằng

Một format tôi khuyên dùng cho application:

```python
"%(asctime)s | %(levelname)s | %(name)s | %(message)s"
```

Ví dụ:

```text
2026-09-05 08:40:12 | INFO | app.crawler | Crawler started
```

Khi cần debugging sâu:

```python
"%(asctime)s | %(levelname)s | "
"%(name)s | %(filename)s:%(lineno)d | "
"%(funcName)s | %(message)s"
```

---

# 21. `message` vs `msg`

Đây là một điểm rất đáng chú ý.

Khi bạn:

```python
logger.info("Hello %s", name)
```

`LogRecord` ban đầu có:

```text
msg
args
```

Formatter sau đó tạo:

```text
message
```

từ:

```text
msg + args
```

Ví dụ:

```python
logger.info("User %s logged in", username)
```

Conceptually:

```text
msg  = "User %s logged in"
args = ("alice",)
```

Sau formatting:

```text
message = "User alice logged in"
```

---

# 22. Vì sao nên dùng lazy formatting?

Nên:

```python
logger.debug(
    "Processing chapter %s",
    chapter_id,
)
```

thay vì:

```python
logger.debug(
    f"Processing chapter {chapter_id}"
)
```

Lý do quan trọng:

Nếu DEBUG bị disable:

```text
Logger level = INFO
```

thì logging có thể tránh thực hiện một số công việc formatting không cần thiết.

Ví dụ:

```python
logger.debug(
    "Processing chapter %s",
    expensive_object,
)
```

Logging giữ:

```text
msg
args
```

và chỉ interpolate khi cần.

Đây là một thói quen tốt trong code production.

---

# 23. `exc_info`

Khi có exception:

```python
try:
    ...
except Exception:
    logger.exception("Request failed")
```

LogRecord sẽ chứa thông tin exception.

Các field liên quan:

```text
exc_info
exc_text
stack_info
```

Formatter có thể output traceback.

Ví dụ:

```text
ERROR | app.database | Database failed
Traceback (most recent call last):
    ...
ValueError: invalid data
```

Chúng ta sẽ dành riêng một buổi cho exception logging.

---

# 24. `stack_info`

Bạn cũng có:

```python
logger.info(
    "Something happened",
    stack_info=True,
)
```

Điều này yêu cầu logging lấy stack hiện tại và đưa vào record.

Khác với `exc_info`.

### `exc_info`

```text
Có exception
     ↓
ghi traceback
```

### `stack_info`

```text
Không nhất thiết có exception
     ↓
ghi current stack
```

---

# 25. `stacklevel`

Đây là một tính năng cực kỳ hữu ích khi xây **library/framework**.

Giả sử:

```python
def log_info(message):
    logger.info(message)
```

Bạn gọi:

```python
log_info("Hello")
```

Nếu không làm gì thêm, logging có thể báo:

```text
filename: logging_helper.py
```

thay vì nơi thực sự gọi:

```text
main.py
```

Có thể dùng:

```python
logger.info(
    message,
    stacklevel=2,
)
```

Khi đó logging sẽ nhìn lên caller.

Điều này cực kỳ hữu ích khi bạn xây abstraction trên logging.

---

# 26. Formatter có thể dùng `style`

Mặc định:

```python
logging.Formatter(
    "%(levelname)s | %(message)s"
)
```

sử dụng `%`.

Có thể dùng `{}`:

```python
logging.Formatter(
    "{levelname} | {message}",
    style="{",
)
```

Hoặc `$`:

```python
logging.Formatter(
    "$levelname | $message",
    style="$",
)
```

Thông thường `%` vẫn là style phổ biến nhất trong Python logging.

---

# 27. `formatException`

Formatter có thể tùy chỉnh cách exception được format.

Ví dụ:

```python
class MyFormatter(logging.Formatter):

    def formatException(self, ei):
        return "CUSTOM TRACEBACK"
```

Đây là bước đầu để xây custom logging system.

---

# 28. `formatTime`

Bạn cũng có thể custom timestamp:

```python
class MyFormatter(logging.Formatter):

    def formatTime(self, record, datefmt=None):
        ...
```

Điều này hữu ích khi cần:

```text
UTC
ISO 8601
custom timezone
custom timestamp format
```

---

# 29. Tự quan sát `LogRecord`

Đây là bài thực hành rất quan trọng.

Ta tạo Handler đặc biệt:

```python
import logging


class InspectHandler(logging.Handler):

    def emit(self, record):
        print("name:", record.name)
        print("level:", record.levelname)
        print("message:", record.getMessage())
        print("filename:", record.filename)
        print("lineno:", record.lineno)
        print("function:", record.funcName)
        print("process:", record.process)
        print("thread:", record.thread)
```

Sau đó:

```python
logger = logging.getLogger("app.crawler")

logger.setLevel(logging.DEBUG)

logger.addHandler(InspectHandler())

logger.info("Crawler started")
```

Bạn sẽ thấy đại loại:

```text
name: app.crawler
level: INFO
message: Crawler started
filename: main.py
lineno: 23
function: <module>
process: 12345
thread: 123456
```

Đây chính là **LogRecord thật**.

---

# 30. `record.getMessage()`

Nếu:

```python
logger.info(
    "Chapter %s completed",
    chapter_id,
)
```

thì trong Handler:

```python
record.msg
```

có thể là:

```text
Chapter %s completed
```

và:

```python
record.args
```

chứa:

```text
(chapter_id,)
```

Nhưng:

```python
record.getMessage()
```

trả về:

```text
Chapter 123 completed
```

Đây là cách đúng để lấy message đã interpolate từ LogRecord.

---

# 31. Một custom Formatter đơn giản

Bây giờ ta tự tạo:

```python
class SimpleFormatter(logging.Formatter):

    def format(self, record):
        return (
            f"{record.levelname} | "
            f"{record.name} | "
            f"{record.getMessage()}"
        )
```

Sau đó:

```python
handler = logging.StreamHandler()
handler.setFormatter(SimpleFormatter())
```

Output:

```text
INFO | app.crawler | Crawler started
```

Chúng ta vừa tự xây một Formatter.

---

# 32. Nhưng không nên tự format mọi thứ bằng f-string

Không nên:

```python
class Formatter(logging.Formatter):

    def format(self, record):
        return f"{record.levelname}..."
```

nếu bạn chỉ cần custom nhẹ.

Python đã cung cấp:

```python
logging.Formatter(...)
```

Nên dùng built-in formatter khi có thể.

Custom Formatter chỉ nên xuất hiện khi bạn thực sự cần behavior riêng.

---

# 33. Formatter cho crawler production

Với project crawler của bạn, tôi đề xuất ban đầu:

```python
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | "
    "%(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
```

Ví dụ:

```text
2026-09-05 08:45:01 | INFO | app.crawler | Start crawling
2026-09-05 08:45:02 | INFO | app.crawler.http | GET https://example.com
2026-09-05 08:45:03 | WARNING | app.crawler.http | HTTP 429
2026-09-05 08:45:04 | ERROR | app.database | SQLite error
```

Rất dễ đọc.

---

# 34. Development formatter

Khi debug:

```python
formatter = logging.Formatter(
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(filename)s:%(lineno)d | "
    "%(funcName)s | "
    "%(message)s"
)
```

Ví dụ:

```text
2026-09-05 08:45:01 | DEBUG |
app.crawler.parser |
parser.py:82 |
parse_chapter |
Found 42 paragraphs
```

---

# 35. Production không nên log quá nhiều metadata

Ví dụ:

```text
timestamp
level
logger
filename
line
function
process
thread
module
pathname
processName
threadName
...
```

Output có thể trở thành:

```text
2026-09-05 | INFO | app.crawler | parser.py | parser | 1234 | MainThread | ...
```

Khó đọc.

Do đó:

### Normal production

```text
timestamp | level | logger | message
```

### Debug mode

```text
timestamp | level | logger | file:line | function | message
```

### Machine-readable logs

Sau này:

```json
{
    "timestamp": "...",
    "level": "INFO",
    "logger": "app.crawler",
    "message": "Crawler started"
}
```

Đây sẽ là nền tảng của **Structured Logging** ở phần sau.

---

# 🧠 36. Mental Model của Buổi 4

Hãy nhớ toàn bộ pipeline:

```text
logger.info(
    "Chapter %s completed",
    123
)
        │
        ▼
   LogRecord
        │
        ├── name
        ├── levelname
        ├── pathname
        ├── filename
        ├── lineno
        ├── funcName
        ├── created
        ├── process
        ├── thread
        ├── msg
        └── args
        │
        ▼
    Handler
        │
        ▼
    Formatter
        │
        ▼
record.getMessage()
        │
        ▼
Final string
```

---

# 🎯 37. Những field nên nhớ

| Field         | Ý nghĩa               |
| ------------- | --------------------- |
| `name`        | Logger name           |
| `levelname`   | `INFO`, `ERROR`...    |
| `levelno`     | 20, 40...             |
| `message`     | Message cuối cùng     |
| `pathname`    | Full path             |
| `filename`    | Filename              |
| `module`      | Module                |
| `lineno`      | Dòng code             |
| `funcName`    | Function              |
| `created`     | Unix timestamp        |
| `msecs`       | Milliseconds          |
| `process`     | PID                   |
| `processName` | Process name          |
| `thread`      | Thread ID             |
| `threadName`  | Thread name           |
| `exc_info`    | Exception information |
| `stack_info`  | Current stack         |

---

# 🧪 Bài tập Buổi 4

## Bài 1 — Formatter

Tạo:

```python
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | "
    "%(name)s | %(filename)s:%(lineno)d | "
    "%(message)s"
)
```

và tạo:

```text
ConsoleHandler
FileHandler
```

---

## Bài 2 — LogRecord Inspector

Tự viết:

```python
class InspectHandler(logging.Handler):
    ...
```

và in ra ít nhất:

```text
name
levelname
pathname
filename
module
lineno
funcName
process
thread
message
```

---

## Bài 3 — Lazy formatting

So sánh:

```python
logger.debug(
    "Processing chapter %s",
    chapter_id,
)
```

với:

```python
logger.debug(
    f"Processing chapter {chapter_id}"
)
```

Sau đó đặt logger:

```python
logger.setLevel(logging.INFO)
```

và suy nghĩ:

> Khi DEBUG bị disable, hai cách trên khác nhau ở điểm nào về việc tạo message?

---

## Bài 4 — `stacklevel`

Tạo:

```python
def log_info(message):
    logger.info(message)
```

Gọi:

```python
log_info("Hello")
```

Quan sát `filename` và `lineno`.

Sau đó sửa:

```python
logger.info(
    message,
    stacklevel=2,
)
```

và quan sát sự khác biệt.

---

## ⭐ Bài 5 — Mini Production Logger

Tự xây:

```text
logging_demo/
├── main.py
└── app.log
```

Yêu cầu:

```text
Logger
  │
  ├── ConsoleHandler → INFO+
  │
  └── FileHandler    → DEBUG+
```

Formatter:

```text
2026-09-05 08:50:10 | INFO | app.crawler | Crawler started
```

Test:

```python
logger.debug("Debug")
logger.info("Info")
logger.warning("Warning")
logger.error("Error")
```

Kết quả mong muốn:

```text
Console:
INFO
WARNING
ERROR

app.log:
DEBUG
INFO
WARNING
ERROR
```

---

## 🔥 Kiến thức cốt lõi cần thuộc sau 4 buổi

Bạn đã có toàn bộ pipeline nền tảng:

```text
                Logger
                   │
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
                 Output
```

Trong đó:

```text
Logger
  → "Có log gì?"

LogRecord
  → "Log event chứa dữ liệu gì?"

Handler
  → "Log đi đâu?"

Formatter
  → "Log được trình bày thế nào?"
```

**Buổi 5** chúng ta sẽ đi sâu vào `basicConfig()` — không chỉ học cách dùng mà sẽ **mổ xẻ tại sao `basicConfig()` đôi khi không có tác dụng, tại sao gọi hai lần không tạo thêm handler, `force=True` làm gì, và khi nào nên bỏ hoàn toàn `basicConfig()` để chuyển sang `dictConfig()`**.
