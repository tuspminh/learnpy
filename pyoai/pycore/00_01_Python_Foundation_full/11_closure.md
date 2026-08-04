# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 11: Làm chủ Scope, Namespace và Closure (Hiểu cách Python tìm biến)

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Hiểu chính xác **Namespace** là gì.
> - Hiểu **Scope** hoạt động như thế nào.
> - Thành thạo quy tắc **LEGB**.
> - Phân biệt `global` và `nonlocal`.
> - Hiểu Closure.
> - Hiểu vì sao Decorator hoạt động.
> - Tránh các lỗi rất phổ biến liên quan đến biến.

---

# 1. Mở đầu

Một trong những câu hỏi quan trọng nhất trong Python là:

> **Khi bạn viết tên một biến, Python tìm biến đó ở đâu?**

Ví dụ:

```text-x-trilium-auto
name = "Python"

def hello():
    print(name)

hello()
```

Tại sao `hello()` lại in được `"Python"`?

Trong khi:

```text-x-trilium-auto
def hello():
    x = 10

print(x)
```

lại báo lỗi?

Để trả lời, chúng ta cần hiểu **Namespace** và **Scope**.

---

# 2. Namespace là gì?

Namespace giống như **một cuốn danh bạ**.

Ví dụ:

```text-x-trilium-auto
name = "An"
age = 20
```

Python lưu:

```text-x-trilium-auto
Tên      Giá trị
-----------------
name -> "An"
age  -> 20
```

Đó chính là một Namespace.

Nói đơn giản:

> Namespace là nơi lưu các tên (name) và giá trị (object) tương ứng.

---

## Ví dụ

```text-x-trilium-auto
x = 100
```

Python tạo:

```text-x-trilium-auto
"x"
 ↓
100
```

Tên và giá trị được liên kết trong Namespace.

---

# 3. Scope là gì?

Scope là:

> **Phạm vi mà một biến có thể được truy cập.**

Ví dụ:

```text-x-trilium-auto
def test():
    x = 100
    print(x)
```

Ở đây:

```text-x-trilium-auto
x
```

chỉ tồn tại trong hàm.

Ra ngoài:

```text-x-trilium-auto
print(x)
```

Lỗi:

```text-x-trilium-auto
NameError
```

---

# 4. Có bao nhiêu loại Scope?

Python có 4 cấp Scope.

Được nhớ bằng:

# LEGB

```text-x-trilium-auto
L
↓

Local

↓

Enclosing

↓

Global

↓

Built-in
```

Python sẽ tìm biến theo đúng thứ tự này.

---

# 5. Local Scope

Ví dụ:

```text-x-trilium-auto
def hello():
    message = "Hello"

    print(message)

hello()
```

`message` chỉ tồn tại trong hàm.

Ra ngoài:

```text-x-trilium-auto
print(message)
```

Lỗi.

---

## Hình dung

```text-x-trilium-auto
Global

↓

hello()

↓

message
```

`message` chỉ sống trong `hello()`.

---

# 6. Global Scope

Ví dụ:

```text-x-trilium-auto
language = "Python"

def show():
    print(language)

show()
```

Python tìm:

```text-x-trilium-auto
show()

↓

language ?

↓

Không có

↓

Ra Global

↓

Tìm thấy
```

---

# 7. Built-in Scope

Python có rất nhiều hàm dựng sẵn.

Ví dụ:

```text-x-trilium-auto
print()
len()
sum()
max()
min()
```

Chúng thuộc Built-in Scope.

Ví dụ:

```text-x-trilium-auto
numbers = [1, 2, 3]

print(len(numbers))
```

Python tìm:

```text-x-trilium-auto
Local

↓

Global

↓

Built-in

↓

len
```

---

# 8. Enclosing Scope

Đây là Scope ít người hiểu.

Ví dụ:

```text-x-trilium-auto
def outer():
    x = 100

    def inner():
        print(x)

    inner()

outer()
```

Kết quả:

```text-x-trilium-auto
100
```

Python tìm:

```text-x-trilium-auto
inner()

↓

Local

↓

Không có

↓

Outer

↓

Có x
```

Đây gọi là:

> Enclosing Scope.

---

# 9. LEGB Rule

Đây là quy tắc quan trọng nhất.

Python tìm biến theo thứ tự:

```text-x-trilium-auto
Local

↓

Enclosing

↓

Global

↓

Built-in
```

Ví dụ:

```text-x-trilium-auto
name = "Global"

def outer():
    name = "Outer"

    def inner():
        name = "Inner"

        print(name)

    inner()

outer()
```

Kết quả:

```text-x-trilium-auto
Inner
```

Vì Local được ưu tiên.

---

Nếu bỏ:

```text-x-trilium-auto
name = "Inner"
```

Kết quả:

```text-x-trilium-auto
Outer
```

Nếu bỏ tiếp:

```text-x-trilium-auto
name = "Outer"
```

Kết quả:

```text-x-trilium-auto
Global
```

---

# 10. Global Keyword

Ví dụ:

```text-x-trilium-auto
count = 0

def increase():
    count = count + 1
```

Lỗi:

```text-x-trilium-auto
UnboundLocalError
```

Tại sao?

Python nghĩ:

```text-x-trilium-auto
count
```

là biến Local.

---

Muốn sửa Global:

```text-x-trilium-auto
count = 0

def increase():
    global count
    count += 1

increase()

print(count)
```

Kết quả:

```text-x-trilium-auto
1
```

---

## Có nên dùng `global`?

Trong các dự án chuyên nghiệp:

> Hầu như **không nên**.

Vì:

- Khó debug.
- Khó test.
- Khó bảo trì.
- Dễ sinh lỗi khi nhiều hàm cùng sửa một biến.

Thay vào đó, hãy truyền dữ liệu qua tham số và trả về bằng `return` hoặc dùng đối tượng (class) khi phù hợp.

---

# 11. Nonlocal Keyword

Ví dụ:

```text-x-trilium-auto
def outer():
    count = 0

    def inner():
        nonlocal count
        count += 1
        print(count)

    inner()
    inner()

outer()
```

Kết quả:

```text-x-trilium-auto
1
2
```

`nonlocal`

không tìm Global.

Nó tìm Scope gần nhất bên ngoài.

---

# 12. Closure là gì?

Ví dụ:

```text-x-trilium-auto
def outer():

    message = "Hello"

    def inner():
        print(message)

    return inner
```

Sau đó:

```text-x-trilium-auto
f = outer()

f()
```

Kết quả:

```text-x-trilium-auto
Hello
```

Điều kỳ lạ:

`outer()`

đã chạy xong.

Tại sao:

```text-x-trilium-auto
message
```

vẫn tồn tại?

Đó chính là:

# Closure

---

# 13. Hiểu Closure

Python lưu:

```text-x-trilium-auto
inner

+

message
```

thành một gói.

Giống như:

```text-x-trilium-auto
Function

+

Data
```

được mang theo cùng nhau.

---

# 14. Ví dụ thực tế

```text-x-trilium-auto
def multiplier(x):

    def multiply(y):
        return x * y

    return multiply
```

Tạo:

```text-x-trilium-auto
double = multiplier(2)

triple = multiplier(3)
```

Gọi:

```text-x-trilium-auto
print(double(10))
print(triple(10))
```

Kết quả:

```text-x-trilium-auto
20

30
```

Mỗi hàm ghi nhớ giá trị `x` riêng của mình.

---

# 15. Closure dùng ở đâu?

Closure xuất hiện rất nhiều trong:

- Decorator
- Callback
- GUI
- Web Framework
- Async Programming
- Dependency Injection

---

# 16. Shadowing (Che khuất biến)

Ví dụ:

```text-x-trilium-auto
name = "Global"

def test():
    name = "Local"

    print(name)
```

Kết quả:

```text-x-trilium-auto
Local
```

Biến Local che khuất Global.

Đây gọi là:

Variable Shadowing.

---

# 17. Kiểm tra Namespace

Có thể dùng:

```text-x-trilium-auto
globals()
```

Ví dụ:

```text-x-trilium-auto
x = 100

print(globals())
```

Hoặc:

```text-x-trilium-auto
locals()
```

Trong hàm:

```text-x-trilium-auto
def test():
    a = 10
    b = 20

    print(locals())

test()
```

Kết quả:

```text-x-trilium-auto
{'a': 10, 'b': 20}
```

Hai hàm này rất hữu ích khi debug, nhưng hiếm khi được dùng trực tiếp trong mã nghiệp vụ.

---

# 18. Những lỗi phổ biến

## Lỗi 1

```text-x-trilium-auto
count = 0

def test():
    count += 1
```

Lỗi.

Python hiểu:

```text-x-trilium-auto
count
```

là Local.

---

## Lỗi 2

Lạm dụng Global.

```text-x-trilium-auto
global x
```

khắp nơi.

Đây là thói quen rất xấu.

---

## Lỗi 3

Nhầm `nonlocal`

`nonlocal`

không truy cập Global.

Nó chỉ truy cập Scope bên ngoài gần nhất.

---

# 19. Ví dụ thực tế

## Bộ đếm

```text-x-trilium-auto
def counter():

    count = 0

    def increment():
        nonlocal count

        count += 1

        return count

    return increment

c = counter()

print(c())
print(c())
print(c())
```

Kết quả:

```text-x-trilium-auto
1
2
3
```

Đây là một ví dụ kinh điển về Closure.

---

## Logger

```text-x-trilium-auto
def logger(prefix):

    def log(message):
        print(f"[{prefix}] {message}")

    return log

info = logger("INFO")
error = logger("ERROR")

info("Kết nối thành công")
error("Không tìm thấy tệp")
```

Kết quả:

```text-x-trilium-auto
[INFO] Kết nối thành công
[ERROR] Không tìm thấy tệp
```

Mỗi logger "ghi nhớ" `prefix` riêng của mình.

---

# 20. Bài tập thực hành

## Bài 1

Viết hàm:

```text-x-trilium-auto
def outer():
    x = 100

    def inner():
        ...
```

Cho `inner()` in được `x`.

---

## Bài 2

Viết bộ đếm dùng `nonlocal`.

Mỗi lần gọi hàm:

```text-x-trilium-auto
1

2

3

4
```

---

## Bài 3

Viết hàm:

```text-x-trilium-auto
make_power(n)
```

Trả về một hàm tính lũy thừa.

Ví dụ:

```text-x-trilium-auto
square = make_power(2)
cube = make_power(3)

print(square(5))  # 25
print(cube(2))    # 8
```

---

## Bài 4

Viết Logger bằng Closure.

---

## Bài 5

Dùng:

```text-x-trilium-auto
globals()

locals()
```

để quan sát Namespace trong chương trình.

---

# Mini Project: Bộ tạo mã giảm giá (Discount Factory)

Viết hàm:

```text-x-trilium-auto
def discount(percent):
    ...
```

Hàm này trả về một hàm mới dùng để tính giá sau khi giảm.

Ví dụ:

```text-x-trilium-auto
sale10 = discount(10)
sale20 = discount(20)

print(sale10(100000))   # 90000.0
print(sale20(100000))   # 80000.0
```

Yêu cầu:

- Không dùng biến toàn cục.
- Sử dụng Closure để "ghi nhớ" phần trăm giảm giá.

---

# Tổng kết buổi 11

Bạn đã học được:

- ✅ Namespace.
- ✅ Scope.
- ✅ LEGB Rule.
- ✅ Local Scope.
- ✅ Enclosing Scope.
- ✅ Global Scope.
- ✅ Built-in Scope.
- ✅ `global`.
- ✅ `nonlocal`.
- ✅ Closure.
- ✅ Variable Shadowing.
- ✅ `globals()` và `locals()`.

---

# Góc lập trình viên chuyên nghiệp

Hiểu **LEGB** và **Closure** là bước chuyển quan trọng từ người mới học sang lập trình viên Python có nền tảng vững.

Những kiến thức hôm nay là nền móng của nhiều kỹ thuật nâng cao:

- **Decorator**: sử dụng Closure để "bọc" một hàm khác mà vẫn giữ được trạng thái.
- **Callback**: truyền hàm và dữ liệu đi cùng nhau.
- **GUI**: các hàm xử lý sự kiện thường là Closure để ghi nhớ trạng thái giao diện.
- **Web Framework**: nhiều middleware và dependency hoạt động dựa trên Closure.
- **Lập trình bất đồng bộ (asyncio)**: callback và coroutine thường tận dụng phạm vi biến để quản lý ngữ cảnh.

Một lập trình viên Python chuyên nghiệp không chỉ biết viết mã chạy được, mà còn hiểu **Python tìm và quản lý biến như thế nào**. Điều này giúp tránh các lỗi khó phát hiện và thiết kế chương trình rõ ràng hơn.

---

# Chuẩn bị cho Buổi 12

Ở buổi tiếp theo, chúng ta sẽ học **Decorator** từ cơ bản đến chuyên sâu:

- Decorator là gì?
- Vì sao Decorator tồn tại?
- Cách tự xây dựng Decorator.
- Decorator có tham số.
- Nhiều Decorator lồng nhau.
- `functools.wraps`.
- Các Decorator có sẵn như `@property`, `@staticmethod`, `@classmethod`.
- Ứng dụng trong **Flask**, **FastAPI**, **Django**, logging, cache và kiểm tra quyền truy cập.

Đây là một trong những chủ đề đặc trưng và mạnh mẽ nhất của Python, được sử dụng rộng rãi trong các thư viện và framework hiện đại.
