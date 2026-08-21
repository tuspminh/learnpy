Nếu bạn muốn học **`uv` thật sâu và dùng nó như công cụ quản lý Python project chuyên nghiệp**, mình đề xuất học theo hướng **từ workflow thực tế → hiểu kiến trúc → dependency → environment → build/package → workspace → CI/CD**.

`uv` hiện là một tool rất mạnh để thay thế/phối hợp nhiều công cụ trước đây như `pip`, `venv`, `pip-tools`, `pipx` và một phần workflow của Poetry/PDM.

---

# 1. `uv` là gì?

`uv` là một Python package/project manager được viết bằng Rust.

Có thể hình dung:

```text
Trước đây:

python
 ├── venv
 ├── pip
 ├── pip-tools
 ├── pipx
 └── poetry/pdm
```

Với `uv`:

```text
uv
 ├── Python installation
 ├── Virtual environment
 ├── Package installation
 ├── Dependency resolution
 ├── Lock file
 ├── Project management
 ├── Tool installation
 ├── Build package
 └── Workspace
```

Ví dụ trước đây:

```bash
python -m venv .venv

source .venv/bin/activate

pip install requests
```

Với `uv`:

```bash
uv venv
uv add requests
```

Thậm chí chạy luôn:

```bash
uv run python main.py
```

Không cần activate `.venv`.

---

# 2. Cài `uv`

## macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Sau đó:

```bash
uv --version
```

Ví dụ:

```text
uv 0.x.x
```

---

## Windows

PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Kiểm tra:

```powershell
uv --version
```

---

# 3. Một cách khác: package manager

Nếu bạn dùng Homebrew:

```bash
brew install uv
```

Windows:

```powershell
winget install --id=astral-sh.uv
```

---

# 4. Tư duy quan trọng nhất về `uv`

Có 4 khái niệm bạn cần phân biệt:

```text
Python
   ↓
Environment
   ↓
Project
   ↓
Dependencies
```

Ví dụ:

```text
my-project/
│
├── pyproject.toml
├── uv.lock
├── .python-version
├── .venv/
│
└── src/
    └── my_project/
```

Trong đó:

### `pyproject.toml`

Khai báo project:

```toml
[project]
name = "my-project"
version = "0.1.0"
dependencies = [
    "requests>=2.32",
]
```

### `uv.lock`

Khóa chính xác dependency tree.

Ví dụ:

```text
my-project
   │
   └── requests
       ├── urllib3
       ├── certifi
       ├── charset-normalizer
       └── idna
```

`uv.lock` ghi lại phiên bản cụ thể để máy khác có thể reproduce environment.

### `.venv`

Virtual environment thực tế.

### `.python-version`

Xác định Python version cho project.

---

# 5. Tạo project đầu tiên

Đây là workflow mình khuyên bạn dùng.

```bash
uv init my-project
```

Sau đó:

```bash
cd my-project
```

Kiểm tra:

```bash
ls
```

Bạn sẽ thấy đại loại:

```text
main.py
pyproject.toml
README.md
```

---

# 6. Chạy project

```bash
uv run python main.py
```

Đây là một trong những lệnh quan trọng nhất của `uv`.

Bạn có thể chạy:

```bash
uv run python
```

hoặc:

```bash
uv run pytest
```

hoặc:

```bash
uv run ruff check .
```

Điểm hay:

```bash
uv run ...
```

sẽ chạy command trong environment của project.

---

# 7. `uv run` khác gì activate `.venv`?

Cách truyền thống:

```bash
source .venv/bin/activate

python main.py
```

Với `uv`:

```bash
uv run python main.py
```

Bạn không bắt buộc phải:

```bash
source .venv/bin/activate
```

Điều này đặc biệt tiện cho:

```bash
CI/CD
Docker
script
automation
```

---

# 8. Tạo virtual environment

Nếu chỉ muốn tạo environment:

```bash
uv venv
```

Kết quả:

```text
.venv/
```

Sau đó:

```bash
uv pip install requests
```

Đây là một workflow khác với project management.

---

# 9. `uv pip` là gì?

`uv` có compatibility layer với `pip`.

Ví dụ:

```bash
uv pip install requests
```

Thay cho:

```bash
pip install requests
```

Xem package:

```bash
uv pip list
```

Freeze:

```bash
uv pip freeze
```

Uninstall:

```bash
uv pip uninstall requests
```

---

# 10. Nhưng project hiện đại nên dùng `uv add`

Nếu bạn đang làm project:

```bash
uv add requests
```

`uv` sẽ cập nhật:

```text
pyproject.toml
uv.lock
```

Ví dụ:

```toml
[project]
dependencies = [
    "requests>=2.32.5",
]
```

Đây là điểm cực kỳ quan trọng.

---

# 11. `uv add`

Cài dependency:

```bash
uv add requests
```

Nhiều package:

```bash
uv add requests beautifulsoup4 lxml
```

Specific version:

```bash
uv add "requests==2.32.5"
```

Minimum version:

```bash
uv add "requests>=2.32"
```

Version range:

```bash
uv add "requests>=2.30,<3"
```

---

# 12. Xóa dependency

```bash
uv remove requests
```

`uv` sẽ cập nhật cả:

```text
pyproject.toml
uv.lock
```

---

# 13. Dev dependencies

Đây là phần rất quan trọng.

Ví dụ project cần:

```text
requests
```

nhưng developer cần:

```text
pytest
ruff
mypy
```

Thêm:

```bash
uv add --dev pytest
uv add --dev ruff
uv add --dev mypy
```

Trong `pyproject.toml` sẽ có nhóm dependency dành cho development.

---

# 14. Ví dụ project thực tế

Giả sử bạn xây crawler.

```bash
uv init novel-crawler
cd novel-crawler
```

Runtime dependencies:

```bash
uv add httpx
uv add beautifulsoup4
uv add lxml
```

Development:

```bash
uv add --dev pytest
uv add --dev ruff
uv add --dev mypy
```

Project:

```text
novel-crawler/
│
├── pyproject.toml
├── uv.lock
├── .python-version
├── .venv/
│
├── src/
│   └── novel_crawler/
│       ├── __init__.py
│       └── crawler.py
│
└── tests/
    └── test_crawler.py
```

Chạy:

```bash
uv run pytest
```

Lint:

```bash
uv run ruff check .
```

---

# 15. `uv sync`

Một lệnh cực kỳ quan trọng:

```bash
uv sync
```

Nó đồng bộ environment với project definition + lock file.

Ví dụ clone project:

```bash
git clone ...
cd project
uv sync
```

Sau đó:

```bash
uv run python main.py
```

Bạn không cần tự:

```bash
python -m venv .venv
pip install ...
```

---

# 16. `uv.lock`

Đây là trái tim của reproducible environment.

Bạn commit:

```text
pyproject.toml
uv.lock
```

vào Git.

Không commit:

```text
.venv/
```

Ví dụ:

```gitignore
.venv/
__pycache__/
*.pyc
```

---

# 17. `uv lock`

Bạn có thể tạo/update lock:

```bash
uv lock
```

Sau đó:

```text
pyproject.toml
      ↓
dependency resolver
      ↓
uv.lock
```

---

# 18. `uv sync` vs `uv lock`

Hiểu rất rõ:

```text
uv lock
```

→ giải dependency và cập nhật lock file.

Còn:

```text
uv sync
```

→ đồng bộ environment theo project/lock.

Workflow:

```bash
uv add httpx
       ↓
pyproject.toml
       ↓
uv.lock
       ↓
.venv
```

---

# 19. Update dependency

Ví dụ:

```bash
uv lock --upgrade
```

Hoặc upgrade một package:

```bash
uv lock --upgrade-package requests
```

Sau đó:

```bash
uv sync
```

---

# 20. Quản lý Python version

Đây là một tính năng rất mạnh của `uv`.

Xem Python hiện có:

```bash
uv python list
```

Cài Python:

```bash
uv python install 3.13
```

Hoặc:

```bash
uv python install 3.12
```

---

# 21. Chọn Python cho project

```bash
uv python pin 3.13
```

Tạo:

```text
.python-version
```

Nội dung đại loại:

```text
3.13
```

Sau này:

```bash
uv run python --version
```

sẽ sử dụng Python version phù hợp với project.

---

# 22. Project yêu cầu Python version

Trong `pyproject.toml`:

```toml
[project]
requires-python = ">=3.12"
```

Hoặc:

```toml
requires-python = ">=3.12,<3.14"
```

Điều này rất quan trọng khi làm library.

---

# 23. Cài Python + tạo project

Bạn có thể làm:

```bash
uv python install 3.13
uv init my-project
cd my-project
uv python pin 3.13
uv sync
```

Workflow hoàn chỉnh:

```text
uv
│
├── Python 3.13
│
├── .venv
│
├── pyproject.toml
│
└── uv.lock
```

---

# 24. `uv tool`

Đây là tính năng mình đặc biệt khuyên bạn học.

Ví dụ muốn dùng:

```bash
ruff
```

nhưng không muốn đưa `ruff` vào project dependency.

Có thể:

```bash
uv tool install ruff
```

Sau đó:

```bash
ruff check .
```

---

# 25. Chạy tool mà không cài vĩnh viễn

Ví dụ:

```bash
uvx ruff check .
```

`uvx` tương đương tư duy:

```text
chạy một Python CLI tool trong isolated environment
```

Ví dụ:

```bash
uvx black .
```

```bash
uvx pytest
```

```bash
uvx httpie
```

---

# 26. `uvx` rất giống `npx`

Nếu bạn biết JavaScript:

```bash
npx some-tool
```

thì có thể hình dung:

```bash
uvx some-tool
```

Ví dụ:

```text
Node.js:

npx ruff-like-tool

Python:

uvx ruff
```

---

# 27. `uv run` vs `uvx`

Đây là điểm rất dễ nhầm.

### `uv run`

Chạy trong **project environment**:

```bash
uv run pytest
```

### `uvx`

Chạy một **CLI tool isolated**:

```bash
uvx ruff
```

Tư duy:

```text
uv run
    ↓
project

uvx
    ↓
standalone tool
```

---

# 28. Scripts

Bạn có thể định nghĩa command trong `pyproject.toml`.

Ví dụ:

```toml
[project.scripts]
crawler = "novel_crawler.cli:main"
```

Sau đó:

```bash
uv run crawler
```

Đây là nền tảng để biến project Python thành CLI application chuyên nghiệp.

Rất phù hợp với những project CLI bạn đang học.

---

# 29. Build package

Cài build dependency:

```bash
uv build
```

Kết quả:

```text
dist/
├── my_project-0.1.0-py3-none-any.whl
└── my_project-0.1.0.tar.gz
```

Có hai dạng:

```text
.whl
```

và:

```text
.tar.gz
```

---

# 30. Install package local

Ví dụ package:

```bash
uv pip install dist/my_project.whl
```

Hoặc test package bằng environment riêng.

---

# 31. Publish package

Sau khi build:

```bash
uv publish
```

Có thể cấu hình credentials/token tùy registry.

Workflow:

```text
source code
    ↓
pyproject.toml
    ↓
uv build
    ↓
dist/
    ↓
PyPI
```

---

# 32. Dependency groups

Khi project lớn, bạn có thể có:

```text
runtime
dev
test
lint
docs
```

Ví dụ:

```text
dependencies
dev
test
docs
```

Sau đó sync group cần thiết.

Đây là một phần mình khuyên học sau khi đã nắm:

```text
uv add
uv remove
uv sync
uv lock
```

---

# 33. Optional dependencies

Một library có thể có:

```text
my-library
```

và optional features:

```text
my-library[http]
my-library[cli]
my-library[all]
```

Trong `pyproject.toml` có thể định nghĩa optional dependency groups.

Ví dụ concept:

```text
my-library
├── core
├── http
├── cli
└── all
```

Đây rất hữu ích khi bạn thiết kế library/framework.

---

# 34. Workspace

Đây là phần advanced.

Giả sử project lớn:

```text
crawler-system/
│
├── pyproject.toml
│
├── packages/
│   ├── crawler-core/
│   ├── crawler-worker/
│   ├── crawler-plugin/
│   └── crawler-cli/
│
└── uv.lock
```

Đây là **monorepo/workspace**.

Các package có thể chia sẻ dependency resolution.

Đặc biệt phù hợp với hệ thống crawler mà bạn đang xây dựng:

```text
crawler-core
      ↑
crawler-worker
      ↑
crawler-plugin
      ↑
crawler-cli
```

---

# 35. `uv` trong Docker

Một pattern rất đẹp:

```dockerfile
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked

COPY . .

CMD ["uv", "run", "python", "main.py"]
```

Điểm quan trọng:

```bash
uv sync --locked
```

đảm bảo Docker environment khớp lock file.

---

# 36. `uv` trong CI/CD

Ví dụ CI:

```bash
uv sync --locked
uv run pytest
```

Sau đó:

```bash
uv run ruff check .
```

Tư duy:

```text
Git clone
    ↓
uv sync --locked
    ↓
tests
    ↓
lint
    ↓
build
```

Không cần script:

```bash
python -m venv ...
pip install ...
```

---

# 37. Workflow mình khuyên bạn dùng

Với Python project mới:

```bash
uv init project
cd project

uv python pin 3.13

uv add httpx
uv add beautifulsoup4

uv add --dev pytest
uv add --dev ruff

uv sync

uv run pytest
uv run ruff check .
uv run python main.py
```

Git:

```bash
git add pyproject.toml uv.lock .python-version
git commit
```

**Không commit `.venv`.**

---

# 38. Cheat Sheet

| Nhu cầu        | Lệnh                |
| -------------- | ------------------- |
| Cài uv         | `uv` installer      |
| Xem version    | `uv --version`      |
| Tạo project    | `uv init`           |
| Tạo venv       | `uv venv`           |
| Cài Python     | `uv python install` |
| Chọn Python    | `uv python pin`     |
| Xem Python     | `uv python list`    |
| Add package    | `uv add`            |
| Remove package | `uv remove`         |
| Sync           | `uv sync`           |
| Lock           | `uv lock`           |
| Upgrade        | `uv lock --upgrade` |
| Chạy command   | `uv run`            |
| Chạy CLI tool  | `uvx`               |
| Cài CLI tool   | `uv tool install`   |
| Build package  | `uv build`          |
| Publish        | `uv publish`        |
| Pip-compatible | `uv pip`            |

---

# 39. Những thứ bạn nên học theo thứ tự

Nếu mục tiêu của bạn là **làm Python chuyên nghiệp**, đừng học `uv` bằng cách thuộc lòng command. Hãy học theo dependency lifecycle:

```text
                    ┌──────────────┐
                    │ Python       │
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │ Environment  │
                    │ .venv        │
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │ Project      │
                    │ pyproject    │
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │ Resolver     │
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │ uv.lock      │
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │ uv sync      │
                    └──────────────┘
```

Sau đó mới đi tới:

```text
Project
   ↓
Dependency Groups
   ↓
Optional Dependencies
   ↓
CLI
   ↓
Build
   ↓
Publish
   ↓
Workspace
   ↓
Docker
   ↓
CI/CD
```

### Roadmap `uv` Deep Dive mình đề xuất

**Phần I — Foundation**

1. `uv` là gì và tại sao ra đời
2. Cài đặt và architecture
3. `uv init`
4. `pyproject.toml`
5. `.python-version`
6. `uv venv`
7. `uv run`
8. `uv add`
9. `uv remove`
10. `uv sync`

**Phần II — Dependency Management**

11. Dependency resolver
12. Version constraint
13. `uv.lock`
14. `uv lock`
15. `uv lock --upgrade`
16. Dependency groups
17. Optional dependencies
18. Development dependencies
19. Git dependencies
20. URL/path dependencies

**Phần III — Python Management**

21. `uv python`
22. Install nhiều Python version
23. Pin Python version
24. Python discovery
25. Environment isolation

**Phần IV — Tools & CLI**

26. `uvx`
27. `uv tool install`
28. Tool isolation
29. CLI applications
30. `[project.scripts]`

**Phần V — Packaging**

31. Package layout
32. `uv build`
33. Wheel
34. Source distribution
35. Local installation
36. PyPI publishing

**Phần VI — Advanced**

37. Workspace
38. Monorepo
39. Dependency groups nâng cao
40. Locking strategy
41. Docker
42. CI/CD
43. Reproducible builds
44. uv cho library
45. uv cho application

**Phần VII — Project thực tế**

46. Xây dựng CLI bằng `uv`
47. Xây dựng library bằng `uv`
48. Xây dựng crawler bằng `uv`
49. Monorepo `crawler-core / worker / plugin / cli`
50. Production workflow hoàn chỉnh.

Với hướng học Python chuyên sâu của bạn, mình đặc biệt khuyên **không bỏ qua `pyproject.toml` + `uv.lock` + dependency resolver**. Đây mới là phần giúp bạn hiểu `uv` thực sự, thay vì chỉ nhớ các lệnh `uv add`, `uv sync`.
