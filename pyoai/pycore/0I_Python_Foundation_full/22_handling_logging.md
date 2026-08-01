# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 22: Exception Handling & Logging (Phần 1) - Xử lý ngoại lệ từ cơ bản đến chuyên nghiệp

> **Đây là một trong những kỹ năng quan trọng nhất của lập trình viên Python chuyên nghiệp.**
>
> Một chương trình tốt không phải là chương trình **không bao giờ lỗi**, mà là chương trình **biết xử lý lỗi một cách đúng đắn**.

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu Exception là gì.
* Phân biệt Syntax Error, Runtime Error và Logic Error.
* Thành thạo `try`, `except`, `else`, `finally`.
* Biết bắt nhiều loại Exception.
* Hiểu cách hoạt động của Exception Propagation.
* Biết khi nào nên và không nên bắt Exception.
* Viết chương trình CLI an toàn hơn.

---

# 1. Chương trình luôn có thể gặp lỗi

Ví dụ:

```python
number = int(input("Nhập số: "))

print(100 / number)
```

Nếu người dùng nhập:

```
abc
```

↓

```
ValueError
```

Nếu nhập:

```
0
```

↓

```
ZeroDivisionError
```

Nếu chương trình không xử lý lỗi:

```
Program Crashed
```

---

# 2. Ba loại lỗi trong Python

## Syntax Error

Sai cú pháp.

```python
if True
    print("Hello")
```

Kết quả:

```
SyntaxError
```

Python **không chạy được chương trình**.

---

## Runtime Error (Exception)

Ví dụ:

```python
10 / 0
```

↓

```
ZeroDivisionError
```

Chương trình đang chạy mới phát hiện.

---

## Logic Error

Nguy hiểm nhất.

Ví dụ:

```python
price = 100

discount = 20

total = price + discount
```

Không có Exception.

Nhưng kết quả sai.

Đúng phải là:

```python
total = price - discount
```

Logic Error thường khó phát hiện hơn cả Runtime Error.

---

# 3. Exception là gì?

Exception là một **đối tượng (Object)** biểu diễn lỗi xảy ra trong quá trình chạy chương trình.

Ví dụ:

```python
ZeroDivisionError

ValueError

TypeError

FileNotFoundError
```

Đều là các lớp (Class) kế thừa từ:

```text
BaseException
    └── Exception
         ├── ValueError
         ├── TypeError
         ├── RuntimeError
         ├── FileNotFoundError
         └── ...
```

---

# 4. `try` và `except`

Ví dụ:

```python
try:
    number = int(input("Nhập số: "))
    print(100 / number)

except:
    print("Đã xảy ra lỗi.")
```

Nếu nhập:

```
abc
```

↓

```
Đã xảy ra lỗi.
```

---

# 5. Không nên dùng `except` trống

Đây là cách viết **không được khuyến khích**:

```python
try:
    ...
except:
    print("Lỗi")
```

Vì nó bắt **mọi ngoại lệ**, kể cả những lỗi mà bạn không mong muốn.

Hãy bắt đúng loại lỗi.

---

# 6. Bắt từng Exception

```python
try:
    number = int(input())

    print(100 / number)

except ValueError:
    print("Bạn phải nhập số.")

except ZeroDivisionError:
    print("Không được chia cho 0.")
```

Ví dụ:

Nhập:

```
abc
```

↓

```
Bạn phải nhập số.
```

Nhập:

```
0
```

↓

```
Không được chia cho 0.
```

---

# 7. Một `except` cho nhiều Exception

```python
try:
    ...

except ValueError, ZeroDivisionError:
    print("Dữ liệu không hợp lệ.")
```

---

# 8. Lấy thông tin lỗi

```python
try:
    ...

except Exception as e:
    print(e)
```

Ví dụ:

```
division by zero
```

Hoặc:

```
invalid literal for int()
```

`e` là đối tượng Exception.

---

# 9. `else`

`else` chỉ chạy khi **không có Exception**.

```python
try:
    number = int(input())

except ValueError:
    print("Sai.")

else:
    print("Bạn nhập đúng.")
```

Nếu nhập:

```
10
```

↓

```
Bạn nhập đúng.
```

---

# 10. `finally`

`finally` **luôn luôn được thực thi**, dù có lỗi hay không.

```python
try:
    print("Mở file")

finally:
    print("Đóng file")
```

Kết quả:

```
Mở file

Đóng file
```

---

# 11. Ví dụ thực tế

```python
try:
    file = open("data.txt")

    ...

finally:
    file.close()
```

Dù đọc file có lỗi.

File vẫn được đóng.

(Trong Python hiện đại, ta thường dùng `with`, sẽ học ở buổi sau.)

---

# 12. Thứ tự thực thi

Ví dụ:

```python
try:
    ...

except:
    ...

else:
    ...

finally:
    ...
```

### Có Exception

```
try

↓

except

↓

finally
```

### Không Exception

```
try

↓

else

↓

finally
```

---

# 13. Exception Propagation

Ví dụ:

```python
def divide(a, b):
    return a / b


def calculate():
    return divide(10, 0)


calculate()
```

Lỗi phát sinh ở:

```python
divide()
```

Nhưng sẽ **lan truyền ngược lên** (`calculate()` rồi tới nơi gọi) cho đến khi gặp `except` hoặc kết thúc chương trình.

---

# 14. Bắt ở đâu?

Không nên:

```python
def divide():
    try:
        ...
    except:
        ...
```

mọi nơi.

Nên bắt ở nơi **biết cách xử lý**.

Ví dụ:

* Hàm tính toán: để Exception nổi lên.
* Giao diện CLI hoặc Web API: bắt Exception và hiển thị thông báo phù hợp.

---

# 15. Thứ tự các `except`

Sai:

```python
except Exception:

except ValueError:
```

`ValueError` sẽ **không bao giờ được chạy**.

Đúng:

```python
except ValueError:

except Exception:
```

Luôn bắt **cụ thể trước**, **tổng quát sau**.

---

# 16. Không lạm dụng Exception

Sai:

```python
try:
    my_list[100]
except:
    pass
```

Lỗi bị "nuốt mất".

Sau này rất khó debug.

---

# 17. Ví dụ CLI

```python
while True:
    try:
        age = int(input("Age: "))

        if age < 0:
            print("Tuổi không hợp lệ.")
            continue

        break

    except ValueError:
        print("Bạn phải nhập số.")
```

Đây là cách viết phổ biến cho ứng dụng dòng lệnh.

---

# 18. Ví dụ File

```python
try:
    with open("data.txt") as f:
        print(f.read())

except FileNotFoundError:
    print("Không tìm thấy file.")
```

Nếu file không tồn tại, chương trình vẫn chạy bình thường.

---

# 19. Ví dụ Network

```python
try:
    response = api_call()

except TimeoutError:
    print("Hết thời gian chờ.")

except ConnectionError:
    print("Không kết nối được.")
```

Mỗi loại lỗi được xử lý theo cách riêng.

---

# 20. Những lỗi phổ biến

## Lỗi 1

Bắt mọi Exception

```python
except:
```

Không nên.

---

## Lỗi 2

Dùng `pass`

```python
except:
    pass
```

Làm mất dấu lỗi.

---

## Lỗi 3

Không đọc thông báo Exception

```python
except Exception:
```

Thay vì:

```python
except Exception as e:
    print(e)
```

---

## Lỗi 4

Bắt Exception quá sớm

Hãy để Exception lan đến nơi có thể xử lý hợp lý.

---

# 21. Bài tập thực hành

## Bài 1

Viết chương trình:

* Nhập hai số.
* Chia hai số.
* Xử lý:

  * `ValueError`
  * `ZeroDivisionError`

---

## Bài 2

Viết chương trình:

* Nhập tuổi.
* Tuổi phải ≥ 0.
* Nếu sai thì yêu cầu nhập lại.

---

## Bài 3

Đọc file:

```
students.txt
```

Nếu file không tồn tại:

```
Thông báo lỗi.
```

---

## Bài 4

Viết hàm:

```python
safe_int(text)
```

Trả về:

* `int` nếu hợp lệ.
* `None` nếu không chuyển đổi được.

---

## Bài 5

Viết hàm:

```python
safe_divide(a, b)
```

Nếu lỗi:

Không làm chương trình dừng.

---

## Bài 6

Viết menu CLI:

```
1. Cộng

2. Trừ

3. Nhân

4. Chia

0. Thoát
```

Không để chương trình bị dừng khi người dùng nhập sai.

---

# Mini Project: Máy tính dòng lệnh an toàn

Xây dựng ứng dụng:

```
====================

Simple Calculator

====================

1. Add

2. Subtract

3. Multiply

4. Divide

0. Exit
```

Yêu cầu:

* Không crash khi nhập sai.
* Kiểm tra dữ liệu đầu vào.
* Xử lý chia cho 0.
* Cho phép tiếp tục sử dụng sau khi xảy ra lỗi.

**Mở rộng:**

* Lưu lịch sử phép tính vào danh sách.
* Thêm chức năng xem lại lịch sử.

---

# Tổng kết buổi 22

Hôm nay bạn đã học:

* ✅ Syntax Error.
* ✅ Runtime Error.
* ✅ Logic Error.
* ✅ `try`.
* ✅ `except`.
* ✅ `else`.
* ✅ `finally`.
* ✅ Bắt nhiều Exception.
* ✅ `Exception as e`.
* ✅ Exception Propagation.
* ✅ Thực hành xử lý lỗi trong CLI và thao tác file.

---

# Góc lập trình viên chuyên nghiệp

Trong các dự án Python lớn như **Django**, **FastAPI**, **PySide6**, **Scrapy**, hay các ứng dụng AI:

* **Không bao giờ** dùng `except:` trống trừ khi có lý do rất đặc biệt.
* Chỉ bắt những ngoại lệ mà chương trình **thực sự biết cách xử lý**.
* Ghi log đầy đủ thông tin lỗi thay vì im lặng bỏ qua.
* Tách riêng **xử lý lỗi** và **logic nghiệp vụ** để mã nguồn rõ ràng, dễ kiểm thử.

Ví dụ, một API nên chuyển `ValueError` thành phản hồi HTTP 400, còn `FileNotFoundError` thành HTTP 404, thay vì để chương trình dừng hoặc trả về lỗi chung chung.

---

# Chuẩn bị cho Buổi 23

Ở **Buổi 23**, chúng ta sẽ đi sâu hơn vào xử lý ngoại lệ với các chủ đề nâng cao:

* `raise` và cách chủ động phát sinh Exception.
* Tự định nghĩa **Custom Exception**.
* Exception Chaining (`raise ... from ...`).
* Context Manager và câu lệnh `with`.
* Xây dựng các lớp quản lý tài nguyên theo chuẩn Python (`__enter__`, `__exit__`).
* Thực hành với file, database và network theo phong cách chuyên nghiệp.

Đây là bước chuyển từ **biết bắt lỗi** sang **thiết kế hệ thống xử lý lỗi chuẩn**, giúp ứng dụng của bạn đáng tin cậy và dễ bảo trì hơn.
