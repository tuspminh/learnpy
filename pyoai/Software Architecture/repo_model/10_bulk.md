# Buổi 10 - Bulk Operations & Batch Processing Deep Dive

> Đây là buổi học cực kỳ quan trọng đối với mọi ứng dụng crawler. Nếu bạn chỉ biết `save()` từng bản ghi, tốc độ crawler sẽ rất chậm khi xử lý hàng nghìn hoặc hàng triệu chương truyện.

Sau buổi này, bạn sẽ biết cách thiết kế Repository để **ghi dữ liệu hàng loạt (bulk)** , **cập nhật hàng loạt** , và **xử lý theo lô (batch)** giống các hệ thống ETL, Data Pipeline và Web Crawler chuyên nghiệp.

* * *

# Roadmap hiện tại
    
    
    ✓ Buổi 1  Domain Analysis
    ✓ Buổi 2  Database Design
    ✓ Buổi 3  Domain Model
    ✓ Buổi 4  Repository Pattern
    ✓ Buổi 5  Generic Repository
    ✓ Buổi 6  Data Mapper
    ✓ Buổi 7  Unit Of Work
    ✓ Buổi 8  Specification Pattern
    ✓ Buổi 9  Pagination & Sorting
    
    ==========================
    ► Buổi 10 Bulk Processing
    ==========================
    
    Buổi 11 Async Repository
    Buổi 12 Cache Repository
    ...

* * *

# 1\. Vấn đề

Giả sử crawler lấy được
    
    
    1 Story
    
    5000 Chapter

Nếu làm như sau
    
    
    for chapter in chapters:
        repository.save(chapter)

điều gì xảy ra?
    
    
    INSERT
    
    ↓
    
    COMMIT
    
    ↓
    
    INSERT
    
    ↓
    
    COMMIT
    
    ↓
    
    INSERT
    
    ↓
    
    COMMIT
    
    ...
    
    5000 lần

SQLite sẽ phải:

  * Parse SQL 5000 lần 
  * Ghi log transaction nhiều lần 
  * Đồng bộ dữ liệu xuống đĩa nhiều lần 



=> **Rất chậm.**

* * *

# 2\. Batch Processing

Ý tưởng
    
    
    5000 chapter
    
    ↓
    
    chia thành
    
    100 chapter
    
    ↓
    
    50 batch

Không còn
    
    
    5000 transaction

Mà chỉ còn
    
    
    50 transaction

* * *

# 3\. Bulk Insert

Repository nên có
    
    
    class ChapterRepository:
    
        def bulk_insert(
            self,
            chapters: list[Chapter]
        ):
            ...

Đây sẽ là API quan trọng nhất của crawler.

* * *

# 4\. executemany()

SQLite hỗ trợ
    
    
    cursor.executemany(
        """
        INSERT INTO chapter(...)
        VALUES(...)
        """,
        data
    )

Thay vì
    
    
    for row in data:
        cursor.execute(...)

`executemany()` giảm đáng kể chi phí gửi nhiều câu lệnh giống nhau.

* * *

# 5\. Mapper kết hợp Bulk

Mapper
    
    
    Chapter
    
    ↓
    
    dict
    
    ↓
    
    tuple

Ví dụ
    
    
    [
        (
            story_id,
            index,
            title,
            url
        ),
        (
            ...
        )
    ]

Repository chỉ cần
    
    
    executemany(...)

Mapper chịu trách nhiệm chuyển Entity thành dữ liệu đầu vào.

* * *

# 6\. Batch Size

Không nên
    
    
    1.000.000 record

↓

Một lần insert.

RAM sẽ tăng rất lớn và transaction kéo dài.

* * *

Thông thường
    
    
    100
    
    hoặc
    
    500
    
    hoặc
    
    1000

record mỗi batch.

Ví dụ
    
    
    BATCH_SIZE = 500

* * *

# 7\. Hàm chia Batch
    
    
    def chunks(
        items,
        size
    ):
        for i in range(
            0,
            len(items),
            size
        ):
            yield items[i:i+size]

Ví dụ
    
    
    5000 chapter
    
    ↓
    
    500
    
    ↓
    
    10 batch

Đây là một utility rất hữu ích trong nhiều dự án.

* * *

# 8\. Bulk Save

Không phải lúc nào dữ liệu cũng là mới.

Ví dụ
    
    
    chapter 1
    
    đã tồn tại
    
    
    chapter 2
    
    mới

Lúc này cần
    
    
    INSERT
    
    +
    
    UPDATE

Đây gọi là

> Bulk Save

hoặc

> Bulk Upsert

* * *

# 9\. UPSERT trong SQLite

SQLite hỗ trợ
    
    
    INSERT INTO chapter(...)
    VALUES(...)
    ON CONFLICT(url)
    DO UPDATE SET
    title=excluded.title

Nếu `url` đã tồn tại:

↓

UPDATE

Nếu chưa:

↓

INSERT

Rất phù hợp với crawler khi quét lại truyện.

* * *

# 10\. Bulk Update

Ví dụ
    
    
    1000 chapter
    
    ↓
    
    status
    
    =
    
    downloaded

Không cần
    
    
    for ...

Repository có thể cung cấp
    
    
    bulk_update_status(
        ids,
        status
    )

Hoặc thiết kế linh hoạt hơn:
    
    
    bulk_update(
        entities
    )

* * *

# 11\. Bulk Delete

Ví dụ

Crawler phát hiện
    
    
    200 chapter
    
    đã bị xóa

Repository
    
    
    bulk_delete(
        ids
    )

SQLite
    
    
    DELETE
    
    WHERE id IN(...)

Nhanh hơn nhiều so với xóa từng dòng.

* * *

# 12\. Bulk Exists

Crawler lấy
    
    
    1000 url

Không nên
    
    
    exists()
    
    1000 lần

Nên
    
    
    existing_urls = repository.find_existing_urls(
        urls
    )

Sau đó
    
    
    Python Set
    
    ↓
    
    O(1)

để kiểm tra nhanh.

* * *

# 13\. Bulk Find

Ví dụ
    
    
    find_by_ids(
        ids
    )

SQLite
    
    
    WHERE id IN(...)

Thay vì
    
    
    SELECT
    
    1000 lần

Đây là cách giảm rất nhiều số lần truy vấn.

* * *

# 14\. Bulk Mapper

Không nên
    
    
    for row:
    
        mapper.to_entity(...)

rải rác trong Repository.

Nên
    
    
    mapper.to_entities(rows)

Ví dụ
    
    
    class ChapterMapper:
    
        @classmethod
        def to_entities(
            cls,
            rows
        ):
            return [
                cls.to_entity(row)
                for row in rows
            ]

Mapper chịu trách nhiệm chuyển đổi hàng loạt.

* * *

# 15\. Batch Import Story
    
    
    Crawler
    
    ↓
    
    Parser
    
    ↓
    
    Story
    
    ↓
    
    500 Chapter
    
    ↓
    
    Bulk Insert
    
    ↓
    
    Commit

Thay vì
    
    
    500 Commit

chỉ còn
    
    
    1 Commit

Đây là điểm khác biệt rất lớn về hiệu năng.

* * *

# 16\. Batch Processing với Unit Of Work
    
    
    with uow:
    
        story_repo.save(story)
    
        chapter_repo.bulk_insert(chapters)
    
        author_repo.bulk_insert(authors)
    
        genre_repo.bulk_insert(genres)

↓

Commit

Một transaction duy nhất.

* * *

# 17\. Batch Processing Pipeline
    
    
    Download HTML
    
    ↓
    
    Parser
    
    ↓
    
    Entity
    
    ↓
    
    Batch Queue
    
    ↓
    
    Repository
    
    ↓
    
    SQLite

Đây là pipeline phổ biến trong các hệ thống crawler.

* * *

# 18\. Streaming

Đừng
    
    
    chapters = parse_all()

Nếu truyện có
    
    
    20.000 chapter

RAM sẽ rất lớn.

Tốt hơn
    
    
    yield chapter

↓

Batch

↓

Insert

↓

Batch

↓

Insert

Kết hợp **Generator** với Batch Processing sẽ giúp ứng dụng tiêu thụ rất ít bộ nhớ.

* * *

# 19\. Batch Iterator
    
    
    Generator
    
    ↓
    
    500
    
    ↓
    
    executemany()
    
    ↓
    
    500
    
    ↓
    
    executemany()

Đây là mô hình lý tưởng cho crawler.

* * *

# 20\. Retry Batch

Nếu
    
    
    Batch số 15
    
    ↓
    
    Fail

Không cần chạy lại từ đầu.

Có thể:

  * rollback batch hiện tại 
  * ghi log 
  * retry batch đó 



Điều này đặc biệt hữu ích khi dùng cơ sở dữ liệu mạng hoặc khi có lỗi tạm thời.

* * *

# 21\. Performance

Ví dụ
    
    
    100.000 chapter

Từng dòng
    
    
    100.000 execute()

↓

Khoảng vài chục giây đến vài phút (tùy máy, transaction và I/O).

Batch
    
    
    100 executemany()

↓

Nhanh hơn rất nhiều.

Lợi ích chính đến từ việc:

  * giảm số lần gọi API của database 
  * giảm số transaction 
  * giảm chi phí phân tích câu lệnh SQL 



* * *

# 22\. Repository API chuyên nghiệp
    
    
    class ChapterRepository:
    
        save()
    
        bulk_insert()
    
        bulk_upsert()
    
        bulk_delete()
    
        bulk_update()
    
        find_by_ids()
    
        find_existing_urls()

Đây là API đủ mạnh cho một crawler quy mô lớn.

* * *

# 23\. Cấu trúc
    
    
    repositories/
    
        story_repository.py
    
        chapter_repository.py
    
    batch/
    
        batch_iterator.py
    
        chunk.py
    
    mappers/
    
        chapter_mapper.py

Có thể tách các tiện ích batch thành module riêng để tái sử dụng.

* * *

# 24\. Luồng hoàn chỉnh
    
    
    Downloader
          │
          ▼
    HTML Parser
          │
          ▼
    Generator<Chapter>
          │
          ▼
    Chunk(500)
          │
          ▼
    ChapterMapper
          │
          ▼
    executemany()
          │
          ▼
    SQLite

Đây là kiến trúc mà nhiều crawler hiệu năng cao áp dụng.

* * *

# 25\. Sai lầm phổ biến

❌ `save()` trong vòng lặp

❌ Commit sau mỗi bản ghi

❌ Parse toàn bộ 20.000 chapter vào RAM

❌ Không dùng `executemany()`

❌ Không chia batch

❌ Không dùng `UPSERT`

❌ Không tái sử dụng Mapper cho xử lý hàng loạt

* * *

# Kiến trúc sau 10 buổi
    
    
    GUI
     │
     ▼
    Service
     │
     ▼
    Unit Of Work
     │
     ├────────────┐
     ▼            ▼
    StoryRepo   ChapterRepo
     │            │
     ▼            ▼
    Bulk APIs   Bulk APIs
     │            │
     ▼            ▼
    Mapper      Mapper
     │            │
     └─────┬──────┘
           ▼
     executemany()
           ▼
        SQLite

Đây là kiến trúc rất phù hợp để nhập dữ liệu nhanh và ổn định.

* * *

# Bài tập

## Bài 1

Viết hàm:
    
    
    chunked(
        iterable,
        size
    )

  * hỗ trợ mọi iterable (không chỉ `list`) 
  * trả về từng batch bằng `yield`
  * không đọc toàn bộ dữ liệu vào RAM. 



* * *

## Bài 2

Thiết kế API cho `ChapterRepository`:

  * `bulk_insert()`
  * `bulk_upsert()`
  * `bulk_delete()`
  * `find_by_ids()`
  * `find_existing_urls()`



Giải thích trường hợp sử dụng của từng API trong crawler truyện.

* * *

## Bài 3

Cập nhật `ChapterMapper` để bổ sung:

  * `to_records(chapters)`
  * `to_entities(rows)`



nhằm hỗ trợ chuyển đổi dữ liệu hàng loạt.

* * *

## Bài 4 (dự án thực tế)

Thiết kế pipeline nhập **100.000 chapter** với các yêu cầu:

  * Parser trả về `Generator[Chapter]`
  * Chia thành batch 500 phần tử 
  * `bulk_upsert()` bằng `executemany()`
  * Chỉ `commit()` sau mỗi batch 
  * Ghi log số chapter thành công và số chapter lỗi 
  * Có khả năng retry nếu một batch thất bại. 



Đây là bài tập mô phỏng rất sát với một hệ thống crawler truyện thực tế.

* * *

# Chuẩn bị cho Buổi 11

Buổi tiếp theo chúng ta sẽ học **Async Repository & aiosqlite**.

Đây là bước chuyển từ Repository đồng bộ sang bất đồng bộ, bao gồm:

  * `AsyncUnitOfWork`
  * `AsyncRepository`
  * `aiosqlite`
  * `async with`
  * `async transaction`
  * phối hợp với downloader bất đồng bộ (`aiohttp`) để xây dựng pipeline crawler hiệu năng cao từ tải trang, phân tích HTML đến lưu cơ sở dữ liệu.

