Pydantic là thư viện xử lý và xác thực dữ liệu (data validation) phổ biến nhất trong Python, đặc biệt khi làm việc với **FastAPI** hoặc các hệ thống nhận/gửi dữ liệu JSON.

Điểm cốt lõi của Pydantic là bạn dùng **Type Hints** của Python để định nghĩa kiểu dữ liệu. Pydantic sẽ tự động ép kiểu (coerce), kiểm tra lỗi và chuyển đổi dữ liệu cho bạn.

---

### 1. Cài đặt

Mở terminal và cài đặt phiên bản Pydantic v2:

```bash
pip install pydantic

```

---

### 2. Ví dụ cơ bản đầu tiên

Tạo một Model bằng cách kế thừa từ `BaseModel`.

```python
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool = True  # Giá trị mặc định


# 1. Dữ liệu hợp lệ (Pydantic tự động ép kiểu "123" thành int 123)
user_data = {"id": "123", "name": "Nguyen Van A", "email": "a@example.com"}

user = User(**user_data)
print(user.id)  # Kết quả: 123 (kiểu int)
print(user.is_active)  # Kết quả: True

# 2. Xuất dữ liệu ra Dictionary hoặc JSON
print(user.model_dump())  # Dạng dict
print(user.model_dump_json())  # Dạng JSON string
```

---

### 3. Các tính năng quan trọng

#### A. Ràng buộc dữ liệu với `Field`

Bạn có thể giới hạn độ dài chuỗi, khoảng giá trị số hoặc thêm mô tả bằng `Field`.

```python
from pydantic import BaseModel, Field


class Product(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    price: float = Field(gt=0, description="Giá phải lớn hơn 0")  # gt = greater than
    stock: int = Field(default=0, ge=0)  # ge = greater or equal


# Lỗi nếu price <= 0 hoặc name quá ngắn
p = Product(name="A", price=-10)  # Sẽ báo ValidationError
```

#### B. Kiểm tra logic tùy chỉnh với `@field_validator`

Khi cần kiểm tra điều kiện phức tạp hơn kiểu dữ liệu cơ bản.

```python
from pydantic import BaseModel, field_validator


class RegisterForm(BaseModel):
    username: str
    age: int

    @field_validator("username")
    @classmethod
    def username_must_not_contain_space(cls, v: str) -> str:
        if " " in v:
            raise ValueError("Username không được chứa khoảng trắng")
        return v.lower()  # Có thể biến đổi dữ liệu trước khi lưu
```

#### C. Lớp lồng nhau (Nested Models)

Pydantic hỗ trợ cấu trúc dữ liệu phức tạp nhiều tầng.

```python
from typing import List
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float


class Order(BaseModel):
    order_id: int
    items: List[Item]


# Khởi tạo Order từ dict phức tạp
order_data = {
    "order_id": 101,
    "items": [{"name": "Bàn phím", "price": 50.0}, {"name": "Chuột", "price": 25.5}],
}

order = Order(**order_data)
print(order.items[0].name)  # Bàn phím
```

---

### 4. Xử lý lỗi (ValidationError)

Khi dữ liệu không hợp lệ, Pydantic sẽ ném ra ngoại lệ `ValidationError` chứa chi tiết lý do sai.

```python
from pydantic import BaseModel, ValidationError


class User(BaseModel):
    id: int
    email: str


try:
    user = User(id="abc", email="test")
except ValidationError as e:
    print(e.json())  # Trả về JSON mô tả chi tiết trường nào bị lỗi
```