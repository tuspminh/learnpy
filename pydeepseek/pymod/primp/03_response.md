Đối tượng `Response` trong primp là kết quả trả về sau khi gửi yêu cầu HTTP, chứa tất cả dữ liệu phản hồi từ máy chủ. Các thuộc tính và phương thức của nó được thiết kế tương tự như thư viện `requests`, nhưng bổ sung thêm một số tính năng độc đáo.

### 📋 Thuộc tính phản hồi

| Thuộc tính | Kiểu | Mô tả |
| :--- | :--- | :--- |
| `status_code` | `int` | Mã trạng thái HTTP (như 200, 404)  |
| `headers` | `dict` | Header HTTP do máy chủ trả về  |
| `cookies` | `dict` | Cookie được trích xuất từ header `Set-Cookie`  |
| `content` | `bytes` | Nội dung phản hồi thô dạng byte. Lần truy cập đầu tiên sẽ đọc và lưu vào bộ nhớ đệm toàn bộ nội dung, các lần sau trả về giá trị đã lưu  |
| `text` | `str` | Giải mã nội dung phản hồi thành chuỗi (tự động phát hiện mã hóa)  |
| `encoding` | `str` | Mã hóa ký tự của phản hồi  |
| `url` | `str` | URL cuối cùng của phản hồi (sau khi chuyển hướng)  |

### ✨ Chuyển đổi văn bản HTML

Đây là tính năng độc đáo của primp, có thể trực tiếp chuyển đổi nội dung HTML thành các định dạng văn bản khác nhau :

| Thuộc tính | Mô tả |
| :--- | :--- |
| `text_plain` | Trích xuất văn bản thuần từ HTML (không định dạng)  |
| `text_markdown` | Chuyển đổi HTML sang định dạng Markdown  |
| `text_rich` | Chuyển đổi HTML sang văn bản định dạng (có định dạng)  |

### 🛠️ Phương thức

**`json()`**：Phân tích nội dung phản hồi thành đối tượng Python (dict/list). Sử dụng `serde_json` để phân tích, sau đó chuyển đổi thành kiểu Python .

```python
response = client.get("https://api.example.com/data")
data = response.json()  # Chuyển đổi phản hồi JSON thành dict/list Python
```

**`stream()`**：Trả về một iterator, trả về nội dung phản hồi từng phần khi nhận được, phù hợp để xử lý các phản hồi lớn mà không cần tải toàn bộ vào bộ nhớ cùng một lúc .

```python
response = client.get("https://example.com/large-file")
for chunk in response.stream():
    process_chunk(chunk)  # Xử lý từng khối byte
```

### 💡 Ví dụ sử dụng

```python
import primp

client = primp.Client(impersonate="chrome_131")
response = client.get("https://example.com")

# Truy cập các thuộc tính cơ bản
print(f"Mã trạng thái: {response.status_code}")
print(f"URL: {response.url}")
print(f"Header: {response.headers}")
print(f"Cookie: {response.cookies}")
print(f"Độ dài nội dung: {len(response.content)} byte")

# Truy cập các định dạng văn bản khác nhau
print(response.text[:100])         # 100 ký tự đầu tiên của văn bản thuần
print(response.text_plain[:100])   # 100 ký tự đầu tiên của văn bản trích xuất từ HTML
print(response.text_markdown[:100]) # 100 ký tự đầu tiên của định dạng Markdown

# Phân tích phản hồi JSON
data = response.json()
```

Đối tượng Response được triển khai bằng Rust và cung cấp cho Python thông qua ràng buộc PyO3 . Nếu bạn muốn biết thêm về các tình huống sử dụng cụ thể của một thuộc tính hoặc phương thức nào đó, hãy cho tôi biết.