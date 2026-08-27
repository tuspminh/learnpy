# Buổi 4 — Job Arguments & Serialization trong RQ

Hôm nay chúng ta đi sâu vào một vấn đề **rất quan trọng khi dùng RQ thực tế**:

> Khi `queue.enqueue()` một function, RQ làm thế nào để đưa function và arguments vào Redis để Worker ở process khác có thể lấy ra và chạy?

Mental model:

```text
Producer Process
      │
      │ enqueue(function, args)
      ▼
   Serialize
      │
      ▼
     Redis
      │
      │ deserialize
      ▼
   RQ Worker
      │
      ▼
   function(args)
```

---

# 1. Tại sao cần Serialization?

Hãy tưởng tượng Producer và Worker là **hai process hoàn toàn khác nhau**:

```text
Process A                         Process B

Python App                        RQ Worker
    │                                 │
    │                                 │
    └────────── Redis ────────────────┘
```

Process A có object:

```python
user = {
    "id": 100,
    "name": "An",
}
```

Process B không thể trực tiếp lấy object Python đang nằm trong RAM của Process A.

Cần biến object thành dữ liệu có thể lưu/truyền:

```text
Python Object
     │
     ▼
Serialization
     │
     ▼
Redis
     │
     ▼
Deserialization
     │
     ▼
Python Object
```

RQ mặc định sử dụng **pickle** cho việc này.

---

# 2. Arguments đơn giản

Function:

```python
def add(a, b):
    return a + b
```

Enqueue:

```python
job = queue.enqueue(
    add,
    10,
    20,
)
```

Arguments:

```text
args = (10, 20)
```

Worker cuối cùng thực hiện:

```python
add(10, 20)
```

Đây là trường hợp đơn giản nhất.

---

# 3. String

```python
def greet(name):
    return f"Hello {name}"
```

```python
queue.enqueue(
    greet,
    "An",
)
```

Worker:

```python
greet("An")
```

Không có vấn đề gì.

---

# 4. List

Ví dụ crawler:

```python
def crawl_urls(urls):
    for url in urls:
        print(url)
```

Producer:

```python
urls = [
    "https://example.com",
    "https://example.org",
    "https://example.net",
]

queue.enqueue(
    crawl_urls,
    urls,
)
```

RQ serialize:

```text
[
    "https://example.com",
    "https://example.org",
    "https://example.net"
]
```

Worker deserialize thành list Python và chạy:

```python
crawl_urls(urls)
```

---

# 5. Dict

Ví dụ:

```python
def create_user(data):
    return data["name"]
```

Producer:

```python
user = {
    "id": 100,
    "name": "An",
    "age": 30,
}

queue.enqueue(
    create_user,
    user,
)
```

Worker nhận lại:

```python
{
    "id": 100,
    "name": "An",
    "age": 30,
}
```

---

# 6. Keyword arguments

Ví dụ:

```python
def send_email(
    to,
    subject,
    body,
):
    print(to)
    print(subject)
    print(body)
```

Enqueue:

```python
queue.enqueue(
    send_email,
    to="user@example.com",
    subject="Hello",
    body="Welcome",
)
```

Worker thực hiện:

```python
send_email(
    to="user@example.com",
    subject="Hello",
    body="Welcome",
)
```

---

# 7. Đừng truyền object quá lớn

Đây là một nguyên tắc rất quan trọng.

❌ Không nên:

```python
queue.enqueue(
    process_book,
    huge_book_object,
)
```

Nếu object có kích thước:

```text
500 MB
```

thì bạn đang yêu cầu:

```text
Producer
   │
   ▼
serialize 500 MB
   │
   ▼
Redis
   │
   ▼
deserialize 500 MB
   │
   ▼
Worker
```

Rất tốn RAM và bandwidth.

---

# 8. Pattern tốt hơn: truyền ID

Thay vì:

```python
queue.enqueue(
    process_book,
    huge_book,
)
```

hãy:

```python
queue.enqueue(
    process_book,
    book_id,
)
```

Worker:

```python
def process_book(book_id):
    book = repository.get(book_id)

    ...
```

Kiến trúc:

```text
Producer
   │
   │ book_id=123
   ▼
 Redis
   │
   ▼
 Worker
   │
   │ get(123)
   ▼
 Database
```

Đây là pattern cực kỳ quan trọng khi xây dựng hệ thống lớn.

---

# 9. Đặc biệt quan trọng với crawler

Giả sử bạn có:

```python
story = Story(
    id=100,
    title="Truyện ABC",
    chapters=[...],
)
```

Không nên:

```python
queue.enqueue(
    crawl_story,
    story,
)
```

Tốt hơn:

```python
queue.enqueue(
    crawl_story,
    story.id,
)
```

Worker:

```python
def crawl_story(story_id):
    story = story_repository.get(story_id)

    ...
```

Lợi ích:

* Job nhỏ
* Redis nhẹ
* serialization nhanh
* Worker luôn lấy state mới nhất từ database
* giảm coupling
* dễ retry

---

# 10. Dataclass

Dataclass có thể serialize được trong nhiều trường hợp:

```python
from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
```

Sau đó:

```python
user = User(
    id=1,
    name="An",
)

queue.enqueue(
    process_user,
    user,
)
```

Có thể hoạt động.

Nhưng trong hệ thống production, tôi vẫn khuyên:

```python
queue.enqueue(
    process_user,
    user.id,
)
```

thay vì truyền cả object.

---

# 11. Lambda — không nên dùng

❌ Tránh:

```python
queue.enqueue(
    lambda: print("hello")
)
```

RQ Worker cần có khả năng import function.

Lambda không có một module/function name ổn định theo cách phù hợp cho job serialization.

Hãy viết:

```python
def say_hello():
    print("hello")
```

rồi:

```python
queue.enqueue(say_hello)
```

---

# 12. Nested function — tránh

❌ Không nên:

```python
def create_job():
    def task():
        print("hello")

    queue.enqueue(task)
```

`task` là local function.

Worker process khác sẽ gặp vấn đề khi import function này.

Hãy đặt task ở module level:

```python
# tasks.py

def task():
    print("hello")
```

Sau đó:

```python
queue.enqueue(task)
```

---

# 13. Closure — cũng nên tránh

Ví dụ:

```python
def create_task(name):
    def task():
        print(name)

    return task
```

Rồi:

```python
task = create_task("An")

queue.enqueue(task)
```

Đây là kiểu thiết kế không phù hợp với RQ.

Thay bằng:

```python
def greet(name):
    print(name)
```

và:

```python
queue.enqueue(
    greet,
    "An",
)
```

Đơn giản hơn rất nhiều.

---

# 14. `tasks.py` nên như thế nào?

Tôi khuyên cấu trúc:

```text
project/
│
├── pyproject.toml
│
├── app/
│   ├── __init__.py
│   │
│   ├── tasks.py
│   │
│   └── services.py
│
└── main.py
```

`tasks.py`:

```python
from app.services import process_data


def process_data_job(data_id):
    return process_data(data_id)
```

Producer:

```python
from app.tasks import process_data_job

job = queue.enqueue(
    process_data_job,
    123,
)
```

Worker phải có khả năng import:

```python
app.tasks
```

---

# 15. Một nguyên tắc rất quan trọng

**Job function phải có thể import được bởi Worker.**

Ví dụ:

```python
from app.tasks import crawl_story
```

Worker cần tìm được:

```text
app.tasks
    │
    └── crawl_story
```

Khi Worker lấy Job từ Redis, nó phải biết:

```text
module = app.tasks
function = crawl_story
```

sau đó:

```python
from app.tasks import crawl_story
```

và chạy:

```python
crawl_story(...)
```

---

# 16. Đừng nhét business logic vào Job

Đây là một nguyên tắc kiến trúc rất đáng nhớ.

❌ Không nên:

```python
def crawl_story_job(story_id):
    story = ...
    response = ...
    html = ...
    parse(...)
    save(...)
    send_notification(...)
```

Job trở thành một **God Function**.

Tốt hơn:

```python
def crawl_story_job(story_id):
    service = CrawlStoryService(...)
    return service.execute(story_id)
```

Kiến trúc:

```text
RQ Job
  │
  ▼
Application Service
  │
  ├── Crawler
  ├── Parser
  ├── Repository
  └── ...
```

Điều này rất phù hợp với hướng **Clean Architecture / DDD / SOLID** mà bạn đang học.

---

# 17. RQ Job nên càng mỏng càng tốt

Một Job lý tưởng:

```python
def crawl_story_job(story_id):
    return crawler_service.crawl(story_id)
```

Nó chỉ làm nhiệm vụ:

```text
RQ
 │
 ▼
Job
 │
 ▼
Service
```

Không nên biến Job thành nơi chứa toàn bộ nghiệp vụ.

---

# 18. Một ví dụ hoàn chỉnh

### `tasks.py`

```python
def calculate_price(
    price: int,
    quantity: int,
) -> int:
    return price * quantity
```

### `main.py`

```python
from redis import Redis
from rq import Queue

from tasks import calculate_price


redis = Redis(
    host="localhost",
    port=6379,
)

queue = Queue(
    "default",
    connection=redis,
)

job = queue.enqueue(
    calculate_price,
    150_000,
    3,
)

print("Job ID:", job.id)
```

Worker:

```bash
rq worker
```

Worker thực hiện:

```python
calculate_price(
    150_000,
    3,
)
```

Kết quả:

```text
450000
```

---

# 19. Kiểm tra Job

Sau khi Worker chạy xong:

```python
from rq.job import Job

job = Job.fetch(
    job.id,
    connection=redis,
)

print("ID:", job.id)
print("Status:", job.get_status())
print("Result:", job.result)
```

Ví dụ:

```text
ID: 7f3...
Status: finished
Result: 450000
```

---

# 20. Thiết kế tốt cho project crawler của bạn

Sau này chúng ta sẽ có:

```text
Producer
    │
    │ story_id
    ▼
 Redis
    │
    ▼
 Worker
    │
    ▼
crawl_story_job(story_id)
    │
    ▼
CrawlStoryUseCase
    │
    ├── StoryRepository
    ├── ChapterRepository
    ├── Crawler
    └── Parser
```

Job chỉ cần:

```python
def crawl_story_job(story_id):
    use_case = ...
    return use_case.execute(story_id)
```

**Không truyền cả Story object, Repository object, Crawler object hoặc DB connection vào Job.**

Chỉ truyền dữ liệu nhỏ, ổn định:

```python
story_id
source_id
chapter_id
url
```

---

# 🧠 Quy tắc vàng của RQ

Hãy nhớ 5 quy tắc:

### 1. Function phải importable

```python
def my_job():
    ...
```

đặt ở module level.

### 2. Truyền dữ liệu nhỏ

```python
queue.enqueue(task, 123)
```

tốt hơn:

```python
queue.enqueue(task, huge_object)
```

### 3. Ưu tiên ID

```python
queue.enqueue(process_story, story_id)
```

### 4. Không truyền infrastructure

Không truyền:

```text
Redis connection
DB connection
Repository instance
HTTP client instance
Crawler instance
```

### 5. Job nên mỏng

```text
RQ Job
   ↓
Use Case / Service
   ↓
Domain
```

---

# 📝 Bài tập Buổi 4

Hãy tự viết:

```python
def process_order(order_id):
    ...
```

và enqueue:

```python
order_id = 12345
```

Sau đó trả lời 3 câu:

**1.** Tại sao nên truyền `order_id` thay vì truyền toàn bộ `Order` object?

**2.** Tại sao không nên enqueue một `lambda`?

**3.** Với crawler, bạn sẽ chọn:

```python
queue.enqueue(crawl_story, story)
```

hay:

```python
queue.enqueue(crawl_story, story.id)
```

và **tại sao**?

---

### Bước tiếp theo

**Buổi 5 — Job Result & Job Lifecycle Deep Dive** sẽ đi sâu vào:

```text
Job
 │
 ├── id
 ├── status
 ├── result
 ├── exc_info
 ├── created_at
 ├── enqueued_at
 ├── started_at
 └── ended_at
```

Sau đó chúng ta sẽ tự xây một **Job Monitor CLI** để xem Job đang `queued / started / finished / failed`.
