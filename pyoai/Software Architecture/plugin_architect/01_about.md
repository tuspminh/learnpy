# Plugin Architecture Deep Dive

# Buổi 1: Tư duy về Plugin Architecture

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ hiểu:
> 
>   * Plugin thực sự là gì. 
>   * Vì sao phần mềm lớn đều sử dụng Plugin Architecture. 
>   * Khi nào nên dùng Plugin. 
>   * Sự khác nhau giữa Module, Package, Library, Framework, Extension và Plugin. 
>   * Các nguyên lý thiết kế phía sau Plugin Architecture. 
>   * Phân tích kiến trúc của các hệ thống nổi tiếng. 
>   * Thiết kế một framework plugin đơn giản. 
> 


* * *

# 1\. Bài toán

Giả sử bạn viết một chương trình tải truyện.

Ban đầu chỉ hỗ trợ TruyenFull.
    
    
    main.py
    
    ↓
    
    download()
    
    ↓
    
    TruyenFull

Code
    
    
    def download(url):
        if "truyenfull.vn" in url:
            ...

Rất đơn giản.

* * *

Một tháng sau.

Khách hàng yêu cầu:

  * NovelBin 
  * Wattpad 
  * TangThuVien 



Bạn sửa
    
    
    def download(url):
        if "truyenfull.vn" in url:
            ...
    
        elif "novelbin.com" in url:
            ...
    
        elif "wattpad.com":
            ...

Có vẻ vẫn ổn.

* * *

Sau một năm

Có

  * 20 website 
  * 30 website 
  * 100 website 



Hàm của bạn biến thành
    
    
    if ...
    
    elif ...
    
    elif ...
    
    elif ...
    
    elif ...
    
    elif ...
    
    elif ...

Mỗi lần thêm website mới

↓

Sửa code

↓

Test lại

↓

Build lại

↓

Deploy lại

Đây gọi là

> **Hard-coded architecture**

Đây là điều Plugin Architecture muốn giải quyết.

* * *

# 2\. Một cách tiếp cận khác

Thay vì sửa code.

Ta tạo
    
    
    plugins/
    
        truyenfull.py
    
        wattpad.py
    
        novelbin.py

Framework chỉ làm
    
    
    Load plugin
    
    ↓
    
    Đăng ký
    
    ↓
    
    Sử dụng

Muốn thêm website

Chỉ cần
    
    
    plugins/
    
        metruyen.py

Không sửa framework.

Đây chính là Plugin.

* * *

# 3\. Plugin là gì?

Plugin là một thành phần độc lập.

Nó có thể:

  * được cài thêm 
  * được gỡ bỏ 
  * được thay thế 
  * được nâng cấp 



mà **không cần sửa code của chương trình chính**.

Plugin luôn chạy **bên trong một Host Application**.

Ví dụ
    
    
    Host
    
    ↓
    
    Plugin A
    
    Plugin B
    
    Plugin C

Host không biết Plugin là gì.

Host chỉ biết:

> Plugin phải tuân theo một Interface.

* * *

# 4\. Ví dụ thực tế

## VS Code

VSCode chỉ cung cấp

  * Editor 
  * API 



Còn

  * Python 
  * Docker 
  * GitHub 
  * Remote SSH 
  * Vim 



đều là plugin.

Nếu bỏ Extension Python

VSCode vẫn chạy.

* * *

## Chrome

Chrome

↓

Extension

  * AdBlock 
  * Grammarly 
  * Dark Reader 



Chrome không cần sửa code.

* * *

## pytest

pytest

↓

pytest-html

pytest-cov

pytest-xdist

Bạn cài
    
    
    pip install pytest-html

pytest tự nhận.

Không sửa pytest.

* * *

## Home Assistant

Home Assistant

↓

Philips Hue

↓

Xiaomi

↓

MQTT

↓

Tuya

Tất cả đều là plugin.

* * *

## Scrapy

Spider

Pipeline

Middleware

Extension

đều là Plugin.

* * *

# 5\. Module ≠ Plugin

Đây là lỗi rất nhiều người mới học nhầm.

## Module
    
    
    math.py

Import
    
    
    import math

Module chỉ là

> File Python.

* * *

Plugin thì khác.

Plugin phải:

✔ có Interface

✔ có Metadata

✔ có Lifecycle

✔ được Discover

✔ được Load động

✔ có thể Enable/Disable

* * *

# 6\. Package
    
    
    mypackage/
    
        __init__.py
    
        a.py
    
        b.py

Package chỉ là

Nhóm Module.

Không phải Plugin.

* * *

# 7\. Library

Ví dụ
    
    
    requests

Ta gọi
    
    
    requests.get(...)

Bạn điều khiển Library.
    
    
    Application
    
    ↓
    
    requests

* * *

# 8\. Framework

Ví dụ

  * Django 
  * Flask 
  * FastAPI 



Lúc này

Framework điều khiển bạn.
    
    
    Framework
    
    ↓
    
    Your Code

Đây gọi là

> Inversion of Control (IoC)

* * *

# 9\. Plugin

Plugin nằm trong Framework.
    
    
    Framework
    
    ↓
    
    Plugin

Framework quyết định

  * Khi nào load 
  * Khi nào gọi 
  * Khi nào hủy 



Plugin không quyết định.

* * *

# 10\. So sánh

Thành phần| Có Interface| Load động| Có Lifecycle| Có Metadata| Có thể cài thêm  
---|---|---|---|---|---  
Module| ❌| ❌| ❌| ❌| ❌  
Package| ❌| ❌| ❌| ❌| ❌  
Library| ❌| ❌| ❌| ❌| ❌  
Framework| Có| Không áp dụng| Có| Có| Không  
Plugin| ✅| ✅| ✅| ✅| ✅  
  
* * *

# 11\. Open/Closed Principle

Đây là nguyên lý quan trọng nhất.

Một hệ thống tốt

> **Open for Extension**

Có thể mở rộng.

Nhưng

> **Closed for Modification**

Không sửa code cũ.

Ví dụ

Sai
    
    
    if site == "A":
        ...
    
    elif site == "B":
        ...
    
    elif site == "C":
        ...

Muốn thêm
    
    
    D

↓

Sửa code.

* * *

Đúng
    
    
    Plugin D

↓

Copy vào thư mục

↓

Framework tự nhận.

Không sửa framework.

* * *

# 12\. Dependency Inversion Principle (DIP)

Framework không phụ thuộc Plugin.

Plugin cũng không phụ thuộc Framework cụ thể.

Cả hai cùng phụ thuộc vào **Interface**.
    
    
    Framework
         │
         ▼
     ISource (Interface)
         ▲
         │
    Plugin A   Plugin B

Điều này giúp bạn có thể thay thế Plugin A bằng Plugin B mà không cần thay đổi Framework.

* * *

# 13\. Kiến trúc tổng quát của một Plugin Framework
    
    
                    +----------------------+
                    |      Application     |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |   Plugin Manager     |
                    +----------+-----------+
                               |
              +----------------+----------------+
              |                |                |
              v                v                v
       Plugin Loader     Plugin Registry   Event System
              |                |                |
              +----------------+----------------+
                               |
             +-----------------+-----------------+
             |                 |                 |
             v                 v                 v
       Plugin A          Plugin B         Plugin C

Trong các buổi tiếp theo, chúng ta sẽ xây dựng lần lượt từng khối này.

* * *

# 14\. Dự án xuyên suốt khóa học

Chúng ta sẽ phát triển một framework plugin cho hệ thống crawler truyện:
    
    
    StoryFramework/
    │
    ├── app.py
    ├── framework/
    │   ├── manager.py
    │   ├── loader.py
    │   ├── registry.py
    │   └── lifecycle.py
    │
    ├── interfaces/
    │   └── source.py
    │
    ├── plugins/
    │   ├── truyenfull/
    │   ├── wattpad/
    │   ├── novelbin/
    │   └── ...
    │
    ├── core/
    │   ├── crawler.py
    │   ├── parser.py
    │   └── downloader.py
    │
    └── config/

Đến cuối khóa, khi muốn hỗ trợ thêm một website mới, bạn chỉ cần thêm:
    
    
    plugins/
        metruyen/

Framework sẽ:

  1. Phát hiện plugin. 
  2. Import động. 
  3. Kiểm tra tính hợp lệ. 
  4. Khởi tạo. 
  5. Đăng ký. 
  6. Đưa plugin vào hoạt động. 



Không cần sửa `app.py`, `crawler.py` hay `manager.py`.

* * *

# 15\. Kiến thức sẽ học trong các buổi tới

Để xây dựng framework trên, chúng ta sẽ đi sâu vào các chủ đề:

  * `abc` và `typing.Protocol` để định nghĩa hợp đồng (contract) cho plugin. 
  * `importlib` để import module động. 
  * `inspect` để khám phá class và phương thức. 
  * `pathlib` và `pkgutil` để tìm plugin trong thư mục. 
  * `importlib.metadata` và Entry Points để phát hiện plugin được cài qua `pip`. 
  * Registry Pattern để quản lý plugin. 
  * Event Bus và Hook System để plugin tương tác với nhau. 
  * Dependency Injection để truyền ngữ cảnh cho plugin. 
  * Hot Reload để cập nhật plugin khi ứng dụng đang chạy. 
  * Packaging và phát hành plugin lên PyPI. 



* * *

# Bài tập thực hành

### Bài 1

Vẽ sơ đồ kiến trúc của một ứng dụng ghi chú (Note App) có khả năng mở rộng bằng plugin.

Gợi ý:

  * Plugin Export PDF 
  * Plugin Markdown 
  * Plugin Theme 
  * Plugin AI Summary 
  * Plugin Spell Check 



* * *

### Bài 2

Liệt kê ít nhất 10 phần mềm hoặc framework mà bạn biết đang sử dụng Plugin Architecture. Với mỗi phần mềm, xác định:

  * Host Application là gì? 
  * Plugin là gì? 
  * Lợi ích của việc dùng plugin trong trường hợp đó. 



* * *

### Bài 3 (chuẩn bị cho Buổi 2)

Hãy suy nghĩ và trả lời:

> Nếu Framework không biết trước sẽ có những plugin nào, thì bằng cách nào nó có thể gọi đúng hàm của mọi plugin?

Đây chính là câu hỏi dẫn chúng ta đến **Buổi 2: Interface, ABC, Protocol và Plugin Contract** , nơi chúng ta sẽ xây dựng "hợp đồng" giữa Framework và Plugin trước khi bắt đầu viết Plugin Manager thực sự.

