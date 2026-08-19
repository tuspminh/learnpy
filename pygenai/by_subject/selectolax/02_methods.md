Trong `selectolax`, kiến trúc được chia thành **2 đối tượng chính**:

1. **Parser Object** (`LexborHTMLParser` hoặc `HTMLParser`): Đại diện cho toàn bộ cây DOM của tài liệu HTML.
2. **Node Object** (`Node`): Đại diện cho từng phần tử (thẻ HTML hoặc text node) bên trong cây DOM.

Dưới đây là chi tiết toàn bộ các thuộc tính và phương thức của từng đối tượng.

---

## 1. Đối tượng Parser (`LexborHTMLParser` / `HTMLParser`)

Đối tượng này được tạo ra khi bạn nạp chuỗi HTML vào thư viện.

### 📌 Thuộc tính (Attributes)

| Thuộc tính | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `.root` | `Node | None` | Trả về Node gốc (Root node) của toàn bộ cây DOM. |
| `.body` | `Node | None` | Trả về Node đại diện cho thẻ `<body>`. Nếu không có, trả về `None`. |
| `.head` | `Node | None` | Trả về Node đại diện cho thẻ `<head>`. Nếu không có, trả về `None`. |
| `.html` | `str | None` | Trả về toàn bộ chuỗi HTML hiện tại dưới dạng `str`. |

---

### 🛠️ Phương thức (Methods)

#### 1. Tìm kiếm & Truy vấn

* **`css(query: str) -> list[Node]`**
* Tìm tất cả các node khớp với CSS Selector.
* **Trả về:** Danh sách các `Node`. Nếu không tìm thấy, trả về danh sách rỗng `[]`.


* **`css_first(query: str, default=None) -> Node | Any`**
* Tìm node **đầu tiên** khớp với CSS Selector.
* **Tham số:** `default` (giá trị trả về nếu không tìm thấy, mặc định là `None`).


* **`tags(name: str) -> list[Node]`**
* Tìm nhanh tất cả các node có tên thẻ bằng `name` (Ví dụ: `tree.tags('a')`).
* **Lưu ý:** Phương thức này chạy nhanh hơn `.css()` vì không cần phân tích cú pháp CSS selector.



#### 2. Trích xuất dữ liệu & Thao tác DOM

* **`text(deep=True, separator='', strip=False) -> str`**
* Lấy toàn bộ văn bản của tài liệu HTML.
* **Tham số:**
* `deep`: Nếu `True`, lấy text của tất cả node con.
* `separator`: Chuỗi phân cách giữa các đoạn text.
* `strip`: Nếu `True`, loại bỏ khoảng trắng thừa ở hai đầu.




* **`strip_tags(tags: list[str]) -> None`**
* Xóa bỏ hoàn toàn các thẻ có tên trong danh sách `tags` nhưng **giữ lại văn bản** bên trong chúng.


* **`clone() -> LexborHTMLParser`**
* Tạo một bản sao độc lập (Deep copy) của cây DOM hiện tại.



---

## 2. Đối tượng Node (`Node`)

`Node` đại diện cho một phần tử HTML. Bạn thu được `Node` sau khi dùng `.css()`, `.css_first()`, hoặc duyệt cây DOM.

### 📌 Thuộc tính thông tin (Information Attributes)

| Thuộc tính | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `.tag` | `str | None` | Tên của thẻ HTML dưới dạng chữ thường (VD: `'div'`, `'a'`). Nếu là Text Node, trả về `'-text'`. |
| `.attributes` | `dict[str, str]` | Dictionary chứa toàn bộ thuộc tính của thẻ (VD: `{'href': '...', 'class': '...'}`). |
| `.attrs` | `dict[str, str]` | Alias (viết tắt) của `.attributes`. |
| `.id` | `str | None` | Giá trị của thuộc tính `id`. Trả về `None` nếu không có id. |
| `.html` | `str | None` | Trả về HTML toàn bộ của Node đó (Outer HTML, bao gồm cả thẻ mở/đóng của chính nó). |
| `.raw_value` | `bytes` | Giá trị mã hóa thô dạng byte của Node. |

---

### 📌 Thuộc tính điều hướng DOM (Navigation Attributes)

| Thuộc tính | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `.parent` | `Node | None` | Node cha trực tiếp. |
| `.child` | `Node | None` | Node con đầu tiên. |
| `.first_child` | `Node | None` | Đồng nghĩa với `.child`. |
| `.last_child` | `Node | None` | Node con cuối cùng. |
| `.next` | `Node | None` | Node anh/em kế tiếp cùng cấp (Next Sibling). |
| `.prev` | `Node | None` | Node anh/em phía trước cùng cấp (Previous Sibling). |

---

### 🛠️ Phương thức của Node

#### 1. Trích xuất Dữ liệu & Truy vấn con

* **`text(deep=True, separator='', strip=False) -> str`**
* Lấy văn bản bên trong Node này.
* **Ví dụ:**
```python
node.text(strip=True, separator=" ")

```


* **`css(query: str) -> list[Node]`**
  * Tìm các Node con bên trong Node hiện tại khớp với CSS Selector.
* **`css_first(query: str, default=None) -> Node | Any`**
  * Tìm Node con đầu tiên khớp với CSS Selector.

#### 2. Duyệt Node (Iteration & Traversal)

* **`iter(include_text=False)`**
  * Trả về một iterator lặp qua tất cả các **Node con trực tiếp** (direct children).
  * `include_text=True`: Bao gồm cả các đoạn văn bản (Text Nodes).
* **`traverse(include_text=False)`**
  * Trả về một generator duyệt qua **tất cả các Node con cháu** (descendants) theo chiều sâu (Depth-first traversal).

#### 3. Chỉnh sửa DOM (DOM Manipulation)

* **`decompose(keep_empty_parent=False) -> None`**
  * Xóa hoàn toàn Node này khỏi cây DOM. 
  * *Rất hữu ích để xóa quảng cáo, script, style trước khi trích xuất.*
* **`replace_with(value: str | Node) -> None`**
  * Thay thế Node hiện tại bằng một Node khác hoặc một chuỗi HTML/Text mới.
* **`insert_before(value: str | Node) -> None`**
  * Chèn một Node hoặc chuỗi HTML vào ngay trước Node hiện tại.
* **`insert_after(value: str | Node) -> None`**
  * Chèn một Node hoặc chuỗi HTML vào ngay sau Node hiện tại.
* **`append_child(value: Node) -> None`**
  * Thêm một Node con vào vị trí cuối cùng trong danh sách con của Node hiện tại.
* **`unwrap() -> None`**
  * Xóa bỏ thẻ hiện tại nhưng **giữ lại tất cả phần tử con** bên trong nó.
* **`unwrap_tags(tags: list[str]) -> None`**
  * Loại bỏ các thẻ chỉ định bên trong Node này nhưng giữ lại con của chúng.
* **`strip_tags(tags: list[str]) -> None`**
  * Loại bỏ các thẻ chỉ định bên trong Node này nhưng giữ lại phần văn bản.

---

## 3. Ví dụ minh họa sử dụng thuộc tính & phương thức

```python
from selectolax.lexbor import LexborHTMLParser

html = """
<div id="container">
    <h1 class="header">Tiêu đề</h1>
    <div class="body-text">
        <p>Đoạn 1 với <a href="/link1">Link 1</a></p>
        <p>Đoạn 2 với <a href="/link2">Link 2</a></p>
    </div>
</div>
"""

tree = LexborHTMLParser(html)

# 1. Sử dụng Parser Attributes & Methods
container = tree.css_first("#container")

# 2. Thuộc tính của Node
print("Tag name:", container.tag)  # Output: div
print("Node ID:", container.id)  # Output: container
print("Attributes:", container.attributes)  # Output: {'id': 'container'}

# 3. Điều hướng DOM (Navigation)
h1_node = container.child  # Node con đầu tiên (h1)
print("H1 Text:", h1_node.text())  # Output: Tiêu đề

next_node = h1_node.next  # Sibling tiếp theo (div.body-text)
print("Next sibling tag:", next_node.tag)  # Output: div

# 4. Thao tác DOM (Unwrap & Decompose)
# Xóa thẻ <a> nhưng giữ lại text "Link 1", "Link 2"
container.unwrap_tags(["a"])
print(container.text(strip=True, separator=" "))

```