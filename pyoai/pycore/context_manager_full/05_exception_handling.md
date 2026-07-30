# Context Manager Deep Dive – Buổi 5

# Exception Handling trong Context Manager

> Đây là một trong những buổi quan trọng nhất của toàn bộ khóa học.

Từ buổi này trở đi, chúng ta sẽ học cách xây dựng Context Manager **đủ an toàn để sử dụng trong các dự án thực tế**.

Nhiều lập trình viên biết viết `__enter__()` và `__exit__()`, nhưng lại **không hiểu cách xử lý ngoại lệ đúng cách** , dẫn đến:

  * Che giấu bug. 
  * Làm mất traceback. 
  * Rollback không đúng. 
  * Ghi log thiếu thông tin. 



* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Ba tham số của `__exit__`
  * Khi nào `__exit__` được gọi 
  * Khi nào nên `return True`
  * Khi nào phải `return False`
  * Cách ghi log exception 
  * Cách rollback transaction 
  * Best Practices 



* * *

# 1\. Chữ ký của `__exit__`
    
    
    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):
        ...

Ba tham số này chỉ có giá trị khi **khối`with` phát sinh ngoại lệ**.

Nếu không có lỗi:
    
    
    exc_type = None
    exc_value = None
    traceback = None

* * *

# 2\. Ví dụ đơn giản
    
    
    class Demo:
    
        def __enter__(self):
            return self
    
        def __exit__(self, exc_type, exc_value, tb):
    
            print("TYPE :", exc_type)
            print("VALUE:", exc_value)
            print("TB   :", tb)

* * *

Không có lỗi
    
    
    with Demo():
        print("Hello")

Output
    
    
    TYPE : None
    VALUE: None
    TB   : None

* * *

Có lỗi
    
    
    with Demo():
        1 / 0

Ví dụ output:
    
    
    TYPE :
    <class 'ZeroDivisionError'>
    
    VALUE:
    division by zero
    
    TB:
    <traceback object at ...>

* * *

# 3\. `exc_type`

Là **class** của ngoại lệ.

Ví dụ
    
    
    ZeroDivisionError
    
    ValueError
    
    FileNotFoundError
    
    KeyError

Bạn có thể kiểm tra:
    
    
    if exc_type is ZeroDivisionError:
        ...

Hoặc:
    
    
    if issubclass(exc_type, ArithmeticError):
        ...

> **Lưu ý:** Hãy kiểm tra `exc_type is not None` trước khi gọi `issubclass`, vì khi không có ngoại lệ thì `exc_type` là `None`.

* * *

# 4\. `exc_value`

Đây là **instance** của exception.

Ví dụ
    
    
    raise ValueError("Age must be positive")

Thì
    
    
    exc_type

là
    
    
    ValueError

Còn
    
    
    exc_value

là
    
    
    ValueError("Age must be positive")

Ta có thể:
    
    
    print(exc_value)

Kết quả
    
    
    Age must be positive

* * *

# 5\. `traceback`

Đây là object chứa stack trace.

Ví dụ
    
    
    import traceback
    
    class Demo:
    
        def __enter__(self):
            return self
    
        def __exit__(self,
                     exc_type,
                     exc_value,
                     tb):
    
            if exc_type:
    
                traceback.print_tb(tb)

Nếu
    
    
    with Demo():
        1 / 0

Sẽ in vị trí gây lỗi.

* * *

# 6\. Ghi log Exception

Ví dụ
    
    
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    class Logger:
    
        def __enter__(self):
            return self
    
        def __exit__(self,
                     exc_type,
                     exc_value,
                     tb):
    
            if exc_type:
    
                logging.exception(
                    "Error inside context",
                    exc_info=(exc_type, exc_value, tb)
                )

Sử dụng
    
    
    with Logger():
    
        int("abc")

Log sẽ chứa:

  * loại lỗi 
  * message 
  * traceback 



Đây là cách phổ biến trong các ứng dụng thực tế.

* * *

# 7\. Chỉ bắt một loại Exception

Không nên
    
    
    return True

cho mọi lỗi.

Ví dụ
    
    
    class IgnoreZero:
    
        def __enter__(self):
            return self
    
        def __exit__(self,
                     exc_type,
                     exc,
                     tb):
    
            if exc_type is ZeroDivisionError:
    
                print("Ignored")
    
                return True
    
            return False

Thử
    
    
    with IgnoreZero():
        1 / 0

Output
    
    
    Ignored

Không crash.

* * *

Nếu
    
    
    with IgnoreZero():
        int("abc")

Output
    
    
    ValueError

Lỗi vẫn được ném ra.

Đây là cách làm đúng.

* * *

# 8\. Rollback Transaction

Ví dụ
    
    
    class Transaction:
    
        def __enter__(self):
    
            print("BEGIN")
    
            return self
    
        def commit(self):
    
            print("COMMIT")
    
        def rollback(self):
    
            print("ROLLBACK")
    
        def __exit__(self,
                     exc_type,
                     exc,
                     tb):
    
            if exc_type:
    
                self.rollback()
    
            else:
    
                self.commit()
    
            return False

* * *

Không lỗi
    
    
    with Transaction():
    
        print("UPDATE")

Output
    
    
    BEGIN
    
    UPDATE
    
    COMMIT

* * *

Có lỗi
    
    
    with Transaction():
    
        raise RuntimeError()

Output
    
    
    BEGIN
    
    ROLLBACK
    
    RuntimeError

Đây là mẫu thiết kế được dùng trong rất nhiều ORM.

* * *

# 9\. Không được che giấu Bug

Sai
    
    
    class Bad:
    
        def __enter__(self):
            return self
    
        def __exit__(self, *args):
    
            return True

Điều này sẽ nuốt mọi lỗi.
    
    
    with Bad():
    
        x = 1 / 0
    
    print("Done")

Output
    
    
    Done

Bug biến mất.

Rất nguy hiểm.

* * *

# 10\. Chỉ xử lý những gì mình hiểu

Ví dụ
    
    
    class IgnoreFile:
    
        def __enter__(self):
            return self
    
        def __exit__(self,
                     exc_type,
                     exc,
                     tb):
    
            if exc_type is FileNotFoundError:
    
                print("Missing file")
    
                return True
    
            return False

Đây là cách làm tốt.

* * *

# 11\. Có thể chuyển đổi Exception

Ví dụ
    
    
    class Convert:
    
        def __enter__(self):
            return self
    
        def __exit__(self,
                     exc_type,
                     exc,
                     tb):
    
            if exc_type is KeyError:
    
                raise ValueError(
                    "Invalid configuration"
                )

Thử
    
    
    with Convert():
    
        raise KeyError("username")

Kết quả
    
    
    ValueError
    
    Invalid configuration

Đây là kỹ thuật "exception translation", giúp API bên ngoài nhất quán hơn.

* * *

# 12\. Ghi thời gian khi có lỗi
    
    
    from datetime import datetime
    
    class Logger:
    
        def __enter__(self):
    
            self.start = datetime.now()
    
            return self
    
        def __exit__(self,
                     exc_type,
                     exc,
                     tb):
    
            if exc_type:
    
                print(datetime.now())
    
                print(exc)

Có thể mở rộng để:

  * ghi vào file 
  * gửi log server 
  * gửi Slack 
  * gửi Telegram 
  * gửi email 



* * *

# 13\. Retry không nên đặt trong `__exit__`

Nhiều người nghĩ:
    
    
    def __exit__(...):
    
        retry()

Đây thường **không phải** là nơi phù hợp.

Lý do:

  * Khối `with` đã thực thi xong. 
  * Python không thể "quay lại" chạy lại toàn bộ khối `with`. 



Retry nên được đặt ở:

  * decorator 
  * vòng lặp 
  * lớp quản lý retry riêng 



Ví dụ:
    
    
    for _ in range(3):
        try:
            with Transaction():
                update_database()
            break
        except ConnectionError:
            continue

* * *

# 14\. Best Practices

## Luôn trả về `False`

Trừ khi thực sự muốn chặn exception.
    
    
    return False

Hoặc
    
    
    return None

* * *

## Ghi log đầy đủ
    
    
    logging.exception(
        "...",
        exc_info=(...)
    )

* * *

## Rollback khi có lỗi
    
    
    if exc_type:
    
        rollback()

* * *

## Commit khi thành công
    
    
    else:
    
        commit()

* * *

## Không nuốt mọi exception

Sai
    
    
    return True

Đúng
    
    
    if exc_type is FileNotFoundError:
    
        return True
    
    return False

* * *

# Ví dụ hoàn chỉnh
    
    
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    class SafeTransaction:
    
        def __enter__(self):
    
            print("BEGIN")
    
            return self
    
        def __exit__(
            self,
            exc_type,
            exc_value,
            tb
        ):
    
            if exc_type:
    
                print("ROLLBACK")
    
                logging.exception(
                    "Transaction failed",
                    exc_info=(
                        exc_type,
                        exc_value,
                        tb
                    )
                )
    
                return False
    
            print("COMMIT")

Sử dụng
    
    
    with SafeTransaction():
    
        print("Updating user")

Hoặc
    
    
    with SafeTransaction():
    
        raise ValueError("Bad data")

* * *

# Tổng kết

`exc_type`| Ý nghĩa  
---|---  
`None`| Không có ngoại lệ  
`ZeroDivisionError`| Chia cho 0  
`ValueError`| Giá trị không hợp lệ  
`KeyError`| Thiếu khóa  
`FileNotFoundError`| Thiếu file  
  
Giá trị trả về của `__exit__`| Kết quả  
---|---  
`True`| Chặn ngoại lệ  
`False`| Ngoại lệ tiếp tục lan truyền  
`None`| Tương đương `False`  
  
* * *

# Bài tập

## Bài 1

Viết `IgnoreValueError`

Yêu cầu:

  * Chỉ bỏ qua `ValueError`
  * Các lỗi khác phải tiếp tục được ném ra 



* * *

## Bài 2

Viết `TransactionLogger`

Yêu cầu:

  * `BEGIN`
  * `COMMIT` nếu thành công 
  * `ROLLBACK` nếu có lỗi 
  * Ghi log đầy đủ bằng `logging.exception`



* * *

## Bài 3

Viết `TimerLogger`

Yêu cầu:

  * Đo thời gian thực thi 
  * Nếu có lỗi, in: 
    * Loại ngoại lệ 
    * Thời gian đã chạy trước khi lỗi xảy ra 



* * *

## Bài 4

Viết `ConfigLoader`

Yêu cầu:

  * Trong `__exit__`, nếu gặp `KeyError`, chuyển thành: 


    
    
    ValueError("Configuration is invalid")

Để người dùng API chỉ cần xử lý một loại ngoại lệ thống nhất.

* * *

# Chuẩn bị cho buổi 6

Buổi 6 là bước chuyển từ **người sử dụng** sang **người thiết kế** Context Manager.

Chúng ta sẽ học cách xây dựng các Context Manager hoàn chỉnh theo phong cách thư viện chuyên nghiệp, bao gồm:

  * Thiết kế lớp quản lý tài nguyên thực tế. 
  * Quản lý nhiều tài nguyên trong một Context Manager. 
  * Đảm bảo an toàn khi `__enter__` hoặc `__exit__` gặp lỗi. 
  * Áp dụng các nguyên tắc thiết kế để Context Manager có thể tái sử dụng và mở rộng trong các dự án lớn. Đây là nền tảng trước khi chuyển sang `contextlib` và các Context Manager dạng generator ở các buổi tiếp theo.

