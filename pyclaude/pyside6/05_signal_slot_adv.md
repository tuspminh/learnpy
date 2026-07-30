## Bài 5: Signal & Slot Nâng Cao — Tự Định Nghĩa Signal, Truyền Tham Số, So Sánh Với `bind()`

### 1. Động lực (Motivation)

Ở Bài 5 khóa Tkinter, bạn đã thành thạo `bind()` — cơ chế lắng nghe sự kiện cấp thấp (mouse, keyboard, window). PySide6 có cơ chế tương đương nhưng đi theo triết lý hoàn toàn khác: **Signal & Slot** — một hệ thống giao tiếp giữa các object, không chỉ giới hạn ở sự kiện chuột/phím mà mở rộng ra **bất kỳ thông báo trạng thái nào** giữa các thành phần trong ứng dụng.

Đây là khái niệm **quan trọng nhất** của toàn bộ framework Qt — nếu Tkinter dạy bạn tư duy "lắng nghe sự kiện hệ thống", thì Qt dạy bạn tư duy **kiến trúc hướng sự kiện (event-driven architecture)** ở tầm ứng dụng, điều mà mọi hệ thống lớn hiện nay đều áp dụng: microservices giao tiếp qua message queue (Kafka, RabbitMQ), frontend React giao tiếp qua custom events, hay pipeline AI thông báo tiến độ huấn luyện qua callback — tất cả đều là biến thể của cùng một tư duy "phát tín hiệu — lắng nghe — phản hồi".

Trong các ứng dụng desktop thực tế 2026 — ví dụ công cụ giám sát tiến trình huấn luyện mô hình AI, hay app theo dõi đơn hàng real-time tại Tiki Logistics — Signal tự định nghĩa chính là cách để các module độc lập (worker thread xử lý dữ liệu, UI hiển thị kết quả) giao tiếp với nhau **mà không cần biết chi tiết nội bộ của nhau**.

### 2. Giải thích khái niệm

#### 2.1. Nhắc lại: Signal có sẵn của widget

Bạn đã dùng qua `clicked`, `textChanged`, `stateChanged` — đây là các **signal built-in** của widget. Nhưng bản chất Signal & Slot **không giới hạn** ở widget có sẵn. Bạn có thể tự tạo signal cho bất kỳ class Python nào.

#### 2.2. Tự định nghĩa Signal với `Signal()`

python

```python
from PySide6.QtCore import QObject, Signal

class OrderProcessor(QObject):
    # Khai báo signal ở CẤP CLASS, không phải trong __init__
    order_completed = Signal(str)          # Signal truyền 1 tham số kiểu str
    progress_updated = Signal(int)          # Signal truyền 1 tham số kiểu int
    error_occurred = Signal(str, int)       # Signal truyền nhiều tham số

    def __init__(self):
        super().__init__()   # BẮT BUỘC - QObject phải được khởi tạo đúng cách

    def process_order(self, order_id: str):
        for progress in range(0, 101, 25):
            self.progress_updated.emit(progress)   # Phát tín hiệu, kèm dữ liệu
        self.order_completed.emit(order_id)
```

**Điểm mấu chốt cần nhớ:**

1. Class phải kế thừa `QObject` (mọi widget đã tự động kế thừa `QObject`, nhưng nếu bạn tạo class **không phải widget** để xử lý logic, phải kế thừa `QObject` thủ công).
2. Signal khai báo ở **cấp class** (giống khai báo class attribute), không đặt trong `__init__`.
3. `Signal(str)` — kiểu dữ liệu trong ngoặc là **kiểu tham số sẽ truyền đi** khi phát tín hiệu, tương tự việc định nghĩa "chữ ký hàm" (type signature).
4. Dùng `.emit(giá_trị)` để **phát tín hiệu** kèm dữ liệu thực tế.

#### 2.3. Kết nối Signal tự định nghĩa với Slot

python

```python
def show_progress(value: int):
    print(f"Tiến độ xử lý: {value}%")

def show_completion(order_id: str):
    print(f"✅ Đơn hàng {order_id} đã xử lý xong!")

processor = OrderProcessor()
processor.progress_updated.connect(show_progress)
processor.order_completed.connect(show_completion)

processor.process_order("DH-10234")
```

**So sánh trực tiếp với `bind()` của Tkinter:**

| Tkinter `bind()` | PySide6 Signal/Slot |
| --- | --- |
| Giới hạn ở sự kiện hệ thống (mouse, key, window) | Phát sinh cho **bất kỳ logic nào** bạn tự định nghĩa |
| `widget.bind("<Button-1>", handler)` — handler nhận `event` object chứa mọi thông tin | `signal.connect(handler)` — handler nhận đúng tham số theo kiểu đã khai báo trong `Signal(...)` |
| Không kiểm tra kiểu dữ liệu | Có kiểm tra kiểu dữ liệu tại thời điểm khai báo (`Signal(int)` chỉ nhận int) |
| Chỉ hoạt động trên widget (đã gắn vào window) | Hoạt động trên **mọi QObject**, kể cả object không phải giao diện (như class xử lý business logic) |
| 1 event string chỉ bind được nhiều handler qua `bind_all()` phức tạp | 1 signal connect được nhiều slot đơn giản bằng nhiều dòng `.connect()` |

#### 2.4. Vì sao đây là thiết kế quan trọng: Tách biệt Logic và Giao diện

Đây chính là điểm PySide6 dạy bạn tư duy kiến trúc phần mềm chuyên nghiệp — tách "worker" (xử lý logic) ra khỏi "UI" (hiển thị), giao tiếp qua signal:

python

```python
import sys
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar

# --- LỚP LOGIC (không biết gì về giao diện) ---
class DataSyncWorker(QObject):
    progress_changed = Signal(int)
    sync_finished = Signal(str)
    sync_failed = Signal(str)

    def sync_orders_from_server(self):
        try:
            total_orders = 5
            for i in range(1, total_orders + 1):
                # Giả lập xử lý đồng bộ từng đơn hàng
                percent = int((i / total_orders) * 100)
                self.progress_changed.emit(percent)
            self.sync_finished.emit(f"Đã đồng bộ {total_orders} đơn hàng thành công")
        except Exception as e:
            self.sync_failed.emit(str(e))


# --- LỚP GIAO DIỆN (chỉ biết lắng nghe signal, không biết logic bên trong) ---
class SyncWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đồng bộ đơn hàng - Tiki Logistics Internal Tool")
        self.resize(400, 180)

        layout = QVBoxLayout(self)
        self.status_label = QLabel("Sẵn sàng đồng bộ")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        sync_btn = QPushButton("Bắt đầu đồng bộ")

        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(sync_btn)

        # Khởi tạo worker và kết nối signal với UI
        self.worker = DataSyncWorker()
        self.worker.progress_changed.connect(self.progress_bar.setValue)
        self.worker.sync_finished.connect(self._on_sync_finished)
        self.worker.sync_failed.connect(self._on_sync_failed)

        sync_btn.clicked.connect(self.worker.sync_orders_from_server)

    def _on_sync_finished(self, message: str):
        self.status_label.setText(f"✅ {message}")

    def _on_sync_failed(self, error: str):
        self.status_label.setText(f"❌ Lỗi: {error}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SyncWindow()
    window.show()
    sys.exit(app.exec())
```

**Quan sát điều đặc biệt:** `self.worker.progress_changed.connect(self.progress_bar.setValue)` — signal được kết nối **trực tiếp với setter method của widget khác**, không cần viết hàm trung gian! Đây là sức mạnh của Signal/Slot: bất kỳ hàm nào nhận đúng kiểu tham số đều có thể làm slot, kể cả method có sẵn của widget khác.

> **Ghi chú quan trọng:** Ví dụ trên chạy đồng bộ (đồng bộ giả lập tức thì), nên UI không bị đơ. Trong thực tế, tác vụ đồng bộ dữ liệu thật (gọi API, đọc DB) sẽ mất thời gian và làm UI đơ nếu chạy trực tiếp như trên. Bài 11 (QThread) sẽ dạy cách chạy `DataSyncWorker` trên **luồng riêng**, giữ nguyên cấu trúc signal này — đây chính là lý do tách Worker/UI riêng biệt ngay từ bây giờ: sau này chỉ cần "di chuyển" Worker sang thread khác mà không cần viết lại logic.

#### 2.5. Truyền tham số qua `lambda` khi cần thêm dữ liệu

Đôi khi bạn cần truyền thêm dữ liệu ngoài những gì signal cung cấp — dùng `lambda`:

python

```python
delete_btn.clicked.connect(lambda: self.delete_order(order_id="DH-10234"))
```

Cẩn trọng với **lỗi late binding** khi tạo nhiều nút trong vòng lặp — vấn đề kinh điển tương tự lỗi closure trong Tkinter khi bind trong `for`:

python

```python
# ❌ SAI - mọi nút đều xóa order_id của lần lặp CUỐI CÙNG
for order_id in ["DH-001", "DH-002", "DH-003"]:
    btn = QPushButton(f"Xóa {order_id}")
    btn.clicked.connect(lambda: self.delete_order(order_id))  # order_id bị "đóng băng" sai giá trị

# ✅ ĐÚNG - dùng default argument để "chốt" giá trị tại thời điểm tạo lambda
for order_id in ["DH-001", "DH-002", "DH-003"]:
    btn = QPushButton(f"Xóa {order_id}")
    btn.clicked.connect(lambda checked=False, oid=order_id: self.delete_order(oid))
```

> Lưu ý `checked=False` — vì signal `clicked` của `QPushButton` mặc định truyền kèm 1 tham số bool (`checked`) cho lambda, phải khai báo để không bị lệch vị trí tham số.

#### 2.6. Ngắt kết nối Signal — `disconnect()`

python

```python
processor.progress_updated.disconnect(show_progress)   # Ngắt 1 slot cụ thể
processor.progress_updated.disconnect()                 # Ngắt TẤT CẢ slot đang kết nối
```

Hữu ích khi bạn cần tạm ngừng lắng nghe 1 sự kiện (ví dụ: tạm khóa nút trong lúc xử lý để tránh double-click gây gọi API 2 lần).

### 3. Ví dụ thực tế 2026: Hệ thống thông báo nội bộ (Notification System) cho app CSKH

Mô phỏng 1 hệ thống nhỏ nơi "Trung tâm thông báo" (logic) phát tín hiệu, nhiều phần UI khác nhau cùng lắng nghe — mô hình phổ biến trong app hỗ trợ khách hàng tại các sàn TMĐT:

python

```python
import sys
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget
)

class NotificationCenter(QObject):
    """Logic trung tâm - không biết gì về giao diện"""
    new_ticket_arrived = Signal(str, str)   # (mã ticket, nội dung)
    ticket_count_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self._ticket_count = 0

    def receive_ticket(self, ticket_id: str, content: str):
        self._ticket_count += 1
        self.new_ticket_arrived.emit(ticket_id, content)
        self.ticket_count_changed.emit(self._ticket_count)


class SupportDashboard(QWidget):
    def __init__(self, notification_center: NotificationCenter):
        super().__init__()
        self.setWindowTitle("CSKH Dashboard - Trung tâm hỗ trợ")
        self.resize(450, 350)

        layout = QVBoxLayout(self)
        self.badge_label = QLabel("🔔 Ticket mới: 0")
        self.badge_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.badge_label)

        self.ticket_list = QListWidget()
        layout.addWidget(self.ticket_list)

        simulate_row = QHBoxLayout()
        simulate_btn = QPushButton("Giả lập ticket mới")
        simulate_row.addWidget(simulate_btn)
        layout.addLayout(simulate_row)

        # Kết nối UI này với 2 signal của NotificationCenter
        self.notification_center = notification_center
        self.notification_center.new_ticket_arrived.connect(self._add_ticket_to_list)
        self.notification_center.ticket_count_changed.connect(self._update_badge)

        self._ticket_counter = 0
        simulate_btn.clicked.connect(self._simulate_new_ticket)

    def _simulate_new_ticket(self):
        self._ticket_counter += 1
        self.notification_center.receive_ticket(
            ticket_id=f"TK-{1000 + self._ticket_counter}",
            content="Khách hàng phản ánh giao hàng chậm"
        )

    def _add_ticket_to_list(self, ticket_id: str, content: str):
        self.ticket_list.addItem(f"[{ticket_id}] {content}")

    def _update_badge(self, count: int):
        self.badge_label.setText(f"🔔 Ticket mới: {count}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    center = NotificationCenter()
    window = SupportDashboard(center)
    window.show()
    sys.exit(app.exec())
```

**Tư duy kiến trúc rút ra:** `NotificationCenter` hoàn toàn **không import bất kỳ thứ gì từ `QtWidgets`** — nó không biết UI trông như thế nào, chỉ phát tín hiệu. Điều này có nghĩa là bạn có thể viết **nhiều UI khác nhau** (dashboard desktop, popup nhỏ, log console) cùng lắng nghe 1 `NotificationCenter` mà không cần sửa logic gốc — đây chính xác là nguyên tắc **Separation of Concerns** (tách biệt mối quan tâm) mà mọi hệ thống phần mềm lớn đều áp dụng.

### 4. Lỗi thường gặp (Common Mistakes)

**Lỗi 1 — Quên `super().__init__()` khi tạo class kế thừa `QObject`:**

python

```python
class Worker(QObject):
    done = Signal(str)
    def __init__(self):
        pass  # ❌ Thiếu super().__init__() → signal hoạt động sai hoặc crash
```

**Lỗi 2 — Khai báo Signal bên trong `__init__` thay vì cấp class:**

python

```python
class Worker(QObject):
    def __init__(self):
        super().__init__()
        self.done = Signal(str)   # ❌ SAI hoàn toàn - Signal phải khai báo ở cấp class
```

**Lỗi 3 — `.emit()` sai kiểu dữ liệu so với khai báo:**

python

```python
progress_updated = Signal(int)
...
self.progress_updated.emit("50%")   # ❌ Truyền str trong khi khai báo int → lỗi hoặc hành vi không xác định
```

**Lỗi 4 — Lỗi late binding trong vòng lặp** (đã giải thích chi tiết ở mục 2.5) — đây là lỗi mà **hầu như ai học Qt cũng gặp ít nhất 1 lần**.

**Lỗi 5 — Kết nối slot có tham số không khớp signal:**

python

```python
progress_updated = Signal(int)

def handler(value, extra):   # ❌ handler cần 2 tham số nhưng signal chỉ truyền 1
    ...

progress_updated.connect(handler)   # Lỗi runtime khi emit
```

### 5. Bài tập thực hành

Xây dựng **"LearnHub Desktop - Hệ thống theo dõi tiến độ học tập"**, áp dụng kiến trúc tách Logic/UI vừa học:

**Yêu cầu:**

1. Tạo class `ProgressTracker(QObject)` với 2 signal tự định nghĩa:
  - `lesson_completed = Signal(str, int)` — truyền (tên bài học, số bài đã hoàn thành)
  - `course_finished = Signal(str)` — truyền tên khóa học khi hoàn thành toàn bộ (giả sử 5 bài/khóa)
2. Class này có method `complete_lesson(lesson_name: str)` — mỗi lần gọi, tăng biến đếm nội bộ, phát `lesson_completed`; nếu đếm đủ 5 bài thì phát thêm `course_finished`.
3. Tạo class UI `LearningDashboard(QWidget)` nhận `ProgressTracker` qua constructor (giống ví dụ `SupportDashboard`), gồm:
  - `QListWidget` hiển thị các bài đã hoàn thành.
  - `QLabel` hiển thị "Tiến độ: x/5 bài".
  - Nút "Hoàn thành bài tiếp theo" — mỗi lần bấm gọi `complete_lesson()` với tên bài tự sinh (VD: `f"Bài {count+1}"`).
  - Khi nhận signal `course_finished`, hiển thị thông báo chúc mừng (đổi màu `QLabel` trạng thái, khóa nút bằng `setEnabled(False)`).

Gõ "bài 6" khi hoàn thành — Bài 6 sẽ học **Menu, Toolbar, StatusBar và QMainWindow** — chuyển từ `QWidget` đơn giản sang cấu trúc cửa sổ chuyên nghiệp chuẩn ứng dụng desktop thực thụ.
