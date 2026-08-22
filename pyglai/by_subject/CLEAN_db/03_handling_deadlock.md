Khi ứng dụng crawl truyện hoạt động ở quy mô lớn với cơ chế đa luồng (Multithreading/Async/Multiprocessing), hiện tượng nhiều worker cùng ghi dữ liệu (insert chương mới, update thông tin truyện) vào database tại một thời điểm rất dễ gây ra lỗi Deadlock (khóa chết) hoặc Lock Wait Timeout (chờ khóa quá lâu).

Để hệ thống tự phục hồi mà không làm sập tiến trình cào, chúng ta cần tích hợp thêm cơ chế Exception Handling (Xử lý lỗi) và Retry Logic (Thử lại tự động) trực tiếp vào lớp `Infrastructure` thông qua cấu trúc Unit of Work (UoW) đã thiết kế.

Dưới đây là giải pháp nâng cấp toàn diện bằng Python.

* * *

## 1\. Kiến trúc xử lý lỗi và thử lại (Retry & Exception Strategy)

Chúng ta sẽ áp dụng các quy tắc SOLID bằng cách:

  * Tách biệt logic retry ra khỏi logic nghiệp vụ (Use Case không cần biết DB bị lỗi gì).
  * Định nghĩa mã lỗi đặc trưng của hệ quản trị cơ sở dữ liệu (ví dụ với MySQL, lỗi `1213` là Deadlock, `1205` là Lock Wait Timeout).
  * Sử dụng Exponential Backoff (thời gian chờ tăng dần giữa các lần thử lại) để giảm tải cho database khi hệ thống đang bị nghẽn.



* * *

## 2\. Triển khai code nâng cấp Unit of Work với cơ chế Tự động Thử lại

Chúng ta sẽ bọc (wrap) khối lệnh thực thi của Unit of Work bằng một hàm Decorator hoặc tích hợp trực tiếp vào hàm `__exit__`. Phương pháp tối ưu nhất cho Clean Architecture là viết một hàm Execute với Retry nằm trong UoW.
    
    
    # src/infrastructure/database/unit_of_work.py
    import time
    import random
    from mysql.connector import errors
    from src.domain.repositories import IUnitOfWork
    from src.infrastructure.database.mysql_repositories import MySqlStoryRepository, MySqlChapterRepository
    
    class MySqlUnitOfWork(IUnitOfWork):
        def __init__(self, db_client, max_retries: int = 3, backoff_factor: float = 0.5):
            self.db_client = db_client
            self.max_retries = max_retries
            self.backoff_factor = backoff_factor # Hệ số tăng thời gian chờ
            self.connection = None
            self.cursor = None
    
        def __enter__(self):
            self.connection = self.db_client.get_connection()
            self.connection.start_transaction()
            self.cursor = self.connection.cursor(dictionary=True)
            
            # Inject cursor vào các repo
            self.story_repo = MySqlStoryRepository(self.cursor)
            self.chapter_repo = MySqlChapterRepository(self.cursor)
            return self
    
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                self.rollback()
            else:
                self.commit()
                
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
    
        def commit(self):
            if self.connection:
                self.connection.commit()
    
        def rollback(self):
            if self.connection:
                self.connection.rollback()
    
        def execute_with_retry(self, operation_callable, *args, **kwargs):
            """
            Hàm bao bọc (Wrapper) thực thi Use Case logic trong một Transaction.
            Nếu gặp lỗi Deadlock hoặc Lock Timeout, hệ thống sẽ tự động Rollback và chạy lại.
            """
            retries = 0
            while retries <= self.max_retries:
                try:
                    # Sử dụng chính Context Manager (khối with) của lớp này
                    with self:
                        # Chạy logic nghiệp vụ được truyền từ Use Case vào
                        return operation_callable(self, *args, **kwargs)
                        
                except errors.OperationalError as err:
                    # Mã lỗi MySQL: 1213 = Deadlock, 1205 = Lock Wait Timeout
                    if err.errno in (1213, 1205):
                        retries += 1
                        if retries > self.max_retries:
                            print(f"❌ Đã thử lại {self.max_retries} lần nhưng vẫn thất bại do lỗi DB Lock. Hủy bỏ task.")
                            raise err # Ném lỗi lên lớp trên nếu vượt quá số lần retry
                        
                        # Tính toán thời gian chờ tăng dần + một chút ngẫu nhiên (Jitter) để tránh các luồng đâm vào DB cùng lúc
                        sleep_time = (self.backoff_factor * (2 ** retries)) + random.uniform(0, 0.1)
                        print(f"⚠️ Phát hiện lỗi DB Lock ({err.msg}). Đang tự động Rollback và thử lại lần {retries}/{self.max_retries} sau {sleep_time:.2f}s...")
                        time.sleep(sleep_time)
                    else:
                        # Nếu là các lỗi cú pháp SQL hoặc mất kết nối vật lý -> Không retry, ném lỗi ngay
                        raise err
                except Exception as e:
                    # Các lỗi logic nghiệp vụ khác -> Không retry, ném lỗi ngay
                    raise e
    

* * *

## 3\. Cập nhật cách gọi từ Use Case và main.py

Nhờ thiết kế `execute_with_retry`, mã nguồn ở tầng nghiệp vụ (`Use Case`) giữ được sự ngắn gọn tuyệt đối và hoàn toàn không phải viết các câu lệnh `try...except` lỗi DB phức tạp.

## Cấu trúc Use Case (Tinh gọn):
    
    
    # src/use_cases/save_chapter_pipeline.py
    from src.domain.entities import Chapter
    
    class SaveChapterPipelineUseCase:
        # Use Case chỉ chứa logic nghiệp vụ thuần túy
        def run_business_logic(self, uow, raw_data: dict):
            """
            Hàm này chỉ chạy khi UoW đã mở transaction thành công.
            """
            # 1. Tìm truyện
            story = uow.story_repo.find_by_source_url(raw_data["source_url"])
            if not story:
                raise ValueError("Truyện không tồn tại để thêm chương.")
    
            # 2. Lưu chương mới
            new_chapter = Chapter(story_id=story.id, title=raw_data["chapter_title"], content=raw_data["content"])
            uow.chapter_repo.create(new_chapter)
            
            print(f"✅ Ghi thành công chương: {raw_data['chapter_title']}")
    

## Ráp nối tại main.py (Điều phối thực thi):
    
    
    # main.py
    from src.infrastructure.database.connection_manager import MySqlDbClient
    from src.infrastructure.database.unit_of_work import MySqlUnitOfWork
    from src.use_cases.save_chapter_pipeline import SaveChapterPipelineUseCase
    
    def main():
        db_client = MySqlDbClient()
        db_client.connect()
    
        try:
            # Khởi tạo UoW với cấu hình tối đa 3 lần retry nếu dính Deadlock
            uow = MySqlUnitOfWork(db_client=db_client, max_retries=3)
            use_case = SaveChapterPipelineUseCase()
    
            raw_crawled_chapter = {
                "source_url": "https://truyenfull.vn",
                "chapter_title": "Chương 100: Trận Chiến Cuối Cùng",
                "content": "Nội dung chương truyện rất dài..."
            }
    
            # Kích hoạt tiến trình lưu thông qua bộ lọc tự động thử lại của UoW
            uow.execute_with_retry(use_case.run_business_logic, raw_data=raw_crawled_chapter)
    
        finally:
            db_client.disconnect()
    
    if __name__ == "__main__":
        main()
    

* * *

## 🧠 Luồng hoạt động khi có xung đột (Deadlock Flow):

  1. Worker A và Worker B cùng lúc gửi lệnh cập nhật dữ liệu của cùng một bộ truyện.
  2. MySQL phát hiện xung đột và trả về mã lỗi `1213 (Deadlock)` cho Worker B.
  3. Hàm `execute_with_retry` ở Worker B ngay lập tức bắt được lỗi này.
  4. Block `with self:` kích hoạt hàm `__exit__` tự động gọi `connection.rollback()` để giải phóng các bản ghi đang bị khóa, tránh làm nghẽn toàn bộ hệ thống.
  5. Worker B tạm dừng khoảng `0.6s`, sau đó tự động xin một kết nối mới từ Pool và thực hiện lại từ đầu (`run_business_logic`). Lúc này Worker A đã ghi xong, Worker B sẽ ghi thành công mà không gặp lỗi nữa.



Hệ thống của bạn hiện tại đã sở hữu một Data Persistence Layer rất mạnh mẽ, có khả năng tự phục hồi lỗi luồng, độc lập công nghệ và bảo vệ toàn vẹn dữ liệu cực tốt.

Tiếp theo, để hoàn thiện ứng dụng crawl truyện, bạn có muốn tối ưu hóa tiếp phần Cơ chế lưu trữ nội dung Text chương truyện (Chapter Content) (vì văn bản chương truyện rất nặng, lưu trực tiếp vào RDBMS SQL mãi sẽ làm phình DB và chậm câu lệnh Join), ví dụ như giải pháp đẩy text lên AWS S3 / MinIO hoặc nén dữ liệu trước khi lưu không?