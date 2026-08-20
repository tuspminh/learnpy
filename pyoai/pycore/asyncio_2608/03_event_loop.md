# Buổi 3 — Event Loop Deep Dive

Đây là một trong những buổi **quan trọng nhất của asyncio**.

Nếu Buổi 2 giúp bạn hiểu:
    
    
    async def
       ↓
    Coroutine
       ↓
    Task

thì hôm nay chúng ta phải trả lời:

> **Ai thực sự chạy Coroutine và Task?**

Câu trả lời là:

> **Event Loop.**

* * *

# 1\. Event Loop là gì?

Có thể hình dung đơn giản:
    
    
                     Event Loop
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
            Task A     Task B     Task C
              │          │          │
              ▼          ▼          ▼
            chạy       chạy       chạy

Event Loop là một vòng lặp liên tục:
    
    
    while running:
        kiểm tra công việc cần chạy
        chạy một phần coroutine
        xử lý I/O
        đánh thức task đã sẵn sàng
        tiếp tục

Một cách đơn giản hóa:
    
    
    while True:
        ready_tasks = get_ready_tasks()
    
        for task in ready_tasks:
            run(task)
    
        process_io()

**Đây không phải source code thật của CPython** , mà là mental model để hiểu cơ chế.

* * *

# 2\. Tại sao gọi là Event Loop?

"Event" có thể là:
    
    
    HTTP response đã về
    Timer hết hạn
    Socket readable
    Socket writable
    Task sẵn sàng tiếp tục
    Future hoàn thành
    Callback cần chạy

Event Loop liên tục kiểm tra:

> Có sự kiện nào đã sẵn sàng để xử lý không?

Sau đó thực hiện callback/task tương ứng.

* * *

# 3\. Một Event Loop chạy ở đâu?

Thông thường:
    
    
    Python Process
          │
          ▼
       Thread
          │
          ▼
     Event Loop
          │
          ├── Task A
          ├── Task B
          └── Task C

Một cách hiểu phổ biến:

> **Một event loop thường chạy trên một thread.**

Ví dụ:
    
    
    Main Process
    │
    └── Main Thread
          │
          └── Event Loop
                 ├── Task A
                 ├── Task B
                 └── Task C

Đây là lý do asyncio không giống `ThreadPoolExecutor`.

* * *

# 4\. Event Loop không chạy tất cả Task cùng một lúc

Đây là điểm rất quan trọng.

Giả sử:
    
    
    async def task_a():
        print("A1")
        await asyncio.sleep(2)
        print("A2")

và:
    
    
    async def task_b():
        print("B1")
        await asyncio.sleep(1)
        print("B2")

Event Loop không thực sự làm:
    
    
    A và B chạy song song trên CPU

Mà gần giống:
    
    
    A chạy
     ↓
    A gặp await
     ↓
    Event Loop lấy B
     ↓
    B chạy
     ↓
    B gặp await
     ↓
    Event Loop chờ I/O/timer
     ↓
    B sẵn sàng
     ↓
    B tiếp tục
     ↓
    A sẵn sàng
     ↓
    A tiếp tục

Đây là:

> **Cooperative concurrency**

* * *

# 5\. `asyncio.run()` thực sự làm gì?

Khi bạn viết:
    
    
    asyncio.run(main())

đừng chỉ nghĩ:

> "Chạy hàm main."

Hãy nghĩ:
    
    
    asyncio.run(main())
           │
           ▼
    Tạo Event Loop
           │
           ▼
    Chạy main()
           │
           ▼
    Chờ main hoàn thành
           │
           ▼
    Cleanup
           │
           ▼
    Đóng Event Loop

Mental model:
    
    
    asyncio.run()
          │
          ├── create event loop
          │
          ├── run main coroutine
          │
          ├── finalize async generators
          │
          ├── shutdown async executor
          │
          └── close loop

Do đó:
    
    
    asyncio.run(main())

thường là **entry point** của chương trình asyncio.

* * *

# 6\. Kiểm tra Event Loop hiện tại

Trong coroutine, bạn có thể dùng:
    
    
    import asyncio
    
    
    async def main():
        loop = asyncio.get_running_loop()
    
        print(loop)
    
    
    asyncio.run(main())

Bạn sẽ nhận được một object đại diện cho event loop hiện tại.

Điểm quan trọng:
    
    
    asyncio.get_running_loop()

có nghĩa:

> Lấy event loop **đang thực sự chạy** trong thread hiện tại.

* * *

# 7\. `get_running_loop()` khác gì `get_event_loop()`?

Đây là điểm bạn nên biết ngay từ đầu.

Trong code asyncio hiện đại, ưu tiên:
    
    
    asyncio.get_running_loop()

Ví dụ:
    
    
    async def main():
        loop = asyncio.get_running_loop()
        print(loop)

Nếu không có event loop đang chạy, nó sẽ báo lỗi.

Điều này rất hữu ích vì nó giúp bạn phát hiện:

> Tôi có đang thực sự ở trong async context hay không?

* * *

# 8\. Event Loop và `await`

Đây là mental model quan trọng nhất của hôm nay.

Giả sử:
    
    
    async def task_a():
        print("A1")
        await asyncio.sleep(2)
        print("A2")

Khi Task A chạy:
    
    
    Task A
     │
     ▼
    print("A1")
     │
     ▼
    await sleep(2)

Task A không tiếp tục chạy ngay.

Nó nói với Event Loop:

> Tôi chưa thể tiếp tục. Hãy chạy việc khác và đánh thức tôi sau.
    
    
                  Event Loop
                      │
                      ▼
                   Task A
                      │
                      ▼
                  await sleep
                      │
                      ▼
                  suspended
                      │
              ┌───────┴───────┐
              │               │
              ▼               ▼
           Task B          Task C

* * *

# 9\. `asyncio.sleep()` rất đặc biệt

Trong ví dụ:
    
    
    await asyncio.sleep(2)

nó không giống:
    
    
    time.sleep(2)

### `time.sleep()`
    
    
    time.sleep(2)

Thread bị block.
    
    
    Thread
    ████████████████  2s

Event Loop không thể làm việc bình thường trong thread đó.

### `asyncio.sleep()`
    
    
    await asyncio.sleep(2)

Coroutine tạm dừng.
    
    
    Task A
    ████────── waiting ──────████

Event Loop có thể xử lý task khác.

* * *

# 10\. Ví dụ quan sát scheduling

Chạy:
    
    
    import asyncio
    
    
    async def worker(name):
        print(f"{name}: 1")
    
        await asyncio.sleep(0)
    
        print(f"{name}: 2")
    
        await asyncio.sleep(0)
    
        print(f"{name}: 3")
    
    
    async def main():
        tasks = [
            asyncio.create_task(worker("A")),
            asyncio.create_task(worker("B")),
            asyncio.create_task(worker("C")),
        ]
    
        await asyncio.gather(*tasks)
    
    
    asyncio.run(main())

Bạn sẽ thấy output có dạng:
    
    
    A: 1
    B: 1
    C: 1
    A: 2
    B: 2
    C: 2
    A: 3
    B: 3
    C: 3

Điều này rất thú vị.

Tại sao?

Mỗi:
    
    
    await asyncio.sleep(0)

cho phép coroutine nhường quyền.

Mental model:
    
    
    A chạy
     │
     └── await
          ↓
    B chạy
     │
     └── await
          ↓
    C chạy
     │
     └── await
          ↓
    A tiếp tục

* * *

# 11\. Cooperative Scheduling

Asyncio sử dụng mô hình:

> **Coroutine phải tự nhường quyền.**

Ví dụ:
    
    
    async def good():
        while True:
            await something()

Task thường xuyên có cơ hội nhường quyền.

Nhưng:
    
    
    async def bad():
        while True:
            do_heavy_work()

thì khác.

Nếu `do_heavy_work()` không trả quyền cho event loop, các task khác có thể bị đói.

* * *

# 12\. Blocking code phá Event Loop

Ví dụ cực kỳ nguy hiểm:
    
    
    import asyncio
    import time
    
    
    async def worker_a():
        print("A start")
    
        time.sleep(5)
    
        print("A done")
    
    
    async def worker_b():
        print("B start")
    
        await asyncio.sleep(1)
    
        print("B done")
    
    
    async def main():
        await asyncio.gather(
            worker_a(),
            worker_b(),
        )
    
    
    asyncio.run(main())

Bạn có thể mong:
    
    
    A start
    B start
    B done
    A done

Nhưng thực tế gần như:
    
    
    A start
         ↓
       block 5s
         ↓
    A done
    B start
         ↓
       1s
         ↓
    B done

Tại sao?

Vì:
    
    
    time.sleep(5)

**block thread đang chạy Event Loop.**

Event Loop không thể chuyển sang B.

* * *

# 13\. Một coroutine CPU-bound cũng có thể block loop

Ví dụ:
    
    
    async def bad():
        total = 0
    
        for i in range(100_000_000):
            total += i
    
        return total

Bạn viết `async def` nhưng không có nghĩa:

> "CPU computation tự động trở thành async."

Không.

Trong đoạn:
    
    
    for i in range(...):

coroutine đang chiếm event loop.

Không có:
    
    
    await

để nhường quyền.

* * *

# 14\. Asyncio không phải magic parallelism

Điều này cần khắc sâu:
    
    
    async def

không biến:
    
    
    CPU-bound

thành:
    
    
    parallel CPU-bound

Asyncio chủ yếu giúp:
    
    
    I/O-bound concurrency

Ví dụ:
    
    
    100 HTTP requests

rất phù hợp.

Nhưng:
    
    
    100 phép tính CPU nặng

thường không phải use case lý tưởng.

* * *

# 15\. Event Loop và timer

Khi bạn viết:
    
    
    await asyncio.sleep(3)

Event Loop có thể quản lý một timer:
    
    
    Task A
     │
     ▼
    sleep(3)
     │
     ▼
    timer scheduled
     │
     ▼
    Task A suspended
     │
     │
     │ 3 seconds
     │
     ▼
    Task A ready

Trong thời gian đó:
    
    
    Task B ────────────────►
    Task C ─────────►
    HTTP request ───────────────────►

có thể được xử lý.

* * *

# 16\. Event Loop có "ready queue"

Để hiểu sâu hơn, hãy tưởng tượng Event Loop có:
    
    
    Ready Queue
    
    ┌─────────┬─────────┬─────────┐
    │ Task A  │ Task B  │ Task C  │
    └─────────┴─────────┴─────────┘

Loop lấy task sẵn sàng:
    
    
    Task A
      │
      ▼
    execute
      │
      ├── hoàn thành
      │
      └── await
           │
           ▼
        suspended

Sau đó lấy task tiếp:
    
    
    Task B
      │
      ▼
    execute

Đây là mental model tốt để hiểu scheduling.

* * *

# 17\. Khi I/O hoàn thành

Giả sử:
    
    
    await http_request()

Task không cần chiếm CPU trong lúc server xử lý.
    
    
    Task A
      │
      ▼
    HTTP request
      │
      ▼
    waiting

Event Loop có thể theo dõi socket/network.

Khi response đến:
    
    
    Network
       │
       ▼
    response ready
       │
       ▼
    Task A ready
       │
       ▼
    Event Loop
       │
       ▼
    Task A tiếp tục

Đây là lý do asyncio cực kỳ mạnh cho network application.

* * *

# 18\. Event Loop không "chạy task khác ở giữa bất kỳ dòng nào"

Đây là một hiểu lầm quan trọng.

Ví dụ:
    
    
    async def worker():
        x = 1
        x += 1
        x += 2
        print(x)
    
        await asyncio.sleep(1)
    
        print("done")

Trong đoạn:
    
    
    x = 1
    x += 1
    x += 2
    print(x)

không có điểm `await`.

Coroutine không tự nhiên bị ngắt tại mỗi dòng để task khác chạy.

Nó thường nhường quyền tại các điểm await/yield tương ứng.

Mental model:
    
    
    worker
     │
     ├── x = 1
     ├── x += 1
     ├── x += 2
     ├── print
     │
     ▼
    await
     │
     ▼
    nhường quyền

* * *

# 19\. Đây là lý do asyncio có tính cooperative

Thread thường có preemption:
    
    
    OS Scheduler
        │
        ├── Thread A
        ├── Thread B
        └── Thread C

Hệ điều hành có thể chuyển thread.

Asyncio thì:
    
    
    Coroutine A
        │
        ▼
        await
        │
        ▼
    Event Loop
        │
        ▼
    Coroutine B

Coroutine phải có cơ hội yield control.

* * *

# 20\. `call_soon()`

Bây giờ chúng ta bắt đầu tiếp cận Event Loop trực tiếp.

Ví dụ:
    
    
    import asyncio
    
    
    def callback():
        print("Callback")
    
    
    async def main():
        loop = asyncio.get_running_loop()
    
        loop.call_soon(callback)
    
        print("Main")
    
    
    asyncio.run(main())

Kết quả thường:
    
    
    Main
    Callback

`call_soon()` đăng ký callback để chạy trong một lượt scheduling gần nhất.

Mental model:
    
    
    main()
     │
     ├── call_soon(callback)
     │
     └── print("Main")
           │
           ▼
    Event Loop
           │
           ▼
    callback()

* * *

# 21\. `call_later()`

Bạn cũng có thể đăng ký callback sau một khoảng thời gian:
    
    
    import asyncio
    
    
    def callback():
        print("Callback")
    
    
    async def main():
        loop = asyncio.get_running_loop()
    
        loop.call_later(2, callback)
    
        await asyncio.sleep(3)
    
    
    asyncio.run(main())

Mental model:
    
    
    call_later(2, callback)
            │
            ▼
    Timer
            │
            │ 2 seconds
            ▼
    callback()

* * *

# 22\. `call_at()`

Bạn có thể schedule theo thời điểm của event loop:
    
    
    loop.call_at(when, callback)

Ví dụ:
    
    
    import asyncio
    
    
    def callback():
        print("Callback")
    
    
    async def main():
        loop = asyncio.get_running_loop()
    
        when = loop.time() + 2
    
        loop.call_at(when, callback)
    
        await asyncio.sleep(3)
    
    
    asyncio.run(main())

Chú ý:
    
    
    loop.time()

không phải Unix timestamp.

Nó là một **monotonic clock** phù hợp để đo khoảng thời gian và scheduling.

* * *

# 23\. `loop.time()` vs `time.time()`

Đây là một kiến thức thực tế rất hữu ích.

### `time.time()`

Thường dùng cho:
    
    
    wall-clock time
    Unix timestamp

### `loop.time()`

Dùng cho:
    
    
    timeout
    deadline
    scheduling
    elapsed duration

Ví dụ:
    
    
    loop = asyncio.get_running_loop()
    
    deadline = loop.time() + 10

Có nghĩa:

> 10 giây kể từ thời điểm hiện tại theo clock của event loop.

* * *

# 24\. Event Loop lifecycle

Mental model đầy đủ:
    
    
                    asyncio.run(main())
                            │
                            ▼
                    Create Event Loop
                            │
                            ▼
                     Start Event Loop
                            │
                            ▼
                        main()
                            │
                  ┌─────────┼─────────┐
                  ▼         ▼         ▼
                Task A    Task B    Task C
                  │         │         │
                  └─────────┼─────────┘
                            │
                            ▼
                     main completed
                            │
                            ▼
                         Cleanup
                            │
                            ▼
                      Close Event Loop

* * *

# 25\. Đừng tự tạo Event Loop quá sớm

Người mới thường thấy:
    
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close()

và nghĩ:

> Đây mới là asyncio "đúng".

Không.

Trong ứng dụng Python hiện đại, entry point đơn giản thường là:
    
    
    asyncio.run(main())

Bạn chỉ nên thao tác trực tiếp với event loop khi thực sự cần kiểm soát lifecycle hoặc tích hợp framework/low-level API.

* * *

# 26\. `run_until_complete()`

API cũ/low-level hơn:
    
    
    loop.run_until_complete(main())

Mental model:
    
    
    run_until_complete(main)
            │
            ▼
    chạy event loop
            │
            ▼
    chờ main hoàn thành
            │
            ▼
    return result

Ví dụ:
    
    
    import asyncio
    
    
    async def main():
        await asyncio.sleep(1)
        return 42
    
    
    loop = asyncio.new_event_loop()
    
    try:
        result = loop.run_until_complete(main())
        print(result)
    finally:
        loop.close()

Nhưng đối với application code hiện đại:
    
    
    asyncio.run(main())

thường rõ ràng hơn.

* * *

# 27\. Một vấn đề bạn sẽ gặp sau này

Nếu bạn đang ở trong một event loop:
    
    
    async def main():
        asyncio.run(other())

thì không được làm như vậy.

Bạn sẽ gặp lỗi kiểu:
    
    
    RuntimeError:
    asyncio.run() cannot be called from a running event loop

Vì bạn đang có:
    
    
    Event Loop
       │
       ▼
    main()
       │
       └── asyncio.run()
              │
              └── muốn tạo event loop mới

Đây là vấn đề rất thường gặp khi làm:

  * Jupyter Notebook

  * GUI

  * web framework

  * async server

  * ứng dụng tích hợp nhiều framework




Trong async context, thường chỉ cần:
    
    
    await other()

* * *

# 28\. Ví dụ tổng hợp

Hãy đọc thật kỹ chương trình này:
    
    
    import asyncio
    
    
    async def worker(name, delay):
        print(f"{name}: start")
    
        await asyncio.sleep(delay)
    
        print(f"{name}: done")
    
    
    async def main():
        loop = asyncio.get_running_loop()
    
        print("Loop:", loop)
    
        task_a = asyncio.create_task(worker("A", 2))
        task_b = asyncio.create_task(worker("B", 1))
    
        await task_a
        await task_b
    
    
    asyncio.run(main())

Luồng thực thi:
    
    
    asyncio.run(main())
            │
            ▼
    Event Loop
            │
            ▼
    main()
            │
            ├── create Task A
            │
            ├── create Task B
            │
            ▼
    await Task A
            │
            ▼
    Event Loop
       ┌────┴────┐
       ▼         ▼
    Task A     Task B
       │         │
     sleep 2    sleep 1
       │         │
       │         ▼
       │       B done
       │
       ▼
     A done
       │
       ▼
    main done
       │
       ▼
    Event Loop shutdown

Điểm rất đáng chú ý:

Mặc dù:
    
    
    await task_a

đứng trước:
    
    
    await task_b

Task B **vẫn có thể chạy trước A hoàn thành** , bởi vì cả hai đã được schedule bằng:
    
    
    asyncio.create_task()

* * *

# 29\. `await` và `create_task()` khác nhau thế nào?

Đây là kiến thức cần nhớ từ Buổi 3.

### Chỉ await
    
    
    await worker("A", 2)
    await worker("B", 2)

Mental model:
    
    
    A ──────────
                B ──────────

### Create Task
    
    
    a = asyncio.create_task(worker("A", 2))
    b = asyncio.create_task(worker("B", 2))
    
    await a
    await b

Mental model:
    
    
    A ──────────
    B ──────────

Cả A và B đã được đưa cho Event Loop schedule.

* * *

# 30\. Thí nghiệm quan trọng

Chạy chương trình này:
    
    
    import asyncio
    
    
    async def worker(name):
        for i in range(3):
            print(name, i)
            await asyncio.sleep(0)
    
    
    async def main():
        a = asyncio.create_task(worker("A"))
        b = asyncio.create_task(worker("B"))
    
        await a
        await b
    
    
    asyncio.run(main())

Quan sát:
    
    
    A 0
    B 0
    A 1
    B 1
    A 2
    B 2

Bây giờ sửa:
    
    
    await asyncio.sleep(0)

thành:
    
    
    for _ in range(10_000_000):
        pass

Bạn sẽ thấy scheduling thay đổi hoàn toàn.

Đây chính là cách **blocking code phá event loop**.

* * *

# 31\. Debug Event Loop

Python có debug mode:
    
    
    asyncio.run(main(), debug=True)

Bạn cũng có thể bật:
    
    
    PYTHONASYNCIODEBUG=1

Debug mode rất hữu ích để phát hiện:

  * coroutine bị bỏ quên

  * callback chạy quá lâu

  * vấn đề event loop

  * một số lỗi scheduling




Khi làm ứng dụng asyncio lớn, đây là kỹ năng rất đáng biết.

* * *

# 32\. Bài tập Buổi 3

## Bài 1 — Quan sát Event Loop

Viết:
    
    
    async def main():
        loop = asyncio.get_running_loop()
    
        print(loop)

Giải thích:

  1. Event Loop được tạo ở đâu?

  2. Ai đang chạy `main()`?

  3. `get_running_loop()` lấy object nào?




* * *

## Bài 2 — `await` vs Task

Tạo:
    
    
    async def work(name, delay):
        print(f"{name} start")
        await asyncio.sleep(delay)
        print(f"{name} done")

So sánh:
    
    
    await work("A", 2)
    await work("B", 2)

với:
    
    
    a = asyncio.create_task(work("A", 2))
    b = asyncio.create_task(work("B", 2))
    
    await a
    await b

Đo thời gian cả hai.

* * *

## Bài 3 — Phát hiện blocking

Viết hai task:
    
    
    Task A:
        time.sleep(3)
    
    Task B:
        asyncio.sleep(1)

Chạy bằng `gather()`.

Giải thích tại sao B không thể chạy như bạn mong đợi.

* * *

## Bài 4 — Scheduling

Chạy:
    
    
    async def worker(name):
        for i in range(5):
            print(name, i)
            await asyncio.sleep(0)

với 3 task:
    
    
    A
    B
    C

Dự đoán output.

Sau đó bỏ:
    
    
    await asyncio.sleep(0)

và giải thích sự khác biệt.

* * *

# Bài tập Deep Dive

Hãy tự vẽ sơ đồ cho chương trình:
    
    
    import asyncio
    
    
    async def download(name, delay):
        print(f"{name}: start")
    
        await asyncio.sleep(delay)
    
        print(f"{name}: done")
    
    
    async def main():
        a = asyncio.create_task(download("A", 3))
        b = asyncio.create_task(download("B", 1))
        c = asyncio.create_task(download("C", 2))
    
        await a
        await b
        await c
    
    
    asyncio.run(main())

Sơ đồ cần thể hiện:
    
    
    asyncio.run
         ↓
    Event Loop
         ↓
    main
         ↓
    create_task
     ┌───┼───┐
     ▼   ▼   ▼
     A   B   C
     │   │   │
     ▼   ▼   ▼
    sleep
     │   │   │
     └───┼───┘
         ▼
     Event Loop
         ↓
    Task nào ready?
         ↓
    Task tiếp tục

Nếu bạn hiểu được sơ đồ này, bạn đã bắt đầu nhìn asyncio theo **cơ chế bên trong** , thay vì chỉ học API.

* * *

# Tóm tắt Buổi 3

Ba khái niệm cần thuộc:

### 1\. Coroutine
    
    
    async def foo():
        ...

là công việc async.

### 2\. Task
    
    
    asyncio.create_task(foo())

đưa coroutine vào hệ thống scheduling của event loop.

### 3\. Event Loop
    
    
    Event Loop
        │
        ├── chạy Task
        ├── xử lý await
        ├── theo dõi I/O
        ├── xử lý timer
        ├── đánh thức Task
        └── tiếp tục scheduling

Và nguyên tắc quan trọng nhất:

> **Asyncio không tạo thêm thread để chạy từng coroutine. Một event loop có thể điều phối rất nhiều task bằng cooperative scheduling; các task nhường quyền chủ yếu tại các điểm`await`.**

**Buổi 4** chúng ta sẽ đi sâu hoàn toàn vào **`asyncio.Task`** : Task lifecycle, state machine, `create_task()`, `Task.result()`, `Task.exception()`, `Task.cancel()`, callback của Task và tại sao Task là "đơn vị concurrency" cốt lõi của asyncio.