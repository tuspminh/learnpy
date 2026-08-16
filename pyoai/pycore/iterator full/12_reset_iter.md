# Iterator Deep Dive — Buổi 12

# Reset Iterator — Vì sao Iterator không thể reset?

Đây là buổi học cuối cùng của **Phần II - Tự xây Iterator**.

Đây cũng là một trong những chủ đề mà rất nhiều lập trình viên Python hiểu chưa đúng.

Một câu hỏi mà người mới thường hỏi là:

> **Tại sao Python không có`iterator.reset()`?**

Câu trả lời nằm ở triết lý thiết kế của Iterator Protocol.

* * *

# Roadmap

## Phần I — Nền tảng

  * ✅ Buổi 1. Iterator 
  * ✅ Buổi 2. Iterable 
  * ✅ Buổi 3. Iterator Protocol 
  * ✅ Buổi 4. for Loop 
  * ✅ Buổi 5. iter() 
  * ✅ Buổi 6. next() 



## Phần II — Tự xây Iterator

  * ✅ Buổi 7. Viết Iterator đầu tiên 
  * ✅ Buổi 8. Iterator cho File 
  * ✅ Buổi 9. Iterator cho Tree 
  * ✅ Buổi 10. Iterator cho Linked List 
  * ✅ Buổi 11. Iterator vô hạn 
  * ✅ **Buổi 12. Reset Iterator**



Tiếp theo

  * 🚀 Phần III — Generator 



* * *

# Câu hỏi đầu tiên

Ví dụ
    
    
    numbers = iter([10, 20, 30])
    
    print(next(numbers))

↓
    
    
    10

Muốn quay lại đầu
    
    
    numbers.reset()

Có được không?

↓

Không.

* * *

# Vì sao?

Iterator chỉ biết
    
    
    Tôi đang ở đâu?

Nó **không biết**
    
    
    Tôi được tạo từ cái gì?

* * *

Ví dụ
    
    
    numbers = iter([1, 2, 3])

Thực tế
    
    
    List
    
    ↓
    
    Iterator
    
    ↓
    
    index = 0

Iterator chỉ giữ
    
    
    index

Nó không có API chuẩn để nói
    
    
    hãy tạo tôi lại

* * *

# Minh họa

Ban đầu
    
    
    Iterator
    
    ↓
    
    index = 0

Sau
    
    
    next()

↓
    
    
    index = 1

Sau nữa

↓
    
    
    index = 2

Không có đường quay lại

↓
    
    
    0

* * *

# Ví dụ
    
    
    it = iter([1, 2, 3])
    
    print(next(it))
    print(next(it))

↓
    
    
    1
    2

Muốn đọc lại

↓

Không thể.

* * *

# Cách đúng

Tạo Iterator mới
    
    
    numbers = [1, 2, 3]
    
    it = iter(numbers)
    
    next(it)
    
    it = iter(numbers)
    
    print(next(it))

↓
    
    
    1

Không phải reset.

Là
    
    
    Tạo Iterator mới

* * *

# Iterable mới reset được

Đây là điều cực kỳ quan trọng.

Có
    
    
    Iterable

↓

mới tạo được
    
    
    Iterator mới

Ví dụ
    
    
    numbers = [1, 2, 3]
    
    it1 = iter(numbers)
    it2 = iter(numbers)

↓

Hai Iterator khác nhau.

* * *

# Generator có reset không?
    
    
    def numbers():
        yield 1
        yield 2
        yield 3
    
    
    g = numbers()
    
    print(next(g))

↓
    
    
    1

Muốn reset

↓

Không thể.

* * *

Phải
    
    
    g = numbers()

Tạo Generator mới.

* * *

# File có reset không?
    
    
    with open("story.txt") as f:
    
        print(next(f))

↓
    
    
    Line 1

Muốn đọc lại?

Có hai cách.

* * *

# Cách 1
    
    
    f.seek(0)

↓

Con trỏ file quay về đầu.

* * *

# Cách 2

Đóng rồi mở lại file.
    
    
    with open("story.txt") as f:
        ...

* * *

# seek() có phải reset Iterator không?

Không.

Nó chỉ thay đổi
    
    
    File Pointer

Ví dụ
    
    
    File
    
    ↓
    
    Position = 300 bytes

↓
    
    
    seek(0)

↓
    
    
    Position = 0

Iterator của file đọc dựa trên vị trí con trỏ này.

* * *

# Infinite Iterator
    
    
    counter = Counter()

Có reset không?

Không.

Muốn bắt đầu lại

↓
    
    
    counter = Counter()

* * *

# Vì sao Python thiết kế như vậy?

Nếu Iterator có
    
    
    reset()

thì phải lưu

  * dữ liệu gốc 
  * trạng thái gốc 
  * cách tạo lại 



Điều này **không khả thi** với nhiều nguồn dữ liệu.

Ví dụ:
    
    
    cursor = database.execute(...)

Đã đọc 10.000 dòng.

Reset?

Database có thể đã thay đổi.

* * *

# Network Stream
    
    
    Server
    
    ↓
    
    Data
    
    ↓
    
    Socket

Đã đọc
    
    
    100 KB

Reset?

Không thể.

Server không gửi lại.

* * *

# Camera
    
    
    Camera
    
    ↓
    
    Frame
    
    ↓
    
    Frame
    
    ↓
    
    Frame

Frame cũ mất rồi.

Không reset.

* * *

# Sensor
    
    
    25.1
    
    ↓
    
    25.2
    
    ↓
    
    25.3

Không thể quay về
    
    
    25.1

* * *

# Iterator là Stream

Đây là tư duy quan trọng.

Iterator thường đại diện cho
    
    
    Một luồng dữ liệu

Không phải
    
    
    Một Collection

Collection

↓

Có thể tạo Iterator mới.

Stream

↓

Không.

* * *

# Nếu muốn reset?

Tự thiết kế.

Ví dụ
    
    
    class Counter:
    
        def __init__(self):
            self.value = 0
    
        def __iter__(self):
            return self
    
        def __next__(self):
            self.value += 1
            return self.value
    
        def reset(self):
            self.value = 0

Sử dụng
    
    
    c = Counter()
    
    print(next(c))
    print(next(c))
    
    c.reset()
    
    print(next(c))

↓
    
    
    1
    2
    1

Đây **không phải** là Iterator Protocol.

Là API do bạn tự thêm.

* * *

# Thiết kế chuyên nghiệp hơn

Không reset Iterator.

Reset Collection.
    
    
    class CounterCollection:
    
        def __iter__(self):
            return CounterIterator()

↓

Mỗi lần
    
    
    iter(collection)

↓

Iterator mới.

Đây là cách `list`, `tuple`, `dict`, `set` hoạt động.

* * *

# Snapshot Iterator

Có trường hợp muốn reset.

Ta tạo bản sao.
    
    
    data = [1, 2, 3]
    
    snapshot = list(data)
    
    it = iter(snapshot)

Muốn đọc lại

↓
    
    
    it = iter(snapshot)

Không ảnh hưởng dữ liệu gốc.

* * *

# tee()

Python có công cụ đặc biệt.
    
    
    import itertools
    
    numbers = iter([1,2,3])
    
    a, b = itertools.tee(numbers)

↓

Hai Iterator.
    
    
    print(next(a))

↓
    
    
    1
    
    
    print(next(b))

↓
    
    
    1

Có vẻ như reset?

Không.

* * *

# tee() hoạt động thế nào?

Thực tế
    
    
    Iterator
    
    ↓
    
    Cache
    
    ↓
    
    Iterator A
    
    Iterator B

Khi A đọc

↓

Dữ liệu được lưu vào cache.

B đọc sau

↓

Lấy từ cache.

Không hề reset nguồn dữ liệu.

* * *

# Ví dụ
    
    
    import itertools
    
    it = iter([10, 20, 30])
    
    a, b = itertools.tee(it)
    
    print(next(a))
    print(next(a))
    
    print(next(b))

↓
    
    
    10
    20
    10

* * *

# Nhược điểm của tee()

Nếu
    
    
    A

đọc
    
    
    1 triệu phần tử
    
    
    B

chưa đọc

↓

Cache sẽ chứa
    
    
    1 triệu phần tử

↓

Tốn RAM.

* * *

# Thiết kế Iterator Resettable

Nếu thực sự cần.
    
    
    class ResettableIterator:
    
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
    
        def reset(self):
            self.index = 0

Đây là API mở rộng, không phải chuẩn Python.

* * *

# Thực tế các thư viện

Thư viện| Reset được?| Cách làm  
---|---|---  
`list`| ✔| `iter(list)`  
`tuple`| ✔| `iter(tuple)`  
`dict`| ✔| `iter(dict)`  
Generator| ✘| Tạo generator mới  
File| ✔| `seek(0)` hoặc mở lại  
`itertools.count()`| ✘| Tạo object mới  
Database Cursor| ✘| Chạy lại truy vấn  
Socket| ✘| Kết nối lại  
Sensor Stream| ✘| Không thể  
  
* * *

# Một nguyên tắc thiết kế quan trọng

Khi xây dựng thư viện, hãy tự hỏi:

**Đối tượng của bạn là Collection hay Stream?**

Nếu là **Collection** :
    
    
    Collection
    
    ↓
    
    iter()
    
    ↓
    
    Iterator mới

Ví dụ:

  * Danh sách sản phẩm 
  * Danh sách chapter truyện 
  * Danh sách user 



* * *

Nếu là **Stream** :
    
    
    Stream
    
    ↓
    
    Iterator

Ví dụ:

  * WebSocket 
  * Log file đang ghi 
  * Camera 
  * AI token stream 
  * Kafka consumer 



Không nên có `reset()`.

* * *

# Ví dụ trong dự án crawler

Giả sử bạn có:
    
    
    crawler = ChapterCrawler()

Nếu crawler đang tải dữ liệu trực tiếp từ Internet:
    
    
    chapter = next(crawler)

Sau khi đã tải đến chương 100, việc "reset" có thể không còn hợp lệ vì:

  * Website đã cập nhật chương mới. 
  * Chương cũ có thể bị sửa. 
  * Kết nối mạng đã thay đổi. 



Thiết kế hợp lý hơn là:
    
    
    crawler = ChapterCrawler(start_page=1)

tạo **một crawler mới** thay vì reset crawler cũ.

* * *

# Tổng kết Phần II — Tự xây Iterator

Qua 6 buổi (7–12), bạn đã học được cách:

  * Thiết kế `Iterable` và `Iterator` tách biệt. 
  * Xây dựng Iterator cho: 
    * Collection đơn giản 
    * File 
    * Tree 
    * Linked List 
  * Thiết kế Infinite Iterator. 
  * Hiểu vì sao Iterator thông thường **không có reset**. 
  * Phân biệt rõ **Collection** và **Stream** trong thiết kế API. 



Đây là nền tảng để bước sang **Generator** , nơi Python giúp bạn viết Iterator chỉ với từ khóa `yield`.

* * *

# Bài tập

## Bài 1

Viết `ResettableRangeIterator`:
    
    
    it = ResettableRangeIterator(1, 5)
    
    print(next(it))
    print(next(it))
    
    it.reset()
    
    print(next(it))

Kết quả:
    
    
    1
    2
    1

* * *

## Bài 2

Dùng `itertools.tee()` để tạo ba Iterator từ cùng một nguồn:
    
    
    it = iter(range(5))
    a, b, c = itertools.tee(it, 3)

Gọi `next()` xen kẽ trên `a`, `b`, `c` và giải thích vì sao mỗi Iterator vẫn nhận được đúng dữ liệu.

* * *

## Bài 3

Thiết kế hai lớp:

  * `BookCollection`
  * `BookIterator`



Trong đó:

  * `BookCollection` lưu danh sách sách. 
  * Mỗi lần gọi `iter(BookCollection)` phải trả về một `BookIterator` mới. 
  * Chứng minh có thể lặp qua `BookCollection` nhiều lần mà không cần bất kỳ phương thức `reset()` nào. 



* * *

# Kết thúc Phần II

Đến đây, bạn đã nắm vững **Iterator Protocol** và biết cách tự xây dựng nhiều loại Iterator khác nhau.

**Buổi 13** sẽ mở đầu **Phần III — Generator** , nơi bạn sẽ khám phá một trong những tính năng mạnh nhất của Python: **Generator chính là một cách viết Iterator cực kỳ ngắn gọn bằng`yield`**. Chúng ta sẽ so sánh Generator với Iterator tự cài đặt, phân tích ưu nhược điểm, và xem bên trong Python đã biến một hàm chứa `yield` thành Iterator như thế nào.

