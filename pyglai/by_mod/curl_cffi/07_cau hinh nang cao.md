Dưới đây là hướng dẫn các cấu hình nâng cao của `curl_cffi` giúp bạn tối ưu hóa việc cào dữ liệu, xử lý proxy, quản lý cookie và tối ưu hiệu năng cho hệ thống crawl truyện chữ.

* * *

## 1\. Cấu hình Proxy (HTTP / HTTPS / SOCKS5)

Để tránh bị khóa IP khi crawl số lượng lớn, bạn cần luân phiên thay đổi IP (Rotate Proxy). `curl_cffi` hỗ trợ cả proxy thông thường và SOCKS5 bảo mật cao.
    
    
    from curl_cffi import requests
    
    proxies = {
        "http": "http://user:password@proxy_ip:port",
        "https": "http://user:password@proxy_ip:port"
        # Hoặc dùng socks5: "https": "socks5://user:password@proxy_ip:port"
    }
    
    response = requests.get(
        "https://httpbin.org", 
        proxies=proxies, 
        impersonate="chrome"
    )
    print(response.json())
    

* * *

## 2\. Quản lý Cookie & Login (Duy trì phiên làm việc)

Khi crawl các trang truyện yêu cầu đăng nhập hoặc trang sử dụng Cookie để theo dõi lượt đọc, bạn phải sử dụng `Session` thay vì các request đơn lẻ.
    
    
    from curl_cffi.requests import Session
    
    # Khởi tạo session để tự động giữ cookie cho các request sau
    with Session(impersonate="chrome") as session:
        # Bước 1: Gửi request đăng nhập hoặc nhận cookie trang chủ
        session.get("https://example-truyen.com")
        
        # Bước 2: Thêm thủ công cookie đặc biệt nếu cần (ví dụ cookie VIP bypass chương khóa)
        session.cookies.set("user_vip_token", "abc123xyz", domain="example-truyen.com")
        
        # Bước 3: Truy cập chương truyện, session tự mang theo toàn bộ cookie trên
        response = session.get("https://example-truyen.com")
        print(response.status_code)
    

* * *

## 3\. Tối ưu hiệu năng Async: Giới hạn số luồng (Semaphore)

Nếu bạn crawl song song quá nhiều chương cùng lúc bằng `asyncio.gather`, website mục tiêu sẽ nhận diện hành vi bất thường và block IP của bạn ngay lập tức. Hãy dùng `asyncio.Semaphore` để giới hạn số request chạy đồng thời.
    
    
    import asyncio
    from curl_cffi.requests import AsyncSession
    
    async def worker(url, session, semaphore):
        # Semaphore đảm bảo chỉ có tối đa N request được chạy cùng 1 thời điểm
        async with semaphore:
            try:
                response = await session.get(url, timeout=10)
                print(f"Thành công: {url} | Size: {len(response.text)}")
            except Exception as e:
                print(f"Lỗi: {url} | {e}")
    
    async def main():
        urls = [f"https://example-truyen.com{i}" for i in range(1, 50)]
        
        # Chỉ cho phép tối đa 5 request chạy đồng thời
        sem = asyncio.Semaphore(5) 
        
        async with AsyncSession(impersonate="chrome") as session:
            tasks = [worker(url, session, sem) for url in urls]
            await asyncio.gather(*tasks)
    
    asyncio.run(main())
    

* * *

## 4\. Bỏ qua xác thực SSL (Verify SSL)

Một số trang truyện sử dụng chứng chỉ SSL tự ký hoặc bị hết hạn, khiến thư viện ném lỗi bảo mật kết nối. Bạn có thể tắt tính năng kiểm tra này bằng tham số `verify=False`.
    
    
    from curl_cffi import requests
    
    response = requests.get(
        "https://expired-ssl-truyen.com", 
        impersonate="chrome", 
        verify=False  # Bỏ qua lỗi SSL Certificate
    )
    

* * *

## 5\. Tự tùy biến Dấu vân tay JA3/JA4 (Cấu hình sâu)

Mặc dù tham số `impersonate="chrome"` đã làm rất tốt, đôi khi bạn cần giả lập một phiên bản trình duyệt cụ thể hơn hoặc đổi sang Safari/Firefox để qua mặt các cơ chế quét bot dị biệt.

Trình duyệt mục tiêu| Giá trị `impersonate` phù hợp  
---|---  
Google Chrome (Khuyên dùng)| `"chrome"`, `"chrome110"`, `"chrome120"`  
Mozilla Firefox| `"firefox"`, `"firefox120"`  
Microsoft Edge| `"edge"`, `"edge101"`  
Apple Safari| `"safari"`, `"safari15_5"`  
      
    
    # Giả lập Firefox trên nền lõi curl
    response = requests.get("https://cloudflare-protected.com", impersonate="firefox120")
    

Để hoàn thiện module fetcher cho app truyện chữ của bạn, bạn có muốn tích hợp thêm:

  * Cơ chế tự động xoay vòng Proxy (Proxy Rotation) từ một danh sách có sẵn?
  * Cách trích xuất nội dung văn bản (Text) sạch sẽ từ HTML bằng các thư viện tốc độ cao như Selectolax?