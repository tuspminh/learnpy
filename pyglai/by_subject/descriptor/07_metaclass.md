Trong Python, metaclass (lớp siêu đối tượng) là một lớp dùng để tạo ra các lớp khác.
Nếu một class thông thường đóng vai trò là "bản thiết kế" để tạo ra các đối tượng (instances), thì metaclass chính là "bản thiết kế của bản thiết kế" dùng để tạo ra chính các class đó.
------------------------------
## 1. Tư duy cốt lõi: Mọi thứ trong Python đều là Đối tượng
Để hiểu metaclass, bạn cần nhớ một quy tắc tối cao của Python: Class cũng là một đối tượng (object).
Vì class là một đối tượng, nên nó phải được tạo ra từ một cái gì đó. Cái tạo ra class đó chính là metaclass. Mặc định trong Python, mọi class đều được tạo ra bởi một metaclass mặc định hệ thống tên là type.

class MyClass:
    pass
obj = MyClass()

print(type(obj))      # <class '__main__.MyClass'> (MyClass tạo ra obj)
print(type(MyClass))  # <class 'type'> (type tạo ra MyClass)

------------------------------
## 2. Cách tự xây dựng một Metaclass
Khi bạn muốn can thiệp vào quá trình khởi tạo hoặc thay đổi cấu trúc của một Class ngay khi nó vừa được định nghĩa (chứ không phải khi tạo instance), bạn sẽ viết một custom metaclass kế thừa từ type.
Phương thức __new__(cls, name, bases, dct) của metaclass nhận vào:

* name: Tên của class sắp được tạo.
* bases: Các class cha mà class này kế thừa (tuple).
* dct: Từ điển chứa toàn bộ thuộc tính và hàm định nghĩa bên trong class đó.

## Ví dụ: Metaclass tự động chuyển tất cả tên thuộc tính thành viết hoa
Giả sử bạn muốn bắt buộc mọi lập trình viên trong dự án khi khai báo thuộc tính trong class đều phải viết hoa, nếu họ viết thường, metaclass sẽ tự động sửa lại.

class UpperCaseMeta(type):
    def __new__(cls, name, bases, dct):
        # Tạo một dictionary mới để lưu các thuộc tính đã chuẩn hóa
        uppercase_attr = {}
        for key, value in dct.items():
            # Nếu là thuộc tính do người dùng định nghĩa (không bắt đầu bằng '__')
            if not key.startswith('__'):
                uppercase_attr[key.upper()] = value
            else:
                uppercase_attr[key] = value
                
        # Gọi class cha (type) để khởi tạo class với dictionary mới
        return super().__new__(cls, name, bases, uppercase_attr)

## Cách áp dụng Metaclass vào Class:
Sử dụng tham số metaclass= khi khai báo lớp:

class ThongTin(metaclass=UpperCaseMeta):
    ten = "Python"
    phien_ban = 3.12
# Kiểm tra kết quả# Các thuộc tính viết thường ban đầu đã bị biến mất và chuyển thành viết hoa
print(hasattr(ThongTin, "ten"))        # Kết quả: False
print(hasattr(ThongTin, "TEN"))        # Kết quả: True
print(ThongTin.TEN)                    # Kết quả: Python

------------------------------
## 3. Ứng dụng thực tế của Metaclass
Bạn sẽ rất hiếm khi tự viết metaclass trong các ứng dụng thông thường, nhưng chúng là xương sống của các framework lớn:

* Django ORM / SQLAlchemy: Khi bạn khai báo name = models.CharField(), Django dùng metaclass để quét qua class của bạn, gom các field này lại và tự động liên kết (map) class đó với một bảng tương ứng trong Database.
* Đăng ký tự động (API/Plugin Registration): Tự động ghi nhận một class mới vào hệ thống quản lý plugin ngay khi class đó được định nghĩa mà không cần lập trình viên phải gọi hàm đăng ký thủ công.
* Kiểm tra và áp đặt luật (Enforcement): Bắt buộc các class con phải định nghĩa một số thuộc tính cụ thể, nếu không có sẽ ném ra lỗi ngay khi chạy chương trình (chặn lỗi sớm trước khi tạo instance).

------------------------------
Nếu bạn muốn tiếp tục đào sâu, tôi có thể cung cấp:

* Cách kết hợp Metaclass với Descriptor từ bài toán trước để hoàn thiện một hệ thống ORM tự động sinh câu lệnh SQL (CREATE TABLE).
* Phân biệt sự khác nhau giữa việc dùng Metaclass và Class Decorator (Cả hai đều sửa đổi class nhưng chạy ở thời điểm khác nhau).

Bạn muốn nâng cấp hệ thống ORM sinh SQL hay phân biệt với Class Decorator?

