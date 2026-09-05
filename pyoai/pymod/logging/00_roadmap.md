Được. Từ bây giờ tôi sẽ đóng vai **Python Senior Developer + người hướng dẫn**, và chúng ta sẽ học **Logging Deep Dive** theo hướng production, không chỉ dừng ở `logging.basicConfig()`.

# 🐍 Logging Deep Dive — Roadmap

Mục tiêu cuối cùng:

```text
Application
    │
    ├── Logger
    │
    ├── Handler
    │      ├── Console
    │      ├── File
    │      ├── Rotating File
    │      └── Error File
    │
    ├── Formatter
    │
    ├── Filter
    │
    ├── LogRecord
    │
    └── Exception / Context / Correlation ID
```

## Phần I — Logging Foundation

**Buổi 1 — Logging Architecture**

* Logger
* Handler
* Formatter
* Filter
* LogRecord
* Logging flow
* `logging.getLogger()`
* `logger.info()`, `debug()`, `warning()`, `error()`, `critical()`

**Buổi 2 — Logger Deep Dive**

* Logger hierarchy
* Root logger
* Named logger
* `__name__`
* Parent/child logger
* `propagate`
* `effectiveLevel`

**Buổi 3 — Handler Deep Dive**

* `StreamHandler`
* `FileHandler`
* nhiều Handler
* Handler level
* Logger level vs Handler level

**Buổi 4 — Formatter Deep Dive**

* Log format
* `%(asctime)s`
* `%(name)s`
* `%(levelname)s`
* `%(message)s`
* `%(filename)s`
* `%(lineno)d`
* `%(funcName)s`

---

# Phần II — Logging Configuration

**Buổi 5 — `basicConfig()` Deep Dive**

**Buổi 6 — `dictConfig()`**

**Buổi 7 — `fileConfig()` và configuration architecture**

**Buổi 8 — Logging trong package/application**

```text
myapp/
├── app/
│   ├── service.py
│   ├── repository.py
│   └── crawler.py
│
└── logging_config.py
```

**Buổi 9 — Logging trong Library vs Application**

Đây là phần rất quan trọng khi xây framework.

---

# Phần III — Advanced Logging

**Buổi 10 — LogRecord Deep Dive**

**Buổi 11 — Filter Deep Dive**

**Buổi 12 — Custom Handler**

**Buổi 13 — Custom Formatter**

**Buổi 14 — `LoggerAdapter`**

**Buổi 15 — Contextual Logging**

```text
request_id
user_id
task_id
story_id
chapter_id
```

---

# Phần IV — Exception & Debugging

**Buổi 16 — `logger.exception()`**

**Buổi 17 — Exception + traceback**

**Buổi 18 — Logging errors đúng cách**

**Buổi 19 — Debugging production**

**Buổi 20 — Anti-patterns**

Ví dụ:

```python
logger.error(str(e))
```

vs

```python
logger.exception("Failed to process chapter")
```

---

# Phần V — Production Logging

**Buổi 21 — RotatingFileHandler**

**Buổi 22 — TimedRotatingFileHandler**

**Buổi 23 — Multi-file logging**

```text
logs/
├── app.log
├── error.log
└── crawler.log
```

**Buổi 24 — QueueHandler / QueueListener**

**Buổi 25 — Thread-safe logging**

**Buổi 26 — Async application logging**

---

# Phần VI — Structured Logging

**Buổi 27 — JSON Logging**

```json
{
    "timestamp": "...",
    "level": "ERROR",
    "logger": "crawler",
    "message": "Request failed",
    "url": "...",
    "status_code": 500
}
```

**Buổi 28 — Structured LogRecord**

**Buổi 29 — Correlation ID**

**Buổi 30 — Logging cho distributed system**

---

# Phần VII — Logging trong hệ thống thực tế

**Buổi 31 — Logging cho HTTPX**

**Buổi 32 — Logging cho Asyncio**

**Buổi 33 — Logging cho ThreadPoolExecutor**

**Buổi 34 — Logging cho ProcessPoolExecutor**

**Buổi 35 — Logging cho SQLite / Repository**

**Buổi 36 — Logging cho PySide6**

**Buổi 37 — Logging cho CLI**

---

# Phần VIII — Production Architecture

**Buổi 38 — Centralized Logging Architecture**

```text
Application
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
     ├── Console
     ├── App File
     └── Error File
```

**Buổi 39 — Logging Architecture cho Crawler**

**Buổi 40 — Logging Architecture cho Clean Architecture**

```text
Presentation
      ↓
Application
      ↓
Domain
      ↓
Infrastructure
```

**Buổi 41 — Logging + Testing**

**Buổi 42 — Logging Security**

* Secret leakage
* Password
* Token
* Cookie
* API key
* PII

**Buổi 43 — Performance**

**Buổi 44 — Logging Anti-patterns**

**Buổi 45 — Final Project**

Xây dựng:

```text
Production Logging Framework
│
├── ConsoleHandler
├── FileHandler
├── ErrorHandler
├── RotatingHandler
├── JSONFormatter
├── ContextFilter
├── Request ID
├── QueueHandler
├── QueueListener
└── configuration
```

---
