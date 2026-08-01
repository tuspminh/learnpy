Đúng rồi. Có một lỗ hổng trong lộ trình.

Trong roadmap, **Buổi 7 là Vòng lặp**, **Buổi 8 là `break`, `continue`, `pass`**. Tuy nhiên, nếu chỉ học `break`, `continue`, `pass` thì sẽ **thiếu một nội dung rất quan trọng** thường được dạy cùng giai đoạn này, đó là **vòng lặp `while`**.

Ở các khóa Python bài bản, phần "Vòng lặp" thường được chia thành:

* Buổi 7: `for`, `range()`
* Buổi 8: `while`, `break`, `continue`, `pass`

Có thể khi dạy trước đây, chúng ta đã tập trung vào `break`, `continue`, `pass` mà chưa học kỹ `while`.

---

## Buổi 8 (Bổ sung). Vòng lặp `while`

### Mục tiêu

Sau buổi học này, bạn sẽ:

* Hiểu cách hoạt động của `while`.
* Phân biệt `for` và `while`.
* Biết tránh vòng lặp vô hạn.
* Kết hợp `while` với `break`, `continue`.
* Viết được các chương trình nhập liệu lặp cho đến khi hợp lệ.

---

# 1. Vòng lặp `while`

`while` lặp **miễn là điều kiện còn đúng**.

Cú pháp:

```python
while điều_kiện:
    # Khối lệnh
```

Ví dụ:

```python
i = 1

while i <= 5:
    print(i)
    i += 1
```

Kết quả:

```text
1
2
3
4
5
```

---

# 2. Luồng hoạt động

```text
i = 1

↓
i <= 5 ?
↓
Đúng
↓
print(i)
↓
i += 1
↓
Quay lại kiểm tra điều kiện
```

Khi điều kiện sai, vòng lặp kết thúc.

---

# 3. Vòng lặp vô hạn

Ví dụ:

```python
i = 1

while i <= 5:
    print(i)
```

Biến `i` không thay đổi nên điều kiện luôn đúng.

Chương trình sẽ chạy mãi.

---

# 4. `while True`

Đây là cách rất phổ biến trong lập trình.

```python
while True:
    text = input("Nhập 'q' để thoát: ")

    if text == "q":
        break

    print("Bạn nhập:", text)
```

Ví dụ chạy:

```text
Nhập 'q' để thoát: Python
Bạn nhập: Python

Nhập 'q' để thoát: Hello
Bạn nhập: Hello

Nhập 'q' để thoát: q
```

---

# 5. `break` trong `while`

```python
i = 1

while True:
    print(i)

    if i == 5:
        break

    i += 1
```

Kết quả:

```text
1
2
3
4
5
```

---

# 6. `continue` trong `while`

```python
i = 0

while i < 5:
    i += 1

    if i == 3:
        continue

    print(i)
```

Kết quả:

```text
1
2
4
5
```

> **Lưu ý:** Với `while`, hãy cập nhật biến điều khiển (`i += 1`) trước `continue` nếu không có thể gây vòng lặp vô hạn.

---

# 7. `pass`

`pass` là câu lệnh "không làm gì".

```python
while False:
    pass

print("Hoàn thành")
```

Kết quả:

```text
Hoàn thành
```

Thường dùng làm chỗ trống khi đang xây dựng chương trình.

---

# 8. `while...else`

Ít người mới biết Python có cú pháp này.

```python
i = 1

while i <= 3:
    print(i)
    i += 1
else:
    print("Đã lặp xong")
```

Kết quả:

```text
1
2
3
Đã lặp xong
```

Nếu vòng lặp kết thúc bằng `break`, phần `else` sẽ **không chạy**.

---

# 9. `for` hay `while`?

Dùng `for` khi:

* Biết trước số lần lặp.
* Duyệt danh sách, chuỗi, `range()`.

Ví dụ:

```python
for i in range(10):
    print(i)
```

Dùng `while` khi:

* Không biết trước số lần lặp.
* Lặp đến khi người dùng nhập đúng.
* Lặp đến khi nhận được dữ liệu mong muốn.

Ví dụ:

```python
password = ""

while password != "python":
    password = input("Mật khẩu: ")
```

---

# 10. Ví dụ thực tế

### Đăng nhập

```python
PASSWORD = "python123"

while True:
    pwd = input("Nhập mật khẩu: ")

    if pwd == PASSWORD:
        print("Đăng nhập thành công.")
        break

    print("Sai mật khẩu.")
```

---

### Tính tổng từ 1 đến n

```python
n = int(input("n = "))

i = 1
total = 0

while i <= n:
    total += i
    i += 1

print("Tổng =", total)
```

---

### Menu đơn giản

```python
while True:
    print("1. Xin chào")
    print("2. Thoát")

    choice = input("Chọn: ")

    if choice == "1":
        print("Xin chào!")

    elif choice == "2":
        print("Tạm biệt!")
        break

    else:
        print("Lựa chọn không hợp lệ.")
```

---

# 11. Những lỗi thường gặp

### Quên cập nhật biến

Sai:

```python
i = 1

while i <= 5:
    print(i)
```

Đúng:

```python
i = 1

while i <= 5:
    print(i)
    i += 1
```

---

### `continue` gây vòng lặp vô hạn

Sai:

```python
i = 0

while i < 5:
    if i == 2:
        continue
    i += 1
```

Khi `i == 2`, `continue` làm bỏ qua `i += 1`, khiến `i` luôn bằng 2.

Đúng:

```python
i = 0

while i < 5:
    i += 1

    if i == 2:
        continue

    print(i)
```

---

# Bài tập thực hành

### Bài 1

Viết chương trình in các số từ 1 đến 20 bằng `while`.

---

### Bài 2

Tính tổng các số từ 1 đến `n` bằng `while`.

---

### Bài 3

Yêu cầu người dùng nhập mật khẩu cho đến khi đúng.

---

### Bài 4

Viết chương trình nhập số nguyên. Nếu người dùng nhập sai (không phải số), yêu cầu nhập lại. *(Gợi ý: bài này sẽ được làm hoàn chỉnh hơn sau khi học `Exception` ở Buổi 19.)*

---

### Bài 5

Viết menu:

```text
1. Cộng
2. Trừ
3. Thoát
```

Chương trình lặp lại cho đến khi người dùng chọn **3**.

---

# Tổng kết

Trong buổi học bổ sung này, bạn đã học:

* Vòng lặp `while`.
* Sự khác nhau giữa `for` và `while`.
* Cách tránh vòng lặp vô hạn.
* Kết hợp `while` với `break`, `continue`, `pass`.
* Cú pháp `while...else`.
* Các ví dụ thực tế như đăng nhập, menu và nhập liệu lặp.

> Như vậy, **Giai đoạn 1** của chúng ta đã được đồng bộ lại đúng thứ tự từ **Buổi 1 đến Buổi 10**, không còn thiếu kiến thức nền tảng trước khi tiếp tục sang **Tuple, Set, Dictionary, Function** và các chủ đề tiếp theo.
