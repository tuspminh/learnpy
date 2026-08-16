Version:0.9 StartHTML:0000000105 EndHTML:0000018523 StartFragment:0000000141 EndFragment:0000018487 

Q

app/model/novel.py, app/repository/novel_repository.py, app/services/novel_service.py

GLAI

Để tổ chức dự án theo mô hình 3 tầng (**Layered Architecture / 3-Tier Architecture**) chuẩn chỉnh, chúng ta sẽ đặt code vào thư mục `app/` và phân tách rõ ràng trách nhiệm:

  * **Model** : Định nghĩa cấu trúc dữ liệu thực thể (Data Entity).
  * **Repository** : Giao tiếp trực tiếp với Database bằng SQL thuần qua `SQLiteSession`.
  * **Service** : Chứa logic nghiệp vụ (Business Logic), điều phối dữ liệu từ Repository và xử lý các điều kiện logic trước khi trả về cho tầng điều khiển (Coordinator/API).



Dưới đây là mã nguồn hoàn chỉnh, đồng bộ cho cả 3 tệp tin theo cấu trúc mới:

* * *

**📦 1. TẦNG DATA MODEL**

**📄 app/model/novel.py**

Sử dụng `dataclasses` để tạo cấu trúc dữ liệu thực thể sạch, đóng gói kèm theo Enum trạng thái để đảm bảo an toàn kiểu dữ liệu (Type Safety).

python
    
    
    # app/model/novel.py
    from dataclasses import dataclass, asdict
    from enum import Enum
    from typing import Optional, Any
    
    class NovelStatus(Enum):
        ONGOING = "Đang tiến hành"
        COMPLETED = "Hoàn thành"
        PAUSED = "Tạm ngưng"
        UNKNOWN = "Không rõ"
    
    @dataclass
    class Novel:
        website_id: int
        title: str
        slug: str
        id: Optional[int] = None
        author: str = "Không rõ"
        status: NovelStatus = NovelStatus.UNKNOWN
        genres: list[str] = None  # Sẽ được lưu dạng chuỗi "A, B, C" trong Database
        description: str = ""
        created_at: Optional[str] = None
    
        def __post_init__(self):
            # Đảm bảo thuộc tính genres luôn luôn là một danh sách mảnh (list)
            if self.genres is None:
                self.genres = []
                
            # Tự động chuẩn hóa kiểu dữ liệu nếu truyền vào dạng chuỗi (String) từ DB
            if isinstance(self.status, str):
                try:
                    self.status = NovelStatus(self.status)
                except ValueError:
                    self.status = NovelStatus.UNKNOWN
    
        def to_dict(self) -> dict[str, Any]:
            """Chuyển đổi thực thể Object thành Dictionary sạch để xử lý I/O hoặc JSON."""
            data = asdict(self)
            data["status"] = self.status.value  # Ép giá trị Enum thành chuỗi thô
            return data
    

Hãy thận trọng khi sử dụng mã.

* * *

**📦 2. TẦNG DATA ACCESS (REPOSITORY)**

**📄 app/repository/novel_repository.py**

Tầng thực thi các câu lệnh SQL vật lý tương tác trực tiếp với tệp cơ sở dữ liệu `sqlite3` thông qua `SQLiteSession`.

python
    
    
    # app/repository/novel_repository.py
    import sqlite3
    from typing import Optional
    from database.session import SQLiteSession
    from app.model.novel import Novel, NovelStatus
    
    class NovelRepository:
        def get_by_id(self, session: SQLiteSession, novel_id: int) -> Optional[Novel]:
            """Tìm kiếm truyện dựa trên ID khóa chính."""
            query = "SELECT * FROM novels WHERE id = ?;"
            cursor = session.execute(query, (novel_id,))
            row = cursor.fetchone()
            return self._map_row_to_entity(row) if row else None
    
        def get_by_slug(self, session: SQLiteSession, slug: str) -> Optional[Novel]:
            """Tìm kiếm truyện dựa trên định danh duy nhất (slug)."""
            query = "SELECT * FROM novels WHERE slug = ?;"
            cursor = session.execute(query, (slug,))
            row = cursor.fetchone()
            return self._map_row_to_entity(row) if row else None
    
        def save(self, session: SQLiteSession, novel: Novel) -> int:
            """Thực hiện chèn mới hoặc cập nhật thông tin (Upsert) một thực thể Novel."""
            genres_str = ", ".join(novel.genres)
            existing = self.get_by_slug(session, novel.slug)
            
            if existing:
                query = """
                    UPDATE novels 
                    SET title = ?, author = ?, status = ?, genres = ?, description = ?
                    WHERE id = ?;
                """
                session.execute(query, (
                    novel.title, novel.author, novel.status.value, 
                    genres_str, novel.description, existing.id
                ))
                novel.id = existing.id
                return existing.id
            else:
                query = """
                    INSERT INTO novels (website_id, title, slug, author, status, genres, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """
                cursor = session.execute(query, (
                    novel.website_id, novel.title, novel.slug, novel.author, 
                    novel.status.value, genres_str, novel.description
                ))
                novel.id = cursor.lastrowid
                return cursor.lastrowid
    
        def _map_row_to_entity(self, row: sqlite3.Row) -> Novel:
            """Hàm Mapper cục bộ: Biến đổi cấu trúc bảng thô thành thực thể Python Object."""
            genres_list = [g.strip() for g in row["genres"].split(",") if g.strip()] if row["genres"] else []
            return Novel(
                id=row["id"],
                website_id=row["website_id"],
                title=row["title"],
                slug=row["slug"],
                author=row["author"],
                status=NovelStatus(row["status"]),
                genres=genres_list,
                description=row["description"],
                created_at=row["created_at"]
            )
    

Hãy thận trọng khi sử dụng mã.

* * *

**📦 3. TẦNG LOGIC NGHIỆP VỤ (BUSINESS SERVICE)**

**📄 app/services/novel_service.py**

Tầng nắm giữ luật xử lý dữ liệu. Nó tiếp nhận `SQLiteEngine` để tự điều phối vòng đời khai mở `SQLiteSession`, thực hiện kiểm tra logic (ví dụ: chuẩn hóa tên chữ, chặn trùng lặp, log hệ thống) trước khi đẩy xuống ổ đĩa.

python
    
    
    # app/services/novel_service.py
    import logging
    from typing import Optional
    from database.engine import SQLiteEngine
    from database.session import SQLiteSession
    from app.model.novel import Novel
    from app.repository.novel_repository import NovelRepository
    
    logger = logging.getLogger(__name__)
    
    class NovelService:
        def __init__(self, engine: SQLiteEngine):
            self.engine = engine
            self.novel_repo = NovelRepository()
    
        def get_novel_details(self, slug: str) -> Optional[Novel]:
            """Lấy thông tin chi tiết của một bộ truyện an toàn bọc trong Session."""
            with SQLiteSession(self.engine) as session:
                return self.novel_repo.get_by_slug(session, slug)
    
        def process_crawled_novel(self, website_id: int, slug: str, raw_data: dict) -> Novel:
            """Xử lý hậu kỳ dữ liệu cào thô, áp dụng logic nghiệp vụ và lưu trữ bền vững."""
            # Nghiệp vụ 1: Chuẩn hóa, làm sạch văn bản (Viết hoa chữ cái đầu tiêu đề truyện)
            clean_title = raw_data["title"].strip().title()
            
            # Nghiệp vụ 2: Khởi tạo thực thể Object an toàn từ dữ liệu thô
            novel_entity = Novel(
                website_id=website_id,
                title=clean_title,
                slug=slug.strip().lower(),
                author=raw_data.get("author", "Không rõ").strip(),
                status=raw_data.get("status", "Không rõ"),
                genres=raw_data.get("genres", []),
                description=raw_data.get("description", "").strip()
            )
    
            # Nghiệp vụ 3: Mở một transaction duy nhất để ghi dữ liệu bền vững
            with SQLiteSession(self.engine) as session:
                logger.info(f"[Service] Tiến hành lưu trữ dữ liệu cho truyện: {novel_entity.slug}")
                self.novel_repo.save(session, novel_entity)
                
            logger.info(f"[Service] Lưu hoàn tất truyện '{novel_entity.title}' với ID hệ thống: {novel_entity.id}")
            return novel_entity
    

Hãy thận trọng khi sử dụng mã.

* * *

**🚀 Hướng dẫn tích hợp sử dụng trong main.py**

Khi cấu trúc của bạn đã tách lớp rõ ràng, việc gọi thực thi luồng chạy tại file đầu não dự án sẽ trở nên vô cùng mạch lạc và chuyên nghiệp:

python
    
    
    # Ví dụ áp dụng trong main.py
    from database.config import DatabaseConfig
    from database.engine import SQLiteEngine
    from app.services.novel_service import NovelService
    
    def main():
        # 1. Khởi tạo hạ tầng DB ở Core
        config = DatabaseConfig(db_name="crawler_layered.db")
        engine = SQLiteEngine(config)
        
        # 2. Khởi tạo Service nghiệp vụ (Chỉ cần truyền engine vào một lần duy nhất)
        novel_service = NovelService(engine)
        
        # Giả lập dữ liệu thô từ một plugin cào về (ví dụ: truyenfull)
        mock_raw_data = {
            "title": "tinh thần biến",
            "author": "Ngã Cật Tây Hồng Thị",
            "status": "Hoàn thành",
            "genres": ["Tiên Hiệp", "Huyền Huyễn"],
            "description": "Hành trình tu luyện đầy gian khổ của Tần Vũ..."
        }
        
        # 3. Điều phối xử lý qua tầng Service (Không cần tự quản lý Session/SQL ở đây)
        novel = novel_service.process_crawled_novel(
            website_id=1, 
            slug="tinh-than-bien", 
            raw_data=mock_raw_data
        )
        
        print(f"🎉 Kết quả xử lý hướng đối tượng: {novel.to_dict()}")
    
    if __name__ == "__main__":
        main()
    

Hãy thận trọng khi sử dụng mã.

Để hoàn thiện trọn vẹn bộ khung 3 tầng cho cả dự án, bạn có muốn tôi viết tiếp các file tương ứng cho thực thể chương truyện là **app/model/chapter.py** , **app/repository/chapter_repository.py** , và **app/services/chapter_service.py** không?

