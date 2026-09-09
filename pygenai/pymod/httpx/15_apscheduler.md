Khi kết hợp **`httpx` async** với tác vụ lập lịch, lựa chọn hoàn hảo nhất là thư viện **`APScheduler`** (Advanced Python Scheduler), cụ thể là class **`AsyncIOScheduler`**.

`AsyncIOScheduler` cho phép các hàm `async def` (như script scraper của bạn) chạy trực tiếp trên cùng một **asyncio Event Loop** mà không cần mở thread/process mới và không gây tốn tài nguyên hệ thống.

---

## 1. Cài đặt thư viện

```bash
pip install apscheduler httpx

```

---

## 2. Script lập lịch cào dữ liệu hoàn chỉnh

Dưới đây là một ví dụ hoàn chỉnh triển khai lập lịch cào dữ liệu định kỳ bằng `AsyncIOScheduler`:

```python
import asyncio
import logging
from datetime import datetime
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

# Cấu hình Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

# 1. Hàm Scraper Asynchronous (Job sẽ được gọi định kỳ)
async def scrape_job():
    logging.info("⏰ [JOB STARTED] Bắt đầu lượt cào dữ liệu mới...")
    start_time = datetime.now()
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://quotes.toscrape.com/page/1/")
            response.raise_for_status()
            
            # Logic bóc tách HTML & lưu DB viết tại đây...
            logging.info(f"✅ [JOB SUCCESS] Cào dữ liệu thành công! Length: {len(response.text)} bytes")

    except httpx.HTTPError as exc:
        logging.error(f"❌ [JOB FAILED] Lỗi HTTP: {exc}")
    except Exception as exc:
        logging.error(f"❌ [JOB FAILED] Lỗi hệ thống: {exc}")
    finally:
        elapsed = (datetime.now() - start_time).total_seconds()
        logging.info(f"⏱️ Lượt cào hoàn tất trong {elapsed:.2f} giây.")

# 2. Hàm khởi chạy Scheduler
async def main():
    # Khởi tạo AsyncIOScheduler dành riêng cho asyncio
    scheduler = AsyncIOScheduler()

    # -------------------------------------------------------------
    # CÁCH 1: Lập lịch theo khoảng thời gian (Interval)
    # Ví dụ: Chạy 30 giây một lần
    # -------------------------------------------------------------
    scheduler.add_job(
        scrape_job,
        trigger=IntervalTrigger(seconds=30),  # minutes=5, hours=1...
        id="scraper_interval_job",
        name="Cào dữ liệu định kỳ mỗi 30s",
        max_instances=1,  # CHỐNG ĐÈ JOB: Lượt cũ chưa chạy xong thì lượt mới tạm bỏ qua
        coalesce=True     # Nếu bị lỡ nhiều lượt, chỉ chạy 1 lượt đại diện gần nhất
    )

    # -------------------------------------------------------------
    # CÁCH 2: Lập lịch theo giờ cố định (Cron style)
    # Ví dụ: Chạy lúc 08:00 sáng mỗi ngày
    # -------------------------------------------------------------
    # scheduler.add_job(
    #     scrape_job,
    #     trigger=CronTrigger(hour=8, minute=0),
    #     id="scraper_cron_job",
    #     max_instances=1
    # )

    # Khởi động scheduler
    scheduler.start()
    logging.info("🚀 AsyncIOScheduler đã khởi chạy thành công!")
    logging.info("📌 Nhấn Ctrl+C để dừng chương trình.\n")

    # Giữ Event Loop chạy vô hạn để Scheduler tiếp tục hoạt động
    try:
        while True:
            await asyncio.sleep(3600)  # Chờ 1 tiếng mỗi vòng lặp để duy trì app
    except (KeyboardInterrupt, SystemExit):
        logging.info("\n🛑 Đang dừng Scheduler...")
        scheduler.shutdown()
        logging.info("✅ Dừng chương trình an toàn!")

if __name__ == "__main__":
    asyncio.run(main())

```

---

## 🛠️ 3 Cấu hình "Sống còn" khi lập lịch Scraper

Khi chạy Scraper tự động trên môi trường Production, bạn nhất định phải bật 3 cấu hình sau trong `add_job`:

### 1. Giới hạn instance (`max_instances=1`)

* **Vấn đề:** Giả sử bạn đặt lịch cào 1 phút/lần. Tuy nhiên, mạng bị chậm khiến lượt cào thứ nhất mất **90 giây**. Nếu không có `max_instances=1`, lượt cào thứ hai sẽ nhảy vào chạy song song, gây quá tải bộ nhớ và dễ bị server chặn IP.
* **Giải pháp:** `max_instances=1` đảm bảo chỉ có **duy nhất 1 phiên scraper** được chạy tại một thời điểm.

### 2. Bỏ qua các job bị bỏ lỡ (`coalesce=True`)

* **Vấn đề:** Khi máy chủ bị mất mạng hoặc sập vài tiếng, khi bật lại, APScheduler có thể sẽ dồn dập "bù lại" hàng chục request bị lỡ cùng một lúc.
* **Giải pháp:** `coalesce=True` báo cho APScheduler biết: *"Nếu lỡ nhiều lượt, chỉ gộp lại và chạy 1 lượt gần nhất"*.

### 3. Bắt lỗi ngoại lệ (Exception Handling) bên trong Job

* Luôn bọc toàn bộ mã cào dữ liệu trong khối `try...except`. Nếu một lượt cào bị crash do lỗi mạng, ngoại lệ sẽ được xử lý gọn gàng và không làm ngắt luôn cả chương trình Scheduler.

---

## 💡 Triển khai lên Production (Chạy ẩn 24/7)

Để script chạy liên tục trên Server Linux (Ubuntu/Debian) ngay cả khi bạn tắt cửa sổ Terminal:

### Dùng `systemd` Service (Khuyên dùng)

Tạo file service tại `/etc/systemd/system/scraper.service`:

```ini
[Unit]
Description=Async Scraper Scheduler Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/your/app
ExecStart=/path/to/your/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

```

Sau đó kích hoạt service:

```bash
sudo systemctl daemon-reload
sudo systemctl start scraper
sudo systemctl enable scraper  # Khởi động cùng hệ thống

```