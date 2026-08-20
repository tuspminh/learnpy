Trong kiến trúc Clean Architecture, Domain-Driven Design (DDD) là triết lý thiết kế đặt Domain (Nghiệp vụ cốt lõi) làm trung tâm của mọi quyết định. DDD không tập trung vào việc thiết kế bảng dữ liệu (Database-First) hay viết API (Framework-First), mà tập trung vào việc mô hình hóa chính xác thế giới thực của nghiệp vụ vào trong mã nguồn Python thuần (`Pure Python`).

Dưới đây là mổ xẻ chi tiết các khái niệm cốt lõi của DDD và cách chúng được áp dụng trực tiếp vào dự án Crawl sách/truyện của bạn.

* * *

## 1\. Ubiquitous Language (Ngôn ngữ đồng nhất)

> _Ngôn ngữ chung được sử dụng nhất quán bởi cả chuyên gia nghiệp vụ (Business Expert) và lập trình viên._

  * Áp dụng: Trong dự án của bạn, từ ngữ trong code phải khớp hoàn toàn với thực tế sử dụng. Không dùng những từ kỹ thuật chung chung như `Table1`, `DataProcessor`. Thay vào đó, bạn sử dụng chính xác các thuật ngữ nghiệp vụ: `Book`, `Chapter`, `SlideImage`, `CrawlService`, `Library`.



* * *

## 2\. Entities (Thực thể)

> _Là những đối tượng có định danh duy nhất (Identity - ID) không thay đổi theo thời gian, dù các thuộc tính khác của chúng có thể biến đổi._

  * Đặc điểm trong Python: Thường dùng `dataclasses` để biểu diễn. Hai Entity được coi là bằng nhau nếu chúng có cùng `id`, kể cả khi các trường khác khác nhau.
  * Áp dụng: Đối tượng `Chapter` (Chương truyện).

    * Nội dung chữ của chương có thể được sửa, tiêu đề chương có thể đổi, nhưng `chapter_id` là duy nhất và cố định vĩnh viễn.



    
    
    @dataclass
    class Chapter:
        chapter_id: str  # ID định danh duy nhất của Entity
        title: str
        content: str
        order_index: int
    
        def __eq__(self, other):
            if not isinstance(other, Chapter): return False
            return self.chapter_id == other.chapter_id
    

* * *

## 3\. Value Objects (Đối tượng giá trị)

> _Là những đối tượng không có định danh (ID). Chúng được định nghĩa hoàn toàn bởi giá trị của các thuộc tính mà chúng chứa._

  * Đặc điểm trong Python: Chúng mang tính bất biến (Immutable). Bạn không sửa thuộc tính của một Value Object; nếu muốn đổi, bạn phải tạo ra một đối tượng hoàn toàn mới. Hai Value Object bằng nhau nếu mọi thuộc tính của chúng giống hệt nhau.
  * Áp dụng: Đối tượng `SlideImage` trong bài toán SlideShare.

    * Một ảnh slide chỉ gồm `page_number` và `image_url`. Nó không cần ID riêng biệt. Nếu link ảnh đổi, ta thay bằng một `SlideImage` mới.



    
    
    @dataclass(frozen=True)  # frozen=True đảm bảo tính bất biến (Immutable)
    class SlideImage:
        page_number: int
        image_url: str
        local_path: str
    
        # Không cần viết __eq__, Python dataclass tự động so sánh bằng tất cả các trường
    

* * *

## 4\. Aggregates & Aggregate Roots (Cụm thực thể & Gốc cụm)

Đây là khái niệm quan trọng nhất trong DDD dùng để thiết lập ranh giới giao dịch và bảo vệ tính toàn vẹn dữ liệu.

  * Aggregate: Là một cụm gồm các _Entities_ và _Value Objects_ có mối quan hệ chặt chẽ với nhau.
  * Aggregate Root: Là Thực thể duy nhất đứng đầu cụm đó, đóng vai trò làm "Cửa ngõ duy nhất" để bên ngoài tương tác với các thành phần bên trong cụm. Bên ngoài tuyệt đối không được sửa trực tiếp lớp con bên trong mà phải ra lệnh thông qua Aggregate Root.
  * Áp dụng: `Book` (hoặc `Story`) là Aggregate Root. Lớp con bên trong là danh sách `Chapter` hoặc `SlideImage`.

    * Quy tắc nghiệp vụ: Khi thêm một chương mới, hệ thống phải tự động tính toán số thứ tự (`order_index`) tăng dần để không bao giờ có 2 chương trùng số thứ tự.
    * Code DDD chuẩn:



    
    
    @dataclass
    class Book:  # <-- AGGREGATE ROOT
        book_id: str
        title: str
        slideshare_url: str
        _slides: List[SlideImage] = field(default_factory=list)  # Đóng gói (Encapsulation)
    
        def add_slide(self, image_url: str) -> None:
            """
            Bên ngoài chỉ được phép gọi hàm này của Aggregate Root.
            Aggregate Root tự thực hiện và bảo vệ quy tắc nghiệp vụ (Invariants).
            """
            next_page = len(self._slides) + 1
            local_path = f"output/{self.book_id}/slide_{next_page:03d}.jpg"
            
            # Tạo Value Object và đưa vào danh sách nội bộ
            new_slide = SlideImage(next_page, image_url, local_path)
            self._slides.append(new_slide)
    
        @property
        def slides(self) -> List[SlideImage]:
            """Chỉ trả về bản sao hoặc danh sách chỉ đọc, chặn bên ngoài tự ý .append() từ xa"""
            return list(self._slides)
    

> _Mối liên kết với Unit of Work_ : Khi lưu dữ liệu, Repository sẽ nhận vào cả một `Book` (Aggregate Root) và UoW sẽ đảm bảo lưu toàn bộ cụm dữ liệu này xuống DB thành công, hoặc hủy bỏ toàn bộ. Bạn không bao giờ tạo ra một `ChapterRepository` hay `SlideRepository` riêng lẻ.

* * *

## 5\. Domain Services (Dịch vụ Domain)

> _Khi một hành động nghiệp vụ mang tính chất xử lý logic quy trình mà không thuộc về trách nhiệm của riêng bất kỳ một Entity hay Value Object nào, hành động đó được tách ra thành một Domain Service._

  * Áp dụng: Logic kiểm tra xem nội dung truyện cào về có chứa các từ khóa vi phạm chính sách cộng đồng hay không (`ContentModerationService`). Việc kiểm tra này độc lập và cần phối hợp nhiều quy tắc, nó xứng đáng là một Domain Service.


    
    
    class ContentModerationService:
        def __init__(self, banned_words: List[str]):
            self.banned_words = banned_words
    
        def is_clean(self, book: Book) -> bool:
            # Duyệt qua các slide/chương để kiểm tra từ cấm
            return True
    

* * *

## 6\. Bounded Context (Ngữ cảnh giới hạn)

> _Chia hệ thống lớn thành các phân vùng không gian độc lập, nơi mà một từ ngữ chỉ mang một ý nghĩa duy nhất._

Hãy nhìn vào cách một ứng dụng lớn phát triển:

  * Context Crawl & Đọc sách: Đối tượng `Book` cần có `title`, `author`, `chapters`, `slides` để hiển thị cho người đọc.
  * Context Kế toán / Mua bán sách: Đối tượng `Book` lúc này chỉ cần `book_id`, `price` (giá tiền), `tax_rate` (thuế) và `inventory_count` (số lượng kho). Nó hoàn toàn không quan tâm sách có bao nhiêu chương hay ảnh slide nằm ở đâu.



Sai lầm phổ biến: Tạo ra một class `Book` khổng lồ chứa 50 trường phục vụ cho tất cả mọi tính năng trong hệ thống.  
Giải pháp DDD: Tách thành 2 Bounded Context riêng biệt. Mỗi bên có một class `Book` độc lập phù hợp với nghiệp vụ của mình.

* * *

## 🎨 Tổng kết: Quy trình tư duy code theo DDD trong Python

  1. Viết Domain trước: Luôn tạo file `domain/models.py` đầu tiên khi làm tính năng mới. Viết code bằng Python thuần (`dataclasses`). Tuyệt đối không import `FastAPI`, `SQLAlchemy`, hay bất kỳ thư viện ngoài nào vào đây.
  2. Bảo vệ thuộc tính: Chuyển các thuộc tính danh sách thành private (`_chapters`) và cung cấp các hàm nghiệp vụ (`add_chapter()`) để chỉnh sửa, ngăn chặn việc lớp ngoài tự ý ghi đè dữ liệu bừa bãi.
  3. Tương tác qua Root: Giao tiếp với Database luôn luôn nhận và trả về một Aggregate Root.



Bạn đã thấy rõ cách các mảnh ghép của DDD tổ chức logic nghiệp vụ sạch sẽ như thế nào chưa? Nếu bạn muốn hoàn thiện, hãy cho tôi biết:

  * Bạn có muốn tìm hiểu về Domain Events (ví dụ: khi Aggregate Root `Book` thực hiện `.add_slide()` xong, nó tự phát ra một Event để các tầng khác bắt lấy và xử lý phụ trợ) không?
  * Hay bạn muốn tối ưu cấu trúc này lên quy mô lớn hơn với mô hình tách biệt đọc/ghi CQRS?