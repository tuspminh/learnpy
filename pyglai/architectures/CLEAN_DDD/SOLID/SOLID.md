SOLID là một bộ 5 nguyên lý thiết kế hướng đối tượng (OOD) được tập hợp bởi Robert C. Martin (Uncle Bob). Đây được coi là "kim chỉ nam" giúp các lập trình viên viết ra những đoạn mã nguồn dễ hiểu, dễ bảo trì, linh hoạt và dễ dàng mở rộng theo thời gian.

Dưới đây là chi tiết về từng nguyên lý trong bộ SOLID kèm theo ví dụ minh họa bằng Python.

* * *

## 1\. S - Single Responsibility Principle (Nguyên lý đơn nhiệm)

> _"Một lớp chỉ nên có một và chỉ một lý do duy nhất để thay đổi."_

Một Class chỉ nên thực hiện đúng một nhiệm vụ chuyên biệt. Nếu một Class vừa xử lý logic nghiệp vụ, vừa kết nối DB, vừa định dạng hiển thị, nó sẽ trở nên quá cồng kềnh và dễ lỗi khi sửa đổi.

  * ❌ Vi phạm: Class `User` vừa chứa thông tin user, vừa có hàm `save_to_db()` và hàm `export_to_xml()`.
  * ✔️ Áp dụng chuẩn: Tách ra thành 3 Class riêng biệt: `User` (chỉ chứa dữ liệu), `UserRepository` (chỉ làm nhiệm vụ lưu trữ), và `UserSerializer` (chỉ làm nhiệm vụ định dạng dữ liệu).



* * *

## 2\. O - Open/Closed Principle (Nguyên lý Đóng/Mở)

> _"Các thực thể phần mềm nên mở rộng cho việc phát triển, nhưng đóng lại với việc sửa đổi."_

Khi bạn muốn thêm tính năng mới, bạn nên viết code mới (kế thừa hoặc mở rộng) thay vì vào sửa đổi (modify) các đoạn code cũ đang chạy ổn định.
    
    
    from abc import ABC, abstractmethod
    
    # ĐÓNG: Interface này không bao giờ thay đổi
    class Shape(ABC):
        @abstractmethod
        def get_area(self) -> float:
            pass
    
    # MỞ RỘNG: Thêm hình mới chỉ cần tạo Class mới, không sửa code cũ
    class Rectangle(Shape):
        def __init__(self, w, h): self.w, self.h = w, h
        def get_area(self): return self.w * self.h
    
    class Circle(Shape):
        def __init__(self, radius): self.radius = radius
        def get_area(self): return 3.14 * self.radius * self.radius
    
    # Hàm tính tổng diện tích này hoàn toàn không phải sửa lại khi có hình mới
    def total_area(shapes: list[Shape]):
        return sum(shape.get_area() for shape in shapes)
    

* * *

## 3\. L - Liskov Substitution Principle (Nguyên lý thay thế Liskov)

> _"Các đối tượng của lớp con phải có thể thay thế các đối tượng của lớp cha mà không làm thay đổi tính đúng đắn của chương trình."_

Nếu lớp B là con của lớp A, thì chương trình phải chạy đúng khi ta thay thế lớp A bằng lớp B mà không sinh ra lỗi hay hành vi bất thường.

  * ❌ Vi phạm kinh điển (Hình vuông - Hình chữ nhật): Class `Square` kế thừa từ `Rectangle`. Khi ta thay đổi chiều rộng của `Square`, chiều cao của nó cũng buộc phải thay đổi theo để giữ tính chất hình vuông. Điều này làm phá vỡ logic toán học của lớp cha `Rectangle` (vốn cho phép chiều rộng và chiều cao thay đổi độc lập).
  * ✔️ Khắc phục: Tạo một lớp cha chung trừu tượng là `Polygon` hoặc `Shape`, không cho `Square` kế thừa trực tiếp từ `Rectangle`.



* * *

## 4\. I - Interface Segregation Principle (Nguyên lý phân tách Interface)

> _"Không nên ép buộc một client phải phụ thuộc vào các interface mà nó không sử dụng."_

Thay vì tạo ra một Interface khổng lồ với quá nhiều hàm (Fat Interface), ta nên chia nhỏ thành nhiều Interface chuyên biệt. Client cần dùng chức năng nào thì chỉ cần triển khai Interface đó, tránh việc phải viết các hàm rỗng để "đối phó".
    
    
    from abc import ABC, abstractmethod
    
    # ❌ TỒI: Tạo một Interface chung bắt buộc mọi loại máy phải làm theo
    # class MultiFunctionDevice(ABC):
    #     @abstractmethod
    #     def print_doc(self): pass
    #     @abstractmethod
    #     def fax_doc(self): pass
    
    # ✔️ CHUẨN: Chia nhỏ Interface
    class Printer(ABC):
        @abstractmethod
        def print_doc(self): pass
    
    class FaxMachine(ABC):
        @abstractmethod
        def fax_doc(self): pass
    
    # Máy in giá rẻ chỉ cần kế thừa Printer, không bị ép phải biết Fax
    class CheapPrinter(Printer):
        def print_doc(self): print("In tài liệu...")
    

* * *

## 5\. D - Dependency Inversion Principle (Nguyên lý đảo ngược phụ thuộc)

> _“1. Các module cấp cao không nên phụ thuộc vào các module cấp thấp. Cả hai nên phụ thuộc vào sự trừu tượng (Abstraction)._  
> _2\. Sự trừu tượng không nên phụ thuộc vào chi tiết, mà chi tiết nên phụ thuộc vào sự trừu tượng.”_

Đây chính là nguyên lý gốc mà bạn đã tìm hiểu ở các phần trước. Thay vì các lớp Business Logic gọi trực tiếp đến lớp Database hay API cụ thể, chúng ta chèn một Interface (Abstraction) ở giữa làm cầu nối độc lập.

* * *

## Tóm tắt tư duy SOLID áp dụng vào dự án

Khi bạn kết hợp SOLID với các kiến trúc như Clean hay Hexagonal Architecture:

  * S giúp các Use Case và Entity của bạn nhỏ gọn, chỉ làm đúng một việc.
  * O và L giúp bạn dễ dàng cắm thêm các Adapter mới (ví dụ gắn thêm phương thức thanh toán mới) vào hệ thống mà không sợ hỏng logic cũ.
  * I và D đảm bảo phần lõi (Core/Domain) của bạn tách biệt hoàn toàn và làm chủ các công nghệ ở tầng ngoài cùng.



Nếu bạn muốn, tôi có thể:

  * Giúp bạn review một đoạn code Python cụ thể xem nó đang vi phạm nguyên lý nào trong bộ SOLID.
  * Hướng dẫn cách kết hợp SOLID khi viết các ứng dụng bất đồng bộ (Asyncio) trong Python.