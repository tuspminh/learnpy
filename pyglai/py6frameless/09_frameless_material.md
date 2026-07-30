Để kết hợp cửa sổ tràn viền (**Frameless Window**) với ngôn ngữ thiết kế **Google Material Design (Material 3)** trong PySide6, cách tối ưu nhất là sử dụng kết hợp bộ khung `qframelesswindow` (xử lý phần tràn viền/resize trên Windows) và thư viện `CustomWidgets` từ bộ thư viện **PyQt-Fluent-Widgets** (hoặc viết QSS theo phong cách Material).

Tuy nhiên, có một thư viện mã nguồn mở chuyên biệt giúp áp dụng trực tiếp giao diện Google Material 3 vào PySide6 rất đẹp mắt là **`PyQt-Material`**.

Dưới đây là hướng dẫn chi tiết cách tích hợp hai thư viện này để tạo ra một ứng dụng tràn viền mang đậm phong cách Material Design (nút bấm bo tròn, hiệu ứng đổ bóng, màu sắc theo bảng màu Material).

1\. Cài đặt các thư viện cần thiết

Bạn chạy lệnh sau trong Terminal để cài đặt cả thư viện tràn viền và bộ giao diện Material:

bash
    
    
    pip install qframelesswindow pyqt-material
    

Hãy thận trọng khi sử dụng mã.

2\. Mã nguồn hoàn chỉnh (Frameless + Material 3 Theme)

Đoạn code dưới đây sẽ cấu hình cửa sổ tràn viền Windows và áp dụng gói giao diện `dark_amber.xml` (hoặc bạn có thể đổi sang các màu Material khác như `dark_teal.xml`, `light_blue.xml`,...).

python
    
    
    import sys
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtWidgets import (QApplication, QVBoxLayout, QWidget, QLabel, 
                                 QPushButton, QHBoxLayout, QLineEdit, QCheckBox)
    # Nhập thư viện tràn viền Windows
    from qframelesswindow import FramelessMainWindow, TitleBar
    # Nhập thư viện Material Design
    from pyqt_material import apply_stylesheet
    
    class MaterialTitleBar(TitleBar):
        """Thanh tiêu đề tràn viền tùy biến theo phong cách Material"""
        def __init__(self, parent):
            super().__init__(parent)
            self.setFixedHeight(45) # Tăng độ cao một chút theo chuẩn Material
            
            # Thiết kế nhãn tiêu đề thanh lịch
            self.titleLabel = QLabel("Material Design 3 App", self)
            self.titleLabel.setStyleSheet("""
                font-family: 'Roboto', 'Segoe UI';
                font-size: 14px;
                font-weight: 500;
                padding-left: 15px;
            """)
            self.hBoxLayout.insertWidget(0, self.titleLabel, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    
    class MainWindow(FramelessMainWindow):
        def __init__(self):
            super().__init__()
            self.resize(800, 500)
            self.setMinimumSize(QSize(500, 400))
            
            # 1. Đặt thanh tiêu đề tràn viền tùy chỉnh
            self.setTitleBar(MaterialTitleBar(self))
            
            # 2. Vùng nội dung chính chứa các thành phần Material
            self.main_widget = QWidget(self)
            self.setCentralWidget(self.main_widget)
            
            # Tạo bố cục chứa các Widget mẫu
            layout = QVBoxLayout(self.main_widget)
            layout.setContentsMargins(30, 20, 30, 30)
            layout.setSpacing(15)
            
            # Tiêu đề lớn bên trong ứng dụng
            heading = QLabel("Chào mừng đến với Material 3")
            heading.setProperty("class", "h1") # Sử dụng class Typography của pyqt-material
            layout.addWidget(heading)
            
            # Ô nhập liệu Material (Tròn góc, hiệu ứng đường viền khi focus)
            self.input_field = QLineEdit()
            self.input_field.setPlaceholderText("Nhập thông tin tại đây...")
            layout.addWidget(self.input_field)
            
            # Hộp kiểm Checkbox phong cách Material
            self.checkbox = QCheckBox("Tôi đồng ý với các điều khoản điều kiện")
            layout.addWidget(self.checkbox)
            
            # Hàng nút bấm bo tròn (Contained Button & Outlined Button)
            btn_layout = QHBoxLayout()
            
            self.btn_primary = QPushButton("Nút Chính (Primary)")
            self.btn_primary.setProperty("class", "primary") # Class định dạng nút chính
            
            self.btn_secondary = QPushButton("Hủy bỏ")
            self.btn_secondary.setProperty("class", "secondary") # Class định dạng nút phụ
            
            btn_layout.addWidget(self.btn_primary)
            btn_layout.addWidget(self.btn_secondary)
            btn_layout.addStretch()
            
            layout.addLayout(btn_layout)
            layout.addStretch() # Đẩy các thành phần lên trên
            
            # 3. Thanh trạng thái đáy cửa sổ
            self.statusBar().setFixedHeight(25)
            self.statusBar().showMessage("Hệ thống hoạt động ổn định.")
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        
        # Khởi tạo MainWindow trước
        window = MainWindow()
        
        # 4. Áp dụng bảng màu Material Design cho toàn bộ ứng dụng PySide6
        # Các chủ đề phổ biến: 'dark_amber.xml', 'dark_teal.xml', 'light_blue.xml', 'dark_purple.xml'
        apply_stylesheet(app, theme='dark_teal.xml')
        
        window.show()
        sys.exit(app.exec())
    

Hãy thận trọng khi sử dụng mã.

Các đặc điểm Material Design đạt được:

  * **Typography chuẩn** : Thư viện tự động ánh xạ các thuộc tính font chữ Roboto gọn gàng, hỗ trợ các lớp tiêu đề như `h1`, `h2`, `danger` thông qua thuộc tính `.setProperty("class", "...")`.
  * **Nút bấm & Ô nhập liệu bo góc**: Khác với nút vuông thô cứng mặc định, các nút bấm giờ đây có góc bo cong mềm mại đúng tinh thần Material 3, có hiệu ứng đổi màu uyển chuyển khi di chuột qua (hover).
  * **Đồng bộ màu sắc (Theme-ready)** : Thanh tiêu đề tràn viền và nội dung bên dưới tự động ăn khớp màu sắc với nhau nhờ cơ chế kế thừa stylesheet của `pyqt-material`.



Nếu bạn muốn tùy biến sâu hơn nữa, hãy cho tôi biết:

  * Bạn có muốn thay đổi sang một **bảng màu cụ thể** nào khác không (ví dụ: Light Mode hay Dark Mode)?
  * Bạn có muốn tích hợp thêm hiệu ứng **Đổ bóng (Drop Shadow)** ở viền ngoài cửa sổ không?
  * Bạn có cần thêm menu **Navigation Drawer** (thanh menu trượt bên trái chuẩn Material) không?

