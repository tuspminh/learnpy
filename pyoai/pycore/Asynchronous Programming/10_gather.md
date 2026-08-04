# Python Asynchronous Programming - Buổi 10

# `asyncio.gather()` - Chạy nhiều Coroutine đồng thời

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ hiểu:
>
> * `asyncio.gather()` là gì.
> * `gather()` hoạt động bên trong như thế nào.
> * Khác gì với `await`.
> * Khác gì với `create_task()`.
> * Thu thập kết quả từ nhiều coroutine.
> * Xử lý exception với `gather()`.
> * Khi nào nên và không nên dùng `gather()`.

---

# 1. Bài toán thực tế

Giả sử cần tải dữ liệu từ 3 API:

```text
API User

API Product

API Order
```

Nếu viết:

```python
user = await get_user()
product = await get_product()
order = await get_order()
```

Timeline:

```text
User

↓

2s

↓

Product

↓

2s

↓

Order

↓

2s
```

Tổng:

```text
6 giây
```

Đây là cách làm **tuần tự**.

---

# 2. Ý tưởng của `gather()`

Thay vì:

```text
A

↓

B

↓

C
```

Ta muốn:

```text
A
 \
  \
   > chạy cùng lúc
  /
 /
B

C
```

Đó là mục đích của `asyncio.gather()`.

---

# 3. Ví dụ đầu tiên

```python
import asyncio

async def task1():
    await asyncio.sleep(2)
    print("Task 1")

async def task2():
    await asyncio.sleep(1)
    print("Task 2")

async def main():

    await asyncio.gather(
        task1(),
        task2()
    )

asyncio.run(main())
```

Kết quả:

```text
Task 2

Task 1
```

Tổng thời gian:

```text
2 giây
```

---

# 4. Điều gì xảy ra?

Bên trong:

```python
await asyncio.gather(
    task1(),
    task2()
)
```

Có thể hình dung:

```text
task1()

↓

Task

↓

Ready Queue

task2()

↓

Task

↓

Ready Queue

↓

Event Loop

↓

Đợi tất cả hoàn thành
```

`gather()` sẽ lập lịch để các coroutine cùng tiến triển, sau đó đợi tất cả hoàn tất.

---

# 5. `gather()` có tự tạo Task không?

Đây là câu hỏi rất hay.

Ví dụ:

```python
await asyncio.gather(
    download(),
    upload()
)
```

Bạn truyền vào **coroutine**.

`gather()` sẽ tự chuyển chúng thành các Task nội bộ (nếu cần) để Event Loop có thể quản lý.

Bạn không cần gọi:

```python
asyncio.create_task()
```

trong trường hợp đơn giản này.

---

# 6. Thu thập kết quả

Ví dụ:

```python
import asyncio

async def square(x):
    await asyncio.sleep(1)
    return x * x

async def main():

    result = await asyncio.gather(
        square(2),
        square(3),
        square(4)
    )

    print(result)

asyncio.run(main())
```

Kết quả:

```text
[4, 9, 16]
```

---

# 7. Thứ tự kết quả

Giả sử:

```python
square(5)

square(2)

square(10)
```

Dù:

* `square(2)` xong trước
* `square(5)` xong sau

`gather()` vẫn trả:

```text
[
    kết quả square(5),
    kết quả square(2),
    kết quả square(10)
]
```

Theo **thứ tự truyền vào**, không phải thứ tự hoàn thành.

---

# 8. Ví dụ

```python
import asyncio

async def work(name, sec):

    await asyncio.sleep(sec)

    return name

async def main():

    result = await asyncio.gather(

        work("A", 3),

        work("B", 1),

        work("C", 2)

    )

    print(result)

asyncio.run(main())
```

Kết quả:

```text
['A', 'B', 'C']
```

Mặc dù:

```text
B

↓

C

↓

A
```

hoàn thành theo thứ tự đó.

---

# 9. `gather()` và `create_task()`

Đây là điều rất nhiều người nhầm.

## Cách 1

```python
await asyncio.gather(

    download(),

    upload()
)
```

Đơn giản.

---

## Cách 2

```python
t1 = asyncio.create_task(download())

t2 = asyncio.create_task(upload())

await asyncio.gather(t1, t2)
```

Cũng đúng.

Khi nào dùng?

Nếu bạn cần giữ tham chiếu đến Task để:

* hủy (`cancel`)
* kiểm tra trạng thái (`done`)
* đặt tên
* quản lý riêng

thì nên tạo Task trước.

---

# 10. Exception

Giả sử:

```python
async def work():

    raise ValueError("Error")
```

```python
await asyncio.gather(

    task1(),

    work(),

    task3()
)
```

Mặc định:

* `gather()` sẽ phát sinh exception đầu tiên gặp phải.
* Các coroutine khác có thể bị hủy hoặc dừng theo cách phù hợp với quá trình xử lý của Event Loop.

Ví dụ:

```python
try:

    await asyncio.gather(...)

except Exception as e:

    print(e)
```

---

# 11. `return_exceptions=True`

Có lúc bạn muốn:

"Dù một coroutine lỗi thì vẫn lấy kết quả của các coroutine khác."

Ví dụ:

```python
result = await asyncio.gather(

    task1(),

    task2(),

    task3(),

    return_exceptions=True

)
```

Nếu:

Task2 lỗi.

Kết quả:

```text
[
    "OK",

    ValueError(...),

    "DONE"
]
```

Không phát sinh exception ngay.

---

# 12. Timeline của `gather()`

```text
Task1

↓

Sleep 3

Task2

↓

Sleep 1

Task3

↓

Sleep 2

↓

1s

Task2 Finish

↓

2s

Task3 Finish

↓

3s

Task1 Finish

↓

Gather Return
```

---

# 13. `gather()` không phải Thread

Nhiều người nghĩ:

```text
gather

↓

Thread
```

Sai.

Thực tế:

```text
gather

↓

Task

↓

Event Loop

↓

Coroutine
```

Vẫn chỉ một Event Loop (mặc định) và thường một Thread.

---

# 14. `gather()` có giới hạn không?

Bạn có thể:

```python
await asyncio.gather(

    *tasks
)
```

Trong đó:

```python
tasks = [

    work(i)

    for i in range(1000)

]
```

Hoàn toàn hợp lệ.

Thậm chí:

```text
10.000 Coroutine
```

cũng có thể chạy nếu công việc chủ yếu là I/O.

Lưu ý: số lượng tối ưu còn phụ thuộc vào bộ nhớ, tài nguyên hệ thống và dịch vụ bên ngoài (API, database...).

---

# 15. Ví dụ thực tế

Crawler:

```python
urls = [

    "...",

    "...",

    "..."

]
```

```python
tasks = [

    fetch(url)

    for url in urls

]

await asyncio.gather(*tasks)
```

Hoặc:

Đọc:

* 500 file

Gửi:

* 500 request

Đều là ứng dụng điển hình.

---

# 16. Khi nào dùng `gather()`?

Rất phù hợp khi:

* Gọi nhiều API độc lập.
* Download nhiều file.
* Upload nhiều file.
* Crawler.
* Web Scraping.
* Đồng bộ dữ liệu.
* Xử lý nhiều thao tác I/O không phụ thuộc lẫn nhau.

---

# 17. Khi nào không dùng?

Nếu:

Task B phụ thuộc:

```text
Task A
```

Ví dụ:

```python
user = await get_user()

order = await get_order(user.id)
```

Không thể:

```python
asyncio.gather()
```

vì:

`order()` cần kết quả từ `user()`.

---

# 18. So sánh

| Cách                   | Chạy đồng thời? | Thu kết quả?                   |
| ---------------------- | --------------- | ------------------------------ |
| `await a(); await b()` | ❌ Không         | Không                          |
| `create_task()`        | ✅ Có            | Có (qua `await task`)          |
| `gather()`             | ✅ Có            | ✅ Có, theo đúng thứ tự đầu vào |

---

# 19. Sai lầm phổ biến

## Sai lầm 1

```python
await asyncio.gather(
    task1,
    task2
)
```

Sai.

Phải gọi:

```python
await asyncio.gather(
    task1(),
    task2()
)
```

hoặc truyền các `Task` đã tạo.

---

## Sai lầm 2

Nghĩ rằng:

```text
gather

↓

Theo thứ tự hoàn thành
```

Sai.

Theo:

```text
Thứ tự truyền vào
```

---

## Sai lầm 3

Dùng `gather()` cho:

```text
Task phụ thuộc nhau
```

Điều này thường không phù hợp vì các tác vụ không thể bắt đầu đồng thời.

---

# 20. Tổng kết

Điều quan trọng nhất:

```text
Coroutine

↓

gather()

↓

Task

↓

Event Loop

↓

Running

↓

Đợi tất cả

↓

List kết quả
```

Hãy ghi nhớ:

> **`asyncio.gather()` là công cụ chuẩn để chạy nhiều coroutine độc lập cùng lúc và thu kết quả của tất cả chúng.**

---

# Sơ đồ tư duy

```text
          gather()

              │

     ┌────────┼────────┐

     ▼        ▼        ▼

 Coroutine Coroutine Coroutine

     │        │        │

     ▼        ▼        ▼

    Task     Task     Task

     └────────┼────────┘

              ▼

         Event Loop

              ▼

       Chạy đồng thời

              ▼

      Thu kết quả (List)
```

---

# Bài tập thực hành

## Bài 1

Viết ba coroutine:

```python
async def download(name, sec):
    ...
```

Tạo:

```python
await asyncio.gather(

    download("A", 3),

    download("B", 2),

    download("C", 1)

)
```

Quan sát:

* Thứ tự bắt đầu.
* Thứ tự kết thúc.
* Tổng thời gian.

---

## Bài 2

Viết:

```python
async def cube(x):
    return x ** 3
```

Sử dụng:

```python
asyncio.gather()
```

để tính:

* 2³
* 3³
* 4³
* 5³

và in danh sách kết quả.

---

## Bài 3

Viết một coroutine luôn phát sinh lỗi:

```python
raise RuntimeError("Oops")
```

Kết hợp với hai coroutine thành công.

Thử:

1. `asyncio.gather(...)`
2. `asyncio.gather(..., return_exceptions=True)`

Quan sát và giải thích sự khác biệt.

---

## Bài 4 (Nâng cao)

Giả sử bạn cần:

* Gọi API lấy thông tin người dùng.
* Gọi API lấy sản phẩm.
* Gọi API lấy đánh giá.

Ba API hoàn toàn độc lập.

Hãy giải thích vì sao `asyncio.gather()` là lựa chọn phù hợp hơn so với:

```python
await get_user()
await get_product()
await get_review()
```

---

# Chuẩn bị cho Buổi 11

Buổi tiếp theo sẽ đi sâu vào một chủ đề rất quan trọng trong các ứng dụng thực tế:

# **Task Lifecycle & Task Management**

Bạn sẽ học:

* Trạng thái đầy đủ của `asyncio.Task`.
* Các phương thức như `done()`, `cancel()`, `cancelled()`, `result()`, `exception()`.
* Hủy Task đúng cách.
* Điều gì xảy ra khi hủy một coroutine đang chạy.
* Các lỗi thường gặp khi quản lý vòng đời Task.

Đây là nền tảng để xây dựng các ứng dụng lớn như **FastAPI**, **Discord Bot**, **Telegram Bot**, **WebSocket Server**, **Crawler** và các dịch vụ nền (background services) hoạt động ổn định và có khả năng xử lý lỗi tốt.
