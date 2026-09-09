Trong môi trường mạng, request thất bại do đứt cáp, server quá tải (502/503) hoặc phản hồi chậm là chuyện xảy ra như cơm bữa. Việc xử lý lỗi, thiết lập Timeout và Retry sẽ giúp ứng dụng của bạn **kiên cường (robust)** hơn rất nhiều.

Dưới đây là hướng dẫn chi tiết từng phần cho `httpx`.

---

## 1. Bắt lỗi (Error Handling)

Hệ thống ngoại lệ (Exception) của `httpx` được thiết kế rất khoa học với cây phân cấp rõ ràng:

```text
httpx.HTTPError (Lỗi gốc)
 ├── httpx.RequestError (Lỗi kết nối: DNS, Timeout, mất mạng...)
 └── httpx.HTTPStatusError (Lỗi HTTP: 4xx, 5xx khi gọi raise_for_status())

```

### Mã mẫu bắt lỗi chuẩn:

```python
import httpx

try:
    response = httpx.get("https://httpbin.org/status/404", timeout=5.0)
    # Bắt buộc quăng Exception nếu status code là 4xx hoặc 5xx
    response.raise_for_status() 
    print("Thành công:", response.json())

except httpx.TimeoutException:
    print("❌ Lỗi: Server phản hồi quá chậm (Timeout)!")

except httpx.ConnectError:
    print("❌ Lỗi: Không thể kết nối tới Server (Sai URL hoặc rớt mạng)!")

except httpx.HTTPStatusError as exc:
    print(f"❌ Lỗi HTTP {exc.response.status_code}: {exc.response.url}")

except httpx.RequestError as exc:
    print(f"❌ Lỗi đường truyền chung: {exc}")

except httpx.HTTPError as exc:
    print(f"❌ Lỗi httpx tổng quát: {exc}")

```

---

## 2. Cấu hình Timeout

> ⚠️ **Lưu ý quan trọng:** Thư viện `requests` mặc định **không có timeout** (khiến app dễ bị treo vô thời hạn). Trái lại, `httpx` **mặc định timeout 5.0 giây** cho tất cả các tác vụ.

Bạn có thể tùy chỉnh timeout theo 2 mức độ:

### Cấu hình đơn giản

Truyền số giây trực tiếp vào request hoặc Client:

```python
# Timeout 10 giây cho 1 request
response = httpx.get("https://httpbin.org/delay/2", timeout=10.0)

# Hoặc thiết lập cho toàn bộ Client
with httpx.Client(timeout=10.0) as client:
    res = client.get("https://httpbin.org/get")

```

### Cấu hình nâng cao (Fine-grained Timeout)

Chia nhỏ timeout cho từng giai đoạn kết nối bằng `httpx.Timeout`:

```python
import httpx

custom_timeout = httpx.Timeout(
    connect=2.0,  # Tối đa 2s để bắt tay (handshake) kết nối TCP/SSL
    read=5.0,     # Tối đa 5s chờ nhận dữ liệu từ server
    write=5.0,    # Tối đa 5s để gửi dữ liệu đi
    pool=10.0     # Tối đa 10s chờ lấy connection trống từ connection pool
)

client = httpx.Client(timeout=custom_timeout)

```

---

## 3. Retry tự động (Automatic Retries)

### Cách 1: Sử dụng tính năng có sẵn của `httpx` (Tốt cho lỗi đường truyền)

`httpx` hỗ trợ sẵn tính năng retry ở tầng **Transport**. Nó sẽ tự động thử lại khi gặp các lỗi mạng ngắn hạn (DNS, ngắt kết nối TCP, Timeout):

```python
import httpx

# Tự động retry tối đa 3 lần nếu lỗi kết nối mạng
transport = httpx.HTTPTransport(retries=3)

with httpx.Client(transport=transport) as client:
    try:
        response = client.get("https://httpbin.org/get")
        print(response.status_code)
    except httpx.RequestError:
        print("Đã thử lại 3 lần nhưng vẫn thất bại!")

```

*(Đối với `AsyncClient`, bạn dùng `httpx.AsyncHTTPTransport(retries=3)`)*.

### Cách 2: Kết hợp với thư viện `tenacity` (Chuẩn Production cho lỗi 5xx)

Nếu bạn muốn retry **cả khi Server trả về mã lỗi 502, 503, 504**, giải pháp mạnh mẽ nhất trong ecosystem của Python là dùng thêm thư viện `tenacity`.

```bash
pip install tenacity

```

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Định nghĩa hàm gọi API với decorator retry
@retry(
    stop=stop_after_attempt(3),                   # Thử tối đa 3 lần
    wait=wait_exponential(multiplier=1, min=2, max=10), # Chờ tăng dần: 2s, 4s, 8s...
    retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)) # Điều kiện retry
)
def fetch_api_safe(url: str):
    print(f"Đang gọi API: {url}...")
    response = httpx.get(url, timeout=3.0)
    response.raise_for_status() # Đẩy lỗi ra để tenacity phát hiện và retry
    return response.json()

# Chạy thử
try:
    # URL này trả về lỗi 500
    data = fetch_api_safe("https://httpbin.org/status/500")
    print(data)
except httpx.HTTPStatusError:
    print("❌ Thất bại hoàn toàn sau 3 lần retry!")

```

---

## Tổng kết mẫu code hoàn chỉnh

Dưới đây là bộ khung chuẩn cho một **Async Client** sẵn sàng cho môi trường Production:

```python
import asyncio
import httpx

async def main():
    # 1. Cấu hình Timeout & Transport Retries cho lỗi mạng
    timeout = httpx.Timeout(connect=3.0, read=10.0, write=5.0, pool=5.0)
    transport = httpx.AsyncHTTPTransport(retries=2)

    async with httpx.AsyncClient(timeout=timeout, transport=transport) as client:
        try:
            response = await client.get("https://httpbin.org/get")
            response.raise_for_status()
            print("Status:", response.status_code)
            print("Data:", response.json())

        except httpx.TimeoutException:
            print("Request bị quá thời gian cho phép!")
        except httpx.HTTPStatusError as exc:
            print(f"Server trả về mã lỗi: {exc.response.status_code}")
        except httpx.RequestError as exc:
            print(f"Lỗi mạng không thể phục hồi: {exc}")

asyncio.run(main())

```