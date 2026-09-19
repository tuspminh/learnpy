# Phần V — Novel Crawler

# Buổi 41 — Request Model

Ở Phần IV chúng ta đã xây được HTTP infrastructure. Sang Phần V, mục tiêu là **đóng gói nó thành Fetcher thực sự dành cho Novel Crawler**.

Buổi này tập trung duy nhất vào:

> **Thiết kế Request Model — object đại diện cho một yêu cầu fetch trong hệ thống crawler.**

---

# 1. Vấn đề của cách truyền tham số thông thường

Nếu không có Request Model, ta rất dễ viết:

```python
await fetcher.get(
    url,
    headers,
    params,
    timeout,
)
```

Sau này thêm:

```text
proxy
browser profile
retry
priority
referer
metadata
```

API sẽ phình ra:

```python
await fetcher.get(
    url,
    headers,
    params,
    timeout,
    proxy,
    browser_profile,
    retry,
    priority,
    referer,
    ...
)
```

Đây là dấu hiệu API đang trở nên khó quản lý.

---

# 2. Request Model giải quyết vấn đề đó

Ta gom request thành một object:

```python
request = FetchRequest(
    url="https://example.com/chapter-1",
    headers={
        "Accept": "text/html",
    },
    timeout=10,
)
```

Sau đó:

```python
response = await fetcher.get(request)
```

API Fetcher luôn ổn định:

```text
Fetcher
   │
   └── get(FetchRequest)
```

Dù sau này Request Model có thêm field.

---

# 3. Request Model nằm ở đâu?

Đây là câu hỏi quan trọng về Clean Architecture.

Ta có:

```text
domain/
application/
infrastructure/
```

`FetchRequest` là **contract của use case/Application**, vì Application cần nói:

> "Tôi muốn fetch resource này."

Nó không phải object riêng của `primp`.

Vì vậy:

```text
application/
└── ports/
    └── fetcher.py
```

có thể chứa:

```text
FetchRequest
FetchResponse
Fetcher
```

---

# 4. Request Model phiên bản đầu tiên

Ta bắt đầu đơn giản:

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class FetchRequest:

    url: str

    headers: dict[str, str] = field(
        default_factory=dict
    )

    params: dict[str, object] = field(
        default_factory=dict
    )

    timeout: float | None = None
```

Ví dụ:

```python
request = FetchRequest(
    url="https://example.com/chapter-1",
    headers={
        "Accept": "text/html",
    },
    params={
        "page": 1,
    },
    timeout=10,
)
```

---

# 5. Tại sao `@dataclass(frozen=True)`?

Ta muốn Request là **immutable**.

Sau khi tạo:

```python
request = FetchRequest(
    url="https://example.com/chapter-1"
)
```

không nên có:

```python
request.url = "https://evil.com"
```

Về mặt kiến trúc, request nên được coi là:

> Một mô tả bất biến của operation.

---

# 6. Nhưng có một chi tiết

`frozen=True` không làm nested dictionary immutable.

Ví dụ:

```python
request = FetchRequest(
    url="https://example.com",
    headers={
        "Accept": "text/html"
    }
)
```

vẫn có thể:

```python
request.headers["Accept"] = "application/json"
```

Do đó `frozen=True` ở đây chủ yếu ngăn:

```python
request.url = ...
```

chứ không biến toàn bộ object thành immutable sâu.

Đối với Request Model hiện tại, điều này chấp nhận được.

---

# 7. Validate URL

Ta không muốn:

```python
FetchRequest(
    url=""
)
```

hoặc:

```python
FetchRequest(
    url="hello"
)
```

Ta có thể thêm validation.

```python
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass(frozen=True)
class FetchRequest:

    url: str

    headers: dict[str, str] = field(
        default_factory=dict
    )

    params: dict[str, object] = field(
        default_factory=dict
    )

    timeout: float | None = None

    def __post_init__(self):

        if not self.url:
            raise ValueError(
                "URL cannot be empty"
            )

        parsed = urlparse(self.url)

        if parsed.scheme not in {
            "http",
            "https",
        }:
            raise ValueError(
                "URL must use http or https"
            )
```

---

# 8. Test Request Model

```python
request = FetchRequest(
    url="https://example.com/chapter-1"
)

print(request)
```

Kết quả:

```text
FetchRequest(
    url='https://example.com/chapter-1',
    headers={},
    params={},
    timeout=None
)
```

---

# 9. URL bắt buộc phải có

Test:

```python
request = FetchRequest(
    url=""
)
```

sẽ:

```text
ValueError:
URL cannot be empty
```

---

# 10. Scheme cũng được kiểm tra

```python
FetchRequest(
    url="ftp://example.com/file"
)
```

→

```text
ValueError:
URL must use http or https
```

Fetcher HTTP không nên nhận FTP.

---

# 11. Timeout

Field:

```python
timeout: float | None = None
```

Cho phép:

```python
FetchRequest(
    url=url
)
```

dùng timeout mặc định của Fetcher.

Hoặc:

```python
FetchRequest(
    url=url,
    timeout=5
)
```

override timeout cho request cụ thể.

---

# 12. Validate timeout

Không nên cho:

```python
timeout=-5
```

Ta thêm:

```python
if self.timeout is not None:
    if self.timeout <= 0:
        raise ValueError(
            "timeout must be > 0"
        )
```

Full:

```python
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass(frozen=True)
class FetchRequest:

    url: str

    headers: dict[str, str] = field(
        default_factory=dict
    )

    params: dict[str, object] = field(
        default_factory=dict
    )

    timeout: float | None = None

    def __post_init__(self):

        if not self.url:
            raise ValueError(
                "URL cannot be empty"
            )

        parsed = urlparse(self.url)

        if parsed.scheme not in {
            "http",
            "https",
        }:
            raise ValueError(
                "URL must use http or https"
            )

        if self.timeout is not None:
            if self.timeout <= 0:
                raise ValueError(
                    "timeout must be > 0"
                )
```

---

# 13. Headers

Headers thuộc Request Model vì Application có thể cần chỉ định:

```python
FetchRequest(
    url=url,
    headers={
        "Accept": "text/html",
        "Referer": "...",
    },
)
```

Nhưng có một nguyên tắc:

> Request-specific headers ≠ default headers.

Ví dụ default:

```text
Accept
Accept-Language
```

có thể thuộc Fetcher/Client configuration.

Request-specific:

```text
Referer
Authorization
```

có thể nằm trong Request.

---

# 14. Params

Ví dụ URL:

```text
https://example.com/search?page=2
```

không nhất thiết phải tự nối string.

```python
request = FetchRequest(
    url="https://example.com/search",
    params={
        "page": 2,
    },
)
```

Transport sẽ chuyển:

```text
params
   ↓
primp
   ↓
? page=2
```

Application không cần biết cách primp encode query string.

---

# 15. Tại sao không dùng `yarl.URL` trong Request Model?

Đây là điểm liên quan trực tiếp tới bài `yarl` chúng ta đã học.

Có thể làm:

```python
url: URL
```

nhưng ở layer Application tôi khuyên giữ:

```python
url: str
```

Lý do:

```text
Application
    ↓
FetchRequest
    ↓
string URL
```

không cần phụ thuộc vào thư viện URL cụ thể.

Nếu Application import:

```python
from yarl import URL
```

thì Application bắt đầu phụ thuộc một thư viện Infrastructure-ish.

Ta có thể dùng `yarl` ở nơi xây URL:

```text
URLBuilder
    ↓
str
    ↓
FetchRequest
```

Đây là separation tốt.

---

# 16. Request Model không chứa Parser

Không:

```python
@dataclass
class FetchRequest:
    url: str
    parser: ChapterParser
```

Request chỉ mô tả:

> HTTP resource cần lấy.

Parser là bước tiếp theo.

```text
FetchRequest
     ↓
Fetcher
     ↓
FetchResponse
     ↓
ChapterParser
```

---

# 17. Request Model không chứa Repository

Không:

```python
@dataclass
class FetchRequest:
    url: str
    repository: ChapterRepository
```

Repository thuộc persistence/application boundary.

Request không cần biết dữ liệu sẽ được lưu ở đâu.

---

# 18. Request Model không chứa `primp.AsyncClient`

Không:

```python
@dataclass
class FetchRequest:
    url: str
    client: primp.AsyncClient
```

Nếu làm như vậy:

```text
Application
     ↓
primp
```

Architecture bị đảo ngược.

Đúng:

```text
Application
    ↓
FetchRequest
    ↓
Fetcher Port
    ↓
Infrastructure
    ↓
primp
```

---

# 19. Request Model cho Novel Crawler

Ở mức hiện tại:

```python
@dataclass(frozen=True)
class FetchRequest:

    url: str

    headers: dict[str, str] = field(
        default_factory=dict
    )

    params: dict[str, object] = field(
        default_factory=dict
    )

    timeout: float | None = None
```

Đủ dùng.

Nhưng Novel Crawler có một nhu cầu quan trọng:

> Ta cần biết request này đến từ CrawlTask nào.

Ví dụ:

```text
Novel:
    Đấu Phá Thương Khung

Chapter:
    Chương 1234

URL:
    https://...
```

---

# 20. Có nên thêm `task_id`?

Có thể:

```python
@dataclass(frozen=True)
class FetchRequest:

    url: str

    task_id: str | None = None

    headers: dict[str, str] = field(
        default_factory=dict
    )

    params: dict[str, object] = field(
        default_factory=dict
    )

    timeout: float | None = None
```

Ví dụ:

```python
request = FetchRequest(
    url=chapter_url,
    task_id="crawl-task-001",
)
```

Nhưng cần phân biệt:

```text
request data
```

với:

```text
observability metadata
```

---

# 21. Tôi khuyên tách metadata

Thay vì nhồi:

```text
task_id
novel_id
chapter_id
source
priority
retry_count
```

vào request ngay từ đầu, có thể có:

```python
@dataclass(frozen=True)
class RequestMetadata:

    task_id: str | None = None

    novel_id: str | None = None

    chapter_id: str | None = None
```

và:

```python
@dataclass(frozen=True)
class FetchRequest:

    url: str

    headers: dict[str, str] = field(
        default_factory=dict
    )

    params: dict[str, object] = field(
        default_factory=dict
    )

    timeout: float | None = None

    metadata: RequestMetadata = field(
        default_factory=RequestMetadata
    )
```

Tuy nhiên **chưa cần làm vậy ở Buổi 41**.

Ta sẽ tới phần Observability ở Buổi 49.

---

# 22. Request Model hiện tại nên đơn giản

Tôi chọn:

```python
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass(frozen=True)
class FetchRequest:

    url: str

    headers: dict[str, str] = field(
        default_factory=dict
    )

    params: dict[str, object] = field(
        default_factory=dict
    )

    timeout: float | None = None

    def __post_init__(self):

        if not self.url:
            raise ValueError(
                "URL cannot be empty"
            )

        parsed = urlparse(self.url)

        if parsed.scheme not in {
            "http",
            "https",
        }:
            raise ValueError(
                "URL must use http or https"
            )

        if self.timeout is not None:
            if self.timeout <= 0:
                raise ValueError(
                    "timeout must be > 0"
                )
```

Đây là phiên bản chúng ta dùng làm nền cho Buổi 42–50.

---

# 23. Request Builder

Khi crawler bắt đầu lớn, có thể có helper:

```python
class FetchRequestBuilder:

    def chapter(
        self,
        url: str,
    ) -> FetchRequest:

        return FetchRequest(
            url=url,
            headers={
                "Accept": "text/html",
            },
            timeout=10,
        )
```

Sử dụng:

```python
builder = FetchRequestBuilder()

request = builder.chapter(
    "https://example.com/chapter-1"
)
```

Nhưng hiện tại:

> **Không cần Builder Pattern.**

Đừng abstraction quá sớm.

---

# 24. Request Model và HTTP Method

Một câu hỏi:

> Tại sao `FetchRequest` không có `method`?

Hiện tại Fetcher của chúng ta tập trung vào:

```python
fetcher.get(...)
```

và Novel Crawler chủ yếu đọc dữ liệu.

Do đó:

```python
url
headers
params
timeout
```

đủ.

Nếu sau này cần:

```text
GET
POST
PUT
DELETE
```

thì có thể tiến hóa thành:

```python
@dataclass(frozen=True)
class FetchRequest:

    method: str
    url: str
    ...
```

Nhưng **không thêm trước khi có nhu cầu**.

---

# 25. Request Model và HTTP body

Tương tự, chưa cần:

```python
json_body
form_data
raw_body
```

Novel Crawler của chúng ta chủ yếu:

```text
GET HTML
```

Nếu source cần POST, lúc đó mở rộng.

Architecture tốt không phải architecture có thật nhiều field.

Architecture tốt là:

> Có đúng abstraction cần thiết ở đúng thời điểm.

---

# 26. Request Model hoàn chỉnh + test

Tạo:

```text
application/
└── ports/
    └── fetcher.py
```

Nội dung:

```python
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass(frozen=True)
class FetchRequest:

    url: str

    headers: dict[str, str] = field(
        default_factory=dict
    )

    params: dict[str, object] = field(
        default_factory=dict
    )

    timeout: float | None = None

    def __post_init__(self):

        if not self.url:
            raise ValueError(
                "URL cannot be empty"
            )

        parsed = urlparse(self.url)

        if parsed.scheme not in {
            "http",
            "https",
        }:
            raise ValueError(
                "URL must use http or https"
            )

        if self.timeout is not None:
            if self.timeout <= 0:
                raise ValueError(
                    "timeout must be > 0"
                )
```

Test:

```python
def test_valid_request():

    request = FetchRequest(
        url="https://example.com/chapter-1",
        headers={
            "Accept": "text/html",
        },
        params={
            "page": 1,
        },
        timeout=10,
    )

    assert request.url == (
        "https://example.com/chapter-1"
    )

    assert request.headers[
        "Accept"
    ] == "text/html"

    assert request.params["page"] == 1

    assert request.timeout == 10
```

---

# 27. Test invalid URL

```python
def test_empty_url():

    try:

        FetchRequest(url="")

    except ValueError as exc:

        assert str(exc) == (
            "URL cannot be empty"
        )
```

Hoặc với pytest:

```python
import pytest


def test_empty_url():

    with pytest.raises(
        ValueError,
        match="URL cannot be empty",
    ):
        FetchRequest(url="")
```

---

# 28. Test invalid scheme

```python
def test_invalid_scheme():

    with pytest.raises(
        ValueError,
        match="URL must use http or https",
    ):
        FetchRequest(
            url="ftp://example.com"
        )
```

---

# 29. Test invalid timeout

```python
def test_invalid_timeout():

    with pytest.raises(
        ValueError,
        match="timeout must be > 0",
    ):
        FetchRequest(
            url="https://example.com",
            timeout=0,
        )
```

---

# 30. Test default values

```python
def test_defaults():

    request = FetchRequest(
        url="https://example.com"
    )

    assert request.headers == {}
    assert request.params == {}
    assert request.timeout is None
```

---

# 31. Test immutability của field chính

```python
def test_frozen():

    request = FetchRequest(
        url="https://example.com"
    )

    with pytest.raises(
        AttributeError
    ):
        request.url = (
            "https://other.com"
        )
```

---

# 32. Request Model trong crawler thật

Ví dụ Chapter URL:

```python
chapter_url = (
    "https://example.com/"
    "truyen/chuong-123"
)

request = FetchRequest(
    url=chapter_url,
    headers={
        "Accept": "text/html",
    },
    timeout=15,
)
```

Fetcher nhận:

```python
response = await fetcher.get(
    request
)
```

Fetcher **không cần biết**:

```text
đây là chapter
```

Đó là trách nhiệm của Application.

---

# 33. Use Case quyết định request

Ví dụ:

```python
class CrawlChapter:

    def __init__(
        self,
        fetcher,
    ):
        self.fetcher = fetcher

    async def execute(
        self,
        chapter_url: str,
    ):

        request = FetchRequest(
            url=chapter_url,
            headers={
                "Accept": "text/html",
            },
            timeout=15,
        )

        return await self.fetcher.get(
            request
        )
```

Flow:

```text
CrawlChapter
      ↓
tạo FetchRequest
      ↓
Fetcher
```

---

# 34. Đây là Dependency Inversion

Application:

```python
class CrawlChapter:

    def __init__(
        self,
        fetcher: Fetcher,
    ):
        self.fetcher = fetcher
```

không:

```python
self.fetcher = PrimpFetcher(...)
```

Application chỉ biết:

```text
Fetcher
```

Infrastructure mới biết:

```text
PrimpFetcher
```

---

# 35. Request Model không phải Domain Entity

Đây cũng là điểm cần nhớ.

`Chapter`:

```text
Domain Entity
```

`FetchRequest`:

```text
Application/Infrastructure boundary object
```

Không nên đưa:

```python
class Chapter:
    fetch_request: FetchRequest
```

vào Domain.

Domain không cần biết chapter được tải bằng:

```text
primp
httpx
requests
browser
```

---

# 36. Tổng kết Buổi 41

Ta đã thiết kế:

```text
FetchRequest
├── url
├── headers
├── params
└── timeout
```

với validation:

```text
URL không rỗng
URL phải http/https
timeout > 0
```

Architecture:

```text
Application
     │
     ↓
FetchRequest
     │
     ↓
Fetcher
     │
     ↓
Infrastructure
     │
     ↓
primp.AsyncClient
```

Và đặc biệt:

```text
FetchRequest
    ✗ không biết primp
    ✗ không biết Proxy
    ✗ không biết Retry
    ✗ không biết Parser
    ✗ không biết SQLite
```

Đó chính là một Request Model sạch.

---

## Bài tiếp theo — Buổi 42: Response Model

Ta sẽ làm chiều ngược lại:

```text
primp.Response
      ↓
Response Adapter
      ↓
FetchResponse
```

và thiết kế Response Model cho crawler gồm:

```text
status_code
url
headers
content
text
is_success
is_redirect
is_client_error
is_server_error
```

Sau Buổi 42, ta sẽ có đầy đủ hai đầu của contract:

```text
FetchRequest
      ↓
    Fetcher
      ↓
FetchResponse
```

để sang **Buổi 43 — Fetcher Interface** xây Port hoàn chỉnh.
