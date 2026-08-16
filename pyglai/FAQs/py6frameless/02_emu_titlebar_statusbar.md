Đoạn code ban đầu của bạn hoàn toàn **có thể** thêm được nút bấm và Status Bar. Lý do nó chưa có là vì chúng ta chưa tạo ra các thành phần đó và chưa đưa chúng vào sơ đồ bố cục (`Layout`) của ứng dụng mà thôi.

Khi đã dùng thuộc tính `FramelessWindowHint` để bỏ đi thanh tiêu đề mặc định của Windows, bạn phải tự tay code một thanh tiêu đề giả lập (gồm 1 layout nằm ngang chứa chữ và 3 nút bấm), sau đó xếp nó lên trên cùng của vùng nội dung chính.

Dưới đây là đoạn code của bạn đã được chỉnh sửa trực tiếp, giữ nguyên cơ chế kéo thả bằng chuột nhưng tích hợp thêm **Thanh tiêu đề tự chế** , **3 nút Đóng/Phóng to/Thu nhỏ** và **Status Bar** ở đáy:

python
    
    
    import sys
    from PySide6.QtCore import Qt, QPoint
    from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QStatusBar
    
    class FramelessWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.resize(800, 600)
    
            # 1. Bỏ viền và thanh tiêu đề mặc định
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    
            # 2. Làm nền cửa sổ trong suốt để bo góc
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    
            # 3. Tạo Widget trung tâm để chứa giao diện
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
    
            # Dùng QSS để bo góc toàn bộ vùng central_widget
            self.central_widget.setStyleSheet("""
                QWidget#CentralWidget {
                    background-color: #2e3440; 
                    border-radius: 15px;
                }
            """)
            self.central_widget.setObjectName("CentralWidget")
    
            # Bố cục tổng thể theo chiều dọc (Gồm: Thanh tiêu đề -> Nội dung giữa -> Status Bar)
            main_layout = QVBoxLayout(self.central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0) # Xóa lề để thanh tiêu đề sát mép
            main_layout.setSpacing(0)
    
            # --- LÀM THANH TIÊU ĐỀ GIẢ LẬP (TITLE BAR) ---
            self.title_bar = QWidget()
            self.title_bar.setFixedHeight(40)
            # Thiết kế thanh tiêu đề bo tròn 2 góc trên để khớp với cửa sổ
            self.title_bar.setStyleSheet("""
                QWidget {
                    background-color: #232831;
                    border-top-left-radius: 15px;
                    border-top-right-radius: 15px;
                }
                QLabel {
                    color: #d8dee9;
                    font-family: 'Segoe UI';
                    font-size: 13px;
                    font-weight: bold;
                    padding-left: 15px;
                }
                QPushButton {
                    color: white;
                    border: none;
                    background-color: transparent;
                    font-family: 'Segoe UI';
                    font-size: 14px;
                    width: 45px;
                    height: 40px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
                QPushButton#CloseBtn:hover {
                    background-color: #bf616a; /* Màu đỏ khi rê chuột vào nút đóng */
                }
            """)
            
            title_layout = QHBoxLayout(self.title_bar)
            title_layout.setContentsMargins(0, 0, 0, 0)
            title_layout.setSpacing(0)
    
            # Chữ tiêu đề app
            self.title_label = QLabel("Ứng dụng Tràn Viền Custom")
            title_layout.addWidget(self.title_label)
            title_layout.addStretch() # Đẩy các nút bấm về phía bên phải
    
            # Tạo 3 nút chức năng
            self.btn_minimize = QPushButton("🗕")
            self.btn_maximize = QPushButton("🗖")
            self.btn_close = QPushButton("🗙")
            self.btn_close.setObjectName("CloseBtn")
    
            # Kết nối sự kiện click của nút bấm với các hàm hệ thống của QMainWindow
            self.btn_minimize.clicked.connect(self.showMinimized)
            self.btn_maximize.clicked.connect(self.toggle_maximize)
            self.btn_close.clicked.connect(self.close)
    
            title_layout.addWidget(self.btn_minimize)
            title_layout.addWidget(self.btn_maximize)
            title_layout.addWidget(self.btn_close)
    
            # Thêm thanh tiêu đề vào bố cục chính
            main_layout.addWidget(self.title_bar)
    
            # --- VÙNG NỘI DUNG CHÍNH (CONTENT AREA) ---
            self.content_widget = QWidget()
            content_layout = QVBoxLayout(self.content_widget)
            
            self.label = QLabel("Cửa sổ tràn viền PySide6")
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.setStyleSheet("color: white; font-size: 24px; background: transparent;")
            content_layout.addWidget(self.label)
            
            main_layout.addWidget(self.content_widget)
    
            # --- THÊM STATUS BAR (THANH TRẠNG THÁI) ---
            self.status_bar = QStatusBar()
            self.status_bar.setFixedHeight(25)
            # Định dạng góc bo 2 góc dưới của Status bar để không bị lồi ra khỏi viền cong cửa sổ
            self.status_bar.setStyleSheet("""
                QStatusBar {
                    background-color: #232831;
                    color: #a3be8c;
                    font-family: 'Segoe UI';
                    font-size: 11px;
                    border-bottom-left-radius: 15px;
                    border-bottom-right-radius: 15px;
                }
            """)
            self.status_bar.showMessage("  Hệ thống sẵn sàng...")
            main_layout.addWidget(self.status_bar)
    
            # Biến lưu trữ vị trí chuột để kéo cửa sổ
            self.old_pos = QPoint()
    
        # 4. Chỉ cho phép kéo cửa sổ khi nhấn chuột vào đúng khu vực THANH TIÊU ĐỀ (Title Bar)
        def mousePressEvent(self, event):
            if event.button() == Qt.MouseButton.LeftButton:
                # Kiểm tra xem vị trí nhấn chuột có nằm trong thanh tiêu đề không
                if self.title_bar.underMouse():
                    self.old_pos = event.globalPosition().toPoint()
    
        def mouseMoveEvent(self, event):
            if event.buttons() & Qt.MouseButton.LeftButton and self.title_bar.underMouse():
                delta = event.globalPosition().toPoint() - self.old_pos
                self.move(self.pos() + delta)
                self.old_pos = event.globalPosition().toPoint()
    
        # Hàm tự viết xử lý Phóng to / Thu nhỏ kích thước cũ khi bấm nút Phóng to
        def toggle_maximize(self):
            if self.isMaximized():
                self.showNormal()
                self.btn_maximize.setText("🗖")
                # Trả lại bo góc khi ở chế độ bình thường
                self.central_widget.setStyleSheet("QWidget#CentralWidget { background-color: #2e3440; border-radius: 15px; }")
                self.title_bar.setStyleSheet("QWidget { background-color: #232831; border-top-left-radius: 15px; border-top-right-radius: 15px; } QPushButton { color: white; border: none; background-color: transparent; width: 45px; height: 40px; } QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); } QPushButton#CloseBtn:hover { background-color: #bf616a; } QLabel { color: #d8dee9; font-family: 'Segoe UI'; font-size: 13px; font-weight: bold; padding-left: 15px; }")
                self.status_bar.setStyleSheet("QStatusBar { background-color: #232831; color: #a3be8c; font-family: 'Segoe UI'; font-size: 11px; border-bottom-left-radius: 15px; border-bottom-right-radius: 15px; }")
            else:
                self.showMaximized()
                self.btn_maximize.setText("🗗")
                # Khi phóng to toàn màn hình thì phải TẮT bo góc (border-radius: 0) để không bị hở góc màn hình desktop
                self.central_widget.setStyleSheet("QWidget#CentralWidget { background-color: #2e3440; border-radius: 0px; }")
                self.title_bar.setStyleSheet("QWidget { background-color: #232831; border-top-left-radius: 0px; border-top-right-radius: 0px; } QPushButton { color: white; border: none; background-color: transparent; width: 45px; height: 40px; } QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); } QPushButton#CloseBtn:hover { background-color: #bf616a; } QLabel { color: #d8dee9; font-family: 'Segoe UI'; font-size: 13px; font-weight: bold; padding-left: 15px; }")
                self.status_bar.setStyleSheet("QStatusBar { background-color: #232831; color: #a3be8c; font-family: 'Segoe UI'; font-size: 11px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; }")
    
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = FramelessWindow()
        window.show()
        sys.exit(app.exec())
    

Hãy thận trọng khi sử dụng mã.

Những điểm cải tiến quan trọng được thêm vào đoạn code:

  1. **Chia tách layout khoa học** : Sử dụng một `main_layout` dạng dọc xếp đè lần lượt 3 tầng: `title_bar` (ngang) → `content_widget` → `status_bar`.
  2. **Giới hạn vùng kéo thả chuột** : Sửa lại điều kiện `self.title_bar.underMouse()` trong hàm bắt chuột. Giờ đây người dùng chỉ kéo được app khi bấm trúng thanh tiêu đề, bấm vào vùng nội dung giữa ứng dụng sẽ không bị kéo đi lung tung.
  3. **Logic Phóng To thông minh (`toggle_maximize`)**: Khi cửa sổ phóng to toàn màn hình, code tự động triệt tiêu góc bo tròn (`border-radius: 0px`) giúp giao diện vuông vắn khít với viền màn hình máy tính. Khi thu nhỏ lại kích thước cũ, góc bo `15px` tự động xuất hiện lại.



Nếu bạn muốn nâng cấp thêm cho giao diện này, hãy cho tôi biết:

  * Bạn có muốn thêm tính năng **Kéo dãn các cạnh viền (Resize cửa sổ)** bằng chuột không?
  * Bạn có muốn thêm hiệu ứng **Đổ bóng mờ (Drop Shadow)** bao quanh viền ngoài ứng dụng không?



