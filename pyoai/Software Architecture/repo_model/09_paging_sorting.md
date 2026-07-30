# Khóa học: Thiết kế Model & Repository cho App Cào Truyện

# Buổi 9 - Pagination, Sorting & Filtering Deep Dive

> Sau Buổi 8 chúng ta đã có **Specification Pattern** để biểu diễn điều kiện truy vấn. Hôm nay chúng ta sẽ giải quyết một vấn đề thực tế hơn: **không bao giờ lấy toàn bộ dữ liệu từ database**.

Nếu app của bạn có:

  * 200.000 truyện 
  * 12.000.000 chapter 



thì câu lệnh:
    
    
    SELECT * FROM story;

là một "thảm họa".

Buổi hôm nay sẽ giúp bạn thiết kế Repository có khả năng **phân trang, sắp xếp và lọc dữ liệu** giống các framework lớn như Django ORM, SQLAlchemy, Entity Framework.

* * *

# Mục tiêu buổi học

Sau buổi này bạn sẽ hiểu

  * Pagination 
  * Offset Pagination 
  * Cursor Pagination 
  * Sorting 
  * Multi-column Sorting 
  * Filter Object 
  * Query Options 
  * Page Object 
  * Repository Query API 
  * Performance 



* * *

# 1\. Vấn đề

Giả sử bảng
    
    
    story

có
    
    
    350.000 record

Nếu GUI mở lên
    
    
    SELECT *
    FROM story;

SQLite sẽ:

↓

Đọc toàn bộ

↓

Mapper

↓

350.000 Story object

↓

GUI

Tốn:

  * RAM 
  * CPU 
  * Thời gian 



Đây là thiết kế không thể mở rộng.

* * *

# 2\. Pagination

Thay vì
    
    
    350.000 Story

Ta lấy
    
    
    20 Story

mỗi lần.

Ví dụ
    
    
    Trang 1
    
    1-20
    
    ----------------
    
    Trang 2
    
    21-40
    
    ----------------
    
    Trang 3
    
    41-60

Đây gọi là

> Pagination.

* * *

# 3\. Offset Pagination

SQLite
    
    
    SELECT *
    FROM story
    LIMIT 20
    OFFSET 40;

Nghĩa là
    
    
    Bỏ qua
    
    40 record
    
    ↓
    
    Lấy
    
    20 record

Đây là cách phổ biến nhất.

* * *

# 4\. Repository API

Không nên
    
    
    list()

Nên
    
    
    find(
        specification,
        pagination
    )

Hoặc
    
    
    search(
        query_options
    )

Repository chỉ có một API thống nhất.

* * *

# 5\. Page Object

Không nên trả về
    
    
    list[Story]

Vì GUI còn cần

  * tổng số trang 
  * tổng số record 
  * trang hiện tại 



Ta tạo
    
    
    @dataclass(slots=True)
    class Page(Generic[T]):
    
        items: list[T]
    
        page: int
    
        page_size: int
    
        total_items: int

* * *

# 6\. Tính tổng số trang
    
    
    @property
    def total_pages(self):
    
        return math.ceil(
    
            self.total_items /
    
            self.page_size
        )

Ví dụ
    
    
    205 record
    
    page size
    
    20

↓

11 trang.

* * *

# 7\. QueryOptions

Đừng truyền
    
    
    page
    
    page_size
    
    sort
    
    ascending
    
    specification

thành 5 tham số.

Hãy gom lại.
    
    
    @dataclass(slots=True)
    class QueryOptions:
    
        page: int = 1
    
        page_size: int = 20
    
        sort: str = "title"
    
        ascending: bool = True
    
        specification = None

Đây là một đối tượng cấu hình truy vấn.

* * *

# 8\. Repository

API trở nên rất đẹp.
    
    
    stories = repository.find(
        options
    )

Thay vì
    
    
    find(
    
        page,
    
        page_size,
    
        sort,
    
        asc,
    
        status,
    
        genre,
    
        source,
    
        ...
    )

* * *

# 9\. Sorting

Ví dụ
    
    
    A
    
    ↓
    
    Z

SQLite
    
    
    ORDER BY title ASC

Ngược lại
    
    
    ORDER BY title DESC

* * *

# 10\. Multi-column Sorting

Ví dụ
    
    
    Status
    
    ↓
    
    Updated_at
    
    ↓
    
    Title

SQLite
    
    
    ORDER BY
    
    status,
    
    updated_at DESC,
    
    title

Đây là điều mà sau này app crawler sẽ dùng rất nhiều.

* * *

# 11\. Sort Object

Không dùng
    
    
    sort="title"

Tạo
    
    
    @dataclass(frozen=True)
    class Sort:
    
        field: str
    
        ascending: bool = True

Sau đó
    
    
    QueryOptions(
    
        sort=[
    
            Sort("status"),
    
            Sort("updated_at", False)
    
        ]
    )

Dễ mở rộng hơn rất nhiều.

* * *

# 12\. Filtering

Đã có Specification.

Ví dụ
    
    
    StoryStatusSpecification(
        StoryStatus.ONGOING
    )

↓

Repository

↓

WHERE status='ongoing'

Kết hợp với Pagination sẽ tạo nên một API rất mạnh.

* * *

# 13\. Ví dụ hoàn chỉnh
    
    
    options = QueryOptions(
    
        page=2,
    
        page_size=30,
    
        specification=StoryStatusSpecification(
    
            StoryStatus.ONGOING
    
        ),
    
        sort=[
    
            Sort(
    
                "updated_at",
    
                False
    
            )
        ]
    )

Repository

↓

Page

↓

GUI

* * *

# 14\. Cursor Pagination

Offset có nhược điểm.

Ví dụ
    
    
    10 triệu record

SQLite vẫn phải:
    
    
    Bỏ qua
    
    9.999.980 record

rồi mới lấy 20 record.

Đây là lý do nhiều hệ thống lớn dùng Cursor Pagination.

* * *

# 15\. Cursor

Ví dụ
    
    
    last_id
    
    =
    
    1000

Lần sau
    
    
    SELECT *
    
    FROM story
    
    WHERE id>1000
    
    LIMIT 20

Nhanh hơn rất nhiều.

* * *

# 16\. Cursor Object
    
    
    @dataclass
    
    class Cursor:
    
        value:int

Repository
    
    
    find_after(cursor)

Không cần OFFSET.

* * *

# 17\. Offset hay Cursor?

Offset

Ưu điểm

  * đơn giản 
  * dễ phân trang 



Nhược điểm

  * chậm khi dữ liệu lớn 



Cursor

Ưu điểm

  * rất nhanh 
  * phù hợp crawler 



Nhược điểm

  * khó nhảy tới trang bất kỳ 



Trong app cào truyện:

  * GUI quản trị: Offset phù hợp. 
  * Tiến trình crawler, đồng bộ dữ liệu: Cursor thường hiệu quả hơn. 



* * *

# 18\. SearchOptions hoàn chỉnh
    
    
    @dataclass(slots=True)
    class QueryOptions:
    
        specification: Specification | None
    
        page: int
    
        page_size: int
    
        sort: list[Sort]

Nếu sau này cần Cursor, có thể mở rộng bằng cách thêm thuộc tính mới hoặc tạo `CursorQueryOptions` riêng thay vì nhồi tất cả vào một lớp.

* * *

# 19\. Repository API cuối cùng
    
    
    page = repository.find(
        options
    )

Trả về
    
    
    Page
    
    ↓
    
    items
    
    ↓
    
    Story

GUI không cần biết SQL.

* * *

# 20\. Count

GUI cần
    
    
    350.000 Story

Không nên
    
    
    SELECT *

rồi
    
    
    len(...)

Nên
    
    
    SELECT COUNT(*)

Repository sẽ chạy hai truy vấn:
    
    
    COUNT(*)
    
    +
    
    LIMIT/OFFSET

Đây là cách phổ biến để hiển thị tổng số bản ghi và dữ liệu của trang hiện tại.

* * *

# 21\. Performance

Nên tạo Index
    
    
    status
    
    updated_at
    
    title
    
    source_id

Nếu thường dùng
    
    
    ORDER BY updated_at

thì
    
    
    INDEX(updated_at)

rất quan trọng.

Nếu truy vấn thường xuyên theo:
    
    
    WHERE status='ongoing'
    
    ORDER BY updated_at DESC

thì nên cân nhắc **composite index** :
    
    
    (status, updated_at DESC)

thay vì hai index riêng lẻ.

* * *

# 22\. Cấu trúc Domain
    
    
    domain/
    
    query/
    
        page.py
    
        query_options.py
    
        sort.py
    
        cursor.py
    
    specifications/
    
    repositories/

Việc tách các đối tượng truy vấn khỏi Repository giúp mã nguồn rõ ràng và tái sử dụng tốt hơn.

* * *

# 23\. Luồng hoạt động
    
    
    GUI
     │
     ▼
    QueryOptions
     │
     ▼
    StoryService
     │
     ▼
    StoryRepository
     │
     ▼
    Specification Translator
     │
     ▼
    SQLite
     │
     ▼
    Page<Story>
     │
     ▼
    GUI

Repository vẫn chỉ là cầu nối giữa Domain và tầng lưu trữ.

* * *

# 24\. Thiết kế cuối khóa

Sau 9 buổi, tầng Repository của chúng ta đã có:
    
    
    Repository
    
    ↓
    
    Specification
    
    ↓
    
    Mapper
    
    ↓
    
    UnitOfWork
    
    ↓
    
    Pagination
    
    ↓
    
    Sorting
    
    ↓
    
    Filtering

Đây là nền tảng rất mạnh, đủ để xây dựng ứng dụng crawler có quy mô lớn mà không cần thay đổi kiến trúc khi dữ liệu tăng lên.

* * *

# Sai lầm phổ biến

❌ `SELECT *` rồi phân trang bằng Python

❌ Repository trả về toàn bộ danh sách

❌ `ORDER BY` trên cột không có index

❌ Truyền 8–10 tham số vào `find()`

❌ Trộn logic phân trang vào GUI

* * *

# Bài tập

## Bài 1

Thiết kế các lớp:

  * `Page[T]`
  * `Sort`
  * `QueryOptions`



sử dụng `dataclass` và `Generic`.

* * *

## Bài 2

Nâng cấp `MemoryStoryRepository.find(options)` để hỗ trợ:

  * `Specification`
  * `Sorting`
  * `Pagination`



Mọi xử lý đều thực hiện trên bộ nhớ.

* * *

## Bài 3

Nâng cấp `SQLiteStoryRepository.find(options)`:

  * sinh `WHERE` từ `Specification`
  * sinh `ORDER BY` từ `Sort`
  * sinh `LIMIT/OFFSET` từ `QueryOptions`
  * trả về `Page[Story]`



* * *

## Bài 4 (nâng cao)

Thiết kế hai API riêng:

  * `OffsetQueryOptions`
  * `CursorQueryOptions`



và phân tích:

  * trường hợp nào nên dùng Offset 
  * trường hợp nào nên dùng Cursor 
  * cách kết hợp với tiến trình crawler để quét hàng triệu truyện mà vẫn đạt hiệu năng cao. 



* * *

# Chuẩn bị cho Buổi 10

Ở **Buổi 10** , chúng ta sẽ học **Bulk Operations & Batch Processing** – một chủ đề cực kỳ quan trọng đối với app cào truyện.

Thay vì:
    
    
    for chapter in chapters:
        repository.save(chapter)

chúng ta sẽ thiết kế các API như:

  * `bulk_insert()`
  * `bulk_update()`
  * `bulk_upsert()`
  * `bulk_delete()`



kết hợp với `UnitOfWork` để nhập hàng nghìn chương truyện chỉ với vài câu lệnh SQL, giảm đáng kể thời gian crawl và tải cho cơ sở dữ liệu.

