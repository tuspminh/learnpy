# **[Python] 15 - Decorators — Cách hoạt động & ví dụ thực tế**

    Decorators trong Python là một trong những công cụ mạnh mẽ nhất của ngôn ngữ này. Chúng cho phép bạn mở rộng hoặc thay đổi hành vi của function/class mà không cần chỉnh sửa trực tiếp code gốc. Hiểu rõ về decorators sẽ là tiền đề giúp bạn nắm vững các framework như Flask, Django, hay pytest.

## **1 - Decorator, cú pháp và cách hoạt động?**

    Decorator là một hàm nhận vào một hàm khác như đối số và trả về một hàm mới với hành vi được mở rộng. Nó thường được sử dụng để thêm logic logging, kiểm tra quyền, đo thời gian thực thi, caching, v.v...

```text-x-trilium-auto
def decorator_func(func):
    def wrapper():
        print("Before function call")
        func()
        print("After function call")
    return wrapper

@decorator_func
def say_hello():
    print("Hello!")

say_hello()
# Output:
# Before function call
# Hello!
# After function call
```

### **Cú pháp và cách hoạt động**

    Khi bạn viết `**@decorator_func**` trên một hàm, Python sẽ tự động thực hiện: `**say_hello = decorator_func(say_hello)**`. Vì vậy decorator thực chất chỉ là cách viết ngắn gọn, giúp code dễ đọc hơn.

## **2 - Stacking & Multiple Decorators**

    Bạn có thể chồng nhiều decorator lên cùng một hàm. Chúng được áp dụng (được "gắn") từ trên xuống dưới tại thời điểm định nghĩa hàm, nhưng khi gọi, các wrapper chạy theo thứ tự ngược lại (tức là từ dưới lên).

```text-x-trilium-auto
def deco1(f):
    def wrap():
        print("deco1")
        f()
    return wrap

def deco2(f):
    def wrap():
        print("deco2")
        f()
    return wrap

@deco1
@deco2
def hello():
    print("hello")

hello()
# Output:
# deco1
# deco2
# hello
```

    **↪ Giải thích chi tiết:**

- **Thời điểm "decoration" (khi Python đọc định nghĩa hàm):**
  - Khi Python gặp `@deco2` phía trên `def hello`, nó thực hiện `hello = deco2(hello)`. Kết quả là `hello` trở thành hàm `wrap` trả về từ `deco2`.
  - Sau đó gặp `@deco1`, Python thực hiện `hello = deco1(hello)`, tức `hello` giờ là hàm `wrap` trả về từ `deco1`, và bên trong nó giữ một tham chiếu tới hàm được trả về bởi `deco2`.
  - Nên thứ tự gắn là: `hello = deco1(deco2(hello_original))`.
- **Thời điểm gọi (call time):**
  - Khi bạn gọi `hello()`, bạn đang gọi wrapper bên ngoài (do `deco1` tạo). Bên ngoài in `deco1`, sau đó gọi hàm nội tại (chính là wrapper được tạo bởi `deco2`).
  - Wrapper của `deco2` in `deco2`, rồi gọi hàm gốc `hello` (in `hello`).
  - Kết quả thực thi theo chuỗi: `deco1 → deco2 → hello`.
- **Vấn đề thường gặp:**
  - Nếu wrapper không chấp nhận [`***args, **kwargs**`](https://www.laptrinhdientu.com/2025/10/python-function-and-arguments.html#python-args-kwargs) nhưng hàm gốc có tham số, sẽ xảy ra `TypeError`. Luôn viết wrapper dạng tổng quát nếu muốn áp dụng cho nhiều hàm khác nhau.
  - Nếu không dùng `functools.wraps`, metadata của hàm (như `__name__`, `__doc__`, signature) sẽ mất — làm khó debug và introspection.

**Phiên bản cải tiến (an toàn hơn, general-purpose):**

```text-x-trilium-auto
from functools import wraps

def deco1(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        print("deco1")
        return f(*args, **kwargs)
    return wrap

def deco2(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        print("deco2")
        return f(*args, **kwargs)
    return wrap

@deco1
@deco2
def hello():
    print("hello")

hello()
# Output:
# deco1
# deco2
# hello
```

    Với `***args**, ****kwargs**` và `**@wraps**`, decorator an toàn hơn và giữ ***metadata***.

---

## **3 - Decorator có tham số**

    Khi bạn muốn truyền tham số cho decorator (ví dụ `@repeat(3)`), cần một "**decorator factory**": hàm ngoài nhận tham số và trả về một decorator thực sự.

```text-x-trilium-auto
def repeat(n):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(n):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def greet():
    print("Hi!")

greet()
# Output: Hi! (in ra 3 lần)
```

**Giải thích chi tiết:**

- **Cấu trúc ba lớp:**
  
  1. `repeat(n)` là hàm **factory** ➜ lúc này gọi `repeat(3)` và nhận về một `**decorator**`.
  2. `decorator(func)` là decorator thực sự ➜ nhận hàm cần bọc và trả về `wrapper`.
  3. `wrapper(*args, **kwargs)` là hàm wrapper khi gọi ➜ thực hiện logic lặp `n` lần rồi gọi hàm gốc.
- [**Closure**](https://www.laptrinhdientu.com/2025/10/python-inner-function-closure.html#closures)**:** giá trị `n` được "bắt" (captured) trong closure của `wrapper`, nên wrapper nhớ số lần lặp mà bạn cấu hình tại thời điểm sử dụng decorator.
  
- **Trả về giá trị:**
  
  - Trong ví dụ trên, `wrapper` không trả về kết quả của hàm gốc (mặc định trả `None`), vì ta gọi hàm gốc nhiều lần và bỏ qua kết quả. Nếu hàm gốc có giá trị trả về quan trọng, bạn cần xác định hành vi mong muốn (ví dụ: trả về kết quả lần cuối, trả list các kết quả, hoặc gộp kết quả).
- **Phiên bản cải tiến (trả về kết quả lần cuối và bảo toàn metadata):** 
  
  ```text-x-trilium-auto
  from functools import wraps
  
  def repeat(n):
      def decorator(func):
          @wraps(func)
          def wrapper(*args, **kwargs):
              result = None
              for _ in range(n):
                  result = func(*args, **kwargs)
              return result
          return wrapper
      return decorator
  
  @repeat(3)
  def greet():
      print("Hi!")
  
  greet()
  # Output: Hi! (in ra 3 lần)
  ```
  
  Ở đây wrapper trả `result` từ lần gọi cuối cùng, phù hợp khi hàm có side-effect và bạn muốn kết quả cuối cùng.
  
- **Lưu ý:**
  
  - Nếu hàm gốc có side-effect (ví dụ gửi request), lặp nhiều lần có thể không mong muốn → cần cân nhắc (exponential backoff, stop-on-success...).
  - Đối với các hàm IO/Network, thường kết hợp `retry` với delay/backoff và điều kiện dừng (stop-on-success hoặc chỉ retry với các exception cụ thể).

---

## **4 - Class Decorators**

    Decorator cũng có thể được viết bằng class, rất hữu ích khi bạn muốn lưu trạng thái giữa các lần gọi (ví dụ đếm số lần gọi). Class decorator hoạt động vì class là callable (khi cài `__call__`).

```text-x-trilium-auto
class Counter:
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call {self.count}")
        return self.func(*args, **kwargs)

@Counter
def hello():
    print("Hi")

hello()
hello()
# Output:
# Call 1
# Hi
# Call 2
# Hi
```

**Giải thích chi tiết:**

- **Khi áp dụng** `**@Counter**`**:**
  
  - Python gọi `Counter(hello)` → tức là tạo một instance của class `Counter` và truyền hàm gốc vào `**__init__**`.
  - Instance trả về được gán thay cho tên hàm `hello`. Vì instance có phương thức `__call__`, nó trở thành một callable thay thế cho hàm ban đầu.
- **Trạng thái được lưu:** Giá trị `self.count` nằm trên instance decorator, vì vậy nó tồn tại và được tăng dần qua nhiều lần gọi, đây là lợi ích chính của decorator dạng class so với hàm: dễ lưu state.
  
- **Gọi hàm:** Khi bạn gọi `hello()`, thực tế Python gọi `Counter_instance.__call__()`. Trong __call__ ta tăng bộ đếm rồi gọi `self.func(*args, **kwargs)` để thực thi hàm gốc.
  
- **Preserve metadata / best practice:**
  
  - Để giữ metadata (tên hàm, docstring), trong `__init__` bạn nên gọi `functools.update_wrapper(self, func)` hoặc dùng `wraps(func)(self)`. Nếu không, introspection (ví dụ `help()` hoặc `inspect.signature()`) sẽ thấy instance thay vì hàm gốc. 
  
  ```text-x-trilium-auto
  from functools import update_wrapper
  
  class Counter:
      def __init__(self, func):
          self.func = func
          self.count = 0
          update_wrapper(self, func)   # copy __name__, __doc__...
      def __call__(self, *args, **kwargs):
          self.count += 1
          print(f"Call {self.count}")
          return self.func(*args, **kwargs)
  ```
  
- **Concurrency / Thread-safety:**
  
  - Nếu ứng dụng đa luồng, `self.count += 1` có thể race condition. Nếu cần chính xác, thêm khóa (lock) để bảo vệ state.
- Ưu điểm của cách làm này là dễ lưu lại trạng thái, có thể chứa nhiều logic phức tạp, cấu trúc rõ ràng. Tuy nhiên, instance thay thế cho hàm nên đôi khi làm khó debug nếu không dùng `**update_wrapper**`; chi phí nhỏ hơn so với function decorator về readability trong một số trường hợp.
  

**Tổng kết nhanh / checklist khi viết decorator:**

- Dùng `*args, **kwargs` trong wrapper để tương thích với mọi signature.
- Dùng `functools.wraps` (hoặc `functools.update_wrapper`) để bảo toàn metadata.
- Quan tâm đến **thứ tự** khi chồng decorator → thứ tự gắn ≠ thứ tự chạy.
- Với decorator có tham số, nhớ pattern `**factory → decorator → wrapper**`.
- Nếu cần lưu state, cân nhắc dùng class-based decorator và xử lý thread-safety nếu cần.
- Luôn cân nhắc return value khi wrapper gọi hàm nhiều lần (ví dụ repeat/retry): phải rõ ràng trả cái gì.

## **5 - Xây dựng decorator retry hoàn chỉnh (với backoff & logging)**

    Một use-case thực tế của decorator là xử lý retry cho các thao tác có thể thất bại tạm thời, như request HTTP hoặc truy cập database. Dưới đây là một ví dụ hoàn chỉnh có hỗ trợ **retry count, delay tăng dần (exponential backoff), và logging**.

1. ```text-x-trilium-auto
  import time
  import logging
  
  logging.basicConfig(level=logging.INFO)
  
  def retry(max_attempts=3, backoff=1.0):
     def decorator(func):
         def wrapper(*args, **kwargs):
             attempt = 1
             delay = backoff
             while attempt <= max_attempts:
                 try:
                     return func(*args, **kwargs)
                 except Exception as e:
                     logging.warning(f"Attempt {attempt} failed: {e}")
                     if attempt == max_attempts:
                         logging.error("Max retries exceeded")
                         raise
                     time.sleep(delay)
                     delay *= 2  # exponential backoff
                     attempt += 1
         return wrapper
     return decorator
  
  @retry(max_attempts=4, backoff=0.5)
  def unstable_func():
     import random
     if random.random() < 0.7:
         raise ValueError("Random failure")
     print("Success!")
  
  unstable_func()
  ```
  

    Trong ví dụ trên: – Hàm sẽ retry tối đa 4 lần, mỗi lần lỗi sẽ chờ lâu hơn gấp đôi trước khi thử lại. Tất cả kết quả được log ra console. Đây là một pattern rất phổ biến khi xử lý API, network hoặc sensor data.

**Unit test mẫu:**

```text-x-trilium-auto
import unittest

class TestRetryDecorator(unittest.TestCase):
    def test_success(self):
        calls = {"count": 0}
        @retry(max_attempts=3)
        def func():
            calls["count"] += 1
            if calls["count"] < 2:
                raise ValueError("fail")
            return "ok"

        result = func()
        self.assertEqual(result, "ok")
        self.assertEqual(calls["count"], 2)

if __name__ == "__main__":
    unittest.main()
```

## **6 - Kết luận**

    Decorators là một phần quan trọng trong Python giúp code sạch, dễ mở rộng và có khả năng tái sử dụng cao. Khi hiểu cách chúng hoạt động, bạn có thể áp dụng để viết logging, retry, validation, hoặc các pattern phức tạp khác một cách hiệu quả.
