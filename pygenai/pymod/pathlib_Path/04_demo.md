Dưới đây là một chương trình Python thực tế: **Script tự động dọn dẹp và phân loại tệp tin theo định dạng** (File Organizer).

Chương trình này sẽ quét một thư mục bất kỳ, lấy thông tin thuộc tính của tệp, phân loại chúng vào các thư mục con tương ứng với phần mở rộng (`.png`, `.pdf`, `.py`...) và ghi lại nhật ký (log) hoạt động.

```python
from pathlib import Path
from datetime import datetime

def organize_folder(target_dir: str | Path) -> None:
    # 1. Chuyển đổi và chuẩn hóa đường dẫn tuyệt đối
    target_path = Path(target_dir).resolve()
    
    if not target_path.exists():
        print(f"❌ Thư mục không tồn tại: {target_path}")
        return
        
    if not target_path.is_dir():
        print(f"❌ Đường dẫn không phải là thư mục: {target_path}")
        return

    print(f"📂 Đang xử lý thư mục: {target_path}")
    
    # 2. Định nghĩa thư mục lưu trữ Log và khởi tạo file Log bằng `.touch()`
    log_dir = target_path / "Logs"
    log_dir.mkdir(parents=True, exist_ok=True)  # Tạo folder Logs nếu chưa có
    log_file = log_dir / f"organize_log_{datetime.now().strftime('%Y%m%d')}.txt"
    log_file.touch(exist_ok=True)

    log_entries = []

    # 3. Duyệt qua tất cả tệp trong thư mục (Bỏ qua các thư mục con)
    for file_path in target_path.iterdir():
        # Kiểm tra điều kiện: chỉ xử lý file, bỏ qua thư mục và file log hiện tại
        if file_path.is_file() and not file_path.is_relative_to(log_dir):
            
            # --- BÓC TÁCH THÔNG TIN BẰNG PROPERTY ---
            full_name = file_path.name        # Ví dụ: "report.draft.pdf"
            stem_name = file_path.stem        # Ví dụ: "report.draft"
            ext = file_path.suffix.lower()    # Ví dụ: ".pdf"
            
            # Lấy kích thước tệp bằng method .stat()
            file_size_kb = round(file_path.stat().st_size / 1024, 2)
            
            # Gán thư mục đích dựa trên phần mở rộng (Loại bỏ dấu chấm ở đầu)
            folder_name = ext.replace(".", "").upper() if ext else "NO_EXTENSION"
            dest_dir = target_path / folder_name
            
            # --- TẠO THƯ MỤC VÀ ĐỔI TÊN/DI CHUYỂN BẰNG METHOD ---
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Tạo đường dẫn mới cho file
            dest_file_path = dest_dir / full_name
            
            # Nếu file đã tồn tại ở thư mục đích, đổi tên mới dùng .with_stem()
            if dest_file_path.exists():
                new_stem = f"{stem_name}_backup_{datetime.now().strftime('%H%M%S')}"
                dest_file_path = dest_dir / file_path.with_stem(new_stem).name

            # Thực hiện di chuyển tệp
            file_path.rename(dest_file_path)
            
            # Lưu nhật ký
            log_entries.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] Moved: {full_name} ({file_size_kb} KB) -> {dest_file_path.relative_to(target_path)}"
            )

    # 4. Ghi thông tin nhật ký bằng `.write_text()`
    if log_entries:
        existing_log = log_file.read_text(encoding="utf-8") if log_file.stat().st_size > 0 else ""
        new_log_content = existing_log + "\n".join(log_entries) + "\n"
        log_file.write_text(new_log_content, encoding="utf-8")
        print(f"✅ Đã dọn dẹp thành công {len(log_entries)} tệp. Chi tiết xem tại: {log_file.name}")
    else:
        print("ℹ️ Không có tệp nào cần xử lý.")

# ==========================================
# THỰC HÀNH CHẠY THỬ NGHỆM
# ==========================================
if __name__ == "__main__":
    # Tạo một thư mục thử nghiệm "sandbox"
    demo_dir = Path.cwd() / "demo_workspace"
    demo_dir.mkdir(exist_ok=True)
    
    # Tạo vài file giả lập bằng .touch() và .write_text()
    (demo_dir / "notes.txt").write_text("Ghi chú công việc", encoding="utf-8")
    (demo_dir / "script.py").write_text("print('Hello')", encoding="utf-8")
    (demo_dir / "chart.PNG").touch()
    (demo_dir / "data.csv").touch()
    (demo_dir / "document_no_ext").touch()

    # Chạy chương trình dọn dẹp thư mục demo
    organize_folder(demo_dir)

```

---

### Các phương thức & thuộc tính `pathlib` đã áp dụng trong bài:

* **Khởi tạo & Đường dẫn:** `Path.cwd()`, `Path()`, `resolve()`, `relative_to()`
* **Kiểm tra trạng thái:** `exists()`, `is_dir()`, `is_file()`, `is_relative_to()`, `stat()`
* **Bóc tách tên:** `.name`, `.stem`, `.suffix`
* **Biến đổi tên:** `.with_stem()`
* **Thao tác I/O & Thư mục:** `.mkdir()`, `.touch()`, `.rename()`, `.iterdir()`, `.read_text()`, `.write_text()`