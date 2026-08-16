Dưới đây là cơ chế biến hàm thành phương thức và cách tự xây dựng decorator @property.
------------------------------
## 1. Cách Python biến Hàm thành Phương thức (Bound Method)
Trong Python, mọi hàm (function) bạn định nghĩa trong class thực chất đều là một Non-Data Descriptor. Chúng sở hữu phương thức __get__ được viết sẵn bằng C.
## Cơ chế hoạt động
Khi bạn gọi một hàm từ instance (ví dụ: obj.method()), Python sẽ kích hoạt __get__ của hàm đó. Phương thức __get__ này sẽ đóng gói (bind) instance vào đối số đầu tiên của hàm, tạo ra một đối tượng mới gọi là Bound Method (phương thức liên kết).
## Code minh họa cơ chế ngầm:

class Người:
    def __init__(self, tên):
        self.tên = tên

    def chào(self):
        return f"Xin chào, tôi là {self.tên}"
p = Người("An")
# 1. Gọi thông thường
print(p.chào())  # "Xin chào, tôi là An"
# 2. Cơ chế thực sự chạy ngầm phía sau:hàm_gốc = Người.__dict__['chào']  # Lấy hàm thuần túy từ Classphương_thức_liên_kết = hàm_gốc.__get__(p, Người)  # Kích hoạt __get__ để truyền 'p' vào 'self'

print(phương_thức_liên_kết())  # "Xin chào, tôi là An"

------------------------------
## 2. Tự viết lại Decorator @property bằng Descriptor
Bản chất của @property trong Python là một Data Descriptor (ngay cả khi bạn không định nghĩa hàm setter, nó vẫn có __set__ ẩn để ném ra lỗi AttributeError: can't set attribute).
Dưới đây là cách tự làm một class BảnSaoProperty mô phỏng chính xác @property:

class BảnSaoProperty:
    """Descriptor giả lập lại decorator @property của Python"""
    def __init__(self, fget=None, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.fget is None:
            raise AttributeError("Thuộc tính này không cấu hình để đọc")
        return self.fget(instance)  # Gọi hàm getter gốc

    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("Không thể chỉnh sửa thuộc tính này (Read-only)")
        self.fset(instance, value)  # Gọi hàm setter gốc

    # Cú pháp bổ sung để hỗ trợ dùng làm decorator cho setter
    def setter(self, fset):
        return BảnSaoProperty(self.fget, fset)

## Cách sử dụng decorator tự chế:

class TàiKhoản:
    def __init__(self, số_dư):
        self._số_dư = số_dư

    @BảnSaoProperty
    def số_dư(self):
        return f"{self._số_dư:,} VND"

    @số_dư.setter
    def số_dư(self, giá_trị_mới):
        if giá_trị_mới < 0:
            raise ValueError("Số dư không thể âm!")
        self._số_dư = giá_trị_mới
# Kiểm tra hoạt độngtk = TàiKhoản(5000000)
print(tk.số_dư)  # Kết quả: 5,000,000 VND

tk.số_dư = 6000000  # Cập nhật thành công
print(tk.số_dư)  # Kết quả: 6,000,000 VND

------------------------------
Nếu bạn muốn tiếp tục nâng cao, tôi có thể:

* Giải thích cách tự viết decorator @classmethod hoặc @staticmethod.
* Hướng dẫn cách dùng descriptor kết hợp với __set_name__ để tự động nhận diện tên biến mà không cần truyền thủ công vào __init__.

Bạn muốn tìm hiểu về cách làm @classmethod hay mẹo __set_name__ để viết code ngắn gọn hơn?

