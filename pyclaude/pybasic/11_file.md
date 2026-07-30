Vai trò này tôi đã ghi nhớ và đang duy trì xuyên suốt từ đầu hành trình — sẽ tiếp tục áp dụng nghiêm túc. Giờ chính thức bước vào **Giai đoạn 2 — Trung cấp**.

### 📘 Bài 11: Làm việc với File

Đến giờ mọi dữ liệu bạn xử lý chỉ "sống" trong bộ nhớ RAM — khi chương trình kết thúc, dữ liệu biến mất. File I/O (Input/Output) là cách chương trình **lưu trữ dữ liệu bền vững (persistent)** và **giao tiếp với thế giới bên ngoài** — đọc log server, xử lý file Excel khách hàng gửi, xuất báo cáo PDF, ghi cấu hình hệ thống.

---

#### 1. Mở file với `open()` — và vì sao cần `with`

python

```python
# Cách CŨ - không khuyến nghị
file = open("don_hang.txt", "r")
noi_dung = file.read()
file.close()   # ⚠️ PHẢI nhớ đóng file - nếu quên, hoặc nếu có lỗi xảy ra TRƯỚC dòng close() này
                # thì file sẽ không được đóng -> rò rỉ tài nguyên (resource leak)
```

Nhớ lại bài 10 — ta đã dùng `finally` để đảm bảo file luôn đóng. Nhưng có cách gọn gàng hơn, chuẩn Pythonic tuyệt đối:

python

```python
# ✅ Cách CHUẨN - dùng context manager "with"
with open("don_hang.txt", "r") as file:
    noi_dung = file.read()
    print(noi_dung)
# Ra khỏi khối with, file TỰ ĐỘNG đóng - dù có lỗi xảy ra bên trong hay không
```

**Tại sao `with` tốt hơn?** `with` sử dụng một cơ chế gọi là **context manager** — nó tự động gọi `file.close()` ngay khi khối lệnh kết thúc, **kể cả khi có exception xảy ra bên trong**, tương đương với việc tự động có `finally` ẩn bên trong. Đây là mẫu thiết kế cực kỳ quan trọng trong Python, không chỉ dùng cho file mà còn cho kết nối database, kết nối mạng, lock đa luồng...

---

#### 2. Các chế độ mở file (mode)

python

```python
open("file.txt", "r")    # Read - đọc (mặc định), lỗi nếu file không tồn tại
open("file.txt", "w")    # Write - ghi, XÓA TOÀN BỘ nội dung cũ nếu file đã tồn tại!
open("file.txt", "a")    # Append - ghi thêm vào CUỐI file, không xóa nội dung cũ
open("file.txt", "x")    # Exclusive create - tạo mới, lỗi nếu file đã tồn tại
open("file.txt", "r+")   # Đọc VÀ ghi

open("data.bin", "rb")   # đọc dạng NHỊ PHÂN (binary) - dùng cho ảnh, PDF, file không phải text
open("data.bin", "wb")   # ghi dạng nhị phân
```

**⚠️ Cạm bẫy nghiêm trọng nhất với người mới**: mở file bằng mode `"w"` khi *chỉ muốn đọc* — sẽ **xóa sạch toàn bộ nội dung file** ngay khi mở, dù bạn chưa viết gì cả! Đây là lỗi có thể gây mất dữ liệu thật trong công việc thực tế, luôn kiểm tra kỹ mode trước khi chạy code.

---

#### 3. Đọc file — 3 phương thức chính

python

```python
# read() - đọc TOÀN BỘ nội dung thành 1 chuỗi
with open("don_hang.txt", "r", encoding="utf-8") as f:
    noi_dung = f.read()
    print(noi_dung)

# readline() - đọc TỪNG DÒNG một, hữu ích khi file quá lớn không nên load hết vào RAM
with open("don_hang.txt", "r", encoding="utf-8") as f:
    dong_dau = f.readline()
    dong_hai = f.readline()

# readlines() - đọc TẤT CẢ dòng, trả về LIST các dòng
with open("don_hang.txt", "r", encoding="utf-8") as f:
    tat_ca_dong = f.readlines()
    print(tat_ca_dong)   # ['Dòng 1\n', 'Dòng 2\n', ...]

# Cách PHỔ BIẾN NHẤT trong thực tế - lặp trực tiếp qua file (tiết kiệm RAM tối đa)
with open("don_hang.txt", "r", encoding="utf-8") as f:
    for dong in f:
        print(dong.strip())   # .strip() để xóa ký tự xuống dòng \n thừa
```

**⚠️ Lưu ý bắt buộc phải nhớ: luôn chỉ định `encoding="utf-8"`** khi làm việc với dữ liệu tiếng Việt (hoặc bất kỳ ngôn ngữ có dấu). Nếu không chỉ định, Python dùng encoding mặc định của hệ điều hành (thường khác nhau giữa Windows/macOS/Linux), dẫn đến lỗi hiển thị ký tự lỗi (mojibake) hoặc crash với `UnicodeDecodeError` khi chạy trên máy khác:

python

```python
# ❌ Rủi ro - có thể lỗi khi chạy trên máy khác hệ điều hành khác
with open("bao_cao.txt", "r") as f:
    ...

# ✅ An toàn - luôn tường minh encoding
with open("bao_cao.txt", "r", encoding="utf-8") as f:
    ...
```

**Tại sao lặp trực tiếp qua file (`for dong in f`) được khuyến nghị nhất?** Vì Python đọc file theo cơ chế **lazy** — chỉ đọc từng dòng khi cần, không load toàn bộ file vào RAM cùng lúc. Với file log server nặng vài GB, `read()` hoặc `readlines()` có thể làm crash chương trình do hết RAM, còn cách lặp trực tiếp xử lý được file có kích thước bất kỳ.

---

#### 4. Ghi file

python

```python
# Ghi mới (xóa nội dung cũ)
with open("bao_cao.txt", "w", encoding="utf-8") as f:
    f.write("Báo cáo doanh thu tháng 7/2026\n")
    f.write("Tổng đơn hàng: 1,245\n")

# Ghi nhiều dòng cùng lúc bằng writelines()
danh_sach_dong = ["Dòng 1\n", "Dòng 2\n", "Dòng 3\n"]
with open("bao_cao.txt", "w", encoding="utf-8") as f:
    f.writelines(danh_sach_dong)

# Ghi thêm (append) - dùng cho log, không mất dữ liệu cũ
with open("log_he_thong.txt", "a", encoding="utf-8") as f:
    f.write("2026-07-05 10:30:00 - Người dùng đăng nhập thành công\n")
```

**Ứng dụng thực tế** — hệ thống ghi log (log hoạt động, sự kiện, lỗi) trong ứng dụng thực tế luôn dùng mode `"a"` (append), vì mỗi lần chạy chương trình không nên xóa lịch sử log cũ:

python

```python
from datetime import datetime

def ghi_log(thong_bao: str, muc_do: str = "INFO"):
    thoi_gian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("app.log", "a", encoding="utf-8") as f:
        f.write(f"[{thoi_gian}] [{muc_do}] {thong_bao}\n")

ghi_log("Đơn hàng DH2026-891 đã được tạo")
ghi_log("Kết nối database thất bại", muc_do="ERROR")
```

---

#### 5. Xử lý lỗi khi làm việc với file — kết hợp Bài 10

python

```python
def doc_cau_hinh(duong_dan: str) -> str | None:
    try:
        with open(duong_dan, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Không tìm thấy file: {duong_dan}")
        return None
    except PermissionError:
        print(f"Không có quyền đọc file: {duong_dan}")
        return None
    except UnicodeDecodeError:
        print(f"File {duong_dan} không đúng định dạng UTF-8")
        return None
```

Trong thực tế production, code xử lý file **luôn phải** bọc `try/except` — vì bạn không thể kiểm soát được liệu file có tồn tại, có quyền đọc, hay có đúng định dạng mã hóa khi chương trình thực sự chạy trên máy chủ khác với máy bạn code.

---

#### 6. Làm việc với CSV — định dạng dữ liệu phổ biến nhất trong doanh nghiệp

CSV (Comma-Separated Values) là định dạng dữ liệu dạng bảng phổ biến nhất khi trao đổi dữ liệu giữa Excel, database, và hệ thống khác. Dùng module `csv` có sẵn thay vì tự viết `split(",")` — vì CSV thực tế phức tạp hơn tưởng (dấu phẩy trong chuỗi có dấu ngoặc kép, xuống dòng trong ô dữ liệu...).

python

```python
import csv

# ĐỌC file CSV
with open("don_hang.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)   # lấy dòng đầu (tên cột), con trỏ tự chuyển sang dòng kế
    print(f"Các cột: {header}")
    for dong in reader:
        print(dong)    # mỗi dòng là 1 list, ví dụ: ['DH001', 'An', '250000']

# ĐỌC file CSV dạng dict - THỰC TẾ hơn, truy cập theo TÊN CỘT thay vì index
with open("don_hang.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for dong in reader:
        print(f"{dong['ten_khach']}: {dong['gia_tri']} VNĐ")   # truy cập rõ nghĩa, không cần nhớ index
```

python

```python
# GHI file CSV
du_lieu = [
    ["ma_don", "ten_khach", "gia_tri"],
    ["DH001", "An", 250000],
    ["DH002", "Bình", 480000],
]

with open("xuat_don_hang.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(du_lieu)

# Ghi CSV từ list of dict - phổ biến hơn trong thực tế xử lý dữ liệu
du_lieu_dict = [
    {"ma_don": "DH001", "ten_khach": "An", "gia_tri": 250000},
    {"ma_don": "DH002", "ten_khach": "Bình", "gia_tri": 480000},
]

with open("xuat_don_hang2.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["ma_don", "ten_khach", "gia_tri"])
    writer.writeheader()
    writer.writerows(du_lieu_dict)
```

**Lưu ý kỹ thuật quan trọng**: tham số `newline=""` khi ghi CSV trên Windows là **bắt buộc** — nếu thiếu, file sẽ bị dòng trống thừa giữa mỗi dòng dữ liệu do xung đột cách xử lý ký tự xuống dòng giữa Python và hệ điều hành.

---

#### 7. Làm việc với JSON — định dạng "ngôn ngữ chung" của API hiện đại

Nhớ lại Bài 8 — dict lồng nhau chính là hình dạng của JSON. Module `json` giúp chuyển đổi qua lại giữa dict/list Python và chuỗi JSON:

python

```python
import json

# Python dict -> chuỗi JSON (serialize)
don_hang = {
    "ma_don": "DH2026-891",
    "khach_hang": {"ten": "Lan", "email": "lan@gmail.com"},
    "san_pham": ["Áo thun", "Quần jean"],
    "tong_tien": 600000
}

chuoi_json = json.dumps(don_hang, ensure_ascii=False, indent=2)
print(chuoi_json)
```

**Kết quả:**

json

```json
{
  "ma_don": "DH2026-891",
  "khach_hang": {
    "ten": "Lan",
    "email": "lan@gmail.com"
  },
  "san_pham": ["Áo thun", "Quần jean"],
  "tong_tien": 600000
}
```

**Lưu ý 2 tham số quan trọng:**

- `ensure_ascii=False` — **bắt buộc** khi có tiếng Việt, nếu không chữ có dấu sẽ bị mã hóa thành `\u1234` khó đọc
- `indent=2` — định dạng đẹp, dễ đọc (không có thì JSON in ra một dòng dài)

python

```python
# Chuỗi JSON -> Python dict (deserialize) - ngược lại
chuoi_nhan_duoc = '{"ten": "An", "tuoi": 25, "la_vip": true}'
du_lieu = json.loads(chuoi_nhan_duoc)
print(du_lieu["ten"])       # 'An'
print(type(du_lieu))         # <class 'dict'>

# Đọc trực tiếp TỪ FILE JSON
with open("cau_hinh.json", "r", encoding="utf-8") as f:
    cau_hinh = json.load(f)     # load (không phải loads) - đọc trực tiếp từ file object

# Ghi trực tiếp VÀO FILE JSON
with open("xuat_don_hang.json", "w", encoding="utf-8") as f:
    json.dump(don_hang, f, ensure_ascii=False, indent=2)   # dump (không phải dumps)
```

**Phân biệt quan trọng — dễ gây nhầm lẫn:**

| Hàm | Làm việc với | Chuyển đổi |
| --- | --- | --- |
| `json.dumps()` | chuỗi string | dict → string |
| `json.loads()` | chuỗi string | string → dict |
| `json.dump()` | file object | dict → ghi vào file |
| `json.load()` | file object | đọc từ file → dict |

Quy tắc nhớ: có chữ **"s"** (dumps/loads) = làm việc với **s**tring; không có "s" (dump/load) = làm việc trực tiếp với file.

**Đây chính là kỹ năng nền tảng trước khi học Bài 19 — Làm việc với API**, vì hầu hết API hiện đại trả về response dạng JSON, và bạn sẽ dùng `json.loads()` (hoặc thư viện `requests` tự động parse) liên tục.

---

#### 8. Kiểm tra file tồn tại và thao tác với đường dẫn — module `os` và `pathlib`

python

```python
import os
from pathlib import Path

# Cách cũ - module os
print(os.path.exists("don_hang.txt"))       # True/False
print(os.path.getsize("don_hang.txt"))       # kích thước file (bytes)
os.makedirs("bao_cao/2026", exist_ok=True)   # tạo thư mục lồng, không lỗi nếu đã tồn tại

# Cách HIỆN ĐẠI và được khuyến nghị hơn - pathlib (Python 3.4+, chuẩn 2026)
duong_dan = Path("bao_cao/2026/thang_7.txt")
print(duong_dan.exists())        # kiểm tra tồn tại
print(duong_dan.parent)           # 'bao_cao/2026' - thư mục cha
print(duong_dan.suffix)           # '.txt' - đuôi file
print(duong_dan.stem)             # 'thang_7' - tên file không có đuôi

duong_dan.parent.mkdir(parents=True, exist_ok=True)   # tạo thư mục nếu chưa có
duong_dan.write_text("Nội dung báo cáo", encoding="utf-8")   # ghi file cực gọn
noi_dung = duong_dan.read_text(encoding="utf-8")               # đọc file cực gọn
```

`pathlib` được xem là cách viết chuẩn hiện đại vì cú pháp gọn hơn, hoạt động nhất quán trên mọi hệ điều hành (Windows dùng `\`, macOS/Linux dùng `/` — `pathlib` tự xử lý sự khác biệt này cho bạn).

---

#### 9. Ví dụ thực chiến tổng hợp — Hệ thống xử lý & xuất báo cáo đơn hàng

python

```python
import csv
import json
from pathlib import Path
from datetime import datetime

def doc_don_hang_csv(duong_dan: str) -> list[dict]:
    """Đọc file CSV đơn hàng, trả về list of dict. Trả về [] nếu lỗi."""
    try:
        with open(duong_dan, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        print(f"Không tìm thấy file: {duong_dan}")
        return []


def tao_bao_cao_json(don_hang: list[dict], duong_dan_xuat: str):
    """Tính tổng doanh thu và xuất báo cáo dạng JSON."""
    tong_doanh_thu = sum(float(dh["gia_tri"]) for dh in don_hang)

    bao_cao = {
        "ngay_tao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "so_don_hang": len(don_hang),
        "tong_doanh_thu": tong_doanh_thu,
        "chi_tiet": don_hang
    }

    Path(duong_dan_xuat).write_text(
        json.dumps(bao_cao, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"Đã xuất báo cáo: {duong_dan_xuat}")


# Sử dụng
don_hang = doc_don_hang_csv("don_hang.csv")
if don_hang:
    tao_bao_cao_json(don_hang, "bao_cao_2026_07.json")
```

---

#### 🎯 Bài tập thực hành

**Bước 1** — Tạo file `khach_hang.csv` với nội dung sau (tự tạo file này bằng notepad/VS Code):

csv

```csv
ten,email,tong_chi_tieu,hang_thanh_vien
Nguyễn An,an@gmail.com,5200000,Vàng
Trần Bình,binh@gmail.com,1800000,Bạc
Lê Chi,chi@gmail.com,8900000,Kim Cương
```

**Bước 2** — Viết file `bai_tap_11.py` với các yêu cầu:

1. Dùng `csv.DictReader` đọc file trên thành list of dict
2. Lọc ra khách hàng có `tong_chi_tieu` >= 5,000,000 (nhớ ép kiểu vì CSV luôn đọc ra string!)
3. Ghi danh sách khách VIP đó ra file mới `khach_vip.json` (định dạng JSON, `ensure_ascii=False`, `indent=2`)
4. Ghi một file log `xu_ly.log` (mode "a") ghi lại: thời gian xử lý + số lượng khách VIP tìm được
5. Bọc toàn bộ logic đọc file trong `try/except FileNotFoundError` để chương trình không crash nếu người dùng lỡ xóa file CSV
6. Thử thách thêm: dùng `pathlib.Path` để kiểm tra file `khach_vip.json` đã được tạo thành công chưa, in ra kích thước file (bytes) nếu có

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 12: Module & Package** — cách tổ chức code Python thành nhiều file có cấu trúc rõ ràng, tái sử dụng được giữa các project, và cách cài đặt thư viện bên thứ ba bằng `pip` — kỹ năng cần thiết trước khi bước vào OOP ở Bài 13.
