Chào mừng đến **Bài 18 - Testing và Benchmarking Nâng Cao**! 🧪

Bài học này sẽ giúp bạn viết tests chuyên nghiệp cho ứng dụng thực tế, bao gồm test async, test API, mock dependencies, và benchmark hiệu suất.

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Testing Async Code

**Test các hàm async với tokio:**

```rust
use tokio::time::{sleep, Duration};

async fn fetch_data(id: u32) -> Result<String, String> {
    sleep(Duration::from_millis(100)).await;
    if id == 0 {
        Err("Invalid ID".to_string())
    } else {
        Ok(format!("Data for id: {}", id))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_fetch_data_success() {
        let result = fetch_data(1).await;
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), "Data for id: 1");
    }
    
    #[tokio::test]
    async fn test_fetch_data_error() {
        let result = fetch_data(0).await;
        assert!(result.is_err());
        assert_eq!(result.unwrap_err(), "Invalid ID");
    }
    
    #[tokio::test]
    #[should_panic(expected = "Invalid ID")]
    async fn test_fetch_data_panic() {
        fetch_data(0).await.unwrap();  // This will panic
    }
}
```

### 2. Testing REST API

**Test Axum API với axum-test:**

```toml
[dev-dependencies]
axum-test = "16.0"
serde_json = "1.0"
```

**tests/api_test.rs:**
```rust
use axum::{Router, routing::get, Json};
use serde::{Deserialize, Serialize};
use axum_test::TestServer;
use axum::http::StatusCode;

#[derive(Debug, Serialize, Deserialize, Clone)]
struct User {
    id: u32,
    name: String,
    email: String,
}

async fn get_users() -> Json<Vec<User>> {
    Json(vec![
        User {
            id: 1,
            name: "Alice".to_string(),
            email: "alice@example.com".to_string(),
        },
        User {
            id: 2,
            name: "Bob".to_string(),
            email: "bob@example.com".to_string(),
        },
    ])
}

async fn get_user(axum::extract::Path(id): axum::extract::Path<u32>) 
    -> Result<Json<User>, StatusCode> {
    if id == 1 {
        Ok(Json(User {
            id: 1,
            name: "Alice".to_string(),
            email: "alice@example.com".to_string(),
        }))
    } else {
        Err(StatusCode::NOT_FOUND)
    }
}

fn app() -> Router {
    Router::new()
        .route("/users", get(get_users))
        .route("/users/:id", get(get_user))
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum_test::TestServer;
    use serde_json::Value;
    
    #[tokio::test]
    async fn test_get_users() {
        let app = app();
        let server = TestServer::new(app).unwrap();
        
        let response = server.get("/users").await;
        assert_eq!(response.status_code(), 200);
        
        let users: Vec<User> = response.json();
        assert_eq!(users.len(), 2);
        assert_eq!(users[0].name, "Alice");
        assert_eq!(users[1].name, "Bob");
    }
    
    #[tokio::test]
    async fn test_get_user_found() {
        let app = app();
        let server = TestServer::new(app).unwrap();
        
        let response = server.get("/users/1").await;
        assert_eq!(response.status_code(), 200);
        
        let user: User = response.json();
        assert_eq!(user.id, 1);
        assert_eq!(user.name, "Alice");
    }
    
    #[tokio::test]
    async fn test_get_user_not_found() {
        let app = app();
        let server = TestServer::new(app).unwrap();
        
        let response = server.get("/users/999").await;
        assert_eq!(response.status_code(), 404);
    }
}
```

### 3. Mocking và Test Doubles

**Mock dependencies với mockall:**

```toml
[dev-dependencies]
mockall = "0.12"
```

```rust
use mockall::{automock, predicate::*};

#[automock]
trait Database {
    fn get_user(&self, id: u32) -> Result<String, String>;
    fn save_user(&mut self, name: &str) -> Result<u32, String>;
}

struct UserService {
    db: Box<dyn Database>,
}

impl UserService {
    fn new(db: Box<dyn Database>) -> Self {
        UserService { db }
    }
    
    fn get_user_name(&self, id: u32) -> Result<String, String> {
        self.db.get_user(id)
    }
    
    fn create_user(&mut self, name: &str) -> Result<u32, String> {
        if name.is_empty() {
            return Err("Name cannot be empty".to_string());
        }
        self.db.save_user(name)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use mockall::predicate::*;
    
    #[test]
    fn test_get_user_name_success() {
        let mut mock_db = MockDatabase::new();
        mock_db
            .expect_get_user()
            .with(eq(1))
            .times(1)
            .returning(|_| Ok("Alice".to_string()));
        
        let service = UserService::new(Box::new(mock_db));
        let result = service.get_user_name(1);
        assert_eq!(result.unwrap(), "Alice");
    }
    
    #[test]
    fn test_get_user_name_error() {
        let mut mock_db = MockDatabase::new();
        mock_db
            .expect_get_user()
            .with(eq(999))
            .times(1)
            .returning(|_| Err("User not found".to_string()));
        
        let service = UserService::new(Box::new(mock_db));
        let result = service.get_user_name(999);
        assert!(result.is_err());
        assert_eq!(result.unwrap_err(), "User not found");
    }
    
    #[test]
    fn test_create_user_success() {
        let mut mock_db = MockDatabase::new();
        mock_db
            .expect_save_user()
            .with(eq("Alice"))
            .times(1)
            .returning(|_| Ok(1));
        
        let mut service = UserService::new(Box::new(mock_db));
        let result = service.create_user("Alice");
        assert_eq!(result.unwrap(), 1);
    }
    
    #[test]
    fn test_create_user_empty_name() {
        let mock_db = MockDatabase::new();  // Không cần mock vì sẽ fail trước
        let mut service = UserService::new(Box::new(mock_db));
        let result = service.create_user("");
        assert!(result.is_err());
        assert_eq!(result.unwrap_err(), "Name cannot be empty");
    }
}
```

### 4. Property-based Testing

**Test với proptest:**

```toml
[dev-dependencies]
proptest = "1.4"
```

```rust
#[cfg(test)]
mod proptests {
    use proptest::prelude::*;
    
    fn reverse(s: &str) -> String {
        s.chars().rev().collect()
    }
    
    fn is_palindrome(s: &str) -> bool {
        s == reverse(s)
    }
    
    proptest! {
        #[test]
        fn test_reverse_reverse_identity(s: String) {
            // reverse(reverse(s)) == s
            assert_eq!(reverse(&reverse(&s)), s);
        }
        
        #[test]
        fn test_palindrome_properties(s in "\\PC*") {
            let rev = reverse(&s);
            let palindrome = format!("{}{}", s, rev);
            assert!(is_palindrome(&palindrome));
        }
        
        #[test]
        fn test_string_length_preserved(s in "\\PC{1,100}") {
            let rev = reverse(&s);
            assert_eq!(s.len(), rev.len());
        }
    }
}
```

### 5. Benchmarking với Criterion

**Benchmark nâng cao:**

```rust
use criterion::{criterion_group, criterion_main, Criterion, BenchmarkId, Throughput};
use rand::Rng;
use std::collections::HashMap;

fn fibonacci_recursive(n: u64) -> u64 {
    match n {
        0 => 0,
        1 => 1,
        _ => fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2),
    }
}

fn fibonacci_iterative(n: u64) -> u64 {
    let mut a = 0;
    let mut b = 1;
    for _ in 0..n {
        let temp = a;
        a = b;
        b = temp + b;
    }
    a
}

fn hashmap_insertion(n: usize) {
    let mut map = HashMap::new();
    for i in 0..n {
        map.insert(i, format!("value_{}", i));
    }
}

fn bench_fibonacci(c: &mut Criterion) {
    let mut group = c.benchmark_group("Fibonacci");
    
    // Bench với nhiều inputs
    for n in [10, 20, 30].iter() {
        group.bench_with_input(
            BenchmarkId::new("recursive", n), 
            n, 
            |b, &n| b.iter(|| fibonacci_recursive(n))
        );
        group.bench_with_input(
            BenchmarkId::new("iterative", n), 
            n, 
            |b, &n| b.iter(|| fibonacci_iterative(n))
        );
    }
    group.finish();
}

fn bench_hashmap(c: &mut Criterion) {
    let mut group = c.benchmark_group("HashMap Insertion");
    
    for size in [100, 1000, 10000, 100000].iter() {
        group.throughput(Throughput::Elements(*size as u64));
        group.bench_with_input(
            BenchmarkId::from_parameter(size),
            size,
            |b, &size| b.iter(|| hashmap_insertion(size))
        );
    }
    group.finish();
}

criterion_group!(benches, bench_fibonacci, bench_hashmap);
criterion_main!(benches);
```

### 6. Test Coverage

**Đo độ bao phủ code với tarpaulin:**

```bash
# Cài đặt
cargo install cargo-tarpaulin

# Chạy coverage
cargo tarpaulin --verbose

# Report HTML
cargo tarpaulin --out Html
```

**Ví dụ coverage trong CI:**

```yaml
# .github/workflows/coverage.yml
name: Coverage

on: [push, pull_request]

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
          override: true
      - name: Install tarpaulin
        run: cargo install cargo-tarpaulin
      - name: Run coverage
        run: cargo tarpaulin --out Xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: cobertura.xml
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án: `cargo new advanced_testing`**

**Cargo.toml:**
```toml
[dependencies]
tokio = { version = "1.0", features = ["full"] }
axum = "0.7"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
uuid = { version = "1.0", features = ["v4", "serde"] }
chrono = "0.4"

[dev-dependencies]
axum-test = "16.0"
mockall = "0.12"
proptest = "1.4"
criterion = "0.5"
```

**src/lib.rs:**
```rust
use std::sync::Arc;
use tokio::sync::Mutex;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Todo {
    pub id: String,
    pub title: String,
    pub completed: bool,
}

#[derive(Debug, Deserialize)]
pub struct CreateTodo {
    pub title: String,
}

pub type TodoStore = Arc<Mutex<Vec<Todo>>>;

pub struct TodoService {
    store: TodoStore,
}

impl TodoService {
    pub fn new(store: TodoStore) -> Self {
        TodoService { store }
    }
    
    pub async fn list(&self) -> Vec<Todo> {
        let store = self.store.lock().await;
        store.clone()
    }
    
    pub async fn create(&self, title: String) -> Todo {
        let todo = Todo {
            id: Uuid::new_v4().to_string(),
            title,
            completed: false,
        };
        let mut store = self.store.lock().await;
        store.push(todo.clone());
        todo
    }
    
    pub async fn get(&self, id: &str) -> Option<Todo> {
        let store = self.store.lock().await;
        store.iter().find(|t| t.id == id).cloned()
    }
    
    pub async fn delete(&self, id: &str) -> bool {
        let mut store = self.store.lock().await;
        let pos = store.iter().position(|t| t.id == id);
        if let Some(pos) = pos {
            store.remove(pos);
            true
        } else {
            false
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tokio::sync::Mutex;
    use std::sync::Arc;
    
    fn create_test_store() -> TodoStore {
        Arc::new(Mutex::new(vec![
            Todo {
                id: "1".to_string(),
                title: "Test todo 1".to_string(),
                completed: false,
            },
            Todo {
                id: "2".to_string(),
                title: "Test todo 2".to_string(),
                completed: true,
            },
        ]))
    }
    
    #[tokio::test]
    async fn test_list_todos() {
        let store = create_test_store();
        let service = TodoService::new(store);
        
        let todos = service.list().await;
        assert_eq!(todos.len(), 2);
        assert_eq!(todos[0].title, "Test todo 1");
    }
    
    #[tokio::test]
    async fn test_create_todo() {
        let store = create_test_store();
        let service = TodoService::new(store);
        
        let todo = service.create("New todo".to_string()).await;
        assert_eq!(todo.title, "New todo");
        assert!(!todo.completed);
        
        let todos = service.list().await;
        assert_eq!(todos.len(), 3);
    }
    
    #[tokio::test]
    async fn test_get_todo() {
        let store = create_test_store();
        let service = TodoService::new(store);
        
        let todo = service.get("1").await;
        assert!(todo.is_some());
        assert_eq!(todo.unwrap().title, "Test todo 1");
        
        let todo = service.get("999").await;
        assert!(todo.is_none());
    }
    
    #[tokio::test]
    async fn test_delete_todo() {
        let store = create_test_store();
        let service = TodoService::new(store);
        
        assert!(service.delete("1").await);
        assert!(!service.delete("999").await);
        
        let todos = service.list().await;
        assert_eq!(todos.len(), 1);
    }
}
```

**tests/axum_test.rs:**
```rust
use advanced_testing::*;
use axum::{Router, routing::{get, post, delete}, extract::{Path, State}, Json, http::StatusCode};
use std::sync::Arc;
use tokio::sync::Mutex;

async fn list_todos(State(service): State<TodoService>) -> Json<Vec<Todo>> {
    Json(service.list().await)
}

async fn create_todo(
    State(service): State<TodoService>,
    Json(payload): Json<CreateTodo>,
) -> (StatusCode, Json<Todo>) {
    let todo = service.create(payload.title).await;
    (StatusCode::CREATED, Json(todo))
}

async fn delete_todo(
    Path(id): Path<String>,
    State(service): State<TodoService>,
) -> StatusCode {
    if service.delete(&id).await {
        StatusCode::NO_CONTENT
    } else {
        StatusCode::NOT_FOUND
    }
}

fn app() -> Router {
    let store: TodoStore = Arc::new(Mutex::new(Vec::new()));
    let service = TodoService::new(store);
    
    Router::new()
        .route("/todos", get(list_todos).post(create_todo))
        .route("/todos/:id", delete(delete_todo))
        .with_state(service)
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum_test::TestServer;
    use serde_json::json;
    
    #[tokio::test]
    async fn test_list_empty() {
        let server = TestServer::new(app()).unwrap();
        let response = server.get("/todos").await;
        assert_eq!(response.status_code(), 200);
        let todos: Vec<Todo> = response.json();
        assert!(todos.is_empty());
    }
    
    #[tokio::test]
    async fn test_create_and_get() {
        let server = TestServer::new(app()).unwrap();
        
        // Create todo
        let response = server
            .post("/todos")
            .json(&json!({"title": "Integration test"}))
            .await;
        assert_eq!(response.status_code(), 201);
        
        let created: Todo = response.json();
        assert_eq!(created.title, "Integration test");
        
        // List todos
        let response = server.get("/todos").await;
        let todos: Vec<Todo> = response.json();
        assert_eq!(todos.len(), 1);
        assert_eq!(todos[0].id, created.id);
        
        // Delete todo
        let response = server
            .delete(&format!("/todos/{}", created.id))
            .await;
        assert_eq!(response.status_code(), 204);
        
        // List again
        let response = server.get("/todos").await;
        let todos: Vec<Todo> = response.json();
        assert!(todos.is_empty());
    }
}
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: Test async function
// Viết async function và test các trường hợp:
// - Success
// - Error
// - Timeout
// - Panic

// Bài 2: API Integration Test
// Test full CRUD API với axum-test
// Kiểm tra status codes, response body, error handling

// Bài 3: Mock Dependencies
// Sử dụng mockall để mock database
// Test business logic không cần DB thật

// Bài 4: Property-based Testing
// Viết proptest cho các functions:
// - sort: luôn trả về sorted list
// - unique: không có duplicates
// - math operations: identity, commutativity

// Bài 5: Performance Testing
// Benchmark các implementation khác nhau
// So sánh hiệu suất và memory usage
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Khái niệm | Cách dùng | Mục đích |
|-----------|-----------|----------|
| **tokio::test** | `#[tokio::test]` | Test async |
| **axum-test** | `TestServer::new()` | Test API |
| **mockall** | `#[automock]` | Mock dependencies |
| **proptest** | `proptest! { #[test] }` | Property-based test |
| **criterion** | `criterion_group!` | Benchmark |

---

## ⚡ MẸO HAY

1. **`cargo test -- --nocapture`** - show println! output
2. **`cargo test -- --test-threads=1`** - run tests sequentially
3. **`cargo test -- --ignored`** - run ignored tests
4. **`cargo bench -- --profile-time 5`** - benchmark for 5 seconds
5. **`cargo tarpaulin --html`** - coverage report

---

## 🔥 BÀI TẬP NÂNG CAO

```rust
// 1. Fuzz Testing
// Sử dụng fuzz testing để tìm bugs
// Test với random inputs

// 2. Mutation Testing
// Kiểm tra chất lượng tests
// Tự động sửa đổi code và kiểm tra test phát hiện

// 3. Stress Testing
// Test với high load
// Concurrent requests
// Memory leak detection

// 4. Smoke Testing
// Kiểm tra các happy path
// Deployment verification

// 5. Performance Regression
// So sánh benchmark với previous runs
// Alert nếu performance giảm
// Automate với CI
```

---

## ✅ CHECKLIST BÀI 18

- [ ] Test async functions
- [ ] API integration tests
- [ ] Mock dependencies
- [ ] Property-based testing
- [ ] Benchmark with Criterion
- [ ] Test coverage report
- [ ] Làm xong 5 bài tập cơ bản
- [ ] Thử bài tập nâng cao

---

**Hoàn thành bài tập, chia sẻ code để tôi review!**

Bài tiếp theo: **Bài 19 - FFI với C** - gọi thư viện C từ Rust! 🔗