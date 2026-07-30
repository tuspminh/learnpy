# Khóa học Click Deep Dive

# Buổi 12: File Configuration nâng cao - Xây dựng ConfigLoader chuyên nghiệp

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu cách tổ chức file config cho CLI lớn. 
>   * Biết dùng TOML, YAML, JSON trong ứng dụng Click. 
>   * Xây dựng hệ thống nhiều profile (`dev`, `test`, `production`). 
>   * Hiểu cơ chế merge config. 
>   * Quản lý secret bằng `.env`. 
>   * Xây dựng `ConfigLoader` hoàn chỉnh cho Story CLI. 
> 


* * *

# 1\. Nhìn lại kiến trúc Config

Buổi trước:
    
    
    CLI
    
     |
    
    Root Command
    
     |
    
    ConfigManager
    
     |
    
    Config Object
    
     |
    
    ctx.obj
    
     |
    
    Command

* * *

Nhưng thực tế:

Một ứng dụng lớn không chỉ có:
    
    
    config.toml

mà thường có:
    
    
    config/
    
    ├── default.toml
    
    ├── development.toml
    
    ├── testing.toml
    
    └── production.toml

* * *

# 2\. Vì sao cần nhiều config?

Ví dụ:

## Development

Máy lập trình viên:
    
    
    database="dev.db"
    debug=true
    threads=2

* * *

## Production

Server:
    
    
    database="story.db"
    debug=false
    threads=32

* * *

Không thể mỗi lần deploy sửa code.

Ta thay đổi config.

* * *

# 3\. Các định dạng config phổ biến

## JSON

Ví dụ:
    
    
    {
        "database": "story.db",
        "threads": 8
    }

Ưu:

  * Có sẵn trong Python. 
  * Dễ đọc máy. 



Nhược:

  * Không có comment. 
  * Dài dòng. 



* * *

## YAML

Ví dụ:
    
    
    database: story.db
    threads: 8
    debug: true

Ưu:

  * Dễ đọc. 
  * Rất phổ biến DevOps. 



Nhược:

  * Cần thư viện ngoài: 


    
    
    pip install pyyaml

* * *

## TOML

Ví dụ:
    
    
    database="story.db"
    
    threads=8
    
    debug=true

Ưu:

  * Chuẩn Python. 
  * Có trong `pyproject.toml`. 
  * Có comment. 



Python 3.11:
    
    
    import tomllib

* * *

# 4\. Khuyến nghị cho Python CLI

Hiện nay:
    
    
    TOML > YAML > JSON

cho CLI Python.

Lý do:

  * Python hỗ trợ native. 
  * Cấu trúc rõ. 
  * An toàn hơn YAML. 



* * *

# 5\. Thiết kế thư mục Config

Cho Story CLI:
    
    
    story_cli/
    
    ├── app.py
    
    ├── config/
    
    │
    ├── default.toml
    │
    ├── dev.toml
    │
    ├── test.toml
    │
    └── prod.toml

* * *

# 6\. default.toml

Đây là config nền:
    
    
    database="story.db"
    
    threads=4
    
    timeout=30
    
    log_level="INFO"

* * *

# 7\. dev.toml
    
    
    debug=true
    
    threads=2
    
    log_level="DEBUG"

* * *

# 8\. prod.toml
    
    
    debug=false
    
    threads=32
    
    log_level="WARNING"

* * *

# 9\. Quy trình load config

Luồng:
    
    
    default.toml
    
    ↓
    
    dev.toml
    
    ↓
    
    environment
    
    ↓
    
    CLI option
    
    ↓
    
    Final Config

* * *

Ví dụ:

default:
    
    
    threads=4

dev:
    
    
    threads=2

CLI:
    
    
    --threads 16

Kết quả:
    
    
    threads=16

* * *

# 10\. Config Merge

Giả sử:

default:
    
    
    {
    "threads":4,
    "timeout":30,
    "log":"INFO"
    }

* * *

dev:
    
    
    {
    "threads":2
    }

* * *

Merge:
    
    
    {
    "threads":2,
    "timeout":30,
    "log":"INFO"
    }

* * *

# 11\. Viết ConfigLoader

Cấu trúc:
    
    
    config/
    
    ├── loader.py
    
    └── models.py

* * *

models.py:
    
    
    from dataclasses import dataclass
    
    
    @dataclass
    class Config:
    
        database: str = "story.db"
    
        threads: int = 4
    
        timeout: int = 30
    
        log_level: str = "INFO"
    
        debug: bool = False

* * *

# 12\. Load TOML

loader.py:
    
    
    import tomllib
    
    
    def load_toml(path):
    
        with open(
            path,
            "rb"
        ) as f:
    
            return tomllib.load(f)

* * *

Sử dụng:
    
    
    data = load_toml(
        "config/dev.toml"
    )

* * *

Kết quả:
    
    
    {
    "threads":2,
    "debug":True
    }

* * *

# 13\. Merge dictionary

Tạo:
    
    
    def merge(
        base,
        override
    ):
    
        base.update(
            override
        )
    
        return base

* * *

Ví dụ:
    
    
    a={
    "threads":4,
    "timeout":30
    }
    
    
    b={
    "threads":8
    }
    
    
    merge(a,b)

* * *

Kết quả:
    
    
    {
    "threads":8,
    "timeout":30
    }

* * *

# 14\. ConfigLoader hoàn chỉnh
    
    
    class ConfigLoader:
    
    
        def __init__(
            self,
            folder
        ):
    
            self.folder = folder
    
    
        def load(
            self,
            profile
        ):
    
            config={}
    
    
            config.update(
                load_toml(
                    "default.toml"
                )
            )
    
    
            config.update(
                load_toml(
                    f"{profile}.toml"
                )
            )
    
    
            return config

* * *

Dùng:
    
    
    loader=ConfigLoader(
        "config"
    )
    
    
    config=loader.load(
        "dev"
    )

* * *

# 15\. Convert dict → Config Object

Không muốn:
    
    
    config["threads"]

* * *

Muốn:
    
    
    config.threads

* * *

Dùng:
    
    
    Config(
        **data
    )

* * *

Ví dụ:
    
    
    data={
    "threads":8
    }
    
    
    config=Config(
        **data
    )

* * *

Kết quả:
    
    
    config.threads

* * *

# 16\. Profile trong CLI

Thiết kế:
    
    
    story --profile dev crawler start

hoặc:
    
    
    story --env production crawler start

* * *

Root command:
    
    
    @click.option(
        "--profile",
        default="dev"
    )

* * *

Ví dụ:
    
    
    @click.group()
    @click.option(
        "--profile"
    )
    @click.pass_context
    def cli(
        ctx,
        profile
    ):
    
        config=loader.load(
            profile
        )
    
        ctx.obj=config

* * *

# 17\. Environment Variable

Ví dụ:
    
    
    STORY_DATABASE=/data/story.db
    STORY_THREADS=16

* * *

Đọc:
    
    
    import os
    
    
    os.getenv(
        "STORY_THREADS"
    )

* * *

Merge:
    
    
    if value:
        config.threads=int(value)

* * *

# 18\. File `.env`

Nhiều dự án dùng:
    
    
    .env

Ví dụ:
    
    
    DATABASE_URL=mysql://...
    API_KEY=xxxx

* * *

Cài:
    
    
    pip install python-dotenv

* * *

Load:
    
    
    from dotenv import load_dotenv
    
    
    load_dotenv()

* * *

Sau đó:
    
    
    os.getenv(
        "API_KEY"
    )

* * *

# 19\. Secret Management

Không nên:
    
    
    api_key="123456"

* * *

Sai:
    
    
    config.toml

commit lên Git.

* * *

Đúng:
    
    
    config.toml
    
    .env
    
    Secret Manager

* * *

Ví dụ:

config:
    
    
    api_url="https://api.com"

.env:
    
    
    API_KEY=secret

* * *

# 20\. CLI Override cuối cùng

Ví dụ:

config:
    
    
    threads=8

* * *

Chạy:
    
    
    story crawler start --threads 32

* * *

Kết quả:
    
    
    threads=32

* * *

Code:
    
    
    if cli_threads:
        config.threads=cli_threads

* * *

# 21\. AppContext hoàn chỉnh

Sau khi load:
    
    
    @dataclass
    class AppContext:
    
        config: Config
    
        logger: object
    
        database: object

* * *

Root:
    
    
    ctx.obj = AppContext(
        config=config,
        logger=logger,
        database=db
    )

* * *

Command:
    
    
    @click.pass_obj
    def start(app):
    
        print(
            app.config.threads
        )

* * *

# 22\. Kiến trúc Story CLI hiện tại
    
    
    story_cli
    
    ├── app.py
    
    ├── context.py
    
    ├── config/
    
    │   ├── loader.py
    
    │   ├── models.py
    
    │   ├── default.toml
    
    │   ├── dev.toml
    
    │   └── prod.toml
    
    │
    ├── commands/
    
    │   ├── crawler.py
    
    │   ├── database.py
    
    │   └── plugin.py
    
    │
    └── services/

* * *

# 23\. Luồng chạy thực tế

Người dùng:
    
    
    story --profile prod crawler start

* * *

Click:
    
    
    Parse arguments
    
    ↓
    
    Load default.toml
    
    ↓
    
    Load prod.toml
    
    ↓
    
    Load .env
    
    ↓
    
    Apply CLI override
    
    ↓
    
    Create AppContext
    
    ↓
    
    crawler.start()
    
    ↓
    
    Service chạy

* * *

# 24\. Bài tập thực hành

## Bài 1

Tạo:
    
    
    config/
    
    default.toml
    
    dev.toml
    
    prod.toml

* * *

## Bài 2

Viết:
    
    
    ConfigLoader

có:
    
    
    load(profile)

* * *

## Bài 3

Merge:
    
    
    default
    +
    profile

* * *

## Bài 4

Convert:
    
    
    dict
    
    ↓
    
    Config dataclass

* * *

## Bài 5 - Mini Project

Xây dựng:
    
    
    story --profile dev crawler start

Output:
    
    
    Profile: dev
    
    Database: story.db
    
    Threads: 2
    
    Debug: True
    
    Crawler started

* * *

# Tổng kết Buổi 12

Bạn đã học:

Thành phần| Vai trò  
---|---  
TOML| Config Python hiện đại  
Profile| dev/test/prod  
Merge config| Gộp cấu hình  
ConfigLoader| Quản lý load  
`.env`| Secret  
Override| Ưu tiên cấu hình  
AppContext| Truyền config  
  
Kiến trúc hiện tại:
    
    
    Click CLI
    
    ↓
    
    Nested Command
    
    ↓
    
    Context
    
    ↓
    
    ConfigLoader
    
    ↓
    
    AppContext
    
    ↓
    
    Service

* * *

# Buổi 13 tiếp theo (theo roadmap)

**Logging trong Click CLI**

Nội dung:

  * Thiết kế Logger cho CLI. 
  * Console handler / File handler. 
  * Log level. 
  * Debug mode. 
  * Rich logging. 
  * Logging trong Context. 
  * Tích hợp Logger vào Story CLI.

