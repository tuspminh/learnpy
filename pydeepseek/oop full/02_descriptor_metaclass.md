# 🚀 BUỔI 2: OOP PYTHON - DESCRIPTORS, PROPERTIES & METACLASS

Chào mừng đến buổi 2! Hôm nay chúng ta sẽ **đi sâu vào cốt lõi** của Python OOP - những thứ làm nên sức mạnh và sự linh hoạt của ngôn ngữ này.

---

## 📚 MỤC TIÊU BUỔI 2

1. Hiểu sâu về **Descriptor Protocol** - linh hồn của property
2. Thành thạo **Property** và cách tạo property động
3. Nắm vững **Metaclass** - class tạo ra class
4. Xây dựng **ORM mini** và **Validation Framework**

---

## 🎯 PHẦN 1: DESCRIPTOR PROTOCOL

### 1.1. Descriptor là gì?

Descriptor là object implement ít nhất 1 trong 3 methods: `__get__`, `__set__`, `__delete__`

```python
print("=== DESCRIPTOR PROTOCOL ===")

class DescriptorExample:
    """Ví dụ đơn giản về descriptor"""
    
    def __init__(self, default=None):
        self.default = default
        self.name = None
    
    def __set_name__(self, owner, name):
        """Được gọi khi descriptor được gán vào class attribute"""
        self.name = name
        print(f"Descriptor '{name}' assigned to {owner.__name__}")
    
    def __get__(self, instance, owner):
        """Được gọi khi truy cập attribute"""
        if instance is None:
            return self
        print(f"Getting {self.name} from {instance}")
        return instance.__dict__.get(self.name, self.default)
    
    def __set__(self, instance, value):
        """Được gọi khi gán giá trị cho attribute"""
        print(f"Setting {self.name} = {value}")
        instance.__dict__[self.name] = value
    
    def __delete__(self, instance):
        """Được gọi khi xóa attribute"""
        print(f"Deleting {self.name}")
        del instance.__dict__[self.name]

class MyClass:
    # Descriptor là class attribute
    x = DescriptorExample(0)
    y = DescriptorExample(1)
    
    def __init__(self, x, y):
        self.x = x  # Gọi __set__
        self.y = y

# Demo
obj = MyClass(10, 20)
print(obj.x)  # Gọi __get__
obj.x = 100   # Gọi __set__
del obj.x     # Gọi __delete__
```

### 1.2. Data Descriptor vs Non-Data Descriptor

```python
print("\n=== DATA VS NON-DATA DESCRIPTOR ===")

class DataDescriptor:
    """Data descriptor - có __set__ hoặc __delete__"""
    def __init__(self, default=0):
        self.default = default
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get('_data', self.default)
    
    def __set__(self, instance, value):
        print(f"DataDescriptor: setting {value}")
        instance.__dict__['_data'] = value

class NonDataDescriptor:
    """Non-data descriptor - chỉ có __get__"""
    def __get__(self, instance, owner):
        if instance is None:
            return self
        print("NonDataDescriptor: getting value")
        return 42

class TestClass:
    data_desc = DataDescriptor()
    non_data_desc = NonDataDescriptor()
    
    def __init__(self):
        self.instance_attr = "I'm instance attr"

# Demo
obj = TestClass()

# Data descriptor - ưu tiên hơn instance attribute
print("\n--- Data Descriptor ---")
obj.data_desc = 100  # Gọi __set__
print(obj.data_desc)  # 100
obj.__dict__['data_desc'] = "hack"  # Gán trực tiếp vào __dict__
print(obj.data_desc)  # Vẫn là 100 (descriptor override)

# Non-data descriptor - instance attribute override
print("\n--- Non-Data Descriptor ---")
print(obj.non_data_desc)  # 42 (gọi descriptor)
obj.non_data_desc = "instance value"  # Gán vào instance
print(obj.non_data_desc)  # "instance value" (instance attr override)
del obj.non_data_desc     # Xóa instance attr
print(obj.non_data_desc)  # 42 (descriptor trở lại)
```

### 1.3. Descriptor cho Validation

```python
print("\n=== DESCRIPTOR FOR VALIDATION ===")

class Validator:
    """Base validator descriptor"""
    
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
        """Override in subclass"""
        pass

class PositiveInt(Validator):
    """Validate positive integer"""
    
    def validate(self, value):
        if not isinstance(value, int):
            raise TypeError(f"{self.name} must be integer")
        if value < 0:
            raise ValueError(f"{self.name} must be positive")
        return True

class StringLength(Validator):
    """Validate string length"""
    
    def __init__(self, min_len=0, max_len=100):
        self.min_len = min_len
        self.max_len = max_len
    
    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError(f"{self.name} must be string")
        if not (self.min_len <= len(value) <= self.max_len):
            raise ValueError(
                f"{self.name} length must be between {self.min_len} and {self.max_len}"
            )

class Email(Validator):
    """Validate email format"""
    
    def validate(self, value):
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            raise ValueError(f"{self.name} must be valid email")

class User:
    """Sử dụng các validator descriptors"""
    
    age = PositiveInt()
    name = StringLength(min_len=2, max_len=50)
    email = Email()
    
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email
    
    def __repr__(self):
        return f"User(name='{self.name}', age={self.age}, email='{self.email}')"

# Demo
try:
    user = User("John", 25, "john@example.com")
    print(user)
    
    # user = User("J", 25, "john@example.com")  # ValueError: name too short
    # user = User("John", -5, "john@example.com")  # ValueError: age must be positive
    # user = User("John", 25, "notemail")  # ValueError: invalid email
    
except Exception as e:
    print(f"Validation error: {e}")
```

### 1.4. Lazy Loading Descriptor

```python
print("\n=== LAZY LOADING DESCRIPTOR ===")

class LazyProperty:
    """Chỉ tính toán giá trị khi được truy cập lần đầu"""
    
    def __init__(self, func):
        self.func = func
        self.name = func.__name__
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        # Tính toán và lưu vào instance dict
        value = self.func(instance)
        instance.__dict__[self.name] = value
        print(f"Lazy property '{self.name}' computed and cached")
        return value

class DatabaseConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        print(f"DatabaseConnection initialized with {host}:{port}")
    
    @LazyProperty
    def connection(self):
        """Kết nối chỉ được tạo khi thực sự cần"""
        print(f"Establishing connection to {self.host}:{self.port}")
        # Giả lập kết nối tốn thời gian
        import time
        time.sleep(0.5)
        return f"Connection to {self.host}:{self.port}"
    
    @LazyProperty
    def stats(self):
        """Thống kê chỉ được tính khi cần"""
        print("Computing statistics...")
        return {"queries": 0, "rows": 0}

# Demo
db = DatabaseConnection("localhost", 5432)
print("Database object created")

print("\nFirst access to connection:")
print(db.connection)  # Lần đầu - tính toán

print("\nSecond access to connection:")
print(db.connection)  # Lần sau - lấy từ cache

print("\nAccessing stats:")
print(db.stats)       # Tính toán lần đầu
print(db.stats)       # Lấy từ cache
```

---

## 🔧 PHẦN 2: PROPERTY NÂNG CAO

### 2.1. Property với Validation và Cache

```python
print("\n=== ADVANCED PROPERTY ===")

class Circle:
    def __init__(self, radius=1):
        self._radius = radius
        self._area_cache = None
        self._circumference_cache = None
    
    @property
    def radius(self):
        """Bán kính - getter"""
        return self._radius
    
    @radius.setter
    def radius(self, value):
        """Setter với validation và clear cache"""
        if value <= 0:
            raise ValueError("Radius must be positive")
        if value != self._radius:
            self._radius = value
            # Clear cache khi radius thay đổi
            self._area_cache = None
            self._circumference_cache = None
    
    @property
    def diameter(self):
        """Đường kính - read-only property"""
        return self._radius * 2
    
    @property
    def area(self):
        """Diện tích - tính toán và cache"""
        if self._area_cache is None:
            import math
            self._area_cache = math.pi * self._radius ** 2
            print(f"Computing area: {self._area_cache}")
        return self._area_cache
    
    @property
    def circumference(self):
        """Chu vi - tính toán và cache"""
        if self._circumference_cache is None:
            import math
            self._circumference_cache = 2 * math.pi * self._radius
            print(f"Computing circumference: {self._circumference_cache}")
        return self._circumference_cache

# Demo
c = Circle(5)
print(f"Radius: {c.radius}")
print(f"Diameter: {c.diameter}")
print(f"Area: {c.area}")        # Tính toán lần đầu
print(f"Area: {c.area}")        # Lấy từ cache
print(f"Circumference: {c.circumference}")

c.radius = 10  # Setter được gọi, cache cleared
print(f"\nNew Area: {c.area}")  # Tính toán lại
```

### 2.2. Property Factory

```python
print("\n=== PROPERTY FACTORY ===")

def typed_property(name, expected_type, default=None):
    """Factory tạo property với type checking"""
    
    storage_name = f"_{name}"
    
    @property
    def prop(self):
        return getattr(self, storage_name, default)
    
    @prop.setter
    def prop(self, value):
        if not isinstance(value, expected_type):
            raise TypeError(f"{name} must be {expected_type.__name__}")
        setattr(self, storage_name, value)
    
    return prop

def ranged_property(name, min_val, max_val, default=None):
    """Factory tạo property với range validation"""
    
    storage_name = f"_{name}"
    
    @property
    def prop(self):
        return getattr(self, storage_name, default)
    
    @prop.setter
    def prop(self, value):
        if not (min_val <= value <= max_val):
            raise ValueError(f"{name} must be between {min_val} and {max_val}")
        setattr(self, storage_name, value)
    
    return prop

class Product:
    # Sử dụng property factory
    name = typed_property("name", str, "Unnamed")
    price = typed_property("price", (int, float), 0.0)
    quantity = ranged_property("quantity", 0, 1000, 0)
    
    # Hoặc kết hợp
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity
    
    @property
    def total(self):
        return self.price * self.quantity

# Demo
p = Product("Laptop", 999.99, 10)
print(f"{p.name}: ${p.price} x {p.quantity} = ${p.total}")

# p.name = 123  # TypeError!
# p.quantity = 2000  # ValueError!
```

### 2.3. Property với Computed Fields

```python
print("\n=== COMPUTED FIELDS ===")

class Person:
    def __init__(self, first_name, last_name, birth_year):
        self.first_name = first_name
        self.last_name = last_name
        self.birth_year = birth_year
        self._full_name = None
    
    @property
    def full_name(self):
        """Full name - computed từ first_name và last_name"""
        if self._full_name is None:
            self._full_name = f"{self.first_name} {self.last_name}"
        return self._full_name
    
    @full_name.setter
    def full_name(self, value):
        """Có thể set full_name, tự động tách ra"""
        parts = value.split()
        if len(parts) >= 2:
            self.first_name = parts[0]
            self.last_name = " ".join(parts[1:])
            self._full_name = value
        else:
            raise ValueError("Full name must have at least first and last name")
    
    @property
    def age(self):
        """Age - tính từ birth_year"""
        from datetime import datetime
        return datetime.now().year - self.birth_year
    
    @property
    def is_adult(self):
        """Boolean property"""
        return self.age >= 18
    
    @property
    def initials(self):
        """Initials - computed"""
        return f"{self.first_name[0]}.{self.last_name[0]}."

# Demo
p = Person("John", "Doe", 1990)
print(f"Name: {p.full_name}")
print(f"Age: {p.age}")
print(f"Adult: {p.is_adult}")
print(f"Initials: {p.initials}")

p.full_name = "Jane Smith"  # Setter được gọi
print(f"New name: {p.full_name}")
print(f"First: {p.first_name}, Last: {p.last_name}")
```

---

## 🧠 PHẦN 3: METACLASS

### 3.1. Hiểu về Type và Metaclass

```python
print("\n=== TYPE AND METACLASS ===")

# Mọi class đều là instance của type
class MyClass:
    pass

print(f"MyClass is instance of: {type(MyClass)}")
print(f"MyClass() is instance of: {type(MyClass())}")

# Tạo class động với type
def hello(self):
    return "Hello from dynamic class!"

DynamicClass = type('DynamicClass', (object,), {
    'x': 10,
    'say_hello': hello
})

obj = DynamicClass()
print(f"{obj.say_hello()} x={obj.x}")

# Xem MRO
print(f"\nMRO của MyClass: {MyClass.__mro__}")
print(f"MRO của DynamicClass: {DynamicClass.__mro__}")
```

### 3.2. Custom Metaclass

```python
print("\n=== CUSTOM METACLASS ===")

class MetaLogger(type):
    """Metaclass tự động log class creation"""
    
    def __new__(cls, name, bases, dct):
        print(f"Creating class: {name}")
        print(f"  Bases: {bases}")
        print(f"  Attributes: {list(dct.keys())}")
        
        # Thêm prefix vào tất cả methods
        for key, value in dct.items():
            if callable(value) and not key.startswith('_'):
                dct[f"logged_{key}"] = cls._add_logging(value)
        
        return super().__new__(cls, name, bases, dct)
    
    @staticmethod
    def _add_logging(func):
        def wrapper(self, *args, **kwargs):
            print(f"  ▶ Calling {func.__name__}")
            return func(self, *args, **kwargs)
        return wrapper

class LoggedClass(metaclass=MetaLogger):
    def greet(self):
        return "Hello!"
    
    def add(self, a, b):
        return a + b

# Khi class được tạo, metaclass tự động log
print("\n--- Using LoggedClass ---")
obj = LoggedClass()
obj.logged_greet()
obj.logged_add(3, 5)
```

### 3.3. Metaclass cho Singleton

```python
print("\n=== SINGLETON WITH METACLASS ===")

class SingletonMeta(type):
    """Metaclass đảm bảo chỉ có 1 instance"""
    
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            print(f"Creating first instance of {cls.__name__}")
            cls._instances[cls] = super().__call__(*args, **kwargs)
        else:
            print(f"Returning existing instance of {cls.__name__}")
        return cls._instances[cls]
    
    def __del__(cls):
        """Cleanup khi class bị xóa"""
        if cls in cls._instances:
            del cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self, host="localhost"):
        self.host = host
        self.connection_id = id(self)
        print(f"Database connected to {host}")
    
    def query(self, sql):
        return f"Executing '{sql}' on {self.host} (conn: {self.connection_id})"

# Demo
db1 = Database("prod-server")
db2 = Database("dev-server")  # Vẫn trả về instance đầu tiên
db3 = Database()

print(f"db1 is db2: {db1 is db2}")
print(f"db1 is db3: {db1 is db3}")
print(db1.query("SELECT * FROM users"))
print(db2.query("SELECT * FROM products"))
```

### 3.4. Metaclass cho Registry Pattern

```python
print("\n=== REGISTRY PATTERN ===")

class RegistryMeta(type):
    """Metaclass tự động đăng ký các class con"""
    
    registry = {}
    
    def __new__(cls, name, bases, dct):
        # Tạo class
        new_class = super().__new__(cls, name, bases, dct)
        
        # Đăng ký class nếu có attribute 'register'
        if dct.get('register', True):
            if name != 'BaseModel':
                cls.registry[name] = new_class
                print(f"Registered: {name}")
        
        return new_class
    
    @classmethod
    def get_registered(cls):
        return cls.registry.copy()
    
    @classmethod
    def get_class(cls, name):
        return cls.registry.get(name)

class BaseModel(metaclass=RegistryMeta):
    """Base class - các subclass tự động đăng ký"""
    register = True
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class User(BaseModel):
    register = True
    pass

class Product(BaseModel):
    pass

class Order(BaseModel):
    register = True

class TempModel(BaseModel):
    register = False  # Không đăng ký

# Xem registry
print(f"\nRegistered classes: {RegistryMeta.get_registered().keys()}")

# Sử dụng registry để tạo object
UserClass = RegistryMeta.get_class('User')
user = UserClass(name="John", age=30)
print(f"User: {user.name}, {user.age}")
```

### 3.5. Metaclass cho ORM Style

```python
print("\n=== ORM STYLE WITH METACLASS ===")

class Field:
    def __init__(self, field_type, required=True, default=None):
        self.field_type = field_type
        self.required = required
        self.default = default
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name, self.default)
    
    def __set__(self, instance, value):
        if value is None and self.required:
            raise ValueError(f"{self.name} is required")
        if value is not None and not isinstance(value, self.field_type):
            raise TypeError(f"{self.name} must be {self.field_type.__name__}")
        instance.__dict__[self.name] = value

class ModelMeta(type):
    """Metaclass cho ORM models"""
    
    def __new__(cls, name, bases, dct):
        # Lưu fields
        fields = {}
        for key, value in dct.items():
            if isinstance(value, Field):
                fields[key] = value
                value.name = key
        
        # Lưu vào class
        dct['_fields'] = fields
        
        # Tạo class
        new_class = super().__new__(cls, name, bases, dct)
        
        # Đăng ký vào registry
        if not hasattr(cls, 'registry'):
            cls.registry = {}
        if name != 'Model':
            cls.registry[name] = new_class
        
        return new_class

class Model(metaclass=ModelMeta):
    """Base ORM model"""
    
    def __init__(self, **kwargs):
        for name, field in self._fields.items():
            value = kwargs.get(name, field.default)
            setattr(self, name, value)
    
    def save(self):
        """Lưu vào database giả lập"""
        table = self.__class__.__name__.lower()
        data = {}
        for name, field in self._fields.items():
            data[name] = getattr(self, name, field.default)
        print(f"SAVING to {table}: {data}")
    
    @classmethod
    def get_all(cls):
        """Lấy tất cả records"""
        print(f"SELECT * FROM {cls.__name__.lower()}")
        return []

class User(Model):
    id = Field(int, required=True)
    name = Field(str, required=True)
    email = Field(str, required=True)
    age = Field(int, required=False, default=0)

class Product(Model):
    id = Field(int, required=True)
    name = Field(str, required=True)
    price = Field(float, required=True)
    stock = Field(int, required=False, default=0)

# Demo
print("\n--- ORM Demo ---")
user = User(id=1, name="John Doe", email="john@example.com", age=30)
user.save()

product = Product(id=1, name="Laptop", price=999.99, stock=10)
product.save()

# Lấy danh sách
User.get_all()
Product.get_all()

# Kiểm tra fields
print(f"\nUser fields: {User._fields.keys()}")
print(f"Product fields: {Product._fields.keys()}")
```

---

## 🏗️ PHẦN 4: PROJECT - VALIDATION FRAMEWORK

```python
print("\n=== PROJECT: VALIDATION FRAMEWORK ===")

class ValidationError(Exception):
    """Custom exception cho validation errors"""
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class Validator:
    """Base validator"""
    
    def __init__(self, message=None):
        self.message = message
    
    def __call__(self, value):
        if not self.validate(value):
            raise ValidationError(self.field, self.message or self.default_message)
        return value
    
    def validate(self, value):
        raise NotImplementedError

class Required(Validator):
    default_message = "This field is required"
    
    def validate(self, value):
        return value is not None and value != ""

class MinLength(Validator):
    def __init__(self, min_len, message=None):
        super().__init__(message)
        self.min_len = min_len
    
    @property
    def default_message(self):
        return f"Must be at least {self.min_len} characters"
    
    def validate(self, value):
        if value is None:
            return False
        return len(str(value)) >= self.min_len

class MaxLength(Validator):
    def __init__(self, max_len, message=None):
        super().__init__(message)
        self.max_len = max_len
    
    @property
    def default_message(self):
        return f"Must be at most {self.max_len} characters"
    
    def validate(self, value):
        if value is None:
            return True
        return len(str(value)) <= self.max_len

class Email(Validator):
    default_message = "Must be a valid email address"
    
    def validate(self, value):
        import re
        if not value:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))

class Range(Validator):
    def __init__(self, min_val, max_val, message=None):
        super().__init__(message)
        self.min_val = min_val
        self.max_val = max_val
    
    @property
    def default_message(self):
        return f"Must be between {self.min_val} and {self.max_val}"
    
    def validate(self, value):
        if value is None:
            return False
        return self.min_val <= value <= self.max_val

class ValidatedField:
    """Descriptor với validation"""
    
    def __init__(self, *validators):
        self.validators = validators
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
        for validator in self.validators:
            validator.field = name
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)
    
    def __set__(self, instance, value):
        for validator in self.validators:
            value = validator(value)  # Validate và trả về value
        instance.__dict__[self.name] = value

class ValidatedModel:
    """Base class với validation fields"""
    
    def __init__(self, **kwargs):
        for name, field in self.__class__.__dict__.items():
            if isinstance(field, ValidatedField):
                setattr(self, name, kwargs.get(name))
    
    def validate(self):
        """Validate tất cả fields"""
        for name, field in self.__class__.__dict__.items():
            if isinstance(field, ValidatedField):
                getattr(self, name)  # Trigger validation

class User(ValidatedModel):
    username = ValidatedField(
        Required("Username is required"),
        MinLength(3, "Username must be at least 3 characters"),
        MaxLength(20, "Username must be at most 20 characters")
    )
    
    email = ValidatedField(
        Required("Email is required"),
        Email("Please enter a valid email")
    )
    
    age = ValidatedField(
        Required("Age is required"),
        Range(18, 120, "Age must be between 18 and 120")
    )

class Product(ValidatedModel):
    name = ValidatedField(
        Required("Product name is required"),
        MinLength(2, "Product name must be at least 2 characters")
    )
    
    price = ValidatedField(
        Required("Price is required"),
        Range(0.01, 9999.99, "Price must be between 0.01 and 9999.99")
    )
    
    quantity = ValidatedField(
        Range(0, 1000, "Quantity must be between 0 and 1000")
    )

# Demo Validation Framework
print("=== TESTING VALIDATION FRAMEWORK ===")

def test_valid_user():
    try:
        user = User(username="john_doe", email="john@example.com", age=25)
        print(f"✅ Valid user: {user.username}, {user.email}, {user.age}")
    except ValidationError as e:
        print(f"❌ {e}")

def test_invalid_user():
    try:
        user = User(username="j", email="notemail", age=15)
        print(f"User created: {user.username}")  # Sẽ không chạy
    except ValidationError as e:
        print(f"❌ Validation failed: {e}")

def test_incomplete_user():
    try:
        user = User(username="john_doe")
        # Thiếu email và age
        user.validate()  # Force validation
    except ValidationError as e:
        print(f"❌ Incomplete user: {e}")

def test_valid_product():
    try:
        product = Product(name="Laptop", price=999.99, quantity=10)
        print(f"✅ Valid product: {product.name}, ${product.price}, qty: {product.quantity}")
    except ValidationError as e:
        print(f"❌ {e}")

def test_invalid_product():
    try:
        product = Product(name="A", price=10000, quantity=2000)
    except ValidationError as e:
        print(f"❌ Product validation failed: {e}")

# Run tests
test_valid_user()
test_invalid_user()
test_incomplete_user()
test_valid_product()
test_invalid_product()
```

---

## 🎯 BÀI TẬP VỀ NHÀ BUỔI 2

### Bài 1: Cache Descriptor
Tạo descriptor `@cached_property`:
- Cache kết quả sau lần tính đầu tiên
- Có method để invalidate cache
- Hỗ trợ timeout (tự động recache sau N giây)

### Bài 2: Metaclass cho API Client
Tạo metaclass tự động tạo API methods:
```python
class APIClient(metaclass=APIMeta):
    base_url = "https://api.example.com"
    
    # Tự động tạo method GET/POST/PUT/DELETE
    users = Resource("/users")
    products = Resource("/products")
```

### Bài 3: Validation với Context
Tạo validation system với:
- Conditional validation (required if field X is set)
- Cross-field validation (field A < field B)
- Custom error messages

---

## 📌 TỔNG KẾT BUỔI 2

**Bạn đã học được:**
1. ✅ Descriptor Protocol (`__get__`, `__set__`, `__delete__`)
2. ✅ Data vs Non-Data Descriptor
3. ✅ Property advanced techniques
4. ✅ Metaclass và ứng dụng thực tế
5. ✅ Xây dựng Validation Framework

**Key Takeaways:**
- **Descriptors** là cốt lõi của Python properties
- **Metaclass** cho phép can thiệp vào quá trình tạo class
- **Property** là cách Pythonic để kiểm soát attribute access
- **Đừng lạm dụng metaclass** - chỉ dùng khi thực sự cần
- **Composition > Inheritance** trong nhiều trường hợp

---

**Chuẩn bị cho Buổi 3:** Chúng ta sẽ học về **Advanced Patterns, Mixins, và Design Patterns** trong Python!

Có gì thắc mắc không? Hãy thực hành code và đặt câu hỏi! 💪🐍