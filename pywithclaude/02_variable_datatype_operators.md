[01_hello_py](01_hello_py.md)    [03_string](03_string.md)

---

### Bài 2: Biến, Kiểu dữ liệu và Toán tử


#### 1. Biến (Variable) — bản chất thực sự

Nhiều tài liệu dạy "biến là cái hộp chứa giá trị" — cách hiểu này **sai với Python** và sẽ gây khó hiểu về sau. Trong Python, biến là một **cái tên (label/tag)** được gắn vào một đối tượng nằm trong bộ nhớ.

python

```python
tuoi = 25
```

Điều xảy ra thực sự: Python tạo ra một object số nguyên `25` trong bộ nhớ, rồi gắn nhãn `tuoi` trỏ đến object đó. Bạn có thể kiểm chứng bằng hàm `id()` (trả về địa chỉ bộ nhớ):

python

```python
a = 25
b = 25
print(id(a) == id(b))   # True - cả hai cùng trỏ đến 1 object số 25 trong bộ nhớ

a = 25
b = [25]                # list chứa 25
print(id(a) == id(b[0])) # thường vẫn True với số nhỏ do Python tối ưu (integer caching)
```

**Tại sao điều này quan trọng?** Vì nó giải thích được hành vi "kỳ lạ" sau này khi bạn làm việc với list, dict — khi hai biến "cùng trỏ một object" thì sửa qua biến này sẽ ảnh hưởng biến kia. Đây gọi là khái niệm **mutable/immutable** mà ta sẽ đào sâu ở Bài 6 (List).

**Quy tắc đặt tên biến:**

- Bắt đầu bằng chữ cái hoặc `_`, không được bắt đầu bằng số
- Chỉ chứa chữ, số, `_` — không dấu cách, không ký tự đặc biệt
- Phân biệt hoa/thường: `tuoi` ≠ `Tuoi`
- Không trùng từ khóa dành riêng (`if`, `for`, `class`, `return`...)
- **Quy ước chuẩn ngành (PEP 8)**: dùng `snake_case` cho biến/hàm (`gia_san_pham`), `PascalCase` cho class (`SanPham`), `UPPER_CASE` cho hằng số (`MAX_SO_LUONG`)

python

```python
# Tốt - theo chuẩn PEP 8, dễ đọc
so_luong_don_hang = 15
gia_tri_don = 250000.0

# Tránh - không rõ nghĩa
x = 15
y = 250000.0
```

Trong công việc thực tế (kể cả khi review code cho AI viết ra), đặt tên biến rõ nghĩa quan trọng ngang với logic đúng — vì code được đọc nhiều hơn được viết.

---

#### 2. Các kiểu dữ liệu cơ bản (Data Types)

Python có kiểu **động (dynamically typed)** — bạn không cần khai báo kiểu, Python tự suy luận dựa trên giá trị gán. Nhưng bên trong, mỗi giá trị vẫn có kiểu rõ ràng, kiểm tra bằng hàm `type()`.

##### a) `int` — Số nguyên

python

```python
so_don_hang = 128
nam_sinh = 2001
nhiet_do_am = -15

print(type(so_don_hang))   # <class 'int'>
```

Python `int` không giới hạn độ lớn theo phần cứng như C (không bị tràn số ở 2^31 hay 2^63) — bạn có thể tính giai thừa của 100 mà không lo lỗi overflow.

##### b) `float` — Số thực (dấu phẩy động)

python

```python
gia_ca_phe = 45000.5
ty_gia_usd = 26150.75

print(type(gia_ca_phe))    # <class 'float'>
```

⚠️ **Cạm bẫy kinh điển mà cả dev có kinh nghiệm vẫn dính:**

python

```python
print(0.1 + 0.2)    # 0.30000000000000004  (!!)
```

Đây **không phải lỗi của Python** mà là bản chất của số dấu phẩy động (IEEE 754) — máy tính lưu số thực dưới dạng nhị phân nên một số số thập phân không biểu diễn chính xác tuyệt đối được. Trong ứng dụng tài chính, ngân hàng thực tế, người ta dùng module `decimal` để tránh sai số này:

python

```python
from decimal import Decimal
gia = Decimal("0.1") + Decimal("0.2")
print(gia)   # 0.3 - chính xác
```

Đây chính là lý do các hệ thống thanh toán thực tế (ví dụ ví điện tử, sàn giao dịch) không bao giờ dùng `float` để tính tiền.

##### c) `str` — Chuỗi văn bản

python

```python
ten = "Nguyễn Văn A"
email = 'a.nguyen@example.com'
mo_ta = """Đây là chuỗi 
nhiều dòng"""
```

Dùng nháy đơn `'` hay kép `"` đều được — quy ước phổ biến là dùng nháy kép cho nội dung có thể chứa nháy đơn (như `"it's ok"`). Chuỗi 3 dấu nháy `"""..."""` dùng cho văn bản nhiều dòng hoặc docstring (sẽ học ở Bài 9).

##### d) `bool` — Kiểu luận lý

python

```python
da_thanh_toan = True
la_khach_vip = False
print(type(da_thanh_toan))   # <class 'bool'>
```

Lưu ý thú vị: `bool` thực chất là **con của `int`** trong Python — `True == 1` và `False == 0` cho kết quả `True`. Điều này cho phép những đoạn code "ảo diệu" như:

python

```python
gio_hang = [1, 2, 3]
so_san_pham_loi = 2
print(so_san_pham_loi + True)   # 3 - True được tính như số 1
```

##### e) `None` — Giá trị "rỗng có chủ đích"

python

```python
ket_qua_tim_kiem = None
```

`None` không giống `0`, `""`, hay `False`. Nó biểu thị **"không có giá trị nào cả"** — dùng khi bạn muốn khởi tạo một biến mà chưa có dữ liệu, hoặc một hàm không trả về gì cụ thể. Ví dụ thực tế: hàm tìm sản phẩm trong database, nếu không tìm thấy sẽ trả về `None` chứ không phải chuỗi rỗng.

---

#### 3. Ép kiểu (Type Casting)

Vì Python suy luận kiểu tự động, đôi khi bạn cần **chủ động chuyển đổi kiểu**:

python

```python
tuoi_str = "25"          # đây là chuỗi, không phải số!
tuoi_int = int(tuoi_str)  # ép thành int -> 25
print(tuoi_int + 5)       # 30 - giờ mới cộng được

gia = 45000
gia_str = str(gia)        # ép thành chuỗi -> "45000"
print("Giá: " + gia_str + " VNĐ")

diem = "8.5"
diem_float = float(diem)  # 8.5
```

**Ứng dụng thực tế cực kỳ phổ biến**: khi bạn nhận input từ người dùng (form web, API request, file CSV), dữ liệu luôn ở dạng chuỗi ban đầu, dù người dùng gõ số. Ví dụ khi xây dựng một API nhận đơn hàng:

python

```python
so_luong_input = "5"        # dữ liệu thô từ request JSON
so_luong = int(so_luong_input)
if so_luong > 0:
    print(f"Đặt {so_luong} sản phẩm")
```

Nếu quên ép kiểu, bạn sẽ gặp lỗi `TypeError` khi cố cộng string với int — một trong những lỗi phổ biến nhất của người mới học.

---

#### 4. Toán tử (Operators)

##### a) Toán tử số học

python

```python
a, b = 17, 5

print(a + b)    # 22   - cộng
print(a - b)    # 12   - trừ
print(a * b)    # 85   - nhân
print(a / b)    # 3.4  - chia (LUÔN trả về float)
print(a // b)   # 3    - chia lấy phần nguyên (floor division)
print(a % b)    # 2    - chia lấy dư (modulo)
print(a ** b)   # 1419857 - lũy thừa (a mũ b)
```

**Ứng dụng thực tế của `%` (modulo)** — cực kỳ hay dùng, không chỉ để "lấy dư" đơn thuần:

python

```python
# Kiểm tra số chẵn/lẻ
so = 24
if so % 2 == 0:
    print("Số chẵn")

# Phân trang dữ liệu (pagination) - hiển thị 10 sản phẩm/trang
tong_san_pham = 47
so_san_pham_moi_trang = 10
so_trang = tong_san_pham // so_san_pham_moi_trang + (1 if tong_san_pham % so_san_pham_moi_trang else 0)
print(so_trang)   # 5 trang
```

##### b) Toán tử so sánh

python

```python
print(10 > 5)     # True
print(10 == 10)   # True (so sánh bằng - lưu ý dùng ==, không phải =)
print(10 != 5)    # True (khác nhau)
print(10 <= 9)    # False
```

⚠️ Lỗi cực kỳ phổ biến của người mới: nhầm `=` (gán giá trị) với `==` (so sánh bằng). `x = 5` gán số 5 cho x; `x == 5` kiểm tra x có bằng 5 không.

##### c) Toán tử logic

python

```python
tuoi = 20
co_bang_lai = True

print(tuoi >= 18 and co_bang_lai)   # True - cả hai điều kiện đều đúng
print(tuoi < 18 or co_bang_lai)     # True - ít nhất một điều kiện đúng
print(not co_bang_lai)              # False - phủ định
```

**Ví dụ thực tế** — logic kiểm tra điều kiện đăng nhập hệ thống:

python

```python
mat_khau_dung = True
tai_khoan_bi_khoa = False

if mat_khau_dung and not tai_khoan_bi_khoa:
    print("Đăng nhập thành công")
else:
    print("Đăng nhập thất bại")
```

##### d) Toán tử gán rút gọn (Compound assignment)

python

```python
diem_thuong = 100
diem_thuong += 50    # tương đương diem_thuong = diem_thuong + 50 -> 150
diem_thuong -= 20     # -> 130
diem_thuong *= 2      # -> 260
```

Cực kỳ phổ biến trong vòng lặp tính tổng, đếm số lượng — bạn sẽ dùng liên tục ở Bài 5.

---

#### 5. f-string — cách "chuẩn 2026" để ghép chuỗi

Cách cũ (nối chuỗi bằng `+`) vừa dài dòng vừa dễ lỗi kiểu dữ liệu. Cách hiện đại và được khuyến nghị dùng trong mọi codebase chuyên nghiệp là **f-string**:

python

```python
ten_khach = "Lan"
tong_tien = 350000

# Cách cũ - phải ép kiểu thủ công, dễ lỗi
print("Khách hàng " + ten_khach + " thanh toán " + str(tong_tien) + " VNĐ")

# Cách hiện đại - f-string (thêm f trước dấu nháy)
print(f"Khách hàng {ten_khach} thanh toán {tong_tien} VNĐ")

# f-string còn tính toán được trực tiếp bên trong {}
print(f"Sau khi giảm 10%: {tong_tien * 0.9} VNĐ")

# Định dạng số - ví dụ làm tròn 2 chữ số thập phân
gia = 1234.5678
print(f"Giá: {gia:.2f} VNĐ")   # Giá: 1234.57 VNĐ
```

f-string là cách viết bắt buộc-nên-biết vì gần như mọi codebase Python hiện đại (kể cả code sinh ra bởi AI) đều dùng nó thay vì `.format()` hay `%` cũ.

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_2.py` mô phỏng **hóa đơn mua hàng đơn giản**:

1. Khai báo các biến: `ten_san_pham` (str), `don_gia` (float), `so_luong` (int), `ma_giam_gia` (bool - có áp dụng giảm giá hay không)
2. Tính `thanh_tien = don_gia * so_luong`
3. Nếu `ma_giam_gia = True`, giảm 15% trên `thanh_tien`
4. In hóa đơn bằng f-string, làm tròn 2 chữ số thập phân, theo dạng:

```
   Sản phẩm: Tai nghe Bluetooth
   Số lượng: 3
   Thành tiền: 450000.00 VNĐ
```

Gợi ý nâng độ khó: thử dùng toán tử `%` để kiểm tra nếu `so_luong` là số chẵn thì tặng thêm 1 sản phẩm miễn phí.

Làm xong gửi code cho tôi xem, tôi sẽ review và mình chuyển sang **Bài 3: Chuỗi (String) và xử lý văn bản** — nơi bạn sẽ học cách cắt chuỗi, tìm kiếm, thay thế, và các kỹ thuật xử lý text dùng nhiều trong xử lý dữ liệu thực tế (làm sạch dữ liệu, xử lý input người dùng...).

---
[01_hello_py](01_hello_py.md)    [03_string](03_string.md)
