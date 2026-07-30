# Khóa học urllib Deep Dive

# Buổi 6: JSON API Deep Dive – Thiết kế `ApiClient` chuyên nghiệp

> **Mục tiêu:** Sau buổi này, bạn sẽ biết cách xây dựng một `ApiClient` có khả năng làm việc với REST API theo phong cách của các thư viện như `requests`, `httpx`, hoặc SDK của GitHub, OpenAI, Docker,...

Đây là một buổi rất quan trọng vì hiện nay **hơn 90% API hiện đại đều sử dụng JSON**.

* * *

# 1\. JSON là gì?

JSON (JavaScript Object Notation) là định dạng trao đổi dữ liệu phổ biến nhất trên Internet.

Ví dụ:
    
    
    {
        "id": 1,
        "name": "Alice",
        "age": 20,
        "skills": [
            "Python",
            "SQL"
        ]
    }

Trong Python:
    
    
    data = {
        "id": 1,
        "name": "Alice",
        "age": 20,
        "skills": [
            "Python",
            "SQL"
        ]
    }

* * *

# 2\. Chu trình làm việc với REST API

Một API client luôn thực hiện quy trình sau:
    
    
    dict
    
    ↓
    
    json.dumps()
    
    ↓
    
    bytes
    
    ↓
    
    HTTP Request
    
    ↓
    
    Internet
    
    ↓
    
    Server
    
    ↓
    
    bytes
    
    ↓
    
    decode()
    
    ↓
    
    json.loads()
    
    ↓
    
    dict

Bạn sẽ lặp đi lặp lại chu trình này trong mọi dự án làm việc với REST API.

* * *

# 3\. `json.dumps()`

Chuyển Python → JSON.
    
    
    import json
    
    payload = {
        "name": "Alice",
        "age": 20
    }
    
    text = json.dumps(payload)
    
    print(text)

Kết quả:
    
    
    {"name": "Alice", "age": 20}

* * *

# 4\. `json.loads()`

Chuyển JSON → Python.
    
    
    import json
    
    text = """
    {
        "name":"Alice",
        "age":20
    }
    """
    
    data = json.loads(text)
    
    print(data["name"])

* * *

# 5\. `json.dumps()` không trả về bytes

Đây là lỗi phổ biến.

Sai:
    
    
    body = json.dumps(data)

Đúng:
    
    
    body = json.dumps(data).encode("utf-8")

* * *

# 6\. `ensure_ascii`

Mặc định:
    
    
    import json
    
    data = {
        "name": "Nguyễn Văn A"
    }
    
    print(json.dumps(data))

Kết quả:
    
    
    {"name":"Nguy\u1ec5n V\u0103n A"}

Đẹp hơn:
    
    
    print(
        json.dumps(
            data,
            ensure_ascii=False
        )
    )

Kết quả:
    
    
    {"name":"Nguyễn Văn A"}

> **Lưu ý:** Khi gửi qua HTTP, cả hai đều hợp lệ. `ensure_ascii=False` chủ yếu giúp dễ đọc khi log hoặc debug.

* * *

# 7\. Viết hàm `request_json`

Thay vì lặp lại:
    
    
    body = json.dumps(obj).encode()
    
    headers = {
        "Content-Type":
        "application/json"
    }

Ta đóng gói:
    
    
    import json
    from urllib.request import Request, urlopen
    
    def request_json(url, payload):
    
        body = json.dumps(payload).encode()
    
        headers = {
            "Content-Type":
            "application/json"
        }
    
        req = Request(
            url,
            data=body,
            headers=headers
        )
    
        with urlopen(req) as response:
            return response.read().decode()

* * *

# 8\. Phân tích JSON tự động

Hiện tại:
    
    
    text = request_json(...)
    
    data = json.loads(text)

Ta muốn:
    
    
    data = request_json(...)

Tự động trả về `dict`.
    
    
    import json
    
    ...
    
    with urlopen(req) as response:
    
        return json.loads(
            response.read().decode()
        )

* * *

# 9\. Thiết kế `ApiResponse`

Trong thực tế, chỉ trả về `dict` là chưa đủ.

Ta muốn biết:

  * HTTP status 
  * Header 
  * URL cuối cùng 
  * Nội dung JSON 


    
    
    ApiResponse
    │
    ├── status
    ├── headers
    ├── url
    └── data

* * *
    
    
    from dataclasses import dataclass
    
    @dataclass
    class ApiResponse:
        status: int
        headers: dict
        url: str
        data: dict

* * *

# 10\. Trả về `ApiResponse`
    
    
    import json
    from urllib.request import Request, urlopen
    
    def post_json(url, payload):
    
        body = json.dumps(payload).encode()
    
        req = Request(
            url,
            data=body,
            headers={
                "Content-Type":
                "application/json"
            }
        )
    
        with urlopen(req) as response:
    
            return ApiResponse(
                status=response.status,
                headers=dict(response.headers),
                url=response.geturl(),
                data=json.loads(
                    response.read().decode()
                )
            )

* * *

# 11\. Thiết kế `ApiClient`

Đây là lúc tách biệt:
    
    
    HttpClient
    
    ↓
    
    ApiClient

`HttpClient`

  * chỉ biết HTTP 



`ApiClient`

  * biết JSON 



* * *
    
    
    class ApiClient(HttpClient):
    
        def post_json(
            self,
            url,
            obj
        ):
            ...

* * *

# 12\. Viết `post_json`
    
    
    import json
    
    class ApiClient(HttpClient):
    
        def post_json(
            self,
            url,
            obj
        ):
    
            return self.post(
                url,
                json_data=obj,
                headers={
                    "Accept":
                    "application/json"
                }
            )

* * *

# 13\. `get_json`
    
    
    import json
    
    class ApiClient(HttpClient):
    
        def get_json(
            self,
            url,
            params=None
        ):
    
            text = self.get(
                url,
                params=params
            )
    
            return json.loads(text)

* * *

Sử dụng:
    
    
    client = ApiClient()
    
    data = client.get_json(
        "https://httpbin.org/get"
    )
    
    print(data)

* * *

# 14\. Xử lý JSON lỗi

Có API trả về:
    
    
    <html>
    
    500 Internal Server Error
    
    </html>

Nếu:
    
    
    json.loads(html)

Sẽ phát sinh:
    
    
    JSONDecodeError

Do đó:
    
    
    import json
    
    try:
        data = json.loads(text)
    
    except json.JSONDecodeError:
    
        ...

* * *

# 15\. Kiểm tra Content-Type

Server nên trả:
    
    
    Content-Type
    
    application/json

Kiểm tra:
    
    
    content_type = response.headers.get(
        "Content-Type",
        ""
    )
    
    if "application/json" in content_type:
        ...

Đây là cách an toàn trước khi gọi `json.loads()`.

* * *

# 16\. Thiết kế Exception
    
    
    class ApiError(Exception):
        """Lỗi chung của API."""
    
    
    class JsonDecodeError(ApiError):
        """Không thể phân tích JSON."""
    
    
    class UnexpectedContentType(ApiError):
        """Content-Type không phải JSON."""

Thay vì trả về `None`, hãy phát sinh ngoại lệ có ý nghĩa.

* * *

# 17\. Cải tiến `ApiClient`
    
    
    class ApiClient(HttpClient):
    
        def get_json(
            self,
            url,
            params=None
        ):
    
            text = self.get(
                url,
                params=params
            )
    
            try:
                return json.loads(text)
    
            except json.JSONDecodeError as e:
                raise JsonDecodeError(
                    str(e)
                )

* * *

# 18\. Thiết kế thư mục

Bắt đầu từ buổi này, dự án có thể tổ chức như sau:
    
    
    httpclient/
    │
    ├── client.py
    ├── api.py
    ├── response.py
    ├── headers.py
    ├── exceptions.py
    ├── auth.py
    ├── retry.py
    ├── downloader.py
    └── examples/

Trong đó:

  * `client.py`: `HttpClient`
  * `api.py`: `ApiClient`
  * `response.py`: `ApiResponse`
  * `exceptions.py`: các ngoại lệ tùy chỉnh 



* * *

# 19\. Ví dụ hoàn chỉnh
    
    
    client = ApiClient()
    
    response = client.get_json(
        "https://httpbin.org/get",
        params={
            "page": 1,
            "limit": 10
        }
    )
    
    print(response["args"])

* * *

POST:
    
    
    response = client.post_json(
        "https://httpbin.org/post",
        {
            "name": "Alice",
            "age": 20
        }
    )
    
    print(response)

* * *

# 20\. Hướng tới Generic API Client

Sau vài buổi nữa, chúng ta sẽ phát triển `ApiClient` thành:
    
    
    client = ApiClient(
        base_url="https://api.github.com",
        token="..."
    )
    
    repos = client.get_json("/user/repos")

Hoặc:
    
    
    client = ApiClient(
        base_url="https://api.openai.com/v1",
        token="..."
    )
    
    models = client.get_json("/models")

Đây là nền tảng của một SDK chuyên nghiệp.

* * *

# Những lỗi thường gặp

## 1\. Gọi `json.loads()` trên HTML
    
    
    json.loads("<html>...</html>")

❌ Phát sinh `JSONDecodeError`.

* * *

## 2\. Quên `Content-Type`

Gửi JSON nhưng không đặt:
    
    
    Content-Type:
    application/json

Server có thể không hiểu dữ liệu.

* * *

## 3\. Không kiểm tra kiểu phản hồi

Một số API trả về:
    
    
    Content-Type:
    text/plain

Hoặc:
    
    
    text/html

Đừng giả định rằng mọi phản hồi đều là JSON.

* * *

# Bài tập thực hành

### Bài 1

Viết lớp:
    
    
    class ApiResponse:

Gồm:

  * `status`
  * `headers`
  * `url`
  * `data`



Sử dụng `@dataclass`.

* * *

### Bài 2

Viết:
    
    
    class ApiClient(HttpClient):

Có:

  * `get_json()`
  * `post_json()`
  * `put_json()`
  * `delete_json()`



Các phương thức nên tự động:

  * gửi/nhận JSON 
  * chuyển đổi giữa `dict` và JSON 



* * *

### Bài 3

Viết ngoại lệ:
    
    
    ApiError
    
    UnexpectedContentType
    
    JsonDecodeError

Và sử dụng chúng trong `ApiClient`.

* * *

### Bài 4

Gọi API:
    
    
    https://httpbin.org/post

Gửi:
    
    
    {
        "framework": "urllib",
        "language": "Python",
        "version": 3
    }

In ra:

  * Status Code 
  * Content-Type của phản hồi 
  * JSON server trả về (`json` trong phản hồi) 



* * *

# Tổng kết

Trong buổi 6, bạn đã xây dựng nền tảng để làm việc với REST API hiện đại:

  * Chuyển đổi dữ liệu giữa `dict`, JSON và `bytes`. 
  * Thiết kế `ApiResponse` để đóng gói phản hồi. 
  * Xây dựng `ApiClient` kế thừa từ `HttpClient`. 
  * Tự động hóa việc gửi và nhận JSON. 
  * Kiểm tra `Content-Type` và xử lý lỗi phân tích JSON. 
  * Thiết kế các ngoại lệ chuyên biệt cho tầng API. 



Ở **buổi 7** , chúng ta sẽ chuyển sang **Download File chuyên nghiệp** , bao gồm:

  * tải file theo từng khối (`chunk`), 
  * hiển thị tiến độ tải (progress), 
  * hỗ trợ tiếp tục tải (`Range`), 
  * kiểm tra `Content-Length`, 
  * và xây dựng lớp `Downloader` có thể tái sử dụng trong các dự án thực tế như crawler, trình cập nhật (updater) hoặc trình quản lý tải xuống.

