## Bài 4: Widget Nâng Cao — QTextEdit, QListWidget, QRadioButton, QSpinBox, QButtonGroup

### 1. Động lực (Motivation)

Ở Bài 4 của khóa Tkinter, bạn đã học `Text`, `Listbox`, `Radiobutton` với `control variables` (`StringVar`, `IntVar`). PySide6 giải quyết các widget này theo cách **hiện đại và object-oriented hơn hẳn** — đặc biệt là cách nhóm radio button, nơi Qt loại bỏ hoàn toàn nhu cầu về "biến điều khiển" mà thay bằng `QButtonGroup`, một object quản lý tập hợp button chuyên nghiệp.

Trong các ứng dụng thực tế 2026: công cụ gán nhãn dữ liệu cho AI/ML (data labeling tool) dùng `QListWidget` để hiển thị danh sách ảnh/văn bản cần gán nhãn; app CSKH (customer service) tại các sàn TMĐT dùng `QTextEdit` để nhân viên ghi chú lịch sử trao đổi với khách; form khảo sát/đánh giá dùng `QRadioButton` + `QButtonGroup` để chọn 1 trong nhiều lựa chọn loại trừ lẫn nhau.

### 2. Giải thích khái niệm

#### 2.1. `QTextEdit` — Vùng nhập văn bản nhiều dòng (tương đương `Text`)

python

```python
from PySide6.QtWidgets import QTextEdit

notes = QTextEdit()
notes.setPlaceholderText("Nhập ghi chú...")

# Đọc / ghi nội dung
notes.setPlainText("Nội dung ban đầu")     # Ghi text thuần
print(notes.toPlainText())                  # Đọc text thuần — tương đương text.get("1.0", END)

notes.append("Thêm dòng mới")               # Thêm vào cuối, không xóa nội dung cũ
notes.clear()                               # Xóa trắng — tương đương text.delete("1.0", END)

# Giới hạn chiều cao (Qt không có "height=5 dòng" như Tkinter, dùng pixel)
notes.setFixedHeight(120)
```

**So sánh với Tkinter `Text`:**

| Tkinter | PySide6 |
| --- | --- |
| `text.get("1.0", END)` | `text_edit.toPlainText()` |
| `text.delete("1.0", END)` | `text_edit.clear()` |
| `text.insert(END, "...")` | `text_edit.append("...")` |
| Không có sẵn rich text dễ dùng | `setHtml()` — hỗ trợ HTML/rich text ngay lập tức |

Điểm mạnh vượt trội: `QTextEdit` hỗ trợ **rich text** (in đậm, màu sắc, ảnh) qua `setHtml()` mà không cần thư viện phụ như `tkinter.html` hay các hack phức tạp.

python

```python
notes.setHtml("<b>Khách hàng VIP</b> — cần ưu tiên xử lý <span style='color:red;'>gấp</span>")
```

Signal quan trọng: `textChanged` phát ra mỗi khi nội dung thay đổi (tương tự `<KeyRelease>` bạn dùng ở Tkinter Bài 5):

python

```python
notes.textChanged.connect(lambda: print("Nội dung vừa thay đổi"))
```

#### 2.2. `QListWidget` — Danh sách chọn (tương đương `Listbox`)

python

```python
from PySide6.QtWidgets import QListWidget

task_list = QListWidget()
task_list.addItem("Xử lý đơn hàng #10234")
task_list.addItems(["Kiểm tra tồn kho", "Gọi khách hàng VIP", "Đối soát công nợ"])

# Đọc item đang chọn
selected_item = task_list.currentItem()
if selected_item:
    print(selected_item.text())

# Chọn nhiều item cùng lúc (multi-select) — điều Tkinter Listbox cần selectmode phức tạp hơn
from PySide6.QtWidgets import QAbstractItemView
task_list.setSelectionMode(QAbstractItemView.MultiSelection)

for item in task_list.selectedItems():
    print(item.text())

# Xóa item
row = task_list.currentRow()
task_list.takeItem(row)
```

**So sánh với Tkinter `Listbox`:**

| Tkinter | PySide6 |
| --- | --- |
| `listbox.get(listbox.curselection())` | `list_widget.currentItem().text()` |
| `listbox.insert(END, "x")` | `list_widget.addItem("x")` |
| `listbox.delete(index)` | `list_widget.takeItem(index)` |
| `listbox.curselection()` trả về tuple index | `currentItem()` trả về **object** `QListWidgetItem`, gọi `.text()` để lấy nội dung |

Signal hữu ích: `itemClicked` (click 1 lần) và `itemDoubleClicked` (click đúp) — tương tự bind `<<ListboxSelect>>` nhưng tách biệt rõ ràng theo loại tương tác:

python

```python
task_list.itemClicked.connect(lambda item: print(f"Đã chọn: {item.text()}"))
task_list.itemDoubleClicked.connect(lambda item: print(f"Mở chi tiết: {item.text()}"))
```

#### 2.3. `QRadioButton` + `QButtonGroup` — Nhóm lựa chọn loại trừ

Đây là khác biệt **lớn nhất** so với Tkinter. Ở Tkinter, bạn phải tạo 1 `IntVar()` hoặc `StringVar()` chung, gán `variable=` cho từng `Radiobutton`. Trong PySide6, cơ chế loại trừ lẫn nhau xảy ra **tự động theo container cha** — nếu các `QRadioButton` nằm chung 1 `QWidget`/layout cha, chúng tự động loại trừ nhau mà **không cần** biến điều khiển:

python

```python
from PySide6.QtWidgets import QRadioButton, QVBoxLayout, QWidget

container = QWidget()
layout = QVBoxLayout(container)

option_credit = QRadioButton("Thanh toán qua thẻ tín dụng")
option_ewallet = QRadioButton("Ví điện tử (Momo/ZaloPay)")
option_cod = QRadioButton("Thanh toán khi nhận hàng (COD)")
option_cod.setChecked(True)   # Chọn mặc định

layout.addWidget(option_credit)
layout.addWidget(option_ewallet)
layout.addWidget(option_cod)
```

**Vấn đề:** Nếu bạn có **2 nhóm radio button khác nhau** trong cùng 1 container (ví dụ: nhóm "phương thức thanh toán" và nhóm "phương thức giao hàng"), việc dựa vào container cha sẽ khiến **tất cả** radio button loại trừ lẫn nhau — sai logic! Đây là lý do cần `QButtonGroup`:

python

```python
from PySide6.QtWidgets import QButtonGroup

payment_group = QButtonGroup()
payment_group.addButton(option_credit, id=1)
payment_group.addButton(option_ewallet, id=2)
payment_group.addButton(option_cod, id=3)

# Đọc lựa chọn hiện tại
checked_button = payment_group.checkedButton()
print(checked_button.text())
print(payment_group.checkedId())    # In id tương ứng (1, 2, hoặc 3)

# Signal khi đổi lựa chọn
payment_group.idClicked.connect(lambda id: print(f"Đã chọn phương thức id={id}"))
```

`QButtonGroup` **không thuộc về giao diện** (không tự vẽ ra màn hình) — nó chỉ là bộ quản lý logic nhóm nút, độc lập hoàn toàn với layout hiển thị. Đây là thiết kế rất "chuyên nghiệp": tách biệt rõ ràng giữa **logic nhóm lựa chọn** và **cách bố trí trên giao diện**.

#### 2.4. `QSpinBox` — Ô nhập số có nút tăng/giảm

Tkinter không có widget tương đương sẵn (phải tự chế bằng `Entry` + validation). Đây là điểm PySide6 vượt trội hoàn toàn:

python

```python
from PySide6.QtWidgets import QSpinBox

quantity = QSpinBox()
quantity.setRange(1, 100)        # Giới hạn giá trị min-max
quantity.setValue(1)              # Giá trị mặc định
quantity.setSingleStep(1)         # Bước nhảy mỗi lần bấm nút tăng/giảm
quantity.setSuffix(" sản phẩm")   # Hiển thị hậu tố (chỉ hiển thị, không ảnh hưởng giá trị)

print(quantity.value())           # Đọc giá trị (kiểu int, không cần ép kiểu như Entry!)

quantity.valueChanged.connect(lambda val: print(f"Số lượng: {val}"))
```

Điểm cực kỳ quan trọng: `QSpinBox.value()` luôn trả về **kiểu int**, tự động validate — người dùng **không thể** gõ chữ vào ô này. Trong Tkinter, bạn phải tự viết `try/except int()` để validate `Entry`, còn ở đây Qt xử lý sẵn.

Với số thập phân, dùng `QDoubleSpinBox` (cùng API, thêm `setDecimals()`).

### 3. Ví dụ thực tế 2026: Công cụ gán nhãn dữ liệu cho mô hình AI (Data Labeling Tool)

Mô phỏng công cụ nội bộ mà đội Data/AI dùng để gán nhãn review sản phẩm — kết hợp toàn bộ widget vừa học:

python

```python
import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QTextEdit, QRadioButton,
    QButtonGroup, QSpinBox, QPushButton
)

class LabelingTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Data Labeling Tool - Sentiment Analysis")
        self.resize(600, 450)
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)

        # Cột trái: danh sách review cần gán nhãn
        left_col = QVBoxLayout()
        left_col.addWidget(QLabel("📋 Danh sách review chờ gán nhãn"))
        self.review_list = QListWidget()
        self.review_list.addItems([
            "Sản phẩm rất tốt, giao hàng nhanh!",
            "Chất lượng tệ, không như mô tả.",
            "Tạm ổn, giá hơi cao so với chất lượng.",
        ])
        left_col.addWidget(self.review_list)
        main_layout.addLayout(left_col, stretch=1)

        # Cột phải: khu vực gán nhãn
        right_col = QVBoxLayout()
        right_col.addWidget(QLabel("🏷️ Gán nhãn cảm xúc"))

        # Nhóm radio button - cảm xúc
        self.sentiment_group = QButtonGroup()
        positive_btn = QRadioButton("Tích cực (Positive)")
        neutral_btn = QRadioButton("Trung lập (Neutral)")
        negative_btn = QRadioButton("Tiêu cực (Negative)")
        for i, btn in enumerate([positive_btn, neutral_btn, negative_btn], start=1):
            self.sentiment_group.addButton(btn, id=i)
            right_col.addWidget(btn)

        # Độ tin cậy gán nhãn
        confidence_row = QHBoxLayout()
        confidence_row.addWidget(QLabel("Độ tin cậy (%):"))
        self.confidence_spin = QSpinBox()
        self.confidence_spin.setRange(0, 100)
        self.confidence_spin.setValue(80)
        self.confidence_spin.setSuffix("%")
        confidence_row.addWidget(self.confidence_spin)
        right_col.addLayout(confidence_row)

        # Ghi chú thêm
        right_col.addWidget(QLabel("Ghi chú:"))
        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Ghi chú thêm về lý do gán nhãn (nếu có)...")
        self.note_input.setFixedHeight(80)
        right_col.addWidget(self.note_input)

        submit_btn = QPushButton("✅ Lưu nhãn")
        submit_btn.clicked.connect(self._handle_submit)
        right_col.addWidget(submit_btn)

        self.status_label = QLabel("")
        right_col.addWidget(self.status_label)

        main_layout.addLayout(right_col, stretch=1)

    def _handle_submit(self):
        current_review = self.review_list.currentItem()
        checked_btn = self.sentiment_group.checkedButton()

        if not current_review:
            self.status_label.setText("⚠️ Vui lòng chọn 1 review trong danh sách!")
            self.status_label.setStyleSheet("color: red;")
            return

        if not checked_btn:
            self.status_label.setText("⚠️ Vui lòng chọn nhãn cảm xúc!")
            self.status_label.setStyleSheet("color: red;")
            return

        result = (
            f"✅ Đã gán nhãn '{checked_btn.text()}' cho review "
            f"(độ tin cậy: {self.confidence_spin.value()}%)"
        )
        self.status_label.setText(result)
        self.status_label.setStyleSheet("color: green;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LabelingTool()
    window.show()
    sys.exit(app.exec())
```

**Chú ý kỹ thuật:** `main_layout.addLayout(left_col, stretch=1)` — tham số `stretch` quyết định **tỉ lệ chiếm không gian** giữa 2 cột khi resize cửa sổ. Nếu 2 cột đều `stretch=1`, chúng chia đều 50/50 và co giãn đồng đều — kỹ thuật rất hay dùng trong layout chuyên nghiệp.

### 4. Lỗi thường gặp (Common Mistakes)

**Lỗi 1 — Radio button ở 2 nhóm khác nhau nhưng cùng container cha, quên tạo `QButtonGroup` riêng:**

python

```python
# ❌ Cả "phương thức thanh toán" và "phương thức giao hàng" cùng nằm trong 1 QWidget
# → Tất cả radio button loại trừ lẫn nhau, chọn "Momo" sẽ bỏ chọn "Giao hỏa tốc"!
```

→ Luôn tạo `QButtonGroup` riêng cho từng nhóm logic độc lập.

**Lỗi 2 — Nhầm `currentItem()` trả về `None` khi chưa chọn gì:**

python

```python
text = task_list.currentItem().text()   # ❌ AttributeError nếu chưa có gì được chọn
```

→ Luôn kiểm tra `if task_list.currentItem():` trước khi gọi `.text()`.

**Lỗi 3 — Dùng `toPlainText()` khi đã set nội dung bằng `setHtml()`:** Kết quả trả về sẽ mất hết định dạng (chỉ còn text thuần), không lỗi nhưng dễ gây nhầm lẫn logic khi cần lấy lại HTML gốc (`toHtml()`).

**Lỗi 4 — Quên `setRange()` cho `QSpinBox`:** Mặc định range là `0-99`. Nếu cần số lượng lớn hơn (ví dụ số lượng hàng trong kho, có thể hàng nghìn), quên set range sẽ khiến giá trị bị chặn ở 99 một cách khó hiểu.

**Lỗi 5 — `addButton(btn, id=...)` dùng trùng `id` cho 2 button khác nhau trong cùng group:** Sẽ khiến `checkedId()` trả về sai, khó debug vì không có lỗi runtime rõ ràng.

### 5. Bài tập thực hành

Xây dựng **"LearnHub Desktop - Đánh giá khóa học"** (mở rộng project xuyên suốt):

**Yêu cầu:**

1. `QListWidget` hiển thị danh sách 4 khóa học đã hoàn thành (dữ liệu mẫu tự đặt).
2. Khi người dùng chọn 1 khóa học trong list, hiển thị tên khóa học đó lên 1 `QLabel` phía trên khu đánh giá (dùng signal `itemClicked`).
3. `QButtonGroup` chứa 3 `QRadioButton`: "Rất hài lòng", "Bình thường", "Không hài lòng".
4. `QSpinBox` cho điểm đánh giá từ 1 đến 10, mặc định là 5.
5. `QTextEdit` để viết nhận xét chi tiết, có `setPlaceholderText()`.
6. Nút "Gửi đánh giá" — kiểm tra: phải chọn khóa học, phải chọn 1 radio button, mới cho gửi. Hiển thị kết quả tổng hợp (tên khóa học + mức hài lòng + điểm + nhận xét) trong `QLabel` trạng thái.

Gõ "bài 5" khi hoàn thành — Bài 5 sẽ đi sâu vào **Signal & Slot nâng cao**: tự định nghĩa signal riêng (`Signal()`), truyền tham số qua signal, và so sánh chi tiết với cơ chế `bind()` của Tkinter mà bạn đã thành thạo.
