Vai trò này tôi đã ghi nhớ từ đầu hành trình (bài 3) và đang duy trì nhất quán suốt 15 bài học qua — sẽ tiếp tục áp dụng nghiêm túc. Giờ vào bài học giúp code của bạn đạt độ "chuẩn Pythonic" ở cấp độ chuyên gia.

### 📘 Bài 16: Comprehension nâng cao & Lập trình hàm (Functional Programming)

Bài này đào sâu tư duy **lập trình hàm (functional programming)** — một phong cách viết code coi hàm như "công dân hạng nhất" (đã giới thiệu sơ ở Bài 9), tập trung vào **biến đổi dữ liệu qua các hàm** thay vì thay đổi trạng thái từng bước. Đây là phong cách viết code bạn sẽ thấy khắp nơi trong xử lý dữ liệu thực tế (pandas, PySpark) và trong code review của các công ty công nghệ lớn.

---

#### 1. `lambda` — Hàm ẩn danh, đào sâu

Bạn đã chạm `lambda` ở Bài 6 (`sorted(key=lambda sp: sp["gia"])`). Giờ ta hiểu bản chất đầy đủ:

python

```python
# Hàm thông thường
def binh_phuong(x):
    return x ** 2

# Lambda tương đương - hàm KHÔNG TÊN, chỉ chứa MỘT biểu thức (không có nhiều dòng logic)
binh_phuong_lambda = lambda x: x ** 2

print(binh_phuong(5))          # 25
print(binh_phuong_lambda(5))   # 25
```

**Cú pháp**: `lambda tham_so_1, tham_so_2: bieu_thuc` — không có `def`, không có `return` (tự động trả về giá trị của biểu thức), không có tên.

**Nguyên tắc quan trọng**: lambda chỉ nên dùng cho logic **cực ngắn, dùng một lần, tại chỗ** — thường là tham số truyền cho hàm khác (`sorted`, `map`, `filter`). Nếu logic dài hoặc cần dùng lại nhiều nơi, hãy dùng `def` để đặt tên rõ ràng và có thể viết docstring:

python

```python
# ✅ HỢP LÝ - dùng lambda tại chỗ, logic đơn giản, dùng 1 lần
danh_sach_sp = [{"ten": "Áo", "gia": 200}, {"ten": "Quần", "gia": 100}]
sp_sap_xep = sorted(danh_sach_sp, key=lambda sp: sp["gia"])

# ❌ KHÔNG NÊN - logic phức tạp, khó đọc, nên dùng def
tinh_phi_phuc_tap = lambda gia, kl, kc: gia + kl * 5000 + kc * 1000 if kl > 5 else gia + kl * 3000
```

---

#### 2. `map()` — Áp dụng một hàm cho MỖI phần tử

python

```python
gia_usd = [10.5, 25.0, 8.75, 42.3]
ty_gia = 25400

# Cách dùng list comprehension (đã biết từ Bài 6)
gia_vnd_v1 = [gia * ty_gia for gia in gia_usd]

# Cách dùng map() - áp dụng hàm cho TỪNG phần tử, trả về map object (lazy, giống generator)
gia_vnd_v2 = list(map(lambda gia: gia * ty_gia, gia_usd))

print(gia_vnd_v1)   # [266700.0, 635000.0, 222250.0, 1074420.0...]
print(gia_vnd_v2)   # kết quả giống nhau
```

**`map()` trả về đối tượng lazy** (giống generator ở Bài 15) — không tính ngay, chỉ tính khi bạn duyệt qua nó (bằng `list()`, `for`, hay `sum()`):

python

```python
ket_qua_map = map(lambda x: x ** 2, [1, 2, 3])
print(ket_qua_map)          # <map object at 0x...>  - chưa tính gì cả
print(list(ket_qua_map))    # [1, 4, 9] - giờ mới thực sự tính
```

**`map()` với nhiều iterable cùng lúc** — tương tự `zip()` ở Bài 5:

python

```python
gia_goc = [100000, 200000, 300000]
so_luong = [2, 1, 3]

thanh_tien = list(map(lambda gia, sl: gia * sl, gia_goc, so_luong))
print(thanh_tien)   # [200000, 200000, 900000]
```

**Nguyên tắc thực chiến 2026**: trong cộng đồng Python hiện đại, **list comprehension thường được ưu tiên hơn `map()`** vì dễ đọc hơn với người mới, đặc biệt khi logic có điều kiện lọc kèm theo. `map()` vẫn phổ biến khi làm việc với các thư viện xử lý dữ liệu, hoặc khi hàm áp dụng đã có tên sẵn (không cần viết lambda):

python

```python
chuoi_so = ["10", "25", "8"]
so_nguyen = list(map(int, chuoi_so))    # dùng trực tiếp hàm int() có sẵn, rất gọn
print(so_nguyen)   # [10, 25, 8]
```

---

#### 3. `filter()` — Lọc phần tử theo điều kiện

python

```python
don_hang = [
    {"ma": "DH001", "gia_tri": 250000, "trang_thai": "hoan_thanh"},
    {"ma": "DH002", "gia_tri": 480000, "trang_thai": "huy"},
    {"ma": "DH003", "gia_tri": 120000, "trang_thai": "hoan_thanh"},
]

# Cách list comprehension
don_hoan_thanh_v1 = [d for d in don_hang if d["trang_thai"] == "hoan_thanh"]

# Cách filter() - hàm truyền vào PHẢI trả về True/False cho mỗi phần tử
don_hoan_thanh_v2 = list(filter(lambda d: d["trang_thai"] == "hoan_thanh", don_hang))

print(len(don_hoan_thanh_v1))   # 2
print(len(don_hoan_thanh_v2))   # 2 - giống nhau
```

**Kết hợp `map()` và `filter()`** — pattern rất phổ biến trong xử lý dữ liệu theo phong cách hàm:

python

```python
# Lấy giá trị của các đơn hàng hoàn thành, đã tính thêm phí xử lý 2%
gia_tri_da_xu_ly = list(map(
    lambda d: d["gia_tri"] * 1.02,
    filter(lambda d: d["trang_thai"] == "hoan_thanh", don_hang)
))
print(gia_tri_da_xu_ly)   # [255000.0, 122400.0]

# So sánh với list comprehension - THƯỜNG dễ đọc hơn cho hầu hết người, đây cũng là lý do
# nhiều dev Python thực tế ưu tiên comprehension hơn map/filter lồng nhau
gia_tri_da_xu_ly_v2 = [d["gia_tri"] * 1.02 for d in don_hang if d["trang_thai"] == "hoan_thanh"]
```

---

#### 4. `reduce()` — Gộp toàn bộ dãy về MỘT giá trị

`reduce()` không có sẵn như `map`/`filter`, phải import từ `functools`:

python

```python
from functools import reduce

gia_tri_don_hang = [250000, 480000, 120000, 890000]

# reduce(hàm, dãy, giá_trị_khởi_đầu) - áp dụng hàm LŨY TÍCH qua từng phần tử
tong = reduce(lambda tong_tam, x: tong_tam + x, gia_tri_don_hang, 0)
print(tong)   # 1740000

# So sánh với sum() có sẵn - cho bài toán CỘNG đơn giản, sum() luôn tốt hơn
print(sum(gia_tri_don_hang))   # 1740000 - kết quả giống nhau, code NGẮN hơn nhiều
```

**`reduce()` thực sự tỏa sáng khi logic gộp KHÔNG đơn giản như cộng/nhân** — ví dụ tìm sản phẩm đắt nhất theo tiêu chí tùy chỉnh:

python

```python
san_pham = [
    {"ten": "Laptop", "gia": 28000000},
    {"ten": "Điện thoại", "gia": 15000000},
    {"ten": "Tablet", "gia": 9000000},
]

sp_dat_nhat = reduce(
    lambda sp1, sp2: sp1 if sp1["gia"] > sp2["gia"] else sp2,
    san_pham
)
print(sp_dat_nhat)   # {'ten': 'Laptop', 'gia': 28000000}

# So với max() có sẵn (thường tốt hơn cho trường hợp này)
sp_dat_nhat_v2 = max(san_pham, key=lambda sp: sp["gia"])
```

**Nguyên tắc thực chiến quan trọng**: `sum()`, `max()`, `min()`, `any()`, `all()` — các hàm tổng hợp có sẵn của Python — **hầu như luôn được ưu tiên hơn `reduce()`** vì rõ ràng, dễ đọc hơn. Chỉ dùng `reduce()` khi logic gộp phức tạp, không có hàm sẵn nào phù hợp.

---

#### 5. `any()` và `all()` — Kiểm tra điều kiện trên toàn dãy

python

```python
diem_thi = [8.5, 6.0, 9.5, 4.5, 7.0]

print(any(diem >= 9 for diem in diem_thi))    # True - CÓ ÍT NHẤT 1 phần tử thỏa điều kiện
print(all(diem >= 5 for diem in diem_thi))    # False - KHÔNG PHẢI TẤT CẢ đều thỏa (có 4.5)

# Ứng dụng thực tế - validate dữ liệu đầu vào
def kiem_tra_don_hang_hop_le(don_hang):
    return all([
        don_hang.get("ma_don"),                 # phải có ma_don (không rỗng/None)
        don_hang.get("gia_tri", 0) > 0,          # giá trị phải dương
        len(don_hang.get("san_pham", [])) > 0    # phải có ít nhất 1 sản phẩm
    ])

don_1 = {"ma_don": "DH001", "gia_tri": 250000, "san_pham": ["Áo"]}
print(kiem_tra_don_hang_hop_le(don_1))   # True
```

Lưu ý cú pháp `any(diem >= 9 for diem in diem_thi)` — đây là **generator expression** (Bài 15) truyền trực tiếp vào `any()`, không cần ngoặc `()` bao ngoài khi nó là tham số duy nhất của hàm — cách viết cực kỳ gọn và Pythonic.

---

#### 6. Comprehension lồng nhau nâng cao — làm phẳng dữ liệu 2 chiều

python

```python
# Ma trận điểm - list chứa list (2 chiều)
diem_cac_lop = [[8.5, 7.0, 9.0], [6.5, 8.0], [9.5, 7.5, 8.0, 6.0]]

# "Làm phẳng" (flatten) thành 1 list duy nhất - kỹ thuật rất hay dùng
diem_tat_ca = [diem for lop in diem_cac_lop for diem in lop]
print(diem_tat_ca)   # [8.5, 7.0, 9.0, 6.5, 8.0, 9.5, 7.5, 8.0, 6.0]

# Đọc thứ tự comprehension lồng: TỪ TRÁI SANG PHẢI, giống viết vòng lặp for lồng thông thường
# Tương đương với:
diem_tat_ca_v2 = []
for lop in diem_cac_lop:
    for diem in lop:
        diem_tat_ca_v2.append(diem)
```

**Ứng dụng thực tế cực kỳ phổ biến** — xử lý dữ liệu API trả về dạng lồng nhau (nhớ lại Bài 8 — dict lồng, list lồng):

python

```python
don_hang_theo_khach = [
    {"khach": "An", "san_pham": ["Áo", "Quần"]},
    {"khach": "Bình", "san_pham": ["Giày", "Mũ", "Tất"]},
]

# Lấy TOÀN BỘ sản phẩm đã bán, từ TẤT CẢ khách hàng, thành 1 danh sách phẳng
tat_ca_san_pham = [sp for don in don_hang_theo_khach for sp in don["san_pham"]]
print(tat_ca_san_pham)   # ['Áo', 'Quần', 'Giày', 'Mũ', 'Tất']
```

---

#### 7. Dict/Set Comprehension nâng cao — nhóm dữ liệu (grouping)

python

```python
giao_dich = [
    {"khach": "An", "gia_tri": 250000},
    {"khach": "Bình", "gia_tri": 480000},
    {"khach": "An", "gia_tri": 120000},
    {"khach": "Chi", "gia_tri": 890000},
]

# Nhóm giá trị giao dịch theo khách hàng - dùng dict comprehension + set để lấy khách duy nhất
ten_khach_duy_nhat = {gd["khach"] for gd in giao_dich}
tong_theo_khach = {
    khach: sum(gd["gia_tri"] for gd in giao_dich if gd["khach"] == khach)
    for khach in ten_khach_duy_nhat
}
print(tong_theo_khach)   # {'An': 370000, 'Bình': 480000, 'Chi': 890000}
```

**Lưu ý về hiệu năng**: cách trên có độ phức tạp O(n²) vì với mỗi khách, ta lại duyệt lại toàn bộ `giao_dich`. Với dữ liệu lớn, cách dùng `defaultdict` (Bài 8) trong vòng lặp `for` thông thường sẽ **nhanh hơn nhiều** (O(n)) — đây là ví dụ thực tế cho thấy **"code ngắn không phải lúc nào cũng là code tốt nhất"**, cần cân nhắc giữa độ gọn và hiệu năng:

python

```python
from collections import defaultdict

tong_theo_khach_toi_uu = defaultdict(int)
for gd in giao_dich:
    tong_theo_khach_toi_uu[gd["khach"]] += gd["gia_tri"]   # O(n) - chỉ duyệt 1 lần
```

---

#### 8. Walrus Operator `:=` — gán giá trị TRONG một biểu thức (Python 3.8+)

Cú pháp hiện đại giúp tránh việc tính toán một biểu thức 2 lần:

python

```python
don_hang = [{"ma": "DH001", "gia_tri": 1200000}, {"ma": "DH002", "gia_tri": 300000}]

# ❌ Không dùng walrus - phải tính len() và lọc riêng biệt, hoặc lặp code
don_lon = [d for d in don_hang if d["gia_tri"] > 1000000]
if len(don_lon) > 0:
    print(f"Có {len(don_lon)} đơn hàng lớn")

# ✅ Dùng walrus operator := - gán VÀ kiểm tra điều kiện trong 1 dòng
if (so_don_lon := len([d for d in don_hang if d["gia_tri"] > 1000000])) > 0:
    print(f"Có {so_don_lon} đơn hàng lớn")
```

**Ứng dụng thực tế phổ biến nhất của walrus** — tránh gọi hàm tốn kém 2 lần trong vòng lặp `while`:

python

```python
# Ứng dụng thực tế: đọc từng dòng input đến khi rỗng
# while (dong := input("Nhập dữ liệu (Enter để dừng): ")):
#     print(f"Đã nhận: {dong}")
```

---

#### 9. Ví dụ thực chiến tổng hợp — Pipeline xử lý dữ liệu bán hàng theo phong cách Functional

python

```python
from functools import reduce

giao_dich_tho = [
    {"ma": "GD001", "khach": "An", "gia_tri": 250000, "trang_thai": "thanh_cong"},
    {"ma": "GD002", "khach": "Bình", "gia_tri": 480000, "trang_thai": "that_bai"},
    {"ma": "GD003", "khach": "An", "gia_tri": 890000, "trang_thai": "thanh_cong"},
    {"ma": "GD004", "khach": "Chi", "gia_tri": 120000, "trang_thai": "thanh_cong"},
]

# Bước 1: Lọc giao dịch thành công (filter)
thanh_cong = list(filter(lambda gd: gd["trang_thai"] == "thanh_cong", giao_dich_tho))

# Bước 2: Áp dụng phí xử lý 1.5% (map)
da_tinh_phi = list(map(lambda gd: {**gd, "gia_tri_thuc": gd["gia_tri"] * 0.985}, thanh_cong))

# Bước 3: Tính tổng doanh thu thực (reduce, hoặc sum() đơn giản hơn)
tong_doanh_thu = sum(gd["gia_tri_thuc"] for gd in da_tinh_phi)

print(f"Số giao dịch thành công: {len(thanh_cong)}")
print(f"Tổng doanh thu thực (sau phí): {tong_doanh_thu:,.0f} VNĐ")
```

Lưu ý cú pháp `{**gd, "gia_tri_thuc": ...}` — dùng `**` để "giải nén" (unpack) toàn bộ dict `gd` vào dict mới, rồi thêm/ghi đè key mới — kỹ thuật tạo dict mới mà không sửa dict gốc, tôn trọng triết lý **immutability (bất biến)** thường được ưa chuộng trong lập trình hàm để tránh side effect ngoài ý muốn.

---

#### 10. Khi nào NÊN và KHÔNG NÊN dùng phong cách Functional

**Nguyên tắc thực chiến tổng kết:**

- **Comprehension** (list/dict/set) → ưu tiên hàng đầu cho hầu hết trường hợp, cân bằng tốt giữa gọn và dễ đọc
- **`map()`/`filter()`** → dùng khi hàm áp dụng đã có tên sẵn (`int`, `str.upper`), hoặc khi làm việc với thư viện yêu cầu (như PySpark)
- **`reduce()`** → chỉ dùng khi logic gộp phức tạp, không có hàm tổng hợp sẵn nào phù hợp (`sum`, `max`, `min`, `any`, `all`)
- **Luôn ưu tiên đọc code dễ hiểu** hơn là "ngắn nhất có thể" — code Python chuyên nghiệp được đọc nhiều hơn được viết, đồng nghiệp của bạn (hoặc chính bạn 6 tháng sau) sẽ cảm ơn vì điều này

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_16.py` xây dựng **hệ thống phân tích dữ liệu bán hàng theo phong cách functional**:

python

```python
danh_sach_giao_dich = [
    {"ma": "GD001", "khach": "An", "san_pham": "Laptop", "gia_tri": 28500000, "trang_thai": "thanh_cong"},
    {"ma": "GD002", "khach": "Bình", "san_pham": "Chuột", "gia_tri": 350000, "trang_thai": "that_bai"},
    {"ma": "GD003", "khach": "An", "san_pham": "Bàn phím", "gia_tri": 1250000, "trang_thai": "thanh_cong"},
    {"ma": "GD004", "khach": "Chi", "san_pham": "Laptop", "gia_tri": 32000000, "trang_thai": "thanh_cong"},
    {"ma": "GD005", "khach": "Chi", "san_pham": "Màn hình", "gia_tri": 5900000, "trang_thai": "thanh_cong"},
]
```

Yêu cầu (kết hợp các kỹ thuật đã học trong bài):

1. Dùng `filter()` + `lambda` lọc giao dịch thành công
2. Dùng `map()` tính giá trị đã áp thuế VAT 8% cho mỗi giao dịch thành công
3. Dùng `reduce()` từ `functools` tính tổng giá trị TẤT CẢ giao dịch thành công (sau thuế) — dù biết `sum()` có thể làm được, hãy thực hành cú pháp `reduce`
4. Dùng `any()` kiểm tra xem có giao dịch nào giá trị > 30,000,000 không
5. Dùng list comprehension lồng để lấy ra danh sách TÊN sản phẩm duy nhất (không trùng) đã từng giao dịch thành công
6. Dùng dict comprehension kết hợp generator expression để tạo `{ten_khach: tong_gia_tri}` cho các khách hàng có giao dịch thành công
7. Thử thách thêm: viết lại toàn bộ pipeline (bước 1-3) chỉ bằng MỘT dòng code duy nhất, kết hợp `filter`, `map`, `reduce` lồng nhau — sau đó tự đánh giá xem cách viết này có dễ đọc hơn hay khó đọc hơn cách viết từng bước, và giải thích tại sao

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 17: Thư viện chuẩn hữu ích (`datetime`, `os`, `re`, `collections`, `itertools`)** — bài học cuối của Giai đoạn 2, trang bị cho bạn bộ công cụ thư viện chuẩn mạnh mẽ nhất mà dev Python chuyên nghiệp dùng hàng ngày, đặc biệt là `re` (regex) để xử lý văn bản nâng cao và `collections` để tối ưu các bài toán đếm/nhóm dữ liệu ta đã chạm qua nhiều lần.
