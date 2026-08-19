Khi viết **Unit Test**, nguyên tắc vàng là **không bao giờ gọi API thật ra bên ngoài internet**. Việc gọi API thật sẽ làm cho test bị chậm, không ổn định (flaky) do mạng, và có thể ảnh hưởng tới dữ liệu Production.

Để mock (giả lập) các HTTP request trong `httpx`, bạn có 2 giải pháp hàng đầu:

1. **`httpx.MockTransport`**: Có sẵn trực tiếp trong `httpx` (không cần cài thêm thư viện phụ).
2. **`respx`**: Thư viện chuyên dụng mạnh mẽ nhất dành riêng cho `httpx` (tương tự như `responses` của `requests`).

---

## Cách 1: Dùng `httpx.MockTransport` (Sẵn có, Zero-dependency)

`MockTransport` cho phép bạn tạo một Transport giả lập nhận vào một hàm callback `handler(request) -> response`. Mỗi khi `httpx` gửi request, thay vì đi ra internet, nó sẽ chạy qua hàm handler này.

### Ví dụ đơn giản:

```python
import httpx

# 1. Định nghĩa hàm xử lý request giả lập
def mock_handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/api/user/1":
        return httpx.Response(200, json={"id": 1, "name": "Alice"})
    elif request.url.path == "/api/user/99":
        return httpx.Response(404, json={"error": "User not found"})
    
    return httpx.Response(500, json={"error": "Internal Error"})

# 2. Truyền MockTransport vào Client
transport = httpx.MockTransport(mock_handler)

def test_get_user_success():
    with httpx.Client(transport=transport, base_url="https://api.example.com") as client:
        response = client.get("/api/user/1")
        assert response.status_code == 200
        assert response.json() == {"id": 1, "name": "Alice"}

def test_get_user_not_found():
    with httpx.Client(transport=transport, base_url="https://api.example.com") as client:
        response = client.get("/api/user/99")
        assert response.status_code == 404

```

### Giả lập Lỗi Mạng (Network Exceptions):

Bạn cũng có thể bắt handler quăng ra lỗi (ví dụ `httpx.TimeoutException`) để test logic xử lý lỗi:

```python
def timeout_handler(request: httpx.Request):
    raise httpx.ReadTimeout("Server không phản hồi", request=request)

def test_api_timeout():
    transport = httpx.MockTransport(timeout_handler)
    client = httpx.Client(transport=transport)
    
    import pytest
    with pytest.raises(httpx.ReadTimeout):
        client.get("https://api.example.com/data")

```

---

## Cách 2: Dùng thư viện `respx` (Tiêu chuẩn Production cho `pytest`)

**`respx`** là công cụ mock mạnh mẽ nhất được thiết kế riêng cho `httpx`. Nó cho phép bạn chặn (intercept) request theo URL, HTTP Method, Headers, Params... bằng cú pháp vô cùng đẹp mắt.

### Cài đặt:

```bash
pip install respx pytest

```

### A. Dùng Decorator `@respx.mock`

```python
import httpx
import pytest
import respx

# Giả sử đây là hàm nghiệp vụ trong mã nguồn ứng dụng của bạn
def get_github_user(username: str) -> dict:
    response = httpx.get(f"https://api.github.com/users/{username}")
    response.raise_for_status()
    return response.json()

# Viết Unit Test
@respx.mock
def test_get_github_user_success():
    # 1. Đăng ký mock route
    respx.get("https://api.github.com/users/octocat").mock(
        return_value=httpx.Response(200, json={"login": "octocat", "id": 583231})
    )

    # 2. Gọi hàm thực tế
    user_data = get_github_user("octocat")

    # 3. Assert kết quả
    assert user_data["login"] == "octocat"
    assert user_data["id"] == 583231

@respx.mock
def test_get_github_user_404():
    # Mock lỗi 404
    respx.get("https://api.github.com/users/notfounduser").mock(
        return_value=httpx.Response(404)
    )

    with pytest.raises(httpx.HTTPStatusError):
        get_github_user("notfounduser")

```

### B. Kiểm tra Request Parameters (Verify Request Data)

`respx` giúp bạn assert xem mã nguồn của mình có gửi đúng **Headers**, **Query String** hoặc **JSON Body** lên server hay không:

```python
import httpx
import respx

@respx.mock
def test_create_post():
    # Mock endpoint POST
    route = respx.post("https://httpbin.org/post").mock(
        return_value=httpx.Response(201, json={"status": "created"})
    )

    # Chạy code gửi request
    client = httpx.Client()
    client.post("https://httpbin.org/post", json={"title": "Hello httpx"})

    # Assert 1: Kiểm tra endpoint đã thực sự được gọi chưa
    assert route.called
    assert route.call_count == 1

    # Assert 2: Kiểm tra dữ liệu JSON gửi đi có chính xác không
    last_request = route.calls.last.request
    import json
    assert json.loads(last_request.content) == {"title": "Hello httpx"}

```

### C. Dùng `respx` trong Async Unit Test (với `pytest-asyncio`)

`respx` hỗ trợ mã bất đồng bộ (Async) 100% tự nhiên:

```python
import httpx
import pytest
import respx

async def fetch_data_async():
    async with httpx.AsyncClient() as client:
        res = await client.get("https://api.example.com/items")
        return res.json()

@pytest.mark.asyncio
@respx.mock
async def test_fetch_data_async():
    respx.get("https://api.example.com/items").mock(
        return_value=httpx.Response(200, json=["item1", "item2"])
    )

    data = await fetch_data_async()
    assert len(data) == 2
    assert data[0] == "item1"

```

---

## Bảng so sánh lựa chọn

| Tiêu chí | `httpx.MockTransport` | `respx` |
| --- | --- | --- |
| **Thư viện ngoài** | Không cần | Cần `pip install respx` |
| **Cú pháp** | Tự viết `if/else` thủ công | Khai báo Fluent API ngắn gọn (`respx.get(...)`) |
| **Assert Call Counter** | Phải tự đếm biến | Tích hợp sẵn (`route.called`, `call_count`) |
| **Phù hợp cho** | Script nhỏ, Unit test cơ bản | **Dự án Production vừa và lớn** |