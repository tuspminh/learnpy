# CELERY DEEP DIVE — BUỔI 3

# Task Deep Dive: delay(), apply_async(), Signature, Arguments, Scheduling Task

* * *

Trong buổi 2 chúng ta đã tạo được task đầu tiên:
    
    
    @app.task
    def add(x, y):
        return x + y

và gọi:
    
    
    add.delay(10, 20)

Nhưng trong hệ thống thực tế, chúng ta cần kiểm soát nhiều hơn:

  * Gửi task khi nào? 
  * Task chạy sau bao lâu? 
  * Task hết hạn lúc nào? 
  * Ưu tiên task nào trước? 
  * Truyền tham số thế nào? 
  * Ghép task với nhau ra sao? 



Đó là nội dung buổi hôm nay.

* * *

# 1\. Celery Task thực chất là gì?

Một function Python bình thường:
    
    
    def add(x, y):
        return x + y

chạy trực tiếp:
    
    
    result = add(10,20)

Luồng:
    
    
    Python Process
    
         |
         |
        add()
    
         |
         |
       return 30

* * *

Nhưng Celery Task:
    
    
    @app.task
    def add(x,y):
        return x+y

không còn chỉ là function.

Nó trở thành:
    
    
    Task Object
    
    +
    Message Definition
    
    +
    Metadata

Ví dụ:
    
    
    Task:
    
    name:
    app.tasks.add
    
    args:
    10,20
    
    id:
    8f923ab
    
    queue:
    default

Celery gửi toàn bộ thông tin này vào Broker.

* * *

# 2\. delay() — cách gửi task đơn giản nhất

Ví dụ:
    
    
    add.delay(5,6)

Tương đương:
    
    
    add.apply_async(
        args=[5,6]
    )

* * *

## delay() làm gì?

Nó:

  1. Tạo message 
  2. Serialize dữ liệu 
  3. Gửi Broker 
  4. Trả về AsyncResult 



Luồng:
    
    
    Client
    
    add.delay(5,6)
    
            |
            |
            v
    
          Redis
    
            |
            |
            v
    
     Celery Worker

* * *

# 3\. AsyncResult

Khi gọi:
    
    
    result = add.delay(5,6)

Bạn nhận:
    
    
    AsyncResult

Ví dụ:
    
    
    print(result.id)

Kết quả:
    
    
    a92bd821-xxxx

Đây là Task ID.

* * *

Task ID dùng để:

  * kiểm tra trạng thái 
  * lấy kết quả 
  * debug 



* * *

# 4\. Task State

Celery quản lý trạng thái:
    
    
    PENDING
     |
     |
    STARTED
     |
     |
    SUCCESS

hoặc:
    
    
    PENDING
    
     |
     |
    STARTED
    
     |
     |
    FAILURE

Ví dụ:
    
    
    result.status

Có thể trả:
    
    
    SUCCESS

* * *

# 5\. apply_async() — điều khiển task chuyên nghiệp

delay():
    
    
    task.delay(args)

nhanh nhưng ít tùy chỉnh.

apply_async():
    
    
    task.apply_async(
        args=[...],
        kwargs={...},
    )

Cho phép:

  * countdown 
  * eta 
  * expires 
  * queue 
  * priority 



* * *

# 6\. Truyền args

Ví dụ:
    
    
    @app.task
    def multiply(a,b):
        return a*b

Cách 1:
    
    
    multiply.delay(3,4)

Cách 2:
    
    
    multiply.apply_async(
        args=[3,4]
    )

Kết quả:
    
    
    12

* * *

# 7\. Truyền kwargs

Task:
    
    
    @app.task
    def send_email(
        email,
        subject
    ):
        pass

Gọi:
    
    
    send_email.apply_async(
        kwargs={
            "email":
            "abc@gmail.com",
    
            "subject":
            "Hello"
        }
    )

* * *

# 8\. countdown — chạy sau N giây

Ví dụ:

Muốn gửi email sau 60 giây:
    
    
    send_email.apply_async(
        args=["user@gmail.com"],
        countdown=60
    )

Luồng:
    
    
    0s
    
    Task gửi Redis
    
    
    60s
    
    
    Worker nhận
    
    
    execute

Ứng dụng:

  * gửi email xác nhận 
  * delay notification 
  * retry 



* * *

# 9\. eta — chạy tại thời điểm cụ thể

ETA:

Estimated Time of Arrival

Ví dụ:
    
    
    from datetime import datetime, timedelta
    
    
    run_time = datetime.now() + timedelta(
        minutes=10
    )
    
    
    task.apply_async(
        eta=run_time
    )

Task chạy sau 10 phút.

* * *

Countdown:
    
    
    sau bao lâu

ETA:
    
    
    vào lúc nào

* * *

# 10\. expires — thời gian hết hạn task

Ví dụ:
    
    
    task.apply_async(
        expires=60
    )

Ý nghĩa:

Task chỉ hợp lệ 60 giây.

Nếu worker nhận sau:
    
    
    Task expired

Ứng dụng:

Ví dụ:

Flash sale:
    
    
    Đặt hàng
    
    Task thanh toán
    
    expires=300

Sau 5 phút:

Không cần xử lý nữa.

* * *

# 11\. Task name

Mỗi task có tên:
    
    
    @app.task(
        name="send.email"
    )
    def send_email():
        pass

Celery lưu:
    
    
    send.email

Không phải:
    
    
    module.function

* * *

# 12\. bind=True — truy cập Task object

Ví dụ:
    
    
    @app.task(bind=True)
    def process(self):
        print(self.request.id)

`self` chứa:
    
    
    self.request

Thông tin:
    
    
    id
    args
    kwargs
    retries
    hostname

Ví dụ:
    
    
    @app.task(bind=True)
    def hello(self):
    
        print(
            self.request.id
        )

Kết quả:
    
    
    Task ID:
    abc123

* * *

# 13\. retry cơ bản

Ví dụ:
    
    
    @app.task(bind=True)
    def download(self,url):
    
        try:
            request(url)
    
        except Exception:
    
            self.retry(
                countdown=10
            )

Ý nghĩa:
    
    
    download fail
    
          |
          |
          v
    
    retry sau 10 giây

Phần retry chúng ta học sâu ở buổi 7.

* * *

# 14\. Task Routing cơ bản

Có nhiều loại task:
    
    
    Email task
    
    Image task
    
    AI task
    
    Crawler task

Không nên để chung:
    
    
               Redis
    
                 |
        -----------------
    
        worker email
    
        worker AI
    
        worker crawler
    

Celery hỗ trợ queue.

Ví dụ:
    
    
    task.apply_async(
        queue="crawler"
    )

* * *

# 15\. Immutable Task

Thông thường:
    
    
    task.s(10,20)

có thể nhận thêm args.

Immutable:
    
    
    task.si(10,20)

Không nhận thêm.

Phần này quan trọng khi học Canvas.

* * *

# 16\. Signature (s)

Signature là mô tả task chưa chạy.

Ví dụ:
    
    
    sig = add.s(10,20)

Hiện tại:
    
    
    Chưa chạy

Nó chỉ là:
    
    
    Task definition

Chạy:
    
    
    sig.delay()

* * *

Ví dụ:
    
    
    from celery import signature
    
    
    sig = signature(
        "app.tasks.add",
        args=(10,20)
    )

* * *

# 17\. Vì sao Signature quan trọng?

Vì Celery có workflow:

Ví dụ:
    
    
    Download file
    
           |
           |
    
    Convert
    
           |
           |
    
    Upload

Ta tạo:
    
    
    download.s()
    
    convert.s()
    
    upload.s()

Rồi nối lại.

Đây là Celery Canvas.

* * *

# 18\. So sánh các cách gọi Task

Cách| Khi dùng  
---|---  
delay()| đơn giản  
apply_async()| cần điều khiển  
signature()| workflow  
si()| immutable workflow  
  
* * *

# 19\. Ví dụ thực tế: hệ thống crawl truyện

Giả sử:
    
    
    Add website
    
    
          |
          |
    
    crawl_book.delay(url)
    
    
          |
          |
    
    Worker
    
    
          |
          |
    
    parse_content
    
    
          |
          |
    
    save_database

Nhưng muốn:

  * Crawl sau 5 phút 
  * Nếu lỗi retry 
  * Chạy queue crawler 



Ta dùng:
    
    
    crawl_book.apply_async(
        args=[url],
    
        countdown=300,
    
        queue="crawler"
    )

* * *

# Bài tập Buổi 3

## Bài 1

Viết task:
    
    
    @task
    def backup_database():
        pass

Yêu cầu:

  * chạy sau 1 giờ 
  * hết hạn sau 2 giờ 



Gợi ý:
    
    
    apply_async(
        countdown=?,
        expires=?
    )

* * *

## Bài 2

Tạo task:
    
    
    resize_image(filename)

Gọi bằng:

  1. delay() 
  2. apply_async() 



* * *

## Bài 3

Tạo signature:
    
    
    add.s(10,20)

Chạy sau.

* * *

# Kiến thức đạt được sau Buổi 3

Bạn hiểu:

✅ Celery Task  
✅ delay()  
✅ apply_async()  
✅ AsyncResult  
✅ Task ID  
✅ Task State  
✅ countdown  
✅ ETA  
✅ expires  
✅ bind=True  
✅ Signature cơ bản  
✅ Queue concept

* * *

# Buổi 4 tiếp theo:

# **Celery Worker Deep Dive**

  * Worker process hoạt động thế nào 
  * Prefork model 
  * Concurrency 
  * Pool 
  * Worker lifecycle 
  * ACK message 
  * Prefetch 
  * Tối ưu worker cho production 



Đây là phần rất quan trọng để chạy Celery ở quy mô lớn.

