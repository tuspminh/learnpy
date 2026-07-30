Để sử dụng **`ThreadPoolExecutor`** , bạn có thể lựa chọn 1 trong 2 cách tiếp cận tùy thuộc vào nhu cầu nhận kết quả: dùng **`map()`** (khi cần nhận kết quả theo đúng thứ tự đầu vào) hoặc dùng **`submit()`** kết hợp với **`as_completed()`** (khi muốn lấy kết quả ngay lập tức khi bất kỳ luồng nào chạy xong).

Dưới đây là hướng dẫn chi tiết kèm code mẫu cho cả 2 cách dùng phổ biến nhất.

* * *

Cách 1: Sử dụng `executor.map()` (Đơn giản, giữ đúng thứ tự)

Cách này phù hợp khi bạn có một danh sách dữ liệu (như danh sách các URL, các file) và muốn áp dụng chung một hàm xử lý cho toàn bộ danh sách đó.

python
    
    
    import time
    from concurrent.futures import ThreadPoolExecutor
    
    # Hàm xử lý tác vụ (I/O-bound)
    def fetch_data(item_id: int):
        print(f"Đang xử lý item {item_id}...")
        time.sleep(1) # Giả lập thời gian chờ phản hồi mạng
        return f"Kết quả của item {item_id}"
    
    items = [10, 20, 30, 40, 50]
    
    start_time = time.time()
    
    # Khởi tạo Pool với tối đa 3 luồng chạy song song
    with ThreadPoolExecutor(max_workers=3) as executor:
        # executor.map tự động gán từng phần tử trong danh sách 'items' vào hàm 'fetch_data'
        results = executor.map(fetch_data, items)
    
    # results là một generator, duyệt qua sẽ trả về kết quả theo ĐÚNG thứ tự [10, 20, 30, 40, 50]
    for result in results:
        print(f"Nhận: {result}")
    
    print(f"Tổng thời gian: {time.time() - start_time:.2f} giây")
    # Giải thích: 5 tác vụ chia cho pool 3 luồng sẽ mất khoảng 2 giây để chạy xong
    

Hãy thận trọng khi sử dụng mã.

* * *

Cách 2: Sử dụng `executor.submit()` và `as_completed()` (Linh hoạt, nhận kết quả sớm nhất)

Cách này tối ưu hơn khi các tác vụ có thời gian phản hồi nhanh chậm khác nhau. Tác vụ nào xong trước sẽ được xử lý trước, không cần đợi các tác vụ đứng trước nó trong danh sách.

python
    
    
    import time
    import random
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def download_file(filename: str):
        # Mỗi file sẽ mất một khoảng thời gian ngẫu nhiên để tải xong
        process_time = random.randint(1, 3)
        time.sleep(process_time)
        return f"File {filename} tải xong trong {process_time}s"
    
    filenames = ["image.png", "video.mp4", "document.pdf", "data.json"]
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        # 1. Gửi các tác vụ vào pool bằng submit()
        # submit() trả về một đối tượng Future, ta lưu nó làm key trong dictionary để biết nó thuộc về file nào
        future_to_file = {executor.submit(download_file, name): name for name in filenames}
        
        # 2. Lấy kết quả ngay khi có bất kỳ luồng nào hoàn thành xong
        for future in as_completed(future_to_file):
            filename = future_to_file[future]
            try:
                # Lấy kết quả trả về từ hàm download_file
                data = future.result() 
                print(f"[Thành công] {data}")
            except Exception as exc:
                # Nếu trong hàm xảy ra lỗi, lỗi đó sẽ được ném ra tại đây để bạn xử lý
                print(f"[Lỗi] File {filename} gặp sự cố: {exc}")
    

Hãy thận trọng khi sử dụng mã.

* * *

💡 4 Quy tắc vàng khi sử dụng ThreadPoolExecutor

  1. **Luôn luôn sử dụng từ khóa`with` (Context Manager):** Tránh việc quên gọi `executor.shutdown()`. Khối `with` đảm bảo tất cả các luồng con sẽ giải phóng tài nguyên an toàn sau khi chạy xong code bên trong.
  2. **Cách tính`max_workers` tối ưu:**
     * Đối với các tác vụ mạng/I/O (gọi API, crawl web), số lượng worker có thể đặt **lớn hơn số nhân CPU** của máy (ví dụ: `min(32, (os.cpu_count() or 1) + 4)` hoặc cấu hình trực tiếp từ `10` đến `30` tùy thuộc vào giới hạn băng thông hoặc giới hạn Rate Limit của API phía đối tác).
  3. **Xử lý ngoại lệ (Exception Handling):**
     * Nếu bạn dùng `map()`, khi một tác vụ bị lỗi, ngoại lệ sẽ được ném ra ngay khi bạn duyệt (`loop`) qua phần tử bị lỗi đó.
     * Nếu bạn dùng `submit()`, lỗi sẽ nằm bên trong đối tượng Future và chỉ ném ra khi bạn gọi phương thức `.result()`.
  4. **Tránh chia sẻ dữ liệu chung (Shared State):** Nếu các luồng cùng ghi dữ liệu vào một `list` hoặc `dict` toàn cục mà không có cơ chế khóa (`threading.Lock`), dữ liệu sẽ dễ bị lỗi hoặc sai lệch (Race Condition). Nên cấu hình để các hàm luồng trả kết quả về thông qua lệnh `return`.



Bạn có muốn tôi hướng dẫn cách áp dụng `ThreadPoolExecutor` này vào một trường hợp thực tế cụ thể nào không, chẳng hạn như **gửi mail hàng loạt** hay **tải xuống danh sách ảnh** từ một trang web?

