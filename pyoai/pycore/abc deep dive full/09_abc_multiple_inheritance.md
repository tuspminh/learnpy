# ABC Deep Dive - Buổi 9

# Multiple Inheritance + MRO + `super()` Deep Dive

Đây là **một trong những buổi quan trọng nhất** của toàn bộ khóa học.

Nếu hiểu không đúng **Multiple Inheritance** và **MRO (Method Resolution Order)** thì rất dễ gặp các lỗi như:

  * `super()` gọi sai lớp. 
  * Phương thức bị thực thi nhiều lần. 
  * Diamond Problem. 
  * Framework hoạt động không đúng. 



Đây cũng là nền tảng để hiểu cách Django, SQLAlchemy, Pydantic, Scrapy và rất nhiều framework Python được thiết kế.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Multiple Inheritance 
  * MRO là gì 
  * C3 Linearization 
  * Diamond Inheritance 
  * `super()` hoạt động như thế nào 
  * ABC + Multiple Inheritance 
  * Mixins 
  * Thiết kế framework đúng cách 



* * *

# 1\. Multiple Inheritance

Trong Python, một lớp có thể kế thừa từ nhiều lớp cha.

Ví dụ:
    
    
    class Flyable:
        pass
    
    
    class Swimmable:
        pass
    
    
    class Duck(Flyable, Swimmable):
        pass

Sơ đồ:
    
    
            Flyable
               ▲
               │
    Duck ◄─────┼────► Swimmable

Khác với Java (chỉ cho phép kế thừa một lớp), Python hỗ trợ kế thừa nhiều lớp.

* * *

# 2\. Ví dụ đầu tiên
    
    
    class A:
    
        def hello(self):
            print("A")
    
    
    class B:
    
        def world(self):
            print("B")
    
    
    class C(A, B):
        pass

Sử dụng:
    
    
    obj = C()
    
    obj.hello()
    
    obj.world()

Kết quả:
    
    
    A
    B

Không có gì đặc biệt.

* * *

# 3\. Khi trùng tên phương thức
    
    
    class A:
    
        def hello(self):
            print("A")
    
    
    class B:
    
        def hello(self):
            print("B")
    
    
    class C(A, B):
        pass

Gọi:
    
    
    C().hello()

Kết quả:
    
    
    A

Python chọn:
    
    
    A
    
    ↓
    
    B

Theo thứ tự khai báo trong danh sách kế thừa.

* * *

# 4\. MRO

Kiểm tra:
    
    
    print(C.mro())

Kết quả:
    
    
    [
        C,
        A,
        B,
        object
    ]

Đây gọi là:

> **Method Resolution Order**

Mọi việc tìm phương thức đều đi theo danh sách này.

* * *

# 5\. Ví dụ
    
    
    class A:
    
        def hello(self):
            print("A")
    
    
    class B:
    
        pass
    
    
    class C(A, B):
        pass

Python tìm:
    
    
    C
    
    ↓
    
    A
    
    ↓
    
    B
    
    ↓
    
    object

* * *

# 6\. Diamond Problem

Đây là ví dụ nổi tiếng.
    
    
    class A:
    
        def hello(self):
            print("A")
    
    
    class B(A):
        pass
    
    
    class C(A):
        pass
    
    
    class D(B, C):
        pass

Sơ đồ:
    
    
            A
          ▲   ▲
          │   │
          B   C
           ▲ ▲
            D

Nếu không có MRO sẽ xảy ra câu hỏi:

> Gọi A qua B trước hay C trước?

Python giải bằng thuật toán C3 Linearization.

* * *

# 7\. MRO của Diamond
    
    
    print(D.mro())

Kết quả:
    
    
    [
        D,
        B,
        C,
        A,
        object
    ]

A chỉ xuất hiện **một lần**.

* * *

# 8\. `super()` là gì?

Nhiều người nghĩ:
    
    
    super()

nghĩa là:

> "Gọi lớp cha."

Điều này **không chính xác**.

Thực chất:

> **`super()` gọi lớp tiếp theo trong MRO.**

* * *

# 9\. Ví dụ
    
    
    class A:
    
        def hello(self):
            print("A")
    
    
    class B(A):
    
        def hello(self):
            print("B")
    
            super().hello()
    
    
    class C(B):
    
        def hello(self):
            print("C")
    
            super().hello()

Kết quả:
    
    
    C().hello()
    
    
    C
    B
    A

Không phải vì:
    
    
    C
    
    ↓
    
    B
    
    ↓
    
    A

mà vì đó là MRO.

* * *

# 10\. Diamond + super()
    
    
    class A:
    
        def hello(self):
            print("A")
    
    
    class B(A):
    
        def hello(self):
            print("B")
    
            super().hello()
    
    
    class C(A):
    
        def hello(self):
            print("C")
    
            super().hello()
    
    
    class D(B, C):
    
        def hello(self):
            print("D")
    
            super().hello()

MRO:
    
    
    print(D.mro())
    
    
    D
    
    ↓
    
    B
    
    ↓
    
    C
    
    ↓
    
    A
    
    ↓
    
    object

* * *

Kết quả:
    
    
    D().hello()
    
    
    D
    
    B
    
    C
    
    A

Chú ý:

A chỉ chạy **một lần**.

* * *

# 11\. Nếu không dùng super()
    
    
    class B(A):
    
        def hello(self):
    
            print("B")
    
            A.hello(self)

và
    
    
    class C(A):
    
        def hello(self):
    
            print("C")
    
            A.hello(self)

Kết quả:
    
    
    A

có thể bị gọi **hai lần** khi kết hợp trong Diamond Inheritance.

Đây là lý do trong multiple inheritance, nên ưu tiên `super()` thay vì gọi trực tiếp tên lớp.

* * *

# 12\. ABC + Multiple Inheritance

Ví dụ:
    
    
    from abc import ABC
    from abc import abstractmethod
    
    
    class Reader(ABC):
    
        @abstractmethod
        def read(self):
            ...
    
    
    class Writer(ABC):
    
        @abstractmethod
        def write(self):
            ...

Lớp:
    
    
    class FileIO(
        Reader,
        Writer
    ):
    
        def read(self):
            print("Read")
    
        def write(self):
            print("Write")

Được phép.

* * *

# 13\. MRO với ABC
    
    
    print(FileIO.mro())

Ví dụ kết quả:
    
    
    FileIO
    
    ↓
    
    Reader
    
    ↓
    
    Writer
    
    ↓
    
    ABC
    
    ↓
    
    object

`ABC` chỉ xuất hiện một lần trong MRO.

* * *

# 14\. Nhiều ABC
    
    
    class Searchable(ABC):
        ...
    
    
    class Downloadable(ABC):
        ...
    
    
    class Cacheable(ABC):
        ...
    
    
    class Plugin(
        Searchable,
        Downloadable,
        Cacheable
    ):
        ...

Hoàn toàn hợp lệ.

* * *

# 15\. Mixins

Đây là kỹ thuật rất phổ biến.

Mixin là lớp:

  * nhỏ 
  * độc lập 
  * chỉ thêm một chức năng 



Ví dụ:
    
    
    class LoggingMixin:
    
        def log(self):
    
            print("LOG")

* * *
    
    
    class RetryMixin:
    
        def retry(self):
    
            print("Retry")

* * *
    
    
    class BaseCrawler(ABC):
    
        @abstractmethod
        def crawl(self):
            ...

* * *
    
    
    class MyCrawler(
        LoggingMixin,
        RetryMixin,
        BaseCrawler
    ):
    
        def crawl(self):
    
            self.log()
    
            self.retry()

* * *

# 16\. Thiết kế đúng

Mixin:
    
    
    LoggingMixin
    
    RetryMixin
    
    ProxyMixin

ABC:
    
    
    BaseCrawler

Plugin:
    
    
    TruyenFullCrawler

Sơ đồ:
    
    
    LoggingMixin
           ▲
    
    RetryMixin
           ▲
    
    BaseCrawler
           ▲
    
    TruyenFullCrawler

Mỗi lớp chỉ chịu trách nhiệm cho một mối quan tâm (logging, retry, giao diện crawler...), giúp hệ thống dễ mở rộng.

* * *

# 17\. Sai lầm phổ biến

Mixin:
    
    
    class LoggingMixin:
    
        def crawl(self):
            ...

ABC:
    
    
    class BaseCrawler:
    
        def crawl(self):
            ...

Plugin:
    
    
    class MyCrawler(
        LoggingMixin,
        BaseCrawler
    ):
        ...

Lúc này MRO sẽ quyết định phương thức `crawl()` nào được dùng. Nếu mixin và lớp cơ sở đều định nghĩa cùng một phương thức mà không phối hợp bằng `super()`, rất dễ dẫn đến hành vi khó đoán.

Vì vậy:

  * Mixins nên bổ sung hành vi nhỏ, rõ ràng. 
  * Nếu override cùng một phương thức, các lớp trong chuỗi nên hợp tác bằng `super()`. 



* * *

# 18\. Áp dụng vào dự án crawler

Một thiết kế tốt:
    
    
    BaseSource (ABC)
    │
    ├── search()
    ├── get_detail()
    ├── get_chapters()
    └── download_chapter()
    
    LoggingMixin
    │
    └── log()
    
    RetryMixin
    │
    └── retry()
    
    ProxyMixin
    │
    └── get_proxy()
    
    CookieMixin
    │
    └── load_cookie()

Plugin:
    
    
    TruyenFullSource(
        LoggingMixin,
        RetryMixin,
        ProxyMixin,
        BaseSource
    )

Như vậy:

  * `BaseSource` định nghĩa "hợp đồng" (contract). 
  * Các mixin bổ sung chức năng. 
  * Plugin tập trung vào logic nghiệp vụ. 



* * *

# 19\. MRO và thiết kế Framework

Một nguyên tắc quan trọng:

Nếu một phương thức có thể được nhiều lớp trong MRO ghi đè và muốn tất cả cùng tham gia xử lý, hãy viết theo kiểu "cooperative multiple inheritance":
    
    
    class LoggingMixin:
    
        def before(self):
            print("Logging")
            super().before()

và:
    
    
    class RetryMixin:
    
        def before(self):
            print("Retry")
            super().before()

Cuối chuỗi:
    
    
    class BaseCrawler(ABC):
    
        def before(self):
            pass

Mỗi lớp gọi `super()`, nhờ đó tất cả các lớp trong MRO đều có cơ hội thực thi.

* * *

# Tổng kết

Trong buổi này bạn đã học:

  * Multiple Inheritance 
  * MRO 
  * Diamond Problem 
  * `super()` hoạt động theo MRO 
  * ABC + Multiple Inheritance 
  * Mixins 
  * Cooperative Multiple Inheritance 
  * Thiết kế framework bằng ABC và mixin 



* * *

# Bài tập

## Bài 1

Viết:
    
    
    Reader(ABC)
    
    Writer(ABC)
    
    Exporter(Reader, Writer)

Cài đặt đầy đủ các abstract method.

* * *

## Bài 2

Tạo:
    
    
    LoggingMixin
    
    RetryMixin
    
    TimingMixin

Mỗi mixin có một phương thức riêng.

Sau đó tạo:
    
    
    Downloader(
        LoggingMixin,
        RetryMixin,
        TimingMixin
    )

và gọi tất cả các phương thức.

* * *

## Bài 3

Xây dựng ví dụ Diamond Inheritance:
    
    
            A
          /   \
         B     C
          \   /
            D

So sánh kết quả khi:

  * dùng `super()`
  * gọi trực tiếp `A.method(self)`



Giải thích vì sao khác nhau.

* * *

## Bài 4 (Áp dụng dự án crawler)

Thiết kế lớp:
    
    
    BaseSource (ABC)
    LoggingMixin
    RetryMixin
    RateLimitMixin
    ProxyMixin
    CookieMixin

Sau đó tạo:
    
    
    class TruyenFullSource(
        LoggingMixin,
        RetryMixin,
        RateLimitMixin,
        ProxyMixin,
        CookieMixin,
        BaseSource,
    ):
        ...

Thử:
    
    
    print(TruyenFullSource.mro())

và giải thích vai trò của từng lớp trong MRO.

* * *

# Buổi 10

Ở **Buổi 10** , chúng ta sẽ đi sâu vào **ABCMeta Deep Dive** :

  * Cách `ABCMeta` kế thừa từ `type`
  * Cách Python tạo abstract class 
  * Cơ chế của `__new__()`
  * Cách `ABCMeta` xây dựng `__abstractmethods__`
  * `update_abstractmethods()`
  * Tự xây dựng một metaclass giống `ABCMeta`



Đây là phần gần nhất với mã nguồn của CPython và sẽ giúp bạn hiểu cách hoạt động bên trong của `abc`.

