Dưới đây là hai giải pháp hoàn chỉnh cho bài toán của bạn bằng `yarl`:

1. **Hàm tự động bóc tách** đường dẫn và số trang từ một URL bất kỳ.
2. **Hàm xây dựng/thay đổi URL** sang một số trang mới.

---

### 1. Hàm tự động bóc tách URL phân trang

Hàm này nhận vào một URL phân trang bất kỳ, tự động nhận diện phần đường dẫn cơ bản và số trang.

```python
import re
from yarl import URL

def parse_pagination_url(url_input: str):
    url = URL(url_input)
    
    # Lọc bỏ các dấu '/' rỗng trong parts
    parts = [p for p in url.parts if p and p != '/']
    
    if not parts:
        return str(url.path), None

    last_part = parts[-1]
    
    # Tìm chuỗi số ở phần tử cuối (Hỗ trợ cả dạng: trang-3, page-3, p3, page=3...)
    match = re.search(r'\d+', last_part)
    
    if match:
        page_num = int(match.group())
        # Cắt bỏ phần chứa số trang ở cuối
        base_path = "/" + "/".join(parts[:-1])
        return base_path, page_num
    else:
        # Nếu không tìm thấy số trang ở path, kiểm tra query parameters (VD: ?page=3)
        if 'page' in url.query:
            return str(url.path), int(url.query['page'])
        elif 'trang' in url.query:
            return str(url.path), int(url.query['trang'])

    return str(url.path), 1  # Mặc định là trang 1 nếu không thấy số trang


# --- KIỂM THỬ HÀM BÓC TÁCH ---
test_urls = [
    "Https://truyenfull.live/danh-sach/truyen-moi/trang-3/",
    "https://example.com/categories/manga/page-12",
    "https://example.com/tin-tuc?trang=5"
]

for u in test_urls:
    path, page = parse_pagination_url(u)
    print(f"URL gốc : {u}")
    print(f"-> Path : {path}")
    print(f"-> Trang: {page}\n" + "-"*40)

```

---

### 2. Hàm xây dựng/thay đổi URL sang số trang mới

Sử dụng tính năng ghép path và bất biến (`immutable`) của `yarl` để tạo URL với số trang mong muốn.

```python
from yarl import URL

def build_next_page_url(url_input: str, target_page: int) -> str:
    url = URL(url_input)
    parts = [p for p in url.parts if p and p != '/']
    
    # 1. Nếu URL dùng Query Parameter (VD: ?page=3 hoặc ?trang=3)
    if 'page' in url.query:
        return str(url.update_query({'page': target_page}))
    if 'trang' in url.query:
        return str(url.update_query({'trang': target_page}))

    # 2. Nếu URL dùng Path Segment (VD: /trang-3/ hoặc /page-3/)
    if parts:
        last_part = parts[-1]
        
        # Kiểm tra tiền tố của phần tử cuối (trang-, page-, ...)
        if 'trang-' in last_part:
            prefix = 'trang-'
        elif 'page-' in last_part:
            prefix = 'page-'
        else:
            prefix = ''

        if prefix:
            # Bỏ phần tử trang cũ, ghép đường dẫn gốc với trang mới
            base_url = url.with_path("/" + "/".join(parts[:-1]))
            new_url = base_url / f"{prefix}{target_page}"
            return str(new_url) + "/" # Giữ lại dấu / ở cuối nếu muốn

    # Mặc định nếu URL chưa có phân trang, nối thêm /trang-{target_page}/
    return str(url / f"trang-{target_page}")


# --- KIỂM THỬ HÀM XÂY DỰNG TẠO TRANG MỚI ---
original_url = "Https://truyenfull.live/danh-sach/truyen-moi/trang-3/"

# Chuyển sang Trang 4
url_page_4 = build_next_page_url(original_url, 4)
print(f"Trang 4: {url_page_4}")
# Output: https://truyenfull.live/danh-sach/truyen-moi/trang-4/

# Chuyển sang Trang 10
url_page_10 = build_next_page_url(original_url, 10)
print(f"Trang 10: {url_page_10}")
# Output: https://truyenfull.live/danh-sach/truyen-moi/trang-10/

```