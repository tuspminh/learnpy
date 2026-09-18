Trong thiết kế hướng tên miền (Domain-Driven Design - DDD), `ParserFactory` không đơn thuần là một mẫu thiết kế khởi tạo đối tượng (Creational Pattern) thông thường, mà nó đóng vai trò là một Domain Factory hoặc Infrastructure Factory.

Nhiệm vụ cốt lõi của nó trong bài toán này là che giấu logic khởi tạo phức tạp của các bộ Parser (luật bóc tách HTML của từng website nguồn) và cung cấp đúng công cụ xử lý cho Application Service.

Dưới đây là phân tích chuyên sâu và cách triển khai `ParserFactory` tối ưu cho bài toán cào bulk 2-3 nguồn của bạn, áp dụng các nguyên lý SOLID.

* * *

## 1\. Phân cấp Trách nhiệm trong DDD (Where does it live?)

Tùy thuộc vào cách bạn thiết kế các Parser, `ParserFactory` có thể nằm ở hai nơi:

  * Domain Layer: Nếu các Parser chỉ chứa logic thuần túy (In-memory logic, Regex, XPath, CSS Selector) không phụ thuộc vào hạ tầng bên ngoài (DB, Network).
  * Infrastructure Layer: Nếu các Parser cần nạp cấu hình động từ Database (ví dụ: các rule CSS selector được lưu trong DB thay vì viết cứng bằng code).



Với bài toán 2-3 nguồn không JS, luật bóc tách thường cố định bằng code nên `ParserFactory` sẽ nằm ở Domain Layer (hoặc Application Layer dưới dạng Service Locator).

* * *

## 2\. Thiết kế Code mẫu `ParserFactory` theo nguyên lý Open-Closed (OCP)

Nếu bạn thiết kế Factory bằng các câu lệnh `if-elif-else` hoặc `switch-case` thông thường, mỗi khi thêm nguồn thứ 4 hoặc thứ 5, bạn sẽ phải sửa đổi trực tiếp mã nguồn của Factory. Điều này vi phạm nguyên lý Open-Closed (Đóng với việc sửa đổi, Mở với việc mở rộng).

Để tối ưu, chúng ta sẽ sử dụng cơ chế Tự động Đăng ký (Self-Registration) hoặc Registry Pattern.
    
    
    from abc import ABC, abstractmethod
    from typing import Dict, Type
    from selectolax.parser import HTMLParser
    
    # ==========================================
    # 1. PARSER INTERFACE & DOMAIN MODEL
    # ==========================================
    class BaseParser(ABC):
        """Lớp trừu tượng cho tất cả các bộ phân tích cú pháp"""
        
        @property
        @abstractmethod
        def source_name(self) -> str:
            """Định danh của nguồn (Vd: 'truyenfull', 'tangthuvien')"""
            pass
    
        @abstractmethod
        def parse_title(self, tree: HTMLParser) -> str:
            pass
    
        @abstractmethod
        def parse_content(self, tree: HTMLParser) -> str:
            pass
    
        def parse(self, html: str) -> dict:
            """Template Method định nghĩa luồng parse chung"""
            tree = HTMLParser(html)
            return {
                "title": self.parse_title(tree),
                "content": self.parse_content(tree)
            }
    
    # ==========================================
    # 2. CONCRETE PARSERS (Triển khai thực tế cho 3 nguồn)
    # ==========================================
    class TruyenFullParser(BaseParser):
        source_name = "truyenfull"
    
        def parse_title(self, tree: HTMLParser) -> str:
            node = tree.css_first(".chapter-title")
            return node.text(strip=True) if node else "Không rõ tiêu đề"
    
        def parse_content(self, tree: HTMLParser) -> str:
            node = tree.css_first(".chapter-c")
            if not node: return ""
            return "\n".join([p.text(strip=True) for p in node.css("p") if p.text(strip=True)])
    
    
    class TangThuVienParser(BaseParser):
        source_name = "tangthuvien"
    
        def parse_title(self, tree: HTMLParser) -> str:
            node = tree.css_first("h2.story-title")
            return node.text(strip=True) if node else "Không rõ tiêu đề"
    
        def parse_content(self, tree: HTMLParser) -> str:
            node = tree.css_first(".box-chap")
            return node.text(strip=True) if node else ""
    
    # ==========================================
    # 3. ADVANCED PARSER FACTORY (Registry Pattern)
    # ==========================================
    class ParserFactory:
        """Factory quản lý và cung cấp Parser động mà không cần dùng if-else"""
        
        # Từ điển lưu trữ các class Parser đã đăng ký
        _parsers_registry: Dict[str, Type[BaseParser]] = {}
    
        @classmethod
        def register_parser(cls, parser_class: Type[BaseParser]):
            """Đăng ký một Parser mới vào hệ thống"""
            if not parser_class.source_name:
                raise ValueError(f"Parser {parser_class.__name__} phải định nghĩa 'source_name'")
            cls._parsers_registry[parser_class.source_name] = parser_class
            return parser_class  # Trả về class để có thể dùng làm decorator
    
        @classmethod
        def get_parser(cls, source_type: str) -> BaseParser:
            """Lấy instance của Parser tương ứng dựa trên nguồn"""
            parser_class = cls._parsers_registry.get(source_type.lower())
            if not parser_class:
                raise ValueError(f"Hệ thống chưa hỗ trợ nguồn truyện: '{source_type}'")
            
            # Khởi tạo Object ( Singleton hoặc New Instance tùy cấu hình )
            return parser_class()
    
    # ==========================================
    # 4. ĐĂNG KÝ CÁC PARSER VÀO FACTORY
    # ==========================================
    # Bạn có thể đăng ký thủ công hoặc dùng Decorator cực kỳ clean như sau:
    ParserFactory.register_parser(TruyenFullParser)
    ParserFactory.register_parser(TangThuVienParser)
    

* * *

## 3\. Cách sử dụng mượt mà trong Application Service

Khi chạy Bulk Crawl Pipeline, Application Service chỉ cần gọi Factory thông qua định danh của nguồn truyện (lấy từ cấu hình hoặc URL).
    
    
    class BulkScraperPipeline:
        def __init__(self, fetcher):
            self.fetcher = fetcher
    
        async def execute(self, url: str, source_type: str):
            # 1. Gọi Factory để lấy đúng vũ khí chiến đấu
            # Hoàn toàn không có logic kiểm tra if source == 'truyenfull' ở đây
            try:
                parser = ParserFactory.get_parser(source_type) [1]
            except ValueError as e:
                print(f"Bỏ qua URL do lỗi cấu hình: {e}")
                return
    
            # 2. Tải HTML thô thông qua Fetcher
            html_content = await self.fetcher.fetch(url)
            
            if html_content:
                # 3. Tiến hành phân tách dữ liệu sạch
                clean_data = parser.parse(html_content)
                print(f"Đã bóc tách thành công truyện từ [{source_type}]: {clean_data['title']}")
                return clean_data
    

## 💎 Ưu điểm vượt trội của thiết kế này:

  1. Cô lập lỗi (Isolation): Nếu website `TruyenFull` thay đổi giao diện, bạn chỉ mở file chứa `TruyenFullParser` ra sửa lại CSS Selector. Mã nguồn của `ParserFactory`, `Fetcher` hay `Pipeline` hoàn toàn không bị động chạm, hạn chế tối đa việc sinh ra lỗi dây chuyền (Regression bugs).
  2. Dễ dàng cào thêm nguồn mới: Sang tuần nếu bạn muốn cào thêm nguồn thứ 4 (ví dụ: `truyenchu`), bạn chỉ cần viết một Class `TruyenChuParser` kế thừa `BaseParser`, sau đó gọi `ParserFactory.register_parser(TruyenChuParser)`. Hệ thống tự động nhận diện nguồn mới mà không cần sửa code cũ.



Để tối ưu hóa sâu hơn cho tầng Parser, bạn có muốn chúng ta xử lý tiếp bài toán:

  * Cách viết Regex để tự động nhận diện Số chương (Chapter Number) từ Tiêu đề chương (vì tiêu đề mỗi nguồn viết một kiểu: "Chương 1:", "Quyển 1 - Chương 12", "Chương 23.1"...) không?
  * Hay bạn muốn thiết kế giải pháp tự động loại bỏ Text rác / Text quảng cáo chèn ẩn bên trong nội dung truyện chữ?