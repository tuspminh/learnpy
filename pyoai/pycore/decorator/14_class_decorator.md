# Decorator Deep Dive — Buổi 14

# Class Decorator (Decorator áp dụng lên Class)

> Đây là một chủ đề **hoàn toàn khác** với **Class-based Decorator** (buổi 11).

Rất nhiều người nhầm lẫn:

Chủ đề| Decorator áp dụng lên  
---|---  
**Class-based Decorator**|  Function/Method  
**Class Decorator**|  Class  
  
Ví dụ:
    
    
    @Logger
    def hello():
        ...

ở buổi 11 là **Class-based Decorator**.

Còn hôm nay:
    
    
    @singleton
    class Database:
        ...

là **Class Decorator**.

Đây là kỹ thuật được sử dụng trong:

  * dataclasses 
  * attrs 
  * pydantic 
  * SQLAlchemy 
  * Django ORM 
  * FastAPI Models 
  * Marshmallow 
  * Plugin Framework 



* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Class Decorator là gì 
  * Python decorate class như thế nào 
  * Thêm thuộc tính vào class 
  * Sửa đổi class 
  * Thay thế class 
  * Registry Pattern 
  * Singleton bằng Class Decorator 
  * Best Practices 



* * *

# 1\. Decorator áp dụng lên Class

Function
    
    
    @logger
    def hello():
        ...

Python dịch
    
    
    hello = logger(hello)

Class
    
    
    @logger
    class User:
        ...

Python dịch thành
    
    
    User = logger(User)

Hoàn toàn giống.

Chỉ khác đối tượng truyền vào là:
    
    
    Function

hay
    
    
    Class

* * *

# 2\. Decorator đơn giản nhất
    
    
    def decorator(cls):
    
        print(cls)
    
        return cls

Sử dụng
    
    
    @decorator
    class User:
        pass

Kết quả
    
    
    <class '__main__.User'>

Decorator nhận **chính class**.

* * *

# 3\. Class cũng là Object

Đây là điều cực kỳ quan trọng.

Ví dụ
    
    
    class User:
        pass

Kiểm tra
    
    
    print(type(User))

Kết quả
    
    
    <class 'type'>

Class cũng là object.

Cho nên
    
    
    User.name = "Administrator"

hoàn toàn hợp lệ.

* * *

# 4\. Thêm thuộc tính

Decorator
    
    
    def entity(cls):
    
        cls.table = cls.__name__.lower()
    
        return cls

Sử dụng
    
    
    @entity
    class User:
        pass

Kiểm tra
    
    
    print(User.table)

Kết quả
    
    
    user

* * *

# 5\. Thêm Method
    
    
    def printable(cls):
    
        def display(self):
    
            print(vars(self))
    
        cls.display = display
    
        return cls

Ví dụ
    
    
    @printable
    class Student:
    
        def __init__(self):
    
            self.name = "Alice"
    
            self.age = 18
    
    
    s = Student()
    
    s.display()

Kết quả
    
    
    {
        'name': 'Alice',
        'age': 18
    }

* * *

# 6\. Thêm nhiều Method
    
    
    def model(cls):
    
        def save(self):
    
            print("Save")
    
        def delete(self):
    
            print("Delete")
    
        cls.save = save
        cls.delete = delete
    
        return cls

Giống ORM.
    
    
    @model
    class User:
        pass
    
    
    User().save()

* * *

# 7\. Thêm Metadata
    
    
    def metadata(author):
    
        def decorator(cls):
    
            cls.author = author
    
            cls.version = "1.0"
    
            return cls
    
        return decorator
    
    
    @metadata("Garden")
    class Plugin:
        pass
    
    
    print(Plugin.author)
    
    
    Garden

* * *

# 8\. Registry Pattern

Đây là mẫu cực kỳ phổ biến.
    
    
    PLUGINS = {}

Decorator
    
    
    def register(cls):
    
        PLUGINS[
            cls.__name__
        ] = cls
    
        return cls
    
    
    @register
    class JsonParser:
        pass
    
    
    @register
    class XmlParser:
        pass

Kết quả
    
    
    print(PLUGINS)
    
    
    {
        'JsonParser': JsonParser,
        'XmlParser': XmlParser
    }

* * *

# 9\. Tạo Instance từ Registry
    
    
    parser = PLUGINS["JsonParser"]()
    
    print(parser)

Đây là nền tảng của:

  * Plugin System 
  * ORM 
  * Dependency Injection 
  * Serializer 



* * *

# 10\. Singleton

Một ứng dụng nổi tiếng.
    
    
    def singleton(cls):
    
        instance = None
    
        def get_instance(*args, **kwargs):
    
            nonlocal instance
    
            if instance is None:
                instance = cls(*args, **kwargs)
    
            return instance
    
        return get_instance

Sử dụng
    
    
    @singleton
    class Database:
    
        pass
    
    
    a = Database()
    
    b = Database()
    
    print(a is b)

Kết quả
    
    
    True

* * *

# 11\. Decorator thay thế Class

Decorator không bắt buộc trả về class cũ.
    
    
    def replace(cls):
    
        class NewClass(cls):
    
            pass
    
        return NewClass

Python
    
    
    User = replace(User)

Lúc này
    
    
    User

đã là
    
    
    NewClass

* * *

# 12\. Logging Constructor
    
    
    def log_creation(cls):
    
        original = cls.__init__
    
        def new_init(self, *args, **kwargs):
    
            print(
                f"Creating {cls.__name__}"
            )
    
            original(
                self,
                *args,
                **kwargs
            )
    
        cls.__init__ = new_init
    
        return cls

Ví dụ
    
    
    @log_creation
    class User:
    
        def __init__(self, name):
    
            self.name = name
    
    
    u = User("Alice")

Kết quả
    
    
    Creating User

* * *

# 13\. Validation
    
    
    def validate_model(cls):
    
        if "__init__" not in cls.__dict__:
    
            raise TypeError(
                "Model needs __init__"
            )
    
        return cls

Áp dụng
    
    
    @validate_model
    class User:
        pass

Lỗi ngay khi import.

* * *

# 14\. Ví dụ ORM
    
    
    MODELS = {}

Decorator
    
    
    def model(cls):
    
        MODELS[
            cls.__name__
        ] = cls
    
        cls.table = cls.__name__.lower()
    
        return cls
    
    
    @model
    class User:
    
        pass
    
    
    @model
    class Product:
    
        pass

Sau khi import
    
    
    print(MODELS)
    
    
    print(User.table)

Kết quả
    
    
    {
        'User': User,
        'Product': Product
    }
    
    
    user

Đây là ý tưởng mà rất nhiều ORM sử dụng.

* * *

# 15\. Ví dụ Plugin Framework
    
    
    PLUGINS = {}

Decorator
    
    
    def plugin(name):
    
        def decorator(cls):
    
            PLUGINS[name] = cls
    
            cls.plugin_name = name
    
            return cls
    
        return decorator
    
    
    @plugin("json")
    class JsonPlugin:
    
        pass
    
    
    @plugin("xml")
    class XmlPlugin:
    
        pass

Kết quả
    
    
    plugin_cls = PLUGINS["json"]
    
    plugin = plugin_cls()

* * *

# 16\. Ví dụ Auto ID
    
    
    def auto_id(cls):
    
        original = cls.__init__
    
        counter = 0
    
        def new_init(self, *args, **kwargs):
    
            nonlocal counter
    
            counter += 1
    
            self.id = counter
    
            original(
                self,
                *args,
                **kwargs
            )
    
        cls.__init__ = new_init
    
        return cls
    
    
    @auto_id
    class User:
    
        def __init__(self, name):
    
            self.name = name
    
    
    u1 = User("A")
    u2 = User("B")
    
    print(u1.id)
    print(u2.id)

Kết quả
    
    
    1
    2

* * *

# 17\. Decorator của dataclass

Một trong những ví dụ nổi tiếng nhất.
    
    
    from dataclasses import dataclass
    
    @dataclass
    class User:
    
        name: str
        age: int

Python sẽ tự sinh:

  * `__init__`
  * `__repr__`
  * `__eq__`
  * `__hash__` (tùy cấu hình) 
  * và nhiều thứ khác. 



Nghĩa là:
    
    
    User
    
    ↓
    
    dataclass(User)
    
    ↓
    
    User mới

Đây chính là **Class Decorator**.

* * *

# 18\. Class Decorator vs Metaclass

Nhiều người nhầm hai khái niệm này.

Class Decorator| Metaclass  
---|---  
Chạy sau khi class được tạo| Chạy trong lúc tạo class  
Dễ học| Khó hơn  
Phù hợp 90% nhu cầu| Dùng cho trường hợp đặc biệt  
Viết như function| Kế thừa `type`  
  
Nếu có thể dùng Class Decorator thì **không nên dùng Metaclass**.

* * *

# 19\. Best Practices

✅ Luôn trả về class hoặc lớp thay thế hợp lệ.
    
    
    return cls

hoặc
    
    
    return NewClass

* * *

✅ Không sửa quá nhiều hành vi của class trong một decorator.

Thay vì:
    
    
    @magic_everything

hãy tách thành:
    
    
    @register
    @validate
    @entity

* * *

✅ Nếu sửa `__init__`, nên gọi lại `original`.
    
    
    original(self, *args, **kwargs)

* * *

✅ Nếu thêm method, tránh ghi đè tên đã tồn tại.
    
    
    if not hasattr(cls, "save"):
        cls.save = save

* * *

# 20\. Ví dụ hoàn chỉnh
    
    
    MODELS = {}
    
    
    def entity(table_name=None):
        def decorator(cls):
            name = table_name or cls.__name__.lower()
    
            cls.table = name
            MODELS[name] = cls
    
            def save(self):
                print(f"Saving into table '{self.table}'")
    
            def delete(self):
                print(f"Deleting from table '{self.table}'")
    
            if not hasattr(cls, "save"):
                cls.save = save
    
            if not hasattr(cls, "delete"):
                cls.delete = delete
    
            return cls
    
        return decorator
    
    
    @entity("users")
    class User:
    
        def __init__(self, name):
            self.name = name
    
    
    @entity()
    class Product:
    
        def __init__(self, title):
            self.title = title
    
    
    u = User("Alice")
    p = Product("Laptop")
    
    u.save()
    p.save()
    
    print(User.table)
    print(Product.table)
    print(MODELS)

Ví dụ kết quả:
    
    
    Saving into table 'users'
    Saving into table 'product'
    users
    product
    {
        'users': <class '__main__.User'>,
        'product': <class '__main__.Product'>
    }

Đây là mô hình thu nhỏ của nhiều ORM hiện đại.

* * *

# Những lỗi phổ biến

## Sai 1

Quên trả về class.
    
    
    def decorator(cls):
    
        cls.version = 1

Kết quả:
    
    
    User = None

* * *

## Sai 2

Thay `__init__` nhưng không gọi lại hàm gốc.
    
    
    cls.__init__ = new_init

mà không:
    
    
    original(self, *args, **kwargs)

Khiến đối tượng không được khởi tạo đầy đủ.

* * *

## Sai 3

Ghi đè method đã có.
    
    
    cls.save = save

có thể vô tình làm mất method do lập trình viên tự viết.

* * *

# Tổng kết buổi 14

Bạn cần ghi nhớ:

  1. `@decorator` trên class tương đương `Class = decorator(Class)`. 
  2. Class là object nên có thể được chỉnh sửa hoặc thay thế. 
  3. Class Decorator có thể: 
     * Thêm thuộc tính. 
     * Thêm method. 
     * Đăng ký vào registry. 
     * Sửa `__init__`. 
     * Trả về lớp mới. 
  4. `@dataclass` là ví dụ điển hình của Class Decorator. 
  5. Class Decorator đơn giản và dễ bảo trì hơn Metaclass trong phần lớn trường hợp. 



* * *

# Bài tập

## Bài 1

Viết Class Decorator:
    
    
    @entity
    class User:
        ...

Yêu cầu:

  * Thêm thuộc tính `table`. 
  * Thêm method `save()`. 
  * Thêm method `delete()`. 



* * *

## Bài 2

Viết hệ thống Plugin:
    
    
    @plugin("json")
    class JsonPlugin:
        ...
    
    @plugin("xml")
    class XmlPlugin:
        ...

Yêu cầu:

  * Lưu tất cả plugin vào dictionary. 
  * Viết hàm: 


    
    
    create_plugin(name)

để tạo instance theo tên plugin.

* * *

## Bài 3

Viết Class Decorator:
    
    
    @auto_timestamp
    class Article:
        ...

Yêu cầu:

  * Khi tạo object, tự động thêm: 
    * `created_at`
    * `updated_at`
  * Viết method `touch()` để cập nhật `updated_at`. 
  * Không làm thay đổi `__init__` gốc ngoài việc bổ sung hành vi. 



* * *

# Chuẩn bị cho buổi 15

Buổi tiếp theo là **Property Decorator**. Đây là chủ đề cực kỳ quan trọng trong OOP Python. Bạn sẽ học:

  * `@property`
  * `@x.setter`
  * `@x.deleter`
  * Thuộc tính tính toán (computed property) 
  * Validation qua property 
  * Lazy Property 
  * Cached Property 
  * Cơ chế Descriptor đứng sau `property`



Đây là nền tảng để hiểu vì sao `property` thực chất cũng là một dạng **decorator + descriptor** , và là cầu nối để tiến tới các chủ đề nâng cao như Descriptor Protocol và ORM.

