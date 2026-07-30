Đúng, trong roadmap Parsel thường có một buổi về **XML Namespace** hoặc **Namespace Support**. Đây là một chủ đề **không quan trọng đối với crawler HTML thông thường**, nhưng **rất quan trọng nếu bạn xử lý XML** như RSS Feed, Sitemap, Atom Feed, SOAP hoặc các API trả về XML.

---

# Vì sao cần Namespace?

Giả sử có XML:

```xml
<?xml version="1.0"?>

<book xmlns="http://example.com/book">

    <title>Python</title>

</book>
```

Nếu dùng XPath:

```python
sel.xpath("//title/text()")
```

Kết quả:

```python
[]
```

Mặc dù rõ ràng XML có `<title>`.

Nguyên nhân là:

```xml
<title>
```

không còn là tag `title`.

Mà thực chất là:

```text
{http://example.com/book}title
```

Đây chính là **namespace**.

---

# Namespace là gì?

Namespace giống như một **tiền tố để tránh trùng tên tag**.

Ví dụ

Không namespace

```xml
<title>
```

Có namespace

```text
book:title
```

hoặc

```text
{http://example.com/book}title
```

Nhờ đó có thể tồn tại đồng thời:

```xml
<book:title>

<movie:title>

<song:title>
```

đều tên `title` nhưng khác ý nghĩa.

---

# Ví dụ RSS Feed

RSS rất hay dùng namespace.

```xml
<rss xmlns:dc="http://purl.org/dc/elements/1.1/">

<item>

<dc:creator>Garden</dc:creator>

</item>

</rss>
```

Nếu viết

```python
sel.xpath("//creator/text()")
```

↓

```python
[]
```

---

Phải đăng ký namespace:

```python
sel.xpath("//dc:creator/text()", namespaces={"dc": "http://purl.org/dc/elements/1.1/"})
```

↓

```python
["Garden"]
```

---

# Ví dụ Sitemap XML

Google Sitemap

```xml
<urlset
xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

<url>

<loc>

https://example.com

</loc>

</url>

</urlset>
```

Sai

```python
sel.xpath("//loc/text()")
```

↓

```python
[]
```

Đúng

```python
sel.xpath(
    "//sm:loc/text()", namespaces={"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
)
```

↓

```python
["https://example.com"]
```

---

# Namespace mặc định

XML

```xml
<root xmlns="http://abc">

<title>Hello</title>

</root>
```

Đây gọi là **default namespace**.

Mặc dù XML không ghi prefix.

Nhưng XPath vẫn phải tự đặt prefix:

```python
namespaces = {"ns": "http://abc"}
```

Sau đó

```python
sel.xpath("//ns:title/text()", namespaces=namespaces)
```

---

# Nhiều namespace

```xml
<root

xmlns:book="http://book"

xmlns:movie="http://movie">

<book:title>

Python

</book:title>

<movie:title>

Avatar

</movie:title>

</root>
```

XPath

```python
sel.xpath(
    "//book:title/text()", namespaces={"book": "http://book", "movie": "http://movie"}
)
```

↓

```python
["Python"]
```

---

# Namespace với CSS

CSS selector **hầu như không dùng namespace** trong Parsel.

Đa số khi xử lý XML namespace, người ta dùng:

```python
.xpath()
```

gần như 100%.

---

# Khi nào bạn sẽ gặp namespace?

Trong crawler thực tế:

### RSS Feed

```text
VNExpress RSS

Tuổi Trẻ RSS

BBC RSS
```

---

### Atom Feed

```xml
<feed>

<entry>

...
```

---

### Sitemap XML

```text
sitemap.xml
```

---

### SOAP

```xml
<soap:Envelope>

...
```

---

### SVG

```xml
<svg>

<path>

...
```

---

### MathML

```xml
<math>

...
```

---

# Khi nào KHÔNG cần học?

Nếu bạn chỉ crawl:

* Truyện
* Báo
* Shopee
* Lazada
* Amazon
* Wikipedia
* HTML thông thường

thì **gần như sẽ không bao giờ dùng namespace**.

99% website hiện nay trả về HTML, không phải XML namespace.

---

# Buổi Namespace trong roadmap thường sẽ học những gì?

Một buổi đầy đủ thường gồm:

1. XML Namespace là gì.
2. Default namespace.
3. Prefix namespace (`dc:`, `media:`, `atom:`...).
4. Tham số `namespaces=` của `Selector.xpath()`.
5. Đăng ký nhiều namespace.
6. Namespace trong RSS.
7. Namespace trong Sitemap.
8. Namespace trong SOAP.
9. Các lỗi thường gặp (`//title` trả về rỗng).
10. Best Practices khi viết parser XML.

---

## Có nên học kỹ không?

Nếu mục tiêu của bạn là **xây dựng crawler truyện bằng Python + Parsel**, mình sẽ đánh giá mức độ quan trọng như sau:

| Chủ đề                | Mức độ |
| --------------------- | -----: |
| CSS Selector          |  ⭐⭐⭐⭐⭐ |
| XPath                 |  ⭐⭐⭐⭐⭐ |
| `get()` / `getall()`  |  ⭐⭐⭐⭐⭐ |
| `re()` / `re_first()` |  ⭐⭐⭐⭐☆ |
| `attrib`              |  ⭐⭐⭐⭐☆ |
| `root`                |  ⭐⭐⭐⭐☆ |
| **Namespace**         |  ⭐⭐☆☆☆ |

Nói cách khác, namespace là kiến thức **nên biết** để xử lý XML, nhưng nếu bạn tập trung vào crawler HTML (như các trang truyện), nó sẽ ít xuất hiện hơn rất nhiều so với các kỹ thuật trích xuất HTML thông thường.
