Vai trò này tôi đã lưu vào bộ nhớ và đang duy trì xuyên suốt toàn bộ hành trình — tiếp tục áp dụng đầy đủ như bạn yêu cầu. Vào bài 22.

### 📘 Bài 22: Async/await — Lập trình bất đồng bộ

Đây là một trong những chủ đề **khó nhất về tư duy** nhưng cũng **quan trọng nhất** trong Python hiện đại — nền tảng của các framework web tốc độ cao (FastAPI), bot Discord/Telegram, và mọi hệ thống cần xử lý hàng nghìn request đồng thời mà không "tắc nghẽn".

---

#### 1. Vấn đề cốt lõi: Tại sao code tuần tự (synchronous) không đủ nhanh?

python

```python
import time
import requests

def lay_du_lieu(url):
    print(f"Bắt đầu gọi {url}")
    response = requests.get(url)
    print(f"Xong {url}")
    return response

bat_dau = time.time()
lay_du_lieu("https://api1.example.com")   # giả sử mất 2 giây
lay_du_lieu("https://api2.example.com")   # giả sử mất 2 giây
lay_du_lieu("https://api3.example.com")   # giả sử mất 2 giây
print(f"Tổng thời gian: {time.time() - bat_dau:.1f}s")   # ~6 giây - CHẠY TUẦN TỰ
```

**Vấn đề**: trong lúc chương trình *đang chờ* server API1 phản hồi (I/O wait), CPU của bạn **hoàn toàn rảnh rỗi**, không làm gì cả — nhưng code vẫn "đứng chờ" (blocking) mà không tận dụng thời gian rảnh đó để bắt đầu gọi API2. Với 3 request độc lập, thời gian tổng là **tổng của cả 3**, dù CPU chẳng bận gì trong lúc chờ mạng.

**Ý tưởng của bất đồng bộ (async)**: trong lúc chờ I/O (mạng, đọc file, truy vấn database), hãy để CPU "chuyển sang làm việc khác" thay vì đứng im chờ đợi — rồi quay lại xử lý tiếp khi dữ liệu đã sẵn sàng.

---

#### 2. Khái niệm nền tảng: I/O-bound vs CPU-bound

Đây là kiến thức bắt buộc phải phân biệt rõ trước khi quyết định có nên dùng async hay không:

| Loại tác vụ | Đặc điểm | Ví dụ | Async có giúp? |
| --- | --- | --- | --- |
| **I/O-bound** | CPU chờ tài nguyên bên ngoài (mạng, disk, DB) | Gọi API, đọc file, query database | ✅ Có — cải thiện rõ rệt |
| **CPU-bound** | CPU liên tục tính toán, không chờ gì cả | Tính toán số học nặng, xử lý ảnh, ML training | ❌ Không — cần `multiprocessing` thay thế |

**Nguyên tắc thực chiến quan trọng nhất của bài học này**: async **chỉ** hữu ích cho tác vụ I/O-bound. Nếu bài toán của bạn là tính toán nặng (CPU-bound), async không giúp gì — cần dùng đa luồng thực sự (`multiprocessing`), một chủ đề nâng cao hơn ngoài phạm vi bài này.

---

#### 3. `async def` và `await` — cú pháp cơ bản

python

```python
import asyncio

async def noi_xin_chao(ten, giay_cho):
    print(f"Bắt đầu chào {ten}")
    await asyncio.sleep(giay_cho)   # giả lập tác vụ I/O tốn thời gian (không dùng time.sleep!)
    print(f"Xong chào {ten}")
    return f"Đã chào {ten}"

async def main():
    ket_qua = await noi_xin_chao("An", 2)
    print(ket_qua)

asyncio.run(main())   # điểm khởi động BẮT BUỘC cho code async
```

**Các quy tắc cú pháp cần khắc sâu:**

- Hàm định nghĩa bằng `async def` gọi là **coroutine** — không chạy ngay khi gọi như hàm thường, mà tạo ra một "đối tượng có thể chờ" (awaitable)
- `await` dùng để "chờ" một coroutine khác hoàn thành, **chỉ dùng được bên trong hàm `async def`**
- `asyncio.run()` là điểm khởi động chương trình async — tạo ra "event loop" (vòng lặp sự kiện) để điều phối các coroutine
- **`asyncio.sleep()` khác hoàn toàn `time.sleep()`**: `asyncio.sleep()` "nhường" quyền điều khiển cho event loop trong lúc chờ (cho phép coroutine khác chạy), còn `time.sleep()` **block hoàn toàn**, làm mất hết ý nghĩa của async

python

```python
# ❌ SAI HOÀN TOÀN - dùng time.sleep() trong code async là lỗi phổ biến của người mới
async def sai_cach(ten):
    time.sleep(2)   # BLOCK toàn bộ event loop, các coroutine khác phải chờ - PHÁ VỠ mục đích của async!
```

---

#### 4. `asyncio.gather()` — chạy nhiều tác vụ ĐỒNG THỜI

Đây là nơi async thể hiện sức mạnh thực sự — quay lại ví dụ 3 API ở đầu bài:

python

```python
import asyncio

async def gia_lap_goi_api(ten_api, thoi_gian_cho):
    print(f"Bắt đầu gọi {ten_api}")
    await asyncio.sleep(thoi_gian_cho)   # giả lập chờ mạng
    print(f"Xong {ten_api}")
    return f"Dữ liệu từ {ten_api}"

async def main():
    bat_dau = asyncio.get_event_loop().time()

    # Chạy 3 tác vụ ĐỒNG THỜI, không tuần tự!
    ket_qua = await asyncio.gather(
        gia_lap_goi_api("API Thời tiết", 2),
        gia_lap_goi_api("API Tỷ giá", 2),
        gia_lap_goi_api("API Vận chuyển", 2),
    )

    print(ket_qua)
    print(f"Tổng thời gian: {asyncio.get_event_loop().time() - bat_dau:.1f}s")   # ~2s, KHÔNG PHẢI 6s!

asyncio.run(main())
```

**Kết quả**: dù mỗi tác vụ "mất" 2 giây, tổng thời gian chỉ **~2 giây** (không phải 6 giây) — vì cả 3 coroutine chạy **đồng thời**, cùng nhau "chờ" trong lúc CPU rảnh, thay vì xếp hàng chờ lần lượt. Đây chính là lợi ích cốt lõi mà async mang lại cho tác vụ I/O-bound.

---

#### 5. Ứng dụng thực tế — Gọi nhiều API cùng lúc với `aiohttp`

`requests` (Bài 19) là thư viện **đồng bộ (sync)** — không tương thích trực tiếp với `async/await`. Để gọi API bất đồng bộ thực sự, cần dùng `aiohttp`:

python

```python
# pip install aiohttp
import asyncio
import aiohttp

async def lay_thong_tin_github(session, username):
    url = f"https://api.github.com/users/{username}"
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
        if response.status == 200:
            du_lieu = await response.json()
            return {"username": username, "followers": du_lieu["followers"]}
        return {"username": username, "loi": f"Status {response.status}"}


async def main():
    danh_sach_user = ["torvalds", "gvanrossum", "octocat"]

    async with aiohttp.ClientSession() as session:
        # Tạo danh sách task, chạy ĐỒNG THỜI cho tất cả user
        tasks = [lay_thong_tin_github(session, user) for user in danh_sach_user]
        ket_qua = await asyncio.gather(*tasks)

    for r in ket_qua:
        print(r)

asyncio.run(main())
```

**So sánh hiệu năng thực tế**: nếu dùng `requests` đồng bộ để gọi 3 API GitHub tuần tự, mỗi request mất ~0.3s → tổng ~0.9s. Với `aiohttp` bất đồng bộ, cả 3 request được gửi **gần như cùng lúc** → tổng thời gian gần bằng thời gian của **request chậm nhất**, không phải tổng của tất cả. Với 100 request, sự khác biệt này trở nên cực kỳ rõ rệt — đây là lý do các hệ thống crawl dữ liệu, tích hợp nhiều API bên thứ ba luôn ưu tiên thiết kế bất đồng bộ.

---

#### 6. `asyncio.as_completed()` — xử lý kết quả ngay khi từng tác vụ hoàn thành

Khác với `gather()` (chờ TẤT CẢ xong rồi mới trả kết quả), `as_completed()` cho phép xử lý ngay khi từng tác vụ xong, không cần chờ cái chậm nhất:

python

```python
import asyncio

async def xu_ly_don_hang(ma_don, thoi_gian):
    await asyncio.sleep(thoi_gian)
    return f"Đơn {ma_don} xử lý xong sau {thoi_gian}s"

async def main():
    tasks = [
        xu_ly_don_hang("DH001", 3),
        xu_ly_don_hang("DH002", 1),
        xu_ly_don_hang("DH003", 2),
    ]

    for coroutine in asyncio.as_completed(tasks):
        ket_qua = await coroutine
        print(f"Nhận kết quả: {ket_qua}")   # in ra theo thứ tự HOÀN THÀNH, không phải thứ tự khai báo

asyncio.run(main())
# Nhận kết quả: Đơn DH002 xử lý xong sau 1s   <- xong trước vì nhanh nhất
# Nhận kết quả: Đơn DH003 xử lý xong sau 2s
# Nhận kết quả: Đơn DH001 xử lý xong sau 3s
```

**Ứng dụng thực tế**: khi xây dựng dashboard theo dõi trạng thái nhiều đơn hàng/tác vụ, bạn muốn hiển thị kết quả **ngay khi có**, không muốn màn hình "đứng im" chờ tác vụ chậm nhất xong rồi mới hiện tất cả cùng lúc.

---

#### 7. `asyncio.Semaphore` — giới hạn số tác vụ đồng thời

Nhớ lại Bài 19 (Rate Limiting) — khi gọi hàng trăm API cùng lúc, bạn có thể làm server bên thứ ba "quá tải" hoặc chạm giới hạn rate limit. `Semaphore` giới hạn số coroutine chạy đồng thời:

python

```python
import asyncio
import aiohttp

async def lay_du_lieu_co_gioi_han(session, url, semaphore):
    async with semaphore:   # chỉ cho phép N coroutine vào đây cùng lúc
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
            return await response.json()


async def main():
    danh_sach_url = [f"https://api.example.com/sp/{i}" for i in range(100)]
    semaphore = asyncio.Semaphore(10)   # tối đa 10 request đồng thời, dù có 100 URL

    async with aiohttp.ClientSession() as session:
        tasks = [lay_du_lieu_co_gioi_han(session, url, semaphore) for url in danh_sach_url]
        ket_qua = await asyncio.gather(*tasks, return_exceptions=True)   # không crash nếu 1 task lỗi

    return ket_qua
```

`return_exceptions=True` trong `gather()` là kỹ thuật quan trọng: nếu không dùng, **một** coroutine bị lỗi sẽ làm toàn bộ `gather()` raise exception ngay lập tức, hủy luôn kết quả của những coroutine khác đã chạy thành công — thường không phải hành vi mong muốn khi xử lý hàng loạt dữ liệu độc lập.

---

#### 8. Khi nào dùng async, khi nào KHÔNG cần?

**Nguyên tắc quyết định thực chiến:**

| Tình huống | Nên dùng async? |
| --- | --- |
| Script cá nhân, gọi 1-2 API, chạy 1 lần | Không cần — code đồng bộ đơn giản, dễ đọc hơn |
| Web server xử lý hàng nghìn request/giây (FastAPI) | Có — bắt buộc để đạt hiệu năng cao |
| Crawl dữ liệu từ hàng trăm nguồn cùng lúc | Có — lợi ích rất rõ rệt |
| Xử lý ảnh, tính toán ML nặng | Không — đây là CPU-bound, cần `multiprocessing` |
| CLI tool đơn giản, chạy tuần tự vài bước | Không cần — thêm async chỉ làm code phức tạp không cần thiết |

**Lời khuyên nhà nghề quan trọng**: async **tăng độ phức tạp** của code đáng kể (khó debug hơn, dễ quên `await`, dễ deadlock nếu dùng sai) — chỉ nên áp dụng khi bài toán *thực sự* cần xử lý nhiều I/O đồng thời với số lượng lớn. Đừng dùng async "vì nó cool" — hãy dùng khi có lý do hiệu năng rõ ràng.

---

#### 9. Ví dụ thực chiến tổng hợp — Hệ thống kiểm tra giá sản phẩm từ nhiều sàn TMĐT

python

```python
import asyncio
import aiohttp
import time

async def lay_gia_tu_san(session, ten_san, url, semaphore):
    async with semaphore:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as response:
                if response.status == 200:
                    du_lieu = await response.json()
                    return {"san": ten_san, "gia": du_lieu.get("gia"), "thanh_cong": True}
                return {"san": ten_san, "loi": f"Status {response.status}", "thanh_cong": False}
        except asyncio.TimeoutError:
            return {"san": ten_san, "loi": "Timeout", "thanh_cong": False}
        except aiohttp.ClientError as e:
            return {"san": ten_san, "loi": str(e), "thanh_cong": False}


async def so_sanh_gia_da_san(ma_san_pham: str) -> list[dict]:
    cac_san = {
        "Shopee": f"https://api-gia-lap.example.com/shopee/{ma_san_pham}",
        "Lazada": f"https://api-gia-lap.example.com/lazada/{ma_san_pham}",
        "Tiki": f"https://api-gia-lap.example.com/tiki/{ma_san_pham}",
    }

    semaphore = asyncio.Semaphore(5)

    async with aiohttp.ClientSession() as session:
        tasks = [
            lay_gia_tu_san(session, ten, url, semaphore)
            for ten, url in cac_san.items()
        ]
        ket_qua = await asyncio.gather(*tasks)

    return ket_qua


async def main():
    bat_dau = time.time()
    ket_qua = await so_sanh_gia_da_san("SP12345")

    print(f"Thời gian tổng: {time.time() - bat_dau:.2f}s")

    gia_hop_le = [r for r in ket_qua if r["thanh_cong"]]
    if gia_hop_le:
        re_nhat = min(gia_hop_le, key=lambda r: r["gia"])
        print(f"Sàn có giá rẻ nhất: {re_nhat['san']} - {re_nhat['gia']:,} VNĐ")

asyncio.run(main())
```

Đây chính là logic cốt lõi của các công cụ **so sánh giá tự động** (price comparison) thực tế — gọi đồng thời nhiều sàn TMĐT, không phải chờ lần lượt, giúp trả kết quả cho người dùng nhanh nhất có thể.

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_22.py`:

1. Viết hàm `async def gia_lap_xu_ly(ten_task, thoi_gian)` dùng `asyncio.sleep()` giả lập một tác vụ I/O
2. Viết chương trình chạy **5 task** với thời gian khác nhau (ví dụ 1s, 3s, 2s, 4s, 1.5s) bằng `asyncio.gather()`, đo tổng thời gian thực tế bằng module `time`, xác nhận tổng thời gian gần bằng **task chậm nhất** (4s), không phải tổng cả 5 task (11.5s)
3. Viết lại bài toán trên nhưng dùng vòng lặp `for` tuần tự thông thường (không async) để so sánh trực tiếp thời gian chạy — chứng minh bằng số liệu cụ thể lợi ích của async
4. Dùng `asyncio.as_completed()` để in ra kết quả từng task **ngay khi hoàn thành**, quan sát thứ tự in ra không giống thứ tự khai báo
5. Thử thách thêm: dùng `asyncio.Semaphore(2)` để giới hạn chỉ 2 task được "chạy" đồng thời trong số 5 task trên, quan sát tổng thời gian thay đổi thế nào so với không giới hạn (gợi ý: sẽ chậm hơn vì phải "xếp hàng" theo nhóm 2)

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 23: Clean Code, Type Hints, Best Practices** — bài học tổng hợp giúp code của bạn không chỉ *chạy đúng* mà còn *dễ đọc, dễ maintain, đạt chuẩn chuyên nghiệp* mà bất kỳ công ty công nghệ nào cũng yêu cầu khi review code.
