# Buổi 8 — Form Data trong `primp`

Theo roadmap của chúng ta:

```text
06. POST
07. JSON
08. Form Data   ← hôm nay
09. Cookies
10. Redirect
```

Mục tiêu hôm nay là hiểu rõ:

* `data=`
* `application/x-www-form-urlencoded`
* form HTML `<form>`
* nhiều field
* upload file và vì sao nó khác Form Data
* `data=` vs `json=`
* ứng dụng vào crawler

---

## 1. Form Data là gì?

Khi HTML có form:

```html
<form method="POST">
    <input name="username">
    <input name="password">
    <button type="submit">Login</button>
</form>
```

Browser có thể gửi dữ liệu dạng:

```text
username=alice&password=123456
```

Đây là kiểu:

```text
application/x-www-form-urlencoded
```

Trong `primp`, ta thường sử dụng:

```python
response = client.post(
    url,
    data={
        "username": "alice",
        "password": "123456",
    },
)
```

---

# 2. `data=` khác `json=`

Đây là điểm quan trọng nhất của bài.

### JSON

```python
response = client.post(
    url,
    json={
        "username": "alice",
        "age": 25,
    },
)
```

Body về logic:

```json
{
    "username": "alice",
    "age": 25
}
```

Content-Type thường là:

```text
application/json
```

---

### Form

```python
response = client.post(
    url,
    data={
        "username": "alice",
        "age": 25,
    },
)
```

Body về logic:

```text
username=alice&age=25
```

Content-Type:

```text
application/x-www-form-urlencoded
```

---

## 3. Test với httpbin

Chúng ta dùng:

```text
https://httpbin.org/post
```

để quan sát request.

Code hoàn chỉnh:

```python
import primp


def main():
    client = primp.Client()

    response = client.post(
        "https://httpbin.org/post",
        data={
            "username": "alice",
            "age": "25",
        },
    )

    print("Status:", response.status_code)
    print("URL:", response.url)

    print()
    print("Response:")

    data = response.json()

    print("Form:")
    print(data["form"])


if __name__ == "__main__":
    main()
```

Kết quả sẽ có dạng:

```text
Status: 200
URL: https://httpbin.org/post

Response:
Form:
{
    'username': 'alice',
    'age': '25'
}
```

---

# 4. Form Data thực chất được gửi như thế nào?

Ta viết:

```python
data={
    "username": "alice",
    "age": "25",
}
```

HTTP body tương ứng về mặt ý nghĩa:

```text
username=alice&age=25
```

Nếu có khoảng trắng:

```python
data={
    "name": "Alice Nguyen",
}
```

thì dữ liệu sẽ được URL-encode tương ứng.

Không nên tự nối chuỗi:

```python
body = "username=" + username + "&age=" + age
```

Hãy để HTTP client xử lý encoding.

---

# 5. Form có nhiều field

Ví dụ:

```html
<form method="POST">

    <input name="username">

    <input name="email">

    <input name="password">

    <input name="age">

    <select name="country">
        ...
    </select>

</form>
```

Ta gửi:

```python
form_data = {
    "username": "alice",
    "email": "alice@example.com",
    "password": "secret",
    "age": "25",
    "country": "VN",
}

response = client.post(
    "https://httpbin.org/post",
    data=form_data,
)
```

Điểm cần nhớ:

> Key trong dictionary chính là giá trị của thuộc tính `name` của HTML form.

Ví dụ:

```html
<input name="username">
```

thì:

```python
{
    "username": "..."
}
```

---

# 6. Checkbox

HTML:

```html
<input
    type="checkbox"
    name="remember"
    value="yes"
>
```

Nếu checkbox được chọn:

```python
data = {
    "remember": "yes",
}
```

Nếu không chọn thì thông thường field này **không được gửi**.

Đây là một chi tiết quan trọng khi crawler mô phỏng form.

---

# 7. Select

HTML:

```html
<select name="category">
    <option value="novel">Novel</option>
    <option value="comic">Comic</option>
</select>
```

Nếu chọn Novel:

```python
data = {
    "category": "novel",
}
```

Không gửi:

```python
data = {
    "category": "Novel",
}
```

nếu server thực sự yêu cầu value:

```text
novel
```

Vì vậy khi crawl form, cần nhìn:

```html
<option value="novel">
```

chứ không chỉ nhìn text hiển thị.

---

# 8. Hidden input

Đây là thứ crawler rất hay gặp.

Ví dụ:

```html
<form method="POST">

    <input
        type="hidden"
        name="csrf_token"
        value="abc123"
    >

    <input
        name="username"
    >

</form>
```

Request phải có:

```python
data = {
    "csrf_token": "abc123",
    "username": "alice",
}
```

Nếu bỏ:

```text
csrf_token
```

server có thể từ chối request.

---

# 9. Form + Query Parameters

POST vẫn có thể có query string.

Ví dụ:

```python
response = client.post(
    "https://httpbin.org/post",
    params={
        "source": "crawler",
    },
    data={
        "username": "alice",
        "password": "123456",
    },
)
```

Conceptually:

```text
URL:
https://httpbin.org/post?source=crawler

Body:
username=alice&password=123456
```

Đây là hai nơi dữ liệu khác nhau:

```text
Request
│
├── URL
│    └── Query Parameters
│
└── Body
     └── Form Data
```

---

# 10. Form Data + Headers

Ta có thể thiết lập headers:

```python
response = client.post(
    "https://httpbin.org/post",
    headers={
        "Accept": "application/json",
    },
    data={
        "username": "alice",
        "password": "123456",
    },
)
```

Nhưng không nên tùy tiện tự đặt:

```python
"Content-Type": "application/x-www-form-urlencoded"
```

nếu `primp` đã tự xử lý phù hợp với `data=`.

Nguyên tắc:

> Hãy để HTTP client quản lý những header có thể suy ra từ cách bạn truyền body.

---

# 11. Form Data với tiếng Việt

Ví dụ:

```python
data = {
    "keyword": "truyện tiên hiệp",
    "author": "Nguyễn Văn A",
}
```

```python
response = client.post(
    "https://httpbin.org/post",
    data=data,
)
```

Không cần tự:

```python
urllib.parse.quote(...)
```

trước khi truyền vào `data=`.

HTTP client sẽ xử lý encoding.

---

# 12. `data=` không chỉ là dictionary

Về mặt API, `data` có thể được dùng cho body dữ liệu khác tùy cách bạn truyền.

Nhưng trong bài này, trường hợp quan trọng nhất là:

```python
data={
    "field1": "value1",
    "field2": "value2",
}
```

→ form-urlencoded.

Đây là trường hợp bạn cần nhớ cho crawler.

---

# 13. Form HTML → `primp`

Giả sử Parser tìm được:

```html
<form action="/search" method="post">

    <input
        type="text"
        name="keyword"
    >

    <input
        type="hidden"
        name="page"
        value="1"
    >

</form>
```

Parser có thể phát hiện:

```text
action = /search
method = POST
fields:
    keyword
    page
```

Sau đó application layer tạo request:

```python
data = {
    "keyword": "python",
    "page": "1",
}
```

Fetcher:

```python
response = client.post(
    url,
    data=data,
)
```

Kiến trúc:

```text
HTML
 │
 ▼
Parser
 │
 │ Form definition
 ▼
Application
 │
 │ Request
 ▼
Fetcher
 │
 ▼
Primp
 │
 ▼
Server
```

Parser **không trực tiếp gọi `primp`**.

---

# 14. Ví dụ gần với Novel Crawler

Giả sử website có form tìm kiếm:

```html
<form action="/search" method="post">

    <input
        name="keyword"
        type="text"
    >

    <input
        name="page"
        type="hidden"
        value="1"
    >

</form>
```

Ta có:

```python
import primp


class PrimpFetcher:

    def __init__(self):
        self.client = primp.Client()

    def post_form(
        self,
        url: str,
        data: dict[str, str],
    ):
        return self.client.post(
            url,
            data=data,
        )


def main():
    fetcher = PrimpFetcher()

    response = fetcher.post_form(
        "https://httpbin.org/post",
        {
            "keyword": "tiên hiệp",
            "page": "1",
        },
    )

    print("Status:", response.status_code)

    if response.status_code == 200:
        data = response.json()

        print("Submitted form:")
        print(data["form"])


if __name__ == "__main__":
    main()
```

Đây là abstraction vừa đủ ở giai đoạn hiện tại.

---

# 15. Form Data không phải Multipart Upload

Có một khái niệm rất dễ nhầm:

```text
application/x-www-form-urlencoded
```

và:

```text
multipart/form-data
```

không giống nhau.

### Form URL encoded

```text
username=alice&password=123
```

thường dùng:

```python
data={
    "username": "alice",
    "password": "123",
}
```

### Multipart

Ví dụ form upload:

```html
<form
    method="POST"
    enctype="multipart/form-data"
>
    <input type="file" name="avatar">
</form>
```

Đây là một loại body khác.

Ta sẽ không gộp hai khái niệm này thành "Form Data" một cách máy móc.

---

# 16. `data=` vs `json=` — ghi nhớ

Bảng này rất quan trọng:

|              | `data=`                             | `json=`            |
| ------------ | ----------------------------------- | ------------------ |
| Mục đích     | HTML Form                           | JSON API           |
| Body         | Form encoded                        | JSON               |
| Content-Type | `application/x-www-form-urlencoded` | `application/json` |
| Ví dụ        | Login HTML                          | REST API           |
| Dictionary   | ✅                                   | ✅                  |

### Form

```python
client.post(
    url,
    data={
        "username": "alice",
        "password": "123",
    },
)
```

### JSON

```python
client.post(
    url,
    json={
        "username": "alice",
        "password": "123",
    },
)
```

Hai đoạn code nhìn gần giống nhau nhưng **protocol body khác nhau**.

---

# 17. Một lỗi phổ biến

Sai:

```python
client.post(
    url,
    data='{"username": "alice"}',
)
```

Bạn đang đưa một chuỗi JSON vào `data`, chứ không phải đang sử dụng JSON API đúng cách.

Nếu API yêu cầu JSON:

```python
client.post(
    url,
    json={
        "username": "alice",
    },
)
```

Nếu website yêu cầu HTML form:

```python
client.post(
    url,
    data={
        "username": "alice",
    },
)
```

---

# 18. Bài thực hành tổng hợp

Hãy chạy chương trình này:

```python
import primp


def main():
    client = primp.Client()

    form_data = {
        "username": "alice",
        "email": "alice@example.com",
        "keyword": "truyện tiên hiệp",
        "page": "2",
    }

    response = client.post(
        "https://httpbin.org/post",
        data=form_data,
    )

    print("Status:", response.status_code)
    print("URL:", response.url)

    print()

    result = response.json()

    print("Form data server nhận được:")

    for key, value in result["form"].items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
```

Bạn sẽ thấy:

```text
username: alice
email: alice@example.com
keyword: truyện tiên hiệp
page: 2
```

---

# 19. Bài tập

### Bài 1

Gửi:

```python
{
    "username": "admin",
    "password": "123456",
}
```

bằng `data=`.

Kiểm tra server nhận được gì.

---

### Bài 2

Thử cùng một dữ liệu với:

```python
data={}
```

và:

```python
json={}
```

Sau đó quan sát:

```python
result = response.json()
```

đặc biệt:

```python
result["form"]
result["json"]
```

Bạn sẽ thấy sự khác biệt rất rõ.

---

### Bài 3 — Novel Crawler

Tạo:

```python
class PrimpFetcher:

    def post_form(
        self,
        url: str,
        data: dict[str, str],
    ):
        ...
```

và test:

```python
fetcher.post_form(
    "https://httpbin.org/post",
    {
        "keyword": "python",
        "page": "2",
    },
)
```

---

# 20. Kiến thức cần nhớ sau Buổi 8

```text
POST
 │
 ├── json=
 │     │
 │     └── JSON API
 │
 └── data=
       │
       └── HTML Form
```

Ví dụ:

```python
# HTML Form
client.post(
    url,
    data={
        "username": "alice",
        "password": "123",
    },
)
```

Còn:

```python
# JSON API
client.post(
    url,
    json={
        "username": "alice",
        "password": "123",
    },
)
```

Với crawler, đặc biệt nhớ thêm:

```text
HTML <form>
      │
      ▼
Parser phát hiện field/name/value
      │
      ▼
Application tạo form data
      │
      ▼
PrimpFetcher
      │
      ▼
primp.post(data=...)
```

**Buổi 9 → Cookies trong `primp`**: từ cookie request/response, `Client` giữ cookie, session-like behavior, login flow và cách cookies kết hợp với crawler.
