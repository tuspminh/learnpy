Vào Bài 6. Từ bài này trở đi, bạn không còn viết code kiểu "mì tôm" - viết từ trên xuống dưới nữa. Bạn sẽ viết code như kiến trúc sư.
LEVEL 3 - BÀI 6: Hàm (Function) - Chia để trị
1. Tại sao phải viết hàm?

3 lý do duy nhất:

    DRY - Don't Repeat Yourself: Đừng copy-paste. Viết 1 lần, dùng 100 lần.
    Dễ đọc: tinh_tien_dien(kwh) dễ hiểu hơn 20 dòng if else.
    Dễ test: Test 1 hàm dễ hơn test cả chương trình 500 dòng.

2. Cú pháp chuẩn Pro
Python

def ten_ham(tham_so1, tham_so2) -> kieu_tra_ve:
    """Docstring: Mô tả hàm làm gì"""
    # logic
    return ket_qua

# Ví dụ chuẩn PEP8 + Type Hint + Docstring
def tinh_bmi(can_nang: float, chieu_cao: float) -> float:
    """
    Tính chỉ số BMI.

    Args:
        can_nang (float): kg
        chieu_cao (float): mét

    Returns:
        float: chỉ số BMI
    """
    if chieu_cao <= 0:
        return 0.0
    return can_nang / (chieu_cao ** 2)

# Gọi hàm
bmi = tinh_bmi(70, 1.75)

Quy tắc đặt tên: snake_case, động từ + danh từ: tinh_tong(), kiem_tra_snt(), lay_du_lieu()
3. 4 loại tham số - Phải nắm
Python

def ham_mau(a, b=10, *args, **kwargs):
    print(f"a={a}, b={b}")
    print(f"args (tuple thừa): {args}")
    print(f"kwargs (dict thừa): {kwargs}")

# a là bắt buộc (positional)
# b=10 là default - không truyền thì lấy 10
# *args gom các giá trị thừa thành tuple
# **kwargs gom các key=value thừa thành dict

ham_mau(1) # a=1, b=10
ham_mau(1, 2, 3, 4, ten="Hùng", tuoi=25)
# a=1, b=2, args=(3,4), kwargs={'ten':'Hùng', 'tuoi':25}

Đây là cách các thư viện lớn như print() hoạt động: print(*objects, sep=' ', end='\n')
4. Scope & return - 2 chỗ dễ bug nhất
Python

x = 10 # global

def ham():
    x = 5 # local, khác x bên ngoài
    return x

print(ham()) # 5
print(x) # vẫn là 10

# return: Hàm gặp return là DỪNG ngay, trả kết quả
def kiem_tra_chan_le(n):
    if n % 2 == 0:
        return True
    return False # không cần else vì trên đã return rồi

5. Lambda - Hàm 1 dòng

Chỉ dùng khi cần hàm siêu ngắn.
Python

# Thay vì
def nhan_doi(x): return x*2

# Viết
nhan_doi = lambda x: x*2

# Dùng nhiều nhất với sort
ds = [{"ten":"A", "diem":8}, {"ten":"B", "diem":9}]
ds_sorted = sorted(ds, key=lambda sv: sv["diem"], reverse=True)

BÀI TẬP BÀI 6

Bài 6.1 (Bắt buộc): Viết lại các bài cũ thành hàm

    def la_nam_nhuan(nam: int) -> bool
    def la_so_nguyen_to(n: int) -> bool
    def tinh_tien_dien(kwh: int) -> int
    Mỗi hàm có docstring đầy đủ.

Bài 6.2 (Bắt buộc): Hàm linh hoạt
Viết hàm def thong_ke(*args, **kwargs)

    Nhận vào bao nhiêu số cũng được (args)
    In ra: số lượng số, tổng, trung bình, max, min
    Nếu kwargs có lam_tron=True thì làm tròn kết quả

Ví dụ: thong_ke(1,2,3,4, lam_tron=True)

Bài 6.3 (Nâng cao - Dùng nhiều khi đi làm):
Viết hàm def loc_san_pham(danh_sach_sp: list, gia_min: float = 0) -> list
Dùng list comprehension + lambda để lọc ra sản phẩm có gia >= gia_min và ton > 0.

Bạn làm xong gửi mình 3 hàm. Mình sẽ review theo tiêu chuẩn code review ở công ty: có type hint không, có docstring không, tên hàm có rõ nghĩa không.

Xong bài này là tới Bài 7: File, Lỗi, OOP - Viết chương trình thực sự có ích.