# Iterator Deep Dive — Buổi 7

# Tự xây dựng Iterator đầu tiên đúng chuẩn Python

Đây là buổi học đánh dấu sự chuyển đổi từ **người sử dụng Iterator** sang **người thiết kế Iterator**.

Ở 6 buổi trước, chúng ta đã học:

  * Iterator là gì 
  * Iterable là gì 
  * Iterator Protocol 
  * `for`
  * `iter()`
  * `next()`



Hôm nay chúng ta sẽ trả lời câu hỏi:

> **Làm thế nào để tự thiết kế một Iterable giống như`list`, `dict`, `pathlib.Path`, hay `os.scandir()`?**

Đây là kiến thức được dùng rất nhiều khi xây dựng framework hoặc thư viện Python.

* * *

# Roadmap

Đã học

  * ✅ Buổi 1 - Iterator 
  * ✅ Buổi 2 - Iterable 
  * ✅ Buổi 3 - Iterator Protocol 
  * ✅ Buổi 4 - for Loop 
  * ✅ Buổi 5 - iter() 
  * ✅ Buổi 6 - next() 



Hôm nay

  * ✅ Buổi 7 - Thiết kế Iterator đúng chuẩn 



Tiếp theo

  * Buổi 8 - Iterator cho File 
  * Buổi 9 - Iterator cho Linked List 



* * *

# Sai lầm của người mới

Sau khi học Iterator, nhiều người viết:
    
    
    class Numbers:
    
        def __init__(self):
            self.current = 1
    
        def __iter__(self):
            return self
    
        def __next__(self):
            if self.current > 5:
                raise StopIteration
    
            value = self.current
            self.current += 1
            return value

Thoạt nhìn có vẻ đúng.

* * *

## Nhưng thử chạy
    
    
    numbers = Numbers()
    
    for x in numbers:
        print(x)
    
    print("Lần hai")
    
    for x in numbers:
        print(x)

Kết quả
    
    
    1
    2
    3
    4
    5
    
    Lần hai

Không in gì.

* * *

# Vì sao?

Sau vòng lặp đầu tiên
    
    
    current = 6

Object đã bị "tiêu thụ".

* * *

Đây **không phải** cách mà `list` hoạt động.

Ví dụ
    
    
    numbers = [1, 2, 3]
    
    for x in numbers:
        print(x)
    
    for x in numbers:
        print(x)

↓
    
    
    1
    2
    3
    
    1
    2
    3

List có thể lặp vô số lần.

* * *

# Nguyên nhân

Ở ví dụ đầu tiên
    
    
    __iter__()

trả về
    
    
    self

Nghĩa là
    
    
    Numbers
    
    ↓
    
    Iterator

chỉ có **một object**.

* * *

Trong khi `list`
    
    
    List
    
    ↓
    
    Iterator A
    
    ↓
    
    Iterator B
    
    ↓
    
    Iterator C

Mỗi lần gọi `iter(list)` sẽ tạo **Iterator mới**.

* * *

# Thiết kế đúng chuẩn

Python tách thành **hai class**.
    
    
    BookCollection
    
    ↓
    
    BookIterator

Đây chính là cách hoạt động của:

  * list 
  * tuple 
  * dict 
  * set 
  * pathlib 
  * os.walk 
  * Django QuerySet 
  * SQLAlchemy Result 
  * pandas DataFrame 



* * *

# Ví dụ đầu tiên

## Iterator
    
    
    class NumberIterator:
    
        def __init__(self, data):
            self.data = data
            self.index = 0
    
        def __iter__(self):
            return self
    
        def __next__(self):
    
            if self.index >= len(self.data):
                raise StopIteration
    
            value = self.data[self.index]
            self.index += 1
    
            return value

* * *

## Iterable
    
    
    class NumberCollection:
    
        def __init__(self, data):
            self.data = data
    
        def __iter__(self):
            return NumberIterator(self.data)

Đây là thiết kế **chuẩn Python**.

* * *

# Thử nghiệm
    
    
    numbers = NumberCollection([10, 20, 30])
    
    for x in numbers:
        print(x)
    
    print("-----")
    
    for x in numbers:
        print(x)

↓
    
    
    10
    20
    30
    -----
    10
    20
    30

Hoạt động giống hệt `list`.

* * *

# Phân tích

Object
    
    
    NumberCollection

không nhớ
    
    
    index

Nó chỉ lưu
    
    
    data

* * *

Iterator mới nhớ
    
    
    index
    
    
    Collection
    
    ↓
    
    [10,20,30]
    
    ↓
    
    Iterator
    
    ↓
    
    index = 0

* * *

# Hai Iterator độc lập
    
    
    numbers = NumberCollection([1, 2, 3])
    
    it1 = iter(numbers)
    it2 = iter(numbers)
    
    print(next(it1))
    print(next(it1))
    
    print(next(it2))

↓
    
    
    1
    2
    1

Vì
    
    
    it1.index = 2
    
    it2.index = 1

Hoàn toàn độc lập.

* * *

# Minh họa
    
    
    Collection
    
    ↓
    
    +-----------+
    |1|2|3|
    +-----------+
    
    ↑         ↑
    
    it1      it2

Sau hai lần
    
    
    next(it1)

↓
    
    
    Collection
    
    ↓
    
    +-----------+
    |1|2|3|
    +-----------+
    
          ↑
    
          it1
    
    ↑
    
    it2

* * *

# Vì sao Python thiết kế như vậy?

Nếu Iterator nằm trong Collection
    
    
    Collection
    
    ↓
    
    index

thì chỉ có thể
    
    
    lặp một lần

* * *

Nếu Iterator tách riêng
    
    
    Collection
    
    ↓
    
    Iterator A
    
    Iterator B
    
    Iterator C

thì có thể

  * nhiều vòng `for`
  * nhiều thread (nếu tự đồng bộ) 
  * nhiều thuật toán 
  * nested loop 



* * *

# Ví dụ Nested Loop
    
    
    numbers = NumberCollection([1, 2, 3])
    
    for a in numbers:
        for b in numbers:
            print(a, b)

↓
    
    
    1 1
    1 2
    1 3
    
    2 1
    2 2
    2 3
    
    3 1
    3 2
    3 3

Nếu chỉ có **một Iterator** , vòng lặp bên trong sẽ làm hỏng trạng thái của vòng lặp bên ngoài.

* * *

# Chứng minh điều đó

Ví dụ sai:
    
    
    class BadNumbers:
    
        def __init__(self):
            self.data = [1,2,3]
            self.index = 0
    
        def __iter__(self):
            return self
    
        def __next__(self):
    
            if self.index >= len(self.data):
                raise StopIteration
    
            value = self.data[self.index]
            self.index += 1
    
            return value

* * *
    
    
    obj = BadNumbers()
    
    for a in obj:
        for b in obj:
            print(a, b)

Kết quả
    
    
    1 2
    1 3

Vòng lặp ngoài bị "mất lượt" vì vòng lặp trong đã tiêu thụ cùng một Iterator.

* * *

# Thiết kế chuyên nghiệp

Hầu hết các thư viện đều thiết kế như sau:
    
    
    Iterable
    
    ↓
    
    immutable state
    
    ↓
    
    Iterator
    
    ↓
    
    mutable state

Ví dụ
    
    
    Path
    
    ↓
    
    DirectoryIterator

* * *
    
    
    QuerySet
    
    ↓
    
    QuerySetIterator

* * *
    
    
    CSVReader
    
    ↓
    
    CSVIterator

* * *

# Ví dụ hoàn chỉnh
    
    
    class StudentIterator:
    
        def __init__(self, students):
            self.students = students
            self.index = 0
    
        def __iter__(self):
            return self
    
        def __next__(self):
    
            if self.index >= len(self.students):
                raise StopIteration
    
            student = self.students[self.index]
            self.index += 1
            return student
    
    
    class Classroom:
    
        def __init__(self):
            self.students = []
    
        def add(self, name):
            self.students.append(name)
    
        def __iter__(self):
            return StudentIterator(self.students)
    
    
    room = Classroom()
    
    room.add("An")
    room.add("Bình")
    room.add("Chi")
    
    for student in room:
        print(student)
    
    print("-" * 20)
    
    for student in room:
        print(student)

Kết quả
    
    
    An
    Bình
    Chi
    --------------------
    An
    Bình
    Chi

* * *

# Đây chính là Collection Pattern
    
    
    Collection
    
    ↓
    
    Iterator
    
    ↓
    
    Current Item

Đây là một trong các **GoF Design Patterns (Iterator Pattern)** và Python áp dụng pattern này rất nhất quán.

* * *

# Thực tế trong Python

`pathlib.Path.iterdir()` không trả về `list`.

Nó trả về một Iterator.
    
    
    from pathlib import Path
    
    path = Path(".")
    
    it = path.iterdir()
    
    print(type(it))

Bạn sẽ thấy một Iterator chuyên dụng để duyệt thư mục.

Tương tự:
    
    
    import os
    
    entries = os.scandir(".")
    
    print(type(entries))

`os.scandir()` cũng trả về một Iterator thay vì đọc toàn bộ thư mục vào bộ nhớ.

* * *

# Khi nào gộp Iterable và Iterator?

Có những trường hợp một đối tượng **vừa là Iterable vừa là Iterator** , ví dụ:

  * Generator (`yield`) 
  * File object 
  * `itertools.count()`
  * `enumerate()`
  * `zip()`



Các đối tượng này mang tính **luồng dữ liệu (stream)** và thường chỉ được thiết kế để duyệt một lần.

Ngược lại, với các **Collection** (danh sách, cây, đồ thị, tập hợp kết quả...), hãy tách riêng `Iterable` và `Iterator`.

* * *

# Tổng kết buổi 7

Có hai cách thiết kế Iterator:

### Cách 1 (đơn giản)
    
    
    Object
    
    ↓
    
    Iterator

Phù hợp với:

  * Generator 
  * Stream 
  * File 
  * Dữ liệu chỉ đọc một lần 



* * *

### Cách 2 (chuyên nghiệp)
    
    
    Collection
    
    ↓
    
    Iterator

Phù hợp với:

  * List 
  * Tree 
  * Graph 
  * Linked List 
  * Framework 
  * Thư viện 
  * Collection tùy chỉnh 



Đây là cách bạn nên áp dụng khi xây dựng các cấu trúc dữ liệu hoặc API có khả năng lặp nhiều lần.

* * *

# Bài tập

## Bài 1

Tạo hai lớp:

  * `BookCollection`
  * `BookIterator`



Yêu cầu:

  * `BookCollection.add(title)` để thêm sách. 
  * Có thể dùng: 


    
    
    for book in books:
        print(book)

  * Có thể lặp nhiều lần mà kết quả luôn giống nhau. 



* * *

## Bài 2

Tạo hai Iterator độc lập:
    
    
    books = BookCollection(...)
    it1 = iter(books)
    it2 = iter(books)

Gọi `next()` xen kẽ trên `it1` và `it2` để chứng minh trạng thái của chúng không ảnh hưởng lẫn nhau.

* * *

## Bài 3

Viết `MatrixCollection` lưu ma trận 2 chiều và `MatrixIterator` duyệt toàn bộ phần tử theo thứ tự từng hàng (row-major order), ví dụ:
    
    
    1 2 3
    4 5 6

sẽ được duyệt thành:
    
    
    1
    2
    3
    4
    5
    6

Đây là một ví dụ rất gần với cách các thư viện xử lý dữ liệu (như NumPy hoặc pandas) xây dựng các Iterator tùy chỉnh.

Ở **Buổi 8** , chúng ta sẽ xây dựng **Iterator cho File** và học cách thiết kế các Iterator đọc dữ liệu theo từng dòng, từng khối (chunk) và theo kiểu **lazy loading** , một kỹ thuật rất quan trọng trong các ứng dụng xử lý dữ liệu lớn và web crawler.

