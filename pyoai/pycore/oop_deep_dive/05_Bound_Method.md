# Buổi 5: Method trong Python OOP – Function, Bound Method, `self` và cơ chế gọi phương thức

Đây là buổi cực kỳ quan trọng. Sau buổi này bạn sẽ hiểu bản chất của:

- Vì sao method Python luôn có `self`.
- `self` thực sự là gì.
- Tại sao `obj.method()` có thể tự truyền object vào method.
- Sự khác nhau giữa:
  - `obj.method()`
  - `Class.method(obj)`
- Function trong class khác function bình thường như thế nào.
- Khái niệm **bound method**.
- Nền tảng để hiểu `classmethod`, `staticmethod`, decorator và descriptor.

---

# 1. Function trong class có phải Method ngay không?

Ví dụ:

```text-x-trilium-auto
class Dog:

    def bark(self):
        print("Woof")
```

Nhiều người nghĩ:

```text-x-trilium-auto
bark = method
```

Nhưng thực tế:

Trong namespace của class:

```text-x-trilium-auto
print(Dog.__dict__)
```

Ta thấy:

```text-x-trilium-auto
{
    'bark': <function Dog.bark>
}
```

Nó vẫn là một **function object**.

Sơ đồ:

```text-x-trilium-auto
Dog Class

__dict__

{
    bark
       |
       v
    function object
}
```

Chưa phải method.

---

# 2. Khi nào function trở thành method?

Khi truy cập thông qua instance.

Ví dụ:

```text-x-trilium-auto
class Dog:

    def bark(self):
        print("Woof")


d = Dog()

print(Dog.bark)

print(d.bark)
```

Kết quả:

```text-x-trilium-auto
<function Dog.bark>

<bound method Dog.bark of <Dog object>>
```

Điểm khác biệt:

## Qua class

```text-x-trilium-auto
Dog.bark
```

là:

```text-x-trilium-auto
function
```

---

## Qua object

```text-x-trilium-auto
d.bark
```

là:

```text-x-trilium-auto
bound method
```

---

# 3. Bound Method là gì?

"Bound" nghĩa là "được gắn".

Ví dụ:

```text-x-trilium-auto
d.bark
```

Python tạo ra một object method đặc biệt:

```text-x-trilium-auto
Bound Method

+----------------+
| function       |
|                |
| self = d       |
+----------------+
```

Nó nhớ:

- Hàm nào cần gọi.
- Object nào sẽ được truyền vào `self`.

---

# 4. `self` thực chất là gì?

Ví dụ:

```text-x-trilium-auto
class Dog:

    def bark(self):
        print(self)


d = Dog()

d.bark()
```

Kết quả:

```text-x-trilium-auto
<__main__.Dog object at 0x...>
```

`self` chính là object gọi method.

Ở đây:

```text-x-trilium-auto
d.bark()
```

tương đương:

```text-x-trilium-auto
Dog.bark(d)
```

---

# 5. Python tự thêm self như thế nào?

Bạn viết:

```text-x-trilium-auto
d.bark()
```

Python chuyển thành:

```text-x-trilium-auto
Dog.bark(d)
```

Sơ đồ:

```text-x-trilium-auto
d.bark()

        |
        |
        v

Dog.bark(d)
```

Vì vậy:

```text-x-trilium-auto
def bark(self):
```

có nghĩa:

```text-x-trilium-auto
nhận object đang gọi method
```

---

# 6. Ví dụ chi tiết

```text-x-trilium-auto
class Person:

    def introduce(self):
        print(self)


p1 = Person()
p2 = Person()


p1.introduce()
p2.introduce()
```

Kết quả:

```text-x-trilium-auto
<Person object A>

<Person object B>
```

Mỗi lần gọi, Python truyền instance khác nhau.

---

# 7. Không có self sẽ xảy ra gì?

Sai:

```text-x-trilium-auto
class Dog:

    def bark():
        print("Woof")


d = Dog()

d.bark()
```

Kết quả:

```text-x-trilium-auto
TypeError:
Dog.bark() takes 0 positional arguments but 1 was given
```

Tại sao?

Python gọi:

```text-x-trilium-auto
Dog.bark(d)
```

Nhưng hàm:

```text-x-trilium-auto
def bark():
```

không nhận tham số.

---

# 8. Gọi qua class

Có thể gọi:

```text-x-trilium-auto
Dog.bark(d)
```

Ví dụ:

```text-x-trilium-auto
class Dog:

    def bark(self):
        print(self)


d = Dog()

Dog.bark(d)
```

Kết quả:

```text-x-trilium-auto
<Dog object>
```

Điều này chứng minh:

`self` không phải từ khóa.

Nó chỉ là tham số đầu tiên.

Bạn có thể viết:

```text-x-trilium-auto
class Dog:

    def bark(myself):
        print(myself)
```

vẫn chạy.

Nhưng quy ước Python là dùng:

```text-x-trilium-auto
self
```

---

# 9. Instance Method hoạt động bằng Descriptor

Đây là phần nâng cao.

Trong Python:

```text-x-trilium-auto
d.bark
```

không đơn giản là lấy giá trị từ dictionary.

Python thấy:

```text-x-trilium-auto
function object
```

Function trong class có cơ chế descriptor.

Nó thực hiện:

```text-x-trilium-auto
Dog.bark.__get__(d, Dog)
```

Kết quả:

```text-x-trilium-auto
Bound Method
```

Sơ đồ:

```text-x-trilium-auto
Class

bark
 |
 |
Function
 |
 |
__get__()

        |
        |
        v

Bound Method
(self=d)
```

Chúng ta sẽ học Descriptor sâu ở phần sau.

---

# 10. Instance Method

Đây là loại method phổ biến nhất.

Ví dụ:

```text-x-trilium-auto
class Account:

    def __init__(self, balance):
        self.balance = balance


    def deposit(self, amount):
        self.balance += amount


a = Account(100)

a.deposit(50)

print(a.balance)
```

Luồng:

```text-x-trilium-auto
a.deposit(50)

↓

Account.deposit(a,50)

↓

self.balance += 50
```

---

# 11. Method có thể truy cập instance

Ví dụ:

```text-x-trilium-auto
class Student:

    def __init__(self, name):
        self.name = name


    def hello(self):
        print(
            f"Hello {self.name}"
        )


s = Student("An")

s.hello()
```

Python:

```text-x-trilium-auto
Student.hello(s)
```

---

# 12. Hai object dùng cùng một method

Ví dụ:

```text-x-trilium-auto
class Counter:

    def increase(self):
        self.value += 1


a = Counter()
b = Counter()

a.value = 0 b.value = 100

a.increase()
b.increase()
```

Cùng method:

```text-x-trilium-auto
Counter.increase
```

nhưng dữ liệu khác:

```text-x-trilium-auto
a
 |
value = 1


b
 |
value = 101
```

Vì `self` khác nhau.

---

# 13. Method Object

Có thể lưu method vào biến:

```text-x-trilium-auto
class Dog:

    def bark(self):
        print("Woof")


d = Dog()

x = d.bark

x()
```

Kết quả:

```text-x-trilium-auto
Woof
```

Vì:

```text-x-trilium-auto
x
```

đã chứa:

```text-x-trilium-auto
function + self
```

---

# 14. Kiểm tra bound method

```text-x-trilium-auto
class Dog:

    def bark(self):
        pass


d = Dog()


m = d.bark


print(m.__self__)

print(m.__func__)
```

Kết quả:

```text-x-trilium-auto
<Dog object>

<function Dog.bark>
```

Một bound method gồm:

```text-x-trilium-auto
__self__
    |
    object


__func__
    |
    function
```

---

# 15. So sánh 3 kiểu gọi

## Cách 1

```text-x-trilium-auto
obj.method()
```

Python làm:

```text-x-trilium-auto
Class.method(obj)
```

---

## Cách 2

```text-x-trilium-auto
Class.method(obj)
```

Bạn tự truyền self.

---

## Cách 3

```text-x-trilium-auto
func = obj.method

func()
```

Method đã nhớ object.

---

# 16. Lỗi thường gặp

## Lỗi 1

Quên self:

```text-x-trilium-auto
class User:

    def login():
        pass
```

Sai.

---

## Lỗi 2

Dùng self sai

```text-x-trilium-auto
class User:

    def set_name(self,name):
        name = name
```

Không thay đổi object.

Đúng:

```text-x-trilium-auto
self.name = name
```

---

## Lỗi 3

Nhầm self là class

Sai:

```text-x-trilium-auto
self = User
```

Self luôn là instance.

---

# 17. Ví dụ thực tế: Repository trong dự án lớn

Ví dụ hệ thống crawler truyện:

```text-x-trilium-auto
class BookRepository:

    def __init__(self, db):
        self.db = db


    def save(self, book):
        self.db.insert(book)


repo = BookRepository(database)

repo.save(book)
```

Thực tế:

```text-x-trilium-auto
BookRepository.save(
    repo,
    book
)
```

`self.db` chính là trạng thái riêng của repository.

Đây là cách các framework lớn tổ chức code.

---

# 18. Tổng kết Buổi 5

| Khái niệm | Ý nghĩa |
| --- | --- |
| Function trong class | Function object |
| Instance.method | Bound method |
| self | Instance hiện tại |
| obj.method() | Class.method(obj) |
| `__self__` | Object được bind |
| `__func__` | Function gốc |
| Method dùng chung | Dữ liệu nằm trong instance |

---

# Bài tập thực hành

## Bài 1

Viết class:

```text-x-trilium-auto
class Calculator:
```

Có:

```text-x-trilium-auto
add(self,a,b)
subtract(self,a,b)
multiply(self,a,b)
```

Gọi:

```text-x-trilium-auto
calc.add(5,3)
```

Sau đó thử:

```text-x-trilium-auto
Calculator.add(calc,5,3)
```

Giải thích.

---

## Bài 2

Viết:

```text-x-trilium-auto
class User:

    def hello(self):
        print(self)
```

Tạo 2 user.

So sánh:

```text-x-trilium-auto
u1.hello
u2.hello
```

Xem `__self__`.

---

## Bài 3 (Nâng cao)

Tạo:

```text-x-trilium-auto
class Logger:

    def log(self,msg):
        print(msg)
```

Lưu:

```text-x-trilium-auto
func = logger.log
```

Gọi lại sau.

Giải thích tại sao `func()` vẫn biết object nào là `self`.

---

## Chuẩn bị Buổi 6

Buổi tiếp theo chúng ta sẽ học:

# Encapsulation trong Python

- Public, Protected, Private thực sự trong Python.
- Vì sao Python không có `private` thật.
- Name Mangling (`__variable`).
- Cơ chế ẩn dữ liệu.
- Thiết kế class an toàn.
- So sánh Python với Java/C++.

Đây là nền tảng để xây dựng các model, service, repository trong các dự án lớn.