Trong DDD (Domain-Driven Design) và SOLID, việc sử dụng logging không đơn thuần là gọi hàm ghi log, mà phải tuân thủ nghiêm ngặt tính độc lập của Domain và các nguyên tắc thiết kế hướng đối tượng.

Dưới đây là cách áp dụng Logging chuẩn chỉnh vào DDD và SOLID:

* * *

## 1\. Nguyên tắc cốt lõi: Domain không được phụ thuộc trực tiếp vào thư viện Logging

Trong DDD, tầng Domain (chứa các Entity, Aggregate Root, Value Object) là trái tim của ứng dụng. Nó phải thuần khiết (Pure) và không được phép phụ thuộc vào bất kỳ thư viện bên thứ ba nào (như `logging` của Python hay `colorlog`).

Nếu bạn import trực tiếp `logging` vào Domain, bạn đã vi phạm:

  * DDD Principle: Làm bẩn tầng Domain bằng các chi tiết hạ tầng (Infrastructure).
  * DIP (Dependency Inversion Principle - chữ D trong SOLID): Tầng logic cao cấp (Domain) lại đi phụ thuộc trực tiếp vào module cấp thấp (Logging framework).



* * *

## 2\. Giải pháp thực tế trong DDD và SOLID

Có 2 cách phổ biến và chuẩn hóa nhất để giải quyết bài toán này:

## Cách 1: Sử dụng Dependency Inversion (DIP) qua Interface (Khuyên dùng)

Chúng ta định nghĩa một `Interface` (hoặc lớp trừu tượng) ở tầng Domain/Application, sau đó cài đặt (implement) nó ở tầng Infrastructure.

## 1\. Định nghĩa Interface ở tầng Domain hoặc Application
    
    
    # domain/interfaces/logger_interface.py
    from abc import ABC, abstractmethod
    
    class IAppLogger(ABC):
        @abstractmethod
        def info(self, message: str, **kwargs) -> None:
            pass
    
        @abstractmethod
        def error(self, message: str, error: Exception = None, **kwargs) -> None:
            pass
    

## 2\. Cài đặt Interface này ở tầng Infrastructure

Tầng này mới là nơi import thư viện `logging` của Python đã cấu hình ở các bước trước.
    
    
    # infrastructure/logging/app_logger.py
    import logging
    from domain.interfaces.logger_interface import IAppLogger
    
    class PythonAppLogger(IAppLogger):
        def __init__(self, name: str):
            self._logger = logging.getLogger(name)
    
        def info(self, message: str, **kwargs) -> None:
            # Bạn có thể log thêm các thông tin bổ sung (context) nếu muốn
            self._logger.info(message, extra=kwargs)
    
        def error(self, message: str, error: Exception = None, **kwargs) -> None:
            self._logger.error(f"{message} | Error: {str(error)}", exc_info=True, extra=kwargs)
    

## 3\. Sử dụng trong Application Service (Dependency Injection)

Khi sử dụng, bạn tiêm (inject) Interface này vào. Điều này tuân thủ hoàn hảo SRP (Single Responsibility) và DIP.
    
    
    # application/services/order_service.py
    from domain.interfaces.logger_interface import IAppLogger
    
    class OrderApplicationService:
        def __init__(self, logger: IAppLogger):
            self.logger = logger  # Nhận logger từ ngoài truyền vào
    
        def create_order(self, order_data) -> None:
            self.logger.info(f"Bắt đầu tạo đơn hàng cho khách: {order_data['customer_id']}")
            try:
                # Logic tạo đơn hàng...
                pass
            except Exception as e:
                self.logger.error("Thất bại khi tạo đơn hàng", error=e)
                raise
    

* * *

## Cách 2: Sử dụng Domain Events để ghi log (Chuẩn DDD nhất)

Đôi khi, việc log một hành động nghiệp vụ (Ví dụ: _"Đơn hàng #123 đã được thanh toán thành công"_) thực chất là một sự kiện nghiệp vụ quan trọng.

Thay vì gọi logger trong Domain, Domain sẽ bắn ra một Domain Event. Tầng Infrastructure hoặc Application sẽ lắng nghe sự kiện này và ghi log.
    
    
    # domain/models/order.py (Domain Pure - Không hề có một dòng chữ "log" nào)
    class Order:
        def __init__(self, order_id: str):
            self.order_id = order_id
            self.events = []
    
        def cancel(self, reason: str):
            self.status = "CANCELLED"
            # Thay vì log ở đây, ta lưu lại một Event
            self.events.append(OrderCancelledEvent(self.order_id, reason))
    
    # infrastructure/event_handlers/log_order_events.py (Tầng hạ tầng lo việc log)
    def handle_order_cancelled(event: OrderCancelledEvent):
        # Thư viện logging thực tế được gọi ở đây
        logger = logging.getLogger("order_domain")
        logger.warning(f"ĐƠN HÀNG BỊ HỦY: ID {event.order_id}. Lý do: {event.reason}")
    

* * *

## Tóm tắt ma trận áp dụng SOLID vào Logging

Nguyên tắc| Cách áp dụng vào Logging  
---|---  
S - Single Responsibility| Mỗi Class chỉ log những gì thuộc phạm vi trách nhiệm của nó. Không để một Class vừa tính toán tiền, vừa lo định dạng chuỗi để in ra file log.  
O - Open/Closed| Khi bạn muốn đổi từ log ra File sang log lên Hệ thống đám mây (như AWS CloudWatch), bạn chỉ cần viết một Class Handler mới, không được sửa code xử lý nghiệp vụ cũ.  
L - Liskov Substitution| Class `PythonAppLogger` phải thay thế hoàn hảo được cho `IAppLogger` mà không làm hỏng ứng dụng.  
I - Interface Segregation| Nếu hệ thống lớn, chia nhỏ Interface Log. Đừng bắt một Module nhỏ phải nhận một Interface Log quá đồ sộ gồm cả log db, log file, log email nếu nó không cần.  
D - Dependency Inversion| Business Logic chỉ gọi `IAppLogger` (Cấp cao). Thư viện `logging` (Cấp thấp) phục tùng `IAppLogger`.  
  
Nếu bạn đang dùng một Framework cụ thể nào cho dự án DDD này (như FastAPI, Flask, hay Django), bạn có muốn biết cách tự động tiêm (Inject) Logger vào các Service bằng Container không?