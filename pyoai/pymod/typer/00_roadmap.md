Rất hay. Nếu mục tiêu của bạn là **xây dựng những ứng dụng CLI chuyên nghiệp** (giống `git`, `docker`, `uv`, `poetry`, `pip`, `pytest`, `alembic`, `click`, `typer`...), thì chúng ta sẽ **không học Typer theo kiểu đọc tài liệu**, mà học theo hướng **thiết kế framework CLI**.

Lộ trình này sẽ đi từ cơ bản đến nâng cao, cuối khóa bạn sẽ tự xây dựng được một CLI framework cho các dự án Python của mình (ví dụ framework crawl truyện mà bạn đang xây dựng).

---

# Khóa học: Xây dựng ứng dụng CLI với Typer

**Mục tiêu cuối khóa**

Sau khóa học bạn có thể tự xây dựng:

```
storycli
│
├── crawl
│      add
│      run
│      stop
│      status
│
├── source
│      install
│      uninstall
│      update
│
├── db
│      migrate
│      backup
│      restore
│
├── config
│      show
│      edit
│
└── plugin
       list
       test
       build
```

giống phong cách

```
git add
git commit
git push

docker compose up

uv pip install

poetry add
```

---

# Giai đoạn I — Làm quen Typer

## Buổi 1. Typer là gì?

* CLI là gì
* argparse vs Click vs Typer
* Cài đặt
* Command đầu tiên
* help
* auto-completion

Project

```
hello.py
```

---

## Buổi 2. Command

* @app.command()
* nhiều command
* command name
* hidden command

Project

```
calculator.py
```

---

## Buổi 3. Arguments

Học toàn bộ

```
str
int
float
bool
Path
Enum
UUID
datetime
```

Validation

Project

```
cp.py
```

---

## Buổi 4. Options

```
--name
--age
--debug

--count

--force

--output
```

Short option

```
-n

-f
```

Project

```
rename.py
```

---

## Buổi 5. Prompt

```
typer.prompt()

confirm()

password
```

Project

```
login.py
```

---

## Buổi 6. Rich Output

```
echo()

style()

color

table

panel

progress
```

Project

```
todo.py
```

---

## Buổi 7. Progress Bar

```
Progress

Spinner

Live

Status
```

Project

Downloader

---

## Buổi 8. Error Handling

```
Exit

Abort

BadParameter

UsageError
```

Project

Validator CLI

---

# Giai đoạn II — Tổ chức ứng dụng

---

## Buổi 9. Typer Group

Sub command

```
git remote

git branch

git stash
```

Project

```
story
```

---

## Buổi 10. Nested Typer

```
story crawl

story plugin

story source
```

Cách chia module

```
main.py

commands/

    crawl.py

    plugin.py

    source.py
```

---

## Buổi 11. Callback

Global option

```
--debug

--config

--verbose
```

Context

---

## Buổi 12. Context (typer.Context)

Deep dive

```
ctx.obj

ctx.invoked_subcommand

ctx.params

ctx.command_path
```

---

## Buổi 13. Dependency Injection

Chia sẻ

```
Database

Config

Logger

HTTP Client
```

---

## Buổi 14. Shell Completion

Autocomplete

```
bash

zsh

fish

powershell
```

---

## Buổi 15. Packaging CLI

Tạo

```
story
```

thay vì

```
python main.py
```

entry_points

---

# Giai đoạn III — Thiết kế CLI chuyên nghiệp

---

## Buổi 16. CLI Architecture

Cấu trúc thư mục

```
cli/

services/

repositories/

models/

config/

plugins/
```

---

## Buổi 17. Config System

```
config.toml

config.json

yaml
```

Priority

```
CLI

↓

ENV

↓

Config

↓

Default
```

---

## Buổi 18. Environment Variables

```
STORY_DEBUG

STORY_DATABASE

STORY_TIMEOUT
```

---

## Buổi 19. Logging

```
verbose

debug

error

warning
```

---

## Buổi 20. Exception Design

Custom Exception

```
CLIError

DatabaseError

PluginError
```

---

## Buổi 21. Plugin Command

Dynamic command

```
story plugin install

story plugin list
```

---

## Buổi 22. Dynamic Loading

importlib

entry point

plugin registry

---

## Buổi 23. Dependency Container

Inject

```
logger

database

http client

config
```

---

## Buổi 24. Middleware

Ví dụ

```
before command

after command

timing

permission
```

---

# Giai đoạn IV — CLI Framework

---

## Buổi 25. BaseCommand

Viết framework

```
class BaseCommand
```

---

## Buổi 26. Service Locator

Framework

---

## Buổi 27. Event System

```
BeforeCommand

AfterCommand

CommandError
```

---

## Buổi 28. Config Loader

Hỗ trợ

```
json

toml

yaml
```

---

## Buổi 29. Command Discovery

Tự động tìm command

```
commands/

*.py
```

---

## Buổi 30. Plugin Discovery

Auto load

```
plugins/
```

---

# Giai đoạn V — CLI thực chiến

---

## Buổi 31. File Manager CLI

```
fm ls

fm cp

fm mv

fm rm
```

---

## Buổi 32. Todo CLI

SQLite

---

## Buổi 33. Password Manager

Encryption

---

## Buổi 34. Downloader CLI

Resume

Progress

---

## Buổi 35. HTTP Client

Giống

```
httpie
```

---

## Buổi 36. SQLite Manager

```
db query

db export

db backup
```

---

## Buổi 37. Crawl CLI

Cho framework crawler của bạn

```
crawl add

crawl run

crawl stop

crawl retry

crawl log
```

---

## Buổi 38. Plugin Manager

```
plugin install

plugin update

plugin build
```

---

## Buổi 39. Story Reader CLI

```
search

download

read

history
```

---

## Buổi 40. Framework hoàn chỉnh

Tổng hợp tất cả

```
story-cli/

    cli/

    commands/

    plugins/

    core/

    models/

    repositories/

    database/

    config/

    services/

    utils/

    tests/

    pyproject.toml
```

Cuối buổi này, bạn sẽ có một **framework CLI có thể tái sử dụng** cho mọi dự án Python.

---

# Giai đoạn VI — Typer nâng cao

## Buổi 41. Async CLI

* Tích hợp `asyncio`
* Gọi HTTP bất đồng bộ
* Quản lý event loop trong Typer
* Ví dụ: kiểm tra nhiều URL đồng thời.

## Buổi 42. Testing CLI

* `typer.testing.CliRunner`
* Unit test cho command
* Kiểm tra mã thoát (exit code), output, lỗi.
* Mock service và repository.

## Buổi 43. Rich + Typer Deep Integration

* `rich.Console`
* `Table`
* `Tree`
* `Panel`
* `Markdown`
* `Syntax`
* `Live`
* `Progress`
* Xây dựng giao diện CLI hiện đại.

## Buổi 44. Typer + Dependency Injection

* Tách lớp CLI khỏi business logic.
* Service Layer.
* Repository Pattern.
* Context chia sẻ tài nguyên.
* Thiết kế dễ mở rộng và dễ kiểm thử.

## Buổi 45. Xây dựng CLI Framework từ đầu

Tổng kết bằng việc tạo một framework CLI hoàn chỉnh với các thành phần:

* Command Registry
* Plugin Loader
* Config Manager
* Logger
* Dependency Container
* Event System
* Middleware
* Test Suite
* Packaging và phân phối qua `pip`

Khóa học này được thiết kế để hỗ trợ trực tiếp dự án **framework cào truyện và đọc truyện** của bạn. Sau các buổi nền tảng (1–15), các ví dụ và bài thực hành sẽ xoay quanh việc xây dựng `story-cli`, giúp bạn có thể dùng ngay cho các module crawler, plugin, database và quản lý nguồn truyện.
