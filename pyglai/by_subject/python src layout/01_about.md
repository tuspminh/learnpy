Cấu trúc `src` layout (bố cục nguồn) là mô hình tổ chức mã nguồn chuẩn hiện đại cho dự án Python, được khuyến nghị chính thức bởi [Hội đồng Đóng gói Python (PyPA)](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/). Điểm cốt lõi của cấu trúc này là đặt toàn bộ mã nguồn phân phối vào trong một thư mục riêng biệt có tên là `src/`, tách rời hoàn toàn khỏi thư mục gốc dự án. [1, 2, 3] 

Dưới đây là chi tiết toàn diện về cấu trúc, lý do áp dụng và cách cấu hình mô hình `src` layout.

* * *

## Bản vẽ cấu trúc thư mục tiêu chuẩn

Mô hình `src` layout chuẩn cho một dự án có tên gói là `my_package` sẽ có dạng như sau:
    
    
    my_project/
    ├── .gitignore
    ├── README.md
    ├── pyproject.toml           # File cấu hình đóng gói và công cụ chính hiện nay
    ├── requirements.txt         # (Tùy chọn) Danh sách thư viện phụ thuộc
    ├── docs/                    # Tài liệu hướng dẫn của dự án
    │   └── index.md
    ├── tests/                   # Thư mục chứa mã kiểm thử (nằm ngoài src/)
    │   ├── __init__.py
    │   └── test_core.py
    └── src/                     # Thư mục chứa mã nguồn bắt buộc
        └── my_package/          # Tên thư mục trùng với tên package khi import
            ├── __init__.py
            ├── core.py
            └── utils.py
    

* * *

## Tại sao nên dùng `src` layout thay vì `flat` layout?

Trình thông dịch Python mặc định luôn ưu tiên thêm thư mục làm việc hiện tại (`current working directory`) vào đầu danh sách đường dẫn tìm kiếm module (`sys.path`). Điều này gây ra nhiều vấn đề lớn mà `src` layout giải quyết triệt để: [1, 4] 

  *   * Tránh hiện tượng "Import nhầm" mã nguồn thô: Nếu dùng `flat` layout (mã nguồn nằm ngay thư mục gốc), khi bạn chạy lệnh kiểm thử, Python sẽ nạp trực tiếp file code thô ở thư mục hiện tại. Với `src` layout, thư mục hiện tại không chứa mã nguồn, ép buộc các công cụ test phải cài đặt dự án thành một package hoàn chỉnh rồi mới import được. [1, 4, 5] 
  * Phát hiện sớm lỗi đóng gói: Nếu bạn quên khai báo một file hoặc thư mục con trong cấu hình build, `flat` layout vẫn chạy tốt trên máy của bạn (vì file thô vẫn nằm đó). Tuy nhiên, khi người dùng tải về sẽ bị lỗi. `src` layout ép bạn phải chạy thử bản build được cài đặt, giúp phát hiện ngay lập tức các tệp bị thiếu. [1, 5, 6] 
  * Ngăn chặn ô nhiễm không gian tên (Namespace Pollution): Trong chế độ cài đặt có thể chỉnh sửa (`editable installs - pip install -e .`), `flat` layout sẽ vô tình đưa cả các tệp cấu hình không liên quan như `setup.py`, `tox.ini` vào đường dẫn import toàn cục, dễ gây xung đột hệ thống. [1] 
  * 


* * *

## Cách cấu hình dự án chạy với `src` layout

Do mã nguồn nằm sâu bên trong thư mục `src/`, bạn cần khai báo rõ ràng cho các công cụ xây dựng (`build backends`) biết nơi tìm mã nguồn thông qua file `pyproject.toml`. [7, 8] 

## 1\. Cấu hình bằng Setuptools

Nếu dự án của bạn sử dụng công cụ đóng gói truyền thống `setuptools`:
    
    
    [build-system]
    requires = ["setuptools>=61.0.0", "wheel"]
    build-backend = "setuptools.build_meta"
    
    [project]
    name = "my_package"
    version = "0.1.0"
    
    [tool.setuptools.packages.find]
    where = ["src"]  # Chỉ định tìm kiếm mã nguồn bên trong thư mục src
    

## 2\. Cấu hình bằng Hatch

Hatch là công cụ quản lý dự án Python hiện đại và nó mặc định tự động nhận diện cấu trúc `src` layout mà không cần cấu hình thêm: [2] 
    
    
    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"
    
    [project]
    name = "my_package"
    version = "0.1.0"
    

* * *

## Cách chạy mã và Test trong `src` layout

Vì mã nguồn không nằm ở thư mục gốc, nếu bạn chạy lệnh `python src/my_package/core.py` theo cách thông thường, hệ thống sẽ báo lỗi `ModuleNotFoundError` khi các file tự import lẫn nhau. Để làm việc với cấu trúc này, bạn áp dụng 2 cách sau:

  *   * Khi phát triển dự án (Development): Cài đặt dự án ở chế độ `editable` để mọi thay đổi trong mã nguồn được cập nhật ngay lập tức mà không cần cài đặt lại.
        
        pip install -e .
        

  * Chạy các bài kiểm tra (Testing): Sử dụng `pytest` ở thư mục gốc, công cụ sẽ tự động nhận diện môi trường cài đặt để chạy test.
        
        pytest
        

[1, 7] 
  * 


Nếu bạn muốn biết cách tự động hóa việc tạo cấu trúc này bằng các công cụ như `uv` hay `Poetry`, hoặc cần giải pháp cấu hình `src` layout cho ứng dụng Flask / FastAPI, hãy cho tôi biết nhé! [2, 9] 

  


[1] [https://packaging.python.org](https://translate.google.com/translate?u=https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/&hl=vi&sl=en&tl=vi&client=sge)

[2] [https://www.pyopensci.org](https://translate.google.com/translate?u=https://www.pyopensci.org/python-package-guide/package-structure-code/python-package-structure.html&hl=vi&sl=en&tl=vi&client=sge)

[3] [https://realpython.com](https://translate.google.com/translate?u=https://realpython.com/ref/best-practices/project-layout/&hl=vi&sl=en&tl=vi&client=sge)

[4] [https://github.com](https://github.com/pypa/packaging.python.org/blob/main/source/discussions/src-layout-vs-flat-layout.rst)

[5] [https://pydevtools.com](https://pydevtools.com/handbook/explanation/src-layout-vs-flat-layout/)

[6] [https://www.youtube.com](https://www.youtube.com/watch?v=sW1qUZ_nSXk)

[7] [https://www.youtube.com](https://www.youtube.com/watch?v=b-LJ1xzIo8Q)

[8] [https://www.youtube.com](https://www.youtube.com/watch?v=Lr1koR-YkMw)

[9] [https://www.jcheng.org](https://www.jcheng.org/post/python-and-the-src-vs-flat-layout-debate/)