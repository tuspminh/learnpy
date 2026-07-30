# Buổi 10: Multiple Inheritance, Diamond Problem và C3 MRO Deep Dive

Đây là một trong những chủ đề khó nhất của OOP Python.

Rất nhiều lập trình viên đã dùng Python nhiều năm nhưng vẫn hiểu sai về `super()` trong **multiple inheritance**.

Sau buổi này, bạn sẽ hiểu:

- Multiple Inheritance hoạt động như thế nào.
- Diamond Problem là gì.
- Python giải quyết Diamond Problem ra sao.
- C3 Linearization là gì.
- Vì sao `super()` **không hề gọi class cha**, mà gọi **class tiếp theo trong MRO**.
- Tại sao Django, PySide6, SQLAlchemy dùng rất nhiều Multiple Inheritance.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- Multiple Inheritance
- Diamond Problem
- MRO (Method Resolution Order)
- C3 Linearization
- Cooperative Inheritance
- `super()` trong Multiple Inheritance

---

# 1. Multiple Inheritance là gì?

Single Inheritance:

```text-x-trilium-auto
Animal
   │
   ▼
 Dog
```

Multiple Inheritance:

```text-x-trilium-auto
 Animal      Pet
      \      /
       \    /
        Dog
```

Python cho phép:

```text-x-trilium-auto
class Animal:
    pass


class Pet:
    pass


class Dog(Animal, Pet):
    pass
```

Dog kế thừa từ **hai class**.

---

# 2. Python tìm method như thế nào?

Ví dụ:

```text-x-trilium-auto
class Animal:

    def speak(self):
        print("Animal")


class Pet:

    def speak(self):
        print("Pet")


class Dog(Animal, Pet):
    pass


Dog().speak()
```

Kết quả:

```text-x-trilium-auto
Animal
```

Tại sao?

---

Python xem MRO:

```text-x-trilium-auto
print(Dog.mro())
```

Kết quả:

```text-x-trilium-auto
[
 Dog,
 Animal,
 Pet,
 object
]
```

Lookup:

```text-x-trilium-auto
Dog

↓

Animal

↓

Pet

↓

object
```

Python gặp `Animal.speak()` trước nên dừng.

---

# 3. Đổi thứ tự kế thừa

Ví dụ:

```text-x-trilium-auto
class Dog(Pet, Animal):
    pass
```

MRO:

```text-x-trilium-auto
[
 Dog,
 Pet,
 Animal,
 object
]
```

Kết quả:

```text-x-trilium-auto
Pet
```

=> **Thứ tự trong dấu ngoặc ảnh hưởng đến MRO**, nhưng không phải là quy tắc duy nhất khi sơ đồ kế thừa phức tạp.

---

# 4. Diamond Problem

Đây là vấn đề nổi tiếng trong OOP.

```text-x-trilium-auto
          Animal
          /    \
         /      \
      Mammal   Pet
         \      /
          \    /
            Dog
```

Code:

```text-x-trilium-auto
class Animal:

    def speak(self):
        print("Animal")


class Mammal(Animal):
    pass


class Pet(Animal):
    pass


class Dog(Mammal, Pet):
    pass
```

---

# 5. Nếu không có MRO

Python sẽ phân vân:

```text-x-trilium-auto
Dog

↓

Mammal

↓

Animal


Hay


Dog

↓

Pet

↓

Animal
```

Nếu cả hai đều gọi `Animal`, có thể:

```text-x-trilium-auto
Animal

↓

Animal
```

bị gọi hai lần.

Đây chính là Diamond Problem.

---

# 6. Python giải quyết thế nào?

Python tạo một MRO duy nhất.

```text-x-trilium-auto
print(Dog.mro())
```

Kết quả:

```text-x-trilium-auto
[
 Dog,
 Mammal,
 Pet,
 Animal,
 object
]
```

Quan trọng:

```text-x-trilium-auto
Animal

chỉ xuất hiện

một lần
```

---

# 7. Vì sao?

Python sử dụng thuật toán:

# C3 Linearization

Mục tiêu:

- Không lặp class.
- Giữ đúng thứ tự ưu tiên.
- Mỗi class chỉ xuất hiện một lần.

---

# 8. Ví dụ Constructor

```text-x-trilium-auto
class Animal:

    def __init__(self):
        print("Animal")


class Mammal(Animal):

    def __init__(self):

        super().__init__()

        print("Mammal")


class Pet(Animal):

    def __init__(self):

        super().__init__()

        print("Pet")


class Dog(Mammal, Pet):

    def __init__(self):

        super().__init__()

        print("Dog")
```

Gọi:

```text-x-trilium-auto
Dog()
```

---

# 9. Kết quả

```text-x-trilium-auto
Animal
Pet
Mammal
Dog
```

Nhiều người ngạc nhiên:

> Tại sao `Pet` chạy trước `Mammal` khi `Dog` kế thừa `(Mammal, Pet)`?

Để hiểu điều này, ta phải xem MRO.

---

# 10. Xem MRO

```text-x-trilium-auto
print(Dog.mro())
```

Kết quả:

```text-x-trilium-auto
[
 Dog,
 Mammal,
 Pet,
 Animal,
 object
]
```

Luồng gọi `super()`:

```text-x-trilium-auto
Dog.__init__()

↓

Mammal.__init__()

↓

Pet.__init__()

↓

Animal.__init__()

↓

object.__init__()
```

Lưu ý: thông điệp `"Animal"` được in **đầu tiên** vì `Animal.__init__()` được gọi trước khi hàm quay trở lại `Pet.__init__()` để in `"Pet"`, rồi tiếp tục quay lại `Mammal`, rồi `Dog`. Đây là cơ chế lời gọi lồng nhau (call stack).

---

# 11. Minh họa Call Stack

```text-x-trilium-auto
Dog.__init__()

↓

super()

↓

Mammal.__init__()

↓

super()

↓

Pet.__init__()

↓

super()

↓

Animal.__init__()

↓

return

↓

Pet

↓

return

↓

Mammal

↓

return

↓

Dog
```

Đây là điểm rất quan trọng.

---

# 12. `super()` KHÔNG gọi class cha

Đây là hiểu nhầm phổ biến.

Ví dụ:

```text-x-trilium-auto
super().__init__()
```

Không có nghĩa:

```text-x-trilium-auto
Gọi Animal
```

Mà là:

```text-x-trilium-auto
Tìm class tiếp theo

trong MRO
```

Đó là lý do `super()` hoạt động đúng trong cả single lẫn multiple inheritance.

---

# 13. `super()` là Proxy

Hãy tưởng tượng:

```text-x-trilium-auto
Dog

↓

super

↓

MRO

↓

Class tiếp theo
```

Nó giống như một con trỏ đang di chuyển trên danh sách MRO.

---

# 14. Điều gì xảy ra nếu không dùng `super()`?

Ví dụ:

```text-x-trilium-auto
class Mammal(Animal):

    def __init__(self):

        Animal.__init__(self)

        print("Mammal")
```

Và:

```text-x-trilium-auto
class Pet(Animal):

    def __init__(self):

        Animal.__init__(self)

        print("Pet")
```

Lúc này:

```text-x-trilium-auto
Animal
```

có thể bị gọi nhiều lần trong những sơ đồ phức tạp hơn.

Đó là lý do Python khuyến khích:

```text-x-trilium-auto
super()
```

---

# 15. Cooperative Inheritance

Python Multiple Inheritance hoạt động tốt khi:

Mọi class đều:

```text-x-trilium-auto
super()
```

Không ai gọi trực tiếp:

```text-x-trilium-auto
Animal.method()
```

Mỗi lớp chỉ làm phần việc của mình rồi chuyển tiếp cho lớp kế tiếp trong MRO.

Đây gọi là:

```text-x-trilium-auto
Cooperative Inheritance
```

---

# 16. Ví dụ Logging

```text-x-trilium-auto
class Logger:

    def process(self):

        print("Logging")

        super().process()
```

---

```text-x-trilium-auto
class Validator:

    def process(self):

        print("Validate")

        super().process()
```

---

```text-x-trilium-auto
class Base:

    def process(self):
        print("Done")
```

---

```text-x-trilium-auto
class App(Logger, Validator, Base):
    pass
```

Kết quả:

```text-x-trilium-auto
Logging

Validate

Done
```

Không lớp nào cần biết lớp kế tiếp là ai, chỉ cần gọi `super()`.

---

# 17. MRO trong ví dụ trên

```text-x-trilium-auto
print(App.mro())
```

```text-x-trilium-auto
App

↓

Logger

↓

Validator

↓

Base

↓

object
```

---

# 18. Ví dụ PySide6

Trong Qt:

```text-x-trilium-auto
class MainWindow(
    QMainWindow,
    Ui_MainWindow
):
    pass
```

Đây là Multiple Inheritance.

Qt tận dụng MRO để kết hợp:

- Cửa sổ (`QMainWindow`)
- Giao diện sinh từ Qt Designer (`Ui_MainWindow`)

thành một class hoàn chỉnh.

---

# 19. Ví dụ Django

```text-x-trilium-auto
class UserView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView
):
    pass
```

Mỗi Mixin thêm một hành vi:

```text-x-trilium-auto
Login

↓

Permission

↓

ListView

↓

View
```

Mỗi lớp đều gọi `super()`, nên chúng phối hợp với nhau theo MRO.

---

# 20. Áp dụng vào hệ thống crawler

Bạn đang xây dựng plugin crawler.

Có thể thiết kế:

```text-x-trilium-auto
class RetryMixin:

    def fetch(self):
        print("Retry")
        return super().fetch()
```

```text-x-trilium-auto
class CacheMixin:

    def fetch(self):
        print("Cache")
        return super().fetch()
```

```text-x-trilium-auto
class BaseSource:

    def fetch(self):
        print("Download")
```

```text-x-trilium-auto
class TruyenFull(
    RetryMixin,
    CacheMixin,
    BaseSource
):
    pass
```

Kết quả:

```text-x-trilium-auto
Retry

Cache

Download
```

MRO:

```text-x-trilium-auto
TruyenFull

↓

RetryMixin

↓

CacheMixin

↓

BaseSource

↓

object
```

Đây là cách thiết kế rất phổ biến trong các framework Python.

---

# 21. Sai lầm phổ biến

## Sai lầm 1

Nghĩ:

```text-x-trilium-auto
super

↓

Class cha
```

Sai.

Đúng:

```text-x-trilium-auto
super

↓

Class tiếp theo trong MRO
```

---

## Sai lầm 2

Gọi trực tiếp:

```text-x-trilium-auto
Animal.method(self)
```

Trong multiple inheritance, điều này có thể phá vỡ chuỗi MRO và làm một số lớp bị bỏ qua hoặc bị gọi lặp lại.

---

## Sai lầm 3

Một lớp dùng `super()`, lớp khác lại gọi trực tiếp class cha.

Điều này phá vỡ Cooperative Inheritance.

---

# 22. Tổng kết

| Khái niệm | Ý nghĩa |
| --- | --- |
| Multiple Inheritance | Kế thừa nhiều lớp |
| Diamond Problem | Một tổ tiên chung có nhiều đường đi |
| C3 Linearization | Thuật toán tạo MRO |
| MRO | Thứ tự tra cứu method |
| `super()` | Chuyển tiếp theo MRO |
| Cooperative Inheritance | Mọi lớp cùng dùng `super()` để phối hợp |

---

# Bài tập thực hành

## Bài 1

Tạo:

```text-x-trilium-auto
class A:
    def hello(self):
        print("A")
```

```text-x-trilium-auto
class B(A):
    def hello(self):
        print("B")
        super().hello()
```

```text-x-trilium-auto
class C(A):
    def hello(self):
        print("C")
        super().hello()
```

```text-x-trilium-auto
class D(B, C):
    def hello(self):
        print("D")
        super().hello()
```

Thực hiện:

```text-x-trilium-auto
D().hello()
```

1. Dự đoán kết quả.
2. In `D.mro()`.
3. Giải thích từng bước Python gọi `super()`.

---

## Bài 2

Viết ba mixin:

- `LoggingMixin`
- `TimingMixin`
- `AuthenticationMixin`

Mỗi mixin có phương thức `process()` in tên của mình rồi gọi `super().process()`.

Tạo lớp:

```text-x-trilium-auto
class App(
    LoggingMixin,
    TimingMixin,
    AuthenticationMixin,
    Base
):
    pass
```

Quan sát thứ tự thực thi và so sánh với MRO.

---

## Bài 3

Lấy ví dụ `TruyenFull` ở trên.

1. Thêm một `HeaderMixin` cũng override `fetch()`.
2. In `TruyenFull.mro()`.
3. Dự đoán thứ tự các thông báo được in ra.
4. Thử thay đổi thứ tự các mixin trong danh sách kế thừa và quan sát sự khác biệt.

---

## Bài 4 (Thử thách)

Tự cài đặt một sơ đồ kế thừa hình kim cương:

```text-x-trilium-auto
        Base
       /    \
      A      B
       \    /
         C
```

Trong mỗi `__init__()`:

- In tên lớp.
- Gọi `super().__init__()`.

Sau đó:

1. In `C.mro()`.
2. Giải thích vì sao `Base.__init__()` chỉ chạy **một lần**.

---

# Chuẩn bị cho Buổi 11

Ở buổi tiếp theo, chúng ta sẽ học một chủ đề cực kỳ quan trọng trong thiết kế phần mềm Python:

# Mixins, Composition, Aggregation và Delegation

Đây là phần giúp trả lời những câu hỏi như:

- Khi nào **không nên dùng kế thừa**?
- Vì sao "Composition over Inheritance" là một nguyên tắc nổi tiếng?
- Mixin khác lớp cơ sở (base class) ở điểm nào?
- Django, Flask, PySide6 và hệ thống plugin crawler của bạn áp dụng các kỹ thuật này như thế nào?

Đây là kiến thức quyết định chất lượng kiến trúc của các dự án Python lớn.