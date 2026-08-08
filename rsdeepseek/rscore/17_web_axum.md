Chào mừng đến **Bài 17 - Web API với Axum**! 🌐

Đây là bài học về **xây dựng RESTful API** với Axum - framework web hiện đại, an toàn và hiệu năng cao của Rust, được phát triển bởi đội ngũ Tokio.

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Giới thiệu về Axum

**Axum là web framework tập trung vào ergonomics và hiệu suất:**

```toml
[dependencies]
axum = "0.7"
tokio = { version = "1.0", features = ["full"] }
tower-http = { version = "0.5", features = ["cors", "trace"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
uuid = { version = "1.0", features = ["v4", "serde"] }
chrono = { version = "0.4", features = ["serde"] }
```

### 2. Hello World với Axum

```rust
use axum::{
    routing::get,
    Router,
    response::Json,
    http::StatusCode,
};
use serde_json::{json, Value};

async fn hello() -> &'static str {
    "Hello, World!"
}

async fn health() -> Json<Value> {
    Json(json!({
        "status": "ok",
        "version": "1.0.0"
    }))
}

#[tokio::main]
async fn main() {
    // Build router
    let app = Router::new()
        .route("/", get(hello))
        .route("/health", get(health));

    // Start server
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000")
        .await
        .unwrap();
    
    println!("Server running on http://localhost:3000");
    axum::serve(listener, app).await.unwrap();
}
```

### 3. REST API với CRUD

```rust
use axum::{
    Router, routing::{get, post, put, delete},
    extract::{Path, State, Json},
    http::StatusCode,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::Mutex;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Todo {
    id: String,
    title: String,
    completed: bool,
}

#[derive(Debug, Deserialize)]
struct CreateTodo {
    title: String,
}

#[derive(Debug, Deserialize)]
struct UpdateTodo {
    title: Option<String>,
    completed: Option<bool>,
}

type TodoStore = Arc<Mutex<Vec<Todo>>>;

// Handlers
async fn get_todos(
    State(store): State<TodoStore>,
) -> Json<Vec<Todo>> {
    let todos = store.lock().await;
    Json(todos.clone())
}

async fn create_todo(
    State(store): State<TodoStore>,
    Json(payload): Json<CreateTodo>,
) -> (StatusCode, Json<Todo>) {
    let todo = Todo {
        id: Uuid::new_v4().to_string(),
        title: payload.title,
        completed: false,
    };
    
    let mut store = store.lock().await;
    store.push(todo.clone());
    
    (StatusCode::CREATED, Json(todo))
}

async fn get_todo(
    Path(id): Path<String>,
    State(store): State<TodoStore>,
) -> Result<Json<Todo>, StatusCode> {
    let store = store.lock().await;
    let todo = store.iter().find(|t| t.id == id)
        .ok_or(StatusCode::NOT_FOUND)?;
    Ok(Json(todo.clone()))
}

async fn update_todo(
    Path(id): Path<String>,
    State(store): State<TodoStore>,
    Json(payload): Json<UpdateTodo>,
) -> Result<Json<Todo>, StatusCode> {
    let mut store = store.lock().await;
    let todo = store.iter_mut().find(|t| t.id == id)
        .ok_or(StatusCode::NOT_FOUND)?;
    
    if let Some(title) = payload.title {
        todo.title = title;
    }
    if let Some(completed) = payload.completed {
        todo.completed = completed;
    }
    
    Ok(Json(todo.clone()))
}

async fn delete_todo(
    Path(id): Path<String>,
    State(store): State<TodoStore>,
) -> Result<StatusCode, StatusCode> {
    let mut store = store.lock().await;
    let pos = store.iter().position(|t| t.id == id)
        .ok_or(StatusCode::NOT_FOUND)?;
    store.remove(pos);
    Ok(StatusCode::NO_CONTENT)
}

#[tokio::main]
async fn main() {
    let store: TodoStore = Arc::new(Mutex::new(Vec::new()));
    
    let app = Router::new()
        .route("/todos", get(get_todos).post(create_todo))
        .route("/todos/:id", 
            get(get_todo)
            .put(update_todo)
            .delete(delete_todo)
        )
        .with_state(store);
    
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000")
        .await
        .unwrap();
    
    println!("🚀 Server running on http://localhost:3000");
    axum::serve(listener, app).await.unwrap();
}
```

### 4. Extractor - Lấy dữ liệu từ request

```rust
use axum::{
    extract::{Query, Path, Json, Form, Multipart, FromRequestParts},
    headers::{Authorization, authorization::Bearer},
    TypedHeader,
};
use std::collections::HashMap;

// Query parameters
async fn search(
    Query(params): Query<HashMap<String, String>>,
) -> String {
    format!("Searching: {:?}", params)
}

// Path parameters
async fn get_user(
    Path(id): Path<u32>,
) -> String {
    format!("User ID: {}", id)
}

// JSON body
#[derive(Deserialize)]
struct LoginRequest {
    username: String,
    password: String,
}

async fn login(
    Json(payload): Json<LoginRequest>,
) -> String {
    format!("Logging in: {}", payload.username)
}

// Form data
async fn submit_form(
    Form(data): Form<HashMap<String, String>>,
) -> String {
    format!("Form data: {:?}", data)
}

// Headers
async fn auth_check(
    TypedHeader(auth): TypedHeader<Authorization<Bearer>>,
) -> String {
    format!("Token: {}", auth.token())
}

// Custom extractor
struct User {
    id: u32,
    name: String,
}

// Implement FromRequestParts
impl<S> FromRequestParts<S> for User {
    type Rejection = (StatusCode, String);
    
    async fn from_request_parts(
        parts: &mut axum::http::request::Parts,
        _state: &S,
    ) -> Result<Self, Self::Rejection> {
        let auth_header = parts
            .headers
            .get("authorization")
            .and_then(|h| h.to_str().ok())
            .ok_or((StatusCode::UNAUTHORIZED, "Missing auth".to_string()))?;
        
        // Validate token (simplified)
        let user = User {
            id: 1,
            name: "Alice".to_string(),
        };
        
        Ok(user)
    }
}

async fn profile(user: User) -> String {
    format!("User: {} (ID: {})", user.name, user.id)
}
```

### 5. Middleware

```rust
use tower_http::{
    cors::{CorsLayer, Any},
    trace::TraceLayer,
    compression::CompressionLayer,
    sensitive_headers::SetSensitiveHeadersLayer,
};
use tower::{ServiceBuilder, ServiceExt};
use std::time::Duration;
use axum::http::{HeaderValue, Method};

#[tokio::main]
async fn main() {
    let middleware = ServiceBuilder::new()
        // Logging
        .layer(TraceLayer::new_for_http())
        
        // CORS
        .layer(CorsLayer::new()
            .allow_origin(Any)
            .allow_methods([Method::GET, Method::POST, Method::PUT, Method::DELETE])
            .allow_headers(Any)
        )
        
        // Compression (gzip, brotli)
        .layer(CompressionLayer::new())
        
        // Rate limiting (custom)
        // .layer(RateLimitLayer::new(100, Duration::from_secs(60)))
        
        // Timeout
        // .layer(TimeoutLayer::new(Duration::from_secs(30)))
        ;
    
    let app = Router::new()
        .route("/", get(handler))
        .layer(middleware);
    
    // Start server...
}
```

### 6. Shared State với Database

```rust
use sqlx::postgres::{PgPool, PgPoolOptions};

#[derive(Clone)]
struct AppState {
    db: PgPool,
}

async fn get_users(
    State(state): State<AppState>,
) -> Json<Vec<User>> {
    let users = sqlx::query!("SELECT * FROM users")
        .fetch_all(&state.db)
        .await
        .unwrap();
    
    Json(users)
}

#[tokio::main]
async fn main() {
    let db = PgPoolOptions::new()
        .max_connections(5)
        .connect("postgres://localhost/mydb")
        .await
        .unwrap();
    
    let state = AppState { db };
    
    let app = Router::new()
        .route("/users", get(get_users))
        .with_state(state);
    
    // Start server...
}
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án: `cargo new todo_api`**

**src/main.rs:**
```rust
use axum::{
    Router, routing::{get, post, put, delete},
    extract::{Path, State, Json},
    http::StatusCode,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::Mutex;
use uuid::Uuid;
use tower_http::{cors::CorsLayer, trace::TraceLayer};

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Todo {
    id: String,
    title: String,
    description: Option<String>,
    completed: bool,
    created_at: String,
}

#[derive(Debug, Deserialize)]
struct CreateTodo {
    title: String,
    description: Option<String>,
}

#[derive(Debug, Deserialize)]
struct UpdateTodo {
    title: Option<String>,
    description: Option<String>,
    completed: Option<bool>,
}

type TodoStore = Arc<Mutex<Vec<Todo>>>;

// Handlers
async fn health_check() -> &'static str {
    "OK"
}

async fn get_todos(State(store): State<TodoStore>) -> Json<Vec<Todo>> {
    let todos = store.lock().await;
    Json(todos.clone())
}

async fn create_todo(
    State(store): State<TodoStore>,
    Json(payload): Json<CreateTodo>,
) -> (StatusCode, Json<Todo>) {
    let todo = Todo {
        id: Uuid::new_v4().to_string(),
        title: payload.title,
        description: payload.description,
        completed: false,
        created_at: chrono::Utc::now().to_rfc3339(),
    };
    
    let mut store = store.lock().await;
    store.push(todo.clone());
    
    (StatusCode::CREATED, Json(todo))
}

async fn get_todo(
    Path(id): Path<String>,
    State(store): State<TodoStore>,
) -> Result<Json<Todo>, StatusCode> {
    let store = store.lock().await;
    let todo = store.iter().find(|t| t.id == id)
        .ok_or(StatusCode::NOT_FOUND)?;
    Ok(Json(todo.clone()))
}

async fn update_todo(
    Path(id): Path<String>,
    State(store): State<TodoStore>,
    Json(payload): Json<UpdateTodo>,
) -> Result<Json<Todo>, StatusCode> {
    let mut store = store.lock().await;
    let todo = store.iter_mut().find(|t| t.id == id)
        .ok_or(StatusCode::NOT_FOUND)?;
    
    if let Some(title) = payload.title {
        todo.title = title;
    }
    if let Some(description) = payload.description {
        todo.description = Some(description);
    }
    if let Some(completed) = payload.completed {
        todo.completed = completed;
    }
    
    Ok(Json(todo.clone()))
}

async fn delete_todo(
    Path(id): Path<String>,
    State(store): State<TodoStore>,
) -> Result<StatusCode, StatusCode> {
    let mut store = store.lock().await;
    let pos = store.iter().position(|t| t.id == id)
        .ok_or(StatusCode::NOT_FOUND)?;
    store.remove(pos);
    Ok(StatusCode::NO_CONTENT)
}

#[tokio::main]
async fn main() {
    // Initialize store
    let store: TodoStore = Arc::new(Mutex::new(Vec::new()));
    
    // Add some initial todos
    {
        let mut store = store.lock().await;
        store.push(Todo {
            id: "1".to_string(),
            title: "Learn Rust".to_string(),
            description: Some("Finish the Rust book".to_string()),
            completed: false,
            created_at: chrono::Utc::now().to_rfc3339(),
        });
        store.push(Todo {
            id: "2".to_string(),
            title: "Build API".to_string(),
            description: Some("Create REST API with Axum".to_string()),
            completed: false,
            created_at: chrono::Utc::now().to_rfc3339(),
        });
    }
    
    // Build router
    let app = Router::new()
        .route("/", get(|| async { "Todo API" }))
        .route("/health", get(health_check))
        .route("/todos", get(get_todos).post(create_todo))
        .route("/todos/:id", 
            get(get_todo)
            .put(update_todo)
            .delete(delete_todo)
        )
        .layer(CorsLayer::permissive())
        .layer(TraceLayer::new_for_http())
        .with_state(store);
    
    // Start server
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000")
        .await
        .unwrap();
    
    println!("🚀 Server running on http://localhost:3000");
    println!("📋 API endpoints:");
    println!("  GET /todos - List all todos");
    println!("  POST /todos - Create todo");
    println!("  GET /todos/:id - Get todo");
    println!("  PUT /todos/:id - Update todo");
    println!("  DELETE /todos/:id - Delete todo");
    
    axum::serve(listener, app).await.unwrap();
}
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: User API
// Tạo User API với CRUD
// Fields: id, name, email, age, created_at
// Validation: email format, age > 0

// Bài 2: Product API
// Product: id, name, price, category, stock
// Endpoints: CRUD + search by category
// Filter: min_price, max_price, in_stock

// Bài 3: Authentication
// Thêm JWT authentication
// Login endpoint
// Protected routes với middleware

// Bài 4: Error Handling
// Custom error types
// Proper HTTP status codes
// Error response format: { error: string }

// Bài 5: Pagination
// GET /todos?page=1&limit=10
// GET /todos?sort=created_at&order=desc
// Trả về: { data: [...], total, page, limit }
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Khái niệm | Cú pháp | Sử dụng |
|-----------|---------|----------|
| **Router** | `Router::new().route()` | Định nghĩa routes |
| **Handler** | `async fn handler() -> Response` | Xử lý request |
| **Extractor** | `Path<T>`, `Query<T>`, `Json<T>` | Lấy dữ liệu |
| **State** | `State<T>` | Shared state |
| **Middleware** | `.layer()` | Thêm middleware |

---

## ⚡ MẸO HAY

1. **`axum::Router`** - xây dựng router modular
2. **`axum::extract`** - nhiều extractors hữu ích
3. **`tower_http`** - middleware collection
4. **`#[axum_macros::debug_handler]`** - debug handler signatures
5. **`axum::response::IntoResponse`** - custom response types
6. **`axum::body::Body`** - streaming responses

---

## 🔥 BÀI TẬP NÂNG CAO

```rust
// Blog API với các tính năng:
// 1. Users: register, login, profile
// 2. Posts: CRUD, publish, draft
// 3. Comments: CRUD on posts
// 4. Categories: tags, categories
// 5. Search: full-text search
// 6. Rate limiting và caching
// 7. WebSocket cho real-time notifications
// 8. File upload: images, attachments
// 9. Email notifications
// 10. API documentation với OpenAPI

// Bonus:
// - Connect với PostgreSQL
// - Migration với sqlx
// - Testing với axum-test
// - Docker deployment
// - CI/CD pipeline
```

---

## ✅ CHECKLIST BÀI 17

- [ ] Cài đặt Axum và dependencies
- [ ] Hello World API
- [ ] CRUD với REST API
- [ ] Sử dụng extractors
- [ ] Shared state
- [ ] Middleware (CORS, Logging)
- [ ] Error handling
- [ ] Làm xong 5 bài tập cơ bản
- [ ] Thử bài tập nâng cao

---

**Hoàn thành bài tập, chia sẻ code để tôi review!**

Bài tiếp theo: **Bài 18 - Testing và Benchmarking Nâng Cao** - đảm bảo API của bạn hoạt động hoàn hảo! 🧪