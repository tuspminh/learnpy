Dưới đây là bảng tổng hợp toàn bộ các **Class**, **Property** (Thuộc tính) và **Method** (Phương thức) chính của thư viện `yarl`.

---

### 1. Danh sách các Class chính

| Class | Mô tả |
| --- | --- |
| `yarl.URL` | Class trung tâm đại diện cho một URL (Bất biến - Immutable). |
| `multidict.MultiDictProxy` | Class được `yarl` dùng cho thuộc tính `.query` để quản lý danh sách Key-Value (cho phép trùng lặp Key). |
| `yarl.URLCache` | Class quản lý cơ chế cache nội bộ của `yarl` giúp tăng hiệu năng xử lý chuỗi URL. |

---

### 2. Tổng hợp các Property của `yarl.URL`

Các thuộc tính giúp bạn truy xuất từng phần cấu trúc của URL mà **không làm thay đổi URL**.

#### A. Thuộc tính cấu trúc cơ bản (Parsed Parts)

| Property | Kiểu dữ liệu | Mô tả | Ví dụ (`[https://user:pass@example.com:8080/a/b?q=1#sec](https://user:pass@example.com:8080/a/b?q=1#sec)`) |
| --- | --- | --- | --- |
| `.scheme` | `str` | Giao thức (Protocol) | `'https'` |
| `.user` | `str | None` | Username trong URL authentication | `'user'` |
| `.password` | `str | None` | Password trong URL authentication | `'pass'` |
| `.host` | `str | None` | Tên miền hoặc IP (Chữ thường) | `'example.com'` |
| `.port` | `int | None` | Cổng kết nối | `8080` |
| `.explicit_port` | `int | None` | Cổng nếu được ghi rõ trên URL (trả về `None` nếu dùng port mặc định của scheme) | `8080` |
| `.path` | `str` | Đường dẫn (Đã decode Unicode) | `'/a/b'` |
| `.query_string` | `str` | Chuỗi query thô đằng sau dấu `?` | `'q=1'` |
| `.query` | `MultiDictProxy` | Dictionary chứa các query parameters | `<MultiDictProxy('q': '1')>` |
| `.fragment` | `str` | Anchor đằng sau dấu `#` | `'sec'` |

#### B. Thuộc tính dạng mã hóa thô (Raw / Percent-Encoded)

Dùng khi bạn muốn lấy dữ liệu ở dạng chưa decode (còn nguyên các ký tự `%20`, `%C3%AC`...):

| Property | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `.raw_user` | `str | None` | Username ở dạng Percent-Encoded |
| `.raw_password` | `str | None` | Password ở dạng Percent-Encoded |
| `.raw_host` | `str | None` | Host ở dạng Percent-Encoded (IDNA mã hóa tên miền) |
| `.raw_path` | `str` | Path ở dạng Percent-Encoded |
| `.raw_query_string` | `str` | Query string ở dạng Percent-Encoded |
| `.raw_fragment` | `str` | Fragment ở dạng Percent-Encoded |
| `.raw_parts` | `tuple[str]` | Tuple chứa các thành phần path chưa decode |
| `.raw_name` | `str` | Tên file/folder cuối cùng ở dạng mã hóa thô |

#### C. Thuộc tính kiểm tra & Phân tích thêm

| Property | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `.parts` | `tuple[str]` | Các phân đoạn cấu thành `.path` (VD: `('/', 'a', 'b')`) |
| `.name` | `str` | Phần tử cuối cùng của path (tương đương tên file/folder) |
| `.stem` | `str` | Tên file bỏ đuôi extension (VD: `/doc/file.txt` -> `'file'`) |
| `.suffix` | `str` | Đuôi mở rộng của file (VD: `/doc/file.txt` -> `'.txt'`) |
| `.suffixes` | `tuple[str]` | Danh sách tất cả các đuôi (VD: `/archive.tar.gz` -> `('.tar', '.gz')`) |
| `.authority` | `str` | Chuỗi `user:pass@host:port` |
| `.raw_authority` | `str` | Chuỗi Authority ở dạng mã hóa thô |

---

### 3. Tổng hợp các Method của `yarl.URL`

Do đối tượng `URL` là **Immutable**, tất cả các phương thức tạo mới hoặc biến đổi dưới đây đều **trả về một đối tượng `URL` mới**.

#### A. Các toán tử (Operators)

| Toán tử / Method | Mô tả | Ví dụ |
| --- | --- | --- |
| `url / 'path'` | Ghép nối thêm phân đoạn path | `URL('[http://a.com](http://a.com)') / 'v1' / 'users'` |
| `url % kwargs` | Viết tắt của `update_query()` | `URL('[http://a.com](http://a.com)') % {'page': 1}` |
| `str(url)` | Chuyển URL thành chuỗi hoàn chỉnh | `str(url)` |
| `url1 == url2` | So sánh 2 URL có tương đương nhau hay không | `URL('[http://a.com](http://a.com)') == URL('[http://a.com/](http://a.com/)')` |

#### B. Phương thức biến đổi URL (`with_*`)

Dùng để thay thế một thành phần cụ thể trong URL:

| Method | Tham số nhận vào | Mục đích |
| --- | --- | --- |
| `.with_scheme(scheme)` | `str` | Thay đổi scheme (VD: `'https'`) |
| `.with_user(user)` | `str | None` | Thay đổi username |
| `.with_password(password)` | `str | None` | Thay đổi password |
| `.with_host(host)` | `str` | Thay đổi hostname |
| `.with_port(port)` | `int | None` | Thay đổi port |
| `.with_path(path)` | `str` | Thay thế hoàn toàn path cũ |
| `.with_query(*args, **kwargs)` | `dict`, `list[tuple]`, `None` | **Thay thế hoàn toàn** query params cũ |
| `.with_fragment(fragment)` | `str | None` | Thay đổi fragment (`#anchor`) |
| `.with_name(name)` | `str` | Thay đổi phần tên file/folder cuối cùng |
| `.with_stem(stem)` | `str` | Thay đổi tên file nhưng giữ nguyên `.suffix` |
| `.with_suffix(suffix)` | `str` | Thay đổi extension file |

#### C. Phương thức cập nhật & Ghép nối (Modification & Joining)

| Method | Tham số | Mục đích |
| --- | --- | --- |
| `.update_query(*args, **kwargs)` | `dict`, `list[tuple]` | **Thêm mới hoặc ghi đè** query params (giữ nguyên tham số cũ không trùng) |
| `.join(target)` | `URL | str` | Ghép URL tương đối vào Base URL (chuẩn RFC 3986) |
| `.origin()` | *Không có* | Trả về URL chỉ gồm `scheme://host:port` |
| `.relative()` | *Không có* | Trả về URL tương đối bỏ đi part `scheme://host:port` |
| `.human_repr()` | *Không có* | Trả về dạng chuỗi dễ đọc cho con người (đã decode Unicode) |

#### D. Phương thức kiểm tra (Validation & Checks)

| Method | Trả về | Mục đích |
| --- | --- | --- |
| `.is_absolute()` | `bool` | Trả về `True` nếu URL có bao gồm `scheme` |
| `.is_default_port()` | `bool` | Trả về `True` nếu port đang dùng là port mặc định (HTTP: 80, HTTPS: 443) |

---

### 4. Bảng tóm tắt ví dụ thao tác nhanh

```python
from yarl import URL

url = URL('https://example.com/api/v1/data?status=active#top')

# 1. TRUY XUẤT (Property)
assert url.scheme == 'https'
assert url.host == 'example.com'
assert url.path == '/api/v1/data'
assert url.query['status'] == 'active'

# 2. THAY ĐỔI / CẬP NHẬT (Method)
updated_url = (
    url.with_scheme('http')                      # Đổi sang http
       .update_query({'page': 2, 'limit': 10})    # Thêm query params
       .with_fragment(None)                       # Xóa fragment
)
# Output: http://example.com/api/v1/data?status=active&page=2&limit=10

# 3. GHÉP PATH (Operator & Method)
new_endpoint = url.origin() / 'v2' / 'users'
# Output: https://example.com/v2/users

```