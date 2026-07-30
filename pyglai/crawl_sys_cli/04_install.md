Để biến các file mã nguồn Python trên thành một công cụ dòng lệnh (CLI) chạy độc lập toàn hệ thống—nghĩa là bạn có thể gõ trực tiếp lệnh `crawl worker scrape ...` từ bất kỳ thư mục nào mà không cần gõ `python cli.py`—bạn chỉ cần đóng gói nó bằng **Setuptools**.

Dưới đây là các bước thực hiện chi tiết:

1\. Chuẩn bị cấu trúc thư mục chuẩn

Bạn hãy sắp xếp lại các file code hiện tại vào một cấu trúc thư mục như sau để Python có thể đóng gói chính xác:

text
    
    
    my_crawler/
    ├── setup.py
    └── crawl_cli/
        ├── __init__.py
        ├── cli.py
        └── tasks.py
    

Hãy thận trọng khi sử dụng mã.

_(Lưu ý: File`__init__.py` chỉ cần tạo trống, không cần viết nội dung gì bên trong)._

* * *

2\. Sửa đổi nhẹ mã nguồn để tương thích dạng Package

Vì chúng ta đưa các file vào trong thư mục `crawl_cli`, bạn cần sửa lại một chút dòng `import` ở đầu các file:

  * Trong file **`crawl_cli/cli.py`** :  
Sửa dòng `from tasks import ...` thành:

python
        
        from crawl_cli.tasks import scrape_novel_task
        

Hãy thận trọng khi sử dụng mã.

  * Trong file **`crawl_cli/tasks.py`** :  
Giữ nguyên cấu hình Celery hoặc đổi tên cho tường minh nếu muốn.



* * *

3\. Tạo file `setup.py`

Tạo file `setup.py` nằm ở thư mục ngoài cùng (`my_crawler/setup.py`) với nội dung sau:

python
    
    
    from setuptools import setup, find_packages
    
    setup(
        name='my-crawl-cli',
        version='1.0.0',
        packages=find_packages(),
        include_package_data=True,
        install_requires=[
            'click',
            'celery',
            'redis',
            'requests',
            'beautifulsoup4',
        ],
        entry_points={
            'console_scripts': [
                # Định nghĩa tên lệnh CLI toàn cục
                # Cú pháp: <tên_lệnh> = <thư_mục>.<file_cli>:<hàm_chính>
                'crawl = crawl_cli.cli:cli',
            ],
        },
    )
    

Hãy thận trọng khi sử dụng mã.

* * *

4\. Cài đặt ứng dụng vào hệ thống

Mở Terminal, di chuyển vào thư mục `my_crawler` (nơi chứa file `setup.py`) và chạy lệnh cài đặt dưới dạng **Editable Mode** (chế độ lập trình viên, sửa code đến đâu CLI cập nhật đến đấy không cần cài lại):

bash
    
    
    pip install -e .
    

Hãy thận trọng khi sử dụng mã.

Sau khi chạy xong lệnh này, hệ thống của bạn đã chính thức sở hữu lệnh `crawl`. Bạn có thể tắt Terminal, di chuyển sang bất kỳ thư mục nào khác để kiểm tra.

* * *

5\. Cách vận hành hệ thống mới với lệnh `crawl`

Bây giờ toàn bộ trải nghiệm của bạn sẽ chuẩn xác như một ứng dụng CLI thực thụ:

**Cửa sổ 1: Khởi động Worker chạy ngầm**  
 _(Do cấu trúc package thay đổi, lệnh khởi động Celery cũng sẽ thay đổi theo đường dẫn mới)_

bash
    
    
    celery -A crawl_cli.tasks worker --loglevel=info
    

Hãy thận trọng khi sử dụng mã.

**Cửa sổ 2: Sử dụng lệnh CLI từ bất kỳ đâu**  
Bạn không cần dùng `python cli.py` nữa, hãy gõ thẳng:

  * **Kiểm tra các lệnh hỗ trợ:**

bash
        
        crawl --help
        

Hãy thận trọng khi sử dụng mã.

  * **Ra lệnh cào truyện:**

bash
        
        crawl scrape http://truyen.com --chaps 20
        

Hãy thận trọng khi sử dụng mã.

  * **Xem bảng trạng thái và tiến độ:**

bash
        
        crawl status
        

Hãy thận trọng khi sử dụng mã.

  * **Tạm dừng tác vụ:**

bash
        
        crawl stop http://truyen.com
        

Hãy thận trọng khi sử dụng mã.

  * **Cào tiếp tục:**

bash
        
        crawl resume http://truyen.com
        

Hãy thận trọng khi sử dụng mã.




Hệ thống CLI Crawl Worker chạy ngầm của bạn hiện đã hoàn chỉnh cả về tính năng lưu trạng thái lẫn trải nghiệm dòng lệnh. Bạn có gặp khó khăn gì trong bước cấu hình file **`setup.py`** hay cần tối ưu thêm phần nào không?

