# Buổi 6 — `await` Deep Dive & Cooperative Scheduling

Buổi này rất quan trọng. Từ đây chúng ta không chỉ **dùng** `asyncio`, mà bắt đầu hiểu **Event Loop thực sự làm gì khi gặp`await`**.

Sau buổi 6, bạn cần trả lời được:

> Khi Python chạy đến `await asyncio.sleep(1)`, thread hiện tại có bị block không?

> Coroutine dừng ở đâu?

> Ai đánh thức coroutine?

> Event Loop làm thế nào để chạy coroutine khác?

> Vì sao `asyncio` có thể chạy hàng nghìn tác vụ I/O trên một thread?

* * *

# 1\. Ôn lại mental model

Một chương trình asyncio cơ bản:
    
    
    import asyncio
    
    
    async def main():
        print("Hello")
    
        await asyncio.sleep(1)
    
        print("World")
    
    
    asyncio.run(main())

Mental model:
    
    
    asyncio.run()
          │
          ▼
     Event Loop
          │
          ▼
       main()
          │
          ▼
       await
          │
          ▼
     nhường quyền
          │
          ▼
     Event Loop
          │
          ▼
     làm việc khác

Điểm mấu chốt hôm nay:

> `await` là cơ chế cho phép coroutine **tạm dừng và nhường quyền điều khiển**.

* * *

# 2\. `await` không có nghĩa là "chờ theo kiểu blocking"

Đây là hiểu lầm phổ biến nhất khi mới học asyncio.

Bạn thấy:
    
    
    await asyncio.sleep(3)

và nghĩ:
    
    
    Thread đứng yên 3 giây

Không chính xác.

Với asyncio:
    
    
    Coroutine A
        │
        │ await sleep(3)
        ▼
    tạm dừng A
        │
        ▼
    Event Loop lấy quyền điều khiển
        │
        ├── chạy B
        ├── chạy C
        ├── chạy D
        └── xử lý I/O

Thread không bị chặn bởi `asyncio.sleep()`.

* * *

# 3\. `await` thực chất là gì?

Ta có:
    
    
    async def foo():
        result = await something()

Mental model đơn giản:
    
    
    foo()
     │
     ▼
    await something()
     │
     ▼
    "something chưa xong"
     │
     ▼
    tạm suspend foo
     │
     ▼
    Event Loop chạy việc khác

Khi `something` hoàn thành:
    
    
    something done
          │
          ▼
    Event Loop
          │
          ▼
    resume foo
          │
          ▼
    result = ...

* * *

# 4\. `await` là điểm nhường quyền

Đây là khái niệm cực kỳ quan trọng:

> **`await` tạo ra một điểm mà coroutine có thể nhường quyền điều khiển cho Event Loop.**

Ví dụ:
    
    
    async def worker():
        print("A")
    
        await asyncio.sleep(1)
    
        print("B")

Có thể hình dung:
    
    
    worker
      │
      ▼
    print("A")
      │
      ▼
    await sleep(1)
      │
      ├──────► Event Loop
      │
      │      chạy task khác
      │
      ▼
    sleep complete
      │
      ▼
    print("B")

* * *

# 5\. Cooperative Scheduling

Asyncio sử dụng mô hình:

> **Cooperative multitasking**

Khác với OS thread scheduling.

### Thread

Operating System có thể chuyển:
    
    
    Thread A
       ↓
    Thread B
       ↓
    Thread C

theo scheduler.

### asyncio

Các coroutine **hợp tác với nhau** bằng cách `await`.
    
    
    Task A
      │
      ├── chạy
      │
      └── await ─────┐
                      ▼
                  Event Loop
                      │
                      ▼
                   Task B
                      │
                      └── await
                             │
                             ▼
                          Task C

Coroutine phải có điểm nhường quyền.

* * *

# 6\. Một ví dụ chứng minh
    
    
    import asyncio
    
    
    async def worker(name):
        for i in range(3):
            print(name, i)
            await asyncio.sleep(0)
    
    
    async def main():
        await asyncio.gather(
            worker("A"),
            worker("B"),
            worker("C"),
        )
    
    
    asyncio.run(main())

Bạn có thể thấy:
    
    
    A 0
    B 0
    C 0
    A 1
    B 1
    C 1
    A 2
    B 2
    C 2

Tại sao?

Vì:
    
    
    await asyncio.sleep(0)

tạo cơ hội để Event Loop chuyển sang Task khác.

* * *

# 7\. Nếu bỏ `await` thì sao?

Ví dụ:
    
    
    async def worker(name):
        for i in range(3):
            print(name, i)

Sau đó:
    
    
    await asyncio.gather(
        worker("A"),
        worker("B"),
        worker("C"),
    )

Kết quả sẽ có xu hướng:
    
    
    A 0
    A 1
    A 2
    B 0
    B 1
    B 2
    C 0
    C 1
    C 2

Bởi vì coroutine không có điểm nhường quyền trong đoạn đó.

* * *

# 8\. Asyncio không tự biến code thành concurrent

Đây là một nguyên tắc rất quan trọng:
    
    
    async def worker():
        for i in range(10_000_000):
            ...

Không có:
    
    
    await

thì Task có thể chiếm event loop trong thời gian dài.

Mental model:
    
    
    Task A
    ████████████████████████████████████
                                          │
                                          ▼
                                       Task B

Task B phải chờ Task A nhường quyền.

* * *

# 9\. Đây là lý do CPU-bound nguy hiểm

Ví dụ:
    
    
    async def cpu_work():
        total = 0
    
        for i in range(100_000_000):
            total += i
    
        return total

Bạn viết:
    
    
    asyncio.create_task(cpu_work())

không có nghĩa CPU work chạy background như Thread/Process.

Nó vẫn chạy trên event-loop thread.
    
    
    Event Loop Thread
           │
           ▼
    cpu_work()
    ████████████████████████████████
           │
           ▼
    Event Loop bị block
           │
           X
       Task khác không chạy

* * *

# 10\. Asyncio phù hợp với I/O-bound

Ví dụ:
    
    
    async def fetch():
        response = await client.get(url)

Khi network đang chờ:
    
    
    Task
     │
     ▼
    await network I/O
     │
     ▼
    nhường Event Loop
     │
     ├── Task B
     ├── Task C
     ├── Task D
     └── ...

Đây chính là sức mạnh của asyncio.

* * *

# 11\. `asyncio.sleep()` là ví dụ dễ hiểu nhất
    
    
    await asyncio.sleep(5)

Không phải:
    
    
    Thread.sleep(5)

Nó có ý nghĩa gần như:

> "Tôi không có việc gì để làm trong khoảng thời gian này. Event Loop hãy chạy việc khác."

* * *

# 12\. So sánh `time.sleep()` và `asyncio.sleep()`

## Sai trong async code
    
    
    import time
    
    
    async def worker():
        time.sleep(3)

Điều này block event-loop thread.
    
    
    Event Loop
       │
       ▼
    time.sleep(3)
    ████████████████
       │
       X
    Tasks khác không chạy

* * *

## Đúng
    
    
    async def worker():
        await asyncio.sleep(3)
    
    
    Event Loop
       │
       ▼
    await sleep
       │
       ├── Task B
       ├── Task C
       └── Task D

* * *

# 13\. Bài kiểm tra cực kỳ quan trọng

Chạy:
    
    
    import asyncio
    import time
    
    
    async def blocking():
        print("blocking start")
    
        time.sleep(3)
    
        print("blocking done")
    
    
    async def worker():
        for i in range(5):
            print("worker", i)
            await asyncio.sleep(0.5)
    
    
    async def main():
        await asyncio.gather(
            blocking(),
            worker(),
        )
    
    
    asyncio.run(main())

Bạn sẽ thấy Worker bị ảnh hưởng.

* * *

# 14\. Thay bằng `asyncio.sleep`
    
    
    async def blocking():
        print("blocking start")
    
        await asyncio.sleep(3)
    
        print("blocking done")

Bây giờ:
    
    
    blocking start
    worker 0
    worker 1
    worker 2
    worker 3
    worker 4
    blocking done

Hai coroutine có thể tiến triển xen kẽ.

* * *

# 15\. `await` không phải "pause thread"

Đây là câu bạn nên ghi nhớ:

> **`await` suspend coroutine, không nhất thiết block thread.**

Ví dụ:
    
    
    Thread
     │
     ├── Task A
     │     │
     │     └── await I/O
     │
     ├── Task B
     │
     ├── Task C
     │
     └── Task D

Một thread có thể phục vụ rất nhiều coroutine.

* * *

# 16\. Vậy `await` đang chờ cái gì?

Câu trả lời chính xác hơn:

> `await` chờ một **awaitable**.

Các đối tượng awaitable quan trọng:
    
    
    Coroutine
    Task
    Future

Ví dụ:
    
    
    await some_coroutine()

hoặc:
    
    
    await some_task

hoặc:
    
    
    await some_future

* * *

# 17\. Coroutine là Awaitable

Ví dụ:
    
    
    async def foo():
        return 42

Ta có:
    
    
    coro = foo()

Có thể:
    
    
    result = await coro

* * *

# 18\. Task cũng là Awaitable
    
    
    task = asyncio.create_task(foo())
    
    result = await task

Task chứa coroutine và quản lý lifecycle của nó.

* * *

# 19\. Future cũng là Awaitable

Ví dụ:
    
    
    future = asyncio.get_running_loop().create_future()
    
    result = await future

Future chưa có kết quả:
    
    
    Future
     │
     └── pending

Sau đó:
    
    
    future.set_result(42)

thì:
    
    
    Future
     │
     └── done → 42

Future chúng ta sẽ học sâu hơn sau.

* * *

# 20\. `await` có thể hình dung như "yield control"

Một mental model hữu ích:
    
    
    await something

≈
    
    
    Tôi tạm nhường quyền
    cho đến khi something sẵn sàng.

Không nên hiểu:
    
    
    await = sleep

vì:
    
    
    await socket_read()

không phải sleep.

Nó là:
    
    
    đợi I/O readiness

* * *

# 21\. Event Loop thực sự làm gì?

Mental model đơn giản hóa:
    
    
    while tasks:
        task = lấy task sẵn sàng
    
        chạy task
    
        nếu task await:
            task suspend
    
        nếu I/O ready:
            task ready lại

Có thể hình dung:
    
    
    ┌────────────────────────────┐
    │        Event Loop          │
    │                            │
    │  Ready Queue               │
    │  ┌───┬───┬───┬───┐         │
    │  │ A │ B │ C │ D │         │
    │  └───┴───┴───┴───┘         │
    │                            │
    │  I/O waiting               │
    │  ┌────┬────┬────┐          │
    │  │ A  │ C  │ D  │          │
    │  └────┴────┴────┘          │
    └────────────────────────────┘

Đây là mental model đủ tốt để xây ứng dụng.

* * *

# 22\. Ready và Waiting

Một Task thường luân chuyển giữa:
    
    
    READY
      │
      ▼
    RUNNING
      │
      ▼
    WAITING
      │
      │ I/O complete
      ▼
    READY
      │
      ▼
    RUNNING

Ví dụ HTTP:
    
    
    Task
     │
     ▼
    send request
     │
     ▼
    await response
     │
     ▼
    WAITING
     │
     │ network response
     │
     ▼
    READY
     │
     ▼
    resume

* * *

# 23\. Một Event Loop không chạy tất cả coroutine cùng lúc

Đây là điểm cần phân biệt:
    
    
    asyncio

không mặc định nghĩa:
    
    
    100 coroutine chạy song song thật sự

Trên một event loop thread:
    
    
    Task A
    Task B
    Task C

thường tiến triển theo kiểu:
    
    
    A → await
    B → await
    C → await
    A → resume
    B → resume
    ...

Đây là **concurrency** , không phải parallelism.

* * *

# 24\. Concurrency vs Parallelism

### Concurrency
    
    
    CPU
     │
     ├── A
     ├── B
     ├── C
     └── D

Các công việc xen kẽ.

### Parallelism
    
    
    CPU 1 → A
    CPU 2 → B
    CPU 3 → C
    CPU 4 → D

Thực sự chạy đồng thời trên nhiều CPU cores.

Asyncio chủ yếu cung cấp:

> **Concurrency**

Không phải CPU parallelism.

* * *

# 25\. Vì sao asyncio vẫn rất nhanh cho HTTP?

Giả sử:
    
    
    100 requests

Mỗi request mất:
    
    
    100 ms network

Sequential:
    
    
    100 × 100ms
    ≈ 10s

Async:
    
    
    100 request
        ↓
    đợi network
        ↓
    Event Loop xử lý task khác

Nếu server/network cho phép:
    
    
    ≈ 100ms + overhead

Đây là nơi asyncio tỏa sáng.

* * *

# 26\. Nhưng nếu mỗi request có CPU processing lớn?

Ví dụ:
    
    
    async def process():
        data = await fetch()
    
        # CPU-heavy
        for _ in range(100_000_000):
            ...

Thì:
    
    
    fetch
      ↓
    await
      ↓
    CPU processing
    ████████████████████
      ↓
    Event Loop bị block

Asyncio không giải quyết CPU-bound workload.

* * *

# 27\. `await` phải xuất hiện ở đâu?

Chỉ trong:
    
    
    async def

Ví dụ:
    
    
    async def main():
        await foo()

Không thể:
    
    
    def main():
        await foo()

* * *

# 28\. Nhưng không phải mọi hàm async đều có `await`

Có thể viết:
    
    
    async def foo():
        return 42

Hợp lệ.

Nhưng coroutine này không có điểm suspend.

Khi chạy:
    
    
    await foo()

nó hoàn thành ngay.

* * *

# 29\. Một ví dụ rất nguy hiểm
    
    
    async def worker():
        for i in range(10_000_000):
            pass

Bạn nghĩ:
    
    
    asyncio.create_task(worker())

là background.

Không.

Task vẫn chạy trên event-loop thread.

Nếu không có:
    
    
    await

thì nó không chủ động nhường quyền.

* * *

# 30\. Có thể "nhường quyền" thủ công

Một kỹ thuật:
    
    
    await asyncio.sleep(0)

Ví dụ:
    
    
    async def worker():
        for i in range(100_000):
            do_work()
    
            if i % 1000 == 0:
                await asyncio.sleep(0)

Điều này cho Task khác cơ hội chạy.

Nhưng lưu ý:

> Đây **không biến CPU-bound code thành async thật sự**.

Nó chỉ giúp event loop có cơ hội xử lý công việc khác.

* * *

# 31\. Tại sao `sleep(0)` không phải giải pháp CPU-bound?

Ví dụ:
    
    
    CPU work
    ████████
    await sleep(0)
    CPU work
    ████████
    await sleep(0)

CPU vẫn phải thực hiện toàn bộ công việc.

Nếu workload nặng, giải pháp đúng thường là:
    
    
    CPU-bound
        ↓
    ThreadPoolExecutor
    hoặc
    ProcessPoolExecutor

Tùy loại workload.

* * *

# 32\. Asyncio + Thread

Khi có blocking API:
    
    
    result = blocking_function()

không nên gọi trực tiếp trong event loop nếu nó có thể block lâu.

Có thể đưa nó sang thread:
    
    
    result = await asyncio.to_thread(
        blocking_function
    )

Mental model:
    
    
    Event Loop
        │
        ├── async Task A
        │
        ├── async Task B
        │
        └── to_thread()
                │
                ▼
           Thread Pool

Đây là cầu nối cực kỳ quan trọng giữa synchronous code và asyncio.

* * *

# 33\. Ví dụ `asyncio.to_thread()`
    
    
    import asyncio
    import time
    
    
    def blocking_work():
        time.sleep(3)
        return 42
    
    
    async def main():
        result = await asyncio.to_thread(
            blocking_work
        )
    
        print(result)
    
    
    asyncio.run(main())

Event Loop không phải tự mình ngủ 3 giây.

Thread khác xử lý blocking operation.

* * *

# 34\. `asyncio.to_thread()` rất hữu ích khi nào?

Ví dụ thư viện cũ:
    
    
    requests
    sqlite3
    PIL
    os operations

hoặc API không hỗ trợ async.

Ví dụ:
    
    
    data = requests.get(url)

Không nên gọi trực tiếp trong event loop nếu request có thể block lâu.

Có thể:
    
    
    response = await asyncio.to_thread(
        requests.get,
        url,
    )

Đây là một kỹ thuật thực tế.

* * *

# 35\. Nhưng đừng lạm dụng `to_thread()`

Không nên:
    
    
    await asyncio.to_thread(
        pure_python_cpu_heavy_function
    )

và kỳ vọng:

> CPU-bound Python tự nhiên chạy nhanh hơn.

GIL và bản chất workload vẫn là vấn đề.

Đối với CPU-bound nặng, `ProcessPoolExecutor` thường phù hợp hơn.

Bạn đã học `ProcessPoolExecutor`, nên sau này chúng ta sẽ ghép hai thế giới:
    
    
    asyncio
       │
       ├── I/O-bound
       │
       ├── to_thread()
       │
       └── ProcessPoolExecutor
              │
              └── CPU-bound

* * *

# 36\. Một ví dụ kết hợp
    
    
    import asyncio
    import time
    
    
    def blocking_io():
        time.sleep(2)
        return "done"
    
    
    async def async_worker():
        await asyncio.sleep(1)
        return "async done"
    
    
    async def main():
        results = await asyncio.gather(
            asyncio.to_thread(blocking_io),
            async_worker(),
        )
    
        print(results)
    
    
    asyncio.run(main())

Hai công việc có thể tiến triển concurrent:
    
    
    Event Loop
       │
       ├── async_worker
       │      └── await
       │
       └── to_thread
              │
              ▼
           Worker Thread

* * *

# 37\. Một lỗi rất phổ biến

Sai:
    
    
    async def main():
        time.sleep(5)
    
        await something()

Đúng hơn:
    
    
    async def main():
        await asyncio.sleep(5)
    
        await something()

Hoặc nếu `time.sleep()` nằm trong thư viện blocking:
    
    
    async def main():
        await asyncio.to_thread(
            time.sleep,
            5,
        )

* * *

# 38\. Asyncio không làm blocking code tự động non-blocking

Đây là nguyên tắc bạn cần nhớ:
    
    
    async def foo():
        requests.get(...)

không có nghĩa:
    
    
    requests.get()

đã trở thành async.

Nó vẫn blocking.

`async def` chỉ nói:

> Hàm này trả về coroutine.

Nó **không biến toàn bộ code bên trong thành non-blocking**.

* * *

# 39\. Một ví dụ rất quan trọng
    
    
    async def foo():
        print("A")
    
        requests.get(url)
    
        print("B")

Đây vẫn là:
    
    
    A
     │
     ▼
    requests.get()
    ████████████████
     │
     ▼
    B

Event Loop bị block trong thời gian request.

* * *

# 40\. Async-friendly library

Trong ứng dụng asyncio, ưu tiên:
    
    
    aiohttp
    httpx.AsyncClient
    asyncpg
    aiosqlite

thay vì các API synchronous tương ứng khi workload cần concurrency.

Mental model:
    
    
    Async app
       │
       ├── async HTTP client
       ├── async DB client
       ├── async filesystem API
       └── async queue

Không phải mọi thứ đều có async version, nên `to_thread()` rất hữu ích.

* * *

# 41\. Bài tập 1 — chứng minh cooperative scheduling

Viết:
    
    
    async def worker(name):
        for i in range(5):
            print(name, i)
            await asyncio.sleep(0)

Chạy:
    
    
    await asyncio.gather(
        worker("A"),
        worker("B"),
        worker("C"),
    )

Quan sát thứ tự.

Sau đó bỏ:
    
    
    await asyncio.sleep(0)

và quan sát lại.

* * *

# 42\. Bài tập 2 — `time.sleep()` vs `asyncio.sleep()`

Tạo:
    
    
    async def worker_a():
        for i in range(5):
            print("A", i)
            await asyncio.sleep(0.5)
    
    
    async def worker_b():
        for i in range(5):
            print("B", i)
            await asyncio.sleep(0.5)

Chạy concurrent.

Sau đó đổi một bên thành:
    
    
    time.sleep(0.5)

Quan sát.

Bạn sẽ **thấy trực tiếp Event Loop bị block**.

* * *

# 43\. Bài tập 3 — CPU-bound

Viết:
    
    
    async def cpu_task(name):
        for i in range(50_000_000):
            pass
    
        print(name, "done")

Tạo:
    
    
    asyncio.create_task(cpu_task("A"))
    asyncio.create_task(cpu_task("B"))

Quan sát.

Sau đó thêm:
    
    
    await asyncio.sleep(0)

vào vòng lặp và so sánh.

Mục tiêu:

> Hiểu tại sao `await` là điểm nhường quyền nhưng không biến CPU-bound thành parallel processing.

* * *

# 44\. Bài tập 4 — `to_thread()`

Tạo:
    
    
    def blocking_work(name):
        import time
    
        time.sleep(3)
    
        return name

Chạy 3 công việc:
    
    
    A
    B
    C

bằng:
    
    
    asyncio.to_thread()

và dùng:
    
    
    asyncio.gather()

Mục tiêu:
    
    
    A ─────
    B ─────
    C ─────

thay vì:
    
    
    A ─────
           B ─────
                  C ─────

* * *

# 45\. Bài tập 5 — Debug Event Loop

Tạo:
    
    
    async def worker(name):
        task = asyncio.current_task()
    
        print(
            task.get_name(),
            "start"
        )
    
        await asyncio.sleep(1)
    
        print(
            task.get_name(),
            "done"
        )

Tạo 5 Task có tên:
    
    
    worker-1
    worker-2
    worker-3
    worker-4
    worker-5

Sau đó sử dụng:
    
    
    asyncio.all_tasks()

để quan sát các Task đang tồn tại.

* * *

# 46\. Mini Project — Async Scheduler

Hãy xây một scheduler rất nhỏ:
    
    
    AsyncScheduler
          │
          ├── Task A
          ├── Task B
          ├── Task C
          └── Task D

API:
    
    
    scheduler.create(coro)
    scheduler.cancel_all()
    await scheduler.wait()

Ví dụ:
    
    
    scheduler.create(
        worker("A")
    )
    
    scheduler.create(
        worker("B")
    )
    
    scheduler.create(
        worker("C")
    )

Bên trong:
    
    
    class AsyncScheduler:
        def __init__(self):
            self.tasks = set()

Khi create:
    
    
    task = asyncio.create_task(coro)
    self.tasks.add(task)

Khi task hoàn thành:
    
    
    task.add_done_callback(
        self.tasks.discard
    )

Đây là một pattern quản lý background task rất đáng học.

* * *

# 47\. Một thiết kế tốt hơn

Có thể viết:
    
    
    class AsyncScheduler:
    
        def __init__(self):
            self.tasks = set()
    
        def create(self, coro):
            task = asyncio.create_task(coro)
    
            self.tasks.add(task)
    
            task.add_done_callback(
                self.tasks.discard
            )
    
            return task
    
        async def wait(self):
            if self.tasks:
                await asyncio.gather(
                    *self.tasks,
                    return_exceptions=True,
                )
    
        def cancel_all(self):
            for task in self.tasks:
                task.cancel()

Đây chưa phải production-grade scheduler, nhưng nó giúp bạn hiểu:
    
    
    create
      ↓
    track Task
      ↓
    Task chạy
      ↓
    Task done
      ↓
    remove khỏi set

* * *

# 48\. Mental Model quan trọng nhất của Buổi 6

Hãy nhớ chuỗi này:
    
    
    async def
       ↓
    Coroutine
       ↓
    Task
       ↓
    Event Loop
       ↓
    run
       ↓
    await
       ↓
    Coroutine suspend
       ↓
    Event Loop lấy quyền
       ↓
    Task khác chạy
       ↓
    I/O hoàn thành
       ↓
    Task trở lại Ready
       ↓
    Coroutine resume

Và đặc biệt:
    
    
    await ≠ block thread

mà:
    
    
    await = suspend coroutine + yield control

* * *

# 49\. 5 nguyên tắc vàng

### 1\. `async def` không tự làm code non-blocking
    
    
    async def foo():
        requests.get(...)

vẫn có thể block.

### 2\. `await` là điểm nhường quyền
    
    
    await something()

cho Event Loop cơ hội chạy Task khác.

### 3\. Asyncio chủ yếu dành cho I/O-bound
    
    
    HTTP
    DB
    Socket
    Queue
    File I/O

### 4\. CPU-bound không nên chạy trực tiếp trong Event Loop
    
    
    CPU-heavy
        ↓
    ProcessPoolExecutor

hoặc tùy trường hợp:
    
    
    blocking I/O
        ↓
    asyncio.to_thread()

### 5\. Concurrency ≠ Parallelism
    
    
    asyncio
        → concurrency
    
    ProcessPool
        → parallelism

* * *

# 50\. Roadmap sau Buổi 6

Bạn đã có nền tảng:
    
    
    Buổi 1
    async / await
          ↓
    Buổi 2
    Event Loop
          ↓
    Buổi 3
    Coroutine
          ↓
    Buổi 4
    Task
          ↓
    Buổi 5
    gather / wait / as_completed
          ↓
    Buổi 6
    await + cooperative scheduling

Bước tiếp theo rất tự nhiên là:

## **Buổi 7 —`asyncio.Future` Deep Dive**

Chúng ta sẽ đi xuống tầng thấp hơn:
    
    
    Coroutine
        ↓
    Task
        ↓
    Future
        ↓
    Event Loop

Bạn sẽ học:

  * Future là gì?

  * Vì sao Future tồn tại?

  * `set_result()`

  * `set_exception()`

  * `done()`

  * `result()`

  * `add_done_callback()`

  * Task và Future khác nhau chính xác ở đâu

  * Tự tạo Future

  * Future dùng để bridge callback-based API với async/await

  * Tự xây một async primitive nhỏ




Đây là phần hơi "low-level", nhưng **rất đáng học** nếu mục tiêu của bạn là sau này tự xây `queue server`, `crawl worker`, scheduler và framework asyncio thay vì chỉ biết gọi `gather()`.