Vai trò này tôi đã ghi nhớ và đang duy trì xuyên suốt từ đầu hành trình — tiếp tục áp dụng nghiêm túc. Giờ vào bài học giải mã những cơ chế "ẩn" mà bạn đã dùng từ Bài 5 đến giờ mà chưa biết bản chất thực sự.

### 📘 Bài 15: Iterator, Generator, Decorator

Đây là bài học nâng tầm tư duy Python của bạn lên mức "hiểu bên dưới lớp vỏ" — bạn sẽ hiểu **tại sao** `for x in [1,2,3]` chạy được, **tại sao** `range(10_000_000)` không tốn RAM, và học kỹ thuật **decorator** — thứ xuất hiện khắp nơi trong Flask, FastAPI, pytest mà bạn sẽ dùng trong tương lai.

---

### PHẦN A: ITERATOR — Cơ chế thực sự của vòng lặp `for`

#### 1. Iterable vs Iterator — phân biệt then chốt

python

```python
danh_sach = [1, 2, 3]

# Khi bạn viết: for x in danh_sach:
# Python NGẦM thực hiện các bước sau:
iterator = iter(danh_sach)     # Bước 1: lấy ITERATOR từ ITERABLE
print(next(iterator))           # 1  - Bước 2: gọi next() để lấy phần tử kế tiếp
print(next(iterator))           # 2
print(next(iterator))           # 3
# print(next(iterator))         # ❌ StopIteration - hết phần tử, vòng lặp for tự bắt lỗi này và dừng
```

**Định nghĩa chính xác:**

- **Iterable** (có thể lặp): bất kỳ object có thể tạo ra iterator qua hàm `iter()` — list, tuple, dict, set, string...
- **Iterator**: object "nhớ vị trí hiện tại", mỗi lần gọi `next()` trả về phần tử kế tiếp, đến khi hết thì raise `StopIteration`

**`for` thực chất là một "vòng lặp `while` che giấu"**:

python

```python
# Đây CHÍNH XÁC là những gì Python làm bên dưới khi bạn viết for x in danh_sach:
iterator = iter(danh_sach)
while True:
    try:
        x = next(iterator)
        print(x)
    except StopIteration:
        break
```

#### 2. Tự viết class Iterator — hiểu sâu cơ chế `__iter__` và `__next__`

python

```python
class DemLui:
    """Iterator tự viết - đếm lùi từ N về 0"""
    def __init__(self, bat_dau):
        self.hien_tai = bat_dau

    def __iter__(self):
        return self   # object này TỰ LÀ iterator của chính nó

    def __next__(self):
        if self.hien_tai < 0:
            raise StopIteration
        gia_tri = self.hien_tai
        self.hien_tai -= 1
        return gia_tri


for so in DemLui(5):
    print(so)   # 5, 4, 3, 2, 1, 0
```

Khi Python thấy `for so in DemLui(5):`, nó gọi `iter(DemLui(5))` → chạy `__iter__` → trả về chính object → rồi lặp gọi `__next__()` liên tục cho đến khi gặp `StopIteration`. **Đây chính là cơ chế đứng sau MỌI vòng lặp `for` bạn đã viết từ Bài 5**, kể cả trên `list`, `dict`, `range`.

---

### PHẦN B: GENERATOR — Cách viết Iterator gọn gàng và tiết kiệm bộ nhớ

#### 3. Vấn đề mà Generator giải quyết

python

```python
def lay_binh_phuong_list(n):
    """Cách THÔNG THƯỜNG - tính TOÀN BỘ và lưu vào list ngay lập tức"""
    ket_qua = []
    for i in range(n):
        ket_qua.append(i ** 2)
    return ket_qua

# Nếu n = 100 triệu, list này chiếm HÀNG GB RAM ngay lập tức, dù bạn chỉ cần dùng vài phần tử đầu!
```

**Generator giải quyết bằng "lazy evaluation"** — chỉ tính từng giá trị **khi được yêu cầu**, không tính trước toàn bộ:

python

```python
def lay_binh_phuong_generator(n):
    """Generator - dùng yield thay vì return + append"""
    for i in range(n):
        yield i ** 2     # "TẠM DỪNG" tại đây, trả về giá trị, rồi chờ lần gọi next() kế tiếp


gen = lay_binh_phuong_generator(100_000_000)   # KHÔNG tính gì cả, tạo tức thời
print(gen)              # <generator object ...>
print(next(gen))         # 0  - tính TỚI ĐÂU, cần TỚI ĐÂU
print(next(gen))         # 1
print(next(gen))         # 4

for x in lay_binh_phuong_generator(5):   # dùng for như bình thường
    print(x)              # 0, 1, 4, 9, 16
```

**`yield` khác `return` ở điểm mấu chốt**: `return` kết thúc hàm hoàn toàn, còn `yield` **"tạm dừng"** hàm tại đó, ghi nhớ toàn bộ trạng thái (giá trị biến local, vị trí đang chạy), và **tiếp tục từ đúng vị trí đó** ở lần gọi `next()` kế tiếp — như một "hàm có thể tạm ngưng và tiếp tục".

#### 4. So sánh hiệu năng bộ nhớ thực tế

python

```python
import sys

list_thuong = [x ** 2 for x in range(1_000_000)]
gen = (x ** 2 for x in range(1_000_000))    # generator expression - cú pháp gọn như comprehension nhưng dùng ()

print(sys.getsizeof(list_thuong))   # khoảng 8,000,000+ bytes (~8MB)
print(sys.getsizeof(gen))            # khoảng 200 bytes - KHÔNG PHỤ THUỘC vào số lượng phần tử!
```

Đây là lý do generator **cực kỳ quan trọng khi xử lý dữ liệu lớn thực tế**: đọc file log hàng GB, xử lý dữ liệu streaming từ API, xử lý dữ liệu huấn luyện AI theo từng batch — bạn không thể (và không nên) load hết vào RAM.

**Ứng dụng thực tế** — xử lý file log khổng lồ mà không làm crash RAM:

python

```python
def doc_dong_loi(duong_dan_log):
    """Generator - đọc file TỪNG DÒNG, chỉ giữ dòng có lỗi trong bộ nhớ"""
    with open(duong_dan_log, "r", encoding="utf-8") as f:
        for dong in f:
            if "ERROR" in dong:
                yield dong.strip()

# Dù file log nặng 50GB, generator này chỉ giữ 1 dòng trong RAM tại một thời điểm
for dong_loi in doc_dong_loi("server.log"):
    print(dong_loi)
```

#### 5. Generator Expression — cú pháp rút gọn

python

```python
# List comprehension (Bài 6) - tính TOÀN BỘ ngay, dùng []
binh_phuong_list = [x ** 2 for x in range(10)]

# Generator expression - tính LAZY, dùng ()
binh_phuong_gen = (x ** 2 for x in range(10))

print(sum(binh_phuong_gen))    # 285 - có thể dùng trực tiếp với sum(), max(), min()... không cần chuyển thành list
```

**Nguyên tắc thực chiến khi chọn giữa list comprehension và generator:**

- Cần **dùng nhiều lần**, cần **index truy cập**, hoặc **dữ liệu nhỏ** → dùng `list comprehension`
- Chỉ cần **duyệt qua MỘT LẦN**, dữ liệu **lớn hoặc không biết trước kích thước** → dùng `generator`

python

```python
# Generator CHỈ dùng được MỘT LẦN - đây là điểm khác biệt quan trọng cần nhớ
gen = (x for x in range(5))
print(list(gen))    # [0, 1, 2, 3, 4]
print(list(gen))    # [] - RỖNG! generator đã "cạn", không thể lặp lại lần 2
```

#### 6. `yield` nhiều lần — pipeline xử lý dữ liệu thực tế

python

```python
def loc_don_hang_hop_le(don_hang_list):
    """Generator lọc và chuẩn hóa dữ liệu - pattern rất phổ biến trong xử lý dữ liệu thực tế"""
    for don in don_hang_list:
        if don.get("gia_tri", 0) > 0:
            yield {
                "ma": don["ma"],
                "gia_tri_da_chuan_hoa": round(don["gia_tri"], 2)
            }


don_hang_tho = [
    {"ma": "DH001", "gia_tri": 250000.567},
    {"ma": "DH002", "gia_tri": -100},      # dữ liệu lỗi, bị lọc bỏ
    {"ma": "DH003", "gia_tri": 480000.123},
]

for don in loc_don_hang_hop_le(don_hang_tho):
    print(don)
```

**Ứng dụng thực tế then chốt**: các pipeline xử lý dữ liệu (ETL - Extract, Transform, Load) trong công việc phân tích dữ liệu thực tế thường được xây dựng bằng cách **kết hợp nhiều generator liên tiếp**, mỗi generator xử lý một bước, dữ liệu "chảy" qua từng bước mà không cần load toàn bộ vào RAM giữa các bước.

---

### PHẦN C: DECORATOR — "Bọc" hành vi mới quanh hàm có sẵn

#### 7. Vấn đề Decorator giải quyết

Giả sử bạn muốn **đo thời gian chạy** của nhiều hàm khác nhau, mà không muốn viết code đo thời gian lặp lại trong mỗi hàm:

python

```python
import time

def tinh_tong_don_hang(don_hang):
    time.sleep(1)   # giả lập xử lý tốn thời gian
    return sum(don_hang)

# ❌ Cách KHÔNG chuyên nghiệp - phải sửa BÊN TRONG mỗi hàm cần đo
def tinh_tong_don_hang_co_do_thoi_gian(don_hang):
    bat_dau = time.time()
    time.sleep(1)
    ket_qua = sum(don_hang)
    print(f"Thời gian chạy: {time.time() - bat_dau:.2f}s")
    return ket_qua
```

**Decorator giải quyết bằng cách "bọc" hàm gốc mà KHÔNG cần sửa code bên trong nó:**

python

```python
import time
from functools import wraps

def do_thoi_gian(ham_goc):
    """Decorator - nhận 1 HÀM, trả về 1 HÀM MỚI đã được 'bọc' thêm logic"""
    @wraps(ham_goc)   # giữ nguyên tên, docstring của hàm gốc (kỹ thuật chuẩn, giải thích ở dưới)
    def ham_wrapper(*args, **kwargs):
        bat_dau = time.time()
        ket_qua = ham_goc(*args, **kwargs)     # gọi hàm GỐC bên trong
        print(f"[{ham_goc.__name__}] Thời gian chạy: {time.time() - bat_dau:.3f}s")
        return ket_qua
    return ham_wrapper


@do_thoi_gian   # cú pháp "@" - áp dụng decorator cho hàm ngay dưới nó
def tinh_tong_don_hang(don_hang):
    time.sleep(1)
    return sum(don_hang)


ket_qua = tinh_tong_don_hang([100000, 200000, 300000])
# [tinh_tong_don_hang] Thời gian chạy: 1.001s
print(ket_qua)   # 600000
```

**Cú pháp `@do_thoi_gian` thực chất là "cú pháp đường tắt" (syntactic sugar) của:**

python

```python
def tinh_tong_don_hang(don_hang):
    time.sleep(1)
    return sum(don_hang)

tinh_tong_don_hang = do_thoi_gian(tinh_tong_don_hang)   # "bọc" hàm gốc, gán lại cùng tên
```

Decorator **thay thế** hàm gốc bằng một phiên bản mới có thêm hành vi "bọc quanh" — hàm gốc vẫn được gọi bên trong, nhưng giờ có thêm logic trước/sau khi nó chạy.

#### 8. Tại sao cần `*args, **kwargs` và `@wraps` trong decorator

python

```python
def do_thoi_gian(ham_goc):
    @wraps(ham_goc)
    def ham_wrapper(*args, **kwargs):    # nhận MỌI kiểu tham số, vì decorator không biết trước
                                            # hàm được bọc sẽ có bao nhiêu tham số gì
        ket_qua = ham_goc(*args, **kwargs)   # "chuyển tiếp" toàn bộ tham số cho hàm gốc
        return ket_qua
    return ham_wrapper
```

Vì decorator có thể áp dụng cho **bất kỳ hàm nào** (nhận 1, 2, hay 10 tham số khác nhau), `wrapper` phải dùng `*args, **kwargs` (nhớ lại Bài 9) để "chuyển tiếp" mọi tham số mà không cần biết trước hàm gốc nhận gì.

`@wraps(ham_goc)` (từ module `functools`) giữ nguyên `__name__`, docstring của hàm gốc — nếu không có nó, `tinh_tong_don_hang.__name__` sẽ trả về `"ham_wrapper"` thay vì tên thật, gây khó khăn khi debug.

#### 9. Decorator có tham số — kỹ thuật nâng cao thường gặp

python

```python
def gioi_han_so_lan(so_lan_toi_da):
    """Decorator FACTORY - hàm trả về decorator, cho phép truyền tham số tùy chỉnh"""
    def decorator(ham_goc):
        so_lan_da_goi = 0

        @wraps(ham_goc)
        def wrapper(*args, **kwargs):
            nonlocal so_lan_da_goi
            if so_lan_da_goi >= so_lan_toi_da:
                raise Exception(f"Đã vượt quá {so_lan_toi_da} lần gọi cho phép")
            so_lan_da_goi += 1
            return ham_goc(*args, **kwargs)
        return wrapper
    return decorator


@gioi_han_so_lan(3)
def goi_api_ben_thu_ba(endpoint):
    print(f"Đang gọi API: {endpoint}")
    return {"status": "ok"}

goi_api_ben_thu_ba("/don-hang")   # OK
goi_api_ben_thu_ba("/khach-hang") # OK
goi_api_ben_thu_ba("/thanh-toan") # OK
# goi_api_ben_thu_ba("/kho-hang")   # ❌ Exception: Đã vượt quá 3 lần gọi
```

Đây chính xác là mẫu decorator dùng để **giới hạn rate limit gọi API** trong thực tế — một kỹ thuật cực kỳ phổ biến khi xây dựng hệ thống backend cần kiểm soát tần suất truy cập tài nguyên.

`nonlocal` (mới gặp lần đầu) cho phép hàm lồng bên trong **sửa** biến ở hàm bao ngoài (khác với biến global ở Bài 9) — cần thiết vì `so_lan_da_goi` sống ở scope của `decorator`, không phải `wrapper`.

#### 10. Decorator có sẵn trong Python bạn cần biết

python

```python
class SanPham:
    def __init__(self, gia):
        self._gia = gia

    @property        # đã học ở Bài 13 - đây CŨNG là decorator!
    def gia(self):
        return self._gia

    @staticmethod     # method KHÔNG cần self, không phụ thuộc vào instance cụ thể
    def tinh_thue(gia, thue_suat=0.1):
        return gia * thue_suat

    @classmethod      # method nhận cls (class) thay vì self (instance) - dùng làm "constructor phụ"
    def tao_tu_chuoi(cls, chuoi_gia):
        return cls(float(chuoi_gia))


print(SanPham.tinh_thue(500000))            # gọi trực tiếp qua class, không cần tạo object
sp = SanPham.tao_tu_chuoi("150000.5")        # tạo object bằng cách khác với __init__ thông thường
print(sp.gia)
```

**Phân biệt `@staticmethod` và `@classmethod`:**

- `@staticmethod`: hàm "tiện ích" liên quan đến class về ngữ nghĩa, nhưng không cần truy cập `self` hay `cls`
- `@classmethod`: nhận `cls` (chính class đó), thường dùng làm **"constructor thay thế"** — ví dụ tạo object từ một định dạng dữ liệu khác (chuỗi, dict, JSON) mà không phù hợp với `__init__` gốc

---

#### 11. Ví dụ thực chiến tổng hợp — Hệ thống ghi log + retry cho API

python

```python
import time
import random
from functools import wraps

def ghi_log_va_retry(so_lan_thu_lai=3):
    def decorator(ham_goc):
        @wraps(ham_goc)
        def wrapper(*args, **kwargs):
            for lan_thu in range(1, so_lan_thu_lai + 1):
                try:
                    print(f"[Lần {lan_thu}] Đang gọi {ham_goc.__name__}...")
                    return ham_goc(*args, **kwargs)
                except ConnectionError as e:
                    print(f"  Lỗi kết nối: {e}. Thử lại...")
                    time.sleep(0.5)
            raise ConnectionError(f"Thất bại sau {so_lan_thu_lai} lần thử")
        return wrapper
    return decorator


@ghi_log_va_retry(so_lan_thu_lai=3)
def goi_api_thanh_toan(ma_don):
    if random.random() < 0.7:   # giả lập 70% khả năng lỗi mạng
        raise ConnectionError("Timeout kết nối server thanh toán")
    return {"ma_don": ma_don, "trang_thai": "thành công"}


ket_qua = goi_api_thanh_toan("DH2026-891")
print(ket_qua)
```

Đây chính là mẫu **"retry pattern"** — cực kỳ phổ biến trong hệ thống thực tế khi gọi API bên ngoài (mạng luôn có khả năng chập chờn), giúp tăng độ tin cậy hệ thống mà không cần lặp code retry ở mọi nơi gọi API.

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_15.py`:

**Phần 1 — Generator:**

1. Viết generator `phan_trang(danh_sach, kich_thuoc_trang)`: `yield` từng "trang" (là một list con) có kích thước `kich_thuoc_trang` từ `danh_sach` gốc (ví dụ 10 phần tử, trang size 3 → yield 4 trang: 3,3,3,1 phần tử)
2. Viết generator `so_nguyen_to(gioi_han)`: `yield` từng số nguyên tố nhỏ hơn `gioi_han` (gợi ý: dùng hàm phụ kiểm tra số nguyên tố)
3. Dùng `sys.getsizeof()` so sánh kích thước bộ nhớ giữa list comprehension và generator expression cho `range(1_000_000)`

**Phần 2 — Decorator:**  
4. Viết decorator `@dang_nhap_bat_buoc` — nhận thêm tham số `da_dang_nhap: bool` khi gọi hàm được bọc, nếu `False` thì raise `PermissionError`, nếu `True` thì cho hàm gốc chạy bình thường (gợi ý: dùng `kwargs.get("da_dang_nhap")`)  
5. Viết decorator factory `@cache_ket_qua(thoi_gian_song_giay)` — lưu cache kết quả hàm theo tham số đầu vào, nếu gọi lại với **cùng tham số** trong khoảng `thoi_gian_song_giay`, trả về kết quả cache thay vì chạy lại hàm (gợi ý: dùng `dict` lưu `{tham_so: (ket_qua, thoi_gian_luu)}`)  
6. Áp dụng decorator ở bài 5 cho một hàm giả lập gọi API tốn thời gian (`time.sleep(1)`), chứng minh lần gọi thứ 2 với cùng tham số trả về **ngay lập tức** (không sleep lại)

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 16: Comprehension nâng cao & Lập trình hàm (Functional Programming)** — nơi ta đào sâu `lambda`, `map()`, `filter()`, `reduce()`, và tư duy functional giúp code Python của bạn ngắn gọn, mạnh mẽ và "chuẩn chuyên gia" hơn nữa.
