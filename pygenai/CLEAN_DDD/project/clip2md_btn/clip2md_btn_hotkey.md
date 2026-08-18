Để tích hợp phím tắt toàn hệ thống (Global Hotkey) như **`Ctrl+Alt+V`** bằng thư viện `keyboard`, bạn cần lưu ý một số điểm quan trọng về **đa luồng (multithreading)**:

1. Thư viện `keyboard` lắng nghe sự kiện ở một background thread riêng.
2. Khi phím tắt được nhấn, hàm handler của `keyboard` được gọi từ thread đó. Việc cập nhật UI của Flet phải được thực thi an toàn thông qua thread chính (hoặc cơ chế tương thích với event loop/UI thread).

---

### Các bước nâng cấp mã nguồn

#### Step 1: Cài đặt thư viện `keyboard`

Lưu ý: Trên Windows, thư viện `keyboard` cần quyền **Administrator** nếu chạy ứng dụng trực tiếp từ Terminal thông thường, hoặc bạn chạy IDE (VS Code/PyCharm) dưới quyền Administrator để listener hoạt động chính xác.

```bash
pip install keyboard

```

---

#### Step 2: Cập nhật `presentation/main.py`

Dưới đây là phiên bản cập nhật của file `presentation/main.py` bổ sung đăng ký phím tắt toàn hệ thống:

```python
import threading
import keyboard
import flet as ft
from infrastructure.clipboard_adapter import PyperclipAdapter
from infrastructure.html_adapter import BS4Html2TextTransformer
from application.use_cases import ProcessClipboardToMarkdownUseCase

def main(page: ft.Page):
    # 1. Cấu hình cửa sổ nổi nhỏ gọn
    page.title = "HTML2MD"
    page.window.width = 180
    page.window.height = 110
    page.window.always_on_top = True
    page.window.resizable = False
    page.padding = 8
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # 2. Khởi tạo Dependency Injection
    clipboard_service = PyperclipAdapter()
    transformer = BS4Html2TextTransformer()
    use_case = ProcessClipboardToMarkdownUseCase(
        clipboard_service=clipboard_service,
        transformer=transformer
    )

    # Khóa tránh việc bấm trùng lặp khi đang xử lý
    is_processing = False

    def process_conversion():
        nonlocal is_processing
        if is_processing:
            return
        
        is_processing = True
        btn.disabled = True
        btn.icon = ft.Icons.HOURGLASS_EMPTY
        page.update()

        success = use_case.execute()

        if success:
            btn.icon = ft.Icons.CHECK_CIRCLE
            btn.style = ft.ButtonStyle(color=ft.Colors.GREEN)
            page.open(ft.SnackBar(ft.Text("Đã chuyển đổi sang Markdown! (Ctrl+Alt+V)"), duration=1500))
        else:
            btn.icon = ft.Icons.ERROR_OUTLINE
            btn.style = ft.ButtonStyle(color=ft.Colors.RED)
            page.open(ft.SnackBar(ft.Text("Clipboard rỗng hoặc không đúng format HTML"), duration=1500))

        btn.disabled = False
        is_processing = False
        page.update()

    def on_activate_click(e):
        process_conversion()

    # 3. Handler cho Global Hotkey (được gọi từ thread khác)
    def on_hotkey_pressed():
        # Đảm bảo lệnh cập nhật UI/xử lý chạy an toàn trên UI thread/event loop
        # Trong Flet, page.run_thread() hoặc threading giúp thực thi mà không nghẽn UI
        threading.Thread(target=process_conversion, daemon=True).start()

    # 4. Đăng ký Global Hotkey với thư viện `keyboard`
    HOTKEY = "ctrl+alt+v"
    try:
        keyboard.add_hotkey(HOTKEY, on_hotkey_pressed)
    except Exception as ex:
        print(f"Lỗi khi đăng ký hotkey: {ex}")

    # 5. Dọn dẹp hotkey khi tắt cửa sổ/ứng dụng
    def on_window_event(e):
        if e.data == "close":
            keyboard.remove_hotkey(HOTKEY)
            page.window.destroy()

    page.window.on_event = on_window_event

    # 6. Giao diện người dùng
    btn = ft.ElevatedButton(
        text="Convert (Ctrl+Alt+V)",
        icon=ft.Icons.TRANSFORM,
        on_click=on_activate_click,
        style=ft.ButtonStyle(
            padding=ft.padding.all(10),
        )
    )

    page.add(btn)

if __name__ == "__main__":
    ft.app(target=main)

```

---

### Chi tiết các điểm cải tiến:

1. **Xử lý Bất đồng bộ / Thread Safety**:
* Dùng `threading.Thread(target=process_conversion, daemon=True).start()` khi hotkey được kích hoạt để đảm bảo không chặn main thread của thư viện `keyboard`.
* Sử dụng biến flag `is_processing` để ngăn chặn việc gọi liên tiếp nếu người dùng lỡ nhấn `Ctrl+Alt+V` nhiều lần quá nhanh.


2. **Dọn dẹp tài nguyên (Clean up)**:
* Sự kiện `page.window.on_event` lắng nghe khi đóng cửa sổ và gọi `keyboard.remove_hotkey(HOTKEY)` để tránh việc duy trì hook phím tắt chạy ngầm trong hệ thống sau khi ứng dụng đã tắt.


3. **Ghi chú khi vận hành**:
* Nếu ứng dụng không nhận phím tắt trên Windows, hãy thử mở CMD/PowerShell dưới quyền **Run as Administrator** rồi chạy file python.