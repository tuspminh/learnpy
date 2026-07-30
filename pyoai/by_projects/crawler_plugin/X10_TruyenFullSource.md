Rất tốt. Chúng ta đã hoàn thành phần khó nhất là **Parser Layer**.

Bây giờ chúng ta bước sang một phần cực kỳ quan trọng trong kiến trúc crawler:

# Bài 10 - Xây dựng `TruyenFullSource`

## Mục tiêu

Sau bài này chúng ta sẽ biến các thành phần rời rạc:

```text-x-trilium-auto
HttpClient

Parser

Urls

Models
```

thành một **plugin có thể sử dụng được**.

Luồng hoàn chỉnh:

```text-x-trilium-auto
Dashboard / Scheduler

          |
          v

   TruyenFullSource

          |

    +-----+------+

    |            |

HttpClient   Parser

    |            |

    +-----+------+

          |

       Models

          |

     Repository

          |

       SQLite
```

---

# 1. Source là gì?

Nhiều người nhầm:

```text-x-trilium-auto
Source = website
```

Không hoàn toàn đúng.

Trong kiến trúc của chúng ta:

```text-x-trilium-auto
Source = Service Adapter
```

Nó là lớp biết:

- Crawl cái gì.
- Gọi URL nào.
- Dùng parser nào.
- Trả dữ liệu gì.

Nó **không biết lưu database**.

---

# 2. Vì sao cần Source?

Nếu không có Source:

Dashboard phải làm:

```text-x-trilium-auto
url = "https://truyenfull.vn..."

html = requests.get(url)

parser.parse(html)

db.save(...)
```

Sai thiết kế.

Dashboard không nên biết:

- URL website.
- HTML.
- CSS selector.
- Parser.

---

Đúng:

Dashboard chỉ cần:

```text-x-trilium-auto
source.fetch_novel(url)
```

---

# 3. Cấu trúc plugin

Hiện tại:

```text-x-trilium-auto
plugins/

    truyenfull/

        urls.py

        selectors.py

        parser.py

        source.py
```

Bây giờ tạo:

```text-x-trilium-auto
source.py
```

---

# 4. BaseSource

Trước khi viết TruyenFullSource, tạo interface chung.

```text-x-trilium-auto
base/

    source.py
```

---

Code:

```text-x-trilium-auto
from abc import ABC, abstractmethod


class BaseSource(ABC):

    name: str


    @abstractmethod
    def fetch_novel(self, url):
        pass


    @abstractmethod
    def fetch_chapter(self, url):
        pass
```

---

Ý nghĩa:

Mọi plugin đều phải có:

```text-x-trilium-auto
fetch_novel()

fetch_chapter()
```

Ví dụ:

```text-x-trilium-auto
TruyenFullSource

TangThuVienSource

MetruyenSource
```

đều giống interface.

---

# 5. Tạo TruyenFullSource

File:

```text-x-trilium-auto
plugins/truyenfull/source.py
```

---

Import:

```text-x-trilium-auto
from base.source import BaseSource

from .urls import TruyenFullUrls

from .parser import TruyenFullParser
```

---

Class:

```text-x-trilium-auto
class TruyenFullSource(BaseSource):

    name = "truyenfull"
```

---

# 6. Dependency Injection

Không nên:

```text-x-trilium-auto
self.http = HttpClient()
self.parser = Parser()
```

bên trong.

Vì khó test.

Nên:

```text-x-trilium-auto
class TruyenFullSource(BaseSource):

    def __init__(
        self,
        http_client,
        parser
    ):
        self.http = http_client
        self.parser = parser
```

---

Bây giờ:

Production:

```text-x-trilium-auto
source = TruyenFullSource(
    HttpClient(),
    TruyenFullParser()
)
```

Test:

```text-x-trilium-auto
source = TruyenFullSource(
    FakeHttpClient(),
    FakeParser()
)
```

Đây là Dependency Injection.

---

# 7. Hàm lấy HTML

Ta có:

```text-x-trilium-auto
self.http.get(url)
```

trả:

```text-x-trilium-auto
html string
```

---

# 8. fetch_novel()

Đây là hàm đầu tiên.

Nhiệm vụ:

```text-x-trilium-auto
URL

↓

download

↓

parse

↓

NovelModel
```

---

Code:

```text-x-trilium-auto
def fetch_novel(self, url):

    html = self.http.get(url)

    return self.parser.parse_novel(
        html,
        url
    )
```

Rất sạch.

---

# 9. fetch_chapter()

Tương tự:

```text-x-trilium-auto
def fetch_chapter(
    self,
    url,
    novel_id
):

    html = self.http.get(url)

    return self.parser.parse_chapter(
        html,
        novel_id,
        url
    )
```

---

# 10. fetch_novel_list()

Thêm chức năng crawl danh sách.

```text-x-trilium-auto
def fetch_novel_list(
    self,
    page=1
):
```

Tạo URL:

```text-x-trilium-auto
url = TruyenFullUrls.newest_page(
    page
)
```

---

Download:

```text-x-trilium-auto
html = self.http.get(url)
```

---

Parse:

```text-x-trilium-auto
return self.parser.parse_list(
    html
)
```

---

# 11. fetch_chapter_list()

Quan trọng.

```text-x-trilium-auto
def fetch_chapter_list(
    self,
    novel_id,
    url
):
```

---

Code:

```text-x-trilium-auto
html = self.http.get(url)


return self.parser.parse_chapter_list(
    html,
    novel_id
)
```

---

# 12. Source hoàn chỉnh

Hiện tại:

```text-x-trilium-auto
class TruyenFullSource:


    name="truyenfull"


    def __init__(
        self,
        http_client,
        parser
    ):

        self.http=http_client

        self.parser=parser



    def fetch_novel_list(self,page):

        url = TruyenFullUrls.newest_page(page)

        html=self.http.get(url)

        return self.parser.parse_list(html)



    def fetch_novel(self,url):

        html=self.http.get(url)

        return self.parser.parse_novel(
            html,
            url
        )



    def fetch_chapter_list(
        self,
        novel_id,
        url
    ):

        html=self.http.get(url)

        return self.parser.parse_chapter_list(
            html,
            novel_id
        )



    def fetch_chapter(
        self,
        novel_id,
        url
    ):

        html=self.http.get(url)

        return self.parser.parse_chapter(
            html,
            novel_id,
            url
        )
```

---

# 13. So sánh trước và sau

## Trước

Dashboard:

```text-x-trilium-auto
requests

BeautifulSoup

CSS Selector

SQLite
```

Biết tất cả.

---

## Sau

Dashboard:

```text-x-trilium-auto
source.fetch_novel(url)
```

Chỉ vậy.

---

# 14. Kiến trúc hiện tại

Sau bài 10:

```text-x-trilium-auto
crawler/

├── base/

│   ├── source.py

│   ├── parser.py

│   └── http.py


plugins/

└── truyenfull/

    ├── urls.py

    ├── selectors.py

    ├── parser.py

    └── source.py
```

---

# 15. Nhưng Source hiện tại còn thiếu

Trong thực tế:

Một crawler không chỉ:

```text-x-trilium-auto
fetch
```

mà còn cần:

```text-x-trilium-auto
sync
retry
resume
status
logging
```

Ví dụ Dashboard muốn:

```text-x-trilium-auto
Cào truyện này

    ↓

Đang tải chương 120/500

    ↓

Lỗi chương 250

    ↓

Retry
```

Source cần phát ra event.

---

# 16. Chuẩn bị bài 11

Bài tiếp theo chúng ta sẽ nâng cấp Source:

# Bài 11 - Xây dựng `CrawlerService`

Chúng ta sẽ tạo tầng Service:

```text-x-trilium-auto
Source
    |
    |
CrawlerService
    |
    |
Repository
```

Service sẽ chịu trách nhiệm:

- Điều khiển quá trình crawl.
- Lưu trạng thái.
- Retry lỗi.
- Resume.
- Pause/Cancel.
- Ghi log.

Đây chính là phần kết nối plugin crawler với Dashboard PySide6 mà bạn muốn xây dựng ban đầu.

Sau bài 11, hệ thống sẽ bắt đầu có hình dạng của một **trình quản lý cào truyện chuyên nghiệp**.