# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 41: Pytest (Phần 13) – Performance Testing, Benchmarking và Profiling

> Một chương trình **đúng** chưa chắc đã **tốt**.
>
> Một chương trình **đúng + nhanh + ổn định** mới là chương trình chất lượng.

Ở các công ty lớn, sau khi Unit Test và Integration Test đều xanh, pipeline CI/CD thường còn có:

```text
Unit Test
      ↓
Integration Test
      ↓
Contract Test
      ↓
Performance Test
      ↓
Benchmark
      ↓
Deploy
```

Buổi học này sẽ giúp bạn làm chủ việc **đo hiệu năng**, **phân tích điểm nghẽn (bottleneck)** và **ngăn hiệu năng bị suy giảm theo thời gian (performance regression)**.

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu Performance Testing.
* Hiểu Benchmark.
* Phân biệt Benchmark và Stress Test.
* Sử dụng `pytest-benchmark`.
* Đọc kết quả Benchmark.
* Profiling bằng `cProfile`.
* Profiling bằng `line_profiler`.
* Memory Profiling.
* Performance Regression Test.
* Áp dụng cho dự án Python thực tế.

---

# Roadmap Pytest

```text
Buổi 29–40
✓ Functional Testing

Buổi 41
✓ Performance Testing
✓ Benchmark
✓ Profiling

Buổi 42
Security Testing

Buổi 43
Async Testing
```

---

# Phần I

# Performance Testing là gì?

Performance Testing trả lời câu hỏi:

```text
Code có chạy nhanh không?
```

Ví dụ:

```python
def search_user(users, name):
    for user in users:
        if user.name == name:
            return user
```

Đúng?

✔ Đúng.

Nhanh?

Chưa biết.

---

Ví dụ:

```python
users = load_5_million_users()
```

Có thể:

```text
Mất

15 giây
```

---

Performance Testing sẽ giúp trả lời:

* Bao lâu?
* Bao nhiêu RAM?
* Bao nhiêu CPU?

---

# Phần II

# Benchmark là gì?

Benchmark là:

> Đo hiệu năng của một đoạn code trong điều kiện kiểm soát.

Ví dụ:

```python
sum(range(1000))
```

Benchmark đo:

```text
Average Time

Median

Max

Min

StdDev
```

---

Khác với Unit Test:

Unit Test:

```text
Đúng?
```

Benchmark:

```text
Nhanh?
```

---

# Phần III

# pytest-benchmark

Cài:

```bash
pip install pytest-benchmark
```

---

Ví dụ:

```python
def calculate():

    return sum(range(10000))
```

---

Benchmark:

```python
def test_speed(benchmark):

    benchmark(calculate)
```

---

Chạy:

```bash
pytest
```

---

Kết quả:

```text
Name

test_speed

Mean

35 us

Rounds

10000
```

---

# Phần IV

# Benchmark có tham số

Ví dụ:

```python
def add(a, b):

    return a + b
```

---

Benchmark:

```python
def test_add(benchmark):

    result = benchmark(add, 10, 20)

    assert result == 30
```

---

Pytest:

* Benchmark.
* Đồng thời verify kết quả.

---

# Phần V

# So sánh hai thuật toán

Ví dụ:

## Cách 1

```python
def total1():

    s = 0

    for i in range(100000):
        s += i

    return s
```

---

## Cách 2

```python
def total2():

    return sum(range(100000))
```

---

Benchmark:

```python
def test_loop(benchmark):

    benchmark(total1)
```

---

```python
def test_sum(benchmark):

    benchmark(total2)
```

---

Kết quả:

```text
total2

Nhanh hơn
```

---

Đây là cách lựa chọn implementation.

---

# Phần VI

# Benchmark Group

Có thể nhóm benchmark:

```python
@pytest.mark.benchmark(group="parser")
def test_parser(benchmark): ...
```

---

```python
@pytest.mark.benchmark(group="repository")
def test_repo(benchmark): ...
```

---

Report:

```text
Parser

Repository
```

Dễ đọc hơn.

---

# Phần VII

# cProfile

Python có profiler tích hợp.

Ví dụ:

```python
import cProfile


def run(): ...
```

---

Chạy:

```python
cProfile.run("run()")
```

---

Output:

```text
10000 function calls

0.25 seconds
```

---

Biết:

* Hàm nào chạy nhiều.
* Hàm nào tốn thời gian.

---

# Phần VIII

# Phân tích bằng pstats

```python
import pstats

stats = pstats.Stats("profile.out")
```

---

Sort:

```python
stats.sort_stats("cumtime")
```

---

In:

```python
stats.print_stats(20)
```

Top:

```text
20 hàm chậm nhất
```

---

# Phần IX

# line_profiler

Có lúc biết:

```text
Hàm chậm
```

chưa đủ.

Muốn biết:

```text
Dòng nào chậm?
```

---

Cài:

```bash
pip install line_profiler
```

---

Ví dụ:

```python
@profile
def process(): ...
```

---

Chạy:

```bash
kernprof -l app.py
```

---

Output:

```text
Line 10

30%

Line 15

60%
```

Biết chính xác bottleneck.

---

# Phần X

# Memory Profiling

Có những chương trình:

CPU thấp.

Nhưng RAM:

```text
10 GB
```

---

Cài:

```bash
pip install memory-profiler
```

---

Ví dụ:

```python
from memory_profiler import profile


@profile
def load_data(): ...
```

---

Kết quả:

```text
Line

Memory

+20MB

+300MB
```

---

# Phần XI

# Performance Regression Test

Ví dụ:

Version 1:

```text
50 ms
```

---

Version 2:

```text
500 ms
```

---

Bug.

---

Benchmark trong CI:

```text
Nếu

>100 ms

↓

Fail
```

---

Đây gọi là:

Performance Regression.

---

# Phần XII

# Benchmark cho Parser

Ví dụ dự án crawler.

Parser:

```python
selector.css(".chapter")
```

---

Benchmark:

```python
def test_parser(benchmark):

    html = load_html()

    benchmark(parse, html)
```

---

Sau khi sửa Parser:

Benchmark:

```text
30%

Nhanh hơn
```

---

# Phần XIII

# Benchmark cho SQLite Repository

Ví dụ:

```python
repo.save()
```

---

Benchmark:

```python
benchmark(repo.save, chapter)
```

---

So sánh:

```text
SQLite

vs

PostgreSQL
```

---

Hoặc:

```text
SQLAlchemy

vs

sqlite3
```

---

# Phần XIV

# Benchmark cho HTTP Downloader

Ví dụ:

Downloader:

```text
urllib

↓

requests

↓

httpx

↓

aiohttp
```

---

Benchmark:

```text
100 requests
```

So sánh:

* Throughput.
* Latency.

---

# Phần XV

# Benchmark Async

Ví dụ:

```python
async def download(): ...
```

Benchmark:

```python
benchmark(asyncio.run, download())
```

---

So sánh:

```text
Sequential

↓

Async
```

---

# Phần XVI

# Áp dụng cho Story Crawler

Project:

```text
Crawler

↓

Downloader

↓

Parser

↓

Repository

↓

Cache
```

---

Benchmark:

## Parser

```text
Parse HTML

<20ms
```

---

Downloader:

```text
Concurrent

100 URLs
```

---

Repository:

```text
1000 insert

<500ms
```

---

Cache:

```text
Redis GET

<5ms
```

---

# Phần XVII

# Sai lầm phổ biến

## 1. Benchmark trên máy đang tải nặng

Ví dụ:

* Đang render video.
* Đang chơi game.
* Đang chạy Docker.

Kết quả sẽ không ổn định.

---

## 2. Benchmark một lần

Sai:

```text
1 lần
```

Đúng:

```text
1000+

lần
```

`pytest-benchmark` tự thực hiện nhiều vòng để giảm nhiễu.

---

## 3. So sánh code với dữ liệu khác nhau

Sai:

```text
Version A

100 dòng

Version B

1 triệu dòng
```

Benchmark phải dùng cùng dữ liệu đầu vào.

---

## 4. Tối ưu quá sớm

Nguyên tắc nổi tiếng của Donald Knuth:

> "Premature optimization is the root of all evil."

Hãy:

1. Đo.
2. Xác định bottleneck.
3. Tối ưu đúng chỗ.

---

# Phần XVIII

# Mini Project

Benchmark hệ thống Story Crawler.

```
tests/

performance/

    test_parser.py

    test_repository.py

    test_downloader.py

    test_cache.py
```

Mỗi module đều có benchmark riêng.

---

# Bài tập

## Bài 1

Benchmark:

```python
sum(range(100000))
```

---

## Bài 2

So sánh:

```python
for
```

và

```python
sum()
```

---

## Bài 3

Dùng:

```python
cProfile
```

để tìm hàm chậm nhất.

---

## Bài 4

Dùng:

```python
line_profiler
```

để tìm dòng chậm nhất.

---

## Bài 5

Benchmark Parser của dự án crawler.

---

# Tổng kết Buổi 41

Bạn đã học:

* ✅ Performance Testing.
* ✅ Benchmark.
* ✅ `pytest-benchmark`.
* ✅ Benchmark Group.
* ✅ `cProfile`.
* ✅ `pstats`.
* ✅ `line_profiler`.
* ✅ Memory Profiling.
* ✅ Performance Regression.
* ✅ Benchmark cho Parser, Repository, HTTP và Async.

---

# Góc nhìn Senior Python Developer

Hiệu năng không nên được đánh giá bằng cảm giác:

> "Có vẻ nhanh."

Mà phải được đo bằng số liệu:

```text
Mean Time

Median

P95

P99

Memory

CPU
```

Trong các dự án lớn, **benchmark là một phần của kiểm thử tự động**, giống như Unit Test.

---

# Chuẩn bị Buổi 42

**Pytest (Phần 14) – Security Testing và kiểm thử các lỗ hổng bảo mật trong ứng dụng Python**

Chúng ta sẽ học:

* Security Testing là gì.
* Kiểm thử xác thực (Authentication).
* Kiểm thử phân quyền (Authorization).
* Kiểm thử Input Validation.
* Kiểm thử SQL Injection.
* Kiểm thử XSS.
* Kiểm thử CSRF.
* Kiểm thử File Upload.
* Kiểm thử Rate Limiting.
* Kiểm thử JWT, API Key và OAuth.
* Kết hợp Security Test vào CI/CD.

Đây là bước chuyển từ **ứng dụng chạy đúng và nhanh** sang **ứng dụng an toàn trước các lỗi và lỗ hổng phổ biến**.
