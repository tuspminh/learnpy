Dưới đây là thiết kế và cài đặt hệ thống **Fetcher** cho ứng dụng cào truyện chữ bằng Python sử dụng **HTTPX (Sync)**, tuân thủ chặt chẽ các nguyên lý **SOLID** và kiến trúc **DDD (Domain-Driven Design)**.

---

## 🏛️ Đặt vấn đề & Mẫu kiến trúc (DDD)

Trong DDD, hệ thống của chúng ta được chia thành các tầng tách biệt:

1. **Domain Layer (Core):** Chứa Value Objects (`RequestSpec`, `ResponseData`, `Proxy`), Interfaces (`IFetcher`) và Exceptions. Tầng này độc lập hoàn toàn với thư viện bên ngoài.
2. **Infrastructure Layer:** Cài đặt thực tế sử dụng `httpx`, quản lý Connection Pool, Retry, Xoay vòng Header/Proxy.
3. **Application Layer:** Đóng vai trò làm Client/Use-case điều khiển Fetcher thông qua Interface.

---

## 💻 Mã nguồn triển khai chi tiết

### 1. Domain Layer (`domain.py`)

Khai báo Value Objects mang tính bất biến (Immutable), Domain Exceptions và Interface giao ước.

```python
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

# --- Exceptions ---
class FetcherException(Exception):
    """Lỗi gốc của Domain Fetcher"""
    pass

class MaxRetriesExceededException(FetcherException):
    """Vượt quá số lần thử lại"""
    pass

# --- Value Objects ---
@dataclass(frozen=True)
class Proxy:
    url: str  # Ví dụ: "http://user:pass@1.2.3.4:8080"

    def __str__(self) -> str:
        return self.url

@dataclass(frozen=True)
class RequestSpec:
    url: str
    method: str = "GET"
    params: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    timeout: float = 10.0

@dataclass(frozen=True)
class ResponseData:
    url: str
    status_code: int
    text: str
    headers: Dict[str, str]

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

# --- Interfaces (Dependency Inversion Principle - DIP) ---
class IUserAgentRotator(ABC):
    @abstractmethod
    def get_random_user_agent(self) -> str:
        pass

class IProxyRotator(ABC):
    @abstractmethod
    def get_random_proxy(self) -> Optional[Proxy]:
        pass

class IFetcher(ABC):
    @abstractmethod
    def fetch(self, spec: RequestSpec) -> ResponseData:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

```

---

## 2. Infrastructure Layer (`infrastructure.py`)

Cài đặt chi tiết các chiến lược Xoay vòng và HTTP Client với `httpx`.

```python
import random
import logging
from typing import List, Optional
import httpx

from domain import (
    IFetcher, 
    IUserAgentRotator, 
    IProxyRotator, 
    Proxy, 
    RequestSpec, 
    ResponseData, 
    MaxRetriesExceededException
)

logger = logging.getLogger(__name__)

# --- Implementations for Rotators ---
class RandomUserAgentRotator(IUserAgentRotator):
    def __init__(self, user_agents: List[str]):
        if not user_agents:
            raise ValueError("Danh sách User-Agent không được rỗng.")
        self._user_agents = user_agents

    def get_random_user_agent(self) -> str:
        return random.choice(self._user_agents)


class RandomProxyRotator(IProxyRotator):
    def __init__(self, proxies: List[Proxy]):
        self._proxies = proxies

    def get_random_proxy(self) -> Optional[Proxy]:
        if not self._proxies:
            return None
        return random.choice(self._proxies)


# --- HTTPX Sync Fetcher Implementation ---
class HttpxSyncFetcher(IFetcher):
    """
    Fetcher đồng bộ sử dụng httpx.Client làm Connection Pool.
    Hỗ trợ Context Manager, Retry, Xoay Proxy và Header cho ứng dụng cào truyện.
    """
    def __init__(
        self,
        ua_rotator: IUserAgentRotator,
        proxy_rotator: Optional[IProxyRotator] = None,
        max_retries: int = 3,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: float = 5.0
    ):
        self._ua_rotator = ua_rotator
        self._proxy_rotator = proxy_rotator
        self._max_retries = max_retries
        
        # Cấu hình Connection Pool cho httpx
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry
        )
        
        # httpx.Client làm vai trò Connection Pool Manager
        self._client = httpx.Client(limits=limits, follow_redirects=True)

    def _build_headers(self, custom_headers: Optional[dict]) -> dict:
        """Kết hợp Header mặc định, User-Agent xoay vòng và Header tùy chỉnh."""
        headers = {
            "User-Agent": self._ua_rotator.get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def fetch(self, spec: RequestSpec) -> ResponseData:
        last_exception: Optional[Exception] = None

        for attempt in range(1, self._max_retries + 1):
            proxy = self._proxy_rotator.get_random_proxy() if self._proxy_rotator else None
            headers = self._build_headers(spec.headers)
            proxy_str = str(proxy) if proxy else None

            logger.info(f"[Attempt {attempt}/{self._max_retries}] Fetching: {spec.url} | Proxy: {proxy_str or 'Direct'}")

            try:
                # Gửi request với proxy và header động cho lượt fetch này
                response = self._client.request(
                    method=spec.method,
                    url=spec.url,
                    params=spec.params,
                    data=spec.data,
                    headers=headers,
                    timeout=spec.timeout,
                    proxy=proxy_str
                )
                
                # Bắn lỗi nếu status 4xx/5xx để trigger cơ chế retry
                response.raise_for_status()

                return ResponseData(
                    url=str(response.url),
                    status_code=response.status_code,
                    text=response.text,
                    headers=dict(response.headers)
                )

            except (httpx.HTTPError, httpx.StreamError) as e:
                logger.warning(f"Lỗi khi cào trang {spec.url} (Lần thử {attempt}): {type(e).__name__} - {e}")
                last_exception = e

        raise MaxRetriesExceededException(
            f"Thất bại sau {self._max_retries} lần thử lại cho URL: {spec.url}. Lỗi cuối: {last_exception}"
        ) from last_exception

    def close(self) -> None:
        """Giải phóng Connection Pool"""
        logger.info("Đóng Connection Pool của HTTPX Client.")
        self._client.close()

```

---

## 3. Application Layer & Usage (`main.py`)

Ví dụ tích hợp Fetcher vào quy trình cào chương truyện chữ thực tế.

```python
import logging
from domain import RequestSpec, Proxy, MaxRetriesExceededException
from infrastructure import RandomUserAgentRotator, RandomProxyRotator, HttpxSyncFetcher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# 1. Khởi tạo dữ liệu giả lập cho Rotators
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0"
]

PROXIES = [
    Proxy("http://103.152.112.162:80"),
    Proxy("http://185.199.229.156:7492"),
]

def main():
    # Dependency Injection (DIP - SOLID)
    ua_rotator = RandomUserAgentRotator(USER_AGENTS)
    proxy_rotator = RandomProxyRotator(PROXIES)

    # Khởi tạo Fetcher với Context Manager (Cấu hình Connection Pool & Retry)
    with HttpxSyncFetcher(
        ua_rotator=ua_rotator,
        proxy_rotator=proxy_rotator,
        max_retries=3,
        max_connections=50,
        max_keepalive_connections=10
    ) as fetcher:

        # Danh sách các chương truyện chữ cần cào
        chapters_to_crawl = [
            "https://quotes.toscrape.com/page/1/",
            "https://quotes.toscrape.com/page/2/",
        ]

        for url in chapters_to_crawl:
            spec = RequestSpec(url=url, timeout=5.0)
            try:
                response = fetcher.fetch(spec)
                print(f"✅ Cào thành công {response.url} | Độ dài nội dung: {len(response.text)} chars")
            except MaxRetriesExceededException as e:
                print(f"❌ Cào thất bại hoàn toàn: {e}")

if __name__ == "__main__":
    main()

```

---

## 🔍 Phân tích nguyên lý SOLID & Thiết kế DDD

1. **Single Responsibility Principle (SRP):**
* `RandomUserAgentRotator`: Chỉ chịu trách nhiệm quản lý và chọn lọc User-Agent.
* `HttpxSyncFetcher`: Chỉ quản lý việc thực thi kết nối HTTP, Connection Pool và Retry logic.
* `RequestSpec` / `ResponseData`: Chỉ chứa dữ liệu request/response mà không chứa bất kỳ business logic nào.


2. **Open/Closed Principle (OCP):**
* Muốn đổi chiến lược chọn Proxy (như Proxy theo độ trễ thấp nhất - *Latency-based Proxy*)? Chỉ cần viết một class mới kế thừa `IProxyRotator` mà **không phải sửa một dòng mã nào** trong `HttpxSyncFetcher`.


3. **Liskov Substitution Principle (LSP):**
* Mọi class cài đặt `IUserAgentRotator` hay `IProxyRotator` đều có thể thay thế cho nhau một cách an toàn mà không làm hỏng Fetcher.


4. **Interface Segregation Principle (ISP):**
* Chia nhỏ các interface (`IUserAgentRotator`, `IProxyRotator`, `IFetcher`) thay vì gộp chung vào một interface khổng lồ.


5. **Dependency Inversion Principle (DIP):**
* `HttpxSyncFetcher` phụ thuộc vào **Interface Abstraction** (`IUserAgentRotator`, `IProxyRotator`), không phụ thuộc vào cụm code cài đặt chi tiết.


6. **Context Manager & Connection Pool:**
* Class `HttpxSyncFetcher` đóng vai trò Wrapper xung quanh `httpx.Client`. Việc dùng Context Manager (`with ... as fetcher:`) đảm bảo tài nguyên TCP Socket từ Connection Pool luôn được đóng an toàn khi hết scope chương trình.