# 🐍 Buổi 4 — Garbage Collector trong Python

Ở Buổi 3 ta đã thấy:

> **Reference Counting không đủ để xử lý Circular Reference.**

Buổi này chúng ta tìm hiểu cơ chế thứ hai của CPython:

```text
Reference Counting
        +
Garbage Collector (GC)
        ↓
Quản lý vòng đời object
```

---

# 1. Vì sao cần Garbage Collector?

Xét ví dụ:

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

Sau `del`:

```text
a ──► Node A
       │
       ▼
      Node B
       │
       └──────► Node A
```

Hai object vẫn tham chiếu lẫn nhau.

Conceptually:

```text
Node A refcount = 1
Node B refcount = 1
```

Nhưng chương trình không còn reference bên ngoài tới chúng.

```text
Program
   │
   └──X──► Node A ◄────► Node B
```

Đây là **cycle**.

Reference Counting không thể tự giải quyết:

```text
refcount > 0
```

nhưng:

```text
object không còn reachable từ các root của chương trình
```

→ cần Garbage Collector.

---

# 2. Garbage Collector là gì?

Garbage Collector là cơ chế phát hiện những object không còn cần thiết, đặc biệt là **reference cycles**, để chúng có thể được giải phóng.

Có thể hình dung:

```text
          Python Objects
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
 Reference Counting     GC
        │                │
        │                ▼
        │          Detect cycles
        │                │
        └───────┬────────┘
                ▼
        Object Lifetime
```

Trong CPython:

```text
Reference Counting
        ↓
xử lý phần lớn object
        +
Cyclic GC
        ↓
xử lý cycle
```

---

# 3. Module `gc`

Python cung cấp module:

```python
import gc
```

Ví dụ:

```python
import gc

print(gc.isenabled())
```

Thông thường:

```text
True
```

Có thể bật/tắt GC:

```python
gc.disable()
gc.enable()
```

Nhưng **không nên tùy tiện disable GC trong application production** nếu chưa hiểu rõ lifecycle của object.

---

# 4. `gc.collect()`

Đây là API rất quan trọng:

```python
gc.collect()
```

Nó yêu cầu garbage collector thực hiện collection.

Ví dụ:

```python
import gc


class Node:
    pass


a = Node()
b = Node()

a.other = b
b.other = a

del a
del b

collected = gc.collect()

print(collected)
```

`gc.collect()` trả về số lượng unreachable objects được thu gom trong lần collection đó.

Ví dụ có thể nhận:

```text
2
```

Không nên phụ thuộc tuyệt đối vào con số trong các ví dụ phức tạp, vì kết quả phụ thuộc vào trạng thái GC và các object khác đang tồn tại.

---

# 5. Reference Counting vs GC

Đây là phần quan trọng nhất của buổi này.

## Reference Counting

Theo dõi:

```text
Có bao nhiêu reference trực tiếp tới object?
```

Ví dụ:

```python
x = []
y = x
```

```text
x ─┐
   ├──► []
y ─┘
```

Có nhiều reference.

Khi:

```python
del x
del y
```

reference count có thể về `0`.

Object có thể được deallocate.

---

# 6. Nhưng Circular Reference thì sao?

```python
a = []
b = []

a.append(b)
b.append(a)
```

Graph:

```text
a
│
▼
List A ─────► List B
  ▲             │
  └─────────────┘
```

Sau:

```python
del a
del b
```

Không còn variable `a`, `b`.

Nhưng:

```text
List A ─────► List B
  ▲             │
  └─────────────┘
```

vẫn còn cycle.

GC sẽ phát hiện rằng nhóm object này không còn reachable từ các root phù hợp và có thể thu gom chúng.

---

# 7. Generational Garbage Collection

CPython không đơn giản là:

```text
scan toàn bộ object
→ tìm garbage
```

Mà sử dụng ý tưởng **generational garbage collection**.

Ý tưởng:

> Object sống lâu thường có xu hướng tiếp tục sống lâu.

Ví dụ:

```text
temporary object
     ↓
sống vài milliseconds

request object
     ↓
sống vài seconds

global configuration
     ↓
sống suốt process
```

Vì vậy không cần kiểm tra mọi object liên tục.

---

# 8. Generation

Ở mức khái niệm, các object GC-tracked được tổ chức theo generations.

Mô hình truyền thống:

```text
Generation 0
     ↓
Generation 1
     ↓
Generation 2
```

Object mới thường bắt đầu ở generation trẻ.

Nếu sống sót qua các lần collection:

```text
Gen 0
 ↓
Gen 1
 ↓
Gen 2
```

Object càng lâu đời thì càng ít bị kiểm tra thường xuyên.

---

# 9. Tại sao làm vậy?

Giả sử application crawler tạo:

```text
1.000.000 temporary objects
```

Trong đó:

```text
999.000 objects
```

chỉ tồn tại rất ngắn.

Nếu mỗi lần GC phải kiểm tra toàn bộ:

```text
1.000.000 objects
```

→ rất tốn chi phí.

Generational hypothesis:

```text
young objects
    ↓
chết nhiều

old objects
    ↓
chết ít
```

Do đó:

```text
GC thường xuyên
    ↓
Gen 0

GC ít thường xuyên hơn
    ↓
Gen 1

GC hiếm hơn
    ↓
Gen 2
```

---

# 10. Xem trạng thái GC

Python cung cấp:

```python
gc.get_count()
```

Ví dụ:

```python
import gc

print(gc.get_count())
```

Có thể nhận tuple dạng:

```text
(x, y, z)
```

Đây là các bộ đếm liên quan đến hoạt động của GC.

Bạn có thể thử:

```python
import gc

for i in range(10):
    objects = []

    for _ in range(1000):
        objects.append({})

    print(gc.get_count())
```

Bạn sẽ thấy các giá trị thay đổi theo hoạt động allocation và collection.

---

# 11. GC Threshold

Có thể xem threshold:

```python
import gc

print(gc.get_threshold())
```

Ví dụ một CPython build có thể trả về một tuple như:

```text
(700, 10, 10)
```

**Không nên coi các con số này là cố định cho mọi phiên bản/build Python.**

Ý tưởng là GC sử dụng các ngưỡng để quyết định khi nào thực hiện collection.

Có thể thay đổi:

```python
gc.set_threshold(...)
```

Nhưng đây là tuning nâng cao.

Đừng bắt đầu optimization bằng cách chỉnh threshold.

---

# 12. `gc.get_objects()`

Có thể lấy các object mà GC đang theo dõi:

```python
objects = gc.get_objects()

print(len(objects))
```

Hoặc:

```python
for obj in gc.get_objects():
    print(type(obj))
```

⚠️ Không nên làm điều này tùy tiện trong production.

Có thể có **rất nhiều object**.

---

# 13. Object nào được GC track?

Đây là một nuance quan trọng.

Không phải mọi Python object đều nhất thiết phải được cyclic GC track.

Bạn có thể kiểm tra:

```python
gc.is_tracked(obj)
```

Ví dụ:

```python
import gc

x = []

print(gc.is_tracked(x))
```

Có thể:

```text
True
```

Đối với các container có khả năng tham gia cycle, GC tracking đặc biệt quan trọng.

---

# 14. `gc.get_referents()`

Một công cụ rất hữu ích để nghiên cứu object graph:

```python
gc.get_referents(obj)
```

Ví dụ:

```python
import gc

x = [1, 2, 3]

print(gc.get_referents(x))
```

Bạn có thể hiểu nó như:

```text
object
   │
   ▼
những object mà object này reference
```

Ví dụ:

```text
list
 ├──► 1
 ├──► 2
 └──► 3
```

`get_referents()` giúp quan sát hướng:

```text
A → B
```

---

# 15. `gc.get_referrers()`

Ngược lại:

```python
gc.get_referrers(obj)
```

cho biết các object đang reference tới `obj`.

Ví dụ:

```python
import gc

x = []

y = [x]

refs = gc.get_referrers(x)

print(refs)
```

Ta có:

```text
y
│
▼
[x]
 │
 └──► x
```

`get_referrers(x)` có thể tìm thấy container chứa reference tới `x`.

---

# 16. Nhưng `get_referrers()` cực kỳ dễ hiểu sai

Đây là một công cụ debugging/introspection, **không phải API business logic**.

Ví dụ:

```python
gc.get_referrers(x)
```

chính thao tác debugging cũng có thể tạo thêm temporary references.

Ngoài ra interpreter/frame/debugger có thể tạo reference mà bạn không quan tâm.

Vì vậy:

```python
gc.get_referrers()
```

không nên được hiểu đơn giản là:

> "Đây chính xác là tất cả nguyên nhân khiến object của tôi không bị giải phóng."

Hãy dùng nó để **điều tra reference graph**, không phải làm logic ứng dụng.

---

# 17. Một thí nghiệm hoàn chỉnh

Hãy chạy:

```python
import gc


class Node:
    def __init__(self, name):
        self.name = name
        self.other = None


a = Node("A")
b = Node("B")

a.other = b
b.other = a

print("GC tracked:")
print(gc.is_tracked(a))
print(gc.is_tracked(b))

del a
del b

print("Collecting...")

collected = gc.collect()

print("Collected:", collected)
```

Điều quan trọng cần hiểu:

```text
a ──► A ──► B
          ▲    │
          └────┘
```

Sau:

```python
del a
del b
```

thì:

```text
Python roots
     │
     X
     │
     ▼
    A ◄──► B
```

Cycle vẫn tồn tại.

GC phát hiện và xử lý cycle.

---

# 18. GC không phải "memory manager duy nhất"

Đây là mental model chính xác hơn:

```text
                 Python Program
                       │
                       ▼
                  References
                       │
              ┌────────┴────────┐
              ▼                 ▼
     Reference Counting    Cyclic GC
              │                 │
              │                 │
              ▼                 ▼
       refcount → 0        detect cycles
              │                 │
              └────────┬────────┘
                       ▼
               Object lifetime
```

Trong CPython:

### Reference Counting

Giỏi xử lý:

```text
A ──► object
```

khi reference cuối cùng biến mất:

```text
refcount = 0
```

### Cyclic GC

Giỏi xử lý:

```text
A ──► B
▲     │
└─────┘
```

khi cycle không còn reachable từ bên ngoài.

---

# 19. Garbage ≠ object có refcount = 0

Đây là điểm rất quan trọng.

Trong CPython, object có:

```text
refcount == 0
```

thường có thể được xử lý ngay bởi reference counting.

Còn cyclic garbage có thể có:

```text
refcount > 0
```

nhưng toàn bộ cycle không còn reachable.

Ví dụ:

```text
A.refcount = 1
B.refcount = 1

A ──► B
▲     │
└─────┘
```

Không có external reference.

GC mới là cơ chế phát hiện tình trạng này.

---

# 20. `__del__` và Garbage Collector

Ví dụ:

```python
class Resource:
    def __del__(self):
        print("destroyed")
```

Có thể thấy:

```python
x = Resource()

del x
```

Nhưng **đừng thiết kế resource management dựa trên `__del__`**.

Không nên:

```python
class Database:
    def __del__(self):
        self.connection.close()
```

Thay vào đó:

```python
with database_connection() as connection:
    ...
```

Tức là dùng:

```text
Context Manager
    ↓
__enter__
    ↓
work
    ↓
__exit__
```

để quản lý resource một cách xác định.

---

# 21. GC và `weakref`

Một cách khác để tránh giữ object sống ngoài ý muốn là:

```python
weakref
```

Ví dụ concept:

```text
Strong reference
    ↓
Object
    ↑
Weak reference
```

Weak reference không giữ object sống chỉ vì bản thân weak reference tồn tại.

Điều này rất hữu ích cho:

* cache
* registry
* observer
* framework
* object graph

Đây sẽ liên kết rất mạnh với các bài:

```text
Descriptor
Plugin Registry
Observer Pattern
Framework Design
Cache
```

---

# 22. GC và crawler của chúng ta

Đây là phần đặc biệt quan trọng với project crawler.

Giả sử crawler có:

```text
Crawler
   │
   ├── Scheduler
   │
   ├── Queue
   │
   ├── Workers
   │
   ├── Cache
   │
   └── Parser Registry
```

Nếu vô tình tạo:

```text
Worker
  │
  ▼
Crawler
  │
  ▼
Worker
```

thì:

```text
Worker ──► Crawler ──► Worker
```

có thể tạo cycle.

Nhưng **cycle không tự động có nghĩa là memory leak**.

Nếu cycle không còn reachable và GC có thể thu gom nó:

```text
cycle
  ↓
unreachable
  ↓
GC
  ↓
collect
```

thì không phải leak.

Memory leak nguy hiểm hơn là:

```text
Global Registry
      │
      ▼
Worker
      │
      ▼
Crawler
      │
      ▼
Huge Response Cache
      │
      ▼
100,000 objects
```

Registry vẫn giữ reference:

```text
Root
 ↓
Registry
 ↓
Worker
 ↓
...
```

→ object vẫn **reachable**.

GC không thể tự ý xóa.

---

# 23. Đây là lý do "GC không sửa được mọi memory leak"

Sai lầm phổ biến:

> "Python có Garbage Collector nên Python không bị memory leak."

Không đúng.

Có thể có:

```text
Memory Leak
```

do application giữ reference ngoài ý muốn.

Ví dụ:

```python
cache = {}

def process(response):
    cache[id(response)] = response
```

Nếu `cache` không bao giờ được cleanup:

```text
cache
 ├── response 1
 ├── response 2
 ├── response 3
 ├── ...
 └── response 1,000,000
```

Tất cả vẫn reachable.

GC nhìn thấy:

```text
Root → cache → response
```

nên **không được phép xóa**.

---

# 24. Ba khái niệm phải phân biệt

```text
Object không còn reference
        ↓
refcount = 0
        ↓
có thể deallocate
```

Khác với:

```text
Cycle
 ↓
refcount > 0
 ↓
nhưng unreachable
 ↓
GC có thể collect
```

Và khác nữa:

```text
Object vẫn reachable
 ↓
GC không thể collect
 ↓
application phải release reference
```

---

# 25. Mental Model của Buổi 4

Hãy ghi nhớ:

```text
                 OBJECT
                   │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
   Reference Counting    Cyclic GC
          │                 │
          ▼                 ▼
 refcount == 0?        Có cycle?
          │                 │
          ▼                 ▼
    deallocate          analyze graph
                            │
                            ▼
                     unreachable cycle?
                            │
                         YES
                            │
                            ▼
                         collect
```

Và:

```text
GC KHÔNG xóa object chỉ vì
object "có vẻ không dùng nữa".

GC phải chứng minh object
không còn reachable theo cơ chế của nó.
```

---

# 🧪 Bài tập Buổi 4

## Bài 1 — Cycle

Tạo:

```python
class Node:
    pass
```

Sau đó tạo:

```text
A → B
↑   ↓
└───┘
```

Xóa toàn bộ reference bên ngoài và thử:

```python
gc.collect()
```

Quan sát kết quả.

---

## Bài 2 — `gc.get_count()`

Viết:

```python
import gc

for i in range(100_000):
    data = [i, i + 1, i + 2]

print(gc.get_count())
```

Thử thay đổi số lượng object.

Quan sát GC hoạt động như thế nào.

---

## Bài 3 — Reference graph

Tạo:

```python
x = []
y = [x]
z = [y]
```

Sau đó sử dụng:

```python
gc.get_referrers(x)
gc.get_referents(y)
```

và vẽ:

```text
x
↑
y
↑
z
```

---

## Bài 4 — Memory leak giả lập

Tạo:

```python
cache = []

for i in range(100_000):
    cache.append({
        "id": i,
        "data": "x" * 1000,
    })
```

Sau đó:

```python
import gc

gc.collect()
```

Giải thích:

> Tại sao `gc.collect()` không thể giải phóng phần lớn memory của `cache`?

**Đáp án:** vì `cache` vẫn giữ strong references tới các object.

---

# 🎯 Sau Buổi 4

Bạn đã có nền tảng:

```text
Buổi 1
Python Object Model
        ↓
Buổi 2
Memory Management
        ↓
Buổi 3
Reference Counting
        ↓
Buổi 4
Garbage Collector
```

Từ đây ta có thể bước sang một chủ đề cực kỳ thực tế:

# Buổi 5 — Shallow Copy

Chúng ta sẽ giải quyết câu hỏi:

```python
a = [[1, 2], [3, 4]]

b = a.copy()

b[0].append(99)

print(a)
```

Tại sao `a` **cũng bị thay đổi**?

Và từ đó đi sâu vào:

```text
Assignment
    ↓
Reference
    ↓
Shallow Copy
    ↓
Deep Copy
    ↓
Object Graph
    ↓
copy.copy()
    ↓
copy.deepcopy()
```

Đây là bước nối trực tiếp giữa **memory model → object graph → copy semantics**.
