# Buổi 1 — Giới thiệu Parsel

* * *

# 1\. Parsel là gì?

Parsel là thư viện dùng để:

  * đọc HTML 
  * đọc XML 
  * chọn node bằng CSS 
  * chọn node bằng XPath 
  * lấy text 
  * lấy attribute 
  * regex trên kết quả 



Nó chính là phần parser của Scrapy.

Ví dụ:
    
    
    from parsel import Selector
    
    html = """
    <html>
        <body>
            <h1>Hello</h1>
        </body>
    </html>
    """
    
    sel = Selector(text=html)
    
    print(sel.css("h1::text").get())

Kết quả
    
    
    Hello

* * *

# 2\. Vì sao dùng Parsel thay BeautifulSoup?

BeautifulSoup
    
    
    soup.find(...)

Parsel
    
    
    selector.css(...)
    selector.xpath(...)

Điểm mạnh của Parsel:

✔ CSS selector cực nhanh

✔ XPath đầy đủ

✔ API rất gọn

✔ dùng trong Scrapy

✔ ít code

* * *

# 3\. Cài đặt
    
    
    pip install parsel

Kiểm tra
    
    
    import parsel
    
    print(parsel.__version__)

* * *

# 4\. Thành phần quan trọng nhất

Thư viện chỉ có vài class quan trọng.
    
    
    Selector
    SelectorList

Trong đó
    
    
    Selector

là class bạn dùng 99% thời gian.

* * *

# 5\. Selector là gì?

Selector giống như:

> "đại diện cho một tài liệu HTML/XML"

Ví dụ
    
    
    html = "<h1>Hello</h1>"
    
    sel = Selector(text=html)

Lúc này
    
    
    sel

đại diện toàn bộ HTML.

Bạn có thể:
    
    
    sel.css(...)
    sel.xpath(...)
    sel.get()
    sel.getall()
    sel.re(...)

* * *

# 6\. HTML mẫu

Suốt khóa học ta dùng HTML sau.
    
    
    <html>
    <body>
    
    <div class="book">
    
        <h2>Python</h2>
    
        <span class="price">100</span>
    
        <a href="/python">Read</a>
    
    </div>
    
    <div class="book">
    
        <h2>Java</h2>
    
        <span class="price">150</span>
    
        <a href="/java">Read</a>
    
    </div>
    
    </body>
    </html>

* * *

# 7\. Tạo Selector
    
    
    from parsel import Selector
    
    html = """..."""
    
    sel = Selector(text=html)

Lúc này
    
    
    sel

là node gốc.

* * *

# 8\. CSS đầu tiên

Lấy tất cả
    
    
    .book
    
    
    books = sel.css(".book")

`books` không phải list Python.

Nó là
    
    
    SelectorList

gồm nhiều Selector.
    
    
    Selector
    │
    ├── book1
    ├── book2

* * *

# 9\. Lấy tiêu đề
    
    
    titles = sel.css("h2::text").getall()
    
    print(titles)

Kết quả
    
    
    ['Python', 'Java']

* * *

# 10\. Lấy giá
    
    
    prices = sel.css(".price::text").getall()
    
    
    ['100', '150']

* * *

# 11\. Lấy href
    
    
    hrefs = sel.css("a::attr(href)").getall()
    
    
    ['/python', '/java']

* * *

# 12\. Lấy phần tử đầu tiên
    
    
    title = sel.css("h2::text").get()
    
    print(title)
    
    
    Python

`get()` luôn trả phần tử đầu tiên.

* * *

# 13\. XPath

Có thể dùng XPath thay CSS.
    
    
    titles = sel.xpath("//h2/text()").getall()
    
    
    ['Python', 'Java']

* * *

# 14\. CSS và XPath giống nhau

CSS
    
    
    sel.css("h2::text")

XPath
    
    
    sel.xpath("//h2/text()")

Đều trả về
    
    
    SelectorList

* * *

# 15\. Mỗi node cũng là Selector

Ví dụ
    
    
    books = sel.css(".book")

Lặp
    
    
    for book in books:
        print(type(book))

Kết quả
    
    
    <class 'parsel.selector.Selector'>

Mỗi book lại có thể
    
    
    book.css(...)
    
    
    book.xpath(...)

Ví dụ
    
    
    for book in books:
    
        title = book.css("h2::text").get()
    
        print(title)
    
    
    Python
    
    Java

Đây chính là cách viết parser sạch và dễ bảo trì.

* * *

# 16\. Ví dụ hoàn chỉnh
    
    
    from parsel import Selector
    
    html = """
    <html>
    <body>
    
    <div class="book">
        <h2>Python</h2>
        <span class="price">100</span>
        <a href="/python">Read</a>
    </div>
    
    <div class="book">
        <h2>Java</h2>
        <span class="price">150</span>
        <a href="/java">Read</a>
    </div>
    
    </body>
    </html>
    """
    
    sel = Selector(text=html)
    
    books = sel.css(".book")
    
    for book in books:
    
        title = book.css("h2::text").get()
    
        price = book.css(".price::text").get()
    
        href = book.css("a::attr(href)").get()
    
        print({
            "title": title,
            "price": price,
            "href": href,
        })

Kết quả
    
    
    {'title': 'Python', 'price': '100', 'href': '/python'}
    
    {'title': 'Java', 'price': '150', 'href': '/java'}

* * *

# 17\. So sánh với BeautifulSoup

BeautifulSoup:
    
    
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html, "html.parser")
    
    for book in soup.find_all("div", class_="book"):
        title = book.find("h2").text
        price = book.find("span", class_="price").text
        href = book.find("a")["href"]

Parsel:
    
    
    from parsel import Selector
    
    sel = Selector(text=html)
    
    for book in sel.css(".book"):
        title = book.css("h2::text").get()
        price = book.css(".price::text").get()
        href = book.css("a::attr(href)").get()

Parsel thường ngắn gọn hơn khi cần dùng CSS Selector hoặc XPath, đặc biệt trong các dự án crawler.

* * *

# 18\. Best Practices

  * Tạo `Selector` một lần cho mỗi tài liệu HTML. 
  * Chia nhỏ phạm vi tìm kiếm: lấy từng `.book` rồi mới truy vấn bên trong để tránh selector dài và khó đọc. 
  * Dùng CSS khi truy vấn đơn giản, dùng XPath khi cần điều kiện phức tạp hoặc điều hướng theo cấu trúc cây. 
  * Sử dụng `get(default=None)` hoặc kiểm tra kết quả khi dữ liệu có thể thiếu để tránh lỗi khi xử lý tiếp. 
  * Tách logic phân tích HTML thành các hàm hoặc lớp `Parser`, giúp dễ kiểm thử và tái sử dụng. 



* * *

# Bài tập thực hành

Cho HTML:
    
    
    <html>
    <body>
    
    <div class="student">
        <h3>Alice</h3>
        <span>20</span>
    </div>
    
    <div class="student">
        <h3>Bob</h3>
        <span>22</span>
    </div>
    
    <div class="student">
        <h3>Charlie</h3>
        <span>19</span>
    </div>
    
    </body>
    </html>

Hãy sử dụng `parsel.Selector` để:

  1. Lấy danh sách tất cả tên sinh viên. 
  2. Lấy danh sách tất cả tuổi. 
  3. In ra danh sách các `dict` có dạng: 


    
    
    [
        {"name": "Alice", "age": "20"},
        {"name": "Bob", "age": "22"},
        {"name": "Charlie", "age": "19"},
    ]

  4. Viết hàm: 


    
    
    def parse_students(html: str) -> list[dict]:
        ...

trả về đúng cấu trúc dữ liệu trên.

* * *

Ở **Buổi 2** , chúng ta sẽ đi sâu vào **`parsel.Selector`** : cách `Selector` biểu diễn cây DOM, các tham số khởi tạo (`text`, `body`, `type`, `base_url`), sự khác biệt giữa `Selector`, `SelectorList` và node HTML, cũng như cách điều hướng giữa các node để xây dựng parser chuyên nghiệp giống như trong Scrapy.

