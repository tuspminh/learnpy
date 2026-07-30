# Khóa học urllib Deep Dive

# Buổi 8: Upload File chuyên nghiệp với `multipart/form-data`

> Sau buổi này, bạn sẽ hiểu cách trình duyệt upload file hoạt động và tự xây dựng được `MultipartEncoder` bằng Python mà **không phụ thuộc vào`requests`**.

Đây là một trong những phần "khó" nhất của `urllib`, vì thư viện chuẩn **không có sẵn API upload file tiện lợi** như `requests`. Chính vì vậy, hiểu phần này sẽ giúp bạn nắm rõ bản chất của giao thức HTTP.

* * *

# Mục tiêu

Sau buổi học này, bạn sẽ:

  * Hiểu `multipart/form-data`. 
  * Biết tại sao upload file khác POST thông thường. 
  * Tự xây dựng HTTP Body cho multipart. 
  * Upload file bằng `urllib`. 
  * Thiết kế `MultipartEncoder`. 
  * Chuẩn bị nền tảng cho việc upload nhiều file. 



* * *

# 1\. POST Form vs Multipart

Ở buổi trước chúng ta gửi:
    
    
    application/x-www-form-urlencoded

Ví dụ:
    
    
    name=Alice&age=20

Chỉ phù hợp với dữ liệu văn bản.

* * *

Upload file phải dùng:
    
    
    multipart/form-data

Ví dụ:
    
    
    POST
    
    ↓
    
    boundary
    
    ↓
    
    field1
    
    ↓
    
    field2
    
    ↓
    
    file
    
    ↓
    
    boundary

* * *

# 2\. Một Multipart Request

Ví dụ đơn giản:
    
    
    POST /upload HTTP/1.1
    
    Content-Type:
    multipart/form-data; boundary=ABC123
    
    --ABC123
    Content-Disposition: form-data; name="username"
    
    alice
    
    --ABC123
    Content-Disposition: form-data; name="avatar"; filename="cat.png"
    Content-Type: image/png
    
    (binary...)
    
    --ABC123--

Đây chính là dữ liệu mà trình duyệt gửi khi bạn chọn file trong `<input type="file">`.

* * *

# 3\. Boundary là gì?

Boundary là chuỗi dùng để phân tách các phần dữ liệu.

Ví dụ:
    
    
    ------ABC123

Mỗi phần đều bắt đầu bằng:
    
    
    --boundary

và kết thúc bằng:
    
    
    --boundary--

Dòng cuối có thêm `--` để đánh dấu kết thúc toàn bộ nội dung.

* * *

# 4\. Sinh Boundary

Không nên hard-code.
    
    
    import uuid
    
    boundary = uuid.uuid4().hex
    
    print(boundary)

Ví dụ:
    
    
    6c1c6a4c65fd4a7d9dbf0d9f4f8a5d71

* * *

# 5\. Header Content-Type
    
    
    headers = {
        "Content-Type":
        f"multipart/form-data; boundary={boundary}"
    }

Server sẽ dùng đúng boundary này để tách dữ liệu.

* * *

# 6\. Một Field

Ví dụ field:
    
    
    username = alice

Phần body sẽ là:
    
    
    --boundary
    
    Content-Disposition:
    form-data; name="username"
    
    alice

* * *

Python:
    
    
    field = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="username"\r\n'
        "\r\n"
        "alice\r\n"
    )

Lưu ý dùng `\r\n` theo chuẩn HTTP.

* * *

# 7\. File Part

Ví dụ:
    
    
    avatar.png

Header:
    
    
    Content-Disposition:
    form-data;
    name="avatar";
    filename="avatar.png"

Thêm:
    
    
    Content-Type:
    image/png

Sau đó là dữ liệu nhị phân của file.

* * *

# 8\. Đọc file
    
    
    from pathlib import Path
    
    path = Path("avatar.png")
    
    data = path.read_bytes()

`read_bytes()` phù hợp với ví dụ nhỏ. Với file rất lớn, ở các buổi nâng cao chúng ta sẽ bàn về stream upload.

* * *

# 9\. MIME Type

Có thể dùng:
    
    
    import mimetypes
    
    mime, _ = mimetypes.guess_type("avatar.png")
    
    print(mime)

Kết quả:
    
    
    image/png

Ví dụ khác:
    
    
    photo.jpg
    
    ↓
    
    image/jpeg
    
    
    report.pdf
    
    ↓
    
    application/pdf

Nếu không xác định được:
    
    
    mime = mime or "application/octet-stream"

* * *

# 10\. Ghép Body
    
    
    body = bytearray()

Field:
    
    
    body.extend(field.encode())

File:
    
    
    body.extend(file_bytes)

Kết thúc:
    
    
    body.extend(
        f"\r\n--{boundary}--\r\n".encode()
    )

`bytearray` rất phù hợp vì có thể nối nhiều phần dữ liệu hiệu quả hơn việc cộng nhiều đối tượng `bytes`.

* * *

# 11\. Upload
    
    
    from urllib.request import Request
    from urllib.request import urlopen
    
    req = Request(
        url,
        data=bytes(body),
        headers=headers,
        method="POST"
    )
    
    with urlopen(req) as response:
        print(response.read().decode())

* * *

# 12\. Thiết kế MultipartEncoder

Thay vì viết mọi thứ trong một hàm:
    
    
    body = ...

Ta tạo:
    
    
    class MultipartEncoder:
        ...

* * *

# 13\. Thuộc tính
    
    
    class MultipartEncoder:
    
        def __init__(self):
    
            self.boundary = ...
    
            self.parts = []

* * *

# 14\. add_field()
    
    
    encoder.add_field(
        "username",
        "alice"
    )

Bên trong:
    
    
    self.parts.append(...)

Lưu dưới dạng cấu trúc dữ liệu (ví dụ `dict` hoặc `dataclass`), thay vì ghép chuỗi ngay lập tức.

* * *

# 15\. add_file()
    
    
    encoder.add_file(
        name="avatar",
        filename="cat.png"
    )

Lớp sẽ:

  * đọc file 
  * đoán MIME type 
  * lưu metadata 
  * chuẩn bị để mã hóa 



* * *

# 16\. encode()
    
    
    body = encoder.encode()

Trả về:
    
    
    bytes

Đồng thời cung cấp:
    
    
    encoder.content_type

Ví dụ:
    
    
    multipart/form-data;
    boundary=....

* * *

# 17\. Upload nhiều file
    
    
    encoder.add_file(
        "file1",
        "a.png"
    )
    
    encoder.add_file(
        "file2",
        "b.png"
    )
    
    encoder.add_file(
        "file3",
        "c.pdf"
    )

`MultipartEncoder` chỉ cần lặp qua tất cả các phần (`parts`) để tạo body.

* * *

# 18\. Tích hợp vào HttpClient
    
    
    client.post(
        url,
        multipart=encoder
    )

Bên trong:
    
    
    headers[
        "Content-Type"
    ] = encoder.content_type
    
    body = encoder.encode()

Đây là hướng mở rộng tốt hơn so với việc thêm nhiều tham số rời rạc.

* * *

# 19\. Cấu trúc thư mục
    
    
    httpclient/
    │
    ├── client.py
    ├── api.py
    ├── downloader.py
    ├── multipart.py
    ├── headers.py
    ├── exceptions.py
    └── examples/

Trong đó:
    
    
    multipart.py

chứa:

  * `MultipartEncoder`
  * `MultipartField`
  * `MultipartFile`



Bạn có thể dùng `@dataclass` để biểu diễn từng phần dữ liệu một cách rõ ràng.

* * *

# 20\. API mong muốn

Sau buổi này, mục tiêu của chúng ta là có API như:
    
    
    encoder = MultipartEncoder()
    
    encoder.add_field(
        "username",
        "alice"
    )
    
    encoder.add_file(
        "avatar",
        "cat.png"
    )
    
    client.post(
        url,
        multipart=encoder
    )

Đây là cách thiết kế tương tự nhiều thư viện HTTP hiện đại.

* * *

# Những lỗi thường gặp

## 1\. Quên Boundary

Sai:
    
    
    Content-Type:
    
    multipart/form-data

Đúng:
    
    
    multipart/form-data;
    boundary=xxxx

Thiếu boundary, server sẽ không thể phân tách các phần dữ liệu.

* * *

## 2\. Sai xuống dòng

HTTP multipart yêu cầu:
    
    
    \r\n

Không phải:
    
    
    \n

* * *

## 3\. Quên kết thúc

Sai:
    
    
    --boundary

Đúng:
    
    
    --boundary--

Dấu `--` cuối cùng rất quan trọng để đánh dấu kết thúc body.

* * *

## 4\. Đọc toàn bộ file lớn

Trong ví dụ hôm nay:
    
    
    Path(...).read_bytes()

đọc toàn bộ file vào RAM.

Điều này phù hợp với ví dụ học tập và file nhỏ.

Đối với file rất lớn (hàng GB), nên thiết kế encoder hỗ trợ **streaming upload** , đọc từng khối dữ liệu thay vì toàn bộ. `urllib` không hỗ trợ trực tiếp điều này nên cần một thiết kế nâng cao hơn.

* * *

# Bài tập thực hành

## Bài 1

Viết:
    
    
    class MultipartEncoder:

Hỗ trợ:

  * `add_field()`
  * `add_file()`
  * `encode()`
  * `content_type`



* * *

## Bài 2

Viết hàm:
    
    
    def guess_mime(path):
        ...

Sử dụng `mimetypes.guess_type()` và trả về `"application/octet-stream"` nếu không xác định được.

* * *

## Bài 3

Mở rộng `HttpClient`

Cho phép:
    
    
    client.post(
        url,
        multipart=encoder
    )

và tự động:

  * đặt `Content-Type`
  * tạo body 
  * gửi request 



* * *

## Bài 4

Sử dụng `https://httpbin.org/post`

Tạo multipart gồm:

  * Field: 
    * `username = alice`
    * `age = 20`
  * File: 
    * một file văn bản bất kỳ trên máy 



Sau đó kiểm tra phản hồi JSON:

  * `form` có chứa các field. 
  * `files` có chứa nội dung file. 



* * *

# Tổng kết

Trong buổi 8, bạn đã học:

  * Sự khác biệt giữa `application/x-www-form-urlencoded` và `multipart/form-data`. 
  * Vai trò của `boundary` trong multipart. 
  * Cách xây dựng body multipart đúng chuẩn HTTP. 
  * Cách xác định MIME type của file. 
  * Thiết kế `MultipartEncoder` có khả năng mở rộng và tái sử dụng. 
  * Tích hợp encoder vào `HttpClient`. 



## Góc nhìn kiến trúc

Để thư viện dễ bảo trì hơn, bạn có thể tách trách nhiệm thành các lớp:
    
    
    MultipartEncoder
    │
    ├── MultipartField
    ├── MultipartFile
    └── MultipartPart (lớp cơ sở)

Mỗi loại phần dữ liệu tự biết cách chuyển thành `bytes`. `MultipartEncoder` chỉ chịu trách nhiệm ghép các phần theo đúng chuẩn HTTP. Đây là cách thiết kế hướng đối tượng linh hoạt hơn và rất phù hợp nếu sau này bạn muốn hỗ trợ thêm các kiểu dữ liệu hoặc upload theo luồng (streaming).

Ở **buổi 9** , chúng ta sẽ học **Timeout, Retry và Connection Handling** , bao gồm:

  * các loại timeout, 
  * xử lý lỗi mạng, 
  * retry với exponential backoff, 
  * thiết kế `RetryPolicy`, 
  * và xây dựng một `HttpClient` có khả năng chịu lỗi tốt trong môi trường thực tế.

