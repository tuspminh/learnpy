# Buổi 26. JSON trong Python (Deep Dive)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu JSON là gì và vì sao nó được dùng ở hầu hết ứng dụng hiện đại.
> * Thành thạo module `json`.
> * Phân biệt `dump()` và `dumps()`.
> * Phân biệt `load()` và `loads()`.
> * Chuyển đổi giữa JSON và đối tượng Python.
> * Xử lý Unicode, Pretty Print.
> * Tự viết `JSONEncoder`.
> * Làm việc với file cấu hình và API.

---

# 1. JSON là gì?

JSON (**JavaScript Object Notation**) là định dạng trao đổi dữ liệu phổ biến nhất hiện nay.

Ví dụ:

```json
{
    "name": "Alice",
    "age": 20,
    "is_student": true
}
```

JSON được dùng ở:

* REST API
* Flask
* FastAPI
* Django
* Crawler
* Config file
* Database NoSQL
* JavaScript
* Mobile App

Hầu như mọi ứng dụng hiện đại đều sử dụng JSON.

---

# 2. JSON và Python

| JSON   | Python      |
| ------ | ----------- |
| Object | dict        |
| Array  | list        |
| String | str         |
| Number | int / float |
| true   | True        |
| false  | False       |
| null   | None        |

Ví dụ

JSON

```json
{
    "name": "Alice",
    "age": 20
}
```

Python

```python
{"name": "Alice", "age": 20}
```

Rất giống nhau.

---

# 3. Module `json`

Python có sẵn module:

```python
import json
```

Không cần cài thêm.

---

# 4. `dumps()`

`dumps()`

```
Python Object
        │
        ▼
JSON String
```

Ví dụ

```python
import json

student = {"name": "Alice", "age": 20}

text = json.dumps(student)

print(text)
```

Kết quả

```text
{"name": "Alice", "age": 20}
```

Kiểu dữ liệu

```python
print(type(text))
```

Kết quả

```python
<class 'str'>
```

Đây là **chuỗi JSON**, chưa phải file.

---

# 5. `dump()`

`dump()`

```
Python Object
        │
        ▼
JSON File
```

Ví dụ

```python
import json

student = {"name": "Alice", "age": 20}

with open("student.json", "w", encoding="utf-8") as f:
    json.dump(student, f)
```

File

```json
{"name": "Alice", "age": 20}
```

---

# 6. `loads()`

`loads()`

```
JSON String
        │
        ▼
Python Object
```

Ví dụ

```python
import json

text = '{"name":"Bob","age":25}'

student = json.loads(text)

print(student)
```

Kết quả

```python
{"name": "Bob", "age": 25}
```

Kiểu

```python
print(type(student))
```

Kết quả

```python
<class 'dict'>
```

---

# 7. `load()`

`load()`

```
JSON File
        │
        ▼
Python Object
```

Ví dụ

```python
import json

with open("student.json", encoding="utf-8") as f:
    student = json.load(f)

print(student)
```

---

# 8. Sơ đồ tổng quát

```
dict
 │
 │ dumps()
 ▼
JSON String

dict
 │
 │ dump()
 ▼
JSON File

JSON String
 │
 │ loads()
 ▼
dict

JSON File
 │
 │ load()
 ▼
dict
```

Đây là bốn hàm quan trọng nhất của module `json`.

---

# 9. Pretty Print

Thông thường

```python
json.dumps(student)
```

Kết quả

```json
{"name":"Alice","age":20}
```

Khó đọc.

Dùng

```python
print(json.dumps(student, indent=4))
```

Kết quả

```json
{
    "name": "Alice",
    "age": 20
}
```

---

# 10. Unicode

Ví dụ

```python
student = {"name": "Nguyễn Văn A"}
```

Nếu

```python
json.dumps(student)
```

Kết quả

```text
{"name":"Nguy\u1ec5n V\u0103n A"}
```

Khó đọc.

Đúng:

```python
json.dumps(student, ensure_ascii=False)
```

Kết quả

```text
{"name":"Nguyễn Văn A"}
```

Khuyến nghị:

```python
ensure_ascii = False
```

---

# 11. Ghi file đẹp

```python
with open("config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4, ensure_ascii=False)
```

File

```json
{
    "host": "localhost",
    "port": 3306
}
```

---

# 12. JSON List

```python
students = [{"name": "Alice"}, {"name": "Bob"}]
```

```python
json.dumps(students, indent=4)
```

---

# 13. Đọc Config

Ví dụ

```json
{
    "host":"localhost",
    "port":3306,
    "debug":true
}
```

Đọc

```python
import json

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

print(config["host"])
```

Output

```text
localhost
```

Đây là cách rất nhiều ứng dụng Python lưu cấu hình.

---

# 14. Ghi Config

```python
config = {"host": "localhost", "port": 3306, "theme": "dark"}

with open("config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4, ensure_ascii=False)
```

---

# 15. Cập nhật JSON

```python
import json

with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

config["debug"] = False

with open("config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4)
```

Quy trình:

```
Đọc

↓

Sửa

↓

Ghi lại
```

---

# 16. JSONEncoder

Một số object không thể chuyển thành JSON.

Ví dụ

```python
from datetime import datetime

student = {"time": datetime.now()}
```

```python
json.dumps(student)
```

Lỗi

```text
TypeError
```

Giải quyết

```python
import json
from datetime import datetime


class DateEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, datetime):
            return obj.isoformat()

        return super().default(obj)
```

Sử dụng

```python
json.dumps(student, cls=DateEncoder, indent=4)
```

---

# 17. `default`

Có thể viết ngắn hơn.

```python
from datetime import datetime
import json

student = {"created": datetime.now()}

text = json.dumps(student, default=str)

print(text)
```

---

# 18. Ví dụ thực tế - API

Server trả về

```json
{
    "status": "ok",
    "data": {
        "id": 1,
        "name": "Alice"
    }
}
```

Python

```python
response = json.loads(text)

print(response["data"]["name"])
```

---

# 19. Ví dụ thực tế - Crawler

```python
stories = [{"title": "Story A", "author": "AAA"}, {"title": "Story B", "author": "BBB"}]

with open("stories.json", "w", encoding="utf-8") as f:
    json.dump(stories, f, indent=4, ensure_ascii=False)
```

---

# 20. Chuyển JSON thành Dataclass

Giả sử

```json
{
    "id":1,
    "name":"Alice",
    "age":20
}
```

Python

```python
from dataclasses import dataclass


@dataclass
class Student:
    id: int
    name: str
    age: int
```

Đọc

```python
import json

with open("student.json") as f:
    data = json.load(f)

student = Student(**data)

print(student)
```

Đây là kỹ thuật rất phổ biến trong các dự án Python hiện đại.

---

# 21. Những lỗi thường gặp

## Sai dấu ngoặc kép

Sai:

```text
{'name':'Alice'}
```

Đây là Python Dictionary, không phải JSON.

JSON đúng:

```json
{"name":"Alice"}
```

JSON **bắt buộc** dùng dấu ngoặc kép (`"`).

---

## Dùng dấu phẩy cuối

Sai:

```json
{
    "name":"Alice",
}
```

JSON chuẩn không cho phép dấu phẩy cuối cùng.

---

## Không hỗ trợ mọi kiểu dữ liệu

JSON hỗ trợ:

* dict
* list
* str
* int
* float
* bool
* None

Không hỗ trợ trực tiếp:

* `datetime`
* `set`
* `bytes`
* đối tượng tự định nghĩa

Cần chuyển đổi trước hoặc dùng `default`/`JSONEncoder`.

---

# 22. Best Practices

## ✔ Luôn dùng UTF-8

```python
encoding = "utf-8"
```

---

## ✔ Luôn dùng

```python
ensure_ascii = False
```

để hiển thị tiếng Việt đúng.

---

## ✔ Format đẹp

```python
indent = 4
```

---

## ✔ Không chỉnh sửa JSON bằng nối chuỗi

Sai:

```python
text = '{"name":"' + name + '"}'
```

Đúng:

```python
json.dumps(obj)
```

---

## ✔ Không dùng `eval()`

Sai:

```python
eval(json_text)
```

Đúng:

```python
json.loads(json_text)
```

`eval()` có thể thực thi mã độc nếu dữ liệu đến từ nguồn không tin cậy.

---

# 23. Mini Project - Config Manager

## Cấu trúc

```text
project/

├── config.json
└── main.py
```

**config.json**

```json
{
    "theme": "dark",
    "language": "vi",
    "font_size": 14
}
```

### Chức năng

* Đọc cấu hình.
* Hiển thị cấu hình.
* Thay đổi giá trị.
* Lưu lại file JSON.
* Khôi phục cấu hình mặc định.

Đây là mô hình thường thấy trong các ứng dụng desktop (PySide6), web hoặc CLI.

---

# Tổng kết

Sau buổi học này, bạn đã nắm được:

* Cấu trúc và vai trò của JSON.
* Bốn hàm cốt lõi: `dump()`, `dumps()`, `load()`, `loads()`.
* Chuyển đổi giữa JSON và đối tượng Python.
* Pretty Print với `indent`.
* Hiển thị Unicode bằng `ensure_ascii=False`.
* Tùy biến quá trình mã hóa với `JSONEncoder`.
* Đọc, ghi và cập nhật file cấu hình JSON.

# Bài tập thực hành

### Bài 1

Tạo `student.json` chứa thông tin một sinh viên, sau đó đọc và in ra màn hình.

### Bài 2

Tạo danh sách 10 sinh viên, lưu vào `students.json` với `indent=4` và `ensure_ascii=False`.

### Bài 3

Viết chương trình đọc `config.json`, thay đổi giá trị `theme` từ `"light"` sang `"dark"` rồi ghi lại file.

### Bài 4

Tạo `@dataclass Student`, đọc dữ liệu từ `student.json` và khởi tạo đối tượng bằng:

```python
student = Student(**data)
```

### Bài 5

Tạo một lớp `Event` có thuộc tính `created_at` là `datetime`, sau đó viết `JSONEncoder` để chuyển đối tượng này thành JSON.

### Bài 6 (Thử thách)

Xây dựng **Settings Manager**:

```text
===== Settings Manager =====
1. Xem cấu hình
2. Thay đổi theme
3. Thay đổi ngôn ngữ
4. Đặt lại mặc định
5. Lưu cấu hình
6. Thoát
```

Toàn bộ cấu hình được lưu trong `config.json`, chương trình phải tự đọc khi khởi động và tự ghi lại khi người dùng thay đổi.

---

## Chuẩn bị cho buổi sau

Ở **Buổi 27**, chúng ta sẽ học **Datetime**, bao gồm:

* `date`, `time`, `datetime`.
* `timedelta`.
* `strftime()` và `strptime()`.
* Timezone.
* So sánh và tính toán thời gian.
* Các bài toán thực tế như tính tuổi, đếm ngược, ghi log và xử lý thời gian trong hệ thống.
