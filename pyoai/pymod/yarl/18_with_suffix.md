# Buổi 18 — `with_suffix()` trong `yarl`

Hôm nay chúng ta học:

> **`URL.with_suffix()` — thay đổi phần mở rộng (extension) của path cuối cùng.**

Đây là phần tiếp nối trực tiếp từ `with_name()`.

Ví dụ:

```text
https://example.com/book/chapter-10.html
                                      ↑
                                    suffix
```

đổi thành:

```text
https://example.com/book/chapter-10.txt
                                      ↑
                                  suffix mới
```

---

# 1. `suffix` là gì?

Trước hết, hãy xem:

```python
from yarl import URL

url = URL("https://example.com/book/chapter-10.html")

print("path  :", url.path)
print("name  :", url.name)
print("stem  :", url.stem)
print("suffix:", url.suffix)
```

Kết quả:

```text
path  : /book/chapter-10.html
name  : chapter-10.html
stem  : chapter-10
suffix: .html
```

Ta có:

```text
chapter-10.html
│          │
│          └── suffix
└───────────── stem
```

---

# 2. `with_suffix()`

Cú pháp:

```python
new_url = url.with_suffix(".txt")
```

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/book/chapter-10.html")

new_url = url.with_suffix(".txt")

print(new_url)
```

Kết quả:

```text
https://example.com/book/chapter-10.txt
```

Chỉ extension thay đổi:

```text
chapter-10.html
      ↓
chapter-10.txt
```

---

# 3. `with_suffix()` không thay đổi URL gốc

Giống `with_name()`, `with_path()`, `with_fragment()`...

```python
from yarl import URL

url = URL("https://example.com/book/chapter-10.html")

new_url = url.with_suffix(".txt")

print("old:", url)
print("new:", new_url)
```

Kết quả:

```text
old: https://example.com/book/chapter-10.html
new: https://example.com/book/chapter-10.txt
```

URL ban đầu vẫn:

```text
.html
```

---

# 4. `with_suffix()` khác `with_name()` thế nào?

Đây là phần cần nhớ.

URL:

```text
https://example.com/book/chapter-10.html
```

### `with_name()`

```python
url.with_name("chapter-20.html")
```

Kết quả:

```text
https://example.com/book/chapter-20.html
```

Nó thay **toàn bộ name**.

---

### `with_suffix()`

```python
url.with_suffix(".txt")
```

Kết quả:

```text
https://example.com/book/chapter-10.txt
```

Nó chỉ thay **suffix**.

---

So sánh:

```text
with_name()
    chapter-10.html
         ↓
    chapter-20.html


with_suffix()
    chapter-10.html
              ↓
         chapter-10.txt
```

---

# 5. `with_suffix()` giữ nguyên stem

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/chapter-10.html")

new_url = url.with_suffix(".json")

print("old stem:", url.stem)
print("new stem:", new_url.stem)
```

Kết quả:

```text
old stem: chapter-10
new stem: chapter-10
```

Như vậy:

```text
stem
 ↓
chapter-10
```

được giữ nguyên.

Chỉ:

```text
.html
```

đổi thành:

```text
.json
```

---

# 6. Có thể đổi nhiều loại extension

```python
from yarl import URL

url = URL("https://example.com/data/chapter-10.html")

print(url.with_suffix(".txt"))
print(url.with_suffix(".json"))
print(url.with_suffix(".xml"))
print(url.with_suffix(".md"))
print(url.with_suffix(".html"))
```

Kết quả:

```text
https://example.com/data/chapter-10.txt
https://example.com/data/chapter-10.json
https://example.com/data/chapter-10.xml
https://example.com/data/chapter-10.md
https://example.com/data/chapter-10.html
```

---

# 7. Extension phải có dấu `.`

Thông thường hãy truyền:

```python
".txt"
```

thay vì:

```python
"txt"
```

Ví dụ:

```python
url.with_suffix(".txt")
```

là cách rõ ràng.

Không nên tự ghép:

```python
f"{url.stem}.txt"
```

vì bạn đang tự xử lý URL/path bằng string trong khi `yarl` đã có API chuyên dụng.

---

# 8. Query và Fragment vẫn được giữ

Đây là điểm rất quan trọng.

Cho URL:

```text
https://example.com/book/chapter-10.html?page=2#content
```

Ta làm:

```python
from yarl import URL

url = URL("https://example.com/book/chapter-10.html?page=2#content")

new_url = url.with_suffix(".txt")

print(new_url)
```

Kết quả:

```text
https://example.com/book/chapter-10.txt?page=2#content
```

Chỉ:

```text
.html
```

được đổi.

Query:

```text
?page=2
```

vẫn còn.

Fragment:

```text
#content
```

vẫn còn.

---

# 9. `with_suffix("")`

Một use case thú vị là loại bỏ suffix.

```python
from yarl import URL

url = URL("https://example.com/book/chapter-10.html")

new_url = url.with_suffix("")

print(new_url)
```

Kết quả:

```text
https://example.com/book/chapter-10
```

Tức là:

```text
chapter-10.html
      ↓
chapter-10
```

Suffix:

```python
print(new_url.suffix)
```

sẽ không còn `.html`.

---

# 10. URL không có suffix

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/book/chapter-10")

print("name  :", url.name)
print("stem  :", url.stem)
print("suffix:", url.suffix)
```

URL này không có extension kiểu:

```text
.html
.txt
.json
```

nên:

```text
suffix
```

là rỗng.

Sau đó:

```python
new_url = url.with_suffix(".html")

print(new_url)
```

sẽ tạo URL có suffix mới:

```text
https://example.com/book/chapter-10.html
```

---

# 11. Đây là điểm rất hữu ích với crawler

Website truyện thường có URL dạng:

```text
https://example.com/truyen/python/chuong-10
```

không có:

```text
.html
```

Nhưng khi lưu local, chúng ta có thể muốn:

```text
chapter-10.html
```

Cần lưu ý:

> `with_suffix()` thay đổi **URL**, không phải tên file local.

Ví dụ:

```python
url = URL("https://example.com/truyen/python/chuong-10")

html_url = url.with_suffix(".html")

print(html_url)
```

Kết quả:

```text
https://example.com/truyen/python/chuong-10.html
```

Điều này **không có nghĩa server thực sự có URL `.html`**.

Nếu URL thật là:

```text
https://example.com/truyen/python/chuong-10
```

thì bạn không nên dùng:

```python
url.with_suffix(".html")
```

để fetch server.

---

# 12. Phân biệt URL server và filename local

Đây là một bài học kiến trúc rất quan trọng cho Novel Crawler.

Giả sử:

```text
Remote URL:

https://example.com/truyen/python/chuong-10
```

Local file:

```text
data/python/chuong-10.html
```

Hai thứ này khác nhau:

```text
Remote URL
    ↓
yarl.URL


Local file
    ↓
pathlib.Path
```

Không nên biến:

```text
URL manipulation
```

thành:

```text
Local filesystem manipulation
```

Ví dụ:

```python
from pathlib import Path
from yarl import URL

url = URL("https://example.com/truyen/python/chuong-10")

local_file = Path("data/python/chuong-10.html")

print(url)
print(local_file)
```

Ở đây:

```text
URL → yarl
File → pathlib
```

Đây là cách thiết kế sạch hơn.

---

# 13. Một use case hợp lý của `with_suffix()`

Giả sử server thực sự cung cấp:

```text
https://example.com/data/chapter-10.html
```

và API có phiên bản:

```text
https://example.com/data/chapter-10.json
```

Khi đó:

```python
from yarl import URL

html_url = URL("https://example.com/data/chapter-10.html")

json_url = html_url.with_suffix(".json")

print(json_url)
```

Kết quả:

```text
https://example.com/data/chapter-10.json
```

Đây là use case hợp lý.

---

# 14. `with_suffix()` + `with_name()`

Có thể kết hợp.

```python
from yarl import URL

url = URL("https://example.com/book/chapter-10.html")

new_url = url.with_name("chapter-20.html").with_suffix(".txt")

print(new_url)
```

Kết quả:

```text
https://example.com/book/chapter-20.txt
```

Nhưng thực tế đoạn này có thể viết đơn giản hơn:

```python
new_url = url.with_name("chapter-20.txt")
```

Vì vậy:

> Không nên chain nhiều transformation nếu một operation đã đủ rõ ràng.

---

# 15. `with_suffix()` + `with_fragment()`

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/book/chapter-10.html#content")

new_url = url.with_suffix(".txt").with_fragment(None)

print(new_url)
```

Kết quả:

```text
https://example.com/book/chapter-10.txt
```

Quá trình:

```text
chapter-10.html#content
        ↓
chapter-10.txt#content
        ↓
chapter-10.txt
```

---

# 16. `with_suffix()` + `with_query()`

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/book/chapter-10.html?download=false")

new_url = url.with_suffix(".json").with_query({"download": "true"})

print(new_url)
```

Kết quả:

```text
https://example.com/book/chapter-10.json?download=true
```

Ta có:

```text
suffix
   ↓
.html → .json

query
   ↓
download=false → download=true
```

---

# 17. `with_suffix()` + `with_path()`

Ví dụ:

```python
from yarl import URL

url = URL("https://example.com/old/chapter-10.html")

new_url = url.with_path("/new/chapter-20.html").with_suffix(".json")

print(new_url)
```

Kết quả:

```text
https://example.com/new/chapter-20.json
```

---

# 18. Complete example

Hãy chạy nguyên chương trình này:

```python
from yarl import URL


def main():
    url = URL("https://example.com/novel/python/chapter-10.html?page=2#content")

    print("=" * 60)
    print("ORIGINAL")
    print("=" * 60)

    print("URL      :", url)
    print("path     :", url.path)
    print("name     :", url.name)
    print("stem     :", url.stem)
    print("suffix   :", url.suffix)
    print("query    :", url.query_string)
    print("fragment :", url.fragment)

    # --------------------------------------------------

    txt_url = url.with_suffix(".txt")

    print("\n" + "=" * 60)
    print("HTML -> TXT")
    print("=" * 60)

    print("Original :", url)
    print("New      :", txt_url)

    # --------------------------------------------------

    json_url = url.with_suffix(".json")

    print("\n" + "=" * 60)
    print("HTML -> JSON")
    print("=" * 60)

    print(json_url)

    # --------------------------------------------------

    no_suffix = url.with_suffix("")

    print("\n" + "=" * 60)
    print("REMOVE SUFFIX")
    print("=" * 60)

    print(no_suffix)

    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("IMMUTABLE")
    print("=" * 60)

    print("Original suffix:", url.suffix)
    print("TXT suffix     :", txt_url.suffix)
    print("JSON suffix    :", json_url.suffix)
    print("No suffix      :", no_suffix.suffix)


if __name__ == "__main__":
    main()
```

Kết quả chính:

```text
ORIGINAL
https://example.com/novel/python/chapter-10.html?page=2#content

HTML -> TXT
https://example.com/novel/python/chapter-10.txt?page=2#content

HTML -> JSON
https://example.com/novel/python/chapter-10.json?page=2#content

REMOVE SUFFIX
https://example.com/novel/python/chapter-10?page=2#content
```

---

# 19. Một `URLTransformer` nhỏ

Bây giờ ghép các kiến thức từ Buổi 11 → 18:

```python
from yarl import URL


class URLTransformer:
    @staticmethod
    def to_https(url: URL) -> URL:
        return url.with_scheme("https")

    @staticmethod
    def change_host(url: URL, host: str) -> URL:
        return url.with_host(host)

    @staticmethod
    def change_port(url: URL, port: int | None) -> URL:
        return url.with_port(port)

    @staticmethod
    def change_path(url: URL, path: str) -> URL:
        return url.with_path(path)

    @staticmethod
    def rename(url: URL, name: str) -> URL:
        return url.with_name(name)

    @staticmethod
    def change_suffix(url: URL, suffix: str) -> URL:
        return url.with_suffix(suffix)

    @staticmethod
    def strip_fragment(url: URL) -> URL:
        return url.with_fragment(None)


def main():
    url = URL("http://example.com:8000/chapter-10.html?page=2#content")

    result = URLTransformer.to_https(url)
    result = URLTransformer.change_port(result, 443)
    result = URLTransformer.rename(result, "chapter-20.html")
    result = URLTransformer.change_suffix(result, ".json")
    result = URLTransformer.strip_fragment(result)

    print(result)


if __name__ == "__main__":
    main()
```

Kết quả:

```text
https://example.com:443/chapter-20.json?page=2
```

Tất nhiên, trong project thật chúng ta **không cần tạo một class chứa mọi method như thế này**. Ví dụ trên chỉ để bạn thấy toàn bộ nhóm API liên kết với nhau như thế nào.

---

# 20. Một nguyên tắc rất quan trọng

Đừng sử dụng `with_suffix()` chỉ vì thấy nó tiện.

Hãy hỏi:

> **Tôi đang thay đổi URL thật hay đang thay đổi tên file local?**

Nếu là URL:

```python
from yarl import URL

url = URL(...)
url.with_suffix(".json")
```

Nếu là filesystem:

```python
from pathlib import Path

path = Path("chapter-10.html")
path.with_suffix(".json")
```

Hai API khá giống nhau:

```text
yarl.URL
    ↓
URL manipulation

pathlib.Path
    ↓
Filesystem path manipulation
```

Đây là một điểm rất đẹp của Python: mỗi abstraction giải quyết đúng một domain.

---

# 21. `yarl` + `pathlib` trong Novel Crawler

Một kiến trúc tốt có thể là:

```text
                  Parser
                    │
                    ▼
              yarl.URL
                    │
             remote URL
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
       Fetcher            URL Policy
          │
          ▼
       Response
          │
          ▼
       Storage
          │
          ▼
      pathlib.Path
          │
          ▼
   chapter-10.html
```

Tức là:

```text
yarl
 ↓
Internet / URL

pathlib
 ↓
Local filesystem
```

Không trộn hai abstraction.

---

# 22. Tổng kết Buổi 18

Các thuộc tính:

```python
url.name
url.stem
url.suffix
```

Ví dụ:

```text
chapter-10.html
│        │
│        └── suffix = ".html"
└─────────── stem   = "chapter-10"
```

Thay extension:

```python
url.with_suffix(".txt")
```

→

```text
chapter-10.txt
```

Xóa extension:

```python
url.with_suffix("")
```

→

```text
chapter-10
```

Quan trọng nhất:

```text
with_name()
    → thay toàn bộ name

with_suffix()
    → thay suffix

with_path()
    → thay toàn bộ path
```

Và:

> `with_suffix()` thao tác trên **URL**, không phải tự động đổi tên file local.

---

## Bài tập Buổi 18

Cho:

```python
from yarl import URL

url = URL("https://example.com/novel/python/chapter-10.html?page=2#content")
```

### Bài 1

Đổi:

```text
.html
```

thành:

```text
.txt
```

---

### Bài 2

Đổi thành:

```text
.json
```

nhưng phải giữ nguyên:

```text
?page=2#content
```

---

### Bài 3

Xóa suffix:

```text
https://example.com/novel/python/chapter-10?page=2#content
```

---

### Bài 4 — kết hợp

Tạo:

```text
https://example.com/novel/python/chapter-99.txt?page=2
```

từ URL ban đầu bằng cách sử dụng:

```python
with_name()
with_suffix()
with_fragment()
```

---

### Bài 5 — phân biệt domain

Viết hai hàm:

```python
def change_url_suffix(url: URL, suffix: str) -> URL: ...


def change_file_suffix(path: Path, suffix: str) -> Path: ...
```

Một hàm dùng `yarl.URL`, một hàm dùng `pathlib.Path`.

Đây là bài rất đáng làm vì nó củng cố ranh giới:

```text
Remote URL ≠ Local File
```

**Buổi 19 — `parent`** sẽ đi sâu vào việc đi ngược lên URL cha:

```text
https://example.com/novel/python/chapter/10
                                      ↓
https://example.com/novel/python/chapter
                                      ↓
https://example.com/novel/python
                                      ↓
https://example.com/novel
```

và đặc biệt áp dụng vào **xử lý relative URL, crawl theo cấu trúc thư mục/path và URL hierarchy**.
