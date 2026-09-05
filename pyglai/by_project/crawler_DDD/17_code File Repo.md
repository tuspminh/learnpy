Dưới đây là mã nguồn chi tiết cho tệp `infrastructure/repositories/file_repo.py` phục vụ cấu trúc dự án phẳng. Tệp này được thiết kế theo đúng chuẩn Clean Architecture / DDD, tuân thủ nguyên lý Liskov Substitution (L trong SOLID) để có thể hoán đổi hoàn hảo với SQLite hay MongoDB.

Để giải quyết bài toán cào dữ liệu phân cấp lớn mà không làm phình RAM, `FileLocalRepository` sẽ lưu trữ dữ liệu theo cấu trúc thư mục thông minh:

  * Thông tin danh sách truyện tổng hợp (`Listing`) được ghi tập trung tại một file JSON chung.
  * Mỗi truyện (`Novel Detail`) sẽ có một thư mục riêng biệt đặt tên theo dạng `slug` an toàn.
  * Danh sách chương (`Chapter List`) lưu thành file JSON nằm trong thư mục truyện đó.
  * Nội dung chữ của từng chương (`Chapter Detail`) - vốn rất nặng - sẽ được ghi thành từng file văn bản `.txt` riêng biệt trong thư mục con `chapters/`.



* * *

## 💻 Triển Khai Mã Nguồn `infrastructure/repositories/file_repo.py`
    
    
    # infrastructure/repositories/file_repo.py
    import os
    import json
    import re
    import logging
    from typing import List, Optional
    from application.interfaces import NovelRepositoryInterface
    from domain.models import NovelListItem, NovelDetail, ChapterItem, ChapterDetail
    
    logger = logging.getLogger(__name__)
    
    class FileLocalRepository(NovelRepositoryInterface):
        """
        Triển khai kho lưu trữ truyện thành cấu trúc tệp tin/thư mục cục bộ (SOLID - L).
        Tối ưu hóa I/O bằng cách chia nhỏ file, tránh load dữ liệu lớn vào bộ nhớ.
        """
        def __init__(self, output_dir: str):
            self._output_dir = output_dir
            if not os.path.exists(self._output_dir):
                os.makedirs(self._output_dir)
    
        def _slugify(self, text: str) -> str:
            """Chuyển đổi tên truyện tiếng Việt thành tên thư mục an toàn (Ví dụ: 'Đấu Phá Thương Khung' -> 'dau-pha-thuong-khung')"""
            text = text.lower()
            text = re.sub(r'[áàảãạăắằẳẵặâấầẩẫậ]', 'a', text)
            text = re.sub(r'[éèẻẽẹêếềểễệ]', 'e', text)
            text = re.sub(r'[óòỏõọôốồổỗộơớờởỡợ]', 'o', text)
            text = re.sub(r'[íìỉĩị]', 'i', text)
            text = re.sub(r'[úùủũụưứừửữự]', 'u', text)
            text = re.sub(r'[ýỳỷỹỵ]', 'y', text)
            text = re.sub(r'đ', 'd', text)
            text = re.sub(r'[^a-z0-9\s-]', '', text)
            return re.sub(r'[\s-]+', '-', text).strip('-')
    
        def _get_novel_dir(self, novel_title: str) -> str:
            """Lấy đường dẫn thư mục riêng biệt của một bộ truyện"""
            novel_dir = os.path.join(self._output_dir, self._slugify(novel_title))
            if not os.path.exists(novel_dir):
                os.makedirs(novel_dir)
            return novel_dir
    
        def save_listing(self, items: List[NovelListItem]) -> None:
            """Lưu cuốn chiếu danh sách truyện. Đọc file cũ lên, gộp dữ liệu mới và ghi đè an toàn."""
            file_path = os.path.join(self._output_dir, "listing_novels.json")
            existing_data = []
    
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        existing_data = json.load(f)
                except Exception as e:
                    logger.warning(f"⚠️ Thất bại khi đọc file listing cũ, tiến hành ghi mới: {e}")
    
            # Chuyển đổi danh sách mới sang định dạng Dict và gộp dựa trên URL để tránh trùng lặp
            url_set = {item["novel_url"] for item in existing_data}
            for item in items:
                if item.novel_url not in url_set:
                    existing_data.append({
                        "title": item.title,
                        "novel_url": item.novel_url
                    })
    
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)
            logger.debug(f"💾 Đã cập nhật {len(items)} mục vào file listing tổng.")
    
        def save_novel_detail(self, detail: NovelDetail) -> None:
            """Lưu thông tin chi tiết của một truyện thành file detail.json nằm riêng trong thư mục truyện"""
            novel_dir = self._get_novel_dir(detail.title)
            file_path = os.path.join(novel_dir, "detail.json")
            
            # Ghi đè hoặc tạo mới thông tin chi tiết truyện
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(detail.__dict__, f, ensure_ascii=False, indent=4)
            logger.debug(f"💾 Đã lưu thông tin chi tiết truyện: {detail.title}")
    
        def save_chapters(self, novel_url: str, chapters: List[ChapterItem]) -> None:
            """Lưu danh sách chương của truyện. Cần quét file detail để tìm đúng thư mục truyện tương ứng."""
            novel_dir = self._find_novel_dir_by_url(novel_url)
            if not novel_dir:
                logger.error(f"❌ Không tìm thấy thư mục truyện tương ứng với URL: {novel_url}. Vui lòng cào Novel Detail trước.")
                return
    
            file_path = os.path.join(novel_dir, "chapters_list.json")
            existing_chapters = []
    
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        existing_chapters = json.load(f)
                except Exception:
                    pass
    
            # Gộp danh sách chương mới
            url_set = {ch["chapter_url"] for ch in existing_chapters}
            for ch in chapters:
                if ch.chapter_url not in url_set:
                    existing_chapters.append({
                        "title": ch.title,
                        "chapter_url": ch.chapter_url,
                        "order_index": ch.order_index
                    })
    
            # Sắp xếp lại danh sách chương theo đúng thứ tự (order_index)
            existing_chapters.sort(key=lambda x: x["order_index"])
    
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(existing_chapters, f, ensure_ascii=False, indent=4)
            logger.debug(f"💾 Đã lưu danh sách chương vào thư mục: {novel_dir}")
    
        def save_chapter_detail(self, detail: ChapterDetail) -> None:
            """Lưu nội dung chữ của chương thành file .txt riêng biệt để tối ưu RAM"""
            novel_dir = self._find_novel_dir_by_url(detail.novel_url)
            if not novel_dir:
                logger.error(f"❌ Không tìm thấy thư mục truyện cho chương '{detail.title}'.")
                return
    
            # Tạo thư mục con 'chapters' bên trong thư mục truyện
            chapters_dir = os.path.join(novel_dir, "chapters")
            if not os.path.exists(chapters_dir):
                os.makedirs(chapters_dir)
    
            # Định dạng tên file chương an toàn dựa trên tiêu đề chương
            file_name = f"{self._slugify(detail.title)}.txt"
            file_path = os.path.join(chapters_dir, file_name)
    
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"=== {detail.title} ===\n\n")
                f.write(detail.content)
            logger.debug(f"💾 Đã xuất file nội dung chương: {file_name}")
    
        def get_by_url(self, url: str) -> Optional[NovelDetail]:
            """Tìm kiếm thông tin truyện dựa trên URL nguồn để kiểm tra trùng lặp dữ liệu"""
            novel_dir = self._find_novel_dir_by_url(url)
            if not novel_dir:
                return None
    
            try:
                with open(os.path.join(novel_dir, "detail.json"), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return NovelDetail(
                        title=data["title"],
                        author=data["author"],
                        description=data["description"],
                        novel_url=data["novel_url"],
                        cover_image_url=data.get("cover_image_url")
                    )
            except Exception:
                return None
    
        def _find_novel_dir_by_url(self, novel_url: str) -> Optional[str]:
            """Hàm hỗ trợ duyệt qua các thư mục hiện có để tìm thư mục truyện khớp với URL nguồn"""
            if not os.path.exists(self._output_dir):
                return None
    
            for item in os.listdir(self._output_dir):
                sub_dir = os.path.join(self._output_dir, item)
                if os.path.isdir(sub_dir):
                    detail_file = os.path.join(sub_dir, "detail.json")
                    if os.path.exists(detail_file):
                        try:
                            with open(detail_file, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                if data.get("novel_url") == novel_url:
                                    return sub_dir
                        except Exception:
                            continue
            return None
    

* * *

## 🎨 Cách Thức Kích Hoạt Trong Hệ Thống

Để chuyển đổi toàn bộ ứng dụng sang lưu trữ bằng cấu trúc tệp tin cục bộ này, bạn chỉ cần nạp nó vào tệp `main.py` thông qua lớp bọc `DummyUnitOfWork` (vì hệ thống File đồng bộ đã tự đảm bảo ghi luồng cuộn cuốn chiếu theo hàm).
    
    
    # Cấu hình đổi dữ liệu lưu trữ tại main.py
    from infrastructure.repositories.file_repo import FileLocalRepository
    from infrastructure.repositories.dummy_uow import DummyUnitOfWork
    
    # Thay thế phân hệ UoW cũ bằng File System UoW
    file_repo = FileLocalRepository(output_dir=settings.FILE_OUTPUT_DIR)
    uow = DummyUnitOfWork(repository=file_repo)
    
    # Tiến hành inject uow này vào NovelCrawlerApplicationService giống như bình thường!
    

Mã nguồn lưu trữ file đã được phân tách và bọc dữ liệu an toàn. Tiếp theo bạn có muốn tôi viết nốt:

  * Mã nguồn hoàn chỉnh cho lớp bọc `DummyUnitOfWork` tại `infrastructure/repositories/dummy_uow.py`?
  * Hoặc Mã nguồn chi tiết bóc tách HTML mẫu cho bộ `TruyenFullParser` để dự án có thể chạy kiểm thử thực tế ngay lập tức không?