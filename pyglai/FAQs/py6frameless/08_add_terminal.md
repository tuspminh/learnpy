Để tích hợp một ô **Console / Terminal** mô phỏng giống y hệt như VS Code ở phía dưới ứng dụng, phương pháp chuẩn nhất là chia màn hình chính bằng `QSplitter` (cho phép người dùng kéo thả để thay đổi chiều cao của khu vực Terminal) và sử dụng `QTextEdit` để hiển thị dòng chữ xuất ra từ hệ thống.

Dưới đây là mã nguồn hoàn chỉnh tích hợp thanh tiêu đề, vùng nội dung, thanh trạng thái, và một phân vùng **Terminal** có phong cách giao diện tối (Dark Mode) giống VS Code:

python
    
    
    import sys
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtGui import QFont, QTextCursor
    from PySide6.QtWidgets import (QApplication, QVBoxLayout, QWidget, QLabel, 
                                 QTextEdit, QSplitter, QTabWidget, QHBoxLayout, QPushButton)
    from qframelesswindow import FramelessMainWindow, TitleBar
    
    class CustomTitleBar(TitleBar):
        """Thanh tiêu đề tùy chỉnh"""
        def __init__(self, parent):
            super().__init__(parent)
            self.setFixedHeight(40)
            self.setStyleSheet("""
                CustomTitleBar { background-color: #1e1e1e; }
                QLabel { color: #cccccc; font-family: 'Segoe UI'; font-size: 13px; padding-left: 10px; }
            """)
            self.titleLabel = QLabel("VS Code Style Window - PySide6", self)
            self.hBoxLayout.insertWidget(0, self.titleLabel, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    
    class MainWindow(FramelessMainWindow):
        def __init__(self):
            super().__init__()
            self.resize(1000, 700)
            self.setMinimumSize(QSize(600, 400))
            self.setTitleBar(CustomTitleBar(self))
            
            # Widget trung tâm chứa toàn bộ bố cục
            self.main_widget = QWidget(self)
            self.setCentralWidget(self.main_widget)
            main_layout = QVBoxLayout(self.main_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
    
            # 1. Dùng QSplitter để chia dọc màn hình (Nội dung trên, Terminal dưới)
            splitter = QSplitter(Qt.Orientation.Vertical)
            
            # --- PHẦN 1: VÙNG NỘI DUNG CHÍNH (PHÍA TRÊN) ---
            self.top_widget = QWidget()
            self.top_widget.setStyleSheet("background-color: #1e1e1e; border-bottom: 1px solid #2b2b2b;")
            top_layout = QVBoxLayout(self.top_widget)
            
            self.editor_placeholder = QLabel("VÙNG SOẠN THẢO / NỘI DUNG CHÍNH")
            self.editor_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.editor_placeholder.setStyleSheet("color: #717171; font-size: 16px; font-family: 'Segoe UI';")
            top_layout.addWidget(self.editor_placeholder)
            
            # --- PHẦN 2: PANEL TERMINAL GIỐNG VS CODE (PHÍA DƯỚI) ---
            self.bottom_panel = QWidget()
            self.bottom_panel.setStyleSheet("background-color: #181818;")
            bottom_layout = QVBoxLayout(self.bottom_panel)
            bottom_layout.setContentsMargins(0, 0, 0, 0)
            bottom_layout.setSpacing(0)
            
            # Thanh điều hướng Tab của Terminal (Giống thanh Tabs: PROBLEMS, OUTPUT, DEBUG CONSOLE, TERMINAL)
            self.tab_bar = QWidget()
            self.tab_bar.setFixedHeight(35)
            self.tab_bar.setStyleSheet("background-color: #181818; border-bottom: 1px solid #2b2b2b;")
            tab_layout = QHBoxLayout(self.tab_bar)
            tab_layout.setContentsMargins(15, 0, 15, 0)
            
            # Tạo nhãn giả lập Tab đang chọn
            self.terminal_tab_btn = QPushButton("TERMINAL")
            self.terminal_tab_btn.setStyleSheet("""
                QPushButton {
                    color: #ffffff; 
                    font-family: 'Segoe UI'; 
                    font-size: 11px; 
                    font-weight: bold;
                    border: none;
                    border-bottom: 2px solid #007acc; /* Viền xanh chuẩn VS Code */
                    padding: 5px 10px;
                    background: transparent;
                }
            """)
            tab_layout.addWidget(self.terminal_tab_btn, 0, Qt.AlignmentFlag.AlignLeft)
            tab_layout.addStretch() # Đẩy khoảng trống sang bên phải
            
            # Ô nhập xuất văn bản Console Terminal
            self.terminal_box = QTextEdit()
            self.terminal_box.setReadOnly(False) # Cho phép gõ (hoặc True nếu chỉ muốn xuất log)
            
            # Định dạng font chữ Code (Monospace) và màu sắc chữ Terminal
            font = QFont("Consolas", 11)
            self.terminal_box.setFont(font)
            self.terminal_box.setStyleSheet("""
                QTextEdit {
                    background-color: #181818;
                    color: #cccccc;
                    border: none;
                    padding-left: 10px;
                    line-height: 1.4;
                }
            """)
            
            # Thêm các phần vào bố cục panel phía dưới
            bottom_layout.addWidget(self.tab_bar)
            bottom_layout.addWidget(self.terminal_box)
            
            # Thêm 2 vùng lớn vào bộ chia Splitter
            splitter.addWidget(self.top_widget)
            splitter.addWidget(self.bottom_panel)
            
            # Thiết lập tỷ lệ mặc định (70% trên, 30% dưới)
            splitter.setSizes([500, 200])
            
            # Đưa splitter vào layout chính
            main_layout.addWidget(splitter)
            
            # 2. Khởi tạo thanh Status Bar chuẩn VS Code dưới đáy ứng dụng
            self.init_status_bar()
            
            # Thử ghi một đoạn văn bản chào mừng vào Terminal
            self.append_terminal_text("Windows PowerShell\nCopyright (C) Microsoft Corporation. All rights reserved.\n\nPS C:\\Users\\PySide6_Project> _")
    
        def init_status_bar(self):
            """Khởi tạo thanh trạng thái màu xanh/tím chuẩn VS Code"""
            status_bar = self.statusBar()
            status_bar.setFixedHeight(22)
            status_bar.setStyleSheet("""
                QStatusBar {
                    background-color: #007acc;  /* Màu xanh đặc trưng của VS Code */
                    color: #ffffff;
                    font-family: 'Segoe UI';
                    font-size: 12px;
                }
                QStatusBar::item { border: none; }
            """)
            status_bar.showMessage("  Master*  ", 0)
            
            # Thêm thông số bên phải (Ln 1, Col 1, UTF-8, LF)
            self.info_label = QLabel("Spaces: 4   UTF-8   LF   Python   ")
            self.info_label.setStyleSheet("color: #ffffff; font-family: 'Segoe UI'; font-size: 12px;")
            status_bar.addPermanentWidget(self.info_label)
    
        def append_terminal_text(self, text):
            """Hàm dùng để xuất log hoặc text mới vào terminal"""
            self.terminal_box.movePosition(QTextCursor.MoveOperation.End)
            self.terminal_box.insertPlainText(text)
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    

Hãy thận trọng khi sử dụng mã.

Các tính năng mô phỏng VS Code đạt được trong code này:

  * **Giao diện phân tầng** : Sử dụng thanh màu đen sẫm (`#181818`) riêng biệt cho Terminal để tách biệt trực quan với khu vực làm việc chính phía trên (`#1e1e1e`).
  * **Kéo dãn linh hoạt (Resizable Splitter)** : Người dùng có thể đưa chuột vào ranh giới giữa Terminal và vùng nội dung để kéo lên/xuống thu phóng diện tích tùy ý.
  * **Font chữ chuyên dụng** : Sử dụng font `Consolas` để căn chỉnh các ký tự lập trình đều nhau tăm tắp.
  * **Thanh Status Bar xanh lam** : Tự động đồng bộ màu xanh chuẩn hệ thống giúp ứng dụng trông như một IDE thực thụ.



Nếu bạn muốn nâng cấp sâu hơn cho phần Terminal này, hãy cho tôi biết:

  * Bạn có muốn kết nối ô Terminal này với **CMD / PowerShell thật** của Windows (để gõ lệnh `pip install`, `dir` chạy được thật) không?
  * Bạn có cần **bắt các sự kiện phím** (ví dụ nhấn `Enter` trong terminal để xử lý chuỗi) không?

