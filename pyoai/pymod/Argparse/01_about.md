# Buổi 1 — Giới thiệu argparse từ cơ bản đến chuyên sâu

## Mục tiêu

Sau buổi học này bạn sẽ hiểu được:

* CLI (Command Line Interface) là gì.
* Vì sao cần `argparse`.
* Hạn chế của `sys.argv`.
* Cách `argparse` hoạt động.
* Viết chương trình CLI đầu tiên.
* Hiểu vòng đời (lifecycle) của một chương trình CLI.

---

# 1. CLI là gì?

CLI (Command Line Interface) là chương trình được điều khiển bằng dòng lệnh thay vì giao diện đồ họa (GUI).

Ví dụ:

```bash
python hello.py
```

hoặc

```bash
git status
```

hoặc

```bash
pip install requests
```

hoặc

```bash
docker run nginx
```

Tất cả đều là CLI.

---

## GUI

```
+----------------------+
|      Button          |
|                      |
|  [ Save ]            |
+----------------------+
```

Bạn bấm chuột.

---

## CLI

```
save --output report.txt
```

Bạn gõ lệnh.

---

# 2. Tại sao CLI quan trọng?

Trong Python, phần lớn công cụ chuyên nghiệp đều là CLI.

Ví dụ:

```
python
pip
pytest
black
ruff
mypy
uv
docker
git
ffmpeg
sqlite3
```

Nếu xây dựng:

* crawler
* downloader
* automation
* AI tool
* TTS
* backup

thì gần như luôn có CLI.

Ví dụ tool crawler:

```bash
story crawl
```

Tool export:

```bash
story export
```

Tool update:

```bash
story update
```

---

# 3. Cách Python nhận tham số

Viết file:

```python
# hello.py

import sys

print(sys.argv)
```

Chạy:

```bash
python hello.py Alice 18
```

Kết quả:

```python
['hello.py', 'Alice', '18']
```

Python tự tách dòng lệnh thành danh sách chuỗi.

```
python hello.py Alice 18

↓

[
    "hello.py",
    "Alice",
    "18"
]
```

Trong đó:

```
argv[0]

↓

hello.py
```

```
argv[1]

↓

Alice
```

```
argv[2]

↓

18
```

---

# 4. sys.argv có vấn đề gì?

Ví dụ:

```python
import sys

name = sys.argv[1]
age = int(sys.argv[2])

print(name)
print(age)
```

Chạy:

```bash
python hello.py Alice 18
```

Đúng.

Nhưng nếu:

```bash
python hello.py
```

Sẽ báo lỗi:

```text
IndexError
```

---

Nếu:

```bash
python hello.py Alice abc
```

Lỗi:

```text
ValueError
```

---

Nếu:

```bash
python hello.py Alice 18 extra data
```

Chương trình cũng không biết phải xử lý thế nào.

=> `sys.argv` quá "thô", mọi thứ đều phải tự kiểm tra.

---

# 5. Argparse giải quyết vấn đề gì?

`argparse` giúp:

* đọc tham số
* kiểm tra kiểu dữ liệu
* tự sinh `--help`
* báo lỗi đẹp
* kiểm tra giá trị hợp lệ
* hỗ trợ subcommand
* hỗ trợ option

Nó là thư viện chuẩn của Python nên **không cần cài đặt**.

---

# 6. Chương trình argparse đầu tiên

```python
import argparse

parser = argparse.ArgumentParser()

args = parser.parse_args()

print(args)
```

Chạy:

```bash
python app.py
```

Kết quả:

```python
Namespace()
```

Đây là một đối tượng chứa các tham số sau khi phân tích.

---

# 7. `ArgumentParser` là gì?

Có thể hình dung:

```
Command Line

↓

ArgumentParser

↓

Namespace
```

Hoặc:

```
argv

↓

Parser

↓

Object
```

`ArgumentParser` chịu trách nhiệm:

* đọc `sys.argv`
* phân tích
* kiểm tra
* tạo đối tượng kết quả

---

# 8. Thêm tham số đầu tiên

```python
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("name")

args = parser.parse_args()

print(args)
```

Chạy:

```bash
python app.py Alice
```

Kết quả:

```python
Namespace(name='Alice')
```

Không còn phải nhớ:

```
argv[1]
```

mà dùng:

```python
args.name
```

---

# 9. Nếu thiếu tham số

```bash
python app.py
```

Kết quả:

```text
usage: app.py [-h] name

error:
the following arguments are required:

name
```

Điểm mạnh:

* tự báo lỗi
* tự in cách sử dụng
* tự thoát chương trình

---

# 10. `--help`

Đây là tính năng tuyệt vời của `argparse`.

```bash
python app.py --help
```

Kết quả:

```text
usage: app.py [-h] name

positional arguments:

name

options:

-h, --help
```

Không cần viết thêm dòng nào, `argparse` tự tạo.

---

# 11. Có nhiều tham số

```python
parser.add_argument("name")
parser.add_argument("age")
```

Chạy:

```bash
python app.py Alice 18
```

Kết quả:

```python
Namespace(
    name='Alice',
    age='18'
)
```

Lưu ý:

```
18
```

vẫn là **chuỗi** (`str`), vì mặc định `argparse` chưa chuyển kiểu dữ liệu.

---

# 12. `parse_args()` làm gì?

Quy trình:

```
python app.py Alice 18
```

↓

```
sys.argv
```

↓

```python
[
'app.py',
'Alice',
'18'
]
```

↓

`parse_args()`

↓

```python
Namespace(
    name='Alice',
    age='18'
)
```

---

# 13. Namespace là gì?

Hiện tại chỉ cần hiểu:

```
Namespace
```

là một đối tượng có các thuộc tính.

Ví dụ:

```python
args.name
```

```python
args.age
```

Tương đương:

```python
class Namespace:

    name = "Alice"

    age = "18"
```

Ở **Buổi 7**, chúng ta sẽ đi sâu vào `Namespace`, cách chuyển sang `dataclass`, và cách tích hợp với kiến trúc ứng dụng.

---

# 14. Luồng hoạt động của argparse

```
Người dùng

↓

python app.py Alice 18

↓

sys.argv

↓

ArgumentParser

↓

parse_args()

↓

Namespace

↓

Code của bạn
```

---

# 15. Ví dụ hoàn chỉnh

```python
import argparse

parser = argparse.ArgumentParser(
    description="Chương trình chào người dùng."
)

parser.add_argument("name")

args = parser.parse_args()

print(f"Xin chào {args.name}!")
```

Chạy:

```bash
python app.py Garden
```

Kết quả:

```
Xin chào Garden!
```

---

# 16. So sánh `sys.argv` và `argparse`

| Tiêu chí            | `sys.argv` | `argparse` |
| ------------------- | ---------- | ---------- |
| Đọc tham số         | ✔          | ✔          |
| Kiểm tra tham số    | ✘          | ✔          |
| `--help`            | ✘          | ✔          |
| Báo lỗi đẹp         | ✘          | ✔          |
| Chuyển kiểu dữ liệu | ✘          | ✔          |
| Subcommand          | ✘          | ✔          |
| Mở rộng             | Khó        | Dễ         |

---

# 17. Best Practices

* Không truy cập trực tiếp `sys.argv` nếu xây dựng CLI có nhiều tham số.
* Luôn tạo một `ArgumentParser` duy nhất ở điểm khởi đầu của chương trình.
* Thêm `description` để `--help` rõ ràng và chuyên nghiệp.
* Đặt tên tham số rõ nghĩa (`input_file`, `output_dir`, `config`) thay vì tên mơ hồ (`a`, `b`, `x`).
* Luôn thử chạy `--help` sau mỗi lần thêm tham số để kiểm tra trải nghiệm người dùng.

---

# 18. Bài tập thực hành

## Bài 1

Viết chương trình:

```bash
python hello.py Alice
```

Kết quả:

```
Hello Alice
```

---

## Bài 2

Nhận hai tham số:

```bash
python user.py Alice 25
```

In ra:

```
Name : Alice
Age  : 25
```

---

## Bài 3

Tạo chương trình:

```bash
python book.py Python
```

Kết quả:

```
Bạn đang đọc sách: Python
```

---

## Bài 4

Thêm `description` cho chương trình và kiểm tra kết quả khi chạy:

```bash
python app.py --help
```

Quan sát các mục:

* `usage`
* `description`
* `positional arguments`
* `options`

---

# Tổng kết

Trong buổi đầu tiên, bạn đã nắm được nền tảng của `argparse`:

* Hiểu vai trò của CLI trong phát triển phần mềm.
* Biết cách Python nhận tham số thông qua `sys.argv`.
* Thấy được những hạn chế của `sys.argv`.
* Sử dụng `ArgumentParser`, `add_argument()` và `parse_args()`.
* Hiểu `Namespace` ở mức cơ bản.
* Tạo chương trình CLI đầu tiên có hỗ trợ `--help`.

Ở **Buổi 2**, chúng ta sẽ **deep dive vào Positional Arguments**, bao gồm các tham số bắt buộc, `metavar`, `help`, `type`, `choices`, `nargs` và những kỹ thuật thiết kế giao diện dòng lệnh rõ ràng, chuyên nghiệp.
