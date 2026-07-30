Chào bạn! Bạn đã vượt qua Bài 10 về File I/O và Serialization - tuyệt vời! Bây giờ chúng ta bước vào **Bài 11: Iterator và Generator** - một trong những tính năng mạnh mẽ nhất của Python giúp xử lý dữ liệu lớn một cách hiệu quả về bộ nhớ!

---

# 📘 BÀI 11: ITERATOR VÀ GENERATOR

---

## 🎯 MỤC TIÊU BÀI HỌC

Sau bài này, bạn sẽ:
- Hiểu **Iterator Protocol** (__iter__, __next__)
- Tạo custom iterator cho các trường hợp đặc biệt
- Sử dụng **Generator** với `yield` - code gọn, tiết kiệm bộ nhớ
- Biết khi nào dùng generator vs list
- Sử dụng **itertools** - thư viện vô cùng mạnh mẽ
- Xử lý dữ liệu lớn (streaming) với generator
- Tạo infinite generators

---

## 📖 PHẦN 1: LÝ THUYẾT CÔ ĐỌNG

### 1.1. Iterator là gì?

**Iterator = Object có thể lặp qua từng phần tử một**

```python
# Python kiểu dữ liệu có thể lặp (iterable)
my_list = [1, 2, 3, 4, 5]
my_string = "Python"
my_dict = {"a": 1, "b": 2}

# Tất cả đều có thể dùng for
for item in my_list:
    print(item)

# Lấy iterator từ iterable
iterator = iter(my_list)
print(next(iterator))  # 1
print(next(iterator))  # 2
print(next(iterator))  # 3
```

**Iterator Protocol:**
- `__iter__()`: Trả về chính iterator object
- `__next__()`: Trả về phần tử tiếp theo, raise StopIteration khi hết

```python
# Vòng lặp for hoạt động như thế nào
iterator = iter(my_list)
while True:
    try:
        item = next(iterator)
        print(item)
    except StopIteration:
        break
```

---

### 1.2. Tạo Custom Iterator

```python
class FibonacciIterator:
    """Custom iterator cho dãy Fibonacci"""

    def __init__(self, max_count):
        self.max_count = max_count
        self.count = 0
        self.a, self.b = 0, 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.count >= self.max_count:
            raise StopIteration

        result = self.a
        self.a, self.b = self.b, self.a + self.b
        self.count += 1
        return result


# Sử dụng
fib = FibonacciIterator(10)
for num in fib:
    print(num, end=" ")  # 0 1 1 2 3 5 8 13 21 34
```

---

### 1.3. Generator - Cách tạo iterator đơn giản

**Generator = Hàm có từ khóa `yield` thay vì `return`**

```python
def fibonacci_generator(max_count):
    """Generator cho dãy Fibonacci - gọn hơn nhiều!"""
    a, b = 0, 1
    count = 0
    while count < max_count:
        yield a
        a, b = b, a + b
        count += 1


# Sử dụng
for num in fibonacci_generator(10):
    print(num, end=" ")  # 0 1 1 2 3 5 8 13 21 34

# Lấy từng giá trị
gen = fibonacci_generator(5)
print(next(gen))  # 0
print(next(gen))  # 1
print(next(gen))  # 1
```

**Điều gì xảy ra khi gọi generator?**
1. Hàm chưa chạy ngay - trả về generator object
2. Mỗi lần `next()` được gọi, hàm chạy đến `yield`
3. Trạng thái của hàm được lưu lại (tất cả biến)
4. Lần gọi tiếp theo, hàm tiếp tục từ chỗ dừng

---

### 1.4. Generator Expression - List Comprehension cho generator

```python
# List Comprehension - Tạo list (tốn bộ nhớ)
squares_list = [x**2 for x in range(10)]
print(squares_list)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
print(type(squares_list))  # <class 'list'>

# Generator Expression - Tạo generator (tiết kiệm bộ nhớ)
squares_gen = (x**2 for x in range(10))
print(squares_gen)  # <generator object <genexpr> at 0x...>
print(type(squares_gen))  # <class 'generator'>

# Duyệt generator
for num in squares_gen:
    print(num, end=" ")
```

**Khi nào dùng cái nào?**

| List Comprehension | Generator Expression |
|--------------------|----------------------|
| Dùng khi cần dữ liệu nhiều lần | Dùng khi chỉ duyệt 1 lần |
| Tốn bộ nhớ (lưu tất cả) | Tiết kiệm bộ nhớ |
| Nhanh hơn (dữ liệu nhỏ) | Chậm hơn (nhưng tiết kiệm) |
| Ví dụ: `[x for x in range(100)]` | Ví dụ: `(x for x in range(100))` |

---

### 1.5. Generator với `yield from` - Delegation

```python
def sub_generator():
    """Generator con"""
    for i in range(3):
        yield f"Sub {i}"


def main_generator():
    """Generator chính với yield from"""
    yield "Start"
    yield from sub_generator()  # Ủy quyền cho generator con
    yield "End"


for item in main_generator():
    print(item)
# Start
# Sub 0
# Sub 1
# Sub 2
# End
```

---

### 1.6. Infinite Generators

```python
def infinite_counter():
    """Generator vô hạn - đếm từ 0 đến vô cùng"""
    num = 0
    while True:
        yield num
        num += 1


# Lấy 10 số đầu
counter = infinite_counter()
for _ in range(10):
    print(next(counter), end=" ")  # 0 1 2 3 4 5 6 7 8 9

# Vòng lặp vô hạn - cẩn thận!
# for num in infinite_counter():
#     print(num)  # Chạy mãi mãi
```

---

### 1.7. `itertools` - Thư viện vô cùng mạnh mẽ

```python
import itertools

# 1. count - Đếm vô hạn
counter = itertools.count(start=10, step=2)
print([next(counter) for _ in range(5)])  # [10, 12, 14, 16, 18]

# 2. cycle - Lặp lại vô hạn
colors = itertools.cycle(["red", "green", "blue"])
print(
    [next(colors) for _ in range(7)]
)  # ['red', 'green', 'blue', 'red', 'green', 'blue', 'red']

# 3. repeat - Lặp lại giá trị
print(list(itertools.repeat("Python", 3)))  # ['Python', 'Python', 'Python']

# 4. chain - Nối nhiều iterables
print(list(itertools.chain([1, 2], [3, 4], [5, 6])))  # [1, 2, 3, 4, 5, 6]

# 5. compress - Lọc theo mask
data = ["a", "b", "c", "d", "e"]
selectors = [1, 0, 1, 0, 1]
print(list(itertools.compress(data, selectors)))  # ['a', 'c', 'e']

# 6. dropwhile / takewhile
numbers = [1, 2, 3, 4, 5, 6, 7, 8]
print(list(itertools.dropwhile(lambda x: x < 5, numbers)))  # [5, 6, 7, 8]
print(list(itertools.takewhile(lambda x: x < 5, numbers)))  # [1, 2, 3, 4]

# 7. permutations - Hoán vị
print(list(itertools.permutations("ABC", 2)))
# [('A', 'B'), ('A', 'C'), ('B', 'A'), ('B', 'C'), ('C', 'A'), ('C', 'B')]

# 8. combinations - Tổ hợp
print(list(itertools.combinations("ABC", 2)))
# [('A', 'B'), ('A', 'C'), ('B', 'C')]

# 9. product - Tích Descartes
print(list(itertools.product("AB", [1, 2])))
# [('A', 1), ('A', 2), ('B', 1), ('B', 2)]

# 10. groupby - Nhóm theo key
data = [("a", 1), ("a", 2), ("b", 3), ("b", 4), ("c", 5)]
for key, group in itertools.groupby(data, lambda x: x[0]):
    print(f"{key}: {list(group)}")
# a: [('a', 1), ('a', 2)]
# b: [('b', 3), ('b', 4)]
# c: [('c', 5)]
```

---

## 💻 PHẦN 2: CODE VÍ DỤ THỰC TẾ

### Ví dụ 1: Xử lý file lớn với generator

```python
import csv
import json
from typing import Iterator, Dict, Any


def read_large_csv(filepath: str, chunk_size: int = 1000) -> Iterator[Dict[str, Any]]:
    """Đọc CSV lớn từng chunk để tiết kiệm bộ nhớ"""
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        chunk = []
        for row in reader:
            chunk.append(row)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk


def read_large_json(filepath: str, chunk_size: int = 1000) -> Iterator[Dict[str, Any]]:
    """Đọc JSON lớn từng chunk"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        for i in range(0, len(data), chunk_size):
            yield data[i : i + chunk_size]


def read_large_text(filepath: str, chunk_size: int = 8192) -> Iterator[str]:
    """Đọc text lớn từng chunk (byte)"""
    with open(filepath, "r", encoding="utf-8") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


# SỬ DỤNG
import tempfile
import time


# Tạo file CSV test lớn
def create_test_csv(filepath: str, rows: int = 10000):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "name", "age", "city"])
        for i in range(rows):
            writer.writerow([i, f"User_{i}", 20 + (i % 20), f"City_{i % 10}"])


# Test với file lớn
with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
    create_test_csv(tmp.name, 10000)
    filepath = tmp.name

# Xử lý từng chunk
print("=== PROCESSING LARGE CSV ===")
start = time.time()
total_count = 0

for chunk in read_large_csv(filepath, chunk_size=2000):
    total_count += len(chunk)
    # Xử lý chunk (ví dụ: tính toán thống kê)
    avg_age = sum(int(row["age"]) for row in chunk) / len(chunk)
    print(f"Chunk: {len(chunk)} rows, avg age: {avg_age:.2f}")

print(f"Total: {total_count} rows")
print(f"Time: {time.time() - start:.2f}s")
```

---

### Ví dụ 2: Data Pipeline với Generator

```python
from typing import Iterator, Any
import time


class DataPipeline:
    """Xây dựng data pipeline sử dụng generator"""

    def __init__(self):
        self.steps = []

    def add_step(self, func):
        """Thêm bước xử lý"""
        self.steps.append(func)
        return self

    def execute(self, data: Iterator[Any]) -> Iterator[Any]:
        """Chạy pipeline với dữ liệu"""
        result = data

        for step in self.steps:
            result = step(result)

        return result


# Các bước xử lý
def filter_positive(data: Iterator[int]) -> Iterator[int]:
    """Lọc số dương"""
    for x in data:
        if x > 0:
            yield x


def multiply_by_two(data: Iterator[int]) -> Iterator[int]:
    """Nhân đôi"""
    for x in data:
        yield x * 2


def add_ten(data: Iterator[int]) -> Iterator[int]:
    """Cộng thêm 10"""
    for x in data:
        yield x + 10


def square(data: Iterator[int]) -> Iterator[int]:
    """Bình phương"""
    for x in data:
        yield x**2


def only_even(data: Iterator[int]) -> Iterator[int]:
    """Lọc số chẵn"""
    for x in data:
        if x % 2 == 0:
            yield x


# Tạo pipeline
pipeline = DataPipeline()
pipeline.add_step(filter_positive)
pipeline.add_step(multiply_by_two)
pipeline.add_step(add_ten)
pipeline.add_step(square)
pipeline.add_step(only_even)

# Dữ liệu đầu vào
data = [-5, -3, 0, 2, 4, 6, 8, 10, -1, 3, 5, 7, 9]

# Chạy pipeline
print("=== DATA PIPELINE ===")
print(f"Input: {data}")
print("Processing...")
result = list(pipeline.execute(iter(data)))
print(f"Output: {result}")


# Pipeline 2 - Xử lý streaming
def generate_data():
    """Generator dữ liệu vô hạn"""
    i = 0
    while True:
        yield i
        i += 1


print("\n=== STREAMING PIPELINE ===")
pipeline2 = DataPipeline()
pipeline2.add_step(filter_positive)
pipeline2.add_step(lambda x: (y for y in x if y % 2 == 0))  # Chỉ số chẵn
pipeline2.add_step(lambda x: (y * 10 for y in x))

# Lấy 10 giá trị đầu từ pipeline
result = pipeline2.execute(generate_data())
for i, val in enumerate(result):
    if i >= 20:
        break
    print(val, end=" ")
```

---

### Ví dụ 3: Hệ thống Monitor và Log với Generator

```python
import time
import random
from typing import Iterator, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Metric:
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]


def generate_metrics() -> Iterator[Metric]:
    """Generator tạo metrics ngẫu nhiên"""
    metric_names = ["cpu_usage", "memory_usage", "disk_io", "network_in", "network_out"]
    tags_options = {
        "host": ["server1", "server2", "server3"],
        "environment": ["prod", "staging", "dev"],
        "region": ["us-east", "us-west", "eu-west"],
    }

    while True:
        for name in metric_names:
            # Chọn tags ngẫu nhiên
            tags = {
                "host": random.choice(tags_options["host"]),
                "environment": random.choice(tags_options["environment"]),
                "region": random.choice(tags_options["region"]),
            }

            # Giá trị ngẫu nhiên
            if name in ["cpu_usage", "memory_usage"]:
                value = random.uniform(0, 100)  # Percentage
            else:
                value = random.uniform(0, 1000)  # MB/s

            yield Metric(name=name, value=value, timestamp=datetime.now(), tags=tags)
        time.sleep(0.1)  # Chờ giữa các lần generate


def filter_metrics(
    metrics: Iterator[Metric], name: str = None, tags: Dict[str, str] = None
) -> Iterator[Metric]:
    """Lọc metrics theo điều kiện"""
    for metric in metrics:
        if name and metric.name != name:
            continue
        if tags:
            if not all(metric.tags.get(k) == v for k, v in tags.items()):
                continue
        yield metric


def aggregate_metrics(
    metrics: Iterator[Metric], window_seconds: int = 5
) -> Iterator[Dict[str, Any]]:
    """Aggregate metrics trong khoảng thời gian"""
    window = []
    start_time = time.time()

    for metric in metrics:
        window.append(metric)

        # Nếu đã đủ thời gian hoặc cửa sổ đầy
        if time.time() - start_time >= window_seconds:
            # Tính toán thống kê
            if window:
                values = [m.value for m in window]
                yield {
                    "timestamp": datetime.now(),
                    "count": len(window),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "sum": sum(values),
                }
            window = []
            start_time = time.time()


def alert_on_threshold(
    metrics: Iterator[Metric], thresholds: Dict[str, float]
) -> Iterator[Metric]:
    """Tạo alert khi vượt ngưỡng"""
    for metric in metrics:
        if metric.name in thresholds:
            if metric.value > thresholds[metric.name]:
                metric.tags["alert"] = "true"
                yield metric
        else:
            yield metric


# SỬ DỤNG
print("=== METRICS MONITORING SYSTEM ===")

# Tạo metrics
metrics_stream = generate_metrics()

# Pipeline xử lý
# 1. Lọc CPU usage
cpu_metrics = filter_metrics(metrics_stream, name="cpu_usage")

# 2. Lọc theo tags
prod_cpu = filter_metrics(cpu_metrics, tags={"environment": "prod", "host": "server1"})

# 3. Aggregation
aggregated = aggregate_metrics(prod_cpu, window_seconds=3)

# 4. Alert
alerts = alert_on_threshold(prod_cpu, thresholds={"cpu_usage": 80.0})

# Thu thập và hiển thị
for i in range(10):  # Chỉ lấy 10 metric
    try:
        metric = next(alerts)
        print(
            f"[{metric.timestamp.strftime('%H:%M:%S')}] {metric.name}: {metric.value:.2f}"
        )
        if metric.tags.get("alert") == "true":
            print(f"  ⚠️ ALERT! CPU usage exceeded threshold!")
    except StopIteration:
        break
```

---

### Ví dụ 4: Xử lý dữ liệu streaming với Generator

```python
import time
import random
from typing import Iterator, Tuple, List


class DataStream:
    """Stream dữ liệu real-time"""

    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size

    def generate_sensor_data(self) -> Iterator[Tuple[str, float]]:
        """Tạo dữ liệu cảm biến"""
        sensors = ["temp_1", "temp_2", "humidity", "pressure", "wind"]
        while True:
            sensor = random.choice(sensors)
            if sensor.startswith("temp"):
                value = random.uniform(15, 35)
            elif sensor == "humidity":
                value = random.uniform(30, 90)
            elif sensor == "pressure":
                value = random.uniform(980, 1030)
            else:
                value = random.uniform(0, 50)

            yield sensor, value
            time.sleep(0.05)  # 20 readings per second

    def batch_data(self, data: Iterator) -> Iterator[List]:
        """Batch dữ liệu thành từng nhóm"""
        batch = []
        for item in data:
            batch.append(item)
            if len(batch) >= self.batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    def calculate_moving_average(
        self, data: Iterator, window: int = 10
    ) -> Iterator[float]:
        """Tính moving average của sensor data"""
        window_data = []
        for sensor, value in data:
            if sensor.startswith("temp"):
                window_data.append(value)
                if len(window_data) > window:
                    window_data.pop(0)
                yield sum(window_data) / len(window_data)

    def detect_anomalies(
        self, data: Iterator, threshold: float = 2.0
    ) -> Iterator[Tuple[str, float]]:
        """Phát hiện bất thường"""
        values = []
        for sensor, value in data:
            if sensor.startswith("temp"):
                values.append(value)
                if len(values) > 10:
                    values.pop(0)
                    mean = sum(values) / len(values)
                    std = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
                    if abs(value - mean) > threshold * std:
                        yield sensor, value


# SỬ DỤNG
print("=== SENSOR DATA STREAM ===")

stream = DataStream(batch_size=20)
sensor_data = stream.generate_sensor_data()

# Pipeline
batched = stream.batch_data(sensor_data)
moving_avg = stream.calculate_moving_average(sensor_data)
anomalies = stream.detect_anomalies(sensor_data)

# Process data
print("Collecting sensor data...")
sensor_gen = stream.generate_sensor_data()
count = 0

# Batch processing
for batch in stream.batch_data(sensor_gen):
    if count >= 50:
        break

    # In batch
    print(f"\n📊 Batch {count // 20 + 1}:")
    for sensor, value in batch:
        print(f"  {sensor}: {value:.2f}")

    # Tính moving average
    print("  📈 Moving Average:")
    avg_gen = stream.calculate_moving_average(iter(batch))
    avg = list(avg_gen)
    if avg:
        print(f"    {avg[-1]:.2f}")

    count += 20
    time.sleep(0.5)
```

---

## 🧪 PHẦN 3: BÀI TẬP VỀ NHÀ (10 bài)

### 📌 Bài tập cơ bản (6 bài)

**Bài 1:** Viết generator `count_down(n)` đếm ngược từ n về 0.

**Bài 2:** Viết generator `fibonacci()` sinh dãy Fibonacci vô hạn.

**Bài 3:** Viết generator `read_file_lines(filename)` đọc từng dòng của file mà không load toàn bộ vào memory.

**Bài 4:** Tạo custom iterator `PrimeIterator` sinh các số nguyên tố.

**Bài 5:** Sử dụng generator để lọc các số chẵn từ list.

**Bài 6:** Viết generator `chunk_data(data, chunk_size)` chia list thành từng chunk nhỏ.

---

### ⭐ Bài tập nâng cao (4 bài)

**Bài 7:** Xây dựng data pipeline với generator xử lý dữ liệu từ CSV.

**Bài 8:** Tạo hệ thống log streaming với generator.

**Bài 9:** Sử dụng `itertools` để giải các bài toán tổ hợp.

**Bài 10:** Xây dựng hệ thống ETL (Extract-Transform-Load) sử dụng generator.

---

## 🏗️ MINI-PROJECT: HỆ THỐNG ETL VỚI GENERATOR

```python
"""
Xây dựng hệ thống ETL (Extract, Transform, Load) sử dụng generator:

1. EXTRACT:
   - extract_from_csv(filepath) -> Generator[Dict]
   - extract_from_json(filepath) -> Generator[Dict]
   - extract_from_api(url) -> Generator[Dict]

2. TRANSFORM:
   - filter_data(generator, condition) -> Generator
   - map_data(generator, mapping) -> Generator
   - aggregate_data(generator, window) -> Generator
   - validate_data(generator, schema) -> Generator

3. LOAD:
   - load_to_csv(generator, filepath)
   - load_to_json(generator, filepath)
   - load_to_database(generator, connection)

4. USE CASE:
   - Đọc dữ liệu từ CSV
   - Filter và transform
   - Load vào database hoặc file mới

5. FEATURES:
   - Streaming xử lý dữ liệu lớn
   - Memory efficient
   - Pipeline pattern
"""

# Hãy tự viết!
```

---

## ✅ KIỂM TRA CODE ITERATOR/GENERATOR

- [ ] Sử dụng `yield` thay vì return list
- [ ] Sử dụng generator expression cho dữ liệu lớn
- [ ] Custom iterator implement `__iter__` và `__next__`
- [ ] Xử lý `StopIteration` đúng cách
- [ ] Sử dụng `itertools` cho các tác vụ thông dụng
- [ ] Generator có `try/finally` để clean up

---

## 🔥 THỬ THÁCH (Bonus)

```python
# Tạo generator pipeline với cú pháp đẹp
@generator_pipeline
def process_data(data):
    return (
        data
        | filter(lambda x: x > 0)
        | map(lambda x: x * 2)
        | filter(lambda x: x % 2 == 0)
        | accumulate(lambda x, y: x + y)
    )


# Sử dụng
result = process_data(range(10))
print(list(result))  # [2, 6, 12, 20, 30, 42, 56, 72, 90]
```

---

## 🎯 TÓM TẮT KIẾN THỨC QUAN TRỌNG

| Khái niệm | Cú pháp | Ứng dụng |
|-----------|---------|----------|
| **Iterator** | `__iter__`, `__next__` | Custom iteration |
| **Generator** | `yield` | Streaming, memory efficient |
| **Generator Expression** | `(x for x in range(10))` | Lazy evaluation |
| **yield from** | `yield from other_gen` | Delegation |
| **itertools** | `import itertools` | Powerful tools |

---

**Chúc mừng bạn đã hoàn thành Bài 11! Generator là kỹ năng quan trọng để xử lý dữ liệu lớn hiệu quả.** 💪

*Bài 12 sẽ dạy bạn về Unit Test và Debug - kỹ năng không thể thiếu của lập trình viên chuyên nghiệp!*

**Hãy gửi code các bài tập để tôi review nhé!** 🚀