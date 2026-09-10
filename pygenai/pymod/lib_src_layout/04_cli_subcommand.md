Khi ứng dụng CLI phát triển, việc gom tất cả hàm vào một file duy nhất sẽ gây khó bảo trì. Trong Typer, cách tốt nhất để tổ chức là **chia nhỏ thành các module/file riêng** và sử dụng **Subcommands (Nhóm lệnh)** bằng `typer.Typer()`.

Mô hình này tương tự như các CLI phổ biến như `git` (`git config ...`, `git remote ...`) hoặc `docker` (`docker container ...`, `docker image ...`).

---

## 1. Cấu trúc thư mục cho ứng dụng CLI đa lệnh

Tách phần CLI thành một sub-package nằm trong lớp `infrastructure` hoặc giao diện người dùng:

```text
src/my_ddd_lib/
├── cli/
│   ├── __init__.py
│   ├── main.py          # Entrypoint kết nối tất cả subcommands
│   ├── account.py       # Nhóm lệnh quản lý tài khoản (account)
│   └── transaction.py   # Nhóm lệnh giao dịch (transfer, withdraw...)

```

---

## 2. Định nghĩa từng Subcommand Module

### Module 1: Quản lý tài khoản (`src/my_ddd_lib/cli/account.py`)

Tạo một instance `typer.Typer()` riêng cho nhóm lệnh `account`:

```python
from uuid import uuid4
import typer
from rich import print

account_app = typer.Typer(help="Quản lý tài khoản ngân hàng")


@account_app.command("create")
def create_account(
    balance: float = typer.Option(..., "--balance", "-b", help="Số dư ban đầu"),
    currency: str = typer.Option("VND", "--currency", "-c", help="Đơn vị tiền tệ"),
):
    """Tạo một tài khoản ngân hàng mới."""
    acc_id = uuid4()
    print(
        f"[bold green]✓[/bold green] Đã tạo tài khoản [bold yellow]{acc_id}[/bold yellow] với số dư [cyan]{balance} {currency}[/cyan]"
    )


@account_app.command("list")
def list_accounts():
    """Liệt kê tất cả tài khoản."""
    print("[bold blue]Danh sách tài khoản:[/bold blue]")
    print("  • Acc 1: 1,000,000 VND")
    print("  • Acc 2: 500,000 VND")
```

### Module 2: Quản lý giao dịch (`src/my_ddd_lib/cli/transaction.py`)

Tạo một instance `typer.Typer()` riêng cho nhóm lệnh `transaction`:

```python
import typer
from rich import print

transaction_app = typer.Typer(help="Thực hiện và tra cứu giao dịch")


@transaction_app.command("transfer")
def transfer_money(
    from_id: str = typer.Argument(..., help="ID tài khoản gửi"),
    to_id: str = typer.Argument(..., help="ID tài khoản nhận"),
    amount: float = typer.Argument(..., help="Số tiền chuyển"),
):
    """Chuyển tiền giữa hai tài khoản."""
    print(
        f"[bold green]✓[/bold green] Đã chuyển [cyan]{amount}[/cyan] từ {from_id[:8]}... sang {to_id[:8]}..."
    )


@transaction_app.command("history")
def transaction_history(account_id: str):
    """Lịch sử giao dịch của tài khoản."""
    print(f"[bold yellow]Lịch sử giao dịch của {account_id}:[/bold yellow]")
```

---

## 3. Kết nối các Subcommands tại `main.py`

Tạo app chính tại `src/my_ddd_lib/cli/main.py` và dùng phương thức `add_typer()` để tích hợp các nhóm lệnh vào app cha:

```python
import typer
from my_ddd_lib.cli.account import account_app
from my_ddd_lib.cli.transaction import transaction_app

# App CLI chính
app = typer.Typer(
    name="bank-cli",
    help="Hệ thống quản lý Ngân hàng theo chuẩn DDD",
    add_completion=False,
)

# Gắn các subcommand vào app chính với name tương ứng
app.add_typer(account_app, name="account", help="Quản lý tài khoản (tạo, liệt kê...)")
app.add_typer(
    transaction_app, name="tx", help="Quản lý giao dịch (chuyển tiền, lịch sử...)"
)

if __name__ == "__main__":
    app()
```

---

## 4. Cập nhật `pyproject.toml`

Trỏ entrypoint trong `pyproject.toml` tới file `main.py` mới:

```toml
[project.scripts]
bank-cli = "my_ddd_lib.cli.main:app"

```

---

## 5. Trải nghiệm cấu trúc nhóm lệnh mới

Sau khi thiết lập, bạn có thể chạy các câu lệnh đa cấp rất chuyên nghiệp qua `uv`:

### Trợ giúp tổng thể:

```bash
uv run bank-cli --help

```

*Kết quả hiển thị nhóm lệnh `account` và `tx`.*

### Trợ giúp nhóm lệnh `account`:

```bash
uv run bank-cli account --help

```

### Chạy trực tiếp subcommand:

```bash
# Tạo tài khoản
uv run bank-cli account create -b 2000000

# Xem danh sách
uv run bank-cli account list

# Thực hiện chuyển tiền
uv run bank-cli tx transfer ID_A ID_B 500000

```