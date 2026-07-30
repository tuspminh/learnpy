# Context Manager Deep Dive – Buổi 3

# Cơ chế hoạt động của `with` và luồng điều khiển

Ở **buổi 2** , chúng ta đã biết:

  * `__enter__()`
  * `__exit__()`
  * Context Manager Protocol 



Hôm nay chúng ta sẽ học điều mà rất ít lập trình viên Python hiểu rõ:

> **Python thực sự làm gì khi gặp câu lệnh`with`?**

Đây là kiến thức quan trọng nếu sau này bạn muốn viết framework, ORM, transaction manager hoặc các thư viện chuyên nghiệp.

* * *

# Mục tiêu

Sau buổi này bạn sẽ:

  * Hiểu luồng thực thi của `with`
  * Biết khi nào `__exit__()` được gọi 
  * Hiểu cách ngoại lệ được truyền vào `__exit__()`
  * Hiểu ý nghĩa của giá trị trả về `True` và `False`
  * Biết `return`, `break`, `continue` ảnh hưởng thế nào đến Context Manager 



* * *

# 1\. `with` không phải là "phép màu"

Ví dụ:
    
    
    with open("data.txt") as f:
        print(f.read())

Nhiều người nghĩ Python có câu lệnh đặc biệt.

Thực ra không.

Python chỉ biến nó thành logic tương đương:
    
    
    ctx = open("data.txt")
    
    value = ctx.__enter__()
    
    try:
        f = value
        print(f.read())
    
    except Exception as e:
        ctx.__exit__(type(e), e, e.__traceback__)
        raise
    
    else:
        ctx.__exit__(None, None, None)

Lưu ý: Đây là **mô phỏng** để hiểu cơ chế. Việc triển khai thực tế trong CPython có thêm các bước xử lý chi tiết.

* * *

# 2\. Luồng thực thi

Ví dụ
    
    
    class Demo:
    
        def __enter__(self):
            print("ENTER")
            return self
    
        def __exit__(self, *args):
            print("EXIT")
    
    
    with Demo():
        print("A")
        print("B")

Thứ tự
    
    
    Tạo object
    
    ↓
    
    __enter__()
    
    ↓
    
    A
    
    ↓
    
    B
    
    ↓
    
    __exit__()

Output
    
    
    ENTER
    A
    B
    EXIT

* * *

# 3\. Nếu có Exception
    
    
    class Demo:
    
        def __enter__(self):
            print("ENTER")
            return self
    
        def __exit__(self, exc_type, exc, tb):
            print("EXIT")
            print(exc_type)
    
    
    with Demo():
        print("Start")
        1 / 0

Output
    
    
    ENTER
    
    Start
    
    EXIT
    
    <class 'ZeroDivisionError'>
    
    Traceback...

Quan sát
    
    
    Exception
    
    ↓
    
    __exit__()
    
    ↓
    
    Exception tiếp tục được ném ra

Điều này cho thấy `__exit__` **không tự động xử lý** ngoại lệ.

* * *

# 4\. `__exit__` trả về gì?

Đây là điểm quan trọng nhất.

Giả sử
    
    
    def __exit__(...):
        return False

hoặc
    
    
    return None

Kết quả
    
    
    Exception
    
    ↓
    
    được ném tiếp

* * *

Nếu
    
    
    return True

thì sao?

Python hiểu rằng

> "Exception đã được xử lý."

Nó sẽ **không ném ngoại lệ ra ngoài nữa**.

* * *

# 5\. Ví dụ
    
    
    class Demo:
    
        def __enter__(self):
            print("Open")
            return self
    
        def __exit__(self, exc_type, exc, tb):
            print("Close")
            return True
    
    
    with Demo():
        1 / 0
    
    print("Program continues")

Output
    
    
    Open
    
    Close
    
    Program continues

Không có traceback.

* * *

# 6\. Nếu trả về False
    
    
    class Demo:
    
        def __enter__(self):
            return self
    
        def __exit__(self, *args):
            return False
    
    
    with Demo():
        1 / 0

Output
    
    
    ZeroDivisionError

Lỗi vẫn xảy ra.

* * *

# 7\. Tại sao cần `True`?

Ví dụ

Bạn muốn ghi log lỗi nhưng chương trình vẫn tiếp tục.
    
    
    class IgnoreError:
    
        def __enter__(self):
            return self
    
        def __exit__(self, exc_type, exc, tb):
    
            if exc_type:
    
                print("Log:", exc)
    
                return True

Sử dụng
    
    
    with IgnoreError():
        int("abc")
    
    print("Still running")

Output
    
    
    Log: invalid literal...
    
    Still running

Đây là cơ chế mà một số Context Manager trong thư viện chuẩn sử dụng.

* * *

# 8\. `return` trong block `with`

Ví dụ
    
    
    class Demo:
    
        def __enter__(self):
            print("Enter")
            return self
    
        def __exit__(self, *args):
            print("Exit")
    
    
    def test():
    
        with Demo():
    
            return 100

Khi gọi
    
    
    print(test())

Output
    
    
    Enter
    
    Exit
    
    100

Quan trọng
    
    
    return
    
    ↓
    
    __exit__()
    
    ↓
    
    thực sự return

Python luôn cleanup trước.

* * *

# 9\. `break`
    
    
    with Demo():
    
        for i in range(10):
    
            break

Output
    
    
    Enter
    
    Exit

* * *

# 10\. `continue`
    
    
    for i in range(3):
    
        with Demo():
    
            continue

Output
    
    
    Enter
    Exit
    
    Enter
    Exit
    
    Enter
    Exit

* * *

# 11\. `raise`
    
    
    with Demo():
    
        raise RuntimeError()

Output
    
    
    Enter
    
    Exit
    
    RuntimeError

* * *

# 12\. Thứ tự đầy đủ
    
    
    Create object
    
    ↓
    
    __enter__()
    
    ↓
    
    Block
    
    ↓
    
    (return)
    
    ↓
    
    break
    
    ↓
    
    continue
    
    ↓
    
    raise
    
    ↓
    
    Exception
    
    ↓
    
    __exit__()
    
    ↓
    
    Rời Context

Điều quan trọng là **mọi đường đi ra khỏi khối`with` đều phải đi qua `__exit__`**.

* * *

# 13\. Nhiều Context Manager
    
    
    with A(), B():
        ...

Python xử lý gần giống
    
    
    with A():
    
        with B():
    
            ...

* * *

Ví dụ
    
    
    class A:
    
        def __enter__(self):
            print("Enter A")
    
        def __exit__(self, *args):
            print("Exit A")
    
    
    class B:
    
        def __enter__(self):
            print("Enter B")
    
        def __exit__(self, *args):
            print("Exit B")
    
    
    with A(), B():
        print("Work")

Output
    
    
    Enter A
    
    Enter B
    
    Work
    
    Exit B
    
    Exit A

Đây là nguyên tắc **LIFO (Last In, First Out)**.

* * *

# 14\. Điều gì xảy ra nếu `__enter__` thất bại?
    
    
    class Demo:
    
        def __enter__(self):
    
            print("Opening")
    
            raise RuntimeError("Cannot open")
    
        def __exit__(self, *args):
    
            print("Closing")
    
    
    with Demo():
        pass

Output
    
    
    Opening
    
    RuntimeError

Quan sát
    
    
    __exit__()
    
    KHÔNG được gọi.

Vì context chưa được thiết lập thành công.

Đây là lý do `__enter__` nên:

  * chỉ thực hiện phần khởi tạo cần thiết, 
  * và nếu cấp phát nhiều tài nguyên, phải tự dọn dẹp những gì đã cấp phát trước khi ném ngoại lệ. 



* * *

# 15\. Nếu `__exit__` cũng gây lỗi
    
    
    class Demo:
    
        def __enter__(self):
            return self
    
        def __exit__(self, *args):
            raise RuntimeError("Exit failed")
    
    
    with Demo():
        print("Hello")

Output
    
    
    Hello
    
    RuntimeError: Exit failed

Nếu khối `with` cũng phát sinh ngoại lệ và `__exit__` lại ném một ngoại lệ khác, thì ngoại lệ từ `__exit__` sẽ được lan truyền, còn ngoại lệ ban đầu được lưu trong ngữ cảnh (`__context__`). Đây là tình huống cần tránh trong các Context Manager thực tế.

* * *

# 16\. Sơ đồ tổng quát
    
    
    Create Context
    
    ↓
    
    __enter__()
    
    ↓
    
    Block
    
    ↓
    
    Có Exception?
    
    ↓
    
    YES ------------------- NO
    
    ↓                      ↓
    
    __exit__(exc)      __exit__(None)
    
    ↓
    
    Return True?
    
    ↓
    
    YES -------- NO
    
    ↓            ↓
    
    Ignore      Raise
    Exception   Exception

* * *

# Tổng kết

Tình huống| `__exit__()` có được gọi?  
---|---  
Kết thúc bình thường| ✅  
`return`| ✅  
`break`| ✅  
`continue`| ✅  
Exception trong block| ✅  
`__enter__` thất bại| ❌  
  
`__exit__` trả về| Kết quả  
---|---  
`True`| Chặn ngoại lệ  
`False` hoặc `None`| Ngoại lệ tiếp tục lan truyền  
  
* * *

# Bài tập thực hành

## Bài 1

Viết `IgnoreZeroDivision`:

  * `__enter__` trả về `self`. 
  * Nếu gặp `ZeroDivisionError`, in `"Ignored ZeroDivisionError"` và trả về `True`. 
  * Với các ngoại lệ khác, trả về `False`. 



Kiểm tra:
    
    
    with IgnoreZeroDivision():
        1 / 0
    
    print("Done")

* * *

## Bài 2

Viết `LoggerContext`:

  * `__enter__`: in `"Start"`. 
  * `__exit__`: 
    * nếu không có lỗi: in `"Success"`; 
    * nếu có lỗi: in tên loại ngoại lệ và thông báo lỗi. 



Ví dụ:
    
    
    with LoggerContext():
        raise ValueError("Invalid value")

* * *

## Bài 3

Tạo hai Context Manager:

  * `Outer`
  * `Inner`



Mỗi lớp in `"Enter ..."` trong `__enter__` và `"Exit ..."` trong `__exit__`.

Thử:
    
    
    with Outer(), Inner():
        print("Working")

Quan sát thứ tự vào và ra để kiểm chứng nguyên tắc **LIFO**.

* * *

## Bài 4

Viết hàm:
    
    
    def calculate():
        with LoggerContext():
            return 42

Xác minh rằng `"Success"` được in trước khi hàm thực sự trả về `42`.

* * *

# Chuẩn bị cho buổi 4

Ở buổi tiếp theo, chúng ta sẽ chuyển từ lý thuyết sang **ứng dụng thực tế** :

  * Quản lý **file** an toàn. 
  * Quản lý **socket**. 
  * Quản lý **SQLite transaction** bằng Context Manager. 
  * Thiết kế Context Manager cho **lock** , **temporary directory** , và các tài nguyên thường gặp trong các dự án Python chuyên nghiệp. 



Đây là buổi giúp bạn thấy Context Manager được sử dụng như thế nào trong các thư viện chuẩn và trong các hệ thống thực tế.

