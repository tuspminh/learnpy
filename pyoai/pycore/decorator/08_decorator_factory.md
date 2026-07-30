# Decorator Deep Dive — Buổi 8

# Decorator Factory (Decorator có tham số)

Đây là một trong những chủ đề mà hầu như **mọi framework Python** đều sử dụng.

Ví dụ:
    
    
    @app.route("/users")
    
    
    @retry(times=3)
    
    
    @click.option("--name")
    
    
    @cache(timeout=60)
    
    
    @permission(role="admin")

Tất cả đều là **Decorator Factory**.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Decorator Factory là gì. 
  * Vì sao Decorator bình thường không đủ. 
  * Decorator Factory hoạt động như thế nào. 
  * Ba tầng hàm lồng nhau. 
  * Luồng thực thi. 
  * Nhiều ví dụ thực tế. 



* * *

# 1\. Decorator bình thường

Buổi trước
    
    
    def logger(func):
    
        def wrapper(*args, **kwargs):
    
            print("Before")
    
            result = func(*args, **kwargs)
    
            print("After")
    
            return result
    
        return wrapper

Sử dụng
    
    
    @logger
    def hello():
        print("Hello")

Python biến thành
    
    
    hello = logger(hello)

* * *

Nhưng nếu muốn
    
    
    @repeat(5)

thì sao?

Decorator hiện tại không làm được.

* * *

# 2\. Tại sao?

Giả sử
    
    
    @repeat(3)
    def hello():
        print("Hello")

Python sẽ hiểu thành
    
    
    hello = repeat(3)(hello)

Đây là điều cực kỳ quan trọng.

Không phải
    
    
    repeat(hello)

Mà là
    
    
    repeat(3)
    
    ↓
    
    trả về decorator
    
    ↓
    
    decorator(hello)
    
    ↓
    
    trả về wrapper
    
    ↓
    
    wrapper()

* * *

# 3\. Decorator Factory đầu tiên
    
    
    def repeat(times):
    
        def decorator(func):
    
            def wrapper(*args, **kwargs):
    
                for _ in range(times):
                    func(*args, **kwargs)
    
            return wrapper
    
        return decorator

Có ba tầng.
    
    
    repeat
    
    ↓
    
    decorator
    
    ↓
    
    wrapper

* * *

# 4\. Sử dụng
    
    
    @repeat(3)
    def hello():
        print("Hello")

Gọi
    
    
    hello()

Kết quả
    
    
    Hello
    Hello
    Hello

* * *

# 5\. Python thực sự làm gì?

Đây là phần quan trọng nhất.

Đoạn
    
    
    @repeat(3)
    def hello():
        print("Hello")

Được Python biến thành
    
    
    def hello():
        print("Hello")
    
    hello = repeat(3)(hello)

Tiếp tục
    
    
    decorator = repeat(3)
    
    hello = decorator(hello)

* * *

# 6\. Từng bước

Bước 1
    
    
    repeat(3)

Trả về
    
    
    decorator

* * *

Bước 2
    
    
    decorator(hello)

Trả về
    
    
    wrapper

* * *

Bước 3
    
    
    hello = wrapper

* * *

Sơ đồ
    
    
    repeat(3)
    
    ↓
    
    decorator
    
    ↓
    
    decorator(hello)
    
    ↓
    
    wrapper
    
    ↓
    
    hello
    
    ↓
    
    wrapper()

* * *

# 7\. Tại sao cần ba tầng?

Tầng 1
    
    
    repeat(times)

Nhận cấu hình.

Ví dụ
    
    
    times = 3

* * *

Tầng 2
    
    
    decorator(func)

Nhận function.

* * *

Tầng 3
    
    
    wrapper()

Nhận dữ liệu khi gọi hàm.

* * *

Ba tầng có nhiệm vụ khác nhau.

* * *

# 8\. Ví dụ Logging Level
    
    
    def logger(level):
    
        def decorator(func):
    
            def wrapper(*args, **kwargs):
    
                print(f"[{level}] Start")
    
                result = func(*args, **kwargs)
    
                print(f"[{level}] End")
    
                return result
    
            return wrapper
    
        return decorator

Sử dụng
    
    
    @logger("INFO")
    def backup():
        print("Backup")

Kết quả
    
    
    [INFO] Start
    Backup
    [INFO] End

* * *

# 9\. Ví dụ Delay
    
    
    import time
    
    def delay(seconds):
    
        def decorator(func):
    
            def wrapper(*args, **kwargs):
    
                time.sleep(seconds)
    
                return func(*args, **kwargs)
    
            return wrapper
    
        return decorator
    
    
    @delay(2)
    def hello():
        print("Hello")

Gọi
    
    
    hello()

Đợi
    
    
    2 giây

rồi mới chạy.

* * *

# 10\. Ví dụ Retry
    
    
    def retry(times):
    
        def decorator(func):
    
            def wrapper(*args, **kwargs):
    
                last_error = None
    
                for attempt in range(times):
    
                    try:
                        return func(*args, **kwargs)
    
                    except Exception as e:
    
                        print(
                            f"Retry {attempt+1}"
                        )
    
                        last_error = e
    
                raise last_error
    
            return wrapper
    
        return decorator

* * *

# 11\. Ví dụ Permission
    
    
    CURRENT_ROLE = "user"
    
    def require(role):
    
        def decorator(func):
    
            def wrapper(*args, **kwargs):
    
                if CURRENT_ROLE != role:
                    print("Access denied")
                    return
    
                return func(*args, **kwargs)
    
            return wrapper
    
        return decorator

Sử dụng
    
    
    @require("admin")
    def delete_user():
        print("Deleted")

* * *

# 12\. Ví dụ Cache
    
    
    def cache(limit):
    
        def decorator(func):
    
            memory = {}
    
            def wrapper(*args):
    
                if args in memory:
                    return memory[args]
    
                result = func(*args)
    
                if len(memory) < limit:
                    memory[args] = result
    
                return result
    
            return wrapper
    
        return decorator
    
    
    @cache(100)

Đây chính là ý tưởng của nhiều cache decorator.

* * *

# 13\. Ví dụ Timer
    
    
    import time
    
    def timer(unit):
    
        def decorator(func):
    
            def wrapper(*args, **kwargs):
    
                start = time.perf_counter()
    
                result = func(*args, **kwargs)
    
                elapsed = time.perf_counter() - start
    
                if unit == "ms":
                    elapsed *= 1000
    
                print(elapsed)
    
                return result
    
            return wrapper
    
        return decorator
    
    
    @timer("ms")

* * *

# 14\. Ví dụ hoàn chỉnh — Repeat
    
    
    def repeat(times):
    
        def decorator(func):
    
            def wrapper(*args, **kwargs):
    
                result = None
    
                for _ in range(times):
    
                    result = func(*args, **kwargs)
    
                return result
    
            return wrapper
    
        return decorator
    
    
    @repeat(3)
    def greet(name):
        print("Hello", name)
        return len(name)
    
    
    value = greet("Alice")
    
    print(value)

Kết quả
    
    
    Hello Alice
    Hello Alice
    Hello Alice
    5

* * *

# 15\. Ví dụ hoàn chỉnh — Benchmark
    
    
    import time
    
    
    def benchmark(rounds):
    
        def decorator(func):
    
            def wrapper(*args, **kwargs):
    
                total = 0
    
                result = None
    
                for _ in range(rounds):
    
                    start = time.perf_counter()
    
                    result = func(*args, **kwargs)
    
                    total += time.perf_counter() - start
    
                average = total / rounds
    
                print(
                    f"Average: {average:.6f}s"
                )
    
                return result
    
            return wrapper
    
        return decorator
    
    
    @benchmark(5)
    def calculate():
    
        total = 0
    
        for i in range(100000):
            total += i
    
        return total
    
    
    calculate()

Đây là một benchmark decorator đơn giản.

* * *

# 16\. Ví dụ hoàn chỉnh — Validator
    
    
    def max_length(limit):
    
        def decorator(func):
    
            def wrapper(text):
    
                if len(text) > limit:
                    raise ValueError(
                        f"Too long (>{limit})"
                    )
    
                return func(text)
    
            return wrapper
    
        return decorator
    
    
    @max_length(10)
    def save_comment(text):
    
        print("Saved:", text)
    
    
    save_comment("Python")

Nếu
    
    
    save_comment(
        "Decorator Factory"
    )

Sẽ báo
    
    
    ValueError

* * *

# 17\. Phân tích Closure

Ví dụ
    
    
    def repeat(times):
    
        def decorator(func):
    
            def wrapper(*args, **kwargs):
    
                for _ in range(times):
                    func(*args, **kwargs)
    
            return wrapper
    
        return decorator

`wrapper`

ghi nhớ
    
    
    times

và
    
    
    func

Kiểm tra
    
    
    wrapped = repeat(3)(print)
    
    print(
        wrapped.__closure__
    )

Sẽ có hai Cell.
    
    
    Cell
    
    ↓
    
    func
    
    
    Cell
    
    ↓
    
    times

Decorator Factory là một ví dụ rất đẹp về Closure nhiều biến.

* * *

# 18\. Thứ tự thực thi

Ví dụ
    
    
    @repeat(2)
    def hello():
        print("Hello")

Khi chương trình import module:
    
    
    repeat(2)

chỉ chạy **một lần** để tạo decorator.

Sau đó:
    
    
    decorator(hello)

cũng chỉ chạy **một lần** để tạo wrapper.

Khi gọi:
    
    
    hello()

mỗi lần gọi mới thực thi:
    
    
    wrapper()

Sơ đồ:
    
    
    Khởi động chương trình
    
    ↓
    
    repeat(2)
    
    ↓
    
    decorator(hello)
    
    ↓
    
    wrapper được tạo
    
    =========================
    
    Mỗi lần gọi hello()
    
    ↓
    
    wrapper()
    
    ↓
    
    hello()

Điều này rất quan trọng để hiểu vì sao các framework có thể "đăng ký" route hoặc command ngay khi module được nạp.

* * *

# 19\. Ví dụ mô phỏng Flask

Giả sử:
    
    
    routes = {}
    
    
    def route(path):
    
        def decorator(func):
            routes[path] = func
            return func
    
        return decorator
    
    
    @route("/")
    def home():
        print("Home")
    
    
    @route("/about")
    def about():
        print("About")
    
    
    routes["/"]()
    routes["/about"]()

Kết quả:
    
    
    Home
    About

Điều xảy ra khi import module:

  1. `route("/")` tạo decorator. 
  2. Decorator nhận `home`. 
  3. `home` được lưu vào `routes`. 
  4. Sau này web server chỉ cần: 


    
    
    routes["/"]()

Đây chính là nguyên lý cốt lõi của Flask và nhiều web framework khác.

* * *

# So sánh Decorator thường và Decorator Factory

Decorator thường| Decorator Factory  
---|---  
`@logger`| `@logger("INFO")`  
2 tầng hàm| 3 tầng hàm  
Không có cấu hình| Có cấu hình  
`decorator(func)`| `factory(config) → decorator(func)`  
Dùng khi logic cố định| Dùng khi cần tùy biến  
  
* * *

# Những lỗi phổ biến

## Sai 1: Trả về wrapper thay vì decorator

Sai:
    
    
    def repeat(times):
        def decorator(func):
            ...
        return wrapper  # wrapper chưa tồn tại ở đây

Đúng:
    
    
    return decorator

* * *

## Sai 2: Quên `return result`

Nếu wrapper không trả về kết quả của hàm gốc, giá trị trả về sẽ bị mất.

* * *

## Sai 3: Không dùng `*args, **kwargs`

Decorator sẽ chỉ hoạt động với một số kiểu hàm và dễ phát sinh `TypeError`.

* * *

# Mẫu Decorator Factory chuẩn

Đây là mẫu mà bạn sẽ gặp trong rất nhiều framework:
    
    
    def factory(config):
    
        def decorator(func):
    
            def wrapper(*args, **kwargs):
    
                # Before
    
                result = func(*args, **kwargs)
    
                # After
    
                return result
    
            return wrapper
    
        return decorator

Hãy ghi nhớ mẫu này. Chỉ cần thay phần `config`, `Before` và `After`, bạn có thể xây dựng rất nhiều decorator khác nhau.

* * *

# Tổng kết buổi 8

Bạn cần nắm chắc:

  1. `@decorator` tương đương: 


    
    
    func = decorator(func)

  2. `@factory(config)` tương đương: 


    
    
    func = factory(config)(func)

  3. Decorator Factory luôn có **3 tầng** : 


  * Factory: nhận cấu hình. 
  * Decorator: nhận hàm. 
  * Wrapper: nhận tham số của lần gọi. 


  4. `wrapper` ghi nhớ cả `func` và `config` nhờ Closure. 
  5. Hầu hết framework hiện đại đều sử dụng Decorator Factory. 



* * *

# Bài tập

## Bài 1

Viết decorator:
    
    
    @repeat(5)
    def hello():
        print("Hello")

Yêu cầu:

  * Gọi hàm đúng 5 lần. 
  * Trả về kết quả của lần gọi cuối cùng. 



* * *

## Bài 2

Viết decorator:
    
    
    @timeout(2)
    def download():
        ...

Hiện tại chưa cần dừng hàm sau 2 giây. Chỉ cần:

  * In giá trị timeout. 
  * Gọi hàm. 
  * In thông báo kết thúc. 



(Hoàn thiện chức năng timeout thực sự sẽ học ở phần về đa luồng và bất đồng bộ.)

* * *

## Bài 3

Viết decorator:
    
    
    @validate(min_value=0, max_value=100)
    def set_score(score):
        print(score)

Yêu cầu:

  * Kiểm tra tất cả đối số kiểu số (`int`, `float`) nằm trong khoảng `[min_value, max_value]`. 
  * Nếu có giá trị ngoài khoảng, ném `ValueError`. 
  * Nếu hợp lệ, gọi hàm bình thường. 



* * *

# Chuẩn bị cho buổi 9

Ở **buổi 9** , chúng ta sẽ học **Decorator Stacking (xếp chồng nhiều decorator)**. Bạn sẽ hiểu chính xác thứ tự áp dụng của nhiều decorator, cách Python chuyển đổi:
    
    
    @A
    @B
    @C
    def hello():
        ...

thành các lời gọi hàm lồng nhau, đồng thời phân tích các trường hợp thực tế như `@cache` \+ `@timer` \+ `@logger`, và cách thứ tự decorator ảnh hưởng trực tiếp đến kết quả chương trình. Đây là kiến thức rất quan trọng khi đọc mã nguồn của Flask, FastAPI, Django và nhiều thư viện Python khác.

