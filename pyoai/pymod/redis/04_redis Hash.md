# 🟢 Buổi 4 — Redis Hash Deep Dive

Hôm nay chúng ta học **Hash**, một Data Type cực kỳ quan trọng khi dùng Redis để lưu **object/entity**.

Nếu String là:

```text
key → value
```

thì Hash là:

```text
key
 ├── field → value
 ├── field → value
 └── field → value
```

Ví dụ:

```text
user:1001
 ├── name  → "An"
 ├── age   → "30"
 └── email → "an@example.com"
```

---

# 1. Tạo Hash

Redis CLI:

```bash
HSET user:1001 name "An"
HSET user:1001 age 30
HSET user:1001 email "an@example.com"
```

Xem toàn bộ:

```bash
HGETALL user:1001
```

Kết quả:

```text
name
An
age
30
email
an@example.com
```

---

# 2. HSET nhiều field

Thay vì:

```bash
HSET user:1001 name "An"
HSET user:1001 age 30
HSET user:1001 email "an@example.com"
```

có thể:

```bash
HSET user:1001 \
    name "An" \
    age 30 \
    email "an@example.com"
```

Python:

```python
r.hset(
    "user:1001",
    mapping={
        "name": "An",
        "age": 30,
        "email": "an@example.com",
    },
)
```

---

# 3. HGET

Lấy một field:

```bash
HGET user:1001 name
```

→

```text
An
```

Python:

```python
name = r.hget("user:1001", "name")

print(name)
```

---

# 4. HGETALL

Lấy toàn bộ object:

```python
user = r.hgetall("user:1001")

print(user)
```

Kết quả:

```python
{
    "name": "An",
    "age": "30",
    "email": "an@example.com",
}
```

Lưu ý:

> Redis Hash không tự biết `age` là `int`.

Redis thường trả dữ liệu về dạng string khi dùng:

```python
decode_responses=True
```

Nếu cần:

```python
age = int(user["age"])
```

---

# 5. HEXISTS

Kiểm tra field tồn tại:

```bash
HEXISTS user:1001 email
```

Python:

```python
exists = r.hexists(
    "user:1001",
    "email",
)
```

---

# 6. HDEL

Xóa field:

```bash
HDEL user:1001 email
```

Python:

```python
r.hdel(
    "user:1001",
    "email",
)
```

Sau đó:

```bash
HGETALL user:1001
```

---

# 7. HINCRBY

Đây là một tính năng rất hay.

Ví dụ:

```text
user:1001
    points → 100
```

Tăng:

```bash
HINCRBY user:1001 points 10
```

→ `110`

Python:

```python
r.hincrby(
    "user:1001",
    "points",
    10,
)
```

Rất hữu ích cho:

```text
points
views
score
login_count
download_count
```

---

# 8. Hash vs nhiều String

Đây là câu hỏi quan trọng.

Có thể lưu User bằng String:

```text
user:1001:name  → An
user:1001:age   → 30
user:1001:email → ...
```

Nhưng Hash tự nhiên hơn:

```text
user:1001
 ├── name
 ├── age
 └── email
```

So sánh:

```text
Nhiều String

user:1001:name
user:1001:age
user:1001:email


Hash

user:1001
 ├── name
 ├── age
 └── email
```

Nếu dữ liệu có cấu trúc giống một object, **Hash thường là lựa chọn tốt**.

---

# 9. Hash + Python Dataclass

Đây là phần tôi muốn bạn chú ý vì nó kết nối trực tiếp với kiến thức Python/OOP của bạn.

Giả sử:

```python
from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    age: int
    email: str
```

Ta có:

```python
user = User(
    id=1001,
    name="An",
    age=30,
    email="an@example.com",
)
```

Có thể lưu vào Redis:

```python
r.hset(
    f"user:{user.id}",
    mapping={
        "name": user.name,
        "age": user.age,
        "email": user.email,
    },
)
```

---

# 10. Đọc Redis → Entity

Ngược lại:

```python
data = r.hgetall("user:1001")
```

Sau đó:

```python
user = User(
    id=1001,
    name=data["name"],
    age=int(data["age"]),
    email=data["email"],
)
```

Mô hình:

```text
             Redis
               │
               │ HGETALL
               ▼
          dict[str, str]
               │
               │ mapping
               ▼
             User
            Entity
```

Đây chính là ý tưởng của **Repository**.

---

# 11. Xây RedisUserRepository

Ví dụ đơn giản:

```python
from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    age: int
    email: str


class RedisUserRepository:

    def __init__(self, redis):
        self.redis = redis

    def _key(self, user_id: int) -> str:
        return f"user:{user_id}"

    def save(self, user: User) -> None:
        self.redis.hset(
            self._key(user.id),
            mapping={
                "name": user.name,
                "age": user.age,
                "email": user.email,
            },
        )

    def get(self, user_id: int) -> User | None:
        data = self.redis.hgetall(
            self._key(user_id)
        )

        if not data:
            return None

        return User(
            id=user_id,
            name=data["name"],
            age=int(data["age"]),
            email=data["email"],
        )

    def delete(self, user_id: int) -> None:
        self.redis.delete(
            self._key(user_id)
        )
```

Sử dụng:

```python
repo = RedisUserRepository(r)

user = User(
    id=1001,
    name="An",
    age=30,
    email="an@example.com",
)

repo.save(user)

user = repo.get(1001)

print(user)
```

Kết quả:

```text
User(
    id=1001,
    name='An',
    age=30,
    email='an@example.com'
)
```

---

# 12. Kiến trúc

Chúng ta đang có:

```text
Application
     │
     ▼
Repository Interface
     │
     ▼
RedisUserRepository
     │
     ▼
redis-py
     │
     ▼
Redis
```

Đây là cách Redis bắt đầu kết nối với những thứ bạn đã học về:

* Clean Architecture
* DDD
* Repository Pattern
* Entity
* Dataclass
* Dependency Injection

---

# 13. Một vấn đề quan trọng: ID

Bạn có thể thấy chúng ta không lưu:

```text
id → 1001
```

vào Hash.

Thay vào đó:

```text
user:1001
```

đã chứa ID.

```text
user:1001
 ├── name
 ├── age
 └── email
```

Đây là một cách thiết kế rất phổ biến.

Key trở thành một phần của **identity**.

---

# 14. Khi nào KHÔNG nên dùng Hash?

Không phải object nào cũng nên biến thành Hash.

Ví dụ dữ liệu:

```json
{
    "name": "An",
    "profile": {
        "avatar": "...",
        "settings": {
            "theme": "dark"
        }
    },
    "posts": [...]
}
```

Nếu object rất phức tạp, đôi khi lưu JSON dưới String sẽ đơn giản hơn:

```python
import json

r.set(
    "user:1001",
    json.dumps(user_data),
)
```

Vì vậy:

```text
Object đơn giản
      ↓
    Hash

Object JSON phức tạp
      ↓
String + JSON
```

Không có quy tắc tuyệt đối.

---

# 15. Một quy tắc thiết kế Redis rất quan trọng

Đừng thiết kế Redis chỉ dựa vào:

> "Dữ liệu của tôi trông như thế nào?"

Hãy hỏi:

> **"Tôi sẽ truy cập dữ liệu như thế nào?"**

Ví dụ cần lấy:

```text
user:1001:name
```

→ String có thể phù hợp.

Cần lấy:

```text
user:1001
 ├── name
 ├── age
 └── email
```

→ Hash.

Cần queue:

```text
url1
url2
url3
```

→ List.

Cần unique:

```text
url1
url2
url3
```

→ Set.

Cần ranking:

```text
url1 → 100
url2 → 50
```

→ Sorted Set.

**Data structure phải phục vụ access pattern.**

Đây là tư duy quan trọng nhất khi thiết kế Redis.

---

# 🧠 Bài tập Buổi 4

Thiết kế Redis cho Entity:

```python
@dataclass
class Story:
    id: int
    title: str
    author: str
    status: str
    chapter_count: int
```

Hãy trả lời:

### Câu 1

Bạn sẽ đặt Redis key là gì?

### Câu 2

Bạn sẽ dùng Data Type nào?

### Câu 3

Viết lệnh Redis để lưu:

```text
id = 1001
title = "Đấu Phá Thương Khung"
author = "Thiên Tằm Thổ Đậu"
status = "ongoing"
chapter_count = 1500
```

### Câu 4

Viết command để tăng:

```text
chapter_count
```

thêm `1`.

### Câu 5 — thiết kế quan trọng

Nếu hệ thống crawler có:

```text
100 Worker
```

và tất cả worker đều có thể cập nhật `chapter_count`, bạn nghĩ nên dùng:

```text
HGET → Python + 1 → HSET
```

hay:

```text
HINCRBY
```

**Tại sao?**

Buổi tiếp theo chúng ta sẽ chuyển sang **Buổi 5 — Redis List**, từ đó bắt đầu xây **Queue Producer → Redis → Worker**, là nền móng trực tiếp cho RQ.
