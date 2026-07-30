Version:0.9 StartHTML:0000000105 EndHTML:0000031191 StartFragment:0000000141 EndFragment:0000031155 

# Typing Deep Dive – Buổi 8

# TypeVar nâng cao - Bound, Constrained TypeVar và Variance

> ⭐⭐⭐⭐⭐ **Đây là buổi học khó nhất của toàn bộ phần Generic.**
> 
> Ngay cả nhiều lập trình viên Python có kinh nghiệm cũng thường hiểu chưa đúng về:
> 
>   * `bound`
>   * `constraints`
>   * `covariance`
>   * `contravariance`
>   * `invariance`
> 

> 
> Sau buổi này, bạn sẽ có thể đọc hiểu mã nguồn của các thư viện lớn như **SQLAlchemy** , **FastAPI** , **Pydantic** , **Trio** , **asyncio** ,...

* * *

# Mục tiêu

Sau buổi học này bạn sẽ hiểu:

  * `TypeVar(bound=...)`
  * Constrained TypeVar
  * Covariance
  * Contravariance
  * Invariance
  * Tại sao `list[Dog]` không phải `list[Animal]`
  * Tại sao `Sequence[Dog]` lại là `Sequence[Animal]`



* * *

# Phần I - Bound TypeVar

* * *

# 1\. Tại sao cần Bound?

Giả sử
    
    
    class Animal:
        def speak(self):
            print("Animal")
    
    
    class Dog(Animal):
        def bark(self):
            print("Woof")
    
    
    class Cat(Animal):
        def meow(self):
            print("Meow")

Ta muốn viết
    
    
    def clone(obj):
        ...

Hàm này chỉ làm việc với Animal.

Không muốn
    
    
    clone(100)

hay
    
    
    clone("Python")

* * *

# 2\. Bound
    
    
    from typing import TypeVar
    
    T = TypeVar(
        "T",
        bound=Animal
    )

Ý nghĩa
    
    
    T
    
    ↓
    
    Animal hoặc subclass của Animal

* * *

# 3\. Ví dụ
    
    
    from typing import TypeVar
    
    T = TypeVar(
        "T",
        bound=Animal
    )
    
    
    def clone(obj: T) -> T:
        return obj

Được phép
    
    
    clone(Dog())
    
    clone(Cat())

Không được
    
    
    clone(10)

IDE báo lỗi.

* * *

# 4\. IDE suy luận

Nếu
    
    
    dog = Dog()
    
    x = clone(dog)

IDE hiểu
    
    
    T
    
    ↓
    
    Dog

Return

↓
    
    
    Dog

Không phải
    
    
    Animal

Đây là ưu điểm cực lớn của Bound.

* * *

# 5\. Nếu không dùng Bound
    
    
    def clone(
        obj: Animal
    ) -> Animal:
        return obj

Kết quả
    
    
    dog = Dog()
    
    x = clone(dog)

IDE

↓
    
    
    Animal

Mất thông tin
    
    
    Dog

Không gọi được
    
    
    x.bark()

* * *

Bound giữ nguyên kiểu cụ thể.

* * *

# Phần II - Constrained TypeVar

* * *

# 6\. Constraint là gì?

Ví dụ
    
    
    T = TypeVar(
        "T",
        int,
        float
    )

Ý nghĩa
    
    
    T
    
    ↓
    
    chỉ được
    
    int
    
    hoặc
    
    float

* * *

Ví dụ
    
    
    T = TypeVar(
        "T",
        str,
        bytes
    )

Được
    
    
    str
    
    bytes

Không được
    
    
    list

* * *

# 7\. Ví dụ
    
    
    T = TypeVar(
        "T",
        str,
        bytes
    )
    
    
    def concat(
        a: T,
        b: T
    ) -> T:
    
        return a + b

Được
    
    
    concat(
        "A",
        "B"
    )

Được
    
    
    concat(
        b"A",
        b"B"
    )

Không được
    
    
    concat(
        "A",
        b"B"
    )

IDE báo lỗi vì hai tham số phải cùng một kiểu `T`.

* * *

# 8\. Bound vs Constraint

Bound
    
    
    bound=Animal

↓
    
    
    Animal
    
    Dog
    
    Cat
    
    ...

* * *

Constraint
    
    
    int
    
    float

↓

chỉ
    
    
    int
    
    hoặc
    
    float

Không subclass khác ngoài tập được chỉ định.

* * *

# Phần III - Variance

Đây là phần khó nhất.

* * *

# 9\. Kế thừa
    
    
    Animal

↓
    
    
    Dog

Có nghĩa
    
    
    Dog
    
    IS-A
    
    Animal

Không có vấn đề.

* * *

# 10\. Nhưng

Có phải
    
    
    list[Dog]
    
    IS-A
    
    list[Animal]

không?

Đa số người mới sẽ trả lời

> Có.

Đáp án

> Không.

* * *

# 11\. Ví dụ
    
    
    dogs: list[Dog] = [
        Dog()
    ]

Nếu
    
    
    animals: list[Animal] = dogs

Được phép.

Thì
    
    
    animals.append(
        Cat()
    )

Lúc này
    
    
    dogs

chứa
    
    
    Dog
    
    Cat

Danh sách "chó" lại có "mèo".

Điều này phá vỡ tính đúng đắn của kiểu dữ liệu.

* * *

Đó là lý do
    
    
    list
    
    ↓
    
    Invariant

* * *

# 12\. Invariance
    
    
    list[Dog]
    
    ≠
    
    list[Animal]

Không chuyển đổi được.

* * *

# 13\. Sequence

Khác với list

Sequence

chỉ đọc.

Không có
    
    
    append()

Không có
    
    
    extend()

Không có
    
    
    insert()

* * *

Ví dụ
    
    
    from collections.abc import Sequence
    
    dogs: Sequence[Dog]

Có thể
    
    
    animals: Sequence[
        Animal
    ] = dogs

Được phép.

* * *

Vì

Sequence

không sửa dữ liệu.

Không thể thêm
    
    
    Cat()

* * *

Đó gọi là

Covariance.

* * *

# 14\. Covariance

Có nghĩa
    
    
    Dog
    
    ↓
    
    Animal

thì
    
    
    Sequence[Dog]
    
    ↓
    
    Sequence[Animal]

Cũng đúng.

* * *

# 15\. Khai báo Covariant
    
    
    T_co = TypeVar(
        "T_co",
        covariant=True
    )

Ví dụ
    
    
    class Reader(
        Generic[T_co]
    ):
        ...

* * *

Reader chỉ
    
    
    đọc

Không ghi.

Nên

Covariant.

* * *

# 16\. Contravariance

Ngược lại.

Ví dụ
    
    
    class AnimalTrainer:
    
        def train(
            animal: Animal
        ):
            ...

Trainer có thể huấn luyện
    
    
    Dog
    
    Cat
    
    Bird

Nếu nơi nào cần một "người huấn luyện chó", thì một "người huấn luyện động vật" cũng đáp ứng được vì họ huấn luyện được cả chó.

Đây là trực giác của **Contravariance** : đối tượng **nhận vào** kiểu dữ liệu thường có quan hệ ngược chiều.

* * *

Khai báo
    
    
    T_contra = TypeVar(
        "T_contra",
        contravariant=True
    )

* * *

# 17\. Quy tắc nhớ

Đọc

↓

Covariant

* * *

Ghi

↓

Contravariant

* * *

Đọc + Ghi

↓

Invariant

* * *

# 18\. Ví dụ Stack
    
    
    class Stack(
        Generic[T]
    ):
        def push(
            self,
            item: T
        ):
            ...
    
        def pop() -> T:
            ...

Có
    
    
    push
    
    ↓
    
    ghi

và
    
    
    pop
    
    ↓
    
    đọc

Cho nên

Stack

↓

Invariant.

* * *

# 19\. Ví dụ Repository
    
    
    Repository[T]

Có
    
    
    save(T)

và
    
    
    get() -> T

Đọc + Ghi

↓

Invariant

Đây là lý do đa số Repository đều bất biến về kiểu.

* * *

# 20\. Tóm tắt Variance

Loại| Ý nghĩa| Ví dụ  
---|---|---  
Invariant| Không chuyển đổi giữa `Container[Dog]` và `Container[Animal]`| `list`, `dict`, `set`, Repository đọc/ghi  
Covariant| Có thể dùng kiểu con ở nơi cần kiểu cha| `Sequence`, `Iterable`, `tuple` chỉ đọc  
Contravariant| Áp dụng cho các kiểu nhận dữ liệu vào| Callback, Handler, Consumer  
  
* * *

# 21\. Áp dụng vào dự án crawler

Giả sử
    
    
    class BaseNovel:
        ...
    
    class Novel(
        BaseNovel
    ):
        ...

Danh sách kết quả parser
    
    
    from collections.abc import Sequence
    
    def show(
        novels: Sequence[
            BaseNovel
        ]
    ):
        ...

Có thể truyền
    
    
    Sequence[
        Novel
    ]

Không cần ép kiểu.

Nhưng nếu hàm nhận:
    
    
    list[BaseNovel]

thì không nên truyền `list[Novel]` chỉ vì quan hệ kế thừa. Điều này giúp tránh việc vô tình thêm một `BaseNovel` không phải `Novel` vào danh sách.

* * *

# 22\. Best Practices

✔ Dùng `bound=` khi muốn giới hạn `TypeVar` vào một lớp cơ sở nhưng vẫn giữ được kiểu cụ thể.

✔ Dùng Constraint khi chỉ có một số kiểu rời rạc hợp lệ (`str`, `bytes`,...).

✔ Dùng `Sequence` thay vì `list` nếu chỉ đọc dữ liệu.

✔ Hiểu rằng `list` là **Invariant** để tránh các lỗi khó phát hiện.

✔ Chỉ khai báo `covariant=True` hoặc `contravariant=True` khi bạn thực sự hiểu vai trò của kiểu trong API.

* * *

# Bài tập

## Bài 1

Tạo
    
    
    class Animal: ...
    class Dog(Animal): ...
    class Cat(Animal): ...

Viết
    
    
    T = TypeVar(
        "T",
        bound=Animal
    )
    
    def clone(obj: T) -> T:
        return obj

Kiểm tra IDE suy luận đúng kiểu `Dog` và `Cat`.

* * *

## Bài 2

Viết
    
    
    T = TypeVar(
        "T",
        str,
        bytes
    )

Viết hàm
    
    
    def duplicate(
        value: T
    ) -> T:
        return value * 2

Thử với:

  * `"abc"`
  * `b"abc"`
  * `123`



Quan sát cảnh báo của IDE.

* * *

## Bài 3

Viết hai hàm:
    
    
    from collections.abc import Sequence
    
    def print_animals(
        animals: Sequence[Animal]
    ):
        ...

và
    
    
    def modify_animals(
        animals: list[Animal]
    ):
        animals.append(Cat())

Sau đó thử truyền một `list[Dog]` vào từng hàm và phân tích:

  * Vì sao hàm dùng `Sequence` phù hợp với danh sách chỉ đọc?
  * Vì sao việc sửa đổi (`append`) khiến `list` phải là **Invariant**?



* * *

## Tổng kết

Sau 8 buổi, bạn đã làm chủ phần **Generic cốt lõi** của Python:

  * `TypeVar`
  * `Generic`
  * Generic Function/Class
  * Generic Repository
  * Type Inference
  * `bound`
  * Constraint
  * Covariance
  * Contravariance
  * Invariance



Đây là nền tảng để đọc và thiết kế các API hiện đại.

**Buổi 9** sẽ chuyển sang một chủ đề cực kỳ quan trọng khác: `**Self**`**(PEP 673)**. Bạn sẽ học cách xây dựng **Fluent API** , **Builder Pattern** , phương thức chuỗi (`method chaining`) và cách `Self` giải quyết những hạn chế của `TypeVar` trong các lớp có kế thừa. Đây là kỹ thuật được sử dụng rất nhiều trong SQLAlchemy, Requests, Pandas và nhiều thư viện Python hiện đại.

