# Buổi 2 — Cài đặt Redis + RQ và chạy Job đầu tiên

Hôm nay chúng ta làm được pipeline hoàn chỉnh:

```text
Python Producer
      │
      │ enqueue()
      ▼
    Redis
      │
      ▼
  RQ Worker
      │
      ▼
 Python Function
```

## 1. Cài RQ

Nếu bạn dùng `uv` — rất phù hợp với workflow Python của bạn:

```bash
uv add rq redis
```

Hoặc với `pip`:

```bash
pip install rq redis
```

Có 2 package:

* `rq`: thư viện Redis Queue
* `redis`: Redis client cho Python

Kiểm tra:

```bash
python -c "import rq, redis; print(rq.__version__)"
```

---

# 2. Redis Server

RQ cần một **Redis server đang chạy**.

Kiểm tra Redis:

```bash
redis-server --version
```

Sau đó chạy:

```bash
redis-server
```

Nếu thành công, bạn sẽ thấy Redis lắng nghe mặc định tại:

```text
127.0.0.1:6379
```

Mở terminal khác và kiểm tra:

```bash
redis-cli ping
```

Kết quả:

```text
PONG
```

Đây là dấu hiệu:

```text
Python ──────► Redis
               │
               └── đang hoạt động
```

---

# 3. Kết nối Redis bằng Python

Tạo:

```text
project/
├── pyproject.toml
└── main.py
```

`main.py`:

```python
from redis import Redis

redis = Redis(
    host="localhost",
    port=6379,
    db=0,
)

print(redis.ping())
```

Chạy:

```bash
python main.py
```

Kết quả:

```text
True
```

Ở đây:

```python
Redis(
    host="localhost",
    port=6379,
    db=0,
)
```

nghĩa là Python kết nối đến:

```text
localhost
   │
   └── port 6379
          │
          ▼
        Redis
```

---

# 4. Tạo Queue

Bây giờ chúng ta sử dụng RQ.

```python
from redis import Redis
from rq import Queue

redis = Redis(
    host="localhost",
    port=6379,
    db=0,
)

queue = Queue(
    "default",
    connection=redis,
)

print(queue)
```

Ta vừa tạo Queue có tên:

```text
default
```

Kiến trúc:

```text
Python
  │
  ▼
Queue("default")
  │
  ▼
Redis
```

---

# 5. Tạo Job

Tạo file:

```text
tasks.py
```

```python
def say_hello():
    print("Hello from RQ!")
```

Sau đó `main.py`:

```python
from redis import Redis
from rq import Queue

from tasks import say_hello


redis = Redis(
    host="localhost",
    port=6379,
)

queue = Queue(
    "default",
    connection=redis,
)

job = queue.enqueue(say_hello)

print("Job ID:", job.id)
```

Chạy:

```bash
python main.py
```

Ví dụ:

```text
Job ID: 8f6c0f8c-...
```

Điều quan trọng:

**Lúc này `say_hello()` chưa chạy.**

Chúng ta chỉ mới:

```text
Producer
   │
   │ enqueue(say_hello)
   ▼
Redis
   │
   ▼
Job
```

---

# 6. Worker

Mở terminal khác.

Chạy:

```bash
rq worker
```

Worker sẽ kết nối vào Redis và Queue `default`.

Bạn sẽ thấy đại loại:

```text
Worker ... started
Listening on default...
```

Sau đó Worker phát hiện Job:

```text
Job
 │
 ▼
Worker
 │
 ▼
say_hello()
```

Terminal Worker sẽ xuất hiện:

```text
Hello from RQ!
```

🎉 Đây chính là **RQ Job đầu tiên**.

---

# 7. Toàn bộ hệ thống

Bây giờ bạn có 3 thành phần:

### Terminal 1

```bash
redis-server
```

```text
Redis
```

### Terminal 2

```bash
rq worker
```

```text
RQ Worker
```

### Terminal 3

```bash
python main.py
```

```text
Producer
```

Luồng thực tế:

```text
                  ┌──────────────┐
                  │   Producer   │
                  │  main.py     │
                  └──────┬───────┘
                         │
                    enqueue()
                         │
                         ▼
                  ┌──────────────┐
                  │    Redis     │
                  │              │
                  │   default    │
                  └──────┬───────┘
                         │
                      Job
                         │
                         ▼
                  ┌──────────────┐
                  │  RQ Worker   │
                  └──────┬───────┘
                         │
                         ▼
                    say_hello()
```

---

# 8. Một điểm cực kỳ quan trọng

Đây:

```python
queue.enqueue(say_hello)
```

**không giống**:

```python
say_hello()
```

### Cách 1

```python
say_hello()
```

Function chạy ngay:

```text
Python Process
     │
     ▼
say_hello()
```

### Cách 2

```python
queue.enqueue(say_hello)
```

Function được đưa vào Job:

```text
Python
  │
  ▼
enqueue
  │
  ▼
Redis
  │
  ▼
Worker
  │
  ▼
say_hello()
```

Đây là tư duy quan trọng nhất của RQ.

---

# 9. Queue có thể kiểm tra

Ta có thể xem Queue:

```python
print(queue.count)
```

Ví dụ:

```text
5
```

nghĩa là hiện có 5 Job đang chờ.

Ta cũng có thể:

```python
print(queue.name)
```

Kết quả:

```text
default
```

---

# 10. Bài tập thực hành

Tạo:

```text
tasks.py
```

với:

```python
def download_file(filename):
    print(f"Downloading {filename}")
```

Sau đó enqueue 3 Job:

```text
file1.zip
file2.zip
file3.zip
```

Mục tiêu:

```text
Producer
   │
   ├── Job 1 → download_file("file1.zip")
   ├── Job 2 → download_file("file2.zip")
   └── Job 3 → download_file("file3.zip")
             │
             ▼
           Redis
             │
             ▼
           Worker
```

Bạn chạy:

```bash
python main.py
```

sau đó:

```bash
rq worker
```

và quan sát Worker xử lý lần lượt 3 Job.

---

## 🧠 Sau Buổi 2 cần nắm chắc

Bạn cần hiểu rõ 6 thứ:

```text
Redis
RQ
Queue
Job
Producer
Worker
```

và đặc biệt:

```python
queue.enqueue(function)
```

có nghĩa:

> **Không chạy function ngay; tạo một Job để Worker xử lý sau.**

**Buổi 3** chúng ta sẽ đi sâu vào **Job + arguments + return value**, ví dụ:

```python
job = queue.enqueue(
    add,
    10,
    20,
)
```

rồi lấy kết quả:

```python
job.result
```

và hiểu chính xác **RQ serialize function/arguments như thế nào**.
