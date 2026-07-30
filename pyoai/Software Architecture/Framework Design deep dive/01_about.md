# Framework Design Deep Dive

# Buổi 1: Framework là gì? — Tư duy của người thiết kế Framework

> Mục tiêu buổi học:
> 
> Sau buổi này bạn sẽ hiểu:
> 
>   * Framework thực sự là gì. 
>   * Framework khác Library ở đâu. 
>   * Vì sao các công ty lớn đều tự xây framework. 
>   * Framework được cấu thành từ những phần nào. 
>   * Thiết kế framework khác viết application như thế nào. 
>   * Bắt đầu xây framework đầu tiên. 
> 


* * *

# 1\. Chúng ta đang viết Application hay Framework?

Giả sử bạn viết app quản lý sinh viên.
    
    
    Student App
    
    main.py
     ↓
    SQLite
     ↓
    UI
     ↓
    Business

Mọi thứ đều phục vụ **một ứng dụng duy nhất**.

Ví dụ
    
    
    Student
    Teacher
    Class

Đây là **Application**.

* * *

Bây giờ giả sử bạn lại cần viết

  * App bán hàng 
  * App quản lý kho 
  * App quản lý thư viện 
  * App cào truyện 
  * App CRM 



Bạn phát hiện:
    
    
    Đăng nhập
    
    SQLite
    
    Config
    
    Logging
    
    Plugin
    
    Command
    
    Cache
    
    Repository
    
    Event

Tất cả đều lặp lại.

Lúc này ta bắt đầu nghĩ:

> "Có cách nào viết một lần dùng nhiều lần?"

Đó là lúc Framework ra đời.

* * *

# 2\. Framework là gì?

Framework là:

> Một bộ khung (skeleton) định nghĩa cách xây dựng ứng dụng.

Nó không giải quyết bài toán cụ thể.

Nó giải quyết **cách tổ chức** bài toán.

Ví dụ

Application
    
    
    Student App

Framework
    
    
    Bạn hãy đặt Student vào đây.
    
    Tôi sẽ lo:
    
    Logging
    
    Config
    
    Routing
    
    Plugin
    
    Event
    
    Lifecycle
    
    Dependency

* * *

## Ví dụ

Không dùng framework
    
    
    main.py
    
    ↓
    
    tự mở config
    
    ↓
    
    tự tạo logger
    
    ↓
    
    tự tạo database
    
    ↓
    
    tự tạo service
    
    ↓
    
    tự chạy

Dùng framework
    
    
    main.py
    
    ↓
    
    Framework.start()
    
    ↓
    
    Framework tự làm hết
    
    ↓
    
    Application chỉ viết business

Đó là điểm khác biệt lớn nhất.

* * *

# 3\. Hình dung Framework

Một chiếc xe hơi
    
    
    Engine
    
    ↓
    
    Transmission
    
    ↓
    
    Brake
    
    ↓
    
    Steering
    
    ↓
    
    Body

Người mua xe chỉ việc lái.

* * *

Application cũng vậy.

Framework
    
    
    Engine
    
    Logger
    
    Config
    
    Container
    
    Plugin
    
    Command
    
    Lifecycle
    
    Scheduler

Application chỉ viết
    
    
    Business

* * *

# 4\. Tư duy Application Developer

Một lập trình viên bình thường sẽ nghĩ:
    
    
    Làm sao viết tính năng này?

Ví dụ
    
    
    Đăng nhập
    
    ↓
    
    Viết login()
    
    ↓
    
    Xong

* * *

Framework Developer nghĩ:
    
    
    Nếu mai sau có:
    
    Google Login
    
    Facebook Login
    
    Github Login
    
    LDAP
    
    OAuth
    
    SSO
    
    thì sao?

Họ thiết kế:
    
    
    Login Interface
    
    ↓
    
    Plugin
    
    ↓
    
    Provider
    
    ↓
    
    Inject

Đó là tư duy framework.

* * *

# 5\. Framework không giải quyết bài toán

Ví dụ

Framework không biết:
    
    
    Student
    
    Book
    
    Movie
    
    Crawler
    
    Music

Nó chỉ biết:
    
    
    Model
    
    Repository
    
    Controller
    
    Command
    
    Plugin
    
    Service

Framework càng tổng quát càng tốt.

* * *

# 6\. Một Framework gồm những gì?

Một framework chuyên nghiệp thường gồm:
    
    
                   +--------------------+
                   |   Application      |
                   +----------+---------+
                              |
                 +------------v------------+
                 |      Framework Core     |
                 +------------+------------+
                              |
          +---------+---------+---------+---------+
          |         |         |         |         |
       Config    Logger   Container   Event   Plugin
          |         |         |         |         |
          +---------+---------+---------+---------+
                              |
                         Runtime Engine

* * *

Các thành phần:
    
    
    Application
    
    ↓
    
    Core
    
    ↓
    
    Config
    
    ↓
    
    Logger
    
    ↓
    
    Event
    
    ↓
    
    Command
    
    ↓
    
    Plugin
    
    ↓
    
    Dependency Injection
    
    ↓
    
    Lifecycle
    
    ↓
    
    Scheduler
    
    ↓
    
    Background Worker
    
    ↓
    
    ...

Chúng ta sẽ xây từng phần.

* * *

# 7\. Framework không phải Library

Đây là phần quan trọng nhất hôm nay.

Giả sử có Logger.

Library
    
    
    logger.info("Hello")

Bạn gọi logger.
    
    
    Application
    
    ↓
    
    Logger

* * *

Framework
    
    
    class MyFramework:
    
        def start(self):
            logger.init()
    
            logger.info("Starting...")
    
            self.run()

Framework gọi logger.
    
    
    Application
    
    ↓
    
    Framework
    
    ↓
    
    Logger

Ứng dụng không biết logger được tạo lúc nào.

Framework quản lý.

* * *

# 8\. Kiến trúc Framework

Một framework tối thiểu
    
    
              start()
    
                 │
    
                 ▼
    
          Load Config
    
                 │
    
                 ▼
    
         Create Logger
    
                 │
    
                 ▼
    
         Create Container
    
                 │
    
                 ▼
    
          Load Plugins
    
                 │
    
                 ▼
    
          Register Services
    
                 │
    
                 ▼
    
          Start Runtime
    
                 │
    
                 ▼
    
          Run Application

Đây là Boot Process.

Sau này ta sẽ xây đầy đủ.

* * *

# 9\. Viết Framework đầu tiên

Cấu trúc:
    
    
    myframework/
    
        framework/
    
            app.py
    
        app.py

* * *

## framework/app.py
    
    
    class Framework:
    
        def start(self):
            print("Loading config...")
    
            print("Loading logger...")
    
            print("Loading plugins...")
    
            print("Running application...")

* * *

## app.py
    
    
    from framework.app import Framework
    
    app = Framework()
    
    app.start()

Kết quả
    
    
    Loading config...
    
    Loading logger...
    
    Loading plugins...
    
    Running application...

Đây là framework nhỏ nhất.

Application không biết bên trong framework làm gì.

* * *

# 10\. Bổ sung Application

Framework sẽ gọi Application.
    
    
    framework/
    
        app.py
    
    application.py
    
    main.py

* * *

## application.py
    
    
    class Application:
    
        def run(self):
            print("Business Logic")

* * *

## framework/app.py
    
    
    class Framework:
    
        def __init__(self, application):
            self.application = application
    
        def start(self):
            print("Loading config")
            print("Loading logger")
            print("Loading plugins")
    
            self.application.run()

* * *

## main.py
    
    
    from framework.app import Framework
    from application import Application
    
    app = Application()
    
    framework = Framework(app)
    
    framework.start()

Kết quả:
    
    
    Loading config
    Loading logger
    Loading plugins
    Business Logic

Đây là mô hình mà nhiều framework thực tế sử dụng: framework khởi động, sau đó mới chuyển quyền điều khiển cho mã nghiệp vụ của bạn.

* * *

# 11\. Phân tích một số Framework nổi tiếng

## Flask
    
    
    app = Flask(__name__)
    
    @app.route("/")
    def index():
        return "Hello"

Bạn chỉ khai báo route.

Flask sẽ:

  * Khởi động server. 
  * Nhận HTTP request. 
  * Chọn đúng hàm `index`. 
  * Trả HTTP response. 
  * Quản lý vòng đời request. 



Bạn **không** gọi `index()` trực tiếp.

* * *

## Click
    
    
    @click.command()
    def hello():
        print("Hello")

Bạn không tự gọi `hello()`.

Click:

  * Phân tích tham số dòng lệnh. 
  * Kiểm tra lỗi. 
  * Hiển thị trợ giúp. 
  * Gọi `hello()` khi phù hợp. 



* * *

## pytest
    
    
    def test_add():
        ...

Bạn không gọi `test_add()`.

`pytest`:

  * Tìm các file kiểm thử. 
  * Thu thập các hàm test. 
  * Thiết lập fixture. 
  * Thực thi và tổng hợp kết quả. 



* * *

## FastAPI
    
    
    @app.get("/")
    def index():
        return {}

FastAPI:

  * Chạy ASGI server. 
  * Định tuyến request. 
  * Chuyển đổi dữ liệu đầu vào. 
  * Kiểm tra kiểu dữ liệu. 
  * Gọi `index()`. 
  * Chuyển kết quả thành JSON. 



* * *

# 12\. Một dấu hiệu nhận biết Framework

Hãy tự hỏi:

> **Ai đang điều khiển luồng thực thi?**

Nếu **bạn** gọi API:
    
    
    logger.info(...)

→ Thường là **Library**.

Nếu **framework** quyết định khi nào gọi mã của bạn:
    
    
    framework.start()
    # ...
    # Framework gọi application.run()

→ Đó là **Framework**.

Đây chính là ý tưởng cốt lõi của **Inversion of Control (IoC)** , sẽ được học kỹ ở buổi 3.

* * *

# 13\. Tổng kết buổi 1

Một framework không chỉ là tập hợp các module. Nó là một **bộ máy điều phối** (orchestrator):

  * Khởi tạo môi trường chạy. 
  * Quản lý các thành phần dùng chung. 
  * Điều khiển vòng đời ứng dụng. 
  * Quyết định thời điểm mã nghiệp vụ được thực thi. 



Vì vậy, khi thiết kế framework, mục tiêu không phải là viết thêm nhiều tính năng, mà là **xây dựng một cấu trúc đủ linh hoạt để nhiều ứng dụng khác nhau có thể hoạt động trên cùng một bộ khung**.

* * *

# Bài tập thực hành

## Bài 1

Mở rộng `Framework.start()` thành các bước:
    
    
    Load Config
    ↓
    Init Logger
    ↓
    Create Container
    ↓
    Load Plugins
    ↓
    Register Services
    ↓
    Run Application

In ra màn hình đúng thứ tự khởi động.

* * *

## Bài 2

Tạo lớp `Application` với hai phương thức:
    
    
    class Application:
        def initialize(self):
            ...
    
        def run(self):
            ...

Hãy để `Framework.start()` gọi:
    
    
    initialize()
    ↓
    run()

* * *

## Bài 3

Thêm lớp `Plugin`:
    
    
    class Plugin:
        def load(self):
            print("Plugin loaded")

Yêu cầu `Framework` có thể nhận danh sách plugin và gọi `load()` cho từng plugin trong quá trình khởi động. Đây sẽ là nền tảng cho hệ thống Plugin Framework ở các buổi sau.

* * *

### Chuẩn bị cho buổi 2

Ở **Buổi 2: Library vs Framework** , chúng ta sẽ đi sâu vào sự khác biệt giữa hai khái niệm này, phân tích **Inversion of Control** ở mức trực quan, và mổ xẻ kiến trúc của các framework như Flask, Django, FastAPI, Click và pytest để thấy vì sao chúng hoạt động theo cách đó. Đây là nền tảng quan trọng trước khi bắt đầu xây dựng framework hoàn chỉnh.

