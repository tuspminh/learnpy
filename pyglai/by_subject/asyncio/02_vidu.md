Dưới đây là script chuẩn chỉnh để cào dữ liệu song song từ nhiều API bằng `asyncio` và `httpx`, kết hợp xử lý lỗi và kiểm soát lưu lượng request.

Trước khi chạy, cài đặt thư viện:

```bash
pip install httpx

```

### Script cào API đồng thời

```python
import asyncio
import time
import httpx

# Danh sách các API endpoint mẫu (Sử dụng JSONPlaceholder)
URLS = [f"https://jsonplaceholder.typicode.com/posts/{i}" for i in range(1, 16)]

async def fetch_api(client: httpx.AsyncClient, url: str, semaphore: asyncio.Semaphore):
    """
    Gửi request đến endpoint API và xử lý ngoại lệ.
    """
    # Sử dụng Semaphore để giới hạn số request chạy đồng thời cùng lúc
    async with semaphore:
        try:
            response = await client.get(url, timeout=5.0)
            response.raise_for_status()  # Ném lỗi nếu status code là 4xx hoặc 5xx
            
            data = response.json()
            print(f"[Thành công {response.status_code}] URL: {url} | Title: {data['title'][:20]}...")
            return data

        except httpx.HTTPStatusError as exc:
            print(f"[Lỗi HTTP {exc.response.status_code}] URL: {url}")
        except httpx.RequestError as exc:
            print(f"[Lỗi Kết nối] URL: {url} - Chi tiết: {exc}")
        except Exception as exc:
            print(f"[Lỗi Không xác định] URL: {url} - {exc}")
            
        return None

async def main():
    start_time = time.time()
    
    # 1. Giới hạn tối đa 5 request gửi đi cùng lúc (Tránh bị Rate Limit / Khóa IP)
    semaphore = asyncio.Semaphore(5)
    
    # 2. Khởi tạo AsyncClient làm Context Manager để dùng chung Connection Pool
    async with httpx.AsyncClient() as client:
        # Tạo danh sách các task bất đồng bộ
        tasks = [fetch_api(client, url, semaphore) for url in URLS]
        
        # 3. Chạy tất cả các task đồng thời
        results = await asyncio.gather(*tasks)
        
    # Lọc bỏ các kết quả bị lỗi (None)
    successful_results = [res for res in results if res is not None]
    
    elapsed = time.time() - start_time
    print(f"\n--- Hoàn tất ---")
    print(f"Tổng số request: {len(URLS)}")
    print(f"Thành công: {len(successful_results)}")
    print(f"Tổng thời gian: {elapsed:.2f} giây")

if __name__ == "__main__":
    asyncio.run(main())

```

---

### Kỹ thuật tối ưu cốt lõi trong Script

* **Tái sử dụng `httpx.AsyncClient()**`: Việc khởi tạo duy nhất 1 `AsyncClient` trong hàm `main` giúp tái sử dụng lại HTTP connections (Connection Pooling), giảm đáng kể chi phí bắt tay TCP/TLS so với việc tạo client mới ở từng request.
* **Kiểm soát bằng `asyncio.Semaphore(5)**`: Giúp giới hạn số lượng request đang hoạt động đồng thời. Nếu bạn gửi 1,000 request cùng lúc mà không dùng Semaphore, IP của bạn rất dễ bị server phản đòn bằng lỗi `429 Too Many Requests` hoặc chặn vĩnh viễn.
* **Xử lý ngoại lệ cô lập (`try...except`)**: Nếu 1 URL bị timeout hoặc trả về lỗi 500, lỗi đó được bắt riêng lẻ và không làm sập toàn bộ các task còn lại trong `asyncio.gather`.