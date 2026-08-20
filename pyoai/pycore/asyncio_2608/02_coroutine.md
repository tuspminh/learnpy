# Buổi 2 — Coroutine Deep Dive

Ở buổi 1, bạn đã thấy:
    
    
    async def hello():
        ...

và:
    
    
    await hello()

Nhưng để thực sự làm chủ `asyncio`, chúng ta phải hiểu một câu hỏi rất quan trọng:

> **`async def` tạo ra cái gì?**

Câu trả lời: **`async def` tạo ra một coroutine function; khi gọi function đó, ta nhận được một coroutine object.**

Đây là nền tảng để hiểu `Task`, `create_task()`, `gather()` và Event Loop.

* * *

# 1\. Function bình thường

Xét function thông thường:
    
    
    def hello():
        return "Hello"
    
    
    result = hello()
    
    print(result)

Kết quả:
    
    
    Hello

Khi:
    
    
    result = hello()

function được **thực thi ngay**.

Có thể hình dung:
    
    
    hello()
       │
       ▼
    function chạy
       │
       ▼
    return "Hello"
       │
       ▼
    result

* * *

# 2\. `async def` khác hoàn toàn

Bây giờ:
    
    
    async def hello():
        return "Hello"

Nếu viết:
    
    
    result = hello()
    
    print(result)

Bạn sẽ không nhận được:
    
    
    Hello

mà đại loại:
    
    
    <coroutine object hello at 0x...>

Tại sao?

Bởi vì:
    
    
    async def hello():

không tạo một function bình thường.

Nó tạo:

> **coroutine function**

Và:
    
    
    hello()

tạo:

> **coroutine object**

* * *

# 3\. Kiểm tra bằng `inspect`
    
    
    import inspect
    
    
    async def hello():
        return "Hello"
    
    
    print(inspect.iscoroutinefunction(hello))
    
    coro = hello()
    
    print(inspect.iscoroutine(coro))

Kết quả:
    
    
    True
    True

Ta có:
    
    
    hello
     │
     │ async def
     ▼
    Coroutine Function
     │
     │ hello()
     ▼
    Coroutine Object

Đây là distinction cực kỳ quan trọng.

* * *

# 4\. Coroutine chưa chạy

Đây là một hiểu lầm rất phổ biến.
    
    
    import asyncio
    
    
    async def hello():
        print("Hello")
    
    
    coro = hello()
    
    print("Created")

Bạn có thể nghĩ:
    
    
    Hello
    Created

Nhưng thực tế:
    
    
    Created

và Python có thể cảnh báo:
    
    
    RuntimeWarning: coroutine 'hello' was never awaited

Tại sao?

Bởi vì:
    
    
    coro = hello()

**chưa chạy`hello()`**.

Nó chỉ tạo coroutine object.

* * *

# 5\. Coroutine giống như một "kế hoạch thực thi"

Bạn có thể hình dung:
    
    
    coro = hello()

giống như:

> "Đây là công việc `hello`, tôi đã tạo nó nhưng chưa yêu cầu event loop thực thi."
    
    
    async def hello()
           │
           ▼
      Coroutine Function
           │
         hello()
           │
           ▼
      Coroutine Object
           │
           │ chưa chạy
           ▼
          await
           │
           ▼
       bắt đầu chạy

Đây là mental model rất quan trọng.

* * *

# 6\. `await` làm gì?

Ví dụ:
    
    
    import asyncio
    
    
    async def hello():
        print("Hello")
        await asyncio.sleep(1)
        print("World")
    
    
    async def main():
        await hello()
    
    
    asyncio.run(main())

Luồng thực thi:
    
    
    asyncio.run(main())
            │
            ▼
          main()
            │
            ▼
       await hello()
            │
            ▼
          hello()
            │
            ▼
       print("Hello")
            │
            ▼
     await sleep(1)
            │
            │
            │ nhường quyền
            ▼
       sau 1 giây
            │
            ▼
     print("World")

* * *

# 7\. `await` không có nghĩa đơn giản là "đợi"

Người mới thường học:

> `await` = chờ.

Cách hiểu này **chưa đủ chính xác**.

Trong asyncio, `await` về bản chất cho phép coroutine:

> **tạm dừng việc thực thi và trao quyền cho event loop xử lý công việc khác.**

Ví dụ:
    
    
    async def task_a():
        print("A start")
        await asyncio.sleep(2)
        print("A done")

Khi A chạy đến:
    
    
    await asyncio.sleep(2)

A tạm dừng.

Event loop có thể chạy:
    
    
    Task A
      │
      ▼
    await sleep
      │
      │ pause
      ▼
    Task B
      │
      ▼
    await ...
      │
      ▼
    Task C

Sau khi 2 giây trôi qua, A có thể tiếp tục.

* * *

# 8\. Coroutine phải được await

Ví dụ:
    
    
    async def hello():
        return 42
    
    
    async def main():
        result = await hello()
    
        print(result)

Kết quả:
    
    
    42

Ở đây:
    
    
    hello()

tạo coroutine object.

Sau đó:
    
    
    await hello()

yêu cầu coroutine thực thi và lấy kết quả.

* * *

# 9\. Không thể `await` ở mọi nơi

Đoạn này sai:
    
    
    async def hello():
        return 42
    
    
    result = await hello()

Nếu đặt ở module bình thường, Python sẽ báo lỗi vì `await` chỉ được sử dụng trong **async context**.

Thông thường:
    
    
    async def main():
        result = await hello()

rồi:
    
    
    asyncio.run(main())

* * *

# 10\. Coroutine function vs coroutine object

Hãy phân biệt thật chắc:

### Coroutine function
    
    
    async def download():
        ...

`download` là:
    
    
    coroutine function

### Coroutine object
    
    
    coro = download()

`coro` là:
    
    
    coroutine object

Có thể kiểm tra:
    
    
    import inspect
    
    print(inspect.iscoroutinefunction(download))
    print(inspect.iscoroutine(coro))

Kết quả:
    
    
    True
    True

* * *

# 11\. Coroutine object có thể được await
    
    
    async def hello():
        return "Hello"
    
    
    async def main():
        coro = hello()
    
        result = await coro
    
        print(result)

Kết quả:
    
    
    Hello

Ở đây:
    
    
    hello
     │
     ▼
    coroutine function
    
    hello()
     │
     ▼
    coroutine object
    
    await coro
     │
     ▼
    thực thi coroutine
     │
     ▼
    "Hello"

* * *

# 12\. Một coroutine thường chỉ được await một lần

Đây là một quy tắc cực kỳ quan trọng.
    
    
    async def hello():
        return "Hello"
    
    
    async def main():
        coro = hello()
    
        print(await coro)
        print(await coro)

Lần thứ hai sẽ lỗi:
    
    
    RuntimeError: cannot reuse already awaited coroutine

Vì coroutine object đại diện cho **một execution cụ thể**.

* * *

# 13\. Muốn chạy lại thì tạo coroutine mới

Sai:
    
    
    coro = hello()
    
    await coro
    await coro

Đúng:
    
    
    await hello()
    await hello()

Mỗi lần:
    
    
    hello()

tạo một coroutine object mới.
    
    
    hello()
       │
       ▼
    Coroutine A
       │
     await
       ▼
    done
    
    hello()
       │
       ▼
    Coroutine B
       │
     await
       ▼
    done

* * *

# 14\. Coroutine có thể trả về giá trị

Ví dụ:
    
    
    async def add(a, b):
        return a + b
    
    
    async def main():
        result = await add(10, 20)
    
        print(result)
    
    
    asyncio.run(main())

Kết quả:
    
    
    30

Về mặt ý tưởng:
    
    
    Coroutine
       │
       ▼
    return value
       │
       ▼
    await
       │
       ▼
    caller nhận value

* * *

# 15\. Coroutine có thể gọi coroutine khác

Ví dụ:
    
    
    async def get_name():
        return "Alice"
    
    
    async def greeting():
        name = await get_name()
    
        return f"Hello {name}"
    
    
    async def main():
        result = await greeting()
    
        print(result)

Luồng:
    
    
    main
     │
     └── await greeting
             │
             └── await get_name
                      │
                      ▼
                   "Alice"
                      │
                      ▼
              "Hello Alice"
                      │
                      ▼
                    main

Đây gọi là **coroutine composition**.

* * *

# 16\. Coroutine không đồng nghĩa với concurrency

Đây là điểm quan trọng nhất của buổi hôm nay.

Bạn có:
    
    
    async def task(name):
        print(name)
        await asyncio.sleep(1)

và:
    
    
    await task("A")
    await task("B")
    await task("C")

Đây vẫn là:
    
    
    A
    ↓
    B
    ↓
    C

Tuần tự.

`async def` **không tự động tạo concurrency**.

* * *

# 17\. Muốn concurrency: Task

Ví dụ:
    
    
    async def task(name):
        print(f"{name} start")
    
        await asyncio.sleep(2)
    
        print(f"{name} done")

Tạo Task:
    
    
    task_a = asyncio.create_task(task("A"))
    task_b = asyncio.create_task(task("B"))
    task_c = asyncio.create_task(task("C"))

Sau đó:
    
    
    await task_a
    await task_b
    await task_c

Bây giờ event loop đã có nhiều task để schedule.
    
    
    Event Loop
        │
        ├── Task A
        ├── Task B
        └── Task C

Đây là chủ đề của **Buổi 4 — Task Deep Dive** , nhưng bạn cần biết khái niệm này từ bây giờ.

* * *

# 18\. Coroutine vs Task

Đây là bảng cần nhớ:

| Coroutine| Task  
---|---|---  
Tạo bằng| `async_func()`| `create_task()`  
Có thể await| ✅| ✅  
Tự được event loop schedule| Không trực tiếp| ✅  
Có trạng thái| Execution object| Managed coroutine execution  
Có `.cancel()`| ❌| ✅  
Có `.result()`| ❌| ✅  
Có `.exception()`| ❌| ✅  
  
Mental model:
    
    
    Coroutine
        │
        │ create_task()
        ▼
      Task
        │
        ▼
    Event Loop scheduling

* * *

# 19\. `asyncio.run()` nằm ở đâu?

Một chương trình thực tế thường có:
    
    
    async def main():
        ...

và:
    
    
    asyncio.run(main())

Mental model:
    
    
    asyncio.run()
          │
          ▼
     Event Loop
          │
          ▼
      main coroutine
          │
          ├── await coroutine A
          ├── create Task B
          ├── create Task C
          └── ...

`asyncio.run()` là cầu nối giữa:
    
    
    Python synchronous world
              │
              ▼
         asyncio world

* * *

# 20\. Kiểm tra coroutine bằng `type()`

Bạn hãy chạy:
    
    
    import asyncio
    
    
    async def hello():
        return "Hello"
    
    
    print(type(hello()))
    
    asyncio.run(hello())

Bạn sẽ thấy một type tương tự:
    
    
    <class 'coroutine'>

Điều này rất quan trọng:
    
    
    hello

là function.
    
    
    hello()

là coroutine object.

* * *

# 21\. Một lỗi kinh điển

Đừng viết:
    
    
    async def get_data():
        return [1, 2, 3]
    
    
    data = get_data()
    
    for item in data:
        print(item)

`data` không phải list.

Nó là:
    
    
    coroutine object

Phải:
    
    
    async def main():
        data = await get_data()
    
        for item in data:
            print(item)

* * *

# 22\. Một lỗi còn nguy hiểm hơn
    
    
    async def download():
        ...
    
    
    async def main():
        download()

Coroutine được tạo nhưng không được await/schedule.

Bạn có thể nhận:
    
    
    RuntimeWarning:
    coroutine 'download' was never awaited

Do đó, khi thấy:
    
    
    something()

và `something` là async function, hãy tự hỏi:

> "Coroutine này được await hoặc schedule ở đâu?"

* * *

# 23\. Quy tắc vàng của Coroutine

Hãy ghi nhớ 5 quy tắc:

### Quy tắc 1
    
    
    async def

tạo **coroutine function**.

### Quy tắc 2
    
    
    func()

với async function tạo **coroutine object**.

### Quy tắc 3

Coroutine object **không tự chạy** chỉ vì bạn tạo nó.

### Quy tắc 4

Muốn chạy coroutine:
    
    
    await coro

hoặc schedule nó:
    
    
    asyncio.create_task(coro)

### Quy tắc 5

Một coroutine object không thể được await lại sau khi đã hoàn thành.

* * *

# 24\. Bài thực hành

## Bài 1 — Phân biệt type

Viết:
    
    
    async def foo():
        return 100

Sau đó kiểm tra:
    
    
    type(foo)
    type(foo())

và giải thích tại sao hai kết quả khác nhau.

* * *

## Bài 2 — Coroutine chưa chạy

Viết:
    
    
    async def hello():
        print("Hello")
    
    
    coro = hello()
    
    print("Created")

Dự đoán output trước khi chạy.

Sau đó giải thích warning nếu có.

* * *

## Bài 3 — Await

Viết:
    
    
    async def calculate():
        return 10 * 20

Sau đó dùng `await` để lấy kết quả:
    
    
    200

* * *

## Bài 4 — Coroutine composition

Tạo:
    
    
    get_user()
        ↓
    get_orders()
        ↓
    calculate_total()

Tất cả đều là coroutine.

Mục tiêu:
    
    
    main()
      ↓
    await get_user()
      ↓
    await get_orders()
      ↓
    await calculate_total()

* * *

# Bài tập quan trọng nhất

Hãy dự đoán thời gian chạy đoạn này:
    
    
    import asyncio
    import time
    
    
    async def work(name, delay):
        print(f"{name} start")
    
        await asyncio.sleep(delay)
    
        print(f"{name} done")
    
    
    async def main():
        await work("A", 3)
        await work("B", 2)
        await work("C", 1)
    
    
    start = time.perf_counter()
    
    asyncio.run(main())
    
    print(time.perf_counter() - start)

Sau đó sửa `main()` để A, B, C chạy concurrent bằng:
    
    
    asyncio.create_task()

và kiểm tra thời gian.

**Nếu bạn hiểu được bài này, bạn đã nắm được sự khác nhau giữa`coroutine` và `concurrency`.**

* * *

## Tóm tắt Buổi 2

Mental model cuối buổi:
    
    
    async def foo()
           │
           ▼
    Coroutine Function
           │
           │ foo()
           ▼
    Coroutine Object
           │
           ├───────────────┐
           │               │
        await           create_task
           │               │
           ▼               ▼
       execution          Task
                           │
                           ▼
                      Event Loop

**Buổi 3** chúng ta sẽ đi vào phần quan trọng nhất của asyncio:

# Event Loop Deep Dive

Không chỉ dùng:
    
    
    asyncio.run(main())

mà sẽ tìm hiểu **event loop thực sự làm gì** , `run_until_complete()`, `get_running_loop()`, scheduling, ready queue, I/O waiting và cách event loop chuyển quyền giữa các Task.