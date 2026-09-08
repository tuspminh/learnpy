Dưới đây là thiết kế một Class chuyên dụng có tên là `URLManager`. Class này đóng gói toàn bộ 5 hàm (`urlparse`, `urlunparse`, `parse_qs`, `urlencode`, `urljoin`) thành các phương thức hướng đối tượng (OOP) trực quan, giúp bạn tái sử dụng cực kỳ tiện lợi trong mọi dự án Scrapy, Automation hoặc Data Analysis.

## 1\. Mã nguồn Class `URLManager`
    
    
    import csv
    from urllib.parse import urlparse, urlunparse, parse_qs, urlencode, urljoin
    
    class URLManager:
        def __init__(self, url: str, base_url: str = None):
            """
            Khởi tạo đối tượng xử lý URL.
            :param url: URL cần xử lý (có thể là tuyệt đối hoặc tương đối)
            :param base_url: Domain gốc, dùng để chuẩn hóa nếu URL truyền vào là tương đối
            """
            # 1. Tự động chuyển đổi link tương đối thành tuyệt đối nếu có base_url
            self.current_url = urljoin(base_url, url) if base_url else url
            
            # 2. Bóc tách URL thành các thành phần cơ bản (urlparse)
            self._parsed = urlparse(self.current_url)
            
            # 3. Chuyển đổi query string thành dictionary để dễ thao tác (parse_qs)
            self.params = parse_qs(self._parsed.query)
    
        def set_param(self, key: str, value):
            """Thêm mới hoặc cập nhật một tham số trên URL (Sửa)"""
            # Ép kiểu giá trị về dạng chuỗi và bọc trong list theo đúng chuẩn parse_qs
            self.params[key] = [str(value)]
            return self
    
        def remove_param(self, key: str):
            """Xóa một tham số khỏi URL nếu tồn tại (Xóa)"""
            if key in self.params:
                del self.params[key]
            return self
    
        def remove_trackers(self):
            """Làm sạch URL bằng cách xóa hàng loạt các tham số theo dõi (Clean)"""
            trackers = {'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'fbclid', 'gclid'}
            for key in list(self.params.keys()):
                if key.lower() in trackers:
                    del self.params[key]
            return self
    
        def next_page(self, page_param: str = 'page'):
            """Tự động tăng số trang (Pagination) lên 1 đơn vị"""
            if page_param in self.params:
                try:
                    current_page = int(self.params[page_param][0])
                    self.params[page_param] = [str(current_page + 1)]
                except ValueError:
                    self.params[page_param] = ['2']
            else:
                self.params[page_param] = ['2']
            return self
    
        def build(self) -> str:
            """
            Đóng gói toàn bộ các thay đổi và trả về chuỗi URL hoàn chỉnh cuối cùng.
            (urlencode + urlunparse)
            """
            # Mã hóa lại dictionary params thành chuỗi query thô
            new_query = urlencode(self.params, doseq=True)
            
            # Tạo bản bản sao cấu trúc URL và thay thế phần query mới
            url_components = list(self._parsed)
            url_components[4] = new_query
            
            # Ghép lại thành chuỗi URL
            self.current_url = urlunparse(url_components)
            return self.current_url
    
        def __str__(self):
            return self.build()
    

* * *

## 2\. Hướng dẫn sử dụng thực tế (Ví dụ minh họa)

Nhờ thiết kế theo dạng Method Chaining (gọi các phương thức liên tiếp nhau qua dấu chấm `.`), mã nguồn của bạn sẽ trở nên cực kỳ ngắn gọn và dễ đọc.

## Ví dụ 1: Xử lý chuỗi (Thêm, Xóa, Tăng trang liên hoàn)
    
    
    # Giả sử ta lấy được một link tương đối từ trang web
    raw_link = "/products?utm_source=adwords&page=1&sort=oldest"
    base_domain = "https://my-ecom.com"
    
    # Khởi tạo và thực hiện chuỗi hành động:
    # Chuẩn hóa -> Xóa tracker -> Sửa sort -> Tăng trang -> Xuất kết quả
    final_url = (URLManager(raw_link, base_url=base_domain)
                 .remove_trackers()
                 .set_param('sort', 'newest')
                 .next_page()
                 .build())
    
    print("URL cuối cùng:", final_url)
    # Output: https://my-ecom.com
    

## Ví dụ 2: Lọc danh sách và Xuất file CSV hàng loạt

Bạn có thể mang Class này ứng dụng trực tiếp vào bài toán xử lý danh sách URL lớn từ file như sau:
    
    
    urls_to_process = [
        "/detail?id=50&utm_medium=banner",
        "https://my-ecom.com",
        "/detail?id=60&page=3&utm_campaign=sale"
    ]
    
    processed_data = []
    for url in urls_to_process:
        # Khởi tạo qua Class, làm sạch và đóng gói lại
        clean_url = URLManager(url, base_url="https://my-ecom.com").remove_trackers().build()
        processed_data.append([url, clean_url])
    
    # Xuất ra file CSV
    with open("normalized_urls.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Original URL", "Cleaned URL"])
        writer.writerows(processed_data)
    
    print("Đã xuất file CSV thành công!")
    

Class này đã tích hợp đầy đủ tính năng cốt lõi cho các nhu cầu thông thường. Tùy thuộc vào dự án của bạn, nếu bạn muốn nâng cấp thêm, hãy cho tôi biết:

  * Bạn có cần Class này tự động nhận diện và thay đổi cả giao thức (ví dụ chuyển ép buộc từ `http` sang `https`) không?
  * Bạn có cần xử lý các URL có chứa ký tự tiếng Việt có dấu (cần tích hợp thêm `unquote` để giải mã mã phần trăm) không?