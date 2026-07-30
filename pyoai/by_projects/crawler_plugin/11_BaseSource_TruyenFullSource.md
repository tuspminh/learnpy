# Bài 11 - Hoàn thiện `BaseSource` + xây dựng `TruyenFullSource`

Ở bài trước chúng ta đã xây dựng **nền móng dùng chung**:

```text-x-trilium-auto
plugins/base/

├── base_source.py
├── http_client.py
├── parser_utils.py
└── exceptions.py
```

Bây giờ chúng ta xây phần **Source Layer**.

Mục tiêu:

Biến plugin TruyenFull thành một module hoàn chỉnh:

```text-x-trilium-auto
truyenfull/

├── manifest.json
├── source.py
├── parser.py
├── selectors.json
└── config.py
```

---

# 1. Vai trò của Source

Cần phân biệt rõ:

## HttpClient

Chỉ biết:

```text-x-trilium-auto
URL

↓

HTML
```

---

## Parser

Chỉ biết:

```text-x-trilium-auto
HTML

↓

Model
```

---

## Source

Điều phối:

```text-x-trilium-auto
URL

↓

HttpClient

↓

Parser

↓

Model
```

---

Ví dụ:

Không gọi:

```text-x-trilium-auto
parser.parse_novel(url)
```

Sai.

Parser không biết tải mạng.

---

Đúng:

```text-x-trilium-auto
source.fetch_novel(url)
```

Source xử lý tất cả.

---

# 2. Tạo BaseSource

File:

```text-x-trilium-auto
plugins/base/base_source.py
```

---

Code:

```text-x-trilium-auto
from abc import ABC, abstractmethod



class BaseSource(ABC):

    name = None


    def __init__(
        self,
        http_client,
        parser
    ):

        self.http = http_client

        self.parser = parser



    @abstractmethod
    def fetch_novel(
        self,
        url
    ):
        pass



    @abstractmethod
    def fetch_chapter(
        self,
        url,
        novel_id
    ):
        pass
```

---

# 3. Vì sao BaseSource cần abstract?

Giả sử có:

```text-x-trilium-auto
plugins/

├── truyenfull

├── tangthuvien

└── metruyen
```

Mỗi plugin bắt buộc có:

```text-x-trilium-auto
fetch_novel()

fetch_chapter()
```

---

Nếu quên:

```text-x-trilium-auto
class ABC
```

Python không báo lỗi ngay.

Sau này rất khó quản lý.

---

# 4. manifest.json

Đây là file mô tả plugin.

File:

```text-x-trilium-auto
plugins/truyenfull/manifest.json
```

---

Nội dung:

```text-x-trilium-auto
{
    "name": "truyenfull",
    "version": "1.0.0",
    "description": "TruyenFull crawler plugin",
    "source": "TruyenFullSource"
}
```

---

Sau này PluginManager đọc:

```text-x-trilium-auto
name
version
class
```

để tự load.

---

# 5. config.py

File:

```text-x-trilium-auto
plugins/truyenfull/config.py
```

---

```text-x-trilium-auto
BASE_URL = "https://truyenfull.vn"


PLUGIN_NAME = "truyenfull"
```

---

Tại sao tách?

Không viết:

```text-x-trilium-auto
url="https://truyenfull.vn"
```

khắp nơi.

---

Sau này đổi:

```text-x-trilium-auto
BASE_URL="https://truyenfull.vn/"
```

chỉ sửa một chỗ.

---

# 6. Tạo TruyenFullSource

File:

```text-x-trilium-auto
plugins/truyenfull/source.py
```

---

Import:

```text-x-trilium-auto
from plugins.base.base_source import BaseSource

from .config import BASE_URL
```

---

Class:

```text-x-trilium-auto
class TruyenFullSource(BaseSource):

    name = "truyenfull"
```

---

# 7. Constructor

Không tạo HttpClient trong Source.

Sai:

```text-x-trilium-auto
class TruyenFullSource:


    def __init__(self):

        self.http=HttpClient()
```

Vì:

- khó test
- phụ thuộc cứng

---

Đúng:

```text-x-trilium-auto
class TruyenFullSource(
    BaseSource
):


    pass
```

Vì BaseSource đã có:

```text-x-trilium-auto
self.http

self.parser
```

---

Khi tạo:

```text-x-trilium-auto
source = TruyenFullSource(
    http_client,
    parser
)
```

---

# 8. fetch_novel()

Đây là hàm quan trọng nhất.

Luồng:

```text-x-trilium-auto
URL

↓

HTTP GET

↓

HTML

↓

Parser

↓

NovelModel
```

---

Code:

```text-x-trilium-auto
def fetch_novel(
    self,
    url
):

    html = self.http.get(
        url
    )


    novel = self.parser.parse_novel(
        html,
        url
    )


    return novel
```

---

# 9. fetch_chapter()

Tương tự:

```text-x-trilium-auto
def fetch_chapter(
    self,
    url,
    novel_id
):

    html = self.http.get(
        url
    )


    chapter = self.parser.parse_chapter(
        html,
        novel_id,
        url
    )


    return chapter
```

---

# 10. fetch_novel_list()

Thêm chức năng lấy danh sách.

Trong BaseSource:

```text-x-trilium-auto
@abstractmethod def fetch_novel_list(self):
    pass
```

---

TruyenFull:

```text-x-trilium-auto
def fetch_novel_list(
    self,
    page=1
):

    url = f"{BASE_URL}/truyen-dang-hot/trang-{page}/"


    html = self.http.get(
        url
    )


    return self.parser.parse_list(
        html
    )
```

---

# 11. fetch_chapter_list()

Một truyện có nhiều chương.

Luồng:

```text-x-trilium-auto
Novel URL

↓

HTML

↓

Parser

↓

ChapterSummaryModel[]
```

---

Code:

```text-x-trilium-auto
def fetch_chapter_list(
    self,
    novel_id,
    url
):

    html = self.http.get(
        url
    )


    return self.parser.parse_chapter_list(
        html,
        novel_id
    )
```

---

# 12. Source hoàn chỉnh

```text-x-trilium-auto
from plugins.base.base_source import BaseSource

from .config import BASE_URL



class TruyenFullSource(
    BaseSource
):

    name="truyenfull"



    def fetch_novel(
        self,
        url
    ):

        html=self.http.get(
            url
        )


        return self.parser.parse_novel(
            html,
            url
        )



    def fetch_novel_list(
        self,
        page=1
    ):

        url=f"{BASE_URL}/truyen-dang-hot/trang-{page}/"


        html=self.http.get(
            url
        )


        return self.parser.parse_list(
            html
        )



    def fetch_chapter_list(
        self,
        novel_id,
        url
    ):

        html=self.http.get(
            url
        )


        return self.parser.parse_chapter_list(
            html,
            novel_id
        )



    def fetch_chapter(
        self,
        url,
        novel_id
    ):

        html=self.http.get(
            url
        )


        return self.parser.parse_chapter(
            html,
            novel_id,
            url
        )
```

---

# 13. Test Source

Tạo:

```text-x-trilium-auto
tests/

    test_truyenfull_source.py
```

---

Mock:

```text-x-trilium-auto
class FakeHttp:

    def get(self,url):

        return "<html></html>"
```

---

Parser giả:

```text-x-trilium-auto
class FakeParser:

    def parse_novel(
        self,
        html,
        url
    ):

        return "NOVEL"
```

---

Test:

```text-x-trilium-auto
source = TruyenFullSource(
    FakeHttp(),
    FakeParser()
)


result = source.fetch_novel(
    "https://test.com"
)


assert result=="NOVEL"
```

---

# 14. Kiến trúc sau bài 11

Hiện tại:

```text-x-trilium-auto
plugins/

├── base/

│   ├── base_source.py

│   ├── http_client.py

│   ├── parser_utils.py

│   └── exceptions.py


└── truyenfull/

    ├── manifest.json

    ├── source.py

    ├── parser.py

    ├── selectors.json

    └── config.py
```

---

Luồng:

```text-x-trilium-auto
CrawlerService

      |

      v

TruyenFullSource

      |

 +----+----+

 |         |

HTTP     Parser

           |

           v

        Models
```

---

# 15. Điểm còn thiếu

Hiện tại chúng ta vẫn tạo thủ công:

```text-x-trilium-auto
source = TruyenFullSource(...)
```

Nhưng hệ thống plugin thật cần:

```text-x-trilium-auto
Đọc thư mục plugins/

↓

Tìm manifest.json

↓

Import source class

↓

Khởi tạo plugin
```

---

Đó chính là:

# Bài 12 - Xây dựng `PluginManager`

Chúng ta sẽ làm:

- Quét thư mục plugin.
- Đọc `manifest.json`.
- Dynamic import bằng Python.
- Đăng ký plugin.
- Load nhiều website cùng lúc.

Sau bài 12, bạn có thể thêm website mới chỉ bằng cách tạo:

```text-x-trilium-auto
plugins/
    website_moi/
```

mà không sửa code lõi.