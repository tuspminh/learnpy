Dưới đây là bảng tra cứu toàn diện về các Class, Method và Property được cung cấp bởi thư viện **`primp`** (phiên bản dựa trên engine `rquest` từ Rust).

---

## 1. Class: `primp.Client` (Đồng bộ - Synchronous)

Client chính dùng cho các tác vụ crawl/request thông thường.

### Khởi tạo (`__init__`)

```python
primp.Client(
    impersonate: Optional[str] = None,
    os: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    cookie_store: bool = True,
    proxy: Optional[str] = None,
    timeout: Optional[float] = 30.0,
    verify: bool = True,
    follow_redirects: bool = True,
    max_redirects: int = 20,
    http2_only: bool = False
)

```

**Các tham số chính:**

* **`impersonate`**: Giả lập trình duyệt. Các giá trị phổ biến:
* *Chrome:* `chrome_100`, `chrome_116`, `chrome_120`, `chrome_126`, `chrome_130`...
* *Firefox:* `firefox_109`, `firefox_117`, `firefox_120`...
* *Safari:* `safari_16_5`, `safari_17_0`, `safari_ios_16_5`...
* *Edge:* `edge_101`, `edge_120`...


* **`os`**: Hệ điều hành tạo vân tay (`windows`, `macos`, `linux`, `ios`, `android`).
* **`cookie_store`**: Nếu `True`, Client tự lưu và gửi lại cookie giữa các request liên tiếp.
* **`proxy`**: URL proxy (ví dụ: `http://user:pass@ip:port` hoặc `socks5://ip:port`).
* **`verify`**: Xác thực SSL/TLS certificates (`True`/`False`).

---

### Các Method HTTP trong `Client`

Mọi HTTP method đều nhận các tham số tương tự như thư viện `requests`:

```python
# Cú pháp tổng quát:
client.get(url, params=None, headers=None, cookies=None, auth=None, timeout=None)
client.post(url, data=None, json=None, files=None, headers=None, ...)

```

* **`client.get(url, ...)`**: Gửi HTTP GET request.
* **`client.post(url, data=..., json=..., ...)`**: Gửi HTTP POST request.
* **`client.put(url, ...)`**: Gửi HTTP PUT request.
* **`client.patch(url, ...)`**: Gửi HTTP PATCH request.
* **`client.delete(url, ...)`**: Gửi HTTP DELETE request.
* **`client.head(url, ...)`**: Gửi HTTP HEAD request.
* **`client.options(url, ...)`**: Gửi HTTP OPTIONS request.
* **`client.request(method, url, ...)`**: Gửi request tùy chỉnh bằng cách truyền tên `method` dạng chuỗi (vd: `"SEARCH"`).

---

## 2. Class: `primp.AsyncClient` (Bất đồng bộ - Asynchronous)

Dùng khi bạn làm việc với `asyncio` để tối ưu hóa hiệu năng crawl dữ liệu song song.

### Cấu trúc và khởi tạo

Tất cả các tham số truyền vào `__init__` của `AsyncClient` giống hệt với `Client`.

### Các Method (yêu cầu `await`)

```python
import primp
import asyncio

async def fetch():
    async with primp.AsyncClient(impersonate="chrome_126") as client:
        response = await client.get("https://httpbin.org/get")
        print(response.status_code)

asyncio.run(fetch())

```

* **`await client.get(...)`**
* **`await client.post(...)`**
* **`await client.put(...)`**
* **`await client.delete(...)`**
* **`await client.request(...)`**

---

## 3. Class: `primp.Response` (Kết quả trả về)

Khi bạn thực hiện một request, đối tượng trả về là một `Response` chứa dữ liệu của phản hồi từ server.

### các Property (Thuộc tính)

| Property | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| **`response.status_code`** | `int` | Mã trạng thái HTTP (vd: 200, 404, 503). |
| **`response.text`** | `str` | Nội dung phản hồi dạng chuỗi (đã decode). |
| **`response.content`** | `bytes` | Nội dung phản hồi ở dạng bytes thô (dùng khi tải ảnh, file PDF...). |
| **`response.headers`** | `dict` | Các HTTP headers trả về từ server. |
| **`response.cookies`** | `dict` | Tất cả cookie mà server trả về trong request này. |
| **`response.url`** | `str` | URL cuối cùng sau khi đã xử lý các chuyển hướng (redirects). |
| **`response.encoding`** | `str` | Bảng mã ký tự của response (vd: `utf-8`). |

### Các Method trong `Response`

* **`response.json()`**: Decode nội dung `text` thành đối tượng Python `dict` hoặc `list`. Nếu response không phải dạng JSON sẽ bắn ra ngoại lệ (`ValueError`).

---

## 4. Các Hàm Tiện Ích (Top-level Functions)

Nếu không muốn tạo đối tượng `Client` quản lý phiên, bạn có thể gọi trực tiếp các hàm tiện ích như thư viện `requests`:

```python
import primp

# Gửi GET request trực tiếp
resp = primp.get("https://httpbin.org/ip", impersonate="firefox_120")

# Gửi POST request trực tiếp
resp = primp.post("https://httpbin.org/post", json={"key": "value"}, impersonate="chrome_126")

```

---

## 5. Danh sách các Browser Fingerprints khả dụng

Bạn có thể kiểm tra danh sách đầy đủ các trình duyệt mà `primp` hỗ trợ giả lập ngay trong Python:

```python
import primp

# In ra danh sách các impersonate strings hỗ trợ
print(primp.IMPERSONATE_TARGETS)

```

**Ví dụ các target hay dùng:**

* `chrome_100`, `chrome_104`, `chrome_116`, `chrome_120`, `chrome_126`
* `safari_16_5`, `safari_17_0`, `safari_ios_17_0`
* `firefox_109`, `firefox_117`, `firefox_120`
* `edge_101`, `edge_120`