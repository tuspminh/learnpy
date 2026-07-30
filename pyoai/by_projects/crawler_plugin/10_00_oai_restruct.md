Bạn nhận xét rất đúng. Ở các bài trước mình đã **trộn hai cách tổ chức project khác nhau**, nên cấu trúc bắt đầu bị lệch.

Cấu trúc bạn đưa ra thực ra phù hợp hơn cho một hệ thống **plugin crawler thực sự**:

```text-x-trilium-auto
plugins/
├── base/
│   ├── base_source.py
│   ├── http_client.py
│   ├── parser_utils.py
│   └── exceptions.py
│
├── truyenfull/
│   ├── manifest.json
│   ├── source.py
│   ├── parser.py
│   ├── selectors.json
│   └── config.py
```

Chúng ta sẽ **điều chỉnh lại kiến trúc từ đây**, giữ nguyên các bài đã học nhưng đưa về đúng vị trí.

---

# Kiến trúc chuẩn của hệ thống

Sau khi chỉnh:

```text-x-trilium-auto
novel_crawler/

│
├── app/
│
│
├── plugins/
│   │
│   ├── base/
│   │   │
│   │   ├── base_source.py
│   │   ├── http_client.py
│   │   ├── parser_utils.py
│   │   └── exceptions.py
│   │
│   │
│   └── truyenfull/
│       │
│       ├── manifest.json
│       ├── source.py
│       ├── parser.py
│       ├── selectors.json
│       └── config.py
│
│
├── models/
│
│   ├── novel.py
│   ├── chapter.py
│
│
├── services/
│
│   └── crawler_service.py
│
│
├── repositories/
│
│   ├── novel_repository.py
│   └── chapter_repository.py
│
│
└── database/
    │
    ├── connection.py
    └── schema.sql
```

---

# Vai trò từng phần

## 1. plugins/base

Đây là **framework mini cho crawler**.

Nó không biết TruyenFull.

Nó chỉ cung cấp công cụ.

---

## `base_source.py`

Định nghĩa chuẩn cho mọi website.

Ví dụ:

```text-x-trilium-auto
from abc import ABC, abstractmethod


class BaseSource(ABC):

    name = None


    @abstractmethod
    def fetch_novel(self, url):
        pass


    @abstractmethod
    def fetch_chapter(self, url):
        pass
```

Sau này:

```text-x-trilium-auto
TruyenFullSource
TienHiepSource
TangThuVienSource
```

đều kế thừa.

---

# 2. http_client.py

Đây là phần mình chưa đặt đúng vị trí ở bài trước.

Nó phải nằm:

```text-x-trilium-auto
plugins/base/http_client.py
```

vì:

- TruyenFull dùng.
- Website khác cũng dùng.

---

Ví dụ:

```text-x-trilium-auto
import requests


class HttpClient:


    def __init__(
        self,
        timeout=20
    ):
        self.timeout = timeout



    def get(self, url):

        response = requests.get(
            url,
            timeout=self.timeout,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )


        response.raise_for_status()


        return response.text
```

---

Bây giờ:

```text-x-trilium-auto
TruyenFullSource

        |
        |
        v

HttpClient
```

---

# 3. parser_utils.py

Các hàm dùng chung cho parser.

Ví dụ:

```text-x-trilium-auto
plugins/base/parser_utils.py
```

---

```text-x-trilium-auto
from urllib.parse import urljoin


def absolute_url(
    base,
    url
):

    return urljoin(
        base,
        url
    )
```

---

Safe text:

```text-x-trilium-auto
def safe_text(node):

    if not node:
        return ""

    return node.get_text(
        strip=True
    )
```

---

Safe attribute:

```text-x-trilium-auto
def safe_attr(
    node,
    attr
):

    if not node:
        return ""

    return node.get(attr,"")
```

---

# 4. exceptions.py

Tập trung lỗi crawler.

Ví dụ:

```text-x-trilium-auto
plugins/base/exceptions.py
```

---

```text-x-trilium-auto
class PluginException(Exception):
    pass



class HttpError(
    PluginException
):
    pass



class ParseError(
    PluginException
):
    pass
```

---

Sau này:

```text-x-trilium-auto
except ParseError:
```

Dashboard biết lỗi parser.

---

# Bây giờ tới TruyenFull

## plugins/truyenfull

Đây mới là plugin cụ thể.

---

# 5. config.py

Chứa cấu hình website.

Ví dụ:

```text-x-trilium-auto
BASE_URL = "https://truyenfull.vn"


NAME = "truyenfull"
```

---

Không viết trong source.

Sai:

```text-x-trilium-auto
url="https://truyenfull.vn"
```

---

Đúng:

```text-x-trilium-auto
from .config import BASE_URL
```

---

# 6. selectors.json

Không hard-code CSS.

Ví dụ:

```text-x-trilium-auto
{
    "novel": {

        "title":
        "h3.title",

        "author":
        ".author",

        "cover":
        ".book img"

    },


    "chapter": {

        "title":
        ".chapter-title",

        "content":
        ".chapter-c"

    }
}
```

---

Lợi ích:

Nếu website đổi HTML:

Chỉ sửa:

```text-x-trilium-auto
selectors.json
```

Không sửa Python.

---

# 7. parser.py

Chỉ làm:

```text-x-trilium-auto
HTML

↓

Model
```

Không:

- requests
- sqlite
- thread

---

Ví dụ:

```text-x-trilium-auto
class TruyenFullParser:


    def parse_novel(
        self,
        html
    ):

        ...
```

---

# 8. source.py

Đây là nơi ghép:

```text-x-trilium-auto
HttpClient

+

Parser
```

---

Ví dụ:

```text-x-trilium-auto
from plugins.base.base_source import BaseSource


class TruyenFullSource(
    BaseSource
):


    name="truyenfull"



    def __init__(
        self,
        http,
        parser
    ):

        self.http=http

        self.parser=parser



    def fetch_novel(
        self,
        url
    ):

        html = self.http.get(url)

        return self.parser.parse_novel(
            html
        )
```

---

Luồng:

```text-x-trilium-auto
CrawlerService

        |
        v

TruyenFullSource

        |
        +------------+
        |            |
        v            v

 HttpClient     Parser

                   |
                   v

                Models
```

---

# So sánh với cấu trúc cũ

## Cũ:

```text-x-trilium-auto
plugins/truyenfull

    http.py
    parser.py
    source.py
```

Nhược điểm:

- Mỗi plugin phải copy HTTP.
- Copy utility.
- Khó mở rộng.

---

## Mới:

```text-x-trilium-auto
plugins/base

    http_client.py
    parser_utils.py


plugins/truyenfull

    parser.py
    source.py
```

Ưu điểm:

- Thêm website mới nhanh.
- Code dùng lại.
- Plugin độc lập.
- Có thể load động.

---

# Một điểm cần sửa trong bài 11-12

`CrawlerService` không nên import:

```text-x-trilium-auto
from plugins.truyenfull.source import TruyenFullSource
```

Sai.

Vì Service bị phụ thuộc website.

Đúng:

```text-x-trilium-auto
source = plugin_manager.get(
    "truyenfull"
)
```

Sau này ta sẽ tạo:

```text-x-trilium-auto
PluginManager
```

đọc:

```text-x-trilium-auto
manifest.json
```

và tự load plugin.

---

# Kiến trúc cuối cùng sẽ là:

```text-x-trilium-auto
                 PySide6 Dashboard

                         |
                         v

                 CrawlerService

                         |
                         v

                  PluginManager

                         |
                         v

              TruyenFullSource

                  /          \

                 /            \

          HttpClient       Parser

                               |

                               v

                            Models

                               |

                               v

                         Repository

                               |

                               v

                            SQLite
```

---

Bạn phát hiện điểm lệch này rất tốt. Từ bài tiếp theo mình sẽ tiếp tục theo **cấu trúc plugin chuẩn này**, không dùng cấu trúc cũ nữa.

Bước tiếp theo hợp lý sẽ là:

**Bài 10 (điều chỉnh lại) - Viết hoàn chỉnh** `**plugins/base/http_client.py**` **+** `**parser_utils.py**` **+** `**exceptions.py**` **trước khi đi tiếp Source/Service.**

Vì đây là nền móng của toàn bộ hệ thống.