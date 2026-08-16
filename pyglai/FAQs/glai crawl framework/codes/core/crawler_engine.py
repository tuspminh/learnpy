"""
Bộ điều phối kết nối Data Tier và Scrape
"""

from database.db_manager import DBManager


class CrawlerEngine:
    def __init__(self, scraper, source_name):
        self.scraper = scraper
        self.source_name = source_name
        self.db = DBManager()

    def execute(self, story_url):
        print(f"[*] Đang bắt đầu cào từ nguồn: {self.source_name}")

        # 1. Tải và bóc tách thông tin truyện chính
        story_html = self.scraper.fetch_html(story_url)
        if not story_html:
            return

        story_info = self.scraper.extract_story_info(story_html)

        # 2. Lưu thông tin truyện vào DB qua Data Tier
        story_id = self.db.save_story(
            title=story_info["title"],
            url=story_url,
            author=story_info["author"],
            source=self.source_name,
        )
        print(f"[+] Đã lưu/Xác nhận truyện: {story_info['title']} (ID: {story_id})")

        # 3. Lấy danh sách chương
        chapters = self.scraper.extract_chapters_list(story_html)
        print(f"[+] Tìm thấy {len(chapters)} chương.")

        # 4. Vòng lặp cào từng chương truyện
        for idx, ch in enumerate(chapters, start=1):
            print(f" -> Đang cào chương {idx}: {ch['title']}")
            ch_html = self.scraper.fetch_html(ch["url"])
            if not ch_html:
                continue

            content = self.scraper.extract_chapter_content(ch_html)

            # Lưu chương vào DB bằng SQL thuần
            self.db.save_chapter(
                story_id=story_id,
                chapter_number=idx,
                title=ch["title"],
                content=content,
            )
        print("[*] Hoàn thành tiến trình cào dữ liệu!")
