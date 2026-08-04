Để cài đặt CLI của bạn thành một lệnh chạy độc lập trong terminal (ví dụ: gõ trực tiếp mtool thay vì python main.py), bạn có thể sử dụng một trong hai cách cấu hình phổ biến nhất dưới đây.
Hãy tạo file cấu hình nằm ở thư mục gốc (ngang hàng với file main.py).
------------------------------
## Cách 1: Sử dụng pyproject.toml (Chuẩn hiện đại)
Đây là cách thiết lập được khuyến nghị cho các dự án Python hiện đại (từ phiên bản Python 3.11 trở đi), thay thế hoàn toàn cho setup.py.
Bạn tạo file pyproject.toml ở thư mục gốc:

[build-system]
requires = ["setuptools>=61.0.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my_cli_project"
version = "0.1.0"
description = "Hệ thống quản lý truyện và nguồn dữ liệu bằng Click CLI"
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "click>=8.0.0",
]

[project.scripts]
mtool = "cli:cli"


* mtool = "cli:cli" nghĩa là gì? Nó sẽ tạo ra một lệnh terminal tên là mtool. Khi bạn gõ lệnh này, Python sẽ tìm vào package cli (file cli/__init__.py) và kích hoạt hàm @click.group() def cli():.

------------------------------
## Cách 2: Sử dụng setup.py (Chuẩn truyền thống)
Nếu bạn đang làm việc với các hệ thống cũ hoặc thích phong cách viết code Python truyền thống, bạn có thể dùng file này.
Bạn tạo file setup.py ở thư mục gốc:

from setuptools import setup, find_packages

setup(
    name="my_cli_project",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "mtool=cli:cli",
        ],
    },
)

------------------------------
## 🚀 Cách cài đặt và chạy thử nghiệm (Editable Mode)
Dù bạn chọn cách 1 hay cách 2, quy trình cài đặt trong terminal đều giống nhau. Hãy mở terminal tại thư mục gốc của dự án (my_cli_project/) và chạy lệnh sau:

pip install -e .

Tham số -e (Editable) giúp bạn vừa phát triển dự án vừa thử nghiệm. Mỗi khi bạn sửa code trong thư mục cli/, lệnh terminal sẽ tự động cập nhật mà không cần phải cài đặt lại.
## 🛠️ Kiếm tra thành quả
Bây giờ, bạn không cần gõ python main.py nữa. Hãy mở một tab terminal mới và gõ trực tiếp tên lệnh mtool:

# Kiểm tra trợ giúp tổng thể
mtool --help
# Chạy các lệnh con
mtool story add "Harry Potter"
mtool story chapter view --chapter=5
mtool source list

Bạn có muốn cấu hình thêm file cấu hình toàn cục (config file bằng YAML hoặc JSON) để lưu lại các cài đặt như thư mục xuất file mặc định không?



===
### mtool only iiss name
Hoàn toàn được! Bạn có thể đổi mtool thành bất kỳ tên nào bạn muốn, miễn là tên đó không bị trùng với các lệnh hệ thống có sẵn (như cd, ls, git,...).
Để thay đổi, bạn chỉ cần sửa lại dòng cấu hình tên lệnh trong file thiết lập của mình.
## 1. Nếu bạn dùng pyproject.toml
Hãy sửa lại mục [project.scripts] ở cuối file:

[project.scripts]
truyen = "cli:cli"  # Đổi 'mtool' thành 'truyen' (hoặc tên bất kỳ)

## 2. Nếu bạn dùng setup.py
Hãy sửa lại mục console_scripts trong hàm setup():

    entry_points={
        "console_scripts": [
            "truyen=cli:cli",  # Đổi 'mtool' thành 'truyen' (hoặc tên bất kỳ)
        ],
    },

------------------------------
## 🚀 Áp dụng thay đổi
Sau khi sửa file cấu hình xong, bạn cần chạy lại lệnh cài đặt trong terminal để hệ thống cập nhật tên gọi mới:

pip install -e .

Bây giờ bạn có thể gọi trực tiếp bằng tên mới trong terminal:

truyen --help
truyen story add "Harry Potter"
truyen source list

Bạn muốn đặt tên lệnh CLI này là gì? Nếu bạn cần, tôi có thể hướng dẫn cách tự động gợi ý lệnh (tab-completion) trong terminal cho tên lệnh mới này.
