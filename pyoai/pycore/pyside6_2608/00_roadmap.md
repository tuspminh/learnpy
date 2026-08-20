Được. Tôi sẽ đóng vai **lập trình viên Python chuyên nghiệp + người hướng dẫn**, dạy bạn **PySide6 từ nền tảng đến mức có thể tự thiết kế ứng dụng desktop thực tế**, không chỉ học các widget rời rạc.

Vì trước đây bạn đã học khá nhiều Python nâng cao, tôi sẽ đi theo hướng **Deep Dive + xây project**, đặc biệt chú trọng:

* Qt Object Model
* Event Loop
* Signal / Slot
* Widget & Layout
* Model/View
* MVC/MVVM
* Threading và Worker
* SQLite
* Kiến trúc ứng dụng
* Custom Widget
* Dialog
* Styling / QSS
* Packaging
* Testing
* Ứng dụng thực tế

# Giáo trình PySide6 Deep Dive

## Phần I — Foundation

**Buổi 1. PySide6 là gì?**

* Qt là gì?
* PySide6 là gì?
* PyQt6 vs PySide6
* Cấu trúc một ứng dụng Qt
* `QApplication`
* `QWidget`
* `show()`
* Event Loop
* `app.exec()`

**Buổi 2. Qt Object Model**

* `QObject`
* Parent / Child
* Object tree
* Lifetime management
* `deleteLater()`
* Vì sao Qt có cơ chế quản lý object riêng?

**Buổi 3. Signal & Slot**

* Signal
* Slot
* `connect()`
* `emit()`
* Custom Signal
* Signal truyền dữ liệu

**Buổi 4. Event System**

* Event là gì?
* `QEvent`
* `event()`
* Mouse event
* Keyboard event
* Close event
* Event filter

**Buổi 5. Layout System**

* `QVBoxLayout`
* `QHBoxLayout`
* `QGridLayout`
* `QFormLayout`
* Stretch
* Size policy
* Margin / spacing

**Buổi 6. Widget Foundation**

* `QLabel`
* `QPushButton`
* `QLineEdit`
* `QTextEdit`
* `QCheckBox`
* `QRadioButton`
* `QComboBox`
* `QSpinBox`

**Buổi 7. Input & Validation**

* Validator
* `QIntValidator`
* `QDoubleValidator`
* `QRegularExpressionValidator`
* Form validation

**Buổi 8. Dialog**

* `QDialog`
* Modal / Modeless
* `QMessageBox`
* `QInputDialog`
* `QFileDialog`
* Custom Dialog

**Buổi 9. Main Window**

* `QMainWindow`
* MenuBar
* ToolBar
* StatusBar
* Central Widget
* Dock Widget

**Buổi 10. Mini Project**

> Xây dựng **Todo App v1**

---

# Phần II — Qt Model/View

Đây là phần cực kỳ quan trọng nếu muốn làm app chuyên nghiệp.

**Buổi 11. Model/View Architecture**

**Buổi 12. `QListView`**

**Buổi 13. `QTableView`**

**Buổi 14. `QTreeView`**

**Buổi 15. `QAbstractListModel`**

**Buổi 16. `QAbstractTableModel`**

**Buổi 17. `QAbstractItemModel`**

**Buổi 18. QModelIndex**

**Buổi 19. Roles**

* `DisplayRole`
* `EditRole`
* `DecorationRole`
* `UserRole`

**Buổi 20. Delegate**

**Buổi 21. Sorting & Filtering**

**Buổi 22. Proxy Model**

**Buổi 23. Selection Model**

**Buổi 24. Mini Project**

> **File Explorer**

---

# Phần III — UI Architecture

**Buổi 25. Tách UI khỏi Business Logic**

**Buổi 26. MVC trong PySide6**

**Buổi 27. MVVM**

**Buổi 28. Controller**

**Buổi 29. Service Layer**

**Buổi 30. Repository Pattern**

**Buổi 31. Dependency Injection**

**Buổi 32. Application State**

**Buổi 33. Event Bus**

**Buổi 34. Signal-based Architecture**

**Buổi 35. Project Structure**

Ví dụ:

```text
myapp/
│
├── main.py
│
├── app/
│   ├── application.py
│   └── config.py
│
├── domain/
│   ├── models/
│   └── services/
│
├── infrastructure/
│   ├── database/
│   └── repositories/
│
├── presentation/
│   ├── windows/
│   ├── dialogs/
│   ├── widgets/
│   └── models/
│
└── resources/
```

---

# Phần IV — Threading & Concurrency

Phần này rất phù hợp với những gì bạn vừa học về `Thread`, `ThreadPoolExecutor`, `ProcessPoolExecutor` và `asyncio`.

**Buổi 36. GUI Thread**

**Buổi 37. Vì sao GUI bị freeze?**

**Buổi 38. `QThread`**

**Buổi 39. Worker Object Pattern**

**Buổi 40. Signal giữa Worker và GUI**

**Buổi 41. Progress Bar**

**Buổi 42. Cancel Task**

**Buổi 43. `QThreadPool`**

**Buổi 44. `QRunnable`**

**Buổi 45. Concurrent Tasks**

**Buổi 46. PySide6 + `asyncio`**

**Buổi 47. PySide6 + HTTP**

**Buổi 48. Mini Project**

> **Download Manager**

---

# Phần V — SQLite + PySide6

**Buổi 49. SQLite Architecture**

**Buổi 50. Database Manager**

**Buổi 51. Repository**

**Buổi 52. Model ↔ Database**

**Buổi 53. CRUD**

**Buổi 54. Transaction**

**Buổi 55. Pagination**

**Buổi 56. Search**

**Buổi 57. Filter**

**Buổi 58. Database Migration**

**Buổi 59. Mini Project**

> **Note App + SQLite**

---

# Phần VI — Custom Widget

**Buổi 60. QWidget Deep Dive**

**Buổi 61. Custom Widget**

**Buổi 62. `paintEvent()`**

**Buổi 63. `QPainter`**

**Buổi 64. Custom Button**

**Buổi 65. Custom Progress Bar**

**Buổi 66. Custom Card**

**Buổi 67. Custom Table**

**Buổi 68. Composite Widget**

**Buổi 69. Reusable Component**

---

# Phần VII — Styling

**Buổi 70. Qt Style System**

**Buổi 71. QSS**

**Buổi 72. Selector**

**Buổi 73. Pseudo State**

```css
QPushButton:hover
QPushButton:pressed
QPushButton:disabled
```

**Buổi 74. Theme System**

**Buổi 75. Dark Mode**

**Buổi 76. Light Mode**

**Buổi 77. Dynamic Theme**

**Buổi 78. Icon System**

---

# Phần VIII — Advanced Qt

**Buổi 79. `QProperty`**

**Buổi 80. `QTimer`**

**Buổi 81. Animation**

**Buổi 82. `QStateMachine`**

**Buổi 83. Drag & Drop**

**Buổi 84. Clipboard**

**Buổi 85. System Tray**

**Buổi 86. Native File System**

**Buổi 87. Settings với `QSettings`**

**Buổi 88. Logging**

**Buổi 89. Error Handling**

---

# Phần IX — Production

**Buổi 90. Resource System**

**Buổi 91. `.qrc`**

**Buổi 92. Qt Designer**

**Buổi 93. `.ui`**

**Buổi 94. Loading UI**

**Buổi 95. Packaging**

**Buổi 96. PyInstaller**

**Buổi 97. Application Configuration**

**Buổi 98. Testing**

**Buổi 99. Architecture Review**

**Buổi 100. Production Checklist**

---

# Phần X — Project lớn

Sau khi học nền tảng, ta sẽ xây một project đủ lớn thay vì chỉ làm các ví dụ nhỏ.

## Project: Story Reader Desktop

Rất phù hợp với hướng project bạn từng muốn xây.

```text
┌─────────────────────────────────────────────┐
│                 MainWindow                  │
├──────────────┬──────────────────────────────┤
│              │                              │
│  Sources     │        Story List            │
│              │                              │
│  ├ Source A  │  ┌────────────────────────┐  │
│  ├ Source B  │  │ Story 1                │  │
│  └ Source C  │  │ Story 2                │  │
│              │  │ Story 3                │  │
│              │  └────────────────────────┘  │
│              │                              │
├──────────────┴──────────────────────────────┤
│ Status / Crawl Progress                     │
└─────────────────────────────────────────────┘
```

Kiến trúc:

```text
                    ┌──────────────┐
                    │   PySide6    │
                    │     UI       │
                    └──────┬───────┘
                           │
                    Signals / Events
                           │
                    ┌──────▼───────┐
                    │ Application  │
                    │   Service    │
                    └──────┬───────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
        Repository     Crawler        Worker
             │             │             │
             └─────────────┼─────────────┘
                           │
                    ┌──────▼───────┐
                    │    SQLite    │
                    └──────────────┘
```

---

# Cách tôi sẽ dạy mỗi buổi

Tôi đề xuất không học kiểu "widget này dùng thế nào, widget kia dùng thế nào".

Mỗi buổi sẽ có cấu trúc:

### 1. Mental Model

Giải thích **PySide6 thực sự hoạt động như thế nào**.

### 2. API

Học các class quan trọng.

### 3. Ví dụ nhỏ

Code ngắn để hiểu một khái niệm.

### 4. Deep Dive

Giải thích những thứ phía sau API.

### 5. Thiết kế

Tại sao viết như vậy, khi nào không nên viết như vậy.

### 6. Bài tập

Tự viết code.

### 7. Mini Project

Ghép kiến thức thành ứng dụng.

---
