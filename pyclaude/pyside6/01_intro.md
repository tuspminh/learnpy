## Bài 1: Cấu trúc chương trình PySide6 & Vòng lặp sự kiện (Event Loop)

### 1. Động lực (Motivation)

Khi bạn học Tkinter, bạn đã quen với việc tạo `Tk()`, gọi `mainloop()`. PySide6 cũng có cấu trúc tương tự nhưng **mạnh mẽ và chuyên nghiệp hơn nhiều**, vì nó là binding Python cho **Qt** — framework C++ đã được dùng để xây dựng hàng loạt phần mềm lớn: Adobe Photoshop (một phần UI), VLC, Maya, thậm chí một số công cụ nội bộ trong ngành fintech và ngân hàng số tại Việt Nam (Cake, Timo) dùng Qt cho các công cụ vận hành nội bộ (internal ops tools) vì nó native, nhanh, và chạy đa nền tảng (Windows/macOS/Linux) mà không cần build lại nhiều.

Trong 2026, xu hướng dùng PySide6 tăng mạnh trong mảng:

- **AI/ML tooling nội bộ**: dashboard giám sát mô hình, công cụ gán nhãn dữ liệu (labeling tool)
- **Fintech desktop apps**: phần mềm giao dịch, phần mềm kế toán nội bộ
- **Công cụ DevOps/Automation**: GUI điều khiển pipeline, giám sát server

Vì bạn đã có nền tảng Tkinter, tư duy "widget - layout - event" sẽ không xa lạ. Bài này tập trung vào cấu trúc **chuẩn Qt** vì nó khác biệt quan trọng so với Tkinter.

### 2. Cài đặt

bash

```bash
pip install PySide6
```

### 3. Giải thích khái niệm

#### 3.1. Ba thành phần cốt lõi

Mọi ứng dụng PySide6 tối thiểu cần 3 thứ:

1. **`QApplication`** — quản lý toàn bộ vòng đời ứng dụng (tương đương "linh hồn" của app). Chỉ được tạo **duy nhất một lần**.
2. **`QWidget`** (hoặc lớp con của nó) — cửa sổ/thành phần giao diện.
3. **Event loop** — vòng lặp lắng nghe sự kiện (click, gõ phím, resize...), khởi động bằng `app.exec()`.

python

```python
import sys
from PySide6.QtWidgets import QApplication, QWidget

# Bước 1: Tạo QApplication - PHẢI tạo trước bất kỳ widget nào
app = QApplication(sys.argv)

# Bước 2: Tạo cửa sổ chính
window = QWidget()
window.setWindowTitle("Ứng dụng PySide6 đầu tiên")
window.resize(400, 300)
window.show()  # Widget mặc định ẩn, phải gọi show()

# Bước 3: Khởi động vòng lặp sự kiện
sys.exit(app.exec())
```

**So sánh nhanh với Tkinter:**

| Tkinter | PySide6 | Ghi chú |
| --- | --- | --- |
| `Tk()` | `QApplication(sys.argv)` | Qt cần `sys.argv` để đọc tham số dòng lệnh (vd: theme hệ thống) |
| `root.mainloop()` | `app.exec()` | PySide6 trả về mã thoát (exit code), nên bọc trong `sys.exit()` |
| Widget tự hiện khi tạo trong `root` | Phải gọi `.show()` | Qt mặc định ẩn widget để bạn có thời gian cấu hình trước khi hiển thị |
| `root.title("...")` | `window.setWindowTitle("...")` | Qt dùng pattern `setXxx()` / `xxx()` (getter/setter) rất nhất quán |
| `root.geometry("400x300")` | `window.resize(400, 300)` | Qt tách riêng resize và move (`window.move(x, y)`) |

#### 3.2. Vì sao phải `sys.exit(app.exec())`?

`app.exec()` trả về mã thoát của ứng dụng (0 = thành công, khác 0 = lỗi). Truyền nó vào `sys.exit()` giúp:

- Hệ điều hành và script bên ngoài (CI/CD, shell script) biết ứng dụng có thoát bình thường không.
- Đây là **chuẩn công nghiệp** — mọi app Qt production đều làm vậy.

python

```python
sys.exit(app.exec())  # ✅ Chuẩn
app.exec()             # ⚠️ Chạy được nhưng không trả mã thoát cho OS
```

#### 3.3. Xây dựng ứng dụng theo hướng OOP (chuẩn thực tế)

Trong thực tế, không ai viết code phẳng như trên. Chuẩn chuyên nghiệp là kế thừa `QWidget` thành class riêng:

python

```python
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()  # Bắt buộc gọi __init__ của lớp cha
        self.setWindowTitle("LearnHub 2026 - Desktop Edition")
        self.resize(500, 350)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)  # Gắn layout trực tiếp vào self
        label = QLabel("Chào mừng đến với LearnHub Desktop!")
        layout.addWidget(label)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

**Tại sao dùng cách này?**

- Dễ mở rộng: mỗi cửa sổ/màn hình là 1 class riêng, dễ quản lý khi app lớn dần (giống bạn tách file trong dự án Tkinter LearnHub 2026).
- `if __name__ == "__main__":` đảm bảo code khởi động chỉ chạy khi file được thực thi trực tiếp, không chạy khi import — thói quen chuẩn của lập trình viên Python chuyên nghiệp.

#### 3.4. Vòng lặp sự kiện (Event Loop) hoạt động thế nào?

Giống Tkinter, PySide6 là **single-threaded UI** theo mặc định: `app.exec()` chạy một vòng lặp vô hạn, liên tục:

1. Chờ sự kiện (click chuột, gõ phím, timer, tín hiệu hệ thống...)
2. Phân phối sự kiện đến widget tương ứng
3. Vẽ lại giao diện nếu cần (repaint)

Đây là lý do **không bao giờ được chạy tác vụ nặng** (gọi API, đọc file lớn, tính toán AI) trực tiếp trong hàm xử lý sự kiện — sẽ làm UI đơ (freeze). Bài 11 (đa luồng với `QThread`) sẽ giải quyết vấn đề này — đây chính là điểm PySide6 vượt trội hẳn Tkinter về mặt kiến trúc.

### 4. Ví dụ thực tế 2026: Splash Screen khởi động cho ứng dụng nội bộ

Nhiều công ty fintech dùng PySide6 để làm công cụ nội bộ (internal tool) có màn hình chờ khi khởi động — ví dụ công cụ giám sát giao dịch real-time:

python

```python
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class TransactionMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transaction Monitor - Internal Tool v1.0")
        self.resize(600, 400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("🏦 Hệ thống giám sát giao dịch")
        title.setAlignment(Qt.AlignCenter)  # Căn giữa - dùng enum của Qt
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 20px;")
        layout.addWidget(title)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransactionMonitor()
    window.show()
    sys.exit(app.exec())
```

Lưu ý: `setStyleSheet()` dùng cú pháp **giống CSS** — đây là điểm mạnh cực lớn của Qt so với Tkinter (Tkinter không có styling linh hoạt như vậy). Chúng ta sẽ học sâu QSS ở Bài 10.

### 5. Lỗi thường gặp (Common Mistakes)

**Lỗi 1 — Tạo widget trước `QApplication`:**

python

```python
window = QWidget()          # ❌ Lỗi: "QWidget: Must construct a QApplication before a QWidget"
app = QApplication(sys.argv)
```

→ `QApplication` luôn phải được tạo **đầu tiên**, trước bất kỳ widget nào.

**Lỗi 2 — Quên gọi `.show()`:**

python

```python
window = MainWindow()
sys.exit(app.exec())   # ❌ Cửa sổ không bao giờ hiện ra
```

**Lỗi 3 — Quên `super().__init__()` khi kế thừa QWidget:**

python

```python
class MainWindow(QWidget):
    def __init__(self):
        self.setWindowTitle("...")  # ❌ Crash vì QWidget chưa được khởi tạo đúng
```

**Lỗi 4 — Tạo nhiều `QApplication` trong 1 tiến trình:**

python

```python
app1 = QApplication(sys.argv)
app2 = QApplication(sys.argv)  # ❌ Lỗi runtime, mỗi process chỉ được 1 QApplication
```

**Lỗi 5 — Nhầm giữa `resize()` và `setFixedSize()`:** `resize()` chỉ đặt kích thước ban đầu, người dùng vẫn kéo được. Nếu muốn khóa kích thước cửa sổ, dùng `window.setFixedSize(400, 300)`.

### 6. Bài tập thực hành

Xây dựng ứng dụng **"LearnHub Desktop - Màn hình chào"** (bước khởi đầu cho project xuyên suốt khóa PySide6, giống LearnHub 2026 bạn từng làm với Tkinter):

**Yêu cầu:**

1. Tạo class `WelcomeScreen(QWidget)` với `__init__` gọi `_setup_ui()`.
2. Tiêu đề cửa sổ: `"LearnHub Desktop 2026"`, kích thước `600x400`, không cho resize (dùng `setFixedSize`).
3. Thêm 1 `QLabel` hiển thị dòng chữ `"Chào mừng bạn đến với LearnHub Desktop!"`, căn giữa, style tùy chỉnh (font-size, màu chữ) qua `setStyleSheet()`.
4. Đặt vị trí cửa sổ xuất hiện tại tọa độ `(200, 100)` trên màn hình bằng `window.move(200, 100)`.
5. Chạy chương trình đúng chuẩn `if __name__ == "__main__":` và `sys.exit(app.exec())`.

Làm xong gõ "bài 2" để mình tiếp tục nhé — Bài 2 sẽ đi vào **hệ thống Layout của Qt** (`QVBoxLayout`, `QHBoxLayout`, `QGridLayout`) và so sánh trực tiếp với `pack`/`grid` của Tkinter mà bạn đã biết.
