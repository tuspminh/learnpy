# 🐍 Logging Deep Dive — Buổi 5

# `basicConfig()` Deep Dive

Hôm nay chúng ta sẽ **mổ xẻ `logging.basicConfig()`**, thay vì chỉ học cách dùng.

Sau buổi này bạn phải hiểu được:

```text
basicConfig()
    │
    ├── Root Logger
    ├── Handler
    ├── Formatter
    ├── Level
    ├── filename
    ├── stream
    ├── force
    └── encoding
```

và đặc biệt:

> **Tại sao gọi `basicConfig()` nhưng không thấy nó thay đổi gì?**

---

# 1. `basicConfig()` là gì?

Cách đơn giản nhất để bật logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO
)

logging.info("Application started")
```

Output:

```text
INFO:root:Application started
```

`basicConfig()` là một **convenience function** để cấu hình logging cơ bản.

Nó chủ yếu cấu hình:

```text
Root Logger
     │
     └── Handler
```

---

# 2. `basicConfig()` thực sự cấu hình Root Logger

Khi:

```python
logging.basicConfig(
    level=logging.INFO
)
```

về concept:

```text
root logger
    │
    ├── level = INFO
    │
    └── handler
          │
          └── formatter
```

Sau đó:

```python
logger = logging.getLogger("app.crawler")
```

có thể propagate lên root:

```text
app.crawler
      │
      │ propagate
      ▼
    root
      │
      ▼
   handler
      │
      ▼
  console
```

---

# 3. Một ví dụ đơn giản

```python
import logging

logging.basicConfig(
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

logger.debug("DEBUG")
logger.info("INFO")
logger.warning("WARNING")
logger.error("ERROR")
```

Kết quả:

```text
INFO:__main__:INFO
WARNING:__main__:WARNING
ERROR:__main__:ERROR
```

DEBUG không xuất hiện vì effective level là INFO.

---

# 4. Các tham số quan trọng

Prototype hiện đại có nhiều option, nhưng những cái bạn cần nắm trước:

```python
logging.basicConfig(
    level=...,
    format=...,
    datefmt=...,
    filename=...,
    filemode=...,
    stream=...,
    handlers=...,
    force=...,
    encoding=...,
    errors=...,
)
```

Chúng ta lần lượt mổ xẻ.

---

# 5. `level`

Ví dụ:

```python
logging.basicConfig(
    level=logging.DEBUG
)
```

Root logger:

```text
DEBUG+
```

Hoặc:

```python
logging.basicConfig(
    level=logging.WARNING
)
```

thì:

```text
DEBUG ❌
INFO  ❌
WARNING ✅
ERROR   ✅
CRITICAL ✅
```

---

# 6. `format`

Mặc định:

```text
INFO:root:Hello
```

Bạn có thể:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
```

Output:

```text
2026-09-05 09:00:00,123 | INFO | __main__ | Hello
```

Bạn đã sử dụng kiến thức Formatter từ Buổi 4.

---

# 7. `datefmt`

Có thể tùy chỉnh timestamp:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
```

Output:

```text
2026-09-05 09:00:00 | INFO | Application started
```

---

# 8. `filename`

Nếu:

```python
logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
)
```

thì logging sẽ ghi vào:

```text
app.log
```

thay vì console.

Ví dụ:

```python
logging.info("Crawler started")
```

→

```text
app.log
```

---

# 9. `filemode`

Mặc định file mode là append.

```python
logging.basicConfig(
    filename="app.log",
    filemode="a",
)
```

Mỗi lần application chạy:

```text
old logs
+
new logs
```

Nếu:

```python
filemode="w"
```

thì file bị ghi lại từ đầu khi logging được cấu hình theo mode đó.

Trong production, log chính thường không nên dùng `w`.

---

# 10. `encoding`

Rất quan trọng với tiếng Việt:

```python
logging.basicConfig(
    filename="app.log",
    encoding="utf-8",
)
```

Ví dụ:

```python
logging.info("Đã tải chương truyện thành công")
```

sẽ được ghi UTF-8.

---

# 11. `stream`

Mặc định handler cơ bản thường dùng `sys.stderr`.

Có thể chỉ định:

```python
import sys

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
)
```

Khi đó:

```text
logging
   ↓
stdout
```

Thay vì:

```text
logging
   ↓
stderr
```

Điều này hữu ích trong Docker/CI/CD.

---

# 12. `handlers`

Đây là option cực kỳ đáng chú ý.

Thay vì để `basicConfig()` tự tạo handler:

```python
logging.basicConfig(
    level=logging.INFO
)
```

ta có thể tự tạo:

```python
console = logging.StreamHandler()
file = logging.FileHandler(
    "app.log",
    encoding="utf-8",
)
```

sau đó:

```python
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        console,
        file,
    ],
)
```

Kiến trúc:

```text
                 Root
                  │
             level=DEBUG
                  │
          ┌───────┴───────┐
          ▼               ▼
      Console           File
       INFO+            DEBUG+
```

Đây đã bắt đầu vượt qua mức "basic".

---

# 13. `basicConfig()` có một đặc điểm cực kỳ quan trọng

Hãy chạy:

```python
import logging

logging.basicConfig(
    level=logging.INFO
)

logging.basicConfig(
    level=logging.DEBUG
)

logging.debug("Hello")
```

Bạn có thể ngạc nhiên:

> DEBUG không xuất hiện!

Tại sao?

---

# 14. `basicConfig()` không cấu hình lại nếu root đã có handler

Đây là behavior cực kỳ quan trọng.

Conceptually:

```text
basicConfig()
    │
    ▼
Root đã có handler?
    │
   YES
    │
    └── Không làm gì
```

Do đó:

```python
logging.basicConfig(level=logging.INFO)
```

đã cấu hình root.

Lần thứ hai:

```python
logging.basicConfig(level=logging.DEBUG)
```

thường không thay đổi configuration hiện tại.

---

# 15. Đây là lỗi rất hay gặp

Ví dụ:

```python
# library_a.py
import logging

logging.basicConfig(
    level=logging.INFO
)
```

Sau đó application:

```python
# main.py

logging.basicConfig(
    level=logging.DEBUG
)
```

Bạn mong:

```text
DEBUG
```

nhưng có thể vẫn nhận:

```text
INFO+
```

vì library đã cấu hình root trước.

Đây chính là lý do:

> **Library không nên tự gọi `basicConfig()` để cấu hình application logging.**

Library chỉ nên tạo logger:

```python
logger = logging.getLogger(__name__)
```

và để application quyết định configuration.

---

# 16. `force=True`

Python cung cấp:

```python
logging.basicConfig(
    level=logging.DEBUG,
    force=True,
)
```

`force=True` yêu cầu logging **tháo các handler hiện có khỏi root và cấu hình lại** theo `basicConfig()`.

Mental model:

```text
root
 │
 ├── old handler
 └── old handler

       │
       │ force=True
       ▼

root
 │
 └── new handler
```

Ví dụ:

```python
logging.basicConfig(
    level=logging.INFO
)

logging.basicConfig(
    level=logging.DEBUG,
    force=True
)
```

Lần thứ hai thực sự có hiệu lực.

---

# 17. `force=True` không phải thuốc chữa mọi vấn đề

Không nên cứ thấy logging sai là:

```python
force=True
```

vì nó thay đổi cấu hình root và tháo các handler hiện có.

Nó phù hợp khi bạn **cố ý muốn application configuration trở thành cấu hình authoritative**, đặc biệt trong executable/application entry point.

---

# 18. `basicConfig()` và `getLogger(__name__)`

Một pattern rất đẹp:

```python
# main.py

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

logger.info("Application started")
```

Module khác:

```python
# crawler.py

import logging

logger = logging.getLogger(__name__)

logger.info("Crawler started")
```

Flow:

```text
crawler
   │
   ▼
app configuration
   │
   ▼
root
   │
   ▼
handler
```

Module không cần biết handler nằm ở đâu.

---

# 19. `basicConfig()` không phải production logging architecture

Đây là điều bạn nên nhớ.

`basicConfig()` rất tốt cho:

```text
script nhỏ
CLI nhỏ
prototype
debug nhanh
tutorial
```

Ví dụ:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
)
```

hoàn toàn ổn.

Nhưng application lớn:

```text
Crawler
Database
Worker
GUI
Scheduler
HTTP
```

thì thường cần:

```text
dictConfig()
```

hoặc configuration architecture riêng.

---

# 20. Một vấn đề khác: `basicConfig(filename=...)`

Bạn có thể:

```python
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
)
```

nhưng lúc này bạn chỉ có một handler kiểu file.

Nếu muốn:

```text
Console
+
app.log
+
error.log
```

thì `basicConfig()` bắt đầu trở nên không tiện.

Có thể sử dụng:

```python
handlers=[...]
```

nhưng với configuration phức tạp, `dictConfig()` sẽ phù hợp hơn.

---

# 21. `basicConfig(handlers=...)`

Ví dụ:

```python
import logging


console = logging.StreamHandler()

file = logging.FileHandler(
    "app.log",
    encoding="utf-8",
)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        console,
        file,
    ],
)
```

Điểm cần nhớ:

`basicConfig()` không tự biến thành một framework configuration system.

Bạn vẫn đang tự tạo Handler.

Nó chỉ giúp configure root.

---

# 22. `basicConfig()` và Handler Level

Một điểm quan trọng từ Buổi 3:

```python
console = logging.StreamHandler()
console.setLevel(logging.INFO)

file = logging.FileHandler("app.log")
file.setLevel(logging.DEBUG)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[console, file],
)
```

Kết quả:

```text
DEBUG
 └── app.log

INFO
 ├── console
 └── app.log

WARNING
 ├── console
 └── app.log

ERROR
 ├── console
 └── app.log
```

`basicConfig(level=DEBUG)` thiết lập level cho root.

Nhưng mỗi Handler vẫn có level riêng.

---

# 23. `basicConfig()` và `propagate`

Ví dụ:

```text
app.crawler
    │
    │ propagate=True
    ▼
root
    │
    ▼
handler
```

Nếu:

```python
logger = logging.getLogger("app.crawler")
```

và không tự add handler:

```text
logger.handlers == []
```

thì log vẫn có thể xuất hiện vì nó propagate lên root.

Đây là lý do:

```python
logger = logging.getLogger(__name__)
```

hoạt động rất tốt cùng với:

```python
logging.basicConfig(...)
```

---

# 24. Một lỗi kinh điển

Bạn có:

```python
logging.basicConfig(
    level=logging.INFO,
    format="ROOT: %(message)s",
)
```

Sau đó:

```python
logger = logging.getLogger("app")

handler = logging.StreamHandler()

logger.addHandler(handler)

logger.info("Hello")
```

Output có thể:

```text
Hello
ROOT: Hello
```

Tại sao?

```text
app
 │
 ├── local handler
 │      ↓
 │    Hello
 │
 └── propagate=True
        ↓
      root
        ↓
      handler
        ↓
    ROOT: Hello
```

Sửa:

```python
logger.propagate = False
```

hoặc tốt hơn là **đừng add handler ở logger con nếu không cần**.

---

# 25. `basicConfig()` trong Library — KHÔNG nên

Giả sử bạn viết:

```python
# mycrawler/__init__.py

import logging

logging.basicConfig(
    level=logging.DEBUG
)
```

Đây là thiết kế không tốt.

Người dùng library có thể muốn:

```text
WARNING+
```

nhưng library tự ép:

```text
DEBUG+
```

rất khó chịu.

Library nên:

```python
import logging

logger = logging.getLogger(__name__)
```

Nếu cần tránh "no handler" warning trong library, Python cung cấp cơ chế `NullHandler`, chúng ta sẽ học kỹ hơn sau.

---

# 26. Application Entry Point mới là nơi configuration

Pattern:

```text
myapp/
├── main.py
├── crawler/
│   ├── service.py
│   └── parser.py
├── database/
│   └── repository.py
└── logging_config.py
```

`main.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)
```

`crawler/service.py`:

```python
import logging

logger = logging.getLogger(__name__)


def crawl():
    logger.info("Crawler started")
```

Đây là separation tốt:

```text
Application
     │
     ├── configure logging
     │
     ▼
Logger hierarchy
     │
     ├── crawler
     ├── database
     └── service
```

---

# 27. `basicConfig()` phù hợp ở đâu?

### Rất phù hợp:

```text
hello.py
script.py
small CLI
prototype
learning
temporary debugging
```

Ví dụ:

```python
logging.basicConfig(
    level=logging.DEBUG,
)
```

### Không phải lựa chọn tốt nhất cho:

```text
large application
multi-handler architecture
structured logging
JSON logging
rotating logs
queue logging
environment-specific config
complex filtering
```

Khi đó chúng ta chuyển sang:

```text
dictConfig()
```

---

# 28. Một cấu hình `basicConfig()` đẹp

Đối với script/CLI:

```python
import logging


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
    datefmt="%Y-%m-%d %H:%M:%S",
)
```

Sau đó:

```python
logger = logging.getLogger(__name__)
```

và dùng:

```python
logger.info("Application started")
logger.warning("Something looks wrong")
logger.error("Operation failed")
```

Đây là cách rất sạch cho application nhỏ.

---

# 29. Thực hành kiểm tra `basicConfig()`

Hãy chạy:

```python
import logging

root = logging.getLogger()

print("Before:")
print(root.level)
print(root.handlers)

logging.basicConfig(
    level=logging.INFO,
)

print("\nAfter:")
print(root.level)
print(root.handlers)
```

Bạn sẽ quan sát được `basicConfig()` đã thay đổi root như thế nào.

---

# 30. Thí nghiệm quan trọng: gọi hai lần

```python
import logging

logging.basicConfig(
    level=logging.INFO,
)

print("After first:")
print(logging.getLogger().handlers)

logging.basicConfig(
    level=logging.DEBUG,
)

print("After second:")
print(logging.getLogger().handlers)
```

Sau đó thử:

```python
logging.debug("DEBUG")
logging.info("INFO")
```

và quan sát.

---

# 31. Thí nghiệm `force=True`

```python
import logging

logging.basicConfig(
    level=logging.INFO,
)

logging.basicConfig(
    level=logging.DEBUG,
    force=True,
)

logging.debug("DEBUG")
```

Bây giờ DEBUG sẽ xuất hiện.

Bạn vừa trực tiếp thấy sự khác biệt giữa:

```text
basicConfig()
```

và:

```text
basicConfig(force=True)
```

---

# 32. Một điểm rất quan trọng: `basicConfig()` có thể được gọi gián tiếp

Một số convenience functions như:

```python
logging.debug(...)
logging.info(...)
logging.warning(...)
logging.error(...)
logging.critical(...)
```

có behavior đặc biệt: nếu root logger chưa có handler, chúng có thể gọi `basicConfig()` tự động.

Ví dụ:

```python
import logging

logging.warning("Something happened")
```

có thể tự tạo basic configuration.

Trong khi:

```python
logger = logging.getLogger(__name__)
logger.warning("Something happened")
```

là cách explicit hơn và phù hợp với application architecture.

---

# 33. Đây là lý do nên configure logging sớm

Trong `main.py`:

```python
def main():
    configure_logging()

    run_application()
```

Tức:

```text
main()
 │
 ├── configure_logging()
 │
 └── application
       │
       ├── crawler
       ├── database
       └── worker
```

Tránh để các module tự ý cấu hình root.

---

# 🧠 34. Mental Model Buổi 5

Hãy nhớ:

```text
basicConfig()
     │
     ▼
   ROOT
     │
     ├── level
     │
     └── handler
             │
             └── formatter
```

Và:

```text
basicConfig()
     │
     ▼
Root đã có handler?
     │
 ┌───┴───┐
YES     NO
 │       │
STOP    CONFIGURE
```

Nếu:

```python
force=True
```

thì:

```text
Existing root handlers
        │
        ▼
     removed
        │
        ▼
new configuration
```

---

# 🎯 35. Khi nào dùng `basicConfig()`?

| Trường hợp                      | `basicConfig()` |
| ------------------------------- | --------------- |
| Script nhỏ                      | ✅               |
| Học Python                      | ✅               |
| Prototype                       | ✅               |
| CLI nhỏ                         | ✅               |
| Application vừa                 | ⚠️              |
| Application lớn                 | ❌/⚠️            |
| Multi-handler phức tạp          | ❌               |
| JSON logging                    | ❌               |
| Queue logging                   | ❌               |
| Production logging architecture | `dictConfig()`  |

Không phải `basicConfig()` "xấu".

Nó chỉ là **cấu hình cơ bản**.

---

# 🧪 Bài tập Buổi 5

## Bài 1 — Basic

Tạo:

```python
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
```

Sau đó test 5 levels.

---

## Bài 2 — File

Thử:

```python
logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    encoding="utf-8",
)
```

Ghi:

```text
Application started
Đã tải chương truyện
Database connected
```

---

## Bài 3 — Hai lần `basicConfig()`

Thử:

```python
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)
```

Giải thích tại sao DEBUG không hoạt động như bạn mong đợi.

---

## Bài 4 — `force=True`

Sửa thành:

```python
logging.basicConfig(
    level=logging.DEBUG,
    force=True,
)
```

Quan sát kết quả.

---

## ⭐ Bài 5 — Multi-handler

Tự tạo:

```text
Logger
  │
  ├── ConsoleHandler → INFO+
  │
  └── FileHandler    → DEBUG+
```

sau đó truyền vào:

```python
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[console, file],
)
```

Kiểm tra:

```text
              Console    app.log
DEBUG            ❌         ✅
INFO             ✅         ✅
WARNING          ✅         ✅
ERROR            ✅         ✅
```

---

# 🔥 Kiến thức quan trọng nhất của Buổi 5

Bạn nên ghi nhớ 5 điều:

```text
1. basicConfig() chủ yếu cấu hình ROOT logger.

2. basicConfig() không reconfigure root
   nếu root đã có handler.

3. force=True ép cấu hình lại root.

4. Library không nên tự gọi basicConfig().

5. Application entry point mới nên chịu trách nhiệm
   cấu hình logging.
```

Kiến trúc sạch:

```text
                main.py
                   │
                   ▼
          configure_logging()
                   │
                   ▼
                 ROOT
                   │
             ┌─────┴─────┐
             ▼           ▼
         Console       File
             ▲           ▲
             │           │
             └─────┬─────┘
                   │
              propagation
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
       crawler  database    ui
          │
       parser
```

**Buổi 6** chúng ta sẽ bước sang phần rất quan trọng: **`logging.config.dictConfig()`**. Đây là lúc Logging Deep Dive chuyển từ "biết sử dụng logging" sang **thiết kế logging architecture cho application production** — nhiều logger, nhiều handler, formatter, level, `propagate`, `disable_existing_loggers`, cấu hình bằng dictionary và tách configuration khỏi code.
