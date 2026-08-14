# Dataclass Deep Dive — Buổi 22

# Dataclass → JSON: `json`, `orjson`, `msgspec`

Hôm nay chúng ta đi sâu vào **serialization Dataclass → JSON**.

Đây là bước rất quan trọng vì trong project thực tế, Dataclass thường nằm giữa:

```text
Database
   ↓
Entity / Model
   ↓
Dataclass
   ↓
DTO
   ↓
JSON
   ↓
API / Queue / File
```

Mục tiêu của buổi này không chỉ là biết:

```python
json.dumps(asdict(obj))
```

mà phải hiểu:

* JSON thực chất là gì
* `asdict()` đóng vai trò gì
* vì sao `json.dumps()` không hiểu Dataclass trực tiếp
* `default=` hoạt động thế nào
* `datetime`, `UUID`, `Enum`, `Decimal`
* `orjson`
* `msgspec`
* performance
* khi nào nên dùng từng giải pháp
* thiết kế serializer cho framework của riêng bạn

---

# 1. JSON là gì?

JSON chỉ có một tập kiểu dữ liệu tương đối nhỏ:

```text
JSON
│
├── object       → dict
├── array        → list
├── string       → str
├── number       → int / float
├── true         → True
├── false        → False
└── null         → None
```

Trong Python:

| JSON   | Python         |
| ------ | -------------- |
| object | `dict`         |
| array  | `list`         |
| string | `str`          |
| number | `int`, `float` |
| true   | `True`         |
| false  | `False`        |
| null   | `None`         |

Nhưng:

```text
datetime
UUID
Decimal
Enum
Dataclass
bytes
Path
```

không phải JSON primitive.

Đây chính là vấn đề chúng ta phải giải quyết.

---

# 2. `json.dumps()` không hiểu Dataclass

Ví dụ:

```python
from dataclasses import dataclass
import json


@dataclass
class User:
    id: int
    name: str


user = User(
    1,
    "Alice",
)
```

Thử:

```python
json.dumps(user)
```

sẽ lỗi dạng:

```text
TypeError:
Object of type User is not JSON serializable
```

Tại sao?

Bởi vì:

```text
json.dumps()
      ↓
JSON encoder
      ↓
biết dict/list/str/int/float/...
      ↓
không biết User
```

Python không tự suy luận:

```text
User
 ↓
fields()
 ↓
dict
```

---

# 3. Cách phổ biến nhất

Ta đã học `asdict()`:

```python
from dataclasses import asdict

data = asdict(user)
```

Kết quả:

```python
{
    "id": 1,
    "name": "Alice",
}
```

Sau đó:

```python
json.dumps(data)
```

Kết quả:

```json
{"id": 1, "name": "Alice"}
```

Pipeline:

```text
Dataclass
    ↓
asdict()
    ↓
dict
    ↓
json.dumps()
    ↓
JSON string
```

Đây là cách đơn giản và dễ hiểu nhất.

---

# 4. Nhưng có một vấn đề

Ta đang tạo ít nhất một cấu trúc trung gian:

```text
User
 ↓
asdict()
 ↓
new dict
 ↓
json.dumps()
 ↓
JSON
```

Nếu object lớn:

```text
Novel
 ├── Chapter × 1000
 ├── Image × 5000
 └── Metadata
```

thì:

```python
asdict(novel)
```

có thể tạo ra một object graph mới trước khi JSON encoder bắt đầu làm việc.

Pipeline:

```text
Original graph
      ↓
copy/traversal
      ↓
New Python graph
      ↓
JSON traversal
      ↓
bytes/string
```

Đây là lý do performance bắt đầu trở thành vấn đề.

---

# 5. `json.dumps(asdict(obj))`

Ví dụ hoàn chỉnh:

```python
from dataclasses import dataclass, asdict
import json


@dataclass
class User:
    id: int
    name: str


user = User(
    1,
    "Alice",
)

payload = json.dumps(
    asdict(user)
)

print(payload)
```

Output:

```json
{"id": 1, "name": "Alice"}
```

Đây là pattern bạn sẽ gặp rất nhiều:

```python
json.dumps(asdict(obj))
```

Nhưng:

> Đơn giản không đồng nghĩa với tối ưu.

---

# 6. Nested Dataclass

Ví dụ:

```python
@dataclass
class Address:
    city: str
    country: str


@dataclass
class User:
    id: int
    name: str
    address: Address
```

:

```python
user = User(
    1,
    "Alice",
    Address(
        "Ho Chi Minh",
        "Vietnam",
    ),
)
```

`asdict()`:

```python
asdict(user)
```

cho:

```python
{
    "id": 1,
    "name": "Alice",
    "address": {
        "city": "Ho Chi Minh",
        "country": "Vietnam",
    },
}
```

Sau đó:

```python
json.dumps(asdict(user))
```

hoạt động bình thường.

---

# 7. `datetime` xuất hiện

Bây giờ:

```python
from datetime import datetime


@dataclass
class Event:
    name: str
    created_at: datetime
```

:

```python
event = Event(
    "login",
    datetime.now(),
)
```

Ta có:

```python
asdict(event)
```

vẫn hoạt động.

Nhưng:

```python
json.dumps(
    asdict(event)
)
```

sẽ lỗi:

```text
TypeError:
Object of type datetime is not JSON serializable
```

Đây là điểm rất quan trọng:

> `asdict()` không biến `datetime` thành JSON string.

---

# 8. `default=` của `json.dumps`

Ta có thể:

```python
json.dumps(
    asdict(event),
    default=str,
)
```

Ví dụ output:

```json
{
    "name": "login",
    "created_at": "2026-08-14 21:..."
}
```

Nhưng:

> `default=str` rất tiện nhưng quá rộng.

Nó có thể biến những object không mong muốn thành string.

Trong production, thường nên kiểm soát kiểu dữ liệu rõ ràng hơn.

---

# 9. Custom JSON Encoder

Ta có thể viết:

```python
import json
from datetime import datetime


class DataclassEncoder(json.JSONEncoder):

    def default(self, obj):

        if isinstance(obj, datetime):
            return obj.isoformat()

        return super().default(obj)
```

Sau đó:

```python
json.dumps(
    asdict(event),
    cls=DataclassEncoder,
)
```

Kết quả:

```json
{
    "name": "login",
    "created_at": "2026-08-14T21:..."
}
```

---

# 10. Nhưng ta có thể serialize Dataclass trực tiếp

Thay vì:

```python
json.dumps(
    asdict(event),
)
```

ta có thể dùng:

```python
json.dumps(
    event,
    cls=DataclassEncoder,
)
```

Nhưng encoder phải biết cách xử lý Dataclass.

Ví dụ:

```python
from dataclasses import (
    is_dataclass,
    asdict,
)


class DataclassEncoder(json.JSONEncoder):

    def default(self, obj):

        if is_dataclass(obj):
            return asdict(obj)

        if isinstance(obj, datetime):
            return obj.isoformat()

        return super().default(obj)
```

Sau đó:

```python
json.dumps(
    event,
    cls=DataclassEncoder,
)
```

---

# 11. Pipeline lúc này

```text
Dataclass
     ↓
JSONEncoder
     │
     ├── dataclass → asdict()
     │
     ├── datetime → isoformat()
     │
     ├── UUID → str()
     │
     └── unknown → error
     ↓
JSON
```

Đây là bước đầu tiên để xây:

> Custom serialization framework.

---

# 12. UUID

Ví dụ:

```python
from uuid import UUID, uuid4


@dataclass
class User:
    id: UUID
    name: str
```

:

```python
user = User(
    uuid4(),
    "Alice",
)
```

`json.dumps(asdict(user))` sẽ không biết `UUID`.

Ta thêm:

```python
if isinstance(obj, UUID):
    return str(obj)
```

---

# 13. Decimal

Ví dụ:

```python
from decimal import Decimal


@dataclass
class Product:
    name: str
    price: Decimal
```

JSON không có Decimal.

Ta phải quyết định:

```text
Decimal
 ↓
string?
```

hay:

```text
Decimal
 ↓
float?
```

Đây không chỉ là vấn đề kỹ thuật.

Nó là **serialization policy**.

---

# 14. Decimal → float?

Ví dụ:

```python
Decimal("19.99")
```

thành:

```python
19.99
```

có thể gây mất precision do floating point.

Với tiền tệ, thường không nên tùy tiện:

```python
Decimal → float
```

Có thể chọn:

```text
Decimal → string
```

Ví dụ:

```json
{
    "price": "19.99"
}
```

---

# 15. Enum

Ví dụ:

```python
from enum import Enum


class Status(Enum):
    PENDING = "pending"
    DONE = "done"


@dataclass
class Task:
    status: Status
```

Ta phải quyết định JSON muốn:

```json
{
    "status": "pending"
}
```

hay:

```json
{
    "status": 1
}
```

Thông thường dùng:

```python
obj.value
```

---

# 16. Một encoder tốt hơn

```python
from dataclasses import (
    is_dataclass,
    asdict,
)
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID
import json


class Encoder(json.JSONEncoder):

    def default(self, obj):

        if is_dataclass(obj):
            return asdict(obj)

        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, UUID):
            return str(obj)

        if isinstance(obj, Decimal):
            return str(obj)

        if isinstance(obj, Enum):
            return obj.value

        return super().default(obj)
```

Sử dụng:

```python
json.dumps(
    obj,
    cls=Encoder,
)
```

---

# 17. Một vấn đề với `is_dataclass()`

Nhớ bài 20:

```python
is_dataclass(User)
```

là:

```text
True
```

và:

```python
is_dataclass(user)
```

cũng:

```text
True
```

Nhưng `json.dumps()` chỉ đưa object vào `default()` khi encoder không biết xử lý nó.

Bạn nên hiểu chính xác boundary này khi viết encoder.

---

# 18. JSON serialization ≠ JSON encoding

Có hai khái niệm:

### Serialization

```text
Object
 ↓
JSON-compatible representation
```

### Encoding

```text
Python representation
 ↓
JSON bytes/string
```

Ví dụ:

```text
User
 ↓ serialization
dict
 ↓ encoding
JSON string
```

`asdict()` gần với serialization.

`json.dumps()` là encoding.

---

# 19. `json.dump()` vs `json.dumps()`

`dumps`:

```python
text = json.dumps(data)
```

trả về:

```text
str
```

`dump`:

```python
json.dump(
    data,
    file,
)
```

ghi trực tiếp vào file.

Tên dễ nhớ:

```text
dump
    ↓
file

dumps
    ↓
string
```

---

# 20. `ensure_ascii`

Ví dụ:

```python
data = {
    "title": "Xin chào Việt Nam"
}
```

Nếu:

```python
json.dumps(data)
```

có thể xuất Unicode escaped.

Bạn thường muốn:

```python
json.dumps(
    data,
    ensure_ascii=False,
)
```

Kết quả dễ đọc hơn:

```json
{"title": "Xin chào Việt Nam"}
```

Đây là option hữu ích với crawler tiếng Việt.

---

# 21. `indent`

Debug:

```python
json.dumps(
    data,
    ensure_ascii=False,
    indent=2,
)
```

Output:

```json
{
  "id": 1,
  "name": "Alice"
}
```

Nhưng không nên mặc định dùng `indent=2` cho payload production nếu bandwidth/size quan trọng.

---

# 22. `sort_keys`

Có thể:

```python
json.dumps(
    data,
    sort_keys=True,
)
```

Điều này hữu ích khi:

* snapshot testing
* deterministic output
* debugging
* cache key

Ví dụ:

```text
{
    "a": 1,
    "b": 2
}
```

thay vì phụ thuộc thứ tự tạo dict.

---

# 23. `orjson`

Bây giờ đến thư viện phổ biến trong hệ thống Python hiệu năng cao:

```text
orjson
```

Ý tưởng:

```text
stdlib json
    ↓
Python implementation

orjson
    ↓
native/Rust implementation
```

API cơ bản:

```python
import orjson

data = {
    "id": 1,
    "name": "Alice",
}

result = orjson.dumps(data)
```

Điểm khác:

```text
json.dumps()
    → str

orjson.dumps()
    → bytes
```

---

# 24. Vì sao `bytes`?

JSON thường được gửi qua network.

Network layer cuối cùng cần:

```text
bytes
```

Do đó:

```python
orjson.dumps(data)
```

trả:

```python
b'{"id":1,"name":"Alice"}'
```

Nếu thực sự cần string:

```python
result.decode()
```

Nhưng nếu HTTP framework chấp nhận bytes thì decode có thể không cần thiết.

---

# 25. `orjson` và Dataclass

Một ưu điểm rất hữu ích:

`orjson` có hỗ trợ Dataclass.

Ví dụ:

```python
@dataclass
class User:
    id: int
    name: str
```

:

```python
user = User(
    1,
    "Alice",
)
```

Có thể:

```python
orjson.dumps(user)
```

với các tùy chọn phù hợp.

Điều này giúp tránh pattern bắt buộc:

```text
dataclass
 ↓
asdict
 ↓
dict
 ↓
orjson
```

---

# 26. `OPT_SERIALIZE_DATACLASS`

`orjson` cung cấp option:

```python
orjson.OPT_SERIALIZE_DATACLASS
```

Ví dụ:

```python
orjson.dumps(
    user,
    option=orjson.OPT_SERIALIZE_DATACLASS,
)
```

Conceptually:

```text
User
 ↓
orjson
 ↓
JSON bytes
```

---

# 27. Datetime với `orjson`

Một điểm mạnh của `orjson` là hỗ trợ nhiều kiểu dữ liệu phổ biến tốt hơn stdlib JSON.

Ví dụ:

```python
@dataclass
class Event:
    created_at: datetime
```

có thể serialize trực tiếp với `orjson` theo semantics của thư viện.

Điều này giúp giảm lượng custom encoder code.

---

# 28. Nhưng đừng chỉ nhìn benchmark

Không nên quyết định:

```text
orjson nhanh
→ luôn dùng orjson
```

Cần xem:

```text
API
database
message queue
file
compatibility
dependency
deployment
data types
```

Ví dụ một library có thể nhanh hơn nhưng API behavior không phù hợp với hệ thống.

---

# 29. `msgspec`

Bây giờ đến một thư viện rất đáng chú ý:

```text
msgspec
```

Nó không chỉ là JSON serializer.

Nó hướng tới:

```text
serialization
+
validation
+
typed schema
+
high performance
```

Một concept quan trọng:

```python
import msgspec
```

Có thể dùng:

```python
msgspec.Struct
```

Ví dụ:

```python
class User(msgspec.Struct):
    id: int
    name: str
```

Đây không phải `@dataclass`, nhưng tư duy rất gần.

---

# 30. `msgspec` và Dataclass

`msgspec` có khả năng làm việc với dataclass trong các trường hợp phù hợp, nhưng điểm mạnh nhất của nó nằm ở mô hình typed struct riêng:

```text
Dataclass
    ↓
general Python data object

msgspec.Struct
    ↓
serialization-oriented typed structure
```

Nếu xây hệ thống serialization hiệu năng cao, đây là một lựa chọn đáng nghiên cứu.

---

# 31. So sánh tư duy

### `dataclasses + json`

```text
General Python
      ↓
Flexible
      ↓
Simple
```

### `dataclasses + orjson`

```text
General Python
      ↓
Fast serialization
```

### `msgspec.Struct`

```text
Schema-oriented
      ↓
Validation
      ↓
Serialization
      ↓
Performance
```

---

# 32. Benchmark đúng cách

Đừng benchmark:

```python
json.dumps({})
```

rồi kết luận.

Hãy benchmark object thực tế:

```text
Novel
 ├── metadata
 ├── Author
 ├── Chapter × 100
 └── Image × 500
```

Các pipeline cần so sánh:

```text
A:
dataclass
 → asdict
 → json.dumps

B:
dataclass
 → orjson

C:
msgspec.Struct
 → msgspec.json.encode
```

Đây mới là benchmark có giá trị.

---

# 33. Benchmark framework

Có thể chuẩn bị:

```python
import timeit


def benchmark(fn, number=10_000):
    return timeit.timeit(
        fn,
        number=number,
    )
```

Sau đó:

```python
print(
    benchmark(
        lambda: json.dumps(
            asdict(user)
        )
    )
)
```

và:

```python
print(
    benchmark(
        lambda: orjson.dumps(
            user
        )
    )
)
```

Nhưng hãy nhớ:

> Benchmark phải cùng semantics.

Nếu một bên deep-copy toàn bộ graph còn bên kia encode trực tiếp thì bạn đang đo cả **chiến lược serialization**, không chỉ tốc độ encoder.

---

# 34. JSON và Crawler

Đây là phần liên quan trực tiếp tới hệ thống của bạn.

Crawler có:

```text
Novel
Chapter
Image
Author
Category
```

Bạn có thể cần JSON để:

```text
Crawler
   ↓
Queue
   ↓
Worker
```

Ví dụ:

```python
@dataclass
class DownloadTask:
    url: str
    chapter_id: int
```

Serialize:

```text
DownloadTask
      ↓
JSON
      ↓
Queue
      ↓
Worker
```

---

# 35. Queue không nhất thiết nên truyền Entity

Ví dụ không nên:

```text
Novel Entity
 ↓
JSON
 ↓
Queue
```

thường tốt hơn là:

```python
@dataclass
class DownloadTask:
    chapter_id: int
    image_url: str
```

Đây là:

> Message DTO.

Nhỏ hơn:

```text
Entity
```

và phù hợp với boundary.

---

# 36. Dataclass → Queue Message

Ví dụ:

```python
@dataclass
class DownloadTask:
    task_id: str
    url: str
    chapter_id: int
```

Ta có:

```python
payload = orjson.dumps(
    task
)
```

Queue:

```text
Producer
   ↓
DownloadTask
   ↓
JSON bytes
   ↓
Queue
   ↓
Worker
```

Worker:

```text
JSON
 ↓
decode
 ↓
DownloadTask
```

Buổi sau này khi xây queue server, pattern này sẽ rất hữu ích.

---

# 37. JSON → Dataclass

Serialization có hai chiều:

```text
Dataclass
    ↓
serialize
    ↓
JSON
```

và:

```text
JSON
    ↓
deserialize
    ↓
Dataclass
```

Ví dụ đơn giản:

```python
data = {
    "id": 1,
    "name": "Alice",
}

user = User(
    **data
)
```

Pipeline:

```text
JSON
 ↓
dict
 ↓
User(**dict)
```

---

# 38. Nhưng `User(**data)` không validation mạnh

Ví dụ:

```python
data = {
    "id": "hello",
    "name": 123,
}
```

Python có thể vẫn tạo:

```python
User(
    id="hello",
    name=123,
)
```

vì type hints không tự validate runtime.

Đây là lý do:

```text
Serialization
```

và:

```text
Validation
```

là hai vấn đề khác nhau.

---

# 39. Đây là lý do `msgspec` đáng chú ý

Một schema-oriented library có thể làm:

```text
JSON
 ↓
decode
 ↓
validate
 ↓
typed object
```

thay vì:

```text
JSON
 ↓
dict
 ↓
constructor
 ↓
hy vọng dữ liệu đúng
```

Trong hệ thống lớn, distinction này rất quan trọng.

---

# 40. Custom Serialization Architecture

Nếu tự xây framework, ta có thể thiết kế:

```text
serializer/
│
├── base.py
├── json.py
├── orjson.py
├── rules.py
└── registry.py
```

Concept:

```python
class Serializer:
    def serialize(self, obj):
        ...
```

Sau đó:

```text
JsonSerializer
OrjsonSerializer
MsgspecSerializer
```

đều implement:

```python
serialize(obj)
```

---

# 41. Serialization Registry

Ta có thể đăng ký:

```python
registry = {
    datetime: serialize_datetime,
    UUID: serialize_uuid,
    Decimal: serialize_decimal,
    Enum: serialize_enum,
}
```

Pipeline:

```text
Object
 ↓
Serializer
 ↓
Registry
 ↓
Type-specific handler
 ↓
JSON-compatible value
```

Đây là kiến trúc rất hữu ích khi sau này chúng ta học:

> Dataclass framework mini.

---

# 42. Metadata-driven JSON

Kết hợp kiến thức Buổi 4:

```python
@dataclass
class User:
    id: int = field(
        metadata={
            "json_name": "userId"
        }
    )

    name: str
```

Custom serializer có thể:

```text
Field
 ↓
metadata
 ↓
json_name
 ↓
JSON
```

Kết quả:

```json
{
  "userId": 1,
  "name": "Alice"
}
```

Đây là một bước rất gần với:

```text
Pydantic
attrs
marshmallow
dataclasses-json
```

---

# 43. Một serializer thực tế

Ta có thể bắt đầu:

```python
from dataclasses import (
    fields,
    is_dataclass,
)


def serialize_dataclass(obj):

    if not is_dataclass(obj):
        raise TypeError(
            "Expected dataclass instance"
        )

    result = {}

    for f in fields(obj):

        key = f.metadata.get(
            "json_name",
            f.name,
        )

        value = getattr(
            obj,
            f.name,
        )

        result[key] = value

    return result
```

Sau đó:

```python
json.dumps(
    serialize_dataclass(user)
)
```

Đây là version đầu tiên.

---

# 44. Nhưng serializer trên chưa recursive

Nếu:

```python
@dataclass
class User:
    address: Address
```

thì:

```python
result["address"]
```

vẫn là:

```text
Address instance
```

JSON encoder lại không hiểu.

Ta cần:

```text
serialize()
   │
   ├── dataclass → recurse
   ├── list → recurse
   ├── dict → recurse
   ├── datetime → encode
   ├── UUID → encode
   └── primitive → 그대로
```

Đây sẽ trở thành một bài tập lớn rất hay.

---

# 45. Architecture hoàn chỉnh

Một serializer framework có thể:

```text
                   serialize()
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      Dataclass      Container      Primitive
          │             │
          ▼             ▼
      fields()       recurse
          │
          ▼
      metadata
          │
          ▼
      type handler
          │
          ▼
    JSON-compatible
```

Sau đó:

```text
JSON-compatible
       ↓
json/orjson/msgspec
       ↓
bytes
```

---

# 46. Khi nào dùng `json`?

Dùng khi:

* không cần dependency ngoài
* payload vừa phải
* compatibility quan trọng
* code đơn giản
* performance không phải bottleneck

Ví dụ:

```python
json.dumps(
    asdict(obj),
    ensure_ascii=False,
)
```

hoàn toàn hợp lý.

---

# 47. Khi nào dùng `orjson`?

Phù hợp khi:

* JSON là hot path
* API
* queue
* crawler
* nhiều serialization
* cần bytes
* muốn performance tốt nhưng vẫn dùng Python object/dataclass

Pattern:

```text
Dataclass
 ↓
orjson
 ↓
bytes
```

---

# 48. Khi nào xem xét `msgspec`?

Đặc biệt đáng xem xét khi:

* throughput cao
* cần validation
* schema rõ ràng
* serialization/deserialization là trọng tâm
* muốn typed data structure
* cần tối ưu cả encode và decode

Pattern:

```text
Typed Schema
   ↓
msgspec
   ↓
encode/decode
```

---

# 49. Một sai lầm kiến trúc phổ biến

Đừng làm:

```text
Entity
 ↓
asdict()
 ↓
JSON
 ↓
API
```

cho mọi boundary.

Hãy xác định:

```text
Entity
   ↓
DTO
   ↓
Serializer
   ↓
Boundary
```

Ví dụ:

```text
Database
   ↓
NovelEntity
   ↓
NovelResponseDTO
   ↓
JSON
   ↓
REST API
```

hoặc:

```text
Crawler
   ↓
DownloadTask
   ↓
JSON
   ↓
Queue
```

---

# 50. Tổng kết Buổi 22

Bạn cần nắm được pipeline:

```text
Dataclass
    │
    ├───────────────┐
    ▼               ▼
 asdict()       custom serializer
    │               │
    ▼               ▼
   dict        JSON-compatible
    │               │
    └───────┬───────┘
            ▼
       JSON encoder
            │
       ┌────┼─────┐
       ▼    ▼     ▼
      json orjson msgspec
       │    │     │
       └────┼─────┘
            ▼
        JSON bytes
```

Và đặc biệt nhớ:

### `asdict()`

```text
Dataclass
 ↓
recursive Python structure
 ↓
deep-copy semantics
```

### `json`

```text
Python JSON-compatible object
 ↓
JSON string
```

### `orjson`

```text
Python object
 ↓
high-performance JSON bytes
```

### `msgspec`

```text
Typed structure
 ↓
validation + serialization/deserialization
```

---

# Bài tập Buổi 22

Hãy xây một serializer cho crawler với model:

```python
@dataclass
class Image:
    url: str
    width: int | None = None


@dataclass
class Chapter:
    id: int
    title: str
    images: list[Image]


@dataclass
class Novel:
    id: int
    title: str
    chapters: list[Chapter]
    updated_at: datetime
```

Yêu cầu:

```text
1. Dataclass → dict
2. datetime → ISO 8601
3. nested dataclass
4. list[dataclass]
5. dict → JSON
6. JSON Unicode tiếng Việt
7. Benchmark:
      asdict + json
      custom serializer + json
      orjson
```

Đặc biệt hãy thử với:

```text
1 Novel
100 Chapter
10 Image / Chapter
```

để thấy sự khác biệt về chi phí.

**Buổi 23** sẽ chuyển sang **Serialization với YAML, TOML và XML**, tập trung vào một câu hỏi quan trọng: *JSON không phải format duy nhất — chọn format nào cho config, document, API và dữ liệu crawler?*
