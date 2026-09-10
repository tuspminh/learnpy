Dưới đây là 3 bài tập thực hành theo cấp độ từ cơ bản đến nâng cao để giúp bạn nắm vững cách ứng dụng `enum.Enum` trong thực tế.

---

### Bài 1: Quản lý Trạng thái Đơn hàng (Cơ bản)

**Đề bài:**
Viết chương trình quản lý đơn hàng.

1. Định nghĩa Enum `TrangThaiDonHang` gồm 4 trạng thái: `CHO_XU_LY`, `DANG_GIAO`, `DA_GIAO`, `DA_HUY`.
2. Tạo lớp `DonHang` có thuộc tính `ma_don` và `trang_thai` (mặc định là `CHO_XU_LY`).
3. Viết phương thức `cap_nhat_trang_thai(trang_thai_moi)` cho phép chuyển trạng thái đơn hàng. Nếu đơn đã ở trạng thái `DA_GIAO` hoặc `DA_HUY`, không cho phép chuyển nữa.

#### Lời giải:

```python
from enum import Enum, auto


class TrangThaiDonHang(Enum):
    CHO_XU_LY = auto()
    DANG_GIAO = auto()
    DA_GIAO = auto()
    DA_HUY = auto()


class DonHang:
    def __init__(self, ma_don: str):
        self.ma_don = ma_don
        self.trang_thai = TrangThaiDonHang.CHO_XU_LY

    def cap_nhat_trang_thai(self, trang_thai_moi: TrangThaiDonHang):
        # Kiểm tra nếu đơn hàng đã kết thúc
        if self.trang_thai in (
            TrangThaiDonHang.DA_GIAO,
            TrangThaiDonHang.DA_HUY,
        ):
            print(
                f"❌ Lỗi: Đơn hàng {self.ma_don} đã ở trạng thái {self.trang_thai.name}, không thể thay đổi!"
            )
            return

        self.trang_thai = trang_thai_moi
        print(f"✅ Đơn hàng {self.ma_don} đã cập nhật thành: {self.trang_thai.name}")


# --- Chạy thử ---
don1 = DonHang("DH001")
don1.cap_nhat_trang_thai(TrangThaiDonHang.DANG_GIAO)  # Cập nhật thành công
don1.cap_nhat_trang_thai(TrangThaiDonHang.DA_GIAO)  # Cập nhật thành công
don1.cap_nhat_trang_thai(TrangThaiDonHang.DANG_GIAO)  # Báo lỗi vì đã DA_GIAO
```

---

### Bài 2: Hệ thống Phân quyền User với StrEnum (Trung bình)

**Đề bài:**
Viết lớp Enum `VaiTro` chứa các giá trị chuỗi (`ADMIN`, `EDITOR`, `VIEWER`).
Viết hàm `kiem_tra_quyen(vai_tro, hanh_dong)` trả về `True` nếu người dùng có quyền thực hiện hành động (`"read"`, `"write"`, `"delete"`):

* `ADMIN`: Có tất cả các quyền.
* `EDITOR`: Có quyền `"read"` và `"write"`.
* `VIEWER`: Chỉ có quyền `"read"`.

#### Lời giải:

```python
from enum import Enum


class VaiTro(Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


def kiem_tra_quyen(vai_tro: VaiTro, hanh_dong: str) -> bool:
    # Định nghĩa bảng quyền dựa trên Enum
    BANG_QUYEN = {
        VaiTro.ADMIN: ["read", "write", "delete"],
        VaiTro.EDITOR: ["read", "write"],
        VaiTro.VIEWER: ["read"],
    }

    quyencua_user = BANG_QUYEN.get(vai_tro, [])
    return hanh_dong in quyencua_user


# --- Chạy thử ---
user_role = VaiTro.EDITOR

print("Editor có quyền ghi không?", kiem_tra_quyen(user_role, "write"))  # True
print("Editor có quyền xóa không?", kiem_tra_quyen(user_role, "delete"))  # False
```

---

### Bài 3: Bổ sung Phương thức và Thuộc tính vào Enum (Nâng cao)

**Đề bài:**
Trong Python, Enum cũng là một class nên bạn có thể viết thêm phương thức (method) và thuộc tính (property) cho nó.
Hãy tạo Enum `LoaiThanhToan` gồm: `TIEN_MAT`, `THE_TIN_DUNG`, `VI_DIEN_TU`. Mỗi loại có một mức phí dịch vụ khác nhau:

* `TIEN_MAT`: 0%
* `THE_TIN_DUNG`: 2%
* `VI_DIEN_TU`: 1%

Viết phương thức `tinh_tong_tien(so_tien)` bên trong Enum để tính tổng tiền sau khi cộng phí.

#### Lời giải:

```python
from enum import Enum


class LoaiThanhToan(Enum):
    # Mỗi member giữ một tuple: (tên hiển thị, tỷ lệ phí)
    TIEN_MAT = ("Tiền mặt", 0.0)
    THE_TIN_DUNG = ("Thẻ tín dụng", 0.02)
    VI_DIEN_TU = ("Ví điện tử", 0.01)

    def __init__(self, ten_hien_thi: str, ty_le_phi: float):
        self.ten_hien_thi = ten_hien_thi
        self.ty_le_phi = ty_le_phi

    def tinh_tong_tien(self, so_tien_goc: float) -> float:
        phi = so_tien_goc * self.ty_le_phi
        return so_tien_goc + phi


# --- Chạy thử ---
hoa_don = 1_000_000  # 1 triệu VNĐ

hinh_thuc = LoaiThanhToan.THE_TIN_DUNG

print(f"Hình thức thanh toán: {hinh_thuc.ten_hien_thi}")
print(f"Tỷ lệ phí: {hinh_thuc.ty_le_phi * 100}%")
print(
    f"Tổng tiền phải trả: {hinh_thuc.tinh_tong_tien(hoa_don):,.0f} VNĐ"
)  # 1,020,000 VNĐ
```