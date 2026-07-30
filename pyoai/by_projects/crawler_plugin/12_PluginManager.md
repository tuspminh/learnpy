# Bài 12 - Xây dựng `PluginManager` (Hệ thống nạp plugin động)

Đây là một bước rất quan trọng.

Sau bài này hệ thống của chúng ta sẽ không còn phụ thuộc cứng vào:

```text-x-trilium-auto
from plugins.truyenfull.source import TruyenFullSource
```

nữa.

Thay vào đó:

```text-x-trilium-auto
Khởi động chương trình

        |
        v

PluginManager

        |
        v

Đọc plugins/*/manifest.json

        |
        v

Load Source Class

        |
        v

Đăng ký plugin
```

Sau này thêm website mới chỉ cần:

```text-x-trilium-auto
plugins/
|
├── truyenfull/
|
├── tangthuvien/
|
└── metruyen/
```

Không sửa code hệ thống.

---

# 1. Vì sao cần PluginManager?

Hiện tại:

```text-x-trilium-auto
source = TruyenFullSource(
    http,
    parser
)
```

Vấn đề:

Core system biết:

```text-x-trilium-auto
TruyenFull
```

Điều này phá vỡ kiến trúc plugin.

---

Mục tiêu:

Core chỉ biết:

```text-x-trilium-auto
source = plugin_manager.get(
    "truyenfull"
)
```

Nó không cần biết:

- File nào.
- Class nào.
- Import ở đâu.

---

# 2. Cấu trúc mới

Thêm:

```text-x-trilium-auto
novel_crawler/

├── plugins/
│
│   ├── plugin_manager.py   <-- mới
│
│   ├── base/
│   │
│   └── truyenfull/
│
└── app/
```

---

# 3. Ý tưởng manifest.json

Mỗi plugin tự khai báo:

```text-x-trilium-auto
{
    "name": "truyenfull",
    "version": "1.0.0",
    "source": "TruyenFullSource"
}
```

PluginManager đọc:

```text-x-trilium-auto
name

source class
```

---

# 4. Tạo PluginManager

File:

```text-x-trilium-auto
plugins/plugin_manager.py
```

---

Import:

```text-x-trilium-auto
import json from pathlib import Path import importlib
```

---

Class:

```text-x-trilium-auto
class PluginManager:


    def __init__(
        self,
        plugin_path
    ):

        self.plugin_path = Path(
            plugin_path
        )

        self.plugins = {}
```

---

Giải thích:

```text-x-trilium-auto
self.plugins
```

sẽ chứa:

```text-x-trilium-auto
{
 "truyenfull": TruyenFullSource
}
```

---

# 5. Quét thư mục plugin

Tạo:

```text-x-trilium-auto
def discover(self):

    for folder in self.plugin_path.iterdir():

        if folder.is_dir():

            self.load_plugin(folder)
```

---

Ví dụ:

Thư mục:

```text-x-trilium-auto
plugins/

truyenfull/

tangthuvien/
```

sẽ duyệt:

```text-x-trilium-auto
truyenfull

tangthuvien
```

---

# 6. Đọc manifest.json

Thêm:

```text-x-trilium-auto
def read_manifest(
    self,
    folder
):

    file = folder / "manifest.json"


    with open(
        file,
        encoding="utf8"
    ) as f:

        return json.load(f)
```

---

Ví dụ:

```text-x-trilium-auto
manifest = {
"name":"truyenfull",
"source":"TruyenFullSource"
}
```

---

# 7. Dynamic Import

Đây là phần quan trọng nhất.

Python cho phép import bằng chuỗi.

Ví dụ:

Chuỗi:

```text-x-trilium-auto
"plugins.truyenfull.source"
```

---

Load:

```text-x-trilium-auto
module = importlib.import_module(
    module_name
)
```

---

Sau đó lấy class:

```text-x-trilium-auto
source_class = getattr(
    module,
    class_name
)
```

---

# 8. Xác định module

Từ folder:

```text-x-trilium-auto
plugins/truyenfull
```

ta có:

```text-x-trilium-auto
plugin_name="truyenfull"
```

Module:

```text-x-trilium-auto
plugins.truyenfull.source
```

---

Code:

```text-x-trilium-auto
module_name = (
    f"plugins."
    f"{plugin_name}"
    f".source"
)
```

---

# 9. Load Plugin

Hoàn chỉnh:

```text-x-trilium-auto
def load_plugin(
    self,
    folder
):

    manifest = self.read_manifest(
        folder
    )


    name = manifest["name"]

    class_name = manifest["source"]


    module_name = (
        f"plugins."
        f"{name}"
        f".source"
    )


    module = importlib.import_module(
        module_name
    )


    source_class = getattr(
        module,
        class_name
    )


    self.plugins[name] = source_class
```

---

Sau khi chạy:

```text-x-trilium-auto
manager.discover()
```

Ta có:

```text-x-trilium-auto
manager.plugins
```

Kết quả:

```text-x-trilium-auto
{
 "truyenfull":
 <class TruyenFullSource>
}
```

---

# 10. Lấy plugin

Thêm:

```text-x-trilium-auto
def get(
    self,
    name
):

    return self.plugins.get(
        name
    )
```

---

Dùng:

```text-x-trilium-auto
SourceClass = manager.get(
    "truyenfull"
)
```

---

# 11. Khởi tạo plugin

Hiện tại Source cần:

```text-x-trilium-auto
HttpClient

Parser
```

nên:

```text-x-trilium-auto
source = SourceClass(
    http_client,
    parser
)
```

---

Nhưng có vấn đề.

Mỗi plugin có parser khác nhau.

Ví dụ:

```text-x-trilium-auto
TruyenFullSource

+

TruyenFullParser
```

---

Do đó manifest cần mở rộng.

---

# 12. Nâng cấp manifest.json

Sửa:

```text-x-trilium-auto
{
    "name":"truyenfull",

    "source":
    "TruyenFullSource",

    "parser":
    "TruyenFullParser"
}
```

---

Bây giờ PluginManager biết:

```text-x-trilium-auto
Source class

Parser class
```

---

# 13. Load Parser

Thêm:

```text-x-trilium-auto
def load_class(
    self,
    module_name,
    class_name
):

    module = importlib.import_module(
        module_name
    )


    return getattr(
        module,
        class_name
    )
```

---

Dùng:

```text-x-trilium-auto
parser_class = self.load_class(
    "plugins.truyenfull.parser",
    "TruyenFullParser"
)
```

---

# 14. Factory Plugin

Thực tế không nên trả class.

Nên tạo instance.

Thêm:

```text-x-trilium-auto
def create(
    self,
    name,
    http_client
):

    source_class = self.plugins[name]


    parser_class = self.parsers[name]


    parser = parser_class()


    return source_class(
        http_client,
        parser
    )
```

---

# 15. Kiến trúc sau PluginManager

Bây giờ:

```text-x-trilium-auto
Dashboard

    |

CrawlerService

    |

PluginManager

    |

    +-------------+

    |             |

TruyenFull   TangThuVien


    |

Source

    |

+---+---+

HTTP Parser

       |

       v

    Models
```

---

# 16. Thêm website mới

Ví dụ:

Muốn thêm:

```text-x-trilium-auto
tangthuvien
```

Chỉ cần:

```text-x-trilium-auto
plugins/

└── tangthuvien/

    ├── manifest.json

    ├── source.py

    ├── parser.py

    ├── selectors.json

    └── config.py
```

Không sửa:

```text-x-trilium-auto
CrawlerService

PluginManager

Dashboard
```

---

# 17. Test PluginManager

Cấu trúc:

```text-x-trilium-auto
tests/

test_plugin_manager.py
```

---

Test:

```text-x-trilium-auto
manager = PluginManager(
    "plugins"
)


manager.discover()


assert "truyenfull" in manager.plugins
```

---

# 18. Tổng kết bài 12

Bạn đã xây dựng được:

✅ Plugin architecture  
✅ Dynamic import Python  
✅ Manifest driven plugin  
✅ Tách core khỏi website cụ thể  
✅ Có khả năng mở rộng nhiều nguồn truyện

Kiến trúc hiện tại:

```text-x-trilium-auto
plugins/

├── plugin_manager.py

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

# Bài 13 tiếp theo

Chúng ta sẽ quay lại phần dữ liệu:

## Xây dựng Model + SQLite Database Layer

Bao gồm:

- `NovelModel`
- `ChapterModel`
- `NovelRepository`
- `ChapterRepository`
- Schema SQLite:
  - novels
  - chapters
  - crawl_tasks
  - crawl_logs

Sau bài 13, plugin có thể:

```text-x-trilium-auto
Website
   |
Plugin
   |
Parser
   |
Model
   |
SQLite
```

và bắt đầu trở thành một hệ thống crawl truyện hoàn chỉnh.