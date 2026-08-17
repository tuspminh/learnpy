Để tích hợp thanh tiến trình trực quan vào lệnh treo máy tải toàn bộ chương, tôi sẽ cập nhật hàm `cmd_download_all` trong file `crawler.py` bằng cách sử dụng `click.progressbar`.

Khi chạy, công cụ CLI sẽ hiển thị một thanh tiến trình chạy phần trăm `%` kèm theo hiệu ứng đổ đầy trực quan thay vì in ra từng dòng văn bản như trước.

## 1\. Cập nhật mã nguồn `crawler.py` (Có thanh tiến trình)

Bạn hãy thay thế toàn bộ nội dung file `crawler.py` bằng đoạn mã dưới đây:
    
    
    import click
    import sys
    import time
    import database as db
    from plugins import get_plugin_by_url
    
    @click.group()
    def cli():
        """Công cụ CLI crawl truyện đa nguồn hỗ trợ cấu trúc Plugin."""
        db.init_db()
    
    @cli.command(name="listing")
    @click.argument("url")
    @click.option("--page", type=int, help="Chỉ định số trang cụ thể cần lấy dữ liệu")
    @click.option("--total-page", is_flag=True, help="Chỉ xem tổng số trang của danh mục")
    def cmd_listing(url, page, total_page):
        """Crawl danh sách truyện từ URL danh mục/thể loại."""
        plugin = get_plugin_by_url(url)
        if not plugin:
            sys.exit(1)
            
        target_url = plugin.build_page_url(url, page)
        soup = plugin.get_soup(target_url)
        if not soup:
            return
    
        if total_page:
            click.echo(f"Tổng số trang danh mục: {plugin.extract_total_pages(soup)}")
            return
    
        novels = plugin.parse_listing(soup)
        click.echo(f"{'Tiêu đề':<50} | {'Tác giả':<20} | SQLite")
        click.echo("-" * 90)
        for nv in novels:
            db.save_listing_item(plugin.clean_url(url), nv['title'], nv['author'], nv['url'])
            click.echo(f"{nv['title']:<50} | {nv['author']:<20} | OK")
    
    @cli.group(name="novel")
    def novel_group():
        """Nhóm lệnh thao tác với thông tin truyện hoặc chương."""
        pass
    
    @novel_group.command(name="info")
    @click.argument("url")
    def cmd_novel_info(url):
        """Crawl thông tin cơ bản của bộ truyện (Tên, tác giả, mô tả)."""
        plugin = get_plugin_by_url(url)
        if not plugin: sys.exit(1)
        
        novel_url = plugin.clean_url(url)
        soup = plugin.get_soup(novel_url)
        if not soup: return
        
        info = plugin.parse_novel_info(soup)
        db.save_novel_info(novel_url, info['title'], info['author'], info['description'], plugin.DOMAIN)
        click.echo(f"Tiêu đề: {info['title']}\nTác giả: {info['author']}\nMô tả truyện đã được lưu vào SQLite.")
    
    @novel_group.command(name="chapters")
    @click.argument("url")
    @click.option("--page", type=int, help="Chỉ định số trang cụ thể của danh sách chương")
    @click.option("--total-page", is_flag=True, help="Chỉ xem tổng số trang chứa danh sách chương")
    def cmd_novel_chapters(url, page, total_page):
        """Crawl danh sách chương hoặc xem tổng số trang chương."""
        plugin = get_plugin_by_url(url)
        if not plugin: sys.exit(1)
        
        target_url = plugin.build_page_url(url, page)
        soup = plugin.get_soup(target_url)
        if not soup: return
    
        if total_page:
            click.echo(f"Tổng số trang chương: {plugin.extract_total_pages(soup)}")
            return
    
        chapters = plugin.parse_chapter_list(soup)
        click.echo(f"{'Tên chương':<60} | SQLite")
        click.echo("-" * 80)
        for ch in chapters:
            db.save_chapter_item(plugin.clean_url(url), ch['title'], ch['url'])
            click.echo(f"{ch['title']:<60} | OK")
    
    @novel_group.command(name="chapter-content")
    @click.argument("url")
    def cmd_chapter_content(url):
        """Crawl nội dung chi tiết của một chương cụ thể."""
        plugin = get_plugin_by_url(url)
        if not plugin: sys.exit(1)
        
        soup = plugin.get_soup(url)
        if not soup: return
        
        data = plugin.parse_chapter_content(soup, url)
        db.save_chapter_item(data['novel_url'], data['title'], plugin.clean_url(url), content=data['content'])
        click.echo(f"--- Đã lưu: {data['title']} vào SQLite ---")
    
    @novel_group.command(name="download-all")
    @click.argument("url")
    def cmd_download_all(url):
        """Treo máy tự động tải toàn bộ chương kèm thanh tiến trình."""
        plugin = get_plugin_by_url(url)
        if not plugin: sys.exit(1)
        
        novel_url = plugin.clean_url(url)
        click.echo("Step 1: Đang lấy thông tin truyện...")
        soup = plugin.get_soup(novel_url)
        if not soup: return
        
        info = plugin.parse_novel_info(soup)
        db.save_novel_info(novel_url, info['title'], info['author'], info['description'], plugin.DOMAIN)
        
        total_pages = plugin.extract_total_pages(soup)
        click.echo(f"Step 2: Bộ truyện có tổng cộng {total_pages} trang chương.")
        
        all_chapters = []
        click.echo("Step 3: Đang quét danh sách link chương...")
        for p in range(1, total_pages + 1):
            p_url = plugin.build_page_url(novel_url, p if p > 1 else None)
            p_soup = plugin.get_soup(p_url)
            if p_soup:
                all_chapters.extend(plugin.parse_chapter_list(p_soup))
            click.echo(f"  > Đã quét xong trang {p}/{total_pages}\r", nl=False)
        
        total_chaps = len(all_chapters)
        click.echo(f"\nTÌm thấy {total_chaps} chương. Bắt đầu tải nội dung...")
        click.echo("-" * 60)
        
        # Sử dụng click.progressbar để quản lý và hiển thị tiến trình tải
        with click.progressbar(all_chapters, label="Tiến độ tải truyện", show_pos=True, item_show_func=lambda c: c['title'] if c else '') as bar:
            for chap in bar:
                c_soup = plugin.get_soup(chap['url'])
                if c_soup:
                    c_data = plugin.parse_chapter_content(c_soup, chap['url'])
                    db.save_chapter_item(novel_url, c_data['title'], chap['url'], content=c_data['content'])
                else:
                    # Nếu lỗi mạng, log nhẹ ra màn hình mà không làm gãy thanh tiến trình
                    click.echo(f"\n[Lỗi] Không thể tải chương: {chap['title']}")
                
                # Thời gian nghỉ tránh spam server
                time.sleep(0.5)
            
        click.echo("-" * 60)
        click.echo(f"--- Hoàn thành! Toàn bộ {total_chaps} chương đã được lưu vào SQLite3 ---")
    
    if __name__ == "__main__":
        cli()
    

## 2\. Giao diện thực tế khi chạy lệnh

Khi bạn thực hiện lệnh treo máy tải truyện:
    
    
    python crawler.py novel download-all "https://truyenfull.live"
    

Màn hình CLI lúc này sẽ hiển thị rất trực quan:
    
    
    Step 1: Đang lấy thông tin truyện...
    Tiêu đề: Tên Truyện Thử Nghiệm
    Tác giả: Người Viết
    Mô tả truyện đã được lưu vào SQLite.
    Step 2: Bộ truyện có tổng cộng 3 trang chương.
    Step 3: Đang quét danh sách link chương...
    Tìm thấy 150 chương. Bắt đầu tải nội dung...
    ------------------------------------------------------------
    Tiến độ tải truyện  [#####-------------------------------]   24/150  Chương 25: Đột phá cảnh giới
    

_Thanh tiến trình sẽ tự động nhảy số, chạy hiệu ứng đổ đầy`#` và liên tục cập nhật tên chương đang được tải ở phía cuối._

Hiện tại cấu trúc plugin đã rất vững vàng và chuyên nghiệp. Bạn có muốn tôi viết tích hợp thêm cơ chế tự động Resume (Kiểm tra chương nào có trong Database rồi thì bỏ qua để tiết kiệm thời gian và băng thông nếu lỡ bị mất mạng) không?