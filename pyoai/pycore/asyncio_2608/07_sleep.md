# Buổi 7 — `asyncio.sleep()` và Cooperative Scheduling

Hôm nay chúng ta **chỉ tập trung vào `sleep()` và cooperative scheduling**, bám đúng roadmap.

Buổi 6 chúng ta đã hiểu:

```text
await
 ↓
coroutine tạm dừng
 ↓
Event Loop lấy quyền điều khiển
```

Hôm nay đào sâu câu hỏi:

> **Event Loop thực sự làm gì trong khoảng thời gian coroutine đang `await asyncio.sleep()`?**

---

# 1. `asyncio.sleep()` là gì?

Cú pháp:

```python
await asyncio.sleep(delay)
```

Ví dụ:

```python
import asyncio


async def main():
    print("A")

    await asyncio.sleep(2)

    print("B")


asyncio.run(main())
```

Kết quả:

```text
A
... chờ 2 giây ...
B
```

Nhưng **không phải thread bị block 2 giây**.

Đây là điểm quan trọng nhất.

---

# 2. `time.sleep()` vs `asyncio.sleep()`

## `time.sleep()`

```python
import time

time.sleep(2)
```

Thread thực sự bị block:

```text
Thread
│
├── time.sleep()
│   ███████████████
│
└── không làm việc khác
```

---

## `asyncio.sleep()`

```python
await asyncio.sleep(2)
```

Coroutine bị suspend:

```text
Coroutine A
│
├── await sleep(2)
│
└── SUSPENDED

Event Loop
│
├── Task B
├── Task C
├── Task D
└── xử lý I/O
```

Thread vẫn hoạt động.

---

# 3. Ví dụ chứng minh

```python
import asyncio


async def worker(name):
    for i in range(3):
        print(name, i)
        await asyncio.sleep(1)


async def main():
    await asyncio.gather(
        worker("A"),
        worker("B"),
    )


asyncio.run(main())
```

Kết quả:

```text
A 0
B 0

A 1
B 1

A 2
B 2
```

Hai coroutine không chạy:

```text
A → đợi 1s → B → đợi 1s → A...
```

Mà:

```text
A chạy
 ↓
await sleep
 ↓
B chạy
 ↓
await sleep
 ↓
Event Loop chờ timer
 ↓
A ready
 ↓
B ready
```

---

# 4. `sleep()` tạo ra một điểm nhường quyền

Đây là khái niệm:

# Cooperative Scheduling

Các coroutine **tự nguyện nhường quyền** cho Event Loop.

Ví dụ:

```python
async def worker():
    print("A")

    await asyncio.sleep(1)

    print("B")
```

Có thể hình dung:

```text
worker
  │
  ▼
print("A")
  │
  ▼
await sleep(1)
  │
  │ yield control
  ▼
Event Loop
```

Sau 1 giây:

```text
Timer expired
      │
      ▼
Task ready
      │
      ▼
resume coroutine
      │
      ▼
print("B")
```

---

# 5. Tại sao gọi là "cooperative"?

Bởi vì Task phải **hợp tác**.

Ví dụ:

```python
async def worker():
    for i in range(10):
        print(i)
        await asyncio.sleep(0)
```

Task nói với Event Loop:

> "Tôi làm xong một chút rồi, cho task khác chạy đi."

---

# 6. Nếu không `await` thì sao?

Xét:

```python
async def worker(name):
    for i in range(5):
        print(name, i)
```

Sau đó:

```python
await asyncio.gather(
    worker("A"),
    worker("B"),
)
```

Bạn có thể thấy:

```text
A 0
A 1
A 2
A 3
A 4
B 0
B 1
B 2
B 3
B 4
```

Tại sao?

Bởi vì:

```text
Task A
████████████████████
```

không có điểm nhường quyền.

Task B phải đợi A chạy xong.

---

# 7. Thêm `sleep(0)`

```python
async def worker(name):
    for i in range(5):
        print(name, i)
        await asyncio.sleep(0)
```

Bây giờ:

```text
A 0
B 0
A 1
B 1
A 2
B 2
A 3
B 3
A 4
B 4
```

`asyncio.sleep(0)` trở thành một điểm:

```text
yield control
```

---

# 8. `sleep(0)` có thực sự "ngủ" không?

Đây là một chi tiết quan trọng.

```python
await asyncio.sleep(0)
```

không có nghĩa:

> "Đợi 0 giây rồi tiếp tục."

Mental model hữu ích hơn:

> **"Tạm nhường quyền cho Event Loop."**

Nó cho Event Loop cơ hội xử lý những việc khác.

---

# 9. `sleep(0)` rất hữu ích để minh họa scheduling

Ví dụ:

```python
import asyncio


async def worker(name):
    for i in range(5):
        print(name, i)
        await asyncio.sleep(0)


async def main():
    await asyncio.gather(
        worker("A"),
        worker("B"),
        worker("C"),
    )


asyncio.run(main())
```

Mental model:

```text
A → print → yield
B → print → yield
C → print → yield

A → print → yield
B → print → yield
C → print → yield
```

---

# 10. Nhưng `sleep(0)` không phải magic

Đừng nghĩ:

```python
await asyncio.sleep(0)
```

sẽ biến:

```python
for i in range(1_000_000_000):
    ...
```

thành code nhanh hơn.

Nó chỉ giúp:

```text
CPU work
 ↓
yield
 ↓
CPU work
 ↓
yield
```

Tổng lượng CPU work vẫn như cũ.

---

# 11. Cooperative scheduling khác Preemptive Scheduling

Có hai mô hình quan trọng.

## Cooperative

```text
Task A
   │
   └── await
         ↓
      Task B
```

Task A chủ động nhường.

Asyncio chủ yếu hoạt động theo mô hình này.

---

## Preemptive

Operating System có thể ngắt thread:

```text
Thread A
██████
      ↓
      scheduler ngắt
             ↓
Thread B
██████
```

Thread không cần tự gọi `await`.

Đây là mô hình quen thuộc của OS threads.

---

# 12. Vì sao cooperative scheduling hiệu quả?

Bởi vì Event Loop không phải liên tục cưỡng chế chuyển context giữa các coroutine.

Coroutine chỉ nhường khi cần:

```text
await I/O
await sleep
await Queue.get()
await Event.wait()
...
```

Đặc biệt tốt cho workload:

```text
HTTP
Database
Socket
WebSocket
Message Queue
```

---

# 13. Event Loop và Timer

Khi bạn:

```python
await asyncio.sleep(5)
```

Event Loop không phải:

```text
sleep thread 5 seconds
```

Thay vào đó, mental model:

```text
Task A
  │
  ▼
sleep(5)
  │
  ▼
đăng ký timer
  │
  ▼
Task A suspended
```

Event Loop tiếp tục:

```text
Task B
Task C
I/O
Task D
...
```

Khi timer đến hạn:

```text
5 seconds elapsed
        │
        ▼
Task A ready
```

---

# 14. Timer không đảm bảo Task chạy chính xác tại thời điểm đó

Ví dụ:

```python
await asyncio.sleep(1)
```

Không nên hiểu là:

> Sau chính xác 1.000000 giây, dòng tiếp theo chắc chắn chạy.

Chính xác hơn:

> Sau khoảng thời gian đó, Task có thể trở thành **ready để được chạy**.

Nếu Event Loop đang bận:

```text
Task A
   │
   └── sleep(1)
           │
           ▼
        timer done
           │
           ▼
        READY
           │
           │ nhưng Event Loop
           │ đang xử lý task khác
           ▼
       chạy sau đó
```

---

# 15. Đây là một khái niệm rất quan trọng

```text
sleep expired
     ≠
code executes immediately
```

Mà:

```text
sleep expired
     ↓
Task becomes runnable
     ↓
Event Loop schedules it
     ↓
Task resumes
```

Đây là cách suy nghĩ chính xác hơn.

---

# 16. Ví dụ

```python
async def worker():
    print("A")

    await asyncio.sleep(1)

    print("B")
```

Ta không nên nói:

```text
A
1 giây
B
```

một cách tuyệt đối.

Nên nói:

```text
A
 ↓
Task suspended khoảng 1 giây
 ↓
Task trở lại trạng thái ready
 ↓
Event Loop resume Task
 ↓
B
```

---

# 17. Scheduling order không nên được coi là API contract

Ví dụ:

```python
async def a():
    print("A")
    await asyncio.sleep(0)
    print("A2")


async def b():
    print("B")
    await asyncio.sleep(0)
    print("B2")
```

Có thể thấy:

```text
A
B
A2
B2
```

Nhưng khi xây ứng dụng thực tế:

> **Không nên dựa vào thứ tự scheduling nội bộ nếu API không đảm bảo nó.**

Hãy thiết kế dựa trên synchronization primitives:

```text
Event
Lock
Queue
Semaphore
Condition
```

chứ không dựa vào:

```text
"Task A chắc chắn chạy trước Task B"
```

---

# 18. Starvation

Một khái niệm quan trọng:

# Event Loop Starvation

Ví dụ:

```python
async def bad_task():
    while True:
        do_heavy_work()
```

Không có:

```python
await
```

Task này có thể giữ Event Loop quá lâu.

```text
Event Loop
│
▼
bad_task
████████████████████████████
████████████████████████████
████████████████████████████

Task B
      X

Task C
      X
```

Các Task khác không có cơ hội chạy.

---

# 19. Đây là lỗi rất nguy hiểm

Bạn có thể có code hoàn toàn hợp lệ về syntax:

```python
async def process():
    for item in huge_dataset:
        expensive_operation(item)
```

nhưng lại phá hỏng hiệu năng asyncio.

Không phải cứ:

```python
async def
```

thì ứng dụng tự nhiên non-blocking.

---

# 20. Cách giảm starvation

Nếu công việc có thể chia nhỏ:

```python
async def process():
    for i, item in enumerate(items):
        process_item(item)

        if i % 100 == 0:
            await asyncio.sleep(0)
```

Bây giờ:

```text
100 items
   ↓
yield
   ↓
100 items
   ↓
yield
```

Task khác có cơ hội chạy.

Nhưng nhớ:

> Đây là giải pháp scheduling, **không phải giải pháp tối ưu CPU**.

Nếu công việc thực sự CPU-bound, hãy xem xét:

```text
ProcessPoolExecutor
```

hoặc thiết kế lại workload.

---

# 21. `asyncio.sleep()` không chỉ dùng để delay

Nó thường có 3 mục đích.

### 1. Delay

```python
await asyncio.sleep(5)
```

### 2. Polling

```python
while True:
    check_status()

    await asyncio.sleep(1)
```

### 3. Yield control

```python
await asyncio.sleep(0)
```

Ba trường hợp này rất khác nhau về ý nghĩa.

---

# 22. Polling pattern

Ví dụ bạn có job:

```text
job_id = 123
```

Bạn muốn kiểm tra:

```python
while True:
    status = await get_status(job_id)

    if status == "done":
        break

    await asyncio.sleep(1)
```

Flow:

```text
check
 ↓
not done
 ↓
sleep 1s
 ↓
check
 ↓
not done
 ↓
sleep 1s
 ↓
check
 ↓
done
```

Đây là polling bất đồng bộ.

---

# 23. Sai lầm: polling bằng `time.sleep()`

Không nên:

```python
while True:
    status = await get_status()

    if status == "done":
        break

    time.sleep(1)
```

Vì:

```text
time.sleep(1)
```

block Event Loop.

Nên:

```python
await asyncio.sleep(1)
```

---

# 24. Một ví dụ thực tế với crawler

Giả sử crawler có:

```text
worker
 ↓
crawl URL
 ↓
server trả 429
 ↓
đợi
 ↓
retry
```

Ta có:

```python
async def fetch_with_retry(url):
    for attempt in range(3):
        response = await fetch(url)

        if response.status != 429:
            return response

        await asyncio.sleep(2)

    raise RuntimeError("Failed")
```

Trong lúc retry delay:

```text
Worker A
   ↓
await sleep(2)
   │
   ├── Worker B
   ├── Worker C
   ├── Worker D
   └── Worker E
```

Đây chính là async scheduling có ích trong thực tế.

---

# 25. Exponential Backoff

Một pattern rất quan trọng:

```python
delay = 1

for attempt in range(5):
    try:
        return await fetch()
    except TemporaryError:
        await asyncio.sleep(delay)
        delay *= 2
```

Timeline:

```text
1s
2s
4s
8s
16s
```

Đây là nền tảng rất quan trọng khi xây:

```text
Crawler
API client
Queue worker
Retry system
Distributed worker
```

---

# 26. `sleep()` và cancellation

Một điểm chúng ta **chưa đào sâu** hôm nay:

```python
await asyncio.sleep(10)
```

Task có thể bị cancel trong lúc đang sleep.

Ví dụ:

```python
task.cancel()
```

Task sẽ không nhất thiết chờ hết 10 giây.

Nó có thể nhận:

```python
asyncio.CancelledError
```

Đây là nội dung chính của:

# Buổi 9 — Cancellation

Hôm nay chỉ cần nhớ:

```text
sleep()
 ↓
await
 ↓
Task có thể bị cancel
```

---

# 27. `sleep()` và timeout

Tương tự:

```python
await asyncio.sleep(10)
```

có thể nằm bên trong timeout scope.

Ví dụ:

```python
async with asyncio.timeout(3):
    await asyncio.sleep(10)
```

Task có thể bị timeout sau khoảng 3 giây.

Nhưng **chúng ta chưa phân tích timeout hôm nay**.

Đó là Buổi 8.

---

# 28. Bài tập 1 — Cooperative Scheduling

Viết:

```python
async def worker(name):
    for i in range(5):
        print(name, i)
        await asyncio.sleep(0)
```

Chạy:

```python
await asyncio.gather(
    worker("A"),
    worker("B"),
    worker("C"),
)
```

Quan sát thứ tự.

Sau đó thử:

```python
await asyncio.sleep(0.1)
```

So sánh với:

```python
await asyncio.sleep(0)
```

---

# 29. Bài tập 2 — Chứng minh Event Loop không block

Viết:

```python
async def sleeper():
    print("sleeper start")

    await asyncio.sleep(5)

    print("sleeper done")


async def ticker():
    for i in range(10):
        print("tick", i)
        await asyncio.sleep(0.5)
```

Chạy:

```python
await asyncio.gather(
    sleeper(),
    ticker(),
)
```

Bạn phải giải thích được:

> Tại sao `ticker()` vẫn chạy trong khi `sleeper()` đang "sleep"?

---

# 30. Bài tập 3 — Chứng minh blocking

Đổi:

```python
await asyncio.sleep(5)
```

thành:

```python
import time

time.sleep(5)
```

Chạy lại.

Giải thích:

```text
Tại sao ticker bị dừng?
```

Nếu bạn trả lời:

> "`time.sleep()` block thread chứa Event Loop, nên Event Loop không thể chạy ticker."

thì bạn đã hiểu đúng.

---

# 31. Bài tập 4 — `sleep(0)`

Viết:

```python
async def worker(name):
    for i in range(10):
        print(name, i)

        if i % 2 == 0:
            await asyncio.sleep(0)
```

Quan sát scheduling.

Sau đó bỏ:

```python
await asyncio.sleep(0)
```

So sánh.

---

# 32. Bài tập 5 — Polling

Viết một hàm:

```python
async def wait_until_done():
    ...
```

Giả lập:

```python
async def check_status():
    ...
```

Yêu cầu:

```text
check status
 ↓
nếu chưa done
 ↓
await asyncio.sleep(1)
 ↓
check lại
```

Không được sử dụng:

```python
time.sleep()
```

---

# 33. Bài tập 6 — Retry + Backoff

Viết:

```python
async def fetch_with_retry():
    ...
```

Yêu cầu:

```text
attempt 1
   ↓
fail
   ↓
sleep 1s

attempt 2
   ↓
fail
   ↓
sleep 2s

attempt 3
   ↓
fail
   ↓
sleep 4s

attempt 4
   ↓
success
```

Sau này pattern này sẽ được dùng rất nhiều trong crawler của bạn.

---

# 34. Bài tập Deep Dive — Scheduler Visualization

Viết:

```python
async def worker(name):
    for i in range(5):
        print(
            f"{name}: step {i}"
        )

        await asyncio.sleep(0)
```

Tạo:

```text
A
B
C
D
```

Sau đó tự vẽ timeline:

```text
Time →
──────────────────────────────>

A   █   █   █   █   █
B     █   █   █   █   █
C       █   █   █   █   █
D         █   █   █   █   █
```

Mục tiêu của bài này không phải code mà là **xây mental model về cooperative scheduling**.

---

# 35. Mental Model cuối buổi

Bạn cần nhớ chính xác chuỗi:

```text
asyncio.sleep(2)
       │
       ▼
 tạo/đăng ký timer
       │
       ▼
 coroutine suspend
       │
       ▼
 Event Loop tiếp tục xử lý
       │
       ├── Task B
       ├── Task C
       ├── I/O
       └── Task D
       │
       ▼
 timer hết hạn
       │
       ▼
 Task trở thành ready
       │
       ▼
 Event Loop chạy Task
       │
       ▼
 coroutine resume
```

Và:

```text
time.sleep()
     ↓
BLOCK THREAD
     ↓
BLOCK EVENT LOOP
```

trong khi:

```text
await asyncio.sleep()
     ↓
SUSPEND COROUTINE
     ↓
YIELD CONTROL
     ↓
EVENT LOOP CONTINUE
```

---

# 36. Ba câu phải thuộc lòng

### Câu 1

> `asyncio.sleep()` **không block Event Loop**; nó suspend coroutine hiện tại và cho Event Loop cơ hội chạy công việc khác.

### Câu 2

> Asyncio sử dụng **cooperative scheduling**: coroutine cần gặp các điểm `await` để nhường quyền.

### Câu 3

> `async def` không biến code bên trong thành non-blocking. Một hàm `async` vẫn có thể block Event Loop nếu chứa blocking/CPU-bound code.

---

## Vị trí của chúng ta

```text
Phần II — Async Control Flow

6. await Deep Dive                    ✅
7. Sleep & Cooperative Scheduling    ← HÔM NAY
8. Timeout
   ├── asyncio.timeout()
   └── asyncio.wait_for()
9. Cancellation
   ├── Task.cancel()
   ├── CancelledError
   ├── propagation
   └── cleanup
10. Exception
   ├── coroutine
   ├── Task
   ├── gather()
   ├── return_exceptions
   └── propagation
```

**Buổi 8** chúng ta sẽ đi sâu vào **Timeout trong asyncio**, đặc biệt là sự khác nhau về semantics giữa `asyncio.timeout()` và `asyncio.wait_for()` — đây là phần rất quan trọng khi xây crawler và worker vì timeout thực tế không chỉ đơn giản là "đợi quá lâu thì lỗi".
