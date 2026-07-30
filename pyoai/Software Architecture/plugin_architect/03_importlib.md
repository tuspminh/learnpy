# Plugin Architecture Deep Dive

# Buổi 3: Dynamic Import với `importlib` – Nền tảng của Plugin Loader

> **Mục tiêu**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu cơ chế `import` của Python. 
>   * Biết `sys.modules` là gì. 
>   * Sử dụng thành thạo `importlib`. 
>   * Import module bằng chuỗi. 
>   * Import class động. 
>   * Khởi tạo plugin mà không biết trước tên class. 
>   * Viết Plugin Loader phiên bản đầu tiên. 
> 


* * *

# Roadmap khóa học
    
    
    Phần I — Tư duy Plugin
    ✓ Buổi 1: Plugin là gì?
    ✓ Buổi 2: Interface & Plugin Contract
    ➜ Buổi 3: Dynamic Import (hôm nay)
    □ Buổi 4: Reflection với inspect
    □ Buổi 5: Plugin Discovery

Từ hôm nay chúng ta bắt đầu viết những thành phần thật sự của framework.

* * *

# 1\. Vì sao cần Dynamic Import?

Giả sử framework có cấu trúc:
    
    
    plugins/
    
        truyenfull.py
        wattpad.py
        novelbin.py

Nếu viết:
    
    
    from plugins.truyenfull import TruyenFull
    from plugins.wattpad import Wattpad
    from plugins.novelbin import NovelBin

thì mỗi khi thêm plugin mới:
    
    
    plugins/
    
        metruyen.py

bạn lại phải sửa framework.

Điều này vi phạm:

> Open/Closed Principle

Framework phải có khả năng:

> "Không biết plugin nào tồn tại."

* * *

# 2\. Import hoạt động như thế nào?

Khi viết
    
    
    import math

Python thực hiện:
    
    
    import
    
    ↓
    
    Tìm module
    
    ↓
    
    Đọc file
    
    ↓
    
    Compile
    
    ↓
    
    Thực thi
    
    ↓
    
    Sinh object module
    
    ↓
    
    Lưu cache
    
    ↓
    
    Trả về module

Điều quan trọng là:

> Module chỉ được load một lần.

* * *

# 3\. sys.modules

Ví dụ
    
    
    import math
    import sys
    
    print("math" in sys.modules)

Kết quả
    
    
    True

Sau khi import
    
    
    import math

Python lưu
    
    
    sys.modules["math"]

Lần sau
    
    
    import math

Python không đọc file nữa.

Chỉ lấy từ cache.

* * *

Ví dụ
    
    
    import math
    
    a = math
    
    import math
    
    b = math
    
    print(a is b)

Kết quả
    
    
    True

Đây là lý do import trong Python rất nhanh sau lần đầu tiên.

* * *

# 4\. importlib

Đây là thư viện chuẩn để import động.
    
    
    import importlib

Thay vì
    
    
    import math

ta có thể
    
    
    module = importlib.import_module("math")

Sau đó
    
    
    print(module.sqrt(16))

Kết quả
    
    
    4.0

* * *

# 5\. Import bằng chuỗi

Ví dụ
    
    
    module_name = "json"
    
    module = importlib.import_module(module_name)
    
    print(module.dumps({"name": "Alice"}))

Kết quả
    
    
    {"name": "Alice"}

Điều này rất quan trọng.

Framework chỉ cần biết
    
    
    plugins.truyenfull

là chuỗi.

Không cần
    
    
    import plugins.truyenfull

* * *

# 6\. Import package con

Cấu trúc
    
    
    plugins/
    
        truyenfull/
    
            __init__.py
    
            source.py

Có thể
    
    
    module = importlib.import_module(
        "plugins.truyenfull.source"
    )

Không khác gì import thông thường.

* * *

# 7\. Lấy class từ module

Giả sử
    
    
    # plugins/truyenfull/source.py
    
    class TruyenFull:
    
        pass

Import
    
    
    module = importlib.import_module(
        "plugins.truyenfull.source"
    )

Lấy class
    
    
    cls = getattr(module, "TruyenFull")
    
    print(cls)

Kết quả
    
    
    <class TruyenFull>

* * *

# 8\. Khởi tạo class động

Sau khi lấy class
    
    
    instance = cls()
    
    print(instance)

Framework không cần biết:
    
    
    TruyenFull

là class gì.

* * *

# 9\. Ví dụ hoàn chỉnh

Giả sử
    
    
    plugins/
    
        truyenfull.py
    
    
    class TruyenFull:
    
        def hello(self):
            print("Hello")

Framework
    
    
    import importlib
    
    module = importlib.import_module(
        "plugins.truyenfull"
    )
    
    plugin_class = getattr(
        module,
        "TruyenFull"
    )
    
    plugin = plugin_class()
    
    plugin.hello()

Kết quả
    
    
    Hello

* * *

# 10\. Nếu không biết tên class?

Đây là vấn đề lớn.

Framework chỉ biết:
    
    
    plugins.truyenfull

Nhưng không biết
    
    
    TruyenFull

hay
    
    
    MainPlugin

hay
    
    
    Crawler

Làm sao?

Đây sẽ là nhiệm vụ của:
    
    
    inspect

ở buổi sau.

* * *

# 11\. Import lỗi

Nếu module không tồn tại
    
    
    importlib.import_module(
        "plugins.abc"
    )

Lỗi
    
    
    ModuleNotFoundError

Nên luôn
    
    
    try:
        module = importlib.import_module(name)
    
    except ModuleNotFoundError:
        ...

* * *

# 12\. Reload module

Python hỗ trợ
    
    
    importlib.reload(module)

Ví dụ
    
    
    import math
    
    import importlib
    
    math = importlib.reload(math)

Đây là nền tảng của

> Hot Reload

mà chúng ta sẽ học sau.

* * *

# 13\. Plugin Loader phiên bản đầu tiên

Cấu trúc
    
    
    framework/
    
        loader.py
    
    
    import importlib
    
    
    class PluginLoader:
    
        def load(self, module_name):
    
            module = importlib.import_module(module_name)
    
            return module

Sử dụng
    
    
    loader = PluginLoader()
    
    module = loader.load(
        "plugins.truyenfull"
    )

Đã load được plugin.

* * *

# 14\. Loader nâng cấp
    
    
    import importlib
    
    
    class PluginLoader:
    
        def load_class(
            self,
            module_name,
            class_name
        ):
    
            module = importlib.import_module(module_name)
    
            cls = getattr(module, class_name)
    
            return cls()

Sử dụng
    
    
    loader = PluginLoader()
    
    plugin = loader.load_class(
        "plugins.truyenfull",
        "TruyenFull"
    )

* * *

# 15\. Thiết kế plugin theo metadata

Một cách tốt hơn là quy ước:
    
    
    PLUGIN_CLASS = "TruyenFull"

Plugin
    
    
    class TruyenFull:
    
        pass
    
    PLUGIN_CLASS = TruyenFull

Framework
    
    
    module = importlib.import_module(name)
    
    plugin_cls = module.PLUGIN_CLASS
    
    plugin = plugin_cls()

Không cần gọi
    
    
    getattr(...)

Cách này được nhiều framework sử dụng vì rõ ràng và dễ kiểm soát.

* * *

# 16\. Thiết kế Story Framework (giai đoạn hiện tại)
    
    
    StoryFramework/
    
    framework/
    
        loader.py
    
    plugins/
    
        truyenfull/
    
            __init__.py
            source.py
    
        wattpad/
    
            __init__.py
            source.py

`loader.py`
    
    
    class PluginLoader:
    
        def load(module_name):
    
            ...
    
        def instantiate():
    
            ...

Hiện tại Loader mới chỉ:
    
    
    Import module
    
    ↓
    
    Lấy class
    
    ↓
    
    Tạo object

Ở các buổi tới sẽ bổ sung:
    
    
    Validate
    
    ↓
    
    Lifecycle
    
    ↓
    
    Registry
    
    ↓
    
    Dependency
    
    ↓
    
    Hot Reload

* * *

# 17\. Hạn chế của cách hiện tại

Giả sử
    
    
    plugins/
    
        truyenfull.py
    
        wattpad.py
    
        novelbin.py

Framework vẫn phải biết:
    
    
    loader.load(
        "plugins.truyenfull"
    )
    
    loader.load(
        "plugins.wattpad"
    )
    
    loader.load(
        "plugins.novelbin"
    )

Điều này vẫn chưa phải Plugin Framework hoàn chỉnh.

Câu hỏi:

> Framework làm sao biết trong thư mục `plugins/` có bao nhiêu plugin?

Muốn vậy phải:

  * Duyệt thư mục 
  * Tìm package 
  * Tự động import tất cả 



Đó chính là nhiệm vụ của **Plugin Discovery**.

* * *

# 18\. Kiến thức nội bộ cần nhớ
    
    
    import
    │
    ├── sys.modules
    ├── importlib.import_module()
    ├── importlib.reload()
    ├── getattr()
    └── Module Object

`importlib` chỉ giải quyết:

> "Làm sao import khi tên module chỉ là một chuỗi?"

Nó **không** giúp:

  * tìm module trong thư mục, 
  * xác định class plugin, 
  * kiểm tra plugin hợp lệ. 



Những việc đó sẽ được giải quyết ở các buổi tiếp theo.

* * *

# Best Practices

## 1\. Không hard-code import

❌
    
    
    from plugins.truyenfull import TruyenFull

✔
    
    
    importlib.import_module(module_name)

* * *

## 2\. Bắt lỗi import
    
    
    try:
        module = importlib.import_module(name)
    except ModuleNotFoundError:
        ...

* * *

## 3\. Tách trách nhiệm

`PluginLoader` chỉ nên:

  * import module, 
  * tạo instance. 



Không nên:

  * quản lý plugin, 
  * lưu registry, 
  * xử lý sự kiện. 



Mỗi thành phần có một nhiệm vụ riêng.

* * *

# Bài tập

## Bài 1

Viết `PluginLoader` có phương thức:
    
    
    load(module_name: str)

Trả về object module.

* * *

## Bài 2

Viết thêm:
    
    
    load_class(module_name, class_name)

Trả về instance của class.

* * *

## Bài 3

Thiết kế plugin:
    
    
    plugins/
    
        demo.py

Trong đó định nghĩa:
    
    
    PLUGIN_CLASS = DemoPlugin

và sửa `PluginLoader` để sử dụng `PLUGIN_CLASS` thay vì `getattr()`.

* * *

## Chuẩn bị cho Buổi 4

Đến đây chúng ta vẫn còn một điểm yếu:

Framework phải biết:
    
    
    PLUGIN_CLASS = DemoPlugin

hoặc biết chính xác tên class.

Nếu một module có nhiều class:
    
    
    class A:
        ...
    
    class B:
        ...
    
    class DemoPlugin:
        ...

Làm sao framework tự nhận ra **đâu mới là plugin thật sự**?

Đó là lúc chúng ta sử dụng **Reflection với`inspect`** để phân tích module, tìm class kế thừa `BasePlugin`, đọc chữ ký hàm (signature), docstring và metadata. Đây sẽ là chủ đề của **Buổi 4: Reflection & Introspection**.

