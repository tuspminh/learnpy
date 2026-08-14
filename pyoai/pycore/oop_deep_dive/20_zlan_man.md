Bạn nói đúng. Tôi đã **đi lệch roadmap gốc** từ Buổi 19 trở đi.

Cụ thể, roadmap bạn xác lập là:

* Buổi 14 → `__str__`, `__repr__`, `__format__`
* Buổi 15 → Operator Overloading
* Buổi 16 → Comparison
* Buổi 17 → Container Protocol
* Buổi 18 → Context Manager
* Buổi 19 → Callable Object
* **Buổi 20 → Attribute Access**
* **Buổi 21 → Descriptor Protocol**
* Buổi 22 → Property thực chất hoạt động thế nào
* Buổi 23 → Method cũng là Descriptor
* Buổi 24 → ORM sử dụng Descriptor

Trong khi tôi đã dạy:

* Buổi 20 → Magic Methods tổng hợp
* Buổi 21 → Container
* Buổi 22 → Operator Overloading
* Buổi 23 → Callable + Context Manager

Như vậy phần **Magic Methods đã bị dạy lại và quan trọng hơn là đã bỏ qua Descriptor**.

## Chúng ta sửa roadmap từ đây

Tôi sẽ **không bắt bạn học lại từ Buổi 20**. Những nội dung bạn đã học vẫn giữ lại như kiến thức bổ sung.

Ta quay về đúng vị trí roadmap:

### Buổi 20 — Attribute Access

* `__getattribute__`
* `__getattr__`
* `__setattr__`
* `__delattr__`
* `__dir__`
* Attribute lookup thực sự diễn ra thế nào
* `object.__getattribute__()`
* Tránh recursion khi override `__getattribute__`
* Proxy Object
* Lazy Loading
* Attribute interception

### **Buổi 21 — Descriptor Protocol**

Đây mới là **Buổi 21 đúng roadmap**.

Ta sẽ học từ nền tảng:

```python
__get__
__set__
__delete__
```

và đặc biệt hiểu sâu:

```text
obj.attr
   ↓
object.__getattribute__(obj, "attr")
   ↓
Descriptor?
   ↓
__get__
```

Sau đó mới đi đến:

* Data Descriptor
* Non-data Descriptor
* Thứ tự ưu tiên Attribute Lookup
* Descriptor + instance `__dict__`
* Descriptor + class `__dict__`
* `__set_name__`
* Tự viết `Field`
* Tự viết `ValidatedField`
* Tự viết `LazyField`

Rồi:

### Buổi 22

`property` thực chất là Descriptor như thế nào.

### Buổi 23

Method thực chất cũng là Descriptor:

```python
obj.method
```

liên quan trực tiếp đến:

```python
function.__get__(obj, type(obj))
```

và từ đó giải thích được **bound method** mà chúng ta đã đề cập ở Buổi 5.

### Buổi 24

Dùng Descriptor xây dựng mô hình ORM:

```python
class User(Model):

    id = IntegerField()
    name = StringField()
    age = IntegerField()
```

để hiểu sâu cách ORM biến:

```python
user.name
```

thành logic truy cập dữ liệu phía sau.

---

## Vì vậy, bài tiếp theo của chúng ta sẽ là

# **Buổi 21 — Descriptor Protocol Deep Dive**

Tôi sẽ dạy **đúng roadmap bạn vừa đưa**, không tự ý thay đổi thứ tự nữa.

Và từ đây tôi sẽ giữ nguyên số buổi **21 → 50** theo roadmap này.
