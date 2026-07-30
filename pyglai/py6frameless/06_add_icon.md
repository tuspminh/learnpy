Để thay đổi icon (biểu tượng) cho các nút Đóng, Phóng to, Thu nhỏ, bạn có thể dễ dàng sử dụng **QSS (Qt Style Sheets)** để chỉ định ảnh hoặc icon riêng cho từng trạng thái của nút.

Dưới đây là đoạn code hoàn chỉnh dựa trên thư viện `qframelesswindow`. Các icon sẽ tự động thay đổi hình ảnh khi bạn di chuột (hover) vào hoặc nhấn vào.

Cần chuẩn bị:

Chuẩn bị sẵn các file `.png` (kích thước khoảng 16 × 16 px) cho từng nút và đặt chung thư mục với file code của bạn, ví dụ:

  * `close.png`, `close_hover.png`, `close_pressed.png`
  * `minimize.png`, `minimize_hover.png`
  * `maximize.png`, `maximize_hover.png`



Mã nguồn hoàn chỉnh:

python
    
    
    import sys
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel
    from qframelesswindow import FramelessMainWindow, TitleBar
    
    class CustomTitleBar(TitleBar):
        """Thanh tiêu đề tùy chỉnh giao diện và icon các nút"""
        def __init__(self, parent):
            super().__init__(parent)
            self.setFixedHeight(40)
            
            # 1. Gọi hàm tùy chỉnh giao diện các nút
            self.setup_buttons_icon()
    
        def setup_buttons_icon(self):
            """Sử dụng QSS để gán Icon riêng cho từng trạng thái nút"""
            # Các trạng thái của nút: normal, hover (di chuột), pressed (nhấn)
            
            close_qss = """
                #closeButton {
                    image: url(close.png); 
                    background-color: transparent;
                }
                #closeButton:hover {
                    image: url(close_hover.png);
                    background-color: #c42b1c; /* Đổi màu nền đỏ đặc trưng khi hover */
                }
                #closeButton:pressed {
                    image: url(close_pressed.png);
                    background-color: #8b1f14;
                }
            """
            
            minimize_qss = """
                #minimizeButton {
                    image: url(minimize.png);
                    background-color: transparent;
                }
                #minimizeButton:hover {
                    image: url(minimize_hover.png);
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """
    
            maximize_qss = """
                #maximizeButton {
                    image: url(maximize.png);
                    background-color: transparent;
                }
                #maximizeButton:hover {
                    image: url(maximize_hover.png);
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """
    
            # Áp dụng các QSS này vào các nút có sẵn của bộ khung
            self.closeButton.setStyleSheet(close_qss)
            self.minimizeButton.setStyleSheet(minimize_qss)
            self.maximizeButton.setStyleSheet(maximize_qss)
    
    
    class MainWindow(FramelessMainWindow):
        def __init__(self):
            super().__init__()
            self.resize(800, 600)
            self.setMinimumSize(QSize(400, 300))
            
            # Đặt tiêu đề và icon cho cửa sổ (icon ứng dụng trên Taskbar)
            self.setWindowTitle("App Tràn Viền Custom Icon")
            
            # 1. Dùng thanh tiêu đề tùy chỉnh
            self.setTitleBar(CustomTitleBar(self))
            
            # 2. Phần nội dung chính
            self.main_widget = QWidget(self)
            self.setCentralWidget(self.main_widget)
            
            layout = QVBoxLayout(self.main_widget)
            self.label = QLabel("Ứng dụng có nút đóng/mở/thu nhỏ tùy chỉnh icon riêng!")
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.label)
            
            self.main_widget.setStyleSheet("""
                QWidget { background-color: #2b2b2b; }
                QLabel { color: #ffffff; font-size: 18px; font-family: 'Segoe UI'; }
            """)
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    

Hãy thận trọng khi sử dụng mã.

Giải thích cách hoạt động:

  * `image: url(...)`: Tùy thuộc vào trạng thái `:hover` hoặc `:pressed` mà PySide6 sẽ thay thế bằng hình ảnh bạn chỉ định thay vì dùng text hoặc icon mặc định của hệ thống.
  * `#closeButton`, `#minimizeButton`, `#maximizeButton`: Là các ID mặc định mà thư viện `TitleBar` tạo sẵn cho bộ 3 nút điều khiển.



Nếu bạn muốn tiếp tục tùy chỉnh nâng cao hơn, hãy cho tôi biết:

  * Bạn có đang muốn dùng **hiệu ứng làm mờ nền (Mica hoặc Acrylic)** đặc trưng của Windows 11 không?
  * Bạn có muốn tùy chỉnh thiết kế giao diện thanh tiêu đề (màu sắc, ẩn/hiện chữ, căn lề logo) theo thiết kế riêng không?



