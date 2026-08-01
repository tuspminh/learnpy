# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 1: Giới thiệu Python và chuẩn bị môi trường phát triển

> **Mục tiêu buổi học**
> 
> Sau buổi học này bạn sẽ:
> 
> - Hiểu Python là gì và tại sao nó rất phổ biến.
> - Hiểu Python hoạt động như thế nào.
> - Cài đặt đầy đủ môi trường lập trình.
> - Biết sử dụng Terminal/Command Prompt.
> - Viết chương trình Python đầu tiên.
> - Biết cách chạy chương trình theo nhiều cách.
> - Hiểu lỗi cơ bản và cách đọc lỗi.
> - Viết code đúng chuẩn ngay từ đầu.

---

# 1. Python là gì?

Python là một **ngôn ngữ lập trình thông dịch (Interpreted Language)** được tạo bởi Guido van Rossum vào năm 1991.

Mục tiêu của Python:

- Dễ đọc
- Dễ học
- Dễ bảo trì
- Mạnh mẽ
- Đa nền tảng

Triết lý nổi tiếng của Python là:

> "Code is read much more often than it is written."

Có nghĩa là:

> Một chương trình được đọc nhiều hơn rất nhiều so với số lần nó được viết.

Đó là lý do Python rất chú trọng đến **sự rõ ràng**.

---

# 2. Python được dùng để làm gì?

Ngày nay Python xuất hiện ở hầu như mọi lĩnh vực.

| Lĩnh vực | Ví dụ |
| --- | --- |
| Web | Flask, FastAPI, Django |
| AI  | Machine Learning, Deep Learning |
| Data Science | Pandas, NumPy |
| Automation | Tự động hóa công việc |
| Web Scraping | Requests, BeautifulSoup |
| DevOps | Docker Script |
| Desktop | PySide6, Flet, Tkinter |
| Game | pygame |
| IoT | Raspberry Pi |
| Cyber Security | Pentest Script |
| API | REST API |

Ví dụ thực tế:

Một công ty thương mại điện tử có thể dùng Python để:

- Crawl giá sản phẩm
- Phân tích dữ liệu bán hàng
- Xây dựng chatbot AI
- Gửi Email tự động
- Tạo báo cáo PDF
- Điều khiển robot kho hàng

---

# 3. Vì sao nên học Python?

Python có cú pháp cực kỳ đơn giản.

Ví dụ:

## C

```text-x-trilium-auto
#include <stdio.h>

int main()
{
    printf("Hello World");
    return 0;
}
```

Python

```text-x-trilium-auto
print("Hello World")
```

Chỉ một dòng.

---

# 4. Python hoạt động như thế nào?

Nhiều người mới nghĩ:

```text-x-trilium-auto
Python
↓

Máy tính
```

Thực tế là:

```text-x-trilium-auto
Code Python

↓

Python Interpreter

↓

Bytecode (.pyc)

↓

Python Virtual Machine (PVM)

↓

Hệ điều hành

↓

CPU
```

Giải thích:

Ví dụ

```text-x-trilium-auto
print("Hello")
```

Khi chạy:

Bước 1

Interpreter đọc code.

↓

Bước 2

Chuyển thành Bytecode.

↓

Bước 3

Python Virtual Machine thực thi Bytecode.

↓

Bước 4

CPU thực hiện.

---

# 5. Compiler và Interpreter

Compiler

```text-x-trilium-auto
Source Code

↓

Compile

↓

Machine Code

↓

Run
```

Ví dụ:

- C
- C++

Interpreter

```text-x-trilium-auto
Source Code

↓

Interpreter

↓

Run ngay
```

Ví dụ:

- Python
- JavaScript

Python là ngôn ngữ thông dịch, nhưng nội bộ vẫn tạo **bytecode** để thực thi hiệu quả hơn.

---

# 6. Cài đặt Python

Khuyến nghị sử dụng phiên bản Python 3.13 hoặc mới hơn (hoặc phiên bản ổn định mới nhất khi bạn cài đặt).

Sau khi cài xong mở Terminal.

Kiểm tra:

```text-x-trilium-auto
python --version
```

hoặc

```text-x-trilium-auto
python3 --version
```

Ví dụ

```text-x-trilium-auto
Python 3.13.2
```

---

# 7. Cài Visual Studio Code

Đây là editor phổ biến nhất hiện nay.

Cài thêm Extension

```text-x-trilium-auto
Python
```

và

```text-x-trilium-auto
Pylance
```

---

# 8. Tạo Project đầu tiên

Ví dụ

```text-x-trilium-auto
python_course/

    lesson01/

        hello.py
```

---

# 9. Chương trình đầu tiên

```text-x-trilium-auto
print("Hello World")
```

Chạy

```text-x-trilium-auto
python hello.py
```

Kết quả

```text-x-trilium-auto
Hello World
```

---

# 10. Hàm print()

Ví dụ

```text-x-trilium-auto
print("Xin chào")
```

```text-x-trilium-auto
print(100)
```

```text-x-trilium-auto
print(3.14)
```

```text-x-trilium-auto
print(True)
```

```text-x-trilium-auto
print(False)
```

---

In nhiều giá trị

```text-x-trilium-auto
print("Tên:", "Nam")
```

Kết quả

```text-x-trilium-auto
Tên: Nam
```

---

Có thể in biến

```text-x-trilium-auto
name = "An"

print(name)
```

---

# 11. Comment

Comment giúp ghi chú.

Một dòng

```text-x-trilium-auto
# Đây là comment

print("Hello")
```

---

Nhiều dòng

```text-x-trilium-auto
"""
Đây là comment
nhiều dòng
"""
```

Lưu ý: Chuỗi ba dấu nháy (`"""..."""`) thực chất là chuỗi nhiều dòng. Khi không gán cho biến hoặc không dùng làm docstring, nó thường được dùng như ghi chú, nhưng để chú thích nhiều dòng trong mã nguồn bạn nên thêm `#` ở từng dòng để rõ ràng hơn.

---

# 12. Quy tắc đặt tên

Đúng

```text-x-trilium-auto
student_name

total_score

user_age
```

Sai

```text-x-trilium-auto
Student Name

123abc

for

class
```

---

Theo chuẩn PEP8

Dùng

```text-x-trilium-auto
snake_case
```

Không dùng

```text-x-trilium-auto
camelCase
```

cho tên biến.

---

# 13. Chạy Python trong Terminal

Có thể chạy trực tiếp.

```text-x-trilium-auto
python
```

Sau đó

```text-x-trilium-auto
>>> print("Hello")
```

Thoát

```text-x-trilium-auto
exit()
```

---

# 14. Đọc lỗi (Error)

Ví dụ

```text-x-trilium-auto
prit("Hello")
```

Kết quả

```text-x-trilium-auto
NameError:
name 'prit' is not defined
```

Không nên hoảng.

Hãy đọc:

```text-x-trilium-auto
NameError
```

và

```text-x-trilium-auto
prit
```

để biết nguyên nhân.

---

Ví dụ

```text-x-trilium-auto
print(
```

Kết quả

```text-x-trilium-auto
SyntaxError
```

Điều này có nghĩa là cú pháp chưa đúng.

---

# 15. Những lỗi người mới thường gặp

Quên dấu ngoặc

```text-x-trilium-auto
print("Hello"
```

Sai tên hàm

```text-x-trilium-auto
Print("Hello")
```

Python phân biệt chữ hoa và chữ thường.

Sai

```text-x-trilium-auto
Print()
```

Đúng

```text-x-trilium-auto
print()
```

---

Quên dấu nháy

```text-x-trilium-auto
print(Hello)
```

Đúng

```text-x-trilium-auto
print("Hello")
```

---

# 16. Ví dụ thực tế

Giả sử bạn viết chương trình chào người dùng.

```text-x-trilium-auto
print("Xin chào Garden!")
```

Hay

```text-x-trilium-auto
print("Chào mừng đến với khóa học Python.")
```

Đây chính là nền tảng để sau này:

- Làm chatbot AI.
- Xây dựng ứng dụng Desktop bằng Flet hoặc PySide6.
- Tạo API với Flask/FastAPI.
- Điều khiển robot hoặc thiết bị IoT.
- Viết công cụ tự động hóa.

---

# 17. Quy tắc viết code chuyên nghiệp

Ngay từ buổi đầu hãy tập các thói quen sau:

- Đặt tên biến có ý nghĩa.
- Viết code dễ đọc hơn là ngắn.
- Mỗi dòng chỉ nên làm một việc.
- Thêm chú thích khi cần giải thích ý tưởng, không chú thích những điều hiển nhiên.
- Tuân thủ chuẩn PEP 8 về khoảng trắng, đặt tên và định dạng mã.

Ví dụ tốt:

```text-x-trilium-auto
message = "Xin chào Python"

print(message)
```

Thay vì:

```text-x-trilium-auto
a = "Xin chào Python"

print(a)
```

---

# 18. Bài tập thực hành

### Bài 1

In ra:

```text-x-trilium-auto
Hello Python
```

---

### Bài 2

In ra:

```text-x-trilium-auto
Tôi đang học Python
```

---

### Bài 3

In ra:

```text-x-trilium-auto
Tên: Nguyễn Văn A
Tuổi: 20
```

---

### Bài 4

In ra:

```text-x-trilium-auto
*****
*****
*****
*****
*****
```

---

### Bài 5

In ra hình tam giác:

```text-x-trilium-auto
*
**
***
****
*****
```

---

### Bài 6

Viết chương trình chỉ gồm các comment mô tả mục tiêu của bạn khi học Python.

---

### Bài 7

Tạo file `about_me.py` và in:

- Họ tên
- Tuổi
- Nghề nghiệp
- Mục tiêu học Python

---

# Mini Project

Tạo chương trình `welcome.py`

Kết quả khi chạy:

```text-x-trilium-auto
====================================
      CHÀO MỪNG ĐẾN VỚI PYTHON
====================================

Hôm nay tôi bắt đầu hành trình trở thành
Python Developer chuyên nghiệp.

Mục tiêu:
- Làm chủ Python
- Xây dựng ứng dụng thực tế
- Trở thành lập trình viên giỏi
```

---

# Tổng kết buổi 1

Bạn đã học được:

- ✅ Python là gì.
- ✅ Python hoạt động như thế nào.
- ✅ Sự khác nhau giữa Compiler và Interpreter.
- ✅ Cài đặt môi trường lập trình.
- ✅ Chạy chương trình Python đầu tiên.
- ✅ Sử dụng `print()`.
- ✅ Viết comment.
- ✅ Quy tắc đặt tên theo PEP 8.
- ✅ Đọc các lỗi cơ bản.
- ✅ Thực hành với các bài tập và mini project.

### Chuẩn bị cho Buổi 2

Ở buổi tiếp theo, chúng ta sẽ đi sâu vào **biến (variables), kiểu dữ liệu (data types), cách Python lưu trữ dữ liệu trong bộ nhớ, quy tắc đặt tên biến, hằng số, ép kiểu và các lỗi thường gặp**, kèm nhiều ví dụ thực tế và bài tập để bạn nắm vững nền tảng lập trình Python.
