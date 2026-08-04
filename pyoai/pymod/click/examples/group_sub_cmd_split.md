Để dự án dễ mở rộng và không bị rối khi thêm nhiều lệnh, bạn nên tách cấu trúc Click CLI thành mô hình thư mục (package).
Dưới đây là cấu trúc thư mục chuẩn, dễ quản lý nhất cho dự án của bạn:
## 📁 Cấu trúc thư mục dự án

my_cli_project/
│
├── main.py              # File chạy chính
└── cli/                 # Thư mục chứa mã nguồn CLI
    ├── __init__.py      # Khởi tạo CLI và nhóm nhóm lệnh gốc (cli)
    ├── story.py         # Nhóm lệnh 'story' và các lệnh con (add, remove...)
    ├── chapter.py       # Nhóm lệnh con 'chapter' (add, view) của story
    └── source.py        # Nhóm lệnh 'source' (list, add)

------------------------------
## 💻 Chi tiết mã nguồn từng file## 1. cli/__init__.py (Khởi tạo group gốc)
File này định nghĩa group chính cli, sau đó import và đăng ký các group con (story, source) vào nó.

import clickfrom .story import storyfrom .source import source

@click.group()def cli():
    """Hệ thống quản lý truyện và nguồn dữ liệu."""
    pass
# Đăng ký các nhóm lệnh song song vào group gốc
cli.add_command(story)
cli.add_command(source)

## 2. cli/story.py (Quản lý truyện)
File này định nghĩa nhóm story và các lệnh trực thuộc nó. Nó cũng sẽ import nhóm lệnh chapter từ file riêng để nhúng vào.

import clickfrom .chapter import chapter

@click.group()def story():
    """Quản lý thư viện truyện."""
    pass

@story.command(name="add")
@click.argument("title")def story_add(title):
    """Thêm một truyện mới."""
    click.echo(f"Đang thêm truyện: {title}")

@story.command()
@click.argument("story_id", type=int)def remove(story_id):
    """Xóa truyện theo ID."""
    click.echo(f"Đang xóa truyện có ID: {story_id}")

@story.command()
@click.argument("keyword")def search(keyword):
    """Tìm kiếm truyện."""
    click.echo(f"Đang tìm kiếm: {keyword}")

@story.command()
@click.argument("db")
@click.option("--format", required=True, help="Định dạng file.")
@click.option("--output", required=True, help="Thư mục xuất file.")def export(db, format, output):
    """Xuất bản thư viện truyện."""
    click.echo(f"Đang xuất {db} sang {output} ({format}).")
# Đăng ký nhóm lệnh chapter vào làm con của story
story.add_command(chapter)

## 3. cli/chapter.py (Quản lý chương)
File này tách biệt hoàn toàn các logic liên quan đến chương (chapter).

import click

@click.group()def chapter():
    """Quản lý các chương trong truyện."""
    pass

@chapter.command(name="add")
@click.argument("name")def chapter_add(name):
    """Thêm chương mới."""
    click.echo(f"Đang thêm chương: {name}")

@chapter.command()
@click.option("--chapter", "chapter_num", type=int, required=True, help="Số thứ tự chương.")def view(chapter_num):
    """Xem nội dung chương."""
    click.echo(f"Đang xem chương số: {chapter_num}")

## 4. cli/source.py (Quản lý nguồn truyện)
File này định nghĩa các lệnh song song với story.

import click

@click.group()def source():
    """Quản lý các nguồn cào truyện (sources)."""
    pass

@source.command(name="list")def source_list():
    """Hiển thị danh sách các nguồn."""
    click.echo("Danh sách nguồn: TruyenFull, TangThuvien, Metruyenchu")

@source.command(name="add")
@click.argument("url")def source_add(url):
    """Thêm một nguồn cào truyện mới."""
    click.echo(f"Đang thêm nguồn mới từ URL: {url}")

## 5. main.py (File thực thi ở thư mục ngoài cùng)
File này cực kỳ ngắn gọn, chỉ làm nhiệm vụ gọi group cli từ gói cli vừa tạo.

from cli import cli
if __name__ == "__main__":
    cli()

------------------------------
## 🚀 Cách chạy ứng dụng sau khi tách file
Bạn đứng ở thư mục gốc (my_cli_project/) và gõ lệnh như bình thường:

* Chạy lệnh truyện: python main.py story add "Harry Potter"
* Chạy lệnh chương: python main.py story chapter view --chapter=5
* Chạy lệnh nguồn: python main.py source list

Để hoàn thiện dự án, bạn có muốn tôi viết thêm file setup.py hoặc pyproject.toml để bạn có thể cài đặt công cụ này thành một lệnh độc lập trong terminal (ví dụ gõ thẳng chữ story-cli story add ... thay vì python main.py) không?
