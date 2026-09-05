Dưới đây là mã nguồn chi tiết cho tệp `infrastructure/repositories/dummy_uow.py` trong cấu trúc dự án phẳng.

Lớp này đóng vai trò là một No-Op (Dummy) Unit of Work phục vụ cho các hình thức lưu trữ không có cơ chế quản lý Transaction phức tạp ở cấp độ ứng dụng (như Hệ thống tệp tin cục bộ `FileLocalRepository` hoặc MongoDB nơi tính chất Atomic đã được xử lý ở tầng Document).

Việc tạo ra lớp bọc này giúp hệ thống tuân thủ tuyệt đối nguyên lý Liskov Substitution (L trong SOLID) và bảo vệ lớp Điều phối (`Application Layer`) khỏi bị sửa đổi code khi hoán đổi giữa các hệ quản trị cơ sở dữ liệu khác nhau.

* * *

## 💻 Triển Khai Mã Nguồn `infrastructure/repositories/dummy_uow.py`
    
    
    # infrastructure/repositories/dummy_uow.py
    import logging
    from application.interfaces import UnitOfWorkInterface, NovelRepositoryInterface
    
    logger = logging.getLogger(__name__)
    
    class DummyUnitOfWork(UnitOfWorkInterface):
        """
        Triển khai Unit of Work giả lập (No-Op / Dummy) dành cho các kho lưu trữ 
        không cần hoặc không hỗ trợ cơ chế Transaction nhiều bảng (như File System hoặc MongoDB).
        
        Giúp duy trì sự đồng nhất về Interface cho lớp Application Layer (SOLID - L).
        """
        def __init__(self, repository: NovelRepositoryInterface):
            self._repository = repository
    
        def __enter__(self) -> 'DummyUnitOfWork':
            logger.debug("🔓 [UoW] Khởi tạo phiên làm việc Dummy Context (Không dùng SQL Transaction).")
            return self
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            """
            Nếu có lỗi xảy ra, vì là Dummy nên ta không thực hiện rollback dữ liệu thô.
            Tuy nhiên hệ thống vẫn log lại để đảm bảo tính minh bạch luồng chạy.
            """
            if exc_type:
                logger.warning(f"⚠️ [UoW] Phát hiện sự cố trong Dummy Context. Chi tiết lỗi: {exc_val}")
                self.rollback()
            else:
                self.commit()
    
        def commit(self) -> None:
            """Hành vi giả lập Commit - Dữ liệu thực tế đã được lưu trực tiếp tại Repository."""
            logger.debug("💾 [UoW] Dummy Context hoàn tất quy trình lưu trữ thành công.")
    
        def rollback(self) -> None:
            """Hành vi giả lập Rollback - Đối với File/Mongo, dữ liệu lỗi cần được xử lý ở cấp độ cao hơn."""
            logger.debug("🔄 [UoW] Dummy Context ghi nhận yêu cầu Rollback (Bỏ qua hành vi thực tế trên đĩa/tài liệu).")
    
        @property
        def novels(self) -> NovelRepositoryInterface:
            """Trả về thực thể Repository được cấu hình (File/Mongo) để Use Case tương tác"""
            return self._repository
    

* * *

## 🎨 Tác dụng chiến lược của DummyUnitOfWork:

  1. Giữ nguyên hợp đồng kiến trúc (Architectural Contract): Lớp `NovelCrawlerApplicationService` ở tầng ứng dụng luôn đòi hỏi một lớp có kiểu dữ liệu là `UnitOfWorkInterface` để quản lý tài nguyên qua khối lệnh `with self._uow as uow:`. Nhờ có `DummyUnitOfWork`, tầng ứng dụng hoàn toàn không cần viết lại mã nguồn, dù bạn chuyển đổi từ lưu trữ SQL sang lưu file.
  2. Tách biệt nỗi lo hạ tầng: File hạ tầng ghi đĩa hay đẩy sang cơ sở dữ liệu NoSQL tự lo liệu việc chống trùng lặp hay ghi đè lỗi. Lớp bọc này chỉ làm nhiệm vụ "trung chuyển" luồng chạy một cách mượt mà nhất.



Hiện tại toàn bộ kiến trúc khung xương của Crawler theo Clean Architecture, DDD và SOLID đã hoàn tất 100%. Bước tiếp theo để chạy thử nghiệm, bạn có muốn tôi viết chi tiết file `infrastructure/parsers/truyenfull.py` (Bóc tách HTML bằng BeautifulSoup4 và xử lý Phân trang) để app có thể cào truyện thực tế ngay lập tức không?