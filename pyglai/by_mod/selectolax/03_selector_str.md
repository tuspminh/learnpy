Trong phương thức `.css(selector)` của thư viện `selectolax`, tham số `selector` là một chuỗi (string) chứa bộ chọn CSS (CSS Selector) theo chuẩn W3C. Do `selectolax` được tối ưu hóa bằng C trên nền thư viện Lexbor, nó hỗ trợ gần như toàn bộ các cú pháp CSS Selector từ cơ bản đến nâng cao.

Dưới đây là chi tiết các loại cú pháp bạn có thể truyền vào tham số `selector` này:

* * *

## 1\. Bộ chọn Cơ bản (Basic Selectors)

  * Tên thẻ: Chọn tất cả các thẻ có cùng tên.

    * `tree.css("p")` → Lấy tất cả các thẻ `<p>`.

  * Class: Chọn theo thuộc tính `class`.

    * `tree.css(".title")` → Lấy tất cả thẻ có `class="title"`.

  * ID: Chọn theo thuộc tính `id`.

    * `tree.css("#main-content")` → Lấy thẻ có `id="main-content"`.




* * *

## 2\. Bộ chọn Thuộc tính (Attribute Selectors)

Đây là nhóm tham số quan trọng nhất trong cào dữ liệu vì nó giúp bạn giả lập tính năng tìm kiếm theo quy luật (gần giống Regex).

  * Khớp chính xác: `[attr=value]`

    * `tree.css("input[type='text']")` → Lấy thẻ input có type đúng bằng 'text'.

  * Bắt đầu bằng: `[attr^=value]`

    * `tree.css("a[href^='https://']")` → Lấy các liên kết bảo mật (bắt đầu bằng https).

  * Kết thúc bằng: `[attr$=value]`

    * `tree.css("img[src$='.png']")` → Chỉ lấy các thẻ ảnh có đuôi `.png`.

  * Chứa chuỗi: `[attr*=value]`

    * `tree.css("div[class*='product-']")` → Lấy tất cả các div có class chứa chữ `product-` (Ví dụ: `product-123`, `shopee-product-item`).




* * *

## 3\. Gộp nhiều Bộ chọn (Gộp bằng dấu phẩy)

Nếu bạn muốn tìm nhiều loại thẻ khác nhau cùng một lúc (thường dùng để gom các thẻ rác hoặc gom các tiêu đề), hãy phân tách chúng bằng dấu phẩy `,`.

  * `tree.css("script, style, .ads-banner, #footer")`

    * _Ý nghĩa:_ Tìm tất cả các thẻ `script`, tất cả thẻ `style`, tất cả thẻ có class `ads-banner` và thẻ có id `footer` cùng một lúc để bạn tiến hành xử lý (ví dụ: dùng `.decompose()` để xóa).




* * *

## 4\. Bộ chọn Mối quan hệ (Combinators)

  * Quan hệ Con cháu (Khoảng trắng): Tìm phần tử nằm bên trong phần tử khác (không quan tâm sâu bao nhiêu cấp).

    * `tree.css("div.content p")` → Tìm tất cả thẻ `<p>` nằm bên trong `<div class="content">`.

  * Quan hệ Con trực tiếp (`>`): Chỉ tìm phần tử là con ở cấp ngay dưới.

    * `tree.css("ul.menu > li")` → Chỉ lấy các thẻ `<li>` là con trực tiếp của `<ul>`, bỏ qua các `<li>` của menu con lồng sâu hơn.

  * Quan hệ Anh em liền kề (`+`): Tìm phần tử nằm ngay sau phần tử trước đó.

    * `tree.css("h2 + p")` → Chỉ lấy thẻ `<p>` nằm ngay dưới thẻ `<h2>`.




* * *

## 5\. Bộ chọn giả lập (Pseudo-classes)

`selectolax` hỗ trợ một số bộ chọn giả lập để lọc phần tử theo vị trí trong danh sách:

  * `:first-child`: Lấy phần tử đầu tiên trong danh sách con.

    * `tree.css("ul > li:first-child")`

  * `:last-child`: Lấy phần tử cuối cùng trong danh sách con.

    * `tree.css("ul > li:last-child")`

  * `:nth-child(n)`: Lấy phần tử ở vị trí bất kỳ (vị trí `n` bắt đầu từ 1).

    * `tree.css("table tr:nth-child(2)")` → Lấy dòng thứ 2 của bảng HTML.

  * `:not(selector)`: Loại trừ các phần tử khớp với bộ chọn bên trong.

    * `tree.css("p:not(.highlight)")` → Lấy tất cả thẻ `<p>` ngoại trừ những thẻ có class là `highlight`.




* * *

## ⚠️ Lưu ý cực kỳ quan trọng (Khác biệt với Parsel/Scrapy)

Trong `selectolax`, tham số `selector` không hỗ trợ các cú pháp mở rộng không thuộc chuẩn CSS như:

  * `::text` (Cú pháp lấy chữ của Parsel/Scrapy) → _Sai cú pháp trong selectolax._
  * `::attr(href)` (Cú pháp lấy thuộc tính của Parsel) → _Sai cú pháp trong selectolax._



Cách viết đúng trong selectolax: Bạn chỉ dùng CSS Selector để tìm đến thẻ Node, sau đó dùng phương thức của Node để lấy dữ liệu:
    
    
    # SAI: tree.css("a::attr(href)")
    # ĐÚNG:
    for node in tree.css("a"):
        url = node.attributes.get('href')
    

Nếu bạn đang có một cấu trúc HTML phức tạp hoặc một bài toán lọc dữ liệu cụ thể mà chưa biết nên viết chuỗi `selector` như thế nào, hãy gửi đoạn HTML đó lên đây để tôi viết mẫu chính xác cho bạn!