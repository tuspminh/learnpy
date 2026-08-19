Khi bạn cài đặt `html2text` qua `pip`, Python sẽ tự động cài sẵn một công cụ CLI (Command Line Interface) giúp bạn chuyển đổi file HTML sang Markdown trực tiếp từ Terminal/Command Prompt mà không cần mở trình biên soạn code.

---

## 1. Cú pháp cơ bản

Cách sử dụng cơ bản nhất là truyền đường dẫn tới file `.html`:

```bash
# In kết quả trực tiếp ra màn hình Terminal
html2text input.html

# Xuất kết quả ra file Markdown (.md)
html2text input.html > output.md

```

---

## 2. Kết hợp với `curl` hoặc `wget` để tải web trực tiếp

Bạn có thể truyền dữ liệu từ lệnh tải web (`curl`) thẳng vào `html2text` thông qua dấu pipe (`|`):

```bash
# Tải trang web và xem định dạng Markdown ngay trên Terminal
curl -s https://en.wikipedia.org/wiki/Python_(programming_language) | html2text

# Tải trang web và lưu trực tiếp thành file Markdown
curl -s https://en.wikipedia.org/wiki/Python_(programming_language) | html2text > python_wiki.md

```

---

## 3. Các tham số (Flags) phổ biến trong CLI

Bạn có thể tùy chỉnh hành vi của `html2text` bằng cách thêm các flag khi gõ lệnh:

| Flag / Tham số | Ý nghĩa | Lệnh mẫu |
| --- | --- | --- |
| **`-b 0`** hoặc **`--body-width=0`** | **Tắt tự động xuống dòng** (giữ văn bản liên tục, rất khuyên dùng). | `html2text -b 0 input.html` |
| **`-i`** hoặc **`--ignore-links`** | Bỏ qua toàn bộ liên kết (chỉ giữ lại văn bản hiển thị). | `html2text -i input.html` |
| **`-I`** hoặc **`--ignore-images`** | Bỏ qua hình ảnh. | `html2text -I input.html` |
| **`--google-doc`** | Tối ưu hóa định dạng cho file HTML xuất từ Google Docs. | `html2text --google-doc input.html` |
| **`--help`** | Xem danh sách đầy đủ tất cả các cờ hỗ trợ. | `html2text --help` |

### Ví dụ kết hợp nhiều tùy chỉnh:

```bash
# Chuyển đổi file: Không ngắt dòng, bỏ qua link và hình ảnh
html2text -b 0 -i -I input.html > output_clean.md

```

---

## 4. Mẹo nâng cao: Chuyển đổi hàng loạt (Batch Processing)

Nếu bạn có một thư mục chứa nhiều file HTML và muốn chuyển đổi tất cả sang `.md` cùng lúc:

**Trên Linux / macOS (Bash/Zsh):**

```bash
for file in *.html; do
    html2text -b 0 "$file" > "${file%.html}.md"
done

```

**Trên Windows (PowerShell):**

```powershell
Get-ChildItem *.html | ForEach-Object {
    html2text -b 0 $_.FullName > "$($_.BaseName).md"
}

```