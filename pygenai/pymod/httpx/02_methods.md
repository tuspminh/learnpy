**HTTPX** là một thư viện HTTP Client toàn diện dành cho Python, hỗ trợ cả hai cơ chế **Synchronous (Đồng bộ)** và **Asynchronous (Bất đồng bộ)**, hỗ trợ HTTP/1.1 lẫn HTTP/2.

Dưới đây là chi tiết toàn bộ các **Object (Đối tượng)**, **Method (Phương thức)** và **Attribute (Thuộc tính)** quan trọng nhất trong `httpx`.

---

## 1. Top-Level Functions (Hàm toàn cục)

Được sử dụng cho các request nhanh đơn lẻ mà không cần quản lý Session hay Connection Pool.

```python
import httpx

response = httpx.get("https://httpbin.org/get", params={"key": "value"})

```

| Hàm | Mô tả | Key Parameters thường dùng |
| --- | --- | --- |
| `httpx.get(url, ...)` | Gửi HTTP GET request | `params`, `headers`, `cookies`, `auth`, `timeout`, `follow_redirects` |
| `httpx.post(url, ...)` | Gửi HTTP POST request | `data` (form-data/urlencoded), `json` (dict), `files` (multipart) |
| `httpx.put(url, ...)` | Gửi HTTP PUT request | `data`, `json`, `files` |
| `httpx.patch(url, ...)` | Gửi HTTP PATCH request | `data`, `json` |
| `httpx.delete(url, ...)` | Gửi HTTP DELETE request | `params`, `headers` |
| `httpx.head(url, ...)` | Gửi HTTP HEAD request | `headers` |
| `httpx.options(url, ...)` | Gửi HTTP OPTIONS request | `headers` |
| `httpx.request(method, url, ...)` | Gửi request với method tùy chỉnh | `method` ("GET", "POST", "CUSTOM", ...), `url` |
| `httpx.stream(method, url, ...)` | Context manager để stream response data | `method`, `url` |

---

## 2. Đối tượng `Client` & `AsyncClient`

Dùng để quản lý Session, giữ lại Cookies, tái sử dụng Connection Pool và cấu hình chung cho nhiều Request.

### A. Khởi tạo & Tham số cấu hình (Initialization Parameters)

```python
# Synchronous
with httpx.Client(base_url="https://api.example.com", timeout=10.0) as client:
    res = client.get("/users")

# Asynchronous
async with httpx.AsyncClient(base_url="https://api.example.com", http2=True) as client:
    res = await client.get("/users")

```

| Tham số | Kiểu dữ liệu | Ý nghĩa |
| --- | --- | --- |
| `base_url` | `str | URL` | URL gốc, các request sau chỉ cần điền path tương đối (ví dụ: `/users`) |
| `headers` | `dict | Headers` | Headers mặc định áp dụng cho tất cả request trong Client |
| `cookies` | `dict | Cookies` | Cookies mặc định |
| `params` | `dict | QueryParams` | Query parameters mặc định gắn vào mọi request |
| `auth` | `tuple | Auth` | Xác thực mặc định (ví dụ: `("user", "pass")` hoặc `httpx.BasicAuth(...)`) |
| `timeout` | `float | Timeout` | Cấu hình thời gian chờ mặc định (mặc định là 5.0 giây) |
| `limits` | `Limits` | Cấu hình giới hạn Connection Pool |
| `proxy` | `str | Proxy` | Cấu hình Proxy (ví dụ: `"[http://10.10.1.10:3128](http://10.10.1.10:3128)"`) |
| `verify` | `bool | str` | Xác thực SSL certificate (`True`/`False` hoặc đường dẫn file CA bundle) |
| `cert` | `str | tuple` | Đường dẫn SSL Client Certificate file |
| `http2` | `bool` | Kích hoạt giao thức HTTP/2 (cần cài `httpx[http2]`) |
| `follow_redirects` | `bool` | Tự động chuyển hướng khi gặp status 3xx (`Default: False`) |
| `event_hooks` | `dict` | Đăng ký callback khi request/response diễn ra (ví dụ: `{"response": [hook_func]}`) |

### B. Các Phương thức (Methods) của Client

* **HTTP Methods:** `.get()`, `.post()`, `.put()`, `.patch()`, `.delete()`, `.head()`, `.options()`, `.request()` *(Cách dùng tương tự các top-level function)*.
* `.build_request(method, url, ...)` $\rightarrow$ Tạo đối tượng `httpx.Request` mà không gửi ngay.
* `.send(request, ...)` $\rightarrow$ Gửi một đối tượng `httpx.Request` đã chuẩn bị trước.
* `.stream(method, url, ...)` $\rightarrow$ Trả về Context Manager để stream dữ liệu từng phần.
* `.close()` (dành cho `Client`) / `.aclose()` (dành cho `AsyncClient`) $\rightarrow$ Đóng toàn bộ Connection Pool.

### C. Các Thuộc tính (Attributes) của Client

```python
client.headers["Authorization"] = "Bearer TOKEN" # Sửa header trực tiếp
print(client.is_closed) # Kiểm tra xem Client đã đóng chưa

```

| Thuộc tính | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `.headers` | `Headers` | Dictionary-like chứa các HTTP Headers mặc định |
| `.cookies` | `Cookies` | Jar chứa Cookies lưu trữ qua các lượt request |
| `.params` | `QueryParams` | Các tham số URL mặc định |
| `.base_url` | `URL` | URL cơ sở đã được parse thành object |
| `.is_closed` | `bool` | Trả về `True` nếu Client đã bị đóng |

---

## 3. Đối tượng `Response`

Đối tượng nhận được sau khi thực hiện request (`response = client.get(...)`).

### A. Thuộc tính dữ liệu & Metadata (Attributes)

```python
response = httpx.get("https://httpbin.org/json")

print(response.status_code) # 200
print(response.json())      # Trả về dict/list Python

```

| Thuộc tính | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `.status_code` | `int` | Mã trạng thái HTTP (ví dụ: `200`, `404`, `500`) |
| `.text` | `str` | Nội dung response dạng chuỗi text (tự giải mã mã hóa) |
| `.content` | `bytes` | Nội dung response dạng dữ liệu nhị phân thô (raw bytes) |
| `.headers` | `Headers` | HTTP Response Headers (không phân biệt hoa thường) |
| `.cookies` | `Cookies` | Cookies được gửi về từ server (`Set-Cookie`) |
| `.url` | `URL` | URL cuối cùng của request (sau khi đã follow redirects) |
| `.encoding` | `str` | Bảng mã ký tự dùng để decode `.text` (ví dụ: `'utf-8'`) |
| `.elapsed` | `datetime.timedelta` | Thời gian từ khi gửi request đến khi nhận xong headers |
| `.request` | `Request` | Đối tượng `httpx.Request` đã tạo ra response này |
| `.history` | `List[Response]` | Danh sách các response chuyển hướng trước đó (nếu có) |
| `.http_version` | `str` | Phiên bản HTTP được server sử dụng (ví dụ: `"HTTP/1.1"`, `"HTTP/2"`) |

### B. Các Thuộc tính Kiểm tra Trạng thái (Boolean Helpers)

| Thuộc tính | Trả về `True` khi Status Code |
| --- | --- |
| `.is_informational` | `100` – `199` |
| `.is_success` | `200` – `299` |
| `.is_redirect` | `300` – `399` |
| `.is_client_error` | `400` – `499` |
| `.is_server_error` | `500` – `599` |
| `.is_error` | `400` – `599` (Bao gồm cả lỗi Client và Server) |

### C. Phương thức (Methods) của Response

| Phương thức | Ý nghĩa |
| --- | --- |
| `.json()` | Parse nội dung response thành Python object (dict/list). Bắn ra `json.JSONDecodeError` nếu hỏng |
| `.raise_for_status()` | Bắn ra ngoại lệ `httpx.HTTPStatusError` nếu status code thuộc nhóm `4xx` hoặc `5xx` |
| `.read()` / `.aread()` | Đọc toàn bộ dung lượng response vào bộ nhớ (khi dùng với `httpx.stream`) |
| `.close()` / `.aclose()` | Đóng stream response thủ công |

### D. Các Phương thức Streaming (Dùng khi tải file lớn)

```python
# Sync Streaming
with httpx.stream("GET", "https://example.com/large-file.zip") as response:
    with open("file.zip", "wb") as f:
        for chunk in response.iter_bytes(chunk_size=8192):
            f.write(chunk)

# Async Streaming
async with client.stream("GET", "https://example.com/large-file.zip") as response:
    async for text_line in response.aiter_lines():
        print(text_line)

```

| Phương thức Sync | Phương thức Async tương ứng | Mô tả |
| --- | --- | --- |
| `.iter_bytes(chunk_size=None)` | `.aiter_bytes(...)` | Duyệt dữ liệu dạng `bytes` theo từng khối nhỏ |
| `.iter_text(chunk_size=None)` | `.aiter_text(...)` | Duyệt dữ liệu dạng chuỗi `str` theo từng khối nhỏ |
| `.iter_lines()` | `.aiter_lines()` | Duyệt dữ liệu dòng theo dòng (xuống dòng `\n`) |
| `.iter_raw()` | `.aiter_raw()` | Duyệt dữ liệu thô chưa giải nén (gzip/deflate) |

---

## 4. Đối tượng `Request`

Đại diện cho HTTP Request được gửi đi. Bạn có thể kiểm tra hoặc tạo thủ công qua `client.build_request()`.

| Thuộc tính / Method | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `.method` | `str` | Tên phương thức HTTP dạng chữ hoa (ví dụ: `"GET"`, `"POST"`) |
| `.url` | `URL` | Đối tượng URL đích của request |
| `.headers` | `Headers` | Danh sách headers được gửi đi |
| `.content` | `bytes` | Nội dung body của request dạng bytes |
| `.read()` / `.aread()` | `bytes` | Đọc toàn bộ luồng request body |

---

## 5. Các Đối tượng Cấu hình & Helper (Configuration Classes)

### A. `httpx.Timeout`

Quản lý cấu hình thời gian chờ chi tiết cho từng giai đoạn.

```python
timeout = httpx.Timeout(
    timeout=10.0,   # Mặc định áp dụng cho tất cả nếu các tham số sau không khai báo
    connect=5.0,    # Thời gian chờ thiết lập kết nối TCP/TLS
    read=5.0,       # Thời gian chờ nhận 1 block dữ liệu từ server
    write=5.0,      # Thời gian chờ gửi 1 block dữ liệu tới server
    pool=2.0        # Thời gian chờ lấy kết nối trống từ Connection Pool
)
client = httpx.Client(timeout=timeout)

```

### B. `httpx.Limits`

Cấu hình Connection Pooling để tối ưu hiệu năng.

```python
limits = httpx.Limits(
    max_connections=100,           # Số kết nối đồng thời tối đa
    max_keepalive_connections=20,  # Số kết nối tối đa giữ lại ở trạng thái rảnh (keep-alive)
    keepalive_expiry=5.0           # Thời gian (giây) ngắt kết nối rảnh
)
client = httpx.Client(limits=limits)

```

### C. `httpx.URL`

Đối tượng bóc tách và thao tác với đường dẫn URL.

```python
url = httpx.URL("https://user:pass@example.com:8080/path?q=python#anchor")

print(url.scheme)    # 'https'
print(url.host)      # 'example.com'
print(url.port)      # 8080
print(url.path)      # '/path'
print(url.query)     # b'q=python'
print(url.join("/new-path")) # Trả về URL mới: https://user:pass@example.com:8080/new-path

```