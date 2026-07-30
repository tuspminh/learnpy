Đây là đoạn mã nguồn đã được tối giản hoàn toàn. Code chỉ tập trung vào việc loại bỏ viền hệ điều hành, gắn thư viện `qt-material`, chia bố cục 3 tầng cơ bản (Thanh tiêu đề, Vùng nội dung, Status Bar) và kết hợp chức năng của các nút bấm mà không có bất kỳ dòng QSS trang trí hay cấu hình bo góc phức tạp nào:

python
    
    
    import sys
    from PySide6.QtCore import Qt, QPoint
    from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QStatusBar
    from qt_material import apply_stylesheet
    
    class FramelessWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.resize(800, 600)
    
            # 1. Ẩn viền cửa sổ mặc định của hệ điều hành
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    
            # 2. Tạo Widget trung tâm để làm khung chứa layout chính
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
    
            # Bố cục tổng thể xếp dọc (Tiêu đề -> Nội dung -> Status Bar)
            main_layout = QVBoxLayout(self.central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
    
            # --- THANH TIÊU ĐỀ TỰ CHẾ (TITLE BAR) ---
            self.title_bar = QWidget()
            self.title_bar.setFixedHeight(40)
            title_layout = QHBoxLayout(self.title_bar)
            title_layout.setContentsMargins(10, 0, 0, 0)
            title_layout.setSpacing(0)
    
            # Nhãn chữ tiêu đề app
            self.title_label = QLabel("Ứng dụng Tràn viền tối giản")
            title_layout.addWidget(self.title_label)
            title_layout.addStretch()
    
            # Bộ nút điều khiển hệ thống
            self.btn_minimize = QPushButton("🗕")
            self.btn_maximize = QPushButton("🗖")
            self.btn_close = QPushButton("🗙")
    
            # Gán cố định kích thước nút bấm trên thanh tiêu đề
            self.btn_minimize.setFixedSize(45, 40)
            self.btn_maximize.setFixedSize(45, 40)
            self.btn_close.setFixedSize(45, 40)
    
            # Kết nối sự kiện Click nút với các lệnh điều khiển cửa sổ cơ bản
            self.btn_minimize.clicked.connect(self.showMinimized)
            self.btn_maximize.clicked.connect(self.toggle_maximize)
            self.btn_close.clicked.connect(self.close)
    
            title_layout.addWidget(self.btn_minimize)
            title_layout.addWidget(self.btn_maximize)
            title_layout.addWidget(self.btn_close)
            
            main_layout.addWidget(self.title_bar)
    
            # --- VÙNG NỘI DUNG CHÍNH (CONTENT AREA) ---
            self.content_widget = QWidget()
            content_layout = QVBoxLayout(self.content_widget)
            
            self.label = QLabel("Nội dung ứng dụng ở đây")
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content_layout.addWidget(self.label)
            
            # Thêm một nút bấm Material mẫu vào giữa màn hình
            self.sample_btn = QPushButton("Nút bấm mẫu")
            self.sample_btn.setFixedWidth(150)
            content_layout.addWidget(self.sample_btn, 0, Qt.AlignmentFlag.AlignCenter)
            
            main_layout.addWidget(self.content_widget)
    
            # --- THANH TRẠNG THÁI (STATUS BAR) ---
            self.status_bar = QStatusBar()
            self.status_bar.setFixedHeight(25)
            self.status_bar.showMessage("Sẵn sàng.")
            main_layout.addWidget(self.status_bar)
    
            # Biến lưu vị trí chuột phục vụ việc kéo thả cửa sổ
            self.old_pos = QPoint()
    
        # 3. Xử lý sự kiện kéo thả cửa sổ khi nhấn vào thanh tiêu đề
        def mousePressEvent(self, event):
            if event.button() == Qt.MouseButton.LeftButton:
                if self.title_bar.underMouse():
                    self.old_pos = event.globalPosition().toPoint()
    
        def mouseMoveEvent(self, event):
            if event.buttons() & Qt.MouseButton.LeftButton and self.title_bar.underMouse():
                if self.isMaximized():
                    return
                delta = event.globalPosition().toPoint() - self.old_pos
                self.move(self.pos() + delta)
                self.old_pos = event.globalPosition().toPoint()
    
        # 4. Xử lý chức năng Phóng to / Thu nhỏ cửa sổ
        def toggle_maximize(self):
            if self.isMaximized():
                self.showNormal()
                self.btn_maximize.setText("🗖")
            else:
                self.showMaximized()
                self.btn_maximize.setText("🗗")
    
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        
        window = FramelessWindow()
        
        # 5. Áp dụng bảng màu của thư viện qt-material lên ứng dụng
        apply_stylesheet(app, theme='dark_teal.xml')
        
        window.show()
        sys.exit(app.exec())
    

Hãy thận trọng khi sử dụng mã.

Nếu bạn cần tinh chỉnh hoặc phát triển thêm tính năng nào khác, hãy cho tôi biết:

  * Bạn có muốn bổ sung tính năng **kéo dãn kích thước viền (Resize)** thủ công cho cửa sổ này không?
  * Bạn có muốn thêm các thành phần nhập liệu khác của Material như **QLineEdit (Ô nhập chữ)** hay **QComboBox (Hộp chọn)** không?

