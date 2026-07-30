LEVEL 1 - BÀI 2: Kiểu dữ liệu, Toán tử & Ép kiểu

Đây là bài quan trọng nhất để không bị bug ngớ ngẩn sau này.
1. 4 Kiểu dữ liệu gốc

Trong Python mọi thứ đều là object, nhưng có 4 ông tổ:
Python

tuoi = 25          # int - số nguyên
gia = 19.99        # float - số thực
ten = "Hùng"       # str - chuỗi
is_dev = True      # bool - True / False (viết hoa chữ đầu)
khong_co_gi = None # None - rỗng, chưa có gì

Dùng type() để soi nó.
2. Toán tử - 3 nhóm phải thuộc

a) Toán học:
+ - * / bình thường.
Cái khác biệt:
// chia lấy phần nguyên: 7 // 2 = 3
% chia lấy dư: 7 % 2 = 1 (dùng cực nhiều để kiểm tra chẵn lẻ)
** lũy thừa: 2 ** 3 = 8

b) So sánh - luôn trả về True/False:
== bằng, != khác, > < >= <=

c) Logic - để nối các điều kiện:
and (và), or (hoặc), not (phủ định)
Python

tuoi = 20
co_bang_lai = True
duoc_lai_xe = tuoi >= 18 and co_bang_lai # True

3. Ép kiểu (Type Casting) - Chỗ 90% newbie lỗi

input() luôn trả về str dù bạn gõ số. Đây là lý do:
Python

# SAI
# tuoi = input("Nhập tuổi: ") # bạn gõ 25
# print(tuoi + 5) -> Lỗi! "25" + 5 không được

# ĐÚNG
tuoi_str = input("Nhập tuổi: ")
tuoi = int(tuoi_str) # ép từ str -> int
print(tuoi + 5)

# Các hàm ép kiểu:
int("25") -> 25
float("3.14") -> 3.14
str(25) -> "25"
bool(0) -> False, bool(1) -> True, bool("") -> False

    Quy tắc ngầm: 0, "", None, [] khi ép qua bool sẽ thành False. Còn lại là True. Cái này sau này viết if rất gọn.

4. Code mẫu chuẩn
Python

# Tính tiền ship
gia_goc = float(input("Giá sản phẩm: "))
so_luong = int(input("Số lượng: "))

tong = gia_goc * so_luong
duoc_freeship = tong >= 300000

print(f"Tổng: {tong} VND")
print(f"Được freeship? {duoc_freeship}")

BÀI TẬP BÀI 2

Bài 2.1 (Bắt buộc): Máy tính BMI
Hỏi người dùng cân nặng (kg) và chiều cao (m).
Công thức: BMI = cân nặng / (chiều cao ** 2)
In ra BMI làm tròn 2 chữ số thập phân. Dùng round(bmi, 2)

Bài 2.2 (Tư duy logic):
Một năm nhuận nếu chia hết cho 400, HOẶC chia hết cho 4 nhưng KHÔNG chia hết cho 100.
Hỏi người dùng 1 năm, in ra True nếu là năm nhuận, False nếu không.
Chỉ dùng 1 dòng print() với biểu thức logic. Không dùng if (chưa học).

Gợi ý công thức: (nam % 400 == 0) or (...)

Code xong dán lên đây, mình review.