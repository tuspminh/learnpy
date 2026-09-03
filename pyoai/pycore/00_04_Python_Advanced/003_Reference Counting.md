# 🐍 Giai đoạn IV — Python Advanced

## Buổi 3 — Reference Counting

Ở Buổi 2, chúng ta đã thấy:

```text
name
  ↓
reference
  ↓
object
```

và biết rằng CPython có một cơ chế rất quan trọng để quản lý lifetime của object:

> **Reference Counting**

Hôm nay chúng ta sẽ hiểu chính xác hơn:

> **Python biết khi nào một object không còn được sử dụng bằng cách nào?**

---

# 1. Reference Counting là gì?

Mỗi Python object trong CPython có một thông tin theo dõi số lượng reference đang trỏ tới nó.

Ví dụ:

```python
x = []
```

Ta hình dung:

```text
x ─────────► List Object
              refcount ≈ 1
```

Nếu:

```python
y = x
```

thì:

```text
x ───────┐
         ├──────► List Object
y ───────┘          refcount ≈ 2
```

Nếu:

```python
del x
```

thì:

```text
y ───────► List Object
             refcount ≈ 1
```

Cuối cùng:

```python
del y
```

thì:

```text
List Object
    │
    └── refcount → 0
```

Object có thể được giải phóng.

---

# 2. Mô hình cơ bản

Hãy nhớ:

```text
Reference Count
       │
       ▼
Số lượng reference đang giữ object
```

Ví dụ:

```python
x = []
```

```text
      x
      │
      ▼
┌──────────────┐
│ List Object  │
│ refcount ≈ 1 │
└──────────────┘
```

Sau:

```python
y = x
```

```text
      x
      │
      ├─────────► List
      │
      y             refcount ≈ 2
```

---

# 3. Tại sao gọi là Reference Counting?

Bởi vì runtime thực hiện ý tưởng:

```text
Reference
   ↓
Count
```

Mỗi khi reference được tạo:

```text
count += 1
```

Khi reference biến mất:

```text
count -= 1
```

Khi:

```text
count == 0
```

object không còn reference trực tiếp nào nữa và có thể được deallocate.

---

# 4. `sys.getrefcount()`

Python cung cấp:

```python
import sys
```

và:

```python
sys.getrefcount()
```

Ví dụ:

```python
import sys

x = []

print(sys.getrefcount(x))
```

Bạn có thể thấy:

```text
2
```

hoặc giá trị khác tùy ngữ cảnh.

Tại sao không phải `1`?

Vì:

```python
sys.getrefcount(x)
```

bản thân việc truyền `x` vào function thường tạo thêm một reference tạm thời.

Vì vậy:

```text
getrefcount(x)
       │
       └── temporary reference
```

Do đó:

> `sys.getrefcount()` thường cao hơn số reference mà bạn đang trực giác đếm.

---

# 5. Thí nghiệm đầu tiên

Chạy:

```python
import sys

x = []

print("A:", sys.getrefcount(x))

y = x

print("B:", sys.getrefcount(x))

z = x

print("C:", sys.getrefcount(x))

del y

print("D:", sys.getrefcount(x))

del z

print("E:", sys.getrefcount(x))
```

Bạn sẽ thấy reference count tăng giảm theo việc tạo/xóa reference.

Mục tiêu của bài này không phải nhớ chính xác con số.

Mục tiêu là hiểu:

```text
y = x
```

làm tăng reference tới object.

Còn:

```text
del y
```

làm giảm reference.

---

# 6. Assignment không copy object

Đây là nguyên nhân rất nhiều người hiểu sai Reference Counting.

```python
x = [1, 2, 3]
y = x
```

Không xảy ra:

```text
❌
x → List A
y → List B
```

Mà:

```text
✅

x ───────┐
         ├────► List A
y ───────┘
```

Hai name.

Một object.

---

# 7. `id()` chứng minh điều này

```python
x = [1, 2, 3]
y = x

print(id(x))
print(id(y))

print(x is y)
```

Kết quả:

```text
True
```

Bởi vì:

```text
x ───┐
     ├──► same object
y ───┘
```

---

# 8. Reference trong container

Reference không chỉ đến từ variable.

Ví dụ:

```python
x = []
container = [x]
```

Ta có:

```text
x ─────────────┐
               ▼
          ┌──────────┐
          │ List A   │
          └──────────┘
               ▲
               │
          container
```

Thực tế:

```text
container
   │
   ▼
┌───────────────┐
│ reference ────┼────► List A
└───────────────┘
```

Vì vậy object vẫn tồn tại ngay cả khi:

```python
del x
```

bởi vì `container` vẫn giữ reference.

---

# 9. Ví dụ

```python
x = [1, 2, 3]

container = [x]

del x

print(container)
```

Kết quả:

```text
[[1, 2, 3]]
```

Tại sao?

Trước:

```text
x ───────┐
         ├──► List A
container┘
```

Sau `del x`:

```text
container ─────► List A
```

Object vẫn sống.

---

# 10. Function argument tạo reference

Ví dụ:

```python
def process(data):
    print(data)
```

Khi:

```python
x = [1, 2, 3]

process(x)
```

trong quá trình gọi function:

```text
x ───────┐
         ├────► List
data ────┘
```

`data` tham chiếu tới cùng object.

Không có một list mới được tạo chỉ vì truyền argument.

---

# 11. Ví dụ chứng minh

```python
def process(data):
    print(data is original)


original = [1, 2, 3]

process(original)
```

Kết quả:

```text
True
```

Argument truyền vào function không tự động copy object.

---

# 12. Return cũng liên quan đến reference

Ví dụ:

```python
def create():
    data = [1, 2, 3]
    return data


x = create()
```

Trong function:

```text
data ─────► List
```

Sau khi return:

```text
x ────────► List
```

Reference được chuyển sang context mới.

Khi function kết thúc, local name:

```text
data
```

không còn tồn tại.

Nhưng object vẫn tồn tại vì:

```text
x ─────► object
```

---

# 13. Local variable không quyết định object lifetime

Sai:

> Object chết khi function kết thúc.

Đúng hơn:

> Object có thể sống tiếp nếu vẫn còn reference.

Ví dụ:

```python
def create():
    data = [1, 2, 3]
    return data


result = create()
```

Sau function:

```text
data ──X

result ─────► List
```

List vẫn sống.

---

# 14. Global Reference

Ví dụ:

```python
cache = []

def add():
    cache.append("hello")
```

`cache` là một global reference tới list.

Ngay cả khi function kết thúc:

```text
function ends
      ↓
local references disappear
```

thì:

```text
global cache
      ↓
List
```

vẫn tồn tại.

---

# 15. Attribute cũng là Reference

Ví dụ:

```python
class User:
    pass

user = User()

data = [1, 2, 3]

user.data = data
```

Ta có:

```text
data ───────┐
            ├────► List
user.data ──┘
```

Nếu:

```python
del data
```

thì:

```text
user.data ─────► List
```

Object vẫn sống.

---

# 16. Dictionary cũng giữ reference

```python
data = [1, 2, 3]

cache = {
    "data": data
}
```

Sơ đồ:

```text
data ───────┐
            │
            ▼
         List
            ▲
            │
cache["data"]
```

Xóa:

```python
del data
```

không xóa List.

---

# 17. List cũng giữ reference

Ví dụ:

```python
obj = {"name": "Alice"}

items = [obj]
```

Ta có:

```text
obj ────────┐
            ▼
         Dict
            ▲
            │
items[0] ───┘
```

`items` đang giữ reference tới dict.

---

# 18. `del` giảm reference

Ví dụ:

```python
x = []
y = x
z = x
```

Ta có:

```text
x ───────┐
y ───────┼────► List
z ───────┘
```

Sau:

```python
del y
```

```text
x ───────┐
         ├────► List
z ───────┘
```

Sau:

```python
del x
```

```text
z ───────► List
```

Sau:

```python
del z
```

```text
List
 ↑
 └── no longer referenced
```

---

# 19. Reference Count = 0

Về mặt khái niệm:

```text
refcount > 0
    ↓
object alive

refcount == 0
    ↓
object can be deallocated
```

Đây là đặc điểm rất quan trọng của CPython.

---

# 20. Nhưng "Reference Count = 0" chưa phải toàn bộ câu chuyện

Đây là điểm cực kỳ quan trọng.

Giả sử:

```python
a = []
b = []

a.append(b)
b.append(a)
```

Ta có:

```text
a ─────► A
         │
         ▼
         B
         │
         └────► A
```

Sau:

```python
del a
del b
```

Các object vẫn tham chiếu lẫn nhau:

```text
A ─────► B
▲       │
└───────┘
```

Reference count của chúng **không về 0**.

Đây chính là vấn đề của **circular reference**.

---

# 21. Reference Counting có giới hạn

Reference Counting rất tốt trong việc:

```text
object
 ↓
không còn reference
 ↓
deallocate
```

Nhưng không tự giải quyết tốt:

```text
A → B
↑   ↓
└───┘
```

Bởi vì:

```text
A reference count > 0
B reference count > 0
```

mặc dù toàn bộ cycle có thể không còn reachable từ chương trình.

---

# 22. Đây là lý do có Garbage Collector

CPython có thêm:

```text
Reference Counting
        +
Cyclic Garbage Collector
```

Mô hình:

```text
Python Memory Management
          │
          ├── Reference Counting
          │
          └── Cyclic GC
```

Reference Counting xử lý phần lớn object lifetime.

GC xử lý những cycle mà reference counting đơn thuần không thể thu hồi.

---

# 23. Một ví dụ rất quan trọng

```python
class Node:
    pass


a = Node()
b = Node()

a.other = b
b.other = a
```

Graph:

```text
a ─────► Node A
          │
          │ other
          ▼
        Node B
          │
          │ other
          ▼
        Node A
```

Sau:

```python
del a
del b
```

Không còn local names:

```text
a ──X
b ──X
```

nhưng:

```text
A ↔ B
```

vẫn tồn tại.

Đây là **reference cycle**.

---

# 24. Reference Counting vs Garbage Collection

|                            | Reference Counting    | Garbage Collector       |
| -------------------------- | --------------------- | ----------------------- |
| Theo dõi reference         | ✅                     | Không chỉ dựa vào count |
| Object không còn reference | Xử lý rất tốt         | Có thể xử lý            |
| Cycle                      | ❌ Không tự giải quyết | ✅                       |
| Immediate cleanup          | Thường có thể         | Không nhất thiết        |
| CPython                    | Rất quan trọng        | Có                      |

---

# 25. Một điểm nâng cao: CPython không phải Python nói chung

Đây là một nguyên tắc cần nhớ từ Giai đoạn IV:

> **Reference Counting là đặc điểm quan trọng của CPython, không phải một quy luật bắt buộc của ngôn ngữ Python.**

Ví dụ:

```text
Python language
       │
       ├── CPython
       ├── PyPy
       ├── Jython
       └── IronPython
```

Các implementation có thể có cơ chế memory management khác nhau.

Khi nói:

> "Python sử dụng reference counting"

cách nói chính xác hơn là:

> **CPython sử dụng reference counting như một cơ chế quản lý lifetime object chủ đạo.**

---

# 26. Object Destruction và `__del__`

Python cho phép định nghĩa:

```python
class Resource:
    def __del__(self):
        print("destroy")
```

Ví dụ:

```python
obj = Resource()

del obj
```

Trong một số tình huống CPython, bạn có thể thấy:

```text
destroy
```

Nhưng **không nên dùng `__del__` làm cơ chế quản lý resource quan trọng**.

Đặc biệt không nên dựa vào nó cho:

```text
file
database connection
network socket
lock
```

Thay vào đó dùng:

```python
with ...
```

hoặc context manager.

---

# 27. Vì sao không nên phụ thuộc vào `__del__`?

Bởi vì object destruction có nhiều trường hợp phức tạp:

```text
Circular reference
Interpreter shutdown
Multiple objects referencing each other
Exception trong __del__
```

Resource management nên dùng:

```python
with open(...) as f:
    ...
```

thay vì:

```python
f = open(...)
...
# hy vọng __del__ sẽ đóng
```

---

# 28. Thí nghiệm `weakref`

Một cách rất hay để quan sát lifetime là `weakref`.

```python
import weakref


class User:
    pass


user = User()

ref = weakref.ref(user)

print(ref())
```

Kết quả:

```text
<User object ...>
```

Sau:

```python
del user
```

nếu không còn strong reference:

```python
print(ref())
```

có thể nhận:

```text
None
```

Mô hình:

```text
strong reference
      │
      ▼
    Object

weak reference
      │
      └────────► Object
```

Weak reference không giữ object sống theo cách của strong reference.

---

# 29. Reference Graph

Đây là cách tư duy quan trọng nhất từ buổi này.

Đừng chỉ nhìn:

```python
x = ...
```

Hãy nhìn chương trình như một **graph**:

```text
Name
 │
 ▼
Object
 │
 ├────► Object
 │
 ├────► Object
 │
 └────► Object
```

Ví dụ:

```python
user = {
    "name": "Alice",
    "friends": []
}
```

Có thể hình dung:

```text
user
 │
 ▼
Dict
 ├── "name" ───► String
 │
 └── "friends" ───► List
```

Khi debugging memory:

> Chúng ta cần tìm **ai đang giữ reference tới object**.

---

# 30. Đây là nền tảng của Memory Leak

Ví dụ:

```python
cache = []

def process():
    data = create_large_object()
    cache.append(data)
```

Mỗi lần gọi:

```python
process()
```

graph phát triển:

```text
cache
 │
 ├──► Large Object
 ├──► Large Object
 ├──► Large Object
 ├──► Large Object
 └──► ...
```

Reference vẫn tồn tại.

Vì vậy GC không thể đơn giản xóa chúng.

Đây là lý do:

> **Memory leak trong Python thường không phải vì Python "quên giải phóng" object, mà vì chương trình vẫn vô tình giữ reference tới object.**

---

# 31. Một ví dụ thực tế hơn

Crawler của chúng ta sau này có thể có:

```text
Crawler
   │
   ▼
Task Queue
   │
   ▼
Request objects
   │
   ▼
Response
   │
   ▼
Parser
   │
   ▼
Cache
```

Nếu cache giữ toàn bộ response:

```text
Cache
 ├── Response 1
 ├── Response 2
 ├── Response 3
 ├── ...
```

thì memory có thể tăng liên tục.

Đây chính là lý do kiến thức Reference Counting sau này sẽ liên quan trực tiếp đến:

* Crawler
* Queue
* Cache
* Thread
* AsyncIO
* Worker
* Framework design

---

# 32. Bài thực hành quan trọng

Hãy chạy chương trình này:

```python
import sys


class User:
    pass


user = User()

print("1:", sys.getrefcount(user))

a = user

print("2:", sys.getrefcount(user))

b = user

print("3:", sys.getrefcount(user))

container = [user]

print("4:", sys.getrefcount(user))

del a

print("5:", sys.getrefcount(user))

del b

print("6:", sys.getrefcount(user))

del container

print("7:", sys.getrefcount(user))
```

Hãy quan sát **xu hướng tăng/giảm**, không cần quá bận tâm tới con số tuyệt đối.

---

# 🧪 Bài tập

## Bài 1 — Assignment

Dự đoán:

```python
a = []
b = a
c = b

print(a is b)
print(b is c)
print(a is c)
```

Giải thích bằng reference graph.

---

## Bài 2 — Container

Dự đoán:

```python
a = [1, 2, 3]
container = [a]

del a

print(container)
```

Tại sao list vẫn tồn tại?

---

## Bài 3 — Function

```python
def create():
    data = [1, 2, 3]
    return data


result = create()
```

Sau khi `create()` kết thúc:

```text
data
result
List object
```

cái nào còn tồn tại?

Hãy vẽ graph.

---

## Bài 4 — Attribute

```python
class User:
    pass


user = User()

data = [1, 2, 3]

user.data = data

del data

print(user.data)
```

Tại sao vẫn truy cập được `user.data`?

---

## Bài 5 — Circular Reference ⭐

Phân tích:

```python
class Node:
    pass


a = Node()
b = Node()

a.other = b
b.other = a

del a
del b
```

Vẽ:

```text
Node A
  ↓
Node B
  ↓
Node A
```

và giải thích tại sao Reference Counting đơn thuần không thể thu hồi cycle này.

---

# 🎯 Kiến thức cần thuộc sau Buổi 3

Bạn nên nhớ 5 câu này:

```text
1. Assignment tạo thêm reference, không tạo object mới.

2. Container, attribute, function argument... đều có thể giữ reference.

3. del name không đồng nghĩa với xóa object.

4. CPython dùng Reference Counting để quản lý object lifetime.

5. Circular Reference là điểm yếu của Reference Counting.
```

Và mô hình quan trọng nhất:

```text
             ┌──────────────┐
             │    Object    │
             │              │
             │ refcount = N │
             └──────────────┘
                ▲    ▲    ▲
                │    │    │
              name  attr container

                    ↓

              refcount == 0
                    ↓
              deallocation
```

## Buổi 4 — Garbage Collector

Tiếp theo chúng ta sẽ giải quyết chính vấn đề còn lại:

```text
Reference Counting
       ↓
       ❌
Circular Reference
       ↓
Garbage Collector
```

Chúng ta sẽ học **`gc` module**, **generation**, **cyclic GC**, cách phát hiện cycle và cách tự quan sát GC trong Python.
