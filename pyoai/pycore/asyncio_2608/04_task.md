# Buổi 4 — `asyncio.Task` Deep Dive

Ở 3 buổi trước, chúng ta đã xây được mental model:
    
    
    async def
        ↓
    Coroutine Function
        ↓
    foo()
        ↓
    Coroutine Object
        ↓
    Task
        ↓
    Event Loop

Hôm nay chúng ta tập trung vào **Task**.

Nếu hiểu Task thật chắc, bạn sẽ hiểu được phần lớn cơ chế concurrency của asyncio.

* * *

# 1\. Task là gì?

Một câu định nghĩa rất quan trọng:

> **Task là một wrapper quản lý việc thực thi một coroutine bởi Event Loop.**

Ví dụ:
    
    
    async def work():
        await asyncio.sleep(1)
        return 42

Ta có coroutine:
    
    
    coro = work()

Nhưng coroutine chưa được event loop schedule một cách độc lập.

Ta tạo Task:
    
    
    task = asyncio.create_task(coro)

Mental model:
    
    
    Coroutine
        │
        │ create_task()
        ▼
    ┌──────────────┐
    │     Task     │
    │              │
    │ coroutine    │
    │ state        │
    │ result       │
    │ exception    │
    │ cancellation │
    └──────┬───────┘
           │
           ▼
      Event Loop

* * *

# 2\. Coroutine và Task khác nhau

Ví dụ:
    
    
    async def work():
        await asyncio.sleep(1)
        return 42

### Coroutine
    
    
    coro = work()

Có nghĩa:

> Tôi có một coroutine object đại diện cho công việc này.

### Task
    
    
    task = asyncio.create_task(work())

Có nghĩa:

> Hãy schedule coroutine này để Event Loop quản lý việc thực thi nó.

Đây là khác biệt cốt lõi.

* * *

# 3\. Task tạo ra concurrency

Ví dụ tuần tự:
    
    
    async def main():
        await work("A")
        await work("B")
        await work("C")

Ta có:
    
    
    A ──────────
                B ──────────
                            C ──────────

Nhưng:
    
    
    async def main():
        a = asyncio.create_task(work("A"))
        b = asyncio.create_task(work("B"))
        c = asyncio.create_task(work("C"))
    
        await a
        await b
        await c

Ta có:
    
    
    A ─────────────
    B ─────────────
    C ─────────────

Task chính là một trong những cơ chế tạo **concurrent execution** trong asyncio.

* * *

# 4\. `create_task()` làm gì?

Ví dụ:
    
    
    task = asyncio.create_task(work())

Có thể hình dung:
    
    
    work()
     │
     ▼
    Coroutine Object
     │
     ▼
    create_task()
     │
     ▼
    Task
     │
     ▼
    Event Loop schedule

Task được đăng ký với event loop để có thể được thực thi.

* * *

# 5\. Task không nhất thiết hoàn thành ngay

Ví dụ:
    
    
    async def work():
        print("start")
    
        await asyncio.sleep(3)
    
        print("done")

Khi:
    
    
    task = asyncio.create_task(work())

Task có thể đang ở trạng thái:
    
    
    PENDING

Sau đó:
    
    
    PENDING
       │
       ▼
    RUNNING
       │
       ▼
    PENDING / waiting
       │
       ▼
    RUNNING
       │
       ▼
    FINISHED

Đây là lifecycle cơ bản.

* * *

# 6\. Kiểm tra Task

Ví dụ:
    
    
    import asyncio
    
    
    async def work():
        await asyncio.sleep(1)
        return 42
    
    
    async def main():
        task = asyncio.create_task(work())
    
        print(task)
    
        result = await task
    
        print(result)
    
    
    asyncio.run(main())

Bạn sẽ thấy một object dạng:
    
    
    <Task pending name='Task-2' coro=<work() running at ...>>

Sau khi hoàn thành:
    
    
    <Task finished name='Task-2' coro=<work() done ...> result=42>

* * *

# 7\. `task.done()`

Task có:
    
    
    task.done()

Dùng để kiểm tra Task đã kết thúc chưa.

Ví dụ:
    
    
    async def work():
        await asyncio.sleep(2)
        return 42
    
    
    async def main():
        task = asyncio.create_task(work())
    
        print(task.done())
    
        await asyncio.sleep(3)
    
        print(task.done())
    
    
    asyncio.run(main())

Kết quả:
    
    
    False
    True

Mental model:
    
    
    create_task()
          │
          ▼
       pending
          │
          │ 2s
          ▼
       finished

* * *

# 8\. `task.result()`

Sau khi Task hoàn thành:
    
    
    result = task.result()

Ví dụ:
    
    
    async def calculate():
        await asyncio.sleep(1)
        return 100
    
    
    async def main():
        task = asyncio.create_task(calculate())
    
        await task
    
        print(task.result())
    
    
    asyncio.run(main())

Kết quả:
    
    
    100

* * *

# 9\. Không được gọi `result()` quá sớm

Ví dụ:
    
    
    async def main():
        task = asyncio.create_task(calculate())
    
        print(task.result())

Nếu Task chưa hoàn thành, sẽ xảy ra:
    
    
    asyncio.exceptions.InvalidStateError

Do đó:
    
    
    task.result()

chỉ nên dùng khi bạn biết Task đã hoàn thành.

Ví dụ:
    
    
    await task
    
    result = task.result()

* * *

# 10\. Nhưng tại sao không chỉ `await task`?

Thực tế thường bạn có thể viết:
    
    
    result = await task

thay vì:
    
    
    await task
    result = task.result()

Ví dụ:
    
    
    async def calculate():
        return 100
    
    
    async def main():
        task = asyncio.create_task(calculate())
    
        result = await task
    
        print(result)

Đây thường là cách rõ ràng hơn.

* * *

# 11\. Task có thể chứa exception

Ví dụ:
    
    
    async def divide():
        return 10 / 0

Task:
    
    
    task = asyncio.create_task(divide())

Khi:
    
    
    await task

exception sẽ được propagate:
    
    
    try:
        await task
    except ZeroDivisionError:
        print("Division error")

* * *

# 12\. `task.exception()`

Task cung cấp:
    
    
    task.exception()

Ví dụ:
    
    
    async def divide():
        return 10 / 0
    
    
    async def main():
        task = asyncio.create_task(divide())
    
        try:
            await task
        except ZeroDivisionError:
            print(task.exception())
    
    
    asyncio.run(main())

Task giữ exception đã xảy ra.

* * *

# 13\. `result()` và `exception()`

Mental model:
    
    
    Task
     │
     ├── thành công
     │      │
     │      └── result()
     │
     └── lỗi
            │
            └── exception()

Ví dụ thành công:
    
    
    task.result()

→ trả về giá trị.

Ví dụ thất bại:
    
    
    task.exception()

→ trả về exception object.

* * *

# 14\. Task State Machine

Hãy nhìn Task như một state machine:
    
    
                 create_task()
                       │
                       ▼
                  ┌─────────┐
                  │ PENDING │
                  └────┬────┘
                       │
                       ▼
                  ┌─────────┐
                  │ RUNNING │
                  └────┬────┘
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
           success   error   cancel
              │        │        │
              ▼        ▼        ▼
          FINISHED  FINISHED  CANCELLED

Trong thực tế Task có thể chuyển qua nhiều trạng thái chờ, nhưng mental model trên rất hữu ích.

* * *

# 15\. `task.cancel()`

Một trong những tính năng cực kỳ quan trọng:
    
    
    task.cancel()

Ví dụ:
    
    
    async def worker():
        print("start")
    
        await asyncio.sleep(10)
    
        print("done")
    
    
    async def main():
        task = asyncio.create_task(worker())
    
        await asyncio.sleep(1)
    
        task.cancel()
    
        try:
            await task
        except asyncio.CancelledError:
            print("Task cancelled")
    
    
    asyncio.run(main())

Output:
    
    
    start
    Task cancelled

`done` không được in.

* * *

# 16\. Cancellation không giống "kill process"

Đây là điểm rất quan trọng.

Khi:
    
    
    task.cancel()

Python không đơn giản:
    
    
    XÓA TASK NGAY LẬP TỨC

Thay vào đó, cancellation được **inject vào coroutine** dưới dạng:
    
    
    asyncio.CancelledError

Tại điểm thích hợp.

Mental model:
    
    
    Task
     │
     │ cancel()
     ▼
    Cancellation requested
     │
     ▼
    Coroutine nhận CancelledError
     │
     ├── cleanup
     │
     └── kết thúc

* * *

# 17\. Bắt `CancelledError`

Ví dụ:
    
    
    async def worker():
        try:
            while True:
                print("working...")
                await asyncio.sleep(1)
    
        except asyncio.CancelledError:
            print("cleanup...")
            raise

Tại sao phải:
    
    
    raise

?

Bởi vì sau cleanup, ta thường muốn cancellation tiếp tục được propagate.

Không nên vô tình nuốt cancellation.

* * *

# 18\. Cleanup khi Task bị cancel

Đây là pattern rất quan trọng:
    
    
    async def worker():
        resource = acquire_resource()
    
        try:
            await do_work()
    
        except asyncio.CancelledError:
            cleanup(resource)
            raise

Hoặc thường tốt hơn:
    
    
    async def worker():
        try:
            await do_work()
    
        finally:
            cleanup()

`finally` rất hữu ích cho cleanup.

* * *

# 19\. `cancelled()`

Task có:
    
    
    task.cancelled()

Ví dụ:
    
    
    async def worker():
        await asyncio.sleep(10)
    
    
    async def main():
        task = asyncio.create_task(worker())
    
        task.cancel()
    
        try:
            await task
        except asyncio.CancelledError:
            pass
    
        print(task.cancelled())
    
    
    asyncio.run(main())

Kết quả:
    
    
    True

* * *

# 20\. Task có tên

Bạn có thể đặt tên:
    
    
    task = asyncio.create_task(
        worker(),
        name="download-worker"
    )

Sau đó:
    
    
    print(task.get_name())

Kết quả:
    
    
    download-worker

Điều này cực kỳ hữu ích khi debug ứng dụng lớn.

Ví dụ:
    
    
    task = asyncio.create_task(
        crawl(url),
        name=f"crawl:{url}"
    )

* * *

# 21\. Đổi tên Task

Có thể:
    
    
    task.set_name("worker-01")

và:
    
    
    task.get_name()

Dùng naming tốt sẽ giúp log dễ đọc hơn:
    
    
    worker-01 started
    worker-02 started
    worker-03 failed

thay vì:
    
    
    Task-17
    Task-18
    Task-19

* * *

# 22\. Lấy coroutine bên trong Task

Có:
    
    
    task.get_coro()

Ví dụ:
    
    
    async def worker():
        ...
    
    
    task = asyncio.create_task(worker())
    
    print(task.get_coro())

Điều này hữu ích cho debugging/introspection.

* * *

# 23\. Lấy tất cả Task đang chạy

Bạn có thể dùng:
    
    
    asyncio.all_tasks()

Ví dụ:
    
    
    async def worker(name):
        await asyncio.sleep(10)
    
    
    async def main():
        asyncio.create_task(worker("A"))
        asyncio.create_task(worker("B"))
    
        tasks = asyncio.all_tasks()
    
        for task in tasks:
            print(task)
    
    
    asyncio.run(main())

Bạn sẽ thấy Task hiện tại và các Task khác.

* * *

# 24\. `asyncio.current_task()`

Để lấy Task hiện tại:
    
    
    asyncio.current_task()

Ví dụ:
    
    
    async def worker():
        task = asyncio.current_task()
    
        print(task)

Mental model:
    
    
    Event Loop
        │
        ▼
    Current Task
        │
        ▼
    asyncio.current_task()

* * *

# 25\. Ví dụ Debug Task
    
    
    async def worker(name):
        task = asyncio.current_task()
    
        print(
            task.get_name(),
            "running"
        )
    
        await asyncio.sleep(1)
    
        print(
            task.get_name(),
            "done"
        )

Tạo:
    
    
    async def main():
        tasks = [
            asyncio.create_task(
                worker("A"),
                name="worker-A"
            ),
            asyncio.create_task(
                worker("B"),
                name="worker-B"
            ),
        ]
    
        await asyncio.gather(*tasks)

Output:
    
    
    worker-A running
    worker-B running
    worker-A done
    worker-B done

Đây là kỹ thuật rất hữu ích cho crawler worker sau này.

* * *

# 26\. Task Callback

Task có thể đăng ký callback:
    
    
    task.add_done_callback(callback)

Ví dụ:
    
    
    def on_done(task):
        print("Task completed")
    
    
    async def worker():
        await asyncio.sleep(1)
    
    
    async def main():
        task = asyncio.create_task(worker())
    
        task.add_done_callback(on_done)
    
        await task
    
    
    asyncio.run(main())

Khi Task hoàn thành:
    
    
    worker
      │
      ▼
    finished
      │
      ▼
    on_done()

* * *

# 27\. Callback nhận Task

Callback phải nhận một argument:
    
    
    def on_done(task):
        ...

Bạn có thể lấy:
    
    
    task.result()

Ví dụ:
    
    
    def on_done(task):
        print("Result:", task.result())

* * *

# 28\. Callback và Exception

Nếu Task lỗi:
    
    
    def on_done(task):
        if task.cancelled():
            print("cancelled")
            return
    
        if task.exception():
            print("error:", task.exception())
            return
    
        print("result:", task.result())

Đây là một pattern debug tốt.

* * *

# 29\. `Task` và `Future`

Bạn sẽ sớm gặp:
    
    
    asyncio.Future

Đừng nhầm:
    
    
    Coroutine
    Task
    Future

Mental model đơn giản:
    
    
    Coroutine
       │
       ▼
     Task
       │
       ▼
    Future-like result

Task thực chất kế thừa/có hành vi của Future.

Nhưng:

> **Future đại diện cho một kết quả sẽ có trong tương lai, còn Task dùng để quản lý việc chạy coroutine.**

Chúng ta sẽ đào sâu Future ở phần nâng cao.

* * *

# 30\. Một lỗi rất phổ biến: tạo Task rồi quên nó

Ví dụ:
    
    
    async def main():
        asyncio.create_task(worker())
    
        print("main done")

Bạn đã tạo Task nhưng không giữ reference và không chờ nó.

Điều này có thể gây vấn đề lifecycle.

Tốt hơn:
    
    
    task = asyncio.create_task(worker())
    
    await task

hoặc:
    
    
    tasks = []
    
    tasks.append(
        asyncio.create_task(worker())
    )

sau đó quản lý chúng.

* * *

# 31\. Task phải có lifecycle rõ ràng

Một application tốt nên có:
    
    
    CREATE
       ↓
    SCHEDULE
       ↓
    RUN
       ↓
    WAIT
       ↓
    COMPLETE / ERROR / CANCEL
       ↓
    CLEANUP

Đừng nghĩ:
    
    
    asyncio.create_task(...)

là xong.

Đối với hệ thống lớn, bạn phải biết:

> Task này do ai tạo? Ai sở hữu nó? Ai chờ nó? Ai cancel nó? Khi application shutdown thì chuyện gì xảy ra?

Đây là tư duy cực kỳ quan trọng khi xây worker/crawler.

* * *

# 32\. Ví dụ Worker thực tế
    
    
    async def worker():
        try:
            while True:
                print("working")
    
                await asyncio.sleep(1)
    
        except asyncio.CancelledError:
            print("worker stopping")
            raise

Main:
    
    
    async def main():
        task = asyncio.create_task(
            worker(),
            name="crawler-worker"
        )
    
        await asyncio.sleep(5)
    
        task.cancel()
    
        try:
            await task
        except asyncio.CancelledError:
            print("worker stopped")

Đây là pattern bạn sẽ sử dụng rất nhiều sau này.

* * *

# 33\. Tại sao phải `await task` sau `cancel()`?

Nhiều người viết:
    
    
    task.cancel()

rồi nghĩ Task đã biến mất.

Không nên nghĩ như vậy.

Tốt hơn:
    
    
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        pass

Mental model:
    
    
    cancel()
       │
       ▼
    request cancellation
       │
       ▼
    await task
       │
       ▼
    Task xử lý cancellation
       │
       ▼
    cleanup
       │
       ▼
    CancelledError
       │
       ▼
    Task kết thúc

* * *

# 34\. Task và `gather()`

Bạn đã thấy:
    
    
    await asyncio.gather(
        worker("A"),
        worker("B"),
        worker("C"),
    )

`gather()` có thể làm việc với awaitables và quản lý concurrent execution.

Bạn cũng có thể:
    
    
    tasks = [
        asyncio.create_task(worker("A")),
        asyncio.create_task(worker("B")),
        asyncio.create_task(worker("C")),
    ]
    
    results = await asyncio.gather(*tasks)

Mental model:
    
    
                  gather
                    │
           ┌────────┼────────┐
           ▼        ▼        ▼
        Task A   Task B   Task C
           │        │        │
           └────────┼────────┘
                    ▼
                 results

`gather()` chúng ta sẽ học sâu ở **Buổi 5**.

* * *

# 35\. Bài tập 1 — Task lifecycle

Viết:
    
    
    async def worker():
        await asyncio.sleep(2)
        return 100

Tạo Task:
    
    
    task = asyncio.create_task(worker())

Sau đó quan sát:
    
    
    task.done()
    task.cancelled()

trước và sau khi:
    
    
    await task

* * *

# 36\. Bài tập 2 — Task exception

Tạo:
    
    
    async def worker():
        await asyncio.sleep(1)
        raise ValueError("Something went wrong")

Tạo Task và xử lý:
    
    
    try:
        await task
    except ValueError:
        ...

Sau đó kiểm tra:
    
    
    task.done()
    task.exception()

* * *

# 37\. Bài tập 3 — Cancellation

Tạo worker chạy vô hạn:
    
    
    async def worker():
        while True:
            print("working...")
            await asyncio.sleep(1)

Main:
    
    
    tạo worker
       ↓
    chạy 5 giây
       ↓
    cancel
       ↓
    cleanup
       ↓
    shutdown

Worker phải xử lý:
    
    
    asyncio.CancelledError

và đảm bảo cleanup bằng `finally`.

* * *

# 38\. Bài tập 4 — Task naming

Tạo 5 task:
    
    
    crawler-1
    crawler-2
    crawler-3
    crawler-4
    crawler-5

Trong mỗi task in:
    
    
    Task name
    Task start
    Task end

Dùng:
    
    
    asyncio.current_task()

để lấy Task hiện tại.

* * *

# 39\. Bài tập Deep Dive — Mini Worker Manager

Đây là bài tôi khuyên bạn làm thật kỹ vì nó liên quan trực tiếp tới hệ thống crawl-worker bạn đang xây.

Thiết kế:
    
    
    WorkerManager
          │
          ├── worker-1
          ├── worker-2
          ├── worker-3
          └── worker-4

API:
    
    
    manager.start()
    manager.stop()
    manager.wait()

Bên trong:
    
    
    start()
      │
      ├── create_task(worker-1)
      ├── create_task(worker-2)
      ├── create_task(worker-3)
      └── create_task(worker-4)
    
    stop()
      │
      ├── cancel(worker-1)
      ├── cancel(worker-2)
      ├── cancel(worker-3)
      └── cancel(worker-4)
    
    wait()
      │
      ▼
    await all tasks

Đây chính là bước đầu tiên để chúng ta chuyển từ **học asyncio API** sang **thiết kế hệ thống async**.

* * *

# 40\. Mental Model cuối Buổi 4

Hãy nhớ sơ đồ này:
    
    
                        Event Loop
                            │
                            │ schedules
                            ▼
                     ┌─────────────┐
                     │     Task    │
                     └──────┬──────┘
                            │
                      manages
                            │
                            ▼
                       Coroutine
                            │
                      ┌─────┴─────┐
                      │           │
                   await        return
                      │           │
                      ▼           ▼
                 suspended     result
                      │
                      ▼
                  Event Loop
                      │
                      ▼
                  resume Task

Task có thể:
    
    
    PENDING
       │
       ▼
    RUNNING
       │
       ├──────────────┐
       │              │
       ▼              ▼
    SUCCESS         ERROR
       │              │
       ▼              ▼
    DONE            DONE
    
    hoặc:
    
    PENDING/RUNNING
          │
          ▼
       cancel()
          │
          ▼
    CANCELLED

Và 6 API bạn cần nhớ sau buổi này:
    
    
    asyncio.create_task()
    task.done()
    task.result()
    task.exception()
    task.cancel()
    task.cancelled()

Thêm 3 API debug rất hữu ích:
    
    
    asyncio.current_task()
    asyncio.all_tasks()
    task.get_name()

**Buổi 5** sẽ ghép những gì bạn vừa học thành concurrency thực sự với **`asyncio.gather()`** , sau đó so sánh sâu `gather()` với `wait()` và `as_completed()` — đặc biệt là **exception, cancellation, return value và cách xử lý hàng trăm coroutine**.