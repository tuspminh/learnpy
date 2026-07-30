# Khóa học: Làm chủ `pathlib` và `urllib`

# Buổi 8: Sao chép, Di chuyển và Đồng bộ File (`pathlib` \+ `shutil`)

> **Mục tiêu**

Sau buổi học này bạn sẽ:

  * Hiểu vì sao `pathlib` **không** có hàm `copy()`. 
  * Thành thạo `shutil.copy()`, `copy2()`, `copyfile()`, `copytree()`, `move()`, `rmtree()`. 
  * Biết kết hợp `pathlib` với `shutil`. 
  * Hiểu sự khác nhau giữa Copy và Move. 
  * Xây dựng **FileManager** chuyên nghiệp. 



* * *

# 1\. Tại sao pathlib không có copy()?

Đây là câu hỏi rất nhiều người thắc mắc.

Ví dụ
    
    
    from pathlib import Path
    
    file = Path("chapter001.txt")

Có
    
    
    file.rename()
    
    file.unlink()
    
    file.mkdir()

Nhưng lại **không có**
    
    
    file.copy()

Lý do:

> `pathlib` chỉ chịu trách nhiệm **biểu diễn đường dẫn (Path)**.

Các thao tác quản lý file nâng cao được giao cho module:
    
    
    shutil

(viết tắt của **Shell Utilities**)

* * *

# 2\. pathlib + shutil

Trong thực tế luôn dùng cùng nhau
    
    
    from pathlib import Path
    import shutil

Đây là cặp đôi rất phổ biến.

* * *

# 3\. copyfile()

Đơn giản nhất.
    
    
    from pathlib import Path
    import shutil
    
    src = Path("chapter001.txt")
    
    dst = Path("backup.txt")
    
    shutil.copyfile(src, dst)

Kết quả
    
    
    chapter001.txt
    
    ↓
    
    backup.txt

* * *

## Điều kiện

Nếu
    
    
    backup.txt

đã tồn tại

↓

Nó sẽ bị ghi đè.

* * *

# 4\. copy()

Thông dụng hơn.
    
    
    shutil.copy(src, dst)

Khác biệt:

Ngoài nội dung file còn sao chép quyền truy cập cơ bản.

Ví dụ
    
    
    src = Path("cover.jpg")
    
    dst = Path("images/cover.jpg")
    
    shutil.copy(src, dst)

* * *

# 5\. copy2()

Đây là hàm mình dùng nhiều nhất.
    
    
    shutil.copy2(src, dst)

Ngoài nội dung còn giữ:

  * thời gian tạo (tùy nền tảng) 
  * thời gian sửa 
  * metadata (nếu hệ điều hành hỗ trợ) 



Ví dụ
    
    
    from pathlib import Path
    import shutil
    
    shutil.copy2(
        Path("chapter001.txt"),
        Path("backup/chapter001.txt")
    )

* * *

# 6\. So sánh

Hàm| Nội dung| Metadata  
---|---|---  
copyfile| ✅| ❌  
copy| ✅| Một phần  
copy2| ✅| Gần như đầy đủ  
  
Trong các dự án thực tế:

> **Ưu tiên`copy2()`**

* * *

# 7\. Copy thư mục
    
    
    downloads/
    
        Naruto/
    
            chapter001.txt
    
            cover.jpg

↓
    
    
    import shutil
    
    shutil.copytree(
        "downloads",
        "backup"
    )

↓
    
    
    backup/
    
        Naruto/
    
            chapter001.txt
    
            cover.jpg

* * *

# 8\. Nếu thư mục tồn tại
    
    
    shutil.copytree(
        src,
        dst
    )

↓
    
    
    FileExistsError

* * *

Python 3.8+

Có thể
    
    
    shutil.copytree(
        src,
        dst,
        dirs_exist_ok=True
    )

↓

Không lỗi.

* * *

# 9\. move()

Di chuyển.
    
    
    from pathlib import Path
    import shutil
    
    src = Path("chapter001.txt")
    
    dst = Path("downloads/chapter001.txt")
    
    shutil.move(src, dst)

↓
    
    
    chapter001.txt
    
    ↓
    
    downloads/chapter001.txt

File gốc biến mất.

* * *

# 10\. rename() vs move()

Buổi trước học
    
    
    Path.rename()

Ví dụ
    
    
    file.rename(new_path)

Thực chất

↓

Có thể là

  * đổi tên 
  * di chuyển 



* * *

`shutil.move()`

Có khả năng:

  * di chuyển giữa nhiều ổ đĩa 
  * hoạt động ổn định hơn trong nhiều tình huống 



* * *

# 11\. rmtree()

Xóa toàn bộ cây thư mục.
    
    
    import shutil
    
    shutil.rmtree(
        "downloads"
    )

↓

Toàn bộ
    
    
    downloads/

bị xóa.

* * *

Khác với
    
    
    Path.rmdir()

chỉ xóa được thư mục rỗng.

* * *

# 12\. disk_usage()

Kiểm tra dung lượng ổ cứng.
    
    
    import shutil
    
    usage = shutil.disk_usage("/")

Windows
    
    
    usage = shutil.disk_usage("C:\\")

Kết quả
    
    
    print(usage)

↓
    
    
    usage(total=...)
    
    used=...
    
    free=...

* * *

# 13\. unpack_archive()

Giải nén.
    
    
    import shutil
    
    shutil.unpack_archive(
        "backup.zip",
        "backup"
    )

* * *

# 14\. make_archive()

Nén.
    
    
    import shutil
    
    shutil.make_archive(
        "backup",
    
        "zip",
    
        "downloads"
    )

↓

Sinh
    
    
    backup.zip

* * *

# 15\. Ví dụ thực tế

Crawler tải
    
    
    chapter001.tmp

↓

Sau khi tải xong

↓

Copy vào Backup

↓

Đổi thành
    
    
    chapter001.txt

↓

Xóa file tạm.
    
    
    from pathlib import Path
    import shutil
    
    tmp = Path("chapter001.tmp")
    
    backup = Path("backup/chapter001.tmp")
    
    backup.parent.mkdir(
        parents=True,
        exist_ok=True
    )
    
    shutil.copy2(tmp, backup)
    
    tmp.replace(
        tmp.with_suffix(".txt")
    )

* * *

# 16\. Backup Database
    
    
    db = Path(
        "database/crawler.db"
    )
    
    backup = Path(
        "backup/crawler.db"
    )
    
    backup.parent.mkdir(
        parents=True,
        exist_ok=True
    )
    
    shutil.copy2(
        db,
        backup
    )

* * *

# 17\. Backup toàn bộ dự án
    
    
    import shutil
    
    shutil.copytree(
        "downloads",
        "backup/downloads",
    
        dirs_exist_ok=True
    )

* * *

# 18\. Đồng bộ thư mục

Giả sử
    
    
    downloads/

↓

Sang
    
    
    backup/
    
    
    import shutil
    from pathlib import Path
    
    src = Path("downloads")
    
    dst = Path("backup")
    
    shutil.copytree(
        src,
    
        dst,
    
        dirs_exist_ok=True
    )

* * *

# 19\. Copy ảnh
    
    
    cover = Path(
        "cover.jpg"
    )
    
    gallery = Path(
        "gallery/cover.jpg"
    )
    
    gallery.parent.mkdir(
        parents=True,
        exist_ok=True
    )
    
    shutil.copy2(
        cover,
    
        gallery
    )

* * *

# 20\. Ví dụ tổng hợp
    
    
    from pathlib import Path
    import shutil
    
    DOWNLOAD = Path("downloads")
    
    BACKUP = Path("backup")
    
    BACKUP.mkdir(
        exist_ok=True
    )
    
    for chapter in DOWNLOAD.rglob("*.txt"):
    
        target = BACKUP / chapter.relative_to(DOWNLOAD)
    
        target.parent.mkdir(
            parents=True,
            exist_ok=True
        )
    
        shutil.copy2(
            chapter,
    
            target
        )

Đây là một chương trình backup cực kỳ thực tế.

* * *

# 21\. Thiết kế lớp FileManager
    
    
    from pathlib import Path
    import shutil
    
    class FileManager:
    
        def copy(self, src, dst):
    
            dst = Path(dst)
    
            dst.parent.mkdir(
                parents=True,
                exist_ok=True
            )
    
            shutil.copy2(src, dst)
    
        def move(self, src, dst):
    
            dst = Path(dst)
    
            dst.parent.mkdir(
                parents=True,
                exist_ok=True
            )
    
            shutil.move(src, dst)
    
        def delete_tree(self, path):
    
            shutil.rmtree(path)
    
        def backup(self, src, backup):
    
            shutil.copytree(
                src,
    
                backup,
    
                dirs_exist_ok=True
            )

* * *

# 22\. Ứng dụng trong Dashboard

Người dùng nhấn
    
    
    Backup Library

↓
    
    
    manager.backup(
        "downloads",
    
        "backup"
    )

* * *

Người dùng nhấn
    
    
    Restore

↓
    
    
    manager.backup(
        "backup",
    
        "downloads"
    )

* * *

# 23\. Những lỗi thường gặp

## Sai
    
    
    Path("a.txt").copy()

↓

Không tồn tại.

* * *

## Sai
    
    
    shutil.copy(
        "a.txt",
    
        "downloads"
    )

Nếu
    
    
    downloads/

chưa tồn tại

↓

Lỗi.

Đúng
    
    
    Path("downloads").mkdir(
        parents=True,
    
        exist_ok=True
    )

* * *

## Sai
    
    
    Path("downloads").rmdir()

↓

Nếu có dữ liệu

↓

Lỗi.

Đúng
    
    
    shutil.rmtree(
        "downloads"
    )

* * *

# 24\. Bài tập thực hành

## Bài 1

Tạo:
    
    
    downloads/
    
        chapter001.txt

Copy thành:
    
    
    backup/
    
        chapter001.txt

* * *

## Bài 2

Copy toàn bộ:
    
    
    downloads/

↓
    
    
    backup/

* * *

## Bài 3

Viết chương trình:

  * tìm toàn bộ file `.txt`
  * copy sang 


    
    
    backup/

vẫn giữ nguyên cấu trúc thư mục.

> Gợi ý: dùng `rglob()`, `relative_to()` và `copy2()`.

* * *

## Bài 4

Viết lớp
    
    
    BackupManager

Có:
    
    
    backup_database()
    
    backup_downloads()
    
    restore()
    
    delete_backup()

* * *

## Bài 5 (Project lớn)

Viết một chương trình **Incremental Backup**.

Yêu cầu:

  * Chỉ copy file mới. 
  * Nếu file cũ không thay đổi thì bỏ qua. 
  * Nếu file đã thay đổi thì ghi đè. 
  * Giữ nguyên cấu trúc thư mục. 



**Gợi ý:** Có thể so sánh:

  * `exists()`
  * `stat().st_size`
  * `stat().st_mtime`



Ví dụ:
    
    
    src_info = src.stat()
    dst_info = dst.stat()
    
    if (
        not dst.exists()
        or src_info.st_size != dst_info.st_size
        or src_info.st_mtime > dst_info.st_mtime
    ):
        shutil.copy2(src, dst)

Đây là nguyên lý nền tảng của nhiều công cụ đồng bộ dữ liệu như `rsync` (ở mức đơn giản).

* * *

# Tổng kết buổi 8

Trong buổi học này, bạn đã nắm được cách kết hợp **`pathlib`** và **`shutil`** để quản lý file ở mức chuyên nghiệp:

  * Sao chép file với `copyfile()`, `copy()` và `copy2()`. 
  * Sao chép cả cây thư mục với `copytree()`. 
  * Di chuyển file bằng `move()`. 
  * Xóa toàn bộ thư mục với `rmtree()`. 
  * Nén và giải nén với `make_archive()` và `unpack_archive()`. 
  * Xây dựng các công cụ backup, restore và đồng bộ thư mục. 



Đến đây, bạn đã gần như làm chủ toàn bộ thao tác quản lý file/thư mục trong `pathlib`. Ở **Buổi 9** , chúng ta sẽ đi sâu vào các tính năng nâng cao như **`resolve()`** , **`absolute()`** , **`expanduser()`** , **`samefile()`** , **`owner()`** , **`group()`** , **`chmod()`** , **`lchmod()`** (nếu hệ điều hành hỗ trợ) và cách làm việc với **Symbolic Link** , giúp bạn hiểu sâu hơn về mối quan hệ giữa `pathlib` và hệ điều hành.

