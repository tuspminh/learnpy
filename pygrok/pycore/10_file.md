**Bài 10: Xử lý File (Đọc & Ghi file)**

Hầu hết chương trình thực tế đều cần đọc/ghi dữ liệu ra file. Nắm vững bài này bạn sẽ làm được lưu điểm, danh bạ, nhật ký, xuất báo cáo…

* * *

### 1\. Mở file – Hàm open()

Python
    
    
    file = open("ten_file.txt", "r", encoding="utf-8")

**Các mode quan trọng:**

Mode| Ý nghĩa| File chưa tồn tại| Ghi đè dữ liệu cũ?  
---|---|---|---  
"r"| Đọc (read) – mặc định| Báo lỗi| —  
"w"| Ghi (write)| Tạo mới| Có (xóa hết)  
"a"| Ghi tiếp (append)| Tạo mới| Không  
"x"| Tạo file mới (exclusive)| Tạo mới| Lỗi nếu đã có  
"r+"| Đọc + ghi| Báo lỗi| Không  
"rb", "wb"| Đọc/ghi nhị phân| —| —  
  
**Luôn nên dùng encoding="utf-8"** khi làm việc với tiếng Việt.

* * *

### 2\. Cách tốt nhất: Dùng with (Khuyến nghị mạnh)

with sẽ **tự động đóng file** dù có lỗi xảy ra.

Python
    
    
    with open("data.txt", "r", encoding="utf-8") as f:
        noi_dung = f.read()
        print(noi_dung)
    # hết khối with → file tự đóng

* * *

### 3\. Đọc file

Python
    
    
    with open("data.txt", "r", encoding="utf-8") as f:
        # Cách 1: Đọc toàn bộ
        noi_dung = f.read()
        print(noi_dung)
    
        # Cách 2: Đọc từng dòng
        f.seek(0)                   # quay về đầu file
        for dong in f:
            print(dong.strip())     # strip() để bỏ ký tự xuống dòng
    
        # Cách 3: Đọc hết thành list
        f.seek(0)
        danh_sach_dong = f.readlines()
        print(danh_sach_dong)

* * *

### 4\. Ghi file

#### 4.1. Ghi mới (mode "w") – sẽ xóa hết nội dung cũ

Python
    
    
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write("Dòng 1\n")
        f.write("Dòng 2\n")
        f.write("Xin chào Python!\n")

#### 4.2. Ghi tiếp vào cuối (mode "a")

Python
    
    
    with open("output.txt", "a", encoding="utf-8") as f:
        f.write("Dòng được thêm vào\n")

#### 4.3. Ghi nhiều dòng từ list

Python
    
    
    dong = ["An\n", "Bình\n", "Chi\n"]
    
    with open("ten.txt", "w", encoding="utf-8") as f:
        f.writelines(dong)

* * *

### 5\. Ví dụ thực tế

**Ghi danh sách học sinh ra file:**

Python
    
    
    hoc_sinh = [
        "An,8.5",
        "Bình,7.0",
        "Chi,9.2"
    ]
    
    with open("diem.csv", "w", encoding="utf-8") as f:
        f.write("Họ tên,Điểm\n")          # tiêu đề
        for hs in hoc_sinh:
            f.write(hs + "\n")

**Đọc lại file vừa ghi:**

Python
    
    
    with open("diem.csv", "r", encoding="utf-8") as f:
        for dong in f:
            print(dong.strip())

* * *

### 6\. Xử lý lỗi thường gặp

Python
    
    
    try:
        with open("file_khong_ton_tai.txt", "r", encoding="utf-8") as f:
            print(f.read())
    except FileNotFoundError:
        print("Không tìm thấy file!")
    except PermissionError:
        print("Không có quyền truy cập file!")
    except Exception as e:
        print("Lỗi khác:", e)

* * *

### 7\. Một số thao tác hữu ích với os và pathlib

Python
    
    
    import os
    from pathlib import Path
    
    # Kiểm tra file có tồn tại không
    print(os.path.exists("data.txt"))
    
    # Lấy tên file, thư mục
    print(os.path.basename("C:/Users/An/data.txt"))
    print(os.path.dirname("C:/Users/An/data.txt"))
    
    # Cách hiện đại hơn với pathlib
    duong_dan = Path("data.txt")
    print(duong_dan.exists())
    print(duong_dan.name)
    print(duong_dan.stem)          # tên không có đuôi
    print(duong_dan.suffix)        # .txt

* * *

### 8\. Tóm tắt quy tắc vàng

  1. **Luôn dùng with open(...) as f:**
  2. Luôn chỉ định encoding="utf-8" khi làm việc với tiếng Việt
  3. Phân biệt rõ "w" (ghi đè) và "a" (ghi tiếp)
  4. Đọc file lớn nên đọc từng dòng (tránh read() hết vào bộ nhớ)
  5. Luôn xử lý ngoại lệ khi làm việc với file



* * *

### Bài tập Bài 10

**Bài 1:** Viết chương trình:

  * Tạo file loi_chao.txt và ghi vào đó 3 dòng bất kỳ
  * Đọc lại file và in ra màn hình



**Bài 2:** Viết chương trình nhập tên và điểm của nhiều học sinh (nhập đến khi tên = "x" thì dừng). Lưu vào file diem.txt theo định dạng:

text
    
    
    An,8.5
    Bình,7.0
    Chi,9.2

**Bài 3:** Viết chương trình đọc file diem.txt ở trên, sau đó:

  * In ra toàn bộ danh sách
  * Tính điểm trung bình
  * Tìm học sinh có điểm cao nhất



**Bài 4:** Viết chương trình đếm số dòng, số từ và số ký tự trong một file bất kỳ.

**Bài 5 (nâng cao):** Viết chương trình quản lý danh bạ đơn giản:

  * Lưu danh bạ vào file danh_ba.txt (mỗi dòng: Tên,Số điện thoại)
  * Có menu: Thêm liên hệ – Hiển thị – Tìm kiếm – Xóa – Thoát
  * Mỗi lần thay đổi phải cập nhật lại file



* * *

Làm xong gửi code + kết quả chạy. Tôi sẽ chữa bài và mở **Bài 11: Xử lý Exception (try – except)**.

Xử lý file là kỹ năng bắt buộc của mọi lập trình viên. Cứ làm kỹ nhé!

