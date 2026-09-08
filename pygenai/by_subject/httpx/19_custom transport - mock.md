Viết Unit Test cho các dịch vụ gửi HTTP request yêu cầu **không thực hiện request thật ra ngoài Internet** nhằm đảm bảo test chạy nhanh, độc lập và ổn định.

Để kiểm thử `HTTPX`, hai phương pháp chuẩn mực nhất là:

1. **Dùng thư viện `respx`:** Mock/Intercept các request HTTP bằng cách giả lập response (Khuyên dùng cho hầu hết các bài test).
2. **Tự viết `Custom Transport` (`httpx.BaseTransport`):** Can thiệp sâu vào tầng mạng của HTTPX để giả lập hành vi hệ thống hoặc test lỗi đường truyền phức tạp.

---

## Phần 1: Mock HTTPX bằng `RESPX` và `pytest`

`RESPX` là thư viện mock dành riêng cho HTTPX, hỗ trợ cả `httpx.Client` (sync) và `httpx.AsyncClient` (async).

### 1. Cài đặt

```bash
pip install pytest pytest-asyncio respx httpx

```

### 2. Hàm ứng dụng cần Test (`app/services.py`)

Giả sử bạn có hàm async cào dữ liệu thời tiết dưới đây:

```python
import httpx

async def get_weather(city: str) -> dict:
    url = f"https://api.weather.com/v1/{city}"
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

```

### 3. Viết Unit Test với `respx` (`tests/test_weather.py`)

#### A. Cách 1: Sử dụng Decorator `@respx.mock`

Cách này sẽ chặn toàn bộ các request HTTP phát sinh trong hàm test.

```python
import pytest
import httpx
import respx
from app.services import get_weather

@pytest.mark.asyncio
@respx.mock
async def test_get_weather_success():
    # 1. Định nghĩa mock: Khi có request GET tới URL này, trả về JSON giả lập với Status 200
    mock_route = respx.get("https://api.weather.com/v1/hanoi").mock(
        return_value=httpx.Response(200, json={"city": "Hanoi", "temp": 30})
    )

    # 2. Gọi hàm cần test
    data = await get_weather("hanoi")

    # 3. Assert kết quả trả về
    assert data["temp"] == 30
    assert data["city"] == "Hanoi"
    
    # 4. Kiểm tra xem route đã được gọi đúng 1 lần hay chưa
    assert mock_route.called
    assert mock_route.call_count == 1

```

#### B. Cách 2: Test trường hợp Server trả về Lỗi (HTTP 404 / 500)

```python
@pytest.mark.asyncio
@respx.mock
async def test_get_weather_not_found():
    # Mock trường hợp server trả về lỗi 404
    respx.get("https://api.weather.com/v1/unknown").mock(
        return_value=httpx.Response(404, json={"detail": "City not found"})
    )

    # Kiểm tra xem hàm có bắn ra HTTPStatusError đúng như mong đợi không
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await get_weather("unknown")
    
    assert exc_info.value.response.status_code == 404

```

#### C. Cách 3: Test lỗi Kết nối / Timeout (Network Exception)

```python
@pytest.mark.asyncio
@respx.mock
async def test_get_weather_timeout():
    # Mock trường hợp bị Timeout
    respx.get("https://api.weather.com/v1/hanoi").mock(
        side_effect=httpx.TimeoutException("Connection timed out")
    )

    with pytest.raises(httpx.TimeoutException):
        await get_weather("hanoi")

```

---

## Phần 2: Viết Custom Transport (`httpx.AsyncBaseTransport`)

Trong HTTPX, mọi thao tác gửi nhận byte thực sự đều đi qua một lớp gọi là **Transport**. Bạn có thể kế thừa `httpx.AsyncBaseTransport` (hoặc `httpx.BaseTransport` cho Sync) để tự quyết định cách HTTPX xử lý request mà không cần đụng tới card mạng.

### 1. Xây dựng Mock Transport tùy chỉnh

```python
import httpx
import pytest

class MockDatabaseTransport(httpx.AsyncBaseTransport):
    """
    Custom Transport giả lập việc trả về dữ liệu trực tiếp 
    mà không gửi request qua Internet.
    """
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        # Kiểm tra URL request gửi đến
        if request.url.path == "/api/v1/status":
            return httpx.Response(
                status_code=200,
                json={"status": "ok", "db": "connected"},
                headers={"content-type": "application/json"}
            )
        
        elif request.url.path == "/api/v1/error":
            return httpx.Response(status_code=500, text="Internal Server Error")
        
        # Nếu URL không khớp, trả về 404
        return httpx.Response(status_code=404, json={"message": "Not Found"})

```

### 2. Sử dụng Custom Transport trong Unit Test

Bạn truyền instance của Custom Transport vào tham số `transport` khi khởi tạo `httpx.AsyncClient`:

```python
@pytest.mark.asyncio
async def test_custom_transport_success():
    # Khởi tạo client với Custom Transport đã tạo
    async with httpx.AsyncClient(transport=MockDatabaseTransport()) as client:
        response = await client.get("https://fake-domain.com/api/v1/status")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "db": "connected"}

@pytest.mark.asyncio
async def test_custom_transport_not_found():
    async with httpx.AsyncClient(transport=MockDatabaseTransport()) as client:
        response = await client.get("https://fake-domain.com/invalid-path")
        
        assert response.status_code == 404

```

---

## 3. Custom Transport thực tế: `httpx.ASGITransport`

Nếu bạn viết Web API bằng **FastAPI** hoặc **Starlette**, HTTPX có sẵn một Custom Transport cực kỳ mạnh mẽ tên là `ASGITransport`. Nó cho phép bạn test ứng dụng FastAPI trực tiếp trong bộ nhớ mà **không cần bật server uvicorn**.

```python
from fastapi import FastAPI
import httpx
import pytest

# 1. Giả sử đây là app FastAPI của bạn
app = FastAPI()

@app.get("/hello")
async def hello():
    return {"message": "Hello World"}

# 2. Viết Test gọi trực tiếp app FastAPI qua ASGITransport
@pytest.mark.asyncio
async def test_fastapi_app_directly():
    # Khởi tạo ASGITransport trỏ tới app FastAPI
    transport = httpx.ASGITransport(app=app)
    
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/hello")
        
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}

```

---

## 💡 So sánh khi nào nên dùng gì?

| Tiêu chí | `respx` (Mocking Library) | `Custom Transport` |
| --- | --- | --- |
| **Mục đích** | Mock request HTTP cho các dịch vụ bên thứ 3 (Third-party APIs) | Can thiệp sâu vào luồng HTTP hoặc Test trực tiếp app WSGI/ASGI (FastAPI/Flask) |
| **Độ linh hoạt** | Rất cao, hỗ trợ kiểm tra xem route đã được gọi bao nhiêu lần, tham số ra sao | Tự do ghi đè logic xử lý request ở mức byte/stream |
| **Độ phức tạp mã** | Rất ngắn gọn và dễ đọc | Cần viết thêm class và override phương thức `handle_async_request` |