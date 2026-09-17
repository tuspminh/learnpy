Để cấu hình Monorepo với nhiều thư viện độc lập sử dụng `uv` làm công cụ quản lý và `hatchling` làm build-backend, bạn thiết lập chi tiết các file `pyproject.toml` như sau.

* * *

## 1\. Cấu hình tại Thư mục gốc (`my-monorepo/pyproject.toml`)

File này đóng vai trò quản lý không gian làm việc (Workspace), quy định nơi chứa các package và quản lý các công cụ phát triển chung (như linter, formatter).
    
    
    [project]
    name = "my-monorepo"
    version = "0.1.0"
    description = "Hệ sinh thái monorepo quản lý bởi uv và hatchling"
    readme = "README.md"
    requires-python = ">=3.10"
    dependencies = []
    
    # Bật tính năng Workspace của uv để gom các package con
    [tool.uv.workspace]
    members = ["packages/*"]
    
    # Công cụ phát triển chung cho toàn bộ monorepo (ví dụ: ruff để format/lint code)
    [tool.uv]
    dev-dependencies = [
        "ruff>=0.3.0",
        "pytest>=8.0.0",
    ]
    

* * *

## 2\. Cấu hình tại Package con độc lập (`packages/my-core/pyproject.toml`)

Đây là file cấu hình của thư viện Core. `hatchling` sẽ dựa vào file này để đóng gói.
    
    
    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"
    
    [project]
    name = "my-core"
    version = "0.1.0"
    description = "Thư viện lõi chứa các tiện ích dùng chung"
    requires-python = ">=3.10"
    dependencies = [
        "requests>=2.31.0", # Package từ PyPI mà my-core cần dùng
    ]
    
    # Cấu hình cụ thể cho Hatchling để nhận diện cấu trúc src layout
    [tool.hatch.build.targets.wheel]
    packages = ["src/my_core"]
    

* * *

## 3\. Cấu hình tại Package con có phụ thuộc nội bộ (`packages/my-api/pyproject.toml`)

Thư viện `my-api` này vừa phụ thuộc vào một thư viện bên ngoài (`fastapi`), vừa phụ thuộc vào thư viện `my-core` nằm cùng trong workspace.
    
    
    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"
    
    [project]
    name = "my-api"
    version = "0.1.0"
    description = "Thư viện API phục vụ ứng dụng"
    requires-python = ">=3.10"
    dependencies = [
        "fastapi>=0.110.0", # Package từ PyPI
        "my-core",           # Khai báo phụ thuộc vào package my-core nội bộ
    ]
    
    # Định tuyến cho uv biết: Lấy "my-core" từ dự án hiện tại thay vì tải trên PyPI về
    [tool.uv.sources]
    my-core = { workspace = true }
    
    # Cấu hình Hatchling đóng gói cho my-api
    [tool.hatch.build.targets.wheel]
    packages = ["src/my_api"]
    

* * *

## 💡 Quy trình làm việc hàng ngày với cấu trúc này

  1. Cài đặt môi trường phát triển:  
Tại thư mục gốc, bạn chỉ cần chạy:
         
         uv sync
         

`uv` sẽ tự tạo môi trường ảo `.venv`, liên kết tất cả các gói trong `packages/*` lại với nhau dưới dạng _Editable mode_. Bạn có thể thay đổi code ở `my-core`, và `my-api` sẽ lập tức cập nhật mà không cần cài đặt lại.
  2. Chạy test cho toàn bộ dự án:
         
         uv run pytest
         

  3. Build thành phẩm độc lập:  
Khi cần xuất bản, chạy lệnh build tại thư mục gốc và chỉ định package mong muốn:
         
         uv build --package my-core
         uv build --package my-api
         

Thành phẩm `.whl` và `.tar.gz` riêng biệt của từng thư viện sẽ được xuất ra thư mục `dist/` ở root.



Tiếp theo, bạn có muốn tôi hướng dẫn cách thiết lập `pytest` để chạy kiểm thử tự động cho cấu trúc Monorepo này, hoặc cách cấu hình `uv publish` để đẩy các thư viện lên PyPI (hoặc một Private Registry nội bộ) không?