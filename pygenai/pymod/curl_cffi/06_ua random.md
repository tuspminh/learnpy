Để tránh bị hệ thống Anti-bot (Cloudflare, Akamai) phát hiện do gửi quá nhiều request trùng lặp một bộ nhận diện, bạn cần **ngẫu nhiên hóa (Rotate)** đồng thời 2 thành phần:

1. **`impersonate`**: Thay đổi dấu vết TLS Fingerprint/JA3 giữa các phiên bản Chrome, Safari, Edge.
2. **`User-Agent` & `Headers**`: Phải **khớp tuyệt đối** với phiên bản `impersonate` đã chọn. *(Lưu ý: Nếu chọn `impersonate="safari17_0"` nhưng lại gửi `User-Agent` của Chrome, hệ thống sẽ chặn ngay vì lỗi Header Anomaly)*.

---

### 1. Danh sách cấu hình chuẩn (Fingerprint Matrix)

Dưới đây là đoạn code xây dựng danh sách các bộ cấu hình (Browser Profiles) đã được đồng bộ chuẩn giữa TLS Fingerprint và HTTP Headers:

```python
import random
from curl_cffi import requests

# Bộ dữ liệu các profile trình duyệt chuẩn
BROWSER_PROFILES = [
    {
        "impersonate": "chrome120",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
        }
    },
    {
        "impersonate": "chrome119",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.8",
            "Sec-Ch-Ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
        }
    },
    {
        "impersonate": "safari17_0",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
        }
    },
    {
        "impersonate": "edge101",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Not/A)Brand";v="99", "Microsoft Edge";v="101", "Chromium";v="101"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
        }
    }
]

def get_random_profile():
    """Lấy ngẫu nhiên một bộ Fingerprint + Headers đồng bộ"""
    return random.choice(BROWSER_PROFILES)

```

---

### 2. Áp dụng Ngẫu nhiên hóa cho Request Đơn lẻ

Mỗi lần gửi request, chọn một profile ngẫu nhiên từ danh sách trên:

```python
import time

urls = [
    "https://httpbin.org/headers",
    "https://httpbin.org/user-agent",
    "https://nowsecure.nl"
]

for url in urls:
    # 1. Lấy profile ngẫu nhiên
    profile = get_random_profile()
    
    print(f"--> Đang gửi request với impersonate: {profile['impersonate']}")
    
    # 2. Gửi request
    response = requests.get(
        url,
        headers=profile["headers"],
        impersonate=profile["impersonate"]
    )
    
    print(f"Status: {response.status_code}")
    time.sleep(1)  # Nghỉ nhẹ giữa các request

```

---

### 3. Xoay Profile cho Bất đồng bộ (`AsyncSession`)

Nếu sử dụng cào dữ liệu song song hàng loạt với Async, bạn có thể truyền ngẫu nhiên profile cho từng công việc (task):

```python
import asyncio
from curl_cffi.requests import AsyncSession

async def fetch_url(url):
    profile = get_random_profile()
    
    async with AsyncSession(
        impersonate=profile["impersonate"],
        headers=profile["headers"]
    ) as session:
        res = await session.get(url)
        print(f"URL: {url} | Status: {res.status_code} | Impersonate: {profile['impersonate']}")

async def main():
    target_urls = [
        "https://httpbin.org/ip",
        "https://httpbin.org/headers",
        "https://httpbin.org/user-agent"
    ]
    
    tasks = [fetch_url(url) for url in target_urls]
    await asyncio.gather(*tasks)

asyncio.run(main())

```

---

### 💡 Nguyên tắc vàng để không bị giới hạn Request (Rate Limit)

1. **Không tạo `User-Agent` ngẫu nhiên bằng chuỗi rác:** Chỉ xoay vòng giữa các `User-Agent` thực tế và luôn khớp với tham số `impersonate`.
2. **Kết hợp với Proxy Rotation:** Xoay Fingerprint giúp tránh bị phát hiện là Bot, nhưng để vượt qua Rate Limit theo IP, bạn **bắt buộc phải xoay cả IP Proxy** song song với xoay Fingerprint.
3. **Thêm Delay ngẫu nhiên (Jitter):** Không bao giờ dùng `time.sleep(1)` cố định. Hãy dùng `time.sleep(random.uniform(1.5, 3.5))` để mô phỏng hành vi bấm chuột của người dùng thật.