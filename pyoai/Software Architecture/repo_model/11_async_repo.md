# Khóa học: Thiết kế Model & Repository cho App Cào Truyện

# Buổi 11 - Async Repository & Async Unit of Work (Deep Dive)

> Đây là một trong những buổi quan trọng nhất nếu mục tiêu cuối cùng là xây dựng **crawler tốc độ cao**.

Từ buổi này trở đi, chúng ta sẽ chuyển dần từ kiến trúc đồng bộ (synchronous) sang bất đồng bộ (asynchronous).

Một crawler hiện đại gần như luôn sử dụng:

  * aiohttp 
  * asyncio 
  * aiosqlite 
  * async queue 
  * async worker 



Nếu Repository vẫn là synchronous thì toàn bộ pipeline sẽ bị chậm.

* * *

# Roadmap
    
    
    ✓ Buổi 1  Domain Analysis
    ✓ Buổi 2  Database Design
    ✓ Buổi 3  Domain Model
    ✓ Buổi 4  Repository Pattern
    ✓ Buổi 5  Generic Repository
    ✓ Buổi 6  Data Mapper
    ✓ Buổi 7  Unit Of Work
    ✓ Buổi 8  Specification
    ✓ Buổi 9  Pagination
    ✓ Buổi 10 Bulk Processing
    
    ==========================
    ► Buổi 11 Async Repository
    ==========================
    
    Buổi 12 Cache Repository
    
    ...

* * *

# 1\. Vì sao cần Async?

Giả sử crawler
    
    
    Download
    
    ↓
    
    Parse
    
    ↓
    
    Save SQLite
    
    ↓
    
    Download
    
    ↓
    
    Parse
    
    ↓
    
    Save SQLite

Mọi thứ diễn ra tuần tự.

CPU sẽ chờ

↓

SQLite

↓

Network

↓

Disk

Rất lãng phí.

* * *

# 2\. Kiến trúc Async

Ta muốn
    
    
    Download A
    
    Download B
    
    Download C
    
    Download D
    
            ↓
    
    Parse
    
            ↓
    
    Save SQLite

Các công việc I/O có thể diễn ra xen kẽ.

* * *

# 3\. Repository hiện tại

Hiện nay
    
    
    story = repository.get_by_id(10)

Đồng bộ.

Muốn Async

↓
    
    
    story = await repository.get_by_id(10)

* * *

# 4\. Async Repository Interface
    
    
    from abc import ABC
    from abc import abstractmethod
    
    
    class StoryRepository(ABC):
    
        @abstractmethod
        async def get_by_id(
            self,
            story_id: int
        ):
            ...

Mọi thao tác I/O đều là `async`.

* * *

# 5\. Async Save
    
    
    class StoryRepository(ABC):
    
        @abstractmethod
        async def save(
            self,
            story
        ):
            ...

Service
    
    
    await repository.save(story)

* * *

# 6\. Async List
    
    
    async def find(
        self,
        options
    ):
        ...

Không còn
    
    
    repository.find(...)

Mà
    
    
    await repository.find(...)

* * *

# 7\. Async SQLite

Dùng
    
    
    import aiosqlite

Không phải
    
    
    sqlite3

* * *

# 8\. Connection
    
    
    conn = await aiosqlite.connect(
        DB_PATH
    )

Khác
    
    
    sqlite3.connect(...)

* * *

# 9\. Cursor
    
    
    cursor = await conn.execute(
        sql,
        params
    )

Mọi thao tác đều có `await`.

* * *

# 10\. Fetch
    
    
    rows = await cursor.fetchall()

Không còn
    
    
    fetchall()

* * *

# 11\. Mapper không đổi

Mapper
    
    
    Row
    
    ↓
    
    Story

Không biết Async.

Mapper vẫn là
    
    
    StoryMapper.to_entity(row)

Điều này rất quan trọng:

> Async chỉ ảnh hưởng đến tầng Infrastructure, không ảnh hưởng Domain.

* * *

# 12\. Async Unit Of Work

Interface
    
    
    class AsyncUnitOfWork(ABC):
    
        stories: StoryRepository
    
        chapters: ChapterRepository
    
        authors: AuthorRepository
    
        @abstractmethod
        async def commit(self):
            ...
    
        @abstractmethod
        async def rollback(self):
            ...

* * *

# 13\. Async Context Manager

Không dùng
    
    
    with uow:

Mà
    
    
    async with uow:
        ...

Python sẽ gọi
    
    
    __aenter__()
    
    __aexit__()

* * *

# 14\. Async Database Session
    
    
    class DatabaseSession:
    
        async def __aenter__(self):
    
            self.conn = await aiosqlite.connect(
                self.path
            )
    
            self.conn.row_factory = aiosqlite.Row
    
            return self

* * *

# 15\. Async Exit
    
    
    async def __aexit__(
        self,
        exc_type,
        exc,
        tb
    ):
        await self.conn.close()

* * *

# 16\. Async Commit
    
    
    await conn.commit()

Rollback
    
    
    await conn.rollback()

Giống SQLite.

Chỉ thêm await.

* * *

# 17\. Async Repository
    
    
    class SQLiteStoryRepository:
    
        async def get_by_id(
            self,
            story_id
        ):
    
            cursor = await self.conn.execute(
                SQL,
                (
                    story_id,
                )
            )
    
            row = await cursor.fetchone()
    
            return StoryMapper.to_entity(row)

Repository vẫn rất sạch.

* * *

# 18\. Async Bulk Insert
    
    
    await conn.executemany(
        SQL,
        records
    )

Đây sẽ là API chính của crawler.

* * *

# 19\. Async Service
    
    
    class StoryService:
    
        async def import_story(
            self,
            story
        ):
            ...

Gọi
    
    
    await service.import_story(
        story
    )

* * *

# 20\. Async Pipeline
    
    
    aiohttp
    
    ↓
    
    Parser
    
    ↓
    
    Story
    
    ↓
    
    Repository
    
    ↓
    
    SQLite

Toàn bộ đều Async.

* * *

# 21\. Semaphore

Không nên
    
    
    10000 task

↓

SQLite

SQLite chỉ có một writer tại một thời điểm.

Nên giới hạn:
    
    
    Semaphore(20)

Ví dụ:

  * tải HTML: có thể 20–100 tác vụ đồng thời (tùy website) 
  * ghi SQLite: thường nên gom thành một hoặc vài worker ghi dữ liệu 



* * *

# 22\. Producer Consumer

Kiến trúc crawler chuyên nghiệp
    
    
    Downloader
    
    ↓
    
    Queue
    
    ↓
    
    Parser
    
    ↓
    
    Queue
    
    ↓
    
    Repository

Đây là Pipeline.

Không nên
    
    
    Download
    
    ↓
    
    Save
    
    ↓
    
    Download
    
    ↓
    
    Save

Pipeline giúp các giai đoạn hoạt động song song.

* * *

# 23\. Async Queue
    
    
    queue = asyncio.Queue()

Downloader

↓
    
    
    await queue.put(story)

Saver

↓
    
    
    story = await queue.get()

Đây là mô hình Producer–Consumer chuẩn trong asyncio.

* * *

# 24\. Async Saver

Một Worker
    
    
    while True:
    
        story = await queue.get()
    
        await repository.save(story)
    
        queue.task_done()

Có thể mở rộng để gom nhiều phần tử trước khi ghi.

* * *

# 25\. Batch Saver

Tốt hơn nữa
    
    
    Queue
    
    ↓
    
    500 chapter
    
    ↓
    
    executemany()
    
    ↓
    
    commit()

Đây là kiến trúc hiệu năng cao.

* * *

# 26\. Kiến trúc hoàn chỉnh
    
    
    Downloader
          │
          ▼
    asyncio.Queue
          │
          ▼
    Parser Workers
          │
          ▼
    asyncio.Queue
          │
          ▼
    Batch Saver
          │
          ▼
    Async Repository
          │
          ▼
    Async Unit Of Work
          │
          ▼
    aiosqlite

Đây là kiến trúc mà nhiều crawler lớn sử dụng.

* * *

# 27\. Sai lầm phổ biến

Sai
    
    
    async def save():
    
        sqlite3.connect(...)

Nếu đã Async

↓

phải dùng
    
    
    aiosqlite

* * *

Sai
    
    
    await mapper.to_entity()

Mapper không phải I/O.

Không cần Async.

* * *

Sai
    
    
    for story:
    
        await repository.save(...)

Nên
    
    
    Batch
    
    ↓
    
    executemany()

* * *

Sai
    
    
    100 task
    
    ↓
    
    ghi SQLite

SQLite chỉ có một writer.

Nên có một **Saver Worker** nhận dữ liệu từ Queue.

* * *

# 28\. Async Repository không thay đổi Domain

Đây là điểm rất quan trọng.

Domain vẫn là
    
    
    Story
    
    Chapter
    
    Author

Repository Interface

↓

Async

Mapper

↓

không đổi

Entity

↓

không đổi

Business Rule

↓

không đổi

Chỉ có tầng Infrastructure thay đổi.

* * *

# 29\. So sánh Sync và Async

Đồng bộ| Bất đồng bộ  
---|---  
`sqlite3`| `aiosqlite`  
`with`| `async with`  
`execute()`| `await execute()`  
`fetchall()`| `await fetchall()`  
`commit()`| `await commit()`  
`save()`| `await save()`  
`UnitOfWork`| `AsyncUnitOfWork`  
  
* * *

# 30\. Kiến trúc sau 11 buổi
    
    
                    GUI
                     │
                     ▼
              StoryService (async)
                     │
                     ▼
            AsyncUnitOfWork
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
    StoryRepository      ChapterRepository
          │                     │
          ▼                     ▼
       StoryMapper        ChapterMapper
          │                     │
          └──────────┬──────────┘
                     ▼
               aiosqlite
                     │
                     ▼
                  SQLite

Đến thời điểm này, tầng Repository của chúng ta đã có:

  * Repository Pattern 
  * Generic Repository 
  * Data Mapper 
  * Unit of Work 
  * Specification 
  * Pagination 
  * Bulk Operations 
  * Async Repository 



Đây là một nền tảng rất vững để xây dựng crawler truyện quy mô lớn.

* * *

# Bài tập

## Bài 1

Chuyển `StoryRepository` từ đồng bộ sang bất đồng bộ:

  * `async get_by_id()`
  * `async save()`
  * `async find()`
  * `async delete()`



* * *

## Bài 2

Viết `AsyncDatabaseSession`:

  * `__aenter__()`
  * `__aexit__()`
  * `commit()`
  * `rollback()`



sử dụng `aiosqlite`.

* * *

## Bài 3

Viết `AsyncUnitOfWork` quản lý:

  * `StoryRepository`
  * `ChapterRepository`
  * `AuthorRepository`



và đảm bảo tất cả dùng chung một kết nối `aiosqlite`.

* * *

## Bài 4 (dự án thực tế)

Thiết kế pipeline crawler bất đồng bộ:

  1. Downloader dùng `aiohttp` tải HTML. 
  2. Parser chuyển HTML thành `Story` và `Chapter`. 
  3. Đưa các `Chapter` vào `asyncio.Queue`. 
  4. Một `BatchSaverWorker` lấy tối đa 500 `Chapter` mỗi lần. 
  5. Gọi `bulk_upsert()` qua `AsyncRepository`. 
  6. `AsyncUnitOfWork` quản lý transaction cho từng batch. 
  7. Nếu ghi thất bại, rollback batch hiện tại và ghi log để có thể retry. 



Đây là kiến trúc nền tảng cho một crawler hiệu năng cao, ổn định và dễ mở rộng.

* * *

# Chuẩn bị cho Buổi 12

Buổi tiếp theo chúng ta sẽ học **Cache Repository Pattern**.

Chúng ta sẽ xây dựng một tầng cache nằm trước Repository, hỗ trợ:

  * In-memory cache 
  * LRU cache 
  * TTL (Time To Live) 
  * Redis cache (mở rộng) 
  * Cache-Aside Pattern 
  * Read-through và Write-through cache 
  * Cache invalidation 



Mục tiêu là giảm số lần truy vấn SQLite, tăng tốc độ hiển thị dữ liệu và giảm tải cho tầng lưu trữ khi crawler và giao diện cùng truy cập dữ liệu.

