# Buổi 2 — Xây dựng Project Structure + Package Architecture

Mục tiêu của buổi này là tạo **một skeleton framework chuyên nghiệp** có thể mở rộng trong nhiều năm mà không phải thay đổi kiến trúc. Sau buổi học, bạn sẽ có:

* Package Python chuẩn (`src layout`)
* `pyproject.toml`
* CLI hoạt động
* Có thể chạy:

  ```bash
  python -m crawler --help
  ```
* Có thể test từng module độc lập.

---

# 1. Vì sao dùng `src layout`?

Thay vì:

```text
novel_crawler/
├── crawler/
├── plugins/
├── tests/
```

chúng ta sẽ dùng:

```text
novel_crawler/
├── src/
│   └── crawler/
├── tests/
├── pyproject.toml
└── README.md
```

Ưu điểm:

* Tránh import nhầm từ thư mục gốc.
* Hoạt động tốt với pytest, packaging, CI/CD.
* Chuẩn của nhiều dự án Python lớn.

---

# 2. Cấu trúc project

```text
novel_crawler/
│
├── pyproject.toml
├── README.md
├── .gitignore
│
├── src/
│   └── crawler/
│       ├── __init__.py
│       ├── __main__.py
│       │
│       ├── cli/
│       ├── core/
│       ├── worker/
│       ├── plugins/
│       ├── parser/
│       ├── repository/
│       ├── database/
│       ├── network/
│       ├── scheduler/
│       └── utils/
│
├── tests/
│
├── data/
│   ├── databases/
│   ├── logs/
│   ├── cache/
│   └── downloads/
│
└── scripts/
```

### Giải thích

| Thư mục    | Chức năng                   |
| ---------- | --------------------------- |
| cli        | Command Line Interface      |
| core       | Interface, model, exception |
| worker     | Crawl worker                |
| plugins    | Plugin từng website         |
| parser     | HTML parser                 |
| repository | Repository Pattern          |
| database   | SQLite Manager              |
| network    | HTTP Client                 |
| scheduler  | Job Scheduler               |
| utils      | Hàm tiện ích                |

---

# 3. Tạo Virtual Environment

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```cmd
.venv\Scripts\activate
```

Kiểm tra:

```bash
python --version
```

---

# 4. Tạo `pyproject.toml`

```toml
[project]
name = "crawler"
version = "0.1.0"
description = "Novel crawler framework"
requires-python = ">=3.12"

dependencies = [
    "click",
    "requests",
    "parsel",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "ruff",
]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

Giải thích:

* `requests`: HTTP Client.
* `parsel`: XPath/CSS Selector.
* `click`: CLI.
* `pytest`: Test.
* `ruff`: Linter + formatter.

---

# 5. Package `crawler`

Tạo:

```text
src/
└── crawler/
    ├── __init__.py
    └── __main__.py
```

`__init__.py`

```python
__version__ = "0.1.0"
```

---

# 6. Entry Point

`__main__.py`

```python
from crawler.cli.main import cli

if __name__ == "__main__":
    cli()
```

Nhờ đó có thể chạy:

```bash
python -m crawler
```

---

# 7. Tạo CLI đầu tiên

```
src/crawler/cli/
```

Tạo:

```text
cli/
├── __init__.py
├── main.py
└── commands/
```

---

## `main.py`

```python
import click

@click.group()
def cli():
    """Novel Crawler Framework"""
    pass

if __name__ == "__main__":
    cli()
```

---

# 8. Chạy thử

```bash
python -m crawler
```

Kết quả:

```text
Usage: python -m crawler [OPTIONS] COMMAND [ARGS]...

Novel Crawler Framework

Options:
  --help
```

Đây là dấu hiệu package hoạt động đúng.

---

# 9. Tạo command đầu tiên

```
commands/
```

Tạo:

```python
import click

@click.command()
def version():
    print("Crawler Framework 0.1.0")
```

---

Trong `cli/main.py`

```python
import click

from crawler.cli.commands.version import version

@click.group()
def cli():
    pass

cli.add_command(version)
```

---

Chạy:

```bash
python -m crawler version
```

Kết quả:

```text
Crawler Framework 0.1.0
```

---

# 10. Tạo command `plugin`

```
commands/plugin.py
```

```python
import click

@click.group()
def plugin():
    """Plugin commands"""
```

Đăng ký:

```python
from crawler.cli.commands.plugin import plugin

cli.add_command(plugin)
```

---

Thử:

```bash
python -m crawler plugin
```

---

# 11. Tạo command con

```python
import click

@click.group()
def plugin():
    pass

@plugin.command()
def list():
    print("No plugin installed")
```

Chạy:

```bash
python -m crawler plugin list
```

Output:

```text
No plugin installed
```

Sau này lệnh này sẽ tự động tìm plugin trong thư mục `plugins`.

---

# 12. Chuẩn bị Plugin Discovery

Tạm thời tạo:

```text
plugins/
│
├── novelbin/
│   └── __init__.py
│
├── truyenfull/
│   └── __init__.py
│
└── tangthuvien/
    └── __init__.py
```

Hiện chưa có mã nguồn, nhưng cấu trúc đã sẵn sàng để phát triển.

---

# 13. Thêm thư mục kiểm thử

```text
tests/
│
├── test_cli.py
├── test_plugin.py
└── test_worker.py
```

Ví dụ:

```python
def test_dummy():
    assert True
```

Chạy:

```bash
pytest
```

---

# 14. Cấu trúc hoàn chỉnh sau Buổi 2

```text
novel_crawler/
│
├── pyproject.toml
├── README.md
│
├── src/
│   └── crawler/
│       ├── __init__.py
│       ├── __main__.py
│       │
│       ├── cli/
│       │   ├── main.py
│       │   └── commands/
│       │       ├── version.py
│       │       └── plugin.py
│       │
│       ├── core/
│       ├── worker/
│       ├── parser/
│       ├── repository/
│       ├── database/
│       ├── network/
│       ├── scheduler/
│       ├── plugins/
│       └── utils/
│
├── tests/
│
├── data/
│   ├── databases/
│   ├── cache/
│   ├── logs/
│   └── downloads/
│
└── scripts/
```

---

# Kiểm thử cuối buổi

Đến cuối buổi, bạn nên chạy thành công các lệnh sau:

```bash
python -m crawler --help
python -m crawler version
python -m crawler plugin
python -m crawler plugin list
pytest
```

Nếu tất cả đều chạy thành công, nền tảng của framework đã sẵn sàng.

---

## Bài tập

1. Tạo đầy đủ cấu trúc thư mục như trên.
2. Viết `pyproject.toml`.
3. Tạo CLI với các lệnh:

   * `version`
   * `plugin`
   * `plugin list`
4. Chạy `pytest` với một test đơn giản.
5. Đảm bảo `python -m crawler --help` hiển thị đúng.

### Buổi 3

Ở buổi tiếp theo, chúng ta sẽ xây dựng **Core Model Layer**, bao gồm:

* Thiết kế các model (`Book`, `Chapter`, `Author`, `Category`, `Image`, ...)
* Metadata và validation
* BaseModel dùng `dataclass`
* Model serialization (`to_dict()`, `from_dict()`)
* Thiết kế model để tương thích với Repository Pattern và SQLite.
