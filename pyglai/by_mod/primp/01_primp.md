PRIMP (viết tắt của PyReqwest_IMPersonate hoặc Python Requests IMPersonate) là một thư viện HTTP client hiệu năng cao dành cho Python, được thiết kế để giả lập (impersonate) chính xác các hành vi của trình duyệt web thực tế. Thư viện này là một bản binding Python của thư viện `rquest` viết bằng Rust, giúp lập trình viên dễ dàng vượt qua các hệ thống chống bot (anti-bot) khi cào dữ liệu (web scraping). [1, 2] 

* * *

## Các tính năng cốt lõi

Tính năng| Chi tiết kỹ thuật  
---|---  
Giả lập dấu vân tay (Fingerprinting)| Mimic chính xác mã hóa TLS, dấu vân tay HTTP/2, JA3, JA4 của các trình duyệt phổ biến như Chrome, Firefox, Safari.  
Hiệu năng vượt trội| Được xây dựng dựa trên lõi Rust (`rquest`), mang lại tốc độ xử lý và khả năng tối ưu hóa luồng cực nhanh.  
Hỗ trợ Bất đồng bộ| Cung cấp cả hai giao diện đồng bộ (`Client`) và bất đồng bộ (`AsyncClient`) để xử lý nhiều yêu cầu cùng lúc.  
Cài đặt sẵn (Precompiled Wheels)| Hỗ trợ đa nền tảng bao gồm Windows, Linux, macOS (cả chip Intel và Apple Silicon/ARM) mà không cần cài đặt thêm trình biên dịch Rust khi cài từ `pip`.  
  
* * *

## Hướng dẫn sử dụng chi tiết

## 1\. Cài đặt thư viện

Bạn có thể cài đặt [thư viện primp thông qua PyPI](https://pypi.org/project/primp/) bằng lệnh:
    
    
    pip install primp
    

## 2\. Sử dụng dạng Đồng bộ (Synchronous Client)

Giao diện này hoạt động tương tự như thư viện `requests` truyền thống nhưng có thêm tham số `impersonate`: [2, 3] 
    
    
    import primp
    
    # Khởi tạo client giả lập trình duyệt Chrome phiên bản cụ thể
    client = primp.Client(impersonate="chrome_146")
    
    # Gửi yêu cầu GET
    response = client.get("https://tls.peet.ws/api/all")
    
    print("Mã trạng thái:", response.status_code)
    print("Nội dung phản hồi:", response.text)
    

## 3\. Sử dụng dạng Bất đồng bộ (Asynchronous Client)

Phù hợp cho các tác vụ cần cào dữ liệu số lượng lớn với tốc độ cao bằng `asyncio`:
    
    
    import asyncio
    import primp
    
    async def fetch():
        # Khởi tạo AsyncClient giả lập trình duyệt Firefox
        async with primp.AsyncClient(impersonate="firefox_130") as client:
            response = await client.get("https://httpbin.org")
            print(response.text)
    
    asyncio.run(fetch())
    

* * *

## Các tùy chọn giả lập trình duyệt (Impersonate Profiles)

Thư viện cung cấp nhiều chuỗi định danh để bạn tùy chọn giả lập, ví dụ:

  *   * Chrome: `"chrome_100"`, `"chrome_120"`, `"chrome_146"`,...
  * Firefox: `"firefox_117"`, `"firefox_130"`,...
  * Safari: `"safari_17"`,... [3] 
  * 


Khi sử dụng các profile này, thư viện tự động cấu hình các tiêu đề HTTP (Headers), thứ tự sắp xếp Header, cơ chế bắt tay TLS và các tham số HTTP/2 sao cho trùng khớp 100% với trình duyệt gốc, giúp giảm thiểu tối đa tỷ lệ bị chặn bởi Cloudflare, Akamai hay các dịch vụ tường lửa tương tự. [2, 4] 

Nếu bạn muốn đi sâu hơn, hãy cho tôi biết:

  *   * Bạn đang gặp khó khăn khi cào dữ liệu từ trang web cụ thể nào (như Cloudflare bảo vệ)?
  * Bạn cần cấu hình thêm về Proxy, Cookie, hay xử lý Redirect?
  * 


Tôi sẽ hướng dẫn bạn viết đoạn mã cấu hình chi tiết cho trường hợp đó.

  


[1] [https://pypi.org](https://pypi.org/project/primp/0.5.4/)

[2] [https://www.freshports.org](https://www.freshports.org/www/py-primp)

[3] [https://github.com](https://github.com/deedy5/primp)

[4] [https://pypi.org](https://pypi.org/project/primp/0.14.0/)