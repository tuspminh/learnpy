Dưới đây là cách triển khai cụ thể cho bài toán quản lý Novel (Tiểu thuyết) sử dụng SQLite3 (thuần SQL - không dùng ORM), tuân thủ nghiêm ngặt Clean Architecture, DDD và các nguyên lý SOLID trong Python.

## 1\. Tầng Domain (Domain Layer)

Tầng này chứa thực thể `Novel` thuần Python, giữ các quy tắc nghiệp vụ (Business Rules) và hoàn toàn không biết gì về cơ sở dữ liệu.
    
    
    # domain/models.py
    from dataclasses import dataclass
    from typing import Optional
    
    @dataclass
    class Novel:
        id: Optional[int]
        title: str
        author: str
        chapters_count: int
        status: str  # Ví dụ: "DRAFT", "PUBLISHED", "COMPLETED"
    
        def publish(self):
            """Nghiệp vụ: Chỉ cho phép xuất bản nếu truyện đã có ít nhất 1 chương."""
            if self.chapters_count < 1:
                raise ValueError("Không thể xuất bản tiểu thuyết chưa có chương nào.")
            self.status = "PUBLISHED"
    
        def add_chapter(self):
            """Nghiệp vụ: Tăng số chương."""
            self.chapters_count += 1
    

* * *

## 2\. Tầng Application (Interfaces & Use Cases)

Định nghĩa các Interface (Trừu tượng) cho Repository và Unit of Work để tuân thủ nguyên lý Dependency Inversion (DIP).
    
    
    # application/interfaces.py
    from abc import ABC, abstractmethod
    from typing import Optional, List
    from domain.models import Novel
    
    class NovelRepository(ABC):
        @abstractmethod
        def add(self, novel: Novel) -> Novel: pass
    
        @abstractmethod
        def get_by_id(self, novel_id: int) -> Optional[Novel]: pass
    
        @abstractmethod
        def update(self, novel: Novel) -> None: pass
    
    
    class UnitOfWork(ABC):
        novel_repository: NovelRepository
    
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                self.rollback()
            else:
                self.commit()
    
        @abstractmethod
        def commit(self): pass
    
        @abstractmethod
        def rollback(self): pass
    

* * *

## 3\. Tầng Infrastructure (Hạ tầng - SQLite3 Thuần SQL)

Đây là nơi xử lý chi tiết kỹ thuật: Kết nối, Transaction, Mapping và thực thi câu lệnh SQL.

## A. Data Mapper (Chuyển đổi dữ liệu)

Vì dùng SQLite3 thuần, kết quả trả về từ DB là Tuple hoặc Dict. Mapper sẽ chuyển Tuple/Dict này thành `Novel` Domain Entity và ngược lại.
    
    
    # infrastructure/mappers.py
    from domain.models import Novel
    from typing import Any, Dict
    
    class NovelMapper:
        @staticmethod
        def to_domain(row: Dict[str, Any]) -> Novel:
            """Chuyển đổi từ hàng trong DB (Dict) sang Domain Entity."""
            return Novel(
                id=row["id"],
                title=row["title"],
                author=row["author"],
                chapters_count=row["chapters_count"],
                status=row["status"]
            )
    
        @staticmethod
        def to_db_params(novel: Novel) -> Dict[str, Any]:
            """Chuyển đổi từ Domain Entity sang tham số truyền vào câu lệnh SQL."""
            return {
                "id": novel.id,
                "title": novel.title,
                "author": novel.author,
                "chapters_count": novel.chapters_count,
                "status": novel.status
            }
    

## B. Repository Pattern (Thực thi SQL)

Repository chỉ tập trung vào việc Đọc/Ghi dữ liệu thông qua một `cursor` được cấp từ Unit of Work. Nó tuân thủ Single Responsibility (SRP): Không tự quản lý kết nối hay transaction.
    
    
    # infrastructure/repositories.py
    import sqlite3
    from typing import Optional
    from application.interfaces import NovelRepository
    from domain.models import Novel
    from infrastructure.mappers import NovelMapper
    
    class SQLiteNovelRepository(NovelRepository):
        def __init__(self, cursor: sqlite3.Cursor):
            self._cursor = cursor
    
        def add(self, novel: Novel) -> Novel:
            query = """
                INSERT INTO novels (title, author, chapters_count, status)
                VALUES (:title, :author, :chapters_count, :status)
            """
            params = NovelMapper.to_db_params(novel)
            self._cursor.execute(query, params)
            novel.id = self._cursor.lastrowid  # Gán lại ID tự sinh từ SQLite cho Entity
            return novel
    
        def get_by_id(self, novel_id: int) -> Optional[Novel]:
            query = "SELECT id, title, author, chapters_count, status FROM novels WHERE id = ?"
            self._cursor.execute(query, (novel_id,))
            row = self._cursor.fetchone()
            if not row:
                return None
            return NovelMapper.to_domain(row)
    
        def update(self, novel: Novel) -> None:
            query = """
                UPDATE novels 
                SET title = :title, author = :author, chapters_count = :chapters_count, status = :status
                WHERE id = :id
            """
            params = NovelMapper.to_db_params(novel)
            self._cursor.execute(query, params)
    

## C. Unit of Work (Quản lý Connection & Giao dịch)

Sử dụng `sqlite3.connect` và điều khiển transaction thủ công (`BEGIN`, `COMMIT`, `ROLLBACK`). Cấu hình `row_factory = sqlite3.Row` để dữ liệu trả về dạng Dict-like giúp Mapper dễ xử lý.
    
    
    # infrastructure/unit_of_work.py
    import sqlite3
    from application.interfaces import UnitOfWork
    from infrastructure.repositories import SQLiteNovelRepository
    
    class SQLiteUnitOfWork(UnitOfWork):
        def __init__(self, db_path: str):
            self._db_path = db_path
            self._connection = None
            self._cursor = None
    
        def __enter__(self):
            # 1. Khởi tạo kết nối và cấu hình row_factory
            self._connection = sqlite3.connect(self._db_path)
            self._connection.row_factory = sqlite3.Row
            self._cursor = self._connection.cursor()
            
            # Tắt chế độ tự động commit để quản lý transaction thủ công
            self._connection.isolation_level = None 
            self._cursor.execute("BEGIN TRANSACTION;")
            
            # 2. Khởi tạo repository, tiêm cursor dùng chung vào
            self.novel_repository = SQLiteNovelRepository(self._cursor)
            return super().__enter__()
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            try:
                super().__exit__(exc_type, exc_val, exc_tb)
            finally:
                # Luôn giải phóng tài nguyên
                if self._cursor:
                    self._cursor.close()
                if self._connection:
                    self._connection.close()
    
        def commit(self):
            if self._connection:
                self._connection.execute("COMMIT;")
    
        def rollback(self):
            if self._connection:
                self._connection.execute("ROLLBACK;")
    

* * *

## 4\. Sử dụng thực tế (Application Use Case)

Dưới đây là một Use Case cụ thể: Thêm chương và Xuất bản truyện. Hãy xem tầng Nghiệp vụ phối hợp với tầng Hạ tầng mượt mà thế nào:
    
    
    # application/use_cases.py
    from application.interfaces import UnitOfWork
    
    class PublishNovelUseCase:
        def __init__(self, uow: UnitOfWork):
            self.uow = uow  # Nhận vào interface, không phụ thuộc SQLite cụ thể (DIP)
    
        def execute(self, novel_id: int):
            with self.uow as tx:
                # 1. Đọc truyện lên từ DB
                novel = tx.novel_repository.get_by_id(novel_id)
                if not novel:
                    raise ValueError("Không tìm thấy tiểu thuyết.")
    
                # 2. Thực thi nghiệp vụ thay đổi trạng thái truyện
                novel.add_chapter()
                novel.publish()  # Có thể ném lỗi nếu chưa đủ điều kiện
    
                # 3. Lưu cập nhật xuống DB
                tx.novel_repository.update(novel)
                
                # Hết khối lệnh with: Tự động COMMIT nếu không có lỗi, ROLLBACK nếu có lỗi.
    

* * *

## 5\. Khởi chạy ứng dụng (Main / Composition Root)

Đoạn code thiết lập cơ sở dữ liệu ban đầu và chạy thử nghiệm hệ thống.
    
    
    # main.py
    import sqlite3
    from infrastructure.unit_of_work import SQLiteUnitOfWork
    from application.use_cases import PublishNovelUseCase
    from domain.models import Novel
    
    DB_PATH = "app_database.db"
    
    def init_db():
        """Khởi tạo bảng cơ sở dữ liệu mẫu."""
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS novels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                chapters_count INTEGER NOT NULL,
                status TEXT NOT NULL
            );
        """)
        conn.close()
    
    if __name__ == "__main__":
        init_db()
        uow = SQLiteUnitOfWork(DB_PATH)
    
        # ---- BƯỚC 1: TẠO TRUYỆN MỚI (DRAFT) ----
        with uow as tx:
            new_novel = Novel(id=None, title="Chúa tể những chiếc nhẫn", author="J.R.R. Tolkien", chapters_count=0, status="DRAFT")
            tx.novel_repository.add(new_novel)
            print(f"Đã tạo truyện với ID: {new_novel.id}")
            # Tự động COMMIT ở đây
    
        # ---- BƯỚC 2: CHẠY USE CASE XUẤT BẢN ----
        publish_service = PublishNovelUseCase(uow)
        try:
            publish_service.execute(novel_id=1)
            print("Xuất bản truyện thành công!")
        except Exception as e:
            print(f"Thất bại: {e}")
    
        # ---- BƯỚC 3: KIỂM TRA LẠI DỮ LIỆU ----
        with uow as tx:
            updated_novel = tx.novel_repository.get_by_id(1)
            print(f"Trạng thái truyện sau Use Case: {updated_novel}")
    

## Điểm mấu chốt đạt được:

  1. SQLite cô lập hoàn toàn: Toàn bộ chuỗi lệnh `INSERT`, `UPDATE`, `BEGIN TRANSACTION` đều nằm gọn ở tầng `Infrastructure`.
  2. Không rò rỉ Logic: Luật nghiệp vụ `if self.chapters_count < 1` nằm trọn trong tầng `Domain`, bảo vệ toàn vẹn dữ liệu từ tầng lõi.
  3. Mã nguồn Pythonic: Quản lý giao dịch bằng từ khóa `with` của Python giúp giảm thiểu tối đa việc quên đóng kết nối hoặc sót lệnh Rollback khi hệ thống gặp sự cố bất ngờ.



Nếu bạn muốn tiếp tục mở rộng cấu trúc này, hãy cho tôi biết:

  * Bạn có cần tổ chức mã nguồn này thành các thư mục/package chuẩn của một dự án Python không?
  * Bạn có muốn tích hợp thêm Domain Events (ví dụ: gửi thông báo cho độc giả khi truyện được xuất bản thành công) không?