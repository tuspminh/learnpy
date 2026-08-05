Đây là một bài tập thực tế kết hợp toàn bộ các kiến thức bạn đã học từ Enclosing, Closure, Nonlocal cho đến Advanced Decorator.
------------------------------
## 📋 Đề bài: Hệ thống giới hạn lượt gọi hàm (Rate Limiter)
Trong thực tế, các API hoặc hệ thống mạng thường giới hạn số lần một người dùng được gọi hàm trong một khoảng thời gian để tránh bị phá hoại (gọi là Rate Limiting).
Nhiệm vụ của bạn: Viết một decorator có tham số tên là @gioi_han_luot_goi(so_lan_toi_da).

* Decorator này sẽ giới hạn số lần một hàm được phép chạy.
* Nếu vượt quá số lần cấu hình, hàm sẽ không chạy nữa mà trả về thông báo lỗi.

## Code mẫu định hình (Bạn hãy điền code vào phần ...):

from functools import wraps
def gioi_han_luot_goi(so_lan_toi_da):
    # 1. Tạo không gian Enclosing ở đây để đếm số lần đã gọi
    ...
    
    def decorator(func):
        # 2. Sử dụng @wraps để giữ danh tính hàm gốc
        ...
        def ham_boc(*args, **kwargs):
            # 3. Sử dụng từ khóa nonlocal để cập nhật biến đếm
            # 4. Kiểm tra nếu vượt quá so_lan_toi_da thì báo lỗi
            # 5. Nếu chưa vượt quá thì tăng biến đếm và chạy hàm gốc func()
            ...
            
        return ham_boc
    return decorator
# ---- Kiểm tra kết quả ----

@gioi_han_luot_goi(so_lan_toi_da=2)def tai_video():
    """Hàm giả lập tải video nặng."""
    return "Đang tải video..."
# Test chạy hàm
print(tai_video())  # Lần 1: Thành công! In ra "Đang tải video..."
print(tai_video())  # Lần 2: Thành công! In ra "Đang tải video..."
print(tai_video())  # Lần 3: Bị chặn! Phải in ra: "Lỗi: Bạn đã vượt quá giới hạn 2 lần gọi!"
# Kiểm tra danh tính hàm gốc xem wraps hoạt động đúng chưa
print(tai_video.__name__)  # Phải in ra: "tai_video"

------------------------------
Gợi ý nhỏ: Bạn cần một biến đếm (ví dụ: luot_da_goi = 0) nằm ở tầng hàm phù hợp để làm biến Enclosing cho ham_boc cập nhật.
Bạn hãy thử viết code giải bài tập này. Khi nào xong, hãy gửi code của bạn qua đây để chúng ta cùng check và tối ưu nhé!
