Để thiết kế cửa sổ tràn viền (frameless) trong PySide6, bạn cần tắt khung viền mặc định của hệ điều hành, làm trong suốt nền cửa sổ và tự xây dựng lại thanh tiêu đề (title bar). [[1](https://www.pythonguis.com/tutorials/custom-title-bar-pyqt6/)]

Các bước cốt lõi gồm:

  1. Dùng `setWindowFlags(Qt.WindowType.FramelessWindowHint)` để bỏ thanh công cụ và viền.
  2. Dùng `setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)` để cho phép bo tròn các góc và tạo độ mờ.
  3. Lập trình lại sự kiện chuột (`mousePressEvent`, `mouseMoveEvent`) để người dùng có thể kéo/di chuyển cửa sổ. [[1](https://www.pythonguis.com/tutorials/custom-title-bar-pyqt6/)]



Dưới đây là mã mẫu cơ bản và đầy đủ giúp bạn tạo ra một cửa sổ tràn viền có góc bo tròn và có thể kéo thả:

python
    
    
    import sys
    from PySide6.QtCore import Qt, QPoint
    from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
    
    class FramelessWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.resize(800, 600)
    
            # 1. Bỏ viền và thanh tiêu đề mặc định
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    
            # 2. Làm nền cửa sổ trong suốt để bo góc
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
            # 3. Tạo Widget trung tâm để chứa giao diện (áp dụng bo góc và đổ bóng tại đây)
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            
            # Dùng QSS để bo góc và đổi màu nền cửa sổ của bạn
            self.central_widget.setStyleSheet("""
                QWidget {
                    background-color: #2e3440; 
                    border-radius: 15px;
                }
            """)
    
            # Bố cục giao diện
            layout = QVBoxLayout()
            self.label = QLabel("Cửa sổ tràn viền PySide6")
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.setStyleSheet("color: white; font-size: 24px;")
            layout.addWidget(self.label)
            self.central_widget.setLayout(layout)
    
            # Biến lưu trữ vị trí chuột để kéo cửa sổ
            self.old_pos = QPoint()
    
        # 4. Ghi đè sự kiện nhấn chuột (lưu vị trí hiện tại)
        def mousePressEvent(self, event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.old_pos = event.globalPosition().toPoint()
    
        # 5. Ghi đè sự kiện di chuyển chuột (tính khoảng cách và di chuyển cửa sổ)
        def mouseMoveEvent(self, event):
            if event.buttons() & Qt.MouseButton.LeftButton:
                delta = event.globalPosition().toPoint() - self.old_pos
                self.move(self.pos() + delta)
                self.old_pos = event.globalPosition().toPoint()
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = FramelessWindow()
        window.show()
        sys.exit(app.exec())
    

Hãy thận trọng khi sử dụng mã.

Các tính năng nâng cao

Nếu bạn muốn bổ sung các hiệu ứng gốc, tối ưu hóa kéo dãn (resize) hoặc sử dụng layout mờ (như Acrylic/Mica của Windows) mà không phải viết lại mã từ đầu, bạn có thể tham khảo thư viện hỗ trợ phổ biến là [PySideSix-Frameless-Window](https://pypi.org/project/PySideSix-Frameless-Window/) trên PyPI. [[1](https://pypi.org/project/PySideSix-Frameless-Window/)]

Nếu bạn muốn bổ sung các tính năng nâng cao cho cửa sổ tràn viền, hãy cho tôi biết:

  * Bạn có cần **thêm nút Đóng/Phóng to/Thu nhỏ** ở thanh tiêu đề không?
  * Bạn có muốn tính năng **kéo dãn viền cửa sổ (resize)** không?
  * Bạn có đang nhắm tới hệ điều hành cụ thể nào (ví dụ: **Windows 11** hay **macOS**) để áp dụng hiệu ứng mờ nền không?



