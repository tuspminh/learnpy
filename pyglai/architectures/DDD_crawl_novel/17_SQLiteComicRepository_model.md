Dưới đây là mã nguồn hiện thực hoàn chỉnh cho file `domain/model.py` và lớp `SQLiteComicRepository` thuộc tầng _Infrastructure_. Cả hai thành phần này đều tuân thủ chặt chẽ kiến trúc Unit of Work tinh gọn nhận kết nối từ ngoài vào.

* * *

## 1\. File Domain Model Hoàn Chỉnh (`domain/model.py`)

File này chứa toàn bộ cấu trúc nghiệp vụ (Business Rules) cốt lõi của truyện và chương truyện, độc lập hoàn toàn với database.
    
    
    from dataclasses import dataclass
    from datetime import datetime
    from typing import List, Optional
    
    # --- Value Objects ---
    @dataclass(frozen=True)
    class ChapterId:
        value: str  # Định danh: "linh-vuc-chuong-1"
    
    @dataclass(frozen=True)
    class ComicId:
        value: str  # Định danh: "linh-vuc"
    
    # --- Chapter Entity ---
    class Chapter:
        def __init__(
            self, 
            id: ChapterId, 
            comic_id: ComicId, 
            number: int, 
            title: str, 
            content: str, 
            created_at: Optional[datetime] = None
        ):
            self.id = id
            self.comic_id = comic_id
            self.number = number
            self.title = title
            self.content = content
            self.created_at = created_at or datetime.now()
    
        def update_content(self, new_content: str):
            """Domain Logic: Đảm bảo nội dung không được rỗng khi cập nhật"""
            if not new_content or not new_content.strip():
                raise ValueError("Nội dung chương truyện không được phép để trống.")
            self.content = new_content
    
    # --- Comic Aggregate Root ---
    class Comic:
        def __init__(self, id: ComicId, title: str, source_url: str, chapters: Optional[List[Chapter]] = None):
            self.id = id
            self.title = title
            self.source_url = source_url
            self.chapters = chapters or []
    
        def create_and_add_chapter(self, chapter_id: ChapterId, number: int, title: str, content: str) -> Chapter:
            """Domain Logic: Khởi tạo chương mới trực tiếp bên trong Aggregate Root"""
            if number <= 0:
                raise ValueError("Số thứ tự chương phải lớn hơn 0.")
                
            # Kiểm tra trùng lặp chương trên bộ nhớ RAM tạm thời
            for existing_chapter in self.chapters:
                if existing_chapter.id == chapter_id:
                    return existing_chapter
    
            new_chapter = Chapter(
                id=chapter_id,
                comic_id=self.id,
                number=number,
                title=title,
                content=content
            )
            self.chapters.append(new_chapter)
            return new_chapter
    

* * *

## 2\. Định nghĩa Interface Comic Repository (`domain/repository.py`)

Thêm giao diện cho `ComicRepository` vào file repository của tầng Domain.
    
    
    from abc import ABC, abstractmethod
    from typing import Optional
    from .model import Comic, ComicId
    
    class ComicRepository(ABC):
        @abstractmethod
        def save(self, comic: Comic) -> None:
            """Lưu hoặc cập nhật thông tin gốc của truyện (UPSERT)"""
            pass
    
        @abstractmethod
        def get_by_id(self, comic_id: ComicId) -> Optional[Comic]:
            """Lấy thông tin truyện theo ID"""
            pass
    

* * *

## 3\. Hiện thực Lớp Hạ tầng `SQLiteComicRepository` (`infrastructure/sqlite_repository.py`)

Lớp này nhận kết nối dùng chung từ `Unit of Work`, thực thi lưu trữ truyện bằng lệnh SQL thuần túy.
    
    
    import sqlite3
    from typing import Optional
    from domain.model import Comic, ComicId
    from domain.repository import ComicRepository
    
    class SQLiteComicRepository(ComicRepository):
        def __init__(self, connection: sqlite3.Connection):
            """
            Nhận kết nối trực tiếp từ Unit of Work.
            Không tự commit, không tự đóng kết nối.
            """
            self.connection = connection
    
        def save(self, comic: Comic) -> None:
            """Sử dụng kỹ thuật UPSERT để đồng bộ thông tin gốc của truyện"""
            cursor = self.connection.cursor()
            
            sql = """
                INSERT INTO comics (id, title, source_url)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    source_url = excluded.source_url;
            """
            
            cursor.execute(sql, (
                comic.id.value,
                comic.title,
                comic.source_url
            ))
    
        def get_by_id(self, comic_id: ComicId) -> Optional[Comic]:
            """Tìm kiếm truyện dựa vào ID và map dữ liệu về Domain Object"""
            cursor = self.connection.cursor()
            
            sql = "SELECT id, title, source_url FROM comics WHERE id = ?"
            cursor.execute(sql, (comic_id.value,))
            row = cursor.fetchone()
            
            if not row:
                return None
                
            # Map dữ liệu thô sang Domain Object
            return Comic(
                id=ComicId(row[0]),
                title=row[1],
                source_url=row[2]
            )
    

* * *

## 5\. Quy trình điều phối phối hợp giữa 2 Repositories trong UoW

Khi bạn chạy ứng dụng, tầng `Application Service` sẽ gọi qua `Unit of Work` để lưu đồng thời cả Truyện và Chương truyện trên cùng một kết nối, một Transaction:
    
    
    from domain.model import ComicId, Comic
    from domain.unit_of_work import AbstractUnitOfWork
    
    class CrawlerApplicationService:
        def __init__(self, uow: AbstractUnitOfWork):
            self.uow = uow
    
        def execute_crawl_flow(self, comic_slug: str, title: str, url: str, chapter_num: int, ch_title: str, ch_content: str):
            # Mở phiên làm việc duy nhất
            with self.uow:
                comic_id = ComicId(comic_slug)
                
                # 1. Kiểm tra / Khởi tạo truyện bằng ComicRepository
                comic = self.uow.comic_repo.get_by_id(comic_id)
                if not comic:
                    comic = Comic(id=comic_id, title=title, source_url=url)
                    self.uow.comic_repo.save(comic) # Gọi Repo 1
    
                # 2. Tạo chương mới thông qua Aggregate Root
                chapter_slug = f"{comic_slug}-chuong-{chapter_num}"
                from domain.model import ChapterId
                
                new_chapter = comic.create_and_add_chapter(
                    chapter_id=ChapterId(chapter_slug),
                    number=chapter_num,
                    title=ch_title,
                    content=ch_content
                )
    
                # 3. Lưu chương vào DB bằng ChapterRepository
                self.uow.chapter_repo.save_or_update(new_chapter) # Gọi Repo 2
                
                # Kết thúc khối 'with': uow tự động gọi COMMIT cho cả Repo 1 và Repo 2
    

Toàn bộ khung mã nguồn (Scaffold) cốt lõi của ứng dụng theo tư duy DDD kết hợp SQLite thuần SQL tinh gọn đã hoàn tất.

Hệ thống đã sẵn sàng hoạt động. Bạn có muốn tiến hành viết file `main.py` hoàn chỉnh để thiết lập cấu trúc chạy thử nghiệm thực tế với dữ liệu giả lập không?