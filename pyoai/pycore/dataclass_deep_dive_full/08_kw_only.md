# Dataclass Deep Dive - Buổi 8

# Keyword-only Fields (`kw_only=True`) Deep Dive

> **Đây là một tính năng mới từ Python 3.10** nhưng lại được sử dụng rất nhiều trong các thư viện hiện đại như **FastAPI**, **Pydantic v2**, **SQLAlchemy 2.0**, **Typer**, **Rich**...

Trong các dự án lớn, `kw_only=True` giúp tránh rất nhiều lỗi do truyền sai tham số.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- Keyword-only parameter là gì?
- `kw_only=True`
- `KW_ONLY`
- Constructor được sinh như thế nào?
- Khi nào nên dùng?
- Thiết kế API chuyên nghiệp
- Áp dụng vào dự án crawler

---

# 1. Positional Argument

Ví dụ

```text-x-trilium-auto
def connect(host, port):
    print(host, port)
```

Gọi

```text-x-trilium-auto
connect("localhost", 3306)
```

Đây gọi là

```text-x-trilium-auto
Positional Argument
```

Python truyền theo vị trí.

---

# 2. Keyword Argument

Ví dụ

```text-x-trilium-auto
connect(
    host="localhost",
    port=3306
)
```

Đây là

```text-x-trilium-auto
Keyword Argument
```

Python truyền theo tên.

---

# 3. Hàm Keyword-only

Python hỗ trợ

```text-x-trilium-auto
def connect(host, *, port):
    ...
```

Dấu

```text-x-trilium-auto
*
```

có nghĩa

Sau dấu *

↓

phải truyền bằng tên.

Ví dụ

```text-x-trilium-auto
connect(
    "localhost",
    port=3306
)
```

Đúng.

---

Sai

```text-x-trilium-auto
connect(
    "localhost",
    3306
)
```

Lỗi

```text-x-trilium-auto
TypeError
```

---

# 4. Dataclass hỗ trợ

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass, field

@dataclass class Config:

    host: str

    port: int = field(
        kw_only=True
    )
```

---

Constructor

gần giống

```text-x-trilium-auto
def __init__(

    self,

    host,

    *,

    port

):
    ...
```

---

# 5. Ví dụ

```text-x-trilium-auto
config = Config(
    "localhost",
    port=3306
)
```

Đúng.

---

Sai

```text-x-trilium-auto
Config(
    "localhost",
    3306
)
```

Kết quả

```text-x-trilium-auto
TypeError
```

---

# 6. inspect.signature()

```text-x-trilium-auto
import inspect

print(

inspect.signature(Config)

)
```

Kết quả

```text-x-trilium-auto
(host: str, *, port: int)
```

Rất rõ ràng.

---

# 7. kw_only toàn bộ class

Có thể

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(
    kw_only=True
)
class Config:

    host:str

    port:int
```

Bây giờ

```text-x-trilium-auto
Config(
    host="localhost",
    port=3306
)
```

Đúng.

---

Sai

```text-x-trilium-auto
Config(
    "localhost",
    3306
)
```

Lỗi.

---

# 8. KW_ONLY

Dataclass còn có

```text-x-trilium-auto
from dataclasses import KW_ONLY
```

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass from dataclasses import KW_ONLY

@dataclass class Config:

    host:str

    _:KW_ONLY

    port:int

    timeout:int
```

Ý nghĩa

```text-x-trilium-auto
host

↓

Positional

----------------

port

↓

Keyword-only

timeout

↓

Keyword-only
```

---

Gọi

```text-x-trilium-auto
Config(

"localhost",

port=3306,

timeout=30

)
```

Đúng.

---

# 9. Minh họa

```text-x-trilium-auto
host

↓

Config(

"localhost",

port=3306,

timeout=30

)
```

Không thể

```text-x-trilium-auto
Config(

"localhost",

3306,

30

)
```

---

# 10. Vì sao cần?

Giả sử

```text-x-trilium-auto
@dataclass class CrawlerConfig:

    host:str

    port:int

    timeout:int

    retry:int

    verify_ssl:bool

    proxy:str
```

Tạo object

```text-x-trilium-auto
CrawlerConfig(

"abc",

443,

60,

3,

False,

"http://..."
)
```

Bạn còn nhớ

```text-x-trilium-auto
False
```

là gì không?

Có thể sau vài ngày sẽ rất khó nhớ ý nghĩa của từng tham số.

---

Dùng

```text-x-trilium-auto
@dataclass class CrawlerConfig:

    host:str

    _:KW_ONLY

    timeout:int

    retry:int

    verify_ssl:bool

    proxy:str
```

Kết quả

```text-x-trilium-auto
CrawlerConfig(

"abc",

timeout=60,

retry=3,

verify_ssl=False,

proxy="..."

)
```

Đọc code rất rõ ràng.

---

# 11. API rõ ràng

Sai

```text-x-trilium-auto
resize(

100,

200,

True,

False

)
```

Đúng

```text-x-trilium-auto
resize(

100,

200,

keep_ratio=True,

smooth=False

)
```

Đây chính là lý do nhiều thư viện thiết kế API bằng keyword-only.

---

# 12. Kết hợp default

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass from dataclasses import field

@dataclass class Config:

    host:str

    timeout:int=field(

        default=30,

        kw_only=True

    )
```

Có thể

```text-x-trilium-auto
Config(
    "localhost"
)
```

Hoặc

```text-x-trilium-auto
Config(

"localhost",

timeout=100
)
```

---

# 13. Kết hợp default_factory

```text-x-trilium-auto
from dataclasses import field

headers = field(

default_factory=dict,

kw_only=True
)
```

---

# 14. Kết hợp repr

```text-x-trilium-auto
password = field(

repr=False,

kw_only=True
)
```

---

# 15. Kết hợp compare

```text-x-trilium-auto
retry = field(

compare=False,

kw_only=True
)
```

Không có xung đột.

---

# 16. kw_only và kế thừa

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass from dataclasses import KW_ONLY

@dataclass class Animal:

    name:str

    _:KW_ONLY

    age:int
```

```text-x-trilium-auto
@dataclass class Dog(Animal):

    breed:str
```

Constructor sẽ kết hợp quy tắc keyword-only từ lớp cha với các field của lớp con. Đây là lý do cần xem `inspect.signature()` khi thiết kế các lớp kế thừa phức tạp.

---

# 17. Thực tế FastAPI

FastAPI có rất nhiều hàm kiểu

```text-x-trilium-auto
Query(

default=None,

alias="id",

description="..."

)
```

Hầu hết đều

↓

Keyword-only.

Không ai muốn viết

```text-x-trilium-auto
Query(

None,

"id",

"..."
)
```

Rất khó đọc.

---

# 18. Crawler Project

Đề xuất

```text-x-trilium-auto
from dataclasses import dataclass from dataclasses import KW_ONLY

@dataclass class CrawlOptions:

    url:str

    _:KW_ONLY

    retry:int=3

    timeout:int=60

    proxy:str|None=None

    verify_ssl:bool=True
```

Sử dụng

```text-x-trilium-auto
CrawlOptions(

"https://...",

retry=5,

timeout=120

)
```

Đọc rất dễ hiểu.

---

# 19. Không nên lạm dụng

Nếu chỉ có

```text-x-trilium-auto
Point(

10,

20
)
```

thì

```text-x-trilium-auto
Point(

x=10,

y=20
)
```

không đem lại nhiều lợi ích.

`kw_only=True` phù hợp hơn với các lớp có nhiều tham số hoặc nhiều giá trị mặc định.

---

# 20. Best Practice

Nên

```text-x-trilium-auto
User(
    username,
    password
)
```

Nhưng

```text-x-trilium-auto
CrawlerOptions(

url,

timeout=60,

retry=5,

proxy="...",

headers={}

)
```

Đây là cách nhiều framework hiện đại thiết kế API.

---

# 21. Constructor được sinh

Ví dụ

```text-x-trilium-auto
@dataclass class User:

    id:int

    name:str

    age:int=field(

        kw_only=True
    )
```

Python sinh gần giống

```text-x-trilium-auto
def __init__(

    self,

    id,

    name,

    *,

    age

):
    ...
```

Đây chính là lý do chỉ `age` bắt buộc phải truyền bằng keyword.

---

# 22. Kết hợp với `slots=True` và `frozen=True`

Hoàn toàn hợp lệ:

```text-x-trilium-auto
from dataclasses import dataclass, KW_ONLY

@dataclass(
    slots=True,
    frozen=True
)
class ApiRequest:
    url: str

    _: KW_ONLY

    timeout: int = 30
    retry: int = 3
```

Bạn có một đối tượng:

- tiết kiệm bộ nhớ,
- bất biến,
- API rõ ràng.

---

# Tổng kết

| Tính năng | Ý nghĩa |
| --- | --- |
| `kw_only=True` | Field phải truyền bằng keyword |
| `@dataclass(kw_only=True)` | Toàn bộ field là keyword-only |
| `KW_ONLY` | Các field phía sau trở thành keyword-only |
| `inspect.signature()` | Xem constructor được sinh |
| Ứng dụng | API, Config, Request Object |

---

# Best Practice

## Nên dùng

✔ Config

✔ Request

✔ Options

✔ Settings

✔ Builder

✔ CrawlerConfig

✔ DatabaseConfig

✔ HTTPOptions

---

## Không cần

✘ Point

✘ Vector

✘ Color

✘ Complex Number

Những object nhỏ có 2–3 field rõ ràng thì truyền theo vị trí thường ngắn gọn và dễ đọc hơn.

---

# Bài tập thực hành

## Bài 1

Tạo:

```text-x-trilium-auto
@dataclass class DatabaseConfig:
    host: str
    _: KW_ONLY
    port: int
    username: str
    password: str = field(repr=False)
```

Yêu cầu:

- Dùng `inspect.signature()` xem constructor.
- Tạo đối tượng đúng cách.
- Thử tạo đối tượng bằng positional argument cho `port` và quan sát lỗi.

---

## Bài 2

Thiết kế:

```text-x-trilium-auto
@dataclass(kw_only=True)
class HttpOptions:
    timeout: int = 30
    retry: int = 3
    verify_ssl: bool = True
    proxy: str | None = None
```

Khởi tạo đối tượng bằng keyword arguments và thử gọi bằng positional arguments để thấy sự khác biệt.

---

## Bài 3 (Áp dụng dự án crawler)

Thiết kế dataclass:

```text-x-trilium-auto
@dataclass class CrawlJob:
    url: str
    _: KW_ONLY
    timeout: int = 60
    retry: int = 3
    headers: dict[str, str] = field(default_factory=dict)
    proxy: str | None = None
    verify_ssl: bool = True
```

Thực hiện:

1. Tạo một `CrawlJob`.
2. In `inspect.signature(CrawlJob)`.
3. Thử gọi constructor sai (truyền tất cả bằng positional arguments) và giải thích lỗi.

---

# Chuẩn bị cho Buổi 9

Buổi tiếp theo chúng ta sẽ học `**InitVar**` **Deep Dive**.

Đây là một tính năng rất đặc biệt của `dataclass`:

- Field chỉ tồn tại trong quá trình khởi tạo.
- Không được lưu vào object.
- Thường kết hợp với `__post_init__()`.
- Dùng để truyền mật khẩu, kết nối cơ sở dữ liệu, đối tượng cấu hình, hoặc dữ liệu tạm thời phục vụ việc khởi tạo.

Đây là một chủ đề mà nhiều lập trình viên Python chưa từng sử dụng, nhưng lại xuất hiện trong các thư viện và mã nguồn chuyên nghiệp.