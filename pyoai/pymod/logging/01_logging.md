
# 🔥 Buổi 1 — Logging Architecture

Trước tiên cần bỏ một suy nghĩ khá phổ biến:

```python
print("Something happened")
```

không phải là logging.

`print()` chỉ đơn giản là ghi text ra stdout.

Logging là **một hệ thống xử lý sự kiện log**.

Kiến trúc cốt lõi của Python logging:

```text
logger
   │
   │ LogRecord
   ▼
handler
   │
   ▼
formatter
   │
   ▼
output
```

Ví dụ:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Application started")
```

Khi chạy, về mặt concept:

```text
logger.info(...)
       │
       ▼
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
   Console/File
```

Đây là kiến trúc mà chúng ta sẽ đào rất sâu.

---

## 1. Logger

`Logger` là nơi application **phát sinh log event**.

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Application started")
logger.warning("Something suspicious")
logger.error("Something failed")
logger.critical("System is unusable")
```

Có 5 level cơ bản:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

Mức độ tăng dần:

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

Có thể hình dung:

```text
DEBUG      → thông tin phục vụ developer
INFO       → application đang hoạt động thế nào
WARNING    → có vấn đề nhưng chưa chết
ERROR      → một operation thất bại
CRITICAL   → vấn đề nghiêm trọng
```

---

# 2. Logger không trực tiếp ghi ra file

Đây là điểm **cực kỳ quan trọng**.

Nhiều người nghĩ:

```python
logger.info("hello")
```

→ logger ghi `"hello"` vào file.

Không chính xác.

Logger tạo ra một `LogRecord`.

```text
logger.info()
      │
      ▼
 LogRecord
```

`LogRecord` chứa rất nhiều metadata:

```text
message
level
logger name
filename
line number
function name
timestamp
exception information
...
```

Sau đó `LogRecord` được đưa cho `Handler`.

---

# 3. Handler

`Handler` quyết định:

> Log này sẽ đi đâu?

Ví dụ:

```python
console_handler
```

→ terminal

```python
file_handler
```

→ file

Có thể có nhiều handler:

```text
                  ┌── ConsoleHandler
                  │
Logger ── LogRecord ── FileHandler
                  │
                  └── ErrorHandler
```

Ví dụ:

```python
import logging

logger = logging.getLogger("app")

console = logging.StreamHandler()
file = logging.FileHandler("app.log")

logger.addHandler(console)
logger.addHandler(file)
```

Một log event có thể được gửi tới **nhiều nơi**.

---

# 4. Formatter

Handler quyết định:

> Đi đâu?

Formatter quyết định:

> Viết như thế nào?

Ví dụ:

```python
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
```

Output:

```text
2026-09-05 07:42:10,123 | INFO | app | Application started
```

Trong đó:

```text
%(asctime)s
```

→ thời gian

```text
%(levelname)s
```

→ INFO

```text
%(name)s
```

→ tên logger

```text
%(message)s
```

→ nội dung log

---

# 5. Filter

Filter cho phép chúng ta quyết định:

> LogRecord này có được phép đi tiếp hay không?

Ví dụ application có:

```text
crawler
database
http
ui
```

Ta có thể filter:

```text
Logger
   │
   ▼
Filter
   │
   ├── ACCEPT
   │
   └── REJECT
```

Sau này chúng ta sẽ dùng Filter để thêm:

```text
request_id
task_id
chapter_id
```

vào log.

---

# 6. Một ví dụ hoàn chỉnh

```python
import logging

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

console.setFormatter(formatter)

logger.addHandler(console)

logger.debug("Debug message")
logger.info("Application started")
logger.warning("Low disk space")
logger.error("Database connection failed")
```

Kiến trúc:

```text
logger
  │
  │ DEBUG
  │ INFO
  │ WARNING
  │ ERROR
  ▼
LogRecord
  │
  ▼
StreamHandler
  │
  ▼
Formatter
  │
  ▼
Terminal
```

---

# 7. Logger level và Handler level

Đây là một chủ đề chúng ta sẽ đào cực sâu.

Có **hai nơi lọc level**:

```text
Logger
   │
   │ level?
   ▼
Handler
   │
   │ level?
   ▼
Formatter
```

Ví dụ:

```python
logger.setLevel(logging.DEBUG)
handler.setLevel(logging.INFO)
```

Kết quả:

```text
DEBUG    ❌
INFO     ✅
WARNING  ✅
ERROR    ✅
CRITICAL ✅
```

Bởi vì:

```text
Logger:
DEBUG trở lên

Handler:
INFO trở lên
```

Do đó DEBUG bị handler loại bỏ.

---

# 8. Root Logger

Python có một logger đặc biệt:

```text
root
```

Có thể truy cập:

```python
logging.getLogger()
```

Trong khi:

```python
logging.getLogger(__name__)
```

lấy **named logger**.

Ví dụ file:

```text
crawler/service.py
```

có:

```python
logger = logging.getLogger(__name__)
```

thì:

```python
logger.name
```

sẽ là:

```text
crawler.service
```

Đây chính là nền tảng của **Logger Hierarchy** mà chúng ta sẽ học ở Buổi 2.

---

# 9. Vì sao nên dùng `__name__`?

Không nên viết khắp nơi:

```python
logger = logging.getLogger("app")
```

Thường nên:

```python
logger = logging.getLogger(__name__)
```

Ví dụ:

```text
app/
├── main.py
├── crawler.py
└── repository.py
```

Ta có:

```python
# crawler.py
logger = logging.getLogger(__name__)
```

→

```text
app.crawler
```

và:

```python
# repository.py
logger = logging.getLogger(__name__)
```

→

```text
app.repository
```

Khi log:

```text
INFO | app.crawler | Start crawling
ERROR | app.repository | Database error
```

Ta biết **log phát sinh từ module nào**.

---

# 10. Mental Model quan trọng nhất

Hãy nhớ mô hình này:

```text
                 Application
                     │
                     ▼
                  Logger
                     │
                     ▼
                 LogRecord
                     │
              ┌──────┴──────┐
              ▼             ▼
           Handler       Handler
              │             │
              ▼             ▼
           Console         File
              │             │
              ▼             ▼
          Formatter      Formatter
```

Và:

```text
Logger
  │
  ├── level
  │
  ├── handlers
  │
  ├── filters
  │
  └── propagate
```

Trong khi:

```text
Handler
  │
  ├── level
  ├── filters
  └── formatter
```

Đây là **xương sống của toàn bộ Logging Deep Dive**.

---

# 🧪 Bài tập Buổi 1

Viết một chương trình:

```text
app.py
```

có:

```python
logger = logging.getLogger(__name__)
```

Tạo:

```text
Console Handler
File Handler
```

Yêu cầu:

```text
DEBUG    → chỉ Console
INFO     → Console + File
WARNING  → Console + File
ERROR    → Console + File
CRITICAL → Console + File
```

Output console:

```text
2026-09-05 07:xx:xx | INFO | __main__ | Application started
```

File:

```text
app.log
```

cũng phải chứa log tương ứng.

**Điểm quan trọng của bài này:** hãy tự cấu hình `Logger`, `Handler`, `Formatter` thay vì dùng `basicConfig()`.

Ở **Buổi 2**, chúng ta sẽ mổ xẻ **Logger Hierarchy + Root Logger + `propagate` + `effectiveLevel`** — đây là phần rất quan trọng để hiểu tại sao một log đôi khi xuất hiện **2 lần**, hoặc tại sao thay đổi level nhưng log vẫn không biến mất.
