# Iterator Deep Dive — Buổi 10

# Xây dựng Iterator cho Linked List

Đây là buổi học rất quan trọng vì Linked List là cấu trúc dữ liệu **không hỗ trợ truy cập ngẫu nhiên** (random access) như `list`. Điều đó khiến cách xây dựng Iterator khác hoàn toàn.

Sau buổi này bạn sẽ hiểu:

  * Iterator hoạt động trên Linked List như thế nào 
  * Vì sao Linked List không cần `index`
  * Cách xây dựng Forward Iterator 
  * Cách xây dựng Doubly Linked List Iterator 
  * Reverse Iterator 
  * Sentinel Node 
  * Cách các thư viện C++, Java và Python thiết kế Iterator cho Linked List 



* * *

# Roadmap

Đã học

  * ✅ Buổi 1 — Iterator 
  * ✅ Buổi 2 — Iterable 
  * ✅ Buổi 3 — Iterator Protocol 
  * ✅ Buổi 4 — for Loop 
  * ✅ Buổi 5 — iter() 
  * ✅ Buổi 6 — next() 
  * ✅ Buổi 7 — Viết Iterator đầu tiên 
  * ✅ Buổi 8 — Iterator cho File 
  * ✅ Buổi 9 — Iterator cho Tree 



Hôm nay

  * ✅ Buổi 10 — Iterator cho Linked List 



Tiếp theo

  * Buổi 11 — Iterator vô hạn 



* * *

# Linked List khác List ở đâu?

List
    
    
    +----+----+----+----+
    | 10 | 20 | 30 | 40 |
    +----+----+----+----+
       0    1    2    3

Muốn lấy phần tử thứ 3
    
    
    numbers[3]

Python nhảy thẳng tới vị trí đó.

* * *

Linked List
    
    
    10 --> 20 --> 30 --> 40 --> None

Muốn tới `40`

phải đi
    
    
    10
    
    ↓
    
    20
    
    ↓
    
    30
    
    ↓
    
    40

Không thể nhảy trực tiếp.

* * *

# Node

Ta bắt đầu từ Node.
    
    
    class Node:
    
        def __init__(self, value):
            self.value = value
            self.next = None

* * *

# Linked List
    
    
    class LinkedList:
    
        def __init__(self):
            self.head = None

Ban đầu
    
    
    head
    
    ↓
    
    None

* * *

# Thêm phần tử
    
    
    class LinkedList:
    
        def __init__(self):
            self.head = None
    
        def append(self, value):
    
            node = Node(value)
    
            if self.head is None:
                self.head = node
                return
    
            current = self.head
    
            while current.next:
                current = current.next
    
            current.next = node

* * *

# Thử
    
    
    ll = LinkedList()
    
    ll.append(10)
    ll.append(20)
    ll.append(30)

Ta được
    
    
    head
    
    ↓
    
    10 → 20 → 30 → None

* * *

# Iterator sẽ hoạt động ra sao?

Với List

Iterator nhớ
    
    
    index

Ví dụ
    
    
    index = 2

* * *

Nhưng Linked List

không có index.

Iterator phải nhớ
    
    
    Node hiện tại

* * *

# Ý tưởng
    
    
    head
    
    ↓
    
    10 → 20 → 30 → None
    
    ↑
    current

Mỗi lần
    
    
    next()

↓
    
    
    current = current.next

* * *

# LinkedListIterator
    
    
    class LinkedListIterator:
    
        def __init__(self, head):
            self.current = head
    
        def __iter__(self):
            return self
    
        def __next__(self):
    
            if self.current is None:
                raise StopIteration
    
            value = self.current.value
    
            self.current = self.current.next
    
            return value

Đây là Iterator đúng chuẩn.

* * *

# Collection
    
    
    class LinkedList:
    
        ...
    
        def __iter__(self):
            return LinkedListIterator(self.head)

* * *

# Ví dụ hoàn chỉnh
    
    
    class Node:
    
        def __init__(self, value):
            self.value = value
            self.next = None
    
    
    class LinkedListIterator:
    
        def __init__(self, head):
            self.current = head
    
        def __iter__(self):
            return self
    
        def __next__(self):
    
            if self.current is None:
                raise StopIteration
    
            value = self.current.value
            self.current = self.current.next
            return value
    
    
    class LinkedList:
    
        def __init__(self):
            self.head = None
    
        def append(self, value):
    
            node = Node(value)
    
            if self.head is None:
                self.head = node
                return
    
            current = self.head
    
            while current.next:
                current = current.next
    
            current.next = node
    
        def __iter__(self):
            return LinkedListIterator(self.head)
    
    
    ll = LinkedList()
    
    ll.append(10)
    ll.append(20)
    ll.append(30)
    
    for value in ll:
        print(value)

Kết quả
    
    
    10
    20
    30

* * *

# Minh họa

Ban đầu
    
    
    head
    
    ↓
    
    10 → 20 → 30
    
    ↑
    current

Sau
    
    
    next()

↓
    
    
    10
    
    ↓
    
    20 → 30
    
        ↑
     current

Sau lần hai
    
    
    30
    
    ↑
    current

Sau lần ba
    
    
    None
    
    ↑
    current

↓

StopIteration

* * *

# Hai Iterator độc lập
    
    
    it1 = iter(ll)
    it2 = iter(ll)
    
    print(next(it1))
    print(next(it1))
    
    print(next(it2))

↓
    
    
    10
    20
    10

Mỗi Iterator có
    
    
    current

riêng.

* * *

# Vì sao không lưu index?

Giả sử
    
    
    10 → 20 → 30 → 40

Nếu Iterator lưu
    
    
    index = 3

Muốn lấy
    
    
    40

vẫn phải đi từ đầu
    
    
    10
    
    ↓
    
    20
    
    ↓
    
    30
    
    ↓
    
    40

Mỗi lần `next()`

↓

O(n)

* * *

Nếu lưu
    
    
    current node

↓

`next()`

chỉ là
    
    
    current = current.next

↓

O(1)

Đây là lý do mọi Linked List Iterator đều lưu **node** , không lưu **index**.

* * *

# Reverse Iterator

Single Linked List
    
    
    10 → 20 → 30

Có đi ngược được không?

Không.

Vì
    
    
    30
    
    ↓
    
    ?

không biết node trước là gì.

* * *

# Doubly Linked List

Nếu Node có thêm
    
    
    prev

thì
    
    
    10 ⇄ 20 ⇄ 30

có thể đi ngược.

* * *

# Node
    
    
    class Node:
    
        def __init__(self, value):
            self.value = value
            self.next = None
            self.prev = None

* * *

# Reverse Iterator
    
    
    class ReverseIterator:
    
        def __init__(self, tail):
            self.current = tail
    
        def __iter__(self):
            return self
    
        def __next__(self):
    
            if self.current is None:
                raise StopIteration
    
            value = self.current.value
            self.current = self.current.prev
    
            return value

* * *

Sử dụng
    
    
    for x in dll.reverse():
        print(x)

↓
    
    
    30
    20
    10

* * *

# Sentinel Node

Trong nhiều thư viện, Linked List không dùng
    
    
    head = None

Mà dùng
    
    
    Sentinel
    
    
    HEAD
    
    ↓
    
    [S]
    
    ↓
    
    10
    
    ↓
    
    20
    
    ↓
    
    30
    
    ↓
    
    TAIL

Lợi ích:

  * Không phải kiểm tra `None` nhiều nơi. 
  * Thêm/xóa ở đầu và cuối danh sách đơn giản hơn. 
  * Giảm số lượng điều kiện đặc biệt (edge cases). 



Python cũng áp dụng ý tưởng tương tự trong nhiều cấu trúc dữ liệu nội bộ.

* * *

# Mutable Collection

Một câu hỏi thú vị:
    
    
    for x in ll:

Nếu trong lúc lặp
    
    
    ll.append(100)

thì sao?

Có ba cách thiết kế phổ biến:

  1. **Cho phép** Iterator nhìn thấy phần tử mới. 
  2. **Không nhìn thấy** phần tử mới (snapshot). 
  3. **Báo lỗi** nếu Collection bị thay đổi trong lúc lặp (fail-fast). 



Python `list_iterator` **không phải** là fail-fast; hành vi khi thay đổi danh sách trong lúc lặp có thể gây kết quả khó đoán, vì vậy nên tránh sửa đổi Collection khi đang duyệt.

Java thường chọn fail-fast thông qua `ConcurrentModificationException`.

* * *

# Lazy Traversal

Iterator luôn chỉ giữ
    
    
    current

Không copy toàn bộ Linked List.

Đó là
    
    
    Lazy

Ví dụ
    
    
    it = iter(ll)
    
    print(next(it))

Chỉ đọc
    
    
    Node đầu tiên

* * *

# Ứng dụng thực tế

## LRU Cache
    
    
    Dictionary
    
    +
    
    Doubly Linked List

Linked List được duyệt bằng Iterator.

* * *

## Undo / Redo
    
    
    State1 ⇄ State2 ⇄ State3

Iterator đi tới

↓

Redo

Iterator đi lùi

↓

Undo

* * *

## Playlist
    
    
    Song1
    
    ↓
    
    Song2
    
    ↓
    
    Song3

Next

↓

`next`

Previous

↓

`prev`

* * *

# Ví dụ nâng cao

Cho phép
    
    
    print(list(ll))

vì `list()` sẽ gọi
    
    
    iter(ll)

rồi liên tục gọi
    
    
    next()

Cho phép
    
    
    print(tuple(ll))

Cho phép
    
    
    print(sum(ll))

Nếu các phần tử là số.

Đây là sức mạnh của việc tuân thủ **Iterator Protocol**.

* * *

# Tổng kết buổi 10

Bạn cần nhớ:

  1. Linked List Iterator **không lưu index** , mà lưu **Node hiện tại**. 
  2. `next()` chỉ cần `current = current.next`, nên có độ phức tạp **O(1)**. 
  3. Collection (`LinkedList`) và Iterator (`LinkedListIterator`) nên được tách riêng. 
  4. Single Linked List chỉ hỗ trợ duyệt xuôi; muốn duyệt ngược cần Doubly Linked List hoặc một cơ chế bổ sung. 
  5. Sentinel Node giúp giảm các trường hợp đặc biệt khi thêm/xóa phần tử. 
  6. Iterator trên Linked List cũng là một ví dụ điển hình của **Lazy Traversal**. 



* * *

# Bài tập

## Bài 1

Thêm phương thức:
    
    
    def __len__(self):
        ...

để:
    
    
    print(len(ll))

trả về số node trong Linked List.

* * *

## Bài 2

Cài đặt:
    
    
    def __contains__(self, value):
        ...

để:
    
    
    if 20 in ll:
        print("Found")

hoạt động đúng.

* * *

## Bài 3

Viết `EvenIterator`:
    
    
    for value in ll.even():
        print(value)

chỉ trả về các số chẵn trong Linked List mà **không tạo một Linked List mới**. Iterator này phải bỏ qua các node lẻ trong quá trình duyệt.

* * *

Ở **Buổi 11** , chúng ta sẽ học **Iterator vô hạn (Infinite Iterator)** : cách xây dựng Iterator không bao giờ kết thúc, ứng dụng trong sinh ID, mô phỏng thời gian thực, stream dữ liệu, và cách kiểm soát chúng an toàn để tránh vòng lặp vô tận.

