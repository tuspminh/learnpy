Hàm `urllib.parse.urlunparse()` là hàm nghịch đảo của `urlparse()`. Nhiệm vụ của nó là ghép nối 6 thành phần của URL trở lại thành một chuỗi URL hoàn chỉnh và đúng chuẩn kỹ thuật [Python](https://docs.python.org/3/library/urllib.parse.html).

Hàm này cực kỳ hữu ích khi bạn muốn thay đổi một phần nhỏ của URL (ví dụ: đổi giao thức từ `http` thành `https`, hoặc đổi tên miền) rồi ghép lại thành một đường dẫn mới.

* * *

## 1\. Cú pháp cơ bản
    
    
    urllib.parse.urlunparse(parts)
    

  * `parts`: Một biến chứa đúng 6 phần tử theo thứ tự bắt buộc: `(scheme, netloc, path, params, query, fragment)`.
  * Tham số này có thể là một `tuple`, `list`, hoặc chính đối tượng `ParseResult` do hàm `urlparse()` trả về.



* * *

## 2\. Ví dụ 1: Ghép nối URL từ một bộ Tuple dữ liệu thô

Nếu bạn có các thành phần riêng lẻ được lưu dưới dạng một danh sách hoặc một tuple, bạn có thể truyền thẳng nó vào hàm `urlunparse`:
    
    
    from urllib.parse import urlunparse
    
    # Tạo một tuple chứa đúng 6 thành phần (thiếu phần nào thì để chuỗi rỗng '')
    url_components = (
        'https',                  # 0. scheme
        'docs.python.org',        # 1. netloc
        '/3/library/urllib.html', # 2. path
        '',                       # 3. params (không dùng thì để rỗng)
        'highlight=urlparse',     # 4. query
        'urlunparse-target'       # 5. fragment
    )
    
    # Ghép thành URL hoàn chỉnh
    full_url = urlunparse(url_components)
    print(full_url)
    # Output: https://python.org
    

* * *

## 3\. Ví dụ 2: Sửa đổi một thành phần của URL (Quy trình Parse -> Modify -> Unparse)

Đây là ứng dụng thực tế phổ biến nhất. Vì đối tượng `ParseResult` trả về từ `urlparse()` là _immutable_ (không thể sửa đổi trực tiếp dữ liệu), bạn cần chuyển nó sang dạng danh sách (`list`) hoặc sử dụng phương thức `._replace()` trước khi ghép lại bằng `urlunparse()`.

## Cách 1: Chuyển đổi sang danh sách (`list`)
    
    
    from urllib.parse import urlparse, urlunparse
    
    original_url = "http://example.com"
    
    # 1. Tách URL thành các thành phần
    parsed_url = urlparse(original_url)
    
    # 2. Chuyển thành list để có thể chỉnh sửa
    url_parts = list(parsed_url)
    
    # 3. Thay đổi các thành phần mong muốn
    url_parts[0] = 'https'               # Đổi giao thức từ http thành https
    url_parts[1] = '://example.com'      # Đổi subdomain/domain
    url_parts[4] = 'q=python&page=2'      # Cập nhật thêm tham số query
    
    # 4. Ghép lại thành URL mới
    new_url = urlunparse(url_parts)
    print(new_url)
    # Output: https://://example.com/search?q=python&page=2
    

## Cách 2: Sử dụng phương thức ẩn `._replace()` (Ngắn gọn hơn)
    
    
    from urllib.parse import urlparse, urlunparse
    
    parsed = urlparse("https://oldsite.com")
    
    # Tạo bản sao mới và thay thế thành phần 'netloc'
    updated_parsed = parsed._replace(netloc="newsite.org")
    
    # Ghép lại thành URL
    new_url = urlunparse(updated_parsed)
    print(new_url)
    # Output: https://newsite.org
    

* * *

## 4\. Những lưu ý quan trọng khi dùng `urlunparse`

  * Quy tắc dấu gạch chéo (`/`): Nếu thành phần `path` của bạn không bắt đầu bằng dấu `/` nhưng trước đó có tồn tại `netloc`, hàm `urlunparse` sẽ tự động thêm dấu `/` vào giữa chúng để đảm bảo URL hợp lệ. Tuy nhiên, để an toàn, bạn nên chủ động định dạng `path` bắt đầu bằng dấu `/`.
  * Bắt buộc phải đủ 6 phần tử: Nếu bạn truyền vào một bộ dữ liệu chỉ có 4 hoặc 5 phần tử, Python sẽ ném ra lỗi `ValueError: need more than X values to unpack`. Đối với các thành phần không có dữ liệu (như `params` hoặc `fragment`), bạn bắt buộc phải truyền vào chuỗi rỗng `''`.



Bạn có muốn kết hợp hai hàm này với `parse_qs` để thực hiện việc thêm, xóa hoặc chỉnh sửa một tham số truy vấn cụ thể (ví dụ thay đổi giá trị của `?page=1` thành `?page=2`) trên URL không?