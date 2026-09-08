Để chỉnh sửa các tham số trong chuỗi Query (phần sau dấu `?`) một cách chính xác mà không làm hỏng cấu trúc URL, chúng ta sẽ kết hợp bộ 3 công cụ: `urlparse` (tách URL), `parse_qs` (chuyển đổi query thành Dictionary để sửa đổi), và `urlunparse` (ghép lại URL).

Ngoài ra, chúng ta cần dùng thêm hàm `urlencode` để chuyển Dictionary đã sửa ngược lại thành chuỗi query thô.

* * *

## Quy trình 4 bước chỉnh sửa Tham số URL

Dưới đây là đoạn code mẫu hoàn chỉnh giúp bạn Thêm, Sửa, và Xóa bất kỳ tham số nào trên URL:
    
    
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    
    # URL ban đầu cần xử lý
    original_url = "https://example.com"
    
    # ----------------------------------------------------
    # BƯỚC 1: Tách URL thành các thành phần cơ bản
    # ----------------------------------------------------
    parsed_url = urlparse(original_url)
    
    # ----------------------------------------------------
    # BƯỚC 2: Chuyển chuỗi query thành dạng Dictionary (Key-Value)
    # ----------------------------------------------------
    # parse_qs sẽ tạo ra Dict với Value là một List (ví dụ: {'page': ['1']})
    query_params = parse_qs(parsed_url.query)
    
    # ----------------------------------------------------
    # BƯỚC 3: Tiến hành Thêm / Sửa / Xóa tham số
    # ----------------------------------------------------
    # Cập nhật/Sửa tham số có sẵn (Lưu ý: Giá trị phải bọc trong List)
    query_params['page'] = ['2']
    
    # Thêm một tham số mới hoàn toàn
    query_params['sort'] = ['newest']
    
    # Xóa một tham số không mong muốn
    if 'status' in query_params:
        del query_params['status']
    
    # ----------------------------------------------------
    # BƯỚC 4: Mã hóa lại chuỗi Query và ghép hoàn chỉnh URL
    # ----------------------------------------------------
    # doseq=True giúp urlencode hiểu và xử lý các Value dạng List một cách chính xác
    new_query_string = urlencode(query_params, doseq=True)
    
    # Chuyển đổi parsed_url sang list để thay thế phần query mới
    url_parts = list(parsed_url)
    url_parts[4] = new_query_string  # Vị trí index 4 chính là thành phần 'query'
    
    # Ghép lại thành URL mới hoàn chỉnh
    final_url = urlunparse(url_parts)
    
    print("URL ban đầu:", original_url)
    print("URL sau khi sửa:", final_url)
    

## Kết quả hiển thị (Output):
    
    
    URL ban đầu: https://example.com
    URL sau khi sửa: https://example.com
    

* * *

## 💡 Lưu ý cốt lõi khi làm việc với `parse_qs`:

  1. Giá trị luôn nằm trong List `[]`: Hàm `parse_qs` hỗ trợ trường hợp một tham số xuất hiện nhiều lần trong URL (ví dụ: `?tags=python&tags=django`). Do đó, cấu trúc trả về luôn là `{'key': ['value1', 'value2']}`. Khi bạn muốn sửa hoặc thêm tham số, bắt buộc phải truyền giá trị dạng List: `query_params['my_key'] = ['my_value']`.
  2. Tham số `doseq=True`: Khi gọi hàm `urlencode(query_params, doseq=True)`, biến này bắt buộc phải đặt là `True`. Nếu thiếu nó, `urlencode` sẽ mã hóa luôn cả dấu ngoặc vuông của List, làm chuỗi URL bị sai định dạng chuẩn.



Bạn có cần áp dụng logic này vào một bài toán cụ thể nào không? Chẳng hạn như quét danh sách nhiều URL để làm sạch tham số theo dõi (rác/tracker như utm_source) hoặc tự động tăng số trang (pagination) trong Web Scraping?