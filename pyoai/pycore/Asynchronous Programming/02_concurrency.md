# Python Asynchronous Programming - Buổi 2

# Concurrency vs Parallelism - Hiểu đúng trước khi học Asyncio

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ hiểu:
>
> * Concurrency là gì.
> * Parallelism là gì.
> * Sự khác nhau giữa Sequential, Thread, Process và Async.
> * Vì sao Async không phải là Multi-thread.
> * Khi nào nên dùng từng mô hình.

---

# 1. Một câu chuyện mở đầu

Giả sử bạn có **10 bức ảnh** cần tải từ Internet.

Mỗi ảnh mất **2 giây**.

Có 4 cách để viết chương trình.

---

## Cách 1 - Sequential (Tuần tự)

```text
Ảnh 1 → xong
        ↓
Ảnh 2 → xong
        ↓
Ảnh 3 → xong
        ↓
...
        ↓
Ảnh 10 → xong
```

Python làm từng việc một.

Nếu mỗi ảnh mất 2 giây:

```text
2 × 10 = 20 giây
```

Đây là cách đơn giản nhất nhưng cũng chậm nhất.

---

# 2. Concurrency là gì?

Định nghĩa:

> **Concurrency** là khả năng xử lý nhiều công việc trong cùng một khoảng thời gian bằng cách **luân phiên** giữa chúng.

Chú ý:

Không có nghĩa là chạy cùng lúc.

Ví dụ:

Bạn đang:

* nấu cơm
* giặt đồ
* xem email

Bạn không làm đồng thời bằng hai tay.

Bạn làm:

```text
Nấu cơm

↓

Giặt đồ

↓

Kiểm tra email

↓

Quay lại nấu

↓

Quay lại giặt
```

Bạn liên tục chuyển đổi giữa các công việc.

Đó là **Concurrency**.

---

# 3. Parallelism là gì?

Parallelism là:

> Nhiều công việc thực sự chạy cùng một thời điểm.

Ví dụ:

Bạn có:

* 4 đầu bếp

Mỗi người nấu một món.

```text
Đầu bếp A → Món 1

Đầu bếp B → Món 2

Đầu bếp C → Món 3

Đầu bếp D → Món 4
```

Các món được nấu cùng lúc.

Đây là Parallelism.

---

# 4. Hình dung trực quan

## Sequential

```text
Task A
██████████

Task B
          ██████████

Task C
                    ██████████
```

---

## Concurrency

```text
Task A
██  ██  ██

Task B
  ██  ██

Task C
    ██  ██
```

CPU liên tục chuyển qua lại.

---

## Parallelism

```text
CPU1
██████████

CPU2
██████████

CPU3
██████████
```

Ba CPU cùng làm việc.

---

# 5. Vì sao dễ nhầm?

Nhiều người nghĩ:

```text
Async = Song song
```

Sai.

Async chủ yếu là:

```text
Concurrency
```

không phải

```text
Parallelism
```

---

# 6. Ví dụ thực tế

Giả sử:

Download 3 file.

## Blocking

```python
download(file1)
download(file2)
download(file3)
```

Timeline

```text
file1
██████

file2
      ██████

file3
            ██████
```

---

## Async

```text
file1
██  ██

file2
  ██  ██

file3
    ██  ██
```

Khi file1 đang chờ Internet,

Python chuyển sang file2.

Sau đó chuyển sang file3.

CPU gần như không đứng yên.

---

# 7. Thread là gì?

Một chương trình có thể có nhiều Thread.

Ví dụ

```text
Process

├── Thread 1

├── Thread 2

├── Thread 3
```

Mỗi Thread có:

* Stack riêng
* Con trỏ lệnh riêng

Nhưng:

* Dùng chung bộ nhớ.

---

Ví dụ

```python
from threading import Thread
import time

def work(name):
    for i in range(5):
        print(name, i)
        time.sleep(1)

Thread(target=work, args=("A",)).start()
Thread(target=work, args=("B",)).start()
```

Hai thread cùng chạy.

---

# 8. Process là gì?

Process là chương trình độc lập.

Ví dụ:

Mở:

* Chrome
* VS Code
* Spotify

Đó là:

```text
Process 1

Process 2

Process 3
```

Mỗi Process có:

* RAM riêng
* Không gian nhớ riêng
* GIL riêng (đối với Python)

---

Ví dụ

```python
from multiprocessing import Process

def work():
    print("Hello")

Process(target=work).start()
```

---

# 9. Async nằm ở đâu?

```text
Process

↓

Main Thread

↓

Event Loop

↓

Coroutine 1

Coroutine 2

Coroutine 3
```

Điểm rất quan trọng:

Async thường chỉ cần **một Thread**.

Không tạo Thread mới cho mỗi công việc.

---

# 10. So sánh trực quan

## Sequential

```text
CPU

↓

Task A

↓

Task B

↓

Task C
```

---

## Thread

```text
CPU

↓

Thread A

↓

Thread B

↓

Thread C
```

Hệ điều hành quyết định chuyển đổi giữa các thread.

---

## Process

```text
CPU1 → Process A

CPU2 → Process B

CPU3 → Process C
```

---

## Async

```text
CPU

↓

Event Loop

↓

Coroutine A

↓

Coroutine B

↓

Coroutine C
```

Event Loop chủ động chuyển đổi giữa các coroutine khi chúng chờ I/O.

---

# 11. So sánh bằng ví dụ đời sống

Giả sử bạn là nhân viên văn phòng.

## Sequential

```text
Làm báo cáo

↓

Xong

↓

Trả lời email

↓

Xong

↓

Photo tài liệu
```

---

## Thread

Bạn thuê thêm người.

```text
Bạn → Báo cáo

Đồng nghiệp → Email
```

---

## Process

Hai công ty khác nhau cùng làm.

---

## Async

Bạn:

```text
Gửi máy in

↓

Trong lúc đợi

↓

Trả lời email

↓

Đợi email

↓

Sửa báo cáo

↓

Máy in xong

↓

Lấy giấy
```

Không đứng chờ máy in.

Đó là Async.

---

# 12. Bảng so sánh

| Đặc điểm            | Sequential | Thread                                | Process        | Async                 |
| ------------------- | ---------- | ------------------------------------- | -------------- | --------------------- |
| Nhiều việc          | ❌          | ✅                                     | ✅              | ✅                     |
| Song song thật      | ❌          | Có thể (phụ thuộc GIL và loại tác vụ) | ✅              | ❌                     |
| Phù hợp CPU-bound   | ❌          | Hạn chế trong CPython                 | ✅              | ❌                     |
| Phù hợp I/O-bound   | ❌          | ✅                                     | Có thể         | ✅                     |
| Tốn RAM             | Thấp       | Thấp                                  | Cao            | Rất thấp              |
| Chuyển đổi ngữ cảnh | Không      | Do HĐH quản lý                        | Do HĐH quản lý | Do Event Loop quản lý |

---

# 13. Khi nào dùng gì?

## Sequential

✔ Script nhỏ

✔ Chương trình đơn giản

---

## Thread

✔ Đọc nhiều file

✔ Giao diện GUI

✔ Tác vụ I/O không hỗ trợ async

✔ Làm việc với thư viện chỉ có API đồng bộ

---

## Process

✔ AI

✔ Machine Learning

✔ Render Video

✔ Xử lý ảnh

✔ Mã hóa

✔ Tính toán lớn

---

## Async

✔ API Server

✔ FastAPI

✔ WebSocket

✔ Downloader

✔ Web Crawler

✔ Chat Server

✔ Bot Telegram

✔ Bot Discord

✔ Database bất đồng bộ

✔ PySide6 + Network

---

# 14. Một hiểu lầm rất phổ biến

Có người nói:

> Async nhanh hơn Thread.

Không đúng.

Đúng phải là:

> Async **thường hiệu quả hơn** Thread trong nhiều bài toán **I/O-bound** vì không cần tạo nhiều thread và giảm chi phí chuyển đổi ngữ cảnh. Tuy nhiên, với tác vụ CPU-bound, Async không mang lại lợi ích về tốc độ.

Lựa chọn phụ thuộc vào bài toán.

---

# 15. Mô hình tổng quát

```text
                 Chương trình Python
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   Sequential        Concurrency      Parallelism
                         │                │
             ┌───────────┴───────┐        │
             │                   │        │
          Thread             Asyncio   Multiprocessing
                                 │
                           Event Loop
                                 │
                           Coroutines
```

---

# Tổng kết

Hãy ghi nhớ 5 ý quan trọng:

1. **Sequential**: làm từng việc một.
2. **Concurrency**: xử lý nhiều việc bằng cách luân phiên.
3. **Parallelism**: nhiều việc thực sự chạy cùng lúc.
4. **Asyncio** là một mô hình **Concurrency**, không phải **Parallelism**.
5. Với Python, **Async** rất mạnh cho các tác vụ **I/O-bound**, còn **Multiprocessing** phù hợp hơn với **CPU-bound**.

---

# Bài tập thực hành

### Bài 1

Viết một chương trình tuần tự:

```python
import time

for i in range(3):
    print(f"Task {i + 1} bắt đầu")
    time.sleep(2)
    print(f"Task {i + 1} kết thúc")
```

Đo tổng thời gian thực thi và giải thích vì sao mất khoảng 6 giây.

---

### Bài 2

Viết lại ví dụ trên bằng `threading.Thread`, chạy 3 tác vụ song song và quan sát thứ tự các dòng được in ra.

---

### Bài 3

Vẽ sơ đồ (trên giấy hoặc bằng Markdown) để mô tả sự khác nhau giữa:

* Sequential
* Thread
* Process
* Async

Mục tiêu là bạn có thể tự giải thích cho người khác mà không cần nhìn tài liệu.

---

## Chuẩn bị cho Buổi 3

Ở buổi tiếp theo, chúng ta sẽ tìm hiểu **CPU-bound và I/O-bound** một cách chuyên sâu. Bạn sẽ biết vì sao:

* `asyncio` không thể làm vòng lặp tính toán chạy nhanh hơn.
* `asyncio` có thể tăng đáng kể hiệu quả khi tải dữ liệu từ mạng hoặc truy cập cơ sở dữ liệu.
* Làm thế nào để nhận biết một bài toán nên dùng **Async**, **Thread** hay **Process**. Đây là nền tảng quan trọng trước khi bắt đầu viết các coroutine đầu tiên với `async` và `await`.
