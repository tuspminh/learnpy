# Python OOP Master – Buổi 6

# Encapsulation (Đóng gói) – Public, Protected, Private và Name Mangling

> Đây là một trong **4 trụ cột của OOP**. Tuy nhiên, Encapsulation trong Python **khác với Java hay C++**. Nếu áp dụng tư duy của Java vào Python, bạn sẽ dễ viết code không "Pythonic".

Sau buổi này, bạn sẽ hiểu:

* Encapsulation thực sự là gì.
* Python quản lý quyền truy cập thuộc tính như thế nào.
* Sự khác nhau giữa `public`, `_protected` và `__private`.
* Name Mangling là gì và hoạt động ra sao.
* Khi nào nên dùng từng loại thuộc tính.

---

# Mục tiêu

Sau buổi học này, bạn sẽ:

* Hiểu bản chất của Encapsulation.
* Phân biệt Public, Protected và Private.
* Hiểu Name Mangling.
* Biết cách bảo vệ trạng thái của object.
* Biết quy ước (convention) của Python về quyền truy cập.

---

# 1. Encapsulation là gì?

**Encapsulation (Đóng gói)** là việc:

* Gom **dữ liệu (attributes)** và **hành vi (methods)** vào cùng một class.
* Kiểm soát cách dữ liệu được truy cập và thay đổi.
* Giữ object ở trạng thái hợp lệ (valid state).

Ví dụ:

```text
BankAccount
│
├── balance
├── owner
├── deposit()
├── withdraw()
└── display()
```

Bạn không muốn người dùng tự ý sửa:

```python
account.balance = -1_000_000
```

Thay vào đó, họ phải dùng:

```python
account.withdraw(500)
```

để class có thể kiểm tra tính hợp lệ.

---

# 2. Public Attribute

Đây là kiểu mặc định trong Python.

```python
class Student:
    def __init__(self, name):
        self.name = name
```

Sử dụng:

```python
student = Student("Alice")

print(student.name)

student.name = "Bob"

print(student.name)
```

Kết quả:

```text
Alice
Bob
```

Có thể đọc và ghi từ bất cứ đâu.

---

# 3. Public Method

```python
class Student:
    def hello(self):
        print("Hello")
```

Gọi:

```python
student = Student()

student.hello()
```

---

# 4. Protected Attribute (`_`)

Theo quy ước của Python:

```python
class Student:
    def __init__(self):
        self._score = 10
```

Dấu gạch dưới **không tạo cơ chế bảo vệ**.

Nó chỉ có nghĩa:

> "Đây là thành phần nội bộ, không nên sử dụng trực tiếp từ bên ngoài."

Ví dụ:

```python
student = Student()

print(student._score)
```

Vẫn chạy bình thường.

---

# 5. Vì sao vẫn dùng `_`?

Ví dụ:

```python
class Database:
    def __init__(self):
        self._connection = None

    def connect(self):
        print("Connected")
```

Người dùng class nên gọi:

```python
db.connect()
```

Thay vì:

```python
db._connection = "fake_connection"
```

Đây là **quy ước giữa các lập trình viên**.

---

# 6. Private Attribute (`__`)

Python hỗ trợ:

```python
class Student:
    def __init__(self):
        self.__age = 18
```

Thử truy cập:

```python
student = Student()

print(student.__age)
```

Kết quả:

```text
AttributeError:
'Student' object has no attribute '__age'
```

Điều gì xảy ra?

---

# 7. Name Mangling

Python **không thực sự tạo private**.

Thay vào đó, Python đổi tên thuộc tính.

Ví dụ:

```python
class Student:
    def __init__(self):
        self.__age = 18
```

Kiểm tra:

```python
student = Student()

print(student.__dict__)
```

Kết quả:

```python
{"_Student__age": 18}
```

Python đã đổi:

```text
__age

↓

_Student__age
```

Đây gọi là **Name Mangling**.

---

# 8. Truy cập sau Name Mangling

Bạn vẫn có thể:

```python
print(student._Student__age)
```

Kết quả:

```text
18
```

Điều này cho thấy:

> `__private` trong Python nhằm **tránh truy cập nhầm hoặc ghi đè ngoài ý muốn**, chứ không phải cơ chế bảo mật tuyệt đối.

---

# 9. Private Method

```python
class User:
    def __login(self):
        print("Login")

    def start(self):
        self.__login()
```

Sử dụng:

```python
user = User()

user.start()
```

Kết quả:

```text
Login
```

Nhưng:

```python
user.__login()
```

Sẽ báo lỗi.

---

# 10. Name Mangling với Method

```python
class User:
    def __login(self):
        pass


print(User.__dict__.keys())
```

Bạn sẽ thấy (rút gọn):

```text
dict_keys([
    '_User__login',
    ...
])
```

---

# 11. Vì sao cần Private?

Ví dụ tài khoản ngân hàng.

❌ Thiết kế kém:

```python
class BankAccount:
    def __init__(self):
        self.balance = 1000
```

Người dùng có thể:

```python
account.balance = -999999
```

Không hợp lệ.

---

Thiết kế tốt hơn:

```python
class BankAccount:
    def __init__(self):
        self.__balance = 1000

    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount

    def withdraw(self, amount):
        if 0 < amount <= self.__balance:
            self.__balance -= amount

    def display(self):
        print(self.__balance)
```

Toàn bộ thay đổi đều đi qua các method kiểm tra điều kiện.

---

# 12. Không nên lạm dụng Private

Nhiều người mới học viết:

```python
class Student:
    def __init__(self):
        self.__name = ""
        self.__age = 0
        self.__address = ""
        self.__phone = ""
```

Rồi tạo rất nhiều getter/setter giống Java.

Trong Python, điều này thường không cần thiết.

Nếu dữ liệu không cần kiểm soát đặc biệt, hãy dùng:

```python
self.name
self.age
```

Đơn giản và dễ đọc hơn.

---

# 13. Protected trong kế thừa

```python
class Animal:
    def __init__(self):
        self._name = "Animal"


class Dog(Animal):
    def show(self):
        print(self._name)


dog = Dog()
dog.show()
```

Kết quả:

```text
Animal
```

Dấu `_` thể hiện thuộc tính này dành cho class hiện tại và các class kế thừa.

---

# 14. Private trong kế thừa

```python
class Animal:
    def __init__(self):
        self.__name = "Animal"


class Dog(Animal):
    def show(self):
        print(self.__name)
```

Kết quả:

```text
AttributeError
```

Vì sau Name Mangling:

```text
Animal.__name

↓

_Animal__name
```

Trong `Dog`, `self.__name` sẽ bị đổi thành:

```text
_Dog__name
```

Đó là **hai thuộc tính khác nhau**.

---

# 15. Ví dụ hoàn chỉnh

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner  # Public
        self._status = "Active"  # Protected (theo quy ước)
        self.__balance = balance  # Private (Name Mangling)

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        self.__balance += amount

    def withdraw(self, amount):
        if amount > self.__balance:
            print("Không đủ số dư.")
            return
        self.__balance -= amount

    def display(self):
        print(f"Owner   : {self.owner}")
        print(f"Status  : {self._status}")
        print(f"Balance : {self.__balance}")


account = BankAccount("Alice", 1000)

account.deposit(500)
account.withdraw(300)

account.display()

print("\nObject namespace:")
print(account.__dict__)
```

Kết quả:

```text
Owner   : Alice
Status  : Active
Balance : 1200

Object namespace:
{
    'owner': 'Alice',
    '_status': 'Active',
    '_BankAccount__balance': 1200
}
```

---

# So sánh Public – Protected – Private

| Loại      | Ký hiệu  | Có truy cập được từ ngoài? | Ý nghĩa                                                              |
| --------- | -------- | -------------------------- | -------------------------------------------------------------------- |
| Public    | `name`   | ✅ Có                       | API công khai của class                                              |
| Protected | `_name`  | ✅ Có (nhưng không nên)     | Thành phần nội bộ, dành cho class và subclass                        |
| Private   | `__name` | ❌ Không trực tiếp          | Python dùng Name Mangling để tránh truy cập hoặc ghi đè ngoài ý muốn |

---

# Best Practices

✅ Dùng **Public** cho API mà người dùng class cần sử dụng.

```python
self.name
self.deposit()
```

✅ Dùng **Protected (`_`)** cho thuộc tính hoặc method nội bộ.

```python
self._connection
self._cache
```

✅ Chỉ dùng **Private (`__`)** khi thật sự cần tránh xung đột tên hoặc bảo vệ trạng thái quan trọng.

---

# Những lỗi người mới thường gặp

### Lỗi 1: Nghĩ `__private` là bảo mật

Sai.

Python chỉ đổi tên thuộc tính bằng Name Mangling.

---

### Lỗi 2: Dùng quá nhiều Private

Viết code theo phong cách Java:

```python
__name
get_name()
set_name()
```

Trong Python, điều này thường làm code dài dòng không cần thiết.

---

### Lỗi 3: Truy cập `_protected` từ bên ngoài

```python
db._connection
```

Không phải lỗi cú pháp, nhưng phá vỡ quy ước thiết kế và làm tăng mức độ phụ thuộc vào chi tiết triển khai.

---

### Lỗi 4: Dùng `__private` rồi cố truy cập trong subclass

```python
self.__name
```

sẽ không truy cập được thuộc tính `__name` của class cha do Name Mangling.

---

# Bài tập

## Bài 1

Viết class `Employee`:

* Public:

  * `name`
* Protected:

  * `_department`
* Private:

  * `__salary`

Viết method `display()` để in đầy đủ thông tin.

Quan sát `__dict__`.

---

## Bài 2

Viết class `BankAccount`

* Private:

  * `__balance`

Method:

* `deposit()`
* `withdraw()`
* `display()`

Đảm bảo không thể nạp số tiền âm hoặc rút quá số dư.

---

## Bài 3

Viết class `Database`

* `_connection`
* `_connected`

Method:

* `connect()`
* `disconnect()`

Không truy cập trực tiếp `_connection` từ bên ngoài trong phần sử dụng.

---

## Bài 4

Viết hai class:

```text
Animal
Dog
```

Trong `Animal`:

```python
self.__name = "Animal"
```

Trong `Dog`, thử:

```python
print(self.__name)
```

Sau đó:

* Giải thích lỗi.
* Truy cập đúng bằng Name Mangling để quan sát kết quả.

---

## Bài 5 (Nâng cao)

Thiết kế class `UserAccount`:

* Public:

  * `username`
* Protected:

  * `_last_login`
* Private:

  * `__password_hash`

Yêu cầu:

* Có method `change_password(new_hash)`.
* Không cho phép truy cập trực tiếp `__password_hash`.
* In `__dict__` và giải thích vì sao tên thuộc tính đã bị đổi.

---

# Tóm tắt buổi học

* **Encapsulation** giúp kết hợp dữ liệu và hành vi, đồng thời kiểm soát cách dữ liệu được thay đổi.
* Python sử dụng **quy ước** nhiều hơn là cơ chế cứng về quyền truy cập.
* `public` là API công khai.
* `_protected` chỉ là quy ước: "đây là thành phần nội bộ".
* `__private` sử dụng **Name Mangling** (`_ClassName__attribute`) để tránh xung đột tên và truy cập nhầm, không phải để bảo mật.
* Trong Python, hãy ưu tiên thiết kế API rõ ràng thay vì lạm dụng `private`.

> **Buổi 7** chúng ta sẽ học **Getter, Setter và `@property` (phần 1)**: tại sao Python không khuyến khích viết getter/setter kiểu Java, cách chuyển từ thuộc tính công khai sang thuộc tính có kiểm soát mà **không làm thay đổi API**, và nền tảng của cơ chế `descriptor` phía sau `property`.
