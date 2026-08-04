Để thêm nhóm lệnh chapter (gồm add và view) vào script hiện tại, bạn chỉ cần tạo một @click.group() mới cho chapter và đăng ký nó vào nhóm story chính.
Dưới đây là mã nguồn hoàn chỉnh:

import click
# --- Nhóm lệnh chính ---
@click.group()def story():
    """Quản lý thư viện truyện."""
    pass
# --- Nhóm lệnh phụ: chapter ---
@story.group()def chapter():
    """Quản lý các chương trong truyện."""
    pass

@chapter.command()
@click.argument("name")def add(name):
    """Thêm một chương mới."""
    click.echo(f"Đang thêm chương: {name}")

@chapter.command()
@click.option("--chapter", "chapter_num", type=int, required=True, help="Số thứ tự chương.")def view(chapter_num):
    """Xem nội dung một chương cụ thể."""
    click.echo(f"Đang xem chương số: {chapter_num}")

# --- Các lệnh story cũ ---
@story.command()
@click.argument("title")def add_story(title):
    """Thêm một truyện mới."""
    click.echo(f"Đang thêm truyện: {title}")
# Đổi tên hiển thị trong CLI của lệnh add cũ để không trùng với chapter add
story.add_command(add_story, name="add")

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
@click.option("--format", required=True, help="Định dạng file (ví dụ: epub).")
@click.option("--output", required=True, help="Thư mục xuất file.")def export(db, format, output):
    """Xuất bản thư viện truyện."""
    click.echo(f"Đang xuất {db} sang thư mục {output} với định dạng {format}.")
if __name__ == "__main__":
    story()

## Cách sử dụng các lệnh mới:

* Thêm chương: python script.py story chapter add "Hồi mở đầu"
* Xem chương 5: python script.py story chapter view --chapter=5

Bạn có muốn bổ sung thêm tham số story_id vào nhóm lệnh chapter để biết chính xác chương đó thuộc về truyện nào không?
