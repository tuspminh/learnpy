Version:0.9 StartHTML:00000097 EndHTML:00040694 StartFragment:00000131 EndFragment:00040658 

# Bắt đầu Buổi 1

# Mục tiêu

Sau buổi này bạn sẽ trả lời được:

  * Interface là gì? 
  * Duck Typing là gì? 
  * Vì sao Python không có interface? 
  * ABC giải quyết vấn đề gì? 
  * Khi nào dùng ABC? 



* * *

# 1\. Python là ngôn ngữ Duck Typing

Có câu nói nổi tiếng:

> If it walks like a duck and quacks like a duck, then it is a duck.

Tạm dịch:

> Nếu nó đi như vịt và kêu như vịt thì coi nó là vịt.

Python không quan tâm kiểu dữ liệu, mà quan tâm **đối tượng có hành vi (behavior) phù hợp hay không**.

Ví dụ:
    
    
    class Dog:
        def speak(self):
            print("Woof")
    
    
    class Cat:
        def speak(self):
            print("Meow")
    
    
    def make_sound(animal):
        animal.speak()
    
    
    make_sound(Dog())
    make_sound(Cat())

Kết quả:
    
    
    Woof
    Meow

Hàm `make_sound` không cần biết đối tượng là `Dog` hay `Cat`, chỉ cần có phương thức `speak()`.

Đây chính là **Duck Typing**.

* * *

# 2\. Lợi ích của Duck Typing

Ví dụ:
    
    
    class Human:
        def speak(self):
            print("Hello")
    
    
    class Robot:
        def speak(self):
            print("010101")
    
    
    class Alien:
        def speak(self):
            print("%%##@@")
    
    
    for obj in [Human(), Robot(), Alien()]:
        obj.speak()

Không cần kế thừa từ lớp cha nào, miễn có `speak()` là hoạt động.

Điều này giúp mã nguồn linh hoạt và giảm sự phụ thuộc giữa các lớp.

* * *

# 3\. Vấn đề của Duck Typing

Nếu một lớp không có phương thức mong đợi:
    
    
    class Fish:
        pass
    
    
    make_sound(Fish())

Kết quả:
    
    
    AttributeError:
    'Fish' object has no attribute 'speak'

Lỗi chỉ xuất hiện **khi chạy chương trình (runtime)**.

Trong các dự án lớn, điều này có thể khiến lỗi chỉ bộc lộ ở môi trường production nếu nhánh mã đó ít được kiểm thử.

* * *

# 4\. Interface trong Java/C#

Trong Java:
    
    
    interface Animal{
        void speak();
    }

Mọi lớp triển khai interface đều phải cài đặt:
    
    
    class Dog implements Animal{
        public void speak(){
        }
    }

Nếu quên:
    
    
    class Dog implements Animal{
    
    }

Chương trình sẽ không biên dịch.

* * *

# 5\. Python không có Interface

Python được thiết kế với triết lý:

> "We are all consenting adults here."

Nghĩa là ngôn ngữ tin rằng lập trình viên sẽ tự chịu trách nhiệm về việc triển khai đúng giao diện cần thiết.

Thay vì ép buộc bằng interface như Java, Python ban đầu dựa vào Duck Typing.

* * *

# 6\. Khi dự án lớn lên

Hãy tưởng tượng bạn xây dựng hệ thống crawler truyện với nhiều nguồn:
    
    
    TruyenFull
    TangThuVien
    Wattpad
    WebNovel

Bạn mong muốn mọi nguồn đều có:
    
    
    search()
    
    
    get_detail()
    
    
    get_chapters()
    
    
    download_chapter()

Nếu một lập trình viên quên cài đặt:
    
    
    class TruyenFull:
        def search(self):
            ...
    
        def get_detail(self):
            ...

Nhưng quên:
    
    
    download_chapter()

Hệ thống chỉ phát hiện lỗi khi chạy đến đoạn gọi phương thức đó.

* * *

# 7\. ABC ra đời

`abc` (Abstract Base Classes) được giới thiệu để định nghĩa một **hợp đồng (contract)** giữa lớp cơ sở và các lớp con.

Thay vì chỉ "hy vọng" các lớp con có đủ phương thức, bạn có thể yêu cầu Python kiểm tra điều đó ngay khi tạo đối tượng.

Ví dụ:
    
    
    from abc import ABC, abstractmethod
    
    
    class Animal(ABC):
    
        @abstractmethod
        def speak(self):
            pass

Nếu viết:
    
    
    class Dog(Animal):
        pass

và tạo đối tượng:
    
    
    Dog()

Python sẽ báo lỗi:
    
    
    TypeError:
    Can't instantiate abstract class Dog
    with abstract method speak

Điều này giúp phát hiện thiếu sót sớm hơn và làm cho API của lớp rõ ràng hơn.

* * *

# 8\. Khi nào dùng ABC?

Nên dùng khi:

  * Xây dựng framework. 
  * Thiết kế plugin. 
  * Thiết kế thư viện. 
  * Xây dựng kiến trúc nhiều module. 
  * Muốn các lớp con bắt buộc triển khai một tập phương thức. 



Không nhất thiết phải dùng khi:

  * Viết script nhỏ. 
  * Chương trình đơn giản. 
  * Chỉ có một vài lớp và không cần ràng buộc chung. 



* * *

# 9\. Tổng kết

Sau buổi học này, bạn nên nắm được:

  * Python ưu tiên **Duck Typing** , tập trung vào hành vi thay vì kiểu. 
  * Duck Typing rất linh hoạt nhưng lỗi thường xuất hiện ở runtime. 
  * ABC cung cấp một cơ chế để định nghĩa "hợp đồng" cho các lớp con, giúp phát hiện việc triển khai thiếu sớm hơn. 
  * ABC đặc biệt hữu ích trong các framework, thư viện và hệ thống plugin. 



* * *

# Bài tập

  1. Viết các lớp `Dog`, `Cat`, `Bird` với phương thức `speak()` và một hàm `make_sound()` sử dụng Duck Typing. 
  2. Thêm một lớp `Fish` không có `speak()` và quan sát lỗi khi gọi `make_sound(Fish())`. 
  3. Chuyển ví dụ trên sang dùng `ABC`, tạo lớp `Animal` với `@abstractmethod speak()`. Thử tạo một lớp con chưa cài đặt `speak()` và quan sát lỗi. 
  4. Áp dụng vào dự án crawler của bạn: thiết kế một lớp `CrawlerSource(ABC)` khai báo các phương thức `search()`, `get_detail()`, `get_chapters()` và `download_chapter()`, sau đó thử tạo một plugin chưa triển khai đầy đủ để xem Python phản hồi như thế nào. 



Ở **Buổi 2** , chúng ta sẽ đi sâu vào module `abc`: cách `ABC`, `ABCMeta` và `@abstractmethod` hoạt động bên trong, cùng những trường hợp ít người biết như abstract property, abstract classmethod và abstract staticmethod.

