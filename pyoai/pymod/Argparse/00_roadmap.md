Rất hay. Nếu mục tiêu của bạn là trở thành **Python Backend Developer** và xây dựng các ứng dụng như **crawler framework**, **TTS CLI**, **tool quản lý SQLite**, **tool build project**, **automation**, thì `argparse` là thư viện bắt buộc phải thành thạo.

Tôi sẽ dạy theo phong cách **Professional Python Developer**, không chỉ biết dùng mà còn hiểu cách thiết kế CLI lớn giống Git, Docker, Pip...

---

# Khóa học Argparse Professional (2026)

## Mục tiêu

Sau khóa học bạn có thể xây dựng được

* CLI cho crawler
* CLI cho downloader
* CLI cho TTS
* CLI quản lý SQLite
* CLI deploy project
* CLI nhiều subcommand như

```
story crawl
story update
story search
story export
story import
story config
story plugin
```

---

# Roadmap

## Phần I — Cơ bản

### Buổi 1. Giới thiệu argparse

* CLI là gì
* Vì sao cần argparse
* sys.argv
* argparse hoạt động thế nào
* Parser đầu tiên

---

### Buổi 2. Positional Arguments

* add_argument()
* kiểu dữ liệu
* nargs
* metavar
* help

---

### Buổi 3. Optional Arguments

---

* *
* default
* required
* action

---

### Buổi 4. Các Action

* store
* store_true
* store_false
* append
* append_const
* count
* version

---

### Buổi 5. Type và Validation

* int
* float
* Path
* custom type
* choices

---

## Phần II — Parsing nâng cao

### Buổi 6. nargs Deep Dive

```
?
*
+
REMAINDER
```

---

### Buổi 7. Namespace

Hiểu rõ

```
Namespace
```

và cách chuyển sang dataclass.

---

### Buổi 8. Nhóm Argument

```
Argument Groups
```

```
required group
```

```
mutually exclusive
```

---

### Buổi 9. Formatter

* RawTextHelpFormatter
* ArgumentDefaultsHelpFormatter
* custom formatter

---

### Buổi 10. Help Message đẹp

Tạo

```
tool --help
```

chuyên nghiệp.

---

## Phần III — Subcommands

### Buổi 11. Subparser

```
git add
git commit
```

cách hoạt động.

---

### Buổi 12. Nested Subcommand

Ví dụ

```
story crawl novel
```

```
story crawl chapter
```

```
story config set
```

---

### Buổi 13. Dispatch Function

Không dùng

```
if args.command
```

mà dùng

```
set_defaults(func=...)
```

---

### Buổi 14. Plugin Command

Tự động load command.

Giống

```
docker plugin
```

---

## Phần IV — Thiết kế CLI

### Buổi 15. Config

```
--config
```

```
.env
```

```
json
```

```
yaml
```

---

### Buổi 16. Logging

```
-v

-vv

-vvv
```

---

### Buổi 17. Progress

Hiển thị

```
Downloading...
```

```
Processing...
```

---

### Buổi 18. Color Output

ANSI

Rich

Colorama

---

### Buổi 19. Error Handling

Thông báo lỗi đẹp.

---

### Buổi 20. Completion

Auto completion

bash

zsh

powershell

---

## Phần V — Professional CLI

### Buổi 21. CLI Architecture

Tách

```
cli/

commands/

services/

config/

```

---

### Buổi 22. Command Pattern

Mỗi command là một class.

---

### Buổi 23. Dependency Injection

Inject service.

---

### Buổi 24. Testing CLI

pytest

subprocess

---

### Buổi 25. Packaging

```
pip install
```

```
entry_points
```

---

### Buổi 26. Phân phối

Build executable.

---

## Phần VI — Project

### Buổi 27.

Xây dựng

```
story
```

CLI

---

### Buổi 28.

Crawler Command

---

### Buổi 29.

Search Command

---

### Buổi 30.

Export Command

---

### Buổi 31.

Import Command

---

### Buổi 32.

Plugin Manager

---

### Buổi 33.

Configuration Manager

---

### Buổi 34.

Database Manager

---

### Buổi 35.

TTS CLI

---

### Buổi 36.

Download Manager

---

### Buổi 37.

Async Command

---

### Buổi 38.

Interactive Mode

---

### Buổi 39.

Refactor thành framework

---

### Buổi 40.

Đồ án cuối khóa

Xây dựng một framework CLI chuyên nghiệp với:

```
story

├── crawl
├── update
├── search
├── plugin
├── db
├── config
├── export
├── import
├── doctor
└── version
```

Có đầy đủ:

* argparse
* logging
* config
* plugin
* SQLite
* Rich
* Packaging
* Testing

---

# Phương pháp giảng dạy

Mỗi buổi sẽ gồm:

1. **Lý thuyết nền tảng**: Giải thích cách `argparse` hoạt động bên trong, không chỉ cách sử dụng.
2. **Ví dụ nhỏ**: Minh họa từng tính năng với mã nguồn rõ ràng.
3. **Ví dụ thực tế**: Áp dụng vào các công cụ CLI như quản lý tệp, crawler hoặc TTS.
4. **Best Practices**: Cách tổ chức mã nguồn, đặt tên, viết trợ giúp (`--help`) chuyên nghiệp.
5. **Những lỗi thường gặp**: Phân tích nguyên nhân và cách tránh.
6. **Bài tập thực hành**: Có yêu cầu và gợi ý để tự làm.
7. **Mini Project**: Cuối mỗi giai đoạn sẽ có một dự án nhỏ để củng cố kiến thức.

---

Khóa học này sẽ phù hợp với lộ trình bạn đang theo đuổi về **Typer**, **crawler framework**, **plugin architecture** và các ứng dụng CLI bằng Python. Tuy nhiên, chúng ta sẽ học **argparse trước**, vì hiểu rõ nền tảng này sẽ giúp bạn sử dụng các framework CLI cấp cao như Typer hoặc Click một cách tự tin và đúng bản chất.
