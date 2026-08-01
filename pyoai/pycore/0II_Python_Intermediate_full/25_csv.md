# Buổi 25. CSV trong Python (Deep Dive)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu CSV là gì và tại sao nó được dùng rất phổ biến.
> * Thành thạo module `csv`.
> * Biết cách sử dụng `reader()`, `writer()`, `DictReader()`, `DictWriter()`.
> * Hiểu `delimiter`, `quotechar`, `quoting`, `newline`.
> * Xử lý dữ liệu CSV có dấu tiếng Việt (UTF-8).
> * Áp dụng CSV vào các dự án thực tế như crawler, xuất báo cáo, quản lý dữ liệu.

---

# 1. CSV là gì?

CSV (**Comma-Separated Values**) là định dạng lưu trữ dữ liệu dạng bảng.

Ví dụ:

```text
id,name,age
1,Alice,20
2,Bob,25
3,Charlie,22
```

Mỗi dòng là một bản ghi.

Mỗi cột được ngăn cách bởi dấu phẩy.

CSV được hỗ trợ bởi:

* Excel
* Google Sheets
* LibreOffice
* Pandas
* Cơ sở dữ liệu
* Hầu hết các ngôn ngữ lập trình

---

# 2. Tại sao dùng CSV?

Ví dụ quản lý sinh viên:

| id | name | age |
| -- | ---- | --- |
| 1  | An   | 20  |
| 2  | Bình | 21  |

Có thể lưu:

```text
students.csv
```

Không cần SQLite.

Không cần MySQL.

Rất phù hợp cho:

* Danh sách sinh viên
* Danh sách sản phẩm
* Kết quả crawler
* Báo cáo thống kê
* Import/Export dữ liệu

---

# 3. Module `csv`

Python có sẵn module:

```python
import csv
```

Không cần cài thêm.

---

# 4. Đọc CSV bằng `reader()`

**students.csv**

```csv
id,name,age
1,Alice,20
2,Bob,25
3,Charlie,22
```

Đọc:

```python
import csv

with open("students.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)

    for row in reader:
        print(row)
```

Kết quả:

```python
["id", "name", "age"]
["1", "Alice", "20"]
["2", "Bob", "25"]
["3", "Charlie", "22"]
```

Lưu ý: Mỗi dòng là một `list[str]`.

---

# 5. Vì sao dùng `newline=""`?

Khi mở file CSV để đọc hoặc ghi, nên luôn dùng:

```python
open("students.csv", newline="", encoding="utf-8")
```

Lý do:

* Tránh xuất hiện dòng trống dư trên Windows.
* Để module `csv` tự xử lý ký tự xuống dòng.

Đây là khuyến nghị chính thức của Python.

---

# 6. Bỏ qua dòng tiêu đề

```python
import csv

with open("students.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)

    next(reader)

    for row in reader:
        print(row)
```

Output:

```python
["1", "Alice", "20"]
["2", "Bob", "25"]
["3", "Charlie", "22"]
```

---

# 7. Truy cập dữ liệu

```python
for row in reader:
    print(row[0])
    print(row[1])
    print(row[2])
```

Kết quả:

```text
1
Alice
20
```

Nhược điểm:

```python
row[1]
```

không rõ ý nghĩa.

Đó là lý do `DictReader` rất hữu ích.

---

# 8. `DictReader`

```python
import csv

with open("students.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        print(row)
```

Kết quả:

```python
{"id": "1", "name": "Alice", "age": "20"}
```

Mỗi dòng là một dictionary.

---

# 9. Truy cập bằng tên cột

```python
for row in reader:
    print(row["name"])
```

Kết quả:

```text
Alice
Bob
Charlie
```

Dễ đọc hơn rất nhiều.

---

# 10. Ghi CSV bằng `writer()`

```python
import csv

with open("students.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow(["id", "name", "age"])

    writer.writerow([1, "Alice", 20])

    writer.writerow([2, "Bob", 25])
```

Kết quả:

```csv
id,name,age
1,Alice,20
2,Bob,25
```

---

# 11. Ghi nhiều dòng

```python
rows = [[1, "Alice", 20], [2, "Bob", 25], [3, "Charlie", 22]]

with open("students.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow(["id", "name", "age"])

    writer.writerows(rows)
```

---

# 12. `DictWriter`

```python
import csv

with open("students.csv", "w", newline="", encoding="utf-8") as f:
    fields = ["id", "name", "age"]

    writer = csv.DictWriter(f, fieldnames=fields)

    writer.writeheader()

    writer.writerow({"id": 1, "name": "Alice", "age": 20})
```

---

# 13. Ghi nhiều Dictionary

```python
writer.writerows(
    [{"id": 1, "name": "Alice", "age": 20}, {"id": 2, "name": "Bob", "age": 25}]
)
```

---

# 14. `delimiter`

Mặc định:

```text
,
```

Có thể đổi thành:

```text
;
```

Ví dụ:

```python
writer = csv.writer(f, delimiter=";")
```

Kết quả:

```text
id;name;age
1;Alice;20
```

Điều này hữu ích khi làm việc với các hệ thống sử dụng dấu `;` thay vì dấu `,`.

---

# 15. `quotechar`

Nếu dữ liệu chứa dấu phẩy:

```text
Hello, World
```

CSV sẽ ghi:

```csv
"Hello, World"
```

Ví dụ:

```python
writer = csv.writer(f, quotechar='"')
```

---

# 16. `quoting`

Một số lựa chọn:

```python
csv.QUOTE_MINIMAL
csv.QUOTE_ALL
csv.QUOTE_NONNUMERIC
csv.QUOTE_NONE
```

Ví dụ:

```python
writer = csv.writer(f, quoting=csv.QUOTE_ALL)
```

Kết quả:

```csv
"id","name","age"
"1","Alice","20"
```

---

# 17. CSV và tiếng Việt

Luôn dùng:

```python
encoding = "utf-8"
```

Ví dụ:

```csv
id,name
1,Nguyễn Văn A
2,Trần Thị B
```

Nếu mở bằng Excel trên Windows mà bị lỗi dấu tiếng Việt, bạn có thể ghi với:

```python
encoding = "utf-8-sig"
```

Điều này thêm BOM để nhiều phiên bản Excel nhận diện UTF-8 tốt hơn.

---

# 18. Ví dụ thực tế: Xuất dữ liệu crawler

```python
import csv

stories = [
    {"title": "Truyện A", "author": "Tác giả A"},
    {"title": "Truyện B", "author": "Tác giả B"},
]

with open("stories.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "author"])

    writer.writeheader()

    writer.writerows(stories)
```

---

# 19. Ví dụ thực tế: Đọc danh sách người dùng

```python
import csv

with open("users.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for user in reader:
        print(user["name"], user["email"])
```

---

# 20. Chuyển CSV thành đối tượng

Giả sử:

```csv
id,name,age
1,Alice,20
2,Bob,25
```

Ta có:

```python
from dataclasses import dataclass
import csv


@dataclass
class Student:
    id: int
    name: str
    age: int


students = []

with open("students.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        students.append(
            Student(id=int(row["id"]), name=row["name"], age=int(row["age"]))
        )

for s in students:
    print(s)
```

Đây là bước đệm rất quan trọng trước khi học `dataclass` ở Buổi 36.

---

# 21. Best Practices

## ✔ Luôn dùng `newline=""`

```python
open(filename, newline="", encoding="utf-8")
```

---

## ✔ Dùng `DictReader`

Thay vì:

```python
row[1]
```

Nên:

```python
row["name"]
```

---

## ✔ Luôn chỉ rõ `encoding`

```python
encoding = "utf-8"
```

Hoặc:

```python
encoding = "utf-8-sig"
```

nếu cần tương thích tốt hơn với Excel.

---

## ✔ Không tự tách chuỗi bằng `split(",")`

Sai:

```python
line.split(",")
```

Ví dụ dòng:

```csv
1,"Nguyễn, Văn A",20
```

`split(",")` sẽ tách sai.

Module `csv` xử lý đúng các trường hợp có dấu phân cách trong dữ liệu.

---

## ✔ Chuyển kiểu dữ liệu

CSV chỉ lưu chuỗi.

Nên:

```python
age = int(row["age"])
```

Không nên để:

```python
age = row["age"]
```

nếu bạn cần tính toán.

---

# 22. Mini Project - Quản lý sinh viên bằng CSV

## Cấu trúc

```text
student_manager/

├── main.py
├── students.csv
└── student_service.py
```

## Định dạng `students.csv`

```csv
id,name,age
1,Nguyễn Văn A,20
2,Trần Thị B,21
```

## Chức năng

* Thêm sinh viên.
* Hiển thị danh sách.
* Tìm theo ID.
* Cập nhật thông tin.
* Xóa sinh viên.
* Lưu lại vào CSV.

Đây là một dự án nhỏ nhưng mô phỏng đầy đủ quy trình CRUD (Create, Read, Update, Delete) trên dữ liệu lưu trữ bằng file CSV.

---

# Tổng kết

Sau buổi học này, bạn đã nắm được:

* Khái niệm và ứng dụng của CSV.
* Đọc dữ liệu bằng `reader()` và `DictReader()`.
* Ghi dữ liệu bằng `writer()` và `DictWriter()`.
* Vai trò của `newline=""`, `delimiter`, `quotechar`, `quoting`.
* Xử lý dữ liệu tiếng Việt với `utf-8` và `utf-8-sig`.
* Chuyển dữ liệu CSV thành đối tượng Python.

# Bài tập thực hành

### Bài 1

Đọc `students.csv` bằng `reader()` và in từng dòng.

### Bài 2

Đọc cùng file bằng `DictReader()`, chỉ in tên và tuổi của từng sinh viên.

### Bài 3

Viết chương trình thêm một sinh viên mới vào `students.csv` mà không làm mất dữ liệu cũ.

### Bài 4

Viết hàm:

```python
def find_student(student_id: int) -> dict | None:
    """Tìm sinh viên theo ID trong file CSV."""
```

### Bài 5

Chuyển toàn bộ dữ liệu trong `students.csv` thành danh sách các đối tượng `Student` sử dụng `@dataclass`.

### Bài 6 (Thử thách)

Xây dựng chương trình **Student Manager** chạy trên dòng lệnh với menu:

```text
===== Student Manager =====
1. Hiển thị danh sách
2. Thêm sinh viên
3. Tìm sinh viên
4. Cập nhật sinh viên
5. Xóa sinh viên
6. Thoát
```

Toàn bộ dữ liệu phải được lưu trong `students.csv` và cập nhật ngay sau mỗi thao tác.

---

## Chuẩn bị cho buổi sau

Ở **Buổi 26**, chúng ta sẽ học **JSON**, bao gồm:

* `json.dump()` và `json.dumps()`.
* `json.load()` và `json.loads()`.
* Chuyển đổi giữa `dict` và JSON.
* Pretty Print (`indent`).
* `ensure_ascii` và xử lý Unicode.
* `JSONEncoder` tùy chỉnh.
* Đọc/ghi file cấu hình (`config.json`) và lưu dữ liệu ứng dụng theo định dạng JSON.
