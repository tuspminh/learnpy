Trong kiến trúc DDD, Domain Event dùng `sync` (đồng bộ) hay `async` (bất đồng bộ) đều được, việc lựa chọn phụ thuộc hoàn toàn vào tính chất của tác vụ hành động (Handler) đi kèm và ranh giới dữ liệu (Aggregate Boundary).

Thực tế, người ta thường chia cách xử lý Domain Event làm hai loại chính:

## 1\. Khi nào nên dùng `sync` (Đồng bộ)?

Dùng `sync` khi các Handler cần tham gia trực tiếp vào cùng một Transaction (giao dịch) cơ sở dữ liệu với tiến trình chính, hoặc khi logic nghiệp vụ yêu cầu các bước sau phải chạy _ngay lập tức_ và _tuần tự_.

  * Đặc điểm: Nếu một Handler bị lỗi (ném ra Exception), toàn bộ tiến trình chính sẽ bị dừng và Rollback (huỷ bỏ) dữ liệu.
  * Ví dụ app Crawl: Khi cào xong một chương truyện, Event `ChapterParsed` phát đi một `sync` event để chạy Handler chuẩn hoá định dạng văn bản (xoá ký tự rác, sửa lỗi chính tả). Việc này bắt buộc phải xong thì mới lưu được vào Database.



## 2\. Khi nào nên dùng `async` (Bất đồng bộ)?

Dùng `async` khi các Handler thực hiện các tác vụ ngoại vi, tốn thời gian I/O (gửi mạng, ghi file, gọi API bên thứ ba) và không nhất thiết phải thành công thì tiến trình chính mới được coi là hoàn tất (Eventual Consistency - Tính nhất quán sau cùng).

  * Đặc điểm: Tiến trình chính cứ chạy tiếp mà không cần đợi Handler làm xong. Nếu Handler lỗi (ví dụ nghẽn mạng không gửi được tin nhắn Telegram), dữ liệu truyện đã cào vẫn được lưu an toàn trong Database.
  * Ví dụ app Crawl: Gửi thông báo Telegram, đẩy webhook sang app khác, hoặc kích hoạt công cụ đóng gói file EPUB.



* * *

## Bảng So sánh Lựa chọn (Matrix)

Tiêu chí| Sử dụng `sync`| Sử dụng `async`  
---|---|---  
Tác vụ phù hợp| Cập nhật logic nghiệp vụ, tính toán dữ liệu nội bộ.| Gửi thông báo, ghi log tracking, I/O nặng (Đóng gói file, HTTP Request).  
Ranh giới Transaction| Nằm chung một Transaction (Lỗi Handler = Lỗi toàn bộ).| Nằm riêng biệt (Lỗi Handler không ảnh hưởng đến luồng chính).  
Hiệu năng| Chậm hơn (Luồng chính phải đợi Handler kết thúc).| Tối ưu hơn (Tận dụng Non-blocking hoặc Background Worker).  
  
* * *

## Cách thiết kế một Event Bus linh hoạt (Hỗ trợ cả Sync và Async)

Trong Python, bạn có thể thiết kế `DomainEventBus` để người lập trình tự quyết định Handler nào chạy `sync` (dùng hàm thông thường) và Handler nào chạy `async` (dùng `async def`) bằng cách kiểm tra thuộc tính của hàm:
    
    
    import asyncio
    import inspect
    from typing import Callable, List, Dict, Type
    
    class FlexibleEventBus:
        _subscribers: Dict[Type, List[Callable]] = {}
    
        @classmethod
        def subscribe(cls, event_type: Type, handler: Callable):
            if event_type not in cls._subscribers:
                cls._subscribers[event_type] = []
            cls._subscribers[event_type].append(handler)
    
        @classmethod
        async def publish(cls, event: object):
            event_type = type(event)
            if event_type not in cls._subscribers:
                return
    
            for handler in cls._subscribers[event_type]:
                try:
                    # Nếu handler là hàm async (coroutine function)
                    if inspect.iscoroutinefunction(handler):
                        await handler(event) # Chạy và đợi kết quả async
                    else:
                        handler(event) # Chạy đồng bộ (sync) trực tiếp
                except Exception as e:
                    print(f"[EventBus Error] Lỗi tại handler {handler.__name__}: {e}")
    

Nếu bạn muốn đi tiếp, hãy cho tôi biết:

  * Bạn muốn hoàn thiện phần lưu trữ bằng cách chuyển đổi hoàn toàn Repository sang thư viện aiosqlite (async SQLite)?
  * Hay bạn muốn viết code cụ thể cho `epub_exporter_handler` để đóng gói file EPUB sau khi cào xong?