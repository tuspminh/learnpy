Để tạo cửa sổ tràn viền hỗ trợ **Resize (Kéo dãn)** và có đầy đủ **Nút Đóng / Phóng to / Thu nhỏ** hoạt động chuẩn trên Windows, việc tự viết sự kiện kéo dãn bằng code thuần Python sẽ rất giật và dễ lỗi.

Giải pháp tối ưu và mượt mà nhất trên Windows là sử dụng hàm API của hệ điều hành thông qua thư viện `qframelesswindow`. Thư viện này giữ nguyên hiệu ứng snap layout của Windows 11, hỗ trợ kéo dãn mượt mà tại các cạnh viền và bo góc tự động.

1\. Cài đặt thư viện bổ trợ

Bạn mở Terminal và chạy lệnh sau để cài đặt:

bash
    
    
    pip install qframelesswindow
    

Hãy thận trọng khi sử dụng mã.

2\. Mã nguồn hoàn chỉnh (PySide6 + qframelesswindow)

Dưới đây là file code hoàn chỉnh chạy trên Windows. Giao diện sử dụng một thanh tiêu đề tùy chỉnh (Custom Title Bar) chứa 3 nút bấm chuẩn hệ thống.

python
    
    
    import sys
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QPushButton
    # Nhập class từ thư viện qframelesswindow chuyên dụng cho Windows
    from qframelesswindow import FramelessMainWindow, TitleBar
    
    class CustomTitleBar(TitleBar):
        """Thanh tiêu đề tự chỉnh sửa giao diện"""
        def __init__(self, parent):
            super().__init__(parent)
            self.setFixedHeight(40)
            
            # Đổi màu nền thanh tiêu đề bằng QSS
            self.setStyleSheet("""
                CustomTitleBar {
                    background-color: #1e1e24;
                }
                QLabel {
                    color: #ffffff;
                    font-family: 'Segoe UI';
                    font-size: 13px;
                    padding-left: 10px;
                }
            """)
            
            # Thêm nút bấm hệ thống chuẩn của thư viện vào layout bên phải
            # Thư viện tự động xử lý chức năng Min/Max/Close mượt mà
            self.titleLabel = QLabel("Ứng dụng PySide6 Tràn Viền", self)
            self.hBoxLayout.insertWidget(0, self.titleLabel, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    
    class MainWindow(FramelessMainWindow):
        def __init__(self):
            super().__init__()
            self.resize(800, 600)
            self.setMinimumSize(QSize(400, 300))
            
            # 1. Thay thế thanh tiêu đề mặc định bằng thanh tiêu đề tùy biến
            self.setTitleBar(CustomTitleBar(self))
            
            # 2. Tạo phần nội dung chính của ứng dụng
            self.main_widget = QWidget(self)
            self.setCentralWidget(self.main_widget)
            
            # Giao diện bên trong
            layout = QVBoxLayout(self.main_widget)
            self.label = QLabel("Cửa sổ này có thể Kéo dãn (Resize) mượt mà\nvà có đầy đủ nút bấm hệ thống!")
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.label)
            
            # Định dạng màu sắc vùng nội dung chính
            self.main_widget.setStyleSheet("""
                QWidget {
                    background-color: #282a36;
                }
                QLabel {
                    color: #f8f8f2;
                    font-size: 18px;
                    font-family: 'Segoe UI';
                }
            """)
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    

Hãy thận trọng khi sử dụng mã.

Điểm vượt trội của giải pháp này trên Windows:

  * **Resize hoàn hảo** : Rê chuột vào 4 cạnh hoặc 4 góc cửa sổ, con trỏ chuột sẽ tự đổi thành mũi tên hai đầu và cho phép kéo dãn mượt mà như app gốc Windows.
  * **Tích hợp tính năng Maximize** : Nút phóng to tự động nhận diện trạng thái cửa sổ. Khi đang phóng to, bấm lại sẽ thu nhỏ về kích thước cũ (Restore). Kéo thanh tiêu đề lên đỉnh màn hình cũng tự phóng to.
  * **Giữ nguyên Windows Snap Layout** : Trên Windows 11, khi bạn rê chuột (hover) vào nút Phóng to, menu chia màn hình (Snap Layout) đặc trưng của Windows vẫn sẽ hiển thị chính xác.



Nếu bạn muốn tiếp tục tùy biến giao diện này, hãy cho tôi biết:

  * Bạn có cần **thay đổi icon hình ảnh** cho các nút Đóng/Phóng to/Thu nhỏ không?
  * Bạn có muốn thêm **hiệu ứng đổ bóng (Drop Shadow)** bao quanh viền cửa sổ không?
  * Bạn có muốn bật **hiệu ứng mờ đục nền dạng Mica / Acrylic** của Windows 11 không?

