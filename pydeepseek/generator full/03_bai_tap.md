Tôi sẽ tạo cho bạn **30 bài tập** từ cơ bản đến nâng cao về iterable, iterator và generator. Mỗi bài đều có mục tiêu rõ ràng và đáp án để bạn kiểm tra.

---

## 📘 PHẦN 1: CƠ BẢN VỀ ITERABLE (Bài 1-8)

### Bài 1: Kiểm tra Iterable
```python
# Viết hàm kiểm tra một object có phải là iterable không
def is_iterable(obj):
    # Your code here
    pass

# Test
print(is_iterable([1, 2, 3]))  # True
print(is_iterable(123))        # False
print(is_iterable("hello"))    # True
print(is_iterable((1, 2)))     # True
```

<details>
<summary>Đáp án</summary>

```python
def is_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False
```
</details>

---

### Bài 2: Đếm số phần tử trong iterable
```python
# Không dùng len(), hãy đếm số phần tử trong iterable
def count_items(iterable):
    # Your code here
    pass

# Test
print(count_items([1, 2, 3, 4, 5]))     # 5
print(count_items(range(10)))            # 10
print(count_items("hello world"))        # 11
```

<details>
<summary>Đáp án</summary>

```python
def count_items(iterable):
    count = 0
    for item in iterable:
        count += 1
    return count
```
</details>

---

### Bài 3: Lấy phần tử cuối cùng
```python
# Lấy phần tử cuối cùng của iterable mà không chuyển thành list
def last_item(iterable):
    # Your code here
    pass

# Test
print(last_item([1, 2, 3, 4, 5]))        # 5
print(last_item(range(100)))             # 99
print(last_item("python"))               # 'n'
```

<details>
<summary>Đáp án</summary>

```python
def last_item(iterable):
    last = None
    for item in iterable:
        last = item
    return last
```
</details>

---

### Bài 4: Kiểm tra iterable rỗng
```python
# Kiểm tra iterable có rỗng không (không dùng len)
def is_empty(iterable):
    # Your code here
    pass

# Test
print(is_empty([]))          # True
print(is_empty([1, 2]))      # False
print(is_empty(range(0)))    # True
print(is_empty(""))          # True
```

<details>
<summary>Đáp án</summary>

```python
def is_empty(iterable):
    try:
        next(iter(iterable))
        return False
    except StopIteration:
        return True
```
</details>

---

### Bài 5: Lấy n phần tử đầu tiên
```python
# Lấy n phần tử đầu tiên từ iterable
def take_n(iterable, n):
    # Your code here
    pass

# Test
print(list(take_n([1, 2, 3, 4, 5], 3)))      # [1, 2, 3]
print(list(take_n(range(10), 5)))             # [0, 1, 2, 3, 4]
print(list(take_n("abcdef", 2)))              # ['a', 'b']
```

<details>
<summary>Đáp án</summary>

```python
def take_n(iterable, n):
    iterator = iter(iterable)
    result = []
    for _ in range(n):
        try:
            result.append(next(iterator))
        except StopIteration:
            break
    return result
```
</details>

---

### Bài 6: Bỏ qua n phần tử đầu
```python
# Bỏ qua n phần tử đầu và trả về iterable mới
def skip_n(iterable, n):
    # Your code here
    pass

# Test
print(list(skip_n([1, 2, 3, 4, 5], 2)))     # [3, 4, 5]
print(list(skip_n(range(10), 7)))           # [7, 8, 9]
print(list(skip_n("hello", 3)))             # ['l', 'o']
```

<details>
<summary>Đáp án</summary>

```python
def skip_n(iterable, n):
    iterator = iter(iterable)
    for _ in range(n):
        try:
            next(iterator)
        except StopIteration:
            break
    for item in iterator:
        yield item
```
</details>

---

### Bài 7: Chia iterable thành các chunk
```python
# Chia iterable thành các chunk có kích thước n
def chunked(iterable, n):
    # Your code here
    pass

# Test
for chunk in chunked([1, 2, 3, 4, 5, 6, 7], 3):
    print(chunk)  # [1, 2, 3], [4, 5, 6], [7]
```

<details>
<summary>Đáp án</summary>

```python
def chunked(iterable, n):
    iterator = iter(iterable)
    while True:
        chunk = []
        for _ in range(n):
            try:
                chunk.append(next(iterator))
            except StopIteration:
                if chunk:
                    yield chunk
                return
        yield chunk
```
</details>

---

### Bài 8: Interleave nhiều iterable
```python
# Trộn các iterable với nhau (lấy lần lượt từ mỗi iterable)
def interleave(*iterables):
    # Your code here
    pass

# Test
print(list(interleave([1, 2, 3], ['a', 'b', 'c'])))  
# [1, 'a', 2, 'b', 3, 'c']
```

<details>
<summary>Đáp án</summary>

```python
def interleave(*iterables):
    iterators = [iter(it) for it in iterables]
    while True:
        for iterator in iterators:
            try:
                yield next(iterator)
            except StopIteration:
                return
```
</details>

---

## 📗 PHẦN 2: CUSTOM ITERATOR (Bài 9-14)

### Bài 9: Custom Iterator - Đếm ngược
```python
# Tạo iterator đếm ngược từ n về 0
class Countdown:
    def __init__(self, n):
        # Your code here
        pass
    
    def __iter__(self):
        # Your code here
        pass
    
    def __next__(self):
        # Your code here
        pass

# Test
for num in Countdown(5):
    print(num, end=' ')  # 5 4 3 2 1 0
```

<details>
<summary>Đáp án</summary>

```python
class Countdown:
    def __init__(self, n):
        self.n = n
        self.current = n
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current < 0:
            raise StopIteration
        result = self.current
        self.current -= 1
        return result
```
</details>

---

### Bài 10: Custom Iterator - Dãy số chẵn
```python
# Tạo iterator cho dãy số chẵn từ 0 đến n
class EvenNumbers:
    # Your code here
    pass

# Test
for num in EvenNumbers(10):
    print(num, end=' ')  # 0 2 4 6 8 10
```

<details>
<summary>Đáp án</summary>

```python
class EvenNumbers:
    def __init__(self, limit):
        self.limit = limit
        self.current = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current > self.limit:
            raise StopIteration
        result = self.current
        self.current += 2
        return result
```
</details>

---

### Bài 11: Custom Iterator - Lũy thừa
```python
# Tạo iterator cho dãy lũy thừa: n^0, n^1, n^2, ... đến khi > limit
class PowersOf:
    # Your code here
    pass

# Test
for num in PowersOf(2, 100):
    print(num, end=' ')  # 1 2 4 8 16 32 64
```

<details>
<summary>Đáp án</summary>

```python
class PowersOf:
    def __init__(self, base, limit):
        self.base = base
        self.limit = limit
        self.exponent = 0
        self.current = 1
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current > self.limit:
            raise StopIteration
        result = self.current
        self.exponent += 1
        self.current = self.base ** self.exponent
        return result
```
</details>

---

### Bài 12: Custom Iterator - Vô hạn
```python
# Tạo iterator vô hạn: lặp lại danh sách
class Cycle:
    # Your code here
    pass

# Test
cycle = Cycle([1, 2, 3])
for i in range(10):
    print(next(cycle), end=' ')  # 1 2 3 1 2 3 1 2 3 1
```

<details>
<summary>Đáp án</summary>

```python
class Cycle:
    def __init__(self, items):
        self.items = items
        self.index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if not self.items:
            raise StopIteration
        result = self.items[self.index]
        self.index = (self.index + 1) % len(self.items)
        return result
```
</details>

---

### Bài 13: Custom Iterator - Fibonacci vô hạn
```python
# Tạo iterator vô hạn cho dãy Fibonacci
class InfiniteFibonacci:
    # Your code here
    pass

# Test
fib = InfiniteFibonacci()
for _ in range(10):
    print(next(fib), end=' ')  # 0 1 1 2 3 5 8 13 21 34
```

<details>
<summary>Đáp án</summary>

```python
class InfiniteFibonacci:
    def __init__(self):
        self.a, self.b = 0, 1
    
    def __iter__(self):
        return self
    
    def __next__(self):
        result = self.a
        self.a, self.b = self.b, self.a + self.b
        return result
```
</details>

---

### Bài 14: Custom Iterator - Prime Numbers
```python
# Tạo iterator cho số nguyên tố (có giới hạn)
class PrimeNumbers:
    # Your code here
    pass

# Test
for prime in PrimeNumbers(20):
    print(prime, end=' ')  # 2 3 5 7 11 13 17 19
```

<details>
<summary>Đáp án</summary>

```python
class PrimeNumbers:
    def __init__(self, limit):
        self.limit = limit
        self.current = 1
    
    def __iter__(self):
        return self
    
    def _is_prime(self, n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    def __next__(self):
        self.current += 1
        while self.current <= self.limit:
            if self._is_prime(self.current):
                return self.current
            self.current += 1
        raise StopIteration
```
</details>

---

## 📙 PHẦN 3: GENERATOR CƠ BẢN (Bài 15-22)

### Bài 15: Generator - Bình phương
```python
# Tạo generator trả về bình phương của các số từ 0 đến n
def squares(n):
    # Your code here
    pass

# Test
for num in squares(5):
    print(num, end=' ')  # 0 1 4 9 16 25
```

<details>
<summary>Đáp án</summary>

```python
def squares(n):
    for i in range(n + 1):
        yield i ** 2
```
</details>

---

### Bài 16: Generator - Bảng cửu chương
```python
# Tạo generator trả về bảng cửu chương của một số
def multiplication_table(num, max_multiplier=10):
    # Your code here
    pass

# Test
for result in multiplication_table(5):
    print(result, end=' ')  # 5 10 15 20 25 30 35 40 45 50
```

<details>
<summary>Đáp án</summary>

```python
def multiplication_table(num, max_multiplier=10):
    for i in range(1, max_multiplier + 1):
        yield num * i
```
</details>

---

### Bài 17: Generator - Dãy số lẻ
```python
# Tạo generator cho dãy số lẻ từ start đến end
def odd_numbers(start, end):
    # Your code here
    pass

# Test
print(list(odd_numbers(1, 20)))  # [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
```

<details>
<summary>Đáp án</summary>

```python
def odd_numbers(start, end):
    if start % 2 == 0:
        start += 1
    for i in range(start, end + 1, 2):
        yield i
```
</details>

---

### Bài 18: Generator - Đọc file từng dòng
```python
# Tạo generator đọc file và trả về từng dòng đã strip
def read_lines(file_path):
    # Your code here
    pass

# Test (tạo file tạm)
with open('test.txt', 'w') as f:
    f.write('line1\nline2\nline3\n')
    
for line in read_lines('test.txt'):
    print(line)  # line1, line2, line3
```

<details>
<summary>Đáp án</summary>

```python
def read_lines(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            yield line.strip()
```
</details>

---

### Bài 19: Generator - Lọc số chẵn
```python
# Tạo generator chỉ yield số chẵn từ iterable
def filter_even(iterable):
    # Your code here
    pass

# Test
print(list(filter_even([1, 2, 3, 4, 5, 6, 7, 8])))  # [2, 4, 6, 8]
```

<details>
<summary>Đáp án</summary>

```python
def filter_even(iterable):
    for item in iterable:
        if item % 2 == 0:
            yield item
```
</details>

---

### Bài 20: Generator - Map function
```python
# Tạo generator áp dụng function lên từng phần tử
def map_generator(func, iterable):
    # Your code here
    pass

# Test
print(list(map_generator(lambda x: x**2, [1, 2, 3, 4])))  # [1, 4, 9, 16]
```

<details>
<summary>Đáp án</summary>

```python
def map_generator(func, iterable):
    for item in iterable:
        yield func(item)
```
</details>

---

### Bài 21: Generator - Unique values
```python
# Tạo generator chỉ yield giá trị duy nhất (loại bỏ trùng lặp)
def unique(iterable):
    # Your code here
    pass

# Test
print(list(unique([1, 2, 2, 3, 3, 3, 4, 1, 5])))  # [1, 2, 3, 4, 5]
```

<details>
<summary>Đáp án</summary>

```python
def unique(iterable):
    seen = set()
    for item in iterable:
        if item not in seen:
            seen.add(item)
            yield item
```
</details>

---

### Bài 22: Generator - Zip với padding
```python
# Tạo generator zip các iterable, nếu ngắn hơn thì dùng default value
def zip_with_padding(default, *iterables):
    # Your code here
    pass

# Test
print(list(zip_with_padding('x', [1, 2], [3, 4, 5], [6])))
# [(1, 3, 6), (2, 4, 'x'), ('x', 5, 'x')]
```

<details>
<summary>Đáp án</summary>

```python
def zip_with_padding(default, *iterables):
    iterators = [iter(it) for it in iterables]
    while True:
        result = []
        has_item = False
        for iterator in iterators:
            try:
                result.append(next(iterator))
                has_item = True
            except StopIteration:
                result.append(default)
        if not has_item:
            break
        yield tuple(result)
```
</details>

---

## 📕 PHẦN 4: NÂNG CAO (Bài 23-30)

### Bài 23: Generator Pipeline
```python
# Tạo pipeline: đọc số, lọc số chẵn, bình phương, lấy tổng tích lũy
def number_pipeline(numbers):
    # Your code here
    # Gợi ý: yield từng bước
    pass

# Test
for result in number_pipeline([1, 2, 3, 4, 5]):
    print(result, end=' ')  # 4, 20, 52 (tích lũy bình phương số chẵn)
```

<details>
<summary>Đáp án</summary>

```python
def number_pipeline(numbers):
    total = 0
    for num in numbers:
        if num % 2 == 0:
            total += num ** 2
            yield total
```
</details>

---

### Bài 24: Generator với send()
```python
# Tạo generator nhận giá trị và trả về trung bình cộng tích lũy
def running_average():
    # Your code here
    pass

# Test
avg = running_average()
next(avg)
print(avg.send(10))  # 10.0
print(avg.send(20))  # 15.0
print(avg.send(30))  # 20.0
```

<details>
<summary>Đáp án</summary>

```python
def running_average():
    total = 0
    count = 0
    while True:
        value = yield
        total += value
        count += 1
        yield total / count
```
</details>

---

### Bài 25: Generator - Batch processing
```python
# Tạo generator xử lý theo batch, áp dụng function cho mỗi batch
def batch_processor(iterable, batch_size, processor):
    # Your code here
    pass

# Test
def sum_batch(batch):
    return sum(batch)

for result in batch_processor(range(10), 3, sum_batch):
    print(result, end=' ')  # 3, 12, 21, 9
```

<details>
<summary>Đáp án</summary>

```python
def batch_processor(iterable, batch_size, processor):
    iterator = iter(iterable)
    while True:
        batch = []
        for _ in range(batch_size):
            try:
                batch.append(next(iterator))
            except StopIteration:
                if batch:
                    yield processor(batch)
                return
        yield processor(batch)
```
</details>

---

### Bài 26: Generator - Flatten nested
```python
# Tạo generator làm phẳng nested structure
def flatten_deep(nested):
    # Your code here
    pass

# Test
nested = [1, [2, 3], [4, [5, 6]], 7]
print(list(flatten_deep(nested)))  # [1, 2, 3, 4, 5, 6, 7]
```

<details>
<summary>Đáp án</summary>

```python
def flatten_deep(nested):
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten_deep(item)
        else:
            yield item
```
</details>

---

### Bài 27: Generator - Window sliding
```python
# Tạo generator trượt cửa sổ kích thước n
def sliding_window(iterable, n):
    # Your code here
    pass

# Test
for window in sliding_window([1, 2, 3, 4, 5], 3):
    print(window, end=' ')  # [1, 2, 3], [2, 3, 4], [3, 4, 5]
```

<details>
<summary>Đáp án</summary>

```python
def sliding_window(iterable, n):
    items = list(iterable)
    for i in range(len(items) - n + 1):
        yield items[i:i+n]
```
</details>

---

### Bài 28: Generator - Merge sorted iterables
```python
# Tạo generator merge các iterable đã được sort
def merge_sorted(*iterables):
    # Your code here
    pass

# Test
print(list(merge_sorted([1, 3, 5], [2, 4, 6], [0, 7, 8])))
# [0, 1, 2, 3, 4, 5, 6, 7, 8]
```

<details>
<summary>Đáp án</summary>

```python
import heapq

def merge_sorted(*iterables):
    heap = []
    iterators = [iter(it) for it in iterables]
    
    for i, iterator in enumerate(iterators):
        try:
            heap.append((next(iterator), i))
        except StopIteration:
            pass
    
    heapq.heapify(heap)
    
    while heap:
        value, idx = heapq.heappop(heap)
        yield value
        try:
            heapq.heappush(heap, (next(iterators[idx]), idx))
        except StopIteration:
            pass
```
</details>

---

### Bài 29: Generator - với context manager
```python
# Tạo generator làm context manager để đo thời gian
import time
from contextlib import contextmanager

@contextmanager
def timer():
    # Your code here
    pass

# Test
with timer() as t:
    time.sleep(1)
    print(f"Elapsed: {t()}")  # Elapsed: ~1.0
```

<details>
<summary>Đáp án</summary>

```python
import time
from contextlib import contextmanager

@contextmanager
def timer():
    start = time.time()
    yield lambda: time.time() - start
```
</details>

---

### Bài 30: Generator - Infinite data stream
```python
# Tạo generator mô phỏng data stream vô hạn
# Cứ mỗi lần gọi, trả về 1 giá trị ngẫu nhiên, 
# nhưng có thể dừng khi gặp giá trị > 0.95
import random

def data_stream():
    # Your code here
    pass

# Test
stream = data_stream()
for i, value in enumerate(stream):
    print(f"{i}: {value:.3f}")
    if i >= 20:  # Giới hạn để test
        break
```

<details>
<summary>Đáp án</summary>

```python
import random

def data_stream():
    while True:
        value = random.random()
        if value > 0.95:
            yield value
            break
        yield value
```
</details>

---

## 🎯 BONUS: Bài tập tổng hợp

### Mini Project: Log Processor
```python
"""
Tạo hệ thống xử lý log với:
1. Đọc log từ file (generator)
2. Lọc log theo level (INFO, WARNING, ERROR)
3. Parse timestamp, message
4. Thống kê số lượng theo level
5. Tìm log theo keyword
"""

def log_reader(file_path):
    # TODO: Đọc log từ file
    pass

def filter_by_level(logs, level):
    # TODO: Lọc log theo level
    pass

def parse_log(log_line):
    # TODO: Parse log line thành dict
    pass

def search_logs(logs, keyword):
    # TODO: Tìm log chứa keyword
    pass

def stats_by_level(logs):
    # TODO: Thống kê số lượng theo level
    pass

# Test với dữ liệu mẫu
sample_logs = """
2024-01-01 10:00:00 INFO User logged in
2024-01-01 10:01:00 ERROR Database connection failed
2024-01-01 10:02:00 WARNING Disk space low
2024-01-01 10:03:00 INFO File uploaded
2024-01-01 10:04:00 ERROR Timeout error
"""

# Viết code xử lý ở đây
```

---

## 💡 Hướng dẫn học tập

1. **Mức độ**: Làm từ bài 1-8 → 9-14 → 15-22 → 23-30
2. **Thực hành**: Mỗi bài không xem đáp án trước, tự code ít nhất 15 phút
3. **Mở rộng**: Sau mỗi bài, thử viết thêm test cases khác
4. **So sánh**: So sánh performance giữa cách dùng list vs generator
5. **Mini project**: Sau khi làm xong 30 bài, hãy làm bài tổng hợp

**Chúc bạn luyện tập vui vẻ!** 🚀