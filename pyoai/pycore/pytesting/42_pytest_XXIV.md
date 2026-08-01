# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 42: Pytest (Phần 14) – Security Testing và kiểm thử bảo mật ứng dụng Python

> **Một ứng dụng có đầy đủ Unit Test vẫn có thể bị hack.**
>
> Unit Test kiểm tra **tính đúng của chức năng**.
>
> Security Test kiểm tra **khả năng chống lại các hành vi bất thường hoặc độc hại**.

Trong các công ty lớn, pipeline CI/CD hiện đại thường có:

```text
Lint
    │
Type Check
    │
Unit Test
    │
Integration Test
    │
Security Test
    │
Dependency Scan
    │
Performance Test
    │
Deploy
```

---

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

* Hiểu Security Testing.
* Biết các nhóm lỗ hổng phổ biến.
* Viết Security Test bằng Pytest.
* Kiểm thử Authentication.
* Kiểm thử Authorization.
* Kiểm thử Input Validation.
* Kiểm thử Upload File.
* Kiểm thử JWT.
* Kiểm thử Rate Limiting.
* Kết hợp Security Test vào CI/CD.

---

# Roadmap

```text
Buổi 29-41
✓ Functional Testing
✓ Architecture Testing
✓ Performance Testing

Buổi 42
✓ Security Testing

Buổi 43
✓ Async Testing

Buổi 44
✓ Plugin Development
```

---

# Phần I

# Security Testing là gì?

Security Testing giúp trả lời các câu hỏi:

```text
Có đăng nhập trái phép được không?

Có truy cập dữ liệu người khác được không?

Có upload file nguy hiểm được không?

Có SQL Injection được không?

Có gửi dữ liệu sai định dạng được không?
```

Nó không chỉ kiểm tra:

```text
Code đúng?
```

mà còn kiểm tra:

```text
Code có an toàn không?
```

---

# Phần II

# Các nhóm kiểm thử bảo mật

Trong thực tế có rất nhiều loại.

Đối với lập trình viên Backend Python, bạn nên thành thạo:

```text
Authentication

Authorization

Input Validation

SQL Injection

Command Injection

Path Traversal

File Upload

Rate Limiting

JWT

Session

API Security
```

---

# Phần III

# Authentication Testing

Ví dụ API:

```text
POST /login
```

---

Test đúng:

```python
response = client.post("/login", json={"username": "admin", "password": "123456"})

assert response.status_code == 200
```

---

Test sai mật khẩu:

```python
response = client.post("/login", json={"username": "admin", "password": "wrong"})

assert response.status_code == 401
```

---

Test user không tồn tại:

```python
response = client.post("/login", json={"username": "unknown", "password": "123"})

assert response.status_code == 401
```

---

Không chỉ test thành công.

Phải test:

* Sai password.
* Sai username.
* Password rỗng.
* Username rỗng.
* JSON sai.
* Thiếu field.

---

# Phần IV

# Authorization Testing

Authentication:

```text
Bạn là ai?
```

Authorization:

```text
Bạn được phép làm gì?
```

---

Ví dụ:

```text
DELETE /users/1
```

Chỉ:

```text
Admin
```

được phép.

---

Test:

```python
response = user_client.delete("/users/1")

assert response.status_code == 403
```

---

Admin:

```python
response = admin_client.delete("/users/1")

assert response.status_code == 200
```

---

Đây là nhóm test rất quan trọng.

---

# Phần V

# Input Validation

Ví dụ:

```python
class UserCreate(BaseModel):
    age: int
```

---

Test:

```python
response = client.post("/users", json={"age": "abc"})

assert response.status_code == 422
```

---

Test:

```python
age = -10
```

Nếu business rule:

```text
age>0
```

phải fail.

---

# Phần VI

# SQL Injection

Sai:

```python
sql = f"SELECT * FROM user WHERE name='{name}'"
```

---

Payload:

```text
' OR 1=1 --
```

---

Test:

```python
payload = {"name": "' OR 1=1 --"}
```

---

Điều cần kiểm tra:

* Không crash.
* Không trả toàn bộ dữ liệu.
* Trả lỗi phù hợp hoặc không có kết quả.

---

Trong Python hiện đại:

* `sqlite3`
* SQLAlchemy
* psycopg

đều nên dùng **parameterized query**.

Ví dụ:

```python
cursor.execute("SELECT * FROM user WHERE name=?", (name,))
```

---

# Phần VII

# Command Injection

Ví dụ:

```python
subprocess.run(f"ping {host}", shell=True)
```

---

Payload:

```text
127.0.0.1 && rm -rf /
```

---

Security Test:

Không kiểm tra xem lệnh có chạy hay không.

Mà kiểm tra:

* Input bị từ chối.
* Không thực thi thêm lệnh.

Giải pháp:

```python
subprocess.run(["ping", host])
```

---

# Phần VIII

# Path Traversal

Ví dụ:

```text
GET

/files/report.txt
```

---

Payload:

```text
../../etc/passwd
```

---

Test:

```python
response = client.get("/files/../../etc/passwd")

assert response.status_code in (400, 403, 404)
```

---

Không được đọc file ngoài thư mục cho phép.

---

# Phần IX

# Upload File Testing

Ví dụ:

```text
POST /upload
```

---

Test:

File hợp lệ:

```text
photo.jpg
```

---

File quá lớn.

---

File:

```text
virus.exe
```

---

File:

```text
shell.php
```

---

Kiểm tra:

* MIME Type.
* Extension.
* Kích thước.
* Nội dung (nếu cần).

---

# Phần X

# JWT Testing

Login:

```text
↓

JWT

↓

API
```

---

Test:

Token đúng.

---

Token hết hạn.

---

Token sai chữ ký.

---

Token bị sửa.

---

Ví dụ:

```python
response = client.get("/profile", headers={"Authorization": "Bearer invalid"})

assert response.status_code == 401
```

---

# Phần XI

# Rate Limiting

Ví dụ:

API:

```text
/login
```

Giới hạn:

```text
5 request/phút
```

---

Test:

```python
for _ in range(10):
    response = client.post("/login")
```

---

Request cuối:

```python
assert response.status_code == 429
```

---

Đây là cách kiểm tra chống brute force.

---

# Phần XII

# Session Testing

Kiểm tra:

Logout.

```text
↓

Session hết hiệu lực.
```

---

Test:

```text
Login

↓

Logout

↓

Truy cập profile
```

---

Kết quả:

```text
401
```

---

# Phần XIII

# Security Test cho FastAPI

Ví dụ:

```python
@app.get("/admin")
```

---

Test:

```python
def test_admin_requires_login():

    response = client.get("/admin")

    assert response.status_code == 401
```

---

Test:

```python
def test_admin_role():

    response = user_client.get("/admin")

    assert response.status_code == 403
```

---

# Phần XIV

# Dependency Security

Ngoài test code.

Cần kiểm tra thư viện.

Ví dụ:

```bash
pip install pip-audit
```

Chạy:

```bash
pip-audit
```

Ví dụ kết quả:

```text
Package

Version

Vulnerability

Fixed Version
```

---

Ngoài ra còn có:

```text
Safety

Dependabot

Renovate
```

---

# Phần XV

# Security Test trong dự án Story Crawler

Giả sử hệ thống:

```text
FastAPI

↓

Crawler

↓

SQLite

↓

Redis

↓

Celery
```

---

Nên có:

### API

* JWT.
* Permission.
* Input Validation.

---

### Downloader

* Chỉ cho phép:

  * http
  * https

Không cho:

```text
file://

ftp://
```

(nếu ứng dụng không hỗ trợ).

---

### File

Kiểm tra:

```text
../../secret.txt
```

---

### Admin

Chỉ:

```text
Role = admin
```

được:

* Crawl.
* Xóa dữ liệu.
* Quản lý người dùng.

---

# Phần XVI

# Tích hợp Security Test vào CI/CD

Pipeline:

```text
ruff

↓

mypy

↓

pytest

↓

pip-audit

↓

benchmark

↓

docker build

↓

deploy
```

Như vậy, mỗi lần commit đều được kiểm tra:

* Chất lượng mã.
* Kiểu dữ liệu.
* Chức năng.
* Hiệu năng.
* Bảo mật phụ thuộc.

---

# Phần XVII

# Sai lầm phổ biến

## 1. Chỉ test đường đi đúng

Sai:

```text
admin

↓

200
```

Không test:

```text
anonymous

↓

401
```

---

## 2. Không test quyền

Ví dụ:

```text
User A

↓

Đọc dữ liệu User B
```

Nếu vẫn thành công:

Lỗi nghiêm trọng.

---

## 3. Tin tưởng dữ liệu từ client

Không bao giờ giả định:

```text
age

email

price

role
```

đều hợp lệ.

---

## 4. Chỉ kiểm tra extension file

Sai:

```text
virus.exe.jpg
```

Ngoài phần mở rộng, cần xác minh loại tệp và xử lý upload an toàn.

---

# Mini Project

Viết Security Test cho:

```text
Book API

↓

JWT

↓

SQLite

↓

Upload Cover Image
```

Các test cần có:

* Login.
* Logout.
* JWT hết hạn.
* JWT sai.
* Upload ảnh hợp lệ.
* Upload file `.exe`.
* User không được xóa sách.
* Admin được xóa sách.
* Input Validation.
* Rate Limiting.

---

# Bài tập

### Bài 1

Viết test:

```text
Login thành công
```

---

### Bài 2

Viết test:

```text
Sai mật khẩu
```

---

### Bài 3

Viết test:

```text
JWT không hợp lệ
```

---

### Bài 4

Viết test:

```text
Upload file .exe
```

---

### Bài 5

Thiết kế Security Test Suite cho dự án Story Crawler.

---

# Tổng kết Buổi 42

Bạn đã học:

* ✅ Security Testing.
* ✅ Authentication Test.
* ✅ Authorization Test.
* ✅ Input Validation.
* ✅ SQL Injection Test.
* ✅ Command Injection Test.
* ✅ Path Traversal Test.
* ✅ File Upload Test.
* ✅ JWT Test.
* ✅ Session Test.
* ✅ Rate Limiting Test.
* ✅ Dependency Security (`pip-audit`).
* ✅ Security Test trong CI/CD.

---

# Góc nhìn Senior Python Developer

Một hệ thống Python hiện đại không chỉ cần:

```text
Code chạy đúng
```

hay:

```text
Code chạy nhanh
```

mà còn phải:

```text
Khó bị khai thác

↓

An toàn trước dữ liệu đầu vào bất thường

↓

Có cơ chế kiểm tra tự động trong CI/CD
```

Trong thực tế, **Security Testing không thay thế Penetration Testing**, nhưng nó giúp phát hiện sớm rất nhiều lỗi bảo mật ngay trong quá trình phát triển.

---

# Chuẩn bị Buổi 43

**Pytest (Phần 15) – Async Testing và kiểm thử ứng dụng bất đồng bộ**

Chúng ta sẽ học:

* `pytest-asyncio`.
* Test `async`/`await`.
* Async Fixture.
* Mock Async Function.
* Test `asyncio.Queue`.
* Test `asyncio.Task`.
* Test Timeout và Cancellation.
* Test `aiohttp`, `httpx.AsyncClient`, WebSocket.
* Kiểm thử Celery, Dramatiq và các workflow bất đồng bộ.

Đây là bước cuối để làm chủ kiểm thử trong các ứng dụng Python hiện đại sử dụng `asyncio`, `FastAPI`, `httpx`, `aiohttp` và các hệ thống xử lý nền.
