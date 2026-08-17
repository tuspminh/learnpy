Để viết một Decorator có nhận tham số (ví dụ: truyền cấu hình, phân quyền @kiem_tra_quyen("admin") hoặc số lần thử lại @retry(3)), bạn cần thêm một tầng hàm bọc bên ngoài cùng nữa.

Bản chất cấu trúc lúc này sẽ là một hàm 3 tầng lồng nhau:

   1. Tầng ngoài cùng: Nhận tham số truyền vào của Decorator.
   2. Tầng giữa: Nhận hàm gốc cần bọc.
   3. Tầng trong cùng: Nhận các tham số của hàm gốc và thực thi logic.

------------------------------

## 1. Cấu trúc tổng quát của Decorator có tham số

Hãy xem cách xây dựng một Decorator kiểm tra quyền truy cập của người dùng dựa trên tham số được truyền vào:

```
from collections.abc import Callable
from typing import Any

# Biến giả lập thông tin người dùng hiện tại đang đăng nhập hệ thống
USER_HIEN_TAI = {"username": "hoang_an", "quyen": "editor"}

# 🟢 TẦNG 1: Nhận tham số của Decorator
def yeu_cau_quyen(quyen_bat_buoc: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    
    # 🟢 TẦNG 2: Nhận hàm gốc (giống Decorator thông thường)
    def decorator_chinh(ham_goc: Callable[..., Any]) -> Callable[..., Any]:
        
        # 🟢 TẦNG 3: Nhận tham số của hàm gốc và chạy logic
        def ham_boc(*args: Any, **kwargs: Any) -> Any:
            print(f"🔒 Hệ thống đang kiểm tra quyền '{quyen_bat_buoc}'...")
            
            # Kiểm tra xem quyền của user hiện tại có khớp với yêu cầu không
            if USER_HIEN_TAI["quyen"] != quyen_bat_buoc:
                raise PermissionError(f"❌ Truy cập bị từ chối! Bạn cần quyền '{quyen_bat_buoc}'.")
            
            # Nếu thỏa mãn quyền, cho phép hàm gốc chạy
            return ham_goc(*args, **kwargs)
            
        return ham_boc
    return decorator_chinh
```
------------------------------

## 2. Cách sử dụng trong thực tế

Bạn chỉ cần truyền giá trị mong muốn vào ngay sau ký hiệu @:

## Trường hợp 1: Chạy THÀNH CÔNG (User hiện tại là editor)

```
@yeu_cau_quyen("editor")
def chinh_sua_bai_viet(id_bai_viet: int) -> None:
    print(f"📝 Đang chỉnh sửa bài viết số: {id_bai_viet}")

# Gọi hàm
chinh_sua_bai_viet(101)

# Kết quả hiển thị:
# 🔒 Hệ thống đang kiểm tra quyền 'editor'...
# 📝 Đang chỉnh sửa bài viết số: 101
```

## Trường hợp 2: Bị CHẶN LỖI (Hàm yêu cầu quyền admin)

```
@yeu_cau_quyen("admin")
def xoa_nguoi_dung(username: str) -> None:
    print(f"🗑️ Đã xóa người dùng: {username}")

# Gọi hàm
xoa_nguoi_dung("nguyen_b")

# Kết quả hiển thị:
# 🔒 Hệ thống đang kiểm tra quyền 'admin'...
# ❌ PermissionError: Truy cập bị từ chối! Bạn cần quyền 'admin'.
```
------------------------------

## 3. Một mẹo bắt buộc: Dùng functools.wraps

Khi bạn dùng Decorator bọc một hàm, Python sẽ vô tình làm thay đổi thông tin định danh (tên hàm __name__, docstring __doc__) của hàm gốc thành thông tin của ham_boc. Để giữ nguyên các thông tin gốc này (giúp ích cho việc debug), bạn luôn nên import @wraps từ thư viện functools để bọc lên ham_boc.

## Cách viết chuẩn công nghiệp (Production-ready):

```
from functools import wraps
from collections.abc import Callable
from typing import Any

def my_decorator_co_tham_so(tham_so: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(ham_goc: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(ham_goc) # 👈 Giữ nguyên tên và thông tin của hàm gốc
        def ham_boc(*args: Any, **kwargs: Any) -> Any:
            # Viết logic ở đây
            return ham_goc(*args, **kwargs)
        return ham_boc
    return decorator
```
Đến đây bạn đã nắm trọn vẹn từ bản chất Decorator cơ bản, cách xử lý đa tham số *args, **kwargs, cho tới Decorator 3 tầng nhận tham số nâng cao.

Bạn có muốn làm một bài tập nhỏ thực hành tự viết một Decorator có tham số (ví dụ: tự động thử lại hàm @retry(so_lan=3) khi gặp lỗi mạng) để chốt lại phần kiến thức nâng cao này không?

