# Buổi 3: Vòng đời của Object – `__new__`, `__init__` và quá trình tạo đối tượng

Đây là một trong những chủ đề quan trọng nhất của OOP Python. Sau buổi này, bạn sẽ hiểu điều gì thực sự xảy ra khi viết:

```text-x-trilium-auto
dog = Dog("Lucky")
```

Nhiều lập trình viên nghĩ Python chỉ gọi `__init__()`. Thực tế, trước đó Python đã thực hiện nhiều bước.

---

# Mục tiêu của buổi học

Sau buổi này bạn sẽ hiểu:

- Object được tạo như thế nào.
- Vai trò của `__new__`.
- Vai trò của `__init__`.
- Tại sao `__new__` luôn chạy trước `__init__`.
- Khi nào cần override `__new__`.
- Immutable object được tạo ra như thế nào.
- Luồng tạo object trong CPython (ở mức khái niệm).

---

# 1. Khi gọi `Dog()`, chuyện gì xảy ra?

Ví dụ:

```text-x-trilium-auto
class Dog:
    def __init__(self, name):
        self.name = name

dog = Dog("Lucky")
```

Nhiều người tưởng Python làm:

```text-x-trilium-auto
Dog()

↓

__init__()

↓

Object
```

Thực tế là:

```text-x-trilium-auto
Dog()

↓

type.__call__()

↓

__new__()

↓

Object được cấp phát

↓

__init__()

↓

Object hoàn chỉnh

↓

Trả về biến dog
```

**Điểm mấu chốt:** `Dog()` không trực tiếp gọi `__init__`. Lời gọi đầu tiên là đến `type.__call__()` vì `Dog` là một object của lớp `type`.

---

# 2. Ai gọi `__new__` và `__init__`?

Hãy nhớ từ buổi 2:

```text-x-trilium-auto
class Dog:
    pass

print(type(Dog))
```

Kết quả:

```text-x-trilium-auto
<class 'type'>
```

`Dog` là instance của `type`.

Khi viết:

```text-x-trilium-auto
Dog()
```

Python thực chất làm gần giống:

```text-x-trilium-auto
type.__call__(Dog)
```

Bên trong `type.__call__` (mô hình đơn giản):

```text-x-trilium-auto
obj = Dog.__new__(Dog)

if isinstance(obj, Dog):
    Dog.__init__(obj)

return obj
```

Đây chính là quy trình tạo object.

---

# 3. `__new__` là gì?

`__new__` chịu trách nhiệm:

- Cấp phát bộ nhớ.
- Tạo object mới.
- Trả về object.

Ví dụ:

```text-x-trilium-auto
class Dog:

    def __new__(cls):
        print("new")

        obj = super().__new__(cls)

        return obj

d = Dog()
```

Kết quả:

```text-x-trilium-auto
new
```

Lúc này:

```text-x-trilium-auto
Dog()

↓

__new__()

↓

Object mới
```

---

# 4. `__init__` làm gì?

`__init__` **không tạo object**.

Nó chỉ **khởi tạo (initialize)** object đã được tạo trước đó.

Ví dụ:

```text-x-trilium-auto
class Dog:

    def __new__(cls):
        print("Creating object")
        return super().__new__(cls)

    def __init__(self):
        print("Initializing object")

Dog()
```

Kết quả:

```text-x-trilium-auto
Creating object
Initializing object
```

---

# 5. Minh họa trực quan

```text-x-trilium-auto
Dog()

        │

        ▼

+-----------------+
| type.__call__() |
+-----------------+

        │

        ▼

Dog.__new__()

        │

        ▼

+----------------+
| Object mới     |
+----------------+

        │

        ▼

Dog.__init__()

        │

        ▼

Object sẵn sàng sử dụng
```

---

# 6. Chứng minh `__new__` chạy trước

```text-x-trilium-auto
class Dog:

    def __new__(cls):
        print("1. __new__")
        return super().__new__(cls)

    def __init__(self):
        print("2. __init__")

Dog()
```

Kết quả:

```text-x-trilium-auto
1. __new__
2. __init__
```

---

# 7. Nếu `__new__` không trả về object?

```text-x-trilium-auto
class Dog:

    def __new__(cls):
        print("Creating...")
        return None

    def __init__(self):
        print("Init")

Dog()
```

Kết quả:

```text-x-trilium-auto
Creating...
```

`__init__` **không được gọi**.

Lý do:

```text-x-trilium-auto
Không có object

↓

Không có gì để khởi tạo
```

Đây là chi tiết rất quan trọng.

---

# 8. `__init__` không được trả về giá trị

Sai:

```text-x-trilium-auto
class Dog:

    def __init__(self):
        return 10
```

Kết quả:

```text-x-trilium-auto
TypeError:
__init__() should return None
```

Vì `__init__` chỉ dùng để khởi tạo object đã tồn tại.

---

# 9. `__new__` phải trả về object

Đúng:

```text-x-trilium-auto
class Dog:

    def __new__(cls):
        return super().__new__(cls)
```

Sai:

```text-x-trilium-auto
class Dog:

    def __new__(cls):
        return 10
```

Lúc này:

```text-x-trilium-auto
d = Dog()
```

Thì:

```text-x-trilium-auto
print(d)
```

Kết quả:

```text-x-trilium-auto
10
```

Tức là biến `d` không còn là `Dog` nữa mà là một `int`.

Đây là bằng chứng cho thấy `__new__` quyết định **object nào sẽ được trả về**.

---

# 10. Tại sao immutable phải dùng `__new__`?

Ví dụ:

```text-x-trilium-auto
x = 5
```

Hay:

```text-x-trilium-auto
s = "Hello"
```

Sau khi tạo:

```text-x-trilium-auto
int

5
```

Bạn không thể sửa:

```text-x-trilium-auto
x.value = 10
```

Không thể.

Vì object immutable phải được quyết định **ngay lúc tạo**, nên việc khởi tạo dữ liệu diễn ra trong `__new__`, không phải `__init__`.

Đó là lý do khi kế thừa các kiểu immutable (`int`, `str`, `tuple`...), bạn thường phải override `__new__`.

---

# 11. Ví dụ kế thừa `int`

```text-x-trilium-auto
class PositiveInt(int):

    def __new__(cls, value):
        if value < 0:
            value = 0

        return super().__new__(cls, value)
```

Thử:

```text-x-trilium-auto
x = PositiveInt(-5)

print(x)
```

Kết quả:

```text-x-trilium-auto
0
```

Ở đây, giá trị đã được quyết định trong `__new__`.

---

# 12. Luồng tạo object trong CPython (mức khái niệm)

```text-x-trilium-auto
Dog()

↓

type.__call__()

↓

Dog.__new__()

↓

PyObject_New()

↓

Heap Memory

↓

Object

↓

Dog.__init__()

↓

Return
```

Trong mã nguồn CPython, việc cấp phát bộ nhớ được thực hiện ở tầng C thông qua các hàm như `PyObject_New` hoặc các API tương đương. Chúng ta chưa cần đi sâu vào mã C, chỉ cần hiểu rằng `__new__` là nơi "xin" một vùng nhớ cho object.

---

# 13. `id()` chứng minh object được tạo trước

```text-x-trilium-auto
class Dog:

    def __new__(cls):
        obj = super().__new__(cls)
        print(id(obj))
        return obj

    def __init__(self):
        print(id(self))

Dog()
```

Ví dụ kết quả:

```text-x-trilium-auto
4378202400
4378202400
```

Hai giá trị giống nhau.

Điều này chứng minh:

```text-x-trilium-auto
__new__

↓

Object

↓

__init__
```

`__init__` nhận đúng object mà `__new__` đã tạo.

---

# 14. Tóm tắt

| Thành phần | Vai trò |
| --- | --- |
| `type.__call__` | Điều phối quá trình tạo object |
| `__new__` | Tạo và trả về object mới |
| `__init__` | Khởi tạo object đã tồn tại |
| `return None` trong `__new__` | `__init__` sẽ không chạy |
| `return` trong `__init__` | Gây `TypeError` |

---

# Ví dụ tổng hợp

```text-x-trilium-auto
class Dog:
    def __new__(cls, name):
        print("[1] __new__")
        obj = super().__new__(cls)
        print(f"Object id trong __new__: {id(obj)}")
        return obj

    def __init__(self, name):
        print("[2] __init__")
        print(f"Object id trong __init__: {id(self)}")
        self.name = name

dog = Dog("Lucky")

print("[3] Hoàn thành")
print(dog.name)
```

**Kết quả mẫu:**

```text-x-trilium-auto
[1] __new__
Object id trong __new__: 4389202192
[2] __init__
Object id trong __init__: 4389202192
[3] Hoàn thành
Lucky
```

---

# Bài tập thực hành

## Bài 1

Viết lớp `Student` có cả `__new__` và `__init__`. In ra thứ tự các bước để xác nhận `__new__` luôn chạy trước.

---

## Bài 2

Trong `__new__`, in `id(obj)`. Trong `__init__`, in `id(self)`. Kiểm tra xem hai giá trị có giống nhau không và giải thích.

---

## Bài 3

Tạo lớp `PositiveFloat(float)` sao cho nếu truyền giá trị âm thì object luôn có giá trị `0.0`. Gợi ý: override `__new__`.

---

## Bài 4 (Thử thách)

Viết một lớp `Singleton` đơn giản bằng cách override `__new__`, đảm bảo rằng dù gọi constructor bao nhiêu lần thì chỉ có **một object duy nhất** được tạo. Đây sẽ là cầu nối rất tốt sang các buổi sau về **class variable**, **attribute lookup** và **design pattern**.