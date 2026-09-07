# Buổi 12 — `DISTINCT` trong SQL + SQLite + Python

Hôm nay chúng ta học:

```sql
DISTINCT
```

Đây là một keyword đơn giản nhưng cực kỳ hay dùng trong các query thực tế.

---

# 1. `DISTINCT` dùng để làm gì?

`DISTINCT` dùng để:

> **Loại bỏ các dòng kết quả bị trùng nhau.**

Ví dụ bảng:

```text id="f9c0e4"
novels

id | source
---+--------
1  | site_a
2  | site_a
3  | site_b
4  | site_a
5  | site_c
6  | site_b
```

Nếu:

```sql id="8y2y0k"
SELECT source
FROM novels;
```

Kết quả:

```text id="y4f3n6"
site_a
site_a
site_b
site_a
site_c
site_b
```

Có duplicate.

Dùng:

```sql id="9g3f3n"
SELECT DISTINCT source
FROM novels;
```

Kết quả:

```text id="j3k5kg"
site_a
site_b
site_c
```

---

# 2. Mental Model

Hãy nhớ:

```text id="y7x6ak"
SELECT
    ↓
DISTINCT
    ↓
loại kết quả trùng
```

Ví dụ:

```sql id="b42v3g"
SELECT DISTINCT source
FROM novels;
```

Có thể đọc:

> Lấy danh sách `source`, nhưng mỗi source chỉ xuất hiện một lần.

---

# 3. `DISTINCT` không xóa dữ liệu trong database

Đây là điểm rất quan trọng.

```sql id="6m58te"
SELECT DISTINCT source
FROM novels;
```

**Không hề xóa duplicate khỏi bảng.**

Nó chỉ loại duplicate trong **result set**.

Database vẫn:

```text id="9z0nwt"
site_a
site_a
site_b
site_a
site_c
site_b
```

Không thay đổi gì.

---

# 4. `DISTINCT` với một column

Đây là trường hợp phổ biến nhất.

### Danh sách status

```sql id="1bsgs2"
SELECT DISTINCT status
FROM novels;
```

Kết quả:

```text id="y8u1qg"
ongoing
completed
```

### Danh sách source

```sql id="o3ml7j"
SELECT DISTINCT source
FROM novels;
```

### Danh sách author

```sql id="2o1h3h"
SELECT DISTINCT author
FROM novels;
```

---

# 5. `DISTINCT` + `ORDER BY`

Rất thường dùng:

```sql id="s3dz3u"
SELECT DISTINCT source
FROM novels
ORDER BY source;
```

Kết quả:

```text id="e3msx5"
site_a
site_b
site_c
```

Có thể giảm dần:

```sql id="flw7zq"
SELECT DISTINCT source
FROM novels
ORDER BY source DESC;
```

---

# 6. `DISTINCT` + `WHERE`

Hoàn toàn có thể kết hợp.

Ví dụ:

> Những source đang có novel ongoing.

```sql id="y9d1b5"
SELECT DISTINCT source
FROM novels
WHERE status = 'ongoing';
```

Logic:

```text id="j3x2d0"
novels
   ↓
WHERE status = ongoing
   ↓
lấy source
   ↓
DISTINCT
   ↓
loại duplicate
```

---

# 7. `DISTINCT` trên nhiều column

Đây là phần rất quan trọng.

Ta có:

```text id="07z5uh"
source   | status
---------+----------
site_a   | ongoing
site_a   | ongoing
site_a   | completed
site_b   | ongoing
site_b   | ongoing
```

Query:

```sql id="w1x4g5"
SELECT DISTINCT
    source,
    status
FROM novels;
```

Kết quả:

```text id="6k2y7f"
site_a   ongoing
site_a   completed
site_b   ongoing
```

`DISTINCT` xét **toàn bộ tổ hợp column**.

Tức là:

```text id="y9krzj"
(source, status)
```

chứ không phải từng column độc lập.

---

# 8. Hiểu sâu `DISTINCT` nhiều column

Ví dụ:

```text id="7h3k7q"
source   status
-------  --------
A        X
A        X
A        Y
B        X
```

Sau:

```sql id="l1f6kn"
SELECT DISTINCT source, status
```

ta có:

```text id="y7n7o0"
A X
A Y
B X
```

Vì:

```text id="d3d2jq"
(A, X)
```

bị lặp.

Nhưng:

```text id="rj1q2p"
(A, Y)
```

khác:

```text id="8c6ycc"
(A, X)
```

nên vẫn giữ.

---

# 9. `DISTINCT` và `NULL`

Một điểm thú vị.

Giả sử:

```text id="4xwz9c"
author
------
Nhĩ Căn
NULL
Nhĩ Căn
NULL
Thần Đông
```

Query:

```sql id="j9cq3z"
SELECT DISTINCT author
FROM novels;
```

Kết quả có thể:

```text id="p9v8fq"
NULL
Nhĩ Căn
Thần Đông
```

Các `NULL` được xem như cùng một giá trị trong kết quả DISTINCT.

---

# 10. `DISTINCT` + `COUNT`

Đây là pattern **cực kỳ quan trọng**.

Ví dụ:

> Có bao nhiêu source khác nhau?

Không phải:

```sql id="xqf9y5"
SELECT COUNT(*)
FROM novels;
```

Cái này đếm **novel**.

Ta cần:

```sql id="7t7pko"
SELECT COUNT(DISTINCT source)
FROM novels;
```

Ví dụ:

```text id="8i5w6d"
5 novel
3 source
```

Kết quả:

```text id="7u4c90"
3
```

---

# 11. `COUNT(*)` vs `COUNT(DISTINCT column)`

Đây là kiến thức nên thuộc.

### Đếm số row

```sql id="hrxjtk"
SELECT COUNT(*)
FROM novels;
```

→ Có bao nhiêu novel?

### Đếm số source khác nhau

```sql id="7vgt3g"
SELECT COUNT(DISTINCT source)
FROM novels;
```

→ Có bao nhiêu source khác nhau?

### Đếm số author khác nhau

```sql id="wy4t4w"
SELECT COUNT(DISTINCT author)
FROM novels;
```

→ Có bao nhiêu author khác nhau?

---

# 12. `COUNT(DISTINCT ...)` và `NULL`

Cẩn thận:

```sql id="k7jz0b"
COUNT(DISTINCT author)
```

không đếm `NULL`.

Ví dụ:

```text id="7s4q6h"
author
------
A
A
B
NULL
NULL
```

```sql id="2j8q9q"
SELECT COUNT(DISTINCT author)
FROM novels;
```

Kết quả:

```text id="k5k0o4"
2
```

Vì:

```text id="v7y5uw"
A
B
```

là hai author khác nhau.

---

# 13. `DISTINCT` không giống `GROUP BY`

Hai query:

```sql id="y8f9ex"
SELECT DISTINCT source
FROM novels;
```

và:

```sql id="7t3kcs"
SELECT source
FROM novels
GROUP BY source;
```

Trong trường hợp đơn giản này có thể cho kết quả giống nhau.

Nhưng ý nghĩa tư duy khác nhau.

### `DISTINCT`

> Tôi muốn **loại duplicate**.

### `GROUP BY`

> Tôi muốn **chia thành group để aggregate / phân tích**.

Ví dụ:

```sql id="yn0k8c"
SELECT
    source,
    COUNT(*)
FROM novels
GROUP BY source;
```

`GROUP BY` có ý nghĩa rõ ràng.

Còn:

```sql id="i1cx8k"
SELECT DISTINCT source
FROM novels;
```

chỉ cần danh sách unique.

---

# 14. Khi nào nên dùng `DISTINCT`?

Nếu yêu cầu là:

> Liệt kê các giá trị duy nhất.

→ `DISTINCT`

Ví dụ:

```text id="7kqjqt"
Danh sách source
Danh sách status
Danh sách author
Danh sách category
Danh sách tag
```

---

Nếu yêu cầu:

> Thống kê từng nhóm.

→ `GROUP BY`

Ví dụ:

```text id="cz0p1o"
Mỗi source có bao nhiêu novel?
Mỗi author có bao nhiêu novel?
Mỗi status có bao nhiêu novel?
```

---

# 15. `DISTINCT` trong app crawler

Giả sử crawler có nhiều novel:

```text id="7c3v4s"
source
------
truyenfull
truyenfull
truyenfull
metruyenchu
metruyenchu
blogtruyen
```

Muốn hiển thị combobox:

```text id="9u7w4k"
Source:
[ truyenfull ]
[ metruyenchu ]
[ blogtruyen ]
```

Query:

```sql id="2v0z2d"
SELECT DISTINCT source
FROM novels
ORDER BY source;
```

Python:

```python id="w8k7dz"
rows = conn.execute(
    """
    SELECT DISTINCT source
    FROM novels
    ORDER BY source
    """
).fetchall()

sources = [
    row["source"]
    for row in rows
]
```

Kết quả:

```python id="y3b9s1"
[
    "blogtruyen",
    "metruyenchu",
    "truyenfull",
]
```

---

# 16. Repository

Có thể encapsulate query:

```python id="9b8r4w"
class NovelRepository:

    def get_sources(self) -> list[str]:
        rows = self._conn.execute(
            """
            SELECT DISTINCT source
            FROM novels
            WHERE source IS NOT NULL
            ORDER BY source
            """
        ).fetchall()

        return [
            row["source"]
            for row in rows
        ]
```

Application chỉ cần:

```python id="t8g0c8"
sources = repo.get_sources()
```

Không cần biết SQL bên dưới.

---

# 17. `DISTINCT` + `LIMIT`

Ví dụ:

> Lấy 10 author khác nhau đầu tiên.

```sql id="z1zz0e"
SELECT DISTINCT author
FROM novels
WHERE author IS NOT NULL
ORDER BY author
LIMIT 10;
```

Lưu ý:

```text id="j5q0x4"
DISTINCT
   ↓
ORDER BY
   ↓
LIMIT
```

Ta đang lấy **10 giá trị unique**, không phải 10 row ban đầu.

---

# 18. `DISTINCT` + `LIKE`

Ví dụ:

> Các author khác nhau có tên chứa "Đường".

```sql id="t9w3i8"
SELECT DISTINCT author
FROM novels
WHERE author LIKE ?
ORDER BY author;
```

Python:

```python id="0r9gsl"
keyword = "Đường"

rows = conn.execute(
    """
    SELECT DISTINCT author
    FROM novels
    WHERE author LIKE ?
    ORDER BY author
    """,
    (f"%{keyword}%",),
).fetchall()
```

---

# 19. `DISTINCT` trong Query Model

Nếu UI cần:

```text
SourceFilter
```

thì database query có thể trả về:

```text id="9x7d3j"
source
------
site_a
site_b
site_c
```

Không cần load toàn bộ novels rồi dùng Python:

```python id="2r9fda"
set(...)
```

Nếu dữ liệu nằm trong database, hãy cân nhắc để database xử lý:

```sql id="x4p0p0"
SELECT DISTINCT source
FROM novels;
```

Đây là tư duy:

> **Đẩy công việc phù hợp xuống database.**

---

# 20. `DISTINCT` vs Python `set`

Bạn có thể làm:

```python id="7n4w6f"
rows = conn.execute(
    "SELECT source FROM novels"
).fetchall()

sources = {
    row["source"]
    for row in rows
}
```

Nhưng cách này phải:

```text id="g7z2h5"
SQLite
  ↓
load toàn bộ rows
  ↓
Python
  ↓
set()
```

Trong khi:

```sql id="x1u2g9"
SELECT DISTINCT source
FROM novels;
```

cho phép:

```text id="2r0w0h"
SQLite
  ↓
DISTINCT
  ↓
chỉ trả kết quả cần thiết
  ↓
Python
```

Đặc biệt khi bảng lớn, cách thứ hai thường hợp lý hơn.

---

# 21. Một lỗi tư duy phổ biến

Người mới thấy:

```sql id="w0g5q4"
SELECT DISTINCT source, title
FROM novels;
```

và nghĩ:

> “Tôi lấy source unique và title unique.”

Không phải.

`DISTINCT` áp dụng cho **cả tổ hợp**:

```text id="l3u0ai"
(source, title)
```

Ví dụ:

```text id="l5x5v6"
A | Novel 1
A | Novel 1
A | Novel 2
```

sẽ thành:

```text id="2r0k6v"
A | Novel 1
A | Novel 2
```

---

# 22. `DISTINCT` + Aggregate + GROUP BY

Ta có thể kết hợp cả ba.

Ví dụ database có:

```text
source
author
```

Muốn:

> Mỗi source có bao nhiêu author khác nhau?

```sql id="g3b3qo"
SELECT
    source,
    COUNT(DISTINCT author) AS unique_authors
FROM novels
GROUP BY source;
```

Ví dụ:

```text id="j5q4vi"
source    unique_authors
--------  --------------
site_a    20
site_b    15
site_c    8
```

Đây là query rất mạnh.

Tư duy:

```text id="i3yq7h"
GROUP BY source
       ↓
mỗi source là một group
       ↓
COUNT(DISTINCT author)
       ↓
đếm author unique trong từng group
```

---

# 23. Ví dụ nâng cao hơn cho crawler

Muốn biết:

> Mỗi source có bao nhiêu author khác nhau và tổng số novel?

```sql id="3n6m4k"
SELECT
    source,
    COUNT(*) AS total_novels,
    COUNT(DISTINCT author) AS unique_authors
FROM novels
GROUP BY source
ORDER BY total_novels DESC;
```

Kết quả:

```text id="gd8q4p"
source    total_novels    unique_authors
--------  -------------   --------------
site_a    120             40
site_b    85              31
site_c    43              19
```

Đây là kiểu query bắt đầu rất hữu ích cho dashboard crawler.

---

# 24. Python hoàn chỉnh

Ví dụ:

```python id="5z8z1p"
import sqlite3


def get_source_statistics(
    conn: sqlite3.Connection,
) -> list[sqlite3.Row]:

    cursor = conn.execute(
        """
        SELECT
            source,
            COUNT(*) AS total_novels,
            COUNT(DISTINCT author) AS unique_authors
        FROM novels
        GROUP BY source
        ORDER BY total_novels DESC
        """
    )

    return cursor.fetchall()
```

Sử dụng:

```python id="cb3y4q"
rows = get_source_statistics(conn)

for row in rows:
    print(
        row["source"],
        row["total_novels"],
        row["unique_authors"],
    )
```

---

# 25. Tổng kết `DISTINCT`

Bạn nên nhớ 5 pattern này:

### ① Unique values

```sql id="bmyvda"
SELECT DISTINCT source
FROM novels;
```

### ② Unique + filter

```sql id="yy4g9s"
SELECT DISTINCT source
FROM novels
WHERE status = 'ongoing';
```

### ③ Đếm unique

```sql id="q4p3z1"
SELECT COUNT(DISTINCT source)
FROM novels;
```

### ④ Unique nhiều column

```sql id="crj5jo"
SELECT DISTINCT source, status
FROM novels;
```

### ⑤ Unique aggregate trong group

```sql id="82a3gk"
SELECT
    source,
    COUNT(DISTINCT author)
FROM novels
GROUP BY source;
```

---

# 26. Bài tập Buổi 12

Giả sử:

```text id="5v3gsy"
novels

id
source
title
author
status
chapter_count
```

### Bài 1

Lấy danh sách `source` không trùng.

---

### Bài 2

Lấy danh sách `author` không trùng.

Nhưng bỏ `NULL`.

---

### Bài 3

Đếm có bao nhiêu source khác nhau.

---

### Bài 4

Đếm có bao nhiêu author khác nhau.

---

### Bài 5

Lấy danh sách source khác nhau của các novel:

```text id="r1g3gc"
status = 'ongoing'
```

---

### Bài 6

Lấy danh sách tổ hợp:

```text id="h4m2o8"
source + status
```

không trùng.

---

### Bài 7

Tính:

```text id="7b4y8a"
mỗi source
    ↓
có bao nhiêu author khác nhau
```

---

### Bài 8 — kết hợp kiến thức

Tìm các source có:

```text id="d7j0de"
ít nhất 10 author khác nhau
```

Gợi ý:

```sql id="3a4z5f"
GROUP BY
COUNT(DISTINCT ...)
HAVING
```

---

# 27. Bài tập Python

Viết:

```python id="4kj5g8"
def get_sources(
    conn: sqlite3.Connection,
) -> list[str]:
    ...
```

Yêu cầu:

```text
site_a
site_b
site_c
```

không trùng và được sắp xếp alphabet.

Sau đó viết:

```python id="w4n8q6"
def count_unique_authors(
    conn: sqlite3.Connection,
) -> int:
    ...
```

---

# 28. Mental Model cuối buổi

```text id="q9z8hc"
DISTINCT
   │
   ├── SELECT DISTINCT source
   │        ↓
   │      unique source
   │
   ├── COUNT(DISTINCT source)
   │        ↓
   │      số source unique
   │
   └── COUNT(DISTINCT author)
            ↓
          số author unique
```

Và phân biệt:

```text id="x7f4kd"
DISTINCT
   ↓
loại duplicate

GROUP BY
   ↓
chia thành group

HAVING
   ↓
lọc group
```

---

## Roadmap

```text
7   Operators                    ✅
8   AND / OR / NOT               ✅
9   COUNT / SUM / AVG / MIN/MAX  ✅
10  GROUP BY                     ✅
11  HAVING                       ✅
12  DISTINCT                     ← hôm nay
13  CASE WHEN
```

**Buổi 13 — `CASE WHEN`** sẽ rất thú vị: chúng ta sẽ học cách để SQL thực hiện logic kiểu:

```text
chapter_count >= 2000 → "long"
chapter_count >= 1000 → "medium"
chapter_count < 1000  → "short"
```

và dùng nó để tạo **computed category**, thống kê trạng thái, phân loại novel và xây các query phục vụ dashboard.
