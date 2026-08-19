Quản lý **Authentication**, **Headers** và **Cookies** trong `httpx` rất trực quan. Bạn có thể thiết lập chúng ở **từng Request riêng lẻ** hoặc thiết lập một lần ở **cấp độ Client** để dùng chung cho tất cả các request.

---

## 1. Authentication (Xác thực)

### A. Basic Auth (Tài khoản & Mật khẩu)

`httpx` hỗ trợ sẵn `BasicAuth`. Bạn có thể truyền dạng `tuple` hoặc dùng class `httpx.BasicAuth`:

```python
import httpx

# Cách 1: Truyền tuple đơn giản (Username, Password)
response = httpx.get("https://httpbin.org/basic-auth/user/pass", auth=("user", "pass"))

# Cách 2: Dùng class httpx.BasicAuth
from httpx import BasicAuth
response = httpx.get("https://httpbin.org/basic-auth/user/pass", auth=BasicAuth("user", "pass"))

```

### B. Bearer Token (JWT / OAuth2)

Phương pháp phổ biến nhất hiện nay khi làm việc với REST API. Cách chuẩn mực là gắn Token vào Header `Authorization`:

```python
import httpx

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

response = httpx.get("https://api.example.com/user/profile", headers=headers)

```

---

## 2. Quản lý Custom Headers

Headers thường dùng để khai báo `Content-Type`, `User-Agent`, `Accept`, hoặc các custom API Key.

```python
import httpx

headers = {
    "User-Agent": "MyApp/1.0.0 (Python/3.11)",
    "Accept": "application/json",
    "X-Custom-API-Key": "my-secret-key-123"
}

response = httpx.get("https://httpbin.org/headers", headers=headers)

```

> 💡 **Mẹo:** `httpx.Headers` không phân biệt chữ hoa/thường (case-insensitive), nên `response.headers['content-type']` hay `response.headers['Content-Type']` đều hoạt động chuẩn xác.

---

## 3. Quản lý Cookies

### Gửi Cookies đi

Bạn có thể truyền Cookie dưới dạng Dictionary:

```python
import httpx

cookies = {
    "session_id": "abc123xyz",
    "theme": "dark"
}

response = httpx.get("https://httpbin.org/cookies", cookies=cookies)

```

### Đọc Cookies từ Response

`httpx` tự động thu thập Cookies do Server trả về qua header `Set-Cookie`:

```python
response = httpx.get("https://httpbin.org/cookies/set?user=john")

# Lấy Cookie trả về
user_cookie = response.cookies.get("user")
print("User Cookie:", user_cookie)

```

---

## 4. Quản lý ở cấp độ Client (Kỹ thuật khuyên dùng 🌟)

Nếu bạn gọi nhiều API trong cùng một phiên, việc khai báo lặp đi lặp lại `headers`, `cookies` hay `auth` ở từng request rất vi phạm nguyên tắc DRY (Don't Repeat Yourself).

Hãy cấu hình chúng ngay khi khởi tạo **`httpx.Client`** (hoặc `httpx.AsyncClient`):

```python
import httpx

BASE_URL = "https://api.example.com/v1"
TOKEN = "secret-bearer-token"

# Khởi tạo Client với các cấu hình mặc định
with httpx.Client(
    base_url=BASE_URL,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "User-Agent": "MobileApp-Backend/2.0"
    },
    cookies={"device_id": "device_9999"},
    auth=("admin", "secret_pass") # Nếu dùng Basic Auth
) as client:
    
    # Mọi request gọi từ client này sẽ TỰ ĐỘNG mang theo Auth, Headers và Cookies trên
    r1 = client.get("/users")       # Gửi tới: https://api.example.com/v1/users
    r2 = client.get("/products")    # Gửi tới: https://api.example.com/v1/products

    # Nếu muốn override (ghi đè) Header riêng cho 1 request cụ thể:
    r3 = client.get("/public-data", headers={"Authorization": ""})

```

---

## 5. Nâng cao: Tự động Refresh Token khi hết hạn (Custom Auth Class)

Chức năng rất mạnh của `httpx` là cho phép bạn tự viết một Class kế thừa `httpx.Auth` để tự động đính kèm Token hoặc tự động làm mới Token (Refresh Token) khi bị lỗi 401 Unauthorized.

```python
import httpx

class BearerAuth(httpx.Auth):
    def __init__(self, token: str):
        self.token = token

    def auth_flow(self, request: httpx.Request):
        # Đính kèm token vào request trước khi gửi
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request # Gửi request đi

        # Ví dụ nâng cao: Nếu nhận về lỗi 401 Token expired, có thể gọi API refresh token tại đây
        # response = yield request_refresh
        # request.headers["Authorization"] = f"Bearer {new_token}"
        # yield request # Gửi lại request ban đầu với token mới

# Sử dụng:
client = httpx.Client(auth=BearerAuth("my-jwt-token"))
res = client.get("https://httpbin.org/get")

```