# CELERY DEEP DIVE — Buổi 8

# Celery Canvas Deep Dive (Phần 1)

## Signature, Chain, Group và tư duy xây dựng Workflow

> **Mục tiêu**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu Celery Canvas là gì. 
>   * Phân biệt `delay()`, `apply_async()`, `signature()`. 
>   * Hiểu `s()` và `si()`. 
>   * Thành thạo `chain()`. 
>   * Thành thạo `group()`. 
>   * Biết khi nào dùng Chain, khi nào dùng Group. 
>   * Thiết kế workflow cho hệ thống Story Scraper. 
> 


* * *

# 1\. Canvas là gì?

Cho đến bây giờ chúng ta chỉ chạy **một task** :
    
    
    download.delay(url)

Nhưng thực tế chúng ta cần:
    
    
    Download
    
    ↓
    
    Parse
    
    ↓
    
    Save Database
    
    ↓
    
    Notify

Hoặc:
    
    
    Download 1000 chapters
    
    ↓
    
    100 Worker
    
    ↓
    
    Parse song song
    
    ↓
    
    Lưu Database

Đó là lúc **Canvas** xuất hiện.

> **Canvas là hệ thống orchestration (điều phối) workflow của Celery.**

* * *

# 2\. Canvas gồm những gì?

Canvas cung cấp các primitive:
    
    
    Signature
    
    Chain
    
    Group
    
    Chord
    
    Map
    
    Starmap
    
    Chunks

Trong buổi này chúng ta học:

  * Signature 
  * Chain 
  * Group 



Buổi sau sẽ học:

  * Chord 
  * Map 
  * Starmap 
  * Chunks 



* * *

# 3\. Signature là gì?

Ví dụ:
    
    
    add.delay(10,20)

Task chạy ngay.

Nếu muốn **mô tả một task nhưng chưa chạy** :
    
    
    sig = add.s(10,20)

Lúc này:
    
    
    Task Definition
    
    ↓
    
    Chưa chạy

* * *

## Kiểm tra
    
    
    print(sig)

Ví dụ:
    
    
    app.tasks.add(10, 20)

Đây chỉ là mô tả.

* * *

# 4\. Signature hoạt động như thế nào?

Ví dụ:
    
    
    sig = add.s(10,20)

Bộ nhớ:
    
    
    Signature
    
    Task Name
    
    ↓
    
    app.tasks.add
    
    Args
    
    ↓
    
    10
    
    20

Chưa gửi Broker.

* * *

# 5\. Thực thi Signature
    
    
    sig.delay()

Hoặc:
    
    
    sig.apply_async()

Lúc này mới:
    
    
    Broker
    
    ↓
    
    Worker

* * *

# 6\. Tại sao Signature quan trọng?

Giả sử:
    
    
    Download
    
    ↓
    
    Parse
    
    ↓
    
    Save

Nếu không có Signature:

Task phải chạy ngay.

Không thể xây dựng workflow.

* * *

# 7\. `s()` và `signature()`

Hai cách viết:
    
    
    from celery import signature
    
    sig = signature(
        "app.tasks.add",
        args=(10,20)
    )

hoặc:
    
    
    sig = add.s(10,20)

Cách thứ hai phổ biến hơn vì ngắn gọn và dễ đọc.

* * *

# 8\. Immutable Signature (`si`)

Ví dụ:
    
    
    sig = add.si(10,20)

Khác:
    
    
    add.s()

Điểm khác biệt sẽ thấy rõ trong `chain()`.

* * *

# 9\. Chain là gì?

Ví dụ:
    
    
    Download
    
    ↓
    
    Parse
    
    ↓
    
    Save
    
    ↓
    
    Notify

Đây gọi là:
    
    
    Workflow tuần tự

Celery:
    
    
    from celery import chain

* * *

# 10\. Ví dụ đầu tiên

Task:
    
    
    @app.task
    def add(x,y):
        return x+y
    
    
    @app.task
    def double(x):
        return x*2

Chain:
    
    
    workflow = chain(
    
        add.s(2,3),
    
        double.s()
    )

* * *

Luồng:
    
    
    add
    
    ↓
    
    5
    
    ↓
    
    double
    
    ↓
    
    10

* * *

Chạy:
    
    
    workflow.delay()

Kết quả:
    
    
    10

* * *

# 11\. Giá trị truyền trong Chain

Đây là điểm cực kỳ quan trọng.

Ví dụ:
    
    
    chain(
    
        add.s(2,3),
    
        double.s()
    )

Celery thực hiện:
    
    
    x = add(2,3)
    
    double(x)

Tức là:
    
    
    5
    
    ↓
    
    double(5)

* * *

# 12\. Chain nhiều Task
    
    
    chain(
    
        download.s(),
    
        parse.s(),
    
        save.s(),
    
        notify.s()
    
    )

Luồng:
    
    
    Download
    
    ↓
    
    HTML
    
    ↓
    
    Parse
    
    ↓
    
    Data
    
    ↓
    
    Save
    
    ↓
    
    Notify

Đây chính là cách xây dựng **pipeline**.

* * *

# 13\. Immutable Signature trong Chain

Ví dụ:
    
    
    chain(
    
        add.s(2,3),
    
        hello.si()
    
    )

`hello()`:
    
    
    @app.task
    def hello():
        print("Hello")

Nếu dùng:
    
    
    hello.s()

Celery sẽ truyền:
    
    
    5

vào `hello()`.

Nếu dùng:
    
    
    hello.si()

Celery:
    
    
    Không truyền gì cả.

* * *

# 14\. Khi nào dùng `si()`?

Ví dụ:
    
    
    Download
    
    ↓
    
    Notify Admin

`notify_admin()`:
    
    
    notify_admin()

Không cần kết quả download.

Ta dùng:
    
    
    notify_admin.si()

* * *

# 15\. Group là gì?

Chain:
    
    
    A
    
    ↓
    
    B
    
    ↓
    
    C

Nhưng:
    
    
    Task1
    
    Task2
    
    Task3
    
    Task4

độc lập nhau.

Ta muốn:
    
    
    Chạy cùng lúc.

Đó là:
    
    
    Group

* * *

# 16\. Ví dụ Group
    
    
    from celery import group
    
    
    jobs = group(
    
        add.s(1,2),
    
        add.s(3,4),
    
        add.s(5,6)
    
    )

* * *

Thực thi:
    
    
    result = jobs.delay()

Worker:
    
    
    Worker1
    
    1+2
    
    ↓
    
    3
    
    ----------------
    
    Worker2
    
    3+4
    
    ↓
    
    7
    
    ----------------
    
    Worker3
    
    5+6
    
    ↓
    
    11

* * *

# 17\. GroupResult

Group trả về:
    
    
    GroupResult

Không phải:
    
    
    AsyncResult

Ví dụ:
    
    
    result.get()

Kết quả:
    
    
    [
        3,
        7,
        11
    ]

* * *

# 18\. Group trong Story Scraper

Ví dụ:
    
    
    Book
    
    ↓
    
    1000 chapters

Không nên:
    
    
    download
    
    ↓
    
    download
    
    ↓
    
    download

Mà:
    
    
    Group
    
    ↓
    
    Chapter1
    
    Chapter2
    
    Chapter3
    
    ...
    
    Chapter1000

100 Worker có thể xử lý đồng thời.

* * *

# 19\. Chain hay Group?

## Chain
    
    
    Download
    
    ↓
    
    Parse
    
    ↓
    
    Save

Có phụ thuộc dữ liệu.

* * *

## Group
    
    
    Download Chapter1
    
    Download Chapter2
    
    Download Chapter3

Không phụ thuộc nhau.

* * *

# 20\. Kết hợp Chain + Group

Ví dụ:
    
    
    Download Book
    
    ↓
    
    Group
    
    ↓
    
    Chapter1
    
    Chapter2
    
    Chapter3
    
    ↓
    
    Save

Hay trực quan hơn:
    
    
                 Download Book
                        │
                        ▼
                  Lấy danh sách chương
                        │
            ┌───────────┼───────────┐
            ▼           ▼           ▼
     Download C1   Download C2  Download C3
            │           │           │
            ▼           ▼           ▼
      Parse C1     Parse C2    Parse C3
            └───────────┼───────────┘
                        ▼
                  Lưu dữ liệu

Đây là nền tảng cho **Chord** , sẽ học ở buổi sau.

* * *

# 21\. Signature có thể tái sử dụng

Ví dụ:
    
    
    download_sig = download.s(url)

Có thể dùng:
    
    
    chain(
        download_sig,
        parse.s()
    )

Hoặc:
    
    
    group(
        download_sig,
        download.s(url2),
        download.s(url3)
    )

Workflow trở nên linh hoạt hơn.

* * *

# 22\. Anti-pattern

## Sai
    
    
    @app.task
    def crawl():
    
        download()
    
        parse()
    
        save()
    
        notify()

Task quá lớn, khó retry và khó mở rộng.

* * *

## Đúng
    
    
    chain(
    
        download.s(),
    
        parse.s(),
    
        save.s(),
    
        notify.s()
    
    )

* * *

## Sai
    
    
    for chapter in chapters:
    
        download.delay(chapter)

Khó theo dõi toàn bộ công việc như một workflow.

* * *

## Đúng
    
    
    group(
        download.s(c)
    
        for c in chapters
    )

Celery quản lý cả nhóm task.

* * *

# 23\. Kiến trúc Story Scraper
    
    
    API
    
    ↓
    
    Create Job
    
    ↓
    
    Download Book
    
    ↓
    
    Group
    
    ↓
    
    Download Chapters
    
    ↓
    
    Group
    
    ↓
    
    Parse Chapters
    
    ↓
    
    Group
    
    ↓
    
    Save Database
    
    ↓
    
    Notify

Đây là kiến trúc rất phổ biến trong:

  * Web Crawler 
  * ETL Pipeline 
  * AI Pipeline 
  * Video Processing 



* * *

# Tổng kết

Sau buổi 8 bạn đã hiểu:

  * ✅ Canvas là gì. 
  * ✅ Signature (`s`). 
  * ✅ Immutable Signature (`si`). 
  * ✅ `chain()`. 
  * ✅ `group()`. 
  * ✅ `AsyncResult` và `GroupResult`. 
  * ✅ Khi nào dùng Chain. 
  * ✅ Khi nào dùng Group. 
  * ✅ Thiết kế workflow cơ bản bằng Celery Canvas. 



* * *

# Bài tập

## Bài 1

Viết ba Task:
    
    
    download(url)
    
    parse(html)
    
    save(data)

Ghép chúng thành một `chain()` và giải thích dữ liệu được truyền giữa các task.

* * *

## Bài 2

Giả sử có danh sách:
    
    
    chapters = [
        "chapter1",
        "chapter2",
        "chapter3",
        "chapter4",
    ]

Tạo một `group()` để tải đồng thời tất cả các chương.

* * *

## Bài 3

Thiết kế workflow cho dự án **Story Scraper** :

  1. Tải thông tin sách. 
  2. Lấy danh sách chương. 
  3. Tải song song tất cả chương. 
  4. Parse song song. 
  5. Lưu cơ sở dữ liệu. 
  6. Gửi thông báo hoàn thành. 



Xác định rõ bước nào dùng **Chain** , bước nào dùng **Group** , và giải thích lý do.

* * *

# Buổi 9 tiếp theo

Chúng ta sẽ học **Celery Canvas Deep Dive (Phần 2)** :

  * **Chord** (đồng bộ hóa nhiều task song song) 
  * **Map**
  * **Starmap**
  * **Chunks**
  * Workflow DAG phức tạp 
  * Fan-out / Fan-in Pattern 
  * Thiết kế pipeline cho AI, ETL và Story Scraper quy mô lớn. 



Đây là phần đưa bạn từ việc chạy nhiều task độc lập sang xây dựng các **workflow phân tán hoàn chỉnh**.

