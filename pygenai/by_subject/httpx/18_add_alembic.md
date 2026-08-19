Khi dự án phát triển trên môi trường Production, việc thay đổi cấu trúc bảng (thêm cột, đổi kiểu dữ liệu, tạo index) bằng các câu lệnh `CREATE TABLE IF NOT EXISTS` thủ công sẽ rất nguy hiểm và khó kiểm soát.

**Alembic** là công cụ Database Migration chính thức của SQLAlchemy. Để dùng Alembic với `asyncpg` trong dự án Async của chúng ta, Alembic sẽ sử dụng **SQLAlchemy Async Engine** để kết nối và thực thi các file revision bản vẽ DB.

---

## 📁 Cấu trúc thư mục sau khi tích hợp Alembic

```text
my-async-scraper/
├── alembic/                 # Thư mục quản lý migration do Alembic tạo
│   ├── versions/            # Chứa các file bản vẽ migration (.py)
│   └── env.py               # File cấu hình môi trường chạy migration
├── app/
│   ├── __init__.py
│   ├── database.py          # Kết nối Async SQLAlchemy
│   ├── models.py            # Khai báo các Bảng (ORM Models)
│   └── main.py              # Script cào và lưu dữ liệu
├── alembic.ini              # File cấu hình chung của Alembic
├── docker-compose.yml
├── Dockerfile
└── requirements.txt

```

---

## Bước 1: Bổ sung thư viện vào `requirements.txt`

Thêm `alembic` và `sqlalchemy` (phiên bản 2.x trở lên hỗ trợ Async hoàn hảo):

```text
httpx>=0.27.0
apscheduler>=3.10.0
selectolax>=0.3.0
asyncpg>=0.29.0
sqlalchemy>=2.0.0
alembic>=1.13.0
python-dotenv>=1.0.0

```

---

## Bước 2: Khởi tạo cấu hình Alembic Async

Chạy lệnh sau tại thư mục gốc của dự án (hoặc chạy trong container):

```bash
alembic init -t async alembic

```

*Lưu ý cờ `-t async`: Bắt buộc phải có để Alembic khởi tạo sẵn template hỗ trợ `asyncio` và `asyncpg`.*

---

## Bước 3: Định nghĩa Model Bảng (`app/models.py`)

Tạo file `app/models.py` khai báo cấu trúc bảng `quotes` bằng SQLAlchemy ORM:

```python
from datetime import datetime
from sqlalchemy import ARRAY, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class QuoteModel(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quote = Column(Text, nullable=False)
    author = Column(String(255), nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

```

---

## Bước 4: Cấu hình `alembic/env.py` kết nối với `.env`

Mở file `alembic/env.py`, chỉnh sửa 2 mục quan trọng:

1. Đọc **Database URL** động từ biến môi trường `.env`.
2. Khai báo **`target_metadata`** từ `app/models.py` để Alembic tự so sánh và sinh file migration (`--autogenerate`).

```python
import asyncio
import os
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# 1. Import Base model từ app của bạn
from app.models import Base

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

# 2. Gán metadata của Model cho Alembic
target_metadata = Base.metadata

# 3. Tạo DATABASE_URL động từ biến môi trường Docker/.env
def get_url():
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("DB_HOST", "postgres-db")
    port = os.getenv("DB_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "scraper_db")
    
    # Bắt buộc dùng driver postgresql+asyncpg://
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

def run_migrations_offline() -> None:
    """Chạy migration ở chế độ offline (xuất ra SQL file)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Chạy migration ở chế độ Async trực tiếp vào DB."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

```

---

## Bước 5: Quy trình tạo và chạy Migration trong Docker

### 1. Tạo bản vẽ Migration đầu tiên (Autogenerate)

Chạy lệnh sau để Alembic tự quét file `app/models.py` và so sánh với PostgreSQL để tạo file bản vẽ trong `alembic/versions/`:

```bash
docker compose run --rm scraper-service alembic revision --autogenerate -m "create quotes table"

```

Alembic sẽ tự động sinh ra 1 file Python trong thư mục `alembic/versions/xxxx_create_quotes_table.py` chứa hàm `upgrade()` và `downgrade()`.

### 2. Thống nhất áp dụng Migration vào Database

Chạy lệnh `upgrade head` để áp dụng bản vẽ mới nhất vào PostgreSQL:

```bash
docker compose run --rm scraper-service alembic upgrade head

```

---

## Bước 6: Tự động chạy Migration khi Container khởi chạy

Để ứng dụng tự động cập nhật Database mỗi khi triển khai Production mà không cần gõ lệnh tay, bạn có thể tạo file `entrypoint.sh`:

### 1. Tạo file `entrypoint.sh` tại thư mục gốc:

```bash
#!/bin/sh
set -e

echo "⏳ Đang kiểm tra và áp dụng Database Migrations (Alembic)..."
alembic upgrade head

echo "🚀 Khởi chạy ứng dụng Async Scraper..."
exec "$@"

```

### 2. Cập nhật `Dockerfile` để gọi `entrypoint.sh`:

```dockerfile
# ... các bước cũ ...

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER appuser

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app/main.py"]

```

---

## 🛠️ Cheat Sheet các câu lệnh Alembic thường dùng

| Thao tác | Lệnh thực thi |
| --- | --- |
| **Tạo file Migration mới** | `alembic revision --autogenerate -m "tên_mô_tả_thay_đổi"` |
| **Áp dụng toàn bộ Migration** | `alembic upgrade head` |
| **Undo 1 bước Migration (Rollback)** | `alembic downgrade -1` |
| **Xem lịch sử các bản Migration** | `alembic history` |
| **Xem phiên bản DB hiện tại** | `alembic current` |