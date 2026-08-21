Clean Architecture (kiến trúc sạch) do Robert C. Martin (Uncle Bob) đề xuất giúp tách biệt logic nghiệp vụ (business logic) khỏi các công cụ, framework và cơ sở dữ liệu. Điểm cốt lõi là **Quy tắc phụ thuộc (Dependency Rule)**: các lớp bên trong không được phép biết bất kỳ thông tin nào về các lớp bên ngoài.

---

**4 Tầng cấu trúc chính trong Python**

**1. Entities (Thực thể - Trong cùng)**

* Chứa các đối tượng nghiệp vụ cốt lõi và các quy tắc chung của toàn hệ thống.
* Trong Python, tầng này thường là các class thuần túy (dùng `dataclasses` hoặc `pydantic`), không phụ thuộc vào ORM như SQLAlchemy hay Django ORM.

**2. Use Cases / Application Logic**

* Chứa quy tắc nghiệp vụ đặc thù cho ứng dụng (ví dụ: tạo tài khoản, xử lý thanh toán).
* Định nghĩa các interface (sử dụng module `abc` của Python) để giao tiếp với tầng ngoài mà không cần quan tâm đến triển khai cụ thể (như Database hay Email Service).

**3. Interface Adapters (Controllers, Presenters, Gateways)**

* Chuyển đổi dữ liệu giữa định dạng thuận tiện cho Use Cases/Entities và định dạng thuận tiện cho các công cụ bên ngoài (DB, Web).
* Thực thi (implement) các interface từ tầng Use Case (ví dụ: SQLAlchemy Repository triển khai Repository Interface).

**4. Frameworks & Drivers (Ngoài cùng)**

* Chứa các công cụ như Web Framework (FastAPI, Flask, Django), Cơ sở dữ liệu (PostgreSQL, MongoDB), UI, các SDK dịch vụ bên ngoài.

---

**Cấu trúc thư mục dự án Python mẫu**

```text
src/
├── domain/                      # 1. Entities
│   ├── models/
│   │   └── user.py
│   └── exceptions.py
├── use_cases/                   # 2. Use Cases
│   ├── interfaces/              # Abstract Base Classes (ABC)
│   │   └── user_repository.py
│   └── create_user.py
├── infrastructure/              # 3. Adapters & Implementations
│   ├── db/
│   │   ├── models.py            # ORM Models (SQLAlchemy)
│   │   └── repositories.py      # Triển khai interface
│   └── services/
│       └── email_service.py
└── presentation/                # 4. Frameworks & Drivers
    ├── api/                     # FastAPI / Flask Endpoints
    │   └── v1/
    │       └── user_router.py
    └── main.py                  # Entrypoint & Dependency Injection

```

---

**Minh họa bằng Code Python**

**Bước 1: Domain (Entities)**

```python
# src/domain/models/user.py
from dataclasses import dataclass
from uuid import UUID

@dataclass
class User:
    id: UUID
    email: str
    is_active: bool = True

```

**Bước 2: Use Case & Interface**

```python
# src/use_cases/interfaces/user_repository.py
from abc import ABC, abstractmethod
from src.domain.models.user import User

class UserRepositoryInterface(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        pass

# src/use_cases/create_user.py
from uuid import uuid4
from src.domain.models.user import User
from src.use_cases.interfaces.user_repository import UserRepositoryInterface

class CreateUserUseCase:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo  # Phụ thuộc vào abstraction

    def execute(self, email: str) -> User:
        user = User(id=uuid4(), email=email)
        self.user_repo.save(user)
        return user

```

**Bước 3: Infrastructure (Adapter Implementation)**

```python
# src/infrastructure/db/repositories.py
from src.domain.models.user import User
from src.use_cases.interfaces.user_repository import UserRepositoryInterface

class PostgresUserRepository(UserRepositoryInterface):
    def __init__(self, db_session):
        self.session = db_session

    def save(self, user: User) -> None:
        # Chuyển đổi từ Domain Model sang ORM Model và lưu DB
        ...

```

**Bước 4: Presentation (FastAPI Route)**

```python
# src/presentation/api/v1/user_router.py
from fastapi import APIRouter, Depends
from src.use_cases.create_user import CreateUserUseCase
from src.infrastructure.db.repositories import PostgresUserRepository

router = APIRouter()

@router.post("/users")
def create_user(email: str, repo = Depends(PostgresUserRepository)):
    use_case = CreateUserUseCase(user_repo=repo)
    return use_case.execute(email)

```