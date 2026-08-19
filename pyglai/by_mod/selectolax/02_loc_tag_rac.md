Để lọc và xóa bỏ tất cả các thẻ rác (như quảng cáo, thanh điều hướng, script, style...) trong `selectolax` trước khi trích xuất nội dung, phương thức tốt nhất là sử dụng `.decompose()` kết hợp với vòng lặp, hoặc sử dụng phương thức nâng cao `.strip_tags()`.

Dưới đây là hướng dẫn chi tiết các cách thực hiện từ cơ bản đến nâng cao.

* * *

## Cách 1: Sử dụng `.decompose()` để xóa hoàn toàn thẻ rác (Khuyên dùng)

Cách này hoạt động bằng cách tìm tất cả các thẻ rác bằng bộ chọn CSS Selector, sau đó gọi lệnh `.decompose()` để bốc hơi hoàn toàn thẻ đó và nội dung bên trong nó ra khỏi cây HTML.
    
    
    from selectolax.lexbor import LexborHTMLParser
    
    html_doc = """
    <div id="post-content">
        <h1>Tiêu đề bài viết chính</h1>
        <script>alert("Mã độc hại hoặc quảng cáo");</script>
        <style>.ads { color: red; }</style>
        
        <p>Đây là nội dung hữu ích số 1.</p>
        
        <div class="banner-ads">
            <p>Quảng cáo: Mua ngay khóa học Python giá rẻ!</p>
        </div>
        
        <p>Đây là nội dung hữu ích số 2.</p>
        <div class="social-share">Thanh chia sẻ Facebook, Zalo (Rác)</div>
    </div>
    """
    
    tree = LexborHTMLParser(html_doc)
    
    # 1. Định nghĩa danh sách các bộ chọn CSS của thẻ rác cần xóa
    # Bạn có thể gom tên thẻ (script, style) và cả class/id (.banner-ads, .social-share) vào một chuỗi, cách nhau bằng dấu phẩy
    garbage_selectors = "script, style, .banner-ads, .social-share"
    
    # 2. Tìm và xóa sạch rác
    for garbage_node in tree.css(garbage_selectors):
        garbage_node.decompose()
    
    # 3. Lấy lại nội dung sau khi đã dọn rác
    clean_content = tree.css_first("#post-content")
    print(clean_content.text(strip=True, separator='\n'))
    

Kết quả in ra (Đã sạch rác hoàn toàn):
    
    
    Tiêu đề bài viết chính
    Đây là một đoạn văn hữu ích số 1.
    Đây là một đoạn văn hữu ích số 2.
    

* * *

## Cách 2: Sử dụng `.strip_tags()` để xóa thẻ nhưng GIỮ LẠI CHỮ

Có những trường hợp bạn không muốn xóa hoàn toàn nội dung, mà chỉ muốn bóc vỏ các thẻ định dạng dư thừa (ví dụ: thẻ `<span>`, `<b>`, `<i>`, `<font>` làm rối văn bản) nhưng vẫn giữ lại chữ bên trong chúng. `selectolax` cung cấp hàm `.strip_tags()` xử lý việc này cực nhanh.
    
    
    from selectolax.lexbor import LexborHTMLParser
    
    html_doc = "<p>Chào bạn <span class='highlight'>Nguyễn Văn A</span>, chúc bạn một ngày <b>tốt lành</b>.</p>"
    tree = LexborHTMLParser(html_doc)
    
    # Xóa bỏ thẻ span và b nhưng giữ lại chữ bên trong chúng
    tree.root.strip_tags(["span", "b"])
    
    print(tree.root.html)
    # Kết quả: <p>Chào bạn Nguyễn Văn A, chúc bạn một ngày tốt lành.</p>
    

* * *

## Kịch bản thực tế: Hàm dọn rác "vạn năng" cho dự án Crawler

Khi cào dữ liệu số lượng lớn, bạn nên viết một hàm xử lý rác chuẩn chỉnh để tái sử dụng cho mọi trang web như sau:
    
    
    from selectolax.lexbor import LexborHTMLParser
    
    def clean_html_and_get_text(html_string, extra_garbage_selectors=None):
        tree = LexborHTMLParser(html_string)
        
        # Danh sách các thẻ rác mặc định của mọi trang web
        default_garbage = ["script", "style", "iframe", "noscript", "header", "footer", "nav"]
        
        # Nếu người dùng có truyền thêm class/id rác cụ thể của trang đó
        if extra_garbage_selectors:
            default_garbage.extend(extra_garbage_selectors)
        
        # Tạo chuỗi CSS selector tổng hợp (ví dụ: "script, style, iframe, .ads-class")
        css_selector = ", ".join(default_garbage)
        
        # Tiến hành hủy diệt thẻ rác
        for node in tree.css(css_selector):
            node.decompose()
            
        # Trả về văn bản sạch, phân tách các đoạn bằng dấu xuống dòng cho đẹp
        return tree.root.text(strip=True, separator='\n')
    
    # Sử dụng hàm:
    # text = clean_html_and_get_text(raw_html, extra_garbage_selectors=[".sidebar", "#comments"])
    

Nếu bạn đang cào một trang web cụ thể và nội dung trích xuất ra vẫn bị lẫn các đoạn chữ lạ (như thanh menu, bài viết liên quan, hoặc khung bình luận), hãy gửi đoạn HTML hoặc class của các vùng rác đó lên đây. Tôi sẽ giúp bạn thiết lập bộ lọc loại bỏ chúng một cách triệt để!