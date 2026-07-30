# Khóa học Click Deep Dive

# Buổi 11: Config Management trong Click - Thiết kế hệ thống cấu hình chuyên nghiệp

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu vì sao CLI lớn cần hệ thống Config. 
>   * Biết cách quản lý cấu hình bằng nhiều nguồn. 
>   * Hiểu thứ tự ưu tiên cấu hình. 
>   * Đọc config từ file YAML/JSON/TOML. 
>   * Kết hợp Config với `Context`. 
>   * Thiết kế `ConfigManager` cho Story CLI. 
> 


* * *

# 1\. Vấn đề khi CLI phát triển lớn

Lúc đầu:
    
    
    story crawler start --threads 8

rất đơn giản.

Nhưng dự án lớn:
    
    
    story crawler start \
    --threads 8 \
    --database story.db \
    --log-level INFO \
    --timeout 30 \
    --proxy http://proxy.com

Sẽ trở thành:
    
    
    rất dài
    khó nhớ
    dễ sai

* * *

Các công cụ lớn đều có config:

Ví dụ:
    
    
    docker
    kubectl
    aws
    git

đều có:

  * config file 
  * environment variable 
  * command line override 



* * *

# 2\. Ba nguồn cấu hình chính

Một CLI chuyên nghiệp thường có:
    
    
                 Configuration
    
                       |
          ----------------------------
    
          |             |            |
    
       Default      Config File   CLI Option
    
                        |
    
                  Environment

* * *

Ví dụ:

## Default
    
    
    threads = 4

* * *

## File config
    
    
    threads: 8

* * *

## CLI
    
    
    --threads 16

* * *

Kết quả:
    
    
    threads = 16

vì CLI ưu tiên cao nhất.

* * *

# 3\. Thứ tự ưu tiên Config

Chuẩn thường dùng:
    
    
    1. Command Line Argument
              ↑
    2. Environment Variable
              ↑
    3. Config File
              ↑
    4. Default Value

Ví dụ:

Default:
    
    
    threads=4

config.yaml:
    
    
    threads: 8

Environment:
    
    
    STORY_THREADS=12

CLI:
    
    
    --threads 16

Kết quả:
    
    
    threads = 16

* * *

# 4\. Thiết kế Config Object

Không nên:
    
    
    config = {
        "threads":8,
        "db":"story.db"
    }

Với dự án lớn:
    
    
    class Config:
        pass

* * *

Ví dụ:

## config.py
    
    
    class Config:
    
        def __init__(self):
    
            self.database = "story.db"
    
            self.threads = 4
    
            self.log_level = "INFO"
    
            self.timeout = 30

* * *

# 5\. ConfigManager

Nên tách trách nhiệm:
    
    
    ConfigManager
    
          |
          |
          +-- Load default
    
          +-- Load file
    
          +-- Load environment
    
          +-- Merge config

* * *

Cấu trúc:
    
    
    story_cli
    
    ├── config
    
    │    ├── manager.py
    
    │    └── models.py
    

* * *

# 6\. Config Model

## models.py
    
    
    from dataclasses import dataclass
    
    
    @dataclass
    class Config:
    
        database: str = "story.db"
    
        threads: int = 4
    
        log_level: str = "INFO"
    
        timeout: int = 30

* * *

Ưu điểm:

  * rõ ràng 
  * type hint 
  * IDE hỗ trợ 



* * *

# 7\. ConfigManager cơ bản

## manager.py
    
    
    from .models import Config
    
    
    class ConfigManager:
    
    
        def __init__(self):
    
            self.config = Config()
    
    
        def load(self):
    
            return self.config

* * *

Sử dụng:
    
    
    manager = ConfigManager()
    
    config = manager.load()

* * *

# 8\. Gắn Config vào Click Context

Nhắc lại:

Buổi 9:
    
    
    ctx.obj

là nơi chia sẻ dữ liệu.

* * *

app.py
    
    
    import click
    
    from config.manager import ConfigManager
    
    
    @click.group()
    @click.pass_context
    def cli(ctx):
    
        manager = ConfigManager()
    
        ctx.obj = manager.load()

* * *

Bây giờ:

mọi command có:
    
    
    ctx.obj

là:
    
    
    Config

* * *

# 9\. Command sử dụng Config
    
    
    @click.command()
    @click.pass_context
    def start(ctx):
    
        config = ctx.obj
    
    
        print(
            config.threads
        )

* * *

Kết quả:
    
    
    4

* * *

# 10\. Load Config từ JSON

Ví dụ:

## config.json
    
    
    {
        "database":"story.db",
        "threads":8,
        "timeout":60
    }

* * *

Đọc:
    
    
    import json
    
    
    with open(
        "config.json"
    ) as f:
    
        data=json.load(f)

* * *

Merge:
    
    
    config.threads = data["threads"]

* * *

# 11\. Load Config từ TOML

Python 3.11 có:
    
    
    import tomllib

* * *

config.toml:
    
    
    database="story.db"
    threads=8
    timeout=60

* * *

Code:
    
    
    with open(
        "config.toml",
        "rb"
    ) as f:
    
        data=tomllib.load(f)

* * *

TOML rất phổ biến trong Python.

Ví dụ:

  * pyproject.toml 
  * Poetry 
  * Ruff 



* * *

# 12\. Config bằng Environment Variable

Ví dụ:
    
    
    STORY_DATABASE=data.db
    STORY_THREADS=16

* * *

Python:
    
    
    import os
    
    
    threads = os.getenv(
        "STORY_THREADS"
    )

* * *

Click hỗ trợ trực tiếp:
    
    
    @click.option(
        "--threads",
        envvar="STORY_THREADS"
    )

* * *

# 13\. Kết hợp Option + Config

Ví dụ:
    
    
    @click.option(
        "--threads",
        default=None
    )

* * *

Command:
    
    
    def start(threads):
    
        if threads is None:
    
            threads=config.threads

* * *

Ý tưởng:
    
    
    CLI có truyền?
    
    YES
     |
     dùng CLI
    
    
    NO
     |
     lấy Config

* * *

# 14\. Dynamic Default từ Config

Đây là pattern tốt.

Ví dụ:
    
    
    @click.option(
        "--threads",
        default=lambda:
            config.threads
    )

* * *

Nhưng Click không biết config ở đâu.

Giải pháp:

dùng Context.

* * *

# 15\. Context Settings

Click hỗ trợ:
    
    
    @click.group(
        context_settings={
            "auto_envvar_prefix":
            "STORY"
        }
    )

* * *

Ví dụ:
    
    
    export STORY_THREADS=8

Click tự nhận:
    
    
    --threads

* * *

# 16\. Config File Option

CLI chuyên nghiệp thường có:
    
    
    story --config myconfig.toml crawler start

* * *

Code:
    
    
    @click.option(
        "--config",
        type=click.Path()
    )

* * *

Root:
    
    
    def cli(config):
    
        load_config(config)

* * *

Sau đó:
    
    
    ctx.obj=config

* * *

# 17\. Kiến trúc hoàn chỉnh

Sau buổi 11:
    
    
    story_cli
    
    
    app.py
    
     |
    
     |
    
    Click Root
    
    
     |
    
     |
    
    ConfigManager
    
    
     |
    
     |
    
    AppContext
    
    
     |
    
     +----------------+
    
     |                |
    
    Crawler        Database
    
    
     |
    
    Service Layer

* * *

# 18\. AppContext chuyên nghiệp

Thực tế không truyền Config trực tiếp.

Tạo:
    
    
    @dataclass
    class AppContext:
    
        config: Config
    
        logger: Logger
    
        database: Database

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
    
        app.config.threads

* * *

# 19\. Ví dụ Story CLI

File:
    
    
    config.toml
    
    
    database="story.db"
    threads=8
    log_level="DEBUG"

* * *

Chạy:
    
    
    story crawler start

Click:
    
    
    Load config.toml
    
    ↓
    
    Create AppContext
    
    ↓
    
    crawler.start()
    
    ↓
    
    Use config

* * *

Output:
    
    
    Database: story.db
    Threads: 8
    Log: DEBUG
    
    Crawler started

* * *

# 20\. Sai lầm thường gặp

## Sai 1: Global Config
    
    
    CONFIG={}

Không nên.

Vấn đề:

  * khó test 
  * khó chạy nhiều instance 



* * *

## Sai 2: Command tự đọc config

Sai:
    
    
    def backup():
    
        open("config.toml")

* * *

Đúng:
    
    
    Root
    
    ↓
    
    ConfigManager
    
    ↓
    
    Context
    
    ↓
    
    Command

* * *

## Sai 3: Trộn Config và Business Logic

Sai:
    
    
    config.load()
    
    crawl()

trong cùng một class.

* * *

Tách:
    
    
    ConfigManager
    
    CrawlerService

* * *

# 21\. Bài tập thực hành

## Bài 1

Tạo:
    
    
    Config

có:
    
    
    database
    threads
    timeout

* * *

## Bài 2

Tạo:
    
    
    config.toml

và load bằng:
    
    
    tomllib

* * *

## Bài 3

Gắn Config vào:
    
    
    ctx.obj

* * *

## Bài 4

Tạo:
    
    
    story crawler start

hiển thị:
    
    
    Database:
    Threads:
    Timeout:

* * *

## Bài 5 - Mini Project

Xây dựng:
    
    
    Story CLI
    
    config.toml
    
          |
    
    ConfigManager
    
          |
    
    AppContext
    
          |
    
    crawler start

Hỗ trợ:
    
    
    story --config dev.toml crawler start

* * *

# Tổng kết Buổi 11

Bạn đã học:

Thành phần| Vai trò  
---|---  
Config Object| Mô hình cấu hình  
ConfigManager| Quản lý config  
TOML/JSON| File config  
Environment Variable| Cấu hình môi trường  
Context| Truyền config  
AppContext| Container ứng dụng  
  
Kiến trúc hiện tại:
    
    
    Nested Command
    
            +
    
    Context
    
            +
    
    Config Management
    
            +
    
    Pipeline
    
            ↓
    
    CLI Framework chuyên nghiệp

* * *

# Buổi 12 tiếp theo (đúng roadmap)

## File Configuration nâng cao

Nội dung:

  * TOML sâu hơn. 
  * YAML. 
  * JSON. 
  * Profile config: 
    * dev.toml 
    * test.toml 
    * production.toml 
  * Merge config. 
  * Override config. 
  * Secret management. 
  * `.env`. 
  * Xây dựng ConfigLoader hoàn chỉnh cho Story CLI.

