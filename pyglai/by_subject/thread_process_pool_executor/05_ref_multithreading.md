multithreading (đa luồng) trong Python là kỹ thuật chạy nhiều luồng phân đoạn mã cùng một lúc bên trong MỘT tiến trình duy nhất.
Nếu như thư viện multiprocessing giúp bạn tạo ra nhiều tiến trình độc lập để tận dụng nhiều lõi CPU, thì multithreading (thông qua module gốc threading) giúp bạn quản lý nhiều luồng công việc chia sẻ chung một vùng bộ nhớ.
Tuy nhiên, do GIL (Global Interpreter Lock) của Python, các luồng này không thực sự chạy song song trên nhiều lõi CPU để tính toán. Thay vào đó, chúng thay phiên nhau chạy cực nhanh [🟢]. Vì vậy, nó chỉ tối ưu cho các tác vụ nghẽn I/O (I/O-bound) — nơi các luồng tận dụng thời gian chờ (chờ mạng, chờ ổ cứng) để nhường quyền chạy cho luồng khác [🟢].
------------------------------
## 1. Cách khởi tạo một Luồng cơ bản với module threading
Module threading là thư viện cấp thấp nằm dưới ThreadPoolExecutor [🟢]. Dưới đây là cách bạn tự tay tạo, đặt tên và quản lý vòng đời của từng luồng:

import threadingimport time
def print_numbers(thread_name, delay):
    print(f"Luồng {thread_name} bắt đầu...")
    for i in range(1, 4):
        time.sleep(delay)  # Giả lập tác vụ chờ (I/O)
        print(f"[{thread_name}] Đếm: {i}")
    print(f"Luồng {thread_name} kết thúc.")
# 1. Khởi tạo các đối tượng Thread độc lậpt1 = threading.Thread(target=print_numbers, args=("A", 1), name="Thread-A")t2 = threading.Thread(target=print_numbers, args=("B", 1.5), name="Thread-B")
# 2. Kích hoạt luồng (chạy bất đồng bộ)
t1.start()
t2.start()
# 3. Chờ luồng hoàn thành
t1.join()  # Ép chương trình chính dừng lại đợi t1 xong
t2.join()  # Ép chương trình chính dừng lại đợi t2 xong

print("Tất cả các luồng đã chạy xong. Luồng chính (Main Thread) kết thúc.")

------------------------------
## 2. Cạm bẫy chí mạng: Hiện tượng Xung đột dữ liệu (Race Condition)
Vì tất cả các luồng trong một tiến trình dùng chung một vùng bộ nhớ (biến toàn cục, danh sách, từ điển) [🟢], hai luồng hoàn toàn có thể nhảy vào chỉnh sửa cùng một biến tại cùng một thời điểm, dẫn đến sai lệch dữ liệu nghiêm trọng.
## ❌ Ví dụ về mã nguồn lỗi (Race Condition):

import threadingimport time
counter = 0
def increase():
    global counter
    for _ in range(1000000):
        # Thao tác này gồm 3 bước: Đọc giá trị -> Cộng 1 -> Ghi lại giá trị.
        # Luồng A đang làm dở bước 2 thì luồng B nhảy vào đọc, dẫn đến mất dữ liệu cộng.
        counter += 1
t1 = threading.Thread(target=increase)t2 = threading.Thread(target=increase)

t1.start()
t2.start()
t1.join()
t2.join()

print(f"Giá trị mong muốn: 2000000")
print(f"Giá trị thực tế: {counter}") # Kết quả sẽ ra một số nhỏ hơn 2 triệu và ngẫu nhiên

------------------------------
## 3. Giải pháp: Sử dụng threading.Lock (Khóa đồng bộ)
Để giải quyết Race Condition, bạn phải dùng cơ chế Lock (Khóa) [🔒]. Khi một luồng chiếm giữ khóa (acquire), bất kỳ luồng nào khác muốn đụng vào đoạn mã đó đều phải xếp hàng chờ cho đến khi khóa được giải phóng (release).
Cách an toàn và chuyên nghiệp nhất là sử dụng câu lệnh with lock: [🟢]:

import threading
counter = 0data_lock = threading.Lock() # Tạo một ổ khóa toàn cục
def safe_increase():
    global counter
    for _ in range(1000000):
        # Sử dụng with để tự động khóa khi vào khối lệnh và mở khóa khi ra ngoài
        with data_lock:
            counter += 1
t1 = threading.Thread(target=safe_increase)t2 = threading.Thread(target=safe_increase)

t1.start()
t2.start()
t1.join()
t2.join()

print(f"Giá trị an toàn tuyệt đối: {counter}") # Chắc chắn ra 2000000

------------------------------
## 4. Khái niệm Luồng chạy ngầm (Daemon Thread)
Thông thường, một chương trình Python chỉ kết thúc khi tất cả các luồng thông thường chạy xong. Tuy nhiên, có những luồng bạn chỉ muốn nó chạy nền (như luồng kiểm tra pin, luồng dọn rác, luồng log dữ liệu), nếu chương trình chính tắt thì nó phải tắt theo. Đó gọi là Daemon Thread.

import threadingimport time
def background_task():
    while True:
        print("Tôi là luồng chạy ngầm, đang kiểm tra hệ thống...")
        time.sleep(0.5)
# Bật thuộc tính daemon=True trước khi .start()t = threading.Thread(target=background_task, daemon=True)
t.start()

time.sleep(2)
print("Chương trình chính kết thúc tại đây!")# Khi luồng chính kết thúc, luồng `t` (daemon) sẽ bị ép buộc tắt ngay lập tức

------------------------------
## 5. So sánh: threading gốc vs ThreadPoolExecutor

| Tiêu chí | threading (Gốc) | ThreadPoolExecutor (High-level) |
|---|---|---|
| Quản lý luồng | Bạn phải tự start(), join() từng luồng thủ công [🟢]. | Tự động quản lý số lượng luồng thông qua Pool (max_workers) [🟢]. |
| Lấy kết quả (return) | Hàm chạy trong Thread không thể trả về giá trị trực tiếp (phải lưu qua danh sách ngoài hoặc Queue). | Lấy dữ liệu cực dễ qua đối tượng Future (.result()) [🟢]. |
| Tái sử dụng | Xong việc là luồng tự hủy. Tạo luồng mới tốn tài nguyên hệ thống. | Tái sử dụng lại các luồng cũ trong Pool để chạy tác vụ mới, tiết kiệm tài nguyên. |
| Phù hợp nhất khi | Cần kiểm soát rất sâu (Ví dụ: tạo Daemon Thread chạy vô hạn, điều khiển tinh vi với Event, Semaphore). | Cần chạy một danh sách tác vụ I-O lặp đi lặp lại nhanh gọn lẹ [🟢]. |

Đến đây, bạn đã đi qua toàn bộ bức tranh toàn cảnh về lập trình song song/bất đồng bộ trong Python: từ concurrent.futures, sang multiprocessing, và kết thúc ở multithreading.
Bạn có muốn làm thử một bài tập tổng hợp: Viết một chương trình cào dữ liệu từ 5 trang web bằng multithreading, sử dụng Lock để ghi kết quả vào một file text duy nhất an toàn không?

