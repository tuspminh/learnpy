Vai trò giảng viên + lập trình viên chuyên nghiệp này tôi đã lưu vào bộ nhớ từ trước và đang duy trì xuyên suốt. Giờ vào bài học được xem là **quan trọng nhất trong toàn bộ giai đoạn nền tảng**.

### 📘 Bài 8: Dictionary (Từ điển)

Nếu phải chọn MỘT cấu trúc dữ liệu quan trọng nhất trong Python hiện đại, đó chính là `dict`. Lý do: **JSON — định dạng dữ liệu chuẩn của toàn bộ web API, ứng dụng di động, microservices ngày nay — về bản chất chính là dictionary lồng nhau**. Hiểu sâu dict nghĩa là bạn đã sẵn sàng làm việc với dữ liệu thực tế từ mọi hệ thống hiện đại.

---

#### 1. Dictionary là gì — cấu trúc key-value

Khác với list/tuple (truy cập theo vị trí số 0, 1, 2...), dict lưu dữ liệu theo cặp **khóa (key) - giá trị (value)**, truy cập bằng khóa có ý nghĩa:

python

```python
khach_hang = {
    "ma_kh": "KH001",
    "ten": "Nguyễn Văn An",
    "tuoi": 28,
    "la_vip": True,
    "diem_tich_luy": 1250
}

print(khach_hang["ten"])         # 'Nguyễn Văn An'
print(khach_hang["diem_tich_luy"]) # 1250
```

So với việc dùng list `["KH001", "Nguyễn Văn An", 28, True, 1250]` rồi phải nhớ "index 1 là tên, index 4 là điểm"— dict giúp code **tự giải thích chính nó (self-documenting)**, dễ đọc và ít lỗi hơn rất nhiều khi dữ liệu có nhiều thuộc tính.

#### 2. Vì sao dict lại nhanh — kết nối lại kiến thức "hashable" từ Bài 7

Đây là lúc khái niệm "hashable" ở bài trước phát huy ý nghĩa đầy đủ. Dict sử dụng **hash table** — mỗi key được "băm" (hash) thành một địa chỉ trong bộ nhớ, giúp truy xuất giá trị với độ phức tạp **O(1)**, gần như tức thời bất kể dict có 10 hay 10 triệu phần tử.

python

```python
# key PHẢI là kiểu bất biến (hashable): str, int, float, tuple, bool
hop_le = {"ten": "An", 25: "tuổi", (1,2): "tọa độ"}   # OK

# key KHÔNG được là kiểu khả biến (unhashable): list, dict, set
# khong_hop_le = {["a", "b"]: "giá trị"}   # ❌ TypeError: unhashable type: 'list'
```

Đây chính xác là lý do tại sao **tuple tồn tại** — khi bạn cần một "danh sách" làm khóa dict, bạn phải dùng tuple (bất biến) thay vì list (khả biến), vì Python cần đảm bảo key không đổi để hash table hoạt động chính xác.

---

#### 3. Truy cập giá trị — 2 cách, và cạm bẫy quan trọng

python

```python
sp = {"ten": "Laptop Dell", "gia": 28500000}

# Cách 1: dùng [] - BÁO LỖI nếu key không tồn tại
print(sp["ten"])
# print(sp["mau_sac"])   # ❌ KeyError: 'mau_sac'

# Cách 2: dùng .get() - AN TOÀN, trả về None nếu không tồn tại (không crash)
print(sp.get("mau_sac"))              # None
print(sp.get("mau_sac", "Chưa xác định"))   # "Chưa xác định" - có giá trị mặc định
```

**Nguyên tắc thực chiến quan trọng**: khi xử lý dữ liệu từ nguồn không đáng tin cậy tuyệt đối (API bên ngoài, input người dùng, dữ liệu database có thể thiếu trường), **luôn dùng `.get()`** thay vì `[]` để tránh chương trình crash bất ngờ:

python

```python
def lay_thong_tin_don_hang(don_hang_api):
    ma = don_hang_api.get("ma", "N/A")
    ghi_chu = don_hang_api.get("ghi_chu", "Không có ghi chú")   # trường có thể không tồn tại
    return f"Đơn {ma}: {ghi_chu}"

# Dữ liệu thực tế từ API thường KHÔNG đầy đủ trường như bạn mong đợi
don_thieu_truong = {"ma": "DH123"}   # thiếu "ghi_chu"
print(lay_thong_tin_don_hang(don_thieu_truong))   # Không crash nhờ .get()
```

---

#### 4. Thêm, sửa, xóa dữ liệu trong dict

python

```python
sp = {"ten": "Laptop Dell", "gia": 28500000}

sp["mau_sac"] = "Bạc"          # thêm key mới (nếu chưa có) hoặc sửa (nếu đã có)
sp["gia"] = 27900000           # sửa giá trị đã tồn tại
print(sp)

sp.update({"gia": 26500000, "bao_hanh": "24 tháng"})   # sửa/thêm nhiều key cùng lúc

del sp["mau_sac"]                    # xóa theo key
gia_tri_xoa = sp.pop("bao_hanh")     # xóa và TRẢ VỀ giá trị đã xóa
gia_tri_an_toan = sp.pop("khong_ton_tai", "Không có")  # xóa an toàn, không crash nếu thiếu key
```

---

#### 5. Duyệt qua dict — 3 cách cần nắm chắc

python

```python
san_pham = {"ten": "Bàn phím cơ", "gia": 1250000, "ton_kho": 15}

# Duyệt qua KEY (mặc định khi lặp trực tiếp trên dict)
for key in san_pham:
    print(key)

# Duyệt qua VALUE
for value in san_pham.values():
    print(value)

# Duyệt qua CẢ key và value cùng lúc - cách dùng NHIỀU NHẤT trong thực tế
for key, value in san_pham.items():
    print(f"{key}: {value}")
```

**Ứng dụng thực tế** — in báo cáo từ dữ liệu dict, cực kỳ phổ biến khi hiển thị kết quả xử lý:

python

```python
doanh_thu_theo_thang = {
    "Tháng 1": 45000000,
    "Tháng 2": 52000000,
    "Tháng 3": 38000000
}

for thang, doanh_thu in doanh_thu_theo_thang.items():
    print(f"{thang}: {doanh_thu:>15,} VNĐ")

tong = sum(doanh_thu_theo_thang.values())
print(f"Tổng quý: {tong:,} VNĐ")
```

---

#### 6. Dict lồng nhau (Nested dict) — mô hình dữ liệu thực tế

Đây là hình dạng dữ liệu bạn sẽ gặp **liên tục** khi làm việc với API thực tế — dict chứa list, list chứa dict, lồng nhiều tầng:

python

```python
he_thong_don_hang = {
    "ma_don": "DH2026-0891",
    "khach_hang": {
        "ten": "Trần Thị Bích",
        "email": "bich.tran@email.com",
        "dia_chi": {
            "duong": "123 Nguyễn Huệ",
            "thanh_pho": "TP. Hồ Chí Minh"
        }
    },
    "san_pham": [
        {"ten": "Áo thun", "gia": 150000, "so_luong": 2},
        {"ten": "Quần jean", "gia": 450000, "so_luong": 1}
    ],
    "trang_thai": "dang_giao"
}

# Truy cập dữ liệu lồng sâu - đọc từ ngoài vào trong
print(he_thong_don_hang["khach_hang"]["ten"])                    # 'Trần Thị Bích'
print(he_thong_don_hang["khach_hang"]["dia_chi"]["thanh_pho"])   # 'TP. Hồ Chí Minh'
print(he_thong_don_hang["san_pham"][0]["ten"])                   # 'Áo thun' - list bên trong dict

# Tính tổng tiền đơn hàng - kết hợp duyệt list bên trong dict
tong_tien = sum(sp["gia"] * sp["so_luong"] for sp in he_thong_don_hang["san_pham"])
print(f"Tổng tiền: {tong_tien:,} VNĐ")
```

**Đây chính xác là hình dạng của một JSON response thực tế** từ bất kỳ REST API nào bạn sẽ làm việc trong tương lai (thanh toán, đặt hàng, mạng xã hội...). Việc thành thạo truy cập dict lồng nhau là kỹ năng sống còn khi làm việc với API — điều ta sẽ học chính thức ở Bài 19.

---

#### 7. Dict Comprehension

python

```python
sp_ten_gia = {"Áo": 150000, "Quần": 450000, "Giày": 890000}

# Tạo dict mới từ dict cũ - ví dụ áp dụng giảm giá 10% cho tất cả sản phẩm
gia_sau_km = {ten: gia * 0.9 for ten, gia in sp_ten_gia.items()}
print(gia_sau_km)   # {'Áo': 135000.0, 'Quần': 405000.0, 'Giày': 801000.0}

# Có điều kiện lọc - chỉ lấy sản phẩm giá > 200,000
sp_dat = {ten: gia for ten, gia in sp_ten_gia.items() if gia > 200000}
print(sp_dat)   # {'Quần': 450000, 'Giày': 890000}

# Đảo key <-> value (chỉ nên dùng khi value là duy nhất, không trùng lặp)
gia_ten = {gia: ten for ten, gia in sp_ten_gia.items()}
```

**Ứng dụng thực tế cực kỳ phổ biến** — chuyển đổi list of dict thành dict tra cứu nhanh theo key (tăng tốc tìm kiếm từ O(n) xuống O(1), nhớ lại Bài 7):

python

```python
danh_sach_sp = [
    {"ma": "SP001", "ten": "Laptop"},
    {"ma": "SP002", "ten": "Chuột"},
    {"ma": "SP003", "ten": "Bàn phím"},
]

# Chuyển thành dict tra cứu theo mã - giờ tìm sản phẩm chỉ tốn O(1) thay vì O(n)
tra_cuu_sp = {sp["ma"]: sp["ten"] for sp in danh_sach_sp}
print(tra_cuu_sp["SP002"])   # 'Chuột' - tức thời, không cần duyệt qua từng phần tử
```

---

#### 8. `defaultdict` và kỹ thuật đếm/nhóm dữ liệu — bài toán thực tế cực phổ biến

Một tình huống rất hay gặp: đếm số lần xuất hiện hoặc nhóm dữ liệu theo danh mục. Cách làm "ngây thơ" dễ gây lỗi:

python

```python
don_hang = [
    {"khach": "An", "gia_tri": 250000},
    {"khach": "Bình", "gia_tri": 480000},
    {"khach": "An", "gia_tri": 120000},
]

# Cách phải kiểm tra tồn tại thủ công - dễ quên, dễ lỗi
tong_theo_khach = {}
for don in don_hang:
    khach = don["khach"]
    if khach not in tong_theo_khach:
        tong_theo_khach[khach] = 0
    tong_theo_khach[khach] += don["gia_tri"]

print(tong_theo_khach)   # {'An': 370000, 'Bình': 480000}
```

Cách chuyên nghiệp hơn, dùng `dict.get()` với giá trị mặc định:

python

```python
tong_theo_khach = {}
for don in don_hang:
    khach = don["khach"]
    tong_theo_khach[khach] = tong_theo_khach.get(khach, 0) + don["gia_tri"]
```

Hoặc dùng `collections.defaultdict` — công cụ chuyên dụng, được dev chuyên nghiệp ưa chuộng nhất cho bài toán này:

python

```python
from collections import defaultdict

tong_theo_khach = defaultdict(int)   # giá trị mặc định cho key mới là 0 (int())
for don in don_hang:
    tong_theo_khach[don["khach"]] += don["gia_tri"]   # không cần kiểm tra tồn tại nữa!

print(dict(tong_theo_khach))   # {'An': 370000, 'Bình': 480000}
```

Ta sẽ gặp lại `collections` — một module cực kỳ hữu dụng của thư viện chuẩn — ở Bài 17.

---

#### 9. Kiểm tra tồn tại key

python

```python
sp = {"ten": "Laptop", "gia": 28500000}

print("ten" in sp)          # True - kiểm tra KEY, không phải value
print("mau_sac" in sp)      # False
print(28500000 in sp)       # False - vì đây là kiểm tra key, 28500000 không phải key!
print(28500000 in sp.values())  # True - phải dùng .values() để kiểm tra value
```

Đây là lỗi nhận thức phổ biến với người mới: `in` trên dict mặc định kiểm tra **key**, không phải value — khác với list mà `in` kiểm tra phần tử trực tiếp.

---

#### 10. Ví dụ thực chiến tổng hợp — Hệ thống phân tích giao dịch e-commerce

python

```python
giao_dich = [
    {"ma_gd": "GD001", "khach": "An", "san_pham": "Laptop", "gia_tri": 28500000, "trang_thai": "thanh_cong"},
    {"ma_gd": "GD002", "khach": "Bình", "san_pham": "Chuột", "gia_tri": 350000, "trang_thai": "thanh_cong"},
    {"ma_gd": "GD003", "khach": "An", "san_pham": "Bàn phím", "gia_tri": 1250000, "trang_thai": "that_bai"},
    {"ma_gd": "GD004", "khach": "Chi", "san_pham": "Laptop", "gia_tri": 32000000, "trang_thai": "thanh_cong"},
]

from collections import defaultdict

doanh_thu_theo_khach = defaultdict(int)
doanh_thu_theo_sp = defaultdict(int)
so_gd_that_bai = 0

for gd in giao_dich:
    if gd["trang_thai"] == "thanh_cong":
        doanh_thu_theo_khach[gd["khach"]] += gd["gia_tri"]
        doanh_thu_theo_sp[gd["san_pham"]] += gd["gia_tri"]
    else:
        so_gd_that_bai += 1

print("=== Doanh thu theo khách hàng ===")
for khach, tien in sorted(doanh_thu_theo_khach.items(), key=lambda item: item[1], reverse=True):
    print(f"{khach:<10}: {tien:>15,} VNĐ")

print(f"\nSố giao dịch thất bại: {so_gd_that_bai}")
```

Lưu ý dòng `sorted(doanh_thu_theo_khach.items(), key=lambda item: item[1], ...)` — đây là kỹ thuật **sắp xếp dict theo value**, cực kỳ phổ biến trong báo cáo thực tế (bảng xếp hạng khách hàng, top sản phẩm bán chạy...).

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_8.py` mô phỏng **hệ thống quản lý đơn hàng dạng JSON API response**:

python

```python
don_hang_api = {
    "ma_don": "ORD-2026-4471",
    "khach_hang": {
        "ten": "Lê Thị Hồng",
        "email": "hong.le@shop.vn",
        "hang_thanh_vien": "Vàng"
    },
    "chi_tiet_san_pham": [
        {"ten": "Tai nghe Bluetooth", "don_gia": 890000, "so_luong": 1},
        {"ten": "Ốp lưng điện thoại", "don_gia": 85000, "so_luong": 3},
        {"ten": "Sạc dự phòng", "don_gia": 450000, "so_luong": 1}
    ],
    "phi_van_chuyen": 25000,
    "trang_thai": "cho_xac_nhan"
}
```

Yêu cầu:

1. In ra tên khách hàng và hạng thành viên bằng cách truy cập dict lồng nhau
2. Tính **tổng tiền hàng** (chưa gồm ship) bằng cách duyệt qua `chi_tiet_san_pham` (dùng vòng lặp hoặc generator expression như ví dụ ở trên)
3. Tính **tổng thanh toán** = tổng tiền hàng + phí vận chuyển
4. Nếu `hang_thanh_vien == "Vàng"`, áp dụng giảm giá 5% trên tổng tiền hàng (không giảm phí ship) — in ra số tiền được giảm
5. Dùng dict comprehension để tạo dict mới `{ten_san_pham: thanh_tien}` cho từng sản phẩm (thành tiền = đơn giá × số lượng)
6. Thử thách thêm: dùng `.get()` để an toàn truy xuất một trường không tồn tại trong `don_hang_api`, ví dụ `"ma_khuyen_mai"`, với giá trị mặc định là `"Không áp dụng"`

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 9: Hàm (Function)** — nơi bạn học cách đóng gói logic thành các đơn vị tái sử dụng, tham số, giá trị trả về, scope biến, và bắt đầu tư duy như một kỹ sư phần mềm thực sự thay vì viết code kịch bản tuần tự.
