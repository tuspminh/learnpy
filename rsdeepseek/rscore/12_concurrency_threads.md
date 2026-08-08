Chào mừng đến **Bài 12 - Concurrency và Threads**! 🔀

Đây là bài học về **lập trình đa luồng** - một trong những điểm mạnh nhất của Rust nhờ hệ thống ownership và borrow checker ngăn chặn data races ngay từ compile time!

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Threads cơ bản

**Tạo và quản lý threads:**

```rust
use std::thread;
use std::time::Duration;

fn main() {
    // Tạo thread
    let handle = thread::spawn(|| {
        for i in 1..10 {
            println!("Thread: {}", i);
            thread::sleep(Duration::from_millis(100));
        }
    });
    
    // Main thread
    for i in 1..5 {
        println!("Main: {}", i);
        thread::sleep(Duration::from_millis(50));
    }
    
    // Đợi thread kết thúc
    handle.join().unwrap();
    println!("Thread đã kết thúc!");
}
```

### 2. Move Closures với Threads

**Dùng `move` để truyền ownership vào thread:**

```rust
use std::thread;

fn main() {
    let data = vec![1, 2, 3, 4, 5];
    
    // move closure để lấy ownership của data
    let handle = thread::spawn(move || {
        println!("Data in thread: {:?}", data);
        // data được sử dụng trong thread
    });
    
    // println!("Data in main: {:?}", data);  // LỖI! data đã bị moved
    
    handle.join().unwrap();
}
```

### 3. Message Passing với Channels

**Channels cho phép thread giao tiếp an toàn:**

```rust
use std::sync::mpsc;  // multiple producer, single consumer
use std::thread;
use std::time::Duration;

fn main() {
    // Tạo channel
    let (tx, rx) = mpsc::channel();
    
    // Spawn thread để gửi message
    thread::spawn(move || {
        let messages = vec![
            String::from("Hello"),
            String::from("World"),
            String::from("From thread"),
        ];
        
        for msg in messages {
            tx.send(msg).unwrap();
            thread::sleep(Duration::from_millis(100));
        }
    });
    
    // Nhận message trong main
    for received in rx {
        println!("Received: {}", received);
    }
}
```

**Multiple Producers:**

```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();
    let tx1 = tx.clone();  // Clone sender
    
    // Thread 1
    thread::spawn(move || {
        let messages = vec![String::from("Thread 1: Hi"), String::from("Thread 1: Bye")];
        for msg in messages {
            tx.send(msg).unwrap();
        }
    });
    
    // Thread 2
    thread::spawn(move || {
        let messages = vec![String::from("Thread 2: Hello"), String::from("Thread 2: Goodbye")];
        for msg in messages {
            tx1.send(msg).unwrap();
        }
    });
    
    // Nhận tất cả messages
    for received in rx {
        println!("{}", received);
    }
}
```

### 4. Shared State với Mutex

**Mutex cho phép thread-safe shared mutable state:**

```rust
use std::sync::{Mutex, Arc};
use std::thread;

fn main() {
    // Arc (Atomic Rc) cho thread-safe reference counting
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];
    
    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter.lock().unwrap();  // Lock mutex
            *num += 1;
        });  // Mutex được unlock khi num out of scope
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    println!("Final value: {}", *counter.lock().unwrap());  // 10
}
```

### 5. Arc (Atomic Reference Counting)

**Arc là version thread-safe của Rc:**

```rust
use std::sync::Arc;
use std::thread;

fn main() {
    let data = Arc::new(vec![1, 2, 3, 4, 5]);
    let mut handles = vec![];
    
    for _ in 0..3 {
        let data = Arc::clone(&data);
        let handle = thread::spawn(move || {
            println!("Data: {:?}", data);
            println!("Length: {}", data.len());
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
}
```

### 6. Sync và Send Traits

**Send và Sync là marker traits:**

```rust
// Send: có thể gửi ownership giữa threads
// Sync: có thể tham chiếu an toàn từ nhiều threads

// Hầu hết types là Send và Sync
// Rc không Send (không an toàn với threads)
// Arc là Send (Atomic Rc)

// Types không Send: Rc, raw pointers, ...
// Types không Sync: RefCell, Cell, ...
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án: `cargo new bai12_concurrency`**

```rust
use std::thread;
use std::sync::{Arc, Mutex, mpsc};
use std::time::Duration;

#[derive(Debug)]
struct Job {
    id: u32,
    name: String,
    duration: u64,
}

#[derive(Debug)]
struct Worker {
    id: u32,
    processed: u32,
}

fn main() {
    // 1. Threads cơ bản
    println!("=== Threads cơ bản ===");
    let handle = thread::spawn(|| {
        for i in 1..5 {
            println!("  Thread: {}", i);
            thread::sleep(Duration::from_millis(50));
        }
    });
    
    for i in 1..3 {
        println!("Main: {}", i);
        thread::sleep(Duration::from_millis(20));
    }
    handle.join().unwrap();
    
    // 2. Channels
    println!("\n=== Channels ===");
    let (tx, rx) = mpsc::channel();
    
    thread::spawn(move || {
        let jobs = vec![
            Job { id: 1, name: "Task A".to_string(), duration: 100 },
            Job { id: 2, name: "Task B".to_string(), duration: 200 },
        ];
        for job in jobs {
            tx.send(job).unwrap();
            thread::sleep(Duration::from_millis(50));
        }
    });
    
    for received in rx {
        println!("Received job: {:?}", received);
    }
    
    // 3. Shared state với Arc<Mutex>
    println!("\n=== Shared Counter ===");
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];
    
    for _ in 0..5 {
        let counter = Arc::clone(&counter);
        handles.push(thread::spawn(move || {
            for _ in 0..100 {
                let mut num = counter.lock().unwrap();
                *num += 1;
            }
        }));
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
    
    println!("Final counter: {}", *counter.lock().unwrap());
    
    // 4. Thread pool pattern
    println!("\n=== Thread Pool ===");
    let (tx, rx) = mpsc::channel();
    let rx = Arc::new(Mutex::new(rx));
    let mut workers = vec![];
    
    // Worker threads
    for id in 0..3 {
        let rx = Arc::clone(&rx);
        workers.push(thread::spawn(move || loop {
            let job = rx.lock().unwrap().recv();
            match job {
                Ok(job) => println!("Worker {} processed: {:?}", id, job),
                Err(_) => break,  // Channel closed
            }
        }));
    }
    
    // Send jobs
    for i in 0..10 {
        let job = Job {
            id: i,
            name: format!("Job {}", i),
            duration: 100,
        };
        tx.send(job).unwrap();
        thread::sleep(Duration::from_millis(20));
    }
    
    // Clean up
    drop(tx);
    for worker in workers {
        worker.join().unwrap();
    }
}
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: Parallel sum
// Viết hàm parallel_sum(v: Vec<i32>) -> i32
// Chia vector thành n parts và tính tổng song song
// Sử dụng channels để thu thập kết quả

// Bài 2: Worker pool
// Tạo hệ thống worker pool với thread count cố định
// Worker nhận job qua channel và xử lý
// Mỗi job có id, duration (sleep), result (random)

// Bài 3: Shared state với Mutex
// Tạo struct Bank với balance: Mutex<f64>
// Implement:
// - deposit(&self, amount: f64)
// - withdraw(&self, amount: f64) -> Result<(), String>
// - balance(&self) -> f64
// Test với 10 threads deposit 100 lần mỗi thread

// Bài 4: Channels với multiple producers
// Tạo logging system:
// - Logger struct với channel
// - Log levels: Info, Warning, Error
// - Multiple threads có thể send log
// - Logger thread print log theo thứ tự

// Bài 5: Parallel processing
// Cho list các số, tính:
// - Sum, average, min, max, median
// Sử dụng threads để xử lý song song
// So sánh performance với sequential version
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Khái niệm | Cú pháp | Đặc điểm |
|-----------|---------|----------|
| **Thread** | `thread::spawn(|| {})` | Tạo thread mới |
| **Channel** | `mpsc::channel()` | Message passing |
| **Mutex** | `Mutex::new(value)` | Mutual exclusion |
| **Arc** | `Arc::new(value)` | Thread-safe Rc |
| **Join** | `handle.join()` | Đợi thread kết thúc |

---

## ⚡ MẸO HAY

1. **`move` closure** - truyền ownership vào thread
2. **`join()`** luôn gọi để đợi thread kết thúc
3. **`Arc`** thay vì `Rc` trong threads
4. **Mutex** unlock tự động khi lock out of scope
5. **`try_lock()`** để non-blocking lock
6. **`cargo run --release`** để benchmark

---

## 🔥 BÀI TẬP NÂNG CAO

```rust
// Hệ thống crawl web đa luồng
// 1. Tạo struct Page { url: String, content: Option<String>, links: Vec<String> }
// 2. Tạo WebCrawler với:
//    - url_queue: Arc<Mutex<VecDeque<String>>>
//    - visited: Arc<Mutex<HashSet<String>>>
//    - results: Arc<Mutex<HashMap<String, Page>>>
// 3. Worker threads:
//    - Lấy URL từ queue
//    - "Crawl" page (giả lập fetch và parse)
//    - Tìm links và thêm vào queue
//    - Lưu kết quả vào results
// 4. Max depth và max pages
// 5. Logging progress với channels
// 6. Graceful shutdown khi hoàn thành

// Bonus: sử dụng tokio để async crawl
```

---

## ✅ CHECKLIST BÀI 12

- [ ] Biết tạo và quản lý threads
- [ ] Dùng channels để giao tiếp
- [ ] Sử dụng Mutex và Arc
- [ ] Hiểu Send và Sync traits
- [ ] Tránh data races
- [ ] Làm xong 5 bài tập cơ bản
- [ ] Thử bài tập nâng cao

---

**Hoàn thành bài tập, chia sẻ code để tôi review!**

Bài tiếp theo: **Bài 13 - Async/Await với Tokio** - lập trình bất đồng bộ hiện đại! 🚀