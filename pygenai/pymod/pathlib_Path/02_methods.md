Dưới đây là bảng tổng hợp đầy đủ và hệ thống nhất về các **Class**, **Property** (Thuộc tính) và **Method** (Phương thức) của mô-đun `pathlib`.

---

## 1. Các Class chính trong `pathlib`

`pathlib` chia đường dẫn làm 2 nhóm: **Pure paths** (chỉ thao tác chuỗi/ký tự, không truy cập ổ đĩa) và **Concrete paths** (thao tác trực tiếp với hệ điều hành/ổ đĩa).

```
                 PurePath
               /          \
     PurePosixPath      PureWindowsPath
          |                    |
      PosixPath           WindowsPath
           \                  /
               Path (Dùng nhiều nhất)

```

| Class | Mô tả |
| --- | --- |
| **`Path`** | Class chính thường dùng nhất. Tự động chuyển thành `PosixPath` (trên Linux/Mac) hoặc `WindowsPath` (trên Windows). Hỗ trợ cả thao tác chuỗi lẫn I/O ổ đĩa. |
| **`PurePath`** | Dùng khi chỉ muốn xử lý chuỗi đường dẫn mà **không thực hiện I/O** (không kiểm tra `exists()`, không đọc/ghi file). |
| **`PurePosixPath`** / **`PosixPath`** | Chuyên xử lý đường dẫn kiểu Unix (Linux, macOS, dùng `/`). |
| **`PureWindowsPath`** / **`WindowsPath`** | Chuyên xử lý đường dẫn kiểu Windows (dùng `\`). |

---

## 2. Các Property (Thuộc tính) quan trọng

Giả sử khởi tạo: `p = Path("/home/user/project/data.csv")`

| Property | Ý nghĩa | Kết quả ví dụ với `p` |
| --- | --- | --- |
| **`p.name`** | Tên tệp hoặc thư mục cuối cùng (gồm cả đuôi) | `'data.csv'` |
| **`p.stem`** | Tên tệp **không** chứa phần mở rộng (đuôi) | `'data'` |
| **`p.suffix`** | Phần mở rộng (đuôi tệp) | `'.csv'` |
| **`p.suffixes`** | Danh sách các đuôi (dành cho file nhiều đuôi như `.tar.gz`) | `['.tar', '.gz']` |
| **`p.parent`** | Thư mục cha trực tiếp | `PosixPath('/home/user/project')` |
| **`p.parents`** | Trình duyệt danh sách tất cả các thư mục tổ tiên (`p.parents[0]`, `p.parents[1]`, ...) | Sequence chứa `/home/user/project`, `/home/user`,... |
| **`p.parts`** | Tuple chứa tất cả các thành phần cấu thành đường dẫn | `('/', 'home', 'user', 'project', 'data.csv')` |
| **`p.anchor`** | Phần gốc (Root + Drive nếu có) | `'/'` (Linux) hoặc `'C:\\'` (Windows) |
| **`p.drive`** | Tên ổ đĩa (chỉ áp dụng trên Windows) | `''` (Linux) hoặc `'C:'` (Windows) |
| **`p.root`** | Ký tự gốc của hệ điều hành | `'/'` hoặc `'\'` |

---

## 3. Các Method (Phương thức) thao tác trên đường dẫn

Các phương thức này không tương tác với ổ đĩa, chỉ biến đổi logic đường dẫn (có sẵn ở cả `PurePath` và `Path`).

| Method | Mô tả | Ví dụ / Kết quả |
| --- | --- | --- |
| **`is_absolute()`** | Kiểm tra xem có phải đường dẫn tuyệt đối hay không | `p.is_absolute() -> True/False` |
| **`is_relative_to(*other)`** | Kiểm tra xem đường dẫn có nằm trong thư mục gốc `other` không | `p.is_relative_to("/home/user") -> True` |
| **`joinpath(*other)`** | Nối thêm đường dẫn (tương đương dùng toán tử `/`) | `Path("a").joinpath("b", "c")` |
| **`with_name(name)`** | Thay đổi tên tệp (bao gồm cả đuôi) | `p.with_name("new.txt") -> .../new.txt` |
| **`with_stem(stem)`** | Thay đổi tên tệp nhưng **giữ nguyên đuôi** | `p.with_stem("new") -> .../new.csv` |
| **`with_suffix(suffix)`** | Thay đổi phần mở rộng của tệp | `p.with_suffix(".json") -> .../data.json` |
| **`relative_to(*other)`** | Lấy đường dẫn tương đối so với một thư mục cha | `p.relative_to("/home/user") -> project/data.csv` |

---

## 4. Các Method (Phương thức) tương tác Hệ thống & I/O (Chỉ có ở `Path`)

### 4.1. Kiểm tra trạng thái & Lấy thông tin

| Method | Mô tả |
| --- | --- |
| **`exists()`** | Kiểm tra tệp hoặc thư mục có tồn tại thực sự trên ổ đĩa hay không |
| **`is_file()`** | Trả về `True` nếu đường dẫn trỏ tới tệp |
| **`is_dir()`** | Trả về `True` nếu đường dẫn trỏ tới thư mục |
| **`is_symlink()`** | Trả về `True` nếu đường dẫn là một liên kết mềm (Symbolic link) |
| **`stat()`** | Lấy thông tin tệp (kích thước `st_size`, thời gian sửa đổi `st_mtime`, ...) |
| **`resolve()`** | Chuyển thành đường dẫn tuyệt đối chuẩn hóa (xóa `..`, giải mã symlink) |
| **`absolute()`** | Chuyển thành đường dẫn tuyệt đối (không rút gọn symlink) |

### 4.2. Khởi tạo & Định vị hệ thống (Classmethod)

| Method | Mô tả |
| --- | --- |
| **`Path.cwd()`** | Lấy thư mục làm việc hiện tại (Current Working Directory) |
| **`Path.home()`** | Lấy thư mục cá nhân của người dùng hiện tại (Home directory) |

### 4.3. Đọc / Ghi tệp

| Method | Mô tả |
| --- | --- |
| **`read_text(encoding, ...)`** | Đọc toàn bộ nội dung tệp dưới dạng chuỗi `str` |
| **`write_text(data, ...)`** | Ghi chuỗi `str` vào tệp (ghi đè mặc định) |
| **`read_bytes()`** | Đọc nội dung tệp dưới dạng nhị phân (`bytes`) |
| **`write_bytes(data)`** | Ghi dữ liệu nhị phân (`bytes`) vào tệp |
| **`open(mode, ...)`** | Mở tệp (tương tự hàm `open()` tích hợp sẵn) |

### 4.4. Duyệt và Tìm kiếm

| Method | Mô tả |
| --- | --- |
| **`iterdir()`** | Duyệt qua tất cả tệp/thư mục con trực tiếp bên trong thư mục |
| **`glob(pattern)`** | Tìm kiếm tệp/thư mục theo mẫu (ví dụ: `*.py`, `data_*.csv`) |
| **`rglob(pattern)`** | Tìm kiếm đệ quy (Recursive glob) xuyên qua tất cả thư mục con (tương đương `glob("**/*")`) |

### 4.5. Quản lý Tệp & Thư mục

| Method | Mô tả |
| --- | --- |
| **`mkdir(parents=False, exist_ok=False)`** | Tạo thư mục mới. Tránh lỗi dùng `parents=True, exist_ok=True` |
| **`touch(exist_ok=True)`** | Tạo một tệp rỗng mới (hoặc cập nhật timestamp nếu tệp đã tồn tại) |
| **`rename(target)`** | Đổi tên hoặc di chuyển tệp/thư mục tới vị trí mới |
| **`replace(target)`** | Đổi tên/di chuyển, bắt buộc ghi đè nếu `target` đã tồn tại |
| **`unlink(missing_ok=False)`** | Xóa tệp hoặc liên kết mềm (`missing_ok=True` tránh lỗi khi file không tồn tại) |
| **`rmdir()`** | Xóa một thư mục **rỗng** |