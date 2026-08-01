# Buổi 24. File trong Python (Deep Dive)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu cách Python làm việc với File.
> * Thành thạo đọc và ghi file.
> * Biết các mode (`r`, `w`, `a`, `x`, `b`, `+`).
> * Hiểu Encoding (UTF-8, UTF-8 BOM...).
> * Sử dụng `with` đúng cách.
> * Đọc file lớn hiệu quả.
> * Xử lý ngoại lệ khi thao tác file.
> * Áp dụng vào các dự án thực tế như crawler, log, config.

---

# 1. File là gì?

File là nơi lưu trữ dữ liệu trên ổ đĩa.

Ví dụ:

```text
students.txt
config.json
story.html
app.log
image.png
database.db
```

Python coi tất cả đều là File.

---

# 2. Hàm `open()`

Đây là hàm cơ bản nhất.

```python
file = open(filename, mode, encoding=None)
```

Ví dụ:

```python
f = open("hello.txt")
```

Python trả về một **file object**.

```python
print(type(f))
```

Kết quả

```python
<class '_io.TextIOWrapper'>
```

---

# 3. File Object

Một File Object có nhiều phương thức.

```python
f.read()
f.readline()
f.readlines()

f.write()

f.close()

f.flush()

f.seek()

f.tell()
```

Bạn sẽ học lần lượt.

---

# 4. Mode của File

Đây là phần cực kỳ quan trọng.

| Mode | Ý nghĩa      |
| ---- | ------------ |
| `r`  | Đọc          |
| `w`  | Ghi mới      |
| `a`  | Ghi thêm     |
| `x`  | Tạo file mới |
| `b`  | Binary       |
| `t`  | Text         |
| `+`  | Đọc + Ghi    |

Ví dụ

```python
open("a.txt", "r")
```

```python
open("a.txt", "w")
```

```python
open("a.txt", "a")
```

---

# 5. Mode `r`

Đọc file.

Ví dụ

```text
hello.txt
```

```
Hello Python

File Example
```

Đọc

```python
f = open("hello.txt", "r", encoding="utf-8")

text = f.read()

print(text)

f.close()
```

Kết quả

```
Hello Python

File Example
```

Nếu file không tồn tại

```python
open("abc.txt")
```

Lỗi

```text
FileNotFoundError
```

---

# 6. Mode `w`

Ghi file.

```python
f = open("note.txt", "w", encoding="utf-8")

f.write("Hello")

f.close()
```

Nếu file chưa có

→ tạo mới.

Nếu file đã có

→ **xóa toàn bộ nội dung cũ** rồi ghi lại.

Ví dụ

```
Old Content
```

Sau

```python
open("note.txt", "w")
```

File sẽ thành

```
Hello
```

---

# 7. Mode `a`

Append.

```python
f = open("note.txt", "a", encoding="utf-8")

f.write("\nPython")

f.close()
```

Kết quả

```
Hello

Python
```

Không mất dữ liệu cũ.

---

# 8. Mode `x`

Tạo file mới.

```python
open("new.txt", "x")
```

Nếu file đã tồn tại

```text
FileExistsError
```

Mode này hữu ích khi bạn muốn đảm bảo không ghi đè dữ liệu.

---

# 9. Đóng File

Sau khi dùng xong

```python
f.close()
```

Nếu quên đóng

* File có thể chưa ghi hết.
* Tốn tài nguyên.
* Một số hệ điều hành khóa file.

---

# 10. `with` (Khuyến nghị)

Đây là cách chuyên nghiệp.

```python
with open("hello.txt", "r", encoding="utf-8") as f:
    text = f.read()

print(text)
```

Khi ra khỏi khối `with`

Python tự động:

```python
f.close()
```

Đây là lý do hầu hết mã nguồn Python hiện đại đều dùng `with`.

---

# 11. `read()`

Đọc toàn bộ file.

```python
with open("story.txt", encoding="utf-8") as f:
    data = f.read()

print(data)
```

Nếu file 2 MB

→ đọc 2 MB.

Nếu file 5 GB

→ đọc 5 GB vào RAM.

Không phù hợp với file rất lớn.

---

# 12. Đọc một phần

Có thể truyền số ký tự.

```python
with open("story.txt", encoding="utf-8") as f:
    print(f.read(10))
```

Ví dụ

```
Hello Pyt
```

Chỉ đọc 10 ký tự.

---

# 13. `readline()`

Đọc từng dòng.

Ví dụ

```
A
B
C
```

```python
with open("data.txt", encoding="utf-8") as f:
    print(f.readline())
    print(f.readline())
```

Kết quả

```
A

B
```

Mỗi lần gọi sẽ đọc tiếp từ vị trí hiện tại.

---

# 14. `readlines()`

```python
with open("data.txt", encoding="utf-8") as f:
    lines = f.readlines()

print(lines)
```

Kết quả

```python
["A\n", "B\n", "C"]
```

Đây là một danh sách các dòng.

---

# 15. Đọc bằng vòng lặp (Khuyến nghị)

Đây là cách hiệu quả nhất.

```python
with open("story.txt", encoding="utf-8") as f:
    for line in f:
        print(line.strip())
```

Ưu điểm:

* Không đọc toàn bộ file vào RAM.
* Phù hợp với file hàng GB.

---

# 16. `write()`

```python
with open("result.txt", "w", encoding="utf-8") as f:
    f.write("Python")
```

`write()` trả về số ký tự đã ghi.

```python
n = f.write("Hello")

print(n)
```

Kết quả

```
5
```

---

# 17. Ghi nhiều dòng

```python
with open("note.txt", "w", encoding="utf-8") as f:
    f.write("A\n")
    f.write("B\n")
    f.write("C\n")
```

---

# 18. `writelines()`

```python
lines = ["One\n", "Two\n", "Three\n"]

with open("a.txt", "w", encoding="utf-8") as f:
    f.writelines(lines)
```

Lưu ý:

`writelines()` **không tự thêm `\n`**.

---

# 19. Con trỏ File

Python luôn có một vị trí hiện tại.

Ví dụ

```
ABCDEFG
```

Đọc

```python
f.read(3)
```

Đọc được

```
ABC
```

Con trỏ đang ở

```
DEFG
^
```

Nếu tiếp tục

```python
f.read(2)
```

Kết quả

```
DE
```

---

# 20. `tell()`

Cho biết vị trí hiện tại.

```python
with open("hello.txt", encoding="utf-8") as f:
    print(f.tell())

    f.read(5)

    print(f.tell())
```

Ví dụ

```
0

5
```

---

# 21. `seek()`

Di chuyển con trỏ.

```python
with open("hello.txt", encoding="utf-8") as f:
    print(f.read(5))

    f.seek(0)

    print(f.read(5))
```

Kết quả

```
Hello

Hello
```

---

# 22. Binary File

Đọc ảnh.

```python
with open("cat.jpg", "rb") as f:
    data = f.read()
```

Ghi ảnh.

```python
with open("copy.jpg", "wb") as f:
    f.write(data)
```

Mode:

```
rb

wb

ab
```

---

# 23. Encoding

Đây là lỗi rất nhiều người mới gặp.

Sai

```python
open("vietnamese.txt")
```

Có thể lỗi

```
UnicodeDecodeError
```

Đúng

```python
open("vietnamese.txt", encoding="utf-8")
```

**Khuyến nghị:** Luôn chỉ rõ `encoding="utf-8"` khi làm việc với file văn bản.

---

# 24. Xử lý lỗi

```python
try:
    with open("abc.txt", encoding="utf-8") as f:
        print(f.read())

except FileNotFoundError:
    print("Không tìm thấy file")
```

---

# 25. Ví dụ thực tế: Ghi Log

```python
from datetime import datetime

with open("app.log", "a", encoding="utf-8") as f:
    f.write(f"{datetime.now()} - Start Program\n")
```

Kết quả

```
2026-08-01 09:15:00 - Start Program
2026-08-01 09:30:00 - Start Program
```

Mỗi lần chạy sẽ thêm một dòng mới.

---

# 26. Ví dụ thực tế: Đọc Config

**config.txt**

```
host=localhost
port=3306
debug=True
```

Đọc:

```python
config = {}

with open("config.txt", encoding="utf-8") as f:
    for line in f:
        key, value = line.strip().split("=")
        config[key] = value

print(config)
```

Kết quả

```python
{"host": "localhost", "port": "3306", "debug": "True"}
```

---

# 27. Ví dụ thực tế: Đếm số dòng

```python
count = 0

with open("story.txt", encoding="utf-8") as f:
    for _ in f:
        count += 1

print(count)
```

Không cần đọc toàn bộ file vào bộ nhớ.

---

# 28. Best Practices

## ✔ Luôn dùng `with`

```python
with open(...) as f:
    ...
```

---

## ✔ Luôn chỉ rõ Encoding

```python
encoding = "utf-8"
```

---

## ✔ Không dùng `read()` với file quá lớn

Thay vào đó:

```python
for line in f:
    ...
```

---

## ✔ Xử lý ngoại lệ

```python
try:
    ...
except FileNotFoundError:
    ...
```

---

## ✔ Không ghi đè ngoài ý muốn

Kiểm tra mode:

* `w` → Ghi mới, xóa dữ liệu cũ.
* `a` → Ghi thêm.
* `x` → Chỉ tạo nếu chưa tồn tại.

---

# 29. Tổng kết

| Phương thức    | Chức năng                           |
| -------------- | ----------------------------------- |
| `open()`       | Mở file                             |
| `close()`      | Đóng file                           |
| `read()`       | Đọc toàn bộ hoặc một phần           |
| `readline()`   | Đọc một dòng                        |
| `readlines()`  | Đọc tất cả các dòng thành danh sách |
| `write()`      | Ghi chuỗi                           |
| `writelines()` | Ghi nhiều chuỗi                     |
| `tell()`       | Xem vị trí con trỏ                  |
| `seek()`       | Di chuyển con trỏ                   |

---

# Bài tập thực hành

### Bài 1

Tạo file `students.txt` chứa 5 tên học sinh. Đọc và in toàn bộ nội dung.

### Bài 2

Đếm số dòng, số từ và số ký tự trong `students.txt`.

### Bài 3

Viết chương trình sao chép nội dung từ `input.txt` sang `output.txt`.

### Bài 4

Viết chương trình ghi nhật ký (`app.log`) theo định dạng:

```
2026-08-01 10:00:00 - Login
2026-08-01 10:05:12 - Logout
```

Mỗi lần chạy chương trình phải **ghi thêm** chứ không được ghi đè.

### Bài 5

Viết hàm:

```python
def tail(filename: str, n: int = 10) -> list[str]:
    """Trả về n dòng cuối cùng của file."""
```

Đây là bài tập mô phỏng lệnh `tail` trên Linux.

### Bài 6 (Thử thách)

Viết chương trình đọc một file văn bản rất lớn (ví dụ vài trăm MB nếu có), sau đó:

* Đếm số dòng.
* Đếm số từ.
* Đếm số ký tự.
* Không được dùng `read()` hoặc `readlines()`.
* Chỉ sử dụng vòng lặp:

```python
for line in f:
    ...
```

Đây là kỹ thuật thường dùng trong các hệ thống xử lý log, crawler và ETL vì tiết kiệm bộ nhớ.

---

## Chuẩn bị cho buổi sau

Ở **Buổi 25**, chúng ta sẽ học **CSV**, bao gồm:

* Module `csv`.
* `reader()` và `writer()`.
* `DictReader()` và `DictWriter()`.
* Các tùy chọn như `delimiter`, `quotechar`.
* Đọc/ghi file CSV theo chuẩn.
* Xây dựng một **hệ thống quản lý sinh viên bằng CSV**, mô phỏng cách nhiều ứng dụng thực tế lưu trữ dữ liệu đơn giản mà không cần cơ sở dữ liệu.
