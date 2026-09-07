# Buổi 23 — EXISTS

Đây là buổi **kết thúc phần quan hệ cơ bản + truy vấn nâng cao đầu tiên** của chúng ta.

Nếu `IN` hỏi:

> **"Giá trị này có nằm trong tập kết quả không?"**

thì `EXISTS` hỏi:

> **"Có tồn tại ít nhất một dòng thỏa điều kiện hay không?"**

Với app crawler truyện, `EXISTS` cực kỳ tự nhiên cho các câu hỏi:

* Novel có chapter chưa?
* Novel có chapter >= 1000 chưa?
* Novel có tag `"Huyền Huyễn"` không?
* Có chapter nào chưa crawl không?
* Có bản ghi liên quan nào tồn tại không?

---

# 1. EXISTS là gì?

Cú pháp:

```sql id="z0d1kx"
SELECT ...
FROM table_a AS a
WHERE EXISTS (
    SELECT 1
    FROM table_b AS b
    WHERE b.a_id = a.id
);
```

Ví dụ:

```sql id="f0j9ab"
SELECT
    n.id,
    n.title
FROM novels AS n
WHERE EXISTS (
    SELECT 1
    FROM chapters AS c
    WHERE c.novel_id = n.id
);
```

Ý nghĩa:

> Lấy Novel nếu **tồn tại ít nhất một Chapter thuộc Novel đó**.

---

# 2. `SELECT 1` nghĩa là gì?

Bạn sẽ thường thấy:

```sql id="xjv3tg"
SELECT 1
FROM chapters
WHERE ...
```

Nhiều người mới học sẽ hỏi:

> "Tại sao lại SELECT 1? Tại sao không SELECT *?"

Bởi vì `EXISTS` **không quan tâm dữ liệu được SELECT là gì**.

Nó chỉ quan tâm:

```text id="2g5f8n"
Có ít nhất một row?
        ↓
YES → TRUE
NO  → FALSE
```

Do đó:

```sql id="qf1j6m"
EXISTS (
    SELECT 1
    FROM chapters
    WHERE ...
)
```

là cách viết rất phổ biến.

Bạn cũng có thể viết:

```sql id="q4d8wy"
EXISTS (
    SELECT *
    FROM chapters
    WHERE ...
)
```

nhưng:

```sql id="3v7h2s"
SELECT 1
```

thể hiện rõ ý đồ:

> Tôi chỉ kiểm tra **sự tồn tại**, không cần dữ liệu.

---

# 3. Ví dụ cơ bản

Database:

```text id="0w2z9p"
novels

1 Tiên Nghịch
2 Đấu Phá
3 Phàm Nhân
```

```text id="h5r8c1"
chapters

1 → novel 1
2 → novel 1
3 → novel 2
```

Query:

```sql id="2x5s8v"
SELECT
    n.id,
    n.title
FROM novels AS n
WHERE EXISTS (
    SELECT 1
    FROM chapters AS c
    WHERE c.novel_id = n.id
);
```

Kết quả:

```text id="6c9m2q"
Tiên Nghịch
Đấu Phá
```

`Phàm Nhân` không xuất hiện.

---

# 4. Đây là Correlated Subquery

Subquery:

```sql id="7v3k5n"
SELECT 1
FROM chapters AS c
WHERE c.novel_id = n.id
```

sử dụng:

```sql id="1n8q4m"
n.id
```

từ query bên ngoài.

Do đó nó gọi là:

> **Correlated Subquery**

Tức là subquery **liên quan đến từng row của outer query**.

Mental model:

```text id="m4q8s1"
Novel 1
   ↓
Có Chapter của Novel 1?
   ↓
YES

Novel 2
   ↓
Có Chapter của Novel 2?
   ↓
YES

Novel 3
   ↓
Có Chapter của Novel 3?
   ↓
NO
```

---

# 5. EXISTS trả về TRUE/FALSE

Đây là cách hiểu quan trọng nhất:

```sql id="y9n2cw"
WHERE EXISTS (...)
```

gần giống:

```python id="x8s4q1"
if exists_related_record:
    ...
```

Trong Python:

```python id="g7v1pz"
if has_chapters(novel_id):
    ...
```

Trong SQL:

```sql id="e3x6m8"
WHERE EXISTS (
    SELECT 1
    FROM chapters c
    WHERE c.novel_id = n.id
)
```

---

# 6. NOT EXISTS

Ngược lại:

```sql id="q8m2s5"
WHERE NOT EXISTS (...)
```

nghĩa là:

> Không tồn tại.

Ví dụ:

> Tìm Novel chưa có Chapter.

```sql id="e2v7ka"
SELECT
    n.id,
    n.title
FROM novels AS n
WHERE NOT EXISTS (
    SELECT 1
    FROM chapters AS c
    WHERE c.novel_id = n.id
);
```

Kết quả:

```text id="r5j9x3"
Phàm Nhân
```

Đây là một pattern cực kỳ quan trọng.

---

# 7. `NOT EXISTS` và `NOT IN`

Ở buổi 22, chúng ta có:

```sql id="3s5m8n"
SELECT
    id,
    title
FROM novels
WHERE id NOT IN (
    SELECT novel_id
    FROM chapters
);
```

Có thể thay bằng:

```sql id="6p1x4v"
SELECT
    n.id,
    n.title
FROM novels AS n
WHERE NOT EXISTS (
    SELECT 1
    FROM chapters AS c
    WHERE c.novel_id = n.id
);
```

Hai query có cùng ý tưởng:

```text id="x3f7n2"
Novel không có Chapter
```

Nhưng `NOT EXISTS` thường thể hiện ý nghĩa nghiệp vụ rõ hơn:

```text id="m8q1s5"
"Không tồn tại chapter liên quan"
```

và tránh các vấn đề logic của `NOT IN` khi tập con có `NULL`.

---

# 8. EXISTS vs IN

Đây là phần quan trọng nhất của buổi hôm nay.

### IN

```sql id="5y8q3m"
SELECT
    id,
    title
FROM novels
WHERE id IN (
    SELECT novel_id
    FROM chapters
);
```

Tư duy:

```text id="3f6n9v"
Lấy tập novel_id
      ↓
id có nằm trong tập đó không?
```

### EXISTS

```sql id="k2m7x4"
SELECT
    n.id,
    n.title
FROM novels AS n
WHERE EXISTS (
    SELECT 1
    FROM chapters AS c
    WHERE c.novel_id = n.id
);
```

Tư duy:

```text id="a9w3p6"
Với Novel này:
có tồn tại Chapter tương ứng không?
```

---

# 9. Mental model

### IN

```text id="7p1x5m"
Chapter
   ↓
tạo danh sách ID
   ↓
Novel.id IN danh sách
```

### EXISTS

```text id="c4n8q2"
Novel
   ↓
kiểm tra
   ↓
có Chapter liên quan?
   ↓
TRUE / FALSE
```

Nói ngắn gọn:

```text id="v8m2r6"
IN
→ membership

EXISTS
→ existence
```

---

# 10. EXISTS không cần lấy dữ liệu Chapter

Ví dụ:

> Novel có chapter số 1000 hay không?

```sql id="z6t3p8"
SELECT
    n.id,
    n.title
FROM novels AS n
WHERE EXISTS (
    SELECT 1
    FROM chapters AS c
    WHERE c.novel_id = n.id
      AND c.chapter_number = 1000
);
```

Ta không cần:

```sql id="x5q8m1"
SELECT c.title
```

vì câu hỏi chỉ là:

> Có tồn tại hay không?

---

# 11. EXISTS với nhiều điều kiện

Ví dụ:

> Novel có chapter >= 1000?

```sql id="f8m2r7"
SELECT
    n.id,
    n.title
FROM novels AS n
WHERE EXISTS (
    SELECT 1
    FROM chapters AS c
    WHERE c.novel_id = n.id
      AND c.chapter_number >= 1000
);
```

Có thể đọc:

> Với từng Novel, hãy kiểm tra xem có ít nhất một Chapter thỏa:

```text id="j3v6q9"
c.novel_id = n.id
AND
c.chapter_number >= 1000
```

---

# 12. EXISTS + Many-to-Many

Bây giờ bài toán:

> Tìm Novel có tag `"Huyền Huyễn"`.

Ta có:

```text id="m6q2x8"
novels
   ↓
novel_tags
   ↓
tags
```

Dùng:

```sql id="s9k4v2"
SELECT
    n.id,
    n.title
FROM novels AS n
WHERE EXISTS (
    SELECT 1
    FROM novel_tags AS nt
    INNER JOIN tags AS t
        ON t.id = nt.tag_id
    WHERE nt.novel_id = n.id
      AND t.name = ?
);
```

Python:

```python id="w3n7q5"
rows = conn.execute(
    """
    SELECT
        n.id,
        n.title
    FROM novels AS n
    WHERE EXISTS (
        SELECT 1
        FROM novel_tags AS nt
        INNER JOIN tags AS t
            ON t.id = nt.tag_id
        WHERE nt.novel_id = n.id
          AND t.name = ?
    )
    """,
    ("Huyền Huyễn",),
).fetchall()
```

Đây là một query rất gần với Repository thực tế.

---

# 13. EXISTS vs JOIN

Cùng bài toán:

> Novel có Chapter hay không?

### JOIN

```sql id="w5c2k8"
SELECT DISTINCT
    n.id,
    n.title
FROM novels AS n
INNER JOIN chapters AS c
    ON c.novel_id = n.id;
```

Cần:

```sql id="y8m1q4"
DISTINCT
```

vì một Novel có nhiều Chapter.

### EXISTS

```sql id="k6p3r9"
SELECT
    n.id,
    n.title
FROM novels AS n
WHERE EXISTS (
    SELECT 1
    FROM chapters AS c
    WHERE c.novel_id = n.id
);
```

Không cần `DISTINCT`.

Đây là một ưu điểm lớn về **độ biểu đạt**.

Bạn không thực sự muốn:

> "Nối Novel với tất cả Chapter."

Bạn muốn:

> "Kiểm tra Novel này có Chapter hay không."

`EXISTS` thể hiện chính xác ý định đó.

---

# 14. JOIN và EXISTS khác nhau về bản chất

### JOIN

```text id="h7n2v5"
Tôi muốn DATA từ bảng liên quan.
```

Ví dụ:

```sql id="g9x4m1"
SELECT
    n.title,
    c.title
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id;
```

Bạn muốn:

```text id="0w6p3q"
Novel title
+
Chapter title
```

---

### EXISTS

```text id="m5k8r2"
Tôi chỉ muốn biết có bản ghi liên quan hay không.
```

Ví dụ:

```sql id="d3v7n9"
WHERE EXISTS (...)
```

Bạn không cần dữ liệu Chapter.

---

# 15. EXISTS có thể dừng khi tìm thấy match

Về mặt logic, `EXISTS` chỉ cần biết:

```text id="r2m6x8"
Có ít nhất 1 row?
```

Khi database có thể xác định được một row phù hợp, nó không cần quan tâm đến việc còn bao nhiêu row khác để trả về giá trị tồn tại.

Đây là một trong những lý do `EXISTS` rất phù hợp cho các phép kiểm tra tồn tại.

**Tuy nhiên:** đừng ghi nhớ quy tắc kiểu "EXISTS luôn nhanh hơn JOIN". Hiệu năng còn phụ thuộc vào query plan, index, dữ liệu và cấu trúc truy vấn.

Sau này khi học:

```text id="k7x2m4"
INDEX
EXPLAIN QUERY PLAN
```

chúng ta sẽ kiểm tra chuyện này bằng SQLite thực tế.

---

# 16. EXISTS + Python Repository

Ta có thể viết:

```python id="v4n8q2"
class NovelRepository:

    def __init__(self, conn):
        self._conn = conn

    def has_chapters(self, novel_id: int) -> bool:
        row = self._conn.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM chapters
                WHERE novel_id = ?
            ) AS has_chapters
            """,
            (novel_id,),
        ).fetchone()

        return bool(row["has_chapters"])
```

Đây là một kỹ thuật rất hay.

SQLite hỗ trợ:

```sql id="c8m1r6"
SELECT EXISTS (...);
```

Kết quả thường là:

```text id="q7v3n9"
1
```

hoặc:

```text id="s2x6m4"
0
```

Python:

```python id="h5k9p2"
bool(1)  # True
bool(0)  # False
```

---

# 17. Đây là pattern Repository rất đẹp

Thay vì:

```python id="u8m3q6"
chapters = chapter_repo.get_by_novel_id(novel_id)

if chapters:
    ...
```

ta có:

```python id="p4x7n1"
if novel_repo.has_chapters(novel_id):
    ...
```

Nếu nghiệp vụ chỉ cần biết:

```text id="q1m5v8"
Có hay không?
```

thì không cần lấy cả danh sách Chapter.

---

# 18. `SELECT EXISTS(...)` khác `WHERE EXISTS(...)`

Hai kiểu này cần phân biệt.

### Kiểu 1 — EXISTS trong WHERE

```sql id="x3m7q9"
SELECT
    n.id,
    n.title
FROM novels n
WHERE EXISTS (
    SELECT 1
    FROM chapters c
    WHERE c.novel_id = n.id
);
```

Mục đích:

> Lọc Novel.

---

### Kiểu 2 — EXISTS trong SELECT

```sql id="b8k2m5"
SELECT
    n.id,
    n.title,
    EXISTS (
        SELECT 1
        FROM chapters c
        WHERE c.novel_id = n.id
    ) AS has_chapters
FROM novels n;
```

Kết quả:

```text id="f6r9x2"
Tiên Nghịch | 1
Đấu Phá     | 1
Phàm Nhân   | 0
```

Cái này rất hữu ích cho dashboard.

---

# 19. Dashboard crawler

Ví dụ:

> Hiển thị Novel và trạng thái đã có chapter hay chưa.

```sql id="j5q8m3"
SELECT
    n.id,
    n.title,
    n.status,

    EXISTS (
        SELECT 1
        FROM chapters AS c
        WHERE c.novel_id = n.id
    ) AS has_chapters

FROM novels AS n
ORDER BY n.updated_at DESC;
```

Python:

```python id="w9x3k7"
rows = conn.execute(
    """
    SELECT
        n.id,
        n.title,
        n.status,
        EXISTS (
            SELECT 1
            FROM chapters AS c
            WHERE c.novel_id = n.id
        ) AS has_chapters
    FROM novels AS n
    ORDER BY n.updated_at DESC
    """
).fetchall()
```

UI có thể hiển thị:

```text id="e6m2q8"
Tiên Nghịch   ongoing   ✓
Đấu Phá       ongoing   ✓
Phàm Nhân     ongoing   ✗
```

---

# 20. EXISTS với trạng thái crawler

Giả sử Chapter có:

```text id="n7q3m1"
is_crawled
```

Ta muốn:

> Novel nào còn chapter chưa crawl?

```sql id="a4x8p2"
SELECT
    n.id,
    n.title
FROM novels AS n
WHERE EXISTS (
    SELECT 1
    FROM chapters AS c
    WHERE c.novel_id = n.id
      AND c.is_crawled = 0
);
```

Câu này rất gần với logic:

```text id="v5k9r3"
Crawler Worker
      ↓
tìm Novel
      ↓
còn chapter chưa crawl?
      ↓
EXISTS
      ↓
đưa vào queue
```

---

# 21. NOT EXISTS trong crawler

Ví dụ:

> Tìm Novel chưa có chapter nào.

```sql id="g2m7x4"
SELECT
    n.id,
    n.title
FROM novels AS n
WHERE NOT EXISTS (
    SELECT 1
    FROM chapters AS c
    WHERE c.novel_id = n.id
);
```

Crawler có thể dùng để:

```text id="z6p1n8"
Novel mới
   ↓
NOT EXISTS chapter
   ↓
cần crawl chapter
```

---

# 22. EXISTS vs LEFT JOIN IS NULL

Cùng bài toán:

> Novel không có Chapter.

### LEFT JOIN

```sql id="m3x7q9"
SELECT
    n.id,
    n.title
FROM novels n
LEFT JOIN chapters c
    ON c.novel_id = n.id
WHERE c.id IS NULL;
```

### NOT EXISTS

```sql id="r8k2v5"
SELECT
    n.id,
    n.title
FROM novels n
WHERE NOT EXISTS (
    SELECT 1
    FROM chapters c
    WHERE c.novel_id = n.id
);
```

Cả hai đều diễn đạt được:

```text id="q6m1x9"
Novel không có Chapter
```

Nhưng:

```text id="e7v3k8"
LEFT JOIN
→ tôi đang nối dữ liệu

NOT EXISTS
→ tôi đang kiểm tra không tồn tại
```

Nếu nghiệp vụ thực sự là **existence check**, `EXISTS/NOT EXISTS` thường rất dễ đọc.

---

# 23. Bộ ba cực kỳ quan trọng

Đến đây bạn đã học:

```text id="r5x8m2"
JOIN
IN
EXISTS
```

Hãy phân biệt:

### JOIN

```sql id="s3q7v9"
SELECT ...
FROM novels n
JOIN chapters c
    ON c.novel_id = n.id;
```

> Tôi muốn lấy dữ liệu từ hai bảng.

---

### IN

```sql id="h8m2x5"
WHERE n.id IN (
    SELECT c.novel_id
    FROM chapters c
);
```

> ID này có nằm trong tập ID kia không?

---

### EXISTS

```sql id="w4k9p1"
WHERE EXISTS (
    SELECT 1
    FROM chapters c
    WHERE c.novel_id = n.id
);
```

> Có tồn tại ít nhất một record liên quan không?

---

# 24. Một bảng so sánh

| Bài toán                         | Công cụ phù hợp                           |
| -------------------------------- | ----------------------------------------- |
| Lấy Novel + Chapter              | `JOIN`                                    |
| Lấy Novel + Tag                  | `JOIN`                                    |
| Kiểm tra ID thuộc tập nào        | `IN`                                      |
| Kiểm tra có Chapter              | `EXISTS`                                  |
| Kiểm tra không có Chapter        | `NOT EXISTS`                              |
| Lấy parent không có child        | `LEFT JOIN ... IS NULL` hoặc `NOT EXISTS` |
| Lấy dữ liệu từ bảng liên quan    | `JOIN`                                    |
| Chỉ cần TRUE/FALSE về sự tồn tại | `EXISTS`                                  |

---

# 25. Một quy tắc thực tế rất hữu ích

Khi đọc yêu cầu tiếng Việt:

### "Lấy thông tin..."

thường nghĩ đến:

```text id="x9m4q7"
JOIN
```

Ví dụ:

> Lấy tên Novel và tên Tag.

→ `JOIN`

---

### "Có ... không?"

nghĩ ngay đến:

```text id="c5v8n2"
EXISTS
```

Ví dụ:

> Novel này có chapter không?

→ `EXISTS`

---

### "Chưa có ..."

nghĩ ngay đến:

```text id="m7q2x6"
NOT EXISTS
```

Ví dụ:

> Novel nào chưa có chapter?

→ `NOT EXISTS`

Đây là một kỹ năng chuyển **ngôn ngữ nghiệp vụ → SQL** rất quan trọng.

---

# 26. Bài tập Buổi 23

## Bài 1

Viết query:

> Lấy tất cả Novel có ít nhất một Chapter.

Bắt buộc dùng:

```sql id="2x7m5q"
EXISTS
```

---

## Bài 2

Viết query:

> Lấy tất cả Novel chưa có Chapter.

Dùng:

```sql id="9k3v8p"
NOT EXISTS
```

---

## Bài 3

Viết query:

> Tìm Novel có Chapter `>= 1000`.

Dùng:

```sql id="f5m2x9"
EXISTS
```

---

## Bài 4

Viết query:

> Tìm Novel có Tag `"Huyền Huyễn"`.

Dùng:

```text id="r8q1m6"
EXISTS
+
novel_tags
+
tags
```

---

## Bài 5

Viết:

```python id="c7m3x8"
def has_chapters(self, novel_id: int) -> bool:
    ...
```

Yêu cầu SQL sử dụng:

```sql id="z2v6p9"
SELECT EXISTS (...)
```

---

## Bài 6 — So sánh

Viết 3 query cùng trả về Novel có Chapter:

```text id="u4m8q2"
1. INNER JOIN
2. IN + Subquery
3. EXISTS
```

Sau đó giải thích:

```text id="b6x1n9"
JOIN
IN
EXISTS
```

khác nhau về **ý nghĩa tư duy** như thế nào.

---

# 27. Chốt phần JOIN + Subquery + EXISTS

Bạn vừa hoàn thành một cụm kiến thức rất quan trọng:

```text id="t9m4x7"
14 FOREIGN KEY          ✅
15 One-to-One           ✅
16 One-to-Many          ✅
17 Many-to-Many         ✅
18 JOIN                 ✅
19 INNER JOIN           ✅
20 LEFT JOIN            ✅
21 JOIN nhiều bảng      ✅
22 Subquery             ✅
23 EXISTS               ✅
```

Mental model hiện tại:

```text
                    SQL
                     │
          ┌──────────┼──────────┐
          ↓          ↓          ↓
        JOIN       Subquery   EXISTS
          │          │          │
      lấy data    tạo tập     kiểm tra
      liên quan   kết quả     tồn tại
```

Đặc biệt hãy nhớ:

```text id="k8m2q5"
JOIN
→ "Tôi cần dữ liệu liên quan."

IN
→ "Giá trị này có thuộc tập kia?"

EXISTS
→ "Có ít nhất một record thỏa điều kiện?"

NOT EXISTS
→ "Không có record nào thỏa điều kiện?"
```

---

# Tiếp theo: Phần IV — SQLite Deep Dive

```text id="p4x7m1"
24 SQLite Type Affinity
25 Constraints Deep Dive
26 PRAGMA
27 Transaction Deep Dive
28 WAL
29 Locking & Concurrency
30 SQLite Performance
```

**Buổi 24 — SQLite Type Affinity** sẽ bắt đầu phần SQLite chuyên sâu. Đây là lúc chúng ta đi sâu hơn vào câu hỏi:

> **Tại sao SQLite nói một column là `INTEGER`, `TEXT`, `REAL`... nhưng lại không hoạt động giống PostgreSQL/MySQL về kiểu dữ liệu?**

Ta sẽ học `storage class`, `type affinity`, implicit conversion và những tình huống dễ gây bug khi thiết kế schema cho app Python.
