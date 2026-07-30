# Khóa học `win32clipboard` Deep Dive

# Buổi 6: DIB (Device Independent Bitmap) Deep Dive

> Đây là một trong những buổi quan trọng nhất của toàn bộ khóa học.

Nếu chỉ biết:
    
    
    dib = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)

thì mới chỉ biết **lấy dữ liệu**.

Sau buổi này bạn sẽ hiểu:

  * Windows lưu DIB như thế nào trong bộ nhớ 
  * Header của DIB 
  * Pixel được lưu ra sao 
  * Color Table 
  * Top-down vs Bottom-up Bitmap 
  * Bit Depth 
  * Compression 
  * Alpha Channel 
  * Vì sao có `CF_DIBV5`
  * Cách tự đọc Header bằng Python (không cần Pillow) 



Đây là kiến thức nền tảng nếu sau này bạn muốn:

  * Viết Image Viewer 
  * Viết Clipboard Manager 
  * Viết Screenshot Tool 
  * OCR 
  * AI Vision 
  * Editor giống Paint 



* * *

# Mục tiêu

Sau buổi học bạn sẽ đọc được cấu trúc của một DIB bằng Python.

* * *

# 1\. DIB là gì?

DIB

=

**Device Independent Bitmap**

Khác với
    
    
    CF_BITMAP

DIB **không phụ thuộc**

  * GPU 
  * Driver 
  * Device Context 



Do đó
    
    
    Windows Clipboard
    
    ↓
    
    CF_DIB
    
    ↓
    
    có thể lưu file
    
    ↓
    
    gửi mạng
    
    ↓
    
    OCR
    
    ↓
    
    AI

* * *

# 2\. Cấu trúc của DIB

Một DIB luôn gồm
    
    
    +----------------------+
    | BITMAPINFOHEADER     |
    +----------------------+
    | Color Table          |
    +----------------------+
    | Pixel Data           |
    +----------------------+

Trong đó

Header

↓

mô tả

Pixel

* * *

# 3\. Header

Header phổ biến nhất là
    
    
    BITMAPINFOHEADER

Có kích thước
    
    
    40 bytes

Đây là 40 byte đầu tiên của DIB.

* * *

# 4\. Layout
    
    
    Offset
    
    0   DWORD biSize
    
    4   LONG Width
    
    8   LONG Height
    
    12  WORD Planes
    
    14  WORD BitCount
    
    16  DWORD Compression
    
    20  DWORD ImageSize
    
    24  LONG XPelsPerMeter
    
    28  LONG YPelsPerMeter
    
    32  DWORD ClrUsed
    
    36  DWORD ClrImportant

40 byte.

* * *

# 5\. Đọc Header

Python
    
    
    import struct
    
    header = dib[:40]
    
    fields = struct.unpack("<IiiHHIIiiII", header)
    
    print(fields)

Ví dụ
    
    
    (
    40,
    1920,
    1080,
    1,
    32,
    0,
    8294400,
    3780,
    3780,
    0,
    0
    )

* * *

# 6\. Ý nghĩa từng trường

## biSize
    
    
    40

↓

Header dài

40 byte

* * *

## Width
    
    
    1920

↓

Chiều rộng

* * *

## Height
    
    
    1080

↓

Chiều cao

* * *

## Planes

Luôn
    
    
    1

Đây là trường lịch sử từ thời Windows rất cũ. Trong hầu hết trường hợp hiện đại, giá trị luôn bằng 1.

* * *

## BitCount

Ví dụ
    
    
    24

↓

24 bit

* * *

Hoặc
    
    
    32

↓

RGBA

* * *

## Compression
    
    
    0

↓

BI_RGB

Không nén.

* * *

# 7\. Tạo Dataclass

Thay vì
    
    
    fields[5]

Ta tạo model
    
    
    from dataclasses import dataclass
    
    
    @dataclass(slots=True)
    class BitmapInfoHeader:
    
        size: int
    
        width: int
    
        height: int
    
        planes: int
    
        bit_count: int
    
        compression: int
    
        image_size: int
    
        xppm: int
    
        yppm: int
    
        clr_used: int
    
        clr_important: int

* * *

# 8\. Hàm parse
    
    
    import struct
    
    
    def parse_header(dib: bytes) -> BitmapInfoHeader:
    
        values = struct.unpack(
            "<IiiHHIIiiII",
            dib[:40]
        )
    
        return BitmapInfoHeader(*values)

Sử dụng
    
    
    info = parse_header(dib)
    
    print(info.width)

* * *

# 9\. Bit Count

Đây là phần cực kỳ quan trọng.

Windows hỗ trợ
    
    
    1 bit
    
    4 bit
    
    8 bit
    
    16 bit
    
    24 bit
    
    32 bit

* * *

## 1 bit
    
    
    1 pixel
    
    ↓
    
    1 bit

Chỉ có
    
    
    đen
    
    trắng

* * *

## 8 bit
    
    
    1 pixel
    
    ↓
    
    1 byte

Dùng
    
    
    Color Table

* * *

## 24 bit
    
    
    R
    
    G
    
    B

Mỗi màu
    
    
    8 bit

↓
    
    
    24 bit

* * *

## 32 bit
    
    
    B
    
    G
    
    R
    
    A

Có thêm

Alpha

* * *

# 10\. Color Table

Nếu
    
    
    BitCount <= 8

Sau Header sẽ có
    
    
    Palette

Ví dụ
    
    
    Header
    
    ↓
    
    256 màu
    
    ↓
    
    Pixel

Đó là lý do ta không thể giả định rằng dữ liệu pixel bắt đầu ngay sau byte thứ 40.

* * *

# 11\. Pixel Data

Ví dụ

Ảnh
    
    
    R G
    
    B W

Windows lưu thành
    
    
    bytes

Không phải
    
    
    list

* * *

# 12\. Padding

Đây là kiến thức mà rất nhiều lập trình viên không biết.

Mỗi dòng pixel phải có độ dài là bội số của **4 byte**.

Ví dụ
    
    
    RGB
    
    RGB
    
    RGB

9 byte

↓

Windows thêm
    
    
    3 byte

↓

12 byte

* * *

Ví dụ
    
    
    Width
    
    ↓
    
    3 pixel
    
    ↓
    
    24 bit

↓
    
    
    9 bytes

↓
    
    
    12 bytes

Đây gọi là
    
    
    Row Padding

Công thức tính số byte của một hàng (stride):
    
    
    stride = ((width * bit_count + 31) // 32) * 4

Đây là công thức chuẩn của Windows.

* * *

# 13\. Bottom-Up Bitmap

Đây là điểm cực kỳ quan trọng.

Ví dụ

Ảnh
    
    
    A
    
    B
    
    C

Windows lưu
    
    
    C
    
    B
    
    A

Dòng cuối

↓

lưu trước.

Đây gọi là
    
    
    Bottom-Up

* * *

# 14\. Top-Down Bitmap

Nếu
    
    
    Height

âm

Ví dụ
    
    
    -1080

Windows hiểu
    
    
    Top Down

↓

Không đảo dòng.

Đây là lý do trường `height` trong header được khai báo là **signed integer (`LONG`)** chứ không phải số không dấu.

* * *

# 15\. Compression

Giá trị
    
    
    0

↓

BI_RGB

* * *
    
    
    1

↓

RLE8

* * *
    
    
    2

↓

RLE4

* * *
    
    
    3

↓

BITFIELDS

* * *
    
    
    6

↓

PNG

* * *
    
    
    5

↓

JPEG

> Trong `BITMAPINFOHEADER` cổ điển, các giá trị `BI_JPEG` (4) và `BI_PNG` (5) được định nghĩa. Một số tài liệu hoặc header mở rộng có thể khác nhau, vì vậy nên đối chiếu với tài liệu Win32 khi làm việc với các định dạng nén.

Trong thực tế Clipboard, phổ biến nhất vẫn là:
    
    
    BI_RGB

* * *

# 16\. CF_DIBV5

Tại sao có
    
    
    CF_DIBV5

?

Bởi vì
    
    
    BITMAPINFOHEADER

quá cũ.

Windows tạo
    
    
    BITMAPV5HEADER

Kích thước
    
    
    124 bytes

Thêm

  * Alpha 
  * Color Space 
  * ICC Profile 
  * Gamma 
  * Intent 



Rất nhiều ứng dụng hiện đại sử dụng `CF_DIBV5` để giữ nguyên thông tin màu sắc và kênh alpha.

* * *

# 17\. Viết Inspector
    
    
    info = parse_header(dib)
    
    print(info)

Kết quả
    
    
    BitmapInfoHeader(
        size=40,
        width=1920,
        height=1080,
        planes=1,
        bit_count=32,
        compression=0,
        image_size=8294400,
        xppm=3780,
        yppm=3780,
        clr_used=0,
        clr_important=0
    )

* * *

# 18\. Kiến trúc chuyên nghiệp
    
    
    clipboard/
    
    images/
    
    ├── dib.py
    ├── dibv5.py
    ├── bitmap.py
    ├── parser.py
    ├── image.py
    ├── header.py
    └── constants.py

Ví dụ:
    
    
    header.py
    
    
    BitmapInfoHeader
    
    
    parser.py
    
    
    parse_header()
    
    parse_palette()
    
    parse_pixels()

Việc tách các thành phần như vậy sẽ giúp dễ mở rộng sang `CF_DIBV5` và các định dạng khác.

* * *

# Bài tập

## Bài 1

Viết
    
    
    parse_header(dib)

* * *

## Bài 2

Viết
    
    
    print_header(dib)

In
    
    
    Width
    
    Height
    
    BitCount
    
    Compression

* * *

## Bài 3

Viết dataclass
    
    
    BitmapInfoHeader

* * *

## Bài 4

Viết
    
    
    ImageInspector

Cho kết quả
    
    
    Width : 1920
    
    Height : 1080
    
    BitCount : 32
    
    Compression : BI_RGB

* * *

## Bài 5 (Nâng cao)

Viết chương trình đọc trực tiếp **40 byte đầu tiên** của `CF_DIB`, phân tích từng trường bằng `struct.unpack()` rồi hiển thị dưới dạng bảng:

Trường| Giá trị| Ý nghĩa  
---|---|---  
Size| 40| Kích thước header  
Width| 1920| Chiều rộng ảnh  
Height| 1080| Chiều cao ảnh (dương = Bottom-Up, âm = Top-Down)  
BitCount| 32| 32-bit BGRA  
Compression| 0| BI_RGB  
  
* * *

# Tổng kết

Trong buổi này, bạn đã hiểu sâu về:

  * Cấu trúc của **Device Independent Bitmap (DIB)**. 
  * `BITMAPINFOHEADER` và ý nghĩa của từng trường. 
  * `BitCount`, `Color Table`, `Padding`, `Bottom-Up` và `Top-Down Bitmap`. 
  * Cách dùng `struct.unpack()` và `dataclass` để tự phân tích dữ liệu DIB mà không phụ thuộc vào Pillow. 
  * Sự khác biệt giữa `CF_DIB` và `CF_DIBV5`. 



## Buổi tiếp theo

Ở **Buổi 7** , chúng ta sẽ đi vào **thực sự giải mã dữ liệu pixel** :

  * Tự đọc từng pixel từ `CF_DIB`. 
  * Chuyển `bytes` thành ma trận ảnh (`list[list[Pixel]]` hoặc `numpy.ndarray`). 
  * Hiểu thứ tự **BGR/BGRA** của Windows. 
  * Tự viết một **DIB Decoder** bằng Python, không sử dụng Pillow để giải mã pixel. Đây là bước nền tảng trước khi xây dựng các công cụ xử lý ảnh chuyên nghiệp.

