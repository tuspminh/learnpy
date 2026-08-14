# Dataclass Deep Dive — Buổi 24

# Pickle, `copy`, `deepcopy` và Dataclass

Hôm nay kết thúc **Phần III — Serialization**.

Chúng ta sẽ phân biệt thật rõ 4 cơ chế:

```text
asdict()
copy.copy()
copy.deepcopy()
pickle.dumps()
```

vì chúng nhìn khá giống nhau nhưng **mục đích hoàn toàn khác nhau**.

---

# 1. Bức tranh tổng thể

Giả sử:

```python
from dataclasses import dataclass


@dataclass
class User:
    name: str
    age: int
```

Ta có object:

```python
user = User("Alice", 20)
```

Có 4 hướng xử lý:

```text
                    User object
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
     asdict()         copy()          pickle
        │               │                │
        ▼               ▼                ▼
      dict          new object       bytes
                        │
                        ▼
                   deepcopy()
```

---

# 2. `asdict()` không phải copy object thông thường

Ta đã học:

```python
from dataclasses import asdict

data = asdict(user)
```

Kết quả:

```python
{
    "name": "Alice",
    "age": 20,
}
```

Kiểu:

```python
type(data)
```

là:

```text
dict
```

Nó không còn là:

```python
User
```

mà là một **data representation**.

---

# 3. `copy.copy()`

Python có:

```python
import copy
```

Shallow copy:

```python
user2 = copy.copy(user)
```

Ta có:

```text
user
 │
 ▼
User object A

user2
 │
 ▼
User object B
```

Hai object khác nhau:

```python
user is user2
```

→

```text
False
```

Nhưng các object bên trong có thể được **chia sẻ**.

---

# 4. Ví dụ với nested object

```python
from dataclasses import dataclass


@dataclass
class Address:
    city: str


@dataclass
class User:
    name: str
    address: Address
```

:

```python
address = Address("HCM")

user1 = User(
    "Alice",
    address,
)
```

Shallow copy:

```python
import copy

user2 = copy.copy(user1)
```

Ta có:

```text
user1 ────────┐
              ▼
          Address A
              ▲
              │
user2 ────────┘
```

Hai User khác nhau:

```python
user1 is user2
```

→ `False`

Nhưng:

```python
user1.address is user2.address
```

→ `True`

---

# 5. Đây chính là shallow copy

```text
Outer object
     │
     ├── copied
     │
     └── nested object
             │
             └── shared
```

Hay:

```text
copy.copy()
    ↓
copy outer
    ↓
reuse inner references
```

---

# 6. `deepcopy()`

Bây giờ:

```python
user2 = copy.deepcopy(user1)
```

Kết quả:

```text
user1
 │
 └── Address A


user2
 │
 └── Address B
```

Kiểm tra:

```python
user1 is user2
```

→ `False`

và:

```python
user1.address is user2.address
```

→ `False`

---

# 7. Deep copy

Mental model:

```text
copy.copy()

User A
  │
  └── Address A
           ▲
           │
       shared


copy.deepcopy()

User A
  │
  └── Address A

User B
  │
  └── Address B
```

Toàn bộ object graph được copy theo quy tắc của `copy` module.

---

# 8. Dataclass không có cơ chế copy riêng

Một điều quan trọng:

```python
copy.copy(user)
```

không phải:

```text
Dataclass.copy()
```

Python sử dụng generic copy machinery.

Dataclass chủ yếu cung cấp:

```text
__init__
__repr__
__eq__
...
```

Còn copy được xử lý bởi:

```python
copy
```

module.

---

# 9. `replace()` của Dataclass

Dataclass có một cơ chế rất hữu ích:

```python
from dataclasses import replace
```

Ví dụ:

```python
user2 = replace(
    user1,
    age=21,
)
```

Kết quả:

```text
user1
User("Alice", 20)

user2
User("Alice", 21)
```

Đây không phải `deepcopy()`.

---

# 10. `replace()` gần với immutable-style programming

Ví dụ:

```python
@dataclass(frozen=True)
class User:
    name: str
    age: int
```

Không thể:

```python
user.age = 21
```

Nhưng có thể:

```python
user2 = replace(
    user,
    age=21,
)
```

Mental model:

```text
old object
    │
    │ replace
    ▼
new object
```

Đây là pattern rất quan trọng khi xây:

* state
* configuration
* event
* immutable model

---

# 11. So sánh `copy()` và `replace()`

### `copy.copy`

```python
user2 = copy.copy(user)
```

Mục tiêu:

> sao chép object.

### `replace`

```python
user2 = replace(
    user,
    age=21,
)
```

Mục tiêu:

> tạo instance mới với một số field thay đổi.

Đây là hai abstraction khác nhau.

---

# 12. `asdict()` và `deepcopy()` có liên quan

Một điểm rất quan trọng từ dataclasses:

`asdict()` xử lý nested dataclass và với các object không phải dataclass thì có cơ chế copy tương ứng.

Ví dụ:

```python
@dataclass
class User:
    name: str
    tags: list[str]
```

:

```python
user = User(
    "Alice",
    ["python", "rust"],
)
```

Sau:

```python
data = asdict(user)
```

ta có:

```text
user.tags
    ↓
original list

data["tags"]
    ↓
copied list
```

Không phải cùng một list.

---

# 13. Vì vậy `asdict()` không phải view

Đừng nghĩ:

```python
data = asdict(user)
```

là:

```text
dict view của object
```

Nó tạo ra một representation mới.

Đó là lý do `asdict()` có thể tốn memory với object graph lớn.

---

# 14. Performance của `asdict()`

Giả sử:

```text
Novel
 ├── Chapter × 1000
 │     └── Image × 10
 └── metadata
```

Ta có:

```python
data = asdict(novel)
```

Có thể tạo một graph Python mới rất lớn.

Sau đó:

```python
json.dumps(data)
```

lại duyệt graph đó.

Pipeline:

```text
Original
   ↓
asdict()
   ↓
New graph
   ↓
json.dumps()
   ↓
JSON
```

Đây là một trong những lý do `orjson` có thể hấp dẫn trong workload serialization.

---

# 15. `pickle` là gì?

`pickle` là cơ chế serialization riêng của Python.

```python
import pickle
```

Ví dụ:

```python
data = pickle.dumps(user)
```

Kết quả:

```text
bytes
```

Khác JSON:

```text
JSON
 ↓
text-oriented format
```

Pickle:

```text
Python object
 ↓
Python-specific serialized representation
```

---

# 16. Pickle có thể khôi phục object

```python
payload = pickle.dumps(user)

user2 = pickle.loads(payload)
```

Kết quả:

```python
type(user2)
```

là:

```text
User
```

Không cần:

```python
User(**data)
```

Pickle có thể tái tạo object Python.

---

# 17. JSON vs Pickle

JSON:

```text
User
 ↓
dict-like data
 ↓
JSON
 ↓
language-independent
```

Pickle:

```text
User
 ↓
pickle
 ↓
Python-specific bytes
 ↓
User
```

Do đó:

### JSON

Phù hợp:

```text
API
Queue
JavaScript
Go
Rust
Java
```

### Pickle

Phù hợp hơn với:

```text
Python ↔ Python
local persistence
cache
internal tooling
```

---

# 18. Pickle không phải format interoperability

Ví dụ:

```text
Python
   ↓
pickle
   ↓
Rust
```

Không phải mục tiêu tự nhiên của pickle.

Trong khi:

```text
Python
   ↓
JSON
   ↓
Rust
```

là chuyện rất bình thường.

---

# 19. Pickle giữ được nhiều thông tin hơn

JSON:

```python
User(
    name="Alice",
    age=20,
)
```

thường trở thành:

```json
{
    "name": "Alice",
    "age": 20
}
```

Pickle cố gắng giữ Python object semantics nhiều hơn.

Ví dụ:

```text
class identity
object graph
references
Python types
```

Đây là lý do pickle mạnh hơn nhưng cũng nguy hiểm hơn.

---

# 20. Object graph

Đây là một khái niệm quan trọng.

Ví dụ:

```python
address = Address("HCM")

user1 = User(
    "Alice",
    address,
)

user2 = User(
    "Bob",
    address,
)
```

Graph:

```text
       Address
       /     \
      /       \
   User A   User B
```

`user1.address` và `user2.address` cùng trỏ đến một object.

---

# 21. Pickle có thể bảo toàn sharing

Một trong những đặc điểm quan trọng của pickle là nó có thể lưu thông tin về object references trong object graph.

Ý tưởng:

```text
User A ─────┐
            ▼
         Address
            ▲
            │
User B ─────┘
```

Sau khi unpickle, sharing có thể được tái tạo:

```text
User A ─────┐
            ▼
         Address'
            ▲
            │
User B ─────┘
```

chứ không nhất thiết tạo hai Address độc lập.

Đây là điểm khác biệt quan trọng so với một số dạng data serialization đơn giản.

---

# 22. Circular reference

Python object có thể tham chiếu vòng:

```python
@dataclass
class Node:
    name: str
    parent: object | None = None
```

Ví dụ:

```python
a = Node("A")
b = Node("B")

a.parent = b
b.parent = a
```

Graph:

```text
A → B
↑   ↓
└───┘
```

JSON tree serialization thông thường gặp vấn đề với circular reference.

Pickle được thiết kế để xử lý object graph phức tạp hơn.

---

# 23. `deepcopy()` cũng có memoization

Một điểm deep dive:

```python
copy.deepcopy(obj)
```

không đơn giản là:

```text
recursive copy forever
```

Nó sử dụng một `memo` mapping để theo dõi object đã được copy.

Điều này giúp xử lý:

```text
shared references
circular references
```

Ví dụ:

```text
A → B
↑   ↓
└───┘
```

`deepcopy()` có thể tránh infinite recursion nhờ memo.

---

# 24. `deepcopy()` không phải serialization

Đây là distinction rất quan trọng.

### `deepcopy`

```text
Python object
     ↓
Python object mới
```

### `pickle`

```text
Python object
     ↓
bytes
```

### `JSON`

```text
Python object
     ↓
JSON-compatible representation
     ↓
JSON text/bytes
```

---

# 25. Bảng so sánh

| Cơ chế           | Input     | Output    | Mục tiêu             |
| ---------------- | --------- | --------- | -------------------- |
| `asdict()`       | Dataclass | dict      | data representation  |
| `copy.copy()`    | Object    | Object    | shallow copy         |
| `deepcopy()`     | Object    | Object    | deep copy            |
| `pickle.dumps()` | Object    | bytes     | Python serialization |
| `replace()`      | Dataclass | Dataclass | modified copy        |

---

# 26. Security — phần cực kỳ quan trọng

Không bao giờ xem:

```python
pickle.loads(data)
```

là:

```text
parse data an toàn
```

Nếu attacker kiểm soát pickle payload, việc unpickle có thể dẫn tới **arbitrary code execution**.

Do đó:

```text
Internet
 ↓
untrusted pickle
 ↓
pickle.loads()
```

là một pattern cực kỳ nguy hiểm.

---

# 27. Đừng dùng Pickle cho Queue public

Ví dụ queue server:

```text
Client
 ↓
Internet
 ↓
Queue
 ↓
Worker
```

Không nên:

```text
pickle.loads(client_data)
```

nếu client không hoàn toàn trusted.

Thay vào đó:

```text
JSON
MessagePack
Protobuf
msgspec
```

hoặc một protocol có schema/validation phù hợp.

Đặc biệt với queue server mà bạn đang xây dựng:

```text
Producer
 ↓
serialized task
 ↓
Queue
 ↓
Worker
```

JSON/msgspec thường an toàn về mặt mô hình dữ liệu hơn pickle khi message đến từ boundary không tin cậy.

---

# 28. Pickle Versioning

Một vấn đề khác:

```text
pickle
```

gắn chặt với Python implementation và class definition.

Hôm nay:

```python
@dataclass
class User:
    name: str
    age: int
```

Ngày mai đổi:

```python
@dataclass
class User:
    username: str
```

Payload pickle cũ có thể không còn tương thích như bạn mong muốn.

---

# 29. JSON versioning

JSON:

```json
{
    "name": "Alice",
    "age": 20
}
```

dễ migrate hơn.

Ví dụ version:

```json
{
    "version": 2,
    "username": "Alice",
    "age": 20
}
```

Ta có thể viết:

```python
if version == 1:
    migrate_v1(data)

elif version == 2:
    load_v2(data)
```

Đây là cách phù hợp hơn cho:

```text
persistent data
API
queue
event
```

---

# 30. Dataclass + Pickle

Một trường hợp đơn giản:

```python
from dataclasses import dataclass
import pickle


@dataclass
class User:
    id: int
    name: str


user = User(
    1,
    "Alice",
)

payload = pickle.dumps(user)

restored = pickle.loads(payload)
```

Kiểm tra:

```python
print(restored)
```

có thể cho:

```text
User(id=1, name='Alice')
```

---

# 31. `frozen=True` không biến Pickle thành immutable storage

Ví dụ:

```python
@dataclass(frozen=True)
class User:
    id: int
    name: str
```

Pickle vẫn có thể serialize object.

Nhưng:

```text
frozen
```

chỉ liên quan đến semantics của instance trong Python.

Nó không có nghĩa:

```text
serialized bytes
=
tamper-proof
```

Đây là hai vấn đề hoàn toàn khác nhau.

---

# 32. Pickle và `__getstate__`

Python cho phép custom serialization behavior.

Ví dụ:

```python
class User:
    def __getstate__(self):
        ...
```

Pickle có thể sử dụng:

```text
__getstate__
__setstate__
```

để kiểm soát state.

Ví dụ concept:

```python
def __getstate__(self):
    return {
        "id": self.id,
        "name": self.name,
    }
```

Khi unpickle:

```python
def __setstate__(self, state):
    self.id = state["id"]
    self.name = state["name"]
```

---

# 33. Dataclass + custom pickle

Dataclass không ngăn bạn định nghĩa:

```python
__getstate__
__setstate__
```

Ví dụ:

```python
@dataclass
class User:
    id: int
    name: str

    def __getstate__(self):
        return {
            "id": self.id,
            "name": self.name,
        }
```

Điều này hữu ích khi object chứa:

```text
cache
connection
lock
file handle
runtime state
```

mà không muốn serialize tất cả.

---

# 34. Runtime state vs persistent state

Ví dụ:

```python
@dataclass
class CrawlerWorker:
    worker_id: int
    queue_name: str
    connection: object
```

Ta không muốn:

```text
connection
 ↓
pickle
```

Vì connection là runtime resource.

Ta muốn:

```text
Persistent state:
worker_id
queue_name

Runtime state:
connection
```

Đây là một distinction cực kỳ quan trọng khi thiết kế model.

---

# 35. `InitVar` và Pickle

Nhớ:

```python
@dataclass
class User:
    raw_password: InitVar[str]
```

`InitVar` không phải instance field thông thường.

Do đó:

```text
constructor input
```

khác:

```text
persistent state
```

Đây là lý do cần phân biệt:

```text
Input state
Stored state
Runtime state
Serialized state
```

---

# 36. Một architecture tốt

Trong project thực tế:

```text
             External Input
                   │
                   ▼
                 DTO
                   │
                   ▼
               Validation
                   │
                   ▼
                Entity
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
     Database     Queue      API
        │          │          │
       SQL        JSON       JSON
```

Không nên mặc định:

```text
mọi Dataclass
 ↓
pickle
```

---

# 37. Copy và Entity

Giả sử:

```python
@dataclass
class Novel:
    title: str
    chapters: list[str]
```

Ta có:

```python
novel2 = copy.copy(novel)
```

Sau đó:

```python
novel2.chapters.append(
    "Chapter 2"
)
```

thì `novel.chapters` cũng thay đổi.

Vì:

```text
novel.chapters
       ▲
       │
       └──── shared ──── novel2.chapters
```

Đây là bug cực kỳ phổ biến.

---

# 38. Deepcopy giải quyết được?

```python
novel2 = copy.deepcopy(novel)
```

Sau đó:

```python
novel2.chapters.append(
    "Chapter 2"
)
```

thì list của `novel` không bị thay đổi.

Nhưng:

> Không có nghĩa `deepcopy()` luôn là giải pháp tốt nhất.

---

# 39. Deepcopy có thể rất đắt

Với:

```text
Novel
 ├── 1000 Chapter
 ├── 10000 Image
 ├── Metadata
 └── Cache
```

:

```python
copy.deepcopy(novel)
```

có thể:

```text
CPU ↑
Memory ↑
Latency ↑
```

Đặc biệt nếu graph lớn.

---

# 40. Immutable Dataclass có thể tốt hơn

Thay vì:

```python
novel2 = deepcopy(novel)
novel2.title = "..."
```

có thể dùng:

```python
@dataclass(frozen=True)
class Novel:
    title: str
```

và:

```python
novel2 = replace(
    novel,
    title="New title",
)
```

Tư duy:

```text
mutable object
    ↓
copy
    ↓
modify

immutable object
    ↓
replace
    ↓
new object
```

---

# 41. Đây là Functional Programming Style

Pattern:

```python
new_state = replace(
    old_state,
    status="done",
)
```

rất phù hợp với:

```text
State management
Event processing
Async systems
GUI state
Task state
```

Đặc biệt liên quan tới những gì bạn đang học về:

```text
Flet
AsyncIO
Queue
Crawler
```

---

# 42. `copy` và AsyncIO

Ví dụ task state:

```python
@dataclass(frozen=True)
class TaskState:
    status: str
    progress: int
```

Worker:

```python
state = TaskState(
    status="running",
    progress=0,
)
```

Update:

```python
state = replace(
    state,
    progress=50,
)
```

Không cần:

```python
deepcopy()
```

Đây thường là cách dễ reasoning hơn trong concurrent code.

---

# 43. Pickle trong multiprocessing

Có một trường hợp pickle xuất hiện rất nhiều:

```text
multiprocessing
```

Python cần truyền object giữa process.

Concept:

```text
Process A
   │
   ▼
pickle
   │
   ▼
IPC
   │
   ▼
unpickle
   │
   ▼
Process B
```

Do đó khi dùng multiprocessing, bạn có thể gặp pickle ngay cả khi không gọi trực tiếp.

---

# 44. Điều này giải thích một số lỗi multiprocessing

Ví dụ object chứa:

```text
lambda
open file
thread lock
socket
database connection
```

có thể không pickle được hoặc không có semantics phù hợp.

Vì vậy:

> Dataclass đơn giản thường rất thân thiện với multiprocessing.

Ví dụ:

```python
@dataclass
class DownloadTask:
    url: str
    path: str
```

rất phù hợp để truyền task.

---

# 45. Dataclass + Pickle cho cache

Một số hệ thống Python nội bộ có thể dùng:

```text
Dataclass
 ↓
pickle
 ↓
cache
```

Ví dụ:

```python
cache.set(
    key,
    pickle.dumps(obj),
)
```

Nhưng cần cân nhắc:

```text
security
versioning
Python compatibility
class changes
cache invalidation
```

Đừng coi pickle là database format lâu dài.

---

# 46. Persistent storage vs temporary cache

### Temporary cache

Pickle có thể phù hợp trong môi trường trusted.

### Long-term storage

Thường nên ưu tiên:

```text
SQLite
JSON
TOML
Parquet
MessagePack
Protobuf
```

tùy use case.

Ví dụ crawler:

```text
Novel metadata
    ↓
SQLite
```

không nên:

```text
Novel metadata
    ↓
pickle file
```

nếu bạn cần query:

```sql
SELECT *
FROM novels
WHERE ...
```

---

# 47. Một quy tắc thực tế

### Dùng `asdict()` khi:

Bạn cần:

```text
Dataclass
 ↓
simple data representation
```

### Dùng `copy.copy()` khi:

Bạn muốn:

```text
new outer object
shared nested objects
```

### Dùng `deepcopy()` khi:

Bạn thực sự cần:

```text
independent object graph
```

### Dùng `replace()` khi:

Bạn muốn:

```text
new dataclass instance
with selected fields changed
```

### Dùng `pickle` khi:

Bạn cần:

```text
Python-specific object serialization
```

và boundary **trusted**.

---

# 48. Bảng quyết định

| Nhu cầu               | Công cụ                          |
| --------------------- | -------------------------------- |
| Dataclass → dict      | `asdict()`                       |
| Shallow copy          | `copy.copy()`                    |
| Deep copy             | `copy.deepcopy()`                |
| Immutable update      | `replace()`                      |
| Python object → bytes | `pickle`                         |
| API                   | JSON                             |
| Queue                 | JSON / msgspec / binary protocol |
| Config                | TOML / YAML                      |
| Database              | SQLite / SQL                     |
| Cross-language        | JSON / MessagePack / Protobuf    |

---

# 49. Mini Project — Object Lifecycle

Hãy tạo:

```python
from dataclasses import dataclass, field
import copy
import pickle


@dataclass
class Chapter:
    title: str
    tags: list[str] = field(
        default_factory=list
    )


@dataclass
class Novel:
    title: str
    chapters: list[Chapter] = field(
        default_factory=list
    )
```

Tạo:

```python
novel = Novel(
    title="Python Deep Dive",
    chapters=[
        Chapter(
            "Dataclass",
            ["python", "oop"],
        )
    ],
)
```

---

# 50. Thí nghiệm 1 — `copy.copy`

```python
shallow = copy.copy(novel)
```

Kiểm tra:

```python
print(novel is shallow)

print(
    novel.chapters
    is shallow.chapters
)
```

Bạn phải dự đoán trước:

```text
False
True
```

---

# 51. Thí nghiệm 2 — `deepcopy`

```python
deep = copy.deepcopy(novel)
```

Kiểm tra:

```python
print(novel is deep)

print(
    novel.chapters
    is deep.chapters
)

print(
    novel.chapters[0]
    is deep.chapters[0]
)
```

Kết quả:

```text
False
False
False
```

---

# 52. Thí nghiệm 3 — `asdict`

```python
data = asdict(novel)
```

Kiểm tra:

```python
print(type(data))
print(type(data["chapters"]))
print(type(data["chapters"][0]))
```

Kết quả:

```text
dict
list
dict
```

Nhớ:

```text
Dataclass graph
 ↓
Python data graph
```

---

# 53. Thí nghiệm 4 — Pickle

```python
payload = pickle.dumps(novel)

restored = pickle.loads(
    payload
)
```

Kiểm tra:

```python
print(type(restored))
print(restored)
```

Bạn sẽ nhận lại:

```text
Novel(...)
```

không phải `dict`.

---

# 54. Thí nghiệm 5 — `replace`

```python
from dataclasses import replace

new_novel = replace(
    novel,
    title="New title",
)
```

Kiểm tra:

```python
print(novel.title)
print(new_novel.title)
```

Kết quả:

```text
Python Deep Dive
New title
```

---

# 55. Bài tập nâng cao

Hãy tạo:

```python
@dataclass
class DownloadTask:
    id: int
    url: str
    headers: dict[str, str]
    retries: int = 0
```

Thực hiện:

### A

```text
task
 ↓
asdict()
```

### B

```text
task
 ↓
copy.copy()
```

### C

```text
task
 ↓
copy.deepcopy()
```

### D

```text
task
 ↓
pickle
 ↓
restore
```

Sau đó thay đổi:

```python
task.headers["User-Agent"]
```

và quan sát sự khác biệt giữa A/B/C/D.

---

# 56. Một bài cực kỳ quan trọng cho crawler

Tạo:

```python
@dataclass(frozen=True)
class DownloadTask:
    url: str
    chapter_id: int
    retry: int = 0
```

Sau đó:

```python
task2 = replace(
    task,
    retry=task.retry + 1,
)
```

Thiết kế worker:

```text
Task
 │
 ▼
Worker
 │
 ├── success → Done
 │
 └── failure
       │
       ▼
   replace(task)
       │
       ▼
   retry task
```

Đây là cách thiết kế state rất đẹp cho queue worker.

---

# 57. Tổng kết Phần III

Chúng ta vừa hoàn thành:

```text
Buổi 21
asdict / astuple

Buổi 22
JSON
orjson
msgspec

Buổi 23
YAML
TOML
XML

Buổi 24
pickle
copy
deepcopy
```

Toàn bộ phần này tạo thành:

```text
                  Dataclass
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       asdict       copy        pickle
          │           │           │
          ▼           ▼           ▼
        dict       object        bytes
          │
    ┌─────┼──────┐
    ▼     ▼      ▼
   JSON  YAML   TOML/XML
```

---

## Kiến thức quan trọng nhất

Đừng nhầm:

```text
copy
```

với:

```text
serialization
```

và đừng nhầm:

```text
pickle
```

với:

```text
safe data interchange
```

Mental model chuẩn:

```text
COPY
Python object
    ↓
Python object


SERIALIZATION
Python object
    ↓
data representation / bytes


DESERIALIZATION
data representation / bytes
    ↓
Python object
```

Và một quy tắc bảo mật phải nhớ:

> **Không `pickle.loads()` dữ liệu đến từ nguồn không tin cậy.**

---

### Sau Buổi 24

**Phần IV — Performance** bắt đầu:

**Buổi 25 — Benchmark: Class vs Dataclass vs NamedTuple vs attrs vs Pydantic**

Chúng ta sẽ không chỉ đo `__init__()` mà sẽ benchmark:

```text
creation
memory
attribute access
equality
serialization
copy
slots
```

và quan trọng nhất:

> **Dataclass có thực sự nhanh hơn class thường không? Khi nào `slots=True` đáng dùng?**
