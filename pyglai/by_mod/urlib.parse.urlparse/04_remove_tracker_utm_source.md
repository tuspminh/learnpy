Để giải quyết hai bài toán rất phổ biến này, chúng ta sẽ viết các hàm Python chuyên dụng, tận dụng tối đa bộ công cụ `urllib.parse` mà chúng ta vừa làm quen.

* * *

## Kịch bản 1: Tự động tăng số trang (Pagination) khi cào dữ liệu (Web Scraping)

Khi viết script cào dữ liệu, bạn thường phải duyệt qua các trang như `page=1`, `page=2`. Hàm dưới đây sẽ tự động tìm tham số trang, tăng nó lên 1 đơn vị. Nếu URL ban đầu chưa có tham số trang, hàm sẽ tự động thêm vào.
    
    
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    
    def next_page_url(url, page_param='page'):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Kiểm tra xem tham số trang đã tồn tại chưa
        if page_param in query_params:
            # Lấy giá trị hiện tại, chuyển sang số nguyên và tăng lên 1
            current_page = int(query_params[page_param][0])
            query_params[page_param] = [str(current_page + 1)]
        else:
            # Nếu chưa có tham số trang, mặc định trang tiếp theo là 2
            query_params[page_param] = ['2']
            
        # Ghép lại URL mới
        url_parts = list(parsed_url)
        url_parts[4] = urlencode(query_params, doseq=True)
        return urlunparse(url_parts)
    
    # --- THỬ NGHIỆM ---
    url_1 = "https://example.com"
    print("Trang tiếp theo (1):", next_page_url(url_1))
    # Output: https://example.com
    
    url_2 = "https://example.com"
    print("Trang tiếp theo (2):", next_page_url(url_2))
    # Output: https://example.com&page=2
    

* * *

## Kịch bản 2: Làm sạch URL (Loại bỏ các tham số theo dõi như `utm_*`, `fbclid`)

Các liên kết chia sẻ trên Facebook, Google Analytics thường bị đính kèm rất nhiều tham số rác để theo dõi người dùng (ví dụ: `?utm_source=facebook&utm_medium=social&fbclid=12345`). Hàm này sẽ giúp bạn lọc sạch danh sách URL, chỉ giữ lại các tham số cốt lõi.
    
    
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    
    def clean_tracker_params(url):
        # Danh sách các từ khóa theo dõi phổ biến cần xóa
        TRACKERS_TO_REMOVE = {'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'fbclid', 'gclid'}
        
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # Lọc bỏ các tham số nằm trong danh sách đen
        # Dùng list() để tránh lỗi "RuntimeError: dictionary changed size during iteration"
        for key in list(query_params.keys()):
            if key.lower() in TRACKERS_TO_REMOVE:
                del query_params[key]
                
        # Ghép lại URL sau khi đã làm sạch
        url_parts = list(parsed_url)
        url_parts[4] = urlencode(query_params, doseq=True)
        return urlunparse(url_parts)
    
    # --- THỬ NGHIỆM ---
    dirty_urls = [
        "https://blog.com",
        "https://shop.com"
    ]
    
    print("--- KẾT QUẢ LÀM SẠCH ---")
    for url in dirty_urls:
        print(clean_tracker_params(url))
    # Output:
    # https://blog.com
    # https://shop.com
    

Nếu bạn muốn nâng cấp các hàm này, hãy cho tôi biết:

  * Bạn có cần xử lý các URL dạng đường dẫn tương đối (ví dụ: `/products?page=1` thay vì có đầy đủ `https://...`) không?
  * Bạn có cần lưu kết quả sau khi làm sạch ra một file cụ thể nào (như CSV hoặc TXT) không?