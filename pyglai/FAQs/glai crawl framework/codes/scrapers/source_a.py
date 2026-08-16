from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper


class SourceAScraper(BaseScraper):
    """Lớp cào cụ thể cho Nguồn A (Ví dụ: Bản mẫu dùng BeautifulSoup)"""

    def extract_story_info(self, html):
        soup = BeautifulSoup(html, "html.parser")
        # Thay thế class/id tùy theo cấu trúc HTML thực tế của Nguồn A
        title = soup.find("h3", class_="title").text.strip()
        author = (
            soup.find("span", class_="author").text.strip()
            if soup.find("span", class_="author")
            else "Unknown"
        )
        return {"title": title, "author": author}

    def extract_chapters_list(self, html):
        soup = BeautifulSoup(html, "html.parser")
        chapters = []
        # Lấy tất cả thẻ chứa link chương
        for a in soup.select("ul.list-chapter a"):
            chapters.append({"title": a.text.strip(), "url": a["href"]})
        return chapters

    def extract_chapter_content(self, html):
        soup = BeautifulSoup(html, "html.parser")
        # Lấy nội dung văn bản của chương truyện
        content_div = soup.find("div", class_="chapter-content")
        return content_div.text.strip() if content_div else ""
