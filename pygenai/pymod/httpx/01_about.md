Chào bạn! Mình rất vui được đồng hành cùng bạn. Nếu bạn đã từng dùng thư viện **`requests`** huyền thoại trong Python, thì việc tiếp cận **`httpx`** sẽ cực kỳ tự nhiên.

Có thể xem **`httpx`** là phiên bản "nâng cấp toàn diện" của `requests` dành cho Python hiện đại.

---

## Tại sao `httpx` lại được yêu thích?

Trước đây, cộng đồng Python thường bị chia làm 2 phe:

* Dùng **`requests`** khi viết mã đồng bộ (Synchronous) đơn giản.
* Dùng **`aiohttp`** khi viết mã bất đồng bộ (Asynchronous - `async`/`await`) để xử lý hàng ngàn request cùng lúc.

`httpx` xuất hiện để giải quyết sự phân mảnh này. Nó mang lại:

1. **Cú pháp quen thuộc:** Gần như giống `requests` 90%.
2. **Hỗ trợ cả Sync lẫn Async:** Viết mã dạng nào cũng được.
3. **Hỗ trợ HTTP/2:** Giúp gửi/nhận dữ liệu nhanh hơn trên các server hiện đại.
4. **Strict Typing:** Tích hợp sẵn Type Hints giúp Autocomplete chuẩn xác trong VS Code/PyCharm.

---

## Bắt đầu cài đặt

```bash
pip install httpx

# Nếu muốn dùng tính năng HTTP/2, bạn cài thêm extension:
pip install httpx[http2]

```

---

## 3 Cách dùng phổ biến nhất

### 1. Request đồng bộ (Sync) – Giống hệt `requests`

Dành cho các script đơn giản, crawl dữ liệu nhỏ hoặc chạy nối tiếp.

```python
import httpx

# Gửi GET request
response = httpx.get("https://httpbin.org/get")

print("Status Code:", response.status_code)
print("Headers:", response.headers["content-type"])
print("JSON Data:", response.json())

```

### 2. Request bất đồng bộ (Async) – "Vũ khí hạng nặng"

Khi bạn cần gọi nhiều API cùng lúc mà không muốn chương trình bị block (tắc nghẽn) chờ phản hồi.

```python
import asyncio
import httpx

async def fetch_data():
    # Sử dụng AsyncClient làm Context Manager
    async with httpx.AsyncClient() as client:
        response = await client.get("https://httpbin.org/get")
        print("Status Code:", response.status_code)
        print("Response:", response.json())

# Chạy hàm async trong Python
asyncio.run(fetch_data())

```

### 3. Tái sử dụng kết nối với `Client` (Connection Pooling)

Nếu bạn gọi nhiều request tới cùng một server, tạo một `Client` giúp giữ lại kết nối TCP (TCP keep-alive), giúp tăng tốc đáng kể.

```python
import httpx

# Tự động đóng kết nối khi thoát khỏi khối with
with httpx.Client(base_url="https://httpbin.org") as client:
    r1 = client.get("/get")
    r2 = client.post("/post", json={"user": "admin"})
    
    print(r1.status_code, r2.status_code)

```

---

## Bảng so sánh nhanh

| Tiêu chí | `requests` | `aiohttp` | `httpx` |
| --- | --- | --- | --- |
| **Đồng bộ (Sync)** | Có | Không | **Có** |
| **Bất đồng bộ (Async)** | Không | Có | **Có** |
| **Hỗ trợ HTTP/2** | Không | Không | **Có** |
| **Cú pháp API** | Rất dễ | Hơi rườm rà | **Rất dễ** |