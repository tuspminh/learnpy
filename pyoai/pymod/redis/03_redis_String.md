Tuyệt 👍 **Buổi 3 — Redis String Deep Dive**.

`String` là Data Type đơn giản nhất của Redis nhưng lại là loại được sử dụng **cực kỳ nhiều**, đặc biệt trong:

* Cache
* Counter
* Session
* Feature flag
* Distributed state
* Rate limiting

---

# 1. String trong Redis

Redis String có thể lưu:

```text
text
number
JSON
binary data
```

Ví dụ:

```bash
SET name "An"
GET name
```

Kết quả:

```text
"An"
```

Python:

```python
r.set("name", "An")

value = r.get("name")

print(value)
```

Nếu tạo connection với:

```python
decode_responses=True
```

thì:

```python
print(type(value))
```

sẽ là:

```text
<class 'str'>
```

---

# 2. SET

Cú pháp:

```bash
SET key value
```

Ví dụ:

```bash
SET name "Nguyen Van An"
```

Lấy:

```bash
GET name
```

Nếu key không tồn tại:

```bash
GET abc
```

Redis trả:

```text
(nil)
```

Python:

```python
value = r.get("abc")

print(value)
```

Kết quả:

```python
None
```

---

# 3. SET ghi đè dữ liệu

Đây là đặc điểm quan trọng.

```bash
SET name "An"
SET name "Binh"

GET name
```

Kết quả:

```text
"Binh"
```

Không có version cũ.

---

# 4. Kiểm tra key tồn tại

```bash
EXISTS name
```

Ví dụ:

```text
(integer) 1
```

Python:

```python
if r.exists("name"):
    print("Exists")
```

---

# 5. DEL

Xóa:

```bash
DEL name
```

Python:

```python
r.delete("name")
```

Kiểm tra:

```bash
EXISTS name
```

Kết quả:

```text
(integer) 0
```

---

# 6. MSET và MGET

Nếu cần lưu nhiều String:

```bash
MSET name "An" age 30 city "HCM"
```

Lấy nhiều:

```bash
MGET name age city
```

Kết quả:

```text
1) "An"
2) "30"
3) "HCM"
```

Python:

```python
r.mset({
    "name": "An",
    "age": 30,
    "city": "HCM",
})

values = r.mget(
    "name",
    "age",
    "city",
)

print(values)
```

---

# 7. String có thể lưu số

Redis không có Data Type riêng gọi là `Integer`.

Ví dụ:

```bash
SET counter 100
```

Redis vẫn coi đây là **String**, nhưng Redis hỗ trợ các phép toán số trên String có nội dung số.

```bash
INCR counter
```

Kết quả:

```text
(integer) 101
```

Tiếp:

```bash
INCR counter
```

→ `102`

---

# 8. INCR

`INCR` cực kỳ quan trọng.

```bash
SET counter 0
INCR counter
INCR counter
INCR counter
```

Kết quả:

```bash
GET counter
```

```text
"3"
```

Python:

```python
r.set("counter", 0)

r.incr("counter")
r.incr("counter")
r.incr("counter")

print(r.get("counter"))
```

---

# 9. INCRBY

Tăng nhiều hơn:

```bash
SET score 100
INCRBY score 50
```

Kết quả:

```text
150
```

Python:

```python
r.set("score", 100)

r.incrby("score", 50)

print(r.get("score"))
```

---

# 10. DECR

Giảm:

```bash
SET stock 10

DECR stock
DECR stock
```

→ `8`

Hoặc:

```bash
DECRBY stock 5
```

→ `3`

Đây là nền tảng để xây:

```text
counter
inventory
view count
download count
like count
```

---

# 11. TTL — Time To Live

Đây là phần **cực kỳ quan trọng** khi dùng Redis làm cache.

Ví dụ:

```bash
SET session:user:1001 "abc"
EXPIRE session:user:1001 60
```

Nghĩa là:

> Key sẽ tự động biến mất sau 60 giây.

Kiểm tra:

```bash
TTL session:user:1001
```

Có thể nhận:

```text
(integer) 53
```

Sau vài giây:

```bash
TTL session:user:1001
```

→

```text
(integer) 48
```

---

# 12. SETEX

Thay vì:

```bash
SET key value
EXPIRE key 60
```

có thể dùng:

```bash
SETEX key 60 value
```

Ví dụ:

```bash
SETEX cache:user:1001 300 "An"
```

Key tồn tại trong:

```text
300 seconds
```

Python:

```python
r.setex(
    "cache:user:1001",
    300,
    "An",
)
```

---

# 13. Cách hiện đại: SET + EX

Trong code thực tế, bạn sẽ thường gặp:

```bash
SET cache:user:1001 "An" EX 300
```

Tức là:

```text
SET
 +
EXPIRE 300
```

Python:

```python
r.set(
    "cache:user:1001",
    "An",
    ex=300,
)
```

Tôi khuyến nghị bạn làm quen với cách này.

---

# 14. Cache bằng Redis

Đây là pattern cực kỳ quan trọng:

```text
             Request
                │
                ▼
             Redis
                │
        ┌───────┴───────┐
        │               │
      HIT             MISS
        │               │
        ▼               ▼
      Return         Database
                        │
                        ▼
                      Redis
                        │
                        ▼
                      Return
```

Python:

```python
def get_user(user_id: int):
    key = f"user:{user_id}"

    cached = r.get(key)

    if cached is not None:
        return cached

    # Giả lập database
    user = "Nguyen Van An"

    r.set(key, user, ex=300)

    return user
```

Lần đầu:

```text
Redis MISS
   ↓
Database
   ↓
Redis SET
```

Lần sau:

```text
Redis HIT
   ↓
Return
```

Đây gọi là **Cache-Aside Pattern**.

---

# 15. Một ví dụ rất thực tế: lượt xem truyện

Giả sử trang truyện:

```text
/story/1001
```

Ta muốn đếm lượt xem.

Redis:

```text
story:1001:views
```

Khi có người đọc:

```python
r.incr("story:1001:views")
```

Lấy:

```python
views = r.get("story:1001:views")
```

Ví dụ:

```text
story:1001:views → 15230
```

Điểm hay là `INCR` là operation nguyên tử ở phía Redis.

Nhiều worker cùng tăng counter vẫn có thể dùng:

```python
r.incr("story:1001:views")
```

mà không cần tự viết:

```python
value = r.get(...)
value += 1
r.set(...)
```

Cách thứ hai dễ gặp race condition.

---

# 16. Một ví dụ khác: rate limiting

Giả sử:

```text
100 requests / 60 seconds
```

Ta có:

```text
rate:user:1001
```

Mỗi request:

```python
count = r.incr("rate:user:1001")

if count == 1:
    r.expire("rate:user:1001", 60)

if count > 100:
    print("Too many requests")
```

Mô hình:

```text
Request 1
   ↓
INCR → 1
   ↓
EXPIRE 60

Request 2
   ↓
INCR → 2

...

Request 101
   ↓
INCR → 101
   ↓
REJECT
```

Đây chính là nền tảng để sau này chúng ta học **Redis Rate Limiter + Atomicity + Lua Script**.

---

# 17. Điều rất quan trọng: Redis không phải biến Python

Đừng nghĩ:

```python
counter = 0
counter += 1
```

giống:

```python
r.incr("counter")
```

Redis là **server riêng**:

```text
Python Process
     │
     │ network
     ▼
Redis Server
```

Mỗi lần gọi Redis có communication giữa client và server.

Vì vậy sau này chúng ta sẽ học:

```text
Pipeline
Connection Pool
Batch operation
Transaction
```

để tối ưu.

---

# 🧠 Bài tập Buổi 3

Không cần viết nhiều code. Hãy trả lời:

### 1.

Muốn lưu:

```text
username = "An"
```

Redis command nào?

### 2.

Muốn tăng:

```text
views
```

lên 1, dùng command nào?

### 3.

Muốn giảm:

```text
stock
```

5 đơn vị, dùng command nào?

### 4.

Muốn lưu:

```text
token = "abc123"
```

trong **300 giây**, viết Redis command.

### 5.

Tại sao cách này nguy hiểm khi nhiều worker cùng cập nhật?

```python
value = r.get("views")
value += 1
r.set("views", value)
```

Và tại sao:

```python
r.incr("views")
```

tốt hơn?

---

Sau bài này, **Buổi 4** chúng ta sẽ học **Redis Hash Deep Dive** và bắt đầu xây một `RedisRepository` bằng Python, theo đúng tư duy Repository Pattern mà bạn đang học.
