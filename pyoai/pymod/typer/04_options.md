# Buổi 4 — Options trong Typer (Deep Dive)

## Mục tiêu

Sau buổi học này, bạn sẽ:

* Hiểu **Option** là gì.
* Phân biệt **Argument** và **Option**.
* Sử dụng thành thạo `typer.Option()`.
* Biết cách khai báo:

  * giá trị mặc định
  * short option (`-o`)
  * long option (`--output`)
  * flag (`--force`)
  * nhiều alias
  * prompt
* Hiểu cách Typer xử lý Option.
* Xây dựng một CLI thực tế giống các công cụ chuyên nghiệp.

---

# 1. Option là gì?

Nếu Argument là:

```bash
story read 100
```

thì:

```bash
story read 100 --theme dark
```

Trong đó

```text
100
```

là **Argument**

còn

```text
--theme dark
```

là **Option**

---

Ví dụ khác

```bash
cp source.txt dest.txt --force
```

```text
source.txt
```

Argument

```text
dest.txt
```

Argument

```text
--force
```

Option

---

# 2. Argument vs Option

Argument

```bash
python app.py hello Garden
```

Option

```bash
python app.py hello --name Garden
```

Trong code

Argument

```python
name: str
```

Option

```python
name: str = typer.Option(...)
```

**Quy tắc**

| Argument        | Option          |
| --------------- | --------------- |
| theo vị trí     | có tên          |
| thường bắt buộc | thường tùy chọn |
| ngắn            | linh hoạt       |

---

# 3. Option đầu tiên

```python
from typing import Annotated

import typer

app = typer.Typer()


@app.command()
def hello(
    name: Annotated[
        str,
        typer.Option(help="Tên người dùng.")
    ] = "World",
):
    print(f"Hello {name}")


if __name__ == "__main__":
    app()
```

Chạy

```bash
python app.py hello
```

↓

```text
Hello World
```

---

```bash
python app.py hello --name Garden
```

↓

```text
Hello Garden
```

---

# 4. Giá trị mặc định

```python
count: Annotated[
    int,
    typer.Option()
] = 1
```

Nếu không nhập

↓

```text
1
```

Nếu nhập

```bash
--count 5
```

↓

```text
5
```

---

# 5. Short Option

Ví dụ

```python
from typing import Annotated

verbose: Annotated[
    bool,
    typer.Option("--verbose", "-v")
] = False
```

Có thể chạy

```bash
python app.py run --verbose
```

hoặc

```bash
python app.py run -v
```

Hai lệnh giống nhau.

---

# 6. Long Option

```python
output: Annotated[
    str,
    typer.Option("--output")
]
```

Chạy

```bash
python app.py build --output dist.txt
```

---

# 7. Flag

Flag là Option **không cần giá trị**.

Ví dụ

```python
force: Annotated[
    bool,
    typer.Option("--force", "-f")
] = False
```

Chạy

```bash
python app.py delete
```

↓

```text
False
```

---

```bash
python app.py delete --force
```

↓

```text
True
```

Đây là kiểu thường gặp nhất.

Ví dụ

```text
git push --force

docker build --no-cache

uv sync --frozen
```

---

# 8. Nhiều alias

Có thể khai báo

```python
output: Annotated[
    str,
    typer.Option(
        "--output",
        "-o"
    )
]
```

Khi đó

```bash
--output result.txt
```

và

```bash
-o result.txt
```

là giống nhau.

---

# 9. Option bắt buộc

Nếu không có giá trị mặc định

```python
from typing import Annotated

name: Annotated[
    str,
    typer.Option(...)
]
```

Typer yêu cầu người dùng phải nhập.

```bash
python app.py hello
```

↓

```text
Missing option '--name'
```

---

# 10. Help

```python
output: Annotated[
    str,
    typer.Option(
        help="Tên file đầu ra."
    )
]
```

Khi

```bash
python app.py build --help
```

↓

```text
--output TEXT

Tên file đầu ra.
```

---

# 11. Bool Option

Ví dụ

```python
debug: Annotated[
    bool,
    typer.Option()
] = False
```

Nếu

```bash
python app.py run
```

↓

```text
False
```

Nếu

```bash
python app.py run --debug
```

↓

```text
True
```

---

Typer còn hỗ trợ:

```bash
--debug

--no-debug
```

nếu cấu hình phù hợp. Đây là phong cách CLI hiện đại vì người dùng có thể bật hoặc tắt rõ ràng.

---

# 12. Ví dụ thực tế

```python
from typing import Annotated

import typer

app = typer.Typer()


@app.command()
def build(
    source: str,
    output: Annotated[
        str,
        typer.Option("--output", "-o")
    ] = "dist.txt",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v")
    ] = False,
):
    print(source)
    print(output)
    print(verbose)


if __name__ == "__main__":
    app()
```

---

Ví dụ

```bash
python app.py build story.txt
```

↓

```text
story.txt
dist.txt
False
```

---

```bash
python app.py build story.txt -o result.txt
```

↓

```text
story.txt
result.txt
False
```

---

```bash
python app.py build story.txt -o result.txt -v
```

↓

```text
story.txt
result.txt
True
```

---

# 13. Path Option

```python
from pathlib import Path
from typing import Annotated

output: Annotated[
    Path,
    typer.Option("--output", "-o")
]
```

Có thể

```bash
-o backup/data.db
```

Sau đó

```python
output.exists()
```

hoặc

```python
output.parent
```

---

# 14. Enum Option

```python
from enum import Enum
from typing import Annotated

class Format(str, Enum):
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"


fmt: Annotated[
    Format,
    typer.Option("--format")
] = Format.JSON
```

Chạy

```bash
--format yaml
```

↓

```text
Format.YAML
```

Nếu

```bash
--format xml
```

Typer báo lỗi ngay.

---

# 15. Project thực hành — rename.py

```python
from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer()


@app.command()
def rename(
    source: Path,
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Tên file mới."
        ),
    ],
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Ghi đè nếu file đã tồn tại."
        ),
    ] = False,
):
    if not source.exists():
        raise typer.BadParameter("File nguồn không tồn tại.")

    if output.exists() and not force:
        raise typer.BadParameter(
            "File đích đã tồn tại. Dùng --force để ghi đè."
        )

    source.rename(output)

    typer.echo(f"Đã đổi tên: {source} -> {output}")
```

---

Ví dụ

```bash
python rename.py rename a.txt -o b.txt
```

↓

```text
Đã đổi tên: a.txt -> b.txt
```

---

Nếu

```bash
python rename.py rename a.txt -o b.txt
```

mà `b.txt` đã tồn tại

↓

```text
Error:

File đích đã tồn tại.
```

---

Muốn ghi đè

```bash
python rename.py rename a.txt -o b.txt -f
```

↓

thành công.

---

# 16. Best Practices

## Luôn có short option

```text
--output

-o
```

---

## Bool dùng flag

Không nên

```bash
--debug true
```

Nên

```bash
--debug
```

---

## Path thay cho str

Không nên

```python
filename: str
```

Nên

```python
filename: Path
```

---

## Enum thay cho chuỗi

Không nên

```python
format: str
```

Nên

```python
format: Format
```

---

## Help đầy đủ

Mỗi Option nên có:

```python
help="..."
```

CLI sẽ chuyên nghiệp hơn rất nhiều.

---

# Bài tập

## Bài 1

Viết chương trình

```text
compress.py
```

Có

```text
source
```

Argument

và

```text
--output

-o
```

Option.

Hiện tại chỉ in ra giá trị nhận được.

---

## Bài 2

Viết

```text
backup.py
```

Có

```text
--force
```

Nếu có flag thì in

```text
Force mode
```

---

## Bài 3

Viết

```text
config.py
```

Có Option

```text
--format
```

Chỉ cho phép

```text
json

yaml

toml
```

bằng `Enum`.

---

## Bài 4

Viết chương trình

```text
download.py
```

Yêu cầu:

* `url` (Argument)
* `--output`, `-o` (`Path`, mặc định là `download.bin`)
* `--timeout`, `-t` (`int`, mặc định `30`)
* `--verbose`, `-v` (flag)
* `--overwrite`, `-f` (flag)

Chương trình chỉ cần in toàn bộ giá trị nhận được để kiểm tra việc parse của Typer.

---

# Tổng kết

Trong buổi học này, bạn đã nắm được toàn bộ kiến thức nền tảng về **Option** trong Typer:

* Phân biệt rõ **Argument** và **Option**.
* Khai báo Option với `typer.Option()` và `typing.Annotated`.
* Sử dụng giá trị mặc định, short option (`-o`), long option (`--output`) và flag (`--force`).
* Áp dụng `Path` và `Enum` để tăng độ an toàn và khả năng tự kiểm tra dữ liệu.
* Xây dựng một ứng dụng CLI thực tế với nhiều Option theo phong cách của các công cụ chuyên nghiệp.

## Chuẩn bị cho Buổi 5

Ở **Buổi 5**, chúng ta sẽ học về **Prompt và nhập liệu tương tác**, bao gồm:

* `typer.prompt()`
* `typer.confirm()`
* Nhập mật khẩu (`hide_input=True`)
* Giá trị mặc định khi prompt
* Validation khi người dùng nhập
* Thiết kế trải nghiệm CLI tương tác giống các công cụ như `poetry`, `pip` và `uv`.
