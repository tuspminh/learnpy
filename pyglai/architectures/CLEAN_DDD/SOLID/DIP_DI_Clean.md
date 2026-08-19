Trong các kiến trúc như Clean Architecture hay Hexagonal Architecture (Ports and Adapters), Dependency Inversion Principle (DIP) và Dependency Injection (DI) là trọng tâm cốt lõi. Mục tiêu lớn nhất là giữ cho Business Logic (Domain/Use Cases) nằm ở trung tâm, hoàn toàn độc lập và không phụ thuộc vào các chi tiết bên ngoài như Cơ sở dữ liệu (Database), Web Framework (FastAPI/Flask), hay bên thứ ba (SMS/Email API).

Dưới đây là cách áp dụng DIP và DI vào mô hình Clean/Hexagonal Architecture trong Python thông qua một bài toán thực tế: _Tạo đơn hàng và gửi email thông báo_.

* * *

## Đồ hình luồng phụ thuộc (Dependency Flow)

Thay vì Domain gọi trực tiếp Database hay Email Service, Domain sẽ định nghĩa ra các Ports (Interfaces). Các dịch vụ bên ngoài (Adapters) sẽ phải triển khai (implement) các Ports đó.
    
    
    [ Infrastructure Layer (Adapters) ] 
           │                │
           ▼ (Triển khai)   ▼ (Triển khai)
    ┌──────────────────────────────────────────────┐
    │ [ Domain Layer (Ports / Business Logic) ]     │
    │   - Port: OrderRepository (Interface)        │
    │   - Port: NotificationService (Interface)    │
    │                                              │
    │   - Use Case: CreateOrderUseCase (Dùng Ports)│
    └──────────────────────────────────────────────┘
    

* * *

## Hướng dẫn triển khai code Python từng bước

## Bước 1: Định nghĩa Domain và Ports (Trung tâm hệ thống)

Tầng này chứa thực thể (Entity) và các lớp trừu tượng (Ports). Nó không import bất kỳ thư viện bên ngoài nào (như SQLAlchemy, Motor, hay requests).
    
    
    # domain/entities.py
    from dataclasses import dataclass
    
    @dataclass
    class Order:
        id: str
        product_name: str
        price: float
    
    # domain/ports.py
    from abc import ABC, abstractmethod
    from domain.entities import Order
    
    class OrderRepository(ABC):
        @abstractmethod
        def save(self, order: Order) -> None:
            pass
    
    class NotificationService(ABC):
        @abstractmethod
        def send_order_confirmation(self, order: Order) -> None:
            pass
    

## Bước 2: Viết Business Logic (Use Case) độc lập

Use Case chỉ tương tác với các Ports. Chúng ta dùng Constructor Injection (DI) để bơm các Adapters thực tế vào khi chạy.
    
    
    # domain/use_cases.py
    from domain.entities import Order
    from domain.ports import OrderRepository, NotificationService
    
    class CreateOrderUseCase:
        # DI: Bơm các Port vào qua __init__. Use Case không biết cụ thể DB hay Email loại gì.
        def __init__(self, order_repo: OrderRepository, notify_service: NotificationService):
            self.order_repo = order_repo
            self.notify_service = notify_service
    
        def execute(self, order_id: str, product_name: str, price: float) -> Order:
            order = Order(id=order_id, product_name=product_name, price=price)
            
            # Thực hiện nghiệp vụ thông qua Port
            self.order_repo.save(order)
            self.notify_service.send_order_confirmation(order)
            
            return order
    

## Bước 3: Triển khai các Adapters (Infrastructure Layer)

Đây là nơi chứa chi tiết kỹ thuật. Các lớp này kế thừa và cài đặt các hàm tương ứng của Ports.
    
    
    # infrastructure/adapters.py
    from domain.entities import Order
    from domain.ports import OrderRepository, NotificationService
    
    class PostgresOrderRepository(OrderRepository):
        def save(self, order: Order) -> None:
            # Giả lập kết nối và lưu vào Postgres SQL
            print(f"[Postgres DB] Đã lưu đơn hàng {order.id} vào SQL Server.")
    
    class SendGridNotificationService(NotificationService):
        def __init__(self, api_key: str):
            self.api_key = api_key
    
        def send_order_confirmation(self, order: Order) -> None:
            # Giả lập gọi API của SendGrid gửi mail
            print(f"[SendGrid Email] Đã gửi mail thông báo cho đơn hàng {order.id}.")
    

## Bước 4: Khởi tạo và Ráp nối (Dependency Injection Container)

Tại điểm chạy ứng dụng (Entrypoint như file `main.py` của FastAPI/Flask), chúng ta tiến hành khởi tạo các lớp và "tiêm" chúng vào nhau.

Bạn có thể dùng thư viện `dependency-injector` để quản lý việc này một cách tự động và sạch sẽ:
    
    
    # container.py
    from dependency_injector import containers, providers
    from infrastructure.adapters import PostgresOrderRepository, SendGridNotificationService
    from domain.use_cases import CreateOrderUseCase
    
    class AppContainer(containers.DeclarativeContainer):
        # 1. Khai báo các Adapters (Phụ thuộc cấp thấp)
        order_repository = providers.Singleton(PostgresOrderRepository)
        
        notification_service = providers.Singleton(
            SendGridNotificationService, 
            api_key="SG.mock_key_12345"
        )
    
        # 2. Khai báo Use Case (Cấp cao) và tự động bơm các Adapters vào
        create_order_use_case = providers.Factory(
            CreateOrderUseCase,
            order_repo=order_repository,
            notify_service=notification_service
        )
    

## Bước 5: Điểm chạy ứng dụng (Entrypoint)

Ví dụ tích hợp luồng xử lý này vào một API endpoint của FastAPI:
    
    
    # main.py
    from fastapi import FastAPI, Depends
    from dependency_injector.wiring import inject, Provide
    from container import AppContainer
    from domain.use_cases import CreateOrderUseCase
    
    app = FastAPI()
    
    # Khởi tạo và wire container
    container = AppContainer()
    container.wire(modules=[__name__])
    
    @app.post("/orders")
    @inject
    def create_order_endpoint(
        order_id: str, 
        product: str, 
        price: float,
        # FastAPI sẽ lấy đối tượng Use Case đã được cấu hình đủ phụ thuộc từ Container
        use_case: CreateOrderUseCase = Depends(Provide[AppContainer.create_order_use_case])
    ):
        order = use_case.execute(order_id, product, price)
        return {"status": "success", "order_id": order.id}
    

* * *

## Điểm mấu chốt giúp kiến trúc này tối ưu

  1. Thay đổi công nghệ trong 5 giây: Nếu ngày mai sếp yêu cầu đổi sang dùng MongoDB và dịch vụ gửi Mail của Amazon (SES), bạn không cần động vào một dòng code nào trong tầng Domain/Use Cases. Bạn chỉ cần viết Adapter mới (`MongoOrderRepository`) và sửa lại đúng 1 dòng khai báo trong file `container.py`.
  2. Kiểm thử biệt lập (Unit Test): Do tầng Domain chỉ phụ thuộc vào `Interface (Ports)`, bạn có thể viết kiểm thử cho Business Logic cực kỳ nhanh mà không cần chạy Docker chứa Postgres hay nạp API Key thật:
         
         def test_create_order_use_case():
             # Tạo Mock cho các Port
             mock_repo = MagicMock(spec=OrderRepository)
             mock_notify = MagicMock(spec=NotificationService)
         
             # Tiêm Mock vào Use Case
             use_case = CreateOrderUseCase(order_repo=mock_repo, notify_service=mock_notify)
             use_case.execute("123", "Laptop", 1500)
         
             # Khẳng định (Assert) logic chạy đúng
             mock_repo.save.assert_called_once()
             mock_notify.send_order_confirmation.assert_called_once()
         




Nếu bạn cần làm rõ thêm, hãy cho tôi biết:

  * Bạn có muốn tối ưu sâu hơn về cấu trúc thư mục (Folder Structure) chuẩn cho một dự án Clean Architecture bằng Python không?
  * Bạn có cần tích hợp phần xử lý Transaction (như Unit of Work Pattern) vào các Port và Use Case này không?