# Buổi 13 — Authentication với `primp`

Ở Buổi 12 chúng ta đã phân biệt:

```text
Network failure
    ↓
Exception

HTTP 4xx / 5xx
    ↓
Response
```

Buổi 13 chuyển sang **Authentication** — tức là cách client chứng minh danh tính/quyền truy cập với server.

Với HTTP client, những kiểu phổ biến gồm:

```text
Authentication
├── Basic Authentication
├── Bearer Token
├── API Key
├── Cookie / Session
└── OAuth 2.0
```

Trong phạm vi `primp`, ta tập trung vào **cách truyền thông tin authentication qua HTTP request**. Một tài liệu hiện có về hệ sinh thái `primp` cũng liệt kê Basic Auth và Bearer token là các kiểu authentication được hỗ trợ. ([GitHub][1])

---

# 1. Authentication là gì?

Ví dụ server có endpoint:

```text
GET /profile
```

Nếu gọi:

```python
response = client.get(
    "https://example.com/profile"
)
```

server có thể trả:

```text
401 Unauthorized
```

Vì server yêu cầu:

```text
"Bạn là ai?"
```

Client phải gửi credential.

Ví dụ:

```text
Authorization: Bearer eyJhbGci...
```

hoặc:

```text
Authorization: Basic xxxxx
```

---

# 2. Authentication ≠ Authorization

Hai khái niệm này rất dễ nhầm.

### Authentication

> Bạn là ai?

```text
Authentication
      ↓
Identity
```

### Authorization

> Bạn được phép làm gì?

```text
Authorization
      ↓
Permission
```

Ví dụ:

```text
User đăng nhập
      ↓
Authentication
      ↓
Server biết user = alice
      ↓
Authorization
      ↓
alice có quyền đọc chapter
```

---

# 3. Basic Authentication

HTTP Basic Auth có dạng:

```text
username + password
```

và được truyền qua:

```http
Authorization: Basic <credentials>
```

Trong đó credentials là dạng Base64 của:

```text
username:password
```

Ví dụ:

```text
alice:secret
```

→ encode Base64:

```text
YWxpY2U6c2VjcmV0
```

→ HTTP:

```http
Authorization: Basic YWxpY2U6c2VjcmV0
```

**Base64 không phải encryption.**

Vì vậy Basic Auth nên được sử dụng qua HTTPS.

---

# 4. Tự tạo Basic Auth bằng Python

Để hiểu bản chất trước khi dùng abstraction:

```python
import base64


username = "alice"
password = "secret"

credentials = f"{username}:{password}"

encoded = base64.b64encode(
    credentials.encode()
).decode()

print(encoded)
```

Kết quả:

```text
YWxpY2U6c2VjcmV0
```

Sau đó:

```python
headers = {
    "Authorization": f"Basic {encoded}"
}
```

---

# 5. Gửi Basic Auth bằng `primp`

Ta có thể xây header:

```python
import base64
import primp


def basic_auth(username: str, password: str) -> str:
    credentials = f"{username}:{password}"

    encoded = base64.b64encode(
        credentials.encode()
    ).decode()

    return f"Basic {encoded}"


def main():
    client = primp.Client()

    headers = {
        "Authorization": basic_auth(
            "alice",
            "secret",
        )
    }

    response = client.get(
        "https://httpbin.org/basic-auth/alice/secret",
        headers=headers,
    )

    print("Status:", response.status_code)
    print(response.text)


if __name__ == "__main__":
    main()
```

Điểm quan trọng ở đây là:

```python
headers={
    "Authorization": "Basic ..."
}
```

Authentication cuối cùng vẫn trở thành **HTTP header**.

---

# 6. Bearer Token

Đây là kiểu rất phổ biến trong API.

Request:

```http
Authorization: Bearer ACCESS_TOKEN
```

Ví dụ:

```python
import primp


def main():
    client = primp.Client()

    token = "my-secret-token"

    response = client.get(
        "https://httpbin.org/headers",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    print(response.status_code)
    print(response.text)


if __name__ == "__main__":
    main()
```

Cấu trúc:

```text
Bearer
   +
token
```

Ví dụ thực tế:

```text
Authorization: Bearer eyJhbGciOiJIUzI1Ni...
```

---

# 7. Bearer Token thực chất là gì?

Ở tầng HTTP:

```text
Bearer Token
      ↓
Authorization header
      ↓
HTTP Request
```

Không nhất thiết token phải là JWT.

Có thể là:

```text
Bearer abc123
```

hoặc:

```text
Bearer eyJhbGciOi...
```

JWT chỉ là **một dạng token**, không đồng nghĩa với Bearer.

---

# 8. API Key

Một API có thể yêu cầu:

```http
X-API-Key: abc123
```

Ta gửi:

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/headers",
        headers={
            "X-API-Key": "my-api-key",
        },
    )

    print(response.text)


if __name__ == "__main__":
    main()
```

Một số API khác có thể yêu cầu:

```http
Authorization: Bearer ...
```

hoặc:

```http
Authorization: Api-Key ...
```

Tên và format **do API server quy định**.

---

# 9. Không phải authentication nào cũng dùng `Authorization`

Ví dụ:

### Bearer

```http
Authorization: Bearer TOKEN
```

### Basic

```http
Authorization: Basic BASE64
```

### API Key

```http
X-API-Key: KEY
```

### Cookie

```http
Cookie: session_id=abc123
```

Vì vậy trong crawler ta không nên thiết kế:

```python
authenticate(token)
```

rồi giả định mọi website đều dùng Bearer.

---

# 10. Authentication bằng Cookie

Phần này liên quan trực tiếp đến **Buổi 9 — Cookies**.

Ví dụ server login:

```text
POST /login
        ↓
username/password
        ↓
Set-Cookie: session_id=abc123
```

Sau đó:

```text
GET /profile
Cookie: session_id=abc123
```

Với `primp`, việc giữ cùng một `Client` giúp duy trì trạng thái client/session.

Ví dụ:

```python
import primp


def main():
    client = primp.Client()

    login_response = client.post(
        "https://example.com/login",
        data={
            "username": "alice",
            "password": "secret",
        },
    )

    print(login_response.status_code)

    profile_response = client.get(
        "https://example.com/profile"
    )

    print(profile_response.status_code)


if __name__ == "__main__":
    main()
```

Đây là:

```text
Login
  ↓
Cookie
  ↓
Client state
  ↓
Authenticated request
```

---

# 11. Authentication và Cookies khác nhau

Đừng gộp chúng thành một khái niệm.

```text
Authentication
    │
    ├── Basic
    ├── Bearer
    ├── API Key
    └── Cookie/session
```

Cookie có thể **mang session credential**, nhưng Cookie bản thân nó là cơ chế HTTP state.

Ví dụ:

```text
Set-Cookie: session=abc
```

khác về cơ chế so với:

```text
Authorization: Bearer abc
```

---

# 12. Không hard-code credential

❌ Không nên:

```python
token = "sk-abc123-secret"
```

hoặc:

```python
password = "MyPassword123"
```

đặc biệt khi code được commit lên Git.

Nên dùng environment variable:

```python
import os
import primp


token = os.environ["API_TOKEN"]

client = primp.Client()

response = client.get(
    "https://httpbin.org/headers",
    headers={
        "Authorization": f"Bearer {token}",
    },
)

print(response.text)
```

Terminal:

```bash
export API_TOKEN="abc123"
```

Windows PowerShell:

```powershell
$env:API_TOKEN="abc123"
```

---

# 13. Tạo `AuthConfig`

Vì chúng ta đang tiến tới Fetcher architecture, có thể bắt đầu tách credential khỏi request.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BearerToken:
    token: str

    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}"
        }
```

Sử dụng:

```python
auth = BearerToken(
    token="abc123"
)

headers = auth.headers()

print(headers)
```

Kết quả:

```python
{
    "Authorization": "Bearer abc123"
}
```

---

# 14. Basic Auth cũng có thể abstraction

```python
from dataclasses import dataclass
import base64


@dataclass(frozen=True)
class BasicAuth:
    username: str
    password: str

    def headers(self) -> dict[str, str]:
        raw = (
            f"{self.username}:{self.password}"
            .encode()
        )

        encoded = base64.b64encode(raw).decode()

        return {
            "Authorization": f"Basic {encoded}"
        }
```

Sử dụng:

```python
auth = BasicAuth(
    username="alice",
    password="secret",
)

print(auth.headers())
```

---

# 15. Authentication không nên nằm cứng trong Parser

Đây là phần quan trọng với **Novel Crawler**.

Không nên:

```text
Parser
  │
  ├── username
  ├── password
  ├── token
  └── HTTP request
```

Parser chỉ làm:

```text
HTML
 ↓
Novel
Chapter
```

Authentication thuộc tầng HTTP/application:

```text
Application
    │
    ▼
Fetcher
    │
    ▼
Authentication
    │
    ▼
Primp
```

---

# 16. Thiết kế Fetcher với Authentication

Phiên bản đơn giản:

```python
import primp


class PrimpFetcher:

    def __init__(
        self,
        timeout: float = 10,
        headers: dict[str, str] | None = None,
    ):
        self.client = primp.Client(
            headers=headers or {}
        )

        self.default_timeout = timeout

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ):
        if timeout is None:
            timeout = self.default_timeout

        return self.client.get(
            url,
            headers=headers,
            timeout=timeout,
        )
```

Sau đó:

```python
fetcher = PrimpFetcher()

response = fetcher.get(
    "https://httpbin.org/headers",
    headers={
        "Authorization": "Bearer abc123",
    },
)
```

---

# 17. Nhưng có một vấn đề

Nếu mọi request đều phải truyền:

```python
headers={
    "Authorization": "Bearer abc123"
}
```

thì rất dễ lặp code:

```text
GET /a → Bearer
GET /b → Bearer
GET /c → Bearer
GET /d → Bearer
```

Trong khi token thường thuộc về **Client/session**.

Đây chính là lý do roadmap tiếp tục có:

```text
16. Session / Connection Reuse
17. Default Headers
18. Default Params
19. Request Options
20. Client Lifecycle
```

Chúng ta **chưa cần giải quyết toàn bộ ngay ở Buổi 13**.

---

# 18. Authentication trong Novel Crawler

Với crawler truyện, phần lớn website public có thể không cần authentication.

Nhưng có thể có:

```text
Public website
    ↓
Không auth

Website yêu cầu login
    ↓
Cookie session

API
    ↓
API Key / Bearer

Private API
    ↓
OAuth / Token
```

Do đó Fetcher nên hỗ trợ authentication **mà không bắt Parser biết authentication tồn tại**.

---

# 19. Authentication Flow

Ví dụ Bearer:

```text
┌──────────────────┐
│ Application      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Fetcher          │
└────────┬─────────┘
         │
         │ Authorization: Bearer TOKEN
         ▼
┌──────────────────┐
│ Primp Client     │
└────────┬─────────┘
         │
         ▼
      Server
```

Parser nằm bên ngoài flow này:

```text
Response
   │
   ▼
Parser
   │
   ▼
Novel / Chapter
```

---

# 20. Authentication không đồng nghĩa với Login

Đây là một điểm cần nhớ.

### Login

Một flow:

```text
POST /login
    ↓
username/password
    ↓
session/token
```

### Authentication request

Có thể đơn giản là:

```text
GET /profile
Authorization: Bearer TOKEN
```

Token đã có từ trước.

Vì vậy:

```text
Login
```

là **một quy trình lấy credential/session**.

Còn:

```text
Authentication
```

là **việc gửi credential để server xác thực request**.

---

# 21. Bảng tổng hợp

| Cơ chế    | Ví dụ                              |
| --------- | ---------------------------------- |
| Basic     | `Authorization: Basic ...`         |
| Bearer    | `Authorization: Bearer ...`        |
| API Key   | `X-API-Key: ...`                   |
| Cookie    | `Cookie: session=...`              |
| OAuth 2.0 | lấy access token rồi sử dụng token |
| JWT       | thường được gửi như Bearer token   |

OAuth 2.0 phức tạp hơn vì nó là **authorization framework/flow**, không đơn giản chỉ là thêm một header; access token sau khi có thường được dùng để gọi API. ([GitHub][2])

---

# 22. Bài tập Buổi 13

### Bài 1 — Basic Auth

Gọi:

```text
https://httpbin.org/basic-auth/alice/secret
```

với:

```text
username = alice
password = secret
```

và in:

```text
status
response.json()
```

---

### Bài 2 — Bearer

Gửi:

```python
Authorization: Bearer abc123
```

đến:

```text
https://httpbin.org/headers
```

và kiểm tra response.

---

### Bài 3 — API Key

Gửi:

```python
X-API-Key: abc123
```

và kiểm tra:

```python
response.json()
```

---

### Bài 4 — Thiết kế

Tạo:

```python
class BearerAuth:
    ...
```

có:

```python
headers()
```

trả về:

```python
{
    "Authorization": "Bearer ..."
}
```

---

# 23. Kiến trúc sau Buổi 13

Chúng ta đang tiến dần đến:

```text
                    Application
                         │
                         ▼
                  Fetcher Interface
                         │
                         ▼
                    PrimpFetcher
                         │
              ┌──────────┼──────────┐
              │          │          │
           Timeout    Headers     Auth
              │          │          │
              └──────────┼──────────┘
                         ▼
                    primp.Client
                         │
                         ▼
                       HTTP
```

Và quan trọng nhất:

```text
Parser
  │
  └── KHÔNG biết authentication

Fetcher
  │
  └── xử lý HTTP concerns

Authentication
  │
  └── credential / Authorization / session
```

### Tiếp theo — Buổi 14: Proxy

Ta sẽ đi từ:

```text
primp.Client()
      ↓
proxy
      ↓
HTTP proxy
HTTPS proxy
      ↓
proxy authentication
      ↓
proxy + timeout
      ↓
proxy + crawler
      ↓
ProxyPool
```

Đây sẽ là buổi rất sát với **Novel Crawler Fetcher** mà bạn đang xây.

[1]: https://github.com/tjsnell/primp-mcp?utm_source=chatgpt.com "GitHub - tjsnell/primp-mcp: MCP server for primp HTTP client library with browser impersonation · GitHub"
[2]: https://github.com/googleapis/google-api-python-client/blob/main/docs/auth.md?utm_source=chatgpt.com "google-api-python-client/docs/auth.md at main · googleapis/google-api-python-client · GitHub"
