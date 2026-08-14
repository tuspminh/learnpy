# Buổi 3 — Optional Arguments Deep Dive

Hôm nay chúng ta chuyển từ **Positional Arguments** sang phần cực kỳ quan trọng trong CLI chuyên nghiệp:

```bash
--output
--config
--verbose
--port
--format
```

Đây là kiểu argument bạn gặp liên tục khi dùng:

```bash
git
docker
pytest
pip
ruff
```

---

# 1. Positional vs Optional

Buổi trước:

```bash
python app.py input.txt output.txt
```

Đây là **positional arguments**.

Ý nghĩa phụ thuộc vào vị trí:

```text
input.txt  → input
output.txt → output
```

---

Optional argument thì có tên:

```bash
python app.py --output result.txt
```

hoặc:

```bash
python app.py -o result.txt
```

Người dùng không cần nhớ vị trí chính xác, vì argument có **flag** xác định ý nghĩa.

---

# 2. Optional Argument đầu tiên

```python
import argparse

parser = argparse.ArgumentParser()

parser.add_argument(
    "--name"
)

args = parser.parse_args()

print(args)
```

Chạy:

```bash
python app.py --name Alice
```

Kết quả:

```text
Namespace(name='Alice')
```

Ta có:

```python
args.name
```

---

# 3. `--name` khác `"name"` như thế nào?

Positional:

```python
parser.add_argument("name")
```

Gọi:

```bash
python app.py Alice
```

Optional:

```python
parser.add_argument("--name")
```

Gọi:

```bash
python app.py --name Alice
```

Đây là hai cơ chế khác nhau.

---

# 4. Optional argument thường có 2 dạng

Thông thường chúng ta khai báo:

```python
parser.add_argument(
    "-n",
    "--name"
)
```

Người dùng có thể dùng:

```bash
python app.py -n Alice
```

hoặc:

```bash
python app.py --name Alice
```

Đây là pattern cực kỳ phổ biến.

---

# 5. Short Option và Long Option

Convention:

```text
-n
```

là **short option**.

```text
--name
```

là **long option**.

Ví dụ:

```bash
-v
--verbose
```

```bash
-o
--output
```

```bash
-c
--config
```

```bash
-p
--port
```

---

# 6. Khai báo short + long

```python
parser.add_argument(
    "-o",
    "--output"
)
```

Chạy:

```bash
python app.py -o result.txt
```

hoặc:

```bash
python app.py --output result.txt
```

Cả hai đều tạo:

```python
args.output
```

---

# 7. Tên attribute được tạo như thế nào?

Ví dụ:

```python
parser.add_argument(
    "-o",
    "--output"
)
```

Argument:

```text
--output
```

sẽ tạo:

```python
args.output
```

---

Nếu:

```python
parser.add_argument(
    "-c",
    "--config-file"
)
```

thì:

```python
args.config_file
```

Dấu `-` trong option được chuyển thành `_` trong Python attribute.

---

# 8. `dest`

Bạn có thể tự đặt tên attribute.

```python
parser.add_argument(
    "-o",
    "--output",
    dest="output_file"
)
```

Sau đó:

```python
args.output_file
```

thay vì:

```python
args.output
```

Thông thường không cần `dest`, nhưng nó hữu ích khi muốn kiểm soát API nội bộ.

---

# 9. Optional argument có thể có giá trị

Ví dụ:

```python
parser.add_argument(
    "-p",
    "--port",
    type=int
)
```

Chạy:

```bash
python server.py --port 8080
```

Kết quả:

```python
Namespace(port=8080)
```

Do:

```python
type=int
```

nên:

```python
args.port
```

là `int`.

---

# 10. `default`

Nếu người dùng không truyền argument:

```python
parser.add_argument(
    "--port",
    type=int,
    default=8000
)
```

Chạy:

```bash
python server.py
```

Kết quả:

```python
Namespace(port=8000)
```

Nếu:

```bash
python server.py --port 9000
```

thì:

```python
Namespace(port=9000)
```

Đây là một pattern rất quan trọng:

```text
user cung cấp giá trị
        ↓
dùng giá trị đó

không cung cấp
        ↓
dùng default
```

---

# 11. `required=True`

Mặc định optional argument là **không bắt buộc**.

```python
parser.add_argument(
    "--config"
)
```

Người dùng có thể chạy:

```bash
python app.py
```

Không lỗi.

---

Nếu:

```python
parser.add_argument(
    "--config",
    required=True
)
```

thì:

```bash
python app.py
```

sẽ lỗi.

Người dùng bắt buộc phải viết:

```bash
python app.py --config config.json
```

---

## Có nên dùng `required=True` nhiều không?

Thông thường **không nên lạm dụng**.

Nếu argument thực sự bắt buộc và có tính chất cốt lõi, đôi khi positional argument rõ ràng hơn:

```bash
python app.py config.json
```

thay vì:

```bash
python app.py --config config.json
```

Nhưng với một số CLI, `required=True` vẫn rất hữu ích.

---

# 12. `help`

Ví dụ:

```python
parser.add_argument(
    "-o",
    "--output",
    help="File đầu ra"
)
```

Chạy:

```bash
python app.py --help
```

sẽ thấy:

```text
-o OUTPUT, --output OUTPUT
    File đầu ra
```

---

# 13. `metavar`

Mặc định:

```python
--output OUTPUT
```

Bạn có thể đổi:

```python
parser.add_argument(
    "-o",
    "--output",
    metavar="FILE",
    help="File đầu ra"
)
```

Kết quả:

```text
-o FILE, --output FILE
```

`metavar` chỉ thay đổi **help display**.

Nó không đổi:

```python
args.output
```

---

# 14. `type`

Ví dụ server:

```python
parser.add_argument(
    "--port",
    type=int,
    default=8000
)
```

Người dùng:

```bash
python server.py --port 9000
```

thì:

```python
args.port == 9000
```

là:

```python
int
```

Nếu:

```bash
python server.py --port abc
```

`argparse` tự báo lỗi.

---

# 15. Optional argument + choices

Ví dụ:

```python
parser.add_argument(
    "--format",
    choices=[
        "json",
        "csv",
        "xml"
    ],
    default="json"
)
```

Hợp lệ:

```bash
python app.py --format json
```

```bash
python app.py --format csv
```

Không hợp lệ:

```bash
python app.py --format yaml
```

---

# 16. Optional argument không có value

Đây là điểm cực kỳ quan trọng.

Ví dụ:

```bash
python app.py --verbose
```

`--verbose` không cần:

```bash
--verbose something
```

Nó chỉ là một **flag**.

Để làm kiểu này, chúng ta dùng:

```python
action="store_true"
```

Ví dụ:

```python
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true"
)
```

---

Nếu:

```bash
python app.py
```

thì:

```python
args.verbose
```

là:

```python
False
```

Nếu:

```bash
python app.py --verbose
```

thì:

```python
args.verbose
```

là:

```python
True
```

Phần `action` sẽ được học rất kỹ ở **Buổi 4**.

---

# 17. Ví dụ thực tế: Downloader CLI

Ta muốn có CLI:

```bash
python download.py URL
```

và:

```bash
python download.py URL --output file.zip
```

và:

```bash
python download.py URL --output file.zip --timeout 30
```

Code:

```python
import argparse


parser = argparse.ArgumentParser(
    description="Simple downloader"
)

parser.add_argument(
    "url",
    help="URL cần download"
)

parser.add_argument(
    "-o",
    "--output",
    metavar="FILE",
    help="Tên file đầu ra"
)

parser.add_argument(
    "--timeout",
    type=int,
    default=30,
    help="Timeout tính bằng giây"
)

args = parser.parse_args()

print("URL:", args.url)
print("Output:", args.output)
print("Timeout:", args.timeout)
```

---

Chạy:

```bash
python download.py https://example.com
```

Kết quả:

```text
URL: https://example.com
Output: None
Timeout: 30
```

---

Chạy:

```bash
python download.py https://example.com \
    --output result.html \
    --timeout 60
```

Kết quả:

```text
URL: https://example.com
Output: result.html
Timeout: 60
```

---

# 18. Kết hợp Positional + Optional

Đây là kiểu CLI bạn sẽ sử dụng rất nhiều.

```python
parser.add_argument(
    "url"
)

parser.add_argument(
    "-o",
    "--output"
)

parser.add_argument(
    "--timeout",
    type=int,
    default=30
)
```

CLI:

```bash
python download.py URL \
    --output result.html \
    --timeout 60
```

Mô hình:

```text
                  CLI
                   │
       ┌───────────┴───────────┐
       │                       │
 positional                optional
       │                       │
      URL              --output result.html
                              │
                       --timeout 60
```

---

# 19. Một CLI thực tế hơn

Giả sử chúng ta xây dựng crawler.

Ta muốn:

```bash
python crawler.py https://example.com
```

hoặc:

```bash
python crawler.py \
    https://example.com \
    --output data.json \
    --timeout 30 \
    --max-pages 100
```

Code:

```python
import argparse


parser = argparse.ArgumentParser(
    description="Web crawler"
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
    "--timeout",
    type=int,
    default=30,
    metavar="SECONDS",
    help="Request timeout"
)

parser.add_argument(
    "--max-pages",
    type=int,
    default=100,
    metavar="N",
    help="Số trang tối đa"
)

args = parser.parse_args()

print(args)
```

---

# 20. Help sẽ trông như thế nào?

Chạy:

```bash
python crawler.py --help
```

Bạn sẽ nhận được đại loại:

```text
usage: crawler.py [-h] [-o FILE] [--timeout SECONDS]
                  [--max-pages N]
                  url

Web crawler

positional arguments:
  url                   URL bắt đầu crawl

options:
  -h, --help            show this help message and exit
  -o FILE, --output FILE
                        File lưu kết quả
  --timeout SECONDS     Request timeout
  --max-pages N         Số trang tối đa
```

Đây chính là kiểu help message mà chúng ta hướng tới khi xây dựng CLI chuyên nghiệp.

---

# 21. Một nguyên tắc thiết kế quan trọng

Hãy phân biệt:

### Positional

Dùng cho dữ liệu **cốt lõi**:

```bash
python crawler.py URL
```

### Optional

Dùng cho **configuration / behavior**:

```bash
--timeout
--output
--max-pages
--proxy
--user-agent
```

Ví dụ crawler:

```bash
crawler URL --timeout 30 --max-pages 100
```

rất tự nhiên.

---

# 22. `default=None`

Nếu không truyền:

```python
parser.add_argument(
    "--output"
)
```

thì mặc định:

```python
args.output is None
```

Bạn có thể viết rõ:

```python
parser.add_argument(
    "--output",
    default=None
)
```

Hai cách tương đương trong trường hợp này.

---

# 23. `default` có thể là string

```python
parser.add_argument(
    "--user-agent",
    default="MyCrawler/1.0"
)
```

Khi đó:

```python
args.user_agent
```

sẽ có giá trị:

```text
MyCrawler/1.0
```

nếu người dùng không cung cấp.

---

# 24. Một lỗi thiết kế thường gặp

Không nên biến mọi thứ thành optional:

```bash
python crawler.py \
    --url https://example.com \
    --output result.json \
    --timeout 30 \
    --max-pages 100
```

Nếu `url` là thành phần bắt buộc và duy nhất, thiết kế:

```bash
python crawler.py https://example.com \
    --output result.json \
    --timeout 30 \
    --max-pages 100
```

thường dễ đọc hơn.

Tuy nhiên đây **không phải luật cứng**. Khi CLI lớn, có subcommand, đôi khi `--url` lại hợp lý hơn.

---

# 25. Pattern CLI bạn nên nhớ

Một CLI cơ bản thường có cấu trúc:

```text
COMMAND [POSITIONAL] [OPTIONS]
```

Ví dụ:

```bash
crawler URL --output result.json --timeout 30
```

Trong đó:

```text
crawler
   │
   ├── URL
   │
   ├── --output
   │
   └── --timeout
```

---

# 26. Bài tập thực hành

## Bài 1 — File Converter

Tạo:

```bash
python convert.py input.txt
```

Hỗ trợ:

```bash
-o output.json
```

và:

```bash
--format json
```

Yêu cầu:

* `input` là positional.
* `output` là optional.
* `format` là optional.
* `format` chỉ nhận:

  * `json`
  * `csv`
  * `xml`
* `format` mặc định là `json`.

---

## Bài 2 — HTTP Client

Tạo CLI:

```bash
python request.py https://example.com
```

Hỗ trợ:

```bash
--method GET
```

và:

```bash
--timeout 30
```

`method` chỉ nhận:

```text
GET
POST
PUT
DELETE
```

`timeout` là `int`, mặc định:

```text
30
```

---

## Bài 3 — Crawler

Thiết kế:

```bash
python crawler.py URL
```

Hỗ trợ:

```text
-o FILE
--output FILE

--max-pages N

--timeout SECONDS
```

Mặc định:

```text
max-pages = 100
timeout = 30
```

Hãy tự thiết kế `--help` sao cho người khác nhìn vào là hiểu ngay CLI hoạt động như thế nào.

---

# 27. Thử thách ⭐

Hãy thiết kế CLI cho crawler mà bạn đang hướng tới:

```bash
crawl URL
```

Hỗ trợ:

```bash
-o result.json
--max-pages 100
--timeout 30
--concurrency 10
--user-agent "MyCrawler/1.0"
```

Hãy viết **chỉ phần `argparse`**, chưa cần thực hiện crawl.

Mục tiêu là tạo được:

```python
Namespace(
    url=...,
    output=...,
    max_pages=...,
    timeout=...,
    concurrency=...,
    user_agent=...
)
```

Đây là bài tập rất tốt vì nó bắt đầu đưa `argparse` vào đúng **crawler framework** mà bạn đang xây dựng.

---

# Tổng kết Buổi 3

Bạn cần nhớ 6 thứ quan trọng:

```python
parser.add_argument(
    "-o",
    "--output",
    type=str,
    default=None,
    metavar="FILE",
    help="..."
)
```

| Thành phần | Vai trò                     |
| ---------- | --------------------------- |
| `-o`       | short option                |
| `--output` | long option                 |
| `type`     | chuyển đổi/validate dữ liệu |
| `default`  | giá trị mặc định            |
| `metavar`  | tên hiển thị trong help     |
| `help`     | mô tả argument              |

Và một pattern cực kỳ quan trọng:

```text
Positional
    ↓
dữ liệu cốt lõi

Optional
    ↓
configuration / behavior
```

**Buổi 4** sẽ là **`action` Deep Dive** — đặc biệt quan trọng vì chúng ta sẽ xây dựng các flag kiểu:

```bash
--verbose
--debug
--dry-run
--force
--no-cache
-v
-vv
-vvv
```

và hiểu chính xác `store`, `store_true`, `store_false`, `append`, `count`, `version` hoạt động bên trong như thế nào.
