Để tạo một nhóm lệnh song song (ngang hàng) với story, bạn chỉ cần tạo một hàm CLI gốc (@click.group()) đóng vai trò là điểm kích hoạt chính. Sau đó, bạn đăng ký cả hai nhóm lệnh story và source vào hàm gốc này.
Dưới đây là mã nguồn hoàn chỉnh giúp bạn tách biệt cấu trúc rõ ràng:

import click
# ==========================================# 0. ĐIỂM KÍCH HOẠT CHÍNH (GỐC)# ==========================================
@click.group()def cli():
    """Hệ thống quản lý truyện và nguồn dữ liệu."""
    pass

# ==========================================# 1. NHÓM LỆNH STORY (NGANG HÀNG)# ==========================================
@cli.group()def story():
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
# --- Nhóm lệnh con của story: chapter ---
@story.group()def chapter():
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

# ==========================================# 2. NHÓM LỆNH SOURCE (SONG SONG VỚI STORY)# ==========================================
@cli.group()def source():
    """Quản lý các nguồn cào truyện (sources)."""
    pass

@source.command(name="list")def source_list():
    """Hiển thị danh sách các nguồn."""
    click.echo("Danh sách nguồn: [1] TruyenFull, [2] TangThuvien, [3] Metruyenchu")

@source.command(name="add")
@click.argument("url")def source_add(url):
    """Thêm một nguồn cào truyện mới."""
    click.echo(f"Đang thêm nguồn mới từ URL: {url}")

if __name__ == "__main__":
    cli() # Gọi group gốc ở đây

## Cách chạy các lệnh mới:

* Xem danh sách nguồn: python script.py source list
* Thêm nguồn mới: python script.py source add "https://example.com"
* Các lệnh story cũ (chỉ cần đổi từ story thành cli ở hàm chạy, cấu trúc gõ lệnh vẫn giữ nguyên): python script.py story add "Harry Potter"

Bạn có muốn thêm các tham số cấu hình cho lệnh source add (ví dụ như --type hoặc --name) để quản lý nguồn dễ dàng hơn không?
