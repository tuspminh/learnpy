Để giải nén tệp `.zip`, chúng ta kết hợp **`zipfile`** (thuộc thư viện tiêu chuẩn của Python) với các phương thức thao tác thư mục mượt mà của `pathlib.Path`.

Dưới đây là phiên bản cập nhật của script, bổ sung tính năng tự động phát hiện tệp zip, giải nén vào thư mục riêng, lưu vết nhật ký và dọn dẹp (xóa hoặc giữ lại) file zip ban đầu.

---

### Script Python tự động giải nén & dọn dẹp

```python
import zipfile
from pathlib import Path
from datetime import datetime

def organize_and_extract(target_dir: str | Path, remove_zip_after_extract: bool = False) -> None:
    # 1. Chuẩn hóa đường dẫn
    target_path = Path(target_dir).resolve()
    
    if not target_path.exists() or not target_path.is_dir():
        print(f"❌ Thư mục không hợp lệ: {target_path}")
        return

    print(f"📂 Đang xử lý thư mục: {target_path}")
    
    # 2. Khởi tạo file Log
    log_dir = target_path / "Logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"organize_log_{datetime.now().strftime('%Y%m%d')}.txt"
    log_file.touch(exist_ok=True)

    log_entries = []

    # 3. Duyệt qua các tệp trong thư mục
    for file_path in target_path.iterdir():
        # Bỏ qua thư mục và thư mục Logs
        if not file_path.is_file() or file_path.is_relative_to(log_dir):
            continue

        full_name = file_path.name
        stem_name = file_path.stem
        ext = file_path.suffix.lower()
        file_size_kb = round(file_path.stat().st_size / 1024, 2)

        # ==========================================
        # XỬ LÝ RIÊNG CHO TỆP .ZIP
        # ==========================================
        if ext == ".zip":
            # Tạo thư mục đích để giải nén (ví dụ: /ZIP_EXTRACTED/my_archive)
            extract_dir = target_path / "ZIP_EXTRACTED" / stem_name
            extract_dir.mkdir(parents=True, exist_ok=True)

            try:
                # Dùng zipfile để mở và giải nén toàn bộ
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)

                log_entries.append(
                    f"[{datetime.now().strftime('%H:%M:%S')}] 📦 Extracted ZIP: {full_name} -> {extract_dir.relative_to(target_path)}"
                )

                # Tùy chọn xóa file .zip gốc sau khi giải nén thành công bằng .unlink()
                if remove_zip_after_extract:
                    file_path.unlink()
                    log_entries.append(
                        f"[{datetime.now().strftime('%H:%M:%S')}] 🗑️ Deleted original zip: {full_name}"
                    )
                else:
                    # Nếu không xóa, di chuyển tệp .zip vào thư mục lưu trữ ZIP
                    zip_archive_dir = target_path / "ZIP"
                    zip_archive_dir.mkdir(parents=True, exist_ok=True)
                    file_path.rename(zip_archive_dir / full_name)

            except zipfile.BadZipFile:
                print(f"⚠️ Tệp zip bị lỗi, không thể giải nén: {full_name}")
                log_entries.append(
                    f"[{datetime.now().strftime('%H:%M:%S')}] ❌ CORRUPTED ZIP: {full_name}"
                )

        # ==========================================
        # XỬ LÝ CÁC TỆP THƯỜNG KHÁC
        # ==========================================
        else:
            folder_name = ext.replace(".", "").upper() if ext else "NO_EXTENSION"
            dest_dir = target_path / folder_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            dest_file_path = dest_dir / full_name
            
            # Xử lý trùng tên bằng .with_stem()
            if dest_file_path.exists():
                new_stem = f"{stem_name}_backup_{datetime.now().strftime('%H%M%S')}"
                dest_file_path = dest_dir / file_path.with_stem(new_stem).name

            file_path.rename(dest_file_path)
            
            log_entries.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] Moved: {full_name} ({file_size_kb} KB) -> {dest_file_path.relative_to(target_path)}"
            )

    # 4. Cập nhật nhật ký
    if log_entries:
        existing_log = log_file.read_text(encoding="utf-8") if log_file.stat().st_size > 0 else ""
        new_log_content = existing_log + "\n".join(log_entries) + "\n"
        log_file.write_text(new_log_content, encoding="utf-8")
        print(f"✅ Đã xử lý xong. Xem chi tiết tại log: {log_file.name}")
    else:
        print("ℹ️ Không có tệp nào để xử lý.")


# ==========================================
# THỰC HÀNH TẠO FILE ZIP THỬ NGHIỆM
# ==========================================
if __name__ == "__main__":
    demo_dir = Path.cwd() / "demo_workspace"
    demo_dir.mkdir(exist_ok=True)

    # 1. Tạo một tệp .zip mẫu để test
    sample_zip_path = demo_dir / "project_docs.zip"
    with zipfile.ZipFile(sample_zip_path, 'w') as zip_file:
        # Ghi vài nội dung giả lập vào file zip
        zip_file.writestr("readme.txt", "Nội dung tài liệu dự án.")
        zip_file.writestr("config.json", '{"version": "1.0"}')

    # 2. Tạo một vài file thường
    (demo_dir / "invoice.pdf").touch()
    (demo_dir / "photo.jpg").touch()

    # 3. Chạy hàm (Tham số remove_zip_after_extract=False sẽ di chuyển file .zip vào folder ZIP)
    organize_and_extract(demo_dir, remove_zip_after_extract=False)

```

---

### Điểm nhấn khi kết hợp `zipfile` và `pathlib`:

1. **`ZipFile(file_path, 'r')`**: Bạn có thể truyền thẳng đối tượng `Path` vào `zipfile.ZipFile()` mà không cần chuyển sang chuỗi `str(file_path)`.
2. **`zip_ref.extractall(extract_dir)`**: Giải nén toàn bộ nội dung trong file zip vào đường dẫn `Path` của thư mục đích.
3. **Quản lý sau giải nén**:
* Xóa file `.zip` gốc dùng **`file_path.unlink()`**.
* Hoặc lưu trữ lại bằng **`file_path.rename(dest)`**.



> **Mẹo nâng cao (Về thư viện `shutil`):**
> Nếu bạn muốn hỗ trợ nhiều định dạng nén khác (như `.tar`, `.gztar`, `.tar.xz`), thay vì dùng `zipfile`, bạn có thể dùng `shutil.unpack_archive(filename, extract_dir)`. `shutil` sẽ tự nhận diện định dạng nén và giải nén tương tự.