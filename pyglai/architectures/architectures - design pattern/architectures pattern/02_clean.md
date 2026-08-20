Clean Architecture (Kiến trúc sạch) là một mô hình kiến trúc phần mềm do Robert C. Martin (Uncle Bob) giới thiệu vào năm 2012, hướng tới mục tiêu tối thượng: tách biệt hoàn toàn mã nguồn xử lý logic nghiệp vụ khỏi các framework, database, UI và các công cụ bên thứ ba.

Về bản chất và triết lý, Clean Architecture và Onion Architecture giống nhau đến 90% khi đều đặt Domain làm trung tâm và sử dụng quy tắc một chiều (Dependency Rule). Tuy nhiên, Clean Architecture định nghĩa các ranh giới và thuật ngữ một cách chuẩn hóa, mang tính thực tế cao cho việc phân tách các thành phần trong hệ thống lớn.

* * *

## Sơ đồ cấu trúc 4 vòng tròn của Clean Architecture

Kiến trúc này được hình dung qua 4 vòng tròn đồng tâm, luồng phụ thuộc chỉ đi từ ngoài vào trong:
    
    
        +---------------------------------------------------+
    
        | Vòng 1: Drivers & Frameworks (Web, DB, Devices)   |
        |   +-------------------------------------------+   |
        |   | Vòng 2: Interface Adapters (Controllers)  |   |
        |   |   +-----------------------------------+   |   |
        |   |   | Vòng 3: Use Cases (Application)   |   |   |
        |   |   |   +---------------------------+   |   |   |
        |   |   |   | Vòng 4: Entities (Domain) |   |   |   |
        |   |   |   +---------------------------+   |   |   |
        |   |   +-----------------------------------+   |   |
        |   +-------------------------------------------+   |
        +---------------------------------------------------+
    

  1. Entities (Nghiệp vụ doanh nghiệp cốt lõi): Chứa các quy tắc nghiệp vụ chung nhất cho toàn doanh nghiệp (Enterprise Business Rules). Nó có thể là một object có phương thức hoặc một tập hợp các cấu trúc dữ liệu.
  2. Use Cases (Nghiệp vụ cụ thể của ứng dụng): Chứa logic vận hành hệ thống (Application Business Rules). Lớp này điều phối luồng dữ liệu đến và đi từ các Entities, thực hiện các kịch bản cụ thể của phần mềm.
  3. Interface Adapters: Tập hợp các bộ chuyển đổi dữ liệu. Nó chuyển dữ liệu từ định dạng tiện lợi cho Use Cases/Entities sang định dạng tiện lợi cho Framework (ví dụ: chuyển đổi Object thành JSON cho Web API, hoặc thành câu lệnh SQL cho Database). Lớp này chứa các Controllers, Presenters, và Gateways (Repositories).
  4. Frameworks & Drivers (Lớp ngoài cùng): Nơi chứa công cụ, framework như FastAPI, Django, SQLAlchemy, Celery, hệ điều hành, UI. Bạn nên viết càng ít code ở lớp này càng tốt.

* * *

### cau truc thu muc

Kiến trúc này phân chia cực kỳ nghiêm ngặt theo các vòng tròn đồng tâm. Logic doanh nghiệp (Domain) nằm ở lõi và không phụ thuộc vào bất kỳ thư viện nào bên ngoài.

📂 Cấu trúc thư mục chuẩn

text
    
    
    my_clean_project/
    │
    ├── domain/                      # Vòng trong cùng: Luật nghiệp vụ cốt lõi
    │   ├── __init__.py
    │   ├── entities.py              # Các thực thể dữ liệu (User, Order, Account)
    │   └── value_objects.py         # Các đối tượng giá trị không có định danh
    │
    ├── application/                 # Vòng 2: Logic cụ thể của ứng dụng (Use Cases)
    │   ├── __init__.py
    │   ├── use_cases/               # Các kịch bản tính năng
    │   │   ├── register_user.py
    │   │   └── process_payment.py
    │   └── interfaces/              # Định nghĩa các cổng kết nối (Ports/Gateways)
    │       ├── db_interface.py
    │       └── email_interface.py
    │
    ├── adapters/                    # Vòng 3: Bộ chuyển đổi dữ liệu (Interface Adapters)
    │   ├── __init__.py
    │   ├── controllers/             # Tiếp nhận request và điều hướng
    │   │   └── user_controller.py
    │   ├── presenters/              # Định dạng dữ liệu trả về cho Client
    │   │   └── user_presenter.py
    │   └── repositories/            # Triển khai các Interface dữ liệu (Data Gateways)
    │       └── user_repository.py
    │
    ├── infrastructure/              # Vòng ngoài cùng: Frameworks & Drivers
    │   ├── __init__.py
    │   ├── web/                     # Cấu hình FastAPI, Flask, hoặc Django
    │   │   └── fastapi_app.py
    │   ├── database/                # Cấu hình DB, Models của SQLAlchemy/Alembic
    │   │   ├── connection.py
    │   │   └── sql_models.py
    │   └── services/                # Triển khai thư viện bên thứ 3 (Boto3, SendGrid)
    │       └── sendgrid_email.py
    │
    └── main.py                      # Composition Root: Điểm ráp nối toàn bộ hệ thống
    



* * *

## Cách triển khai Clean Architecture trong Python

Để minh họa, chúng ta sẽ xây dựng tính năng "Rút tiền từ tài khoản ngân hàng". Quy tắc vàng là Use Cases không được gọi trực tiếp DB, mà phải thông qua Interface (Input/Output Ports).

## 1\. Lớp Entities (Vòng trong cùng)

Chứa luật nghiệp vụ tối cao, không đổi dù bạn dùng app Web hay app Mobile.
    
    
    # domain/entities.py
    from dataclasses import dataclass
    
    @dataclass
    class BankAccount:
        account_id: str
        balance: float
    
        def withdraw(self, amount: float):
            if amount <= 0:
                raise ValueError("Số tiền rút phải lớn hơn 0.")
            if amount > self.balance:
                raise ValueError("Số dư tài khoản không đủ.")
            self.balance -= amount
    

## 2\. Lớp Use Cases (Ứng dụng)

Định nghĩa một kịch bản sử dụng (Use Case) cụ thể và định nghĩa cổng giao tiếp (Port) để lấy dữ liệu.
    
    
    # application/ports.py
    from abc import ABC, abstractmethod
    from domain.entities import BankAccount
    
    class AccountRepository(ABC):
        @abstractmethod
        def get_by_id(self, account_id: str) -> BankAccount:
            pass
    
        @abstractmethod
        def save(self, account: BankAccount) -> None:
            pass
    
    
    
    # application/use_cases.py
    from application.ports import AccountRepository
    
    class WithdrawUseCase:
        def __init__(self, account_repo: AccountRepository):
            self.account_repo = account_repo  # Đảo ngược phụ thuộc (DI)
    
        def execute(self, account_id: str, amount: float) -> float:
            # 1. Lấy thực thể thông qua cổng Port
            account = self.account_repo.get_by_id(account_id)
            
            # 2. Thực thi nghiệp vụ lõi của Entity
            account.withdraw(amount)
            
            # 3. Lưu lại trạng thái mới
            self.account_repo.save(account)
            return account.balance
    

## 3\. Lớp Interface Adapters

Đóng vai trò làm cầu nối, chuyển đổi request từ API thành dạng dữ liệu mà Use Case hiểu được.
    
    
    # adapters/controllers.py
    from application.use_cases import WithdrawUseCase
    
    class BankAccountController:
        def __init__(self, withdraw_use_case: WithdrawUseCase):
            self.withdraw_use_case = withdraw_use_case
    
        def handle_withdraw(self, request_data: dict) -> dict:
            # Nhận dữ liệu thô, validate sơ bộ, rồi chuyển vào Use Case
            account_id = request_data.get("account_id")
            amount = float(request_data.get("amount", 0))
            
            try:
                new_balance = self.withdraw_use_case.execute(account_id, amount)
                return {"status": "success", "new_balance": new_balance}
            except ValueError as e:
                return {"status": "error", "message": str(e)}
    

## 4\. Lớp Frameworks & Drivers (Lớp ngoài cùng)

Nơi triển khai cụ thể các thư viện và kết nối DB thực tế.
    
    
    # infrastructure/repositories.py
    from application.ports import AccountRepository
    from domain.entities import BankAccount
    
    class InMemoryAccountRepository(AccountRepository):
        """Triển khai thực tế của Port bằng cách lưu tạm trong RAM"""
        def __init__(self):
            self.storage = {"ACC123": BankAccount(account_id="ACC123", balance=1000.0)}
    
        def get_by_id(self, account_id: str) -> BankAccount:
            if account_id not in self.storage:
                raise ValueError("Không tìm thấy tài khoản.")
            return self.storage[account_id]
    
        def save(self, account: BankAccount) -> None:
            self.storage[account.account_id] = account
            print(f"[DB] Đã cập nhật số dư mới: {account.balance}")
    

## Ráp nối hệ thống tại điểm khởi chạy (Composition Root)
    
    
    # main.py
    from infrastructure.repositories import InMemoryAccountRepository
    from application.use_cases import WithdrawUseCase
    from adapters.controllers import BankAccountController
    
    # 1. Khởi tạo các thành phần từ ngoài vào trong
    repo = InMemoryAccountRepository()
    use_case = WithdrawUseCase(account_repo=repo)
    controller = BankAccountController(withdraw_use_case=use_case)
    
    # 2. Giả lập một lượt gọi API từ phía Client (Frontend) gửi lên
    mock_api_request = {"account_id": "ACC123", "amount": 250.0}
    response = controller.handle_withdraw(mock_api_request)
    
    print("Kết quả API trả về:", response)
    

* * *

## Điểm khác biệt mấu chốt giữa Clean Architecture và Onion Architecture

Mặc dù có chung tư tưởng tách biệt Domain, hai kiến trúc có một vài điểm khác biệt nhỏ về cách tiếp cận:

  * Sự phân ranh giới: Clean Architecture phân chia rất nghiêm ngặt thông qua các khái niệm Boundary, Interactor, Request/Response Model. Dữ liệu đi qua các ranh giới lớp phải là dữ liệu thô (DTO hoặc kiểu dữ liệu nguyên bản như dict, str trong Python) chứ không được bê nguyên Entity ra ngoài lớp Interface Adapters. Trong khi Onion Architecture có phần lỏng lẻo hơn ở các lớp Application Services bên ngoài.
  * Thuật ngữ: Clean gọi lớp xử lý chức năng là _Use Case (hoặc Interactor)_ , Onion gọi là _Application Service_. Clean gọi cổng kết nối dữ liệu là _Gateways/Ports_ , Onion gọi là _Repositories/Interfaces_.



## Quy tắc bất biến khi viết Clean Architecture trong Python

  * Không import ngược: File thuộc thư mục `domain` tuyệt đối không được có dòng code import bất kỳ thứ gì từ `application`, `adapters`, hay `infrastructure`.
  * Sử dụng Type Hinting mạnh mẽ: Tận dụng triệt để tính năng gợi ý kiểu dữ liệu (`account: BankAccount`) và lớp trừu tượng (`abc.ABC`) để giúp trình biên dịch và IDE phát hiện lỗi vi phạm kiến trúc ngay khi gõ code.



Để tiếp tục, bạn có muốn xem một cấu trúc thư mục (Folder Tree) chuẩn hóa theo Clean Architecture cho một dự án Python thực tế không?