# Khóa học Parsel

# Buổi 2 — `parsel.Selector` Deep Dive

Ở buổi trước, bạn đã biết cách sử dụng `Selector` để lấy dữ liệu bằng CSS và XPath.

Trong buổi này chúng ta sẽ tìm hiểu kỹ **`Selector`** , vì đây là class trung tâm của toàn bộ thư viện Parsel cũng như Scrapy.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Selector thực sự là gì 
  * Cấu trúc DOM trong Selector 
  * Khởi tạo Selector theo nhiều cách 
  * Các thuộc tính quan trọng 
  * CSS và XPath hoạt động như thế nào 
  * Node Context 
  * Relative Selector 
  * Những lỗi thường gặp 



* * *

# 1\. Selector là gì?

Có thể hiểu đơn giản:
    
    
    HTML
          ↓
    Selector
          ↓
    DOM Tree
          ↓
    CSS / XPath
          ↓
    Node

Ví dụ
    
    
    from parsel import Selector
    
    html = """
    <html>
        <body>
            <h1>Hello</h1>
        </body>
    </html>
    """
    
    sel = Selector(text=html)

Lúc này
    
    
    sel

không phải là string.

Nó là một object.
    
    
    print(type(sel))
    
    
    <class 'parsel.selector.Selector'>

* * *

# 2\. Selector lưu cái gì?

Giả sử HTML
    
    
    <html>
    <body>
    
    <div>
    
        <h1>Hello</h1>
    
    </div>
    
    </body>
    </html>

Sau khi tạo
    
    
    sel = Selector(text=html)

bên trong sẽ có cây DOM
    
    
    Selector
    
    │
    
    └── html
    
          │
    
          └── body
    
                │
    
                └── div
    
                      │
    
                      └── h1

Mỗi node đều có thể trở thành một Selector mới.

* * *

# 3\. Một node cũng là Selector

Ví dụ
    
    
    div = sel.css("div").get()

Sai.

Vì
    
    
    .get()

trả về string.

Đúng phải là
    
    
    div = sel.css("div")[0]

hoặc
    
    
    div = sel.css("div").xpath(".")

Hoặc
    
    
    div = sel.css("div")

nếu chỉ có một node.

Ví dụ
    
    
    book = sel.css(".book")[0]
    
    print(type(book))
    
    
    Selector

Book này lại có
    
    
    book.css(...)

và
    
    
    book.xpath(...)

* * *

# 4\. Context

Đây là điều quan trọng nhất.

Giả sử
    
    
    <div class="book">
    
        <h2>Python</h2>
    
    </div>
    
    <div class="book">
    
        <h2>Java</h2>
    
    </div>

Lấy tất cả
    
    
    books = sel.css(".book")

Ta có
    
    
    books
    
    │
    
    ├── book1
    
    └── book2

Bây giờ
    
    
    for book in books:
    
        print(book.css("h2::text").get())

Kết quả
    
    
    Python
    
    Java

Tại sao?

Vì mỗi Selector có context riêng.

Book đầu tiên chỉ nhìn thấy
    
    
    <div>
    
    <h2>Python</h2>
    
    </div>

Book thứ hai chỉ nhìn thấy
    
    
    <div>
    
    <h2>Java</h2>
    
    </div>

* * *

# 5\. Context giúp code sạch

Không nên
    
    
    titles = sel.css(".book h2::text")

rồi lấy giá
    
    
    prices = sel.css(".book .price::text")

Sau đó zip.

Nên
    
    
    for book in sel.css(".book"):
    
        title = book.css("h2::text").get()
    
        price = book.css(".price::text").get()

Đây chính là phong cách Scrapy.

* * *

# 6\. Selector(text=...)

Đây là cách dùng phổ biến nhất.
    
    
    Selector(text=html)

Ví dụ
    
    
    from parsel import Selector
    
    html = "<h1>Hello</h1>"
    
    sel = Selector(text=html)

* * *

# 7\. Selector(body=...)

Nếu đã có bytes.

Ví dụ
    
    
    import requests
    from parsel import Selector
    
    r = requests.get("https://example.com")
    
    sel = Selector(body=r.content)

Không cần
    
    
    r.text

* * *

# 8\. text hay body?

Nếu
    
    
    str

↓
    
    
    text=

Nếu
    
    
    bytes

↓
    
    
    body=

Ví dụ
    
    
    html = "<h1>Hello</h1>"
    
    Selector(text=html)

Ví dụ
    
    
    html = b"<h1>Hello</h1>"
    
    Selector(body=html)

* * *

# 9\. type

Parsel hỗ trợ
    
    
    html
    
    xml

Ví dụ
    
    
    Selector(text=html, type="html")

hoặc
    
    
    Selector(text=xml, type="xml")

* * *

# 10\. HTML và XML khác nhau

HTML
    
    
    <br>

XML
    
    
    <br/>

HTML
    
    
    <img>

XML
    
    
    <img/>

Nếu parser XML

hãy dùng
    
    
    Selector(text=data, type="xml")

* * *

# 11\. Root Selector

Selector đầu tiên
    
    
    Selector(text=...)

được gọi là Root.
    
    
    Root
    
    │
    
    ├── body
    
    ├── div
    
    ├── h1
    
    └── ...

Mọi query đều bắt đầu từ đây.

* * *

# 12\. Relative Selector

Giả sử
    
    
    book = sel.css(".book")[0]

Muốn lấy
    
    
    h2

Đúng
    
    
    book.css("h2::text")

Sai
    
    
    sel.css("h2::text")

vì
    
    
    sel

là root.
    
    
    book

là node con.

* * *

# 13\. XPath Relative

Ví dụ
    
    
    book.xpath(".//h2/text()")

Dấu
    
    
    .

rất quan trọng.

Nó nghĩa là
    
    
    node hiện tại

Nếu viết
    
    
    book.xpath("//h2/text()")

thì XPath sẽ tìm từ root của tài liệu, có thể trả về mọi `<h2>` trong toàn bộ HTML thay vì chỉ trong `book`.

Ví dụ:
    
    
    from parsel import Selector
    
    html = """
    <div class="book">
        <h2>Python</h2>
    </div>
    <div class="book">
        <h2>Java</h2>
    </div>
    """
    
    sel = Selector(text=html)
    
    book = sel.css(".book")[0]
    
    print(book.xpath(".//h2/text()").getall())
    # ['Python']
    
    print(book.xpath("//h2/text()").getall())
    # ['Python', 'Java']

* * *

# 14\. Kiểm tra Selector
    
    
    print(type(sel))
    
    
    Selector
    
    
    print(type(sel.css("h1")))
    
    
    SelectorList
    
    
    print(type(sel.css("h1")[0]))
    
    
    Selector

* * *

# 15\. Chuyển node thành HTML

Ví dụ
    
    
    book = sel.css(".book")[0]

In HTML
    
    
    print(book.get())

Kết quả
    
    
    <div class="book">
    
    ...
    
    </div>

Lưu ý:

  * `Selector.get()` trả về **HTML của node hiện tại**. 
  * `SelectorList.get()` trả về **HTML của phần tử đầu tiên** trong danh sách. 



* * *

# 16\. Lấy text

Ví dụ
    
    
    book.css("h2::text").get()

Kết quả
    
    
    Python

* * *

# 17\. Ví dụ hoàn chỉnh
    
    
    from parsel import Selector
    
    html = """
    <html>
    <body>
    
    <div class="book">
    
        <h2>Python</h2>
    
        <span class="price">100</span>
    
    </div>
    
    <div class="book">
    
        <h2>Java</h2>
    
        <span class="price">150</span>
    
    </div>
    
    </body>
    </html>
    """
    
    sel = Selector(text=html)
    
    print("ROOT:")
    print(type(sel))
    
    books = sel.css(".book")
    
    print(type(books))
    
    for book in books:
    
        print("-" * 30)
    
        print(type(book))
    
        print(book.get())
    
        print(book.css("h2::text").get())
    
        print(book.css(".price::text").get())

Kết quả:
    
    
    ROOT:
    <class 'parsel.selector.Selector'>
    
    <class 'parsel.selector.SelectorList'>
    
    ------------------------------
    <class 'parsel.selector.Selector'>
    <div class="book">...</div>
    Python
    100
    
    ------------------------------
    <class 'parsel.selector.Selector'>
    <div class="book">...</div>
    Java
    150

* * *

# 18\. Sơ đồ hoạt động của Selector
    
    
    HTML
    
          │
    
          ▼
    
    Selector(root)
    
          │
    
          ▼
    
    .css(".book")
    
          │
    
          ▼
    
    SelectorList
    
          │
    
     ┌────┴────┐
    
     ▼         ▼
    
    Selector   Selector
    
    (book1)    (book2)
    
     │            │
    
     ▼            ▼
    
    .css()      .css()
    
     │            │
    
     ▼            ▼
    
    text        text

Mô hình này rất quan trọng khi xây dựng parser cho các trang web lớn: luôn thu hẹp phạm vi truy vấn về node hiện tại thay vì tìm kiếm trên toàn bộ tài liệu.

* * *

# 19\. Những lỗi phổ biến

### Lỗi 1: Dùng `.get()` quá sớm
    
    
    book = sel.css(".book").get()
    
    book.css("h2::text")

❌ Sai vì `book` lúc này là `str`, không còn là `Selector`.

Đúng:
    
    
    book = sel.css(".book")[0]

* * *

### Lỗi 2: Nhầm `Selector` và `SelectorList`
    
    
    books = sel.css(".book")
    
    books.get()

`books.get()` chỉ lấy HTML của **phần tử đầu tiên**.

Nếu muốn duyệt tất cả:
    
    
    for book in books:
        ...

* * *

### Lỗi 3: Dùng XPath tuyệt đối trong node con
    
    
    book.xpath("//span/text()")

Có thể trả về tất cả `<span>` trong tài liệu.

Đúng:
    
    
    book.xpath(".//span/text()")

* * *

# Best Practices

  * Luôn giữ `Selector` càng lâu càng tốt, chỉ gọi `.get()` hoặc `.getall()` khi cần lấy dữ liệu cuối cùng. 
  * Duyệt từng node cha (`.book`, `.product`, `.article`) rồi mới lấy dữ liệu bên trong. 
  * Với XPath trên node con, ưu tiên dùng đường dẫn tương đối (`.//`). 
  * Nếu parser có nhiều bước, hãy truyền `Selector` giữa các hàm thay vì truyền HTML dạng chuỗi để tránh phải parse lại. 



* * *

# Bài tập

Cho HTML sau:
    
    
    <html>
    <body>
    
    <div class="product">
        <h2>Laptop A</h2>
        <span class="price">1500</span>
        <span class="brand">Dell</span>
    </div>
    
    <div class="product">
        <h2>Laptop B</h2>
        <span class="price">2200</span>
        <span class="brand">Lenovo</span>
    </div>
    
    <div class="product">
        <h2>Laptop C</h2>
        <span class="price">1800</span>
        <span class="brand">HP</span>
    </div>
    
    </body>
    </html>

Hãy thực hiện:

  1. Tạo `Selector` từ chuỗi HTML. 
  2. In kiểu dữ liệu của `sel`, `sel.css(".product")` và `sel.css(".product")[0]`. 
  3. Duyệt từng sản phẩm và in: 
     * Tên 
     * Giá 
     * Hãng 
  4. In HTML đầy đủ của sản phẩm thứ hai bằng `Selector.get()`. 
  5. Chứng minh sự khác nhau giữa: 
     * `product.xpath(".//span/text()")`
     * `product.xpath("//span/text()")`



Ở **Buổi 3** , chúng ta sẽ đi sâu vào **`SelectorList`** , cách hoạt động nội bộ, các phương thức như `get()`, `getall()`, `re()`, `re_first()`, khả năng lồng `SelectorList` và các kỹ thuật xử lý danh sách node hiệu quả trong các parser chuyên nghiệp.

