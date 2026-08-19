Thư viện selectolax [1] là một trong những bộ phân tích cú pháp HTML (HTML parser) có tốc độ xử lý nhanh nhất hiện nay trong hệ sinh thái Python. Nhờ được viết bằng ngôn ngữ C/C++ trên nền tảng hai công cụ nguồn mở mãnh mẽ là Modest và Lexbor, `selectolax` có khả năng phân tích cây tài liệu HTML (DOM) và truy xuất dữ liệu bằng bộ chọn CSS (CSS Selectors) với tốc độ nhanh gấp từ 10 đến 30 lần so với BeautifulSoup.

Dưới đây là cẩm nang chi tiết toàn tập về cách sử dụng, các phương thức cốt lõi và kỹ thuật nâng cao của `selectolax`.

* * *

## 1\. Khởi tạo và Lựa chọn Backend

`selectolax` cung cấp hai backend chính để bạn lựa chọn khi phân tích HTML. Bạn nên ưu tiên sử dụng Lexbor vì nó hiện đại, hỗ trợ HTML5 tốt hơn và có hiệu năng tối ưu nhất.
    
    
    from selectolax.lexbor import LexborHTMLParser
    # Hoặc dùng Modest (cũ hơn): from selectolax.parser import HTMLParser
    
    html_doc = "<div><p class='text'>Chào mừng bạn!</p></div>"
    
    # Khởi tạo bộ phân tích parser
    parser = LexborHTMLParser(html_doc)
    

* * *

## 2\. Các phương thức Tìm kiếm & Điều hướng (Tìm từ Parser)

Khi gọi phương thức từ đối tượng gốc (`parser`), bạn có các lựa chọn tìm kiếm cốt lõi sau:

## 📌 Tìm kiếm bằng CSS Selector

  * `.css_first(selector, default=None, strict=False)`: Tìm và trả về duy nhất một phần tử (Node) đầu tiên khớp với bộ chọn CSS. Nếu không tìm thấy, trả về giá trị của tham số `default` (mặc định là `None`). Nếu đặt `strict=True`, nó sẽ ném ra lỗi `SelectorError` thay vì trả về `None`.
  * `.css(selector)`: Tìm và trả về một danh sách (Python list) chứa tất cả các đối tượng Node khớp với bộ chọn CSS.


    
    
    # Lấy phần tử đầu tiên
    first_p = parser.css_first("p.text")
    
    # Lấy tất cả phần tử khớp điều kiện
    all_divs = parser.css("div")
    

## 📌 Điều hướng cây thư mục gốc

  * `.body`: Thuộc tính đi thẳng tới Node đại diện cho thẻ `<body>` của tài liệu.
  * `.root`: Thuộc tính trả về Node gốc cao nhất của cây thư mục (thường là thẻ `<html>`).



* * *

## 3\. Các thuộc tính và phương thức của một nút (Node)

Khi bạn đã lấy được một phần tử (Node) từ hàm `.css()` hoặc `.css_first()`, đối tượng Node này cung cấp sẵn các công cụ mạnh mẽ để trích xuất hoặc chỉnh sửa:

## 📑 Nhóm trích xuất dữ liệu (Data Extraction)

  * `.text(deep=True, separator='')`: Trích xuất chuỗi văn bản thô bên trong thẻ.

    * `deep=True` (Mặc định): Lấy toàn bộ chữ của thẻ hiện tại và toàn bộ chữ của các thẻ con lồng bên trong nó.
    * `deep=False`: Chỉ lấy chữ của riêng thẻ hiện tại, bỏ qua văn bản nằm trong các thẻ con.
    * `separator=' '`: Ký tự phân tách văn bản giữa các thẻ con (rất hữu ích khi các thẻ bị dính chữ).

  * `.attributes`: Trả về một Python Dictionary chứa toàn bộ các thuộc tính (`href`, `src`, `id`, `class`...) và giá trị của thẻ đó. Nếu thuộc tính không tồn tại, bạn có thể dùng `.get()` của từ điển để tránh lỗi.
  * `.html`: Trả về chuỗi mã HTML thô (Outer HTML) của chính thẻ đó và toàn bộ nội dung bên trong nó.
  * `.text_content`: Tương tự như `.text(deep=True)` nhưng giữ nguyên cấu trúc xuống dòng nguyên bản của HTML.
  * `.tag`: Trả về tên thẻ dưới dạng chuỗi viết thường (ví dụ: `'div'`, `'a'`).


    
    
    node = parser.css_first("p.text")
    if node:
        print(node.text())              # Lấy chữ
        print(node.tag)                 # Kết quả: 'p'
        print(node.attributes.get('id')) # Lấy id an toàn
    

## 🌲 Nhóm điều hướng quan hệ (DOM Navigation)

  * `.parent`: Di chuyển lên một cấp, trả về Node cha trực tiếp bao bọc nó.
  * `.next`: Trả về Node anh-em nằm ngay phía sau (cùng cấp).
  * `.prev`: Trả về Node anh-em nằm ngay phía trước (cùng cấp).
  * `.child`: Trả về Node con đầu tiên của thẻ hiện tại.



## ✂️ Nhóm chỉnh sửa cấu trúc (Modification)

  * `.decompose()`: Xóa hoàn toàn Node hiện tại ra khỏi cây HTML. Phương thức này cực kỳ quan trọng để dọn rác (xóa bỏ các thẻ `<script>`, `<style>`, quảng cáo) giúp dữ liệu text lấy ra sạch sẽ hơn và tiết kiệm bộ nhớ.
  * `.strip_tags(tags_list)`: Xóa bỏ các thẻ được chỉ định trong danh sách nhưng giữ lại phần chữ bên trong chúng (ví dụ: biến `<b>Chữ</b>` thành `Chữ`).



* * *

## 4\. Ví dụ tổng hợp: Cào dữ liệu thực tế với Selectolax

Dưới đây là kịch bản hoàn chỉnh: Phân tích một trang blog, xóa bỏ các thẻ script rác, trích xuất tiêu đề, danh sách các liên kết, và lấy nội dung chính của một bài viết.
    
    
    from selectolax.lexbor import LexborHTMLParser
    
    html_content = """
    <html>
        <head><title>Trang Tin Tức</title></head>
        <body>
            <nav><ul><li><a href="/home">Trang chủ</a></li></ul></nav>
            
            <div id="article-container">
                <h1 class="main-title">Hướng dẫn lập trình Python siêu tốc</h1>
                <p class="meta">Tác giả: <span>Nguyễn Văn A</span> | Ngày: 2026</p>
                
                <div class="content">
                    <p>Python là ngôn ngữ mã nguồn mở <b>mạnh mẽ</b>.</p>
                    <script>console.log("Mã script độc hại/quảng cáo");</script>
                    <p>Ứng dụng rất nhiều trong <a href="/ai">Trí tuệ nhân tạo</a>.</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    # 1. Khởi tạo parser
    tree = LexborHTMLParser(html_content)
    
    # 2. Dọn rác: Xóa bỏ toàn bộ thẻ script có trong bài viết
    for script_node in tree.css("script"):
        script_node.decompose()
    
    # 3. Trích xuất tiêu đề (Dùng css_first)
    title_node = tree.css_first("h1.main-title")
    if title_node:
        print(f"Tiêu đề: {title_node.text(strip=True)}")
    
    # 4. Trích xuất văn bản trong nội dung (Chỉ lấy chữ thuộc thẻ cha, hoặc lấy sạch)
    content_div = tree.css_first("div.content")
    if content_div:
        # Lấy sạch chữ bao gồm cả thẻ con, phân tách bằng khoảng trắng để tránh dính chữ
        clean_text = content_div.text(deep=True, separator=' ')
        print(f"Nội dung thô: {clean_text.strip()}")
    
    # 5. Thu thập toàn bộ liên kết (Dùng vòng lặp với .css)
    print("\n--- Danh sách liên kết trong bài viết ---")
    for link in tree.css("div.content a"):
        url = link.attributes.get('href')
        text = link.text()
        print(f"- {text}: {url}")
    

## Tại sao bạn nên chuyển từ BeautifulSoup sang Selectolax?

  1. Tiết kiệm tài nguyên: `selectolax` tiêu tốn cực kỳ ít RAM so với BeautifulSoup khi xử lý các file HTML lớn hàng chục Megabyte.
  2. Tốc độ hủy diệt: Phù hợp tuyệt đối cho các tác vụ Crawl dữ liệu bất đồng bộ (`asyncio`, `httpx`, `aiohttp`) nơi mà tốc độ phân tích cú pháp HTML của CPU thường là nút thắt cổ chai khiến chương trình bị chậm.



Nếu bạn đang gặp khó khăn khi chuyển đổi một hàm cụ thể nào từ BeautifulSoup sang `selectolax` (ví dụ như tìm kiếm theo biểu thức chính quy Regex hoặc lọc thẻ theo điều kiện phức tạp), hãy gửi yêu cầu đó tại đây để tôi viết mã mẫu tối ưu cho bạn!