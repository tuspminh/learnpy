Khi nhắc đến `request` trong lập trình Python, có **2 ngữ cảnh phổ biến nhất** tùy thuộc vào công cụ bạn đang dùng:

1. **`requests` / `primp` Request:** Cấu trúc dữ liệu yêu cầu HTTP trong các thư viện Client (dùng để **crawl data, gửi API**).
2. **`request` trong Web Frameworks (FastAPI / Flask / Django):** Đối tượng đại diện cho HTTP Request gửi từ phía Client lên máy chủ (dùng để **viết API / Backend**).

Dưới đây là chi tiết các methods và properties cho cả 2 trường hợp:

---

### PHẦN 1: Trong Client Crawl (Thư viện `requests` / `primp`)

Trong thư viện Client như `requests` (hoặc đối tượng `Request` nội bộ của `primp`), một đối tượng `Request` / `PreparedRequest` chứa thông tin chuẩn bị được gửi đi tới máy chủ.

#### Properties (Thuộc tính)

* **`request.method`** (`str`): Phương thức HTTP (`"GET"`, `"POST"`, `"PUT"`, `"DELETE"`...).
* **`request.url`** (`str`): URL đầy đủ mà request sẽ hướng tới (bao gồm cả query parameters nếu có).
* **`request.headers`** (`dict` / `CaseInsensitiveDict`): Tệp các HTTP Headers gửi đi (vd: `User-Agent`, `Authorization`, `Content-Type`).
* **`request.body`** (`str` | `bytes` | `None`): Nội dung phần thân gửi đi (Data payload dạng chuỗi hoặc chuỗi byte thô).
* **`request.cookies`** (`dict` / `RequestsCookieJar`): Các cookie được gắn kèm theo request.

#### Methods (Phương thức)

* **`request.prepare()`**: Đóng gói đối tượng `Request` thành `PreparedRequest` (kiểm tra URL, format headers, serialize body) trước khi gửi qua Network.

---

### PHẦN 2: Trong Web Framework Backend (FastAPI / Flask)

Khi bạn viết Server/App bằng FastAPI hoặc Flask, đối tượng `request` đại diện cho dữ liệu do người dùng gửi tới Server.

#### 1. Trong FastAPI (`from fastapi import Request`)

FastAPI sử dụng chuẩn **ASGI (Starlette)** nên hỗ trợ cả các phương thức bất đồng bộ (`async`).

##### Properties (Thuộc tính)

* **`request.method`** (`str`): HTTP Method (GET, POST...).
* **`request.url`** (`URL`): Đối tượng URL (chứa các thuộc tính con như `.scheme`, `.netloc`, `.path`, `.query`).
* **`request.headers`** (`Headers`): Headers gửi từ Client (truy cập dạng dict: `request.headers.get("User-Agent")`).
* **`request.query_params`** (`QueryParams`): Tham số trên URL dạng Dict-like (vd: `?page=1&limit=10`).
* **`request.path_params`** (`dict`): Các tham số khai báo trên đường dẫn URL (vd: `/items/{item_id}`).
* **`request.cookies`** (`dict`): Cookie gửi từ client.
* **`request.client`** (`Address`): Thông tin IP và Port của Client (truy cập IP via `request.client.host`).
* **`request.state`** (`State`): Kho chứa dữ liệu tùy chỉnh cá nhân gắn liền với vòng đời của request đó (thường dùng trong Middleware).

##### Methods (Phương thức)

* **`await request.body()`** (`bytes`): Lấy toàn bộ nội dung Body ở dạng `bytes` thô.
* **`await request.json()`** (`dict` / `list`): Parse nội dung Body từ JSON thành Python dict/list.
* **`await request.form()`** (`FormData`): Parse dữ liệu gửi lên dạng Form (`application/x-www-form-urlencoded` hoặc `multipart/form-data`).
* **`await request.stream()`** (`AsyncGenerator`): Nhận dữ liệu body theo từng chunk (dùng khi upload file lớn).
* **`request.url_for(name, **path_params)`**: Tạo URL chuỗi dựa trên tên của hàm route.

---

#### 2. Trong Flask (`from flask import request`)

Flask sử dụng chuẩn **WSGI**, đối tượng `request` là một Context Global (được cách ly giữa các thread).

##### Properties (Thuộc tính)

* **`request.method`** (`str`): Phương thức HTTP (`"GET"`, `"POST"`...).
* **`request.args`** (`MultiDict`): Chứa các tham số Query string trên URL.
* **`request.form`** (`MultiDict`): Chứa dữ liệu form POST gửi từ HTML form.
* **`request.values`** (`CombinedMultiDict`): Hợp nhất cả `args` và `form`.
* **`request.headers`** (`EnvironHeaders`): Các HTTP Headers gửi lên.
* **`request.cookies`** (`dict`): Cookie từ trình duyệt.
* **`request.files`** (`MultiDict`): Chứa các file upload (đối tượng `FileStorage`).
* **`request.data`** (`bytes`): Dữ liệu Body thô nếu không thuộc dạng Form hay JSON.
* **`request.remote_addr`** (`str`): Địa chỉ IP của người dùng/Client.
* **`request.path`** (`str`): Đường dẫn URL (không chứa domain và query string).
* **`request.endpoint`** (`str`): Tên hàm xử lý (view function) tương ứng với route.

##### Methods (Phương thức)

* **`request.get_json(force=False, silent=False)`** (`dict`): Parse dữ liệu JSON gửi lên.
* **`request.get_data(as_text=False)`** (`bytes` / `str`): Lấy dữ liệu Body thô.

---

### Tóm tắt nhanh bảng so sánh đối chiếu

| Nhu cầu lấy thông tin | Client Request (`requests`/`primp`) | FastAPI Server | Flask Server |
| --- | --- | --- | --- |
| **HTTP Method** | `req.method` | `req.method` | `request.method` |
| **URL Parameters (`?a=1`)** | Nằm trong `req.url` | `req.query_params` | `request.args` |
| **Headers** | `req.headers` | `req.headers` | `request.headers` |
| **Body (JSON)** | N/A (Truyền vào qua `json=`) | `await req.json()` | `request.get_json()` |
| **Client IP** | N/A | `req.client.host` | `request.remote_addr` |