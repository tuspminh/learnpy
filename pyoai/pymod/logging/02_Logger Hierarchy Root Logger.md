# 🐍 Logging Deep Dive — Buổi 2

## Logger Hierarchy, Root Logger, `propagate`, `effectiveLevel`

Buổi này cực kỳ quan trọng. Sau buổi này bạn sẽ hiểu được những lỗi logging rất thường gặp:

* Vì sao log xuất hiện **2 lần**
* Vì sao `logger.setLevel()` nhưng log vẫn xuất hiện
* Vì sao một logger không có level riêng vẫn hoạt động
* `logging.getLogger(__name__)` thực sự tạo ra cái gì
* `propagate=False` dùng để làm gì

---

# 1. Logger không tồn tại độc lập

Giả sử project:

```text
myapp/
├── main.py
├── crawler/
│   ├── __init__.py
│   ├── service.py
│   └── parser.py
└── database/
    └── repository.py
```

Trong `service.py`:

```python
import logging

logger = logging.getLogger(__name__)
```

Logger có tên:

```text
myapp.crawler.service
```

Trong `parser.py`:

```python
logger = logging.getLogger(__name__)
```

→

```text
myapp.crawler.parser
```

Repository:

```text
myapp.database.repository
```

Python tạo ra một **cây logger**:

```text
root
│
└── myapp
    │
    ├── crawler
    │   ├── service
    │   └── parser
    │
    └── database
        └── repository
```

Đây gọi là:

# Logger Hierarchy

---

# 2. Tại sao logger có hierarchy?

Giả sử bạn muốn cấu hình toàn bộ crawler:

```text
myapp.crawler
```

Bạn có:

```text
myapp.crawler.service
myapp.crawler.parser
myapp.crawler.scheduler
myapp.crawler.worker
```

Bạn không cần cấu hình từng logger.

Có thể:

```python
crawler_logger = logging.getLogger("myapp.crawler")
```

Sau đó:

```python
crawler_logger.setLevel(logging.DEBUG)
```

Các logger con có thể kế thừa cấu hình từ parent.

Mô hình:

```text
myapp
 │
 └── crawler
      │
      ├── service
      ├── parser
      ├── scheduler
      └── worker
```

---

# 3. `logging.getLogger()` không phải mỗi lần gọi đều tạo Logger mới

Ví dụ:

```python
a = logging.getLogger("myapp")
b = logging.getLogger("myapp")

print(a is b)
```

Kết quả:

```text
True
```

Python quản lý logger theo tên.

```python
logging.getLogger("myapp")
```

về cơ bản có nghĩa:

> Lấy logger có tên `myapp` từ logging system.

Do đó:

```python
logger1 = logging.getLogger("app")
logger2 = logging.getLogger("app")
```

là cùng một logger.

---

# 4. Root Logger

Ở trên cùng của hierarchy là:

```text
root
```

Lấy root logger:

```python
root = logging.getLogger()
```

Hoặc:

```python
root = logging.root
```

Ví dụ:

```python
import logging

root = logging.getLogger()

print(root.name)
```

Kết quả thường là:

```text
root
```

Hierarchy:

```text
root
 │
 └── myapp
      │
      └── crawler
           │
           └── service
```

Root là **ancestor cuối cùng** của mọi named logger.

---

# 5. Logger `__name__` liên quan thế nào?

Giả sử:

```text
myapp/
└── crawler/
    └── service.py
```

Trong `service.py`:

```python
logger = logging.getLogger(__name__)
```

Nếu package được import đúng:

```text
__name__ = "myapp.crawler.service"
```

Vì vậy hierarchy:

```text
root
└── myapp
    └── crawler
        └── service
```

Đây là lý do best practice thường là:

```python
logger = logging.getLogger(__name__)
```

---

# 6. Parent logger

Ví dụ:

```python
service = logging.getLogger("myapp.crawler.service")
```

Parent trực tiếp của nó là:

```text
myapp.crawler
```

Parent tiếp theo:

```text
myapp
```

Cuối cùng:

```text
root
```

Có thể kiểm tra:

```python
print(service.parent.name)
```

Có thể cho kết quả:

```text
myapp.crawler
```

---

# 7. `propagate` — phần quan trọng nhất

Đây là cơ chế khiến nhiều người mới học logging đau đầu.

Giả sử:

```text
root
 │
 └── myapp
      │
      └── crawler
           │
           └── service
```

Bạn gọi:

```python
logger = logging.getLogger("myapp.crawler.service")

logger.info("Start crawling")
```

LogRecord được tạo tại:

```text
service
```

Nhưng nó có thể **propagate lên parent**:

```text
service
   │
   ▼
crawler
   │
   ▼
myapp
   │
   ▼
root
```

Đây chính là:

```python
logger.propagate
```

Mặc định thường là:

```python
True
```

---

# 8. Propagation không có nghĩa là tạo LogRecord mới

Điểm này rất quan trọng.

Không phải:

```text
service
 ↓ tạo record 1

crawler
 ↓ tạo record 2

myapp
 ↓ tạo record 3
```

Mà là:

```text
             LogRecord
                 │
                 ▼
service ────────► handler
                 │
                 ▼
              crawler
                 │
                 ▼
               myapp
                 │
                 ▼
                root
```

Cùng một `LogRecord` được xử lý bởi các handler trên đường propagation.

---

# 9. Vì sao log xuất hiện 2 lần?

Đây là lỗi kinh điển.

Ví dụ:

```python
import logging

root = logging.getLogger()
root.setLevel(logging.DEBUG)

root_handler = logging.StreamHandler()
root.addHandler(root_handler)


logger = logging.getLogger("myapp")

logger_handler = logging.StreamHandler()
logger.addHandler(logger_handler)

logger.info("Hello")
```

Có thể thấy:

```text
Hello
Hello
```

Tại sao?

Flow:

```text
myapp
 │
 ├── myapp_handler
 │       ↓
 │     print
 │
 └── propagate=True
         ↓
       root
         │
         └── root_handler
                 ↓
               print
```

Một LogRecord.

Hai handlers.

Hai output.

---

# 10. Cách sửa

Có hai cách.

### Cách 1 — Chỉ dùng root handler

Đây thường là kiến trúc đơn giản:

```python
logger = logging.getLogger(__name__)
```

Các module **không tự add handler**.

```text
application
     │
     └── root/config
             │
             └── handlers
```

---

### Cách 2 — `propagate=False`

Nếu logger tự quản lý handler:

```python
logger = logging.getLogger("myapp.crawler")

logger.addHandler(handler)
logger.propagate = False
```

Flow:

```text
crawler
  │
  └── handler
       ↓
     output

STOP
```

Không đi lên root.

---

# 11. `propagate=False` không có nghĩa là disable logger

Đây là hiểu nhầm phổ biến.

```python
logger.propagate = False
```

không có nghĩa:

```text
logger OFF
```

Nó chỉ có nghĩa:

> Không truyền LogRecord lên ancestor logger.

Logger vẫn hoạt động.

Ví dụ:

```python
logger.propagate = False

logger.error("Database failed")
```

Nếu logger có handler:

```text
logger
  │
  ▼
handler
  │
  ▼
output
```

vẫn output bình thường.

---

# 12. `effectiveLevel`

Một logger có:

```python
logger.level
```

nhưng còn một khái niệm khác:

```python
logger.getEffectiveLevel()
```

Hai cái này **không giống nhau**.

Ví dụ:

```python
parent = logging.getLogger("app")
parent.setLevel(logging.WARNING)

child = logging.getLogger("app.service")
```

Child không set level.

```python
print(child.level)
```

Có thể là:

```text
0
```

`0` nghĩa là:

```text
NOTSET
```

Child nói:

> Tôi không tự quyết định level, hãy tìm lên parent.

Vì vậy:

```python
print(child.getEffectiveLevel())
```

→

```text
30
```

`30` chính là:

```python
logging.WARNING
```

---

# 13. `NOTSET` rất quan trọng

Các level có giá trị:

```python
logging.DEBUG      # 10
logging.INFO       # 20
logging.WARNING   # 30
logging.ERROR     # 40
logging.CRITICAL  # 50
```

Và:

```python
logging.NOTSET     # 0
```

Ví dụ:

```text
app
 │
 ├── level = INFO
 │
 └── service
      └── level = NOTSET
```

Service sẽ dùng level của `app`.

```text
service
   │
   │ NOTSET
   ▼
app
   │
   │ INFO
   ▼
effective level = INFO
```

---

# 14. `setLevel()` và `effectiveLevel`

Ví dụ:

```python
logger = logging.getLogger("app.service")

logger.setLevel(logging.DEBUG)
```

Lúc này:

```python
logger.level
```

→

```text
10
```

và:

```python
logger.getEffectiveLevel()
```

→

```text
10
```

Nhưng:

```python
logger.setLevel(logging.NOTSET)
```

thì:

```python
logger.level
```

→

```text
0
```

Logger sẽ tìm parent.

---

# 15. Một ví dụ để bạn tự quan sát

Chạy:

```python
import logging

root = logging.getLogger()
app = logging.getLogger("app")
service = logging.getLogger("app.service")

root.setLevel(logging.ERROR)

print("root:", root.level)
print("app:", app.level)
print("service:", service.level)

print("service effective:", service.getEffectiveLevel())
```

Bạn sẽ thấy đại ý:

```text
root: 40
app: 0
service: 0
service effective: 40
```

Tại sao?

```text
service
   │
   │ NOTSET
   ▼
app
   │
   │ NOTSET
   ▼
root
   │
   │ ERROR
   ▼
effective level = ERROR
```

---

# 16. Một hierarchy thực tế cho project của bạn

Với một crawler/reading application, tôi khuyên dùng:

```text
root
│
└── app
    │
    ├── crawler
    │   ├── http
    │   ├── parser
    │   ├── scheduler
    │   └── worker
    │
    ├── database
    │   ├── sqlite
    │   └── repository
    │
    ├── domain
    │
    └── ui
```

Code:

```python
# crawler.py
logger = logging.getLogger(__name__)
```

Ví dụ:

```text
app.crawler
```

Parser:

```python
logger = logging.getLogger(__name__)
```

→

```text
app.crawler.parser
```

Repository:

```text
app.database.repository
```

Sau đó application configuration có thể kiểm soát:

```text
app
├── level = INFO
│
├── crawler
│   └── level = DEBUG
│
└── database
    └── level = WARNING
```

Rất mạnh.

---

# 17. Một kiến trúc logging sạch

Tôi đặc biệt khuyến nghị bạn ghi nhớ pattern này:

```text
                    Application
                         │
                         ▼
                  Logging Config
                         │
                         ▼
                       Root
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
         Console                  File
             ▲                       ▲
             │                       │
             └─────────┬─────────────┘
                       │
                    Handlers
                       ▲
                       │
                  propagation
                       ▲
                       │
              Logger hierarchy
                       ▲
                       │
       ┌───────────────┼───────────────┐
       │               │               │
    crawler         database           ui
       │               │
    parser        repository
```

Các module chỉ cần:

```python
logger = logging.getLogger(__name__)
```

**Không nên tự tạo handler ở từng module** nếu bạn đang xây application.

---

# 🧠 18. Ba quy tắc cần nhớ

### Quy tắc 1

Trong application:

```python
logger = logging.getLogger(__name__)
```

là lựa chọn mặc định tốt.

### Quy tắc 2

Handler thường nên được cấu hình **ở application/configuration layer**, không phải từng module.

### Quy tắc 3

Nếu logger có handler riêng:

```python
logger.addHandler(...)
```

hãy đặc biệt chú ý:

```python
logger.propagate
```

Nếu không, rất dễ:

```text
LOG
LOG
```

---

# 🧪 Bài tập Buổi 2

Hãy tạo:

```text
app
├── crawler
│   ├── parser
│   └── worker
└── database
    └── repository
```

Tạo logger:

```python
logging.getLogger("app")
logging.getLogger("app.crawler")
logging.getLogger("app.crawler.parser")
logging.getLogger("app.crawler.worker")
logging.getLogger("app.database.repository")
```

Sau đó thực hành:

### Bài 1

In:

```python
logger.name
logger.parent.name
logger.level
logger.getEffectiveLevel()
logger.propagate
```

### Bài 2

Đặt:

```text
root = WARNING
app = INFO
app.crawler = DEBUG
```

Quan sát effective level của:

```text
app.crawler.parser
app.crawler.worker
app.database.repository
```

### Bài 3

Cố tình tạo:

```text
root handler
app handler
app.crawler handler
```

rồi:

```python
logger = logging.getLogger("app.crawler.parser")
logger.info("Hello")
```

Quan sát vì sao `"Hello"` xuất hiện nhiều lần.

Sau đó sửa bằng:

```python
propagate = False
```

---

## 🎯 Sau Buổi 2 bạn cần thuộc lòng

```text
Logger hierarchy
        ↓
root
        ↓
app
        ↓
app.crawler
        ↓
app.crawler.parser
```

và:

```text
logger.level
      ≠
logger.getEffectiveLevel()
```

cũng như:

```text
propagate=True
```

nghĩa là LogRecord có thể tiếp tục đi lên ancestor để được các handler ở đó xử lý.

**Buổi 3** chúng ta sẽ mổ xẻ **Handler Deep Dive**: `StreamHandler`, `FileHandler`, Handler Level, nhiều Handler, và đặc biệt là **Logger Level vs Handler Level** — phần này sẽ giúp bạn hiểu chính xác tại sao `DEBUG` bị mất ở đâu trong pipeline.
