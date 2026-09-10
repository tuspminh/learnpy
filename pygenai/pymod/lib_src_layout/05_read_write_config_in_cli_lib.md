Để lưu trữ thông tin trạng thái giữa các lần chạy (như cấu hình người dùng, thông tin đăng nhập, hoặc đường dẫn cơ sở dữ liệu), ứng dụng CLI thường dùng file cấu hình dạng **JSON** hoặc **YAML**.

Chuẩn nhất trong Python là lưu file cấu hình vào thư mục cấu hình mặc định của hệ điều hành (ví dụ: `~/.config/my_ddd_lib/` trên Linux/macOS hoặc `C:\Users\<User>\AppData\Local\my_ddd_lib\` trên Windows) thông qua thư viện `platformdirs`.

---

## 1. Cài đặt các thư viện hỗ trợ

Cài đặt `platformdirs` để tự động xác định đường dẫn lưu trữ chuẩn trên các HĐH, và `pydantic` (hoặc `pyyaml` nếu dùng YAML) để Validate dữ liệu cấu hình:

```bash
uv add platformdirs pydantic pyyaml

```

---

## 2. Tạo Module Quản lý Cấu hình

Tạo file `src/my_ddd_lib/cli/config.py` xử lý việc đọc, ghi và lấy thông tin cấu hình:

```python
from pathlib import Path
import yaml
from pydantic import BaseModel
from platformdirs import user_config_dir

APP_NAME = "my_ddd_lib"


class CLIConfig(BaseModel):
    """Schema cấu hình với giá trị mặc định"""

    db_url: str = "sqlite:///./bank.db"
    default_currency: str = "VND"
    environment: str = "development"


def get_config_path() -> Path:
    """Xác định đường dẫn file config theo chuẩn của hệ điều hành"""
    config_dir = Path(user_config_dir(APP_NAME))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.yaml"


def load_config() -> CLIConfig:
    """Đọc cấu hình từ file YAML, nếu chưa có thì tạo file mặc định"""
    config_path = get_config_path()

    if not config_path.exists():
        default_cfg = CLIConfig()
        save_config(default_cfg)
        return default_cfg

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return CLIConfig(**data)
    except Exception:
        return CLIConfig()


def save_config(config: CLIConfig) -> None:
    """Ghi đối tượng cấu hình vào file YAML"""
    config_path = get_config_path()
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config.model_dump(), f, default_flow_style=False)
```

---

## 3. Tạo Subcommand Quản lý Cấu hình trong Typer

Tạo file `src/my_ddd_lib/cli/config_cmd.py` cung cấp các lệnh giúp người dùng xem và cập nhật cấu hình:

```python
import typer
from rich import print
from rich.table import Table

from my_ddd_lib.cli.config import load_config, save_config, get_config_path

config_app = typer.Typer(help="Quản lý cấu hình ứng dụng CLI")


@config_app.command("show")
def show_config():
    """Hiển thị file cấu hình hiện tại."""
    cfg = load_config()
    path = get_config_path()

    print(f"[bold yellow]Đường dẫn file config:[/bold yellow] {path}\n")

    table = Table(title="Cấu hình hệ thống")
    table.add_column("Thuộc tính", style="cyan")
    table.add_column("Giá trị", style="green")

    for key, value in cfg.model_dump().items():
        table.add_row(key, str(value))

    print(table)


@config_app.command("set")
def set_config(
    key: str = typer.Argument(
        ..., help="Tên cấu hình (ví dụ: default_currency, environment)"
    ),
    value: str = typer.Argument(..., help="Giá trị mới"),
):
    """Cập nhật một thuộc tính trong file cấu hình."""
    cfg = load_config()
    cfg_data = cfg.model_dump()

    if key not in cfg_data:
        print(
            f"[bold red]X Lỗi:[/bold red] Thuộc tính '[yellow]{key}[/yellow]' không tồn tại."
        )
        raise typer.Exit(code=1)

    cfg_data[key] = value
    new_cfg = CLIConfig(**cfg_data)
    save_config(new_cfg)

    print(
        f"[bold green]✓[/bold green] Đã cập nhật [cyan]{key}[/cyan] = [green]{value}[/green]"
    )
```

---

## 4. Tích hợp vào CLI Chính (`main.py`)

Cập nhật `src/my_ddd_lib/cli/main.py` để gắn nhóm lệnh `config` vào app:

```python
import typer
from my_ddd_lib.cli.account import account_app
from my_ddd_lib.cli.transaction import transaction_app
from my_ddd_lib.cli.config_cmd import config_app

app = typer.Typer(
    name="bank-cli",
    help="Hệ thống quản lý Ngân hàng theo chuẩn DDD",
    add_completion=False,
)

app.add_typer(account_app, name="account")
app.add_typer(transaction_app, name="tx")
app.add_typer(config_app, name="config")  # Nhóm lệnh quản lý cấu hình

if __name__ == "__main__":
    app()
```

---

## 5. Sử dụng Cấu hình trong các Business Commands

Khi người dùng thực hiện một tác vụ (ví dụ: tạo tài khoản), bạn có thể đọc cấu hình để lấy đơn vị tiền tệ mặc định mà họ không cần truyền cờ `--currency`:

```python
# Trong src/my_ddd_lib/cli/account.py
from my_ddd_lib.cli.config import load_config


@account_app.command("create")
def create_account(
    balance: float = typer.Option(..., "--balance", "-b", help="Số dư ban đầu"),
    currency: str = typer.Option(None, "--currency", "-c", help="Đơn vị tiền tệ"),
):
    # Lấy currency từ config nếu người dùng không truyền tham số
    cfg = load_config()
    final_currency = currency or cfg.default_currency

    print(f"Tạo tài khoản với số dư {balance} {final_currency}")
```

---

## 6. Dùng thử các lệnh cấu hình với `uv`

### Xem danh sách cấu hình hiện tại

```bash
uv run bank-cli config show

```

### Đổi đơn vị tiền tệ mặc định sang USD

```bash
uv run bank-cli config set default_currency USD

```

### Kiểm tra lại cấu hình

```bash
uv run bank-cli config show

```