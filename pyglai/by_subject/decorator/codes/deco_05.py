from functools import wraps

def gioi_han_luot_goi(so_lan_toi_da):
    # 1. Tạo không gian Enclosing ở đây để đếm số lần đã gọi
    count = 0
    
    def decorator(func):
        # 2. Sử dụng @wraps để giữ danh tính hàm gốc
        @wraps(func)
        def ham_boc(*args, **kwargs):
            # 3. Sử dụng từ khóa nonlocal để cập nhật biến đếm
            # 4. Kiểm tra nếu vượt quá so_lan_toi_da thì báo lỗi
            # 5. Nếu chưa vượt quá thì tăng biến đếm và chạy hàm gốc func()
            nonlocal count
            count += 1
            if count > so_lan_toi_da:
                print("het luot")
                return 
            func(*args,**kwargs)
            
        return ham_boc
    return decorator
# ---- Kiểm tra kết quả ----

@gioi_han_luot_goi(so_lan_toi_da=2)
def tai_video():
    """Hàm giả lập tải video nặng."""
    return "Đang tải video..."
# Test chạy hàm
print(tai_video())  # Lần 1: Thành công! In ra "Đang tải video..."
print(tai_video())  # Lần 2: Thành công! In ra "Đang tải video..."
print(tai_video())  # Lần 3: Bị chặn! Phải in ra: "Lỗi: Bạn đã vượt quá giới hạn 2 lần gọi!"
# Kiểm tra danh tính hàm gốc xem wraps hoạt động đúng chưa
print(tai_video.__name__)  # Phải in ra: "tai_video"