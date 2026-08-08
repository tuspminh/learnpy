Chào mừng đến **Bài 11: Smart Pointers: Box, Rc, RefCell**! 💡

Đây là bài học về **quản lý bộ nhớ nâng cao** - giúp bạn vượt qua các giới hạn của ownership cơ bản.

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Box<T> - Con trỏ trên Heap

**Box cho phép lưu dữ liệu trên heap thay vì stack:**

```rust
fn main() {
    // Tạo box
    let b = Box::new(5);  // i32 trên heap
    println!("b = {}", b);
    
    // Box cho kiểu dữ liệu lớn
    let huge_array = Box::new([0; 1000]);  // Array 1000 phần tử trên heap
    
    // Recursive types với Box
    // List không thể có kích thước cố định nếu recursive
    // Box giải quyết vì nó có kích thước cố định
    let list = List::Cons(1, Box::new(List::Cons(2, Box::new(List::Nil))));
    
    // Deref coercion - Box tự động deref
    let x = 5;
    let y = Box::new(x);
    assert_eq!(5, *y);  // *y deref Box
}
```

**Recursive type với Box:**

```rust
#[derive(Debug)]
enum List {
    Cons(i32, Box<List>),  // Box để break infinite size
    Nil,
}

fn main() {
    let list = List::Cons(1, 
        Box::new(List::Cons(2, 
            Box::new(List::Cons(3, 
                Box::new(List::Nil))))));
    println!("{:?}", list);
}
```

### 2. Rc<T> - Reference Counting (Multiple Ownership)

**Rc cho phép nhiều biến cùng sở hữu dữ liệu:**

```rust
use std::rc::Rc;

#[derive(Debug)]
struct Node {
    value: i32,
    next: Option<Rc<Node>>,
}

fn main() {
    // Tạo Rc
    let a = Rc::new(5);
    println!("Ref count: {}", Rc::strong_count(&a));  // 1
    
    // Clone Rc (không copy dữ liệu, chỉ tăng ref count)
    let b = Rc::clone(&a);
    println!("a = {}, b = {}", a, b);
    println!("Ref count: {}", Rc::strong_count(&a));  // 2
    
    {
        let c = Rc::clone(&a);
        println!("Ref count: {}", Rc::strong_count(&a));  // 3
    }  // c drop, ref count giảm
    
    println!("Ref count: {}", Rc::strong_count(&a));  // 2
    
    // Rc với List
    let node3 = Rc::new(Node { value: 3, next: None });
    let node2 = Rc::new(Node { value: 2, next: Some(Rc::clone(&node3)) });
    let node1 = Rc::new(Node { value: 1, next: Some(Rc::clone(&node2)) });
    
    // Cả node1 và node2 đều có thể truy cập node3
    println!("node1: {:?}", node1);
    println!("node2: {:?}", node2);
    println!("Ref count node3: {}", Rc::strong_count(&node3));
}
```

### 3. RefCell<T> - Interior Mutability

**RefCell cho phép thay đổi dữ liệu dù có immutable reference:**

```rust
use std::cell::RefCell;

// RefCell thường dùng với Rc để có multiple mutable ownership
#[derive(Debug)]
struct User {
    name: String,
    age: RefCell<u32>,  // Có thể thay đổi age ngay cả khi User là immutable
}

impl User {
    fn new(name: &str, age: u32) -> Self {
        User {
            name: String::from(name),
            age: RefCell::new(age),
        }
    }
    
    fn birthday(&self) {
        // borrow_mut để có mutable reference
        *self.age.borrow_mut() += 1;
    }
    
    fn age(&self) -> u32 {
        *self.age.borrow()
    }
}

fn main() {
    let alice = User::new("Alice", 25);
    println!("Age: {}", alice.age());  // 25
    
    alice.birthday();  // Có thể sửa ngay cả khi alice immutable
    println!("Age: {}", alice.age());  // 26
    
    // Rc + RefCell = Multiple ownership + Interior mutability
    let shared_data = Rc::new(RefCell::new(5));
    let data1 = Rc::clone(&shared_data);
    let data2 = Rc::clone(&shared_data);
    
    *data1.borrow_mut() += 1;  // Cả data1 và data2 đều thấy thay đổi
    println!("data2: {}", data2.borrow());  // 6
}
```

### 4. Kết hợp Rc + RefCell

```rust
use std::rc::Rc;
use std::cell::RefCell;

#[derive(Debug)]
struct Bank {
    balance: RefCell<f64>,
    accounts: RefCell<Vec<String>>,
}

impl Bank {
    fn new() -> Self {
        Bank {
            balance: RefCell::new(0.0),
            accounts: RefCell::new(Vec::new()),
        }
    }
    
    fn deposit(&self, amount: f64) {
        *self.balance.borrow_mut() += amount;
    }
    
    fn add_account(&self, name: String) {
        self.accounts.borrow_mut().push(name);
    }
    
    fn balance(&self) -> f64 {
        *self.balance.borrow()
    }
}

fn main() {
    let bank = Rc::new(Bank::new());
    let bank1 = Rc::clone(&bank);
    let bank2 = Rc::clone(&bank);
    
    // Từ cả 2 tham chiếu đều có thể thay đổi dữ liệu
    bank1.deposit(100.0);
    bank2.add_account("Alice".to_string());
    bank1.add_account("Bob".to_string());
    
    println!("Balance: {}", bank.balance());  // 100
    println!("Accounts: {:?}", bank.accounts.borrow());  // ["Alice", "Bob"]
}
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án: `cargo new bai11_smart_pointers`**

```rust
use std::rc::Rc;
use std::cell::RefCell;

// 1. Box - Recursive List
#[derive(Debug)]
enum LinkedList {
    Node(i32, Box<LinkedList>),
    Nil,
}

impl LinkedList {
    fn new() -> Self {
        LinkedList::Nil
    }
    
    fn prepend(self, value: i32) -> Self {
        LinkedList::Node(value, Box::new(self))
    }
    
    fn len(&self) -> usize {
        match self {
            LinkedList::Node(_, next) => 1 + next.len(),
            LinkedList::Nil => 0,
        }
    }
}

// 2. Rc + RefCell - Shared mutable state
#[derive(Debug)]
struct SharedCounter {
    count: RefCell<i32>,
}

impl SharedCounter {
    fn new() -> Self {
        SharedCounter {
            count: RefCell::new(0),
        }
    }
    
    fn increment(&self) {
        *self.count.borrow_mut() += 1;
    }
    
    fn decrement(&self) {
        *self.count.borrow_mut() -= 1;
    }
    
    fn value(&self) -> i32 {
        *self.count.borrow()
    }
}

// 3. Graph-like structure
#[derive(Debug)]
struct Node2 {
    value: String,
    neighbors: RefCell<Vec<Rc<Node2>>>,
}

impl Node2 {
    fn new(value: &str) -> Rc<Self> {
        Rc::new(Node2 {
            value: String::from(value),
            neighbors: RefCell::new(Vec::new()),
        })
    }
    
    fn add_neighbor(&self, neighbor: Rc<Node2>) {
        self.neighbors.borrow_mut().push(neighbor);
    }
}

fn main() {
    // 1. Box List
    let mut list = LinkedList::new();
    list = list.prepend(1);
    list = list.prepend(2);
    list = list.prepend(3);
    println!("List: {:?}", list);
    println!("Length: {}", list.len());
    
    // 2. Rc + RefCell
    let counter = Rc::new(SharedCounter::new());
    let c1 = Rc::clone(&counter);
    let c2 = Rc::clone(&counter);
    
    c1.increment();
    c2.increment();
    c1.increment();
    println!("Counter value: {}", counter.value());  // 3
    
    // 3. Graph
    let node_a = Node2::new("A");
    let node_b = Node2::new("B");
    let node_c = Node2::new("C");
    
    node_a.add_neighbor(Rc::clone(&node_b));
    node_a.add_neighbor(Rc::clone(&node_c));
    node_b.add_neighbor(Rc::clone(&node_c));
    
    println!("Node A: {}", node_a.value);
    println!("Node A neighbors: {}", node_a.neighbors.borrow().len());
    println!("Node C: {}", node_c.value);
}
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: Box với recursive struct
// Tạo struct BinaryTree<T> với Box để lưu children
// Implement new, insert, contains methods

// Bài 2: Rc để share data
// Tạo struct Book { title: String, author: String }
// Tạo Library với Vec<Rc<Book>> và implement:
// - add_book(book: Book) -> Rc<Book>
// - get_book(index: usize) -> Option<Rc<Book>>
// - count_shared_references()

// Bài 3: RefCell với cache
// Tạo struct Cache { data: RefCell<HashMap<String, i32>> }
// Implement:
// - get_or_compute(&self, key: &str, compute: impl Fn() -> i32) -> i32
// - clear(&self)
// - stats(&self) -> (usize, f64) // (size, average age)

// Bài 4: Rc + RefCell cho shared configuration
// Tạo struct Config { settings: RefCell<HashMap<String, String>> }
// Implement:
// - set(&self, key: &str, value: &str)
// - get(&self, key: &str) -> Option<String>
// - apply_defaults(&self)

// Bài 5: Graph với Rc + RefCell
// Tạo struct Graph { nodes: Vec<Rc<Node>> } với Node có thể thay đổi
// Implement:
// - add_node(&mut self, value: &str) -> Rc<Node>
// - add_edge(&self, from: Rc<Node>, to: Rc<Node>)
// - find_path(&self, from: Rc<Node>, to: Rc<Node>) -> Option<Vec<String>>
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Smart Pointer | Đặc điểm | Khi nào dùng |
|---------------|----------|--------------|
| **Box<T>** | Single ownership, heap allocation | Recursive types, lớn data |
| **Rc<T>** | Multiple ownership, read-only | Shared data, không thread-safe |
| **RefCell<T>** | Interior mutability, runtime borrowing | Khi cần thay đổi dữ liệu |
| **Rc<RefCell<T>>** | Multiple ownership + mutability | Shared mutable state |

---

## ⚡ MẸO HAY

1. **Box** - dùng cho recursive types (list, tree)
2. **Rc** - share data mà không copy
3. **RefCell** - internal mutability pattern
4. **Rc::clone()** tăng ref count, không copy data
5. **`borrow_mut()`** sẽ panic nếu đang borrow
6. **Weak<T>** - weak reference để tránh memory leak

---

## 🔥 BÀI TẬP NÂNG CAO

```rust
// Hệ thống DOM (Document Object Model) đơn giản
// Sử dụng Rc + RefCell + Weak để tránh memory leak

// 1. Tạo Node { element: String, children: RefCell<Vec<Rc<Node>>>, parent: RefCell<Weak<Node>> }
// 2. Implement methods:
//    - new(element: &str) -> Rc<Self>
//    - append_child(&self, child: Rc<Node>)
//    - remove_child(&self, child: Rc<Node>) -> bool
//    - parent(&self) -> Option<Rc<Node>>
//    - find_by_element(&self, element: &str) -> Vec<Rc<Node>>
//    - to_string(&self) -> String (render DOM)

// 3. Tạo HTML tree:
//    - <div> -> <p>, <span>
//    - <p> -> text node
//    - <span> -> text node

// 4. Tìm và thay đổi text của node
// 5. In ra HTML string
```

---

## ✅ CHECKLIST BÀI 11

- [ ] Hiểu Box và recursive types
- [ ] Biết Rc cho multiple ownership
- [ ] Hiểu RefCell và interior mutability
- [ ] Kết hợp Rc + RefCell
- [ ] Biết borrowing rules tại runtime
- [ ] Làm xong 5 bài tập cơ bản
- [ ] Thử bài tập nâng cao

---

**Hoàn thành bài tập, chia sẻ code để tôi review!**

Bài tiếp theo: **Bài 12 - Concurrency và Threads** - lập trình đa luồng trong Rust! 🔀