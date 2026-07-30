Tới Bài 7 - bài cuối của Core Python. Xong bài này bạn đã có thể viết tool thực sự để bán hoặc dùng cho công việc.
LEVEL 4 - BÀI 7: Xử lý Lỗi, File & OOP Cơ bản
1. Xử lý lỗi try-except - Đừng để chương trình chết

User luôn nhập bậy. File luôn có thể không tồn tại. Dev pro không để chương trình crash.
Python

# Cách gà: để crash
# tuoi = int(input("Nhập tuổi: ")) # user gõ "abc" -> crash

# Cách pro: bọc lại
try:
    tuoi = int(input("Nhập tuổi: "))
    print(f"Bạn {tuoi} tuổi")
except ValueError:
    print("Bạn phải nhập số!")
except Exception as e:
    print(f"Lỗi không ngờ: {e}")
else:
    print("Không lỗi thì chạy vào đây")
finally:
    print("Dù lỗi hay không, finally luôn chạy - dùng để đóng file")

2. Làm việc với File - with open là chân lý

Luôn dùng with open, đừng bao giờ dùng open() rồi quên close().
Python

# Ghi file
with open("data.txt", "w", encoding="utf-8") as f:
    f.write("Học Python\n")
    f.write("Bài 7\n")

# Đọc file
try:
    with open("data.txt", "r", encoding="utf-8") as f:
        noi_dung = f.read()
        print(noi_dung)

        # Đọc từng dòng
        # for dong in f:
        # print(dong.strip())
except FileNotFoundError:
    print("File không tồn tại")

# Đọc/ghi JSON (90% công việc là JSON)
import json

data = {"ten": "Hùng", "diem": [8,9,10]}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open("data.json", "r", encoding="utf-8") as f:
    data_doc = json.load(f)

3. OOP - Lập trình Hướng Đối Tượng

Khi Dict không đủ, bạn cần Class. Class là bản thiết kế, Object là sản phẩm tạo ra từ bản thiết kế đó.
Python

class SinhVien:
    # Hàm khởi tạo - chạy đầu tiên khi tạo object
    def __init__(self, ten: str, tuoi: int):
        self.ten = ten
        self.tuoi = tuoi
        self.diem = [] # thuộc tính riêng của mỗi object

    # Phương thức (method) - hành động
    def them_diem(self, diem: float):
        if 0 <= diem <= 10:
            self.diem.append(diem)

    def diem_trung_binh(self) -> float:
        if not self.diem:
            return 0.0
        return sum(self.diem) / len(self.diem)

    # Hàm đặc biệt để in object cho đẹp
    def __str__(self):
        return f"SinhVien(ten={self.ten}, GPA={self.diem_trung_binh():.2f})"

# Sử dụng
sv1 = SinhVien("Hùng", 25)
sv1.them_diem(9)
sv1.them_diem(8.5)
print(sv1) # SinhVien(ten=Hùng, GPA=8.75)
print(sv1.diem_trung_binh())

Tại sao dùng OOP?

    Gộp dữ liệu + hành động vào 1 chỗ
    Dễ quản lý khi có 1000 sinh viên, không phải tạo 1000 dict rời rạc

MINI PROJECT BÀI 7 - BẮT BUỘC

Đây là project tổng hợp toàn bộ Level 0-4. Làm được là bạn đã hơn 70% người tự học.

Yêu cầu: Quản lý chi tiêu cá nhân lưu ra file

Viết chương trình quan_ly_chi_tieu.py với Class:
Python

class QuanLyChiTieu:
    def __init__(self, file_path="chi_tieu.json"):...
    def them_khoan_chi(self, ten, so_tien, loai):...
    def xem_bao_cao(self): # in tổng chi, chi theo loại
    def luu_file(self): # lưu ra json
    def doc_file(self): # đọc từ json khi khởi động

Menu:
Code

1. Thêm khoản chi
2. Xem báo cáo
3. Thoát và Lưu

Phải có:

    try-except khi nhập số tiền
    Lưu/đọc JSON bằng with open
    Dùng List hoặc List bên trong[Dict][Object]

Đây là project bạn có thể bỏ vào CV khi ghi "Biết Python cơ bản".

Bạn code xong project này gửi mình file .py. Mình sẽ review chi tiết: cấu trúc file, xử lý lỗi, có clean code không.

Xong bài này là hết phần CORE. Bài tiếp theo Bài 8: Git, Venv, Pip - Lên trình Dev chuyên nghiệp - bài mà công ty nào cũng yêu cầu.