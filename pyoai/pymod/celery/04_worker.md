# CELERY DEEP DIVE — BUỔI 4

# Worker Deep Dive: Kiến trúc Worker, Concurrency, Pool, ACK, Prefetch

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ hiểu:
> 
>   * Worker thực chất là gì. 
>   * Một Worker gồm những process nào. 
>   * Worker lấy task từ Redis/RabbitMQ như thế nào. 
>   * Prefork hoạt động ra sao. 
>   * Concurrency là gì. 
>   * ACK và Late ACK là gì. 
>   * Prefetch là gì. 
>   * Cách chọn số worker phù hợp. 
> 


* * *

# 1\. Worker là gì?

Nhiều người mới học nghĩ rằng:
    
    
    celery -A app worker

chỉ là chạy một chương trình Python.

Thực tế không phải vậy.

Worker là **một hệ thống quản lý nhiều tiến trình**.

Ví dụ:
    
    
                 Celery Worker
    
                        │
    
          ┌─────────────┼─────────────┐
    
          │             │             │
    
     Process 1      Process 2     Process 3
    
          │             │             │
    
       Task A        Task B        Task C

Worker giống như một "quản đốc nhà máy", còn các process là "công nhân".

* * *

# 2\. Một Task đi qua Worker như thế nào?

Giả sử:
    
    
    add.delay(10, 20)

Luồng đầy đủ:
    
    
    Producer
    
        │
    
        ▼
    
    Redis Queue
    
        │
    
        ▼
    
    Worker Main Process
    
        │
    
        ▼
    
    Child Process
    
        │
    
        ▼
    
    add()
    
        │
    
        ▼
    
    Result Backend

Điểm quan trọng:

> Main Process **không trực tiếp chạy task**.

Nó chỉ:

  * kết nối Broker 
  * nhận message 
  * phân phối task 



* * *

# 3\. Kiến trúc Worker

Ví dụ Worker có concurrency = 4.
    
    
                    Main Process
    
                           │
    
         ┌─────────────────┼──────────────────┐
    
         │                 │                  │
    
     Child 1           Child 2           Child 3
    
                                             │
    
                                         Child 4

Main Process giống như Dispatcher.

Các Child Process mới chạy code Python.

* * *

# 4\. Tại sao phải dùng nhiều Process?

Ví dụ:

Task:
    
    
    sleep(10)

Có 100 task.

Nếu chỉ có:
    
    
    Worker
    
    ↓
    
    Task1
    
    ↓
    
    Task2
    
    ↓
    
    Task3

Mất:
    
    
    100 × 10 = 1000 giây

* * *

Nếu có:
    
    
    8 process
    
    
    Task1
    
    Task2
    
    Task3
    
    Task4
    
    Task5
    
    Task6
    
    Task7
    
    Task8

Thời gian giảm rất nhiều.

* * *

# 5\. Concurrency là gì?

Ví dụ:
    
    
    celery worker -c 4

Nghĩa là:
    
    
    4 process

Ví dụ:
    
    
    Queue
    
    ↓
    
    Task1
    
    Task2
    
    Task3
    
    Task4
    
    ↓
    
    Worker
    
    ↓
    
    P1
    P2
    P3
    P4

Bốn task chạy cùng lúc.

* * *

# 6\. Celery Pool

Celery hỗ trợ nhiều loại Pool.

## Prefork (mặc định)
    
    
    Main Process
    
    ↓
    
    N Process

Đây là loại dùng nhiều nhất.

Ưu điểm:

  * ổn định 
  * tận dụng nhiều CPU 
  * tránh GIL 



Đây là lựa chọn mặc định cho hầu hết hệ thống production.

* * *

## Threads
    
    
    Process
    
    ↓
    
    Thread1
    
    Thread2
    
    Thread3

Ít dùng.

Lý do:

Python có GIL.

* * *

## Solo
    
    
    Worker
    
    ↓
    
    1 Process

Thường dùng để debug.

* * *

## Eventlet
    
    
    Green Threads

Thích hợp cho:

  * network 
  * socket 



* * *

## Gevent

Tương tự Eventlet.

Thường dùng:

  * hàng chục nghìn kết nối I/O. 



* * *

# 7\. Chọn Pool nào?

Công việc| Pool  
---|---  
CPU nặng| Prefork  
Gửi email| Prefork  
Crawl web| Prefork hoặc Gevent  
AI| Prefork  
Debug| Solo  
  
Trong 95% dự án Python, **Prefork** là lựa chọn tốt.

* * *

# 8\. Worker Lifecycle

Khi chạy:
    
    
    celery worker

Worker trải qua:
    
    
    Start
    
    ↓
    
    Load Config
    
    ↓
    
    Connect Broker
    
    ↓
    
    Register Task
    
    ↓
    
    Spawn Processes
    
    ↓
    
    Ready

Sau đó:
    
    
    Ready
    
    ↓
    
    Receive Task
    
    ↓
    
    Execute
    
    ↓
    
    ACK
    
    ↓
    
    Ready

* * *

# 9\. Worker nhận Task như thế nào?

Worker không liên tục hỏi:
    
    
    Có task chưa?

Broker giữ Queue.

Ví dụ:
    
    
    Redis
    
    ↓
    
    Task1
    
    Task2
    
    Task3

Worker:
    
    
    Lấy Task1
    
    ↓
    
    Thực thi
    
    ↓
    
    ACK
    
    ↓
    
    Lấy Task2

* * *

# 10\. ACK là gì?

ACK = Acknowledgement.

Sau khi hoàn thành:
    
    
    Task
    
    ↓
    
    Worker
    
    ↓
    
    SUCCESS
    
    ↓
    
    ACK Broker

Broker mới xóa message.

* * *

Nếu Worker chết trước ACK:
    
    
    Task
    
    ↓
    
    Worker
    
    ↓
    
    Crash

Broker biết:
    
    
    Task chưa ACK

Task sẽ được chạy lại (tùy Broker và cấu hình).

* * *

# 11\. Early ACK

Mặc định:

Worker nhận task là ACK ngay.
    
    
    Receive
    
    ↓
    
    ACK
    
    ↓
    
    Execute

Nếu Worker chết:

Task mất.

Đây gọi là:
    
    
    Early ACK

* * *

# 12\. Late ACK

Cấu hình:
    
    
    @app.task(
        acks_late=True
    )
    def process():
        ...

Luồng:
    
    
    Receive
    
    ↓
    
    Execute
    
    ↓
    
    SUCCESS
    
    ↓
    
    ACK

Nếu Worker chết:

Broker vẫn giữ task.

Worker khác sẽ chạy lại.

Đây là cấu hình thường dùng cho:

  * xử lý thanh toán 
  * crawl dữ liệu 
  * AI 
  * xử lý file 



* * *

# 13\. Prefetch là gì?

Ví dụ:

Worker có:
    
    
    Concurrency = 4

Celery có thể lấy trước nhiều task.
    
    
    Redis
    
    ↓
    
    Task1
    
    Task2
    
    Task3
    
    Task4
    
    Task5
    
    Task6
    
    ↓
    
    Worker

Worker giữ sẵn task trong bộ nhớ.

Đây gọi là:
    
    
    Prefetch

* * *

# 14\. Prefetch Multiplier

Ví dụ:
    
    
    Concurrency = 4
    
    Prefetch = 4

Worker lấy:
    
    
    16 task

Công thức:
    
    
    Concurrency × Prefetch Multiplier

Ví dụ:
    
    
    4 × 4 = 16

* * *

# 15\. Tại sao Prefetch có thể gây vấn đề?

Giả sử:

Worker A:
    
    
    Lấy 100 task

Worker B:
    
    
    Không còn task.

Kết quả:
    
    
    Worker A rất bận
    
    Worker B rảnh

Mất cân bằng tải.

* * *

# 16\. Cấu hình Prefetch
    
    
    worker_prefetch_multiplier = 1

Khi đó:
    
    
    Worker chỉ lấy đủ số task cần chạy.

Ví dụ:
    
    
    Concurrency = 4
    
    ↓
    
    Lấy đúng 4 task

Đây là cấu hình rất phổ biến cho production.

* * *

# 17\. Worker Autoscale

Ví dụ:
    
    
    celery worker \
    --autoscale=16,4

Ý nghĩa:

Ít việc:
    
    
    4 process

Nhiều việc:
    
    
    16 process

Celery tự mở rộng.

* * *

# 18\. Chọn Concurrency bao nhiêu?

Không có đáp án cố định.

Ví dụ máy:
    
    
    8 CPU

Task CPU-bound:
    
    
    Concurrency = 8

Task chủ yếu chờ I/O (gọi API, truy vấn mạng...):
    
    
    Concurrency = 16
    
    hoặc
    
    32

Cần benchmark để tìm giá trị tối ưu.

* * *

# 19\. Worker cho hệ thống Crawl Truyện

Giả sử hệ thống của bạn có ba loại task:
    
    
    crawl chapter
    
    parse html
    
    download image

Không nên để chung.

Nên tách:
    
    
    Redis
    
    │
    
    ├── Queue: crawler
    
    ├── Queue: parser
    
    └── Queue: image
    
              │
    
    ──────────┼────────────
    
    Worker Crawl
    
    Worker Parse
    
    Worker Image

Ưu điểm:

  * Dễ scale. 
  * Không để task nặng chặn task nhẹ. 
  * Có thể tối ưu từng nhóm worker. 



* * *

# 20\. Những sai lầm phổ biến

## Sai lầm 1
    
    
    Concurrency = 1000

trên máy 4 CPU.

→ Context switching quá nhiều.

* * *

## Sai lầm 2

Một task chạy:
    
    
    3 giờ

→ Nên chia thành nhiều task nhỏ.

* * *

## Sai lầm 3

Một Worker làm tất cả:

  * AI 
  * Email 
  * Crawl 
  * Resize ảnh 



→ Nên tách queue.

* * *

## Sai lầm 4

Không bật:
    
    
    acks_late=True

với task quan trọng.

→ Có nguy cơ mất task nếu worker bị dừng giữa chừng.

* * *

# Tổng kết

Sau buổi 4, bạn đã hiểu:

  * ✅ Worker không phải là một process đơn lẻ. 
  * ✅ Main Process chỉ điều phối, Child Process mới thực thi task. 
  * ✅ Concurrency quyết định số task chạy song song. 
  * ✅ Prefork là pool mặc định và phù hợp với đa số hệ thống. 
  * ✅ ACK quyết định khi nào Broker xóa task. 
  * ✅ `acks_late=True` giúp tăng độ tin cậy cho các tác vụ quan trọng. 
  * ✅ Prefetch ảnh hưởng lớn đến khả năng cân bằng tải. 
  * ✅ Có thể dùng nhiều queue và nhiều worker để mở rộng hệ thống. 



* * *

## Bài tập

### Bài 1

Giải thích bằng lời luồng xử lý của một task từ lúc gọi:
    
    
    add.delay(1, 2)

đến khi kết quả được lưu vào Result Backend.

* * *

### Bài 2

Máy chủ có:

  * 8 CPU 
  * 32 GB RAM 



Bạn cần xử lý:

  * 10.000 email 
  * 200.000 chương truyện cần crawl 
  * 50.000 ảnh cần tải 



Hãy đề xuất:

  * Số queue. 
  * Số worker. 
  * Concurrency cho từng worker. 
  * Có nên dùng `acks_late=True` cho từng loại task hay không? Giải thích. 



* * *

### Bài 3

Vẽ sơ đồ kiến trúc Celery cho dự án **Story Scraper** với ba queue:

  * `crawler`
  * `parser`
  * `image`



và chỉ rõ Producer, Broker, Worker và Database nằm ở đâu.

* * *

**Buổi 5** sẽ đi sâu vào **Result Backend và AsyncResult** , bao gồm vòng đời của một task, các trạng thái (`PENDING`, `STARTED`, `RETRY`, `FAILURE`, `SUCCESS`), cách truy vấn kết quả, timeout, revoke task và quản lý kết quả trong môi trường production.

