Event-Driven Architecture (EDA - Kiến trúc hướng sự kiện) là một mô hình kiến trúc phần mềm mà trong đó các thành phần của hệ thống sẽ tương tác với nhau bằng cách phát ra (Publish) và tiêu thụ (Consume) các sự kiện (Events). [1, 2, 3, 4, 5] 

Thay vì gọi trực tiếp lẫn nhau theo dạng đồng bộ (gọi API và đợi kết quả), các thành phần trong EDA hoạt động hoàn toàn bất đồng bộ (Asynchronous) và bị động (Decoupled). Chúng không cần biết ai là người tạo ra sự kiện và ai sẽ là người xử lý sự kiện đó. [6, 7, 8, 9, 10] 

Một Sự kiện (Event) là một thông báo về một hành động đã xảy ra trong quá khứ (Ví dụ: `UserRegistered`, `PaymentCaptured`, `OrderShipped`). Vì sự kiện là việc đã xảy ra nên dữ liệu của nó là bất biến (immutable). [11, 12, 13, 14, 15] 

* * *

## 🌟 Cấu trúc tổng quan của Kiến trúc hướng Sự kiện

Kiến trúc EDA thường bao gồm 3 thành phần chính: [16, 17] 
    
    
    +--------------------+       +--------------------+       +--------------------+
    
    |  Event Producers   | ----> |   Event Broker     | ----> |   Event Consumers  |
    |  (Người phát)      |       |  (Bộ trung chuyển) |       |   (Người nhận)     |
    +--------------------+       +--------------------+       +--------------------+
      Ví dụ: Order Service        Kafka / RabbitMQ / AWS SMS   Ví dụ: Inventory Service
                                  (Chứa các Topic/Queue)              Email Service
    

  1. Event Producers (Người phát): Nơi phát sinh ra sự kiện khi trạng thái hệ thống thay đổi (ví dụ: Khách hàng bấm nút đặt hàng). Producer đẩy sự kiện lên Broker rồi tiếp tục làm việc khác ngay lập tức, không đợi phản hồi. [18, 19, 20, 21] 
  2. Event Broker (Bộ định tuyến/Trung chuyển): Trái tim của hệ thống. Nơi tiếp nhận, lưu trữ tạm thời và phân phối các sự kiện đến đúng nơi cần nhận. Các Broker phổ biến bao gồm Apache Kafka, RabbitMQ, AWS SNS/SQS, hoặc Redis Pub/Sub. [22, 23, 24, 25, 26] 
  3. Event Consumers (Người tiêu thụ): Các dịch vụ đăng ký lắng nghe một loại sự kiện cụ thể. Khi có sự kiện mới xuất hiện trên Broker, Consumer sẽ tự động kéo dữ liệu về và xử lý logic của riêng mình. [27, 28, 29, 30, 31] 



* * *

### cau truc thu muc

Kiến trúc Event-Driven Architecture (EDA)

Cấu trúc này tập trung xoay quanh luồng di chuyển của các Sự kiện (Events). Nó có thể nằm trong một Monolith hoặc phân tán trong hệ thống Microservices.

📂 Cấu trúc thư mục chuẩn

text
    
    
    my_event_driven_app/
    │
    ├── broker/                      # Cấu hình kết nối hạ tầng truyền tin
    │   ├── __init__.py
    │   ├── kafka_client.py          # Hoặc rabbitmq_client.py, redis_client.py
    │   └── connection.py
    │
    ├── events/                      # Định nghĩa cấu trúc (Schema) của các sự kiện
    │   ├── __init__.py
    │   ├── base_event.py
    │   ├── order_events.py          # Ví dụ: OrderCreatedEvent, OrderCancelledEvent
    │   └── user_events.py           # Ví dụ: UserRegisteredEvent
    │
    ├── producers/                   # Nơi phát đi các sự kiện
    │   ├── __init__.py
    │   └── checkout_publisher.py    # Phát sự kiện khi khách thanh toán thành công
    │
    ├── handlers/                    # Lớp Consumer xử lý sự kiện khi nó đổ về
    │   ├── __init__.py
    │   ├── email_handler.py         # Nhận event -> Gửi mail chúc mừng
    │   └── inventory_handler.py     # Nhận event -> Giảm số lượng tồn kho
    │
    └── worker.py                    # Tiến trình chạy ngầm liên tục để lắng nghe sự kiện
    

Hãy thận trọng khi sử dụng mã.


* * *

## 🐍 Triển khai Event-Driven Architecture bằng Python

Trong Python, bạn có thể hiện thực hóa EDA theo hai quy mô: Trong cùng một ứng dụng (In-app Event) hoặc Giữa các dịch vụ phân tán (Distributed Event). [32, 33, 34] 

## Cách 1: Sử dụng thư viện `blinker` cho kiến trúc trong cùng 1 ứng dụng (In-App) [35] 

Thư viện `blinker` được sử dụng rất nhiều trong các framework như Flask để phát sự kiện nội bộ giúp tách biệt các hàm xử lý dữ liệu.
    
    
    # app_internal_eda.py
    from blinker import signal
    
    # 1. Định nghĩa một sự kiện (Signal)
    order_created_signal = signal('order-created')
    
    # 2. Định nghĩa các Consumer (Lắng nghe sự kiện)
    @order_created_signal.connect
    def send_confirmation_email(sender, **kwargs):
        order_id = kwargs.get("order_id")
        print(f"[Email Service] Đang gửi email xác nhận cho đơn hàng #{order_id}...")
    
    @order_created_signal.connect
    def update_inventory(sender, **kwargs):
        order_id = kwargs.get("order_id")
        print(f"[Inventory Service] Đang trừ kho cho sản phẩm trong đơn hàng #{order_id}...")
    
    # 3. Kích hoạt sự kiện từ Producer
    print("[Order Service] Người dùng thanh toán thành công!")
    # Phát sự kiện đi, kèm theo dữ liệu phụ tải (payload)
    order_created_signal.send("OrderService", order_id=4567)
    

## Cách 2: Sử dụng `Redis Pub/Sub` cho hệ thống phân tán (Distributed) [36] 

Khi ứng dụng của bạn phình to thành các service chạy độc lập, ta cần một Broker như Redis để truyền tin. [37] 

👉 Mã nguồn Producer (Phát sự kiện):
    
    
    # producer.py
    import redis
    import json
    import time
    
    # Kết nối đến Redis Server
    r = redis.Redis(host='localhost', port=6373, decode_responses=True)
    
    def publish_user_login(user_id: int):
        event_data = {
            "event_type": "UserLoggedIn",
            "user_id": user_id,
            "timestamp": time.time()
        }
        # Phát sự kiện vào kênh (channel) đặt tên là 'user_events'
        r.publish('user_events', json.dumps(event_data))
        print(f"[Auth Service] Đã phát sự kiện UserLoggedIn cho ID: {user_id}")
    
    if __name__ == "__main__":
        publish_user_login(user_id=102)
    

👉 Mã nguồn Consumer (Nhận và xử lý sự kiện):
    
    
    # consumer.py
    import redis
    import json
    
    r = redis.Redis(host='localhost', port=6373, decode_responses=True)
    
    # Khởi tạo đối tượng PubSub của Redis
    pubsub = r.pubsub()
    # Đăng ký lắng nghe kênh 'user_events'
    pubsub.subscribe('user_events')
    
    print("[Analytics Service] Đang lắng nghe sự kiện trên kênh 'user_events'...")
    
    for message in pubsub.listen():
        # Bỏ qua tin nhắn đăng ký thành công ban đầu của Redis
        if message['type'] == 'message':
            event = json.loads(message['data'])
            
            if event['event_type'] == "UserLoggedIn":
                # Xử lý logic cập nhật thống kê, lịch sử đăng nhập
                print(f"[Analytics Service] Ghi nhận: User #{event['user_id']} vừa đăng nhập lúc {event['timestamp']}.")
    

* * *

## 📊 Ưu điểm và Nhược điểm của EDA

Ưu điểm 🟢| Nhược điểm 🔴  
---|---  
Loose Coupling (Ràng buộc lỏng): Các dịch vụ hoàn toàn mù tịt về sự tồn tại của nhau. Thêm một tính năng mới (ví dụ: Đơn hàng thành công thì cộng điểm thưởng) chỉ cần viết thêm một Consumer mới lắng nghe mà không cần sửa code cũ.| Khó Debug và Trace log: Vì luồng xử lý chạy bất đồng bộ, bạn không thể dùng `try/except` bao quát từ đầu đến cuối luồng. Phải dùng các hệ thống log tập trung để theo vết sự kiện qua ID (Correlation ID).  
Tính sẵn sàng cao (High Availability): Nếu Consumer (ví dụ: hệ thống gửi SMS) bị sập, các sự kiện vẫn nằm an toàn trên Broker. Khi hệ thống SMS bật trở lại, nó tự động xử lý tiếp các sự kiện tồn đọng, hệ thống không bị mất dữ liệu.| Rủi ro trùng lặp sự kiện: Hệ thống mạng có thể khiến Broker gửi một sự kiện 2 lần. Code xử lý của Consumer bắt buộc phải thiết kế theo cơ chế Idempotent (Xử lý nhiều lần cùng 1 sự kiện nhưng chỉ cho ra một kết quả duy nhất).  
Phản hồi siêu nhanh (Responsiveness): Người dùng không cần xoay vòng vòng chờ hệ thống gửi Email, SMS xong mới thấy trang "Đặt hàng thành công".| Hệ thống nhất quán muộn (Eventual Consistency): Dữ liệu không được cập nhật ngay lập tức ở tất cả mọi nơi mà cần một khoảng trễ nhỏ để sự kiện truyền đi.  
  
* * *

## 💡 Các mô hình truyền tin sự kiện phổ biến

  * Pub/Sub (Publish/Subscribe): Phổ biến nhất. Một sự kiện phát ra có thể được tiêu thụ bởi nhiều Consumer khác nhau cùng một lúc (giống như đài phát thanh truyền hình). [38, 39, 40, 41, 42] 
  * Event Streaming: Các sự kiện được ghi liên tục vào một luồng (Stream) theo dòng thời gian và được lưu trữ vĩnh viễn (như Apache Kafka). Consumer có thể đọc lại các sự kiện từ quá khứ bất cứ lúc nào (Event Sourcing). [43, 44, 45, 46, 47] 



## 📌 Khi nào nên chọn Event-Driven Architecture?

  * Nên dùng: Hệ thống có nhiều tác vụ chạy ngầm mất thời gian (gửi mail, xử lý ảnh/video, báo cáo thống kê, tích hợp API bên thứ 3), hoặc hệ thống Chat, IoT thời gian thực xử lý hàng triệu data-point. [48, 49, 50, 51, 52] 
  * Không nên dùng: Các luồng xử lý nghiệp vụ yêu cầu tính tuần tự nghiêm ngặt, bắt buộc phải biết kết quả ngay lập tức (Ví dụ: Kiểm tra mật khẩu có đúng hay không để cho phép đăng nhập). [53] 



Để quản lý tốt các hệ thống xử lý bất đồng bộ quy mô lớn trong Python, công cụ hàng đầu thường được áp dụng là Celery phối hợp với RabbitMQ. Bạn có muốn xem cách cấu hình một hệ thống Task Queue hoàn chỉnh bằng Celery không? [54] 

  


[1] [https://medium.com](https://medium.com/@msrijita189/event-driven-architecture-what-why-and-how-1033b97b24df)

[2] [https://medium.com](https://medium.com/microservicegeeks/introduction-to-event-driven-architecture-e94ef442d824)

[3] [https://mytechblogs.medium.com](https://mytechblogs.medium.com/distributed-software-architecture-styles-567fb61ce6df)

[4] [https://www.geeksforgeeks.org](https://www.geeksforgeeks.org/system-design/event-driven-apis-in-microservice-architectures/)

[5] [https://aws.plainenglish.io](https://aws.plainenglish.io/event-driven-architecture-explained-with-real-world-examples-4f9cc5c67661)

[6] [https://medium.com](https://medium.com/microservicegeeks/introduction-to-event-driven-architecture-e94ef442d824)

[7] [https://www.linkedin.com](https://www.linkedin.com/pulse/power-event-driven-architecture-comprehensive-guide-nayeem-islam-jtp8c)

[8] [https://querio.ai](https://querio.ai/blog/request-driven-vs-event-driven-architecture)

[9] [https://buildsimple.substack.com](https://buildsimple.substack.com/p/event-driven-architecture-the-power)

[10] [https://modernanalyst.com](https://modernanalyst.com/Careers/InterviewQuestions/tabid/128/ID/6306/What-is-Event-driven-architecture-EDA.aspx)

[11] [https://medium.com](https://medium.com/h7w/understanding-concepts-in-event-driven-architectures-eda-5adbe097f180)

[12] [https://we-archers.com](https://we-archers.com/integration-insights/eda-what-does-it-mean/)

[13] [https://distantjob.com](https://distantjob.com/blog/software-architecture-patterns/)

[14] [https://www.cognixia.com](https://www.cognixia.com/blog/what-is-event-driven-process-orchestration/)

[15] [https://medium.com](https://medium.com/@shailendrasinghpatil/event-driven-architecture-vs-06fc0b5e1f94)

[16] [https://stackoverflow.blog](https://stackoverflow.blog/2020/03/16/how-event-driven-architecture-solves-modern-web-app-problems/)

[17] [https://yokwejuste.medium.com](https://yokwejuste.medium.com/do-you-know-about-event-driven-architecture-247646180177)

[18] [https://wslisam.medium.com](https://wslisam.medium.com/event-driven-architecture-enhancing-system-responsiveness-with-modern-design-af7909c60ac9)

[19] [https://medium.com](https://medium.com/@dulanjayasandaruwan1998/day-4-event-driven-architecture-39f7129dab93)

[20] [https://flowfuse.com](https://flowfuse.com/blog/2026/02/what-is-event-driven-architecture-in-manufacturing/)

[21] [https://designgurus.substack.com](https://designgurus.substack.com/p/system-design-basics-event-driven)

[22] [https://medium.com](https://medium.com/@dulanjayasandaruwan1998/day-4-event-driven-architecture-39f7129dab93)

[23] [https://www.researchgate.net](https://www.researchgate.net/figure/Event-Driven-Architecture_fig1_220880680)

[24] [https://solace.com](https://solace.com/blog/digital-transformation-supply-chain-management-eda/)

[25] [https://atlan.com](https://atlan.com/know/event-driven-architecture-for-data-pipelines/)

[26] [https://blog.stackademic.com](https://blog.stackademic.com/event-sourcing-vs-event-driven-architecture-9a3e04c68f87)

[27] [https://encore.dev](https://encore.dev/articles/event-driven-architecture)

[28] [https://www.linkedin.com](https://www.linkedin.com/pulse/event-driven-integration-paradigm-shift-modern-software-%C3%A7elebi-inzdc)

[29] [https://medium.com](https://medium.com/@dulanjayasandaruwan1998/day-4-event-driven-architecture-39f7129dab93)

[30] [https://www.tothenew.com](https://www.tothenew.com/blog/design-implement-a-event-driven-architecture-in-python/)

[31] [https://www.infoq.com](https://www.infoq.com/articles/realtime-event-driven-ecosystem/)

[32] [https://www.tothenew.com](https://www.tothenew.com/blog/design-implement-a-event-driven-architecture-in-python/)

[33] [https://medium.com](https://medium.com/tamara-tech-product/modern-software-architecture-event-driven-design-meets-event-sourcing-5f7a480d75e3)

[34] [https://www.c-sharpcorner.com](https://www.c-sharpcorner.com/article/introduction-to-event-driven-architecture-eda5/)

[35] [https://solace.com](https://solace.com/what-is-event-driven-architecture/)

[36] [https://softwareengineering.stackexchange.com](https://softwareengineering.stackexchange.com/questions/456283/using-event-driven-architecture-in-a-synchronous-time-constrained-environment)

[37] [https://dev.to](https://dev.to/cadienvan/understanding-the-broker-pattern-in-event-driven-architecture-18b1)

[38] [https://medium.com](https://medium.com/@bhargavkoya56/mastering-event-driven-architecture-for-bulletproof-modern-applications-part-1-53e796a1a1b2)

[39] [https://nordicapis.com](https://nordicapis.com/whats-the-difference-between-rest-and-event-driven-architecture/)

[40] [https://blog.devgenius.io](https://blog.devgenius.io/accelerate-communication-between-microservices-using-node-js-and-redis-pub-sub-9097b4efd995)

[41] [https://medium.com](https://medium.com/@clearwateranalyticsengineering/architecture-patterns-for-modern-applications-978e252d3d25)

[42] [https://ieeexplore.ieee.org](https://ieeexplore.ieee.org/iel5/5283544/5283545/05284211.pdf)

[43] [https://www.akamai.com](https://www.akamai.com/glossary/what-is-event-driven-architecture)

[44] [https://serverlessland.com](https://serverlessland.com/event-driven-architecture/what-are-event-driven-architectures)

[45] [https://medium.com](https://medium.com/@bubu.tripathy/event-driven-architecture-adb658a1dc9c)

[46] [https://ibm-cloud-architecture.github.io](https://ibm-cloud-architecture.github.io/refarch-eda/concepts/terms-and-definitions/)

[47] [https://medium.com](https://medium.com/@carlosmarcano2704/messaging-made-easy-a-list-of-message-brokers-and-event-streaming-platforms-183428ddc336)

[48] [https://medium.com](https://medium.com/@rrakshith007/event-driven-architecture-6ed2f02f2690)

[49] [https://www.adservio.fr](https://www.adservio.fr/post/event-driven-architecture)

[50] [https://dsincl12.medium.com](https://dsincl12.medium.com/clearing-up-misconceptions-the-role-of-events-in-event-driven-architecture-eda-e68ec692c9f0)

[51] [https://learn.microsoft.com](https://learn.microsoft.com/en-us/azure/iot/iot-glossary)

[52] [https://www.linkedin.com](https://www.linkedin.com/pulse/event-driven-architecture-agent-communication-kafka-rabbitmq-mqu9c)

[53] [https://medium.com](https://medium.com/@souzaluis/introduction-to-event-driven-architecture-f726c56b537f)

[54] [https://www.tothenew.com](https://www.tothenew.com/blog/design-implement-a-event-driven-architecture-in-python/)