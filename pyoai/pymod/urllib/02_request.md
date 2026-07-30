# Khóa học urllib Deep Dive

# Buổi 2: `urllib.request` cơ bản – Gửi HTTP Request và đọc HTTP Response

Ở buổi 1, chúng ta đã tìm hiểu kiến trúc của `urllib` và biết rằng `urllib.request` là module quan trọng nhất.

Buổi 2 sẽ tập trung vào việc **làm chủ`urllib.request`**, hiểu cách gửi request và phân tích response một cách chi tiết.

* * *

# Mục tiêu buổi học

Sau buổi này, bạn sẽ:

  * Hiểu `urlopen()` hoạt động như thế nào. 
  * Phân biệt URL, Request và Response. 
  * Biết cách đọc dữ liệu theo nhiều cách. 
  * Hiểu đối tượng `HTTPResponse`. 
  * Biết sử dụng `with`. 
  * Hiểu vòng đời của một HTTP request. 



* * *

# 1\. Quy trình của một HTTP Request

Khi gọi:
    
    
    from urllib.request import urlopen
    
    response = urlopen("https://httpbin.org/get")

Thực tế Python làm rất nhiều bước.
    
    
    Python
    
    ↓
    
    urlopen()
    
    ↓
    
    Tạo HTTP Request
    
    ↓
    
    DNS Lookup
    
    ↓
    
    TCP Connection
    
    ↓
    
    TLS Handshake (HTTPS)
    
    ↓
    
    Gửi HTTP Request
    
    ↓
    
    Server xử lý
    
    ↓
    
    Nhận HTTP Response
    
    ↓
    
    Tạo HTTPResponse object
    
    ↓
    
    Trả về cho chương trình

Đây là lý do vì sao một lệnh tưởng như đơn giản lại có thể mất vài chục đến vài trăm mili giây.

* * *

# 2\. Hàm `urlopen()`

Cú pháp:
    
    
    urlopen(url,
            data=None,
            timeout=None,
            cafile=None,
            capath=None,
            cadefault=False,
            context=None)

Trong buổi này chúng ta quan tâm ba tham số đầu tiên.

  * `url`
  * `data`
  * `timeout`



Ví dụ:
    
    
    from urllib.request import urlopen
    
    response = urlopen(
        "https://httpbin.org/get",
        timeout=10
    )

* * *

# 3\. Giá trị trả về

`urlopen()` không trả về chuỗi.

Nó trả về:
    
    
    http.client.HTTPResponse

Kiểm tra:
    
    
    from urllib.request import urlopen
    
    r = urlopen("https://httpbin.org/get")
    
    print(type(r))

Kết quả
    
    
    <class 'http.client.HTTPResponse'>

* * *

# 4\. HTTPResponse chứa những gì?
    
    
    HTTPResponse
    │
    ├── status
    ├── reason
    ├── headers
    ├── read()
    ├── readline()
    ├── readlines()
    ├── geturl()
    ├── info()
    └── close()

Đây là đối tượng bạn sẽ làm việc nhiều nhất trong `urllib`.

* * *

# 5\. Đọc toàn bộ dữ liệu
    
    
    from urllib.request import urlopen
    
    with urlopen("https://httpbin.org/get") as r:
        data = r.read()
    
    print(type(data))

Kết quả
    
    
    <class 'bytes'>

Luôn nhớ:

> `urllib` trả về **bytes** , không phải `str`.

* * *

# 6\. Decode
    
    
    text = data.decode("utf-8")

Hoặc:
    
    
    text = data.decode()

Ví dụ:
    
    
    from urllib.request import urlopen
    
    with urlopen("https://httpbin.org/get") as r:
        text = r.read().decode()
    
    print(text)

* * *

# 7\. Đọc từng dòng

Ví dụ:
    
    
    from urllib.request import urlopen
    
    with urlopen("https://www.python.org") as r:
    
        while True:
            line = r.readline()
    
            if not line:
                break
    
            print(line.decode())

`readline()` hữu ích khi làm việc với:

  * HTML lớn 
  * CSV 
  * Log 
  * Stream 



* * *

# 8\. Đọc toàn bộ thành danh sách
    
    
    with urlopen("https://www.python.org") as r:
        lines = r.readlines()
    
    print(len(lines))

Kết quả:
    
    
    480

Danh sách:
    
    
    [
        b'<html>\n',
        b'<head>\n',
        ...
    ]

* * *

# 9\. Đọc theo kích thước

Đây là cách chuyên nghiệp hơn.

Ví dụ:
    
    
    with urlopen("https://www.python.org") as r:
    
        chunk = r.read(100)
    
    print(chunk)

Chỉ đọc:
    
    
    100 bytes

* * *

Đọc từng block:
    
    
    from urllib.request import urlopen
    
    with urlopen("https://www.python.org") as r:
    
        while True:
    
            chunk = r.read(1024)
    
            if not chunk:
                break
    
            print(len(chunk))

Đây là cách download file.

* * *

# 10\. Kiểm tra mã trạng thái
    
    
    with urlopen("https://httpbin.org/get") as r:
        print(r.status)

Kết quả
    
    
    200

* * *

# 11\. Status Code

Một số mã phổ biến:

Code| Ý nghĩa  
---|---  
200| OK  
201| Created  
204| No Content  
301| Moved Permanently  
302| Found  
400| Bad Request  
401| Unauthorized  
403| Forbidden  
404| Not Found  
500| Internal Server Error  
  
* * *

# 12\. Reason
    
    
    with urlopen("https://httpbin.org/get") as r:
        print(r.reason)

Kết quả
    
    
    OK

* * *

# 13\. Headers
    
    
    with urlopen("https://httpbin.org/get") as r:
        print(r.headers)

Ví dụ:
    
    
    Date
    Server
    Content-Type
    Content-Length
    Connection

* * *

# 14\. Lấy từng Header
    
    
    content_type = r.headers["Content-Type"]
    
    print(content_type)

Hoặc:
    
    
    print(r.headers.get("Content-Type"))

* * *

# 15\. Duyệt tất cả Header
    
    
    with urlopen("https://httpbin.org/get") as r:
    
        for key, value in r.headers.items():
            print(key, value)

Ví dụ:
    
    
    Server gunicorn
    
    Content-Type application/json
    
    Content-Length 312

* * *

# 16\. URL cuối cùng

Nếu server redirect:
    
    
    A
    
    ↓
    
    B
    
    ↓
    
    C

Thì:
    
    
    print(r.geturl())

trả về:
    
    
    C

* * *

# 17\. info()
    
    
    print(r.info())

Thực chất:
    
    
    r.info() == r.headers

`info()` là API cũ nhưng bạn vẫn sẽ gặp trong nhiều mã nguồn.

* * *

# 18\. Đóng kết nối

Không nên:
    
    
    r = urlopen(url)
    
    ...
    
    r.close()

Nên:
    
    
    with urlopen(url) as r:
        ...

Vì `with` luôn đảm bảo đóng kết nối ngay cả khi xảy ra ngoại lệ.

* * *

# 19\. Ví dụ thực tế: đọc JSON
    
    
    import json
    from urllib.request import urlopen
    
    url = "https://httpbin.org/get"
    
    with urlopen(url) as r:
    
        data = json.loads(
            r.read().decode()
        )
    
    print(data)

* * *

# 20\. Ví dụ thực tế: đọc HTML
    
    
    from urllib.request import urlopen
    
    url = "https://www.python.org"
    
    with urlopen(url) as r:
    
        html = r.read().decode()
    
    print(html[:500])

* * *

# 21\. Ví dụ thực tế: Download theo từng block
    
    
    from urllib.request import urlopen
    
    url = "https://www.python.org"
    
    with (
        urlopen(url) as response,
        open("python.html", "wb") as file,
    ):
        while True:
    
            chunk = response.read(4096)
    
            if not chunk:
                break
    
            file.write(chunk)
    
    print("Done")

Đây là nền tảng của mọi chương trình tải file.

* * *

# 22\. Những lỗi phổ biến

### Lỗi 1: Quên decode

Sai:
    
    
    print(r.read())

Kết quả:
    
    
    b'<html>...'

Đúng:
    
    
    print(r.read().decode())

* * *

### Lỗi 2: Đọc hai lần

Sai:
    
    
    print(r.read())
    
    print(r.read())

Kết quả:
    
    
    b'...'
    
    b''

Vì luồng dữ liệu đã được đọc hết.

* * *

### Lỗi 3: Không dùng `with`

Sai:
    
    
    r = urlopen(url)

Nếu quên `close()`, tài nguyên mạng có thể không được giải phóng kịp thời.

* * *

# 23\. Bài tập thực hành

## Bài 1

Viết chương trình:

  * tải trang `https://www.python.org`
  * in: 
    * status 
    * reason 
    * content-type 
    * content-length 



* * *

## Bài 2

Đọc nội dung HTML và in ra:

  * 100 ký tự đầu 
  * 100 ký tự cuối 



* * *

## Bài 3

Đọc trang theo từng block 1024 byte và:

  * đếm số block 
  * đếm tổng số byte 



* * *

## Bài 4

Tạo hàm:
    
    
    def fetch(url):
        ...

Trả về:
    
    
    {
        "status": ...,
        "reason": ...,
        "headers": ...,
        "text": ...
    }

* * *

# Tổng kết

Hôm nay bạn đã nắm được các nền tảng quan trọng nhất của `urllib.request`:

  * `urlopen()` và vòng đời của một HTTP request. 
  * Đối tượng `HTTPResponse`. 
  * Đọc dữ liệu bằng `read()`, `readline()`, `readlines()` và đọc theo từng block. 
  * Truy cập `status`, `reason`, `headers`, `geturl()`. 
  * Sử dụng `with` để quản lý kết nối an toàn. 
  * Đọc HTML và JSON từ máy chủ. 



Ở **buổi 3** , chúng ta sẽ đi sâu vào **HTTP GET nâng cao** , bao gồm cách xây dựng đối tượng `Request`, thêm tham số truy vấn (query string), tùy biến header và phân tích quá trình gửi request ở mức chi tiết hơn. Đây là bước chuyển từ việc chỉ "gọi URL" sang việc chủ động xây dựng một HTTP request hoàn chỉnh.

