# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 7: Làm chủ vòng lặp `while`

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Hiểu bản chất của vòng lặp.
> - Thành thạo `while`.
> - Hiểu điều kiện dừng.
> - Biết cách tránh vòng lặp vô hạn.
> - Thành thạo `break`, `continue`, `else`.
> - Biết các mẫu (pattern) thường dùng trong thực tế.
> - Xây dựng được nhiều chương trình tương tác.

---

# 1. Vòng lặp là gì?

Trong lập trình, có rất nhiều công việc phải lặp đi lặp lại.

Ví dụ:

- In 1000 hóa đơn.
- Đọc từng dòng trong file.
- Xử lý hàng triệu bản ghi trong cơ sở dữ liệu.
- Server luôn chờ yêu cầu từ người dùng.
- Game luôn cập nhật trạng thái mỗi khung hình.

Nếu không có vòng lặp:

```text-x-trilium-auto
print("Xin chào")
print("Xin chào")
print("Xin chào")
print("Xin chào")
print("Xin chào")
```

Nếu cần in 10.000 lần thì sao?

Không ai viết như vậy.

---

# 2. `while` là gì?

`while` có nghĩa là:

> **Lặp lại khi điều kiện còn đúng.**

Cú pháp:

```text-x-trilium-auto
while điều_kiện:
    khối_lệnh
```

Luồng hoạt động:

```text-x-trilium-auto
Bắt đầu

↓

Kiểm tra điều kiện

↓

True?

↓

Có

↓

Thực hiện khối lệnh

↓

Quay lại kiểm tra

↓

False

↓

Kết thúc
```

---

# 3. Ví dụ đầu tiên

```text-x-trilium-auto
count = 1

while count <= 5:
    print(count)
    count += 1
```

Kết quả:

```text-x-trilium-auto
1
2
3
4
5
```

---

Điều gì xảy ra?

Lần đầu:

```text-x-trilium-auto
count = 1

1 <= 5

↓

True

↓

In 1

↓

count = 2
```

Lần thứ hai:

```text-x-trilium-auto
2 <= 5

↓

True

↓

In 2
```

...

Lần cuối:

```text-x-trilium-auto
count = 6

6 <= 5

↓

False

↓

Dừng
```

---

# 4. Biến đếm (Counter)

Hầu hết vòng lặp đều cần biến đếm.

```text-x-trilium-auto
i = 1

while i <= 10:
    print(i)
    i += 1
```

Trong Python, `i` thường là viết tắt của **index** hoặc **iterator**.

---

# 5. Quên cập nhật biến

Sai:

```text-x-trilium-auto
i = 1

while i <= 5:
    print(i)
```

Điều gì xảy ra?

```text-x-trilium-auto
1

1

1

1

1

...
```

Không bao giờ dừng.

Đây gọi là:

# Vòng lặp vô hạn (Infinite Loop)

---

# 6. Ví dụ thực tế

Đếm ngược:

```text-x-trilium-auto
seconds = 10

while seconds > 0:
    print(seconds)
    seconds -= 1

print("Hết giờ!")
```

Kết quả:

```text-x-trilium-auto
10
9
8
7
6
5
4
3
2
1
Hết giờ!
```

---

# 7. `while True`

Đây là mẫu rất phổ biến trong các chương trình thực tế.

```text-x-trilium-auto
while True:
    print("Chương trình đang chạy...")
```

Vòng lặp sẽ không bao giờ dừng nếu không có lệnh thoát.

Ứng dụng:

- Server Web
- Chatbot
- Game
- CLI Menu
- Robot
- Camera AI

---

# 8. `break`

`break` dùng để thoát khỏi vòng lặp ngay lập tức.

```text-x-trilium-auto
while True:
    text = input("Nhập exit để thoát: ")

    if text == "exit":
        break

    print("Bạn nhập:", text)

print("Đã kết thúc.")
```

Ví dụ:

```text-x-trilium-auto
Nhập exit để thoát: Python
Bạn nhập: Python

Nhập exit để thoát: Hello
Bạn nhập: Hello

Nhập exit để thoát: exit

Đã kết thúc.
```

---

# 9. `continue`

`continue` bỏ qua phần còn lại của lần lặp hiện tại và chuyển sang lần lặp tiếp theo.

```text-x-trilium-auto
i = 0

while i < 5:
    i += 1

    if i == 3:
        continue

    print(i)
```

Kết quả:

```text-x-trilium-auto
1
2
4
5
```

Số `3` bị bỏ qua.

---

# 10. `while...else`

Ít người mới biết tính năng này.

```text-x-trilium-auto
i = 1

while i <= 3:
    print(i)
    i += 1
else:
    print("Đã lặp xong.")
```

Kết quả:

```text-x-trilium-auto
1
2
3
Đã lặp xong.
```

---

Nếu dùng `break`:

```text-x-trilium-auto
i = 1

while i <= 5:
    if i == 3:
        break

    print(i)
    i += 1
else:
    print("Hoàn thành.")
```

Kết quả:

```text-x-trilium-auto
1
2
```

`else` **không được thực hiện** vì vòng lặp kết thúc bằng `break`.

---

# 11. Mẫu nhập dữ liệu hợp lệ

```text-x-trilium-auto
while True:
    age = int(input("Tuổi: "))

    if age >= 0:
        break

    print("Tuổi phải lớn hơn hoặc bằng 0.")

print("Tuổi hợp lệ:", age)
```

Đây là mẫu rất phổ biến trong các ứng dụng thực tế.

---

# 12. Ví dụ: Đăng nhập 3 lần

```text-x-trilium-auto
PASSWORD = "python123"

count = 0

while count < 3:
    password = input("Mật khẩu: ")

    if password == PASSWORD:
        print("Đăng nhập thành công.")
        break

    count += 1
    print("Sai mật khẩu.")
else:
    print("Đã vượt quá số lần cho phép.")
```

---

# 13. Tổng các số từ 1 đến 100

```text-x-trilium-auto
i = 1
total = 0

while i <= 100:
    total += i
    i += 1

print(total)
```

Kết quả:

```text-x-trilium-auto
5050
```

---

# 14. Tìm số đầu tiên chia hết cho 17

```text-x-trilium-auto
number = 1

while True:
    if number % 17 == 0:
        print(number)
        break

    number += 1
```

Kết quả:

```text-x-trilium-auto
17
```

---

# 15. Menu lặp

```text-x-trilium-auto
while True:
    print("""
1. Xem thông tin
2. Đổi mật khẩu
3. Thoát
""")

    choice = input("Chọn: ")

    if choice == "1":
        print("Thông tin người dùng")

    elif choice == "2":
        print("Đổi mật khẩu")

    elif choice == "3":
        print("Tạm biệt!")
        break

    else:
        print("Lựa chọn không hợp lệ.")
```

Đây là mẫu được dùng rất nhiều trong các ứng dụng CLI.

---

# 16. Những lỗi phổ biến

## Lỗi 1: Quên cập nhật biến

```text-x-trilium-auto
i = 1

while i <= 5:
    print(i)
```

➡️ Vòng lặp vô hạn.

---

## Lỗi 2: `continue` trước khi cập nhật biến

Sai:

```text-x-trilium-auto
i = 0

while i < 5:
    if i == 2:
        continue

    i += 1
```

Khi `i == 2`, chương trình quay lại đầu vòng lặp mà `i` không tăng nữa, dẫn đến vòng lặp vô hạn.

Đúng:

```text-x-trilium-auto
i = 0

while i < 5:
    i += 1

    if i == 2:
        continue

    print(i)
```

---

## Lỗi 3: Điều kiện không bao giờ sai

```text-x-trilium-auto
while True:
    print("Hello")
```

Nếu không có `break`, chương trình sẽ chạy mãi.

---

# 17. Pythonic

Không nên:

```text-x-trilium-auto
running = True

while running:
    command = input("> ")

    if command == "exit":
        running = False
```

Có thể viết ngắn gọn hơn:

```text-x-trilium-auto
while True:
    command = input("> ")

    if command == "exit":
        break
```

Dễ đọc và phổ biến hơn.

---

# 18. Ứng dụng thực tế

`while` xuất hiện trong:

- Máy ATM.
- Chatbot AI.
- Trò chơi.
- Máy chủ web.
- Ứng dụng đọc dữ liệu cảm biến.
- Camera giám sát.
- Hệ thống xử lý hàng đợi.
- Giao diện dòng lệnh (CLI).

---

# 19. Bài tập thực hành

## Bài 1

In các số từ `1` đến `20`.

---

## Bài 2

In các số chẵn từ `2` đến `100`.

---

## Bài 3

Tính tổng các số từ `1` đến `50`.

---

## Bài 4

Nhập mật khẩu.

Nếu sai thì yêu cầu nhập lại.

Đúng thì kết thúc.

---

## Bài 5

Viết chương trình đếm ngược từ `10` về `1`.

---

## Bài 6

Nhập các số nguyên.

Nếu nhập `0` thì dừng.

Sau đó in tổng các số đã nhập.

*Gợi ý:* Dùng `while True` và `break`.

---

## Bài 7

Viết menu:

```text-x-trilium-auto
1. Cộng
2. Trừ
3. Thoát
```

Sau mỗi thao tác, menu xuất hiện lại.

Chỉ kết thúc khi người dùng chọn `3`.

---

# Mini Project: Trò chơi đoán số

Máy tính "nghĩ" đến một số từ **1 đến 100**.

Ví dụ:

```text-x-trilium-auto
secret_number = 73
```

Yêu cầu:

1. Người chơi nhập một số.
2. Nếu nhỏ hơn số bí mật:

```text-x-trilium-auto
Quá nhỏ!
```

3. Nếu lớn hơn:

```text-x-trilium-auto
Quá lớn!
```

4. Nếu đúng:

```text-x-trilium-auto
Chúc mừng! Bạn đã đoán đúng.
```

5. Sau khi đoán đúng, kết thúc chương trình.

> **Nâng cao:** Hãy dùng mô-đun `random` để sinh số bí mật ngẫu nhiên thay vì gán cố định:
> 
> ```text-x-trilium-auto
> import random
> 
> secret_number = random.randint(1, 100)
> ```
> 
> Chúng ta sẽ học chi tiết về mô-đun và thư viện chuẩn ở các buổi sau, nhưng bạn có thể thử ngay để tăng tính thú vị cho trò chơi.

---

# Tổng kết buổi 7

Hôm nay bạn đã học được:

- ✅ Bản chất của vòng lặp `while`.
- ✅ Biến đếm và điều kiện dừng.
- ✅ Vòng lặp vô hạn và cách tránh.
- ✅ `while True`.
- ✅ `break`.
- ✅ `continue`.
- ✅ `while...else`.
- ✅ Các mẫu lập trình thực tế như nhập dữ liệu hợp lệ, đăng nhập nhiều lần và menu lặp.
- ✅ Những lỗi phổ biến và cách khắc phục.

---

# Góc lập trình viên chuyên nghiệp

`while` được sử dụng khi **không biết trước số lần lặp**.

Ví dụ:

- Đọc dữ liệu từ socket cho đến khi kết nối đóng.
- Chờ người dùng nhập dữ liệu hợp lệ.
- Xử lý hàng đợi công việc cho đến khi hết việc.
- Chạy server hoặc chatbot liên tục.
- Thực hiện game loop cho đến khi người chơi thoát.

Ngược lại, khi **đã biết trước số lần lặp**, Python thường ưu tiên dùng `for`, vì ngắn gọn, an toàn và dễ đọc hơn.

## Chuẩn bị cho Buổi 8

Ở buổi tiếp theo, chúng ta sẽ học **vòng lặp** `**for**` từ cơ bản đến nâng cao: cách hoạt động của `range()`, duyệt chuỗi, danh sách, từ điển, `enumerate()`, `zip()`, vòng lặp lồng nhau, cùng nhiều kỹ thuật Pythonic được sử dụng hằng ngày trong các dự án thực tế. Đây là một trong những công cụ được dùng nhiều nhất trong Python.
