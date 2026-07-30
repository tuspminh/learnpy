**Bài 11: Xử lý Exception (try – except)**

Khi chương trình chạy, rất nhiều tình huống bất ngờ có thể xảy ra (chia cho 0, file không tồn tại, nhập sai kiểu dữ liệu…). Exception Handling giúp chương trình **không bị dừng đột ngột** và xử lý lỗi một cách chuyên nghiệp.

* * *

### 1\. Lỗi (Error) vs Exception

  * **Syntax Error** : Lỗi cú pháp → phải sửa trước khi chạy
  * **Exception** : Lỗi xảy ra **khi đang chạy** chương trình



Ví dụ các Exception phổ biến:

  * ZeroDivisionError: Chia cho 0
  * ValueError: Sai kiểu giá trị (int("abc"))
  * TypeError: Sai kiểu dữ liệu
  * FileNotFoundError: Không tìm thấy file
  * IndexError: Truy cập index ngoài phạm vi
  * KeyError: Truy cập key không tồn tại trong dict
  * NameError: Dùng biến chưa được định nghĩa



* * *

### 2\. Cấu trúc cơ bản: try – except

Python
    
    
    try:
        # đoạn code có thể gây lỗi
        so = int(input("Nhập một số: "))
        print(10 / so)
    except:
        print("Có lỗi xảy ra!")

**Cách tốt hơn – bắt lỗi cụ thể:**

Python
    
    
    try:
        so = int(input("Nhập một số: "))
        print(10 / so)
    except ValueError:
        print("Bạn phải nhập số nguyên!")
    except ZeroDivisionError:
        print("Không thể chia cho 0!")

* * *

### 3\. Nhiều Exception cùng lúc

Python
    
    
    try:
        so = int(input("Nhập số: "))
        print(10 / so)
    except (ValueError, ZeroDivisionError) as e:
        print("Lỗi:", e)

Hoặc bắt từng loại riêng để xử lý khác nhau.

* * *

### 4\. else và finally

Python
    
    
    try:
        so = int(input("Nhập số: "))
        ket_qua = 10 / so
    except ValueError:
        print("Nhập sai kiểu dữ liệu")
    except ZeroDivisionError:
        print("Không chia được cho 0")
    else:
        # Chỉ chạy khi KHÔNG có lỗi
        print("Kết quả là:", ket_qua)
    finally:
        # Luôn chạy dù có lỗi hay không
        print("Kết thúc xử lý")

**Tóm tắt:**

  * else: chạy khi không có exception
  * finally: luôn chạy (thường dùng để đóng file, giải phóng tài nguyên)



* * *

### 5\. raise – Chủ động gây ra Exception

Python
    
    
    def chia(a, b):
        if b == 0:
            raise ZeroDivisionError("Mẫu số không được bằng 0")
        return a / b
    
    try:
        print(chia(10, 0))
    except ZeroDivisionError as e:
        print("Lỗi:", e)

**Ví dụ thực tế hơn:**

Python
    
    
    def kiem_tra_tuoi(tuoi):
        if tuoi < 0:
            raise ValueError("Tuổi không được âm")
        if tuoi > 150:
            raise ValueError("Tuổi không hợp lệ")
        print("Tuổi hợp lệ:", tuoi)
    
    try:
        kiem_tra_tuoi(-5)
    except ValueError as e:
        print(e)

* * *

### 6\. Một số Exception thường gặp & cách xử lý

Python
    
    
    # 1. ValueError
    try:
        so = int("abc")
    except ValueError:
        print("Không thể chuyển thành số nguyên")
    
    # 2. IndexError
    ds = [1, 2, 3]
    try:
        print(ds[10])
    except IndexError:
        print("Index vượt quá phạm vi list")
    
    # 3. KeyError
    d = {"ten": "An"}
    try:
        print(d["tuoi"])
    except KeyError:
        print("Không tồn tại key này")
    
    # 4. FileNotFoundError
    try:
        with open("file_khong_co.txt", "r") as f:
            print(f.read())
    except FileNotFoundError:
        print("File không tồn tại")

* * *

### 7\. Tạo Exception tùy chỉnh (Custom Exception)

Python
    
    
    class TuoiKhongHopLe(Exception):
        pass
    
    def kiem_tra_tuoi(tuoi):
        if tuoi < 0 or tuoi > 150:
            raise TuoiKhongHopLe("Tuổi phải nằm trong khoảng 0 – 150")
        return tuoi
    
    try:
        kiem_tra_tuoi(200)
    except TuoiKhongHopLe as e:
        print("Lỗi tùy chỉnh:", e)

* * *

### 8\. Nguyên tắc viết code xử lý lỗi tốt

  1. **Bắt Exception cụ thể** , tránh dùng except: trống
  2. Chỉ dùng try cho đoạn code thực sự có thể gây lỗi
  3. Không lạm dụng try-except để che giấu lỗi logic
  4. Luôn thông báo lỗi rõ ràng cho người dùng
  5. Dùng finally hoặc with để giải phóng tài nguyên
  6. Ghi log lỗi trong chương trình thực tế (thay vì chỉ print)



* * *

### Bài tập Bài 11

**Bài 1:** Viết chương trình nhập 2 số và thực hiện phép chia. Xử lý đầy đủ các trường hợp: nhập không phải số, chia cho 0.

**Bài 2:** Viết hàm tinh_bmi(can_nang, chieu_cao):

  * Kiểm tra cân nặng và chiều cao phải > 0
  * Nếu không hợp lệ thì raise ValueError
  * Trả về BMI nếu hợp lệ



**Bài 3:** Viết chương trình đọc file. Nếu file không tồn tại thì thông báo và tạo file mới với nội dung mặc định.

**Bài 4:** Viết hàm lay_phan_tu(ds, index):

  * Trả về phần tử tại vị trí index
  * Nếu index vượt phạm vi thì trả về None và in cảnh báo (dùng try-except)



**Bài 5 (nâng cao):** Viết chương trình đăng nhập đơn giản:

  * Tên đăng nhập đúng: "admin"
  * Mật khẩu đúng: "python123"
  * Cho phép nhập tối đa 3 lần
  * Nếu sai quá 3 lần thì báo “Tài khoản bị khóa”
  * Xử lý đầy đủ exception khi nhập liệu



* * *

Làm xong gửi code + kết quả chạy. Tôi sẽ chữa bài và mở **Bài 12: Lập trình hướng đối tượng (OOP) – Phần 1: Class & Object**.

Xử lý Exception là kỹ năng giúp chương trình của bạn “bền” và chuyên nghiệp hơn rất nhiều. Cứ làm kỹ nhé!

