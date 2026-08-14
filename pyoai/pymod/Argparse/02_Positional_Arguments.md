# Buổi 2 — Positional Arguments Deep Dive

> **Mục tiêu**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu sâu về Positional Argument.
> * Biết `add_argument()` hoạt động như thế nào.
> * Thành thạo `type`, `metavar`, `help`, `choices`, `nargs`.
> * Biết cách thiết kế CLI dễ sử dụng.
> * Hiểu các lỗi thường gặp và cách xử lý.

---

# 1. Positional Argument là gì?

Positional Argument là tham số **được xác định bởi vị trí** trên dòng lệnh.

Ví dụ:

```bash
python app.py Alice 20
```

Ở đây:

```
Alice
```

là tham số thứ nhất.

```
20
```

là tham số thứ hai.

Thứ tự **không được đổi**.

Ví dụ:

```bash
python app.py 20 Alice
```

`argparse` sẽ hiểu:

```
name = "20"

age = "Alice"
```

Nó **không biết** bạn đã nhập nhầm.

---

# 2. add_argument()

Đây là hàm quan trọng nhất của argparse.

Ví dụ đơn giản:

```python
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("name")

args = parser.parse_args()

print(args)
```

Kết quả:

```bash
python app.py Alice
```

↓

```
Namespace(name='Alice')
```

---

## Thêm nhiều tham số

```python
parser.add_argument("name")
parser.add_argument("age")
parser.add_argument("city")
```

Chạy:

```bash
python app.py Alice 20 Hanoi
```

↓

```
Namespace(
    name='Alice',
    age='20',
    city='Hanoi'
)
```

---

# 3. add_argument() nhận những gì?

Các tham số thường dùng:

```python
parser.add_argument(

    "name",

    type=str,

    help="Tên người dùng",

    metavar="USERNAME",

    choices=[...],

    nargs="?"

)
```

Trong buổi này chúng ta sẽ học từng phần.

---

# 4. type

Mặc định:

```
mọi dữ liệu đều là str
```

Ví dụ:

```python
parser.add_argument("age")
```

```
18
```

↓

```
"18"
```

Không phải số.

---

Muốn chuyển sang int:

```python
parser.add_argument(
    "age",
    type=int
)
```

Chạy:

```bash
python app.py 18
```

↓

```
Namespace(age=18)
```

Lúc này:

```python
print(type(args.age))
```

↓

```python
<class 'int'>
```

---

# 5. Khi type sai

Ví dụ:

```bash
python app.py abc
```

Kết quả:

```
error:
argument age:

invalid int value: 'abc'
```

Không cần tự viết:

```python
try:
    ...
except:
```

`argparse` tự kiểm tra.

---

# 6. Nhiều kiểu dữ liệu

## float

```python
parser.add_argument(
    "price",
    type=float
)
```

```
19.5
```

↓

```
19.5
```

---

## str

```python
type=str
```

---

## bool?

Đây là lỗi người mới hay mắc.

KHÔNG làm:

```python
type=bool
```

Ví dụ:

```bash
python app.py False
```

↓

```
True
```

Vì:

```python
bool("False")
```

↓

```
True
```

Để xử lý cờ bật/tắt, `argparse` sử dụng `action="store_true"` hoặc `action="store_false"`, chúng ta sẽ học kỹ ở **Buổi 4**.

---

# 7. help

Ví dụ:

```python
parser.add_argument(

    "name",

    help="Tên người dùng"

)
```

Chạy:

```bash
python app.py --help
```

↓

```
positional arguments:

name

Tên người dùng
```

Không có `help`:

```
name
```

Có `help`:

```
name

Tên người dùng
```

Giúp CLI chuyên nghiệp hơn.

---

# 8. metavar

Mặc định:

```python
parser.add_argument("name")
```

`--help`

↓

```
usage:

app.py name
```

---

Có thể đổi:

```python
parser.add_argument(

    "name",

    metavar="USERNAME"

)
```

↓

```
usage:

app.py USERNAME
```

Đây chỉ thay đổi **cách hiển thị**, không thay đổi tên thuộc tính:

```python
args.name
```

vẫn là:

```
name
```

---

# 9. choices

Giới hạn giá trị.

Ví dụ:

```python
parser.add_argument(

    "mode",

    choices=[
        "fast",
        "slow"
    ]
)
```

Đúng:

```bash
python app.py fast
```

Sai:

```bash
python app.py medium
```

↓

```
invalid choice

choose from

fast

slow
```

Rất hữu ích khi chỉ chấp nhận một số giá trị cố định.

---

# 10. nargs

Đây là một trong những tính năng mạnh nhất của `argparse`.

Ví dụ:

```python
parser.add_argument(

    "files",

    nargs="+"

)
```

Chạy:

```bash
python app.py a.txt b.txt c.txt
```

↓

```
Namespace(

files=[

'a.txt',

'b.txt',

'c.txt'

]
)
```

Tức là:

```
1 hoặc nhiều
```

tham số.

Các giá trị `nargs` sẽ được học chi tiết ở **Buổi 6**, nhưng bạn nên biết trước ý nghĩa:

| Giá trị | Ý nghĩa                                                         |
| ------- | --------------------------------------------------------------- |
| `1`     | Đúng 1 giá trị (ít dùng vì kết quả là danh sách có một phần tử) |
| `2`     | Đúng 2 giá trị                                                  |
| `3`     | Đúng 3 giá trị                                                  |
| `?`     | 0 hoặc 1 giá trị                                                |
| `*`     | 0 hoặc nhiều                                                    |
| `+`     | 1 hoặc nhiều                                                    |

---

# 11. Ví dụ thực tế

## Chương trình cộng hai số

```python
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "a",
    type=float,
    help="Số thứ nhất"
)

parser.add_argument(
    "b",
    type=float,
    help="Số thứ hai"
)

args = parser.parse_args()

print(args.a + args.b)
```

Chạy:

```bash
python add.py 12.5 7.5
```

↓

```
20.0
```

---

# 12. Ví dụ: Book CLI

```python
import argparse

parser = argparse.ArgumentParser(
    description="Quản lý sách"
)

parser.add_argument(
    "title",
    help="Tên sách"
)

parser.add_argument(
    "category",
    choices=[
        "novel",
        "comic",
        "science"
    ],
    help="Thể loại"
)

args = parser.parse_args()

print(args)
```

Chạy:

```bash
python book.py Dune science
```

↓

```
Namespace(

title='Dune',

category='science'

)
```

---

# 13. Ví dụ: Resize ảnh

```bash
python resize.py image.jpg 800 600
```

```python
parser.add_argument("image")

parser.add_argument(
    "width",
    type=int
)

parser.add_argument(
    "height",
    type=int
)
```

↓

```
image.jpg

800

600
```

---

# 14. Những lỗi thường gặp

## Lỗi 1

```python
type=bool
```

❌ Không nên.

---

## Lỗi 2

Quên `help`

↓

`--help` rất khó đọc.

---

## Lỗi 3

Tên tham số không rõ ràng

Không nên:

```python
parser.add_argument("x")
```

Nên:

```python
parser.add_argument("filename")
```

---

## Lỗi 4

Không dùng `choices`

Ví dụ:

```
fast

slow

debug
```

Nếu không dùng `choices`, người dùng có thể nhập:

```
abc
```

và bạn phải tự kiểm tra sau này.

---

# 15. Best Practices

## Đặt tên rõ nghĩa

```python
input_file
```

tốt hơn:

```python
f
```

---

## Có help

Luôn viết:

```python
help="..."
```

---

## Có type

Không nên:

```python
age
```

Nên:

```python
type=int
```

---

## Có choices nếu giá trị hữu hạn

Ví dụ:

```python
choices=[
    "json",
    "csv",
    "xml"
]
```

---

## Thiết kế CLI nhất quán

Nếu chương trình có nhiều tham số, hãy sắp xếp theo mức độ quan trọng:

```bash
python export.py INPUT_FILE OUTPUT_DIR FORMAT
```

thay vì thứ tự ngẫu nhiên.

---

# 16. Bài tập thực hành

### Bài 1

Viết chương trình:

```bash
python hello.py Alice
```

↓

```
Xin chào Alice
```

Yêu cầu:

* Có `help`
* Có `description`

---

### Bài 2

Viết chương trình tính diện tích hình chữ nhật.

```bash
python area.py 20 15
```

↓

```
300
```

Yêu cầu:

* `width`
* `height`
* `type=int`

---

### Bài 3

Viết chương trình:

```bash
python convert.py input.jpg png
```

Chỉ chấp nhận:

```
png
jpg
webp
```

Sử dụng:

```python
choices=[...]
```

---

### Bài 4

Viết chương trình:

```bash
python movie.py "Interstellar" science
```

Trong đó:

* `title`
* `genre`

`genre` chỉ được phép là:

* action
* comedy
* science
* horror

---

# Tổng kết

Trong buổi này, bạn đã học được các khái niệm cốt lõi của **Positional Arguments**:

* Hiểu cách `add_argument()` khai báo tham số theo vị trí.
* Sử dụng `type` để chuyển đổi và kiểm tra kiểu dữ liệu.
* Viết `help` để tạo tài liệu `--help` rõ ràng.
* Dùng `metavar` để cải thiện cách hiển thị mà không đổi tên thuộc tính.
* Giới hạn giá trị hợp lệ bằng `choices`.
* Làm quen với `nargs` để nhận nhiều giá trị từ dòng lệnh.

Ở **Buổi 3**, chúng ta sẽ chuyển sang **Optional Arguments** (`-o`, `--output`, `--config`, `--verbose`...), nền tảng để xây dựng các CLI chuyên nghiệp như `git`, `docker`, `pip` và `uv`.
