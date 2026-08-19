Lỗi mã hóa font chữ (hiển thị ký tự lạ như `Tiáº¿ng Viá»‡t` hoặc giật lỗi `UnicodeEncodeError`) khi làm việc với tiếng Việt trong Python thường đến từ **3 nguyên nhân chính**:

1. Tải HTML về bị sai Encoding (do thư viện `requests` tự đoán sai).
2. Lưu file ra máy không khai báo chuẩn `utf-8` (đặc biệt phổ biến trên Windows).
3. Màn hình Terminal/CMD không hỗ trợ hiển thị UTF-8.

Dưới đây là cách xử lý triệt để từng nguyên nhân.

---

## 1. Lỗi khi Lưu File (Phổ biến nhất trên Windows)

Mặc định trên Windows, hàm `open()` trong Python sẽ dùng bảng mã của hệ điều hành (thường là CP1252 hoặc ANSI) chứ không dùng `UTF-8`. Điều này khiến các ký tự có dấu tiếng Việt bị lỗi hoặc giật khung lỗi `UnicodeEncodeError`.

### ❌ Code lỗi:

```python
with open("output.md", "w") as f:  # Thiếu encoding!
    f.write(markdown_text)

```

### ✅ Cách khắc phục:

Luôn luôn khai báo tham số `encoding="utf-8"` khi mở file để ghi:

```python
with open("output.md", "w", encoding="utf-8") as f:
    f.write(markdown_text)

```

---

## 2. Lỗi khi Tải Dữ liệu Web (`requests`)

Thư viện `requests` đôi khi tự đoán sai bảng mã của trang web (thường đoán nhầm thành `ISO-8859-1`), dẫn đến chuỗi HTML truyền vào `html2text` đã bị lỗi font ngay từ đầu.

### ❌ Code lỗi:

```python
response = requests.get(url)
html_content = response.text  # Rất dễ bị sai mã hóa nếu server không trả header charset

```

### ✅ Cách khắc phục:

Ép `requests` sử dụng đúng mã hóa `utf-8` hoặc tự động phát hiện mã hóa (`apparent_encoding`) trước khi lấy dữ liệu:

```python
response = requests.get(url)

# CÁCH 1: Ép thẳng về UTF-8 (Khuyên dùng cho hầu hết web Việt Nam)
response.encoding = "utf-8"

# CÁCH 2: Cho requests tự đoán lại dựa trên nội dung thực tế
# response.encoding = response.apparent_encoding

html_content = response.text

```

---

## 3. Lỗi khi `print()` ra màn hình Terminal / CMD Windows

Đôi khi file `.md` lưu ra đã chuẩn UTF-8 rồi, nhưng khi bạn chạy `print(markdown_text)` ra màn hình Command Prompt / PowerShell thì bị lỗi hiển thị.

### ✅ Cách khắc phục:

Thêm 2 dòng lệnh này vào ngay đầu file script Python của bạn để ép `sys.stdout` xuất ra chuẩn UTF-8:

```python
import sys

# Ép Terminal xuất dữ liệu chuẩn UTF-8
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

```

---

## Code hoàn chỉnh chống lỗi mã hóa Tiếng Việt 100%

Dưới đây là đoạn code chuẩn kết hợp tất cả các giải pháp trên:

```python
import html2text
import requests
import sys

# 1. Khắc phục lỗi in ra Terminal (Windows)
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

url = "https://vi.wikipedia.org/wiki/Python_(ng%C3%B4n_ng%E1%BB%AF_l%E1%BA%ADp_tr%C3%ACnh)"

# 2. Khắc phục lỗi mã hóa khi tải Web
response = requests.get(url)
response.encoding = "utf-8"  # Đảm bảo mã hóa UTF-8 cho response

# 3. Chuyển đổi bằng html2text
h = html2text.HTML2Text()
h.body_width = 0
markdown_content = h.handle(response.text)

# 4. Khắc phục lỗi mã hóa khi lưu File
filename = "python_vi.md"
with open(filename, "w", encoding="utf-8") as f:
    f.write(markdown_content)

print(f"✅ Đã lưu thành công bài viết tiếng Việt vào file '{filename}'!")

```