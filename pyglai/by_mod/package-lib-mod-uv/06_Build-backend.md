## Build-backend là gì?

Trong hệ sinh thái Python, build-backend là công cụ thực thi việc đóng gói mã nguồn (compile và đóng gói) từ các file code thô của bạn thành các định dạng phân phối chuẩn như Wheel (`.whl`) hoặc Source Distribution (`.tar.gz`) để có thể cài đặt được qua `pip`.

Trước đây, `setuptools` (thông qua file `setup.py`) vừa đảm nhận vai trò quản lý vừa làm nhiệm vụ đóng gói. Từ khi chuẩn PEP 517 và PEP 518 ra đời, nhiệm vụ đóng gói được tách riêng ra cho các build-backend chuyên trách (ví dụ: `hatchling`, `flit`, `setuptools`, `poetry-core`).

* * *

## Cách thức hoạt động của Build-backend

Quá trình đóng gói diễn ra theo 4 bước khép kín dưới sự điều phối của công cụ quản lý (gọi là build-frontend như `uv`, `pip`, hoặc `build`):
    
    
    [Người dùng] ──> [Build-Frontend (uv / pip)] ──> đọc pyproject.toml ──> [Build-Backend (Hatchling/Flit)] ──> File .whl / .tar.gz
    

## Bước 1: Frontend đọc cấu hình `[build-system]`

Khi bạn chạy lệnh `uv build`, công cụ front-end (`uv`) sẽ mở file `pyproject.toml` của bạn ra và tìm khối khai báo này:
    
    
    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"
    

Qua đây, `uv` biết được nó cần phải tải thư viện `hatchling` về một môi trường cô lập tạm thời để phục vụ việc đóng gói.

## Bước 2: Frontend gọi API của Backend

`uv` (Frontend) sẽ gọi các hàm tiêu chuẩn (được quy định bởi PEP 517) bên trong `hatchling` (Backend), cụ thể là:

  * `build_wheel()`: Yêu cầu tạo file cài đặt nhanh `.whl`.
  * `build_sdist()`: Yêu cầu tạo file mã nguồn nén `.tar.gz`.



## Bước 3: Backend thu thập và xử lý file

Lúc này, build-backend bắt đầu làm việc trực tiếp với mã nguồn của bạn:

  * Quét thư mục: Nó tìm các file `.py` dựa theo cấu hình cấu trúc thư mục (ví dụ: quét thư mục `src/my_package`).
  * Tạo Metadata: Nó tự động tạo ra các file đặc biệt như `METADATA` (chứa tên package, phiên bản, các thư viện phụ thuộc), `RECORD` (danh sách hash mã hóa của tất cả các file để kiểm tra tính toàn vẹn).
  * Biên dịch (nếu có): Nếu dự án của bạn có code C/C++/Rust (như thư viện `numpy`), build-backend thích hợp (như `setuptools` hoặc `maturin`) sẽ gọi compiler để biên dịch thành file nhị phân `.so` hoặc `.pyd`.



## Bước 4: Đóng gói và xuất bản thành phẩm

Cuối cùng, backend nén toàn bộ mã nguồn cùng thư mục metadata đã tạo thành một file duy nhất (định dạng file `.whl` thực chất là một file `.zip` được đổi đuôi) và bàn giao lại cho frontend (`uv`) lưu vào thư mục `dist/`.

* * *

## So sánh các Build-backend phổ biến hiện nay

Tùy thuộc vào loại dự án, bạn có thể chọn một trong các backend sau để điền vào `pyproject.toml`:

Build-backend| Nhà phát triển| Đặc điểm / Phù hợp nhất với  
---|---|---  
`hatchling`| PyPA (Hatch)| Khuyên dùng cho dự án thuần Python. Rất nhanh, hỗ trợ cấu trúc `src/` hoàn hảo, cấu hình tường minh, là mặc định mới của nhiều công cụ.  
`setuptools.build_meta`| PyPA| Dự án kế thừa hoặc có code C/C++. To lớn, lâu đời, tương thích tốt nhất nếu bạn cần viết custom script để compile extension.  
`flit_core.buildapi`| Flit| Cực kỳ tối giản. Dành cho các thư viện thuần Python siêu nhỏ gọn, không cần cấu hình phức tạp.  
`poetry.core.masonry.api`| Poetry| Hệ sinh thái Poetry. Chỉ nên dùng nếu toàn bộ đội ngũ của bạn đang dùng Poetry làm công cụ quản lý chính.  
`maturin`| PyO3| Dự án Python kết hợp Rust. Tự động biên dịch code Rust thành extension cho Python cực kỳ mạnh mẽ.  
  
Trong mô hình Monorepo với `uv` mà bạn đang hướng tới, `hatchling` là lựa chọn tối ưu và đồng bộ nhất. Bạn có muốn tôi hướng dẫn cách cấu hình chi tiết file `pyproject.toml` sử dụng `hatchling` để tự động nhận diện chính xác các thư mục độc lập trong phân vùng `packages/` không?