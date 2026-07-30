# ABC Deep Dive - Buổi 6

# Abstract Class + Concrete Method + Template Method Pattern

Đến buổi này, chúng ta sẽ học cách **xây dựng framework thực sự**.

Đây là kỹ thuật được sử dụng trong:

  * Django 
  * unittest 
  * pathlib 
  * io 
  * asyncio 
  * logging 
  * Scrapy 
  * SQLAlchemy 



Đặc biệt, **hệ thống crawler truyện** mà bạn đang xây dựng cũng nên áp dụng mô hình này.

* * *

# Mục tiêu

Sau buổi học này bạn sẽ hiểu:

  * Abstract Method 
  * Concrete Method 
  * Hook Method 
  * Template Method Pattern 
  * Inversion of Control (IoC) 
  * Framework Design 
  * Áp dụng vào dự án crawler 



* * *

# 1\. Abstract Class không chỉ chứa Abstract Method

Rất nhiều người nghĩ:
    
    
    class Animal(ABC):
    
        @abstractmethod
        def speak(self):
            ...

là đủ.

Thực tế, một Abstract Class thường chứa:

  * Abstract Method 
  * Concrete Method 
  * Helper Method 
  * Private Method 
  * Protected Method 
  * Class Method 
  * Static Method 
  * Property 



Đây mới là cách các framework lớn được thiết kế.

* * *

# 2\. Ví dụ đơn giản
    
    
    from abc import ABC, abstractmethod
    
    
    class Animal(ABC):
    
        @abstractmethod
        def speak(self):
            pass
    
        def sleep(self):
            print("Sleeping...")

Subclass
    
    
    class Dog(Animal):
    
        def speak(self):
            print("Woof")

Sử dụng
    
    
    dog = Dog()
    
    dog.speak()
    dog.sleep()

Kết quả
    
    
    Woof
    Sleeping...

* * *

# 3\. Nhưng đây chưa phải Template Method

Ví dụ trên chỉ có:
    
    
    Abstract Method
    
    +
    
    Concrete Method

Template Method còn mạnh hơn nhiều.

* * *

# 4\. Template Method Pattern là gì?

Ý tưởng:

Framework quyết định:
    
    
    Bước 1
    
    ↓
    
    Bước 2
    
    ↓
    
    Bước 3
    
    ↓
    
    Bước 4

Lớp con **không được thay đổi thứ tự**.

Chúng chỉ được thay đổi:
    
    
    Bước 2
    
    Bước 4

* * *

Ví dụ:
    
    
    Pha cà phê
    
    ↓
    
    Đun nước
    
    ↓
    
    Cho cà phê
    
    ↓
    
    Rót nước
    
    ↓
    
    Uống

Người dùng chỉ thay đổi:
    
    
    Cho cà phê

Không thay đổi:
    
    
    Đun nước
    
    ↓
    
    Rót nước

* * *

# 5\. Ví dụ đầu tiên
    
    
    from abc import ABC, abstractmethod
    
    
    class Coffee(ABC):
    
        def make(self):
    
            self.boil_water()
    
            self.add_coffee()
    
            self.pour()
    
        def boil_water(self):
            print("Boil water")
    
        @abstractmethod
        def add_coffee(self):
            pass
    
        def pour(self):
            print("Pour into cup")

Subclass
    
    
    class Espresso(Coffee):
    
        def add_coffee(self):
            print("Espresso Powder")

Sử dụng
    
    
    coffee = Espresso()
    
    coffee.make()

Kết quả
    
    
    Boil water
    
    Espresso Powder
    
    Pour into cup

* * *

# Đây chính là Template Method

Framework quyết định:
    
    
    make()
    
    ↓
    
    boil_water()
    
    ↓
    
    add_coffee()
    
    ↓
    
    pour()

Subclass chỉ thay đổi:
    
    
    add_coffee()

* * *

# 6\. Áp dụng vào Crawler

Đây chính là nơi ABC phát huy sức mạnh.

Thay vì:
    
    
    class TruyenFull:
    
        def crawl(self):
            ...
    
    
    class Wattpad:
    
        def crawl(self):
            ...

Mỗi plugin tự viết toàn bộ quy trình, ta xây dựng một lớp cơ sở điều phối.

* * *

# 7\. Thiết kế Framework
    
    
    from abc import ABC, abstractmethod
    
    
    class BaseCrawler(ABC):
    
        def crawl(self, keyword):
    
            url = self.search(keyword)
    
            data = self.get_detail(url)
    
            chapters = self.get_chapters(data)
    
            self.save(chapters)
    
        @abstractmethod
        def search(self, keyword):
            ...
    
        @abstractmethod
        def get_detail(self, url):
            ...
    
        @abstractmethod
        def get_chapters(self, data):
            ...
    
        def save(self, chapters):
    
            print("Saving...")

* * *

Plugin
    
    
    class TruyenFullCrawler(BaseCrawler):
    
        def search(self, keyword):
    
            print("Search TruyenFull")
    
            return "/abc"
    
        def get_detail(self, url):
    
            print("Detail")
    
            return {}
    
        def get_chapters(self, data):
    
            print("Chapters")
    
            return []

Sử dụng
    
    
    crawler = TruyenFullCrawler()
    
    crawler.crawl("Harry Potter")

Kết quả
    
    
    Search TruyenFull
    
    Detail
    
    Chapters
    
    Saving...

* * *

# Điều quan trọng

Plugin **không được phép** thay đổi:
    
    
    crawl()

Framework quyết định:
    
    
    search()
    
    ↓
    
    detail()
    
    ↓
    
    chapters()
    
    ↓
    
    save()

* * *

# 8\. Hook Method

Không phải mọi phương thức đều phải là abstract.

Ví dụ
    
    
    class BaseCrawler(ABC):
    
        def before_crawl(self):
            pass
    
        def after_crawl(self):
            pass

Framework
    
    
    def crawl(self, keyword):
    
        self.before_crawl()
    
        ...
    
        self.after_crawl()

Subclass
    
    
    class MyCrawler(BaseCrawler):
    
        def before_crawl(self):
    
            print("Login")

Đây gọi là:
    
    
    Hook Method

* * *

# Hook khác Abstract ở đâu?

Abstract
    
    
    Bắt buộc viết

Hook
    
    
    Muốn viết cũng được
    
    Không viết cũng được

* * *

# 9\. Framework thật

Ví dụ
    
    
    class BaseCrawler(ABC):
    
        def crawl(self, keyword):
    
            self.before()
    
            url = self.search(keyword)
    
            detail = self.get_detail(url)
    
            chapters = self.get_chapters(detail)
    
            self.save(chapters)
    
            self.after()
    
        def before(self):
            pass
    
        @abstractmethod
        def search(self, keyword):
            ...
    
        @abstractmethod
        def get_detail(self, url):
            ...
    
        @abstractmethod
        def get_chapters(self, detail):
            ...
    
        def save(self, chapters):
            print("Save Database")
    
        def after(self):
            pass

Đây là mô hình phổ biến trong nhiều framework.

* * *

# 10\. Inversion of Control (IoC)

Đây là tư tưởng quan trọng.

Thông thường:
    
    
    Application
    
    ↓
    
    Plugin

Plugin quyết định mọi thứ.

Trong Template Method:
    
    
    Framework
    
    ↓
    
    Plugin

Framework gọi plugin.

Plugin không tự chạy.

Đây gọi là:
    
    
    Inversion of Control

Hay:
    
    
    Hollywood Principle

> **"Don't call us, we'll call you."**  
>  (Đừng gọi chúng tôi, chúng tôi sẽ gọi bạn.)

Đây là triết lý cốt lõi của rất nhiều framework hiện đại.

* * *

# 11\. Ví dụ thực tế

Django
    
    
    runserver()
    
    ↓
    
    Middleware
    
    ↓
    
    View
    
    ↓
    
    Response

Bạn chỉ viết:
    
    
    View

* * *

unittest
    
    
    run()
    
    ↓
    
    setUp()
    
    ↓
    
    test_xxx()
    
    ↓
    
    tearDown()

Bạn chỉ viết:
    
    
    setUp()
    
    test_xxx()

* * *

asyncio
    
    
    Loop
    
    ↓
    
    Task
    
    ↓
    
    Coroutine

Bạn không điều khiển vòng lặp ở mức thấp.

* * *

# 12\. Nâng cấp BaseCrawler

Một thiết kế thực tế hơn:
    
    
    class BaseCrawler(ABC):
    
        def crawl(self, keyword):
    
            self.before()
    
            try:
    
                url = self.search(keyword)
    
                detail = self.get_detail(url)
    
                chapters = self.get_chapters(detail)
    
                self.save(chapters)
    
            finally:
    
                self.after()
    
        def before(self):
            pass
    
        def after(self):
            pass

Điểm hay:

Nếu xảy ra lỗi ở:
    
    
    search()
    
    detail()
    
    chapters()

thì:
    
    
    after()

vẫn được gọi để dọn dẹp tài nguyên.

* * *

# 13\. Một thiết kế gần với dự án của bạn
    
    
    BaseSource
    │
    ├── crawl()
    ├── before()
    ├── after()
    ├── download_cover()
    ├── save_story()
    ├── save_chapters()
    │
    ├── search()              (abstract)
    ├── get_detail()          (abstract)
    ├── get_chapters()        (abstract)
    └── download_chapter()    (abstract)

Plugin:
    
    
    TruyenFullSource
    
    TangThuVienSource
    
    WattpadSource
    
    WebNovelSource

Mỗi plugin chỉ tập trung vào việc lấy dữ liệu từ website tương ứng, còn quy trình xử lý, lưu trữ và ghi log được lớp cơ sở quản lý.

* * *

# 14\. Sai lầm phổ biến

Nhiều người viết:
    
    
    class TruyenFull:
    
        def crawl(self):
            ...
    
    
    class Wattpad:
    
        def crawl(self):
            ...
    
    
    class WebNovel:
    
        def crawl(self):
            ...

Kết quả:

  * Logic bị lặp lại. 
  * Khó sửa lỗi. 
  * Khó bổ sung logging, retry, cache, metrics. 



Template Method giúp gom phần chung vào một nơi.

* * *

# 15\. Khi nào dùng Template Method?

Nên dùng khi:

  * Có nhiều lớp có cùng quy trình xử lý. 
  * Chỉ khác một vài bước. 
  * Muốn framework kiểm soát luồng thực thi. 
  * Muốn giảm lặp mã. 



Không nên dùng khi:

  * Các quy trình khác nhau hoàn toàn. 
  * Không có luồng xử lý chung để tái sử dụng. 



* * *

# Tổng kết

Trong buổi này, bạn đã học:

  * Abstract Method 
  * Concrete Method 
  * Hook Method 
  * Template Method Pattern 
  * Inversion of Control 
  * Hollywood Principle 
  * Cách thiết kế BaseCrawler theo phong cách framework 



Đây là nền tảng để xây dựng các framework Python chuyên nghiệp.

* * *

# Bài tập

## Bài 1

Viết:
    
    
    class FileProcessor(ABC)

Template:
    
    
    open()
    
    ↓
    
    read()
    
    ↓
    
    process()
    
    ↓
    
    save()
    
    ↓
    
    close()

Trong đó:

  * `process()` là abstract method. 
  * `open()`, `save()`, `close()` là concrete method. 



* * *

## Bài 2

Viết:
    
    
    class PaymentGateway(ABC)

Template:
    
    
    before_payment()
    
    ↓
    
    validate()
    
    ↓
    
    pay()
    
    ↓
    
    log()
    
    ↓
    
    after_payment()

`pay()` là abstract method.

* * *

## Bài 3

Nâng cấp `BaseCrawler` của dự án truyện:

Thêm các hook:

  * `before_search()`
  * `after_search()`
  * `before_download()`
  * `after_download()`



Để plugin có thể tùy chọn ghi log, đăng nhập hoặc thiết lập proxy mà không phải ghi đè toàn bộ `crawl()`.

* * *

# Buổi 7 (rất quan trọng)

Ở **Buổi 7** , chúng ta sẽ đi sâu vào **Abstract Property** :

  * `@property + @abstractmethod`
  * Getter 
  * Setter 
  * Readonly Property 
  * Cached Property 
  * Validation 
  * Abstract Property trong các framework lớn 



Đây là phần thường bị bỏ qua nhưng lại rất hữu ích khi thiết kế API sạch và dễ sử dụng.

