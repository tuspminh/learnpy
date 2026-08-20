Kiến trúc Clean Architecture kết hợp với DDD (Domain-Driven Design) và các nguyên lý SOLID giúp xây dựng hệ thống Python dễ bảo trì, dễ kiểm thử và độc lập với các framework bên ngoài. Sự kết hợp này tập trung vào việc đặt Domain (Nghiệp vụ cốt lõi) làm trung tâm và bảo vệ nó khỏi các tác động của công nghệ như Cơ sở dữ liệu (Database) hay Web Framework (FastAPI, Flask).

Dưới đây là hướng dẫn chi tiết cách tổ chức cấu trúc thư mục và triển khai code Python áp dụng mô hình này.

* * *

## 📂 Cấu trúc thư mục chuẩn (Project Structure)

Mô hình này chia mã nguồn thành các lớp (Layers) rõ rệt theo mô hình củ hành (Onion Architecture):
    
    
    src/
    │
    ├── domain/                  # Lớp Domain (Chứa nghiệp vụ cốt lõi - Không phụ thuộc vào bất kỳ thư viện nào)
    │   ├── models.py            # Entities, Aggregates, Value Objects
    │   ├── exceptions.py        # Các ngoại lệ riêng của nghiệp vụ
    │   └── repositories.py      # Interfaces (Abstractions) định nghĩa cách lưu trữ data
    │
    ├── application/             # Lớp Ứng dụng (Điều hướng luồng xử lý)
    │   ├── use_cases.py         # Các chức năng hệ thống (Đăng ký, Mua hàng,...)
    │   └── dto.py               # Data Transfer Objects (Dữ liệu đầu vào/đầu ra)
    │
    ├── infrastructure/          # Lớp Hạ tầng (Chi tiết công nghệ cấu hình)
    │   ├── repositories/        # Triển khai thực tế các Interfaces (SQLAlchemy, MongoDB)
    │   │   └── postgres_repo.py
    │   └── database.py          # Kết nối DB, Cấu hình ORM
    │
    └── presentation/            # Lớp Hiển thị (Giao tiếp với bên ngoài)
        └── api/                 # FastAPI / Flask Routes
            └── v1/
    

* * *

## 💻 Triển khai Code Minh họa (Ví dụ: Quản lý Người dùng)

## 1\. Lớp Domain (Áp dụng DDD + Single Responsibility trong SOLID)

Lớp này hoàn toàn bằng Python thuần (`Pure Python`), sử dụng `dataclasses` để định nghĩa thực thể.
    
    
    # src/domain/models.py
    from dataclasses import dataclass, field
    import uuid
    from src.domain.exceptions import InvalidEmailError
    
    @dataclass
    class User:  # Aggregate Root / Entity
        id: uuid.UUID = field(default_factory=uuid.uuid4)
        name: str = ""
        email: str = ""
    
        def change_email(self, new_email: str) -> None:
            # Áp dụng Đóng gói và Nghiệp vụ domain
            if "@" not in new_email:
                raise InvalidEmailError("Email không hợp lệ.")
            self.email = new_email
    
    # src/domain/repositories.py
    from abc import ABC, abstractmethod
    from src.domain.models import User
    
    class UserRepository(ABC):  # Interface áp dụng Dependency Inversion Principle (D)
        @abstractmethod
        def save(self, user: User) -> None:
            pass
    
        @abstractmethod
        def get_by_id(self, user_id: str) -> User:
            pass
    

## 2\. Lớp Application (Áp dụng Use Case + Open/Closed Principle)

Lớp này nhận vào các Interface (`UserRepository`) chứ không nhận vào Database thực tế để đảm bảo lỏng lẻo (Loose coupling).
    
    
    # src/application/dto.py
    from pydantic import BaseModel
    
    class UserRegisterInput(BaseModel):
        name: str
        email: str
    
    class UserResponse(BaseModel):
        id: str
        name: str
        email: str
    
    # src/application/use_cases.py
    from src.domain.models import User
    from src.domain.repositories import UserRepository
    from src.application.dto import UserRegisterInput, UserResponse
    
    class RegisterUserUseCase:
        # Nhận vào Interface (D trong SOLID) qua Dependency Injection
        def __init__(self, user_repo: UserRepository):
            self.user_repo = user_repo
    
        def execute(self, input_data: UserRegisterInput) -> UserResponse:
            # 1. Tạo Domain Model
            user = User(name=input_data.name)
            user.change_email(input_data.email)
            
            # 2. Lưu trữ thông qua Repository Interface
            self.user_repo.save(user)
            
            # 3. Trả về DTO cho lớp bên ngoài
            return UserResponse(id=str(user.id), name=user.name, email=user.email)
    

## 3\. Lớp Infrastructure (Triển khai công nghệ thực tế)

Đây là nơi bạn sử dụng SQLAlchemy, Postgres, v.v. để hiện thực hóa `UserRepository`.
    
    
    # src/infrastructure/repositories/postgres_repo.py
    from src.domain.models import User
    from src.domain.repositories import UserRepository
    
    class PostgresUserRepository(UserRepository): # Hiện thực hóa Interface
        def __init__(self, db_session):
            self.db_session = db_session
    
        def save(self, user: User) -> None:
            # Mã nguồn mapping từ Domain Model sang SQLAlchemy Model và save vào DB
            print(saving_to_postgres=user.name)
    
        def get_by_id(self, user_id: str) -> User:
            # Truy vấn DB và map ngược lại thành Domain Model
            pass
    

## 4\. Lớp Presentation (Giao tiếp bên ngoài - FastAPI)
    
    
    # src/presentation/api/v1/users.py
    from fastapi import APIRouter, Depends
    from src.application.dto import UserRegisterInput, UserResponse
    from src.application.use_cases import RegisterUserUseCase
    from src.infrastructure.repositories import PostgresUserRepository
    
    router = APIRouter()
    
    # Hàm giả lập cung cấp DB session
    def get_db():
        return "mock_session" 
    
    @router.post("/users", response_model=UserResponse)
    def register_user(payload: UserRegisterInput, db = Depends(get_db)):
        # 1. Khởi tạo cụ thể lớp Infrastructure
        repo = PostgresUserRepository(db_session=db)
        
        # 2. Tiêm Repo vào Use Case (Dependency Injection)
        use_case = RegisterUserUseCase(user_repo=repo)
        
        # 3. Chạy nghiệp vụ
        return use_case.execute(payload)
    

* * *

## 🛠 Cách các nguyên lý SOLID được áp dụng trong kiến trúc này

  * S (Single Responsibility): Mỗi class chỉ làm một việc. `User` quản lý dữ liệu người dùng, `RegisterUserUseCase` điều phối luồng đăng ký, `UserRepository` lo việc lưu trữ.
  * O (Open/Closed): Khi bạn muốn thêm tính năng thông báo bằng SMS sau khi đăng ký, bạn chỉ cần tạo một `NotificationService` mới và truyền vào Use Case mà không cần sửa đổi logic cốt lõi của lớp `User`.
  * L (Liskov Substitution): Lớp `PostgresUserRepository` có thể thay thế hoàn toàn cho `UserRepository` ở bất kỳ đâu mà không làm ứng dụng bị lỗi.
  * I (Interface Segregation): Thay vì tạo một Repository khổng lồ cho mọi thực thể, Python sử dụng các `ABC` (Abstract Base Class) nhỏ gọn, tách biệt như `UserRepository`, `OrderRepository`.
  * D (Dependency Inversion): Lớp core (`Application/Domain`) không phụ thuộc vào lớp ngoài (`Infrastructure`). Lớp ngoài phải phụ thuộc ngược lại vào các `Interface` do lớp trong định nghĩa.



## 🎯 Điểm mấu chốt khi code Python theo mô hình này

  1. Tránh rò rỉ Framework vào Domain: Tuyệt đối không import `FastAPI`, `SQLAlchemy`, hay `Pydantic` vào trong thư mục `domain/`.
  2. Sử dụng Type Hinting mạnh mẽ: Python là ngôn ngữ dynamic, hãy dùng `typing` (`from abc import ABC`) để định nghĩa rõ Interface giúp IDE kiểm soát lỗi tốt hơn.
  3. Dễ dàng viết Unit Test: Vì Domain không dính tới DB, bạn có thể tạo một `InMemoryUserRepository` (bằng `list` hoặc `dict` thuần) để test Use Case chỉ trong vài mili-giây.



* * *

Nếu bạn muốn tiếp tục phát triển dự án này, hãy cho tôi biết:

  * Bạn định dùng Framework nào (FastAPI, Django, hay Flask)?
  * Bạn muốn tích hợp cụ thể thư viện ORM nào (SQLAlchemy, Tortoise ORM, hay SQLModel)?
  * Bạn có cần làm rõ thêm về cách quản lý Database Transaction (Unit of Work) trong kiến trúc này không?