**Bài 5: List (Danh sách)**

List là cấu trúc dữ liệu **quan trọng nhất** và dùng nhiều nhất trong Python. List dùng để lưu nhiều giá trị trong một biến, có thể thay đổi được (mutable).

* * *

### 1\. Tạo List

Python
    
    
    # List rỗng
    ds = []
    
    # List có sẵn phần tử
    so = [1, 2, 3, 4, 5]
    ten = ["An", "Bình", "Chi"]
    hon_hop = [1, "Python", 3.14, True]     # có thể chứa nhiều kiểu khác nhau
    
    # Dùng list()
    ds2 = list("Python")     # ['P', 'y', 't', 'h', 'o', 'n']

* * *

### 2\. Truy cập phần tử (Indexing & Slicing)

Python
    
    
    so = [10, 20, 30, 40, 50]
    
    print(so[0])      # 10 (phần tử đầu tiên)
    print(so[2])      # 30
    print(so[-1])     # 50 (phần tử cuối cùng)
    print(so[-2])     # 40

**Slicing (cắt list):**

Python
    
    
    print(so[1:4])    # [20, 30, 40]   (từ index 1 đến 3)
    print(so[:3])     # [10, 20, 30]   (từ đầu đến index 2)
    print(so[2:])     # [30, 40, 50]   (từ index 2 đến hết)
    print(so[::2])    # [10, 30, 50]   (bước nhảy 2)
    print(so[::-1])   # [50, 40, 30, 20, 10]  (đảo ngược)

* * *

### 3\. Thay đổi, thêm, xóa phần tử

Python
    
    
    so = [10, 20, 30, 40]
    
    # Thay đổi
    so[1] = 25
    print(so)               # [10, 25, 30, 40]
    
    # Thêm phần tử
    so.append(50)           # thêm vào cuối
    so.insert(1, 15)        # thêm vào vị trí index 1
    so.extend([60, 70])     # thêm nhiều phần tử
    
    # Xóa phần tử
    so.remove(30)           # xóa giá trị 30 đầu tiên tìm thấy
    so.pop()                # xóa phần tử cuối và trả về giá trị đó
    so.pop(0)               # xóa phần tử ở index 0
    del so[1]               # xóa theo index
    so.clear()              # xóa toàn bộ list

* * *

### 4\. Các phương thức thường dùng

Phương thức| Ý nghĩa| Ví dụ  
---|---|---  
append(x)| Thêm 1 phần tử vào cuối| ds.append(5)  
insert(i, x)| Thêm vào vị trí i| ds.insert(0, 9)  
extend(list)| Thêm nhiều phần tử| ds.extend([1,2])  
remove(x)| Xóa phần tử có giá trị x| ds.remove(3)  
pop(i)| Xóa và trả về phần tử ở vị trí i| ds.pop()  
index(x)| Trả về vị trí đầu tiên của x| ds.index(20)  
count(x)| Đếm số lần xuất hiện của x| ds.count(5)  
sort()| Sắp xếp tăng dần (thay đổi list gốc)| ds.sort()  
reverse()| Đảo ngược list| ds.reverse()  
copy()| Tạo bản sao| ds2 = ds.copy()  
  
Python
    
    
    diem = [7, 9, 5, 8, 6]
    diem.sort()                 # [5, 6, 7, 8, 9]
    diem.sort(reverse=True)     # [9, 8, 7, 6, 5]

* * *

### 5\. Các thao tác hữu ích khác

Python
    
    
    so = [1, 2, 3]
    
    print(len(so))          # 3 (số phần tử)
    print(2 in so)          # True
    print(5 not in so)      # True
    
    # Nối list
    a = [1, 2]
    b = [3, 4]
    c = a + b               # [1, 2, 3, 4]
    
    # Lặp list
    print(a * 3)            # [1, 2, 1, 2, 1, 2]

* * *

### 6\. Duyệt List

Python
    
    
    ten = ["An", "Bình", "Chi"]
    
    # Cách 1: duyệt giá trị
    for t in ten:
        print(t)
    
    # Cách 2: duyệt theo index
    for i in range(len(ten)):
        print(i, ten[i])
    
    # Cách 3: vừa index vừa giá trị (khuyên dùng)
    for i, t in enumerate(ten):
        print(i, t)

* * *

### 7\. List lồng nhau (Nested List)

Python
    
    
    hoc_sinh = [
        ["An", 8.5],
        ["Bình", 7.0],
        ["Chi", 9.2]
    ]
    
    print(hoc_sinh[0])          # ["An", 8.5]
    print(hoc_sinh[0][0])       # "An"
    print(hoc_sinh[2][1])       # 9.2

* * *

### 8\. List Comprehension (giới thiệu nhanh)

Cách viết ngắn gọn để tạo list mới:

Python
    
    
    # Tạo list các số bình phương từ 1 đến 5
    binh_phuong = [x**2 for x in range(1, 6)]
    print(binh_phuong)          # [1, 4, 9, 16, 25]
    
    # Chỉ lấy số chẵn
    so_chan = [x for x in range(1, 11) if x % 2 == 0]
    print(so_chan)              # [2, 4, 6, 8, 10]

* * *

### Bài tập Bài 5

**Bài 1:** Tạo một list chứa 5 tên bạn bè. Sau đó:

  * In phần tử đầu tiên và cuối cùng
  * Thêm 1 tên mới vào cuối
  * Xóa 1 tên bất kỳ
  * Sắp xếp list theo alphabet



**Bài 2:** Cho list: so = [4, 7, 1, 9, 3, 6, 2]

  * Tìm số lớn nhất, nhỏ nhất (không dùng max, min)
  * Tính tổng các phần tử
  * Đếm có bao nhiêu số chẵn



**Bài 3:** Viết chương trình nhập n số nguyên từ bàn phím, lưu vào list, rồi in ra:

  * List vừa nhập
  * List đã được sắp xếp tăng dần
  * Số phần tử của list



**Bài 4 (nâng cao):** Cho list điểm của học sinh: diem = [7.5, 8.0, 4.5, 9.0, 6.5, 3.5, 8.5]

Viết chương trình:

  1. Đếm số học sinh đạt (điểm >= 5)
  2. Tính điểm trung bình
  3. Tạo list mới chỉ chứa các điểm >= 8.0



* * *

Làm xong gửi code + kết quả. Tôi sẽ chữa bài và mở **Bài 6: Tuple, Set và Dictionary**.

Nắm vững List là bạn đã nắm được 50% sức mạnh xử lý dữ liệu của Python. Cứ làm kỹ nhé!

