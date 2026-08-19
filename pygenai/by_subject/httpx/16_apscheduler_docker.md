Đóng gói ứng dụng Python bằng **Docker** là bước chuẩn mực để chuyển mã nguồn từ môi trường phát triển (Local) sang môi trường chạy thực tế (Production).

Khi đóng gói một ứng dụng Async chạy ẩn định kỳ (`httpx` + `APScheduler`), container cần đảm bảo 4 tiêu chí Production: **mới/nhẹ (slim)**, **chạy bằng user không có quyền root (security)**, **xử lý múi giờ chuẩn (để Cron chạy đúng giờ)** và **không tràn đĩa cứng vì log**.

---

## 1. Cấu trúc thư mục dự án chuẩn

Tổ chức các tệp tin trong dự án của bạn như sau:

```text
my-async-scraper/
├── app/
│   ├── __init__.py
│   └── main.py          # Mã nguồn httpx + APScheduler
├── data/                # Thư mục lưu dữ liệu/SQLite (nếu có)
├── logs/                # Thư mục lưu log
├── .dockerignore        # Loại bỏ các tệp không cần thiết khi build
├── .env                 # Khai báo biến môi trường
├── Dockerfile           # File cấu hình Build Docker Image
├── docker-compose.yml   # File điều phối Container
└── requirements.txt     # Danh sách thư viện Python

```

---

## 2. Tạo các file cấu hình

### A. File `.dockerignore`

Giúp giảm dung lượng Image và tăng tốc độ Build bằng cách bỏ qua các file thừa:

```text
__pycache__/
*.pyc
*.pyo
*.pyd
.git/
.gitignore
.venv/
env/
venv/
.env
data/*.db
logs/*.log

```

### B. File `requirements.txt`

```text
httpx>=0.27.0
apscheduler>=3.10.0
selectolax>=0.3.0
aiosqlite>=0.20.0
python-dotenv>=1.0.0

```

### C. File `Dockerfile` (Chuẩn Production & Bật Bảo mật)

```dockerfile
# 1. Sử dụng Python 3.11 Slim (nhẹ, chỉ ~150MB)
FROM python:3.11-slim

# 2. Cấu hình biến môi trường Python
# PYTHONUNBUFFERED=1: Đẩy log trực tiếp ra console ngay lập tức (không bị kẹt trong buffer)
# PYTHONDONTWRITEBYTECODE=1: Không tạo file .pyc
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Ho_Chi_Minh

# 3. Cài đặt các gói hệ thống cần thiết (bao gồm tzdata để chỉnh múi giờ)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. Tạo thư mục làm việc
WORKDIR /app

# 5. Copy requirements và cài đặt thư viện trước (Tối ưu Docker Layer Caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy mã nguồn ứng dụng
COPY app/ ./app/

# 7. TẠO USER KHÔNG PHẢI ROOT (Bảo mật container)
RUN useradd -m appuser && \
    mkdir -p /app/data /app/logs && \
    chown -R appuser:appuser /app
USER appuser

# 8. Lệnh khởi chạy ứng dụng
CMD ["python", "app/main.py"]

```

---

### D. File `docker-compose.yml` (Quản lý Service & Volumes)

```yaml
version: '3.8'

services:
  scraper-service:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: async_scraper_app
    restart: unless-stopped  # Tự động bật lại nếu server crash hoặc reboot
    
    # Đọc biến môi trường từ file .env
    env_file:
      - .env

    # Múi giờ Việt Nam cho Container
    environment:
      - TZ=Asia/Ho_Chi_Minh

    # Gắn ổ đĩa ra ngoài máy host để không bị mất dữ liệu/log khi xóa Container
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs

    # GIỚI HẠN LOG (Tránh việc file log phình to làm đầy ổ cứng Server)
    logging:
      driver: "json-file"
      options:
        max-size: "10m"   # Tối đa 10MB cho 1 file log
        max-file: "3"     # Lưu tối đa 3 file (tổng 30MB)

```

---

## 3. Cập nhật `app/main.py` để tương thích Docker & Graceful Shutdown

Khi Docker gửi lệnh dừng (`docker stop`), nó sẽ gửi tín hiệu `SIGTERM`. Chúng ta cần lập trình để `APScheduler` dừng một cách an toàn (chờ nốt job đang chạy xong mới tắt):

```python
import asyncio
import logging
import signal
import sys
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

async def run_scraper():
    logging.info("🚀 [JOB] Bắt đầu cào dữ liệu...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get("https://httpbin.org/get")
        logging.info(f"✅ [JOB] Hoàn thành, Status: {res.status_code}")

async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_scraper,
        trigger=IntervalTrigger(seconds=60),
        id="scraper_job",
        max_instances=1,
        coalesce=True
    )
    
    scheduler.start()
    logging.info("🐳 Container Async Scraper đã sẵn sàng!")

    # Lắng nghe tín hiệu SIGTERM / SIGINT từ Docker để Shutdown an toàn
    stop_event = asyncio.Event()

    def shutdown_handler(sig, frame):
        logging.info(f"🛑 Nhận tín hiệu {sig}. Đang đóng Scheduler an toàn...")
        scheduler.shutdown(wait=True)
        stop_event.set()

    # Bắt tín hiệu ngắt từ Docker
    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    # Đợi cho đến khi nhận tín hiệu tắt
    while not stop_event.is_set():
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())

```

---

## 4. Các lệnh điều khiển Docker

### Khởi chạy ứng dụng ở chế độ ngầm (Background / Detached):

```bash
docker compose up -d --build

```

### Xem Log thời gian thực (Real-time logs):

```bash
docker compose logs -f scraper-service

```

### Kiểm tra trạng thái Container:

```bash
docker compose ps

```

### Dừng ứng dụng an toàn:

```bash
docker compose down

```

---

## 💡 Checklist Kiểm tra Môi trường Production

1. **Múi giờ (Timezone):** `TZ=Asia/Ho_Chi_Minh` đã được cấu hình ở cả `Dockerfile` và `docker-compose.yml`. Điều này giúp các lệnh `CronTrigger(hour=8)` chạy đúng 8 giờ sáng giờ Việt Nam thay vì UTC.
2. **Loại bỏ Root User:** Trong Dockerfile đã dùng `USER appuser`. Việc này ngăn chặn hacker chiếm quyền điều khiển server nếu ứng dụng có lỗ hổng.
3. **Quản lý dung lượng Log:** Đã có cấu hình `logging.options` giới hạn tối đa 30MB log trong `docker-compose.yml`.