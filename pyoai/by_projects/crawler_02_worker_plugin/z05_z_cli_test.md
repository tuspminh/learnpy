Đây là điểm mà rất nhiều người thiết kế framework bỏ qua. **CLI test không phải để người dùng cuối sử dụng**, mà là **công cụ dành cho lập trình viên** để kiểm tra từng tầng của framework độc lập.

Tôi thường chia CLI thành **2 nhóm**:

```
crawler
│
├── dev/          ← chỉ dành cho developer
│
└── crawl/        ← command thực tế
```

Ví dụ:

```bash
crawler dev plugin list
crawler dev plugin doctor mock
crawler dev http get https://...
crawler dev parser book novelbin url
crawler dev worker run mock
crawler crawl novelbin https://...
```

---

# Ví dụ 1: Test Plugin

Giả sử đang viết plugin NovelBin.

Bạn không muốn chạy cả Worker.

Chỉ muốn biết parser có lấy đúng tên truyện hay không.

CLI:

```bash
crawler dev plugin book novelbin \
    "https://novelbin.com/abc"
```

CLI làm gì?

```
CLI

↓

Load plugin

↓

plugin.get_book(url)

↓

In Book Model
```

Code:

```python
@click.command()
@click.argument("plugin_name")
@click.argument("url")
def book(plugin_name, url):

    plugin = registry.get(plugin_name)

    book = plugin.get_book(url)

    pprint(book.to_dict())
```

Output

```text
Title:
Đấu Phá Thương Khung

Author:
Thiên Tằm Thổ Đậu

Status:
Completed
```

Không có SQLite.

Không Worker.

Không Queue.

Chỉ test plugin.

---

# Ví dụ 2: Test Chapter Parser

```
crawler dev plugin chapter \
    novelbin \
    https://.../chapter-1
```

CLI

↓

```
plugin.get_chapter()

↓

print(content)
```

Output

```
Chapter 1

Lorem ipsum...

...
```

Nếu parser sai sẽ biết ngay.

---

# Ví dụ 3: Test HTTP

Giả sử plugin lỗi.

Không biết:

* website die
* requests lỗi
* proxy lỗi

Ta test:

```
crawler dev http get https://novelbin.com
```

CLI

↓

```
HttpClient.get()

↓

Response
```

Output

```
Status : 200

Elapsed : 0.63s

Encoding : utf-8

Length : 450 KB
```

---

# Ví dụ 4: Test XPath

Đây là command tôi dùng nhiều nhất.

```
crawler dev xpath \
    page.html \
    "//h1/text()"
```

Output

```
Đấu Phá Thương Khung
```

Không cần sửa code.

Chỉ sửa XPath.

---

# Ví dụ 5: Test CSS Selector

```
crawler dev css \
    page.html \
    ".book-title::text"
```

Output

```
Đấu Phá Thương Khung
```

---

# Ví dụ 6: Test Worker

Giả sử muốn test Worker.

Không muốn gọi Internet.

Ta dùng MockPlugin.

```
crawler dev worker run mock
```

Luồng:

```
Worker

↓

MockPlugin

↓

Book

↓

Repository(Mock)

↓

Done
```

Không có HTTP.

---

# Ví dụ 7: Test Repository

```
crawler dev repo insert-book
```

↓

```
Book()

↓

Repository.save()

↓

SQLite
```

Output

```
Insert OK

Book ID = 10
```

---

# Ví dụ 8: Test Database

```
crawler dev db schema
```

Output

```
Tables

book

chapter

author

image
```

---

# Ví dụ 9: Test Serialization

```
crawler dev model serialize
```

↓

```
Book

↓

to_dict()

↓

json
```

Output

```json
{
  "title": "...",
  "author": "..."
}
```

---

# Ví dụ 10: Test toàn bộ Plugin

Đây là command cực kỳ hữu ích.

```
crawler dev plugin doctor novelbin
```

Nó tự chạy toàn bộ bài kiểm tra.

```
✓ metadata

✓ capability

✓ get_book()

✓ get_chapters()

✓ get_chapter()

✓ validate()

✓ serialization()

PASS
```

Nếu lỗi:

```
FAIL

get_book()

Reason

XPath not found
```

---

# Cấu trúc CLI tôi khuyên dùng

```
crawler
│
├── crawl
│   ├── book
│   ├── chapter
│   └── update
│
├── plugin
│   ├── list
│   ├── enable
│   └── disable
│
└── dev
    │
    ├── http
    │   ├── get
    │   ├── head
    │   └── benchmark
    │
    ├── parser
    │   ├── book
    │   ├── chapter
    │   └── content
    │
    ├── xpath
    ├── css
    │
    ├── model
    │
    ├── repo
    │
    ├── db
    │
    ├── worker
    │
    └── plugin
        ├── doctor
        ├── info
        └── benchmark
```

## Một bước tiến xa hơn

Nếu mục tiêu của bạn là xây dựng **framework crawler chuyên nghiệp** (tương tự Scrapy nhưng chuyên cho truyện), tôi sẽ không chỉ dạy từng module riêng lẻ mà sẽ thiết kế toàn bộ framework theo hướng **CLI-first**.

Điều đó có nghĩa là **mọi thành phần đều có thể được kiểm thử độc lập bằng CLI**:

* `crawler dev request` — kiểm tra HTTP client.
* `crawler dev parser` — kiểm tra parser với HTML lưu sẵn hoặc URL.
* `crawler dev plugin` — kiểm tra từng plugin.
* `crawler dev worker` — chạy worker với `MockPlugin`.
* `crawler dev repo` — kiểm tra Repository.
* `crawler dev db` — kiểm tra schema và migration.
* `crawler dev queue` — kiểm tra hàng đợi.
* `crawler dev benchmark` — đo hiệu năng.

Với cách thiết kế này, bạn có thể xác định chính xác lỗi nằm ở HTTP, parser, plugin, worker hay database chỉ bằng một lệnh CLI, thay vì phải chạy toàn bộ ứng dụng rồi lần theo log. Đây cũng là cách các framework lớn thường tổ chức công cụ dành cho lập trình viên.
