# Framework Design Deep Dive

# Buổi 3: Inversion of Control (IoC) Deep Dive

> **Mục tiêu**
> 
> Sau buổi này bạn sẽ hiểu:
> 
>   * IoC thực sự là gì (không chỉ là định nghĩa). 
>   * Tại sao IoC là nền tảng của mọi framework hiện đại. 
>   * Các cách hiện thực IoC. 
>   * IoC khác Dependency Injection (DI) như thế nào. 
>   * Xây dựng mini IoC Framework đầu tiên. 
> 


* * *

# Roadmap
    
    
    PHẦN I - Framework Mindset
    
    ✔ Buổi 1. Framework là gì?
    
    ✔ Buổi 2. Library vs Framework
    
    ▶ Buổi 3. Inversion of Control
    
    Buổi 4. Dependency Injection
    
    Buổi 5. Lifecycle
    
    Buổi 6. Application Context
    
    Buổi 7. Service Container
    
    Buổi 8. Object Graph

> Sau buổi này bạn sẽ thấy hầu hết framework Python (Flask, FastAPI, Django, Click, pytest, Celery...) đều áp dụng IoC theo những cách khác nhau.

* * *

# 1\. Inversion of Control là gì?

Đừng nhớ định nghĩa.

Hãy nhớ hình ảnh.

## Chương trình bình thường
    
    
    main()
    
    ↓
    
    config()
    
    ↓
    
    logger()
    
    ↓
    
    database()
    
    ↓
    
    service()
    
    ↓
    
    run()

Bạn điều khiển mọi thứ.

* * *

Framework
    
    
    Framework.start()
    
    ↓
    
    Framework
    
    ↓
    
    config()
    
    ↓
    
    logger()
    
    ↓
    
    database()
    
    ↓
    
    Application.run()

Framework điều khiển.

Đó chính là:

> **Control đã bị đảo chiều.**

* * *

# 2\. "Control" là gì?

Ví dụ
    
    
    def load_config():
        print("Load config")
    
    
    def connect_db():
        print("Connect DB")
    
    
    def run():
        load_config()
        connect_db()
    
    run()

Ai quyết định:

  * load_config chạy trước? 
  * connect_db chạy sau? 



Chính `run()`.

Nó giữ quyền điều khiển.

* * *

# 3\. Đảo quyền điều khiển

Bây giờ đổi thành
    
    
    class Framework:
    
        def start(self):
            self.load_config()
            self.connect_db()
    
            self.application.run()

Application không biết:

  * Config ở đâu 
  * DB tạo lúc nào 
  * Logger khởi tạo khi nào 



Framework quyết định.

* * *

# 4\. Tại sao phải IoC?

Giả sử có 100 ứng dụng.

Không IoC.
    
    
    App1
    
    ↓
    
    Logger
    
    ↓
    
    Config
    
    ↓
    
    DB
    
    ↓
    
    Plugin

App2
    
    
    ↓
    
    Logger
    
    ↓
    
    Config
    
    ↓
    
    DB
    
    ↓
    
    Plugin

App3
    
    
    ↓
    
    Logger
    
    ↓
    
    Config
    
    ↓
    
    DB
    
    ↓
    
    Plugin

100 app.

100 lần lặp.

* * *

IoC
    
    
                 Framework
    
                    │
    
          ┌─────────┼──────────┐
    
          │         │          │
    
        App1      App2       App3

Framework lo tất cả.

Application chỉ viết nghiệp vụ.

* * *

# 5\. IoC không phải một kỹ thuật

Đây là điều rất nhiều người hiểu sai.

IoC KHÔNG phải:

  * class 
  * decorator 
  * DI 
  * container 



IoC là:

> **Một nguyên lý thiết kế (Design Principle).**

Có rất nhiều cách để hiện thực.

* * *

# 6\. Có bao nhiêu cách hiện thực IoC?

Có rất nhiều.

Ví dụ
    
    
    Template Method
    
    Callback
    
    Hook
    
    Observer
    
    Event
    
    Signal
    
    Middleware
    
    Plugin
    
    Dependency Injection
    
    Service Locator
    
    Pipeline
    
    Command Dispatcher

Bạn sẽ gặp tất cả trong khóa học này.

* * *

# 7\. IoC bằng Callback

Ví dụ
    
    
    def framework(callback):
    
        print("Before")
    
        callback()
    
        print("After")

Application
    
    
    def app():
    
        print("Business")

Main
    
    
    framework(app)

Output
    
    
    Before
    
    Business
    
    After

Framework quyết định:

  * gọi lúc nào 
  * gọi bao nhiêu lần 



Đây chính là IoC.

* * *

# 8\. IoC bằng kế thừa (Template Method)

Framework
    
    
    class Framework:
    
        def start(self):
    
            print("Before")
    
            self.run()
    
            print("After")
    
        def run(self):
            raise NotImplementedError

Application
    
    
    class MyApp(Framework):
    
        def run(self):
            print("Business")

Main
    
    
    app = MyApp()
    
    app.start()

Output
    
    
    Before
    
    Business
    
    After

Framework kiểm soát.

* * *

# 9\. IoC bằng Event

Framework
    
    
    class EventManager:
    
        def __init__(self):
            self.listeners = []
    
        def register(self, callback):
            self.listeners.append(callback)
    
        def emit(self):
    
            for callback in self.listeners:
                callback()

Application
    
    
    def business():
        print("Business")
    
    
    manager = EventManager()
    
    manager.register(business)
    
    manager.emit()

Framework quyết định emit.

* * *

# 10\. IoC bằng Hook

Framework
    
    
    class Framework:
    
        def before_request(self):
            pass
    
        def after_request(self):
            pass
    
        def handle(self):
    
            self.before_request()
    
            print("Request")
    
            self.after_request()

Application
    
    
    class MyFramework(Framework):
    
        def before_request(self):
            print("Auth")
    
        def after_request():
            print("Log")

Framework gọi hook.

* * *

# 11\. IoC bằng Plugin

Plugin
    
    
    class HelloPlugin:
    
        def start(self):
            print("Hello")

Framework
    
    
    class Framework:
    
        def __init__(self):
            self.plugins = []
    
        def register(self, plugin):
            self.plugins.append(plugin)
    
        def start(self):
    
            for plugin in self.plugins:
                plugin.start()

Plugin không tự chạy.

Framework chạy.

* * *

# 12\. IoC bằng Decorator

Ví dụ Flask
    
    
    @app.route("/")
    def home():
        ...

Decorator chỉ đăng ký.

Sau này framework mới gọi.

* * *

Ví dụ Click
    
    
    @click.command()
    def hello():
        ...

`hello()` không chạy.

Click chỉ ghi nhớ.

Sau này mới thực thi.

* * *

# 13\. IoC bằng Generator

Framework
    
    
    def framework():
    
        print("before")
    
        yield
    
        print("after")

Application
    
    
    f = framework()
    
    next(f)
    
    print("Business")
    
    next(f, None)

Ý tưởng này xuất hiện trong:

  * pytest fixture 
  * Context Manager 
  * Middleware 



* * *

# 14\. IoC bằng Context Manager
    
    
    with framework():
    
        business()

Framework
    
    
    Enter
    
    ↓
    
    Business
    
    ↓
    
    Exit

Ứng dụng không điều khiển vòng đời.

* * *

# 15\. IoC trong FastAPI

Bạn viết
    
    
    @app.get("/users")
    def users():
        ...

Framework làm
    
    
    Receive Request
    
    ↓
    
    Parse
    
    ↓
    
    Validate
    
    ↓
    
    Create Dependency
    
    ↓
    
    Call users()
    
    ↓
    
    Serialize
    
    ↓
    
    Response

Bạn chỉ viết:
    
    
    def users():

* * *

# 16\. IoC trong pytest

Bạn viết
    
    
    def test_login(db):

Framework
    
    
    Create DB
    
    ↓
    
    Inject DB
    
    ↓
    
    Run Test
    
    ↓
    
    Destroy DB

Không cần tự tạo DB.

* * *

# 17\. IoC khác DI như thế nào?

Đây là câu hỏi phỏng vấn rất hay.

Nhiều người trả lời sai.

IoC
    
    
    Framework điều khiển.

DI
    
    
    Framework cung cấp dependency.

DI chỉ là **một cách hiện thực IoC**.

Quan hệ:
    
    
    IoC
    
    ├── Callback
    
    ├── Hook
    
    ├── Event
    
    ├── Plugin
    
    ├── Middleware
    
    ├── Template Method
    
    └── Dependency Injection

IoC lớn hơn DI.

* * *

# 18\. Mini IoC Framework

Cấu trúc
    
    
    project/
    
        framework.py
    
        application.py
    
        main.py

* * *

## application.py
    
    
    class Application:
    
        def initialize(self):
            print("Initialize Application")
    
        def run(self):
            print("Business Logic")

* * *

## framework.py
    
    
    class Framework:
    
        def __init__(self, app):
            self.app = app
    
        def load_config(self):
            print("Load Config")
    
        def load_logger(self):
            print("Load Logger")
    
        def load_plugins(self):
            print("Load Plugins")
    
        def before_run(self):
            print("Before Run")
    
        def after_run(self):
            print("After Run")
    
        def start(self):
            self.load_config()
            self.load_logger()
            self.load_plugins()
    
            self.before_run()
    
            self.app.initialize()
            self.app.run()
    
            self.after_run()

* * *

## main.py
    
    
    from framework import Framework
    from application import Application
    
    app = Application()
    
    framework = Framework(app)
    
    framework.start()

Kết quả
    
    
    Load Config
    Load Logger
    Load Plugins
    Before Run
    Initialize Application
    Business Logic
    After Run

Toàn bộ luồng thực thi do `Framework.start()` điều phối. `Application` chỉ tập trung vào nghiệp vụ.

* * *

# 19\. Kiến trúc IoC
    
    
                    main.py
    
                        │
    
                        ▼
    
              Framework.start()
    
                        │
    
         ┌──────────────┼──────────────┐
    
         ▼              ▼              ▼
    
     Config         Logger        Plugins
    
                        │
    
                        ▼
    
              before_run()
    
                        │
    
                        ▼
    
          Application.initialize()
    
                        │
    
                        ▼
    
            Application.run()
    
                        │
    
                        ▼
    
               after_run()

Đây chính là "xương sống" của rất nhiều framework hiện đại.

* * *

# Tổng kết

Trong buổi học này, bạn cần ghi nhớ ba ý quan trọng:

  1. **IoC là một nguyên lý thiết kế** , không phải một thư viện hay một kỹ thuật cụ thể. 
  2. **Framework giữ quyền điều khiển** , còn mã của bạn được gọi vào những thời điểm thích hợp. 
  3. **Dependency Injection chỉ là một cách để hiện thực IoC** , không phải IoC đồng nghĩa với DI. 



Nếu hiểu chắc ba điểm này, bạn sẽ dễ dàng tiếp cận kiến trúc của các framework lớn.

* * *

# Bài tập

## Bài 1

Viết `Framework` có các hook:
    
    
    before_start()
    before_initialize()
    before_run()
    after_run()
    after_stop()

Hãy in ra thứ tự thực thi để kiểm chứng vòng đời.

* * *

## Bài 2

Hiện thực IoC bằng **Callback** :

  * `Framework.start(callback)`
  * Framework in `"Before"`. 
  * Gọi callback. 
  * Framework in `"After"`. 



Thử thay callback bằng nhiều hàm khác nhau.

* * *

## Bài 3

Hiện thực IoC bằng **Template Method** :

  * Tạo lớp `Framework` với phương thức `start()`. 
  * `start()` gọi `setup()`, `run()`, `cleanup()`. 
  * Cho phép lớp con ghi đè `run()`. 



Quan sát cách framework giữ nguyên quy trình nhưng cho phép thay đổi từng bước.

* * *

# Chuẩn bị cho buổi 4

Ở **Buổi 4: Dependency Injection Deep Dive** , chúng ta sẽ xây dựng hệ thống **Dependency Injection** từ con số 0:

  * Constructor Injection. 
  * Setter Injection. 
  * Method Injection. 
  * Interface Injection. 
  * So sánh Service Locator và DI. 
  * Tự xây một **DI Container** đơn giản, nền tảng để phát triển thành **Service Container** chuyên nghiệp ở các buổi tiếp theo.

