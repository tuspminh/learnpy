# 🚀 BUỔI 3: OOP PYTHON - ADVANCED PATTERNS, MIXINS & DESIGN PATTERNS

Chào mừng đến buổi 3! Hôm nay chúng ta sẽ **nâng tầm OOP** với các pattern thiết kế chuyên nghiệp và kỹ thuật mixin mạnh mẽ.

---

## 📚 MỤC TIÊU BUỔI 3

1. Thành thạo **Mixin Pattern** và **Multiple Inheritance**
2. Nắm vững các **Design Patterns** quan trọng trong Python
3. Hiểu và áp dụng **Composition vs Inheritance**
4. Xây dựng **Event System** và **Plugin Architecture**

---

## 🧩 PHẦN 1: MIXIN PATTERN

### 1.1. Mixin là gì?

Mixin là class cung cấp functionality cụ thể, không đứng độc lập mà được "pha trộn" vào các class khác.

```python
print("=== MIXIN PATTERN ===")

# Mixin cơ bản
class JSONMixin:
    """Mixin cung cấp khả năng chuyển đổi sang JSON"""
    
    def to_json(self):
        import json
        return json.dumps(self.__dict__)
    
    def from_json(self, json_str):
        import json
        data = json.loads(json_str)
        for key, value in data.items():
            setattr(self, key, value)
        return self

class CSVExportMixin:
    """Mixin cung cấp khả năng export CSV"""
    
    def to_csv(self, headers=None):
        if headers is None:
            headers = list(self.__dict__.keys())
        values = [str(getattr(self, h, '')) for h in headers]
        return ','.join(values)

class LoggingMixin:
    """Mixin cung cấp logging"""
    
    def log(self, message, level="INFO"):
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def info(self, message):
        self.log(message, "INFO")
    
    def error(self, message):
        self.log(message, "ERROR")

# Sử dụng Mixin
class User(JSONMixin, CSVExportMixin, LoggingMixin):
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age
        self.info(f"User created: {name}")

class Product(JSONMixin, CSVExportMixin, LoggingMixin):
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock
        self.info(f"Product created: {name}")

# Demo
user = User("John Doe", "john@example.com", 30)
print("User JSON:", user.to_json())
print("User CSV:", user.to_csv())
print()

product = Product("Laptop", 999.99, 10)
print("Product JSON:", product.to_json())
print("Product CSV:", product.to_csv())
```

### 1.2. Mixin với Abstract Methods

```python
print("\n=== MIXIN WITH ABSTRACT METHODS ===")

from abc import ABC, abstractmethod

class ValidatableMixin(ABC):
    """Mixin yêu cầu class con implement validation"""
    
    @abstractmethod
    def validate(self):
        """Phải được implement bởi class con"""
        pass
    
    def validate_and_save(self):
        """Sử dụng validate method"""
        errors = self.validate()
        if errors:
            raise ValueError(f"Validation failed: {errors}")
        self.save()
    
    def save(self):
        """Có thể override"""
        print(f"Saving {self.__class__.__name__}...")

class TimestampMixin:
    """Mixin thêm timestamp"""
    
    def __init__(self, *args, **kwargs):
        from datetime import datetime
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        super().__init__(*args, **kwargs)  # Quan trọng!
    
    def update_timestamp(self):
        from datetime import datetime
        self.updated_at = datetime.now()

class SerializeMixin:
    """Mixin serialization"""
    
    def to_dict(self):
        return {
            k: v for k, v in self.__dict__.items() 
            if not k.startswith('_')
        }
    
    def to_dict_with_timestamps(self):
        data = self.to_dict()
        if hasattr(self, 'created_at'):
            data['created_at'] = self.created_at.isoformat()
        if hasattr(self, 'updated_at'):
            data['updated_at'] = self.updated_at.isoformat()
        return data

class User(ValidatableMixin, TimestampMixin, SerializeMixin):
    def __init__(self, name, email, age):
        super().__init__()  # Gọi TimestampMixin
        self.name = name
        self.email = email
        self.age = age
    
    def validate(self):
        errors = []
        if not self.name or len(self.name) < 2:
            errors.append("Name must be at least 2 characters")
        if '@' not in self.email:
            errors.append("Invalid email")
        if not (0 <= self.age <= 150):
            errors.append("Invalid age")
        return errors

# Demo
user = User("John", "john@example.com", 30)
print("User dict:", user.to_dict_with_timestamps())
print("Validating...", user.validate())
user.validate_and_save()
print()

try:
    invalid_user = User("J", "invalid-email", 200)
    invalid_user.validate_and_save()
except ValueError as e:
    print(f"Validation error: {e}")
```

### 1.3. Mixin với Context Manager

```python
print("\n=== MIXIN CONTEXT MANAGER ===")

class ContextMixin:
    """Mixin cho phép object được dùng trong with statement"""
    
    def __enter__(self):
        print(f"Entering context: {self.__class__.__name__}")
        self._enter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Exiting context: {self.__class__.__name__}")
        self._exit()
        if exc_type:
            print(f"Exception: {exc_type.__name__}: {exc_val}")
        return False
    
    def _enter(self):
        """Override để thêm logic khi enter"""
        pass
    
    def _exit(self):
        """Override để thêm logic khi exit"""
        pass

class TransactionMixin:
    """Mixin cho transaction management"""
    
    def begin_transaction(self):
        print("BEGIN TRANSACTION")
        self._transaction_active = True
    
    def commit(self):
        if hasattr(self, '_transaction_active') and self._transaction_active:
            print("COMMIT")
            self._transaction_active = False
    
    def rollback(self):
        if hasattr(self, '_transaction_active') and self._transaction_active:
            print("ROLLBACK")
            self._transaction_active = False

class DatabaseConnection(ContextMixin, TransactionMixin):
    def __init__(self, db_name):
        self.db_name = db_name
        self._transaction_active = False
    
    def _enter(self):
        print(f"Connecting to {self.db_name}")
        self.begin_transaction()
    
    def _exit(self):
        self.commit()
        print(f"Disconnecting from {self.db_name}")
    
    def query(self, sql):
        print(f"Executing: {sql}")

# Demo
with DatabaseConnection("users.db") as db:
    db.query("SELECT * FROM users")
    db.query("UPDATE users SET active = true")
    # Tự động commit khi exit
```

---

## 🎨 PHẦN 2: DESIGN PATTERNS TRONG PYTHON

### 2.1. Factory Pattern

```python
print("\n=== FACTORY PATTERN ===")

from abc import ABC, abstractmethod

# Product interface
class Button(ABC):
    @abstractmethod
    def render(self):
        pass

class Checkbox(ABC):
    @abstractmethod
    def render(self):
        pass

# Concrete Products - Windows
class WindowsButton(Button):
    def render(self):
        return "Windows Button [  OK  ]"

class WindowsCheckbox(Checkbox):
    def render(self):
        return "Windows Checkbox [✓]"

# Concrete Products - Mac
class MacButton(Button):
    def render(self):
        return "Mac Button [  OK  ]"

class MacCheckbox(Checkbox):
    def render(self):
        return "Mac Checkbox [✓]"

# Abstract Factory
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self):
        pass
    
    @abstractmethod
    def create_checkbox(self):
        pass

# Concrete Factories
class WindowsFactory(GUIFactory):
    def create_button(self):
        return WindowsButton()
    
    def create_checkbox(self):
        return WindowsCheckbox()

class MacFactory(GUIFactory):
    def create_button(self):
        return MacButton()
    
    def create_checkbox(self):
        return MacCheckbox()

# Client code
class Application:
    def __init__(self, factory: GUIFactory):
        self.factory = factory
        self.button = factory.create_button()
        self.checkbox = factory.create_checkbox()
    
    def render(self):
        print(f"Rendering: {self.button.render()}")
        print(f"Rendering: {self.checkbox.render()}")

# Factory Method Pattern (Simple Factory)
class LoggerFactory:
    @staticmethod
    def get_logger(logger_type="console"):
        if logger_type == "console":
            return ConsoleLogger()
        elif logger_type == "file":
            return FileLogger()
        elif logger_type == "database":
            return DatabaseLogger()
        else:
            raise ValueError(f"Unknown logger type: {logger_type}")

class Logger(ABC):
    @abstractmethod
    def log(self, message):
        pass

class ConsoleLogger(Logger):
    def log(self, message):
        print(f"[CONSOLE] {message}")

class FileLogger(Logger):
    def log(self, message):
        with open("app.log", "a") as f:
            f.write(f"[FILE] {message}\n")
        print(f"[FILE] Logged: {message}")

class DatabaseLogger(Logger):
    def log(self, message):
        # Giả lập log vào database
        print(f"[DB] Logged: {message}")

# Demo
print("--- Abstract Factory ---")
app = Application(WindowsFactory())
app.render()
print()

app_mac = Application(MacFactory())
app_mac.render()

print("\n--- Factory Method ---")
logger = LoggerFactory.get_logger("console")
logger.log("Console message")

logger = LoggerFactory.get_logger("file")
logger.log("File message")
```

### 2.2. Builder Pattern (Nâng cao)

```python
print("\n=== BUILDER PATTERN ===")

class Pizza:
    """Product - Pizza với nhiều thành phần tùy chọn"""
    
    def __init__(self):
        self.size = None
        self.crust = None
        self.sauce = None
        self.cheese = False
        self.pepperoni = False
        self.mushrooms = False
        self.onions = False
        self.bacon = False
        self.extra_cheese = False
    
    def __str__(self):
        toppings = []
        if self.pepperoni: toppings.append("Pepperoni")
        if self.mushrooms: toppings.append("Mushrooms")
        if self.onions: toppings.append("Onions")
        if self.bacon: toppings.append("Bacon")
        if self.extra_cheese: toppings.append("Extra Cheese")
        
        return f"""
🍕 Pizza Order:
  Size: {self.size}
  Crust: {self.crust}
  Sauce: {self.sauce}
  Cheese: {'Yes' if self.cheese else 'No'}
  Toppings: {', '.join(toppings) if toppings else 'None'}
        """.strip()

class PizzaBuilder:
    """Builder cho Pizza"""
    
    def __init__(self):
        self.pizza = Pizza()
    
    def set_size(self, size):
        self.pizza.size = size
        return self
    
    def set_crust(self, crust):
        self.pizza.crust = crust
        return self
    
    def set_sauce(self, sauce):
        self.pizza.sauce = sauce
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
    
    def add_onions(self):
        self.pizza.onions = True
        return self
    
    def add_bacon(self):
        self.pizza.bacon = True
        return self
    
    def add_extra_cheese(self):
        self.pizza.extra_cheese = True
        return self
    
    def build(self):
        return self.pizza

# Director - Xây dựng các loại pizza tiêu chuẩn
class PizzaDirector:
    @staticmethod
    def make_pepperoni():
        return (PizzaBuilder()
                .set_size("Large")
                .set_crust("Thin")
                .set_sauce("Tomato")
                .add_cheese()
                .add_pepperoni()
                .build())
    
    @staticmethod
    def make_veggie():
        return (PizzaBuilder()
                .set_size("Medium")
                .set_crust("Thick")
                .set_sauce("BBQ")
                .add_cheese()
                .add_mushrooms()
                .add_onions()
                .build())
    
    @staticmethod
    def make_meat_lovers():
        return (PizzaBuilder()
                .set_size("Large")
                .set_crust("Stuffed")
                .set_sauce("Tomato")
                .add_cheese()
                .add_pepperoni()
                .add_bacon()
                .add_extra_cheese()
                .build())

# Demo
print("--- Custom Pizza ---")
custom_pizza = (PizzaBuilder()
                .set_size("Small")
                .set_crust("Gluten-Free")
                .set_sauce("Pesto")
                .add_cheese()
                .add_mushrooms()
                .add_onions()
                .build())
print(custom_pizza)
print()

print("--- Pepperoni Pizza ---")
pepperoni = PizzaDirector.make_pepperoni()
print(pepperoni)
print()

print("--- Veggie Pizza ---")
veggie = PizzaDirector.make_veggie()
print(veggie)
print()

print("--- Meat Lovers Pizza ---")
meat = PizzaDirector.make_meat_lovers()
print(meat)
```

### 2.3. Observer Pattern

```python
print("\n=== OBSERVER PATTERN ===")

from typing import List, Callable, Any
from abc import ABC, abstractmethod

class Observer(ABC):
    """Interface cho Observer"""
    
    @abstractmethod
    def update(self, event: str, data: Any):
        pass

class EventManager:
    """Subject - Quản lý các observers và thông báo events"""
    
    def __init__(self):
        self._observers: List[Observer] = []
        self._callbacks: List[Callable] = []
    
    def attach(self, observer: Observer):
        """Thêm observer (class-based)"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer):
        """Xóa observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def on(self, callback: Callable):
        """Thêm callback (function-based)"""
        self._callbacks.append(callback)
        return callback  # Cho phép dùng decorator
    
    def notify(self, event: str, data: Any = None):
        """Thông báo cho tất cả observers"""
        print(f"📢 Event: {event}")
        
        # Notify class-based observers
        for observer in self._observers:
            observer.update(event, data)
        
        # Notify function-based observers
        for callback in self._callbacks:
            callback(event, data)

class UserManager:
    """Concrete Subject - Quản lý người dùng"""
    
    def __init__(self):
        self.users = []
        self.events = EventManager()
    
    def add_user(self, user):
        self.users.append(user)
        self.events.notify("user_added", user)
    
    def remove_user(self, user):
        if user in self.users:
            self.users.remove(user)
            self.events.notify("user_removed", user)
    
    def update_user(self, old_user, new_user):
        if old_user in self.users:
            idx = self.users.index(old_user)
            self.users[idx] = new_user
            self.events.notify("user_updated", {"old": old_user, "new": new_user})

# Concrete Observers
class EmailNotifier(Observer):
    def update(self, event: str, data: Any):
        if event == "user_added":
            print(f"📧 Sending welcome email to {data.name}")
        elif event == "user_removed":
            print(f"📧 Sending goodbye email to {data.name}")

class LoggerObserver(Observer):
    def update(self, event: str, data: Any):
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"📝 [{timestamp}] {event}: {data}")

class CacheManager:
    """Observer dùng callback"""
    
    def __init__(self):
        self.cache = {}
    
    def invalidate(self, event, data):
        if event in ["user_added", "user_removed", "user_updated"]:
            self.cache.clear()
            print(f"🗑️ Cache cleared due to {event}")

# Demo
user_manager = UserManager()

# Thêm observers
email_notifier = EmailNotifier()
logger = LoggerObserver()
cache = CacheManager()

user_manager.events.attach(email_notifier)
user_manager.events.attach(logger)
user_manager.events.on(cache.invalidate)

# Sử dụng
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
    
    def __str__(self):
        return f"{self.name} ({self.email})"

print("--- Adding users ---")
user_manager.add_user(User("John", "john@example.com"))
user_manager.add_user(User("Jane", "jane@example.com"))

print("\n--- Removing user ---")
user_manager.remove_user(User("John", "john@example.com"))

print("\n--- Updating user ---")
old_user = User("Jane", "jane@example.com")
new_user = User("Jane", "jane@newdomain.com")
user_manager.update_user(old_user, new_user)
```

### 2.4. Strategy Pattern

```python
print("\n=== STRATEGY PATTERN ===")

from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    """Interface cho các payment strategy"""
    
    @abstractmethod
    def pay(self, amount: float) -> str:
        pass

class CreditCardStrategy(PaymentStrategy):
    def __init__(self, card_number, expiry, cvv):
        self.card_number = card_number
        self.expiry = expiry
        self.cvv = cvv
    
    def pay(self, amount: float) -> str:
        print(f"💳 Processing credit card payment of ${amount}")
        print(f"   Card: {self.card_number[-4:].rjust(4, '*')}")
        return f"Paid ${amount} via Credit Card"

class PayPalStrategy(PaymentStrategy):
    def __init__(self, email, password):
        self.email = email
        self.password = password
    
    def pay(self, amount: float) -> str:
        print(f"💰 Processing PayPal payment of ${amount}")
        print(f"   Account: {self.email}")
        return f"Paid ${amount} via PayPal"

class CryptoStrategy(PaymentStrategy):
    def __init__(self, wallet_address):
        self.wallet_address = wallet_address
    
    def pay(self, amount: float) -> str:
        print(f"₿ Processing Crypto payment of ${amount}")
        print(f"   Wallet: {self.wallet_address[:8]}...")
        return f"Paid ${amount} via Cryptocurrency"

class CashStrategy(PaymentStrategy):
    def pay(self, amount: float) -> str:
        print(f"💵 Processing cash payment of ${amount}")
        return f"Paid ${amount} in Cash"

class PaymentProcessor:
    """Context - sử dụng strategy"""
    
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy
    
    def set_strategy(self, strategy: PaymentStrategy):
        self.strategy = strategy
    
    def process_payment(self, amount: float) -> str:
        return self.strategy.pay(amount)

# Demo
print("--- Payment Processing ---")

credit_card = CreditCardStrategy("1234-5678-9012-3456", "12/25", "123")
paypal = PayPalStrategy("user@example.com", "pass123")
crypto = CryptoStrategy("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
cash = CashStrategy()

processor = PaymentProcessor(credit_card)
print(processor.process_payment(99.99))
print()

processor.set_strategy(paypal)
print(processor.process_payment(49.50))
print()

processor.set_strategy(crypto)
print(processor.process_payment(1000.00))
print()

processor.set_strategy(cash)
print(processor.process_payment(25.00))
```

### 2.5. Decorator Pattern

```python
print("\n=== DECORATOR PATTERN ===")

from abc import ABC, abstractmethod

# Component Interface
class Beverage(ABC):
    @abstractmethod
    def cost(self) -> float:
        pass
    
    @abstractmethod
    def description(self) -> str:
        pass

# Concrete Components
class Espresso(Beverage):
    def cost(self) -> float:
        return 2.50
    
    def description(self) -> str:
        return "Espresso"

class HouseBlend(Beverage):
    def cost(self) -> float:
        return 2.00
    
    def description(self) -> str:
        return "House Blend Coffee"

class DarkRoast(Beverage):
    def cost(self) -> float:
        return 2.75
    
    def description(self) -> str:
        return "Dark Roast"

# Decorator Base
class CondimentDecorator(Beverage):
    def __init__(self, beverage: Beverage):
        self.beverage = beverage
    
    @abstractmethod
    def cost(self) -> float:
        pass
    
    @abstractmethod
    def description(self) -> str:
        pass

# Concrete Decorators
class Milk(CondimentDecorator):
    def cost(self) -> float:
        return self.beverage.cost() + 0.50
    
    def description(self) -> str:
        return f"{self.beverage.description()}, Milk"

class Mocha(CondimentDecorator):
    def cost(self) -> float:
        return self.beverage.cost() + 0.75
    
    def description(self) -> str:
        return f"{self.beverage.description()}, Mocha"

class Whip(CondimentDecorator):
    def cost(self) -> float:
        return self.beverage.cost() + 0.30
    
    def description(self) -> str:
        return f"{self.beverage.description()}, Whip"

class Soy(CondimentDecorator):
    def cost(self) -> float:
        return self.beverage.cost() + 0.40
    
    def description(self) -> str:
        return f"{self.beverage.description()}, Soy"

# Demo
print("--- Coffee Shop ---")

# Espresso with Mocha and Whip
espresso = Espresso()
print(f"{espresso.description()}: ${espresso.cost():.2f}")

espresso_with_mocha = Mocha(espresso)
print(f"{espresso_with_mocha.description()}: ${espresso_with_mocha.cost():.2f}")

espresso_with_mocha_whip = Whip(Mocha(espresso))
print(f"{espresso_with_mocha_whip.description()}: ${espresso_with_mocha_whip.cost():.2f}")

print()

# House Blend with Milk, Mocha, and Whip
house_blend = HouseBlend()
house_blend_with_milk = Milk(house_blend)
house_blend_with_milk_mocha = Mocha(house_blend_with_milk)
house_blend_deluxe = Whip(house_blend_with_milk_mocha)

print(f"{house_blend_deluxe.description()}: ${house_blend_deluxe.cost():.2f}")
print()

# Chaining decorators
dark_roast = DarkRoast()
dark_roast_deluxe = Whip(Mocha(Milk(dark_roast)))
print(f"{dark_roast_deluxe.description()}: ${dark_roast_deluxe.cost():.2f}")
```

---

## 🔗 PHẦN 3: COMPOSITION OVER INHERITANCE

```python
print("\n=== COMPOSITION OVER INHERITANCE ===")

# ❌ Bad: Deep inheritance hierarchy
class Animal:
    def move(self):
        pass

class Bird(Animal):
    def fly(self):
        return "Flying"

class Duck(Bird):
    def swim(self):
        return "Swimming"

class Penguin(Bird):
    def fly(self):
        return "Cannot fly"  # Vi phạm LSP!
    
    def swim(self):
        return "Swimming"

# ✅ Good: Composition with Behaviors
class FlyBehavior:
    def fly(self):
        return "Flying"

class SwimBehavior:
    def swim(self):
        return "Swimming"

class WalkBehavior:
    def walk(self):
        return "Walking"

class CannotFlyBehavior:
    def fly(self):
        return "Cannot fly"

class QuackBehavior:
    def make_sound(self):
        return "Quack!"

class MuteBehavior:
    def make_sound(self):
        return "..."

# Composition approach
class AnimalComposed:
    def __init__(self, fly_behavior=None, swim_behavior=None, 
                 walk_behavior=None, sound_behavior=None):
        self.fly_behavior = fly_behavior
        self.swim_behavior = swim_behavior
        self.walk_behavior = walk_behavior
        self.sound_behavior = sound_behavior
    
    def fly(self):
        if self.fly_behavior:
            return self.fly_behavior.fly()
        return "Cannot fly"
    
    def swim(self):
        if self.swim_behavior:
            return self.swim_behavior.swim()
        return "Cannot swim"
    
    def walk(self):
        if self.walk_behavior:
            return self.walk_behavior.walk()
        return "Cannot walk"
    
    def make_sound(self):
        if self.sound_behavior:
            return self.sound_behavior.make_sound()
        return "..."

# Tạo các loài động vật khác nhau
class DuckComposed(AnimalComposed):
    def __init__(self):
        super().__init__(
            fly_behavior=FlyBehavior(),
            swim_behavior=SwimBehavior(),
            walk_behavior=WalkBehavior(),
            sound_behavior=QuackBehavior()
        )

class PenguinComposed(AnimalComposed):
    def __init__(self):
        super().__init__(
            fly_behavior=CannotFlyBehavior(),
            swim_behavior=SwimBehavior(),
            walk_behavior=WalkBehavior(),
            sound_behavior=MuteBehavior()
        )

class FishComposed(AnimalComposed):
    def __init__(self):
        super().__init__(
            swim_behavior=SwimBehavior(),
            sound_behavior=MuteBehavior()
        )

# Demo
print("--- Inheritance vs Composition ---")
duck = Duck()
print(f"Duck: fly={duck.fly()}, swim={duck.swim()}")

penguin = Penguin()
print(f"Penguin: fly={penguin.fly()}, swim={penguin.swim()}")

print("\n--- Composition ---")
duck2 = DuckComposed()
print(f"Duck: fly={duck2.fly()}, swim={duck2.swim()}, walk={duck2.walk()}, sound={duck2.make_sound()}")

penguin2 = PenguinComposed()
print(f"Penguin: fly={penguin2.fly()}, swim={penguin2.swim()}, walk={penguin2.walk()}, sound={penguin2.make_sound()}")

fish = FishComposed()
print(f"Fish: fly={fish.fly()}, swim={fish.swim()}, walk={fish.walk()}, sound={fish.make_sound()}")

# Dễ dàng thay đổi behavior runtime
print("\n--- Runtime behavior change ---")
penguin2.fly_behavior = FlyBehavior()
print(f"Penguin after upgrade: fly={penguin2.fly()}")
```

---

## 🏗️ PHẦN 4: EVENT SYSTEM VÀ PLUGIN ARCHITECTURE

### 4.1. Event System

```python
print("\n=== EVENT SYSTEM ===")

from typing import Dict, List, Callable, Any
import time

class EventSystem:
    """Hệ thống event đơn giản"""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._once_handlers: Dict[str, List[Callable]] = {}
    
    def on(self, event: str, handler: Callable):
        """Đăng ký handler cho event"""
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)
        return handler
    
    def once(self, event: str, handler: Callable):
        """Đăng ký handler chỉ chạy 1 lần"""
        if event not in self._once_handlers:
            self._once_handlers[event] = []
        self._once_handlers[event].append(handler)
        return handler
    
    def off(self, event: str, handler: Callable):
        """Xóa handler"""
        if event in self._handlers:
            self._handlers[event].remove(handler)
    
    def emit(self, event: str, data: Any = None):
        """Phát event"""
        print(f"🔔 Emitting event: {event}")
        
        # Gọi handlers thường
        if event in self._handlers:
            for handler in self._handlers[event]:
                try:
                    handler(data)
                except Exception as e:
                    print(f"Error in handler: {e}")
        
        # Gọi once handlers
        if event in self._once_handlers:
            handlers = self._once_handlers[event].copy()
            for handler in handlers:
                try:
                    handler(data)
                except Exception as e:
                    print(f"Error in once handler: {e}")
            self._once_handlers[event].clear()

class EventEmitter:
    """Mixin để có thể emit event"""
    
    def __init__(self):
        self._events = EventSystem()
    
    def on(self, event, handler):
        self._events.on(event, handler)
        return self
    
    def once(self, event, handler):
        self._events.once(event, handler)
        return self
    
    def emit(self, event, data=None):
        self._events.emit(event, data)

# Application Example
class TaskManager(EventEmitter):
    def __init__(self):
        super().__init__()
        self.tasks = []
    
    def add_task(self, task):
        self.tasks.append(task)
        self.emit("task_added", task)
    
    def complete_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                self.emit("task_completed", task)
                return
        self.emit("task_error", f"Task {task_id} not found")
    
    def delete_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                self.tasks.remove(task)
                self.emit("task_deleted", task)
                return

# Demo
manager = TaskManager()

# Các handlers
def notify_task_added(task):
    print(f"📨 Task added: {task['title']}")

def update_stats(task):
    print(f"📊 Stats updated for task: {task['title']}")

def log_completed(task):
    print(f"✅ Task completed: {task['title']} at {time.strftime('%H:%M:%S')}")

def send_email(task):
    print(f"📧 Email sent for task: {task['title']}")

# Đăng ký handlers
manager.on("task_added", notify_task_added)
manager.on("task_added", update_stats)
manager.once("task_completed", log_completed)  # Chỉ chạy 1 lần
manager.on("task_completed", send_email)

# Test
manager.add_task({"id": 1, "title": "Learn Python", "completed": False})
manager.add_task({"id": 2, "title": "Build project", "completed": False})

manager.complete_task(1)
manager.complete_task(2)  # log_completed không chạy nữa
```

### 4.2. Plugin Architecture

```python
print("\n=== PLUGIN ARCHITECTURE ===")

from abc import ABC, abstractmethod
import importlib
import os
from typing import Dict, Type

class Plugin(ABC):
    """Base class cho tất cả plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        pass
    
    @abstractmethod
    def initialize(self, context):
        """Khởi tạo plugin"""
        pass
    
    @abstractmethod
    def execute(self, data):
        """Thực thi plugin"""
        pass

class PluginManager:
    """Quản lý plugins"""
    
    def __init__(self):
        self._plugins: Dict[str, Plugin] = {}
        self._context = {}
    
    def register(self, plugin: Plugin):
        """Đăng ký plugin"""
        print(f"📦 Registering plugin: {plugin.name} v{plugin.version}")
        plugin.initialize(self._context)
        self._plugins[plugin.name] = plugin
    
    def unregister(self, name: str):
        """Xóa plugin"""
        if name in self._plugins:
            del self._plugins[name]
            print(f"🗑️ Unregistered plugin: {name}")
    
    def get_plugin(self, name: str) -> Plugin:
        return self._plugins.get(name)
    
    def execute(self, name: str, data):
        """Thực thi plugin"""
        plugin = self.get_plugin(name)
        if plugin:
            print(f"▶️ Executing plugin: {name}")
            return plugin.execute(data)
        raise ValueError(f"Plugin '{name}' not found")
    
    def list_plugins(self):
        """Liệt kê plugins"""
        print("📋 Available plugins:")
        for name, plugin in self._plugins.items():
            print(f"  - {name} v{plugin.version}")

# Concrete Plugins
class TextProcessorPlugin(Plugin):
    @property
    def name(self):
        return "text_processor"
    
    @property
    def version(self):
        return "1.0.0"
    
    def initialize(self, context):
        context['text_processor'] = self
        print("  🔧 Initialized text processor")
    
    def execute(self, data):
        text = data.get('text', '')
        operation = data.get('operation', 'upper')
        
        if operation == 'upper':
            return text.upper()
        elif operation == 'lower':
            return text.lower()
        elif operation == 'reverse':
            return text[::-1]
        elif operation == 'title':
            return text.title()
        return text

class MathPlugin(Plugin):
    @property
    def name(self):
        return "math"
    
    @property
    def version(self):
        return "1.2.0"
    
    def initialize(self, context):
        context['math'] = self
        print("  🔧 Initialized math plugin")
    
    def execute(self, data):
        operation = data.get('operation', 'add')
        a = data.get('a', 0)
        b = data.get('b', 0)
        
        if operation == 'add':
            return a + b
        elif operation == 'sub':
            return a - b
        elif operation == 'mul':
            return a * b
        elif operation == 'div':
            return a / b if b != 0 else "Division by zero"
        return "Unknown operation"

class FilePlugin(Plugin):
    @property
    def name(self):
        return "file"
    
    @property
    def version(self):
        return "1.0.0"
    
    def initialize(self, context):
        context['file'] = self
        print("  🔧 Initialized file plugin")
    
    def execute(self, data):
        operation = data.get('operation', 'read')
        filename = data.get('filename', 'test.txt')
        
        if operation == 'read':
            try:
                with open(filename, 'r') as f:
                    return f.read()
            except FileNotFoundError:
                return f"File {filename} not found"
        elif operation == 'write':
            content = data.get('content', '')
            with open(filename, 'w') as f:
                f.write(content)
            return f"Written to {filename}"
        elif operation == 'append':
            content = data.get('content', '')
            with open(filename, 'a') as f:
                f.write(content + '\n')
            return f"Appended to {filename}"
        return "Unknown operation"

# Demo Plugin System
print("--- Plugin System ---")

manager = PluginManager()

# Register plugins
manager.register(TextProcessorPlugin())
manager.register(MathPlugin())
manager.register(FilePlugin())

print()
manager.list_plugins()

print("\n--- Executing Plugins ---")
result = manager.execute("text_processor", {
    'text': 'hello world',
    'operation': 'title'
})
print(f"Result: {result}")

result = manager.execute("math", {
    'operation': 'mul',
    'a': 6,
    'b': 7
})
print(f"Result: {result}")

# Test file plugin
result = manager.execute("file", {
    'operation': 'write',
    'filename': 'test_plugin.txt',
    'content': 'Hello from plugin!'
})
print(f"Result: {result}")
```

---

## 🎯 BÀI TẬP VỀ NHÀ BUỔI 3

### Bài 1: Plugin System với Hot Reload
Xây dựng plugin system hỗ trợ:
- Tự động phát hiện plugin trong thư mục
- Load/Unload plugin runtime
- Plugin dependencies

### Bài 2: Command Pattern với Undo/Redo
Tạo hệ thống command:
- Command interface (execute, undo)
- Command history với undo/redo
- Macro commands (nhiều commands)

### Bài 3: State Pattern cho Workflow
Xây dựng workflow system:
- States: Draft → Review → Approved → Published
- Transitions với validation
- Actions khi chuyển state

---

## 📌 TỔNG KẾT BUỔI 3

**Bạn đã học được:**
1. ✅ **Mixin Pattern** - Tái sử dụng code linh hoạt
2. ✅ **Design Patterns** quan trọng (Factory, Builder, Observer, Strategy, Decorator)
3. ✅ **Composition over Inheritance** - Thiết kế tốt hơn
4. ✅ **Event System** và **Plugin Architecture**

**Key Takeaways:**
- **Mixin** mạnh mẽ nhưng cần hiểu rõ MRO
- **Design Patterns** là giải pháp cho các vấn đề thường gặp
- **Composition** linh hoạt hơn inheritance
- **Event System** giúp tách biệt các components
- **Plugin Architecture** cho phép mở rộng dễ dàng

---

**Chuẩn bị cho Buổi 4:** Chúng ta sẽ học về **Testing OOP Code, Type Hints, và Async OOP**!

Hãy thực hành và đặt câu hỏi! 💪🐍