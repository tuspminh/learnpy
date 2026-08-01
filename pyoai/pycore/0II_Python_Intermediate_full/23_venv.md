# Buổi 23. Virtual Environment (Deep Dive)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ hiểu:
>
> * Virtual Environment là gì và tại sao phải dùng.
> * Cách tạo và kích hoạt môi trường ảo bằng `venv`.
> * Cách quản lý package với `pip`.
> * `requirements.txt` dùng để làm gì.
> * Cách cô lập (isolate) các dự án.
> * Best Practices khi làm việc với môi trường Python.
> * Quy trình chuẩn khi bắt đầu một dự án Python mới.

---

# 1. Tại sao cần Virtual Environment?

Giả sử bạn có hai dự án:

```text
Project_A
Project_B
```

`Project_A` cần:

```text
requests==2.28
```

`Project_B` cần:

```text
requests==2.32
```

Nếu cài trực tiếp vào Python toàn cục (global):

```bash
pip install requests
```

Thì chỉ có **một phiên bản** được cài.

Điều này dễ gây:

* Xung đột phiên bản (dependency conflict).
* Lỗi khi chạy dự án cũ.
* Khó tái tạo môi trường trên máy khác.

---

# 2. Virtual Environment là gì?

Virtual Environment (môi trường ảo) là một **thư mục chứa một bản sao môi trường Python**, bao gồm:

* Python interpreter.
* Thư mục `site-packages`.
* Các package đã cài riêng cho dự án.
* Script kích hoạt môi trường.

Mỗi dự án có môi trường riêng.

Ví dụ:

```text
Project_A/
│
├── .venv/
└── main.py
```

```text
Project_B/
│
├── .venv/
└── app.py
```

Hai dự án không ảnh hưởng lẫn nhau.

---

# 3. `venv` là gì?

`venv` là module có sẵn từ Python 3.

Không cần cài thêm.

Tạo môi trường:

```bash
python -m venv .venv
```

Hoặc:

```bash
python3 -m venv .venv
```

Sau khi chạy:

```text
my_project/

    .venv/

    main.py
```

---

# 4. Cấu trúc của `.venv`

Ví dụ (Linux/macOS):

```text
.venv/

    bin/

    include/

    lib/

    pyvenv.cfg
```

Windows:

```text
.venv/

    Scripts/

    Lib/

    pyvenv.cfg
```

Trong đó:

* `Scripts/` hoặc `bin/`: chứa Python và lệnh kích hoạt.
* `Lib/site-packages/`: nơi cài các package.
* `pyvenv.cfg`: thông tin cấu hình môi trường.

---

# 5. Kích hoạt môi trường

## Windows (CMD)

```cmd
.venv\Scripts\activate
```

## Windows (PowerShell)

```powershell
.venv\Scripts\Activate.ps1
```

## Linux/macOS

```bash
source .venv/bin/activate
```

Sau khi kích hoạt, dấu nhắc lệnh thường có tiền tố:

```text
(.venv)
```

Điều này cho biết bạn đang làm việc trong môi trường ảo.

---

# 6. Thoát môi trường

Chỉ cần:

```bash
deactivate
```

---

# 7. Kiểm tra Python đang sử dụng

Trong môi trường:

```bash
python --version
```

Kiểm tra đường dẫn:

```bash
python -c "import sys; print(sys.executable)"
```

Ví dụ:

```text
/home/user/project/.venv/bin/python
```

Hoặc trên Windows:

```text
C:\Project\.venv\Scripts\python.exe
```

Điều này xác nhận bạn đang dùng Python của môi trường ảo.

---

# 8. `pip`

`pip` là trình quản lý package của Python.

Ví dụ:

```bash
pip install requests
```

Cài:

```text
requests
urllib3
certifi
charset-normalizer
idna
```

Nếu môi trường ảo đang kích hoạt, các package này chỉ được cài vào `.venv`.

---

# 9. Cài package

Ví dụ:

```bash
pip install requests
```

Hoặc:

```bash
pip install flask
```

Cài nhiều package:

```bash
pip install requests beautifulsoup4 lxml
```

---

# 10. Xem package đã cài

```bash
pip list
```

Ví dụ:

```text
Package     Version
----------- -------
requests    2.32.0
Flask       3.x.x
```

Xem chi tiết:

```bash
pip show requests
```

---

# 11. Gỡ package

```bash
pip uninstall requests
```

---

# 12. `requirements.txt`

Đây là tệp ghi lại các package cần thiết cho dự án.

Tạo:

```bash
pip freeze > requirements.txt
```

Ví dụ:

```text
Flask==3.1.0
requests==2.32.0
beautifulsoup4==4.13.0
```

---

# 13. Cài từ `requirements.txt`

Trên máy khác:

```bash
pip install -r requirements.txt
```

Python sẽ cài đúng các phiên bản đã ghi.

Đây là cách phổ biến để chia sẻ dự án.

---

# 14. `pip freeze` và `pip list`

Ví dụ:

```bash
pip list
```

Hiển thị:

```text
Flask
requests
click
```

Trong khi:

```bash
pip freeze
```

Hiển thị:

```text
click==8.1.7
Flask==3.1.0
requests==2.32.0
```

`pip freeze` phù hợp để tạo `requirements.txt` vì có cả số phiên bản.

---

# 15. Cập nhật package

```bash
pip install --upgrade requests
```

Hoặc:

```bash
pip install -U requests
```

---

# 16. Xóa môi trường ảo

Không cần lệnh đặc biệt.

Chỉ cần:

```text
Xóa thư mục .venv
```

Ví dụ:

```bash
rm -rf .venv
```

Hoặc trên Windows:

```cmd
rmdir /S .venv
```

Sau đó có thể tạo lại bằng:

```bash
python -m venv .venv
pip install -r requirements.txt
```

---

# 17. Thực hành: Tạo dự án mới

```text
student_manager/

    .venv/

    main.py

    requirements.txt
```

### Bước 1

```bash
mkdir student_manager
cd student_manager
```

### Bước 2

```bash
python -m venv .venv
```

### Bước 3

Kích hoạt môi trường.

### Bước 4

```bash
pip install requests
```

### Bước 5

```python
# main.py
import requests

print(requests.__version__)
```

### Bước 6

```bash
pip freeze > requirements.txt
```

---

# 18. Không nên đưa `.venv` vào Git

Cấu trúc:

```text
project/

    .venv/

    main.py

    .gitignore
```

`.gitignore`

```text
.venv/
__pycache__/
*.pyc
```

Lý do:

* Dung lượng lớn.
* Có thể tạo lại từ `requirements.txt`.
* Phụ thuộc hệ điều hành.

---

# 19. Best Practices

## ✔ Đặt tên môi trường là `.venv`

```text
project/

    .venv/
```

Nhiều IDE như VS Code, PyCharm tự nhận diện.

---

## ✔ Mỗi dự án một môi trường

Không dùng chung một môi trường cho nhiều dự án.

---

## ✔ Luôn có `requirements.txt`

Giúp đồng đội hoặc máy khác tái tạo môi trường dễ dàng.

---

## ✔ Không cài package vào Python toàn cục

Ưu tiên:

```bash
python -m venv .venv
```

rồi mới:

```bash
pip install ...
```

---

## ✔ Dùng `python -m pip`

Thay vì:

```bash
pip install requests
```

Nên dùng:

```bash
python -m pip install requests
```

Lợi ích:

* Đảm bảo `pip` thuộc đúng interpreter đang dùng.
* Tránh nhầm lẫn khi máy có nhiều phiên bản Python.

---

# 20. Các công cụ liên quan

Ngoài `venv`, bạn sẽ gặp:

| Công cụ      | Mục đích                                                     |
| ------------ | ------------------------------------------------------------ |
| `venv`       | Môi trường ảo chuẩn của Python                               |
| `virtualenv` | Công cụ cũ hơn, nhiều tính năng hơn                          |
| `pip`        | Quản lý package                                              |
| `pip-tools`  | Quản lý dependency nâng cao                                  |
| `poetry`     | Quản lý package và môi trường                                |
| `uv`         | Công cụ hiện đại, rất nhanh để quản lý môi trường và package |
| `conda`      | Môi trường và package cho khoa học dữ liệu                   |

Đối với đa số dự án Python thông thường, **`venv` + `pip`** là lựa chọn phù hợp và đủ mạnh.

---

# 21. Quy trình chuẩn khi bắt đầu dự án Python

```text
Tạo thư mục dự án
        │
        ▼
python -m venv .venv
        │
        ▼
Kích hoạt .venv
        │
        ▼
python -m pip install <package>
        │
        ▼
Viết mã nguồn
        │
        ▼
python -m pip freeze > requirements.txt
        │
        ▼
Thêm .venv vào .gitignore
        │
        ▼
Đưa mã nguồn lên Git
```

Đây là quy trình được sử dụng trong hầu hết các dự án Python chuyên nghiệp.

---

# Tổng kết

Sau buổi học này, bạn đã nắm được:

* Khái niệm và lợi ích của Virtual Environment.
* Cách tạo, kích hoạt và xóa môi trường ảo với `venv`.
* Quản lý package bằng `pip`.
* Tạo và sử dụng `requirements.txt`.
* Các thực hành tốt như không đưa `.venv` lên Git và sử dụng `python -m pip`.

## Bài tập thực hành

1. Tạo một dự án mới tên `hello_python`, tạo môi trường `.venv`, kích hoạt và kiểm tra `sys.executable`.
2. Cài `requests` và `rich`, sau đó viết chương trình in phiên bản của hai thư viện này.
3. Tạo `requirements.txt` bằng `pip freeze`, xóa môi trường `.venv`, tạo lại và cài đặt từ `requirements.txt`.
4. Tạo `.gitignore` để loại trừ `.venv`, `__pycache__` và các tệp `*.pyc`.
5. Thử cài thêm một package khác (ví dụ `httpx`), quan sát sự thay đổi của `requirements.txt`.

Ở **Buổi 24**, chúng ta sẽ học **File**, bao gồm đọc/ghi tệp văn bản và nhị phân, xử lý encoding, sử dụng `with`, các chế độ mở tệp (`r`, `w`, `a`, `x`, `b`) và các kỹ thuật đọc ghi hiệu quả trong Python.
