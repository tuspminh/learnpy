# Khóa học urllib Deep Dive

# Buổi 7: Download File chuyên nghiệp với `urllib`

> Đây là buổi học rất thực tế. Sau buổi này, bạn sẽ có thể xây dựng một **Downloader** tương tự như `wget`, `curl` hoặc trình cập nhật (updater) của phần mềm.

Trong thực tế, rất nhiều ứng dụng Python cần tải file:

  * Crawler tải ảnh 
  * Downloader tải video 
  * Auto Updater 
  * Download dataset AI 
  * Backup dữ liệu 
  * Tải model Machine Learning 
  * Tải package/plugin 



* * *

# Mục tiêu

Sau buổi học này, bạn sẽ:

  * Download file đúng cách. 
  * Không đọc toàn bộ file vào RAM. 
  * Hiểu Binary Stream. 
  * Download theo từng block (chunk). 
  * Hiển thị tiến trình tải. 
  * Kiểm tra kích thước file. 
  * Thiết kế lớp `Downloader`. 



* * *

# 1\. Sai lầm phổ biến

Nhiều người mới học thường viết:
    
    
    from urllib.request import urlopen
    
    with urlopen(url) as response:
        data = response.read()
    
    with open("file.zip", "wb") as f:
        f.write(data)

Điều gì xảy ra nếu file có dung lượng:

  * 2 GB 
  * 5 GB 
  * 20 GB 


    
    
    Internet
    
    ↓
    
    response.read()
    
    ↓
    
    RAM
    
    ↓
    
    Ổ cứng

Toàn bộ file sẽ được nạp vào RAM trước khi ghi xuống đĩa.

Nếu RAM không đủ:

  * chương trình chậm 
  * tốn bộ nhớ 
  * có thể bị `MemoryError`



* * *

# 2\. Download theo Stream

Thay vào đó:
    
    
    Internet
    
    ↓
    
    1024 bytes
    
    ↓
    
    Ghi file
    
    ↓
    
    1024 bytes
    
    ↓
    
    Ghi file
    
    ↓
    
    ...

Đây là cách tất cả downloader chuyên nghiệp hoạt động.

* * *

# 3\. Chunk là gì?

Chunk = một khối dữ liệu nhỏ.

Ví dụ:
    
    
    File 100 MB
    
    ↓
    
    4096 bytes
    
    ↓
    
    4096 bytes
    
    ↓
    
    4096 bytes
    
    ↓
    
    ...

* * *

# 4\. Download cơ bản
    
    
    from urllib.request import urlopen
    
    url = "https://example.com/file.zip"
    
    with (
        urlopen(url) as response,
        open("file.zip", "wb") as file,
    ):
    
        while True:
    
            chunk = response.read(4096)
    
            if not chunk:
                break
    
            file.write(chunk)

Đây là cách download chuẩn.

* * *

# 5\. Vì sao dùng 4096?

Ví dụ:
    
    
    response.read(1)

↓

Rất nhiều lần đọc

↓

Chậm

* * *
    
    
    response.read(1024 * 1024)

↓

Ít lần đọc

↓

Nhưng tốn RAM hơn

* * *

Thông thường:
    
    
    4096 bytes
    
    8192 bytes
    
    16384 bytes
    
    65536 bytes

đều là lựa chọn tốt.

Để linh hoạt, nên cho phép cấu hình:
    
    
    chunk_size = 8192

* * *

# 6\. Content-Length

Server thường gửi:
    
    
    Content-Length:
    
    123456789

Python:
    
    
    length = response.headers.get(
        "Content-Length"
    )
    
    print(length)

* * *

# 7\. Chuyển sang số
    
    
    total = int(
        response.headers.get(
            "Content-Length",
            0
        )
    )

Nếu server không gửi `Content-Length`, giá trị mặc định là `0`.

* * *

# 8\. Theo dõi số byte đã tải
    
    
    downloaded = 0
    
    while True:
    
        chunk = response.read(8192)
    
        if not chunk:
            break
    
        file.write(chunk)
    
        downloaded += len(chunk)

* * *

# 9\. Tính phần trăm
    
    
    percent = (
        downloaded
        / total
    ) * 100

Ví dụ:
    
    
    Downloaded:
    
    40%
    
    65%
    
    83%
    
    100%

* * *

# 10\. Hiển thị Progress
    
    
    print(
        f"{percent:.2f}%"
    )

Hoặc:
    
    
    print(
        downloaded,
        "/",
        total
    )

Ví dụ:
    
    
    45%
    
    46%
    
    47%
    
    ...

* * *

# 11\. Download hoàn chỉnh
    
    
    from urllib.request import urlopen
    
    url = "https://example.com/file.zip"
    
    with (
        urlopen(url) as response,
        open("file.zip", "wb") as file,
    ):
    
        total = int(
            response.headers.get(
                "Content-Length",
                0
            )
        )
    
        downloaded = 0
    
        while True:
    
            chunk = response.read(8192)
    
            if not chunk:
                break
    
            file.write(chunk)
    
            downloaded += len(chunk)
    
            if total:
    
                percent = (
                    downloaded
                    / total
                ) * 100
    
                print(
                    f"\r{percent:.1f}%",
                    end=""
                )
    
    print()
    print("Done")

Lưu ý `\r` giúp ghi đè lên cùng một dòng trong terminal thay vì in ra hàng trăm dòng mới.

* * *

# 12\. Tốc độ tải

Ta cần biết:
    
    
    Downloaded
    
    ↓
    
    Time
    
    ↓
    
    Speed

* * *
    
    
    import time
    
    start = time.time()

Sau mỗi vòng:
    
    
    elapsed = time.time() - start

* * *

Tốc độ:
    
    
    speed = downloaded / elapsed

Đơn vị:
    
    
    Bytes/s

Để hiển thị đẹp hơn, có thể đổi sang KB/s hoặc MB/s.

* * *

# 13\. Hàm chuyển kích thước
    
    
    def format_size(size):
    
        units = [
            "B",
            "KB",
            "MB",
            "GB",
            "TB"
        ]
    
        for unit in units:
    
            if size < 1024:
                return (
                    f"{size:.1f} {unit}"
                )
    
            size /= 1024
    
        return (
            f"{size:.1f} PB"
        )

Ví dụ:
    
    
    print(
        format_size(
            123456789
        )
    )

Kết quả:
    
    
    117.7 MB

* * *

# 14\. Hiển thị tốc độ
    
    
    speed = (
        downloaded
        / elapsed
    )
    
    print(
        format_size(speed),
        "/s"
    )

Ví dụ:
    
    
    4.8 MB/s

* * *

# 15\. Thiết kế `Downloader`
    
    
    class Downloader:
    
        def __init__(
            self,
            chunk_size=8192
        ):
            self.chunk_size = chunk_size

* * *

# 16\. Hàm download
    
    
    from urllib.request import urlopen
    
    class Downloader:
    
        def __init__(
            self,
            chunk_size=8192
        ):
            self.chunk_size = chunk_size
    
        def download(
            self,
            url,
            filename
        ):
    
            with (
                urlopen(url) as response,
                open(
                    filename,
                    "wb"
                ) as file,
            ):
    
                while True:
    
                    chunk = response.read(
                        self.chunk_size
                    )
    
                    if not chunk:
                        break
    
                    file.write(chunk)

* * *

# 17\. Callback Progress

Thay vì `print()` trực tiếp, ta truyền callback:
    
    
    def progress(
        downloaded,
        total
    ):
        print(
            downloaded,
            total
        )

Trong `Downloader`:
    
    
    class Downloader:
    
        ...
    
        def download(
            self,
            url,
            filename,
            progress=None
        ):
            ...

Mỗi lần ghi xong:
    
    
    if progress:
    
        progress(
            downloaded,
            total
        )

Điều này giúp lớp `Downloader` không phụ thuộc vào giao diện (CLI, GUI hay Web).

* * *

# 18\. Thiết kế hướng đối tượng
    
    
    Downloader
    │
    ├── download()
    ├── get_size()
    ├── format_size()
    ├── report_progress()
    └── chunk_size

Về sau có thể mở rộng:

  * Resume download 
  * Retry 
  * Verify checksum 
  * Multi-thread download 



mà không cần sửa mã nguồn hiện có.

* * *

# 19\. Cấu trúc dự án
    
    
    httpclient/
    │
    ├── downloader.py
    ├── progress.py
    ├── client.py
    ├── api.py
    ├── exceptions.py
    └── examples/

`progress.py` có thể chứa:
    
    
    class ProgressPrinter:
        ...

để quản lý việc hiển thị tiến trình.

* * *

# 20\. Thiết kế Downloader chuyên nghiệp

Sau vài buổi nữa, mục tiêu của chúng ta là sử dụng được API như sau:
    
    
    client = Downloader()
    
    client.download(
        url="https://example.com/file.zip",
        filename="file.zip"
    )

Hoặc:
    
    
    client.download(
        url,
        filename,
        progress=my_progress
    )

Trong đó `my_progress` có thể cập nhật:

  * CLI 
  * PySide6 
  * Textual 
  * Flet 



mà không cần sửa lớp `Downloader`.

* * *

# Những lỗi thường gặp

## 1\. Dùng `read()` không giới hạn

Sai:
    
    
    data = response.read()

Đối với file lớn, cách này có thể làm tăng đáng kể lượng RAM sử dụng.

Đúng:
    
    
    while True:
        chunk = response.read(8192)
    
        if not chunk:
            break

* * *

## 2\. Không mở file ở chế độ nhị phân

Sai:
    
    
    open(
        "file.zip",
        "w"
    )

Đúng:
    
    
    open(
        "file.zip",
        "wb"
    )

* * *

## 3\. Chia cho 0

Nếu:
    
    
    Content-Length
    
    =
    
    0

thì:
    
    
    downloaded / total

sẽ gây lỗi.

Cần kiểm tra:
    
    
    if total:
        percent = (
            downloaded
            / total
        ) * 100

* * *

# Bài tập thực hành

### Bài 1

Viết hàm:
    
    
    def download(
        url,
        filename
    ):
        ...

Yêu cầu:

  * tải theo từng chunk 
  * không dùng `response.read()` không tham số 



* * *

### Bài 2

Viết hàm:
    
    
    def format_size(size):
        ...

Chuyển:
    
    
    123
    
    ↓
    
    123 B
    
    
    123456
    
    ↓
    
    120.6 KB
    
    
    123456789
    
    ↓
    
    117.7 MB

* * *

### Bài 3

Thiết kế lớp:
    
    
    class Downloader:

Hỗ trợ:

  * `chunk_size`
  * `download()`
  * callback `progress`



* * *

### Bài 4

Viết chương trình tải một file bất kỳ và hiển thị trên cùng một dòng:
    
    
    45.3%
    12.5 MB / 50.0 MB
    3.4 MB/s

Hãy cập nhật bằng `\r` để giao diện gọn gàng.

* * *

# Tổng kết

Trong buổi 7, bạn đã học được:

  * Vì sao cần tải file theo **stream** thay vì đọc toàn bộ vào RAM. 
  * Sử dụng `response.read(chunk_size)` để xử lý file lớn hiệu quả. 
  * Đọc `Content-Length` để tính tiến độ tải. 
  * Hiển thị phần trăm, dung lượng đã tải và tốc độ tải. 
  * Thiết kế lớp `Downloader` theo hướng mở rộng với callback tiến trình. 



## Góc nhìn thiết kế

Có một điểm cần lưu ý trong thiết kế ở trên: việc `Downloader` trực tiếp gọi `urlopen()` khiến lớp này phụ thuộc chặt vào `urllib`.

Trong các dự án lớn, nên áp dụng **Dependency Injection** :
    
    
    class Downloader:
        def __init__(self, http_client):
            self.http_client = http_client

Khi đó:

  * `Downloader` chỉ quan tâm đến việc ghi dữ liệu ra file. 
  * `HttpClient` chịu trách nhiệm tạo kết nối HTTP. 
  * Sau này bạn có thể thay `urllib` bằng `httpx` hoặc `requests` mà không phải sửa logic tải file. 



Đây là hướng kiến trúc chúng ta sẽ dần hoàn thiện trong các buổi tiếp theo.

Ở **buổi 8** , chúng ta sẽ học **Upload dữ liệu** , bao gồm:

  * gửi file bằng `multipart/form-data`, 
  * upload ảnh, tài liệu và dữ liệu nhị phân, 
  * xây dựng `MultipartEncoder`, 
  * và mở rộng `HttpClient` để hỗ trợ upload file theo cách chuyên nghiệp.

