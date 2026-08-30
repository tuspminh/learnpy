# 📘 Selectolax — Buổi 16: Crawl Website Truyện

Hôm nay chúng ta nâng Mini Crawler thành **Story Crawler**.

Mục tiêu:

```text
URL
 ↓
HTTPX
 ↓
Fetcher
 ↓
Selectolax
 ↓
StoryParser
 ↓
Story
 ├── title
 ├── author
 ├── categories
 └── description
 ↓
SQLite
```

Và quan trọng nhất: **chúng ta bắt đầu thiết kế domain cho crawler truyện**, chuẩn bị cho Pagination, Plugin Parser và Asyncio ở các buổi sau.

---

# 1. Bài toán thực tế

Giả sử website truyện có trang:

```text
https://example.com/story/python
```

HTML:

```html
<article class="story">

    <h1 class="story-title">
        Python Crawler
    </h1>

    <div class="author">
        Garden
    </div>

    <div class="categories">
        <a href="/category/python">
            Python
        </a>

        <a href="/category/programming">
            Programming
        </a>
    </div>

    <div class="description">
        Học xây dựng crawler bằng Python.
    </div>

</article>
```

Chúng ta muốn biến nó thành:

```python
Story(
    title="Python Crawler",
    author="Garden",
    categories=[
        "Python",
        "Programming",
    ],
    description="Học xây dựng crawler bằng Python.",
)
```

---

# 2. Domain Model

Tạo:

```text
app/
├── models.py
├── fetcher.py
├── parser.py
├── story_parser.py
├── repository.py
└── crawler.py
```

`models.py`:

```python
from dataclasses import dataclass, field


@dataclass
class Story:
    title: str
    url: str
    author: str | None = None
    categories: list[str] = field(
        default_factory=list
    )
    description: str | None = None
```

---

# 3. Tại sao `default_factory=list`?

Không nên:

```python
categories: list[str] = []
```

Vì mutable default dễ gây lỗi.

Đúng:

```python
categories: list[str] = field(
    default_factory=list
)
```

Mỗi `Story` có một list riêng:

```python
story1.categories
story2.categories
```

---

# 4. StoryParser

Tạo:

```text
app/story_parser.py
```

```python
from selectolax.parser import HTMLParser

from .models import Story


class StoryParser:

    def parse(
        self,
        tree: HTMLParser,
        url: str,
    ) -> Story:

        title_node = tree.css_first(
            ".story-title"
        )

        if title_node is None:
            raise ValueError(
                "Story title not found"
            )

        author_node = tree.css_first(
            ".author"
        )

        description_node = (
            tree.css_first(
                ".description"
            )
        )

        categories = [
            node.text(strip=True)
            for node in tree.css(
                ".categories a"
            )
            if node.text(strip=True)
        ]

        return Story(
            title=title_node.text(
                strip=True
            ),
            url=url,
            author=(
                author_node.text(
                    strip=True
                )
                if author_node
                else None
            ),
            categories=categories,
            description=(
                description_node.text(
                    strip=True
                )
                if description_node
                else None
            ),
        )
```

---

# 5. Phân tích Selectolax

Đoạn này:

```python
tree.css_first(
    ".story-title"
)
```

lấy:

```html
<h1 class="story-title">
    Python Crawler
</h1>
```

Còn:

```python
tree.css(
    ".categories a"
)
```

lấy **nhiều node**:

```text
a
a
```

Đây là điểm chúng ta đã học ở Buổi 5.

---

# 6. Extract nhiều node

Ví dụ:

```html
<div class="categories">

    <a>Python</a>
    <a>Programming</a>
    <a>Web Scraping</a>

</div>
```

:

```python
nodes = tree.css(
    ".categories a"
)
```

Kết quả là collection các node.

Ta chuyển thành list:

```python
categories = [
    node.text(strip=True)
    for node in nodes
]
```

Kết quả:

```python
[
    "Python",
    "Programming",
    "Web Scraping",
]
```

---

# 7. Story và Chapter là hai Entity khác nhau

Đây là điểm cực kỳ quan trọng.

Không nên:

```python
@dataclass
class Story:
    title: str
    chapters: list[str]
```

ngay từ đầu.

Tốt hơn:

```python
@dataclass
class Story:
    id: int | None
    title: str
    url: str
```

và:

```python
@dataclass
class Chapter:
    id: int | None
    story_id: int
    title: str
    url: str
    content: str
```

Quan hệ:

```text
Story
  │
  ├── Chapter 1
  ├── Chapter 2
  ├── Chapter 3
  └── Chapter 4
```

Đây sẽ cực kỳ hữu ích khi chúng ta xây SQLite.

---

# 8. Model hoàn chỉnh hơn

`models.py`:

```python
from dataclasses import dataclass, field


@dataclass
class Story:
    id: int | None
    title: str
    url: str
    author: str | None = None
    categories: list[str] = field(
        default_factory=list
    )
    description: str | None = None


@dataclass
class Chapter:
    id: int | None
    story_id: int
    title: str
    url: str
    content: str
    number: int | None = None
```

---

# 9. Database Schema

Bây giờ database không còn chỉ có:

```text
articles
```

mà có:

```text
stories
chapters
categories
story_categories
```

Quan hệ:

```text
stories
   │
   │ 1:N
   ▼
chapters
```

và:

```text
stories
   │
   │ N:M
   ▼
categories
```

---

# 10. Tạo bảng Story

```sql
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT NOT NULL,

    url TEXT NOT NULL UNIQUE,

    author TEXT,

    description TEXT
);
```

`url UNIQUE` giúp tránh:

```text
Story A
Story A
Story A
```

---

# 11. Chapter table

```sql
CREATE TABLE IF NOT EXISTS chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    story_id INTEGER NOT NULL,

    title TEXT NOT NULL,

    url TEXT NOT NULL UNIQUE,

    content TEXT NOT NULL,

    number INTEGER,

    FOREIGN KEY (
        story_id
    )
    REFERENCES stories(id)
);
```

---

# 12. Tại sao Chapter có `story_id`?

Database:

```text
stories
id = 1
title = Python Crawler
```

chapters:

```text
id | story_id | title
---+----------+-------------
1  | 1        | Chương 1
2  | 1        | Chương 2
3  | 1        | Chương 3
```

Ta biết:

```text
Chapter 1
    ↓
Story 1
```

---

# 13. Repository

Tạo:

```text
app/repository.py
```

```python
import sqlite3

from .models import Story


class StoryRepository:

    def __init__(
        self,
        connection: sqlite3.Connection,
    ):
        self.connection = connection

    def save(
        self,
        story: Story,
    ) -> int:

        cursor = self.connection.execute(
            """
            INSERT OR IGNORE INTO stories (
                title,
                url,
                author,
                description
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                story.title,
                story.url,
                story.author,
                story.description,
            ),
        )

        self.connection.commit()

        if cursor.lastrowid:
            return cursor.lastrowid

        row = self.connection.execute(
            """
            SELECT id
            FROM stories
            WHERE url = ?
            """,
            (story.url,),
        ).fetchone()

        return row[0]
```

---

# 14. Một vấn đề rất quan trọng

`INSERT OR IGNORE` có behavior:

```text
new story
→ INSERT

existing story
→ IGNORE
```

Nhưng crawler cần **story_id** trong cả hai trường hợp.

Vì vậy:

```python
if cursor.lastrowid:
    return cursor.lastrowid
```

Nếu đã tồn tại:

```sql
SELECT id
FROM stories
WHERE url = ?
```

---

# 15. Đây là Upsert tư duy

Crawler thường xuyên chạy lại.

Ví dụ:

```text
Ngày 1
crawl Story A
```

Ngày 2:

```text
crawl Story A
```

Không muốn:

```text
Story A
Story A
```

Mà muốn:

```text
Story A
 ↓
update nếu cần
```

Đây chính là bài toán **upsert**.

Sau này chúng ta sẽ làm:

```sql
INSERT ...
ON CONFLICT(url)
DO UPDATE SET ...
```

---

# 16. Story crawler

Crawler hiện tại:

```text
URL
 ↓
Fetcher
 ↓
Parser
 ↓
StoryParser
 ↓
StoryRepository
```

Code:

```python
class StoryCrawler:

    def __init__(
        self,
        fetcher,
        parser,
        story_parser,
        repository,
    ):
        self.fetcher = fetcher
        self.parser = parser
        self.story_parser = story_parser
        self.repository = repository

    def crawl_story(
        self,
        url: str,
    ) -> Story:

        html = self.fetcher.fetch(url)

        tree = self.parser.parse(html)

        story = self.story_parser.parse(
            tree,
            url,
        )

        self.repository.save(story)

        return story
```

---

# 17. Luồng hoàn chỉnh

```text
                Story URL
                    │
                    ▼
                 Fetcher
                    │
                    ▼
                  HTTPX
                    │
                    ▼
                   HTML
                    │
                    ▼
              Selectolax
                    │
                    ▼
               StoryParser
                    │
                    ▼
                  Story
                    │
                    ▼
             StoryRepository
                    │
                    ▼
                 SQLite
```

Đây chính là phiên bản đầu tiên của **truyện crawler**.

---

# 18. Nhưng website truyện thực tế phức tạp hơn

Một trang Story thường có:

```text
Story page
│
├── title
├── author
├── category
├── description
│
└── chapter list
      │
      ├── Chapter 1
      ├── Chapter 2
      ├── Chapter 3
      └── ...
```

Vì vậy StoryParser cần lấy cả chapter links.

---

# 19. Chapter Link Model

Có thể tạo:

```python
@dataclass
class ChapterLink:
    title: str
    url: str
    number: int | None = None
```

Sau đó:

```python
@dataclass
class Story:
    id: int | None
    title: str
    url: str

    author: str | None = None

    categories: list[str] = field(
        default_factory=list
    )

    description: str | None = None

    chapters: list[ChapterLink] = field(
        default_factory=list
    )
```

---

# 20. Nhưng có nên lưu Chapter vào Story?

Ở tầng **parser**, có thể.

Ở tầng **database**, không nên nhét toàn bộ chapter vào Story.

Tách:

```text
Story
  │
  └── metadata

Chapter
  │
  └── content
```

Parser có thể tạo:

```text
Story
+
ChapterLink[]
```

Crawler sau đó:

```text
Story
 ↓
save Story
 ↓
ChapterLink[]
 ↓
crawl từng Chapter
```

Đây chính là kiến trúc chúng ta cần ở Buổi 17.

---

# 21. Parse Chapter Links

HTML:

```html
<div class="chapter-list">

    <a href="/chapter/1">
        Chương 1
    </a>

    <a href="/chapter/2">
        Chương 2
    </a>

    <a href="/chapter/3">
        Chương 3
    </a>

</div>
```

Selectolax:

```python
chapter_nodes = tree.css(
    ".chapter-list a"
)
```

Sau đó:

```python
chapters = []

for node in chapter_nodes:

    title = node.text(
        strip=True
    )

    url = node.attributes.get(
        "href"
    )

    if not url:
        continue

    chapters.append(
        ChapterLink(
            title=title,
            url=url,
        )
    )
```

---

# 22. URL tương đối

Đây là vấn đề crawler thực tế.

HTML:

```html
<a href="/chapter/1">
```

Ta nhận:

```text
/chapter/1
```

Nhưng HTTPX cần:

```text
https://example.com/chapter/1
```

Dùng `urllib.parse.urljoin`:

```python
from urllib.parse import urljoin
```

```python
absolute_url = urljoin(
    story_url,
    relative_url,
)
```

Ví dụ:

```python
urljoin(
    "https://example.com/story/python",
    "/chapter/1",
)
```

→

```text
https://example.com/chapter/1
```

---

# 23. Đây là một utility đáng tách riêng

Tạo:

```text
app/url.py
```

```python
from urllib.parse import urljoin


def absolute_url(
    base_url: str,
    url: str,
) -> str:

    return urljoin(
        base_url,
        url,
    )
```

Sau này mọi parser dùng chung.

---

# 24. Defensive extraction

Đừng:

```python
url = node.attributes["href"]
```

vì nếu HTML:

```html
<a>Chapter 1</a>
```

sẽ lỗi.

Tốt:

```python
url = node.attributes.get(
    "href"
)

if not url:
    continue
```

Đây chính là kiến thức Buổi 12 áp dụng vào project.

---

# 25. Parse Chapter number

HTML:

```text
Chương 1
Chương 2
Chương 10
```

Ta có thể lấy:

```python
import re


def parse_chapter_number(
    title: str,
) -> int | None:

    match = re.search(
        r"\d+",
        title,
    )

    if not match:
        return None

    return int(match.group())
```

Ví dụ:

```python
parse_chapter_number(
    "Chương 123"
)
```

→

```text
123
```

---

# 26. Đừng phụ thuộc hoàn toàn vào title

Một số website:

```text
Chương 1
```

Một số:

```text
Chapter 1
```

Một số:

```text
001 - Khởi đầu
```

Một số:

```text
第1章
```

Vì vậy:

```python
r"\d+"
```

chỉ là heuristic.

Parser thực tế nên có khả năng tùy biến theo website.

Đây chính là lý do chúng ta sẽ học:

> **Plugin Parser ở Buổi 18.**

---

# 27. StoryParser version 2

Ví dụ:

```python
class StoryParser:

    def parse(
        self,
        tree,
        url,
    ):

        title = self._extract_title(
            tree
        )

        author = self._extract_author(
            tree
        )

        categories = (
            self._extract_categories(
                tree
            )
        )

        description = (
            self._extract_description(
                tree
            )
        )

        chapters = (
            self._extract_chapters(
                tree,
                url,
            )
        )

        return Story(
            id=None,
            title=title,
            url=url,
            author=author,
            categories=categories,
            description=description,
            chapters=chapters,
        )
```

Đây là hướng tốt hơn so với một method 100 dòng.

---

# 28. Tách extraction methods

```python
def _extract_title(self, tree):
    node = tree.css_first(
        ".story-title"
    )

    if node is None:
        raise ValueError(
            "Story title not found"
        )

    return node.text(strip=True)
```

Author:

```python
def _extract_author(self, tree):

    node = tree.css_first(
        ".author"
    )

    if node is None:
        return None

    return node.text(
        strip=True
    )
```

---

# 29. Categories

```python
def _extract_categories(
    self,
    tree,
):

    return [
        node.text(strip=True)
        for node in tree.css(
            ".categories a"
        )
        if node.text(strip=True)
    ]
```

---

# 30. Chapter links

```python
def _extract_chapters(
    self,
    tree,
    base_url,
):

    chapters = []

    for node in tree.css(
        ".chapter-list a"
    ):

        title = node.text(
            strip=True
        )

        href = node.attributes.get(
            "href"
        )

        if not title or not href:
            continue

        chapters.append(
            ChapterLink(
                title=title,
                url=urljoin(
                    base_url,
                    href,
                ),
                number=(
                    parse_chapter_number(
                        title
                    )
                ),
            )
        )

    return chapters
```

---

# 31. Đây là lúc crawler bắt đầu có domain logic

Chúng ta không còn đơn giản:

```text
CSS Selector
 ↓
text
```

mà có:

```text
HTML
 ↓
Extract
 ↓
Normalize
 ↓
Validate
 ↓
Domain Model
```

Ví dụ:

```text
"  Chương 001  "
        ↓
"Chương 001"
        ↓
number = 1
```

---

# 32. Chapter Parser

Bây giờ giả sử:

```html
<article class="chapter">

    <h1 class="chapter-title">
        Chương 1 - Hello Python
    </h1>

    <div class="chapter-content">

        <p>Hello Python.</p>

        <p>This is chapter one.</p>

    </div>

</article>
```

Parser:

```python
class ChapterParser:

    def parse(
        self,
        tree,
        url,
        story_id,
    ) -> Chapter:

        title_node = tree.css_first(
            ".chapter-title"
        )

        content_node = (
            tree.css_first(
                ".chapter-content"
            )
        )

        if title_node is None:
            raise ValueError(
                "Chapter title not found"
            )

        if content_node is None:
            raise ValueError(
                "Chapter content not found"
            )

        title = title_node.text(
            strip=True
        )

        content = content_node.text(
            separator="\n",
            strip=True,
        )

        return Chapter(
            id=None,
            story_id=story_id,
            title=title,
            url=url,
            content=content,
            number=parse_chapter_number(
                title
            ),
        )
```

---

# 33. Tư duy Domain

Bây giờ ta có:

```text
Story
│
├── metadata
│
└── ChapterLink[]
        │
        ▼
     Chapter
        │
        ├── title
        ├── number
        ├── url
        └── content
```

Đây là mô hình rất gần với hệ thống crawler truyện thực tế.

---

# 34. Story Crawl và Chapter Crawl

Không nên làm:

```python
crawl_story()
    ↓
crawl 1000 chapters
```

trong một method khổng lồ.

Tách:

```python
crawl_story(url)
```

và:

```python
crawl_chapter(
    url,
    story_id,
)
```

Sau này:

```text
crawl_story
     ↓
discover chapters
     ↓
queue chapters
     ↓
workers
     ↓
crawl_chapter
```

Đây chính là nền tảng để kết hợp với **Redis Queue / crawler worker** mà bạn đang học.

---

# 35. Architecture sau Buổi 16

```text
                         Crawler
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
        StoryCrawler                  ChapterCrawler
             │                             │
             ▼                             ▼
        StoryParser                  ChapterParser
             │                             │
             ▼                             ▼
           Story                         Chapter
             │                             │
             └──────────────┬──────────────┘
                            ▼
                       Repository
                            │
                            ▼
                          SQLite
```

---

# 36. Testing

Chúng ta đã học testing ở Buổi 14, nên **không được bỏ qua**.

Tạo:

```text
tests/
├── fixtures/
│   ├── story.html
│   └── chapter.html
│
├── test_story_parser.py
└── test_chapter_parser.py
```

---

# 37. Test Story

```python
def test_parse_story():

    html = load_fixture(
        "story.html"
    )

    tree = HTMLParser(html)

    parser = StoryParser()

    story = parser.parse(
        tree,
        "https://example.com/story/python",
    )

    assert story.title == (
        "Python Crawler"
    )

    assert story.author == (
        "Garden"
    )

    assert story.categories == [
        "Python",
        "Programming",
    ]
```

---

# 38. Test Chapter Links

```python
def test_parse_chapters():

    html = load_fixture(
        "story.html"
    )

    tree = HTMLParser(html)

    parser = StoryParser()

    story = parser.parse(
        tree,
        "https://example.com/story/python",
    )

    assert len(
        story.chapters
    ) == 3

    assert (
        story.chapters[0].title
        == "Chương 1"
    )

    assert (
        story.chapters[0].number
        == 1
    )
```

---

# 39. Test URL normalization

```python
def test_chapter_url():

    ...

    assert (
        story.chapters[0].url
        == "https://example.com/chapter/1"
    )
```

Đây là test rất quan trọng.

---

# 40. Test Chapter

```python
def test_parse_chapter():

    html = load_fixture(
        "chapter.html"
    )

    tree = HTMLParser(html)

    parser = ChapterParser()

    chapter = parser.parse(
        tree,
        "https://example.com/chapter/1",
        story_id=10,
    )

    assert chapter.title == (
        "Chương 1 - Hello Python"
    )

    assert chapter.number == 1

    assert chapter.story_id == 10

    assert (
        "Hello Python."
        in chapter.content
    )
```

---

# 41. Một vấn đề thực tế: thứ tự chapter

Website có thể trả:

```text
Chapter 10
Chapter 1
Chapter 2
Chapter 3
```

Không nên tin thứ tự HTML.

Có thể sort:

```python
chapters.sort(
    key=lambda chapter: (
        chapter.number
        if chapter.number is not None
        else float("inf")
    )
)
```

Kết quả:

```text
1
2
3
10
```

---

# 42. Nhưng cũng đừng luôn sort

Có website:

```text
Prologue
Chapter 1
Chapter 2
Extra
Chapter 3
```

Nếu sort bằng number:

```text
Chapter 1
Chapter 2
Chapter 3
Prologue
Extra
```

có thể không đúng ý website.

Vì vậy tốt hơn là lưu:

```text
source_order
```

hoặc để parser/site plugin quyết định.

Đây là một vấn đề sẽ trở nên quan trọng ở **Plugin Parser**.

---

# 43. Database Repository cho Chapter

```python
class ChapterRepository:

    def __init__(self, connection):
        self.connection = connection

    def save(
        self,
        chapter: Chapter,
    ) -> int:

        cursor = self.connection.execute(
            """
            INSERT OR IGNORE INTO chapters (
                story_id,
                title,
                url,
                content,
                number
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                chapter.story_id,
                chapter.title,
                chapter.url,
                chapter.content,
                chapter.number,
            ),
        )

        self.connection.commit()

        if cursor.lastrowid:
            return cursor.lastrowid

        row = self.connection.execute(
            """
            SELECT id
            FROM chapters
            WHERE url = ?
            """,
            (chapter.url,),
        ).fetchone()

        return row[0]
```

---

# 44. Một điểm rất đáng chú ý

Tại sao:

```text
Chapter.url UNIQUE
```

thay vì:

```text
story_id + title UNIQUE
```

Bởi vì URL thường là identity tốt hơn:

```text
https://example.com/chapter/123
```

Nếu title đổi:

```text
Chương 123
```

→

```text
Chương 123 - Updated
```

thì vẫn là cùng chapter.

---

# 45. Crawler lifecycle

Story crawler:

```text
START
  │
  ▼
Fetch story
  │
  ▼
Parse story
  │
  ▼
Save story
  │
  ▼
Discover chapters
  │
  ▼
Return chapter URLs
```

Chưa crawl chapter hàng loạt.

Buổi 17 chúng ta sẽ làm:

```text
Story
 ↓
Chapter URLs
 ↓
Pagination
 ↓
Many chapters
 ↓
Crawl
 ↓
Save
```

---

# 46. Những gì chúng ta chưa làm

Hôm nay **chưa** làm:

```text
❌ Asyncio
❌ Concurrent requests
❌ Retry
❌ Rate limiter
❌ Queue
❌ Plugin
❌ Pagination engine
```

Lý do rất rõ:

Chúng ta trước tiên cần mô hình hóa:

```text
Story
Chapter
```

Nếu domain model sai, async hóa chỉ làm cái sai chạy nhanh hơn.

---

# 47. Project structure tốt hơn

Sau Buổi 16:

```text
mini_crawler/
│
├── app/
│   │
│   ├── models.py
│   │
│   ├── fetcher.py
│   │
│   ├── parser.py
│   │
│   ├── story_parser.py
│   │
│   ├── chapter_parser.py
│   │
│   ├── repository.py
│   │
│   ├── crawler.py
│   │
│   └── url.py
│
├── tests/
│   │
│   ├── fixtures/
│   │   ├── story.html
│   │   └── chapter.html
│   │
│   ├── test_story_parser.py
│   └── test_chapter_parser.py
│
├── main.py
│
└── crawler.db
```

---

# 🎯 Bài tập Buổi 16

## Bài 1 — Story

Tự tạo fixture:

```text
story.html
```

có:

```text
title
author
categories
description
```

Parser phải trả:

```python
Story(...)
```

---

## Bài 2 — Chapter links

Thêm:

```html
<div class="chapter-list">
    ...
</div>
```

Parser lấy được:

```python
list[ChapterLink]
```

---

## Bài 3 — URL

Hỗ trợ:

```text
/chapter/1
chapter/1
https://example.com/chapter/1
```

đều thành URL tuyệt đối.

---

## Bài 4 — Chapter Parser

Tạo:

```text
chapter.html
```

và extract:

```text
title
content
number
```

---

## Bài 5 — SQLite

Tạo:

```text
stories
chapters
```

và:

```text
StoryRepository
ChapterRepository
```

Test:

```text
save story
save chapter
query story
query chapters
```

---

# 🧠 Bài tập kiến trúc — quan trọng nhất

Hãy thử tự vẽ:

```text
StoryCrawler
      │
      ▼
StoryParser
      │
      ▼
Story
      │
      ├──────────────┐
      ▼              ▼
Repository     ChapterLink[]
                       │
                       ▼
                 ChapterCrawler
                       │
                       ▼
                 ChapterParser
                       │
                       ▼
                    Chapter
                       │
                       ▼
                  Repository
```

Nếu bạn hiểu được sơ đồ này thì **Buổi 17 sẽ rất quan trọng**, vì chúng ta sẽ biến:

```text
ChapterLink[]
```

thành một **crawl pipeline thực sự**:

```text
Story URL
   ↓
Story
   ↓
Chapter links
   ↓
Pagination
   ↓
Deduplicate URLs
   ↓
Crawl nhiều chapter
   ↓
ChapterParser
   ↓
SQLite
```

Và từ đó chúng ta sẽ có nền móng rất tốt để sang **Buổi 18 — Plugin Parser**, nơi một `Crawler` có thể chạy được nhiều website truyện khác nhau mà không phải sửa core crawler.
