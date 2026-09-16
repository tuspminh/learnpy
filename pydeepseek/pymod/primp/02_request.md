Chi tiết về khả năng yêu cầu của thư viện primp, cốt lõi nằm ở hai lớp: **cấu hình tham số mặc định của lớp `Client`** và **các tham số truyền vào của từng yêu cầu riêng lẻ**. Chúng lần lượt giải quyết vấn đề "cấu hình chung của phiên làm việc" và "cấu hình riêng của yêu cầu đơn lẻ".

### 1. Cấu hình mặc định của Client (áp dụng toàn cục)

Khi tạo `primp.Client`, các tham số được truyền vào sẽ trở thành mặc định cho tất cả các yêu cầu tiếp theo, có thể được ghi đè riêng khi thực hiện yêu cầu cụ thể.

| Tham số | Kiểu | Mặc định | Mô tả |
| :--- | :--- | :--- | :--- |
| `auth` | `tuple` | `None` | Thông tin xác thực cơ bản `(tên người dùng, mật khẩu)` |
| `auth_bearer` | `str` | `None` | Token xác thực Bearer |
| `params` | `dict` | `None` | Tham số truy vấn mặc định |
| `headers` | `dict` | `None` | Header mặc định. **Lưu ý**: Nếu đã đặt `impersonate`, `headers` sẽ bị bỏ qua |
| `cookies` | `dict` | `None` | Cookie mặc định |
| `timeout` | `float` | `30` | Thời gian chờ yêu cầu (giây) |
| `cookie_store` | `bool` | `True` | Bật lưu trữ cookie liên tục, cookie nhận được sẽ tự động mang theo trong các yêu cầu tiếp theo |
| `referer` | `bool` | `True` | Tự động đặt header `Referer` |
| `proxy` | `str` | `None` | Địa chỉ proxy, hỗ trợ http/https/socks5 |
| `impersonate` | `str` | `None` | **Chức năng cốt lõi**: Mô phỏng đối tượng trình duyệt, ví dụ `"chrome_127"`, `"safari_17.5"` |
| `follow_redirects` | `bool` | `True` | Có theo dõi chuyển hướng không |
| `max_redirects` | `int` | `20` | Số lần chuyển hướng tối đa |
| `verify` | `bool` | `True` | Xác minh chứng chỉ SSL |
| `http1` / `http2` | `bool` | `None` | Cưỡng bức chỉ sử dụng HTTP/1.1 hoặc HTTP/2 |

### 2. Tham số thời gian gọi phương thức yêu cầu

Các phương thức như `get`, `post` có thể truyền tham số riêng để tạm thời ghi đè cấu hình Client, **phạm vi chỉ giới hạn trong yêu cầu đó**.

**Phương thức GET** (`get`, `head`, `options`, `delete`):

| Tham số | Kiểu | Mô tả |
| :--- | :--- | :--- |
| `url` | `str` | Địa chỉ yêu cầu |
| `params` | `dict` | Tham số truy vấn, sẽ được nối vào URL |
| `headers` | `dict` | Header yêu cầu tạm thời |
| `cookies` | `dict` | Cookie yêu cầu tạm thời |
| `auth` / `auth_bearer` | `tuple` / `str` | Xác thực tạm thời |
| `timeout` | `float` | Thời gian chờ tạm thời |

**Phương thức POST** (`post`, `put`, `patch`):

Ngoài tất cả tham số của GET ở trên, còn thêm phần body dữ liệu đặc trưng:

| Tham số | Kiểu | Mô tả |
| :--- | :--- | :--- |
| `content` | `bytes` | Dữ liệu body nhị phân thô |
| `data` | `dict` | Dữ liệu form (`application/x-www-form-urlencoded`) |
| `json` | `Any` | Đối tượng JSON, thư viện sẽ tự động serialize |
| `files` | `dict` | Tải tệp lên (`multipart/form-data`) |

### 3. Đối tượng Response

Các thuộc tính chính của đối tượng phản hồi do yêu cầu trả về:

```python
response.status_code   # Mã trạng thái HTTP
response.text          # Nội dung phản hồi dạng văn bản
response.json()        # Parse thành dict
response.headers       # Header phản hồi
response.cookies       # Cookie phản hồi
response.content       # Dữ liệu nhị phân
response.url           # URL cuối cùng sau chuyển hướng
response.text_plain    # Trích xuất văn bản thuần từ HTML (tính năng đặc biệt)
response.text_markdown # Trích xuất Markdown từ HTML (tính năng đặc biệt)
```

### 4. Ví dụ thực tế

```python
import primp

# 1. Tạo Client mô phỏng trình duyệt (cấu hình toàn cục)
client = primp.Client(
    impersonate="chrome_127",
    timeout=15,
    cookie_store=True
)

# 2. Yêu cầu GET (ghi đè timeout tạm thời)
resp = client.get(
    "https://httpbin.org/anything",
    params={"page": "1", "size": "10"},
    timeout=5  # Yêu cầu này chỉ chờ 5 giây
)
print(resp.json()["args"])  # Xem tham số truy vấn

# 3. Yêu cầu POST JSON
resp = client.post(
    "https://httpbin.org/anything",
    json={"username": "test", "action": "login"},
    headers={"X-Custom": "header-value"}
)
print(resp.json()["json"])

# 4. Tải tệp lên
resp = client.post(
    "https://httpbin.org/post",
    files={"document": open("report.pdf", "rb").read()}
)
print(resp.json()["files"])
```

**Tóm tắt một câu**: Tham số của `Client` quản lý "mặc định cả phiên làm việc như thế nào", tham số của phương thức yêu cầu quản lý "yêu cầu cụ thể này gửi như thế nào". Khi `impersonate` được kích hoạt, cấu hình `headers` thủ công sẽ mất hiệu lực, ưu tiên sử dụng header trình duyệt được tạo tự động.