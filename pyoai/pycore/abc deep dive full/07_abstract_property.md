# ABC Deep Dive - Buổi 7

# Abstract Property Deep Dive

Ở các buổi trước, chúng ta chủ yếu làm việc với **abstract method**.

Hôm nay, chúng ta sẽ học một chủ đề rất quan trọng khi thiết kế API và framework:

> **Abstract Property**

Đây là kỹ thuật được sử dụng trong:

  * `pathlib`
  * `logging`
  * `asyncio`
  * `importlib`
  * ORM 
  * Plugin Framework 
  * Driver Database 
  * Storage Engine 



Đặc biệt, trong **dự án crawler truyện** của bạn, Abstract Property sẽ giúp định nghĩa các thuộc tính bắt buộc như:

  * `site_name`
  * `base_url`
  * `encoding`
  * `headers`
  * `rate_limit`



* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Property là gì? 
  * Vì sao dùng property thay vì method? 
  * Abstract Property 
  * Read-only Property 
  * Read-Write Property 
  * Property Setter 
  * Property Deleter 
  * Property Validation 
  * Property trong Framework 



* * *

# 1\. Ôn lại Property

Ví dụ:
    
    
    class Dog:
    
        def __init__(self):
            self._name = "Lucky"
    
        @property
        def name(self):
            return self._name

Sử dụng:
    
    
    dog = Dog()
    
    print(dog.name)

Không cần:
    
    
    dog.get_name()

Đây là điểm khác biệt lớn so với Java/C#.

* * *

# 2\. Property hoạt động như thế nào?

Thực tế:
    
    
    dog.name

Python chuyển thành:
    
    
    dog.__class__.name.__get__(dog)

`property` là một **descriptor**.

Sơ đồ:
    
    
    dog.name
    
    ↓
    
    property.__get__()
    
    ↓
    
    getter()
    
    ↓
    
    return value

Chúng ta sẽ học Descriptor Deep Dive trong một khóa riêng, nhưng cần nhớ rằng property không phải là "biến đặc biệt", mà là một đối tượng quản lý truy cập thuộc tính.

* * *

# 3\. Read-only Property

Ví dụ:
    
    
    class User:
    
        def __init__(self):
            self._id = 100
    
        @property
        def id(self):
            return self._id

Sử dụng:
    
    
    user = User()
    
    print(user.id)

Nếu:
    
    
    user.id = 200

Lỗi:
    
    
    AttributeError:
    can't set attribute

Đây gọi là:

> **Read-only Property**

* * *

# 4\. Property Setter

Muốn cho phép sửa:
    
    
    class User:
    
        def __init__(self):
            self._id = 100
    
        @property
        def id(self):
            return self._id
    
        @id.setter
        def id(self, value):
            self._id = value

Bây giờ:
    
    
    user.id = 200
    
    print(user.id)

Kết quả:
    
    
    200

* * *

# 5\. Validation

Setter thường dùng để kiểm tra dữ liệu.

Ví dụ:
    
    
    class Product:
    
        def __init__(self):
            self._price = 0
    
        @property
        def price(self):
            return self._price
    
        @price.setter
        def price(self, value):
    
            if value < 0:
                raise ValueError("Price must >= 0")
    
            self._price = value

Sử dụng:
    
    
    p = Product()
    
    p.price = -5

Kết quả:
    
    
    ValueError

Đây là lý do property được ưa chuộng hơn việc để người dùng sửa trực tiếp thuộc tính.

* * *

# 6\. Abstract Property

Ví dụ:
    
    
    from abc import ABC
    from abc import abstractmethod
    
    
    class Animal(ABC):
    
        @property
        @abstractmethod
        def name(self):
            pass

Lớp con:
    
    
    class Dog(Animal):
    
        @property
        def name(self):
            return "Dog"

Được phép tạo object.

* * *

# 7\. Nếu không implement
    
    
    class Cat(Animal):
        pass
    
    
    Cat()

Lỗi:
    
    
    TypeError

Tương tự abstract method.

* * *

# 8\. Vì sao dùng Property?

Giả sử:
    
    
    class Source:
    
        @abstractmethod
        def get_site_name(self):
            ...

Người dùng phải gọi:
    
    
    source.get_site_name()

Nhưng:
    
    
    @property
    @abstractmethod
    def site_name(self):
        ...

Sử dụng:
    
    
    source.site_name

API tự nhiên và dễ đọc hơn.

* * *

# 9\. Áp dụng vào Plugin

Ví dụ:
    
    
    from abc import ABC
    from abc import abstractmethod
    
    
    class BaseSource(ABC):
    
        @property
        @abstractmethod
        def site_name(self):
            pass
    
        @property
        @abstractmethod
        def base_url(self):
            pass

Plugin:
    
    
    class TruyenFull(BaseSource):
    
        @property
        def site_name(self):
            return "TruyenFull"
    
        @property
        def base_url(self):
            return "https://truyenfull.vn"

Framework:
    
    
    print(plugin.site_name)
    print(plugin.base_url)

Rất rõ ràng và không cần các phương thức `get_*()`.

* * *

# 10\. Read-Write Abstract Property

Không chỉ getter.

Có thể bắt buộc setter.

Ví dụ:
    
    
    from abc import ABC
    from abc import abstractmethod
    
    
    class Config(ABC):
    
        @property
        @abstractmethod
        def timeout(self):
            pass
    
        @timeout.setter
        @abstractmethod
        def timeout(self, value):
            pass

Lớp con:
    
    
    class HttpConfig(Config):
    
        def __init__(self):
            self._timeout = 30
    
        @property
        def timeout(self):
            return self._timeout
    
        @timeout.setter
        def timeout(self, value):
    
            if value <= 0:
                raise ValueError
    
            self._timeout = value

* * *

# 11\. Property có thể có body

Abstract Property cũng có thể viết logic:
    
    
    class Animal(ABC):
    
        @property
        @abstractmethod
        def name(self):
            print("Base")

Lớp con:
    
    
    class Dog(Animal):
    
        @property
        def name(self):
    
            super().name
    
            return "Dog"

Tuy nhiên, trong thực tế điều này ít được dùng hơn so với abstract method có body. Nếu property cần chia sẻ nhiều logic, thường nên đưa phần đó vào một helper method riêng để mã nguồn rõ ràng hơn.

* * *

# 12\. Property + Concrete Method

Framework:
    
    
    class BaseSource(ABC):
    
        @property
        @abstractmethod
        def site_name(self):
            pass
    
        def info(self):
    
            return f"Plugin: {self.site_name}"

Plugin:
    
    
    class Wattpad(BaseSource):
    
        @property
        def site_name(self):
            return "Wattpad"

Kết quả:
    
    
    plugin = Wattpad()
    
    print(plugin.info())
    
    
    Plugin: Wattpad

Đây là sự kết hợp rất phổ biến: lớp cơ sở yêu cầu một vài property, sau đó dùng chúng trong các phương thức dùng chung.

* * *

# 13\. Ví dụ Framework hoàn chỉnh
    
    
    from abc import ABC
    from abc import abstractmethod
    
    
    class BaseSource(ABC):
    
        @property
        @abstractmethod
        def site_name(self):
            pass
    
        @property
        @abstractmethod
        def base_url(self):
            pass
    
        @property
        def headers(self):
    
            return {
                "User-Agent": "Crawler"
            }
    
        def crawl(self):
    
            print(self.site_name)
    
            print(self.base_url)
    
            print(self.headers)

Plugin:
    
    
    class TruyenFull(BaseSource):
    
        @property
        def site_name(self):
            return "TruyenFull"
    
        @property
        def base_url(self):
            return "https://truyenfull.vn"

Kết quả:
    
    
    TruyenFull
    
    https://truyenfull.vn
    
    {'User-Agent': 'Crawler'}

* * *

# 14\. Sai lầm phổ biến

Nhiều người viết:
    
    
    class BaseSource(ABC):
    
        @abstractmethod
        def site_name(self):
            ...

Sau đó:
    
    
    plugin.site_name()

Điều này không sai, nhưng nếu `site_name` chỉ là dữ liệu thì dùng property sẽ biểu đạt ý định tốt hơn.

* * *

# 15\. Khi nào dùng Property?

Dùng Property khi:

  * Giá trị là đặc tính của đối tượng. 
  * Không cần tham số. 
  * Truy cập thường xuyên. 
  * Muốn có khả năng thêm validation hoặc tính toán sau này mà không thay đổi API. 



Không nên dùng Property khi:

  * Hành động mất nhiều thời gian (ví dụ gọi API, đọc file lớn, tải dữ liệu mạng). 
  * Có tác dụng phụ (side effects) đáng kể. 
  * Cần truyền nhiều tham số. 



Ví dụ, `download_chapter()` không nên là property vì đó là một hành động.

* * *

# 16\. Áp dụng vào hệ thống crawler

Một thiết kế hợp lý:
    
    
    class BaseSource(ABC):
    
        @property
        @abstractmethod
        def site_name(self):
            ...
    
        @property
        @abstractmethod
        def base_url(self):
            ...
    
        @property
        @abstractmethod
        def encoding(self):
            ...
    
        @property
        def headers(self):
            return {
                "User-Agent": "Crawler/1.0"
            }
    
        @property
        def timeout(self):
            return 30

Plugin:
    
    
    class TruyenFullSource(BaseSource):
    
        @property
        def site_name(self):
            return "TruyenFull"
    
        @property
        def base_url(self):
            return "https://truyenfull.vn"
    
        @property
        def encoding(self):
            return "utf-8"

Framework có thể truy cập thống nhất:
    
    
    print(source.site_name)
    print(source.base_url)
    print(source.timeout)
    print(source.headers)

* * *

# So sánh Method và Property

Method| Property  
---|---  
`user.get_name()`| `user.name`  
Có thể nhận tham số| Không nhận tham số  
Biểu diễn hành động| Biểu diễn trạng thái/thuộc tính  
Phù hợp với thao tác| Phù hợp với dữ liệu  
  
* * *

# Tổng kết

Trong buổi này bạn đã học:

  * `@property`
  * Getter 
  * Setter 
  * Validation 
  * Read-only Property 
  * Abstract Property 
  * Read-Write Abstract Property 
  * Kết hợp Property với Template Method 
  * Thiết kế API sạch bằng Property 



* * *

# Bài tập

## Bài 1

Viết:
    
    
    class Shape(ABC):

Yêu cầu:

  * abstract property `name`
  * abstract property `color`



Cài đặt:
    
    
    Circle
    
    Rectangle

* * *

## Bài 2

Viết:
    
    
    class DatabaseConfig(ABC)

Yêu cầu:

  * host 
  * port 
  * username 
  * password 



Đều là abstract property.

* * *

## Bài 3

Viết:
    
    
    class Storage(ABC)

Yêu cầu:

  * abstract property `capacity`
  * setter kiểm tra capacity > 0 



* * *

## Bài 4 (Áp dụng dự án crawler)

Thiết kế `BaseSource` với các property:
    
    
    site_name
    base_url
    encoding
    headers
    timeout
    rate_limit
    support_proxy

Trong đó:

  * `site_name`, `base_url`, `encoding` là **abstract property**. 
  * `headers`, `timeout`, `rate_limit`, `support_proxy` có giá trị mặc định ở lớp cơ sở nhưng plugin có thể ghi đè nếu cần. 



Đây là một thiết kế rất gần với các framework crawler chuyên nghiệp như Scrapy.

* * *

# Buổi 8

Ở **Buổi 8** , chúng ta sẽ học:

> **ABC + Generic + TypeVar + typing**

Đây là bước đưa ABC lên một cấp độ mới, giúp bạn xây dựng các `Repository`, `Service`, `Storage`, `Parser` và `Plugin` **an toàn về kiểu dữ liệu (type-safe)** , rất phù hợp với dự án crawler truyện và các ứng dụng Python quy mô lớn.

