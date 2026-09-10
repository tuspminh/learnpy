`pydantic-settings` là thư viện mở rộng từ Pydantic (được tách ra từ Pydantic v2) giúp tự động đọc, ép kiểu và kiểm tra dữ liệu từ các biến môi trường (Environment Variables) hoặc file `.env`.

---

### 1. Cài đặt

Cài đặt `pydantic-settings` cùng thư viện đọc file `.env`:

```bash
pip install pydantic-settings python-dotenv

```

---

### 2. Tạo file `.env`

Tạo file có tên `.env` tại thư mục gốc của dự án:

```env
# .env
APP_NAME=MyAwesomeApp
DEBUG=True
PORT=8000
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
SECRET_KEY=super-secret-key-123

```

---

### 3. Định nghĩa cấu hình trong Python

Thay vì kế thừa `BaseModel`, bạn kế thừa từ `BaseSettings` và chỉ định cấu hình file `.env` trong `model_config`.

```python
# config.py
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Định nghĩa các biến cấu hình và kiểu dữ liệu
    app_name: str = "DefaultApp"
    debug: bool = False
    port: int = 8000
    database_url: str
    secret_key: str = Field(min_length=8)

    # Cấu hình nạp dữ liệu từ file .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # Không phân biệt hoa/thường (APP_NAME = app_name)
    )


# Khởi tạo instance duy nhất để dùng trong toàn bộ ứng dụng
settings = Settings()
```

---

### 4. Cách sử dụng trong ứng dụng

Nạp và truy cập các biến cấu hình trực tiếp từ đối tượng `settings`:

```python
# main.py
from config import settings

print(f"Đang chạy ứng dụng: {settings.app_name}")
print(f"Cổng kết nối: {settings.port} (Kiểu dữ liệu: {type(settings.port)})")
print(f"Chế độ Debug: {settings.debug}")
print(f"Database URL: {settings.database_url}")
```

---

### 5. Thứ tự ưu tiên nạp biến môi trường

`pydantic-settings` giải quyết xung đột cấu hình theo thứ tự ưu tiên từ cao xuống thấp:

1. **Biến truyền trực tiếp** khi khởi tạo lớp: `Settings(port=9000)`
2. **Biến môi trường hệ thống** (được set qua terminal bằng `export PORT=9000` hoặc Docker)
3. **Giá trị đọc từ file `.env**`
4. **Giá trị mặc định** định nghĩa trong Class (`port: int = 8000`)

> **Lưu ý Security:** Nếu thiếu các biến bắt buộc (như `database_url` không có giá trị mặc định và không có trong file `.env`), ứng dụng sẽ dừng ngay lập tức và báo lỗi `ValidationError` lúc khởi động.

---

### 6. Cấu trúc lồng nhau (Nested Settings)

Dùng cho các ứng dụng lớn cần nhóm cấu hình theo từng mô-đun:

```python
# .env
DB__HOST = localhost
DB__PORT = 5432
DB__NAME = prod_db

# config.py
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    host: str
    port: int = 5432
    name: str


class Settings(BaseSettings):
    db: DatabaseSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",  # Dùng dấu '__' để phân tách lớp lồng nhau
    )


settings = Settings()
print(settings.db.host)  # localhost
print(settings.db.name)  # prod_db
```