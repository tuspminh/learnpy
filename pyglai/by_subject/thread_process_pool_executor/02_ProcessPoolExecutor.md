ProcessPoolExecutor cũng nằm trong module concurrent.futures, nhưng nó sử dụng đa tiến trình (Multi-processing) thay vì đa luồng (Multi-threading).
Bằng cách tạo ra các tiến trình Python độc lập, ProcessPoolExecutor hoàn toàn vượt qua được rào cản của GIL (Global Interpreter Lock). Điều này cho phép chương trình tận dụng tối đa 100% sức mạnh của tất cả các lõi (cores) CPU trên máy tính của bạn để tính toán song song.
------------------------------
## 1. Khi nào nên dùng và sự khác biệt cốt lõi

* 🟢 Nên dùng cho (CPU-bound): Các tác vụ tính toán nặng, thuật toán phức tạp, xử lý ảnh/video, nén file, xử lý dữ liệu lớn (Big Data), hoặc machine learning cơ bản.
* 🔴 Hạn chế lớn nhất (Memory & Overhead): Mỗi tiến trình (Process) là một bản sao độc lập của chương trình Python. Nó có vùng nhớ riêng, không chia sẻ biến toàn cục với tiến trình khác. Việc khởi tạo một tiến trình tốn thời gian và RAM hơn rất nhiều so với luồng (Thread).

------------------------------
## 2. Ví dụ thực tế: Tính toán nặng với map()
Dưới đây là mã nguồn chạy song song một hàm tính toán nặng (tìm ước chung lớn nhất hoặc băm chuỗi phức tạp liên tục).

```
import timeimport mathfrom concurrent.futures import ProcessPoolExecutor


# Hàm giả lập tính toán nặng tiêu tốn CPUdef heavy_calculation(n):
    # Tính giai thừa của một số lớn để ép CPU làm việc
    return sum(math.factorial(i) for i in range(n))

    
if __name__ == '__main__':
    # BẮT BUỘC phải có `if __name__ == '__main__':` trên Windows/macOS để tránh lặp vô hạn khi tạo tiến trình con
    
    numbers = [500, 600, 700, 800]
    start_time = time.time()
    
    # max_workers mặc định sẽ bằng số lõi CPU vật lý của máy bạn
    with ProcessPoolExecutor() as executor:
        results = executor.map(heavy_calculation, numbers)
        
    for num, result in zip(numbers, results):
        print(f"Số chữ số của kết quả tính từ {num}: {len(str(result))}")
        
    print(f"Tổng thời gian xử lý: {time.time() - start_time:.2f} giây")
```

------------------------------
## 3. Sự khác biệt chí mạng giữa Thread và Process

| Tiêu chí | ThreadPoolExecutor (Luồng) | ProcessPoolExecutor (Tiến trình) |
|---|---|---|
| Bản chất | Nhiều luồng chạy chung trong 1 tiến trình. | Nhiều tiến trình độc lập chạy song song. |
| GIL ảnh hưởng? | Có. Chỉ có 1 luồng được chạy code Python tại một thời điểm. | Không. Mỗi tiến trình có 1 GIL riêng nên chạy song song thực sự. |
| Chia sẻ dữ liệu | Rất dễ. Các luồng dùng chung bộ nhớ (biến toàn cục, list, dict). | Khó. Dữ liệu truyền qua lại phải được "đóng gói" (Pickle). |
| Mức độ tiêu tốn tài nguyên | Rất nhẹ. Khởi tạo cực nhanh. | Rất nặng. Tốn nhiều RAM để nhân bản bộ nhớ. |
| Loại tác vụ tối ưu | I/O-bound (Mạng, File, API). | CPU-bound (Toán học, Mã hóa, Đồ họa). |

------------------------------
## 4. Những "Cạm bẫy" cần tránh khi dùng ProcessPoolExecutor

* Lỗi PicklingError: Vì các tiến trình nằm ở các vùng nhớ khác nhau, mọi dữ liệu bạn truyền vào hàm (tham số) và nhận ra (kết quả return) đều phải được "Pickle" (mã hóa thành byte để gửi qua mạng/tiến trình khác). Nếu bạn truyền một hàm ẩn danh (lambda) hoặc một đối tượng kết nối Database phức tạp vào tiến trình con, Python sẽ báo lỗi.
* Không chia sẻ biến trực tiếp: Nếu tiến trình con thay đổi một biến toàn cục, biến đó ở tiến trình cha (chương trình chính) sẽ không thay đổi. Nếu muốn chia sẻ dữ liệu, bạn phải dùng các công cụ chuyên dụng như multiprocessing.Manager.
* Phải có dòng bảo vệ: Luôn đặt code kích hoạt trong khối if __name__ == '__main__':. Nếu không, khi tiến trình con được sinh ra, nó sẽ chạy lại toàn bộ file code từ đầu, dẫn đến lỗi tạo tiến trình vô hạn làm treo máy.

Bạn có muốn chạy thử một bài toán so sánh trực diện tốc độ giữa ThreadPoolExecutor và ProcessPoolExecutor trên cùng một tác vụ tính toán để thấy rõ sự khác biệt không? Hay bạn đang gặp lỗi PicklingError khi cố gắng áp dụng nó?

