aaa

```
comic_crawler/
    │
    ├── database/
    │   ├── __init__.py
    │   └── db_manager.py      # Tầng 1: Kết nối DB, chạy SQL thuần
    │
    ├── scrapers/
    │   ├── __init__.py
    │   ├── base_scraper.py    # Tầng 2: Lớp cơ sở (Abstract Class)
    │   ├── source_a.py        # Tầng 2: Cào nguồn A (Ví dụ: TruyenFull)
    │   └── source_b.py        # Tầng 2: Cào nguồn B (Ví dụ: Nettruyen)
    │
    ├── core/
    │   ├── __init__.py
    │   └── crawler_engine.py  # Tầng 2: Điều phối dòng chảy dữ liệu
    │
    ├── main.py                # Tầng 3: Giao diện CLI điều khiển
    └── requirements.txt
```


    