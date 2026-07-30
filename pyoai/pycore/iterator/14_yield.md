# Iterator Deep Dive

# Phần III — Generator

# Buổi 14: `yield` Deep Dive — Trái tim của Generator

Đây là **buổi quan trọng nhất của phần Generator**.

Nếu Buổi 13 trả lời câu hỏi:

> **Generator là gì?**

thì Buổi 14 sẽ trả lời:

> **`yield` thực sự làm gì bên trong CPython?**

Sau buổi này bạn sẽ hiểu:

  * `yield` không phải `return`
  * `yield` lưu toàn bộ trạng thái của hàm 
  * Generator Frame 
  * Suspension Point (điểm tạm dừng) 
  * Resume (tiếp tục thực thi) 
  * Generator State Machine 
  * Vì sao `yield` cực kỳ tiết kiệm bộ nhớ 



* * *

# Roadmap

## Phần III — Generator

  * ✅ Buổi 13 — Generator là Iterator 
  * ✅ **Buổi 14 — yield Deep Dive**
  * Buổi 15 — `yield from`
  * Buổi 16 — Generator Expression 



* * *

# Ôn tập

Generator
    
    
    def numbers():
        yield 1
        yield 2
        yield 3

Sử dụng
    
    
    g = numbers()
    
    print(next(g))
    print(next(g))

↓
    
    
    1
    2

Đến đây chúng ta biết **Generator hoạt động**.

Hôm nay chúng ta tìm hiểu **vì sao nó hoạt động được.**

* * *

# yield KHÔNG phải return

Đây là nhầm lẫn lớn nhất.

## return
    
    
    def f():
    
        print("A")
    
        return 10
    
        print("B")

↓
    
    
    A
    10

`print("B")`

không bao giờ chạy.

* * *

## yield
    
    
    def g():
    
        print("A")
    
        yield 10
    
        print("B")

Lần đầu
    
    
    gen = g()
    
    print(next(gen))

↓
    
    
    A
    10

* * *

Lần hai
    
    
    next(gen)

↓
    
    
    B
    
    StopIteration

Khác hoàn toàn.

* * *

# Điều gì xảy ra?

`yield`

không kết thúc hàm.

Nó chỉ nói
    
    
    Tạm dừng tại đây.

* * *

# Minh họa
    
    
    A
    
    ↓
    
    yield
    
    ↓
    
    PAUSE
    
    ↓
    
    Resume
    
    ↓
    
    B

Đây gọi là

> **Suspension Point**

* * *

# Suspension Point

Mỗi `yield`

là một
    
    
    Checkpoint

Python nhớ

  * đang ở dòng nào 
  * biến cục bộ 
  * stack frame 
  * exception context 



Tất cả đều được giữ nguyên.

* * *

# Ví dụ
    
    
    def demo():
    
        x = 10
    
        yield x
    
        x += 5
    
        yield x

Lần đầu
    
    
    g = demo()
    
    print(next(g))

↓
    
    
    10

* * *

Lần hai
    
    
    print(next(g))

↓
    
    
    15

Điều này chứng minh
    
    
    x vẫn còn tồn tại.

Nếu là `return`

thì `x`

đã bị hủy.

* * *

# Generator nhớ Local Variables

Ví dụ
    
    
    def counter():
    
        i = 1
    
        while True:
    
            yield i
    
            i += 1

Lần đầu

↓
    
    
    yield 1

Python nhớ
    
    
    i = 1

* * *

Sau Resume

↓
    
    
    i += 1

↓
    
    
    i = 2

↓
    
    
    yield 2

Lại nhớ
    
    
    i = 2

* * *

# Nếu là hàm bình thường?
    
    
    def f():
    
        i = 1
    
        return i

Mỗi lần gọi

↓
    
    
    i = 1

khởi tạo lại từ đầu.

Generator thì không.

* * *

# Generator Frame

Mỗi Generator có một
    
    
    Frame

Chứa
    
    
    Generator
    
    ↓
    
    Frame
    
    ↓
    
    Local Variables
    
    ↓
    
    Instruction Pointer
    
    ↓
    
    Evaluation Stack

Frame này tồn tại cho đến khi Generator kết thúc.

* * *

# Kiểm tra Frame
    
    
    def demo():
    
        x = 100
    
        yield x
    
    
    g = demo()
    
    print(g.gi_frame)

↓
    
    
    <frame object ...>

Generator có thuộc tính
    
    
    gi_frame

* * *

# Local Variables

Sau
    
    
    next(g)

ta có
    
    
    print(g.gi_frame.f_locals)

↓
    
    
    {'x':100}

Python vẫn giữ
    
    
    x

trong bộ nhớ.

* * *

# Instruction Pointer

Generator cũng nhớ
    
    
    Đang đứng ở dòng nào.

Ví dụ
    
    
    def demo():
    
        yield 1
    
        yield 2
    
        yield 3

Sau lần đầu

↓

Python nhớ
    
    
    Lần tới chạy từ yield đầu tiên.

Không chạy lại từ đầu.

* * *

# Minh họa
    
    
    yield 1
    
    ↓
    
    STOP
    
    ↓
    
    yield 2
    
    ↓
    
    STOP
    
    ↓
    
    yield 3

* * *

# next()

Lần đầu
    
    
    next(g)

↓
    
    
    Start
    
    ↓
    
    yield
    
    ↓
    
    Pause

* * *

Lần hai

↓
    
    
    Resume
    
    ↓
    
    yield
    
    ↓
    
    Pause

* * *

Lần ba

↓
    
    
    Resume
    
    ↓
    
    End

* * *

# Generator State Machine
    
    
    Created
    
    ↓
    
    Running
    
    ↓
    
    Suspended
    
    ↓
    
    Running
    
    ↓
    
    Suspended
    
    ↓
    
    Closed

Đây là sơ đồ rất quan trọng.

* * *

# Kiểm tra trạng thái
    
    
    import inspect
    
    g = demo()
    
    print(inspect.getgeneratorstate(g))

↓
    
    
    GEN_CREATED

* * *

Sau
    
    
    next(g)

↓
    
    
    GEN_SUSPENDED

* * *

Sau khi hết

↓
    
    
    GEN_CLOSED

* * *

# Generator chỉ chạy khi cần

Ví dụ
    
    
    def huge():
    
        for i in range(1000000000):
    
            yield i
    
    
    g = huge()

Lúc này

↓
    
    
    0 số

được tạo.

* * *

Sau
    
    
    next(g)

↓
    
    
    0

mới được tạo.

* * *

Sau
    
    
    next(g)

↓
    
    
    1

mới được tạo.

* * *

Không bao giờ có
    
    
    1 tỷ số

trong RAM.

* * *

# So sánh với List

List
    
    
    numbers = list(range(1000000000))

Python phải tạo
    
    
    1 tỷ object

trước.

* * *

Generator
    
    
    numbers = huge()

↓
    
    
    Chưa tạo gì.

* * *

# Ví dụ trực quan
    
    
    def read_book():
    
        print("Đọc trang 1")
        yield "Trang 1"
    
        print("Đọc trang 2")
        yield "Trang 2"
    
        print("Đọc trang 3")
        yield "Trang 3"

Lần đầu
    
    
    book = read_book()
    
    print(next(book))

↓
    
    
    Đọc trang 1
    Trang 1

* * *

Lần hai

↓
    
    
    Đọc trang 2
    Trang 2

Không đọc lại trang 1.

* * *

# Nhiều yield
    
    
    def f():
    
        yield "A"
    
        yield "B"
    
        yield "C"

Python tạo
    
    
    A
    
    ↓
    
    Pause
    
    ↓
    
    B
    
    ↓
    
    Pause
    
    ↓
    
    C

* * *

# yield trong vòng lặp
    
    
    def squares():
    
        i = 1
    
        while True:
    
            yield i * i
    
            i += 1

Mỗi lần Resume

↓
    
    
    i

vẫn còn.

* * *

# Generator lưu Call Stack

Ví dụ
    
    
    def demo():
    
        x = 5
    
        y = x * 2
    
        yield y
    
        z = y + 3
    
        yield z

Sau yield đầu tiên

Python vẫn nhớ
    
    
    x = 5
    
    y = 10

Không phải tính lại.

* * *

# Một ví dụ gần với dự án crawler
    
    
    def crawl_pages():
    
        page = 1
    
        while True:
    
            print(f"Tải page {page}")
    
            html = f"<html>Page {page}</html>"
    
            yield html
    
            page += 1

Mỗi lần
    
    
    next(crawler)

Generator sẽ:

  1. Tải đúng **một** trang. 
  2. Trả HTML. 
  3. Tạm dừng. 
  4. Giữ nguyên `page`. 
  5. Lần sau tiếp tục từ đúng vị trí. 



Đây là cách rất nhiều thư viện crawler hoặc xử lý dữ liệu theo luồng được thiết kế.

* * *

# So sánh Iterator Class và Generator

Iterator Class
    
    
    class Counter:
    
        def __init__(self):
            self.i = 0
    
        def __iter__(self):
            return self
    
        def __next__(self):
            self.i += 1
            return self.i

Generator
    
    
    def counter():
    
        i = 0
    
        while True:
            i += 1
            yield i

Ở phiên bản Generator:

  * Không cần `__iter__`. 
  * Không cần `__next__`. 
  * Không cần tự quản lý `StopIteration`. 
  * Python tự lưu toàn bộ trạng thái. 



* * *

# Những hiểu lầm phổ biến

## Sai lầm 1

> `yield` giống `return`.

❌ Sai.

`return` kết thúc hàm, `yield` chỉ tạm dừng.

* * *

## Sai lầm 2

> Generator chạy ngay khi gọi hàm.

❌ Sai.
    
    
    g = generator()

chỉ tạo Generator Object.

* * *

## Sai lầm 3

> Sau `yield`, biến cục bộ bị mất.

❌ Sai.

Generator giữ nguyên toàn bộ local variables trong `gi_frame`.

* * *

## Sai lầm 4

> Mỗi lần `next()` hàm chạy lại từ đầu.

❌ Sai.

Generator tiếp tục từ đúng vị trí đã `yield`.

* * *

# Tổng kết buổi 14

Bạn cần nhớ 8 ý quan trọng:

  1. `yield` **không phải** `return`. 
  2. `yield` tạo ra một **Suspension Point**. 
  3. Generator lưu toàn bộ **Frame** của hàm. 
  4. Biến cục bộ vẫn tồn tại sau mỗi `yield`. 
  5. Generator nhớ chính xác vị trí thực thi. 
  6. `next()` chỉ tiếp tục từ nơi đã dừng. 
  7. Generator chỉ sinh dữ liệu khi cần (**Lazy Evaluation**). 
  8. Toàn bộ cơ chế này được Python quản lý tự động, giúp bạn không cần tự cài `__next__()` như khi viết Iterator Class. 



* * *

# Bài tập

## Bài 1

Viết Generator:
    
    
    def countdown(start):
        ...

Yêu cầu:

  * In `"Preparing..."` trước `yield` đầu tiên. 
  * Mỗi lần `yield` trả về một số giảm dần. 
  * Sau khi kết thúc, in `"Done!"`. 



Quan sát thứ tự các thông báo để hiểu rõ điểm tạm dừng của `yield`.

* * *

## Bài 2

Viết Generator:
    
    
    def file_reader(lines):
        ...

Trong đó `lines` là một danh sách chuỗi.

Mỗi lần `yield`:

  * In `"Reading line..."`. 
  * Trả về đúng một dòng. 
  * Chứng minh rằng chỉ khi gọi `next()` thì dòng tiếp theo mới được "đọc". 



* * *

## Bài 3

Viết Generator:
    
    
    def crawler(urls):
        ...

Mỗi lần:

  1. In: 


    
    
    Downloading: <url>

  2. `yield` nội dung HTML giả lập. 
  3. Sau khi được `next()` lần tiếp theo, in: 


    
    
    Finished: <url>

Bài tập này giúp bạn thấy rõ rằng mã **sau`yield`** chỉ được thực thi khi Generator được tiếp tục, không phải ngay lúc `yield` xảy ra.

* * *

**Buổi 15** sẽ học về **`yield from`** —một trong những tính năng mạnh và tinh tế nhất của Generator. Bạn sẽ hiểu vì sao `yield from` không chỉ là "vòng lặp viết tắt", mà còn là cơ chế **ủy quyền (delegation)** giữa các Generator, được sử dụng rộng rãi trong các framework bất đồng bộ và các pipeline xử lý dữ liệu.

