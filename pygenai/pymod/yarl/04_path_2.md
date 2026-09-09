Trong `yarl`, vì đối tượng `URL` là **bất biến (immutable)**, mọi thao tác cắt, ghép hay thay thế trên path sẽ không chỉnh sửa trực tiếp URL cũ mà sẽ **trả về một đối tượng `URL` mới**.

Dưới đây là chi tiết các kỹ thuật cắt, ghép và thay thế thành phần path trong `yarl`:

---

### 1. Ghép thành phần Path (Path Appending / Joining)

#### A. Dùng toán tử `/` (Khuyên dùng)

Đây là cách tự nhiên nhất để nối thêm các phân đoạn (segments) vào cuối path. `yarl` tự động xử lý dấu `/` ở đầu và cuối chuỗi ghép.

```python
from yarl import URL

base_url = URL('https://api.example.com/v1')

# Nối thêm chuỗi đơn lẻ
url_1 = base_url / 'users' / '101'
print(url_1) 
# Output: https://api.example.com/v1/users/101

# Tự động loại bỏ dấu / thừa
url_2 = base_url / '/reports/' / '/monthly/'
print(url_2) 
# Output: https://api.example.com/v1/reports/monthly

```

#### B. Dùng phương thức `.join()` cho đường dẫn tương đối (Relative Path)

Dùng `.join()` khi bạn cần giải quyết đường dẫn chuyển hướng như `../` (đi ngược thư mục) hoặc `/` (nhảy về gốc domain):

```python
current_page = URL('https://example.com/blog/tech/posts/python-tips')

# Đi ngược lên 2 cấp thư mục
parent_dir = current_page.join(URL('../../news'))
print(parent_dir) 
# Output: https://example.com/blog/news

# Nhảy thẳng về gốc Domain
root_path = current_page.join(URL('/about'))
print(root_path) 
# Output: https://example.com/about

```

---

### 2. Cắt thành phần Path (Path Slicing / Truncating)

`yarl` hỗ trợ thuộc tính `.parts` trả về một `tuple` chứa toàn bộ các phân đoạn của path. Bạn có thể áp dụng kỹ thuật **Slice** (`[:]`) của Python trên `parts` để cắt path tùy ý.

```python
from yarl import URL

url = URL('https://example.com/v1/shop/categories/electronics/phones')

# Lấy tuple các phần tử path
print(url.parts) 
# Output: ('/', 'v1', 'shop', 'categories', 'electronics', 'phones')

# 1. Bỏ đi n phân đoạn cuối cùng (Ví dụ: bỏ 2 phân đoạn cuối)
# Dùng *url.parts[:-2] để unwrap danh sách parts đã cắt
cut_parts = url.parts[:-2]  # ('/', 'v1', 'shop', 'categories')
new_path = '/'.join(cut_parts).replace('//', '/') # Đảm bảo chuẩn hóa / ở gốc
new_url = url.with_path(new_path)

print(new_url) 
# Output: https://example.com/v1/shop/categories

# 2. Lấy parent URL (Tương tự như folder cha)
parent_url = url.with_path('/'.join(url.parts[:-1]))
print(parent_url) 
# Output: https://example.com/v1/shop/categories/electronics

```

---

### 3. Thay thế thành phần trong Path (Path Replacement)

#### A. Thay thế toàn bộ path bằng `.with_path()`

```python
url = URL('https://example.com/old/v1/data?key=123')

# Thay thế hoàn toàn path cũ (giữ nguyên domain và query)
updated = url.with_path('/new/v2/data')
print(updated) 
# Output: https://example.com/new/v2/data?key=123

```

#### B. Thay thế phân đoạn cụ thể trong path (Pattern Matching & Replace)

Nếu muốn tìm và thay thế một từ/phân đoạn cụ thể (ví dụ đổi `/v1/` thành `/v2/` hoặc đổi phiên bản ngôn ngữ):

```python
url = URL('https://example.com/en-us/docs/v1/installation')

# Cách 1: Thay thế chuỗi trực tiếp trên .path
new_path = url.path.replace('/en-us/', '/vi-vn/').replace('/v1/', '/v2/')
url_updated = url.with_path(new_path)

print(url_updated) 
# Output: https://example.com/vi-vn/docs/v2/installation

```

#### C. Thay thế Tên file, Tên gốc hoặc Extension (Đuôi file)

Khi path chỉ đến một tập tin, `yarl` cung cấp các phương thức chuyên dụng rất tiện lợi:

```python
file_url = URL('https://cdn.example.com/assets/images/user_avatar.jpg')

# 1. Thay đổi toàn bộ tên file ở cuối path (.with_name)
print(file_url.with_name('banner.png'))
# Output: https://cdn.example.com/assets/images/banner.png

# 2. Chỉ thay đổi tên file, GIỮ NGUYÊN extension .jpg (.with_stem)
print(file_url.with_stem('hero_image'))
# Output: https://cdn.example.com/assets/images/hero_image.jpg

# 3. Chỉ thay đổi extension, GIỮ NGUYÊN tên file (.with_suffix)
print(file_url.with_suffix('.webp'))
# Output: https://cdn.example.com/assets/images/user_avatar.webp

```

---

### Bảng tổng hợp nhanh các hàm thao tác Path

| Nhu cầu | Cú pháp / Phương thức | Kết quả mẫu |
| --- | --- | --- |
| **Nối thêm path** | `url / 'subpath'` | `/path` $\rightarrow$ `/path/subpath` |
| **Ghi đè path** | `url.with_path('/new')` | `/old` $\rightarrow$ `/new` |
| **Đổi tên file cuối** | `url.with_name('b.png')` | `/a.jpg` $\rightarrow$ `/b.png` |
| **Đổi tên file (giữ đuôi)** | `url.with_stem('new_name')` | `/old.jpg` $\rightarrow$ `/new_name.jpg` |
| **Đổi đuôi file** | `url.with_suffix('.pdf')` | `/doc.docx` $\rightarrow$ `/doc.pdf` |
| **Lấy danh sách đoạn** | `url.parts` | `('/', 'v1', 'users')` |