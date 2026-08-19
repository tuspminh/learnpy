Khi sử dụng `httpx` bất đồng bộ (`async`/`await`), nếu bạn ghi dữ liệu vào cơ sở dữ liệu (DB) bằng các thư viện đồng bộ tiêu chuẩn (như `sqlite3` hoặc `psycopg2`), các thao tác ghi ổ đĩa sẽ **làm đóng băng (block)** Event Loop của `asyncio`, khiến toàn bộ ứng dụng bị khựng lại.

Để giải quyết triệt để, chúng ta cần sử dụng các **driver DB bất đồng bộ (Async DB Drivers)**:

* **SQLite:** Sử dụng **`aiosqlite`**
* **PostgreSQL:** Sử dụng **`asyncpg`** (Driver PostgreSQL nhanh nhất hiện nay cho Python)

---

## 1. SQLite bất đồng bộ với `aiosqlite`

`aiosqlite` giúp chuyển đổi thư viện `sqlite3` tiêu chuẩn thành giao diện `async/await`. Phù hợp cho ứng dụng nhỏ, lưu trữ local hoặc crawler vừa phải.

### Cài đặt

```bash
pip install httpx selectolax aiosqlite

```

### Script Scraper + Ghi SQLite hoàn chỉnh

```python
import asyncio
import logging
import httpx
from selectolax.parser import HTMLParser
import aiosqlite

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

DB_FILE = "quotes.db"
BASE_URL = "https://quotes.toscrape.com/page/{page_num}/"

# 1. Hàm khởi tạo Bảng dữ liệu trong SQLite
async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page INTEGER,
                quote TEXT,
                author TEXT,
                tags TEXT
            )
        """)
        await db.commit()

# 2. Hàm ghi hàng loạt (Batch Insert) dữ liệu bất đồng bộ
async def save_quotes_to_db(quotes: list):
    if not quotes:
        return
    
    async with aiosqlite.connect(DB_FILE) as db:
        # Chuẩn bị dữ liệu dạng tuple để insert
        data_to_insert = [
            (q["page"], q["quote"], q["author"], ",".join(q["tags"]))
            for q in quotes
        ]
        
        # executemany giúp ghi hàng loạt record trong 1 transaction duy nhất
        await db.executemany(
            "INSERT INTO quotes (page, quote, author, tags) VALUES (?, ?, ?, ?)",
            data_to_insert
        )
        await db.commit()
        logging.info(f"💾 Đã ghi {len(quotes)} record vào SQLite!")

# 3. Hàm cào dữ liệu bằng httpx + selectolax
async def fetch_and_parse(client: httpx.AsyncClient, page_num: int) -> list:
    url = BASE_URL.format(page_num=page_num)
    try:
        response = await client.get(url)
        response.raise_for_status()
        
        tree = HTMLParser(response.text)
        quotes = []
        for node in tree.css(".quote"):
            quotes.append({
                "page": page_num,
                "quote": node.css_first(".text").text(strip=True),
                "author": node.css_first(".author").text(strip=True),
                "tags": [t.text(strip=True) for t in node.css(".tag")]
            })
        return quotes
    except Exception as e:
        logging.error(f"❌ Lỗi cào trang {page_num}: {e}")
        return []

async def main():
    await init_db()
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Cào song song 5 trang
        tasks = [fetch_and_parse(client, page) for page in range(1, 6)]
        results = await asyncio.gather(*tasks)

    # Gom kết quả lại và ghi vào Database
    all_quotes = [q for page_quotes in results for q in page_quotes]
    await save_quotes_to_db(all_quotes)

if __name__ == "__main__":
    asyncio.run(main())

```

---

## 2. PostgreSQL bất đồng bộ với `asyncpg`

`asyncpg` được thiết kế đặc biệt cho `asyncio` và có tốc độ xử lý nhanh hơn `psycopg2` từ **3 đến 5 lần**. Đây là lựa chọn hàng đầu cho mảng Production & Big Data.

### Cài đặt

```bash
pip install httpx selectolax asyncpg

```

### Script Scraper + Ghi PostgreSQL hoàn chỉnh (Dùng Connection Pool)

```python
import asyncio
import logging
import httpx
from selectolax.parser import HTMLParser
import asyncpg

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Thông tin kết nối PostgreSQL (Thay đổi theo cấu hình của bạn)
PG_URI = "postgresql://postgres:password@localhost:5432/my_scraper_db"
BASE_URL = "https://quotes.toscrape.com/page/{page_num}/"

# 1. Khởi tạo Bảng trong PostgreSQL
async def init_pg_table(pool: asyncpg.Pool):
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id SERIAL PRIMARY KEY,
                page INT,
                quote TEXT,
                author VARCHAR(255),
                tags TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

# 2. Ghi dữ liệu vào Postgres dùng Connection Pool
async def save_quotes_to_postgres(pool: asyncpg.Pool, quotes: list):
    if not quotes:
        return
    
    # Mượn 1 connection từ Pool
    async with pool.acquire() as conn:
        # Tải dữ liệu siêu tốc bằng executemany
        data_tuples = [
            (q["page"], q["quote"], q["author"], q["tags"]) 
            for q in quotes
        ]
        
        await conn.executemany(
            """
            INSERT INTO quotes (page, quote, author, tags) 
            VALUES ($1, $2, $3, $4)
            """,
            data_tuples
        )
        logging.info(f"🐘 [PostgreSQL] Đã lưu {len(quotes)} records thành công!")

async def fetch_and_parse(client: httpx.AsyncClient, page_num: int) -> list:
    url = BASE_URL.format(page_num=page_num)
    try:
        res = await client.get(url)
        res.raise_for_status()
        tree = HTMLParser(res.text)
        
        return [{
            "page": page_num,
            "quote": n.css_first(".text").text(strip=True),
            "author": n.css_first(".author").text(strip=True),
            "tags": [t.text(strip=True) for t in n.css(".tag")]
        } for n in tree.css(".quote")]
    except Exception as e:
        logging.error(f"❌ Lỗi trang {page_num}: {e}")
        return []

async def main():
    # Tạo Connection Pool cho PostgreSQL
    async with asyncpg.create_pool(dsn=PG_URI, min_size=2, max_size=10) as pg_pool:
        # Khởi tạo bảng
        await init_pg_table(pg_pool)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            tasks = [fetch_and_parse(client, page) for page in range(1, 11)]
            results = await asyncio.gather(*tasks)

        all_quotes = [item for page_data in results for item in page_data]
        
        # Ghi vào DB
        await save_quotes_to_postgres(pg_pool, all_quotes)

if __name__ == "__main__":
    asyncio.run(main())

```

---

## ⚡ Best Practices để đạt tốc độ cao nhất khi lưu Database

1. **Ghi theo lô (Batch Processing / Bulk Insert):**
* **Tránh:** Gọi lệnh `INSERT` từng dòng một trong vòng lặp (`for item in data: await db.execute(...)`).
* **Nên:** Gom dữ liệu lại thành danh sách (ví dụ 100 - 500 items) và ghi bằng `executemany()` trong 1 Transaction duy nhất.


2. **Dùng Connection Pool với PostgreSQL (`asyncpg.create_pool`):**
* Việc mở/đóng kết nối tới DB tốn rất nhiều thời gian mạng. Connection Pool giữ sẵn các kết nối mở và tái sử dụng chúng cực kỳ hiệu quả.


3. **Chống trùng lặp dữ liệu (Upsert / ON CONFLICT):**
* Khi cào dữ liệu nhiều lần, bạn có thể dùng cú pháp `ON CONFLICT` của PostgreSQL để cập nhật thay vì tạo dòng mới:
```sql
INSERT INTO quotes (url, title) VALUES ($1, $2)
ON CONFLICT (url) DO UPDATE SET title = EXCLUDED.title;

```