# Bài 10 (điều chỉnh) - Xây dựng `plugins/base/http_client.py`, `parser_utils.py`, `exceptions.py`

Chúng ta sẽ quay lại xây dựng đúng theo kiến trúc plugin:

```text-x-trilium-auto
plugins/
│
├── base/
│   ├── base_source.py
│   ├── http_client.py
│   ├── parser_utils.py
│   └── exceptions.py
│
└── truyenfull/
    ├── source.py
    ├── parser.py
    ├── selectors.json
    └── config.py
```

Trong bài này chưa làm TruyenFull.

Chúng ta xây **bộ khung dùng chung** cho mọi plugin.

---

# 1. Tại sao phải có `plugins/base`?

Giả sử sau này bạn có:

```text-x-trilium-auto
plugins/

├── truyenfull

├── tangthuvien

├── metruyenchu

└── doctruyen
```

Nếu mỗi plugin tự viết:

```text-x-trilium-auto
requests
BeautifulSoup
retry
logging
```

thì sẽ thành:

```text-x-trilium-auto
truyenfull/http.py

tangthuvien/http.py

metruyen/http.py
```

Code bị lặp.

---

Thiết kế tốt:

```text-x-trilium-auto
                 base

                  |

        +---------+---------+

        |                   |

   TruyenFull          TangThuVien

        |                   |

        +---------+---------+

                  |

             HttpClient
```

---

# Phần 1 - `exceptions.py`

File:

```text-x-trilium-auto
plugins/base/exceptions.py
```

---

## 1.1 Lớp lỗi gốc

```text-x-trilium-auto
class PluginException(Exception):
    """
    Lỗi chung của plugin
    """
    pass
```

---

Tại sao không dùng Exception trực tiếp?

Ví dụ:

```text-x-trilium-auto
except Exception:
```

quá rộng.

Ta muốn:

```text-x-trilium-auto
except PluginException:
```

---

# 1.2 HTTP Error

```text-x-trilium-auto
class HttpError(PluginException):

    def __init__(
        self,
        url,
        message
    ):
        self.url = url
        self.message = message


        super().__init__(
            message
        )
```

Ví dụ:

```text-x-trilium-auto
HttpError

url:
https://truyenfull.vn/abc

message:
Timeout
```

---

# 1.3 Parse Error

```text-x-trilium-auto
class ParseError(PluginException):
    pass
```

Dùng khi:

HTML thay đổi.

Ví dụ:

```text-x-trilium-auto
title = None
```

không tìm thấy.

---

# 1.4 Code hoàn chỉnh

```text-x-trilium-auto
class PluginException(Exception):
    pass



class HttpError(PluginException):

    def __init__(
        self,
        url,
        message
    ):

        self.url = url
        self.message = message

        super().__init__(
            message
        )



class ParseError(PluginException):
    pass
```

---

# Phần 2 - `http_client.py`

Đây là trái tim của crawler.

File:

```text-x-trilium-auto
plugins/base/http_client.py
```

---

# 2.1 Nhiệm vụ

HttpClient chịu trách nhiệm:

- Gửi HTTP request.
- Header.
- Timeout.
- Retry.
- Encoding.
- Xử lý lỗi.

Không làm:

- Parse HTML.
- Lưu database.

---

Luồng:

```text-x-trilium-auto
Source

 |

 v

HttpClient

 |

 v

HTML string
```

---

# 2.2 Phiên bản đơn giản

```text-x-trilium-auto
import requests

from .exceptions import HttpError



class HttpClient:


    def __init__(
        self,
        timeout=20
    ):

        self.timeout = timeout
```

---

# 2.3 Header mặc định

Website thường chặn bot nếu không có User-Agent.

Thêm:

```text-x-trilium-auto
self.headers = {

    "User-Agent":

    "Mozilla/5.0"

}
```

---

Hoàn chỉnh:

```text-x-trilium-auto
class HttpClient:


    def __init__(
        self,
        timeout=20
    ):

        self.timeout = timeout


        self.headers = {

            "User-Agent":
            "Mozilla/5.0"

        }
```

---

# 2.4 Hàm GET

```text-x-trilium-auto
def get(
    self,
    url
):

    try:

        response = requests.get(

            url,

            headers=self.headers,

            timeout=self.timeout

        )


        response.raise_for_status()


        return response.text


    except Exception as e:


        raise HttpError(

            url,

            str(e)

        )
```

---

Bây giờ:

```text-x-trilium-auto
html = client.get(
    "https://truyenfull.vn"
)
```

trả:

```text-x-trilium-auto
"<html>...</html>"
```

---

# 2.5 Thêm retry

Crawler thực tế bắt buộc phải có.

Ví dụ:

```text-x-trilium-auto
Request 1

timeout


Request 2

timeout


Request 3

OK
```

---

Thêm:

```text-x-trilium-auto
def get(
    self,
    url,
    retries=3
):
```

---

Code:

```text-x-trilium-auto
def get(
    self,
    url,
    retries=3
):

    last_error=None


    for i in range(retries):

        try:

            response=requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )


            response.raise_for_status()


            return response.text


        except Exception as e:

            last_error=e



    raise HttpError(
        url,
        str(last_error)
    )
```

---

# 2.6 Tại sao retry nằm trong HttpClient?

Sai:

```text-x-trilium-auto
CrawlerService

retry()
```

Vì:

Service không cần biết HTTP.

---

Đúng:

```text-x-trilium-auto
CrawlerService

       |

HttpClient

       |

retry request
```

---

# Phần 3 - `parser_utils.py`

File:

```text-x-trilium-auto
plugins/base/parser_utils.py
```

---

Nhiệm vụ:

Các hàm dùng chung cho parser.

---

# 3.1 safe_text()

Vấn đề:

```text-x-trilium-auto
node.get_text()
```

nếu:

```text-x-trilium-auto
node=None
```

sẽ lỗi.

---

Tạo:

```text-x-trilium-auto
def safe_text(node):

    if not node:

        return ""


    return node.get_text(
        strip=True
    )
```

---

Ví dụ:

```text-x-trilium-auto
safe_text(None)
```

kết quả:

```text-x-trilium-auto
""
```

---

# 3.2 safe_attr()

Lấy attribute.

Ví dụ:

```text-x-trilium-auto
<img src="abc.jpg">
```

---

Code:

```text-x-trilium-auto
def safe_attr(
    node,
    name
):

    if not node:

        return ""


    return node.get(
        name,
        ""
    )
```

---

Dùng:

```text-x-trilium-auto
cover = safe_attr(
    img,
    "src"
)
```

---

# 3.3 absolute_url()

Website hay trả:

```text-x-trilium-auto
/chapter-1/
```

nhưng ta cần:

```text-x-trilium-auto
https://truyenfull.vn/chapter-1/
```

---

Code:

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

Ví dụ:

```text-x-trilium-auto
absolute_url(
"https://truyenfull.vn",
"/abc"
)
```

Kết quả:

```text-x-trilium-auto
https://truyenfull.vn/abc
```

---

# 3.4 extract_slug()

Rất hay dùng.

```text-x-trilium-auto
from urllib.parse import urlparse


def extract_slug(url):

    path=urlparse(url).path


    return path.strip(
        "/"
    ).split("/")[-1]
```

---

Ví dụ:

```text-x-trilium-auto
extract_slug(
"https://truyenfull.vn/than-dao-dan-ton/"
)
```

Kết quả:

```text-x-trilium-auto
than-dao-dan-ton
```

---

# 3.5 normalize_content()

Dùng cho nội dung chương.

Ví dụ:

Trước:

```text-x-trilium-auto
Hello



World
```

Sau:

```text-x-trilium-auto
Hello

World
```

---

Code:

```text-x-trilium-auto
def normalize_content(
    text
):

    lines=[]


    for line in text.splitlines():

        line=line.strip()


        if line:

            lines.append(line)



    return "\n\n".join(lines)
```

---

# 4. Tổng kết 3 file nền

Bây giờ:

```text-x-trilium-auto
plugins/base/

├── exceptions.py

    PluginException
    HttpError
    ParseError


├── http_client.py

    HttpClient
    get()
    retry()


└── parser_utils.py

    safe_text()
    safe_attr()
    absolute_url()
    extract_slug()
    normalize_content()
```

---

# 5. Kiểm thử nhanh

Tạo:

```text-x-trilium-auto
tests/

    test_http.py

    test_utils.py
```

---

Ví dụ:

```text-x-trilium-auto
from plugins.base.parser_utils import *


def test_slug():

    assert extract_slug(
        "https://truyenfull.vn/abc/"
    )=="abc"
```

---

# 6. Kiến trúc hiện tại

Sau bài này:

```text-x-trilium-auto
Dashboard

    |

CrawlerService

    |

PluginManager

    |

TruyenFullSource

    |

+-----------+

|           |

HttpClient Parser

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

# Bài 11 tiếp theo

Bây giờ nền móng đã đúng.

Chúng ta sẽ xây:

# Bài 11 - Hoàn thiện `BaseSource` + `TruyenFullSource`

Nội dung:

- Thiết kế interface plugin.
- Đọc `manifest.json`.
- Khởi tạo plugin.
- Inject `HttpClient`.
- Inject `Parser`.
- Viết `fetch_novel()`.
- Viết `fetch_chapter_list()`.
- Chuẩn bị cho PluginManager.

Sau bài 11, plugin TruyenFull sẽ trở thành một module độc lập có thể cắm/rút khỏi hệ thống.