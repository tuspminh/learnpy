Để đo tốc độ chạy của một hàm trong Python, bạn có thể dùng time.perf_counter() (cho các hàm xử lý dài, phức tạp) hoặc thư viện timeit (cho các hàm xử lý siêu nhanh, cần đo độ chính xác cao).
Dưới đây là 3 cách phổ biến từ cơ bản đến chuyên nghiệp.
## Cách 1: Dùng time.perf_counter() (Dễ dùng nhất)
Cách này phù hợp để đo các hàm chạy mất từ vài mili giây đến vài giây. Hàm perf_counter() sử dụng đồng hồ có độ chính xác cao nhất của hệ thống.

import time
def my_function():
    # Giả lập một hàm tốn thời gian xử lý
    total = 0
    for i in range(10_000_000):
        total += i
    return total
# 1. Ghi lại thời gian bắt đầustart_time = time.perf_counter()
# 2. Chạy hàm cần đo
my_function()
# 3. Ghi lại thời gian kết thúcend_time = time.perf_counter()
# 4. Tính toán kết quảexecution_time = end_time - start_time
print(f"Hàm chạy hết: {execution_time:.6f} giây")
print(f"Hàm chạy hết: {execution_time * 1000:.2f} mili giây")

## Cách 2: Dùng timeit (Chính xác nhất cho hàm siêu nhanh)
Nếu hàm của bạn chạy quá nhanh (dưới 1 mili giây), việc đo 1 lần duy nhất sẽ bị sai số lớn do hệ điều hành gây ra. Thư viện timeit giải quyết việc này bằng cách cho hàm chạy lặp lại nhiều lần (ví dụ: 10.000 lần) rồi tính tổng hoặc trung bình thời gian.

import timeit
def my_fast_function():
    return [i for i in range(1000)]
# Đo thời gian chạy của hàm my_fast_function 10.000 lần# Hàm lambda giúp truyền hàm vào timeit một cách dễ dàngtotal_time = timeit.timeit(lambda: my_fast_function(), number=10_000)

print(f"Tổng thời gian chạy 10.000 lần: {total_time:.4f} giây")
print(f"Thời gian trung bình 1 lần chạy: {total_time / 10_000 * 1000:.6f} mili giây")

## Cách 3: Dùng Decorator (Chuyên nghiệp, tái sử dụng cao)
Nếu bạn có rất nhiều hàm cần đo tốc độ trong dự án, hãy tạo một decorator. Bạn chỉ cần thêm chữ @time_it lên phía trên bất kỳ hàm nào muốn đo.

import time
# Định nghĩa decorator đo thời giandef time_it(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs) # Chạy hàm gốc
        end = time.perf_counter()
        print(f"--- Hàm [{func.__name__}] chạy mất: {(end - start) * 1000:.4f} ms ---")
        return result
    return wrapper
# Sử dụng decorator cho các hàm của bạn
@time_itdef process_data(n):
    return sum(i * i for i in range(n))
# Gọi hàm bình thường, tốc độ sẽ tự động in ra màn hình
process_data(5_000_000)

Nếu bạn đang dùng công cụ nào khác như Jupyter Notebook, tôi có thể hướng dẫn bạn cách dùng lệnh phép thuật %%time hoặc %%timeit để đo siêu nhanh mà không cần viết code. Bạn có muốn tìm hiểu thêm về cách đo trên Jupyter Notebook hay cách truyền tham số vào hàm khi đo không?

