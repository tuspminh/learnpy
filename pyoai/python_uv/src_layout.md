Nếu bạn đang học Python theo hướng **project chuyên nghiệp**, thì `src layout` rất đáng học vì nó giải quyết một vấn đề quan trọng: **tránh vô tình import code từ source tree thay vì package đã được cài đặt**.

# 1. `src layout` là gì?

Thay vì tổ chức project như:

```text
myapp/
├── pyproject.toml
├── README.md
├── myapp/
│   ├── __init__.py
│   ├── main.py
│   └── services.py
└── tests/
```

ta tổ chức:

```text
myapp/
├── pyproject.toml
├── README.md
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── main.py
│       └── services.py
└── tests/
    └── test_services.py
```

Điểm quan trọng nhất:

```text
src/
└── myapp/
```

`src` **không phải package**.

Package thực sự là:

```text
myapp
```

---

# 2. Tại sao phải dùng `src`?

Hãy xem project truyền thống:

```text
myapp/
├── pyproject.toml
├── myapp/
│   └── service.py
└── tests/
```

Bạn đứng tại thư mục project:

```bash
python
```

rồi:

```python
from myapp.service import UserService
```

Python có thể tìm thấy:

```text
./myapp/
```

ngay lập tức.

Điều này đôi khi tạo ra **ảo giác rằng package đã được đóng gói/cài đặt đúng**, trong khi thực tế chưa chắc.

Với `src layout`:

```text
myapp/
├── pyproject.toml
├── src/
│   └── myapp/
│       └── service.py
└── tests/
```

nếu chưa cài package:

```bash
python
```

thì:

```python
from myapp.service import UserService
```

thường sẽ **không import được**.

Muốn import đúng:

```bash
pip install -e .
```

hoặc:

```bash
uv sync
```

Sau đó:

```python
from myapp.service import UserService
```

mới hoạt động.

Đây chính là một ưu điểm rất lớn của `src layout`:

> **Ép bạn sử dụng package theo cách gần với cách người dùng thật sự cài đặt package.**

---

# 3. Một project `src layout` chuẩn

Ví dụ ta xây dựng project:

```text
task-manager/
```

Cấu trúc:

```text
task-manager/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
│
├── src/
│   └── task_manager/
│       ├── __init__.py
│       ├── domain/
│       │   ├── __init__.py
│       │   └── task.py
│       │
│       ├── application/
│       │   ├── __init__.py
│       │   └── task_service.py
│       │
│       └── infrastructure/
│           ├── __init__.py
│           └── task_repository.py
│
└── tests/
    ├── __init__.py
    ├── test_task.py
    └── test_task_service.py
```

Đây là cấu trúc rất phù hợp với hướng bạn đang học:

```text
src/
└── package/
    ├── domain/
    ├── application/
    └── infrastructure/
```

Sau này có thể kết hợp rất tốt với:

* Clean Architecture
* DDD
* Repository Pattern
* SOLID
* Dependency Injection
* CLI application
* package/library development

---

# 4. `pyproject.toml` đóng vai trò gì?

Ví dụ:

```toml
[project]
name = "task-manager"
version = "0.1.0"
description = "A task manager"
requires-python = ">=3.12"
dependencies = []
```

Ở đây:

```toml
name = "task-manager"
```

là **tên distribution/package project**.

Còn:

```text
src/task_manager/
```

là Python import package.

Hai cái có thể giống nhau nhưng **không bắt buộc phải giống**.

Ví dụ:

```toml
name = "my-awesome-project"
```

nhưng:

```text
src/
└── awesome/
    └── __init__.py
```

thì:

```python
import awesome
```

---

# 5. Cài project

Với project `src layout`, bạn thường đứng ở:

```text
task-manager/
```

và chạy:

```bash
pip install -e .
```

`-e` nghĩa là:

```text
editable install
```

Sau đó:

```text
task-manager/
├── src/
│   └── task_manager/
└── ...
```

được cài vào environment.

Bạn có thể:

```python
from task_manager.domain.task import Task
```

---

# 6. `-e` cực kỳ quan trọng khi development

Nếu dùng:

```bash
pip install .
```

Python cài package vào environment.

Nếu bạn sửa:

```text
src/task_manager/domain/task.py
```

thì package đã cài **không nhất thiết phản ánh source hiện tại** theo cách development mong muốn.

Trong khi:

```bash
pip install -e .
```

tạo editable installation.

Ý tưởng:

```text
Python environment
        │
        ▼
   task_manager
        │
        ▼
src/task_manager/
```

Bạn sửa:

```text
src/task_manager/...
```

thì Python sử dụng code mới.

Đây là cách rất phổ biến khi phát triển library/application package.

---

# 7. Với `uv`

Vì bạn vừa hỏi về `uv`, `src layout` kết hợp với `uv` rất đẹp.

Tạo project:

```bash
uv init --package task-manager
```

Sau đó cấu trúc có thể là:

```text
task-manager/
├── pyproject.toml
├── README.md
├── src/
│   └── task_manager/
│       └── __init__.py
└── ...
```

Sau đó:

```bash
uv sync
```

`uv` sẽ quản lý environment và cài project vào environment theo cấu hình trong `pyproject.toml`.

Chạy:

```bash
uv run python
```

rồi:

```python
from task_manager import ...
```

---

# 8. `src` không phải magic folder

Một hiểu lầm phổ biến:

> "Python tự động hiểu thư mục `src`."

Không.

Python không có quy tắc đặc biệt kiểu:

```text
src/
```

là tự động import.

`src` chỉ là **convention**.

Cái quyết định package nào được cài là **build system / packaging configuration**.

Ví dụ:

```text
src/
└── task_manager/
```

Packaging tool sẽ được cấu hình để biết:

```text
package nằm trong src/
```

---

# 9. Import hoạt động thế nào?

Giả sử:

```text
project/
├── pyproject.toml
└── src/
    └── calculator/
        ├── __init__.py
        └── math.py
```

Trong `math.py`:

```python
def add(a: int, b: int) -> int:
    return a + b
```

Sau khi package được cài:

```python
from calculator.math import add

print(add(1, 2))
```

Kết quả:

```text
3
```

Chú ý:

```python
from src.calculator.math import add
```

**không phải cách import đúng**.

Không nên coi:

```text
src
```

là một phần của package name.

---

# 10. `tests` nằm ngoài `src`

Đây cũng là một convention quan trọng:

```text
project/
├── src/
│   └── calculator/
│       ├── __init__.py
│       └── math.py
│
└── tests/
    └── test_math.py
```

Không nên:

```text
src/
├── calculator/
└── tests/
```

trừ khi bạn có lý do đặc biệt.

Mục tiêu là phân biệt:

```text
production code
        ↓
src/

test code
        ↓
tests/
```

---

# 11. Chạy test

Ví dụ:

```text
tests/test_math.py
```

```python
from calculator.math import add


def test_add():
    assert add(2, 3) == 5
```

Sau khi:

```bash
uv sync
```

có thể chạy:

```bash
uv run pytest
```

Điều rất hay ở đây là test đang kiểm tra package theo môi trường đã được cài đặt.

Nó gần với thực tế hơn.

---

# 12. CLI với `src layout`

Ví dụ bạn muốn xây CLI:

```bash
task-manager add "Learn Python"
```

Trong:

```text
src/task_manager/cli.py
```

có:

```python
def main():
    print("Task Manager")
```

Trong `pyproject.toml`:

```toml
[project.scripts]
task-manager = "task_manager.cli:main"
```

Sau đó:

```bash
uv sync
```

Bạn có thể:

```bash
uv run task-manager
```

và:

```text
Task Manager
```

Đây là một điểm cực kỳ quan trọng nếu bạn đang xây các CLI framework/project như những project bạn đã học.

---

# 13. `src layout` + Clean Architecture

Nếu áp dụng vào project crawler của bạn, có thể tổ chức:

```text
novel-crawler/
│
├── pyproject.toml
│
├── src/
│   └── novel_crawler/
│       │
│       ├── domain/
│       │   ├── entities/
│       │   ├── value_objects/
│       │   ├── repositories/
│       │   └── services/
│       │
│       ├── application/
│       │   ├── use_cases/
│       │   └── dto/
│       │
│       ├── infrastructure/
│       │   ├── database/
│       │   ├── repositories/
│       │   ├── crawler/
│       │   └── http/
│       │
│       └── presentation/
│           └── cli/
│
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

Đây là nơi `src layout` thực sự phát huy tác dụng.

Nó tạo ra ranh giới rõ:

```text
project root
    │
    ├── src/       → production package
    │
    ├── tests/     → test
    │
    └── pyproject.toml → packaging/configuration
```

---

# 14. Một nguyên tắc rất đáng nhớ

Hãy phân biệt 3 khái niệm:

### Project

```text
task-manager/
```

### Source directory

```text
src/
```

### Python package

```text
src/task_manager/
```

và:

### Import name

```python
import task_manager
```

### Distribution name

```toml
name = "task-manager"
```

Có thể hình dung:

```text
task-manager/              ← project/distribution
│
├── pyproject.toml
│
└── src/
    │
    └── task_manager/      ← Python package
        │
        ├── __init__.py
        ├── domain/
        ├── application/
        └── infrastructure/
```

---

# 15. Khi nào nên dùng `src layout`?

Tôi khuyên bạn **nên dùng ngay từ bây giờ** nếu project có một trong các đặc điểm:

* project có nhiều module
* dùng `pyproject.toml`
* dùng `uv`
* có test
* xây CLI
* xây library
* muốn publish package
* Clean Architecture
* DDD
* Repository Pattern
* plugin architecture
* project crawler/worker

Với các script nhỏ:

```text
hello.py
```

thì không cần.

---

# 16. Quy trình chuẩn tôi khuyên bạn dùng

Với project Python hiện đại:

```text
1. Tạo project
       ↓
2. src layout
       ↓
3. pyproject.toml
       ↓
4. uv quản lý environment
       ↓
5. editable install
       ↓
6. tests/
       ↓
7. package import
       ↓
8. CLI / library
```

Ví dụ:

```bash
uv init --package myapp
cd myapp
uv sync
```

Sau đó:

```bash
uv run pytest
```

và nếu có CLI:

```bash
uv run myapp
```

---

## Một điểm rất quan trọng

`src layout` không đơn thuần là:

> "đặt code vào thư mục `src`."

Tư duy đúng phải là:

> **Source code là một Python package được packaging và cài đặt vào environment; `src` giúp ngăn project root vô tình đóng vai trò như package environment.**

Đây là nền tảng rất tốt trước khi đi sâu vào **Python Packaging → `pyproject.toml` → build backend → wheel/sdist → editable install → dependency → CLI entry point → publish package**.

Nếu học theo kiểu **deep dive**, tôi đề xuất học `src layout` thành một chuỗi khoảng **6–8 buổi**, bắt đầu từ import mechanism rồi đi đến `uv + pyproject.toml + pytest + build wheel`, thay vì chỉ học cách tạo thư mục.
