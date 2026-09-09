So sánh trực diện giữa **`urllib.parse`** (thư viện chuẩn) và **`yarl`** (Yet Another URL Library) giúp bạn đưa ra lựa chọn tối ưu cho dự án thực tế.

---

### Bang so sánh tổng quan

| Tiêu chí | `urllib.parse` | `yarl` |
| --- | --- | --- |
| **Nguồn gốc** | Thư viện chuẩn (Standard Library) | Thư viện bên thứ 3 (phát triển bởi đội ngũ `aiohttp`) |
| **Kiểu thiết kế** | Functional (Thao tác qua hàm & chuỗi) | Object-Oriented (Đối tượng `URL` bất biến - Immutable) |
| **Xử lý Unicode / IRI** | Cần mã hóa/mã hóa lại thủ công | Tự động hóa chuẩn xác (IRI & Percent-encoding) |
| **Thao tác Query / Path** | Phức tạp, dễ sai sót khi ghép chuỗi | Ngắn gọn, hỗ trợ toán tử (`/`, `%`) |
| **Hiệu năng (Performance)** | Rất nhanh cho tác vụ tách chuỗi đơn giản | Tối ưu tốt (viết bằng Cython), xử lý URL phức tạp an toàn hơn |
| **Cài đặt** | Có sẵn, không tốn dung lượng | Cần `pip install yarl` |

---

### Những khác biệt then chốt trong code thực tế

#### 1. Cách khởi tạo và thao tác với Query Parameter

Khi cần thêm hoặc sửa đổi thông số tìm kiếm:

* **Với `urllib.parse`:** Bạn phải tách URL -> giải mã query -> cập nhật dict -> mã hóa lại -> dựng lại URL.

```python
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

url = "https://example.com/search?q=python"
parsed = urlparse(url)
query = parse_qs(parsed.query)
query['page'] = [2] # Cập nhật tham số

new_query = urlencode(query, doseq=True)
new_url = urlunparse(parsed._replace(query=new_query))
# https://example.com/search?q=python&page=2

```

* **Với `yarl`:** Thao tác trực tiếp bằng cú pháp phương thức chuỗi.

```python
from yarl import URL

url = URL("https://example.com/search?q=python")
new_url = url.with_query(q="python", page=2)
# URL('https://example.com/search?q=python&page=2')

```

#### 2. Thao tác ghép đường dẫn (Path Operations)

* **Với `urllib.parse`:** Ghép đường dẫn với `urljoin` dễ nhầm lẫn nếu thiếu hoặc thừa dấu slash `/`.

```python
from urllib.parse import urljoin

base = "https://api.example.com/v1/"
# Nếu base không có "/" ở cuối, urljoin sẽ ghi đè phần path cuối
print(urljoin(base, "users"))  # https://api.example.com/v1/users

```

* **Với `yarl`:** Sử dụng toán tử `/` cực kỳ trực quan như đường dẫn thư mục `pathlib`.

```python
from yarl import URL

base = URL("https://api.example.com/v1")
endpoint = base / "users" / "123"
# URL('https://api.example.com/v1/users/123')

```

#### 3. Xử lý Unicode & Chuyển đổi mã hóa an toàn

`yarl` phân biệt rõ ràng giữa dạng hiển thị cho con người đọc (human-readable) và dạng truyền tải trên mạng (encoded):

```python
from yarl import URL

url = URL("https://example.com/tìm-kiếm?q=lập trình")

# Dạng hiển thị sạch
print(url.human_repr()) 
# https://example.com/tìm-kiếm?q=lập trình

# Dạng mã hóa truyền qua HTTP request
print(str(url)) 
# https://example.com/t%C3%ACm-ki%E1%BA%BFm?q=l%E1%BA%ADp+tr%C3%ACnh

```

---

### Đánh giá: Thư viện nào tối ưu hơn cho dự án thực tế?

**`yarl` vượt trội hơn trong hầu hết các dự án thực tế.**

1. **Khi nào nên chọn `yarl`?**
* **Dự án Async / Web Scraping / API:** Dự án dùng `aiohttp`, `httpx` hoặc cào dữ liệu quy mô lớn. `yarl` là thư viện URL mặc định của hệ sinh thái `aiohttp`.
* **Hệ thống lớn xử lý URL phức tạp:** Cần sửa query, nối path, xử lý ngôn ngữ có dấu (Unicode) thường xuyên.
* **Ưu tiên độ an toàn và sạch sẽ của code:** Tránh các lỗi tiềm ẩn do quên `urlencode` hay sai dấu `/` khi ghép chuỗi.


2. **Khi nào nên dùng `urllib.parse`?**
* **Script nhẹ, Tool nhỏ:** Muốn viết file Python đơn lẻ (standalone script) không cần file `requirements.txt` hay cài môi trường ảo.
* **Môi trường hạn chế thư viện ngoài:** Server/Container nghiêm ngặt không cho phép cài gói PIP bên thứ 3.
* **Chỉ cần parse URL đơn giản:** Khi bạn chỉ cần lấy duy nhất tên miền (`hostname`) hoặc một tham số đơn lẻ từ URL.