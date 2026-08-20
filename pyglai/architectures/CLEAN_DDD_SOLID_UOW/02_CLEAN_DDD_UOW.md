Trong kiến trúc Clean Architecture kết hợp DDD, Unit of Work (UoW) đóng vai trò là một mẫu thiết kế (Design Pattern) quản lý các Database Transaction. Nó đảm bảo tính toàn vẹn dữ liệu (ACID): hoặc tất cả các thao tác thay đổi dữ liệu trong một Use Case đều thành công (Commit), hoặc tất cả đều thất bại (Rollback) nếu có lỗi xảy ra.

Dưới đây là cách triển khai Unit of Work chuẩn trong Python bằng cách tận dụng `Context Manager` (`with` statement) và Dependency Inversion.

* * *

## 📂 Cấu trúc thư mục cập nhật

Mẫu Unit of Work sẽ nằm ở lớp Application dưới dạng Interface, và được triển khai thực tế (Implementation) ở lớp Infrastructure.
    
    
    src/
    ├── domain/
    │   └── repositories.py   # Interface của các Repository
    ├── application/
    │   ├── unit_of_work.py   # [MỚI] Interface Unit of Work (Abstract Base Class)
    │   └── use_cases.py      # Use Case sử dụng UoW để quản lý Transaction
    └── infrastructure/
        ├── database.py       # Cấu hình SQLAlchemy (Session)
        └── unit_of_work.py   # [MỚI] Triển khai UoW thực tế bằng SQLAlchemy Session
    

* * *

## 💻 Triển khai Code Chi tiết (Sử dụng SQLAlchemy)

## 1\. Lớp Application: Định nghĩa Interface cho UoW

Interface này sử dụng Context Manager thuần của Python, hoàn toàn tách biệt khỏi các thư viện bên ngoài.
    
    
    # src/application/unit_of_work.py
    from abc import ABC, abstractmethod
    from src.domain.repositories import UserRepository # Giả định bạn đã có Repository này
    
    class AbstractUnitOfWork(ABC):
        users: UserRepository  # UoW chứa các Repository để đồng bộ chung một Session
    
        def __enter__(self) -> "AbstractUnitOfWork":
            return self
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                self.rollback()  # Tự động rollback nếu có Exception xảy ra trong khối `with`
            else:
                self.commit()    # Tự động commit nếu mọi thứ suôn sẻ
    
        @abstractmethod
        def commit(self):
            pass
    
        @abstractmethod
        def rollback(self):
            pass
    

## 2\. Lớp Infrastructure: Triển khai UoW với SQLAlchemy

Đây là nơi công nghệ thực tế (SQLAlchemy) nhảy vào. UoW sẽ quản lý vòng đời của một `Session`.
    
    
    # src/infrastructure/unit_of_work.py
    from sqlalchemy.orm import Session
    from src.application.unit_of_work import AbstractUnitOfWork
    from src.infrastructure.repositories.postgres_repo import PostgresUserRepository
    
    class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
        def __init__(self, session_factory):
            self.session_factory = session_factory # Thường là sessionmaker() của SQLAlchemy
    
        def __enter__(self):
            self.session: Session = self.session_factory()  # Khởi tạo session thực tế khi vào khối `with`
            self.users = PostgresUserRepository(self.session)  # Truyền session chung vào repository
            return super().__enter__()
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            super().__exit__(exc_type, exc_val, exc_tb)
            self.session.close()  # Luôn đóng session sau khi kết thúc khối `with`
    
        def commit(self):
            self.session.commit()
    
        def rollback(self):
            self.session.rollback()
    

## 3\. Lớp Application: Sử dụng UoW trong Use Case

Bây giờ, Use Case sẽ không nhận trực tiếp `UserRepository` nữa. Thay vào đó, nó nhận vào `AbstractUnitOfWork`. Toàn bộ logic nghiệp vụ được bọc trong khối `with uow:`.
    
    
    # src/application/use_cases.py
    from src.domain.models import User
    from src.application.unit_of_work import AbstractUnitOfWork
    from src.application.dto import UserRegisterInput
    
    class RegisterUserUseCase:
        def __init__(self, uow: AbstractUnitOfWork): # Tiêm UoW Interface qua Constructor
            self.uow = uow
    
        def execute(self, input_data: UserRegisterInput) -> None:
            # Bắt đầu một Transaction
            with self.uow:
                user = User(name=input_data.name, email=input_data.email)
                
                # Sử dụng repository được quản lý bên trong UoW
                self.uow.users.save(user)
                
                # Giả sử bạn có thêm hành động lưu log hoặc tạo ví tiền cho user mới:
                # self.uow.wallets.create_wallet(user_id=user.id)
                
                # Kết thúc khối `with`: 
                # - Nếu lỗi ở dòng này -> tự động rollback.
                # - Nếu thành công -> tự động commit tất cả các thao tác trên (User và Wallet).
    

## 4\. Lớp Presentation: Cấu hình Dependency Injection (FastAPI)
    
    
    # src/presentation/api/v1/users.py
    from fastapi import APIRouter, Depends
    from src.infrastructure.database import SessionLocal # sessionmaker cấu hình sẵn từ DB
    from src.infrastructure.unit_of_work import SQLAlchemyUnitOfWork
    from src.application.use_cases import RegisterUserUseCase
    from src.application.dto import UserRegisterInput
    
    router = APIRouter()
    
    # Hàm dependency cung cấp UoW thực tế
    def get_uow():
        return SQLAlchemyUnitOfWork(session_factory=SessionLocal)
    
    @router.post("/users")
    def register_user(payload: UserRegisterInput, uow: SQLAlchemyUnitOfWork = Depends(get_uow)):
        use_case = RegisterUserUseCase(uow=uow)
        use_case.execute(payload)
        return {"message": "Đăng ký thành công và dữ liệu đã được commit toàn vẹn!"}
    

* * *

## 🛡 Tại sao cách làm này tuân thủ Clean Architecture & SOLID?

  * Tách biệt tuyệt đối (Decoupling): Lớp `Application` (Use Case) chỉ biết đến `AbstractUnitOfWork`. Bạn có thể dễ dàng đổi từ SQLAlchemy sang TortoiseORM, hay MongoDB mà không cần sửa một dòng code nào trong Use Case.
  * Dễ dàng viết Unit Test (High Testability): Bạn có thể tạo ra một `FakeUnitOfWork` chạy hoàn toàn trên RAM (`list`/`dict`) để test Use Case cực kỳ nhanh mà không cần bật database thật.
  * Tránh hiện tượng "Anemic Domain Model": Thao tác Transaction không bị phân tán ở tầng Controller/API, giữ cho các luồng nghiệp vụ tập trung đúng chỗ.



* * *

Nếu bạn muốn tối ưu sâu hơn cho dự án, hãy chia sẻ thêm:

  * Bạn có cần xử lý Asynchronous (Async/Await) với `asyncio` và `AsyncSession` của SQLAlchemy cho UoW này không?
  * Bạn có muốn tích hợp thêm Domain Events (ví dụ: sau khi UoW commit thành công thì tự động bắn ra một Event để gửi Email) không?