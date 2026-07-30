# CELERY DEEP DIVE — BUỔI 5

# Result Backend & AsyncResult Deep Dive

> **Mục tiêu**
> 
> Sau buổi này bạn sẽ hiểu:
> 
>   * Result Backend là gì. 
>   * AsyncResult hoạt động như thế nào. 
>   * Vòng đời (Lifecycle) của một Task. 
>   * Các trạng thái của Task. 
>   * Cách lấy kết quả đúng cách. 
>   * Timeout. 
>   * Revoke Task. 
>   * Quản lý kết quả trong Production. 
> 


* * *

# 1\. Result Backend là gì?

Ở các buổi trước chúng ta có:
    
    
    Producer
         │
         ▼
     Broker
         │
         ▼
     Worker

Nhưng sau khi Worker chạy xong:
    
    
    @app.task
    def add(x, y):
        return x + y

thì kết quả sẽ ở đâu?

Ví dụ:
    
    
    result = add.delay(10,20)

Làm sao biết kết quả là **30**?

Đó là nhiệm vụ của **Result Backend**.

* * *

## Kiến trúc
    
    
               Producer
    
                   │
    
                   ▼
    
              Redis Broker
    
                   │
    
                   ▼
    
             Celery Worker
    
                   │
    
                   ▼
    
            Result Backend
    
                   │
    
             SUCCESS
    
             Result = 30

* * *

# 2\. Broker và Backend khác nhau thế nào?

Đây là điểm rất nhiều người mới học nhầm.

## Broker

Broker chỉ làm nhiệm vụ:
    
    
    Task Message

Ví dụ:
    
    
    add(10,20)

Nó không lưu kết quả lâu dài.

* * *

## Backend

Backend lưu:
    
    
    Task ID
    
    Status
    
    Return Value
    
    Exception
    
    Traceback

Ví dụ:
    
    
    Task:
    
    ID:
    abc123
    
    State:
    SUCCESS
    
    Result:
    30

* * *

# 3\. Redis có thể vừa làm Broker vừa làm Backend

Ví dụ:
    
    
    Celery(
        broker="redis://localhost:6379/0",
    
        backend="redis://localhost:6379/1"
    )

Ở đây:
    
    
    Redis
    
    DB0
    
    ↓
    
    Task Queue
    
    ------------------
    
    DB1
    
    ↓
    
    Task Result

Tách database giúp dễ quản lý.

* * *

# 4\. AsyncResult là gì?

Ví dụ:
    
    
    result = add.delay(5,6)

Kết quả:
    
    
    print(result)
    
    
    <AsyncResult: 9d82...>

Đây KHÔNG phải kết quả của phép cộng.

Nó chỉ là:

> "Tay cầm" (Handle) để theo dõi Task.

* * *

# 5\. AsyncResult chứa gì?

Ví dụ:
    
    
    print(result.id)
    
    
    9d82b1...

Ngoài ra:
    
    
    result.status
    
    result.state
    
    result.ready()
    
    result.successful()
    
    result.failed()
    
    result.get()

* * *

# 6\. Vòng đời của Task

Một Task thường trải qua:
    
    
    PENDING
    
        │
    
        ▼
    
    RECEIVED
    
        │
    
        ▼
    
    STARTED
    
        │
    
        ▼
    
    SUCCESS

Nếu lỗi:
    
    
    STARTED
    
        │
    
        ▼
    
    FAILURE

Nếu retry:
    
    
    STARTED
    
        │
    
        ▼
    
    RETRY
    
        │
    
        ▼
    
    STARTED

* * *

# 7\. PENDING

Ví dụ:
    
    
    result = add.delay(10,20)

Ngay lập tức:
    
    
    print(result.state)

Có thể:
    
    
    PENDING

Không có nghĩa Task bị lỗi.

Nó chỉ có nghĩa:

> Worker chưa hoàn thành.

* * *

# 8\. STARTED

Muốn Celery ghi nhận trạng thái STARTED:
    
    
    @app.task(
        track_started=True
    )
    def process():
        ...

Khi Worker bắt đầu:
    
    
    STARTED

* * *

# 9\. SUCCESS

Task:
    
    
    @app.task
    def add(a,b):
        return a+b

Sau khi hoàn thành:
    
    
    result.state
    
    
    SUCCESS

* * *

# 10\. FAILURE

Ví dụ:
    
    
    @app.task
    def divide(a,b):
        return a/b

Nếu:
    
    
    divide.delay(10,0)

Worker:
    
    
    ZeroDivisionError

Task:
    
    
    FAILURE

* * *

# 11\. RETRY

Ví dụ:
    
    
    @app.task(bind=True)
    def download(self,url):
    
        try:
            ...
    
        except:
    
            self.retry(
                countdown=5
            )

State:
    
    
    RETRY

Sau 5 giây:
    
    
    STARTED

* * *

# 12\. REVOKED

Ví dụ:

Task đang chờ.

Bạn hủy:
    
    
    result.revoke()

Task:
    
    
    REVOKED

Không chạy nữa.

* * *

# 13\. result.ready()

Ví dụ:
    
    
    result.ready()

Trả về:
    
    
    True

nếu:

  * SUCCESS 
  * FAILURE 



Ngược lại:
    
    
    False

* * *

# 14\. successful()
    
    
    result.successful()

Ví dụ:
    
    
    True

nếu:
    
    
    SUCCESS

* * *

# 15\. failed()
    
    
    result.failed()

Ví dụ:
    
    
    True

nếu:
    
    
    FAILURE

* * *

# 16\. get()

Đây là hàm quan trọng nhất.

Ví dụ:
    
    
    result = add.delay(10,20)

Sau đó:
    
    
    value = result.get()
    
    
    30

* * *

## Nhưng hãy cẩn thận
    
    
    result.get()

là:
    
    
    Blocking

Nó sẽ chờ.

Ví dụ:

Task:
    
    
    sleep(60)

Nếu:
    
    
    result.get()

Python sẽ đứng:
    
    
    60 giây

* * *

# 17\. Timeout

Có thể:
    
    
    result.get(
        timeout=5
    )

Nếu:

Task:
    
    
    30 giây

Kết quả:
    
    
    TimeoutError

* * *

# 18\. Polling

Một cách phổ biến:
    
    
    while not result.ready():
        print("Waiting...")

Hoặc:
    
    
    import time
    
    while True:
    
        if result.ready():
            break
    
        time.sleep(1)

* * *

# 19\. Exception

Nếu Task lỗi:
    
    
    divide.delay(10,0)
    
    
    result.get()

Sẽ ném:
    
    
    ZeroDivisionError

Giống như lỗi xảy ra trong code gốc.

* * *

# 20\. Traceback

Celery lưu traceback.

Ví dụ:
    
    
    print(
        result.traceback
    )

Ví dụ:
    
    
    File...
    
    ZeroDivisionError

Rất hữu ích để debug.

* * *

# 21\. Forget Result

Nếu không cần kết quả:
    
    
    result.forget()

Celery xóa:
    
    
    Status
    
    Result
    
    Metadata

Khỏi Backend.

* * *

# 22\. Result Expiration

Không nên lưu kết quả mãi mãi.

Ví dụ:
    
    
    result_expires = 3600

Sau:
    
    
    1 giờ

Celery tự xóa.

* * *

# 23\. Production

Rất nhiều Task:
    
    
    10 triệu task/ngày

Nếu lưu mãi:

Redis sẽ đầy.

Thông thường:
    
    
    1 giờ
    
    6 giờ
    
    24 giờ

rồi xóa.

* * *

# 24\. Có phải Task nào cũng cần Result?

Không.

Ví dụ:
    
    
    send_email.delay(...)

Bạn không cần:
    
    
    Email gửi xong trả về gì?

Có thể:
    
    
    task_ignore_result = True

Hoặc:
    
    
    @app.task(
        ignore_result=True
    )

Giúp:

  * giảm RAM 
  * giảm Redis 
  * tăng tốc 



* * *

# 25\. Ví dụ thực tế: Story Scraper

Task:
    
    
    crawl_chapter.delay(url)

Bạn muốn Dashboard hiển thị:
    
    
    Task:
    
    SUCCESS
    
    Chapter:
    
    120
    
    Time:
    
    1.2s

Dashboard:
    
    
    Task ID
    
    ↓
    
    AsyncResult
    
    ↓
    
    Backend
    
    ↓
    
    Status

* * *

# 26\. Kiến trúc hoàn chỉnh
    
    
                    Producer
    
                        │
    
                        ▼
    
                 Redis Broker
    
                        │
    
                        ▼
    
                 Celery Worker
    
                        │
    
                execute task
    
                        │
    
                        ▼
    
                Result Backend
    
                        │
    
                AsyncResult
    
                        │
    
                Dashboard/API

* * *

# 27\. Khi nào KHÔNG nên gọi `result.get()`?

Đây là một lỗi phổ biến.

Ví dụ trong FastAPI:
    
    
    @app.post("/crawl")
    def crawl():
    
        result = crawl_book.delay()
    
        return result.get()

Như vậy:
    
    
    API sẽ chờ Worker.

=> Mất ý nghĩa của Celery.

Đúng hơn:
    
    
    @app.post("/crawl")
    def crawl():
    
        result = crawl_book.delay()
    
        return {
            "task_id": result.id
        }

API khác sẽ kiểm tra:
    
    
    GET /task/{id}

để xem trạng thái.

* * *

# Tổng kết

Sau buổi 5 bạn đã hiểu:

  * ✅ Broker khác Backend. 
  * ✅ AsyncResult là đối tượng theo dõi Task. 
  * ✅ Lifecycle của Task. 
  * ✅ Các trạng thái (`PENDING`, `STARTED`, `SUCCESS`, `FAILURE`, `RETRY`, `REVOKED`). 
  * ✅ `ready()`, `successful()`, `failed()`. 
  * ✅ `get()` và nhược điểm của việc chặn (blocking). 
  * ✅ `timeout`. 
  * ✅ `forget()`. 
  * ✅ `ignore_result`. 
  * ✅ Cách quản lý kết quả trong môi trường production. 



* * *

# Bài tập

## Bài 1

Viết Task:
    
    
    @app.task
    def square(x):
        return x * x

Thực hiện:

  * Gửi bằng `delay()`. 
  * In `task_id`. 
  * In `state`. 
  * Gọi `get()`. 
  * In `successful()`. 



* * *

## Bài 2

Viết Task:
    
    
    @app.task
    def divide(a,b):
        return a/b

Gọi:
    
    
    divide.delay(10,0)

Quan sát:

  * `state`
  * `failed()`
  * `traceback`
  * `get()`



và giải thích vì sao `get()` ném ngoại lệ.

* * *

## Bài 3

Thiết kế API cho dự án **Story Scraper** :

  * `POST /crawl` → tạo task và trả về `task_id`. 
  * `GET /tasks/{task_id}` → trả về: 
    * trạng thái (`PENDING`, `STARTED`, `SUCCESS`, `FAILURE`...) 
    * kết quả (nếu có) 
    * lỗi (nếu có) 



Giải thích vì sao API này tốt hơn việc gọi `result.get()` ngay trong request.

* * *

## Buổi 6 tiếp theo

Chúng ta sẽ học **Task Design Pattern** — phần rất quan trọng trong các hệ thống thực tế:

  * Thiết kế task nhỏ hay lớn? 
  * Idempotency (tính lặp lại an toàn). 
  * Atomic Task. 
  * Retry-safe Task. 
  * Giao dịch (transaction) với database. 
  * Các anti-pattern thường gặp khi thiết kế Celery Task. 



Đây là phần giúp bạn viết các task có khả năng mở rộng và đáng tin cậy trong production.

