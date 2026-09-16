Tương tự như `request`, đối tượng **`response`** đại diện cho **kết quả phản hồi** từ máy chủ. Tuỳ thuộc vào việc bạn đang ở phía **Client (Crawl/Gửi API)** hay **Server (Xây dựng Backend)**, đối tượng `response` sẽ có các thuộc tính và phương thức khác nhau.

---

### PHẦN 1: Phản hồi ở phía Client (`primp`, `requests`, `httpx`)

Khi bạn gửi một request thành công, bạn nhận về đối tượng `Response` chứa dữ liệu từ server trả về.

#### Properties (Thuộc tính)

* **`response.status_code`** (`int`): Mã trạng thái HTTP (vd: `200` OK, `404` Not Found, `500` Server Error).
* **`response.ok`** (`bool`): Trả về `True` nếu `status_code` nhỏ hơn 400 (thành công), ngược lại `False`.
* **`response.text`** (`str`): Nội dung phản hồi dạng chuỗi văn bản (tự động decode theo bảng mã).
* **`response.content`** (`bytes`): Nội dung phản hồi dạng byte thô (dùng để lưu file ảnh, PDF, audio...).
* **`response.headers`** (`dict` / `CaseInsensitiveDict`): Các HTTP headers do server gửi về (vd: `Content-Type`, `Set-Cookie`).
* **`response.cookies`** (`dict` / `CookieJar`): Danh sách cookie mà server thiết lập cho client.
* **`response.url`** (`str`): URL cuối cùng nhận phản hồi (hữu ích để kiểm tra xem request có bị redirect không).
* **`response.encoding`** (`str`): Bảng mã ký tự dùng để decode `response.text` (vd: `'utf-8'`, `'iso-8859-1'`). Bạn có thể thay đổi thuộc tính này thủ công nếu bị lỗi font.
* **`response.history`** (`list[Response]`): Danh sách các đối tượng Response của những lần chuyển hướng (redirect) trước đó (nếu có).
* **`response.elapsed`** (`timedelta`): Thời gian chờ từ khi gửi request đến khi nhận được response đầu tiên.
* **`response.reason`** (`str`): Tóm tắt bằng chữ của mã trạng thái (vd: `"OK"`, `"Not Found"`).

#### Methods (Phương thức)

* **`response.json()`**: Decode nội dung `text` thành đối tượng Python `dict` hoặc `list`. Ném ra lỗi `JSONDecodeError` nếu dữ liệu không phải format JSON.
* **`response.raise_for_status()`**: Bắn ra ngoại lệ HTTPError nếu `status_code` từ 400 đến 599. Nếu status code thành công (2xx/3xx), hàm không làm gì cả.
* **`response.iter_content(chunk_size=1024)`**: Đọc phản hồi theo từng mảnh (chunk) dữ liệu. Rất hữu ích khi tải các file dung lượng lớn để tránh tràn RAM.
* **`response.iter_lines()`**: Đọc dữ liệu response theo từng dòng một (thường dùng khi stream dữ liệu hoặc nhận server-sent events).
* **`response.close()`**: Đóng kết nối HTTP thô (thường tự động được gọi khi dùng `with`).

---

### PHẦN 2: Phản hồi ở phía Backend (FastAPI / Flask)

Khi làm Server, bạn tự khởi tạo đối tượng `Response` để trả dữ liệu về cho người dùng.

#### 1. Trong FastAPI (`from fastapi import Response, JSONResponse, HTMLResponse`)

FastAPI cung cấp class `Response` cơ sở và các subclass chuyển đổi định dạng.

##### Key Properties & Methods

* **`Response(content=..., status_code=200, headers=..., media_type=...)`**: Hàm khởi tạo response thủ công.
* **`response.status_code`** (`int`): Thiết lập hoặc lấy mã HTTP status trả về.
* **`response.headers`**: Đổi/thêm headers bằng cú pháp dict (`response.headers["X-Custom-Header"] = "value"`).
* **`response.set_cookie(key, value, max_age=..., httponly=True, ...)`**: Đặt cookie xuống trình duyệt client với các tham số bảo mật.
* **`response.delete_cookie(key)`**: Gửi lệnh xóa cookie phía trình duyệt client.
* **Các lớp Response dựng sẵn (Subclasses):**
* `JSONResponse(...)`: Trả về dữ liệu định dạng JSON.
* `HTMLResponse(...)`: Trả về giao diện HTML.
* `StreamingResponse(...)`: Stream dữ liệu lớn hoặc real-time.
* `FileResponse(...)`: Trả về file tải xuống cho client.



#### 2. Trong Flask (`from flask import make_response, jsonify, Response`)

Flask cho phép tạo phản hồi thông qua tuple `(body, status, headers)` hoặc qua đối tượng `Response`.

##### Key Properties & Methods

* **`response = make_response(html_or_text)`**: Chuyển chuỗi hoặc template thành đối tượng Response.
* **`response.status_code`** (`int`): Thay đổi mã trạng thái HTTP.
* **`response.headers`**: Thêm/sửa header trả về (`response.headers['Content-Type'] = 'application/json'`).
* **`response.set_cookie(key, value, max_age=..., httponly=True)`**: Thiết lập Cookie cho Client.
* **`response.delete_cookie(key)`**: Xóa Cookie phía Client.
* **`jsonify(dict_data)`**: Tạo nhanh một JSON Response với header `Content-Type: application/json`.

---

### Bảng Tóm Tắt So Sánh Cần Thiết

| Thao tác phổ biến | Client (Crawl data) | Server (FastAPI / Flask) |
| --- | --- | --- |
| **Mục đích** | Đọc dữ liệu server gửi về | Tạo dữ liệu trả về cho client |
| **Lấy/Đặt Status Code** | `status = resp.status_code` | `resp.status_code = 201` |
| **Đọc/Gửi Header** | `hdr = resp.headers['Content-Type']` | `resp.headers['X-Server'] = 'Py'` |
| **Xử lý JSON** | `data = resp.json()` | `return JSONResponse(data)` |
| **Xử lý Cookie** | `cookie = resp.cookies.get('session')` | `resp.set_cookie('session', val)` |