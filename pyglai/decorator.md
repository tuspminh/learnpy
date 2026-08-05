Decorator là một trong những tính năng mạnh mẽ và phổ biến nhất của Python. Bản chất của Decorator chính là một Closure nhận đầu vào là một hàm và trả về một hàm khác đã được nâng cấp tính năng.
Nó giúp bạn chỉnh sửa hoặc thêm tính năng cho một hàm có sẵn mà không cần sửa bất kỳ dòng code nào bên trong hàm đó.
------------------------------
## 1. Cách Decorator hoạt động (Bản chất Closure)
Hãy xem cách tạo ra một Decorator thủ công bằng kiến thức Closure bạn vừa học:

# Đây là Decorator (Hàm cha nhận vào một hàm khác)def bo_trang_tri(ham_goc):
    
    # Hàm con đóng vai trò bọc hàm gốc lại
    def ham_boc():
        print("[Trước] Thực hiện kiểm tra hệ thống...") # Tính năng thêm vào
        ham_goc() # Gọi hàm gốc (Được lưu trong Enclosing scope)
        print("[Sau] Ghi nhật ký (Log) hoàn tất!")      # Tính năng thêm vào
        
    return ham_boc # Trả về closure
def chao_xin():
    print("Xin chào người dùng!")
# Áp dụng decorator thủ côngchao_xin_nang_cap = bo_trang_tri(chao_xin)
chao_xin_nang_cap()

------------------------------
## 2. Ký pháp @ (Syntactic Sugar)
Để code gọn gàng hơn, Python cung cấp ký pháp @ đặt ngay trên đầu hàm cần nâng cấp. Cách này hoàn toàn tương đương với cách viết thủ công ở trên.

def bo_trang_tri(ham_goc):
    def ham_boc():
        print("[Trước] Kiểm tra quyền truy cập...")
        ham_goc()
        print("[Sau] Đóng kết nối.")
    return ham_boc
# Dùng ký pháp @ để áp dụng decorator
@bo_trang_tridef lay_du_lieu():
    print("-> Đang tải dữ liệu từ Database...")
# Gọi hàm như bình thường, tính năng mới tự động chạy
lay_du_lieu()

------------------------------
## 3. Ứng dụng thực tế: Tính thời gian chạy hàm
Trong thực tế, Decorator được dùng rất nhiều để đo hiệu năng (thời gian chạy) của các hàm trong hệ thống.

import time
def tinh_thoi_gian(ham_goc):
    # Dùng *args và **kwargs để hàm bọc nhận mọi tham số của hàm gốc
    def ham_boc(*args, **kwargs):
        bat_dau = time.time()
        
        ket_qua = ham_goc(*args, **kwargs) # Chạy hàm gốc
        
        ket_thuc = time.time()
        print(f"Hàm '{ham_goc.__name__}' chạy mất: {ket_thuc - bat_dau:.6f} giây")
        return ket_qua
        
    return ham_boc

@tinh_thoi_giandef xu_ly_vong_lap(n):
    tong = 0
    for i in range(n):
        tong += i
    return tong
# Chạy thử nghiệm
xu_ly_vong_lap(10000000)

------------------------------
Đến đây bạn đã đi trọn vẹn lộ trình từ Enclosing Scope -> Nonlocal -> Closure -> Decorator.
Nếu bạn muốn tiếp tục nâng cao chuyên sâu, tôi có thể hướng dẫn:

* Cách viết Decorator nhận tham số (Ví dụ: @phanquyen("admin")).
* Cách dùng thư viện functools.wraps để giữ lại danh tính (tên, docstring) của hàm gốc sau khi bị trang trí.

Hãy cho tôi biết bạn muốn tìm hiểu phần nào tiếp theo!
