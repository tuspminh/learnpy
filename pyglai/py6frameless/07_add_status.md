Để thêm một thanh trạng thái (**Status Bar**) nằm ở dưới cùng của cửa sổ tràn viền, bạn chỉ cần sử dụng thành phần `QStatusBar` tiêu chuẩn của PySide6.

Do chúng ta đang dùng bộ khung `FramelessMainWindow`, bạn có thể gọi thẳng hàm `self.statusBar()` giống hệt như trong QMainWindow thông thường. Thư viện sẽ tự động tính toán để thanh trạng thái nằm sát mép dưới của cửa sổ mà không đè lên phần viền kéo dãn (resize area).

Dưới đây là mã nguồn đã tích hợp thanh Status Bar và được định dạng màu sắc (QSS) đồng bộ với giao diện tối:

python
    
    
    import sys
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QStatusBar
    from qframelesswindow import FramelessMainWindow, TitleBar
    
    class CustomTitleBar(TitleBar):
        """Thanh tiêu đề tùy chỉnh"""
        def __init__(self, parent):
            super().__init__(parent)
            self.setFixedHeight(40)
            
            self.setStyleSheet("""
                CustomTitleBar { background-color: #1e1e24; }
                QLabel { color: #ffffff; font-family: 'Segoe UI'; font-size: 13px; padding-left: 10px; }
            """)
            
            self.titleLabel = QLabel("Ứng dụng PySide6 với Status Bar", self)
            self.hBoxLayout.insertWidget(0, self.titleLabel, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    
    
    class MainWindow(FramelessMainWindow):
        def __init__(self):
            super().__init__()
            self.resize(800, 600)
            self.setMinimumSize(QSize(400, 300))
            
            # 1. Thiết lập thanh tiêu đề
            self.setTitleBar(CustomTitleBar(self))
            
            # 2. Phần nội dung chính (Vùng trung tâm)
            self.main_widget = QWidget(self)
            self.setCentralWidget(self.main_widget)
            
            layout = QVBoxLayout(self.main_widget)
            self.label = QLabel("Nội dung ứng dụng ở đây.\nNhìn xuống góc dưới để xem Status Bar!")
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.label)
            
            # Giao diện cho vùng trung tâm
            self.main_widget.setStyleSheet("""
                QWidget { background-color: #282a36; }
                QLabel { color: #f8f8f2; font-size: 18px; font-family: 'Segoe UI'; }
            """)
    
            # 3. Khởi tạo và cấu hình Status Bar
            self.init_status_bar()
    
        def init_status_bar(self):
            """Khởi tạo thanh trạng thái dưới đáy cửa sổ"""
            # Gọi thanh status bar mặc định của QMainWindow
            status_bar = self.statusBar()
            
            # Thiết lập chiều cao và màu sắc bằng QSS để hợp với giao diện tối
            status_bar.setFixedHeight(25)
            status_bar.setStyleSheet("""
                QStatusBar {
                    background-color: #1e1e24;  /* Trùng màu với thanh tiêu đề */
                    color: #8b92a5;            /* Màu chữ xám nhạt */
                    font-family: 'Segoe UI';
                    font-size: 11px;
                    border-top: 1px solid #343746; /* Đường viền mỏng ngăn cách với nội dung */
                }
                QStatusBar::item {
                    border: none; /* Bỏ viền phân cách mặc định giữa các widget trong status bar */
                }
            """)
            
            # Hiển thị một tin nhắn mặc định tạm thời (biến mất sau x mili-giây nếu muốn)
            status_bar.showMessage("Sẵn sàng", 0) 
            
            # Bạn cũng có thể thêm các widget vĩnh viễn vào bên phải status bar (ví dụ: số dòng, phiên bản)
            self.version_label = QLabel("v1.0.0")
            self.version_label.setStyleSheet("color: #6272a4; padding-right: 10px;")
            status_bar.addPermanentWidget(self.version_label)
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    

Hãy thận trọng khi sử dụng mã.

Cách cập nhật thông tin lên Status Bar khi đang chạy app:

Bất kỳ lúc nào bạn muốn thay đổi dòng chữ ở thanh trạng thái, bạn chỉ cần gọi dòng code này từ các hàm xử lý logic khác trong class `MainWindow`:

  * Thay đổi tin nhắn chính (bên trái): `self.statusBar().showMessage("Đang tải dữ liệu...")`
  * Xóa tin nhắn: `self.statusBar().clearMessage()`



Bạn có muốn thêm **hiệu ứng đổ bóng (Drop Shadow)** bao quanh viền cửa sổ hay muốn chuyển sang **hiệu ứng mờ đục Acrylic/Mica** của Windows 11 không?

