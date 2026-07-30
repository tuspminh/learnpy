# Khóa học PySide6 từ A-Z

# Buổi 8: Event System - Làm chủ Mouse, Keyboard, Window và Paint Event

> **Mục tiêu của buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu Event là gì và khác gì với Signal. 
>   * Biết Override (ghi đè) các Event của Qt. 
>   * Thành thạo xử lý chuột, bàn phím và cửa sổ. 
>   * Hiểu cơ chế Event Loop. 
>   * Biết sử dụng `paintEvent()` để tự vẽ lên Widget. 
>   * Xây dựng một chương trình **Paint Mini** và **Keyboard Tester**. 
> 


* * *

# 1\. Event là gì?

Ở buổi trước, chúng ta học:
    
    
    button.clicked.connect(save)

Đây là **Signal**.

Nhưng thực tế bên trong Qt diễn ra như sau:
    
    
    Người dùng
    
    ↓
    
    Nhấn chuột
    
    ↓
    
    Mouse Event
    
    ↓
    
    QPushButton xử lý
    
    ↓
    
    clicked Signal
    
    ↓
    
    Slot

Điều đó có nghĩa là:

  * **Event** là sự kiện gốc do hệ điều hành gửi đến Qt. 
  * **Signal** là tín hiệu do widget phát ra sau khi đã xử lý Event. 



* * *

# 2\. Event Loop

Hãy nhớ câu lệnh:
    
    
    app.exec()

Nó bắt đầu **Event Loop**.
    
    
    while chương trình đang chạy:
    
        Chờ Event
    
        Nếu có Event:
    
            Xử lý

Ví dụ:
    
    
    Di chuyển chuột
    
    ↓
    
    MouseMoveEvent
    
    ↓
    
    Qt
    
    ↓
    
    Widget

* * *

# 3\. Event và Signal khác nhau

Event| Signal  
---|---  
Đến từ hệ điều hành| Đến từ Qt Widget  
Phải override| Dùng `connect()`  
Mức thấp| Mức cao  
Linh hoạt hơn| Dễ dùng hơn  
  
Ví dụ:
    
    
    Chuột
    
    ↓
    
    Mouse Event
    
    ↓
    
    Button
    
    ↓
    
    clicked Signal

* * *

# 4\. Override Event

Muốn xử lý Event, ta **ghi đè (override)** phương thức tương ứng.

Ví dụ:
    
    
    class MyWidget(QWidget):
    
        def mousePressEvent(self, event):
            print("Click")

Qt sẽ tự động gọi hàm này khi người dùng nhấn chuột.

* * *

# 5\. Mouse Press Event

Ví dụ hoàn chỉnh:
    
    
    import sys
    
    from PySide6.QtWidgets import QApplication, QWidget
    
    
    class Window(QWidget):
    
        def mousePressEvent(self, event):
            print("Đã nhấn chuột")
    
    
    app = QApplication(sys.argv)
    
    window = Window()
    
    window.show()
    
    app.exec()

Mỗi lần click:
    
    
    Đã nhấn chuột

* * *

# 6\. Lấy vị trí chuột
    
    
    def mousePressEvent(self, event):
    
        print(event.position())

Ví dụ:
    
    
    QPointF(120, 80)

Nếu muốn lấy tọa độ số nguyên:
    
    
    x = int(event.position().x())
    y = int(event.position().y())
    
    print(x, y)

* * *

# 7\. Kiểm tra nút chuột
    
    
    from PySide6.QtCore import Qt
    
    if event.button() == Qt.MouseButton.LeftButton:
        print("Chuột trái")

Các nút phổ biến:
    
    
    LeftButton
    
    RightButton
    
    MiddleButton

* * *

# 8\. Mouse Move Event
    
    
    def mouseMoveEvent(self, event):
    
        print(event.position())

Để nhận được sự kiện khi di chuyển chuột mà không cần giữ nút chuột:
    
    
    self.setMouseTracking(True)

* * *

# 9\. Mouse Release Event
    
    
    def mouseReleaseEvent(self, event):
    
        print("Thả chuột")

* * *

# 10\. Double Click Event
    
    
    def mouseDoubleClickEvent(self, event):
    
        print("Double Click")

* * *

# 11\. Key Press Event
    
    
    def keyPressEvent(self, event):
    
        print(event.key())

Ví dụ:
    
    
    65

Đây là mã của phím `A`.

* * *

## So sánh với hằng số
    
    
    from PySide6.QtCore import Qt
    
    if event.key() == Qt.Key.Key_A:
        print("Bạn nhấn A")

Một số phím:
    
    
    Key_A
    
    Key_B
    
    Key_Return
    
    Key_Enter
    
    Key_Escape
    
    Key_Space
    
    Key_Left
    
    Key_Right
    
    Key_Up
    
    Key_Down

* * *

# 12\. Key Release Event
    
    
    def keyReleaseEvent(self, event):
    
        print("Nhả phím")

* * *

# 13\. Resize Event
    
    
    def resizeEvent(self, event):
    
        print(self.width())
    
        print(self.height())

Mỗi lần thay đổi kích thước cửa sổ:
    
    
    800
    
    600

* * *

# 14\. Close Event

Ví dụ:
    
    
    from PySide6.QtWidgets import QMessageBox
    
    
    def closeEvent(self, event):
    
        answer = QMessageBox.question(
            self,
    
            "Thoát",
    
            "Bạn có chắc muốn thoát?"
        )
    
        if answer == QMessageBox.StandardButton.Yes:
            event.accept()
    
        else:
            event.ignore()

Giải thích:

  * `event.accept()`: cho phép đóng cửa sổ. 
  * `event.ignore()`: hủy thao tác đóng. 



Đây là cách rất phổ biến để cảnh báo người dùng nếu dữ liệu chưa được lưu.

* * *

# 15\. Paint Event

Đây là Event mạnh nhất trong Qt.

Mỗi lần Widget cần vẽ lại:

Qt sẽ gọi:
    
    
    paintEvent()

Ví dụ:
    
    
    from PySide6.QtGui import QPainter
    
    
    def paintEvent(self, event):
    
        painter = QPainter(self)
    
        painter.drawText(20, 40, "Hello Qt")

Kết quả:
    
    
    Hello Qt

được vẽ trực tiếp lên Widget.

> **Lưu ý:** Không gọi `paintEvent()` trực tiếp. Nếu muốn yêu cầu Qt vẽ lại, hãy dùng `self.update()`.

* * *

# 16\. Vẽ hình chữ nhật
    
    
    def paintEvent(self, event):
    
        painter = QPainter(self)
    
        painter.drawRect(
            50,
            50,
            200,
            100
        )

* * *

# 17\. Vẽ hình tròn
    
    
    painter.drawEllipse(
        50,
        50,
        100,
        100
    )

* * *

# 18\. Vẽ đường thẳng
    
    
    painter.drawLine(
        10,
        10,
        300,
        300
    )

* * *

# 19\. Ví dụ: Hiển thị vị trí chuột
    
    
    import sys
    
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QVBoxLayout,
        QWidget,
    )
    
    
    class Window(QWidget):
    
        def __init__(self):
            super().__init__()
    
            self.setMouseTracking(True)
    
            self.label = QLabel("Di chuyển chuột")
    
            layout = QVBoxLayout()
    
            layout.addWidget(self.label)
    
            self.setLayout(layout)
    
        def mouseMoveEvent(self, event):
    
            x = int(event.position().x())
            y = int(event.position().y())
    
            self.label.setText(
                f"{x}, {y}"
            )
    
    
    app = QApplication(sys.argv)
    
    window = Window()
    
    window.show()
    
    app.exec()

* * *

# 20\. Ví dụ: Keyboard Tester
    
    
    import sys
    
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QVBoxLayout,
        QWidget,
    )
    
    
    class Window(QWidget):
    
        def __init__(self):
            super().__init__()
    
            self.label = QLabel("Nhấn phím")
    
            layout = QVBoxLayout()
    
            layout.addWidget(self.label)
    
            self.setLayout(layout)
    
            self.setFocus()
    
        def keyPressEvent(self, event):
    
            if event.key() == Qt.Key.Key_Space:
                self.label.setText("SPACE")
    
            elif event.key() == Qt.Key.Key_Escape:
                self.close()
    
            else:
                self.label.setText(
                    str(event.text())
                )
    
    
    app = QApplication(sys.argv)
    
    window = Window()
    
    window.show()
    
    app.exec()

> **Lưu ý:** Để `keyPressEvent()` hoạt động, widget phải có **focus**. Nếu không nhận được sự kiện bàn phím, hãy kiểm tra xem widget nào đang được focus.

* * *

# 21\. Những lỗi người mới thường gặp

## 1\. Không gọi lớp cha khi cần

Ví dụ:
    
    
    def keyPressEvent(self, event):
    
        print(event.key())

Nếu bạn muốn **vẫn giữ hành vi mặc định** của Qt sau khi xử lý, hãy gọi:
    
    
    super().keyPressEvent(event)

Điều này đặc biệt quan trọng với nhiều widget như `QLineEdit`, `QTextEdit`, nơi Qt còn phải xử lý việc nhập văn bản.

* * *

## 2\. Không bật Mouse Tracking

Sai:
    
    
    mouseMoveEvent()

Không chạy khi chỉ di chuyển chuột.

Đúng:
    
    
    self.setMouseTracking(True)

* * *

## 3\. Gọi `paintEvent()` trực tiếp

Sai:
    
    
    self.paintEvent(...)

Đúng:
    
    
    self.update()

Qt sẽ tự gọi `paintEvent()` khi thích hợp.

* * *

## 4\. Không dùng `event.accept()` hoặc `event.ignore()`

Trong `closeEvent()`, nếu bạn muốn quyết định việc đóng cửa sổ, hãy sử dụng hai phương thức này để thể hiện rõ ý định.

* * *

# Bài tập thực hành

## Bài 1

Tạo Widget.

Mỗi lần click chuột:

Hiển thị:
    
    
    Bạn vừa click tại:
    
    120, 80

* * *

## Bài 2

Nếu click:

  * Chuột trái 



Hiển thị:
    
    
    LEFT

  * Chuột phải 



Hiển thị:
    
    
    RIGHT

* * *

## Bài 3

Hiển thị kích thước cửa sổ.

Mỗi lần resize:
    
    
    1024 × 768

* * *

## Bài 4

Khi nhấn:

  * `Esc` → đóng cửa sổ. 
  * `Space` → đổi nội dung `QLabel`. 
  * Các phím khác → hiển thị ký tự vừa nhập. 



* * *

## Bài 5

Trong `paintEvent()`:

  * Vẽ 1 hình chữ nhật. 
  * Vẽ 1 hình tròn. 
  * Vẽ 1 đường thẳng. 
  * Vẽ dòng chữ `"PySide6"`. 



* * *

# Mini Project cuối buổi: Paint Mini

Hãy xây dựng một ứng dụng đơn giản với các yêu cầu:

  * Một vùng vẽ (`QWidget`). 
  * Khi người dùng nhấn và kéo chuột trái: 
    * Lưu lại các điểm chuột. 
    * Gọi `self.update()` để yêu cầu vẽ lại. 
  * Trong `paintEvent()`: 
    * Dùng `QPainter.drawLine()` để nối các điểm liên tiếp, tạo thành nét vẽ. 
  * Thêm nút **Xóa** để làm sạch vùng vẽ (xóa danh sách điểm và gọi `update()`). 



> Dự án này sẽ giúp bạn kết hợp `mousePressEvent()`, `mouseMoveEvent()` và `paintEvent()` thành một ứng dụng tương tác hoàn chỉnh.

* * *

# Tổng kết Buổi 8

Bạn đã hiểu hệ thống Event của Qt và biết cách xử lý:

  * `mousePressEvent()`
  * `mouseReleaseEvent()`
  * `mouseMoveEvent()`
  * `mouseDoubleClickEvent()`
  * `keyPressEvent()`
  * `keyReleaseEvent()`
  * `resizeEvent()`
  * `closeEvent()`
  * `paintEvent()`



Đồng thời, bạn đã biết:

  * Phân biệt **Event** và **Signal**. 
  * Vai trò của **Event Loop**. 
  * Cách sử dụng `QPainter` để tự vẽ giao diện. 
  * Những lưu ý quan trọng như `setMouseTracking()`, `update()` và `super().<event>()`. 



## Chuẩn bị cho Buổi 9

Ở **Buổi 9** , chúng ta sẽ học về **Event Filter** và **Event Propagation** :

  * `installEventFilter()`
  * `eventFilter()`
  * `QObject.event()`
  * Chặn hoặc cho phép Event tiếp tục truyền. 
  * Theo dõi sự kiện của nhiều widget cùng lúc. 
  * Xây dựng các chức năng như: 
    * Tự động đổi màu khi rê chuột. 
    * Ghi log mọi thao tác của người dùng. 
    * Phím tắt toàn cục trong ứng dụng. 
    * Kiểm soát hành vi nhập liệu. 



Đây là kỹ thuật được sử dụng rất nhiều trong các ứng dụng PySide6 quy mô lớn vì nó giúp tập trung việc xử lý sự kiện mà không cần ghi đè từng widget riêng lẻ.

