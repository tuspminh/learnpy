Rất sẵn lòng. Với nền tảng bạn đã học (Python, Tkinter, PySide6, SQLite, PostgreSQL, MongoDB...), đây là thời điểm rất phù hợp để học **lập trình bất đồng bộ (Asynchronous Programming)**.

Tôi sẽ dạy theo phong cách của một **Senior Python Developer**, không chỉ dạy cách sử dụng `asyncio`, mà còn giải thích **tại sao nó hoạt động**, **bên trong Event Loop làm gì**, và **khi nào nên hoặc không nên dùng async**.

---

# Giáo trình Python Asynchronous Programming (Từ Zero → Deep Dive)

Tổng cộng khoảng **40 buổi**, chia thành 8 chương.

---

# Chương 1. Nền tảng về Concurrency

(5 buổi)

Mục tiêu:

Hiểu rõ trước khi học async.

## Buổi 1

* Blocking là gì?
* Non-blocking là gì?
* Sequential Programming
* Ví dụ thực tế
* Tại sao chương trình bị "đơ"

Ví dụ

```python
import time

print("A")
time.sleep(5)
print("B")
```

Tại sao 5 giây không làm được gì khác?

---

## Buổi 2

Concurrency vs Parallelism

Đây là phần nhiều người nhầm nhất.

Học

* Single Thread
* Multi Thread
* Multi Process
* Async

So sánh bằng hình ảnh.

---

## Buổi 3

CPU-bound

Ví dụ

```python
for i in range(100000000):
    ...
```

Tại sao Async không giúp nhanh hơn?

---

## Buổi 4

I/O-bound

Ví dụ

* Download file
* HTTP Request
* Database
* Socket
* Read file

Tại sao Async sinh ra để giải quyết việc này.

---

## Buổi 5

GIL (Global Interpreter Lock)

Hiểu:

* Thread có thật chạy song song không?
* Async có liên quan GIL không?

---

# Chương 2. Coroutine

(5 buổi)

Đây là trái tim của Async.

---

## Buổi 6

Coroutine là gì?

```python
async def hello():
    print("Hello")
```

Tại sao không chạy?

---

## Buổi 7

await

Ví dụ

```python
await something()
```

await thực sự làm gì?

---

## Buổi 8

Event Loop

Đây là bài cực kỳ quan trọng.

Bạn sẽ hiểu

```
Task

↓

Event Loop

↓

OS
```

---

## Buổi 9

asyncio.run()

Bên trong làm gì?

---

## Buổi 10

Coroutine Chain

```
main()

↓

login()

↓

get_user()

↓

download_avatar()
```

Async chạy như thế nào?

---

# Chương 3. Task

(6 buổi)

---

## Buổi 11

Task là gì?

Khác Coroutine thế nào?

---

## Buổi 12

asyncio.create_task()

Ví dụ

```python
task = asyncio.create_task(download())
```

---

## Buổi 13

Chạy nhiều Task

```python
asyncio.gather()
```

---

## Buổi 14

wait()

as_completed()

FIRST_COMPLETED

---

## Buổi 15

Cancel Task

```python
task.cancel()
```

---

## Buổi 16

TaskGroup (Python 3.11+)

Structured Concurrency

---

# Chương 4. Event Loop Deep Dive

(5 buổi)

---

## Buổi 17

Loop hoạt động thế nào?

---

## Buổi 18

Future

Future là gì?

Tại sao tồn tại?

---

## Buổi 19

Callback

```python
future.add_done_callback()
```

---

## Buổi 20

Scheduler

Loop Scheduling

---

## Buổi 21

Loop Policy

uvloop

Windows Loop

Linux Loop

---

# Chương 5. Async I/O

(6 buổi)

---

## Buổi 22

Async HTTP

aiohttp

---

## Buổi 23

Download nhiều file

---

## Buổi 24

Async TCP Socket

---

## Buổi 25

Async UDP

---

## Buổi 26

Async File

aiofiles

---

## Buổi 27

Streaming

Chunk

Backpressure

---

# Chương 6. Async Database

(5 buổi)

---

## Buổi 28

SQLite

aiosqlite

---

## Buổi 29

PostgreSQL

asyncpg

---

## Buổi 30

SQLAlchemy Async

---

## Buổi 31

MongoDB

Motor

---

## Buổi 32

Connection Pool

---

# Chương 7. Async trong Framework

(5 buổi)

---

## Buổi 33

FastAPI Async

---

## Buổi 34

Quart

---

## Buổi 35

Django Async

---

## Buổi 36

PySide6 + Async

Đây là phần bạn sẽ thích.

Ghép

```
Qt Event Loop

+

asyncio
```

để GUI không bị treo.

---

## Buổi 37

Background Worker

---

# Chương 8. Deep Dive

(8 buổi)

---

## Buổi 38

Semaphore

Giới hạn số lượng Task

---

## Buổi 39

Queue

Producer Consumer

---

## Buổi 40

Lock

Condition

Barrier

Event

---

## Buổi 41

ContextVar

---

## Buổi 42

Timeout

Shield

---

## Buổi 43

Retry

Circuit Breaker

---

## Buổi 44

Performance Tuning

Profiler

Debug Async

---

## Buổi 45

Thiết kế Async Architecture

---

# Dự án thực hành

Trong suốt khóa học chúng ta sẽ xây dựng khoảng 10 project.

### Project 1

Downloader

```
URL

↓

Task

↓

Download

↓

Save
```

---

### Project 2

Async Chat Server

Socket

---

### Project 3

Crawler Website

aiohttp

BeautifulSoup

---

### Project 4

API Client

REST

---

### Project 5

Weather Dashboard

---

### Project 6

File Synchronizer

---

### Project 7

Log Collector

---

### Project 8

Async Database CRUD

---

### Project 9

PySide6 Async Downloader

GUI không bị treo.

---

### Project 10 (Capstone)

Xây dựng ứng dụng hoàn chỉnh:

```
PySide6

↓

Asyncio

↓

aiohttp

↓

asyncpg

↓

Redis

↓

WebSocket
```

Đây là mô hình thường gặp trong các ứng dụng desktop hiện đại.

---

# Sau khóa học bạn sẽ hiểu sâu

Không chỉ biết dùng mà còn hiểu rõ:

* Coroutine hoạt động như thế nào
* Event Loop vận hành ra sao
* await thực chất làm gì
* Future và Task khác nhau thế nào
* Scheduler phân phối công việc ra sao
* Vì sao async nhanh hơn trong bài toán I/O-bound
* Khi nào nên dùng Thread, Process hoặc Async
* Cách debug chương trình async
* Cách tích hợp async với PySide6, FastAPI và cơ sở dữ liệu
* Thiết kế kiến trúc ứng dụng bất đồng bộ có khả năng mở rộng

Khóa học sẽ đi từ nền tảng đến chuyên sâu, kết hợp giữa lý thuyết, ví dụ nhỏ và các dự án thực tế để bạn không chỉ "biết dùng" mà còn hiểu được cơ chế hoạt động bên trong của `asyncio`. Chúng ta sẽ bắt đầu từ **Buổi 1: Blocking, Non-blocking và vì sao lập trình bất đồng bộ ra đời** trước khi đi vào cú pháp `async`/`await`.
