# Buổi 22. Package trong Python (Deep Dive)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu Package là gì.
> * Phân biệt Module và Package.
> * Biết vai trò của `__init__.py`.
> * Biết tổ chức project Python chuyên nghiệp.
> * Hiểu Absolute Import và Relative Import.
> * Hiểu `__all__`.
> * Biết cách xây dựng một package có API đẹp như thư viện chuẩn.
> * Áp dụng Package vào các dự án thực tế (Crawler, Flask, PySide6, CLI...).

---

# 1. Ôn lại: Module là gì?

Ở buổi trước, chúng ta đã biết:

```text
math_utils.py
```

đây là **một module**.

Ví dụ:

```python
# math_utils.py
def add(a, b):
    return a + b
```

Sử dụng:

```python
import math_utils

print(math_utils.add(2, 3))
```

Một file `.py` = một **Module**.

---

# 2. Package là gì?

Khi chương trình lớn lên, chỉ có module là chưa đủ.

Ví dụ:

```text
crawler.py
database.py
logger.py
config.py
parser.py
models.py
services.py
utils.py
```

Sau vài tháng...

```text
crawler.py

5000 dòng
```

```text
utils.py

200 hàm
```

Mọi thứ trở nên hỗn loạn.

Giải pháp:

👉 Gom các module cùng chức năng vào một thư mục.

Đó chính là **Package**.

---

# 3. Package đầu tiên

Ví dụ:

```text
myapp/

    __init__.py

    math_utils.py

    string_utils.py

main.py
```

Trong đó:

**math_utils.py**

```python
def add(a, b):
    return a + b
```

**string_utils.py**

```python
def upper(text):
    return text.upper()
```

**main.py**

```python
from myapp import math_utils

print(math_utils.add(2, 5))
```

Output

```text
7
```

---

# 4. `__init__.py` là gì?

Đây là file đặc biệt.

```text
myapp/

    __init__.py
```

Nó được chạy khi package được import.

Ví dụ:

```python
# __init__.py

print("Package loaded")
```

```python
import myapp
```

Output

```text
Package loaded
```

---

## Vai trò của `__init__.py`

Có nhiều vai trò:

* đánh dấu package (trong các phiên bản Python cũ).
* khởi tạo package.
* export API.
* import module con.
* khai báo version.

Ví dụ:

```python
__version__ = "1.0.0"
```

---

# 5. Package có thể chứa Package

Ví dụ:

```text
myapp/

    __init__.py

    models/

        __init__.py

        student.py

        teacher.py

    services/

        __init__.py

        student_service.py
```

Đây gọi là:

> Nested Package

---

# 6. Import trong Package

Ví dụ

```text
myapp/

    math_utils.py

    string_utils.py
```

Trong `main.py`

```python
from myapp.math_utils import add

print(add(2, 3))
```

---

# 7. Absolute Import

Đây là cách import được khuyến nghị.

```python
from myapp.math_utils import add
```

Python bắt đầu từ package gốc.

Ưu điểm:

* rõ ràng
* dễ đọc
* IDE hỗ trợ tốt
* ít lỗi

Đây là cách mà các dự án lớn sử dụng.

---

# 8. Relative Import

Ví dụ

```text
myapp/

    models/

        student.py

    services/

        student_service.py
```

Trong

```text
student_service.py
```

```python
from ..models.student import Student
```

Ý nghĩa:

```text
..

lùi 1 package
```

Ví dụ

```python
from .student import Student
```

```text
.

package hiện tại
```

---

# 9. So sánh

Absolute

```python
from myapp.models.student import Student
```

Relative

```python
from ..models.student import Student
```

Nên dùng cái nào?

Thông thường:

* Package nội bộ → Relative hoặc Absolute đều được.
* Ứng dụng lớn → Ưu tiên Absolute Import để dễ đọc và dễ refactor.

---

# 10. `__all__`

Giả sử

```python
# math_utils.py


def add():
    pass


def sub():
    pass


def internal():
    pass


__all__ = ["add", "sub"]
```

Khi

```python
from math_utils import *
```

Chỉ import

```text
add

sub
```

Không import

```text
internal
```

Lưu ý: `__all__` **không** ngăn người khác import trực tiếp (`from math_utils import internal` vẫn được), mà chỉ điều khiển hành vi của `from ... import *`.

---

# 11. Export API

Giả sử

```text
myapp/

    __init__.py

    math_utils.py
```

**math_utils.py**

```python
def add(a, b):
    return a + b
```

Nếu trong

```python
# __init__.py

from .math_utils import add
```

Thì

```python
import myapp

print(myapp.add(2, 3))
```

Không cần

```python
myapp.math_utils.add()
```

Đây là cách nhiều thư viện thiết kế API ngắn gọn.

---

# 12. Khai báo Version

Ví dụ

```python
# __init__.py

__version__ = "2.0.1"
```

Người dùng

```python
import myapp

print(myapp.__version__)
```

---

# 13. Package thực tế

Ví dụ

```text
crawler/

    __init__.py

    config.py

    parser.py

    downloader.py

    database.py

    logger.py
```

Main

```python
from crawler.downloader import download

download()
```

---

# 14. Package trong thư viện chuẩn

Ví dụ

```python
import email
```

Thực ra

```text
email/

    __init__.py

    parser.py

    message.py

    policy.py
```

Đây là một package.

---

# 15. Package của Flask

Ví dụ (đơn giản hóa):

```text
flask/

    __init__.py

    app.py

    cli.py

    config.py

    globals.py

    helpers.py
```

Người dùng chỉ cần

```python
from flask import Flask
```

Nhờ

```python
# flask/__init__.py

from .app import Flask
```

Đây là ví dụ điển hình về việc xây dựng API thông qua `__init__.py`.

---

# 16. Package trong dự án Crawler

Đây là cách mình khuyến nghị cho dự án cào truyện của bạn:

```text
crawler/

│
├── __init__.py
│
├── config/
│   ├── __init__.py
│   └── settings.py
│
├── downloader/
│   ├── __init__.py
│   └── http.py
│
├── parser/
│   ├── __init__.py
│   ├── html.py
│   └── chapter.py
│
├── database/
│   ├── __init__.py
│   ├── models.py
│   └── repository.py
│
├── logger/
│   ├── __init__.py
│   └── logger.py
│
└── utils/
    ├── __init__.py
    ├── retry.py
    └── text.py
```

Mỗi package đảm nhiệm **một nhóm chức năng**, tuân theo nguyên tắc **Single Responsibility**.

---

# 17. Best Practices

## ✔ Đặt tên package bằng chữ thường

```text
good

crawler
database
utils
```

Không nên

```text
Crawler
Database
Utils
```

---

## ✔ Không để quá nhiều module trong cùng một package

Thay vì

```text
utils/

50 file
```

Hãy chia nhỏ:

```text
utils/

    file/

    text/

    network/

    datetime/
```

---

## ✔ Tránh import vòng (Circular Import)

Ví dụ:

```text
service

↓

repository

↓

service
```

Nên tách phần dùng chung sang package khác hoặc thiết kế lại phụ thuộc.

---

## ✔ `__init__.py` nên gọn

Chỉ nên:

* export API.
* khai báo version.
* khởi tạo đơn giản.

Không nên đặt logic nặng, mở kết nối cơ sở dữ liệu hoặc thực hiện các tác vụ tốn thời gian khi import.

---

# 18. Bài tập thực hành

## Bài 1

Tạo package

```text
myapp/

    math_utils.py

    string_utils.py

    __init__.py
```

Gọi các hàm từ `main.py`.

---

## Bài 2

Tạo package

```text
models/

    student.py

    teacher.py
```

Trong `student.py` tạo lớp:

```python
class Student:
    def __init__(self, name):
        self.name = name
```

Import và sử dụng từ `main.py`.

---

## Bài 3

Trong `__init__.py`

```python
from .math_utils import add
```

Sau đó gọi:

```python
import myapp

print(myapp.add(1, 2))
```

---

## Bài 4

Khai báo:

```python
__version__ = "1.0.0"
```

In ra:

```python
import myapp

print(myapp.__version__)
```

---

## Bài 5

Tạo package lồng nhau:

```text
school/

    models/

        student.py

    services/

        student_service.py
```

Trong `student_service.py`, thử cả **absolute import** và **relative import**, sau đó so sánh ưu, nhược điểm của từng cách.

---

# Tổng kết

Sau buổi học này, bạn đã hiểu:

* Module và Package khác nhau như thế nào.
* Vai trò của `__init__.py`.
* Cách tổ chức package lồng nhau.
* Absolute Import và Relative Import.
* `__all__` và cách kiểm soát API của package.
* Cách export API thông qua `__init__.py`.
* Các nguyên tắc tổ chức package cho dự án Python thực tế.

Ở **Buổi 23**, chúng ta sẽ học **Virtual Environment**, bao gồm `venv`, `pip`, `requirements.txt`, quản lý phụ thuộc (dependency management) và cách tạo môi trường phát triển chuyên nghiệp cho từng dự án Python.
