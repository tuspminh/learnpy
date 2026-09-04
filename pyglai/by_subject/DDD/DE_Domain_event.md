Domain Event là một pattern cốt lõi trong Domain-Driven Design (DDD), đại diện cho "một sự kiện quan trọng đã xảy ra trong Domain nghiệp vụ". Về mặt kỹ thuật, Domain Event giúp giảm sự liên kết (decoupling) giữa các thành phần bên trong hệ thống bằng cách áp dụng mô hình Publish-Subscribe. [1, 2, 3] 

Dưới đây là hướng dẫn chi tiết cách triển khai Domain Event bằng ngôn ngữ Python theo phong cách Clean Architecture / DDD. [4] 

* * *

## 1\. Cấu trúc một Domain Event

Domain Event là một Immutable Object (đối tượng không thể thay đổi sau khi tạo). Trong Python, cách tốt nhất là sử dụng `dataclasses` với thuộc tính `frozen=True`.
    
    
    from dataclasses import dataclass
    from datetime import datetime
    import uuid
    
    @dataclass(frozen=True)
    class DomainEvent:
        event_id: uuid.UUID = uuid.uuid4()
        occurred_on: datetime = datetime.utcnow()
    
    @dataclass(frozen=True)
    class OrderPlaced(DomainEvent):
        order_id: str
        customer_id: str
        total_amount: float
    

## 2\. Tích hợp Event vào Aggregate Root

Thay vì kích hoạt (trigger) event ngay lập tức, cách tiếp cận chuẩn của DDD là để Aggregate Root (ví dụ: `Order`) thu thập các event vào một danh sách nội bộ. Sau khi transaction kết thúc (Unit of Work thành công), chúng ta mới phát tán (dispatch) các event này đi. [1, 4] 
    
    
    from typing import List
    
    class AggregateRoot:
        def __init__(self):
            self._domain_events: List[DomainEvent] = []
    
        def record_event(self, event: DomainEvent):
            self._domain_events.append(event)
    
        @property
        def domain_events(self) -> List[DomainEvent]:
            return self._domain_events
    
        def clear_events(self):
            self._domain_events.clear()
    
    class Order(AggregateRoot):
        def __init__(self, order_id: str, customer_id: str):
            super().__init__()
            self.order_id = order_id
            self.customer_id = customer_id
            self.status = "PENDING"
    
        def place(self, total_amount: float):
            self.status = "PLACED"
            # Ghi nhận sự kiện quan trọng xảy ra trong nghiệp vụ
            self.record_event(
                OrderPlaced(order_id=self.order_id, customer_id=self.customer_id, total_amount=total_amount)
            )
    

## 3\. Bộ điều phối sự kiện (Event Dispatcher)

`EventDispatcher` (hoặc `EventBus`) chịu trách nhiệm đăng ký các `Handler` (bộ xử lý) tương ứng với từng loại Event và kích hoạt chúng khi có Event xuất hiện. [2] 
    
    
    from typing import Callable, Dict, Type
    
    class EventDispatcher:
        def __init__(self):
            self._handlers: Dict[Type[DomainEvent], List[Callable]] = {}
    
        def register(self, event_type: Type[DomainEvent], handler: Callable):
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)
    
        def dispatch(self, event: DomainEvent):
            event_type = type(event)
            if event_type in self._handlers:
                for handler in self._handlers[event_type]:
                    handler(event)
    

## 4\. Tạo các Event Handlers

Handler chứa logic chạy sau khi event xảy ra, ví dụ như gửi Email, thông báo cho hệ thống khác, hoặc cập nhật Read Model (CQRS). [4] 
    
    
    def send_welcome_email_handler(event: OrderPlaced):
        print(f"[Email Service] Đang gửi mail xác nhận cho đơn hàng {event.order_id}...")
    
    def update_inventory_handler(event: OrderPlaced):
        print(f"[Inventory Service] Đang trừ kho cho đơn hàng trị giá {event.total_amount}...")
    

## 5\. Kết nối toàn bộ quy trình (Workflow)

Dưới đây là cách mã nguồn vận hành tại tầng Application Service / Use Case:
    
    
    # 1. Khởi tạo hạ tầng Event
    dispatcher = EventDispatcher()
    dispatcher.register(OrderPlaced, send_welcome_email_handler)
    dispatcher.register(OrderPlaced, update_inventory_handler)
    
    # 2. Thực thi Nghiệp vụ (Domain Layer)
    order = Order(order_id="ORD-123", customer_id="CUST-99")
    order.place(total_amount=250.0)  # Tạo ra event nội bộ
    
    # 3. Lưu trữ & Phát tán Event (Application Layer)
    # Giả sử: order_repository.save(order) đã thành công...
    
    for event in order.domain_events:
        dispatcher.dispatch(event)
    
    # Xóa các event sau khi đã xử lý xong để tránh trùng lặp
    order.clear_events()
    

* * *

## 💡 Lưu ý nâng cao khi dùng Domain Event với Python

  *   * Xử lý Bất đồng bộ (Async): Ví dụ trên xử lý đồng bộ (Synchronous). Đối với các hệ thống lớn, bạn nên tích hợp thư viện `asyncio` hoặc sử dụng các Message Broker bên thứ ba như [Celery](https://docs.celeryq.dev/), [RabbitMQ](https://www.rabbitmq.com/), hoặc [Kafka](https://kafka.apache.org/) để Dispatcher đẩy event vào hàng đợi (Queue) thay vì xử lý trực tiếp. [3, 4, 5, 6] 
  * Thư viện sẵn có: Nếu không muốn tự viết boilerplate code, bạn có thể tham khảo gói mã nguồn mở [eventsourcing](https://eventsourcing.readthedocs.io/) hoặc [domain-event-pattern](https://github.com/adriamontoto/domain-event-pattern) trên GitHub. [2, 7] 
  * 


Bạn đang muốn áp dụng Domain Event cho use case cụ thể nào (ví dụ: quản lý đơn hàng, ví điện tử...)? Hay bạn muốn tích hợp nó với một framework như FastAPI / Django? Hãy chia sẻ thêm để mình tối ưu code mẫu nhé!

  


[1] [https://viblo.asia](https://viblo.asia/p/domain-events-la-gi-924lJ8j8KPM)

[2] [https://github.com](https://github.com/adriamontoto/domain-event-pattern)

[3] [https://gist.github.com](https://gist.github.com/objarni/320f52d4a9d46ff2f658)

[4] [https://www.reddit.com](https://www.reddit.com/r/Python/comments/qm436h/python_domaindriven_design_ddd_example_project/?tl=vi)

[5] [https://newsletter.grokking.org](https://newsletter.grokking.org/p/143-t-monolith-cho-d-n-event-driven-microservices-286592)

[6] [https://realpython.com](https://translate.google.com/translate?u=https://realpython.com/async-io-python/&hl=vi&sl=en&tl=vi&client=sge)

[7] [https://eventsourcing.readthedocs.io](https://eventsourcing.readthedocs.io/en/v9.1.4/topics/domain.html)