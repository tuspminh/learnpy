Thư viện typer sử dụng chung bộ công cụ hiển thị với click, do đó bạn có thể dùng typer.progressbar() để tạo thanh tiến trình (Progress Bar) hiển thị thời gian và phần trăm hoàn thành cực kỳ trực quan.
Dưới đây là cách tích hợp thanh tiến trình vào hai lệnh export và source add. Bạn chỉ cần cập nhật mã nguồn ở các file tương ứng:
## 1. Thêm Progress Bar vào lệnh export (cli/story.py)
Chúng ta sẽ giả lập quá trình xuất file của từng chương bằng cách duyệt qua một vòng lặp và cập nhật thanh tiến trình.

import typerimport time  # Dùng để giả lập thời gian xử lý
app = typer.Typer(help="Quản lý thư viện truyện.")
# ... Các lệnh add, remove, search giữ nguyên ...

@app.command()def export(
    db: str = typer.Argument(..., help="Tên database"),
    format: str = typer.Option(..., help="Định dạng file (ví dụ: epub)."),
    output: str = typer.Option(..., help="Thư mục xuất file.")
):
    """Xuất bản thư viện truyện với thanh tiến trình."""
    print(f"📦 Bắt đầu xuất dữ liệu từ {db}...")
    
    # Giả lập danh sách 100 chương cần xuất
    total_chapters = 100
    
    # Sử dụng typer.progressbar để bọc ngoài vòng lặp
    with typer.progressbar(range(total_chapters), label="Đang xử lý chương") as progress:
        for chapter in progress:
            # Giả lập thời gian export mỗi chương (0.02 giây)
            time.sleep(0.02) 
            
    # Hiển thị thông báo khi hoàn thành bằng chữ màu xanh lá (style)
    typer.secho(f"✨ Đã xuất xong file sang {output} với định dạng {format}!", fg=typer.colors.GREEN, bold=True)

## 2. Thêm Progress Bar vào lệnh source add (cli/source.py)
Đối với lệnh cào dữ liệu từ URL, ta có thể tạo thanh tiến trình hiển thị trạng thái "đang tải" không xác định trước số lượng (hoặc giả lập tải dung lượng KB).

import typerimport time
app = typer.Typer(help="Quản lý các nguồn cào truyện (sources).")

@app.command(name="list")def source_list():
    """Hiển thị danh sách các nguồn."""
    print("Danh sách nguồn: TruyenFull, TangThuvien, Metruyenchu")

@app.command(name="add")def source_add(url: str = typer.Argument(..., help="URL của nguồn truyện")):
    """Thêm một nguồn cào truyện mới và tải siêu dữ liệu (metadata)."""
    typer.echo(f"🔗 Đang kết nối tới nguồn: {url}")
    
    # Giả lập tải dữ liệu dung lượng 1000 KB
    total_kb = 1000
    
    with typer.progressbar(length=total_kb, label="Đang tải dữ liệu nguồn") as progress:
        while progress.finished is False:
            # Giả lập mỗi lần tải được một lượng dữ liệu ngẫu nhiên
            time.sleep(0.1)
            progress.update(200) # Cập nhật thanh tiến trình thêm 200 KB
            
    typer.secho("✅ Đã thêm và đồng bộ cấu hình nguồn thành công!", fg=typer.colors.CYAN)

------------------------------
## 🚀 Thử nghiệm trong Terminal
Sau khi lưu lại mã nguồn, bạn hãy chạy thử để xem hiệu ứng chuyển động của thanh tiến trình:

# Thử nghiệm lệnh export
truyen story export library.db --format epub --output exports/
# Thử nghiệm lệnh source add
truyen source add "https://truyen-moi.com"

Khi chạy, terminal sẽ hiển thị một thanh tiến trình dạng [████████████████████████████████████████] 100% tăng dần rất mượt mà.
Bạn có muốn tôi hướng dẫn cách kết nối CLI này vào một file cơ sở dữ liệu SQLite thật để khi bạn gõ story add, truyện sẽ được lưu trực tiếp vào ổ cứng không?
