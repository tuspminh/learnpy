# CELERY DEEP DIVE — BUỔI 1

# Tổng quan Celery và kiến trúc Background Task

* * *

# 1\. Vấn đề thực tế mà Celery giải quyết

Hãy tưởng tượng bạn đang xây dựng một ứng dụng web.

Ví dụ:

  * Người dùng đăng ký tài khoản 
  * Upload một video 2GB 
  * Yêu cầu tạo file PDF 
  * Crawl 100.000 trang web 
  * Gửi email hàng loạt 
  * Huấn luyện model AI 



Nếu xử lý trực tiếp trong request:
    
    
    Client
      |
      |
      v
    FastAPI / Django
      |
      |
      +---- Upload file
      |
      +---- Resize image
      |
      +---- Convert video
      |
      +---- Send email
      |
      |
    Response sau 10 phút

Vấn đề:

  * Người dùng phải chờ. 
  * Request có thể timeout. 
  * Server bị chiếm tài nguyên. 
  * Không thể scale. 



Ví dụ:
    
    
    def register_user():
    
        save_user()
    
        send_email()
    
        create_avatar()
    
        generate_report()
    
        return "OK"

Hàm này làm quá nhiều việc.

* * *

# 2\. Background Task là gì?

Background Task nghĩa là:

> Giao việc cho một tiến trình khác xử lý sau.

Thay vì:
    
    
    User
     |
     |
    Request
     |
     |
    Xử lý tất cả
     |
     |
    Response

Ta làm:
    
    
    User
     |
     |
    Request
     |
     |
    Gửi nhiệm vụ
     |
     |
    Response ngay
    
    
           Worker
              |
              |
              |
           xử lý sau

Ví dụ:

User đăng ký:
    
    
    POST /register
    
            |
            |
            v
    
    Create user
    
            |
            |
            v
    
    Push task:
    
    send_welcome_email(user_id)
    
    
            |
            |
            v
    
    return OK

Sau đó worker:
    
    
    Celery Worker
    
         |
         |
    send email

* * *

# 3\. Celery là gì?

Celery là:

> Một distributed task queue framework viết bằng Python.

Nói đơn giản:

Celery là hệ thống giúp Python:

  * gửi công việc sang hàng đợi 
  * có worker nhận việc 
  * xử lý bất đồng bộ 
  * quản lý trạng thái 



Ví dụ:

Bạn có 1 triệu ảnh cần resize.

Không làm:
    
    
    Python script
    
    ảnh1
    ảnh2
    ảnh3
    ...
    ảnh1000000

Mà:
    
    
    Task Queue
    
    
    resize(img1)
    resize(img2)
    resize(img3)
    ...
    resize(img1000000)
    
    
            |
            |
    
    Workers
    
    
    Worker 1
    Worker 2
    Worker 3
    Worker 4
    

* * *

# 4\. Kiến trúc Celery

Một hệ thống Celery gồm 3 thành phần chính:

# 4.1 Producer

Producer là nơi tạo task.

Ví dụ:

Web API:
    
    
    send_email.delay(
        "user@gmail.com"
    )

Nó không gửi email.

Nó chỉ nói:

> "Này Celery, có việc cần làm."

* * *

# 4.2 Broker

Broker là trung gian nhận task.

Ví dụ:
    
    
    Producer
    
        |
        |
        v
    
     Message Broker
    
        |
        |
        v
    
     Worker

Broker phổ biến:

## Redis
    
    
    Producer
       |
       |
     Redis Queue
       |
       |
     Worker

## RabbitMQ
    
    
    Producer
    
        |
     Exchange
    
        |
     Queue
    
        |
     Worker

Broker giống như:

> Bưu điện nhận thư và chuyển thư.

* * *

# 4.3 Worker

Worker là người thực hiện công việc.

Ví dụ:

Task:
    
    
    @app.task
    def send_email(email):
        ...

Worker:
    
    
    Celery Worker
    
    
    Nhận task:
    
    send_email(
    "user@gmail.com"
    )
    
    
    Thực thi:
    
    
    SMTP
     |
     |
    Email sent
    

* * *

# 4.4 Result Backend

Sau khi worker chạy xong:
    
    
    Worker
    
       |
       |
       v
    
    Result Backend
    

Lưu:

  * thành công 
  * thất bại 
  * kết quả 



Ví dụ:

Task:
    
    
    @app.task
    def add(x,y):
        return x+y

Celery trả:
    
    
    Task ID:
    
    8af23d...
    
    
    Status:
    
    SUCCESS
    
    
    Result:
    
    15

* * *

# 5\. Toàn bộ luồng hoạt động

Ví dụ:
    
    
    add.delay(10,5)

Luồng:
    
    
                  Python App
    
                      |
                      |
                 create task
    
                      |
                      v
    
    
                  Broker
                  Redis
    
                      |
                      |
              task message
    
    
                      |
                      v
    
    
                 Celery Worker
    
    
                      |
                      |
    
                  execute
    
    
                      |
                      v
    
    
                Result Backend
    
                      |
                      |
    
                  SUCCESS
    

* * *

# 6\. Celery khác Threading / Multiprocessing thế nào?

## Threading

Trong cùng process:
    
    
    Python Process
    
     Thread 1
     Thread 2
     Thread 3
    

Giới hạn:

  * cùng máy 
  * phụ thuộc GIL 



* * *

## Multiprocessing
    
    
    Computer
    
     Process 1
     Process 2
     Process 3
    

Vẫn:

  * cùng máy 
  * khó quản lý 



* * *

## Celery
    
    
    Machine A
    
    API
    
    
          |
          |
          v
    
    
    Machine B
    
    Worker
    
    
          |
          |
          v
    
    
    Machine C
    
    Worker
    

Có thể:

  * nhiều server 
  * nhiều worker 
  * scale ngang 



* * *

# 7\. Celery dùng trong thực tế ở đâu?

## 1\. Email

Ví dụ:

100.000 email marketing:
    
    
    email_task(user1)
    email_task(user2)
    ...

* * *

## 2\. Web scraping

Rất phù hợp với dự án của bạn:
    
    
    Website source
    
         |
         |
    Celery Queue
    
         |
    -----------------
    
    Worker 1
    crawl trang 1
    
    Worker 2
    crawl trang 2
    
    Worker 3
    parse HTML
    

* * *

## 3\. Xử lý file

Upload:
    
    
    video.mp4
    
    
    Celery
    
       |
       |
    convert
    
       |
       |
    thumbnail
    
       |
       |
    compress
    

* * *

## 4\. AI

Ví dụ:

Generate ảnh:
    
    
    API
    
     |
     |
    Celery
    
     |
     |
    GPU Worker
    
     |
     |
    AI Model
    

* * *

# 8\. Celery không phải là gì?

## Không phải Asyncio

Asyncio:
    
    
    Một chương trình
    Một event loop

Celery:
    
    
    Nhiều process
    Nhiều máy
    Distributed

* * *

## Không phải Scheduler

Celery không tự chạy theo giờ.

Muốn:

"mỗi ngày 12h chạy"

dùng:
    
    
    Celery Beat

(chúng ta học sau)

* * *

# 9\. Cài đặt Celery đầu tiên

Tạo môi trường:
    
    
    celery-demo/
    
        app.py
        tasks.py

Cài:
    
    
    pip install celery redis

* * *

# 10\. Ví dụ Celery đơn giản

tasks.py
    
    
    from celery import Celery
    
    
    app = Celery(
        "demo",
        broker="redis://localhost:6379/0"
    )
    
    
    @app.task
    def add(x, y):
        return x + y

Chạy worker:
    
    
    celery -A tasks worker --loglevel=info

Gọi task:
    
    
    from tasks import add
    
    
    result = add.delay(10,20)
    
    print(result.id)

Kết quả:
    
    
    Task sent:
    
    c4a23f...
    
    
    Worker:
    
    Task add received
    
    Task completed

* * *

# 11\. Tư duy quan trọng khi học Celery

Đừng nghĩ:

"Celery chạy hàm Python khác"

Mà hãy nghĩ:
    
    
    Task = Message
    
    Worker = Consumer
    
    Broker = Transport
    
    Result Backend = Database trạng thái
    

Celery thực chất là một hệ thống **message-driven architecture**.

* * *

# Bài tập Buổi 1

## Bài 1

Giải thích bằng lời:
    
    
    Producer
    Broker
    Worker
    Result Backend

hoạt động thế nào.

* * *

## Bài 2

Thiết kế kiến trúc Celery cho:

Một app đọc truyện:

  * Người dùng thêm website mới 
  * Hệ thống crawl chương mới 
  * Parse nội dung 
  * Lưu database 



Vẽ sơ đồ:
    
    
    ?
     |
     |
    ?
     |
     |
    ?

* * *

## Bài 3

Tự trả lời:

Tại sao không nên dùng:
    
    
    while True:
        crawl()

mà nên dùng Celery?

* * *

**Buổi 2 tiếp theo: Cài đặt Celery thực chiến — Redis Broker, tạo project chuẩn, chạy worker đầu tiên, debug Celery.**

