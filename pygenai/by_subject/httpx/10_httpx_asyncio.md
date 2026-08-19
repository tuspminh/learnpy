Gửi hàng chục (hoặc hàng trăm) HTTP request song song là "vũ khí mạnh nhất" của **`httpx`** kết hợp với **`asyncio`**. Trong các tác vụ I/O Bound (chờ mạng phản hồi), kỹ thuật này giúp bạn giảm thời gian chạy từ vài phút xuống chỉ còn vài giây.

Dưới đây là từ cơ bản đến nâng cao để bạn làm chủ kỹ thuật này.

---

## 1. Cơ bản: Dùng `asyncio.gather` gửi song song

Phương pháp đơn giản nhất là khởi tạo danh sách các Coroutine và gom chúng lại bằng `asyncio.gather()`.

```python
import asyncio
import time
import httpx

async def fetch_url(client: httpx.AsyncClient, url: str) -> int:
    response = await client.get(url)
    return response.status_code

async def main():
    # Giả lập 20 URLs (mỗi request server sẽ delay 1 giây)
    urls = [f"https://httpbin.org/delay/1" for _ in range(20)]
    
    start_time = time.perf_counter()
    
    # Dùng chung 1 AsyncClient cho tất cả các request
    async with httpx.AsyncClient() as client:
        # 1. Tạo danh sách công việc (Tasks)
        tasks = [fetch_url(client, url) for url in urls]
        
        # 2. Chạy tất cả song song và chờ nhận toàn bộ kết quả
        results = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start_time
    print(f"✅ Hoàn thành {len(results)} requests trong {elapsed:.2f} giây!")

asyncio.run(main())

```

> 💡 **So sánh hiệu năng:** Nếu chạy nối tiếp (Sync), 20 request delay 1s sẽ mất **~20 giây**. Nhưng với `asyncio.gather`, tất cả chạy cùng lúc và chỉ mất **~1.2 giây**!

---

## 2. Nâng cao: Khống chế số lượng request cùng lúc với `asyncio.Semaphore`

Nếu bạn gửi 1,000 request **cùng một thời điểm**, server đối phương có thể coi bạn là tấn công DDoS và trả về mã lỗi `429 Too Many Requests` hoặc khoá IP của bạn.

Dùng **`asyncio.Semaphore`** để đặt ra giới hạn (Throttle / Rate Limit), ví dụ: *"Chỉ cho phép tối đa 5 request chạy cùng lúc, các request còn lại phải xếp hàng chờ"*.

```python
import asyncio
import httpx

async def fetch_with_semaphore(client: httpx.AsyncClient, url: str, semaphore: asyncio.Semaphore):
    # Khóa semaphore: Chỉ cho phép N coroutine vào đây cùng lúc
    async with semaphore:
        response = await client.get(url)
        print(f"Đã tải xong: {url} | Status: {response.status_code}")
        return response.json()

async def main():
    urls = [f"https://httpbin.org/get?id={i}" for i in range(50)]
    
    # 🛑 Giới hạn: Tối đa 5 request đồng thời tại MỌI THỜI ĐIỂM
    semaphore = asyncio.Semaphore(5)
    
    async with httpx.AsyncClient() as client:
        tasks = [fetch_with_semaphore(client, url, semaphore) for url in urls]
        results = await asyncio.gather(*tasks)

asyncio.run(main())

```

---

## 3. Quản lý Connection Pool với `httpx.Limits`

Mặc định `httpx.AsyncClient` mở tối đa **100 kết nối đồng thời** (Max Connections) và **20 kết nối giữ lại** (Keep-Alive). Bạn có thể điều chỉnh tham số này cho phù hợp với cấu hình máy và server:

```python
import httpx

# Cấu hình Connection Pool cho Client
limits = httpx.Limits(
    max_connections=50,          # Tối đa 50 kết nối mở cùng lúc
    max_keepalive_connections=10 # Giữ 10 kết nối mở sẵn để tái sử dụng
)

client = httpx.AsyncClient(limits=limits)

```

---

## 4. Chuẩn Python 3.11+: Dùng `asyncio.TaskGroup`

Nếu bạn đang dùng **Python 3.11 trở lên**, `asyncio.TaskGroup` là cách viết hiện đại thay thế cho `asyncio.gather()`. Ưu điểm của nó là **an toàn tuyệt đối về Exception** (nếu 1 task bị lỗi, các task còn lại sẽ tự động cancelled an toàn).

```python
import asyncio
import httpx

async def fetch_task(client: httpx.AsyncClient, url: str, results: list):
    res = await client.get(url)
    results.append(res.status_code)

async def main():
    urls = [f"https://httpbin.org/get?id={i}" for i in range(10)]
    results = []

    async with httpx.AsyncClient() as client:
        # Sử dụng TaskGroup chuẩn Python 3.11+
        async with asyncio.TaskGroup() as tg:
            for url in urls:
                tg.create_task(fetch_task(client, url, results))

    print("Kết quả:", results)

asyncio.run(main())

```

---

## 📋 Tóm tắt Best Practices khi gọi Concurrency

1. **Luôn tái sử dụng `httpx.AsyncClient`:** Tạo 1 Client duy nhất và dùng chung cho tất cả các task thay vì khởi tạo client mới trong từng hàm.
2. **Luôn dùng `Semaphore`:** Tránh bị Server block IP hoặc ăn lỗi `429 Too Many Requests`.
3. **Thêm `timeout` hợp lý:** Tránh trường hợp 1 request bị treo làm nghẽn toàn bộ ứng dụng.