Dưới đây là đoạn script Python hoàn chỉnh được tối ưu cho việc cào dữ liệu hàng loạt. Script tích hợp đầy đủ 3 cơ chế: **Xoay Proxy ngẫu nhiên**, **Xoay Fingerprint/Headers đồng bộ**, và **Tự động thử lại (Retry) với kĩ thuật Exponential Backoff** khi gặp các lỗi Rate Limit (429), Block (403), hoặc Timeout.

---

### Code Python Hoàn Chỉnh

```python
import time
import random
import logging
from typing import Optional, Dict, Any
from curl_cffi import requests
from curl_cffi.requests.exceptions import RequestException

# Cấu hình logging để theo dõi tiến trình
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

# 1. DANH SÁCH PROXY (Thay thế bằng danh sách Proxy thực tế của bạn)
PROXY_LIST = [
    # Format: "http://user:password@host:port" hoặc "socks5h://host:port"
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://proxy3.example.com:8080",
]

# 2. BỘ FINGERPRINT PROFILES (Đồng bộ chuẩn giữa impersonate và Headers)
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
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
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
    }
]

def get_random_proxy() -> Optional[Dict[str, str]]:
    """Lấy ngẫu nhiên một Proxy từ danh sách."""
    if not PROXY_LIST:
        return None
    proxy_url = random.choice(PROXY_LIST)
    return {"http": proxy_url, "https": proxy_url}

def get_random_profile() -> Dict[str, Any]:
    """Lấy ngẫu nhiên một bộ Browser Profile."""
    return random.choice(BROWSER_PROFILES)

def fetch_with_retry(
    url: str,
    max_retries: int = 4,
    backoff_factor: float = 2.0,
    timeout: int = 10
) -> Optional[requests.Response]:
    """
    Gửi HTTP request với cơ chế xoay IP, xoay Fingerprint và tự động Retry khi gặp lỗi.
    """
    retry_status_codes = {403, 429, 500, 502, 503, 504}

    for attempt in range(1, max_retries + 1):
        profile = get_random_profile()
        proxies = get_random_proxy()
        
        logging.info(
            f"[Lần thử {attempt}/{max_retries}] Request tới '{url}' | "
            f"Impersonate: {profile['impersonate']} | "
            f"Proxy: {proxies['http'] if proxies else 'Không dùng Proxy'}"
        )

        try:
            # Gửi request với curl_cffi
            response = requests.get(
                url,
                headers=profile["headers"],
                impersonate=profile["impersonate"],
                proxies=proxies,
                timeout=timeout
            )

            # Nếu thành công (200 OK)
            if response.status_code == 200:
                logging.info(f"==> Thành công! Status: 200 (Đã lấy {len(response.content)} bytes)")
                return response

            # Nếu gặp lỗi trong danh sách cần Retry (403, 429, 5xx)
            if response.status_code in retry_status_codes:
                logging.warning(f"==> Cảnh báo: Gặp HTTP Status {response.status_code}. Tiến hành thử lại...")
            else:
                logging.error(f"==> Lỗi không thể retry: Status {response.status_code}")
                return response

        except RequestException as e:
            logging.warning(f"==> Lỗi kết nối/Timeout: {e}. Tiến hành thử lại...")

        # Tính toán thời gian chờ tăng dần (Exponential Backoff + Random Jitter)
        if attempt < max_retries:
            sleep_time = (backoff_factor ** attempt) + random.uniform(0.5, 2.0)
            logging.info(f"Nghỉ {sleep_time:.2f} giây trước khi thử lại...")
            time.sleep(sleep_time)

    logging.error(f"==> Thất bại hoàn toàn sau {max_retries} lần thử cho URL: {url}")
    return None

# ==========================================
# THỰC THI THỬ NGHIỆM
# ==========================================
if __name__ == "__main__":
    # URL kiểm tra HTTP Headers/IP
    target_urls = [
        "https://httpbin.org/ip",
        "https://nowsecure.nl",  # Trang mẫu test Cloudflare
    ]

    for target in target_urls:
        print("\n" + "="*50)
        res = fetch_with_retry(url=target, max_retries=3)
        
        if res and res.status_code == 200:
            print(f"Kết quả trả về (300 ký tự đầu):\n{res.text[:300]}")
        else:
            print("Không thể lấy dữ liệu từ URL này.")
        
        # Thêm khoảng nghỉ ngẫu nhiên giữa các URL khác nhau
        time.sleep(random.uniform(1.5, 3.0))

```

---

### Điểm nổi bật của Script

1. **Exponential Backoff & Jitter**: Khi gặp lỗi 403/429, thời gian chờ giữa các lần thử lại sẽ tăng dần ($2^1$, $2^2$, $2^3$...) kết hợp với thời gian ngẫu nhiên (Jitter) để tránh việc tiếp tục bị máy chủ hạn chế do gửi lại quá nhanh.
2. **Xoay Proxy & Fingerprint độc lập mỗi lần Retry**: Khi một request bị block, ở lần retry tiếp theo, script sẽ **tự động đổi sang Proxy mới và Profile trình duyệt mới**, giúp vượt qua rào cản do IP cũ hoặc Fingerprint cũ bị cờ đỏ.
3. **Bắt lỗi kết nối linh hoạt**: Sử dụng `RequestException` từ `curl_cffi` để bắt trọn các lỗi nghẽn mạng, reset connection hoặc proxy timeout.