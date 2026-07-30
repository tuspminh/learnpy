Version:0.9 StartHTML:0000000105 EndHTML:0000024853 StartFragment:0000000141 EndFragment:0000024817 

# Typing Deep Dive – Buổi 1

# Giới thiệu Type Hint và tư duy về hệ thống kiểu (Type System)

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ hiểu:
> 
>   * Python là ngôn ngữ kiểu động (Dynamic Typing) nghĩa là gì.
>   * Type Hint là gì và **không phải là gì**.
>   * Tại sao Python bổ sung module `typing`.
>   * IDE và `mypy` sử dụng Type Hint như thế nào.
>   * Sự khác nhau giữa Dynamic Typing, Static Typing, Duck Typing và Gradual Typing.
>   * Khi nào nên dùng Type Hint trong dự án thực tế.
> 


* * *

# 1\. Python là ngôn ngữ Dynamic Typing

Trước tiên cần hiểu một điều:

> **Python luôn là Dynamic Typed Language.**

Không phải từ Python 3.5 có type hint thì Python biến thành Java.

Ví dụ
    
    
    x = 10
    
    print(type(x))
    
    
    <class 'int'>

Sau đó
    
    
    x = "Hello"
    
    print(type(x))
    
    
    <class 'str'>

Biến `x` ban đầu là `int`.

Sau đó lại là `str`.

Python hoàn toàn chấp nhận.

Đó gọi là

> Runtime quyết định kiểu dữ liệu.

* * *

## Ví dụ
    
    
    value = 100
    
    value = 3.14
    
    value = [1, 2, 3]
    
    value = {
        "name": "Alice"
    }

Biến `value` đổi kiểu liên tục.

Python không báo lỗi.

* * *

# 2\. Dynamic Typing là gì?

Nhiều người hiểu sai.

Không phải:

> "Biến không có kiểu."

Thực tế là:

> **Biến không có kiểu cố định.**

Đối tượng (Object) mới có kiểu.

Ví dụ
    
    
    x = 10

Bộ nhớ
    
    
    x
     │
     ▼
    +------+
    |  10  |
    +------+
     type=int

Sau đó
    
    
    x = "Python"
    
    
    x
     │
     ▼
    +-----------+
    | "Python"  |
    +-----------+
     type=str

Không phải object đổi kiểu.

Mà biến `x` trỏ sang object khác.

Đây là khái niệm cực kỳ quan trọng.

* * *

# 3\. Python có phải Weak Type không?

Không.

Python là

> Strongly Typed

Ví dụ
    
    
    10 + "20"

Kết quả
    
    
    TypeError

Python không tự ép kiểu.

Trong JavaScript
    
    
    10 + "20"

Kết quả
    
    
    "1020"

Python nghiêm ngặt hơn nhiều.

* * *

# 4\. Type Hint ra đời vì sao?

Trước Python 3.5

Code như sau
    
    
    def add(a, b):
        return a + b

Không ai biết

  * a là gì?
  * b là gì?
  * return là gì?



Có thể
    
    
    int
    
    float
    
    Decimal
    
    str
    
    list

Đều được.

Đọc code rất mệt.

* * *

Từ Python 3.5

PEP 484

Python bổ sung

Type Hint

Ví dụ
    
    
    def add(a: int, b: int) -> int:
        return a + b

Bây giờ IDE biết
    
    
    a : int
    
    b : int
    
    return : int

Đọc code dễ hơn nhiều.

* * *

# 5\. Type Hint KHÔNG kiểm tra kiểu khi chạy

Đây là điều quan trọng nhất của buổi hôm nay.

Ví dụ
    
    
    def add(a: int, b: int) -> int:
        return a + b

Gọi
    
    
    print(add("Hello", "World"))

Kết quả
    
    
    HelloWorld

Không có lỗi.

Python bỏ qua Type Hint khi thực thi.

* * *

Ví dụ khác
    
    
    def square(x: int) -> int:
        return x * x

Gọi
    
    
    square("abc")

Kết quả
    
    
    abcabcabc

Không lỗi.

Vì
    
    
    "abc" * 3

là hợp lệ.

* * *

# 6\. Vậy Type Hint dùng để làm gì?

Để

  * IDE
  * mypy
  * pyright
  * pylance
  * pyre



phân tích code.

Ví dụ
    
    
    def add(a: int, b: int) -> int:
        return a + b
    
    add("A", "B")

IDE sẽ gạch vàng hoặc đỏ:
    
    
    Expected int
    Got str

Python vẫn chạy.

Nhưng IDE cảnh báo.

* * *

# 7\. mypy hoạt động thế nào?

Giả sử file
    
    
    main.py
    
    
    def add(a: int, b: int) -> int:
        return a + b
    
    add("A", "B")

Chạy
    
    
    mypy main.py

Kết quả
    
    
    Argument 1 has incompatible type "str"
    
    Argument 2 has incompatible type "str"

Không cần chạy chương trình.

Đó gọi là

Static Analysis.

* * *

# 8\. Runtime và Static Analysis

Runtime
    
    
    Python Interpreter

Static Analysis
    
    
    mypy
    
    pyright
    
    Pylance
    
    PyCharm

Hai thứ hoàn toàn độc lập.
    
    
            Source Code
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
    Python Runtime     mypy
        │                 │
     chạy chương trình   kiểm tra kiểu

* * *

# 9\. IDE sử dụng Type Hint

Ví dụ
    
    
    name: str = "Alice"
    
    print(name.upper())

IDE biết
    
    
    name
    
    ↓
    
    str

Nên gợi ý
    
    
    upper()
    
    lower()
    
    split()
    
    replace()

Nếu
    
    
    age: int = 18

IDE gợi ý
    
    
    bit_length()
    
    to_bytes()
    
    ...

Đó là lợi ích cực lớn của Type Hint.

* * *

# 10\. Type Hint không làm chương trình chạy nhanh hơn

Sai lầm phổ biến:

> Có Type Hint sẽ chạy nhanh hơn.

Sai.

Ví dụ
    
    
    def add(a: int, b: int) -> int:
        return a + b

và
    
    
    def add(a, b):
        return a + b

Tốc độ gần như giống hệt nhau.

Interpreter bỏ qua annotation khi thực thi.

* * *

# 11\. Duck Typing

Python rất nổi tiếng với Duck Typing.

Triết lý:

> Nếu nó hành xử như con vịt thì cứ coi nó là vịt.

Ví dụ
    
    
    class Dog:
        def speak(self):
            print("Woof")
    
    
    class Cat:
        def speak(self):
            print("Meow")
    
    
    def talk(animal):
        animal.speak()

Có thể gọi
    
    
    talk(Dog())
    talk(Cat())

Không cần
    
    
    Animal
    
    Interface
    
    Abstract Class

Miễn có phương thức `speak()`.

Đó là Duck Typing.

* * *

# 12\. Gradual Typing

Python không ép bạn phải viết type.

Có thể
    
    
    def hello(name):
        return name

Hoặc
    
    
    def hello(name: str) -> str:
        return name

Hoặc
    
    
    def hello(name: str | None) -> str:
        ...

Hoặc
    
    
    from typing import Any
    
    def hello(name: Any):
        ...

Bạn có thể thêm type dần dần.

Đó là **Gradual Typing**.

* * *

# 13\. Dynamic Typing vs Static Typing vs Duck Typing vs Gradual Typing

Khái niệm| Ý nghĩa  
---|---  
Dynamic Typing| Kiểu được xác định khi chạy (runtime). Biến có thể tham chiếu đến đối tượng của nhiều kiểu khác nhau theo thời gian.  
Static Typing| Trình kiểm tra kiểu phân tích mã trước khi chạy để phát hiện lỗi kiểu.  
Duck Typing| Quan tâm đối tượng làm được gì (có phương thức/phép toán phù hợp), không cần quan tâm nó thuộc lớp nào.  
Gradual Typing| Có thể thêm hoặc bỏ type hint từng phần; không bắt buộc toàn bộ chương trình phải được chú thích kiểu.  
  
* * *

# 14\. Best Practice

✔ Luôn viết type cho hàm công khai (public API).
    
    
    def calculate_total(price: float, quantity: int) -> float:
        return price * quantity

✔ Luôn khai báo kiểu trả về.
    
    
    def load_user(user_id: int) -> dict:
        ...

✔ Dùng `mypy` hoặc `pyright` trong các dự án lớn để phát hiện lỗi sớm.

❌ Không thêm type chỉ để "cho có". Nếu chưa biết kiểu chính xác, các buổi sau sẽ học cách mô tả bằng `Protocol`, `Generic`, `TypeVar`, `TypedDict`,... thay vì lạm dụng `Any`.

* * *

# Bài tập thực hành

## Bài 1

Viết các hàm sau có đầy đủ type hint:

  * `subtract(a, b)`
  * `multiply(a, b)`
  * `divide(a, b)`



Tất cả nhận vào hai số thực (`float`) và trả về `float`.

* * *

## Bài 2

Tạo hàm:
    
    
    def greet(name):
        return f"Hello {name}"

Sau đó:

  1. Thêm type hint.
  2. Gọi hàm với:
     * `"Alice"`
     * `123`
  3. Quan sát:
     * Chương trình có chạy không?
     * IDE hoặc `mypy` có cảnh báo gì?



* * *

## Bài 3

Tạo hai lớp:
    
    
    class Bird:
        def speak(self):
            print("Chirp")
    
    
    class Robot:
        def speak(self):
            print("Beep")

Viết hàm:
    
    
    def talk(obj):
        obj.speak()

Gọi:
    
    
    talk(Bird())
    talk(Robot())

Hãy giải thích tại sao đây là một ví dụ điển hình của **Duck Typing**.

* * *

Ở **Buổi 2** , chúng ta sẽ đi sâu vào **các kiểu dữ liệu trong**`**typing**` (`list[int]`, `dict[str, int]`, `tuple`, `set`, `Sequence`, `Mapping`...), đồng thời phân tích khi nào nên dùng kiểu cụ thể (`list`) và khi nào nên dùng kiểu trừu tượng (`Sequence`) để thiết kế API linh hoạt hơn.

