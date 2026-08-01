# Python OOP Master – Buổi 12

# Multiple Inheritance (Đa kế thừa) – C3 Linearization, Diamond Problem và MRO

> **Multiple Inheritance (MI)** là một trong những điểm khác biệt lớn giữa Python và nhiều ngôn ngữ OOP khác như Java hay C#. Trong Python, một class có thể kế thừa từ **nhiều class cha** cùng lúc. Đây là tính năng rất mạnh nhưng cũng dễ gây nhầm lẫn nếu không hiểu **Method Resolution Order (MRO)** và **C3 Linearization**.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu Multiple Inheritance là gì.
* Biết cách khai báo class kế thừa nhiều lớp.
* Hiểu Diamond Problem.
* Hiểu Method Resolution Order (MRO).
* Hiểu thuật toán C3 Linearization ở mức thực hành.
* Biết cách phối hợp `super()` trong Multiple Inheritance.
* Biết khi nào nên và không nên sử dụng Multiple Inheritance.

---

# 1. Multiple Inheritance là gì?

Một class kế thừa từ **nhiều class cha**.

```python
class A:
    pass


class B:
    pass


class C(A, B):
    pass
```

Sơ đồ:

```text
      A      B
       \    /
        \  /
         C
```

Class `C` có thể sử dụng thành viên của cả `A` và `B`.

---

# 2. Ví dụ đầu tiên

```python
class Flyable:
    def fly(self):
        print("Flying...")


class Swimmable:
    def swim(self):
        print("Swimming...")


class Duck(Flyable, Swimmable):
    pass


duck = Duck()

duck.fly()
duck.swim()
```

Kết quả:

```text
Flying...
Swimming...
```

`Duck` có cả hai khả năng.

---

# 3. Python tìm method như thế nào?

```python
class A:
    def hello(self):
        print("A")


class B:
    def hello(self):
        print("B")


class C(A, B):
    pass


c = C()

c.hello()
```

Kết quả

```text
A
```

Tại sao?

---

# 4. MRO

Python tra cứu theo

```python
print(C.mro())
```

Kết quả

```text
[
 C,
 A,
 B,
 object
]
```

Python tìm

```text
C

↓

A

↓

B

↓

object
```

Gặp `A.hello()` trước.

---

# 5. Đổi thứ tự

```python
class C(B, A):
    pass
```

MRO

```text
[
 C,
 B,
 A,
 object
]
```

Bây giờ

```python
c.hello()
```

Kết quả

```text
B
```

---

# 6. Diamond Problem

Đây là vấn đề nổi tiếng của OOP.

```text
        A
      /   \
     B     C
      \   /
        D
```

Nếu

```python
A.hello()
```

được định nghĩa.

Khi gọi

```python
d.hello()
```

Python sẽ chọn đường nào?

---

# 7. Ví dụ

```python
class A:
    def hello(self):
        print("A")


class B(A):
    pass


class C(A):
    pass


class D(B, C):
    pass


d = D()

d.hello()
```

Kết quả

```text
A
```

Không có lỗi.

---

# 8. MRO của Diamond

```python
print(D.mro())
```

Kết quả

```text
[
 D,
 B,
 C,
 A,
 object
]
```

Python chỉ đi qua `A` **một lần**.

---

# 9. C3 Linearization

Python dùng thuật toán

```text
C3 Linearization
```

Để tạo MRO sao cho:

* Không lặp class.
* Giữ đúng quan hệ cha-con.
* Giữ thứ tự khai báo.

Ví dụ:

```python
class D(B, C):
    pass
```

MRO luôn là:

```text
D
↓

B
↓

C
↓

A
↓

object
```

---

# 10. `super()` trong Multiple Inheritance

Đây là lý do thực sự của `super()`.

```python
class A:
    def hello(self):
        print("A")


class B(A):
    def hello(self):

        print("B")

        super().hello()


class C(B):
    def hello(self):

        print("C")

        super().hello()


c = C()

c.hello()
```

Kết quả

```text
C
B
A
```

---

# 11. Ví dụ Diamond với `super()`

```python
class A:
    def hello(self):
        print("A")


class B(A):
    def hello(self):

        print("B")

        super().hello()


class C(A):
    def hello(self):

        print("C")

        super().hello()


class D(B, C):
    def hello(self):

        print("D")

        super().hello()


d = D()

d.hello()
```

Kết quả

```text
D
B
C
A
```

Điều đáng chú ý là:

* `A.hello()` chỉ được gọi **một lần**.
* `super()` không gọi "class cha trực tiếp", mà gọi **class kế tiếp trong MRO**.

---

# 12. Nếu gọi trực tiếp class cha

```python
class B(A):
    def hello(self):

        print("B")

        A.hello(self)


class C(A):
    def hello(self):

        print("C")

        A.hello(self)


class D(B, C):
    def hello(self):

        print("D")

        B.hello(self)

        C.hello(self)
```

Kết quả

```text
D
B
A
C
A
```

`A.hello()` bị gọi **hai lần**.

Đây chính là vấn đề mà `super()` giúp giải quyết.

---

# 13. Constructor với Multiple Inheritance

```python
class A:
    def __init__(self):
        print("A")


class B(A):
    def __init__(self):

        print("B")

        super().__init__()


class C(A):
    def __init__(self):

        print("C")

        super().__init__()


class D(B, C):
    def __init__(self):

        print("D")

        super().__init__()


d = D()
```

Kết quả

```text
D
B
C
A
```

---

# 14. Xem MRO

```python
print(D.__mro__)
```

hoặc

```python
print(D.mro())
```

Ví dụ:

```text
[
 D,
 B,
 C,
 A,
 object
]
```

---

# 15. Ví dụ thực tế

```python
class Logger:
    def log(self):
        print("Logging...")


class Timestamp:
    def timestamp(self):
        print("2026-08-01")


class FileManager(Logger, Timestamp):
    def save(self):

        self.log()

        self.timestamp()

        print("File saved.")
```

```python
fm = FileManager()

fm.save()
```

Kết quả

```text
Logging...
2026-08-01
File saved.
```

Đây là ví dụ đơn giản về việc kết hợp nhiều hành vi.

---

# 16. Khi nào nên dùng Multiple Inheritance?

Phù hợp khi kết hợp **nhiều khả năng độc lập**.

Ví dụ:

```text
Printable
```

```text
Serializable
```

```text
Loggable
```

```text
TimestampMixin
```

Các class này thường **không có trạng thái phức tạp**, chỉ bổ sung hành vi.

---

# 17. Khi nào không nên?

Không nên tạo cây kế thừa quá sâu và quá phức tạp.

Ví dụ:

```text
A

↓

B

↓

C

↓

D

↓

E

↓

F
```

Hoặc kết hợp quá nhiều lớp:

```python
class X(A, B, C, D, E): ...
```

Code sẽ khó đọc và khó bảo trì.

---

# 18. Multiple Inheritance vs Composition

Thay vì:

```text
Duck

↓

Flyable

↓

Swimmable
```

Có thể dùng:

```python
class Duck:
    def __init__(self):
        self.fly_engine = FlyEngine()
        self.swim_engine = SwimEngine()
```

Đây là **Composition**, thường linh hoạt hơn khi hành vi có thể thay đổi lúc chạy.

---

# 19. Best Practices

✅ Luôn sử dụng `super()` trong tất cả các class tham gia Multiple Inheritance.

✅ Kiểm tra MRO bằng:

```python
ClassName.mro()
```

khi gặp hành vi khó hiểu.

✅ Chỉ dùng Multiple Inheritance khi các lớp cha đại diện cho **các hành vi độc lập**.

---

# 20. Những lỗi người mới thường gặp

## Lỗi 1: Gọi trực tiếp class cha

```python
A.method(self)
```

Thay vì:

```python
super().method()
```

Điều này có thể làm một số lớp trong MRO bị bỏ qua hoặc bị gọi nhiều lần.

---

## Lỗi 2: Không gọi `super()`

Nếu một lớp trong chuỗi MRO không gọi `super()`, chuỗi sẽ dừng tại đó.

Ví dụ:

```python
class B(A):
    def hello(self):
        print("B")
        # Quên super()
```

`A.hello()` sẽ không bao giờ được gọi.

---

## Lỗi 3: Không hiểu MRO

Đừng đoán `super()` sẽ gọi lớp nào.

Hãy kiểm tra:

```python
print(ClassName.mro())
```

---

# 21. Ví dụ tổng hợp

```python
class A:
    def process(self):
        print("A")


class B(A):
    def process(self):
        print("B")
        super().process()


class C(A):
    def process(self):
        print("C")
        super().process()


class D(B, C):
    def process(self):
        print("D")
        super().process()


d = D()

print("MRO:", [cls.__name__ for cls in D.mro()])
print()

d.process()
```

Kết quả

```text
MRO: ['D', 'B', 'C', 'A', 'object']

D
B
C
A
```

---

# Bài tập

## Bài 1

Tạo các class:

```text
A
B
C(A, B)
```

Mỗi class có method:

```python
hello()
```

In ra tên class và kiểm tra MRO.

---

## Bài 2

Tạo cấu trúc Diamond:

```text
      Animal
      /    \
    Dog    Cat
      \    /
      Hybrid
```

Mỗi class định nghĩa:

```python
identify()
```

Sử dụng `super()` trong tất cả các lớp và quan sát thứ tự gọi.

---

## Bài 3

Viết các class:

* `Logger`
* `Cache`
* `Service(Logger, Cache)`

Mỗi lớp có method `setup()` gọi `super().setup()` nếu phù hợp. Quan sát chuỗi thực thi.

---

## Bài 4

Cho đoạn mã:

```python
class A:
    def show(self):
        print("A")


class B(A):
    def show(self):
        print("B")
        super().show()


class C(A):
    def show(self):
        print("C")
        super().show()


class D(B, C):
    pass
```

Hãy:

1. In `D.mro()`.
2. Dự đoán kết quả của:

```python
D().show()
```

3. Chạy chương trình để kiểm chứng.

---

## Bài 5 (Nâng cao)

Viết hệ thống:

* `Loggable`
* `Validatable`
* `Serializable`

Tạo:

```python
class User(Loggable, Validatable, Serializable): ...
```

Mỗi lớp có phương thức:

```python
initialize()
```

Tất cả đều gọi `super().initialize()`.

Quan sát thứ tự thực thi và giải thích bằng MRO.

---

# Tóm tắt buổi học

* **Multiple Inheritance** cho phép một class kế thừa từ nhiều class cha.
* Python giải quyết xung đột bằng **Method Resolution Order (MRO)** dựa trên **thuật toán C3 Linearization**.
* `super()` luôn gọi **lớp kế tiếp trong MRO**, không phải "class cha trực tiếp".
* Trong cấu trúc Diamond, sử dụng `super()` giúp mỗi phương thức của lớp chung chỉ được gọi **một lần**.
* Multiple Inheritance rất mạnh nhưng nên dùng có chọn lọc; trong nhiều trường hợp, **Composition** hoặc **Mixins** sẽ phù hợp hơn.

> **Buổi 13** chúng ta sẽ học **Mixins**: cách thiết kế các lớp bổ sung hành vi nhỏ gọn, cách phân biệt Mixins với Multiple Inheritance thông thường, quy tắc đặt tên (`*Mixin`), và cách các framework như Django, Flask, SQLAlchemy sử dụng Mixins để mở rộng chức năng mà không làm hệ thống kế thừa trở nên phức tạp.
