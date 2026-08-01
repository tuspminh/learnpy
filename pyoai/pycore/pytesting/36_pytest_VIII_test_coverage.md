# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 36: Pytest (Phần 8) – Test Coverage, pytest-cov và đánh giá chất lượng kiểm thử

> **Coverage không đo xem phần mềm có đúng hay không.**
>
> Nó chỉ đo:
>
> **"Bao nhiêu phần code đã được chạy qua khi test?"**

Một lập trình viên chuyên nghiệp không chạy theo 100% coverage một cách máy móc.

Mục tiêu thật sự:

> Viết test đúng chỗ quan trọng, có giá trị bảo vệ hệ thống.

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu Code Coverage.
* Hiểu Line Coverage.
* Hiểu Branch Coverage.
* Cài đặt và sử dụng `pytest-cov`.
* Tạo báo cáo coverage.
* Đọc HTML Coverage Report.
* Thiết lập coverage trong CI/CD.
* Hiểu giới hạn của coverage.
* Xây chiến lược coverage thực tế.

---

# Roadmap Pytest

```text
Buổi 29
✓ Pytest cơ bản

Buổi 30
✓ Fixture

Buổi 31
✓ Parametrize

Buổi 32
✓ MonkeyPatch

Buổi 33
✓ Mock

Buổi 34
✓ Integration Test

Buổi 35
✓ E2E Test

Buổi 36
✓ Coverage

Buổi 37+
✓ Advanced Testing
```

---

# Phần I

# Coverage là gì?

Ví dụ:

File:

```python
calculator.py
```

```python
def add(a, b):

    return a + b


def divide(a, b):

    if b == 0:
        raise ValueError()

    return a / b
```

---

Test:

```python
def test_add():

    assert add(1, 2) == 3
```

---

Coverage:

```text
add()
✓ đã chạy

divide()
✗ chưa chạy
```

---

Kết quả:

```text
Coverage = 50%
```

---

# Phần II

# Các loại Coverage

Có nhiều loại:

---

# 1. Line Coverage

Đơn giản nhất.

Đo:

> Bao nhiêu dòng code đã được chạy?

Ví dụ:

```python
def hello():

    print("Hello")

    print("World")
```

Test:

```python
hello()
```

Coverage:

```text
2/2 lines

100%
```

---

# 2. Branch Coverage

Quan trọng hơn.

Kiểm tra:

Các nhánh điều kiện.

Ví dụ:

```python
def check_age(age):

    if age >= 18:
        return "adult"

    else:
        return "child"
```

---

Test:

```python
check_age(20)
```

Chạy:

```text
if True
```

Nhưng chưa chạy:

```text
else
```

---

Line Coverage:

```text
100%
```

Nhưng Branch Coverage:

```text
50%
```

---

Đây là lý do branch coverage quan trọng.

---

# Phần III

# Cài đặt pytest-cov

Cài:

```bash
pip install pytest-cov
```

---

Kiểm tra:

```bash
pytest --cov
```

---

Ví dụ:

```bash
pytest --cov=myapp
```

---

Kết quả:

```text
Name                 Stmts   Miss

app/service.py        50       5

app/repository.py     30       0


TOTAL                 80      93%
```

---

# Phần IV

# Tạo HTML Coverage Report

Lệnh:

```bash
pytest \
--cov=myapp \
--cov-report html
```

---

Sinh:

```text
htmlcov/

    index.html
```

---

Mở:

```text
htmlcov/index.html
```

---

Bạn thấy:

* File nào chưa test.
* Dòng nào chưa chạy.
* Bao nhiêu %.

---

# Phần V

# Ví dụ thực tế

Project:

```text
shop/

├── app/

│
├── tests/

│
└── requirements.txt
```

---

Chạy:

```bash
pytest \
--cov=app \
--cov-report html
```

---

Kết quả:

```text
app/

service.py        90%

repository.py     100%

payment.py        40%
```

---

Nhìn vào:

```text
payment.py
```

cần thêm test.

---

# Phần VI

# Coverage với pytest.ini

Không muốn gõ dài.

Tạo:

```text
pytest.ini
```

---

Nội dung:

```ini
[pytest]

addopts =
    --cov=app
    --cov-report=html
    --cov-report=term
```

---

Bây giờ:

```bash
pytest
```

Tự chạy coverage.

---

# Phần VII

# Coverage Fail Threshold

Ví dụ:

Muốn tối thiểu:

```text
80%
```

---

Chạy:

```bash
pytest \
--cov=app \
--cov-fail-under=80
```

---

Nếu:

```text
Coverage 75%
```

CI fail.

---

Kết quả:

```text
ERROR:
Coverage failure:
75 < 80
```

---

# Phần VIII

# Coverage trong CI/CD

Ví dụ GitHub Actions:

```yaml
name: Test

on:
  push:


jobs:

  test:

    runs-on: ubuntu-latest


    steps:

    - uses: actions/checkout@v4


    - name: Install

      run:

        pip install -r requirements.txt


    - name: Test

      run:

        pytest --cov
```

---

Flow:

```text
Developer

↓

Push code

↓

CI chạy pytest

↓

Coverage kiểm tra

↓

Pass / Fail
```

---

# Phần IX

# Coverage cho Clean Architecture

Ví dụ:

```text
app/

├── domain/

├── application/

├── infrastructure/

└── api/
```

Coverage nên ưu tiên:

---

## Domain

Mục tiêu:

```text
95-100%
```

Vì:

* Business rule.
* Không phụ thuộc bên ngoài.

---

## Service

Mục tiêu:

```text
85-95%
```

---

## Repository

Mục tiêu:

```text
70-90%
```

Vì:

* Cần integration test.

---

## API

Mục tiêu:

```text
70-80%
```

---

# Phần X

# Sai lầm: Chạy theo 100% Coverage

Ví dụ:

Code:

```python
def hello():

    print("hello")
```

Test:

```python
def test_hello():

    hello()
```

Coverage:

```text
100%
```

Nhưng:

Test có giá trị thấp.

---

Một test tốt phải kiểm tra:

```text
Input

↓

Behavior

↓

Output
```

---

# Phần XI

# Coverage không phát hiện Bug

Ví dụ:

Code:

```python
def discount(price):

    return price * 0.5
```

---

Test:

```python
assert discount(100) == 50
```

Coverage:

100%

---

Nhưng yêu cầu:

```text
Giảm 20%
```

Code sai.

Coverage không biết.

---

Coverage chỉ biết:

"Code đã chạy"

Không biết:

"Code đúng".

---

# Phần XII

# Mutation Testing

Đây là cấp cao hơn.

Ý tưởng:

Cố tình sửa code.

Ví dụ:

Code:

```python
return price * 0.8
```

Mutation:

```python
return price * 0.5
```

---

Nếu test vẫn pass:

Test yếu.

---

Công cụ:

```text
mutmut
```

---

Ví dụ:

```bash
pip install mutmut
```

---

Chạy:

```bash
mutmut run
```

---

# Phần XIII

# Coverage cho dự án Crawler

Áp dụng:

```text
story_crawler/

├── crawler/

├── parser/

├── repository/

├── services/

└── tests/
```

---

Mục tiêu:

## Parser

```text
95%
```

Test:

* HTML đúng.
* HTML lỗi.
* Thiếu tag.

---

## Service

```text
90%
```

Test:

* Crawl thành công.
* Timeout.
* Retry.

---

## Repository

```text
80%
```

Test:

* Save.
* Update.
* Delete.

---

# Phần XIV

# Kết hợp Coverage + Pytest Marker

Ví dụ:

```python
@pytest.mark.unit
def test_parser(): ...
```

---

```python
@pytest.mark.integration
def test_database(): ...
```

---

Chạy:

Unit:

```bash
pytest -m unit
```

---

Integration:

```bash
pytest -m integration
```

---

Coverage:

```bash
pytest -m unit --cov
```

---

# Phần XV

# Chiến lược Coverage chuyên nghiệp

Không phải:

```text
Tất cả 100%
```

---

Nên:

```text
Critical Business Logic

        95%


Service Layer

        85%


Infrastructure

        70%


UI

        60%
```

---

# Phần XVI

# Mini Project

## Thiết lập Coverage cho Story App

Cấu trúc:

```text
story_app/

├── app/

│   ├── parser

│   ├── service

│   └── repository


├── tests/


└── pytest.ini
```

---

pytest.ini:

```ini
[pytest]

addopts =
    --cov=app
    --cov-report=html
    --cov-fail-under=80
```

---

Chạy:

```bash
pytest
```

---

Kết quả:

```text
TOTAL

85%
```

Pass.

---

# Bài tập thực hành

## Bài 1

Cài:

```bash
pytest-cov
```

---

## Bài 2

Tạo:

```text
pytest.ini
```

---

## Bài 3

Sinh:

```text
HTML Coverage Report
```

---

## Bài 4

Đạt:

```text
80% coverage
```

cho:

```python
calculator.py
```

---

## Bài 5

Thiết lập:

```text
CI Coverage Check
```

---

# Tổng kết Buổi 36

Bạn đã học:

✅ Code Coverage
✅ Line Coverage
✅ Branch Coverage
✅ pytest-cov
✅ HTML Report
✅ Coverage Threshold
✅ CI/CD Coverage
✅ Coverage trong Clean Architecture
✅ Coverage Strategy
✅ Mutation Testing

---

# Góc nhìn Senior Python Developer

Một team chuyên nghiệp không hỏi:

> "Coverage bao nhiêu %?"

Mà hỏi:

> "Những phần quan trọng nhất của hệ thống đã được bảo vệ chưa?"

Một hệ thống tốt thường có:

```text
             Quality

                |

        ----------------

        Correctness

        Maintainability

        Testability

        Coverage
```

Coverage chỉ là **một công cụ đo lường**, không phải mục tiêu cuối cùng.

---

# Chuẩn bị Buổi 37

**Pytest (Phần 9) – Test Design Pattern và kiến trúc Test chuyên nghiệp**

Nội dung:

* AAA Pattern (Arrange - Act - Assert).
* Given When Then.
* Test Isolation.
* Test Data Builder.
* Object Mother.
* Factory Pattern trong Testing.
* Repository Test Pattern.
* Service Test Pattern.
* Thiết kế bộ test dễ bảo trì cho dự án lớn.
