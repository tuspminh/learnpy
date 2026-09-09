Trong quá trình phát triển ứng dụng (đặc biệt là hệ thống microservices hoặc crawler), việc ghi log (logging) toàn bộ các lượt gửi/nhận HTTP request là cực kỳ quan trọng để **debug**, **giám sát hiệu năng (latency)**, và **audit trail**.

Trong `httpx`, bạn có 2 giải pháp mạnh mẽ để thực hiện việc này hoàn toàn tự động mà không cần chèn mã log ở từng câu lệnh gọi API:

1. **Event Hooks:** Đơn giản, dễ viết, phù hợp cho hầu hết nhu cầu logging.
2. **Custom Transport:** Can thiệp sâu ở tầng gửi nhận, đo thời gian phản hồi (latency) cực kỳ chính xác.

---

## 1. Event Hooks (Cách đơn giản & phổ biến nhất)

`httpx` cung cấp sẵn 2 điểm chặn (event hooks):

* `'request'`: Gọi **ngay trước khi** request được gửi đi.
* `'response'`: Gọi **ngay sau khi** nhận được response từ server.

### Mẫu Code Event Hooks (Synchronous)

```python
import httpx
import logging

# Cấu hình logging cơ bản
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def log_request(request: httpx.Request):
    """Callback chạy trước khi gửi Request"""
    logging.info(f"📤 [REQUEST] {request.method} {request.url}")
    # Bạn có thể log thêm headers hoặc body nếu muốn
    # logging.info(f"Headers: {dict(request.headers)}")

def log_response(response: httpx.Response):
    """Callback chạy sau khi nhận Response"""
    request = response.request
    logging.info(f"📥 [RESPONSE] {request.method} {request.url} - Status: {response.status_code}")

# Đăng ký hooks vào Client
client = httpx.Client(
    event_hooks={
        "request": [log_request],
        "response": [log_response]
    }
)

# Chạy thử
client.get("https://httpbin.org/get")
client.post("https://httpbin.org/post", json={"hello": "world"})

```

### Mẫu Code Event Hooks (Asynchronous)

Đối với `AsyncClient`, các hàm hook có thể là hàm **`async def`**:

```python
import asyncio
import httpx
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

async def async_log_request(request: httpx.Request):
    logging.info(f"📤 [ASYNC REQ] {request.method} {request.url}")

async def async_log_response(response: httpx.Response):
    # Đọc nội dung response nếu cần (dùng aread)
    await response.aread()
    logging.info(f"📥 [ASYNC RES] {response.status_code} - Body size: {len(response.content)} bytes")

async def main():
    async with httpx.AsyncClient(
        event_hooks={
            "request": [async_log_request],
            "response": [async_log_response]
        }
    ) as client:
        await client.get("https://httpbin.org/get")

asyncio.run(main())

```

---

## 2. Custom Transport (Đo chính xác Latency / Can thiệp sâu)

Nếu bạn muốn **đo độ trễ (execution time)** của từng request một cách chính xác nhất hoặc muốn đóng gói logic này thành một Middleware dùng lại ở nhiều dự án, hãy kế thừa `httpx.HTTPTransport` (hoặc `httpx.AsyncHTTPTransport`).

### Mẫu Code Custom Logging Transport

```python
import time
import logging
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

class LoggingHTTPTransport(httpx.HTTPTransport):
    """Custom Transport ghi log và tính chính xác milisecond thời gian phản hồi"""
    
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        start_time = time.perf_counter()
        
        logging.info(f"🚀 [START] {request.method} {request.url}")
        
        # Gọi transport gốc để thực hiện kết nối HTTP
        response = super().handle_request(request)
        
        # Tính thời gian xử lý (Latency)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        logging.info(
            f"✅ [DONE] {request.method} {request.url} "
            f"| Status: {response.status_code} | Time: {elapsed_ms:.2f}ms"
        )
        return response

# Khởi tạo client với custom transport
client = httpx.Client(transport=LoggingHTTPTransport())

# Chạy thử
response = client.get("https://httpbin.org/delay/1")

```

---

## 3. Best Practices khi viết Log cho HTTP Requests

When triển khai ghi log trên Production, bạn nên lưu ý 3 nguyên tắc quan trọng sau:

### A. Che giấu thông tin nhạy cảm (Sanitize / Masking)

Không bao giờ log lộ các thông tin như `Authorization`, `Cookie`, `X-API-Key` hay mật khẩu trong JSON payload.

```python
def sanitize_headers(headers: httpx.Headers) -> dict:
    masked = dict(headers)
    SENSITIVE_KEYS = ["authorization", "cookie", "x-api-key"]
    for key in masked:
        if key.lower() in SENSITIVE_KEYS:
            masked[key] = "****** [MASKED] ******"
    return masked

```

### B. Cẩn thận với Streaming Response

Trong Event Hook hay Transport, nếu bạn gọi `response.read()` hoặc `response.text` đối với các request dạng **Stream** (ví dụ file download lớn), nó sẽ đọc kiệt stream và khiến ứng dụng không đọc được dữ liệu ở bước tiếp theo.

* **Giải pháp:** Chỉ log `status_code`, `headers`, `url` hoặc kiểm tra header `Content-Type` xem có phải JSON/Text trước khi đọc body.

---

## So sánh nhanh

| Tiêu chí | Event Hooks | Custom Transport |
| --- | --- | --- |
| **Độ phức tạp** | Rất đơn giản, dễ học | Cần hiểu về OO / Class inheritance |
| **Đo Latency (Thời gian)** | Tương đối (cần lưu timestamp tạm) | **Cực kỳ chính xác** |
| **Trường hợp sử dụng** | Log đơn giản, gửi thông báo | Middleware doanh nghiệp, APM Tracing |