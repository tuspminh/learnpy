Được. Chúng ta sẽ **quay lại đúng roadmap Giai đoạn 1** và học tuần tự từ **Buổi 9**. Tôi sẽ bỏ qua toàn bộ phần đã đi lệch trước đó (Decorator, DDD, Flask, Iterator...) và chỉ bám sát giáo trình này.

Roadmap còn lại của Giai đoạn 1:

* ✅ Buổi 1. Python là gì?
* ✅ Buổi 2. Biến và kiểu dữ liệu
* ✅ Buổi 3. Input Output
* ✅ Buổi 4. Toán tử
* ✅ Buổi 5. Điều kiện
* ✅ Buổi 6. Match Case
* ✅ Buổi 7. Vòng lặp
* ✅ Buổi 8. break continue pass
* **➡ Buổi 9. String**
* Buổi 10. List
* Buổi 11. Tuple
* Buổi 12. Set
* Buổi 13. Dictionary
* Buổi 14. Hàm
* Buổi 15. Scope
* Buổi 16. Lambda
* Buổi 17. List Comprehension
* Buổi 18. Dict Comprehension
* Buổi 19. Exception

---

# Buổi 9. String (Chuỗi) – Nền tảng xử lý văn bản trong Python

## Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu bản chất của `str`.
* Biết cách tạo chuỗi.
* Hiểu Immutable Object.
* Truy cập từng ký tự.
* Cắt chuỗi (Slicing).
* Duyệt chuỗi.
* Nối chuỗi.
* Lặp chuỗi.
* Kiểm tra chuỗi.
* Hiểu Unicode.
* Biết các phép toán thường dùng với chuỗi.

---

# 1. String là gì?

String là kiểu dữ liệu dùng để lưu văn bản.

```python
name = "Nguyễn Văn A"

city = "Hà Nội"

message = "Hello Python"
```

Kiểm tra kiểu dữ liệu

```python
name = "Python"

print(type(name))
```

Kết quả

```text
<class 'str'>
```

`str` là viết tắt của **string**.

---

# 2. Tạo String

Có 3 cách.

## Dùng dấu nháy đơn

```python
name = "Python"
```

---

## Dùng dấu nháy kép

```python
name = "Python"
```

Hai cách hoàn toàn giống nhau.

---

## Dùng ba dấu nháy

```python
text = """
Python
Java
C++
"""
```

Kết quả

```text
Python
Java
C++
```

Thường dùng cho:

* SQL
* HTML
* JSON
* Văn bản nhiều dòng

---

# 3. String là Immutable

Đây là kiến thức cực kỳ quan trọng.

Chuỗi trong Python **không thể thay đổi trực tiếp**.

Ví dụ

```python
name = "Python"

name[0] = "J"
```

Kết quả

```text
TypeError:
'str' object does not support item assignment
```

Không thể sửa từng ký tự.

---

Muốn đổi

```text
Python
```

thành

```text
Jython
```

Ta phải tạo chuỗi mới.

```python
name = "Python"

name = "J" + name[1:]

print(name)
```

Kết quả

```text
Jython
```

---

# 4. Độ dài chuỗi

Dùng

```python
len()
```

Ví dụ

```python
text = "Python"

print(len(text))
```

Kết quả

```text
6
```

---

Chuỗi rỗng

```python
text = ""

print(len(text))
```

Kết quả

```text
0
```

---

# 5. Truy cập ký tự

Giống List.

```python
text = "Python"

print(text[0])
```

```text
P
```

---

```python
print(text[1])
```

```text
y
```

---

```python
print(text[5])
```

```text
n
```

---

# 6. Index âm

Python hỗ trợ index âm.

```python
text = "Python"

print(text[-1])
```

```text
n
```

---

```python
print(text[-2])
```

```text
o
```

---

```python
print(text[-6])
```

```text
P
```

---

# 7. Slicing

Cú pháp

```python
string[start:stop]
```

Ví dụ

```python
text = "Python"

print(text[0:2])
```

```text
Py
```

---

```python
print(text[2:5])
```

```text
tho
```

---

```python
print(text[:3])
```

```text
Pyt
```

---

```python
print(text[3:])
```

```text
hon
```

---

```python
print(text[:])
```

```text
Python
```

---

# 8. Bước nhảy (Step)

```python
text = "Python"

print(text[::2])
```

```text
Pto
```

---

```python
print(text[1::2])
```

```text
yhn
```

---

Đảo chuỗi

```python
print(text[::-1])
```

```text
nohtyP
```

---

# 9. Duyệt chuỗi

## Cách 1

```python
text = "Python"

for ch in text:
    print(ch)
```

Kết quả

```text
P
y
t
h
o
n
```

---

## Cách 2

```python
for i in range(len(text)):
    print(i, text[i])
```

Kết quả

```text
0 P
1 y
2 t
3 h
4 o
5 n
```

---

# 10. Toán tử `+`

```python
first = "Hello"

second = "Python"

print(first + second)
```

```text
HelloPython
```

---

Thêm khoảng trắng

```python
print(first + " " + second)
```

```text
Hello Python
```

---

# 11. Toán tử `*`

```python
print("Hi" * 3)
```

```text
HiHiHi
```

---

```python
print("=" * 30)
```

```text
==============================
```

Thường dùng để in tiêu đề.

---

# 12. Toán tử `in`

```python
text = "Hello Python"

print("Python" in text)
```

```text
True
```

---

```python
print("Java" in text)
```

```text
False
```

---

# 13. Toán tử `not in`

```python
print("Java" not in text)
```

```text
True
```

---

# 14. So sánh chuỗi

```python
print("abc" == "abc")
```

```text
True
```

---

```python
print("abc" == "ABC")
```

```text
False
```

---

Python so sánh theo mã Unicode.

```python
print("A" < "B")
```

```text
True
```

---

```python
print("apple" < "banana")
```

```text
True
```

---

# 15. Unicode

Python 3 dùng Unicode.

Ví dụ

```python
text = "Xin chào Việt Nam"

print(text)
```

```text
Xin chào Việt Nam
```

Không cần xử lý đặc biệt cho tiếng Việt.

---

# 16. Escape Character

Xuống dòng

```python
print("Hello\nPython")
```

```text
Hello
Python
```

---

Tab

```python
print("A\tB")
```

```text
A    B
```

---

Dấu nháy kép

```python
print('Tôi tên là "An"')
```

```text
Tôi tên là "An"
```

---

Dấu gạch chéo

```python
print("C:\\Users\\Admin")
```

```text
C:\Users\Admin
```

---

# 17. Raw String

Đường dẫn Windows

```python
path = r"C:\Users\Admin\Documents"

print(path)
```

Kết quả

```text
C:\Users\Admin\Documents
```

`r"..."` giúp Python không xử lý các ký tự escape.

---

# 18. Ví dụ thực tế

Chương trình kiểm tra tên đăng nhập.

```python
username = input("Tên đăng nhập: ")

if username == "admin":
    print("Đăng nhập thành công.")
else:
    print("Sai tên đăng nhập.")
```

---

Đảo ngược chuỗi.

```python
text = input("Nhập chuỗi: ")

print(text[::-1])
```

---

Kiểm tra chuỗi đối xứng (Palindrome).

```python
text = input("Nhập chuỗi: ")

if text == text[::-1]:
    print("Chuỗi đối xứng.")
else:
    print("Không phải chuỗi đối xứng.")
```

Ví dụ:

```text
Nhập chuỗi: madam
Chuỗi đối xứng.
```

---

# 19. Những lỗi người mới thường gặp

### 1. Truy cập ngoài phạm vi

```python
text = "Python"

print(text[10])
```

Lỗi:

```text
IndexError: string index out of range
```

---

### 2. Quên tính bất biến của chuỗi

```python
text = "Python"

text[0] = "J"
```

Lỗi:

```text
TypeError
```

---

### 3. Cộng chuỗi với số

```python
age = 20

print("Age: " + age)
```

Lỗi:

```text
TypeError
```

Đúng:

```python
print("Age:", age)

print("Age: " + str(age))
```

---

# 20. Bài tập thực hành

### Bài 1

Nhập họ và tên, in ra:

* Độ dài chuỗi.
* Ký tự đầu tiên.
* Ký tự cuối cùng.

---

### Bài 2

Nhập một chuỗi và:

* In chuỗi đảo ngược.
* In các ký tự ở vị trí chẵn.
* In các ký tự ở vị trí lẻ.

---

### Bài 3

Kiểm tra một chuỗi có chứa từ `"Python"` hay không bằng toán tử `in`.

---

### Bài 4

Viết chương trình kiểm tra chuỗi có đối xứng (palindrome) hay không.

---

### Bài 5

Nhập một đường dẫn Windows và in ra bằng `raw string` để quan sát sự khác biệt với chuỗi thông thường.

---

# Tổng kết

Trong buổi học này, bạn đã nắm được những kiến thức nền tảng về `str`:

* Bản chất của chuỗi và tính **immutable**.
* Truy cập ký tự bằng chỉ số dương và âm.
* Cắt chuỗi với **slicing** và **step**.
* Duyệt chuỗi bằng `for`.
* Các toán tử `+`, `*`, `in`, `not in`.
* So sánh chuỗi theo Unicode.
* Escape character và `raw string`.
* Một số ví dụ và bài tập thực hành.

> **Lưu ý:** Đây mới chỉ là phần **nền tảng của String**. Ở buổi tiếp theo, chúng ta sẽ học sâu hơn về **các phương thức (methods) của `str`** như `upper()`, `lower()`, `strip()`, `split()`, `join()`, `replace()`, `find()`, `startswith()`, `endswith()`, `format()`, `count()`,... Đây là những công cụ được sử dụng rất nhiều trong các dự án Python thực tế.
