# Python Asynchronous Programming - Buổi 8

# Coroutine Deep Dive - Coroutine Chain, Call Stack và `await` nhiều tầng

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ hiểu:
>
> * Coroutine gọi coroutine khác như thế nào.
> * `await` hoạt động qua nhiều tầng lời gọi (call chain).
> * Giá trị trả về của coroutine.
> * Coroutine Stack là gì.
> * Event Loop resume đúng vị trí như thế nào.
> * Vì sao coroutine rất giống function nhưng vẫn khác hoàn toàn.

> **Buổi học này cực kỳ quan trọng**, vì sau khi hiểu coroutine chain, bạn sẽ rất dễ học `Task`, `gather()`, `TaskGroup` và các framework như FastAPI hay aiohttp.

---

# 1. Hàm gọi hàm

Trước tiên hãy xem hàm thông thường.

```python
def c():
    print("C")

def b():
    print("B")
    c()

def a():
    print("A")
    b()

a()
```

Kết quả:

```
A
B
C
```

Call Stack:

```text
a()

↓

b()

↓

c()

↓

return

↓

b()

↓

return

↓

a()

↓

return
```

Đây là cách Python hoạt động từ trước đến nay.

---

# 2. Coroutine cũng giống như vậy

```python
import asyncio

async def c():
    print("C")

async def b():
    print("B")
    await c()

async def a():
    print("A")
    await b()

asyncio.run(a())
```

Kết quả:

```
A
B
C
```

Thoạt nhìn giống hệt.

Nhưng bên trong khác rất nhiều.

---

# 3. Điều gì xảy ra?

Timeline:

```text
Event Loop

↓

a()

↓

await b()

↓

b()

↓

await c()

↓

c()

↓

return

↓

b()

↓

return

↓

a()

↓

finish
```

Điều cần nhớ:

`await`

không phải:

```
Thread mới
```

cũng không phải:

```
Process mới
```

Mà là:

```
Coroutine mới
```

---

# 4. Giá trị trả về của Coroutine

Ví dụ:

```python
import asyncio

async def add():
    return 10

async def main():
    value = await add()
    print(value)

asyncio.run(main())
```

Kết quả:

```
10
```

Điều này rất quan trọng.

Coroutine hoàn toàn có thể:

* nhận tham số
* trả về giá trị

giống Function.

---

# 5. Coroutine trả về Object gì?

Ví dụ:

```python
async def hello():
    return "Hello"

coro = hello()

print(coro)
```

Kết quả:

```
<coroutine object hello at ...>
```

Sau khi:

```python
await coro
```

thì:

```
Hello
```

mới được trả về.

---

# 6. Chuỗi Coroutine

Ví dụ:

```python
import asyncio

async def get_name():
    return "Alice"

async def greeting():
    name = await get_name()
    return f"Hello {name}"

async def main():
    text = await greeting()
    print(text)

asyncio.run(main())
```

Kết quả:

```
Hello Alice
```

Luồng chạy:

```text
main()

↓

await greeting()

↓

await get_name()

↓

return "Alice"

↓

greeting()

↓

return "Hello Alice"

↓

main()
```

---

# 7. Coroutine Stack

Bạn đã biết Call Stack.

Async có khái niệm:

```
Coroutine Stack
```

Ví dụ:

```python
main()

↓

download()

↓

save()

↓

write_file()
```

Nếu:

```python
await write_file()
```

Coroutine Stack:

```text
main

↓

download

↓

save

↓

write_file
```

Được lưu lại.

---

# 8. Suspend toàn bộ Stack

Ví dụ:

```python
import asyncio

async def c():
    await asyncio.sleep(2)

async def b():
    await c()

async def a():
    await b()

asyncio.run(a())
```

Khi:

```python
await asyncio.sleep(2)
```

Điều xảy ra:

```
c

Pause
```

↓

```
b

Pause
```

↓

```
a

Pause
```

Toàn bộ chuỗi coroutine bị tạm dừng.

---

# 9. Resume

Sau 2 giây:

Python không chạy lại từ đầu.

Mà:

```text
Resume c()

↓

return

↓

Resume b()

↓

return

↓

Resume a()

↓

Finish
```

Đây là một trong những điểm mạnh nhất của Coroutine.

---

# 10. Ví dụ thực tế

Ứng dụng web.

```text
HTTP Request

↓

Controller

↓

Service

↓

Repository

↓

Database
```

Code:

```python
async def repository():
    ...

async def service():
    await repository()

async def controller():
    await service()

async def main():
    await controller()
```

Bạn sẽ thấy cấu trúc này ở:

* FastAPI
* aiohttp
* Quart
* Sanic

---

# 11. await nhiều tầng

Ví dụ:

```python
import asyncio

async def level3():
    print("Level 3")

async def level2():
    print("Level 2 Start")
    await level3()
    print("Level 2 End")

async def level1():
    print("Level 1 Start")
    await level2()
    print("Level 1 End")

asyncio.run(level1())
```

Kết quả:

```
Level 1 Start
Level 2 Start
Level 3
Level 2 End
Level 1 End
```

Giống Function.

Khác ở chỗ:

Mỗi tầng đều có thể bị Suspend.

---

# 12. await có thể lồng vô hạn

Ví dụ:

```
A

↓

B

↓

C

↓

D

↓

E

↓

F

↓

Database
```

Nếu Database chờ:

```
await
```

Toàn bộ Stack:

```
Pause
```

Sau đó:

```
Resume F

↓

Resume E

↓

Resume D

↓

Resume C

↓

Resume B

↓

Resume A
```

---

# 13. Coroutine không bị mất dữ liệu

Ví dụ:

```python
import asyncio

async def test():
    x = 100

    await asyncio.sleep(2)

    print(x)

asyncio.run(test())
```

Kết quả:

```
100
```

Vì:

Coroutine lưu:

* biến cục bộ
* vị trí hiện tại
* stack logic

để tiếp tục sau khi Resume.

---

# 14. Sai lầm phổ biến

## Sai lầm 1

Nghĩ rằng:

```
await

↓

Restart Function
```

Sai.

Coroutine tiếp tục từ:

```
đúng dòng await
```

---

## Sai lầm 2

Nghĩ rằng:

```
await

↓

Mất biến
```

Sai.

Biến vẫn được giữ nguyên.

---

## Sai lầm 3

Nghĩ rằng:

Coroutine không trả về giá trị.

Sai.

Coroutine hoàn toàn có thể:

```python
return value
```

và nhận lại bằng:

```python
value = await coroutine()
```

---

# 15. Mô hình tổng quát

```text
main()

↓

controller()

↓

service()

↓

repository()

↓

database()

↓

await

↓

Pause

↓

Event Loop

↓

Resume database

↓

Resume repository

↓

Resume service

↓

Resume controller

↓

Resume main
```

---

# 16. Tổng kết

Coroutine:

✔ Có tham số

✔ Có return

✔ Có local variable

✔ Có stack

✔ Có call chain

✔ Có thể Suspend

✔ Có thể Resume

Đó là lý do Async trông rất giống lập trình tuần tự.

Đây chính là ưu điểm lớn nhất của `async`/`await`.

---

# Sơ đồ tư duy

```text
          Coroutine

              │

      await Coroutine

              │

      Coroutine Stack

              │

           Suspend

              │

         Event Loop

              │

           Resume

              │

         Return Value

              │

         Caller nhận kết quả
```

---

# Bài tập thực hành

## Bài 1

Viết ba coroutine:

```python
async def get_age():
    return 25

async def get_name():
    return "Alice"

async def get_user():
    ...
```

Yêu cầu:

`get_user()` gọi hai coroutine còn lại và trả về:

```
Alice (25)
```

---

## Bài 2

Viết chuỗi lời gọi:

```
main()

↓

A()

↓

B()

↓

C()
```

Trong đó:

`C()` chờ:

```python
await asyncio.sleep(2)
```

Hãy mô tả:

* coroutine nào bị Suspend
* coroutine nào được Resume trước

---

## Bài 3

Giải thích:

Tại sao:

```python
x = await get_data()
```

trông giống:

```python
x = get_data()
```

nhưng bên trong hoàn toàn khác?

---

## Bài 4 (Nâng cao)

Vẽ sơ đồ Call Stack và Coroutine Stack cho chương trình có 4 tầng lời gọi (`main → service → repository → database`) và chỉ rõ thời điểm toàn bộ chuỗi bị tạm dừng khi `database()` thực hiện một thao tác I/O.

---

# Chuẩn bị cho Buổi 9

Từ buổi sau, chúng ta sẽ bước vào phần được sử dụng nhiều nhất trong lập trình `asyncio` thực tế:

# **Task - Đơn vị thực thi của Event Loop**

Bạn sẽ học:

* Task là gì.
* Task khác Coroutine như thế nào.
* `asyncio.create_task()`.
* Vì sao chỉ `await` thôi chưa tạo ra sự chạy đồng thời.
* Khi nào nên dùng `Task` và khi nào chỉ cần `await`.

Đây là bước chuyển từ **hiểu cơ chế** sang **xây dựng các chương trình bất đồng bộ thực sự**, nơi nhiều coroutine có thể được lập lịch và tiến triển đồng thời trên cùng một Event Loop.
