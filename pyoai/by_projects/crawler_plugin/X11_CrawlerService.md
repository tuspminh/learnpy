Rất tốt. Chúng ta đã có:

```text-x-trilium-auto
HttpClient
      |
      v
Parser
      |
      v
Models
      |
      v
Source
```

Nhưng hiện tại hệ thống vẫn **chưa phải một crawler hoàn chỉnh**.

Vấn đề:

`TruyenFullSource` chỉ biết:

- tải một trang
- parse một trang

Nó chưa biết:

- crawl toàn bộ truyện
- crawl hàng nghìn chương
- lưu trạng thái
- retry lỗi
- pause
- resume
- báo tiến trình cho Dashboard

Vì vậy chúng ta cần thêm một tầng mới.

---

# Bài 11 - Xây dựng `CrawlerService`

## Mục tiêu

Sau bài này kiến trúc sẽ thành:

```text-x-trilium-auto
              Dashboard PySide6

                    |
                    v

             CrawlerService

                    |
        +-----------+-----------+

        |                       |

TruyenFullSource          Repository

        |

 HttpClient + Parser
```

---

# 1. Vì sao cần Service?

Sai thiết kế:

```text-x-trilium-auto
button_click():

    source.fetch_novel()

    source.fetch_chapters()

    db.save()
```

Dashboard đang làm quá nhiều việc.

GUI không nên biết:

- crawler chạy thế nào
- database ra sao
- retry thế nào

---

Đúng:

```text-x-trilium-auto
button_click():

    crawler_service.sync_novel(id)
```

---

# 2. Trách nhiệm của Service

`CrawlerService` sẽ quản lý:

## Crawl flow

```text-x-trilium-auto
Novel

 |

Chapter list

 |

Chapter content

 |

Save DB
```

---

## Error handling

Ví dụ:

```text-x-trilium-auto
Chapter 100

download lỗi

retry 3 lần

vẫn lỗi

đánh dấu failed
```

---

## Progress

Ví dụ Dashboard nhận:

```text-x-trilium-auto
Đang tải:

Truyện: Thần Đạo Đan Tôn

Chương:

120 / 500
```

---

# 3. Cấu trúc thư mục

Thêm:

```text-x-trilium-auto
crawler/

    services/

        crawler_service.py
```

---

# 4. Base Service

Không nhất thiết phải có BaseService.

Service thường là lớp nghiệp vụ.

Tạo:

```text-x-trilium-auto
class CrawlerService:
    pass
```

---

# 5. Dependency Injection

Không tạo bên trong:

Sai:

```text-x-trilium-auto
class CrawlerService:

    def __init__(self):

        self.db = SQLite()
        self.source = TruyenFullSource()
```

Vì:

- khó test
- phụ thuộc cứng

---

Đúng:

```text-x-trilium-auto
class CrawlerService:

    def __init__(
        self,
        source,
        repository
    ):
        self.source = source
        self.repository = repository
```

---

# 6. Hàm đồng bộ truyện

Tên:

```text-x-trilium-auto
sync_novel()
```

Nhiệm vụ:

```text-x-trilium-auto
URL

↓

Novel

↓

Save DB
```

---

Code:

```text-x-trilium-auto
def sync_novel(self, url):

    novel = self.source.fetch_novel(url)

    self.repository.save_novel(
        novel
    )

    return novel
```

---

# 7. Đồng bộ danh sách chương

Sau khi có truyện:

```text-x-trilium-auto
Novel

↓

Chapter list
```

---

Code:

```text-x-trilium-auto
def sync_chapters(
    self,
    novel
):

    chapters = self.source.fetch_chapter_list(
        novel.source_id,
        novel.url
    )

    for chapter in chapters:

        self.repository.save_chapter(
            chapter
        )
```

---

# 8. Đồng bộ nội dung chương

Đây là phần nặng.

Ví dụ:

```text-x-trilium-auto
Truyện:

500 chương
```

Ta không tải một lúc.

Mỗi chapter:

```text-x-trilium-auto
def sync_chapter(
    self,
    chapter
):

    data = self.source.fetch_chapter(
        chapter.novel_id,
        chapter.url
    )


    self.repository.save_content(
        data
    )
```

---

# 9. Sync toàn bộ truyện

Bây giờ ghép lại.

```text-x-trilium-auto
def sync_full_novel(
    self,
    url
):

    novel = self.sync_novel(url)


    chapters = self.sync_chapters(
        novel
    )


    for chapter in chapters:

        self.sync_chapter(
            chapter
        )
```

---

Luồng:

```text-x-trilium-auto
sync_full_novel()

        |
        |
        +--> sync_novel()

        |
        |
        +--> sync_chapters()

        |
        |
        +--> sync_chapter()
```

---

# 10. Nhưng có vấn đề

Một truyện 3000 chương.

Nếu:

```text-x-trilium-auto
for chapter in chapters:

    download()
```

thì:

- mất nhiều giờ
- lỗi giữa chừng mất hết
- không pause được

---

Cần thêm:

```text-x-trilium-auto
Task Manager
```

Đây là phần sau.

---

# 11. Thêm Progress Callback

Service không biết PySide6.

Không import:

```text-x-trilium-auto
from PySide6 import *
```

Sai.

---

Thay vào đó:

```text-x-trilium-auto
def sync_chapter(
    self,
    chapter,
    progress=None
):
```

---

Trong vòng lặp:

```text-x-trilium-auto
if progress:

    progress(
        current,
        total
    )
```

---

Dashboard:

```text-x-trilium-auto
service.sync_full_novel(
    url,
    progress=update_ui
)
```

---

# 12. Error Handling

Ví dụ:

```text-x-trilium-auto
try:

    chapter = self.source.fetch_chapter(...)

except Exception as e:

    self.repository.mark_failed(
        chapter,
        str(e)
    )
```

Không làm chết toàn bộ crawler.

---

# 13. Retry

Tạo helper:

```text-x-trilium-auto
def retry(
    func,
    times=3
):

    for i in range(times):

        try:
            return func()

        except:

            if i == times-1:
                raise
```

---

Dùng:

```text-x-trilium-auto
chapter = retry(
    lambda:
    self.source.fetch_chapter(...)
)
```

---

# 14. Kiến trúc sau bài 11

```text-x-trilium-auto
app/

├── base/

│
├── plugins/

│   └── truyenfull/

│
├── services/

│   └── crawler_service.py

│
├── repositories/

│
├── models/

│
└── database/
```

---

# 15. Luồng thực tế

Ví dụ người dùng bấm:

```text-x-trilium-auto
Cào truyện
```

PySide6 gọi:

```text-x-trilium-auto
crawler.sync_full_novel(url)
```

Service:

```text-x-trilium-auto
fetch novel

↓

save novel

↓

fetch chapters

↓

save chapters

↓

download chapter

↓

save content

↓

update progress
```

---

# 16. Bài tập

Tự viết:

```text-x-trilium-auto
class CrawlerService:

    def sync_novel()

    def sync_chapters()

    def sync_chapter()

    def sync_full_novel()
```

Không dùng:

```text-x-trilium-auto
requests

sqlite

PySide6
```

trong Service.

Service chỉ điều phối.

---

# Tổng kết bài 11

Bạn đã học được:

✅ Vai trò của Service Layer  
✅ Tách GUI khỏi logic crawler  
✅ Dependency Injection  
✅ Điều phối Source + Repository  
✅ Progress callback  
✅ Retry cơ bản  
✅ Chuẩn bị kiến trúc cho Pause/Resume

---

# Bài 12 tiếp theo: Repository + SQLite

Chúng ta sẽ xây dựng tầng lưu dữ liệu:

```text-x-trilium-auto
CrawlerService

        |

        v

Repository

        |

        v

SQLite
```

Bao gồm:

- `NovelRepository`
- `ChapterRepository`
- Thiết kế bảng SQLite:
  - novels
  - chapters
  - crawl_tasks
  - crawl_logs
- Insert/update tránh trùng dữ liệu
- Resume crawl khi tắt chương trình

Đây là bước biến crawler thành **một hệ thống quản lý truyện thật sự**, không còn là script cào dữ liệu nữa.