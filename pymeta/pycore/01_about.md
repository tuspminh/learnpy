Rồi, vào LEVEL 0 - BÀI 1: Tư duy & Setup chuẩn Dev

Bài này xong là bạn đã có tư duy của lập trình viên, không phải người học vẹt.
1. Mục tiêu của Bài 1

Sau bài này bạn sẽ:

    Hiểu Python chạy như thế nào (không phải ma thuật)
    Cài đặt bộ đồ nghề chuẩn đi làm
    Chạy được chương trình đầu tiên và hiểu 3 khái niệm: Biến, Kiểu dữ liệu, Hàm print() / input()

2. Tư duy cốt lõi: Máy tính nghĩ gì?

Đừng nghĩ code là tiếng Anh. Hãy nghĩ nó là công thức nấu ăn:

    Biến (variable) = cái hộp có nhãn, để đồ bên trong
    Hàm (function) = cái máy, bỏ nguyên liệu vào -> ra sản phẩm
    Chương trình = 1 dãy các mệnh lệnh sắp xếp theo thứ tự

Python là ngôn ngữ thông dịch. Bạn gõ -> Python đọc từng dòng và dịch cho máy tính làm ngay. Nên nó cực dễ debug.
3. Setup đồ nghề (Làm 1 lần cho chuẩn)

Bước 1: Cài Python
Vào python.org -> Download Python 3.12.x. QUAN TRỌNG: Lúc cài đặt trên Windows, nhớ tick vào Add python.exe to PATH.
Kiểm tra: mở Terminal / CMD gõ:
Bash

python --version

Ra Python 3.12.x là ok.

Bước 2: Cài VS Code
Vào code.visualstudio.com tải VS Code. Vào VS Code -> Extensions -> cài 2 cái này:

    Python (của Microsoft)
    Pylance

Bước 3: Tạo dự án đầu tiên đúng chuẩn
Đừng bao giờ code ngoài Desktop. Làm như dev:

    Tạo thư mục D:\hoc-python hoặc ~/hoc-python
    Mở VS Code -> File -> Open Folder -> chọn thư mục đó
    Trong VS Code mở Terminal (Ctrl + `) gõ:

Bash

python -m venv venv

Đây là tạo môi trường ảo, để sau này không bị loạn thư viện. Đây là thói quen của pro.
4. Tạo file main.py

Bạn đang dùng Windows hay Mac? Nếu làm tới đây bị kẹt thì chụp màn hình lỗi gửi mình.
4. Code đầu tiên - Hiểu thật sâu

Dán code này vào main.py:
Python

# Bài 1: Biến là chiếc hộp

# 1. Khai báo biến - tạo hộp và bỏ đồ vào
ten = "Hùng"
tuoi = 25
chieu_cao = 1.75
dang_hoc_python = True

# 2. Hàm print() - in ra màn hình
print("Xin chào:", ten)
print(f"Bạn {ten} năm nay {tuoi} tuổi") # f-string là cách in hiện đại nhất

# 3. Hàm input() - hỏi người dùng
ten_ban = input("Bạn tên là gì? ")
print(f"Rất vui được gặp {ten_ban}!")

# 4. Kiểm tra kiểu dữ liệu
print(type(ten), type(tuoi), type(chieu_cao))

Bấm F5 hoặc nút ▶️ trên góc phải để chạy.

Giải thích pro:

    ten = "Hùng" : Dấu = không phải là "bằng", nó là phép gán - "đưa giá trị vào hộp".
    Python tự hiểu kiểu dữ liệu, không cần khai báo string ten như ngôn ngữ khác.
    f"..." gọi là f-string, dùng 99% khi đi làm.

5. Bài tập về nhà - BẮT BUỘC CODE

Không làm thì không qua bài 2 được. Chỉ 2 bài thôi:

Bài 1.1 (Cơ bản): Viết chương trình hỏi:

    Tên, năm sinh
    Rồi in ra: "Chào [Tên], bạn [tuổi] tuổi"
    Gợi ý: tuổi = 2026 - năm sinh. Nhớ int() để đổi chữ thành số.

Bài 1.2 (Tư duy): Đổi chỗ 2 biến không dùng biến thứ 3.
Python

a = 5
b = 10
# viết code ở đây để sau đó a=10, b=5
print(a, b)

Đây là câu phỏng vấn intern hay ra.

Làm xong dán code của bạn vào đây. Mình sẽ review code như review code của junior trong công ty - soi cả cách đặt tên biến, PEP8.

Bạn code xong bài nào thì gửi mình bài đó nhé.