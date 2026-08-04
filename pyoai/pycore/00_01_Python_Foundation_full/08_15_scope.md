# Giai đoạn 1 – Python Foundation

# Buổi 15. Scope (Phạm vi biến)

> Đây là một trong những chủ đề quan trọng nhất để hiểu **Python hoạt động như thế nào**. Rất nhiều lỗi khó tìm của người mới học đều liên quan đến **Scope (phạm vi biến)**. Nếu nắm vững buổi học này, bạn sẽ dễ dàng học các chủ đề nâng cao như **Closure**, **Decorator**, **Class**, **Context Manager** và **Framework Design**.

---

# Mục tiêu

Sau buổi học này, bạn sẽ:

* Hiểu Scope là gì.
* Phân biệt Local Scope và Global Scope.
* Hiểu Namespace.
* Hiểu quy tắc LEGB.
* Biết sử dụng `global`.
* Biết sử dụng `nonlocal`.
* Hiểu Variable Shadowing.
* Biết các nguyên tắc thiết kế code liên quan đến Scope.

---

# 1. Scope là gì?

**Scope (phạm vi)** là nơi một biến có thể được truy cập.

Ví dụ:

```python
x = 10

print(x)
```

Ở đây:

```python
x
```

được truy cập ở mọi nơi trong file.

---

Ví dụ khác:

```python
def hello():
    name = "Python"

    print(name)
```

Biến

```python
name
```

chỉ tồn tại bên trong hàm.

Đó là Scope.

---

# 2. Namespace là gì?

Trước khi học Scope, cần hiểu Namespace.

Namespace là **vùng lưu trữ tên (name) và đối tượng (object)**.

Ví dụ:

```python
age = 20
```

Python lưu:

```text
Tên          Giá trị
-----------------------
age   ───►   20
```

Một Namespace giống như một "từ điển":

```python
{"age": 20, "name": "An"}
```

Python quản lý biến thông qua Namespace.

---

# 3. Global Scope

Biến khai báo ngoài hàm.

```python
name = "Python"


def show():
    print(name)


show()
```

Kết quả:

```text
Python
```

Biến `name` thuộc Global Scope.

---

# 4. Local Scope

Biến tạo trong hàm.

```python
def hello():
    language = "Python"

    print(language)


hello()
```

Kết quả:

```text
Python
```

---

Nếu:

```python
print(language)
```

Lỗi:

```text
NameError
```

Vì biến chỉ tồn tại trong hàm.

---

# 5. Local Variable

```python
def test():

    x = 100

    print(x)


test()
```

`x`

chỉ tồn tại trong lời gọi hàm đó.

Sau khi hàm kết thúc:

```text
x
```

biến mất.

---

# 6. Global Variable

```python
x = 100


def show():
    print(x)


show()

print(x)
```

Kết quả:

```text
100
100
```

---

# 7. Variable Shadowing

Ví dụ:

```python
name = "Python"


def show():

    name = "Java"

    print(name)


show()

print(name)
```

Kết quả:

```text
Java
Python
```

Biến trong hàm **che khuất (shadow)** biến toàn cục.

---

# 8. Sửa Global Variable

Ví dụ:

```python
count = 0


def increase():

    count = count + 1
```

Lỗi:

```text
UnboundLocalError
```

Vì Python nghĩ:

```python
count
```

là biến cục bộ.

---

Muốn sửa Global:

```python
count = 0


def increase():
    global count

    count += 1


increase()

print(count)
```

Kết quả:

```text
1
```

---

# 9. Từ khóa `global`

Cú pháp:

```python
global variable_name
```

Ví dụ:

```python
score = 10


def update():
    global score

    score = 20


update()

print(score)
```

Kết quả:

```text
20
```

---

# 10. Có nên dùng `global`?

**Không nên** nếu không thật sự cần.

Ví dụ không tốt:

```python
balance = 1000


def withdraw():

    global balance

    balance -= 100
```

Khó kiểm soát.

---

Nên:

```python
def withdraw(balance, amount):
    return balance - amount


balance = withdraw(balance, 100)
```

Dễ kiểm thử hơn.

---

# 11. Hàm lồng nhau

```python
def outer():

    def inner():
        print("Hello")

    inner()


outer()
```

---

# 12. Outer Scope

```python
def outer():

    name = "Python"

    def inner():
        print(name)

    inner()


outer()
```

Kết quả:

```text
Python
```

`inner()` truy cập được biến của `outer()`.

---

# 13. `nonlocal`

Ví dụ:

```python
def outer():

    count = 0

    def inner():

        nonlocal count

        count += 1

        print(count)

    inner()


outer()
```

Kết quả:

```text
1
```

`nonlocal` sửa biến của hàm bao ngoài, **không phải biến toàn cục**.

---

# 14. Nếu không dùng `nonlocal`

```python
def outer():

    count = 0

    def inner():

        count += 1
```

Lỗi:

```text
UnboundLocalError
```

---

# 15. Quy tắc LEGB

Python tìm biến theo thứ tự:

```text
L
↓

E
↓

G
↓

B
```

---

## L = Local

Biến trong hàm hiện tại.

---

## E = Enclosing

Biến trong hàm bao ngoài.

---

## G = Global

Biến toàn cục.

---

## B = Built-in

Biến có sẵn của Python.

Ví dụ:

```python
print(len("Python"))
```

`len`

đến từ Built-in Namespace.

---

# 16. Ví dụ LEGB

```python
x = "Global"


def outer():

    x = "Outer"

    def inner():

        x = "Inner"

        print(x)

    inner()


outer()
```

Kết quả:

```text
Inner
```

Python tìm:

```
Local ✓
```

nên dừng.

---

Ví dụ:

```python
x = "Global"


def outer():

    x = "Outer"

    def inner():

        print(x)

    inner()


outer()
```

Kết quả:

```text
Outer
```

Python:

```
Local ✗

↓

Enclosing ✓
```

---

Ví dụ:

```python
x = "Global"


def show():
    print(x)


show()
```

Kết quả:

```text
Global
```

---

Ví dụ Built-in:

```python
print(len("ABC"))
```

Python:

```
Local ✗

↓

Enclosing ✗

↓

Global ✗

↓

Built-in ✓
```

---

# 17. Xem Global Namespace

```python
name = "Python"

print(globals())
```

Kết quả (rút gọn):

```python
{
    "name": "Python",
    ...
}
```

---

# 18. Xem Local Namespace

```python
def test():

    age = 20

    city = "Huế"

    print(locals())


test()
```

Kết quả:

```python
{"age": 20, "city": "Huế"}
```

---

# 19. Built-in Namespace

```python
print(abs(-10))

print(max(1, 2, 3))
```

Các hàm:

* `len`
* `abs`
* `sum`
* `min`
* `max`

đều thuộc Built-in Namespace.

---

# 20. Những lỗi thường gặp

## Lỗi 1

```python
count = 0


def update():
    count += 1
```

Sai.

Phải dùng:

```python
global count
```

hoặc thiết kế lại hàm.

---

## Lỗi 2

Shadowing

```python
sum = 100

print(sum([1, 2, 3]))
```

Lỗi:

```text
TypeError
```

Vì bạn đã ghi đè hàm `sum()` bằng biến `sum`.

Không nên đặt tên biến là:

```text
list
dict
set
str
int
sum
max
min
input
print
```

---

## Lỗi 3

Dùng quá nhiều Global Variable.

Đây là một trong những nguyên nhân khiến chương trình khó bảo trì.

---

# 21. Best Practices

## Ưu tiên truyền tham số

Không nên:

```python
tax = 0.1


def calculate(price):
    return price * tax
```

Nên:

```python
def calculate(price, tax):
    return price * tax
```

---

## Hạn chế `global`

Chỉ dùng khi thực sự cần, ví dụ:

* Bộ đếm toàn cục.
* Cấu hình chương trình.
* Singleton (nâng cao).

---

## Đặt tên rõ ràng

```python
total_price
```

Tốt hơn:

```python
x
```

---

# 22. Ví dụ thực tế

### Bộ đếm số lần gọi hàm

```python
counter = 0


def visit():
    global counter

    counter += 1

    print(f"Đã truy cập {counter} lần")


visit()
visit()
visit()
```

Kết quả:

```text
Đã truy cập 1 lần
Đã truy cập 2 lần
Đã truy cập 3 lần
```

---

### Sử dụng `nonlocal`

```python
def create_counter():
    count = 0

    def increment():
        nonlocal count
        count += 1
        return count

    return increment


counter = create_counter()

print(counter())
print(counter())
print(counter())
```

Kết quả:

```text
1
2
3
```

Đây là nền tảng của **Closure**, sẽ học ở giai đoạn Intermediate.

---

# 23. Bài tập thực hành

## Bài 1

Cho:

```python
x = 100
```

Viết hàm in giá trị của `x` mà không truyền tham số.

---

## Bài 2

Viết chương trình minh họa sự khác nhau giữa:

* Global Variable.
* Local Variable.

---

## Bài 3

Viết chương trình dùng `global` để đếm số lần gọi hàm.

---

## Bài 4

Viết hàm lồng nhau.

Hàm trong truy cập biến của hàm ngoài.

---

## Bài 5

Viết hàm `create_counter()` sử dụng `nonlocal`.

Mỗi lần gọi:

```python
counter()
```

sẽ tăng thêm 1.

---

# 24. Tổng kết

Trong buổi học này, bạn đã học:

* Scope và Namespace.
* Local Scope và Global Scope.
* Variable Shadowing.
* Từ khóa `global` và `nonlocal`.
* Quy tắc tìm kiếm biến **LEGB**.
* Hàm `globals()` và `locals()`.
* Các nguyên tắc thiết kế hàm để tránh phụ thuộc vào biến toàn cục.

---

# Chuẩn bị cho Buổi 16

Buổi tiếp theo, chúng ta sẽ học **Lambda Function**, bao gồm:

* Hàm vô danh (`lambda`).
* Cú pháp và cách hoạt động.
* Khi nào nên dùng và không nên dùng `lambda`.
* Kết hợp `lambda` với `sorted()`, `map()`, `filter()`, `max()`, `min()`.
* So sánh `lambda` với hàm thông thường (`def`).
* Các ví dụ thực tế và những lỗi thường gặp. Đây là nền tảng để học lập trình hàm (Functional Programming) trong Python.
