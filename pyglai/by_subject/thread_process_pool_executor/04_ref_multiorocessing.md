multiprocessing là một module chuẩn của Python cho phép bạn tạo ra các tiến trình (Processes) hoàn toàn độc lập.
Nếu như ProcessPoolExecutor (trong module concurrent.futures) là một lớp bọc cao cấp, đơn giản hóa mọi thứ thành một "cái hồ chứa" (Pool) để bạn ném việc vào, thì multiprocessing chính là thư viện nền tảng cấp thấp (low-level) nằm bên dưới. Nó cung cấp cho bạn toàn bộ quyền lực để can thiệp, điều khiển, bắt các tiến trình "nói chuyện" với nhau, chia sẻ bộ nhớ và đồng bộ hóa một cách chi tiết nhất.
------------------------------
## 1. Tại sao cần dùng multiprocessing thay vì concurrent.futures?
Bạn nên chuyển từ ProcessPoolExecutor sang dùng module multiprocessing gốc khi rơi vào các trường hợp:

* 🔀 Cần các tiến trình giao tiếp liên tục: Các tiến trình con cần truyền tin nhắn, gửi dữ liệu qua lại cho nhau trong lúc đang chạy (chứ không phải đợi chạy xong mới trả kết quả).
* 🔒 Đồng bộ hóa nâng cao: Cần dùng cơ chế khóa như Lock, Semaphore, Event giữa các tiến trình để tránh xung đột dữ liệu.
* 🛠 Kiểm soát vòng đời chi tiết: Bạn muốn tự tay đặt tên cho tiến trình, chủ động ép nó dừng (terminate), kiểm tra xem nó còn sống hay chết (is_alive) tại bất kỳ thời điểm nào.

------------------------------
## 2. Cách khởi tạo một Tiến trình cơ bản (Process)
Thay vì ném vào một cái Pool, bạn tự tay định nghĩa và kích hoạt từng tiến trình một.

import osimport timefrom multiprocessing import Process
def worker_task(name):
    # os.getpid() giúp lấy ID của tiến trình hiện tại trên hệ điều hành
    print(f"Tiến trình {name} (PID: {os.getpid()}) bắt đầu chạy...")
    time.sleep(2)
    print(f"Tiến trình {name} hoàn thành.")
if __name__ == '__main__':
    # Khởi tạo 2 tiến trình độc lập, truyền tham số qua `args` (dưới dạng tuple)
    p1 = Process(target=worker_task, args=("A",))
    p2 = Process(target=worker_task, args=("B",))

    # Kích hoạt tiến trình (chạy bất đồng bộ)
    p1.start()
    p2.start()

    # .join() bắt chương trình chính (tiến trình cha) dừng lại chờ p1 và p2 xong rồi mới đi tiếp
    p1.join()
    p2.join()

    print("Tất cả các tiến trình đã xử lý xong. Chương trình chính kết thúc.")

------------------------------
## 3. Cơ chế giao tiếp giữa các tiến trình (Inter-Process Communication - IPC)
Như bạn đã biết từ cơ chế Pickle, các tiến trình có vùng nhớ riêng biệt. Để chúng có thể gửi dữ liệu cho nhau, multiprocessing cung cấp hai công cụ chính:
## 🟢 Cách 1: Sử dụng Queue (Hàng đợi an toàn cho đa tiến trình)
Queue hoạt động theo nguyên lý FIFO (Vào trước - Ra trước). Nó tự động lo liệu việc Pickle dữ liệu khi một tiến trình đẩy vào (put) và Unpickle khi tiến trình khác lấy ra (get).

import timefrom multiprocessing import Process, Queue
def producer(q):
    """Tiến trình tạo ra dữ liệu"""
    for i in range(3):
        print(f"Tạo ra sản phẩm {i}")
        q.put(f"Sản phẩm {i}")
        time.sleep(1)
    q.put(None) # Tín hiệu báo hiệu đã hết dữ liệu
def consumer(q):
    """Tiến trình tiêu thụ dữ liệu"""
    while True:
        item = q.get() # Sẽ đợi (block) cho đến khi có dữ liệu trong Queue
        if item is None:
            break
        print(f"Đang xử lý: {item}")
if __name__ == '__main__':
    queue = Queue()

    p_prod = Process(target=producer, args=(queue,))
    p_cons = Process(target=consumer, args=(queue,))

    p_prod.start()
    p_cons.start()

    p_prod.join()
    p_cons.join()

## 🔵 Cách 2: Sử dụng Pipe (Đường ống hai chiều)
Pipe() trả về một cặp đối tượng kết nối (conn1, conn2) đại diện cho hai đầu của một đường ống. Thường dùng khi bạn chỉ có đúng 2 tiến trình cần nói chuyện trực tiếp với nhau theo mô hình 1-1.

* Tiến trình này dùng conn1.send(data) thì tiến trình kia sẽ nhận bằng conn2.recv().

------------------------------
## 4. Chia sẻ trạng thái bộ nhớ (Shared Memory)
Nếu bạn thực sự muốn các tiến trình con dùng chung một vùng bộ nhớ (thay vì sao chép hoặc truyền tin nhắn), bạn phải dùng các đối tượng đặc biệt được quản lý bởi hệ điều hành:

* Value và Array: Định nghĩa một ô nhớ chứa số nguyên, số thực hoặc một mảng dữ liệu có kích thước cố định được chia sẻ trực tiếp.
* Manager: Tiện lợi hơn, giúp bạn tạo ra các đối tượng quen thuộc như list hoặc dict được chia sẻ giữa các tiến trình (nhưng tốc độ sẽ chậm hơn Value/Array do có một tiến trình máy chủ quản lý ngầm).

from multiprocessing import Process, Manager
def update_dict(shared_dict, shared_list):
    shared_dict["status"] = "Đang chạy"
    shared_list.append("Dữ liệu mới từ tiến trình con")
if __name__ == '__main__':
    with Manager() as manager:
        # Tạo dict và list đặc biệt có khả năng chia sẻ
        d = manager.dict({"status": "Khởi tạo"})
        l = manager.list(["Dữ liệu gốc"])

        p = Process(target=update_dict, args=(d, l))
        p.start()
        p.join()

        # Tiến trình cha in ra xem dữ liệu thay đổi chưa
        print(d)  # Kết quả: {'status': 'Đang chạy'}
        print(l)  # Kết quả: ['Dữ liệu gốc', 'Dữ liệu mới từ tiến trình con']

------------------------------
## 5. So sánh: multiprocessing vs ProcessPoolExecutor

| Tiêu chí | ProcessPoolExecutor (Futures) | multiprocessing (Gốc) |
|---|---|---|
| Mức độ phức tạp | Rất thấp, dễ viết, dễ đọc. | Cao hơn, phải tự quản lý vòng đời. |
| Kiểm soát Tiến trình | Tự động (Hệ thống tự tạo/tắt tiến trình). | Thủ công (Bạn tự start, join, terminate). |
| Giao tiếp (IPC) | Chỉ nhận kết quả khi hàm chạy xong (return). | Giao tiếp thời gian thực qua Queue, Pipe. |
| Chia sẻ bộ nhớ | Không hỗ trợ trực tiếp. | Hỗ trợ qua Value, Array, Manager. |
| Phù hợp nhất cho | Chạy một loạt tác vụ tính toán độc lập, song song. | Xây dựng các kiến trúc hệ thống phức tạp (Pipeline, Chat server, Engine game). |

Bạn có muốn tôi hướng dẫn sâu hơn về cách áp dụng Lock (Khóa chống xung đột) dữ liệu khi nhiều tiến trình cùng ghi vào một file, hay bạn muốn làm một bài tập thực hành liên kết các tiến trình bằng Queue?

