# Buổi 9 — Cookies trong `primp`

Theo roadmap:

```text
06. POST
07. JSON
08. Form Data
09. Cookies   ← hôm nay
10. Redirect
```

Cookies cực kỳ quan trọng khi xây crawler vì chúng liên quan đến:

* Session
* Login
* Theo dõi trạng thái người dùng
* CSRF
* Cloudflare / anti-bot state
* Duy trì trạng thái giữa nhiều request

Mục tiêu hôm nay là hiểu **cookie đi từ server → client → request tiếp theo như thế nào**.

---

# 1. Cookie là gì?

HTTP vốn có tính chất **stateless**.

Ví dụ:

```text
Request 1
Client ────────────────> Server

Request 2
Client ────────────────> Server
```

Server không mặc định biết:

> "Request 2 có phải cùng người với Request 1 không?"

Cookie giúp server lưu một phần trạng thái ở phía client.

Luồng cơ bản:

```text
                    Response
Server ─────────────────────────> Client
          Set-Cookie: session=abc

Client
  │
  │ lưu cookie
  ▼
Cookie Jar
  │
  │ Request tiếp theo
  ▼
Server
```

---

# 2. Server gửi Cookie như thế nào?

HTTP response có thể chứa:

```text
Set-Cookie: session_id=abc123
```

Ví dụ sử dụng `httpbin`:

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/cookies/set/session_id/abc123"
    )

    print("Status:", response.status_code)
    print("URL:", response.url)


if __name__ == "__main__":
    main()
```

Server sẽ thiết lập cookie:

```text
session_id=abc123
```

---

# 3. Xem Cookie server trả về

Về HTTP, cookie được biểu diễn bởi header:

```text
Set-Cookie
```

Ta có thể kiểm tra response headers:

```python
print(response.headers)
```

Tìm:

```text
set-cookie
```

Tuy nhiên khi làm việc thực tế, chúng ta thường không muốn tự parse `Set-Cookie` bằng tay.

HTTP client nên quản lý cookie jar.

---

# 4. Cookie Jar

Khái niệm quan trọng:

```text
Cookie Jar
```

là nơi client lưu cookies.

Hình dung:

```text
Primp Client
     │
     ├── HTTP Request
     │
     ├── HTTP Response
     │
     └── Cookie Jar
             │
             ├── session_id=abc
             ├── user_id=123
             └── csrf_token=xyz
```

Sau đó các request phù hợp có thể sử dụng những cookie này.

---

# 5. Kiểm tra Cookie Flow

Dùng endpoint:

```text
https://httpbin.org/cookies/set/session_id/abc123
```

sau đó:

```text
https://httpbin.org/cookies
```

Code:

```python
import primp


def main():
    client = primp.Client()

    # Request 1:
    # Server set cookie
    response1 = client.get(
        "https://httpbin.org/cookies/set/session_id/abc123"
    )

    print("Request 1:")
    print(response1.status_code)
    print(response1.url)

    print()

    # Request 2:
    # Kiểm tra cookie
    response2 = client.get(
        "https://httpbin.org/cookies"
    )

    print("Request 2:")
    print(response2.status_code)
    print(response2.text)


if __name__ == "__main__":
    main()
```

Nếu cookie jar hoạt động như mong đợi, request thứ hai sẽ cho thấy:

```json
{
    "cookies": {
        "session_id": "abc123"
    }
}
```

Điểm quan trọng:

> **Hai request dùng cùng một `Client`.**

---

# 6. Tại sao phải dùng cùng `Client`?

Đây là lỗi rất phổ biến:

```python
client1 = primp.Client()

client1.get(
    "https://httpbin.org/cookies/set/session_id/abc123"
)

client2 = primp.Client()

response = client2.get(
    "https://httpbin.org/cookies"
)
```

Bạn đã tạo:

```text
Client 1
   └── Cookie Jar A

Client 2
   └── Cookie Jar B
```

Cookie từ Client 1 không tự nhiên xuất hiện trong Client 2.

Trong khi:

```python
client = primp.Client()

client.get(...)
client.get(...)
client.get(...)
```

thì:

```text
Client
 │
 └── Cookie Jar
       │
       ├── Request 1
       ├── Request 2
       └── Request 3
```

Đây chính là lý do `Client` có ý nghĩa rất lớn trong HTTP crawler.

---

# 7. Tự gửi Cookie

Ngoài cookie server cấp, bạn có thể chủ động gửi cookie.

Ví dụ:

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/cookies",
        cookies={
            "session_id": "abc123",
            "user_id": "100",
        },
    )

    print(response.text)


if __name__ == "__main__":
    main()
```

Server sẽ nhận được:

```json
{
    "cookies": {
        "session_id": "abc123",
        "user_id": "100"
    }
}
```

Đây là trường hợp:

```text
Python
   │
   │ cookies={}
   ▼
primp
   │
   │ Cookie: session_id=abc123
   ▼
Server
```

---

# 8. Cookie không phải Header thông thường

Bạn có thể nghĩ:

```python
headers={
    "Cookie": "session_id=abc123"
}
```

và về mặt HTTP nó có thể biểu diễn cookie.

Nhưng nếu API của client hỗ trợ:

```python
cookies={
    "session_id": "abc123"
}
```

thì nên sử dụng abstraction cookie.

Không nên tự xây:

```python
cookie_string = "; ".join(...)
```

trừ khi bạn thực sự cần kiểm soát HTTP header ở mức thấp.

---

# 9. Cookie trong Login Flow

Đây là tình huống thực tế hơn.

Giả sử website có:

```text
POST /login
```

và server trả:

```text
Set-Cookie: session=abc123
```

Luồng:

```text
                 POST /login
Client ─────────────────────────> Server
         username/password

Client <───────────────────────── Server
         Set-Cookie: session=abc123

              ↓
          Cookie Jar
              │
              ▼

Client ─────────────────────────> Server
        GET /profile
        Cookie: session=abc123
```

Code:

```python
import primp


def main():
    client = primp.Client()

    # Login
    login_response = client.post(
        "https://example.com/login",
        data={
            "username": "alice",
            "password": "123456",
        },
    )

    print(
        "Login:",
        login_response.status_code,
    )

    # Request sau login
    profile_response = client.get(
        "https://example.com/profile"
    )

    print(
        "Profile:",
        profile_response.status_code,
    )


if __name__ == "__main__":
    main()
```

Điểm quan trọng là:

```python
client = primp.Client()
```

được dùng xuyên suốt flow.

---

# 10. Cookie + Form Data

Buổi trước chúng ta học:

```python
client.post(
    url,
    data={
        "username": "alice",
        "password": "123",
    },
)
```

Bây giờ kết hợp:

```text
GET login page
       │
       ▼
Cookie session / CSRF
       │
       ▼
POST form
       │
       ▼
Cookie session
       │
       ▼
GET protected page
```

Đây là pattern rất thường gặp khi crawl website.

---

# 11. CSRF Cookie

Ví dụ server trả:

```text
Set-Cookie: csrf_token=abc123
```

HTML:

```html
<input
    type="hidden"
    name="csrf_token"
    value="abc123"
>
```

Khi POST:

```python
response = client.post(
    url,
    data={
        "username": "alice",
        "csrf_token": "abc123",
    },
)
```

Request có thể đồng thời chứa:

```text
Cookie:
csrf_token=abc123
```

và body:

```text
csrf_token=abc123
```

Đây là lý do khi crawler mô phỏng website, chúng ta thường phải:

1. GET trang trước.
2. Nhận cookie.
3. Parse HTML.
4. Lấy hidden token.
5. POST form.
6. Giữ nguyên Client.

---

# 12. Cookie có thuộc tính

Một cookie thực tế không chỉ có:

```text
name=value
```

Nó có thể có:

```text
session=abc123;
Path=/;
Domain=example.com;
Secure;
HttpOnly;
SameSite=Lax
```

Các thuộc tính có ý nghĩa:

| Attribute  | Ý nghĩa                                          |
| ---------- | ------------------------------------------------ |
| `Domain`   | Cookie áp dụng domain nào                        |
| `Path`     | Cookie áp dụng path nào                          |
| `Expires`  | Thời điểm hết hạn                                |
| `Max-Age`  | Thời gian tồn tại                                |
| `Secure`   | Chỉ gửi qua HTTPS                                |
| `HttpOnly` | JavaScript phía browser không đọc trực tiếp được |
| `SameSite` | Quy tắc gửi cookie trong cross-site context      |

Trong crawler, các thuộc tính này quan trọng vì cookie **không phải lúc nào cũng được gửi cho mọi URL**.

---

# 13. Cookie theo Domain

Ví dụ:

```text
session=abc123
Domain=example.com
```

Cookie này không có nghĩa là:

```text
example-other.com
```

cũng nhận được.

Hình dung:

```text
example.com
    │
    ├── /
    ├── /novel
    └── /chapter

Cookie có thể được gửi
```

nhưng:

```text
other.com

Không gửi cookie đó
```

HTTP client/cookie jar sẽ xử lý phạm vi áp dụng dựa trên cookie attributes.

---

# 14. Cookie Session trong Novel Crawler

Đây là architecture chúng ta muốn hướng tới:

```text
                 ┌─────────────────┐
                 │ PrimpFetcher    │
                 └────────┬────────┘
                          │
                    Primp Client
                          │
                   ┌──────▼──────┐
                   │ Cookie Jar  │
                   └──────┬──────┘
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          Request 1    Request 2    Request 3
             │            │            │
             └────────────┴────────────┘
```

Một Fetcher instance có thể duy trì state HTTP cần thiết cho một crawl session.

Ví dụ:

```python
import primp


class PrimpFetcher:

    def __init__(self):
        self.client = primp.Client()

    def get(self, url: str):
        return self.client.get(url)

    def post_form(
        self,
        url: str,
        data: dict[str, str],
    ):
        return self.client.post(
            url,
            data=data,
        )
```

---

# 15. Một Fetcher có nên dùng mãi mãi không?

Không nhất thiết.

Đây là vấn đề kiến trúc.

Ví dụ:

```text
Crawler Job A
    │
    └── Fetcher A
          └── Cookie Jar A


Crawler Job B
    │
    └── Fetcher B
          └── Cookie Jar B
```

Không nên vô tình để:

```text
Crawler Job A
      │
      └──── Cookie ────┐
                       ▼
                  Fetcher Global
                       ▲
                       │
      ┌──── Cookie ────┘
      │
Crawler Job B
```

Nếu cookie mang tính session/user-specific, việc chia sẻ Client toàn cục có thể gây lỗi trạng thái và vấn đề bảo mật.

Vì vậy sau này khi xây crawler production, ta sẽ phải xác định **lifetime của HTTP session**.

---

# 16. Cookie và Proxy

Cookie cũng liên quan đến proxy.

Ví dụ:

```text
Session
   │
   ├── Cookie Jar
   │
   └── Proxy
```

Nếu bạn thay đổi proxy giữa một session:

```text
Request 1
Proxy A
Cookie X

Request 2
Proxy B
Cookie X
```

thì về mặt kỹ thuật có thể xảy ra, nhưng với một số hệ thống việc gắn session state với network identity có thể khiến flow trở nên khó đoán.

Với crawler, thường nên thiết kế rõ:

```text
Browser/Session Profile
    │
    ├── Client
    ├── Cookies
    ├── Headers
    ├── Proxy
    └── Browser identity
```

Sau này phần Browser Impersonation chúng ta sẽ quay lại vấn đề này.

---

# 17. Bài test quan trọng nhất

Hãy chạy nguyên chương trình này:

```python
import primp


def main():
    client = primp.Client()

    print("=== STEP 1: SET COOKIE ===")

    response = client.get(
        "https://httpbin.org/cookies/set/session_id/abc123"
    )

    print("Status:", response.status_code)
    print("URL:", response.url)

    print()

    print("=== STEP 2: SEND COOKIE ===")

    response = client.get(
        "https://httpbin.org/cookies"
    )

    print("Status:", response.status_code)
    print("Body:")
    print(response.text)


if __name__ == "__main__":
    main()
```

Mục tiêu của bài này không phải chỉ nhìn output.

Bạn cần hiểu:

```text
STEP 1

Server
   │
   │ Set-Cookie
   ▼
Primp Client
   │
   ▼
Cookie Jar


STEP 2

Primp Client
   │
   │ Cookie
   ▼
Server
```

---

# 18. Bài test Cookie thủ công

Thử:

```python
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/cookies",
        cookies={
            "novel_source": "truyenfull",
            "session": "abc123",
        },
    )

    print(response.json())


if __name__ == "__main__":
    main()
```

Bạn sẽ thấy:

```text
cookies:
    novel_source: truyenfull
    session: abc123
```

---

# 19. Bài tập

### Bài 1

Tạo Client:

```python
client = primp.Client()
```

Gửi cookie:

```text
username=alice
theme=dark
```

đến:

```text
https://httpbin.org/cookies
```

và kiểm tra JSON.

---

### Bài 2

Thử cookie persistence:

```text
Request 1:
Set session_id

Request 2:
GET /cookies
```

Nhưng **chỉ sử dụng một Client**.

Sau đó thử lại bằng hai Client khác nhau và quan sát sự khác biệt.

---

### Bài 3 — Login simulation

Thiết kế:

```text
login()
    ↓
POST form
    ↓
cookie
    ↓
get_profile()
```

Ví dụ API:

```python
class PrimpFetcher:

    def login(
        self,
        url: str,
        username: str,
        password: str,
    ):
        ...

    def get_profile(
        self,
        url: str,
    ):
        ...
```

Chưa cần xây authentication abstraction phức tạp.

---

# 20. Tổng kết Buổi 9

Ba khái niệm quan trọng nhất:

### ① Server → Cookie

```text
Set-Cookie
      ↓
Cookie Jar
```

### ② Client → Server

```text
Cookie
   ↓
Request
```

### ③ Cùng Client → giữ session state

```python
client = primp.Client()

client.get(...)
client.post(...)
client.get(...)
```

Có thể hình dung:

```text
                 Primp Client
                      │
               ┌──────▼──────┐
               │ Cookie Jar  │
               └──────┬──────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       GET /       POST /       GET /
       login       login        profile
          │           │           │
          └───────────┴───────────┘
                  Session
```

**Điểm đặc biệt đối với Novel Crawler:** Cookie không nên được xem đơn thuần là một dictionary. Nó là **HTTP session state**, và lifetime của nó sẽ ảnh hưởng trực tiếp đến thiết kế `Fetcher`, proxy, retry và browser profile sau này.

**Buổi 10 — Redirect** sẽ nối tiếp rất tự nhiên: `301/302/303/307/308`, redirect tự động, `response.url`, redirect history và cách xử lý redirect trong crawler.
