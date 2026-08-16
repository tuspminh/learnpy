Dưới đây là cách kết hợp Metaclass với Descriptor để tạo ra một bộ sinh câu lệnh SQL tự động, cùng với cách phân biệt Metaclass và Class Decorator.
------------------------------
## 1. Kết hợp Metaclass và Descriptor: Nâng cấp ORM tự sinh SQL
Chúng ta sẽ dùng Metaclass để quét qua class User, tìm tất cả các thuộc tính là Descriptor (các trường dữ liệu) đã làm ở bài trước, sau đó tự động tạo ra câu lệnh SQL CREATE TABLE.
## Code hoàn chỉnh:

# --- 1. Tái sử dụng các Descriptor từ bài trước (Đơn giản hóa để tập trung vào SQL) ---class Field:
    def __set_name__(self, owner, name):
        self.name = name
    def __get__(self, instance, owner):
        if instance is None: return self
        return instance.__dict__.get(self.name)
    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
class StringField(Field):
    sql_type = "VARCHAR(255)"
class IntegerField(Field):
    sql_type = "INTEGER"
# --- 2. Xây dựng Metaclass để quét và sinh cấu trúc Table ---class ORMMetaclass(type):
    def __new__(cls, name, bases, dct):
        # Không xử lý bản thân class cha Model
        if name == 'Model':
            return super().__new__(cls, name, bases, dct)

        # Quét tìm các thuộc tính là Descriptor (Field)
        fields = {}
        for key, value in dct.items():
            if isinstance(value, Field):
                fields[key] = value.sql_type

        # Lưu danh sách fields vào cấu trúc class để dùng sau này
        dct['_fields'] = fields
        dct['_table_name'] = name.lower()  # Tên bảng mặc định là tên class viết thường
        return super().__new__(cls, name, bases, dct)
# --- 3. Class Cha nền tảng cung cấp hàm sinh SQL ---class Model(metaclass=ORMMetaclass):
    @classmethod
    def get_create_table_sql(cls):
        """Hàm tự động sinh câu lệnh SQL CREATE TABLE"""
        columns = [f"{name} {sql_type}" for name, sql_type in cls._fields.items()]
        sql = f"CREATE TABLE {cls._table_name} (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    "
        sql += ",\n    ".join(columns)
        sql += "\n);"
        return sql

## Cách sử dụng để tạo Model và sinh SQL:

class User(Model):
    username = StringField()
    age = IntegerField()
# Chỉ cần gọi hàm từ class, SQL sẽ tự động được sinh ra dựa trên cấu trúc các Descriptor!
print(User.get_create_table_sql())

## Kết quả in ra màn hình:

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255),
    age INTEGER
);

------------------------------
## 2. Phân biệt Metaclass và Class Decorator
Cả hai công cụ này đều được dùng để chỉnh sửa hoặc mở rộng tính năng của một Class, nhưng chúng có bản chất và thời điểm hoạt động khác nhau.

| Tiêu chí | Metaclass | Class Decorator |
|---|---|---|
| Bản chất | Là một Class kế thừa từ type để tạo ra class mới. | Là một Hàm (hoặc class) nhận vào một class và trả về class đã sửa đổi. |
| Thời điểm chạy | Chạy trong khi class đang được xây dựng (giai đoạn __new__). | Chạy sau khi class đã được xây dựng xong hoàn toàn. |
| Tính kế thừa | Có. Nếu Class Cha dùng metaclass, các Class Con tự động thừa hưởng metaclass đó. | Không. Decorator chỉ tác động lên đúng Class được bọc nó, Class Con sẽ không tự động có. |
| Độ phức tạp | Cao, khó đọc, can thiệp sâu vào cấu trúc cốt lõi của Python. | Thấp, dễ viết, tường minh và dễ debug hơn. |

## Ví dụ minh họa sự khác biệt:

# Cách 1: Dùng Class Decorator (Chỉ áp dụng cho đúng class được bọc)def add_status(cls):
    cls.status = "active"
    return cls

@add_statusclass Order:
    pass
class SpecialOrder(Order): 
    pass  # Không tự động chạy lại logic của decorator, chỉ thừa hưởng thuộc tính tĩnh status từ cha

# Cách 2: Dùng Metaclass (Áp dụng cho cả cây phả hệ kế thừa)class StatusMeta(type):
    def __new__(cls, name, bases, dct):
        dct['status'] = "active"
        return super().__new__(cls, name, bases, dct)
class Invoice(metaclass=StatusMeta):
    pass
class SpecialInvoice(Invoice):
    pass  # Khi định nghĩa SpecialInvoice, Metaclass SẼ CHẠY LẠI một lần nữa cho class con này

------------------------------
## Tóm lại quy tắc chọn lựa:

* Hãy ưu tiên dùng Class Decorator nếu bạn chỉ muốn thêm một vài hàm, thuộc tính đơn giản cho một vài class cụ thể (vì nó dễ viết, dễ hiểu).
* Hãy dùng Metaclass khi bạn đang xây dựng Framework, thư viện (như ORM), cần can thiệp vào quá trình tạo dựng class của người dùng hoặc bắt buộc tính năng đó phải tự động lan truyền xuống mọi Class Con khi kế thừa.

Đến đây, bạn đã đi qua toàn bộ các khái niệm nâng cao bổ trợ nhau: Descriptor -> @classmethod/@property -> Metaclass -> ORM.
Nếu bạn muốn tiếp tục, tôi có thể giải thích về MRO (Method Resolution Order) - cơ chế giúp Python tìm kiếm hàm khi một class kế thừa từ rất nhiều class cha khác nhau (đa kế thừa). Bạn có muốn chuyển sang tìm hiểu cơ chế MRO này không?

