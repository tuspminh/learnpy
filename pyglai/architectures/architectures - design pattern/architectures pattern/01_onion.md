Onion Architecture (Kiến trúc củ hành) là một mô hình kiến trúc phần mềm hướng domain (Domain-Driven Design), tập trung vào việc đặt Logic cốt lõi (Domain) làm trung tâm và các thành phần khác sẽ bao bọc xung quanh giống như các lớp của một củ hành.

Nguyên tắc tối cao của kiến trúc này là Quy tắc phụ thuộc (Dependency Rule): Các lớp bên ngoài có thể phụ thuộc vào các lớp bên trong, nhưng các lớp bên trong _không bao giờ_ được phép biết hoặc phụ thuộc vào các lớp bên ngoài.

* * *

## Cấu trúc các lớp trong Onion Architecture

Kiến trúc này thường được chia thành 4 lớp chính từ trong ra ngoài:
    
    
        +-------------------------------------------+
    
        | Lớp 4: Infrastructure (DB, API, UI, File) |
        |   +-----------------------------------+   |
        |   | Lớp 3: Application Services       |   |
        |   |   +---------------------------+   |   |
        |   |   | Lớp 2: Domain Services    |   |   |
        |   |   |   +-------------------+   |   |   |
        |   |   |   | Lớp 1: Domain     |   |   |   |
        |   |   |   |        Entities   |   |   |   |
        |   |   |   +-------------------+   |   |   |
        |   |   +---------------------------+   |   |
        |   +-----------------------------------+   |
        +-------------------------------------------+
    

  1. Domain Entities (Lớp lõi): Chứa các đối tượng doanh nghiệp (Business Objects), cấu trúc dữ liệu và các quy tắc logic nghiệp vụ cơ bản nhất. Lớp này độc lập 100%, không phụ thuộc vào bất kỳ thư viện hay framework nào.
  2. Domain Services: Chứa các logic nghiệp vụ phức tạp hơn, liên quan đến sự tương tác giữa nhiều Entities mà bản thân một Entity không tự xử lý được.
  3. Application Services (Use Cases): Định nghĩa các chức năng của ứng dụng (Ví dụ: `CreateUser`, `ProcessOrder`). Lớp này điều phối luồng dữ liệu từ ngoài vào trong nhưng không chứa logic nghiệp vụ cốt lõi.
  4. Infrastructure / External Interfaces (Lớp ngoài cùng): Chứa UI, Web Framework (FastAPI, Flask), Database (SQLAlchemy, MongoDB), các thư viện gửi Mail, gọi API bên thứ ba. Lớp này rất dễ thay đổi mà không ảnh hưởng đến phần lõi.



* * *

### cau truc thu muc

Rất tương đồng với Clean Architecture nhưng Onion phân ranh giới lỏng hơn ở tầng Application và phân tách rõ hơn giữa Domain Entities (Thực thể) và Domain Services (Nghiệp vụ giữa các thực thể).

📂 Cấu trúc thư mục chuẩn

text
    
    
    my_onion_project/
    │
    ├── core/                        # Phần lõi (Tầng 1 & Tầng 2)
    │   ├── domain/
    │   │   ├── __init__.py
    │   │   ├── entities/            # Lớp 1: Khái niệm thực thể nghiệp vụ
    │   │   │   └── product.py
    │   │   └── services/            # Lớp 2: Logic tương tác giữa các thực thể
    │   │       └── discount_service.py
    │   │
    │   └── application/             # Lớp 3: Điều phối Use Cases & Interfaces
    │       ├── __init__.py
    │       ├── services/            # Application Services
    │       │   └── order_flow.py
    │       └── ports/               # Giao diện trừu tượng để lớp ngoài cắm vào
    │           ├── i_order_repository.py
    │           └── i_payment_gateway.py
    │
    ├── infrastructure/              # Lớp 4: Lớp ngoài cùng (Bao bọc tất cả công nghệ)
    │   ├── __init__.py
    │   ├── persistence/             # Lưu trữ dữ liệu (SQLAlchemy, MongoDB)
    │   │   └── postgres_order_repo.py
    │   ├── external_apis/           # Gọi API bên thứ 3 (Stripe, Paypal)
    │   │   └── stripe_gateway.py
    │   └── delivery/                # Giao diện người dùng (REST API, CLI, gRPC)
    │       ├── http_routes.py
    │       └── cli_commands.py
    │
    └── config.py                    # Cấu hình môi trường và khởi chạy ứng dụng
    



* * *

## Cách triển khai Onion Architecture trong Python

Để triển khai Onion Architecture trong Python mà không vi phạm quy tắc phụ thuộc, chúng ta bắt buộc phải sử dụng kỹ thuật Dependency Inversion (Đảo ngược phụ thuộc) bằng cách định nghĩa các Interface (lớp trừu tượng `abc.ABC`) ở lớp trong, và viết code triển khai thực tế (Implementation) ở lớp ngoài cùng.

Dưới đây là một ví dụ thực tế về tính năng Đăng ký người dùng:

## 1\. Lớp Domain Entities (Lớp 1)
    
    
    # domain/entities.py
    from dataclasses import dataclass
    
    @dataclass
    class User:
        id: int | None
        username: str
        email: str
        password_hash: str
    

## 2\. Lớp Domain / Application Interfaces (Lớp 2/3)

Định nghĩa cổng giao tiếp (Port) bằng Interface. Lớp con này không cần biết cơ sở dữ liệu là gì.
    
    
    # application/interfaces.py
    from abc import ABC, abstractmethod
    from domain.entities import User
    
    class UserRepository(ABC):
        @abstractmethod
        def save(self, user: User) -> User:
            pass
    
        @abstractmethod
        def get_by_email(self, email: str) -> User | None:
            pass
    

## 3\. Lớp Application Services (Lớp 3)

Chứa Use Case xử lý logic luồng công việc. Nó chỉ giao tiếp với Interface `UserRepository`.
    
    
    # application/use_cases.py
    from domain.entities import User
    from application.interfaces import UserRepository
    
    class RegisterUserUseCase:
        def __init__(self, user_repo: UserRepository):
            self.user_repo = user_repo  # Inject interface vào đây
    
        def execute(self, username: str, email: str, password_raw: str) -> User:
            # Kiểm tra xem email đã tồn tại chưa
            if self.user_repo.get_by_email(email):
                raise ValueError("Email already registered")
            
            # Giả định đã hash password (logic nghiệp vụ)
            hashed_password = f"hashed_{password_raw}" 
            
            new_user = User(id=None, username=username, email=email, password_hash=hashed_password)
            return self.user_repo.save(new_user)
    

## 4\. Lớp Infrastructure (Lớp ngoài cùng - Lớp 4)

Nơi viết code thực tế để kết nối Database hoặc xử lý Web Framework.

_Triển khai Repository thực tế (Database):_
    
    
     # infrastructure/database.py
    from application.interfaces import UserRepository
    from domain.entities import User
    
    class SQLUserRepository(UserRepository):
        def __init__(self):
            self.db = {} # Giả lập database bằng dict trong bộ nhớ
            self.counter = 1
    
        def save(self, user: User) -> User:
            user.id = self.counter
            self.db[user.id] = user
            self.counter += 1
            print(f"[DB] Đã lưu User {user.username} vào SQL Database.")
            return user
    
        def get_by_email(self, email: str) -> User | None:
            for user in self.db.values():
                if user.email == email:
                    return user
            return None
    

_Triển khai API Giao diện (Ví dụ sử dụng FastAPI hoặc script chạy chính):_
    
    
     # app.py (Composition Root - Nơi ráp nối các lớp lại với nhau)
    from infrastructure.database import SQLUserRepository
    from application.use_cases import RegisterUserUseCase
    
    # 1. Khởi tạo đối tượng ở lớp ngoài cùng
    user_repository = SQLUserRepository()
    
    # 2. Inject vào Use Case lớp bên trong
    register_service = RegisterUserUseCase(user_repo=user_repository)
    
    # 3. Chạy ứng dụng
    try:
        user = register_service.execute("nguyenvana", "ana@gmail.com", "secret123")
        print(f"Thành công! ID người dùng mới: {user.id}")
    except ValueError as e:
        print(f"Lỗi: {e}")
    

* * *

## Ưu điểm và Nhược điểm

Ưu điểm 🟢| Nhược điểm 🔴  
---|---  
Dễ Test (Testability): Bạn có thể viết Unit Test cho Domain và Use Case cực kỳ dễ dàng bằng cách Mock/Fake các Repository mà không cần bật Database thật.| Cồng kềnh (Boilerplate): Phải viết rất nhiều file, nhiều lớp Interface trung gian cho một tính năng đơn giản.  
Độc lập với Công nghệ: Hôm nay bạn dùng MySQL, ngày mai đổi sang MongoDB hay PostgreSQL thì code Logic cốt lõi (Domain) hoàn toàn giữ nguyên, chỉ cần viết lại lớp Infrastructure.| Độ dốc học tập cao: Đòi hỏi lập trình viên phải hiểu rõ về OOP nâng cao, Dependency Injection và tư duy tách biệt trách nhiệm.  
Dễ bảo trì: Code nghiệp vụ không bị trộn lẫn với code cấu hình DB hay code của Web Framework.| Hiệu năng: Việc đi qua nhiều lớp trung gian (Abstraction) có thể làm giảm một chút hiệu năng hoặc tăng độ trễ đọc code (nhưng không đáng kể).  
  
* * *

## Khi nào nên sử dụng Onion Architecture?

  * Nên dùng: Các dự án lớn (Enterprise), có logic nghiệp vụ (Business Logic) phức tạp, thay đổi liên tục, và dự án dự kiến sẽ kéo dài nhiều năm cần bảo trì, nâng cấp phần mềm dễ dàng.
  * Không nên dùng: Các dự án nhỏ, ứng dụng dạng CRUD đơn giản (chỉ thêm, sửa, xóa dữ liệu không có logic gì phức tạp). Nếu làm dự án nhỏ, kiến trúc này sẽ biến thành "over-engineering" (làm quá phức tạp hóa vấn đề).



Nếu bạn muốn áp dụng mô hình này vào một framework cụ thể, tôi có thể hướng dẫn bạn cấu trúc thư mục chuẩn cho FastAPI hoặc Django. Bạn có muốn xem cấu trúc thư mục thực tế không?