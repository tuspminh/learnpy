Khi bạn muốn đóng gói thành các thư viện độc lập (phát hành riêng biệt thành nhiều file `.whl` / `.tar.gz`) trong cùng một kho mã nguồn (Monorepo) bằng công cụ `uv`, kiến trúc chuẩn nhất là sử dụng tính năng `uv` Workspaces.

Thay vì nhét tất cả các folder package trực tiếp vào trong một thư mục `src/` duy nhất ở root, `uv` khuyến khích bạn chia nhỏ mỗi thư viện thành một workspace member (mỗi thư viện có một file `pyproject.toml` và một thư mục `src/` riêng).

Dưới đây là cấu trúc thư mục chuẩn và cách thiết lập:

## 1\. Cấu trúc thư mục Monorepo với `uv`
    
    
    my-monorepo/
    ├── pyproject.toml      # Cấu hình Workspace gốc (Root)
    ├── uv.lock             # Quản lý lockfile chung cho toàn bộ dự án
    └── packages/           # Thư mục chứa các thư viện độc lập
        ├── my-core/        # Thư viện 1: Core logic
        │   ├── pyproject.toml
        │   └── src/
        │       └── my_core/
        │           └── __init__.py
        └── my-api/         # Thư viện 2: API layer (phụ thuộc vào my-core)
            ├── pyproject.toml
            └── src/
                └── my_api/
                    └── __init__.py
    

## 2\. Cấu hình file `pyproject.toml`

## Tại thư mục gốc (`my-monorepo/pyproject.toml`):

Khai báo cho `uv` biết nơi chứa các thư viện độc lập.
    
    
    [project]
    name = "my-monorepo"
    version = "0.1.0"
    description = "Monorepo chứa các thư viện độc lập"
    dependencies = []
    
    [tool.uv.workspace]
    members = ["packages/*"]
    

## Tại thư viện Core (`packages/my-core/pyproject.toml`):

Cấu hình như một thư viện Python tiêu chuẩn, sử dụng build-backend mà bạn chọn (ví dụ: `hatchling` hoặc `setuptools`).
    
    
    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"
    
    [project]
    name = "my-core"
    version = "0.1.0"
    dependencies = [] # Các package từ PyPI nếu có
    
    [tool.hatch.build.targets.wheel]
    packages = ["src/my_core"]
    

## Tại thư viện API (`packages/my-api/pyproject.toml`):

Nếu `my-api` cần sử dụng các hàm từ `my-core`, bạn khai báo phụ thuộc nội bộ bằng tính năng `workspace = true` của `uv`:
    
    
    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"
    
    [project]
    name = "my-api"
    version = "0.1.0"
    dependencies = [
        "my-core", # Khai báo tên package
    ]
    
    [tool.uv.sources]
    my-core = { workspace = true } # Chỉ định uv lấy từ workspace nội bộ
    
    [tool.hatch.build.targets.wheel]
    packages = ["src/my_api"]
    

* * *

## 3\. Cách Import và Dùng Lệnh với `uv`

  * Cách Import: Trong code của `my-api`, bạn import thẳng từ tên package của core (bỏ qua `src`):
        
        from my_core.utils import helper_function
        

  * Phát triển và đồng bộ: Tại thư mục gốc monorepo, bạn chỉ cần chạy:
        
        uv sync
        

`uv` sẽ tự động liên kết (editable install) tất cả các package trong `packages/` vào môi trường ảo chung. Bạn chỉnh sửa code ở `my-core` thì `my-api` sẽ nhận được thay đổi ngay lập tức.
  * Đóng gói độc lập: Khi muốn build ra file `.whl` để upload lên PyPI cho từng thư viện, bạn di chuyển vào thư mục của thư viện đó hoặc dùng cờ `-p` (`--package`):
        
        uv build -p my-core
        uv build -p my-api
        




Bạn đã quyết định chọn build-backend nào cho các gói chưa (như `hatchling`, `setuptools`, hay `flit`)? Nếu chưa hoặc cần tôi hướng dẫn cách publish (đăng tải) các gói này lên PyPI bằng `uv publish`, hãy cho tôi biết nhé!