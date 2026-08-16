Để tích hợp cả Hiệu ứng hoạt họa (Animation) đóng mở mượt mà cho thanh Side Menu và Hộp thoại Pop-up (Material Dialog) tự chế, chúng ta sẽ sử dụng lớp QPropertyAnimation của PySide6 để chạy hiệu ứng thay đổi chiều rộng (minimumWidth và maximumWidth) của thanh Menu, kết hợp với một lớp Widget tùy biến tạo hiệu ứng phủ mờ đè lên giao diện chính để làm hộp thoại Pop-up.Dưới đây là mã nguồn hoàn chỉnh đã nâng cấp cả 2 tính năng:python
```
import sys
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (QApplication, QVBoxLayout, QWidget, QLabel, 
                             QPushButton, QHBoxLayout, QLineEdit, QCheckBox,
                             QStackedWidget, QListWidget, QListWidgetItem, QGraphicsDropShadowEffect)
from qframelesswindow import FramelessMainWindow, TitleBar
from pyqt_material import apply_stylesheet

class MaterialTitleBar(TitleBar):
    """Thanh tiêu đề tràn viền phong cách Material"""
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(45)
        
        self.titleLabel = QLabel("Material 3 Full Features App", self)
        self.titleLabel.setStyleSheet("""
            font-family: 'Roboto', 'Segoe UI';
            font-size: 14px;
            font-weight: 500;
            padding-left: 15px;
        """)
        self.hBoxLayout.insertWidget(0, self.titleLabel, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)


class MaterialDialog(QWidget):
    """Hộp thoại Pop-up tùy biến chuẩn Material Design"""
    def __init__(self, parent, title_text, body_text):
        super().__init__(parent)
        self.parent = parent
        # Phủ kín toàn bộ cửa sổ cha để tạo hiệu ứng làm mờ/tối nền xung quanh (Modal overlay)
        self.setGeometry(0, 0, parent.width(), parent.height())
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.6);") # Nền tối mờ 60%
        
        # Thùng chứa nội dung Hộp thoại nằm ở giữa
        self.dialog_box = QWidget(self)
        self.dialog_box.setStyleSheet("""
            QWidget {
                background-color: #1e292b; /* Màu tối hợp tông với dark_teal */
                border-radius: 28px;       /* Bo góc lớn chuẩn Material 3 */
            }
            QLabel { background: transparent; }
        """)
        
        # Tạo hiệu ứng đổ bóng cho hộp thoại nổi bật hẳn lên
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(Qt.GlobalColor.black)
        self.dialog_box.setGraphicsEffect(shadow)
        
        # Bố cục bên trong hộp thoại
        box_layout = QVBoxLayout(self.dialog_box)
        box_layout.setContentsMargins(24, 24, 24, 24)
        box_layout.setSpacing(16)
        
        title = QLabel(title_text)
        title.setStyleSheet("font-family: 'Roboto'; font-size: 24px; color: #ffffff; font-weight: 400;")
        
        body = QLabel(body_text)
        body.setWordWrap(True)
        body.setStyleSheet("font-family: 'Roboto'; font-size: 14px; color: #a4b1b3; line-height: 1.4;")
        
        # Hàng nút bấm ở dưới cùng bên phải
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_confirm = QPushButton("Đồng ý")
        self.btn_confirm.setProperty("class", "primary")
        self.btn_confirm.clicked.connect(self.close_dialog)
        
        self.btn_cancel = QPushButton("Hủy")
        self.btn_cancel.setProperty("class", "secondary")
        self.btn_cancel.clicked.connect(self.close_dialog)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_confirm)
        
        box_layout.addWidget(title)
        box_layout.addWidget(body)
        box_layout.addLayout(btn_layout)
        
        # Căn chỉnh kích thước hộp thoại cố định
        self.dialog_box.setFixedSize(320, 200)
        self.center_dialog()

    def center_dialog(self):
        """Đặt hộp thoại luôn nằm chính giữa cửa sổ ứng dụng"""
        x = (self.width() - self.dialog_box.width()) // 2
        y = (self.height() - self.dialog_box.height()) // 2
        self.dialog_box.move(x, y)

    def close_dialog(self):
        """Đóng và xóa hộp thoại khỏi bộ nhớ"""
        self.deleteLater()


class MainWindow(FramelessMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(950, 600)
        self.setMinimumSize(QSize(700, 500))
        self.setTitleBar(MaterialTitleBar(self))
        
        # Widget trung tâm chứa toàn bộ giao diện
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        
        main_layout = QHBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- 1. THANH NAVIGATION DRAWER (SIDE MENU) ---
        self.drawer_widget = QWidget()
        self.drawer_widget.setFixedWidth(220)
        self.drawer_widget.setObjectName("DrawerWidget")
        self.drawer_widget.setStyleSheet("QWidget#DrawerWidget { border-right: 1px solid rgba(255, 255, 255, 0.1); }")
        
        drawer_layout = QVBoxLayout(self.drawer_widget)
        drawer_layout.setContentsMargins(10, 15, 10, 15)
        drawer_layout.setSpacing(10)
        
        self.toggle_btn = QPushButton(" ☰  Menu")
        self.toggle_btn.setProperty("class", "flat")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.clicked.connect(self.toggle_drawer_animation) # Sử dụng hàm animation mới
        drawer_layout.addWidget(self.toggle_btn)
        
        self.menu_list = QListWidget()
        self.menu_list.setStyleSheet("""
            QListWidget { border: none; background: transparent; }
            QListWidget::item { height: 45px; border-radius: 22px; margin-bottom: 5px; padding-left: 15px; }
        """)
        
        items = ["🏠  Trang chủ", "⚙️  Cài đặt", "👤  Tài khoản"]
        for text in items:
            self.menu_list.addItem(QListWidgetItem(text))
            
        self.menu_list.setCurrentRow(0)
        self.menu_list.currentRowChanged.connect(self.display_page)
        drawer_layout.addWidget(self.menu_list)
        
        # --- 2. VÙNG CHỨA NỘI DUNG MULTI-PAGE (QSTACKEDWIDGET) ---
        self.page_container = QStackedWidget()
        self.init_home_page()
        self.init_settings_page()
        self.init_profile_page()
        
        main_layout.addWidget(self.drawer_widget)
        main_layout.addWidget(self.page_container)
        
        # 3. Khởi tạo hiệu ứng Hoạt họa (Animation) cho Menu
        self.sidebar_animation = QPropertyAnimation(self.drawer_widget, b"minimumWidth")
        self.sidebar_animation.setDuration(250) # Thời gian chạy hiệu ứng: 250ms
        self.sidebar_animation.setEasingCurve(QEasingCurve.Type.InOutQuad) # Kiểu chạy mượt chuẩn Material
        
        # Đồng bộ chiều rộng cực đại khi chiều rộng cực tiểu thay đổi
        self.drawer_widget.widthChanged = lambda: self.drawer_widget.setMaximumWidth(self.drawer_widget.minimumWidth())
        self.sidebar_animation.valueChanged.connect(lambda val: self.drawer_widget.setMaximumWidth(val))

        self.statusBar().setFixedHeight(25)
        self.statusBar().showMessage("Sẵn sàng.")

    def init_home_page(self):
        """Trang chủ chứa nút bấm kích hoạt Pop-up"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 40)
        
        title = QLabel("Tính năng Nổi bật Material 3")
        title.setProperty("class", "h1")
        
        sub = QLabel("Bấm nút bên dưới để mở Hộp thoại Pop-up (Dialog) có nền mờ mượt mà.")
        sub.setProperty("class", "body1")
        
        # Nút kích hoạt Dialog
        btn_show_popup = QPushButton("Mở Material Dialog")
        btn_show_popup.setProperty("class", "primary")
        btn_show_popup.clicked.connect(self.show_material_dialog) # Kết nối hàm bật popup
        
        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addWidget(btn_show_popup)
        layout.addStretch()
        self.page_container.addWidget(page)

    def init_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 40)
        title = QLabel("Cấu hình Cài đặt")
        title.setProperty("class", "h1")
        layout.addWidget(title)
        layout.addStretch()
        self.page_container.addWidget(page)

    def init_profile_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 30, 40, 40)
        title = QLabel("Thông tin cá nhân")
        title.setProperty("class", "h1")
        layout.addWidget(title)
        layout.addStretch()
        self.page_container.addWidget(page)

    def display_page(self, index):
        self.page_container.setCurrentIndex(index)

    def toggle_drawer_animation(self):
        """Xử lý hiệu ứng co giãn Menu mượt mà bằng QPropertyAnimation"""
        if self.sidebar_animation.state() == QPropertyAnimation.State.Running:
            return # Nếu đang chạy dở animation thì bỏ qua tránh lỗi xung đột phím liên tục
            
        if self.toggle_btn.isChecked():
            # Cấu hình kích thước đích khi thu nhỏ
            self.sidebar_animation.setStartValue(220)
            self.sidebar_animation.setEndValue(60)
            self.toggle_btn.setText(" ☰")
        else:
            # Cấu hình kích thước đích khi phóng to trở lại
            self.sidebar_animation.setStartValue(60)
            self.sidebar_animation.setEndValue(220)
            self.toggle_btn.setText(" ☰  Menu")
            
        self.sidebar_animation.start()

    def show_material_dialog(self):
        """Khởi tạo và hiển thị Hộp thoại Pop-up"""
        dialog = MaterialDialog(
            self, 
            "Xác nhận tác vụ?", 
            "Bạn có chắc chắn muốn thực hiện hành động này không? Thao tác này sẽ áp dụng thiết kế Material 3 cho toàn hệ thống."
        )
        dialog.show()

    def resizeEvent(self, event):
        """Cập nhật lại kích thước lớp phủ mờ Dialog nếu người dùng co dãn cửa sổ chính lúc đang mở pop-up"""
        super().resizeEvent(event)
        for child in self.children():
            if isinstance(child, MaterialDialog):
                child.setGeometry(0, 0, self.width(), self.height())
                child.center_dialog()
                
    if name == "main":
        app = QApplication(sys.argv)
        window = MainWindow()
        apply_stylesheet(app, theme='dark_teal.xml')
        window.show()
        sys.exit(app.exec())
```

Hãy thận trọng khi sử dụng mã.
### Các chi tiết nâng cấp đáng giá:
1. **Hiệu ứng trượt Menu (`QEasingCurve.Type.InOutQuad`)**: Thanh Menu không bị co rút đột ngột mà chuyển động có gia tốc tăng và giảm dần, mang lại cảm giác phản hồi tự nhiên cao cấp.
2. **Lớp phủ đè Modal (Modal Overlay)**: Lớp `MaterialDialog` gán `rgba(0, 0, 0, 0.6)` phủ kín 100% diện tích app, khiến người dùng tạm thời không thể tương tác với các nút ở dưới cho tới khi xử lý xong hộp thoại, tạo sự tập trung tuyệt đối.
3. **Đổ bóng thực sự (`QGraphicsDropShadowEffect`)**: Khối Dialog trung tâm được trang bị bóng mờ khuếch tán giúp nó "nổi" lên trên mặt phẳng 2D của giao diện ứng dụng.

Để tiếp tục phát triển ứng dụng này, hãy cho tôi biết:
* Bạn có cần **bổ sung thêm bộ icon (hình ảnh đồ họa vector)** cho các dòng chữ như Trang chủ, Cài đặt thay cho emoji không?
* Bạn có muốn lưu cấu hình trạng thái của Menu (ví dụ: tắt đi bật lại app vẫn nhớ đang thu gọn hay mở rộng) bằng **QSettings** không?
