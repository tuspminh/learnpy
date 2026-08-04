# Buổi 3 — Arguments trong Typer (Deep Dive)

## Mục tiêu

Sau buổi học này, bạn sẽ:

* Hiểu rõ **Argument** là gì.
* Phân biệt **Argument** và **Option**.
* Sử dụng thành thạo các kiểu dữ liệu:

  * `str`
  * `int`
  * `float`
  * `bool`
  * `pathlib.Path`
  * `Enum`
  * `UUID`
  * `datetime`
* Hiểu cách Typer tự động chuyển đổi kiểu dữ liệu.
* Biết cách khai báo metadata cho Argument.
* Biết cách validate dữ liệu đầu vào.
* Hoàn thành một dự án CLI thực tế.

---

# 1. Argument là gì?

Argument là **giá trị bắt buộc** được truyền theo **vị trí**.

Ví dụ:

```bash
python app.py hello Garden
```

Ở đây:

```text
hello
```

là command.

```text
Garden
```

là argument.

Typer sẽ gọi:

```python
hello("Garden")
```

---

Ví dụ:

```python
import typer

app = typer.Typer()


@app.command()
def hello(name: str):
    print(name)


if __name__ == "__main__":
    app()
```

---

Chạy

```bash
python app.py hello Garden
```

Kết quả

```text
Garden
```

---

# 2. Argument khác Option như thế nào?

Argument:

```bash
python app.py hello Garden
```

Option:

```bash
python app.py hello --name Garden
```

Trong Typer:

Argument

```python
def hello(name: str):
```

Option

```python
def hello(
    name: str = typer.Option(...)
):
```

**Quy tắc ghi nhớ:**

* Argument → bắt buộc, theo vị trí.
* Option → có tên (`--name`), thường tùy chọn.

---

# 3. Argument kiểu `str`

Đây là kiểu phổ biến nhất.

```python
import typer

app = typer.Typer()


@app.command()
def greet(name: str):
    print(f"Hello {name}")


if __name__ == "__main__":
    app()
```

Chạy

```bash
python app.py greet Alice
```

Kết quả

```text
Hello Alice
```

---

# 4. Argument kiểu `int`

```python
@app.command()
def square(number: int):
    print(number ** 2)
```

Chạy

```bash
python app.py square 12
```

Kết quả

```text
144
```

Nếu:

```bash
python app.py square abc
```

Typer tự báo lỗi

```text
Invalid value for 'NUMBER'
```

Không cần tự viết:

```python
try:
    number = int(...)
except:
    ...
```

---

# 5. Argument kiểu `float`

```python
@app.command()
def bmi(weight: float, height: float):
    print(weight / (height ** 2))
```

Chạy

```bash
python app.py bmi 70 1.75
```

Kết quả

```text
22.857142857
```

---

# 6. Argument kiểu `bool`

Đây là phần rất nhiều người mới nhầm.

```python
@app.command()
def test(value: bool):
    print(value)
```

Chạy

```bash
python app.py test true
```

↓

```text
True
```

---

```bash
python app.py test false
```

↓

```text
False
```

Typer chấp nhận nhiều giá trị:

```text
true
false
1
0
yes
no
on
off
```

**Lưu ý:** Trong CLI, `bool` thường phù hợp hơn với **Option** (`--debug`, `--force`) thay vì Argument. Chúng ta sẽ học chi tiết ở Buổi 4.

---

# 7. Argument kiểu `pathlib.Path`

Đây là kiểu cực kỳ quan trọng.

```python
from pathlib import Path
import typer

app = typer.Typer()


@app.command()
def show(file: Path):
    print(file)
```

Chạy

```bash
python app.py show README.md
```

Kết quả

```text
README.md
```

Có thể dùng:

```python
print(file.exists())
print(file.is_file())
print(file.read_text())
```

Không cần:

```python
open(...)
```

ngay từ đầu.

---

# 8. Ví dụ đọc file

```python
from pathlib import Path
import typer

app = typer.Typer()


@app.command()
def read(file: Path):
    print(file.read_text(encoding="utf8"))


if __name__ == "__main__":
    app()
```

Ví dụ `note.txt`

```text
Hello Typer
```

Chạy

```bash
python app.py read note.txt
```

↓

```text
Hello Typer
```

---

# 9. Enum

Giả sử chỉ cho phép ba màu.

```python
from enum import Enum

import typer

app = typer.Typer()


class Color(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


@app.command()
def paint(color: Color):
    print(color)
```

Chạy

```bash
python app.py paint red
```

↓

```text
Color.RED
```

---

Nếu

```bash
python app.py paint yellow
```

Typer báo lỗi ngay.

Đây là cách rất hay để giới hạn giá trị hợp lệ.

---

# 10. UUID

```python
from uuid import UUID

import typer

app = typer.Typer()


@app.command()
def user(user_id: UUID):
    print(user_id)
```

Ví dụ

```bash
python app.py user 550e8400-e29b-41d4-a716-446655440000
```

Nếu UUID sai định dạng, Typer sẽ từ chối.

---

# 11. Datetime

```python
from datetime import datetime

import typer

app = typer.Typer()


@app.command()
def event(time: datetime):
    print(time)
```

Ví dụ

```bash
python app.py event 2026-08-04T18:30:00
```

↓

```text
2026-08-04 18:30:00
```

Typer sẽ chuyển chuỗi thành `datetime.datetime`.

---

# 12. Metadata cho Argument

Có thể mô tả Argument bằng `typer.Argument()`.

```python
from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer()


@app.command()
def read(
    file: Annotated[
        Path,
        typer.Argument(help="Đường dẫn đến tệp văn bản.")
    ]
):
    print(file.read_text())
```

Khi chạy:

```bash
python app.py read --help
```

Bạn sẽ thấy phần mô tả của `file`.

> **Khuyến nghị:** Với Python 3.10+, nên dùng `typing.Annotated` để gắn metadata thay vì truyền trực tiếp vào giá trị mặc định. Đây cũng là phong cách được Typer khuyến nghị.

---

# 13. Validation bằng callback

Ví dụ:

```python
from typing import Annotated

import typer

app = typer.Typer()


def positive(value: int):
    if value <= 0:
        raise typer.BadParameter("Giá trị phải lớn hơn 0.")
    return value


@app.command()
def square(
    number: Annotated[
        int,
        typer.Argument(callback=positive)
    ]
):
    print(number ** 2)
```

Chạy

```bash
python app.py square -5
```

↓

```text
Error: Giá trị phải lớn hơn 0.
```

Validation được tách riêng, dễ tái sử dụng.

---

# 14. Dự án thực hành — cp.py

Xây dựng chương trình sao chép tệp.

```python
from pathlib import Path
import shutil
from typing import Annotated

import typer

app = typer.Typer()


def existing_file(path: Path) -> Path:
    if not path.exists():
        raise typer.BadParameter("Tệp nguồn không tồn tại.")
    if not path.is_file():
        raise typer.BadParameter("Đường dẫn nguồn không phải là tệp.")
    return path


@app.command()
def copy(
    source: Annotated[
        Path,
        typer.Argument(
            help="Tệp nguồn.",
            callback=existing_file,
        ),
    ],
    destination: Annotated[
        Path,
        typer.Argument(help="Tệp đích."),
    ],
):
    shutil.copy2(source, destination)
    typer.echo(f"Đã sao chép: {source} -> {destination}")


if __name__ == "__main__":
    app()
```

---

Ví dụ:

```bash
python cp.py copy story.txt backup.txt
```

↓

```text
Đã sao chép: story.txt -> backup.txt
```

Nếu:

```bash
python cp.py copy abc.txt out.txt
```

↓

```text
Error: Tệp nguồn không tồn tại.
```

---

# 15. Best Practices

## Luôn dùng type annotation

```python
def read(file: Path):
```

Không nên:

```python
def read(file):
```

---

## Dùng `Path`

Thay vì:

```python
filename: str
```

nên:

```python
filename: Path
```

---

## Dùng `Enum`

Thay vì:

```python
mode: str
```

nên:

```python
mode: Mode
```

---

## Dùng callback để validation

Không nên:

```python
@app.command()
def add(number: int):
    if number < 0:
        ...
```

Nên:

```python
def validate():
    ...

@app.command()
def add(...):
```

Validation được tách khỏi business logic.

---

# Bài tập

## Bài 1

Viết chương trình:

```text
cat.py
```

Nhận một `Path`.

Đọc nội dung file.

---

## Bài 2

Viết chương trình:

```text
age.py
```

Nhận:

```text
age
```

Là số nguyên.

Không cho phép nhỏ hơn 0.

---

## Bài 3

Viết chương trình:

```text
traffic.py
```

Dùng `Enum`.

Cho phép:

```text
red

yellow

green
```

Nếu nhập sai màu thì Typer phải báo lỗi.

---

## Bài 4

Viết chương trình:

```text
backup.py
```

Nhận:

* file nguồn (`Path`)
* thư mục đích (`Path`)

Kiểm tra file nguồn tồn tại rồi sao chép sang thư mục đích.

---

# Tổng kết

Trong buổi học này, bạn đã học cách sử dụng **Argument** trong Typer một cách bài bản:

* Phân biệt rõ **Argument** và **Option**.
* Khai báo Argument với nhiều kiểu dữ liệu (`str`, `int`, `float`, `bool`, `Path`, `Enum`, `UUID`, `datetime`).
* Tận dụng `typing.Annotated` và `typer.Argument()` để bổ sung metadata và tài liệu tự động.
* Tách logic kiểm tra dữ liệu bằng callback validation.
* Xây dựng một công cụ CLI thực tế để sao chép tệp.

Ở **Buổi 4**, chúng ta sẽ chuyển sang **Options**, tìm hiểu các tham số dạng `--output`, `--force`, `--verbose`, `-o`, `-f`, `-v`, giá trị mặc định, cờ (flags), alias và các kỹ thuật thiết kế CLI chuyên nghiệp theo phong cách `git`, `docker` và `uv`.
