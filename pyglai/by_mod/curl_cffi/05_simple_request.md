Để tạo một request đơn giản nhất bằng `curl_cffi` (không cần viết class hay cấu hình phức tạp), bạn có thể sử dụng trực tiếp hàm `requests.get` hoặc `requests.post` tương tự như thư viện `requests` truyền thống.

Dưới đây là mã nguồn mẫu cho cả 2 phiên bản Đồng bộ (Sync) và Bất đồng bộ (Async):

## 1\. Phiên bản Đồng bộ (Sync) – Đơn giản nhất

Chỉ cần import `requests` từ `curl_cffi` và truyền thêm tham số `impersonate` để giả mạo trình duyệt.
    
    
    from curl_cffi import requests
    
    # Gửi một GET Request đơn giản giả mạo Chrome
    response = requests.get("https://httpbin.org", impersonate="chrome")
    
    # In kết quả
    print(f"Status Code: {response.status_code}")
    print("Nội dung phản hồi:")
    print(response.text)
    

## 2\. Phiên bản Bất đồng bộ (Async)

Nếu bạn đang chạy trong môi trường `asyncio`, hãy import `requests` từ `curl_cffi.requests`.
    
    
    import asyncio
    from curl_cffi.requests import requests
    
    async def main():
        # Gửi GET Request bất đồng bộ
        response = await requests.get("https://httpbin.org", impersonate="chrome")
        
        print(f"Status Code: {response.status_code}")
        print(response.text)
    
    # Chạy hàm async
    asyncio.run(main())
    

## 3\. Gửi kèm Headers, Params hoặc POST Data

Khi cần truyền thêm dữ liệu, cấu trúc viết hoàn toàn giống với thư viện `requests` quen thuộc:
    
    
    from curl_cffi import requests
    
    url = "https://httpbin.org"
    headers = {"Custom-Header": "value"}
    data = {"username": "crawl_user", "page": 1}
    
    # Gửi POST request kèm form data và fake vân tay trình duyệt Edge
    response = requests.post(
        url, 
        headers=headers, 
        data=data, 
        impersonate="edge", 
        timeout=10
    )
    
    print(response.json())
    

Bạn có muốn thử nghiệm request này trên một trang web cụ thể nào đang chặn bot không, hay bạn cần hướng dẫn cách trích xuất dữ liệu JSON / HTML từ phản hồi trả về?