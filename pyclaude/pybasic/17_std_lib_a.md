Vai trò giảng viên chuyên nghiệp + lập trình viên Python chuyên nghiệp này tôi đã lưu vào bộ nhớ từ bài 3 và đã duy trì xuyên suốt 16 bài học qua — sẽ tiếp tục áp dụng nghiêm túc cho toàn bộ hành trình còn lại. Giờ vào bài học cuối cùng của Giai đoạn 2 — Trung cấp.

### 📘 Bài 17: Thư viện chuẩn hữu ích (`datetime`, `os`, `re`, `collections`, `itertools`)

Đây là bộ công cụ mà dev Python chuyên nghiệp dùng **hàng ngày** — thay vì tự viết lại logic xử lý ngày giờ, tìm kiếm mẫu văn bản, hay đếm/nhóm dữ liệu, thư viện chuẩn đã tối ưu sẵn cho bạn. Nắm chắc bài này giúp code của bạn ngắn hơn, ít bug hơn, và "trông chuyên nghiệp" hơn rất nhiều.

---

### PHẦN A: `datetime` — Xử lý ngày giờ

#### 1. Các đối tượng cơ bản

python

```python
from datetime import datetime, date, timedelta

# Thời điểm hiện tại
bay_gio = datetime.now()
print(bay_gio)                    # 2026-07-05 14:32:07.123456
print(type(bay_gio))               # <class 'datetime.datetime'>

hom_nay = date.today()
print(hom_nay)                     # 2026-07-05 - chỉ có ngày, không có giờ

# Tạo ngày giờ cụ thể
ngay_sinh = datetime(2001, 5, 20, 8, 30, 0)   # năm, tháng, ngày, giờ, phút, giây
print(ngay_sinh)                    # 2001-05-20 08:30:00
```

#### 2. Định dạng hiển thị (`strftime`) và phân tích chuỗi (`strptime`)

python

```python
bay_gio = datetime.now()

# strftime - datetime -> chuỗi có định dạng (format TIME -> String)
print(bay_gio.strftime("%d/%m/%Y"))               # 05/07/2026
print(bay_gio.strftime("%H:%M:%S"))                # 14:32:07
print(bay_gio.strftime("%A, %d %B %Y"))            # Sunday, 05 July 2026
print(bay_gio.strftime("%Y-%m-%d %H:%M"))          # 2026-07-05 14:32

# strptime - chuỗi -> datetime (String -> parse TIME) - NGƯỢC LẠI
chuoi_ngay = "20/05/2001"
ngay_sinh = datetime.strptime(chuoi_ngay, "%d/%m/%Y")
print(ngay_sinh)   # 2001-05-20 00:00:00
```

**Bảng mã định dạng quan trọng cần nhớ:**

| Mã  | Ý nghĩa | Ví dụ |
| --- | --- | --- |
| `%Y` | Năm 4 số | 2026 |
| `%m` | Tháng (01-12) | 07  |
| `%d` | Ngày (01-31) | 05  |
| `%H` | Giờ 24h | 14  |
| `%M` | Phút | 32  |
| `%S` | Giây | 07  |
| `%A` | Tên thứ đầy đủ | Sunday |
| `%B` | Tên tháng đầy đủ | July |

**Ứng dụng thực tế cực kỳ phổ biến** — parse timestamp từ dữ liệu log hoặc API trả về, rồi định dạng lại cho người dùng xem:

python

```python
timestamp_tu_api = "2026-07-05T14:32:07"
thoi_gian = datetime.strptime(timestamp_tu_api, "%Y-%m-%dT%H:%M:%S")
print(f"Đơn hàng được tạo lúc: {thoi_gian.strftime('%H:%M ngày %d/%m/%Y')}")
```

#### 3. Tính toán với `timedelta`

python

```python
from datetime import datetime, timedelta

bay_gio = datetime.now()

# Cộng/trừ thời gian
sau_7_ngay = bay_gio + timedelta(days=7)
truoc_30_phut = bay_gio - timedelta(minutes=30)
sau_2_tuan = bay_gio + timedelta(weeks=2)

print(sau_7_ngay.strftime("%d/%m/%Y"))

# Tính khoảng cách giữa 2 thời điểm
ngay_dat_hang = datetime(2026, 6, 20)
ngay_giao_hang = datetime(2026, 7, 5)
khoang_cach = ngay_giao_hang - ngay_dat_hang

print(khoang_cach.days)   # 15 - số ngày giữa 2 mốc
```

**Ứng dụng thực tế** — tính hạn thanh toán, kiểm tra hết hạn khuyến mãi, tính tuổi:

python

```python
def kiem_tra_qua_han_thanh_toan(ngay_tao_don: datetime, han_thanh_toan_ngay: int = 7) -> bool:
    han_cuoi = ngay_tao_don + timedelta(days=han_thanh_toan_ngay)
    return datetime.now() > han_cuoi

def tinh_tuoi(ngay_sinh: date) -> int:
    hom_nay = date.today()
    tuoi = hom_nay.year - ngay_sinh.year
    if (hom_nay.month, hom_nay.day) < (ngay_sinh.month, ngay_sinh.day):
        tuoi -= 1   # chưa tới sinh nhật năm nay
    return tuoi
```

**Lưu ý về múi giờ (timezone)** — trong thực tế production, đặc biệt hệ thống có người dùng ở nhiều quốc gia, luôn nên dùng `datetime` "aware" (có gắn timezone) thay vì "naive" như trên, dùng module `zoneinfo` (Python 3.9+):

python

```python
from datetime import datetime
from zoneinfo import ZoneInfo

gio_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
gio_ny = datetime.now(ZoneInfo("America/New_York"))
print(gio_vn.strftime("%H:%M %Z"))
```

---

### PHẦN B: `re` — Regular Expression (Biểu thức chính quy)

#### 4. `re` là gì và tại sao cần thiết

Nhớ lại Bài 3, bạn dùng `.split()`, `.find()`, `in` để xử lý chuỗi. Nhưng có những bài toán mà cách tiếp cận đó bất lực — ví dụ: *"kiểm tra chuỗi có đúng định dạng email không"*, *"tìm mọi số điện thoại trong đoạn văn bản"*. Đây là lúc **regex** — "ngôn ngữ mini" chuyên dùng để mô tả **mẫu (pattern)** trong văn bản — phát huy sức mạnh.

python

```python
import re

# match() - kiểm tra chuỗi có KHỚP mẫu từ ĐẦU không
ket_qua = re.match(r"\d+", "123abc")
print(ket_qua.group() if ket_qua else "Không khớp")   # '123'

# search() - tìm mẫu XUẤT HIỆN Ở ĐÂU trong chuỗi (không cần từ đầu)
ket_qua = re.search(r"\d+", "Đơn hàng số 12345 đã giao")
print(ket_qua.group())   # '12345'

# findall() - tìm TẤT CẢ các đoạn khớp mẫu, trả về LIST
so_dien_thoai_trong_van_ban = "Liên hệ 0912345678 hoặc 0987654321 để được hỗ trợ"
ket_qua = re.findall(r"\d{10}", so_dien_thoai_trong_van_ban)
print(ket_qua)   # ['0912345678', '0987654321']
```

#### 5. Các ký hiệu regex cốt lõi cần nhớ

| Ký hiệu | Ý nghĩa | Ví dụ |
| --- | --- | --- |
| `\d` | Một chữ số (0-9) | `\d{3}` = đúng 3 chữ số |
| `\w` | Chữ, số, hoặc `_` | `\w+` = 1 hoặc nhiều ký tự chữ/số |
| `\s` | Khoảng trắng | `\s+` = 1 hoặc nhiều dấu cách |
| `.` | Bất kỳ ký tự nào | `a.c` = "abc", "axc"... |
| `+` | 1 hoặc nhiều lần | `\d+` |
| `*` | 0 hoặc nhiều lần | `\d*` |
| `?` | 0 hoặc 1 lần | `\d?` |
| `{n}` | Chính xác n lần | `\d{4}` |
| `{n,m}` | Từ n đến m lần | `\d{8,10}` |
| `^` | Bắt đầu chuỗi | `^Xin chào` |
| `$` | Kết thúc chuỗi | `kết thúc$` |
| `[...]` | Một trong các ký tự | `[aeiou]` |
| `\\|` | HOẶC | `mèo\\|chó` |

**Ứng dụng thực tế cực kỳ phổ biến** — validate định dạng email trong hệ thống đăng ký:

python

```python
def validate_email(email: str) -> bool:
    mau = r"^[\w.-]+@[\w.-]+\.\w+$"
    return re.match(mau, email) is not None

print(validate_email("an.nguyen@gmail.com"))    # True
print(validate_email("khong_hop_le"))            # False
```

**Giải nghĩa mẫu trên**: `^[\w.-]+` (bắt đầu bằng chữ/số/`.`/`-`) + `@` (bắt buộc có ký tự @) + `[\w.-]+` (tên domain) + `\.` (dấu chấm literal, cần `\` để thoát vì `.` bình thường nghĩa là "bất kỳ ký tự") + `\w+$` (đuôi domain, kết thúc chuỗi).

#### 6. `sub()` — Thay thế theo mẫu (mạnh hơn `.replace()` của Bài 3)

python

```python
# Ẩn số điện thoại để bảo vệ thông tin cá nhân trong log
van_ban = "Khách hàng liên hệ qua số 0912345678"
van_ban_an = re.sub(r"\d{10}", "**********", van_ban)
print(van_ban_an)   # 'Khách hàng liên hệ qua số **********'

# Chuẩn hóa nhiều khoảng trắng thừa thành 1 khoảng trắng - rất hay dùng khi làm sạch dữ liệu
chuoi_tho = "Nguyễn    Văn      An"
chuoi_sach = re.sub(r"\s+", " ", chuoi_tho)
print(chuoi_sach)   # 'Nguyễn Văn An'
```

#### 7. Compile pattern — tối ưu khi dùng lại nhiều lần

python

```python
# Nếu dùng CÙNG MỘT mẫu regex nhiều lần (ví dụ validate hàng nghìn email),
# compile trước giúp tăng tốc đáng kể vì Python không phải "biên dịch" lại mẫu mỗi lần
mau_email = re.compile(r"^[\w.-]+@[\w.-]+\.\w+$")

danh_sach_email = ["an@gmail.com", "loi_dinh_dang", "binh@yahoo.com"]
email_hop_le = [email for email in danh_sach_email if mau_email.match(email)]
print(email_hop_le)   # ['an@gmail.com', 'binh@yahoo.com']
```

---

### PHẦN C: `collections` — Cấu trúc dữ liệu chuyên dụng

#### 8. `Counter` — đếm phần tử cực nhanh, cực gọn

python

```python
from collections import Counter

san_pham_ban = ["Áo", "Quần", "Áo", "Giày", "Áo", "Quần", "Mũ"]

# Cách thông thường (đã biết) - dài dòng
dem_thu_cong = {}
for sp in san_pham_ban:
    dem_thu_cong[sp] = dem_thu_cong.get(sp, 0) + 1

# Cách dùng Counter - GỌN, và có nhiều tiện ích built-in
dem = Counter(san_pham_ban)
print(dem)                        # Counter({'Áo': 3, 'Quần': 2, 'Giày': 1, 'Mũ': 1})
print(dem.most_common(2))         # [('Áo', 3), ('Quần', 2)] - TOP 2 phổ biến nhất!
print(dem["Áo"])                   # 3 - truy cập như dict thông thường
```

**Ứng dụng thực tế cực kỳ phổ biến** — bảng xếp hạng sản phẩm bán chạy nhất, phân tích từ khóa phổ biến trong feedback khách hàng:

python

```python
def top_san_pham_ban_chay(don_hang: list[dict], top_n: int = 3):
    ten_sp_list = [don["san_pham"] for don in don_hang]
    return Counter(ten_sp_list).most_common(top_n)
```

#### 9. `defaultdict` — đã gặp ở Bài 8, ôn lại vị trí trong hệ sinh thái `collections`

python

```python
from collections import defaultdict

# defaultdict(list) - tự tạo list rỗng cho key mới, cực hữu dụng khi NHÓM dữ liệu
don_hang_theo_khach = defaultdict(list)
giao_dich = [("An", "DH001"), ("Bình", "DH002"), ("An", "DH003")]

for khach, ma_don in giao_dich:
    don_hang_theo_khach[khach].append(ma_don)

print(dict(don_hang_theo_khach))   # {'An': ['DH001', 'DH003'], 'Bình': ['DH002']}
```

#### 10. `namedtuple` — Tuple có tên trường, thay thế class đơn giản

python

```python
from collections import namedtuple

# Tạo "kiểu tuple" mới có TÊN cho từng trường - đọc code rõ nghĩa hơn tuple thường
DiemGPS = namedtuple("DiemGPS", ["vi_do", "kinh_do"])

vi_tri_kho = DiemGPS(10.762622, 106.660172)
print(vi_tri_kho.vi_do)     # 10.762622 - truy cập bằng TÊN, không phải index [0]
print(vi_tri_kho[0])         # 10.762622 - vẫn truy cập được bằng index (vẫn là tuple)

# So sánh: tuple thường phải nhớ index 0 là gì, 1 là gì
vi_tri_thuong = (10.762622, 106.660172)   # phải nhớ [0] là vĩ độ, [1] là kinh độ - dễ nhầm
```

`namedtuple` là lựa chọn tuyệt vời khi bạn cần một cấu trúc dữ liệu **đơn giản, bất biến, có tên trường rõ ràng** nhưng chưa cần đầy đủ sức mạnh của `class` (Bài 13) — nhẹ hơn, code ngắn hơn class thông thường.

#### 11. `deque` — Hàng đợi 2 đầu hiệu năng cao

python

```python
from collections import deque

hang_doi = deque(["Đơn 1", "Đơn 2", "Đơn 3"])

hang_doi.append("Đơn 4")          # thêm CUỐI - giống list
hang_doi.appendleft("Đơn 0")      # thêm ĐẦU - list KHÔNG hỗ trợ hiệu quả (O(n)), deque làm O(1)

print(hang_doi.popleft())          # 'Đơn 0' - lấy và xóa phần tử ĐẦU - O(1), rất nhanh
print(hang_doi)                     # deque(['Đơn 1', 'Đơn 2', 'Đơn 3', 'Đơn 4'])
```

**Tại sao dùng `deque` thay vì `list` cho hàng đợi?** Vì `list.pop(0)` hoặc `list.insert(0, x)` có độ phức tạp **O(n)** (phải dịch chuyển toàn bộ phần tử còn lại), còn `deque` được thiết kế tối ưu cho việc thêm/xóa ở **cả hai đầu** với độ phức tạp **O(1)**. Nhớ lại Bài 6, ta đã dùng `list.pop(0)` để mô phỏng hàng đợi — với hàng đợi lớn trong hệ thống thực tế, `deque` là lựa chọn đúng đắn hơn nhiều.

---

### PHẦN D: `itertools` — Công cụ tổ hợp/lặp nâng cao

#### 12. Các hàm hữu dụng nhất

python

```python
from itertools import combinations, permutations, product, chain

# combinations - tổ hợp (không quan tâm thứ tự)
mau_sac = ["Đỏ", "Xanh", "Vàng"]
print(list(combinations(mau_sac, 2)))
# [('Đỏ', 'Xanh'), ('Đỏ', 'Vàng'), ('Xanh', 'Vàng')]

# permutations - chỉnh hợp (CÓ quan tâm thứ tự)
print(list(permutations(mau_sac, 2)))
# [('Đỏ', 'Xanh'), ('Đỏ', 'Vàng'), ('Xanh', 'Đỏ'), ('Xanh', 'Vàng'), ('Vàng', 'Đỏ'), ('Vàng', 'Xanh')]

# product - tích Descartes (mọi tổ hợp giữa nhiều dãy) - thay thế comprehension lồng nhiều vòng
size = ["S", "M", "L"]
mau = ["Đỏ", "Xanh"]
print(list(product(size, mau)))
# [('S', 'Đỏ'), ('S', 'Xanh'), ('M', 'Đỏ'), ('M', 'Xanh'), ('L', 'Đỏ'), ('L', 'Xanh')]

# chain - nối nhiều iterable thành MỘT luồng liên tục, không cần tạo list mới tốn bộ nhớ
danh_sach_1 = ["An", "Bình"]
danh_sach_2 = ["Chi", "Dũng"]
for ten in chain(danh_sach_1, danh_sach_2):
    print(ten)   # An, Bình, Chi, Dũng
```

**Ứng dụng thực tế** — sinh mọi biến thể sản phẩm (size × màu) cho hệ thống quản lý kho, thay thế comprehension lồng ở Bài 6:

python

```python
bien_the_sp = [f"{s}-{m}" for s, m in product(size, mau)]
print(bien_the_sp)   # ['S-Đỏ', 'S-Xanh', 'M-Đỏ', ...]
```

---

### PHẦN E: `os` và `pathlib` — Tương tác hệ điều hành (ôn lại + mở rộng từ Bài 11)

python

```python
import os

print(os.getenv("DATABASE_URL", "sqlite:///default.db"))   # đọc biến môi trường, có giá trị mặc định
print(os.cpu_count())                                        # số nhân CPU của máy
for ten_file in os.listdir("."):                              # liệt kê file trong thư mục hiện tại
    print(ten_file)
```

**Ứng dụng thực tế quan trọng của `os.getenv()`** — đọc thông tin nhạy cảm (API key, mật khẩu database) từ **biến môi trường** thay vì viết cứng (hardcode) trong code — đây là chuẩn bảo mật bắt buộc trong mọi hệ thống production, ta sẽ đào sâu ở Bài 18 với file `.env`.

---

#### 13. Ví dụ thực chiến tổng hợp — Phân tích log server bằng regex + Counter + datetime

python

```python
import re
from collections import Counter
from datetime import datetime

log_mau = """
2026-07-05 10:15:23 INFO Đơn hàng DH001 tạo thành công
2026-07-05 10:16:45 ERROR Kết nối database thất bại
2026-07-05 10:20:01 INFO Đơn hàng DH002 tạo thành công
2026-07-05 10:22:30 ERROR Timeout khi gọi API thanh toán
2026-07-05 10:25:10 INFO Đơn hàng DH003 tạo thành công
""".strip()

dong_log = log_mau.split("\n")
mau_regex = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\w+) (.+)")

muc_do_list = []
for dong in dong_log:
    ket_qua = mau_regex.match(dong)
    if ket_qua:
        thoi_gian_str, muc_do, noi_dung = ket_qua.groups()
        muc_do_list.append(muc_do)
        if muc_do == "ERROR":
            print(f"⚠️  {thoi_gian_str}: {noi_dung}")

print(f"\nThống kê mức độ log: {Counter(muc_do_list)}")
```

**Kết quả:**

```
⚠️  2026-07-05 10:16:45: Kết nối database thất bại
⚠️  2026-07-05 10:22:30: Timeout khi gọi API thanh toán

Thống kê mức độ log: Counter({'INFO': 3, 'ERROR': 2})
```

Ví dụ này thể hiện cách các module thư viện chuẩn **kết hợp với nhau** trong bài toán thực tế — regex để parse cấu trúc log, Counter để thống kê nhanh, và datetime (nếu cần) để tiếp tục phân tích theo mốc thời gian.

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_17.py` xây dựng **hệ thống phân tích đơn hàng từ dữ liệu văn bản thô**:

python

```python
du_lieu_tho = """
Đơn DH2026-001 | KH: Nguyễn An | SĐT: 0912345678 | Ngày: 01/07/2026 | Tổng: 1250000
Đơn DH2026-002 | KH: Trần Bình | SĐT: 0987654321 | Ngày: 03/07/2026 | Tổng: 480000
Đơn DH2026-003 | KH: Nguyễn An | SĐT: 0912345678 | Ngày: 05/07/2026 | Tổng: 2100000
"""
```

Yêu cầu:

1. Dùng `re.findall()` với regex phù hợp để trích xuất TẤT CẢ mã đơn hàng (dạng `DH2026-XXX`) từ `du_lieu_tho`
2. Dùng regex trích xuất toàn bộ số điện thoại (10 chữ số) trong văn bản, dùng `re.sub()` để ẩn 4 số cuối mỗi số điện thoại (VD: `0912345***`)
3. Parse chuỗi ngày `"01/07/2026"` thành object `datetime` bằng `strptime`, tính số ngày giữa đơn hàng đầu tiên và đơn hàng cuối cùng
4. Dùng `Counter` đếm số lần mỗi khách hàng xuất hiện trong dữ liệu, in ra khách hàng có nhiều đơn nhất bằng `most_common(1)`
5. Dùng `defaultdict(list)` nhóm các mã đơn hàng theo tên khách hàng
6. Thử thách thêm: dùng `itertools.combinations` để sinh mọi cặp khách hàng (không trùng), giả lập tính năng "gợi ý khách hàng có thể giới thiệu nhau" cho một chương trình referral

---

🎉 **Chúc mừng bạn đã hoàn thành toàn bộ Giai đoạn 2 — Trung cấp!** Từ giờ bạn đã có trong tay: file I/O, tổ chức code theo module/package, OOP đầy đủ (kế thừa, đa hình, abstraction), iterator/generator/decorator, functional programming, và bộ thư viện chuẩn thiết yếu — đủ để đọc hiểu và đóng góp vào codebase Python thực tế cỡ trung bình.

Làm bài tập xong gửi tôi xem nhé. Sau đó ta bước vào **Giai đoạn 3 — Nâng cao & Thực chiến**, bắt đầu với **Bài 18: Quản lý môi trường ảo, pip, dependency chuyên sâu** — nơi ta hoàn thiện quy trình làm việc chuẩn ngành với `requirements.txt`, biến môi trường `.env`, và cách tổ chức một dự án Python sẵn sàng đưa lên production.
