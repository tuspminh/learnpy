# Buổi 10 — Unicode & HTML Entities

Hôm nay chúng ta học một phần rất quan trọng khi dùng `html2text` để **crawl → clean HTML → Markdown → TTS**:

```text
HTML Entity
     ↓
Unicode character
     ↓
html2text
     ↓
Markdown
```

Nếu không hiểu entity và Unicode, bạn rất dễ gặp output kiểu:

```text
&nbsp;
&amp;
&#39;
&#x27;
```

thay vì:

```text
 
&
'
'
```

---

# 1. HTML Entity là gì?

HTML không phải lúc nào cũng viết trực tiếp ký tự.

Ví dụ:

```html
<p>
Tom &amp; Jerry
</p>
```

`&amp;` đại diện cho:

```text
&
```

Vì vậy:

```text
&amp;
 ↓
&
```

---

# 2. Những entity cơ bản

Một số entity thường gặp:

| HTML       | Ký tự              |
| ---------- | ------------------ |
| `&amp;`    | `&`                |
| `&lt;`     | `<`                |
| `&gt;`     | `>`                |
| `&quot;`   | `"`                |
| `&#39;`    | `'`                |
| `&nbsp;`   | non-breaking space |
| `&copy;`   | ©                  |
| `&hellip;` | …                  |
| `&mdash;`  | —                  |
| `&ndash;`  | –                  |

Ví dụ:

```html
<p>
Tom &amp; Jerry &copy; 2026
</p>
```

về mặt ý nghĩa là:

```text
Tom & Jerry © 2026
```

---

# 3. Có 3 dạng entity chính

## Named entity

```text
&amp;
&nbsp;
&copy;
```

## Decimal numeric entity

```text
&#38;
&#160;
&#169;
```

## Hexadecimal numeric entity

```text
&#x26;
&#xA0;
&#xA9;
```

Ba cách này có thể biểu diễn cùng một Unicode character.

Ví dụ:

```text
&amp;
&#38;
&#x26;
```

đều là:

```text
&
```

---

# 4. Python xử lý entity như thế nào?

Python có module:

```python
import html
```

Ví dụ:

```python
import html

text = "Tom &amp; Jerry"

print(html.unescape(text))
```

Kết quả:

```text
Tom & Jerry
```

---

# 5. `html.unescape()`

Đây là function rất đáng nhớ:

```python
html.unescape(text)
```

Ví dụ:

```python
import html

samples = [
    "&amp;",
    "&lt;",
    "&gt;",
    "&quot;",
    "&#39;",
    "&#x27;",
    "&copy;",
]

for value in samples:
    print(value, "=>", html.unescape(value))
```

---

# 6. Unicode là gì?

Unicode là hệ thống biểu diễn ký tự.

Ví dụ:

```text
A
B
C
```

cũng là Unicode characters.

Tiếng Việt:

```text
ă
â
ê
ô
ơ
ư
đ
```

cũng là Unicode.

Ví dụ:

```python
text = "Tiếng Việt"

print(text)
```

Python 3 xử lý Unicode rất tốt.

---

# 7. `str` trong Python 3

Trong Python 3:

```python
text = "Xin chào Việt Nam"
```

`text` là:

```python
str
```

và `str` đại diện cho text Unicode.

```python
print(type(text))
```

→

```text
<class 'str'>
```

Điểm quan trọng:

> Python `str` không phải là một chuỗi bytes.

---

# 8. `str` và `bytes`

Hai thứ này khác nhau:

```python
text = "Tiếng Việt"

data = text.encode("utf-8")
```

Ta có:

```text
str
 ↓ encode
bytes
```

và ngược lại:

```python
text = data.decode("utf-8")
```

```text
bytes
 ↓ decode
str
```

Mental model:

```text
Unicode text
     │
     │ encode("utf-8")
     ▼
   bytes
     │
     │ decode("utf-8")
     ▼
Unicode text
```

---

# 9. UTF-8

Trong crawler Python, gần như bạn sẽ gặp:

```text
UTF-8
```

Ví dụ:

```python
text = "Xin chào Việt Nam 🇻🇳"

data = text.encode("utf-8")

print(data)
```

Sau đó:

```python
print(data.decode("utf-8"))
```

trở lại:

```text
Xin chào Việt Nam 🇻🇳
```

---

# 10. Entity không phải UTF-8

Đây là điểm rất quan trọng.

```text
&amp;
```

không phải một dạng UTF-8 của `&`.

Nó là:

```text
HTML entity
```

Trong khi:

```text
& → Unicode character
```

và sau đó:

```text
& → UTF-8 bytes
```

là một chuyện khác.

Pipeline:

```text
&amp;
 │
 │ HTML parsing / unescape
 ▼
&
 │
 │ UTF-8 encoding
 ▼
bytes
```

---

# 11. `html2text` và entity

Ví dụ:

```python
import html2text

html = """
<p>
Tom &amp; Jerry
</p>
"""

converter = html2text.HTML2Text()

result = converter.handle(html)

print(result)
```

Bạn sẽ thấy entity được xử lý thành text tương ứng thay vì giữ nguyên `&amp;`.

Điểm cần nhớ:

```text
HTML entity
      ↓
HTML parser/converter
      ↓
Unicode text
```

---

# 12. Entity trong tiếng Việt

Website tiếng Việt có thể chứa:

```html
<p>
Việt Nam &ndash; Đất nước tôi
</p>
```

hoặc:

```html
<p>
Tôi &nbsp; yêu &nbsp; Việt Nam
</p>
```

Nếu xử lý không tốt, bạn có thể nhận:

```text
Việt Nam &ndash; Đất nước tôi
```

hoặc whitespace kỳ lạ.

Trong khi mong muốn:

```text
Việt Nam – Đất nước tôi
```

---

# 13. `&nbsp;` đặc biệt quan trọng

`&nbsp;` là:

```text
non-breaking space
```

Nó không hoàn toàn giống:

```text
" "
```

Thông thường Unicode của nó là:

```text
U+00A0
```

Python:

```python
import html

text = html.unescape("&nbsp;")

print(repr(text))
```

Bạn có thể thấy:

```text
'\xa0'
```

---

# 14. `\xa0` là gì?

Đây là cách Python biểu diễn Unicode character:

```text
U+00A0
```

Ví dụ:

```python
text = "\xa0"

print(repr(text))
```

Kết quả:

```text
'\xa0'
```

Nhìn trên terminal rất khó nhận ra:

```text
space
```

và:

```text
non-breaking space
```

nhưng chúng khác nhau.

---

# 15. Vì sao `&nbsp;` gây phiền cho crawler?

Ví dụ HTML:

```html
<p>
Xin&nbsp;chào&nbsp;bạn
</p>
```

Sau decode:

```text
Xin chào bạn
```

Nhìn giống:

```text
Xin chào bạn
```

nhưng thực tế:

```text
space != NBSP
```

Điều này có thể ảnh hưởng:

* `.split()`
* regex
* search
* text normalization
* TTS
* database comparison

---

# 16. Normalize NBSP

Một cách đơn giản:

```python
text = text.replace("\xa0", " ")
```

Ví dụ:

```python
text = "Xin\xa0chào\xa0bạn"

text = text.replace("\xa0", " ")

print(text)
```

Kết quả:

```text
Xin chào bạn
```

---

# 17. Tốt hơn: dùng `isspace()`

Unicode có rất nhiều whitespace.

Bạn có thể normalize:

```python
def normalize_spaces(text: str) -> str:
    return " ".join(text.split())
```

Ví dụ:

```python
text = "Xin\xa0chào   bạn"

print(normalize_spaces(text))
```

Kết quả:

```text
Xin chào bạn
```

---

# 18. Nhưng đừng dùng `.split()` quá sớm

Đây là lỗi rất phổ biến.

Ví dụ Markdown:

```markdown
# Chapter 1

Đây là đoạn đầu.

Đây là đoạn thứ hai.
```

Nếu:

```python
" ".join(text.split())
```

thì trở thành:

```text
# Chapter 1 Đây là đoạn đầu. Đây là đoạn thứ hai.
```

Bạn đã phá:

```text
paragraph
heading
line break
```

Vì vậy:

> Whitespace normalization phải diễn ra **đúng tầng**.

---

# 19. Entity decoding và Markdown

Có những ký tự có ý nghĩa đặc biệt trong Markdown:

```text
*
_
`
[
]
#
>
```

Ví dụ HTML:

```html
<p>
5 &lt; 10
</p>
```

Output Markdown cần là:

```markdown
5 < 10
```

`<` ở đây là text character, không phải HTML tag.

Đây là một trong những lý do converter phải phân biệt:

```text
HTML syntax
```

và:

```text
text content
```

---

# 20. Entity `&lt;`

HTML:

```html
<p>
if (x &lt; 10):
</p>
```

Sau entity decoding:

```text
if (x < 10):
```

Nếu bạn tự xử lý HTML bằng regex thì rất dễ làm sai.

Ví dụ không nên:

```python
html.replace("&lt;", "<")
```

vì HTML entity processing phức tạp hơn vài replacement đơn giản.

---

# 21. Dùng `html.unescape()` khi nào?

Nếu bạn đang xử lý **plain text đã tách khỏi HTML**, `html.unescape()` rất hữu ích:

```python
import html

text = html.unescape(text)
```

Nhưng nếu bạn đang có:

```text
raw HTML
```

thì không nên tùy tiện:

```python
html.unescape(raw_html)
```

trước khi parse.

---

# 22. Tại sao không unescape raw HTML trước?

Ví dụ:

```html
<p>
5 &lt; 10
</p>
```

Nếu bạn biến thành:

```html
<p>
5 < 10
</p>
```

thì `<` có thể bị hiểu như HTML markup.

Đây là vấn đề:

```text
entity decoding
      ↓
thay đổi ý nghĩa HTML
```

Do đó:

```text
Raw HTML
   ↓
HTML parser
   ↓
text extraction
   ↓
entity decoding / normalization
```

an toàn hơn.

---

# 23. Đừng dùng regex để parse entity toàn bộ HTML

Sai hướng:

```python
import re

html = re.sub(r"&[^;]+;", "", html)
```

hoặc:

```python
html = html.replace("&nbsp;", " ")
```

cho toàn bộ document.

HTML có:

* named entities
* numeric entities
* hex entities
* malformed entities
* entities trong attributes
* entities trong text

Hãy để HTML parser xử lý cấu trúc.

---

# 24. Entity trong attributes

Ví dụ:

```html
<img
    src="image.jpg"
    alt="Tom &amp; Jerry"
>
```

`&amp;` nằm trong:

```text
attribute
```

không phải text node.

Khi parser đọc attribute:

```text
alt
 ↓
Tom & Jerry
```

Đây là một lý do nữa để dùng parser thay vì regex.

---

# 25. Unicode normalization

Đây là phần sâu hơn.

Có thể có hai chuỗi nhìn giống nhau:

```text
é
```

nhưng Unicode representation khác nhau.

### Form 1

```text
é
```

một code point.

### Form 2

```text
e + combining acute accent
```

hai code points.

Hiển thị:

```text
é
```

nhưng representation khác.

---

# 26. Kiểm tra bằng Python

```python
import unicodedata

a = "é"
b = "e\u0301"

print(a == b)
```

Có thể cho:

```text
False
```

dù nhìn bằng mắt:

```text
é
é
```

---

# 27. Unicode normalization với `unicodedata`

Python:

```python
import unicodedata
```

Có:

```python
unicodedata.normalize()
```

Ví dụ:

```python
import unicodedata

a = "é"
b = "e\u0301"

b = unicodedata.normalize("NFC", b)

print(a == b)
```

Kết quả:

```text
True
```

---

# 28. NFC và NFD

Bạn chưa cần nhớ toàn bộ Unicode standard.

Chỉ cần biết:

```text
NFC
NFD
NFKC
NFKD
```

### NFC

Canonical composition.

### NFD

Canonical decomposition.

### NFKC/NFKD

Compatibility normalization.

Trong document processing, thường bắt đầu bằng:

```python
unicodedata.normalize("NFC", text)
```

---

# 29. Vì sao crawler nên quan tâm NFC?

Ví dụ database:

```text
title
```

Một page có:

```text
Café
```

page khác có representation equivalent:

```text
Cafe + combining accent
```

Nếu không normalize:

```python
title1 == title2
```

có thể là:

```text
False
```

Sau NFC:

```text
True
```

Điều này quan trọng khi:

* deduplicate
* search
* indexing
* database comparison

---

# 30. Unicode normalization pipeline

Một text normalization pipeline có thể là:

```text
HTML
 ↓
HTML parser
 ↓
text
 ↓
entity decoding
 ↓
Unicode normalization
 ↓
whitespace normalization
 ↓
Markdown
```

Ví dụ:

```python
import unicodedata
import html


def normalize_text(text: str) -> str:
    text = html.unescape(text)

    text = unicodedata.normalize(
        "NFC",
        text,
    )

    text = text.replace("\xa0", " ")

    return text
```

---

# 31. Nhưng với `html2text` thì sao?

Đừng làm:

```text
raw HTML
 ↓
html.unescape()
 ↓
html2text
```

một cách mặc định.

Thay vào đó:

```text
raw HTML
 ↓
html2text
 ↓
Markdown
 ↓
text normalization
```

nếu mục tiêu là normalize **output text**.

Hoặc:

```text
raw HTML
 ↓
Selectolax / BeautifulSoup
 ↓
clean DOM
 ↓
html2text
 ↓
Markdown
```

tùy pipeline.

---

# 32. Một pipeline production

Với crawler:

```text
                 HTTPX
                   │
                   ▼
                Raw HTML
                   │
                   ▼
               Selectolax
                   │
             ┌─────┴─────┐
             │           │
          Cleaner    URL/Image
             │        Normalizer
             └─────┬─────┘
                   │
                   ▼
                html2text
                   │
                   ▼
                Markdown
                   │
                   ▼
            Text Normalizer
                   │
                   ▼
                 TTS
```

Ở đây:

```text
HTML parsing
```

và:

```text
Unicode normalization
```

là hai vấn đề khác nhau.

---

# 33. Entity trong Markdown code block

Đây là case thú vị.

HTML:

```html
<pre><code>
if (x &lt; 10):
    print("&amp;")
</code></pre>
```

Bạn muốn Markdown:

````markdown
```python
if (x < 10):
    print("&")
```
````

Không được biến:

```text
&lt;
```

thành:

```text
&amp;lt;
```

hoặc decode sai nhiều lần.

---

# 34. Double escaping

Một lỗi rất hay gặp:

```text
&amp;
```

decode một lần:

```text
&
```

Nếu xử lý lại không đúng, có thể tạo:

```text
&amp;
```

lần nữa.

Hoặc:

```text
&amp;amp;
```

là dạng double-encoded.

Ví dụ:

```python
import html

text = "&amp;amp;"

print(html.unescape(text))
```

→

```text
&amp;
```

Decode lần nữa:

```python
text = html.unescape(text)

print(html.unescape(text))
```

→

```text
&
```

Vì vậy:

> Đừng `unescape()` nhiều lần nếu không có lý do rõ ràng.

---

# 35. Tạo test entity

Hãy tạo test suite:

```python
import html2text

html = """
<p>Tom &amp; Jerry</p>
<p>5 &lt; 10</p>
<p>10 &gt; 5</p>
<p>&copy; 2026</p>
<p>&hellip;</p>
<p>&nbsp;</p>
"""

converter = html2text.HTML2Text()

result = converter.handle(html)

print(repr(result))
```

`repr()` rất hữu ích để phát hiện:

```text
\xa0
\n
```

---

# 36. Test tiếng Việt

Hãy test:

```python
html = """
<h1>Tiếng Việt</h1>

<p>
Xin chào Việt Nam.
</p>

<p>
Cà phê, phở, bánh mì.
</p>

<p>
Trường mầm non &amp; giáo viên.
</p>
"""
```

Đây là loại test bạn nên luôn có trong crawler.

---

# 37. Test emoji

Unicode không chỉ có chữ cái.

```python
html = """
<p>
Python 🐍
</p>

<p>
Việt Nam 🇻🇳
</p>

<p>
❤️ Python
</p>
"""
```

Converter phải giữ Unicode.

Đừng biến mọi thứ thành ASCII:

```python
text.encode("ascii", errors="ignore")
```

trừ khi bạn thực sự có lý do.

---

# 38. Đây là một anti-pattern

Không nên:

```python
text.encode(
    "ascii",
    errors="ignore",
).decode()
```

vì:

```text
Tiếng Việt
```

có thể trở thành:

```text
Ting Vit
```

và:

```text
🇻🇳 ❤️
```

có thể biến mất.

---

# 39. UTF-8 khi lưu file

Nếu ghi Markdown:

```python
from pathlib import Path

Path("article.md").write_text(
    markdown,
    encoding="utf-8",
)
```

Đây là cách rõ ràng.

Đọc lại:

```python
markdown = Path("article.md").read_text(
    encoding="utf-8",
)
```

---

# 40. SQLite và Unicode

SQLite lưu text Unicode tốt.

Ví dụ:

```python
cursor.execute(
    """
    INSERT INTO chapters(title, content)
    VALUES (?, ?)
    """,
    (
        "Chương 1 – Tiếng Việt",
        markdown,
    ),
)
```

Không cần tự encode:

```python
markdown.encode("utf-8")
```

trước khi đưa vào SQLite.

Hãy để Python DB API xử lý `str`.

---

# 41. TTS và Unicode

Đây là nơi bài học này liên quan trực tiếp đến app TTS.

Input:

```text
Xin\xa0chào Việt Nam…
```

có thể gây behavior không mong muốn tùy engine.

Một bước normalization:

```python
import unicodedata


def normalize_for_tts(text: str) -> str:
    text = unicodedata.normalize("NFC", text)

    text = text.replace("\xa0", " ")

    return text
```

Sau đó:

```text
Markdown
 ↓
extract text
 ↓
normalize
 ↓
TTS
```

---

# 42. Đừng nhầm Unicode normalization với whitespace normalization

Hai việc khác nhau:

### Unicode normalization

```text
e + combining accent
        ↓
é
```

### Whitespace normalization

```text
Xin   chào
        ↓
Xin chào
```

Có thể pipeline:

```text
Unicode normalization
        ↓
Whitespace normalization
```

nhưng không phải lúc nào cũng cần áp dụng cả hai.

---

# 43. Hàm normalize thực tế

Một phiên bản đơn giản:

```python
import unicodedata


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)

    text = text.replace("\xa0", " ")

    return text
```

Nếu cần collapse whitespace:

```python
def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text)

    text = text.replace("\xa0", " ")

    return " ".join(text.split())
```

Nhưng nhớ:

> Phiên bản thứ hai có thể phá Markdown structure.

Chỉ dùng nó cho **plain text**, không dùng mù quáng cho Markdown.

---

# 44. Markdown và Unicode

Markdown hoàn toàn có thể chứa Unicode:

```markdown
# Tiếng Việt 🇻🇳

Xin chào.

Đây là **Python** 🐍.

© 2026
```

Không cần chuyển sang ASCII.

Vì vậy:

```text
HTML
 ↓
html2text
 ↓
Unicode Markdown
```

là pipeline hoàn toàn bình thường.

---

# 45. Bài tập 1

Chạy:

```python
import html

samples = [
    "&amp;",
    "&lt;",
    "&gt;",
    "&quot;",
    "&#39;",
    "&#x27;",
    "&copy;",
    "&hellip;",
]

for item in samples:
    print(f"{item:10} => {html.unescape(item)}")
```

Hãy kiểm tra kết quả.

---

# 46. Bài tập 2 — NBSP

```python
text = "Xin\xa0chào\xa0bạn"

print(text)
print(repr(text))
```

Sau đó:

```python
text = text.replace("\xa0", " ")

print(repr(text))
```

Bạn sẽ thấy sự khác biệt.

---

# 47. Bài tập 3 — Unicode normalization

```python
import unicodedata

a = "é"
b = "e\u0301"

print(a == b)

b = unicodedata.normalize("NFC", b)

print(a == b)
```

Đây là bài tập rất quan trọng.

---

# 48. Bài tập 4 — HTML entity

Chuyển HTML:

```html
<article>
    <h1>Python &amp; Unicode</h1>

    <p>
        Tiếng Việt rất đẹp.
    </p>

    <p>
        5 &lt; 10 &amp;&amp; 20 &gt; 10
    </p>

    <p>
        Copyright &copy; 2026
    </p>
</article>
```

qua:

```python
html2text.HTML2Text()
```

và kiểm tra:

```python
print(repr(result))
```

---

# 49. Bài tập 5 — Entity + TTS

Viết:

```python
def normalize_for_tts(text: str) -> str:
    ...
```

Yêu cầu:

```text
NFC normalize
+
NBSP → normal space
```

Input:

```python
text = "Xin\xa0chào Việt Nam"
```

Output mong muốn về mặt hiển thị:

```text
Xin chào Việt Nam
```

---

# 50. Bài tập 6 — Double entity

Test:

```python
import html

samples = [
    "&amp;",
    "&amp;amp;",
    "&amp;amp;amp;",
]

for value in samples:
    print(value)
    print("  1:", html.unescape(value))
    print("  2:", html.unescape(html.unescape(value)))
```

Mục tiêu là hiểu tại sao **decode entity nhiều lần có thể nguy hiểm**.

---

# 51. Bài tập 7 — Production test

Tạo một HTML chứa:

```text
Tiếng Việt
NBSP
emoji
HTML entities
numeric entities
hex entities
Markdown special characters
code
```

Ví dụ:

```html
<article>

<h1>Python &amp; Unicode 🐍</h1>

<p>
Xin&nbsp;chào Việt Nam 🇻🇳
</p>

<p>
5 &lt; 10 &amp;&amp; 20 &gt; 10
</p>

<p>
Copyright &copy; 2026
</p>

<pre><code>
if (x &lt; 10):
    print("&amp;")
</code></pre>

</article>
```

Sau đó chạy:

```python
converter = html2text.HTML2Text()

result = converter.handle(html)

print(result)
print(repr(result))
```

---

# 52. Mental model của Buổi 10

Đây là phần quan trọng nhất:

```text
                 RAW HTML
                    │
                    ▼
               HTML Parser
                    │
                    ▼
               HTML entities
                    │
                    ▼
              Unicode text
                    │
                    ▼
             Unicode normalize
                    │
                    ▼
            Whitespace normalize
                    │
                    ▼
                Markdown
```

Nhưng trong pipeline thực tế, cần phân biệt:

```text
HTML parsing
     ≠
entity decoding
     ≠
Unicode normalization
     ≠
whitespace normalization
```

---

# 53. Architecture cho crawler

Từ các buổi trước, hệ thống đang hình thành:

```text
                     HTTPX
                       │
                       ▼
                    HTML
                       │
                       ▼
                  Selectolax
                       │
             ┌─────────┴─────────┐
             │                   │
          Cleaner          URL/Image Parser
             │                   │
             └─────────┬─────────┘
                       │
                       ▼
                   html2text
                       │
                       ▼
                    Markdown
                       │
                       ▼
              Text Normalizer
                       │
             ┌─────────┴─────────┐
             │                   │
           Reader               TTS
```

`html2text` nằm ở giữa:

```text
HTML → Markdown
```

chứ không nên biến thành một **God Object** xử lý tất cả mọi thứ.

---

# 54. Những điều cần nhớ

### ① Entity

```text
&amp; → &
```

### ② `&nbsp;`

```text
&nbsp; → U+00A0
```

có thể normalize:

```python
text.replace("\xa0", " ")
```

### ③ Unicode

Python 3 `str` là Unicode text.

### ④ UTF-8

```text
str
 ↓ encode
bytes
```

### ⑤ NFC

```python
unicodedata.normalize("NFC", text)
```

hữu ích cho canonical Unicode normalization.

### ⑥ Không decode raw HTML tùy tiện

Không nên:

```text
raw HTML
 ↓
html.unescape()
 ↓
HTML parser
```

một cách mặc định.

### ⑦ Không normalize whitespace mù quáng

```python
" ".join(text.split())
```

có thể phá Markdown.

---

## Bài tập tổng hợp cuối buổi

Hãy tự xây một function:

```python
def normalize_document_text(text: str) -> str:
    ...
```

với yêu cầu:

```text
1. NFC normalization
2. NBSP → normal space
3. Không làm mất tiếng Việt
4. Không làm mất emoji
5. Không phá newline
```

Sau đó test:

```python
text = """
Xin\xa0chào Việt Nam 🇻🇳

Việt Nam rất đẹp.

Python 🐍
"""
```

Nếu làm được bài này, bạn đã nắm được nền tảng quan trọng để sang **Buổi 11 — Whitespace & Newline**, nơi chúng ta sẽ đi sâu vào một trong những vấn đề khó nhất của HTML → Markdown:

```text
HTML whitespace
      ↓
DOM whitespace
      ↓
html2text
      ↓
Markdown newline
      ↓
paragraph
      ↓
TTS text
```

và đặc biệt là tại sao `<br>`, `<p>`, `<div>`, `<pre>`, indentation và nhiều newline liên tiếp lại cho output rất khác nhau.
