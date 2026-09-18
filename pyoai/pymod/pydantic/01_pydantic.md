# Pydantic v2 — Buổi 1: Pydantic là gì? `BaseModel` và Validation cơ bản

> Khóa học: Làm chủ Pydantic v2 từ A–Z (2026 Edition)
>
> Buổi 1/50 — Foundation

Buổi học này sẽ đặt nền móng cho toàn bộ khóa Pydantic. Theo đúng lộ trình học Python của bạn (DDD, SOLID, Repository, Novel Crawler), chúng ta sẽ học Pydantic như một thư viện mô hình hóa dữ liệu (Data Modeling + Validation) chứ không chỉ là thư viện kiểm tra kiểu dữ liệu.

# Mục tiêu buổi học

Sau buổi này bạn sẽ hiểu và làm được:

* Hiểu Pydantic giải quyết vấn đề gì.

* Phân biệt Type Hint và Runtime Validation.

* Biết `BaseModel` hoạt động như thế nào.

* Tạo model đầu tiên.

* Parse `dict` thành object.

* Validation tự động.

* Đọc và hiểu `ValidationError`.

* Áp dụng vào dữ liệu crawl truyện.

Kết quả sau buổi này

# Bạn sẽ viết được Request/Response Model đầu tiên cho Fetcher của Novel Crawler.

# Phần 1 — Pydantic là gì?

## Một định nghĩa ngắn gọn

Pydantic là thư viện giúp Python:

> Biến dữ liệu không đáng tin cậy thành object Python đã được kiểm tra hợp lệ.

Nguồn dữ liệu không đáng tin cậy gồm:

<table class="_6IUVGW_Table" data-d-column-sizing="auto" data-d-dividers="" style="table-layout: auto;"><tbody><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-has-width="" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Nguồn dữ liệu</span></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Ví dụ trong Novel Crawler</span></p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">HTTP Response</td><td data-d-component="table-cell" data-d-valign="start">JSON trả về từ API.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">HTML Parser</td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text">Parser trả về <code class="er4J8W_Code" data-d-component="code">dict</code> chứa title, author, url...</p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">SQLite</td><td data-d-component="table-cell" data-d-valign="start">Dữ liệu đọc từ database.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">YAML / JSON Config</td><td data-d-component="table-cell" data-d-valign="start">Cấu hình crawler.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">CLI Arguments</td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">--timeout=30</code>.</p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Environment Variables</td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">DATABASE_URL</code>, <code class="er4J8W_Code" data-d-component="code">PROXY</code>...</p></td></tr></tbody></table>

## Vì sao cần Pydantic?

Giả sử parser trả về:

Python

Chạy

```
novel = {
    "title": "Đấu Phá Thương Khung",
    "author": "Thiên Tằm Thổ Đậu",
    "chapter_count": "1520",
    "completed": "true"
}
```

Thoạt nhìn có vẻ đúng.

Nhưng thực tế:

<table class="_6IUVGW_Table" data-d-column-sizing="auto" data-d-dividers="" style="table-layout: auto;"><tbody><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-has-width="" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Field</span></p></td><td data-d-component="table-cell" data-d-has-width="" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Kiểu mong muốn</span></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Dữ liệu parser</span></p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">title</td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">str</code></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">"Đấu Phá Thương Khung"</code> ✅</p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">author</td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">str</code></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">"Thiên Tằm Thổ Đậu"</code> ✅</p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">chapter_count</td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">int</code></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">"1520"</code> ❌</p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">completed</td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">bool</code></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">"true"</code> ❌</p></td></tr></tbody></table>

Nếu dùng Python thuần thì bạn phải tự kiểm tra từng field.

Pydantic làm việc đó tự động.

# Phần 2 — Type Hint KHÔNG phải Validation

Đây là kiến thức cực kỳ quan trọng.

## Type Hint chỉ là gợi ý

Python

Chạy

```
class Novel:
    def __init__(self, title: str, chapter_count: int):
        self.title = title
        self.chapter_count = chapter_count


novel = Novel("ĐPTK", "1500")

print(type(novel.chapter_count))
```

Kết quả:

Python

Chạy

```
<class 'str'>
```

Không có lỗi.

Python không kiểm tra kiểu dữ liệu.

## Type Hint chỉ giúp IDE

![Python Types Intro - FastAPI](https://images.openai.com/static-rsc-4/-4wXa2vCQH_HH9mVtFwAaiwYOtQrLpNOelTEibO7WFulsncwSFUaTpnGJro1qNjvzlH4VdkAr_abP2Wfx5aaDc38n-05-uHoi8cWCgA1wVdTemO3VgG3UiGHZQjQxpljQKq5DQ4Bp1321tVOH-9MV1jWbSLQKSwQ_TGXaQAEo8g?purpose=inline)

![FastAPI - Quick Guide](https://images.openai.com/static-rsc-4/s9qhcmE-Ft3ecpt5gLCpeDotF_MimV8ur09hq98thbheXCsYhc67a8miioVxV4EHyxxR4yMpfE57_RhCTcMcEmyiLM-Dm7ymBhoV6MFqDDXwIG9_ayhk9rITPxVDQYnK_YTbzY9fRWbGFfhxlkZqMH-4CXZuTTdotjen7ubgAwg?purpose=inline)

![Python's type hints - DEV Community](https://images.openai.com/static-rsc-4/e1llX3j4iuJgr-HLJehKhMbhepGesVLxYl4RzoS7hXTn5xBuX_EWS3egdJXMN-NF2loxPx5oQZu7iW-WpC4qsVyRTU2fvTOupUVC5Ej5xIUn2sjP_bmPgRBiJeVV_uGGOb0Z_9nzOZQ4lTezLFGxuktcq5NADdIjTs1Z5r0kKBs?purpose=inline)

5

IDE cảnh báo.

Nhưng khi chạy chương trình:

Python

Chạy

```
Novel("ĐPTK", "1500")
```

Python vẫn chấp nhận.

## Runtime Validation mới là nhiệm vụ của Pydantic

Python

Chạy

```
from pydantic import BaseModel

class Novel(BaseModel):
    title: str
    chapter_count: int

novel = Novel(
    title="ĐPTK",
    chapter_count="1500"
)

print(novel.chapter_count)
print(type(novel.chapter_count))
```

Kết quả:

Python

Chạy

```
1500
<class 'int'>
```

Pydantic:

* đọc type hint.

* validate.

* convert nếu hợp lệ.

# Phần 3 — Cài đặt Pydantic v2

## Cài bằng uv (khuyến nghị)

Bash

```
uv add pydantic
```

## Hoặc pip

Bash

```
pip install pydantic
```

## Kiểm tra phiên bản

Python

Chạy

```
import pydantic

print(pydantic.__version__)
```

Ví dụ:

```
2.12.x
```

> Khóa học này dùng Pydantic v2.

# Phần 4 — BaseModel đầu tiên

## Ví dụ hoàn chỉnh

Python

Chạy

```
from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    email: str
    active: bool


user = User(
    id=1,
    username="garden",
    email="garden@example.com",
    active=True,
)

print(user)
print(type(user))
```

## Kết quả

```
id=1 username='garden' email='garden@example.com' active=True

<class '__main__.User'>
```

Đây không còn là dict.

Đây là object.

## Giải thích từng dòng

<table class="_6IUVGW_Table" data-d-column-sizing="auto" data-d-dividers="" style="table-layout: auto;"><tbody><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-has-width="" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Code</span></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Ý nghĩa</span></p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">class User(BaseModel)</code></p></td><td data-d-component="table-cell" data-d-valign="start">Khai báo một model Pydantic.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">id: int</code></p></td><td data-d-component="table-cell" data-d-valign="start">Field bắt buộc kiểu int.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">username: str</code></p></td><td data-d-component="table-cell" data-d-valign="start">Field bắt buộc kiểu string.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">active: bool</code></p></td><td data-d-component="table-cell" data-d-valign="start">Field bool.</td></tr></tbody></table>

## Truy cập field

Python

Chạy

```
print(user.id)
print(user.username)
```

Không cần:

Python

Chạy

```
user["id"]
```

Đây là object thực sự.

# Phần 5 — Parse dict thành Model

Đây là tính năng dùng rất nhiều trong crawler.

## Parser trả về dict

Python

Chạy

```
data = {
    "id": 1,
    "username": "garden",
    "email": "garden@example.com",
    "active": True,
}
```

## Parse

Python

Chạy

```
user = User(**data)

print(user)
```

Hoặc cách chuẩn Pydantic v2:

Python

Chạy

```
user = User.model_validate(data)
```

Hai cách đều tạo object.

## Vì sao `model_validate()` được khuyến nghị?

Bởi vì nó còn parse:

* dict

* object

* ORM

* mapping

Chúng ta sẽ học sâu ở Buổi 7.

# Phần 6 — Validation tự động

## Ví dụ 1 — String thành Integer

Python

Chạy

```
user = User(
    id="5",
    username="garden",
    email="garden@example.com",
    active=True,
)

print(user.id)
print(type(user.id))
```

Kết quả

```
5
<class 'int'>
```

Pydantic convert `"5"` → `5`.

## Ví dụ 2 — Bool

Python

Chạy

```
user = User(
    id=1,
    username="garden",
    email="garden@example.com",
    active="true",
)

print(user.active)
print(type(user.active))
```

Kết quả

```
True
<class 'bool'>
```

## Những giá trị bool được hiểu

<table class="_6IUVGW_Table" data-d-column-sizing="auto" data-d-dividers="" style="table-layout: auto;"><tbody><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-has-width="" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Input</span></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Output</span></p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">"true"</code></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">True</code></p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">"false"</code></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">False</code></p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">"yes"</code></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">True</code></p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">"no"</code></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">False</code></p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">1</code></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">True</code></p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">0</code></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">False</code></p></td></tr></tbody></table>

# Phần 7 — ValidationError

## Ví dụ

Python

Chạy

```
from pydantic import BaseModel, ValidationError


class User(BaseModel):
    id: int
    username: str
    active: bool


try:
    User(
        id="abc",
        username=123,
        active="hello",
    )
except ValidationError as e:
    print(e)
```

## Kết quả

```
3 validation errors for User

id
  Input should be a valid integer

username
  Input should be a valid string

active
  Input should be a valid boolean
```

Pydantic báo tất cả lỗi cùng lúc.

Đây là điểm mạnh.

## Đọc lỗi có cấu trúc

Python

Chạy

```
try:
    User(...)
except ValidationError as e:
    print(e.errors())
```

Kết quả:

Python

Chạy

```
[
    {
        "type": "int_parsing",
        "loc": ("id",),
        "msg": "Input should be a valid integer",
        "input": "abc",
    },
    ...
]
```

### Ý nghĩa

<table class="_6IUVGW_Table" data-d-column-sizing="auto" data-d-dividers="" style="table-layout: auto;"><tbody><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-has-width="" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Key</span></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Ý nghĩa</span></p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">type</code></p></td><td data-d-component="table-cell" data-d-valign="start">Loại lỗi.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">loc</code></p></td><td data-d-component="table-cell" data-d-valign="start">Field bị lỗi.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">msg</code></p></td><td data-d-component="table-cell" data-d-valign="start">Thông báo.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">input</code></p></td><td data-d-component="table-cell" data-d-valign="start">Giá trị gây lỗi.</td></tr></tbody></table>

Trong production rất hữu ích để logging.

# Phần 8 — Type Coercion (Tự động chuyển kiểu)

Pydantic mặc định coerce dữ liệu.

## Ví dụ

Python

Chạy

```
from pydantic import BaseModel


class Product(BaseModel):
    id: int
    price: float
    available: bool


product = Product(
    id="10",
    price="99.5",
    available="yes",
)

print(product)
print(type(product.id))
print(type(product.price))
print(type(product.available))
```

## Kết quả

```
id=10 price=99.5 available=True

int
float
bool
```

## Minh họa quá trình

![](data\:image/svg+xml;charset=utf-8,%3Csvg%20font-family%3D%22-apple-system-body%2C%20ui-sans-serif%2C%20-apple-system%2C%20system-ui%2C%20Segoe%20UI%2C%20Helvetica%2C%20Apple%20Color%20Emoji%2C%20Arial%2C%20sans-serif%2C%20Segoe%20UI%20Emoji%2C%20Segoe%20UI%20Symbol%22%20font-weight%3D%22400%22%20data-d-component%3D%22svg%22%20fill%3D%22currentColor%22%20style%3D%22color%3Argb\(13%2C%2013%2C%2013\)%22%20viewBox%3D%220%200%20740%20220%22%20width%3D%22100%25%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Crect%20x%3D%2220%22%20y%3D%2220%22%20width%3D%22180%22%20height%3D%22180%22%20rx%3D%2212%22%20fill%3D%22%23F59E0B22%22%20stroke%3D%22%23F59E0B%22%2F%3E%3Ctext%20x%3D%22110%22%20y%3D%2255%22%20text-anchor%3D%22middle%22%20fill%3D%22%23F59E0B%22%20font-size%3D%2216%22%3EInput%3C%2Ftext%3E%3Ctext%20x%3D%2240%22%20y%3D%2290%22%20fill%3D%22currentColor%22%20font-size%3D%2214%22%3Eid%3D%2210%22%3C%2Ftext%3E%3Ctext%20x%3D%2240%22%20y%3D%22120%22%20fill%3D%22currentColor%22%20font-size%3D%2214%22%3Eprice%3D%2299.5%22%3C%2Ftext%3E%3Ctext%20x%3D%2240%22%20y%3D%22150%22%20fill%3D%22currentColor%22%20font-size%3D%2214%22%3Eavailable%3D%22yes%22%3C%2Ftext%3E%3Crect%20x%3D%22270%22%20y%3D%2255%22%20width%3D%22200%22%20height%3D%22110%22%20rx%3D%2214%22%20fill%3D%22%232563EB22%22%20stroke%3D%22%232563EB%22%2F%3E%3Ctext%20x%3D%22370%22%20y%3D%2295%22%20text-anchor%3D%22middle%22%20fill%3D%22%232563EB%22%20font-size%3D%2216%22%3EPydantic%20Core%3C%2Ftext%3E%3Ctext%20x%3D%22370%22%20y%3D%22125%22%20text-anchor%3D%22middle%22%20fill%3D%22currentColor%22%20font-size%3D%2213%22%3EValidation%20%2B%20Conversion%3C%2Ftext%3E%3Crect%20x%3D%22540%22%20y%3D%2220%22%20width%3D%22180%22%20height%3D%22180%22%20rx%3D%2212%22%20fill%3D%22%2316A34A22%22%20stroke%3D%22%2316A34A%22%2F%3E%3Ctext%20x%3D%22630%22%20y%3D%2255%22%20text-anchor%3D%22middle%22%20fill%3D%22%2316A34A%22%20font-size%3D%2216%22%3EOutput%3C%2Ftext%3E%3Ctext%20x%3D%22560%22%20y%3D%2290%22%20fill%3D%22currentColor%22%20font-size%3D%2214%22%3Eid%3D10%3C%2Ftext%3E%3Ctext%20x%3D%22560%22%20y%3D%22120%22%20fill%3D%22currentColor%22%20font-size%3D%2214%22%3Eprice%3D99.5%3C%2Ftext%3E%3Ctext%20x%3D%22560%22%20y%3D%22150%22%20fill%3D%22currentColor%22%20font-size%3D%2214%22%3Eavailable%3DTrue%3C%2Ftext%3E%3Cpath%20d%3D%22M200%20110%20L270%20110%22%20stroke%3D%22currentColor%22%20stroke-width%3D%222%22%20marker-end%3D%22url\(%23a\)%22%2F%3E%3Cpath%20d%3D%22M470%20110%20L540%20110%22%20stroke%3D%22currentColor%22%20stroke-width%3D%222%22%20marker-end%3D%22url\(%23a\)%22%2F%3E%3Cdefs%3E%3Cmarker%20id%3D%22a%22%20markerWidth%3D%228%22%20markerHeight%3D%228%22%20refX%3D%227%22%20refY%3D%224%22%20orient%3D%22auto%22%3E%3Cpolygon%20points%3D%220%2C0%208%2C4%200%2C8%22%20fill%3D%22currentColor%22%2F%3E%3C%2Fmarker%3E%3C%2Fdefs%3E%3C%2Fsvg%3E)

# Phần 9 — Model có giá trị mặc định

Python

Chạy

```
from pydantic import BaseModel


class Novel(BaseModel):
    title: str
    author: str
    completed: bool = False
    chapter_count: int = 0


novel = Novel(
    title="Đấu Phá Thương Khung",
    author="Thiên Tằm Thổ Đậu",
)

print(novel)
```

## Kết quả

```
title='Đấu Phá Thương Khung'
author='Thiên Tằm Thổ Đậu'
completed=False
chapter_count=0
```

Field có default không bắt buộc nhập.

# Phần 10 — Required Field

## Thiếu field

Python

Chạy

```
Novel(
    title="ĐPTK"
)
```

Kết quả:

```
ValidationError

author
 Field required
```

Pydantic phân biệt:

<table class="_6IUVGW_Table" data-d-column-sizing="auto" data-d-dividers="" style="table-layout: auto;"><tbody><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-has-width="" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Loại field</span></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Bắt buộc?</span></p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">title: str</code></p></td><td data-d-component="table-cell" data-d-valign="start">✅ Có</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">title: str = "abc"</code></p></td><td data-d-component="table-cell" data-d-valign="start">❌ Không</td></tr></tbody></table>

# Phần 11 — Dict vs BaseModel

## Dict truyền thống

Python

Chạy

```
novel = {
    "title": "ĐPTK",
    "author": "Thiên Tằm",
}

print(novel["title"])
```

### Nhược điểm

Python

Chạy

```
novel["titlte"]
```

Lỗi:

```
KeyError
```

Không biết trước.

## BaseModel

Python

Chạy

```
print(novel.title)
```

IDE autocomplete.

Sai tên:

Python

Chạy

```
novel.titlte
```

IDE báo ngay.

## So sánh

<table class="_6IUVGW_Table" data-d-column-sizing="auto" data-d-dividers="" style="table-layout: auto;"><tbody><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Dict</span></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">BaseModel</span></p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Không validate.</td><td data-d-component="table-cell" data-d-valign="start">Có validate.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Không convert kiểu.</td><td data-d-component="table-cell" data-d-valign="start">Tự convert.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Không autocomplete.</td><td data-d-component="table-cell" data-d-valign="start">Autocomplete.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Không schema.</td><td data-d-component="table-cell" data-d-valign="start">Có schema.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Dễ thiếu key.</td><td data-d-component="table-cell" data-d-valign="start">Field required.</td></tr></tbody></table>

# Phần 12 — Ví dụ hoàn chỉnh: Parser Novel

Giả sử parser HTML trả về `dict`.

## Parser (giả lập)

Python

Chạy

```
parser_output = {
    "title": "Đấu Phá Thương Khung",
    "author": "Thiên Tằm Thổ Đậu",
    "url": "https://example.com/dau-pha-thuong-khung",
    "cover": "https://example.com/cover.jpg",
    "chapter_count": "1648",
    "completed": "true",
}
```

## Model

Python

Chạy

```
from pydantic import BaseModel


class NovelSummary(BaseModel):
    title: str
    author: str
    url: str
    cover: str
    chapter_count: int
    completed: bool


parser_output = {
    "title": "Đấu Phá Thương Khung",
    "author": "Thiên Tằm Thổ Đậu",
    "url": "https://example.com/dau-pha-thuong-khung",
    "cover": "https://example.com/cover.jpg",
    "chapter_count": "1648",
    "completed": "true",
}


novel = NovelSummary.model_validate(parser_output)

print(novel)
print(type(novel.chapter_count))
print(type(novel.completed))
```

## Kết quả

```
chapter_count = 1648
completed = True
```

Parser không cần quan tâm kiểu.

Pydantic xử lý ở boundary.

# Phần 13 — Vị trí Pydantic trong Novel Crawler

Đây là kiến trúc chúng ta sẽ dùng suốt khóa.

![](data\:image/svg+xml;charset=utf-8,%3Csvg%20font-family%3D%22-apple-system-body%2C%20ui-sans-serif%2C%20-apple-system%2C%20system-ui%2C%20Segoe%20UI%2C%20Helvetica%2C%20Apple%20Color%20Emoji%2C%20Arial%2C%20sans-serif%2C%20Segoe%20UI%20Emoji%2C%20Segoe%20UI%20Symbol%22%20font-weight%3D%22400%22%20data-d-component%3D%22svg%22%20fill%3D%22currentColor%22%20style%3D%22color%3Argb\(13%2C%2013%2C%2013\)%22%20viewBox%3D%220%200%20740%20540%22%20width%3D%22100%25%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Crect%20x%3D%22170%22%20y%3D%2210%22%20width%3D%22400%22%20height%3D%2250%22%20rx%3D%2210%22%20fill%3D%22%232563EB22%22%20stroke%3D%22%232563EB%22%2F%3E%3Ctext%20x%3D%22370%22%20y%3D%2240%22%20text-anchor%3D%22middle%22%20fill%3D%22%232563EB%22%20font-size%3D%2216%22%3EHTTPX%20Fetcher%3C%2Ftext%3E%3Crect%20x%3D%22170%22%20y%3D%2290%22%20width%3D%22400%22%20height%3D%2260%22%20rx%3D%2210%22%20fill%3D%22%23EA580C22%22%20stroke%3D%22%23EA580C%22%2F%3E%3Ctext%20x%3D%22370%22%20y%3D%22120%22%20text-anchor%3D%22middle%22%20fill%3D%22%23EA580C%22%20font-size%3D%2216%22%3EParser%20\(selectolax\)%3C%2Ftext%3E%3Ctext%20x%3D%22370%22%20y%3D%22140%22%20text-anchor%3D%22middle%22%20fill%3D%22currentColor%22%20font-size%3D%2212%22%3Edict%20%2F%20list%20%2F%20raw%20data%3C%2Ftext%3E%3Crect%20x%3D%22150%22%20y%3D%22190%22%20width%3D%22440%22%20height%3D%2290%22%20rx%3D%2212%22%20fill%3D%22%2316A34A22%22%20stroke%3D%22%2316A34A%22%20stroke-width%3D%222%22%2F%3E%3Ctext%20x%3D%22370%22%20y%3D%22220%22%20text-anchor%3D%22middle%22%20fill%3D%22%2316A34A%22%20font-size%3D%2217%22%3EPydantic%20DTO%20Layer%3C%2Ftext%3E%3Ctext%20x%3D%22370%22%20y%3D%22245%22%20text-anchor%3D%22middle%22%20fill%3D%22currentColor%22%20font-size%3D%2213%22%3ENovelSummaryDTO%3C%2Ftext%3E%3Ctext%20x%3D%22370%22%20y%3D%22262%22%20text-anchor%3D%22middle%22%20fill%3D%22currentColor%22%20font-size%3D%2213%22%3EChapterDTO%3C%2Ftext%3E%3Crect%20x%3D%22170%22%20y%3D%22330%22%20width%3D%22400%22%20height%3D%2260%22%20rx%3D%2210%22%20fill%3D%22%237C3AED22%22%20stroke%3D%22%237C3AED%22%2F%3E%3Ctext%20x%3D%22370%22%20y%3D%22365%22%20text-anchor%3D%22middle%22%20fill%3D%22%237C3AED%22%20font-size%3D%2216%22%3EDomain%20Entity%3C%2Ftext%3E%3Crect%20x%3D%22170%22%20y%3D%22430%22%20width%3D%22400%22%20height%3D%2260%22%20rx%3D%2210%22%20fill%3D%22%2364748B22%22%20stroke%3D%22%2364748B%22%2F%3E%3Ctext%20x%3D%22370%22%20y%3D%22465%22%20text-anchor%3D%22middle%22%20fill%3D%22%2364748B%22%20font-size%3D%2216%22%3ESQLite%20Repository%3C%2Ftext%3E%3Cpath%20d%3D%22M370%2060V90M370%20150V190M370%20280V330M370%20390V430%22%20stroke%3D%22currentColor%22%20stroke-width%3D%222%22%20marker-end%3D%22url\(%23arr\)%22%2F%3E%3Cdefs%3E%3Cmarker%20id%3D%22arr%22%20markerWidth%3D%228%22%20markerHeight%3D%228%22%20refX%3D%224%22%20refY%3D%224%22%20orient%3D%22auto%22%3E%3Cpolygon%20points%3D%220%2C0%208%2C4%200%2C8%22%20fill%3D%22currentColor%22%2F%3E%3C%2Fmarker%3E%3C%2Fdefs%3E%3C%2Fsvg%3E)

## Giải thích

<table class="_6IUVGW_Table" data-d-column-sizing="auto" data-d-dividers="" style="table-layout: auto;"><tbody><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-has-width="" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Layer</span></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Vai trò</span></p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Fetcher</td><td data-d-component="table-cell" data-d-valign="start">Lấy HTML.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Parser</td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text">Trích xuất dữ liệu thô (<code class="er4J8W_Code" data-d-component="code">dict</code>).</p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Pydantic DTO</span></p></td><td data-d-component="table-cell" data-d-valign="start">Validate và chuẩn hóa dữ liệu parser.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Domain Entity</td><td data-d-component="table-cell" data-d-valign="start">Logic nghiệp vụ.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Repository</td><td data-d-component="table-cell" data-d-valign="start">Lưu SQLite.</td></tr></tbody></table>

> Best Practice DDD: Parser chỉ trả về dữ liệu thô; Pydantic là lớp kiểm tra dữ liệu ở ranh giới (boundary); Domain Entity không kế thừa `BaseModel`.

# Phần 14 — Sai lầm người mới thường gặp

## Sai lầm 1 — Dùng Pydantic làm Entity

Python

Chạy

```
class Novel(BaseModel):
    ...
```

Sau đó thêm business logic.

❌ Không nên trong Clean Architecture.

Nên tách:

```
NovelDTO (Pydantic)
       ↓ Mapper
Novel Entity (dataclass/class)
```

## Sai lầm 2 — Tin tưởng parser

Python

Chạy

```
chapter_count = parser["chapter_count"]
```

Nếu parser trả `"N/A"`.

Lỗi xuất hiện rất muộn.

Hãy validate ngay khi parser kết thúc.

## Sai lầm 3 — Bắt `Exception`

Nên bắt:

Python

Chạy

```
from pydantic import ValidationError

try:
    NovelSummary.model_validate(data)
except ValidationError as e:
    ...
```

# Phần 15 — Best Practices Buổi 1

<table class="_6IUVGW_Table" data-d-column-sizing="auto" data-d-dividers="" style="table-layout: auto;"><tbody><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-has-width="" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Nên làm</span></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Không nên</span></p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Validate dữ liệu ở boundary.</td><td data-d-component="table-cell" data-d-valign="start">Validate rải rác trong business logic.</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text">Dùng <code class="er4J8W_Code" data-d-component="code">model_validate()</code> để parse dữ liệu.</p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text">Tự ép kiểu từng field bằng <code class="er4J8W_Code" data-d-component="code">int()</code>, <code class="er4J8W_Code" data-d-component="code">bool()</code>.</p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text">Bắt <code class="er4J8W_Code" data-d-component="code">ValidationError</code> riêng.</p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text">Bắt <code class="er4J8W_Code" data-d-component="code">Exception</code> chung chung.</p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Dùng DTO để giao tiếp giữa các layer.</td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text">Dùng <code class="er4J8W_Code" data-d-component="code">dict</code> xuyên suốt toàn bộ ứng dụng.</p></td></tr></tbody></table>

# Mini Project — Validate dữ liệu Parser

## Yêu cầu

Viết model `NovelSummaryDTO` gồm:

<table class="_6IUVGW_Table" data-d-column-sizing="auto" data-d-dividers="" style="table-layout: auto;"><tbody><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-has-width="" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Field</span></p></td><td data-d-component="table-cell" data-d-has-width="" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Kiểu</span></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Bắt buộc</span></p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">title</td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">str</code></p></td><td data-d-component="table-cell" data-d-valign="start">✅</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">author</td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">str</code></p></td><td data-d-component="table-cell" data-d-valign="start">✅</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">url</td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">str</code></p></td><td data-d-component="table-cell" data-d-valign="start">✅</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">cover</td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">str</code></p></td><td data-d-component="table-cell" data-d-valign="start">✅</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">chapter_count</td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">int</code></p></td><td data-d-component="table-cell" data-d-valign="start">✅</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">completed</td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">bool</code></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text">❌ mặc định <code class="er4J8W_Code" data-d-component="code">False</code></p></td></tr></tbody></table>

### Test với 3 bộ dữ liệu

* Bộ hợp lệ.

* Bộ thiếu `author`.

* Bộ `chapter_count="abc"`.

Quan sát `ValidationError`.

# Tổng kết Buổi 1

## Kiến thức đã học

<table class="_6IUVGW_Table" data-d-column-sizing="auto" data-d-dividers="" style="table-layout: auto;"><tbody><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-has-width="" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Chủ đề</span></p></td><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><span class="w6asjq_TextBase _85PZeG_Text" data-d-component="text" data-d-default-strong="" data-d-inline="">Đã học</span></p></td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Pydantic là gì</td><td data-d-component="table-cell" data-d-valign="start">✅</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">BaseModel</code></p></td><td data-d-component="table-cell" data-d-valign="start">✅</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Tạo model đầu tiên</td><td data-d-component="table-cell" data-d-valign="start">✅</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text">Parse <code class="er4J8W_Code" data-d-component="code">dict</code> → object</p></td><td data-d-component="table-cell" data-d-valign="start">✅</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">model_validate()</code></p></td><td data-d-component="table-cell" data-d-valign="start">✅</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Validation tự động</td><td data-d-component="table-cell" data-d-valign="start">✅</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Type coercion</td><td data-d-component="table-cell" data-d-valign="start">✅</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start"><p class="w6asjq_TextBase _85PZeG_Text" data-d-component="text"><code class="er4J8W_Code" data-d-component="code">ValidationError</code></p></td><td data-d-component="table-cell" data-d-valign="start">✅</td></tr><tr data-d-component="table-row"><td data-d-component="table-cell" data-d-valign="start">Ứng dụng vào Novel Crawler</td><td data-d-component="table-cell" data-d-valign="start">✅</td></tr></tbody></table>

## Sơ đồ tư duy Buổi 1

![](data\:image/svg+xml;charset=utf-8,%3Csvg%20font-family%3D%22-apple-system-body%2C%20ui-sans-serif%2C%20-apple-system%2C%20system-ui%2C%20Segoe%20UI%2C%20Helvetica%2C%20Apple%20Color%20Emoji%2C%20Arial%2C%20sans-serif%2C%20Segoe%20UI%20Emoji%2C%20Segoe%20UI%20Symbol%22%20font-weight%3D%22400%22%20data-d-component%3D%22svg%22%20fill%3D%22currentColor%22%20style%3D%22color%3Argb\(13%2C%2013%2C%2013\)%22%20viewBox%3D%220%200%20740%20420%22%20width%3D%22100%25%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Crect%20x%3D%22220%22%20y%3D%2215%22%20width%3D%22300%22%20height%3D%2250%22%20rx%3D%2212%22%20fill%3D%22%2316A34A22%22%20stroke%3D%22%2316A34A%22%20stroke-width%3D%222%22%2F%3E%3Ctext%20x%3D%22370%22%20y%3D%2245%22%20text-anchor%3D%22middle%22%20fill%3D%22%2316A34A%22%20font-size%3D%2218%22%3EPydantic%20BaseModel%3C%2Ftext%3E%3Crect%20x%3D%2230%22%20y%3D%22120%22%20width%3D%22170%22%20height%3D%2270%22%20rx%3D%2210%22%20fill%3D%22%232563EB22%22%20stroke%3D%22%232563EB%22%2F%3E%3Ctext%20x%3D%22115%22%20y%3D%22155%22%20text-anchor%3D%22middle%22%20fill%3D%22%232563EB%22%20font-size%3D%2215%22%3EType%20Hint%3C%2Ftext%3E%3Ctext%20x%3D%22115%22%20y%3D%22172%22%20text-anchor%3D%22middle%22%20fill%3D%22currentColor%22%20font-size%3D%2212%22%3EKhai%20b%C3%A1o%20ki%E1%BB%83u%3C%2Ftext%3E%3Crect%20x%3D%22285%22%20y%3D%22120%22%20width%3D%22170%22%20height%3D%2270%22%20rx%3D%2210%22%20fill%3D%22%23EA580C22%22%20stroke%3D%22%23EA580C%22%2F%3E%3Ctext%20x%3D%22370%22%20y%3D%22150%22%20text-anchor%3D%22middle%22%20fill%3D%22%23EA580C%22%20font-size%3D%2215%22%3EValidation%3C%2Ftext%3E%3Ctext%20x%3D%22370%22%20y%3D%22168%22%20text-anchor%3D%22middle%22%20fill%3D%22currentColor%22%20font-size%3D%2212%22%3ERuntime%20checking%3C%2Ftext%3E%3Crect%20x%3D%22540%22%20y%3D%22120%22%20width%3D%22170%22%20height%3D%2270%22%20rx%3D%2210%22%20fill%3D%22%237C3AED22%22%20stroke%3D%22%237C3AED%22%2F%3E%3Ctext%20x%3D%22625%22%20y%3D%22150%22%20text-anchor%3D%22middle%22%20fill%3D%22%237C3AED%22%20font-size%3D%2215%22%3EType%20Coercion%3C%2Ftext%3E%3Ctext%20x%3D%22625%22%20y%3D%22168%22%20text-anchor%3D%22middle%22%20fill%3D%22currentColor%22%20font-size%3D%2212%22%3EConvert%20d%E1%BB%AF%20li%E1%BB%87u%3C%2Ftext%3E%3Crect%20x%3D%2230%22%20y%3D%22280%22%20width%3D%22170%22%20height%3D%2290%22%20rx%3D%2210%22%20fill%3D%22%2364748B22%22%20stroke%3D%22%2364748B%22%2F%3E%3Ctext%20x%3D%22115%22%20y%3D%22315%22%20text-anchor%3D%22middle%22%20fill%3D%22%2364748B%22%20font-size%3D%2215%22%3Edict%3C%2Ftext%3E%3Ctext%20x%3D%22115%22%20y%3D%22333%22%20text-anchor%3D%22middle%22%20fill%3D%22currentColor%22%20font-size%3D%2212%22%3EParser%20Output%3C%2Ftext%3E%3Crect%20x%3D%22285%22%20y%3D%22280%22%20width%3D%22170%22%20height%3D%2290%22%20rx%3D%2210%22%20fill%3D%22%2316A34A22%22%20stroke%3D%22%2316A34A%22%2F%3E%3Ctext%20x%3D%22370%22%20y%3D%22315%22%20text-anchor%3D%22middle%22%20fill%3D%22%2316A34A%22%20font-size%3D%2215%22%3EBaseModel%3C%2Ftext%3E%3Ctext%20x%3D%22370%22%20y%3D%22333%22%20text-anchor%3D%22middle%22%20fill%3D%22currentColor%22%20font-size%3D%2212%22%3EValidated%20Object%3C%2Ftext%3E%3Crect%20x%3D%22540%22%20y%3D%22280%22%20width%3D%22170%22%20height%3D%2290%22%20rx%3D%2210%22%20fill%3D%22%23DC262622%22%20stroke%3D%22%23DC2626%22%2F%3E%3Ctext%20x%3D%22625%22%20y%3D%22315%22%20text-anchor%3D%22middle%22%20fill%3D%22%23DC2626%22%20font-size%3D%2215%22%3EValidationError%3C%2Ftext%3E%3Ctext%20x%3D%22625%22%20y%3D%22333%22%20text-anchor%3D%22middle%22%20fill%3D%22currentColor%22%20font-size%3D%2212%22%3ED%E1%BB%AF%20li%E1%BB%87u%20kh%C3%B4ng%20h%E1%BB%A3p%20l%E1%BB%87%3C%2Ftext%3E%3Cpath%20d%3D%22M370%2065V120M200%20325H285M455%20325H540M370%20190V280%22%20stroke%3D%22currentColor%22%20stroke-width%3D%222%22%20marker-end%3D%22url\(%23m\)%22%2F%3E%3Cdefs%3E%3Cmarker%20id%3D%22m%22%20markerWidth%3D%228%22%20markerHeight%3D%228%22%20refX%3D%227%22%20refY%3D%224%22%20orient%3D%22auto%22%3E%3Cpolygon%20points%3D%220%2C0%208%2C4%200%2C8%22%20fill%3D%22currentColor%22%2F%3E%3C%2Fmarker%3E%3C%2Fdefs%3E%3C%2Fsvg%3E)

## Roadmap tiếp theo

Buổi 2 sẽ học Field và Type Annotation trong Pydantic v2. Chúng ta sẽ đi rất sâu vào:

1. Kiểu dữ liệu cơ bản (`str`, `int`, `float`, `bool`).

2. Collection (`list`, `tuple`, `set`, `dict`).

3. `Optional`, `Literal`, `Union`.

4. `Field()` và metadata (mô tả, giá trị mặc định, ràng buộc đơn giản).

5. Required field vs default field.

6. Áp dụng để thiết kế `NovelDTO`, `ChapterDTO` và `CrawlerConfigDTO` cho dự án Novel Crawler.
