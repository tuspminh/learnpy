# Khóa học `win32clipboard` Deep Dive

# Buổi 10: Custom Clipboard Format Deep Dive

> Đây là buổi học quan trọng nhất nếu bạn muốn xây dựng **ứng dụng Windows chuyên nghiệp**.

Cho đến nay chúng ta đã làm việc với:

  * `CF_UNICODETEXT`
  * `CF_HDROP`
  * `CF_DIB`
  * `HTML Format`
  * `Rich Text Format`



Đó đều là các định dạng đã có sẵn hoặc được cộng đồng thống nhất.

Hôm nay chúng ta sẽ học cách **tự tạo định dạng Clipboard của riêng ứng dụng**.

Đây là kỹ thuật được sử dụng bởi:

  * Photoshop 
  * Visual Studio 
  * Office 
  * AutoCAD 
  * Blender 
  * Notion 
  * Figma 
  * Chrome 
  * Edge 



* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Custom Clipboard Format 
  * RegisterClipboardFormat() 
  * Format ID 
  * Clipboard Protocol 
  * Serialization 
  * Versioning 
  * Binary Data 
  * JSON Data 
  * Trao đổi dữ liệu giữa hai chương trình Python 



* * *

# 1\. Tại sao cần Custom Format?

Giả sử bạn viết ứng dụng:
    
    
    StoryCrawler

Người dùng copy một truyện:
    
    
    Thần Đạo Đan Tôn

Nếu dùng:
    
    
    CF_UNICODETEXT

thì chỉ copy được:
    
    
    Thần Đạo Đan Tôn

Nhưng bạn còn muốn lưu:

  * ID truyện 
  * URL 
  * Tác giả 
  * Nguồn 
  * Chương hiện tại 
  * Thumbnail 
  * Tags 



→ Plain Text không đủ.

* * *

# 2\. Ý tưởng

Clipboard có thể chứa:
    
    
    Clipboard
    
    ├── CF_UNICODETEXT
    ├── HTML Format
    ├── StoryCrawler/Novel

Trong đó:
    
    
    StoryCrawler/Novel

là định dạng do **chính bạn định nghĩa**.

* * *

# 3\. RegisterClipboardFormat()
    
    
    import win32clipboard
    
    FORMAT = win32clipboard.RegisterClipboardFormat(
        "StoryCrawler/Novel"
    )
    
    print(FORMAT)

Ví dụ:
    
    
    49482

Mỗi máy có thể khác nhau.

Điều quan trọng:

Tên giống nhau

↓

ID giống nhau

trong cùng một phiên Windows.

* * *

# 4\. Windows làm gì?

Windows lưu:
    
    
    "StoryCrawler/Novel"
    
    ↓
    
    49482

Sau này:
    
    
    RegisterClipboardFormat(
        "StoryCrawler/Novel"
    )

↓

luôn trả
    
    
    49482

đến khi Windows khởi động lại.

* * *

# 5\. Dữ liệu gì có thể lưu?

Bất kỳ dữ liệu nhị phân nào.

Ví dụ:
    
    
    JSON

* * *
    
    
    XML

* * *
    
    
    Protocol Buffer

* * *
    
    
    Pickle

* * *
    
    
    msgpack

* * *
    
    
    CBOR

* * *
    
    
    Avro

* * *
    
    
    FlatBuffer

* * *

# 6\. Khuyến nghị

Trong Python,

nên dùng:
    
    
    JSON

vì:

  * dễ debug 
  * đa ngôn ngữ 
  * dễ mở rộng 
  * không phụ thuộc Python 



Không nên dùng `pickle` để trao đổi dữ liệu với ứng dụng không tin cậy vì có thể dẫn đến thực thi mã khi giải tuần tự hóa.

* * *

# 7\. Ví dụ JSON
    
    
    import json
    
    novel = {
    
        "id": 12,
    
        "title": "Thần Đạo",
    
        "author": "ABC",
    
        "chapters": 1823
    }
    
    data = json.dumps(
        novel,
        ensure_ascii=False
    )

↓
    
    
    {"id":12,...}

* * *

# 8\. Ghi Clipboard
    
    
    import win32clipboard
    import json
    
    FORMAT = win32clipboard.RegisterClipboardFormat(
        "StoryCrawler/Novel"
    )
    
    data = json.dumps(
        {
            "title": "Thần Đạo"
        },
        ensure_ascii=False
    )
    
    win32clipboard.OpenClipboard()
    
    try:
    
        win32clipboard.EmptyClipboard()
    
        win32clipboard.SetClipboardData(
            FORMAT,
            data
        )
    
    finally:
    
        win32clipboard.CloseClipboard()

> Lưu ý: Với một số custom format, pywin32 có thể yêu cầu dữ liệu ở dạng `bytes` thay vì `str`, tùy theo định dạng và API bên dưới. Một lựa chọn an toàn là `json.dumps(...).encode("utf-8")`.

* * *

# 9\. Đọc Clipboard
    
    
    win32clipboard.OpenClipboard()
    
    try:
    
        data = win32clipboard.GetClipboardData(
            FORMAT
        )
    
    finally:
    
        win32clipboard.CloseClipboard()
    
    print(data)

↓
    
    
    {"title":"Thần Đạo"}

* * *

# 10\. Deserialize
    
    
    obj = json.loads(data)
    
    print(obj["title"])

↓
    
    
    Thần Đạo

* * *

# 11\. Versioning

Đây là điều cực kỳ quan trọng.

Đừng lưu:
    
    
    {
    "title":"..."
    }

Hãy lưu:
    
    
    {
    "version":1,
    
    "type":"novel",
    
    "payload":{
    ...
    }
    }

↓

Sau này

Version 2

↓

không phá ứng dụng cũ.

* * *

# 12\. Protocol

Ví dụ
    
    
    {
    "type":"novel",
    
    "version":1,
    
    "payload":{
    
    "id":15,
    
    "title":"ABC",
    
    "source":"TruyenFull"
    
    }
    }

↓

Clipboard Protocol

Đây là cách nhiều phần mềm định nghĩa giao thức trao đổi dữ liệu.

* * *

# 13\. Thiết kế Model
    
    
    from dataclasses import dataclass
    
    
    @dataclass(slots=True)
    class NovelClipboard:
    
        id: int
    
        title: str
    
        author: str
    
        source: str

* * *

# 14\. Serialize
    
    
    import json
    from dataclasses import asdict
    
    novel = NovelClipboard(
        1,
        "ABC",
        "Nguyễn Văn A",
        "TruyenFull"
    )
    
    data = json.dumps(
        asdict(novel),
        ensure_ascii=False
    )

* * *

# 15\. Deserialize
    
    
    obj = json.loads(data)
    
    novel = NovelClipboard(
        **obj
    )

* * *

# 16\. Clipboard Manager
    
    
    class StoryClipboard:
    
        FORMAT = win32clipboard.RegisterClipboardFormat(
            "StoryCrawler/Novel"
        )
    
        @classmethod
        def copy(cls, novel):
    
            ...
    
        @classmethod
        def paste(cls):
    
            ...

Sau này bạn có thể mở rộng:

  * `copy_bookmark()`
  * `copy_chapter()`
  * `copy_author()`



mỗi loại dùng một định dạng riêng hoặc một trường `type`.

* * *

# 17\. Binary Data

Không nhất thiết phải dùng JSON.

Ví dụ
    
    
    bytes

↓
    
    
    b"\x01\x04..."

↓

Clipboard

↓

App khác

↓

bytes

Đây là cách nhiều phần mềm đồ họa trao đổi dữ liệu lớn.

* * *

# 18\. Hai chương trình

App A

↓

Copy

↓

Clipboard

↓

StoryCrawler/Novel

↓

App B

↓

Paste

↓

Đọc đầy đủ:

  * id 
  * title 
  * author 
  * tags 



Không mất dữ liệu.

* * *

# 19\. Kết hợp nhiều Format

Đây là kỹ thuật chuyên nghiệp.

Một lần Copy

↓

Clipboard
    
    
    CF_UNICODETEXT
    
    ↓
    
    "Thần Đạo"
    
    HTML Format
    
    ↓
    
    <b>Thần Đạo</b>
    
    StoryCrawler/Novel
    
    ↓
    
    JSON

Nếu

Paste vào

Notepad

↓

Plain Text

Nếu

Paste vào

StoryCrawler

↓

JSON

↓

Đầy đủ dữ liệu.

Đây chính là cách Microsoft Office và nhiều ứng dụng khác hoạt động: cùng một thao tác Copy nhưng cung cấp nhiều định dạng để ứng dụng đích tự chọn.

* * *

# 20\. Kiến trúc
    
    
    clipboard/
    
    custom/
    
    ├── protocol.py
    ├── registry.py
    ├── serializer.py
    ├── deserializer.py
    ├── manager.py
    ├── models.py
    └── constants.py

* * *

# 21\. Registry

Ví dụ
    
    
    FORMATS = {
    
    "novel":
    
    RegisterClipboardFormat(
    "StoryCrawler/Novel"
    ),
    
    "chapter":
    
    RegisterClipboardFormat(
    "StoryCrawler/Chapter"
    ),
    
    "bookmark":
    
    RegisterClipboardFormat(
    "StoryCrawler/Bookmark"
    )
    
    }

↓

Quản lý tập trung.

* * *

# 22\. Serializer
    
    
    serialize(obj)
    
    ↓
    
    JSON
    
    ↓
    
    Clipboard

* * *

# 23\. Deserializer
    
    
    Clipboard
    
    ↓
    
    JSON
    
    ↓
    
    Model

* * *

# 24\. Dự án thực tế

Đối với dự án **story_crawler** mà chúng ta đang xây dựng, bạn có thể thiết kế:
    
    
    StoryCrawler/Novel
    
    StoryCrawler/Chapter
    
    StoryCrawler/Author
    
    StoryCrawler/Bookmark
    
    StoryCrawler/Image

Ví dụ:

Người dùng:
    
    
    Ctrl+C

một truyện.

↓

Clipboard

↓
    
    
    Plain Text
    
    ↓
    
    Tên truyện
    
    HTML
    
    ↓
    
    Có Link
    
    Custom
    
    ↓
    
    JSON đầy đủ

↓

Người dùng

Ctrl+V

↓

Ứng dụng tự khôi phục toàn bộ metadata.

* * *

# Bài tập

## Bài 1

Đăng ký:
    
    
    StoryCrawler/Novel

* * *

## Bài 2

Viết
    
    
    copy_novel(
        novel
    )

* * *

## Bài 3

Viết
    
    
    paste_novel()

* * *

## Bài 4

Tạo
    
    
    NovelClipboard

dùng `@dataclass`.

* * *

## Bài 5

Viết:
    
    
    ClipboardProtocol

Có:

  * version 
  * type 
  * payload 



Ví dụ:
    
    
    {
      "version": 1,
      "type": "novel",
      "payload": {
        "id": 1,
        "title": "Thần Đạo Đan Tôn",
        "author": "Cô Đơn Địa Phi",
        "source": "TruyenFull"
      }
    }

* * *

# Mini Project

Viết chương trình:
    
    
    Story Clipboard Demo
    
    ====================
    
    Copy Novel
    
    ↓
    
    Clipboard
    
    ↓
    
    Paste Novel
    
    ↓
    
    ID : 1
    
    Title : Thần Đạo Đan Tôn
    
    Author : ...
    
    Source : ...

* * *

# Tổng kết

Trong buổi 10, bạn đã học:

  * Cơ chế hoạt động của **Custom Clipboard Format**. 
  * Cách đăng ký định dạng riêng bằng `RegisterClipboardFormat()`. 
  * Thiết kế giao thức trao đổi dữ liệu (protocol) với **version** và **payload**. 
  * Tuần tự hóa (serialization) và giải tuần tự hóa (deserialization) bằng JSON. 
  * Chiến lược cung cấp **nhiều định dạng cùng lúc** (Plain Text + HTML + Custom Format) để ứng dụng của bạn vừa tương thích với mọi chương trình, vừa giữ được đầy đủ metadata. 



* * *

# Lộ trình tiếp theo

Đến đây chúng ta đã hoàn thành phần **Clipboard Data Formats** :

  * ✅ CF_UNICODETEXT 
  * ✅ CF_HDROP 
  * ✅ CF_DIB / CF_DIBV5 
  * ✅ HTML Format 
  * ✅ Rich Text Format 
  * ✅ CSV 
  * ✅ Custom Clipboard Format 



Từ **Buổi 11** , chúng ta sẽ chuyển sang phần nâng cao hơn:

> **Clipboard Monitoring & Windows Messages**

Đây là nơi bạn sẽ học cách:

  * Theo dõi Clipboard theo thời gian thực. 
  * Nhận thông báo mỗi khi người dùng **Ctrl+C**. 
  * Xây dựng **Clipboard History** giống Windows 11 (`Win + V`). 
  * Tạo Clipboard Manager chạy nền, tự lưu lịch sử, tìm kiếm và đồng bộ dữ liệu. Đây là những kỹ thuật cốt lõi trong các công cụ như Ditto, ClipClip hay PowerToys Clipboard.

