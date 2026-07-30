Vai trò này tôi đã lưu vào bộ nhớ từ bài 3 và đang áp dụng xuyên suốt — sẽ tiếp tục duy trì đến hết hành trình. Giờ vào bài học cuối cùng của giai đoạn nền tảng.

### 📘 Bài 10: Xử lý lỗi (Exception Handling)

Đây là bài học đánh dấu sự khác biệt rõ ràng nhất giữa "code chạy được trên máy mình" và "code sẵn sàng chạy trong môi trường thực tế (production)" — nơi dữ liệu luôn có khả năng sai lệch, mạng luôn có thể mất kết nối, file luôn có thể không tồn tại.

---

#### 1. Exception là gì — và tại sao chương trình "crash"?

python

```python
tuoi = int("hai mươi lăm")   # ❌ Chương trình dừng đột ngột
print("Dòng này không bao giờ được chạy")
```

**Kết quả:**

```
Traceback (most recent call last):
  File "bai10.py", line 1, in <module>
    tuoi = int("hai mươi lăm")
ValueError: invalid literal for int() with base 10: 'hai mươi lăm'
```

Khi Python gặp một lỗi **tại runtime** (lúc chương trình đang chạy, không phải lỗi cú pháp), nó tạo ra một **Exception object**, rồi "ném" (raise) nó lên. Nếu không ai "bắt" (catch) exception đó, chương trình **dừng hoàn toàn** — mọi dòng code sau đó không chạy nữa.

Trong một hệ thống thực tế phục vụ hàng nghìn người dùng, một lỗi như vậy có thể làm **crash toàn bộ server**, ảnh hưởng tất cả người dùng khác — đây là lý do exception handling là kỹ năng bắt buộc, không phải "nice to have".

---

#### 2. Cấu trúc `try / except` cơ bản

python

```python
try:
    tuoi = int(input("Nhập tuổi của bạn: "))
    print(f"Bạn {tuoi} tuổi")
except ValueError:
    print("Lỗi: vui lòng nhập một số hợp lệ")
```

**Luồng hoạt động**: Python chạy khối `try`. Nếu có lỗi xảy ra, nó **ngay lập tức nhảy vào khối `except`** tương ứng (bỏ qua phần code còn lại trong `try`), thay vì crash toàn bộ chương trình.

#### 3. Các loại Exception phổ biến cần nắm chắc

python

```python
# ValueError - dữ liệu đúng kiểu nhưng giá trị không hợp lệ
int("abc")              # ValueError

# TypeError - thao tác không hợp lệ giữa các kiểu dữ liệu
"5" + 5                  # TypeError: can only concatenate str (not "int") to str

# ZeroDivisionError - chia cho 0
10 / 0                    # ZeroDivisionError

# KeyError - truy cập key không tồn tại trong dict (nhớ lại Bài 8)
d = {"a": 1}
d["b"]                    # KeyError: 'b'

# IndexError - truy cập index ngoài phạm vi list
lst = [1, 2, 3]
lst[10]                   # IndexError: list index out of range

# FileNotFoundError - mở file không tồn tại
open("khong_ton_tai.txt")  # FileNotFoundError

# AttributeError - gọi phương thức/thuộc tính không tồn tại
"hello".khong_ton_tai()    # AttributeError
```

**Ứng dụng thực tế** — xử lý nhiều loại lỗi khác nhau cho một hàm xử lý đơn hàng:

python

```python
def lay_gia_san_pham(kho_hang: dict, ma_sp: str, so_luong: str):
    try:
        gia = kho_hang[ma_sp]              # có thể KeyError
        so_luong_int = int(so_luong)        # có thể ValueError
        return gia * so_luong_int / 0        # cố ý lỗi ZeroDivisionError để minh họa
    except KeyError:
        print(f"Không tìm thấy sản phẩm mã {ma_sp}")
    except ValueError:
        print(f"Số lượng '{so_luong}' không hợp lệ")
    except ZeroDivisionError:
        print("Lỗi chia cho 0 trong tính toán")

kho = {"SP001": 150000}
lay_gia_san_pham(kho, "SP002", "5")     # Không tìm thấy sản phẩm mã SP002
lay_gia_san_pham(kho, "SP001", "abc")   # Số lượng 'abc' không hợp lệ
```

**Nguyên tắc quan trọng**: luôn bắt exception **cụ thể nhất có thể** (`ValueError`, `KeyError`...), tránh dùng `except:` trống hoặc `except Exception:` một cách bừa bãi — vì nó sẽ "nuốt" luôn cả những lỗi nghiêm trọng bạn không ngờ tới, khiến việc debug về sau cực kỳ khó khăn:

python

```python
# ❌ RẤT KHÔNG NÊN - bắt MỌI loại lỗi mà không phân biệt, ẩn đi cả lỗi logic nghiêm trọng
try:
    xu_ly_thanh_toan(don_hang)
except:
    print("Có lỗi xảy ra")   # Không biết lỗi gì, khó debug, có thể ẩn cả bug nguy hiểm
```

---

#### 4. `else` và `finally` — hoàn thiện cấu trúc try

python

```python
def chia(a, b):
    try:
        ket_qua = a / b
    except ZeroDivisionError:
        print("Không thể chia cho 0")
    else:
        # chỉ chạy khi try KHÔNG có lỗi
        print(f"Kết quả: {ket_qua}")
    finally:
        # LUÔN LUÔN chạy, có lỗi hay không cũng chạy
        print("Đã hoàn thành phép tính")

chia(10, 2)
# Kết quả: 5.0
# Đã hoàn thành phép tính

chia(10, 0)
# Không thể chia cho 0
# Đã hoàn thành phép tính
```

**Ứng dụng thực tế cực kỳ quan trọng của `finally`** — đảm bảo tài nguyên luôn được giải phóng (đóng file, đóng kết nối database, đóng kết nối mạng) **dù có lỗi xảy ra hay không**:

python

```python
def ghi_log_giao_dich(ma_gd, so_tien):
    file = open("log_giao_dich.txt", "a")
    try:
        if so_tien <= 0:
            raise ValueError("Số tiền phải lớn hơn 0")
        file.write(f"{ma_gd}: {so_tien}\n")
        print("Ghi log thành công")
    except ValueError as e:
        print(f"Lỗi dữ liệu: {e}")
    finally:
        file.close()   # LUÔN đóng file, tránh rò rỉ tài nguyên (resource leak)
        print("Đã đóng file log")
```

(Ta sẽ học cách làm việc này gọn gàng hơn bằng `with` ở Bài 11 — Xử lý File.)

---

#### 5. Bắt nhiều loại lỗi cùng lúc

python

```python
try:
    du_lieu = kho_hang[ma_sp] / int(so_luong)
except (KeyError, ValueError, ZeroDivisionError) as loi:
    print(f"Đã xảy ra lỗi: {loi}")
    print(f"Loại lỗi: {type(loi).__name__}")
```

Dùng `as loi` để lấy **object exception**, cho phép truy cập thông báo lỗi chi tiết — rất hữu ích khi cần ghi log lỗi để phân tích sau này (một tác vụ dev chuyên nghiệp làm hàng ngày).

---

#### 6. `raise` — Tự tạo và ném lỗi có chủ đích

Đôi khi *bạn* là người muốn báo lỗi, không phải Python tự phát sinh — đây là kỹ thuật quan trọng để bảo vệ tính đúng đắn dữ liệu (data validation) trong hàm của chính bạn:

python

```python
def rut_tien(so_du: float, so_tien_rut: float) -> float:
    if so_tien_rut <= 0:
        raise ValueError("Số tiền rút phải lớn hơn 0")
    if so_tien_rut > so_du:
        raise ValueError(f"Số dư không đủ. Số dư hiện tại: {so_du:,} VNĐ")
    return so_du - so_tien_rut

try:
    so_du_moi = rut_tien(500000, 800000)
except ValueError as e:
    print(f"Giao dịch bị từ chối: {e}")
```

**Đây chính là cách các hệ thống ngân hàng, ví điện tử thực tế bảo vệ tính đúng đắn dữ liệu** — hàm chủ động "từ chối" thực hiện logic sai thay vì để dữ liệu bị sai lệch âm thầm (ví dụ số dư âm mà không ai biết).

---

#### 7. Custom Exception — tạo loại lỗi riêng cho nghiệp vụ

Trong các hệ thống thực tế lớn, dev thường tạo class Exception riêng để phân biệt rõ loại lỗi thuộc về nghiệp vụ nào (ta sẽ hiểu sâu về `class` ở Bài 13, nhưng giới thiệu sớm vì liên quan trực tiếp):

python

```python
class SoDuKhongDuException(Exception):
    """Exception riêng cho lỗi số dư không đủ"""
    pass

class TaiKhoanBiKhoaException(Exception):
    """Exception riêng cho lỗi tài khoản bị khóa"""
    pass


def rut_tien_ngan_hang(so_du, so_tien_rut, bi_khoa=False):
    if bi_khoa:
        raise TaiKhoanBiKhoaException("Tài khoản đang bị tạm khóa")
    if so_tien_rut > so_du:
        raise SoDuKhongDuException(f"Cần {so_tien_rut:,} nhưng chỉ có {so_du:,}")
    return so_du - so_tien_rut


try:
    rut_tien_ngan_hang(500000, 800000)
except SoDuKhongDuException as e:
    print(f"[LỖI SỐ DƯ] {e}")
except TaiKhoanBiKhoaException as e:
    print(f"[TÀI KHOẢN BỊ KHÓA] {e}")
```

**Lợi ích thực tế**: khi hệ thống lớn (ví dụ ứng dụng ngân hàng có hàng trăm loại lỗi nghiệp vụ khác nhau), custom exception giúp code xử lý lỗi **rõ ràng, có tổ chức**, và cho phép các phần khác của hệ thống (ví dụ lớp giao diện người dùng) phản hồi khác nhau tùy loại lỗi cụ thể — thay vì phải đoán ý nghĩa qua nội dung chuỗi thông báo lỗi.

---

#### 8. Exception chaining — giữ nguyên "chuỗi nhân quả" của lỗi

python

```python
def doc_cau_hinh(ten_file):
    try:
        with open(ten_file) as f:
            return f.read()
    except FileNotFoundError as e:
        raise RuntimeError("Không thể khởi động hệ thống do thiếu file cấu hình") from e
```

Cú pháp `raise ... from e` giữ lại **thông tin lỗi gốc** trong traceback, giúp việc debug sau này biết chính xác nguyên nhân gốc rễ (root cause) chứ không chỉ thấy lỗi bề mặt — kỹ thuật hay dùng trong hệ thống lớn nhiều tầng xử lý.

---

#### 9. Nguyên tắc thực chiến: Khi nào dùng exception, khi nào dùng `if`?

Đây là câu hỏi thiết kế quan trọng dev chuyên nghiệp luôn cân nhắc:

python

```python
# Nếu tình huống là BÌNH THƯỜNG, dễ đoán trước -> dùng if
def lay_gia(kho_hang, ma_sp):
    if ma_sp not in kho_hang:
        return None   # sản phẩm không tồn tại là tình huống hoàn toàn bình thường
    return kho_hang[ma_sp]

# Nếu tình huống là BẤT THƯỜNG, khó đoán, hoặc lỗi hệ thống -> dùng try/except
def doc_file_cau_hinh(duong_dan):
    try:
        with open(duong_dan) as f:
            return f.read()
    except FileNotFoundError:
        # File bị thiếu là tình huống bất thường, ngoài tầm kiểm soát trực tiếp của code
        return None
```

Nguyên tắc chung: **`if` cho logic nghiệp vụ có thể đoán trước, `try/except` cho lỗi từ môi trường ngoài** (file, mạng, input người dùng, API bên thứ ba) — những thứ code của bạn không kiểm soát trực tiếp được.

---

#### 10. Ví dụ thực chiến tổng hợp — Hệ thống xử lý đơn hàng chống lỗi toàn diện

python

```python
class SanPhamKhongTonException(Exception):
    pass

class SoLuongKhongHopLeException(Exception):
    pass


def xu_ly_don_hang(kho_hang: dict, ma_sp: str, so_luong_input: str) -> dict:
    """
    Xử lý một đơn hàng, trả về dict kết quả.
    Luôn trả về dict có key 'thanh_cong' để nơi gọi biết kết quả xử lý.
    """
    try:
        if ma_sp not in kho_hang:
            raise SanPhamKhongTonException(f"Sản phẩm {ma_sp} không tồn tại")

        so_luong = int(so_luong_input)

        if so_luong <= 0:
            raise SoLuongKhongHopLeException("Số lượng phải lớn hơn 0")

        gia = kho_hang[ma_sp]
        thanh_tien = gia * so_luong

        return {"thanh_cong": True, "thanh_tien": thanh_tien}

    except SanPhamKhongTonException as e:
        return {"thanh_cong": False, "loi": str(e)}
    except SoLuongKhongHopLeException as e:
        return {"thanh_cong": False, "loi": str(e)}
    except ValueError:
        return {"thanh_cong": False, "loi": f"'{so_luong_input}' không phải số hợp lệ"}
    finally:
        print(f"Đã xử lý yêu cầu cho mã sản phẩm: {ma_sp}")


kho = {"SP001": 150000, "SP002": 450000}

don_1 = xu_ly_don_hang(kho, "SP001", "3")
don_2 = xu_ly_don_hang(kho, "SP999", "2")
don_3 = xu_ly_don_hang(kho, "SP001", "-5")
don_4 = xu_ly_don_hang(kho, "SP001", "abc")

for i, don in enumerate([don_1, don_2, don_3, don_4], start=1):
    print(f"Đơn {i}: {don}")
```

Cách thiết kế "hàm luôn trả về dict có `thanh_cong: True/False`" là một **mẫu thiết kế (pattern) rất phổ biến** trong API thực tế — nơi gọi hàm không cần bọc `try/except` mà chỉ cần kiểm tra `if ket_qua["thanh_cong"]:` — code gọi hàm trở nên đơn giản và dễ đọc hơn.

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_10.py` xây dựng **hệ thống xử lý thanh toán chống lỗi toàn diện**:

python

```python
tai_khoan = {
    "TK001": {"so_du": 5000000, "bi_khoa": False},
    "TK002": {"so_du": 200000, "bi_khoa": True},
}
```

Yêu cầu:

1. Tạo 2 custom exception: `TaiKhoanKhongTonException` và `TaiKhoanBiKhoaException`
2. Viết hàm `chuyen_tien(tai_khoan_dict, ma_tk, so_tien_input)`:
  - Raise `TaiKhoanKhongTonException` nếu `ma_tk` không tồn tại
  - Raise `TaiKhoanBiKhoaException` nếu tài khoản bị khóa
  - Bắt `ValueError` nếu `so_tien_input` không ép được thành số
  - Raise `ValueError` riêng (tự viết) nếu số tiền <= 0 hoặc vượt quá số dư
  - Nếu mọi thứ hợp lệ, trừ tiền và trả về dict `{"thanh_cong": True, "so_du_moi": ...}`
  - Dùng `finally` để in ra dòng log `"Giao dịch trên tài khoản {ma_tk} đã xử lý xong"` trong MỌI trường hợp
3. Gọi hàm với ít nhất 4 trường hợp khác nhau (tài khoản không tồn tại, bị khóa, số tiền không hợp lệ, giao dịch thành công) và in kết quả từng trường hợp
4. Thử thách thêm: thêm khối `else` vào cấu trúc `try` để in ra "Giao dịch hợp lệ về mặt logic" chỉ khi không có lỗi nào xảy ra trong `try`

---

🎉 **Chúc mừng bạn đã hoàn thành toàn bộ Giai đoạn 1 — Nền tảng cốt lõi!** Bạn giờ đã nắm được: biến/kiểu dữ liệu, string, rẽ nhánh, vòng lặp, 4 cấu trúc dữ liệu chính (list/tuple/set/dict), hàm, và xử lý lỗi — đây là bộ công cụ đủ để viết được những chương trình Python có ý nghĩa thực tế.

Làm bài tập xong gửi tôi xem nhé. Sau đó ta chính thức bước vào **Giai đoạn 2 — Trung cấp**, bắt đầu với **Bài 11: Làm việc với File** — kỹ năng đọc/ghi file văn bản, CSV, JSON, dùng `with` để quản lý tài nguyên an toàn (giải quyết triệt để vấn đề `finally` đóng file mà ta vừa thấy ở bài này).
