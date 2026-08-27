# Buổi 3 — Job, Arguments và Result trong RQ

Ở buổi trước, chúng ta đã biết:

```python
queue.enqueue(function)
```

Hôm nay ta sẽ học cách đưa **dữ liệu vào Job** và lấy **kết quả từ Job**.

Mục tiêu:

```text
Producer
   │
   │ function + arguments
   ▼
 Redis
   │
   ▼
 Worker
   │
   │ execute
   ▼
 Result
```

---

# 1. Job là gì?

Khi bạn viết:

```python
job = queue.enqueue(add, 10, 20)
```

RQ tạo ra một object `Job`.

```python
print(job)
```

Ta có thể lấy ID:

```python
print(job.id)
```

Ví dụ:

```text
8f4a3c7e-...
```

ID này dùng để xác định **một Job cụ thể**.

---

# 2. Function nhận arguments

Tạo `tasks.py`:

```python
def add(a, b):
    return a + b
```

Producer:

```python
from redis import Redis
from rq import Queue

from tasks import add


redis = Redis(
    host="localhost",
    port=6379,
)

queue = Queue(
    "default",
    connection=redis,
)

job = queue.enqueue(add, 10, 20)

print("Job ID:", job.id)
```

Chạy:

```bash
python main.py
```

Worker:

```bash
rq worker
```

Worker sẽ thực hiện:

```python
add(10, 20)
```

và function trả về:

```text
30
```

---

# 3. `enqueue()` truyền arguments như thế nào?

Cú pháp:

```python
queue.enqueue(
    function,
    arg1,
    arg2,
    arg3,
)
```

Ví dụ:

```python
queue.enqueue(
    add,
    10,
    20,
)
```

tương đương Worker sẽ chạy:

```python
add(10, 20)
```

---

# 4. Keyword arguments

Function:

```python
def greet(name, age):
    return f"{name} is {age} years old"
```

Ta có thể:

```python
job = queue.enqueue(
    greet,
    name="An",
    age=30,
)
```

Worker thực hiện:

```python
greet(
    name="An",
    age=30,
)
```

Kết quả:

```text
An is 30 years old
```

---

# 5. Positional + keyword arguments

Có thể kết hợp:

```python
def create_user(name, age, city):
    return f"{name}, {age}, {city}"
```

```python
job = queue.enqueue(
    create_user,
    "An",
    age=30,
    city="HCM",
)
```

Worker thực hiện:

```python
create_user(
    "An",
    age=30,
    city="HCM",
)
```

---

# 6. Job có kết quả

Đây là phần rất quan trọng.

Function:

```python
def multiply(a, b):
    return a * b
```

Producer:

```python
job = queue.enqueue(
    multiply,
    10,
    20,
)
```

Worker chạy:

```python
multiply(10, 20)
```

Function trả:

```text
200
```

RQ lưu result của Job.

Sau đó Producer có thể lấy:

```python
print(job.result)
```

Kết quả:

```text
200
```

---

# 7. Nhưng có một vấn đề

Ngay sau:

```python
job = queue.enqueue(multiply, 10, 20)

print(job.result)
```

**không đảm bảo** kết quả đã có.

Vì:

```text
Producer
   │
   │ enqueue()
   ▼
 Redis
   │
   │ Job
   ▼
 Worker
   │
   │ multiply()
   ▼
  200
```

Producer và Worker chạy độc lập.

Có thể Producer chạy nhanh hơn Worker.

Ví dụ:

```python
job = queue.enqueue(multiply, 10, 20)

print(job.result)
```

có thể nhận:

```text
None
```

vì Worker chưa hoàn thành.

---

# 8. Kiểm tra trạng thái Job

RQ cung cấp:

```python
job.get_status()
```

Ví dụ:

```python
print(job.get_status())
```

Có thể nhận:

```text
queued
```

hoặc:

```text
started
```

hoặc:

```text
finished
```

hoặc:

```text
failed
```

---

# 9. Job lifecycle

Hãy nhớ lifecycle này:

```text
             enqueue()
                │
                ▼
             QUEUED
                │
                ▼
             STARTED
                │
                ▼
            FINISHED
```

Nếu lỗi:

```text
             QUEUED
                │
                ▼
             STARTED
                │
                ▼
             FAILED
```

Đây là nền tảng để sau này học:

* retry
* failure handling
* monitoring
* dashboard

---

# 10. Chờ Job hoàn thành

Trong những trường hợp cần chờ kết quả, ta có thể sử dụng:

```python
job = queue.enqueue(
    multiply,
    10,
    20,
)

job.latest_result()
```

Tuy nhiên, trong ứng dụng thực tế **không nên biến RQ thành một RPC đồng bộ** bằng cách enqueue rồi chờ ngay lập tức.

Mục đích chính của RQ là:

```text
Request
   │
   ▼
enqueue Job
   │
   ▼
trả response ngay
```

Sau đó:

```text
Worker
   │
   ▼
xử lý background
```

---

# 11. Một ví dụ thực tế hơn

Giả sử crawler:

```python
def crawl(url):
    print(f"Crawling {url}")
    return {
        "url": url,
        "status": 200,
    }
```

Producer:

```python
job = queue.enqueue(
    crawl,
    "https://example.com",
)
```

Worker chạy:

```python
crawl("https://example.com")
```

và nhận:

```python
{
    "url": "https://example.com",
    "status": 200,
}
```

RQ lưu kết quả Job.

Ta có thể truy cập:

```python
job.result
```

---

# 12. Job ID rất quan trọng

Giả sử bạn enqueue:

```python
job = queue.enqueue(
    crawl,
    "https://example.com",
)
```

RQ tạo:

```text
Job ID
    │
    ▼
8a4e...
```

Bạn có thể lưu Job ID vào database:

```text
crawl_tasks
────────────────────────
id
url
rq_job_id
status
created_at
```

Ví dụ:

```text
1 | https://example.com | 8a4e... | queued
2 | https://example.org | 91bc... | started
3 | https://example.net | 72fd... | finished
```

Đây chính là cách rất hữu ích khi xây dựng **Crawler Dashboard**.

---

# 13. Lấy Job bằng ID

Nếu chỉ có Job ID:

```python
job_id = "8a4e..."
```

có thể lấy Job:

```python
from rq.job import Job

job = Job.fetch(
    job_id,
    connection=redis,
)
```

Sau đó:

```python
print(job.get_status())
```

hoặc:

```python
print(job.result)
```

Điều này rất quan trọng.

Ví dụ:

```text
PySide6 Dashboard
       │
       │ Job ID
       ▼
      Redis
       │
       ▼
      RQ Job
```

Dashboard không nhất thiết phải giữ object `Job` từ lúc enqueue.

Nó chỉ cần lưu:

```text
job_id
```

rồi fetch lại khi cần.

---

# 14. Serialization — một khái niệm quan trọng

RQ cần đưa thông tin Job vào Redis.

Ví dụ:

```python
queue.enqueue(
    add,
    10,
    20,
)
```

Thông tin cần được lưu:

```text
function
arguments
keyword arguments
job metadata
```

RQ sử dụng serialization để lưu dữ liệu.

Vì vậy **không phải object Python nào cũng phù hợp để truyền vào Job**.

Ví dụ đơn giản:

```python
queue.enqueue(
    add,
    10,
    20,
)
```

rất tốt.

Các kiểu dữ liệu thông thường:

```python
str
int
float
bool
None
list
dict
tuple
```

thường dễ xử lý.

Nhưng với object phức tạp, chúng ta phải đặc biệt chú ý serialization.

Buổi sau chúng ta sẽ đào sâu phần này.

---

# 15. Sai lầm rất phổ biến

❌ Sai:

```python
queue.enqueue(
    add(10, 20)
)
```

Bạn vừa **gọi function trước**.

Python sẽ thực hiện:

```python
add(10, 20)
```

rồi truyền kết quả `30` vào `enqueue()`.

---

### Đúng:

```python
queue.enqueue(
    add,
    10,
    20,
)
```

Nghĩa là:

```text
function = add
args = (10, 20)
```

Worker mới thực hiện:

```python
add(10, 20)
```

---

# 16. Một ví dụ hoàn chỉnh

### `tasks.py`

```python
def calculate(a, b):
    return a * b
```

### `main.py`

```python
from redis import Redis
from rq import Queue

from tasks import calculate


redis = Redis(
    host="localhost",
    port=6379,
)

queue = Queue(
    "default",
    connection=redis,
)

job = queue.enqueue(
    calculate,
    10,
    20,
)

print("Job ID:", job.id)
print("Status:", job.get_status())
```

Chạy Worker:

```bash
rq worker
```

Sau khi Worker hoàn thành, bạn có thể fetch Job:

```python
from rq.job import Job

job = Job.fetch(
    job.id,
    connection=redis,
)

print(job.result)
```

Kết quả:

```text
200
```

---

# 🧠 Tổng kết Buổi 3

Bạn cần phân biệt:

```python
queue.enqueue(
    function,
    *args,
    **kwargs,
)
```

và:

```python
function(*args, **kwargs)
```

RQ Job có:

```text
Job
 ├── id
 ├── function
 ├── arguments
 ├── status
 ├── result
 └── exception information
```

Lifecycle:

```text
QUEUED
   │
   ▼
STARTED
   │
   ▼
FINISHED
```

hoặc:

```text
QUEUED
   │
   ▼
STARTED
   │
   ▼
FAILED
```

### 🎯 Bài tập

Viết một Job:

```python
def calculate_price(price, quantity):
    return price * quantity
```

Enqueue:

```text
price = 150_000
quantity = 3
```

Sau đó:

1. In `job.id`
2. In `job.get_status()`
3. Chạy Worker
4. Lấy lại Job bằng `Job.fetch()`
5. In `job.result`

**Buổi 4** chúng ta sẽ học sâu về **Job arguments + serialization**: tại sao truyền `dict/list/dataclass` được, tại sao `lambda`, local function, một số object không truyền được, và cách thiết kế `tasks.py` đúng để Worker có thể import và chạy Job ổn định.
