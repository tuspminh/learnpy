Vai trò này tôi đã ghi nhớ từ trước và đang duy trì xuyên suốt hành trình của chúng ta. Giờ vào bài học đánh dấu bước chuyển mình từ "viết script" sang "tư duy kỹ thuật phần mềm".

### 📘 Bài 9: Hàm (Function)

Đến giờ, mọi code bạn viết chạy tuần tự từ trên xuống, hoặc lặp lại qua vòng lặp. Hàm giới thiệu một khái niệm cách mạng: **đóng gói logic thành một đơn vị độc lập, có thể gọi lại nhiều lần** — đây chính là nền tảng của mọi kiến trúc phần mềm lớn, từ một script nhỏ đến hệ thống backend phục vụ triệu người dùng.

---

#### 1. Tại sao cần hàm? — Nguyên tắc DRY

python

```python
# ❌ KHÔNG dùng hàm - lặp lại logy tính thuế 3 lần cho 3 khách hàng
gia_don_hang_1 = 500000
thue_1 = gia_don_hang_1 * 0.1
tong_1 = gia_don_hang_1 + thue_1

gia_don_hang_2 = 750000
thue_2 = gia_don_hang_2 * 0.1
tong_2 = gia_don_hang_2 + thue_2
# ... lặp lại mãi, và nếu thuế đổi từ 10% -> 8%, phải sửa ở MỌI nơi
```

python

```python
# ✅ Dùng hàm - viết logic MỘT LẦN, gọi lại bao nhiêu lần tùy ý
def tinh_tong_co_thue(gia_don_hang):
    thue = gia_don_hang * 0.1
    return gia_don_hang + thue

tong_1 = tinh_tong_co_thue(500000)
tong_2 = tinh_tong_co_thue(750000)
```

Đây chính là nguyên tắc **DRY (Don't Repeat Yourself)** — một trong những nguyên tắc quan trọng nhất của kỹ thuật phần mềm chuyên nghiệp. Khi thuế thay đổi, bạn chỉ sửa **một chỗ duy nhất**, toàn bộ hệ thống tự động cập nhật đúng.

---

#### 2. Cấu trúc cơ bản của hàm

python

```python
def ten_ham(tham_so_1, tham_so_2):
    """Docstring - mô tả hàm làm gì (sẽ nói kỹ ở phần sau)"""
    # logic xử lý
    ket_qua = tham_so_1 + tham_so_2
    return ket_qua

# Gọi hàm
gia_tri = ten_ham(5, 10)
print(gia_tri)   # 15
```

**Thuật ngữ cần phân biệt rõ:**

- **Tham số (parameter)**: tên biến khai báo trong định nghĩa hàm (`tham_so_1`, `tham_so_2`)
- **Đối số (argument)**: giá trị thực tế truyền vào khi gọi hàm (`5`, `10`)
- **`return`**: trả kết quả về nơi gọi hàm. Hàm không có `return` sẽ tự động trả về `None`

python

```python
def in_thong_bao(ten):
    print(f"Xin chào {ten}")
    # không có return

ket_qua = in_thong_bao("An")   # in ra "Xin chào An"
print(ket_qua)                   # None - vì hàm không return gì
```

Đây là điểm gây nhầm lẫn phổ biến: `print()` bên trong hàm chỉ **hiển thị** dữ liệu, không **trả về** dữ liệu cho biến bên ngoài sử dụng tiếp. Muốn dùng kết quả ở nơi khác, bạn **phải** dùng `return`.

---

#### 3. Tham số mặc định (Default Parameters)

python

```python
def tinh_phi_van_chuyen(gia_tri_don, khu_vuc="noi_thanh"):
    if khu_vuc == "noi_thanh":
        return 15000
    elif khu_vuc == "ngoai_thanh":
        return 25000
    else:
        return 40000

print(tinh_phi_van_chuyen(500000))                    # 15000 - dùng giá trị mặc định
print(tinh_phi_van_chuyen(500000, "ngoai_thanh"))     # 25000 - override giá trị mặc định
```

**⚠️ Cạm bẫy kinh điển — KHÔNG BAO GIỜ dùng mutable object (list, dict) làm giá trị mặc định:**

python

```python
# ❌ NGUY HIỂM - lỗi âm thầm cực kỳ phổ biến, kể cả với dev có kinh nghiệm
def them_san_pham_vao_gio(ten_sp, gio_hang=[]):    # list mặc định bị TÁI SỬ DỤNG giữa các lần gọi!
    gio_hang.append(ten_sp)
    return gio_hang

print(them_san_pham_vao_gio("Áo"))      # ['Áo']
print(them_san_pham_vao_gio("Quần"))    # ['Áo', 'Quần']  <- BẤT NGỜ! Không phải ['Quần']
```

**Tại sao xảy ra lỗi này?** Vì giá trị mặc định `[]` chỉ được tạo **MỘT LẦN DUY NHẤT** khi hàm được định nghĩa (không phải mỗi lần gọi hàm), nên mọi lần gọi hàm mà không truyền `gio_hang` đều dùng chung **một object list** đó — nhớ lại khái niệm mutable từ Bài 6!

**Cách khắc phục chuẩn (best practice bắt buộc phải biết):**

python

```python
def them_san_pham_vao_gio(ten_sp, gio_hang=None):
    if gio_hang is None:
        gio_hang = []          # tạo list MỚI mỗi lần gọi hàm
    gio_hang.append(ten_sp)
    return gio_hang

print(them_san_pham_vao_gio("Áo"))      # ['Áo']
print(them_san_pham_vao_gio("Quần"))    # ['Quần'] - đúng như mong đợi
```

Đây là một trong những lỗi được hỏi nhiều nhất trong phỏng vấn kỹ thuật Python — hiểu sâu lỗi này chứng tỏ bạn nắm chắc bản chất mutable/immutable.

---

#### 4. Positional Arguments vs Keyword Arguments

python

```python
def tao_don_hang(ten_khach, san_pham, so_luong):
    return f"{ten_khach} đặt {so_luong} {san_pham}"

# Positional - theo đúng THỨ TỰ khai báo
print(tao_don_hang("An", "Áo thun", 2))

# Keyword - chỉ rõ tên tham số, THỨ TỰ không quan trọng
print(tao_don_hang(san_pham="Áo thun", so_luong=2, ten_khach="An"))

# Kết hợp - positional PHẢI đứng trước keyword
print(tao_don_hang("An", so_luong=2, san_pham="Áo thun"))
```

**Nguyên tắc thực chiến**: khi hàm có nhiều tham số (từ 3-4 trở lên), luôn dùng keyword argument khi gọi hàm — giúp code tự giải thích và tránh lỗi truyền sai thứ tự (một lỗi khó phát hiện vì không báo lỗi cú pháp, chỉ sai logic âm thầm):

python

```python
# Khó đọc, dễ nhầm thứ tự nếu có nhiều tham số cùng kiểu
gui_email("user@gmail.com", "Chào mừng", "Cảm ơn bạn đã đăng ký", True)

# Rõ ràng, an toàn hơn - đọc code như đọc câu tiếng Anh
gui_email(
    dia_chi="user@gmail.com",
    chu_de="Chào mừng",
    noi_dung="Cảm ơn bạn đã đăng ký",
    gui_ngay=True
)
```

---

#### 5. `*args` và `**kwargs` — nhận số lượng tham số không xác định

Đây là kỹ thuật quan trọng khi bạn không biết trước có bao nhiêu đối số sẽ được truyền vào:

python

```python
def tinh_tong(*args):
    """*args thu thập MỌI positional argument thành một TUPLE"""
    print(type(args))   # <class 'tuple'>
    return sum(args)

print(tinh_tong(1, 2, 3))          # 6
print(tinh_tong(1, 2, 3, 4, 5))    # 15 - số lượng tham số tùy ý
```

python

```python
def tao_thong_tin_khach(**kwargs):
    """**kwargs thu thập MỌI keyword argument thành một DICT"""
    print(type(kwargs))   # <class 'dict'>
    for key, value in kwargs.items():
        print(f"{key}: {value}")

tao_thong_tin_khach(ten="An", tuoi=25, email="an@gmail.com")
# ten: An
# tuoi: 25
# email: an@gmail.com
```

**Ứng dụng thực tế cực kỳ phổ biến** — bạn sẽ thấy `*args, **kwargs` xuất hiện liên tục khi đọc code của các framework nổi tiếng (Django, FastAPI, Flask) vì nó cho phép hàm **linh hoạt nhận mọi loại tham số** mà không cần biết trước:

python

```python
def ghi_log(muc_do, thong_bao, **chi_tiet):
    print(f"[{muc_do}] {thong_bao}")
    for key, value in chi_tiet.items():
        print(f"    {key}: {value}")

ghi_log("ERROR", "Thanh toán thất bại", ma_don="DH123", ma_loi="E402", so_tien=250000)
```

---

#### 6. Scope (Phạm vi biến) — Local vs Global

python

```python
so_du_toan_cuc = 1000000    # biến global (toàn cục)

def rut_tien(so_tien):
    so_du_toan_cuc = so_du_toan_cuc - so_tien   # ❌ UnboundLocalError!
    return so_du_toan_cuc
```

Lỗi trên xảy ra vì: khi Python thấy có **phép gán** (`=`) cho một biến bên trong hàm, nó tự động coi biến đó là **local (biến cục bộ)** của hàm — dù bạn có ý định "sửa" biến global. Vì biến local `so_du_toan_cuc` chưa được gán giá trị nào trước khi dùng ở phép trừ, Python báo lỗi.

**Cách khắc phục đúng — hàm nên nhận và trả giá trị, tránh phụ thuộc biến global:**

python

```python
def rut_tien(so_du_hien_tai, so_tien_rut):
    return so_du_hien_tai - so_tien_rut

so_du_toan_cuc = 1000000
so_du_toan_cuc = rut_tien(so_du_toan_cuc, 200000)
print(so_du_toan_cuc)   # 800000
```

**Nguyên tắc kỹ thuật phần mềm quan trọng bậc nhất ở đây**: hàm nên là **"hộp đen" tự chứa (self-contained)** — nhận đầu vào qua tham số, trả kết quả qua `return`, **tránh đọc/sửa biến global** bất cứ khi nào có thể. Nguyên tắc này giúp code dễ test, dễ debug, và dễ dự đoán hành vi — cực kỳ quan trọng khi làm việc nhóm trên codebase lớn.

(Nếu thực sự cần sửa biến global bên trong hàm, có từ khóa `global`, nhưng trong thực tế chuyên nghiệp, việc này được xem là "code smell" — dấu hiệu thiết kế chưa tốt — nên tránh trừ trường hợp đặc biệt.)

---

#### 7. Docstring — Tài liệu hóa hàm chuẩn chuyên nghiệp

python

```python
def tinh_lai_suat_kep(von_goc, lai_suat_nam, so_nam):
    """
    Tính giá trị vốn sau khi áp dụng lãi suất kép.

    Tham số:
        von_goc (float): Số vốn đầu tư ban đầu (VNĐ)
        lai_suat_nam (float): Lãi suất năm, dạng thập phân (VD: 0.08 = 8%)
        so_nam (int): Số năm đầu tư

    Trả về:
        float: Giá trị vốn sau khi đáo hạn
    """
    return von_goc * (1 + lai_suat_nam) ** so_nam

print(tinh_lai_suat_kep(100000000, 0.08, 5))
print(tinh_lai_suat_kep.__doc__)   # in ra docstring - hữu ích khi dùng help()
help(tinh_lai_suat_kep)             # Python tự hiển thị docstring có định dạng
```

Trong môi trường làm việc chuyên nghiệp thực tế, docstring không phải "cho có" — nó là tài liệu chính thức được các IDE (VS Code, PyCharm) hiển thị khi đồng nghiệp hover chuột vào hàm bạn viết, và được công cụ tự động sinh tài liệu API sử dụng.

---

#### 8. Type Hints — chuẩn hiện đại 2026 mà mọi codebase chuyên nghiệp áp dụng

python

```python
def tinh_thanh_tien(don_gia: float, so_luong: int, giam_gia: float = 0.0) -> float:
    """Tính thành tiền sau giảm giá."""
    tam_tinh = don_gia * so_luong
    return tam_tinh * (1 - giam_gia)

ket_qua: float = tinh_thanh_tien(150000, 3, 0.1)
```

**Lưu ý quan trọng**: type hint **không bắt buộc**, Python vẫn chạy bình thường nếu bạn truyền sai kiểu — chúng chỉ là "gợi ý" giúp IDE cảnh báo lỗi sớm và giúp người đọc code hiểu ý định của hàm mà không cần đọc docstring. Đây là kỹ năng gần như **bắt buộc** trong môi trường làm việc chuyên nghiệp hiện nay, đặc biệt với các dự án dùng công cụ kiểm tra kiểu tĩnh như `mypy`.

---

#### 9. Hàm lồng và hàm là "first-class citizen"

Trong Python, hàm cũng là một loại **object** — có thể gán cho biến, truyền như tham số, trả về từ hàm khác. Đây là nền tảng cho `lambda` (Bài 6 đã dùng qua) và `decorator` (Bài 15):

python

```python
def ap_dung_thue(gia, ham_tinh_thue):
    """Nhận một HÀM khác làm tham số"""
    return gia + ham_tinh_thue(gia)

def thue_10_phan_tram(gia):
    return gia * 0.1

def thue_vat_8_phan_tram(gia):
    return gia * 0.08

print(ap_dung_thue(500000, thue_10_phan_tram))       # 550000.0
print(ap_dung_thue(500000, thue_vat_8_phan_tram))    # 540000.0
```

Khả năng "truyền hàm như một giá trị" mở ra tư duy **lập trình hàm (functional programming)** — nền tảng của các hàm `map()`, `filter()`, `sorted(key=...)` mà bạn đã dùng qua ở Bài 6, và sẽ đào sâu ở Bài 16.

---

#### 10. Ví dụ thực chiến tổng hợp — Module xử lý đơn hàng

python

```python
from typing import Optional

def tinh_gia_sau_giam(don_gia: float, ty_le_giam: float = 0.0) -> float:
    """Tính giá sau khi áp dụng tỷ lệ giảm giá."""
    return don_gia * (1 - ty_le_giam)


def tinh_tong_don_hang(san_pham: list[dict], ma_giam_gia: Optional[str] = None) -> dict:
    """
    Tính tổng giá trị đơn hàng, áp dụng mã giảm giá nếu có.

    Trả về dict chứa: tong_truoc_giam, tong_sau_giam, so_tien_tiet_kiem
    """
    ty_le_giam = 0.0
    if ma_giam_gia == "SALE10":
        ty_le_giam = 0.10
    elif ma_giam_gia == "SALE20":
        ty_le_giam = 0.20

    tong_truoc_giam = sum(sp["don_gia"] * sp["so_luong"] for sp in san_pham)
    tong_sau_giam = sum(
        tinh_gia_sau_giam(sp["don_gia"], ty_le_giam) * sp["so_luong"]
        for sp in san_pham
    )

    return {
        "tong_truoc_giam": tong_truoc_giam,
        "tong_sau_giam": tong_sau_giam,
        "so_tien_tiet_kiem": tong_truoc_giam - tong_sau_giam
    }


gio_hang = [
    {"ten": "Áo thun", "don_gia": 150000, "so_luong": 2},
    {"ten": "Quần jean", "don_gia": 450000, "so_luong": 1},
]

ket_qua = tinh_tong_don_hang(gio_hang, ma_giam_gia="SALE10")
print(f"Trước giảm: {ket_qua['tong_truoc_giam']:,.0f} VNĐ")
print(f"Sau giảm: {ket_qua['tong_sau_giam']:,.0f} VNĐ")
print(f"Tiết kiệm: {ket_qua['so_tien_tiet_kiem']:,.0f} VNĐ")
```

Lưu ý cách hàm `tinh_tong_don_hang` **tái sử dụng** hàm `tinh_gia_sau_giam` bên trong — đây chính là tư duy **phân rã vấn đề (decomposition)**: chia bài toán lớn thành các hàm nhỏ, mỗi hàm làm đúng một việc (nguyên tắc **Single Responsibility**), rồi ráp lại với nhau.

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_9.py` xây dựng **module tính lương nhân viên**:

1. Viết hàm `tinh_thue_tncn(thu_nhap: float) -> float` áp dụng biểu thuế đơn giản:
  - Thu nhập <= 5,000,000: không thuế
  - Thu nhập 5,000,001 - 10,000,000: thuế 5% trên phần vượt 5 triệu
  - Thu nhập > 10,000,000: thuế 10% trên phần vượt 10 triệu (+ thuế cố định phần trước)
2. Viết hàm `tinh_luong_thuc_nhan(luong_co_ban: float, so_ngay_nghi: int = 0, *thuong, **phu_cap) -> dict` với:
  - Trừ lương theo ngày nghỉ (mỗi ngày nghỉ trừ `luong_co_ban / 26`)
  - `*thuong` nhận nhiều khoản tiền thưởng (cộng tất cả vào)
  - `**phu_cap` nhận các khoản phụ cấp có tên (ví dụ `an_trua=500000, xang_xe=300000`), cộng tất cả vào
  - Áp dụng `tinh_thue_tncn()` cho lương trước khi cộng thưởng/phụ cấp (giả định thưởng/phụ cấp không chịu thuế theo quy tắc đơn giản này)
  - Trả về dict gồm: `luong_gross`, `thue`, `luong_thuc_nhan`
3. Gọi hàm với dữ liệu mẫu, in báo cáo lương bằng f-string định dạng đẹp
4. Thử thách thêm: viết docstring đầy đủ + type hints cho cả 2 hàm, cố ý gọi hàm sai kiểu tham số (ví dụ truyền string vào `luong_co_ban`) để quan sát Python **không** báo lỗi ngay (vì type hint chỉ là gợi ý) — điều này giúp bạn hiểu rõ giới hạn của type hints trong Python

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 10: Xử lý lỗi (Exception Handling)** — bài học cuối của giai đoạn nền tảng, dạy bạn cách viết code "chống chịu lỗi" chuyên nghiệp bằng `try/except`, thay vì để chương trình crash bất ngờ khi gặp dữ liệu ngoài dự kiến — kỹ năng bắt buộc phải có trước khi bước vào giai đoạn trung cấp.
