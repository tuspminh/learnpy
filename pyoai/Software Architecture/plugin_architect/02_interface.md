# Plugin Architecture Deep Dive

# Buổi 2: Interface, ABC, Protocol và Plugin Contract

> **Mục tiêu**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu tại sao Plugin phải có "Contract" (hợp đồng). 
>   * Phân biệt Interface, ABC, Protocol và Duck Typing. 
>   * Biết khi nào dùng `abc.ABC`, khi nào dùng `typing.Protocol`. 
>   * Thiết kế Interface chuyên nghiệp cho Plugin. 
>   * Xây dựng Plugin Contract đầu tiên cho Story Framework. 
> 


* * *

# 1\. Ôn lại buổi trước

Ở buổi 1, chúng ta có kiến trúc:
    
    
    Host Application
            │
            ▼
     Plugin Manager
            │
            ▼
        ??? Plugin ???

Plugin Manager không biết:

  * Plugin tên gì 
  * Plugin viết bởi ai 
  * Plugin nằm ở đâu 
  * Plugin dùng thư viện gì 



Nhưng Plugin Manager vẫn phải gọi được:
    
    
    plugin.download(...)

Hoặc
    
    
    plugin.search(...)

Làm sao?

Câu trả lời là:

> Tất cả Plugin phải tuân theo cùng một **Contract**.

* * *

# 2\. Contract là gì?

Contract (hợp đồng) là tập hợp các quy tắc mà mọi plugin bắt buộc phải tuân theo.

Ví dụ:
    
    
    Plugin phải có:
    
    ✓ name
    ✓ version
    ✓ author
    
    ✓ initialize()
    
    ✓ search()
    
    ✓ download()
    
    ✓ shutdown()

Framework chỉ cần tin rằng:

> "Plugin nào cũng có những thứ này."

* * *

Ví dụ đời thực.

Ổ điện.
    
    
    Ổ điện
    
    ↓
    
    220V

Máy giặt

↓

Cắm được.

Quạt

↓

Cắm được.

Laptop

↓

Cắm được.

Không phải vì chúng giống nhau.

Mà vì đều tuân theo cùng một chuẩn.

Plugin cũng vậy.

* * *

# 3\. Nếu không có Contract?

Ví dụ:

Plugin A
    
    
    class PluginA:
    
        def crawl(self):
            ...

Plugin B
    
    
    class PluginB:
    
        def download_story(self):
            ...

Plugin C
    
    
    class PluginC:
    
        def fetch(self):
            ...

Framework sẽ làm gì?
    
    
    plugin.???

Không biết gọi hàm nào.

Đây chính là lý do Contract tồn tại.

* * *

# 4\. Interface

Trong nhiều ngôn ngữ.

Java
    
    
    interface Downloader {
    
        download();
    
    }

C#
    
    
    interface IDownloader

Python không có keyword `interface`.

Nhưng vẫn có nhiều cách.

* * *

# 5\. Cách 1 — Duck Typing

Python rất nổi tiếng với câu:

> If it walks like a duck and quacks like a duck, then it is a duck.

Ví dụ
    
    
    class Dog:
    
        def speak(self):
            print("Woof")
    
    
    class Cat:
    
        def speak(self):
            print("Meow")

Framework
    
    
    def make_sound(animal):
        animal.speak()

Không cần:
    
    
    isinstance(...)

Chỉ cần có:
    
    
    speak()

là chạy.

* * *

Ưu điểm

  * Linh hoạt 
  * Pythonic 



Nhược điểm

Plugin viết sai tên hàm.
    
    
    speek()

Chỉ khi chạy mới lỗi.

* * *

# 6\. Cách 2 — ABC (Abstract Base Class)

Đây là cách phổ biến nhất.
    
    
    from abc import ABC
    from abc import abstractmethod
    
    
    class SourcePlugin(ABC):
    
        @abstractmethod
        def search(self, keyword):
            pass
    
        @abstractmethod
        def chapters(self, story):
            pass

Plugin
    
    
    class TruyenFull(SourcePlugin):
    
        def search(self, keyword):
            ...
    
        def chapters(self, story):
            ...

Nếu thiếu
    
    
    chapters()

Python báo lỗi ngay khi khởi tạo.
    
    
    TypeError
    
    Can't instantiate abstract class

* * *

# 7\. Ví dụ hoàn chỉnh
    
    
    from abc import ABC, abstractmethod
    
    
    class Animal(ABC):
    
        @abstractmethod
        def sound(self):
            pass
    
    
    class Dog(Animal):
    
        def sound(self):
            print("Woof")
    
    
    class Cat(Animal):
    
        def sound(self):
            print("Meow")
    
    
    animals = [Dog(), Cat()]
    
    for animal in animals:
        animal.sound()

Kết quả
    
    
    Woof
    
    Meow

Framework không cần biết:

Dog

hay

Cat.

* * *

# 8\. ABC kiểm tra điều gì?

ABC chỉ kiểm tra:

Có implement method hay không.

Ví dụ
    
    
    class Wrong(SourcePlugin):
    
        pass

↓

Lỗi.

* * *

Nhưng
    
    
    class Wrong(SourcePlugin):
    
        def search(self, keyword):
            return 123
    
        def chapters(self, story):
            return None

ABC vẫn cho phép.

Nó không kiểm tra logic.

* * *

# 9\. Protocol (Python hiện đại)

Python 3.8+
    
    
    from typing import Protocol

Ví dụ
    
    
    from typing import Protocol
    
    
    class Downloader(Protocol):
    
        def download(self, url):
            ...

Plugin
    
    
    class HttpDownloader:
    
        def download(self, url):
            print(url)

Không cần kế thừa.

Nhưng
    
    
    def run(d: Downloader):
        d.download("abc")

Vẫn hợp lệ.

Đây gọi là

> Structural Typing.

* * *

# 10\. ABC vs Protocol

ABC| Protocol  
---|---  
Bắt buộc kế thừa| Không cần kế thừa  
Kiểm tra khi runtime| Chủ yếu phục vụ type checker  
Có thể chứa logic mặc định| Thường chỉ mô tả giao diện  
Phù hợp Framework| Phù hợp thư viện và API công khai  
  
* * *

Trong Plugin Framework.

ABC thường được dùng nhiều hơn.

Protocol thường dùng kết hợp với `mypy`, `pyright`.

* * *

# 11\. Plugin Contract chuyên nghiệp

Một plugin crawler nên có gì?

Ví dụ
    
    
    name
    
    version
    
    author
    
    language
    
    initialize()
    
    search()
    
    story()
    
    chapters()
    
    chapter()
    
    shutdown()

Không nên chỉ có
    
    
    download()

Vì framework sẽ khó mở rộng.

* * *

# 12\. Thiết kế Interface đầu tiên
    
    
    from abc import ABC
    from abc import abstractmethod
    
    
    class SourcePlugin(ABC):
    
        @property
        @abstractmethod
        def name(self):
            pass
    
        @property
        @abstractmethod
        def version(self):
            pass
    
        @abstractmethod
        def initialize(self):
            pass
    
        @abstractmethod
        def search(self, keyword):
            pass
    
        @abstractmethod
        def shutdown(self):
            pass

Đây chính là Contract.

* * *

# 13\. Plugin đầu tiên
    
    
    class TruyenFull(SourcePlugin):
    
        @property
        def name(self):
            return "TruyenFull"
    
        @property
        def version(self):
            return "1.0"
    
        def initialize(self):
            print("Initialize")
    
        def search(self, keyword):
            print("Search:", keyword)
    
        def shutdown(self):
            print("Bye")

Framework
    
    
    plugin = TruyenFull()
    
    plugin.initialize()
    
    plugin.search("Naruto")
    
    plugin.shutdown()

Kết quả
    
    
    Initialize
    
    Search: Naruto
    
    Bye

Framework hoàn toàn không biết:

  * TruyenFull 
  * Wattpad 
  * NovelBin 



Nó chỉ biết:
    
    
    SourcePlugin

* * *

# 14\. Interface nhiều tầng

Một hệ thống lớn thường không chỉ có một Interface.
    
    
    Plugin
    │
    ├── SourcePlugin
    │
    ├── DownloaderPlugin
    │
    ├── ParserPlugin
    │
    ├── ThemePlugin
    │
    ├── SearchPlugin
    │
    └── AuthPlugin

Ví dụ:
    
    
    class DownloaderPlugin(ABC):
    
        @abstractmethod
        def download(self, url):
            ...
    
    
    class ThemePlugin(ABC):
    
        @abstractmethod
        def apply(self):
            ...

Mỗi loại plugin có một Contract riêng.

* * *

# 15\. Thiết kế Contract cho Story Framework

Đây là phiên bản chúng ta sẽ dùng và mở rộng trong các buổi tiếp theo:
    
    
    StoryFramework/
    │
    ├── interfaces/
    │   ├── base.py
    │   ├── source.py
    │   ├── parser.py
    │   ├── downloader.py
    │   ├── auth.py
    │   └── search.py
    │
    ├── framework/
    │   ├── loader.py
    │   ├── registry.py
    │   └── manager.py
    │
    └── plugins/
        ├── truyenfull/
        ├── wattpad/
        └── novelbin/

Mỗi plugin sẽ triển khai một hoặc nhiều Interface tương ứng.

* * *

# Best Practices

## 1\. Interface nên nhỏ

Thay vì:
    
    
    class Plugin(ABC):
    
        def login(self):
            ...
    
        def search(self):
            ...
    
        def parse(self):
            ...
    
        def theme(self):
            ...
    
        def download(self):
            ...

Hãy tách thành nhiều Interface chuyên biệt.

* * *

## 2\. Interface chỉ mô tả "làm gì"

Không mô tả "làm như thế nào".

Sai:
    
    
    def search_using_requests():

Đúng:
    
    
    def search():

* * *

## 3\. Không nhồi logic vào Interface

Interface chỉ nên có:

  * Contract 
  * Giá trị mặc định rất đơn giản (nếu cần) 



Logic nghiệp vụ nên nằm trong Plugin cụ thể.

* * *

# Bài tập

## Bài 1

Thiết kế `BasePlugin` với các thuộc tính:

  * `name`
  * `version`
  * `author`
  * `description`



và các phương thức:

  * `initialize()`
  * `enable()`
  * `disable()`
  * `shutdown()`



Sử dụng `abc.ABC`.

* * *

## Bài 2

Thiết kế thêm ba Interface:

  * `SourcePlugin`
  * `ThemePlugin`
  * `DownloaderPlugin`



Mỗi Interface chỉ chứa các phương thức cần thiết cho vai trò của nó.

* * *

## Bài 3 (chuẩn bị cho Buổi 3)

Hiện tại, Framework vẫn phải viết:
    
    
    plugin = TruyenFull()

Nhưng nếu có **100 plugin** , Framework không thể import thủ công từng plugin.

Câu hỏi đặt ra là:

> Làm thế nào để Python **tự động tìm** , **import** và **khởi tạo** tất cả plugin trong thư mục `plugins/` mà không cần biết tên của chúng?

Đó sẽ là nội dung của **Buổi 3: Dynamic Import với`importlib`**, nơi chúng ta bắt đầu xây dựng **Plugin Loader** thực thụ.

