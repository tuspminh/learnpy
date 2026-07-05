Vai trò này tôi đã lưu vào bộ nhớ từ trước (bài 3) và đang duy trì xuyên suốt — tiếp tục áp dụng cho toàn bộ hành trình. Vào bài 19.

### 📘 Bài 19: Làm việc với API (requests, HTTP)

Đây là bài học mở ra khả năng **kết nối chương trình của bạn với thế giới bên ngoài** — gọi API thời tiết, thanh toán, bản đồ, hay chính API của các mô hình AI như Claude. Đây là kỹ năng cốt lõi của hầu hết ứng dụng phần mềm hiện đại năm 2026, vì gần như không hệ thống nào hoạt động độc lập hoàn toàn nữa.

---

#### 1. HTTP là gì — nền tảng bắt buộc phải hiểu trước khi code

Trước khi gõ dòng code đầu tiên, cần hiểu **giao thức HTTP (HyperText Transfer Protocol)** — cách các chương trình trên Internet "nói chuyện" với nhau theo mô hình **client-server**:

```
[Chương trình Python của bạn]  --- Request (yêu cầu) --->  [Server API]
[Chương trình Python của bạn]  <--- Response (phản hồi) ---  [Server API]
```

**Các phương thức HTTP (HTTP Methods) chính cần nắm:**

| Method | Ý nghĩa | Ví dụ thực tế |
| --- | --- | --- |
| `GET` | Lấy dữ liệu | Lấy thông tin thời tiết, xem danh sách sản phẩm |
| `POST` | Tạo dữ liệu mới | Tạo đơn hàng mới, đăng ký tài khoản |
| `PUT` / `PATCH` | Cập nhật dữ liệu | Sửa thông tin đơn hàng |
| `DELETE` | Xóa dữ liệu | Hủy đơn hàng |

**Mã trạng thái (Status Code)** — server luôn trả về một mã số cho biết kết quả xử lý:

| Mã  | Ý nghĩa | Nhóm |
| --- | --- | --- |
| `200` | Thành công (OK) | 2xx - Thành công |
| `201` | Tạo mới thành công (Created) | 2xx |
| `400` | Yêu cầu sai (Bad Request) | 4xx - Lỗi từ phía client |
| `401` | Chưa xác thực (Unauthorized) | 4xx |
| `404` | Không tìm thấy (Not Found) | 4xx |
| `429` | Gửi quá nhiều request (Too Many Requests) | 4xx |
| `500` | Lỗi server (Internal Server Error) | 5xx - Lỗi từ phía server |

Ghi nhớ nguyên tắc: **4xx = lỗi do bạn gửi sai, 5xx = lỗi do server** — đây là bước đầu tiên khi debug lỗi API trong thực tế.

---

#### 2. Gọi API đầu tiên với `requests`

python

```python
import requests

response = requests.get("https://api.github.com/users/octocat")

print(response.status_code)    # 200
print(response.headers["Content-Type"])   # application/json; charset=utf-8
print(response.text)            # chuỗi JSON thô (raw string)

du_lieu = response.json()       # chuyển JSON string thành dict Python - DÙNG NHIỀU NHẤT
print(du_lieu["name"])          # 'The Octocat'
print(du_lieu["public_repos"])  # số lượng repo
```

**Điểm quan trọng cần khắc sâu**: `response.json()` chính là lúc kiến thức **dict lồng nhau ở Bài 8** phát huy tác dụng đầy đủ — JSON response từ API thực tế hầu như luôn có cấu trúc dict/list lồng nhau nhiều tầng.

---

#### 3. Query Parameters — gửi tham số tìm kiếm qua URL

python

```python
import requests

# Cách viết thủ công - dễ lỗi khi có ký tự đặc biệt (dấu cách, ký tự Unicode)
url = "https://api.openweathermap.org/data/2.5/weather?q=Ho Chi Minh&appid=YOUR_KEY"

# Cách chuẩn chuyên nghiệp - dùng params, requests tự xử lý encode URL an toàn
response = requests.get(
    "https://api.openweathermap.org/data/2.5/weather",
    params={
        "q": "Ho Chi Minh City",
        "appid": "YOUR_API_KEY",
        "units": "metric"
    }
)

du_lieu = response.json()
print(f"Nhiệt độ: {du_lieu['main']['temp']}°C")
print(f"Mô tả: {du_lieu['weather'][0]['description']}")
```

Dùng `params=` thay vì tự nối chuỗi URL là **best practice bắt buộc** — vì `requests` tự động xử lý encode ký tự đặc biệt (dấu cách thành `%20`, tiếng Việt có dấu thành URL-safe...), tránh lỗi ngầm khó phát hiện.

---

#### 4. Headers — thông tin đi kèm request, đặc biệt là xác thực (Authentication)

Hầu hết API thực tế yêu cầu **xác thực** để biết ai đang gọi API — thường qua **API Key** hoặc **Bearer Token** gửi trong header:

python

```python
import requests

headers = {
    "Authorization": "Bearer sk-ant-xxxxxxxxxxxxx",   # dạng token phổ biến (ví dụ API của Claude)
    "Content-Type": "application/json"
}

response = requests.get("https://api.example.com/orders", headers=headers)
```

**⚠️ NGUYÊN TẮC AN TOÀN SỐNG CÒN** — không bao giờ viết API key trực tiếp trong code:

python

```python
# ❌ NGUY HIỂM - nếu code này push lên GitHub công khai, ai cũng lấy được key của bạn
API_KEY = "sk-ant-abc123xyz789"

# ✅ ĐÚNG - đọc key từ biến môi trường (environment variable)
import os
from dotenv import load_dotenv    # package python-dotenv đã cài ở Bài 18

load_dotenv()   # đọc file .env
API_KEY = os.getenv("ANTHROPIC_API_KEY")
```

File `.env` (nhớ lại `.gitignore` ở Bài 18 — file này **KHÔNG BAO GIỜ** được commit lên Git):

```
ANTHROPIC_API_KEY=sk-ant-abc123xyz789
WEATHER_API_KEY=abc123def456
```

Đây là quy trình bảo mật **bắt buộc tuyệt đối** trong mọi công ty công nghệ thực tế — lộ API key có thể dẫn đến bị lạm dụng, tính phí khống, hoặc rò rỉ dữ liệu nhạy cảm.

---

#### 5. Gửi dữ liệu với POST — tạo dữ liệu mới

python

```python
import requests

don_hang_moi = {
    "khach_hang": "Nguyễn Văn An",
    "san_pham": ["SP001", "SP002"],
    "tong_tien": 890000
}

response = requests.post(
    "https://api.myshop.com/orders",
    json=don_hang_moi,      # requests TỰ ĐỘNG chuyển dict -> JSON và set header Content-Type
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

if response.status_code == 201:
    ket_qua = response.json()
    print(f"Đơn hàng tạo thành công, mã: {ket_qua['ma_don']}")
else:
    print(f"Lỗi tạo đơn hàng: {response.status_code}")
```

**Lưu ý quan trọng**: dùng tham số `json=` (không phải `data=`) khi gửi dict — `requests` sẽ tự động serialize (chuyển đổi) dict thành chuỗi JSON và thiết lập header `Content-Type: application/json` chính xác. Nếu dùng `data=`, bạn phải tự làm những việc này thủ công.

---

#### 6. Xử lý lỗi khi gọi API — kết hợp trực tiếp kiến thức Bài 10

Gọi API trong thực tế **luôn** phải đối mặt với: mất mạng, server quá tải, response trả về dữ liệu bất ngờ. Đây là lúc `try/except` không còn là lý thuyết mà là **yêu cầu bắt buộc**:

python

```python
import requests

def lay_thong_tin_thoi_tiet(thanh_pho: str, api_key: str) -> dict | None:
    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": thanh_pho, "appid": api_key, "units": "metric"},
            timeout=5    # QUAN TRỌNG - không chờ vô hạn nếu server không phản hồi
        )
        response.raise_for_status()   # tự raise HTTPError nếu status_code là 4xx/5xx
        return response.json()

    except requests.exceptions.Timeout:
        print("Lỗi: Server phản hồi quá chậm, đã hết thời gian chờ")
    except requests.exceptions.ConnectionError:
        print("Lỗi: Không thể kết nối - kiểm tra internet hoặc URL")
    except requests.exceptions.HTTPError as e:
        print(f"Lỗi HTTP: {e}")
    except requests.exceptions.JSONDecodeError:
        print("Lỗi: Server trả về dữ liệu không phải JSON hợp lệ")

    return None


ket_qua = lay_thong_tin_thoi_tiet("Ho Chi Minh City", "YOUR_KEY")
if ket_qua:
    print(f"Nhiệt độ hiện tại: {ket_qua['main']['temp']}°C")
else:
    print("Không thể lấy dữ liệu thời tiết lúc này")
```

**Điểm mấu chốt cần khắc sâu — `timeout=5`**: nếu không đặt timeout, chương trình của bạn có thể **treo vô hạn** nếu server không phản hồi — đây là lỗi cực kỳ phổ biến trong hệ thống production, gây ra hiện tượng "server bị treo" dây chuyền khi một API bên thứ ba gặp sự cố. **Luôn luôn đặt timeout** khi gọi API trong code chuyên nghiệp, không có ngoại lệ.

**`raise_for_status()`** là kỹ thuật gọn gàng: tự động raise exception nếu status code là lỗi (4xx/5xx), giúp bạn không cần viết `if response.status_code != 200:` thủ công ở mọi nơi.

---

#### 7. Retry logic — xử lý lỗi tạm thời một cách chuyên nghiệp

Trong thực tế, lỗi mạng đôi khi chỉ là **tạm thời** (server quá tải nhất thời) — dev chuyên nghiệp thường thêm logic **thử lại (retry)**:

python

```python
import requests
import time

def goi_api_voi_retry(url: str, so_lan_thu_toi_da: int = 3, **kwargs) -> dict | None:
    for lan_thu in range(1, so_lan_thu_toi_da + 1):
        try:
            response = requests.get(url, timeout=5, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Lần thử {lan_thu}/{so_lan_thu_toi_da} thất bại: {e}")
            if lan_thu < so_lan_thu_toi_da:
                thoi_gian_cho = 2 ** lan_thu   # exponential backoff: 2s, 4s, 8s...
                print(f"Đợi {thoi_gian_cho}s rồi thử lại...")
                time.sleep(thoi_gian_cho)

    print("Đã thử hết số lần cho phép, bỏ cuộc")
    return None
```

Kỹ thuật **exponential backoff** (thời gian chờ tăng dần theo cấp số nhân giữa các lần thử) là chuẩn ngành khi gọi API bên thứ ba — tránh việc "spam" server đang gặp sự cố khiến tình hình tệ hơn, đồng thời tăng khả năng thành công nếu lỗi chỉ là tạm thời.

---

#### 8. Rate Limiting — tránh bị chặn vì gọi API quá nhiều

Hầu hết API thực tế (bao gồm API của Claude) đều giới hạn số request/phút. Khi vượt giới hạn, server trả về mã `429 Too Many Requests`:

python

```python
import requests
import time

def goi_api_ton_trong_rate_limit(url, headers, danh_sach_request):
    ket_qua = []
    for i, params in enumerate(danh_sach_request):
        response = requests.get(url, headers=headers, params=params, timeout=5)

        if response.status_code == 429:
            # Server thường trả về header "Retry-After" báo cần đợi bao lâu
            thoi_gian_cho = int(response.headers.get("Retry-After", 5))
            print(f"Bị rate limit, đợi {thoi_gian_cho}s...")
            time.sleep(thoi_gian_cho)
            response = requests.get(url, headers=headers, params=params, timeout=5)

        ket_qua.append(response.json())
        time.sleep(0.5)   # chủ động giãn cách giữa các request để tránh chạm giới hạn

    return ket_qua
```

---

#### 9. Ví dụ thực chiến tổng hợp — Module tích hợp API thời tiết cho hệ thống logistics

python

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def kiem_tra_thoi_tiet_giao_hang(danh_sach_thanh_pho: list[str]) -> dict:
    """
    Kiểm tra thời tiết cho nhiều thành phố cùng lúc để quyết định
    lịch giao hàng - ứng dụng thực tế trong ngành logistics.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    ket_qua = {}

    for thanh_pho in danh_sach_thanh_pho:
        try:
            response = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": thanh_pho, "appid": api_key, "units": "metric"},
                timeout=5
            )
            response.raise_for_status()
            du_lieu = response.json()

            co_mua = any(
                "rain" in thoi_tiet["main"].lower()
                for thoi_tiet in du_lieu["weather"]
            )

            ket_qua[thanh_pho] = {
                "nhiet_do": du_lieu["main"]["temp"],
                "co_mua": co_mua,
                "canh_bao_giao_hang": "Nên hoãn giao hàng" if co_mua else "An toàn giao hàng"
            }

        except requests.exceptions.RequestException as e:
            ket_qua[thanh_pho] = {"loi": str(e)}

    return ket_qua


thanh_pho_can_giao = ["Ho Chi Minh City", "Hanoi", "Da Nang"]
bao_cao = kiem_tra_thoi_tiet_giao_hang(thanh_pho_can_giao)

for thanh_pho, info in bao_cao.items():
    print(f"\n{thanh_pho}:")
    for key, value in info.items():
        print(f"  {key}: {value}")
```

Đây là ví dụ thực tế của cách các công ty logistics, giao hàng (Grab, Shopee Express) tích hợp dữ liệu thời tiết bên thứ ba vào hệ thống vận hành của họ để tối ưu quyết định giao hàng.

---

#### 🎯 Bài tập thực hành

Viết file `bai_tap_19.py` xây dựng **module tra cứu thông tin từ API công khai (không cần key)**:

Dùng API miễn phí không cần đăng ký: `https://api.github.com` (thông tin GitHub user/repo)

1. Viết hàm `lay_thong_tin_github_user(username: str) -> dict | None` gọi `GET https://api.github.com/users/{username}`, có `timeout=5`, xử lý đầy đủ lỗi (`Timeout`, `ConnectionError`, `HTTPError`)
2. Từ kết quả, in ra: tên, số lượng follower, số lượng repo công khai, ngày tạo tài khoản
3. Viết hàm `lay_danh_sach_repo(username: str) -> list[dict]` gọi `GET https://api.github.com/users/{username}/repos`, dùng `params={"sort": "updated", "per_page": 5}` để lấy 5 repo cập nhật gần nhất
4. In ra tên và số lượng star (`stargazers_count`) của 5 repo đó, sắp xếp theo số star giảm dần (dùng lại kiến thức `sorted()` + `lambda` từ Bài 6)
5. Thử thách thêm: viết hàm với retry logic đơn giản (thử lại tối đa 3 lần nếu gặp lỗi mạng), thử nghiệm bằng cách cố ý gõ sai URL để quan sát hành vi retry hoạt động

Làm xong gửi tôi xem nhé. Sau đó ta sang **Bài 20: Cơ sở dữ liệu (SQLite, ORM cơ bản)** — nơi bạn học cách lưu trữ dữ liệu bền vững (persistent), thay vì dữ liệu chỉ tồn tại tạm thời trong RAM khi chương trình đang chạy như từ đầu đến giờ.
