# Dataclass Deep Dive — Buổi 14

# Recursive Dataclass — Dataclass đệ quy

Hôm nay chúng ta học một trong những ứng dụng mạnh nhất của `dataclass`:

> **Một dataclass có thể chứa chính nó, trực tiếp hoặc gián tiếp.**

Điều này rất quan trọng khi mô hình hóa:

* Tree
* AST
* Filesystem
* Category
* Menu
* Organization
* Dependency graph
* Comment tree
* Novel category tree

Đặc biệt với crawler framework của bạn, cấu trúc:

```text
Category
├── Fantasy
│   ├── Magic
│   └── Adventure
├── Romance
└── Action
```

là một recursive structure điển hình.

---

# 1. Recursive Dataclass là gì?

Ví dụ đơn giản nhất:

```python
from dataclasses import dataclass


@dataclass
class Node:
    value: int
    children: list["Node"]
```

`Node` chứa:

```text
Node
 └── Node[]
```

và mỗi `Node` lại có thể chứa:

```text
Node
 └── Node
      └── Node
           └── ...
```

Đó chính là recursion.

---

# 2. Vì sao cần `"Node"`?

Nếu viết:

```python
@dataclass
class Node:
    value: int
    children: list[Node]
```

Python có thể gặp vấn đề vì tại thời điểm class body đang được thực thi:

```text
class Node:
    ...
```

thì tên:

```text
Node
```

chưa hoàn toàn được bind.

Do đó dùng forward reference:

```python
list["Node"]
```

---

# 3. `from __future__ import annotations`

Python hiện đại cho phép:

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Node:
    value: int
    children: list[Node]
```

Đây là cách rất đẹp để viết recursive dataclass.

Type annotation không được eager evaluate theo cách cũ mà được trì hoãn dưới dạng annotation representation.

---

# 4. Forward Reference là gì?

Forward reference nghĩa là:

> Type được tham chiếu trước khi nó được định nghĩa hoàn chỉnh.

Ví dụ:

```python
class Employee:
    manager: "Employee | None"
```

`Employee` đang tham chiếu đến chính nó.

Hoặc:

```python
class Category:
    parent: "Category | None"
```

Đây là self-reference.

---

# 5. Recursive Dataclass cơ bản

Ta xây một tree:

```python
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Node:
    value: int
    children: list[Node] = field(
        default_factory=list
    )
```

Tạo node:

```python
root = Node(1)
```

Thêm child:

```python
root.children.append(
    Node(2)
)

root.children.append(
    Node(3)
)
```

Cây:

```text
    1
   / \
  2   3
```

---

# 6. Tree sâu hơn

```python
root = Node(1)

node2 = Node(2)
node3 = Node(3)

node2.children.append(
    Node(4)
)

node2.children.append(
    Node(5)
)

root.children.extend(
    [node2, node3]
)
```

Cây:

```text
       1
      / \
     2   3
    / \
   4   5
```

---

# 7. Recursive Dataclass chính là Object Graph

Hãy nhìn dưới góc độ memory:

```text
root
 │
 ▼
Node(1)
 │
 ├───────► Node(2)
 │          │
 │          ├──► Node(4)
 │          └──► Node(5)
 │
 └───────► Node(3)
```

Mỗi `children` là một reference tới object khác.

Đây là lý do cần phân biệt:

```text
tree structure
```

với:

```text
memory/reference graph
```

---

# 8. Tree traversal

Recursive dataclass thường đi cùng recursive algorithm.

Ví dụ depth-first traversal:

```python
def traverse(node: Node):
    print(node.value)

    for child in node.children:
        traverse(child)
```

Chạy:

```python
traverse(root)
```

Kết quả:

```text
1
2
4
5
3
```

Đây là:

> DFS — Depth First Search.

---

# 9. Vì sao recursion tự nhiên với tree?

Tree có định nghĩa recursive:

```text
Tree
=
Node
+
zero or more Trees
```

Nên class:

```python
Node
```

chứa:

```python
list[Node]
```

là một representation rất tự nhiên.

Algorithm cũng recursive:

```text
process(Node)
    ↓
process(children)
    ↓
process(children)
    ↓
...
```

---

# 10. Computed Property

Ta có thể thêm:

```python
@dataclass
class Node:
    value: int
    children: list[Node] = field(
        default_factory=list
    )

    @property
    def is_leaf(self) -> bool:
        return not self.children
```

Node:

```python
Node(1)
```

là leaf:

```python
node.is_leaf
```

→ `True`.

---

# 11. `depth`

Ta có thể tính depth:

```python
@dataclass
class Node:
    value: int
    children: list[Node] = field(
        default_factory=list
    )

    def depth(self) -> int:
        if not self.children:
            return 0

        return 1 + max(
            child.depth()
            for child in self.children
        )
```

Tree:

```text
       1
      / \
     2   3
    / \
   4   5
```

thì:

```python
root.depth()
```

→ `2`.

---

# 12. `size`

Recursive computation:

```python
def size(self) -> int:
    return 1 + sum(
        child.size()
        for child in self.children
    )
```

Tree:

```text
       1
      / \
     2   3
    / \
   4   5
```

có:

```text
5 nodes
```

---

# 13. Recursive Search

Ví dụ tìm node:

```python
def find(
    self,
    value: int
) -> Node | None:

    if self.value == value:
        return self

    for child in self.children:
        result = child.find(value)

        if result is not None:
            return result

    return None
```

Dùng:

```python
node = root.find(5)
```

---

# 14. Recursive Validation

Ví dụ không cho phép node có giá trị âm:

```python
def validate(self):
    if self.value < 0:
        raise ValueError(
            "value cannot be negative"
        )

    for child in self.children:
        child.validate()
```

Ta có:

```text
root.validate()
```

và validation chạy toàn bộ tree.

---

# 15. Recursive `__post_init__()`

Có thể validation ngay khi tạo:

```python
@dataclass
class Node:
    value: int
    children: list[Node] = field(
        default_factory=list
    )

    def __post_init__(self):
        if self.value < 0:
            raise ValueError(
                "value cannot be negative"
            )
```

Nhưng lưu ý:

> `__post_init__()` chỉ validate node hiện tại.

Nó không tự động recurse vào `children`.

Nếu muốn:

```python
def __post_init__(self):
    if self.value < 0:
        raise ValueError(...)

    for child in self.children:
        child.validate()
```

---

# 16. Parent → Child

Một tree có thể chỉ lưu:

```text
parent
 ↓
children
```

Ví dụ:

```python
@dataclass
class Node:
    value: int
    children: list[Node] = field(
        default_factory=list
    )
```

Đây là:

> One-way relationship.

---

# 17. Child → Parent

Đôi khi muốn child biết parent:

```python
@dataclass
class Node:
    value: int
    parent: Node | None = None
    children: list[Node] = field(
        default_factory=list
    )
```

Bây giờ:

```text
       Node
      /    \
 parent   children
```

Nhưng nếu:

```python
root.children.append(child)
child.parent = root
```

ta có reference hai chiều:

```text
root ─────► child
 ▲           │
 └───────────┘
```

Đây là **circular reference graph**.

---

# 18. Circular Reference không phải lúc nào cũng xấu

Ví dụ filesystem:

```text
Directory
    └── File
```

File có thể cần biết directory cha:

```python
file.parent
```

Trong trường hợp đó parent reference có ý nghĩa.

Nhưng circular reference làm:

* serialization khó hơn
* `repr()` phức tạp hơn
* equality cần cẩn thận
* traversal cần tránh loop

---

# 19. Một lỗi rất dễ gặp

Ví dụ:

```python
@dataclass
class Node:
    value: int
    parent: Node | None = None
    children: list[Node] = field(
        default_factory=list
    )
```

Sau đó:

```python
root.children.append(child)
child.parent = root
```

Nếu bạn serialize naïvely:

```text
root
 ↓
child
 ↓
parent
 ↓
root
 ↓
child
 ↓
...
```

sẽ xảy ra infinite recursion.

---

# 20. Vì vậy cần phân biệt Tree và Graph

Tree:

```text
       A
      / \
     B   C
```

Graph:

```text
A ─── B
│   ╱ │
│ ╱   │
C ─── D
```

Tree thường:

```text
mỗi node có một parent
```

Graph có thể:

```text
nhiều path
cycle
shared nodes
```

Recursive dataclass có thể biểu diễn cả hai, nhưng algorithm phải khác.

---

# 21. Parent Reference nên dùng `field()`

Ví dụ:

```python
@dataclass
class Node:
    value: int

    parent: Node | None = field(
        default=None,
        repr=False,
        compare=False
    )

    children: list[Node] = field(
        default_factory=list
    )
```

Tại sao:

```python
repr=False
```

?

Để tránh `repr()` đi sâu qua:

```text
parent
 → children
 → parent
 → ...
```

---

# 22. `compare=False`

Nếu parent tham gia equality:

```python
node1 == node2
```

Python có thể đi theo graph.

Trong cấu trúc circular:

```text
A
 ↕
B
```

việc recursive equality có thể trở nên phức tạp.

Do đó parent reference thường không nên tham gia value equality:

```python
compare=False
```

---

# 23. `repr=False` + `compare=False`

Một pattern thường thấy:

```python
parent: Node | None = field(
    default=None,
    repr=False,
    compare=False
)
```

Ý nghĩa:

```text
parent
├── không xuất hiện trong repr
└── không tham gia equality
```

Đây là một kỹ thuật rất hữu ích khi model hóa tree.

---

# 24. `weakref` cho Parent

Trong một số thiết kế, parent không cần giữ object sống.

Có thể dùng:

```python
weakref.ref
```

để tránh strong reference cycle.

Ví dụ conceptually:

```python
parent_ref = weakref.ref(parent)
```

Khi đó:

```python
parent_ref()
```

trả về parent nếu object vẫn tồn tại.

Đây là phần memory-management nâng cao, nhưng rất đáng biết.

---

# 25. Recursive Dataclass cho Filesystem

Một ứng dụng rất tự nhiên:

```python
@dataclass
class File:
    name: str
    size: int
```

```python
@dataclass
class Directory:
    name: str
    files: list[File] = field(
        default_factory=list
    )
    directories: list[Directory] = field(
        default_factory=list
    )
```

Cấu trúc:

```text
root/
├── a.txt
├── b.txt
├── src/
│   ├── main.py
│   └── utils.py
└── tests/
    └── test.py
```

map thành:

```text
Directory
├── File
├── File
├── Directory
│   ├── File
│   └── File
└── Directory
    └── File
```

---

# 26. Recursive Dataclass cho Category

Đây là ứng dụng rất phù hợp với crawler.

```python
@dataclass
class Category:
    name: str
    children: list[Category] = field(
        default_factory=list
    )
```

Cây:

```text
Truyện
├── Tiên hiệp
│   ├── Tu tiên
│   └── Huyền huyễn
├── Ngôn tình
│   ├── Hiện đại
│   └── Cổ đại
└── Kiếm hiệp
```

---

# 27. Category với Parent

Nếu cần đi ngược:

```python
@dataclass
class Category:
    name: str

    parent: Category | None = field(
        default=None,
        repr=False,
        compare=False
    )

    children: list[Category] = field(
        default_factory=list
    )
```

Thêm child bằng method:

```python
def add_child(
    self,
    child: Category
) -> None:

    child.parent = self
    self.children.append(child)
```

Đây là cách tốt hơn:

```python
child.parent = parent
parent.children.append(child)
```

rải rác khắp application.

---

# 28. Bảo vệ invariant

Method:

```python
def add_child(
    self,
    child: Category
) -> None:

    if child.parent is not None:
        raise ValueError(
            "Child already belongs to a parent"
        )

    child.parent = self
    self.children.append(child)
```

Bây giờ object đảm bảo:

```text
child.parent == parent
```

và:

```text
child ∈ parent.children
```

---

# 29. Đây là Domain Behavior

Dataclass không nhất thiết chỉ là:

```text
data holder
```

Nó có thể chứa behavior liên quan trực tiếp đến state.

Ví dụ:

```python
category.add_child(child)
category.remove_child(child)
category.find("Fantasy")
category.depth()
```

Đây là một domain object thực sự.

---

# 30. Recursive Property — Full Path

Category:

```python
@dataclass
class Category:
    name: str
    parent: Category | None = field(
        default=None,
        repr=False,
        compare=False
    )

    @property
    def path(self) -> str:

        if self.parent is None:
            return self.name

        return (
            f"{self.parent.path}"
            f" / {self.name}"
        )
```

Ví dụ:

```text
Truyện
  ↓
Tiên hiệp
  ↓
Huyền huyễn
```

thì:

```python
category.path
```

→

```text
Truyện / Tiên hiệp / Huyền huyễn
```

Đây là recursive computation.

---

# 31. Recursive Serialization

Nếu không có parent:

```python
from dataclasses import asdict

asdict(root)
```

có thể recursively chuyển:

```text
Node
 ↓
children
 ↓
Node
 ↓
children
```

thành nested dict/list.

Nhưng nếu có:

```text
parent
```

và:

```text
children
```

thì graph trở thành cyclic.

`asdict()` không phải công cụ serialize arbitrary cyclic graph.

Đây là điểm cực kỳ quan trọng.

---

# 32. Tree Serialization nên chủ động thiết kế

Ví dụ:

```python
def to_dict(node: Node) -> dict:
    return {
        "value": node.value,
        "children": [
            to_dict(child)
            for child in node.children
        ]
    }
```

Không serialize `parent`.

Kết quả:

```json
{
    "value": 1,
    "children": [
        {
            "value": 2,
            "children": []
        }
    ]
}
```

Đây là một pattern rất tốt.

---

# 33. Recursive Dataclass và JSON

Có thể:

```python
import json

data = to_dict(root)

text = json.dumps(data)
```

Điểm quan trọng:

> Không phải `dataclass` nào cũng có thể `json.dumps()` trực tiếp.

Phải có serialization strategy.

Phần Serialization sẽ được học sâu từ **Buổi 21–24**.

---

# 34. AST — Abstract Syntax Tree

Recursive dataclass cực kỳ phù hợp để biểu diễn AST.

Ví dụ expression:

```text
1 + 2 * 3
```

có thể thành:

```text
       +
      / \
     1   *
        / \
       2   3
```

Ta có:

```python
@dataclass
class Number:
    value: int
```

```python
@dataclass
class BinaryOp:
    operator: str
    left: Number | BinaryOp
    right: Number | BinaryOp
```

Nhưng type union sẽ nhanh chóng phức tạp.

Đây là lúc recursive typing trở nên quan trọng.

---

# 35. AST tốt hơn với Base Node

```python
from dataclasses import dataclass


@dataclass
class Expr:
    pass
```

```python
@dataclass
class Number(Expr):
    value: int
```

```python
@dataclass
class BinaryOp(Expr):
    operator: str
    left: Expr
    right: Expr
```

Bây giờ:

```text
Expr
├── Number
└── BinaryOp
    ├── Expr
    └── Expr
```

Đây là sự kết hợp:

```text
Inheritance
+
Composition
+
Recursion
```

rất mạnh.

---

# 36. AST example

Expression:

```text
1 + 2
```

thành:

```python
expr = BinaryOp(
    operator="+",
    left=Number(1),
    right=Number(2)
)
```

Object graph:

```text
BinaryOp("+")
├── Number(1)
└── Number(2)
```

Expression:

```text
1 + 2 * 3
```

có thể:

```python
expr = BinaryOp(
    "+",
    Number(1),
    BinaryOp(
        "*",
        Number(2),
        Number(3)
    )
)
```

---

# 37. Recursive Visitor

Ta có thể traverse AST:

```python
def evaluate(expr: Expr) -> int:

    if isinstance(expr, Number):
        return expr.value

    if isinstance(expr, BinaryOp):
        left = evaluate(expr.left)
        right = evaluate(expr.right)

        if expr.operator == "+":
            return left + right

        if expr.operator == "*":
            return left * right

        raise ValueError(
            f"Unknown operator: {expr.operator}"
        )

    raise TypeError(
        f"Unknown expression: {type(expr)}"
    )
```

Sau đó:

```python
evaluate(expr)
```

→ `7`.

---

# 38. Recursive Dataclass + Inheritance

Đây là pattern cực kỳ quan trọng:

```text
Expr
│
├── Number
│
└── BinaryOp
      │
      ├── Expr
      └── Expr
```

Nó kết hợp chính xác những gì chúng ta đã học:

### Buổi 11

Inheritance.

### Buổi 12

MRO / multiple inheritance.

### Buổi 13

Composition.

### Buổi 14

Recursion.

---

# 39. Recursive Dataclass và `repr`

Dataclass tự động tạo:

```python
__repr__()
```

cho nested object.

Tree:

```text
Node(
    value=1,
    children=[
        Node(
            value=2,
            children=[]
        )
    ]
)
```

Điều này rất tiện.

Nhưng với tree quá sâu:

```text
Node
 ↓
Node
 ↓
Node
 ↓
...
```

repr có thể rất dài.

Với cyclic graph:

```text
A
↕
B
```

cần đặc biệt cẩn thận.

---

# 40. Recursive Depth và Recursion Limit

Python có recursion limit:

```python
import sys

print(sys.getrecursionlimit())
```

Thường khoảng vài nghìn call stack, nhưng giá trị cụ thể phụ thuộc runtime.

Tree rất sâu:

```text
Node
 ↓
Node
 ↓
Node
 ↓
...
```

có thể gây:

```text
RecursionError
```

---

# 41. Khi nào nên dùng iterative traversal?

Nếu tree rất sâu, thay:

```python
def traverse(node):
    for child in node.children:
        traverse(child)
```

bằng stack:

```python
def traverse(root: Node):

    stack = [root]

    while stack:

        node = stack.pop()

        print(node.value)

        stack.extend(
            reversed(node.children)
        )
```

Không phụ thuộc sâu vào Python call stack.

---

# 42. BFS

Nếu muốn duyệt theo level:

```python
from collections import deque


def bfs(root: Node):

    queue = deque([root])

    while queue:

        node = queue.popleft()

        print(node.value)

        queue.extend(
            node.children
        )
```

Tree:

```text
       1
      / \
     2   3
    / \
   4   5
```

BFS:

```text
1
2
3
4
5
```

---

# 43. Tree API chuyên nghiệp

Một `Node` có thể cung cấp:

```python
@dataclass
class Node:
    value: int
    children: list[Node] = field(
        default_factory=list
    )

    def add_child(
        self,
        child: Node
    ) -> None:
        ...

    def remove_child(
        self,
        child: Node
    ) -> None:
        ...

    def find(
        self,
        value: int
    ) -> Node | None:
        ...

    def depth(self) -> int:
        ...

    def size(self) -> int:
        ...

    def walk(self):
        ...
```

Đây đã gần trở thành một mini domain framework.

---

# 44. Áp dụng vào Crawler — Category Tree

Thiết kế:

```python
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Category:

    name: str

    parent: Category | None = field(
        default=None,
        repr=False,
        compare=False
    )

    children: list[Category] = field(
        default_factory=list
    )

    def add_child(
        self,
        child: Category
    ) -> None:

        if child.parent is not None:
            raise ValueError(
                "Category already has parent"
            )

        child.parent = self
        self.children.append(child)
```

---

# 45. Thêm `path`

```python
@property
def path(self) -> str:

    if self.parent is None:
        return self.name

    return (
        f"{self.parent.path}"
        f" / {self.name}"
    )
```

Ví dụ:

```python
root = Category("Truyện")

fantasy = Category("Tiên hiệp")
magic = Category("Huyền huyễn")

root.add_child(fantasy)
fantasy.add_child(magic)
```

Sau đó:

```python
print(magic.path)
```

→

```text
Truyện / Tiên hiệp / Huyền huyễn
```

---

# 46. Phát hiện Cycle

Với parent-child mutable tree, người dùng có thể vô tình:

```text
A
 ↓
B
 ↓
C
 ↓
A
```

Nếu `add_child()` không kiểm tra, tree biến thành cycle.

Có thể kiểm tra:

```python
def is_ancestor(
    self,
    node: Category
) -> bool:

    current = self

    while current is not None:

        if current is node:
            return True

        current = current.parent

    return False
```

Sau đó:

```python
def add_child(
    self,
    child: Category
) -> None:

    if child is self:
        raise ValueError(
            "Cannot add itself"
        )

    if child.is_ancestor(self):
        raise ValueError(
            "Would create cycle"
        )

    child.parent = self
    self.children.append(child)
```

Đây là domain invariant rất quan trọng.

---

# 47. Recursive Dataclass không chỉ là Tree

Một số cấu trúc khác:

### Filesystem

```text
Directory
└── Directory
```

### AST

```text
Expr
└── Expr
```

### Organization

```text
Department
└── Department
```

### Comment

```text
Comment
└── replies[]
```

### Menu

```text
MenuItem
└── children[]
```

### Category

```text
Category
└── children[]
```

---

# 48. Một vấn đề lớn: Shared Nodes

Tree chuẩn:

```text
        A
       / \
      B   C
```

B chỉ thuộc A.

Nhưng graph:

```text
      A
     / \
    B   C
     \ /
      D
```

D được reference từ B và C.

Nếu model:

```python
children: list[Node]
```

vẫn được, nhưng đây không còn là strict tree.

Khi đó cần suy nghĩ theo:

> **Graph model**

chứ không chỉ tree.

---

# 49. Identity trong Recursive Structure

Hai node có cùng data:

```python
a = Node(1)
b = Node(1)
```

nhưng:

```python
a is b
```

→ `False`

và:

```python
a == b
```

→ `True`

nếu children giống nhau.

Đây lại là sự khác biệt:

```text
identity
vs
value equality
```

rất quan trọng khi làm graph.

---

# 50. `compare=False` và Graph Identity

Trong graph domain, đôi khi muốn equality dựa trên:

```text
node.id
```

thay vì toàn bộ recursive structure.

Ví dụ:

```python
@dataclass
class Node:
    id: int
    name: str
    children: list[Node] = field(
        default_factory=list,
        compare=False
    )
```

Khi đó equality không recurse vào children.

Đây thường là lựa chọn tốt cho entity graph lớn.

---

# 51. Entity vs Value Object

Đây là một điểm rất quan trọng đối với hướng DDD.

### Value Object

Equality theo giá trị:

```text
Address(
    city="HCM"
)
```

Hai Address giống nhau:

```text
== True
```

### Entity

Identity quan trọng:

```text
Category(
    id=123
)
```

Hai object cùng `id` có thể đại diện cùng entity.

Trong recursive graph, quyết định equality semantics rất quan trọng.

---

# 52. Recursive Dataclass + ID

Ví dụ:

```python
@dataclass
class Category:
    id: int
    name: str

    parent: Category | None = field(
        default=None,
        repr=False,
        compare=False
    )

    children: list[Category] = field(
        default_factory=list,
        compare=False
    )
```

Ở đây:

```text
id
name
```

có thể là phần equality.

Còn:

```text
parent
children
```

không tham gia.

Điều này tránh recursive equality.

---

# 53. Một thiết kế hoàn chỉnh cho crawler Category

```python
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Category:

    id: int
    name: str

    parent: Category | None = field(
        default=None,
        repr=False,
        compare=False
    )

    children: list[Category] = field(
        default_factory=list,
        compare=False
    )

    def __post_init__(self):

        if self.id <= 0:
            raise ValueError(
                "id must be positive"
            )

        if not self.name.strip():
            raise ValueError(
                "name cannot be empty"
            )

        self.name = self.name.strip()

    def add_child(
        self,
        child: Category
    ) -> None:

        if child is self:
            raise ValueError(
                "Cannot add itself"
            )

        if child.parent is not None:
            raise ValueError(
                "Child already has parent"
            )

        current = self

        while current is not None:

            if current is child:
                raise ValueError(
                    "Would create cycle"
                )

            current = current.parent

        child.parent = self
        self.children.append(child)

    @property
    def path(self) -> str:

        if self.parent is None:
            return self.name

        return (
            f"{self.parent.path}"
            f" / {self.name}"
        )
```

Đây đã là một **domain object tương đối hoàn chỉnh**.

---

# 54. Sử dụng

```python
root = Category(
    1,
    "Truyện"
)

fantasy = Category(
    2,
    "Tiên hiệp"
)

magic = Category(
    3,
    "Huyền huyễn"
)

root.add_child(fantasy)
fantasy.add_child(magic)
```

Sau đó:

```python
print(magic.path)
```

Kết quả:

```text
Truyện / Tiên hiệp / Huyền huyễn
```

---

# 55. Điều gì xảy ra trong memory?

Ta có:

```text
root
 │
 ▼
Category(1)
 │
 └──────────────► Category(2)
                   │
                   └──────────► Category(3)
```

Nhưng vì child có parent:

```text
Category(1) ◄──────── Category(2)
     │                    │
     └──────────────────► Category(3)
```

thực tế là graph có reference hai chiều.

Python garbage collector có thể xử lý cyclic references, nhưng thiết kế vẫn phải cẩn thận khi:

* serialize
* copy
* compare
* traverse
* debug

---

# 56. `copy.deepcopy()` với recursive object

Với graph phức tạp:

```python
from copy import deepcopy

clone = deepcopy(root)
```

Python cố gắng giữ cấu trúc reference tương ứng trong bản copy.

Nhưng với domain object phức tạp, đừng mặc định rằng `deepcopy()` luôn là chiến lược copy tốt nhất.

Nhiều khi nên tạo:

```python
clone()
```

hoặc:

```python
from_dict()
```

một cách explicit.

---

# 57. Recursive Dataclass và Performance

Recursive structure có chi phí:

```text
Node
Node
Node
Node
...
```

Mỗi node là một Python object.

Nếu có:

```text
1,000,000 nodes
```

thì overhead object có thể rất đáng kể.

Đây sẽ liên quan trực tiếp tới:

> **Buổi 26 — Memory Layout, GC, slots, cache locality**

---

# 58. `slots=True` cho Recursive Nodes

Có thể:

```python
@dataclass(slots=True)
class Node:
    value: int
    children: list[Node] = field(
        default_factory=list
    )
```

Điều này có thể giảm per-instance memory overhead.

Nhưng cần benchmark trước khi kết luận rằng nó luôn nhanh hơn.

---

# 59. Recursive Tree và `slots`

Một million node tree có thể rất khác biệt về memory giữa:

```python
@dataclass
class Node:
    ...
```

và:

```python
@dataclass(slots=True)
class Node:
    ...
```

Đây là lý do recursive data structure thường là một use case tốt để benchmark `slots`.

---

# 60. Bài tập thực hành

## Bài 1 — Tree cơ bản

Viết:

```python
@dataclass
class Node:
    value: int
    children: list[Node]
```

Implement:

```python
size()
depth()
find()
```

---

## Bài 2 — Category Tree

Implement:

```python
Category
```

có:

```text
id
name
parent
children
```

và:

```python
add_child()
remove_child()
find()
path
depth
```

---

## Bài 3 — Cycle Detection

Đảm bảo không thể:

```text
A
 ↓
B
 ↓
C
 ↓
A
```

---

## Bài 4 — Recursive Serialization

Viết:

```python
def category_to_dict(
    category: Category
) -> dict:
    ...
```

Không serialize:

```text
parent
```

chỉ serialize:

```text
id
name
children
```

---

## Bài 5 — Filesystem

Thiết kế:

```text
Directory
├── files[]
└── directories[]
```

Implement:

```python
total_size()
find_file()
walk()
```

---

## Bài 6 — AST

Thiết kế:

```text
Expr
├── Number
└── BinaryOp
```

Implement:

```python
evaluate()
```

cho:

```text
1 + 2 * 3
```

---

# 61. Những điều cần nhớ

### 1. Self-reference

```python
children: list["Node"]
```

hoặc:

```python
from __future__ import annotations

children: list[Node]
```

---

### 2. Mutable collection

Luôn:

```python
field(default_factory=list)
```

không:

```python
children = []
```

---

### 3. Parent reference

Nếu cần:

```python
parent: Node | None
```

thường cân nhắc:

```python
repr=False
compare=False
```

---

### 4. Tree ≠ Graph

Tree:

```text
mỗi node có một parent
```

Graph:

```text
có thể shared node
có thể cycle
```

---

### 5. Recursive algorithm

Tree thường đi cùng:

```text
DFS
BFS
recursive traversal
```

---

### 6. Recursive serialization

Không nên blindly serialize graph có cycle.

---

### 7. Identity vs Equality

Trong graph/domain model, phải quyết định rõ:

```text
== dựa trên value?
```

hay:

```text
== dựa trên identity?
```

---

# 62. Kết nối với các buổi trước

Chúng ta đã đi qua một chuỗi rất quan trọng:

```text
Buổi 11
Inheritance
      ↓
Buổi 12
Multiple Inheritance + MRO
      ↓
Buổi 13
Composition
      ↓
Buổi 14
Recursive Dataclass
```

Bây giờ bạn đã có thể xây một domain graph như:

```text
                  Novel
                /   |   \
               /    |    \
          Author  Category  Image
                    |
                    ├── Category
                    │      └── Category
                    │
                    └── Category

Novel
 └── chapters[]
       ├── Chapter
       ├── Chapter
       └── Chapter
```

Đây chính là nền tảng rất tốt cho crawler framework.

---

# Roadmap sau Buổi 14

```text
Phần II — Advanced

11. Inheritance                  ✅
12. Multiple Inheritance + MRO   ✅
13. Composition                  ✅
14. Recursive Dataclass          ✅
15. Generic Dataclass            ← tiếp theo
16. Abstract Dataclass
17. Protocols
18. Descriptors
19. Metaclass + Dataclass
20. Dynamic Dataclass
```

## Buổi 15 — Generic Dataclass

Chúng ta sẽ đi sâu vào:

```python
T = TypeVar("T")

@dataclass
class Box(Generic[T]):
    value: T
```

và xây các abstraction như:

```text
Box[T]
Result[T]
Response[T]
Page[T]
Repository[T]
Cache[T]
```

Sau đó kết hợp:

```text
Generic
+
Dataclass
+
TypeVar
+
Generic[T]
+
Type checking
+
Inheritance
+
Composition
```

Đây là phần rất quan trọng nếu mục tiêu của bạn là xây **framework crawler có typing chuyên nghiệp**.
