Version:0.9 StartHTML:0000000105 EndHTML:0000024281 StartFragment:0000000141 EndFragment:0000024245 

# Typing Deep Dive – Buổi 5

# Type Alias và `type` (Python 3.12)

> **Mục tiêu buổi học**
> 
> Sau buổi này bạn sẽ:
> 
>   * Hiểu Type Alias là gì.
>   * Phân biệt Type Alias với `NewType`.
>   * Thành thạo cú pháp `type` trong Python 3.12.
>   * Biết cách tổ chức file `types.py` trong dự án lớn.
>   * Xây dựng hệ thống kiểu (Type System) cho dự án crawler truyện.
> 


* * *

# 1\. Vấn đề khi không dùng Type Alias

Ví dụ
    
    
    def crawl(
        urls: list[dict[str, tuple[int, str | None]]]
    ):
        ...

Nhìn vào kiểu dữ liệu này bạn có hiểu ngay không?

Rất khó.

Trong dự án lớn sẽ có những kiểu còn dài hơn:
    
    
    dict[
        str,
        list[
            dict[
                str,
                tuple[
                    int,
                    float,
                    bool | None
                ]
            ]
        ]
    ]

Đọc cực kỳ khó.

* * *

# 2\. Type Alias là gì?

Type Alias đơn giản là:

> **Đặt tên cho một kiểu dữ liệu.**

Ví dụ

Không dùng Alias
    
    
    def save(
        data: dict[str, str]
    ):
        ...

Dùng Alias
    
    
    JsonObject = dict[str, str]
    
    def save(
        data: JsonObject
    ):
        ...

Dễ đọc hơn rất nhiều.

* * *

# 3\. Alias cơ bản

Ví dụ
    
    
    UserId = int
    
    BookId = int
    
    ChapterId = int

IDE hiểu
    
    
    UserId
    
    ↓
    
    int

Đây **chỉ là bí danh**.

Không tạo kiểu mới.

* * *

Ví dụ
    
    
    UserId = int
    
    user: UserId = 100

Hoàn toàn giống
    
    
    user: int = 100

* * *

# 4\. Alias cho Collection

Ví dụ
    
    
    BookList = list[str]

Sử dụng
    
    
    def print_books(
        books: BookList
    ):
        ...

Thay vì
    
    
    def print_books(
        books: list[str]
    ):
        ...

* * *

# 5\. Alias nhiều tầng

Ví dụ
    
    
    Book = dict[str, str]
    
    BookList = list[Book]

Khi đó
    
    
    def load_books() -> BookList:
        ...

Dễ hiểu hơn nhiều.

* * *

# 6\. Alias cho JSON

Đây là ví dụ rất phổ biến.
    
    
    JsonValue = (
        str
        | int
        | float
        | bool
        | None
    )

Sau đó
    
    
    JsonObject = dict[
        str,
        JsonValue
    ]

Hoặc
    
    
    JsonArray = list[
        JsonValue
    ]

* * *

Thực tế

JSON còn có thể lồng nhau.

Ta sẽ học Recursive Type ở buổi sau.

* * *

# 7\. Alias cho trạng thái

Ví dụ
    
    
    from typing import Literal
    
    Status = Literal[
        "pending",
        "running",
        "success",
        "failed",
    ]

Sau đó
    
    
    def update(
        status: Status
    ):
        ...

Đọc cực kỳ rõ.

* * *

# 8\. Alias cho URL

Ví dụ
    
    
    Url = str

Sau đó
    
    
    def download(
        url: Url
    ):
        ...

Rõ nghĩa hơn
    
    
    def download(
        url: str
    ):
        ...

* * *

# 9\. Alias trong dự án crawler

Ví dụ
    
    
    NovelId = int
    
    ChapterId = int
    
    SourceName = str
    
    Url = str

Sau đó
    
    
    def crawl(
        novel_id: NovelId,
        url: Url
    ):
        ...

Nhìn vào chữ ký hàm là hiểu ngay ý nghĩa.

* * *

# 10\. Python 3.12 - Cú pháp `type`

Python 3.12 giới thiệu cú pháp mới:
    
    
    type UserId = int

Thay cho
    
    
    UserId = int

* * *

Ví dụ
    
    
    type Url = str
    
    type Status = Literal[
        "running",
        "done"
    ]

Ưu điểm:

  * Rõ ràng hơn.
  * Trình kiểm tra kiểu biết chắc đây là alias.
  * Dễ đọc trong các dự án lớn.



* * *

# 11\. Alias lồng nhau
    
    
    type UserId = int
    
    type UserName = str
    
    type User = dict[
        UserName,
        UserId
    ]

* * *

# 12\. Alias Generic

Ví dụ
    
    
    type StringDict = dict[
        str,
        str
    ]

Sau này sẽ học
    
    
    type Cache[T] = dict[
        str,
        T
    ]

Đây là Generic Type Alias (Python 3.12), sẽ được giải thích kỹ ở các buổi về Generic.

* * *

# 13\. Alias KHÔNG tạo kiểu mới

Ví dụ
    
    
    UserId = int
    
    BookId = int

IDE coi
    
    
    UserId
    
    ↓
    
    int

và
    
    
    BookId
    
    ↓
    
    int

là giống nhau.

Ví dụ
    
    
    UserId = int
    
    BookId = int
    
    def get_user(
        user_id: UserId
    ):
        ...
    
    book: BookId = 10
    
    get_user(book)

Không lỗi.

Vì cả hai đều là `int`.

* * *

# 14\. Khi nào Alias là đủ?

Nếu chỉ muốn:

  * dễ đọc
  * dễ bảo trì
  * giảm lặp lại



→ Alias là đủ.

* * *

# 15\. Khi nào Alias không đủ?

Ví dụ
    
    
    UserId = int
    
    BookId = int

Bạn vô tình
    
    
    get_user(book_id)

IDE không phát hiện.

Vì cả hai đều là
    
    
    int

Nếu muốn
    
    
    UserId ≠ BookId

thì cần
    
    
    NewType

Chúng ta sẽ học chi tiết ở **Buổi 21**.

* * *

# 16\. Tổ chức Alias trong dự án

Một cấu trúc thường gặp:
    
    
    app/
    │
    ├── models/
    ├── services/
    ├── repository/
    ├── types.py
    └── main.py

Trong `types.py`
    
    
    from typing import Literal
    
    type Url = str
    type NovelId = int
    type ChapterId = int
    
    type Status = Literal[
        "pending",
        "running",
        "success",
        "failed"
    ]

Sau đó
    
    
    from app.types import Url

Sử dụng ở mọi nơi.

* * *

# 17\. Ví dụ thực tế (Crawler)
    
    
    type Url = str
    type Html = str
    
    def fetch(
        url: Url
    ) -> Html:
        ...

Parser
    
    
    type ChapterTitle = str
    
    type ChapterContent = str
    
    
    def parse(
        html: Html
    ) -> ChapterContent:
        ...

Đọc code rất rõ ràng.

* * *

# 18\. Best Practices

✔ Dùng Type Alias để đặt tên cho các kiểu phức tạp.

✔ Trong Python 3.12+, ưu tiên cú pháp `type`.

✔ Đặt các alias dùng chung vào một module (`types.py` hoặc `typing.py`). Lưu ý: nếu đặt tên file là `typing.py`, bạn có thể vô tình che khuất module chuẩn `typing`, vì vậy `types.py` thường là lựa chọn an toàn hơn.

✔ Dùng tên mang ý nghĩa nghiệp vụ (`NovelId`, `Url`, `Status`) thay vì chỉ phản ánh kiểu cơ sở (`int`, `str`).

❌ Không dùng Alias để cố tạo ra kiểu mới. Nếu cần phân biệt hai kiểu có cùng kiểu cơ sở (như `UserId` và `BookId`), hãy dùng `NewType`.

* * *

# Ví dụ áp dụng vào dự án crawler truyện
    
    
    from typing import Literal
    
    type Url = str
    type Html = str
    type NovelId = int
    type ChapterId = int
    
    type CrawlStatus = Literal[
        "pending",
        "running",
        "success",
        "failed",
    ]

Sau đó:
    
    
    def download(url: Url) -> Html:
        ...
    
    def save_chapter(
        novel_id: NovelId,
        chapter_id: ChapterId,
        html: Html,
    ) -> None:
        ...
    
    def update_status(status: CrawlStatus) -> None:
        ...

Ngay cả khi chưa đọc phần thân hàm, chữ ký của chúng đã mô tả rất rõ ý nghĩa của dữ liệu.

* * *

# Bài tập thực hành

## Bài 1

Tạo các Type Alias:
    
    
    UserId BookId ChapterId Url Html

với kiểu cơ sở phù hợp (`int` hoặc `str`).

* * *

## Bài 2

Định nghĩa:
    
    
    type Book = dict[str, str]
    type BookList = list[Book]

Viết hàm:
    
    
    def load_books() -> BookList:
        ...

Trả về danh sách gồm ít nhất 3 cuốn sách.

* * *

## Bài 3

Định nghĩa:
    
    
    from typing import Literal
    
    type CrawlStatus = Literal[
        "pending",
        "running",
        "success",
        "failed",
    ]

Viết hàm:
    
    
    def set_status(status: CrawlStatus) -> None:
        print(status)

Thử gọi với:

  * `"pending"` ✅
  * `"success"` ✅
  * `"error"` ❌ (IDE hoặc `mypy` nên cảnh báo).



* * *

## Tổng kết 5 buổi đầu

Sau 5 buổi, bạn đã nắm được nền tảng quan trọng của `typing`:

  * Hiểu vai trò của Type Hint trong Python.
  * Biết sử dụng các kiểu dựng sẵn (`list[int]`, `dict[str, int]`, `tuple`, `set`...).
  * Thành thạo `Union`, `Optional`, `Literal`.
  * Phân biệt rõ `Any`, `object`, `Never`, `NoReturn`.
  * Biết sử dụng Type Alias để xây dựng ngôn ngữ kiểu cho dự án.



Từ **Buổi 6** , chúng ta sẽ bước sang **Generic Programming** — phần cốt lõi và mạnh mẽ nhất của `typing`, nơi bạn sẽ học `TypeVar`, `Generic`, và cách xây dựng các cấu trúc dữ liệu cũng như API có thể tái sử dụng với nhiều kiểu dữ liệu khác nhau. Đây là nền tảng để viết các `Repository[T]`, `Service[T]` và hệ thống plugin tổng quát trong các dự án Python chuyên nghiệp.

