"""
 Presentation Tier (Tầng Điều Khiển / Giao Diện)

Giao diện dòng lệnh CLI đơn giản cho phép người dùng tương tác, chọn nguồn muốn cào và nhập link.
"""

from core.crawler_engine import CrawlerEngine
from scrapers.source_a import SourceAScraper


def main():
    print("=== HỆ THỐNG CÀO TRUYỆN ĐA NGUỒN 3-TIER ===")
    print("1. Cào từ Nguồn A (TruyenFull...)")
    print("2. Cào từ Nguồn B (Hiện chưa cấu hình...)")

    choice = input("Chọn nguồn cào (1-2): ")

    if choice == "1":
        scraper = SourceAScraper()
        source_name = "Nguon_A"
    else:
        print("Lựa chọn không hợp lệ hoặc chưa cấu hình nguồn này!")
        return

    story_url = input("Nhập URL của truyện cần cào: ").strip()

    if not story_url:
        print("URL không được để trống!")
        return

    # Kích hoạt Logic Tier xử lý tác vụ
    engine = CrawlerEngine(scraper, source_name)
    engine.execute(story_url)


if __name__ == "__main__":
    main()
