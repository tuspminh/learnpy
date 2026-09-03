# 🐍 Giai đoạn IV — Python Advanced

## Buổi 2 — Memory Management

Ở Buổi 1, chúng ta đã xây dựng mô hình:

```text
name
  ↓
object
  ↓
type
  ↓
memory
```

Hôm nay chúng ta đi xuống một tầng sâu hơn:

> **Khi Python tạo một object, object đó được quản lý trong bộ nhớ như thế nào?**

Đây là kiến thức nền cho:

* Reference Counting
* Garbage Collector
* Shallow Copy / Deep Copy
* Memory Leak
* `tracemalloc`
* Performance
* GIL
* CPython internals

---

# 1. Memory Management là gì?

Khi viết:

```python
user = User("Alice")
```

Python phải làm rất nhiều việc:

```text
User("Alice")
      │
      ▼
Tạo object
      │
      ▼
Cấp phát memory
      │
      ▼
Khởi tạo object
      │
      ▼
Đặt reference
      │
      ▼
user ───────► object
```

Khi object không còn được sử dụng:

```text
object
  ↓
không còn reference
  ↓
memory có thể được giải phóng
```

Python có cơ chế tự động quản lý phần lớn quá trình này.

Đây gọi là:

> **Automatic Memory Management**

---

# 2. Python không bắt bạn `free()`

Trong C:

```c
User *user = malloc(...);

free(user);
```

Lập trình viên phải chủ động giải phóng memory.

Python thì:

```python
user = User()
```

Sau đó bạn không cần:

```python
free(user)
```

Python tự quản lý lifetime của object.

Đây là một trong những ưu điểm lớn của Python.

Nhưng điều đó **không có nghĩa Python không thể có memory leak**.

Ví dụ:

```python
cache = []

while True:
    cache.append(generate_large_object())
```

Object vẫn còn reference:

```text
cache
 │
 ├──► object
 ├──► object
 ├──► object
 ├──► object
 └──► ...
```

Python không thể tự giải phóng chúng vì chương trình vẫn giữ reference.

---

# 3. Memory của Python — nhìn ở mức khái niệm

Ta có thể hình dung:

```text
Operating System
       │
       ▼
Process Memory
       │
       ├── Python runtime
       │
       ├── Python heap
       │      │
       │      ├── Object A
       │      ├── Object B
       │      ├── Object C
       │      └── ...
       │
       └── other memory
```

Điểm quan trọng:

> Python quản lý một vùng memory riêng dành cho các Python object.

Với CPython, phần này thường được gọi là **Python-managed heap**.

---

# 4. Stack và Heap

Bạn sẽ thường nghe:

```text
Stack
Heap
```

Trong Python cần cẩn thận với cách giải thích này.

Không nên đơn giản hóa thành:

> "Python variable nằm trên stack, object nằm trên heap."

Mô hình chính xác hơn là:

```text
Python execution
       │
       ├── Frames
       │
       └── Python objects
              ↓
           Heap
```

Ví dụ:

```python
x = 100
```

Có thể hình dung:

```text
Frame
┌──────────────┐
│ x ───────────┼────────► int object
└──────────────┘          100
```

`x` là một name trong namespace/frame.

Object `100` là một Python object được runtime quản lý.

---

# 5. Python Object không chỉ chứa Value

Một object Python không đơn giản chỉ là:

```text
100
```

Ở mức khái niệm, một object có metadata.

Ví dụ:

```text
┌──────────────────────┐
│ Python Object        │
├──────────────────────┤
│ Reference count      │
│ Type pointer         │
│ Object data          │
└──────────────────────┘
```

Trong CPython, object header có những thông tin quan trọng liên quan đến:

* reference count
* type

Đây là lý do Buổi 3 chúng ta sẽ học:

> **Reference Counting**

---

# 6. Type Pointer

Hãy quay lại:

```python
x = 100
```

Python phải biết:

> `x` đang tham chiếu tới object kiểu gì?

Object có thông tin về type.

Khái niệm:

```text
x
│
▼
┌─────────────────────┐
│ Object              │
├─────────────────────┤
│ refcount            │
│ type ───────────────┼────► int
│ value               │
└─────────────────────┘
```

Vì vậy:

```python
type(x)
```

có thể xác định được:

```text
int
```

---

# 7. Reference Count

Đây là phần chúng ta sẽ đào sâu ở Buổi 3.

Ví dụ:

```python
x = []
```

Ta có:

```text
x ───────► list object
```

Python theo dõi số lượng reference tới object.

Nếu:

```python
x = []
y = x
```

thì:

```text
x ───────┐
         ├────► list object
y ───────┘
```

Object có nhiều reference hơn.

Khi:

```python
del x
```

thì:

```text
y ───────► list object
```

Object vẫn tồn tại.

Khi:

```python
del y
```

thì không còn reference trực tiếp nào từ hai name này.

Đây là nền tảng của Reference Counting.

---

# 8. `del` không có nghĩa là "xóa object"

Đây là một hiểu nhầm phổ biến.

```python
x = [1, 2, 3]

del x
```

Không nhất thiết có nghĩa:

> list object bị xóa ngay.

`del x` chủ yếu loại bỏ **name `x`** khỏi namespace hiện tại.

Ví dụ:

```python
x = [1, 2, 3]
y = x

del x

print(y)
```

Vẫn chạy:

```text
[1, 2, 3]
```

Bởi vì:

```text
x ──X

y ───────► list
```

Object vẫn còn reference từ `y`.

---

# 9. Object Lifetime

Một object có lifecycle:

```text
Create
  ↓
Use
  ↓
References change
  ↓
No longer reachable
  ↓
Cleanup
  ↓
Memory reclaimed
```

Ví dụ:

```python
def create_user():
    user = {"name": "Alice"}
    return user
```

Sau khi:

```python
data = create_user()
```

thì:

```text
data ─────► dict
```

Khi:

```python
del data
```

và không còn reference khác:

```text
dict
 ↑
 0 references
```

Object có thể trở thành đối tượng để runtime thu hồi.

---

# 10. Nhưng Python có nhiều tầng Memory Management

Đây là phần quan trọng.

Không nên nghĩ:

```text
Object
 ↓
malloc()
 ↓
free()
```

đơn giản như vậy.

CPython có nhiều tầng:

```text
Your Python Code
       ↓
Python Object Allocator
       ↓
Python Memory Allocator
       ↓
System Allocator
       ↓
Operating System
```

Ở tầng thấp hơn, CPython có các cơ chế allocator riêng nhằm giảm overhead và tăng tốc việc cấp phát object.

---

# 11. Python Memory Manager

Ta có thể hình dung:

```text
Application
     │
     ▼
Python Runtime
     │
     ▼
Memory Manager
     │
     ├── Allocate
     ├── Reuse
     ├── Manage
     └── Release
```

Ví dụ bạn liên tục tạo object nhỏ:

```python
for i in range(1_000_000):
    x = SmallObject()
```

Nếu mỗi lần đều phải gọi trực tiếp hệ điều hành để xin memory thì sẽ rất tốn.

Do đó CPython có các tầng allocator để quản lý hiệu quả hơn.

---

# 12. `pymalloc`

Với CPython, một thành phần quan trọng là:

```text
pymalloc
```

Nó được tối ưu cho các allocation nhỏ.

Mô hình khái niệm:

```text
Python object
      ↓
pymalloc
      ↓
memory pools
      ↓
larger memory arenas
```

Không cần nhớ chi tiết implementation ngay.

Điều quan trọng cần hiểu:

> CPython không nhất thiết yêu cầu Operating System cấp phát memory cho từng Python object nhỏ.

Nó có thể quản lý và tái sử dụng các vùng memory đã được cấp phát.

---

# 13. Arena → Pool → Block

Đây là một khái niệm nổi tiếng khi học CPython memory allocator.

Mô hình đơn giản:

```text
Arena
└── Pool
    ├── Block
    ├── Block
    ├── Block
    └── ...
```

Có thể hình dung:

```text
Large memory area
       │
       ▼
┌──────────────────────────────┐
│            Arena             │
│                              │
│ ┌────────┐ ┌────────┐       │
│ │ Pool   │ │ Pool   │ ...   │
│ │        │ │        │       │
│ │ blocks │ │ blocks │       │
│ └────────┘ └────────┘       │
└──────────────────────────────┘
```

Đây là cách CPython tối ưu allocation cho object nhỏ.

---

# 14. Tại sao Memory không giảm ngay?

Một hiện tượng rất dễ gặp:

```python
import sys

data = [i for i in range(1_000_000)]

del data
```

Bạn có thể thấy process vẫn sử dụng khá nhiều memory.

Tại sao?

Vì:

```text
Object freed
       ≠
Process memory immediately returned to OS
```

Có thể xảy ra:

```text
Python object
    ↓
released
    ↓
allocator giữ lại memory
    ↓
reuse cho object tương lai
```

Đây là lý do nhìn memory của process đôi khi gây nhầm lẫn.

---

# 15. Object được giải phóng ≠ RAM lập tức trả về OS

Đây là một nguyên tắc rất quan trọng:

```text
Object no longer needed
        ↓
Python allocator can reclaim/reuse memory
        ↓
OS may or may not immediately see RSS decrease
```

Ví dụ:

```python
data = [b"x" * 1024 for _ in range(100_000)]

del data
```

Không nên kết luận:

> "del rồi thì RAM process chắc chắn giảm ngay."

Không nhất thiết.

---

# 16. Python có Memory Leak không?

Có.

Nhưng cần phân biệt hai loại vấn đề.

### Loại 1 — Object vẫn còn reference

```python
cache = []

def add():
    cache.append(large_object())
```

Đây là vấn đề logic:

```text
cache
 ↓
object
 ↓
object
 ↓
object
 ↓
...
```

GC không thể xóa những object này nếu chúng vẫn reachable.

---

### Loại 2 — Allocator giữ memory

Object có thể đã được giải phóng nhưng allocator giữ memory để tái sử dụng.

```text
Object freed
      ↓
allocator retains memory
      ↓
future allocations reuse it
```

Đây không nhất thiết là memory leak.

---

# 17. `sys.getsizeof()`

Python cung cấp:

```python
import sys

x = []
print(sys.getsizeof(x))
```

Nó cho biết kích thước cơ bản của object theo góc nhìn Python.

Nhưng:

> **Không phải tổng memory mà toàn bộ object graph đang sử dụng.**

Ví dụ:

```python
data = ["hello"] * 100
```

`sys.getsizeof(data)` không đơn giản bằng tổng kích thước của tất cả `"hello"` theo cách bạn có thể tưởng tượng.

---

# 18. Shallow Size vs Deep Size

Ví dụ:

```python
data = {
    "name": "Alice",
    "scores": [90, 80, 70]
}
```

Ta có:

```text
dict
├── name ───► "Alice"
└── scores ─► list
                ├── 90
                ├── 80
                └── 70
```

`sys.getsizeof(data)` chủ yếu phản ánh kích thước của **dict object itself**.

Nó không tự động tính toàn bộ object graph theo cách "deep memory size".

Đây là lý do profiling memory là một chủ đề riêng.

---

# 19. `tracemalloc`

Python có module:

```python
import tracemalloc
```

Dùng để theo dõi memory allocations của Python.

Ví dụ cơ bản:

```python
import tracemalloc

tracemalloc.start()

data = [i for i in range(100_000)]

snapshot = tracemalloc.take_snapshot()

for stat in snapshot.statistics("lineno")[:5]:
    print(stat)
```

Sau này ở phần **Profiling & Performance**, chúng ta sẽ học `tracemalloc` rất sâu.

---

# 20. Một thí nghiệm quan trọng

Chạy:

```python
import sys

x = []

print("1:", sys.getrefcount(x))

y = x

print("2:", sys.getrefcount(x))

z = x

print("3:", sys.getrefcount(x))

del y

print("4:", sys.getrefcount(x))

del z

print("5:", sys.getrefcount(x))
```

Bạn sẽ thấy số reference thay đổi.

Nhưng có một chi tiết quan trọng:

```python
sys.getrefcount(x)
```

bản thân việc truyền `x` vào function có thể tạo thêm một reference tạm thời.

Do đó số bạn nhìn thấy thường **cao hơn một reference** so với trực giác đơn giản.

Đừng dùng nó như một phép đo tuyệt đối về implementation internals.

---

# 21. `None` và object lifetime

Ví dụ:

```python
x = SomeLargeObject()

x = None
```

Điều gì xảy ra?

Name:

```text
x
```

không còn trỏ tới object cũ.

```text
x ─────► None

SomeLargeObject
       ↑
       ?
```

Nếu không còn reference nào khác, object có thể trở nên unreachable.

---

# 22. Một lỗi phổ biến trong cache

Ví dụ:

```python
cache = {}

def load(key):
    if key not in cache:
        cache[key] = create_large_object()

    return cache[key]
```

Cache có thể phát triển vô hạn:

```text
cache
├── key1 → object
├── key2 → object
├── key3 → object
├── ...
└── key999999 → object
```

Đây có thể tạo ra memory growth.

Giải pháp có thể là:

```text
LRU Cache
TTL Cache
Bounded Cache
Weak Reference
```

Chúng ta sẽ gặp những khái niệm này ở các phần sau.

---

# 23. Weak Reference — preview

Python có:

```python
import weakref
```

Weak reference cho phép tham chiếu tới object mà không giữ object sống theo cách của strong reference.

Ví dụ khái niệm:

```text
strong reference
      │
      ▼
    Object
```

vs:

```text
weak reference
      │
      └──────► Object
```

Weak reference rất hữu ích trong:

* Cache
* Registry
* Framework
* Observer
* Object tracking

Chúng ta sẽ chưa đi sâu hôm nay.

---

# 24. Memory Management và Garbage Collection

Hai khái niệm này **không giống nhau**.

### Memory Management

Là khái niệm rộng:

```text
Allocation
Reference
Object lifetime
Deallocation
Allocator
Memory reuse
```

### Garbage Collection

Là một cơ chế cụ thể để xử lý những object khó thu hồi bằng Reference Counting, đặc biệt là **reference cycles** trong CPython.

Mô hình:

```text
Memory Management
│
├── Allocation
├── Reference Counting
├── Garbage Collection
├── Allocator
└── Memory Reuse
```

Ở Buổi 3 chúng ta sẽ tập trung vào:

> **Reference Counting**

Sau đó Buổi 4:

> **Garbage Collector**

---

# 25. Một ví dụ về Circular Reference

Ví dụ:

```python
a = []
b = []

a.append(b)
b.append(a)
```

Ta có:

```text
a ─────► list A
          │
          ▼
        list B
          │
          ▼
          A
```

Tức là:

```text
A ───► B
▲     │
└─────┘
```

Nếu:

```python
del a
del b
```

thì vẫn có một cycle bên trong:

```text
A ───► B
▲     │
└─────┘
```

Reference Counting đơn thuần gặp khó khăn với trường hợp này.

Đây chính là lý do CPython có **cyclic garbage collector**.

---

# 26. Mental Model của Memory Management

Bạn nên ghi nhớ sơ đồ này:

```text
Python Code
     │
     ▼
Names / References
     │
     ▼
Python Objects
     │
     ▼
Python-managed Heap
     │
     ▼
Memory Allocator
     │
     ├── pymalloc
     │
     └── system allocator
             │
             ▼
        Operating System
```

Và object lifecycle:

```text
Create
  ↓
Allocate memory
  ↓
Initialize object
  ↓
Reference exists
  ↓
Use object
  ↓
References decrease
  ↓
Object becomes unreachable
  ↓
Cleanup / reclaim
  ↓
Memory may be reused
```

---

# 🧠 27. Những điều cần nhớ

### ① Python sử dụng Automatic Memory Management

Bạn không thường xuyên phải tự `free()` object.

### ② Name ≠ Object

```python
x = []
```

là:

```text
x ───► object
```

### ③ `del x` không nhất thiết xóa object

Nó loại bỏ reference/name `x`.

### ④ Object có metadata

Ở mức khái niệm:

```text
object
├── reference count
├── type
└── data
```

### ⑤ Python có allocator riêng

Đặc biệt trong CPython có:

```text
pymalloc
arena
pool
block
```

### ⑥ Object được giải phóng không đồng nghĩa RAM trả ngay OS

Allocator có thể giữ lại memory để tái sử dụng.

### ⑦ Memory leak vẫn có thể xảy ra

Đặc biệt khi chương trình giữ reference không cần thiết:

```text
global
cache
container
closure
registry
```

### ⑧ GC ≠ toàn bộ Memory Management

GC chỉ là một phần trong hệ thống quản lý memory.

---

# 🧪 Bài tập Buổi 2

## Bài 1 — Reference

Dự đoán:

```python
x = []
y = x
z = y

del x
del y

print(z)
```

**Câu hỏi:** Object list có bị giải phóng sau `del x`, `del y` không? Vì sao?

---

## Bài 2 — Hai object

```python
a = []
b = []

print(a is b)
print(a == b)
```

Giải thích sự khác nhau giữa:

```text
identity
vs
value/equality
```

---

## Bài 3 — Object lifetime

```python
class User:
    pass

user = User()

other = user

del user

print(other)
```

Vẽ sơ đồ reference trước và sau `del user`.

---

## Bài 4 — Memory

Giải thích tại sao:

```python
data = [i for i in range(1_000_000)]

del data
```

**không đảm bảo** process trả ngay toàn bộ memory về Operating System.

---

## Bài 5 — Circular Reference

Phân tích:

```python
a = []
b = []

a.append(b)
b.append(a)

del a
del b
```

Vẽ object graph:

```text
?
```

và giải thích tại sao đây là trường hợp đặc biệt đối với reference counting.

---

# 🎯 Buổi 3

Tiếp theo chúng ta sẽ đi thẳng vào:

# **Reference Counting — Cơ chế quan trọng nhất của CPython Memory Management**

Chúng ta sẽ mổ xẻ:

```text
PyObject
   │
   ├── reference count
   ├── type pointer
   └── object data
```

và thực hành với:

```python
sys.getrefcount()
```

cùng các tình huống:

```text
Assignment
Function argument
Return value
Container
Local variable
Global variable
del
Circular reference
```

Sau Buổi 3, bạn sẽ hiểu **tại sao một object chết**, thay vì chỉ biết Python "tự động quản lý memory".
