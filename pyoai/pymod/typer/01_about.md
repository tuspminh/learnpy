# Buổi 1 — Typer là gì? Viết ứng dụng CLI đầu tiên

## Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu CLI là gì.
* Biết vì sao nên dùng Typer thay vì `argparse`.
* Viết được chương trình CLI đầu tiên.
* Hiểu cách Typer hoạt động.
* Biết cách chạy chương trình.
* Biết cách xem `--help`.
* Biết annotation ảnh hưởng thế nào đến CLI.
* Hoàn thành project đầu tiên.

---

# 1. CLI là gì?

CLI (**Command Line Interface**) là chương trình được điều khiển bằng dòng lệnh.

Ví dụ:

```bash
git status

git commit -m "Hello"

docker ps

python main.py

pip install typer

uv sync
```

Thay vì bấm nút bằng chuột (GUI), người dùng gõ lệnh.

Ví dụ:

```
story search "Đấu phá thương khung"

story download 1001

story read 1001
```

CLI rất phù hợp với:

* automation
* script
* dev tools
* server
* crawler
* AI tools

---

# 2. Vì sao nên học Typer?

Python có rất nhiều thư viện CLI.

## argparse

Có sẵn trong Python.

Ví dụ:

```python
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("name")

args = parser.parse_args()

print(args.name)
```

Chạy:

```
python main.py Garden
```

Kết quả

```
Garden
```

Được nhưng code khá dài.

---

## Click

Sau này xuất hiện Click.

```python
import click

@click.command()
@click.argument("name")
def hello(name):
    print(name)
```

Ngắn hơn.

---

## Typer

Typer được xây dựng trên Click.

Code cực kỳ Pythonic.

```python
import typer

app = typer.Typer()

@app.command()
def hello(name: str):
    print(name)

app()
```

Typer đọc luôn type annotation.

Đây chính là điểm mạnh nhất.

---

# 3. Cài đặt

Khuyến nghị dùng môi trường ảo.

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Linux/macOS

```bash
source .venv/bin/activate
```

Cài Typer:

```bash
pip install "typer[all]"
```

Kiểm tra:

```bash
python -c "import typer; print(typer.__version__)"
```

---

# 4. Project đầu tiên

Tạo cấu trúc:

```
lesson01/

    hello.py
```

---

## hello.py

```python
import typer

app = typer.Typer()


@app.command()
def hello(name: str):
    print(f"Hello {name}!")


if __name__ == "__main__":
    app()
```

---

Chạy

```bash
python hello.py hello Garden
```

Kết quả

```
Hello Garden!
```

---

# 5. Vì sao phải có app = Typer()

```python
app = typer.Typer()
```

Đây là đối tượng đại diện toàn bộ ứng dụng CLI.

Sau này nó sẽ quản lý:

* command
* help
* callback
* context
* plugin
* completion

Có thể xem như:

```python
app = CLIApplication()
```

---

# 6. @app.command()

```python
@app.command()
def hello():
    ...
```

Decorator này đăng ký hàm thành một command.

Nếu bỏ decorator:

```python
def hello():
    ...
```

Typer sẽ không biết hàm này tồn tại.

---

# 7. app()

Dòng cuối:

```python
app()
```

rất quan trọng.

Nó sẽ:

* đọc `sys.argv`
* phân tích command
* gọi đúng function

Ví dụ:

```
python hello.py hello Garden
```

Python nhận được:

```python
sys.argv
```

là

```python
[
    "hello.py",
    "hello",
    "Garden"
]
```

Typer sẽ phân tích:

```
command

↓

hello
```

```
argument

↓

Garden
```

rồi gọi

```python
hello("Garden")
```

---

# 8. Type Annotation

Đây là điểm mạnh nhất.

```python
def hello(name: str):
```

Nếu sửa thành

```python
def hello(age: int):
```

Typer hiểu ngay đây là số nguyên.

Chạy:

```bash
python hello.py hello 18
```

Kết quả

```
18
```

Nếu nhập

```bash
python hello.py hello abc
```

Typer tự báo lỗi.

```
Invalid value for AGE
```

Không cần viết code kiểm tra.

---

# 9. Help tự động

Chạy

```bash
python hello.py --help
```

Ví dụ đầu ra:

```text
Usage: hello.py [OPTIONS] COMMAND [ARGS]...

Commands:
  hello
```

Tiếp tục:

```bash
python hello.py hello --help
```

Ví dụ:

```text
Usage: hello.py hello [OPTIONS] NAME

Arguments:
  NAME
```

Typer sinh toàn bộ help.

Không cần tự viết.

---

# 10. Thêm command thứ hai

```python
import typer

app = typer.Typer()


@app.command()
def hello(name: str):
    print(f"Hello {name}")


@app.command()
def bye(name: str):
    print(f"Bye {name}")


if __name__ == "__main__":
    app()
```

Chạy:

```bash
python hello.py hello Garden
```

```
Hello Garden
```

---

```bash
python hello.py bye Garden
```

```
Bye Garden
```

---

Help:

```bash
python hello.py --help
```

```
Commands

hello

bye
```

Typer tự động phát hiện cả hai command.

---

# 11. Cách Typer hoạt động

```text
Người dùng

↓

Terminal

↓

sys.argv

↓

Typer

↓

Parser

↓

Validation

↓

Function

↓

Output
```

Toàn bộ việc phân tích dòng lệnh được Typer thực hiện.

---

# 12. Project thực hành

Tạo file:

```
greet.py
```

Yêu cầu:

Có ba command:

```text
hello
```

```text
bye
```

```text
welcome
```

Ví dụ:

```
python greet.py hello Garden
```

```
Hello Garden!
```

---

```
python greet.py bye Garden
```

```
Goodbye Garden!
```

---

```
python greet.py welcome Garden
```

```
Welcome Garden!
```

Sau đó:

```
python greet.py --help
```

và

```
python greet.py hello --help
```

Quan sát cách Typer tự sinh tài liệu.

---

# 13. Bài tập

## Bài 1

Viết chương trình:

```text
math.py
```

Có command:

```
square
```

Ví dụ:

```
python math.py square 5
```

Kết quả:

```
25
```

---

## Bài 2

Thêm command:

```
cube
```

Ví dụ:

```
python math.py cube 4
```

Kết quả:

```
64
```

---

## Bài 3

Thêm command:

```
circle
```

Nhập bán kính.

In diện tích hình tròn.

---

## Bài 4

Thử truyền sai kiểu dữ liệu:

```
python math.py square abc
```

Quan sát lỗi Typer sinh ra và giải thích vì sao.

---

# Tổng kết

Hôm nay bạn đã nắm được những khái niệm nền tảng của Typer:

* CLI là gì và khi nào nên sử dụng.
* Cài đặt và chạy ứng dụng Typer đầu tiên.
* Vai trò của `Typer()`, `@app.command()` và `app()`.
* Cách Typer tận dụng type annotation để tự động kiểm tra dữ liệu đầu vào.
* Cách sử dụng hệ thống `--help` được sinh tự động.
* Cách tạo nhiều command trong cùng một ứng dụng CLI.

Ở **Buổi 2**, chúng ta sẽ đi sâu vào **Command**, tìm hiểu cách đặt tên command, đổi tên command, ẩn command, tổ chức nhiều command và xây dựng cấu trúc CLI chuyên nghiệp giống `git` hoặc `docker`.
