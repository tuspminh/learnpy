Dưới đây là mã nguồn **Async Fetcher** được thiết kế lại hoàn chỉnh bằng **`httpx.AsyncClient`** kết hợp với **`asyncio`**, tuân thủ chuẩn **DDD** và **SOLID**.

Phiên bản này duy trì cơ chế **Retry 2 tầng**: Tầng Transport tự xử lý sự cố socket nhẹ và Tầng Application tự động **xoay Proxy / User-Agent** bất đồng bộ khi vấp phải các mã lỗi Anti-Bot/Server quá tải (`429`, `502`, `503`, `504`).

---

## 1. Domain Layer (`domain.py`)

Khai báo các Interface bất đồng bộ sử dụng từ khóa `async / await` và `AsyncContextManager`.

```python
from dataclasses import dataclass
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

# --- Interfaces (DIP - SOLID) ---
class IUserAgentRotator(ABC):
    @abstractmethod
    def get_random_user_agent(self) -> str:
        pass

class IProxyRotator(ABC):
    @abstractmethod
    def get_random_proxy(self) -> Optional[Proxy]:
        pass

class IAsyncFetcher(ABC):
    @abstractmethod
    async def fetch(self, spec: RequestSpec) -> ResponseData:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

```

---

## 2. Infrastructure Layer (`infrastructure.py`)

Sử dụng `httpx.AsyncHTTPTransport` và `httpx.AsyncClient` để xử lý I/O bất đồng bộ.

```python
import logging
import random
from typing import List, Optional
import httpx

from domain import (
    IAsyncFetcher, 
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


# --- HTTPX Async Fetcher Implementation ---
class HttpxAsyncFetcher(IAsyncFetcher):
    """
    Fetcher bất đồng bộ kết hợp 2 tầng Retry:
    - Tầng 1 (Transport Layer): AsyncHTTPTransport tự xử lý lỗi rớt mạng socket/connection.
    - Tầng 2 (Application Layer): Xử lý HTTP Status code (429, 502, 503, 504) và xoay Proxy/UA mới.
    """
    RETRYABLE_STATUS_CODES = {429, 502, 503, 504}

    def __init__(
        self,
        ua_rotator: IUserAgentRotator,
        proxy_rotator: Optional[IProxyRotator] = None,
        app_max_retries: int = 3,       # Retry tầng Application (Xoay Proxy/Header)
        transport_retries: int = 1,     # Retry tầng Transport (Giật lag socket nhẹ)
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: float = 5.0
    ):
        self._ua_rotator = ua_rotator
        self._proxy_rotator = proxy_rotator
        self._app_max_retries = app_max_retries

        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry
        )

        # 1. Cấu hình AsyncHTTPTransport với retries tầng mạng
        self._transport = httpx.AsyncHTTPTransport(
            retries=transport_retries,
            limits=limits
        )

        # 2. Khởi tạo httpx.AsyncClient
        self._client = httpx.AsyncClient(
            transport=self._transport,
            follow_redirects=True
        )

    def _build_headers(self, custom_headers: Optional[dict]) -> dict:
        headers = {
            "User-Agent": self._ua_rotator.get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        if custom_headers:
            headers.update(custom_headers)
        return headers

    async def fetch(self, spec: RequestSpec) -> ResponseData:
        last_exception: Optional[Exception] = None

        for attempt in range(1, self._app_max_retries + 1):
            proxy = self._proxy_rotator.get_random_proxy() if self._proxy_rotator else None
            headers = self._build_headers(spec.headers)
            proxy_str = str(proxy) if proxy else None

            logger.info(
                f"[Attempt {attempt}/{self._app_max_retries}] Fetching: {spec.url} "
                f"| Proxy: {proxy_str or 'Direct'}"
            )

            try:
                # Gửi async request
                response = await self._client.request(
                    method=spec.method,
                    url=spec.url,
                    params=spec.params,
                    data=spec.data,
                    headers=headers,
                    timeout=spec.timeout,
                    proxy=proxy_str
                )

                # Kiểm tra mã lỗi Anti-Bot / Quá tải server
                if response.status_code in self.RETRYABLE_STATUS_CODES:
                    logger.warning(
                        f"⚠️ Phát hiện HTTP {response.status_code} ({response.reason_phrase}) tại {spec.url}. "
                        f"Đang xoay Proxy/UA để thử lại..."
                    )
                    last_exception = httpx.HTTPStatusError(
                        message=f"Server returned status {response.status_code}",
                        request=response.request,
                        response=response
                    )
                    continue  # Nhảy sang vòng lặp tiếp theo để lấy Proxy/UA mới

                # Bắn lỗi nếu có HTTP Status 4xx/5xx khác (ví dụ 404 sẽ không retry)
                response.raise_for_status()

                return ResponseData(
                    url=str(response.url),
                    status_code=response.status_code,
                    text=response.text,
                    headers=dict(response.headers)
                )

            except (httpx.NetworkError, httpx.TimeoutException) as e:
                logger.warning(f"❌ Lỗi mạng Async ở lần thử {attempt}: {type(e).__name__} - {e}")
                last_exception = e

            except httpx.HTTPStatusError as e:
                logger.error(f"🚫 Lỗi HTTP không thể retry ({e.response.status_code}) tại {spec.url}")
                raise e

        raise MaxRetriesExceededException(
            f"Thất bại sau {self._app_max_retries} lần đổi Proxy/UA cho URL: {spec.url}. "
            f"Lỗi cuối cùng: {last_exception}"
        ) from last_exception

    async def close(self) -> None:
        logger.info("Đóng Connection Pool và AsyncHTTPTransport.")
        await self._client.aclose()

```

---

## 3. Application Layer (`main.py`)

Thực thi cào hàng loạt chương truyện đồng thời bằng **`asyncio.gather`** và **`asyncio.Semaphore`** (giới hạn số luồng cào đồng thời để tránh làm sập server target).

```python
import asyncio
import logging
from typing import List

from domain import RequestSpec, Proxy, MaxRetriesExceededException
from infrastructure import RandomUserAgentRotator, RandomProxyRotator, HttpxAsyncFetcher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0"
]

PROXIES = [
    Proxy("http://103.152.112.162:80"),
    Proxy("http://185.199.229.156:7492"),
]

async def crawl_chapter(fetcher: HttpxAsyncFetcher, semaphore: asyncio.Semaphore, url: str):
    """Hàm worker cào 1 chương truyện, giới hạn bởi Semaphore"""
    async with semaphore:
        spec = RequestSpec(url=url, timeout=5.0)
        try:
            response = await fetcher.fetch(spec)
            logger.info(f"✅ [SUCCESS] Cào xong {response.url} | Độ dài HTML: {len(response.text)}")
            return response
        except MaxRetriesExceededException as e:
            logger.error(f"❌ [FAILED] {e}")
            return None

async def main():
    ua_rotator = RandomUserAgentRotator(USER_AGENTS)
    proxy_rotator = RandomProxyRotator(PROXIES)

    # Khai báo Async Context Manager cho Fetcher
    async with HttpxAsyncFetcher(
        ua_rotator=ua_rotator,
        proxy_rotator=proxy_rotator,
        app_max_retries=3,
        transport_retries=1,
        max_connections=100,
        max_keepalive_connections=20
    ) as fetcher:

        # Giả lập danh sách 10 chương truyện chữ cần cào đồng thời
        chapter_urls = [f"https://quotes.toscrape.com/page/{i}/" for i in range(1, 11)]

        # Giới hạn tối đa 5 request diễn ra đồng thời tại một thời điểm
        semaphore = asyncio.Semaphore(5)

        # Tạo danh sách các async tasks
        tasks = [
            crawl_chapter(fetcher, semaphore, url) 
            for url in chapter_urls
        ]

        # Chạy bất đồng bộ toàn bộ các chương
        results = await asyncio.gather(*tasks)
        
        successful_crawls = [r for r in results if r is not None]
        print(f"\n🎉 Hoàn thành: {len(successful_crawls)}/{len(chapter_urls)} chương thành công!")

if __name__ == "__main__":
    asyncio.run(main())

```