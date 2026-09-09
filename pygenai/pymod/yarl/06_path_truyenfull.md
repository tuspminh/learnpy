Trong `yarl`, bạn có thể lấy về đường dẫn `/danh-sach/truyen-moi` (hoặc `/truyen-moi` tùy nhu cầu cắt chuỗi) và số trang `3` bằng cách kết hợp thuộc tính `.path` và `.parts` của đối tượng `URL`.

### Code thực hiện

```python
from yarl import URL

url_str = "Https://truyenfull.live/danh-sach/truyen-moi/trang-3/"
url = URL(url_str)

# 1. Lấy các phần tử của path (dạng tuple)
# url.parts sẽ là: ('/', 'danh-sach', 'truyen-moi', 'trang-3', '')
parts = [p for p in url.parts if p and p != '/'] 
# Kết quả parts: ['danh-sach', 'truyen-moi', 'trang-3']

# 2. Lấy đường dẫn base (/danh-sach/truyen-moi)
base_path = "/" + "/".join(parts[:-1])  # '/danh-sach/truyen-moi'

# Nếu chỉ muốn lấy riêng đoạn '/truyen-moi'
category_path = "/" + parts[1]         # '/truyen-moi'

# 3. Lấy số trang từ phần tử cuối ('trang-3')
page_segment = parts[-1]               # 'trang-3'
page_num = int(page_segment.split('-')[-1])  # 3

# In kết quả
print(f"Path cơ bản : {base_path}")
print(f"Đoạn mới    : /{parts[1]}")
print(f"Số trang    : {page_num}")

```

### Kết quả đầu ra

```text
Path cơ bản : /danh-sach/truyen-moi
Đoạn mới    : /truyen-moi
Số trang    : 3

```

---

### Giải thích chi tiết

1. **`url.parts`**: Tách đường dẫn thành từng phân đoạn. Do URL có dấu `/` ở cuối, ta lọc bỏ các phần tử rỗng `''` để thu được `['danh-sach', 'truyen-moi', 'trang-3']`.
2. **`parts[:-1]`**: Cắt bỏ phần tử cuối cùng (`'trang-3'`) để giữ lại các phần phía trước.
3. **`split('-')`**: Tách chuỗi `'trang-3'` theo dấu gạch ngang và lấy phần tử cuối cùng ép kiểu về `int` để thu được con số `3`.