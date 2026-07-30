# Iterator Deep Dive

# Phần IV — Iterator nâng cao

# Buổi 19: Infinite Iterator Deep Dive

Đây là một chủ đề rất quan trọng vì rất nhiều hệ thống thực tế **không có khái niệm "kết thúc dữ liệu"**.

Ví dụ:

  * Crawler chạy 24/7 
  * Log Server 
  * Kafka Consumer 
  * RabbitMQ Consumer 
  * Redis Stream 
  * WebSocket 
  * MQTT 
  * Cảm biến IoT 
  * AI Streaming 
  * Terminal Input 



Tất cả đều có thể được xem là **Infinite Iterator**.

Sau buổi này, bạn sẽ biết cách thiết kế các Iterator vô hạn một cách an toàn và hiệu quả.

* * *

# Roadmap

## Phần IV

  * ✅ Buổi 17 — itertools 
  * ✅ Buổi 18 — Lazy Evaluation 
  * ✅ **Buổi 19 — Infinite Iterator**
  * Buổi 20 — Async Iterator 
  * Buổi 21 — Performance 
  * Buổi 22 — Thiết kế thư viện sử dụng Iterator 
  * Buổi 23 — Dự án thực tế 



* * *

# 1\. Infinite Iterator là gì?

Iterator bình thường
    
    
    1
    2
    3
    4
    5
    
    ↓
    
    StopIteration

Infinite Iterator
    
    
    1
    2
    3
    4
    5
    6
    7
    8
    9
    ...
    
    Không bao giờ StopIteration

* * *

# Ví dụ đơn giản nhất
    
    
    def forever():
        i = 1
    
        while True:
            yield i
            i += 1

Sử dụng
    
    
    numbers = forever()
    
    print(next(numbers))
    print(next(numbers))
    print(next(numbers))

↓
    
    
    1
    2
    3

Generator này sẽ **không bao giờ kết thúc**.

* * *

# Vì sao lại cần Iterator vô hạn?

Ví dụ

Máy chủ Web
    
    
    Request
    
    ↓
    
    Response
    
    ↓
    
    Request
    
    ↓
    
    Response

Server không biết

khi nào request cuối cùng xuất hiện.

* * *

Ví dụ

Log
    
    
    10:00
    
    ↓
    
    10:01
    
    ↓
    
    10:02
    
    ↓
    
    ...

Log không có "dòng cuối".

* * *

# 2\. itertools.count()

Đây là Infinite Iterator có sẵn.
    
    
    from itertools import count
    
    counter = count()
    
    for _ in range(5):
        print(next(counter))

↓
    
    
    0
    1
    2
    3
    4

* * *

Có bước nhảy
    
    
    counter = count(100, 10)
    
    for _ in range(5):
        print(next(counter))

↓
    
    
    100
    110
    120
    130
    140

* * *

Ứng dụng

Sinh ID
    
    
    from itertools import count
    
    ids = count(1)
    
    def create_user(name):
    
        return {
            "id": next(ids),
            "name": name
        }

* * *

# 3\. itertools.cycle()
    
    
    from itertools import cycle
    
    colors = cycle([
        "red",
        "green",
        "blue"
    ])

↓
    
    
    red
    green
    blue
    red
    green
    blue
    ...

* * *

Ứng dụng

Round Robin
    
    
    Worker A
    
    ↓
    
    Worker B
    
    ↓
    
    Worker C
    
    ↓
    
    Worker A

* * *

Ví dụ
    
    
    workers = cycle([
        "Crawler1",
        "Crawler2",
        "Crawler3"
    ])
    
    urls = [
        "page1",
        "page2",
        "page3",
        "page4"
    ]
    
    for url in urls:
        print(next(workers), url)

↓
    
    
    Crawler1 page1
    Crawler2 page2
    Crawler3 page3
    Crawler1 page4

* * *

# 4\. itertools.repeat()
    
    
    from itertools import repeat
    
    values = repeat("Hello")

↓
    
    
    Hello
    Hello
    Hello
    ...

Có thể giới hạn
    
    
    repeat("Python", 5)

* * *

Ứng dụng

Tạo dữ liệu mặc định
    
    
    names = [
        "A",
        "B",
        "C"
    ]
    
    scores = repeat(0)
    
    for item in zip(names, scores):
        print(item)

↓
    
    
    ('A',0)
    
    ('B',0)
    
    ('C',0)

* * *

# 5\. Fibonacci vô hạn
    
    
    def fibonacci():
    
        a = 0
        b = 1
    
        while True:
            yield a
    
            a, b = b, a + b

Sử dụng
    
    
    fib = fibonacci()
    
    for _ in range(10):
        print(next(fib))

↓
    
    
    0
    1
    1
    2
    3
    5
    8
    13
    21
    34

* * *

# 6\. Prime Generator
    
    
    def primes():
    
        n = 2
    
        while True:
    
            is_prime = True
    
            for i in range(2, int(n ** 0.5) + 1):
    
                if n % i == 0:
                    is_prime = False
                    break
    
            if is_prime:
                yield n
    
            n += 1

↓
    
    
    2
    3
    5
    7
    11
    13
    17
    ...

* * *

# 7\. Random Stream
    
    
    import random
    
    def random_numbers():
    
        while True:
    
            yield random.randint(1,100)

↓
    
    
    17
    81
    44
    92
    ...

* * *

Ứng dụng

Simulation

Testing

Game

* * *

# 8\. Sensor Stream
    
    
    import random
    
    def temperature_sensor():
    
        while True:
    
            yield round(
                random.uniform(
                    25,
                    35
                ),
                1
            )

↓
    
    
    28.5
    
    29.0
    
    31.2
    
    ...

Đây là mô hình rất gần với dữ liệu IoT.

* * *

# 9\. Event Stream
    
    
    def event_stream():
    
        event_id = 1
    
        while True:
    
            yield {
                "id": event_id,
                "type": "CLICK"
            }
    
            event_id += 1

↓
    
    
    Event1
    
    Event2
    
    Event3

* * *

# 10\. Infinite File Tail

Ý tưởng giống
    
    
    tail -f app.log

Mô phỏng
    
    
    def tail(lines):
    
        index = 0
    
        while True:
    
            if index < len(lines):
    
                yield lines[index]
    
                index += 1

Trong thực tế

↓

File sẽ liên tục có dòng mới.

* * *

# 11\. Infinite Web Crawler
    
    
    def crawler():
    
        page = 1
    
        while True:
    
            yield f"https://site/page/{page}"
    
            page += 1

Không bao giờ hết URL.

* * *

# 12\. Dừng Infinite Iterator

Đây là điều quan trọng nhất.

Không bao giờ
    
    
    for x in forever():
        print(x)

Nếu không có điều kiện dừng.

* * *

## islice()
    
    
    from itertools import islice
    
    for x in islice(
        forever(),
        10
    ):
        print(x)

↓

10 số đầu.

* * *

## break
    
    
    for x in forever():
    
        if x > 20:
            break
    
        print(x)

* * *

## takewhile()
    
    
    from itertools import takewhile
    
    numbers = takewhile(
        lambda x: x < 10,
        forever()
    )
    
    for x in numbers:
        print(x)

↓
    
    
    1
    2
    3
    ...
    9

`takewhile()` sẽ dừng khi điều kiện trả về `False`.

* * *

## dropwhile()

Ngược lại.
    
    
    from itertools import dropwhile
    
    numbers = dropwhile(
        lambda x: x < 5,
        forever()
    )
    
    for x in numbers:
    
        if x > 10:
            break
    
        print(x)

↓
    
    
    5
    6
    7
    8
    9
    10

* * *

# 13\. Infinite Pipeline
    
    
    numbers = forever()
    
    evens = (
        x
        for x in numbers
        if x % 2 == 0
    )
    
    squares = (
        x*x
        for x in evens
    )

Không có điểm kết thúc.

↓

Chỉ
    
    
    next(squares)

↓

Sinh
    
    
    4
    
    16
    
    36
    ...

* * *

# 14\. Infinite Queue
    
    
    from collections import deque
    
    queue = deque()
    
    def consume():
    
        while True:
    
            if queue:
    
                yield queue.popleft()

Ý tưởng này gần giống Consumer trong hệ thống hàng đợi.

* * *

# 15\. Producer–Consumer
    
    
    Producer
    
    ↓
    
    Queue
    
    ↓
    
    Consumer
    
    ↓
    
    Database

Consumer có thể là Infinite Iterator.

* * *

# 16\. Ứng dụng trong crawler

Bạn đang xây dựng một hệ thống crawler truyện.

Có thể thiết kế như sau:
    
    
    def url_generator():
    
        page = 1
    
        while True:
    
            yield f"https://site/page/{page}"
    
            page += 1

↓
    
    
    def downloader(urls):
    
        for url in urls:
    
            yield download(url)

↓
    
    
    def parser(htmls):
    
        for html in htmls:
    
            yield parse(html)

↓
    
    
    def saver(items):
    
        for item in items:
    
            save(item)

Pipeline:
    
    
    Infinite URL Generator
              │
              ▼
    Downloader
              │
              ▼
    Parser
              │
              ▼
    Repository

Bạn có thể dừng pipeline bất kỳ lúc nào bằng:

  * `break`
  * số lượng bản ghi 
  * thời gian chạy 
  * tín hiệu từ người dùng 



* * *

# 17\. Những sai lầm phổ biến

## Sai lầm 1
    
    
    list(forever())

↓

❌ Chương trình sẽ không bao giờ kết thúc và có thể hết bộ nhớ.

* * *

## Sai lầm 2
    
    
    sorted(forever())

↓

❌ `sorted()` cần toàn bộ dữ liệu trước khi sắp xếp.

* * *

## Sai lầm 3
    
    
    sum(forever())

↓

❌ Không bao giờ trả kết quả.

* * *

## Sai lầm 4

Không đặt điều kiện dừng.

Luôn tự hỏi:

> "Infinite Iterator này sẽ kết thúc bằng cách nào?"

* * *

# So sánh Iterator hữu hạn và vô hạn

Đặc điểm| Iterator hữu hạn| Infinite Iterator  
---|---|---  
StopIteration| Có| Không (trừ khi chủ động dừng)  
Kích thước| Biết trước hoặc hữu hạn| Không xác định  
Dùng `list()`| Thường được| Không nên  
Dùng `sum()`| Được| Không nên  
Dùng `islice()`| Có thể| Rất nên  
Ứng dụng| File, List, DB Query| Stream, Queue, Crawler, Sensor  
  
* * *

# Tổng kết buổi 19

Bạn cần nhớ:

  1. Infinite Iterator là Iterator không tự phát sinh `StopIteration`. 
  2. `itertools.count()`, `cycle()`, `repeat()` là các Infinite Iterator phổ biến. 
  3. Có thể tự xây dựng Infinite Iterator bằng `while True`. 
  4. Các luồng dữ liệu như cảm biến, log, queue, WebSocket hay crawler đều có thể mô hình hóa bằng Infinite Iterator. 
  5. Luôn cần một **chiến lược dừng** (`break`, `islice()`, `takewhile()`, giới hạn thời gian hoặc số lượng dữ liệu). 
  6. Không chuyển Infinite Iterator sang `list()`, `sorted()` hay `sum()`. 
  7. Infinite Iterator kết hợp rất tốt với Generator và Lazy Evaluation để tạo các pipeline xử lý dữ liệu liên tục. 



* * *

# Bài tập

## Bài 1

Viết Infinite Iterator sinh các số chính phương:
    
    
    1
    4
    9
    16
    25
    ...

Sau đó dùng `islice()` để lấy 20 số đầu tiên.

* * *

## Bài 2

Viết Infinite Iterator sinh URL crawler:
    
    
    https://example.com/page/1
    https://example.com/page/2
    https://example.com/page/3
    ...

Sau đó:

  * dùng `takewhile()` để chỉ lấy các trang có số thứ tự nhỏ hơn 50; 
  * hoặc dùng `islice()` để lấy đúng 50 URL đầu tiên. 



* * *

## Bài 3

Xây dựng mô phỏng một hệ thống Producer–Consumer:

  * `producer()` là Infinite Generator sinh các "task". 
  * `consumer()` nhận từng task và xử lý ngay. 
  * Dùng `itertools.islice()` để mô phỏng việc xử lý 100 task đầu tiên. 



Đây là mô hình nền tảng của nhiều hệ thống xử lý hàng đợi như RabbitMQ, Kafka hay các crawler chạy liên tục.

* * *

Ở **Buổi 20** , chúng ta sẽ học **Async Iterator** (`__aiter__`, `__anext__`, `async for`, Async Generator). Đây là bước chuyển từ Iterator đồng bộ sang xử lý dữ liệu bất đồng bộ (streaming), rất quan trọng khi làm việc với `aiohttp`, WebSocket, FastAPI và các crawler bất đồng bộ.

