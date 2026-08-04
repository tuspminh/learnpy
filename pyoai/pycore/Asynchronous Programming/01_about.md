# Python Asynchronous Programming - Buổi 1

# Blocking, Non-blocking và vì sao Async ra đời

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ hiểu:
>
> * Chương trình máy tính thực thi như thế nào.
> * Blocking là gì.
> * Non-blocking là gì.
> * Vì sao chương trình bị "đơ".
> * Vì sao Python cần asyncio.
> * Khi nào nên dùng Async.

---

# 1. Chương trình chạy như thế nào?

Giả sử chương trình đơn giản:

```python
print("A")
print("B")
print("C")
```

Kết quả

```
A
B
C
```

Python thực hiện từng dòng một.

```
CPU

↓

print("A")

↓

print("B")

↓

print("C")
```

Điều này gọi là **Sequential Execution** (thực thi tuần tự).

Trong Python mặc định:

> Một câu lệnh chưa chạy xong thì câu lệnh sau chưa được thực hiện.

---

# Ví dụ

```python
import time

print("A")

time.sleep(3)

print("B")
```

Kết quả

```
A
(chờ 3 giây)

B
```

Trong 3 giây đó Python làm gì?

Đáp án:

**Không làm gì cả.**

CPU gần như rảnh.

---

# 2. Blocking là gì?

**Blocking** nghĩa là

> Một thao tác khiến chương trình phải dừng lại và chờ cho đến khi thao tác đó hoàn thành.

Ví dụ

```
Đọc file

↓

Đợi

↓

Đọc xong

↓

Chạy tiếp
```

Hay

```
Download

↓

Đợi Server

↓

Có dữ liệu

↓

Tiếp tục
```

Hay

```
Truy vấn Database

↓

Đợi Database

↓

Có kết quả

↓

Tiếp tục
```

---

# Ví dụ 1

```python
import time

print("Start")

time.sleep(5)

print("End")
```

Timeline

```
0s   Start

1s   Waiting

2s   Waiting

3s   Waiting

4s   Waiting

5s   End
```

Trong 5 giây đó:

```
CPU

↓

Rảnh

↓

Python

↓

Đang chờ
```

Đó gọi là **Blocking**.

---

# Ví dụ 2

Đọc file lớn

```python
with open("movie.mp4", "rb") as f:
    data = f.read()
```

Nếu file 10GB

```
Open File

↓

Đọc

↓

Đợi

↓

Đọc

↓

Đợi

↓

Đọc xong
```

Chương trình không thể chạy dòng sau.

---

# Ví dụ 3

HTTP Request

```python
import requests

response = requests.get("https://example.com")
```

Quá trình

```
Python

↓

Gửi Request

↓

Đợi Internet

↓

Đợi Server

↓

Đợi Response

↓

Nhận dữ liệu
```

Nếu server mất 10 giây.

Python sẽ đứng yên 10 giây.

---

# Ví dụ 4

Database

```python
cursor.execute("SELECT * FROM users")
```

Python phải chờ:

```
Python

↓

Database

↓

Query

↓

Trả kết quả

↓

Python chạy tiếp
```

---

# 3. Vì sao Blocking gây vấn đề?

Giả sử có chương trình:

```python
print("Download")

download_file()

print("Update GUI")

print("Play Music")
```

Nếu download mất 30 giây

```
Download...

(30 giây)

Update GUI

Play Music
```

GUI bị treo.

Nhạc không phát.

Người dùng nghĩ chương trình bị lỗi.

---

# Ví dụ thực tế

Giả sử bạn dùng PySide6.

```python
def on_button_clicked():
    download_big_file()
```

Khi bấm nút

```
Click

↓

Download

↓

Đợi

↓

Đợi

↓

Đợi

↓

Xong
```

Trong lúc đó

* Không kéo được cửa sổ
* Không bấm được nút
* Không repaint
* Không animation

Đây là hiện tượng rất phổ biến với người mới học GUI.

---

# 4. CPU đang làm gì?

Giả sử server trả lời sau 5 giây.

```
Python

↓

Send Request

↓

Wait

↓

Wait

↓

Wait

↓

Receive
```

CPU

```
1%

↓

0%

↓

0%

↓

0%
```

CPU gần như không làm gì.

Vấn đề nằm ở **thời gian chờ (waiting)**.

---

# 5. I/O là gì?

I/O = **Input / Output**

Bao gồm mọi thao tác giao tiếp với thế giới bên ngoài.

Ví dụ:

```
Internet

Database

File

USB

Camera

Microphone

Keyboard

Socket

Bluetooth
```

Những thiết bị này đều chậm hơn CPU rất nhiều.

---

# So sánh tốc độ

| Thiết bị     |  Thời gian |
| ------------ | ---------: |
| CPU Register |    ~0.3 ns |
| RAM          |    ~100 ns |
| SSD          |    ~100 µs |
| HDD          |     ~10 ms |
| Internet     | ~10–300 ms |
| API chậm     |   vài giây |

CPU có thể thực hiện hàng triệu lệnh trong lúc chờ một phản hồi từ mạng.

---

# 6. Ví dụ "Đặt pizza"

Đây là ví dụ kinh điển để hiểu Blocking và Async.

## Blocking

Bạn đến quầy.

```
Đặt pizza

↓

Đứng chờ

↓

Đứng chờ

↓

Đứng chờ

↓

Lấy pizza
```

Bạn không làm việc gì khác.

---

## Non-blocking

```
Đặt pizza

↓

Nhận số thứ tự

↓

Đi mua nước

↓

Đi dạo

↓

Có chuông

↓

Lấy pizza
```

Trong thời gian chờ

Bạn vẫn làm được việc khác.

Đó chính là tư tưởng của **Asynchronous Programming**.

---

# 7. Non-blocking là gì?

Non-blocking nghĩa là:

> Không đứng chờ một thao tác hoàn thành nếu có thể làm việc khác trong lúc chờ.

Ví dụ

```
Download File A

↓

Đợi mạng

↓

Download File B

↓

Đợi mạng

↓

Download File C
```

Trong lúc File A đang chờ phản hồi, chương trình có thể xử lý File B hoặc File C thay vì "ngồi không".

---

# 8. Vì sao Async ra đời?

Giả sử cần tải 100 ảnh.

Nếu viết kiểu Blocking:

```python
for url in urls:
    download(url)
```

Timeline

```
Image1

↓

Image2

↓

Image3

↓

...

↓

Image100
```

Mỗi ảnh mất 1 giây.

Tổng thời gian khoảng:

```
100 giây
```

---

Nếu dùng Async:

```
Image1

Image2

Image3

Image4

...

Image100
```

Các yêu cầu được gửi gần như đồng thời.

Thời gian có thể chỉ còn khoảng:

```
1–3 giây
```

(Con số thực tế phụ thuộc vào mạng, máy chủ và giới hạn kết nối.)

Đây là lý do các ứng dụng tải nhiều dữ liệu từ Internet thường dùng lập trình bất đồng bộ.

---

# 9. Async KHÔNG làm CPU nhanh hơn

Đây là hiểu lầm phổ biến.

Async **không tăng tốc CPU**.

Nó chỉ tận dụng thời gian **CPU đang chờ I/O** để làm việc khác.

Ví dụ

```
CPU

↓

Làm việc

↓

Đợi mạng

↓

Làm việc khác

↓

Đợi Database

↓

Làm việc khác
```

Thay vì:

```
Làm

↓

Đợi

↓

Đợi

↓

Đợi

↓

Làm
```

---

# 10. Những bài toán phù hợp với Async

✔ Web crawler

✔ Download manager

✔ Chat server

✔ API server

✔ WebSocket

✔ Bot Telegram/Discord

✔ Bot Facebook

✔ Email sender

✔ Async Database

✔ Streaming

✔ PySide6 không treo giao diện

---

# 11. Những bài toán KHÔNG phù hợp

Ví dụ:

```python
for i in range(10_000_000_000):
    ...
```

Hoặc:

* AI
* Machine Learning
* Mã hóa (Encryption)
* Render video
* Xử lý ảnh
* Tính toán ma trận lớn

Đây là các bài toán **CPU-bound**, nơi thời gian chủ yếu dùng để tính toán chứ không phải chờ I/O. Async gần như không giúp tăng tốc; các giải pháp như đa tiến trình (multiprocessing) hoặc tối ưu thuật toán thường phù hợp hơn.

---

# 12. Tổng kết

## Những điều cần nhớ

* Python mặc định chạy tuần tự.
* Blocking khiến chương trình phải dừng để chờ.
* Phần lớn thao tác I/O (mạng, file, cơ sở dữ liệu...) đều là blocking nếu dùng API đồng bộ.
* CPU thường rảnh trong lúc chờ I/O.
* Async tận dụng khoảng thời gian chờ đó để xử lý công việc khác.
* Async đặc biệt hiệu quả với các ứng dụng có nhiều thao tác I/O.

---

# Sơ đồ tư duy

```text
Python Program
│
├── Sequential
│      │
│      └── Blocking
│
├── I/O
│      ├── File
│      ├── HTTP
│      ├── Database
│      ├── Socket
│      └── API
│
├── Waiting
│      │
│      └── CPU nhàn rỗi
│
└── Async
       │
       ├── Không đứng chờ
       ├── Làm việc khác khi chờ I/O
       └── Tăng khả năng xử lý đồng thời
```

---

# Bài tập thực hành

### Bài 1

Viết chương trình:

```python
print("Start")
time.sleep(5)
print("End")
```

Quan sát và ghi lại thời gian chương trình "đứng yên".

### Bài 2

Thay `time.sleep(5)` bằng `time.sleep(1)` trong vòng lặp:

```python
import time

for i in range(5):
    print(f"Lần {i}")
    time.sleep(1)
```

Quan sát khoảng cách giữa các lần in.

### Bài 3

Viết chương trình mô phỏng tải 3 tệp theo kiểu tuần tự:

```python
import time

def download(name):
    print(f"Bắt đầu tải {name}")
    time.sleep(2)
    print(f"Hoàn thành {name}")

download("file1")
download("file2")
download("file3")
```

Tính tổng thời gian thực thi và tự trả lời: **CPU thực sự bận trong bao lâu, và chờ trong bao lâu?**

---

Ở **Buổi 2**, chúng ta sẽ học chủ đề rất quan trọng: **Concurrency vs Parallelism**, bao gồm so sánh chi tiết giữa **Sequential Programming, Multithreading, Multiprocessing và Asyncio** bằng sơ đồ trực quan và các ví dụ thực tế. Đây là nền tảng để hiểu vì sao `asyncio` không phải là "đa luồng" nhưng vẫn có thể xử lý rất nhiều công việc cùng lúc.
