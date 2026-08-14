# Dataclass Deep Dive - Buổi 6

# Ordering Deep Dive (`order=True`)

> Đây là một trong những tính năng được sử dụng rất nhiều trong các hệ thống quản lý dữ liệu.

Sau buổi này bạn sẽ hiểu:

- Python tạo `__lt__`, `__gt__`, `__le__`, `__ge__` như thế nào.
- Dataclass so sánh theo quy tắc nào.
- Khi nào nên dùng `order=True`.
- Khi nào **không nên** dùng.
- Cách kết hợp với `field(compare=False)`.
- Cách sắp xếp dữ liệu trong dự án crawler của bạn.

---

# 1. Vì sao cần Ordering?

Giả sử có danh sách sinh viên:

```text-x-trilium-auto
students = [
    Student(3, "C"),
    Student(1, "A"),
    Student(2, "B"),
]
```

Muốn:

```text-x-trilium-auto
students.sort()
```

Python phải biết:

> Student nào lớn hơn?

> Student nào nhỏ hơn?

Nếu không biết, Python báo lỗi.

---

## Ví dụ

```text-x-trilium-auto
class Student:

    def __init__(self, id):
        self.id = id
```

```text-x-trilium-auto
students = [
    Student(2),
    Student(1)
]

students.sort()
```

Kết quả

```text-x-trilium-auto
TypeError:
'<' not supported between instances of Student and Student
```

---

# 2. order=True

Dataclass giải quyết việc này.

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(order=True)
class Student:

    id: int

    name: str
```

Bây giờ

```text-x-trilium-auto
students = [
    Student(3, "C"),
    Student(1, "A"),
    Student(2, "B")
]

students.sort()

print(students)
```

Kết quả

```text-x-trilium-auto
[
Student(id=1,name='A'),
Student(id=2,name='B'),
Student(id=3,name='C')
]
```

Không cần viết `__lt__()`.

---

# 3. Dataclass sinh những gì?

Nếu

```text-x-trilium-auto
@dataclass(order=True)
```

Python sinh:

```text-x-trilium-auto
__lt__()
__le__()
__gt__()
__ge__()
```

Ngoài:

```text-x-trilium-auto
__eq__()
```

đã có sẵn.

---

# 4. **lt**()

Ví dụ

```text-x-trilium-auto
a = Student(1,"A")

b = Student(2,"B")
```

```text-x-trilium-auto
print(a < b)
```

Kết quả

```text-x-trilium-auto
True
```

Python gọi

```text-x-trilium-auto
a.__lt__(b)
```

Dataclass sinh gần giống:

```text-x-trilium-auto
def __lt__(self, other):

    return (
        self.id,
        self.name
    ) < (
        other.id,
        other.name
    )
```

Điều rất quan trọng là dataclass **so sánh theo tuple của các field**.

---

# 5. So sánh theo thứ tự khai báo

Ví dụ

```text-x-trilium-auto
@dataclass(order=True)
class Student:

    id: int

    name: str

    age: int
```

Python so sánh

```text-x-trilium-auto
(id, name, age)
```

Không phải

```text-x-trilium-auto
(age, id, name)
```

Thứ tự field quyết định toàn bộ thứ tự sắp xếp.

---

# 6. Ví dụ

```text-x-trilium-auto
Student(
    1,
    "An",
    20
)
```

và

```text-x-trilium-auto
Student(
    1,
    "Bình",
    18
)
```

Python so sánh

```text-x-trilium-auto
id

↓

1 == 1

↓

name

↓

"An" < "Bình"

↓

Kết luận
```

Đến khi tìm được field khác nhau thì dừng.

`age` sẽ không được xét nữa trong ví dụ này.

---

# 7. So sánh giống Tuple

Ví dụ

```text-x-trilium-auto
print(

(1,"A",10)

<

(1,"B",5)

)
```

Kết quả

```text-x-trilium-auto
True
```

Dataclass hoạt động y hệt.

---

# 8. compare=False

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass, field

@dataclass(order=True)
class Student:

    id: int

    name: str

    score: int = field(compare=False)
```

Python chỉ so sánh

```text-x-trilium-auto
(id,name)
```

Không xét

```text-x-trilium-auto
score
```

---

Ví dụ

```text-x-trilium-auto
a = Student(
    1,
    "An",
    10
)

b = Student(
    1,
    "An",
    999
)
```

```text-x-trilium-auto
print(a == b)
```

Kết quả

```text-x-trilium-auto
True
```

Score bị bỏ qua.

---

# 9. Thứ tự field rất quan trọng

Ví dụ

```text-x-trilium-auto
@dataclass(order=True)
class Book:

    title:str

    pages:int
```

Python sắp xếp theo

```text-x-trilium-auto
title

↓

pages
```

Nếu bạn muốn sắp xếp theo số trang trước, hãy khai báo:

```text-x-trilium-auto
@dataclass(order=True)
class Book:

    pages:int

    title:str
```

Hoặc tự truyền `key` cho `sorted()`.

---

# 10. Không thể order nếu eq=False

Sai

```text-x-trilium-auto
@dataclass(
    eq=False,
    order=True
)
```

Python báo

```text-x-trilium-auto
ValueError

eq must be true
if order is true
```

Vì:

Nếu không biết khi nào hai object bằng nhau,

Python cũng không thể xác định chính xác `<`, `<=`, `>=`, `>`.

---

# 11. sorted()

Ví dụ

```text-x-trilium-auto
students = [

Student(3,"C"),

Student(1,"A"),

Student(2,"B")

]
```

```text-x-trilium-auto
print(

sorted(students)

)
```

Không cần

```text-x-trilium-auto
key=
```

---

# 12. max()

```text-x-trilium-auto
print(

max(students)

)
```

Python dùng

```text-x-trilium-auto
__gt__()
```

---

# 13. min()

```text-x-trilium-auto
print(

min(students)

)
```

Python dùng

```text-x-trilium-auto
__lt__()
```

---

# 14. Ví dụ Crawler

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(order=True)
class Chapter:

    index:int

    title:str
```

```text-x-trilium-auto
chapters = [

Chapter(5,"5"),

Chapter(1,"1"),

Chapter(3,"3")

]
```

```text-x-trilium-auto
chapters.sort()
```

Kết quả

```text-x-trilium-auto
1

3

5
```

Rất phù hợp khi parser trả về các chương chưa đúng thứ tự.

---

# 15. Khi nào không nên dùng order=True?

Ví dụ

```text-x-trilium-auto
Product
```

Có nhiều cách sắp xếp:

- theo giá
- theo tên
- theo rating
- theo ngày

Nếu dùng

```text-x-trilium-auto
order=True
```

thì chỉ có **một** quy tắc duy nhất.

Trong trường hợp này nên dùng

```text-x-trilium-auto
sorted(
    products,
    key=lambda x:x.price
)
```

---

# 16. key= linh hoạt hơn

Ví dụ

```text-x-trilium-auto
students = [
    Student(1,"Tom"),
    Student(2,"Alice"),
    Student(3,"Bob")
]
```

Sắp theo tên

```text-x-trilium-auto
sorted(

students,

key=lambda s:s.name

)
```

Không cần

```text-x-trilium-auto
order=True
```

---

# 17. Nhiều tiêu chí

Ví dụ

```text-x-trilium-auto
sorted(

students,

key=lambda s:(

s.age,

s.name

)

)
```

Rất linh hoạt.

---

# 18. reverse

```text-x-trilium-auto
students.sort(

reverse=True

)
```

Đảo ngược.

---

# 19. So sánh object khác class

```text-x-trilium-auto
@dataclass(order=True)
class A:

    x:int
```

```text-x-trilium-auto
@dataclass(order=True)
class B:

    x:int
```

```text-x-trilium-auto
A(1)<B(1)
```

Kết quả

```text-x-trilium-auto
TypeError
```

Dataclass chỉ hỗ trợ so sánh có thứ tự giữa **các đối tượng cùng lớp**.

---

# 20. Ví dụ thực tế

Crawler

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(order=True)
class DownloadTask:

    priority:int

    novel:str
```

Queue

```text-x-trilium-auto
tasks=[

DownloadTask(5,"A"),

DownloadTask(1,"B"),

DownloadTask(3,"C")

]
```

```text-x-trilium-auto
tasks.sort()
```

Kết quả

```text-x-trilium-auto
priority

1

3

5
```

Đây là cách đơn giản để xử lý hàng đợi theo mức ưu tiên.

---

# 21. order=True và heapq

`heapq` là hàng đợi ưu tiên (priority queue) của Python.

```text-x-trilium-auto
import heapq from dataclasses import dataclass

@dataclass(order=True)
class Task:
    priority: int
    name: str

tasks = [
    Task(3, "Download"),
    Task(1, "Parse"),
    Task(2, "Save"),
]

heapq.heapify(tasks)

while tasks:
    print(heapq.heappop(tasks))
```

Kết quả:

```text-x-trilium-auto
Task(priority=1, name='Parse')
Task(priority=2, name='Save')
Task(priority=3, name='Download')
```

Không cần viết thêm bất kỳ phương thức so sánh nào.

---

# 22. Tùy biến thứ tự mà không đổi cấu trúc dữ liệu

Đôi khi bạn không muốn thay đổi thứ tự khai báo field chỉ để phục vụ việc sắp xếp.

Ví dụ:

```text-x-trilium-auto
@dataclass class Chapter:
    title: str
    index: int
```

Thay vì chuyển `index` lên đầu, hãy dùng:

```text-x-trilium-auto
sorted(
    chapters,
    key=lambda c: c.index
)
```

Đây là cách thường được dùng trong các dự án lớn vì tách biệt **mô hình dữ liệu** và **quy tắc sắp xếp**.

---

# Tổng kết

| Tính năng | Ý nghĩa |
| --- | --- |
| `order=True` | Sinh các phép so sánh `<`, `<=`, `>`, `>=` |
| Quy tắc so sánh | Theo **thứ tự khai báo field** |
| `compare=False` | Bỏ qua field khi so sánh và sắp xếp |
| Điều kiện | `eq=True` (mặc định) |
| Ứng dụng | `sort()`, `sorted()`, `min()`, `max()`, `heapq` |

---

# Best Practice

### Nên dùng `order=True` khi:

- Có **một quy tắc sắp xếp tự nhiên**.
- `Point(x, y)` (theo tọa độ).
- `Version(major, minor, patch)`.
- `Chapter(index, title)`.
- `PriorityTask(priority, name)`.

---

### Không nên dùng khi:

- Có nhiều tiêu chí sắp xếp khác nhau.
- Quy tắc thay đổi theo từng ngữ cảnh.
- Muốn sắp theo giá hôm nay, tên ngày mai, ngày tạo hôm khác.

Lúc đó nên dùng:

```text-x-trilium-auto
sorted(items, key=...)
```

---

# Bài tập thực hành

## Bài 1

Tạo dataclass:

```text-x-trilium-auto
@dataclass(order=True)
class Version:
    major: int
    minor: int
    patch: int
```

So sánh:

```text-x-trilium-auto
Version(1, 2, 0) < Version(1, 3, 0)
Version(2, 0, 0) > Version(1, 9, 9)
```

Giải thích kết quả.

---

## Bài 2

Tạo dataclass:

```text-x-trilium-auto
@dataclass(order=True)
class Student:
    id: int
    name: str
    score: float = field(compare=False)
```

Tạo ba sinh viên có cùng `id` và `name` nhưng điểm khác nhau. Kiểm tra:

- `==`
- `<`
- `sorted()`

Quan sát vai trò của `compare=False`.

---

## Bài 3 (Áp dụng dự án crawler)

Thiết kế:

```text-x-trilium-auto
@dataclass(order=True)
class CrawlTask:
    priority: int
    novel_name: str
    chapter_index: int
    retry_count: int = field(compare=False, default=0)
```

- Tạo 10 `CrawlTask` với mức ưu tiên khác nhau.
- Dùng `list.sort()`.
- Dùng `heapq` để mô phỏng hàng đợi ưu tiên.
- Thử thay đổi `retry_count` và xác nhận rằng thứ tự ưu tiên không thay đổi.

---

# Chuẩn bị cho Buổi 7

Buổi tiếp theo là `**slots=True**` **Deep Dive**.

Đây là một trong những tính năng giúp tối ưu **bộ nhớ** và **tốc độ truy cập thuộc tính**, đặc biệt hữu ích khi làm việc với hàng trăm nghìn hoặc hàng triệu đối tượng như:

- `Chapter`
- `Novel`
- `Author`
- `CrawlerJob`
- `DownloadTask`

Chúng ta sẽ tìm hiểu:

- `__dict__` là gì.
- `__slots__` hoạt động ra sao.
- Vì sao `slots=True` giúp tiết kiệm bộ nhớ.
- Benchmark về tốc độ và bộ nhớ.
- Những hạn chế khi dùng `slots=True`.
- Khi nào nên và không nên sử dụng trong các dự án Python thực tế.