# Khóa học PySide6 từ A-Z

# Buổi 9: Event Filter và Event Propagation - Kiểm soát toàn bộ sự kiện trong ứng dụng

> **Mục tiêu của buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu cơ chế Event Propagation (lan truyền sự kiện). 
>   * Biết cách sử dụng `installEventFilter()`. 
>   * Thành thạo `eventFilter()`. 
>   * Biết khi nào nên dùng Event Filter thay vì override Event. 
>   * Biết chặn hoặc cho phép Event tiếp tục truyền. 
>   * Xây dựng ứng dụng theo dõi toàn bộ sự kiện của nhiều widget. 
> 


* * *

# 1\. Ôn tập

Buổi trước chúng ta xử lý Event bằng cách ghi đè:
    
    
    class MyWidget(QWidget):
    
        def mousePressEvent(self, event):
            print("Click")

Điều này rất tốt khi chỉ có **một widget**.

Nhưng nếu có:

  * 50 Button 
  * 20 LineEdit 
  * 10 ComboBox 



thì bạn sẽ phải ghi đè rất nhiều hàm.

Qt có một cơ chế mạnh hơn:

> **Event Filter**

* * *

# 2\. Event Propagation (Lan truyền sự kiện)

Giả sử bạn click vào một `QPushButton`.

Luồng xử lý:
    
    
    Hệ điều hành
    
    ↓
    
    Qt Event Loop
    
    ↓
    
    Event Filter (nếu có)
    
    ↓
    
    Widget nhận Event
    
    ↓
    
    mousePressEvent()
    
    ↓
    
    Signal clicked()

Nếu Event Filter chặn sự kiện:
    
    
    Event
    
    ↓
    
    Event Filter
    
    ↓
    
    STOP

Widget sẽ **không nhận được Event**.

* * *

# 3\. Event Filter là gì?

Event Filter là một đối tượng có thể **theo dõi hoặc chặn** sự kiện của widget khác.

Ví dụ:
    
    
    Button
    
    ↓
    
    Mouse Click
    
    ↓
    
    Event Filter
    
    ↓
    
    Button xử lý

Hoặc:
    
    
    Button
    
    ↓
    
    Mouse Click
    
    ↓
    
    Event Filter
    
    ↓
    
    STOP

* * *

# 4\. installEventFilter()

Muốn theo dõi widget:
    
    
    widget.installEventFilter(self)

Ý nghĩa:

> "Hãy gửi mọi Event của `widget` cho `self` kiểm tra trước."

* * *

# 5\. eventFilter()

Đây là nơi xử lý.
    
    
    from PySide6.QtCore import QObject
    
    class Window(QWidget):
    
        def eventFilter(self, obj, event):
    
            return super().eventFilter(obj, event)

Qt sẽ gọi hàm này trước khi gửi Event cho widget.

* * *

# 6\. Ví dụ đầu tiên
    
    
    import sys
    
    from PySide6.QtCore import QEvent
    from PySide6.QtWidgets import QApplication, QPushButton, QWidget
    
    
    class Window(QWidget):
    
        def __init__(self):
    
            super().__init__()
    
            self.button = QPushButton("Click", self)
    
            self.button.installEventFilter(self)
    
        def eventFilter(self, obj, event):
    
            if obj == self.button:
    
                if event.type() == QEvent.Type.MouseButtonPress:
    
                    print("Button được click")
    
            return super().eventFilter(obj, event)
    
    
    app = QApplication(sys.argv)
    
    window = Window()
    
    window.show()
    
    app.exec()

Khi click:
    
    
    Button được click

* * *

# 7\. Các loại Event

Qt có hàng trăm Event.

Thường dùng:

Event| Ý nghĩa  
---|---  
`MouseButtonPress`| Nhấn chuột  
`MouseButtonRelease`| Thả chuột  
`MouseMove`| Di chuyển chuột  
`KeyPress`| Nhấn phím  
`KeyRelease`| Nhả phím  
`Enter`| Chuột đi vào widget  
`Leave`| Chuột rời widget  
`FocusIn`| Có focus  
`FocusOut`| Mất focus  
`Wheel`| Cuộn chuột  
  
* * *

# 8\. Theo dõi nhiều Widget

Ví dụ:
    
    
    button1.installEventFilter(self)
    
    button2.installEventFilter(self)
    
    button3.installEventFilter(self)

Trong `eventFilter()`:
    
    
    if obj == button1:
        ...
    
    elif obj == button2:
        ...

Một Event Filter có thể quản lý rất nhiều widget.

* * *

# 9\. Chặn Event

Ví dụ:
    
    
    def eventFilter(self, obj, event):
    
        if event.type() == QEvent.Type.MouseButtonPress:
    
            print("Đã chặn")
    
            return True
    
        return False

`return True`

↓

Qt dừng xử lý.

Button sẽ **không phát Signal`clicked()`**.

* * *

# 10\. Cho phép Event
    
    
    return False

Hoặc:
    
    
    return super().eventFilter(obj, event)

Event tiếp tục đi đến widget.

* * *

# 11\. Ví dụ chặn Button
    
    
    if obj == self.button:
    
        if event.type() == QEvent.Type.MouseButtonPress:
    
            print("Không cho click")
    
            return True

Kết quả:
    
    
    Không cho click

Button không hoạt động nữa.

* * *

# 12\. Hover Effect

Ví dụ:
    
    
    if event.type() == QEvent.Type.Enter:
    
        obj.setStyleSheet(
            "background:yellow;"
        )

Khi chuột đi vào:

Button đổi màu.

* * *

Chuột rời:
    
    
    if event.type() == QEvent.Type.Leave:
    
        obj.setStyleSheet("")

* * *

# 13\. Theo dõi QLineEdit
    
    
    if obj == self.edit:
    
        if event.type() == QEvent.Type.FocusIn:
    
            print("Đang nhập")

Mất focus:
    
    
    FocusOut

Đây là cách thường dùng để kiểm tra dữ liệu khi người dùng rời khỏi ô nhập.

* * *

# 14\. Event()

Ngoài `eventFilter()` còn có:
    
    
    def event(self, event):

Đây là hàm nhận **mọi Event** của chính widget đó.

Ví dụ:
    
    
    def event(self, event):
    
        print(event.type())
    
        return super().event(event)

Thông thường, chỉ nên override `event()` khi bạn cần xử lý nhiều loại Event trong cùng một widget.

* * *

# 15\. Ví dụ hoàn chỉnh
    
    
    import sys
    
    from PySide6.QtCore import QEvent
    from PySide6.QtWidgets import (
        QApplication,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
    
    
    class Window(QWidget):
    
        def __init__(self):
    
            super().__init__()
    
            layout = QVBoxLayout()
    
            self.button = QPushButton("Hover")
    
            layout.addWidget(self.button)
    
            self.setLayout(layout)
    
            self.button.installEventFilter(self)
    
        def eventFilter(self, obj, event):
    
            if obj == self.button:
    
                if event.type() == QEvent.Type.Enter:
    
                    self.button.setStyleSheet(
                        """
                        background:yellow;
                        font-size:18px;
                        """
                    )
    
                elif event.type() == QEvent.Type.Leave:
    
                    self.button.setStyleSheet("")
    
            return super().eventFilter(obj, event)
    
    
    app = QApplication(sys.argv)
    
    window = Window()
    
    window.show()
    
    app.exec()

* * *

# 16\. Khi nào dùng Event Filter?

### Dùng Override Event

✔ Một widget.

✔ Xử lý riêng.

Ví dụ:
    
    
    mousePressEvent()

* * *

### Dùng Event Filter

✔ Nhiều widget.

✔ Theo dõi toàn bộ ứng dụng.

✔ Chặn Event.

✔ Viết framework.

✔ Ghi log.

✔ Validation.

Đây là lựa chọn phổ biến trong các ứng dụng lớn.

* * *

# 17\. Những lỗi người mới thường gặp

## Lỗi 1

Quên:
    
    
    installEventFilter()

Khi đó:
    
    
    eventFilter()

không bao giờ được gọi.

* * *

## Lỗi 2

So sánh sai Event.

Sai:
    
    
    event.MousePress

Đúng:
    
    
    QEvent.Type.MouseButtonPress

* * *

## Lỗi 3

Luôn trả về `True`
    
    
    return True

Mọi Event đều bị chặn.

Hậu quả:

  * Button không click được. 
  * LineEdit không nhập được. 
  * ComboBox không mở được. 



* * *

## Lỗi 4

Quên gọi:
    
    
    return super().eventFilter(
        obj,
        event
    )

hoặc ít nhất:
    
    
    return False

* * *

# 18\. Ví dụ thực tế

## Kiểm tra nhập Email

Khi:
    
    
    FocusOut

↓

Kiểm tra:
    
    
    Có ký tự @ ?

Nếu sai:
    
    
    Đổi viền đỏ.

Đây là cách rất nhiều ứng dụng hiện đại kiểm tra dữ liệu nhập.

* * *

## Ghi log

Mỗi lần:
    
    
    Click
    
    ↓
    
    Hover
    
    ↓
    
    Keyboard

↓

Ghi:
    
    
    2026-07-07 09:15
    
    Click Button Save

Đây là nền tảng của hệ thống audit trong các phần mềm doanh nghiệp.

* * *

# Bài tập thực hành

## Bài 1

Tạo 3 Button.

Khi Hover:

Đổi màu nền.

Khi Leave:

Trở lại bình thường.

* * *

## Bài 2

Tạo `QLineEdit`.

Khi FocusIn:

Đổi viền xanh.

Khi FocusOut:

Đổi viền xám.

* * *

## Bài 3

Chặn chuột phải trên Button.

Yêu cầu:

  * Chuột trái hoạt động bình thường. 
  * Chuột phải bị chặn. 



_Gợi ý:_ Trong `eventFilter()`, kiểm tra `event.type()` là `MouseButtonPress` và `event.button()` là `Qt.MouseButton.RightButton`. Trả về `True` để chặn sự kiện.

* * *

## Bài 4

Tạo Logger.

Mỗi lần:

  * Click 
  * Hover 
  * Nhấn phím 



In Event ra terminal.

* * *

# Mini Project cuối buổi: Dashboard giám sát sự kiện

Xây dựng ứng dụng gồm:

  * 3 `QPushButton`. 
  * 2 `QLineEdit`. 
  * 1 `QComboBox`. 
  * 1 `QTextEdit` để hiển thị nhật ký. 



Yêu cầu:

  * Cài đặt `EventFilter` cho tất cả widget. 
  * Ghi lại các sự kiện: 
    * Click chuột. 
    * Hover. 
    * Focus. 
    * Nhấn phím. 
  * Mỗi dòng log gồm: 
    * Thời gian. 
    * Tên widget. 
    * Loại Event. 



Ví dụ:
    
    
    14:35:20 | btnSave | MouseButtonPress
    14:35:22 | txtName | FocusIn
    14:35:25 | txtName | KeyPress
    14:35:30 | cboDepartment | FocusOut

* * *

# Tổng kết Buổi 9

Bạn đã làm chủ các khái niệm quan trọng trong hệ thống sự kiện của Qt:

  * Hiểu **Event Propagation**. 
  * Biết cài đặt và sử dụng `installEventFilter()`. 
  * Xử lý sự kiện tập trung bằng `eventFilter()`. 
  * Chặn hoặc cho phép Event tiếp tục truyền. 
  * Theo dõi nhiều widget bằng một bộ lọc duy nhất. 
  * Phân biệt khi nào nên dùng `override Event` và khi nào nên dùng `Event Filter`. 



Đây là kỹ thuật thường xuất hiện trong các framework và các ứng dụng desktop quy mô lớn.

* * *

# Chuẩn bị cho Buổi 10

Từ **Buổi 10** , chúng ta sẽ bắt đầu một chương hoàn toàn mới: **Kiến trúc ứng dụng PySide6 chuyên nghiệp**.

Bạn sẽ học:

  * Mô hình **MVC (Model - View - Controller)**. 
  * Mô hình **MVVM** trong Qt. 
  * Tổ chức dự án nhiều file. 
  * Tách giao diện (UI) và logic xử lý. 
  * Quản lý tài nguyên (icons, images, styles). 
  * Tạo cấu trúc dự án có khả năng mở rộng. 



Sau buổi này, bạn sẽ không còn viết tất cả mã trong một file `main.py`, mà sẽ học cách tổ chức dự án như các phần mềm PySide6 chuyên nghiệp với hàng chục hoặc hàng trăm module.

