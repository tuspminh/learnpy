# Bài 2 - Phân tích URL và xây dựng `urls.py`

## Mục tiêu

Sau bài này bạn sẽ biết:

- Cấu trúc URL của TruyenFull
- Cách sinh URL bằng code thay vì nối chuỗi
- Thiết kế `urls.py`
- Vì sao mọi plugin crawler đều nên có module URL riêng

---

# 1. Vì sao cần `urls.py`?

Người mới thường viết như sau:

```text-x-trilium-auto
url = "https://truyenfull.vn"

page = 5

html = client.get(url + "/danh-sach/truyen-moi/trang-" + str(page))
```

hoặc

```text-x-trilium-auto
chapter = 150

url = f"https://truyenfull.vn/than-dao-dan-ton/chuong-{chapter}/"
```

Ban đầu có vẻ ổn.

Nhưng sau này website đổi thành

```text-x-trilium-auto
/chuong/150/
```

hoặc

```text-x-trilium-auto
chapter-150.html
```

thì bạn phải sửa ở rất nhiều nơi.

Đó là lý do URL nên tập trung vào một chỗ.

---

# 2. Thiết kế

```text-x-trilium-auto
plugins/

    truyenfull/

        urls.py
```

Đây là nơi duy nhất biết:

- Base URL
- URL danh sách
- URL truyện
- URL chapter
- URL tìm kiếm
- URL phân trang

Các file khác chỉ gọi hàm.

---

# 3. Các URL của TruyenFull

Ví dụ:

```text-x-trilium-auto
https://truyenfull.vn
```

là Base URL.

---

Danh sách truyện mới

```text-x-trilium-auto
https://truyenfull.vn/danh-sach/truyen-moi/
```

---

Trang 2

```text-x-trilium-auto
https://truyenfull.vn/danh-sach/truyen-moi/trang-2/
```

---

Truyện

```text-x-trilium-auto
https://truyenfull.vn/than-dao-dan-ton/
```

---

Chapter

```text-x-trilium-auto
https://truyenfull.vn/than-dao-dan-ton/chuong-100/
```

---

Danh sách chapter trang 3

```text-x-trilium-auto
https://truyenfull.vn/than-dao-dan-ton/trang-3/
```

---

Thể loại

```text-x-trilium-auto
https://truyenfull.vn/the-loai/tien-hiep/
```

---

Tác giả

```text-x-trilium-auto
https://truyenfull.vn/tac-gia/co-doc-dia-phi/
```

---

Hoàn thành

```text-x-trilium-auto
https://truyenfull.vn/danh-sach/hoan/
```

---

Đang ra

```text-x-trilium-auto
https://truyenfull.vn/danh-sach/dang-ra/
```

---

# 4. Quan sát quy luật

Ví dụ

Trang 1

```text-x-trilium-auto
/danh-sach/truyen-moi/
```

Trang 2

```text-x-trilium-auto
/danh-sach/truyen-moi/trang-2/
```

Trang 3

```text-x-trilium-auto
/danh-sach/truyen-moi/trang-3/
```

Có thể viết thành

```text-x-trilium-auto
page == 1

↓

/danh-sach/truyen-moi/

page >1

↓

/danh-sach/truyen-moi/trang-{page}/
```

Đây chính là **rule**.

Crawler luôn hoạt động dựa trên các rule như vậy.

---

# 5. Thiết kế `urls.py`

Ta không viết hằng số rời rạc.

Thay vào đó tạo một class.

```text-x-trilium-auto
class TruyenFullUrls:
    BASE = "https://truyenfull.vn"
```

Sau này plugin chỉ cần

```text-x-trilium-auto
urls = TruyenFullUrls()
```

---

# 6. URL danh sách

Thay vì

```text-x-trilium-auto
url = BASE + "/danh-sach/truyen-moi/"
```

ta viết

```text-x-trilium-auto
class TruyenFullUrls:

    BASE = "https://truyenfull.vn"

    @classmethod
    def newest(cls):

        return cls.BASE + "/danh-sach/truyen-moi/"
```

Sau này

```text-x-trilium-auto
url = TruyenFullUrls.newest()
```

rất rõ nghĩa.

---

# 7. URL phân trang

Đây là phần quan trọng nhất.

```text-x-trilium-auto
@classmethod def newest_page(cls, page):

    if page == 1:
        return cls.newest()

    return f"{cls.BASE}/danh-sach/truyen-moi/trang-{page}/"
```

Sử dụng

```text-x-trilium-auto
TruyenFullUrls.newest_page(1)

↓

https://truyenfull.vn/danh-sach/truyen-moi/
```

```text-x-trilium-auto
TruyenFullUrls.newest_page(5)

↓

https://truyenfull.vn/danh-sach/truyen-moi/trang-5/
```

Không cần if ở nơi khác nữa.

---

# 8. URL truyện

Giả sử slug

```text-x-trilium-auto
than-dao-dan-ton
```

Ta sinh URL

```text-x-trilium-auto
@classmethod def novel(cls, slug):

    return f"{cls.BASE}/{slug}/"
```

Ví dụ

```text-x-trilium-auto
TruyenFullUrls.novel(
    "than-dao-dan-ton"
)
```

↓

```text-x-trilium-auto
https://truyenfull.vn/than-dao-dan-ton/
```

---

# 9. URL chapter

```text-x-trilium-auto
@classmethod def chapter(cls, slug, chapter_slug):

    return f"{cls.BASE}/{slug}/{chapter_slug}/"
```

Ví dụ

```text-x-trilium-auto
chapter(
    "than-dao-dan-ton",
    "chuong-15"
)
```

↓

```text-x-trilium-auto
https://truyenfull.vn/than-dao-dan-ton/chuong-15/
```

---

# 10. URL danh sách chapter

```text-x-trilium-auto
@classmethod def chapter_page(cls, slug, page):

    if page == 1:
        return cls.novel(slug)

    return f"{cls.BASE}/{slug}/trang-{page}/"
```

Ví dụ

```text-x-trilium-auto
page=1

↓

https://truyenfull.vn/than-dao-dan-ton/
```

```text-x-trilium-auto
page=3

↓

https://truyenfull.vn/than-dao-dan-ton/trang-3/
```

---

# 11. Không nên dùng nối chuỗi thủ công

Không nên

```text-x-trilium-auto
url = BASE + "/" + slug + "/"
```

Vì:

- Khó đọc
- Dễ sai dấu `/`
- Khó bảo trì

Hãy luôn dùng f-string hoặc `urllib.parse.urljoin` khi ghép URL có thể thay đổi.

---

# 12. Hoàn chỉnh `urls.py`

```text-x-trilium-auto
class TruyenFullUrls:
    BASE = "https://truyenfull.vn"

    @classmethod
    def newest(cls):
        return f"{cls.BASE}/danh-sach/truyen-moi/"

    @classmethod
    def newest_page(cls, page: int):
        if page <= 1:
            return cls.newest()
        return f"{cls.BASE}/danh-sach/truyen-moi/trang-{page}/"

    @classmethod
    def novel(cls, slug: str):
        return f"{cls.BASE}/{slug}/"

    @classmethod
    def chapter(cls, slug: str, chapter_slug: str):
        return f"{cls.BASE}/{slug}/{chapter_slug}/"

    @classmethod
    def chapter_page(cls, slug: str, page: int):
        if page <= 1:
            return cls.novel(slug)
        return f"{cls.BASE}/{slug}/trang-{page}/"

    @classmethod
    def category(cls, slug: str, page: int = 1):
        if page <= 1:
            return f"{cls.BASE}/the-loai/{slug}/"
        return f"{cls.BASE}/the-loai/{slug}/trang-{page}/"

    @classmethod
    def author(cls, slug: str, page: int = 1):
        if page <= 1:
            return f"{cls.BASE}/tac-gia/{slug}/"
        return f"{cls.BASE}/tac-gia/{slug}/trang-{page}/"
```

---

# 13. Chuẩn bị cho tương lai

Hiện tại plugin chỉ hỗ trợ TruyenFull.

Sau này bạn sẽ có:

```text-x-trilium-auto
plugins/

    truyenfull/
        urls.py

    metruyen/
        urls.py

    tangthuvien/
        urls.py

    bachngocsach/
        urls.py
```

Mỗi plugin tự quản lý URL của mình. `BaseSource` không cần biết chi tiết URL của từng website.

---

# Bài tập

1. Thêm phương thức `completed(page)` để tạo URL cho danh sách truyện đã hoàn thành.
2. Thêm phương thức `ongoing(page)` để tạo URL cho danh sách truyện đang ra.
3. Thêm phương thức `full_url(path)` nhận vào đường dẫn tương đối như `/than-dao-dan-ton/` hoặc `than-dao-dan-ton/` và trả về URL đầy đủ. Gợi ý: dùng `urllib.parse.urljoin` để xử lý chính xác các trường hợp có hoặc không có dấu `/`.

---

## Kiến thức rút ra

Sau bài này bạn đã hiểu:

- Tại sao nên tách riêng module quản lý URL.
- Cách nhận diện và tổng quát hóa quy luật URL của một website.
- Cách xây dựng các hàm sinh URL thay vì nối chuỗi thủ công.
- Cách thiết kế `urls.py` để dễ mở rộng khi thêm nhiều plugin nguồn truyện khác.

Ở **Bài 3**, chúng ta sẽ xây dựng `**selectors.py**`, học cách phân tích HTML bằng CSS Selector, tổ chức các selector tập trung và chuẩn bị nền tảng để viết `parser.py` một cách sạch sẽ và dễ bảo trì. Đây là bước quan trọng trước khi bắt đầu trích xuất dữ liệu từ HTML.