Thao tác với đường dẫn (**Path**) là một trong những thế mạnh lớn nhất của `yarl.URL`. Thư viện này thiết kế các thuộc tính và phương thức xử lý path mô phỏng rất giống với thư viện chuẩn **`pathlib`** của Python, giúp trải nghiệm viết code cực kỳ tự nhiên.

---

### 1. Ghép đường dẫn (Path Joining)

Thay vì dùng cộng chuỗi hay `os.path.join`, bạn sử dụng toán tử **`/`**. `yarl` sẽ tự động xử lý các dấu `/` thừa hoặc thiếu.

```python
from yarl import URL

base = URL('https://api.example.com/v1')

# Ghép nối từng đoạn path
endpoint = base / 'users' / '123' / 'profile'
print(endpoint) 
# Output: https://api.example.com/v1/users/123/profile

# Tự động loại bỏ dấu / thừa ở đầu hoặc cuối chuỗi ghép
clean_url = base / '/orders/' / '/details'
print(clean_url) 
# Output: https://api.example.com/v1/orders/details

```

---

### 2. Truy xuất thông tin Path (Path Properties)

Giả sử bạn có URL hướng tới một file: `[https://example.com/static/docs/report.pdf](https://example.com/static/docs/report.pdf)`

```python
from yarl import URL

url = URL('https://example.com/static/docs/report.tar.gz')

# 1. Lấy toàn bộ path
print(url.path)        # '/static/docs/report.tar.gz'

# 2. Phân tách path thành các đoạn (Tuple)
print(url.parts)       # ('/', 'static', 'docs', 'report.tar.gz')

# 3. Lấy tên file / thư mục cuối cùng (name)
print(url.name)        # 'report.tar.gz'

# 4. Lấy tên bỏ đi đuôi mở rộng (stem)
print(url.stem)        # 'report.tar'

# 5. Lấy đuôi mở rộng cuối cùng (suffix)
print(url.suffix)      # '.gz'

# 6. Lấy tất cả các đuôi mở rộng (suffixes)
print(url.suffixes)    # ('.tar', '.gz')

```

---

### 3. Sửa đổi Path (Path Modification)

Do đối tượng `URL` là **Immutable**, các phương thức thay đổi path sẽ trả về đối tượng `URL` mới.

#### A. Thay thế toàn bộ path (`with_path`)

```python
url = URL('https://example.com/old/path?v=1')

# Ghi đè path mới (giữ nguyên domain và query)
new_url = url.with_path('/new/endpoint')
print(new_url) 
# Output: https://example.com/new/endpoint?v=1

```

#### B. Đổi tên file hoặc đuôi mở rộng (`with_name`, `with_stem`, `with_suffix`)

Rất hữu ích khi bạn cần thay đổi định dạng file tải về từ API (ví dụ: đổi từ `.jpg` sang `.png` hoặc `.json` sang `.csv`):

```python
url = URL('https://cdn.example.com/images/avatar.jpg')

# 1. Đổi toàn bộ tên file (bao gồm cả đuôi)
print(url.with_name('cover.png'))
# Output: https://cdn.example.com/images/cover.png

# 2. Chỉ đổi tên file (giữ nguyên đuôi .jpg)
print(url.with_stem('hero_banner'))
# Output: https://cdn.example.com/images/hero_banner.jpg

# 3. Chỉ đổi đuôi mở rộng (giữ nguyên tên file)
print(url.with_suffix('.webp'))
# Output: https://cdn.example.com/images/avatar.webp

```

---

### 4. Xử lý Đường dẫn tương đối (Relative Path & Resolution)

Khi cào dữ liệu (web scraping), bạn thường bắt gặp các đường dẫn tương đối như `../about` hoặc `/blog`. Phương thức `.join()` giúp bạn resolve chúng thành URL tuyệt đối.

```python
base_page = URL('https://example.com/products/category/item_10')

# 1. Đi ngược lên 1 cấp thư mục (..)
relative_1 = URL('../item_11')
print(base_page.join(relative_1))
# Output: https://example.com/products/item_11

# 2. Nhảy về gốc domain (bắt đầu bằng /)
relative_2 = URL('/cart')
print(base_page.join(relative_2))
# Output: https://example.com/cart

# 3. Bỏ toàn bộ host, chỉ lấy phần path tương đối
abs_url = URL('https://example.com/api/v1/users')
print(abs_url.relative())
# Output: /api/v1/users

```

---

### 5. Xử lý Unicode và Ký tự đặc biệt trong Path

`yarl` tự động **Percent-Encode** các ký tự tiếng Việt, khoảng trắng, hoặc ký tự đặc biệt khi chuyển thành chuỗi, nhưng vẫn cho phép bạn đọc dạng văn bản rõ ràng qua thuộc tính `.path`:

```python
# Tạo URL có dấu tiếng Việt và khoảng trắng
url = URL('https://shop.vn/danh mục/điện thoại & máy tính')

# Dạng hiển thị chuẩn cho cỗ máy / HTTP request (Percent-encoded)
print(str(url))
# Output: https://shop.vn/danh%20m%E1%BB%A5c/%C4%91i%E1%BB%87n%20tho%E1%BA%A1i%20%26%20m%C3%A1y%20t%C3%ADnh

# Dạng đọc được cho con người (Decoded path)
print(url.path)
# Output: /danh mục/điện thoại & máy tính

# Dạng thô mã hóa từng phần
print(url.raw_path)
# Output: /danh%20m%E1%BB%A5c/%C4%91i%E1%BB%87n%20tho%E1%BA%A1i%20%26%20m%C3%A1y%20t%C3%ADnh

```