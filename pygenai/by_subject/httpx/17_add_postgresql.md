Để kết nối **Async Scraper** với **PostgreSQL** trong môi trường Docker, hai service (Scraper và Database) cần nằm trên cùng một mạng ảo (Docker Network).

Điểm quan trọng nhất cần lưu ý: **Inside Docker, địa chỉ host của Database KHÔNG PHẢI là `localhost` mà chính là Tên Service (`postgres-db`) được định nghĩa trong `docker-compose.yml`.**

---

## 1. Cập nhật file `.env`

Khai báo thông tin tài khoản Database và các biến môi trường:

```env
# PostgreSQL Credentials
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret_password_123
POSTGRES_DB=scraper_db

# Kết nối nội bộ Docker (DB_HOST trùng tên service trong docker-compose.yml)
DB_HOST=postgres-db
DB_PORT=5432

```

---

## 2. Cập nhật `docker-compose.yml`

Chúng ta thêm service `postgres-db`, cấu hình `healthcheck` (để đảm bảo Database đã sẵn sàng nhận kết nối mới khởi chạy Scraper) và gắn **Named Volume** `pgdata` để dữ liệu không bị mất khi xóa Container.

```yaml
version: '3.8'

services:
  # 🐘 Service 1: PostgreSQL Database
  postgres-db:
    image: postgres:15-alpine
    container_name: async_postgres_db
    restart: unless-stopped
    env_file:
      - .env
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"  # Mở port 5432 ra ngoài host để bạn kết nối qua DBeaver/PgAdmin
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5

  # 🚀 Service 2: Async Scraper + APScheduler App
  scraper-service:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: async_scraper_app
    restart: unless-stopped
    depends_on:
      postgres-db:
        condition: service_healthy # Chỉ chạy Scraper khi Postgres đã SẴN SÀNG
    env_file:
      - .env
    environment:
      - TZ=Asia/Ho_Chi_Minh
    volumes:
      - ./logs:/app/logs

# Khai báo Volume cho PostgreSQL để lưu dữ liệu lâu dài trên máy thật
volumes:
  pgdata:

```

---

## 3. Thêm `asyncpg` vào `requirements.txt`

Thêm thư viện driver `asyncpg` để Python giao tiếp bất đồng bộ với Postgres:

```text
httpx>=0.27.0
apscheduler>=3.10.0
selectolax>=0.3.0
asyncpg>=0.29.0
python-dotenv>=1.0.0

```

---

## 4. Mã nguồn Python hoàn chỉnh (`app/main.py`)

File `main.py` dưới đây sẽ tự động tạo Connection Pool với PostgreSQL, khởi tạo bảng dữ liệu nếu chưa có, và lưu kết quả cào được vào Database sau mỗi lượt chạy của APScheduler:

```python
import asyncio
import logging
import os
import signal
import httpx
import asyncpg
from selectolax.parser import HTMLParser
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# 1. Tạo Database DSN từ biến môi trường
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "scraper_db")
DB_HOST = os.getenv("DB_HOST", "postgres-db")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 2. Khởi tạo Bảng dữ liệu
async def init_db(pool: asyncpg.Pool):
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id SERIAL PRIMARY KEY,
                quote TEXT,
                author VARCHAR(255),
                tags TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        logging.info("🐘 PostgreSQL: Khởi tạo bảng 'quotes' thành công!")

# 3. Hàm cào và parse dữ liệu
async def fetch_and_parse() -> list:
    url = "https://quotes.toscrape.com/page/1/"
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get(url)
        res.raise_for_status()
        
        tree = HTMLParser(res.text)
        quotes = []
        for n in tree.css(".quote"):
            quotes.append((
                n.css_first(".text").text(strip=True),
                n.css_first(".author").text(strip=True),
                [t.text(strip=True) for t in n.css(".tag")]
            ))
        return quotes

# 4. Tác vụ định kỳ (Job) của APScheduler
async def scrape_job(pool: asyncpg.Pool):
    logging.info("⏰ [JOB STARTED] Bắt đầu cào dữ liệu mới...")
    try:
        data = await fetch_and_parse()
        
        if data:
            async with pool.acquire() as conn:
                # Insert hàng loạt dữ liệu vào PostgreSQL bằng executemany
                await conn.executemany("""
                    INSERT INTO quotes (quote, author, tags)
                    VALUES ($1, $2, $3);
                """, data)
                logging.info(f"💾 [JOB SUCCESS] Đã lưu {len(data)} bản ghi vào PostgreSQL!")

    except Exception as exc:
        logging.error(f"❌ [JOB FAILED] Lỗi xảy ra: {exc}")

# 5. Hàm chạy chính (Main Event Loop)
async def main():
    logging.info("🔌 Đang kết nối tới PostgreSQL Pool...")
    # Khởi tạo Connection Pool kết nối tới Postgres
    pool = await asyncpg.create_pool(dsn=DATABASE_URL, min_size=2, max_size=10)
    await init_db(pool)

    # Cấu hình Scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scrape_job,
        trigger=IntervalTrigger(seconds=60), # Chạy mỗi 60 giây
        args=[pool],
        id="postgres_scraper_job",
        max_instances=1,
        coalesce=True
    )
    
    scheduler.start()
    logging.info("🚀 Scheduler + Asyncpg Scraper đã khởi chạy!")

    # Graceful Shutdown
    stop_event = asyncio.Event()

    def shutdown_handler(sig, frame):
        logging.info(f"🛑 Nhận tín hiệu {sig}. Đang dừng hệ thống an toàn...")
        scheduler.shutdown(wait=True)
        stop_event.set()

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    while not stop_event.is_set():
        await asyncio.sleep(1)

    # Đóng Connection Pool PostgreSQL an toàn
    await pool.close()
    logging.info("✅ Đã đóng toàn bộ kết nối PostgreSQL an toàn!")

if __name__ == "__main__":
    asyncio.run(main())

```

---

## 5. Khởi chạy và Kiểm tra

### Khởi chạy toàn bộ hệ thống bằng Docker Compose:

```bash
docker compose up -d --build

```

### Xem log hệ thống realtime:

```bash
docker compose logs -f

```

*(Bạn sẽ thấy `postgres-db` chạy và khởi tạo xong trước, sau đó `scraper-service` mới bật lên kết nối và cào dữ liệu)*.

### Kết nối kiểm tra dữ liệu từ máy host:

Bạn có thể dùng ứng dụng **DBeaver** hoặc **TablePlus** trên máy thật để kiểm tra dữ liệu:

* **Host:** `localhost`
* **Port:** `5432`
* **Database:** `scraper_db`
* **Username / Password:** Khai báo trong file `.env`

---

## ⚠️ 2 Lỗi phổ biến nhất cần tránh

1. **Lỗi `ConnectionRefusedError`:** Do dùng `DB_HOST=localhost` trong file `.env`. Trong Docker network, phải dùng `DB_HOST=postgres-db` (trùng tên service database).
2. **Lỗi Scraper chạy trước khi Database kịp mở port:** Cần dùng `depends_on` dạng `condition: service_healthy` như trong file `docker-compose.yml` ở bước 2 để đảm bảo Postgres kiểm tra healthcheck thành công rồi mới bật Scraper.