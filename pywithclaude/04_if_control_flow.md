### Bài 4: Cấu trúc rẽ nhánh (if / elif / else)

Đã ghi nhớ vai trò bạn giao. Đây là bài học đánh dấu bước ngoặt quan trọng: từ giờ chương trình của bạn không còn chạy tuần tự cứng nhắc từ trên xuống dưới nữa, mà có thể **"ra quyết định"** dựa trên dữ liệu — đây chính là nền tảng của mọi logic nghiệp vụ (business logic) trong phần mềm thực tế: từ hệ thống tính thuế, xét duyệt khoản vay, đến logic game.

---

#### 1. Cấu trúc `if` cơ bản

python

```python
tuoi = 20

if tuoi >= 18:
    print("Đủ tuổi bầu cử")
```

**Cú pháp bắt buộc:**

- Sau điều kiện là dấu hai chấm `:`
- Khối lệnh thực thi khi điều kiện đúng phải **thụt lề** (4 dấu cách, như đã nói ở Bài 1)
- Python đánh giá điều kiện thành `True` hoặc `False` (kiểu `bool` bạn học ở Bài 2)

#### 2. `if / else` — hai nhánh rẽ

python

```python
diem_thi = 4.5

if diem_thi >= 5:
    print("Đậu")
else:
    print("Rớt")
```

#### 3. `if / elif / else` — nhiều nhánh rẽ

Đây là cấu trúc bạn sẽ dùng nhiều nhất trong thực tế khi có **nhiều điều kiện loại trừ lẫn nhau**:

python

```python
diem = 8.5

if diem >= 9:
    xep_loai = "Xuất sắc"
elif diem >= 8:
    xep_loai = "Giỏi"
elif diem >= 6.5:
    xep_loai = "Khá"
elif diem >= 5:
    xep_loai = "Trung bình"
else:
    xep_loai = "Yếu"

print(f"Xếp loại: {xep_loai}")   # Xếp loại: Giỏi
```

**Điểm cực kỳ quan trọng về thứ tự đánh giá**: Python kiểm tra từ trên xuống, và **dừng lại ngay khi gặp điều kiện đúng đầu tiên**. Vì `diem = 8.5` thỏa `diem >= 8` nên nó không bao giờ chạy tới kiểm tra `diem >= 6.5` nữa, dù điều kiện đó cũng đúng. Đây là lỗi phổ biến nhất người mới hay mắc — viết sai thứ tự các mốc điều kiện dẫn đến kết quả sai:

python

```python
# ❌ SAI - thứ tự ngược, mọi điểm >= 5 đều bị rơi vào nhánh đầu tiên
if diem >= 5:
    xep_loai = "Trung bình"
elif diem >= 8:
    xep_loai = "Giỏi"     # Không bao giờ chạy tới đây nếu diem = 9!
```

**Nguyên tắc thực chiến**: khi viết điều kiện theo khoảng giá trị, luôn kiểm tra từ **cao nhất → thấp nhất** (hoặc ngược lại nhất quán), không bao giờ trộn lẫn.

---

#### 4. Điều kiện lồng nhau (Nested if)

python

```python
so_du_tai_khoan = 5000000
diem_tin_dung = 720

if so_du_tai_khoan > 1000000:
    if diem_tin_dung >= 700:
        print("Đủ điều kiện vay tín chấp lãi suất ưu đãi")
    else:
        print("Cần cải thiện điểm tín dụng")
else:
    print("Số dư không đủ điều kiện xét duyệt")
```

Lồng nhau quá sâu (3-4 cấp trở lên) khiến code khó đọc — dân chuyên nghiệp gọi hiện tượng này là **"Arrow code"** (code hình mũi tên do thụt lề dồn về phải). Cách khắc phục phổ biến là dùng `and` để gộp điều kiện:

python

```python
# Rõ ràng hơn, tránh lồng sâu không cần thiết
if so_du_tai_khoan > 1000000 and diem_tin_dung >= 700:
    print("Đủ điều kiện vay tín chấp lãi suất ưu đãi")
```

---

#### 5. Toán tử logic trong điều kiện phức hợp

Kết hợp lại kiến thức `and`, `or`, `not` từ Bài 2 — đây là nơi chúng phát huy sức mạnh thực sự:

python

```python
tuoi = 25
co_the_can_cuoc = True
bi_no_xau = False

# Xét duyệt mở thẻ tín dụng - logic nghiệp vụ ngân hàng thực tế
if tuoi >= 18 and co_the_can_cuoc and not bi_no_xau:
    print("Đủ điều kiện mở thẻ")
else:
    print("Không đủ điều kiện")
```

**Lưu ý về "short-circuit evaluation" (đánh giá ngắn mạch)** — kiến thức nền dev chuyên nghiệp luôn tận dụng: Python dừng đánh giá ngay khi biết chắc kết quả, không cần kiểm tra hết:

python

```python
def kiem_tra_ton_kho(ma_sp):
    print(f"Đang truy vấn database cho {ma_sp}...")  # giả lập thao tác tốn kém
    return True

gio_hang_rong = True

# Vì gio_hang_rong = True (điều kiện or đầu tiên đúng),
# Python KHÔNG BAO GIỜ gọi kiem_tra_ton_kho() -> tiết kiệm tài nguyên
if gio_hang_rong or kiem_tra_ton_kho("SP001"):
    print("Không cần kiểm tra thêm")
```

Đây là lý do trong thực tế, khi viết điều kiện `and`/`or`, người ta thường đặt **điều kiện rẻ tiền, dễ tính trước** (so sánh số, biến bool có sẵn) lên đầu, còn **điều kiện tốn kém** (gọi database, gọi API) đặt sau — giúp chương trình chạy nhanh hơn đáng kể ở quy mô lớn.

---

#### 6. Toán tử ba ngôi (Ternary / Conditional Expression)

Khi logic đơn giản, viết `if/else` đầy đủ 4 dòng có thể dư thừa. Python hỗ trợ viết gọn trên 1 dòng:

python

```python
tuoi = 16

# Cách viết dài
if tuoi >= 18:
    trang_thai = "Người lớn"
else:
    trang_thai = "Trẻ vị thành niên"

# Cách viết gọn - ternary expression (chuẩn Pythonic)
trang_thai = "Người lớn" if tuoi >= 18 else "Trẻ vị thành niên"
print(trang_thai)
```

**Ứng dụng thực tế** rất hay gặp trong xử lý dữ liệu, ví dụ gán giá trị mặc định:

python

```python
gia_km = None
gia_ban = gia_km if gia_km is not None else 100000
```

Lưu ý: chỉ nên dùng ternary khi logic **ngắn gọn, dễ đọc trong 1 dòng**. Nếu điều kiện phức tạp, hãy quay lại `if/else` đầy đủ — code dễ đọc quan trọng hơn code ngắn.

---

#### 7. So sánh `==` vs `is` — cạm bẫy thường gặp

python

```python
a = None
if a == None:      # Hoạt động nhưng KHÔNG được khuyến nghị
    print("a rỗng")

if a is None:       # ✅ Cách chuẩn Pythonic, nhanh hơn và an toàn hơn
    print("a rỗng")
```

**Tại sao dùng `is` với `None`?** Vì `is` so sánh **định danh object** (có phải cùng 1 object trong bộ nhớ không), còn `==` so sánh **giá trị** (có thể bị override hành vi bởi class tùy chỉnh, gây kết quả bất ngờ). Với `None`, `True`, `False`, quy ước ngành luôn dùng `is`/`is not` — đây là điều PEP 8 (chuẩn coding style chính thức của Python) khuyến nghị rõ ràng.

---

#### 8. Ví dụ thực chiến tổng hợp — Hệ thống tính phí ship

python

```python
tong_gia_tri_don = 350000
la_khach_vip = True
khu_vuc = "noi_thanh"   # noi_thanh / ngoai_thanh / tinh_khac

phi_ship = 0

if la_khach_vip:
    phi_ship = 0
    print("Khách VIP - Miễn phí ship")
elif tong_gia_tri_don >= 500000:
    phi_ship = 0
    print("Đơn hàng >= 500K - Miễn phí ship")
else:
    if khu_vuc == "noi_thanh":
        phi_ship = 15000
    elif khu_vuc == "ngoai_thanh":
        phi_ship = 25000
    else:
        phi_ship = 40000
    print(f"Phí ship: {phi_ship:,} VNĐ")

tong_thanh_toan = tong_gia_tri_don + phi_ship
print(f"Tổng thanh toán: {tong_thanh_toan:,} VNĐ")
```

Đây chính là kiểu logic bạn sẽ viết **hàng ngày** khi làm backend cho các hệ thống thương mại điện tử thực tế — nhiều điều kiện lồng nhau, ưu tiên theo thứ tự nghiệp vụ.

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_4.py` mô phỏng **hệ thống xét duyệt giảm giá sinh nhật** cho một app thương mại điện tử:

python

```python
tuoi_khach = 27
la_thang_sinh_nhat = True
diem_thanh_vien = 850     # điểm tích lũy
gia_tri_don_hang = 620000
```

Yêu cầu logic:

1. Nếu là tháng sinh nhật **và** điểm thành viên >= 500 → giảm giá **20%**
2. Nếu không phải sinh nhật nhưng điểm thành viên >= 1000 → giảm giá **10%**
3. Nếu giá trị đơn hàng >= 1,000,000 (bất kể điều kiện trên) → cộng thêm **5%** giảm giá nữa (gợi ý: có thể cần 2 khối `if` độc lập, không phải toàn bộ `elif`)
4. Nếu không thỏa điều kiện nào → không giảm giá
5. In ra số tiền giảm và tổng tiền cần thanh toán, định dạng bằng f-string có dấu phẩy ngăn cách hàng nghìn

Đây là bài tập có "bẫy" nhỏ về việc phân biệt khi nào dùng `elif` (loại trừ lẫn nhau) và khi nào dùng `if` độc lập (điều kiện có thể cộng dồn) — hãy suy nghĩ kỹ trước khi code.

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 5: Vòng lặp (for, while)** — công cụ giúp bạn xử lý hàng loạt dữ liệu tự động thay vì viết code lặp đi lặp lại thủ công.
