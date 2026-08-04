# Python Asynchronous Programming - Buổi 13

# Timeout, Deadline & Cancellation nâng cao

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ hiểu:
>
> * Timeout là gì.
> * Deadline khác Timeout như thế nào.
> * `asyncio.wait_for()`.
> * `asyncio.timeout()` (Python 3.11+).
> * `asyncio.shield()`.
> * `TimeoutError` và `CancelledError` khác nhau như thế nào.
> * Thiết kế coroutine có khả năng timeout an toàn.

> ⭐ Đây là kiến thức được sử dụng rất nhiều trong **FastAPI**, **aiohttp**, **asyncpg**, **aiomysql**, **Redis**, **Crawler**, **Telegram Bot**, **Discord Bot**...

---

# 1. Vì sao cần Timeout?

Giả sử bạn gọi một API:

```python
result = await fetch_data()
```

Thông thường:

```text
Request

↓

Server

↓

Response
```

Nhưng nếu server:

* bị treo
* mạng chậm
* DNS lỗi
* firewall chặn

thì:

```text
Request

↓

...

↓

...

↓

Không bao giờ trả lời
```

Nếu không có timeout:

```text
Coroutine

↓

Chờ mãi mãi
```

Đây là điều rất nguy hiểm.

---

# 2. Timeout là gì?

Timeout nghĩa là:

> **Nếu một thao tác không hoàn thành trong khoảng thời gian cho phép thì hủy nó.**

Ví dụ:

```text
Download

↓

5 giây

↓

Timeout = 3 giây

↓

Cancel
```

---

# 3. `asyncio.wait_for()`

Đây là API truyền thống.

Ví dụ:

```python
import asyncio

async def work():
    await asyncio.sleep(5)

async def main():
    try:
        await asyncio.wait_for(
            work(),
            timeout=2
        )
    except TimeoutError:
        print("Timeout!")

asyncio.run(main())
```

Kết quả:

```text
Timeout!
```

---

# 4. Điều gì xảy ra bên trong?

Timeline:

```text
work()

↓

sleep(5)

↓

2 giây

↓

wait_for()

↓

cancel()

↓

CancelledError

↓

TimeoutError
```

Lưu ý:

* **Bên trong coroutine**, `work()` nhận `CancelledError`.
* **Bên ngoài**, `wait_for()` chuyển thành `TimeoutError`.

Đây là điểm rất nhiều người nhầm.

---

# 5. Coroutine nhận `CancelledError`

```python
import asyncio

async def work():
    try:
        print("Start")
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("Cleaning...")
        raise

async def main():
    try:
        await asyncio.wait_for(work(), timeout=2)
    except TimeoutError:
        print("Timeout")

asyncio.run(main())
```

Kết quả:

```text
Start
Cleaning...
Timeout
```

Giải thích:

* `wait_for()` hủy coroutine.
* Coroutine có cơ hội cleanup.
* Sau đó `wait_for()` báo `TimeoutError` cho bên gọi.

---

# 6. `asyncio.timeout()` (Python 3.11+)

Từ Python 3.11 có cú pháp mới:

```python
import asyncio

async def work():
    await asyncio.sleep(5)

async def main():
    try:
        async with asyncio.timeout(2):
            await work()
    except TimeoutError:
        print("Timeout")

asyncio.run(main())
```

Đây là cách được **khuyến nghị** trên Python hiện đại.

---

# 7. So sánh `wait_for()` và `timeout()`

### `wait_for()`

```python
await asyncio.wait_for(
    coro(),
    timeout=5
)
```

Timeout áp dụng cho **một coroutine cụ thể**.

---

### `timeout()`

```python
async with asyncio.timeout(5):
    await task1()
    await task2()
```

Timeout áp dụng cho **toàn bộ khối lệnh**.

---

# 8. Deadline

Timeout:

```text
Task

↓

Có 5 giây riêng
```

Deadline:

```text
Bắt đầu lúc 10:00

↓

10:00:05

↓

Hết hạn
```

Dù task đang ở đâu cũng phải dừng.

`asyncio.timeout()` rất phù hợp để biểu diễn deadline cho một nhóm thao tác.

---

# 9. Timeout lồng nhau

Ví dụ:

```python
async with asyncio.timeout(10):

    await step1()

    async with asyncio.timeout(2):

        await step2()
```

Ý nghĩa:

```text
Toàn bộ

10 giây

↓

Riêng step2

2 giây
```

Rất hữu ích trong các workflow nhiều bước.

---

# 10. `asyncio.shield()`

Có lúc bạn **không muốn** coroutine bị hủy.

Ví dụ:

```python
await asyncio.shield(save_database())
```

Ý nghĩa:

> Bảo vệ coroutine khỏi việc bị hủy từ bên ngoài.

Ví dụ:

```python
import asyncio

async def save():
    print("Saving...")
    await asyncio.sleep(3)
    print("Saved")

async def main():
    task = asyncio.create_task(save())

    try:
        await asyncio.wait_for(
            asyncio.shield(task),
            timeout=1
        )
    except TimeoutError:
        print("Timeout")

    await task

asyncio.run(main())
```

Kết quả:

```text
Saving...
Timeout
Saved
```

Giải thích:

* `wait_for()` hết thời gian.
* Nhưng `shield()` ngăn Task bị hủy.
* Task vẫn tiếp tục chạy đến khi hoàn thành.

---

# 11. Khi nào dùng `shield()`?

Ví dụ:

* Ghi log.
* Ghi file.
* Commit database.
* Gửi email xác nhận.
* Lưu dữ liệu quan trọng.

Không nên hủy giữa chừng vì có thể làm dữ liệu không nhất quán.

---

# 12. Timeout và TaskGroup

```python
async with asyncio.timeout(5):

    async with asyncio.TaskGroup() as tg:

        tg.create_task(download())

        tg.create_task(upload())
```

Nếu quá 5 giây:

```text
Timeout

↓

TaskGroup

↓

Cancel toàn bộ Task

↓

Cleanup

↓

Exit
```

Đây là mẫu thiết kế rất phổ biến.

---

# 13. Timeout và `gather()`

```python
await asyncio.wait_for(
    asyncio.gather(
        task1(),
        task2()
    ),
    timeout=5
)
```

Nếu hết thời gian:

* `gather()` bị hủy.
* Các Task bên trong cũng bị hủy (trừ khi bạn có cơ chế bảo vệ riêng như `shield()`).

---

# 14. Sai lầm phổ biến

## Sai lầm 1

Nghĩ rằng:

```text
TimeoutError

=

CancelledError
```

Sai.

* `CancelledError`: coroutine bị yêu cầu hủy.
* `TimeoutError`: bên gọi biết rằng thời gian chờ đã hết.

---

## Sai lầm 2

Không cleanup.

```python
except CancelledError:
    pass
```

Nếu Task đang giữ:

* File
* Database Connection
* Socket

→ dễ gây rò rỉ tài nguyên.

Nên:

```python
except asyncio.CancelledError:
    # cleanup
    raise
```

---

## Sai lầm 3

Lạm dụng `shield()`.

Nếu bọc mọi coroutine bằng `shield()`:

```text
Không thể hủy

↓

Ứng dụng khó dừng

↓

Tốn tài nguyên
```

Chỉ dùng khi thật sự cần bảo vệ một thao tác quan trọng.

---

# 15. Ví dụ thực tế

Một API xử lý đơn hàng:

```text
Nhận Request

↓

Timeout 10 giây

↓

TaskGroup

├── Kiểm tra tồn kho

├── Tính phí ship

└── Tính khuyến mãi

↓

Commit Database (shield)

↓

Response
```

Nếu:

* tính phí ship bị treo
* quá 10 giây

→ toàn bộ request bị hủy.

Nhưng nếu đã bắt đầu **commit database**, có thể dùng `shield()` để hoàn tất việc ghi dữ liệu.

---

# 16. Tổng kết

| API                  | Công dụng                                   |
| -------------------- | ------------------------------------------- |
| `asyncio.wait_for()` | Timeout cho một coroutine                   |
| `asyncio.timeout()`  | Timeout cho cả một khối lệnh (`async with`) |
| `asyncio.shield()`   | Bảo vệ coroutine khỏi bị hủy từ bên ngoài   |
| `CancelledError`     | Coroutine bị yêu cầu hủy                    |
| `TimeoutError`       | Bên gọi biết thời gian chờ đã hết           |

---

# Sơ đồ tư duy

```text
                 Timeout

                    │

        ┌───────────┴───────────┐

        ▼                       ▼

 wait_for()               timeout()

        │                       │

        ▼                       ▼

   Một coroutine          Một block async

                │

                ▼

        Hết thời gian

                │

                ▼

        CancelledError

                │

                ▼

         TimeoutError

                │

        shield() (tùy chọn)

                │

                ▼

     Tiếp tục chạy đến hoàn thành
```

---

# Bài tập thực hành

## Bài 1

Viết coroutine:

```python
async def download():
    await asyncio.sleep(5)
```

Sử dụng:

```python
asyncio.wait_for()
```

để timeout sau **2 giây**.

Quan sát exception.

---

## Bài 2

Viết:

```python
async def process():
```

gồm:

* `step1()` mất 1 giây.
* `step2()` mất 4 giây.

Đặt:

```python
async with asyncio.timeout(3):
```

Quan sát bước nào bị hủy.

---

## Bài 3

Viết coroutine:

```python
async def save_file():
```

* chạy 5 giây.
* bọc bằng `asyncio.shield()`.

Dùng:

```python
wait_for(timeout=2)
```

Quan sát:

* bên ngoài timeout.
* bên trong vẫn ghi file hoàn tất.

---

## Bài 4 (Nâng cao)

Thiết kế một chương trình mô phỏng hệ thống xử lý thanh toán:

* Timeout toàn bộ giao dịch là **8 giây**.
* Ba Task chạy song song trong `TaskGroup`:

  * Kiểm tra số dư.
  * Gửi yêu cầu tới cổng thanh toán.
  * Ghi log giao dịch.
* Sau khi thanh toán thành công, thao tác **ghi hóa đơn vào cơ sở dữ liệu** phải được bảo vệ bằng `asyncio.shield()` để không bị hủy giữa chừng.

Hãy mô tả luồng hoạt động và triển khai chương trình.

---

# Chuẩn bị cho Buổi 14

Buổi tiếp theo chúng ta sẽ học về:

# **Synchronization Primitives trong asyncio**

Đây là nhóm công cụ giúp nhiều coroutine phối hợp với nhau an toàn khi cùng truy cập tài nguyên.

Bạn sẽ học:

* `asyncio.Lock`
* `asyncio.Event`
* `asyncio.Condition`
* `asyncio.Semaphore`
* `asyncio.BoundedSemaphore`
* Race Condition trong môi trường bất đồng bộ.
* Kỹ thuật đồng bộ hóa coroutine.

Đây là nền tảng để xây dựng các hệ thống crawler, connection pool, worker pool, hàng đợi và các dịch vụ bất đồng bộ có độ tin cậy cao.
