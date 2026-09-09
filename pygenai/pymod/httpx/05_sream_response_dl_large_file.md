Khi bạn gọi `httpx.get()`, mặc định `httpx` sẽ tải toàn bộ nội dung (Response Body) vào bộ nhớ RAM trước khi trả về đối tượng `Response`. Nếu file cần tải có dung lượng lớn (vài trăm MB hoặc vài GB), việc này sẽ gây tốn RAM dữ dội hoặc khiến chương trình crash vì lỗi **Out of Memory (OOM)**.

Giải pháp chuẩn mực trong `httpx` là sử dụng cơ chế **Streaming** thông qua phương thức `httpx.stream()` hoặc `client.stream()`.

---

## Nguyên lý hoạt động của Streaming

Thay vì nạp toàn bộ dữ liệu vào RAM, Streaming chỉ mở một kết nối mạng (Socket) và đọc dữ liệu theo từng khối nhỏ (chuẩn bị từng **chunk**, ví dụ 8KB hay 64KB) rồi ghi trực tiếp xuống đĩa cứng (Disk). RAM chỉ lưu đúng dung lượng của khối nhỏ đó tại một thời điểm.

```text
[ Server ] ---> (Từng chunk 8KB qua Socket) ---> [ RAM tạm 8KB ] ---> [ Ghi vào Disk ]

```

---

## 1. Stream & Download File đồng bộ (Sync)

Sử dụng hàm `httpx.stream()` kết hợp với vòng lặp `response.iter_bytes()`:

```python
import httpx

url = "https://speed.hetzner.de/100MB.bin"
output_filename = "downloaded_100MB.bin"

# 1. Mở stream bằng context manager (with)
with httpx.stream("GET", url) as response:
    # Bắt lỗi HTTP nếu status code >= 400
    response.raise_for_status()
    
    # 2. Mở file ở chế độ ghi nhị phân (write binary)
    with open(output_filename, "wb") as file:
        # 3. Đọc dữ liệu theo từng chunk (8KB mỗi lần)
        for chunk in response.iter_bytes(chunk_size=8192):
            file.write(chunk)

print("Tải file hoàn tất mà không tốn RAM!")

```

---

## 2. Stream & Download File bất đồng bộ (Async)

Với `AsyncClient`, bạn sử dụng `async with client.stream(...)` và duyệt qua từng chunk bằng `aiter_bytes()`:

```python
import asyncio
import httpx

async def download_large_file(url: str, output_path: str):
    async with httpx.AsyncClient() as client:
        # 1. Mở async stream
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            
            with open(output_path, "wb") as file:
                # 2. Lặp bất đồng bộ qua từng chunk bằng aiter_bytes()
                async for chunk in response.aiter_bytes(chunk_size=8192):
                    file.write(chunk)

# Chạy chương trình async
asyncio.run(download_large_file("https://speed.hetzner.de/100MB.bin", "async_100MB.bin"))

```

---

## 3. Hiển thị thanh tiến trình (Progress Bar) khi tải

Bạn có thể đọc Header `Content-Length` để biết tổng dung lượng file và tính toán % tiến trình tải (kết hợp với thư viện `tqdm`):

```bash
pip install tqdm

```

```python
import httpx
from tqdm import tqdm

url = "https://speed.hetzner.de/100MB.bin"

with httpx.stream("GET", url) as response:
    response.raise_for_status()
    
    # Lấy tổng dung lượng file từ Header (tính bằng Bytes)
    total_bytes = int(response.headers.get("Content-Length", 0))
    
    # Khởi tạo thanh tiến trình tqdm
    with tqdm(total=total_bytes, unit="iB", unit_scale=True, desc="Downloading") as progress_bar:
        with open("100MB_with_progress.bin", "wb") as file:
            for chunk in response.iter_bytes(chunk_size=8192):
                file.write(chunk)
                # Cập nhật tiến trình sau mỗi chunk ghi thành công
                progress_bar.update(len(chunk))

```

---

## 💡 Lưu ý & Best Practices

1. **Kích thước `chunk_size` tối ưu:**
* Mặc định `chunk_size` thường chọn là `8192` (8 KB) hoặc `65536` (64 KB).
* Chunk quá nhỏ (ví dụ 100 bytes) làm tăng Overhead xử lý CPU.
* Chunk quá lớn (ví dụ 100 MB) lại làm tăng dung lượng RAM chiếm dụng.


2. **Luôn dùng Context Manager (`with` / `async with`):**
* Nếu không bọc `stream()` trong khối `with`, kết nối TCP socket sẽ bị treo và không được đóng đúng cách, gây rò rỉ tài nguyên mạng (Connection Leak).


3. **Phân biệt `iter_bytes()` và `iter_raw()`:**
* `iter_bytes()`: Tự động giải nén dữ liệu nếu Server gửi dạng nén (`gzip`, `brotli`, `deflate`). **Hầu hết trường hợp bạn nên dùng hàm này.**
* `iter_raw()`: Đọc các byte thô chưa giải nén trực tiếp từ Socket.