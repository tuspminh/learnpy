Lưu trữ dữ liệu bất đồng bộ là mảnh ghép cuối cùng để hoàn thiện một hệ thống Crawler hiệu năng cao. Nếu bạn dùng các phương thức ghi file/database đồng bộ tiêu chuẩn (như `open().write()` hay `sqlite3`), chương trình sẽ bị "khựng" (blocking) mỗi khi ghi đĩa, làm mất đi lợi thế tốc độ của `asyncio` và `httpx`.

Dưới đây là hướng dẫn chi tiết cách tích hợp **`aiofiles`** (ghi file JSON bất đồng bộ) và **`aiosqlite`** (thao tác cơ sở dữ liệu SQLite bất đồng bộ).

---

## 1. Cài đặt thư viện bổ sung

```bash
pip install aiofiles aiosqlite

```

---

## 2. Cách 1: Ghi dữ liệu vào File JSON bằng `aiofiles`

Thay vì ghi từng dòng gây tốn I/O đĩa, cách tối ưu nhất là gom tất cả dữ liệu thu thập được và ghi bất đồng bộ ra file JSON khi hoàn tất, hoặc dùng định dạng **JSON Lines (`.jsonl`)** để ghi theo từng dòng/bắt đầu stream.

### A. Ghi toàn bộ danh sách ra file `.json` chuẩn

```python
import json
import aiofiles


async def save_to_json(data: list[dict], filename: str = "output.json") -> None:
    """Lưu toàn bộ danh sách dict vào file JSON một cách bất đồng bộ"""
    # chuyển đổi dict thành chuỗi JSON với định dạng đẹp (indent)
    json_content = json.dumps(data, ensure_ascii=False, indent=2)

    # Ghi file bất đồng bộ bằng aiofiles
    async with aiofiles.open(filename, mode="w", encoding="utf-8") as f:
        await f.write(json_content)

    print(f"✅ Đã lưu {len(data)} mục vào file {filename}")

```

### B. Ghi từng dòng theo dạng JSON Lines (`.jsonl`)

*Dạng này cực kỳ thích hợp cho các bài toán cào dữ liệu lớn: vừa cào xong 1 trang là ghi ngay, không sợ mất dữ liệu nếu bị ngắt đột ngột.*

```python
import json
import aiofiles


async def append_to_jsonl(items: list[dict], filename: str = "output.jsonl") -> None:
    """Ghi bổ sung (append) từng item thành từng dòng JSON bất đồng bộ"""
    async with aiofiles.open(filename, mode="a", encoding="utf-8") as f:
        for item in items:
            line = json.dumps(item, ensure_ascii=False) + "\n"
            await f.write(line)

```

---

## 3. Cách 2: Lưu dữ liệu vào Cơ sở dữ liệu SQLite bằng `aiosqlite`

Sử dụng `aiosqlite` giúp bạn thực hiện các câu lệnh SQL (`CREATE TABLE`, `INSERT`, `UPDATE`) hoàn toàn bất đồng bộ mà không nghẽn Event Loop.

### Quản lý kết nối Database (`DatabaseManager`)

Dưới đây là một class trợ lý giúp khởi tạo bảng và chèn hàng loạt (Bulk Insert) dữ liệu siêu nhanh:

```python
from typing import Any, Dict, List
import aiosqlite


class AsyncDatabase:

    def __init__(self, db_path: str = "books.db"):
        self.db_path = db_path

    async def init_db(self) -> None:
        """Khởi tạo bảng cơ sở dữ liệu bất đồng bộ"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    upc TEXT UNIQUE,
                    title TEXT,
                    price TEXT,
                    stock TEXT,
                    url TEXT
                )
            """
            )
            await db.commit()
            print("🗄️  Khởi tạo Cơ sở dữ liệu thành công!")

    async def save_books_bulk(self, books: List[Dict[str, Any]]) -> None:
        """Ghi hàng loạt (Bulk Insert) danh sách sách vào SQLite"""
        if not books:
            return

        # Chuẩn bị dữ liệu dạng tuple
        data_tuples = [
            (
                b.get("upc"),
                b.get("title"),
                b.get("price"),
                b.get("stock"),
                b.get("url"),
            )
            for b in books
        ]

        query = """
            INSERT OR REPLACE INTO books (upc, title, price, stock, url)
            VALUES (?, ?, ?, ?, ?)
        """

        async with aiosqlite.connect(self.db_path) as db:
            # executemany giúp chèn hàng trăm bản ghi trong 1 transaction duy nhất
            await db.executemany(query, data_tuples)
            await db.commit()

        print(f"💾 Đã lưu thành công {len(books)} bản ghi vào SQLite!")

```

---

## 4. Tích hợp hoàn chỉnh vào Crawler (HTTPX + Selectolax + SQLite/JSON)

Dưới đây là script ghép nối toàn bộ luồng cào dữ liệu từ `httpx` + `selectolax` rồi lưu song song vào cả file **JSON** lẫn **SQLite**.

```python
import asyncio
from typing import Any, Dict, List
import aiofiles
import aiosqlite
import httpx
from selectolax.lexbor import LexborHTMLParser

# ------------------------------------------------------------------------------
# 1. DATABASE & STORAGE HELPERS
# ------------------------------------------------------------------------------


async def init_db(db_path: str):
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                price TEXT,
                url TEXT UNIQUE
            )
        """
        )
        await db.commit()


async def save_to_sqlite(db_path: str, data: List[Dict[str, Any]]):
    query = "INSERT OR IGNORE INTO books (title, price, url) VALUES (?, ?, ?)"
    records = [(item["title"], item["price"], item["url"]) for item in data]

    async with aiosqlite.connect(db_path) as db:
        await db.executemany(query, records)
        await db.commit()


async def save_to_json(data: List[Dict[str, Any]], filename: str):
    import json

    async with aiofiles.open(filename, mode="w", encoding="utf-8") as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=2))


# ------------------------------------------------------------------------------
# 2. CRAWLER & PARSER
# ------------------------------------------------------------------------------


def parse_page(html: str, url: str) -> List[Dict[str, Any]]:
    tree = LexborHTMLParser(html)
    items = []
    for article in tree.css("article.product_pod"):
        title_node = article.css_first("h3 a")
        price_node = article.css_first("p.price_color")

        items.append(
            {
                "title": (
                    title_node.attributes.get("title") if title_node else None
                ),
                "price": price_node.text(strip=True) if price_node else None,
                "url": url,
            }
        )
    return items


async def fetch_page(
    client: httpx.AsyncClient, semaphore: asyncio.Semaphore, url: str
) -> List[Dict[str, Any]]:
    async with semaphore:
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            return parse_page(resp.text, url)
        except Exception as e:
            print(f"❌ Lỗi {url}: {e}")
            return []


# ------------------------------------------------------------------------------
# 3. MAIN WORKFLOW
# ------------------------------------------------------------------------------


async def main():
    DB_FILE = "books_data.db"
    JSON_FILE = "books_data.json"

    # Khởi tạo bảng Database trước
    await init_db(DB_FILE)

    urls = [
        f"https://books.toscrape.com/catalogue/page-{i}.html" for i in range(1, 4)
    ]
    semaphore = asyncio.Semaphore(5)

    async with httpx.AsyncClient(timeout=10.0) as client:
        print("🚀 Đang cào dữ liệu...")
        tasks = [fetch_page(client, semaphore, url) for url in urls]
        results = await asyncio.gather(*tasks)

        # Gom phẳng danh sách kết quả
        all_books = [book for sublist in results for book in sublist]

    print(f"✅ Thu thập xong {len(all_books)} mục.")

    # Ghi bất đồng bộ song song ra cả SQLite và File JSON bằng asyncio.gather
    print("⏳ Đang lưu dữ liệu bất đồng bộ...")
    await asyncio.gather(
        save_to_sqlite(DB_FILE, all_books), save_to_json(all_books, JSON_FILE)
    )

    print("🎉 TẤT CẢ HOÀN TẤT!")


if __name__ == "__main__":
    asyncio.run(main())

```

---

## 💡 Mẹo hiệu năng (Performance Tips)

1. **Dùng `executemany` thay vì vòng lặp `execute**`:
Khi lưu vào SQLite, gọi `db.executemany()` cùng với danh sách tuples nhanh hơn việc gọi `db.execute()` trong vòng lặp `for` từ **10 đến 50 lần**.
2. **Không lạm dụng `await db.commit()**`:
Mỗi lần `commit()` là một lần ghi cứng xuống đĩa cứng. Chỉ nên `commit()` một lần duy nhất sau khi đã chèn xong toàn bộ lô (batch) dữ liệu.
3. **Thao tác song song với `asyncio.gather()**`:
Như trong ví dụ trên, bạn có thể gọi `await asyncio.gather(save_to_sqlite(...), save_to_json(...))` để tiến hành lưu dữ liệu ra nhiều nơi cùng một lúc mà không phải chờ đợi lẫn nhau.