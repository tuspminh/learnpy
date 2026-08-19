Thư viện html2text trong Python cung cấp rất nhiều tham số (được gọi là các thuộc tính cấu hình) để bạn kiểm soát chính xác cách chuyển đổi từ HTML sang Markdown hoặc Text thuần. [1, 2] 

Để sử dụng các tham số này, bạn cần khởi tạo đối tượng `html2text.HTML2Text()` thay vì gọi hàm `html2text.html2text()` dạng rút gọn. [3, 4] 

Dưới đây là các nhóm tham số quan trọng nhất được phân loại theo chức năng:

* * *

## 1\. Nhóm xử lý Liên kết (Links) & Hình ảnh (Images)

  * `ignore_links` _(Boolean, Mặc định:`False`)_: Nếu đặt là `True`, thư viện sẽ xóa bỏ toàn bộ URL. Nó chỉ giữ lại phần chữ hiển thị bên trong thẻ `<a>`. [4, 5] 
  * `ignore_images` _(Boolean, Mặc định:`False`)_: Nếu đặt là `True`, nó sẽ xóa bỏ hoàn toàn định dạng của các thẻ ảnh `<img>`, không hiển thị đường dẫn ảnh hay chữ thay thế. [5, 6] 
  * `images_to_alt` _(Boolean, Mặc định:`False`)_: Nếu đặt là `True`, thẻ ảnh sẽ bị biến đổi thành chuỗi text thuần của thuộc tính `alt` (ví dụ: thay vì `![Mô tả](anh.jpg)` thì nó chỉ lấy chữ `Mô tả`).
  * `no_wrap_links` _(Boolean, Mặc định:`False`)_: Ngăn chặn việc tự động xuống dòng ở giữa các đường link dài.
  * `reference_links` _(Boolean, Mặc định:`False`)_: Chuyển đổi định dạng link sang dạng tham chiếu (đặt toàn bộ danh sách URL ở cuối văn bản giống như mục tài liệu tham khảo của Wikipedia). [1, 5] 



## 2\. Nhóm định dạng Văn bản & Bố cục (Layout & Typography)

  * `body_width` _(Integer, Mặc định:`78`)_: Số lượng ký tự tối đa trên một dòng. Sau số ký tự này, văn bản sẽ tự động bị bẻ dòng (`\n`). Khuyên dùng: Đặt bằng `0` nếu bạn muốn tắt tính năng tự động xuống dòng và giữ nguyên các đoạn văn bản dài chạy liên tục. [2, 6, 7] 
  * `ignore_emphasis` _(Boolean, Mặc định:`False`)_: Nếu đặt là `True`, nó sẽ bỏ qua các định dạng in đậm (`<b>`, `<strong>`) và in nghiêng (`<i>`, `<em>`). Toàn bộ chữ sẽ biến thành chữ thường không có dấu `*` hoặc `_`. [5] 
  * `dash_unordered-list` _(Boolean, Mặc định:`False`)_: Mặc định danh sách không thứ tự sử dụng dấu sao (`* Item`). Đổi thành `True` nếu bạn muốn dùng dấu gạch ngang (`- Item`). [6, 8] 
  * `single_line_break` _(Boolean, Mặc định:`False`)_: Buộc các khối phần tử (như giữa các đoạn văn `<p>`) chỉ cách nhau duy nhất 1 dấu xuống dòng thay vì 2 dấu xuống dòng trống. [5] 



## 3\. Nhóm xử lý Bảng (Tables)

  * `ignore_tables` _(Boolean, Mặc định:`False`)_: Nếu đặt là `True`, thư viện sẽ bỏ qua cấu trúc bảng (`<table>`), chỉ trích xuất phần chữ bên trong các ô một cách thô sơ.
  * `bypass_tables` _(Boolean, Mặc định:`False`)_: Nếu đặt là `True`, các thẻ bảng HTML sẽ được giữ nguyên ở dạng mã HTML thô thay vì cố gắng chuyển đổi nó sang dạng bảng Markdown.
  * `pad_tables` _(Boolean, Mặc định:`False`)_: Tự động căn chỉnh và thêm các khoảng trắng vào các ô trong bảng Markdown để cấu trúc bảng trông vuông vắn, đẹp mắt và dễ đọc hơn khi xem bằng mắt thường. [5, 9] 



## 4\. Nhóm xử lý Mã nguồn (Code blocks)

  * `mark_code` _(Boolean, Mặc định:`False`)_: Đánh dấu các khối code (`<pre>`, `<code>`) bằng thẻ đặc biệt `[code]...[/code]` thay vì dùng các dấu backtick (```) mặc định của Markdown.
  * `backquote_code_style` _(Boolean, Mặc định:`False`)_: Ép buộc sử dụng cú pháp dấu backtick cho các khối code dài thay vì dùng cách thụt lề tab truyền thống của Markdown. [1, 5] 



* * *

## Ví dụ áp dụng thực tế cấu hình nâng cao

Dưới đây là cách bạn kết hợp nhiều tham số để dọn sạch một đoạn HTML phức tạp theo ý muốn:
    
    
    import html2text
    
    html_content = """
    <div>
        <h1>Bài viết mẫu</h1>
        <p>Hãy truy cập <a href="https://example.com">đường link này</a> để xem chi tiết.</p>
        <img src="logo.png" alt="Ảnh Logo Công Ty">
        <p>Đoạn văn này rất dài và chúng ta không muốn nó bị tự động cắt dòng khi đạt tới giới hạn ký tự mặc định.</p>
    </div>
    """
    
    # 1. Khởi tạo đối tượng
    config = html2text.HTML2Text()
    
    # 2. Cấu hình các tham số mong muốn
    config.ignore_links = True       # Không lấy link URL, chỉ lấy chữ
    config.images_to_alt = True      # Biến ảnh thành chữ alt thô
    config.body_width = 0            # Tắt tự động bẻ dòng, giữ chữ chạy dài liên tục
    
    # 3. Tiến hành chuyển đổi
    markdown_output = config.handle(html_content)
    print(markdown_output)
    

Kết quả đầu ra:
    
    
    # Bài viết mẫu
    
    Hãy truy cập đường link này để xem chi tiết.
    
    Ảnh Logo Công Ty
    
    Đoạn văn này rất dài và chúng ta không muốn nó bị tự động cắt dòng khi đạt tới giới hạn ký tự mặc định.
    

Nếu bạn đang gặp rắc rối với một cấu trúc HTML cụ thể nào (ví dụ: bảng bị vỡ, link làm rối văn bản, hoặc chữ bị xuống dòng lung tung), hãy gửi đoạn HTML đó lên, tôi sẽ tư vấn bộ tham số tối ưu nhất cho bạn!

  


[1] [https://pypi.org](https://pypi.org/project/html2text/)

[2] [https://medium.com](https://medium.com/@tubelwj/how-to-utilize-html2text-in-python-a-quick-guide-4d4ad799c445)

[3] [https://github.com](https://github.com/Alir3z4/html2text/blob/master/docs/usage.md)

[4] [https://pypi.org](https://pypi.org/project/html2text2/)

[5] [https://www.mankier.com](https://www.mankier.com/1/python3-html2text)

[6] [https://github.com](https://github.com/aaronsw/html2text)

[7] [https://www.npmjs.com](https://www.npmjs.com/package/html-to-text)

[8] [https://gist.github.com](https://gist.github.com/reorx/4140119)

[9] [https://github.com](https://github.com/Alir3z4/html2text/blob/master/docs/usage.md)