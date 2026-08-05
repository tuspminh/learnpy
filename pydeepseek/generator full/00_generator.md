Chào bạn! Tôi sẽ hướng dẫn bạn về **Iterator** và **Generator** trong Python một cách chuyên nghiệp và dễ hiểu nhất. Đây là hai khái niệm cực kỳ quan trọng để viết code Pythonic, tiết kiệm bộ nhớ và hiệu quả.

---

## PHẦN 1: ITERATOR (VÒNG LẶP)

### 1.1. Iterable vs Iterator - Phân biệt cơ bản

```python
# ITERABLE: object có thể lặp (có phương thức __iter__())
# Ví dụ: list, tuple, dict, set, string, file...

my_list = [1, 2, 3]  # Đây là iterable

# ITERATOR: object nhớ vị trí lặp (có __iter__() và __next__())
iterator = iter(my_list)  # Tạo iterator từ iterable

print(next(iterator))  # 1
print(next(iterator))  # 2
print(next(iterator))  # 3
# print(next(iterator))  # StopIteration - Hết phần tử
```

### 1.2. Cách hoạt động của vòng lặp for

```python
# Vòng lặp for thực chất hoạt động như sau:
my_list = [10, 20, 30]

# Cách Python thực hiện for loop:
iterator = iter(my_list)  # 1. Lấy iterator
while True:
    try:
        item = next(iterator)  # 2. Lấy phần tử tiếp theo
        print(item)            # 3. Xử lý
    except StopIteration:
        break                  # 4. Dừng khi hết
```

### 1.3. Tạo Custom Iterator (Iterator Class)

```python
class FibonacciIterator:
    """Iterator cho dãy Fibonacci"""
    def __init__(self, max_count):
        self.max_count = max_count
        self.current = 0
        self.next_num = 1
        self.count = 0
    
    def __iter__(self):
        return self  # Iterator phải trả về chính nó
    
    def __next__(self):
        if self.count >= self.max_count:
            raise StopIteration
        
        result = self.current
        self.current, self.next_num = self.next_num, self.current + self.next_num
        self.count += 1
        return result

# Sử dụng
fib = FibonacciIterator(10)
for num in fib:
    print(num, end=' ')  # 0 1 1 2 3 5 8 13 21 34
```

---

## PHẦN 2: GENERATOR (BỘ SINH)

Generator là cách đơn giản hơn để tạo iterator - **dùng `yield` thay vì `return`**.

### 2.1. Generator Function - Cơ bản

```python
def fibonacci_generator(max_count):
    """Tạo dãy Fibonacci - phiên bản generator"""
    a, b = 0, 1
    count = 0
    while count < max_count:
        yield a  # Tạm dừng và trả về giá trị
        a, b = b, a + b
        count += 1

# Sử dụng
fib_gen = fibonacci_generator(10)
for num in fib_gen:
    print(num, end=' ')  # 0 1 1 2 3 5 8 13 21 34

# Lấy từng giá trị một:
fib = fibonacci_generator(5)
print(next(fib))  # 0
print(next(fib))  # 1
print(next(fib))  # 1
```

### 2.2. Generator Expression (Biểu thức Generator)

```python
# List comprehension - Tạo list (tốn bộ nhớ)
squares_list = [x**2 for x in range(10)]  # Lưu hết 10 phần tử

# Generator expression - Tạo generator (tiết kiệm bộ nhớ)
squares_gen = (x**2 for x in range(10))   # Không lưu, tính khi cần

print(squares_gen)  # <generator object <genexpr> at 0x...>
print(next(squares_gen))  # 0
print(next(squares_gen))  # 1

# Ví dụ thực tế: Đọc file lớn
with open('large_file.txt') as f:
    # Generator expression để xử lý từng dòng
    lines = (line.strip() for line in f if line.strip())
    for line in lines:
        process(line)  # Xử lý từng dòng, không load cả file
```

---

## PHẦN 3: SO SÁNH - KHI NÀO DÙNG GÌ?

### 3.1. Bảng so sánh chi tiết

```python
import sys
import time

# 1. List (Eager Evaluation - Tính ngay)
def get_squares_list(n):
    return [i**2 for i in range(n)]

# 2. Generator (Lazy Evaluation - Tính khi cần)
def get_squares_gen(n):
    for i in range(n):
        yield i**2

# So sánh bộ nhớ
n = 1000000
list_result = get_squares_list(n)
gen_result = get_squares_gen(n)

print(f"List memory: {sys.getsizeof(list_result)} bytes")  # ~8MB
print(f"Generator memory: {sys.getsizeof(gen_result)} bytes")  # ~112 bytes
```

### 3.2. Khi nào dùng cái nào?

```python
# DÙNG LIST KHI:
# - Cần truy cập ngẫu nhiên (indexing, slicing)
# - Cần lặp lại nhiều lần
# - Dữ liệu nhỏ

# DÙNG GENERATOR KHI:
# - Dữ liệu lớn (streaming data, file lớn)
# - Chỉ cần lặp 1 lần
# - Tiết kiệm bộ nhớ là ưu tiên

# Ví dụ thực tế:
def read_large_log(file_path):
    """Đọc log file lớn - dùng generator"""
    with open(file_path, 'r') as f:
        for line in f:
            if 'ERROR' in line:
                yield line.strip()

# Xử lý từng dòng lỗi - không load cả file
for error_line in read_large_log('app.log'):
    print(f"Found error: {error_line}")
```

---

## PHẦN 4: KỸ THUẬT NÂNG CAO VỚI GENERATOR

### 4.1. yield from - Ủy quyền cho sub-generator

```python
def sub_generator():
    yield 1
    yield 2
    yield 3

def main_generator():
    yield 'Start'
    yield from sub_generator()  # Ủy quyền
    yield 'End'

for val in main_generator():
    print(val)  # Start, 1, 2, 3, End

# Ví dụ thực tế: flatten nested list
def flatten(nested_list):
    for sublist in nested_list:
        yield from sublist  # yield từng phần tử của sublist

nested = [[1, 2], [3, 4, 5], [6]]
for item in flatten(nested):
    print(item, end=' ')  # 1 2 3 4 5 6
```

### 4.2. Generator với send() - Two-way communication

```python
def accumulator():
    """Generator nhận giá trị và tính tổng"""
    total = 0
    while True:
        value = yield total  # Nhận giá trị từ send()
        if value is None:
            break
        total += value

# Sử dụng
acc = accumulator()
next(acc)  # Khởi tạo (bắt buộc)

print(acc.send(10))  # 10
print(acc.send(20))  # 30
print(acc.send(30))  # 60
acc.close()  # Đóng generator

# Ví dụ thực tế: Data pipeline
def data_processor():
    """Xử lý data stream"""
    data = []
    while True:
        item = yield
        if item == 'END':
            break
        processed = item.upper().strip()
        data.append(processed)
    yield data  # Trả về kết quả cuối cùng

processor = data_processor()
next(processor)  # Khởi tạo

processor.send('hello')
processor.send(' world ')
processor.send('python')
result = processor.send('END')
print(result)  # ['HELLO', 'WORLD', 'PYTHON']
```

### 4.3. Generator với throw() - Xử lý exception

```python
def safe_division():
    """Generator xử lý chia với error handling"""
    while True:
        try:
            a, b = yield
            result = a / b
            yield result
        except ZeroDivisionError:
            yield "Cannot divide by zero!"

div_gen = safe_division()
next(div_gen)  # Khởi tạo

print(div_gen.send((10, 2)))   # 5.0
print(div_gen.send((10, 0)))   # Cannot divide by zero!
print(div_gen.send((20, 4)))   # 5.0
```

---

## PHẦN 5: ỨNG DỤNG THỰC TẾ

### 5.1. Đọc file CSV lớn

```python
import csv

def read_large_csv(file_path, chunk_size=1000):
    """Đọc CSV lớn theo từng chunk"""
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        chunk = []
        for row in reader:
            chunk.append(row)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk

# Xử lý 1000 dòng một lần
for chunk in read_large_csv('huge_data.csv'):
    process_chunk(chunk)  # Không tốn bộ nhớ
```

### 5.2. Pipeline xử lý dữ liệu

```python
def read_data():
    """Đọc dữ liệu từ nguồn"""
    for i in range(1000000):
        yield i

def filter_even(data):
    """Lọc số chẵn"""
    for num in data:
        if num % 2 == 0:
            yield num

def square(data):
    """Bình phương"""
    for num in data:
        yield num ** 2

def sum_pipeline(data):
    """Tính tổng"""
    total = 0
    for num in data:
        total += num
        yield total

# Xây dựng pipeline - cực kỳ hiệu quả
pipeline = sum_pipeline(
    square(
        filter_even(
            read_data()
        )
    )
)

# Lấy kết quả từng bước, không lưu gì cả
for result in pipeline:
    if result > 1000:
        print(f"First sum > 1000: {result}")
        break
```

### 5.3. Infinite sequences (Vô hạn)

```python
def infinite_primes():
    """Sinh số nguyên tố vô hạn"""
    primes = []
    num = 2
    while True:
        is_prime = True
        for p in primes:
            if p * p > num:
                break
            if num % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
            yield num
        num += 1

# Lấy 10 số nguyên tố đầu tiên
primes = infinite_primes()
first_10 = [next(primes) for _ in range(10)]
print(first_10)  # [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

---

## PHẦN 6: MẸO VÀ THỰC HÀNH TỐT

### 6.1. Lazy Evaluation Tips

```python
# ❌ Xấu: Tạo list không cần thiết
def get_errors(logs):
    return [line for line in logs if 'ERROR' in line]

for error in get_errors(big_logs):  # Tốn bộ nhớ
    process(error)

# ✅ Tốt: Dùng generator
def get_errors(logs):
    for line in logs:
        if 'ERROR' in line:
            yield line

for error in get_errors(big_logs):  # Streaming
    process(error)
```

### 6.2. Kiểm tra Generator có rỗng không?

```python
# ⚠️ Không kiểm tra trực tiếp được
def is_empty(gen):
    """Kiểm tra generator rỗng - sẽ tiêu tốn 1 phần tử"""
    try:
        first = next(gen)
        # Tạo generator mới với phần tử đã lấy
        def new_gen():
            yield first
            yield from gen
        return new_gen(), False
    except StopIteration:
        return iter([]), True

# Sử dụng
gen = (x for x in range(5))
new_gen, empty = is_empty(gen)
if not empty:
    for item in new_gen:
        print(item)
```

### 6.3. Context Manager với Generator

```python
from contextlib import contextmanager

@contextmanager
def managed_resource(*args, **kwargs):
    """Quản lý resource với generator"""
    resource = acquire_resource(*args, **kwargs)
    try:
        yield resource
    finally:
        release_resource(resource)

# Sử dụng
with managed_resource('db', 'user', 'pass') as db:
    db.query("SELECT * FROM users")
```

---

## BÀI TẬP THỰC HÀNH

### Bài 1: Generator for Pagination

```python
# TODO: Viết generator để phân trang dữ liệu
def paginate(data, page_size):
    # Yêu cầu: yield từng page, mỗi page là list có page_size phần tử
    pass

# Test:
data = list(range(100))
for page in paginate(data, 10):
    print(f"Page: {page[:3]}...")  # Hiển thị 3 phần tử đầu
```

### Bài 2: Chain Generator

```python
# TODO: Viết chain generator nối nhiều iterable
def chain(*iterables):
    # Yêu cầu: yield từng phần tử từ iterable đầu tiên, rồi đến iterable tiếp theo
    pass

# Test:
for item in chain([1, 2], 'abc', (10, 20)):
    print(item, end=' ')  # 1 2 a b c 10 20
```

### Bài 3: Generator với send()

```python
# TODO: Tạo calculator với generator
def calculator():
    # Nhận: phép toán (+,-,*,/) và 2 số
    # Trả về kết quả
    pass

calc = calculator()
next(calc)
print(calc.send(('+', 5, 3)))  # 8
print(calc.send(('*', 4, 7)))  # 28
```

---

## TÓM TẮT NHANH

| Đặc điểm | Iterator | Generator |
|----------|----------|-----------|
| Tạo bằng | Class với `__iter__`, `__next__` | Hàm với `yield` |
| Bộ nhớ | Có thể tốn nếu lưu hết | Rất ít (lazy) |
| Độ phức tạp | Cao | Thấp |
| Reuse | Có thể (nếu tạo mới) | Không (1 lần) |
| Ứng dụng | Custom iteration logic | Data streaming, pipelines |

**Nguyên tắc vàng**: 
- Dùng **Generator** nếu có thể - đơn giản hơn, hiệu quả hơn
- Dùng **Custom Iterator** khi cần logic lặp phức tạp
- Luôn nghĩ về **Lazy Evaluation** để tối ưu memory

Chúc bạn thành công! Hãy thực hành nhiều để thành thạo nhé! 🚀