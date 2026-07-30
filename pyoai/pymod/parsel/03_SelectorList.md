# Khóa học Parsel

# Buổi 3 — `SelectorList` Deep Dive

Ở buổi trước, chúng ta đã học `Selector`. Hôm nay sẽ học class quan trọng thứ hai trong Parsel:

> **`SelectorList`**

Nếu hiểu rõ `SelectorList`, bạn sẽ tránh được rất nhiều lỗi khi viết crawler.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * `SelectorList` là gì 
  * Khi nào Parsel trả về `SelectorList`
  * Khác nhau giữa `Selector` và `SelectorList`
  * Các phương thức quan trọng 
  * Có thể lồng `SelectorList` như thế nào 
  * Các lỗi phổ biến 
  * Best Practices 



* * *

# 1\. SelectorList là gì?

Giả sử HTML
    
    
    <html>
    <body>
    
    <div class="book">
        <h2>Python</h2>
    </div>
    
    <div class="book">
        <h2>Java</h2>
    </div>
    
    <div class="book">
        <h2>Rust</h2>
    </div>
    
    </body>
    </html>

Tạo Selector
    
    
    from parsel import Selector
    
    sel = Selector(text=html)

Lấy
    
    
    books = sel.css(".book")

Kiểu dữ liệu
    
    
    print(type(books))

Kết quả
    
    
    <class 'parsel.selector.SelectorList'>

* * *

# 2\. SelectorList không phải list thường

Nó hoạt động gần giống list Python.

Ví dụ
    
    
    books[0]
    books[1]
    books[2]

Đều được.

Có thể
    
    
    len(books)
    
    
    for book in books:
        ...
    
    
    books[-1]

Nhưng ngoài các tính năng của list, nó còn có thêm nhiều phương thức đặc biệt.

* * *

# 3\. Cấu trúc
    
    
    SelectorList
    
    │
    
    ├── Selector(book1)
    
    ├── Selector(book2)
    
    └── Selector(book3)

Mỗi phần tử đều là `Selector`.

* * *

# 4\. Kiểm tra kiểu
    
    
    print(type(books))

↓
    
    
    SelectorList
    
    
    print(type(books[0]))

↓
    
    
    Selector

* * *

# 5\. Có thể lặp
    
    
    for book in books:
    
        print(book.css("h2::text").get())

Kết quả
    
    
    Python
    
    Java
    
    Rust

* * *

# 6\. Có thể index
    
    
    first = books[0]
    
    
    last = books[-1]

Đây đều là
    
    
    Selector

* * *

# 7\. Có thể slice
    
    
    books[:2]

Kết quả
    
    
    SelectorList

Không phải list.

Ví dụ
    
    
    top2 = books[:2]
    
    print(type(top2))

↓
    
    
    SelectorList

Đây là điểm rất hay của Parsel.

* * *

# 8\. `get()`

Đây là phương thức gây nhầm lẫn nhiều nhất.

Ví dụ
    
    
    titles = sel.css("h2::text")

Kiểu
    
    
    SelectorList

Nếu
    
    
    titles.get()

Kết quả
    
    
    Python

Chỉ phần tử đầu tiên.

* * *

# 9\. `getall()`

Ví dụ
    
    
    titles = sel.css("h2::text")
    
    
    titles.getall()

↓
    
    
    [
        "Python",
        "Java",
        "Rust"
    ]

* * *

# 10\. Minh họa
    
    
    SelectorList
    
    │
    
    ├── Python
    
    ├── Java
    
    └── Rust

`get()`

↓
    
    
    Python

`getall()`

↓
    
    
    [
    Python,
    Java,
    Rust
    ]

* * *

# 11\. `extract()`

Ngày xưa Scrapy dùng
    
    
    .extract()

Hiện nay
    
    
    .getall()

được khuyến khích hơn.

Ví dụ
    
    
    titles.getall()

và
    
    
    titles.extract()

cho cùng kết quả.

* * *

# 12\. `extract_first()`

Ngày xưa
    
    
    .extract_first()

Hiện nay nên dùng
    
    
    .get()

* * *

# 13\. `re()`

Có thể áp dụng regex trên toàn bộ danh sách.

Ví dụ
    
    
    <span>$100</span>
    
    <span>$200</span>
    
    <span>$300</span>
    
    
    prices = sel.css("span::text")
    
    
    prices.re(r"\d+")

↓
    
    
    [
    '100',
    '200',
    '300'
    ]

* * *

# 14\. `re_first()`
    
    
    prices.re_first(r"\d+")

↓
    
    
    100

* * *

# 15\. `attrib`

Ví dụ
    
    
    <a href="/python">
    
    
    links = sel.css("a")
    
    
    links[0].attrib

↓
    
    
    {
        "href": "/python"
    }

* * *

# 16\. Có thể lồng SelectorList

Ví dụ
    
    
    books = sel.css(".book")

Mỗi book
    
    
    book.css("span")

lại trả về
    
    
    SelectorList

Ta có
    
    
    SelectorList(book)
    
    ↓
    
    Selector
    
    ↓
    
    SelectorList(span)

Điều này rất phổ biến trong HTML lồng nhau.

* * *

# 17\. Ví dụ hoàn chỉnh
    
    
    from parsel import Selector
    
    html = """
    <html>
    <body>
    
    <div class="book">
        <h2>Python</h2>
        <span>100</span>
    </div>
    
    <div class="book">
        <h2>Java</h2>
        <span>200</span>
    </div>
    
    <div class="book">
        <h2>Rust</h2>
        <span>300</span>
    </div>
    
    </body>
    </html>
    """
    
    sel = Selector(text=html)
    
    books = sel.css(".book")
    
    print(type(books))
    print(len(books))
    
    print()
    
    print("Tên sách")
    
    titles = sel.css("h2::text")
    
    print(titles.get())
    
    print(titles.getall())
    
    print()
    
    print("Chi tiết")
    
    for book in books:
    
        print(book.css("h2::text").get())
    
        print(book.css("span::text").get())

Kết quả
    
    
    <class 'parsel.selector.SelectorList'>
    3
    
    Tên sách
    Python
    ['Python', 'Java', 'Rust']
    
    Chi tiết
    Python
    100
    Java
    200
    Rust
    300

* * *

# 18\. `SelectorList` hỗ trợ nhiều thao tác list
    
    
    books = sel.css(".book")
    
    print(len(books))
    
    
    print(books[:2])
    
    
    print(books[1:])
    
    
    print(books[-1])
    
    
    for item in books:
        print(item)

Bạn có thể kết hợp với list comprehension:
    
    
    titles = [
        book.css("h2::text").get()
        for book in books
    ]
    
    print(titles)

* * *

# 19\. `get(default=...)`

Một tính năng rất hữu ích là cung cấp giá trị mặc định nếu không tìm thấy kết quả.

Ví dụ:
    
    
    title = sel.css("h1::text").get(default="Không có tiêu đề")
    print(title)

Nếu HTML không có `<h1>`, kết quả sẽ là:
    
    
    Không có tiêu đề

Điều này giúp tránh phải viết nhiều câu lệnh `if` khi parser các trang có dữ liệu không đồng nhất.

* * *

# 20\. Những lỗi phổ biến

## Lỗi 1
    
    
    books.css("h2")

Sai.

`books` là `SelectorList`.

Không có phương thức `css()` áp dụng trực tiếp lên toàn bộ danh sách.

Đúng:
    
    
    for book in books:
    
        print(book.css("h2"))

* * *

## Lỗi 2
    
    
    book = books.get()

Kết quả
    
    
    str

Không còn là `Selector`.

Nếu cần `Selector`
    
    
    book = books[0]

* * *

## Lỗi 3
    
    
    books[0].getall()

Sai.

`Selector` không có ý nghĩa "lấy tất cả các node" như `SelectorList`. `Selector.get()` trả về HTML của node hiện tại; còn `SelectorList.getall()` trả về HTML của tất cả các node trong danh sách.

* * *

# So sánh `Selector` và `SelectorList`

Đặc điểm| Selector| SelectorList  
---|---|---  
Đại diện| Một node| Nhiều node  
`css()`| ✔| ✖  
`xpath()`| ✔| ✖  
`get()`| HTML của node hiện tại| HTML/text của phần tử đầu tiên  
`getall()`| ✖| HTML/text của tất cả phần tử  
Có thể lặp| ✖| ✔  
Có thể index| ✖| ✔  
  
* * *

# Best Practices

  * Khi mong đợi nhiều kết quả, hãy giữ nguyên `SelectorList` và lặp qua từng `Selector`. 
  * Chỉ gọi `get()` hoặc `getall()` ở bước cuối cùng khi cần lấy dữ liệu dạng chuỗi. 
  * Dùng `get(default=...)` để xử lý các trường có thể bị thiếu. 
  * Đừng nhầm lẫn giữa `books[0]` (một `Selector`) và `books.get()` (một `str`). 
  * Nếu mỗi node đại diện cho một thực thể (book, product, article...), hãy duyệt từng node rồi trích xuất các trường bên trong. Đây là cách tổ chức parser rõ ràng và dễ mở rộng. 



* * *

# Bài tập

Cho HTML:
    
    
    <html>
    <body>
    
    <ul class="menu">
        <li><a href="/home">Home</a></li>
        <li><a href="/blog">Blog</a></li>
        <li><a href="/about">About</a></li>
        <li><a href="/contact">Contact</a></li>
    </ul>
    
    </body>
    </html>

Hãy thực hiện:

  1. Lấy tất cả thẻ `<a>` thành một `SelectorList`. 
  2. In kiểu dữ liệu của danh sách và của phần tử đầu tiên. 
  3. In số lượng liên kết. 
  4. In: 
     * Liên kết đầu tiên (`get()`) 
     * Tất cả liên kết (`getall()`) 
  5. Duyệt từng `<a>` và in: 
     * Nội dung text 
     * Thuộc tính `href`
  6. Viết một hàm: 


    
    
    def parse_menu(html: str) -> list[dict]:
        ...

Trả về:
    
    
    [
        {"text": "Home", "href": "/home"},
        {"text": "Blog", "href": "/blog"},
        {"text": "About", "href": "/about"},
        {"text": "Contact", "href": "/contact"},
    ]

Ở **Buổi 4** , chúng ta sẽ đi sâu vào **CSS Selector** trong Parsel: cú pháp đầy đủ, các bộ chọn nâng cao, pseudo-element (`::text`, `::attr()`), kết hợp selector, và các mẹo viết selector ổn định cho các website thực tế.

