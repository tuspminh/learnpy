### Bài 3: Chuỗi (String) và Xử lý Văn bản

Đã ghi nhận phong cách giảng dạy bạn muốn — tôi sẽ duy trì xuyên suốt hành trình này. String là kiểu dữ liệu bạn sẽ chạm vào **nhiều nhất** trong công việc thực tế: xử lý input người dùng, làm sạch dữ liệu (data cleaning), parse file log, xây dựng API response... Ta đi sâu vào bài này.

---

#### 1. String là gì về bản chất?

Trong Python, `str` là một **chuỗi bất biến (immutable sequence)** các ký tự Unicode. Hai từ khóa quan trọng ở đây:

- **Sequence (dãy có thứ tự)**: mỗi ký tự có một vị trí (index) cố định, truy cập được như list.
- **Immutable (bất biến)**: một khi chuỗi đã tạo ra, bạn **không thể sửa trực tiếp** từng ký tự bên trong nó. Mọi "thay đổi" thực chất tạo ra chuỗi mới.

python

```python
ten = "Python"
# ten[0] = "J"   # ❌ Lỗi: TypeError: 'str' object does not support item assignment

ten_moi = "J" + ten[1:]   # ✅ Tạo chuỗi mới: "Jython"
print(ten_moi)
```

**Tại sao Python thiết kế string bất biến?** Vì tính an toàn và hiệu năng — chuỗi được dùng làm khóa (key) trong dictionary rất nhiều (Bài 8), mà key phải là dữ liệu không đổi để đảm bảo tính toàn vẹn của cấu trúc dữ liệu. Đây là kiến thức nền quan trọng, bạn sẽ thấy áp dụng lại khi học về `dict` và `set`.

---

#### 2. Indexing — Truy cập từng ký tự

Mỗi ký tự trong chuỗi có chỉ số (index), **bắt đầu từ 0**:

python

```python
ten_cty = "Anthropic"
#          A  n  t  h  r  o  p  i  c
#          0  1  2  3  4  5  6  7  8
#         -9 -8 -7 -6 -5 -4 -3 -2 -1   (index âm - đếm từ cuối)

print(ten_cty[0])    # 'A'
print(ten_cty[4])    # 'r'
print(ten_cty[-1])   # 'c'  - ký tự cuối cùng
print(ten_cty[-2])   # 'i'  - ký tự áp chót
```

**Index âm** cực kỳ hữu dụng thực tế — ví dụ lấy đuôi file mà không cần biết độ dài chuỗi:

python

```python
ten_file = "bao_cao_thang_6.pdf"
print(ten_file[-3:])   # 'pdf' - 3 ký tự cuối
```

---

#### 3. Slicing — Cắt chuỗi con

Cú pháp: `chuoi[bat_dau:ket_thuc:buoc_nhay]`. Đây là công cụ bạn dùng **hàng ngày** khi xử lý dữ liệu thực tế.

python

```python
email = "nguyen.van.a@company.com"

print(email[0:12])      # 'nguyen.van.a'  - từ index 0 đến 11 (không lấy 12)
print(email[13:])       # 'company.com'   - từ index 13 đến hết
print(email[:12])       # 'nguyen.van.a'  - từ đầu đến trước index 12
print(email[::-1])      # đảo ngược toàn bộ chuỗi
print(email[::2])       # lấy mỗi 2 ký tự một lần (bước nhảy = 2)
```

**Lưu ý quan trọng**: `ket_thuc` là **chỉ số KHÔNG được bao gồm** (exclusive) — đây là quy tắc thống nhất trong toàn bộ Python (list, range... đều theo quy tắc này), nên nhớ kỹ ngay từ đầu.

**Ví dụ thực tế** — tách domain từ email trong hệ thống xác thực người dùng:

python

```python
email = "user@gmail.com"
vi_tri_at = email.index("@")
domain = email[vi_tri_at + 1:]
print(domain)   # 'gmail.com'
```

---

#### 4. Các phương thức (methods) xử lý chuỗi thiết yếu

String trong Python có hàng chục method sẵn có. Dưới đây là nhóm bạn sẽ dùng thường xuyên nhất trong công việc thực tế, chia theo mục đích.

##### a) Chuẩn hóa & làm sạch dữ liệu (data cleaning)

Đây là nhóm quan trọng nhất khi xử lý dữ liệu đầu vào từ người dùng hoặc file:

python

```python
raw_input = "   Nguyễn Văn A   "

print(raw_input.strip())        # 'Nguyễn Văn A' - xóa khoảng trắng đầu/cuối
print(raw_input.lstrip())       # xóa khoảng trắng bên trái
print(raw_input.rstrip())       # xóa khoảng trắng bên phải

email = "USER@GMAIL.COM"
print(email.lower())            # 'user@gmail.com' - chuyển chữ thường
print(email.upper())            # in hoa toàn bộ
print("python".capitalize())    # 'Python' - viết hoa chữ đầu
print("hello world".title())    # 'Hello World' - viết hoa đầu mỗi từ
```

**Ứng dụng thực tế cực kỳ phổ biến**: khi xây dựng hệ thống đăng ký tài khoản, bạn luôn phải chuẩn hóa email trước khi so sánh/lưu database, để tránh trường hợp `User@Gmail.com` và `user@gmail.com` bị coi là 2 tài khoản khác nhau:

python

```python
def chuan_hoa_email(email_input):
    return email_input.strip().lower()

email1 = chuan_hoa_email("  User@Gmail.com  ")
email2 = chuan_hoa_email("user@gmail.com")
print(email1 == email2)   # True - giờ so sánh chính xác
```

##### b) Tìm kiếm & kiểm tra nội dung

python

```python
cau = "Python là ngôn ngữ lập trình phổ biến nhất năm 2026"

print("Python" in cau)              # True - kiểm tra có chứa không
print(cau.startswith("Python"))     # True - kiểm tra bắt đầu bằng
print(cau.endswith("2026"))         # True - kiểm tra kết thúc bằng
print(cau.find("ngôn ngữ"))         # 10 - trả về vị trí, -1 nếu không tìm thấy
print(cau.count("n"))               # đếm số lần xuất hiện ký tự/chuỗi con
```

**Ứng dụng thực tế** — validate định dạng file upload, một tình huống rất phổ biến trong xây dựng web app:

python

```python
ten_file = "bao_cao_quy2.pdf"
dinh_dang_cho_phep = (".pdf", ".docx", ".xlsx")

if ten_file.lower().endswith(dinh_dang_cho_phep):
    print("File hợp lệ")
else:
    print("Chỉ chấp nhận PDF, Word, Excel")
```

##### c) Thay thế & tách/ghép chuỗi

python

```python
thong_bao = "Đơn hàng #12345 đang được xử lý"
thong_bao_moi = thong_bao.replace("đang được xử lý", "đã giao thành công")
print(thong_bao_moi)

# split() - tách chuỗi thành list, cực kỳ hay dùng khi xử lý dữ liệu CSV/log
du_lieu = "Lan,25,Hà Nội,Nhân viên"
thong_tin = du_lieu.split(",")
print(thong_tin)   # ['Lan', '25', 'Hà Nội', 'Nhân viên']

# join() - ngược lại với split(), ghép list thành chuỗi
danh_sach_tu = ["Python", "rất", "thú", "vị"]
cau_hoan_chinh = " ".join(danh_sach_tu)
print(cau_hoan_chinh)   # 'Python rất thú vị'
```

**Ứng dụng thực tế** — đây chính là kỹ thuật nền tảng để **parse file CSV/log** trước khi bạn học thư viện `csv` chuyên dụng sau này:

python

```python
dong_log = "2026-07-03 14:32:01 | ERROR | Kết nối database thất bại"
cac_phan = dong_log.split(" | ")
thoi_gian, muc_do, noi_dung = cac_phan   # unpacking - sẽ học kỹ ở Bài 6
print(f"[{muc_do}] {noi_dung} vào lúc {thoi_gian}")
```

##### d) Kiểm tra kiểu nội dung

python

```python
print("12345".isdigit())      # True - toàn số
print("Python3".isalpha())    # False - có chứa số nên không phải toàn chữ
print("Python".isalpha())     # True
print("password123".isalnum())# True - chỉ chữ và số, không ký tự đặc biệt
```

**Ứng dụng thực tế** — validate input trước khi ép kiểu, tránh crash chương trình:

python

```python
tuoi_input = input("Nhập tuổi của bạn: ")

if tuoi_input.isdigit():
    tuoi = int(tuoi_input)
    print(f"Bạn {tuoi} tuổi")
else:
    print("Vui lòng chỉ nhập số")
```

---

#### 5. f-string nâng cao — định dạng chuyên nghiệp

Ở Bài 2 bạn đã biết f-string cơ bản. Giờ ta khai thác sâu hơn — kỹ năng này giúp output của bạn trông "chuyên nghiệp" như báo cáo thật:

python

```python
ten_sp = "Bàn phím cơ"
gia = 1250000
so_luong = 3

# Căn chỉnh và định dạng số
print(f"{ten_sp:<20} | {gia:>10,.0f} VNĐ")
# 'Bàn phím cơ          |  1,250,000 VNĐ'
# <20 = căn trái, độ rộng 20 ký tự
# >10 = căn phải, độ rộng 10 ký tự
# ,.0f = thêm dấu phẩy ngăn cách hàng nghìn, không lấy số thập phân

ty_le_hoan_thanh = 0.874
print(f"Tiến độ: {ty_le_hoan_thanh:.1%}")   # 'Tiến độ: 87.4%'

# Debug nhanh - Python 3.8+ hỗ trợ "=" để in cả tên biến lẫn giá trị
print(f"{gia=}")   # 'gia=1250000' - cực tiện khi debug thay vì print("gia:", gia)
```

Tính năng `{gia=}` là một "mẹo nhà nghề" ít tài liệu cơ bản nhắc đến nhưng dev chuyên nghiệp dùng liên tục để debug nhanh mà không cần gõ tên biến hai lần.

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_3.py` mô phỏng **hệ thống kiểm tra thông tin đăng ký tài khoản**:

1. Cho một chuỗi thô mô phỏng input người dùng:

python

```python
   raw_data = "  NGUYEN.VAN.A@GMAIL.COM , MatKhau123  "
```

2. Tách chuỗi này thành `email` và `mat_khau` (dùng `split(",")`), sau đó `strip()` từng phần
3. Chuẩn hóa `email` về chữ thường
4. Kiểm tra:
  - Email có chứa ký tự `@` không (dùng `in`)
  - Mật khẩu có `isalnum()` không (chỉ chữ và số) — nếu không, in cảnh báo
  - Độ dài mật khẩu có `>= 8` không (dùng `len()`)
5. In kết quả bằng f-string dạng báo cáo, ví dụ:

```
   Email: nguyen.van.a@gmail.com   -> Hợp lệ
   Mật khẩu: ***********           -> Đạt yêu cầu độ dài, Đạt yêu cầu định dạng
```

Làm xong gửi cho tôi xem nhé. Sau đó ta sang **Bài 4: Cấu trúc rẽ nhánh (if/elif/else)** — nền tảng để chương trình bạn viết có thể "ra quyết định" thay vì chỉ chạy tuần tự từ trên xuống dưới.
