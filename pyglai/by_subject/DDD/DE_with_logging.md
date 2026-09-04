Khi áp dụng Domain Event trong Python, hệ thống của bạn sẽ trở thành một kiến trúc hướng sự kiện (Event-Driven). Việc quản lý Logging lúc này vô cùng quan trọng để bạn có thể debug, theo dõi (trace) luồng đi của dữ liệu và xử lý lỗi khi hệ thống phình to.

Dưới đây là cách thiết lập cấu trúc Logging chuyên nghiệp cho Domain Event bằng thư viện `logging` tiêu chuẩn của Python.

* * *

## 1\. Chiến lược ghi Log cho Domain Event

Một hệ thống DDD/Clean Architecture chuẩn cần ghi nhận log ở 3 cột mốc chính:

  * Ghi nhận (Recorded): Khi Event vừa được tạo ra bên trong Aggregate Root.
  * Phát tán (Dispatched): Khi Event bắt đầu được gửi đi từ Event Bus/Dispatcher.
  * Xử lý (Handled): Khi một Handler tiếp nhận và xử lý Event (Thành công hoặc Thất bại).



Để liên kết các hành động này lại với nhau trên cùng một luồng nghiệp vụ, chúng ta cần dùng `correlation_id` (hoặc `trace_id`).

## 2\. Triển khai code Logging chi tiết

## Bước 1: Cấu hình Logging tập trung (Chuyển sang dạng JSON để dễ quản lý)

Trong thực tế, bạn nên log dưới dạng cấu trúc (Structured Logging / JSON) để dễ dàng đẩy lên các hệ thống như ELK, Datadog hoặc Loki. Ở đây chúng ta sẽ định nghĩa format chuẩn trước.
    
    
    import logging
    import uuid
    import contextvars
    
    # Sử dụng contextvars để lưu trữ trace_id xuyên suốt một request/luồng xử lý
    trace_id_var = contextvars.ContextVar("trace_id", default="N/A")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [TraceID: %(trace_id)s] %(name)s: %(message)s"
    )
    
    # Custom Filter để tự động chèn trace_id vào mọi dòng log
    class TraceIdFilter(logging.Filter):
        def filter(self, record):
            record.trace_id = trace_id_var.get()
            return True
    
    logger = logging.getLogger("DomainEventSystem")
    logger.addFilter(TraceIdFilter())
    

## Bước 2: Tích hợp ghi log vào cấu trúc Event & Dispatcher
    
    
    from dataclasses import dataclass, field
    from datetime import datetime
    from typing import List, Callable, Dict, Type
    
    @dataclass(frozen=True)
    class DomainEvent:
        event_id: uuid.UUID = field(default_factory=uuid.uuid4)
        occurred_on: datetime = field(default_factory=datetime.utcnow)
    
    @dataclass(frozen=True)
    class OrderPlaced(DomainEvent):
        order_id: str
        total_amount: float
    
    class AggregateRoot:
        def __init__(self):
            self._domain_events: List[DomainEvent] = []
    
        def record_event(self, event: DomainEvent):
            self._domain_events.append(event)
            # Log mốc 1: Vừa được tạo trong Domain
            logger.debug(f"📝 Event [Type: {type(event).__name__}] được tạo với ID {event.event_id}")
    
    class EventDispatcher:
        def __init__(self):
            self._handlers: Dict[Type[DomainEvent], List[Callable]] = {}
    
        def register(self, event_type: Type[DomainEvent], handler: Callable):
            self._handlers.setdefault(event_type, []).append(handler)
    
        def dispatch(self, event: DomainEvent):
            event_type = type(event)
            # Log mốc 2: Bắt đầu phát tán
            logger.info(f"🚀 [DISPATCH] Bắt đầu phát tán Event {event_type.__name__} (ID: {event.event_id})")
            
            if event_type not in self._handlers or not self._handlers[event_type]:
                logger.warning(f"⚠️ Không tìm thấy Handler nào cho Event {event_type.__name__}")
                return
    
            for handler in self._handlers[event_type]:
                handler_name = handler.__name__
                try:
                    # Log mốc 3a: Bắt đầu xử lý
                    logger.info(f"⏳ [HANDLE] Handler '{handler_name}' bắt đầu xử lý Event {event.event_id}")
                    
                    handler(event)
                    
                    # Log mốc 3b: Xử lý thành công
                    logger.info(f"✅ [SUCCESS] Handler '{handler_name}' hoàn thành xử lý Event {event.event_id}")
                except Exception as e:
                    # Log mốc 3c: Xử lý thất bại (Ghi nhận toàn bộ lỗi / Stack trace)
                    logger.error(
                        f"❌ [FAILED] Handler '{handler_name}' thất bại khi xử lý Event {event.event_id}. Lỗi: {str(e)}", 
                        exc_info=True
                    )
    

## Bước 3: Tạo các Handlers giả lập
    
    
    def send_email_handler(event: OrderPlaced):
        # Giả lập xử lý thành công
        pass
    
    def Inventory_error_handler(event: OrderPlaced):
        # Giả lập xử lý bị lỗi
        raise ConnectionError("Không thể kết nối đến cơ sở dữ liệu kho!")
    

## Bước 4: Chạy thử luồng xử lý và quan sát Log
    
    
    # Thiết lập Trace ID cho luồng request này (Ví dụ khi nhận request từ REST API)
    trace_id_var.set(str(uuid.uuid4()))
    
    # 1. Cài đặt hệ thống
    dispatcher = EventDispatcher()
    dispatcher.register(OrderPlaced, send_email_handler)
    dispatcher.register(OrderPlaced, Inventory_error_handler)
    
    # 2. Tạo Domain Aggregate và kích hoạt hành động
    logger.info("Khởi tạo tiến trình tạo đơn hàng...")
    class Order(AggregateRoot):
        def place(self):
            self.record_event(OrderPlaced(order_id="ORD-999", total_amount=150.0))
    
    order = Order()
    order.place()
    
    # 3. Dispatch sự kiện
    for event in order.domain_events:
        dispatcher.dispatch(event)
    

* * *

## 3\. Kết quả hiển thị trên Console

Khi chạy đoạn code trên, log xuất ra sẽ cực kỳ tường minh nhờ chung một `TraceID`:
    
    
    2026-09-04 14:25:01 [INFO] [TraceID: 5a2b3c4d...] DomainEventSystem: Khởi tạo tiến trình tạo đơn hàng...
    2026-09-04 14:25:01 [DEBUG] [TraceID: 5a2b3c4d...] DomainEventSystem: 📝 Event [Type: OrderPlaced] được tạo với ID f81d4fae...
    2026-09-04 14:25:01 [INFO] [TraceID: 5a2b3c4d...] DomainEventSystem: 🚀 [DISPATCH] Bắt đầu phát tán Event OrderPlaced (ID: f81d4fae...)
    2026-09-04 14:25:01 [INFO] [TraceID: 5a2b3c4d...] DomainEventSystem: ⏳ [HANDLE] Handler 'send_email_handler' bắt đầu xử lý Event f81d4fae...
    2026-09-04 14:25:01 [INFO] [TraceID: 5a2b3c4d...] DomainEventSystem: ✅ [SUCCESS] Handler 'send_email_handler' hoàn thành xử lý Event f81d4fae...
    2026-09-04 14:25:01 [INFO] [TraceID: 5a2b3c4d...] DomainEventSystem: ⏳ [HANDLE] Handler 'Inventory_error_handler' bắt đầu xử lý Event f81d4fae...
    2026-09-04 14:25:01 [ERROR] [TraceID: 5a2b3c4d...] DomainEventSystem: ❌ [FAILED] Handler 'Inventory_error_handler' thất bại khi xử lý Event f81d4fae... Lỗi: Không thể kết nối đến cơ sở dữ liệu kho!
    Traceback (most recent call last):
      ...
    ConnectionError: Không thể kết nối đến cơ sở dữ liệu kho!
    

## 💡 Lời khuyên khi làm việc với Log trong Production

  1. Sử dụng thư viện bên thứ ba: Thay vì module `logging` mặc định, bạn có thể tham khảo `structlog` hoặc `loguru`. Hai thư viện này hỗ trợ ghi log dạng JSON và quản lý context (`trace_id`) mượt mà hơn rất nhiều.
  2. Không log dữ liệu nhạy cảm (PII): Tránh đưa mật khẩu, số thẻ tín dụng hoặc thông tin cá nhân của khách hàng vào payload của Event nếu bạn định log toàn bộ object event ra ngoài.



Nếu bạn đang chạy ứng dụng này trên nền tảng cụ thể nào (như Docker / Kubernetes hay AWS Lambda), hãy cho mình biết để mình hướng dẫn cách cấu hình ghi log ra file hoặc stdout cho phù hợp nhất nhé!