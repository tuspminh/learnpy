# Buổi 9: Inheritance (Kế thừa) và `super()` – Deep Dive

Đây là buổi đầu tiên của phần **Inheritance**. Rất nhiều lập trình viên biết cách viết:

```text-x-trilium-auto
class Dog(Animal):
    pass
```

nhưng **không thực sự hiểu Python làm gì phía sau**.

Sau buổi này, bạn sẽ hiểu:

- Kế thừa thực chất là gì.
- Python tìm method theo thứ tự nào.
- Override hoạt động ra sao.
- `super()` thực sự là gì.
- Vì sao `super()` không phải là "gọi class cha".
- Cách thiết kế class base cho các dự án lớn (PySide6, Crawler, Backend...).

---

# Mục tiêu

Sau buổi này bạn sẽ nắm được:

- Single Inheritance
- Override
- `super()`
- Constructor Chain
- Method Lookup
- IS-A Relationship
- Liskov Substitution Principle (LSP)

---

# 1. Tại sao cần Inheritance?

Giả sử bạn viết:

```text-x-trilium-auto
class Dog:

    def eat(self):
        print("Eating")


class Cat:

    def eat(self):
        print("Eating")


class Bird:

    def eat(self):
        print("Eating")
```

Có gì sai?

Bạn đang lặp code.

---

Thay vào đó:

```text-x-trilium-auto
class Animal:

    def eat(self):
        print("Eating")


class Dog(Animal):
    pass


class Cat(Animal):
    pass


class Bird(Animal):
    pass
```

Sơ đồ:

```text-x-trilium-auto
          Animal
         /   |   \
       Dog  Cat  Bird
```

Code dùng chung được đặt trong `Animal`.

---

# 2. IS-A Relationship

Một nguyên tắc quan trọng:

```text-x-trilium-auto
Dog IS-A Animal

Cat IS-A Animal

Bird IS-A Animal
```

Nhưng:

```text-x-trilium-auto
Animal IS-A Dog
```

❌ Sai.

---

Ví dụ đúng:

```text-x-trilium-auto
class Vehicle:
    pass


class Car(Vehicle):
    pass
```

Car là Vehicle.

---

Ví dụ sai:

```text-x-trilium-auto
class Engine(Vehicle):
```

Engine không phải Vehicle.

Đây nên là **Composition**, không phải Inheritance.

---

# 3. Khi tạo Dog

```text-x-trilium-auto
class Animal:
    pass


class Dog(Animal):
    pass
```

Python tạo:

```text-x-trilium-auto
Dog

↓

Base Class

↓

Animal
```

Kiểm tra:

```text-x-trilium-auto
print(Dog.__bases__)
```

Kết quả:

```text-x-trilium-auto
(<class '__main__.Animal'>,)
```

---

# 4. Kiểm tra quan hệ

```text-x-trilium-auto
print(isinstance(Dog(), Animal))
```

Kết quả:

```text-x-trilium-auto
True
```

Vì:

```text-x-trilium-auto
Dog

↓

Animal
```

---

Ngược lại:

```text-x-trilium-auto
print(isinstance(Animal(), Dog))
```

Kết quả:

```text-x-trilium-auto
False
```

---

# 5. Attribute Lookup khi kế thừa

Ví dụ:

```text-x-trilium-auto
class Animal:

    def eat(self):
        print("Eating")


class Dog(Animal):
    pass


d = Dog()

d.eat()
```

Python tìm:

```text-x-trilium-auto
Dog Instance

↓

Dog Class

↓

Không có

↓

Animal

↓

Có

↓

eat()
```

---

Sơ đồ:

```text-x-trilium-auto
Dog Instance

↓

Dog

↓

Animal

↓

object
```

Đây là chuỗi lookup cơ bản.

---

# 6. Override

Ví dụ:

```text-x-trilium-auto
class Animal:

    def speak(self):
        print("...")


class Dog(Animal):

    def speak(self):
        print("Woof")
```

Khi:

```text-x-trilium-auto
Dog().speak()
```

Python tìm:

```text-x-trilium-auto
Dog

↓

Có speak()

↓

Dừng
```

Không lên `Animal`.

Đây gọi là **Method Override**.

---

# 7. Gọi method của lớp cha

Ví dụ:

```text-x-trilium-auto
class Animal:

    def speak(self):
        print("Animal")


class Dog(Animal):

    def speak(self):

        Animal.speak(self)

        print("Dog")
```

Kết quả:

```text-x-trilium-auto
Animal

Dog
```

Đây là cách cũ.

Python khuyến khích dùng `super()`.

---

# 8. `super()` là gì?

Nhiều người nghĩ:

```text-x-trilium-auto
super()

↓

Class Cha
```

Sai.

`super()` **không phải** là "class cha".

Nó là một **proxy object** dùng để tiếp tục quá trình tra cứu phương thức theo **Method Resolution Order (MRO)**.

Điểm này cực kỳ quan trọng vì ở đa kế thừa (multiple inheritance), "class cha" không phải lúc nào cũng là lớp sẽ được gọi tiếp theo.

---

# 9. Ví dụ

```text-x-trilium-auto
class Animal:

    def speak(self):
        print("Animal")


class Dog(Animal):

    def speak(self):

        super().speak()

        print("Dog")
```

Kết quả:

```text-x-trilium-auto
Animal

Dog
```

---

# 10. `super()` làm gì?

Khi:

```text-x-trilium-auto
super().speak()
```

Python:

```text-x-trilium-auto
Dog

↓

MRO

↓

Sau Dog là gì?

↓

Animal

↓

Gọi speak()
```

Quan trọng là **"sau Dog trong MRO"**, không phải "class cha trực tiếp".

---

# 11. Constructor Chain

Ví dụ:

```text-x-trilium-auto
class Animal:

    def __init__(self):
        print("Animal")


class Dog(Animal):

    def __init__(self):
        print("Dog")
```

Thử:

```text-x-trilium-auto
Dog()
```

Kết quả:

```text-x-trilium-auto
Dog
```

`Animal.__init__` không chạy.

---

# 12. Dùng `super()`

```text-x-trilium-auto
class Animal:

    def __init__(self):
        print("Animal")


class Dog(Animal):

    def __init__(self):

        super().__init__()

        print("Dog")
```

Kết quả:

```text-x-trilium-auto
Animal

Dog
```

---

# 13. Chuỗi Constructor

```text-x-trilium-auto
Dog()

↓

Dog.__init__()

↓

super()

↓

Animal.__init__()

↓

Trở về Dog
```

---

# 14. Truyền tham số

```text-x-trilium-auto
class Animal:

    def __init__(self,name):

        self.name=name


class Dog(Animal):

    def __init__(self,name):

        super().__init__(name)
```

Sử dụng:

```text-x-trilium-auto
d=Dog("Lucky")

print(d.name)
```

Kết quả:

```text-x-trilium-auto
Lucky
```

---

# 15. Override nhưng mở rộng hành vi

Ví dụ:

```text-x-trilium-auto
class Animal:

    def eat(self):
        print("Eating")


class Dog(Animal):

    def eat(self):

        super().eat()

        print("Chewing bone")
```

Kết quả:

```text-x-trilium-auto
Eating

Chewing bone
```

Đây là kiểu override phổ biến nhất.

---

# 16. Không nên copy code

Sai:

```text-x-trilium-auto
class Animal:

    def eat(self):

        print("Eating")


class Dog(Animal):

    def eat(self):

        print("Eating")

        print("Bone")
```

Nếu sau này `Animal.eat()` thay đổi, bạn phải sửa ở nhiều nơi.

Đúng:

```text-x-trilium-auto
super().eat()
```

---

# 17. Kiểm tra MRO

```text-x-trilium-auto
class Animal:
    pass


class Dog(Animal):
    pass


print(Dog.mro())
```

Kết quả:

```text-x-trilium-auto
[
 Dog,
 Animal,
 object
]
```

Đây chính là thứ tự Python tìm method.

Ở buổi 10 chúng ta sẽ nghiên cứu MRO sâu hơn với **Multiple Inheritance**.

---

# 18. Ví dụ thực tế trong dự án Crawler

Giả sử bạn có:

```text-x-trilium-auto
class BaseSource:

    def fetch(self):
        print("Download HTML")
```

Nguồn cụ thể:

```text-x-trilium-auto
class TruyenFullSource(BaseSource):

    def fetch(self):

        html = super().fetch()

        print("Parse HTML")
```

Sơ đồ:

```text-x-trilium-auto
BaseSource.fetch()

↓

Download

↓

Return HTML

↓

TruyenFull.fetch()

↓

Parse
```

Đây là cách rất phổ biến khi xây dựng plugin.

---

# 19. Liskov Substitution Principle (LSP)

Một đối tượng của lớp con phải có thể thay thế lớp cha mà không làm chương trình hoạt động sai.

Ví dụ:

```text-x-trilium-auto
class Animal:

    def speak(self):
        pass


class Dog(Animal):

    def speak(self):
        print("Woof")
```

Hàm:

```text-x-trilium-auto
def make_sound(animal):
    animal.speak()
```

Có thể truyền:

```text-x-trilium-auto
make_sound(Dog())
```

Được.

Đây là LSP.

Nếu lớp con phá vỡ kỳ vọng của lớp cha, thiết kế có thể chưa hợp lý.

---

# 20. Sai lầm phổ biến

## Sai

Quên gọi:

```text-x-trilium-auto
super().__init__()
```

Dẫn đến class cha chưa được khởi tạo.

---

## Sai

Copy toàn bộ code của class cha.

Nên:

```text-x-trilium-auto
super()
```

---

## Sai

Nghĩ:

```text-x-trilium-auto
super

↓

Class cha
```

Thực tế:

```text-x-trilium-auto
super

↓

Proxy

↓

MRO

↓

Method tiếp theo
```

---

# 21. Tổng kết

| Khái niệm | Ý nghĩa |
| --- | --- |
| Inheritance | Tái sử dụng và mở rộng hành vi |
| Override | Lớp con định nghĩa lại method |
| `super()` | Tiếp tục tra cứu theo MRO |
| Constructor Chain | Chuỗi khởi tạo từ lớp con lên các lớp cơ sở |
| `isinstance()` | Kiểm tra quan hệ IS-A |
| `mro()` | Thứ tự Python tìm thuộc tính/phương thức |

---

# Bài tập thực hành

## Bài 1

Viết:

```text-x-trilium-auto
class Animal:

    def eat(self):
        print("Eating")
```

Lớp:

```text-x-trilium-auto
class Dog(Animal):
```

Override:

```text-x-trilium-auto
eat()
```

Yêu cầu:

- Gọi `super().eat()`
- Sau đó in:

```text-x-trilium-auto
Eating bone
```

---

## Bài 2

Viết:

```text-x-trilium-auto
class Vehicle
```

Có:

```text-x-trilium-auto
__init__(brand)
```

Lớp:

```text-x-trilium-auto
class Car(Vehicle)
```

Có thêm:

```text-x-trilium-auto
model
```

Sử dụng `super()` để khởi tạo `brand`.

---

## Bài 3

In kết quả:

```text-x-trilium-auto
print(Car.mro())
```

Giải thích từng phần tử trong danh sách.

---

## Bài 4 (Áp dụng dự án crawler)

Thiết kế:

```text-x-trilium-auto
class BaseSource:

    def fetch(self):
        print("Download HTML")

    def parse(self):
        raise NotImplementedError
```

Lớp:

```text-x-trilium-auto
class TruyenFullSource(BaseSource):
```

- Override `fetch()`, gọi `super().fetch()` rồi in `"Using TruyenFull headers"`.
- Override `parse()` để in `"Parse TruyenFull HTML"`.

Qua bài này, bạn sẽ thấy cách xây dựng **plugin architecture** bằng kế thừa và override.

---

# Chuẩn bị cho Buổi 10

Buổi tiếp theo là một trong những chủ đề khó nhất của OOP Python:

# Multiple Inheritance và MRO Deep Dive

Chúng ta sẽ học:

- Multiple Inheritance.
- Diamond Problem.
- C3 Linearization.
- `super()` hoạt động như thế nào trong đa kế thừa.
- Vì sao Python giải quyết Diamond Problem tốt hơn nhiều ngôn ngữ khác.
- Cách các framework như **PySide6** và **Django** sử dụng multiple inheritance và mixin trong thực tế.

Đây là bước ngoặt để bạn hiểu đầy đủ cơ chế tra cứu phương thức của Python.