Khi dùng `uv add` trong mô hình Monorepo (Workspace), bạn phải chỉ định rõ gói nào cần thêm thư viện bằng cờ `--package <tên-package>` hoặc di chuyển (`cd`) trực tiếp vào thư mục chứa package đó. [1, 2] 

Cơ chế hoạt động và cách sử dụng lệnh `uv add` trong monorepo cụ thể như sau.

## 1\. Hai cách thêm thư viện vào Package con

## Cách 1: Đứng từ thư mục gốc (Root) dùng cờ `-p` / `--package`

Bạn không cần đổi thư mục, chỉ cần gọi tên package đích thông qua cờ `--package`: [2] 
    
    
    uv add requests --package my-api
    

Lệnh này sẽ cập nhật file `packages/my-api/pyproject.toml` và tự động đồng bộ vào file `uv.lock` chung.

## Cách 2: Di chuyển vào thư mục của Package con (`cd`)

Bạn đi thẳng vào thư mục của dự án thành viên rồi chạy `uv add` như một dự án độc lập bình thường: [3] 
    
    
    cd packages/my-api
    uv add requests
    

Sau đó, bạn có thể quay lại thư mục gốc và chạy `uv sync` để cập nhật môi trường ảo chung. [4] 

* * *

## 2\. Cách thêm một Package nội bộ trong Workspace

Khi `my-api` cần phụ thuộc vào `my-core` (cả hai cùng nằm trong monorepo), bạn có thể thêm trực tiếp bằng lệnh: [5] 
    
    
    uv add my-core --package my-api
    

  *   * Hành vi của `uv`: `uv` sẽ tự động điền `my-core` vào mục `dependencies` và tạo cấu hình trỏ cục bộ tại `[tool.uv.sources]` trong file `pyproject.toml` của `my-api`. [2] 
  * 


* * *

## 3\. Thêm thư viện chung cho toàn bộ Workspace (`--group` / `--dev`)

Nếu bạn muốn thêm các công cụ dùng chung cho toàn bộ dự án (như `pytest`, `ruff`), hãy thêm vào nhóm phát triển ở thư mục gốc: [6, 7] 
    
    
    uv add --dev pytest
    

Hoặc dùng nhóm tùy chỉnh (dependency-groups) định nghĩa tại file `pyproject.toml` ở root. [6, 7] 

Bạn có muốn tìm hiểu cách tối ưu hóa `uv sync` hoặc cấu hình Docker multi-stage build cực nhanh cho cấu trúc Monorepo này không?

  


[1] [https://github.com](https://github.com/PUDAP/puda/blob/main/docs/uv.md)

[2] [https://pydevtools.com](https://pydevtools.com/handbook/how-to/how-to-set-up-a-python-monorepo-with-uv-workspaces/)

[3] [https://han8931.github.io](https://han8931.github.io/uv-packages/)

[4] [https://han8931.github.io](https://han8931.github.io/uv-packages/)

[5] [https://github.com](https://github.com/astral-sh/uv/issues/10960)

[6] [https://docs.astral.sh](https://docs.astral.sh/uv/concepts/projects/dependencies/)

[7] [https://gafni.dev](https://gafni.dev/blog/cracking-the-python-monorepo/)