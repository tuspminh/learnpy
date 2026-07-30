Version:0.9 StartHTML:0000000105 EndHTML:0000025723 StartFragment:0000000141 EndFragment:0000025687 

# Typing Deep Dive – Buổi 2

# Built-in Generic Types và Collection Types

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Thành thạo cách khai báo type cho mọi collection trong Python.
>   * Hiểu sự khác nhau giữa `list`, `tuple`, `set`, `dict`.
>   * Biết khi nào dùng `list[int]` và khi nào dùng `Sequence[int]`.
>   * Hiểu tư duy "lập trình hướng interface" trong typing.
>   * Viết được API linh hoạt, dễ mở rộng.
> 


* * *

# 1\. Từ `typing.List` đến `list[int]`

Trước Python 3.9:
    
    
    from typing import List
    
    numbers: List[int] = [1, 2, 3]

Từ Python 3.9 trở đi:
    
    
    numbers: list[int] = [1, 2, 3]

Đây là cách viết hiện đại và được khuyến nghị.

Tương tự:

Cũ| Mới  
---|---  
`List[int]`| `list[int]`  
`Dict[str, int]`| `dict[str, int]`  
`Tuple[int, str]`| `tuple[int, str]`  
`Set[str]`| `set[str]`  
  
* * *

# 2\. list[T]

Ví dụ:
    
    
    numbers: list[int] = [1, 2, 3]
    
    names: list[str] = ["Alice", "Bob"]

Danh sách hỗn hợp:
    
    
    items: list[int | str] = [1, "hello", 2]

Danh sách lồng nhau:
    
    
    matrix: list[list[int]] = [
        [1, 2],
        [3, 4]
    ]

Ba chiều:
    
    
    cube: list[list[list[int]]] = [
        [[1], [2]],
        [[3], [4]]
    ]

* * *

# 3\. dict[K, V]

Ví dụ:
    
    
    scores: dict[str, int] = {
        "Alice": 90,
        "Bob": 85
    }

Key là `str`, value là `int`.

Ví dụ khác:
    
    
    users: dict[int, str] = {
        1: "Alice",
        2: "Bob"
    }

Dictionary lồng nhau:
    
    
    student: dict[str, dict[str, int]] = {
        "math": {
            "score": 90
        }
    }

* * *

# 4\. tuple

Tuple có hai cách dùng.

## Cách 1: Tuple cố định
    
    
    point: tuple[int, int] = (10, 20)

Hoặc:
    
    
    person: tuple[str, int] = ("Alice", 20)

Mỗi vị trí có kiểu xác định.

* * *

## Cách 2: Tuple biến độ dài
    
    
    numbers: tuple[int, ...] = (
        1,
        2,
        3,
        4,
        5
    )

Dấu `...` nghĩa là:

> Có thể có bao nhiêu phần tử cũng được, miễn tất cả đều là `int`.

* * *

# 5\. set[T]
    
    
    tags: set[str] = {
        "python",
        "typing",
        "sqlite"
    }

Ví dụ:
    
    
    visited: set[int] = {
        1,
        2,
        3
    }

* * *

# 6\. Collection lồng nhau

Ví dụ:
    
    
    students: list[dict[str, int]]

Có nghĩa:
    
    
    list
     ├── dict
          ├── key = str
          └── value = int

Ví dụ:
    
    
    students = [
        {"math": 90},
        {"math": 100}
    ]

* * *

Ví dụ lớn hơn:
    
    
    dict[str, list[int]]

Có nghĩa:
    
    
    dict
     ├── key = str
     └── value = list[int]

Ví dụ:
    
    
    scores = {
        "Alice": [90, 80],
        "Bob": [100, 95]
    }

* * *

# 7\. Hàm nhận list

Ví dụ:
    
    
    def average(scores: list[int]) -> float:
        return sum(scores) / len(scores)

Gọi:
    
    
    average([10, 20, 30])

Không vấn đề gì.

* * *

# 8\. Nhưng có một vấn đề

Ví dụ:
    
    
    def print_items(items: list[str]):
        for item in items:
            print(item)

Gọi:
    
    
    print_items(
        ("A", "B", "C")
    )

Tuple cũng có thể lặp được.

Nhưng IDE sẽ báo lỗi.

Tại sao?

Vì tuple không phải list.

Trong khi hàm chỉ cần:

> Có thể lặp.

Nó không cần list.

Đây là lý do cần dùng **kiểu trừu tượng**.

* * *

# 9\. Iterable
    
    
    from collections.abc import Iterable
    
    def print_items(items: Iterable[str]):
        for item in items:
            print(item)

Bây giờ có thể truyền:
    
    
    ["A", "B"]
    
    ("A", "B")
    
    {"A", "B"}
    

Thậm chí:
    
    
    def generator():
        yield "A"
        yield "B"
    
    print_items(generator())

Đều hợp lệ.

* * *

# 10\. Sequence

`Sequence` mạnh hơn `Iterable`.

Nó hỗ trợ:

  * for
  * len()
  * indexing



Ví dụ:
    
    
    from collections.abc import Sequence
    
    def first(items: Sequence[str]) -> str:
        return items[0]

Có thể truyền:
    
    
    list
    
    tuple
    
    str

Đều được.

* * *

# 11\. Vì sao không dùng list?

Ví dụ:
    
    
    def show(items: list[str]):
        ...

Bạn vô tình giới hạn người dùng.

Trong khi:
    
    
    def show(items: Sequence[str]):
        ...

Linh hoạt hơn rất nhiều.

* * *

# 12\. Mapping

Ví dụ:
    
    
    from collections.abc import Mapping
    
    def print_scores(
        scores: Mapping[str, int]
    ):
        ...

Có thể truyền:

  * dict
  * defaultdict
  * OrderedDict
  * MappingProxyType



Nếu dùng:
    
    
    dict[str, int]

Thì chỉ dict.

* * *

# 13\. MutableMapping

Nếu hàm sửa dữ liệu:
    
    
    scores["Alice"] = 100

Lúc này phải dùng:
    
    
    from collections.abc import MutableMapping

Không dùng `Mapping`.

* * *

# 14\. MutableSequence

Nếu cần
    
    
    append()
    
    extend()
    
    pop()
    
    clear()

Thì dùng:
    
    
    MutableSequence

Ví dụ:
    
    
    from collections.abc import MutableSequence
    
    def add_student(
        students: MutableSequence[str]
    ):
        students.append("Alice")

* * *

# 15\. Collection ABC quan trọng

Interface| Có thể làm gì  
---|---  
`Iterable`| Chỉ lặp (`for`)  
`Iterator`| `next()` \+ `for`  
`Sequence`| Lặp, `len()`, chỉ mục (`[]`)  
`MutableSequence`| Thêm, sửa, xóa phần tử  
`Mapping`| Chỉ đọc theo key  
`MutableMapping`| Thêm, sửa, xóa key/value  
`Set`| Tập hợp chỉ đọc  
`MutableSet`| Thêm, xóa phần tử  
  
> Các kiểu này hiện được khuyến nghị import từ `collections.abc` thay vì `typing` trong Python hiện đại.

* * *

# 16\. Ví dụ thiết kế API

❌ Chưa tốt:
    
    
    def calculate(data: list[int]):
        ...

Chỉ chấp nhận list.

* * *

Tốt hơn:
    
    
    from collections.abc import Sequence
    
    def calculate(
        data: Sequence[int]
    ):
        ...

Có thể truyền:
    
    
    list
    
    tuple
    
    array
    
    ...

API linh hoạt hơn.

* * *

# 17\. Quy tắc vàng

Hãy tự hỏi:

> Hàm **thực sự cần khả năng gì** từ tham số?

  * Chỉ cần lặp → `Iterable`
  * Cần truy cập theo chỉ số và `len()` → `Sequence`
  * Cần sửa đổi danh sách → `MutableSequence`
  * Chỉ đọc dữ liệu dạng từ điển → `Mapping`
  * Cần thêm/xóa khóa → `MutableMapping`



Đừng mặc định dùng `list` hoặc `dict` nếu hàm không cần các khả năng đặc thù của chúng.

* * *

# Ví dụ thực tế (dự án crawler truyện)

Thay vì:
    
    
    def crawl_all(urls: list[str]) -> None:
        for url in urls:
            print(url)

Hãy viết:
    
    
    from collections.abc import Iterable
    
    def crawl_all(urls: Iterable[str]) -> None:
        for url in urls:
            print(url)

Khi đó bạn có thể truyền:
    
    
    crawl_all(["https://a.com", "https://b.com"])
    
    crawl_all(("https://a.com", "https://b.com"))
    
    crawl_all(
        url for url in [
            "https://a.com",
            "https://b.com",
        ]
    )

Mà không cần sửa hàm.

* * *

# Best Practices

  * ✅ Dùng `list[int]`, `dict[str, int]`, `tuple[...]`, `set[...]` thay cho `typing.List`, `typing.Dict` trong Python 3.9+.
  * ✅ Ưu tiên `Sequence`, `Iterable`, `Mapping` trong tham số hàm khi chỉ cần hành vi tương ứng.
  * ✅ Chỉ dùng `MutableSequence` hoặc `MutableMapping` khi hàm thực sự thay đổi dữ liệu.
  * ❌ Không dùng `list` chỉ vì "thói quen" nếu API không yêu cầu khả năng thêm/xóa phần tử.



* * *

# Bài tập thực hành

### Bài 1

Viết các khai báo kiểu sau:
    
    
    names = ["Alice", "Bob", "Charlie"]
    
    
    scores = {
        "Math": 95,
        "English": 88
    }
    
    
    point = (10, 20)

Thêm type hint phù hợp.

* * *

### Bài 2

Viết hàm:
    
    
    def total(numbers):
        return sum(numbers)

Sau đó:

  1. Chú thích bằng `list[int]`.
  2. Chú thích lại bằng `Sequence[int]`.
  3. Thử gọi hàm với:
     * `list`
     * `tuple`
  4. So sánh sự khác biệt.



* * *

### Bài 3

Viết hàm:
    
    
    def print_all(items):
        ...

Yêu cầu:

  * Chỉ dùng `Iterable[str]`.
  * Gọi hàm với:
    * `list[str]`
    * `tuple[str, ...]`
    * `set[str]`
    * một generator (`yield`)



Quan sát rằng cùng một API có thể làm việc với nhiều kiểu dữ liệu khác nhau mà không cần thay đổi mã.

Ở **Buổi 3** , chúng ta sẽ học `**Union**`**,**`**Optional**`**,**`**Literal**`**và cú pháp**`**|**`**của Python 3.10+** , đồng thời tìm hiểu cách mô tả các giá trị hợp lệ một cách chính xác và an toàn hơn trong hệ thống kiểu.

