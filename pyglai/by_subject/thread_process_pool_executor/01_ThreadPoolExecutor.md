ThreadPoolExecutor trong module concurrent.futures của Python là một công cụ cao cấp giúp bạn quản lý và tự động hóa việc chạy đa luồng (Multi-threading). Nó giúp chương trình thực hiện nhiều tác vụ cùng một lúc mà không cần phải tự tạo hay tắt từng luồng (Thread) thủ công. Công cụ này cực kỳ hiệu quả để tăng tốc các tác vụ phụ thuộc vào I/O (I/O-bound) như tải file, cào web, hoặc gọi API. [1, 2, 3] 
------------------------------
## 1. Khi nào nên và không nên dùng?
Do Python có cơ chế GIL (Global Interpreter Lock), đa luồng không thể tận dụng nhiều lõi CPU để tính toán song song cùng lúc. Vì vậy: [1] 

* 🟢 Nên dùng cho (I/O-bound): Gửi yêu cầu HTTP, đọc/ghi file, truy vấn cơ sở dữ liệu, tải dữ liệu từ internet. Thời gian chờ mạng hoặc chờ ổ cứng sẽ được tận dụng để chạy luồng khác. [1, 4, 5] 
* 🔴 Không nên dùng cho (CPU-bound): Các phép toán nặng, mã hóa, nén file, xử lý ảnh. Đối với các tác vụ này, bạn phải dùng ProcessPoolExecutor (đa tiến trình). [1, 3, 6] 

------------------------------
## 2. Cách sử dụng cơ bản với with và map()
Phương thức map() là cách đơn giản nhất khi bạn có một hàm duy nhất và muốn áp dụng nó cho một danh sách dữ liệu. [6, 7] 
```
import timefrom concurrent.futures import ThreadPoolExecutor


# Hàm giả lập tải dữ liệu từ internet (mất 2 giây)
def download_site(url):
    print(f"Bắt đầu tải: {url}")
    time.sleep(2)  # Giả lập thời gian chờ phản hồi từ network
    print(f"Tải xong: {url}")
    return f"Dữ liệu từ {url}"

urls = ["site1.com", "site2.com", "site3.com", "site4.com"]
start_time = time.time()

# Sử dụng câu lệnh with để tự động dọn dẹp và đóng các luồng khi xong
with ThreadPoolExecutor(max_workers=3) as executor:
    # executor.map trả về một generator chứa kết quả theo đúng thứ tự của danh sách đầu vào
    results = executor.map(download_site, urls)

# In kết quả nhận được
for result in results:
    print(result)

print(f"Tổng thời gian thực hiện: {time.time() - start_time:.2f} giây")
```

* max_workers=3: Chỉ cho phép tối đa 3 luồng chạy cùng một lúc. URL thứ 4 sẽ phải xếp hàng chờ một luồng trống. [5, 8, 9] 

------------------------------
## 3. Cách sử dụng linh hoạt với submit() và Future
Nếu bạn muốn chạy nhiều hàm khác nhau, truyền các tham số khác nhau, hoặc cần kiểm soát trạng thái của từng tác vụ, hãy dùng submit(). Hàm này trả về một đối tượng gọi là Future (đại diện cho một kết quả trong tương lai). [9] 
```
import timefrom concurrent.futures import ThreadPoolExecutor, as_completed


def task(name, delay):
    print(f"Tác vụ {name} đang chạy...")
    time.sleep(delay)
    return f"Kết quả của {name} sau {delay}s"

with ThreadPoolExecutor(max_workers=2) as executor:
    # Kích hoạt các tác vụ bất đồng bộ, submit trả về đối tượng Future
    future1 = executor.submit(task, "A", 3)
    future2 = executor.submit(task, "B", 1)
    future3 = executor.submit(task, "C", 2)
    
    # Gom các Future lại thành một danh sách
    futures = [future1, future2, future3]
    
    # as_completed() giúp lấy kết quả của tác vụ nào HOÀN THÀNH TRƯỚC
    for future in as_completed(futures):
        print(future.result())  # .result() sẽ lấy giá trị return từ hàm task
```
------------------------------
## 4. So sánh nhanh giữa map() và submit()

| Tiêu chí | executor.map() | executor.submit() |
|---|---|---|
| Cách dùng | Áp dụng 1 hàm cho nhiều phần tử. | Chạy các hàm độc lập, linh hoạt tham số. |
| Thứ tự kết quả | Trả về theo đúng thứ tự của list đầu vào. | Trả về theo thứ tự hoàn thành (tác vụ nào nhanh hơn xong trước). |
| Kiểm soát lỗi | Khó bắt lỗi riêng lẻ của từng luồng. | Dễ dàng quản lý trạng thái và bắt ngoại lệ qua đối tượng Future. |

------------------------------
## 5. Lưu ý quan trọng khi lập trình đa luồng

* Tránh Race Condition: Không nên để nhiều luồng cùng chỉnh sửa (ghi) vào một biến toàn cục hoặc một file cùng một lúc. Nếu bắt buộc, bạn phải dùng cơ chế khóa (threading.Lock).
* Số lượng max_workers tối ưu: Đối với I/O-bound, bạn có thể đặt max_workers lớn hơn số lõi CPU của máy (ví dụ: Số lõi * 5 hoặc thậm chí nhiều hơn tùy thuộc vào độ trễ của mạng).

Để tôi có thể hướng dẫn bạn thực hành tốt nhất, hãy chia sẻ thêm:

* Bạn đang muốn áp dụng ThreadPoolExecutor cho tác vụ cụ thể nào (Ví dụ: Cào dữ liệu web, tải ảnh, hay gọi API)?
* Bạn đã quen thuộc với khái niệm bất đồng bộ (Asynchronous) hoặc thư viện threading cơ bản chưa?


[1] [https://www.geeksforgeeks.org](https://translate.google.com/translate?u=https://www.geeksforgeeks.org/python/how-to-use-threadpoolexecutor-in-python3/&hl=vi&sl=en&tl=vi&client=sge)
[2] [https://vietnix.vn](https://vietnix.vn/hoc-lap-trinh/python/thread-pool-trong-python/)
[3] [https://www.youtube.com](https://www.youtube.com/watch?v=nRVT4olRbMA)
[4] [https://medium.com](https://translate.google.com/translate?u=https://medium.com/@smrati.katiyar/introduction-to-concurrent-futures-in-python-009fe1d4592c&hl=vi&sl=en&tl=vi&client=sge)
[5] [https://viblo.asia](https://viblo.asia/p/tim-hieu-ve-thread-pool-trong-java-OeVKBDQMlkW)
[6] [https://n.pymi.vn](https://n.pymi.vn/concurrent.html)
[7] [https://hosjiu.gitlab.io](https://hosjiu.gitlab.io/personal-blog/2021/06/08/HiConcurrent/)
[8] [https://realpython.com](https://translate.google.com/translate?u=https://realpython.com/intro-to-python-threading/&hl=vi&sl=en&tl=vi&client=sge)
[9] [https://phamdinhkhanh.github.io](https://phamdinhkhanh.github.io/2020/11/30/ParallelComputingPython.html)
