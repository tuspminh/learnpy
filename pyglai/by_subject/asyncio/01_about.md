Trong Python, `asyncio` là thư viện tiêu chuẩn dùng để xử lý **lập trình bất đồng bộ (asynchronous programming)**. Nó đặc biệt hiệu quả cho các tác vụ **I/O-bound** (như gọi API, cào dữ liệu web, đọc/ghi cơ sở dữ liệu) vì giúp chương trình không bị gián đoạn (block) trong lúc chờ phản hồi.

**3 Khái niệm cốt lõi:**

* **Coroutine (`async def`)**: Hàm bất đồng bộ có khả năng tạm dừng và khôi phục thực thi.
* **`await`**: Từ khóa đặt trước một coroutine để báo cho Python: *"Trong lúc chờ tác vụ này xong, hãy nhường CPU đi làm việc khác."*
* **Event Loop (Vòng lặp sự kiện)**: Bộ điều phối trung tâm quản lý và phân phối tất cả các tác vụ bất đồng bộ.

---

### Ví dụ thực tế: So sánh Đồng bộ vs Bất đồng bộ

Ví dụ bạn cần tải dữ liệu từ 3 nguồn khác nhau, lần lượt mất 2 giây, 3 giây và 1 giây.

```python
import asyncio
import time

# Định nghĩa một coroutine mô phỏng việc tải dữ liệu từ mạng (I/O)
async def fetch_data(task_id: int, delay: int):
    print(f"Bắt đầu tải Task {task_id} (chờ {delay}s)...")
    await asyncio.sleep(delay)  # Dùng asyncio.sleep thay vì time.sleep để không block
    print(f" Hoàn thành Task {task_id}")
    return f"Data {task_id}"

async def main():
    start_time = time.time()
    
    # asyncio.gather cho phép chạy đồng thời cả 3 task
    results = await asyncio.gather(
        fetch_data(1, 2),
        fetch_data(2, 3),
        fetch_data(3, 1)
    )
    
    elapsed = time.time() - start_time
    print(f"\nKết quả thu được: {results}")
    print(f"Tổng thời gian thực thi: {elapsed:.2f} giây")

# Điểm khởi chạy chương trình asyncio
asyncio.run(main())

```

**Cách hoạt động của đoạn mã:**

1. Nếu chạy **đồng bộ** (`sync`), chương trình sẽ chờ từng task hoàn thành: $2 + 3 + 1 = 6$ giây.
2. Với **`asyncio`**, ngay khi `Task 1` rơi vào trạng thái chờ (`await`), Event Loop chuyển sang chạy `Task 2` và `Task 3`.
3. **Tổng thời gian hoàn thành chỉ mất khoảng 3 giây** (bằng thời gian của task dài nhất).

---

### Lưu ý quan trọng khi dùng asyncio

* **Không dùng các hàm block đồng bộ**: Tránh dùng `time.sleep()`, `requests.get()`, hoặc thư viện IO thông thường inside coroutine. Hãy dùng các thư viện tương thích bất đồng bộ như `asyncio.sleep()`, `aiohttp`, `httpx`, `aiomysql`.
* **Không phù hợp cho CPU-bound**: Nếu là tác vụ tính toán nặng (xử lý ảnh, AI, vòng lặp triệu lần), `asyncio` không làm tăng tốc độ. Với CPU-bound, bạn nên chọn `multiprocessing`.