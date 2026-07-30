"""
 Logic Tier (Tầng Xử Lý)

Tầng này chịu trách nhiệm gửi request, phân tích HTML. Để cào được nhiều nguồn , ta dùng kỹ thuật OOP để định nghĩa một khung chuẩn (BaseScraper), sau đó mỗi nguồn sẽ tự viết hàm bóc tách riêng.
"""

from abc import ABC, abstractmethod
import requests


class BaseScraper(ABC):
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    def fetch_html(self, url):
        """Hàm tải HTML chung cho tất cả các nguồn"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"Lỗi khi tải URL {url}: {e}")
        return None

    @abstractmethod
    def extract_story_info(self, html):
        """Mỗi nguồn phải tự định nghĩa cách lấy Tên, Tác giả"""
        pass

    @abstractmethod
    def extract_chapters_list(self, html):
        """Mỗi nguồn phải tự định nghĩa cách lấy danh sách Link chương"""
        pass

    @abstractmethod
    def extract_chapter_content(self, html):
        """Mỗi nguồn phải tự định nghĩa cách lấy nội dung chữ/ảnh của chương"""
        pass
