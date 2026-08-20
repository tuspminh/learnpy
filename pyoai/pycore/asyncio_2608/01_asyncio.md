Được. Tôi sẽ dạy bạn **Asyncio theo kiểu Deep Dive** , không chỉ học cú pháp mà đi từ mô hình thực thi → event loop → coroutine → task → cancellation → timeout → queue → semaphore → producer/consumer → HTTP → thiết kế ứng dụng async thực tế.

Vì bạn đã học `ThreadPoolExecutor`, `ProcessPoolExecutor`, Thread và đang xây các ứng dụng crawl/worker Python, tôi sẽ đặc biệt nhấn mạnh **asyncio khác Thread/Process ở đâu và khi nào nên dùng cái nào**.

# Khóa học Asyncio Deep Dive — Python

## Phần I — Nền tảng Asyncio

  1. **Buổi 1 — Asyncio là gì?**

     * Synchronous vs Asynchronous

     * Blocking vs Non-blocking

     * I/O-bound vs CPU-bound

     * Vì sao asyncio tồn tại?

     * Asyncio khác Thread/Process

     * Event Loop

     * Coroutine

     * `async` / `await`

     * Chương trình async đầu tiên

  2. **Buổi 2 — Coroutine Deep Dive**

     * Coroutine function

     * Coroutine object

     * Coroutine lifecycle

     * `async def`

     * `await`

     * Coroutine chưa chạy ngay

     * Coroutine execution

  3. **Buổi 3 — Event Loop Deep Dive**

     * Event Loop thực chất làm gì?

     * `asyncio.run()`

     * Scheduling

     * Ready queue

     * I/O waiting

     * Event loop lifecycle

     * `get_running_loop()`

  4. **Buổi 4 — Task**

     * `asyncio.create_task()`

     * Coroutine vs Task

     * Task scheduling

     * Task state

     * `Task.result()`

     * `Task.exception()`

  5. **Buổi 5 — Chạy nhiều coroutine**

     * Tuần tự

     * Concurrent

     * `asyncio.gather()`

     * `asyncio.wait()`

     * `asyncio.as_completed()`

     * Khi nào dùng cái nào?




* * *

# Phần II — Async Control Flow

  6. **Buổi 6 —`await` Deep Dive**

  7. **Buổi 7 — Sleep và cooperative scheduling**

  8. **Buổi 8 — Timeout**

     * `asyncio.timeout()`

     * `asyncio.wait_for()`

  9. **Buổi 9 — Cancellation**

     * `Task.cancel()`

     * `CancelledError`

     * Cancellation propagation

     * Cleanup

  10. **Buổi 10 — Exception trong Asyncio**

     * Exception trong coroutine

     * Exception trong Task

     * `gather()`

     * `return_exceptions`

     * Exception propagation




* * *

# Phần III — Synchronization

  11. **Buổi 11 —`asyncio.Lock`**

  12. **Buổi 12 —`asyncio.Event`**

  13. **Buổi 13 —`asyncio.Condition`**

  14. **Buổi 14 —`asyncio.Semaphore`**

  15. **Buổi 15 —`asyncio.BoundedSemaphore`**




Đây là phần cực kỳ quan trọng khi bạn xây **crawler**.

Ví dụ:
    
    
    1000 URL
       │
       ▼
    ┌─────────────────┐
    │ asyncio crawler │
    └────────┬────────┘
             │
             ▼
     Semaphore(20)
             │
        ┌────┴────┐
        ▼         ▼
     worker     worker
        │         │
        ▼         ▼
     HTTP       HTTP

* * *

# Phần IV — Async Queue & Worker

  16. **Buổi 16 —`asyncio.Queue`**

  17. **Buổi 17 — Producer / Consumer**

  18. **Buổi 18 — Multiple Workers**

  19. **Buổi 19 — Backpressure**

  20. **Buổi 20 — Graceful Shutdown**

  21. **Buổi 21 — Worker Pool**

  22. **Buổi 22 — Retry**

  23. **Buổi 23 — Rate Limiting**




Phần này sẽ liên hệ trực tiếp với **crawl-worker / queue server** mà bạn đang học.

* * *

# Phần V — Async HTTP

  24. **Buổi 24 — HTTP async**

  25. **Buổi 25 —`aiohttp`**

  26. **Buổi 26 — HTTP connection pool**

  27. **Buổi 27 — Concurrent requests**

  28. **Buổi 28 — Timeout / Retry HTTP**

  29. **Buổi 29 — Rate limit crawler**

  30. **Buổi 30 — Async Crawler**




* * *

# Phần VI — Async Database

  31. SQLite + asyncio

  32. `aiosqlite`

  33. Async Repository

  34. Transaction

  35. Connection management

  36. Concurrent database operations

  37. Async Unit of Work

  38. Async crawler + SQLite




* * *

# Phần VII — Async File & Stream

  39. Async file I/O

  40. Stream

  41. Async generator

  42. `async for`

  43. `async with`

  44. Async context manager

  45. Async iterator




* * *

# Phần VIII — Asyncio nâng cao

  46. `TaskGroup`

  47. Structured Concurrency

  48. `ExceptionGroup`

  49. `except*`

  50. Shielding

  51. Cancellation scopes

  52. Debug mode

  53. Asyncio performance

  54. Detect blocking code

  55. `to_thread()`

  56. `run_in_executor()`




* * *

# Phần IX — Async Architecture

  57. Async Service

  58. Async Repository Pattern

  59. Async Worker Architecture

  60. Async Pipeline

  61. Producer → Queue → Worker → Storage

  62. Retry architecture

  63. Rate limiter

  64. Graceful shutdown

  65. Signal handling

  66. Logging async application

  67. Testing async code




* * *

# Phần X — Project thực tế

### Project 1 — Async URL Checker
    
    
    urls.txt
       │
       ▼
    Producer
       │
       ▼
    asyncio.Queue
       │
       ├── Worker 1
       ├── Worker 2
       ├── Worker 3
       └── Worker N
              │
              ▼
           HTTP
              │
              ▼
           Result

### Project 2 — Async Web Crawler
    
    
    URL
     │
     ▼
    Scheduler
     │
     ▼
    Queue
     │
     ├── Worker
     ├── Worker
     ├── Worker
     └── Worker
          │
          ▼
        HTTP
          │
          ▼
     Parser
          │
          ▼
     SQLite

### Project 3 — Async Crawl Worker Framework

Cuối khóa chúng ta sẽ ghép những thứ bạn đã học:
    
    
                 ┌──────────────┐
                 │ Crawl Server │
                 └──────┬───────┘
                        │
                        ▼
                 asyncio.Queue
                        │
            ┌───────────┼───────────┐
            ▼           ▼           ▼
        Worker 1     Worker 2    Worker 3
            │           │           │
            └───────────┼───────────┘
                        ▼
                     Crawler
                        │
                        ▼
                     Parser
                        │
                        ▼
                   Repository
                        │
                        ▼
                     SQLite

* * *

# Cách tôi sẽ dạy mỗi buổi

Mỗi buổi sẽ có cấu trúc:

  1. **Concept**

  2. **Mental model**

  3. **Syntax**

  4. **Ví dụ nhỏ**

  5. **Phân tích từng dòng**

  6. **So sánh với synchronous**

  7. **So sánh với Thread**

  8. **Pitfall thường gặp**

  9. **Bài tập**

  10. **Mini project**




Đặc biệt tôi sẽ tránh kiểu học:

> `async def` là hàm bất đồng bộ → `await` dùng để chờ → hết.

Thay vào đó chúng ta sẽ hiểu **event loop thực sự chạy chương trình như thế nào**.

* * *

# Buổi 1 — Asyncio là gì?

Hãy bắt đầu từ một vấn đề rất đơn giản.

Giả sử chúng ta có:
    
    
    import time
    
    
    def task(name):
        print(f"{name}: start")
        time.sleep(2)
        print(f"{name}: done")
    
    
    task("A")
    task("B")
    task("C")

Thời gian chạy xấp xỉ:
    
    
    A start
        ↓ 2s
    A done
    B start
        ↓ 2s
    B done
    C start
        ↓ 2s
    C done
    
    ≈ 6 giây

Vấn đề là trong lúc A đang:
    
    
    time.sleep(2)

CPU không cần phải làm gì với task A.

Đây là **I/O-bound waiting**.

Ví dụ thực tế:
    
    
    HTTP request
         ↓
    chờ server
         ↓
    database query
         ↓
    chờ database
         ↓
    đọc network
         ↓
    chờ network

Nếu ta có hàng trăm request, việc chờ tuần tự sẽ rất lãng phí.

* * *

# Asyncio giải quyết chuyện này thế nào?

Asyncio cho phép một thread chạy nhiều công việc **cooperatively**.

Ví dụ:
    
    
    Task A ── request ─────────────── response
                  │
                  │ waiting
                  ▼
    Task B ── request ───── response
                  │
                  ▼
    Task C ── request ───────── response

Thay vì:
    
    
    A █████████████████
    B                  █████████████████
    C                                   █████████████████

ta có:
    
    
    A ███───────wait────────███
    B     ███────wait──────████
    C         ███────wait──────███

**Một thread có thể chuyển sang task khác trong lúc task hiện tại đang chờ I/O.**

Đây chính là ý tưởng cốt lõi của asyncio.

* * *

# Asyncio không phải là Thread

Đây là điểm bạn cần ghi nhớ.

### Thread
    
    
    Thread 1 ── Task A
    Thread 2 ── Task B
    Thread 3 ── Task C

Hệ điều hành scheduler quyết định thread nào chạy.

### Asyncio
    
    
                 Event Loop
                     │
           ┌─────────┼─────────┐
           ▼         ▼         ▼
         Task A    Task B    Task C
           │         │         │
           └─────────┼─────────┘
                     │
                  1 thread

Các coroutine **tự nhường quyền** tại những điểm `await`.

Đây gọi là:

> **Cooperative multitasking**

* * *

# Ví dụ Asyncio đầu tiên
    
    
    import asyncio
    
    
    async def hello():
        print("Hello")
        await asyncio.sleep(2)
        print("World")
    
    
    asyncio.run(hello())

Có 3 thứ quan trọng:

### 1\. `async def`
    
    
    async def hello():

Định nghĩa một **coroutine function**.

* * *

### 2\. `await`
    
    
    await asyncio.sleep(2)

Nói đơn giản:

> "Trong lúc tôi đang chờ, hãy cho event loop cơ hội chạy công việc khác."

* * *

### 3\. `asyncio.run()`
    
    
    asyncio.run(hello())

Đây là entry point thông thường của một chương trình asyncio.

Nó tạo và chạy event loop, thực thi coroutine chính, rồi đóng loop khi hoàn thành.

* * *

# Một ví dụ quan trọng hơn
    
    
    import asyncio
    
    
    async def task(name, delay):
        print(f"{name}: start")
    
        await asyncio.sleep(delay)
    
        print(f"{name}: done")
    
    
    async def main():
        await task("A", 2)
        await task("B", 2)
        await task("C", 2)
    
    
    asyncio.run(main())

Bạn có thể nghĩ rằng asyncio sẽ chạy đồng thời.

**Không.**

Đoạn này vẫn gần:
    
    
    A ████████
             B ████████
                      C ████████

≈ 6 giây.

Tại sao?

Vì:
    
    
    await task("A", 2)

đang **chờ A hoàn thành** rồi mới chạy B.

* * *

# Muốn concurrent thì sao?

Ta tạo Task:
    
    
    import asyncio
    
    
    async def task(name, delay):
        print(f"{name}: start")
    
        await asyncio.sleep(delay)
    
        print(f"{name}: done")
    
    
    async def main():
        tasks = [
            asyncio.create_task(task("A", 2)),
            asyncio.create_task(task("B", 2)),
            asyncio.create_task(task("C", 2)),
        ]
    
        await asyncio.gather(*tasks)
    
    
    asyncio.run(main())

Bây giờ:
    
    
    A start
    B start
    C start
    
        ↓↓↓ cùng chờ
    
    A done
    B done
    C done

Thời gian khoảng:
    
    
    ≈ 2 giây

thay vì:
    
    
    ≈ 6 giây

Đây chính là sức mạnh lớn nhất của asyncio đối với các workload **I/O-bound**.

* * *

# Mental model quan trọng nhất

Hãy nhớ chuỗi này:
    
    
    async def
       │
       ▼
    Coroutine
       │
       ▼
    Task
       │
       ▼
    Event Loop
       │
       ├── chạy Task A
       │
       ├── A gặp await
       │
       ├── chuyển sang Task B
       │
       ├── B gặp await
       │
       ├── chuyển sang Task C
       │
       └── quay lại A khi I/O sẵn sàng

Đây là nền tảng của toàn bộ khóa học.

* * *

# Một hiểu lầm rất phổ biến

Không phải cứ viết:
    
    
    async def download():
        ...

thì code tự động nhanh hơn.

Ví dụ:
    
    
    async def bad():
        time.sleep(5)

Đây là **code blocking**.

Nó sẽ chặn event loop.

Trong async code, thay vì:
    
    
    time.sleep(5)

thường phải dùng:
    
    
    await asyncio.sleep(5)

Tương tự với HTTP, database, file I/O... chúng ta cần các API async phù hợp hoặc đưa phần blocking sang thread/executor khi cần.

* * *

# Asyncio phù hợp với gì?

Rất phù hợp:
    
    
    HTTP requests
    Web crawler
    API server
    WebSocket
    Database I/O
    Network service
    Queue worker
    大量 concurrent connections

Không phải lựa chọn chính cho:
    
    
    CPU calculation nặng
    Image processing CPU-bound
    Machine learning CPU-bound
    Video encoding CPU-bound

Với CPU-bound, chúng ta thường xem xét:
    
    
    ProcessPoolExecutor
    multiprocessing
    native extensions

Đây cũng là lý do việc bạn học `ThreadPoolExecutor` và `ProcessPoolExecutor` trước đó rất hữu ích: chúng ta sẽ ghép chúng với asyncio ở phần nâng cao.

* * *

# Bài tập Buổi 1

### Bài 1

Viết chương trình:
    
    
    Task A: sleep 3s
    Task B: sleep 2s
    Task C: sleep 1s

Chạy tuần tự.

Đo thời gian.

* * *

### Bài 2

Chuyển sang:
    
    
    asyncio.create_task()
    asyncio.gather()

Đo thời gian lại.

Dự đoán trước kết quả:
    
    
    Sequential: ~6s
    Concurrent: ~3s

* * *

### Bài 3 — Quan trọng

Thử:
    
    
    async def task(name):
        print(f"{name} start")
        time.sleep(2)
        print(f"{name} done")

sau đó chạy bằng `create_task()`.

Quan sát xem tại sao nó **không còn concurrent như bạn mong đợi**.

Đây là bài tập rất quan trọng để hiểu bản chất asyncio.

* * *

## Buổi 2

Tiếp theo chúng ta sẽ đi sâu vào:

**Coroutine thực chất là gì?**

Ta sẽ phân biệt thật rõ:
    
    
    async function
          ↓
    coroutine function
          ↓
    coroutine object
          ↓
    await coroutine
          ↓
    Task
          ↓
    Event Loop

Đây là chỗ rất nhiều người học asyncio bị nhầm giữa **coroutine và task**.