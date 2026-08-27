Tốt 👍 Bạn chọn **câu 2**. Ta đi sâu vào:

# Buổi 2 — Redis Data Types

Đây là buổi **rất quan trọng**, vì muốn giỏi Redis thì không chỉ biết `SET/GET`, mà phải biết **chọn đúng Data Type cho từng bài toán**.

---

## 1. Redis có những Data Type nào?

Các loại cơ bản:

```text
Redis
│
├── String
├── Hash
├── List
├── Set
└── Sorted Set
```

Sau này chúng ta học thêm:

```text
├── Stream
├── Bitmap
├── HyperLogLog
└── Geospatial
```

Hôm nay tập trung 5 loại đầu.

---

# 2. String

Đây là loại đơn giản nhất.

```text
key → value
```

Ví dụ:

```text
name → "Nguyen Van A"
age  → "30"
```

Redis CLI:

```bash
SET name "Nguyen Van A"
GET name
```

Kết quả:

```text
"Nguyen Van A"
```

Python:

```python
import redis

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)

r.set("name", "Nguyen Van A")

name = r.get("name")

print(name)
```

---

# 3. Hash

Hash rất thích hợp để biểu diễn **một object**.

Ví dụ User:

```text
user:1001
    │
    ├── name → "An"
    ├── age  → "30"
    └── city → "HCM"
```

Redis:

```bash
HSET user:1001 name "An"
HSET user:1001 age 30
HSET user:1001 city "HCM"
```

Lấy một field:

```bash
HGET user:1001 name
```

Lấy toàn bộ:

```bash
HGETALL user:1001
```

Python:

```python
r.hset(
    "user:1001",
    mapping={
        "name": "An",
        "age": 30,
        "city": "HCM",
    },
)

user = r.hgetall("user:1001")

print(user)
```

Kết quả:

```python
{
    "name": "An",
    "age": "30",
    "city": "HCM",
}
```

### Quy tắc thực tế

Nếu bạn có:

```python
User(
    id=1001,
    name="An",
    age=30,
    city="HCM",
)
```

thì Redis Hash thường là lựa chọn tự nhiên:

```text
user:1001
```

---

# 4. List

List là một danh sách có thứ tự.

Ví dụ:

```text
tasks

task1
task2
task3
```

Redis:

```bash
LPUSH tasks "task1"
LPUSH tasks "task2"
LPUSH tasks "task3"
```

Xem:

```bash
LRANGE tasks 0 -1
```

Kết quả:

```text
task3
task2
task1
```

Điểm cực kỳ quan trọng:

> Redis List rất phù hợp để xây dựng **Queue**.

Ví dụ:

```text
Producer
    │
    │ LPUSH
    ▼
Redis List
    │
    │ BRPOP
    ▼
Worker
```

Đây chính là thứ chúng ta sẽ dùng sau này để **tự xây Redis Queue**.

---

# 5. Set

Set là tập hợp **không trùng lặp**.

Ví dụ:

```text
online_users

{
    user:1
    user:2
    user:5
}
```

Thêm:

```bash
SADD online_users user:1
SADD online_users user:2
SADD online_users user:5
```

Nếu:

```bash
SADD online_users user:1
```

thêm lần nữa thì Redis **không tạo duplicate**.

Kiểm tra:

```bash
SISMEMBER online_users user:1
```

Lấy tất cả:

```bash
SMEMBERS online_users
```

Set rất phù hợp cho:

* unique values
* tag
* online users
* membership
* intersection

Ví dụ:

```text
user:1 → Python, Redis, Docker
user:2 → Python, Redis
```

Ta có thể tìm:

```text
Những thứ cả hai user cùng thích
```

bằng **Set Intersection**.

---

# 6. Sorted Set

Sorted Set giống Set nhưng mỗi phần tử có thêm **score**.

Ví dụ leaderboard:

```text
leaderboard

Alice → 1000
Bob   → 850
John  → 700
```

Redis:

```bash
ZADD leaderboard 1000 Alice
ZADD leaderboard 850 Bob
ZADD leaderboard 700 John
```

Xem bảng xếp hạng:

```bash
ZRANGE leaderboard 0 -1 WITHSCORES
```

Từ cao xuống thấp:

```bash
ZREVRANGE leaderboard 0 -1 WITHSCORES
```

Đây là Data Type cực kỳ hữu ích cho:

* leaderboard
* ranking
* priority
* scheduled tasks
* scoring system

---

# 7. So sánh 5 Data Types

Hãy nhớ bảng này:

| Data Type  | Hình dung      | Dùng cho         |
| ---------- | -------------- | ---------------- |
| String     | `key → value`  | Cache, counter   |
| Hash       | Object         | User, Product    |
| List       | Danh sách      | Queue            |
| Set        | Tập hợp unique | Tags, membership |
| Sorted Set | Set + score    | Ranking          |

---

# 8. Một ví dụ thực tế

Giả sử chúng ta xây app crawl truyện.

Redis có thể thiết kế:

```text
story:1001
    │
    ├── title
    ├── author
    └── status
```

→ **Hash**

---

URL cần crawl:

```text
crawl_queue

[url1, url2, url3, ...]
```

→ **List**

---

Những URL đã crawl:

```text
crawled_urls

{
    url1,
    url2,
    url3
}
```

→ **Set**

---

Ưu tiên crawl:

```text
crawl_priority

url1 → 100
url2 → 50
url3 → 10
```

→ **Sorted Set**

---

Cache:

```text
story:1001:html
    ↓
"<html>...</html>"
```

→ **String**

Như vậy một hệ thống thực tế có thể dùng **nhiều Redis Data Type cùng lúc**.

---

# 🧠 Bài tập

Hãy chọn Data Type phù hợp:

### Câu 1

Lưu:

```text
user:1001
name = "An"
age = 30
email = "an@example.com"
```

→ ?

### Câu 2

Danh sách URL đang chờ crawl:

```text
https://site.com/page1
https://site.com/page2
https://site.com/page3
```

→ ?

### Câu 3

Danh sách URL **không được phép trùng**:

```text
url1
url2
url1
url3
```

→ ?

### Câu 4

Bảng xếp hạng:

```text
An   → 950
Binh → 800
Cuong → 1200
```

→ ?

### Câu 5

Cache HTML của một trang:

```text
page:123 → "<html>..."
```

→ ?

**Bạn trả lời 5 câu này**, tôi sẽ chấm và chuyển sang **Buổi 3 — String Deep Dive: `SET`, `GET`, `INCR`, `TTL`, `EXPIRE` + xây Counter và Cache bằng Python**.
