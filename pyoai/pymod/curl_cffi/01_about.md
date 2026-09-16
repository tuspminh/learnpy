

# Buổi 1 — Cài đặt và request đầu tiên

## 1. Cài đặt

```bash
pip install curl_cffi
```

Kiểm tra:

```bash
pip show curl_cffi
```

Hoặc:

```bash
python -c "import curl_cffi; print(curl_cffi.__version__)"
```

---

# 2. Request đơn giản

`curl_cffi` có API khá gần `requests`.

```python
from curl_cffi import requests


response = requests.get("https://example.com")

print(response)
print(response.status_code)
print(response.text)
```

Ví dụ:

```text
<Response [200]>
200
<!doctype html>
<html>
...
```

---

# 3. `Response` là gì?

Sau:

```python
response = requests.get(url)
```

ta nhận được object:

```python
Response
```

Một số thuộc tính quan trọng:

```python
response.status_code
response.headers
response.cookies
response.text
response.content
response.url
response.encoding
```

Ví dụ:

```python
from curl_cffi import requests


response = requests.get("https://example.com")

print("Status:", response.status_code)
print("URL:", response.url)
print("Encoding:", response.encoding)
print("Content-Type:", response.headers.get("content-type"))
```

---

# 4. `text` và `content`

Đây là phần rất quan trọng đối với crawler.

### `response.text`

Trả về:

```python
str
```

Ví dụ:

```python
html = response.text

print(type(html))
```

Kết quả:

```text
<class 'str'>
```

Dùng khi parser nhận HTML:

```python
html = response.text
```

sau đó:

```python
from selectolax.parser import HTMLParser

tree = HTMLParser(html)
```

---

### `response.content`

Trả về:

```python
bytes
```

Ví dụ:

```python
data = response.content

print(type(data))
```

Kết quả:

```text
<class 'bytes'>
```

Phù hợp với:

* hình ảnh
* PDF
* ZIP
* audio
* binary data

Ví dụ:

```python
from curl_cffi import requests


response = requests.get("https://example.com/image.jpg")

data = response.content

with open("image.jpg", "wb") as f:
    f.write(data)
```

---

# 5. Kiểm tra status code

Không nên mặc định rằng request thành công.

```python
response = requests.get("https://example.com")

if response.status_code == 200:
    print("Success")
else:
    print("Failed:", response.status_code)
```

Một số status thường gặp:

```text
200 OK
201 Created
204 No Content

301 Moved Permanently
302 Found
304 Not Modified

400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
408 Request Timeout
429 Too Many Requests

500 Internal Server Error
502 Bad Gateway
503 Service Unavailable
504 Gateway Timeout
```

Trong crawler sau này ta sẽ không xử lý chúng bằng những `if` rải rác khắp code.

Ta sẽ gom thành:

```text
HTTP response
      ↓
ResponseMapper
      ↓
Application-level result
```

---

# 6. `raise_for_status()`

Có thể dùng:

```python
response.raise_for_status()
```

Ví dụ:

```python
from curl_cffi import requests


response = requests.get("https://example.com")

response.raise_for_status()

print(response.text)
```

Nếu HTTP response là lỗi, exception sẽ được raise.

Điều này hữu ích khi viết code đơn giản.

Nhưng với **Fetcher production** của chúng ta, mình sẽ không phụ thuộc hoàn toàn vào `raise_for_status()`.

Ta sẽ map HTTP status thành application-level result.

Ví dụ ý tưởng:

```python
FetchResult(
    success=False,
    status_code=403,
    error=FetchError.BLOCKED,
)
```

Điều này phù hợp hơn với kiến trúc DDD/SOLID mà bạn đang xây.

---

# 7. Request với timeout

Không nên viết crawler kiểu:

```python
requests.get(url)
```

mà không có timeout.

Nên:

```python
response = requests.get(
    "https://example.com",
    timeout=10,
)
```

Ví dụ:

```python
from curl_cffi import requests


try:
    response = requests.get(
        "https://example.com",
        timeout=10,
    )

    print(response.status_code)

except Exception as e:
    print("Request failed:", e)
```

Sau này ta sẽ không để `timeout=10` rải rác.

Ta sẽ có:

```python
HttpClientConfig(
    connect_timeout=5,
    read_timeout=15,
)
```

hoặc một timeout policy riêng.

---

# 8. Một ví dụ hoàn chỉnh

Tạo:

```text
lesson01.py
```

Code:

```python
from curl_cffi import requests


def main():
    url = "https://example.com"

    try:
        response = requests.get(
            url,
            timeout=10,
        )

        print("=" * 50)
        print("URL:", response.url)
        print("STATUS:", response.status_code)
        print("CONTENT-TYPE:", response.headers.get("content-type"))
        print("ENCODING:", response.encoding)
        print("=" * 50)

        response.raise_for_status()

        print(response.text[:500])

    except Exception as e:
        print("Request failed:", e)


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python lesson01.py
```

---

# 9. Bài tập thực hành

Tạo chương trình:

```text
lesson01_exercise.py
```

Yêu cầu:

```text
URL
 ↓
curl_cffi
 ↓
GET
 ↓
in status code
 ↓
in final URL
 ↓
in Content-Type
 ↓
in độ dài response
```

Gợi ý:

```python
from curl_cffi import requests


url = "https://example.com"

response = requests.get(
    url,
    timeout=10,
)

print("Status:", response.status_code)
print("URL:", response.url)
print("Content-Type:", response.headers.get("content-type"))
print("Length:", len(response.content))
```

---

## Điều cần nhớ sau Buổi 1

```text
curl_cffi
   │
   └── requests.get()
          │
          ▼
       Response
          │
          ├── status_code
          ├── headers
          ├── cookies
          ├── text
          ├── content
          ├── url
          └── encoding
```

Và trong **Novel Crawler**:

```text
curl_cffi
    ↓
Infrastructure
    ↓
HttpClient
    ↓
Fetcher
    ↓
HTML
    ↓
Selectolax
```

**Buổi 2** chúng ta sẽ đi vào `requests.get()` thật kỹ: **query parameters, headers, User-Agent và cách `curl_cffi` tạo một HTTP request**, rồi bắt đầu liên hệ trực tiếp với Fetcher mà bạn đã xây bằng `httpx`.
