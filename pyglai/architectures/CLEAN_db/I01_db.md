Trong kiến trúc sạch (Clean Architecture) và Thiết kế hướng tên miền (DDD), công đoạn xử lý database (kết nối, transaction, mapping) thuộc về tầng Infrastructure (Hạ tầng). Mục tiêu cốt lõi là giữ cho tầng Domain (Nghiệp vụ) hoàn toàn tinh khiết, không phụ thuộc vào bất kỳ công cụ hay cơ sở dữ liệu cụ thể nào (như PostgreSQL, MySQL, SQLAlchemy, hay MongoDB).

Dưới đây là phân tích chi tiết cách thiết kế các công đoạn này bằng Python, áp dụng các nguyên lý SOLID.

* * *

## 1\. Quản lý Kết nối (Connection Management)

  * DDD & Clean Architecture: Kết nối DB là chi tiết kỹ thuật thuộc tầng _Infrastructure_. Tầng _Domain_ và _Application_ không được biết về cách kết nối được mở hay đóng.
  * SOLID (DIP - Dependency Inversion): Tầng cao không phụ thuộc tầng thấp. Định nghĩa một interface (hoặc trừu tượng) cho client kết nối, sau đó cụ thể hóa bằng thư viện Python (như SQLAlchemy, Motor, Asyncpg).



## Triển khai bằng Python:

Sử dụng `contextmanager` để quản lý vòng đời của session/connection một cách an toàn.
    
    
    from abc import ABC, abstractmethod
    from contextlib import contextmanager
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session
    
    # LAYER: Application/Domain (Interface)
    class DBConnectionProvider(ABC):
        @abstractmethod
        @contextmanager
        def get_session(self):
            pass
    
    # LAYER: Infrastructure (Implementation)
    class SQLAlchemyConnectionProvider(DBConnectionProvider):
        def __init__(self, database_url: str):
            self._engine = create_engine(database_url, pool_pre_ping=True)
            self._session_factory = sessionmaker(bind=self._engine)
    
        @contextmanager
        def get_session(self) -> Session:
            session = self._session_factory()
            try:
                yield session
            finally:
                session.close() # SRP: Đảm bảo giải phóng tài nguyên tự động
    

* * *

## 2\. Quản lý Giao dịch (Transaction Management - Unit of Work)

  * DDD: Sử dụng pattern Unit of Work (UoW). UoW quản lý một chuỗi các thao tác thay đổi dữ liệu trên nhiều Repository trong cùng một Transaction, đảm bảo tính toàn vẹn dữ liệu (All or Nothing) cho một _Aggregate Root_.
  * Clean Architecture: UoW thuộc tầng _Application Use Cases_. Use Case điều khiển transaction (khi nào bắt đầu, khi nào commit/rollback) nhưng không được can thiệp vào mã lệnh SQL cụ thể.
  * SOLID (SRP - Single Responsibility): Tách biệt việc thực thi nghiệp vụ (Repository) khỏi việc quản lý transaction (Unit of Work).



## Triển khai bằng Python:

Sử dụng Context Manager (`__enter__`, `__exit__`) để tạo ra một UoW trực quan và Pythonic.
    
    
    # LAYER: Application (Interfaces)
    class UnitOfWork(ABC):
        def __enter__(self):
            return self
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                self.rollback()
            else:
                self.commit()
    
        @abstractmethod
        def commit(self):
            pass
    
        @abstractmethod
        def rollback(self):
            pass
    
    # LAYER: Infrastructure (Implementation)
    class SQLAlchemyUnitOfWork(UnitOfWork):
        def __init__(self, session_factory):
            self.session_factory = session_factory
    
        def __enter__(self):
            self.session: Session = self.session_factory()
            # Khởi tạo các repositories dùng chung session này tại đây
            # ví dụ: self.users = SQLAlchemyUserRepository(self.session)
            return super().__enter__()
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            super().__exit__(exc_type, exc_val, exc_tb)
            self.session.close()
    
        def commit(self):
            self.session.commit()
    
        def rollback(self):
            self.session.rollback()
    

* * *

## 3\. Ánh xạ Mô hình (Model Mapping / Data Mapping)

Sai lầm phổ biến trong Python (đặc biệt khi dùng Django ORM hoặc SQLAlchemy) là dùng chung một Model cho cả bảng DB và thực thể nghiệp vụ.

  * DDD: Định nghĩa các Domain Entity (chứa logic nghiệp vụ, thuần Python, không kế thừa từ ORM).
  * Clean Architecture: Định nghĩa các Database Model (ORM Model) ở tầng _Infrastructure_. Sau đó dùng một Data Mapper để chuyển đổi qua lại giữa hai mô hình này tại ranh giới của tầng Infrastructure.
  * SOLID (OCP - Open/Closed): Khi cấu trúc bảng DB thay đổi, bạn chỉ cần sửa Database Model và Mapper. Logic nghiệp vụ trong Domain Entity hoàn toàn đóng kín và không bị ảnh hưởng.



## Triển khai bằng Python:
    
    
    from dataclasses import dataclass
    from sqlalchemy.orm import declarative_base
    from sqlalchemy import Column, String, Integer
    
    Base = declarative_base()
    
    # 1. LAYER: Domain (Thuần Python, không dính dáng đến DB)
    @dataclass
    class User:
        id: int
        name: str
        email: str
    
        def change_name(self, new_name: str):
            if not new_name:
                raise ValueError("Tên không được để trống")
            self.name = new_name
    
    # 2. LAYER: Infrastructure (SQLAlchemy Model đại diện cho bảng DB)
    class UserORM(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        name = Column(String(50))
        email = Column(String(100), unique=True)
    
    # 3. LAYER: Infrastructure (User Mapper chịu trách nhiệm chuyển đổi)
    class UserMapper:
        @staticmethod
        def to_domain(orm: UserORM) -> User:
            return User(id=orm.id, name=orm.name, email=orm.email)
    
        @staticmethod
        def to_orm(domain: User) -> UserORM:
            return UserORM(id=domain.id, name=domain.name, email=domain.email)
    

_(Mẹo Python: Bạn có thể cấu hình Imperative Mapping của SQLAlchemy để map trực tiếp Data Class vào bảng DB mà không cần viết class ORM riêng, giúp code gọn hơn nhưng vẫn đạt được sự phân tách)._

* * *

## 4\. Tổng hợp luồng hoạt động trong một Use Case (Application Layer)

Hãy xem cách các thành phần trên phối hợp với nhau tạo nên một cấu trúc Clean, SOLID và chuẩn DDD khi thực hiện một Use Case: Đổi tên người dùng.
    
    
    # LAYER: Application (Use Case / Command Handler)
    class ChangeUserNameUseCase:
        def __init__(self, uow: UnitOfWork, user_repository_factory):
            self.uow = uow
            self.user_repo_factory = user_repository_factory
    
        def execute(self, user_id: int, new_name: str):
            # Sử dụng Unit of Work để quản lý Transaction
            with self.uow as tx:
                # 1. Khởi tạo repo với session lấy từ transaction hiện tại
                repo = self.user_repo_factory(tx.session)
                
                # 2. Đọc dữ liệu lên (Repo đã tự động dùng Mapper để trả về Domain Entity)
                user: User = repo.get_by_id(user_id)
                
                # 3. Thực thi nghiệp vụ thuần túy trên Domain Entity
                user.change_name(new_name)
                
                # 4. Lưu lại thay đổi (Repo dịch từ Domain Entity về ORM để lưu vào DB)
                repo.save(user)
                
                # Khối lệnh 'with' kết thúc thành công sẽ tự động gọi tx.commit()
                # Nếu có lỗi (ví dụ: ValueError), tx.rollback() tự động kích hoạt.
    

## Tóm tắt lợi ích thiết kế này mang lại:

  1. Dễ viết Unit Test: Bạn có thể test toàn bộ logic nghiệp vụ (Domain) và luồng đi (Use Case) bằng cách Mock bộ nhớ (`MemoryUnitOfWork`, `MemoryRepository`) mà không cần bật một database PostgreSQL/MySQL thật lên.
  2. Linh hoạt thay đổi công nghệ: Nếu ngày mai dự án quyết định chuyển từ cơ sở dữ liệu quan hệ (SQLAlchemy) sang NoSQL (MongoDB), bạn chỉ cần viết lại các class ở tầng Infrastructure (UoW mới, Repo mới, Mapper mới). Toàn bộ tầng nghiệp vụ (Domain và Use Case) được giữ nguyên 100%.
  3. Tuân thủ SOLID triệt để: Mỗi class chỉ giữ một trách nhiệm duy nhất (UoW lo transaction, Repo lo truy vấn, Mapper lo chuyển đổi, Entity lo luật nghiệp vụ).



Nếu bạn muốn đi sâu hơn, hãy cho tôi biết:

  * Bạn đang dùng thư viện ORM nào (SQLAlchemy, Tortoise ORM, SQLModel,...) hoặc thuần SQL?
  * Dự án của bạn chạy cơ chế Đồng bộ (Synchronous) hay Bất đồng bộ (Asyncio)?