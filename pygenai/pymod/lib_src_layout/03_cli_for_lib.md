**Typer** là thư viện xây dựng ứng dụng dòng lệnh (CLI) hiện đại, dựa trên Type Hints của Python và được phát triển bởi tác giả của FastAPI. Dưới đây là hướng dẫn tích hợp Typer vào cấu trúc dự án DDD hiện tại của bạn.

---

## 1. Cài đặt Typer vào dự án bằng `uv`

Mở terminal tại thư mục gốc của dự án (`my_ddd_lib`) và cài đặt Typer:

```bash
uv add typer

```

---

## 2. Tạo giao diện CLI trong ứng dụng

Tạo một file mới tại `src/my_ddd_lib/cli.py`. Trong cấu trúc DDD, CLI đóng vai trò là một **Interface Adapter** (lớp giao tiếp bên ngoài), gọi đến các **Application Services** hoặc **Domain Models**.

```python
# src/my_ddd_lib/cli.py
from typing import Optional
from uuid import uuid4
import typer
from rich import print  # Typer tự động hỗ trợ tô màu văn bản qua Rich

from my_ddd_lib.domain.models import BankAccount, Money
from my_ddd_lib.application.services import TransferService
from my_ddd_lib.infrastructure.repositories import InMemoryAccountRepository

# Khai báo ứng dụng Typer
app = typer.Typer(
    name="my-ddd-cli",
    help="Giao diện dòng lệnh quản lý tài khoản ngân hàng (DDD)",
    add_completion=False,
)

# Giả lập cơ sở dữ liệu tạm thời
repo = InMemoryAccountRepository()


@app.command()
def create_account(
    balance: float = typer.Option(
        ..., "--balance", "-b", help="Số dư ban đầu của tài khoản"
    ),
    currency: str = typer.Option("VND", "--currency", "-c", help="Đơn vị tiền tệ"),
):
    """
    Tạo một tài khoản ngân hàng mới.
    """
    acc_id = uuid4()
    account = BankAccount(account_id=acc_id, balance=Money(balance, currency))
    repo.save(account)

    print(f"[bold green]✓[/bold green] Tạo tài khoản thành công!")
    print(f"  • ID: [bold yellow]{acc_id}[/bold yellow]")
    print(f"  • Số dư: [bold cyan]{balance} {currency}[/bold cyan]")


@app.command()
def transfer(
    from_id: str = typer.Argument(..., help="ID tài khoản gửi"),
    to_id: str = typer.Argument(..., help="ID tài khoản nhận"),
    amount: float = typer.Argument(..., help="Số tiền cần chuyển"),
):
    """
    Chuyển tiền giữa hai tài khoản.
    """
    service = TransferService(repo)
    try:
        service.transfer(uuid4(), uuid4(), amount)  # Minh họa gọi service
        print(
            f"[bold green]✓[/bold green] Đã chuyển [bold cyan]{amount}[/bold cyan] thành công!"
        )
    except Exception as e:
        print(f"[bold red]X Lỗi:[/bold red] {e}")


if __name__ == "__main__":
    app()
```

---

## 3. Khai báo Entry Point trong `pyproject.toml`

Để người dùng có thể gõ tên lệnh ngắn gọn từ terminal, mở file `pyproject.toml` và thêm đoạn cấu hình `[project.scripts]`:

```toml
[project]
name = "my-ddd-lib"
version = "0.1.0"
dependencies = [
    "typer>=0.12.0",
]

[project.scripts]
bank-cli = "my_ddd_lib.cli:app"

```

---

## 4. Chạy và kiểm tra CLI với `uv`

Bây giờ bạn có thể thực thi ứng dụng CLI trực tiếp thông qua `uv`:

### Xem menu trợ giúp (Auto-generated Help)

```bash
uv run bank-cli --help

```

Typer sẽ tự động tạo giao diện trợ giúp đẹp mắt liệt kê toàn bộ các lệnh và tùy chọn dựa trên Type Hints và Docstrings của hàm.

### Chạy thử lệnh tạo tài khoản

```bash
uv run bank-cli create-account -b 500000 -c VND

```

### Xem trợ giúp cho một lệnh cụ thể

```bash
uv run bank-cli transfer --help

```

---

## 5. Đóng gói và trải nghiệm khi cài đặt

Khi bạn đóng gói thư viện bằng `uv build` và ai đó cài đặt gói `.whl` của bạn, câu lệnh `bank-cli` sẽ tự động có sẵn trên hệ thống của họ để thực thi trực tiếp từ bất kỳ đâu.