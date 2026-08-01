# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 35: Pytest (Phần 7) – End-to-End Testing (E2E) và Functional Testing chuyên nghiệp

> **E2E Testing mô phỏng hành động của người dùng thật.**
>
> Không kiểm tra từng hàm.
>
> Không kiểm tra từng module.
>
> Nó kiểm tra toàn bộ hệ thống từ đầu đến cuối.

Ví dụ một ứng dụng bán hàng:

```text
Người dùng

 ↓

Mở Website

 ↓

Đăng nhập

 ↓

Tìm sản phẩm

 ↓

Thêm vào giỏ hàng

 ↓

Thanh toán

 ↓

Nhận Email
```

E2E Test kiểm tra toàn bộ luồng này.

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu E2E Testing.
* Hiểu Functional Testing.
* Phân biệt Unit / Integration / E2E.
* Thiết kế E2E Test.
* Test API End-to-End.
* Test CLI Application.
* Test Web Application.
* Biết Selenium / Playwright.
* Viết workflow test chuyên nghiệp.
* Chuẩn bị cho CI/CD.

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

Buổi 36+
✓ Advanced Testing
```

---

# Phần I

# Ba tầng Testing

Một hệ thống chuyên nghiệp thường có:

```text
                 E2E

              /       \

       Integration

        /          \

            Unit
```

---

# 1. Unit Test

Kiểm tra:

```text
Function
Class
Method
```

Ví dụ:

```python
calculate_total()
```

---

Nhanh:

```text
10000 tests
≈ vài giây
```

---

# 2. Integration Test

Kiểm tra:

```text
Service

+

Database
```

---

Ví dụ:

```text
UserService

↓

Repository

↓

SQLite
```

---

# 3. E2E Test

Kiểm tra:

```text
Toàn bộ hệ thống
```

---

Ví dụ:

```text
Browser

↓

API

↓

Service

↓

Database

↓

Email
```

---

# Phần II

# Functional Testing là gì?

Functional Test kiểm tra:

> Hệ thống có thực hiện đúng chức năng người dùng mong muốn không?

Ví dụ:

Yêu cầu:

> Người dùng đăng nhập thành công.

Test:

```text
Nhập username

↓

Nhập password

↓

Click Login

↓

Vào Dashboard
```

---

Không quan tâm:

* Code bên trong.
* Class nào chạy.
* Database gì.

Chỉ quan tâm:

"Kết quả cuối cùng".

---

# Phần III

# Khi nào dùng E2E?

Dùng cho:

✅ Quy trình quan trọng

Ví dụ:

* Login.
* Thanh toán.
* Đăng ký.
* Upload file.
* Đặt hàng.
* Crawl dữ liệu.

---

Không dùng cho:

❌ Hàm nhỏ.

Ví dụ:

```python
def add(a,b):
```

Không cần E2E.

---

# Phần IV

# E2E Testing cho API

Rất phổ biến trong Python backend.

Ví dụ:

Ứng dụng:

```text
FastAPI

↓

PostgreSQL

↓

Redis
```

---

Luồng:

```text
Client

↓

POST /users

↓

Database

↓

Response
```

---

## Ví dụ

API:

```python
POST / users
```

Body:

```json
{
"name":"Alice"
}
```

---

E2E Test:

```python
def test_create_user(client):

    response = client.post("/users", json={"name": "Alice"})

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Alice"
```

---

Ở đây:

Không Mock.

Chạy:

```text
API thật

Database thật(test)

Logic thật
```

---

# Phần V

# E2E với Database riêng

Không dùng:

```text
Production DB
```

---

Dùng:

```text
Test Database
```

Ví dụ:

```text
app_db

app_test_db
```

---

Cấu hình:

```python
DATABASE_URL=

sqlite:///test.db
```

---

Khi pytest chạy:

```text
Create DB

↓

Run test

↓

Delete DB
```

---

# Phần VI

# E2E Testing với CLI Application

Python có rất nhiều CLI:

* Click.
* Typer.
* argparse.

Ví dụ:

Ứng dụng:

```bash
python app.py download book
```

---

Test:

Dùng:

```python
from click.testing import CliRunner
```

---

Ví dụ:

```python
def test_download():

    runner = CliRunner()

    result = runner.invoke(cli, ["download", "book1"])

    assert result.exit_code == 0
```

---

Ứng dụng:

* Crawler CLI.
* Backup tool.
* Deployment tool.

---

# Phần VII

# E2E Testing Web Application

Có hai công cụ phổ biến:

---

# Selenium

Cũ nhưng phổ biến.

```text
Browser

↓

Selenium Driver

↓

Chrome
```

---

# Playwright

Hiện đại hơn.

Hỗ trợ:

* Chromium.
* Firefox.
* WebKit.

---

Cài:

```bash
pip install playwright
```

---

Cài browser:

```bash
playwright install
```

---

# Phần VIII

# Playwright + Pytest

Ví dụ:

```python
from playwright.sync_api import Page


def test_login(page: Page):

    page.goto("http://localhost:8000/login")

    page.fill("#username", "admin")

    page.fill("#password", "123456")

    page.click("button")

    assert page.url.endswith("/dashboard")
```

---

Mô phỏng:

```text
Người dùng thật
```

---

# Phần IX

# Fixture cho Browser

Ví dụ:

```python
import pytest


@pytest.fixture
def browser():

    browser = launch_browser()

    yield browser

    browser.close()
```

---

Test:

```python
def test_home(browser):

    page = browser.new_page()

    page.goto("http://localhost")
```

---

# Phần X

# Page Object Model (POM)

Đây là kiến trúc chuyên nghiệp.

Không viết:

```python
page.click()
page.fill()
page.click()
```

lung tung.

---

Tạo:

```text
tests/

pages/

    login_page.py

    home_page.py
```

---

Ví dụ:

```python
class LoginPage:
    def __init__(self, page):

        self.page = page

    def login(self, username, password):

        self.page.fill("#user", username)

        self.page.fill("#pass", password)

        self.page.click("button")
```

---

Test:

```python
def test_login(page):

    login = LoginPage(page)

    login.login("admin", "123")
```

---

Ưu điểm:

* Dễ bảo trì.
* Ít duplicate.
* Phù hợp dự án lớn.

---

# Phần XI

# E2E Testing cho hệ thống Crawler

Áp dụng vào dự án của bạn.

Kiến trúc:

```text
User

↓

PySide6 Dashboard

↓

Crawler Service

↓

Parser

↓

Repository

↓

SQLite
```

---

E2E Test:

```text
Click "Start Crawl"

↓

Crawler chạy

↓

Download HTML

↓

Parse Chapter

↓

Save Database

↓

Hiển thị trên Dashboard
```

---

Test:

```python
def test_crawl_story():

    start_crawler()

    chapter = database.find("Chapter 1")

    assert chapter is not None
```

---

# Phần XII

# Test Workflow

Một E2E Test tốt kiểm tra workflow.

Ví dụ:

## App đọc truyện

Workflow:

```text
1. Add Website

2. Crawl Story

3. Download Chapter

4. Save Database

5. Open Reader

6. Display Content
```

---

Không test:

```python
parse_html()
```

(vì đã có Unit Test)

---

# Phần XIII

# E2E Test trong CI/CD

Pipeline:

```text
Developer Push Code

↓

GitHub Actions

↓

pytest

↓

Build

↓

Deploy
```

---

Ví dụ:

```yaml
- name: Test

  run:

    pytest tests/
```

---

E2E thường chạy:

* Trước release.
* Nightly build.

---

# Phần XIV

# Sai lầm khi viết E2E Test

## Sai 1

Quá nhiều E2E.

Ví dụ:

10000 E2E test.

Kết quả:

```text
Chạy 5 tiếng
```

---

## Sai 2

Test quá chi tiết.

Ví dụ:

Kiểm tra:

```text
Màu nút
Font chữ
Pixel
```

Không cần.

---

## Sai 3

Phụ thuộc dữ liệu thật.

Ví dụ:

```text
User admin thật
```

Không tốt.

---

# Phần XV

# Chiến lược Testing chuyên nghiệp

Một dự án Python lớn:

```text
tests/

├── unit

│   70%

│

├── integration

│   20%

│

└── e2e

    10%
```

---

Ví dụ:

1000 test:

```text
700 Unit

200 Integration

100 E2E
```

---

# Phần XVI

# Mini Project

## Xây E2E Test cho Blog API

Workflow:

```text
Register User

↓

Login

↓

Create Post

↓

Read Post

↓

Delete Post
```

---

Test:

```python
def test_blog_flow(client):

    register()

    token = login()

    post = create_post(token)

    result = get_post(post.id)

    assert result.title == "Hello"
```

---

Đây chính là cách QA Engineer test sản phẩm thật.

---

# Bài tập

## Bài 1

Viết E2E test:

```text
User Register
```

---

## Bài 2

Viết E2E:

```text
Login → Dashboard
```

---

## Bài 3

Tạo:

```text
Page Object Model
```

cho trang Login.

---

## Bài 4

Viết CLI E2E Test:

```bash
crawler start
```

---

## Bài 5

Thiết kế E2E Workflow:

Ứng dụng:

```
Story Crawler
```

---

# Tổng kết Buổi 35

Bạn đã học:

✅ E2E Testing
✅ Functional Testing
✅ Unit vs Integration vs E2E
✅ API E2E Test
✅ CLI Testing
✅ Browser Testing
✅ Selenium
✅ Playwright
✅ Page Object Model
✅ Workflow Testing
✅ CI/CD Testing Strategy

---

# Góc nhìn lập trình viên chuyên nghiệp

Một hệ thống Python hiện đại thường có:

```
              User

               |
               |

             E2E

               |

            API/UI

               |

        Integration

               |

          Services

               |

            Unit
```

Mỗi tầng có nhiệm vụ riêng.

Một lập trình viên senior không chỉ viết code chạy được.

Họ xây dựng:

* Code dễ test.
* Architecture dễ thay thế.
* Dependency rõ ràng.
* Pipeline kiểm thử tự động.

---

# Chuẩn bị Buổi 36

**Pytest (Phần 8) – Test Coverage, pytest-cov và chất lượng mã nguồn**

Nội dung:

* Code Coverage là gì?
* Branch Coverage.
* pytest-cov.
* Coverage Report HTML.
* Coverage trong CI/CD.
* Đánh giá chất lượng test.
* Những lỗi khi chạy theo % coverage.
* Chiến lược đạt 80–90% coverage thực tế.
