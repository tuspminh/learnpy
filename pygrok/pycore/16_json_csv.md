**Bài 16: Làm việc với JSON & CSV**

Đây là bài thực chiến rất quan trọng. Hầu hết dữ liệu trong thực tế đều ở dạng **CSV** hoặc **JSON**. Nắm vững bài này bạn sẽ đọc/ghi được dữ liệu từ file, API, Excel… một cách chuyên nghiệp.

---

### 1. Làm việc với CSV

CSV (Comma-Separated Values) là file văn bản, mỗi dòng là một bản ghi, các trường cách nhau bởi dấu phẩy (hoặc dấu khác).

#### 1.1. Đọc file CSV

**Cách 1: Dùng `csv.reader`**
```python
import csv

with open("diem.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)  # đọc dòng tiêu đề
    print("Tiêu đề:", header)

    for row in reader:
        print(row)  # mỗi row là list
```

**Cách 2: Dùng `csv.DictReader` (Khuyến nghị)**
```python
import csv

with open("diem.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["Họ tên"], row["Điểm"])  # truy cập theo tên cột
```

#### 1.2. Ghi file CSV

```python
import csv

header = ["Họ tên", "Điểm", "Lớp"]
data = [["An", 8.5, "CNTT1"], ["Bình", 7.0, "CNTT1"], ["Chi", 9.2, "CNTT2"]]

with open("diem_moi.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)  # ghi tiêu đề
    writer.writerows(data)  # ghi nhiều dòng
```

**Ghi bằng DictWriter (rất tiện):**
```python
import csv

data = [
    {"Họ tên": "An", "Điểm": 8.5, "Lớp": "CNTT1"},
    {"Họ tên": "Bình", "Điểm": 7.0, "Lớp": "CNTT1"},
]

with open("diem_dict.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["Họ tên", "Điểm", "Lớp"])
    writer.writeheader()
    writer.writerows(data)
```

> **Lưu ý quan trọng:** Luôn dùng `newline=""` khi ghi CSV trên Windows để tránh bị dòng trống.

---

### 2. Làm việc với JSON

JSON (JavaScript Object Notation) là định dạng dữ liệu phổ biến nhất hiện nay (API, config, lưu trữ…).

#### 2.1. Chuyển đổi giữa JSON và Python

| Python          | JSON          |
|-----------------|---------------|
| dict            | object        |
| list / tuple    | array         |
| str             | string        |
| int / float     | number        |
| True / False    | true / false  |
| None            | null          |

```python
import json

# Python → JSON string
data = {"ten": "An", "tuoi": 20, "diem": [8.5, 7.0, 9.0], "da_tot_nghiep": False}

json_string = json.dumps(data, ensure_ascii=False, indent=4)
print(json_string)

# JSON string → Python
data2 = json.loads(json_string)
print(data2["ten"])
```

#### 2.2. Đọc / Ghi file JSON

```python
import json

# Ghi file
data = {"hoc_sinh": [{"ten": "An", "diem": 8.5}, {"ten": "Bình", "diem": 7.0}]}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

# Đọc file
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(data["hoc_sinh"][0]["ten"])  # An
```

**Giải thích tham số quan trọng:**
- `ensure_ascii=False`: Giữ nguyên tiếng Việt (không bị thành `\u00e1…`)
- `indent=4`: Format đẹp, dễ đọc

---

### 3. Ví dụ thực tế kết hợp

**Đọc CSV → xử lý → lưu thành JSON**

```python
import csv
import json

hoc_sinh = []

with open("diem.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        hoc_sinh.append(
            {"ten": row["Họ tên"], "diem": float(row["Điểm"]), "lop": row["Lớp"]}
        )

# Tính điểm trung bình
tong = sum(hs["diem"] for hs in hoc_sinh)
trung_binh = tong / len(hoc_sinh)

ket_qua = {
    "danh_sach": hoc_sinh,
    "diem_trung_binh": round(trung_binh, 2),
    "so_luong": len(hoc_sinh),
}

with open("ket_qua.json", "w", encoding="utf-8") as f:
    json.dump(ket_qua, f, ensure_ascii=False, indent=4)

print("Đã lưu kết quả vào ket_qua.json")
```

---

### 4. Xử lý lỗi thường gặp

```python
import json

try:
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    print("Không tìm thấy file")
except json.JSONDecodeError:
    print("File JSON bị lỗi định dạng")
```

---

### 5. Tóm tắt nhanh

| Công việc              | CSV                          | JSON                          |
|------------------------|------------------------------|-------------------------------|
| Đọc file               | `csv.DictReader`             | `json.load()`                 |
| Ghi file               | `csv.DictWriter`             | `json.dump()`                 |
| Chuyển từ chuỗi        | —                            | `json.loads()`                |
| Chuyển thành chuỗi     | —                            | `json.dumps()`                |
| Phù hợp với            | Dữ liệu dạng bảng            | Dữ liệu lồng nhau, API        |

---

### Bài tập Bài 16

**Bài 1:**  
Tạo file `sinhvien.csv` với nội dung:
```
MaSV,HoTen,Diem
SV01,Nguyễn Văn An,8.5
SV02,Trần Thị Bình,7.0
SV03,Lê Văn Chi,9.2
```
Viết chương trình đọc file và in ra danh sách sinh viên có điểm ≥ 8.0.

**Bài 2:**  
Viết chương trình nhập thông tin nhiều sinh viên (mã, tên, điểm), lưu vào file `sinhvien.csv`.

**Bài 3:**  
Đọc file `sinhvien.csv` ở trên, chuyển thành dạng list of dict, rồi lưu ra file `sinhvien.json` (format đẹp).

**Bài 4:**  
Viết chương trình đọc file `sinhvien.json`, tính điểm trung bình và tìm sinh viên có điểm cao nhất.

**Bài 5 (nâng cao):**  
Viết chương trình quản lý danh bạ:
- Lưu danh bạ dưới dạng JSON (`danh_ba.json`)
- Có menu: Thêm – Xóa – Tìm kiếm – Hiển thị – Lưu file
- Mỗi lần thay đổi phải cập nhật lại file JSON

---

Làm xong gửi code + kết quả chạy.  
Tôi sẽ chữa bài và mở **Bài 17: Làm việc với thư viện bên ngoài & Virtual Environment** (pip, venv, requests…).

CSV và JSON là kỹ năng “cơm canh” của lập trình viên. Cứ làm kỹ nhé!