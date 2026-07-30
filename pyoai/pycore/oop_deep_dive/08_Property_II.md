# Buổi 8: Property nâng cao – Lazy Property, Cached Property, Validation Pattern và Pythonic API

Đây là buổi cuối cùng của phần **Encapsulation** trước khi chúng ta chuyển sang **Inheritance (Kế thừa)**.

Nếu Buổi 7 giúp bạn biết **property là gì**, thì Buổi 8 sẽ giúp bạn biết **khi nào nên dùng property, khi nào không nên dùng**, và cách các framework lớn như Django, SQLAlchemy, PySide6 tận dụng property để xây dựng API đẹp và hiệu quả.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- Lazy Property
- Cached Property
- Validation Pattern
- Read-only Object
- Computed Object
- Property trong `dataclass`
- Thiết kế API Pythonic
- Những lỗi hiệu năng khi dùng property

---

# 1. Property không chỉ để Validation

Đa số lập trình viên mới nghĩ:

```text-x-trilium-auto
Property

↓

Kiểm tra dữ liệu
```

Thực ra property còn dùng để:

- Tính toán giá trị
- Cache kết quả
- Trì hoãn tính toán (Lazy)
- Đọc dữ liệu từ file
- Đọc từ database
- Gọi API
- Đồng bộ dữ liệu

---

# 2. Vấn đề của Computed Property

Ví dụ:

```text-x-trilium-auto
class Rectangle:

    def __init__(self,w,h):
        self.width = w
        self.height = h

    @property
    def area(self):
        print("Calculating...")
        return self.width * self.height
```

Sử dụng:

```text-x-trilium-auto
r = Rectangle(100,200)

print(r.area)
print(r.area)
print(r.area)
```

Kết quả

```text-x-trilium-auto
Calculating...
20000

Calculating...
20000

Calculating...
20000
```

Mỗi lần truy cập đều tính lại.

Nếu phép tính mất vài giây thì sao?

---

# 3. Lazy Property là gì?

Lazy = **chưa dùng thì chưa tính**.

Ví dụ:

```text-x-trilium-auto
class Book:

    @property
    def content(self):
        print("Reading file...")
        return open("book.txt").read()
```

Nếu:

```text-x-trilium-auto
book = Book()
```

Python chưa đọc file.

Chỉ khi:

```text-x-trilium-auto
book.content
```

mới đọc.

Sơ đồ

```text-x-trilium-auto
Create object

↓

Không đọc file

↓

book.content

↓

Đọc file
```

Đây là Lazy Evaluation.

---

# 4. Ví dụ Database

Giả sử:

```text-x-trilium-auto
class User:

    @property
    def orders(self):

        print("Query Database")

        return query_orders()
```

Nếu chương trình không bao giờ gọi

```text-x-trilium-auto
user.orders
```

thì database không bị truy vấn.

---

# 5. Cached Property

Nếu:

```text-x-trilium-auto
@property def area(self):
```

được gọi 1000 lần.

Python tính 1000 lần.

Ta muốn:

```text-x-trilium-auto
Lần đầu

↓

Tính

↓

Lưu

↓

Lần sau

↓

Đọc cache
```

---

# 6. Tự viết Cached Property

Ví dụ:

```text-x-trilium-auto
class Rectangle:

    def __init__(self,w,h):
        self.width = w
        self.height = h

        self._area = None

    @property
    def area(self):

        if self._area is None:

            print("Calculating...")

            self._area = self.width*self.height

        return self._area
```

Kết quả

```text-x-trilium-auto
Calculating...

20000

20000

20000
```

Chỉ tính một lần.

---

# 7. Vấn đề của Cache

Nếu:

```text-x-trilium-auto
r.width = 300
```

thì

```text-x-trilium-auto
r.area
```

vẫn:

```text-x-trilium-auto
20000
```

Sai.

Vì cache chưa cập nhật.

---

# 8. Invalidate Cache

Cách đơn giản:

```text-x-trilium-auto
class Rectangle:

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self,v):
        self._width = v
        self._area = None
```

Mỗi khi width thay đổi:

```text-x-trilium-auto
Area cache

↓

Xóa

↓

Tính lại khi cần
```

Đây là kỹ thuật rất phổ biến.

---

# 9. `functools.cached_property`

Python đã có sẵn.

```text-x-trilium-auto
from functools import cached_property

class Rectangle:

    @cached_property
    def area(self):

        print("Calculating")

        return self.width*self.height
```

Lần đầu:

```text-x-trilium-auto
Calculating
```

Lần sau:

Không tính nữa.

Lưu ý: `cached_property` **không tự xóa cache** khi dữ liệu thay đổi. Nếu object có trạng thái thay đổi, bạn cần tự xóa thuộc tính cache (ví dụ `del obj.area`) hoặc dùng chiến lược invalidate như trên.

---

# 10. Validation Pattern

Ví dụ:

```text-x-trilium-auto
class Employee:

    @property
    def salary(self):
        return self._salary

    @salary.setter
    def salary(self,v):

        if v<0:
            raise ValueError

        self._salary=v
```

Đây gọi là Validation Pattern.

Sơ đồ

```text-x-trilium-auto
Set salary

↓

Validate

↓

OK

↓

Store
```

---

# 11. Property Chain

Ví dụ:

```text-x-trilium-auto
class Temperature:

    def __init__(self,c):
        self._c = c

    @property
    def celsius(self):
        return self._c

    @property
    def fahrenheit(self):
        return self._c*9/5+32
```

Không lưu:

```text-x-trilium-auto
_f
```

Mỗi lần:

```text-x-trilium-auto
temp.fahrenheit
```

Python tự tính.

---

# 12. Property kết hợp Setter

```text-x-trilium-auto
@fahrenheit.setter def fahrenheit(self,v):

    self._c=(v-32)*5/9
```

Bây giờ:

```text-x-trilium-auto
temp.fahrenheit=212
```

thì

```text-x-trilium-auto
print(temp.celsius)
```

Kết quả

```text-x-trilium-auto
100
```

---

# 13. Read Only Object

Ví dụ:

```text-x-trilium-auto
class Config:

    def __init__(self):

        self._version="1.0"

    @property
    def version(self):
        return self._version
```

Không có setter.

Người dùng:

```text-x-trilium-auto
cfg.version="2.0"
```

↓

```text-x-trilium-auto
AttributeError
```

---

# 14. Property trong dataclass

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Book:

    title:str

    price:float

    @property
    def tax(self):
        return self.price*0.1
```

Sử dụng:

```text-x-trilium-auto
b.tax
```

giống hệt class thường.

---

# 15. Pythonic API

Thay vì:

```text-x-trilium-auto
book.get_title()

book.set_title()
```

Python thích:

```text-x-trilium-auto
book.title

book.title="ABC"
```

Nhìn như thuộc tính.

Bên trong vẫn có:

- Validation
- Logging
- Cache
- Database
- API

Người dùng không cần biết.

Đây là sức mạnh của property.

---

# 16. Ví dụ PySide6

Ví dụ:

```text-x-trilium-auto
window.width()
```

đây là method.

Nhưng nếu bạn thiết kế API mới:

```text-x-trilium-auto
window.width
```

có thể đẹp hơn.

Nhiều thư viện Python hiện đại ưu tiên property cho những giá trị mang tính "trạng thái" hơn là hành động.

---

# 17. Ví dụ SQLAlchemy

Trong ORM:

```text-x-trilium-auto
book.author
```

Có vẻ là một thuộc tính bình thường.

Nhưng lần đầu truy cập:

```text-x-trilium-auto
↓

Query Database

↓

Return Author Object
```

Đây là Lazy Loading.

Bản chất cũng dựa trên Descriptor và Property.

---

# 18. Ví dụ dự án Crawler

Giả sử:

```text-x-trilium-auto
class Novel:

    def __init__(self):

        self._chapters=None
```

Property:

```text-x-trilium-auto
@property def chapters(self):

    if self._chapters is None:

        print("Download chapters")

        self._chapters=download()

    return self._chapters
```

Kết quả:

Lần đầu:

```text-x-trilium-auto
Download chapters
```

Lần sau:

Không tải nữa.

---

# 19. Sai lầm phổ biến

## Sai

Property thực hiện công việc rất nặng:

```text-x-trilium-auto
@property def books(self):

    sleep(5)

    return download()
```

Người dùng chỉ nhìn thấy:

```text-x-trilium-auto
user.books
```

Nhưng chương trình bị treo 5 giây.

Nếu property có tác vụ nặng hoặc có tác dụng phụ (side effect) như gọi mạng, ghi file..., hãy cân nhắc dùng method (`load_books()`) để người dùng hiểu rằng thao tác đó không "miễn phí".

---

## Sai

Setter:

```text-x-trilium-auto
self.age=value
```

Lại gọi setter.

Đúng:

```text-x-trilium-auto
self._age=value
```

---

## Sai

Lưu cache nhưng không xóa.

Đây là lỗi phổ biến trong ứng dụng lớn.

---

# 20. Khi nào dùng Property?

| Trường hợp | Có nên dùng? |
| --- | --- |
| Validation | ✅   |
| Giá trị tính toán | ✅   |
| Chỉ đọc | ✅   |
| Cache | ✅   |
| Lazy Load | ✅ (nếu hành vi rõ ràng) |
| Hành động như gửi email, ghi file, xóa dữ liệu | ❌ Dùng method |

Quy tắc thực tế: nếu việc truy cập một "thuộc tính" có thể gây chậm đáng kể, thay đổi trạng thái hệ thống hoặc tạo side effect rõ ràng, hãy cân nhắc dùng method thay vì property để API dễ hiểu hơn.

---

# Tổng kết Buổi 8

```text-x-trilium-auto
@property

        │

        ├──────── Getter

        ├──────── Setter

        ├──────── Deleter

        ├──────── Validation

        ├──────── Lazy Loading

        ├──────── Cache

        └──────── Descriptor
```

Property là một trong những ví dụ đẹp nhất của triết lý Python: **giao diện đơn giản, bên trong có thể rất mạnh mẽ**.

---

# Bài tập thực hành

## Bài 1

Viết lớp `Image`:

- `_pixels = None`

Property:

```text-x-trilium-auto
pixels
```

Yêu cầu:

- Lần đầu truy cập thì in `"Loading image..."` và trả về một danh sách giả lập, ví dụ `[[0, 1], [1, 0]]`.
- Những lần sau không in nữa, chỉ trả về dữ liệu đã lưu.

Đây là bài tập về **Lazy Property**.

---

## Bài 2

Viết lớp `Invoice`:

- `price`
- `quantity`

Property:

```text-x-trilium-auto
total
```

Tính:

```text-x-trilium-auto
price × quantity
```

Sau đó mở rộng để cache kết quả và tự làm mất hiệu lực cache khi `price` hoặc `quantity` thay đổi.

---

## Bài 3

Viết lớp `Temperature`:

Chỉ lưu:

```text-x-trilium-auto
_celsius
```

Viết hai property:

- `celsius`
- `fahrenheit`

Cho phép đọc và ghi ở cả hai đơn vị mà không lưu trùng dữ liệu.

---

## Bài 4 (Áp dụng vào dự án crawler)

Thiết kế lớp `Novel`:

```text-x-trilium-auto
class Novel:
    def __init__(self):
        self._chapters = None
```

Tạo property `chapters` có hành vi:

- Lần đầu truy cập: giả lập tải dữ liệu (in `"Downloading chapters..."`) và lưu danh sách chương.
- Những lần sau: trả về dữ liệu đã tải.
- Viết thêm một method `refresh_chapters()` để xóa cache và buộc tải lại ở lần truy cập tiếp theo.

Đây là mô hình thường gặp trong các ứng dụng crawler, ORM và client API.

---

# Chuẩn bị cho Buổi 9

Từ buổi sau, chúng ta sẽ bước sang **Phần III – Inheritance (Kế thừa)**.

Chúng ta sẽ không chỉ học cú pháp `class Dog(Animal)`, mà sẽ đi sâu vào:

- Python tạo chuỗi kế thừa như thế nào.
- Cơ chế `super()`.
- Override hoạt động ra sao.
- Method Resolution Order (MRO) là gì.
- Tại sao `super()` không đơn giản là "gọi lớp cha".

Đây là nền tảng để hiểu các framework lớn như **PySide6**, **Django**, **SQLAlchemy** và kiến trúc plugin mà bạn đang xây dựng cho hệ thống crawler truyện.