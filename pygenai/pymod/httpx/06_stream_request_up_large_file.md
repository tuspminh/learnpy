```python
import httpx
print(httpx.__version__)


```

```text
Traceback (most recent call last):
  File "<xbox-string>", line 1, in <module>
    import httpx
ModuleNotFoundError: No module named 'httpx'


```

Khi bạn **tải lên (upload)** một tệp tin dung lượng lớn (vài GB) lên server, nếu đọc toàn bộ dữ liệu file vào memory trước (ví dụ: dùng `file.read()`), ứng dụng sẽ ngay lập tức bị nghẽn hoặc tràn RAM (Out of Memory).

Để khắc phục điều này, `httpx` cho phép bạn truyền vào một **generator** (hoặc **async generator**) hoặc một **file object** mở ở chế độ binary. Khi đó, `httpx` sử dụng kỹ thuật **Streaming Request Body** (thường sử dụng cơ chế *HTTP Chunked Transfer Encoding*) để vừa đọc từng phần dữ liệu từ đĩa cứng, vừa gửi từng phần qua socket tới server.

---

## 1. Upload Stream đồng bộ (Sync)

Trong synchronous mode, bạn chỉ cần truyền một **file-like object** (đã mở ở dạng `rb`) hoặc một **generator** phát ra từng khối `bytes` cho tham số `content`.

### Cách 1: Truyền trực tiếp File Object (Cách đơn giản & tối ưu nhất)

`httpx` tự động xử lý đọc từng chunk từ file object mà không load hết vào RAM.

```python
import httpx

file_path = "video_4k_huge_file.mp4"
upload_url = "https://httpbin.org/post"

# 1. Mở file ở chế độ binary read ('rb')
with open(file_path, "rb") as file_stream:
    # 2. Truyền file object trực tiếp vào tham số content
    # httpx sẽ tự động stream nội dung file theo từng chunk
    response = httpx.post(
        upload_url,
        content=file_stream,
        headers={"Content-Type": "video/mp4"},
        timeout=300.0  # Upload file lớn nên tăng timeout
    )

print("Status Code:", response.status_code)

```

---

### Cách 2: Tự định nghĩa Generator (Tuyệt vời nếu muốn thêm Tiến trình - Progress)

Nếu muốn kiểm soát dung lượng từng chunk gửi đi hoặc theo dõi tiến trình upload, bạn có thể viết một Generator function:

```python
import os
import httpx

file_path = "huge_archive.zip"
file_size = os.path.getsize(file_path)

def file_generator(path: str, chunk_size: int = 65536): # 64 KB per chunk
    uploaded_bytes = 0
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            uploaded_bytes += len(chunk)
            
            # Tính phần trăm tiến trình
            percent = (uploaded_bytes / file_size) * 100
            print(f"\rUploading: {percent:.2f}% ({uploaded_bytes}/{file_size} bytes)", end="")
            
            yield chunk

# Sử dụng generator làm content request
response = httpx.post(
    "https://httpbin.org/post",
    content=file_generator(file_path),
    headers={"Content-Type": "application/zip"},
    timeout=600.0
)
print("\nUpload thành công!")

```

---

## 2. Upload Stream bất đồng bộ (Async)

Đối với `AsyncClient`, bạn sử dụng một **Async Generator** truyền vào tham số `content`.

```python
import asyncio
import os
import httpx

async def async_file_generator(path: str, chunk_size: int = 65536):
    """Async Generator đọc file từng khối nhỏ"""
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk
            # Cho phép các tác vụ async khác chen ngang xử lý
            await asyncio.sleep(0)

async def main():
    file_path = "huge_data.bin"
    
    async with httpx.AsyncClient(timeout=600.0) as client:
        # Truyền async generator vào content
        response = await client.post(
            "https://httpbin.org/post",
            content=async_file_generator(file_path),
            headers={"Content-Type": "application/octet-stream"}
        )
        print("Status Code:", response.status_code)

asyncio.run(main())

```

---

## 3. Streaming Multipart Form Upload (Upload đính kèm theo tên Form field)

Nếu API backend yêu cầu gửi file theo chuẩn `multipart/form-data` (ví dụ giống như submit form HTML `<input type="file">`), bạn **không** nên dùng tham số `files` theo cách thông thường nếu file quá lớn vì nó có thể tự động đọc nội dung file vào RAM.

Thay vào đó, sử dụng lớp **`httpx.MultipartStream`** hoặc thư viện **`requests-toolbelt` / `multipart**` nếu cần cấu hình sâu. Tuy nhiên, cách chuẩn nhất của `httpx` khi upload Multipart lớn là kết hợp với các gói stream chuyên dụng hoặc mở stream trực tiếp qua `files`:

```python
import httpx

file_path = "large_image.iso"

# httpx hỗ trợ stream file qua giao thức multipart nếu bạn truyền file handle vào dictionary `files`
with open(file_path, "rb") as f:
    files = {"file": ("large_image.iso", f, "application/x-iso9660-image")}
    
    response = httpx.post(
        "https://httpbin.org/post",
        files=files,
        timeout=300.0
    )
    print("Status:", response.status_code)

```

---

## 💡 Lưu ý quan trọng khi Streaming Request Body

1. **Header `Content-Length` & Chunked Transfer:**
* Khi truyền bằng Generator, `httpx` không thể biết trước chính xác tổng dung lượng request. Do đó, nó sẽ tự động thêm header `Transfer-Encoding: chunked`.
* Một số server/proxy cũ (hoặc cấu hình Nginx chưa chuẩn) có thể từ chối nhận request dạng `Chunked`. Nếu gặp lỗi này, bạn nên tính sẵn `Content-Length` và khai báo thủ công trong `headers`:
```python
file_size = os.path.getsize(file_path)
headers = {
    "Content-Length": str(file_size),
    "Content-Type": "video/mp4"
}

```




2. **Kích thước `chunk_size` tối ưu:**
* Kích thước chunk phù hợp khi upload nên từ **64 KB (`65536`) đến 1 MB (`1048576`)**.
* Tránh đặt chunk quá nhỏ (dưới 4KB) làm giảm hiệu năng đường truyền mạng.