Để chuyển đổi toàn bộ giao diện dòng lệnh sang thư viện `click`, chúng ta sẽ giữ nguyên kiến trúc plugin và database đã thiết lập, chỉ thay đổi phần xử lý CLI trong file `crawler.py`.

Thư viện `click` giúp phân tách các nhóm tính năng (như `listing`, `novel`, `chapter`) thành các lệnh con (`subcommands`) rõ ràng hơn, giúp câu lệnh của bạn tường minh và dễ mở rộng hơn rất nhiều.

Trước khi bắt đầu, hãy cài đặt thư viện `click`:
    
    
    pip install click
    

Dưới đây là mã nguồn file `crawler.py` được viết lại hoàn toàn bằng `click`.

## Mã nguồn `crawler.py` mới (Dùng thư viện `click`)
    
    
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
        """Treo máy tự động tải toàn bộ chương của một bộ truyện từ đầu đến cuối."""
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
        click.echo(f"\nTìm thấy {total_chaps} chương. Bắt đầu treo máy tải nội dung...")
        click.echo("-" * 60)
        
        for index, chap in enumerate(all_chapters, 1):
            click.echo(f"[{index}/{total_chaps}] Đang tải: {chap['title']} ... ", nl=False)
            c_soup = plugin.get_soup(chap['url'])
            if c_soup:
                c_data = plugin.parse_chapter_content(c_soup, chap['url'])
                db.save_chapter_item(novel_url, c_data['title'], chap['url'], content=c_data['content'])
                click.echo("Xong!")
            else:
                click.echo("Thất bại!")
            time.sleep(0.5)
            
        click.echo("-" * 60)
        click.echo("--- Hoàn thành tải toàn bộ truyện về SQLite3! ---")
    
    if __name__ == "__main__":
        cli()
    

* * *

## Hướng dẫn sử dụng các cú pháp câu lệnh mới với `click`

Khi chuyển qua `click`, cấu trúc lệnh sẽ đổi sang dạng `python crawler.py [lệnh_con] [url] [tùy_chọn]`. Bạn có thể gõ `python crawler.py --help` để xem menu hướng dẫn rất đẹp mắt.

## 1\. Nhóm lệnh cào Danh mục (`listing`)

  * Lấy danh sách truyện từ trang đầu tiên:
        
        python crawler.py listing "https://truyenfull.live"
        

  * Lấy tổng số trang của danh mục:
        
        python crawler.py listing "https://truyenfull.live" --total-page
        

  * Lấy danh sách truyện tại một trang cụ thể:
        
        python crawler.py listing "https://truyenfull.live" --page 3
        




## 2\. Nhóm lệnh cào Truyện và Chương (`novel`)

  * Lấy thông tin chi tiết một bộ truyện:
        
        python crawler.py novel info "https://truyenfull.live"
        

  * Xem tổng số trang chứa danh sách chương của bộ truyện:
        
        python crawler.py novel chapters "https://truyenfull.live" --total-page
        

  * Lấy danh sách chương của truyện ở một trang cụ thể:
        
        python crawler.py novel chapters "https://truyenfull.live" --page 2
        

  * Lấy nội dung chi tiết của một chương cụ thể:
        
        python crawler.py novel chapter-content "https://truyenfull.live"
        

  * Treo máy cào TOÀN BỘ chương từ chương 1 đến chương cuối:
        
        python crawler.py novel download-all "https://truyenfull.live"
        




Bạn có muốn tích hợp thêm thanh tiến trình trực quan `click.progressbar` cho lệnh tải toàn bộ chương (`download-all`) để giao diện lúc treo máy trông chuyên nghiệp hơn không?