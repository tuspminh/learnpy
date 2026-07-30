# Khóa học win32clipboard Deep Dive

# Buổi 5: CF_BITMAP, CF_DIB và xử lý ảnh trong Clipboard

Đây là buổi học đưa chúng ta bước sang một mức độ hoàn toàn mới.

Từ buổi này trở đi, bạn sẽ bắt đầu làm việc với **ảnh trong Windows Clipboard**.

Đây là kiến thức được sử dụng trong:

  * ShareX 
  * Greenshot 
  * Snipping Tool 
  * PowerToys 
  * Photoshop 
  * Paint 
  * Microsoft Office 
  * Discord 
  * Slack 
  * Teams 



và rất nhiều phần mềm chuyên nghiệp khác.

* * *

# Mục tiêu

Sau buổi học bạn sẽ hiểu:

  * `CF_BITMAP`
  * `CF_DIB`
  * `CF_DIBV5`
  * Handle (HBITMAP) 
  * Device Dependent Bitmap (DDB) 
  * Device Independent Bitmap (DIB) 
  * Vì sao `CF_DIB` được sử dụng phổ biến hơn `CF_BITMAP`
  * Chuyển dữ liệu Clipboard thành `PIL.Image`
  * Lưu ảnh Clipboard thành PNG/JPEG 
  * Thiết kế `ImageClipboard`



* * *

# 1\. Copy một ảnh thì Clipboard chứa gì?

Ví dụ:

  * Nhấn **Print Screen**
  * Hoặc **Win + Shift + S**
  * Hoặc Copy một ảnh từ Paint 



Clipboard **không chỉ chứa một định dạng**.

Có thể có:
    
    
    Clipboard
    
    ├── CF_BITMAP
    ├── CF_DIB
    ├── CF_DIBV5
    ├── PNG (Custom Format)
    ├── HTML Format
    └── ...

Nhiều ứng dụng còn thêm cả định dạng PNG hoặc JPEG riêng để tăng khả năng tương thích.

* * *

# 2\. Bitmap là gì?

Bitmap là ma trận điểm ảnh.

Ví dụ ảnh 4×4:
    
    
    R G B Y
    
    W W K K
    
    R R B B
    
    G G G G

Mỗi ô là một pixel.

* * *

# 3\. CF_BITMAP
    
    
    win32clipboard.CF_BITMAP

Đây là định dạng cổ điển.

Điều quan trọng:

`GetClipboardData(CF_BITMAP)` **không trả về dữ liệu ảnh** , mà trả về **handle** của Windows.

Ví dụ:
    
    
    bitmap = win32clipboard.GetClipboardData(
        win32clipboard.CF_BITMAP
    )
    
    print(bitmap)

Kết quả:
    
    
    197420

Đây **không phải ảnh**.

Nó chỉ là:
    
    
    HBITMAP

* * *

# 4\. Handle là gì?

Windows không trả về đối tượng thật.

Nó trả về:
    
    
    Handle
    
    ↓
    
    12345

Giống như:
    
    
    Chìa khóa
    
    ↓
    
    Mở tủ
    
    ↓
    
    Lấy đồ

Handle chỉ là một "khóa" để Windows quản lý tài nguyên.

* * *

# 5\. DDB (Device Dependent Bitmap)

`CF_BITMAP`

↓

DDB

Nó phụ thuộc vào:

  * Card đồ họa 
  * Driver 
  * Device Context (DC) 



Do đó:

  * Khó lưu thành PNG trực tiếp. 
  * Khó chia sẻ giữa các ứng dụng. 



* * *

# 6\. DIB (Device Independent Bitmap)

Để khắc phục hạn chế của DDB, Windows tạo ra:
    
    
    CF_DIB

Đây là:
    
    
    Device Independent Bitmap

Ưu điểm:

  * Không phụ thuộc card màn hình. 
  * Có thể lưu file. 
  * Có thể truyền qua mạng. 
  * Có thể xử lý bằng Pillow. 



Đó là lý do **đa số ứng dụng hiện đại ưu tiên`CF_DIB`**.

* * *

# 7\. CF_DIB trả về gì?
    
    
    data = win32clipboard.GetClipboardData(
        win32clipboard.CF_DIB
    )

`data` là:
    
    
    bytes

Ví dụ:
    
    
    print(type(data))

Kết quả:
    
    
    <class 'bytes'>

Đây chính là dữ liệu nhị phân của ảnh.

* * *

# 8\. Cấu trúc DIB

Một DIB gồm:
    
    
    BITMAPINFOHEADER
    
    ↓
    
    Color Table (nếu có)
    
    ↓
    
    Pixel Data
    
    
    +----------------------+
    | Header               |
    +----------------------+
    | Color Palette        |
    +----------------------+
    | Pixel                |
    +----------------------+

Thông thường chúng ta **không cần tự phân tích thủ công** , vì Pillow có thể hỗ trợ khi được cung cấp đúng định dạng.

* * *

# 9\. Tại sao Pillow không mở trực tiếp CF_DIB?

Một file BMP đầy đủ gồm:
    
    
    BMP FILE
    
    FILE HEADER
    
    ↓
    
    DIB HEADER
    
    ↓
    
    PIXELS

Trong khi:
    
    
    CF_DIB
    
    ↓
    
    DIB HEADER
    
    ↓
    
    PIXELS

Thiếu:
    
    
    BITMAPFILEHEADER

Vì vậy cần thêm header BMP trước khi đưa cho Pillow.

* * *

# 10\. Chuyển CF_DIB thành BMP

Ý tưởng:
    
    
    Clipboard
    
    ↓
    
    CF_DIB
    
    ↓
    
    Thêm BITMAPFILEHEADER
    
    ↓
    
    BMP
    
    ↓
    
    Pillow

* * *

# 11\. Hàm chuyển đổi
    
    
    import io
    import struct
    from PIL import Image
    
    
    def dib_to_image(dib_data: bytes) -> Image.Image:
        header_size = struct.unpack("<I", dib_data[:4])[0]
    
        file_size = 14 + len(dib_data)
        offset = 14 + header_size
    
        bmp_header = struct.pack(
            "<2sIHHI",
            b"BM",
            file_size,
            0,
            0,
            offset,
        )
    
        bmp = bmp_header + dib_data
    
        return Image.open(io.BytesIO(bmp))

Đây là một kỹ thuật rất phổ biến trong các ứng dụng Windows.

* * *

# 12\. Đọc ảnh từ Clipboard
    
    
    import win32clipboard
    
    win32clipboard.OpenClipboard()
    
    try:
    
        if win32clipboard.IsClipboardFormatAvailable(
            win32clipboard.CF_DIB
        ):
    
            dib = win32clipboard.GetClipboardData(
                win32clipboard.CF_DIB
            )
    
    finally:
    
        win32clipboard.CloseClipboard()

Sau đó:
    
    
    img = dib_to_image(dib)

* * *

# 13\. Lưu PNG
    
    
    img.save("clipboard.png")

Hoặc:
    
    
    img.save(
        "clipboard.jpg",
        quality=95
    )

* * *

# 14\. Hiển thị thông tin ảnh
    
    
    print(img.width)
    
    print(img.height)
    
    print(img.mode)
    
    print(img.format)

Ví dụ:
    
    
    1920
    
    1080
    
    RGB
    
    BMP

Lưu ý: Khi mở từ dữ liệu DIB đã ghép thành BMP, Pillow thường nhận định dạng là BMP trước khi bạn lưu sang PNG/JPEG.

* * *

# 15\. Thiết kế ImageClipboard
    
    
    from PIL import Image
    import win32clipboard
    
    
    class ImageClipboard:
    
        @staticmethod
        def has_image():
    
            return (
                win32clipboard.IsClipboardFormatAvailable(
                    win32clipboard.CF_DIB
                )
            )
    
        @staticmethod
        def image():
    
            win32clipboard.OpenClipboard()
    
            try:
    
                dib = win32clipboard.GetClipboardData(
                    win32clipboard.CF_DIB
                )
    
            finally:
    
                win32clipboard.CloseClipboard()
    
            return dib_to_image(dib)

> **Lưu ý:** Trong thực tế, `has_image()` cũng nên tự mở/đóng Clipboard hoặc được gọi trong một context đã mở Clipboard. Phiên bản trên chỉ nhằm minh họa cấu trúc lớp.

* * *

# 16\. Lưu tự động
    
    
    img = ImageClipboard.image()
    
    img.save("capture.png")

* * *

# 17\. Ứng dụng thực tế

Ví dụ:
    
    
    Win + Shift + S
    
    ↓
    
    Clipboard
    
    ↓
    
    Python
    
    ↓
    
    PNG
    
    ↓
    
    OCR
    
    ↓
    
    AI
    
    ↓
    
    SQLite

Hoặc:
    
    
    Print Screen
    
    ↓
    
    Clipboard
    
    ↓
    
    Resize
    
    ↓
    
    Upload
    
    ↓
    
    Cloud

Hoặc:
    
    
    Clipboard
    
    ↓
    
    Image
    
    ↓
    
    Convert WebP
    
    ↓
    
    Compress
    
    ↓
    
    Save

Đây là nền tảng của rất nhiều công cụ chụp màn hình và tự động hóa.

* * *

# 18\. Kiến trúc
    
    
    clipboard/
    
    ├── text.py
    ├── files.py
    ├── images.py
    ├── manager.py
    ├── inspector.py
    ├── retry.py
    └── context.py

Trong đó:
    
    
    images.py
    
    ↓
    
    ImageClipboard
    
    ↓
    
    image()
    
    ↓
    
    save()
    
    ↓
    
    size()
    
    ↓
    
    mode()

Ở các buổi sau, chúng ta sẽ tiếp tục mở rộng lớp này để hỗ trợ nhiều định dạng ảnh hơn.

* * *

# Bài tập

## Bài 1

Viết:
    
    
    has_image()

Trả về:
    
    
    True
    
    False

* * *

## Bài 2

Viết:
    
    
    save_image(path)

Ví dụ:
    
    
    save_image("screen.png")

* * *

## Bài 3

Viết:
    
    
    print_image_info()

In:
    
    
    Width : 1920
    
    Height : 1080
    
    Mode : RGB

* * *

## Bài 4

Viết lớp:
    
    
    ImageClipboard

Có các phương thức:

  * `has_image()`
  * `image()`
  * `save(path)`
  * `size()`
  * `mode()`



* * *

## Bài 5 (Nâng cao)

Viết chương trình:
    
    
    Clipboard Image Inspector
    
    Có ảnh: Có
    
    Width : 1920
    
    Height : 1080
    
    Mode : RGB
    
    Save? (y/n)

Nếu chọn:
    
    
    y

↓
    
    
    clipboard.png

được tạo trong thư mục hiện tại.

* * *

# Những điểm cần lưu ý

Có một số chi tiết quan trọng mà nhiều tài liệu bỏ qua:

  * Không phải mọi ứng dụng đều đặt `CF_DIB` lên Clipboard; một số chỉ cung cấp `CF_BITMAP` hoặc các định dạng tùy chỉnh như PNG. 
  * Với `CF_BITMAP`, việc chuyển sang `PIL.Image` đòi hỏi sử dụng thêm các API GDI (`win32gui`, `win32ui`, `GetDIBits`, ...) để trích xuất pixel. Chúng ta chưa làm việc với phần này ở buổi học này. 
  * Trong các ứng dụng hiện đại, nên kiểm tra nhiều định dạng theo thứ tự ưu tiên (ví dụ PNG → DIB → BITMAP) để tăng khả năng tương thích. 



* * *

# Tổng kết

Trong buổi 5, bạn đã học:

  * Sự khác nhau giữa `CF_BITMAP` (DDB) và `CF_DIB` (DIB). 
  * Khái niệm **Handle (HBITMAP)** và lý do `CF_BITMAP` không trả về dữ liệu ảnh trực tiếp. 
  * Cấu trúc cơ bản của DIB và vì sao cần thêm `BITMAPFILEHEADER` để Pillow đọc được. 
  * Cách chuyển dữ liệu `CF_DIB` thành `PIL.Image` và lưu thành PNG/JPEG. 
  * Thiết kế nền tảng cho lớp `ImageClipboard`. 



Ở **Buổi 6** , chúng ta sẽ đi sâu hơn vào **GDI (Graphics Device Interface)** , cách chuyển đổi `HBITMAP` từ `CF_BITMAP` thành ảnh thực, sử dụng `win32gui`, `win32ui` và `GetDIBits()`. Đây là kỹ thuật mà nhiều ứng dụng Windows chuyên nghiệp sử dụng khi cần xử lý ảnh ở mức thấp.

