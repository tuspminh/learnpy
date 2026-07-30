**Bài 8: Xử lý chuỗi (String)**

Chuỗi (string) là kiểu dữ liệu dùng cực kỳ nhiều. Nắm vững cách xử lý chuỗi sẽ giúp bạn làm được rất nhiều bài toán thực tế (xử lý tên, email, dữ liệu văn bản…).

* * *

### 1\. Tạo chuỗi

Python
    
    
    s1 = "Xin chào"
    s2 = 'Python'
    s3 = """Đây là
    chuỗi
    nhiều dòng"""
    
    s4 = "I'm learning Python"          # dùng dấu kép khi bên trong có dấu nháy đơn
    s5 = 'He said "Hello"'              # ngược lại

* * *

### 2\. Indexing & Slicing (giống List)

Python
    
    
    s = "Python"
    
    print(s[0])       # P
    print(s[-1])      # n
    print(s[1:4])     # yth
    print(s[:3])      # Pyt
    print(s[2:])      # thon
    print(s[::-1])    # nohtyP   (đảo ngược chuỗi)

**Lưu ý quan trọng:** String là **immutable** (không thể thay đổi phần tử trực tiếp).

Python
    
    
    s = "Python"
    # s[0] = "J"     → lỗi

Muốn thay đổi phải tạo chuỗi mới.

* * *

### 3\. Các phương thức xử lý chuỗi thường dùng

#### 3.1. Chuyển đổi chữ hoa / thường

Python
    
    
    s = "Python Programming"
    
    print(s.upper())          # PYTHON PROGRAMMING
    print(s.lower())          # python programming
    print(s.title())          # Python Programming
    print(s.capitalize())     # Python programming
    print(s.swapcase())       # pYTHON pROGRAMMING

#### 3.2. Xóa khoảng trắng

Python
    
    
    s = "   Xin chào   "
    
    print(s.strip())          # "Xin chào"     (xóa 2 đầu)
    print(s.lstrip())         # "Xin chào   "  (xóa bên trái)
    print(s.rstrip())         # "   Xin chào"  (xóa bên phải)

#### 3.3. Tìm kiếm & thay thế

Python
    
    
    s = "Tôi đang học Python và yêu Python"
    
    print(s.find("Python"))       # 13 (vị trí đầu tiên)
    print(s.find("Java"))         # -1 (không tìm thấy)
    print(s.index("Python"))      # 13 (giống find nhưng không tìm thấy sẽ lỗi)
    print(s.count("Python"))      # 2
    print(s.replace("Python", "Java"))

#### 3.4. Kiểm tra nội dung

Python
    
    
    s = "Python3"
    
    print(s.startswith("Py"))     # True
    print(s.endswith("3"))        # True
    print(s.isalpha())            # False (vì có số)
    print("Python".isalpha())     # True
    print("12345".isdigit())      # True
    print("Python3".isalnum())    # True (chữ + số)
    print("   ".isspace())        # True

#### 3.5. Tách & nối chuỗi

Python
    
    
    s = "An,Bình,Chi,Dũng"
    
    ds = s.split(",")             # ['An', 'Bình', 'Chi', 'Dũng']
    print(ds)
    
    s2 = " ".join(ds)             # "An Bình Chi Dũng"
    print(s2)
    
    s3 = " - ".join(ds)           # "An - Bình - Chi - Dũng"

* * *

### 4\. Định dạng chuỗi (quan trọng)

#### Cách hiện đại nhất: **f-string** (khuyên dùng)

Python
    
    
    ten = "An"
    tuoi = 20
    diem = 8.5
    
    print(f"Tôi tên {ten}, {tuoi} tuổi, điểm {diem}")
    print(f"Năm sau tôi {tuoi + 1} tuổi")
    print(f"Điểm làm tròn: {diem:.1f}")

#### Các cách khác

Python
    
    
    # .format()
    print("Tôi tên {}, {} tuổi".format(ten, tuoi))
    print("Tôi tên {0}, {1} tuổi".format(ten, tuoi))
    print("Tôi tên {name}, {age} tuổi".format(name=ten, age=tuoi))
    
    # % (kiểu cũ)
    print("Tôi tên %s, %d tuổi" % (ten, tuoi))

* * *

### 5\. Một số thao tác hữu ích khác

Python
    
    
    s = "python"
    
    print(len(s))                 # 6
    print("th" in s)              # True
    print("java" not in s)        # True
    
    # Lặp chuỗi
    print("Ha" * 3)               # HaHaHa
    
    # Kiểm tra chuỗi rỗng
    s = ""
    if not s:
        print("Chuỗi rỗng")

* * *

### 6\. Ví dụ thực tế hay gặp

Python
    
    
    # Chuẩn hóa tên
    ten = "  nGuYễn vĂn aN  "
    ten_chuan = ten.strip().title()
    print(ten_chuan)              # Nguyễn Văn An
    
    # Kiểm tra email đơn giản
    email = "nguyenvanan@gmail.com"
    if "@" in email and email.endswith(".com"):
        print("Email hợp lệ (kiểm tra cơ bản)")

* * *

### Bài tập Bài 8

**Bài 1:** Cho chuỗi: s = " Python Programming "

  * Xóa khoảng trắng 2 đầu
  * Chuyển thành chữ hoa toàn bộ
  * Chuyển thành chữ thường toàn bộ
  * Đếm số lần xuất hiện chữ “m”



**Bài 2:** Viết chương trình nhập vào họ tên đầy đủ (có thể thừa khoảng trắng). In ra họ tên đã được chuẩn hóa (xóa khoảng trắng thừa + viết hoa chữ cái đầu mỗi từ).

**Ví dụ:** Input: " nGuYễn vĂn aN " Output: "Nguyễn Văn An"

**Bài 3:** Viết hàm dem_ky_tu(chuoi) trả về dictionary đếm số lần xuất hiện của mỗi ký tự (bỏ qua khoảng trắng).

**Ví dụ:** Input: "hello world" Output: {'h':1, 'e':1, 'l':3, 'o':2, 'w':1, 'r':1, 'd':1}

**Bài 4:** Viết chương trình kiểm tra một chuỗi có phải là **palindrome** không (đọc xuôi ngược giống nhau). Ví dụ: "radar", "level", "12321" là palindrome.

**Bài 5 (nâng cao):** Viết hàm chuan_hoa_email(email):

  * Chuyển thành chữ thường
  * Xóa khoảng trắng thừa
  * Kiểm tra có chứa @ và dấu . sau @ không
  * Trả về True / False kèm email đã chuẩn hóa



* * *

Làm xong gửi code + kết quả. Tôi sẽ chữa bài và mở **Bài 9: Module & Package** (cách tổ chức code và dùng thư viện).

Chuỗi là “vật liệu” xuất hiện ở hầu hết mọi chương trình. Cứ làm kỹ nhé!

