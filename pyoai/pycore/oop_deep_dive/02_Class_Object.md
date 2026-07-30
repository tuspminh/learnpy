# Buổi 2: Class Object, Instance Object, Namespace và Attribute Lookup

Đây là một trong những buổi quan trọng nhất của OOP Python.

Sau buổi này bạn sẽ hiểu:

- Class thực chất cũng là một object.
- Instance được tạo ra như thế nào.
- Python lưu thuộc tính ở đâu.
- Vì sao đôi khi `obj.x` lấy được giá trị từ class, đôi khi lại từ instance.
- Cơ chế **Attribute Lookup** – nền tảng để hiểu `property`, `descriptor`, `super()`, ORM (SQLAlchemy, Django), PySide6...

---

# 1. Ôn lại buổi trước

Ví dụ:

```text-x-trilium-auto
a = 10
```

Nhiều người nghĩ:

```text-x-trilium-auto
a
│
▼
10
```

Thực tế:

```text-x-trilium-auto
Variable
   │
   ▼
Reference
   │
   ▼
Object(int)
```

Biến chỉ giữ **tham chiếu (reference)** đến object.

Điều này cũng đúng với class.

---

# 2. Class cũng là một object

Ví dụ:

```text-x-trilium-auto
class Dog:
    pass
```

Nhiều người nghĩ:

```text-x-trilium-auto
Dog
```

chỉ là "định nghĩa".

Thực ra khi Python chạy đến đây, nó tạo ra một object.

```text-x-trilium-auto
          Dog
           │
           ▼
     +--------------+
     | Class Object |
     +--------------+
```

Hãy kiểm tra:

```text-x-trilium-auto
class Dog:
    pass

print(type(Dog))
```

Kết quả

```text-x-trilium-auto
<class 'type'>
```

Điều này có nghĩa:

```text-x-trilium-auto
Dog là object

Dog được tạo bởi class type
```

Có thể hình dung:

```text-x-trilium-auto
type
 │
 │ tạo ra
 ▼
Dog
```

---

# 3. Class được tạo như thế nào?

Khi Python đọc:

```text-x-trilium-auto
class Dog:
    pass
```

Nó thực hiện gần giống:

```text-x-trilium-auto
Dog = type(
    "Dog",
    (),
    {}
)
```

Giải thích:

```text-x-trilium-auto
Tên class

Dog

↓

Base classes

()

↓

Dictionary

{}
```

Đó là lý do sau này ta có thể tạo class động.

---

# 4. Instance Object

Ví dụ

```text-x-trilium-auto
class Dog:
    pass

d = Dog()
```

Điều gì xảy ra?

```text-x-trilium-auto
Dog()
```

↓

Python tạo object mới

↓

Trả về reference

```text-x-trilium-auto
d
│
▼
Dog Instance
```

Sơ đồ

```text-x-trilium-auto
           Dog (Class Object)
                 │
                 │ tạo
                 ▼
          +---------------+
d ───────▶| Dog Instance  |
          +---------------+
```

---

# 5. Mỗi instance là object riêng

```text-x-trilium-auto
class Dog:
    pass

a = Dog()
b = Dog()

print(a is b)
```

Kết quả

```text-x-trilium-auto
False
```

Sơ đồ

```text-x-trilium-auto
Dog
 │
 ├────► Instance A
 │
 └────► Instance B
```

Hai object khác nhau.

---

# 6. Class có namespace riêng

Thêm thuộc tính:

```text-x-trilium-auto
class Dog:

    species = "Canis"

    def bark(self):
        print("Woof")
```

Python lưu ở đâu?

```text-x-trilium-auto
Dog
│
▼

Namespace

{
    species : "Canis",
    bark : function
}
```

Namespace đơn giản là một **từ điển (dictionary)** lưu tên → object.

---

# 7. Xem namespace

```text-x-trilium-auto
class Dog:

    species = "Canis"

    def bark(self):
        pass

print(Dog.__dict__)
```

Kết quả (rút gọn):

```text-x-trilium-auto
{
 'species': 'Canis',
 'bark': <function ...>
}
```

Đây là namespace của class.

---

# 8. Instance cũng có namespace

```text-x-trilium-auto
class Dog:
    pass

d = Dog()

d.name = "Lucky" d.age = 3
```

Python lưu ở đâu?

```text-x-trilium-auto
Instance

{
    name : Lucky
    age : 3
}
```

Kiểm tra

```text-x-trilium-auto
print(d.__dict__)
```

Kết quả

```text-x-trilium-auto
{
    'name': 'Lucky',
    'age': 3
}
```

---

# 9. Class namespace và Instance namespace độc lập

```text-x-trilium-auto
class Dog:

    species = "Canis"

d = Dog()

d.name = "Lucky"
```

Sơ đồ

```text-x-trilium-auto
Dog Namespace

species

↓

Canis


Instance Namespace

name

↓

Lucky
```

Không nằm chung.

---

# 10. Attribute Lookup (Cơ chế tra cứu thuộc tính)

Đây là phần quan trọng nhất.

Giả sử

```text-x-trilium-auto
class Dog:

    species = "Canis"

d = Dog()
```

Ta truy cập:

```text-x-trilium-auto
print(d.species)
```

Python làm gì?

### Bước 1

Tìm trong instance

```text-x-trilium-auto
Instance

species ?

Không
```

↓

### Bước 2

Tìm trong class

```text-x-trilium-auto
Dog

species ?

Có
```

↓

Trả về

```text-x-trilium-auto
Canis
```

---

Sơ đồ

```text-x-trilium-auto
d.species

↓

Instance

↓

Không có

↓

Dog Class

↓

Có

↓

Return
```

---

# 11. Khi instance có cùng tên

```text-x-trilium-auto
class Dog:

    species = "Canis"

d = Dog()

d.species = "Wolf"

print(d.species)
```

Kết quả

```text-x-trilium-auto
Wolf
```

Python tìm

```text-x-trilium-auto
Instance

species ?

Có

↓

Dừng

↓

Không cần lên class
```

---

Sơ đồ

```text-x-trilium-auto
Instance

species

↓

Wolf

(Class bị che)
```

Hiện tượng này gọi là **shadowing (che khuất)**.

---

# 12. Ví dụ trực quan

```text-x-trilium-auto
class Student:

    school = "ABC"

s1 = Student()
s2 = Student()

s1.name = "An" s2.name = "Bình"
```

Bộ nhớ

```text-x-trilium-auto
Class

school

↓

ABC



s1

name

↓

An



s2

name

↓

Bình
```

Khi

```text-x-trilium-auto
print(s1.school)
```

Python

```text-x-trilium-auto
s1

↓

school ?

Không

↓

Student

↓

Có

↓

ABC
```

---

# 13. `__dict__` là cửa sổ nhìn vào namespace

```text-x-trilium-auto
class Student:

    school = "ABC"

    def hello(self):
        print("Hi")

s = Student()

s.name = "Nam"

print(Student.__dict__)
print(s.__dict__)
```

Kết quả (rút gọn):

```text-x-trilium-auto
Student.__dict__

{
 'school': 'ABC',
 'hello': <function ...>
}

s.__dict__

{
 'name': 'Nam'
}
```

Điều này cho thấy:

- `Student.__dict__` chứa thuộc tính và phương thức của lớp.
- `s.__dict__` chỉ chứa các thuộc tính riêng của đối tượng.

---

# 14. Tóm tắt quá trình tra cứu thuộc tính

Khi gọi:

```text-x-trilium-auto
obj.attr
```

Python (phiên bản đơn giản) thực hiện:

```text-x-trilium-auto
1. Kiểm tra obj.__dict__

↓

2. Nếu không có

↓

Kiểm tra class.__dict__

↓

3. Nếu không có

↓

Kiểm tra các class cha (theo MRO)

↓

4. Không tìm thấy

↓

AttributeError
```

> Lưu ý: Đây là mô hình đơn giản để học. Thực tế, Python còn ưu tiên **data descriptor** trước `instance.__dict__`, rồi mới đến `class.__dict__`. Chúng ta sẽ đi sâu vào điều này ở phần **Descriptor**.

---

# Ví dụ tổng hợp

```text-x-trilium-auto
class Dog:
    species = "Canis"

    def bark(self):
        print("Woof")


d = Dog()

d.name = "Lucky"

print(d.__dict__)
print(Dog.__dict__["species"])

print(d.name)
print(d.species)

d.species = "Wolf"

print(d.species)
print(Dog.species)
```

**Kết quả:**

```text-x-trilium-auto
{'name': 'Lucky'}
Canis
Lucky
Canis
Wolf
Canis
```

Điểm đáng chú ý là sau khi gán `d.species = "Wolf"`, bạn **không hề thay đổi** `Dog.species`; bạn chỉ tạo một thuộc tính mới trong namespace của `d` và nó che khuất thuộc tính cùng tên của class.

---

# Bài tập thực hành

## Bài 1

Tạo class `Car` có:

- `brand = "Toyota"`
- `country = "Japan"`

Tạo 2 instance và kiểm tra:

- `Car.__dict__`
- `instance.__dict__`

---

## Bài 2

Thêm:

```text-x-trilium-auto
car1.color = "Red" car2.color = "Blue"
```

In `__dict__` của từng instance và giải thích vì sao chúng khác nhau.

---

## Bài 3

Gán:

```text-x-trilium-auto
car1.brand = "Honda"
```

Dự đoán và kiểm tra kết quả của:

```text-x-trilium-auto
print(car1.brand)
print(car2.brand)
print(Car.brand)
```

Giải thích cơ chế **attribute lookup** và hiện tượng **shadowing**.

---

## Bài 4 (Thử thách)

Viết một hàm:

```text-x-trilium-auto
def show_namespace(obj):
    ...
```

Hàm này in ra:

- Namespace của instance (`obj.__dict__`)
- Namespace của class (`obj.__class__.__dict__`)

để quan sát trực tiếp Python lưu trữ dữ liệu ở đâu.

Ở **Buổi 3**, chúng ta sẽ đi sâu vào **vòng đời của một object**: từ lúc gọi `Dog()` cho đến khi đối tượng được tạo hoàn chỉnh, bao gồm `__new__`, `__init__`, cách cấp phát bộ nhớ và tại sao `__new__` luôn chạy trước `__init__`. Đây là kiến thức nền tảng để hiểu các framework lớn và các kỹ thuật nâng cao như Singleton, immutable object và metaclass.