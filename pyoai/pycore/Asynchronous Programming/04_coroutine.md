# Python Asynchronous Programming - Buổi 4

# Coroutine - Trái tim của Asyncio

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ hiểu:
>
> * Coroutine là gì.
> * `async def` thực chất tạo ra cái gì.
> * Tại sao gọi hàm `async` lại không chạy.
> * Coroutine khác Function như thế nào.
> * Vòng đời của một Coroutine.
> * Kiến thức nền tảng để học `await` ở buổi sau.

---

# 1. Hàm thông thường (Function)

Chúng ta bắt đầu với một hàm quen thuộc:

```python
def hello():
    print("Hello")

hello()
```

Kết quả:

```text
Hello
```

Quá trình diễn ra:

```text
Gọi hello()

↓

Python tạo Stack Frame

↓

Thực thi toàn bộ hàm

↓

Trả về

↓

Hàm kết thúc
```

Điểm quan trọng:

> Khi gọi một hàm thông thường, **hàm sẽ chạy ngay lập tức**.

---

# 2. Hàm async

Bây giờ thử:

```python
async def hello():
    print("Hello")

hello()
```

Bạn nghĩ sẽ in:

```text
Hello
```

Không.

Kết quả thực tế:

```text
RuntimeWarning:
coroutine 'hello' was never awaited
```

Hoặc thậm chí không có gì được in (tùy môi trường chạy), nhưng Python sẽ cảnh báo rằng coroutine chưa được chờ (`await`).

Đây là điều khiến gần như mọi người mới học Async đều ngạc nhiên.

---

# 3. Tại sao không chạy?

Bởi vì:

```python
async def hello():
    print("Hello")
```

không tạo ra một hàm bình thường.

Nó tạo ra:

> **Coroutine Function**

Khi gọi:

```python
hello()
```

Python **không chạy**.

Python chỉ tạo ra một **Coroutine Object**.

---

# 4. Kiểm tra kiểu dữ liệu

```python
async def hello():
    print("Hello")

coro = hello()

print(type(coro))
```

Kết quả:

```text
<class 'coroutine'>
```

Không phải:

```text
<class 'function'>
```

Không phải:

```text
None
```

Mà là:

```text
Coroutine Object
```

---

# 5. Coroutine Object là gì?

Hãy tưởng tượng:

Hàm bình thường giống như:

```text
Nút PLAY

↓

Bấm

↓

Phim chạy ngay
```

Coroutine giống như:

```text
Đĩa DVD

↓

Đã có phim

↓

Chưa phát

↓

Đợi đầu DVD chạy
```

Coroutine chỉ là:

> Một công việc đã được mô tả, **chưa được thực hiện**.

---

# 6. Ví dụ trực quan

```python
async def cook():
    print("Nấu cơm")

task = cook()

print(task)
```

Kết quả:

```text
<coroutine object cook at 0x...>
```

Không có dòng:

```text
Nấu cơm
```

---

# 7. Khi nào Coroutine chạy?

Coroutine chỉ chạy khi được:

* `await`
* `asyncio.run()`
* `create_task()`
* `TaskGroup`
* Event Loop điều khiển

Ví dụ:

```python
import asyncio

async def hello():
    print("Hello")

asyncio.run(hello())
```

Kết quả:

```text
Hello
```

---

# 8. So sánh Function và Coroutine

## Function

```python
def add():
    print("Running")
```

Gọi:

```python
add()
```

Timeline:

```text
Call

↓

Run

↓

Finish
```

---

## Coroutine

```python
async def add():
    print("Running")
```

Gọi:

```python
add()
```

Timeline:

```text
Call

↓

Create Coroutine

↓

Return Coroutine Object

↓

(Không chạy)
```

---

# 9. Coroutine giống "công việc"

Ví dụ:

Bạn viết giấy nhắc việc:

```text
□ Mua sữa

□ Đi ngân hàng

□ Mua sách
```

Danh sách này chưa làm gì cả.

Chỉ khi bạn bắt đầu thực hiện:

```text
Đi mua sữa
```

thì công việc mới chạy.

Coroutine cũng vậy.

---

# 10. Coroutine có trạng thái

Một Coroutine thường trải qua các trạng thái:

```text
Created

↓

Running

↓

Suspended

↓

Running

↓

Finished
```

Giải thích:

### Created

```python
coro = hello()
```

Đã tạo.

Chưa chạy.

---

### Running

Event Loop bắt đầu chạy.

---

### Suspended

Gặp:

```python
await something()
```

Coroutine tạm dừng.

Nhường quyền.

---

### Running

Event Loop quay lại.

---

### Finished

Kết thúc.

---

# 11. Coroutine khác Generator không?

Nếu đã học `yield`, bạn sẽ thấy rất giống.

Generator:

```python
def gen():
    yield 1
```

Coroutine:

```python
async def work():
    await something()
```

Thực tế:

Coroutine hiện đại trong Python được xây dựng dựa trên ý tưởng của Generator.

Chúng đều có khả năng:

* tạm dừng
* tiếp tục

Khác nhau ở mục đích sử dụng.

| Generator    | Coroutine                       |
| ------------ | ------------------------------- |
| Sinh dữ liệu | Thực hiện công việc bất đồng bộ |
| `yield`      | `await`                         |
| Lặp dữ liệu  | Chờ I/O                         |

---

# 12. Bên trong Python

Khi viết:

```python
async def download():
    ...
```

Python tạo:

```text
Coroutine Function
```

Khi gọi:

```python
download()
```

Python tạo:

```text
Coroutine Object
```

Sau đó:

```text
Coroutine Object

↓

Event Loop

↓

Run
```

---

# 13. Một ví dụ trực quan

```python
import asyncio

async def hello():
    print("A")
    print("B")

print("1")

coro = hello()

print("2")

asyncio.run(coro)

print("3")
```

Kết quả:

```text
1
2
A
B
3
```

Giải thích:

```text
1

↓

Tạo Coroutine

↓

2

↓

Event Loop chạy

↓

A

↓

B

↓

3
```

Lưu ý: `hello()` chỉ tạo coroutine, còn `asyncio.run(coro)` mới thực sự thực thi.

---

# 14. Sai lầm phổ biến

## Sai lầm 1

```python
async def work():
    ...

work()
```

Nghĩ rằng:

```text
Đã chạy
```

Sai.

Chỉ tạo Coroutine.

---

## Sai lầm 2

```python
async def work():
    ...

a = work()
b = work()
```

Nghĩ rằng:

Hai công việc đang chạy.

Sai.

Chúng chỉ mới được tạo.

---

## Sai lầm 3

```python
async def work():
    ...

print(work())
```

Kết quả:

```text
<coroutine object ...>
```

Không phải kết quả của hàm.

---

# 15. Vòng đời Coroutine

```text
async def

↓

Coroutine Function

↓

Call

↓

Coroutine Object

↓

Event Loop

↓

Running

↓

await

↓

Pause

↓

Resume

↓

Finish
```

Đây là sơ đồ bạn nên ghi nhớ.

---

# 16. Tổng kết

## Điều quan trọng nhất của buổi học

### Hàm thường

```python
func()
```

↓

Chạy ngay.

---

### Coroutine

```python
async_func()
```

↓

Không chạy.

↓

Chỉ tạo Coroutine Object.

---

### Muốn chạy

Phải có:

```python
asyncio.run(...)
```

hoặc

```python
await ...
```

hoặc Event Loop quản lý thông qua `Task`.

---

# Sơ đồ tư duy

```text
                  async def
                      │
                      ▼
            Coroutine Function
                      │
             Gọi hello()
                      │
                      ▼
            Coroutine Object
                      │
          (Chưa chạy gì cả)
                      │
                      ▼
               Event Loop
                      │
                      ▼
                 Running
                      │
                await ...
                      │
                      ▼
                 Suspended
                      │
                      ▼
                  Running
                      │
                      ▼
                  Finished
```

---

# Bài tập thực hành

## Bài 1

Viết chương trình:

```python
async def hello():
    print("Hello")

coro = hello()

print(type(coro))
print(coro)
```

Quan sát kiểu dữ liệu được in ra.

---

## Bài 2

Thử chạy:

```python
async def test():
    print("Python Async")

test()
```

Quan sát cảnh báo và giải thích vì sao không có dòng `"Python Async"` được in ra.

---

## Bài 3

Sửa lại bằng:

```python
import asyncio

async def test():
    print("Python Async")

asyncio.run(test())
```

Giải thích vai trò của `asyncio.run()`.

---

## Bài 4 (Nâng cao)

Viết chương trình:

```python
import asyncio

async def hello():
    print("Hello")

async def world():
    print("World")

c1 = hello()
c2 = world()

print(type(c1))
print(type(c2))
```

Tự trả lời:

* Đã có coroutine chưa?
* Đã có Event Loop chạy chưa?
* `"Hello"` và `"World"` đã được in ra chưa?
* Vì sao Python có thể cảnh báo "coroutine was never awaited"?

---

# Chuẩn bị cho Buổi 5

Ở buổi tiếp theo, chúng ta sẽ học về **`await`** – từ khóa quan trọng nhất trong `asyncio`. Bạn sẽ hiểu:

* `await` thực sự làm gì.
* Vì sao `await` có thể "tạm dừng" một coroutine mà không chặn cả chương trình.
* Event Loop chuyển quyền điều khiển giữa các coroutine như thế nào.
* Vì sao `await` không giống `time.sleep()`.

Đây là bước nền tảng để hiểu cơ chế hoạt động của `asyncio` ở mức sâu.
