# CELERY DEEP DIVE — BUỔI 2

# Cài đặt môi trường Celery thực chiến

# Redis Broker + Project Structure + Worker đầu tiên

* * *

# 1\. Ôn lại kiến trúc Celery

Ở buổi 1 chúng ta đã biết:
    
    
                     Producer
                        |
                        |
                        v
                  Message Broker
                  (Redis/RabbitMQ)
                        |
                        |
                        v
                   Celery Worker
                        |
                        |
                        v
                 Result Backend

Hôm nay chúng ta sẽ tự dựng hệ thống này.

Mục tiêu cuối buổi:

  * Cài Celery 
  * Cài Redis 
  * Tạo project chuẩn 
  * Tạo task đầu tiên 
  * Chạy worker 
  * Gửi task 
  * Quan sát worker xử lý 



* * *

# 2\. Celery cần những thành phần gì?

Một hệ thống tối thiểu:
    
    
    Python Application
            |
            |
            v
    
         Celery
    
            |
            |
            v
    
          Redis
    
            |
            |
            v
    
     Celery Worker

Chúng ta cần:

Thành phần| Vai trò  
---|---  
Celery| Task framework  
Redis| Message Broker  
Worker| Process chạy task  
Python| Viết task  
  
* * *

# 3\. Chuẩn bị môi trường

Tạo project:
    
    
    celery_learning/
    
    ├── venv/
    │
    ├── app/
    │   ├── __init__.py
    │   ├── celery_app.py
    │   └── tasks.py
    │
    ├── run_task.py
    │
    └── requirements.txt

Đây là cấu trúc thực tế hơn so với để tất cả trong một file.

* * *

# 4\. Tạo virtual environment

Linux/macOS:
    
    
    python -m venv venv
    
    source venv/bin/activate

Windows:
    
    
    python -m venv venv
    
    venv\Scripts\activate

* * *

# 5\. Cài Celery
    
    
    pip install celery

Kiểm tra:
    
    
    celery --version

Ví dụ:
    
    
    5.5.x

* * *

# 6\. Cài Redis

Celery không tự lưu queue.

Nó cần Broker.

Chúng ta dùng Redis.

## Docker (khuyến nghị)

Nếu bạn đã học Docker thì dùng cách này:
    
    
    docker run \
    --name redis-celery \
    -p 6379:6379 \
    -d redis

Kiểm tra:
    
    
    docker ps

Kết quả:
    
    
    redis-celery
    0.0.0.0:6379->6379

* * *

# 7\. Cài Redis client Python

Celery cần thư viện kết nối Redis:
    
    
    pip install redis

* * *

# 8\. Tạo Celery Application

File:
    
    
    app/celery_app.py

Code:
    
    
    from celery import Celery
    
    
    celery_app = Celery(
        "learning",
    
        broker=
        "redis://localhost:6379/0",
    
        backend=
        "redis://localhost:6379/1"
    )

Giải thích:

## Tên app
    
    
    "learning"

Tên Celery instance.

* * *

## Broker
    
    
    redis://localhost:6379/0

Redis database số 0:
    
    
    Redis
    
    DB0
     |
     |-- task queue
    
    
    DB1
     |
     |-- results

* * *

## Backend
    
    
    redis://localhost:6379/1

Lưu:
    
    
    task_id
    
    status
    
    result

* * *

# 9\. Tạo Task đầu tiên

File:
    
    
    app/tasks.py

Code:
    
    
    from .celery_app import celery_app
    
    
    @celery_app.task
    def add(x, y):
    
        print(
            f"Calculating {x}+{y}"
        )
    
        return x + y

* * *

# 10\. Ý nghĩa decorator @task

Code:
    
    
    @celery_app.task
    def add():
        pass

Không còn là function bình thường.

Trước:
    
    
    add()

chạy ngay.

Sau:
    
    
    add()

tạo task.

Muốn gửi vào queue:
    
    
    add.delay()

* * *

# 11\. Chạy Celery Worker

Đứng ở thư mục:
    
    
    celery_learning

Chạy:
    
    
    celery \
    -A app.celery_app \
    worker \
    --loglevel=info

Giải thích:

## -A
    
    
    -A app.celery_app

Nói với Celery:

"App Celery nằm ở đâu?"

* * *

## worker

Khởi động worker:
    
    
    Celery Worker

* * *

## \--loglevel

Mức log:
    
    
    info
    debug
    warning
    error

* * *

# 12\. Worker chạy thành công

Bạn sẽ thấy:
    
    
    -------------- celery@PC
    
    [tasks]
    
     . app.tasks.add
    
    
    Connected to redis://localhost:6379/0
    
    
    ready.

Điểm quan trọng:
    
    
    ready.

nghĩa là:

> Worker đang chờ task.

* * *

# 13\. Gửi task

Tạo file:
    
    
    run_task.py

Code:
    
    
    from app.tasks import add
    
    
    result = add.delay(
        10,
        20
    )
    
    
    print(
        result.id
    )

Chạy:
    
    
    python run_task.py

Ví dụ:
    
    
    8e4f2a3d-xxxx

Đây là:
    
    
    Task ID

* * *

# 14\. Quan sát Worker

Terminal worker:
    
    
    Task app.tasks.add received
    
    
    Calculating 10+20
    
    
    Task succeeded
    
    
    30

Luồng:
    
    
    run_task.py
    
        |
        |
    add.delay()
    
        |
        |
    Redis
    
        |
        |
    Worker
    
        |
        |
    execute add()
    
        |
        |
    Result

* * *

# 15\. Kiểm tra kết quả Task

Hiện tại:
    
    
    result = add.delay(10,20)

trả về:
    
    
    AsyncResult

Không phải:
    
    
    30

Ví dụ:
    
    
    print(result)

Kết quả:
    
    
    <AsyncResult: 8e4f2a>

* * *

Muốn lấy kết quả:
    
    
    print(
        result.get()
    )

Kết quả:
    
    
    30

* * *

# 16\. Một lỗi rất phổ biến

## Lỗi:
    
    
    Received unregistered task

Ví dụ:

Worker không biết task:
    
    
    app.tasks.add

Nguyên nhân:

Worker chưa import tasks.

* * *

# 17\. Đăng ký tasks đúng cách

Sửa:

`celery_app.py`
    
    
    celery_app = Celery(
        "learning",
        broker=
        "redis://localhost:6379/0",
        backend=
        "redis://localhost:6379/1",
    
        include=[
            "app.tasks"
        ]
    )

Bây giờ Celery biết:
    
    
    app.tasks.add

* * *

# 18\. Debug Celery

Xem task:
    
    
    celery \
    -A app.celery_app \
    inspect registered

Ví dụ:
    
    
    registered tasks:
    
    app.tasks.add

* * *

# 19\. Celery worker thực sự là gì?

Khi chạy:
    
    
    celery worker

Nó tạo:
    
    
    Main Process
    
           |
           |
           + Worker Process 1
    
           |
           + Worker Process 2
    
           |
           + Worker Process 3
    

Mặc định dùng:
    
    
    prefork

(multi process)

Phần này sẽ học sâu ở buổi 4.

* * *

# 20\. Project thực tế nên tổ chức thế nào?

Ví dụ dự án lớn:
    
    
    project/
    
    ├── celery_app/
    │
    │   ├── config.py
    │   ├── app.py
    │
    ├── tasks/
    │
    │   ├── email.py
    │   ├── crawler.py
    │   ├── image.py
    │
    ├── services/
    │
    ├── repositories/
    │
    └── main.py

Đây chính là kiểu kiến trúc phù hợp với dự án:

  * scraper truyện 
  * hệ thống AI 
  * backend API 



* * *

# Bài tập Buổi 2

## Bài 1

Tạo task:
    
    
    multiply(x,y)

Chạy:
    
    
    multiply.delay(5,6)

Kết quả:
    
    
    30

* * *

## Bài 2

Tạo task:
    
    
    download_file(url)

Giả lập:
    
    
    sleep(10)

Quan sát:

  * API không bị block 
  * Worker chạy riêng 



* * *

## Bài 3

Vẽ lại kiến trúc:
    
    
    run_task.py
    
          ?
    
          ?
    
          ?
    
          ?
    

* * *

# Kiến thức đạt được sau Buổi 2

Bạn đã hiểu:

✅ Cài Celery  
✅ Redis Broker  
✅ Result Backend  
✅ Celery App  
✅ Task decorator  
✅ Worker  
✅ delay()  
✅ AsyncResult  
✅ Project structure cơ bản

* * *

**Buổi 3 tiếp theo: Celery Task Deep Dive — delay(), apply_async(), Task Signature, arguments, countdown, ETA, expiration và cách điều khiển task chuyên nghiệp.**

