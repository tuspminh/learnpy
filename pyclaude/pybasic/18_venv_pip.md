### Bài 18: Quản lý môi trường ảo, pip và Dependency

Đây là bài học đánh dấu bước chuyển từ "viết script cá nhân" sang **"xây dựng phần mềm có thể chia sẻ, triển khai (deploy), và duy trì lâu dài"** — kỹ năng bắt buộc với mọi dev Python chuyên nghiệp, dù làm web, data, hay AI.

---

#### 1. Vấn đề thực tế: Tại sao không thể cài package "thẳng vào máy"?

Khi mới học, người ta thường làm:

bash

```bash
pip install requests
pip install pandas
pip install django
```

Điều này cài package vào **Python toàn cục (global)** của máy — nghe tiện, nhưng gây ra vấn đề nghiêm trọng khi làm nhiều project:

**Tình huống thực tế rất phổ biến:**

- Project A (viết năm 2024) cần `django==4.2` (phiên bản cũ, ổn định với code cũ)
- Project B (viết năm 2026) cần `django==5.1` (phiên bản mới, có tính năng mới)
- Nếu cả hai đều cài vào Python toàn cục → **xung đột phiên bản (dependency conflict)** — cài bản mới sẽ ghi đè bản cũ, làm Project A ngừng hoạt động

Đây chính là bài toán mà **môi trường ảo (virtual environment)** ra đời để giải quyết: **mỗi project có một "hộp cách ly" riêng**, chứa đúng phiên bản Python + package mà project đó cần, hoàn toàn độc lập với project khác và với hệ thống máy.

---

#### 2. `venv` — Công cụ chính thức tạo môi trường ảo

Python có sẵn module `venv` (built-in từ Python 3.3+), không cần cài thêm gì.

**Bước 1 — Tạo môi trường ảo:**

bash

```bash
# Cấu trúc: python -m venv <tên_thư_mục_môi_trường>
python -m venv venv
```

Lệnh này tạo ra một thư mục tên `venv` (tên phổ biến theo quy ước, có thể đặt tên khác như `.venv`, `env`) chứa một bản Python + pip **độc lập**, hoàn toàn tách biệt với Python hệ thống.

**Bước 2 — Kích hoạt (activate) môi trường ảo:**

bash

```bash
# macOS / Linux
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

Sau khi activate, terminal của bạn sẽ hiện tiền tố `(venv)` phía trước dòng lệnh:

bash

```bash
(venv) user@laptop:~/my_project$
```

Đây là dấu hiệu **quan trọng** cho biết bạn đang làm việc *bên trong* môi trường ảo — mọi lệnh `pip install` từ giờ chỉ ảnh hưởng project này, không đụng đến máy hay project khác.

**Bước 3 — Kiểm tra đang dùng Python nào:**

bash

```bash
which python      # macOS/Linux
where python       # Windows
```

Kết quả sẽ chỉ vào đường dẫn bên trong thư mục `venv/`, xác nhận bạn đang dùng Python "cách ly" chứ không phải Python hệ thống.

**Bước 4 — Thoát môi trường ảo khi xong việc:**

bash

```bash
deactivate
```

---

#### 3. `pip` — Trình quản lý package của Python

`pip` (Package Installer for Python) là công cụ để cài đặt thư viện bên thứ ba từ **PyPI** (Python Package Index — kho lưu trữ package chính thức, tương tự npm cho JavaScript).

bash

```bash
pip install requests                # cài phiên bản mới nhất
pip install requests==2.31.0        # cài phiên bản CHÍNH XÁC (khuyến nghị cho production)
pip install "requests>=2.28,<3.0"   # cài trong khoảng phiên bản (version range)

pip install --upgrade requests      # nâng cấp package đã cài
pip uninstall requests               # gỡ package

pip show requests                    # xem thông tin chi tiết (phiên bản, dependency của nó...)
pip list                             # xem toàn bộ package đã cài trong môi trường hiện tại
```

**Ứng dụng thực tế 2026** — các package bạn sẽ dùng thường xuyên tùy hướng đi:

bash

```bash
pip install requests           # gọi HTTP API
pip install pandas numpy       # phân tích dữ liệu
pip install fastapi uvicorn    # xây dựng REST API hiện đại
pip install pytest             # viết unit test (Bài 21)
pip install anthropic          # gọi API của Claude
```

---

#### 4. `requirements.txt` — "Danh sách nguyên liệu" của project

Đây là file **quan trọng bậc nhất** để chia sẻ project với người khác hoặc deploy lên server — nó ghi lại chính xác project cần package nào, phiên bản nào.

**Tạo file từ môi trường hiện tại:**

bash

```bash
pip freeze > requirements.txt
```

Kết quả file `requirements.txt` trông như:

```
requests==2.31.0
pandas==2.2.1
numpy==1.26.4
python-dotenv==1.0.1
```

**Cài lại toàn bộ dependency từ file này** (ví dụ khi đồng nghiệp clone code của bạn, hoặc khi deploy lên server production):

bash

```bash
pip install -r requirements.txt
```

**Quy trình chuẩn ngành khi làm việc nhóm hoặc deploy thực tế:**

bash

```bash
git clone https://github.com/congty/du-an-abc.git
cd du-an-abc
python -m venv venv
source venv/bin/activate       # hoặc lệnh Windows tương ứng
pip install -r requirements.txt
python main.py
```

Đây chính xác là quy trình **bất kỳ dev Python nào** cũng thực hiện khi bắt đầu làm việc trên một codebase mới — kể cả khi bạn tải một project mã nguồn mở từ GitHub về chạy thử.

---

#### 5. `.gitignore` — Không commit môi trường ảo lên Git

Một sai lầm rất phổ biến của người mới: đưa cả thư mục `venv/` (có thể nặng hàng trăm MB) lên Git repository. Điều này **không cần thiết và sai nguyên tắc** — vì `requirements.txt` đã đủ để bất kỳ ai tái tạo lại chính xác môi trường đó.

Tạo file `.gitignore` trong thư mục gốc project:

```
venv/
.venv/
__pycache__/
*.pyc
.env
```

**Nguyên tắc**: Git nên chỉ chứa **code**, không chứa **môi trường thực thi**. Môi trường luôn có thể tái tạo lại từ `requirements.txt` — đây là triết lý cốt lõi của quản lý dependency chuyên nghiệp.

---

#### 6. `pyproject.toml` và các công cụ hiện đại — chuẩn 2026

`requirements.txt` vẫn phổ biến, nhưng cộng đồng Python hiện đại (2025-2026) đang dịch chuyển mạnh sang các công cụ quản lý dependency toàn diện hơn, giải quyết luôn cả vấn đề "resolve version conflict" mà `pip` thuần không làm tốt:

**`uv`** — công cụ được viết bằng Rust, nổi lên mạnh mẽ vì tốc độ cực nhanh (nhanh hơn `pip` hàng chục đến hàng trăm lần):

bash

```bash
pip install uv                      # cài uv (chỉ cần 1 lần)

uv venv                             # tạo môi trường ảo, nhanh hơn venv chuẩn
uv pip install requests             # cài package, tốc độ vượt trội
uv add pandas                       # thêm dependency, tự cập nhật pyproject.toml
```

**`poetry`** — công cụ quản lý dependency + đóng gói (packaging) toàn diện, phổ biến trong các team chuyên nghiệp:

bash

```bash
poetry init                # tạo pyproject.toml
poetry add requests        # thêm dependency
poetry install              # cài toàn bộ dependency đã khai báo
poetry shell                 # kích hoạt môi trường ảo do poetry quản lý
```

Cả hai công cụ này dùng file `pyproject.toml` thay cho `requirements.txt` — một file cấu hình toàn diện hơn (khai báo cả metadata project, dependency, cấu hình build...):

toml

```toml
[project]
name = "he-thong-quan-ly-don-hang"
version = "0.1.0"
dependencies = [
    "requests>=2.31.0",
    "pandas>=2.2.0",
    "fastapi>=0.110.0"
]
```

**Lời khuyên thực chiến**: với người mới, hãy thành thạo `venv` + `pip` + `requirements.txt` trước (đây vẫn là kiến thức nền tảng bắt buộc, xuất hiện trong hầu hết codebase cũ và tài liệu học tập). Sau khi vững, chuyển sang `uv` hoặc `poetry` sẽ rất tự nhiên vì bản chất vấn đề chúng giải quyết là giống nhau — chỉ khác ở cách thực hiện gọn gàng hơn.

---

#### 7. Semantic Versioning — hiểu ý nghĩa số phiên bản

Khi thấy `requests==2.31.0`, con số này tuân theo chuẩn **Semantic Versioning (SemVer)**: `MAJOR.MINOR.PATCH`

```
2    .  31   .   0
MAJOR   MINOR    PATCH
```

- **MAJOR** (2): thay đổi lớn, có thể **phá vỡ** code cũ (breaking change)
- **MINOR** (31): thêm tính năng mới, **tương thích ngược** (không phá code cũ)
- **PATCH** (0): sửa lỗi nhỏ, **hoàn toàn tương thích**

Hiểu quy ước này giúp bạn quyết định độ "chặt" khi khai báo version:

```
requests==2.31.0      # CHÍNH XÁC phiên bản này - an toàn nhất cho production, nhưng cần cập nhật thủ công
requests~=2.31        # cho phép patch update (2.31.x) - cân bằng an toàn và cập nhật
requests>=2.28,<3.0   # cho phép minor update trong MAJOR version 2 - linh hoạt hơn
```

**Nguyên tắc thực chiến**: trong môi trường **production** (hệ thống đang chạy thực tế phục vụ người dùng), luôn ghim (pin) version chính xác (`==`) để tránh việc một bản cập nhật package bất ngờ làm hỏng hệ thống mà không ai kiểm soát được thời điểm.

---

#### 8. Ví dụ thực chiến tổng hợp — Khởi tạo một project chuẩn chuyên nghiệp

bash

```bash
# 1. Tạo thư mục project
mkdir he-thong-quan-ly-don-hang
cd he-thong-quan-ly-don-hang

# 2. Tạo môi trường ảo
python -m venv venv

# 3. Kích hoạt
source venv/bin/activate    # macOS/Linux

# 4. Cài dependency cần thiết
pip install requests pandas python-dotenv

# 5. Ghi lại dependency
pip freeze > requirements.txt

# 6. Tạo .gitignore
echo "venv/
__pycache__/
.env" > .gitignore

# 7. Khởi tạo git
git init
git add .
git commit -m "Khởi tạo project với môi trường ảo và dependency"
```

Cấu trúc thư mục kết quả:

```
he-thong-quan-ly-don-hang/
├── venv/                  # KHÔNG commit lên Git
├── requirements.txt       # CÓ commit - đây là "công thức" tái tạo môi trường
├── .gitignore
└── main.py
```

Đây chính xác là bộ khung khởi đầu của **bất kỳ project Python chuyên nghiệp nào** — từ một script nhỏ đến hệ thống backend phức tạp.

---

#### 🎯 Bài tập thực hành

Thực hiện trên máy của bạn (không phải viết code Python thuần, mà là thực hành dùng terminal — kỹ năng vận hành thực tế):

1. Tạo một thư mục project mới tên `bai_tap_18`
2. Tạo môi trường ảo bằng `venv`, kích hoạt nó, xác nhận bằng `which python` / `where python`
3. Cài 3 package: `requests`, `python-dotenv`, `rich` (một thư viện làm đẹp output terminal)
4. Chạy `pip list` để xem toàn bộ package đã cài (chú ý: `rich` và `requests` có thể tự kéo theo các package phụ thuộc khác — đây là dependency của dependency)
5. Xuất ra file `requirements.txt` bằng `pip freeze`
6. Viết một file `test_moi_truong.py` đơn giản:

python

```python
   import requests
   from rich import print as rprint

   rprint("[bold green]Môi trường ảo đã hoạt động chính xác![/bold green]")
   print(f"Phiên bản requests: {requests.__version__}")
```

Chạy file này để xác nhận package đã cài hoạt động đúng trong môi trường ảo  
7. Thử thách thêm: tạo `.gitignore` phù hợp, sau đó `deactivate` môi trường ảo và thử chạy lại `test_moi_truong.py` — quan sát lỗi `ModuleNotFoundError` xảy ra (vì giờ bạn đang dùng Python hệ thống, không có `requests`/`rich` được cài ở đó) để khắc sâu vì sao môi trường ảo quan trọng

Làm xong báo tôi kết quả (không cần gửi code dài, chỉ cần xác nhận các bước chạy thành công hoặc lỗi gặp phải). Sau đó ta sang **Bài 19: Làm việc với API (requests, HTTP)** — nơi bạn sẽ dùng chính package `requests` vừa cài để gọi các API thực tế (thời tiết, thanh toán, AI...), áp dụng trực tiếp kiến thức dict lồng nhau từ Bài 8 để xử lý JSON response.
