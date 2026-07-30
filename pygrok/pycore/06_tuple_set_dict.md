**Bài 6: Tuple – Set – Dictionary**

Đây là 3 cấu trúc dữ liệu quan trọng còn lại của Python. Sau bài này bạn sẽ nắm gần như toàn bộ cách lưu trữ dữ liệu cơ bản.

* * *

### 1\. Tuple (Bộ giá trị bất biến)

Tuple giống List nhưng **không thể thay đổi** sau khi tạo (immutable).

Python
    
    
    # Tạo tuple
    t1 = (1, 2, 3)
    t2 = ("An", "Bình", "Chi")
    t3 = 10, 20, 30          # không cần dấu ngoặc cũng được
    t4 = (5,)                # tuple 1 phần tử phải có dấu phẩy
    
    print(type(t1))          # <class 'tuple'>

**Truy cập giống List:**

Python
    
    
    t = (10, 20, 30, 40, 50)
    print(t[0])       # 10
    print(t[-1])      # 50
    print(t[1:4])     # (20, 30, 40)

**Đặc điểm quan trọng:**

  * Không thể gán lại phần tử: t[0] = 99 → **lỗi**
  * Không có append, remove, pop…
  * Chỉ có 2 phương thức chính: count() và index()



Python
    
    
    t = (1, 2, 2, 3, 2)
    print(t.count(2))     # 3
    print(t.index(3))     # 3

**Khi nào dùng Tuple?**

  * Dữ liệu không được phép thay đổi (tọa độ, thông tin cố định…)
  * Làm khóa của Dictionary
  * Trả về nhiều giá trị từ hàm



**Unpacking (rất hay dùng):**

Python
    
    
    point = (3, 5)
    x, y = point
    print(x, y)           # 3 5
    
    a, b, *rest = (1, 2, 3, 4, 5)
    print(a, b, rest)     # 1 2 [3, 4, 5]

* * *

### 2\. Set (Tập hợp)

Set là tập hợp **không có thứ tự** , **không trùng lặp**.

Python
    
    
    s1 = {1, 2, 3, 4}
    s2 = {3, 4, 5, 6}
    s3 = set([1, 2, 2, 3, 3])   # {1, 2, 3}  → tự động loại trùng
    
    print(type(s1))

**Thêm & Xóa:**

Python
    
    
    s = {1, 2, 3}
    s.add(4)
    s.add(2)              # không có tác dụng vì đã có 2
    s.remove(3)           # xóa 3 (nếu không có sẽ lỗi)
    s.discard(10)         # xóa an toàn (không lỗi nếu không có)
    s.clear()

**Các phép toán tập hợp (rất mạnh):**

Python
    
    
    a = {1, 2, 3, 4}
    b = {3, 4, 5, 6}
    
    print(a | b)          # hợp: {1, 2, 3, 4, 5, 6}
    print(a & b)          # giao: {3, 4}
    print(a - b)          # hiệu: {1, 2}
    print(a ^ b)          # đối xứng: {1, 2, 5, 6}

**Ứng dụng thực tế:**

Python
    
    
    # Loại bỏ phần tử trùng trong list
    ds = [1, 2, 2, 3, 4, 4, 5]
    ds_khong_trung = list(set(ds))
    print(ds_khong_trung)

* * *

### 3\. Dictionary (Từ điển)

Dictionary lưu dữ liệu dạng **key – value**. Đây là cấu trúc dùng rất nhiều trong thực tế.

Python
    
    
    # Tạo dictionary
    sinh_vien = {
        "ten": "Nguyễn Văn A",
        "tuoi": 20,
        "diem": 8.5,
        "da_tot_nghiep": False
    }

**Truy cập giá trị:**

Python
    
    
    print(sinh_vien["ten"])           # Nguyễn Văn A
    print(sinh_vien.get("tuoi"))      # 20
    print(sinh_vien.get("lop", "Chưa có"))  # trả về mặc định nếu không có key

**Thêm / Sửa / Xóa:**

Python
    
    
    sinh_vien["lop"] = "CNTT01"       # thêm mới
    sinh_vien["diem"] = 9.0           # sửa
    del sinh_vien["da_tot_nghiep"]    # xóa
    sinh_vien.pop("tuoi")             # xóa và trả về giá trị

**Các phương thức quan trọng:**

Python
    
    
    print(sinh_vien.keys())       # tất cả key
    print(sinh_vien.values())     # tất cả value
    print(sinh_vien.items())      # cặp (key, value)
    
    # Duyệt dictionary
    for key in sinh_vien:
        print(key, ":", sinh_vien[key])
    
    for key, value in sinh_vien.items():
        print(key, "→", value)

**Dictionary lồng nhau (rất phổ biến):**

Python
    
    
    hoc_sinh = {
        "SV001": {"ten": "An", "diem": 8.5},
        "SV002": {"ten": "Bình", "diem": 7.0},
        "SV003": {"ten": "Chi", "diem": 9.2}
    }
    
    print(hoc_sinh["SV001"]["ten"])     # An
    print(hoc_sinh["SV003"]["diem"])    # 9.2

* * *

### So sánh nhanh 4 cấu trúc

Đặc điểm| List| Tuple| Set| Dictionary  
---|---|---|---|---  
Có thứ tự| Có| Có| Không| Có (từ 3.7+)  
Trùng lặp| Cho phép| Cho phép| Không| Key không trùng  
Thay đổi được| Có| Không| Có| Có  
Truy cập bằng| Index| Index| —| Key  
Ký hiệu| []| ()| {}| {key: value}  
  
* * *

### Bài tập Bài 6

**Bài 1: Tuple** Cho tuple: thong_tin = ("An", 20, 8.5, "CNTT")

  * In từng phần tử
  * Unpacking thành các biến ten, tuoi, diem, nganh
  * Thử thay đổi phần tử đầu tiên và quan sát lỗi



**Bài 2: Set** Cho 2 list: a = [1, 2, 3, 4, 5, 2, 3] b = [4, 5, 6, 7, 8, 4]

  * Tạo 2 set từ 2 list trên
  * In ra phần tử chung
  * In ra phần tử chỉ có ở a
  * In ra tất cả phần tử không trùng lặp của cả 2



**Bài 3: Dictionary** Tạo dictionary lưu thông tin 3 học sinh (mã SV làm key). Mỗi học sinh có: tên, tuổi, điểm.

Yêu cầu:

  1. In toàn bộ thông tin
  2. Thêm 1 học sinh mới
  3. Cập nhật điểm của 1 học sinh
  4. Xóa 1 học sinh
  5. Tính điểm trung bình của cả lớp



**Bài 4 (nâng cao):** Viết chương trình quản lý danh bạ đơn giản:

  * Dùng dictionary: key là tên, value là số điện thoại
  * Cho phép: thêm, xóa, tìm kiếm, hiển thị toàn bộ danh bạ
  * Dùng vòng lặp while để tạo menu



* * *

Làm xong gửi code + kết quả chạy. Tôi sẽ chữa bài và mở **Bài 7: Hàm (Function)** – một trong những bài quan trọng nhất.

Nắm vững 4 cấu trúc dữ liệu (List – Tuple – Set – Dict) là bạn đã có nền tảng rất vững. Cứ làm kỹ nhé!

