### Bài 6: List (Danh sách)

`list` là cấu trúc dữ liệu bạn sẽ dùng **thường xuyên nhất** trong sự nghiệp lập trình Python — từ lưu danh sách sản phẩm trong giỏ hàng, kết quả truy vấn database, đến dữ liệu huấn luyện mô hình AI. Ta đào sâu toàn diện.

---

#### 1. List là gì — và vì sao nó "mutable" (khả biến)

Khác với `str` (bất biến, học ở Bài 3), `list` là **mutable** — có thể thay đổi nội dung sau khi tạo mà không cần tạo object mới:

python

```python
gio_hang = ["Áo thun", "Quần jean"]
print(id(gio_hang))         # ví dụ: 140234567891200

gio_hang.append("Giày")
print(id(gio_hang))         # VẪN CÙNG địa chỉ - list bị thay đổi tại chỗ (in-place)
print(gio_hang)             # ['Áo thun', 'Quần jean', 'Giày']
```

Đây là điểm khác biệt cốt lõi cần khắc sâu, vì nó gây ra **cạm bẫy kinh điển nhất** với người mới học Python:

python

```python
gio_hang_a = ["Áo thun", "Quần jean"]
gio_hang_b = gio_hang_a       # ❌ KHÔNG tạo bản sao - chỉ tạo thêm 1 nhãn trỏ tới CÙNG object

gio_hang_b.append("Giày")
print(gio_hang_a)             # ['Áo thun', 'Quần jean', 'Giày']  <- BỊ ẢNH HƯỞNG THEO!
```

**Tại sao lại vậy?** Nhớ lại Bài 2: biến chỉ là **nhãn trỏ tới object**. `gio_hang_b = gio_hang_a` không tạo list mới, mà chỉ tạo thêm một nhãn trỏ vào **cùng một object** trong bộ nhớ. Sửa qua nhãn nào cũng ảnh hưởng object gốc.

**Cách tạo bản sao thực sự (copy độc lập):**

python

```python
gio_hang_a = ["Áo thun", "Quần jean"]
gio_hang_b = gio_hang_a.copy()      # hoặc gio_hang_a[:] hoặc list(gio_hang_a)

gio_hang_b.append("Giày")
print(gio_hang_a)   # ['Áo thun', 'Quần jean']  <- KHÔNG bị ảnh hưởng
print(gio_hang_b)   # ['Áo thun', 'Quần jean', 'Giày']
```

Đây là lỗi âm thầm (silent bug) nguy hiểm nhất trong Python cho người mới — chương trình không báo lỗi gì cả, nhưng dữ liệu bị thay đổi ngoài ý muốn ở một nơi hoàn toàn khác trong code. Trong hệ thống thực tế (ví dụ xử lý đơn hàng), lỗi này có thể khiến dữ liệu khách hàng A vô tình bị ghi đè bởi thao tác trên khách hàng B.

---

#### 2. Tạo list và truy cập phần tử

python

```python
so_nguyen = [1, 2, 3, 4, 5]
hon_hop = ["Python", 3.9, True, None, [1, 2]]   # list chứa nhiều kiểu khác nhau, kể cả list lồng
rong = []
rong2 = list()

# Indexing và slicing - hoạt động giống hệt string (Bài 3)
diem = [8.5, 9.0, 7.5, 6.0, 9.5]
print(diem[0])       # 8.5
print(diem[-1])      # 9.5 - phần tử cuối
print(diem[1:3])     # [9.0, 7.5]
print(diem[::-1])    # đảo ngược: [9.5, 6.0, 7.5, 9.0, 8.5]
```

---

#### 3. Các phương thức thao tác list — nhóm THÊM

python

```python
gio_hang = ["Áo thun", "Quần jean"]

gio_hang.append("Giày")           # thêm 1 phần tử vào CUỐI
print(gio_hang)   # ['Áo thun', 'Quần jean', 'Giày']

gio_hang.insert(1, "Mũ")          # chèn tại vị trí chỉ định (index 1)
print(gio_hang)   # ['Áo thun', 'Mũ', 'Quần jean', 'Giày']

gio_hang.extend(["Tất", "Thắt lưng"])  # nối thêm NHIỀU phần tử từ list khác
print(gio_hang)   # [..., 'Tất', 'Thắt lưng']
```

**Lưu ý phân biệt `append` vs `extend`** — lỗi rất phổ biến:

python

```python
danh_sach = [1, 2, 3]
danh_sach.append([4, 5])   # [1, 2, 3, [4, 5]]  <- thêm CẢ list làm 1 phần tử
danh_sach.extend([4, 5])   # [1, 2, 3, 4, 5]     <- thêm TỪNG phần tử riêng lẻ
```

#### 4. Nhóm XÓA

python

```python
sp = ["Áo", "Quần", "Giày", "Mũ", "Áo"]

sp.remove("Áo")        # xóa phần tử ĐẦU TIÊN khớp giá trị -> ['Quần', 'Giày', 'Mũ', 'Áo']
phan_tu = sp.pop()      # xóa và TRẢ VỀ phần tử cuối -> phan_tu = 'Áo', sp = ['Quần', 'Giày', 'Mũ']
phan_tu2 = sp.pop(0)    # xóa và trả về phần tử tại index 0 -> 'Quần'
del sp[0]                # xóa theo index, không trả về giá trị
sp.clear()                # xóa sạch toàn bộ list -> []
```

**Ứng dụng thực tế của `pop()`** — mô phỏng hàng đợi xử lý (queue) hoặc ngăn xếp (stack), khái niệm nền tảng trong xử lý dữ liệu thực tế:

python

```python
hang_doi_xu_ly = ["Đơn 1", "Đơn 2", "Đơn 3"]

while hang_doi_xu_ly:
    don_dang_xu_ly = hang_doi_xu_ly.pop(0)   # lấy đơn ĐẦU TIÊN ra xử lý -> FIFO (hàng đợi)
    print(f"Đang xử lý: {don_dang_xu_ly}")
```

#### 5. Nhóm SẮP XẾP & TÌM KIẾM

python

```python
gia_sp = [450000, 120000, 890000, 250000]

gia_sp.sort()                    # sắp xếp TĂNG DẦN, thay đổi list gốc (in-place)
print(gia_sp)   # [120000, 250000, 450000, 890000]

gia_sp.sort(reverse=True)        # giảm dần
print(gia_sp)   # [890000, 450000, 250000, 120000]

# sorted() - KHÔNG thay đổi list gốc, trả về list MỚI - dùng khi cần giữ nguyên bản gốc
gia_goc = [450000, 120000, 890000]
gia_da_sap_xep = sorted(gia_goc)
print(gia_goc)             # [450000, 120000, 890000] - không đổi
print(gia_da_sap_xep)      # [120000, 450000, 890000]

# Tìm kiếm
sp_list = ["Áo", "Quần", "Giày"]
print("Giày" in sp_list)          # True
print(sp_list.index("Quần"))       # 1 - vị trí của "Quần"
print(len(sp_list))                 # 3 - số phần tử
```

**Sắp xếp theo tiêu chí tùy chỉnh với `key`** — kỹ thuật cực kỳ hữu dụng trong thực tế, ví dụ sắp xếp danh sách sản phẩm theo giá trong dict:

python

```python
san_pham = [
    {"ten": "Áo thun", "gia": 150000},
    {"ten": "Quần jean", "gia": 450000},
    {"ten": "Mũ", "gia": 80000},
]

# Sắp xếp theo giá, tăng dần
san_pham_sap_xep = sorted(san_pham, key=lambda sp: sp["gia"])
for sp in san_pham_sap_xep:
    print(f"{sp['ten']}: {sp['gia']:,} VNĐ")
```

`lambda sp: sp["gia"]` là một **hàm ẩn danh** (anonymous function) — cách viết hàm rút gọn. Ta sẽ học kỹ `lambda` ở Bài 16, giờ chỉ cần hiểu nó nói với `sorted()`: *"hãy sắp xếp dựa trên giá trị `gia` của mỗi phần tử"*.

---

#### 6. List Comprehension — đào sâu (đã giới thiệu sơ ở Bài 5)

Đây là cú pháp **được coi là "Pythonic" nhất** — ngắn gọn, hiệu năng tốt hơn vòng lặp `for` truyền thống với `append()`, và gần như là "chữ ký phong cách" của code Python chuyên nghiệp.

python

```python
# Cú pháp cơ bản: [biểu_thức for phần_tử in iterable]
so = [1, 2, 3, 4, 5]
binh_phuong = [x ** 2 for x in so]
print(binh_phuong)   # [1, 4, 9, 16, 25]

# Có điều kiện lọc (filter)
so_chan = [x for x in range(1, 21) if x % 2 == 0]
print(so_chan)   # [2, 4, 6, ..., 20]

# Có if/else trong biểu thức (khác với if lọc ở trên)
gia_tri = [10, -5, 20, -8, 15]
da_xu_ly = [x if x > 0 else 0 for x in gia_tri]   # thay số âm bằng 0
print(da_xu_ly)   # [10, 0, 20, 0, 15]

# Lồng nhiều vòng lặp trong comprehension
mau = ["Đỏ", "Xanh"]
size = ["S", "M", "L"]
bien_the_sp = [f"{m}-{s}" for m in mau for s in size]
print(bien_the_sp)
# ['Đỏ-S', 'Đỏ-M', 'Đỏ-L', 'Xanh-S', 'Xanh-M', 'Xanh-L']
```

**So sánh hiệu năng & khả năng đọc** — ví dụ thực tế: lọc danh sách khách hàng đủ điều kiện khuyến mãi:

python

```python
khach_hang = [
    {"ten": "An", "tong_chi_tieu": 5200000},
    {"ten": "Bình", "tong_chi_tieu": 800000},
    {"ten": "Chi", "tong_chi_tieu": 3100000},
]

# Cách truyền thống
khach_vip = []
for kh in khach_hang:
    if kh["tong_chi_tieu"] >= 3000000:
        khach_vip.append(kh["ten"])

# Cách Pythonic - list comprehension
khach_vip = [kh["ten"] for kh in khach_hang if kh["tong_chi_tieu"] >= 3000000]
print(khach_vip)   # ['An', 'Chi']
```

**Nguyên tắc thực chiến**: dùng comprehension khi logic đơn giản (1-2 điều kiện), gọn trong 1 dòng dễ đọc. Nếu logic phức tạp (nhiều bước xử lý, nhiều điều kiện lồng), hãy quay về vòng lặp `for` truyền thống — code rõ ràng luôn quan trọng hơn code ngắn.

---

#### 7. Unpacking — giải nén list ra biến riêng lẻ

python

```python
toa_do = [10.762622, 106.660172]
vi_do, kinh_do = toa_do
print(f"Vĩ độ: {vi_do}, Kinh độ: {kinh_do}")

# Unpacking với * - "hốt" phần còn lại vào 1 list
diem = [8, 9, 7, 6, 10, 5]
diem_cao_nhat, diem_thap_nhat, *diem_con_lai = sorted(diem, reverse=True)
```

Đợi đã — ví dụ trên hơi rối, để rõ ràng hơn:

python

```python
first, second, *rest = [1, 2, 3, 4, 5]
print(first)    # 1
print(second)   # 2
print(rest)     # [3, 4, 5]
```

Kỹ thuật này bạn đã thấy thoáng qua ở Bài 3 (`split(" | ")` rồi gán 3 biến) — giờ hiểu rõ bản chất: bất kỳ list/tuple nào cũng unpacking được, miễn số biến khớp số phần tử (hoặc dùng `*` để "hứng" phần dư).

---

#### 8. Hàm tổng hợp hữu dụng với list số

python

```python
diem_thi = [8.5, 7.0, 9.5, 6.5, 10.0]

print(sum(diem_thi))              # 41.5 - tổng
print(max(diem_thi))              # 10.0 - lớn nhất
print(min(diem_thi))              # 6.5 - nhỏ nhất
print(len(diem_thi))              # 5 - số phần tử
print(sum(diem_thi) / len(diem_thi))  # 8.3 - điểm trung bình
```

---

#### 9. Ví dụ thực chiến tổng hợp — Hệ thống quản lý kho đơn giản

python

```python
kho_hang = [
    {"ten": "Laptop Dell XPS", "gia": 28500000, "ton_kho": 5},
    {"ten": "Chuột không dây", "gia": 350000, "ton_kho": 42},
    {"ten": "Bàn phím cơ", "gia": 1250000, "ton_kho": 0},
    {"ten": "Màn hình 27inch", "gia": 5900000, "ton_kho": 8},
]

# 1. Sản phẩm hết hàng
het_hang = [sp["ten"] for sp in kho_hang if sp["ton_kho"] == 0]
print(f"Hết hàng: {het_hang}")

# 2. Tổng giá trị tồn kho
tong_gia_tri = sum(sp["gia"] * sp["ton_kho"] for sp in kho_hang)
print(f"Tổng giá trị kho: {tong_gia_tri:,} VNĐ")

# 3. Sắp xếp theo giá trị tồn kho giảm dần (sản phẩm cần nhập thêm ưu tiên xử lý trước)
kho_sap_xep = sorted(kho_hang, key=lambda sp: sp["gia"] * sp["ton_kho"], reverse=True)
for sp in kho_sap_xep:
    gia_tri_ton = sp["gia"] * sp["ton_kho"]
    print(f"{sp['ten']:<20} | Tồn: {sp['ton_kho']:>3} | Giá trị: {gia_tri_ton:>15,} VNĐ")
```

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_6.py` mô phỏng **hệ thống phân tích đơn hàng thương mại điện tử**:

python

```python
don_hang = [
    {"ma": "DH001", "khach": "An", "gia_tri": 1250000, "trang_thai": "hoan_thanh"},
    {"ma": "DH002", "khach": "Bình", "gia_tri": 480000, "trang_thai": "huy"},
    {"ma": "DH003", "khach": "An", "gia_tri": 2100000, "trang_thai": "hoan_thanh"},
    {"ma": "DH004", "khach": "Chi", "gia_tri": 890000, "trang_thai": "dang_giao"},
    {"ma": "DH005", "khach": "Bình", "gia_tri": 3200000, "trang_thai": "hoan_thanh"},
]
```

Yêu cầu (khuyến khích dùng list comprehension khi phù hợp):

1. Lọc ra danh sách các đơn hàng có `trang_thai == "hoan_thanh"`
2. Tính tổng doanh thu từ các đơn hoàn thành
3. Lấy ra danh sách **tên khách hàng không trùng lặp** đã có đơn hoàn thành (gợi ý: có thể dùng list thường trước, ta sẽ học cách tối ưu bằng `set` ở Bài 7)
4. Sắp xếp các đơn hoàn thành theo `gia_tri` giảm dần, in ra bằng f-string căn chỉnh đẹp
5. Thử thách thêm: viết đoạn code tạo ra một **bản sao độc lập** (deep copy thực sự) của `don_hang`, sửa một giá trị trong bản sao, chứng minh bằng `print` rằng list gốc không bị ảnh hưởng

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 7: Tuple & Set** — hai cấu trúc dữ liệu anh em với list nhưng có đặc tính riêng biệt (bất biến với tuple, không trùng lặp với set), giúp bạn chọn đúng công cụ cho đúng bài toán thay vì dùng list cho mọi thứ.
