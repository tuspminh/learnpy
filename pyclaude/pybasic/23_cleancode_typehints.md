### Bài 23: Clean Code, Type Hints, Best Practices

Đây là bài học tổng hợp, đánh dấu sự chuyển mình từ "viết code chạy được" sang **"viết code mà đồng nghiệp đọc vào hiểu ngay, dễ sửa, dễ mở rộng sau nhiều năm"**. Đây chính là kỹ năng phân biệt rõ nhất một lập trình viên có kinh nghiệm thực chiến với người mới — và là yêu cầu bắt buộc trong mọi buổi code review tại các công ty công nghệ.

---

#### 1. Nguyên tắc nền tảng: Code được ĐỌC nhiều hơn được VIẾT

Đây là câu nói kinh điển trong ngành (từ "The Zen of Python", triết lý chính thức của Python):

python

```python
import this   # thử chạy dòng này trong Python - Python "tự giới thiệu" triết lý của mình
```

**Ý nghĩa thực tế**: một đoạn code bạn viết trong 10 phút có thể được đồng nghiệp (hoặc chính bạn 6 tháng sau) đọc lại **hàng chục lần** để sửa lỗi, thêm tính năng. Code khó đọc gây tốn thời gian gấp nhiều lần công viết ra ban đầu — đây là chi phí "kỹ thuật nợ" (technical debt) mà mọi công ty phần mềm đều rất coi trọng.

---

#### 2. PEP 8 — Chuẩn coding style chính thức (nhắc lại và mở rộng)

Ta đã áp dụng PEP 8 xuyên suốt các bài học (snake_case, 4 dấu cách...), giờ hệ thống hóa đầy đủ:

python

```python
# ✅ Đặt tên rõ nghĩa, đúng quy ước
so_luong_don_hang = 15              # biến, hàm: snake_case
MAX_SO_LUONG_DON = 100                # hằng số: UPPER_CASE
class QuanLyDonHang:                  # class: PascalCase
    pass

# ✅ Khoảng trắng hợp lý
ket_qua = (gia * so_luong) + phi_ship     # có khoảng trắng quanh toán tử
ham(a, b, c)                                # có khoảng trắng sau dấu phẩy
danh_sach = [1, 2, 3]                        # không khoảng trắng ngay sau [ hoặc trước ]

# ❌ Tránh
ketQua=(gia*soLuong)+phiShip     # thiếu khoảng trắng, dùng camelCase sai quy ước Python
```

**Công cụ tự động kiểm tra/format PEP 8** — dev chuyên nghiệp không tự kiểm tra bằng mắt, mà dùng công cụ tự động:

bash

```bash
pip install black flake8

black ten_file.py       # TỰ ĐỘNG format lại code theo chuẩn PEP 8
flake8 ten_file.py       # BÁO CÁO các điểm vi phạm chuẩn (không tự sửa)
```

`black` được gọi là "opinionated formatter" — nó tự quyết định cách format, loại bỏ hoàn toàn tranh luận "code style nên viết sao" giữa các thành viên trong team, một vấn đề từng gây tranh cãi rất nhiều trước khi các công cụ này phổ biến.

---

#### 3. Đặt tên biến/hàm — nghệ thuật quan trọng nhất của Clean Code

python

```python
# ❌ Tên không có ý nghĩa
def f(x, y):
    return x * y * 0.1

d = f(500000, 3)

# ✅ Tên tự giải thích - đọc code như đọc câu tiếng Anh
def tinh_thue_ban_hang(gia_tri_don_hang: float, so_luong: int) -> float:
    THUE_SUAT = 0.1
    return gia_tri_don_hang * so_luong * THUE_SUAT

tong_thue = tinh_thue_ban_hang(gia_tri_don_hang=500000, so_luong=3)
```

**Nguyên tắc thực chiến khi đặt tên:**

- Hàm nên đặt tên là **động từ** (mô tả hành động): `tinh_thue()`, `lay_thong_tin_khach()`, `gui_email()`
- Biến boolean nên có tiền tố `la_`, `co_`, `da_`: `la_khach_vip`, `co_giam_gia`, `da_thanh_toan`
- Tránh viết tắt mơ hồ: `sl` (số lượng hay "sản lượng"?), `tk` (tài khoản hay "tổng kết"?) — viết đầy đủ `so_luong`, `tai_khoan`
- Độ dài tên nên **tỷ lệ với phạm vi sử dụng**: biến dùng trong vòng lặp ngắn (`for i in range(...)`) có thể ngắn, biến dùng xuyên suốt module cần tên đầy đủ, rõ nghĩa

---

#### 4. Hàm nên làm MỘT việc — Nguyên tắc Single Responsibility

python

```python
# ❌ Hàm làm QUÁ NHIỀU việc - khó test, khó tái sử dụng, khó đọc
def xu_ly_don_hang(don_hang):
    # Validate dữ liệu
    if don_hang["gia_tri"] <= 0:
        raise ValueError("Giá trị đơn không hợp lệ")

    # Tính thuế
    thue = don_hang["gia_tri"] * 0.1

    # Gửi email
    import smtplib
    server = smtplib.SMTP("smtp.gmail.com")
    server.sendmail(...)

    # Ghi log vào database
    import sqlite3
    conn = sqlite3.connect("log.db")
    conn.execute("INSERT INTO log ...")

    return don_hang["gia_tri"] + thue
```

python

```python
# ✅ Phân rã thành các hàm nhỏ, mỗi hàm MỘT trách nhiệm rõ ràng
def validate_don_hang(don_hang: dict) -> None:
    if don_hang["gia_tri"] <= 0:
        raise ValueError("Giá trị đơn không hợp lệ")

def tinh_thue(gia_tri: float, thue_suat: float = 0.1) -> float:
    return gia_tri * thue_suat

def gui_email_xac_nhan(email: str, noi_dung: str) -> None:
    ...   # logic gửi email riêng biệt

def ghi_log_don_hang(don_hang: dict) -> None:
    ...   # logic ghi log riêng biệt

def xu_ly_don_hang(don_hang: dict) -> float:
    """Điều phối các hàm nhỏ - dễ đọc luồng xử lý tổng thể"""
    validate_don_hang(don_hang)
    thue = tinh_thue(don_hang["gia_tri"])
    tong = don_hang["gia_tri"] + thue

    gui_email_xac_nhan(don_hang["email"], f"Đơn hàng của bạn: {tong:,} VNĐ")
    ghi_log_don_hang(don_hang)

    return tong
```

**Lợi ích thực chiến của cách phân rã này** (kết nối trực tiếp Bài 21 — Testing): mỗi hàm nhỏ giờ có thể **test độc lập** — bạn test `tinh_thue()` mà không cần lo về email hay database, giúp viết unit test nhanh và chính xác hơn rất nhiều.

---

#### 5. Tránh "Magic Numbers/Strings" — dùng hằng số có tên

python

```python
# ❌ Magic number - đọc code không hiểu 0.1 và 500000 nghĩa là gì
def tinh_gia_cuoi(gia):
    if gia > 500000:
        return gia * 0.9
    return gia

# ✅ Đặt tên rõ nghĩa cho các con số quan trọng
MUC_GIA_AP_DUNG_GIAM_GIA = 500_000
TY_LE_GIAM_GIA = 0.1

def tinh_gia_cuoi(gia: float) -> float:
    if gia > MUC_GIA_AP_DUNG_GIAM_GIA:
        return gia * (1 - TY_LE_GIAM_GIA)
    return gia
```

**Lợi ích thực tế**: khi công ty đổi chính sách (mức giá áp dụng giảm từ 500k lên 1 triệu), bạn chỉ sửa **một dòng khai báo hằng số**, không cần tìm và sửa `500000` rải rác khắp codebase — tránh sót, tránh nhầm với các số `500000` khác không liên quan đến logic này.

---

#### 6. Type Hints nâng cao — chuẩn 2026

Nhớ lại type hints cơ bản ở Bài 9, giờ mở rộng với các trường hợp thực tế phức tạp hơn:

python

```python
from typing import Optional, Union
from datetime import datetime

def tim_khach_hang(ma_kh: str) -> Optional[dict]:
    """Trả về dict thông tin khách, hoặc None nếu không tìm thấy."""
    ...

def xu_ly_id(id_input: Union[int, str]) -> int:
    """Nhận id dạng int hoặc str, luôn trả về int."""
    return int(id_input)

def lay_don_hang(tu_ngay: datetime, den_ngay: datetime) -> list[dict]:
    """Python 3.9+ cho phép viết list[dict] trực tiếp, không cần import List từ typing"""
    ...

# Cú pháp hiện đại 2026 (Python 3.10+) - dùng | thay cho Union
def xu_ly_id_moi(id_input: int | str) -> int:
    return int(id_input)

def tim_khach_hang_moi(ma_kh: str) -> dict | None:
    ...
```

**`TypedDict`** — định nghĩa chính xác cấu trúc dict (thay vì `dict` mơ hồ), cực hữu ích khi làm việc với JSON response từ API (nhớ lại Bài 8, 19):

python

```python
from typing import TypedDict

class ThongTinDonHang(TypedDict):
    ma_don: str
    tong_tien: float
    trang_thai: str

def tao_bao_cao(don_hang: ThongTinDonHang) -> str:
    # IDE giờ biết CHÍNH XÁC don_hang có những key nào, kiểu gì
    return f"Đơn {don_hang['ma_don']}: {don_hang['tong_tien']:,} VNĐ"
```

---

#### 7. Docstring chuẩn Google Style — được dùng rộng rãi trong công nghiệp

python

```python
def tinh_lai_suat_kep(von_goc: float, lai_suat_nam: float, so_nam: int) -> float:
    """Tính giá trị vốn sau khi áp dụng lãi suất kép.

    Args:
        von_goc: Số vốn đầu tư ban đầu, đơn vị VNĐ.
        lai_suat_nam: Lãi suất năm dạng thập phân (0.08 = 8%).
        so_nam: Số năm đầu tư.

    Returns:
        Giá trị vốn sau khi đáo hạn, đơn vị VNĐ.

    Raises:
        ValueError: Nếu so_nam âm hoặc lai_suat_nam âm.

    Example:
        >>> tinh_lai_suat_kep(100_000_000, 0.08, 5)
        146932.80...
    """
    if so_nam < 0 or lai_suat_nam < 0:
        raise ValueError("Số năm và lãi suất phải không âm")
    return von_goc * (1 + lai_suat_nam) ** so_nam
```

Định dạng này được các công cụ tự động sinh tài liệu (Sphinx) và IDE hiện đại nhận diện chuẩn — phần `Example` với `>>>` còn cho phép chạy **doctest** (kiểm tra tự động ví dụ trong docstring luôn đúng, một kỹ thuật testing thú vị kết hợp Bài 21).

---

#### 8. Tránh Nested Code sâu — "Guard Clauses" (mệnh đề chặn sớm)

python

```python
# ❌ Lồng nhiều cấp - khó đọc, khó theo dõi luồng logic
def xu_ly_thanh_toan(don_hang):
    if don_hang is not None:
        if don_hang["trang_thai"] == "cho_xu_ly":
            if don_hang["tong_tien"] > 0:
                # logic xử lý chính, bị "chôn" 3 cấp thụt lề
                return thuc_hien_thanh_toan(don_hang)
            else:
                return "Lỗi: tổng tiền không hợp lệ"
        else:
            return "Lỗi: đơn hàng không ở trạng thái chờ xử lý"
    else:
        return "Lỗi: không có đơn hàng"
```

python

```python
# ✅ Guard clauses - kiểm tra và "thoát sớm", logic chính không bị lồng sâu
def xu_ly_thanh_toan(don_hang: Optional[dict]) -> str:
    if don_hang is None:
        return "Lỗi: không có đơn hàng"
    if don_hang["trang_thai"] != "cho_xu_ly":
        return "Lỗi: đơn hàng không ở trạng thái chờ xử lý"
    if don_hang["tong_tien"] <= 0:
        return "Lỗi: tổng tiền không hợp lệ"

    # Logic chính giờ ở cấp thụt lề NGOÀI CÙNG - rõ ràng, dễ theo dõi
    return thuc_hien_thanh_toan(don_hang)
```

Kỹ thuật "guard clauses" (đảo ngược điều kiện, xử lý trường hợp lỗi/đặc biệt trước, thoát sớm bằng `return`) là mẫu thiết kế **rất phổ biến** trong code chuyên nghiệp — giúp logic "đường chính" (happy path) luôn ở cấp thụt lề thấp nhất, dễ đọc nhất.

---

#### 9. f-string và tránh lặp code với walrus operator (`:=`)

python

```python
# Walrus operator (Python 3.8+) - gán giá trị NGAY TRONG điều kiện, tránh gọi hàm 2 lần
danh_sach_don = [{"gia_tri": 100000}, {"gia_tri": 600000}, {"gia_tri": 50000}]

# ❌ Gọi len() nhiều lần không cần thiết
if len(danh_sach_don) > 0 and len(danh_sach_don) < 100:
    print(f"Có {len(danh_sach_don)} đơn hàng")

# ✅ Walrus operator - tính một lần, dùng lại
if (so_don := len(danh_sach_don)) > 0 and so_don < 100:
    print(f"Có {so_don} đơn hàng")
```

---

#### 10. Comment — Khi nào NÊN và KHÔNG NÊN viết

python

```python
# ❌ Comment vô nghĩa - lặp lại điều code đã tự nói rõ
i = i + 1   # tăng i lên 1

# ❌ Comment giải thích "CÁI GÌ" - code tốt tự giải thích được điều này
# Tính thuế bằng cách nhân giá trị đơn hàng với 0.1
thue = gia_tri_don * 0.1

# ✅ Comment giải thích "TẠI SAO" - lý do nghiệp vụ mà code không tự nói được
# Áp dụng mức thuế ưu đãi 10% theo Nghị định 44/2025 cho ngành F&B
thue = gia_tri_don * 0.1

# ✅ Comment cảnh báo về quyết định kỹ thuật không hiển nhiên
# Dùng Decimal thay float ở đây vì tính tiền, tránh sai số dấu phẩy động (xem Bài 2)
from decimal import Decimal
tong_tien = Decimal("100.50") + Decimal("50.25")
```

**Nguyên tắc vàng**: comment tốt giải thích **lý do (why)**, không lặp lại **cái gì (what)** — vì "cái gì" nên tự hiển thị rõ qua tên biến/hàm tốt. Comment thừa còn có rủi ro **bị lỗi thời** khi code thay đổi mà quên cập nhật comment — gây hiểu sai nghiêm trọng hơn là không có comment.

---

#### 11. Ví dụ thực chiến tổng hợp — Refactor code từ "chưa clean" sang "clean"

**Trước (code hoạt động đúng nhưng khó đọc, khó maintain):**

python

```python
def xl(d):
    t = 0
    for x in d:
        if x[2] == "ok":
            t = t + x[1] * x[0]
    if t > 1000000:
        t = t * 0.9
    return t
```

**Sau khi áp dụng toàn bộ nguyên tắc Clean Code trong bài:**

python

```python
from typing import TypedDict

class MucSanPham(TypedDict):
    don_gia: float
    so_luong: int
    trang_thai: str

MUC_AP_DUNG_GIAM_GIA = 1_000_000
TY_LE_GIAM_GIA_DON_LON = 0.1
TRANG_THAI_HOP_LE = "ok"


def tinh_tong_don_hang(danh_sach_san_pham: list[MucSanPham]) -> float:
    """Tính tổng tiền đơn hàng, áp dụng giảm giá cho đơn lớn.

    Args:
        danh_sach_san_pham: Danh sách sản phẩm, mỗi mục gồm đơn giá,
            số lượng, và trạng thái ("ok" = hợp lệ để tính tiền).

    Returns:
        Tổng tiền cuối cùng sau khi áp dụng giảm giá (nếu đủ điều kiện).
    """
    tong_tien = sum(
        sp["don_gia"] * sp["so_luong"]
        for sp in danh_sach_san_pham
        if sp["trang_thai"] == TRANG_THAI_HOP_LE
    )

    if tong_tien > MUC_AP_DUNG_GIAM_GIA:
        tong_tien *= (1 - TY_LE_GIAM_GIA_DON_LON)

    return tong_tien
```

So sánh trực tiếp: cùng một logic, nhưng phiên bản sau **tự giải thích được ý nghĩa nghiệp vụ** chỉ qua việc đọc tên hàm, tên biến, và docstring — không cần người viết gốc giải thích thêm gì.

---

#### 🎯 Bài tập thực hành

Cho đoạn code "chưa clean" sau, viết file `bai_tap_23.py` refactor lại áp dụng TẤT CẢ nguyên tắc đã học trong bài:

python

```python
def calc(lst, disc):
    r = []
    for i in lst:
        if i['s'] > 0:
            p = i['p'] * i['s']
            if disc == 1:
                p = p * 0.95
            elif disc == 2:
                p = p * 0.9
            r.append(p)
    return sum(r)
```

Yêu cầu refactor:

1. Đặt tên hàm và biến rõ nghĩa, tiếng Việt không dấu hoặc tiếng Anh đều được, nhưng phải nhất quán
2. Thay `disc == 1`, `disc == 2` (magic number) bằng hằng số có tên rõ ràng, hoặc tốt hơn — dùng `Enum` nếu bạn muốn tìm hiểu thêm (gợi ý: `from enum import Enum`)
3. Thêm type hints đầy đủ, dùng `TypedDict` để định nghĩa cấu trúc mỗi phần tử trong `lst`
4. Viết docstring chuẩn Google Style, giải thích rõ tham số, giá trị trả về
5. Áp dụng guard clause hoặc list comprehension để code gọn, dễ đọc hơn thay vì vòng lặp lồng if
6. Chạy `black` và `flake8` lên file kết quả (cần `pip install black flake8`), sửa các cảnh báo nếu có
7. Thử thách thêm: viết 2-3 test case bằng `pytest` (kết hợp Bài 21) để xác nhận hàm sau khi refactor **vẫn hoạt động đúng như hàm gốc** — đây chính là quy trình "refactor an toàn" chuẩn ngành: có test trước, sau đó tự tin sửa code mà không sợ phá vỡ logic cũ

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 24 — bài cuối cùng của toàn khóa học**: **Định hướng chuyên sâu (Web/Data/Automation/AI)** — nơi ta tổng kết lại toàn bộ kiến thức, và tôi sẽ tư vấn cụ thể lộ trình tiếp theo phù hợp với hướng đi bạn muốn theo đuổi trong sự nghiệp Python.
