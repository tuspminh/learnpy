### 📘 Bài 21: Testing (unittest, pytest)

Đây là bài học đánh dấu ranh giới rõ rệt nhất giữa "code cho vui, chạy thử bằng mắt" và **"code chuyên nghiệp sẵn sàng đưa vào production"**. Từ bài này, bạn sẽ học cách để *chương trình tự kiểm tra chương trình* — nền tảng bắt buộc trong mọi quy trình phát triển phần mềm hiện đại (CI/CD).

---

#### 1. Tại sao không thể chỉ `print()` để kiểm tra code?

Từ đầu khóa học, cách bạn kiểm tra code đúng/sai là:

python

```python
ket_qua = tinh_thue_tncn(8000000)
print(ket_qua)   # nhìn bằng mắt, tự so sánh với kết quả mong đợi
```

**Vấn đề nghiêm trọng của cách này ở quy mô thực tế:**

- Khi hàm được sửa lại sau 6 tháng (bởi bạn hoặc đồng nghiệp), ai đảm bảo logic cũ vẫn đúng? Phải `print()` kiểm tra lại bằng tay **mọi lần**
- Với project có hàng trăm hàm, kiểm tra bằng mắt là **không thể** — cần hàng giờ, dễ bỏ sót lỗi
- Không có "bằng chứng" khách quan rằng code đúng — chỉ là cảm giác chủ quan của người viết

**Giải pháp: Automated Testing (kiểm thử tự động)** — viết code riêng, chuyên để **kiểm tra code chính** có hoạt động đúng như mong đợi hay không, chạy lại bất cứ lúc nào chỉ với một lệnh.

---

#### 2. `unittest` — Framework testing có sẵn của Python

`unittest` là module built-in (không cần `pip install`), lấy cảm hứng từ JUnit (Java) — chuẩn công nghiệp lâu đời.

**Giả sử ta có hàm cần test** (file `tinh_luong.py`):

python

```python
def tinh_thue_tncn(thu_nhap: float) -> float:
    if thu_nhap <= 5_000_000:
        return 0
    elif thu_nhap <= 10_000_000:
        return (thu_nhap - 5_000_000) * 0.05
    else:
        return (10_000_000 - 5_000_000) * 0.05 + (thu_nhap - 10_000_000) * 0.1
```

**Viết test (file `test_tinh_luong.py`):**

python

```python
import unittest
from tinh_luong import tinh_thue_tncn

class TestTinhThueTNCN(unittest.TestCase):

    def test_thu_nhap_duoi_nguong_khong_thue(self):
        """Thu nhập <= 5 triệu -> thuế = 0"""
        self.assertEqual(tinh_thue_tncn(4_000_000), 0)
        self.assertEqual(tinh_thue_tncn(5_000_000), 0)

    def test_thu_nhap_bac_thue_5_phan_tram(self):
        """Thu nhập 5-10 triệu -> thuế 5% trên phần vượt"""
        self.assertEqual(tinh_thue_tncn(8_000_000), 150_000)   # (8tr - 5tr) * 5%

    def test_thu_nhap_bac_thue_10_phan_tram(self):
        """Thu nhập > 10 triệu -> thuế 5% (bậc 1) + 10% (phần vượt)"""
        self.assertEqual(tinh_thue_tncn(15_000_000), 750_000)  # 250k + (5tr * 10%)

    def test_thu_nhap_am_nen_bao_loi(self):
        """Thu nhập âm là dữ liệu vô lý - test này minh họa CHƯA xử lý, sẽ fail"""
        with self.assertRaises(ValueError):
            tinh_thue_tncn(-1000)


if __name__ == "__main__":
    unittest.main()
```

**Chạy test:**

bash

```bash
python -m unittest test_tinh_luong.py -v
```

**Kết quả mẫu:**

```
test_thu_nhap_am_nen_bao_loi ... FAIL
test_thu_nhap_bac_thue_10_phan_tram ... ok
test_thu_nhap_bac_thue_5_phan_tram ... ok
test_thu_nhap_duoi_nguong_khong_thue ... ok
```

Test `test_thu_nhap_am_nen_bao_loi` **FAIL** — đây chính xác là giá trị của testing: nó **phát hiện ngay** rằng hàm `tinh_thue_tncn` hiện tại chưa xử lý trường hợp thu nhập âm (không raise `ValueError` như mong đợi), một lỗi mà bạn có thể dễ dàng bỏ sót nếu chỉ kiểm tra bằng `print()`.

---

#### 3. Các phương thức `assert` phổ biến trong `unittest`

python

```python
self.assertEqual(a, b)          # a == b
self.assertNotEqual(a, b)       # a != b
self.assertTrue(x)               # x là True
self.assertFalse(x)              # x là False
self.assertIsNone(x)             # x is None
self.assertIn(item, list_)       # item có trong list_
self.assertRaises(ValueError)    # đoạn code raise đúng loại exception
self.assertAlmostEqual(a, b, places=2)  # so sánh float, cho phép sai số nhỏ (QUAN TRỌNG cho số thực!)
```

**Lưu ý cực kỳ quan trọng về `assertAlmostEqual`** — nhớ lại cạm bẫy số thực ở Bài 2 (`0.1 + 0.2 != 0.3` do sai số dấu phẩy động):

python

```python
# ❌ Có thể FAIL sai một cách vô lý do sai số float
self.assertEqual(0.1 + 0.2, 0.3)   # FAIL! 0.30000000000000004 != 0.3

# ✅ Đúng cách khi test với số thực
self.assertAlmostEqual(0.1 + 0.2, 0.3, places=7)   # PASS
```

---

#### 4. `setUp` và `tearDown` — chuẩn bị và dọn dẹp trước/sau mỗi test

python

```python
import unittest
import sqlite3

class TestQuanLyKho(unittest.TestCase):

    def setUp(self):
        """Chạy TRƯỚC mỗi test method - tạo môi trường sạch, độc lập"""
        self.ket_noi = sqlite3.connect(":memory:")   # database TẠM trong RAM, không tạo file thật
        self.ket_noi.execute("""
            CREATE TABLE san_pham (id INTEGER PRIMARY KEY, ten TEXT, ton_kho INTEGER)
        """)
        self.ket_noi.execute("INSERT INTO san_pham VALUES (1, 'Laptop', 10)")
        self.ket_noi.commit()

    def tearDown(self):
        """Chạy SAU mỗi test method - dọn dẹp, tránh test này ảnh hưởng test khác"""
        self.ket_noi.close()

    def test_ton_kho_ban_dau(self):
        cursor = self.ket_noi.execute("SELECT ton_kho FROM san_pham WHERE id = 1")
        self.assertEqual(cursor.fetchone()[0], 10)
```

**Nguyên tắc thực chiến quan trọng bậc nhất trong testing — "Test Isolation" (mỗi test độc lập)**: dùng `:memory:` (database SQLite tạm trong RAM, nhớ lại Bài 20) đảm bảo mỗi test chạy trên dữ liệu **hoàn toàn mới, sạch sẽ**, không bị ảnh hưởng bởi test trước đó chạy để lại dữ liệu — đây là nguyên nhân phổ biến nhất khiến test "lúc pass lúc fail" một cách khó hiểu (flaky test) trong thực tế.

---

#### 5. `pytest` — Framework testing được ưa chuộng nhất trong ngành 2026

`pytest` không phải built-in, cần cài: `pip install pytest`. Nó phổ biến hơn `unittest` trong hầu hết codebase chuyên nghiệp hiện đại vì cú pháp **ngắn gọn hơn nhiều**, không cần class, không cần nhớ tên phương thức `assertEqual` — chỉ cần từ khóa `assert` chuẩn của Python.

**Test tương đương viết bằng pytest** (file `test_tinh_luong_pytest.py`):

python

```python
import pytest
from tinh_luong import tinh_thue_tncn

def test_thu_nhap_duoi_nguong_khong_thue():
    assert tinh_thue_tncn(4_000_000) == 0
    assert tinh_thue_tncn(5_000_000) == 0

def test_thu_nhap_bac_thue_5_phan_tram():
    assert tinh_thue_tncn(8_000_000) == 150_000

def test_thu_nhap_bac_thue_10_phan_tram():
    assert tinh_thue_tncn(15_000_000) == 750_000

def test_thu_nhap_am_nen_bao_loi():
    with pytest.raises(ValueError):
        tinh_thue_tncn(-1000)
```

**Chạy test:**

bash

```bash
pytest test_tinh_luong_pytest.py -v
```

So sánh trực quan: `unittest` cần class kế thừa `TestCase`, gọi `self.assertEqual(...)`; `pytest` chỉ cần hàm bắt đầu bằng `test_`, dùng `assert` thuần Python — đây là lý do pytest được xem là "Pythonic hơn" và được cộng đồng ưa chuộng áp dụng rộng rãi trong các dự án mới.

---

#### 6. Fixture trong pytest — nâng cấp của `setUp`/`tearDown`

python

```python
import pytest
import sqlite3

@pytest.fixture
def db_ket_noi():
    """Fixture - chuẩn bị dữ liệu test, tự động 'yield' rồi dọn dẹp sau khi test xong"""
    ket_noi = sqlite3.connect(":memory:")
    ket_noi.execute("CREATE TABLE san_pham (id INTEGER PRIMARY KEY, ten TEXT, ton_kho INTEGER)")
    ket_noi.execute("INSERT INTO san_pham VALUES (1, 'Laptop', 10)")
    ket_noi.commit()

    yield ket_noi    # trả về giá trị cho test dùng, code SAU yield chạy khi test xong

    ket_noi.close()   # tự động dọn dẹp

def test_ton_kho_ban_dau(db_ket_noi):
    """pytest TỰ ĐỘNG truyền fixture vào test qua tên tham số khớp"""
    cursor = db_ket_noi.execute("SELECT ton_kho FROM san_pham WHERE id = 1")
    assert cursor.fetchone()[0] == 10
```

Fixture linh hoạt hơn `setUp`/`tearDown` vì có thể **tái sử dụng giữa nhiều file test**, và pytest tự động "tiêm" (inject) đúng fixture vào test cần nó chỉ qua tên tham số khớp — đây là cơ chế **Dependency Injection** đơn giản, khái niệm quan trọng trong kỹ thuật phần mềm hiện đại.

---

#### 7. Parametrize — chạy 1 test với nhiều bộ dữ liệu

Đây là kỹ thuật giúp tránh viết lặp lại nhiều test giống nhau chỉ khác dữ liệu đầu vào — áp dụng trực tiếp nguyên tắc DRY đã học ở Bài 9:

python

```python
import pytest
from tinh_luong import tinh_thue_tncn

@pytest.mark.parametrize("thu_nhap, thue_mong_doi", [
    (3_000_000, 0),
    (5_000_000, 0),
    (8_000_000, 150_000),
    (10_000_000, 250_000),
    (15_000_000, 750_000),
])
def test_tinh_thue_nhieu_truong_hop(thu_nhap, thue_mong_doi):
    assert tinh_thue_tncn(thu_nhap) == thue_mong_doi
```

Kết quả: pytest tự động chạy **5 test case riêng biệt** từ 1 hàm test duy nhất, mỗi trường hợp báo pass/fail độc lập — cực kỳ hiệu quả khi cần kiểm tra hàm với nhiều bộ dữ liệu biên (boundary values).

---

#### 8. Mocking — giả lập API/Database khi test, không gọi thật

Nhớ lại Bài 19 (gọi API thực): nếu hàm của bạn gọi API thật trong test, mỗi lần chạy test sẽ **thực sự gửi request** — chậm, tốn tiền (nếu API trả phí), và **fail nếu mất mạng** dù code hoàn toàn đúng. Giải pháp: **mock** (giả lập) phần gọi API.

python

```python
from unittest.mock import patch
import requests

def lay_gia_usd_vnd():
    response = requests.get("https://api.exchangerate.com/usd-vnd")
    return response.json()["rate"]


@patch("requests.get")   # "giả mạo" requests.get, không gọi mạng thật
def test_lay_gia_usd_vnd(mock_get):
    # Định nghĩa mock trả về gì khi được gọi
    mock_get.return_value.json.return_value = {"rate": 26150.5}

    ket_qua = lay_gia_usd_vnd()

    assert ket_qua == 26150.5
    mock_get.assert_called_once()   # kiểm tra requests.get được gọi ĐÚNG 1 lần
```

**Nguyên tắc cốt lõi cần khắc sâu**: test nên **nhanh, đáng tin cậy, độc lập với môi trường bên ngoài** (mạng, database thật, thời gian hệ thống...). Mocking là kỹ thuật để đạt được điều này khi code của bạn phụ thuộc vào những yếu tố bên ngoài không kiểm soát được — một kỹ năng bắt buộc khi test các hệ thống thực tế có gọi API bên thứ ba.

---

#### 9. Code Coverage — đo lường bao nhiêu % code đã được test

bash

```bash
pip install pytest-cov
pytest --cov=tinh_luong test_tinh_luong_pytest.py
```

**Kết quả mẫu:**

```
Name             Stmts   Miss  Cover
------------------------------------
tinh_luong.py        6      0   100%
```

Coverage 100% **không đồng nghĩa** code không có bug — nó chỉ nghĩa là mọi dòng code đã được *chạy qua* ít nhất 1 lần trong test, không đảm bảo mọi *tình huống logic* đã được kiểm tra đầy đủ. Đây là chỉ số hữu ích để phát hiện phần code **hoàn toàn chưa được test tới**, nhưng không nên coi là mục tiêu tuyệt đối "phải đạt 100%" — 80-90% coverage có ý nghĩa thực tế hơn nhiều so với việc chạy theo con số.

---

#### 10. Ví dụ thực chiến tổng hợp — Test cho module xử lý đơn hàng

python

```python
# module: xu_ly_don_hang.py
class SoDuKhongDuException(Exception):
    pass

def tinh_tong_don_hang(san_pham: list[dict], ma_giam_gia: str = None) -> float:
    ty_le_giam = {"SALE10": 0.1, "SALE20": 0.2}.get(ma_giam_gia, 0.0)
    tong = sum(sp["gia"] * sp["so_luong"] for sp in san_pham)
    return tong * (1 - ty_le_giam)


def rut_tien(so_du: float, so_tien: float) -> float:
    if so_tien > so_du:
        raise SoDuKhongDuException(f"Số dư {so_du:,} không đủ để rút {so_tien:,}")
    return so_du - so_tien
```

python

```python
# test_xu_ly_don_hang.py
import pytest
from xu_ly_don_hang import tinh_tong_don_hang, rut_tien, SoDuKhongDuException


class TestTinhTongDonHang:
    """Nhóm test theo class giúp tổ chức rõ ràng hơn khi có nhiều test liên quan"""

    def test_khong_co_ma_giam_gia(self):
        san_pham = [{"gia": 100_000, "so_luong": 2}]
        assert tinh_tong_don_hang(san_pham) == 200_000

    def test_co_ma_giam_gia_10_phan_tram(self):
        san_pham = [{"gia": 100_000, "so_luong": 2}]
        assert tinh_tong_don_hang(san_pham, "SALE10") == 180_000

    def test_ma_giam_gia_khong_ton_tai_khong_ap_dung(self):
        san_pham = [{"gia": 100_000, "so_luong": 1}]
        assert tinh_tong_don_hang(san_pham, "MA_KHONG_TON") == 100_000

    def test_danh_sach_rong_tra_ve_0(self):
        assert tinh_tong_don_hang([]) == 0


class TestRutTien:

    def test_rut_tien_hop_le(self):
        assert rut_tien(500_000, 200_000) == 300_000

    def test_rut_vuot_so_du_raise_exception(self):
        with pytest.raises(SoDuKhongDuException):
            rut_tien(100_000, 200_000)

    def test_rut_dung_bang_so_du(self):
        """Test biên (boundary test) - trường hợp rút đúng bằng số dư hiện có"""
        assert rut_tien(100_000, 100_000) == 0
```

Lưu ý `test_rut_dung_bang_so_du` — đây gọi là **boundary testing (test giá trị biên)**, một kỹ thuật tư duy quan trọng: luôn test không chỉ trường hợp "bình thường" và "rõ ràng sai", mà cả **ranh giới chính xác** giữa hợp lệ/không hợp lệ — nơi bug thường ẩn náu nhiều nhất trong thực tế.

---

#### 🎯 Bài tập thực hành

Viết file test `test_bai_tap_21.py` (dùng `pytest`) cho module sau (tạo file `kho_hang.py` chứa code này trước):

python

```python
class KhongDuTonKhoException(Exception):
    pass

class SanPhamKhongTonException(Exception):
    pass

def xuat_kho(kho: dict, ma_sp: str, so_luong: int) -> dict:
    if ma_sp not in kho:
        raise SanPhamKhongTonException(f"Không tìm thấy sản phẩm {ma_sp}")
    if so_luong <= 0:
        raise ValueError("Số lượng xuất phải lớn hơn 0")
    if kho[ma_sp] < so_luong:
        raise KhongDuTonKhoException(f"Chỉ còn {kho[ma_sp]}, không đủ xuất {so_luong}")
    kho[ma_sp] -= so_luong
    return kho
```

Yêu cầu:

1. Viết ít nhất 5 test case dùng `pytest`, bao gồm: xuất hàng hợp lệ, sản phẩm không tồn tại, số lượng <= 0, không đủ tồn kho, và **test biên** (xuất đúng bằng số lượng tồn kho hiện có, kho phải về 0)
2. Dùng `@pytest.fixture` để tạo dữ liệu `kho` mẫu dùng chung cho nhiều test, tránh lặp lại code khởi tạo
3. Dùng `@pytest.mark.parametrize` để test hàm với ít nhất 4 bộ dữ liệu số lượng xuất khác nhau (một số hợp lệ, một số nên raise lỗi)
4. Chạy `pytest -v` và `pytest --cov=kho_hang` (cần `pip install pytest-cov`), báo cáo kết quả coverage đạt được
5. Thử thách thêm: cố ý sửa sai 1 dòng trong hàm `xuat_kho` (ví dụ đổi `<` thành `<=` ở điều kiện kiểm tra tồn kho) rồi chạy lại test — quan sát test nào FAIL để hiểu cách test giúp **bắt lỗi ngay khi code bị sửa sai**, đây chính là giá trị lớn nhất của automated testing trong làm việc nhóm dài hạn

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 22: Async/await — Lập trình bất đồng bộ** — kỹ năng giúp chương trình xử lý được hàng nghìn request/tác vụ I/O (gọi API, đọc file, truy vấn database) đồng thời mà không cần chờ tuần tự, nền tảng của các framework web hiện đại như FastAPI.
