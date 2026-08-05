Chào bạn! Tôi sẽ hướng dẫn bạn **OOP trong Python ở cấp độ Deep Dive**, không chỉ dừng lại ở class/object cơ bản mà đi sâu vào cách Python thực sự hoạt động.

---

## 📌 PHẦN 1: MÔ HÌNH DỮ LIỆU PYTHON (DATA MODEL)

### 1. **Mọi thứ đều là object**
```python
# Function cũng là object
def hello():
    pass
print(type(hello))  # <class 'function'>
print(dir(hello))   # Xem thuộc tính

# Class cũng là object (instance của type)
class MyClass:
    pass
print(type(MyClass))  # <class 'type'>
```

### 2. **Special Methods (Magic/Dunder Methods)**
Đây là sức mạnh thực sự của OOP Python:

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    # Biểu diễn object
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    # Toán tử +
    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        return NotImplemented
    
    # Toán tử *
    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector(self.x * scalar, self.y * scalar)
        return NotImplemented
    
    # Hỗ trợ scalar * vector
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    # So sánh
    def __eq__(self, other):
        if not isinstance(other, Vector):
            return False
        return self.x == other.x and self.y == other.y
    
    def __lt__(self, other):
        return (self.x**2 + self.y**2) < (other.x**2 + other.y**2)
    
    # Container protocol
    def __len__(self):
        return 2
    
    def __getitem__(self, index):
        return (self.x, self.y)[index]
    
    # Callable object
    def __call__(self):
        return f"Vector at ({self.x}, {self.y})"

# Sử dụng
v1 = Vector(1, 2)
v2 = Vector(3, 4)
v3 = v1 + v2        # Vector(4, 6)
v4 = v1 * 3         # Vector(3, 6)
v5 = 3 * v1         # Vector(3, 6) - nhờ __rmul__
print(len(v1))      # 2
print(v1[0])        # 1
print(v1())         # "Vector at (1, 2)"
```

---

## 📌 PHẦN 2: DESCRIPTORS - LINH HỒN CỦA PROPERTY

### 1. **Data Descriptor vs Non-Data Descriptor**
```python
class PositiveNumber:
    """Data descriptor - quản lý thuộc tính số dương"""
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name, 0)
    
    def __set__(self, instance, value):
        if value < 0:
            raise ValueError(f"{self.name} must be positive")
        instance.__dict__[self.name] = value
    
    def __delete__(self, instance):
        del instance.__dict__[self.name]

class Person:
    age = PositiveNumber()  # Descriptor
    score = PositiveNumber()
    
    def __init__(self, name, age, score):
        self.name = name
        self.age = age
        self.score = score

# p = Person("John", -5, 10)  # ValueError!
```

### 2. **Property - Descriptor được tích hợp sẵn**
```python
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        """Getter - được gọi khi truy cập temp.celsius"""
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        """Setter - được gọi khi gán temp.celsius = value"""
        if value < -273.15:
            raise ValueError("Temperature below absolute zero!")
        self._celsius = value
    
    @celsius.deleter
    def celsius(self):
        """Deleter - được gọi khi del temp.celsius"""
        print("Deleting temperature")
        del self._celsius
    
    @property
    def fahrenheit(self):
        """Read-only property"""
        return (self._celsius * 9/5) + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        """Set by fahrenheit"""
        self.celsius = (value - 32) * 5/9
```

### 3. **Property Factory Pattern**
```python
def validate(validator):
    """Decorator factory để tạo property có validation"""
    def decorator(func):
        name = func.__name__
        
        def getter(self):
            return self.__dict__.get(name)
        
        def setter(self, value):
            validator(value)
            self.__dict__[name] = value
            
        return property(getter, setter)
    return decorator

# Sử dụng
def positive(value):
    if value < 0:
        raise ValueError("Must be positive")

class BankAccount:
    @validate(positive)
    def balance(self):
        pass  # Property sẽ được tạo tự động
    
    def __init__(self, balance):
        self.balance = balance  # Gọi setter
```

---

## 📌 PHẦN 3: METACLASS - TẠO CLASS TẠO RA CLASS

### 1. **Type là metaclass cơ bản**
```python
# Cách tạo class động
MyClass = type('MyClass', (object,), {
    'x': 10,
    'hello': lambda self: "Hello"
})

obj = MyClass()
print(obj.x)      # 10
print(obj.hello()) # "Hello"
```

### 2. **Tạo Metaclass tùy chỉnh**
```python
class MetaValidator(type):
    """Metaclass tự động thêm validation"""
    def __new__(cls, name, bases, dct):
        # Thêm prefix vào tất cả method
        for key, value in dct.items():
            if callable(value) and not key.startswith('_'):
                dct[key] = cls.add_logging(value)
        
        # Thêm __init__ nếu chưa có
        if '__init__' not in dct:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
            dct['__init__'] = __init__
        
        return super().__new__(cls, name, bases, dct)
    
    @staticmethod
    def add_logging(func):
        def wrapper(self, *args, **kwargs):
            print(f"Calling {func.__name__}")
            return func(self, *args, **kwargs)
        return wrapper

class User(metaclass=MetaValidator):
    def say_hello(self):
        return "Hello"

u = User(name="John")
u.say_hello()  # In "Calling say_hello"
```

### 3. **Singleton Pattern với Metaclass**
```python
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.connection = "Connected"
        
    def query(self, sql):
        return f"Executing: {sql}"

db1 = Database()
db2 = Database()
print(db1 is db2)  # True - chỉ có 1 instance
```

---

## 📌 PHẦN 4: ABSTRACT BASE CLASSES (ABC)

### 1. **Tạo Interface trừu tượng**
```python
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator

class Animal(ABC):
    @abstractmethod
    def speak(self):
        """Phải override"""
        pass
    
    @abstractmethod
    def move(self):
        pass
    
    def eat(self):
        """Có thể override hoặc không"""
        return "Eating..."

class Dog(Animal):
    def speak(self):
        return "Woof!"
    
    def move(self):
        return "Running"

# dog = Animal()  # TypeError! Không thể khởi tạo abstract class
```

### 2. **Đăng ký lớp ảo (Virtual Subclass)**
```python
class MyIterable(ABC):
    @abstractmethod
    def __iter__(self):
        pass

# Đăng ký list là subclass ảo của MyIterable
MyIterable.register(list)

print(isinstance([1, 2, 3], MyIterable))  # True
print(issubclass(list, MyIterable))       # True
```

---

## 📌 PHẦN 5: DATACLASSES - CODE NGẮN GỌN

```python
from dataclasses import dataclass, field
from typing import List, Optional
import json

@dataclass
class Person:
    name: str
    age: int = 0
    email: Optional[str] = None
    hobbies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Được gọi sau __init__"""
        if self.age < 0:
            raise ValueError("Age must be positive")
    
    def to_json(self):
        return json.dumps(self.__dict__)

# Tương đương với class thông thường nhưng ngắn gọn hơn nhiều
p1 = Person("John", 30, hobbies=["reading", "coding"])
p2 = Person("John", 30, hobbies=["reading", "coding"])
print(p1 == p2)  # True - có sẵn __eq__
```

### **Dataclass nâng cao**
```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Advanced:
    # Field với metadata
    value: int = field(metadata={'unit': 'px', 'min': 0})
    
    # Field không xuất hiện trong __init__
    _cache: dict = field(default_factory=dict, init=False, repr=False)
    
    # Field tính toán
    @property
    def double(self):
        return self.value * 2
    
    def __post_init__(self):
        self._cache['value'] = self.value
```

---

## 📌 PHẦN 6: MRO - METHOD RESOLUTION ORDER

### 1. **Thứ tự tìm kiếm method**
```python
class A:
    def method(self):
        print("A")

class B(A):
    def method(self):
        print("B")

class C(A):
    def method(self):
        print("C")

class D(B, C):
    pass

d = D()
d.method()  # B (MRO: D -> B -> C -> A)

print(D.__mro__)  # Xem thứ tự
# (<class '__main__.D'>, <class '__main__.B'>, 
#  <class '__main__.C'>, <class '__main__.A'>, <class 'object'>)
```

### 2. **Super() hoạt động thế nào**
```python
class Base:
    def __init__(self):
        print(f"Base init: {self.__class__}")

class A(Base):
    def __init__(self):
        super().__init__()
        print("A init")

class B(Base):
    def __init__(self):
        super().__init__()
        print("B init")

class C(A, B):
    def __init__(self):
        super().__init__()
        print("C init")

# Kết quả:
# Base init: <class '__main__.C'>
# B init
# A init
# C init
# super() đi theo MRO, không phải cha trực tiếp!
```

---

## 📌 PHẦN 7: SLOTS - TỐI ƯU BỘ NHỚ

```python
class NormalClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SlottedClass:
    __slots__ = ('x', 'y')
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Slots tiết kiệm bộ nhớ và nhanh hơn
import sys
normal = NormalClass(1, 2)
slotted = SlottedClass(1, 2)

print(sys.getsizeof(normal.__dict__))  # ~64 bytes
# slotted không có __dict__
# slotted.z = 3  # AttributeError!

# Kết hợp với descriptor
class Efficient:
    __slots__ = ('_value',)
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = val * 2
```

---

## 📌 PHẦN 8: PATTERN THIẾT KẾ NÂNG CAO

### 1. **Builder Pattern**
```python
class Pizza:
    def __init__(self):
        self.size = None
        self.cheese = False
        self.pepperoni = False
        self.mushrooms = False
    
    def __str__(self):
        return f"Pizza(size={self.size}, cheese={self.cheese}, ...)"

class PizzaBuilder:
    def __init__(self):
        self.pizza = Pizza()
    
    def set_size(self, size):
        self.pizza.size = size
        return self
    
    def add_cheese(self):
        self.pizza.cheese = True
        return self
    
    def add_pepperoni(self):
        self.pizza.pepperoni = True
        return self
    
    def add_mushrooms(self):
        self.pizza.mushrooms = True
        return self
    
    def build(self):
        return self.pizza

# Sử dụng fluent interface
pizza = (PizzaBuilder()
         .set_size("large")
         .add_cheese()
         .add_pepperoni()
         .build())
```

### 2. **Context Manager Pattern**
```python
class Timer:
    def __enter__(self):
        import time
        self.start = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        elapsed = time.time() - self.start
        print(f"Elapsed: {elapsed:.3f}s")
        return False  # Không suppress exception

# Sử dụng
with Timer():
    # Code ở đây sẽ được timing
    sum(range(1000000))
```

---

## 📌 BÀI TẬP THỰC HÀNH TỔNG HỢP

### **Xây dựng hệ thống ORM mini**
```python
class Field:
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)
    
    def __set__(self, instance, value):
        self.validate(value)
        instance.__dict__[self.name] = value
    
    def validate(self, value):
        pass

class IntegerField(Field):
    def validate(self, value):
        if not isinstance(value, int):
            raise TypeError(f"{self.name} must be int")

class StringField(Field):
    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError(f"{self.name} must be str")
        if len(value) > 255:
            raise ValueError(f"{self.name} max length 255")

class MetaModel(type):
    def __new__(cls, name, bases, dct):
        fields = {}
        for key, value in dct.items():
            if isinstance(value, Field):
                fields[key] = value
        dct['_fields'] = fields
        return super().__new__(cls, name, bases, dct)

class Model(metaclass=MetaModel):
    def __init__(self, **kwargs):
        for name, field in self._fields.items():
            setattr(self, name, kwargs.get(name))
    
    def save(self):
        # Giả lập lưu vào DB
        print(f"Saving {self}")

class User(Model):
    id = IntegerField()
    name = StringField()
    email = StringField()

user = User(id=1, name="John", email="john@example.com")
user.save()
```

---

## 📌 TIPS QUAN TRỌNG

1. **Dùng `__slots__`** khi tạo nhiều object để tiết kiệm memory
2. **Dùng `@dataclass`** thay vì viết boilerplate __init__, __repr__
3. **Dùng `@property`** thay vì getter/setter kiểu Java
4. **Kế thừa chỉ nên dùng** khi thực sự là "is-a" relationship
5. **Prefer composition over inheritance** - dùng thành phần thay vì kế thừa
6. **Dùng ABC** để định nghĩa interface rõ ràng
7. **Đừng lạm dụng metaclass** - chỉ dùng khi thực sự cần

---

Bạn muốn tôi đi sâu vào phần nào hơn? Có thể thực hành code cùng tôi với một dự án cụ thể như xây dựng web framework mini hoặc game engine đơn giản!