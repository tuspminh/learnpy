Vai trò này tôi đã ghi nhớ từ bài 3 và đang áp dụng nhất quán suốt 11 bài qua — sẽ tiếp tục duy trì nghiêm túc đến hết hành trình của bạn.

### 📘 Bài 12: Module & Package

Đến giờ mọi code bạn viết nằm trong **một file duy nhất**. Khi dự án lớn dần lên (hàng trăm, hàng nghìn dòng code), việc dồn tất cả vào 1 file trở nên không thể quản lý được. Bài này dạy bạn cách **tổ chức code chuyên nghiệp** — kỹ năng phân định rõ ràng giữa "người mới học viết script" và "kỹ sư phần mềm xây dựng hệ thống".

---

#### 1. Module là gì?

Một **module** đơn giản là **một file `.py`** — bất kỳ file Python nào bạn viết cũng đã là một module. Bạn có thể **import** (nhập) code từ module này vào module khác để tái sử dụng.

**Ví dụ**: tạo file `tinh_toan.py`:

python

```python
# tinh_toan.py
def tinh_thue_vat(gia: float, thue_suat: float = 0.08) -> float:
    return gia * thue_suat

def tinh_tong_co_thue(gia: float) -> float:
    return gia + tinh_thue_vat(gia)

PHI_SHIP_MAC_DINH = 15000
```

Rồi tạo file khác `main.py` cùng thư mục, import và sử dụng:

python

```python
# main.py
import tinh_toan

gia_sp = 500000
tong = tinh_toan.tinh_tong_co_thue(gia_sp)
print(f"Tổng tiền có thuế: {tong:,.0f} VNĐ")
print(f"Phí ship mặc định: {tinh_toan.PHI_SHIP_MAC_DINH:,} VNĐ")
```

Khi bạn `import tinh_toan`, Python chạy toàn bộ file `tinh_toan.py` một lần, rồi cho phép bạn truy cập mọi hàm/biến trong đó qua cú pháp `tinh_toan.ten_ham()`.

---

#### 2. Các cách import — và khi nào dùng cách nào

python

```python
# Cách 1: import cả module - PHẢI gọi qua tên module (RÕ RÀNG, khuyến nghị nhất)
import tinh_toan
tinh_toan.tinh_thue_vat(500000)

# Cách 2: import module với tên viết tắt (alias) - phổ biến với thư viện tên dài
import tinh_toan as tt
tt.tinh_thue_vat(500000)

# Cách 3: import cụ thể hàm/biến cần dùng - gọi trực tiếp không cần tiền tố
from tinh_toan import tinh_thue_vat, PHI_SHIP_MAC_DINH
tinh_thue_vat(500000)   # không cần viết tinh_toan.tinh_thue_vat

# Cách 4: import TẤT CẢ (❌ KHÔNG khuyến nghị trong code chuyên nghiệp)
from tinh_toan import *
```

**Tại sao `from module import *` bị coi là "code smell" (thiết kế tệ)?** Vì nó **đưa mọi tên hàm/biến vào namespace hiện tại một cách ẩn**, khiến người đọc code không biết `tinh_thue_vat()` đến từ đâu, và dễ gây **xung đột tên (name collision)** nếu 2 module có hàm cùng tên. Trong mọi codebase chuyên nghiệp, quy tắc PEP 8 khuyến nghị tránh cách này tuyệt đối.

**Ví dụ thực tế alias cực kỳ phổ biến** mà bạn sẽ gặp trong hầu hết codebase khoa học dữ liệu:

python

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
```

---

#### 3. `if __name__ == "__main__":` — mẫu code xuất hiện trong MỌI file Python chuyên nghiệp

Đây là một trong những cú pháp gây khó hiểu nhất cho người mới, nhưng cực kỳ quan trọng để hiểu:

python

```python
# tinh_toan.py
def tinh_thue_vat(gia):
    return gia * 0.08

print(f"Module tinh_toan đang được nạp, __name__ = {__name__}")

if __name__ == "__main__":
    # Khối này CHỈ chạy khi file này được CHẠY TRỰC TIẾP (python tinh_toan.py)
    # KHÔNG chạy khi file này bị IMPORT bởi file khác
    print("Đang test hàm tinh_thue_vat...")
    print(tinh_thue_vat(100000))
```

**Cơ chế hoạt động**: Python gán biến đặc biệt `__name__` cho mỗi module.

- Khi bạn chạy trực tiếp `python tinh_toan.py` → `__name__` = `"__main__"`
- Khi file này bị import từ file khác (`import tinh_toan`) → `__name__` = `"tinh_toan"` (tên module)

**Tại sao điều này quan trọng trong thực tế?** Nó cho phép bạn viết code test/demo ngay trong module, nhưng đảm bảo đoạn test đó **không tự động chạy** khi module bị import làm thư viện ở nơi khác:

python

```python
# xu_ly_thanh_toan.py
def xu_ly_giao_dich(so_tien):
    """Hàm nghiệp vụ chính, dùng ở nhiều nơi khác"""
    return so_tien * 1.0

if __name__ == "__main__":
    # Code test tạm - CHỈ chạy khi bạn trực tiếp test file này
    # Nếu file khác import xu_ly_thanh_toan, đoạn test này sẽ KHÔNG chạy
    print("=== TEST ===")
    print(xu_ly_giao_dich(100000))
```

Nếu không có `if __name__ == "__main__":`, mọi file import module `xu_ly_thanh_toan` sẽ vô tình kích hoạt luôn cả đoạn code test — một lỗi thiết kế rất dở trong thực tế.

---

#### 4. Package — thư mục chứa nhiều module có tổ chức

Khi số module tăng lên, ta nhóm chúng vào **package** — về bản chất là một **thư mục** chứa nhiều file `.py`, cùng với file đặc biệt `__init__.py`.

**Cấu trúc thư mục thực tế của một dự án e-commerce nhỏ:**

```
cua_hang/
├── main.py
├── __init__.py
├── khach_hang/
│   ├── __init__.py
│   ├── xac_thuc.py
│   └── thanh_vien.py
├── don_hang/
│   ├── __init__.py
│   ├── xu_ly.py
│   └── thanh_toan.py
└── utils/
    ├── __init__.py
    └── dinh_dang.py
```

python

```python
# don_hang/xu_ly.py
def tao_don_hang(khach, san_pham):
    return {"khach": khach, "san_pham": san_pham}
```

python

```python
# main.py
from don_hang.xu_ly import tao_don_hang
from don_hang.thanh_toan import xu_ly_thanh_toan
from utils.dinh_dang import format_tien_vnd

don = tao_don_hang("An", ["Áo thun"])
print(format_tien_vnd(500000))
```

**Vai trò của `__init__.py`**: đây là file (thường để trống, hoặc chứa code khởi tạo) đánh dấu cho Python biết "thư mục này là một package, có thể import được". Từ Python 3.3+, package không có `__init__.py` vẫn hoạt động được (gọi là "namespace package"), nhưng thực tế chuyên nghiệp vẫn khuyến nghị giữ file này để rõ ràng và tương thích với công cụ cũ.

**`__init__.py` còn dùng để "làm phẳng" import**, giúp người dùng package không cần biết cấu trúc file bên trong:

python

```python
# don_hang/__init__.py
from .xu_ly import tao_don_hang
from .thanh_toan import xu_ly_thanh_toan

# Giờ ở main.py, có thể import gọn hơn:
# from don_hang import tao_don_hang, xu_ly_thanh_toan
# (thay vì phải viết from don_hang.xu_ly import ...)
```

---

#### 5. Thư viện chuẩn (Standard Library) — "pin đã lắp sẵn"

Python đi kèm hàng trăm module có sẵn, không cần cài thêm gì — chỉ cần `import`. Đây là những module bạn sẽ dùng **liên tục** trong công việc thực tế:

python

```python
import math
print(math.sqrt(16))        # 4.0 - căn bậc 2
print(math.ceil(4.3))       # 5 - làm tròn lên
print(math.floor(4.7))      # 4 - làm tròn xuống

import random
print(random.randint(1, 100))          # số nguyên ngẫu nhiên từ 1-100
print(random.choice(["A", "B", "C"]))  # chọn ngẫu nhiên 1 phần tử

import datetime
hom_nay = datetime.date.today()
print(hom_nay)                          # 2026-07-05

import os
print(os.getcwd())                       # thư mục làm việc hiện tại
print(os.environ.get("HOME"))            # biến môi trường hệ thống

import re    # regular expression - xử lý chuỗi nâng cao, học kỹ ở Bài 17
```

Ta sẽ đào sâu các module quan trọng nhất (`datetime`, `os`, `re`, `collections`) một cách toàn diện ở **Bài 17**.

---

#### 6. Cài thư viện bên thứ ba với `pip`

Thư viện chuẩn không có mọi thứ — cộng đồng Python đã xây dựng hàng triệu package công khai trên **PyPI (Python Package Index)**, cài bằng công cụ `pip` (đi kèm sẵn khi bạn cài Python ở Bài 1):

bash

```bash
# Cài 1 thư viện
pip install requests

# Cài phiên bản cụ thể
pip install requests==2.31.0

# Xem danh sách thư viện đã cài
pip list

# Xem thông tin chi tiết 1 thư viện
pip show requests

# Gỡ thư viện
pip uninstall requests

# Cập nhật thư viện lên bản mới nhất
pip install --upgrade requests
```

**Một số thư viện phổ biến nhất trong thực tế 2026 theo từng lĩnh vực:**

| Lĩnh vực | Thư viện tiêu biểu |
| --- | --- |
| Web API / HTTP | `requests`, `httpx` |
| Web Backend | `fastapi`, `django`, `flask` |
| Data Science | `pandas`, `numpy` |
| Trực quan hóa dữ liệu | `matplotlib`, `plotly` |
| Machine Learning | `scikit-learn`, `pytorch` |
| Xử lý Excel | `openpyxl` |
| Testing | `pytest` |

Sau khi cài, import và dùng như module thông thường:

python

```python
import requests

response = requests.get("https://api.example.com/don-hang/123")
print(response.json())   # tự động parse JSON response thành dict Python
```

(Ta sẽ đào sâu `requests` và làm việc với API thực sự ở **Bài 19**.)

---

#### 7. Môi trường ảo (Virtual Environment) — kiến thức quan trọng cần biết sớm

Vấn đề thực tế: nếu bạn cài thư viện trực tiếp vào máy (global), các dự án khác nhau có thể **xung đột phiên bản** — ví dụ dự án A cần `django==4.0`, dự án B cần `django==5.0`, nhưng máy chỉ cài được 1 phiên bản tại một thời điểm.

**Giải pháp**: mỗi dự án có một **môi trường ảo (virtual environment)** riêng biệt, cách ly hoàn toàn với nhau:

bash

```bash
# Tạo môi trường ảo tên "venv" trong thư mục dự án
python -m venv venv

# Kích hoạt môi trường ảo
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Sau khi activate, terminal hiển thị (venv) ở đầu dòng
# Giờ pip install chỉ ảnh hưởng môi trường ảo này, không ảnh hưởng máy tổng
pip install requests

# Thoát môi trường ảo
deactivate
```

Đây là **quy trình bắt buộc** trong mọi công việc phát triển Python chuyên nghiệp — không một dev thực thụ nào cài thư viện trực tiếp vào Python hệ thống cho dự án thực tế. Ta sẽ đào sâu chủ đề này (kèm file `requirements.txt` để chia sẻ danh sách thư viện với đồng nghiệp) ở **Bài 18**.

---

#### 8. Ví dụ thực chiến tổng hợp — Tổ chức lại project tính lương (từ Bài 9)

**Cấu trúc file:**

```
quan_ly_luong/
├── main.py
├── thue/
│   ├── __init__.py
│   └── tinh_thue.py
└── utils/
    ├── __init__.py
    └── dinh_dang.py
```

python

```python
# thue/tinh_thue.py
def tinh_thue_tncn(thu_nhap: float) -> float:
    if thu_nhap <= 5_000_000:
        return 0
    elif thu_nhap <= 10_000_000:
        return (thu_nhap - 5_000_000) * 0.05
    else:
        return (10_000_000 - 5_000_000) * 0.05 + (thu_nhap - 10_000_000) * 0.1
```

python

```python
# utils/dinh_dang.py
def format_tien_vnd(so_tien: float) -> str:
    return f"{so_tien:,.0f} VNĐ"
```

python

```python
# main.py
from thue.tinh_thue import tinh_thue_tncn
from utils.dinh_dang import format_tien_vnd

luong = 12_000_000
thue = tinh_thue_tncn(luong)
luong_thuc_nhan = luong - thue

print(f"Lương gross: {format_tien_vnd(luong)}")
print(f"Thuế TNCN: {format_tien_vnd(thue)}")
print(f"Lương thực nhận: {format_tien_vnd(luong_thuc_nhan)}")

if __name__ == "__main__":
    print("\n=== Chạy chương trình chính ===")
```

Đây chính là cách một dự án Python thực tế được tổ chức — mỗi module chỉ chịu trách nhiệm **một mảng nghiệp vụ cụ thể** (thuế, định dạng...), giúp code dễ maintain, dễ test riêng từng phần, và nhiều người có thể làm việc song song trên các module khác nhau mà không xung đột.

---

#### 🎯 Bài tập thực hành

Tổ chức lại bài tập Bài 11 (xử lý CSV khách hàng) thành cấu trúc package:

```
xu_ly_khach_hang/
├── main.py
├── doc_du_lieu/
│   ├── __init__.py
│   └── csv_reader.py
├── phan_tich/
│   ├── __init__.py
│   └── loc_vip.py
└── xuat_du_lieu/
    ├── __init__.py
    └── json_writer.py
```

Yêu cầu:

1. `doc_du_lieu/csv_reader.py`: viết hàm `doc_khach_hang_csv(duong_dan)` (copy logic từ bài 11)
2. `phan_tich/loc_vip.py`: viết hàm `loc_khach_vip(danh_sach, nguong=5_000_000)`
3. `xuat_du_lieu/json_writer.py`: viết hàm `xuat_json(du_lieu, duong_dan)`
4. `main.py`: import 3 hàm trên từ 3 module, chạy toàn bộ luồng xử lý (đọc → lọc → xuất)
5. Thêm `if __name__ == "__main__":` phù hợp vào từng module con để mỗi module có thể tự test độc lập (ví dụ `csv_reader.py` khi chạy trực tiếp sẽ tự đọc và in ra 1 file mẫu để kiểm tra)
6. Thử thách thêm: tạo virtual environment cho project này, cài thử thư viện `requests` vào trong đó, chạy `pip list` để xác nhận nó chỉ nằm trong venv (không ảnh hưởng cài đặt Python toàn hệ thống)

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 13: Lập trình hướng đối tượng (OOP) — nền tảng** — đây là bước chuyển đổi tư duy lớn nhất trong toàn bộ khóa học, dạy bạn cách mô hình hóa dữ liệu và hành vi thành `class` và `object`, nền tảng của hầu hết framework và thư viện lớn trong Python hiện đại.
