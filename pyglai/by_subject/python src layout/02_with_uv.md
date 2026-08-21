`uv` là một công cụ quản lý dự án Python siêu tốc được phát triển bởi [Astral](https://astral.sh/) (công ty đứng sau `Ruff`) [1.1]. Nó được viết bằng ngôn ngữ Rust, đóng vai trò thay thế toàn diện cho `pip`, `pip-tools`, `virtualenv`, `poetry`, và `pyenv` với tốc độ nhanh hơn từ 10 đến 100 lần [1.1].

Dưới đây là cách sử dụng `uv` để khởi tạo, quản lý cấu trúc `src` layout và điều hành dự án Python của bạn.

* * *

## 1\. Khởi tạo dự án `src` layout bằng `uv`

Mặc định, khi bạn tạo một dự án dạng thư viện (package) hoặc ứng dụng lớn, `uv` sẽ tự động áp dụng cấu trúc `src` layout tiêu chuẩn [1.2].

Để tạo một dự án mới, hãy chạy lệnh sau trong terminal:
    
    
    uv init --lib my_project
    

_(Nếu chỉ chạy`uv init`, nó sẽ tạo cấu trúc flat layout dạng ứng dụng đơn giản. Tham số `--lib` ép buộc `uv` tạo cấu trúc package chuyên nghiệp dạng `src` layout)._

## Cấu trúc thư mục do `uv` tự động tạo ra:
    
    
    my_project/
    ├── .gitignore
    ├── pyproject.toml       # Chứa toàn bộ cấu hình dự án, thư viện phụ thuộc
    ├── README.md
    └── src/                 # Thư mục nguồn
        └── my_project/
            ├── py.typed
            └── __init__.py  # Điểm khởi đầu của package
    

## 2\. Quản lý dự án với `uv` (Thay thế hoàn toàn Pip & Poetry)

`uv` quản lý toàn bộ vòng đời dự án (từ cài đặt Python, cài thư viện đến chạy mã) mà bạn không cần phải tự tay kích hoạt môi trường ảo (`source .venv/bin/activate`) [1.3].

  * Cài đặt tự động phiên bản Python mong muốn:  
Nếu máy bạn chưa có Python 3.12, `uv` sẽ tự động tải về và cấu hình riêng cho dự án mà không ảnh hưởng hệ thống [1.3].
        
        uv python pin 3.12
        

  * Thêm thư viện phụ thuộc (Dependencies):  
Thêm một thư viện (ví dụ: `requests`) vào dự án. `uv` sẽ tự động cập nhật file `pyproject.toml` và tạo file khóa `uv.lock` để cố định phiên bản [1.4, 1.5].
        
        uv add requests
        

  * Thêm thư viện dành cho môi trường phát triển (Dev Dependencies):  
Thêm các công cụ dùng để test hoặc format code (ví dụ: `pytest`) [1.6].
        
        uv add --dev pytest
        

  * Chạy mã nguồn trong cấu trúc `src` layout:  
Bạn không cần lo lắng về lỗi `ModuleNotFoundError`. Hãy dùng `uv run` để chạy, công cụ sẽ tự động nhận diện và nạp package trong `src/` vào môi trường [1.3].
        
        uv run python -c "import my_project; print('Package hoạt động tốt!')"
        

  * Chạy các công cụ kiểm thử (Test):
        
        uv run pytest
        




* * *

## 3\. Xem cấu hình `pyproject.toml` do `uv` tạo ra

Khi dùng `uv init --lib`, file cấu hình dự án của bạn sẽ được thiết lập tự động sử dụng build-backend hiện đại của chính Astral (`hatchling` hoặc hệ thống build của `uv` tùy phiên bản):
    
    
    [project]
    name = "my_project"
    version = "0.1.0"
    description = "Một dự án Python sử dụng uv và src layout"
    readme = "README.md"
    requires-python = ">=3.12"
    dependencies = [
        "requests>=2.31.0",
    ]
    
    [dependency-groups]
    dev = [
        "pytest>=8.0.0",
    ]
    
    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"
    

_(Lưu ý: Giống như Hatch,`hatchling` sẽ tự động quét thư mục `src/` để đóng gói `my_project` mà bạn không cần cấu hình thủ công đường dẫn `where = ["src"]` nữa)._

* * *

## Ưu điểm vượt trội của `uv` so với các công cụ khác

  1. Tốc độ cực hạn: Nhờ viết bằng Rust và cơ chế tận dụng tối đa bộ nhớ đệm (Global Cache) [1.1], việc cài đặt thư viện diễn ra gần như lập tức.
  2. Một cho tất cả: Thay vì cài `pyenv` quản lý Python, `virtualenv` quản lý môi trường ảo, `pip` cài thư viện; bạn chỉ cần cài duy nhất `uv` [1.1].
  3. Quản lý Tool độc lập: Bạn có thể chạy nhanh bất kỳ công cụ Python nào mà không cần cài vào dự án (Ví dụ: `uvx ruff check .` hoặc `uvx black .`).



Nếu bạn muốn biết cách cài đặt `uv` lên máy tính (Windows/Mac/Linux) hoặc cách chuyển đổi một dự án cũ (dùng `requirements.txt` hoặc `poetry`) sang `uv`, hãy cho tôi biết nhé!