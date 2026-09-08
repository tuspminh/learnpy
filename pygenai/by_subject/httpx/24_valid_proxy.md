Để thêm chức năng **Valid Proxy** (chỉ lấy những Proxy còn sống/chưa bị block) cho bản **Sync**, chúng ta sẽ cải tiến lớp `ProxyRotator` bằng cách tích hợp cơ chế **Health Check (Kiểm tra sức khỏe Proxy)** theo chu kỳ và quản lý danh sách Proxy khả dụng (Active Pool).

---

## 🏛️ Đặt vấn đề & Thiết kế

1. **Khái niệm Health Check:** Trước khi cấp Proxy cho `Fetcher`, hệ thống sẽ kiểm tra xem Proxy đó có kết nối được tới internet (hoặc domain cào truyện) không.
2. **Loại bỏ Proxy chết:** Nếu Proxy không phản hồi trong khoảng `timeout` cho phép hoặc trả về mã lỗi, Proxy đó sẽ bị tạm thời hoặc vĩnh viễn xóa khỏi danh sách Active.
3. **Cơ chế Cache/Background Validation:** Để tránh việc request nào cũng phải chờ check Proxy (gây chậm ứng dụng), chúng ta sẽ giữ danh sách `working_proxies` và có hàm re-validate theo chu kỳ hoặc tự động loại bỏ Proxy ngay khi `Fetcher` báo lỗi.

---

## 1. Cập nhật Domain Layer (`domain.py`)

Cập nhật `Proxy` Value Object và nâng cấp `IProxyRotator` thêm method validate.

```python
import time
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

@dataclass(frozen=True)
class Proxy:
    url: str  # Ví dụ: "http://user:pass@1.2.3.4:8080"

    def __str__(self) -> str:
        return self.url

# --- Domain Interface cho Validated Proxy Rotator ---
class IProxyRotator(ABC):
    @abstractmethod
    def get_valid_proxy((self) -> Optional[Proxy]:
        """Chỉ trả về Proxy còn sống"""
        pass

    @abstractmethod
    def mark_bad(self, proxy: Proxy) -> None:
        """Đánh dấu Proxy bị lỗi/chết để loại bỏ khỏi danh sách"""
        pass

    @abstractmethod
    def validate_all(self) -> int:
        """Kiểm tra toàn bộ danh sách và lọc ra các Proxy còn sống"""
        pass

```

---

## 2. Cài đặt Health Check Proxy Rotator (`infrastructure.py`)

Viết lớp `ValidatingProxyRotator` sử dụng `httpx.Client` để kiểm tra Proxy.

```python
import logging
import random
import time
from typing import List, Optional
import httpx

from domain import IProxyRotator, Proxy

logger = logging.getLogger(__name__)

class ValidatingProxyRotator(IProxyRotator):
    """
    Proxy Rotator thông minh cho bản Sync:
    - Chỉ phân phối các Proxy đã được kiểm tra còn sống (Valid).
    - Tự động loại bỏ Proxy khi Fetcher đánh dấu là lỗi (mark_bad).
    - Hỗ trợ validate toàn bộ danh sách Proxy theo yêu cầu.
    """
    def __init__(
        self, 
        proxies: List[Proxy], 
        check_url: str = "https://httpbin.org/ip", # Hoặc URL trang truyện target
        check_timeout: float = 3.0
    ):
        self._all_proxies: List[Proxy] = list(proxies)
        self._active_proxies: List[Proxy] = []
        self._check_url = check_url
        self._check_timeout = check_timeout

        # Thực hiện kiểm tra lần đầu khi khởi tạo
        logger.info("🔍 Đang kiểm tra danh sách Proxy ban đầu...")
        self.validate_all()

    def is_proxy_alive(self, proxy: Proxy) -> bool:
        """Kiểm tra 1 Proxy có kết nối thành công hay không"""
        try:
            with httpx.Client(proxy=str(proxy), timeout=self._check_timeout) as client:
                res = client.get(self._check_url)
                return res.status_code == 200
        except Exception:
            return False

    def validate_all(self) -> int:
        """Lọc và cập nhật lại danh sách Active Proxies"""
        alive_list = []
        for p in self._all_proxies:
            if self.is_proxy_alive(p):
                alive_list.append(p)
                logger.info(f"✅ Proxy ALIVE: {p}")
            else:
                logger.warning(f"❌ Proxy DEAD/BLOCKED: {p}")
        
        self._active_proxies = alive_list
        logger.info(f"📊 Tổng kết: {len(self._active_proxies)}/{len(self._all_proxies)} Proxy còn hoạt động.")
        return len(self._active_proxies)

    def get_valid_proxy(self) -> Optional[Proxy]:
        """Lấy ngẫu nhiên 1 Proxy còn sống từ danh sách Active"""
        if not self._active_proxies:
            logger.warning("⚠️ Không còn Proxy nào còn sống trong Active Pool!")
            return None
        return random.choice(self._active_proxies)

    def mark_bad(self, proxy: Proxy) -> None:
        """Xóa Proxy khỏi Active Pool ngay lập tức khi Fetcher báo lỗi"""
        if proxy in self._active_proxies:
            self._active_proxies.remove(proxy)
            logger.warning(f"🗑️ Đã loại bỏ Proxy hỏng khỏi Pool: {proxy} (Còn lại: {len(self._active_proxies)})")

```

---

## 3. Cập nhật `HttpxSyncFetcher` để báo xấu Proxy (`infrastructure.py`)

Sửa đổi `HttpxSyncFetcher` để khi gặp lỗi kết nối hoặc HTTP 429/503, nó sẽ gọi `proxy_rotator.mark_bad(proxy)` để loại bỏ ngay Proxy đó ra khỏi danh sách.

```python
class HttpxSyncFetcher(IFetcher):
    RETRYABLE_STATUS_CODES = {429, 502, 503, 504}

    def __init__(
        self,
        ua_rotator: IUserAgentRotator,
        proxy_rotator: Optional[IProxyRotator] = None,
        app_max_retries: int = 3,
        transport_retries: int = 1,
    ):
        self._ua_rotator = ua_rotator
        self._proxy_rotator = proxy_rotator
        self._app_max_retries = app_max_retries

        self._transport = httpx.HTTPTransport(retries=transport_retries)
        self._client = httpx.Client(transport=self._transport, follow_redirects=True)

    def fetch(self, spec: RequestSpec) -> ResponseData:
        last_exception: Optional[Exception] = None

        for attempt in range(1, self._app_max_retries + 1):
            # Lấy PROXY CÒN SỐNG từ Rotator
            proxy = self._proxy_rotator.get_valid_proxy() if self._proxy_rotator else None
            headers = self._build_headers(spec.headers)
            proxy_str = str(proxy) if proxy else None

            logger.info(f"[Attempt {attempt}/{self._app_max_retries}] Fetching: {spec.url} | Proxy: {proxy_str or 'Direct'}")

            try:
                response = self._client.request(
                    method=spec.method,
                    url=spec.url,
                    params=spec.params,
                    data=spec.data,
                    headers=headers,
                    timeout=spec.timeout,
                    proxy=proxy_str
                )

                # Bị Anti-bot / Quá tải -> Báo xấu Proxy này và Retry
                if response.status_code in self.RETRYABLE_STATUS_CODES:
                    logger.warning(f"⚠️ Proxy {proxy_str} bị trả về HTTP {response.status_code}.")
                    if proxy and self._proxy_rotator:
                        self._proxy_rotator.mark_bad(proxy) # Đánh dấu Proxy chết/bị block
                    
                    last_exception = httpx.HTTPStatusError("Retryable error", request=response.request, response=response)
                    continue

                response.raise_for_status()

                return ResponseData(
                    url=str(response.url),
                    status_code=response.status_code,
                    text=response.text,
                    headers=dict(response.headers)
                )

            except (httpx.NetworkError, httpx.TimeoutException) as e:
                logger.warning(f"❌ Proxy {proxy_str} gặp lỗi mạng/timeout.")
                if proxy and self._proxy_rotator:
                    self._proxy_rotator.mark_bad(proxy) # Đánh dấu loại bỏ Proxy lỗi mạng
                last_exception = e

        raise MaxRetriesExceededException(f"Thất bại sau {self._app_max_retries} lần đổi Proxy cho URL: {spec.url}")

```

---

## 4. Chạy thực tế (`main.py`)

```python
from domain import RequestSpec, Proxy
from infrastructure import RandomUserAgentRotator, ValidatingProxyRotator, HttpxSyncFetcher

PROXIES = [
    Proxy("http://103.152.112.162:80"),     # Ví dụ Proxy sống
    Proxy("http://1.1.1.1:8080"),           # Ví dụ Proxy chết
    Proxy("http://192.168.1.1:8080"),       # Ví dụ Proxy chết
]

USER_AGENTS = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0"]

def main():
    ua_rotator = RandomUserAgentRotator(USER_AGENTS)
    
    # Khởi tạo ValidatingProxyRotator (Sẽ tự động lọc proxy sống ngay lúc tạo)
    proxy_rotator = ValidatingProxyRotator(
        proxies=PROXIES,
        check_url="https://quotes.toscrape.com", # URL trang cào thực tế
        check_timeout=3.0
    )

    with HttpxSyncFetcher(ua_rotator=ua_rotator, proxy_rotator=proxy_rotator) as fetcher:
        spec = RequestSpec(url="https://quotes.toscrape.com/page/1/")
        try:
            res = fetcher.fetch(spec)
            print(f"✅ Fetch thành công: {res.status_code}")
        except Exception as e:
            print(f"❌ Fetch thất bại: {e}")

if __name__ == "__main__":
    main()

```