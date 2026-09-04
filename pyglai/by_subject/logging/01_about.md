Mô-đun `logging` chuẩn trong Python giúp bạn ghi lại các sự kiện, lỗi và thông tin chẩn đoán trong quá trình chạy chương trình. [1, 2] 

## Các mức độ ghi log (Log Levels)

Python chia log thành 5 mức độ từ thấp đến cao theo độ nghiêm trọng:

  * DEBUG: Thông tin chi tiết, thường chỉ dùng khi gỡ lỗi.
  * INFO: Xác nhận rằng mọi thứ vẫn hoạt động bình thường.
  * WARNING: Cảnh báo về một sự cố tiềm ẩn hoặc tình huống bất ngờ trong tương lai gần.
  * ERROR: Lỗi nghiêm trọng khiến chương trình không thể thực hiện một chức năng cụ thể.
  * CRITICAL: Lỗi cực kỳ nghiêm trọng, có thể khiến toàn bộ ứng dụng bị dừng.



## 4 Thành phần chính của Logging

  * Loggers: Nơi tiếp nhận thông điệp log từ mã nguồn của bạn.
  * Handlers: Quyết định nơi các thông điệp log sẽ đi về đâu (ví dụ: ghi ra màn hình console, ghi vào file, gửi qua email).
  * Filters: Cung cấp thêm bộ lọc chi tiết để quyết định log nào được đi qua.
  * Formatters: Định dạng hiển thị của chuỗi log (thêm thời gian, mức độ, tên module, dòng code). [3, 4] 



## Ví dụ cơ bản

Cách sử dụng đơn giản nhất với cấu hình mặc định:
    
    
    import logging
    
    logging.basicConfig(level=logging.INFO)
    logging.debug("Thông tin debug (sẽ bị ẩn vì mức tối thiểu là INFO)")
    logging.info("Chương trình bắt đầu chạy")
    logging.warning("Cảnh báo dung lượng ổ đĩa sắp đầy")
    logging.error("Không thể kết nối cơ sở dữ liệu")
    

Cho tôi biết:

  1. Bạn muốn ghi log ra file hay hiển thị trên màn hình console?
  2. Ứng dụng của bạn là script nhỏ hay dự án lớn (nhiều file/module)?



Tôi sẽ viết cho bạn một đoạn mã cấu hình `logging` nâng cao phù hợp nhất.

  


[1] [https://blog.sentry.io](https://translate.google.com/translate?u=https://blog.sentry.io/logging-in-python-a-developers-guide/&hl=vi&sl=en&tl=vi&client=sge)

[2] [https://codelearn.io](https://codelearn.io/sharing/logging-python-system-talk-module)

[3] [https://viblo.asia](https://viblo.asia/p/log-cho-python-su-dung-sao-cho-dung-va-de-nhan-biet-WAyK8Mk9ZxX)

[4] [https://sematext.com](https://translate.google.com/translate?u=https://sematext.com/blog/python-logging/&hl=vi&sl=en&tl=vi&client=sge)