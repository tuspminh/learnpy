# Buổi 21. Module trong Python (Deep Dive)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ hiểu:
>
> * Module là gì
> * Tại sao phải chia chương trình thành module
> * Cơ chế `import` hoạt động như thế nào
> * `import` vs `from ... import`
> * Alias (`as`)
> * Module cache (`sys.modules`)
> * Đường dẫn tìm module (`sys.path`)
> * `__name__`
> * `if __name__ == "__main__"`
> * Circular Import
> * Best Practice khi tổ chức module

---

# 1. Module là gì?

Module đơn giản là **một file `.py`**.

Ví dụ

```
math_utils.py
```

```python
PI = 3.14159


def add(a, b):
    return a + b


def sub(a, b):
    return a - b
```

File này chính là một module.

Ta có thể sử dụng ở file khác.

```
main.py
```

```python
import math_utils

print(math_utils.PI)
print(math_utils.add(5, 3))
```

Kết quả

```
3.14159
8
```

---

# 2. Tại sao cần Module?

Nếu tất cả code nằm trong một file

```
main.py
```

Có thể lên tới

```
5000 dòng

10000 dòng

30000 dòng
```

=> cực kỳ khó bảo trì.

Ví dụ ứng dụng cào truyện

```
main.py

- Download HTML
- Parse HTML
- SQLite
- Logging
- CLI
- Config
- Retry
- Export
```

=> Một file khổng lồ.

Thay vào đó chia thành

```
crawler.py

database.py

config.py

logger.py

parser.py

export.py
```

Đây chính là tư tưởng Modular Programming.

---

# 3. Import Module

Ví dụ

```
calculator.py
```

```python
def add(a, b):
    return a + b


def mul(a, b):
    return a * b
```

```
main.py
```

```python
import calculator

print(calculator.add(2, 5))
print(calculator.mul(3, 4))
```

Output

```
7
12
```

---

# 4. Import nhiều Module

```
math_utils.py
```

```python
def square(x):
    return x * x
```

```
string_utils.py
```

```python
def upper(text):
    return text.upper()
```

```
main.py
```

```python
import math_utils
import string_utils

print(math_utils.square(5))
print(string_utils.upper("python"))
```

---

# 5. Alias

Có thể đổi tên module.

```python
import math_utils as mu

print(mu.square(10))
```

Alias giúp code ngắn hơn.

Ví dụ

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
```

Đây là quy ước phổ biến.

---

# 6. Import một hàm

Thay vì

```python
import calculator

calculator.add(...)
```

Có thể

```python
from calculator import add

print(add(3, 5))
```

---

# 7. Import nhiều hàm

```python
from calculator import add, mul

print(add(1, 2))
print(mul(4, 5))
```

---

# 8. Import tất cả (`*`)

```python
from calculator import *
```

Không nên.

Vì

```python
add()
mul()
```

Không biết đến từ module nào.

Ngoài ra dễ bị đè tên.

Ví dụ

```
math1.py

math2.py
```

Đều có

```python
add()
```

Nếu

```python
from math1 import *
from math2 import *
```

`add()` cuối cùng sẽ là của `math2`.

Đây là nguyên nhân gây lỗi khó phát hiện.

**Best Practice:** Tránh `from module import *`, trừ các trường hợp đặc biệt (ví dụ trong `__init__.py` để xây dựng API của package).

---

# 9. Module chỉ được import một lần

Ví dụ

```
hello.py
```

```python
print("Loading module...")

x = 10
```

```
main.py
```

```python
import hello
import hello
import hello
```

Output

```
Loading module...
```

Chỉ in **một lần**.

Tại sao?

Python có cache module.

---

# 10. `sys.modules`

Python lưu module đã import trong bộ nhớ.

```python
import sys

print(sys.modules.keys())
```

Bạn sẽ thấy hàng trăm module.

Ví dụ

```
os

math

pathlib

logging

typing
```

Khi

```python
import math
```

lần thứ hai

Python kiểm tra

```
sys.modules
```

Nếu đã có

→ không load lại.

Điều này giúp tăng hiệu năng và đảm bảo chỉ có một đối tượng module trong bộ nhớ.

---

# 11. Module là một Object

Điều thú vị:

```python
import math

print(type(math))
```

Kết quả

```python
<class 'module'>
```

Module cũng là object.

Có thể

```python
dir(math)
```

Kết quả

```
acos

asin

cos

sin

sqrt

...
```

---

# 12. Module có Namespace riêng

```
a.py
```

```python
x = 100
```

```
b.py
```

```python
x = 999
```

```
main.py
```

```python
import a
import b

print(a.x)
print(b.x)
```

Output

```
100
999
```

Không bị xung đột.

---

# 13. Python tìm Module ở đâu?

Python tìm module theo thứ tự:

1. Thư mục hiện tại.
2. Thư mục trong `PYTHONPATH`.
3. Thư viện chuẩn (Standard Library).
4. Thư viện cài bằng `pip`.

Xem đường dẫn:

```python
import sys

for p in sys.path:
    print(p)
```

Ví dụ

```
C:\project

C:\Python\Lib

site-packages
```

---

# 14. `__name__`

Mỗi module đều có biến đặc biệt

```python
__name__
```

Ví dụ

```
hello.py
```

```python
print(__name__)
```

Nếu chạy trực tiếp

```
python hello.py
```

Output

```
__main__
```

Nếu

```
main.py
```

```python
import hello
```

Output

```
hello
```

---

# 15. `if __name__ == "__main__"`

Đây là mẫu (pattern) rất quan trọng.

```python
def main():
    print("Application Start")


if __name__ == "__main__":
    main()
```

Ý nghĩa:

* Nếu file được chạy trực tiếp → gọi `main()`.
* Nếu file chỉ được import → không chạy `main()`.

Ví dụ

```
tool.py
```

```python
def add(a, b):
    return a + b


def main():
    print(add(2, 3))


if __name__ == "__main__":
    main()
```

```
main.py
```

```python
import tool

print(tool.add(5, 7))
```

Output

```
12
```

Không in `5` từ `tool.py` vì `main()` không được gọi khi import.

---

# 16. Circular Import (Import vòng)

Ví dụ:

```
a.py
```

```python
from b import func_b


def func_a():
    print("A")
```

```
b.py
```

```python
from a import func_a


def func_b():
    print("B")
```

Khi chạy

```
ImportError
```

Vì:

```
A
 ↓
B
 ↓
A
 ↓
B
...
```

Python không thể hoàn tất quá trình import.

**Cách khắc phục:**

* Di chuyển phần dùng chung sang module thứ ba.
* Hoặc import bên trong hàm (local import) nếu phù hợp.

---

# 17. Best Practices

## Nên

```python
import pathlib
import logging

from datetime import datetime

from myapp import config
```

Rõ ràng, dễ đọc.

---

## Không nên

```python
from math import *
```

---

## Một module chỉ nên có một nhiệm vụ

Thay vì

```
utils.py
```

chứa:

```
500 hàm
```

Hãy tách thành:

```
string_utils.py
file_utils.py
date_utils.py
math_utils.py
network_utils.py
```

Mỗi module có trách nhiệm riêng, giúp dễ kiểm thử và tái sử dụng.

---

# 18. Ví dụ thực tế

```
project/

│
├── main.py
├── config.py
├── logger.py
├── database.py
├── parser.py
└── crawler.py
```

**config.py**

```python
BASE_URL = "https://example.com"
TIMEOUT = 30
```

**crawler.py**

```python
from config import BASE_URL


def crawl():
    print(f"Crawling {BASE_URL}")
```

**main.py**

```python
from crawler import crawl


def main():
    crawl()


if __name__ == "__main__":
    main()
```

Cấu trúc này rõ ràng, mỗi module đảm nhiệm một vai trò riêng.

---

# Tổng kết

Sau buổi học này, bạn đã nắm được:

* Khái niệm Module và lợi ích của việc chia nhỏ chương trình.
* Cách sử dụng `import`, `from ... import`, và `as`.
* Cơ chế cache module thông qua `sys.modules`.
* Namespace của module và cách Python tìm kiếm module qua `sys.path`.
* Vai trò của `__name__` và mẫu `if __name__ == "__main__":`.
* Nguyên nhân gây ra Circular Import và cách tránh.
* Các thực hành tốt khi tổ chức module trong dự án.

## Bài tập thực hành

1. Tạo module `math_utils.py` với các hàm `add()`, `sub()`, `mul()`, `div()` và sử dụng trong `main.py`.
2. Tạo module `string_utils.py` với các hàm `upper()`, `lower()`, `capitalize()`.
3. In toàn bộ `sys.path` và giải thích từng đường dẫn trên máy của bạn.
4. In ra số lượng module đang có trong `sys.modules` sau khi import `math`, `json`, `pathlib`.
5. Viết một module có `main()` và sử dụng `if __name__ == "__main__":` để kiểm chứng sự khác biệt giữa **chạy trực tiếp** và **được import**.
6. Tự tạo một ví dụ gây **Circular Import**, quan sát lỗi, sau đó sửa bằng cách tách phần dùng chung sang module thứ ba. Đây là bài tập rất quan trọng để hiểu cách Python xử lý quá trình import.

Ở **Buổi 22**, chúng ta sẽ học **Package**, bao gồm `__init__.py`, package lồng nhau, absolute import, relative import và cách tổ chức một dự án Python chuyên nghiệp với nhiều module.
