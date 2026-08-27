# 🟢 Buổi 5 — Redis List & Queue

Hôm nay là buổi rất quan trọng, vì **Redis List chính là nền tảng để chúng ta hiểu cách xây Queue**.

Sau buổi này bạn sẽ hiểu:

```text
Producer
   │
   ▼
Redis List
   │
   ▼
Worker
```

Và sau đó khi học **RQ**, bạn sẽ thấy RQ thực chất đang giải quyết bài toán này ở mức cao hơn.

---

# 1. Redis List là gì?

List là một danh sách có thứ tự:

```text
tasks

┌───────┬───────┬───────┐
│ task1 │ task2 │ task3 │
└───────┴───────┴───────┘
```

Redis cho phép thêm/xóa phần tử ở **đầu hoặc cuối List**.

Hai nhóm command quan trọng:

```text
LPUSH / LPOP
RPUSH / RPOP
```

---

# 2. LPUSH

Tạo List:

```bash
LPUSH tasks "task1"
```

Sau đó:

```bash
LPUSH tasks "task2"
```

Tiếp:

```bash
LPUSH tasks "task3"
```

Danh sách:

```text
task3
task2
task1
```

Bởi vì `LPUSH` thêm vào **bên trái**.

---

# 3. RPUSH

```bash
RPUSH tasks "task1"
RPUSH tasks "task2"
RPUSH tasks "task3"
```

Kết quả:

```text
task1
task2
task3
```

`RPUSH` thêm vào **bên phải**.

---

# 4. LRANGE

Xem List:

```bash
LRANGE tasks 0 -1
```

Ý nghĩa:

```text
0    → phần tử đầu tiên
-1   → phần tử cuối cùng
```

Ví dụ:

```text
LRANGE tasks 0 -1
```

→ lấy toàn bộ List.

Lấy 3 phần tử đầu:

```bash
LRANGE tasks 0 2
```

---

# 5. LPOP

Lấy và xóa phần tử bên trái:

```bash
LPOP tasks
```

Nếu:

```text
tasks

task1
task2
task3
```

thì:

```text
LPOP
```

→ `task1`

List còn:

```text
task2
task3
```

---

# 6. RPOP

Tương tự nhưng từ bên phải:

```bash
RPOP tasks
```

Nếu:

```text
task1
task2
task3
```

thì lấy:

```text
task3
```

---

# 7. List có thể trở thành Queue

Đây là phần quan trọng nhất.

Queue có nguyên tắc:

```text
FIFO

First In
First Out
```

Ví dụ:

```text
task1
task2
task3
```

Task vào trước:

```text
task1
```

phải được xử lý trước.

Ta có thể xây:

```text
Producer
    │
    │ RPUSH
    ▼
┌──────────────────┐
│ Redis List       │
│                  │
│ task1 task2 task3│
└──────────────────┘
    │
    │ LPOP
    ▼
 Worker
```

Producer:

```python
r.rpush("task_queue", "task1")
r.rpush("task_queue", "task2")
r.rpush("task_queue", "task3")
```

Worker:

```python
task = r.lpop("task_queue")
```

Như vậy:

```text
RPUSH → bên phải
LPOP  → bên trái
```

tạo thành:

```text
FIFO Queue
```

---

# 8. Vấn đề của LPOP

Giả sử Worker chạy:

```python
while True:
    task = r.lpop("task_queue")

    if task:
        process(task)
```

Khi queue rỗng:

```text
r.lpop(...)
    ↓
None
```

Worker sẽ phải liên tục hỏi Redis:

```text
Có task chưa?
    ↓
Không
    ↓
Có task chưa?
    ↓
Không
    ↓
Có task chưa?
```

Đây gọi là **polling**.

Không tối ưu.

---

# 9. BRPOP — Blocking Pop

Redis có một command rất hay:

```bash
BRPOP task_queue 0
```

`BRPOP` nghĩa là:

> Nếu chưa có task, Redis giữ connection chờ.

```text
Worker
   │
   │ BRPOP
   ▼
 Redis
   │
   │ chờ...
   │
   │ task xuất hiện
   ▼
Worker
```

`0` nghĩa là:

```text
block indefinitely
```

Ví dụ Python:

```python
while True:
    result = r.brpop(
        "task_queue",
        timeout=0,
    )

    print(result)
```

Worker sẽ **không phải liên tục polling**.

---

# 10. Producer

Ví dụ Producer:

```python
import redis

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)


def produce(task: str) -> None:
    r.rpush(
        "task_queue",
        task,
    )


produce("task-1")
produce("task-2")
produce("task-3")
```

---

# 11. Worker

Worker:

```python
import redis

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)


while True:
    _, task = r.brpop(
        "task_queue",
        timeout=0,
    )

    print(f"Processing: {task}")
```

Chạy Worker:

```bash
python worker.py
```

Worker sẽ đứng chờ.

Sau đó chạy:

```bash
python producer.py
```

Bạn sẽ thấy:

```text
Processing: task-1
Processing: task-2
Processing: task-3
```

🎯 Đây chính là một **message queue cực kỳ đơn giản**.

---

# 12. Nhưng Queue này có một vấn đề lớn

Giả sử:

```text
Redis
  │
  ▼
task-1
  │
  ▼
Worker
```

Worker gọi:

```python
r.brpop("task_queue")
```

Redis trả:

```text
task-1
```

Sau đó Worker:

```python
process(task)
```

Nhưng Worker bị crash:

```text
Redis
  │
  ▼
task-1
  │
  ▼
Worker 💥
```

Task đã bị lấy khỏi queue.

Nó **không còn trong Redis**.

Kết quả:

```text
task-1 → mất
```

Đây là vấn đề cực kỳ quan trọng.

---

# 13. Queue thực tế cần ACK

Một message queue tốt thường có:

```text
Producer
   │
   ▼
Queue
   │
   ▼
Worker
   │
   ▼
Process
   │
   ▼
ACK
```

Nếu Worker chết trước ACK:

```text
Worker 💥
   │
   X
  ACK
```

thì task cần được xử lý lại.

Đây là lý do chúng ta sẽ học tiếp:

* Reliable Queue
* ACK
* Retry
* Visibility Timeout
* Dead Letter Queue

và sau đó:

```text
Redis
  ↓
RQ
  ↓
Worker
```

---

# 14. Queue Crawl truyện

Hãy áp dụng vào project crawler của bạn.

Ta có:

```text
crawl_queue
```

Producer:

```python
r.rpush(
    "crawl_queue",
    "https://example.com/story/1",
)
```

Worker:

```python
while True:
    _, url = r.brpop(
        "crawl_queue",
        timeout=0,
    )

    crawl(url)
```

Kiến trúc:

```text
                ┌─────────────┐
                │ CLI / API   │
                └──────┬──────┘
                       │
                       │ RPUSH
                       ▼
              ┌─────────────────┐
              │ Redis           │
              │                 │
              │ crawl_queue     │
              └────────┬────────┘
                       │
                       │ BRPOP
                       ▼
              ┌─────────────────┐
              │ Crawl Worker    │
              └────────┬────────┘
                       │
                       ▼
                    Website
```

Nếu có 5 Worker:

```text
                    Redis
                      │
              crawl_queue
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
    Worker 1      Worker 2      Worker 3
        │             │             │
        ▼             ▼             ▼
      Crawl         Crawl         Crawl
```

Redis sẽ phân phối task cho các Worker thông qua việc lấy phần tử khỏi queue.

---

# 15. Queue FIFO vs Stack

Điều này rất đáng nhớ.

### Queue

```text
RPUSH
  +
LPOP
```

→ FIFO.

```text
task1 → task2 → task3

task1 được lấy trước
```

### Stack

```text
LPUSH
  +
LPOP
```

→ LIFO.

```text
task1
task2
task3

task3 được lấy trước
```

Từ đó:

```text
RPUSH + LPOP → Queue
LPUSH + LPOP → Stack
```

---

# 16. Redis List không chỉ dùng cho Queue

List còn phù hợp với:

### Recent items

```text
recent_stories
```

### Activity feed

```text
user:1001:activities
```

### Log buffer

```text
logs
```

### Task queue

```text
crawl_queue
```

---

# 17. Một pattern rất hay: Queue + JSON

Task crawler có thể phức tạp:

```python
task = {
    "url": "https://example.com/story/1",
    "source": "source_a",
    "priority": 10,
}
```

Ta serialize:

```python
import json

r.rpush(
    "crawl_queue",
    json.dumps(task),
)
```

Worker:

```python
raw = r.lpop("crawl_queue")

task = json.loads(raw)

print(task["url"])
```

Đây là cách đơn giản để truyền **structured message** qua Redis List.

Sau này chúng ta sẽ tìm hiểu tại sao **Redis Streams** hoặc **RQ** thường phù hợp hơn khi hệ thống queue trở nên phức tạp.

---

# 18. `LLEN`

Đếm số task:

```bash
LLEN crawl_queue
```

Python:

```python
size = r.llen("crawl_queue")

print(size)
```

Rất hữu ích cho dashboard:

```text
Crawler Dashboard

Pending: 1532
Workers: 8
```

---

# 19. `LTRIM`

Giả sử muốn chỉ giữ 100 activity gần nhất:

```bash
LTRIM activities 0 99
```

Pattern:

```python
r.lpush("activities", activity)
r.ltrim("activities", 0, 99)
```

Kết quả:

```text
activities

item 1
item 2
...
item 100
```

Các item cũ hơn bị loại.

Rất phù hợp cho:

```text
recent searches
recent stories
activity feed
recent logs
```

---

# 🧠 Tổng kết Buổi 5

Bạn cần nhớ:

```text
LPUSH  → thêm bên trái
RPUSH  → thêm bên phải

LPOP   → lấy bên trái
RPOP   → lấy bên phải

LRANGE → đọc List
LLEN   → đếm phần tử

BRPOP  → blocking pop
BLPOP  → blocking pop
```

Và đặc biệt:

```text
RPUSH + LPOP
       ↓
      FIFO
       ↓
     Queue
```

---

# 📝 Bài tập Buổi 5

### Câu 1

Muốn tạo FIFO Queue:

```text
task1
task2
task3
```

Bạn chọn:

```text
A. LPUSH + LPOP
B. RPUSH + LPOP
C. LPUSH + RPOP
```

### Câu 2

Tại sao `BRPOP` tốt hơn việc liên tục:

```python
while True:
    task = r.lpop("queue")
```

khi queue đang rỗng?

### Câu 3

Viết Producer:

```text
crawl_queue
```

thêm 3 URL:

```text
https://example.com/1
https://example.com/2
https://example.com/3
```

### Câu 4

Viết Worker dùng `BRPOP` để lấy URL.

### Câu 5 — quan trọng

Worker lấy task thành công nhưng **crash trước khi xử lý xong**.

```text
Redis
  │
  ▼
task-1
  │
  ▼
Worker 💥
```

**Task có bị mất không? Tại sao?**

Câu 5 sẽ dẫn chúng ta sang **Buổi 6 — Redis List nâng cao + Reliable Queue**, nơi chúng ta bắt đầu giải quyết vấn đề **ACK / retry / task bị Worker chết giữa chừng**.
