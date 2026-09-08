Dưới đây là phiên bản cập nhật cho `HttpxSyncFetcher`. Bản cập nhật này sử dụng **`httpx.HTTPTransport(retries=...)`** ở tầng giao vận để tự động thử lại các lỗi giật lag kết nối cấp thấp (như `ConnectError`, `ReadTimeout`), đồng thời kết hợp **cơ chế Retry ở tầng Application** để bắt các mã lỗi HTTP Anti-Bot (`429 Too Many Requests`, `502`, `503`, `504`) nhằm xoay đổi Proxy và User-Agent mới ngay lập tức.

---

## Code hoàn chỉnh kết hợp 2 tầng Retry (`infrastructure.py`)

```python
import logging
import random
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


class HttpxSyncFetcher(IFetcher):
    """
    Fetcher đồng bộ kết hợp 2 tầng Retry:
    - Tầng 1 (Transport Layer): HTTPTransport tự xử lý lỗi rớt mạng socket/connection.
    - Tầng 2 (Application Layer): Xử lý HTTP Status code (429, 502, 503, 504) và xoay Proxy/UA mới.
    """
    # Các mã HTTP trigger việc xoay Proxy/Header và retry
    RETRYABLE_STATUS_CODES = {429, 502, 503, 504}

    def __init__(
        self,
        ua_rotator: IUserAgentRotator,
        proxy_rotator: Optional[IProxyRotator] = None,
        app_max_retries: int = 3,       # Số lần retry ở tầng Application (Xoay Proxy/Header)
        transport_retries: int = 1,     # Số lần retry ở tầng Transport (Lỗi mạng socket)
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

        # 1. Cấu hình HTTPTransport với tính năng retries tầng mạng tích hợp sẵn của httpx
        self._transport = httpx.HTTPTransport(
            retries=transport_retries,
            limits=limits
        )

        # 2. Khởi tạo httpx.Client sử dụng transport tùy chỉnh
        self._client = httpx.Client(
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

    def fetch(self, spec: RequestSpec) -> ResponseData:
        last_exception: Optional[Exception] = None

        # Vòng lặp Retry tầng Application (Xoay Proxy / User-Agent)
        for attempt in range(1, self._app_max_retries + 1):
            proxy = self._proxy_rotator.get_random_proxy() if self._proxy_rotator else None
            headers = self._build_headers(spec.headers)
            proxy_str = str(proxy) if proxy else None

            logger.info(
                f"[Attempt {attempt}/{self._app_max_retries}] Fetching: {spec.url} "
                f"| Proxy: {proxy_str or 'Direct'}"
            )

            try:
                # Gửi request đi (Nếu gặp lỗi socket nhẹ, HTTPTransport sẽ tự retry tại chỗ)
                response = self._client.request(
                    method=spec.method,
                    url=spec.url,
                    params=spec.params,
                    data=spec.data,
                    headers=headers,
                    timeout=spec.timeout,
                    proxy=proxy_str
                )

                # Bắt các status code bị chặn / quá tải (429, 502, 503, 504)
                if response.status_code in self.RETRYABLE_STATUS_CODES:
                    logger.warning(
                        f"⚠️ Phát hiện HTTP {response.status_code} ({response.reason_phrase}) tại {spec.url}. "
                        f"Chuẩn bị xoay Proxy/UA để thử lại..."
                    )
                    last_exception = httpx.HTTPStatusError(
                        message=f"Server returned status {response.status_code}",
                        request=response.request,
                        response=response
                    )
                    continue  # Chuyển sang lượt thử tiếp theo để đổi Proxy/User-Agent

                # Kiểm tra các lỗi 4xx/5xx còn lại (ví dụ: 404 Not Found sẽ không retry)
                response.raise_for_status()

                return ResponseData(
                    url=str(response.url),
                    status_code=response.status_code,
                    text=response.text,
                    headers=dict(response.headers)
                )

            except (httpx.NetworkError, httpx.TimeoutException) as e:
                # Lỗi mạng mà HTTPTransport cũng không cứu được sau transport_retries lần
                logger.warning(f"❌ Lỗi mạng/Timeout ở lần thử {attempt}: {type(e).__name__} - {e}")
                last_exception = e

            except httpx.HTTPStatusError as e:
                # Các lỗi 4xx/5xx không nằm trong danh sách RETRYABLE_STATUS_CODES
                logger.error(f"🚫 Lỗi HTTP không thể retry ({e.response.status_code}) tại {spec.url}")
                raise e

        # Nếu chạy hết số lần app_max_retries mà vẫn không thành công
        raise MaxRetriesExceededException(
            f"Thất bại sau {self._app_max_retries} lần đổi Proxy/UA cho URL: {spec.url}. "
            f"Lỗi cuối cùng: {last_exception}"
        ) from last_exception

    def close(self) -> None:
        logger.info("Đóng Connection Pool và HTTPTransport.")
        self._client.close()

```

---

## 🎯 Luồng hoạt động của hệ thống sau khi cải tiến

1. **Khi gặp sự cố rớt mạng nhỏ (`ConnectError`, `ReadTimeout`):**
* **`HTTPTransport`** xử lý trước: Tự động thử lại `transport_retries` lần ngay lập tức trên cùng một connection mà không cần chạy lại toàn bộ logic trong hàm `fetch()`.


2. **Khi gặp Anti-bot hoặc Quá tải (`429 Too Many Requests`, `503 Service Unavailable`):**
* `HTTPTransport` cho qua vì response vẫn trả về bình thường.
* **`HttpxSyncFetcher`** bắt mã `429/503`, nhảy sang vòng lặp tiếp theo `attempt + 1`.
* Lấy **Proxy mới** từ `proxy_rotator` và **User-Agent mới** từ `ua_rotator` để tiếp tục gửi lại request.