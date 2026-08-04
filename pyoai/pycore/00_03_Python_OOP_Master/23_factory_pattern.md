# Python OOP Master – Buổi 23

# Factory Pattern – Tạo đối tượng một cách linh hoạt

> Factory Pattern là một trong những Design Pattern được sử dụng nhiều nhất trong Python.
>
> Gần như mọi framework lớn đều sử dụng Factory ở đâu đó:
>
> * SQLAlchemy
> * Django ORM
> * logging
> * pathlib
> * requests
> * sqlite3 wrapper
> * Plugin System
>
> Sau buổi này bạn sẽ hiểu vì sao Factory lại là nền tảng của những framework chuyên nghiệp.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu Factory Pattern là gì.
* Biết khi nào nên dùng Factory.
* Phân biệt Factory với `if...elif...else`.
* Xây dựng Simple Factory.
* Xây dựng Factory Method.
* Áp dụng vào framework cào truyện.

---

# 1. Vấn đề

Giả sử có nhiều loại crawler:

```text
TruyenFullCrawler
TangThuVienCrawler
WikiDichCrawler
NovelBinCrawler
```

Nếu viết:

```python
if source == "truyenfull":
    crawler = TruyenFullCrawler()
elif source == "wikidich":
    crawler = WikiDichCrawler()
elif source == "novelbin":
    crawler = NovelBinCrawler()
```

Có vấn đề gì?

* Code dài.
* Khó mở rộng.
* Mỗi lần thêm crawler phải sửa lại khối `if`.

Đây là dấu hiệu nên dùng **Factory Pattern**.

---

# 2. Factory Pattern là gì?

Factory là một đối tượng hoặc phương thức có nhiệm vụ **tạo object**.

Thay vì:

```python
crawler = TruyenFullCrawler()
```

Ta viết:

```python
crawler = CrawlerFactory.create("truyenfull")
```

Người dùng **không cần biết** object được tạo như thế nào.

---

# 3. Ví dụ đầu tiên

```python
class Dog:
    def speak(self):
        print("Gâu")


class Cat:
    def speak(self):
        print("Meo")


class AnimalFactory:
    @staticmethod
    def create(kind):

        if kind == "dog":
            return Dog()

        if kind == "cat":
            return Cat()

        raise ValueError("Unknown animal")
```

Sử dụng

```python
animal = AnimalFactory.create("dog")

animal.speak()
```

↓

```text
Gâu
```

---

# 4. Lợi ích

Code client

```python
animal = AnimalFactory.create(kind)
```

Không cần biết

```python
Dog()

Cat()

Bird()
```

được tạo ra như thế nào.

---

# 5. Factory + Polymorphism

```python
class Animal:
    def speak(self):
        raise NotImplementedError
```

```python
class Dog(Animal):
    def speak(self):
        print("Gâu")
```

```python
class Cat(Animal):
    def speak(self):
        print("Meo")
```

Factory

```python
animal = AnimalFactory.create(kind)

animal.speak()
```

Không quan tâm object thật là gì.

---

# 6. Không cần `if` dài

Thay vì

```python
if kind == ...
elif kind == ...
elif kind == ...
```

Ta dùng dictionary.

```python
class AnimalFactory:
    _mapping = {
        "dog": Dog,
        "cat": Cat,
    }

    @classmethod
    def create(cls, kind):

        try:
            return cls._mapping[kind]()
        except KeyError:
            raise ValueError(f"Unknown animal: {kind}")
```

Đây là cách chuyên nghiệp hơn.

---

# 7. Đăng ký động (Registration)

Có thể cho phép đăng ký class mới:

```python
class AnimalFactory:
    _mapping = {}

    @classmethod
    def register(cls, name, animal_cls):

        cls._mapping[name] = animal_cls

    @classmethod
    def create(cls, name):

        return cls._mapping[name]()
```

Sử dụng

```python
AnimalFactory.register("dog", Dog)
AnimalFactory.register("cat", Cat)

animal = AnimalFactory.create("cat")
```

---

# 8. Factory trong framework cào truyện

```python
class BaseCrawler:
    def fetch(self, url):
        raise NotImplementedError
```

```python
class TruyenFullCrawler(BaseCrawler): ...
```

```python
class WikiDichCrawler(BaseCrawler): ...
```

Factory

```python
class CrawlerFactory:
    _mapping = {
        "truyenfull": TruyenFullCrawler,
        "wikidich": WikiDichCrawler,
    }

    @classmethod
    def create(cls, source):

        try:
            return cls._mapping[source]()
        except KeyError:
            raise ValueError(f"Unsupported source: {source}")
```

Sử dụng

```python
crawler = CrawlerFactory.create("wikidich")
```

---

# 9. Factory cho Parser

```python
class ParserFactory:
    _mapping = {
        "html": HtmlParser,
        "json": JsonParser,
        "xml": XmlParser,
    }

    @classmethod
    def create(cls, parser_type):

        return cls._mapping[parser_type]()
```

---

# 10. Factory cho Database

```python
class SQLiteDatabase: ...
```

```python
class MySQLDatabase: ...
```

```python
class PostgreSQLDatabase: ...
```

Factory

```python
db = DatabaseFactory.create("sqlite")
```

Sau này đổi sang PostgreSQL:

```python
db = DatabaseFactory.create("postgres")
```

Không cần sửa code client.

---

# 11. Factory + Plugin

Giả sử mỗi plugin tự đăng ký:

```python
CrawlerFactory.register("novelbin", NovelBinCrawler)
```

Main program

```python
crawler = CrawlerFactory.create(source)
```

Không cần sửa Factory khi thêm plugin mới.

Đây là nền tảng của **Plugin Architecture**.

---

# 12. Factory Method bằng `@classmethod`

Ngoài việc có lớp Factory riêng, đôi khi chính class cũng có thể đóng vai trò factory.

```python
class Book:
    def __init__(self, title):
        self.title = title

    @classmethod
    def create_default(cls):

        return cls("Unknown")
```

Sử dụng

```python
book = Book.create_default()
```

---

# 13. Ví dụ hoàn chỉnh

```python
class BaseStorage:
    def save(self, text):
        raise NotImplementedError


class FileStorage(BaseStorage):
    def save(self, text):
        print(f"Lưu file: {text}")


class MemoryStorage(BaseStorage):
    def save(self, text):
        print(f"Lưu RAM: {text}")


class StorageFactory:
    _mapping = {
        "file": FileStorage,
        "memory": MemoryStorage,
    }

    @classmethod
    def create(cls, storage_type):

        try:
            return cls._mapping[storage_type]()
        except KeyError:
            raise ValueError(f"Unknown storage: {storage_type}")


storage = StorageFactory.create("file")
storage.save("Hello")
```

---

# 14. Factory và SOLID

Factory giúp tuân thủ **Open/Closed Principle**:

* Thêm class mới.
* Không sửa code cũ.

Ví dụ:

```python
CrawlerFactory.register("new_site", NewSiteCrawler)
```

Không cần sửa:

```python
CrawlerFactory.create()
```

---

# 15. Factory vs Constructor

Constructor

```python
book = Book(...)
```

Factory

```python
book = BookFactory.create(...)
```

Constructor dùng khi:

* Tạo object đơn giản.

Factory dùng khi:

* Quy trình tạo phức tạp.
* Có nhiều loại object.
* Muốn ẩn logic khởi tạo.

---

# 16. Factory vs Alternative Constructor

Alternative Constructor

```python
Book.from_json(...)
```

Factory

```python
BookFactory.create(...)
```

Khác nhau:

| Alternative Constructor | Factory                    |
| ----------------------- | -------------------------- |
| Tạo **một loại object** | Tạo **nhiều loại object**  |
| Thuộc chính class       | Có thể là class riêng      |
| Dùng `cls(...)`         | Chọn class phù hợp rồi tạo |

---

# 17. Best Practices

✅ Dùng dictionary thay vì nhiều `if...elif`.

```python
_mapping = {
    "sqlite": SQLiteDatabase,
    "postgres": PostgreSQLDatabase,
}
```

---

✅ Đăng ký class bằng `register()` nếu muốn mở rộng động.

---

✅ Factory chỉ nên tạo object, không nên chứa logic nghiệp vụ.

---

✅ Trả về kiểu cơ sở (`BaseCrawler`, `BaseStorage`, ...) để tận dụng tính đa hình.

---

# Những lỗi người mới thường gặp

## Lỗi 1

Factory quá lớn

```python
class MegaFactory:
```

Tạo:

* Database
* Parser
* Crawler
* Logger
* Cache

↓

Nên tách thành nhiều factory nhỏ.

---

## Lỗi 2

Nhét logic nghiệp vụ vào Factory

Sai:

```python
class BookFactory:

    def create(...):
        # tạo object
        # lưu database
        # gửi email
```

Factory chỉ nên tạo object.

---

## Lỗi 3

Không xử lý trường hợp không tồn tại

Sai:

```python
return cls._mapping[name]()
```

Nên:

```python
try:
    return cls._mapping[name]()
except KeyError:
    raise ValueError(f"Unknown type: {name}")
```

---

## Lỗi 4

Không dùng lớp cơ sở

Nếu các class không có giao diện chung:

```python
Dog.speak()
Cat.run()
```

Client sẽ khó sử dụng thống nhất.

Hãy xây dựng một lớp cơ sở hoặc `ABC` với các phương thức chung.

---

# Bài tập

## Bài 1

Viết `ShapeFactory`:

* `Circle`
* `Rectangle`
* `Triangle`

```python
shape = ShapeFactory.create("circle")
```

---

## Bài 2

Viết `PaymentFactory`:

* `CashPayment`
* `CardPayment`
* `BankTransferPayment`

Mỗi class có:

```python
pay(amount)
```

---

## Bài 3

Trong framework cào truyện, viết `ParserFactory`:

* `HtmlParser`
* `JsonParser`
* `XmlParser`

Hỗ trợ:

```python
parser = ParserFactory.create("html")
```

---

## Bài 4

Viết `CrawlerFactory`:

* `TruyenFullCrawler`
* `TangThuVienCrawler`
* `WikiDichCrawler`

Hỗ trợ:

* `create(source)`
* `register(name, crawler_cls)`

Thử đăng ký thêm:

```python
CrawlerFactory.register("novelbin", NovelBinCrawler)
```

mà **không cần sửa** mã nguồn của `create()`.

---

## Bài 5 (Nâng cao)

Thiết kế `RepositoryFactory` cho dự án cào truyện:

```python
repo = RepositoryFactory.create("book", database)

repo = RepositoryFactory.create("chapter", database)

repo = RepositoryFactory.create("author", database)
```

Yêu cầu:

* Mỗi repository kế thừa từ `BaseRepository`.
* Sử dụng dictionary để ánh xạ tên → lớp.
* Hỗ trợ `register()` để các plugin có thể thêm repository mới.
* Chuẩn bị nền tảng cho **Dependency Injection** và **Plugin Architecture** ở các buổi sau.

---

# Tổng kết buổi học

* **Factory Pattern** tách logic tạo đối tượng khỏi mã sử dụng đối tượng, giúp mã nguồn linh hoạt và dễ mở rộng.
* Thay vì chuỗi `if...elif...else`, hãy sử dụng bảng ánh xạ (`dict`) hoặc cơ chế `register()` để quản lý các lớp có thể tạo.
* Factory kết hợp rất tốt với **Polymorphism**, **Abstract Base Class**, `@classmethod` và **Plugin Architecture**.
* Trong các dự án thực tế như framework cào truyện, Factory là nền tảng để tạo `Crawler`, `Parser`, `Repository`, `Database` hoặc `Storage` theo cấu hình mà không làm thay đổi mã nguồn phía client.

> **Buổi 24** chúng ta sẽ chuyển sang **Phần VII – Thiết kế Class** với chủ đề **Composition (Hợp thành)**. Đây là một nguyên tắc thiết kế quan trọng giúp giảm phụ thuộc vào kế thừa và là nền tảng của nhiều kiến trúc hiện đại như Clean Architecture, Domain-Driven Design và Dependency Injection.
