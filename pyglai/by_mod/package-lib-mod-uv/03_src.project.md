Khi sử dụng cấu trúc `src` layout trong Python, bạn nên import theo dạng `from projectname import module` (bỏ qua `src.`).

Dưới đây là lý do tại sao cấu trúc này là chuẩn mực và cách cấu hình để hệ thống hoạt động mượt mà.

## Tại sao không nên dùng `from src.projectname`?

  1. Tránh lỗi khi đóng gói (Distribution): Khi bạn đóng gói thư viện (build thành file `.whl` hoặc `.tar.gz`) để cài đặt qua `pip`, thư mục `src/` sẽ bị loại bỏ. Chỉ có thư mục `projectname` được cài đặt vào thư mục `site-packages` của hệ thống. Nếu bạn viết `from src.projectname`, mã nguồn của bạn sẽ bị lỗi hoàn toàn sau khi cài đặt.
  2. Tính nhất quán: Người dùng bên ngoài khi cài thư viện của bạn sẽ dùng `import projectname`. Việc bạn tự import chính nó trong nội bộ bằng `from projectname` giúp code đồng nhất ở mọi nơi.



* * *

## Cách thiết lập để IDE và Python hiểu được `from projectname`

Vì thư mục `projectname` nằm bên trong `src/`, Python sẽ không tự động tìm thấy nó nếu bạn chạy script trực tiếp từ thư mục gốc. Bạn cần áp dụng các giải pháp sau:

## 1\. Cài đặt ở chế độ chỉnh sửa (Editable Mode) - Khuyên dùng 🌟

Đây là cách chuẩn nhất khi phát triển dự án. Bạn chỉ cần chạy lệnh sau ở thư mục gốc (nơi chứa file `pyproject.toml` hoặc `setup.py`):
    
    
    pip install -e .
    

Lệnh này sẽ tạo một liên kết (link) từ thư mục dự án vào môi trường ảo của bạn. Khi đó, Python sẽ hiểu `projectname` là một thư viện toàn cục và bạn có thể `import projectname` thoải mái.

## 2\. Cấu hình cho IDE (VS Code / PyCharm)

Nếu IDE của bạn báo lỗi gạch chân đỏ khi `import projectname`, hãy chỉ định `src` làm thư mục gốc chứa source code:

  * VS Code: Thêm cấu hình sau vào file `.vscode/settings.json`:
        
        {
          "python.analysis.extraPaths": ["./src"]
        }
        

  * PyCharm: Nhấp chuột phải vào thư mục `src` -> Mark Directory as -> Sources Root.



* * *

## Tóm tắt cấu trúc thư mục chuẩn
    
    
    my_project/
    ├── pyproject.toml      # File cấu hình đóng gói
    ├── src/
    │   └── projectname/    # Thư mục chứa code chính
    │       ├── __init__.py
    │       ├── core.py
    │       └── utils.py
    └── tests/              # Thư mục kiểm thử (bên ngoài src)
        └── test_core.py
    

Khi viết code trong file `tests/test_core.py` hoặc `src/projectname/core.py`, bạn đều gọi:
    
    
    from projectname.utils import my_function
    

* * *

Nếu bạn đang gặp khó khăn trong việc thiết lập, hãy chia sẻ thêm:

  * Bạn đang dùng công cụ nào để quản lý dự án? (Poetry, Hatch, Setuptools, hay Pipenv?)
  * Bạn đang viết ứng dụng độc lập hay thư viện để chia sẻ cho người khác?



Tôi sẽ hướng dẫn bạn cách viết file cấu hình (`pyproject.toml`) chuẩn xác nhất cho trường hợp đó!