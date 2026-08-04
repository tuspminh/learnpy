# Python OOP Master – Buổi 19

# Container Magic Methods – Xây dựng class hoạt động như list và dict

> Đây là một trong những nhóm Magic Methods quan trọng nhất trong Python.
>
> Sau buổi học này, bạn sẽ hiểu vì sao có thể viết:
>
> ```python
> len(repo)
> chapter[0]
> chapter[-1]
> for book in library:
> if book in library:
> ```
>
> mặc dù `repo`, `library` hay `chapter` đều là class do bạn tự xây dựng.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu Container Protocol của Python.
* Cài đặt `__len__()`.
* Cài đặt `__getitem__()`.
* Cài đặt `__setitem__()`.
* Cài đặt `__delitem__()`.
* Cài đặt `__contains__()`.
* Cài đặt `__iter__()`.
* Hiểu mối quan hệ giữa Iterator và Container.
* Xây dựng Collection chuyên nghiệp cho framework cào truyện.

---

# 1. Container là gì?

Container là object dùng để chứa nhiều phần tử.

Ví dụ:

```python
list
tuple
dict
set
str
```

Chúng đều hỗ trợ:

```python
len(obj)

obj[0]

for x in obj

x in obj
```

Lý do?

↓

Vì chúng cài đặt **Container Protocol**.

---

# 2. Container Protocol

Những magic method phổ biến:

| Method         | Ý nghĩa              |
| -------------- | -------------------- |
| `__len__`      | `len(obj)`           |
| `__getitem__`  | `obj[index]`         |
| `__setitem__`  | `obj[index] = value` |
| `__delitem__`  | `del obj[index]`     |
| `__contains__` | `x in obj`           |
| `__iter__`     | `for x in obj`       |

---

# 3. `__len__()`

Ví dụ

```python
class Library:
    def __init__(self):
        self.books = []

    def __len__(self):
        return len(self.books)
```

Sử dụng

```python
library = Library()

print(len(library))
```

Python gọi

```python
library.__len__()
```

---

# 4. Ví dụ đầy đủ

```python
class Library:
    def __init__(self):
        self.books = []

    def add(self, book):
        self.books.append(book)

    def __len__(self):
        return len(self.books)
```

```python
library = Library()

library.add("Python")

library.add("Java")

print(len(library))
```

↓

```text
2
```

---

# 5. `__getitem__()`

Cho phép

```python
obj[index]
```

Ví dụ

```python
class Library:
    def __init__(self):
        self.books = []

    def __getitem__(self, index):
        return self.books[index]
```

Sử dụng

```python
library = Library()

library.books.extend(["Python", "Rust", "Go"])

print(library[1])
```

↓

```text
Rust
```

---

# 6. Hỗ trợ Slice

Điều thú vị là

```python
library[1:3]
```

cũng gọi

```python
__getitem__()
```

Nhưng tham số

```python
index
```

là

```python
slice(1, 3, None)
```

Ví dụ

```python
def __getitem__(self, index):
    print(index)
    return self.books[index]
```

Kết quả

```text
slice(1,3,None)
```

Không cần xử lý riêng nếu dùng list bên trong.

---

# 7. `__setitem__()`

Cho phép

```python
library[0] = "C++"
```

Ví dụ

```python
class Library:
    def __init__(self):
        self.books = []

    def __setitem__(self, index, value):
        self.books[index] = value
```

---

# 8. `__delitem__()`

Ví dụ

```python
class Library:
    def __init__(self):
        self.books = []

    def __delitem__(self, index):
        del self.books[index]
```

Sử dụng

```python
del library[1]
```

---

# 9. `__contains__()`

Cho phép

```python
if "Python" in library:
```

Ví dụ

```python
class Library:
    def __init__(self):
        self.books = []

    def __contains__(self, item):
        return item in self.books
```

↓

```python
print("Python" in library)
```

---

# 10. `__iter__()`

Đây là method quan trọng nhất.

Ví dụ

```python
class Library:
    def __init__(self):
        self.books = []

    def __iter__(self):
        return iter(self.books)
```

Sử dụng

```python
for book in library:
    print(book)
```

Python gọi

```python
library.__iter__()
```

---

# 11. `iter()`

```python
iterator = iter(library)
```

↓

```python
library.__iter__()
```

---

# 12. `next()`

Iterator trả về từ `__iter__()` phải hỗ trợ

```python
next(iterator)
```

Ví dụ

```python
library = Library()

library.books.extend(["A", "B", "C"])

it = iter(library)

print(next(it))
print(next(it))
print(next(it))
```

↓

```text
A
B
C
```

---

# 13. Tự viết Iterator

Không bắt buộc dùng list.

Ví dụ

```python
class Counter:
    def __init__(self):

        self.value = 0

    def __iter__(self):

        return self

    def __next__(self):

        self.value += 1

        if self.value > 5:
            raise StopIteration

        return self.value
```

Sử dụng

```python
for x in Counter():
    print(x)
```

↓

```text
1
2
3
4
5
```

---

# 14. Ví dụ Repository

```python
class BookRepository:
    def __init__(self):

        self.books = []

    def add(self, book):
        self.books.append(book)

    def __len__(self):
        return len(self.books)

    def __iter__(self):
        return iter(self.books)

    def __getitem__(self, index):
        return self.books[index]
```

Có thể

```python
repo = BookRepository()

repo.add("Python")

repo.add("Rust")

print(len(repo))

print(repo[0])

for book in repo:
    print(book)
```

---

# 15. Ví dụ trong framework cào truyện

```python
class ChapterCollection:
    def __init__(self):

        self.chapters = []

    def add(self, chapter):

        self.chapters.append(chapter)

    def __len__(self):

        return len(self.chapters)

    def __getitem__(self, index):

        return self.chapters[index]

    def __iter__(self):

        return iter(self.chapters)
```

Sử dụng

```python
collection = ChapterCollection()

collection.add("Chapter 1")

collection.add("Chapter 2")

print(collection[0])

for chapter in collection:
    print(chapter)
```

---

# 16. Hỗ trợ `reversed()`

Nếu class có

```python
__len__()

__getitem__()
```

Python thường có thể dùng:

```python
reversed(obj)
```

Ví dụ

```python
for book in reversed(library):
    print(book)
```

Hoặc bạn có thể tự cài đặt `__reversed__()` để tối ưu.

---

# 17. `__contains__()` và hiệu năng

Nếu không cài `__contains__()`:

```python
item in obj
```

Python sẽ:

* gọi `__iter__()`
* duyệt từng phần tử

Nếu dữ liệu lớn và có cấu trúc phù hợp (ví dụ dùng `set` hoặc `dict` nội bộ), hãy cài `__contains__()` để kiểm tra nhanh hơn.

---

# 18. Ví dụ hoàn chỉnh

```python
class Library:
    def __init__(self):

        self.books = []

    def add(self, book):

        self.books.append(book)

    def __len__(self):

        return len(self.books)

    def __getitem__(self, index):

        return self.books[index]

    def __contains__(self, item):

        return item in self.books

    def __iter__(self):

        return iter(self.books)


library = Library()

library.add("Python")

library.add("Go")

library.add("Rust")

print(len(library))

print(library[0])

print("Go" in library)

for book in library:
    print(book)
```

---

# 19. Best Practices

✅ `__iter__()` nên trả về một **iterator**, thường dùng:

```python
return iter(self._items)
```

---

✅ `__getitem__()` nên hỗ trợ cả:

* index
* slice

nếu class biểu diễn một chuỗi phần tử.

---

✅ `__len__()` phải trả về số nguyên không âm (`int >= 0`).

---

✅ Ưu tiên lưu dữ liệu trong thuộc tính "riêng":

```python
self._items
```

thay vì:

```python
self.items
```

để tránh bị sửa trực tiếp từ bên ngoài.

---

# Những lỗi người mới thường gặp

## Lỗi 1

`__len__()` trả về sai kiểu

Sai:

```python
def __len__(self):
    return "10"
```

Đúng:

```python
def __len__(self):
    return 10
```

---

## Lỗi 2

`__iter__()` trả về list

Sai:

```python
def __iter__(self):
    return self.books
```

`list` là iterable nhưng **không phải iterator**.

Đúng:

```python
def __iter__(self):
    return iter(self.books)
```

---

## Lỗi 3

Tự viết `__getitem__()` nhưng quên xử lý `slice`

Ví dụ:

```python
repo[1:5]
```

nếu không chuyển tiếp cho danh sách nội bộ có thể gây lỗi hoặc mất tính năng.

---

## Lỗi 4

Lạm dụng `__contains__()`

Nếu chỉ gọi:

```python
return item in self._items
```

thì không khác nhiều so với để Python duyệt qua `__iter__()`. Chỉ cài đặt riêng khi có thể cải thiện hiệu năng hoặc thay đổi ý nghĩa kiểm tra.

---

# Bài tập

## Bài 1

Viết class `Playlist`:

* `add(song)`
* `__len__()`
* `__getitem__()`

Cho phép:

```python
len(playlist)

playlist[0]
```

---

## Bài 2

Viết class `StudentCollection`:

* `add(student)`
* `__iter__()`

Cho phép:

```python
for student in collection:
    ...
```

---

## Bài 3

Viết class `Dictionary` (không dùng `dict` trực tiếp trong giao diện):

Hỗ trợ:

```python
dictionary["python"] = "Một ngôn ngữ"

print(dictionary["python"])

del dictionary["python"]
```

Bằng cách cài:

* `__getitem__()`
* `__setitem__()`
* `__delitem__()`

---

## Bài 4

Trong dự án cào truyện, viết `ChapterCollection`:

Yêu cầu:

* `add(chapter)`
* `remove(chapter)`
* `len(collection)`
* `collection[5]`
* `collection[2:8]`
* `for chapter in collection`
* `chapter in collection`

---

## Bài 5 (Nâng cao)

Thiết kế `CrawlerTaskQueue`:

Yêu cầu:

* Lưu danh sách `CrawlerTask`.
* Hỗ trợ:

```python
len(queue)

queue[0]

queue[-1]

queue[2:5]

task in queue

for task in queue

reversed(queue)
```

Không để mã bên ngoài truy cập trực tiếp danh sách nội bộ.

---

# Tổng kết buổi học

* **Container Magic Methods** giúp class của bạn hoạt động giống các kiểu dữ liệu chuẩn như `list`, `tuple` hay `dict`.
* `__len__()`, `__getitem__()`, `__setitem__()`, `__delitem__()`, `__contains__()` và `__iter__()` là nền tảng của **Container Protocol** trong Python.
* `__getitem__()` không chỉ xử lý chỉ số mà còn có thể nhận đối tượng `slice`, giúp hỗ trợ cú pháp cắt lát (`obj[1:5]`) một cách tự nhiên.
* `__iter__()` nên trả về một **iterator**, thường thông qua `iter(self._items)`, thay vì trả về danh sách trực tiếp.
* Các collection như `Repository`, `ChapterCollection` hay `CrawlerTaskQueue` trong framework cào truyện sẽ trở nên Pythonic hơn rất nhiều khi triển khai đúng các magic methods này.

> **Buổi 20** chúng ta sẽ học **Callable Object** với `__call__()`. Bạn sẽ biết cách biến một object thành một "hàm", hiểu cơ chế hoạt động của decorator class, middleware, validator và nhiều framework Python hiện đại như Flask, Django hay PyTorch sử dụng `__call__()` để xây dựng API linh hoạt.
