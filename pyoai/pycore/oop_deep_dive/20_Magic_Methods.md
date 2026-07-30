# OOP Deep Dive – Buổi 20

# Magic Methods Deep Dive I – Xây dựng các Class "Pythonic"

> **Đây là buổi học sẽ thay đổi cách bạn thiết kế class trong Python.**

Một class Python chuyên nghiệp không chỉ có:

```text-x-trilium-auto
class User:
    ...
```

Mà còn hoạt động tự nhiên như:

- `list`
- `dict`
- `str`
- `pathlib.Path`
- `datetime`
- `requests.Response`

Làm sao?

Nhờ **Magic Methods** (Special Methods).

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- Magic Methods là gì
- Data Model của Python
- `__repr__()`
- `__str__()`
- `__bytes__()`
- `__format__()`
- `__bool__()`
- `__len__()`
- `__contains__()`
- `__iter__()`
- `__next__()`

---

# 1. Magic Method là gì?

Magic Method là các method có dạng:

```text-x-trilium-auto
__xxx__()
```

Ví dụ

```text-x-trilium-auto
__init__()

__repr__()

__len__()

__iter__()

__getitem__()

__call__()

__enter__()

__exit__()
```

Python sẽ tự động gọi chúng khi bạn sử dụng các cú pháp quen thuộc.

Ví dụ:

```text-x-trilium-auto
len(obj)
```

↓

Python thực chất gọi

```text-x-trilium-auto
obj.__len__()
```

---

# 2. Python Data Model

Đây là khái niệm cực kỳ quan trọng.

Python không hỏi:

> Object này có phải list không?

Python hỏi:

> Object này có hỗ trợ `__iter__()` không?

Ví dụ

```text-x-trilium-auto
for item in obj:
```

↓

Python tìm

```text-x-trilium-auto
obj.__iter__()
```

Đây gọi là:

> Python Data Model

---

# 3. `__repr__()`

Đây là method quan trọng nhất.

Ví dụ

```text-x-trilium-auto
class User:
    pass

u = User()

print(u)
```

Kết quả

```text-x-trilium-auto
<__main__.User object at 0x7f...>
```

Không hữu ích.

---

# 4. Override `__repr__()`

```text-x-trilium-auto
class User:

    def __init__(self,name):

        self.name=name

    def __repr__(self):

        return f"User(name={self.name!r})"
```

---

```text-x-trilium-auto
print(User("Alice"))
```

↓

```text-x-trilium-auto
User(name='Alice')
```

---

# 5. Tại sao dùng `!r`?

Ví dụ

```text-x-trilium-auto
name="Python"
```

```text-x-trilium-auto
repr(name)
```

↓

```text-x-trilium-auto
'Python'
```

Có dấu `'`.

Trong khi

```text-x-trilium-auto
str(name)
```

↓

```text-x-trilium-auto
Python
```

---

`repr()` hướng đến:

> Lập trình viên.

---

# 6. `__str__()`

Ví dụ

```text-x-trilium-auto
class User:

    def __str__(self):

        return "Người dùng"
```

---

```text-x-trilium-auto
print(user)
```

↓

```text-x-trilium-auto
Người dùng
```

---

`str()` hướng đến:

> Người sử dụng.

---

# 7. Khác nhau

```text-x-trilium-auto
repr()

↓

Developer
```

---

```text-x-trilium-auto
str()

↓

End User
```

---

Ví dụ

```text-x-trilium-auto
class Book:

    def __repr__(self):

        return "Book(title='Python')"

    def __str__(self):

        return "Python Book"
```

---

```text-x-trilium-auto
print(book)
```

↓

```text-x-trilium-auto
Python Book
```

---

```text-x-trilium-auto
repr(book)
```

↓

```text-x-trilium-auto
Book(title='Python')
```

---

# 8. Nếu không có `__str__()`

Python sẽ dùng

```text-x-trilium-auto
__repr__()
```

Đó là lý do nhiều thư viện chỉ cài `__repr__()`.

---

# 9. `__bytes__()`

Ví dụ

```text-x-trilium-auto
class Message:

    def __bytes__(self):

        return b"Hello"
```

---

```text-x-trilium-auto
bytes(msg)
```

↓

```text-x-trilium-auto
b'Hello'
```

---

Ứng dụng:

- Network
- Binary Protocol
- Socket

---

# 10. `__format__()`

Ví dụ

```text-x-trilium-auto
class Money:

    def __init__(self,value):

        self.value=value

    def __format__(self,spec):

        if spec=="usd":

            return f"${self.value:.2f}"

        if spec=="vnd":

            return f"{self.value:,.0f} VNĐ"

        return str(self.value)
```

---

```text-x-trilium-auto
print(f"{Money(100):usd}")
```

↓

```text-x-trilium-auto
$100.00
```

---

```text-x-trilium-auto
print(f"{Money(1000000):vnd}")
```

↓

```text-x-trilium-auto
1,000,000 VNĐ
```

---

# 11. `__bool__()`

Ví dụ

```text-x-trilium-auto
class User:

    def __bool__(self):

        return False
```

---

```text-x-trilium-auto
if user:
```

↓

Python gọi

```text-x-trilium-auto
user.__bool__()
```

---

# 12. Ví dụ thực tế

```text-x-trilium-auto
class Response:

    def __init__(self,status):

        self.status=status

    def __bool__(self):

        return self.status==200
```

---

```text-x-trilium-auto
if response:

    print("Success")
```

Rất Pythonic.

---

# 13. Nếu không có `__bool__()`

Python sẽ dùng

```text-x-trilium-auto
__len__()
```

Nếu:

```text-x-trilium-auto
len(obj)==0
```

↓

False.

---

# 14. `__len__()`

Ví dụ

```text-x-trilium-auto
class Playlist:

    def __init__(self):

        self.songs=[]

    def __len__(self):

        return len(self.songs)
```

---

```text-x-trilium-auto
len(playlist)
```

↓

```text-x-trilium-auto
playlist.__len__()
```

---

# 15. `__contains__()`

Ví dụ

```text-x-trilium-auto
class Playlist:

    def __contains__(self,item):

        return item in self.songs
```

---

```text-x-trilium-auto
if "Song A" in playlist:
```

↓

Python gọi

```text-x-trilium-auto
playlist.__contains__("Song A")
```

---

# 16. `__iter__()`

Ví dụ

```text-x-trilium-auto
class Playlist:

    def __iter__(self):

        return iter(self.songs)
```

---

```text-x-trilium-auto
for song in playlist:
```

↓

Hoạt động.

---

# 17. Iterator

Một Iterator cần:

```text-x-trilium-auto
__iter__()

__next__()
```

Ví dụ

```text-x-trilium-auto
class Counter:

    def __init__(self):

        self.i=0

    def __iter__(self):

        return self

    def __next__(self):

        self.i+=1

        if self.i>5:

            raise StopIteration

        return self.i
```

---

```text-x-trilium-auto
for i in Counter():

    print(i)
```

↓

```text-x-trilium-auto
1
2
3
4
5
```

---

# 18. Iterable vs Iterator

Đây là điểm rất nhiều người nhầm.

## Iterable

Có

```text-x-trilium-auto
__iter__()
```

Ví dụ

```text-x-trilium-auto
list

tuple

dict
```

---

## Iterator

Có

```text-x-trilium-auto
__iter__()

__next__()
```

Ví dụ

```text-x-trilium-auto
iter(list)
```

---

# 19. `iter()`

```text-x-trilium-auto
numbers=[1,2,3]
```

```text-x-trilium-auto
it=iter(numbers)
```

↓

```text-x-trilium-auto
next(it)
```

↓

```text-x-trilium-auto
1
```

---

# 20. `StopIteration`

Iterator phải kết thúc bằng

```text-x-trilium-auto
raise StopIteration
```

Nếu không

↓

Vòng lặp

```text-x-trilium-auto
for
```

không bao giờ dừng.

---

# 21. Áp dụng vào hệ thống crawler

Ví dụ

```text-x-trilium-auto
class NovelCollection:

    def __iter__(self):

        return iter(self.novels)
```

Bây giờ

```text-x-trilium-auto
for novel in collection:
```

↓

Hoạt động tự nhiên.

---

# 22. Dashboard

```text-x-trilium-auto
class CrawlQueue:

    def __len__(self):

        return len(self.jobs)

    def __contains__(self,job):

        return job in self.jobs
```

---

Có thể viết

```text-x-trilium-auto
len(queue)

job in queue
```

Thay vì

```text-x-trilium-auto
queue.count()

queue.has()
```

Đây là phong cách Pythonic.

---

# 23. Sơ đồ

```text-x-trilium-auto
len(obj)

↓

__len__()
```

---

```text-x-trilium-auto
for

↓

__iter__()

↓

__next__()
```

---

```text-x-trilium-auto
in

↓

__contains__()
```

---

```text-x-trilium-auto
print()

↓

__str__()
```

---

```text-x-trilium-auto
repr()

↓

__repr__()
```

---

# 24. Bảng tổng hợp

| Magic Method | Được gọi khi |
| --- | --- |
| `__repr__` | `repr(obj)` |
| `__str__` | `str(obj)`, `print(obj)` |
| `__bytes__` | `bytes(obj)` |
| `__format__` | `format(obj)`, f-string |
| `__bool__` | `if obj` |
| `__len__` | `len(obj)` |
| `__contains__` | `x in obj` |
| `__iter__` | `iter(obj)`, `for` |
| `__next__` | `next(iterator)` |

---

# 25. Nguyên tắc thiết kế

Khi thiết kế một class, hãy tự hỏi:

- Có cần in đẹp không? → `__str__()`, `__repr__()`
- Có phải một collection không? → `__len__()`, `__iter__()`, `__contains__()`
- Có cần đánh giá đúng/sai không? → `__bool__()`
- Có cần hỗ trợ f-string không? → `__format__()`

Thay vì tạo các method như:

```text-x-trilium-auto
book.to_string()
queue.count_jobs()
collection.has_item()
```

hãy tận dụng Data Model của Python.

---

# Tổng kết Buổi 20

```text-x-trilium-auto
               Python Data Model

                      │

     ┌────────────────┼────────────────┐

     ▼                ▼                ▼

 Printing       Collection        Boolean

 repr()         len()             if obj

 str()          in                bool()

                for

                next()
```

---

# Điều quan trọng nhất cần nhớ

Magic Methods giúp object của bạn **hòa nhập với ngôn ngữ Python**.

Một class tốt không bắt người dùng học API riêng, mà tận dụng các cú pháp quen thuộc:

- `len(obj)`
- `obj in collection`
- `for x in obj`
- `print(obj)`
- `if obj`

Đó là lý do các thư viện chuẩn của Python và các framework lớn đều triển khai rất nhiều magic method.

---

# Bài tập thực hành

## Bài 1

Viết lớp `Library`:

- Chứa danh sách sách.
- Hỗ trợ:

```text-x-trilium-auto
len(library)
```

```text-x-trilium-auto
for book in library
```

```text-x-trilium-auto
"Python" in library
```

---

## Bài 2

Viết lớp `Money`:

- Cài `__repr__()`.
- Cài `__str__()`.
- Cài `__format__()`.

Hỗ trợ:

```text-x-trilium-auto
f"{money:usd}"
```

```text-x-trilium-auto
f"{money:vnd}"
```

---

## Bài 3

Viết một `Countdown` Iterator:

```text-x-trilium-auto
for i in Countdown(5):
    print(i)
```

Kết quả:

```text-x-trilium-auto
5
4
3
2
1
```

---

## Bài 4 (Áp dụng dự án crawler)

Thiết kế:

```text-x-trilium-auto
class CrawlQueue:
    ...
```

Hỗ trợ:

- `len(queue)`
- `job in queue`
- `for job in queue`
- `bool(queue)` (hết job thì `False`)
- `print(queue)` hiển thị trạng thái hàng đợi.
- `repr(queue)` hiển thị thông tin phục vụ debug.

---

# Chuẩn bị cho Buổi 21

Buổi tiếp theo sẽ tiếp tục với **Magic Methods nâng cao**, tập trung vào việc biến class của bạn thành một **container** thực thụ:

- `__getitem__()`
- `__setitem__()`
- `__delitem__()`
- `__missing__()`
- `__reversed__()`
- `__index__()`
- `__hash__()`
- `__eq__()`

Sau buổi đó, bạn sẽ có thể tự xây dựng các kiểu dữ liệu tùy chỉnh hoạt động gần như `list`, `dict` hoặc `set` của Python. Đây là bước quan trọng để thiết kế các API mạnh mẽ và tự nhiên.