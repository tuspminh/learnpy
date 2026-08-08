Chào mừng đến **Bài 13 - Async/Await với Tokio**! 🚀

Đây là bài học về **lập trình bất đồng bộ** - cách xử lý nhiều tác vụ I/O cùng lúc một cách hiệu quả, thay vì phải chờ đợi tuần tự.

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Async/Await Cơ Bản

**Async cho phép hàm "tạm dừng" khi chờ I/O, giải phóng thread:**

```rust
use tokio::time::{sleep, Duration};

// Hàm async
async fn say_hello() {
    println!("Hello");
    sleep(Duration::from_secs(1)).await;  // Không block thread
    println!("World");
}

#[tokio::main]
async fn main() {
    say_hello().await;  // Gọi async function
    
    // Chạy nhiều tasks cùng lúc
    let task1 = tokio::spawn(async {
        for i in 1..=3 {
            println!("Task 1: {}", i);
            sleep(Duration::from_millis(100)).await;
        }
    });
    
    let task2 = tokio::spawn(async {
        for i in 1..=3 {
            println!("Task 2: {}", i);
            sleep(Duration::from_millis(150)).await;
        }
    });
    
    task1.await.unwrap();
    task2.await.unwrap();
}
```

### 2. Tokio Runtime

**Tokio là runtime cho async Rust:**

```rust
use tokio::runtime::Runtime;

fn main() {
    // Tạo runtime manually
    let rt = Runtime::new().unwrap();
    rt.block_on(async {
        println!("Running async code in custom runtime");
    });
    
    // Hoặc dùng macro
    // #[tokio::main]
    // async fn main() { ... }
}
```

### 3. Concurrent và Parallel

**Concurrency vs Parallelism:**

```rust
use tokio::time::{sleep, Duration};

async fn task(name: &str, duration: u64) {
    println!("{}: Starting", name);
    sleep(Duration::from_millis(duration)).await;
    println!("{}: Done", name);
}

#[tokio::main]
async fn main() {
    // Sequential - chạy tuần tự
    println!("=== Sequential ===");
    task("Task 1", 100).await;
    task("Task 2", 200).await;
    
    // Concurrent - chạy đồng thời
    println!("=== Concurrent ===");
    let t1 = task("Task 1", 100);
    let t2 = task("Task 2", 200);
    tokio::join!(t1, t2);  // Chờ cả 2
    
    // Spawn tasks - chạy song song
    println!("=== Spawned ===");
    let handle1 = tokio::spawn(task("Task 1", 100));
    let handle2 = tokio::spawn(task("Task 2", 200));
    let _ = tokio::join!(handle1, handle2);
}
```

### 4. Channels trong Async

**Async channels cho giao tiếp bất đồng bộ:**

```rust
use tokio::sync::mpsc;
use tokio::time::{sleep, Duration};

#[tokio::main]
async fn main() {
    let (tx, mut rx) = mpsc::channel::<String>(32);
    
    // Sender
    let tx1 = tx.clone();
    tokio::spawn(async move {
        let messages = vec![
            "Hello".to_string(),
            "World".to_string(),
            "Async".to_string(),
        ];
        for msg in messages {
            tx1.send(msg).await.unwrap();
            sleep(Duration::from_millis(100)).await;
        }
    });
    
    // Receiver
    while let Some(msg) = rx.recv().await {
        println!("Received: {}", msg);
    }
}
```

### 5. Async HTTP với Reqwest

**Gọi API bất đồng bộ:**

```rust
use reqwest;

#[tokio::main]
async fn main() -> Result<(), reqwest::Error> {
    // GET request
    let response = reqwest::get("https://httpbin.org/json").await?;
    let body = response.text().await?;
    println!("Response: {}", body);
    
    // POST request
    let client = reqwest::Client::new();
    let response = client
        .post("https://httpbin.org/post")
        .json(&serde_json::json!({
            "name": "Rust",
            "version": "1.0"
        }))
        .send()
        .await?;
    println!("POST response: {}", response.status());
    
    Ok(())
}
```

### 6. Async với File I/O

**Tokio file operations:**

```rust
use tokio::fs;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Write file
    let mut file = fs::File::create("hello.txt").await?;
    file.write_all(b"Hello, async world!").await?;
    
    // Read file
    let mut file = fs::File::open("hello.txt").await?;
    let mut contents = vec![];
    file.read_to_end(&mut contents).await?;
    println!("File contents: {}", String::from_utf8(contents)?);
    
    Ok(())
}
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án: `cargo new bai13_async` và thêm dependencies:**

```toml
[dependencies]
tokio = { version = "1.0", features = ["full"] }
reqwest = { version = "0.11", features = ["json"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
```

```rust
use tokio::time::{sleep, Duration};
use tokio::sync::mpsc;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct Task {
    id: u32,
    name: String,
    priority: u8,
}

impl Task {
    fn new(id: u32, name: &str, priority: u8) -> Self {
        Task {
            id,
            name: name.to_string(),
            priority,
        }
    }
}

async fn process_task(task: Task) -> Result<String, String> {
    println!("Processing: {:?}", task);
    sleep(Duration::from_millis((task.priority * 50) as u64)).await;
    
    if task.priority > 5 {
        Ok(format!("Task {} completed", task.id))
    } else {
        Err(format!("Task {} failed - priority too low", task.id))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 1. Basic async
    println!("=== Basic Async ===");
    let handle = tokio::spawn(async {
        sleep(Duration::from_secs(1)).await;
        println!("Task spawned!");
    });
    handle.await?;
    
    // 2. Concurrent tasks
    println!("\n=== Concurrent Tasks ===");
    let tasks = vec![
        process_task(Task::new(1, "Important", 8)),
        process_task(Task::new(2, "Normal", 5)),
        process_task(Task::new(3, "Critical", 9)),
    ];
    
    let results = futures::future::join_all(tasks).await;
    for result in results {
        match result {
            Ok(msg) => println!("✅ {}", msg),
            Err(err) => println!("❌ {}", err),
        }
    }
    
    // 3. Async channel
    println!("\n=== Async Channel ===");
    let (tx, mut rx) = mpsc::channel::<(u32, String)>(32);
    
    // Producer
    let producer = tokio::spawn(async move {
        for i in 0..5 {
            tx.send((i, format!("Message {}", i))).await.unwrap();
            sleep(Duration::from_millis(50)).await;
        }
    });
    
    // Consumer
    let consumer = tokio::spawn(async move {
        while let Some((id, msg)) = rx.recv().await {
            println!("Received: {} - {}", id, msg);
        }
    });
    
    let _ = tokio::join!(producer, consumer);
    
    // 4. Timeout
    println!("\n=== Timeout ===");
    let slow_task = tokio::spawn(async {
        sleep(Duration::from_secs(2)).await;
        "Done!"
    });
    
    match tokio::time::timeout(Duration::from_secs(1), slow_task).await {
        Ok(result) => println!("✅ Task completed: {}", result?),
        Err(_) => println!("❌ Task timed out!"),
    }
    
    Ok(())
}
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: Concurrent downloader
// Tạo các URLs giả, download content từ mỗi URL
// Dùng tokio::spawn và join_all để download đồng thời
// In ra kích thước và status code của mỗi URL

// Bài 2: Async file processor
// Đọc nhiều file cùng lúc (tạo mock files)
// Xử lý content (đếm từ, line count)
// Dùng tokio::fs và các async operations
// Tổng hợp kết quả

// Bài 3: Rate limiter với async
// Tạo function fetch_with_limit(url: &str, limit: Duration)
// Giới hạn số request trong khoảng thời gian
// Sử dụng Semaphore hoặc time interval

// Bài 4: Task scheduler
// Tạo hệ thống task scheduler với priority
// Tasks có thể delay (scheduled time)
// Chạy task vào thời điểm đã lên lịch
// Sử dụng tokio::time::delay_until

// Bài 5: Async log collector
// Multiple log producers gửi log qua channel
// Log collector aggregate và write vào file
// Log levels: INFO, WARNING, ERROR
// In ra statistics mỗi 5 seconds
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Khái niệm | Cú pháp | Đặc điểm |
|-----------|---------|----------|
| **Async fn** | `async fn name() {}` | Hàm bất đồng bộ |
| **.await** | `future.await` | Chờ future hoàn thành |
| **tokio::spawn** | `tokio::spawn(async {})` | Chạy task trên runtime |
| **join!** | `tokio::join!(future1, future2)` | Chờ nhiều futures |
| **select!** | `tokio::select! { ... }` | Chờ future đầu tiên |

---

## ⚡ MẸO HAY

1. **`#[tokio::main]`** - entry point cho async
2. **`tokio::spawn`** - spawn tasks lên runtime
3. **`join!`** - chờ nhiều futures cùng lúc
4. **`select!`** - chờ future nào xong trước
5. **`timeout`** - giới hạn thời gian chờ
6. **`spawn_blocking`** - CPU-intensive tasks

---

## 🔥 BÀI TẬP NÂNG CAO

```rust
// Web scraper đa luồng async
// 1. Đọc danh sách URLs từ file
// 2. Sử dụng client pool với connection reuse
// 3. Phân tích HTML với scraper crate
// 4. Trích xuất dữ liệu (title, description, links)
// 5. Save kết quả vào database (SQLite)
// 6. Retry logic với exponential backoff
// 7. Rate limiting (throttle)
// 8. Progress bar với indicatif

// Bonus: Sử dụng Stream để process
// Dùng tokio_stream::wrappers::ReceiverStream
// Stream operations: map, filter, buffer_unordered
```

---

## ✅ CHECKLIST BÀI 13

- [ ] Hiểu async/await cơ bản
- [ ] Biết dùng Tokio runtime
- [ ] Concurrent vs Parallel execution
- [ ] Dùng async channels
- [ ] Xử lý HTTP requests async
- [ ] Async file I/O
- [ ] Làm xong 5 bài tập cơ bản
- [ ] Thử bài tập nâng cao

---

**Hoàn thành bài tập, chia sẻ code để tôi review!**

Bài tiếp theo: **Bài 14 - Macros** - viết code viết code! 🪄