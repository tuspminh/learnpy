Đây là bài mà 99% khóa học trên YouTube bỏ qua, nhưng lại là bài đầu tiên mình check khi phỏng vấn junior. Không có bài này, bạn mãi chỉ là người viết script, không phải developer.
LEVEL 5 - BÀI 8: Tư duy Dev Chuyên Nghiệp - Git, Venv, Pip
1. Venv - Mỗi dự án một thế giới riêng

Vấn đề: Dự án A cần pandas 1.0, dự án B cần pandas 2.0. Cài chung vào máy sẽ xung đột.

Giải pháp: Mỗi dự án một môi trường ảo.
Bash

# Tạo dự án mới
mkdir du-an-moi && cd du-an-moi

# Tạo venv (chỉ làm 1 lần)
python -m venv venv

# Kích hoạt venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
# Khi thấy (venv) ở đầu terminal là thành công

# Bây giờ mọi pip install chỉ nằm trong dự án này
pip install requests pandas

# Thoát venv
deactivate

Quy tắc vàng: Luôn pip freeze > requirements.txt trước khi push code. Người khác chỉ cần pip install -r requirements.txt là có đủ thư viện.
2. Cấu trúc dự án chuẩn đi làm

Đừng bao giờ để 10 file .py nằm lung tung ngoài Desktop. Cấu trúc chuẩn:
Code

quan-ly-chi-tieu/
├── venv/                 # môi trường ảo (không push lên git)
├── src/
│   ├── __init__.py
│   ├── models.py         # chứa class SinhVien, QuanLyChiTieu
│   ├── utils.py          # chứa hàm tinh_tien_dien, la_so_nguyen_to
│   └── main.py           # file chạy chính, chứa menu
├── data/
│   └── chi_tieu.json
├── requirements.txt      # pip freeze
├── .gitignore            # nói git bỏ qua file nào
└── README.md             # mô tả dự án

File .gitignore tối thiểu:
Code

venv/
__pycache__/
*.pyc
data/
.env

3. Git - Cứu cánh cuộc đời dev

Git không phải để cho ngầu, mà để không bao giờ mất code.
Bash

# Cài đặt 1 lần
git config --global user.name "Hung"
git config --global user.email "you@gmail.com"

# Bắt đầu dự án
git init
git add .
git commit -m "feat: hoan thanh quan ly chi tieu bai 7"

# Đẩy lên Github (tạo repo trống trên github trước)
git remote add origin https://github.com/ten-ban/quan-ly-chi-tieu.git
git push -u origin main

Từ giờ mỗi khi làm xong 1 tính năng:
Bash

git add .
git commit -m "feat: them chuc nang thong ke theo thang"
git push

Nhà tuyển dụng chỉ cần nhìn Github của bạn có commit đều, có README là đã +10 điểm.
4. Viết code sạch (Clean Code) - PEP8

VS Code cài extension Black Formatter và Flake8. Sau đó setting:

    Tên biến, hàm: snake_case
    Tên Class: PascalCase - QuanLyChiTieu
    Hằng số: UPPER_CASE - VAT = 0.1
    Mỗi hàm không quá 20 dòng. Dài quá thì tách nhỏ.
    Luôn có docstring và type hint như Bài 6.

Bấm Shift + Alt + F để Black tự format code cho đẹp.
BÀI TẬP BÀI 8 - LÀM THẬT

Nhiệm vụ duy nhất, bắt buộc:

    Refactor lại project quản lý chi tiêu Bài 7 theo cấu trúc src/ ở trên.
    Tạo venv, tạo requirements.txt
    Tạo file .gitignore và README.md (viết mô tả project, cách chạy)
    Đẩy lên Github tạo 1 repo public tên python-personal-expense-tracker
    Gửi mình link Github repo.

Mình sẽ review repo của bạn như một tech lead review: nhìn vào commit message có rõ không, có README không, có tách hàm tốt không.

Làm xong bài này, bạn đã chính thức có tác phong của một Python Developer Junior.

Bài tiếp theo là bài cuối Bài 9: Chọn Ngành - Bạn muốn kiếm tiền với Python bằng cách nào? Mình sẽ cho bạn chọn 1 trong 3 nhánh: Backend (FastAPI), Automation/Data (Pandas), hoặc AI Bot. Bạn muốn đi nhánh nào?