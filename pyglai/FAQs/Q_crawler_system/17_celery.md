Version:0.9 StartHTML:00000097 EndHTML:00120185 StartFragment:00000131 EndFragment:00120149 

**Celery** là một thư viện Python mã nguồn mở rất mạnh mẽ dùng để quản lý **Hàng đợi tác vụ (Task Queue)**. Nó giúp bạn thực thi các tác vụ nặng hoặc tốn thời gian ở chế độ chạy ngầm (asynchronous/background) trên một hoặc nhiều máy chủ độc lập, tách biệt hoàn toàn khỏi tiến trình chính của ứng dụng Web.

* * *

Mô hình hoạt động của Celery

Hệ thống sử dụng Celery luôn gồm 3 thành phần cốt lõi bắt buộc:
    
    
    [Ứng dụng Web / FastAPI]  ──(Gửi tác vụ)──>  [Message Broker (Redis/RabbitMQ)]
                                                          │
                                               (Phân phối tác vụ ngầm)
                                                          ▼
    [Kết quả trả về Client]  <──(Lưu trữ)───────  [Celery Workers]
    

  1. **Producer (Web App):** Nơi nhận yêu cầu từ người dùng (ví dụ: bấm nút "Xuất báo cáo PDF"). Thay vì tự xử lý, Web App chỉ gửi một tin nhắn lệnh vào hàng đợi rồi phản hồi ngay lập tức cho người dùng: _"Đang xử lý, vui lòng chờ"_.
  2. **Message Broker (Trạm trung chuyển):** Thường là **Redis** hoặc **RabbitMQ**. Nơi này nhận tin nhắn lệnh từ Web App, xếp hàng theo thứ tự và giữ chúng an toàn.
  3. **Celery Worker (Tiến trình chạy ngầm):** Một hoặc nhiều tiến trình độc lập liên tục túc trực tại Broker. Hễ có tác vụ mới trong hàng đợi, Worker sẽ bốc về xử lý (ví dụ: cào dữ liệu, tạo file PDF). Sau khi xong, nó có thể lưu kết quả vào **Result Backend** (Redis, Postgres, v.v.).



* * *

Các kịch bản sử dụng Celery kinh điển

  * **Xử lý tác vụ mất nhiều thời gian:** Gửi email hàng loạt, xử lý/render video, resize ảnh dung lượng lớn, xuất file Excel/PDF từ hàng triệu bản ghi.
  * **Đồng bộ dữ liệu và Cào web (Web Scraping):** Tự động quét dữ liệu từ các API bên thứ ba hoặc các website khác theo chu kỳ mà không làm treo giao diện người dùng.
  * **Tác vụ định kỳ (Cron Jobs):** Celery hỗ trợ một thành phần gọi là **Celery Beat**. Bạn có thể cấu hình để chạy một tác vụ cụ thể vào đúng 12 giờ đêm mỗi ngày (ví dụ: tính tổng doanh thu ngày, dọn dẹp bộ nhớ đệm).



* * *

Hướng dẫn nhanh: Code ví dụ Celery + Redis

1\. Cài đặt thư viện

Bạn cần cài đặt Celery và thư viện hỗ trợ kết nối với Redis:

bash
    
    
    pip install celery redis
    

Hãy thận trọng khi sử dụng mã.

_(Lưu ý: Bạn cần cài đặt và khởi động sẵn phần mềm Redis Server trên máy hoặc dùng Docker)._

2\. Định nghĩa tác vụ trong file `tasks.py`

python
    
    
    from celery import Celery
    import time
    
    # Khởi tạo Celery, sử dụng Redis làm Broker và nơi lưu kết quả (Backend)
    app = Celery('my_tasks', 
                 broker='redis://localhost:6379/0',
                 backend='redis://localhost:6379/0')
    
    @app.task
    def send_welcome_email(user_email):
        print(f"[Worker] Bắt đầu gửi email tới {user_email}...")
        time.sleep(5)  # Giả lập việc gửi email mất 5 giây
        print(f"[Worker] Đã gửi email thành công tới {user_email}!")
        return f"Email sent to {user_email}"
    

Hãy thận trọng khi sử dụng mã.

3\. Gọi tác vụ từ ứng dụng Web của bạn (ví dụ: `main.py`)

python
    
    
    from tasks import send_welcome_email
    
    def register_user_endpoint():
        # Giả lập người dùng đăng ký tài khoản thành công
        user_email = "khachhang@example.com"
        
        # KHÔNG gọi trực tiếp kiểu send_welcome_email(user_email) vì sẽ bị nghẽn 5 giây.
        # Sử dụng .delay() để đẩy tác vụ này vào hàng đợi Celery chạy ngầm.
        send_welcome_email.delay(user_email)
        
        # Trả về kết quả cho client ngay lập tức trong 0.001 giây
        return {"status": "Đăng ký thành công! Vui lòng kiểm tra email của bạn."}
    
    if __name__ == "__main__":
        print(register_user_endpoint())
    

Hãy thận trọng khi sử dụng mã.

4\. Cách kích hoạt Celery Worker chạy thực tế

Mở một Terminal mới (tách biệt với file chạy Web) và gõ lệnh sau để bật Worker:

bash
    
    
    celery -A tasks worker --loglevel=info
    

Hãy thận trọng khi sử dụng mã.

Khi bạn chạy file `main.py`, bạn sẽ thấy Terminal của Web trả về kết quả ngay lập tức, trong khi Terminal của Celery Worker sẽ hiện log đang xử lý ngầm tác vụ gửi email trong 5 giây.

* * *

Để tôi hỗ trợ bạn thiết lập Celery chuẩn xác nhất cho hạ tầng của bạn, hãy phản hồi:

  * Bạn định chọn phần mềm nào làm Message Broker (**Redis** hay **RabbitMQ**)?
  * Bạn có cần cấu hình chạy tác vụ lặp đi lặp lại theo giờ cố định (**Celery Beat**) không?

