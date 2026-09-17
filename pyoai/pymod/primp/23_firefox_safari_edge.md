# Phần III — Browser Impersonation

# Buổi 23 — Firefox / Safari / Edge

Ở Buổi 22, chúng ta học **Chrome fingerprint**. Hôm nay mở rộng sang ba browser khác:

```text
Chrome
Firefox
Safari
Edge
```

Điểm quan trọng nhất của bài này là:

> **Không phải cứ thay `User-Agent` là đã chuyển từ Chrome sang Firefox/Safari/Edge. Mỗi browser có một profile giao tiếp riêng.**

`primp` 2.0.1 hiện có profile cho Chrome, Safari, Edge, Firefox và Opera; mỗi profile bao gồm các thiết lập liên quan đến TLS, HTTP/2 và default headers. ([Docs.rs][1])

---

# 1. Browser family trong `primp`

Hiện tại `primp 2.0.1` hỗ trợ các nhóm chính:

| Browser | Một số profile hiện tại                                            |
| ------- | ------------------------------------------------------------------ |
| Chrome  | `chrome_144` … `chrome_153`, `chrome`                              |
| Firefox | `firefox_140`, `firefox_146` … `firefox_151`, `firefox`            |
| Safari  | `safari_18.5`, `safari_26`, `safari_26.3`, `safari_26.4`, `safari` |
| Edge    | `edge_144` … `edge_153`, `edge`                                    |
| Opera   | `opera_126` … `opera_135`                                          |
| Random  | `random`                                                           |

Danh sách này là **version-dependent**, nên không nên lấy các profile cũ từ tutorial trên mạng rồi mặc định rằng chúng vẫn tồn tại. ([Docs.rs][1])

---

# 2. Cách sử dụng cơ bản

Ví dụ Chrome:

```python
import primp

client = primp.Client(
    impersonate="chrome_146"
)
```

Firefox:

```python
import primp

client = primp.Client(
    impersonate="firefox_146"
)
```

Safari:

```python
import primp

client = primp.Client(
    impersonate="safari_26"
)
```

Edge:

```python
import primp

client = primp.Client(
    impersonate="edge_146"
)
```

Đây là API Python chính thức hiện tại của `primp`. ([PyPI][2])

---

# 3. Đừng hiểu `firefox_146` là User-Agent

Đây là lỗi rất dễ mắc.

Không nên suy nghĩ:

```text
firefox_146
    ↓
User-Agent = Firefox 146
```

Mà:

```text
firefox_146
       │
       ├── Firefox-like headers
       ├── Firefox TLS configuration
       └── Firefox HTTP/2 behavior
```

Tài liệu `primp` mô tả `Impersonate` là browser version ánh xạ tới **TLS fingerprint và default headers**, trong khi module impersonation chứa thêm HTTP/2 configuration. ([Docs.rs][3])

---

# 4. Chrome và Edge

Đây là trường hợp thú vị nhất.

Edge hiện đại dựa trên Chromium.

Vì vậy:

```text
Chrome
   │
   └── Chromium

Edge
   │
   └── Chromium
```

Nhưng không có nghĩa:

```text
Chrome == Edge
```

Tài liệu `primp` mô tả Edge là:

> Chrome-based TLS/HTTP2, nhưng có Edge-specific headers. ([Docs.rs][3])

Có thể hình dung:

```text
Chrome
 ├── Chromium-based TLS
 ├── Chromium HTTP/2
 └── Chrome headers

Edge
 ├── Chromium-based TLS
 ├── Chromium HTTP/2
 └── Edge-specific headers
```

---

# 5. Ví dụ Chrome vs Edge

```python
import primp


URL = "https://tls.peet.ws/api/all"


def chrome():
    client = primp.Client(
        impersonate="chrome_146"
    )

    return client.get(URL)


def edge():
    client = primp.Client(
        impersonate="edge_146"
    )

    return client.get(URL)


def main():
    chrome_response = chrome()
    edge_response = edge()

    print("CHROME")
    print(chrome_response.text)

    print()
    print("=" * 80)
    print()

    print("EDGE")
    print(edge_response.text)


if __name__ == "__main__":
    main()
```

Bài tập ở đây không phải tìm "browser nào tốt hơn".

Mục tiêu là quan sát:

```text
Chrome profile
     vs
Edge profile
```

và hiểu rằng browser family là một phần của fingerprint.

---

# 6. Firefox khác Chromium

Chrome và Edge đều thuộc hệ sinh thái Chromium.

Firefox sử dụng engine khác:

```text
Chrome
   ↓
Chromium / Blink

Edge
   ↓
Chromium / Blink

Firefox
   ↓
Gecko
```

Điều này rất quan trọng đối với fingerprint.

Ta không nên làm:

```text
Firefox
   ↓
Chrome TLS
   ↓
Firefox User-Agent
```

mà cần profile nhất quán:

```text
Firefox
   │
   ├── Firefox headers
   ├── Firefox TLS
   └── Firefox HTTP/2
```

`primp` có module Firefox riêng trong impersonation settings. ([Docs.rs][3])

---

# 7. Test Firefox

```python
import primp


def main():
    client = primp.Client(
        impersonate="firefox_146"
    )

    response = client.get(
        "https://tls.peet.ws/api/all"
    )

    print(response.text)


if __name__ == "__main__":
    main()
```

Nếu profile `firefox_146` tồn tại trong version bạn đang cài thì request sẽ sử dụng profile đó.

Bạn cũng có thể kiểm tra version `primp`:

```python
import importlib.metadata

print(
    importlib.metadata.version("primp")
)
```

Điều này quan trọng vì danh sách profile thay đổi theo phiên bản. ([Docs.rs][1])

---

# 8. Safari đặc biệt hơn

Safari khác Chrome/Edge/Firefox ở chỗ:

```text
Safari
   ↓
WebKit ecosystem
```

và profile của Safari có những version riêng.

Hiện `primp` 2.0.1 liệt kê:

```text
safari_18.5
safari_26
safari_26.3
safari_26.4
safari
```

([Docs.rs][1])

Ví dụ:

```python
import primp


client = primp.Client(
    impersonate="safari_26"
)

response = client.get(
    "https://tls.peet.ws/api/all"
)

print(response.text)
```

---

# 9. Safari không chỉ có "Safari"

Ta sẽ gặp:

```text
Safari desktop
Safari mobile
```

và OS trở thành yếu tố quan trọng.

Đây chính là lý do roadmap của chúng ta tiếp theo là:

```text
24. impersonate_os
```

Hiện `primp` hỗ trợ các OS impersonation:

```text
android
ios
linux
macos
windows
random
```

([Docs.rs][1])

---

# 10. Firefox cũng có version profile

Ví dụ:

```python
client = primp.Client(
    impersonate="firefox_146"
)
```

Không nên viết:

```python
client = primp.Client(
    impersonate="firefox"
)
```

rồi nghĩ rằng nó nhất thiết là một version cụ thể cố định.

Theo tài liệu hiện tại, profile không version như:

```text
chrome
firefox
safari
edge
```

có cơ chế resolve profile; `imp` cũng cung cấp các hàm resolve/random profile. ([Docs.rs][3])

Với production crawler, ta sẽ bàn về việc:

```text
generic profile
vs
pinned profile
```

ở phần BrowserClient.

---

# 11. Generic profile

Ví dụ:

```python
client = primp.Client(
    impersonate="firefox"
)
```

Có thể xem:

```text
firefox
   ↓
Firefox family
   ↓
một profile cụ thể
```

Trong tài liệu Rust, `resolve_impersonate` được dùng để resolve profile không version thành version cụ thể. ([Docs.rs][3])

Tư duy:

```text
"firefox"
    =
"Firefox family"
```

không nhất thiết đồng nghĩa:

```text
"Firefox 146 cố định"
```

---

# 12. Pinned profile

Ngược lại:

```python
client = primp.Client(
    impersonate="firefox_146"
)
```

Ta biết rõ:

```text
Browser = Firefox
Version = 146
```

Điều này hữu ích cho:

* reproducible testing
* debug
* fingerprint comparison
* crawler configuration

Ví dụ:

```text
Development
    ↓
firefox_146

Production
    ↓
firefox_146
```

thì việc phân tích behavior dễ tái lập hơn.

---

# 13. Random profile

`primp` hiện cũng có:

```python
client = primp.Client(
    impersonate="random"
)
```

Profile `random` được liệt kê trong danh sách impersonation hiện tại. ([Docs.rs][1])

Nhưng **đừng vội dùng random cho Novel Crawler**.

Ví dụ:

```text
Request 1 → Chrome
Request 2 → Firefox
Request 3 → Safari
Request 4 → Edge
```

sẽ tạo ra một identity rất thiếu nhất quán.

Đặc biệt nếu crawler còn giữ:

```text
Cookies
```

thì:

```text
Cookie
  +
Chrome
  +
Firefox
  +
Safari
```

có thể trở thành một profile rất kỳ lạ.

---

# 14. Browser Profile và Cookie phải nhất quán

Hãy hình dung:

```text
Session
 │
 ├── Cookies
 ├── Headers
 ├── Browser Profile
 └── Connection
```

Nếu:

```text
Session
  ↓
Chrome
```

thì nên tiếp tục:

```text
Session
  ↓
Chrome
```

thay vì:

```text
Request 1 → Chrome
Request 2 → Firefox
Request 3 → Safari
```

Đây là một trong những lý do sau này chúng ta sẽ thiết kế:

```text
BrowserClient
```

theo **profile/session**, thay vì random browser cho từng request.

---

# 15. Browser Profile ≠ OS

Một lỗi tư duy khác:

```text
firefox_146
```

không nên hiểu là:

```text
Firefox 146 + Windows
```

OS là concern riêng.

Ta có:

```text
Browser
   +
OS
   ↓
Browser Fingerprint
```

Ví dụ:

```text
Firefox
+
Windows
```

khác về persona so với:

```text
Firefox
+
Linux
```

và:

```text
Safari
+
macOS
```

lại là một combination khác.

Buổi 24 sẽ đi sâu vào điều này.

---

# 16. Chrome vs Edge vs Firefox vs Safari

Ta có thể xây một bảng tư duy:

|                 | Chrome   | Edge                | Firefox | Safari         |
| --------------- | -------- | ------------------- | ------- | -------------- |
| Engine family   | Chromium | Chromium            | Gecko   | WebKit         |
| TLS profile     | Chrome   | Edge                | Firefox | Safari         |
| HTTP/2 profile  | Chrome   | Edge/Chromium-based | Firefox | Safari         |
| Headers         | Chrome   | Edge-specific       | Firefox | Safari         |
| OS sensitivity  | Có       | Có                  | Có      | Rất đáng chú ý |
| `primp` profile | Có       | Có                  | Có      | Có             |

Các profile này không phải chỉ là UA strings; `primp` định nghĩa browser-specific settings cho TLS/HTTP2/headers. ([Docs.rs][3])

---

# 17. Bài thực hành — so sánh 4 browser

Tạo:

```text
lesson_23.py
```

```python
import primp


URL = "https://tls.peet.ws/api/all"


PROFILES = [
    "chrome_146",
    "edge_146",
    "firefox_146",
    "safari_26",
]


def test_profile(profile: str):
    print("=" * 80)
    print("PROFILE:", profile)
    print("=" * 80)

    client = primp.Client(
        impersonate=profile
    )

    response = client.get(URL)

    print(response.text)
    print()


def main():
    for profile in PROFILES:
        test_profile(profile)


if __name__ == "__main__":
    main()
```

**Lưu ý:** nếu một profile cụ thể không tồn tại trong version `primp` bạn đang cài, thay nó bằng profile có trong danh sách hiện tại của `pip`/PyPI. Danh sách chính thức của 2.0.1 hiện có `edge_146`, `firefox_146`, `chrome_146` và các Safari profile được liệt kê ở trên. ([PyPI][2])

---

# 18. Bài thực hành tốt hơn — chỉ lấy thông tin cần thiết

Response từ:

```text
https://tls.peet.ws/api/all
```

khá dài.

Ta có thể:

```python
import primp


URL = "https://tls.peet.ws/api/all"


def inspect(profile: str):
    client = primp.Client(
        impersonate=profile
    )

    response = client.get(URL)

    data = response.json()

    print("=" * 60)
    print(profile)
    print("=" * 60)

    print("User-Agent:")
    print(data.get("user_agent"))

    print()

    print("HTTP Version:")
    print(data.get("http_version"))

    print()

    print("TLS:")
    print(data.get("tls"))


def main():
    for profile in [
        "chrome_146",
        "edge_146",
        "firefox_146",
        "safari_26",
    ]:
        inspect(profile)


if __name__ == "__main__":
    main()
```

Cấu trúc response của endpoint có thể thay đổi, nên mục đích của bài là **quan sát**, không phải phụ thuộc vào một schema cố định.

---

# 19. Không nên làm Browser Factory kiểu này

Có thể bạn sẽ nghĩ:

```python
class BrowserFactory:

    def create(self, browser):
        if browser == "chrome":
            return primp.Client(
                impersonate="chrome_146"
            )

        elif browser == "firefox":
            return primp.Client(
                impersonate="firefox_146"
            )

        elif browser == "edge":
            return primp.Client(
                impersonate="edge_146"
            )

        elif browser == "safari":
            return primp.Client(
                impersonate="safari_26"
            )
```

Vấn đề:

```text
if
elif
elif
elif
elif
elif
...
```

Khi profile tăng lên, class này sẽ phình ra.

---

# 20. Tách Browser Profile khỏi Client

Ta có thể bắt đầu đơn giản:

```python
PROFILES = {
    "chrome": "chrome_146",
    "edge": "edge_146",
    "firefox": "firefox_146",
    "safari": "safari_26",
}
```

Sau đó:

```python
import primp


class BrowserClient:

    def __init__(self, profile: str):
        self.client = primp.Client(
            impersonate=profile
        )

    def get(self, url: str):
        return self.client.get(url)
```

Sử dụng:

```python
client = BrowserClient(
    PROFILES["firefox"]
)

response = client.get(
    "https://example.com"
)
```

Đây **chưa phải** BrowserClient cuối cùng.

Đây chỉ là bước đầu để chúng ta hiểu separation.

---

# 21. Tại sao đây là SOLID?

Ta đang tách:

```text
Browser Profile
       │
       ▼
HTTP Client
```

thay vì:

```text
HTTP Client
  ├── Chrome
  ├── Firefox
  ├── Safari
  ├── Edge
  ├── Proxy
  ├── Retry
  ├── Rate Limit
  └── ...
```

Sau này:

```text
BrowserProfile
ProxyStrategy
RetryPolicy
RateLimiter
```

sẽ là các concern riêng.

Đây chính là hướng:

```text
Single Responsibility
Dependency Inversion
Composition
```

mà bạn đã học trong OOP/DDD.

---

# 22. Một lỗi khác: đổi browser giữa request

Không nên:

```python
for url in urls:
    profile = random.choice([
        "chrome_146",
        "firefox_146",
        "safari_26",
    ])

    client = primp.Client(
        impersonate=profile
    )

    client.get(url)
```

Vấn đề không phải "random luôn sai".

Vấn đề là **identity lifecycle**.

Tốt hơn:

```text
BrowserClient
     │
     ├── profile = chrome_146
     │
     ├── request 1
     ├── request 2
     ├── request 3
     └── request 4
```

Nếu cần thay profile:

```text
BrowserClient A
    Chrome

BrowserClient B
    Firefox
```

thay vì:

```text
Request 1 → Chrome
Request 2 → Firefox
Request 3 → Safari
```

---

# 23. Trong Novel Crawler

Ta có thể hình dung:

```text
Crawler
   │
   ▼
Fetcher
   │
   ▼
BrowserClient
   │
   ├── BrowserProfile
   │
   ├── Cookies
   │
   ├── Headers
   │
   └── Primp Client
```

Ví dụ:

```python
browser_client = BrowserClient(
    profile="chrome_146"
)
```

Sau đó:

```python
fetcher = PrimpFetcher(
    client=browser_client
)
```

Application:

```python
response = fetcher.get(chapter_url)
```

Application không cần biết:

```text
Chrome
Firefox
TLS
HTTP/2
```

---

# 24. Một nguyên tắc production rất quan trọng

Đừng chọn browser dựa trên câu:

> "Browser nào mạnh nhất?"

Đó không phải cách tư duy đúng.

Hãy chọn:

```text
Website target
      │
      ▼
Expected browser profile
      │
      ▼
Browser + version + OS
      │
      ▼
BrowserClient
```

Ví dụ configuration:

```python
browser = "chrome"
version = 146
os = "windows"
```

sau này có thể trở thành:

```python
BrowserProfile(
    browser="chrome",
    version=146,
    os="windows",
)
```

Đây chính là hướng chúng ta sẽ xây ở **Buổi 24**.

---

# 25. Tổng kết Buổi 23

Điều quan trọng nhất:

```text
Chrome
  ↓
Chromium

Edge
  ↓
Chromium-based

Firefox
  ↓
Gecko

Safari
  ↓
WebKit
```

Vì vậy:

```text
Chrome fingerprint
        ≠
Firefox fingerprint
        ≠
Safari fingerprint
        ≠
Edge fingerprint
```

`primp` phản ánh sự khác biệt này bằng các browser-specific impersonation profiles. Tài liệu hiện tại tách riêng module settings cho Chrome, Edge, Firefox và Safari; Edge dùng nền Chromium nhưng có headers riêng, còn Chrome/Safari có các cấu hình TLS/HTTP2 theo version. ([Docs.rs][3])

### Mô hình cần nhớ

```text
                  Browser Profile
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
          Headers       TLS        HTTP/2
             │           │           │
             └───────────┼───────────┘
                         ▼
                    primp.Client
                         │
                         ▼
                       Server
```

Và:

```text
Browser Profile
      +
OS
      ↓
Browser Persona
```

Đó là lý do **Buổi 24 — `impersonate_os`** sẽ nối trực tiếp từ bài hôm nay sang việc xây một `BrowserProfile` hoàn chỉnh cho Novel Crawler.

[1]: https://docs.rs/crate/primp/latest?utm_source=chatgpt.com "primp 2.0.1 - Docs.rs"
[2]: https://pypi.org/project/primp/2.0.1/?utm_source=chatgpt.com "primp · PyPI"
[3]: https://docs.rs/primp/latest/primp/imp/index.html?utm_source=chatgpt.com "primp::imp - Rust"
