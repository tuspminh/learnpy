# Khóa học PySide6 từ A-Z

# Buổi 21: Dock Widget, Splitter, StackedWidget, TabWidget nâng cao và MDI

> **Đây là buổi học giúp bạn thiết kế giao diện theo phong cách của các phần mềm chuyên nghiệp như:**
> 
>   * Visual Studio Code 
>   * Qt Creator 
>   * Photoshop 
>   * AutoCAD 
>   * PyCharm 
>   * Android Studio 
> 


Đây là những widget được sử dụng trong hầu hết các phần mềm desktop lớn.

* * *

# Mục tiêu buổi học

Sau buổi này bạn sẽ:

  * Hiểu nhiều kiểu bố cục giao diện chuyên nghiệp. 
  * Thành thạo `QDockWidget`. 
  * Thành thạo `QSplitter`. 
  * Thành thạo `QStackedWidget`. 
  * Thành thạo `QTabWidget` nâng cao. 
  * Hiểu MDI (`QMdiArea`). 
  * Biết khi nào nên dùng từng loại. 



* * *

# 1\. Các kiểu giao diện phổ biến

## Kiểu 1: Single Window
    
    
    +--------------------------+
    |          Menu            |
    +--------------------------+
    |                          |
    |        Nội dung          |
    |                          |
    +--------------------------+

Ví dụ:

  * Calculator 
  * Notepad 



Đơn giản nhất.

* * *

## Kiểu 2: Sidebar
    
    
    +------------------------------+
    | Toolbar                      |
    +------------------------------+
    | Menu |        Content        |
    |      |                       |
    |      |                       |
    +------------------------------+

Ví dụ:

  * Telegram Desktop 
  * Spotify 
  * Discord 



* * *

## Kiểu 3: IDE
    
    
    +------------------------------------------------+
    | Menu                                           |
    +------------------------------------------------+
    | Explorer |      Editor      | Properties       |
    |          |                  |                  |
    |          |                  |                  |
    +------------------------------------------------+
    | Console                                       |
    +------------------------------------------------+

Ví dụ:

  * VS Code 
  * Qt Creator 



* * *

## Kiểu 4: MDI
    
    
    +--------------------------------------+
    |               Menu                   |
    +--------------------------------------+
    |                                      |
    |  Window A                            |
    |                                      |
    |          Window B                    |
    |                                      |
    +--------------------------------------+

Ví dụ:

  * AutoCAD 
  * Photoshop (phiên bản cũ) 
  * Một số phần mềm quản lý doanh nghiệp 



* * *

# 2\. QDockWidget

Dock Widget là cửa sổ có thể:

  * Dock (gắn) 
  * Float (tách) 
  * Kéo 
  * Thả 
  * Đóng 
  * Mở lại 



Ví dụ:
    
    
    Explorer
    
    ↓
    
    DockWidget

* * *

## Tạo Dock
    
    
    dock = QDockWidget("Explorer", self)

Thêm Widget:
    
    
    dock.setWidget(tree)

Hiển thị:
    
    
    self.addDockWidget(
        Qt.LeftDockWidgetArea,
        dock
    )

* * *

# 3\. Dock Area

Có 4 vị trí:
    
    
    Left
    
    Right
    
    Top
    
    Bottom

Ví dụ:
    
    
    Qt.LeftDockWidgetArea

* * *

# 4\. Floating

Cho phép Dock tách khỏi cửa sổ.
    
    
    dock.setFloating(True)

Kết quả:
    
    
    Explorer
    
    ↓
    
    Một cửa sổ riêng

* * *

# 5\. Dock Features

Cho phép:
    
    
    dock.setFeatures(
    
        QDockWidget.DockWidgetClosable |
    
        QDockWidget.DockWidgetMovable |
    
        QDockWidget.DockWidgetFloatable
    
    )

* * *

# 6\. QSplitter

Một trong những Widget quan trọng nhất.

Ví dụ:
    
    
    Explorer | Editor

Người dùng kéo:
    
    
    Explorer |||||| Editor

Độ rộng thay đổi.

* * *

## Tạo
    
    
    splitter = QSplitter()

Thêm Widget:
    
    
    splitter.addWidget(tree)
    
    splitter.addWidget(editor)

* * *

## Chiều

Ngang:
    
    
    QSplitter(Qt.Horizontal)

Dọc:
    
    
    QSplitter(Qt.Vertical)

* * *

# 7\. Splitter lồng nhau

Ví dụ:
    
    
    Explorer | Editor
              --------
              Console

Ta có:
    
    
    Horizontal Splitter
    
    ↓
    
    Vertical Splitter

Đây là cách VS Code hoạt động.

* * *

# 8\. Stretch Factor

Ví dụ:
    
    
    splitter.setStretchFactor(0,1)
    
    splitter.setStretchFactor(1,4)

Nghĩa là:
    
    
    Explorer
    
    20%
    
    Editor
    
    80%

* * *

# 9\. QStackedWidget

Một Widget chứa nhiều "trang".

Ví dụ:
    
    
    Page 1
    
    ↓
    
    Login

↓
    
    
    Page 2
    
    ↓
    
    Dashboard

↓
    
    
    Page 3
    
    ↓
    
    Settings

* * *

## Tạo
    
    
    stack = QStackedWidget()

* * *

## Thêm trang
    
    
    stack.addWidget(login)
    
    stack.addWidget(home)
    
    stack.addWidget(setting)

* * *

## Đổi trang
    
    
    stack.setCurrentIndex(1)

Hoặc:
    
    
    stack.setCurrentWidget(home)

* * *

# 10\. Khi nào dùng QStackedWidget?

Ví dụ:

Ứng dụng:
    
    
    Đăng nhập
    
    ↓
    
    Trang chính
    
    ↓
    
    Cài đặt
    
    ↓
    
    Thông tin

Không cần mở nhiều cửa sổ.

* * *

# 11\. QTabWidget

Đã học cơ bản.

Bây giờ nâng cao.

Thêm Tab:
    
    
    tabs.addTab(widget,"Sinh viên")

Đổi vị trí:
    
    
    tabs.setTabPosition(
    
        QTabWidget.West
    )

Tab bên trái giống VS Code.

* * *

# 12\. Đóng Tab
    
    
    tabs.setTabsClosable(True)

Bắt sự kiện:
    
    
    tabs.tabCloseRequested.connect(...)

* * *

# 13\. Di chuyển Tab
    
    
    tabs.setMovable(True)

Người dùng kéo đổi vị trí.

* * *

# 14\. Icon Tab
    
    
    tabs.addTab(
    
        widget,
    
        icon,
    
        "Python"
    
    )

* * *

# 15\. QMdiArea

MDI = Multiple Document Interface.

Ví dụ:
    
    
    Window1
    
    Window2
    
    Window3

Đều nằm trong một cửa sổ lớn.

* * *

## Tạo
    
    
    mdi = QMdiArea()

* * *

## Thêm cửa sổ
    
    
    sub = QMdiSubWindow()
    
    sub.setWidget(editor)
    
    mdi.addSubWindow(sub)
    
    sub.show()

* * *

# 16\. Chế độ hiển thị

Cascade:
    
    
    □□□□□
    
     □□□□□
    
      □□□□□
    
    
    mdi.cascadeSubWindows()

* * *

Tile:
    
    
    □□□□ □□□□
    
    □□□□ □□□□
    
    
    mdi.tileSubWindows()

* * *

# 17\. Khi nào dùng MDI?

Nên:

  * CAD 
  * Photoshop 
  * GIS 
  * IDE cũ 



Không nên:

  * CRUD 
  * POS 
  * ERP 
  * Quản lý nhân sự 



Ngày nay, nhiều ứng dụng hiện đại ưu tiên giao diện một cửa sổ với tab hoặc splitter hơn MDI.

* * *

# 18\. Dock + Splitter

Đây là kiến trúc phổ biến nhất.
    
    
    Explorer
    
    ↓
    
    Dock
    
    Editor
    
    ↓
    
    Splitter
    
    Console
    
    ↓
    
    Dock

* * *

# 19\. VS Code Layout
    
    
    +----------------------------------------------------+
    | Menu                                               |
    +----------------------------------------------------+
    | Explorer |        Editor         | Outline         |
    |          |                       |                 |
    +----------------------------------------------------+
    | Terminal                                         |
    +----------------------------------------------------+

Tương ứng:

Explorer

↓

Dock

Editor

↓

Splitter

Terminal

↓

Dock

* * *

# 20\. Qt Creator Layout
    
    
    Projects
    
    Open Documents
    
    Bookmarks
    
    ↓
    
    Dock
    
    Code Editor
    
    ↓
    
    Splitter
    
    Compile Output
    
    ↓
    
    Dock

* * *

# 21\. Thiết kế Student Manager

Ta sẽ dùng:
    
    
    Toolbar
    
    ↓
    
    Splitter
    
    ↓
    
    Left
    
    Danh sách lớp
    
    ↓
    
    Center
    
    Student Table
    
    ↓
    
    Right
    
    Thông tin sinh viên
    
    ↓
    
    Bottom
    
    Log

Không dùng MDI.

* * *

# 22\. Những lỗi người mới thường gặp

## Lỗi 1

Lạm dụng nhiều cửa sổ (`QMainWindow`).

Nên dùng:

  * Dialog 
  * StackedWidget 
  * DockWidget 



trong cùng một cửa sổ khi phù hợp.

* * *

## Lỗi 2

Không dùng Splitter.

↓

Người dùng không thay đổi được kích thước.

* * *

## Lỗi 3

Dùng MDI cho mọi ứng dụng.

↓

Không cần thiết.

* * *

## Lỗi 4

Mỗi màn hình:

↓

Một MainWindow.

Sai.

Thông thường chỉ cần **một`QMainWindow` chính**, các màn hình khác là `QWidget`, `QDialog` hoặc các trang trong `QStackedWidget`.

* * *

# 23\. Khi nào dùng Widget nào?

Widget| Nên dùng khi  
---|---  
QDockWidget| Sidebar, Explorer, Terminal, Properties  
QSplitter| Chia vùng có thể kéo thay đổi kích thước  
QStackedWidget| Chuyển đổi giữa nhiều màn hình  
QTabWidget| Nhiều tài liệu hoặc nhiều chức năng song song  
QMdiArea| Nhiều cửa sổ con trong một cửa sổ chính  
  
* * *

# Bài tập thực hành

## Bài 1

Tạo giao diện:
    
    
    Explorer
    
    |
    
    Editor

Bằng:
    
    
    QSplitter

* * *

## Bài 2

Thêm:
    
    
    Console

ở dưới.

Sử dụng:
    
    
    QSplitter

lồng nhau.

* * *

## Bài 3

Tạo:
    
    
    Login
    
    ↓
    
    Dashboard
    
    ↓
    
    Settings

Bằng:
    
    
    QStackedWidget

* * *

## Bài 4

Tạo:

  * Explorer 
  * Properties 
  * Output 



bằng:
    
    
    QDockWidget

* * *

# Mini Project cuối buổi: IDE Layout Demo

Thiết kế một ứng dụng mô phỏng bố cục của một IDE:
    
    
    +---------------------------------------------------------+
    | Menu | Toolbar                                          |
    +---------------------------------------------------------+
    | Explorer |        Editor (TabWidget)      | Properties  |
    |          |                                 |            |
    +---------------------------------------------------------+
    | Output / Terminal (Dock hoặc Splitter)                 |
    +---------------------------------------------------------+

Yêu cầu:

  * **Explorer** là `QDockWidget`. 
  * **Editor** là `QTabWidget`: 
    * Cho phép mở nhiều tab. 
    * Có thể đóng và kéo đổi vị trí tab. 
  * **Properties** là `QDockWidget`. 
  * **Output/Terminal** đặt ở phía dưới bằng `QDockWidget` hoặc `QSplitter`. 
  * Người dùng có thể thay đổi kích thước các vùng làm việc bằng `QSplitter`. 



Đây là bố cục được sử dụng rộng rãi trong các IDE hiện đại và sẽ là nền tảng tốt cho các dự án lớn.

* * *

# Tổng kết Buổi 21

Bạn đã học:

  * `QDockWidget` để tạo các cửa sổ dock linh hoạt. 
  * `QSplitter` để chia vùng giao diện có thể thay đổi kích thước. 
  * `QStackedWidget` để chuyển đổi giữa nhiều màn hình. 
  * `QTabWidget` nâng cao (đóng tab, kéo thả, icon). 
  * `QMdiArea` và `QMdiSubWindow`. 
  * Cách lựa chọn bố cục phù hợp cho từng loại ứng dụng. 



Bạn đã có đầy đủ kiến thức để thiết kế giao diện tương đương nhiều phần mềm desktop chuyên nghiệp.

* * *

# Chuẩn bị cho Buổi 22

Ở **Buổi 22** , chúng ta sẽ học về **Custom Widgets và Composite Widgets**.

Đây là bước chuyển từ "sử dụng widget có sẵn" sang "tự tạo widget của riêng mình".

Bạn sẽ học:

  * Thiết kế `Custom Widget` bằng cách kế thừa các widget có sẵn. 
  * Xây dựng `Composite Widget` (kết hợp nhiều widget thành một thành phần tái sử dụng). 
  * Tạo `Card Widget`, `SearchBox`, `Toolbar`, `StatusPanel`. 
  * Thiết kế các widget có Signal/Slot riêng. 
  * Đóng gói widget thành module để tái sử dụng trong nhiều dự án. 



Sau buổi này, bạn sẽ có thể xây dựng một thư viện widget riêng cho các ứng dụng PySide6 của mình, giúp tăng khả năng tái sử dụng và giảm đáng kể lượng mã lặp lại.

