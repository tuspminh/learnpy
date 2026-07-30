# Iterator Deep Dive — Buổi 9

# Xây dựng Iterator cho Tree (Cây dữ liệu)

Đây là một trong những buổi quan trọng nhất của khóa học.

Sau buổi này, bạn sẽ hiểu:

  * Vì sao Tree khó hơn List 
  * Cách thiết kế Tree Iterator đúng chuẩn Python 
  * DFS Iterator 
  * BFS Iterator 
  * Preorder, Inorder, Postorder 
  * Lazy Tree Traversal 
  * Đây cũng là nền tảng của AST (Abstract Syntax Tree), HTML DOM, XML, JSON Parser... 



* * *

# Roadmap

Đã học

  * ✅ Buổi 1–8 



Hôm nay

  * ✅ Buổi 9 — Tree Iterator 



Tiếp theo

  * Buổi 10 — Linked List Iterator 
  * Buổi 11 — Iterator vô hạn 



* * *

# Tree là gì?

Khác với List
    
    
    [10,20,30]

Tree có dạng
    
    
            A
          / | \
         B  C  D
        / \    |
       E   F   G

Mỗi node có thể có:

  * 0 con 
  * 1 con 
  * nhiều con 



Đây là lý do Tree khó Iterator hơn List.

* * *

# Định nghĩa Node

Ta xây dựng Tree đơn giản.
    
    
    class Node:
    
        def __init__(self, value):
            self.value = value
            self.children = []
    
        def add(self, child):
            self.children.append(child)

Ví dụ
    
    
    root = Node("A")
    
    b = Node("B")
    c = Node("C")
    d = Node("D")
    
    root.add(b)
    root.add(c)
    root.add(d)

Ta được
    
    
    A
    ├── B
    ├── C
    └── D

* * *

# Thêm nhiều tầng
    
    
    e = Node("E")
    f = Node("F")
    g = Node("G")
    
    b.add(e)
    b.add(f)
    
    d.add(g)

Tree
    
    
            A
          / | \
         B  C  D
        / \    |
       E   F   G

* * *

# Iterator sẽ đi như thế nào?

Đây là câu hỏi đầu tiên.

Tree có nhiều cách duyệt.

Ví dụ

## DFS
    
    
    A
    
    ↓
    
    B
    
    ↓
    
    E
    
    ↓
    
    F
    
    ↓
    
    C
    
    ↓
    
    D
    
    ↓
    
    G

* * *

## BFS
    
    
    A
    
    ↓
    
    B
    
    ↓
    
    C
    
    ↓
    
    D
    
    ↓
    
    E
    
    ↓
    
    F
    
    ↓
    
    G

Khác hoàn toàn.

* * *

# DFS là gì?

DFS

Depth First Search

Đi sâu trước.

Ví dụ
    
    
            A
          / | \
         B  C  D
        / \
       E   F

DFS
    
    
    A
    
    ↓
    
    B
    
    ↓
    
    E
    
    ↓
    
    F
    
    ↓
    
    C
    
    ↓
    
    D

* * *

# Ý tưởng

Muốn đi DFS

ta cần
    
    
    Stack

* * *

# Stack

Ban đầu
    
    
    [A]

Pop
    
    
    A

Push
    
    
    D
    C
    B

Stack
    
    
    [D C B]

Pop
    
    
    B

Push
    
    
    F
    E

Stack
    
    
    [D C F E]

...

* * *

# Vì sao push ngược?

Nếu push
    
    
    B
    C
    D

Stack
    
    
    Top
    
    D
    C
    B

sẽ lấy
    
    
    D

trước.

Không đúng.

Muốn
    
    
    B

được lấy trước

ta phải push
    
    
    D
    C
    B

* * *

# DFS Iterator
    
    
    class DFSIterator:
    
        def __init__(self, root):
            self.stack = [root]
    
        def __iter__(self):
            return self
    
        def __next__(self):
    
            if not self.stack:
                raise StopIteration
    
            node = self.stack.pop()
    
            for child in reversed(node.children):
                self.stack.append(child)
    
            return node

Đây là một Iterator đúng chuẩn.

* * *

# Tree Collection
    
    
    class Tree:
    
        def __init__(self, root):
            self.root = root
    
        def __iter__(self):
            return DFSIterator(self.root)

* * *

# Sử dụng
    
    
    tree = Tree(root)
    
    for node in tree:
        print(node.value)

Kết quả
    
    
    A
    B
    E
    F
    C
    D
    G

Đúng DFS.

* * *

# Minh họa Stack

Ban đầu
    
    
    [A]

Sau A
    
    
    [D C B]

Sau B
    
    
    [D C F E]

Sau E
    
    
    [D C F]

Sau F
    
    
    [D C]

Sau C
    
    
    [D]

Sau D
    
    
    [G]

* * *

# BFS Iterator

BFS dùng
    
    
    Queue

không dùng Stack.

* * *

Ý tưởng
    
    
    Queue
    
    ↓
    
    FIFO

* * *

Ban đầu
    
    
    [A]

Lấy
    
    
    A

Đưa vào
    
    
    B
    
    C
    
    D

Queue
    
    
    B C D

Sau
    
    
    B

↓
    
    
    C D E F

* * *

# BFS Iterator
    
    
    from collections import deque
    
    class BFSIterator:
    
        def __init__(self, root):
            self.queue = deque([root])
    
        def __iter__(self):
            return self
    
        def __next__(self):
    
            if not self.queue:
                raise StopIteration
    
            node = self.queue.popleft()
    
            for child in node.children:
                self.queue.append(child)
    
            return node

* * *

# Collection
    
    
    class BFSTree:
    
        def __init__(self, root):
            self.root = root
    
        def __iter__(self):
            return BFSIterator(self.root)

* * *

Kết quả
    
    
    A
    
    B
    
    C
    
    D
    
    E
    
    F
    
    G

* * *

# So sánh DFS và BFS

Tree
    
    
            A
          / | \
         B  C  D
        / \
       E   F

DFS
    
    
    A
    
    B
    
    E
    
    F
    
    C
    
    D

* * *

BFS
    
    
    A
    
    B
    
    C
    
    D
    
    E
    
    F

* * *

# Thiết kế chuyên nghiệp

Thay vì
    
    
    tree = Tree(root)

ta có thể
    
    
    tree.dfs()
    
    tree.bfs()
    
    
    class Tree:
    
        def __init__(self, root):
            self.root = root
    
        def dfs(self):
            return DFSIterator(self.root)
    
        def bfs(self):
            return BFSIterator(self.root)
    
        def __iter__(self):
            return self.dfs()

Lúc này
    
    
    for node in tree:

mặc định

↓

DFS

* * *

# Lazy Traversal

Điều cực kỳ hay là
    
    
    next(iterator)

chỉ duyệt
    
    
    1 node

Ví dụ
    
    
    it = tree.dfs()
    
    print(next(it).value)

↓
    
    
    A

Tree chưa duyệt hết.

* * *

Tiếp
    
    
    print(next(it).value)

↓
    
    
    B

Chưa duyệt tiếp.

Đây chính là
    
    
    Lazy Traversal

* * *

# Ứng dụng thực tế

## HTML
    
    
    <html>
    
    <body>
    
    <div>
    
    <p>Hello</p>
    
    </div>
    
    </body>
    
    </html>

BeautifulSoup duyệt
    
    
    DOM Tree

bằng Iterator.

* * *

## pathlib
    
    
    Path(".")
    
    .rglob("*")

Trả về Iterator duyệt cây thư mục.

* * *

## JSON
    
    
    {
     "user":{
       "address":{
          "city":"HCM"
       }
     }
    }

JSON parser cũng duyệt một cây.

* * *

## AST
    
    
    a = b + c * d

Python tạo
    
    
    Abstract Syntax Tree

rồi duyệt Tree.

* * *

# Ví dụ hoàn chỉnh
    
    
    from collections import deque
    
    
    class Node:
    
        def __init__(self, value):
            self.value = value
            self.children = []
    
        def add(self, child):
            self.children.append(child)
    
    
    class DFSIterator:
    
        def __init__(self, root):
            self.stack = [root]
    
        def __iter__(self):
            return self
    
        def __next__(self):
    
            if not self.stack:
                raise StopIteration
    
            node = self.stack.pop()
    
            for child in reversed(node.children):
                self.stack.append(child)
    
            return node
    
    
    class Tree:
    
        def __init__(self, root):
            self.root = root
    
        def __iter__(self):
            return DFSIterator(self.root)
    
    
    root = Node("A")
    
    b = Node("B")
    c = Node("C")
    d = Node("D")
    e = Node("E")
    f = Node("F")
    g = Node("G")
    
    root.add(b)
    root.add(c)
    root.add(d)
    
    b.add(e)
    b.add(f)
    
    d.add(g)
    
    tree = Tree(root)
    
    for node in tree:
        print(node.value)

Kết quả
    
    
    A
    B
    E
    F
    C
    D
    G

* * *

# Kiến thức nâng cao: Binary Tree

Ví dụ trên là **N-ary Tree** (mỗi node có nhiều con).

Với **Binary Tree** , ngoài DFS còn có ba cách duyệt kinh điển:
    
    
            A
           / \
          B   C
         / \
        D   E

### Preorder (Node → Left → Right)
    
    
    A B D E C

### Inorder (Left → Node → Right)
    
    
    D B E A C

### Postorder (Left → Right → Node)
    
    
    D E B C A

Ba kiểu duyệt này rất quan trọng trong:

  * Trình biên dịch (Compiler) 
  * Biểu thức toán học 
  * Cây tìm kiếm nhị phân (BST) 
  * Cây AVL, Red-Black Tree 



Chúng ta sẽ quay lại khi học về cấu trúc dữ liệu chuyên sâu.

* * *

# Tổng kết buổi 9

Bạn cần nhớ:

  * **Tree** không có một cách duyệt duy nhất. 
  * **DFS** thường dùng **Stack**. 
  * **BFS** thường dùng **Queue (`collections.deque`)**. 
  * `Tree` nên là **Iterable** , còn `DFSIterator` và `BFSIterator` là **Iterator**. 
  * Iterator giúp duyệt cây theo kiểu **lazy** , mỗi lần chỉ xử lý một node. 
  * Đây là nền tảng cho nhiều thư viện và framework như DOM parser, AST, `pathlib`, ORM, và các cấu trúc dữ liệu phức tạp. 



* * *

# Bài tập

## Bài 1

Viết `DFSIterator` nhưng trả về `node.value` thay vì trả về cả `Node`.

* * *

## Bài 2

Thêm phương thức:
    
    
    tree.bfs()

để có thể:
    
    
    for node in tree.bfs():
        print(node.value)

* * *

## Bài 3

Viết lớp:
    
    
    class FilterIterator:

Nhận vào:

  * một `Tree Iterator`
  * một hàm điều kiện (`predicate`) 



Chỉ trả về các node thỏa điều kiện.

Ví dụ:
    
    
    for node in FilterIterator(tree.dfs(), lambda n: n.value in {"B", "E", "G"}):
        print(node.value)

Kết quả:
    
    
    B
    E
    G

Đây là bước đầu tiên để xây dựng các **Iterator có thể kết hợp (Composable Iterators)** , nền tảng của `itertools`, `filter()`, `map()`, và nhiều thư viện xử lý dữ liệu trong Python.

