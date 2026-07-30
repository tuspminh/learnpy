Version:0.9 StartHTML:0000000105 EndHTML:0000029434 StartFragment:0000000141 EndFragment:0000029398 

# Typing Deep Dive – Buổi 9

# `Self` (PEP 673) – Fluent API, Builder Pattern và Method Chaining

> ⭐⭐⭐⭐ Đây là một trong những tính năng đẹp nhất của Python 3.11.
> 
> Trước Python 3.11, việc biểu diễn "phương thức trả về chính đối tượng hiện tại" khá dài dòng và dễ sai. `Self` ra đời để giải quyết vấn đề đó.

* * *

# Mục tiêu

Sau buổi học này bạn sẽ:

  * Hiểu `Self` là gì.
  * Biết tại sao `Self` được thêm vào Python.
  * Phân biệt `Self` và `TypeVar`.
  * Xây dựng Fluent API.
  * Xây dựng Builder Pattern.
  * Hiểu cách `Self` hoạt động với kế thừa.



* * *

# 1\. Bài toán

Giả sử có class
    
    
    class Query:
    
        def where(self):
            return self
    
        def order_by(self):
            return self
    
        def limit(self):
            return self

Muốn viết
    
    
    query = (
        Query()
            .where()
            .order_by()
            .limit()
    )

Đây gọi là

> Method Chaining

* * *

# 2\. Không có Type Hint
    
    
    class Query:
    
        def where(self):
            return self

IDE biết
    
    
    where()
    
    ↓
    
    ???
    

Không rõ kiểu trả về.

Autocomplete sẽ kém.

* * *

# 3\. Cách cũ (trước Python 3.11)

Ta phải dùng
    
    
    from typing import TypeVar
    
    T = TypeVar(
        "T",
        bound="Query"
    )

Sau đó
    
    
    class Query:
    
        def where(
            self: T
        ) -> T:
    
            return self

Hoạt động.

Nhưng khá dài.

* * *

# 4\. Self

Python 3.11
    
    
    from typing import Self

Viết
    
    
    from typing import Self
    
    
    class Query:
    
        def where(self) -> Self:
            return self

Đơn giản hơn rất nhiều.

* * *

# 5\. Ví dụ hoàn chỉnh
    
    
    from typing import Self
    
    
    class Query:
    
        def where(self) -> Self:
            print("WHERE")
            return self
    
        def order_by(self) -> Self:
            print("ORDER")
            return self
    
        def limit(self) -> Self:
            print("LIMIT")
            return self

Dùng
    
    
    query = (
        Query()
            .where()
            .order_by()
            .limit()
    )

IDE hiểu
    
    
    Query

ở mọi bước.

* * *

# 6\. Self hoạt động như thế nào?

Ví dụ
    
    
    class Query:
    
        def where(self) -> Self:
            return self

Có thể tưởng tượng

IDE biến nó thành
    
    
    T = TypeVar(
        "T",
        bound=Query
    )
    
    def where(
        self: T
    ) -> T:
        ...

Đây chỉ là cách hình dung; `Self` không thực sự được triển khai bằng cách thay thế mã nguồn như vậy.

* * *

# 7\. Self với kế thừa

Ví dụ
    
    
    class Animal:
    
        def rename(
            self,
            name: str
        ) -> Self:
    
            self.name = name
    
            return self

Subclass
    
    
    class Dog(Animal):
    
        def bark(self):
            print("Woof")

Dùng
    
    
    dog = (
        Dog()
            .rename("Lucky")
    )

IDE hiểu
    
    
    Dog

Không phải
    
    
    Animal

* * *

# 8\. Nếu không dùng Self
    
    
    class Animal:
    
        def rename(
            self,
            name: str
        ) -> Animal:
    
            return self

Thì
    
    
    dog = Dog()
    
    dog.rename("Lucky")

IDE

↓
    
    
    Animal

Không gọi được
    
    
    dog.rename(
        "Lucky"
    ).bark()

Autocomplete mất.

* * *

# 9\. Self giữ nguyên subclass

Đây là ưu điểm lớn nhất.
    
    
    Dog
    
    ↓
    
    rename()
    
    ↓
    
    Dog

Không bị ép thành
    
    
    Animal

* * *

# 10\. Fluent API

Đây là mẫu thiết kế rất phổ biến.

Ví dụ
    
    
    class Config:
    
        def host(
            self,
            host: str
        ) -> Self:
            ...
    
        def port(
            self,
            port: int
        ) -> Self:
            ...
    
        def timeout(
            self,
            timeout: int
        ) -> Self:
            ...

Dùng
    
    
    config = (
        Config()
            .host("localhost")
            .port(8080)
            .timeout(30)
    )

Rất đẹp.

* * *

# 11\. Builder Pattern

Ví dụ
    
    
    from typing import Self
    
    
    class UserBuilder:
    
        def name(
            self,
            name: str
        ) -> Self:
    
            self._name = name
    
            return self
    
        def age(
            self,
            age: int
        ) -> Self:
    
            self._age = age
    
            return self
    
        def build(self):
            return {
                "name": self._name,
                "age": self._age
            }

Sử dụng
    
    
    user = (
        UserBuilder()
            .name("Alice")
            .age(20)
            .build()
    )

* * *

# 12\. SQLAlchemy

SQLAlchemy dùng Fluent API.

Ví dụ
    
    
    select(User)\
    .where(User.id == 1)\
    .order_by(User.name)\
    .limit(10)

Nếu không có kiểu trả về chính xác

Autocomplete sẽ rất tệ.

* * *

# 13\. Requests

Ví dụ giả định
    
    
    client\
    .set_timeout(30)\
    .set_proxy(...)\
    .set_retry(5)

Đây cũng là Fluent API.

* * *

# 14\. PySide6

Ví dụ tự xây
    
    
    window\
    .set_title("Demo")\
    .resize(800,600)\
    .show_toolbar()

Đây cũng là ứng dụng của
    
    
    Self

* * *

# 15\. Self trong Dataclass
    
    
    from dataclasses import dataclass from typing import Self
    
    
    @dataclass class User:
    
        name: str
    
        def rename(
            self,
            new_name: str
        ) -> Self:
    
            self.name = new_name
    
            return self

Dùng
    
    
    user = (
        User("Alice")
            .rename("Bob")
    )

IDE

↓
    
    
    User

* * *

# 16\. Self trong Generic

Ví dụ
    
    
    class Box[T]:
    
        def reset(self) -> Self:
            ...

`Self`

không thay thế
    
    
    T

Mà thay thế
    
    
    Box[T]

Nếu
    
    
    IntBox(Box[int])

Thì
    
    
    reset()

trả về
    
    
    IntBox

* * *

# 17\. Self KHÔNG dùng cho hàm bình thường

Sai
    
    
    def clone(
        obj
    ) -> Self:
        ...

`Self`

chỉ hợp lệ bên trong ngữ cảnh của lớp (class), nơi nó có ý nghĩa là "kiểu của chính đối tượng hiện tại".

* * *

# 18\. Self trong Classmethod

Ví dụ
    
    
    from typing import Self
    
    
    class User:
    
        @classmethod
        def create(cls) -> Self:
            return cls()

Subclass
    
    
    class Admin(User):
        pass

Dùng
    
    
    admin = Admin.create()

IDE hiểu
    
    
    Admin

Không phải
    
    
    User

* * *

# 19\. Self và Factory

Ví dụ
    
    
    class BaseModel:
    
        @classmethod
        def from_json(
            cls,
            text: str
        ) -> Self:
    
            ...

Nếu
    
    
    User.from_json(...)

↓
    
    
    User

Nếu
    
    
    Book.from_json(...)

↓
    
    
    Book

Đây là kỹ thuật được rất nhiều ORM và thư viện serialization sử dụng.

* * *

# 20\. So sánh

## Self
    
    
    def rename(...) -> Self

↓

trả về
    
    
    chính subclass hiện tại

* * *

## TypeVar
    
    
    T = TypeVar(...)

↓

Generic

* * *

## object
    
    
    object

↓

mất thông tin kiểu.

* * *

# 21\. Best Practices

✔ Dùng `Self` cho các phương thức trả về `self`.

✔ Dùng `Self` cho các `@classmethod` tạo đối tượng bằng `cls()`.

✔ Dùng `Self` khi xây dựng Fluent API hoặc Builder Pattern.

✔ Dùng `TypeVar` khi biểu diễn mối quan hệ giữa nhiều tham số hoặc giữa tham số và kiểu trả về trong Generic.

❌ Không dùng `Self` cho hàm độc lập (không thuộc class).

* * *

# Áp dụng vào dự án crawler truyện

Giả sử bạn có một `CrawlerConfig`:
    
    
    from typing import Self
    
    class CrawlerConfig:
        def user_agent(self, ua: str) -> Self:
            self._ua = ua
            return self
    
        def timeout(self, seconds: int) -> Self:
            self._timeout = seconds
            return self
    
        def max_workers(self, workers: int) -> Self:
            self._workers = workers
            return self

Bạn có thể cấu hình rất tự nhiên:
    
    
    config = (
        CrawlerConfig()
            .user_agent("Mozilla/5.0")
            .timeout(15)
            .max_workers(8)
    )

Nếu sau này tạo:
    
    
    class TruyenFullConfig(CrawlerConfig):
        def category(self, name: str) -> Self:
            self._category = name
            return self

Thì:
    
    
    cfg = (
        TruyenFullConfig()
            .timeout(10)
            .category("Tiên Hiệp")
    )

IDE vẫn biết `cfg` là `TruyenFullConfig`, không bị "rơi" về `CrawlerConfig`.

* * *

# Bài tập

## Bài 1

Viết lớp:
    
    
    class Person:

Có:

  * `set_name(name) -> Self`
  * `set_age(age) -> Self`



Sau đó viết:
    
    
    person = (
        Person()
            .set_name("Alice")
            .set_age(20)
    )

* * *

## Bài 2

Viết `DatabaseConfig`

Có các phương thức:

  * `host()`
  * `port()`
  * `database()`
  * `username()`
  * `password()`



Tất cả đều trả về `Self`.

* * *

## Bài 3

Tạo:
    
    
    class Animal:

Có:
    
    
    rename() -> Self

Sau đó:
    
    
    class Dog(Animal):
        def bark(self):
            ...

Kiểm tra rằng:
    
    
    Dog().rename("Lucky").bark()

được IDE nhận diện đúng kiểu mà không cần ép kiểu.

* * *

# Tổng kết

Đến đây, bạn đã làm chủ gần như toàn bộ nền tảng **Generic và Self** trong `typing`:

  * Type Hint cơ bản
  * Collection Types
  * `Union`, `Optional`, `Literal`
  * `Any`, `object`, `Never`, `NoReturn`
  * Type Alias
  * `TypeVar`
  * Generic Function/Class
  * Bound & Constraint
  * Variance
  * `Self`



Đây là nền tảng để bước sang giai đoạn tiếp theo: **typing cho hàm và decorator**.

**Buổi 10** sẽ bắt đầu với `**Callable**`, nơi bạn sẽ học cách mô tả kiểu của hàm, lambda, callback và chuẩn bị cho các chủ đề nâng cao như `**ParamSpec**` và `**Concatenate**`, vốn rất quan trọng khi xây dựng decorator chuyên nghiệp.

