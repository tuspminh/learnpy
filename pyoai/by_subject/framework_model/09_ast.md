# Buổi 9 — Expression Tree & SQL AST Deep Dive

> Đây là buổi đánh dấu sự chuyển mình từ một **Query Builder đơn giản** sang một **ORM Engine** thực sự.

Đến buổi trước, chúng ta lưu điều kiện như:

```python
.where(title="ABC")
```

↓

```python
[
    "title=?",
    "author=?"
]
```

Thiết kế này hoạt động, nhưng có rất nhiều hạn chế.

Sau buổi này, toàn bộ câu SQL sẽ được biểu diễn dưới dạng **AST (Abstract Syntax Tree)**.

Đây là kỹ thuật được sử dụng trong:

* SQLAlchemy Core
* Django ORM
* LINQ (.NET)
* Compiler (Python, C++, Java...)

---

# Mục tiêu

Sau buổi này bạn sẽ xây dựng được kiến trúc:

```text
Novel.query()

      │

      ▼

Expression Tree

      │

      ▼

SQL Compiler

      │

      ▼

SQL + Params

      │

      ▼

DatabaseManager
```

Đây là kiến trúc mà hầu hết ORM chuyên nghiệp đều áp dụng.

---

# Vì sao cần AST?

Hiện tại

```python
.where(
    title="ABC"
)
```

chỉ lưu

```python
"title=?"
```

Nếu muốn

```sql
title LIKE ?
```

thì sao?

---

Hoặc

```sql
rating > ?
```

---

Hoặc

```sql
(title=? OR author=?)
```

---

Hoặc

```sql
NOT (...)
```

---

Hoặc

```sql
EXISTS (...)
```

---

Càng ngày càng khó.

Giải pháp

↓

Mọi điều kiện đều là Object.

---

# Ý tưởng

Không lưu

```text
"title=?"
```

Mà lưu

```text
ComparisonExpression
```

---

Ví dụ

```text
title

=

ABC
```

↓

Object

```text
ComparisonExpression

├── left

├── operator

└── right
```

---

# AST là gì?

Ví dụ

```sql
title='ABC'
```

không còn là string.

Mà là

```text
          =
        /   \
   title    ABC
```

Đó gọi là cây biểu thức.

---

# Expression Base

Ta bắt đầu

```python
class Expression:

    pass
```

Mọi biểu thức đều kế thừa.

---

Ví dụ

```text
Expression

├── Column

├── Value

├── Comparison

├── Logical

├── Function

├── Alias

└── Order
```

---

# Column

Biểu diễn

```sql
title
```

---

```python
class Column(Expression):

    def __init__(

        self,

        name

    ):

        self.name = name
```

---

Ví dụ

```python
Column("title")
```

↓

```text
title
```

---

# Value

Biểu diễn

```text
ABC
```

---

```python
Value(
    "ABC"
)
```

---

Tại sao?

Vì

```sql
ABC
```

không nên nối vào SQL.

Nó phải trở thành

```sql
?
```

và

params.

---

# ComparisonExpression

Ví dụ

```sql
title='ABC'
```

↓

```python
ComparisonExpression(

    Column("title"),

    "=",

    Value("ABC")

)
```

---

Cấu trúc

```text
Comparison

├── left

├── operator

└── right
```

---

# LogicalExpression

Ví dụ

```sql
title='A'

AND

author='B'
```

↓

```text
        AND
       /   \
     expr  expr
```

---

Object

```python
LogicalExpression(

    left,

    "AND",

    right

)
```

---

Có thể lồng nhau.

---

Ví dụ

```sql
(

A

AND

B

)

OR

C
```

↓

```text
          OR
        /     \
      AND      C
     /   \
    A     B
```

Đó chính là AST.

---

# FunctionExpression

Ví dụ

```sql
COUNT(*)
```

↓

```python
FunctionExpression(

    "COUNT",

    "*"

)
```

---

Hay

```sql
MAX(rating)
```

↓

```python
FunctionExpression(

    "MAX",

    Column("rating")
)
```

---

# AliasExpression

Ví dụ

```sql
COUNT(*)

AS

total
```

↓

```python
AliasExpression(

    expr,

    "total"

)
```

---

# OrderExpression

Ví dụ

```sql
ORDER BY

updated_at DESC
```

↓

```python
OrderExpression(

    Column("updated_at"),

    desc=True
)
```

---

# JoinExpression

Ví dụ

```sql
INNER JOIN author

ON

novel.author_id=author.id
```

↓

```text
JoinExpression

table

condition
```

---

# QueryBuilder thay đổi

Thay vì

```python
self.where.append(

"title=?"
)
```

↓

```python
self.where.append(

ComparisonExpression(...)
)
```

---

Ví dụ

```python
.where(

title="ABC"
)
```

↓

```python
ComparisonExpression(

Column("title"),

"=",

Value("ABC")

)
```

---

# SQL Compiler

Builder

↓

AST

↓

Compiler

↓

SQL

---

Ví dụ

```python
compile(

ComparisonExpression(...)
)
```

↓

```sql
title=?
```

---

Params

↓

```python
["ABC"]
```

---

# Compile Column

```python
Column(

"title"

)
```

↓

```text
title
```

---

# Compile Value

```python
Value(

"ABC"

)
```

↓

SQL

```text
?
```

↓

Params

```python
ABC
```

---

# Compile Comparison

AST

↓

```text
title

=

?
```

↓

Params

```text
ABC
```

---

# Compile Logical

Ví dụ

```text
AND
```

↓

```sql
(

left

AND

right

)
```

---

Compiler gọi đệ quy.

```python
compile(

left

)

compile(

right
)
```

---

# Đệ quy

Đây là điểm mạnh.

Ví dụ

```text
OR

↓

AND

↓

Comparison
```

Compiler không cần biết sâu bao nhiêu.

Nó chỉ

↓

compile node.

---

# AST lớn

Ví dụ

```sql
(

rating>8

AND

author='A'

)

OR

status='done'
```

↓

```text
             OR

        /          \

      AND        status

    /     \

rating    author
```

Compiler chỉ đi từ trên xuống.

---

# Tách Compiler

Không để QueryBuilder compile.

Ta tạo

```python
SQLCompiler
```

---

Kiến trúc

```text
QueryBuilder

↓

AST

↓

SQLCompiler

↓

SQL
```

Rất sạch.

---

# Hỗ trợ nhiều Database

SQLite

↓

CompilerSQLite

---

PostgreSQL

↓

CompilerPostgres

---

MySQL

↓

CompilerMySQL

---

Builder không đổi.

Chỉ thay Compiler.

Đây là kiến trúc của SQLAlchemy Core.

---

# Visitor Pattern

Compiler thực ra là

Visitor Pattern.

Ví dụ

```python
visit_column()

visit_value()

visit_compare()

visit_join()
```

Không dùng

```python
if isinstance(...)
```

quá nhiều.

---

# Expression Factory

API

```python
.where(

title="ABC"
)
```

↓

Factory

↓

```python
Comparison(...)
```

Builder không cần biết cách tạo.

---

# Tối ưu AST

Ví dụ

```sql
A

AND

TRUE
```

↓

Compiler có thể tối ưu

↓

```text
A
```

---

Hoặc

```sql
A

OR

FALSE
```

↓

```text
A
```

Đó gọi là

Expression Optimization.

---

# Kiến trúc ORM sau Buổi 9

```text
Application

      │

      ▼

QueryBuilder

      │

      ▼

Expression Tree

      │

      ▼

SQL Compiler

      │

      ▼

SQL + Params

      │

      ▼

DatabaseManager

      │

      ▼

SQLite
```

---

# Áp dụng cho Framework Cào Truyện

Ví dụ

```python
Novel.query() \
.where(status="completed") \
.where("rating", ">", 8) \
.where_like("title", "%đấu%") \
.order_by("updated_at", desc=True) \
.limit(20)
```

Sau khi xây AST

↓

```text
WHERE

      AND

   /        \

 status     AND

          /      \

     rating      title
```

↓

Compiler

↓

SQL.

---

# Cấu trúc thư mục mới

```text
orm/

    expressions/

        base.py

        column.py

        value.py

        comparison.py

        logical.py

        function.py

        alias.py

        order.py

        join.py

    compiler/

        sqlite.py

        postgres.py

        mysql.py

    query/

        builder.py

        factory.py
```

Đây là kiến trúc rất dễ mở rộng khi số lượng biểu thức tăng lên.

---

# Bài tập thực hành

## Bài 1

Xây dựng hệ phân cấp:

```text
Expression
    ├── Column
    ├── Value
    ├── ComparisonExpression
    ├── LogicalExpression
    ├── FunctionExpression
    ├── AliasExpression
    └── OrderExpression
```

---

## Bài 2

Viết `SQLCompiler` hỗ trợ:

* `Column`
* `Value`
* `ComparisonExpression`

và trả về:

* SQL
* Danh sách `params`

---

## Bài 3

Thêm hỗ trợ `LogicalExpression` (`AND`, `OR`) bằng cách biên dịch đệ quy.

---

## Bài 4

Tạo `ExpressionFactory` để `QueryBuilder.where()` chỉ việc gọi:

```python
ExpressionFactory.comparison(
    "title",
    "=",
    "ABC"
)
```

---

## Bài 5

Tách Compiler thành các lớp:

```text
BaseCompiler
SQLiteCompiler
```

để chuẩn bị hỗ trợ nhiều hệ quản trị cơ sở dữ liệu trong tương lai.

---

# Buổi tiếp theo

**Buổi 10 — Identity Map & Unit of Work Deep Dive**

Đây là một trong những thành phần quan trọng nhất của ORM chuyên nghiệp. Chúng ta sẽ xây dựng:

* **Identity Map**: Trong một phiên làm việc (session), mỗi bản ghi trong database chỉ tương ứng với **một đối tượng Model duy nhất** trong bộ nhớ.
* **Unit of Work**: Theo dõi toàn bộ đối tượng mới, đã sửa và đã xóa, sau đó đồng bộ tất cả thay đổi xuống database trong một transaction.

Sau buổi này, framework của bạn sẽ có nền tảng để quản lý trạng thái đối tượng hiệu quả, giảm truy vấn trùng lặp và đảm bảo tính nhất quán dữ liệu khi thực hiện nhiều thao tác cùng lúc.
