Chào mừng đến **Bài 16 - Xây dựng CLI App với Clap**! 🖥️

Đây là bài học thực tế đầu tiên - chúng ta sẽ xây dựng một ứng dụng command-line hoàn chỉnh. Clap là thư viện tốt nhất để parse arguments và tạo CLI chuyên nghiệp.

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Cài đặt Clap

**Thêm vào Cargo.toml:**

```toml
[dependencies]
clap = { version = "4.0", features = ["derive"] }
anyhow = "1.0"  # Error handling
colored = "2.0" # Màu sắc cho terminal
```

### 2. Cấu trúc CLI cơ bản

**Sử dụng derive macro để định nghĩa CLI:**

```rust
use clap::{Parser, Subcommand, Args};

/// Ứng dụng CLI mẫu
#[derive(Parser)]
#[command(name = "myapp")]
#[command(about = "Mô tả ứng dụng", long_about = None)]
struct Cli {
    /// Tùy chọn bắt buộc
    #[arg(short, long)]
    name: String,

    /// Tùy chọn optional
    #[arg(short, long, default_value_t = 1)]
    count: u8,

    /// Flag không có giá trị
    #[arg(short, long)]
    verbose: bool,
}

fn main() {
    let cli = Cli::parse();
    
    for _ in 0..cli.count {
        println!("Hello, {}!", cli.name);
    }
    if cli.verbose {
        println!("Verbose mode enabled");
    }
}
```

### 3. Subcommands

**Tạo lệnh con như git add, git commit:**

```rust
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "todo")]
#[command(about = "Todo list manager")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Thêm todo mới
    Add {
        /// Nội dung todo
        text: String,
        
        /// Priority (1-10)
        #[arg(short, long, default_value_t = 5)]
        priority: u8,
    },
    
    /// Liệt kê todos
    List {
        /// Chỉ show todos với priority cao
        #[arg(short, long)]
        high: bool,
    },
    
    /// Xóa todo theo id
    Remove {
        /// ID của todo
        id: u32,
    },
    
    /// Đánh dấu todo đã hoàn thành
    Done {
        /// ID của todo
        id: u32,
    },
}

fn main() {
    let cli = Cli::parse();
    
    match cli.command {
        Commands::Add { text, priority } => {
            println!("Adding todo: {} (priority: {})", text, priority);
        }
        Commands::List { high } => {
            println!("Listing todos (high priority: {})", high);
        }
        Commands::Remove { id } => {
            println!("Removing todo with id: {}", id);
        }
        Commands::Done { id } => {
            println!("Marking todo {} as done", id);
        }
    }
}
```

### 4. Arguments nâng cao

**Các kiểu argument khác:**

```rust
use clap::Parser;
use std::path::PathBuf;

#[derive(Parser)]
struct Args {
    // Vị trí argument (không có flag)
    input: PathBuf,
    
    // Optional positional argument
    output: Option<PathBuf>,
    
    // Multiple values
    #[arg(short, long, num_args = 1..)]
    files: Vec<PathBuf>,
    
    // Giá trị với validation
    #[arg(short, long, value_parser = clap::value_parser!(u8).range(1..=100))]
    percent: u8,
    
    // Enum argument
    #[arg(short, long, value_enum)]
    mode: Mode,
    
    // Boolean flag (negative support)
    #[arg(short, long, action = clap::ArgAction::SetTrue)]
    quiet: bool,
    
    // Có thể xuất hiện nhiều lần
    #[arg(short, long, action = clap::ArgAction::Count)]
    verbose: u8,
}

#[derive(clap::ValueEnum, Clone, Debug)]
enum Mode {
    Fast,
    Normal,
    Slow,
}

fn main() {
    let args = Args::parse();
    println!("Input: {:?}", args.input);
    println!("Output: {:?}", args.output);
    println!("Files: {:?}", args.files);
    println!("Percent: {}", args.percent);
    println!("Mode: {:?}", args.mode);
    println!("Quiet: {}", args.quiet);
    println!("Verbose level: {}", args.verbose);
}
```

### 5. Error Handling với Anyhow

**Xử lý lỗi chuyên nghiệp:**

```rust
use anyhow::{Context, Result, bail};

fn process_file(path: &str) -> Result<String> {
    let content = std::fs::read_to_string(path)
        .with_context(|| format!("Failed to read file: {}", path))?;
    
    if content.is_empty() {
        bail!("File is empty: {}", path);
    }
    
    Ok(content)
}

fn main() -> Result<()> {
    let content = process_file("test.txt")?;
    println!("Content: {}", content);
    Ok(())
}
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án: `cargo new todo_cli`**

**Cargo.toml:**
```toml
[dependencies]
clap = { version = "4.0", features = ["derive"] }
anyhow = "1.0"
colored = "2.0"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
```

**src/main.rs:**
```rust
use clap::{Parser, Subcommand, Args};
use colored::*;
use serde::{Serialize, Deserialize};
use std::fs;
use std::path::PathBuf;
use anyhow::{Result, Context, bail};

#[derive(Debug, Serialize, Deserialize, Clone)]
struct Todo {
    id: u32,
    text: String,
    done: bool,
    priority: u8,
}

#[derive(Debug, Serialize, Deserialize)]
struct TodoList {
    todos: Vec<Todo>,
    next_id: u32,
}

impl TodoList {
    fn new() -> Self {
        TodoList {
            todos: Vec::new(),
            next_id: 1,
        }
    }
    
    fn add(&mut self, text: String, priority: u8) -> Todo {
        let todo = Todo {
            id: self.next_id,
            text,
            done: false,
            priority,
        };
        self.next_id += 1;
        self.todos.push(todo.clone());
        todo
    }
    
    fn list(&self, high_priority: bool) -> Vec<&Todo> {
        self.todos
            .iter()
            .filter(|t| !high_priority || t.priority >= 8)
            .filter(|t| !t.done)
            .collect()
    }
    
    fn remove(&mut self, id: u32) -> Result<Todo> {
        let index = self.todos.iter().position(|t| t.id == id)
            .with_context(|| format!("Todo with id {} not found", id))?;
        Ok(self.todos.remove(index))
    }
    
    fn done(&mut self, id: u32) -> Result<&mut Todo> {
        let todo = self.todos.iter_mut().find(|t| t.id == id)
            .with_context(|| format!("Todo with id {} not found", id))?;
        todo.done = true;
        Ok(todo)
    }
    
    fn save(&self, path: &PathBuf) -> Result<()> {
        let json = serde_json::to_string_pretty(self)?;
        fs::write(path, json)?;
        Ok(())
    }
    
    fn load(path: &PathBuf) -> Result<Self> {
        if !path.exists() {
            return Ok(TodoList::new());
        }
        let content = fs::read_to_string(path)?;
        let list: TodoList = serde_json::from_str(&content)?;
        Ok(list)
    }
}

#[derive(Parser)]
#[command(name = "todo")]
#[command(about = "A simple todo list manager", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
    
    /// Path to todo file
    #[arg(short, long, default_value = "todos.json")]
    file: PathBuf,
}

#[derive(Subcommand)]
enum Commands {
    /// Add a new todo
    Add {
        /// Todo text
        text: String,
        
        /// Priority (1-10)
        #[arg(short, long, default_value_t = 5)]
        priority: u8,
    },
    
    /// List all todos
    List {
        /// Show only high priority todos
        #[arg(short, long)]
        high: bool,
    },
    
    /// Remove a todo
    Remove {
        /// Todo ID
        id: u32,
    },
    
    /// Mark a todo as done
    Done {
        /// Todo ID
        id: u32,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let mut todo_list = TodoList::load(&cli.file)?;
    
    match cli.command {
        Commands::Add { text, priority } => {
            let todo = todo_list.add(text, priority);
            println!("{} Added todo #{}: {}", "✓".green(), todo.id, todo.text);
            todo_list.save(&cli.file)?;
        }
        Commands::List { high } => {
            let todos = todo_list.list(high);
            if todos.is_empty() {
                println!("{}", "No todos found!".yellow());
            } else {
                for todo in todos {
                    let priority_stars = "★".repeat(todo.priority as usize / 2);
                    let priority_color = if todo.priority >= 8 { "red" } else { "yellow" };
                    println!(
                        "{} #{}: {} [{}]",
                        if todo.priority >= 8 { "🔴" } else { "🟡" },
                        todo.id,
                        todo.text,
                        priority_stars.color(priority_color)
                    );
                }
            }
        }
        Commands::Remove { id } => {
            let todo = todo_list.remove(id)?;
            println!("{} Removed: {}", "✓".green(), todo.text);
            todo_list.save(&cli.file)?;
        }
        Commands::Done { id } => {
            let todo = todo_list.done(id)?;
            println!("{} Done: {}", "✓".green(), todo.text);
            todo_list.save(&cli.file)?;
        }
    }
    
    Ok(())
}
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: Calculator CLI
// Tạo CLI calculator với các operation:
// - add, subtract, multiply, divide
// - Support: calc add 2 3
// - Support: calc --expression "2 + 3"

// Bài 2: File Manager CLI
// Tạo CLI quản lý file:
// - list: liệt kê files
// - info: hiển thị thông tin file
// - copy: copy file
// - move: move file
// - delete: xóa file

// Bài 3: Password Generator CLI
// - length (default 16)
// - include-uppercase
// - include-numbers
// - include-symbols
// - count: số lượng password cần tạo

// Bài 4: Weather CLI
// Sử dụng API thời tiết
// - city: tên thành phố
// - units: metric/imperial
// - forecast: số ngày forecast

// Bài 5: Database CLI
// Tạo CLI để quản lý database:
// - create-table
// - insert
// - select (với filter)
// - update (với filter)
// - delete (với filter)
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Khái niệm | Cú pháp | Sử dụng |
|-----------|---------|----------|
| **Parser** | `#[derive(Parser)]` | Struct chính |
| **Subcommand** | `#[derive(Subcommand)]` | Command enum |
| **Args** | `#[derive(Args)]` | Nested arguments |
| **Flag** | `#[arg(short, long)]` | --flag / -f |
| **Positional** | `input: PathBuf` | Không có flag |

---

## ⚡ MẸO HAY

1. **`#[arg(value_enum)]`** - enum arguments
2. **`#[arg(num_args=1..)]`** - multiple values
3. **`#[arg(action = clap::ArgAction::Count)]`** - count occurrences
4. **`#[arg(conflicts_with)]`** - conflict checking
5. **`#[arg(required = true)]`** - required fields
6. **`#[arg(hide = true)]`** - hide from help

---

## 🔥 BÀI TẬP NÂNG CAO

```rust
// Todo CLI với các tính năng nâng cao:
// 1. Thêm tags và categories
// 2. Filter và sort
// 3. Due date và reminder
// 4. Export/Import (JSON, CSV)
// 5. Sync với server
// 6. Interactive mode với tui
// 7. Autocomplete và suggestions
// 8. Colored output và progress bars

// Bonus:
// - Tạo plugin system
// - Customizable themes
// - Command aliases
// - Config file support
// - Environment variables
```

---

## ✅ CHECKLIST BÀI 16

- [ ] Cài đặt và cấu hình Clap
- [ ] Hiểu các derive macros
- [ ] Biết tạo subcommands
- [ ] Parse arguments cơ bản và nâng cao
- [ ] Xử lý lỗi với Anyhow
- [ ] Lưu dữ liệu với Serde
- [ ] Làm xong 5 bài tập cơ bản
- [ ] Thử bài tập nâng cao

---

**Hoàn thành bài tập, chia sẻ code để tôi review!**

Bài tiếp theo: **Bài 17 - Web API với Axum** - xây dựng web service RESTful! 🌐