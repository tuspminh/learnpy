Dưới đây là một bài tập lớn mang tính thực tế cao, giúp bạn kết hợp toàn bộ sức mạnh của Descriptor, Metaclass, và Class Decorator để xây dựng một Hệ thống Quản lý và Kiểm toán Nhân sự (HR Audit System).
------------------------------
## 🛑 Đặt bài toán thực tế
Bạn cần xây dựng một hệ thống quản lý thông tin nhân viên (Employee) đáp ứng các yêu cầu sau:

   1. Descriptor: Kiểm soát dữ liệu thuộc tính. Thuộc tính salary phải là số nguyên dương. Thuộc tính role phải nằm trong danh sách cho trước (ví dụ: "Dev", "Manager", "HR").
   2. Metaclass: Tự động đăng ký (Auto-register). Mỗi khi một class nhân viên mới được định nghĩa (như Employee, Contractor), hệ thống phải tự động lưu tên class đó vào một danh mục tổng mà không cần đăng ký thủ công.
   3. Class Decorator: Tính năng bảo mật/kiểm toán. Tự động ghi log (Nhật ký hành động) kèm theo dấu thời gian (timestamp) chính xác của hệ thống (năm hiện tại là 2026) mỗi khi có ai đó thay đổi lương hoặc chức vụ của nhân viên.

------------------------------
## 🛠️ Code giải quyết bài toán tổng hợp

from datetime import datetime
# ==========================================# 1. DESCRIPTOR: Kiểm soát thuộc tính (Data Validation)# ==========================================class ValidatedField:
    def __set_name__(self, owner, name):
        self.name = name
    def __get__(self, instance, owner):
        if instance is None: return self
        return instance.__dict__.get(self.name)
class PositiveInteger(ValidatedField):
    def __set__(self, instance, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"Trường '{self.name}' phải là số nguyên dương!")
        instance.__dict__[self.name] = value
class ChoiceField(ValidatedField):
    def __init__(self, choices):
        self.choices = choices
    def __set__(self, instance, value):
        if value not in self.choices:
            raise ValueError(f"Giá trị '{value}' cho '{self.name}' phải nằm trong: {self.choices}")
        instance.__dict__[self.name] = value

# ==========================================# 2. METACLASS: Tự động đăng ký Class vào Hệ thống (Registry)# ==========================================# Danh mục tổng lưu trữ các lớp nhân sự hợp lệ trong hệ thốngHR_REGISTRY = {}
class HRMeta(type):
    def __new__(cls, name, bases, dct):
        new_class = super().__new__(cls, name, bases, dct)
        # Bỏ qua không đăng ký class cha chung nếu tên là 'BaseEmployee'
        if name != 'BaseEmployee':
            HR_REGISTRY[name.lower()] = new_class
            print(f"[HỆ THỐNG] Đã tự động đăng ký mô hình nhân sự mới: '{name}'")
        return new_class
class BaseEmployee(metaclass=HRMeta):
    pass

# ==========================================# 3. CLASS DECORATOR: Giám sát và Kiểm toán (Audit Logging)# ==========================================def audit_logging(cls):
    """Decorator bọc thuộc tính descriptor để ghi nhật ký thay đổi."""
    # Lấy hàm __set__ gốc của các descriptor trong class
    for attr_name, attr_obj in cls.__dict__.items():
        if isinstance(attr_obj, ValidatedField):
            orig_set = attr_obj.__set__
            
            # Viết đè một hàm __set__ mới có tính năng ghi log thời gian
            def make_audited_set(field_name, original_set_method):
                def audited_set(instance, value):
                    # Lấy giá trị cũ trước khi thay đổi (nếu có)
                    old_value = instance.__dict__.get(field_name, "Chưa khởi tạo")
                    # Chạy hàm gán dữ liệu gốc (để kiểm tra validate lỗi nếu có)
                    original_set_method(instance, value)
                    # Ghi log kèm mốc thời gian hệ thống hiện tại (Năm 2026)
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"  [KIỂM TOÁN LƯU VẾT - {now_str}] "
                          f"Nhân viên '{instance.name}': Thay đổi '{field_name}' "
                          f"từ [{old_value}] thành [{value}]")
                return audited_set
            
            # Gán đè hàm set đã được nhúng tính năng kiểm toán vào descriptor
            attr_obj.__set__ = make_audited_set(attr_name, orig_set)
    return cls

------------------------------
## 🧪 Áp dụng vào Mô hình Nhân viên và Chạy thử nghiệm
Bây giờ chúng ta sẽ định nghĩa một lớp nhân viên cụ thể bằng cách sử dụng cả 3 công cụ trên.

@audit_loggingclass Employee(BaseEmployee):
    # Khai báo các Descriptor kiểm soát dữ liệu
    salary = PositiveInteger()
    role = ChoiceField(choices=["Dev", "Manager", "HR"])

    def __init__(self, name, salary, role):
        self.name = name
        # Các lệnh gán này sẽ kích hoạt tính năng kiểm toán từ Decorator
        self.salary = salary
        self.role = role
# --- KIỂM TRA HỆ THỐNG ---
print("\n--- 1. Kiểm tra Metaclass ---")
print(f"Các lớp nhân sự hiện có trong hệ thống: {list(HR_REGISTRY.keys())}")

print("\n--- 2. Khởi tạo và Kiểm toán Nhân viên ---")# Tạo nhân viên hợp lệ (Sẽ in log khởi tạo)emp = Employee(name="Thành", salary=20000000, role="Dev")

print("\n--- 3. Thay đổi thông tin (Ghi đè thuộc tính) ---")# Thay đổi lương (Tính năng Decorator bọc Descriptor bắt đầu lưu vết)
emp.salary = 25000000
emp.role = "Manager"

print("\n--- 4. Kiểm tra lỗi dữ liệu vi phạm Descriptor ---")try:
    emp.salary = -5000000  # Lương âmexcept ValueError as e:
    print(f"Ứng dụng chặn lỗi thành công: {e}")
try:
    emp.role = "CEO"  # Role không nằm trong danh sách choicesexcept ValueError as e:
    print(f"Ứng dụng chặn lỗi thành công: {e}")

------------------------------
## 🎯 Phân tích vai trò của từng công cụ trong bài tập:

   1. Metaclass (HRMeta): Hoạt động ngầm ngay khi class Employee được định nghĩa. Nó tự động nạp class vào dictionary HR_REGISTRY giúp hệ thống quản lý tập trung mà bạn không cần viết code đăng ký bằng tay.
   2. Descriptor (PositiveInteger, ChoiceField): Chịu trách nhiệm bảo vệ tính toàn vẹn của dữ liệu (chặn số âm, chặn chức vụ không tồn tại). Nó hoạt động tách biệt, có thể tái sử dụng cho bất kỳ class nào khác (như class Contractor, Intern).
   3. Class Decorator (@audit_logging): Sau khi class Employee được sinh ra, decorator nhảy vào quét các thuộc tính của nó, bọc thêm một lớp "camera giám sát" lên hàm __set__ của các descriptor để tự động in ra dòng lịch sử thay đổi kèm mốc thời gian thực tế.

Để tiếp tục nâng cao trình độ, chúng ta có thể:

* Tìm hiểu sâu về thuật toán MRO (Method Resolution Order) của Python để giải quyết triệt để các xung đột hàm khi làm việc với Đa kế thừa (Multiple Inheritance) phức tạp.
* Hoặc chuyển sang nghiên cứu cơ chế quản lý bộ nhớ của Python như Garbage Collection (Bộ thu gom rác) và Reference Counting.

Bạn muốn chuyển sang khám phá cơ chế MRO hay tìm hiểu về quản lý bộ nhớ?

