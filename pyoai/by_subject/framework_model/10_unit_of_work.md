# Buổi 10 — Identity Map & Unit of Work Deep Dive

> Đây là buổi quan trọng nhất trong toàn bộ ORM Framework.

Sau buổi này, framework của bạn sẽ chuyển từ **Data Mapper đơn giản** sang **ORM hoàn chỉnh**.

Đây là hai pattern được sử dụng trong:

* SQLAlchemy ORM
* Doctrine ORM
* Hibernate
* Entity Framework

Đặc biệt, đối với **framework cào truyện** của bạn, Identity Map và Unit of Work sẽ giúp:

* Không tạo nhiều object cho cùng một truyện.
* Theo dõi chính xác các thay đổi.
* Đồng bộ hàng nghìn chapter trong **một transaction**.
* Giảm số lần truy cập SQLite.

---

# Mục tiêu

Sau buổi này, kiến trúc sẽ trở thành:

```text
                    Application
                          │
                          ▼
                       Session
                          │
        ┌─────────────────┼──────────────────┐
        ▼                 ▼                  ▼
  Identity Map      Unit of Work      Repository
        │                 │                  │
        └─────────────────┼──────────────────┘
                          ▼
                   DatabaseManager
                          │
                          ▼
                        SQLite
```

> **Điểm thay đổi lớn:** Repository sẽ không còn làm việc trực tiếp với DatabaseManager. Mọi thao tác đều đi qua **Session**.

---

# Phần I — Vấn đề nếu không có Identity Map

Giả sử:

```python
novel1 = repo.find_by_id(10)

novel2 = repo.find_by_id(10)
```

Hiện tại

```text
novel1
```

và

```text
novel2
```

là hai object khác nhau.

```python
print(id(novel1))

print(id(novel2))
```

↓

```text
140100

140880
```

---

Nếu sửa

```python
novel1.title = "AAA"
```

thì

```python
novel2.title
```

vẫn là giá trị cũ.

Rất nguy hiểm.

---

# Identity Map giải quyết

Thay vào đó

```text
Database

↓

Novel #10

↓

Identity Map

↓

Novel Object
```

Nếu lần sau hỏi lại

↓

trả về object cũ.

---

Kết quả

```python
novel1 is novel2
```

↓

```python
True
```

Đây chính là mục tiêu.

---

# Identity Map là gì?

Đơn giản chỉ là một dictionary.

```python
class IdentityMap:

    def __init__(self):

        self._objects = {}
```

---

Key

```text
(ModelClass, PrimaryKey)
```

Ví dụ

```python
(Novel, 10)
```

↓

Object.

---

Ví dụ

```python
{
    (Novel, 10): novel_object,

    (Novel, 20): novel2,

    (Chapter, 100): chapter
}
```

---

# API

```python
identity.add(obj)

identity.get(Model, pk)

identity.remove(obj)

identity.clear()
```

---

Thêm

```python
self._objects[
    (type(obj), obj.id)
] = obj
```

---

Lấy

```python
identity.get(
    Novel,
    10
)
```

↓

Nếu có

↓

trả object.

---

Nếu không

↓

Repository query SQLite.

↓

Đưa vào Identity Map.

↓

Trả object.

---

# Repository thay đổi

Trước đây

```text
Repository

↓

Database
```

Bây giờ

```text
Repository

↓

Identity Map?

↓

Có

↓

Return

↓

Không

↓

Database

↓

Identity Map

↓

Return
```

---

# Lợi ích

Ví dụ

Crawler

```text
1000 chapter
```

đều thuộc

```text
Novel #10
```

Không tạo

1000

object Novel.

Chỉ có

1

object.

Tiết kiệm RAM rất lớn.

---

# Phần II — Unit of Work

Đây là pattern lớn nhất.

Ý tưởng

↓

Không lưu ngay.

Chỉ đánh dấu.

---

Ví dụ

```python
novel.title = "AAA"
```

Không UPDATE.

Chỉ

↓

Dirty.

---

Cuối cùng

```python
session.commit()
```

mới UPDATE.

---

# UnitOfWork

Thiết kế

```python
class UnitOfWork:

    ...
```

---

Nó quản lý

```text
new

dirty

deleted
```

---

Ba tập hợp

```python
self.new = set()

self.dirty = set()

self.deleted = set()
```

---

# Object mới

```python
Novel()
```

↓

```python
uow.register_new(
    obj
)
```

---

Sau này

```python
commit()
```

↓

INSERT.

---

# Object sửa

```python
novel.title = "ABC"
```

↓

Model

↓

```python
mark_dirty()
```

↓

UnitOfWork

↓

dirty.

---

Commit

↓

UPDATE.

---

# Object xóa

```python
repo.delete(
    novel
)
```

↓

Không DELETE.

↓

register_deleted()

↓

Commit.

↓

DELETE.

---

# Commit

Commit

↓

```text
INSERT

↓

UPDATE

↓

DELETE
```

theo đúng thứ tự.

---

Ví dụ

```python
for obj in self.new:

    repository.insert(obj)
```

---

Sau đó

```python
dirty
```

↓

update.

---

Sau đó

```python
deleted
```

↓

delete.

---

Cuối cùng

↓

clear()

---

# Rollback

Nếu lỗi

↓

Không commit.

↓

clear()

↓

rollback()

---

# Session

Identity Map

*

UnitOfWork

=

Session.

---

Thiết kế

```python
class Session:

    ...
```

---

Nó chứa

```python
identity_map

unit_of_work

database
```

---

Repository

không còn nhận

```python
DatabaseManager
```

mà nhận

```python
Session
```

---

# Repository mới

```python
repo = NovelRepository(
    session
)
```

---

find_by_id()

↓

```text
Identity Map

↓

Database
```

---

save()

↓

```text
UnitOfWork

↓

register
```

---

Không INSERT ngay.

---

# Session.commit()

```python
session.commit()
```

↓

```text
BEGIN

↓

INSERT

↓

UPDATE

↓

DELETE

↓

COMMIT
```

---

Nếu lỗi

↓

```text
ROLLBACK
```

---

# Session.close()

↓

```text
clear identity

clear uow

close db
```

---

# Context Manager

Muốn

```python
with Session(...) as session:

    ...
```

↓

Tự động

```text
commit

rollback

close
```

---

Ví dụ

```python
with Session(db) as session:

    repo = NovelRepository(session)

    ...
```

---

# Session Factory

Sau này

```python
SessionFactory
```

↓

tạo Session.

---

Ví dụ

```python
session = SessionFactory.create(
    "global"
)
```

↓

DatabaseRegistry

↓

DatabaseManager

↓

Session.

---

# Workflow

```text
Application

      │

      ▼

Session

      │

      ▼

Repository

      │

      ▼

Identity Map

      │

Có?

 │       │

Có      Không

 │        │

Return   DB

           │

           ▼

 Identity Map

           ▼

Return
```

---

# Khi commit

```text
Session

↓

UnitOfWork

↓

INSERT

↓

UPDATE

↓

DELETE

↓

DatabaseManager

↓

SQLite
```

---

# Áp dụng cho Framework Cào Truyện

Ví dụ:

Crawler lấy được:

```text
Novel

↓

500 Chapter

↓

10 Author

↓

100 Tag
```

Không lưu ngay.

↓

UnitOfWork

↓

```text
new

dirty

deleted
```

↓

Cuối cùng

```python
session.commit()
```

↓

Một transaction.

Nhanh hơn rất nhiều.

---

# Tổ chức thư mục

```text
orm/

    session/

        session.py

        identity_map.py

        unit_of_work.py

        session_factory.py

    repository/

    query/

    compiler/

    expressions/

    model/

    database/
```

Đây là cấu trúc phổ biến của các ORM lớn và cũng rất phù hợp với framework của bạn.

---

# Một số cải tiến quan trọng

## 1. Identity Map nên dùng khóa bất biến

Thay vì:

```python
(type(obj), obj.id)
```

hãy chuẩn hóa thành:

```python
IdentityKey(
    model=Novel,
    database="truyenfull",
    primary_key=10
)
```

Vì trong dự án của bạn có **nhiều database nguồn**, cùng một `id=10` có thể tồn tại ở `truyenfull.db` và `tangthuvien.db`. Database cũng phải là một phần của khóa.

---

## 2. UnitOfWork nên dùng `dict` thay vì `set`

Thay vì:

```python
self.dirty = set()
```

nên dùng:

```python
self.dirty = {
    identity_key: model
}
```

Điều này:

* Không bị trùng đối tượng.
* Tra cứu nhanh.
* Dễ đồng bộ với Identity Map.

---

## 3. Repository chỉ đăng ký thay đổi

Repository không gọi:

```python
UPDATE
```

ngay.

Thay vào đó:

```python
session.uow.register_dirty(model)
```

Toàn bộ SQL chỉ được phát sinh khi:

```python
session.commit()
```

Đây chính là tinh thần của Unit of Work.

---

## 4. Transaction bao trùm toàn bộ Commit

```text
BEGIN

↓

INSERT tất cả object mới

↓

UPDATE tất cả object thay đổi

↓

DELETE tất cả object bị xóa

↓

COMMIT
```

Nếu bất kỳ bước nào lỗi:

```text
ROLLBACK
```

Toàn bộ transaction sẽ bị hủy, giúp dữ liệu luôn nhất quán.

---

# Bài tập thực hành

## Bài 1

Viết `IdentityMap` với các phương thức:

* `add()`
* `get()`
* `remove()`
* `clear()`

và sử dụng `IdentityKey`.

---

## Bài 2

Viết `UnitOfWork` quản lý:

* `register_new()`
* `register_dirty()`
* `register_deleted()`

và triển khai `commit()` theo đúng thứ tự:

1. INSERT
2. UPDATE
3. DELETE

---

## Bài 3

Xây dựng `Session`:

* chứa `IdentityMap`
* chứa `UnitOfWork`
* làm context manager (`with Session(...)`)

---

## Bài 4

Sửa `BaseRepository` để:

* `find_by_id()` ưu tiên lấy từ `IdentityMap`
* `save()` chỉ đăng ký với `UnitOfWork`

---

## Bài 5

Tích hợp với dự án cào truyện:

* Một `Session` cho `global.db`
* Một `Session` cho mỗi database nguồn
* Kiểm tra rằng cùng một truyện được đọc nhiều lần trong cùng Session chỉ tạo **một object Model duy nhất**.

---

# Buổi tiếp theo

**Buổi 11 — Relationship Mapping Deep Dive**

Đây là buổi chúng ta sẽ xây dựng hệ thống quan hệ giữa các model:

* `ForeignKey`
* `OneToOne`
* `OneToMany`
* `ManyToMany`
* Lazy Loading
* Eager Loading
* `select_related()`
* `prefetch_related()`
* Cascade Delete
* Back Reference (`novel.chapters`, `chapter.novel`)

Sau buổi này, framework ORM của bạn sẽ có khả năng mô hình hóa đầy đủ cấu trúc dữ liệu của ứng dụng đọc truyện và crawler, tương tự các ORM hiện đại như Django ORM hoặc SQLAlchemy.
