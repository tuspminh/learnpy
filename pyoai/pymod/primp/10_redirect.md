# Buổi 10 — Redirect trong `primp`

Đây là **buổi cuối của Phần I — Cơ bản**.

```text
PHẦN I — CƠ BẢN

01. Cài đặt + Client       ✓
02. GET request            ✓
03. Response               ✓
04. Headers
05. Query Parameters       ✓
06. POST                   ✓
07. JSON                   ✓
08. Form Data              ✓
09. Cookies                ✓
10. Redirect                ← hôm nay
```

> Lưu ý: theo roadmap ban đầu của bạn, Headers và Query Parameters có vị trí 04/05. Các buổi trước có một chút lệch thứ tự, nhưng từ đây mình sẽ giữ **roadmap gốc** làm chuẩn.

---

# 1. Redirect là gì?

Giả sử bạn request:

```text
https://example.com/old
```

Server trả:

```text
HTTP 301
Location: https://example.com/new
```

Server đang nói:

> URL này đã chuyển sang URL khác.

Browser thường tự động truy cập URL mới.

Luồng:

```text
Client
   │
   │ GET /old
   ▼
Server
   │
   │ 301
   │ Location: /new
   ▼
Client
   │
   │ GET /new
   ▼
Server
   │
   │ 200
   ▼
Response
```

---

# 2. Các Redirect Status Code

Các mã quan trọng:

|  Code | Ý nghĩa            |
| ----: | ------------------ |
| `301` | Moved Permanently  |
| `302` | Found              |
| `303` | See Other          |
| `307` | Temporary Redirect |
| `308` | Permanent Redirect |

Có một điểm cực kỳ quan trọng:

### 301/302/303

Trong nhiều trường hợp redirect sau POST có thể dẫn đến request tiếp theo trở thành GET tùy semantics/client behavior.

### 307/308

Giữ nguyên HTTP method.

Ví dụ:

```text
POST /login
   │
   │ 307
   ▼
POST /new-login
```

Trong khi với một số flow 303:

```text
POST /login
   │
   │ 303
   ▼
GET /profile
```

Khi crawler xử lý redirect, **không nên coi mọi redirect là giống nhau**.

---

# 3. Test Redirect

`httpbin` có endpoint:

```text
https://httpbin.org/redirect/2
```

Nó tạo redirect qua 2 bước.

Code:

```python id="1m3h9v"
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/redirect/2"
    )

    print("Status:", response.status_code)
    print("URL:", response.url)
    print()
    print(response.text)


if __name__ == "__main__":
    main()
```

Nếu redirect được follow tự động, URL cuối cùng sẽ khác URL ban đầu.

---

# 4. `response.url` rất quan trọng

Giả sử:

```text
Request URL:

https://example.com/old
```

redirect:

```text
https://example.com/new
```

Cuối cùng:

```python id="j2bl7p"
response.url
```

có thể là:

```text
https://example.com/new
```

Vì vậy:

```python id="yq3cju"
print(response.url)
```

không nhất thiết chính là URL bạn truyền vào `client.get()`.

---

# 5. URL ban đầu và URL cuối

Trong crawler nên phân biệt:

```text
requested_url
final_url
```

Ví dụ:

```python id="kz1r6u"
url = "https://example.com/old"

response = client.get(url)

print("Requested:", url)
print("Final:", response.url)
```

Kết quả conceptually:

```text
Requested:
https://example.com/old

Final:
https://example.com/new
```

Điều này rất hữu ích khi:

* canonical URL
* URL normalization
* deduplication
* logging
* debugging
* crawler database

Đặc biệt bạn đã học `yarl` về URL normalization và canonical URL, nên đây là nơi hai thư viện bắt đầu kết nối với nhau.

---

# 6. Redirect chain

Redirect không nhất thiết chỉ có một bước.

Ví dụ:

```text
A
│
│ 301
▼
B
│
│ 302
▼
C
│
│ 301
▼
D
│
│ 200
▼
Final Response
```

Đây gọi là:

```text
redirect chain
```

Crawler cần quan tâm vì chain quá dài có thể là dấu hiệu:

* URL configuration sai
* website redirect nhiều tầng
* redirect loop
* URL cũ
* authentication flow
* anti-bot behavior

---

# 7. Redirect Loop

Ví dụ server:

```text
A → B
B → A
```

Ta có:

```text
A
 ↓
B
 ↓
A
 ↓
B
 ↓
A
...
```

Nếu client không giới hạn redirect:

```text
infinite loop
```

Một HTTP client thường có cơ chế giới hạn hoặc xử lý redirect để tránh việc này.

Trong crawler production, chúng ta vẫn nên có:

```text
max_redirects
```

---

# 8. Tắt Redirect

Một HTTP client có thể cung cấp option để **không tự follow redirect**.

Với `primp`, API/version cụ thể nên kiểm tra theo phiên bản đang cài đặt trước khi đưa vào production code. Ý tưởng cần hiểu là:

```text
follow_redirects = False
```

Khi tắt automatic redirect:

```text
GET /old
   │
   ▼
301
Location: /new
   │
   ▼
Response
```

Client dừng tại `301`.

Sau đó application có thể tự quyết định:

```python id="h2u3kd"
if response.status_code in {301, 302, 303, 307, 308}:
    ...
```

---

# 9. Header `Location`

Redirect thường chứa:

```text
Location: https://example.com/new
```

Ta có thể đọc:

```python id="m6spxg"
location = response.headers.get("location")

print(location)
```

Flow:

```text
Response
│
├── status_code = 301
│
└── Location = /new
```

Nếu automatic redirect bị tắt, đây là thông tin quan trọng để crawler quyết định bước tiếp theo.

---

# 10. Redirect và Relative URL

`Location` không nhất thiết phải là absolute URL.

Server có thể trả:

```text
Location: /new-page
```

thay vì:

```text
Location: https://example.com/new-page
```

Lúc này crawler cần biến:

```text
/new-page
```

thành:

```text
https://example.com/new-page
```

Đây chính là việc bạn đã học ở `yarl`.

Ví dụ concept:

```python id="3jny4b"
from yarl import URL


base_url = URL("https://example.com/old")

location = URL("/new-page")

final_url = location if location.is_absolute() else base_url.join(location)

print(final_url)
```

Kết quả:

```text
https://example.com/new-page
```

---

# 11. `yarl` và `primp` phân chia trách nhiệm

Đây là architecture chúng ta muốn:

```text
yarl
 │
 ├── URL construction
 ├── URL joining
 ├── normalization
 ├── query
 └── canonicalization
```

Còn:

```text
primp
 │
 ├── HTTP request
 ├── Response
 ├── Cookies
 ├── Redirect
 └── Browser impersonation
```

Không nên biến `primp` thành URL manipulation library.

---

# 12. Redirect trong Novel Crawler

Giả sử crawler phát hiện:

```text
https://site.com/truyen/abc
```

Server trả:

```text
301
Location: /truyen/abc-moi
```

Fetcher:

```text
GET old URL
      │
      ▼
   301
      │
      ▼
GET new URL
      │
      ▼
   200
      │
      ▼
response.text
      │
      ▼
Parser
```

Parser cuối cùng nên parse:

```text
https://site.com/truyen/abc-moi
```

chứ không nhất thiết là URL ban đầu.

---

# 13. Redirect có thể ảnh hưởng URL của Novel

Ví dụ database có:

```text
novel.url
```

Nếu crawler request:

```text
https://site.com/novel/a
```

nhưng server redirect:

```text
https://site.com/novel/b
```

thì có ít nhất hai khái niệm:

```text
requested_url
canonical/final_url
```

Không nên vô thức ghi đè:

```python id="xv2q4n"
novel.url = response.url
```

mà phải xác định domain model muốn lưu cái gì.

Có thể cần:

```text
source_url
canonical_url
last_fetched_url
```

Đây là vấn đề **domain modeling**, không phải vấn đề của `primp`.

---

# 14. Redirect + Cookies

Redirect còn có thể kết hợp với cookie.

Ví dụ:

```text
GET /login
     │
     ▼
302 /dashboard
     │
     │ Set-Cookie: session=abc
     ▼
GET /dashboard
     │
     │ Cookie: session=abc
     ▼
200
```

Do đó flow:

```text
Cookies
+
Redirect
```

có thể tạo thành một session flow phức tạp.

Đây là lý do `Client` nên được giữ xuyên suốt một workflow khi cần session state.

---

# 15. Redirect + Authentication

Một flow thường gặp:

```text
GET /private
       │
       ▼
302 /login
       │
       ▼
GET /login
       │
       ▼
POST /login
       │
       ▼
302 /dashboard
       │
       ▼
GET /dashboard
       │
       ▼
200
```

Crawler không nên chỉ nhìn:

```python id="4ygbdy"
response.status_code == 200
```

mà phải hiểu **200 cuối cùng có thực sự là nội dung mình muốn không**.

Ví dụ server có thể redirect bạn tới:

```text
/login
```

và login page trả `200`.

HTTP request thành công, nhưng crawler chưa lấy được novel page.

Đây là một distinction rất quan trọng:

```text
HTTP success
      ≠
Business success
```

---

# 16. Đây là lý do cần Error Classification

Sau này trong Fetcher production chúng ta sẽ có:

```text
HTTP Response
      │
      ▼
Response Classifier
      │
      ├── SUCCESS
      ├── REDIRECT
      ├── NOT_FOUND
      ├── FORBIDDEN
      ├── RATE_LIMITED
      ├── SERVER_ERROR
      └── UNKNOWN
```

Sau đó:

```text
Classifier
     │
     ▼
Retry Policy
```

Ví dụ:

```text
404 → không retry
403 → có thể đổi strategy
429 → retry + backoff
500 → retry
502 → retry
503 → retry
301 → follow / canonicalize
```

**Đây chỉ là ví dụ policy**, chưa phải policy production cuối cùng của crawler.

---

# 17. Một Fetcher đơn giản

Ở giai đoạn hiện tại:

```python id="v7a8kw"
import primp


class PrimpFetcher:

    def __init__(self):
        self.client = primp.Client()

    def get(self, url: str):
        response = self.client.get(url)

        return response
```

Application:

```python id="t1s1xu"
def fetch_page(fetcher, url: str):
    response = fetcher.get(url)

    print("Requested:", url)
    print("Final:", response.url)
    print("Status:", response.status_code)

    return response
```

Test:

```python id="d5k2ku"
def main():
    fetcher = PrimpFetcher()

    response = fetch_page(
        fetcher,
        "https://httpbin.org/redirect/2",
    )

    print(response.text)


if __name__ == "__main__":
    main()
```

---

# 18. Một điều rất quan trọng: đừng tự follow redirect bằng tay ngay từ đầu

Ví dụ bạn không cần lập tức làm:

```python id="h1g7vl"
while response.status_code in {301, 302}:
    location = response.headers["location"]
    response = client.get(location)
```

Vì còn phải xử lý:

* absolute URL
* relative URL
* redirect limit
* method
* cookies
* status code
* redirect loop
* URL normalization
* history

HTTP client đã có cơ chế redirect riêng.

Ở tầng Fetcher, trước tiên nên **hiểu rõ behavior của client**, sau đó mới quyết định có cần custom redirect policy hay không.

---

# 19. Bài thực hành 1

Test:

```python id="y5x7lz"
import primp


def main():
    client = primp.Client()

    response = client.get(
        "https://httpbin.org/redirect/1"
    )

    print("Status:", response.status_code)
    print("Final URL:", response.url)


if __name__ == "__main__":
    main()
```

Quan sát:

```text
status_code
response.url
```

---

# 20. Bài thực hành 2 — Redirect chain

Đổi:

```python id="z6q8dy"
"https://httpbin.org/redirect/1"
```

thành:

```python id="sv0hcx"
"https://httpbin.org/redirect/5"
```

Quan sát URL cuối.

Mục tiêu:

```text
redirect/5
    ↓
...
    ↓
final response
```

---

# 21. Bài thực hành 3 — Location

Hãy thử request endpoint redirect nhưng **tắt automatic redirect theo API của phiên bản `primp` bạn đang cài**, sau đó in:

```text
Status:
Location:
URL:
```

Mục tiêu là hiểu:

```text
301/302/303/307/308
       │
       └── Location
```

Nếu API local của bạn không hỗ trợ option bạn thử, đừng tự viết workaround; hãy kiểm tra API/version trước.

---

# 22. Bài thực hành 4 — Xây RedirectInfo

Sau này chúng ta sẽ cần model hóa redirect.

Có thể bắt đầu bằng:

```python id="5svqk4"
from dataclasses import dataclass


@dataclass
class RedirectInfo:
    status_code: int
    from_url: str
    to_url: str
```

Ví dụ:

```text
RedirectInfo(
    status_code=301,
    from_url="https://example.com/a",
    to_url="https://example.com/b",
)
```

Nhưng **chưa cần đưa class này vào domain**.

Hiện tại chỉ cần hiểu concept.

---

# 23. Tổng kết Phần I

Sau 10 buổi, bạn đã có nền tảng HTTP Client:

```text
                 primp.Client
                      │
        ┌─────────────┼──────────────┐
        │             │              │
       GET           POST           ...
        │             │
        ▼             ▼
     params=       data=
                   json=
        │             │
        └──────┬──────┘
               ▼
            Response
               │
       ┌───────┼────────┐
       ▼       ▼        ▼
    status    text     json
       │
       ▼
    redirect
       │
       ▼
   final URL
```

Các khái niệm cần nắm chắc:

```text
Client
GET
POST
Query Params
Headers
JSON
Form Data
Cookies
Response
Redirect
```

Và kiến trúc crawler:

```text
                  Application
                       │
              ┌────────┴────────┐
              │                 │
           Fetcher            Parser
              │                 │
              ▼                 ▼
        PrimpFetcher         Selectolax
              │
              ▼
            primp
              │
              ▼
          HTTP Response
              │
              ▼
        response.text
              │
              ▼
            Parser
```

### Phần II sẽ đi vào HTTP Client

```text
11. Timeout
12. Exception
13. Authentication
14. Proxy
15. SSL / Verify
16. Session / Connection Reuse
17. Default Headers
18. Default Params
19. Request Options
20. Client Lifecycle
```

Đặc biệt với project Novel Crawler của bạn, **Buổi 11 — Timeout** sẽ là bước chuyển từ “biết gửi HTTP request” sang “xây Fetcher có khả năng chạy crawler thực tế”.
