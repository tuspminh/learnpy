LEVEL 2 - BÀI 5: 4 Cấu trúc dữ liệu - List, Tuple, Set, Dict
1. LIST - Danh sách, thay đổi được, có thứ tự

Dùng nhiều nhất. Như một dãy hộp.
Python

# Khai báo
trai_cay = ["táo", "ổi", "xoài"]
# Truy cập: index bắt đầu từ 0
print(trai_cay[0]) # táo
print(trai_cay[-1]) # xoài - index âm là từ cuối

# Cắt lát (slicing) - cực mạnh
print(trai_cay[0:2]) # ["táo", "ổi"]
print(trai_cay[::-1]) # đảo ngược list

# Thêm / Xóa / Sửa
trai_cay.append("dưa") # thêm cuối
trai_cay.insert(1, "cam") # chèn vào vị trí 1
trai_cay[0] = "táo mỹ"
trai_cay.remove("ổi") # xóa theo giá trị
popped = trai_cay.pop() # xóa cuối và trả về

# Duyệt
for qua in trai_cay:
    print(qua)

# Độ dài
len(trai_cay)

2. TUPLE - List nhưng bất biến (không sửa được)

Dùng khi bạn muốn dữ liệu an toàn, không ai sửa được.
Python

toa_do = (10, 20) # tọa độ
# toa_do[0] = 15 -> LỖI
# Nhanh hơn List, dùng làm key cho Dict được

# Unpacking như bài a,b = b,a
x, y = toa_do

3. SET - Tập hợp, không trùng lặp, không thứ tự

Dùng để lọc trùng và kiểm tra tồn tại siêu nhanh.
Python

so = [1,2,2,3,3,3,4]
so_unique = set(so) # {1,2,3,4}
print(5 in so_unique) # False - kiểm tra O(1) cực nhanh

# Toán tử tập hợp
a = {1,2,3}
b = {3,4,5}
print(a & b) # giao {3}
print(a | b) # hợp {1,2,3,4,5}
print(a - b) # hiệu {1,2}

4. DICT - Từ điển, Key -> Value

Đây là cấu trúc quan trọng nhất khi đi làm, mọi API, JSON đều là Dict.
Python

# Khai báo
sinh_vien = {
    "ten": "Hùng",
    "tuoi": 25,
    "mon_hoc": ["Python", "SQL"]
}

# Truy cập
print(sinh_vien["ten"]) # Hùng
print(sinh_vien.get("diem", 0)) # dùng.get() an toàn hơn, không có thì trả về default

# Thêm / Sửa
sinh_vien["tuoi"] = 26
sinh_vien["truong"] = "HUST"

# Duyệt - 3 cách
for key in sinh_vien: # duyệt key
    print(key)

for key, value in sinh_vien.items(): # duyệt cả 2 - DÙNG NHIỀU NHẤT
    print(f"{key}: {value}")

for value in sinh_vien.values():
    print(value)

5. Vũ khí bí mật: List Comprehension

Viết 1 dòng bằng 4 dòng for.
Python

# Cách thường
binh_phuong = []
for i in range(5):
    binh_phuong.append(i**2)

# Cách Pro
binh_phuong = [i**2 for i in range(5)] # [0,1,4,9,16]

# Có cả điều kiện
so_chan = [i for i in range(10) if i % 2 == 0] # [0,2,4,6,8]

BÀI TẬP BÀI 5

Bài 5.1 (Bắt buộc): Thống kê từ
Nhập 1 câu: "hoc python rat vui"
In ra Dict đếm số lần mỗi từ xuất hiện: {'hoc':1, 'python':2, 'rat':1, 'vui':1}
Gợi ý: cau.split() để tách thành list từ.

Bài 5.2 (Bắt buộc): Quản lý kho
Cho list sản phẩm:
Python

kho = [
    {"ten": "Laptop", "gia": 1500, "ton": 5},
    {"ten": "Chuot", "gia": 20, "ton": 100},
    {"ten": "Ban phim", "gia": 50, "ton": 0},
]

    In ra các sản phẩm còn hàng (ton > 0)
    Tính tổng giá trị kho: sum(gia * ton)
    Tìm sản phẩm đắt nhất

Bài 5.3 (Nâng cao):
Cho 2 list: a = [1][2][3][4][5] và b = [4][5][6][7][8]. Tìm các phần tử chung chỉ dùng Set, 1 dòng code.

Làm xong 3 bài này gửi mình. Xong bài này bạn đã nắm 90% công việc hàng ngày của một Python Dev. Tiếp theo là Bài 6: Hàm - Viết code như một kiến trúc sư.