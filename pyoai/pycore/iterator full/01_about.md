# Buổi 1 — Iterator là gì?

* * *

## Bài toán

Giả sử có một danh sách
    
    
    numbers = [10, 20, 30, 40]

Ta viết
    
    
    for n in numbers:
        print(n)

Kết quả
    
    
    10
    20
    30
    40

Câu hỏi:

**Python lấy từng phần tử bằng cách nào?**

Có phải `for` biết danh sách có bao nhiêu phần tử không?

Không.

Python hoàn toàn **không quan tâm đối tượng là list hay tuple**.

Nó chỉ cần một thứ:

> Iterator

* * *

# Hình dung

Giả sử có hộp chứa bóng.
    
    
    +----------------------+
    | 10 |
    | 20 |
    | 30 |
    | 40 |
    +----------------------+

Iterator giống như một bàn tay.
    
    
    next()
    
    ↓
    
    10
    
    ↓
    
    next()
    
    ↓
    
    20
    
    ↓
    
    next()
    
    ↓
    
    30

Mỗi lần gọi
    
    
    next()

nó chỉ đưa ra **một phần tử**.

* * *

# Iterator không chứa dữ liệu

Đây là điều rất nhiều người hiểu sai.

Ví dụ
    
    
    numbers = [1, 2, 3]

Iterator KHÔNG tạo bản sao.

Sai:
    
    
    Iterator
    
    1
    2
    3

Đúng:
    
    
    List
    
    1
    2
    3
    
    ↑
    
    Iterator chỉ nhớ:
    
    "đang đứng ở vị trí nào"

Nó giống con trỏ.
    
    
    [1][2][3]
    
     ^

Sau `next()`
    
    
    [1][2][3]
    
        ^

* * *

# Ví dụ
    
    
    numbers = [10, 20, 30]
    
    it = iter(numbers)
    
    print(it)

Kết quả
    
    
    <list_iterator object at ...>

Không phải list.

Mà là
    
    
    list_iterator

* * *

# Lấy phần tử
    
    
    numbers = [10, 20, 30]
    
    it = iter(numbers)
    
    print(next(it))
    print(next(it))
    print(next(it))

Kết quả
    
    
    10
    20
    30

Sau đó
    
    
    next(it)

sẽ báo lỗi
    
    
    StopIteration

* * *

# Vì sao lại có StopIteration?

Iterator nói với Python

> Tôi hết dữ liệu rồi.

Thay vì trả về `None`.

Nếu trả về `None` thì không phân biệt được:
    
    
    None

là dữ liệu thật

hay
    
    
    hết dữ liệu

Ví dụ
    
    
    numbers = [1, None, 3]

Nếu trả về `None`

Python sẽ tưởng
    
    
    hết dữ liệu

→ sai.

Do đó Python tạo ngoại lệ đặc biệt:
    
    
    StopIteration

* * *

# Minh họa
    
    
    next()
    
    ↓
    
    10
    
    next()
    
    ↓
    
    20
    
    next()
    
    ↓
    
    30
    
    next()
    
    ↓
    
    StopIteration

* * *

# Iterator nhớ trạng thái

Ví dụ
    
    
    numbers = [10, 20, 30]
    
    it = iter(numbers)
    
    print(next(it))

Iterator nhớ
    
    
    đã đọc tới số 10

Lần tiếp
    
    
    print(next(it))

Nó không quay lại đầu.

Mà tiếp tục
    
    
    20

* * *

# Ví dụ hoàn chỉnh
    
    
    numbers = [100, 200, 300]
    
    it = iter(numbers)
    
    print(next(it))
    print(next(it))
    
    print("Làm việc khác...")
    
    print(next(it))

Kết quả
    
    
    100
    200
    Làm việc khác...
    300

Iterator không quên vị trí.

* * *

# Một Iterator chỉ đi một chiều

Sau khi đọc hết
    
    
    100
    200
    300

thì
    
    
    for x in it:
        print(x)

không in gì cả.

Muốn đọc lại
    
    
    it = iter(numbers)

* * *

# Ví dụ
    
    
    numbers = [1, 2, 3]
    
    it = iter(numbers)
    
    for x in it:
        print(x)
    
    print("Lần hai")
    
    for x in it:
        print(x)

Kết quả
    
    
    1
    2
    3
    Lần hai

Không còn gì.

* * *

# Tại sao Iterator tiết kiệm RAM?

Giả sử có
    
    
    10 tỷ số

Nếu tạo list
    
    
    [1,2,3,...]

RAM sẽ rất lớn.

Iterator chỉ giữ
    
    
    phần tử hiện tại

Ví dụ
    
    
    Database
    
    ↓
    
    Iterator
    
    ↓
    
    Record hiện tại
    
    ↓
    
    Xử lý
    
    ↓
    
    Record tiếp theo

Đây là lý do iterator được dùng rất nhiều trong:

  * đọc file lớn 
  * xử lý CSV lớn 
  * đọc dữ liệu từ cơ sở dữ liệu 
  * web crawler 
  * API phân trang 
  * xử lý log 
  * AI pipeline 



* * *

# Ví dụ thực tế: đọc file
    
    
    with open("data.txt", "r", encoding="utf-8") as f:
        for line in f:
            print(line.rstrip())

Bạn không cần đọc toàn bộ file vào RAM. Đối tượng file tự đóng vai trò là một iterator, trả về từng dòng khi vòng lặp yêu cầu.

* * *

# Ví dụ tự gọi `next()`
    
    
    text = "Python"
    
    it = iter(text)
    
    while True:
        try:
            ch = next(it)
            print(ch)
        except StopIteration:
            print("Hết dữ liệu.")
            break

Kết quả:
    
    
    P
    y
    t
    h
    o
    n
    Hết dữ liệu.

Ở đây bạn đang làm đúng những gì `for` thực hiện ở bên trong, chỉ khác là `for` tự bắt ngoại lệ `StopIteration` để kết thúc vòng lặp một cách tự nhiên.

* * *

# Bên trong vòng lặp `for`

Đoạn mã:
    
    
    for x in numbers:
        print(x)

về bản chất tương đương:
    
    
    it = iter(numbers)
    
    while True:
        try:
            x = next(it)
        except StopIteration:
            break
    
        print(x)

Đây là một trong những ý tưởng cốt lõi của Python: **`for` không lặp theo chỉ số, mà lặp bằng giao thức Iterator (Iterator Protocol).**

* * *

# Tổng kết buổi 1

Sau buổi học này, bạn cần nắm vững các ý sau:

  * Iterator là đối tượng trả về **từng phần tử một** khi gọi `next()`. 
  * Iterator **không lưu dữ liệu** , mà chỉ theo dõi vị trí hiện tại trong quá trình duyệt. 
  * Hết dữ liệu sẽ phát sinh `StopIteration`. 
  * Iterator thường chỉ duyệt được **một lần**. 
  * Hàm `for` hoạt động dựa trên `iter()` và `next()`, không phụ thuộc vào việc đối tượng là `list`, `tuple`, `set` hay kiểu dữ liệu nào khác. 
  * Iterator là nền tảng cho các kỹ thuật xử lý dữ liệu lớn, lazy evaluation và generator. 



* * *

### Bài tập

  1. Tạo một `list`, một `tuple` và một `string`, sau đó: 
     * Gọi `iter()`. 
     * Dùng `next()` để lấy từng phần tử. 
     * Quan sát `StopIteration` khi đọc hết dữ liệu. 
  2. Viết lại một vòng lặp `for` bằng `while True` \+ `next()` \+ `try/except StopIteration`. 
  3. Chứng minh rằng iterator chỉ duyệt được một lần bằng cách: 
     * Duyệt hết một iterator. 
     * Thử duyệt lại. 
     * Tạo iterator mới từ cùng dữ liệu và duyệt lại. 



Ở **Buổi 2** , chúng ta sẽ học **Iterable là gì?** , phân biệt rõ **Iterable** và **Iterator** —một chủ đề mà rất nhiều lập trình viên Python mới thường nhầm lẫn.

