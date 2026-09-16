Tham số `format` trong hàm `logging.basicConfig()` của Python dùng để định nghĩa cấu trúc hiển thị của các dòng nhật ký (log). [1, 2] 

## Cú pháp cơ bản
    
    
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logging.info("Đây là một thông báo!")
    

_Kết quả xuất ra:_
    
    
     2026-09-16 18:09:23,123 - INFO - Đây là một thông báo!
    

* * *

## Các thuộc tính định dạng (LogRecord Attributes) phổ biến

Bạn có thể kết hợp các biến định dạng dưới đây trong chuỗi mẫu (chuỗi dùng định dạng mặc định `%`):

Thuộc tính| Ý nghĩa / Giá trị trả về| Ví dụ kết quả  
---|---|---  
`%(asctime)s`| Thời gian diễn ra sự kiện (dạng human-readable)| `2026-09-16 18:09:23,123`  
`%(levelname)s`| Tên cấp độ log (DEBUG, INFO, WARNING, ERROR, CRITICAL)| `INFO`  
`%(message)s`| Thông điệp log do người dùng truyền vào| `Đây là một thông báo!`  
`%(name)s`| Tên của logger tạo ra log này (mặc định là `root`)| `root` hoặc `__main__`  
`%(filename)s`| Tên tệp nguồn chứa dòng mã ghi log| `main.py`  
`%(funcName)s`| Tên hàm gọi dòng mã ghi log| `my_function`  
`%(lineno)d`| Số dòng trong mã nguồn nơi log được gọi| `15`  
`%(threadName)s`| Tên của luồng (thread) thực thi dòng mã| `MainThread`  
`%(process)d`| ID của tiến trình (PID) đang chạy hệ thống| `4312`  
  
* * *

## Thay đổi phong cách định dạng (`style`)

Từ Python 3.2+, bạn có thể chọn các kiểu định dạng chuỗi khác nhau thông qua tham số `style` (`%`, `{` hoặc `$`): [1, 3] 

  *   * Kiểu `%` (Mặc định): `format='%(asctime)s [%(levelname)s] %(message)s'`
  * Kiểu `{` (str.format): `format='{asctime} [{levelname}] {message}', style='{'`
  * Kiểu `$` (string.Template): `format='${asctime} [${levelname}] ${message}', style='$'` [1, 4] 
  * 


Ví dụ cấu hình bằng kiểu `{`:
    
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='[{asctime}] [{levelname}] ({filename}:{lineno}) {message}',
        style='{'
    )
    

Bạn có muốn tự chỉnh sửa định dạng thời gian (`datefmt`), xuất log ra tệp đồng thời với console hay cấu hình log dạng JSON để phục vụ môi trường Production không? Hãy cho tôi biết yêu cầu cụ thể của bạn nhé.

  


[1] [https://docs.python.org](https://docs.python.org/3/howto/logging.html)

[2] [https://signoz.io](https://signoz.io/guides/what-is-pythons-default-logging-formatter/)

[3] [https://docs.python.org](https://docs.python.org/3/library/logging.html)

[4] [https://gist.github.com](https://gist.github.com/c7e677eaade39b49a70b)