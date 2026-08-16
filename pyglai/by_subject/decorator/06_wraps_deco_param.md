Dưới đây là hai mảnh ghép cuối cùng để bạn làm chủ hoàn toàn Decorator trong Python: Giữ danh tính hàm gốc và Tạo Decorator có tham số.
------------------------------
## 1. Giữ danh tính hàm gốc bằng functools.wraps
Khi bạn bọc một hàm gốc bằng một Decorator, bản chất là bạn đã thay thế hàm gốc bằng ham_boc. Điều này làm mất đi danh tính thực sự (như tên hàm __name__ hoặc tài liệu hướng dẫn __doc__) của hàm gốc.
Để giải quyết vấn đề này, Python cung cấp @wraps từ thư viện functools.
## Lỗi nếu không dùng wraps:
```
def decorator_loi(func):
    def ham_boc():
        return func()
    return ham_boc

@decorator_loidef ham_cua_toi():
    """Đây là tài liệu hướng dẫn của hàm."""
    pass

print(ham_cua_toi.__name__) # Kết quả bị sai: 'ham_boc'
print(ham_cua_toi.__doc__)  # Kết quả bị sai: None
```
## Cách sửa đúng với functools.wraps:
```
from functools import wraps
def decorator_chuan(func):
    @wraps(func) # <--- Sao chép tên và docstring của func sang ham_boc
    def ham_boc():
        return func()
    return ham_boc

@decorator_chuandef ham_cua_toi():
    """Đây là tài liệu hướng dẫn của hàm."""
    pass

print(ham_cua_toi.__name__) # Kết quả chuẩn: 'ham_cua_toi'
print(ham_cua_toi.__doc__)  # Kết quả chuẩn: 'Đây là tài liệu hướng dẫn của hàm.'
```
------------------------------
## 2. Viết Decorator nhận tham số (Ví dụ: Phân quyền)
Khi bạn muốn truyền tham số vào Decorator (ví dụ: @phan_quyen("admin")), cấu trúc Closure sẽ cần thêm một tầng hàm ngoài cùng để nhận tham số đó. Tổng cộng chúng ta sẽ có 3 tầng hàm lồng nhau.
```
from functools import wraps
# Tầng 1: Nhận tham số của Decorator
def phan_quyen(quyen_yeu_cau):
    
    # Tầng 2: Nhận hàm gốc (đây chính là decorator chuẩn)
    def decorator(func):
        
        # Tầng 3: Nhận tham số của hàm gốc và thực thi
        @wraps(func)
        def ham_boc(user_role, *args, **kwargs):
            if user_role != quyen_yeu_cau:
                return f"Lỗi: Quyền '{user_role}' không được phép truy cập chức năng này!"
            return func(user_role, *args, **kwargs)
            
        return ham_boc
    return decorator
# ---- Cách sử dụng ----

@phan_quyen("admin")
def xoa_nguoi_dung(user_role, user_id):
    return f"Đã xóa thành công người dùng {user_id}."

@phan_quyen("editor")
def viet_bai(user_role, tieu_de):
    return f"Đã đăng bài viết: {tieu_de}"

# Kiểm tra thực tế
print(xoa_nguoi_dung("guest", 42))     # Kết quả: Lỗi: Quyền 'guest' không được phép...
print(xoa_nguoi_dung("admin", 42))     # Kết quả: Đã xóa thành công người dùng 42.

print(viet_bai("editor", "Học Python")) # Kết quả: Đã đăng bài viết: Học Python
```
------------------------------
## Tổng kết chuỗi kiến thức bạn đã học

   1. Enclosing Scope: Không gian lưu trữ của hàm cha bao quanh hàm con.
   2. Nonlocal: Từ khóa để sửa đổi biến ở không gian Enclosing.
   3. Closure: Hàm con "đóng gói" và mang theo biến Enclosing ngay cả khi hàm cha đã chết (lưu dưới dạng Cell Object).
   4. Decorator: Ứng dụng nâng cao của Closure để "trang trí", thêm tính năng cho hàm khác.
   5. Advanced Decorator: Dùng @wraps giữ danh tính và lồng 3 tầng hàm để truyền tham số cho Decorator.

Nếu bạn muốn rèn luyện thêm, tôi có thể đưa ra một bài tập thử thách nhỏ kết hợp toàn bộ các kiến thức trên để bạn tự giải. Bạn có muốn thử sức không?

