Đây là **Giai đoạn 1 - Python Foundation** trong giáo trình "Làm chủ Python từ A-Z (2026 Edition)". Chúng ta sẽ học theo phong cách của một lập trình viên Python chuyên nghiệp: từ bản chất → cú pháp → ví dụ → thực hành → bài tập → lưu ý thực tế.

---

# Buổi 19. Exception (Xử lý ngoại lệ)

## Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu Exception là gì

* Biết vì sao cần Exception

* Biết sử dụng

* try

* except

* else

* finally

* raise

* Biết tạo Exception riêng

* Biết cách thiết kế chương trình không bị crash

---

# 1. Exception là gì?

Exception là **lỗi xảy ra trong lúc chương trình đang chạy (Runtime Error).**

Ví dụ:

```python
print(10 / 0)
```

Kết quả

```
ZeroDivisionError
```

Python dừng chương trình.

Đây gọi là Exception.

---

Ví dụ

```python
number = int("abc")
```

Kết quả

```
ValueError
```

---

Ví dụ

```python
data = [1, 2]

print(data[10])
```

Kết quả

```
IndexError
```

---

# 2. Có nên để chương trình bị crash?

Ví dụ

```python
age = int(input("Age: "))

print(age)
```

Người dùng nhập

```
abc
```

Chương trình

```
ValueError
```

và dừng.

Đây là trải nghiệm rất tệ.

---

Ta muốn

```
Age: abc

Bạn nhập sai.
Vui lòng nhập số.
```

Đó là lý do Exception ra đời.

---

# 3. try except

Cú pháp

```python
try:
    code
except:
    xử lý lỗi
```

Ví dụ

```python
try:
    number = int(input("Number: "))
    print(number)
except:
    print("Bạn nhập không hợp lệ.")
```

---

Nhập

```
abc
```

Kết quả

```
Bạn nhập không hợp lệ.
```

Không crash.

---

# 4. Exception hoạt động như thế nào?

Ví dụ

```python
print("A")

try:
    print("B")
    x = 10 / 0
    print("C")
except:
    print("Có lỗi")

print("D")
```

Kết quả

```
A
B
Có lỗi
D
```

Lệnh

```
print("C")
```

không chạy.

---

# 5. Bắt từng loại Exception

Không nên

```python
except:
```

Nên

```python
except ZeroDivisionError:
```

Ví dụ

```python
try:
    print(10 / 0)

except ZeroDivisionError:
    print("Không được chia cho 0.")
```

---

Ví dụ

```python
try:
    age = int(input())

except ValueError:
    print("Bạn phải nhập số.")
```

---

# 6. Một try nhiều except

```python
try:
    ...

except ValueError:
    ...

except ZeroDivisionError:
    ...

except IndexError:
    ...
```

Ví dụ

```python
try:
    numbers = [1, 2]

    x = int(input())

    print(numbers[x])

except ValueError:
    print("Không phải số.")

except IndexError:
    print("Sai chỉ mục.")
```

---

# 7. except Exception

Có thể

```python
try:
    ...

except Exception:
    print("Có lỗi.")
```

Exception là cha của gần như toàn bộ Exception.

Ví dụ

```python
try:
    print(10 / 0)

except Exception:
    print("Lỗi.")
```

---

Không nên dùng quá nhiều.

Nó che mất lỗi thật.

---

# 8. Lấy thông tin lỗi

```python
try:
    ...

except Exception as e:
    print(e)
```

Ví dụ

```python
try:
    print(10 / 0)

except Exception as e:
    print(e)
```

Kết quả

```
division by zero
```

---

Ví dụ

```python
try:
    int("abc")

except Exception as e:
    print(type(e))
    print(e)
```

```
<class 'ValueError'>

invalid literal for int()
```

---

# 9. else

Nếu không có lỗi

```
try
```

thì

```
else
```

được chạy.

Ví dụ

```python
try:
    x = int(input())

except ValueError:
    print("Sai.")

else:
    print("Đúng.")
```

---

Nhập

```
100
```

```
Đúng.
```

---

# 10. finally

finally luôn chạy.

Ví dụ

```python
try:
    print(10 / 0)

except:
    print("Có lỗi")

finally:
    print("Đóng file")
```

Kết quả

```
Có lỗi

Đóng file
```

---

Ngay cả

```python
return
```

thì finally vẫn chạy.

Ví dụ

```python
def demo():
    try:
        return 100

    finally:
        print("Finally")


print(demo())
```

Kết quả

```
Finally
100
```

---

# 11. raise

Ta có thể chủ động tạo Exception.

Ví dụ

```python
age = -10

if age < 0:
    raise ValueError("Age không hợp lệ.")
```

Kết quả

```
ValueError
```

---

Ví dụ

```python
score = 15

if score > 10:
    raise Exception("Điểm sai.")
```

---

# 12. Tạo Exception riêng

Ví dụ

```python
class AgeError(Exception):
    pass
```

Sử dụng

```python
age = -5

if age < 0:
    raise AgeError("Age phải >= 0")
```

---

Bắt

```python
try:
    age = -5

    if age < 0:
        raise AgeError("Sai.")

except AgeError as e:
    print(e)
```

---

# 13. Exception lồng nhau

```python
try:
    try:
        print(10 / 0)

    except ZeroDivisionError:
        print("Inner")

except:
    print("Outer")
```

Kết quả

```
Inner
```

---

Nếu bỏ inner

Outer sẽ bắt.

---

# 14. Bắt nhiều Exception

```python
except (ValueError, TypeError):
```

Ví dụ

```python
try:
    ...

except ValueError, TypeError:
    print("Sai dữ liệu.")
```

---

# 15. Assertion

```python
assert điều_kiện
```

Ví dụ

```python
age = 20

assert age >= 0
```

Không có gì xảy ra.

---

Sai

```python
age = -1

assert age >= 0
```

```
AssertionError
```

---

Có message

```python
assert age >= 0, "Age âm."
```

---

# 16. Exception thường gặp

| Exception           | Ý nghĩa             |
| ------------------- | ------------------- |
| ValueError          | Sai giá trị         |
| TypeError           | Sai kiểu            |
| IndexError          | Sai index           |
| KeyError            | Sai key             |
| AttributeError      | Không có thuộc tính |
| NameError           | Biến chưa tồn tại   |
| FileNotFoundError   | Không tìm thấy file |
| ZeroDivisionError   | Chia cho 0          |
| ImportError         | Import lỗi          |
| ModuleNotFoundError | Không có module     |
| RuntimeError        | Lỗi runtime         |
| AssertionError      | assert sai          |

---

# 17. Ví dụ thực tế

```python
while True:
    try:
        age = int(input("Age: "))

        if age < 0:
            raise ValueError("Age âm.")

    except ValueError as e:
        print(e)

    else:
        print("OK")
        break
```

Ví dụ chạy:

```
Age: abc
invalid literal for int() with base 10: 'abc'

Age: -5
Age âm.

Age: 25
OK
```

---

# 18. Best Practices

### Luôn bắt Exception cụ thể

```python
except ValueError:
```

Thay vì

```python
except:
```

---

### Không bỏ qua Exception

Không nên

```python
except:
    pass
```

Việc này khiến lỗi bị "nuốt", rất khó gỡ lỗi.

---

### Dùng `finally` để giải phóng tài nguyên

```python
file = None

try:
    file = open("data.txt")
    content = file.read()
except FileNotFoundError:
    print("Không tìm thấy file.")
finally:
    if file:
        file.close()
```

Trong thực tế, ở các buổi sau bạn sẽ học `with`, đây là cách hiện đại và an toàn hơn để làm việc với file.

---

### Ghi log thay vì chỉ in lỗi

```python
import logging

logging.basicConfig(level=logging.ERROR)

try:
    1 / 0
except ZeroDivisionError:
    logging.exception("Có lỗi xảy ra")
```

---

# 19. Bài tập thực hành

### Bài 1

Viết chương trình yêu cầu nhập số nguyên.

* Nếu nhập sai thì yêu cầu nhập lại.
* Chỉ kết thúc khi nhập đúng.

---

### Bài 2

Nhập hai số và thực hiện phép chia.

* Bắt lỗi chia cho 0.
* Bắt lỗi nhập sai kiểu dữ liệu.

---

### Bài 3

Viết lớp ngoại lệ `InvalidPasswordError`.

* Nếu mật khẩu ngắn hơn 8 ký tự thì phát sinh ngoại lệ.
* Bắt ngoại lệ và hiển thị thông báo thân thiện.

---

### Bài 4

Viết hàm `read_positive_number()`:

* Chỉ chấp nhận số nguyên dương.
* Nếu nhập âm hoặc không phải số thì yêu cầu nhập lại.
* Sử dụng `raise` để phát sinh ngoại lệ khi giá trị âm.

---

# 20. Tổng kết

Trong buổi này, bạn đã học được:

* Khái niệm Exception và Runtime Error.
* Cách sử dụng `try`, `except`, `else`, `finally`.
* Bắt các loại ngoại lệ cụ thể và lấy thông tin lỗi với `except ... as`.
* Chủ động phát sinh ngoại lệ bằng `raise`.
* Tạo ngoại lệ tùy chỉnh bằng cách kế thừa `Exception`.
* Sử dụng `assert` để kiểm tra các điều kiện trong quá trình phát triển.
* Các nguyên tắc xử lý ngoại lệ theo hướng chuyên nghiệp.

## Chuẩn bị cho buổi 20

Ở buổi tiếp theo, chúng ta sẽ bước sang **Giai đoạn 2 – Python Intermediate** với chủ đề **Module**, tìm hiểu cách tổ chức mã nguồn thành nhiều tệp, cơ chế `import`, cách Python tìm kiếm module và các nguyên tắc xây dựng module theo chuẩn dự án.
