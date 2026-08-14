# Dataclass Deep Dive - Buổi 9

# `InitVar` Deep Dive (Initialization-only Variables)

> Đây là một trong những tính năng **ít được biết đến nhất** của `dataclass`, nhưng lại cực kỳ hữu ích trong các dự án thực tế.

Nhiều lập trình viên Python sử dụng `dataclass` nhiều năm nhưng chưa từng dùng `InitVar`. Tuy nhiên, nếu bạn đọc mã nguồn của các thư viện lớn hoặc xây dựng hệ thống có kiến trúc tốt, bạn sẽ gặp nó khá thường xuyên.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- `InitVar` là gì?
- Khác gì với field thông thường?
- Quan hệ giữa `InitVar` và `__post_init__()`
- Khi nào nên dùng?
- Khi nào không nên dùng?
- Ứng dụng trong hệ thống crawler của bạn

---

# 1. Vấn đề

Giả sử ta có:

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class User:

    username: str

    password: str
```

Tạo object:

```text-x-trilium-auto
u = User("alice", "123456")
```

Object chứa:

```text-x-trilium-auto
print(u)
```

```text-x-trilium-auto
User(username='alice', password='123456')
```

Nhưng có những dữ liệu **chỉ dùng để khởi tạo**, không nên lưu trong object.

Ví dụ:

- mật khẩu gốc
- token tạm
- file cấu hình
- database connection
- HTTP client
- Session

---

# 2. InitVar là gì?

```text-x-trilium-auto
from dataclasses import InitVar
```

`InitVar`

↓

Là biến **chỉ tồn tại trong constructor**.

Sau khi object được tạo

↓

biến này biến mất.

---

# 3. Ví dụ đầu tiên

```text-x-trilium-auto
from dataclasses import dataclass from dataclasses import InitVar

@dataclass class User:

    username: str

    password: InitVar[str]
```

Tạo

```text-x-trilium-auto
u = User(
    "alice",
    "123456"
)
```

Bây giờ

```text-x-trilium-auto
print(u)
```

Kết quả

```text-x-trilium-auto
User(username='alice')
```

Không có

```text-x-trilium-auto
password
```

---

# 4. Kiểm tra

```text-x-trilium-auto
print(hasattr(
    u,
    "password"
))
```

Kết quả

```text-x-trilium-auto
False
```

Không tồn tại.

---

# 5. Vậy password đi đâu?

Python truyền nó vào

```text-x-trilium-auto
__post_init__()
```

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass from dataclasses import InitVar

@dataclass class User:

    username: str

    password: InitVar[str]

    def __post_init__(
        self,
        password
    ):
        print(password)
```

Kết quả

```text-x-trilium-auto
123456
```

Sau đó

↓

password biến mất.

---

# 6. Constructor được sinh

Dataclass sinh gần giống

```text-x-trilium-auto
def __init__(
    self,
    username,
    password
):

    self.username = username

    self.__post_init__(
        password
    )
```

Lưu ý

```text-x-trilium-auto
password
```

không được gán vào

```text-x-trilium-auto
self.password
```

---

# 7. Ví dụ Hash Password

Đây là ví dụ kinh điển.

```text-x-trilium-auto
from dataclasses import dataclass from dataclasses import InitVar import hashlib

@dataclass class User:

    username: str

    password_hash: str = ""

    password: InitVar[str] = ""

    def __post_init__(
        self,
        password
    ):
        self.password_hash = hashlib.sha256(
            password.encode()
        ).hexdigest()
```

Tạo

```text-x-trilium-auto
u = User(
    "alice",
    "123456"
)
```

Object

```text-x-trilium-auto
User(
username='alice',
password_hash='8d969e...'
)
```

Không còn password gốc.

---

# 8. Ví dụ Database Connection

```text-x-trilium-auto
@dataclass class Repository:

    table: str

    db: InitVar[object]

    def __post_init__(
        self,
        db
    ):
        print(
            "Connect:",
            db
        )
```

Database Connection

↓

không lưu vào object.

---

# 9. Ví dụ Config

```text-x-trilium-auto
@dataclass class Parser:

    encoding: str

    config: InitVar[dict]

    def __post_init__(
        self,
        config
    ):
        self.encoding = config.get(
            "encoding",
            self.encoding
        )
```

Config chỉ dùng lúc khởi tạo.

---

# 10. Có nhiều InitVar

```text-x-trilium-auto
from dataclasses import InitVar

@dataclass class Demo:

    x: int

    a: InitVar[int]

    b: InitVar[int]

    c: InitVar[int]

    def __post_init__(
        self,
        a,
        b,
        c
    ):
        print(a, b, c)
```

---

# 11. Thứ tự **post_init**

Nếu có

```text-x-trilium-auto
a

b

c
```

thì

```text-x-trilium-auto
__post_init__(

a,

b,

c

)
```

theo đúng thứ tự khai báo.

---

# 12. fields()

```text-x-trilium-auto
from dataclasses import fields

print(fields(User))
```

Kết quả

```text-x-trilium-auto
username

password_hash
```

Không có

```text-x-trilium-auto
password
```

Vì `InitVar` **không phải field thực sự**.

---

# 13. asdict()

```text-x-trilium-auto
from dataclasses import asdict

print(asdict(u))
```

Kết quả

```text-x-trilium-auto
{
'username':'alice',

'password_hash':'...'
}
```

Không có password.

---

# 14. repr()

Không xuất hiện.

```text-x-trilium-auto
User(
username='alice'
)
```

---

# 15. replace()

Lưu ý.

```text-x-trilium-auto
replace(
    user
)
```

không thể tự động khôi phục các `InitVar` đã truyền lúc tạo đối tượng, vì chúng không được lưu trong object.

Nếu `InitVar` không có giá trị mặc định và `__post_init__()` cần đến nó, bạn sẽ phải truyền lại giá trị khi gọi `replace()`.

Ví dụ:

```text-x-trilium-auto
from dataclasses import dataclass, InitVar, replace

@dataclass class User:
    name: str
    password: InitVar[str]

    def __post_init__(self, password):
        print(password)

u = User("Alice", "123")

# Cần truyền lại password u2 = replace(u, password="456")
```

---

# 16. Kết hợp Frozen

```text-x-trilium-auto
@dataclass(
    frozen=True
)
class User:

    username: str

    password: InitVar[str]
```

Trong `__post_init__()` nếu cần gán giá trị cho field thật của object, bạn phải dùng:

```text-x-trilium-auto
object.__setattr__(
    self,
    "password_hash",
    value
)
```

vì đối tượng đã là immutable.

---

# 17. Kết hợp Slots

```text-x-trilium-auto
@dataclass(
    slots=True
)
class User:

    username: str

    password: InitVar[str]
```

Hoàn toàn hợp lệ.

`InitVar` không chiếm thêm slot vì nó không được lưu trong object.

---

# 18. Crawler Project

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass from dataclasses import InitVar

@dataclass class CrawlTask:

    url: str

    html: str = ""

    client: InitVar[object]

    def __post_init__(
        self,
        client
    ):
        self.html = client.get(
            self.url
        )
```

Sau khi khởi tạo

↓

client biến mất.

Object chỉ còn

```text-x-trilium-auto
url

html
```

---

# 19. Một ví dụ thực tế hơn

```text-x-trilium-auto
from dataclasses import dataclass, InitVar

@dataclass class Chapter:

    title: str
    content: str = ""

    parser: InitVar[object]

    def __post_init__(self, parser):
        self.content = parser.parse(self.title)
```

Parser chỉ dùng để lấy dữ liệu ban đầu, sau đó không cần lưu trong `Chapter`.

---

# 20. Khi nào nên dùng?

Rất phù hợp với:

- Password
- Access Token
- HTTP Client
- Database Session
- SQLAlchemy Session
- SQLite Connection
- API Client
- Temporary Config
- Parser
- Logger khởi tạo
- Dependency Injection

Đây đều là các đối tượng phục vụ việc khởi tạo chứ không phải trạng thái của object.

---

# 21. Khi nào không nên?

Không dùng `InitVar` cho dữ liệu mà object cần giữ lâu dài.

Ví dụ:

```text-x-trilium-auto
name

age

email

price

title

url
```

Đây đều là **state** của object.

Phải là field bình thường.

---

# 22. So sánh Field và InitVar

| Đặc điểm | Field | InitVar |
| --- | --- | --- |
| Có trong object | ✔   | ✘   |
| Có trong `fields()` | ✔   | ✘   |
| Có trong `asdict()` | ✔   | ✘   |
| Có trong `repr()` | ✔ (trừ `repr=False`) | ✘   |
| Có trong `__post_init__()` | ✔ (qua `self`) | ✔ (qua tham số) |
| Được lưu lâu dài | ✔   | ✘   |

---

# 23. Kiến trúc cho dự án crawler

Ví dụ:

```text-x-trilium-auto
from dataclasses import dataclass, InitVar

@dataclass(slots=True)
class Chapter:

    title: str
    url: str
    html: str = ""

    http_client: InitVar[object]

    def __post_init__(self, http_client):
        self.html = http_client.get(self.url)
```

Hoặc:

```text-x-trilium-auto
@dataclass class TruyenFullParser:

    novel_url: str

    session: InitVar[object]

    def __post_init__(self, session):
        # tải metadata ban đầu
        ...
```

Ý tưởng là:

- `session` chỉ phục vụ quá trình khởi tạo.
- Object sau khi tạo chỉ giữ **dữ liệu**, không giữ **phụ thuộc (dependency)** nếu không cần thiết.

---

# Best Practice

✅ Dùng `InitVar` khi:

- Dữ liệu chỉ phục vụ việc khởi tạo.
- Muốn giảm trạng thái lưu trong object.
- Muốn tách rõ "tham số khởi tạo" và "trạng thái của object".

❌ Không dùng khi:

- Dữ liệu cần được truy cập nhiều lần sau khi tạo object.
- Dữ liệu là một phần của mô hình nghiệp vụ (domain model).

---

# Tổng kết

| Thành phần | Vai trò |
| --- | --- |
| `InitVar[T]` | Biến chỉ dùng khi khởi tạo |
| `__post_init__()` | Nhận các `InitVar` để xử lý |
| `fields()` | Không chứa `InitVar` |
| `asdict()` | Không chứa `InitVar` |
| `replace()` | Có thể cần truyền lại `InitVar` |
| Kết hợp tốt | `slots=True`, `frozen=True`, `kw_only=True` |

---

# Bài tập thực hành

## Bài 1

Tạo:

```text-x-trilium-auto
@dataclass class User:
    username: str
    password_hash: str = ""
    password: InitVar[str] = ""
```

Trong `__post_init__()`:

- Hash mật khẩu bằng `hashlib.sha256`.
- Không lưu mật khẩu gốc.
- Kiểm tra `hasattr(user, "password")`.

---

## Bài 2

Thiết kế:

```text-x-trilium-auto
@dataclass class DatabaseConfig:
    host: str
    port: int
    config: InitVar[dict]
```

Trong `__post_init__()`:

- Nếu `config` có khóa `"port"` thì ghi đè `self.port`.
- Kiểm tra `fields()` và `asdict()`.

---

## Bài 3 (Áp dụng dự án crawler)

Thiết kế:

```text-x-trilium-auto
@dataclass(slots=True)
class CrawlRequest:
    url: str
    html: str = ""
    client: InitVar[HttpClient]
```

Trong `__post_init__()`:

- Dùng `client.get(url)` để lấy HTML.
- Lưu HTML vào `self.html`.
- Xác nhận rằng `client` không còn tồn tại sau khi khởi tạo.

---

# Chuẩn bị cho Buổi 10

Buổi tiếp theo chúng ta sẽ học **Inheritance Deep Dive** – một trong những chủ đề phức tạp nhất của `dataclass`.

Bạn sẽ tìm hiểu:

- Dataclass kế thừa hoạt động như thế nào.
- Constructor (`__init__`) được sinh khi có nhiều lớp.
- Gọi `super()` trong `__post_init__()`.
- Ghi đè (override) field.
- Thứ tự field giữa lớp cha và lớp con.
- Kết hợp với `slots`, `frozen`, `kw_only`, `InitVar`.
- Thiết kế hệ thống model nhiều tầng cho dự án crawler (BaseModel → Novel → Chapter → Image...). Đây là nền tảng để xây dựng các mô hình dữ liệu lớn và chuyên nghiệp.