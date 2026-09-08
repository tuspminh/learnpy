Để xử lý cả hai yêu cầu nâng cấp trên, chúng ta sẽ xây dựng một script Python hoàn chỉnh. Script này có khả năng:

  1. Xử lý URL tương đối: Tự động chuyển đổi các đường dẫn dạng tương đối (như `/products?page=1`) thành URL tuyệt đối bằng cách kết hợp với một tên miền gốc (Base URL) thông qua hàm `urllib.parse.urljoin()`.
  2. Xuất file dữ liệu: Tự động lọc sạch danh sách URL rác và xuất kết quả ra một file CSV để bạn tiện sử dụng cho công việc.



* * *

## Mã nguồn Python Hoàn Chỉnh

Dưới đây là đoạn code mẫu chuẩn sử dụng các thư viện tích hợp sẵn của Python:
    
    
    import csv
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, urljoin
    
    def clean_and_normalize_url(url, base_url="https://example.com"):
        """
        1. Chuyển URL tương đối thành tuyệt đối.
        2. Loại bỏ các tham số tracker (utm_*, fbclid, gclid).
        """
        # Bước 1: Xử lý URL tương đối bằng urljoin
        # Nếu 'url' đã là tuyệt đối (có http/https), urljoin sẽ giữ nguyên nó.
        absolute_url = urljoin(base_url, url)
        
        # Bước 2: Phân tích cấu trúc URL
        parsed_url = urlparse(absolute_url)
        query_params = parse_qs(parsed_url.query)
        
        # Danh sách các tham số theo dõi cần loại bỏ
        TRACKERS_TO_REMOVE = {'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'fbclid', 'gclid'}
        
        # Lọc bỏ các tham số rác
        for key in list(query_params.keys()):
            if key.lower() in TRACKERS_TO_REMOVE:
                del query_params[key]
                
        # Bước 3: Ghép lại URL hoàn chỉnh
        url_parts = list(parsed_url)
        url_parts[4] = urlencode(query_params, doseq=True) # Cập nhật lại phần query
        
        return urlunparse(url_parts)
    
    # ==========================================
    # Cấu hình dữ liệu thử nghiệm
    # ==========================================
    # Giả định trang web bạn đang cào dữ liệu có tên miền gốc sau:
    BASE_DOMAIN = "https://myshop.com"
    
    # Danh sách URL thô thu thập được (lẫn lộn cả URL tuyệt đối, tương đối và tracker)
    raw_urls = [
        "https://myshop.com",
        "/categories/shoes?utm_medium=email&page=2&sort=price",
        "https://partner-site.com",
        "/cart?utm_campaign=retargeting"
    ]
    
    # Tên file CSV đầu ra
    output_file = "cleaned_urls.csv"
    
    # ==========================================
    # Tiến hành xử lý và xuất file CSV
    # ==========================================
    print("Đang xử lý dữ liệu...")
    
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Ghi dòng tiêu đề (Header) cho file CSV
        writer.writerow(["URL Gốc", "URL Sau Khi Làm Sạch"])
        
        # Xử lý từng URL và ghi vào file
        for original_url in raw_urls:
            cleaned_url = clean_and_normalize_url(original_url, base_url=BASE_DOMAIN)
            writer.writerow([original_url, cleaned_url])
    
    print(f"Xử lý thành công! Kết quả đã được lưu vào file: {output_file}")
    

* * *

## Kết quả file CSV tạo ra sẽ trông như thế nào?

Khi bạn mở file `cleaned_urls.csv` (bằng Excel hoặc các trình đọc text), dữ liệu sẽ được phân tách rõ ràng:

URL Gốc| URL Sau Khi Làm Sạch|  _Ghi chú giải thích_  
---|---|---  
`https://myshop.com`| `https://myshop.com`|  _Đã lọc bỏ các tracker_  
`/categories/shoes?utm_medium=email&page=2&sort=price`| `https://myshop.com`|  _Đã thêm domain gốc + lọc tracker_  
`https://partner-site.com`| `https://partner-site.com`|  _Giữ nguyên domain ngoài + lọc tracker_  
`/cart?utm_campaign=retargeting`| `https://myshop.com`|  _Chuyển thành tuyệt đối, xóa hết query vì chỉ toàn tracker_  
  
Nếu bạn muốn tiếp tục tối ưu script này, vui lòng cho biết:

  * Bạn có cần đọc danh sách URL đầu vào trực tiếp từ một file có sẵn (như file TXT hoặc file CSV khác) thay vì khai báo cứng trong code không?
  * Bạn có cần tải hoặc cào (Scrape) nội dung của các URL sau khi đã làm sạch này không?