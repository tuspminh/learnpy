# OOP Deep Dive – Buổi 22

# Operator Overloading Deep Dive – Biến Object thành "Kiểu dữ liệu" thực thụ

> Đây là một trong những khả năng mạnh nhất của OOP Python.

Sau buổi này, bạn sẽ hiểu vì sao có thể viết:

```text-x-trilium-auto
from pathlib import Path

path = Path("/home") / "user" / "file.txt"
```

hoặc

```text-x-trilium-auto
import numpy as np

c = a + b d = a @ b
```

hoặc

```text-x-trilium-auto
from sqlalchemy import select

query = users & active_users
```

Trong khi:

- `+`
- `-`
- `*`
- `/`
- `@`
- `&`
- `|`
- `+=`

đều chỉ là **toán tử của Python**.

Python không "biết" cộng hai object của bạn.

Nó chỉ gọi **Magic Method** tương ứng.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- Operator Overloading
- `__add__()`
- `__sub__()`
- `__mul__()`
- `__truediv__()`
- `__floordiv__()`
- `__mod__()`
- `__pow__()`
- `__matmul__()`
- `__iadd__()`
- `__radd__()`

---

# 1. Operator Overloading là gì?

Ví dụ

```text-x-trilium-auto
a = 5 b = 3

print(a + b)
```

Python thực chất gọi

```text-x-trilium-auto
a.__add__(b)
```

Tương tự

```text-x-trilium-auto
a - b
```

↓

```text-x-trilium-auto
a.__sub__(b)
```

---

# 2. `__add__()`

Ví dụ

```text-x-trilium-auto
class Money:

    def __init__(self, amount):
        self.amount = amount

    def __add__(self, other):
        return Money(self.amount + other.amount)

    def __repr__(self):
        return f"Money({self.amount})"
```

---

```text-x-trilium-auto
a = Money(100)
b = Money(50)

print(a + b)
```

↓

```text-x-trilium-auto
Money(150)
```

---

# 3. Không nhất thiết trả về cùng kiểu

Ví dụ

```text-x-trilium-auto
class Score:

    def __init__(self, value):
        self.value = value

    def __add__(self, other):
        return self.value + other.value
```

---

```text-x-trilium-auto
Score(10) + Score(20)
```

↓

```text-x-trilium-auto
30
```

Tuy nhiên, trong đa số trường hợp, việc trả về cùng kiểu (`Score`) sẽ giúp API nhất quán hơn.

---

# 4. Hỗ trợ nhiều kiểu

```text-x-trilium-auto
class Money:

    def __init__(self, amount):
        self.amount = amount

    def __add__(self, other):

        if isinstance(other, Money):
            return Money(
                self.amount + other.amount
            )

        if isinstance(other, int):
            return Money(
                self.amount + other
            )

        return NotImplemented
```

---

```text-x-trilium-auto
Money(100) + 50
```

↓

```text-x-trilium-auto
Money(150)
```

---

# 5. Tại sao trả về `NotImplemented`?

Rất nhiều người viết:

```text-x-trilium-auto
raise TypeError
```

Không nên.

Nên:

```text-x-trilium-auto
return NotImplemented
```

Vì Python sẽ thử:

```text-x-trilium-auto
other.__radd__(self)
```

Đây là cơ chế chuẩn của Data Model.

---

# 6. `__radd__()`

Ví dụ

```text-x-trilium-auto
class Money:

    def __radd__(self, other):

        return Money(
            other + self.amount
        )
```

---

```text-x-trilium-auto
100 + Money(50)
```

Python làm:

```text-x-trilium-auto
int.__add__(Money)

↓

Không biết

↓

Money.__radd__(100)
```

↓

```text-x-trilium-auto
Money(150)
```

---

# 7. Thứ tự ưu tiên

```text-x-trilium-auto
a + b

↓

a.__add__(b)

↓

NotImplemented

↓

b.__radd__(a)
```

Đây là cơ chế rất quan trọng khi thiết kế class tương tác với kiểu dữ liệu khác.

---

# 8. `__iadd__()`

Đây là:

```text-x-trilium-auto
+=
```

Ví dụ

```text-x-trilium-auto
a += b
```

Python ưu tiên gọi:

```text-x-trilium-auto
a.__iadd__(b)
```

Nếu không có:

↓

```text-x-trilium-auto
a = a + b
```

---

Ví dụ

```text-x-trilium-auto
class Counter:

    def __init__(self):
        self.value = 0

    def __iadd__(self, other):

        self.value += other

        return self
```

---

```text-x-trilium-auto
c = Counter()

c += 5
```

↓

```text-x-trilium-auto
value = 5
```

---

# 9. `__sub__()`

```text-x-trilium-auto
class Money:

    def __sub__(self, other):

        return Money(
            self.amount - other.amount
        )
```

---

```text-x-trilium-auto
Money(100) - Money(40)
```

↓

```text-x-trilium-auto
Money(60)
```

---

# 10. `__mul__()`

```text-x-trilium-auto
class Vector:

    def __init__(self, x):
        self.x = x

    def __mul__(self, n):

        return Vector(
            self.x * n
        )

    def __repr__(self):
        return f"Vector({self.x})"
```

---

```text-x-trilium-auto
Vector(5) * 3
```

↓

```text-x-trilium-auto
Vector(15)
```

---

# 11. `__truediv__()`

```text-x-trilium-auto
class Money:

    def __truediv__(self, n):

        return Money(
            self.amount / n
        )
```

---

```text-x-trilium-auto
Money(100) / 4
```

↓

```text-x-trilium-auto
Money(25)
```

---

# 12. `__floordiv__()`

```text-x-trilium-auto
Money(100) // 6
```

↓

```text-x-trilium-auto
__floordiv__()
```

Ví dụ

```text-x-trilium-auto
def __floordiv__(self, n):
    return Money(self.amount // n)
```

---

# 13. `__mod__()`

```text-x-trilium-auto
Money(100) % 30
```

↓

```text-x-trilium-auto
__mod__()
```

---

# 14. `__pow__()`

```text-x-trilium-auto
a ** b
```

↓

```text-x-trilium-auto
__pow__()
```

Ví dụ

```text-x-trilium-auto
class Number:

    def __init__(self, value):
        self.value = value

    def __pow__(self, n):

        return Number(
            self.value ** n
        )
```

---

# 15. `__matmul__()`

Đây là toán tử:

```text-x-trilium-auto
@
```

Ví dụ

```text-x-trilium-auto
A @ B
```

↓

Python gọi

```text-x-trilium-auto
A.__matmul__(B)
```

Đây là toán tử được NumPy dùng cho phép nhân ma trận.

---

Ví dụ đơn giản

```text-x-trilium-auto
class Matrix:

    def __init__(self, value):
        self.value = value

    def __matmul__(self, other):

        return Matrix(
            self.value * other.value
        )

    def __repr__(self):
        return f"Matrix({self.value})"
```

---

```text-x-trilium-auto
Matrix(3) @ Matrix(4)
```

↓

```text-x-trilium-auto
Matrix(12)
```

Trong thực tế, phép nhân ma trận sẽ phức tạp hơn nhiều, ví dụ này chỉ nhằm minh họa cơ chế.

---

# 16. Toán tử so sánh

Ngoài các phép toán số học còn có:

```text-x-trilium-auto
< <= > >=
```

Tương ứng

```text-x-trilium-auto
__lt__()
__le__()
__gt__()
__ge__()
```

Ví dụ

```text-x-trilium-auto
class Money:

    def __init__(self, amount):
        self.amount = amount

    def __lt__(self, other):
        return self.amount < other.amount
```

---

```text-x-trilium-auto
Money(10) < Money(20)
```

↓

```text-x-trilium-auto
True
```

---

# 17. Toán tử logic theo bit

Python cho phép overload:

```text-x-trilium-auto
&
|
^
~
<<
>>
```

Tương ứng:

```text-x-trilium-auto
__and__()
__or__()
__xor__()
__invert__()
__lshift__()
__rshift__()
```

SQLAlchemy tận dụng `&` và `|` để kết hợp điều kiện truy vấn.

---

# 18. Áp dụng vào dự án crawler

Giả sử

```text-x-trilium-auto
queue1 + queue2
```

↓

Ghép hai hàng đợi.

```text-x-trilium-auto
class CrawlQueue:

    def __add__(self, other):
        return CrawlQueue(
            self.jobs + other.jobs
        )
```

---

# 19. Ví dụ `NovelCollection`

```text-x-trilium-auto
collection1 + collection2
```

↓

Ghép hai danh sách truyện.

---

```text-x-trilium-auto
collection * 3
```

↓

Lặp ba lần (hoặc tạo ba bản sao tùy thiết kế).

---

# 20. `Path`

Đây là ví dụ nổi tiếng nhất.

```text-x-trilium-auto
from pathlib import Path

path = Path("data") / "novels" / "book.txt"
```

Bạn có thể nghĩ:

```text-x-trilium-auto
"/"

↓

__truediv__()
```

Thực tế, `pathlib.Path` overload toán tử `/` để biểu diễn việc nối đường dẫn, giúp cú pháp rất tự nhiên.

---

# 21. Mini Query Builder

```text-x-trilium-auto
name = Field("name")
age = Field("age")
```

---

```text-x-trilium-auto
query = (name == "Alice") & (age > 18)
```

Ở đây:

- `==` gọi `__eq__()`
- `>` gọi `__gt__()`
- `&` gọi `__and__()`

Kết quả không phải `bool`, mà là một cây biểu thức (expression tree) dùng để sinh SQL.

Đây là ý tưởng cốt lõi của SQLAlchemy.

---

# 22. Bảng tổng hợp

| Toán tử | Magic Method |
| --- | --- |
| `+` | `__add__()` |
| `-` | `__sub__()` |
| `*` | `__mul__()` |
| `/` | `__truediv__()` |
| `//` | `__floordiv__()` |
| `%` | `__mod__()` |
| `**` | `__pow__()` |
| `@` | `__matmul__()` |
| `+=` | `__iadd__()` |
| `a + b` (fallback) | `__radd__()` |

---

# 23. Thiết kế API Pythonic

Thay vì:

```text-x-trilium-auto
queue.merge(other)
```

Bạn có thể cho phép:

```text-x-trilium-auto
queue + other
```

---

Thay vì:

```text-x-trilium-auto
matrix.multiply(other)
```

Có thể dùng:

```text-x-trilium-auto
matrix @ other
```

---

Thay vì:

```text-x-trilium-auto
money.add(100)
```

Có thể dùng:

```text-x-trilium-auto
money + 100
```

Điều này làm API ngắn gọn, tự nhiên và gần với cách Python được thiết kế.

---

# Điều quan trọng nhất cần nhớ

**Operator Overloading không phải để "làm màu".**

Hãy chỉ overload toán tử khi ý nghĩa của nó rõ ràng.

Ví dụ:

- `Money + Money` ✔
- `Vector * Number` ✔
- `Path / "file.txt"` ✔

Nhưng:

- `User + User` ❌ (ý nghĩa không rõ ràng)
- `Novel % Author` ❌

Một API tốt là API mà người đọc có thể **đoán được hành vi của toán tử**.

---

# Bài tập thực hành

## Bài 1

Viết lớp `Vector2D`:

```text-x-trilium-auto
v1 = Vector2D(1, 2)
v2 = Vector2D(3, 4)

print(v1 + v2)
print(v1 - v2)
print(v1 * 2)
```

---

## Bài 2

Viết lớp `Money`:

Hỗ trợ:

```text-x-trilium-auto
Money(100) + Money(50)
Money(100) + 50 50 + Money(100)
Money(100) += Money(20)
```

Hãy triển khai:

- `__add__()`
- `__radd__()`
- `__iadd__()`

và luôn trả về `NotImplemented` khi gặp kiểu dữ liệu không hỗ trợ.

---

## Bài 3

Viết lớp `Matrix2x2`:

Hỗ trợ:

```text-x-trilium-auto
A @ B
```

với phép nhân ma trận 2×2 đúng theo công thức toán học.

---

## Bài 4 (Áp dụng dự án crawler)

Thiết kế các lớp:

- `NovelCollection`
- `CrawlQueue`
- `SearchCondition`

Đề xuất API:

```text-x-trilium-auto
all_novels = collection1 + collection2

queue += retry_queue

condition = (Author == "Kim Dung") & (Views > 1_000_000)

top10 = collection[:10]
```

Hãy xác định magic method nào sẽ được gọi trong từng biểu thức và vì sao cách thiết kế này lại giúp mã nguồn của hệ thống crawler trở nên ngắn gọn, dễ đọc và mang phong cách Pythonic.

---

# Chuẩn bị cho Buổi 23

Từ buổi 23 trở đi, chúng ta sẽ chuyển sang **Protocol và Context Manager nâng cao**, bao gồm:

- `__call__()`
- `__enter__()`
- `__exit__()`
- `with` statement hoạt động như thế nào
- Tự xây dựng Context Manager
- Context Manager bất đồng bộ (`__aenter__()`, `__aexit__()`)
- Decorator Class

Đây là những kỹ thuật được sử dụng rất nhiều trong:

- `open()`
- `sqlite3`
- `requests`
- `asyncio`
- SQLAlchemy
- Django ORM

và sẽ là bước quan trọng để bạn xây dựng các thư viện và framework Python chuyên nghiệp.