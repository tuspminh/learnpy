Để thêm thanh menu trượt bên trái (**Navigation Drawer / Side Menu**) đúng chuẩn thiết kế **Google Material 3** , chúng ta sẽ sử dụng cấu trúc `QSplitter` phối hợp với `QListWidget` (hoặc một cụm các nút bấm) và `QStackedWidget` để chuyển đổi qua lại giữa các màn hình giao diện một cách mượt mà.

Dưới đây là mã nguồn hoàn chỉnh kết hợp **Cửa sổ tràn viền Windows** , chủ đề **Material Design 3** , và thanh **Side Menu (Navigation Drawer)** có thể thu gọn / mở rộng:

python
    
    
    import sys
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtWidgets import (QApplication, QVBoxLayout, QWidget, QLabel, 
                                 QPushButton, QHBoxLayout, QLineEdit, QCheckBox,
                                 QStackedWidget, QListWidget, QListWidgetItem, QFrame)
    from qframelesswindow import FramelessMainWindow, TitleBar
    from pyqt_material import apply_stylesheet
    
    class MaterialTitleBar(TitleBar):
        """Thanh tiêu đề tràn viền phong cách Material"""
        def __init__(self, parent):
            super().__init__(parent)
            self.setFixedHeight(45)
            
            self.titleLabel = QLabel("Material 3 App with Navigation Drawer", self)
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
            self.resize(950, 600)
            self.setMinimumSize(QSize(700, 500))
            self.setTitleBar(MaterialTitleBar(self))
            
            # Widget trung tâm chứa toàn bộ giao diện
            self.main_widget = QWidget(self)
            self.setCentralWidget(self.main_widget)
            
            # Bố cục chính nằm ngang (Bên trái: Menu, Bên phải: Nội dung)
            main_layout = QHBoxLayout(self.main_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # --- 1. TẠO THANH NAVIGATION DRAWER (SIDE MENU) ---
            self.drawer_widget = QWidget()
            self.drawer_widget.setFixedWidth(220) # Chiều rộng của menu bên trái
            self.drawer_widget.setObjectName("DrawerWidget")
            
            # Dùng QSS để tạo đường viền mỏng phân cách Menu và Nội dung
            self.drawer_widget.setStyleSheet("""
                QWidget#DrawerWidget {
                    border-right: 1px solid rgba(255, 255, 255, 0.1);
                }
            """)
            
            drawer_layout = QVBoxLayout(self.drawer_widget)
            drawer_layout.setContentsMargins(10, 15, 10, 15)
            drawer_layout.setSpacing(10)
            
            # Nút Thu gọn/Mở rộng menu (Hamburger Button)
            self.toggle_btn = QPushButton(" ☰  Menu")
            self.toggle_btn.setProperty("class", "flat") # Dạng nút phẳng không viền của pyqt-material
            self.toggle_btn.setCheckable(True)
            self.toggle_btn.clicked.connect(self.toggle_drawer)
            drawer_layout.addWidget(self.toggle_btn)
            
            # Danh sách các nút chuyển Tab (Dùng QListWidget giả lập menu)
            self.menu_list = QListWidget()
            self.menu_list.setStyleSheet("""
                QListWidget {
                    border: none;
                    background: transparent;
                }
                QListWidget::item {
                    height: 45px;
                    border-radius: 22px; /* Bo tròn viên thuốc chuẩn Material 3 */
                    margin-bottom: 5px;
                    padding-left: 15px;
                }
            """)
            
            # Thêm các mục vào menu
            items = ["🏠  Trang chủ", "⚙️  Cài đặt", "👤  Tài khoản"]
            for text in items:
                item = QListWidgetItem(text)
                self.menu_list.addItem(item)
                
            self.menu_list.setCurrentRow(0) # Mặc định chọn Trang chủ
            self.menu_list.currentRowChanged.connect(self.display_page)
            drawer_layout.addWidget(self.menu_list)
            
            # --- 2. TẠO VÙNG CHỨA NỘI DUNG MULTI-PAGE (QSTACKEDWIDGET) ---
            self.page_container = QStackedWidget()
            
            # Khởi tạo các trang nội dung
            self.init_home_page()
            self.init_settings_page()
            self.init_profile_page()
            
            # Đưa Menu và Vùng nội dung vào layout chính của ứng dụng
            main_layout.addWidget(self.drawer_widget)
            main_layout.addWidget(self.page_container)
            
            # 3. Cấu hình Status Bar đáy màn hình
            self.statusBar().setFixedHeight(25)
            self.statusBar().showMessage("Hệ thống Material 3 sẵn sàng.")
    
        def init_home_page(self):
            """Trang 1: Trang chủ"""
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(40, 30, 40, 40)
            
            title = QLabel("Đây là Trang Chủ")
            title.setProperty("class", "h1")
            
            sub = QLabel("Thiết kế thanh điều hướng chuẩn Material 3 với các góc bo viên thuốc.")
            sub.setProperty("class", "body1")
            
            # Một vài widget tương tác mẫu
            input_field = QLineEdit()
            input_field.setPlaceholderText("Nhập từ khóa tìm kiếm...")
            
            btn = QPushButton("Tìm kiếm")
            btn.setProperty("class", "primary")
            
            layout.addWidget(title)
            layout.addWidget(sub)
            layout.addWidget(input_field)
            layout.addWidget(btn)
            layout.addStretch()
            
            self.page_container.addWidget(page)
    
        def init_settings_page(self):
            """Trang 2: Cài đặt"""
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(40, 30, 40, 40)
            
            title = QLabel("Cấu hình Cài đặt")
            title.setProperty("class", "h1")
            
            cb1 = QCheckBox("Bật thông báo đẩy")
            cb2 = QCheckBox("Tự động cập nhật phần mềm")
            
            layout.addWidget(title)
            layout.addWidget(cb1)
            layout.addWidget(cb2)
            layout.addStretch()
            
            self.page_container.addWidget(page)
    
        def init_profile_page(self):
            """Trang 3: Tài khoản"""
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(40, 30, 40, 40)
            
            title = QLabel("Thông tin cá nhân")
            title.setProperty("class", "h1")
            
            info = QLabel("Người dùng: Admin\nCấp độ: Developer")
            info.setProperty("class", "body2")
            
            layout.addWidget(title)
            layout.addWidget(info)
            layout.addStretch()
            
            self.page_container.addWidget(page)
    
        def display_page(self, index):
            """Hàm chuyển đổi trang khi bấm vào menu bên trái"""
            self.page_container.setCurrentIndex(index)
    
        def toggle_drawer(self):
            """Hiệu ứng thu gọn / mở rộng Side Menu khi bấm nút Hamburger"""
            if self.toggle_btn.isChecked():
                self.drawer_widget.setFixedWidth(60) # Khi thu nhỏ, chỉ chừa lại khoảng trống nhỏ chứa icon
                # Ẩn bớt chữ, chỉ giữ icon nếu bạn cấu hình text riêng, hoặc ẩn tạm thời:
                self.toggle_btn.setText(" ☰")
            else:
                self.drawer_widget.setFixedWidth(220) # Mở rộng lại kích thước cũ
                self.toggle_btn.setText(" ☰  Menu")
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = MainWindow()
        
        # Áp dụng bảng màu Material Design dạng tối (Teal)
        apply_stylesheet(app, theme='dark_teal.xml')
        
        window.show()
        sys.exit(app.exec())
    

Hãy thận trọng khi sử dụng mã.

Các điểm nhấn thiết kế trong mã nguồn:

  * **Hiệu ứng viên thuốc (Pill Shape)** : Đoạn QSS gán cho `QListWidget::item` có `border-radius: 22px;` giúp cho vệt sáng khi chọn menu bo tròn hai đầu đúng tinh thần thiết kế Material 3 của Google.
  * **QStackedWidget** : Đóng vai trò làm bộ quản lý trang. Khi người dùng bấm vào hàng số 0, 1 hoặc 2 của menu bên trái, giao diện bên phải sẽ lật sang trang tương ứng tức thì mà không bị giật lag.
  * **Tính năng Hamburger Toggle** : Khi bấm vào chữ `☰ Menu`, thanh điều hướng sẽ tự động co hẹp chiều rộng lại từ `220px` xuống `60px` để nhường diện tích hiển thị cho vùng nội dung chính.



Nếu bạn muốn hoàn thiện ứng dụng này hơn nữa, hãy cho tôi biết:

  * Bạn có muốn thêm hiệu ứng **hình hoạt họa (Animation)** chạy mượt mà khi thanh Menu đóng/mở ra không?
  * Bạn có muốn bổ sung thêm **hộp thoại Pop-up (Material Dialog)** khi người dùng bấm nút không?

