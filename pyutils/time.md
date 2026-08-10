Đơn vị đo thời gian chuẩn trong các module gốc của Python (như time, timeit, datetime) mặc định luôn là giây (seconds). [1, 2] 
Khi bạn sử dụng các hàm hệ thống, kết quả trả về thường là một số thực (float), cho phép bạn đo chính xác đến các đơn vị nhỏ hơn nhờ phần thập phân. [2, 3] 
## Cách quy đổi sang các đơn vị khác
Nếu bạn cần hiển thị thời gian ở các đơn vị nhỏ hơn giây, hãy thực hiện phép nhân toán học từ giá trị giây ban đầu: [2] 

* 
* Mili giây (ms): Nhân kết quả với 10³ (1 giây = 1.000 ms).
* Micro giây (μs): Nhân kết quả với 10⁶ ($1\text{ giây} = 1.000.000\text{ }\mu\text{s}$).
* Nano giây (ns): Nhân kết quả với 10⁹ ($1\text{ giây} = 1.000.000.000\text{ ns}$). Python cũng cung cấp sẵn các hàm trả về số nguyên hệ nano giây như time.perf_counter_ns() hoặc time.time_ns(). [1, 2] 
* 

## Các thư viện đo thời gian phổ biến## 1. Thư viện time (Đo khoảng thời gian, hiệu năng mã)
Thư viện time cung cấp các công cụ để ghi lại các mốc thời gian thực tế hoặc thời gian chạy của CPU. [4, 5] 

* 
* time.time(): Trả về số giây đã trôi qua tính từ mốc Epoch (00:00:00 UTC ngày 1/1/1970).
* time.perf_counter(): Trả về số giây từ một mốc không xác định của hệ thống. Đây là hàm có độ chính xác cao nhất để đo thời gian chạy của một đoạn code. [2, 3, 4, 6, 7] 
* 

import time
# Đo thời gian bằng giâystart = time.perf_counter()# Đoạn mã cần kiểm tra hiệu năng nằm ở đâyend = time.perf_counter()
elapsed_seconds = end - start
print(f"Thời gian chạy: {elapsed_seconds} giây")
print(f"Thời gian chạy: {elapsed_seconds * 1000:.2f} mili giây")

## 2. Thư viện datetime (Quản lý lịch, ngày, giờ)
Thư viện datetime dùng để xử lý mốc thời gian thực tế. Khi tính toán khoảng chênh lệch giữa hai mốc ngày giờ, Python trả về đối tượng timedelta. Mặc định timedelta lưu trữ ba đơn vị là: ngày (days), giây (seconds), và micro giây (microseconds). [5, 8, 9] 

from datetime import datetime
start_time = datetime.now()# Thực hiện tác vụend_time = datetime.now()
duration = end_time - start_time
print(f"Số giây chênh lệch: {duration.total_seconds()} giây")

## 3. Thư viện timeit (Đo hiệu năng chuẩn xác cao)
Đối với các bài kiểm tra hiệu năng (benchmark) các đoạn mã ngắn, thư viện timeit là lựa chọn tốt nhất. Nó sẽ lặp lại đoạn mã nhiều lần và trả về tổng thời gian thực thi tính bằng giây. [1, 4, 7] 
Bạn đang cần đo thời gian để tính toán khoảng chênh lệch lịch trình (như ngày/tháng/năm) hay để đo tốc độ chạy của một hàm code cụ thể? Hãy chia sẻ mục đích để tôi hướng dẫn đoạn mã phù hợp nhất!

[1] [https://pynative.com](https://translate.google.com/translate?u=https://pynative.com/python-get-execution-time-of-program/&hl=vi&sl=en&tl=vi&client=sge)
[2] [https://www.geeksforgeeks.org](https://translate.google.com/translate?u=https://www.geeksforgeeks.org/python/how-to-measure-elapsed-time-in-python/&hl=vi&sl=en&tl=vi&client=sge)
[3] [https://topdev.vn](https://topdev.vn/blog/date-time-trong-python/)
[4] [https://stackoverflow.com](https://translate.google.com/translate?u=https://stackoverflow.com/questions/14452145/how-to-measure-time-taken-between-lines-of-code-in-python&hl=vi&sl=en&tl=vi&client=sge)
[5] [https://www.tranvanbinh.vn](https://www.tranvanbinh.vn/2025/07/bai-12-xu-ly-thoi-gian-trong-python.html)
[6] [https://realpython.com](https://translate.google.com/translate?u=https://realpython.com/python-timer/&hl=vi&sl=en&tl=vi&client=sge)
[7] [https://builtin.com](https://translate.google.com/translate?u=https://builtin.com/articles/timing-functions-python&hl=vi&sl=en&tl=vi&client=sge)
[8] [https://numpy.org](https://translate.google.com/translate?u=https://numpy.org/devdocs/reference/arrays.datetime.html&hl=vi&sl=en&tl=vi&client=sge)
[9] [https://mimo.org](https://translate.google.com/translate?u=https://mimo.org/glossary/python/datetime&hl=vi&sl=en&tl=vi&client=sge)
