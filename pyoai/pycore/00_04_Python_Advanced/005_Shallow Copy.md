# 🐍 Buổi 5 — Shallow Copy

Ở Buổi 4, ta đã học **Garbage Collector** và cách Python quản lý object graph.

Hôm nay chúng ta đi sâu vào một câu hỏi cực kỳ quan trọng:

```python
a = [[1, 2], [3, 4]]

b = a.copy()

b[0].append(99)

print(a)
```

Kết quả:

```text
[[1, 2, 99], [3, 4]]
```

😮 Tại sao `a` cũng thay đổi?

Câu trả lời nằm ở **Shallow Copy**.

---

# 1. Trước tiên: Assignment không phải Copy

Đây là điều cần phân biệt rõ:

```python
a = [1, 2, 3]
b = a
```

Không tạo object mới.

```text
a ─────┐
       ▼
   ┌─────────┐
   │ [1,2,3] │
   └─────────┘
       ▲
       │
b ─────┘
```

Vì vậy:

```python
a is b
```

kết quả:

```text
True
```

Nếu:

```python
b.append(4)
```

thì:

```python
print(a)
```

→

```text
[1, 2, 3, 4]
```

---

# 2. Copy thật sự là gì?

Khi copy, ta muốn tạo:

```text
Object mới
```

Ví dụ:

```python
a = [1, 2, 3]

b = a.copy()
```

Bây giờ:

```python
a is b
```

→

```text
False
```

Graph:

```text
       ┌─────────────┐
a ───► │ [1, 2, 3]   │
       └─────────────┘

       ┌─────────────┐
b ───► │ [1, 2, 3]   │
       └─────────────┘
```

Có **hai list khác nhau**.

---

# 3. Nhưng Shallow Copy chỉ copy "lớp ngoài"

Đây là điểm quan trọng nhất.

Ví dụ:

```python
a = [
    [1, 2],
    [3, 4],
]
```

Object graph:

```text
a
│
▼
Outer List
├──► Inner List [1, 2]
└──► Inner List [3, 4]
```

Bây giờ:

```python
b = a.copy()
```

Shallow copy tạo một **outer list mới**:

```text
a ───► Outer A
        │
        ├──► Inner 1
        │
        └──► Inner 2


b ───► Outer B
        │
        ├──► Inner 1
        │
        └──► Inner 2
```

Nhìn kỹ:

```text
Outer A ≠ Outer B

Inner 1 == Inner 1
Inner 2 == Inner 2
```

Tức là:

```python
a is b
```

→ `False`

nhưng:

```python
a[0] is b[0]
```

→ `True`

---

# 4. Đây chính là Shallow Copy

Định nghĩa:

> **Shallow copy tạo object container mới nhưng giữ nguyên references tới các object bên trong.**

Mô hình:

```text
Shallow Copy
      │
      ▼
copy outer object
      │
      ▼
reuse inner references
```

---

# 5. Ví dụ cơ bản

```python
a = [
    [1, 2],
    [3, 4],
]

b = a.copy()

print(a is b)
print(a[0] is b[0])
print(a[1] is b[1])
```

Kết quả:

```text
False
True
True
```

---

# 6. Tại sao `b[0].append()` làm `a` thay đổi?

Ta có:

```python
b[0].append(99)
```

`b[0]` và `a[0]` là **cùng một object**.

```text
a ─────► Outer A
          │
          └────► [1, 2, 99]
                     ▲
                     │
b ─────► Outer B ────┘
```

Vì vậy:

```python
a[0]
```

và:

```python
b[0]
```

đều nhìn thấy:

```text
[1, 2, 99]
```

---

# 7. Nhưng thay thế phần tử thì sao?

Đây là một distinction rất quan trọng.

```python
a = [
    [1, 2],
    [3, 4],
]

b = a.copy()

b[0] = [100, 200]
```

Kết quả:

```python
print(a)
print(b)
```

```text
[[1, 2], [3, 4]]

[[100, 200], [3, 4]]
```

Tại sao?

Vì:

```python
b[0] = ...
```

không mutate inner list cũ.

Nó thay reference:

```text
Trước:

b
│
▼
Outer B
│
├──► Inner 1
└──► Inner 2


Sau:

b
│
▼
Outer B
│
├──► New Inner
└──► Inner 2
```

Trong khi `a` vẫn:

```text
a
│
▼
Outer A
│
├──► Inner 1
└──► Inner 2
```

---

# 8. Mutation vs Assignment

Đây là một trong những kỹ năng quan trọng nhất khi debug Python.

### Mutation

```python
b[0].append(99)
```

Object cũ bị thay đổi.

### Assignment

```python
b[0] = [100, 200]
```

Reference trong container bị thay đổi.

So sánh:

```text
Mutation
    ↓
thay đổi object

Assignment
    ↓
thay đổi reference
```

---

# 9. `list.copy()`

Đối với list:

```python
b = a.copy()
```

tương đương về ý nghĩa shallow copy với:

```python
b = list(a)
```

Ví dụ:

```python
a = [1, 2, 3]

b = a.copy()
c = list(a)

print(b is a)
print(c is a)
```

```text
False
False
```

---

# 10. Slice cũng là Shallow Copy

Với list:

```python
b = a[:]
```

cũng tạo shallow copy.

Ví dụ:

```python
a = [[1, 2], [3, 4]]

b = a[:]

print(a is b)
print(a[0] is b[0])
```

```text
False
True
```

---

# 11. `copy.copy()`

Python có module:

```python
import copy
```

và:

```python
copy.copy(obj)
```

Ví dụ:

```python
import copy

a = [[1, 2], [3, 4]]

b = copy.copy(a)

print(a is b)
print(a[0] is b[0])
```

```text
False
True
```

---

# 12. Ba cách thường gặp

Với list:

```python
b = a.copy()
```

```python
b = list(a)
```

```python
b = a[:]
```

đều có thể tạo shallow copy.

Ngoài ra:

```python
import copy

b = copy.copy(a)
```

cũng là shallow copy.

---

# 13. Shallow Copy với Dictionary

Ví dụ:

```python
user = {
    "name": "An",
    "settings": {
        "theme": "dark"
    }
}

other = user.copy()
```

Graph:

```text
user
 │
 ▼
Dict A
 ├── name ─────► "An"
 │
 └── settings ─► Dict Settings
                       ▲
                       │
other                 │
 │                    │
 ▼                    │
Dict B ───────────────┘
```

Vì vậy:

```python
user is other
```

→ `False`

nhưng:

```python
user["settings"] is other["settings"]
```

→ `True`

---

# 14. Hậu quả

```python
other["settings"]["theme"] = "light"
```

thì:

```python
print(user)
```

sẽ là:

```text
{
    "name": "An",
    "settings": {
        "theme": "light"
    }
}
```

Bởi vì `settings` là cùng một object.

---

# 15. Shallow Copy với Object

Ví dụ:

```python
class User:
    def __init__(self, name):
        self.name = name
        self.settings = {
            "theme": "dark"
        }
```

Tạo:

```python
user1 = User("An")
user2 = copy.copy(user1)
```

Ta có:

```text
user1 ──► User Object A
            │
            ├── name ─────► "An"
            │
            └── settings ─► Dict


user2 ──► User Object B
            │
            ├── name ─────► "An"
            │
            └── settings ─► SAME Dict
```

Do đó:

```python
user1 is user2
```

→ `False`

nhưng:

```python
user1.settings is user2.settings
```

→ `True`

---

# 16. Shallow Copy thực chất là Copy Object Graph ở một level

Đây là cách nhìn sâu hơn.

Original:

```text
A
│
├──► B
│
└──► C
```

Shallow copy:

```text
A' 
│
├──► B
│
└──► C
```

Chỉ tạo:

```text
A'
```

Còn:

```text
B
C
```

được dùng lại.

---

# 17. Deep Copy

Để hiểu shallow copy, chúng ta cần biết contrast với:

```python
copy.deepcopy()
```

Ví dụ:

```python
import copy

a = [
    [1, 2],
    [3, 4],
]

b = copy.deepcopy(a)
```

Graph:

```text
a ───► Outer A
        │
        ├──► Inner A1
        └──► Inner A2


b ───► Outer B
        │
        ├──► Inner B1
        └──► Inner B2
```

Lúc này:

```python
a is b
```

→ `False`

và:

```python
a[0] is b[0]
```

→ `False`

---

# 18. So sánh

|                                | Assignment | Shallow Copy | Deep Copy |
| ------------------------------ | ---------- | ------------ | --------- |
| Outer object mới               | ❌          | ✅            | ✅         |
| Inner object mới               | ❌          | ❌            | ✅         |
| Reference được chia sẻ         | ✅          | ✅            | thường ❌  |
| `a is b`                       | True       | False        | False     |
| Nested mutation ảnh hưởng nhau | ✅          | ✅            | ❌         |

Mental model:

```text
Assignment
A ─────► Object
B ─────► Object


Shallow Copy
A ─────► Object A
B ─────► Object B
              │
              └──► SAME nested objects


Deep Copy
A ─────► Object A
B ─────► Object B
              │
              └──► NEW nested objects
```

---

# 19. Một ví dụ rất dễ nhầm

```python
a = {
    "users": [
        {"name": "A"},
        {"name": "B"},
    ]
}

b = a.copy()

b["users"].append({"name": "C"})
```

Sau đó:

```python
print(a)
```

Kết quả:

```python
{
    "users": [
        {"name": "A"},
        {"name": "B"},
        {"name": "C"},
    ]
}
```

Vì:

```python
a["users"] is b["users"]
```

→ `True`.

---

# 20. Còn trường hợp này?

```python
b["users"] = [
    {"name": "X"}
]
```

thì `a` không thay đổi.

Vì bạn đang thay reference trong `b`.

```text
a
│
▼
Dict A
│
└── users ──► List A


b
│
▼
Dict B
│
└── users ──► List B
```

Ban đầu:

```text
Dict A ──┐
         ├──► List A
Dict B ──┘
```

Sau assignment:

```text
Dict A ──► List A

Dict B ──► List B
```

---

# 21. Copy không đơn giản là "nhân đôi object"

Đây là một tư duy rất quan trọng.

Không nên nghĩ:

```text
copy(object)
    ↓
nhân đôi toàn bộ memory
```

Mà nên nghĩ:

```text
copy
 ↓
tạo object graph mới
 ↓
quyết định node nào được reuse
 ↓
quyết định node nào được clone
```

Shallow:

```text
clone root
+
reuse descendants
```

Deep:

```text
clone root
+
clone descendants
```

---

# 22. Tại sao Deep Copy không phải lúc nào cũng tốt?

Deep copy có thể rất đắt.

Ví dụ crawler:

```text
Response
 ├── Request
 ├── Headers
 ├── Cookies
 ├── HTML
 ├── Parser
 ├── Metadata
 └── Cache
```

Nếu:

```python
copy.deepcopy(response)
```

thì có thể phải copy một object graph rất lớn.

Điều này:

* tốn CPU
* tốn memory
* có thể copy những thứ không cần thiết
* có thể gặp object không phù hợp để deepcopy

Vì vậy:

> **Đừng dùng `deepcopy()` như giải pháp mặc định cho mọi vấn đề về shared state.**

---

# 23. Cách tốt hơn trong Architecture

Ví dụ crawler có:

```python
request = Request(
    url=url,
    headers=headers,
)
```

Thay vì:

```python
new_request = copy.deepcopy(request)
```

đôi khi tốt hơn là thiết kế API rõ ràng:

```python
new_request = request.with_headers(
    new_headers
)
```

Hoặc:

```python
new_request = Request(
    url=request.url,
    headers=new_headers,
)
```

Tức là **explicit copy semantics**.

Điều này rất phù hợp với:

```text
DDD
Clean Architecture
Immutable Value Object
Functional style
```

---

# 24. `copy.deepcopy()` xử lý cycle như thế nào?

Đây là một chi tiết rất thú vị.

Giả sử:

```python
a = []

a.append(a)
```

Graph:

```text
a
│
▼
List
│
└──────► chính nó
```

Nếu naïvely deepcopy:

```text
copy(a)
 ↓
copy(element)
 ↓
copy(a)
 ↓
copy(element)
 ↓
...
```

→ infinite recursion.

Python `deepcopy()` sử dụng cơ chế memoization để xử lý object đã được copy.

Ví dụ:

```python
import copy

a = []
a.append(a)

b = copy.deepcopy(a)
```

Sau đó:

```python
b is b[0]
```

→

```text
True
```

Đây là một ví dụ rất đẹp về **object graph + identity**.

---

# 25. Connection với Buổi 1–4

Chúng ta đang nối toàn bộ kiến thức:

```text
Buổi 1
Object Model
      ↓
Object Identity
      ↓
References
      ↓
Buổi 2
Memory
      ↓
Buổi 3
Reference Counting
      ↓
Buổi 4
Garbage Collector
      ↓
Buổi 5
Copy / Object Graph
```

Thực tế:

```text
Python object
      │
      ▼
Reference graph
      │
 ┌────┴────┐
 ▼         ▼
GC       Copy
          │
    ┌─────┴─────┐
    ▼           ▼
Shallow       Deep
```

---

# 🧪 Bài tập Buổi 5

### Bài 1

Dự đoán:

```python
a = [[1, 2], [3, 4]]
b = a.copy()

print(a is b)
print(a[0] is b[0])
```

---

### Bài 2

Giải thích kết quả:

```python
a = [[1, 2]]

b = a.copy()

b[0].append(3)

print(a)
```

---

### Bài 3

So sánh:

```python
a = [[1, 2]]

b = a.copy()
c = a[:]

import copy
d = copy.copy(a)
e = copy.deepcopy(a)
```

Kiểm tra:

```python
a is b
a is c
a is d
a is e

a[0] is b[0]
a[0] is c[0]
a[0] is d[0]
a[0] is e[0]
```

---

### Bài 4 — Object Graph

Cho:

```python
a = {
    "users": [
        {"name": "A"},
        {"name": "B"},
    ]
}

b = a.copy()
```

Hãy vẽ object graph và xác định:

```python
a is b
a["users"] is b["users"]
a["users"][0] is b["users"][0]
```

---

### Bài 5 — Crawler

Giả sử:

```python
request = {
    "url": "https://example.com",
    "headers": {
        "User-Agent": "Crawler"
    }
}
```

Bạn muốn tạo một request mới với:

```python
User-Agent = "Bot/2.0"
```

nhưng **không được làm thay đổi request cũ**.

Hãy thử giải quyết bằng:

1. shallow copy
2. deep copy
3. explicit reconstruction

Sau đó so sánh ưu/nhược điểm.

---

## 🎯 Buổi tiếp theo

**Buổi 6 — Deep Copy**

Chúng ta sẽ đi sâu vào:

```text
copy.deepcopy()
       │
       ├── Object Graph
       ├── Memo
       ├── Circular Reference
       ├── __deepcopy__()
       ├── __copy__()
       ├── Custom Class
       ├── Immutable Object
       └── Deep Copy trong Architecture
```

Đặc biệt sẽ phân tích **từng bước `deepcopy()` duyệt object graph như thế nào**, thay vì chỉ dùng `copy.deepcopy()` một cách máy móc.
