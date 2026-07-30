# Khóa học PySide6 từ A-Z

# Buổi 17: Threading và Concurrency - Làm chủ QThread, QRunnable và QThreadPool

> **Đây là một trong những buổi quan trọng nhất đối với lập trình GUI.**
> 
> Nếu không hiểu Thread, bạn sẽ gặp tình trạng:
> 
>   * Cửa sổ bị treo (Not Responding) 
>   * Không bấm được nút 
>   * ProgressBar không chạy 
>   * Không thể hủy tác vụ 
>   * Chương trình có trải nghiệm người dùng rất kém 
> 


Sau buổi này bạn sẽ:

  * Hiểu Thread là gì. 
  * Biết khi nào cần dùng `QThread`. 
  * Thành thạo mô hình **Worker + QThread** (được Qt khuyến nghị). 
  * Hiểu `QRunnable` và `QThreadPool`. 
  * Giao tiếp giữa Thread và GUI bằng Signal/Slot. 
  * Cập nhật ProgressBar theo thời gian thực. 
  * Hủy tác vụ đang chạy an toàn. 
  * Áp dụng vào các ứng dụng TTS, AI, Web Scraping, tải file,... 



* * *

# 1\. Vì sao GUI bị treo?

Ví dụ:
    
    
    def export_pdf():
        time.sleep(10)

Người dùng bấm:
    
    
    Xuất PDF

↓

Trong 10 giây:

  * Không bấm được nút. 
  * Không kéo cửa sổ. 
  * Không đóng ứng dụng. 



Đây gọi là **UI Freeze**.

* * *

# 2\. Event Loop

Qt hoạt động dựa trên Event Loop.
    
    
    QApplication
    
    ↓
    
    Event Loop
    
    ↓
    
    Mouse
    
    ↓
    
    Keyboard
    
    ↓
    
    Paint
    
    ↓
    
    Signal

Nếu một hàm chạy quá lâu:
    
    
    while True:
        ...

Event Loop bị chặn.

↓

GUI ngừng phản hồi.

* * *

# 3\. Sai lầm của người mới
    
    
    button.clicked.connect(download)

Trong `download()`:
    
    
    requests.get(...)

Nếu mất:
    
    
    30 giây

↓

GUI treo 30 giây.

* * *

# 4\. Thread là gì?

Thread là luồng thực thi.

Ví dụ:
    
    
    Main Thread
    
    ↓
    
    GUI

Nếu thêm:
    
    
    Worker Thread

↓

Tải dữ liệu.

↓

GUI vẫn hoạt động.

* * *

# 5\. Mô hình đúng
    
    
    GUI Thread
    
    ↓
    
    Button
    
    ↓
    
    Signal
    
    ↓
    
    Worker Thread
    
    ↓
    
    Xử lý
    
    ↓
    
    Signal
    
    ↓
    
    GUI

**Không để Worker Thread cập nhật Widget trực tiếp.**

* * *

# 6\. QThread

Qt cung cấp:
    
    
    from PySide6.QtCore import QThread

Có hai cách sử dụng:

  * Kế thừa `QThread`. 
  * **Worker + moveToThread()**. 



> Trong các ứng dụng chuyên nghiệp, Qt khuyến nghị dùng **Worker + moveToThread()** vì tách biệt rõ luồng và công việc.

* * *

# 7\. Worker Object
    
    
    from PySide6.QtCore import QObject
    
    class Worker(QObject):
    
        def run(self):
            ...

Worker chỉ chứa logic xử lý.

Không chứa giao diện.

* * *

# 8\. Tạo Thread
    
    
    thread = QThread()
    
    worker = Worker()
    
    worker.moveToThread(thread)
    
    thread.started.connect(worker.run)
    
    thread.start()

Luồng hoạt động:
    
    
    Main Thread
    
    ↓
    
    thread.start()
    
    ↓
    
    Worker.run()
    
    ↓
    
    Hoàn thành

* * *

# 9\. Signal giữa Thread và GUI

Ví dụ:
    
    
    from PySide6.QtCore import Signal
    
    class Worker(QObject):
    
        finished = Signal()

Khi xong:
    
    
    self.finished.emit()

MainWindow:
    
    
    worker.finished.connect(self.done)

Đây là cách an toàn để cập nhật giao diện.

* * *

# 10\. Gửi dữ liệu

Ví dụ:
    
    
    progress = Signal(int)

Worker:
    
    
    self.progress.emit(50)

GUI:
    
    
    worker.progress.connect(
        progressBar.setValue
    )

Không gọi:
    
    
    progressBar.setValue(...)

trực tiếp từ Worker Thread.

* * *

# 11\. Ví dụ ProgressBar

Worker:
    
    
    for i in range(101):
    
        self.progress.emit(i)
    
        time.sleep(0.05)

MainWindow:
    
    
    worker.progress.connect(
        self.progressBar.setValue
    )

ProgressBar chạy mượt.

GUI không bị treo.

* * *

# 12\. Kết thúc Thread

Sau khi Worker hoàn thành:
    
    
    worker.finished.connect(
        thread.quit
    )

Sau đó:
    
    
    thread.finished.connect(
        thread.deleteLater
    )

và:
    
    
    worker.finished.connect(
        worker.deleteLater
    )

Đây là cách giải phóng tài nguyên đúng chuẩn của Qt.

* * *

# 13\. Không nên làm

Sai:
    
    
    class MyThread(QThread):
    
        def run(self):
    
            self.window.label.setText(...)

Worker Thread truy cập trực tiếp GUI.

Có thể gây lỗi hoặc hành vi không xác định.

* * *

Nên:
    
    
    Worker
    
    ↓
    
    Signal
    
    ↓
    
    Main Thread
    
    ↓
    
    Widget

* * *

# 14\. QRunnable

Nếu có nhiều tác vụ nhỏ:
    
    
    Tải ảnh
    
    ↓
    
    Resize
    
    ↓
    
    OCR
    
    ↓
    
    Lưu

Không cần tạo nhiều `QThread`.

Dùng:
    
    
    QRunnable

* * *

# 15\. QThreadPool

Qt có sẵn:
    
    
    pool = QThreadPool.globalInstance()

Thực thi:
    
    
    pool.start(task)

Ưu điểm:

  * Tái sử dụng Thread. 
  * Nhanh. 
  * Tiết kiệm RAM. 



* * *

# 16\. Khi nào dùng gì?

Công việc| Nên dùng  
---|---  
Một tác vụ dài (TTS, tải file, AI)| Worker + `QThread`  
Nhiều tác vụ nhỏ độc lập| `QRunnable` \+ `QThreadPool`  
Chạy nền định kỳ| `QThread` hoặc `QTimer` tùy tình huống  
  
* * *

# 17\. Hủy tác vụ

Không nên:
    
    
    thread.terminate()

Vì có thể dừng luồng giữa chừng, làm tài nguyên hoặc dữ liệu ở trạng thái không nhất quán.

Nên:
    
    
    self.stop = True

Worker:
    
    
    while not self.stop:
        ...

Đây gọi là **Cooperative Cancellation**.

* * *

# 18\. Ví dụ Download
    
    
    GUI
    
    ↓
    
    Download
    
    ↓
    
    Worker
    
    ↓
    
    Signal
    
    ↓
    
    Progress
    
    ↓
    
    Done

Người dùng vẫn:

  * Di chuyển cửa sổ. 
  * Bấm Cancel. 
  * Chuyển Tab. 



* * *

# 19\. Ứng dụng thực tế

## Google TTS
    
    
    Nhập văn bản
    
    ↓
    
    Worker
    
    ↓
    
    Google API
    
    ↓
    
    Lưu MP3
    
    ↓
    
    Finished

* * *

## Web Scraping
    
    
    100 Website
    
    ↓
    
    ThreadPool
    
    ↓
    
    Lấy HTML
    
    ↓
    
    GUI

* * *

## AI
    
    
    Prompt
    
    ↓
    
    LLM
    
    ↓
    
    Signal
    
    ↓
    
    Hiển thị

* * *

## OCR
    
    
    Ảnh
    
    ↓
    
    Thread
    
    ↓
    
    Tesseract
    
    ↓
    
    Text

* * *

# 20\. Thread và SQLite

SQLite có những quy tắc riêng về kết nối giữa các luồng.

Một nguyên tắc an toàn là:

  * Không chia sẻ cùng một đối tượng kết nối (`Connection`) giữa nhiều thread. 
  * Mỗi worker nên tự mở và đóng kết nối của riêng mình (hoặc sử dụng cơ chế quản lý kết nối phù hợp). 



Điều này sẽ giúp tránh nhiều lỗi khó chẩn đoán.

* * *

# 21\. Những lỗi người mới thường gặp

## Lỗi 1
    
    
    time.sleep(10)

Trong Main Thread.

↓

GUI treo.

* * *

## Lỗi 2

Worker sửa Widget.

Sai.

Phải dùng Signal.

* * *

## Lỗi 3

Quên:
    
    
    thread.quit()

Thread vẫn tồn tại sau khi hoàn thành.

* * *

## Lỗi 4

Tạo:
    
    
    thread = QThread()

Trong một hàm rồi không giữ tham chiếu.

Nếu đối tượng `QThread` hoặc `Worker` bị thu hồi quá sớm, tác vụ có thể dừng bất ngờ. Hãy lưu chúng vào thuộc tính của lớp, ví dụ:
    
    
    self.thread = QThread()
    self.worker = Worker()

* * *

# 22\. Mẫu kiến trúc chuyên nghiệp
    
    
    MainWindow
    
    ↓
    
    Controller
    
    ↓
    
    Worker
    
    ↓
    
    QThread
    
    ↓
    
    Signal
    
    ↓
    
    GUI

Worker hoàn toàn độc lập với giao diện.

Điều này giúp dễ kiểm thử và tái sử dụng.

* * *

# Bài tập thực hành

## Bài 1

Tạo Worker.

Đếm:
    
    
    0
    
    ↓
    
    100

Hiển thị ProgressBar.

* * *

## Bài 2

Thêm:
    
    
    Cancel

Dừng Worker bằng cờ (`stop flag`).

* * *

## Bài 3

Tạo:
    
    
    Download giả lập

Mỗi giây:

↓

10%.

Hiển thị lên giao diện.

* * *

## Bài 4

Sử dụng:
    
    
    QThreadPool

Chạy:

  * Task 1 
  * Task 2 
  * Task 3 



Độc lập.

* * *

# Mini Project cuối buổi: Download Manager

Xây dựng ứng dụng:
    
    
    Download Manager
    
    +--------------------------+
    
    URL
    
    [______________________]
    
    Start
    
    Cancel
    
    ProgressBar
    
    Status
    
    +--------------------------+

Yêu cầu:

  * Nhấn **Start** : 
    * Tạo Worker. 
    * Chạy bằng `QThread`. 
  * Worker: 
    * Giả lập tải từ 0 → 100%. 
    * Phát Signal tiến độ. 
  * MainWindow: 
    * Cập nhật `QProgressBar`. 
    * Hiển thị trạng thái "Đang tải..." và "Hoàn thành". 
  * Nút **Cancel** : 
    * Yêu cầu Worker dừng an toàn bằng cờ (`stop flag`). 
  * Sau khi hoàn thành hoặc hủy: 
    * Thread kết thúc (`quit()`). 
    * Worker và Thread được giải phóng bằng `deleteLater()`. 



* * *

# Tổng kết Buổi 17

Bạn đã học được một trong những kỹ năng quan trọng nhất khi phát triển ứng dụng desktop:

  * Hiểu Event Loop và nguyên nhân GUI bị treo. 
  * Sử dụng `QThread` theo mô hình **Worker + moveToThread()`. 
  * Trao đổi dữ liệu giữa Worker và GUI bằng Signal/Slot. 
  * Cập nhật `QProgressBar` theo thời gian thực. 
  * Hủy tác vụ an toàn. 
  * Sử dụng `QRunnable` và `QThreadPool` cho nhiều tác vụ song song. 
  * Áp dụng vào các bài toán thực tế như tải file, TTS, AI, OCR và Web Scraping. 



* * *

# Chuẩn bị cho Buổi 18

Ở **Buổi 18** , chúng ta sẽ học về **SQLite và SQLModel trong PySide6**.

Đây là bước kết nối giao diện với dữ liệu thực tế.

Bạn sẽ học:

  * Tổ chức tầng Repository. 
  * Kết nối SQLite bằng `sqlite3` và `QSqlDatabase`. 
  * Hiển thị dữ liệu từ cơ sở dữ liệu lên `QTableView`. 
  * CRUD (Create, Read, Update, Delete). 
  * Tìm kiếm và phân trang. 
  * Thiết kế ứng dụng theo mô hình: 


    
    
    PySide6 GUI
            │
    Controller
            │
    Repository
            │
    SQLite

Sau buổi này, bạn sẽ có thể xây dựng các phần mềm quản lý thực sự với dữ liệu được lưu trữ bền vững trong cơ sở dữ liệu, thay vì chỉ lưu trong bộ nhớ.

