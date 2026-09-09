Chào bạn, mình sẽ hướng dẫn bạn làm chủ thư viện **`urllib.parse`** trong Python một cách trực quan và dễ hiểu nhất.

`urllib.parse` là một thư viện chuẩn (standard library) tích hợp sẵn trong Python, dùng để phân tích (parse), tách nhỏ, ghép nối hoặc mã hóa các chuỗi URL.

---

### 1. Phân tích URL (`urlparse` và `urlsplit`)

Hàm `urlparse` giúp bạn bóc tách một URL thành các thành phần cơ bản.

```python
from urllib.parse import urlparse

url = "https://admin:password@example.com:8080/path/to/page;matrix?query=python&sort=asc#section-1"
parsed = urlparse(url)

print("Scheme (Giao thức):", parsed.scheme)        # https
print("Netloc (Tên miền + Port):", parsed.netloc)  # admin:password@example.com:8080
print("Path (Đường dẫn):", parsed.path)            # /path/to/page
print("Params (Tham số matrix):", parsed.params)   # matrix
print("Query (Truy vấn):", parsed.query)           # query=python&sort=asc
print("Fragment (Neo/Bookmark):", parsed.fragment) # section-1
print("Hostname:", parsed.hostname)                # example.com
print("Port:", parsed.port)                        # 8080

```

* **`urlsplit`**: Tương tự như `urlparse`, nhưng bỏ qua trường `params` (gộp chung vào `path`). Trong thực tế phát triển web hiện đại, `urlsplit` thường được dùng nhiều hơn vì chuẩn URL hiện nay ít dùng tham số matrix `;`.

---

### 2. Xử lý Chuỗi Query (`parse_qs` và `parse_qsl`)

Khi lấy được chuỗi query (ví dụ: `query=python&sort=asc`), bạn cần chuyển nó thành dữ liệu Python để làm việc.

```python
from urllib.parse import parse_qs, parse_qsl

query_str = "category=books&tag=python&tag=web&page=2"

# 1. parse_qs: Chuyển thành dictionary (Giá trị luôn là dạng list)
qs_dict = parse_qs(query_str)
print(qs_dict)
# Kết quả: {'category': ['books'], 'tag': ['python', 'web'], 'page': ['2']}

# 2. parse_qsl: Chuyển thành danh sách các tuple (Giữ nguyên thứ tự xuất hiện)
qs_list = parse_qsl(query_str)
print(qs_list)
# Kết quả: [('category', 'books'), ('tag', 'python'), ('tag', 'web'), ('page', '2')]

```

---

### 3. Ghép Nối URL (`urljoin` và `urlunparse`)

#### A. Ghép đường dẫn tương đối bằng `urljoin`

Rất hữu ích khi bạn làm bài toán cào dữ liệu web (web scraping).

```python
from urllib.parse import urljoin

base_url = "https://example.com/blog/article-1"

# Đường dẫn tương đối
print(urljoin(base_url, "image.png"))          # https://example.com/blog/image.png
print(urljoin(base_url, "/about"))            # https://example.com/about
print(urljoin(base_url, "https://other.com"))  # https://other.com

```

#### B. Dựng lại URL hoàn chỉnh bằng `urlunparse`

Chuyển một tuple/sequence các thành phần quay trở lại chuỗi URL.

```python
from urllib.parse import urlunparse

components = ('https', 'example.com', '/search', '', 'q=python', 'top')
full_url = urlunparse(components)
print(full_url)
# Kết quả: https://example.com/search?q=python#top

```

---

### 4. Mã hóa URL (`quote`, `unquote`, và `urlencode`)

URL chỉ chấp nhận các ký tự ASCII chuẩn. Khi URL chứa tiếng Việt, khoảng trắng hoặc ký tự đặc biệt, bạn phải mã hóa (Percent-encoding).

#### A. Mã hóa chuỗi đơn lẻ (`quote` & `unquote`)

```python
from urllib.parse import quote, unquote

text = "lập trình python"

# Mã hóa
encoded = quote(text)
print(encoded)  # l%E1%BA%ADp%20tr%C3%ACnh%20python

# Giải mã
decoded = unquote(encoded)
print(decoded)  # lập trình python

```

#### B. Mã hóa một Dictionary tham số (`urlencode`)

Hàm này được dùng cực kỳ phổ biến khi gửi request HTTP GET.

```python
from urllib.parse import urlencode

params = {
    "q": "lập trình python",
    "page": 1,
    "filters": ["free", "beginner"]
}

# doseq=True để xử lý các giá trị dạng list
query_string = urlencode(params, doseq=True)
print(query_string)
# Kết quả: q=l%E1%BA%ADp+tr%C3%ACnh+python&page=1&filters=free&filters=beginner

```

---

### Tóm tắt công dụng chính

| Hàm | Công dụng |
| --- | --- |
| `urlparse()` / `urlsplit()` | Tách URL ra từng phần nhỏ (scheme, host, path, query...) |
| `parse_qs()` / `parse_qsl()` | Chuyển chuỗi `a=1&b=2` thành Dictionary hoặc List of Tuples |
| `urljoin()` | Ghép đường dẫn gốc (Base URL) với đường dẫn tương đối |
| `urlencode()` | Chuyển Dictionary tham số thành chuỗi Query đúng chuẩn URL |
| `quote()` / `unquote()` | Mã hóa / Giải mã các ký tự đặc biệt/tiếng Việt trong URL |