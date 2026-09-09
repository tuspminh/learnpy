**`yarl`** (Yet Another URL Library) là một thư viện Python cực kỳ mạnh mẽ, được thiết kế chuyên biệt để **tạo, thao tác và phân tích URL** một cách chuẩn xác, an toàn và dễ dàng.

Nó được phát triển bởi cùng đội ngũ tạo ra `aiohttp` nhằm giải quyết các hạn chế của thư viện tiêu chuẩn `urllib.parse` (vốn hay gặp lỗi mã hóa/giải mã unicode và cú pháp cồng kềnh).

---

### 1. Cài đặt

```bash
pip install yarl

```

---

### 2. Các khái niệm nền tảng

Trong `yarl`, đối tượng trung tâm là lớp `URL`.

> **Quy tắc vàng của `yarl`:**
> Đối tượng `URL` là **Immutable** (Bất biến). Mọi phương thức làm thay đổi URL sẽ **không sửa trực tiếp** trên URL cũ mà sẽ **trả về một đối tượng `URL` mới**.

```python
from yarl import URL

# Khởi tạo URL
url = URL('https://user:password@api.example.com:8080/v1/users/profile?sort=asc&page=1#section-2')

```

---

### 3. Truy xuất các thành phần của URL (Parsing)

Khi truyền một chuỗi vào `URL()`, `yarl` tự động tách thành các thuộc tính vô cùng tiện lợi:

```python
from yarl import URL

url = URL('https://user:password@api.example.com:8080/v1/users/profile?sort=asc&page=1#section-2')

print(url.scheme)      # 'https'
print(url.user)        # 'user'
print(url.password)    # 'password'
print(url.host)        # 'api.example.com'
print(url.port)        # 8080
print(url.path)        # '/v1/users/profile'
print(url.query_string)# 'sort=asc&page=1'
print(url.fragment)    # 'section-2'

# Lấy query dưới dạng MultiDict (Cho phép 1 key có nhiều giá trị)
print(url.query)       # <MultiDictProxy('sort': 'asc', 'page': '1')>
print(url.query['sort']) # 'asc'

```

---

### 4. Thao tác xây dựng và biến đổi URL

Vì `URL` là bất biến, bạn sử dụng toán tử `/` hoặc các phương thức dạng `with_*` để tạo ra URL mới.

#### A. Ghép đường dẫn với toán tử `/` (Path Joining)

Không cần lo lắng về việc thừa hay thiếu dấu `/`, `yarl` tự động xử lý:

```python
base_url = URL('https://api.example.com/v1')

# Ghép đường dẫn
endpoint = base_url / 'users' / '123' / 'posts'
print(endpoint) 
# Output: https://api.example.com/v1/users/123/posts

```

#### B. Thay đổi Query Parameters (`with_query`, `update_query`)

* **`with_query()`**: Thay thế **toàn bộ** query parameters hiện tại bằng query mới.
* **`update_query()`**: **Cập nhật/Thêm mới** các tham số (giữ nguyên các tham số không bị đè).

```python
url = URL('https://example.com/search?q=python')

# 1. Thay thế hoàn toàn Query
new_url1 = url.with_query({'q': 'yarl', 'page': 2})
print(new_url1) # https://example.com/search?q=yarl&page=2

# 2. Cập nhật thêm Query vào URL hiện có
new_url2 = url.update_query({'page': 1, 'limit': 10})
print(new_url2) # https://example.com/search?q=python&page=1&limit=10

# 3. Xóa hoàn toàn Query (truyền None)
clean_url = url.with_query(None)
print(clean_url) # https://example.com/search

```

#### C. Thay đổi các thành phần khác (`with_*`)

```python
url = URL('http://example.com/path')

# Thay đổi scheme (http -> https)
url_ssl = url.with_scheme('https')

# Thay đổi host
url_new_host = url.with_host('api.org')

# Thay đổi port
url_port = url.with_port(8000)

# Thay đổi path
url_path = url.with_path('/new-path')

# Thay đổi fragment (#anchor)
url_frag = url.with_fragment('top')

print(url_ssl.with_port(8000)) # https://example.com:8000/path

```

---

### 5. Xử lý Unicode và Percent-Encoding (Điểm mạnh nhất)

`yarl` tự động encode/decode ký tự Unicode hoặc ký tự đặc biệt theo đúng tiêu chuẩn RFC 3986.

#### Tự động Encode khi khởi tạo:

```python
# Tên đường dẫn chứa tiếng Việt và khoảng trắng
url = URL('https://example.com/tìm kiếm/bài viết python')

print(str(url)) 
# Output: https://example.com/t%C3%ACm%20ki%E1%BA%BFm/b%C3%A0i%20vi%E1%BA%BFt%20python

# Lấy path dạng human-readable (đã decode):
print(url.path) 
# Output: /tìm kiếm/bài viết python

# Lấy path dạng raw (đã percent-encoded):
print(url.raw_path) 
# Output: /t%C3%ACm%20ki%E1%BA%BFm/b%C3%A0i%20vi%E1%BA%BFt%20python

```

#### Phân biệt `encoded=True` và `encoded=False`:

Nếu bạn truyền một chuỗi **đã được encode sẵn**, hãy dùng cờ `encoded=True` để tránh bị encode 2 lần:

```python
# Chuỗi đã encoded sẵn (%20)
url = URL('https://example.com/hello%20world', encoded=True)
print(url.path) # 'hello world'

# Nếu KHÔNG dùng encoded=True, dấu % sẽ bị encode thành %25:
url_wrong = URL('https://example.com/hello%20world')
print(str(url_wrong)) # https://example.com/hello%2520world

```

---

### 6. Xử lý Relative URL (Đường dẫn tương đối)

`yarl` giúp bạn dễ dàng chuyển đổi qua lại giữa URL tương đối và tuyệt đối thông qua `.origin()` và toán tử `%` / `.join()`:

```python
base = URL('https://example.com/blog/posts/')
relative_path = URL('../about')

# Ghép URL tương đối vào Base URL
absolute_url = base.join(relative_path)
print(absolute_url) # https://example.com/blog/about

# Kiểm tra xem URL có phải tương đối hay không
print(relative_path.is_absolute()) # False
print(absolute_url.is_absolute())  # True

# Lấy Origin (Scheme + Host + Port)
print(absolute_url.origin()) # https://example.com

```

---

### 7. So sánh `yarl` với `urllib.parse`

| Tính năng | `urllib.parse` (Standard Library) | `yarl` |
| --- | --- | --- |
| **Kiểu dữ liệu** | Trả về `ParseResult` (NamedTuple) / String | Đối tượng `URL` hướng đối tượng |
| **Tính bất biến** | Không hỗ trợ sửa đổi trực tiếp | Hỗ trợ chuỗi phương thức (`with_*`) |
| **Ghép đường dẫn** | `urljoin('[http://a.com/b](http://a.com/b)', 'c')` (dễ nhầm lẫn) | `base / 'c'` (rõ ràng, tự nhiên) |
| **Xử lý Unicode** | Phải gọi `quote()` / `unquote()` thủ công | Tự động hóa 100% chuẩn RFC |
| **Thao tác Query** | Phải dùng `parse_qs`, `urlencode` qua lại | Quản lý bằng `MultiDict` qua `.query` |

---

### 8. Ví dụ thực tế: Tích hợp với `requests` hoặc `httpx`

Mặc dù `yarl` là lõi của `aiohttp`, bạn hoàn toàn có thể dùng nó để xây dựng URL cho bất kỳ thư viện HTTP nào bằng cách ép kiểu sang `str`:

```python
import requests
from yarl import URL

# Dùng yarl xây dựng API endpoint an toàn
base_api = URL('https://api.github.com')
search_url = (base_api / 'search' / 'repositories').with_query({
    'q': 'language:python topic:asyncio',
    'sort': 'stars',
    'order': 'desc'
})

# Ép kiểu yarl URL thành string để gửi request
response = requests.get(str(search_url))
data = response.json()

print(f"URL đã gọi: {search_url}")
print(f"Tổng số repos tìm thấy: {data['total_count']}")

```