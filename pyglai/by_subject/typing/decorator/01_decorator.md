Trong Python, Decorator (Bộ trang trí) là một công cụ cực kỳ mạnh mẽ cho phép bạn thay đổi hoặc mở rộng hành vi của một hàm (hoặc class) mà không cần phải sửa đổi trực tiếp mã nguồn bên trong hàm đó.

Để hiểu một cách đơn giản nhất: Decorator giống như một lớp vỏ bọc (wrapper). Nó bọc xung quanh hàm gốc, chạy một số đoạn code trước khi hàm gốc chạy, và chạy một số đoạn code sau khi hàm gốc kết thúc.

------------------------------

## 1. Nguyên lý cốt lõi: Hàm cũng là đối tượng (First-class functions)

Để hiểu được Decorator, bạn cần nhớ rằng trong Python, hàm được đối xử như một biến thông thường. Nghĩa là bạn có thể:

* Gán một hàm vào một biến.
* Truyền một hàm vào làm tham số của một hàm khác.
* Khai báo một hàm nằm bên trong một hàm khác (hàm lồng nhau).
* Trả về một hàm từ một hàm khác.


------------------------------

## 2. Cấu trúc cơ bản của một Decorator

Một Decorator thực chất là một hàm nhận đầu vào là một hàm khác, và trả về một hàm đã được "nâng cấp".

#### Ví dụ: Tạo một decorator tự động thông báo trước và sau khi hàm chạy
```
from collections.abc import Callable
# 1. Định nghĩa Decoratordef bo_trang_tri(ham_goc: Callable[[], None]) -> Callable[[], None]:
    # Tạo một hàm bọc bên trong
    def ham_boc():
        print("[TRƯỚC] Đang chuẩn bị chạy hàm...")
        ham_goc() # Chạy hàm gốc ở đây
        print("[SAU] Hàm đã chạy xong thành công!")
    
    return ham_boc # Trả về hàm bọc đã được nâng cấp
# 2. Sử dụng Decorator bằng cú pháp ký hiệu @
@bo_trang_tridef chao_hoi():
    print("Xin chào thế giới Python!")
# 3. Gọi hàm
chao_hoi()
```

Kết quả hiển thị trên màn hình:

```
[TRƯỚC] Đang chuẩn bị chạy hàm...
Xin chào thế giới Python!
[SAU] Hàm đã chạy xong thành công!
```

(Lưu ý về Type Hinting: Từ Python 3.9+, bạn nên dùng collections.abc.Callable để gợi ý kiểu cho hàm).

------------------------------

## 3. Ví dụ thực tế: Đo thời gian chạy của hàm (Timer Decorator)

Đây là ứng dụng phổ biến nhất của Decorator trong thực tế để kiểm tra xem hàm nào đang chạy chậm và làm tốn tài nguyên hệ thống.

Để decorator này có thể bọc được mọi loại hàm (hàm không có tham số, hàm có nhiều tham số, hàm có giá trị trả về), chúng ta sẽ kết hợp cú pháp nhận tham số vô hạn *args và **kwargs.

```
import time
from collections.abc import Callable
from typing import Any

# Định nghĩa Decorator đo thời gian
def tinh_thoi_gian(ham_goc: Callable[..., Any]) -> Callable[..., Any]:
    def ham_boc(*args: Any, **kwargs: Any) -> Any:
        thoi_gian_bat_dau = time.time()
        
        # Chạy hàm gốc và hứng lấy kết quả trả về của nó (nếu có)
        ket_qua = ham_goc(*args, **kwargs)
        
        thoi_gian_ket_thuc = time.time()
        tong_thoi_gian = thoi_gian_ket_thuc - thoi_gian_bat_dau
        print(f"⏱️ Hàm '{ham_goc.__name__}' chạy mất: {tong_thoi_gian:.6f} giây.")
        
        return ket_qua # Trả lại kết quả để không làm hỏng logic của hàm gốc
        
    return ham_boc
# Sử dụng decorator cho một hàm tính toán
@tinh_thoi_giandef tinh_tong_binh_phuong(n: int) -> int:
    tong = 0
    for i in range(n):
        tong += i ** 2
    return tong
# Gọi hàm với 1 triệu phần tửket_qua_tinh = tinh_tong_binh_phuong(1000000)
print(f"Kết quả tính toán: {ket_qua_tinh}")
```

Kết quả đầu ra:
```
⏱️ Hàm 'tinh_tong_binh_phuong' chạy mất: 0.124531 giây.
Kết quả tính toán: 333332833333500000
```

------------------------------

## 4. Khi nào bạn nên dùng Decorator?

Decorator giúp bạn tuân thủ triệt để nguyên lý DRY (Don't Repeat Yourself - Đừng lặp lại chính mình) bằng cách tách biệt phần logic phụ trợ ra khỏi logic chính của hàm. Các trường hợp áp dụng nhiều nhất bao gồm:

* Ủy quyền & Phân quyền (Authorization): Kiểm tra xem người dùng đã đăng nhập hoặc có quyền admin trước khi cho phép họ chạy hàm xóa dữ liệu.
* Ghi nhật ký (Logging): Tự động ghi lại nhật ký (log) mỗi khi có ai đó gọi vào các hàm quan trọng trong hệ thống.
* Bộ nhớ đệm (Caching/Memoization): Lưu lại kết quả của các hàm tính toán nặng. Nếu hàm bị gọi lại với tham số cũ, trả về kết quả trong cache ngay lập tức thay vì tính lại từ đầu (Python có sẵn @functools.lru_cache cho việc này).
* Kiểm tra dữ liệu đầu vào (Validation): Đảm bảo các tham số truyền vào hàm phải thỏa mãn một điều kiện nào đó trước khi xử lý.

------------------------------

Bạn đã nắm được bức tranh tổng thể về cách Decorator "bọc" và nâng cấp một hàm chưa? Bạn có muốn tìm hiểu thêm về cách viết Decorator có thể nhận tham số truyền vào (ví dụ: @kiểm_tra_quyền("admin")) không?

