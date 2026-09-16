**Primp** là một HTTP client hiệu năng cao dành cho Python, điểm mạnh cốt lõi nằm ở khả năng **mô phỏng dấu vết trình duyệt** (bao gồm TLS/JA3/JA4 fingerprint, HTTP/2 fingerprint và thứ tự header). Nói một cách đơn giản, nó giúp chương trình Python của bạn trông giống như một trình duyệt thực thụ (như Chrome, Firefox) đang truy cập trang web, từ đó vượt qua một số cơ chế phát hiện bot ở tầng kết nối.

### 1. Cài đặt và Xác minh

Primp không phụ thuộc vào thư viện Python bên thứ ba nào, việc cài đặt rất đơn giản:

```bash
pip install -U primp
```

Sau khi cài đặt, bạn có thể chạy lệnh sau để xác minh:

```python
import primp
print(primp.__version__)  # In ra số phiên bản đã cài đặt
```

### 2. Bắt đầu nhanh: Cách sử dụng API cơ bản

Cách sử dụng của Primp rất giống với `requests`, nếu bạn đã quen với requests thì gần như không có chi phí chuyển đổi nào.

**Cách một: Sử dụng hàm tiện ích (đơn giản nhất)**

```python
import primp

# Gửi yêu cầu GET trực tiếp, mô phỏng Chrome 146 mặc định
response = primp.get("https://tls.peet.ws/api/all")

print(response.status_code)  # Mã trạng thái
print(response.text)         # Nội dung phản hồi văn bản
print(response.json())       # Nếu là JSON, có thể trực tiếp lấy dict
```

**Cách hai: Tạo đối tượng Client (khuyến nghị cho nhiều yêu cầu)**

```python
import primp

# Tạo một instance Client có khả năng mô phỏng
client = primp.Client(impersonate="chrome_146")

# Thực hiện yêu cầu
resp = client.get("https://tls.peet.ws/api/all")
print(resp.text)
```

### 3. Chức năng cốt lõi: Mô phỏng trình duyệt

Đây là lý do chính khiến bạn sử dụng primp. Bạn có thể chỉ định trình duyệt và hệ điều hành cần mô phỏng trong quá trình khởi tạo Client hoặc khi gọi hàm.

```python
import primp

# Mô phỏng Chrome 146 trên Windows
client = primp.Client(impersonate="chrome_146", impersonate_os="windows")

# Mô phỏng ngẫu nhiên
client_random = primp.Client(impersonate="random", impersonate_os="random")
```

Các cấu hình mô phỏng trình duyệt và hệ điều hành hiện được hỗ trợ:

**Trình duyệt**: chrome, safari, edge, firefox, opera, random
**Hệ điều hành**: android, ios, linux, macos, windows, random

### 4. Các thao tác yêu cầu thường gặp

**GET với tham số**

```python
params = {"key1": "value1", "key2": "value2"}
response = client.get("https://httpbin.org/anything", params=params)
```

**POST với JSON**

```python
json_data = {"name": "test", "value": 123}
response = client.post("https://httpbin.org/anything", json=json_data)
```

**POST với dữ liệu form**

```python
form_data = {"field1": "value1"}
response = client.post("https://httpbin.org/anything", data=form_data)
```

**Tải tệp lên**

```python
files = {"file": open("example.txt", "rb")}
response = client.post("https://httpbin.org/post", files=files)
```

### 5. Xác thực

Primp hỗ trợ xác thực cơ bản (Basic) và xác thực token Bearer.

```python
# Xác thực cơ bản
client = primp.Client(auth=("username", "password"))

# Xác thực Bearer
client = primp.Client(auth_bearer="your_token_here")

# Cũng có thể truyền vào phương thức yêu cầu
response = client.get("https://httpbin.org/anything", auth=("user", "pass"))
```

### 6. Quản lý Cookie và Cấu hình Proxy

**Cookie**: Primp có lưu trữ cookie liên tục, khi `cookie_store` được bật (mặc định là True), cookie nhận được sẽ tự động được mang theo trong các yêu cầu tiếp theo.

```python
# Đặt cookie thủ công
client = primp.Client(cookies={"session_id": "abc123"})

# Lấy cookie của một tên miền nào đó
cookies = client.get_cookies("https://example.com")
```

**Proxy**: Hỗ trợ proxy HTTP, HTTPS và SOCKS5.

```python
client = primp.Client(proxy="http://127.0.0.1:8080")
# hoặc sử dụng SOCKS5
client = primp.Client(proxy="socks5://127.0.0.1:9150")
```

### 7. Xử lý ngoại lệ

Cấu trúc ngoại lệ của Primp tham khảo thiết kế của requests, nếu bạn quen với `requests.exceptions` thì sẽ cảm thấy rất thân thuộc.

```python
import primp

try:
    response = primp.get("https://httpbin.org/status/404")
    response.raise_for_status()
except primp.HTTPError as e:
    print(f"Lỗi HTTP: {e}")
except primp.ConnectionError as e:
    print(f"Lỗi kết nối: {e}")
except primp.Timeout as e:
    print(f"Yêu cầu hết thời gian: {e}")
```

Các ngoại lệ thường gặp bao gồm: `HTTPError`, `ConnectionError`, `ConnectTimeout`, `SSLError`, `ProxyError`, `ReadTimeout`, `TooManyRedirects`, v.v.

### 8. Cách sử dụng nâng cao: Chuyển đổi HTML và phiên bản bất đồng bộ

**Chuyển đổi văn bản HTML**: Primp có thể trực tiếp chuyển đổi phản hồi HTML thành văn bản thuần, Markdown hoặc văn bản định dạng, rất tiện lợi khi thu thập nội dung trang web.

```python
response = client.get("https://example.com/article")

# Trích xuất văn bản thuần
print(response.text_plain)

# Trích xuất định dạng Markdown
print(response.text_markdown)
```

**Phiên bản bất đồng bộ (AsyncClient)**: Phù hợp với các tác vụ có mức độ đồng thời cao, có thể cải thiện đáng kể hiệu quả thu thập dữ liệu.

```python
import asyncio
import primp

async def main():
    async with primp.AsyncClient(impersonate="chrome_146") as client:
        resp = await client.get("https://tls.peet.ws/api/all")
        print(resp.text)

asyncio.run(main())
```

---

**Tóm tắt**: Giá trị cốt lõi của Primp nằm ở "mô phỏng trình duyệt". Khi đối mặt với các trang web có phát hiện bot mạnh, việc sử dụng requests thông thường có thể bị chặn ở tầng TLS fingerprint, trong khi primp có thể giải quyết vấn đề này ở mức chi phí rất thấp, và API gần như không có chi phí học tập, đồng thời hiệu năng cao hơn đáng kể so với requests nhờ triển khai bằng Rust.