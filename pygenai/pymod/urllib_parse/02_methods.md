`urllib.parse` cung cấp các hàm và lớp phục vụ 5 nhóm tác vụ chính: **Phân tích (Parse)**, **Mã hóa/Giải mã (Quote/Unquote)**, **Ghép nối (Join/Build)**, **Xử lý Query**, và các **Lớp đại diện (Classes)**.

---

### 1. Danh sách các Lớp (Classes)

Các hàm phân tích URL trả về các đối tượng thuộc các lớp này dưới dạng `namedtuple`:

* **`ParseResult`**: Kết quả trả về từ `urlparse()`. Chứa 6 thuộc tính: `scheme`, `netloc`, `path`, `params`, `query`, `fragment`.
* **`SplitResult`**: Kết quả trả về từ `urlsplit()`. Chứa 5 thuộc tính: `scheme`, `netloc`, `path`, `query`, `fragment` (không có `params`).
* **`DefragResult`**: Kết quả trả về từ `urldefrag()`. Chứa 2 thuộc tính: `url`, `fragment`.

#### Các Property & Method chung của `ParseResult` và `SplitResult`:

| Property / Method | Loại | Mô tả |
| --- | --- | --- |
| **`.scheme`** | Property | Giao thức (ví dụ: `http`, `https`, `ftp`) |
| **`.netloc`** | Property | Tên miền kèm port & auth (ví dụ: `user:pass@example.com:8080`) |
| **`.path`** | Property | Đường dẫn tài nguyên (ví dụ: `/index.html`) |
| **`.params`** | Property | Tham số kiểu matrix (chỉ có trong `ParseResult`) |
| **`.query`** | Property | Chuỗi truy vấn (ví dụ: `q=python&page=1`) |
| **`.fragment`** | Property | Thẻ neo / Bookmark (ví dụ: `section-2`) |
| **`.username`** | Property | Tên đăng nhập (trích xuất từ `netloc`, trả về `None` nếu không có) |
| **`.password`** | Property | Mật khẩu (trích xuất từ `netloc`, trả về `None` nếu không có) |
| **`.hostname`** | Property | Tên miền viết thường (trích xuất từ `netloc`, loại bỏ port/user/pass) |
| **`.port`** | Property | Cổng kết nối dưới dạng số nguyên `int` (trả về `None` nếu không có) |
| **`._replace(**kwargs)`** | Method | Tạo một đối tượng mới với các thuộc tính được thay thế |
| **`.geturl()`** | Method | Dựng lại chuỗi URL hoàn chỉnh từ các thuộc tính hiện tại |

---

### 2. Các Hàm Phân Tích & Ghép Nối (Parsing & Joining)

* **`urlparse(urlstring, scheme='', allow_fragments=True)`**: Phân tích URL thành `ParseResult` (6 thành phần).
* **`urlsplit(urlstring, scheme='', allow_fragments=True)`**: Phân tích URL thành `SplitResult` (5 thành phần - bỏ qua `params`).
* **`urlunparse(components)`**: Ghép 1 tuple/iterable gồm 6 phần tử thành chuỗi URL.
* **`urlunsplit(components)`**: Ghép 1 tuple/iterable gồm 5 phần tử thành chuỗi URL.
* **`urljoin(base, url, allow_fragments=True)`**: Ghép nối đường dẫn gốc (`base`) với một đường dẫn tương đối (`url`).
* **`urldefrag(url)`**: Tách phần `fragment` ra khỏi URL, trả về `DefragResult(url, fragment)`.

---

### 3. Các Hàm Xử Lý Query String

* **`parse_qs(qs, keep_blank_values=False, strict_parsing=False, encoding='utf-8', errors='replace')`**: Chuyển chuỗi query `a=1&b=2` thành `dict` với giá trị là danh sách (`list`).
* **`parse_qsl(qs, keep_blank_values=False, strict_parsing=False, encoding='utf-8', errors='replace')`**: Chuyển chuỗi query thành danh sách các tuple dạng `[(key1, value1), (key2, value2)]`.
* **`urlencode(query, doseq=False, safe='', encoding=None, errors=None, quote_via=quote_plus)`**: Chuyển `dict` hoặc danh sách tuple thành chuỗi query string. Tham số `doseq=True` dùng khi giá trị trong dict là danh sách.

---

### 4. Các Hàm Mã Hóa & Giải Mã (Encoding / Decoding)

* **`quote(string, safe='/', encoding=None, errors=None)`**: Mã hóa ký tự đặc biệt/Unicode thành dạng Percent-encoding (`%XX`). Mặc định giữ nguyên dấu `/`.
* **`quote_plus(string, safe='', encoding=None, errors=None)`**: Tương tự `quote()`, nhưng thay thế khoảng trắng thành dấu `+` thay vì `%20` (chuẩn cho query string).
* **`quote_from_bytes(bytes, safe='/')`**: Mã hóa trực tiếp từ chuỗi bytes.
* **`unquote(string, encoding='utf-8', errors='replace')`**: Giải mã các ký tự `%XX` về dạng chuỗi văn bản ban đầu.
* **`unquote_plus(string, encoding='utf-8', errors='replace')`**: Giải mã chuỗi Percent-encoded, biến dấu `+` quay lại thành khoảng trắng.
* **`unquote_to_bytes(string)`**: Giải mã chuỗi về dạng `bytes`.

---

### 5. Ví dụ mã nguồn minh họa tổng hợp

```python
from urllib.parse import (
    urlparse, urlunparse, urljoin, urldefrag,
    parse_qs, urlencode, quote, unquote
)

# 1. Parse & Truy cập Property / Method
url = "https://user:pass@example.com:8080/path/file.py;matrix?q=python#top"
p = urlparse(url)

print(p.hostname)   # 'example.com'
print(p.port)       # 8080
print(p.username)   # 'user'

# Thay đổi path bằng ._replace và tái tạo bằng .geturl()
new_p = p._replace(path="/new/path.py")
print(new_p.geturl()) 
# 'https://user:pass@example.com:8080/new/path.py;matrix?q=python#top'

# 2. Urldefrag
clean_url, fragment = urldefrag("https://example.com/index.html#section1")
print(clean_url) # 'https://example.com/index.html'

# 3. Query string & Encode/Decode
data = {'search': 'lập trình', 'tags': ['python', 'web']}
query_str = urlencode(data, doseq=True)
print(query_str) # 'search=l%E1%BA%ADp+tr%C3%ACnh&tags=python&tags=web'

parsed_query = parse_qs(query_str)
print(parsed_query) # {'search': ['lập trình'], 'tags': ['python', 'web']}

```