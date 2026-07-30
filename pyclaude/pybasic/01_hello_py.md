[Roadmap](00_roadmap.md)    [02_variable_datatype_operators](02_variable_datatype_operators.md)
### Bài 1: Python là gì? Cài đặt môi trường & chương trình đầu tiên

#### 1. Python là gì và tại sao nó phổ biến?

Python là ngôn ngữ lập trình **thông dịch (interpreted)**, **bậc cao (high-level)**, do Guido van Rossum tạo ra năm 1991. Điểm khác biệt lớn nhất so với C/C++/Java:

- **Không cần biên dịch (compile)** trước khi chạy — bạn viết code, chạy ngay lập tức. Máy tính đọc và thực thi từng dòng thông qua một chương trình gọi là **interpreter** (trình thông dịch).
- **Cú pháp gần với tiếng Anh tự nhiên**, dùng thụt lề (indentation) để phân định khối lệnh thay vì dấu ngoặc `{}` như nhiều ngôn ngữ khác.
- **"Pin đã lắp sẵn" (batteries included)** — thư viện chuẩn cực kỳ phong phú, gần như làm gì cũng có sẵn module hỗ trợ.

**Ứng dụng thực tế hiện nay (2026):**

- **AI/Machine Learning**: PyTorch, TensorFlow — hầu hết mô hình AI lớn (kể cả các LLM bạn đang dùng) được huấn luyện bằng framework viết trên Python.
- **Web Backend**: Django, FastAPI — Instagram, một phần hạ tầng của YouTube dùng Python.
- **Tự động hóa**: viết script tự động xử lý Excel, gửi email, cào dữ liệu web (web scraping).
- **Khoa học dữ liệu & phân tích tài chính**: Pandas, NumPy.
- **DevOps & scripting hệ thống**.

#### 2. Cài đặt Python

**Bước 1 — Tải Python:**  
Vào [python.org/downloads](https://www.python.org/downloads/), tải bản mới nhất (khuyến nghị Python 3.12 hoặc mới hơn).

- **Windows**: khi cài đặt, **nhớ tick vào ô "Add Python to PATH"** trước khi bấm Install — đây là lỗi phổ biến nhất khiến người mới không chạy được Python từ terminal.
- **macOS**: có thể dùng trình cài đặt từ python.org, hoặc `brew install python3` nếu đã có Homebrew.
- **Linux**: thường có sẵn Python, kiểm tra bằng `python3 --version`.

**Bước 2 — Kiểm tra cài đặt:**  
Mở Terminal (macOS/Linux) hoặc Command Prompt/PowerShell (Windows), gõ:

bash

```bash
python --version
```

hoặc trên macOS/Linux đôi khi cần:

bash

```bash
python3 --version
```

Nếu hiện ra ví dụ `Python 3.12.4` — bạn đã cài thành công.

**Bước 3 — Cài trình soạn thảo code (IDE):**  
Tôi khuyến nghị **Visual Studio Code (VS Code)** — miễn phí, nhẹ, có extension Python cực mạnh (autocomplete, debug, gợi ý lỗi). Tải tại [code.visualstudio.com](https://code.visualstudio.com), sau đó cài extension **"Python"** của Microsoft trong tab Extensions.

#### 3. Chương trình đầu tiên

Tạo file tên `bai1.py`, gõ đúng nội dung sau:

python

```python
# Đây là comment - dòng chú thích, Python sẽ bỏ qua, không thực thi
# Comment dùng để giải thích code cho người đọc (kể cả chính bạn sau này)

print("Xin chào, tôi đang học Python!")
print("Hôm nay là ngày đầu tiên của hành trình.")

# Thử một chút tính toán
print(5 + 3)
```

Chạy bằng cách mở terminal tại thư mục chứa file, gõ:

bash

```bash
python bai1.py
```

**Kết quả mong đợi:**

```
Xin chào, tôi đang học Python!
Hôm nay là ngày đầu tiên của hành trình.
8
```

#### 4. Giải phẫu đoạn code trên — hiểu từng phần

- **`print()`** là một **hàm (function)** có sẵn của Python, dùng để in giá trị ra màn hình. Cặp ngoặc `()` là nơi bạn "đưa" dữ liệu vào cho hàm xử lý — gọi là **tham số (argument)**.
- **Chuỗi văn bản (string)** phải được bao trong dấu nháy `"..."` hoặc `'...'`. Python coi đây là kiểu dữ liệu văn bản.
- **`5 + 3`** không có dấu nháy → Python hiểu đây là **số (number)**, và thực hiện phép cộng thực sự, kết quả là `8`.
- **Không có dấu chấm phẩy `;`** cuối dòng như C/Java — Python dùng **dấu xuống dòng** để biết một lệnh đã kết thúc.

#### 5. Quy tắc thụt lề (Indentation) — điều SỐNG CÒN trong Python

Đây là điều khiến Python khác biệt hoàn toàn: **thụt lề không phải để đẹp mắt, mà là cú pháp bắt buộc**. Ví dụ (sẽ học kỹ ở Bài 4), nhưng bạn cần ghi nhớ ngay từ bây giờ:

python

```python
if 5 > 3:
    print("5 lớn hơn 3")   # dòng này PHẢI thụt vào 4 dấu cách
print("Dòng này không thụt lề")
```

Nếu bạn thụt lề sai (thiếu hoặc thừa khoảng trắng), Python sẽ báo lỗi `IndentationError`. Quy ước chuẩn: **4 dấu cách** cho mỗi cấp thụt lề (không dùng Tab trộn với Space).

---

#### 🎯 Bài tập thực hành

Hãy tạo file `bai_tap_1.py` và viết chương trình:

1. In ra dòng chữ giới thiệu tên bạn (ví dụ: `"Tôi tên là Minh"`)
2. In ra kết quả phép tính: tuổi bạn nhân 2
3. Thêm ít nhất 1 dòng comment giải thích code

Bạn thử làm rồi gửi kết quả cho tôi xem nhé — tôi sẽ nhận xét và chúng ta chuyển sang **Bài 2: Biến, kiểu dữ liệu và toán tử**, nơi bạn sẽ hiểu sâu về cách Python lưu trữ và thao tác dữ liệu.

[Roadmap](00_roadmap.md)    [02_variable_datatype_operators](02_variable_datatype_operators.md)
