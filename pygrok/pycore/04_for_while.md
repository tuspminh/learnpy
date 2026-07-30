**Bài 4: Vòng lặp (for – while)**

Vòng lặp giúp bạn lặp lại một đoạn code nhiều lần mà không cần viết lại. Đây là một trong những công cụ mạnh nhất của lập trình.

* * *

### 1\. Vòng lặp while

Cú pháp:

Python
    
    
    while điều_kiện:
        # khối lệnh sẽ chạy liên tục khi điều_kiện còn đúng

**Ví dụ 1: Đếm từ 1 đến 5**

Python
    
    
    i = 1
    while i <= 5:
        print(i)
        i += 1          # rất quan trọng: phải thay đổi biến điều kiện

**Ví dụ 2: Nhập mật khẩu đến khi đúng**

Python
    
    
    mat_khau_dung = "python123"
    
    while True:
        mk = input("Nhập mật khẩu: ")
        if mk == mat_khau_dung:
            print("Đăng nhập thành công!")
            break
        else:
            print("Sai mật khẩu, thử lại!")

* * *

### 2\. Vòng lặp for

Dùng khi bạn biết trước số lần lặp hoặc muốn duyệt qua một chuỗi/danh sách.

#### 2.1. Duyệt chuỗi

Python
    
    
    for chu_cai in "Python":
        print(chu_cai)

#### 2.2. Dùng range() (rất quan trọng)

Python
    
    
    # range(stop) → từ 0 đến stop-1
    for i in range(5):
        print(i)          # 0 1 2 3 4
    
    # range(start, stop)
    for i in range(1, 6):
        print(i)          # 1 2 3 4 5
    
    # range(start, stop, step)
    for i in range(0, 10, 2):
        print(i)          # 0 2 4 6 8
    
    for i in range(5, 0, -1):
        print(i)          # 5 4 3 2 1

* * *

### 3\. break và continue

Lệnh| Ý nghĩa  
---|---  
break| Dừng vòng lặp ngay lập tức  
continue| Bỏ qua phần còn lại của vòng hiện tại, nhảy sang vòng tiếp theo  
  
**Ví dụ break:**

Python
    
    
    for i in range(1, 10):
        if i == 5:
            break
        print(i)          # chỉ in 1 2 3 4

**Ví dụ continue:**

Python
    
    
    for i in range(1, 8):
        if i % 2 == 0:
            continue      # bỏ qua số chẵn
        print(i)          # chỉ in số lẻ: 1 3 5 7

* * *

### 4\. Vòng lặp lồng nhau (Nested loop)

Python
    
    
    for i in range(1, 4):
        for j in range(1, 4):
            print(f"i = {i}, j = {j}")

**Ứng dụng thực tế – In bảng cửu chương:**

Python
    
    
    for i in range(1, 10):
        for j in range(1, 10):
            print(f"{i} x {j} = {i*j}")
        print("-" * 15)     # ngăn cách giữa các bảng

* * *

### 5\. Một số mẫu hay dùng

Python
    
    
    # Tính tổng từ 1 đến n
    n = 10
    tong = 0
    for i in range(1, n+1):
        tong += i
    print("Tổng =", tong)
    
    # Đếm số lần xuất hiện
    chuoi = "hello python"
    dem = 0
    for ky_tu in chuoi:
        if ky_tu == "o":
            dem += 1
    print("Số chữ o:", dem)

* * *

### 6\. Lỗi thường gặp

Lỗi| Nguyên nhân| Cách tránh  
---|---|---  
Vòng lặp vô hạn| Quên thay đổi biến điều kiện trong while| Luôn kiểm tra biến đếm  
IndentationError| Thụt lề sai| Dùng 4 space nhất quán  
range sai| Nhầm range(5) với range(1,5)| Nhớ range không lấy giá trị stop  
  
* * *

### Bài tập Bài 4

**Bài 1:** In ra các số từ 1 đến 20 bằng cả for và while.

**Bài 2:** In ra tất cả số chẵn từ 1 đến 50.

**Bài 3:** Viết chương trình nhập một số n, tính tổng các số từ 1 đến n.

**Bài 4:** In bảng cửu chương của một số bất kỳ (người dùng nhập vào).

**Bài 5 (nâng cao):** Viết chương trình đoán số:

  * Máy tính “nghĩ” ra một số ngẫu nhiên từ 1 đến 100
  * Người chơi nhập số để đoán
  * Chương trình báo “Lớn hơn”, “Nhỏ hơn” hoặc “Đúng rồi!”
  * Đếm số lần đoán



_(Gợi ý: dùng import random và random.randint(1, 100))_

* * *

Làm xong gửi code + kết quả chạy. Tôi sẽ chữa bài và mở **Bài 5: List (Danh sách)** – cấu trúc dữ liệu quan trọng nhất của Python.

Cứ làm từ từ, nắm vững vòng lặp rồi mới sang bài tiếp theo nhé!

