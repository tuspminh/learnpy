Thư viện **`concurrent`** thực chất là một thư viện tiêu chuẩn (built-in package) được cài đặt sẵn khi bạn cài Python (từ phiên bản 3.2 trở đi). Do đó, bạn **không cần phải dùng lệnh`pip install`** để cài đặt nó.

Tuy nhiên, như đã đề cập ở câu trước, `concurrent` chỉ là một thư mục gói (package name). Bản thân nó không chứa mã nguồn thực thi trực tiếp, mà nó bao gồm các module con bên trong. Cho đến hiện tại, module con quan trọng và được sử dụng rộng rãi nhất của nó là **`concurrent.futures`**.

Dưới đây là tổng hợp toàn bộ những gì có bên trong thư viện `concurrent` và cách bạn khai thác nó:

* * *

Các thành phần chính trong `concurrent.futures`

Khi làm việc với thư viện này, bạn chỉ cần nhớ và làm việc quanh **3 khái niệm cốt lõi** :

1\. Các bộ thực thi (Executors)

Đây là lớp trừu tượng (Abstract Class) cung cấp giao diện để thực thi các tác vụ bất đồng bộ. Bạn sẽ không gọi trực tiếp `Executor` mà gọi 2 lớp con của nó:

  * **`ThreadPoolExecutor`** : Tạo ra một nhóm các **luồng (threads)**. Phù hợp nhất cho các tác vụ nghẽn I/O (I/O-bound) như gọi API, tải dữ liệu từ web, đọc/ghi file.
  * **`ProcessPoolExecutor`** : Tạo ra một nhóm các **tiến trình (processes)** trên các lõi CPU độc lập. Phù hợp cho các tác vụ tính toán nặng (CPU-bound) như xử lý hình ảnh, ma trận, giải thuật toán phức tạp nhằm vượt qua rào cản của cơ chế Python GIL.



2\. Đối tượng Tương lai (Future Object)

Khi bạn giao một việc cho bộ thực thi bằng hàm `.submit()`, nó không bắt bạn phải đứng đợi kết quả ngay lập tức mà trả về một đối tượng gọi là `Future`.

  * Nó giống như chiếc "vé hẹn" hoặc "phiếu chờ".
  * Bạn có thể dùng chiếc vé này để kiểm tra xem tác vụ đã chạy xong chưa (`.done()`), hủy tác vụ (`.cancel()`), hoặc lấy kết quả cuối cùng ra (`.result()`).



3\. Các hàm bổ trợ quản lý luồng

  * **`as_completed(fs)`** : Nhận vào danh sách các đối tượng `Future` và trả về kết quả của từng tác vụ **ngay khi nó vừa hoàn thành xong** , không quan trọng tác vụ nào được gửi vào trước.
  * **`wait(fs)`** : Dừng chương trình lại để đợi cho đến khi một điều kiện thỏa mãn (ví dụ: đợi cho tất cả các tác vụ chạy xong, hoặc chỉ cần tác vụ đầu tiên xong là đi tiếp).



* * *

Cách Import chuẩn trong Python

Bạn có thể import thư viện này theo các cách sau tùy nhu cầu viết code:

python
    
    
    # Cách 1: Import trực tiếp các công cụ cần dùng (Khuyên dùng vì code ngắn gọn)
    from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
    
    # Cách 2: Import toàn bộ module futures
    from concurrent import futures
    
    # Lúc này khi dùng bạn phải ghi rõ:
    # executor = futures.ThreadPoolExecutor(max_workers=5)
    

Hãy thận trọng khi sử dụng mã.

* * *

Một ví dụ thực tế sử dụng `ProcessPoolExecutor` (Xử lý nặng CPU)

Để bạn thấy sức mạnh của module song song này, đây là cách chia nhỏ một bài toán tính toán nặng (ví dụ: kiểm tra số nguyên tố lớn hoặc mã hóa chuỗi) cho nhiều lõi CPU chạy cùng lúc:

python
    
    
    import time
    from concurrent.futures import ProcessPoolExecutor
    
    # Hàm giả lập tính toán nặng, ngốn nhiều tài nguyên CPU
    def heavy_calculation(number):
        count = 0
        for i in range(1, number):
            count += i
        return count
    
    if __name__ == "__main__":
        numbers = [20000000, 21000000, 22000000, 23000000]
        
        start_time = time.time()
        
        # Sử dụng ProcessPoolExecutor để tận dụng đa nhân (Multi-core) của máy tính
        # Hàm executor.map() sẽ tự chia 4 con số trên cho các nhân CPU xử lý song song
        with ProcessPoolExecutor() as executor:
            results = executor.map(heavy_calculation, numbers)
            
        print(f"Kết quả: {list(results)}")
        print(f"Tổng thời gian xử lý song song: {time.time() - start_time:.2f} giây")
    

Hãy thận trọng khi sử dụng mã.

_(Lưu ý: Đối với`ProcessPoolExecutor`, bạn bắt buộc phải đặt code chạy trong khối `if __name__ == "__main__":` để tránh lỗi lặp vô hạn khi Python khởi tạo các tiến trình con)._

Bạn đang muốn áp dụng thư viện này vào việc **tối ưu tốc độ cho một đoạn code cụ thể nào** trong dự án của mình không? Hãy chia sẻ đoạn code đó, tôi sẽ giúp bạn chuyển đổi nó sang dạng chạy song song.

