concurrent.futures là một module chuẩn trong thư viện Python giúp bạn lập trình bất đồng bộ và thực hiện các tác vụ song song một cách dễ dàng nhất.
Nó đóng vai trò như một "lớp bọc cao cấp" (high-level interface) phía trên các thư viện cấp thấp như threading (đa luồng) và multiprocessing (đa tiến trình). Thay vì bạn phải tự quản lý việc tạo, chạy, khóa và tắt từng luồng/tiến trình thủ công, concurrent.futures tự động hóa toàn bộ các công việc phức tạp đó thông qua khái niệm "Pool" (Hồ quản lý tài nguyên).
------------------------------
## 1. Kiến trúc cốt lõi của concurrent.futures
Module này được xây dựng dựa trên 3 thành phần chính:

* Executor (Người thực thi): Là một lớp trừu tượng (abstract class) định nghĩa cấu trúc điều khiển. Bạn sẽ không dùng trực tiếp nó mà dùng 2 lớp con của nó:
* ThreadPoolExecutor: Sử dụng cho tác vụ nghẽn I/O (Mạng, Ổ cứng, API).
   * ProcessPoolExecutor: Sử dụng cho tác vụ nghẽn CPU (Tính toán nặng, thuật toán, xử lý ảnh).
* Future (Đối tượng tương lai): Khi bạn gửi một tác vụ cho Executor, nó không bắt bạn ngồi chờ kết quả ngay lập tức mà trả về một vật đại diện gọi là Future. Đối tượng này giống như một "phiếu hẹn" đại diện cho một kết quả chắc chắn sẽ có trong tương lai. Bạn có thể dùng nó để kiểm tra tác vụ đã chạy xong chưa, hủy tác vụ, hoặc lấy kết quả khi nó hoàn thành.
* Các hàm tiện ích bổ sung:
* as_completed(): Trả về kết quả của các tác vụ theo thứ tự thằng nào xong trước lấy trước.
   * wait(): Dừng chương trình chính để chờ một nhóm tác vụ hoàn thành dựa trên điều kiện (Ví dụ: chờ tất cả xong, hoặc chỉ cần 1 thằng đầu tiên xong).

------------------------------
## 2. Bản đồ tư duy: Lựa chọn công cụ phù hợp
Để sử dụng thành thạo concurrent.futures, bạn chỉ cần ghi nhớ sơ đồ quyết định sau:

                           BẠN MUỐN LÀM GÌ?
                                  |
         +------------------------+------------------------+

         |                                                 |
   Tác vụ nghẽn I/O (Chờ mạng/File)             Tác vụ nghẽn CPU (Tính toán)

         |                                                 |
 [ThreadPoolExecutor]                             [ProcessPoolExecutor]

         |                                                 |
         +------------------------+------------------------+
                                  |
                    Gửi tác vụ vào Pool bằng cách nào?
                                  |
         +------------------------+------------------------+

         |                                                 |
Áp dụng 1 hàm cho 1 danh sách dữ liệu           Chạy nhiều hàm/tham số linh hoạt

         |                                                 |
     [.map()]                                         [.submit()]

         |                                                 |
Kết quả trả về đúng thứ tự ban đầu           Trả về đối tượng [Future] độc lập
                                                           |
                                              Gom danh sách Future và xử lý:
                                              - Thằng nào xong trước lấy trước: [as_completed()]
                                              - Chờ điều kiện cụ thể: [wait()]

------------------------------
## 3. Ví dụ tổng hợp: Sử dụng wait() để kiểm soát nâng cao
Chúng ta đã xem qua map() và as_completed(). Hãy xem cách dùng submit() kết hợp với wait() để tạo ra cơ chế kiểm soát tiến độ rất chuyên nghiệp:

import timefrom concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
def worker(task_id, duration):
    print(f"Luồng {task_id} bắt đầu làm việc trong {duration}s...")
    time.sleep(duration)
    return f"Kết quả {task_id}"
with ThreadPoolExecutor(max_workers=3) as executor:
    # Gửi 3 tác vụ với thời gian chạy khác nhau
    futures = [
        executor.submit(worker, 1, 5), # Lâu nhất
        executor.submit(worker, 2, 2), # Nhanh nhất
        executor.submit(worker, 3, 3)
    ]
    
    # wait() giúp bạn tạm dừng và kiểm tra trạng thái
    # FIRST_COMPLETED: Chỉ cần 1 tác vụ bất kỳ xong là dừng chờ và đi tiếp
    done, not_done = wait(futures, return_when=FIRST_COMPLETED)
    
    print("\n--- ĐÃ CÓ TÁC VỤ HOÀN THÀNH ĐẦU TIÊN ---")
    for f in done:
        print(f"Tác vụ hoàn thành: {f.result()}")
        
    print(f"Số tác vụ vẫn đang tiếp tục chạy ngầm: {len(not_done)}")

------------------------------
## 4. Khi nào KHÔNG NÊN dùng concurrent.futures?
Dù rất mạnh mẽ và tiện lợi, module này vẫn có những giới hạn:

   1. Khi số lượng kết nối I/O quá khổng lồ (Hàng nghìn đến hàng vạn kết nối): ThreadPoolExecutor bị giới hạn bởi số lượng Thread của hệ điều hành (thường dưới vài trăm). Nếu bạn cần làm hệ thống Chat Realtime, Web Scraper cào hàng triệu trang web cùng lúc, bạn phải chuyển sang lập trình hướng sự kiện (Event-driven) sử dụng asyncio kết hợp aiohttp (nhẹ hơn Thread rất nhiều).
   2. Khi cần giao tiếp phức tạp giữa các Tiến trình: ProcessPoolExecutor chỉ mạnh khi bạn quăng dữ liệu vào và nhận kết quả ra độc lập. Nếu các tiến trình con cần liên tục nói chuyện với nhau, đồng bộ hóa trạng thái phức tạp, bạn nên dùng module cấp thấp multiprocessing vì nó hỗ trợ Queue, Pipe và Value/Array dùng chung mạnh mẽ hơn.

Để giúp bạn nâng cao tay nghề, bạn có muốn thử giải quyết một bài toán thực tế cụ thể không? Hãy chọn một trong các ý tưởng sau và tôi sẽ hướng dẫn bạn viết code từ A-Z:

* Bài toán 1 (I/O-bound): Viết script tải đồng thời 10 hình ảnh từ internet về máy và lưu vào thư mục.
* Bài toán 2 (CPU-bound): Kiểm tra một danh sách 20 số cực lớn xem số nào là số nguyên tố (phân tích đa tiến trình).
* Bài toán 3 (Xử lý lỗi): Cách viết code để khi 1 luồng bị sập/gặp lỗi (Exception), chương trình chính không bị chết đứng.


