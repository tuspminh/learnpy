Để chạy (run) trực tiếp mã nguồn trong thư viện Python của bạn mà không cần đóng gói và cài đặt lại mỗi khi chỉnh sửa, bạn có 3 phương pháp phổ biến nhất tùy theo mục đích:

---

## 1. Chạy dưới dạng Module (`python -m`)

Đây là cách chuẩn nhất khi làm việc với cấu trúc thư mục dạng `src-layout`.

Chạy trực tiếp một file bất kỳ trong thư viện bằng cờ `-m` từ thư mục gốc của dự án:

```bash
uv run python -m my_ddd_lib.application.services

```

> **Lưu ý:** Trong file Python bạn muốn chạy trực tiếp, hãy thêm khối lệnh `if __name__ == "__main__":` ở cuối file để thực thi mã thử nghiệm.

---

## 2. Tạo một script chạy thử nghiệm (`main.py` hoặc `run.py`)

Tạo một file script độc lập ở ngay thư mục gốc (nằm ngoài `src/`) để gọi và test các chức năng trong thư viện:

**Tạo file `main.py`:**

```python
from uuid import uuid4
from my_ddd_lib import BankAccount, Money, TransferService, InMemoryAccountRepository


def main():
    repo = InMemoryAccountRepository()

    # Tạo 2 tài khoản
    acc1 = BankAccount(account_id=uuid4(), balance=Money(1000))
    acc2 = BankAccount(account_id=uuid4(), balance=Money(500))

    repo.save(acc1)
    repo.save(acc2)

    # Thực hiện chuyển tiền
    service = TransferService(repo)
    service.transfer(acc1.id, acc2.id, 200)

    print(f"Số dư Tk1: {repo.get_by_id(acc1.id).balance.amount}")  # 800.0
    print(f"Số dư Tk2: {repo.get_by_id(acc2.id).balance.amount}")  # 700.0


if __name__ == "__main__":
    main()
```

**Chạy file bằng `uv`:**

```bash
uv run python main.py

```

`uv` sẽ tự động nhận diện thư viện trong thư mục `src/` nhờ cấu hình trong `pyproject.toml` mà không cần bạn phải link thủ công.

---

## 3. Khai báo Command-Line Interface (CLI / Entry Point)

Nếu bạn muốn đóng gói thư viện sao cho sau khi cài đặt, người dùng (hoặc chính bạn) có thể gõ một câu lệnh terminal ngắn gọn để chạy ngay:

### Bước 1: Tạo hàm entrypoint trong thư viện

Thêm một hàm vào file `src/my_ddd_lib/cli.py` (hoặc ngay trong `src/my_ddd_lib/__init__.py`):

```python
# src/my_ddd_lib/cli.py
def main():
    print("Thư viện my_ddd_lib đang chạy!")


if __name__ == "__main__":
    main()
```

### Bước 2: Cấu hình `scripts` trong `pyproject.toml`

Thêm phần cấu hình sau vào `pyproject.toml`:

```toml
[project.scripts]
my-lib = "my_ddd_lib.cli:main"

```

### Bước 3: Chạy trực tiếp lệnh CLI qua `uv`

```bash
uv run my-lib

```

---

## 4. Cài đặt chế độ Editable Mode (`pip install -e .`)

Nếu bạn có một dự án khác bên ngoài và muốn dùng thử thư viện này trong khi vẫn đang tiếp tục chỉnh sửa code:

```bash
# Ở thư mục dự án bên ngoài đó:
uv pip install -e /duong/dan/den/my_ddd_lib

```

Mọi sự thay đổi trong code của thư viện sẽ được cập nhật ngay lập tức mà không cần phải `uv build` hay cài đặt lại.