Hàm `urllib.parse.urlparse()` là một công cụ mạnh mẽ thuộc thư viện chuẩn `urllib` của [Python](https://docs.python.org/3/library/urllib.parse.html), được sử dụng để tách một chuỗi URL thành 6 thành phần cơ bản. Hàm này giúp bạn dễ dàng bóc tách thông tin như tên miền, giao thức, hoặc tham số truy vấn từ một địa chỉ web mà không cần dùng các biểu thức chính quy (Regex) phức tạp. [1, 2, 3] 

* * *

## 1\. Cú pháp cơ bản
    
    
    urllib.parse.urlparse(urlstring, scheme='', allow_fragments=True)
    

  * `urlstring`: Chuỗi URL cần phân tích (kiểu dữ liệu có thể là `str` hoặc `bytes`).
  * `scheme`: Giao thức mặc định (ví dụ: `'http'`, `'https'`) được sử dụng nếu URL truyền vào không chứa giao thức.
  * `allow_fragments`: Nếu đặt là `False`, phần định danh đoạn (fragment `#`) sẽ không được tách riêng mà bị gộp vào thành phần liền trước (path hoặc query). [2, 4] 



* * *

## 2\. Kết quả trả về (6 thành phần chính)

Hàm trả về một đối tượng `ParseResult`. Đối tượng này hoạt động giống như một `namedtuple` gồm 6 thuộc tính tương ứng với cấu trúc URL chuẩn: [1, 2] 

> `scheme://netloc/path;params?query#fragment` [2] 

Thuộc tính| Chỉ số (Index)| Ý nghĩa| Ví dụ với URL mẫu  
---|---|---|---  
`scheme`| 0| Giao thức kết nối| `https`  
`netloc`| 1| Vị trí mạng (Domain + Port)| `://example.com`  
`path`| 2| Đường dẫn đến tài nguyên| `/products/search.php`  
`params`| 3| Tham số của đường dẫn (ít dùng ngày nay)| `type=full`  
`query`| 4| Chuỗi truy vấn dữ liệu (Query string)| `id=123&category=books`  
`fragment`| 5| Neo xác định vị trí trong trang (Anchor)| `reviews`  
  
* * *

## 3\. Ví dụ minh họa thực tế

Dưới đây là cách triển khai hàm `urlparse` để bóc tách một địa chỉ URL phức tạp:
    
    
    from urllib.parse import urlparse
    
    url = "https://example.com"
    
    # Phân tích URL
    result = urlparse(url)
    
    # 1. In toàn bộ đối tượng ParseResult
    print(result)
    # Output: ParseResult(scheme='https', netloc='://example.com', path='/shop/item.php', params='type=digital', query='id=99&coupon=save10', fragment='description')
    
    # 2. Truy cập từng thuộc tính theo tên
    print("Giao thức:", result.scheme)      # Output: https
    print("Tên miền & Cổng:", result.netloc) # Output: ://example.com
    print("Đường dẫn:", result.path)         # Output: /shop/item.php
    print("Query tham số:", result.query)    # Output: id=99&coupon=save10
    print("Đoạn neo (Fragment):", result.fragment) # Output: description
    
    # 3. Truy cập theo chỉ số (Index giống như tuple)
    print("Giao thức (index 0):", result[0]) # Output: https
    

* * *

## 4\. Các thuộc tính mở rộng hữu ích

Ngoài 6 thuộc tính cơ bản trên, đối tượng `ParseResult` còn cung cấp các thuộc tính bổ sung được tính toán sẵn giúp bạn thao tác nhanh hơn:

  * `result.hostname`: Trích xuất chỉ riêng tên miền/máy chủ (loại bỏ đi cổng Port và phần User/Password nếu có). Ví dụ: `://example.com`.
  * `result.port`: Trích xuất chỉ riêng số cổng dưới dạng số nguyên (`int`). Nếu URL không ghi rõ cổng, thuộc tính này trả về `None`.
  * `result.username` / `result.password`: Lấy thông tin đăng nhập nếu URL có chứa chuỗi xác thực dạng `https://domain.com`.



* * *

## 5\. Lưu ý quan trọng khi sử dụng

  * Không giải mã mã hóa phần trăm (%-escapes): `urlparse` giữ nguyên các ký tự được mã hóa đặc biệt (ví dụ `%20` đại diện cho dấu cách). Nếu muốn giải mã các ký tự này sang dạng văn bản đọc được, bạn cần kết hợp sử dụng hàm `urllib.parse.unquote()`. [2, 5] 
  * Tính đồng nhất dữ liệu: Nếu bạn truyền vào chuỗi dạng `str`, kết quả trả về sẽ chứa `str`. Nếu truyền vào chuỗi dạng bytes (`bytes`), các thành phần trả về cũng sẽ ở dạng `bytes`. Tránh truyền lẫn lộn hai kiểu dữ liệu này để không gặp lỗi `TypeError`. [4] 



Bạn có muốn tìm hiểu thêm cách sử dụng kết quả từ `urlparse` để phân tích sâu các tham số trong chuỗi Query (bằng hàm `parse_qs`) hoặc cách gộp các thành phần lại thành URL hoàn chỉnh (bằng hàm `urlunparse`) không?

  


[1] [https://pymotw.com](https://translate.google.com/translate?u=https://pymotw.com/2/urlparse/&hl=vi&sl=en&tl=vi&client=sge)

[2] [https://www.cs.unb.ca](https://www.cs.unb.ca/~bremner/teaching/cs2613/books/python3-doc/library/urllib.parse.html)

[3] [https://www.studocu.vn](https://www.studocu.vn/vn/document/truong-trung-hoc-pho-thong-nguyen-trung-truc/toan-12-thi-tot-nghiep/phan-tich-url-bang-python-bai-1-url-parsing-tuan-1/155301421)

[4] [https://github.com](https://github.com/python/cpython/blob/main/Doc/library/urllib.parse.rst)

[5] [https://stackoverflow.com](https://translate.google.com/translate?u=https://stackoverflow.com/questions/18727347/how-to-extract-a-filename-from-a-url-and-append-a-word-to-it&hl=vi&sl=en&tl=vi&client=sge)