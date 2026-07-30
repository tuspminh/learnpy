# CELERY DEEP DIVE — Buổi 6

# Task Design Pattern Deep Dive

## Thiết kế Celery Task chuyên nghiệp cho Production

> **Mục tiêu**
> 
> Sau buổi này bạn sẽ biết cách thiết kế Celery Task theo chuẩn production:
> 
>   * Task nên lớn hay nhỏ? 
>   * Idempotency là gì? 
>   * Atomic Task là gì? 
>   * Retry-safe Task. 
>   * Transaction với Database. 
>   * Chia nhỏ workflow. 
>   * Các anti-pattern thường gặp. 
> 


* * *

# 1\. Thiết kế Task quan trọng hơn viết Task

Rất nhiều lập trình viên học Celery chỉ biết:
    
    
    @app.task
    def send_email():
        ...

Nhưng trong thực tế, vấn đề không phải là **viết được task** , mà là **thiết kế task đúng**.

Một task được thiết kế kém có thể gây ra:

  * gửi email trùng lặp 
  * thanh toán hai lần 
  * ghi dữ liệu sai 
  * crawl trùng dữ liệu 
  * retry làm hỏng database 
  * khó mở rộng 



* * *

# 2\. Một Task tốt nên có những đặc điểm gì?

Một Celery Task tốt thường có các tính chất:

  * Đơn giản (Simple) 
  * Nhỏ (Small) 
  * Độc lập (Independent) 
  * Có thể Retry (Retry-safe) 
  * Có tính Idempotent 
  * Dễ mở rộng (Composable) 
  * Không giữ trạng thái (Stateless) 



* * *

# 3\. Anti-pattern: Một Task làm tất cả

Ví dụ:
    
    
    @app.task
    def register_user(user):
        save_user(user)
        send_email(user)
        resize_avatar(user)
        create_statistics(user)
        notify_admin(user)

Nhìn có vẻ tiện.

Nhưng thực tế:
    
    
    register_user()
    
    │
    
    ├── save
    
    ├── email
    
    ├── avatar
    
    ├── statistics
    
    └── notify

Nếu:
    
    
    send_email()

bị lỗi:

Task sẽ retry.

Kết quả:
    
    
    save_user()
    
    ↓
    
    retry
    
    ↓
    
    save_user()
    
    ↓
    
    retry
    
    ↓
    
    save_user()

Người dùng có thể bị tạo nhiều lần.

* * *

# 4\. Thiết kế đúng

Thay vì:
    
    
    Một Task lớn

Ta chia:
    
    
    Create User
    
    ↓
    
    Send Email
    
    ↓
    
    Resize Avatar
    
    ↓
    
    Statistics
    
    ↓
    
    Notify

Tương ứng:
    
    
    create_user.delay()
    
    send_email.delay()
    
    resize_avatar.delay()
    
    create_statistics.delay()
    
    notify_admin.delay()

Ưu điểm:

  * Retry từng bước. 
  * Dễ debug. 
  * Dễ scale. 
  * Dễ monitor. 



* * *

# 5\. Quy tắc "Task nên làm một việc"

Một Task tốt chỉ nên làm **một trách nhiệm**.

Ví dụ:

❌ Không nên:
    
    
    process_order()

bên trong:

  * lưu DB 
  * gửi email 
  * tạo PDF 
  * gửi SMS 



* * *

Nên:
    
    
    save_order
    
    ↓
    
    send_email
    
    ↓
    
    generate_invoice
    
    ↓
    
    send_sms

Đây cũng chính là nguyên tắc **Single Responsibility Principle (SRP)** trong thiết kế phần mềm.

* * *

# 6\. Idempotency là gì?

Đây là khái niệm cực kỳ quan trọng trong Celery.

## Định nghĩa

Một thao tác **Idempotent** là thao tác:

> Thực hiện nhiều lần nhưng kết quả cuối cùng không thay đổi.

Ví dụ:
    
    
    user.status = "ACTIVE"

Chạy:

1 lần

hay

100 lần

đều:
    
    
    ACTIVE

* * *

Ví dụ KHÔNG Idempotent:
    
    
    user.balance += 100

Chạy:
    
    
    100
    
    ↓
    
    200
    
    ↓
    
    300
    
    ↓
    
    400

Retry sẽ gây lỗi nghiêm trọng.

* * *

# 7\. Vì sao Celery cần Idempotency?

Giả sử:

Worker:
    
    
    Task
    
    ↓
    
    Execute
    
    ↓
    
    Crash

Broker:
    
    
    Task chưa ACK
    
    ↓
    
    Retry

Nếu Task không Idempotent:
    
    
    Thanh toán
    
    ↓
    
    Thanh toán lại

Khách bị trừ tiền hai lần.

* * *

# 8\. Ví dụ Idempotent trong Story Scraper

Sai:
    
    
    chapter.views += 1

Retry:
    
    
    100
    
    ↓
    
    101
    
    ↓
    
    102
    
    ↓
    
    103

* * *

Đúng:
    
    
    chapter.content = html

Retry:
    
    
    html
    
    ↓
    
    html
    
    ↓
    
    html

Không có vấn đề.

* * *

# 9\. Atomic Task là gì?

Atomic nghĩa là:

> Thành công hoàn toàn hoặc thất bại hoàn toàn.

Ví dụ:
    
    
    @app.task
    def transfer_money():
        deduct()
        add()

Nếu:
    
    
    deduct()
    
    ↓
    
    Crash

Tiền biến mất.

* * *

Đúng:
    
    
    BEGIN
    
    ↓
    
    deduct
    
    ↓
    
    add
    
    ↓
    
    COMMIT

Hoặc:
    
    
    ROLLBACK

* * *

# 10\. Retry-safe Task

Ví dụ:
    
    
    @app.task(bind=True)
    def download(url):
        ...

Nếu retry:
    
    
    Download
    
    ↓
    
    Network Error
    
    ↓
    
    Retry
    
    ↓
    
    Download

Không sao.

* * *

Nhưng:
    
    
    @app.task
    def create_invoice():
        insert_invoice()

Retry:
    
    
    Invoice 1
    
    ↓
    
    Retry
    
    ↓
    
    Invoice 2

Hai hóa đơn.

* * *

Đúng:
    
    
    if invoice_exists():
        return

* * *

# 11\. Không truyền Object vào Task

Sai:
    
    
    user = User(...)
    
    send_email.delay(user)

Vì:

  * Object khó serialize. 
  * Có thể lỗi pickle/JSON. 
  * Dữ liệu có thể đã cũ khi Worker chạy. 



* * *

Đúng:
    
    
    send_email.delay(user.id)

Worker:
    
    
    user = get_user(user_id)

Luôn lấy dữ liệu mới nhất.

* * *

# 12\. Không truyền dữ liệu lớn

Sai:
    
    
    process.delay(big_image_bytes)

Broker phải lưu:
    
    
    20 MB
    
    ↓
    
    Redis

Rất tốn bộ nhớ và băng thông.

* * *

Đúng:
    
    
    process.delay(image_path)

Hoặc:
    
    
    process.delay(file_id)

Worker tự đọc file.

* * *

# 13\. Stateless Task

Task không nên phụ thuộc vào biến toàn cục.

Sai:
    
    
    cache = {}
    
    @app.task
    def process():
        cache["x"] = 10

Worker khác:
    
    
    Không có cache.

* * *

Đúng:

Task luôn lấy dữ liệu từ:

  * Database 
  * Redis 
  * API 
  * File 



* * *

# 14\. Transaction với Database

Sai:
    
    
    save_order()
    
    send_email()
    
    commit()

Nếu:
    
    
    send_email
    
    ↓
    
    Crash

Database chưa commit.

* * *

Đúng:
    
    
    BEGIN
    
    ↓
    
    Save
    
    ↓
    
    COMMIT
    
    ↓
    
    Send Email

Hoặc:
    
    
    COMMIT
    
    ↓
    
    Celery Task

Đây là mô hình **Transactional Outbox** , sẽ học sâu ở các buổi sau.

* * *

# 15\. Thiết kế Workflow

Sai:
    
    
    @app.task
    def crawl():
        crawl()
        parse()
        save()
        notify()

Đúng:
    
    
    crawl
    
    ↓
    
    parse
    
    ↓
    
    save
    
    ↓
    
    notify

Mỗi bước là một Task.

Sau này có thể dùng **Celery Canvas** để nối các bước.

* * *

# 16\. Logging

Task nên log đầy đủ.

Ví dụ:
    
    
    logger.info(
        "Download chapter %s",
        chapter_id
    )

Không nên:
    
    
    print("Done")

Vì:

  * khó tìm kiếm 
  * không có mức độ (INFO, WARNING, ERROR) 
  * không tích hợp với hệ thống giám sát. 



* * *

# 17\. Timeout

Task không nên chạy vô hạn.

Ví dụ:
    
    
    download()

Nếu server treo:
    
    
    3 ngày

Worker bị chiếm mãi.

Nên cấu hình:
    
    
    @app.task(
        soft_time_limit=60,
        time_limit=120
    )

  * `soft_time_limit`: Celery gửi tín hiệu để task có cơ hội dọn dẹp tài nguyên. 
  * `time_limit`: Celery buộc dừng task nếu vẫn chưa kết thúc. 



* * *

# 18\. Đặt tên Task

Sai:
    
    
    @app.task
    def run():

Đúng:
    
    
    @app.task(
        name="crawler.download_chapter"
    )

Tên rõ ràng giúp:

  * debug 
  * monitor 
  * thống kê 



* * *

# 19\. Thiết kế cho Story Scraper

Thay vì:
    
    
    crawl_all

Nên:
    
    
    download_book
    
    ↓
    
    download_chapter
    
    ↓
    
    parse_html
    
    ↓
    
    save_database
    
    ↓
    
    download_images
    
    ↓
    
    generate_index

Mỗi bước có thể:

  * retry riêng 
  * scale riêng 
  * monitor riêng 



* * *

# 20\. Kiến trúc Production
    
    
                    API
    
                     │
    
                     ▼
    
             Create Crawl Job
    
                     │
    
                     ▼
    
              Redis Broker
    
                     │
    
    ─────────────────┼──────────────────
    
            download_worker
    
            parse_worker
    
            image_worker
    
            notify_worker
    
    ─────────────────┼──────────────────
    
                     │
    
                     ▼
    
                PostgreSQL

Đây là kiến trúc rất phổ biến trong các hệ thống crawler, xử lý ảnh, AI pipeline và ETL.

* * *

# 21\. Checklist thiết kế Task

Trước khi tạo một Task, hãy tự hỏi:

  * Task chỉ làm **một việc**? 
  * Có thể retry an toàn? 
  * Có idempotent không? 
  * Có truyền object lớn không? 
  * Có cần transaction không? 
  * Có log đầy đủ không? 
  * Có timeout không? 
  * Có tên rõ ràng không? 



Nếu trả lời "Có" cho các câu hỏi phù hợp, Task của bạn đã gần đạt chuẩn production.

* * *

# Bài tập

## Bài 1

Cho Task sau:
    
    
    @app.task
    def process_order(order):
        save(order)
        send_email(order)
        print_invoice(order)
        update_statistics(order)

Hãy chia lại thành nhiều Task nhỏ theo nguyên tắc **Single Responsibility** và giải thích lợi ích.

* * *

## Bài 2

Trong hệ thống Story Scraper, hãy thiết kế các Task cho quy trình:

  1. Crawl danh sách chương. 
  2. Tải HTML từng chương. 
  3. Parse nội dung. 
  4. Lưu cơ sở dữ liệu. 
  5. Tải ảnh minh họa. 
  6. Gửi thông báo khi hoàn tất. 



Vẽ sơ đồ workflow và xác định Task nào cần có tính **idempotent**.

* * *

## Bài 3

Xem xét Task sau:
    
    
    @app.task
    def increase_view(chapter_id):
        chapter = get_chapter(chapter_id)
        chapter.views += 1
        save(chapter)

Hãy phân tích:

  * Vì sao Task này **không idempotent**? 
  * Điều gì xảy ra nếu Worker bị crash và Celery retry? 
  * Đề xuất ít nhất **hai cách** để thiết kế lại tùy theo yêu cầu nghiệp vụ (ví dụ: đếm lượt xem chính xác hoặc chỉ đánh dấu đã xem). 



* * *

# Buổi 7 tiếp theo

Chúng ta sẽ học **Retry & Error Handling Deep Dive**, bao gồm:

  * `self.retry()`
  * `autoretry_for`
  * `max_retries`
  * `retry_backoff`
  * Exponential Backoff 
  * Retry theo từng loại Exception 
  * Dead Letter Queue (DLQ) 
  * Thiết kế chiến lược retry trong production 
  * Các lỗi phổ biến khi retry với Redis và RabbitMQ 



Đây là một trong những chủ đề quan trọng nhất để xây dựng hệ thống Celery có độ tin cậy cao.

