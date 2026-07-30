# Decorator Deep Dive — Buổi 4

# LEGB Scope & Name Resolution (Hiểu cách Python tìm biến)

> **Mục tiêu buổi học**

Sau buổi này bạn sẽ hiểu:

  * Scope (phạm vi biến) là gì. 
  * LEGB Rule hoạt động như thế nào. 
  * Python tìm biến theo thứ tự nào. 
  * `global` và `nonlocal` khác nhau ra sao. 
  * Shadowing (che khuất biến). 
  * Late Binding - nguyên nhân gây lỗi phổ biến trong Closure và Decorator. 
  * Best Practices. 



* * *

# Roadmap chúng ta đã đi

✓ Buổi 1: Function là Object

✓ Buổi 2: First-Class Function

✓ Buổi 3: Closure

➡ Hôm nay: LEGB Scope

Sau buổi này chúng ta sẽ đủ kiến thức để bắt đầu viết Decorator thật sự.

* * *

# 1\. Scope là gì?

Scope là:

> Phạm vi mà một biến có thể được truy cập.

Ví dụ
    
    
    x = 10
    
    print(x)

`x` đang ở phạm vi toàn cục.

* * *

Ví dụ
    
    
    def hello():
        y = 20
        print(y)
    
    hello()

Biến `y` chỉ tồn tại trong `hello()`.

Sau đó
    
    
    print(y)

sẽ lỗi
    
    
    NameError

* * *

# 2\. LEGB Rule

Python luôn tìm biến theo đúng thứ tự:
    
    
    L
    ↓
    
    E
    ↓
    
    G
    ↓
    
    B

Có nghĩa là
    
    
    Local
    
    ↓
    
    Enclosing
    
    ↓
    
    Global
    
    ↓
    
    Built-in

Python KHÔNG tìm ngẫu nhiên.

Nó luôn tìm theo thứ tự trên.

* * *

# 3\. L = Local

Ví dụ
    
    
    x = 100
    
    def hello():
        x = 10
        print(x)
    
    hello()

Kết quả
    
    
    10

Python thấy Local trước.
    
    
    hello()
    
    ↓
    
    Local x = 10

Nó dừng luôn.

Không tìm tiếp.

* * *

# 4\. E = Enclosing

Đây là Scope của hàm cha.
    
    
    def outer():
    
        x = 20
    
        def inner():
            print(x)
    
        inner()
    
    outer()

Kết quả
    
    
    20

Python tìm
    
    
    inner()
    
    ↓
    
    Local
    
    không có
    
    ↓
    
    Enclosing
    
    x = 20

* * *

# 5\. G = Global
    
    
    x = 50
    
    def hello():
        print(x)
    
    hello()
    
    
    50

Python tìm
    
    
    Local
    
    ↓
    
    không có
    
    ↓
    
    Global
    
    ↓
    
    50

* * *

# 6\. B = Built-in

Ví dụ
    
    
    print(len("Python"))

Ta chưa hề khai báo
    
    
    len

Python tìm
    
    
    Local
    
    ↓
    
    Enclosing
    
    ↓
    
    Global
    
    ↓
    
    Built-in
    
    ↓
    
    len

* * *

Ví dụ
    
    
    print(max([1,2,3]))

`max`

cũng là Built-in.

* * *

# 7\. Minh họa LEGB
    
    
    x = "Global"
    
    def outer():
    
        x = "Outer"
    
        def inner():
    
            x = "Inner"
    
            print(x)
    
        inner()
    
    outer()

Kết quả
    
    
    Inner

Python thấy Local đầu tiên.

* * *

Nếu bỏ
    
    
    x = "Inner"

thì
    
    
    Outer

* * *

Nếu bỏ luôn
    
    
    x = "Outer"

thì
    
    
    Global

* * *

Nếu bỏ luôn
    
    
    x = "Global"

thì
    
    
    NameError

* * *

# 8\. Shadowing (Che khuất biến)

Ví dụ
    
    
    x = 100
    
    def hello():
    
        x = 5
    
        print(x)
    
    hello()
    
    print(x)

Kết quả
    
    
    5
    100

Hai biến khác nhau.
    
    
    Global x
    
    ↓
    
    100
    
    
    Local x
    
    ↓
    
    5

Local che khuất Global.

* * *

# 9\. global

Ví dụ
    
    
    count = 0
    
    def increase():
        count += 1

Lỗi
    
    
    UnboundLocalError

Python nghĩ
    
    
    count

là Local.

* * *

Muốn sửa Global
    
    
    count = 0
    
    def increase():
        global count
    
        count += 1
    
    increase()
    
    print(count)
    
    
    1

* * *

# 10\. nonlocal

Đây là từ khóa cực kỳ quan trọng đối với Decorator.

Ví dụ
    
    
    def outer():
    
        count = 0
    
        def inner():
    
            nonlocal count
    
            count += 1
    
            print(count)
    
        return inner
    
    
    f = outer()
    
    f()
    f()
    f()
    
    
    1
    2
    3

* * *

Không có
    
    
    nonlocal

thì
    
    
    UnboundLocalError

* * *

# 11\. global vs nonlocal

Global
    
    
    Module
    
    ↓
    
    Variable

Nonlocal
    
    
    Outer Function
    
    ↓
    
    Variable

Ví dụ
    
    
    x = 10
    
    def outer():
    
        y = 20
    
        def inner():
    
            global x
    
            nonlocal y
    
            x += 1
    
            y += 1
    
            print(x, y)
    
        inner()
    
    outer()

Kết quả
    
    
    11 21

* * *

# 12\. Late Binding (Lỗi nổi tiếng)

Đây là lỗi mà gần như ai học Closure cũng gặp.

Ví dụ
    
    
    funcs = []
    
    for i in range(3):
    
        def show():
            print(i)
    
        funcs.append(show)

Sau đó
    
    
    for f in funcs:
        f()

Bạn nghĩ kết quả là
    
    
    0
    1
    2

Không.

Thực tế
    
    
    2
    2
    2

* * *

## Tại sao?

Closure không lưu giá trị.

Closure lưu **tham chiếu**.

Sau vòng lặp
    
    
    i
    
    ↓
    
    2

Tất cả Closure cùng nhìn vào một biến.
    
    
    show1
    
    ↓
    
    i
    
    ↓
    
    2
    
    show2
    
    ↓
    
    i
    
    ↓
    
    2
    
    show3
    
    ↓
    
    i
    
    ↓
    
    2

* * *

# 13\. Cách sửa Late Binding

Cách phổ biến nhất là dùng tham số mặc định.
    
    
    funcs = []
    
    for i in range(3):
    
        def show(i=i):
            print(i)
    
        funcs.append(show)

Kết quả
    
    
    0
    1
    2

Vì
    
    
    i=i

được đánh giá ngay khi tạo hàm.

Mỗi hàm có bản sao riêng.

* * *

# 14\. Sửa bằng Factory Function
    
    
    def create(i):
    
        def show():
            print(i)
    
        return show
    
    
    funcs = []
    
    for i in range(3):
        funcs.append(create(i))

Kết quả
    
    
    0
    1
    2

Đây là cách mà nhiều framework áp dụng.

* * *

# 15\. Kiểm tra Scope
    
    
    x = 10
    
    def outer():
    
        y = 20
    
        def inner():
    
            z = 30
    
            print(locals())
    
        inner()
    
    outer()
    
    print(globals()["x"])

Kết quả
    
    
    {'z': 30}
    10

* * *

# 16\. Ví dụ hoàn chỉnh — Bộ đếm lượt gọi
    
    
    def make_call_counter():
    
        count = 0
    
        def wrapper(name):
    
            nonlocal count
    
            count += 1
    
            print(f"Call {count}: {name}")
    
        return wrapper
    
    
    counter = make_call_counter()
    
    counter("backup")
    counter("clean")
    counter("upload")

Kết quả
    
    
    Call 1: backup
    Call 2: clean
    Call 3: upload

Đây chính là ý tưởng của nhiều decorator như:

  * `@retry`
  * `@cache`
  * `@timer`
  * `@rate_limit`



Tất cả đều cần lưu trạng thái trong Closure.

* * *

# 17\. Ví dụ hoàn chỉnh — Mini Logger
    
    
    LOG_LEVEL = "INFO"
    
    
    def create_logger(prefix):
    
        total = 0
    
        def log(message):
    
            nonlocal total
    
            total += 1
    
            print(f"[{LOG_LEVEL}] {prefix} #{total}: {message}")
    
        return log
    
    
    db_log = create_logger("Database")
    api_log = create_logger("API")
    
    db_log("Connected")
    db_log("Query executed")
    
    api_log("GET /users")
    api_log("POST /login")

Kết quả
    
    
    [INFO] Database #1: Connected
    [INFO] Database #2: Query executed
    [INFO] API #1: GET /users
    [INFO] API #2: POST /login

Phân tích theo LEGB khi gọi `db_log("Connected")`:

Biến| Tìm thấy ở đâu  
---|---  
`message`| Local  
`total`| Enclosing (`create_logger`)  
`prefix`| Enclosing (`create_logger`)  
`LOG_LEVEL`| Global  
`print`| Built-in  
  
Đây là một ví dụ điển hình cho việc cả bốn mức của LEGB cùng được sử dụng trong một hàm.

* * *

# 18\. Debug Scope với `dis`

Python biên dịch mã khác nhau tùy theo phạm vi biến.
    
    
    import dis
    
    x = 10
    
    def outer():
        y = 20
    
        def inner():
            return x + y
    
        return inner
    
    dis.dis(outer())

Bạn sẽ thấy các lệnh như:
    
    
    LOAD_GLOBAL
    LOAD_DEREF

Ý nghĩa:

  * `LOAD_GLOBAL`: lấy biến từ Global. 
  * `LOAD_DEREF`: lấy biến từ Closure (Cell Object). 



Điều này cho thấy Python đã xác định phạm vi biến ngay từ khi biên dịch bytecode.

* * *

# Những lỗi phổ biến

### Sai 1: Quên `nonlocal`
    
    
    def outer():
        count = 0
    
        def inner():
            count += 1   # Lỗi

* * *

### Sai 2: Lạm dụng `global`
    
    
    count = 0
    
    def increase():
        global count

`global` làm tăng sự phụ thuộc vào trạng thái toàn cục. Trong các decorator, ưu tiên dùng `nonlocal` để giữ trạng thái cục bộ của từng decorator.

* * *

### Sai 3: Late Binding trong vòng lặp
    
    
    funcs = []
    
    for i in range(5):
        funcs.append(lambda: i)

Kết quả:
    
    
    4
    4
    4
    4
    4

Nên sửa bằng:
    
    
    funcs.append(lambda i=i: i)

hoặc dùng một factory function.

* * *

# Tổng kết buổi 4

Bạn cần nắm chắc các kiến thức sau:

  1. Python tìm biến theo quy tắc **LEGB** : 
     * **L** ocal 
     * **E** nclosing 
     * **G** lobal 
     * **B** uilt-in 
  2. `global` dùng để sửa biến ở phạm vi module. 
  3. `nonlocal` dùng để sửa biến ở hàm bao ngoài (Enclosing Scope). 
  4. Shadowing xảy ra khi biến cục bộ che khuất biến cùng tên ở phạm vi lớn hơn. 
  5. **Late Binding** là lỗi rất phổ biến khi tạo Closure trong vòng lặp. 
  6. Decorator hoạt động ổn định nhờ hiểu đúng LEGB, Closure và `nonlocal`. 



* * *

# Bài tập

## Bài 1

Viết chương trình minh họa đầy đủ cả 4 mức của LEGB trong một ví dụ duy nhất và giải thích Python lấy từng biến từ đâu.

* * *

## Bài 2

Viết một `make_average()`:
    
    
    avg = make_average()
    
    print(avg(10))
    print(avg(20))
    print(avg(30))

Kết quả:
    
    
    10.0
    15.0
    20.0

Gợi ý: dùng `nonlocal` để lưu tổng và số lượng phần tử.

* * *

## Bài 3

Tạo danh sách gồm 10 hàm, mỗi hàm trả về bình phương của chỉ số khi được gọi:
    
    
    funcs = ...
    
    print(funcs[0]())   # 0
    print(funcs[3]())   # 9
    print(funcs[9]())   # 81

Hãy triển khai theo **hai cách** :

  1. Dùng tham số mặc định (`i=i`) để tránh Late Binding. 
  2. Dùng Factory Function. 



* * *

## Chuẩn bị cho buổi 5

Ở **buổi 5** , chúng ta sẽ học **Nested Function (Hàm lồng nhau)** một cách chuyên sâu. Mặc dù đã sử dụng nested function ở các buổi trước, buổi học tới sẽ tập trung vào cách tổ chức mã nguồn bằng hàm lồng nhau, các mẫu thiết kế phổ biến (factory, helper, encapsulation), và cách chúng trở thành khung xương của mọi decorator trong Python. Sau buổi đó, chúng ta sẽ bắt đầu xây dựng **decorator đầu tiên** từ đầu.

