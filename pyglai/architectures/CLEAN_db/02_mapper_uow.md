Việc bổ sung Model Mapper là rất cần thiết trong Clean Architecture để cắt đứt sự phụ thuộc của lõi (Domain) vào database. Đối với Unit of Work (UoW), câu trả lời là: Rất cần đối với ứng dụng crawl truyện, vì một phiên cào dữ liệu thường phải lưu đồng thời nhiều bảng (Truyện, Chương, Lịch sử cào) và cần tính toàn vẹn dữ liệu (Atomicity).

Dưới đây là thiết kế chi tiết khi tích hợp hai thành phần này bằng Python theo chuẩn SOLID.

* * *

## 1\. Model Mapper: Tại sao cần và Triển khai thế nào?

Lý do: Khi dùng các thư viện DB hoặc ORM (SQLAlchemy, Peewee, PyMySQL), dữ liệu trả về thường là một `dict` hoặc một Model của ORM (đầy rẫy các phương thức liên quan đến database). Nếu bạn mang Model đó vào lớp `Domain/Use Case`, bạn đã vi phạm Clean Architecture.

Model Mapper đóng vai trò là "biên dịch viên" ở biên của lớp Infrastructure:

  * `to_domain`: Chuyển dữ liệu từ DB (Dict/ORM Model) thành Domain Entity sạch.
  * `to_infrastructure`: Chuyển Domain Entity thành dạng DB có thể hiểu để lưu (Dict/Tuple).



## Triển khai Model Mapper:
    
    
    # src/infrastructure/database/mappers.py
    from src.domain.entities import Story
    
    class StoryMapper:
        @staticmethod
        def to_domain(db_row: dict) -> Story:
            """Chuyển đổi từ dữ liệu thô DB thành Domain Entity sạch"""
            if not db_row:
                return None
            return Story(
                id=db_row["id"],
                title=db_row["title"],
                author=db_row["author"],
                slug=db_row["slug"],
                description=db_row.get("description")
            )
    
        @staticmethod
        def to_infrastructure(story: Story) -> dict:
            """Chuyển từ Domain Entity thành dict để chuẩn bị câu lệnh INSERT/UPDATE"""
            return {
                "id": story.id,
                "title": story.title,
                "author": story.author,
                "slug": story.slug,
                "description": story.description
            }
    

* * *

## 2\. Unit of Work (UoW): Tại sao app Crawl truyện lại cần?

Trong app crawl truyện, khi bạn cào thành công một chương mới, bạn phải thực hiện chuỗi hành động:

  1. `INSERT` vào bảng `chapters` (nội dung chương).
  2. `UPDATE` bảng `stories` (cập nhật số lượng chương mới nhất, thời gian cập nhật).
  3. `UPDATE` bảng `crawl_queue` (đổi trạng thái URL từ `processing` sang `done`).



Nếu bước 1 và 2 thành công nhưng bước 3 lỗi (hoặc mất điện), dữ liệu sẽ bị lệch (chương đã lưu nhưng hàng đợi vẫn báo chưa cào -> lần sau cào lại bị trùng). Unit of Work quản lý một Transaction duy nhất cho cả 3 hành động này: Cùng thành công hoặc cùng thất bại (Rollback).

## Bước 2.1: Định nghĩa Interface UoW tại lớp Domain
    
    
    # src/domain/repositories.py
    from abc import ABC, abstractmethod
    
    class IUnitOfWork(ABC):
        story_repo: any
        chapter_repo: any
        queue_repo: any
    
        @abstractmethod
        def __enter__(self):
            pass
    
        @abstractmethod
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
    
        @abstractmethod
        def commit(self) -> None:
            pass
    
        @abstractmethod
        def rollback(self) -> None:
            pass
    

## Bước 2.2: Triển khai UoW chi tiết tại lớp Infrastructure

Lúc này, UoW sẽ thay thế `DbContextManager` cũ, đóng vai trò quản lý vòng đời kết nối và transaction. Các Repository sẽ dùng chung một connection/cursor do UoW cấp phát.
    
    
    # src/infrastructure/database/unit_of_work.py
    from src.domain.repositories import IUnitOfWork
    from src.infrastructure.database.mysql_repositories import MySqlStoryRepository
    # từ các repo khác...
    
    class MySqlUnitOfWork(IUnitOfWork):
        def __init__(self, db_client):
            self.db_client = db_client
            self.connection = None
            self.cursor = None
    
        def __enter__(self):
            # Mượn 1 connection từ pool và bắt đầu Transaction
            self.connection = self.db_client.get_connection()
            self.connection.start_transaction()
            self.cursor = self.connection.cursor(dictionary=True)
    
            # Inject chung cursor/connection vào các Repository để đảm bảo dùng chung 1 Transaction
            self.story_repo = MySqlStoryRepository(self.cursor)
            # self.chapter_repo = MySqlChapterRepository(self.cursor)
            return self
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                self.rollback() # Tự động rollback nếu có exception trong khối 'with'
            else:
                self.commit()   # Tự động commit nếu chạy mượt mà
                
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close() # Trả connection về pool
    
        def commit(self):
            if self.connection:
                self.connection.commit()
    
        def rollback(self):
            if self.connection:
                self.connection.rollback()
    

* * *

## 3\. Cập nhật lại Repository và Use Case (Kết hợp Mapper + UoW)

## Thay đổi ở Repository:

Repository bây giờ rất đơn giản, không tự quản lý connection nữa mà nhận `cursor` từ UoW giao phó, đồng thời dùng `Mapper` để trả về Entity sạch.
    
    
    # src/infrastructure/database/mysql_repositories.py
    from src.infrastructure.database.mappers import StoryMapper
    from src.domain.entities import Story
    
    class MySqlStoryRepository:
        def __init__(self, cursor):
            self.cursor = cursor  # Nhận cursor dùng chung từ UoW
    
        def find_by_source_url(self, url: str) -> Optional[Story]:
            query = "SELECT s.* FROM stories s JOIN story_source_mappings m ON s.id = m.story_id WHERE m.remote_url = %s LIMIT 1"
            self.cursor.execute(query, (url,))
            row = self.cursor.fetchone()
            # Dùng Mapper chuyển đổi raw DB sang Domain Entity
            return StoryMapper.to_domain(row)
    
        def create(self, story: Story) -> None:
            # Dùng Mapper chuyển đổi Entity sang dict để insert
            data = StoryMapper.to_infrastructure(story)
            query = "INSERT INTO stories (id, title, author, slug) VALUES (%(id)s, %(title)s, %(author)s, %(slug)s)"
            self.cursor.execute(query, data)
    

## Thay đổi ở Use Case (Tuyệt đẹp và cô lập):

Lớp Use Case giờ đây không nhận từng Repo lẻ tẻ nữa, nó chỉ nhận đúng `IUnitOfWork`. Toàn bộ công đoạn lưu trở thành một giao dịch nguyên tử (Atomic).
    
    
    # src/use_cases/save_chapter_pipeline.py
    from src.domain.repositories import IUnitOfWork
    from src.domain.entities import Chapter
    
    class SaveChapterPipelineUseCase:
        def __init__(self, uow: IUnitOfWork):
            self.uow = uow  # Chỉ phụ thuộc vào Interface UoW
    
        def execute(self, raw_data: dict) -> None:
            # 1. Khởi chạy Transaction thông qua Context Manager của UoW
            with self.uow:
                # Bước A: Tìm truyện có sẵn
                story = self.uow.story_repo.find_by_source_url(raw_data["source_url"])
                if not story:
                    raise ValueError("Truyện không tồn tại để thêm chương.")
    
                # Bước B: Tạo Entity chương mới và lưu
                new_chapter = Chapter(story_id=story.id, title=raw_data["chapter_title"], content=raw_data["content"])
                self.uow.chapter_repo.create(new_chapter)
    
                # Bước C: Cập nhật trạng thái hàng đợi cào thành 'done'
                self.uow.queue_repo.update_status(raw_data["queue_id"], "done")
                
                # Khối 'with' kết thúc tại đây -> UoW tự động commit tất cả các bước trên cùng lúc.
                # Nếu bất kỳ bước nào lỗi (ví dụ text chương quá dài gây crash DB), toàn bộ tiến trình sẽ rollback.
    

* * *

## 📊 Tóm tắt vai trò khi kết hợp

Thành phần| Nhiệm vụ chính trong App Crawl| Thuộc lớp nào trong Clean Arch  
---|---|---  
Model Mapper| Đảm bảo Domain Entity hoàn toàn sạch bóng, không dính líu tới cấu trúc hay thư viện DB.| Infrastructure  
Unit of Work| Gom cụm các hành động (Lưu chương + Đổi trạng thái hàng đợi) vào một Transaction để tránh mất mát/lệch dữ liệu khi crawler bị ngắt giữa chừng.| Interface: Domain / Impl: Infra  
  
Bạn thấy cấu trúc phối hợp giữa Mapper và Unit of Work này đã giải quyết triệt để bài toán an toàn dữ liệu của bạn chưa? Nếu bạn muốn, tôi có thể hỗ trợ thiết kế tiếp phần Xử lý Exception / Retry logic khi Transaction bị lỗi do Deadlock (rất hay gặp khi nhiều worker crawl cùng ghi vào DB một lúc).