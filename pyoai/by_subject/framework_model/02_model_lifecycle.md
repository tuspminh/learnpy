# Buổi 2 — Model Lifecycle & Hooks Deep Dive

> Đây là buổi tiếp theo trong series **Model Framework Deep Dive**. Sau buổi này, model của chúng ta sẽ có **vòng đời (Lifecycle)** tương tự như Django ORM, SQLAlchemy ORM hay Pydantic.

---

# Mục tiêu

Sau buổi này bạn sẽ tự xây dựng được:

```
Application

        │

        ▼

Repository.save()

        │

        ▼

before_validate()

        │

        ▼

validate()

        │

        ▼

after_validate()

        │

        ▼

before_insert()
          hoặc
before_update()

        │

        ▼

Database

        │

        ▼

after_insert()
          hoặc
after_update()

        │

        ▼

after_save()
```

Đây chính là **Lifecycle của Model**.

---

# Hook là gì?

Hook là các hàm được framework gọi **tự động** tại những thời điểm xác định.

Ví dụ:

```
save()

↓

before_save()

↓

INSERT

↓

after_save()
```

Bạn không cần gọi `before_save()`.

Framework sẽ gọi.

---

Ví dụ:

```python
novel.save()
```

Framework:

```python
novel.before_save()

database.insert()

novel.after_save()
```

---

# Vì sao cần Hook?

Ví dụ

Khi lưu truyện.

Bạn muốn:

* sinh slug
* cập nhật updated_at
* validate
* ghi log

Nếu không có hook

```python
novel.make_slug()

novel.validate()

novel.updated_at = ...

repository.save()
```

Code sẽ lặp lại rất nhiều.

Hook giải quyết vấn đề này.

---

# Thiết kế BaseModel

```python
class BaseModel:
    def before_validate(self):
        pass

    def after_validate(self):
        pass

    def before_save(self):
        pass

    def after_save(self):
        pass

    def before_delete(self):
        pass

    def after_delete(self):
        pass
```

Đây là lớp cha.

---

Model con

```python
class Novel(BaseModel):
    def before_save(self):
        print("Generating slug...")
```

---

# Repository gọi Hook

Ví dụ

```python
class Repository:
    def save(self, model):

        model.before_save()

        print("Saving database...")

        model.after_save()
```

---

Kết quả

```
Generating slug...

Saving database...

...
```

---

# Hook Validation

Repository

```python
class Repository:
    def save(self, model):

        model.before_validate()

        model.validate()

        model.after_validate()

        ...
```

---

Ví dụ

```python
class Novel(BaseModel):
    def before_validate(self):

        print("Normalize title")
```

---

Kết quả

```
Normalize title

Validate

Save
```

---

# Normalize Data

Ví dụ

User nhập

```
"   Đấu Phá Thương Khung    "
```

Không nên lưu nguyên.

before_validate()

```python
class Novel(BaseModel):
    def before_validate(self):

        self.title = self.title.strip()
```

---

Sau đó

```
Đấu Phá Thương Khung
```

được validate.

---

# Sinh Slug

Ví dụ

```
Đấu Phá Thương Khung
```

↓

```
dau-pha-thuong-khung
```

Hook

```python
class Novel(BaseModel):
    def before_save(self):

        self.slug = self.title.lower().replace(" ", "-")
```

---

# Auto Timestamp

before_save

```python
from datetime import datetime


class Novel(BaseModel):
    def before_save(self):

        self.updated_at = datetime.now()
```

Không cần nhớ cập nhật.

---

# after_save()

Ví dụ

Bạn muốn

* ghi log

* clear cache

* gửi event

Hook

```python
class Novel(BaseModel):
    def after_save(self):

        print("Saved")
```

---

Repository

```
INSERT

↓

after_save()
```

---

# before_insert()

Model mới

```
id=None
```

↓

INSERT

---

Model cũ

```
id=10
```

↓

UPDATE

Hai trường hợp khác nhau.

---

Repository

```python
if model.id is None:
    model.before_insert()

else:
    model.before_update()
```

---

BaseModel

```python
class BaseModel:
    def before_insert(self):
        pass

    def after_insert(self):
        pass

    def before_update(self):
        pass

    def after_update(self):
        pass
```

---

Ví dụ

```python
class Novel(BaseModel):
    def before_insert(self):

        print("New Novel")
```

---

# before_delete()

Ví dụ

Bạn muốn

```
xóa file ảnh

↓

xóa chapter cache

↓

xóa database
```

---

Hook

```python
class Novel(BaseModel):
    def before_delete(self):

        print("Remove cover image")
```

---

Repository

```python
model.before_delete()

DELETE

model.after_delete()
```

---

# before_load()

Đọc database

```
SQLite

↓

dict

↓

Model
```

Có thể cần xử lý.

---

Ví dụ

Database

```
title

"đấu phá thương khung"
```

Sau load

```
Đấu Phá Thương Khung
```

---

Hook

```python
class Novel(BaseModel):
    def after_load(self):

        self.title = self.title.title()
```

---

# Hook cho Serialization

Ví dụ

```
Model

↓

to_dict()

↓

JSON
```

Có thể

```
before_export()

after_export()
```

---

Ví dụ

```python
class Novel(BaseModel):
    def before_export(self):

        print("Preparing json...")
```

---

# Hook Chain

Một lần save

```
save()

↓

before_validate()

↓

validate()

↓

after_validate()

↓

before_save()

↓

before_insert()

↓

INSERT

↓

after_insert()

↓

after_save()
```

---

Nếu update

```
save()

↓

before_validate()

↓

validate()

↓

after_validate()

↓

before_save()

↓

before_update()

↓

UPDATE

↓

after_update()

↓

after_save()
```

---

# Một Lifecycle hoàn chỉnh

```python
class BaseModel:
    def before_validate(self):
        pass

    def after_validate(self):
        pass

    def before_save(self):
        pass

    def after_save(self):
        pass

    def before_insert(self):
        pass

    def after_insert(self):
        pass

    def before_update(self):
        pass

    def after_update(self):
        pass

    def before_delete(self):
        pass

    def after_delete(self):
        pass

    def before_load(self):
        pass

    def after_load(self):
        pass
```

---

# Repository hoàn chỉnh

```python
class Repository:
    def save(self, model):

        model.before_validate()

        model.validate()

        model.after_validate()

        model.before_save()

        if model.id is None:
            model.before_insert()

            print("INSERT")

            model.after_insert()

        else:
            model.before_update()

            print("UPDATE")

            model.after_update()

        model.after_save()
```

---

# Ví dụ thực tế

```python
class Novel(BaseModel):
    def before_validate(self):

        self.title = self.title.strip()

    def validate(self):

        if not self.title:
            raise ValueError("Title empty")

    def before_save(self):

        self.slug = self.title.lower().replace(" ", "-")

    def before_insert(self):

        print("Create new novel")

    def after_save(self):

        print("Novel saved")
```

---

Khi gọi

```python
repo.save(novel)
```

Kết quả

```
before_validate

↓

validate

↓

after_validate

↓

before_save

↓

before_insert

↓

INSERT

↓

after_insert

↓

after_save
```

---

# Hook có nên gọi trực tiếp?

Không.

Sai:

```python
novel.before_save()
```

Đúng:

```python
repo.save(novel)
```

Repository là nơi điều phối toàn bộ vòng đời của model.

---

# Lợi ích của Lifecycle

* **Tách biệt trách nhiệm**: Repository quản lý quy trình, Model quản lý hành vi của chính nó.
* **Dễ mở rộng**: Thêm xử lý mới mà không sửa luồng `save()`.
* **Tái sử dụng**: Mọi model đều dùng chung vòng đời.
* **Kiểm thử dễ dàng**: Có thể kiểm tra từng hook độc lập.
* **Giảm lặp mã**: Không cần nhớ gọi validate, sinh slug hay cập nhật timestamp ở nhiều nơi.

---

# Sơ đồ Lifecycle đầy đủ

```text
                    save()
                       │
                       ▼
            before_validate()
                       │
                       ▼
                 validate()
                       │
                       ▼
             after_validate()
                       │
                       ▼
               before_save()
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
before_insert()                before_update()
        │                             │
        ▼                             ▼
     INSERT                        UPDATE
        │                             │
        ▼                             ▼
 after_insert()               after_update()
        └──────────────┬──────────────┘
                       ▼
                 after_save()

----------------------------------------------

                  delete()
                       │
                       ▼
              before_delete()
                       │
                       ▼
                    DELETE
                       │
                       ▼
               after_delete()

----------------------------------------------

                  load()
                       │
                       ▼
               before_load()
                       │
                       ▼
                Read Database
                       │
                       ▼
                Mapping Model
                       │
                       ▼
                after_load()
```

---

# Bài tập thực hành

## Bài 1

Xây dựng `BaseModel` với đầy đủ 12 hook:

* `before_validate()`
* `after_validate()`
* `before_save()`
* `after_save()`
* `before_insert()`
* `after_insert()`
* `before_update()`
* `after_update()`
* `before_delete()`
* `after_delete()`
* `before_load()`
* `after_load()`

---

## Bài 2

Viết `Repository.save()` thực hiện đúng chuỗi lifecycle cho cả **INSERT** và **UPDATE**.

---

## Bài 3

Tạo model `Novel`:

* `before_validate()` chuẩn hóa `title` bằng `strip()`.
* `validate()` kiểm tra `title` không rỗng.
* `before_save()` sinh `slug`.
* `before_insert()` gán `created_at`.
* `before_update()` cập nhật `updated_at`.
* `after_save()` ghi log `"Novel saved"`.

---

## Bài 4

Thêm model `Chapter` có lifecycle tương tự và kiểm tra bằng cách gọi `repo.save()` với cả bản ghi mới và bản ghi đã có `id`.

---

## Buổi tiếp theo

**Buổi 3 — Descriptor & Field Deep Dive**

Đây là phần cốt lõi để biến `Field` từ một lớp chỉ chứa metadata thành **descriptor** thực thụ. Chúng ta sẽ tìm hiểu:

* Descriptor Protocol (`__get__`, `__set__`, `__delete__`)
* `__set_name__()`
* Quản lý dữ liệu nội bộ (`instance.__dict__`)
* Validation tự động khi gán giá trị
* Lazy loading
* Read-only field
* Computed field bằng descriptor

Sau buổi này, `Field` của framework sẽ hoạt động gần giống các trường trong Django ORM hoặc SQLAlchemy.
