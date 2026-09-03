# 🐍 Buổi 6 — Deep Copy

Ở Buổi 5, ta đã học:

```text
Assignment
    ↓
Reference
    ↓
Shallow Copy
    ↓
Deep Copy
```

Hôm nay tập trung hoàn toàn vào:

```python
copy.deepcopy()
```

Mục tiêu không chỉ là biết dùng `deepcopy()`, mà phải hiểu **nó copy object graph như thế nào**.

---

# 1. Deep Copy là gì?

Ví dụ:

```python
import copy

a = [
    [1, 2],
    [3, 4],
]

b = copy.deepcopy(a)
```

Shallow copy:

```text
A ──► Outer A
       │
       ├──► Inner 1
       └──► Inner 2

B ──► Outer B
       │
       ├──► SAME Inner 1
       └──► SAME Inner 2
```

Deep copy:

```text
A ──► Outer A
       │
       ├──► Inner A1
       └──► Inner A2


B ──► Outer B
       │
       ├──► Inner B1
       └──► Inner B2
```

Các object mutable bên trong được sao chép thay vì đơn giản reuse reference.

---

# 2. Kiểm chứng

```python
import copy

a = [[1, 2], [3, 4]]

b = copy.deepcopy(a)

print(a is b)
print(a[0] is b[0])
print(a[1] is b[1])
```

Kết quả:

```text
False
False
False
```

Vì vậy:

```python
b[0].append(99)
```

thì:

```python
print(a)
print(b)
```

cho:

```text
[[1, 2], [3, 4]]
[[1, 2, 99], [3, 4]]
```

---

# 3. Nhưng Deep Copy không có nghĩa "mọi object đều tạo bản sao mới"

Đây là một nuance rất quan trọng.

Ví dụ:

```python
a = [1, 2, 3]
b = copy.deepcopy(a)
```

Bạn không nên suy luận rằng Python nhất thiết tạo một object integer hoàn toàn mới cho từng số.

Các immutable object như:

```text
int
float
str
bytes
tuple chứa immutable objects...
```

có thể được reuse tùy semantics của `copy`.

Điểm quan trọng là **deep copy quan tâm đến việc sao chép object graph sao cho các mutable objects cần độc lập thì được tách ra**.

---

# 4. Object Graph mới là trung tâm

Đừng nghĩ:

```text
deepcopy(list)
```

Hãy nghĩ:

```text
deepcopy(Object Graph)
```

Ví dụ:

```python
data = {
    "users": [
        {
            "name": "Alice",
            "roles": ["admin", "editor"]
        }
    ]
}
```

Graph:

```text
Dict
 │
 └── users
      │
      ▼
     List
      │
      ▼
     User Dict
      ├── name ──► "Alice"
      │
      └── roles
            │
            ▼
           List
            ├──► "admin"
            └──► "editor"
```

`deepcopy()` phải đi qua graph này.

---

# 5. Deep Copy hoạt động theo ý tưởng nào?

Conceptually:

```text
deepcopy(root)
     │
     ▼
đã copy object này chưa?
     │
 ┌───┴────┐
 │        │
YES       NO
 │        │
 ▼        ▼
reuse    tạo copy
           │
           ▼
      copy children
           │
           ▼
      lưu vào memo
```

Trong đó **memo** cực kỳ quan trọng.

---

# 6. Memo là gì?

Deep copy phải giữ một bảng kiểu:

```text
original object → copied object
```

Ví dụ:

```text
memo

Object A → Object A'
Object B → Object B'
Object C → Object C'
```

Tại sao?

Có hai lý do chính:

1. Xử lý circular reference.
2. Giữ nguyên sharing relationships trong object graph.

---

# 7. Circular Reference

Ví dụ:

```python
import copy

a = []
a.append(a)
```

Object graph:

```text
a
│
▼
List
│
└────────► chính nó
```

Nếu copy naïve:

```text
copy(a)
 ↓
copy(a[0])
 ↓
copy(a)
 ↓
copy(a[0])
 ↓
...
```

→ infinite recursion.

Nhưng:

```python
b = copy.deepcopy(a)
```

hoạt động.

Kiểm tra:

```python
print(b is b[0])
```

Kết quả:

```text
True
```

---

# 8. Deep Copy xử lý cycle như thế nào?

Conceptually:

### Bước 1

Gặp:

```text
A
```

Tạo:

```text
A'
```

và lưu:

```text
memo[A] = A'
```

### Bước 2

Đi vào child:

```text
A → A
```

Deepcopy gặp lại `A`.

Tra:

```text
memo[A]
```

đã tồn tại.

→ trả về `A'`.

Kết quả:

```text
A' → A'
```

Graph được giữ nguyên topology.

---

# 9. Đây là lý do memo cực kỳ quan trọng

Không có memo:

```text
Cycle
 ↓
infinite recursion
```

Có memo:

```text
Cycle
 ↓
đã gặp object
 ↓
reuse copied object
```

---

# 10. Sharing Relationship

Đây là một trường hợp rất hay bị bỏ qua.

```python
shared = []

a = [shared, shared]
```

Graph:

```text
a
│
├──► shared
│
└──► shared
```

Hai reference cùng trỏ đến **một object**.

Deep copy:

```python
b = copy.deepcopy(a)
```

Ta kiểm tra:

```python
print(b[0] is b[1])
```

Kết quả:

```text
True
```

Đây là điều rất quan trọng.

Deep copy không đơn giản:

```text
copy từng occurrence độc lập
```

Mà cố gắng giữ **quan hệ identity/sharing của object graph**.

---

# 11. So sánh

Original:

```text
A
├──► B
└──► B
```

Deep copy:

```text
A'
├──► B'
└──► B'
```

Không phải:

```text
A'
├──► B1'
└──► B2'
```

Đó chính là vai trò của `memo`.

---

# 12. `copy.copy()` và `copy.deepcopy()`

```python
import copy
```

### Shallow

```python
b = copy.copy(a)
```

Conceptually:

```text
clone root
+
reuse children
```

### Deep

```python
b = copy.deepcopy(a)
```

Conceptually:

```text
clone root
+
recursively copy relevant children
+
memoize objects
```

---

# 13. Custom Class

Ví dụ:

```python
class User:
    def __init__(self, name):
        self.name = name
        self.settings = {
            "theme": "dark"
        }
```

```python
import copy

user1 = User("An")
user2 = copy.deepcopy(user1)
```

Ta có:

```text
user1 ──► User A
            │
            └──► settings A


user2 ──► User B
            │
            └──► settings B
```

Kiểm tra:

```python
print(user1 is user2)
print(user1.settings is user2.settings)
```

```text
False
False
```

---

# 14. `__copy__()`

Python cho phép class tùy chỉnh shallow-copy behavior.

Ví dụ:

```python
import copy


class User:
    def __init__(self, name):
        self.name = name

    def __copy__(self):
        print("Custom shallow copy")
        new = type(self)(self.name)
        return new
```

Khi:

```python
user2 = copy.copy(user1)
```

Python có thể sử dụng:

```python
__copy__()
```

---

# 15. `__deepcopy__()`

Tương tự, class có thể tùy chỉnh:

```python
__deepcopy__(memo)
```

Ví dụ:

```python
import copy


class User:
    def __init__(self, name, settings):
        self.name = name
        self.settings = settings

    def __deepcopy__(self, memo):
        new = type(self).__new__(type(self))

        memo[id(self)] = new

        new.name = self.name
        new.settings = copy.deepcopy(
            self.settings,
            memo,
        )

        return new
```

Đây là pattern quan trọng:

```text
create new object
       ↓
register in memo
       ↓
deepcopy children
       ↓
return new object
```

---

# 16. Tại sao phải truyền `memo`?

Bạn sẽ thấy:

```python
copy.deepcopy(value, memo)
```

thay vì:

```python
copy.deepcopy(value)
```

Trong custom `__deepcopy__`, `memo` phải được truyền tiếp.

Ví dụ:

```python
new.settings = copy.deepcopy(
    self.settings,
    memo,
)
```

Nếu bạn bỏ qua `memo` và tự gọi deepcopy một cách không đúng trong một object graph phức tạp, bạn có thể phá vỡ cơ chế xử lý cycle/sharing.

---

# 17. Pattern chuẩn

Một implementation custom thường có dạng:

```python
def __deepcopy__(self, memo):
    new = type(self).__new__(type(self))

    memo[id(self)] = new

    new.field1 = copy.deepcopy(self.field1, memo)
    new.field2 = copy.deepcopy(self.field2, memo)

    return new
```

Mental model:

```text
__deepcopy__
     │
     ├── create object
     │
     ├── memo[id(self)] = new
     │
     ├── deepcopy child 1
     │
     ├── deepcopy child 2
     │
     └── return new
```

---

# 18. Immutable Objects

Deep copy với immutable object là một câu chuyện khác.

Ví dụ:

```python
import copy

x = "hello"
y = copy.deepcopy(x)

print(x is y)
```

Có thể:

```text
True
```

Điều này hoàn toàn hợp lý.

Nếu object không thể mutate:

```text
"hello"
```

thì không nhất thiết phải tạo bản sao vật lý mới.

---

# 19. Tuple

Tuple cần đặc biệt chú ý.

```python
a = (1, 2, 3)
b = copy.deepcopy(a)
```

Vì tuple chứa immutable objects nên implementation có thể reuse.

Nhưng:

```python
a = ([1, 2], [3, 4])
b = copy.deepcopy(a)
```

thì các list bên trong cần được deep-copy.

Kiểm tra:

```python
print(a is b)
print(a[0] is b[0])
```

Thông thường:

```text
False
False
```

---

# 20. Deep Copy không phải Serialization

Đừng nhầm:

```python
copy.deepcopy(obj)
```

với:

```text
pickle
JSON
serialization
database persistence
```

Deep copy mục tiêu là:

> tạo một object graph mới trong memory với semantics copy tương ứng.

Serialization mục tiêu là:

> biến object/data thành representation có thể lưu trữ/truyền tải.

Ví dụ:

```text
Object
  │
  ├── deepcopy → Object Graph mới
  │
  └── serialize → bytes / text
```

---

# 21. Deep Copy có thể rất đắt

Ví dụ:

```python
huge_data = {
    "pages": [...],
    "responses": [...],
    "parsed": [...],
    "metadata": [...],
}
```

Nếu:

```python
copy.deepcopy(huge_data)
```

Bạn có thể tạo một object graph rất lớn.

Memory:

```text
Original
   ↓
500 MB

Deep Copy
   ↓
500 MB+

Total
   ↓
~1 GB+
```

Không chỉ memory.

CPU cũng phải duyệt graph.

---

# 22. Crawler là nơi dễ gặp vấn đề này

Giả sử:

```text
CrawlerContext
├── scheduler
├── downloader
├── cache
├── parser_registry
├── request_history
└── metrics
```

Nếu làm:

```python
new_context = copy.deepcopy(context)
```

có thể bạn vô tình copy:

```text
cache
request history
metrics
registry
HTTP client
```

trong khi thực tế chỉ muốn tạo một request mới.

Đây là **design smell**.

---

# 23. Tốt hơn Deep Copy trong nhiều trường hợp

Thay vì:

```python
new_request = copy.deepcopy(request)
```

hãy thiết kế:

```python
new_request = request.clone(
    headers=new_headers
)
```

Hoặc:

```python
new_request = Request(
    url=request.url,
    method=request.method,
    headers=new_headers,
    timeout=request.timeout,
)
```

Ưu điểm:

```text
Explicit
   ↓
dễ hiểu
   ↓
ít memory
   ↓
ít coupling
   ↓
dễ test
```

---

# 24. Deep Copy và Immutability

Một architectural approach tốt hơn nữa:

```text
Mutable giant object
        ↓
deepcopy()
        ↓
sửa vài field
```

thay bằng:

```text
Immutable object
        ↓
create new object với field mới
```

Ví dụ:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    url: str
    method: str
    timeout: float
```

Thay vì:

```python
request2 = copy.deepcopy(request1)
```

có thể thiết kế API kiểu:

```text
request1
   ↓
new Request(...)
```

hoặc dùng cơ chế tạo bản sao có thay đổi có chủ đích.

---

# 25. Deep Copy và `dataclass`

Ví dụ:

```python
from dataclasses import dataclass


@dataclass
class Config:
    headers: dict
    options: list
```

:

```python
import copy

config1 = Config(
    headers={"User-Agent": "Bot"},
    options=["retry", "timeout"],
)

config2 = copy.deepcopy(config1)
```

Khi đó:

```python
config2.headers["User-Agent"] = "Bot/2.0"
config2.options.append("cache")
```

không làm thay đổi:

```python
config1
```

---

# 26. Một lỗi rất nguy hiểm

Không phải lúc nào:

```python
deepcopy()
```

cũng là solution.

Ví dụ object chứa:

```text
socket
file handle
thread
lock
database connection
HTTP client
GUI widget
OS resource
```

thì "copy toàn bộ object graph" có thể không có ý nghĩa hoặc không được hỗ trợ như bạn mong muốn.

Ví dụ architectural object:

```python
class Crawler:
    self.http_client
    self.scheduler
    self.worker_pool
    self.database
```

Không nên có tư duy:

```python
crawler2 = copy.deepcopy(crawler1)
```

Thay vào đó hãy xác định **state nào cần copy**.

---

# 27. Rule rất quan trọng

Khi bạn thấy:

```python
copy.deepcopy(...)
```

hãy tự hỏi:

### Câu 1

> Tôi thực sự cần copy toàn bộ graph không?

### Câu 2

> Object nào cần độc lập?

### Câu 3

> Object nào có thể share?

### Câu 4

> Có thể tạo object mới bằng constructor/factory không?

### Câu 5

> Có thể thiết kế immutable không?

---

# 28. Một ví dụ thực tế hơn

Giả sử:

```python
request = {
    "url": "https://example.com",
    "headers": {
        "User-Agent": "Crawler"
    },
    "metadata": {
        "retry": 3
    }
}
```

Bạn muốn thay:

```text
User-Agent
```

Có thể:

```python
new_request = copy.deepcopy(request)

new_request["headers"]["User-Agent"] = "Bot/2.0"
```

Cách này đúng.

Nhưng nếu request rất lớn và chỉ cần thay headers, có thể tốt hơn:

```python
new_request = {
    **request,
    "headers": {
        **request["headers"],
        "User-Agent": "Bot/2.0",
    },
}
```

Đây là kiểu **structural reconstruction**.

---

# 29. So sánh ba chiến lược

### Shallow copy

```python
new = old.copy()
```

Nhanh hơn, nhưng nested mutable objects có thể được share.

### Deep copy

```python
new = copy.deepcopy(old)
```

An toàn hơn về nested mutable state, nhưng có thể tốn CPU/memory.

### Explicit reconstruction

```python
new = Request(
    url=old.url,
    headers=new_headers,
)
```

Thường rõ ràng nhất về mặt architecture.

---

# 30. Mental Model quan trọng nhất

Đừng nhớ:

> `deepcopy()` = copy tất cả.

Hãy nhớ:

```text
deepcopy
   │
   ▼
Object Graph Traversal
   │
   ├── object đã copy?
   │       │
   │       └── YES → lấy từ memo
   │
   └── NO
       │
       ▼
   tạo copied object
       │
       ▼
   lưu vào memo
       │
       ▼
   deepcopy children
```

---

# 🧠 Tổng kết Buổi 5 → Buổi 6

```text
Assignment
    │
    ▼
cùng object
    │
    ├───────────────┐
    ▼               ▼
Shallow Copy     Deep Copy
    │               │
    ▼               ▼
copy root       copy graph
    │               │
    ▼               ▼
share children  clone children
                    │
                    ▼
                  memo
                    │
             ┌──────┴──────┐
             ▼             ▼
          cycles        sharing
```

---

# 🧪 Bài tập Buổi 6

### Bài 1 — Nested object

Dự đoán:

```python
import copy

a = {
    "config": {
        "retry": 3
    }
}

b = copy.deepcopy(a)

b["config"]["retry"] = 10

print(a)
print(b)
```

---

### Bài 2 — Sharing

```python
import copy

shared = {
    "value": 100
}

a = [shared, shared]

b = copy.deepcopy(a)

print(b[0] is b[1])
print(a[0] is b[0])
```

Giải thích cả hai kết quả.

---

### Bài 3 — Circular Reference

```python
import copy

a = []
a.append(a)

b = copy.deepcopy(a)

print(b is b[0])
```

Giải thích tại sao không xảy ra infinite recursion.

---

### Bài 4 — Custom `__deepcopy__`

Tự viết:

```python
class User:
    def __init__(self, name, settings):
        self.name = name
        self.settings = settings
```

Sau đó implement:

```python
__deepcopy__(self, memo)
```

để:

```python
user2 = copy.deepcopy(user1)
```

tạo `settings` độc lập.

---

### Bài 5 — Crawler Architecture

Thiết kế:

```text
Request
├── url
├── method
├── headers
├── cookies
└── metadata
```

Viết ba phiên bản:

```python
clone_shallow()
clone_deep()
clone_explicit()
```

Sau đó benchmark và suy nghĩ:

> Trong production crawler framework, bạn sẽ chọn cách nào và tại sao?

---

## 🎯 Buổi 7 — Memory Debugging

Đây là buổi cuối của **Part I — Python Runtime & Memory**.

Chúng ta sẽ chuyển từ:

```text
"Hiểu memory"
```

sang:

```text
"Điều tra memory"
```

với:

```text
tracemalloc
gc
gc.get_referrers()
gc.get_referents()
snapshot
compare_to()
memory growth
leak detection
```

và đặc biệt xây một **memory leak simulator cho crawler** để tìm chính xác object nào đang giữ memory.
