Thư viện pathlib (cụ thể là đối tượng pathlib.Path) là công cụ hiện đại và chuẩn mực nhất từ Python 3.4 trở đi để xử lý đường dẫn hệ thống [docs.python.org]. Thay vì xử lý đường dẫn dưới dạng chuỗi ký tự (string) như thư viện cũ os.path, pathlib biến mỗi đường dẫn thành một đối tượng thông minh (Object) giúp mã nguồn cực kỳ trực quan và dễ đọc [docs.python.org]. [1, 2, 3, 4]

## Các thuộc tính bóc tách đường dẫn (Thuộc tính không cần dấu ())

Giả sử bạn có một đối tượng đường dẫn: p = Path("/home/user/documents/report.pdf")

* p.name: Lấy tên file hoàn chỉnh kèm đuôi (report.pdf).
* p.stem: Lấy tên file không chứa phần mở rộng (report).
* p.suffix: Lấy phần mở rộng (đuôi file) kèm dấu chấm (.pdf).
* p.parent: Lấy thư mục chứa file đó (/home/user/documents).
* p.parts: Tách đường dẫn thành một tuple các thư mục con (('/', 'home', 'user', 'documents', 'report.pdf')). [5] 

## Các phương thức thao tác hệ thống (Phương thức cần dấu ())

* Path.cwd(): Lấy thư mục làm việc hiện tại (tương đương os.getcwd()).
* p.exists(): Kiểm tra đường dẫn này có tồn tại thật trên ổ cứng hay không.
* p.is_file() / p.is_dir(): Kiểm tra đối tượng là tệp tin hay là thư mục.
* p.mkdir(parents=True, exist_ok=True): Tạo thư mục mới. Tham số giúp tự động tạo cả thư mục cha nếu chưa có và không báo lỗi nếu thư mục đã tồn tại.
* p.with_suffix('.txt'): Đổi đuôi file cũ thành đuôi file mới một cách nhanh chóng. [6, 7, 8, 9, 10] 

## Ví dụ mã nguồn thực tế
Dưới đây là cách sử dụng pathlib.Path cho các tác vụ phổ biến:

```
from pathlib import Path


# 1. Khởi tạo và nối đường dẫn bằng toán tử gạch chéo '/' cực kỳ trực quan
base_dir = Path("data")
file_path = base_dir / "users" / "profile.json"
print("Đường dẫn:", file_path)  # Tự động đổi dấu gạch theo hệ điều hành

# 2. Bóc tách thông tin từ file_path
print("Tên file:", file_path.name)       # profile.json
print("Tên không đuôi:", file_path.stem) # profile
print("Đuôi file:", file_path.suffix)    # .json
print("Thư mục cha:", file_path.parent)   # data/users

# 3. Tạo thư mục tự động nếu chưa cóoutput_dir = Path("output/logs")
output_dir.mkdir(parents=True, exist_ok=True)

# 4. Tìm kiếm file bằng tính năng Glob (Tìm tất cả file .txt trong thư mục hiện tại)current_dir = Path(".")for txt_file in current_dir.glob("*.txt"):
    print("Tìm thấy file text:", txt_file.name)
```

Nếu bạn muốn áp dụng pathlib vào mã nguồn của mình, bạn có thể cho biết:

* Bạn đang cần đọc/ghi nội dung file trực tiếp bằng pathlib không?
* Bạn có cần quét và lọc danh sách toàn bộ file trong một thư mục phức tạp nào không?


[1] [https://autogis-site.readthedocs.io](https://autogis-site.readthedocs.io/en/latest/lessons/lesson-2/managing-file-paths.html)
[2] [https://miguendes.me](https://miguendes.me/python-pathlib)
[3] [https://towardsdatascience.com](https://towardsdatascience.com/10-examples-to-master-python-pathlib-1249cc77de0b/)
[4] [https://realpython.com](https://realpython.com/videos/creating-path-objects-from-strings/)
[5] [https://pythontutorials.eu](https://pythontutorials.eu/basic/files-and-folders/)
[6] [https://alemsbaja.hashnode.dev](https://alemsbaja.hashnode.dev/demystifying-python-paths-a-comprehensive-guide-to-the-path-module-for-effortless-file-and-directory-management)
[7] [https://www.geeksforgeeks.org](https://www.geeksforgeeks.org/python/pathlib-module-in-python/)
[8] [https://geekpython.in](https://geekpython.in/python-pathlib-module)
[9] [https://doc.rust-lang.org](https://doc.rust-lang.org/std/path/struct.Path.html?search=Path%20-%3E%20OsStr)
[10] [https://www.tradingcode.net](https://www.tradingcode.net/python/pathlib-path-isdir-method/)
