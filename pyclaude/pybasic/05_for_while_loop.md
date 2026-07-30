### Bài 5: Vòng lặp (for, while)

Vòng lặp là công cụ giúp máy tính làm điều nó giỏi nhất: **lặp lại một tác vụ hàng nghìn, hàng triệu lần mà không mệt mỏi, không sai sót**. Đây là nền tảng của mọi thứ từ xử lý dữ liệu Excel hàng chục nghìn dòng, đến training một mô hình AI qua hàng triệu vòng lặp cập nhật trọng số.

---

#### 1. Vòng lặp `for` — lặp qua một chuỗi có sẵn

`for` trong Python **khác biệt** so với C/Java — nó không lặp theo "chỉ số từ 0 đến n" theo kiểu thủ công, mà **duyệt trực tiếp qua từng phần tử** của một đối tượng có thể lặp (gọi là **iterable** — khái niệm quan trọng ta sẽ đào sâu ở Bài 15).

python

```python
trai_cay = ["táo", "chuối", "xoài", "cam"]

for tc in trai_cay:
    print(f"Tôi thích ăn {tc}")
```

**Kết quả:**

```
Tôi thích ăn táo
Tôi thích ăn chuối
Tôi thích ăn xoài
Tôi thích ăn cam
```

Ở mỗi vòng lặp, biến `tc` lần lượt được gán bằng từng phần tử trong list — bạn đặt tên biến này tùy ý, nhưng quy ước là đặt tên có ý nghĩa, số ít (vì nó đại diện cho *một* phần tử).

**Lặp qua chuỗi (string)** — vì string cũng là một sequence:

python

```python
ma_don_hang = "DH2026"
for ky_tu in ma_don_hang:
    print(ky_tu)
```

#### 2. Hàm `range()` — khi bạn cần lặp theo số lần

python

```python
for i in range(5):        # 0, 1, 2, 3, 4 (5 số, KHÔNG bao gồm 5)
    print(f"Lần lặp thứ {i}")

for i in range(1, 6):     # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 20, 5): # 0, 5, 10, 15 (bước nhảy 5)
    print(i)

for i in range(10, 0, -1):  # 10, 9, 8, ... 1 (đếm ngược)
    print(i)
```

`range()` không tạo ra một list khổng lồ trong bộ nhớ ngay lập tức — nó là một **đối tượng lazy** (sinh giá trị khi cần), nên `range(10_000_000)` vẫn chạy nhẹ nhàng, không tốn bộ nhớ như bạn tưởng. Đây là một ví dụ đầu tiên về tư duy **lazy evaluation** mà bạn sẽ gặp lại ở generator (Bài 15).

**Ứng dụng thực tế** — tạo dữ liệu mẫu, giả lập ID tự động tăng:

python

```python
for don_hang_id in range(1001, 1011):
    print(f"Đang xử lý đơn hàng #{don_hang_id}")
```

#### 3. `enumerate()` — lấy cả chỉ số lẫn giá trị

Đây là kỹ thuật **rất Pythonic** mà người mới thường bỏ qua, dùng cách viết dài dòng thay thế:

python

```python
danh_sach_khach = ["An", "Bình", "Chi"]

# ❌ Cách không chuyên nghiệp - dùng range(len(...))
for i in range(len(danh_sach_khach)):
    print(f"{i+1}. {danh_sach_khach[i]}")

# ✅ Cách chuẩn Pythonic - dùng enumerate()
for i, ten in enumerate(danh_sach_khach, start=1):
    print(f"{i}. {ten}")
```

**Kết quả cả hai:**

```
1. An
2. Bình
3. Chi
```

`enumerate()` trả về cặp `(chỉ_số, giá_trị)` cho mỗi phần tử, tham số `start=1` cho phép chỉ số bắt đầu từ 1 thay vì 0 mặc định — cực tiện khi hiển thị danh sách cho người dùng (STT bắt đầu từ 1, không phải 0).

#### 4. Lặp qua nhiều dữ liệu song song với `zip()`

python

```python
ten_sp = ["Áo thun", "Quần jean", "Giày sneaker"]
gia_sp = [150000, 450000, 890000]

for ten, gia in zip(ten_sp, gia_sp):
    print(f"{ten}: {gia:,} VNĐ")
```

**Kết quả:**

```
Áo thun: 150,000 VNĐ
Quần jean: 450,000 VNĐ
Giày sneaker: 890,000 VNĐ
```

`zip()` ghép các list theo từng cặp vị trí tương ứng — cực kỳ hữu ích khi dữ liệu của bạn đến từ 2 nguồn tách biệt (ví dụ 2 cột trong file Excel) nhưng cần xử lý đồng thời.

---

#### 5. Vòng lặp `while` — lặp khi CHƯA BIẾT trước số lần

Khác với `for` (lặp qua dữ liệu có sẵn, biết trước độ dài), `while` lặp **chừng nào điều kiện còn đúng** — dùng khi số lần lặp phụ thuộc vào một điều kiện động, không xác định trước.

python

```python
so_du_tai_khoan = 1000000
phi_rut_moi_lan = 150000

so_lan_rut = 0
while so_du_tai_khoan >= phi_rut_moi_lan:
    so_du_tai_khoan -= phi_rut_moi_lan
    so_lan_rut += 1
    print(f"Lần rút {so_lan_rut}: còn lại {so_du_tai_khoan:,} VNĐ")

print(f"Đã rút được {so_lan_rut} lần, số dư cuối: {so_du_tai_khoan:,} VNĐ")
```

**⚠️ Cạm bẫy nguy hiểm nhất của `while`: vòng lặp vô hạn (infinite loop)**

python

```python
# ❌ NGUY HIỂM - quên cập nhật biến điều kiện -> chạy mãi mãi, treo chương trình
dem = 0
while dem < 5:
    print("Đang chạy...")
    # QUÊN dòng dem += 1 -> vòng lặp không bao giờ dừng!
```

Đây là lỗi runtime cực kỳ phổ biến khi mới học `while` — luôn tự hỏi: **"Điều kiện dừng này chắc chắn sẽ đạt được không?"** trước khi chạy code.

**Ứng dụng thực tế cực kỳ phổ biến** — vòng lặp xác thực input người dùng cho đến khi hợp lệ (dùng nhiều trong CLI tool, script tự động hóa):

python

```python
mat_khau_dung = "Python2026!"
so_lan_thu = 0
so_lan_toi_da = 3

while so_lan_thu < so_lan_toi_da:
    nhap = input("Nhập mật khẩu: ")
    if nhap == mat_khau_dung:
        print("Đăng nhập thành công!")
        break
    so_lan_thu += 1
    print(f"Sai mật khẩu. Còn {so_lan_toi_da - so_lan_thu} lần thử")
else:
    print("Tài khoản đã bị khóa do nhập sai quá số lần cho phép")
```

#### 6. `while True` + `break` — mẫu thiết kế vòng lặp phổ biến trong thực tế

python

```python
tong_don_hang = 0
while True:
    nhap = input("Nhập giá trị đơn hàng (gõ 'xong' để kết thúc): ")
    if nhap.lower() == "xong":
        break
    tong_don_hang += float(nhap)

print(f"Tổng giá trị: {tong_don_hang:,.0f} VNĐ")
```

Mẫu `while True` kết hợp `break` được dùng rất nhiều trong thực tế khi xây dựng **vòng lặp sự kiện (event loop)** — ví dụ server liên tục lắng nghe request, hoặc chương trình CLI chờ lệnh người dùng cho đến khi họ chủ động thoát.

---

#### 7. `break`, `continue`, và mệnh đề `else` của vòng lặp

python

```python
# break - thoát khỏi vòng lặp ngay lập tức
for so in range(1, 100):
    if so > 10:
        break
    print(so)

# continue - bỏ qua lần lặp hiện tại, tiếp tục lần sau
for so in range(1, 11):
    if so % 2 == 0:
        continue    # bỏ qua số chẵn
    print(so)        # chỉ in số lẻ: 1, 3, 5, 7, 9
```

**`for...else`** — cấu trúc lạ với người mới nhưng rất hữu ích: khối `else` chạy khi vòng lặp **kết thúc bình thường** (không bị `break`):

python

```python
danh_sach_ma_don = [1001, 1002, 1003, 1005]
ma_can_tim = 1004

for ma in danh_sach_ma_don:
    if ma == ma_can_tim:
        print(f"Đã tìm thấy đơn hàng {ma_can_tim}")
        break
else:
    print(f"Không tìm thấy đơn hàng {ma_can_tim} trong hệ thống")
```

Đây là mẫu code cực kỳ thanh lịch (elegant) cho bài toán "tìm kiếm rồi báo không tìm thấy" mà không cần dùng thêm biến cờ (flag) `da_tim_thay = False`.

---

#### 8. Vòng lặp lồng nhau (Nested loops)

python

```python
# Ma trận sản phẩm x kích cỡ - ví dụ quản lý kho hàng thời trang
san_pham = ["Áo thun", "Áo sơ mi"]
kich_co = ["S", "M", "L", "XL"]

for sp in san_pham:
    for kc in kich_co:
        print(f"SKU: {sp}-{kc}")
```

**Cảnh báo về độ phức tạp**: vòng lặp lồng 2 cấp với n và m phần tử sẽ chạy `n × m` lần. Với dữ liệu lớn (ví dụ so sánh 2 danh sách 10,000 phần tử mỗi cái), lồng vòng lặp ngây thơ sẽ chạy 100 triệu lần — đây là lúc dev chuyên nghiệp cần nghĩ đến cấu trúc dữ liệu hiệu quả hơn như `set` hay `dict` (sẽ học ở Bài 7, 8) để tránh vòng lặp lồng không cần thiết.

---

#### 9. List Comprehension — cách viết vòng lặp "chuẩn Python" (giới thiệu sơ bộ)

Đây là cú pháp bạn sẽ dùng RẤT nhiều sau khi học `list` kỹ ở Bài 6, nhưng giới thiệu sớm để bạn làm quen tư duy:

python

```python
# Cách viết vòng lặp truyền thống
binh_phuong = []
for i in range(1, 6):
    binh_phuong.append(i ** 2)

# Cách viết Pythonic - list comprehension (gọn hơn, nhanh hơn)
binh_phuong = [i ** 2 for i in range(1, 6)]
print(binh_phuong)   # [1, 4, 9, 16, 25]
```

Ta sẽ đào sâu comprehension ở Bài 6 và nâng cao ở Bài 16 — giờ chỉ cần biết nó tồn tại.

---

#### 10. Ví dụ thực chiến tổng hợp — Phân tích doanh thu cửa hàng

python

```python
don_hang = [
    {"ma": "DH001", "gia_tri": 250000, "trang_thai": "hoan_thanh"},
    {"ma": "DH002", "gia_tri": 480000, "trang_thai": "huy"},
    {"ma": "DH003", "gia_tri": 120000, "trang_thai": "hoan_thanh"},
    {"ma": "DH004", "gia_tri": 890000, "trang_thai": "hoan_thanh"},
    {"ma": "DH005", "gia_tri": 60000,  "trang_thai": "dang_giao"},
]

tong_doanh_thu = 0
so_don_hoan_thanh = 0

for don in don_hang:
    if don["trang_thai"] == "hoan_thanh":
        tong_doanh_thu += don["gia_tri"]
        so_don_hoan_thanh += 1
        print(f"✓ {don['ma']}: {don['gia_tri']:,} VNĐ")
    else:
        print(f"✗ {don['ma']}: bỏ qua ({don['trang_thai']})")

print(f"\nTổng doanh thu từ {so_don_hoan_thanh} đơn hoàn thành: {tong_doanh_thu:,} VNĐ")
if so_don_hoan_thanh > 0:
    print(f"Giá trị trung bình/đơn: {tong_doanh_thu / so_don_hoan_thanh:,.0f} VNĐ")
```

(Đừng lo nếu cú pháp `{"ma": ..., "gia_tri": ...}` còn lạ — đó là `dict`, ta sẽ học kỹ ở Bài 8. Ở đây chỉ để bạn thấy vòng lặp áp dụng vào bài toán thực tế trông như thế nào.)

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_5.py` mô phỏng **hệ thống kiểm kê điểm danh lớp học lập trình online**:

python

```python
danh_sach_hoc_vien = ["Minh", "Lan", "Huy", "Trang", "Phúc", "Ngọc", "Đức"]
diem_danh = [True, True, False, True, False, True, True]
```

Yêu cầu:

1. Dùng `zip()` và `enumerate()` kết hợp để in danh sách theo dạng:

```
   1. Minh - Có mặt
   2. Lan - Có mặt
   3. Huy - Vắng
   ...
```

2. Đếm tổng số học viên có mặt và vắng mặt (dùng vòng lặp, không dùng hàm đếm sẵn)
3. Dùng `while` để mô phỏng: mỗi buổi học trừ 100,000đ học phí còn lại từ số dư `500,000đ` của một học viên, in ra số dư sau mỗi buổi, dừng lại khi số dư không đủ trả cho buổi tiếp theo — dùng `while` + tính điều kiện dừng chính xác
4. Thử thách thêm: viết đoạn code dùng `for...else` để tìm xem "Huy" có mặt buổi nào không trong danh sách trên, nếu tìm hết mà không thấy thì in "Huy vắng toàn bộ khóa học"

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 6: List (Danh sách)** — nơi ta đào sâu vào cấu trúc dữ liệu bạn đã chạm tới nhiều lần trong bài này, bao gồm các thao tác thêm/xóa/sửa, list comprehension đầy đủ, và hiểu rõ khái niệm mutable đã nhắc ở Bài 2.
