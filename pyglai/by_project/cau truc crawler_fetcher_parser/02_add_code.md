Dưới đây là mã nguồn chi tiết cấu trúc Parser cho ứng dụng crawl truyện chữ bằng Python theo chuẩn Domain-Driven Design (DDD).

## 1\. Tầng Domain (Nghiệp vụ cốt lõi)

_Không chứa bất kỳ mã nguồn nào liên quan đến thư viện cào dữ liệu (BeautifulSoup, Requests) hay cấu trúc HTML._

## `domain/entities.py`
    
    
    from typing import List, Optional
    
    class Chapter:
        """Domain Entity đại diện cho một chương truyện"""
        def __init__(self, number: float, title: str, content: Optional[str] = None):
            self.number = number
            self.title = title.strip()
            self.content = content.strip() if content else None
    
        def update_content(self, content: str):
            self.content = content.strip()
    
    
    class Novel:
        """Domain Entity đại diện cho một bộ truyện"""
        def __init__(self, title: str, author: str, description: str, source_url: str):
            self.title = title.strip()
            self.author = author.strip()
            self.description = description.strip()
            self.source_url = source_url
            self.chapters: List[Chapter] = []
    
        def add_chapter(self, chapter: Chapter):
            # Logic nghiệp vụ: Tránh trùng lặp số chương
            if any(c.number == chapter.number for c in self.chapters):
                return
            self.chapters.append(chapter)
    

* * *

## 2\. Tầng Infrastructure (Thực thi kỹ thuật)

_Nơi chứa Interface chuẩn và các triển khai cụ thể sử dụng thư viện bên ngoài (`BeautifulSoup`)._

## `infrastructure/parsers/base_parser.py`
    
    
    from abc import ABC, abstractmethod
    from domain.entities import Novel, Chapter
    
    class BaseParser(ABC):
        """Abstract Base Class định nghĩa giao tiếp chuẩn cho mọi Parser nguồn truyện"""
        
        @abstractmethod
        def parse_novel_info(self, html_content: str, source_url: str) -> Novel:
            """Phân tích HTML trang tổng quan để lấy thông tin truyện & danh sách chương"""
            pass
    
        @abstractmethod
        def parse_chapter_content(self, html_content: str, number: float, title: str) -> Chapter:
            """Phân tích HTML trang đọc truyện để lấy nội dung văn bản của chương"""
            pass
    

## `infrastructure/parsers/truyenfull_parser.py`
    
    
    from bs4 import BeautifulSoup
    from domain.entities import Novel, Chapter
    from infrastructure.parsers.base_parser import BaseParser
    
    class TruyenFullParser(BaseParser):
        """Parser cụ thể dành cho trang truyenfull.io (Ví dụ minh họa)"""
    
        def parse_novel_info(self, html_content: str, source_url: str) -> Novel:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Bóc tách thông tin dựa trên cấu trúc DOM của site
            title = soup.find('h3', class_='title').get_text()
            author = soup.find('a', itemprop='author').get_text()
            desc = soup.find('div', class_='desc-text').get_text()
            
            novel = Novel(title=title, author=author, description=desc, source_url=source_url)
            
            # Bóc tách danh sách chương sơ bộ (chỉ lấy số chương và tiêu đề)
            chapter_elements = soup.find_all('ul', class_='list-chapter')
            for ul in chapter_elements:
                for li in ul.find_all('a'):
                    chapter_title = li.get_text()
                    # Giả định trích xuất số chương từ text hoặc href (ví dụ: Chương 1 -> 1.0)
                    chapter_number = float(chapter_title.split(':')[0].replace('Chương ', '')) 
                    
                    novel.add_chapter(Chapter(number=chapter_number, title=chapter_title))
                    
            return novel
    
        def parse_chapter_content(self, html_content: str, number: float, title: str) -> Chapter:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Lấy phần thẻ chứa nội dung chính của truyện chữ
            content_div = soup.find('div', class_='chapter-c')
            
            # Làm sạch dữ liệu: loại bỏ quảng cáo chèn trong văn bản (nếu có)
            for ads in content_div.find_all(['div', 'ins', 'script']):
                ads.decompose()
                
            # Chuyển đổi các thẻ <br> thành xuống dòng để giữ định dạng văn bản gốc
            content = content_div.get_text(separator="\n")
            
            return Chapter(number=number, title=title, content=content)
    

## `infrastructure/parsers/parser_factory.py`
    
    
    from urllib.parse import urlparse
    from infrastructure.parsers.base_parser import BaseParser
    from infrastructure.parsers.truyenfull_parser import TruyenFullParser
    
    class ParserFactory:
        """Factory chịu trách nhiệm chọn đúng Parser dựa vào Domain của URL nguồn"""
        
        @staticmethod
        def get_parser(url: str) -> BaseParser:
            domain = urlparse(url).netloc.lower()
            
            if 'truyenfull' in domain:
                return TruyenFullParser()
            # Thêm các nguồn khác tại đây:
            # elif 'tangthuvien' in domain:
            #     return TangThuVienParser()
                
            raise ValueError(f"Hệ thống chưa hỗ trợ cào dữ liệu từ nguồn: {domain}")
    

* * *

## 3\. Tầng Application (Điều phối & Thực thi Luồng)

_Đóng vai trò làm Use Case liên kết Client, Network Request và Parser lại với nhau._

## `application/crawl_use_case.py`
    
    
    import requests
    from infrastructure.parsers.parser_factory import ParserFactory
    from domain.entities import Novel
    
    class CrawlNovelUseCase:
        """Use Case quản lý luồng cào thông tin một bộ truyện"""
        
        def execute(self, url: str) -> Novel:
            # 1. Nhận parser tương ứng thông qua Factory
            parser = ParserFactory.get_parser(url)
            
            # 2. Thực hiện HTTP request lấy HTML (Có thể chuyển sang một HttpService riêng)
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # 3. Thực thi parse dữ liệu thô thành Domain Object chuẩn hóa
            novel = parser.parse_novel_info(response.text, source_url=url)
            
            return novel
    

Nếu bạn muốn hoàn thiện hơn hệ thống này, hãy cho tôi biết:

  * Bạn có cần xây dựng thêm phần chống anti-crawl (Cloudflare bypass, Rotating Proxy)?
  * Bạn muốn lưu trữ dữ liệu đầu ra vào Database (SQL/NoSQL) hay xuất ra file EPUB/TXT?