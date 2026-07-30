Version:0.9 StartHTML:0000000105 EndHTML:0000023794 StartFragment:0000000141 EndFragment:0000023758 

# Typing Deep Dive – Buổi 4

# `Any`, `object`, `Never`, `NoReturn` và hệ thống kiểu của Python

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu chính xác `Any` là gì.
>   * Phân biệt `Any` và `object`.
>   * Hiểu khái niệm **Top Type** và **Bottom Type**.
>   * Biết khi nào dùng `Any`.
>   * Biết tại sao lạm dụng `Any` là một trong những nguyên nhân lớn khiến type hint mất giá trị.
>   * Hiểu `Never` và `NoReturn`.
> 


* * *

# 1\. Hệ thống kiểu (Type Hierarchy)

Có thể hình dung hệ thống kiểu của Python như sau:
    
    
                       Any
                        │
            ┌───────────┼────────────┐
            │           │            │
          object      int          str
            │
         list[int]
            │
        ...
            │
          Never

Trong đó:

  * **Any** : chấp nhận mọi kiểu và cũng có thể được dùng ở mọi nơi.
  * **object** : lớp gốc của hầu hết các đối tượng Python.
  * **Never** : kiểu "không bao giờ có giá trị".



* * *

# 2\. Any là gì?
    
    
    from typing import Any

`Any` nghĩa là:

> **"Trình kiểm tra kiểu hãy bỏ qua mọi kiểm tra đối với giá trị này."**

Ví dụ:
    
    
    from typing import Any
    
    value: Any = 10
    
    value = "Hello"
    
    value = [1, 2, 3]
    
    value = {"name": "Alice"}

IDE không báo lỗi.

* * *

## Ví dụ
    
    
    from typing import Any
    
    def process(data: Any):
        print(data.upper())

Gọi
    
    
    process(100)

IDE vẫn không cảnh báo.

Đến runtime mới lỗi:
    
    
    AttributeError:
    'int' object has no attribute 'upper'

Đây chính là nhược điểm của `Any`.

* * *

# 3\. `Any` làm mất tác dụng của Type Checking

Ví dụ
    
    
    from typing import Any
    
    def add(a: Any, b: Any):
        return a + b

Các lời gọi sau đều không bị IDE báo lỗi:
    
    
    add(1, 2)
    
    add("A", "B")
    
    add([], [])
    
    add({}, {})

Ngay cả:
    
    
    add(1, {})

IDE vẫn im lặng.

Trong khi runtime sẽ lỗi.

* * *

# 4\. object là gì?
    
    
    value: object

`object` nghĩa là:

> Giá trị này có thể là bất kỳ đối tượng Python nào.

Nhưng khác `Any` ở chỗ:

IDE **vẫn kiểm tra kiểu**.

Ví dụ
    
    
    value: object = "Hello"
    
    print(value.upper())

IDE báo:
    
    
    "object" has no attribute "upper"

Muốn dùng

phải kiểm tra kiểu.

* * *

# 5\. Type Narrowing với object
    
    
    value: object = "Python"
    
    if isinstance(value, str):
        print(value.upper())

Sau `isinstance`

IDE hiểu
    
    
    value
    
    ↓
    
    str

Lúc này mới cho phép gọi
    
    
    upper()

* * *

# 6\. So sánh `Any` và `object`

## `Any`
    
    
    from typing import Any
    
    value: Any = "Python"
    
    value.upper()

IDE:

✔ Không báo lỗi.

* * *

## `object`
    
    
    value: object = "Python"
    
    value.upper()

IDE:

❌ Báo lỗi.

* * *

## Bảng so sánh

Đặc điểm| `Any`| `object`  
---|---|---  
Có thể nhận mọi kiểu| ✔| ✔  
IDE kiểm tra kiểu| ❌| ✔  
Có thể gọi mọi phương thức| ✔| ❌  
An toàn| ❌| ✔  
  
* * *

# 7\. Khi nào dùng `Any`?

Chỉ nên dùng khi:

  * Thư viện bên thứ ba không có type hint.
  * Dữ liệu thực sự chưa biết kiểu.
  * Giai đoạn chuyển đổi từ code cũ sang code có type hint.
  * Điểm giao tiếp với hệ thống động (plugin, JSON chưa phân tích, reflection...).



Ví dụ:
    
    
    from typing import Any
    
    import json
    
    data: Any = json.loads(text)

Sau đó nên chuyển đổi dần sang kiểu cụ thể.

* * *

# 8\. Không nên truyền `Any` khắp chương trình

Ví dụ
    
    
    def load_data() -> Any:
        ...

Sau đó
    
    
    user = load_data()
    
    print(user.upper())

Rồi
    
    
    print(user.age)
    
    print(user.salary)

IDE không phát hiện được lỗi nào.

Đây gọi là

> **Any Leak**

Một `Any` có thể lan truyền khắp dự án.

* * *

# 9\. Tư duy đúng

Thay vì
    
    
    def get_data() -> Any:

Hãy cố gắng viết
    
    
    def get_data() -> dict[str, str]:

Hoặc
    
    
    def get_data() -> User:

Hoặc
    
    
    def get_data() -> list[Book]:

Kiểu càng cụ thể, IDE càng hỗ trợ tốt.

* * *

# 10\. Never là gì?

Python 3.11
    
    
    from typing import Never

`Never`

nghĩa là

> Không bao giờ tồn tại giá trị thuộc kiểu này.

Đây là **Bottom Type**.

* * *

Ví dụ
    
    
    from typing import Never
    
    def impossible(x: Never):
        ...

Không thể gọi
    
    
    impossible(10)

Không kiểu nào phù hợp với `Never`.

* * *

# 11\. Never trong kiểm tra tính đầy đủ (Exhaustiveness)

Ví dụ
    
    
    from typing import Literal, Never
    
    Status = Literal["running", "done"]
    
    def handle(status: Status) -> None:
        if status == "running":
            print("Run")
        elif status == "done":
            print("Finish")
        else:
            unreachable(status)
    
    def unreachable(value: Never) -> Never:
        raise AssertionError(f"Unexpected value: {value}")

Nếu sau này thêm:
    
    
    Status = Literal[
        "running",
        "done",
        "failed"
    ]

`mypy`/`pyright` sẽ báo rằng nhánh `else` không còn là `Never`, giúp bạn phát hiện nơi cần cập nhật logic.

* * *

# 12\. NoReturn
    
    
    from typing import NoReturn

`NoReturn`

nghĩa là

> Hàm không bao giờ trả về.

Ví dụ
    
    
    from typing import NoReturn
    
    def die(message: str) -> NoReturn:
        raise RuntimeError(message)

Hoặc
    
    
    import sys from typing import NoReturn
    
    def exit_program() -> NoReturn:
        sys.exit(1)

Các hàm này luôn:

  * raise exception
  * hoặc kết thúc chương trình



* * *

# 13\. `Never` và `NoReturn`

Hiện nay

`Never`

được xem là tổng quát hơn.

Ví dụ
    
    
    def fail(message: str) -> Never:
        raise RuntimeError(message)

Hoàn toàn hợp lệ.

Trong code mới (Python 3.11+), nhiều dự án ưu tiên `Never`. Tuy nhiên, `NoReturn` vẫn rất phổ biến và bạn sẽ gặp nhiều trong các thư viện hiện có.

* * *

# 14\. Top Type và Bottom Type
    
    
                Any
                 ▲
                 │
             object
                 ▲
                 │
                int
                 ▲
                 │
               Never

  * `Any`



→ chấp nhận tất cả

  * `Never`



→ không có giá trị nào

* * *

# 15\. Ví dụ thực tế (Plugin System)

Giả sử bạn đang xây dựng hệ thống crawler truyện.

Không nên
    
    
    def load_plugin() -> Any:
        ...

Nên
    
    
    def load_plugin() -> BaseSource:
        ...

Hoặc
    
    
    def load_plugin() -> SourceProtocol:
        ...

Nhờ đó:

  * IDE tự gợi ý phương thức.
  * `mypy` phát hiện sai sót.
  * Dễ refactor hơn.



* * *

# 16\. Best Practices

✔ Tránh dùng `Any` nếu có thể mô tả kiểu chính xác.

✔ Dùng `object` khi muốn chấp nhận mọi đối tượng nhưng vẫn giữ được kiểm tra kiểu.

✔ Thu hẹp kiểu bằng `isinstance()` trước khi gọi phương thức đặc thù.

✔ Dùng `Never` cho các hàm hoặc nhánh mã "không thể xảy ra".

✔ Dùng `NoReturn` (hoặc `Never`) cho các hàm luôn `raise` hoặc `exit`.

❌ Không để `Any` lan truyền từ lớp dưới lên lớp trên (Any Leak).

* * *

# Bài tập thực hành

## Bài 1

Viết hai hàm:
    
    
    from typing import Any
    
    def print_any(value: Any):
        print(value)

và
    
    
    def print_object(value: object):
        print(value)

Sau đó thử gọi:

  * `10`
  * `"Python"`
  * `[1, 2, 3]`



So sánh trải nghiệm khi IDE gợi ý hoặc kiểm tra kiểu.

* * *

## Bài 2

Viết hàm:
    
    
    def shout(value: object):
        ...

Yêu cầu:

  * Nếu là `str` thì in chữ hoa.
  * Nếu không thì in `"Not a string"`.



Sử dụng `isinstance()` để thu hẹp kiểu.

* * *

## Bài 3

Viết hàm:
    
    
    from typing import Never
    
    def panic(message: str) -> Never:
        raise RuntimeError(message)

Gọi thử:
    
    
    panic("Database connection failed")

Quan sát rằng sau lời gọi này, mọi câu lệnh phía dưới trong cùng nhánh sẽ được IDE coi là **không thể thực thi** (unreachable code).

* * *

Ở **Buổi 5** , chúng ta sẽ học về **Type Alias** , `type` (Python 3.12), `NewType` và cách xây dựng một "ngôn ngữ kiểu" riêng cho dự án. Đây là bước đầu để tạo ra các API có ý nghĩa và dễ đọc trong những hệ thống lớn như dự án crawler truyện mà bạn đang xây dựng.

