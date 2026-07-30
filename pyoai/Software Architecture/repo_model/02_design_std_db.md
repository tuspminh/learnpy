# Khóa học: Thiết kế Model & Repository cho App Cào Truyện

# Buổi 2 - Thiết kế Database chuẩn cho hệ thống crawler truyện

Ở buổi trước chúng ta đã xác định **Domain Model** :
    
    
    Source
    Story
    Chapter
    Author
    Genre
    Bookmark
    History
    CrawlJob
    ...

Hôm nay chúng ta sẽ chuyển những Entity đó thành một **Database Design** đúng chuẩn.

Mục tiêu buổi này không chỉ là "đủ dùng", mà là thiết kế để:

  * chạy được với SQLite 
  * sau này chuyển sang PostgreSQL gần như không phải sửa model 
  * hỗ trợ nhiều website 
  * hỗ trợ nhiều crawler chạy đồng thời 
  * hỗ trợ hàng triệu chapter 
  * hỗ trợ plugin 



* * *

# Mục tiêu cuối buổi

Sau buổi này bạn sẽ biết:

✅ Phân tích dữ liệu

✅ Thiết kế ERD

✅ Chuẩn hóa dữ liệu

✅ PK

✅ FK

✅ UNIQUE

✅ INDEX

✅ Composite Key

✅ Junction Table

✅ Soft Delete

✅ Timestamp

✅ Versioning

* * *

# 1\. Phân tích nghiệp vụ

Giả sử app của chúng ta hỗ trợ
    
    
    TruyenFull
    
    TangThuVien
    
    NovelBin
    
    WikiDich
    
    RoyalRoad
    
    Sangtacviet

Mỗi website có
    
    
    Nhiều truyện
    
    ↓
    
    Mỗi truyện
    
    ↓
    
    Nhiều chương
    
    ↓
    
    Nhiều thể loại
    
    ↓
    
    Nhiều tác giả

Ngoài ra còn có
    
    
    Bookmark
    
    Reading History
    
    Favorite
    
    Download
    
    Image
    
    Crawler Log
    
    Task Queue

* * *

# 2\. Các bảng chính

Tôi thường chia thành 5 nhóm.
    
    
    Metadata
    
    Crawler
    
    Reading
    
    System
    
    Cache

* * *

## Metadata
    
    
    source
    
    story
    
    chapter
    
    author
    
    genre
    
    tag
    
    publisher

* * *

## Mapping
    
    
    story_author
    
    story_genre
    
    story_tag

* * *

## Reading
    
    
    bookmark
    
    reading_history
    
    download

* * *

## Crawler
    
    
    crawl_job
    
    crawl_log
    
    crawl_queue
    
    crawl_error

* * *

## System
    
    
    setting
    
    image
    
    attachment
    
    cache

* * *

# Tổng sơ đồ
    
    
    Source
        │
        │1
        │
        │N
     Story
       │
       ├────────────┐
       │            │
    Chapter     StoryGenre
                     │
                  Genre
    
    Story
       │
    StoryAuthor
       │
    Author
    
    Story
       │
    Bookmark
    
    Story
       │
    History
    
    Story
       │
    Image
    
    Story
       │
    Download

Đây là sơ đồ tối thiểu. Sau này chúng ta sẽ mở rộng thêm như `Translator`, `Comment`, `Rating`, `Volume`, `AlternativeTitle`...

* * *

# 3\. Thiết kế bảng Source
    
    
    source

Field| Kiểu  
---|---  
id| INTEGER PK  
name| TEXT  
domain| TEXT  
enabled| BOOLEAN  
created_at| DATETIME  
  
Ví dụ

id| name  
---|---  
1| TruyenFull  
2| NovelBin  
3| TangThuVien  
  
Tại sao cần bảng Source?

Không nên hard-code:
    
    
    if site == "truyenfull":

Thay vào đó:
    
    
    Story
    
    ↓
    
    source_id
    
    ↓
    
    Source

Sau này chỉ cần thêm plugin.

* * *

# 4\. Thiết kế Story
    
    
    story

Field| Ý nghĩa  
---|---  
id| PK  
source_id| FK  
title| Tên  
slug| Slug  
url| URL gốc  
summary| Giới thiệu  
status| ongoing/completed  
cover| Ảnh  
chapter_count| Số chương  
last_chapter| Tên chương cuối  
last_update| Website update  
created_at|   
updated_at|   
  
Quan hệ
    
    
    Story
    
    ↓
    
    belongs to
    
    ↓
    
    Source

* * *

# Tại sao lưu URL?

Ví dụ
    
    
    https://truyenfull.vn/dau-la-dai-luc/

Crawler cần quay lại URL này để:

  * cập nhật chương 
  * lấy ảnh 
  * lấy metadata 



* * *

# 5\. Thiết kế Chapter

Đây là bảng lớn nhất.
    
    
    chapter

Field  
---  
id  
story_id  
index  
title  
url  
content  
word_count  
created_at  
updated_at  
  
Quan hệ
    
    
    Story
    
    ↓
    
    Chapter

Một Story

↓

1000 chapter

↓

1 triệu dòng cũng bình thường.

Do đó phải tối ưu ngay từ đầu.

* * *

# Index rất quan trọng

Sai:
    
    
    SELECT *
    
    FROM chapter
    
    WHERE story_id=10;

Không có Index.

SQLite sẽ đọc toàn bộ bảng.

Nếu bảng có
    
    
    5 triệu chapter

Sẽ rất chậm.

Phải tạo
    
    
    INDEX(story_id)

Thậm chí
    
    
    INDEX(story_id,index)

để lấy chương theo thứ tự.

* * *

# 6\. Author
    
    
    author

Field  
---  
id  
name  
  
Rất đơn giản.

* * *

# Sai lầm phổ biến

Nhiều người làm
    
    
    story
    
    author_name

Sai.

Vì
    
    
    Nguyễn Nhật Ánh

Có
    
    
    100 truyện

Nếu đổi tên
    
    
    100 record phải update.

Chuẩn hơn
    
    
    author
    
    ↓
    
    story_author
    
    ↓
    
    story

* * *

# 7\. StoryAuthor
    
    
    story_author

story_id  
---  
author_id  
  
Đây gọi là
    
    
    Junction Table

Quan hệ
    
    
    Story
    
    N
    
    ↓
    
    StoryAuthor
    
    ↑
    
    N
    
    Author

Nghĩa là:

Một truyện có thể có nhiều tác giả (đồng tác giả, dịch giả...). Một tác giả cũng có thể có nhiều truyện.

* * *

# 8\. Genre
    
    
    genre
    
    id
    
    name

Ví dụ
    
    
    Tiên hiệp
    
    Kiếm hiệp
    
    Huyền huyễn
    
    Ngôn tình
    
    Đô thị

* * *

# 9\. StoryGenre

Giống StoryAuthor.
    
    
    story_genre
    
    
    story_id
    
    genre_id

Ví dụ
    
    
    Đấu La Đại Lục
    
    ↓
    
    Tiên hiệp
    
    ↓
    
    Huyền huyễn
    
    ↓
    
    Hành động

Một truyện có nhiều thể loại.

* * *

# 10\. Bookmark
    
    
    bookmark

Field  
---  
id  
story_id  
chapter_id  
created_at  
  
Dùng để
    
    
    Đánh dấu chương đang đọc.

Sau này nếu ứng dụng có nhiều người dùng, bạn chỉ cần thêm `user_id` vào bảng này mà không phải thiết kế lại.

* * *

# 11\. Reading History
    
    
    history

Field  
---  
id  
story_id  
chapter_id  
read_time  
  
Có thể mở rộng:
    
    
    progress
    
    scroll_position
    
    device
    
    last_sync

* * *

# 12\. Crawl Job

Crawler không nên chạy lung tung.

Ta cần bảng
    
    
    crawl_job

Ví dụ

Field  
---  
id  
story_id  
type  
status  
retry  
created_at  
  
Status
    
    
    PENDING
    
    RUNNING
    
    SUCCESS
    
    FAILED

Đây là nền tảng nếu sau này dùng Celery hoặc Dramatiq.

* * *

# 13\. Crawl Log
    
    
    crawl_log

Ví dụ

Field  
---  
id  
job_id  
message  
level  
created_at  
  
Ví dụ
    
    
    INFO
    
    Download chapter 150
    
    
    WARNING
    
    Captcha detected
    
    
    ERROR
    
    Timeout

* * *

# 14\. Soft Delete

Đừng xóa dữ liệu ngay.

Thay vì
    
    
    DELETE

Dùng
    
    
    is_deleted

hoặc
    
    
    deleted_at

Ví dụ
    
    
    Story
    
    deleted_at=NULL

↓

Đang tồn tại.
    
    
    deleted_at=2026...

↓

Đã xóa logic.

Ưu điểm:

  * Khôi phục được dữ liệu. 
  * Không làm hỏng các khóa ngoại. 
  * Phục vụ audit và thống kê. 



* * *

# 15\. Timestamp

Mọi bảng nên có
    
    
    created_at
    
    updated_at

Một số bảng thêm
    
    
    deleted_at

Không nên dùng
    
    
    createDate
    
    modifyDate
    
    date
    
    time

Hãy thống nhất cách đặt tên trong toàn bộ dự án.

* * *

# 16\. UNIQUE Constraint

Ví dụ
    
    
    story.slug

Không được trùng.
    
    
    UNIQUE(slug)

Hoặc tốt hơn:
    
    
    UNIQUE(source_id, slug)

Vì hai website khác nhau hoàn toàn có thể có cùng một `slug`.

* * *

# 17\. Composite UNIQUE cho Chapter

Đừng đặt
    
    
    UNIQUE(title)

Sai.

Hai truyện khác nhau có thể đều có
    
    
    Chương 1

Đúng hơn:
    
    
    UNIQUE(story_id,index)

hoặc
    
    
    UNIQUE(story_id,url)

Điều này ngăn crawler chèn trùng chương của cùng một truyện.

* * *

# 18\. Danh sách Index nên tạo

Bảng| Index đề xuất  
---|---  
story| source_id, slug, status  
chapter| story_id, (story_id, index), updated_at  
story_author| story_id, author_id  
story_genre| story_id, genre_id  
bookmark| story_id, chapter_id  
history| story_id, read_time  
crawl_job| status, created_at  
crawl_log| job_id, level  
  
Không nên tạo quá nhiều index vì mỗi lần `INSERT`/`UPDATE` đều phải cập nhật index, làm giảm tốc độ ghi.

* * *

# Cấu trúc Database hoàn chỉnh
    
    
    source
    │
    ├── story
    │      │
    │      ├── chapter
    │      ├── bookmark
    │      ├── history
    │      ├── image
    │      ├── download
    │      │
    │      ├── story_author
    │      │          │
    │      │          author
    │      │
    │      └── story_genre
    │                 │
    │                 genre
    │
    ├── crawl_job
    │      │
    │      └── crawl_log
    │
    └── setting

Đây là nền tảng đủ mạnh để phát triển từ ứng dụng đọc truyện cá nhân lên một hệ thống crawler quy mô lớn.

* * *

# Bài tập

### Bài 1

Vẽ lại ERD đầy đủ cho các bảng:

  * source 
  * story 
  * chapter 
  * author 
  * story_author 
  * genre 
  * story_genre 
  * bookmark 
  * history 
  * crawl_job 
  * crawl_log 



Đánh dấu rõ PK, FK, UNIQUE và INDEX.

### Bài 2

Viết file `schema.sql` tạo toàn bộ các bảng trên bằng SQLite, bao gồm:

  * `PRIMARY KEY`
  * `FOREIGN KEY`
  * `UNIQUE`
  * `CHECK` (ví dụ `status IN ('ongoing', 'completed', 'hiatus')`) 
  * Các `CREATE INDEX` cần thiết. 



### Bài 3

Giả sử một website đổi URL của truyện nhưng giữ nguyên nội dung. Hãy đề xuất cách thiết kế để crawler vẫn nhận ra đó là cùng một truyện mà không tạo bản ghi mới (gợi ý: cân nhắc `external_id`, `canonical_url`, hoặc cơ chế so khớp theo plugin).

### Bài 4 (nâng cao)

Thiết kế thêm các bảng:

  * `alternative_title` (tên gọi khác của truyện) 
  * `translator`
  * `story_translator`
  * `rating`
  * `comment`



Đảm bảo thiết kế vẫn tuân thủ chuẩn hóa dữ liệu và có khả năng mở rộng trong tương lai.

Ở **Buổi 3** , chúng ta sẽ chuyển từ thiết kế cơ sở dữ liệu sang **thiết kế Domain Model bằng Python** , xây dựng các `dataclass`, `Value Object`, `Enum`, quy tắc validation và mối quan hệ giữa các model theo tư duy Domain-Driven Design, thay vì chỉ ánh xạ đơn thuần từ bảng cơ sở dữ liệu.

