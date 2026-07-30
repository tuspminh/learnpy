Dưới đây là toàn bộ đoạn mã nguồn của bạn (sử dụng cơ chế kéo thả chuột thuần, không phụ thuộc vào thư viện tràn viền bên ngoài) đã được tích hợp thư viện **`qt-material`** , **Status Bar** , bộ 3 nút điều khiển hệ thống và logic tự động bật/tắt bo góc khi phóng to:

python
    
    
    import sys
    from PySide6.QtCore import Qt, QPoint
    from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QStatusBar
    # Nạp thư viện qt-material chính xác để áp dụng giao diện Google Material
    from qt_material import apply_stylesheet
    
    class FramelessWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.resize(800, 600)
    
            # 1. Bỏ viền và thanh tiêu đề mặc định của hệ điều hành
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    
            # 2. Làm nền cửa sổ trong suốt để hiển thị bo góc mịn màng
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
            # 3. Tạo Widget trung tâm để định hình phom dáng cửa sổ
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
    
            # Thiết lập tên đối tượng để chỉ định QSS bo góc chính xác
            self.central_widget.setObjectName("CentralWidget")
            self.update_window_styles(is_maximized=False)
    
            # Bố cục tổng thể xếp dọc (Thanh tiêu đề -> Vùng nội dung -> Status Bar)
            main_layout = QVBoxLayout(self.central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
    
            # --- THANH TIÊU ĐỀ TỰ CHẾ (TITLE BAR) ---
            self.title_bar = QWidget()
            self.title_bar.setFixedHeight(45) # Tăng nhẹ độ cao theo chuẩn Material
            self.title_bar.setObjectName("TitleBar")
            
            title_layout = QHBoxLayout(self.title_bar)
            title_layout.setContentsMargins(0, 0, 0, 0)
            title_layout.setSpacing(0)
    
            # Nhãn chữ tiêu đề
            self.title_label = QLabel("Ứng dụng Tràn viền + Qt Material")
            self.title_label.setStyleSheet("font-weight: 500; font-size: 13px; padding-left: 15px;")
            title_layout.addWidget(self.title_label)
            title_layout.addStretch()
    
            # Bộ 3 nút bấm điều khiển
            self.btn_minimize = QPushButton("🗕")
            self.btn_maximize = QPushButton("🗖")
            self.btn_close = QPushButton("🗙")
            
            # Gán tên định danh độc lập cho nút đóng để làm hiệu ứng nền đỏ khi hover
            self.btn_close.setObjectName("CloseBtn")
    
            # Kết nối chức năng nút với các hàm điều khiển cửa sổ
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
            content_layout.setContentsMargins(20, 20, 20, 20)
            
            self.label = QLabel("Cửa sổ tràn viền kết hợp Google Material 3")
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.setProperty("class", "h2") # Sử dụng định dạng font tiêu đề của qt-material
            content_layout.addWidget(self.label)
            
            # Thêm một nút bấm mẫu chuẩn Material để kiểm tra giao diện
            self.sample_btn = QPushButton("Nút bấm Material")
            self.sample_btn.setProperty("class", "primary") # Gán class nút chính đổ màu nổi bật
            self.sample_btn.setFixedWidth(200)
            content_layout.addWidget(self.sample_btn, 0, Qt.AlignmentFlag.AlignCenter)
            
            main_layout.addWidget(self.content_widget)
    
            # --- THANH TRẠNG THÁI (STATUS BAR) ---
            self.status_bar = QStatusBar()
            self.status_bar.setFixedHeight(25)
            self.status_bar.setObjectName("StatusBar")
            self.status_bar.showMessage("  Hệ thống chạy trên nền cấu hình Material Design.")
            main_layout.addWidget(self.status_bar)
    
            # Áp dụng bộ QSS bổ sung cho các thành phần nút bấm tràn viền
            self.apply_custom_frameless_qss()
    
            # Biến lưu vị trí chuột để kéo cửa sổ
            self.old_pos = QPoint()
    
        def apply_custom_frameless_qss(self):
            """Bổ sung stylesheet riêng cho bộ nút điều khiển để đè lên style mặc định của qt-material"""
            custom_qss = """
                QPushButton#CloseBtn, QPushButton {
                    border: none;
                    background-color: transparent;
                    border-radius: 0px;
                    width: 45px;
                    height: 45px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.12);
                }
                QPushButton#CloseBtn:hover {
                    background-color: #b00020; /* Màu đỏ đô chuẩn Material Error */
                    color: white;
                }
            """
            # Áp dụng riêng cho cụm thanh tiêu đề để không ảnh hưởng nút bấm ở vùng nội dung
            self.title_bar.setStyleSheet(custom_qss)
    
        def update_window_styles(self, is_maximized):
            """Tự động đổi cấu trúc bo góc dựa vào trạng thái thu phóng của cửa sổ"""
            radius = "0px" if is_maximized else "16px" # Material 3 sử dụng góc bo lớn từ 12-24px
            
            # Cập nhật viền cho Widget tổng, thanh tiêu đề và thanh status bar
            self.central_widget.setStyleSheet(f"QWidget#CentralWidget {{ border-radius: {radius}; }}")
            if hasattr(self, 'title_bar') and hasattr(self, 'status_bar'):
                self.title_bar.setStyleSheet(self.title_bar.styleSheet() + f" QWidget#TitleBar {{ border-top-left-radius: {radius}; border-top-right-radius: {radius}; }}")
                self.status_bar.setStyleSheet(f"QStatusBar#StatusBar {{ border-bottom-left-radius: {radius}; border-bottom-right-radius: {radius}; }}")
    
        # 4. Sự kiện bắt chuột kéo thả cửa sổ (Chỉ hiệu lực khi nhấn vào Thanh tiêu đề)
        def mousePressEvent(self, event):
            if event.button() == Qt.MouseButton.LeftButton:
                if self.title_bar.underMouse():
                    self.old_pos = event.globalPosition().toPoint()
    
        def mouseMoveEvent(self, event):
            if event.buttons() & Qt.MouseButton.LeftButton and self.title_bar.underMouse():
                if self.isMaximized():
                    return # Không cho phép kéo đi khi đang phóng to toàn màn hình
                delta = event.globalPosition().toPoint() - self.old_pos
                self.move(self.pos() + delta)
                self.old_pos = event.globalPosition().toPoint()
    
        # 5. Hàm xử lý logic Phóng to / Thu nhỏ
        def toggle_maximize(self):
            if self.isMaximized():
                self.showNormal()
                self.btn_maximize.setText("🗖")
                self.update_window_styles(is_maximized=False)
            else:
                self.showMaximized()
                self.btn_maximize.setText("🗗")
                self.update_window_styles(is_maximized=True)
    
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        
        # Khởi tạo cửa sổ trước khi nạp theme
        window = FramelessWindow()
        
        # 6. Áp dụng bảng màu của thư viện qt-material [1]
        # Bạn có thể thay 'dark_teal.xml' bằng 'dark_blue.xml', 'light_pink.xml', 'dark_amber.xml', v.v.
        apply_stylesheet(app, theme='dark_teal.xml')
        
        window.show()
        sys.exit(app.exec())
    

Hãy thận trọng khi sử dụng mã.

Các điểm điều chỉnh kỹ thuật để tích hợp mượt mà:

  * **Sắp xếp thứ tự** : Khởi tạo đối tượng `window = FramelessWindow()` xong mới gọi hàm `apply_stylesheet(app, ...)` [1] ở khối `if __name__ == "__main__":`. Cách sắp xếp này giúp `qt-material` phủ đều màu lên các lớp layer tự chế của bạn một cách chính xác.
  * **Bảo vệ cụm nút Hệ thống** : Đoạn hàm `apply_custom_frameless_qss` được thêm vào để ép bộ 3 nút bấm (Min/Max/Close) giữ nguyên dạng hình vuông phẳng không viền và có hiệu ứng đổi nền khi di chuột, tránh việc chúng bị ép chuyển thành dạng nút bo tròn của giao diện Material thông thường.
  * **Định vị ID bằng`#`**: Đặt tên `setObjectName` cụ thể cho các thành phần chính để kiểm soát vùng bo góc (`border-radius`) không bị lem hoặc lỗi hiển thị đen góc trên hệ điều hành Windows.



Nếu bạn cần nâng cấp thêm tính năng nào khác cho giao diện này, hãy phản hồi cho tôi biết:

  * Bạn có muốn bổ sung tính năng **Kéo dãn viền cửa sổ (Resize)** thủ công bằng chuột mà không cần dùng thư viện ngoài không?
  * Bạn có muốn tạo thêm hiệu ứng **nhấp nháy đổi màu mượt mà (Fade-in transition)** cho các nút bấm không?

