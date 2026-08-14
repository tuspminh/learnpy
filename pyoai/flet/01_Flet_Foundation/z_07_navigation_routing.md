# Buổi 7 — Navigation & Routing trong Flet

Từ Buổi 1 → 6, chúng ta mới chủ yếu xây **một màn hình**.

Nhưng một ứng dụng thật sẽ có:

```text
Home
Books
Book Detail
Reader
Settings
About
```

Ví dụ app đọc truyện của bạn:

```text
┌──────────────────────────────────────────────┐
│ Novel Reader                                 │
├──────────────────────────────────────────────┤
│ Home │ Library │ History │ Settings          │
├──────────────────────────────────────────────┤
│                                              │
│                 CONTENT                      │
│                                              │
└──────────────────────────────────────────────┘
```

Hôm nay chúng ta học cách xây hệ thống đó.

---

# 1. Navigation là gì?

Có 3 khái niệm cần phân biệt:

```text
Navigation
    ↓
Đi từ màn hình A → B

Routing
    ↓
Xác định URL/route nào tương ứng với màn hình nào

View
    ↓
UI của một màn hình
```

Ví dụ:

```text
"/"
    ↓
HomeView

"/books"
    ↓
BookListView

"/books/123"
    ↓
BookDetailView

"/reader/123/5"
    ↓
ReaderView

"/settings"
    ↓
SettingsView
```

---

# 2. Route

Route có thể hiểu đơn giản là:

> Một địa chỉ đại diện cho một màn hình hoặc trạng thái navigation.

Ví dụ:

```text
/
```

là Home.

```text
/books
```

là danh sách truyện.

```text
/settings
```

là Settings.

---

# 3. Route tree

Ứng dụng:

```text
Novel Reader
│
├── /
│
├── /books
│
├── /books/:id
│
├── /reader/:book_id/:chapter
│
└── /settings
```

Đây chính là **navigation tree**.

---

# 4. View

Một View đại diện cho một màn hình.

Ví dụ:

```python
home_view = ft.View(
    route="/",
    controls=[
        ft.Text("Home"),
    ],
)
```

Tư duy:

```text
View
│
├── route
└── controls
```

---

# 5. Một app nhiều View

Ví dụ:

```python
import flet as ft


def main(page: ft.Page):

    home_view = ft.View(
        route="/",
        controls=[
            ft.Text("Home"),
        ],
    )

    books_view = ft.View(
        route="/books",
        controls=[
            ft.Text("Books"),
        ],
    )

    page.views.append(home_view)
    page.views.append(books_view)

    page.update()


ft.run(main)
```

Nhưng cách này chưa phải navigation hoàn chỉnh.

Chúng ta cần routing.

---

# 6. `page.go()`

Đây là API rất quan trọng.

Ví dụ:

```python
page.go("/books")
```

Khi đó ứng dụng chuyển sang route:

```text
/
 ↓
/books
```

Ví dụ button:

```python
ft.Button(
    "Books",
    on_click=lambda e: page.go("/books"),
)
```

Flow:

```text
User click
    ↓
Button
    ↓
page.go("/books")
    ↓
Route changes
    ↓
Build View
```

---

# 7. `page.on_route_change`

Ta cần một nơi xử lý route.

```python
def route_change(e):
    print(page.route)
```

Sau đó:

```python
page.on_route_change = route_change
```

Khi:

```python
page.go("/books")
```

Flet gọi:

```python
route_change(...)
```

---

# 8. Routing cơ bản

Một cấu trúc:

```python
import flet as ft


def main(page: ft.Page):

    def route_change(e):
        page.views.clear()

        if page.route == "/":
            page.views.append(
                ft.View(
                    route="/",
                    controls=[
                        ft.Text("Home"),
                        ft.Button(
                            "Books",
                            on_click=lambda e: page.go("/books"),
                        ),
                    ],
                )
            )

        elif page.route == "/books":
            page.views.append(
                ft.View(
                    route="/books",
                    controls=[
                        ft.Text("Books"),
                        ft.Button(
                            "Home",
                            on_click=lambda e: page.go("/"),
                        ),
                    ],
                )
            )

        page.update()

    page.on_route_change = route_change

    page.go("/")


ft.run(main)
```

Đây là routing cơ bản.

---

# 9. Phân tích flow

Khi app chạy:

```text
page.go("/")
     ↓
route_change()
     ↓
page.route == "/"
     ↓
Home View
```

User click:

```text
Books
 ↓
page.go("/books")
 ↓
route_change()
 ↓
page.route == "/books"
 ↓
Books View
```

---

# 10. `page.route`

Route hiện tại:

```python
page.route
```

Ví dụ:

```python
print(page.route)
```

có thể trả:

```text
/
```

hoặc:

```text
/books
```

---

# 11. Tại sao không nên viết routing kiểu này mãi?

Code:

```python
if page.route == "/":
    ...
elif page.route == "/books":
    ...
elif page.route == "/settings":
    ...
elif page.route == "/reader":
    ...
elif page.route == "/history":
    ...
```

ban đầu ổn.

Nhưng app lớn sẽ thành:

```text
route_change()
    500 dòng
```

Đó là anti-pattern.

Chúng ta cần tách View.

---

# 12. Tách `HomeView`

```python
def build_home_view(page):
    return ft.View(
        route="/",
        controls=[
            ft.Text("Home"),
            ft.Button(
                "Books",
                on_click=lambda e: page.go("/books"),
            ),
        ],
    )
```

Books:

```python
def build_books_view(page):
    return ft.View(
        route="/books",
        controls=[
            ft.Text("Books"),
            ft.Button(
                "Home",
                on_click=lambda e: page.go("/"),
            ),
        ],
    )
```

---

# 13. Router đơn giản

Bây giờ:

```python
def build_route(page):
    if page.route == "/":
        return build_home_view(page)

    if page.route == "/books":
        return build_books_view(page)

    return build_not_found_view(page)
```

Sau đó:

```python
def route_change(e):
    page.views.clear()
    page.views.append(build_route(page))
    page.update()
```

Đã tốt hơn rất nhiều.

---

# 14. Kiến trúc

Bây giờ:

```text
main
│
├── Router
│
├── HomeView
│
├── BooksView
│
└── NotFoundView
```

Không còn:

```text
main
└── 500 dòng UI
```

---

# 15. Back navigation

Một ứng dụng thật cần:

```text
Home
 ↓
Books
 ↓
Book Detail
 ↓
Reader
```

User nhấn Back:

```text
Reader
 ↓
Book Detail
 ↓
Books
 ↓
Home
```

Flet hỗ trợ navigation stack thông qua `page.views`.

Mental model:

```text
Views Stack

┌──────────────┐
│ Reader       │ ← top
├──────────────┤
│ Book Detail  │
├──────────────┤
│ Books        │
├──────────────┤
│ Home         │
└──────────────┘
```

---

# 16. `page.views`

Ví dụ:

```python
page.views.append(
    ft.View(
        route="/",
        controls=[
            ft.Text("Home"),
        ],
    )
)
```

Sau đó:

```python
page.views.append(
    ft.View(
        route="/books",
        controls=[
            ft.Text("Books"),
        ],
    )
)
```

Stack:

```text
[
    HomeView,
    BooksView,
]
```

---

# 17. Back bằng pop

Về tư duy:

```python
page.views.pop()
```

sẽ loại View trên cùng.

Sau đó:

```python
page.update()
```

Nhưng trong ứng dụng có routing, cần đồng bộ stack với route.

Do đó chúng ta không nên tùy tiện thao tác stack ở mọi nơi.

---

# 18. `page.on_view_pop`

Flet cung cấp event để xử lý khi một View bị pop.

Mental model:

```text
User Back
    ↓
View Pop Event
    ↓
Route synchronization
    ↓
UI update
```

Ví dụ pattern:

```python
def view_pop(e):
    page.views.pop()
    page.go(page.views[-1].route)
```

Ý tưởng quan trọng hơn syntax:

> Navigation state và route phải được đồng bộ.

---

# 19. Router chuyên nghiệp hơn

Ta có thể xây:

```text
Router
│
├── navigate()
├── build_view()
├── handle_route_change()
└── handle_view_pop()
```

Ví dụ:

```python
class Router:

    def __init__(self, page):
        self.page = page

    def navigate(self, route):
        self.page.go(route)

    def build_view(self):
        ...
```

Sau này router có thể trở thành một component độc lập.

---

# 20. Navigation không nên biết business logic

Ví dụ không nên:

```python
def open_book(e):
    database.connect()
    database.query(...)
    parser.parse(...)
    page.go(...)
```

Button navigation nên chỉ làm:

```text
Click
 ↓
Navigation command
 ↓
Route
```

Business logic nên nằm ở:

```text
Use Case / Service
```

Ví dụ:

```text
UI
 ↓
OpenBookUseCase
 ↓
Repository
 ↓
Database
```

Sau đó:

```text
UI
 ↓
page.go("/books/123")
```

---

# 21. Dynamic route

Đây là phần cực kỳ quan trọng cho Novel Reader.

Ta có:

```text
/books/123
```

Trong đó:

```text
123
```

là:

```text
book_id
```

Ví dụ:

```text
/books/42
/books/100
/books/999
```

Không thể viết:

```python
if page.route == "/books/42":
```

vì có hàng nghìn book.

---

# 22. Parse route

Ta có thể:

```python
parts = page.route.split("/")
```

Ví dụ:

```text
/books/123
```

trở thành:

```python
[
    "",
    "books",
    "123",
]
```

Sau đó:

```python
book_id = parts[2]
```

Đây là cách đơn giản để hiểu routing động.

---

# 23. Dynamic route example

```python
def build_route(page):

    route = page.route

    if route == "/":
        return build_home_view(page)

    if route == "/books":
        return build_books_view(page)

    if route.startswith("/books/"):
        book_id = route.split("/")[2]

        return build_book_detail_view(
            page,
            book_id,
        )

    return build_not_found_view(page)
```

Bây giờ:

```text
/books/1
/books/2
/books/100
```

đều dùng:

```python
build_book_detail_view()
```

---

# 24. Novel Reader route tree

Một ứng dụng đọc truyện có thể:

```text
/
│
├── /books
│
├── /books/{book_id}
│
├── /reader/{book_id}/{chapter_id}
│
├── /history
│
└── /settings
```

Ví dụ:

```text
/books/123
```

→ Book Detail.

```text
/reader/123/5
```

→ Chapter 5 của Book 123.

---

# 25. Route parser

Thay vì parse khắp nơi:

```python
route.split("/")
```

hãy tạo:

```python
def parse_route(route):
    ...
```

Ví dụ:

```python
from dataclasses import dataclass


@dataclass
class RouteInfo:
    name: str
    params: dict
```

Ví dụ:

```text
/books/123
```

→

```python
RouteInfo(
    name="book_detail",
    params={
        "book_id": "123",
    },
)
```

Đây là bước đầu để xây router chuyên nghiệp.

---

# 26. Tách Router và View

Architecture:

```text
main
 │
 ▼
Router
 │
 ├── parse route
 │
 ├── resolve route
 │
 └── build view
       │
       ├── HomeView
       ├── BooksView
       ├── BookDetailView
       └── ReaderView
```

Đây là kiến trúc chúng ta muốn hướng tới.

---

# 27. Navigation với Bottom Navigation

Mobile app thường:

```text
┌──────────────────────┐
│                      │
│      CONTENT         │
│                      │
│                      │
├──────────────────────┤
│ Home │ Books │ More  │
└──────────────────────┘
```

Ta có thể dùng navigation control phù hợp của Flet.

Mental model:

```text
NavigationBar
      │
      ├── Home
      ├── Books
      └── Settings
```

Khi user chọn:

```text
Books
 ↓
page.go("/books")
```

---

# 28. Navigation rail

Desktop/tablet thường phù hợp với navigation rail/sidebar:

```text
┌──────┬─────────────────────────┐
│ Home │                         │
│ Books│        Content          │
│ Fav  │                         │
│      │                         │
└──────┴─────────────────────────┘
```

Responsive strategy:

```text
Desktop → NavigationRail / Sidebar
Mobile  → NavigationBar
```

Đây chính là nơi kiến thức Buổi 6 + Buổi 7 kết hợp.

---

# 29. App Shell

Một app lớn không nên mỗi View tự tạo Header/Navigation riêng.

Ta tạo:

```text
AppShell
│
├── Header
├── Navigation
└── Content
```

Ví dụ:

```text
┌──────────────────────────────────────────┐
│ Header                                   │
├──────────────┬───────────────────────────┤
│ Navigation   │ View                      │
│              │                           │
│              │                           │
└──────────────┴───────────────────────────┘
```

---

# 30. AppShell architecture

```text
Page
└── AppShell
    │
    ├── Header
    │
    ├── Navigation
    │
    └── Content
          │
          └── Current View
```

Khi route đổi:

```text
/books
```

chỉ:

```text
Current View
    ↓
BooksView
```

AppShell vẫn giữ nguyên.

Đây là architecture cực kỳ quan trọng.

---

# 31. Novel Reader AppShell

Ví dụ:

```text
┌─────────────────────────────────────────────┐
│ Novel Reader                         ⚙      │
├──────────────┬──────────────────────────────┤
│ Home         │                              │
│ Library      │         Current View         │
│ History      │                              │
│ Favorites    │                              │
│ Settings     │                              │
└──────────────┴──────────────────────────────┘
```

Route:

```text
/
    → Home

/books
    → Library

/history
    → History

/favorites
    → Favorites

/settings
    → Settings
```

---

# 32. View không nên chứa AppShell

Sai:

```text
HomeView
 ├── Header
 ├── Sidebar
 └── HomeContent

BooksView
 ├── Header
 ├── Sidebar
 └── BooksContent
```

Bạn sẽ lặp:

```text
Header
Sidebar
Navigation
```

đến hàng chục lần.

Tốt hơn:

```text
AppShell
├── Header
├── Sidebar
└── Content
      ├── HomeView
      ├── BooksView
      └── SettingsView
```

---

# 33. Routing + AppShell

Flow:

```text
User click Books
        ↓
page.go("/books")
        ↓
Router
        ↓
BooksView
        ↓
AppShell
        ↓
Content = BooksView
```

Header và Sidebar không bị recreate về mặt kiến trúc.

---

# 34. Route-driven UI

Một nguyên tắc rất mạnh:

> URL/route là source of truth cho navigation.

Ví dụ:

```text
/books
```

thì app phải hiển thị:

```text
BooksView
```

Không nên có:

```python
current_page = "books"
```

mà route lại là:

```text
/settings
```

Hai state mâu thuẫn nhau.

---

# 35. Sai lầm: hai navigation state

Không nên:

```python
current_page = "books"
page.route = "/settings"
```

Bạn có:

```text
State A
    current_page

State B
    route
```

và chúng có thể lệch nhau.

Tốt hơn:

```text
Route
  ↓
Resolve
  ↓
View
```

Route là navigation state.

---

# 36. Query parameters

Ngoài path:

```text
/books/123
```

còn có query:

```text
/books?search=naruto
```

Mental model:

```text
Path
/books

Query
search=naruto
```

Sau này search page có thể:

```text
/books?search=naruto
```

refresh app vẫn giữ search.

Đây là một lợi ích lớn của route-based state.

---

# 37. Route và deep linking

Một ưu điểm của routing:

User có thể mở trực tiếp:

```text
/reader/123/5
```

thay vì phải:

```text
Home
 ↓
Books
 ↓
Book 123
 ↓
Chapter 5
```

Đây gọi là:

> Deep linking.

Đặc biệt hữu ích cho app có URL hoặc web deployment.

---

# 38. Một Router hoàn chỉnh hơn

Ví dụ foundation:

```python
class Router:

    def __init__(self, page):
        self.page = page

    def navigate(self, route: str):
        self.page.go(route)

    def resolve(self, route: str):
        if route == "/":
            return "home"

        if route == "/books":
            return "books"

        if route == "/history":
            return "history"

        if route == "/settings":
            return "settings"

        return "404"
```

Sau này:

```text
resolve()
```

sẽ trả về route object thay vì string.

---

# 39. Một phiên bản tốt hơn

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Route:
    name: str
    path: str
```

Định nghĩa:

```python
HOME = Route("home", "/")
BOOKS = Route("books", "/books")
HISTORY = Route("history", "/history")
SETTINGS = Route("settings", "/settings")
```

Navigation:

```python
page.go(BOOKS.path)
```

Điều này tránh magic string rải khắp code.

---

# 40. Magic string problem

Không nên:

```python
page.go("/books")
```

xuất hiện ở 50 file.

Có thể dùng:

```python
Routes.BOOKS
```

hoặc:

```python
Routes.books()
```

Sau này khi refactor route:

```text
/books
```

thành:

```text
/library
```

chỉ cần sửa một nơi.

---

# 41. Navigation architecture cho app lớn

Cuối cùng chúng ta hướng tới:

```text
app/
│
├── main.py
│
├── routing/
│   ├── router.py
│   ├── routes.py
│   └── parser.py
│
├── layouts/
│   ├── app_shell.py
│   ├── desktop.py
│   └── mobile.py
│
└── views/
    ├── home.py
    ├── books.py
    ├── book_detail.py
    ├── reader.py
    ├── history.py
    └── settings.py
```

Đây là cấu trúc rất phù hợp với project Flet lớn.

---

# 42. Ví dụ mini project

Ta xây:

```text
Novel Reader
```

Routes:

```text
/
 /books
 /books/1
 /reader/1/1
 /history
 /settings
```

Navigation:

```text
Home
Books
History
Settings
```

---

# 43. Code foundation

```python
import flet as ft


def home_view(page):
    return ft.View(
        route="/",
        controls=[
            ft.Text(
                "Novel Reader",
                size=30,
            ),

            ft.Button(
                "Books",
                on_click=lambda e: page.go("/books"),
            ),
        ],
    )


def books_view(page):
    return ft.View(
        route="/books",
        controls=[
            ft.Text(
                "Books",
                size=30,
            ),

            ft.Button(
                "Book 1",
                on_click=lambda e: page.go("/books/1"),
            ),
        ],
    )


def book_detail_view(page, book_id):
    return ft.View(
        route=f"/books/{book_id}",
        controls=[
            ft.Text(
                f"Book {book_id}",
                size=30,
            ),

            ft.Button(
                "Read",
                on_click=lambda e:
                    page.go(f"/reader/{book_id}/1"),
            ),
        ],
    )


def reader_view(page, book_id, chapter_id):
    return ft.View(
        route=f"/reader/{book_id}/{chapter_id}",
        controls=[
            ft.Text(
                f"Book {book_id} - Chapter {chapter_id}",
                size=30,
            ),
        ],
    )
```

---

# 44. Route resolver

```python
def build_view(page):

    route = page.route

    if route == "/":
        return home_view(page)

    if route == "/books":
        return books_view(page)

    if route.startswith("/books/"):
        book_id = route.split("/")[2]

        return book_detail_view(
            page,
            book_id,
        )

    if route.startswith("/reader/"):
        parts = route.split("/")

        book_id = parts[2]
        chapter_id = parts[3]

        return reader_view(
            page,
            book_id,
            chapter_id,
        )

    return ft.View(
        route=route,
        controls=[
            ft.Text("404 - Not Found"),
        ],
    )
```

---

# 45. Main

```python
def main(page: ft.Page):

    def route_change(e):
        page.views.clear()

        page.views.append(
            build_view(page)
        )

        page.update()

    page.on_route_change = route_change

    page.go("/")


ft.run(main)
```

Đây đã là một mini routing system.

---

# 46. Nhưng còn một vấn đề

Nếu mỗi View chứa:

```python
Header
Sidebar
Footer
```

thì chúng ta lặp.

Do đó bước tiếp theo:

```text
View
 ↓
AppShell
 ↓
Content
```

---

# 47. Kiến trúc tốt hơn

```python
def build_shell(page, content):

    return ft.Column(
        controls=[
            build_header(page),

            ft.Row(
                controls=[
                    build_sidebar(page),

                    ft.Container(
                        expand=True,
                        content=content,
                    ),
                ],
                expand=True,
            ),
        ],
        expand=True,
    )
```

View chỉ cần:

```python
def build_books_content(page):
    return ft.Column(
        controls=[
            ft.Text("Books"),
        ],
    )
```

Sau đó:

```python
build_shell(
    page,
    build_books_content(page),
)
```

---

# 48. Kiến trúc cuối buổi

```text
                    Page
                     │
                     ▼
                  Router
                     │
              resolve route
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       HomeView   BooksView   ReaderView
          │          │          │
          └──────────┼──────────┘
                     ▼
                  AppShell
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
      Header      Navigation    Content
```

Đây là kiến trúc bạn nên ghi nhớ.

---

# 49. Navigation + Responsive

Kết hợp Buổi 6:

### Desktop

```text
AppShell
├── Header
├── Sidebar
└── Content
```

### Mobile

```text
AppShell
├── Header
├── Content
└── NavigationBar
```

Router không cần biết desktop/mobile.

```text
Router
   ↓
View
   ↓
Responsive AppShell
```

Đây là separation rất tốt.

---

# 50. Navigation + Domain

Với app cào truyện:

```text
Crawler Dashboard
│
├── Dashboard
├── Sources
├── Crawl Jobs
├── Workers
├── Books
├── Logs
└── Settings
```

Routes:

```text
/
/sources
/jobs
/workers
/books
/logs
/settings
```

Router chỉ biết:

```text
route → view
```

Không biết:

```text
SQLite
Crawler
Redis
Celery
HTTP
Parser
```

Đây là một nguyên tắc kiến trúc cực kỳ quan trọng.

---

# Bài tập Buổi 7

Xây **Novel Reader Navigation** với:

```text
/
├── /books
├── /books/1
├── /books/2
├── /reader/1/1
├── /reader/1/2
├── /history
└── /settings
```

## Yêu cầu 1 — Router

Tạo:

```text
router.py
```

có:

```python
class Router:
    ...
```

Router phải xử lý:

```text
/
 /books
 /books/{id}
 /reader/{book_id}/{chapter_id}
 /history
 /settings
```

---

## Yêu cầu 2 — Views

Tạo:

```text
views/
├── home.py
├── books.py
├── book_detail.py
├── reader.py
├── history.py
└── settings.py
```

Mỗi file có một hàm:

```python
build_view(...)
```

---

## Yêu cầu 3 — AppShell

Tạo:

```text
layouts/
└── app_shell.py
```

Có:

```text
Header
Navigation
Content
```

---

## Yêu cầu 4 — Navigation

Sidebar:

```text
Home
Books
History
Settings
```

Click:

```text
Home     → /
Books    → /books
History  → /history
Settings → /settings
```

---

## Yêu cầu 5 — Dynamic route

Books:

```text
Book 1
Book 2
Book 3
```

Click Book 2:

```text
/books/2
```

Click Read:

```text
/reader/2/1
```

---

## Yêu cầu 6 — Back

Reader:

```text
/reader/2/1
```

Back:

```text
/books/2
```

Book Detail:

```text
/books/2
```

Back:

```text
/books
```

---

# Deep Dive Challenge

Không dùng:

```python
if page.route == ...
```

trực tiếp trong `main()`.

Mục tiêu:

```text
main.py
    ↓
Router
    ↓
AppShell
    ↓
View
```

và cấu trúc:

```text
novel_reader/
│
├── main.py
│
├── routing/
│   ├── router.py
│   └── routes.py
│
├── layouts/
│   └── app_shell.py
│
└── views/
    ├── home.py
    ├── books.py
    ├── book_detail.py
    ├── reader.py
    ├── history.py
    └── settings.py
```

**Chưa cần database. Chưa cần Model. Chưa cần Repository.**

Mục tiêu duy nhất:

> **Hiểu sâu Navigation → Route → Router → View → AppShell.**

---

# Roadmap sau Buổi 7

```text
Buổi 1  — Flet Architecture
Buổi 2  — Page / Control / Event
Buổi 3  — State / Update
Buổi 4  — Text / Button / TextField / Image
Buổi 5  — Row / Column / Container
Buổi 6  — Responsive Layout
Buổi 7  — Navigation & Routing          ← hiện tại
Buổi 8  — Dialog / SnackBar / BottomSheet
Buổi 9  — Form & Validation
Buổi 10 — Theme & Styling
Buổi 11 — Component Architecture
Buổi 12 — State Management
Buổi 13 — Async UI
Buổi 14 — HTTP/API
Buổi 15 — SQLite
...
```

**Buổi 8** sẽ tập trung vào **Overlay & User Interaction**: `AlertDialog`, `SnackBar`, `BottomSheet`, confirmation dialog, loading dialog, error dialog và cách xây một **Dialog Manager** để tránh việc mỗi View tự quản lý dialog riêng lẻ.
