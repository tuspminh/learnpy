Chào bạn! Bài 4 với hàm là một bước ngoặt quan trọng - hy vọng bạn đã thực hành nhiều. Bây giờ chúng ta sang **Bài 5: Xử lý Ngoại lệ** - kỹ năng giúp code của bạn **không bao giờ bị lỗi giữa chừng**, chạy chuyên nghiệp như phần mềm thương mại!

---

# 📘 BÀI 5: XỬ LÝ NGOẠI LỆ (EXCEPTION HANDLING)

---

## 🎯 MỤC TIÊU BÀI HỌC

Sau bài này, bạn sẽ:
- Hiểu lỗi (Error) và ngoại lệ (Exception) khác nhau thế nào
- Bắt và xử lý mọi loại lỗi với `try/except`
- Sử dụng `else` và `finally` đúng cách
- Tự tạo Exception của riêng mình
- Viết code **an toàn, không sập** dù người dùng nhập gì đi nữa

---

## 📖 PHẦN 1: LÝ THUYẾT CÔ ĐỌNG

### 1.1. Lỗi cú pháp vs Ngoại lệ

```python
# LỖI CÚ PHÁP (Syntax Error) - Không chạy được
# print("Hello"   # Thiếu dấu ) -> SyntaxError

# NGOẠI LỆ (Exception) - Lỗi khi đang chạy
print(10 / 0)  # ZeroDivisionError: division by zero

# Các ngoại lệ thường gặp:
int("abc")  # ValueError
[1, 2, 3][10]  # IndexError
{"a": 1}["b"]  # KeyError
10 + "5"  # TypeError
```

---

### 1.2. Cú pháp `try/except` cơ bản

```python
try:
    # Code có thể gây lỗi
    so = int(input("Nhập số: "))
    ket_qua = 100 / so
    print(f"100 / {so} = {ket_qua}")
    
except ValueError:
    # Xử lý lỗi nhập sai
    print("Lỗi: Bạn phải nhập số!")
    
except ZeroDivisionError:
    # Xử lý lỗi chia cho 0
    print("Lỗi: Không thể chia cho 0!")
    
except Exception as e:
    # Bắt tất cả lỗi khác (nên để cuối cùng)
    print(f"Lỗi không xác định: {e}")
```

**Cách viết gọn hơn - bắt nhiều lỗi 1 lúc:**
```python
try:
    so = int(input("Nhập số: "))
    ket_qua = 100 / so
    print(ket_qua)
    
except (ValueError, ZeroDivisionError) as e:
    print(f"Lỗi: {e}")
```

---

### 1.3. `else` và `finally` - Khi nào dùng?

```python
try:
    so = int(input("Nhập số: "))
    ket_qua = 100 / so
    
except ValueError:
    print("Lỗi: Không phải số hợp lệ!")
    
except ZeroDivisionError:
    print("Lỗi: Chia cho 0!")
    
else:
    # Chạy khi KHÔNG có lỗi
    print(f"Kết quả: {ket_qua}")
    print("✅ Chương trình chạy thành công!")
    
finally:
    # LUÔN chạy, dù có lỗi hay không
    print("🔒 Đóng kết nối, giải phóng tài nguyên...")
    print("Hoàn tất xử lý!")
```

**Ứng dụng thực tế của `finally`:**
```python
def doc_file():
    file = None
    try:
        file = open("data.txt", "r")
        noi_dung = file.read()
        return noi_dung
    except FileNotFoundError:
        print("Không tìm thấy file!")
    finally:
        # Luôn đóng file dù có lỗi hay không
        if file:
            file.close()
            print("File đã được đóng!")
```

---

### 1.4. Các loại ngoại lệ phổ biến (Nên biết)

| Ngoại lệ | Khi nào xảy ra |
|----------|----------------|
| `ValueError` | Ép kiểu sai: `int("abc")` |
| `TypeError` | Phép toán không hợp lệ: `10 + "5"` |
| `ZeroDivisionError` | Chia cho 0 |
| `IndexError` | Truy cập index không tồn tại trong list |
| `KeyError` | Truy cập key không tồn tại trong dict |
| `FileNotFoundError` | Mở file không có |
| `AttributeError` | Gọi method không có của object |
| `ImportError` | Import module không tồn tại |
| `ConnectionError` | Lỗi kết nối mạng |
| `KeyboardInterrupt` | Người dùng bấm Ctrl+C |

---

### 1.5. Tự tạo Exception (Custom Exception)

```python
# Tạo class Exception của riêng bạn
class TuoiKhongHopLeError(Exception):
    """Exception khi tuổi không hợp lệ"""

    def __init__(self, tuoi, message="Tuổi phải từ 0-120"):
        self.tuoi = tuoi
        self.message = message
        super().__init__(self.message)


class SoDuKhongDuError(Exception):
    """Exception khi số dư không đủ"""

    def __init__(self, so_du, so_tien_rut):
        self.so_du = so_du
        self.so_tien_rut = so_tien_rut
        super().__init__(f"Số dư {so_du} không đủ để rút {so_tien_rut}")


# Sử dụng
def kiem_tra_tuoi(tuoi):
    if not (0 <= tuoi <= 120):
        raise TuoiKhongHopLeError(tuoi)
    print(f"Tuổi {tuoi} hợp lệ!")


try:
    nguoi_tuoi = int(input("Nhập tuổi: "))
    kiem_tra_tuoi(nguoi_tuoi)
except TuoiKhongHopLeError as e:
    print(f"Lỗi: {e}")
    print(f"Tuổi đã nhập: {e.tuoi}")
except ValueError:
    print("Lỗi: Phải nhập số!")
```

---

### 1.6. `raise` - Tự ném ra ngoại lệ

```python
def tinh_tuoi(nam_sinh, nam_hien_tai=2026):
    """Tính tuổi, ném lỗi nếu dữ liệu không hợp lệ"""

    if not isinstance(nam_sinh, int):
        raise TypeError("Năm sinh phải là số nguyên!")

    if nam_sinh < 1900:
        raise ValueError(f"Năm sinh {nam_sinh} quá cũ!")

    if nam_sinh > nam_hien_tai:
        raise ValueError(f"Năm sinh {nam_sinh} không thể lớn hơn năm hiện tại!")

    return nam_hien_tai - nam_sinh


# Sử dụng
try:
    nam = input("Nhập năm sinh: ")
    tuoi = tinh_tuoi(int(nam))
    print(f"Tuổi: {tuoi}")
except (ValueError, TypeError) as e:
    print(f"Lỗi: {e}")
```

---

### 1.7. Assert - Kiểm tra điều kiện (Debug)

```python
def tinh_tich(a, b):
    # Assert: Nếu sai, chương trình dừng ngay
    assert isinstance(a, (int, float)), "a phải là số"
    assert isinstance(b, (int, float)), "b phải là số"
    return a * b


# Nếu chạy với -O (optimize), assert bị bỏ qua
print(tinh_tich(5, 3))  # 15
# print(tinh_tich("5", 3))  # AssertionError: a phải là số


# Ứng dụng: Kiểm tra input
def tinh_tong_2_so(a, b):
    assert a > 0 and b > 0, "Cả 2 số phải dương!"
    return a + b


print(tinh_tong_2_so(5, 3))  # 8
# print(tinh_tong_2_so(-1, 5))  # AssertionError
```

---

## 💻 PHẦN 2: CODE VÍ DỤ THỰC TẾ

### Ví dụ 1: Máy tính an toàn (Không bao giờ sập)

```python
def may_tinh():
    print("=" * 40)
    print("MÁY TÍNH ĐƠN GIẢN (nhập 'exit' để thoát)")
    print("=" * 40)

    while True:
        try:
            # Nhập biểu thức
            bieu_thuc = input("\nNhập phép tính (vd: 10 + 5): ")

            if bieu_thuc.lower() == "exit":
                print("Tạm biệt!")
                break

            # Tách và xử lý
            parts = bieu_thuc.split()
            if len(parts) != 3:
                print("❌ Vui lòng nhập đúng định dạng: số + toán tử + số")
                continue

            so1 = float(parts[0])
            toan_tu = parts[1]
            so2 = float(parts[2])

            # Tính toán
            if toan_tu == "+":
                ket_qua = so1 + so2
            elif toan_tu == "-":
                ket_qua = so1 - so2
            elif toan_tu == "*":
                ket_qua = so1 * so2
            elif toan_tu == "/":
                ket_qua = so1 / so2
            else:
                print("❌ Toán tử không hỗ trợ! Dùng +, -, *, /")
                continue

            print(f"✅ {so1} {toan_tu} {so2} = {ket_qua}")

        except ValueError:
            print("❌ Lỗi: Vui lòng nhập số hợp lệ!")
        except ZeroDivisionError:
            print("❌ Lỗi: Không thể chia cho 0!")
        except Exception as e:
            print(f"❌ Lỗi không xác định: {e}")
        else:
            # Chạy khi không có lỗi
            print("✨ Phép tính thành công!")
        finally:
            # Luôn chạy
            print("-" * 40)


# Chạy máy tính
may_tinh()
```

---

### Ví dụ 2: Hệ thống quản lý sách (Kiểm tra dữ liệu chặt chẽ)

```python
class DuLieuSachError(Exception):
    """Lỗi dữ liệu sách không hợp lệ"""

    pass


class Sach:
    def __init__(self, ma, ten, tac_gia, nam_xuat_ban):
        self.ma = ma
        self.ten = ten
        self.tac_gia = tac_gia
        self.nam_xuat_ban = nam_xuat_ban
        self.trang_thai = "Có sẵn"

    @classmethod
    def tao_tu_dict(cls, data):
        """Tạo đối tượng Sach từ dict, kiểm tra dữ liệu"""
        try:
            ma = data.get("ma")
            ten = data.get("ten")
            tac_gia = data.get("tac_gia")
            nam = data.get("nam_xuat_ban")

            # Kiểm tra dữ liệu
            if not ma or not ten or not tac_gia:
                raise DuLieuSachError("Thiếu thông tin bắt buộc: mã, tên, tác giả")

            if not isinstance(nam, int) or nam < 0 or nam > 2026:
                raise DuLieuSachError(f"Năm xuất bản {nam} không hợp lệ!")

            return cls(ma, ten, tac_gia, nam)

        except DuLieuSachError as e:
            raise  # Ném tiếp lỗi lên trên
        except Exception as e:
            raise DuLieuSachError(f"Dữ liệu không hợp lệ: {e}")

    def muon(self):
        if self.trang_thai == "Đã mượn":
            raise ValueError(f"Sách {self.ma} đã được mượn!")
        self.trang_thai = "Đã mượn"
        return f"Đã mượn sách: {self.ten}"

    def tra(self):
        if self.trang_thai == "Có sẵn":
            raise ValueError(f"Sách {self.ma} đã có sẵn!")
        self.trang_thai = "Có sẵn"
        return f"Đã trả sách: {self.ten}"


# Sử dụng hệ thống
def quan_ly_sach():
    danh_sach_sach = []

    while True:
        try:
            print("\n1. Thêm sách")
            print("2. Mượn sách")
            print("3. Trả sách")
            print("4. Hiển thị tất cả")
            print("5. Thoát")

            choice = input("Chọn chức năng: ")

            if choice == "1":
                # Nhập dữ liệu sách
                ma = input("Mã sách: ").strip()
                ten = input("Tên sách: ").strip()
                tac_gia = input("Tác giả: ").strip()
                nam = int(input("Năm xuất bản: "))

                # Tạo sách với kiểm tra
                sach = Sach.tao_tu_dict(
                    {"ma": ma, "ten": ten, "tac_gia": tac_gia, "nam_xuat_ban": nam}
                )
                danh_sach_sach.append(sach)
                print(f"✅ Đã thêm sách: {sach.ten}")

            elif choice == "2":
                ma = input("Nhập mã sách cần mượn: ")
                # Tìm sách
                sach_tim = next((s for s in danh_sach_sach if s.ma == ma), None)
                if not sach_tim:
                    raise ValueError(f"Không tìm thấy sách mã {ma}")
                print(sach_tim.muon())

            elif choice == "3":
                ma = input("Nhập mã sách cần trả: ")
                sach_tim = next((s for s in danh_sach_sach if s.ma == ma), None)
                if not sach_tim:
                    raise ValueError(f"Không tìm thấy sách mã {ma}")
                print(sach_tim.tra())

            elif choice == "4":
                print("\n=== DANH SÁCH SÁCH ===")
                for s in danh_sach_sach:
                    print(
                        f"{s.ma}: {s.ten} - {s.tac_gia} ({s.nam_xuat_ban}) - {s.trang_thai}"
                    )

            elif choice == "5":
                print("Tạm biệt!")
                break

        except ValueError as e:
            print(f"❌ Lỗi: {e}")
        except DuLieuSachError as e:
            print(f"❌ Lỗi dữ liệu: {e}")
        except Exception as e:
            print(f"❌ Lỗi không xác định: {e}")
        finally:
            print("-" * 40)


# Chạy
quan_ly_sach()
```

---

### Ví dụ 3: Retry logic - Thử lại khi có lỗi

```python
import time
import random


def ket_noi_api(attempt=3):
    """Mô phỏng kết nối API với cơ chế thử lại"""

    for i in range(attempt):
        try:
            print(f"Đang kết nối lần {i + 1}...")
            time.sleep(0.5)

            # Mô phỏng lỗi ngẫu nhiên
            if random.random() < 0.6:  # 60% lỗi
                raise ConnectionError("Mất kết nối mạng!")

            # Giả lập thành công
            data = {"status": "success", "data": [1, 2, 3]}
            print("✅ Kết nối thành công!")
            return data

        except ConnectionError as e:
            print(f"⚠️ Lỗi: {e}")
            if i < attempt - 1:
                wait = 2**i  # Exponential backoff: 1s, 2s, 4s
                print(f"Thử lại sau {wait}s...")
                time.sleep(wait)
            else:
                raise Exception(f"Kết nối thất bại sau {attempt} lần thử")


# Sử dụng
try:
    ket_qua = ket_noi_api(3)
    print("Kết quả:", ket_qua)
except Exception as e:
    print(f"❌ {e}")
```

---

## 🧪 PHẦN 3: BÀI TẬP VỀ NHÀ (10 bài)

### 📌 Bài tập cơ bản (6 bài)

**Bài 1:** Viết chương trình yêu cầu nhập số nguyên. Bắt lỗi nếu người dùng nhập không phải số, yêu cầu nhập lại đến khi đúng.

**Bài 2:** Viết hàm `tinh_trung_binh(ds_so)` tính trung bình cộng, xử lý:
- Danh sách rỗng → raise ValueError
- Phần tử không phải số → TypeError
- Trả về trung bình

**Bài 3:** Viết chương trình đọc file `data.txt`. Nếu file không tồn tại, tạo file mới với nội dung mặc định.

**Bài 4:** Cho list `[1, 2, 3]`. Viết hàm `lay_phan_tu(index)`:
- Nếu index hợp lệ → trả về phần tử
- Nếu index không hợp lệ → bắt IndexError và in ra thông báo

**Bài 5:** Nhập 2 số a, b. Tính a/b, xử lý tất cả lỗi có thể xảy ra (ValueError, ZeroDivisionError, TypeError).

**Bài 6:** Tạo class `TaiKhoan` với các method `nap_tien`, `rut_tien`. Tạo custom exception `SoDuKhongDuError`, `SoTienAmError`.

---

### ⭐ Bài tập nâng cao (4 bài)

**Bài 7:** Viết decorator `xu_ly_loi` tự động bắt exception cho bất kỳ hàm nào:
```python
@xu_ly_loi
def ham_co_loi():
    return 10 / 0


# Khi gọi, tự động in ra lỗi thay vì crash
```

**Bài 8:** Hệ thống đăng nhập với 3 lần thử:
- Nhập username và password
- Sai → báo lỗi và giảm số lần thử
- Đúng → chào mừng và break
- Sai 3 lần → raise `KhoaTaiKhoanError`

**Bài 9:** Viết chương trình kiểm tra định dạng email:
- Tạo Exception: `EmailFormatError`
- Kiểm tra: có @, có domain (.com, .vn, .org...)
- Raise exception nếu sai format

**Bài 10:** Xây dựng hệ thống chuyển đổi tiền tệ:
- Dictionary tỷ giá: `{"USD": 25500, "EUR": 28000, "JPY": 230}`
- Hàm `doi_tien(so_tien, tu_loai, den_loai)` 
- Xử lý lỗi: loại tiền không hỗ trợ, số tiền âm, kiểu dữ liệu sai

---

## 🏗️ MINI-PROJECT: HỆ THỐNG NGÂN HÀNG AN TOÀN

```python
"""
Xây dựng hệ thống ngân hàng với xử lý lỗi hoàn chỉnh:

1. Class NganHang:
   - `__init__()`: Tạo 5 tài khoản mặc định
   - `dang_nhap(so_tk, pin)`: Login, kiểm tra tài khoản
   - `xem_so_du()`: Hiển thị số dư
   - `rut_tien(so_tien)`: Rút tiền (kiểm tra nhiều điều kiện)
   - `chuyen_tien(so_tk_nhan, so_tien)`: Chuyển tiền
   - `nap_tien(so_tien)`: Nạp tiền

2. Custom Exceptions cần có:
   - TaiKhoanKhongTonTaiError
   - PinSaiError
   - SoDuKhongDuError
   - GiaoDichQuaHanMucError
   - TaiKhoanBiKhoaError

3. Xử lý tất cả trường hợp:
   - Nhập sai định dạng (dùng try/except)
   - Số tiền không hợp lệ (< 0, > 0)
   - Quá hạn mức giao dịch (100 triệu/ngày)
   - Tài khoản bị khóa sau 5 lần nhập sai PIN
"""

# Hãy tự viết!
```

---

## ✅ KIỂM TRA CODE CHUYÊN NGHIỆP

- [ ] Sử dụng exception cụ thể, không chỉ `except: pass`
- [ ] Có `finally` để giải phóng tài nguyên (file, database, network)
- [ ] Custom Exception có tên rõ ràng, kế thừa từ `Exception`
- [ ] Không bắt quá rộng (tránh `except Exception` trừ khi cần)
- [ ] Thông báo lỗi rõ ràng, hữu ích cho người dùng
- [ ] Sử dụng `else` đúng mục đích (code chạy khi không lỗi)
- [ ] Log lỗi (ghi lại) để debug sau này

---

## 🔥 THỬ THÁCH (Bonus)

```python
# Viết hàm retry decorator
@retry(max_attempts=3, delay=1, exceptions=(ValueError, ConnectionError))
def ket_noi_he_thong():
    # Code có thể gây lỗi
    pass


# Decorator tự động thử lại khi có lỗi
# Hãy tự implement!
```

---

## 🎯 TÓM TẮT KIẾN THỨC QUAN TRỌNG

| Khái niệm | Cú pháp | Ứng dụng |
|-----------|---------|----------|
| **Try/Except** | `try: ... except ErrorType: ...` | Bắt và xử lý lỗi |
| **Multiple except** | `except (Error1, Error2):` | Bắt nhiều lỗi 1 lúc |
| **Else** | `else: ...` | Chạy khi không có lỗi |
| **Finally** | `finally: ...` | Luôn chạy (đóng file, db) |
| **Raise** | `raise ValueError("msg")` | Chủ động ném lỗi |
| **Custom Exception** | `class MyError(Exception):` | Lỗi riêng cho ứng dụng |
| **Assert** | `assert condition, "msg"` | Debug, kiểm tra điều kiện |

---

## 📝 LỜI KHUYỂN VÀNG

> **"Code của bạn không bao giờ hoàn hảo, nhưng nó có thể an toàn!"**

1. **Luôn luôn xử lý lỗi** ở những nơi có input từ người dùng
2. **Không bỏ qua exception** bằng `except: pass` 
3. **Log lỗi** để biết chuyện gì đã xảy ra
4. **Tạo custom exception** để code có ý nghĩa hơn
5. **Sử dụng finally** để đảm bảo giải phóng tài nguyên

---

**Chúc mừng bạn! Sau 5 bài, bạn đã có nền tảng vững chắc về Python cốt lõi.** 💪

*Bài 6 sẽ là OOP (Lớp và Đối tượng) - Nếu bạn đã nắm vững 5 bài này, bạn sẵn sàng để bước sang lập trình hướng đối tượng!*

**Hãy gửi code 5 bài tập để tôi review nhé!** 🚀