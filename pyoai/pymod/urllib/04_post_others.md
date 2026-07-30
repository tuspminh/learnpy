# Khóa học urllib Deep Dive

# Buổi 4: HTTP POST, PUT và DELETE – Làm việc với REST API

Đến buổi này, chúng ta sẽ chuyển từ việc **chỉ đọc dữ liệu (GET)** sang **gửi dữ liệu lên server**.

Đây là kiến thức quan trọng nếu bạn muốn làm:

  * REST API Client 
  * Web Scraper có đăng nhập 
  * Chatbot 
  * AI API (OpenAI, Gemini...) 
  * GitHub API 
  * Docker API 
  * Kubernetes API 



Sau buổi này, bạn sẽ hiểu cách `urllib` gửi dữ liệu qua HTTP.

* * *

# 1\. HTTP Method là gì?

HTTP không chỉ có GET.

Các method phổ biến:

Method| Ý nghĩa  
---|---  
GET| Lấy dữ liệu  
POST| Tạo dữ liệu  
PUT| Cập nhật toàn bộ  
PATCH| Cập nhật một phần  
DELETE| Xóa  
HEAD| Chỉ lấy Header  
OPTIONS| Kiểm tra API hỗ trợ gì  
  
Ví dụ REST API:
    
    
    GET     /users
    GET     /users/5
    POST    /users
    PUT     /users/5
    PATCH   /users/5
    DELETE  /users/5

* * *

# 2\. GET không có Body

GET thường chỉ gửi:
    
    
    GET /users?id=5 HTTP/1.1

Không có dữ liệu phía sau.

* * *

# 3\. POST có Body

POST gửi dữ liệu trong phần Body.

Ví dụ:
    
    
    POST /login HTTP/1.1
    
    username=admin
    
    password=123456

* * *

# 4\. urllib gửi POST như thế nào?

Có hai cách:

  * truyền `data`
  * chỉ định `method`



Ví dụ đơn giản:
    
    
    from urllib.request import Request
    
    req = Request(
        url,
        data=data
    )

Khi `data` khác `None`, `urllib` mặc định sử dụng **POST**.

* * *

# 5\. Data phải là bytes

Đây là lỗi người mới thường gặp.

Sai:
    
    
    data = "name=Alice"

Đúng:
    
    
    data = b"name=Alice"

Hoặc:
    
    
    data = "name=Alice".encode()

* * *

# 6\. urlencode()

Không nên tự nối chuỗi.

Sai:
    
    
    data = (
        "name=Alice"
        "&age=20"
    )

Đúng:
    
    
    from urllib.parse import urlencode
    
    payload = {
        "name": "Alice",
        "age": 20,
    }
    
    data = urlencode(payload).encode()

* * *

# 7\. Gửi POST Form

Ví dụ:
    
    
    from urllib.request import Request
    from urllib.request import urlopen
    from urllib.parse import urlencode
    
    payload = {
        "name": "Alice",
        "age": 20,
    }
    
    data = urlencode(payload).encode()
    
    req = Request(
        "https://httpbin.org/post",
        data=data
    )
    
    with urlopen(req) as response:
        print(response.read().decode())

Server sẽ nhận:
    
    
    {
        "form": {
            "name": "Alice",
            "age": "20"
        }
    }

* * *

# 8\. Content-Type

Body luôn có định dạng.

Ví dụ:
    
    
    application/x-www-form-urlencoded

hoặc
    
    
    application/json

hoặc
    
    
    multipart/form-data

Server phải biết bạn gửi kiểu gì.

* * *

# 9\. Header Content-Type
    
    
    headers = {
        "Content-Type":
        "application/x-www-form-urlencoded"
    }

* * *

# 10\. Gửi JSON

Hiện nay hầu hết REST API đều dùng JSON.

Ví dụ:
    
    
    {
        "name":"Alice",
        "age":20
    }

* * *

# 11\. Chuyển dict thành JSON
    
    
    import json
    
    payload = {
        "name": "Alice",
        "age": 20,
    }
    
    body = json.dumps(payload)

Kết quả:
    
    
    {"name":"Alice","age":20}

* * *

# 12\. Encode
    
    
    body = body.encode("utf-8")

Hoặc:
    
    
    body = json.dumps(payload).encode()

* * *

# 13\. POST JSON
    
    
    import json
    
    from urllib.request import Request
    from urllib.request import urlopen
    
    payload = {
        "name": "Alice",
        "age": 20,
    }
    
    body = json.dumps(payload).encode()
    
    headers = {
        "Content-Type":
        "application/json"
    }
    
    req = Request(
        "https://httpbin.org/post",
        data=body,
        headers=headers
    )
    
    with urlopen(req) as response:
        print(response.read().decode())

Server sẽ trả về:
    
    
    {
        "json": {
            "name": "Alice",
            "age": 20
        }
    }

* * *

# 14\. PUT

Từ Python 3.3+, `Request` cho phép chỉ định method:
    
    
    req = Request(
        url,
        method="PUT"
    )

* * *

Ví dụ:
    
    
    import json
    from urllib.request import Request, urlopen
    
    payload = {
        "name": "Alice",
    }
    
    body = json.dumps(payload).encode()
    
    req = Request(
        "https://httpbin.org/put",
        data=body,
        method="PUT",
        headers={
            "Content-Type":
            "application/json"
        }
    )
    
    with urlopen(req) as r:
        print(r.read().decode())

* * *

# 15\. DELETE

DELETE thường không cần Body.
    
    
    req = Request(
        "https://httpbin.org/delete",
        method="DELETE"
    )

* * *

Ví dụ:
    
    
    from urllib.request import Request
    from urllib.request import urlopen
    
    req = Request(
        "https://httpbin.org/delete",
        method="DELETE"
    )
    
    with urlopen(req) as r:
        print(r.read().decode())

* * *

# 16\. PATCH
    
    
    req = Request(
        url,
        method="PATCH",
        data=body
    )

Không phải server nào cũng hỗ trợ.

* * *

# 17\. HEAD

HEAD chỉ lấy Header.
    
    
    req = Request(
        "https://httpbin.org/get",
        method="HEAD"
    )
    
    with urlopen(req) as r:
        print(r.headers)

Không có Body.

* * *

# 18\. OPTIONS
    
    
    req = Request(
        "https://httpbin.org/get",
        method="OPTIONS"
    )

Server sẽ trả:
    
    
    Allow:
    
    GET
    
    POST
    
    PUT
    
    DELETE

* * *

# 19\. Viết HttpClient
    
    
    import json
    from urllib.request import Request
    from urllib.request import urlopen
    from urllib.parse import urlencode
    
    
    class HttpClient:
    
        def request(
            self,
            method,
            url,
            params=None,
            data=None,
            json_data=None,
            headers=None,
        ):
    
            headers = headers or {}
    
            if params:
                url += "?" + urlencode(params)
    
            body = None
    
            if data:
                body = urlencode(data).encode()
    
                headers.setdefault(
                    "Content-Type",
                    "application/x-www-form-urlencoded",
                )
    
            if json_data:
    
                body = json.dumps(json_data).encode()
    
                headers.setdefault(
                    "Content-Type",
                    "application/json",
                )
    
            request = Request(
                url,
                data=body,
                headers=headers,
                method=method,
            )
    
            with urlopen(request) as response:
                return response.read().decode()

* * *

Sử dụng:
    
    
    client = HttpClient()
    
    print(
        client.request(
            "POST",
            "https://httpbin.org/post",
            json_data={
                "name": "Alice"
            }
        )
    )

* * *

# 20\. Cải tiến với các phương thức tiện ích

Thay vì:
    
    
    client.request("GET", url)

Ta thêm các phương thức:
    
    
    class HttpClient:
        ...
    
        def get(self, url, **kwargs):
            return self.request(
                "GET",
                url,
                **kwargs
            )
    
        def post(self, url, **kwargs):
            return self.request(
                "POST",
                url,
                **kwargs
            )
    
        def put(self, url, **kwargs):
            return self.request(
                "PUT",
                url,
                **kwargs
            )
    
        def delete(self, url, **kwargs):
            return self.request(
                "DELETE",
                url,
                **kwargs
            )

Sử dụng:
    
    
    client = HttpClient()
    
    print(
        client.post(
            "https://httpbin.org/post",
            json_data={
                "hello": "world"
            }
        )
    )

Đây là kiến trúc mà nhiều thư viện HTTP hiện đại áp dụng.

* * *

# Những lỗi thường gặp

## 1\. Quên encode

Sai:
    
    
    data = json.dumps(payload)

Đúng:
    
    
    data = json.dumps(payload).encode()

* * *

## 2\. Sai Content-Type

Gửi JSON nhưng lại để:
    
    
    application/x-www-form-urlencoded

Server có thể trả về:
    
    
    400 Bad Request

* * *

## 3\. Gửi cả `data` và `json_data`

Trong ví dụ `HttpClient` ở trên, nếu truyền cả hai tham số thì `json_data` sẽ ghi đè `data`.

Trong thiết kế thực tế, nên kiểm tra:
    
    
    if data is not None and json_data is not None:
        raise ValueError(
            "Chỉ được truyền một trong data hoặc json_data"
        )

Điều này giúp API rõ ràng và tránh lỗi khó phát hiện.

* * *

# Bài tập thực hành

### Bài 1

Viết hàm:
    
    
    def post_form(url, data):
        ...

Yêu cầu:

  * gửi `application/x-www-form-urlencoded`
  * trả về chuỗi phản hồi. 



* * *

### Bài 2

Viết hàm:
    
    
    def post_json(url, obj):
        ...

Yêu cầu:

  * chuyển `dict` thành JSON 
  * thiết lập `Content-Type: application/json`
  * trả về chuỗi phản hồi. 



* * *

### Bài 3

Mở rộng `HttpClient` với các phương thức:
    
    
    get()
    
    post()
    
    put()
    
    patch()
    
    delete()
    
    head()
    
    options()

Để tất cả đều dùng chung phương thức `request()`.

* * *

### Bài 4

Viết một chương trình gọi các endpoint của `https://httpbin.org`:

  * `GET /get`
  * `POST /post`
  * `PUT /put`
  * `DELETE /delete`



Sau mỗi lần gọi, in ra:

  * HTTP Method 
  * Status Code 
  * Content-Type của phản hồi 
  * 200 ký tự đầu tiên của nội dung phản hồi 



* * *

# Tổng kết

Trong buổi 4, bạn đã học:

  * Sự khác biệt giữa GET, POST, PUT, PATCH, DELETE, HEAD và OPTIONS. 
  * Cách gửi dữ liệu dạng biểu mẫu (`application/x-www-form-urlencoded`). 
  * Cách gửi JSON (`application/json`). 
  * Vai trò của `Content-Type`. 
  * Thiết kế một `HttpClient` có phương thức `request()` làm lõi và các phương thức tiện ích (`get`, `post`, `put`, `delete`) bao quanh. 



Ở **buổi 5** , chúng ta sẽ đi sâu vào **HTTP Header và User-Agent** , tìm hiểu chi tiết về các loại header, cách trình duyệt và API sử dụng chúng, đồng thời xây dựng một hệ thống quản lý header linh hoạt cho `HttpClient`. Đây là nền tảng quan trọng cho crawler, scraper và các ứng dụng giao tiếp với REST API chuyên nghiệp.

