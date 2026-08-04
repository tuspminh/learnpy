# Buổi 2 — Command trong Typer (Deep Dive)

## Mục tiêu

Sau buổi này bạn sẽ:

* Hiểu cách Typer đăng ký command.
* Biết cách đổi tên command.
* Biết cách ẩn command.
* Biết cách viết command có mô tả.
* Biết cách tổ chức nhiều command.
* Hiểu vòng đời (lifecycle) của một command.
* Hoàn thành một ứng dụng CLI Calculator.

---

# 1. Command là gì?

Trong Typer, mỗi **command** là một chức năng mà người dùng có thể gọi từ dòng lệnh.

Ví dụ:

```bash
git status
git commit
git push
```

Ở đây:

* `git` là ứng dụng CLI.
* `status`, `commit`, `push` là các command.

Tương tự:

```bash
story search
story download
story read
```

* `story` là ứng dụng.
* `search`, `download`, `read` là command.

Trong Typer:

```python
import typer

app = typer.Typer()


@app.command()
def hello():
    print("Hello")


if __name__ == "__main__":
    app()
```

`hello()` chính là một command.

---

# 2. Command được đăng ký như thế nào?

Decorator:

```python
@app.command()
```

thực chất sẽ đăng ký hàm vào danh sách command của ứng dụng.

Có thể hình dung:

```text
Typer()

↓

Command Registry

↓

hello()

↓

bye()

↓

search()

↓

download()
```

Khi người dùng chạy:

```bash
python app.py hello
```

Typer tìm command tên `hello` và gọi:

```python
hello()
```

---

# 3. Tạo nhiều command

Ví dụ:

```python
import typer

app = typer.Typer()


@app.command()
def hello():
    print("Hello")


@app.command()
def bye():
    print("Bye")


@app.command()
def welcome():
    print("Welcome")


if __name__ == "__main__":
    app()
```

Chạy:

```bash
python app.py hello
```

Kết quả:

```text
Hello
```

---

```bash
python app.py bye
```

```text
Bye
```

---

```bash
python app.py welcome
```

```text
Welcome
```

---

Help:

```bash
python app.py --help
```

Ví dụ đầu ra:

```text
Commands

hello
bye
welcome
```

---

# 4. Tên command mặc định

Typer lấy tên hàm làm tên command.

```python
@app.command()
def hello():
    ...
```

↓

Command:

```text
hello
```

---

```python
@app.command()
def download():
    ...
```

↓

Command:

```text
download
```

---

# 5. Đổi tên command

Có thể đổi tên:

```python
@app.command(name="hi")
def hello():
    print("Hello")
```

Bây giờ:

```bash
python app.py hi
```

sẽ chạy:

```python
hello()
```

Nhưng:

```bash
python app.py hello
```

sẽ báo lỗi vì command `hello` không còn được đăng ký.

---

# 6. Command có mô tả

Ví dụ:

```python
@app.command(help="In lời chào tới người dùng.")
def hello():
    print("Hello")
```

Chạy:

```bash
python app.py --help
```

Bạn sẽ thấy:

```text
Commands

hello    In lời chào tới người dùng.
```

Đây là cách viết tài liệu ngay trong code.

---

# 7. Docstring cũng tạo Help

Nếu không truyền `help=`, Typer sẽ dùng docstring.

```python
@app.command()
def hello():
    """
    In lời chào tới người dùng.
    """
    print("Hello")
```

Kết quả `--help` vẫn hiển thị mô tả.

Khuyến nghị: sử dụng docstring để code gọn và dễ bảo trì.

---

# 8. Command có tham số

```python
import typer

app = typer.Typer()


@app.command()
def hello(name: str):
    print(f"Hello {name}")


if __name__ == "__main__":
    app()
```

Chạy:

```bash
python app.py hello Garden
```

Kết quả:

```text
Hello Garden
```

---

# 9. Nhiều tham số

```python
@app.command()
def introduce(name: str, age: int):
    print(f"{name} - {age}")
```

Chạy:

```bash
python app.py introduce Garden 30
```

Kết quả:

```text
Garden - 30
```

Nếu truyền sai:

```bash
python app.py introduce Garden abc
```

Typer sẽ tự động báo lỗi kiểu dữ liệu.

---

# 10. Lifecycle của một command

Giả sử chạy:

```bash
python app.py hello Garden
```

Quy trình:

```text
Người dùng

↓

Terminal

↓

sys.argv

↓

Typer

↓

Tìm command "hello"

↓

Phân tích tham số

↓

Kiểm tra kiểu dữ liệu

↓

Gọi hello("Garden")

↓

Hiển thị kết quả
```

Đây là lý do bạn không cần tự phân tích `sys.argv`.

---

# 11. Command ẩn (Hidden Command)

Đôi khi có command chỉ dùng nội bộ.

Ví dụ:

```python
@app.command(hidden=True)
def debug():
    print("Debug mode")
```

Command vẫn chạy được:

```bash
python app.py debug
```

Nhưng:

```bash
python app.py --help
```

sẽ không hiển thị `debug`.

---

# 12. Ví dụ thực tế — Calculator CLI

Tạo file `calculator.py`:

```python
import typer

app = typer.Typer(help="Ứng dụng máy tính đơn giản.")


@app.command()
def add(a: float, b: float):
    """Cộng hai số."""
    print(a + b)


@app.command()
def sub(a: float, b: float):
    """Trừ hai số."""
    print(a - b)


@app.command()
def mul(a: float, b: float):
    """Nhân hai số."""
    print(a * b)


@app.command()
def div(a: float, b: float):
    """Chia hai số."""
    if b == 0:
        raise typer.BadParameter("Không thể chia cho 0.")
    print(a / b)


if __name__ == "__main__":
    app()
```

---

# 13. Thử nghiệm

Cộng:

```bash
python calculator.py add 5 3
```

Kết quả:

```text
8.0
```

---

Trừ:

```bash
python calculator.py sub 10 4
```

Kết quả:

```text
6.0
```

---

Nhân:

```bash
python calculator.py mul 6 7
```

Kết quả:

```text
42.0
```

---

Chia:

```bash
python calculator.py div 20 4
```

Kết quả:

```text
5.0
```

---

Sai kiểu:

```bash
python calculator.py add 5 abc
```

Typer sẽ báo:

```text
Invalid value for 'B'
```

---

Chia cho 0:

```bash
python calculator.py div 5 0
```

Typer sẽ hiển thị thông báo lỗi do `BadParameter`.

---

# 14. Cấu trúc thư mục

```
lesson02/
│
├── calculator.py
└── README.md
```

Sau này, khi ứng dụng lớn hơn:

```
story_cli/
│
├── app.py
├── commands/
│   ├── crawl.py
│   ├── source.py
│   ├── plugin.py
│   └── config.py
└── services/
```

Đây sẽ là chủ đề chính của các buổi sau.

---

# 15. Bài tập

## Bài 1

Viết chương trình `convert.py` với các command:

* `km-to-m`
* `m-to-km`
* `kg-to-g`
* `g-to-kg`

Ví dụ:

```bash
python convert.py km-to-m 2.5
```

Kết quả:

```text
2500.0
```

---

## Bài 2

Viết `student.py`:

* `add`
* `remove`
* `list`

Tạm thời chỉ in thông báo:

```text
Student added.
Student removed.
Student list.
```

---

## Bài 3

Tạo command ẩn:

```text
reset
```

Command này in:

```text
Database reset completed.
```

và xác nhận rằng nó **không xuất hiện trong `--help`**.

---

# Tổng kết

Trong buổi học này, bạn đã hiểu sâu về command trong Typer:

* Command được đăng ký bằng `@app.command()`.
* Mặc định tên command là tên hàm, nhưng có thể đổi bằng `name=`.
* Có thể thêm mô tả bằng `help=` hoặc docstring.
* Có thể tạo command ẩn với `hidden=True`.
* Hiểu vòng đời xử lý của một command từ `sys.argv` đến khi hàm được gọi.
* Xây dựng ứng dụng CLI nhiều command với ví dụ Calculator.

Ở **Buổi 3**, chúng ta sẽ đi sâu vào **Arguments**, bao gồm kiểu dữ liệu (`str`, `int`, `float`, `bool`, `Path`, `Enum`, `UUID`, `datetime`...), cách Typer tự động chuyển đổi và kiểm tra dữ liệu, cùng các kỹ thuật validation để xây dựng CLI mạnh mẽ và thân thiện.
