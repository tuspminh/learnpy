# Pydantic v2 — Buổi 3: Validation chuyên sâu cơ bản

> **Buổi 3/50 — Foundation**

Ở Buổi 1 chúng ta đã biết `BaseModel`, `model_validate()` và `ValidationError`.
Buổi 2 tập trung vào `Field` và type annotation.

Buổi này chúng ta đi sâu vào **cơ chế validation của Pydantic v2**, đặc biệt là:

* Pydantic validate dữ liệu như thế nào.
* Type coercion.
* Strict mode.
* `ValidationError`.
* `errors()`.
* `error_count()`.
* `json()`.
* Xử lý lỗi trong application.
* Áp dụng validation vào **Novel Crawler**.

---

# 1. Validation là gì?

Giả sử crawler parser trả về:

```python
data = {
    "title": "Đấu Phá Thương Khung",
    "chapter_count": "1648",
}
```

Ta định nghĩa:

```python
from pydantic import BaseModel


class Novel(BaseModel):
    title: str
    chapter_count: int
```

Sau đó:

```python
novel = Novel.model_validate(data)
```

Pydantic sẽ thực hiện đại khái:

```text
data
 │
 ▼
Pydantic
 │
 ├── title → str
 │
 └── chapter_count → int
 │
 ▼
Novel
```

Nếu dữ liệu hợp lệ:

```text
Novel(...)
```

Nếu không hợp lệ:

```text
ValidationError
```

---

# 2. Validation không chỉ là kiểm tra kiểu

Đây là điểm quan trọng.

Pydantic không đơn giản làm:

```python
isinstance(value, int)
```

Mà còn có thể **parse / convert** dữ liệu.

Ví dụ:

```python
from pydantic import BaseModel


class User(BaseModel):
    age: int


user = User(age="25")

print(user.age)
print(type(user.age))
```

Kết quả:

```text
25
<class 'int'>
```

Pydantic đã biến:

```text
"25"
```

thành:

```text
25
```

---

# 3. Type coercion

**Type coercion** = tự động chuyển dữ liệu về kiểu mong muốn khi Pydantic xác định việc chuyển đổi đó hợp lệ.

Ví dụ:

```python
from pydantic import BaseModel


class Product(BaseModel):
    id: int
    price: float


product = Product(
    id="100",
    price="29.5",
)

print(product)
```

Kết quả:

```text
id=100 price=29.5
```

Kiểm tra:

```python
print(type(product.id))
print(type(product.price))
```

Kết quả:

```text
<class 'int'>
<class 'float'>
```

---

# 4. Không phải mọi thứ đều được convert

Ví dụ:

```python
from pydantic import BaseModel, ValidationError


class Product(BaseModel):
    id: int


try:
    Product(id="abc")
except ValidationError as e:
    print(e)
```

Pydantic không thể biến:

```text
"abc"
```

thành:

```text
int
```

nên validation thất bại.

---

# 5. `ValidationError`

Đây là exception quan trọng nhất khi làm việc với Pydantic.

```python
from pydantic import BaseModel, ValidationError


class User(BaseModel):
    id: int
    name: str
    age: int


try:
    user = User(
        id="abc",
        name="John",
        age="hello",
    )
except ValidationError as e:
    print(e)
```

Pydantic có thể báo nhiều lỗi:

```text
2 validation errors for User

id
  Input should be a valid integer, unable to parse string as an integer

age
  Input should be a valid integer, unable to parse string as an integer
```

Điểm quan trọng:

> Pydantic không dừng ngay ở lỗi đầu tiên.

Nó cố gắng thu thập các lỗi validation rồi trả về cùng lúc.

---

# 6. `errors()`

Trong application thực tế, chúng ta thường không chỉ:

```python
print(e)
```

Mà sử dụng:

```python
e.errors()
```

Ví dụ:

```python
from pydantic import BaseModel, ValidationError


class User(BaseModel):
    id: int
    name: str
    age: int


try:
    User(
        id="abc",
        name="John",
        age="hello",
    )

except ValidationError as e:
    print(e.errors())
```

Bạn sẽ nhận được một list các dictionary.

Ví dụ dạng:

```python
[
    {
        "type": "int_parsing",
        "loc": ("id",),
        "msg": "Input should be a valid integer, unable to parse string as an integer",
        "input": "abc",
    },
    {
        "type": "int_parsing",
        "loc": ("age",),
        "msg": "Input should be a valid integer, unable to parse string as an integer",
        "input": "hello",
    },
]
```

---

# 7. `loc` — vị trí lỗi

Một phần cực kỳ quan trọng là:

```python
"loc": ("id",)
```

Nó cho biết lỗi nằm ở đâu.

Ví dụ:

```python
class User(BaseModel):
    id: int
    name: str
```

Lỗi:

```python
{
    "loc": ("id",)
}
```

nghĩa là:

```text
User.id
```

---

## Nested model

Sau này chúng ta có:

```python
class Author(BaseModel):
    name: str


class Novel(BaseModel):
    title: str
    author: Author
```

Nếu dữ liệu:

```python
data = {
    "title": "ĐPTK",
    "author": {
        "name": 123
    }
}
```

`loc` có thể biểu diễn đường dẫn:

```python
("author", "name")
```

Tức là:

```text
Novel.author.name
```

Đây là lý do `loc` rất hữu ích khi xử lý JSON phức tạp.

---

# 8. `error_count()`

Pydantic cung cấp:

```python
e.error_count()
```

Ví dụ:

```python
from pydantic import BaseModel, ValidationError


class User(BaseModel):
    id: int
    age: int


try:
    User(
        id="abc",
        age="xyz",
    )
except ValidationError as e:
    print(e.error_count())
```

Kết quả:

```text
2
```

---

# 9. `json()` — thông tin lỗi dạng JSON

Có thể lấy lỗi ở dạng JSON:

```python
try:
    User(
        id="abc",
        age="xyz",
    )
except ValidationError as e:
    print(e.json())
```

Điều này hữu ích khi:

```text
API
Logging
Monitoring
Error response
```

---

# 10. `ValidationError` không nên bị nuốt

Một cách viết không tốt:

```python
try:
    user = User(...)
except ValidationError:
    pass
```

Bạn đã làm mất thông tin lỗi.

Tệ hơn:

```python
try:
    user = User(...)
except Exception:
    pass
```

Không biết:

* validation lỗi?
* database lỗi?
* network lỗi?
* programming bug?

---

# 11. Xử lý đúng ở boundary

Ví dụ application:

```python
from pydantic import BaseModel, ValidationError


class NovelDTO(BaseModel):
    title: str
    author: str
    chapter_count: int


def parse_novel(data: dict) -> NovelDTO:
    return NovelDTO.model_validate(data)


data = {
    "title": "ĐPTK",
    "author": "Thiên Tằm Thổ Đậu",
    "chapter_count": "1648",
}

try:
    novel = parse_novel(data)

except ValidationError as e:
    print("Dữ liệu Novel không hợp lệ")
    print(e.errors())

else:
    print("Novel hợp lệ")
    print(novel)
```

Đây là pattern chúng ta sẽ sử dụng nhiều trong crawler.

---

# 12. Type coercion có thể gây bất ngờ

Ví dụ:

```python
class User(BaseModel):
    age: int
```

Dữ liệu:

```python
User(age="100")
```

→ hợp lệ.

Nhưng trong một số application, chúng ta muốn:

> `"100"` phải bị coi là sai vì API phải trả đúng integer.

Khi đó chúng ta cần **Strict Mode**.

---

# 13. Strict Mode

Pydantic mặc định thiên về việc parse dữ liệu.

Nhưng có thể yêu cầu strict:

```python
from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(strict=True)

    age: int
```

Bây giờ:

```python
User(age=25)
```

OK.

Nhưng:

```python
User(age="25")
```

sẽ lỗi.

---

# 14. Strict theo từng field

Không nhất thiết toàn bộ model phải strict.

Có thể:

```python
from typing import Annotated

from pydantic import BaseModel, Field


class User(BaseModel):
    age: Annotated[int, Field(strict=True)]
```

Hoặc cách thường dùng với Pydantic:

```python
from pydantic import BaseModel, StrictInt


class User(BaseModel):
    age: StrictInt
```

Khi đó:

```python
User(age=25)
```

OK.

Nhưng:

```python
User(age="25")
```

→ lỗi.

---

# 15. Khi nào dùng coercion?

Ví dụ crawler đọc HTML:

```html
<span class="chapter-count">1648</span>
```

Parser:

```python
{
    "chapter_count": "1648"
}
```

Trong trường hợp này coercion:

```text
"1648"
 ↓
1648
```

rất tiện.

---

# 16. Khi nào dùng strict?

Ví dụ API contract:

```json
{
    "chapter_count": 1648
}
```

Nếu API trả:

```json
{
    "chapter_count": "1648"
}
```

và bạn muốn phát hiện API contract sai ngay lập tức, strict mode phù hợp hơn.

---

# 17. So sánh

|                                  | Coercion | Strict   |
| -------------------------------- | -------- | -------- |
| `"10"` → `int`                   | Có       | Không    |
| `10` → `int`                     | Có       | Có       |
| Dễ dùng                          | Cao      | Thấp hơn |
| Phù hợp parsing                  | ✅        | Có thể   |
| Phù hợp API contract nghiêm ngặt | Có thể   | ✅        |

Không có lựa chọn tuyệt đối đúng.

**Chọn theo boundary và nguồn dữ liệu.**

---

# 18. Validation ở Novel Crawler

Đây là một pipeline rất thực tế:

```text
HTML
 │
 ▼
selectolax
 │
 ▼
dict
 │
 ▼
Pydantic
 │
 ├── valid
 │     ↓
 │   DTO
 │
 └── invalid
       ↓
   ValidationError
```

Ví dụ parser:

```python
data = {
    "title": "Đấu Phá Thương Khung",
    "author": "Thiên Tằm Thổ Đậu",
    "url": "/truyen/dau-pha",
    "chapter_count": "1648",
}
```

Model:

```python
from pydantic import BaseModel


class NovelSummaryDTO(BaseModel):
    title: str
    author: str
    url: str
    chapter_count: int
```

Validate:

```python
novel = NovelSummaryDTO.model_validate(data)
```

Kết quả:

```python
NovelSummaryDTO(
    title="Đấu Phá Thương Khung",
    author="Thiên Tằm Thổ Đậu",
    url="/truyen/dau-pha",
    chapter_count=1648,
)
```

---

# 19. Validation thất bại trong crawler

Parser có thể gặp:

```python
data = {
    "title": "ĐPTK",
    "author": "Thiên Tằm",
    "url": "/truyen/dptk",
    "chapter_count": "N/A",
}
```

Khi đó:

```python
try:
    novel = NovelSummaryDTO.model_validate(data)

except ValidationError as e:
    print("Parser output invalid")

    for error in e.errors():
        print(error)
```

Kết quả có thể:

```text
Parser output invalid

{
    'type': 'int_parsing',
    'loc': ('chapter_count',),
    ...
}
```

Ta biết chính xác parser đã tạo dữ liệu không hợp lệ.

---

# 20. Validation Error ≠ Domain Error

Đây là một phân biệt rất quan trọng đối với DDD.

Ví dụ:

```text
chapter_count = "abc"
```

Đây là:

```text
Data Validation Error
```

Nhưng:

```text
chapter_count = -10
```

có thể là:

```text
Domain Validation Error
```

Và:

```text
Novel đã tồn tại
```

có thể là:

```text
Business Rule Error
```

Ba loại này không nên trộn lẫn.

```text
Pydantic Validation
        │
        ▼
     DTO hợp lệ
        │
        ▼
 Domain Rules
        │
        ▼
 Application Rules
```

Chúng ta sẽ quay lại vấn đề này ở phần **DTO + DDD**.

---

# 21. Một ví dụ hoàn chỉnh

Tạo file:

```text
lesson_03.py
```

Nội dung:

```python
from pydantic import BaseModel, ValidationError


class NovelSummaryDTO(BaseModel):
    title: str
    author: str
    url: str
    chapter_count: int
    completed: bool = False


def validate_novel(data: dict) -> NovelSummaryDTO | None:
    try:
        return NovelSummaryDTO.model_validate(data)

    except ValidationError as e:
        print("❌ Novel không hợp lệ")
        print(f"Số lỗi: {e.error_count()}")

        for error in e.errors():
            print()
            print(f"Field : {error['loc']}")
            print(f"Type  : {error['type']}")
            print(f"Input : {error['input']}")
            print(f"Error : {error['msg']}")

        return None


def main() -> None:
    data = {
        "title": "Đấu Phá Thương Khung",
        "author": "Thiên Tằm Thổ Đậu",
        "url": "https://example.com/dptk",
        "chapter_count": "1648",
        "completed": "true",
    }

    novel = validate_novel(data)

    if novel is not None:
        print()
        print("✅ Novel hợp lệ")
        print(novel)

        print()
        print("chapter_count:", novel.chapter_count)
        print("type:", type(novel.chapter_count))


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python lesson_03.py
```

Bạn sẽ thấy:

```text
✅ Novel hợp lệ

title='Đấu Phá Thương Khung'
author='Thiên Tằm Thổ Đậu'
url='https://example.com/dptk'
chapter_count=1648
completed=True

chapter_count: 1648
type: <class 'int'>
```

---

# 22. Thử dữ liệu lỗi

Đổi:

```python
"chapter_count": "1648",
```

thành:

```python
"chapter_count": "abc",
```

Chạy lại.

Bạn sẽ nhận được validation error.

Đây chính là một trong những workflow quan trọng của crawler:

```text
Parser
  ↓
dict
  ↓
DTO validation
  ↓
❌ Parser bug / dữ liệu bất thường
```

Thay vì để dữ liệu lỗi chạy sâu xuống:

```text
Parser
 ↓
Use Case
 ↓
Domain
 ↓
Repository
 ↓
SQLite
```

---

# 23. Một nguyên tắc kiến trúc quan trọng

Không nên làm:

```python
class Novel(BaseModel):
    ...
    
    def save_to_database(self):
        ...
```

Pydantic model không nên biết SQLite.

Cũng không nên:

```python
class Novel(BaseModel):
    ...
    
    def crawl_chapters(self):
        ...
```

Pydantic không nên biết crawler.

Thay vào đó:

```text
                    External Data
                         │
                         ▼
                ┌────────────────┐
                │ Pydantic DTO   │
                │ Validation     │
                └───────┬────────┘
                        │
                      Mapper
                        │
                        ▼
                ┌────────────────┐
                │ Domain Entity  │
                └───────┬────────┘
                        │
                        ▼
                ┌────────────────┐
                │ Application    │
                └───────┬────────┘
                        │
                        ▼
                ┌────────────────┐
                │ Repository     │
                └────────────────┘
```

Đây sẽ là tư duy xuyên suốt phần Pydantic nâng cao.

---

# 24. Bài tập thực hành

## Bài 1 — User

Tạo:

```python
class User(BaseModel):
    id: int
    username: str
    age: int
    active: bool
```

Test:

```python
{
    "id": "10",
    "username": "garden",
    "age": "30",
    "active": "true",
}
```

Kiểm tra type của từng field.

---

## Bài 2 — Validation Error

Test:

```python
{
    "id": "abc",
    "username": "garden",
    "age": "hello",
    "active": "???",
}
```

In:

```python
e.errors()
```

và tự đọc:

```text
type
loc
msg
input
```

---

## Bài 3 — Strict

Tạo:

```python
class User(BaseModel):
    model_config = ConfigDict(strict=True)

    id: int
    age: int
```

Test:

```python
User(
    id="10",
    age="30",
)
```

Quan sát sự khác biệt so với model bình thường.

---

## Bài 4 — Novel Crawler

Tạo:

```python
class NovelSummaryDTO(BaseModel):
    title: str
    author: str
    url: str
    chapter_count: int
    completed: bool
```

Test lần lượt:

### Case 1

```python
{
    "title": "ĐPTK",
    "author": "Thiên Tằm",
    "url": "/dptk",
    "chapter_count": "1648",
    "completed": "true",
}
```

### Case 2

```python
{
    "title": "ĐPTK",
    "author": "Thiên Tằm",
    "url": "/dptk",
    "chapter_count": "N/A",
    "completed": "true",
}
```

### Case 3

```python
{
    "title": "ĐPTK",
    "author": "Thiên Tằm",
}
```

Quan sát **3 loại tình huống khác nhau**:

```text
Case 1 → coercion thành công
Case 2 → parsing error
Case 3 → required field error
```

---

# 25. Tổng kết Buổi 3

Bạn cần nhớ 6 ý chính:

```text
1. Pydantic thực hiện runtime validation.

2. Pydantic v2 mặc định có type coercion trong nhiều trường hợp.

3. Dữ liệu không thể chuyển/validate → ValidationError.

4. e.errors() cho structured validation errors.

5. Strict mode dùng khi cần kiểm soát type chặt hơn.

6. Pydantic nên nằm ở boundary, không phải là Domain Entity.
```

Và kiến trúc chúng ta đang hướng tới:

```text
                 UNTRUSTED DATA
                       │
                       ▼
              ┌─────────────────┐
              │    Pydantic     │
              │   Validation    │
              └────────┬────────┘
                       │
                 Validated DTO
                       │
                       ▼
              ┌─────────────────┐
              │     Domain      │
              │     Entity      │
              └────────┬────────┘
                       │
                       ▼
              Application / Repo
```

**Buổi 4** sẽ chuyển sang một phần cực kỳ quan trọng: **Nested Models** — model lồng nhau, `list[Model]`, `dict[str, Model]`, và chúng ta sẽ bắt đầu mô hình hóa dữ liệu kiểu:

```text
Novel
 ├── author
 ├── metadata
 └── chapters
      ├── Chapter
      ├── Chapter
      └── Chapter
```

Đây là nền tảng để sau này xây `NovelDTO`, `ChapterDTO`, `ParserResult` cho Novel Crawler.
