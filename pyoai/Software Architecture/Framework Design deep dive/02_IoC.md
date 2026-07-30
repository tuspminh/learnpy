# Framework Design Deep Dive

# Buổi 2: Library vs Framework — Inversion of Control (IoC) từ góc nhìn kiến trúc sư

> **Mục tiêu**
> 
> Sau buổi này bạn sẽ hiểu:
> 
>   * Chính xác Library và Framework khác nhau ở đâu. 
>   * Inversion of Control (IoC) là gì. 
>   * Vì sao mọi framework đều dựa trên IoC. 
>   * Framework kiểm soát chương trình như thế nào. 
>   * Tự xây một mini framework sử dụng IoC. 
> 


* * *

# Roadmap
    
    
    PHẦN I - Framework Mindset
    
    ✔ Buổi 1. Framework là gì?
    
    ▶ Buổi 2. Library vs Framework
    
    Buổi 3. Inversion of Control (IoC)
    
    Buổi 4. Dependency Injection
    
    Buổi 5. Lifecycle
    
    Buổi 6. Application Context
    
    Buổi 7. Service Container
    
    Buổi 8. Object Graph

> Hôm nay chúng ta mới giới thiệu IoC ở mức trực quan. Buổi 3 sẽ đi sâu vào IoC với nhiều mẫu thiết kế và ví dụ thực tế.

* * *

# 1\. Sai lầm phổ biến

Rất nhiều lập trình viên nghĩ:
    
    
    Framework = Library lớn

Đây là **không đúng**.

Ví dụ:
    
    
    NumPy
    Pandas
    Requests
    Rich

Có hàng chục nghìn dòng code.

Nhưng chúng **không phải Framework**.

* * *

# 2\. Library là gì?

Library là tập hợp các hàm hoặc lớp mà **bạn chủ động gọi**.

Ví dụ:
    
    
    from pathlib import Path
    
    p = Path("data.txt")
    
    print(p.exists())

Ai gọi `exists()`?

Chính bạn.

Luồng chương trình:
    
    
    main()
    
    ↓
    
    Path.exists()
    
    ↓
    
    main()

Bạn là người điều khiển.

* * *

Ví dụ với `requests`
    
    
    import requests
    
    response = requests.get("https://example.com")

Bạn quyết định:

  * gọi lúc nào 
  * gọi bao nhiêu lần 
  * gọi với tham số nào 



Library hoàn toàn bị động.

* * *

# 3\. Framework là gì?

Framework thì ngược lại.

Ví dụ Flask:
    
    
    @app.route("/")
    def home():
        return "Hello"

Bạn không hề viết:
    
    
    home()

Flask sẽ gọi.

Luồng:
    
    
    Browser
    
    ↓
    
    Flask
    
    ↓
    
    home()

Flask kiểm soát.

* * *

# 4\. So sánh

## Library
    
    
    Bạn
    
    ↓
    
    Library

* * *

## Framework
    
    
    Bạn
    
    ↓
    
    Framework
    
    ↓
    
    Code của bạn

Đây là điểm khác biệt lớn nhất.

* * *

# 5\. Một ví dụ dễ hiểu

Giả sử bạn có một chiếc máy khoan.

Library
    
    
    Bạn
    
    ↓
    
    Cầm máy khoan
    
    ↓
    
    Khoan tường

Bạn điều khiển.

* * *

Framework

Giống như một dây chuyền sản xuất.
    
    
    Bạn đặt linh kiện
    
    ↓
    
    Dây chuyền
    
    ↓
    
    Máy tự lắp ráp

Bạn không điều khiển từng bước.

* * *

# 6\. Inversion of Control (IoC)

Đây là khái niệm quan trọng nhất.

Library
    
    
    main()
    
    ↓
    
    logger()
    
    ↓
    
    database()
    
    ↓
    
    service()

Main điều khiển.

* * *

Framework
    
    
    Framework.start()
    
    ↓
    
    Framework
    
    ↓
    
    logger()
    
    ↓
    
    database()
    
    ↓
    
    plugin()
    
    ↓
    
    Application.run()

Framework điều khiển.

* * *

Tức là:
    
    
    Quyền điều khiển
    
    đã bị đảo ngược

Đó là **Inversion of Control**.

* * *

# 7\. Ví dụ bằng code

## Library
    
    
    class Logger:
    
        def info(self, message):
            print(message)
    
    
    logger = Logger()
    
    logger.info("Hello")

Output
    
    
    Hello

Bạn gọi Logger.

* * *

## Framework
    
    
    class Logger:
    
        def info(self, message):
            print(message)
    
    
    class Framework:
    
        def __init__(self):
            self.logger = Logger()
    
        def start(self):
    
            self.logger.info("Framework started")
    
            self.run()
    
        def run(self):
            print("Business")

Main
    
    
    Framework().start()

Output
    
    
    Framework started
    
    Business

Framework gọi Logger.

* * *

# 8\. Ví dụ với Plugin

Library
    
    
    plugin.run()

Bạn quyết định.

* * *

Framework
    
    
    class Framework:
    
        def load_plugins(self):
    
            for plugin in self.plugins:
    
                plugin.run()

Plugin không tự chạy.

Framework chạy plugin.

* * *

# 9\. Ví dụ với Event

Library
    
    
    event.emit()

Bạn emit.

* * *

Framework
    
    
    class Framework:
    
        def request(self):
    
            self.before_request()
    
            ...
    
            self.after_request()

Framework emit event.

* * *

# 10\. Ví dụ với CLI

Click

Bạn viết
    
    
    @click.command()
    def hello():
        print("Hello")

Bạn không gọi
    
    
    hello()

Click sẽ:
    
    
    Đọc argv
    
    ↓
    
    Parse
    
    ↓
    
    Validate
    
    ↓
    
    Inject parameter
    
    ↓
    
    hello()

* * *

# 11\. Ví dụ với pytest

Bạn chỉ viết
    
    
    def test_login():
        ...

pytest
    
    
    Scan folder
    
    ↓
    
    Find tests
    
    ↓
    
    Create fixtures
    
    ↓
    
    Inject fixtures
    
    ↓
    
    Run test
    
    ↓
    
    Generate report

Bạn không hề gọi test.

* * *

# 12\. Ví dụ với FastAPI

Bạn viết
    
    
    @app.get("/users")
    def users():
        ...

Framework:
    
    
    Receive HTTP Request
    
    ↓
    
    Routing
    
    ↓
    
    Validation
    
    ↓
    
    Dependency Injection
    
    ↓
    
    Call users()
    
    ↓
    
    Convert JSON
    
    ↓
    
    Response

* * *

# 13\. Ví dụ với Celery

Bạn chỉ viết
    
    
    @app.task
    def send_email():
        ...

Framework
    
    
    RabbitMQ
    
    ↓
    
    Worker
    
    ↓
    
    Deserialize
    
    ↓
    
    Retry
    
    ↓
    
    Logging
    
    ↓
    
    send_email()

* * *

# 14\. Mini Framework

Bây giờ hãy xây một framework có IoC.
    
    
    project/
    
        framework.py
    
        application.py
    
        main.py

* * *

## application.py
    
    
    class Application:
    
        def initialize(self):
            print("Application initialized")
    
        def run(self):
            print("Application running")

* * *

## framework.py
    
    
    class Framework:
    
        def __init__(self, application):
    
            self.application = application
    
        def load_config(self):
            print("Load config")
    
        def load_logger(self):
            print("Load logger")
    
        def boot(self):
            print("Boot framework")
    
        def start(self):
    
            self.load_config()
    
            self.load_logger()
    
            self.boot()
    
            self.application.initialize()
    
            self.application.run()

* * *

## main.py
    
    
    from framework import Framework
    from application import Application
    
    app = Application()
    
    framework = Framework(app)
    
    framework.start()

Output
    
    
    Load config
    
    Load logger
    
    Boot framework
    
    Application initialized
    
    Application running

* * *

# 15\. Điều gì xảy ra nếu không có Framework?

Ứng dụng sẽ phải tự làm mọi việc:
    
    
    config.load()
    
    logger.init()
    
    database.connect()
    
    plugin.load()
    
    service.start()
    
    app.run()

Sau vài năm, bạn sẽ thấy các dự án đều lặp lại những bước này.

Framework ra đời để gom những phần chung thành một bộ khung tái sử dụng.

* * *

# 16\. "Hollywood Principle"

Framework thường tuân theo nguyên lý nổi tiếng:

> **"Don't call us, we'll call you."**

Bạn chỉ cần cung cấp:
    
    
    class Application:
    
        def run(self):
            ...

Framework sẽ quyết định:

  * Khi nào gọi. 
  * Gọi bao nhiêu lần. 
  * Gọi theo thứ tự nào. 
  * Gọi trong ngữ cảnh nào. 



* * *

# 17\. So sánh kiến trúc

## Ứng dụng dùng Library
    
    
            main.py
               │
     ┌─────────┼─────────┐
     │         │         │
     ▼         ▼         ▼
    Logger   SQLite   Requests

`main.py` phải điều phối tất cả.

* * *

## Ứng dụng dùng Framework
    
    
              main.py
                 │
                 ▼
          Framework.start()
                 │
     ┌───────────┼────────────┐
     ▼           ▼            ▼
    Logger    Container    Plugins
                 │
                 ▼
          Application.run()

`main.py` rất nhỏ, còn framework trở thành "bộ điều phối trung tâm".

* * *

# 18\. Tư duy thiết kế

Khi viết **Application** , hãy hỏi:

> "Làm sao giải quyết bài toán?"

Ví dụ:
    
    
    Làm sao đăng nhập?
    Làm sao lưu dữ liệu?
    Làm sao cào truyện?

Khi viết **Framework** , hãy hỏi:

> "Làm sao để bất kỳ ứng dụng nào cũng có thể giải quyết bài toán này theo cùng một cách?"

Ví dụ:

  * Làm sao mọi plugin đều có thể đăng ký? 
  * Làm sao mọi service đều được khởi tạo đúng thứ tự? 
  * Làm sao mọi ứng dụng đều có lifecycle nhất quán? 



Đây là tư duy chuyển từ **người viết ứng dụng** sang **người thiết kế nền tảng**.

* * *

# Tổng kết

Trong buổi học này, chúng ta đã rút ra ba ý chính:

  1. **Library** là tập hợp công cụ mà **ứng dụng gọi**. 
  2. **Framework** là bộ khung **gọi ứng dụng** và quản lý toàn bộ vòng đời của nó. 
  3. **Inversion of Control (IoC)** là nguyên lý cốt lõi tạo nên sự khác biệt giữa hai mô hình trên. 



Hiểu rõ ba điểm này sẽ giúp bạn đọc kiến trúc của Django, FastAPI, Click, Celery hay pytest dễ dàng hơn, vì tất cả đều dựa trên cùng một nguyên lý.

* * *

# Bài tập

### Bài 1

Mở rộng `Framework.start()` theo thứ tự:
    
    
    Load Config
    ↓
    Load Logger
    ↓
    Create Database
    ↓
    Load Plugins
    ↓
    Initialize Application
    ↓
    Run Application

Mỗi bước là một phương thức riêng.

* * *

### Bài 2

Tạo lớp `Plugin`:
    
    
    class Plugin:
        def initialize(self):
            print("Plugin initialized")

Cho `Framework` nhận danh sách plugin và tự động gọi `initialize()` trước khi chạy `Application`.

* * *

### Bài 3

Thêm một lớp `Lifecycle` với các hook:
    
    
    before_start()
    after_start()
    before_stop()
    after_stop()

Để `Framework` gọi các hook này đúng thứ tự. Đây sẽ là nền tảng cho **Lifecycle Management** mà chúng ta sẽ học ở buổi 5.

* * *

## Chuẩn bị cho buổi 3

Ở **Buổi 3: Inversion of Control (IoC)** , chúng ta sẽ đi sâu vào bản chất của IoC, phân biệt IoC với Dependency Injection (DI), tìm hiểu các cách hiện thực IoC (callback, event, template method, service locator...), và bắt đầu xây dựng **IoC Container** đầu tiên cho framework của chúng ta.

