`respx` là một thư viện Python chuyên dụng dùng để mock (giả lập) các yêu cầu HTTP được gửi từ thư viện `httpx`.

Nó được thiết kế nhằm phục vụ cho mục đích viết Unit Test (kiểm thử phần mềm). Khi test, bạn không muốn code của mình thực sự gửi request qua Internet đến server của bên thứ ba (vì sẽ làm test chạy chậm, tốn băng thông, phụ thuộc vào mạng và làm dữ liệu thử nghiệm bị sai lệch). `respx` sẽ chặn các request đó lại và trả về dữ liệu giả lập do bạn cấu hình.

* * *

## Cách hoạt động và Ví dụ minh họa

Hãy xem cách `respx` hoạt động thông qua một ví dụ kiểm thử cụ thể:

## 1\. Đoạn code thực tế cần test (app.py)

Giả sử bạn có một hàm lấy thông tin thời tiết từ một API bên ngoài bằng `httpx`:
    
    
    import httpx
    
    def get_weather(city: str):
        response = httpx.get(f"https://weather.com{city}")
        if response.status_code == 200:
            return response.json()
        return {"error": "Không thể lấy dữ liệu"}
    

## 2\. Đoạn code viết Test sử dụng `respx` (test_app.py)

Thay vì để `httpx.get` gọi lên `://weather.com` thật, bạn dùng `respx` để cấu hình sẵn kết quả trả về:
    
    
    import respx
    import httpx
    from app import get_weather
    
    # Sử dụng decorator @respx.mock để kích hoạt chế độ giả lập trong hàm test
    @respx.mock
    def test_get_weather_success():
        # 1. Định nghĩa: Nếu có request GET gửi đến URL này...
        # ... thì trả về mã 200 kèm nội dung JSON bên dưới.
        respx.get("https://weather.com").mock(
            return_value=httpx.Response(200, json={"temperature": "28C", "condition": "Sunny"})
        )
    
        # 2. Chạy hàm cần test
        result = get_weather("hanoi")
    
        # 3. Kiểm tra kết quả trả về có đúng như mong đợi không
        assert result["temperature"] == "28C"
        assert result["condition"] == "Sunny"
    

* * *

## Các tính năng nổi bật của `respx`

  * Hỗ trợ đầy đủ Async: Vì `httpx` nổi tiếng với khả năng xử lý bất đồng bộ (Asynchronous), `respx` cũng hỗ trợ mock hoàn hảo cho cả `httpx.Client` (đồng bộ) lẫn `httpx.AsyncClient` (bất đồng bộ).
  * Cú pháp rõ ràng, linh hoạt: Bạn có thể bắt request dựa trên nhiều tiêu chí như: URL, Method (GET, POST,...), Headers, Query Params hoặc Content body.
  * Tích hợp tốt với Pytest: Cung cấp sẵn một `fixture` tên là `respx_mock` giúp việc viết test với `pytest` trở nên cực kỳ gọn gàng.
  * Giả lập lỗi mạng dễ dàng: Bạn có thể bắt `respx` ném ra lỗi mạng (như lỗi `httpx.TimeoutException` mà bạn đã xử lý ở câu hỏi trước) để test xem code của bạn xử lý lỗi có đúng chuẩn không:
        
        respx.get("https://example.com").mock(side_effect=httpx.TimeoutException("Hết thời gian chờ"))
        




## So sánh nhanh với các thư viện khác

Thư viện| Thư viện HTTP đi kèm| Đặc điểm  
---|---|---  
`responses`| `requests`| Thư viện mock tiêu chuẩn dành cho `requests` (chỉ chạy đồng bộ).  
`respx`| `httpx`| Được thiết kế riêng cho `httpx`, hỗ trợ cả đồng bộ và bất đồng bộ (`async`/`await`).  
  
Nếu dự án của bạn đang dùng `httpx` để gọi API bên ngoài, thì `respx` là công cụ tốt nhất hiện tại để bạn viết Unit Test cho tầng kết nối đó.

Bạn có muốn tôi hướng dẫn cách tích hợp `respx` vào một test case cụ thể sử dụng `pytest`, hoặc cách giả lập mã lỗi 500 Internal Server Error để kiểm tra đoạn code xử lý lỗi `ExternalServiceUnavailable` trước đó của bạn không?