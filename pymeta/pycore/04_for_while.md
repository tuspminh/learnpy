LEVEL 1 - BÀI 4: Vòng lặp for và while

Nếu if là ra quyết định, thì vòng lặp là bắt máy tính làm việc cật lực thay bạn.
1. for - Lặp khi biết trước số lần

Đây là vòng lặp bạn sẽ dùng 80% thời gian.

a) range() - Kẻ tạo dãy số:
Python

range(5)       # 0,1,2,3,4
range(1, 6)    # 1,2,3,4,5
range(1, 10, 2)# 1,3,5,7,9 (bước nhảy 2)

b) Cú pháp chuẩn:
Python

# In 3 lần "Học Python"
for i in range(3):
    print(f"Lần {i}: Học Python")

# Duyệt chuỗi
for ky_tu in "Python":
    print(ky_tu)

2. while - Lặp khi chưa biết khi nào dừng

Dùng khi đợi điều kiện xảy ra. CỰC KỲ NGUY HIỂM nếu quên điều kiện dừng -> treo máy.
Python

mat_khau_dung = "123456"
nhap = ""

while nhap != mat_khau_dung:
    nhap = input("Nhập lại mật khẩu: ")

print("Đăng nhập thành công!")

3. 2 vũ khí điều khiển vòng lặp

Đây là thứ phân biệt code gà và code pro:

    break: Phá vòng lặp, thoát ngay lập tức
    continue: Bỏ qua lần lặp hiện tại, nhảy tới lần sau

Python

# Tìm số đầu tiên chia hết cho 7 trong 1-20
for i in range(1, 21):
    if i % 7 == 0:
        print(f"Tìm thấy: {i}")
        break # thấy rồi thì nghỉ, không cần chạy tiếp

# In số lẻ
for i in range(10):
    if i % 2 == 0:
        continue # chẵn thì bỏ qua
    print(i) # chỉ in lẻ

4. Vòng lặp lồng nhau & else của vòng lặp

Một trick ít ai dạy: vòng lặp có else
Python

# Kiểm tra số nguyên tố
n = 13
for i in range(2, n):
    if n % i == 0:
        print(f"{n} không phải số nguyên tố")
        break
else:
    # else này chỉ chạy nếu vòng for KHÔNG bị break
    print(f"{n} là số nguyên tố")

BÀI TẬP BÀI 4 - QUAN TRỌNG

Bài 4.1 (Bắt buộc): FizzBuzz - Câu hỏi phỏng vấn huyền thoại
In từ 1 đến 100:

    Nếu chia hết cho 3 in "Fizz"
    Chia hết cho 5 in "Buzz"
    Chia hết cho cả 3 và 5 in "FizzBuzz"
    Còn lại in số đó

Bài 4.2 (Bắt buộc): Tính tổng
Hỏi người dùng nhập n. Tính S = 1 + 2 + ... + n và S2 = 1^2 + 2^2 + ... + n^2. Dùng cả for và công thức toán để so sánh.

Bài 4.3 (Nâng cao - Ra dáng dev):
Vẽ hình chữ nhật rỗng bằng *
Nhập cao=5, rong=10 in ra:
Code

**********
*        *
*        *
*        *
**********

Gợi ý: Dùng 2 vòng for lồng nhau + if kiểm tra biên.

Bạn làm 3 bài này xong là đã xong 80% tư duy lập trình cơ bản. Xong gửi mình, mình review rồi qua Bài 5: List, Dict - nơi Python mạnh nhất.