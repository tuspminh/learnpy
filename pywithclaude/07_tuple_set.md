### Bài 7: Tuple & Set

Sau khi thành thạo `list`, ta học hai "người anh em họ" của nó — mỗi loại được thiết kế cho một mục đích riêng biệt. Dev chuyên nghiệp không chỉ biết dùng list cho mọi thứ, mà biết **chọn đúng cấu trúc dữ liệu cho đúng bài toán** — đây là kỹ năng phân biệt lập trình viên có kinh nghiệm với người mới.

---

### PHẦN A: TUPLE — Danh sách bất biến

#### 1. Tuple là gì?

Tuple giống list ở việc lưu trữ dãy phần tử có thứ tự, nhưng **bất biến (immutable)** — giống string, một khi tạo ra thì không thể thêm/xóa/sửa phần tử.

python

```python
toa_do_hcm = (10.762622, 106.660172)
thong_tin_sp = ("Laptop Dell", 28500000, "Điện tử")

print(type(toa_do_hcm))   # <class 'tuple'>

# toa_do_hcm[0] = 11.0   # ❌ TypeError: 'tuple' object does not support item assignment
```

**Cú pháp tạo tuple:**

python

```python
tuple_rong = ()
tuple_1_phan_tu = (5,)      # ⚠️ BẮT BUỘC có dấu phẩy, nếu không Python hiểu đó là số nguyên trong ngoặc
khong_phai_tuple = (5)      # đây chỉ là số int 5, KHÔNG phải tuple!
print(type((5,)))            # <class 'tuple'>
print(type((5)))             # <class 'int'>

# Trong thực tế, ngoặc đơn thường có thể lược bỏ
diem = 10, 20
print(type(diem))    # <class 'tuple'> - Python tự hiểu dấu phẩy nghĩa là tuple
```

#### 2. Tại sao cần tuple khi đã có list? — Đây là câu hỏi quan trọng nhất

**Lý do 1 — Bảo vệ dữ liệu khỏi bị vô tình sửa đổi (data integrity):**

python

```python
# Tọa độ địa lý của một cửa hàng KHÔNG BAO GIỜ nên bị thay đổi tình cờ trong code
VI_TRI_CUA_HANG = (10.762622, 106.660172)

def tinh_khoang_cach(vi_tri_khach, vi_tri_cua_hang):
    # Hàm này CHẮC CHẮN không thể vô tình sửa vi_tri_cua_hang
    # vì tuple không cho phép việc đó - Python tự bảo vệ bạn khỏi bug
    ...
```

Nếu dùng `list` thay vì `tuple`, một dòng code sai ở bất kỳ đâu trong codebase lớn (`vi_tri_cua_hang[0] = 0`) có thể âm thầm phá hỏng dữ liệu mà không báo lỗi gì. Tuple khiến lỗi đó **được phát hiện ngay lập tức** dưới dạng `TypeError`.

**Lý do 2 — Hiệu năng tốt hơn:** Vì Python biết tuple không đổi, nó tối ưu bộ nhớ và tốc độ truy cập tốt hơn list một chút. Với dữ liệu lớn, sự khác biệt này có ý nghĩa.

**Lý do 3 — Dùng làm khóa trong dictionary (list KHÔNG làm được điều này):**

python

```python
# Lưu trữ tọa độ (lat, lng) làm khóa cho dict - CHỈ tuple làm được vì cần hashable
gia_theo_khu_vuc = {
    (10.762622, 106.660172): "Nội thành HCM",
    (21.028511, 105.804817): "Nội thành Hà Nội",
}
```

Ta sẽ hiểu sâu hơn khái niệm "hashable" khi học `dict` ở Bài 8 — nhưng ghi nhớ ngay: **chỉ dữ liệu bất biến mới dùng làm key trong dict được**, đây là lý do tuple tồn tại song song với list.

#### 3. Unpacking tuple — ứng dụng cực kỳ phổ biến

python

```python
def tinh_thong_ke(danh_sach_diem):
    return min(danh_sach_diem), max(danh_sach_diem), sum(danh_sach_diem) / len(danh_sach_diem)

diem = [8.5, 7.0, 9.5, 6.5, 10.0]
diem_thap_nhat, diem_cao_nhat, diem_trung_binh = tinh_thong_ke(diem)
print(f"Thấp nhất: {diem_thap_nhat}, Cao nhất: {diem_cao_nhat}, TB: {diem_trung_binh:.2f}")
```

Đây chính là kỹ thuật đứng sau việc **"một hàm trả về nhiều giá trị"** trong Python (thực chất hàm trả về 1 tuple, rồi bạn unpacking nó) — bạn sẽ dùng lại rất nhiều khi học Hàm ở Bài 9.

**Hoán đổi giá trị 2 biến — mẹo kinh điển tận dụng tuple unpacking:**

python

```python
a, b = 10, 20
a, b = b, a       # hoán đổi giá trị mà không cần biến tạm!
print(a, b)        # 20 10
```

---

### PHẦN B: SET — Tập hợp không trùng lặp

#### 4. Set là gì?

Set là tập hợp các phần tử **duy nhất (không trùng lặp)** và **không có thứ tự**, được thiết kế để trả lời cực nhanh câu hỏi: *"phần tử này có tồn tại trong tập hợp không?"*

python

```python
mau_sac = {"đỏ", "xanh", "vàng", "đỏ", "xanh"}   # trùng tự động bị loại
print(mau_sac)   # {'đỏ', 'xanh', 'vàng'} - chỉ giữ giá trị duy nhất, thứ tự không đảm bảo

set_rong = set()   # ⚠️ dùng set(), KHÔNG dùng {} vì {} tạo ra dict rỗng!
```

**Ứng dụng thực tế cực kỳ phổ biến — loại bỏ trùng lặp trong dữ liệu:**

python

```python
email_dang_ky = ["a@gmail.com", "b@gmail.com", "a@gmail.com", "c@gmail.com", "b@gmail.com"]

email_duy_nhat = set(email_dang_ky)
print(email_duy_nhat)              # {'a@gmail.com', 'b@gmail.com', 'c@gmail.com'}
print(len(email_duy_nhat))         # 3 - số lượng khách hàng thực sự (không trùng)

# Chuyển lại thành list nếu cần giữ thứ tự thao tác tiếp theo
email_list_sach = list(email_duy_nhat)
```

#### 5. Tại sao set nhanh hơn list khi kiểm tra tồn tại?

Đây là kiến thức nền tảng cực kỳ quan trọng cho hiệu năng phần mềm thực tế:

python

```python
import time

# Với LIST 1 triệu phần tử
danh_sach_lon = list(range(1_000_000))
bat_dau = time.time()
print(999999 in danh_sach_lon)     # Python phải duyệt tuần tự tới khi tìm thấy
print(f"List: {time.time() - bat_dau:.6f} giây")

# Với SET 1 triệu phần tử  
set_lon = set(range(1_000_000))
bat_dau = time.time()
print(999999 in set_lon)            # Python tính toán vị trí trực tiếp qua hashing
print(f"Set: {time.time() - bat_dau:.6f} giây")
```

Về mặt lý thuyết: kiểm tra `in` trên **list** có độ phức tạp **O(n)** (càng nhiều phần tử càng chậm tuyến tính), còn trên **set** là **O(1)** (gần như tức thời bất kể bao nhiêu phần tử) nhờ cơ chế **hash table** — cùng cơ chế mà `dict` sử dụng (Bài 8).

**Ứng dụng thực tế đắt giá**: khi bạn cần kiểm tra hàng chục nghìn user ID có nằm trong "danh sách đen" (blacklist) hay không, dùng `set` thay vì `list` có thể tạo ra khác biệt hiệu năng từ vài giây xuống vài mili-giây:

python

```python
danh_sach_den = {"user_882", "user_104", "user_998"}   # set, không phải list

def kiem_tra_bi_khoa(user_id):
    return user_id in danh_sach_den   # O(1) - cực nhanh dù danh_sach_den có 1 triệu phần tử
```

#### 6. Các phép toán tập hợp (Set Operations) — sức mạnh thực sự của set

Đây là điều **list hoàn toàn không làm được**, và là lý do lớn nhất để chọn set trong bài toán phù hợp:

python

```python
khach_mua_ao = {"An", "Bình", "Chi", "Dũng"}
khach_mua_quan = {"Bình", "Chi", "Em", "Phúc"}

# Giao (Intersection) - khách mua CẢ HAI sản phẩm
print(khach_mua_ao & khach_mua_quan)             # {'Bình', 'Chi'}
print(khach_mua_ao.intersection(khach_mua_quan))  # cách viết tương đương

# Hợp (Union) - tất cả khách mua ít nhất 1 trong 2 sản phẩm
print(khach_mua_ao | khach_mua_quan)              # {'An', 'Bình', 'Chi', 'Dũng', 'Em', 'Phúc'}

# Hiệu (Difference) - khách CHỈ mua áo, không mua quần
print(khach_mua_ao - khach_mua_quan)              # {'An', 'Dũng'}

# Hiệu đối xứng (Symmetric difference) - khách chỉ mua 1 trong 2, không mua cả hai
print(khach_mua_ao ^ khach_mua_quan)              # {'An', 'Dũng', 'Em', 'Phúc'}
```

**Ứng dụng thực tế** — đây chính xác là logic đứng sau tính năng **"gợi ý sản phẩm chéo" (cross-sell)** của các sàn thương mại điện tử: *"Khách mua áo thun thường cũng mua quần jean"* — được tính bằng phép giao giữa các tập khách hàng.

#### 7. Các thao tác thêm/xóa của set

python

```python
tags_bai_viet = {"python", "lập trình"}

tags_bai_viet.add("tutorial")           # thêm 1 phần tử
tags_bai_viet.update(["ai", "2026"])    # thêm nhiều phần tử cùng lúc
print(tags_bai_viet)

tags_bai_viet.discard("ai")             # xóa, KHÔNG báo lỗi nếu phần tử không tồn tại
tags_bai_viet.remove("2026")            # xóa, BÁO LỖI KeyError nếu không tồn tại
```

**Nguyên tắc thực chiến**: dùng `discard()` khi bạn không chắc phần tử có tồn tại hay không (an toàn hơn), dùng `remove()` khi bạn *chắc chắn* nó phải tồn tại và muốn được cảnh báo nếu giả định đó sai (giúp phát hiện bug sớm).

#### 8. Set Comprehension

Cú pháp tương tự list comprehension nhưng dùng ngoặc nhọn `{}`:

python

```python
so = [1, 2, 2, 3, 3, 3, 4, 5, 5]
so_chan_duy_nhat = {x for x in so if x % 2 == 0}
print(so_chan_duy_nhat)   # {2, 4}
```

---

#### 9. Bảng so sánh — Khi nào dùng gì?

| Đặc điểm | `list` | `tuple` | `set` |
| --- | --- | --- | --- |
| Thứ tự | Có  | Có  | Không |
| Trùng lặp | Cho phép | Cho phép | Không cho phép |
| Thay đổi được | Có (mutable) | Không (immutable) | Có (nhưng phần tử phải bất biến) |
| Truy cập theo index | Có `list[0]` | Có `tuple[0]` | Không có index |
| Dùng làm key dict | Không | Có  | Không |
| Tốc độ kiểm tra `in` | Chậm — O(n) | Chậm — O(n) | Rất nhanh — O(1) |

**Quy tắc quyết định thực chiến:**

- Dữ liệu cần **thay đổi liên tục, có thứ tự** (giỏ hàng, danh sách đơn hàng) → `list`
- Dữ liệu **cố định, không nên bị sửa** (tọa độ GPS, RGB màu, cấu hình hằng số) → `tuple`
- Cần **loại bỏ trùng lặp** hoặc **kiểm tra tồn tại cực nhanh** trên tập dữ liệu lớn (blacklist, tags, ID duy nhất) → `set`

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_7.py` mô phỏng **hệ thống phân tích hành vi mua sắm khách hàng**:

python

```python
khach_mua_thang_1 = ["An", "Bình", "Chi", "An", "Dũng", "Bình"]
khach_mua_thang_2 = ["Bình", "Chi", "Em", "Phúc", "An"]

toa_do_kho_hang = (10.762622, 106.660172)   # KHÔNG được sửa - đại diện dữ liệu cố định
```

Yêu cầu:

1. Chuyển 2 danh sách trên thành `set` để loại bỏ trùng lặp, in ra số khách hàng thực sự duy nhất mỗi tháng
2. Tìm nhóm khách hàng **trung thành** (mua cả tháng 1 và tháng 2) bằng phép giao
3. Tìm nhóm khách hàng **mới** ở tháng 2 (không mua ở tháng 1) bằng phép hiệu
4. Tìm nhóm khách hàng **đã rời bỏ** (mua tháng 1 nhưng không quay lại tháng 2)
5. Thử unpacking `toa_do_kho_hang` thành 2 biến `vi_do, kinh_do`, sau đó thử gán `toa_do_kho_hang[0] = 0` để tận mắt thấy lỗi `TypeError` — điều này giúp bạn khắc sâu vì sao tuple bất biến lại hữu ích

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 8: Dictionary** — cấu trúc dữ liệu quan trọng bậc nhất trong Python thực tế, dùng để biểu diễn dữ liệu dạng key-value, chính là nền tảng của JSON — định dạng dữ liệu phổ biến nhất khi làm việc với API trong thế giới lập trình hiện đại.
