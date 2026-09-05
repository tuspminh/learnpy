# 🐍 Logging Deep Dive — Buổi 3

# Handler Deep Dive

Ở Buổi 2, ta đã hiểu:

```text
Logger
   │
   ▼
LogRecord
   │
   ▼
Handler
```

Hôm nay chúng ta tập trung hoàn toàn vào **Handler**.

Mục tiêu:

* Hiểu Handler thực sự làm gì
* `StreamHandler`
* `FileHandler`
* nhiều Handler
* Handler level
* Logger level vs Handler level
* Vì sao một log có thể đi vào file nhưng không ra console
* Thiết kế nhiều Handler trong application thực tế

---

# 1. Handler là gì?

Nếu `Logger` trả lời:

> "Application muốn ghi log gì?"

thì `Handler` trả lời:

> "Log đó sẽ được gửi đi đâu?"

Ví dụ:

```text
Logger
   │
   ▼
LogRecord
   │
   ├──────────────► Console
   │
   ├──────────────► app.log
   │
   └──────────────► error.log
```

Ba output trên tương ứng với ba Handler.

---

# 2. Handler không phải là Formatter

Đây là hai khái niệm khác nhau.

```text
Handler
    │
    ├── quyết định OUTPUT ở đâu
    │
    └── có Formatter
             │
             └── quyết định FORMAT như thế nào
```

Ví dụ:

```python
handler = logging.StreamHandler()
```

Handler này gửi log tới stream, thường là `stderr`.

Sau đó:

```python
formatter = logging.Formatter(
    "%(levelname)s | %(message)s"
)

handler.setFormatter(formatter)
```

Formatter chỉ thay đổi **hình thức**.

---

# 3. `StreamHandler`

Handler cơ bản nhất:

```python
import logging

handler = logging.StreamHandler()
```

Mặc định nó ghi vào:

```python
sys.stderr
```

Ví dụ:

```python
import logging

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()

logger.addHandler(handler)

logger.info("Hello")
```

Có thể hình dung:

```text
logger.info()
      │
      ▼
LogRecord
      │
      ▼
StreamHandler
      │
      ▼
stderr
      │
      ▼
Terminal
```

---

# 4. Có thể chỉ định stream

Ví dụ muốn stdout:

```python
import sys
import logging

handler = logging.StreamHandler(sys.stdout)
```

Hoặc:

```python
handler = logging.StreamHandler(sys.stderr)
```

Điểm này đặc biệt hữu ích khi chạy application trong:

```text
Docker
Kubernetes
systemd
CI/CD
```

vì stdout/stderr thường được platform thu thập riêng.

---

# 5. `FileHandler`

Muốn ghi log vào file:

```python
handler = logging.FileHandler("app.log")
```

Ví dụ:

```python
import logging

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

handler = logging.FileHandler("app.log")

logger.addHandler(handler)

logger.info("Application started")
```

File:

```text
app.log
```

sẽ chứa:

```text
Application started
```

---

# 6. Encoding

Khi application có tiếng Việt, nên quan tâm encoding:

```python
handler = logging.FileHandler(
    "app.log",
    encoding="utf-8"
)
```

Ví dụ:

```python
logger.info("Đã bắt đầu crawler")
```

sẽ được ghi đúng UTF-8.

Trong production, nên chủ động chỉ định:

```python
encoding="utf-8"
```

thay vì phụ thuộc encoding mặc định của hệ thống.

---

# 7. Append vs Write

`FileHandler` mặc định ghi theo chế độ append:

```text
app chạy lần 1
    ↓
app.log

app chạy lần 2
    ↓
append vào app.log
```

Nếu cần mode khác:

```python
handler = logging.FileHandler(
    "app.log",
    mode="w",
    encoding="utf-8"
)
```

`w` sẽ overwrite file khi handler được tạo.

Thông thường application production **không nên dùng `w`** cho log chính.

---

# 8. Một Logger có thể có nhiều Handler

Đây là sức mạnh quan trọng của logging.

```python
logger = logging.getLogger("app")

console = logging.StreamHandler()
file = logging.FileHandler("app.log")

logger.addHandler(console)
logger.addHandler(file)
```

Flow:

```text
                  Logger
                    │
                    ▼
                LogRecord
                    │
             ┌──────┴──────┐
             ▼             ▼
        ConsoleHandler  FileHandler
             │             │
             ▼             ▼
          Terminal       app.log
```

Một log event có thể được xử lý bởi nhiều Handler.

---

# 9. Formatter có thể khác nhau

Đây là pattern rất hữu ích.

Console:

```text
INFO | Application started
```

File:

```text
2026-09-05 08:00:10 | INFO | app | Application started
```

Ta có:

```python
console_formatter = logging.Formatter(
    "%(levelname)s | %(message)s"
)

file_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
```

Sau đó:

```python
console.setFormatter(console_formatter)
file.setFormatter(file_formatter)
```

Như vậy:

```text
Logger
   │
   ▼
LogRecord
   │
   ├── Console
   │      └── ConsoleFormatter
   │
   └── File
          └── FileFormatter
```

---

# 10. Handler Level

Đây là phần quan trọng nhất hôm nay.

Handler cũng có:

```python
handler.setLevel(...)
```

Ví dụ:

```python
console.setLevel(logging.INFO)
```

nghĩa là ConsoleHandler chỉ xử lý:

```text
INFO
WARNING
ERROR
CRITICAL
```

Không xử lý:

```text
DEBUG
```

---

# 11. Logger Level và Handler Level

Giả sử:

```python
logger.setLevel(logging.DEBUG)
```

và:

```python
console.setLevel(logging.INFO)
```

Khi:

```python
logger.debug("debug")
```

LogRecord có thể được tạo, nhưng ConsoleHandler không xử lý nó.

Khi:

```python
logger.info("info")
```

ConsoleHandler xử lý.

Mô hình:

```text
Logger
level = DEBUG
     │
     ├── DEBUG ──────► Handler
     │                    X
     │
     └── INFO ───────► Handler
                          ✓
```

---

# 12. Hai tầng filtering

Ta có:

```text
Logger
   │
   │ Logger Level
   ▼
LogRecord
   │
   │ Handler Level
   ▼
Handler
```

Có thể hiểu:

### Logger level

Quyết định:

> Có tạo/xử lý log record cho logger này hay không?

### Handler level

Quyết định:

> Handler này có xử lý record đó hay không?

---

# 13. Ví dụ rất quan trọng

```python
import logging

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

logger.addHandler(console)

logger.debug("DEBUG")
logger.info("INFO")
logger.warning("WARNING")
logger.error("ERROR")
```

Output:

```text
INFO
WARNING
ERROR
```

Không có:

```text
DEBUG
```

vì:

```text
Logger:
DEBUG trở lên

Handler:
INFO trở lên
```

---

# 14. Trường hợp ngược lại

```python
logger.setLevel(logging.INFO)
console.setLevel(logging.DEBUG)
```

Bạn có thể tưởng:

```text
DEBUG sẽ xuất hiện
```

Nhưng không.

Kết quả:

```text
INFO
WARNING
ERROR
```

Tại sao?

Logger đã chặn DEBUG từ trước.

```text
DEBUG
  │
  ▼
Logger INFO
  │
  X
```

Handler thậm chí không nhận được DEBUG record.

Đây là lý do cần nhớ:

> **Handler không thể khôi phục một log đã bị Logger level loại bỏ.**

---

# 15. Công thức mental model

Hãy nhớ:

```text
Logger Level
     ↓
   Record
     ↓
Handler Level
     ↓
Formatter
     ↓
Output
```

Nếu bị chặn ở Logger:

```text
Logger
  │
  X
```

thì Handler không bao giờ nhìn thấy record.

---

# 16. Một ví dụ production rất thực tế

Ta muốn:

```text
DEBUG    → file
INFO     → console + file
WARNING  → console + file
ERROR    → console + file + error.log
CRITICAL → console + file + error.log
```

Thiết kế:

```text
                    Logger
                      │
                 level=DEBUG
                      │
          ┌───────────┼────────────┐
          ▼           ▼            ▼
       Console      app.log     error.log
       INFO         DEBUG        ERROR
```

Code:

```python
import logging

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

app_file = logging.FileHandler(
    "app.log",
    encoding="utf-8"
)
app_file.setLevel(logging.DEBUG)

error_file = logging.FileHandler(
    "error.log",
    encoding="utf-8"
)
error_file.setLevel(logging.ERROR)

logger.addHandler(console)
logger.addHandler(app_file)
logger.addHandler(error_file)
```

Bây giờ:

```python
logger.debug("debug")
```

→ `app.log`

```python
logger.info("started")
```

→ console + `app.log`

```python
logger.warning("slow response")
```

→ console + `app.log`

```python
logger.error("database failed")
```

→ console + `app.log` + `error.log`

---

# 17. Đừng quên Formatter

Hoàn thiện:

```python
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

console.setFormatter(formatter)
app_file.setFormatter(formatter)
error_file.setFormatter(formatter)
```

Kết quả:

```text
2026-09-05 08:10:12 | INFO | app | Application started
```

---

# 18. Một lỗi rất phổ biến: thêm Handler nhiều lần

Ví dụ bạn viết function:

```python
def setup_logging():
    logger = logging.getLogger("app")

    handler = logging.StreamHandler()

    logger.addHandler(handler)
```

Sau đó gọi:

```python
setup_logging()
setup_logging()
setup_logging()
```

Logger có:

```text
handler 1
handler 2
handler 3
```

Một log:

```python
logger.info("Hello")
```

có thể xuất hiện:

```text
Hello
Hello
Hello
```

---

# 19. Vì sao?

`Logger` giữ danh sách:

```python
logger.handlers
```

Bạn có thể kiểm tra:

```python
print(logger.handlers)
```

Hoặc:

```python
print(len(logger.handlers))
```

Nếu:

```text
3
```

thì bạn đã add ba handler.

---

# 20. Kiểm tra trước khi add

Có thể:

```python
if not logger.handlers:
    logger.addHandler(handler)
```

Nhưng trong application lớn, tôi thích thiết kế configuration rõ ràng hơn thay vì rải các điều kiện kiểu này khắp code.

---

# 21. `logger.handlers` và `logger.hasHandlers()`

Hai thứ này khác nhau.

```python
logger.handlers
```

chỉ xem handler **trực tiếp gắn vào logger đó**.

Trong khi:

```python
logger.hasHandlers()
```

có thể xem cả handler ở ancestor thông qua propagation.

Ví dụ:

```text
root
 └── handler

app
 └── no handler
```

thì:

```python
app.handlers
```

→ rỗng.

Nhưng:

```python
app.hasHandlers()
```

→ `True`

vì nó tìm thấy handler ở root.

---

# 22. Handler inheritance không giống Logger inheritance

Đây là điểm cần nhớ.

Nếu:

```text
root
 └── handler
```

thì handler **không được copy** xuống:

```text
app
```

Mà LogRecord propagate lên root:

```text
app
 │
 │ propagate
 ▼
root
 │
 └── handler
```

---

# 23. `addHandler()` không nên dùng trong từng module

Không nên:

```python
# crawler.py

logger = logging.getLogger(__name__)

handler = logging.FileHandler("crawler.log")
logger.addHandler(handler)
```

rồi:

```python
# repository.py

logger = logging.getLogger(__name__)

handler = logging.FileHandler("database.log")
logger.addHandler(handler)
```

Nếu application lớn, cấu hình sẽ trở nên khó kiểm soát.

Thay vào đó:

```text
app
│
├── main.py
│
├── logging_config.py
│
├── crawler/
├── database/
└── domain/
```

Các module:

```python
logger = logging.getLogger(__name__)
```

Còn cấu hình:

```text
logging_config.py
```

quản lý Handler.

---

# 24. Architecture tôi khuyên bạn dùng

Cho các project Python lớn:

```text
                    Application
                         │
                         ▼
                  configure_logging()
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
          Console      app.log    error.log
              ▲          ▲          ▲
              │          │          │
              └──────────┴──────────┘
                         ▲
                         │
                    Logger Tree
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
       crawler        database         ui
          │              │
        parser       repository
```

Module code cực kỳ đơn giản:

```python
import logging

logger = logging.getLogger(__name__)
```

Không cần biết:

* log đi file nào
* console format thế nào
* rotating thế nào
* error file ở đâu

Đó là trách nhiệm của **logging configuration**.

---

# 25. Một ví dụ hoàn chỉnh

```python
import logging


def configure_logging():
    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    app_file = logging.FileHandler(
        "app.log",
        encoding="utf-8",
    )
    app_file.setLevel(logging.DEBUG)
    app_file.setFormatter(formatter)

    error_file = logging.FileHandler(
        "error.log",
        encoding="utf-8",
    )
    error_file.setLevel(logging.ERROR)
    error_file.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(app_file)
    logger.addHandler(error_file)


configure_logging()

logger = logging.getLogger("app.crawler")

logger.debug("Crawler initialized")
logger.info("Crawler started")
logger.warning("Slow response")
logger.error("Request failed")
```

Kiến trúc:

```text
app
 │
 └── crawler
       │
       ▼
    LogRecord
       │
       ├────────────► Console
       │               INFO+
       │
       ├────────────► app.log
       │               DEBUG+
       │
       └────────────► error.log
                       ERROR+
```

---

# 🧠 26. Tổng kết Buổi 3

Bạn cần phân biệt rõ:

| Thành phần | Vai trò                       |
| ---------- | ----------------------------- |
| Logger     | Phát sinh log                 |
| LogRecord  | Dữ liệu của một log event     |
| Handler    | Đưa log tới đâu               |
| Formatter  | Log được hiển thị như thế nào |
| Filter     | Log nào được phép đi tiếp     |

Và đặc biệt:

```text
Logger Level
     ↓
  LogRecord
     ↓
Handler Level
     ↓
 Formatter
     ↓
  Output
```

Ví dụ production:

```text
Logger = DEBUG

ConsoleHandler = INFO
FileHandler = DEBUG
ErrorHandler = ERROR
```

sẽ tạo ra:

```text
DEBUG
 └──────────────► app.log

INFO
 ├─────────────► console
 └─────────────► app.log

WARNING
 ├─────────────► console
 └─────────────► app.log

ERROR
 ├─────────────► console
 ├─────────────► app.log
 └─────────────► error.log
```

---

# 🧪 Bài tập Buổi 3

Hãy tự xây:

```text
logging_demo/
└── main.py
```

Yêu cầu:

### Handler 1 — Console

```text
INFO+
```

### Handler 2 — `app.log`

```text
DEBUG+
```

### Handler 3 — `error.log`

```text
ERROR+
```

Logger:

```text
DEBUG+
```

Sau đó chạy:

```python
logger.debug("debug")
logger.info("info")
logger.warning("warning")
logger.error("error")
logger.critical("critical")
```

Và tự dự đoán trước khi chạy:

```text
              Console    app.log    error.log
DEBUG            ?          ?           ?
INFO             ?          ?           ?
WARNING          ?          ?           ?
ERROR            ?          ?           ?
CRITICAL         ?          ?           ?
```

**Buổi 4** chúng ta sẽ đi sâu vào **Formatter + LogRecord fields**: `asctime`, `created`, `msecs`, `relativeCreated`, `pathname`, `filename`, `module`, `lineno`, `funcName`, `process`, `thread`, `message`… và cuối buổi sẽ tự xây một formatter production-style.
