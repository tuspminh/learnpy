Để hiểu rõ sức mạnh của Descriptor trong thực tế, chúng ta sẽ cùng giải quyết một bài toán mô phỏng hệ thống ORM (Object-Relational Mapping) mini – tương tự như cách Django ORM hoặc SQLAlchemy quản lý các Model.
------------------------------
## 🛑 Bài toán đặt ra
Bạn cần viết một class User để quản lý thông tin tài khoản người dùng với các yêu cầu kiểm tra dữ liệu (validation) nghiêm ngặt sau:

   1. username: Phải là một chuỗi (string), có độ dài từ 3 đến 20 ký tự.
   2. age: Phải là một số nguyên (integer), nằm trong khoảng từ 18 đến 100 tuổi.
   3. email: Phải là một chuỗi chứa ký tự @.

## Vấn đề nếu dùng cách thông thường (@property):
Nếu dùng @property, bạn sẽ phải viết 3 hàm getter và 3 hàm setter cho cả 3 biến này. Code sẽ bị lặp lại (boilerplate code) rất nhiều và cực kỳ dài dòng nếu class có 10 hoặc 20 thuộc tính.
## Giải pháp tối ưu:
Sử dụng Data Descriptor kết hợp với __set_name__ để tạo ra các khuôn mẫu định dạng (Field Types) dùng chung.
------------------------------
## 🛠️ Code giải quyết bài toán

class StringField:
    """Descriptor kiểm tra định dạng chuỗi và độ dài."""
    def __init__(self, min_len=0, max_len=255):
        self.min_len = min_len
        self.max_len = max_len

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if not isinstance(value, str):
            raise TypeError(f"Trường '{self.name}' phải là một chuỗi (string)!")
        if not (self.min_len <= len(value) <= self.max_len):
            raise ValueError(f"Độ dài '{self.name}' phải từ {self.min_len} đến {self.max_len} ký tự!")
        instance.__dict__[self.name] = value

class IntegerField:
    """Descriptor kiểm tra số nguyên và khoảng giá trị."""
    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise TypeError(f"Trường '{self.name}' phải là số nguyên (integer)!")
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"Giá trị '{self.name}' không được nhỏ hơn {self.min_value}!")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"Giá trị '{self.name}' không được lớn hơn {self.max_value}!")
        instance.__dict__[self.name] = value

class EmailField(StringField):
    """Descriptor kế thừa StringField để kiểm tra định dạng email."""
    def __set__(self, instance, value):
        # Gọi validate kiểu chuỗi của lớp cha trước
        super().__set__(instance, value)
        if "@" not in value:
            raise ValueError(f"Email '{value}' không hợp lệ (thiếu ký tự '@')!")

## Cách áp dụng vào Model User cực kỳ ngắn gọn:

class User:
    # Khai báo các trường dữ liệu như một Framework ORM thực thụ
    username = StringField(min_len=3, max_len=20)
    age = IntegerField(min_value=18, max_value=100)
    email = EmailField()

    def __init__(self, username, age, email):
        self.username = username
        self.age = age
        self.email = email

------------------------------
## 🧪 Chạy thử nghiệm và kiểm tra lỗi## Trường hợp 1: Dữ liệu hợp lệ thành công

u = User(username="dan_dev", age=25, email="dandev@example.com")
print(f"User hợp lệ: {u.username}, {u.age} tuổi, Email: {u.email}")# Kết quả: User hợp lệ: dan_dev, 25 tuổi, Email: dandev@example.com

## Trường hợp 2: Thử gán sai kiểu dữ liệu

try:
    u.age = "hai mươi tuổi"  # Gán string cho trường IntegerFieldexcept TypeError as e:
    print(f"Lỗi: {e}")# Kết quả: Lỗi: Trường 'age' phải là số nguyên (integer)!

## Trường hợp 3: Thử gán giá trị vi phạm ràng buộc số lượng

try:
    u.age = 15  # Chưa đủ 18 tuổiexcept ValueError as e:
    print(f"Lỗi: {e}")# Kết quả: Lỗi: Giá trị 'age' không được nhỏ hơn 18!

## Trường hợp 4: Thử gán tên quá ngắn hoặc quá dài

try:
    u.username = "an"  # Chỉ có 2 ký tự, yêu cầu tối thiểu là 3except ValueError as e:
    print(f"Lỗi: {e}")# Kết quả: Lỗi: Độ dài 'username' phải từ 3 đến 20 ký tự!

## Trường hợp 5: Thử gán email sai định dạng

try:
    u.email = "dandev_gmail.com"  # Thiếu chữ @except ValueError as e:
    print(f"Lỗi: {e}")# Kết quả: Lỗi: Email 'dandev_gmail.com' không hợp lệ (thiếu ký tự '@')!

------------------------------
## 💡 Lợi ích lớn nhất ở đây là gì?
Nhờ có descriptor, class User của bạn trông cực kỳ sạch sẽ và dễ đọc. Nếu sau này bạn cần tạo thêm các class khác như Product(name=StringField(), price=IntegerField()) hay Customer(), bạn chỉ cần tái sử dụng lại các Field descriptor đã viết ở trên mà không phải copy-paste lại một dòng code kiểm tra (validation) nào cả.
Nếu bạn muốn tiếp tục, tôi có thể hướng dẫn bạn:

* Kết hợp các descriptor này với Metaclass để tự động xuất ra câu lệnh SQL (CREATE TABLE, INSERT) dựa trên dữ liệu object.
* Hoặc chuyển sang tìm hiểu về MRO (Method Resolution Order) trong đa kế thừa.

Bạn muốn nâng cấp hệ thống ORM mini này lên mức tự sinh SQL hay chuyển sang lý thuyết MRO?

