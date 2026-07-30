# Bài 1

# Phân tích website

Một lập trình viên crawler **không viết code ngay**.

Bước đầu tiên luôn là:

> Phân tích website.

Ví dụ:

```text-x-trilium-auto
https://truyenfull.vn
```

Ta cần trả lời:

Website gồm những loại trang nào?

Ví dụ:

```text-x-trilium-auto
Trang chủ
↓

Danh sách truyện
↓

Trang truyện
↓

Danh sách chapter

↓

Trang chapter
```

Tức là có 4 loại page.

```text-x-trilium-auto
Home

Category

Novel

Chapter
```

---

## 1. Trang danh sách

Ví dụ

```text-x-trilium-auto
https://truyenfull.vn/danh-sach/truyen-moi/
```

Trang này chứa

```text-x-trilium-auto
Tên

Ảnh

Tác giả

URL

Thể loại

Trạng thái
```

Ví dụ HTML thường có dạng

```text-x-trilium-auto
<div class="row">
    <h3>
        <a href="/than-dao-dan-ton/">
            Thần Đạo Đan Tôn
        </a>
    </h3>

    <span class="author">
        Cô Đơn Địa Phi
    </span> </div>
```

Ta cần lấy

```text-x-trilium-auto
title

url

author
```

---

## 2. Trang truyện

Ví dụ

```text-x-trilium-auto
https://truyenfull.vn/than-dao-dan-ton/
```

Trang này chứa

```text-x-trilium-auto
Tên

Ảnh

Mô tả

Tác giả

Nguồn

Thể loại

Trạng thái

Danh sách chương
```

Ví dụ

```text-x-trilium-auto
<h3 class="title">
Thần Đạo Đan Tôn
</h3>
```

---

Có

```text-x-trilium-auto
<div class="desc-text">
```

chứa mô tả.

---

Có

```text-x-trilium-auto
<img class="book">
```

chứa ảnh.

---

Có

```text-x-trilium-auto
<a href="/the-loai/tien-hiep/">
Tiên Hiệp
</a>
```

chứa thể loại.

---

## 3. Danh sách chapter

Ví dụ

```text-x-trilium-auto
https://truyenfull.vn/than-dao-dan-ton/trang-2/
```

Có

```text-x-trilium-auto
<ul>

<li>

<a href="..."> 
```

Mỗi dòng là

```text-x-trilium-auto
chapter

url
```

---

## 4. Trang chapter

Ví dụ

```text-x-trilium-auto
https://truyenfull.vn/than-dao-dan-ton/chuong-120/
```

Có

```text-x-trilium-auto
Tiêu đề

Nội dung
```

Ví dụ

```text-x-trilium-auto
<div class="chapter-c">
```

Toàn bộ nội dung nằm trong đây.

---

# Từ đó ta xác định được plugin cần có những chức năng gì

Plugin cần biết cách:

```text-x-trilium-auto
download page

↓

parse novel list

↓

parse novel

↓

parse chapter list

↓

parse chapter
```

Hay dưới dạng các hàm:

```text-x-trilium-auto
fetch_novel_list()

fetch_novel()

fetch_chapter_list()

fetch_chapter()
```

Đây chính là **trách nhiệm (responsibility)** của plugin. Plugin chỉ lo lấy và phân tích dữ liệu từ website, không quan tâm đến việc lưu cơ sở dữ liệu hay giao diện.

---

# Kiến trúc plugin TruyenFull

```text-x-trilium-auto
plugins/
└── truyenfull/
    ├── __init__.py
    ├── source.py          # Điều phối các thao tác crawl
    ├── parser.py          # Phân tích HTML
    ├── urls.py            # Khai báo URL và tạo URL
    ├── selectors.py       # CSS Selector/XPath tập trung
    ├── models.py          # DTO riêng của plugin (nếu cần)
    ├── normalizer.py      # Chuẩn hóa dữ liệu (tên, trạng thái...)
    └── tests/
        ├── test_parser.py
        └── samples/
```

Tách riêng `urls.py`, `selectors.py` và `normalizer.py` giúp việc sửa plugin khi website thay đổi dễ dàng hơn, thay vì phải tìm và sửa nhiều chỗ trong mã nguồn.

---

# Kết quả của Bài 1

Sau bài này, bạn cần hiểu rõ:

- Cách phân tích một website trước khi viết crawler.
- Xác định các loại trang và dữ liệu cần lấy.
- Xác định rõ trách nhiệm của plugin.
- Thiết kế cấu trúc thư mục cho plugin theo hướng dễ bảo trì và mở rộng.

---

Ở **Bài 2**, chúng ta sẽ phân tích **toàn bộ URL của TruyenFull**, xây dựng `urls.py`, hiểu cách phân trang, tạo URL động và thiết kế các hàm sinh URL để plugin không cần ghép chuỗi thủ công ở nhiều nơi. Đây là nền tảng quan trọng trước khi bắt đầu viết `TruyenFullSource`.