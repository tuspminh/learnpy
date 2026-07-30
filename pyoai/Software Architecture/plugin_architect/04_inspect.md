# Plugin Architecture Deep Dive

# Buổi 4: Reflection & Introspection với `inspect` – Tự động tìm Plugin

> **Mục tiêu**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu Reflection (Phản chiếu) và Introspection là gì. 
>   * Thành thạo module `inspect`. 
>   * Tự động tìm class Plugin trong module. 
>   * Kiểm tra class có kế thừa `BasePlugin` hay không. 
>   * Đọc metadata, method, signature của plugin. 
>   * Xây dựng Plugin Loader v2 không cần biết tên class. 
> 


* * *

# Roadmap
    
    
    Phần I - Tư duy Plugin
    
    ✓ Buổi 1 : Plugin là gì?
    ✓ Buổi 2 : Plugin Contract
    ✓ Buổi 3 : importlib
    ➜ Buổi 4 : inspect
    □ Buổi 5 : Plugin Discovery

Đến hôm nay chúng ta đã import được module.

Nhưng còn một vấn đề:
    
    
    module = importlib.import_module(
        "plugins.truyenfull"
    )

Framework chỉ có object module.

Nó **không biết**

  * class nào là plugin 
  * class nào chỉ là helper 
  * class nào là parser 
  * class nào là model 



Làm sao?

Đó là lúc Reflection xuất hiện.

* * *

# 1\. Reflection là gì?

Reflection là khả năng chương trình:

> Tự quan sát chính nó khi đang chạy.

Ví dụ
    
    
    class Dog:
    
        def bark(self):
            print("Woof")

Thay vì đọc code bằng mắt.

Python có thể tự hỏi:
    
    
    Class này tên gì?
    
    Có bao nhiêu method?
    
    Có kế thừa ai không?
    
    Có attribute nào?

* * *

# 2\. Introspection

Trong Python người ta thường dùng từ

> Introspection

nhiều hơn Reflection.

Ví dụ
    
    
    class Dog:
    
        age = 2
    
        def bark(self):
            pass

Ta có thể hỏi
    
    
    print(type(Dog))
    
    
    print(dir(Dog))
    
    
    print(hasattr(Dog, "age"))
    
    
    print(getattr(Dog, "age"))

Python trả lời ngay.

* * *

# 3\. Module inspect

Thư viện chuẩn
    
    
    import inspect

Đây là "dao đa năng" của Reflection.

* * *

# 4\. inspect.getmembers()

Ví dụ
    
    
    import inspect
    
    
    class Dog:
    
        age = 2
    
        def bark(self):
            pass
    
    
    members = inspect.getmembers(Dog)
    
    for name, value in members:
        print(name)

Kết quả
    
    
    __class__
    
    __dict__
    
    __doc__
    
    age
    
    bark

Framework nhờ đó biết class có gì.

* * *

# 5\. Chỉ lấy Method
    
    
    import inspect
    
    methods = inspect.getmembers(
        Dog,
        inspect.isfunction
    )
    
    print(methods)

Kết quả
    
    
    [
     ('bark',
       <function ...>)
    ]

* * *

# 6\. Chỉ lấy Class

Giả sử module
    
    
    class Helper:
        pass
    
    
    class Parser:
        pass
    
    
    class TruyenFull:
        pass

Ta dùng
    
    
    classes = inspect.getmembers(
        module,
        inspect.isclass
    )

Kết quả
    
    
    Helper
    
    Parser
    
    TruyenFull

Đây là nền tảng của Plugin Loader.

* * *

# 7\. issubclass()

Giả sử
    
    
    from abc import ABC
    
    
    class BasePlugin(ABC):
        pass
    
    
    class Helper:
        pass
    
    
    class TruyenFull(BasePlugin):
        pass

Ta kiểm tra
    
    
    issubclass(
        TruyenFull,
        BasePlugin
    )

↓
    
    
    True

Còn
    
    
    issubclass(
        Helper,
        BasePlugin
    )

↓
    
    
    False

Đây là cách framework nhận biết plugin.

* * *

# 8\. Tự tìm Plugin

Ví dụ
    
    
    import inspect
    
    
    def find_plugin(module):
    
        for _, obj in inspect.getmembers(
            module,
            inspect.isclass
        ):
    
            if issubclass(obj, BasePlugin):
    
                return obj

Không cần biết
    
    
    TruyenFull

hay
    
    
    NovelBin

Framework tự tìm.

* * *

# 9\. Nhưng có bug!

Giả sử
    
    
    class BasePlugin:
        pass
    
    
    class TruyenFull(BasePlugin):
        pass

`inspect.getmembers()`

trả về
    
    
    BasePlugin
    
    TruyenFull

Nếu viết
    
    
    issubclass(obj, BasePlugin)

thì
    
    
    BasePlugin

cũng trả về
    
    
    True

Cần loại bỏ.

* * *

Cách đúng
    
    
    if (
        issubclass(obj, BasePlugin)
        and obj is not BasePlugin
    ):
        ...

Đây là lỗi rất nhiều người gặp khi viết Plugin Loader.

* * *

# 10\. Signature

Framework muốn biết
    
    
    search()

cần bao nhiêu tham số.
    
    
    class Plugin:
    
        def search(
            self,
            keyword,
            page=1
        ):
            pass

Ta dùng
    
    
    inspect.signature(
        Plugin.search
    )

Kết quả
    
    
    (keyword, page=1)

* * *

# 11\. Parameters
    
    
    sig = inspect.signature(
        Plugin.search
    )
    
    print(sig.parameters)

↓
    
    
    keyword
    
    page

Có thể kiểm tra

  * kiểu dữ liệu 
  * default 
  * annotation 



* * *

# 12\. Type Hint
    
    
    class Plugin:
    
        def search(
            self,
            keyword: str
        ) -> list:
            pass
    
    
    sig = inspect.signature(
        Plugin.search
    )
    
    print(sig.return_annotation)

↓
    
    
    list

* * *

# 13\. Docstring
    
    
    class Plugin:
    
        """
        Plugin TruyenFull
        """
    
        pass
    
    
    inspect.getdoc(
        Plugin
    )

↓
    
    
    Plugin TruyenFull

Framework có thể hiển thị
    
    
    Plugin Information

* * *

# 14\. Module Information
    
    
    inspect.getmodule(
        Plugin
    )

↓
    
    
    plugins.truyenfull

* * *

# 15\. Source Code
    
    
    inspect.getsource(
        Plugin
    )

↓
    
    
    class Plugin:
        ...

Cực kỳ hữu ích khi:

  * Debug 
  * IDE 
  * Documentation Generator 



Lưu ý: Chỉ hoạt động khi mã nguồn còn tồn tại dưới dạng file `.py`. Nếu plugin được đóng gói hoặc biên dịch theo cách khác thì có thể không lấy được source.

* * *

# 16\. Plugin Loader v2
    
    
    import importlib
    import inspect
    
    
    class PluginLoader:
    
        def load(self, module_name):
    
            module = importlib.import_module(module_name)
    
            for _, cls in inspect.getmembers(
                module,
                inspect.isclass
            ):
    
                if (
                    issubclass(cls, BasePlugin)
                    and cls is not BasePlugin
                ):
    
                    return cls()

Đây là Loader thực sự đầu tiên.

Framework không cần biết
    
    
    TruyenFull

hay
    
    
    NovelBin

* * *

# 17\. Nếu có nhiều Plugin?

Giả sử
    
    
    class A(BasePlugin):
        pass
    
    
    class B(BasePlugin):
        pass

Loader hiện tại
    
    
    return cls()

chỉ lấy plugin đầu tiên.

Đúng hơn
    
    
    plugins = []
    
    for _, cls in inspect.getmembers(
        module,
        inspect.isclass
    ):
    
        if (
            issubclass(cls, BasePlugin)
            and cls is not BasePlugin
        ):
    
            plugins.append(cls())
    
    return plugins

* * *

# 18\. Metadata bằng Attribute
    
    
    class TruyenFull(BasePlugin):
    
        name = "TruyenFull"
    
        version = "1.0"
    
        author = "Garden"

Framework
    
    
    plugin.name
    
    plugin.version
    
    plugin.author

Hoặc
    
    
    getattr(
        plugin,
        "version"
    )

Nếu thuộc tính có thể không tồn tại, nên dùng giá trị mặc định:
    
    
    version = getattr(plugin, "version", "unknown")

* * *

# 19\. Kiến trúc hiện tại
    
    
              Plugin Loader
    
                    │
    
          importlib.import_module()
    
                    │
    
                 Module
    
                    │
    
     inspect.getmembers(module)
    
                    │
    
              Class Objects
    
                    │
    
     issubclass(BasePlugin)
    
                    │
    
              Instantiate()
    
                    │
    
             Plugin Instance

* * *

# 20\. Một ví dụ hoàn chỉnh
    
    
    from abc import ABC
    from abc import abstractmethod
    
    import inspect
    import importlib
    
    
    class BasePlugin(ABC):
    
        @abstractmethod
        def hello(self):
            pass
    
    
    class PluginLoader:
    
        def load(self, module_name):
    
            module = importlib.import_module(module_name)
    
            plugins = []
    
            for _, cls in inspect.getmembers(
                module,
                inspect.isclass
            ):
    
                if (
                    issubclass(cls, BasePlugin)
                    and cls is not BasePlugin
                ):
    
                    plugins.append(cls())
    
            return plugins

Đây là phiên bản rất gần với nhiều framework thực tế.

* * *

# Hạn chế của phiên bản hiện tại

Framework vẫn phải biết
    
    
    loader.load(
        "plugins.truyenfull"
    )

Nghĩa là vẫn cần biết:
    
    
    plugins.truyenfull
    plugins.wattpad
    plugins.novelbin

Nếu có 500 plugin thì sao?

Không thể viết
    
    
    loader.load(...)
    loader.load(...)
    loader.load(...)
    ...

Đó là nhiệm vụ của **Plugin Discovery**.

* * *

# Best Practices

## 1\. Luôn dùng `inspect.isclass`

Không dùng
    
    
    type(obj) == type

vì `inspect` xử lý đúng nhiều trường hợp hơn.

* * *

## 2\. Luôn loại bỏ `BasePlugin`
    
    
    obj is not BasePlugin

Nếu quên, Loader có thể cố khởi tạo lớp trừu tượng và gây lỗi.

* * *

## 3\. Không dựa vào tên class

Sai
    
    
    if cls.__name__ == "Plugin":

Đúng
    
    
    issubclass(
        cls,
        BasePlugin
    )

* * *

## 4\. Reflection chỉ để khám phá

Không nên dùng `inspect` để điều khiển toàn bộ logic của ứng dụng. Hãy dùng nó để:

  * tìm plugin, 
  * đọc metadata, 
  * kiểm tra hợp đồng, 



sau đó làm việc thông qua interface (`BasePlugin`).

* * *

# Bài tập

### Bài 1

Viết hàm:
    
    
    find_plugins(module) -> list[type]

Trả về tất cả các class kế thừa `BasePlugin`.

* * *

### Bài 2

Mở rộng `PluginLoader` để:

  * import module, 
  * tìm tất cả plugin, 
  * khởi tạo tất cả plugin, 
  * trả về `list[BasePlugin]`. 



* * *

### Bài 3

Thêm metadata cho plugin:
    
    
    name
    version
    author
    description

Sau đó dùng `inspect.getmembers()` hoặc `getattr()` để in ra bảng thông tin của mỗi plugin.

* * *

# Chuẩn bị cho Buổi 5

Đến đây Loader đã có thể:

  * Import module. 
  * Tự tìm class plugin. 
  * Khởi tạo plugin. 



Nhưng vẫn còn một câu hỏi quan trọng:

> **Framework làm thế nào để biết trong thư mục`plugins/` hiện có những plugin nào?**

Ở **Buổi 5: Plugin Discovery** , chúng ta sẽ học cách:

  * Duyệt thư mục bằng `pathlib`. 
  * Khám phá package bằng `pkgutil`. 
  * Tự động phát hiện plugin mới mà **không cần ghi tên module ở bất kỳ đâu**. 



Đó là mảnh ghép cuối cùng để hoàn thiện **Plugin Loader** đầu tiên của framework.

