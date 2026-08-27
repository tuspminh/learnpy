Được. Tôi sẽ dạy bạn **Redis Queue (RQ) với Python từ cơ bản → nâng cao → xây dựng hệ thống worker thực tế**.

RQ rất phù hợp với những project bạn đang học như **crawler, TTS, xử lý file, background job**.

# 🧭 Roadmap học Redis Queue (RQ)

## Phần I — Nền tảng

1. **Buổi 1 — RQ là gì?**

   * Redis là gì?
   * Queue là gì?
   * Background Job
   * Producer / Worker / Queue
   * RQ hoạt động như thế nào?
   * Job lifecycle

2. **Buổi 2 — Cài đặt RQ + Redis**

   * Redis server
   * `redis-py`
   * `rq`
   * Kết nối Redis
   * Chạy RQ Worker

3. **Buổi 3 — Job đầu tiên**

   * `Queue`
   * `queue.enqueue()`
   * Worker
   * Function → Job
   * Job ID

4. **Buổi 4 — Job arguments**

   * positional arguments
   * keyword arguments
   * truyền object
   * serialization

5. **Buổi 5 — Job Result**

   * `Job`
   * `job.result`
   * `job.return_value()`
   * trạng thái Job

---

# Phần II — Job Lifecycle

6. **Buổi 6 — Job Status**

   * `queued`
   * `started`
   * `finished`
   * `failed`
   * `deferred`
   * `scheduled`

7. **Buổi 7 — Job Timeout**

   * timeout
   * execution timeout
   * job bị kill
   * xử lý timeout

8. **Buổi 8 — Retry**

   * retry job
   * `Retry`
   * số lần retry
   * retry interval
   * exponential backoff

9. **Buổi 9 — Failure Handling**

   * FailedJobRegistry
   * exception
   * traceback
   * failed job cleanup

10. **Buổi 10 — Job Cancellation**

    * cancel job
    * cancel queued job
    * stop job

---

# Phần III — Queue nâng cao

11. **Buổi 11 — Multiple Queues**

    ```text
    high
    normal
    low
    ```

12. **Buổi 12 — Worker**

    * Worker lifecycle
    * worker name
    * worker registration
    * worker heartbeat

13. **Buổi 13 — Worker Process**

    * worker execution model
    * fork
    * process isolation
    * worker chết giữa Job

14. **Buổi 14 — Worker nhiều queue**

    ```text
    rq worker high normal low
    ```

15. **Buổi 15 — Job Dependencies**

    * Job A → Job B
    * dependency
    * workflow

---

# Phần IV — Scheduling

16. **Buổi 16 — Scheduled Job**
17. **Buổi 17 — Delay Job**
18. **Buổi 18 — Cron + RQ**
19. **Buổi 19 — RQ Scheduler**
20. **Buổi 20 — Periodic Job**

---

# Phần V — Production

21. **Buổi 21 — Redis connection**
22. **Buổi 22 — Redis connection pool**
23. **Buổi 23 — Serialization**
24. **Buổi 24 — Job TTL**
25. **Buổi 25 — Result TTL**
26. **Buổi 26 — Cleanup**
27. **Buổi 27 — Worker graceful shutdown**
28. **Buổi 28 — Monitoring**
29. **Buổi 29 — Logging**
30. **Buổi 30 — RQ Dashboard / monitoring**

---

# Phần VI — Kiến trúc ứng dụng

31. **Buổi 31 — Producer / Consumer Architecture**

```text
Application
     │
     ▼
   Queue
     │
     ▼
   Worker
     │
     ▼
  Service
```

32. **Buổi 32 — RQ + Repository Pattern**

33. **Buổi 33 — RQ + Clean Architecture**

```text
CLI / API
    │
    ▼
Use Case
    │
    ▼
Job Queue
    │
    ▼
Worker
    │
    ▼
Application Service
    │
    ▼
Repository
```

34. **Buổi 34 — RQ + Dependency Injection**

35. **Buổi 35 — Testing RQ**

---

# Phần VII — Project thực tế

### Project 1 — Image Processing Queue

```text
CLI
 │
 ▼
RQ Queue
 │
 ├── resize image
 ├── compress image
 └── convert image
       │
       ▼
    Worker
```

### Project 2 — TTS Queue

Rất phù hợp với project TTS của bạn:

```text
Text File
   │
   ▼
Producer
   │
   ▼
Redis
   │
   ▼
RQ
   │
   ├── TTS Job 1
   ├── TTS Job 2
   ├── TTS Job 3
   └── TTS Job 4
          │
          ▼
       Worker
          │
          ▼
        Audio
```

### Project 3 — Crawler Queue

Đây sẽ là project quan trọng nhất:

```text
                ┌──────────────┐
                │   Dashboard  │
                └──────┬───────┘
                       │
                       ▼
                 ┌───────────┐
                 │  Producer │
                 └─────┬─────┘
                       │
                       ▼
              ┌─────────────────┐
              │      Redis      │
              └────────┬────────┘
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
          Worker 1  Worker 2  Worker 3
             │         │         │
             ▼         ▼         ▼
           Crawler   Crawler   Crawler
             │         │         │
             └─────────┼─────────┘
                       ▼
                    SQLite
```

Sau đó chúng ta có thể nâng cấp thành:

```text
PySide6 Dashboard
        │
        ▼
   Application
        │
        ▼
   RQ Producer
        │
        ▼
      Redis
        │
   ┌────┼────┐
   ▼    ▼    ▼
  W1   W2    W3
   │    │    │
   └────┼────┘
        ▼
   Story Sources
        │
        ▼
      SQLite
```

---

# 🎯 Cách tôi sẽ dạy

Mỗi buổi sẽ theo cấu trúc:

1. **Concept**
2. **Kiến trúc bên trong**
3. **Code tối thiểu**
4. **Giải thích từng dòng**
5. **Thực hành**
6. **Bài tập**
7. **Sai lầm thường gặp**
8. **Best Practice**
9. **Mini project**

Và tôi sẽ ưu tiên **Python thuần + RQ + Redis**, không che giấu cơ chế bằng framework khác.

---

# 🚀 Buổi 1 — RQ là gì?

Trước tiên cần hiểu vấn đề mà RQ giải quyết.

Giả sử bạn có:

```python
def send_email():
    # mất 10 giây
    ...
```

Nếu chạy trực tiếp:

```python
send_email()
print("Done")
```

thì chương trình phải **đợi 10 giây**.

Trong ứng dụng thực tế, ta muốn:

```text
Application
     │
     │ tạo Job
     ▼
   Queue
     │
     │
     ▼
   Worker
     │
     ▼
send_email()
```

Application không cần tự thực hiện công việc nặng.

Nó chỉ nói:

> "Hãy làm việc này sau."

---

## 1. Queue là gì?

Queue là hàng đợi.

Ví dụ:

```text
             Queue
        ┌──────────────┐
        │ Job A        │
        │ Job B        │
        │ Job C        │
        │ Job D        │
        └──────────────┘
```

Worker lấy Job ra:

```text
Queue
 │
 ├── Job A ──────► Worker
 │
 ├── Job B
 │
 ├── Job C
 └── Job D
```

Thông thường:

```text
Producer → Queue → Consumer
```

Trong RQ:

```text
Producer → Redis → RQ Worker
```

---

# 2. Redis nằm ở đâu?

RQ **không phải database**.

RQ sử dụng Redis để lưu/truyền thông tin về Job.

Có thể hình dung:

```text
Python Application
       │
       │ enqueue()
       ▼
      RQ
       │
       ▼
     Redis
       │
       │ Job
       ▼
   RQ Worker
       │
       ▼
    Function
```

Redis đóng vai trò backend cho queue.

---

# 3. Producer là gì?

Producer là chương trình **tạo Job**.

Ví dụ:

```python
queue.enqueue(send_email)
```

Producer không thực hiện:

```python
send_email()
```

mà thực hiện:

```python
queue.enqueue(send_email)
```

Nghĩa là:

> Đưa công việc `send_email` vào Queue.

---

# 4. Worker là gì?

Worker là process chuyên lấy Job từ Queue và thực hiện.

```text
Redis
  │
  │ lấy Job
  ▼
Worker
  │
  ▼
send_email()
```

Một Worker có thể xử lý rất nhiều Job:

```text
Job 1 ──► Worker
Job 2 ──► Worker
Job 3 ──► Worker
Job 4 ──► Worker
```

---

# 5. RQ viết tắt của gì?

**RQ = Redis Queue**

Đây là thư viện Python dùng Redis làm backend cho background jobs.

Điểm mạnh của RQ là API khá đơn giản.

Ví dụ conceptually:

```python
queue.enqueue(my_function, 10, 20)
```

RQ sẽ biến lời gọi đó thành một Job.

Worker sau đó thực hiện tương đương:

```python
my_function(10, 20)
```

---

# 6. Một Job thực chất là gì?

Ví dụ:

```python
def add(a, b):
    return a + b
```

Ta enqueue:

```python
job = queue.enqueue(add, 10, 20)
```

RQ tạo một Job đại diện cho:

```text
function = add
args     = (10, 20)
```

Worker lấy Job:

```text
Job
 │
 ├── function: add
 ├── args: (10, 20)
 │
 ▼
add(10, 20)
 │
 ▼
30
```

Đây là khái niệm **cực kỳ quan trọng** khi học RQ.

---

# 7. RQ khác ThreadPoolExecutor thế nào?

Bạn đã học `ThreadPoolExecutor`, nên đây là điểm cần phân biệt.

### ThreadPoolExecutor

```text
Python Process
 │
 ├── Thread 1
 ├── Thread 2
 └── Thread 3
```

Queue nằm **trong memory của process**.

### RQ

```text
Application
     │
     ▼
   Redis
     │
     ├── Worker 1
     ├── Worker 2
     └── Worker 3
```

Queue nằm bên ngoài process.

Do đó:

```text
Application chết
      ↓
Redis vẫn còn Job
      ↓
Worker khác có thể tiếp tục xử lý
```

Đây chính là một trong những giá trị lớn của Job Queue.

---

# 8. RQ khác `asyncio` thế nào?

`asyncio` chủ yếu giải quyết:

```text
Một process
     │
     ├── coroutine A
     ├── coroutine B
     └── coroutine C
```

RQ giải quyết:

```text
Process A
    │
    ▼
 Redis Queue
    │
    ├── Worker 1
    ├── Worker 2
    └── Worker 3
```

Có thể kết hợp cả hai.

Ví dụ:

```text
RQ
 │
 ▼
Worker
 │
 ▼
asyncio
 │
 ├── HTTP request
 ├── HTTP request
 └── HTTP request
```

Sau này chúng ta sẽ học trường hợp này.

---

# 9. Mental Model cần nhớ

Hãy nhớ đúng 5 thành phần:

```text
┌────────────┐
│  Producer  │
└─────┬──────┘
      │
      │ enqueue Job
      ▼
┌────────────┐
│   Queue    │
└─────┬──────┘
      │
      │ Redis
      ▼
┌────────────┐
│   Worker   │
└─────┬──────┘
      │
      ▼
┌────────────┐
│  Function  │
└────────────┘
```

Trong RQ:

* **Producer** → Python application
* **Queue** → RQ Queue
* **Backend** → Redis
* **Worker** → RQ Worker
* **Job** → công việc cần thực hiện

---

# 🧪 Bài tập Buổi 1

Chưa cần code RQ.

Hãy tự phân tích 3 bài toán:

### Bài 1

Một API nhận request:

```text
POST /send-email
```

Gửi email mất 5 giây.

Hãy thiết kế:

```text
API → ? → ? → send_email()
```

### Bài 2

Crawler cần crawl 10.000 URL.

Thiết kế:

```text
10.000 URL
      ↓
     ???
      ↓
Workers
```

### Bài 3

App TTS của bạn nhận:

```text
book.txt
```

và phải tạo:

```text
book.mp3
```

Thời gian xử lý 10 phút.

Thiết kế:

```text
CLI
 ↓
???
 ↓
???
 ↓
TTS
```

**Buổi 2** chúng ta sẽ bắt đầu cài **Redis + RQ**, chạy Redis server, tạo `Queue`, tạo Worker và chạy **Job đầu tiên** bằng Python.
