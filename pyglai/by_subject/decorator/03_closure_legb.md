Dưới đây là chi tiết về toàn bộ quy tắc LEGB và ví dụ thực tế của Closure để bảo mật dữ liệu.
------------------------------
## 1. Quy tắc LEGB trong Python
Khi bạn gọi một biến, Python sẽ tìm kiếm theo đúng thứ tự 4 phạm vi từ trong ra ngoài (LEGB). Nếu không tìm thấy ở cả 4 tầng, hệ thống sẽ báo lỗi NameError.

  [ L ] Local (Trong hàm hiện tại)
    ↓
  [ E ] Enclosing (Hàm cha bao quanh)
    ↓
  [ G ] Global (Toàn bộ file script)
    ↓
  [ B ] Built-in (Hàm có sẵn của Python)

## Chi tiết từng phạm vi:

* Local (L): Biến khai báo bên trong hàm. Định nghĩa ở đâu thì chỉ dùng được ở đó.
* Enclosing (E): Biến thuộc hàm cha (outer), nằm ngoài hàm con (inner) như đã giải thích.
* Global (G): Biến khai báo ở tầng cao nhất của file .py, mọi hàm đều nhìn thấy.
* Built-in (B): Các từ khóa/hàm mặc định của Python (Ví dụ: print, len, int).

## Ví dụ minh họa LEGB:
```
x = "Global X"  # [G] Global
def ham_cha():
    x = "Enclosing X"  # [E] Enclosing
    
    def ham_con():
        x = "Local X"  # [L] Local
        print(x)       # Tìm thấy [L] đầu tiên -> In ra: Local X
        print(len(x))  # Tìm [L]->[E]->[G] không có 'len' -> Lấy [B] Built-in (hàm len)
        
    ham_con()

ham_cha()
```
------------------------------
## 2. Ứng dụng Closure thực tế: Bảo mật mật khẩu
Closure thường được dùng để che giấu dữ liệu (Encapsulation), không cho code bên ngoài can thiệp hoặc chỉnh sửa biến gốc một cách trái phép.
```
def khoi_tao_tai_khoan(mat_khau_goc):
    # Biến 'mat_khau_goc' nằm ở phạm vi Enclosing
    so_lan_nhap_sai = 0 
    
    def xac_thuc(mat_khau_nhap):
        nonlocal so_lan_nhap_sai  # Sửa đổi biến ở Enclosing scope
        
        if so_lan_nhap_sai >= 3:
            return "Tài khoản đã bị khóa do nhập sai quá 3 lần!"
            
        if mat_khau_nhap == mat_khau_goc:
            so_lan_nhap_sai = 0 # Reset nếu đúng
            return "Đăng nhập thành công!"
        else:
            so_lan_nhap_sai += 1
            return f"Sai mật khẩu! (Sai {so_lan_nhap_sai}/3 lần)"
            
    return xac_thuc  # Trả về hàm con (Tạo thành Closure)

# ---- Cách sử dụng ----
# Tạo một tài khoản mới với mật khẩu là "Admin123"
dang_nhap = khoi_tao_tai_khoan("Admin123")

# Biến 'mat_khau_goc' hiện tại hoàn toàn bị ẩn, không thể truy cập từ bên ngoài.# Bạn chỉ có thể tương tác thông qua hàm closure 'dang_nhap':
print(dang_nhap("1111"))     # Kết quả: Sai mật khẩu! (Sai 1/3 lần)
print(dang_nhap("2222"))     # Kết quả: Sai mật khẩu! (Sai 2/3 lần)
print(dang_nhap("Admin123")) # Kết quả: Đăng nhập thành công!
```
------------------------------
Nếu bạn muốn tiếp tục nâng cao tay nghề, tôi có thể hướng dẫn:

* Cách ứng dụng Closure để viết Decorator (một tính năng cực mạnh trong Python).
* Cách kiểm tra các biến đang nằm trong Closure bằng thuộc tính ẩn __closure__.

Bạn muốn chuyển sang học Decorator hay xem cách Python lưu biến closure trong bộ nhớ?

