# 🚀 BUỔI 1: OOP PYTHON - TỪ CƠ BẢN ĐẾN CHUYÊN SÂU

Chào mừng bạn đến với buổi học đầu tiên! Hôm nay chúng ta sẽ **xây dựng nền tảng vững chắc** và hiểu **bản chất thực sự** của OOP trong Python.

---

## 📚 MỤC TIÊU BUỔI 1

1. Hiểu **object model** của Python
2. Nắm vững **4 trụ cột** của OOP
3. Thành thạo **Magic Methods** cơ bản
4. Xây dựng **project thực tế** đầu tiên

---

## 🎯 PHẦN 1: PYTHON OBJECT MODEL - NỀN TẢNG

### 1.1. Mọi thứ đều là Object

```python
# Mở Python interpreter và chạy thử
print("=== MỌI THỨ ĐỀU LÀ OBJECT ===")

# 1. Số nguyên là object
x = 5
print(f"x = {x}, type = {type(x)}")
print(f"Các method của int: {dir(x)[:5]}...")

# 2. Hàm là object
def hello(name):
    return f"Hello {name}"

print(f"hello là {type(hello)}")
# Gán hàm vào biến khác
greet = hello
print(greet("John"))  # Hello John

# 3. Class cũng là object
class MyClass:
    pass

print(f"MyClass là {type(MyClass)}")  # <class 'type'>
print(f"Instance của MyClass: {type(MyClass())}")  # <class '__main__.MyClass'>
```

### 1.2. Identity, Type, Value

```python
print("\n=== IDENTITY, TYPE, VALUE ===")

# Mỗi object có 3 thuộc tính
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(f"a == b: {a == b}")        # True (so sánh value)
print(f"a is b: {a is b}")        # False (so sánh identity)
print(f"a is c: {a is c}")        # True (cùng object)
print(f"id(a): {id(a)}")          # Địa chỉ bộ nhớ
print(f"id(b): {id(b)}")          # Khác với id(a)
print(f"id(c): {id(c)}")          # Bằng với id(a)

# Immutable objects
x = 10
y = 10
print(f"x is y: {x is y}")  # True (Python cache small ints)

# Mutable objects
list1 = [1, 2]
list2 = [1, 2]
print(f"list1 is list2: {list1 is list2}")  # False
```

### 1.3. Mutable vs Immutable

```python
print("\n=== MUTABLE VS IMMUTABLE ===")

# Immutable: int, float, string, tuple, frozenset
s = "hello"
print(f"s id before: {id(s)}")
s += " world"  # Tạo object mới
print(f"s id after: {id(s)}")

# Mutable: list, dict, set, custom objects
lst = [1, 2, 3]
print(f"lst id before: {id(lst)}")
lst.append(4)  # Modify object hiện tại
print(f"lst id after: {id(lst)}")  # Giữ nguyên id

# Hậu quả khi truyền vào hàm
def modify_list(lst):
    lst.append(99)
    print(f"Inside function: {lst}, id: {id(lst)}")

my_list = [1, 2, 3]
modify_list(my_list)
print(f"Outside function: {my_list}")  # Bị thay đổi!

# Cách tránh: copy
def safe_modify(lst):
    new_lst = lst.copy()
    new_lst.append(99)
    return new_lst

original = [1, 2, 3]
new = safe_modify(original)
print(f"Original: {original}")
print(f"New: {new}")
```

---

## 🏗️ PHẦN 2: 4 TRỤ CỘT CỦA OOP

### 2.1. Encapsulation (Đóng gói)

```python
print("\n=== ENCAPSULATION ===")

class BankAccount:
    """Ví dụ về đóng gói - ẩn chi tiết bên trong"""
    
    def __init__(self, owner, initial_balance=0):
        self.owner = owner                    # Public
        self._balance = initial_balance      # Protected (convention)
        self.__transaction_history = []      # Private (name mangling)
        self._log(f"Account created with {initial_balance}")
    
    # Public method - interface
    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self._balance += amount
        self.__transaction_history.append(f"+{amount}")
        self._log(f"Deposited {amount}")
        return self._balance
    
    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount
        self.__transaction_history.append(f"-{amount}")
        self._log(f"Withdrew {amount}")
        return self._balance
    
    # Property - controlled access
    @property
    def balance(self):
        """Read-only balance"""
        return self._balance
    
    @property
    def history(self):
        """Return copy của history để không bị sửa đổi"""
        return self.__transaction_history.copy()
    
    # Private method
    def _log(self, message):
        """Logging - chỉ dùng nội bộ"""
        from datetime import datetime
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.owner}: {message}")
    
    # Special method để biểu diễn
    def __str__(self):
        return f"Account({self.owner}, balance={self._balance})"
    
    def __repr__(self):
        return f"BankAccount('{self.owner}', {self._balance})"

# Sử dụng
acc = BankAccount("John", 1000)
print(acc.balance)        # 1000 - access qua property
acc.deposit(500)
acc.withdraw(200)

# Private không thể truy cập trực tiếp
# print(acc.__transaction_history)  # AttributeError!

# Nhưng vẫn có thể truy cập qua name mangling (không nên làm)
print(acc._BankAccount__transaction_history)  # Không khuyến khích

# Protected cũng có thể truy cập nhưng là convention
print(acc._balance)  # Có thể nhưng không nên
```

### 2.2. Inheritance (Kế thừa)

```python
print("\n=== INHERITANCE ===")

class Vehicle:
    """Base class"""
    
    def __init__(self, brand, model, year):
        self.brand = brand
        self.model = model
        self.year = year
        self._mileage = 0
    
    def start(self):
        return f"{self.brand} {self.model} is starting..."
    
    def stop(self):
        return f"{self.brand} {self.model} is stopping..."
    
    def drive(self, km):
        self._mileage += km
        return f"Driving {km} km"
    
    @property
    def mileage(self):
        return self._mileage
    
    def __str__(self):
        return f"{self.year} {self.brand} {self.model}"

class Car(Vehicle):
    """Subclass - kế thừa từ Vehicle"""
    
    def __init__(self, brand, model, year, doors=4):
        super().__init__(brand, model, year)  # Gọi __init__ của parent
        self.doors = doors
        self._is_convertible = False
    
    # Override method
    def start(self):
        # Gọi method của parent và thêm behavior
        parent_start = super().start()
        return f"{parent_start} Vroom vroom! 🚗"
    
    # Thêm method mới
    def honk(self):
        return "Beep beep!"
    
    def toggle_convertible(self):
        self._is_convertible = not self._is_convertible
        return f"Convertible: {self._is_convertible}"

class ElectricCar(Car):
    """Kế thừa nhiều cấp"""
    
    def __init__(self, brand, model, year, battery_capacity):
        super().__init__(brand, model, year)
        self.battery_capacity = battery_capacity
        self._charge_level = 100
    
    # Override
    def start(self):
        return f"{self.brand} {self.model} is starting silently... ⚡"
    
    # Thêm method mới
    def charge(self, amount):
        self._charge_level = min(100, self._charge_level + amount)
        return f"Charging... Battery now at {self._charge_level}%"
    
    def drive(self, km):
        # Sử dụng super() để gọi method của parent
        result = super().drive(km)
        self._charge_level -= km * 0.5  # Mỗi km tốn 0.5% pin
        return f"{result}, battery at {self._charge_level}%"

class Motorcycle(Vehicle):
    """Subclass khác của Vehicle"""
    
    def __init__(self, brand, model, year, has_sidecar=False):
        super().__init__(brand, model, year)
        self.has_sidecar = has_sidecar
    
    def start(self):
        return f"{self.brand} {self.model} is starting... Vroom! 🏍️"
    
    def wheelie(self):
        return "Doing a wheelie! 🛵"

# Demo
print("=== DEMO INHERITANCE ===")
car = Car("Toyota", "Camry", 2022, 4)
ev = ElectricCar("Tesla", "Model 3", 2023, 75)
bike = Motorcycle("Harley", "Davidson", 2021)

print(car.start())          # Toyota Camry is starting... Vroom vroom! 🚗
print(ev.start())           # Tesla Model 3 is starting silently... ⚡
print(bike.start())         # Harley Davidson is starting... Vroom! 🏍️

print(car.honk())           # Beep beep!
print(bike.wheelie())       # Doing a wheelie! 🛵

print(ev.drive(50))         # Driving 50 km, battery at 75.0%
print(ev.charge(20))        # Charging... Battery now at 95%

# Kiểm tra inheritance
print(f"Is car a Vehicle? {isinstance(car, Vehicle)}")        # True
print(f"Is ev a Car? {isinstance(ev, Car)}")                  # True
print(f"Is ev a Vehicle? {isinstance(ev, Vehicle)}")          # True
print(f"Is bike a Car? {isinstance(bike, Car)}")              # False
print(f"Is Car subclass of Vehicle? {issubclass(Car, Vehicle)}")  # True
```

### 2.3. Polymorphism (Đa hình)

```python
print("\n=== POLYMORPHISM ===")

# Interface chung cho các loại động vật
class Animal:
    def make_sound(self):
        raise NotImplementedError("Subclass must implement this")
    
    def move(self):
        raise NotImplementedError("Subclass must implement this")

class Dog(Animal):
    def make_sound(self):
        return "Woof! 🐕"
    
    def move(self):
        return "Running on four legs"
    
    def fetch(self):
        return "Fetching the ball!"

class Cat(Animal):
    def make_sound(self):
        return "Meow! 🐱"
    
    def move(self):
        return "Walking gracefully"
    
    def purr(self):
        return "Purr purr..."

class Duck(Animal):
    def make_sound(self):
        return "Quack quack! 🦆"
    
    def move(self):
        return "Swimming in the pond"
    
    def swim(self):
        return "Swimming fast!"

# Hàm đa hình - hoạt động với bất kỳ Animal nào
def animal_show(animal):
    """Hàm này không cần biết loại animal cụ thể"""
    print(f"Sound: {animal.make_sound()}")
    print(f"Move: {animal.move()}")
    print("-" * 30)

# Demo
animals = [Dog(), Cat(), Duck()]
for animal in animals:
    animal_show(animal)

# Duck typing - "Nếu nó đi như vịt và kêu như vịt..."
def make_it_sound(thing):
    """Không cần kiểm tra type, chỉ cần có method make_sound"""
    if hasattr(thing, 'make_sound'):
        print(thing.make_sound())
    else:
        print(f"{thing} can't make sound")

class Robot:
    def make_sound(self):
        return "Beep boop! 🤖"

make_it_sound(Dog())     # Woof! 🐕
make_it_sound(Robot())   # Beep boop! 🤖
make_it_sound(42)        # 42 can't make sound

# Polymorphism với + operator
print(1 + 2)              # 3 - int
print("Hello " + "World") # Hello World - string
print([1] + [2])          # [1, 2] - list
```

### 2.4. Abstraction (Trừu tượng)

```python
print("\n=== ABSTRACTION ===")

from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    """Abstract class - định nghĩa interface thanh toán"""
    
    @abstractmethod
    def process_payment(self, amount):
        """Xử lý thanh toán - bắt buộc phải implement"""
        pass
    
    @abstractmethod
    def refund(self, transaction_id):
        """Hoàn tiền - bắt buộc phải implement"""
        pass
    
    def validate_card(self, card_number):
        """Method có sẵn - không cần override"""
        # Logic validation chung
        return len(str(card_number)) == 16

class CreditCardProcessor(PaymentProcessor):
    """Implement cụ thể cho Credit Card"""
    
    def process_payment(self, amount):
        print(f"Processing credit card payment of ${amount}")
        # Logic xử lý credit card
        return {"status": "success", "id": "CC_12345"}
    
    def refund(self, transaction_id):
        print(f"Refunding credit card transaction {transaction_id}")
        return {"status": "refunded"}

class PayPalProcessor(PaymentProcessor):
    """Implement cụ thể cho PayPal"""
    
    def process_payment(self, amount):
        print(f"Processing PayPal payment of ${amount}")
        # Logic xử lý PayPal
        return {"status": "success", "id": "PP_67890"}
    
    def refund(self, transaction_id):
        print(f"Refunding PayPal transaction {transaction_id}")
        return {"status": "refunded"}

class CryptoProcessor(PaymentProcessor):
    """Implement cụ thể cho Cryptocurrency"""
    
    def process_payment(self, amount):
        print(f"Processing Crypto payment of ${amount}")
        return {"status": "success", "id": "CRYPTO_111"}
    
    def refund(self, transaction_id):
        print(f"Refunding Crypto transaction {transaction_id}")
        return {"status": "refunded"}

# Function sử dụng abstraction
def checkout(processor: PaymentProcessor, amount: float):
    """Không cần biết loại processor cụ thể"""
    result = processor.process_payment(amount)
    print(f"Payment result: {result}")
    
    # Test validation (đã có sẵn)
    print(f"Card valid: {processor.validate_card("1234567890123456")}")

# Demo
print("=== PAYMENT SYSTEM ===")
cc_processor = CreditCardProcessor()
paypal_processor = PayPalProcessor()
crypto_processor = CryptoProcessor()

checkout(cc_processor, 99.99)
checkout(paypal_processor, 49.50)
checkout(crypto_processor, 1000.00)

# Không thể khởi tạo abstract class
# processor = PaymentProcessor()  # TypeError!
```

---

## ✨ PHẦN 3: MAGIC METHODS CƠ BẢN

### 3.1. Khởi tạo và Biểu diễn

```python
print("\n=== MAGIC METHODS - INIT & REPRESENTATION ===")

class Book:
    def __init__(self, title, author, pages):
        """Constructor - được gọi khi tạo object"""
        self.title = title
        self.author = author
        self.pages = pages
        print(f"Book '{title}' created")
    
    def __str__(self):
        """String representation - cho người dùng"""
        return f"'{self.title}' by {self.author} ({self.pages} pages)"
    
    def __repr__(self):
        """Developer representation - cho debugging"""
        return f"Book(title='{self.title}', author='{self.author}', pages={self.pages})"
    
    def __del__(self):
        """Destructor - khi object bị xóa"""
        print(f"Book '{self.title}' destroyed")

# Sử dụng
book = Book("Python Programming", "John Doe", 500)
print(str(book))    # 'Python Programming' by John Doe (500 pages)
print(repr(book))   # Book(title='Python Programming', author='John Doe', pages=500)

# Trong interactive console
# book -> sẽ hiển thị repr
```

### 3.2. So sánh và Toán tử

```python
print("\n=== COMPARISON & OPERATOR MAGIC METHODS ===")

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        """Phép cộng +"""
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        return NotImplemented
    
    def __sub__(self, other):
        """Phép trừ -"""
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        return NotImplemented
    
    def __mul__(self, scalar):
        """Phép nhân *"""
        if isinstance(scalar, (int, float)):
            return Point(self.x * scalar, self.y * scalar)
        return NotImplemented
    
    def __rmul__(self, scalar):
        """scalar * point - khi operand bên trái không hỗ trợ"""
        return self.__mul__(scalar)
    
    def __eq__(self, other):
        """So sánh bằng =="""
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y
    
    def __lt__(self, other):
        """So sánh nhỏ hơn <"""
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x**2 + self.y**2) < (other.x**2 + other.y**2)
    
    def __le__(self, other):
        """So sánh nhỏ hơn hoặc bằng <="""
        return self < other or self == other
    
    def __len__(self):
        """Độ dài - trả về số chiều"""
        return 2
    
    def __getitem__(self, index):
        """Truy cập bằng []"""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("Point only has 2 dimensions")
    
    def __iter__(self):
        """Iterable - cho phép for loop"""
        yield self.x
        yield self.y
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"

# Demo
p1 = Point(1, 2)
p2 = Point(3, 4)
p3 = Point(1, 2)

print(f"p1 + p2 = {p1 + p2}")        # Point(4, 6)
print(f"p2 - p1 = {p2 - p1}")        # Point(2, 2)
print(f"p1 * 3 = {p1 * 3}")          # Point(3, 6)
print(f"3 * p1 = {3 * p1}")          # Point(3, 6)
print(f"p1 == p3: {p1 == p3}")       # True
print(f"p1 < p2: {p1 < p2}")         # True (5 < 25)
print(f"p1[0] = {p1[0]}, p1[1] = {p1[1]}")  # 1, 2
print(f"len(p1) = {len(p1)}")         # 2

# Iteration
for coord in p1:
    print(f"Coordinate: {coord}")
```

### 3.3. Container và Callable

```python
print("\n=== CONTAINER & CALLABLE MAGIC METHODS ===")

class ShoppingCart:
    def __init__(self):
        self._items = {}
        self._total = 0
    
    def add_item(self, name, price, quantity=1):
        """Thêm item vào cart"""
        if name in self._items:
            self._items[name]['quantity'] += quantity
        else:
            self._items[name] = {'price': price, 'quantity': quantity}
        self._total += price * quantity
    
    def __getitem__(self, name):
        """Truy cập item: cart['item_name']"""
        return self._items.get(name, None)
    
    def __setitem__(self, name, price):
        """Thêm item bằng syntax cart['item'] = price"""
        self.add_item(name, price)
    
    def __delitem__(self, name):
        """Xóa item: del cart['item']"""
        if name in self._items:
            item = self._items[name]
            self._total -= item['price'] * item['quantity']
            del self._items[name]
    
    def __contains__(self, name):
        """Kiểm tra item có trong cart không: 'item' in cart"""
        return name in self._items
    
    def __len__(self):
        """Số lượng item khác nhau trong cart"""
        return len(self._items)
    
    def __iter__(self):
        """Iterator - for item in cart"""
        return iter(self._items)
    
    def __call__(self, discount=0):
        """Gọi object như hàm: cart(10%) -> tính tổng với discount"""
        if discount:
            return self._total * (1 - discount/100)
        return self._total
    
    def __add__(self, other):
        """Gộp 2 cart lại: cart1 + cart2"""
        new_cart = ShoppingCart()
        for name, details in self._items.items():
            new_cart.add_item(name, details['price'], details['quantity'])
        for name, details in other._items.items():
            new_cart.add_item(name, details['price'], details['quantity'])
        return new_cart
    
    def __str__(self):
        if not self._items:
            return "Empty cart"
        result = "Shopping Cart:\n"
        for name, details in self._items.items():
            result += f"  {name}: ${details['price']} x {details['quantity']}\n"
        result += f"Total: ${self._total}"
        return result

# Demo
cart = ShoppingCart()
cart['Apple'] = 0.99
cart['Banana'] = 0.59
cart.add_item('Orange', 0.79, 3)

print(cart)
print(f"Total with 10% discount: ${cart(10):.2f}")
print(f"Apple in cart? {'Apple' in cart}")
print(f"Grape in cart? {'Grape' in cart}")
print(f"Number of items: {len(cart)}")

# Iterate
for item in cart:
    print(f"Item: {item}")

# Combine carts
cart2 = ShoppingCart()
cart2['Milk'] = 2.99
cart2['Bread'] = 1.99

combined = cart + cart2
print(combined)
```

---

## 🏗️ PHẦN 4: PROJECT THỰC TẾ - HỆ THỐNG QUẢN LÝ THƯ VIỆN

```python
print("\n=== PROJECT: LIBRARY MANAGEMENT SYSTEM ===")
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

class LibraryItem(ABC):
    """Abstract class cho tất cả items trong thư viện"""
    
    def __init__(self, title: str, author: str, year: int):
        self.id = str(uuid.uuid4())[:8]
        self.title = title
        self.author = author
        self.year = year
        self.is_checked_out = False
        self.due_date = None
        self.checkout_history = []
    
    @abstractmethod
    def get_type(self) -> str:
        """Trả về loại item"""
        pass
    
    def check_out(self, days: int = 14):
        """Mượn item"""
        if self.is_checked_out:
            raise ValueError(f"'{self.title}' is already checked out")
        self.is_checked_out = True
        self.due_date = datetime.now() + timedelta(days=days)
        self.checkout_history.append({
            'date': datetime.now(),
            'due': self.due_date
        })
        return f"Checked out '{self.title}' until {self.due_date.strftime('%Y-%m-%d')}"
    
    def return_item(self):
        """Trả item"""
        if not self.is_checked_out:
            raise ValueError(f"'{self.title}' is not checked out")
        self.is_checked_out = False
        self.due_date = None
        return f"Returned '{self.title}'"
    
    def __str__(self):
        status = "Available" if not self.is_checked_out else f"Due: {self.due_date.strftime('%Y-%m-%d')}"
        return f"{self.get_type()}: {self.title} by {self.author} ({self.year}) - {status}"

class Book(LibraryItem):
    def __init__(self, title: str, author: str, year: int, pages: int, genre: str):
        super().__init__(title, author, year)
        self.pages = pages
        self.genre = genre
    
    def get_type(self) -> str:
        return "Book"

class Magazine(LibraryItem):
    def __init__(self, title: str, author: str, year: int, issue: int, publisher: str):
        super().__init__(title, author, year)
        self.issue = issue
        self.publisher = publisher
    
    def get_type(self) -> str:
        return "Magazine"

class DVD(LibraryItem):
    def __init__(self, title: str, author: str, year: int, duration: int, director: str):
        super().__init__(title, author, year)
        self.duration = duration
        self.director = director
    
    def get_type(self) -> str:
        return "DVD"

class Library:
    """Hệ thống quản lý thư viện chính"""
    
    def __init__(self, name: str):
        self.name = name
        self.items: List[LibraryItem] = []
        self.members = {}
        self._log(f"Library '{name}' created")
    
    def _log(self, message: str):
        """Logging nội bộ"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def add_item(self, item: LibraryItem):
        """Thêm item vào thư viện"""
        self.items.append(item)
        self._log(f"Added {item.get_type()}: {item.title}")
    
    def remove_item(self, item_id: str):
        """Xóa item khỏi thư viện"""
        for i, item in enumerate(self.items):
            if item.id == item_id:
                if item.is_checked_out:
                    raise ValueError(f"Cannot remove '{item.title}' - it's checked out")
                removed = self.items.pop(i)
                self._log(f"Removed {removed.get_type()}: {removed.title}")
                return removed
        raise ValueError(f"Item with ID {item_id} not found")
    
    def search(self, query: str) -> List[LibraryItem]:
        """Tìm kiếm items theo title hoặc author"""
        query = query.lower()
        results = [
            item for item in self.items
            if query in item.title.lower() or query in item.author.lower()
        ]
        self._log(f"Found {len(results)} items for '{query}'")
        return results
    
    def get_available(self) -> List[LibraryItem]:
        """Lấy danh sách items đang có sẵn"""
        return [item for item in self.items if not item.is_checked_out]
    
    def get_overdue(self) -> List[LibraryItem]:
        """Lấy danh sách items quá hạn"""
        now = datetime.now()
        return [item for item in self.items if item.is_checked_out and item.due_date < now]
    
    def __len__(self):
        return len(self.items)
    
    def __iter__(self):
        return iter(self.items)
    
    def __str__(self):
        total = len(self.items)
        available = len(self.get_available())
        overdue = len(self.get_overdue())
        return f"""
📚 {self.name}
━━━━━━━━━━━━━━━━━━━━━━━
Total items: {total}
Available: {available}
Overdue: {overdue}
        """.strip()

# Demo hệ thống
print("=== RUNNING LIBRARY SYSTEM ===")

# Tạo thư viện
library = Library("Knowledge Hub")

# Thêm sách
library.add_item(Book("Clean Code", "Robert Martin", 2008, 464, "Programming"))
library.add_item(Book("Python Crash Course", "Eric Matthes", 2019, 544, "Programming"))
library.add_item(Book("The Hobbit", "J.R.R. Tolkien", 1937, 310, "Fantasy"))
library.add_item(Magazine("National Geographic", "Various", 2023, 125, "NG Media"))
library.add_item(DVD("Inception", "Christopher Nolan", 2010, 148, "Christopher Nolan"))

print(library)
print()

# Tìm kiếm
print("=== SEARCH RESULTS ===")
results = library.search("Python")
for item in results:
    print(f"  {item}")

print()

# Mượn sách
print("=== CHECK OUT ===")
book = library.items[1]  # Python Crash Course
print(book.check_out(14))
print(book)
print()

# Xem trạng thái
print("=== LIBRARY STATUS ===")
print(library)
print()

# Mượn thêm
print("=== CHECK OUT MORE ===")
hobbit = library.items[2]
print(hobbit.check_out(7))
print()

# Kiểm tra overdue
print("=== OVERDUE ITEMS ===")
overdue = library.get_overdue()
print(f"Overdue items: {len(overdue)}")
for item in overdue:
    print(f"  {item.title} - due: {item.due_date.strftime('%Y-%m-%d')}")

print()

# Trả sách
print("=== RETURN ITEM ===")
print(hobbit.return_item())
print(f"'{hobbit.title}' is now available")
```

---

## 🎯 BÀI TẬP VỀ NHÀ BUỔI 1

### Bài 1: Xây dựng lớp `Fraction`
Tạo lớp phân số với:
- Numerator (tử số) và denominator (mẫu số)
- Tự động rút gọn phân số
- Hỗ trợ các phép toán +, -, *, /
- So sánh ==, <, >
- Chuyển sang float

### Bài 2: Hệ thống quản lý nhân viên
Xây dựng class hierarchy:
- `Employee` (abstract): name, id, salary, abstract method `calculate_bonus()`
- `Manager` extends Employee: có team_size, bonus = salary * 0.2
- `Developer` extends Employee: có programming_languages, bonus = salary * 0.1
- `Intern` extends Employee: có mentor, bonus = fixed 100

### Bài 3: Tạo Decorator cho OOP
Viết decorator `@timer` để đo thời gian chạy của method

---

## 📌 TỔNG KẾT BUỔI 1

**Bạn đã học được:**
1. ✅ Python Object Model - mọi thứ đều là object
2. ✅ 4 trụ cột của OOP (Encapsulation, Inheritance, Polymorphism, Abstraction)
3. ✅ Magic Methods cơ bản (__init__, __str__, __repr__, các toán tử)
4. ✅ Xây dựng project thực tế

**Key Takeaways:**
- `is` vs `==` - hiểu rõ identity vs equality
- Mutable vs Immutable - ảnh hưởng đến behavior
- `super()` quan trọng trong inheritance
- ABC giúp tạo interface rõ ràng
- Magic methods làm cho class "Pythonic"

---

**Chuẩn bị cho Buổi 2:** Chúng ta sẽ học về **Descriptors, Properties và Metaclass** - những thứ làm nên sức mạnh của OOP Python!

Bạn có thắc mắc gì không? Hãy thử code và đặt câu hỏi! 💪