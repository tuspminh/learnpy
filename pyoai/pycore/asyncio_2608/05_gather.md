# Buổi 5 — `asyncio.gather()`, `wait()` và `as_completed()`

Đây là buổi chúng ta chuyển từ:
    
    
    Coroutine
       ↓
    Task
       ↓
    Event Loop

sang:
    
    
    Nhiều Task
       ↓
    Concurrent execution
       ↓
    Thu thập kết quả
       ↓
    Xử lý lỗi / timeout / cancellation

Ba API trọng tâm:
    
    
    asyncio.gather()
    asyncio.wait()
    asyncio.as_completed()

Chúng đều giúp quản lý **nhiều awaitable** , nhưng mục đích và hành vi rất khác nhau.

* * *

# 1\. Bài toán thực tế

Giả sử bạn cần tải 5 URL:
    
    
    URL 1 → 3 giây
    URL 2 → 1 giây
    URL 3 → 5 giây
    URL 4 → 2 giây
    URL 5 → 1 giây

Nếu chạy tuần tự:
    
    
    URL1 █████████
    URL2          ███
    URL3             ███████████████
    URL4                            ██████
    URL5                                  ███
    
    ≈ 12 giây

Nếu concurrent:
    
    
    URL1 █████████
    URL2 ███
    URL3 ███████████████
    URL4 ██████
    URL5 ███

Thời gian gần:
    
    
    ≈ 5 giây

Nhưng ngay sau đó xuất hiện một loạt câu hỏi:

> Làm sao lấy kết quả của tất cả?

> Nếu một task lỗi thì sao?

> Nếu task nhanh nhất hoàn thành trước thì sao?

> Nếu muốn xử lý từng task ngay khi nó hoàn thành thì sao?

Đây chính là lý do có `gather()`, `wait()` và `as_completed()`.

* * *

# 2\. `asyncio.gather()` — API quan trọng nhất

Ví dụ đơn giản:
    
    
    import asyncio
    
    
    async def work(name, delay):
        print(f"{name}: start")
    
        await asyncio.sleep(delay)
    
        print(f"{name}: done")
    
        return name
    
    
    async def main():
        results = await asyncio.gather(
            work("A", 3),
            work("B", 1),
            work("C", 2),
        )
    
        print(results)
    
    
    asyncio.run(main())

Output có thể:
    
    
    A: start
    B: start
    C: start
    B: done
    C: done
    A: done
    
    ['A', 'B', 'C']

Chú ý cực kỳ quan trọng:
    
    
    Thứ tự hoàn thành:
    B
    C
    A
    
    Thứ tự kết quả:
    A
    B
    C

* * *

# 3\. `gather()` giữ nguyên thứ tự input

Bạn truyền:
    
    
    asyncio.gather(
        work("A", 3),
        work("B", 1),
        work("C", 2),
    )

Kết quả:
    
    
    [
        result_A,
        result_B,
        result_C,
    ]

Không phụ thuộc task nào hoàn thành trước.

Mental model:
    
    
    Input:
    
    A ────────────────┐
    B ──────┐         │
    C ───────────┐    │
                 │    │
                 ▼    ▼
              gather()
                 │
                 ▼
            [A, B, C]

Đây là một trong những lý do `gather()` rất tiện.

* * *

# 4\. `gather()` chạy concurrent

Ví dụ:
    
    
    async def work(name, delay):
        await asyncio.sleep(delay)
        return name

Chạy:
    
    
    await asyncio.gather(
        work("A", 3),
        work("B", 2),
        work("C", 1),
    )

Không phải:
    
    
    A → B → C

mà:
    
    
    A ─────────────
    B ─────────
    C ─────

Tổng thời gian gần:
    
    
    max(3, 2, 1) = 3 giây

chứ không phải:
    
    
    3 + 2 + 1 = 6 giây

* * *

# 5\. Có cần `create_task()` trước không?

Không nhất thiết.

Bạn có thể:
    
    
    await asyncio.gather(
        work("A", 3),
        work("B", 2),
        work("C", 1),
    )

`gather()` có thể schedule các coroutine được truyền vào.

Bạn cũng có thể truyền Task:
    
    
    tasks = [
        asyncio.create_task(work("A", 3)),
        asyncio.create_task(work("B", 2)),
        asyncio.create_task(work("C", 1)),
    ]
    
    results = await asyncio.gather(*tasks)

Cả hai đều hợp lệ.

* * *

# 6\. Khi nào nên `create_task()` trước?

Khi bạn cần **quản lý Task trực tiếp**.

Ví dụ:
    
    
    task = asyncio.create_task(work())

bạn có thể:
    
    
    task.cancel()
    task.done()
    task.result()
    task.exception()
    task.get_name()

Trong khi:
    
    
    await asyncio.gather(work())

phù hợp hơn khi bạn chỉ muốn:

> Chạy một nhóm công việc concurrent và lấy kết quả.

* * *

# 7\. `gather()` với return value

Ví dụ:
    
    
    async def square(x):
        await asyncio.sleep(1)
        return x * x

Chạy:
    
    
    results = await asyncio.gather(
        square(2),
        square(3),
        square(4),
    )

Kết quả:
    
    
    [4, 9, 16]

Rất tiện cho:
    
    
    fetch users
    fetch orders
    fetch products

sau đó thu thập:
    
    
    users, orders, products = await asyncio.gather(
        fetch_users(),
        fetch_orders(),
        fetch_products(),
    )

* * *

# 8\. `gather()` và exception

Đây là phần cực kỳ quan trọng.

Ví dụ:
    
    
    async def good():
        await asyncio.sleep(1)
        return "OK"
    
    
    async def bad():
        await asyncio.sleep(2)
        raise ValueError("Something went wrong")

Chạy:
    
    
    try:
        results = await asyncio.gather(
            good(),
            bad(),
        )
    except ValueError as e:
        print(e)

Exception sẽ được propagate ra caller.

Mental model:
    
    
    good ──────── DONE
    bad  ───────────── ERROR
                        │
                        ▼
                     gather
                        │
                        ▼
                  raise exception

* * *

# 9\. Một hiểu lầm rất phổ biến

Khi một coroutine trong `gather()` lỗi:
    
    
    await asyncio.gather(
        task_a,
        task_b,
        task_c,
    )

không nên mặc định nghĩ:

> "Tất cả task còn lại tự động bị cancel ngay."

Hành vi mặc định của `gather()` cần được hiểu chính xác:

  * Exception của awaitable lỗi được propagate.

  * Các awaitable khác **không mặc định bị cancel chỉ vì một awaitable khác lỗi**.

  * Chúng có thể tiếp tục chạy.




Ví dụ:
    
    
    import asyncio
    
    
    async def slow():
        try:
            await asyncio.sleep(5)
            print("slow done")
        except asyncio.CancelledError:
            print("slow cancelled")
            raise
    
    
    async def bad():
        await asyncio.sleep(1)
        raise ValueError("boom")
    
    
    async def main():
        try:
            await asyncio.gather(
                slow(),
                bad(),
            )
        except ValueError:
            print("gather failed")
    
        await asyncio.sleep(5)
    
    
    asyncio.run(main())

`slow()` không nhất thiết bị cancel chỉ vì `bad()` lỗi.

Đây là điểm cực kỳ quan trọng khi thiết kế worker system.

* * *

# 10\. `return_exceptions=True`

Nếu muốn `gather()` biến exception thành kết quả:
    
    
    results = await asyncio.gather(
        good(),
        bad(),
        return_exceptions=True,
    )

Kết quả có thể:
    
    
    [
        "OK",
        ValueError("Something went wrong"),
    ]

Thay vì `gather()` raise ngay.

* * *

# 11\. Khi nào dùng `return_exceptions=True`?

Rất hữu ích khi xử lý batch:
    
    
    100 URL

Bạn không muốn:
    
    
    URL 27 lỗi
        ↓
    toàn bộ batch thất bại

Mà muốn:
    
    
    URL 1  → OK
    URL 2  → OK
    URL 3  → ERROR
    URL 4  → OK
    ...
    URL 100 → OK

Ví dụ:
    
    
    results = await asyncio.gather(
        *tasks,
        return_exceptions=True,
    )
    
    for result in results:
        if isinstance(result, Exception):
            print("ERROR:", result)
        else:
            print("SUCCESS:", result)

* * *

# 12\. `gather()` và cancellation

Nếu chính Task đang chờ `gather()` bị cancel, các awaitable đang được gather quản lý có thể bị cancel theo cơ chế cancellation của `gather()`.

Ví dụ:
    
    
    group = asyncio.gather(
        work("A"),
        work("B"),
        work("C"),
    )
    
    group.cancel()

Đây là lý do cancellation propagation phải được thiết kế cẩn thận trong worker system.

Chúng ta sẽ đào sâu hơn ở phần Cancellation.

* * *

# 13\. `asyncio.wait()`

Bây giờ đến API thứ hai:
    
    
    done, pending = await asyncio.wait(tasks)

Điểm khác biệt lớn:

> `wait()` trả về **hai tập hợp** :
    
    
    done
    pending

Ví dụ:
    
    
    tasks = {
        asyncio.create_task(work("A", 3)),
        asyncio.create_task(work("B", 1)),
        asyncio.create_task(work("C", 2)),
    }
    
    done, pending = await asyncio.wait(tasks)

Khi `wait()` hoàn thành:
    
    
    done
     ├── A
     ├── B
     └── C
    
    pending
     └── empty

* * *

# 14\. `wait()` không trả kết quả trực tiếp

Khác với:
    
    
    results = await asyncio.gather(...)

`wait()` trả:
    
    
    done, pending

Bạn phải lấy kết quả:
    
    
    for task in done:
        print(task.result())

* * *

# 15\. `wait()` hữu ích khi muốn kiểm soát completion

Ví dụ:
    
    
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED,
    )

Đây là một tính năng cực kỳ hữu ích.

* * *

# 16\. `FIRST_COMPLETED`

Giả sử:
    
    
    A → 5s
    B → 1s
    C → 3s

Ta chạy:
    
    
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED,
    )

Sau khoảng 1 giây:
    
    
    done
     └── B
    
    pending
     ├── A
     └── C

Đây là điểm `wait()` rất khác `gather()`.

* * *

# 17\. `FIRST_EXCEPTION`

Bạn cũng có:
    
    
    return_when=asyncio.FIRST_EXCEPTION

Nó return khi một task kết thúc với exception.

Ví dụ:
    
    
    A → 5s
    B → ERROR sau 1s
    C → 3s

thì:
    
    
    done
     └── B
    
    pending
     ├── A
     └── C

Bạn có thể tự quyết định:
    
    
    for task in pending:
        task.cancel()

Đây là một pattern rất hữu ích.

* * *

# 18\. `ALL_COMPLETED`

Mặc định:
    
    
    await asyncio.wait(tasks)

tương đương ý tưởng:
    
    
    return_when=asyncio.ALL_COMPLETED

Nó chờ tất cả Task hoàn thành.

* * *

# 19\. `wait()` cho bạn quyền kiểm soát nhiều hơn

So sánh:

### `gather()`
    
    
    tasks
      ↓
    gather
      ↓
    results

### `wait()`
    
    
    tasks
      ↓
    wait
      ↓
    ┌────────────┐
    │ done       │
    │ pending    │
    └────────────┘

`wait()` thấp tầng hơn và linh hoạt hơn.

* * *

# 20\. `asyncio.as_completed()`

Đây là API thứ ba và cực kỳ thú vị.

Mục tiêu:

> **Xử lý kết quả theo thứ tự task hoàn thành.**

Ví dụ:
    
    
    A → 3s
    B → 1s
    C → 2s

Bạn muốn:
    
    
    B result
    C result
    A result

chứ không phải:
    
    
    A result
    B result
    C result

Đây là lúc `as_completed()` rất phù hợp.

* * *

# 21\. Ví dụ `as_completed()`
    
    
    async def work(name, delay):
        await asyncio.sleep(delay)
        return name
    
    
    async def main():
        tasks = [
            asyncio.create_task(work("A", 3)),
            asyncio.create_task(work("B", 1)),
            asyncio.create_task(work("C", 2)),
        ]
    
        for task in asyncio.as_completed(tasks):
            result = await task
            print(result)

Output:
    
    
    B
    C
    A

* * *

# 22\. Đây là điểm khác biệt cực lớn

### `gather()`
    
    
    A ────────┐
    B ───┐    │
    C ─────┐  │
            ▼  ▼
         [A, B, C]

Giữ **input order**.

### `as_completed()`
    
    
    B → xử lý ngay
    C → xử lý ngay
    A → xử lý ngay

Giữ **completion order**.

* * *

# 23\. Khi nào `as_completed()` rất hữu ích?

Ví dụ crawler:
    
    
    1000 URL

Một số URL:
    
    
    0.2s
    0.4s
    1.1s
    2.3s
    5.7s

Bạn không muốn chờ tất cả 1000 URL mới xử lý kết quả.

Bạn muốn:
    
    
    URL 17 done
        ↓
    parse ngay
    
    URL 82 done
        ↓
    save ngay
    
    URL 4 done
        ↓
    save ngay

Đây là mô hình:
    
    
    Task completed
          ↓
    process result immediately
          ↓
    next completed task

Rất phù hợp với crawler, downloader, API aggregator.

* * *

# 24\. So sánh ba API

API| Kết quả| Thứ tự| Khi return  
---|---|---|---  
`gather()`| list results| Input order| Tất cả hoàn thành / exception  
`wait()`| `done`, `pending`| Không quan trọng| Tùy `return_when`  
`as_completed()`| từng awaitable| Completion order| Mỗi task hoàn thành  
  
Mental model:
    
    
    gather()
        ↓
    "Cho tôi toàn bộ kết quả"
    
    wait()
        ↓
    "Cho tôi biết task nào đã xong"
    
    as_completed()
        ↓
    "Cho tôi kết quả ngay khi từng task xong"

* * *

# 25\. Ví dụ thực tế: API Aggregator

Giả sử:
    
    
    Service A → user
    Service B → orders
    Service C → recommendations

Bạn cần tất cả:
    
    
    user, orders, recommendations = await asyncio.gather(
        get_user(),
        get_orders(),
        get_recommendations(),
    )

**`gather()` là lựa chọn tự nhiên.**

* * *

# 26\. Ví dụ thực tế: Crawler

Bạn có:
    
    
    100 URL

và muốn xử lý kết quả ngay khi URL hoàn thành:
    
    
    for task in asyncio.as_completed(tasks):
        result = await task
        save(result)

**`as_completed()` phù hợp.**

* * *

# 27\. Ví dụ thực tế: Race

Bạn có:
    
    
    Server A
    Server B
    Server C

Muốn lấy server phản hồi đầu tiên:
    
    
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED,
    )

Sau đó:
    
    
    for task in pending:
        task.cancel()

Mental model:
    
    
    A ───────────
    B ─── DONE
    C ──────────────
    
          ↓
    
    chọn B
          ↓
    cancel A
    cancel C

Đây là pattern **race**.

* * *

# 28\. Race pattern hoàn chỉnh
    
    
    async def main():
        tasks = {
            asyncio.create_task(server_a()),
            asyncio.create_task(server_b()),
            asyncio.create_task(server_c()),
        }
    
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED,
        )
    
        winner = done.pop()
    
        try:
            result = await winner
            print("Winner:", result)
        finally:
            for task in pending:
                task.cancel()
    
            await asyncio.gather(
                *pending,
                return_exceptions=True,
            )

Đây là pattern rất đáng học.

Tại sao phải:
    
    
    await asyncio.gather(
        *pending,
        return_exceptions=True,
    )

sau `cancel()`?

Để đảm bảo các Task pending thực sự được kết thúc/thu hồi và cleanup của chúng được xử lý.

* * *

# 29\. Timeout với `wait()`

Bạn có thể:
    
    
    done, pending = await asyncio.wait(
        tasks,
        timeout=3,
    )

Nếu 3 giây trôi qua mà chưa xong:
    
    
    done
     ├── Task B
     └── Task C
    
    pending
     └── Task A

Điểm quan trọng:

> `wait(timeout=...)` **không tự động cancel pending tasks**.

Bạn phải tự quyết định:
    
    
    for task in pending:
        task.cancel()

* * *

# 30\. `gather()` vs `wait(timeout)`

Ví dụ:
    
    
    await asyncio.gather(...)

có ý tưởng:

> Chờ nhóm hoàn thành.

Còn:
    
    
    done, pending = await asyncio.wait(
        tasks,
        timeout=5,
    )

có ý tưởng:

> Chờ tối đa 5 giây, sau đó nói cho tôi biết ai xong và ai chưa.

* * *

# 31\. Một ví dụ crawler hoàn chỉnh

Giả sử:
    
    
    async def fetch(url):
        ...

Tạo tasks:
    
    
    tasks = [
        asyncio.create_task(fetch(url))
        for url in urls
    ]

Sau đó xử lý completion order:
    
    
    for task in asyncio.as_completed(tasks):
        try:
            html = await task
            await save(html)
        except Exception as e:
            print("Failed:", e)

Flow:
    
    
                     URLs
                       │
                       ▼
                  create_task
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
          URL1       URL2       URL3
            │          │          │
            ▼          ▼          ▼
           HTTP       HTTP       HTTP
            │          │          │
            └──────┬───┴──────────┘
                   ▼
             as_completed()
                   │
           ┌───────┼────────┐
           ▼       ▼        ▼
        result   result   result
           │       │        │
           ▼       ▼        ▼
          save    save     save

Đây là kiến trúc rất gần với crawler thực tế.

* * *

# 32\. Nhưng có một vấn đề lớn

Bạn có:
    
    
    tasks = [
        asyncio.create_task(fetch(url))
        for url in urls
    ]

Nếu:
    
    
    urls = 1,000,000

thì bạn đang tạo:
    
    
    1,000,000 Task

Đây thường **không phải thiết kế tốt**.

Đây là lúc chúng ta sẽ cần:
    
    
    asyncio.Queue
    Semaphore
    Worker Pool
    Backpressure

Những phần này sẽ xuất hiện ở các buổi sau.

* * *

# 33\. `gather()` không phải Worker Pool

Sai mental model:
    
    
    gather(1,000,000 tasks)

không có nghĩa:
    
    
    chỉ chạy 20 task một lúc

Nếu muốn giới hạn concurrency:
    
    
    1000 URL
         ↓
    20 workers
         ↓
    Queue

chúng ta sẽ học `Semaphore` và `Queue`.

* * *

# 34\. Pattern `gather()` cho batch nhỏ

Ví dụ:
    
    
    async def process_batch(items):
        return await asyncio.gather(
            *(process(item) for item in items)
        )

Phù hợp khi batch có kích thước vừa phải.

Ví dụ:
    
    
    20
    50
    100

Nhưng không nên vô tư:
    
    
    1,000,000

* * *

# 35\. Pattern `as_completed()` cho streaming result

Ví dụ:
    
    
    async def process_all(items):
        tasks = [
            asyncio.create_task(process(item))
            for item in items
        ]
    
        for task in asyncio.as_completed(tasks):
            result = await task
            yield result

Đây là bước đầu tiên tiến tới:

> **Async streaming pipeline**

* * *

# 36\. Một điểm rất quan trọng về exception

Với:
    
    
    for task in asyncio.as_completed(tasks):
        result = await task

nếu một task lỗi:
    
    
    try:
        result = await task
    except Exception as e:
        ...

Bạn xử lý **từng task độc lập**.

Điều này rất phù hợp batch processing.

* * *

# 37\. Bài tập 1 — `gather()`

Viết:
    
    
    async def work(name, delay):
        ...

Tạo:
    
    
    A → 3s
    B → 1s
    C → 2s

Dùng:
    
    
    asyncio.gather()

và chứng minh:
    
    
    Completion order:
    B
    C
    A
    
    Result order:
    A
    B
    C

* * *

# 38\. Bài tập 2 — Exception

Tạo 3 task:
    
    
    A → success
    B → exception
    C → success

Thử:
    
    
    await asyncio.gather(...)

Sau đó thử:
    
    
    await asyncio.gather(
        ...,
        return_exceptions=True,
    )

So sánh kết quả.

* * *

# 39\. Bài tập 3 — `wait()`

Tạo:
    
    
    A → 5s
    B → 1s
    C → 3s

Dùng:
    
    
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED,
    )

Sau 1 giây phải có:
    
    
    done:
        B
    
    pending:
        A
        C

Sau đó cancel pending.

* * *

# 40\. Bài tập 4 — `as_completed()`

Tạo:
    
    
    A → 3s
    B → 1s
    C → 2s

Dùng:
    
    
    for task in asyncio.as_completed(tasks):
        ...

Mục tiêu:
    
    
    B
    C
    A

* * *

# 41\. Bài tập 5 — Race

Giả lập 3 API:
    
    
    server_a → 5s
    server_b → 2s
    server_c → 4s

Yêu cầu:
    
    
    1. Chạy cả 3 concurrent
    2. Lấy server phản hồi đầu tiên
    3. Cancel 2 server còn lại
    4. Cleanup đúng cách

Đây là bài tập rất tốt để hiểu:
    
    
    wait()
    cancel()
    gather()

kết hợp với nhau.

* * *

# 42\. Bài tập Deep Dive — Async URL Checker

Đây là mini-project cuối buổi.

Cho:
    
    
    urls = [
        "https://example.com",
        "https://python.org",
        "https://github.com",
        ...
    ]

Giả lập `fetch()` bằng:
    
    
    async def fetch(url):
        ...

Yêu cầu:
    
    
    1. Tạo Task cho mỗi URL
    2. Chạy concurrent
    3. Dùng as_completed()
    4. URL nào hoàn thành thì in ngay
    5. URL lỗi không làm dừng toàn bộ
    6. Đếm:
       - success
       - failed
    7. Đo tổng thời gian

Kết quả mong muốn:
    
    
    [OK] https://example.com
    [OK] https://python.org
    [ERROR] https://...
    [OK] https://github.com
    
    Finished: 4/5
    Success: 4
    Failed: 1
    Elapsed: 2.31s

* * *

# 43\. Ba API — Mental Model cuối buổi

Đây là phần bạn nên thuộc lòng.

### `gather()`
    
    
    "Tôi cần tất cả kết quả."
    
    A ──────┐
    B ───┐  │
    C ─────┘
           ↓
     [A, B, C]

**Giữ thứ tự input.**

* * *

### `wait()`
    
    
    "Tôi muốn biết task nào đã xong."
    
            tasks
              │
            wait()
              │
         ┌────┴────┐
         ▼         ▼
       done      pending

**Cho phép kiểm soát thời điểm return.**

* * *

### `as_completed()`
    
    
    "Tôi muốn xử lý ngay khi task hoàn thành."
    
    B ──► result
    C ──► result
    A ──► result

**Theo completion order.**

* * *

# 44\. Cheat Sheet
    
    
    # Tất cả kết quả, giữ input order
    results = await asyncio.gather(
        coro1(),
        coro2(),
        coro3(),
    )
    
    
    # Không làm gather fail khi có exception
    results = await asyncio.gather(
        coro1(),
        coro2(),
        return_exceptions=True,
    )
    
    
    # Kiểm soát done / pending
    done, pending = await asyncio.wait(tasks)
    
    
    # Return khi task đầu tiên hoàn thành
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED,
    )
    
    
    # Xử lý theo completion order
    for task in asyncio.as_completed(tasks):
        result = await task

* * *

# 45\. Kiến trúc chúng ta đang tiến tới

Đến thời điểm này bạn đã có:
    
    
                     asyncio
                        │
                 ┌──────┴──────┐
                 ▼             ▼
            Coroutine         Task
                                │
                                ▼
                           Event Loop
                                │
                     ┌──────────┼──────────┐
                     ▼          ▼          ▼
                  gather      wait   as_completed

Nhưng vẫn còn một vấn đề lớn:

> **Nếu tôi có 100.000 URL thì có nên tạo 100.000 Task cùng lúc không?**

Câu trả lời thường là **không**.

Chúng ta cần kiểm soát concurrency:
    
    
    100,000 jobs
          │
          ▼
       Queue
          │
          ▼
    20 Workers
          │
          ▼
    20 concurrent operations

Đó chính là lý do **Buổi 6** sẽ chuyển sang một chủ đề rất quan trọng:

# `await` Deep Dive + Cooperative Scheduling

Chúng ta sẽ mổ xẻ chính xác hơn chuyện gì xảy ra khi:
    
    
    await something()

đặc biệt là:
    
    
    Coroutine
       ↓
    await
       ↓
    Future
       ↓
    yield control
       ↓
    Event Loop
       ↓
    I/O readiness
       ↓
    resume coroutine

và từ đó chuẩn bị nền tảng để học **timeout, cancellation, semaphore và asyncio.Queue** một cách thực sự chắc chắn.