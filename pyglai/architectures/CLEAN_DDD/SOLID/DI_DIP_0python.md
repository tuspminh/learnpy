Trong Python, do có đặc tính Duck Typing (định kiểu động), việc áp dụng DIP và DI sẽ có một chút khác biệt thú vị. Bạn không bắt buộc phải khai báo từ khóa `interface` như Java hay TypeScript, nhưng bạn vẫn nên dùng module `abc` (Abstract Base Classes) để định nghĩa tính trừu tượng một cách rõ ràng.

Dưới đây là hướng dẫn chi tiết cách kết hợp DIP và DI trong Python, từ code thuần cho đến việc sử dụng thư viện tự động.

* * *

## ❌ Khi chưa áp dụng DIP và DI (Thiết kế tồi)

Lớp cấp cao `OrderManager` tự khởi tạo trực tiếp lớp cấp thấp `MySQLDatabase`.
    
    
    class MySQLDatabase:
        def save_order(self, order_id: str):
            print(f"Đang lưu đơn hàng {order_id} vào MySQL...")
    
    class OrderManager:
        def __init__(self):
            # Tự khởi tạo trực tiếp -> Dính chặt (Tightly Coupled)
            self.database = MySQLDatabase()
    
        def create_order(self, order_id: str):
            self.database.save_order(order_id)
    

* * *

## Cách kết hợp DIP và DI trong Python (Chuẩn hóa)

Chúng ta sẽ dùng lớp trừu tượng `ABC` để làm "Interface" (DIP) và truyền đối tượng qua hàm `__init__` (DI).
    
    
    from abc import ABC, abstractmethod
    
    # ==========================================
    # BƯỚC 1: Tạo Abstraction bằng ABC (Theo nguyên lý DIP)
    # ==========================================
    class Database(ABC):
        @abstractmethod
        def save_order(self, order_id: str) -> None:
            pass
    
    # ==========================================
    # BƯỚC 2: Các module cấp thấp triển khai trừu tượng
    # ==========================================
    class MySQLDatabase(Database):
        def save_order(self, order_id: str) -> None:
            print(f"Lưu đơn hàng {order_id} vào MySQL.")
    
    class MongoDatabase(Database):
        def save_order(self, order_id: str) -> None:
            print(f"Lưu đơn hàng {order_id} vào MongoDB.")
    
    # ==========================================
    # BƯỚC 3: Module cấp cao nhận trừu tượng qua DI (Constructor Injection)
    # ==========================================
    class OrderManager:
        # Sử dụng Type Hinting để chỉ định phụ thuộc vào Database (Trừu tượng)
        def __init__(self, database: Database):
            self.database = database  # DI: Bơm phụ thuộc từ ngoài vào
    
        def create_order(self, order_id: str):
            self.database.save_order(order_id)
    
    # ==========================================
    # CÁCH VẬN HÀNH TRONG THỰC TẾ (Manual DI)
    # ==========================================
    # Dùng MySQL
    mysql_db = MySQLDatabase()
    manager_mysql = OrderManager(database=mysql_db)
    manager_mysql.create_order("HD001")
    
    # Đổi sang MongoDB mà KHÔNG cần sửa bất kỳ dòng code nào trong lớp OrderManager
    mongo_db = MongoDatabase()
    manager_mongo = OrderManager(database=mongo_db)
    manager_mongo.create_order("HD002")
    

* * *

## 🤖 Tự động hóa DI với thư viện `dependency-injector`

Trong các dự án Python lớn (như Django, FastAPI, Flask), việc tự kết nối các lớp bằng tay (Manual DI) sẽ rất cồng kềnh. Thư viện phổ biến nhất để giải quyết việc này là `dependency-injector`.

Để sử dụng, bạn cài đặt qua terminal: `pip install dependency-injector`

Sau đó cấu hình hệ thống tự động "bơm" như sau:
    
    
    from dependency_injector import containers, providers
    from dependency_injector.wiring import Provide, inject
    
    # 1. Khai báo Container quản lý các phụ thuộc
    class Container(containers.DeclarativeContainer):
        # Cấu hình: Khi cần Database, hệ thống sẽ trả về MongoDatabase
        # Bạn chỉ cần đổi MongoDatabase thành MySQLDatabase tại đây để thay đổi toàn bộ hệ thống
        database_provider = providers.Factory(MongoDatabase)
    
    # 2. Sử dụng Decorator @inject để tự động lấy phụ thuộc từ Container
    @inject
    def main(order_manager: OrderManager = Provide[Container.database_provider]):
        # Thư viện sẽ tự động khởi tạo Database và nạp vào OrderManager cho bạn
        manager = OrderManager(order_manager)
        manager.create_order("HD003")
    
    if __name__ == "__main__":
        container = Container()
        container.wire(modules=[__name__])
        main()
    

* * *

## 🧪 Lợi ích tối thượng: Viết Unit Test cực kỳ dễ dàng

Khi đã tách rời phụ thuộc bằng DI, bạn có thể dễ dàng tạo ra một Database giả (`Mock`) để kiểm thử lớp `OrderManager` mà không cần phải kết nối vào cơ sở dữ liệu thật.
    
    
    import unittest
    from unittest.mock import MagicMock
    
    class TestOrderManager(unittest.TestCase):
        def test_create_order_calls_save_order(self):
            # Tạo một database giả dựa trên lớp trừu tượng Database
            mock_db = MagicMock(spec=Database)
            
            # Tiêm mock_db vào OrderManager
            manager = OrderManager(database=mock_db)
            manager.create_order("TEST_ID")
            
            # Kiểm tra xem hàm save_order đã được gọi đúng với tham số chưa
            mock_db.save_order.assert_called_once_with("TEST_ID")
    
    if __name__ == "__main__":
        unittest.main()
    

* * *

Nếu bạn muốn tiếp tục tối ưu mã nguồn Python của mình, hãy cho tôi biết:

  * Bạn đang làm việc với Framework nào (FastAPI, Django, Flask)? Tôi sẽ hướng dẫn cách thiết lập DI chuẩn cho framework đó.
  * Bạn có muốn xem cách áp dụng DIP/DI vào mô hình kiến trúc Hexagonal Architecture hoặc Clean Architecture trong Python không?