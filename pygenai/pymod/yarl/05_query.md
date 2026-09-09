Làm việc với **Query Parameters** (các tham số đằng sau dấu `?` trên URL) trong `yarl` rất linh hoạt và trực quan nhờ tích hợp lớp `MultiDict` (cho phép một key chứa nhiều giá trị) và thuộc tính bất biến (`Immutable`).

---

### 1. Truy xuất Query Parameters

Để đọc tham số query, bạn sử dụng thuộc tính `.query` (trả về đối tượng kiểu `MultiDictProxy` tương tự `dict`) hoặc `.query_string` (chuỗi thô).

```python
from yarl import URL

url = URL('https://example.com/search?q=python&category=code&category=web&page=1')

# 1. Lấy toàn bộ query string thô
print(url.query_string) 
# Output: 'q=python&category=code&category=web&page=1'

# 2. Truy xuất giá trị theo Key (tương tự dict)
print(url.query['q'])     # 'python'
print(url.query['page'])  # '1' (Lưu ý: Tất cả giá trị thu được luôn ở dạng str)

# 3. Với key có nhiều giá trị trùng nhau (dùng getall)
print(url.query.getall('category')) 
# Output: ['code', 'web']

```

---

### 2. Thêm hoặc Cập nhật Query (`update_query` / Toán tử `%`)

Dùng `update_query()` khi bạn muốn **thêm mới** các tham số, hoặc **cập nhật giá trị** cho các key đã tồn tại mà **không làm mất các tham số cũ khác**.

#### A. Dùng phương thức `update_query()`

```python
url = URL('https://example.com/products?category=laptop&page=1')

# Thêm 'sort' và cập nhật 'page' từ 1 thành 2
new_url = url.update_query({'page': 2, 'sort': 'price_asc'})

print(new_url)
# Output: https://example.com/products?category=laptop&page=2&sort=price_asc

```

#### B. Dùng toán tử `%` (Cú pháp viết tắt)

Toán tử `%` là cách viết ngắn gọn của `update_query()`:

```python
url = URL('https://example.com/search?q=python')

# Thêm/cập nhật tham số bằng toán tử %
new_url = url % {'page': 1, 'limit': 20}

print(new_url)
# Output: https://example.com/search?q=python&page=1&limit=20

```

---

### 3. Thay thế toàn bộ Query (`with_query`)

Nếu bạn muốn **xóa hết tất cả query cũ** và thay thế hoàn toàn bằng một bộ query mới, hãy dùng `with_query()`.

```python
url = URL('https://example.com/search?q=python&filter=active&page=5')

# Thay thế toàn bộ query cũ
new_url = url.with_query({'q': 'yarl', 'format': 'json'})

print(new_url)
# Output: https://example.com/search?q=yarl&format=json

```

---

### 4. Xóa Query Parameters

`yarl` hỗ trợ nhiều cách để xóa một phần hoặc toàn bộ query parameter:

#### A. Xóa TOÀN BỘ Query Parameters

Truyền `None` hoặc dict rỗng vào `with_query()`:

```python
url = URL('https://example.com/search?q=python&page=1')

# Xóa hoàn toàn phần query đằng sau dấu ?
clean_url = url.with_query(None)

print(clean_url)
# Output: https://example.com/search

```

#### B. Xóa MỘT HOẶC NHIỀU Key cụ thể

Truyền giá trị `None` cho key muốn xóa trong `update_query()`:

```python
url = URL('https://example.com/items?q=shoes&brand=nike&page=2')

# Xóa key 'brand' và 'page' bằng cách gán giá trị None
new_url = url.update_query({'brand': None, 'page': None})

print(new_url)
# Output: https://example.com/items?q=shoes

```

---

### 5. Làm việc với Query có các Key trùng nhau (Multiple Values)

Trong một số API, một key có thể xuất hiện nhiều lần (ví dụ: `?tag=python&tag=asyncio`). Để xử lý trường hợp này, bạn truyền một **list of tuples** thay vì `dict`.

```python
url = URL('https://example.com/posts')

# Thêm nhiều giá trị cho cùng một key 'tag'
multi_url = url.with_query([
    ('tag', 'python'),
    ('tag', 'asyncio'),
    ('tag', 'yarl'),
    ('limit', 10)
])

print(multi_url)
# Output: https://example.com/posts?tag=python&tag=asyncio&tag=yarl&limit=10

```

---

### Bảng tổng hợp thao tác Query Parameters

| Thao tác | Phương thức / Cú pháp | Kết quả minh họa |
| --- | --- | --- |
| **Thêm / Cập nhật** | `url.update_query({'a': 1})` hoặc `url % {'a': 1}` | Thêm/sửa `a=1`, giữ nguyên các key khác |
| **Thay thế hoàn toàn** | `url.with_query({'b': 2})` | Đè toàn bộ query thành `b=2` |
| **Xóa 1 Key** | `url.update_query({'a': None})` | Xóa riêng key `a` khỏi URL |
| **Xóa tất cả Query** | `url.with_query(None)` | Xóa bỏ hoàn bộ chuỗi query |
| **Query trùng Key** | `url.with_query([('tag', '1'), ('tag', '2')])` | Tạo `?tag=1&tag=2` |