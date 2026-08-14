# Buổi 4 — `action` Deep Dive trong argparse

Hôm nay chúng ta học một phần **rất quan trọng** của `argparse`: `action`.

Nếu `type` quyết định **giá trị được nhận vào kiểu gì**, thì `action` quyết định **parser phải làm gì khi gặp argument đó**.

Sau buổi này bạn sẽ hiểu và sử dụng được:

```bash
--verbose
--debug
--dry-run
--force
--no-cache
-vv
-vvv
--tag python --tag cli
--version
```

---

# 1. `action` là gì?

Xét:

```python
parser.add_argument(
    "--verbose",
    action="store_true"
)
```

Khi người dùng chạy:

```bash
python app.py --verbose
```

`argparse` không cần một giá trị phía sau:

```bash
--verbose something
```

Thay vào đó, việc **xuất hiện `--verbose` chính là giá trị**.

Nói cách khác:

```text
--verbose xuất hiện
        ↓
verbose = True
```

Không xuất hiện:

```text
verbose = False
```

Đây chính là vai trò của `action`.

---

# 2. `action` mặc định là `store`

Nếu bạn viết:

```python
parser.add_argument(
    "--name"
)
```

thực chất `argparse` đang dùng action mặc định:

```python
action="store"
```

Ví dụ:

```bash
python app.py --name Alice
```

Kết quả:

```python
Namespace(name="Alice")
```

Giá trị `Alice` được **store** vào `args.name`.

---

# 3. `store` hoạt động như thế nào?

Code:

```python
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--name",
    action="store"
)

args = parser.parse_args()

print(args.name)
```

Chạy:

```bash
python app.py --name Alice
```

Kết quả:

```text
Alice
```

Đây là dạng argument thông thường:

```text
--name VALUE
```

Ví dụ:

```text
--output result.json
--port 8000
--timeout 30
--format json
```

---

# 4. `store_true`

Đây là action bạn sẽ sử dụng **rất nhiều**.

```python
parser.add_argument(
    "--verbose",
    action="store_true"
)
```

Không có:

```bash
python app.py
```

↓

```python
args.verbose == False
```

Có:

```bash
python app.py --verbose
```

↓

```python
args.verbose == True
```

---

# 5. Tư duy về `store_true`

Hãy đọc:

```python
action="store_true"
```

là:

> Nếu thấy option này, hãy lưu `True`.

Ví dụ:

```bash
python app.py --debug
```

thì:

```python
debug = True
```

Nếu không:

```python
debug = False
```

---

# 6. Ví dụ `--dry-run`

Một CLI chuyên nghiệp thường có:

```bash
crawler crawl URL --dry-run
```

Ý nghĩa:

> Chạy thử nhưng không thực sự thay đổi dữ liệu.

Khai báo:

```python
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Chỉ chạy thử, không thay đổi dữ liệu"
)
```

Sau đó:

```python
if args.dry_run:
    print("DRY RUN")
else:
    print("EXECUTE")
```

---

# 7. `--force`

Ví dụ:

```python
parser.add_argument(
    "--force",
    action="store_true"
)
```

Chạy:

```bash
python delete.py data.db --force
```

thì:

```python
args.force == True
```

Ứng dụng có thể:

```python
if args.force:
    delete_database()
```

---

# 8. `store_false`

Ngược lại với `store_true`.

```python
parser.add_argument(
    "--no-cache",
    action="store_false",
    dest="cache"
)
```

Nếu:

```bash
python app.py --no-cache
```

thì:

```python
args.cache == False
```

---

# 9. Tại sao cần `dest`?

Vì chúng ta muốn:

```bash
--no-cache
```

nhưng code lại dễ đọc:

```python
args.cache
```

Khai báo:

```python
parser.add_argument(
    "--no-cache",
    action="store_false",
    dest="cache"
)
```

Kết quả:

```text
--no-cache
      ↓
cache = False
```

---

# 10. Pattern `--cache` và `--no-cache`

Một thiết kế tốt hơn là:

```python
parser.add_argument(
    "--cache",
    dest="cache",
    action="store_true"
)

parser.add_argument(
    "--no-cache",
    dest="cache",
    action="store_false"
)
```

Sau đó:

```python
args.cache
```

sẽ biểu diễn trạng thái cache.

Ví dụ:

```bash
python app.py --cache
```

↓

```python
cache = True
```

và:

```bash
python app.py --no-cache
```

↓

```python
cache = False
```

Đây là pattern rất hữu ích trong CLI thực tế.

---

# 11. `store_true` và `store_false`

So sánh:

| Action        | Khi xuất hiện |
| ------------- | ------------- |
| `store_true`  | lưu `True`    |
| `store_false` | lưu `False`   |

Ví dụ:

```python
action="store_true"
```

```text
không có → False
có       → True
```

Còn:

```python
action="store_false"
```

thường dùng với option mang nghĩa phủ định:

```text
--no-cache
--no-color
--no-progress
```

---

# 12. `append`

Bây giờ đến một action cực kỳ hữu ích.

Giả sử muốn:

```bash
python app.py \
    --tag python \
    --tag argparse \
    --tag cli
```

Ta muốn:

```python
args.tag
```

trở thành:

```python
[
    "python",
    "argparse",
    "cli"
]
```

Dùng:

```python
parser.add_argument(
    "--tag",
    action="append"
)
```

---

# 13. `append` hoạt động như thế nào?

Mỗi lần gặp:

```bash
--tag
```

giá trị được thêm vào list.

Ví dụ:

```bash
--tag python
```

↓

```python
["python"]
```

Tiếp:

```bash
--tag argparse
```

↓

```python
["python", "argparse"]
```

Tiếp:

```bash
--tag cli
```

↓

```python
["python", "argparse", "cli"]
```

---

# 14. Ví dụ thực tế với crawler

Crawler có thể cho phép nhiều domain:

```bash
python crawler.py \
    --allow-domain example.com \
    --allow-domain example.org
```

Code:

```python
parser.add_argument(
    "--allow-domain",
    action="append"
)
```

Kết quả:

```python
args.allow_domain
```

↓

```python
[
    "example.com",
    "example.org"
]
```

Rất tiện.

---

# 15. `append` + `type`

Bạn có thể kết hợp:

```python
parser.add_argument(
    "--port",
    action="append",
    type=int
)
```

Chạy:

```bash
python app.py \
    --port 8000 \
    --port 9000
```

Kết quả:

```python
args.port
```

↓

```python
[8000, 9000]
```

---

# 16. `append_const`

Đây là action nâng cao hơn.

Ví dụ:

```python
parser.add_argument(
    "--fast",
    dest="mode",
    action="append_const",
    const="fast"
)

parser.add_argument(
    "--safe",
    dest="mode",
    action="append_const",
    const="safe"
)
```

Chạy:

```bash
python app.py --fast --safe
```

Kết quả:

```python
args.mode
```

↓

```python
[
    "fast",
    "safe"
]
```

`append_const` sẽ thêm **một giá trị cố định** thay vì lấy giá trị từ command line.

---

# 17. `count`

Đây là action cực kỳ thú vị.

Nhiều CLI sử dụng:

```bash
-v
-vv
-vvv
```

để tăng mức verbosity.

Ví dụ:

```python
parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0
)
```

---

## Không có `-v`

```bash
python app.py
```

↓

```python
args.verbose == 0
```

---

## Một `-v`

```bash
python app.py -v
```

↓

```python
args.verbose == 1
```

---

## Hai `-v`

```bash
python app.py -vv
```

↓

```python
args.verbose == 2
```

---

## Ba `-v`

```bash
python app.py -vvv
```

↓

```python
args.verbose == 3
```

---

# 18. Tại sao `count` hữu ích?

Bạn có thể xây dựng:

```text
0 → WARNING
1 → INFO
2 → DEBUG
3 → TRACE
```

Ví dụ:

```python
if args.verbose == 0:
    level = "WARNING"

elif args.verbose == 1:
    level = "INFO"

elif args.verbose >= 2:
    level = "DEBUG"
```

Đây là một pattern rất thường gặp trong CLI chuyên nghiệp.

---

# 19. `version`

`argparse` có sẵn action để xử lý:

```bash
--version
```

Ví dụ:

```python
parser.add_argument(
    "--version",
    action="version",
    version="crawler 1.0.0"
)
```

Chạy:

```bash
python crawler.py --version
```

Kết quả:

```text
crawler 1.0.0
```

Chương trình sẽ tự kết thúc sau khi in version.

---

# 20. Ví dụ CLI hoàn chỉnh

Bây giờ kết hợp những gì đã học.

```python
import argparse


parser = argparse.ArgumentParser(
    description="Professional crawler CLI"
)

parser.add_argument(
    "url",
    help="URL bắt đầu crawl"
)

parser.add_argument(
    "-o",
    "--output",
    metavar="FILE",
    help="File lưu kết quả"
)

parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Chạy thử, không lưu dữ liệu"
)

parser.add_argument(
    "--force",
    action="store_true",
    help="Bỏ qua cảnh báo"
)

parser.add_argument(
    "--tag",
    action="append",
    help="Tag của job"
)

parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0,
    help="Tăng mức độ log"
)

parser.add_argument(
    "--version",
    action="version",
    version="crawler 1.0.0"
)

args = parser.parse_args()

print(args)
```

---

# 21. Thử chạy

### Cơ bản

```bash
python crawler.py https://example.com
```

Kết quả có thể là:

```text
Namespace(
    url='https://example.com',
    output=None,
    dry_run=False,
    force=False,
    tag=None,
    verbose=0
)
```

---

### Dry run

```bash
python crawler.py \
    https://example.com \
    --dry-run
```

Ta có:

```python
args.dry_run == True
```

---

### Force

```bash
python crawler.py \
    https://example.com \
    --force
```

Ta có:

```python
args.force == True
```

---

### Nhiều tag

```bash
python crawler.py \
    https://example.com \
    --tag novel \
    --tag fiction \
    --tag vietnamese
```

Ta có:

```python
args.tag
```

↓

```python
[
    "novel",
    "fiction",
    "vietnamese"
]
```

---

### Verbosity

```bash
python crawler.py https://example.com -vv
```

↓

```python
args.verbose == 2
```

---

# 22. `action` + `type` + `default`

Ba thành phần này có thể kết hợp:

```python
parser.add_argument(
    "--workers",
    type=int,
    default=4
)
```

Đây là:

```text
type
 ↓
chuyển string → int

default
 ↓
nếu không truyền → 4
```

Còn:

```python
parser.add_argument(
    "--tag",
    action="append"
)
```

là:

```text
action
 ↓
mỗi lần xuất hiện → append vào list
```

---

# 23. Bảng tổng hợp

| Action         | Ý nghĩa                |
| -------------- | ---------------------- |
| `store`        | Lưu giá trị            |
| `store_true`   | Xuất hiện → `True`     |
| `store_false`  | Xuất hiện → `False`    |
| `append`       | Thêm giá trị vào list  |
| `append_const` | Thêm constant vào list |
| `count`        | Đếm số lần xuất hiện   |
| `version`      | In version rồi thoát   |

Bạn chưa cần nhớ mọi action ngay lập tức.

Quan trọng nhất là nhớ:

```text
store
store_true
store_false
append
count
version
```

---

# 24. Một lỗi rất phổ biến

Đừng viết:

```python
parser.add_argument(
    "--verbose",
    type=bool
)
```

Rồi chạy:

```bash
python app.py --verbose False
```

Đây là thiết kế sai cho boolean flag.

Hãy dùng:

```python
parser.add_argument(
    "--verbose",
    action="store_true"
)
```

và:

```bash
python app.py --verbose
```

---

# 25. Một lỗi khác

Không nên:

```bash
python app.py --tag python argparse cli
```

với:

```python
action="append"
```

`append` yêu cầu:

```bash
--tag python
--tag argparse
--tag cli
```

Nếu muốn nhận nhiều giá trị sau **một option**, đó là vấn đề của `nargs`, chúng ta sẽ học sâu ở **Buổi 6**.

---

# 26. Thiết kế CLI cho TTS

Với ứng dụng TTS mà bạn đang xây dựng, có thể thiết kế:

```bash
tts input.txt \
    --voice vi-VN-HoaiMyNeural \
    --rate 1.0 \
    --volume 100 \
    --output output.mp3
```

Các argument:

```python
parser.add_argument(
    "input_file"
)

parser.add_argument(
    "--voice"
)

parser.add_argument(
    "--rate",
    type=float,
    default=1.0
)

parser.add_argument(
    "--volume",
    type=int,
    default=100
)

parser.add_argument(
    "-o",
    "--output"
)
```

Sau đó thêm:

```bash
--dry-run
```

```bash
--verbose
```

thì:

```python
parser.add_argument(
    "--dry-run",
    action="store_true"
)

parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0
)
```

Đây chính là cách `argparse` bắt đầu trở thành **kiến trúc CLI thực tế**, thay vì chỉ là vài dòng demo.

---

# 27. Bài tập thực hành

## Bài 1 — Boolean flags

Tạo CLI:

```bash
python app.py --debug --dry-run --force
```

Kết quả:

```python
args.debug == True
args.dry_run == True
args.force == True
```

Không truyền thì tất cả phải là:

```python
False
```

---

## Bài 2 — Multiple values

Tạo:

```bash
python app.py \
    --tag python \
    --tag cli \
    --tag argparse
```

Kết quả:

```python
[
    "python",
    "cli",
    "argparse"
]
```

Dùng `action="append"`.

---

## Bài 3 — Verbosity

Tạo:

```bash
python app.py -vvv
```

Kết quả:

```python
verbose = 3
```

Không truyền:

```python
verbose = 0
```

---

## Bài 4 — Version

Tạo:

```bash
python app.py --version
```

In:

```text
mytool 1.0.0
```

Sau đó chương trình phải tự kết thúc.

---

# 28. Bài tập lớn ⭐

Hãy xây dựng parser cho:

```bash
crawler URL
```

Hỗ trợ:

```bash
-o FILE
--max-pages N
--timeout SECONDS
--dry-run
--force
--tag TAG
-v
--version
```

Ví dụ:

```bash
crawler https://example.com \
    -o result.json \
    --max-pages 100 \
    --timeout 30 \
    --dry-run \
    --tag novel \
    --tag fiction \
    -vv
```

Parser phải tạo ra một `Namespace` tương đương:

```python
Namespace(
    url="https://example.com",
    output="result.json",
    max_pages=100,
    timeout=30,
    dry_run=True,
    force=False,
    tag=["novel", "fiction"],
    verbose=2
)
```

**Chưa cần viết crawler.** Chỉ tập trung vào việc thiết kế parser.

---

# 29. Kiến thức cần ghi nhớ

Nếu gặp:

```bash
--name Alice
```

→ `store`

Nếu gặp:

```bash
--verbose
```

→ `store_true`

Nếu gặp:

```bash
--no-cache
```

→ thường là `store_false`

Nếu gặp:

```bash
--tag python --tag cli
```

→ `append`

Nếu gặp:

```bash
-vvv
```

→ `count`

Nếu gặp:

```bash
--version
```

→ `version`

---

# 30. Sơ đồ tư duy

```text
                    argparse
                       │
                    action
                       │
       ┌───────────────┼────────────────┐
       │               │                │
     store          boolean           collection
       │               │                │
       │        ┌──────┴──────┐         │
       │        │             │         │
       │   store_true   store_false   append
       │                                  │
       │                                list
       │
       ├── value
       │
       └── type/default
       
                    count
                      │
                   -v -vv -vvv

                    version
                      │
                 --version
```

---

## Kết quả cần đạt sau Buổi 4

Bạn nên có khả năng nhìn vào CLI:

```bash
crawler URL \
    --dry-run \
    --force \
    --tag python \
    --tag web \
    -vv
```

và **tự suy ra được**:

```python
args.url
args.dry_run
args.force
args.tag
args.verbose
```

mà không cần tra tài liệu.

**Buổi 5** chúng ta sẽ học **Type & Validation Deep Dive**: `int`, `float`, `Path`, `FileType`, `choices`, custom type, validation nhiều tầng và cách viết validator chuyên nghiệp cho CLI.
