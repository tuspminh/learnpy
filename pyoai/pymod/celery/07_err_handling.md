# CELERY DEEP DIVE — Buổi 7

# Retry & Error Handling Deep Dive

## Xây dựng Celery Worker có khả năng tự phục hồi (Self-Healing)

> **Mục tiêu**
> 
> Sau buổi này bạn sẽ hiểu:
> 
>   * Retry hoạt động như thế nào. 
>   * `self.retry()`
>   * `autoretry_for`
>   * `max_retries`
>   * `retry_backoff`
>   * Exponential Backoff 
>   * Retry có điều kiện. 
>   * Khi nào nên và không nên retry. 
>   * Thiết kế chiến lược retry trong production. 
> 


* * *

# 1\. Retry là gì?

Trong hệ thống thực tế, lỗi là điều **không thể tránh khỏi**.

Ví dụ:
    
    
    Celery Worker
    
    ↓
    
    Download API
    
    ↓
    
    Network Timeout

Đây là lỗi **tạm thời (Transient Error)**.

Nếu thử lại sau vài giây:
    
    
    Retry
    
    ↓
    
    Download thành công

Celery sinh ra để xử lý chính xác trường hợp này.

* * *

# 2\. Những lỗi nào nên Retry?

Ví dụ:
    
    
    requests.get(...)

Có thể gặp:

  * Timeout 
  * ConnectionError 
  * DNS lỗi 
  * Server 503 
  * Gateway Timeout 



Đây đều là lỗi nên retry.

* * *

## Không nên Retry

Ví dụ:
    
    
    int("abc")
    
    
    ValueError

Retry:
    
    
    Lần 1
    
    ↓
    
    ValueError
    
    ↓
    
    Retry
    
    ↓
    
    ValueError
    
    ↓
    
    Retry
    
    ↓
    
    ValueError

Không có ý nghĩa.

* * *

# 3\. Retry Flow
    
    
    Task
    
    ↓
    
    Exception
    
    ↓
    
    Retry
    
    ↓
    
    Broker
    
    ↓
    
    Worker
    
    ↓
    
    Task
    
    ↓
    
    SUCCESS

* * *

# 4\. `self.retry()`

Ví dụ:
    
    
    from celery import Celery
    import requests
    
    app = Celery("demo")
    
    
    @app.task(bind=True)
    def download(self, url):
    
        try:
    
            return requests.get(url).text
    
        except requests.RequestException as exc:
    
            raise self.retry(
                exc=exc,
                countdown=10
            )

Giải thích:
    
    
    download()
    
    ↓
    
    Network Error
    
    ↓
    
    Retry sau 10 giây

* * *

# 5\. Tại sao phải `raise self.retry()`?

Sai:
    
    
    self.retry()

Đúng:
    
    
    raise self.retry()

Lý do:

`self.retry()` sẽ ném ra ngoại lệ đặc biệt (`Retry`) để Celery biết:
    
    
    Task chưa thất bại
    
    ↓
    
    Đưa lại vào Queue

* * *

# 6\. `bind=True`

Muốn dùng:
    
    
    self.retry()

Task phải:
    
    
    @app.task(bind=True)

Ví dụ:
    
    
    @app.task(bind=True)
    def download(self, url):
        ...

Nếu không:
    
    
    self

không tồn tại.

* * *

# 7\. `countdown`
    
    
    raise self.retry(
        countdown=30
    )

Luồng:
    
    
    Now
    
    ↓
    
    Retry
    
    ↓
    
    30 giây
    
    ↓
    
    Worker chạy lại

* * *

# 8\. `max_retries`

Ví dụ:
    
    
    @app.task(
        bind=True,
        max_retries=5
    )
    def download(self):
        ...

Celery:
    
    
    Lần 1
    
    ↓
    
    Lần 2
    
    ↓
    
    Lần 3
    
    ↓
    
    Lần 4
    
    ↓
    
    Lần 5
    
    ↓
    
    FAILURE

* * *

# 9\. Retry Count

Trong Task:
    
    
    self.request.retries

Ví dụ:
    
    
    @app.task(bind=True)
    def test(self):
    
        print(
            self.request.retries
        )

Kết quả:
    
    
    0
    
    1
    
    2
    
    3

* * *

# 10\. `autoretry_for`

Thay vì:
    
    
    try:
        ...
    except:
        self.retry()

Ta viết:
    
    
    @app.task(
    
        autoretry_for=(
            requests.ConnectionError,
        ),
    
        retry_kwargs={
            "max_retries":5
        }
    )
    def download(url):
        ...

Celery tự retry.

* * *

# 11\. Retry nhiều Exception
    
    
    @app.task(
    
        autoretry_for=(
    
            requests.Timeout,
    
            requests.ConnectionError,
    
            OSError,
    
        )
    
    )

Celery sẽ retry nếu gặp một trong các ngoại lệ trên.

* * *

# 12\. `retry_backoff`

Đây là tính năng rất quan trọng.

Ví dụ:
    
    
    @app.task(
    
        autoretry_for=(Exception,),
    
        retry_backoff=True
    )

Retry:
    
    
    Lần 1
    
    1 giây
    
    ↓
    
    Lần 2
    
    2 giây
    
    ↓
    
    Lần 3
    
    4 giây
    
    ↓
    
    Lần 4
    
    8 giây
    
    ↓
    
    16
    
    ↓
    
    32

Đây gọi là **Exponential Backoff**.

* * *

# 13\. Vì sao cần Backoff?

Giả sử:

API bị sập.

1000 Worker:
    
    
    Retry
    
    ↓
    
    Retry
    
    ↓
    
    Retry
    
    ↓
    
    Retry

API bị quá tải.

Nếu Backoff:
    
    
    1s
    
    ↓
    
    2s
    
    ↓
    
    4s
    
    ↓
    
    8s

Áp lực lên API giảm đáng kể.

* * *

# 14\. `retry_backoff_max`
    
    
    @app.task(
    
        retry_backoff=True,
    
        retry_backoff_max=300
    )

Tối đa:
    
    
    300 giây

Sau đó không tăng nữa.

* * *

# 15\. `retry_jitter`

Nếu:

100 Worker

đều retry sau:
    
    
    60 giây

thì:
    
    
    60s
    
    ↓
    
    100 Worker cùng chạy

Đây gọi là **Thundering Herd Problem**.

* * *

Celery có:
    
    
    retry_jitter=True

Ví dụ:
    
    
    Worker1
    
    61s
    
    Worker2
    
    57s
    
    Worker3
    
    65s
    
    Worker4
    
    59s

Các Worker được phân tán thời điểm retry.

* * *

# 16\. Retry theo điều kiện

Ví dụ:
    
    
    response = requests.get(url)

Nếu:
    
    
    404

Không nên retry.

* * *

Nếu:
    
    
    503

Nên retry.

Ví dụ:
    
    
    if response.status_code == 503:
    
        raise self.retry(...)

* * *

# 17\. Retry Database

Ví dụ:
    
    
    save_user()

Lỗi:
    
    
    Deadlock

Có thể retry.

* * *

Nhưng:
    
    
    Duplicate Key

Không nên retry.

* * *

# 18\. Retry File Download

Ví dụ:
    
    
    download_file()

Nếu:
    
    
    Network Timeout

Retry.

Nếu:
    
    
    Permission Denied

Không retry.

* * *

# 19\. Retry và Idempotency

Ví dụ:
    
    
    balance += 100

Retry:
    
    
    100
    
    ↓
    
    200
    
    ↓
    
    300

Sai.

* * *

Nên:
    
    
    update_status(order_id)

Retry:
    
    
    SUCCESS
    
    ↓
    
    SUCCESS
    
    ↓
    
    SUCCESS

An toàn.

* * *

# 20\. Dead Letter Queue (DLQ)

Nếu:
    
    
    Retry
    
    ↓
    
    Retry
    
    ↓
    
    Retry
    
    ↓
    
    Retry
    
    ↓
    
    FAILURE

Task có thể chuyển sang:
    
    
    Dead Letter Queue

để:

  * điều tra 
  * chạy lại thủ công 
  * cảnh báo 



Lưu ý: **Celery không có DLQ tích hợp**. Khả năng này thường được cung cấp bởi Broker (đặc biệt là RabbitMQ). Với Redis, bạn cần tự xây dựng cơ chế lưu các task thất bại hoặc sử dụng các công cụ bổ trợ.

* * *

# 21\. Logging Retry

Ví dụ:
    
    
    logger.warning(
    
        "Retry %s",
    
        self.request.retries
    )

Log:
    
    
    Retry 1
    
    Retry 2
    
    Retry 3

Giúp theo dõi nguyên nhân và tần suất retry.

* * *

# 22\. Retry Strategy trong Production

Ví dụ:

Task| Retry  
---|---  
Email| Có  
HTTP API| Có  
Download File| Có  
AI Inference| Có (tùy nguyên nhân lỗi)  
Ghi Database| Có chọn lọc  
Thanh toán| Rất cẩn thận, phải idempotent  
Parse HTML| Thường không  
  
* * *

# 23\. Ví dụ Story Scraper

Task:
    
    
    download_chapter()

Nếu:
    
    
    503

Retry.

Nếu:
    
    
    404

Không retry.

Nếu:
    
    
    DNS Error

Retry.

Nếu:
    
    
    Parser Error

Không retry ngay. Nên ghi log để phân tích hoặc sửa parser.

* * *

# 24\. Retry Workflow
    
    
    download
    
    ↓
    
    Timeout
    
    ↓
    
    Retry
    
    ↓
    
    Download
    
    ↓
    
    Parse
    
    ↓
    
    Save
    
    ↓
    
    Notify

Chỉ:
    
    
    Download

retry.

Không cần chạy lại toàn bộ workflow.

* * *

# 25\. Mẫu Task Production
    
    
    @app.task(
        bind=True,
        autoretry_for=(requests.ConnectionError,),
        retry_backoff=True,
        retry_backoff_max=300,
        retry_jitter=True,
        max_retries=5,
    )
    def download(self, url):
    
        return requests.get(url).text

Đây là một cấu hình rất tốt cho các tác vụ gọi HTTP.

* * *

# 26\. Anti-pattern

## Sai
    
    
    except:
    
        self.retry()

Retry mọi lỗi.

* * *

## Đúng
    
    
    except requests.Timeout:

Retry đúng loại lỗi.

* * *

## Sai
    
    
    max_retries=1000

Có thể gây lãng phí tài nguyên và che giấu lỗi thực sự.

* * *

## Đúng
    
    
    max_retries=3

Hoặc:
    
    
    5

Tùy yêu cầu nghiệp vụ.

* * *

# Tổng kết

Sau buổi 7 bạn đã hiểu:

  * ✅ Retry là gì. 
  * ✅ Khi nào nên retry. 
  * ✅ `self.retry()`. 
  * ✅ `autoretry_for`. 
  * ✅ `countdown`. 
  * ✅ `max_retries`. 
  * ✅ `retry_backoff`. 
  * ✅ Exponential Backoff. 
  * ✅ `retry_jitter`. 
  * ✅ Retry có điều kiện. 
  * ✅ Chiến lược retry trong production. 



* * *

# Bài tập

## Bài 1

Viết Task:
    
    
    download(url)

Yêu cầu:

  * Retry khi gặp `requests.Timeout`. 
  * Tối đa 5 lần. 
  * Backoff theo cấp số nhân. 
  * Có `jitter`. 



* * *

## Bài 2

Thiết kế chiến lược retry cho hệ thống Story Scraper với các Task:

  * `download_book`
  * `download_chapter`
  * `parse_html`
  * `save_database`
  * `download_image`



Xác định:

  * Task nào nên retry? 
  * Retry theo loại lỗi nào? 
  * `max_retries` bao nhiêu? 
  * Có dùng backoff không? Giải thích. 



* * *

## Bài 3

Phân tích đoạn code sau:
    
    
    @app.task(bind=True)
    def charge(self, order_id):
        pay(order_id)

Nếu `pay()` đã trừ tiền nhưng Worker bị crash trước khi ACK:

  * Điều gì có thể xảy ra? 
  * Vì sao đây là bài toán khó? 
  * Cần áp dụng những kỹ thuật nào (ví dụ: idempotency key, transaction, outbox...) để tránh trừ tiền nhiều lần? 



* * *

# Buổi 8 tiếp theo

Chúng ta sẽ học **Celery Canvas Deep Dive** — một trong những tính năng mạnh nhất của Celery:

  * Signature (`s`, `si`) 
  * Chain 
  * Group 
  * Chord 
  * Map 
  * Starmap 
  * Chunks 
  * Workflow phân tán 
  * Orchestration cho các hệ thống crawler, ETL và AI Pipeline. 



Đây là phần giúp bạn xây dựng các quy trình xử lý phức tạp bằng cách kết hợp nhiều task một cách rõ ràng và dễ mở rộng.

