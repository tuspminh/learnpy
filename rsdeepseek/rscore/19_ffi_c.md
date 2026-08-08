Chào mừng đến **Bài 19 - FFI với C**! 🔗

Đây là bài học về **Foreign Function Interface** - cách để Rust gọi code C/C++ và ngược lại. Đây là kỹ năng quan trọng khi bạn cần tận dụng thư viện C cũ hoặc nhúng Rust vào project C hiện có.

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Gọi Hàm C từ Rust (Basic)

**Cách cơ bản để gọi hàm C:**

```c
// math.c
#include <stdint.h>

int32_t add(int32_t a, int32_t b) {
    return a + b;
}

int32_t multiply(int32_t a, int32_t b) {
    return a * b;
}
```

**Rust code:**

```rust
// build.rs
fn main() {
    cc::Build::new()
        .file("src/math.c")
        .compile("math");
}

// src/main.rs
use std::ffi::c_int;

extern "C" {
    fn add(a: c_int, b: c_int) -> c_int;
    fn multiply(a: c_int, b: c_int) -> c_int;
}

fn main() {
    unsafe {
        let sum = add(10, 20);
        let product = multiply(10, 20);
        println!("Sum: {}, Product: {}", sum, product);
    }
}
```

### 2. Gọi Thư Viện C Hệ Thống

**Gọi thư viện C đã có sẵn:**

```rust
use std::ffi::CString;
use std::os::raw::c_char;

// Link với thư viện C
#[link(name = "c")]
extern "C" {
    fn printf(format: *const c_char, ...) -> i32;
    fn puts(s: *const c_char) -> i32;
    fn atoi(s: *const c_char) -> i32;
}

fn main() {
    // Gọi printf (cẩn thận với variadic functions)
    let msg = CString::new("Hello from Rust via C printf!\n").unwrap();
    unsafe {
        printf(msg.as_ptr());
    }
    
    // Gọi puts
    let msg = CString::new("Hello from puts!").unwrap();
    unsafe {
        puts(msg.as_ptr());
    }
    
    // Gọi atoi
    let num = CString::new("123").unwrap();
    unsafe {
        let value = atoi(num.as_ptr());
        println!("Parsed: {}", value);
    }
}
```

### 3. Làm Việc với C Strings

**Chuyển đổi giữa Rust String và C string:**

```rust
use std::ffi::{CString, CStr};
use std::os::raw::c_char;

// Hàm C trả về string
extern "C" {
    fn get_message() -> *const c_char;
    fn free_message(ptr: *const c_char);
}

fn get_c_string() -> String {
    unsafe {
        let ptr = get_message();
        let c_str = CStr::from_ptr(ptr);
        let result = c_str.to_str().unwrap().to_string();
        free_message(ptr);
        result
    }
}

// Hàm C nhận string
extern "C" {
    fn process_string(s: *const c_char) -> i32;
}

fn process_rust_string(s: &str) -> i32 {
    let c_string = CString::new(s).unwrap();
    unsafe {
        process_string(c_string.as_ptr())
    }
}

fn main() {
    // Tạo CString từ Rust
    let rust_str = "Hello from Rust!";
    let c_str = CString::new(rust_str).unwrap();
    
    // In raw pointer
    println!("C string pointer: {:?}", c_str.as_ptr());
    
    // Chuyển từ CString sang &str
    let c_str_ref = c_str.to_str().unwrap();
    println!("Rust str: {}", c_str_ref);
}
```

### 4. Struct và Opaque Types

**Truyền struct qua FFI:**

```c
// person.h
typedef struct {
    char* name;
    int age;
} Person;

Person* person_new(const char* name, int age);
void person_free(Person* p);
const char* person_get_name(const Person* p);
int person_get_age(const Person* p);
```

**Rust bindings:**

```rust
use std::ffi::{CString, CStr};
use std::os::raw::{c_char, c_int};

#[repr(C)]
#[derive(Debug)]
struct Person {
    name: *mut c_char,
    age: c_int,
}

extern "C" {
    fn person_new(name: *const c_char, age: c_int) -> *mut Person;
    fn person_free(p: *mut Person);
    fn person_get_name(p: *const Person) -> *const c_char;
    fn person_get_age(p: *const Person) -> c_int;
}

impl Person {
    fn new(name: &str, age: i32) -> *mut Self {
        let c_name = CString::new(name).unwrap();
        unsafe {
            person_new(c_name.as_ptr(), age as c_int)
        }
    }
    
    fn name(&self) -> String {
        unsafe {
            let ptr = person_get_name(self);
            CStr::from_ptr(ptr).to_str().unwrap().to_string()
        }
    }
    
    fn age(&self) -> i32 {
        unsafe {
            person_get_age(self) as i32
        }
    }
}

impl Drop for Person {
    fn drop(&mut self) {
        unsafe {
            person_free(self);
        }
    }
}

fn main() {
    let person = Person::new("Alice", 30);
    unsafe {
        let name = person.name();
        let age = person.age();
        println!("Name: {}, Age: {}", name, age);
    }
}
```

### 5. Callbacks từ Rust sang C

**Rust function callback cho C:**

```rust
use std::os::raw::c_void;

// Type alias cho callback
type Callback = extern "C" fn(i32) -> i32;

// Hàm C nhận callback
extern "C" {
    fn set_callback(cb: Callback);
    fn run_with_callback(data: i32) -> i32;
}

// Rust function được export sang C
#[no_mangle]
pub extern "C" fn rust_callback(x: i32) -> i32 {
    println!("Rust callback called with: {}", x);
    x * 2
}

// Tạo closure wrapper
fn create_callback_wrapper<F>(f: F) -> Callback 
where 
    F: Fn(i32) -> i32 + 'static,
{
    // Box và leak để có 'static lifetime
    let boxed: Box<F> = Box::new(f);
    let raw = Box::into_raw(boxed);
    
    extern "C" fn wrapper<F: Fn(i32) -> i32>(x: i32) -> i32 {
        unsafe {
            let f = &*raw;
            f(x)
        }
    }
    
    wrapper::<F>
}

fn main() {
    // Set callback trực tiếp
    unsafe {
        set_callback(rust_callback);
        let result = run_with_callback(10);
        println!("Result: {}", result); // 20
    }
    
    // Set callback với closure
    let callback = create_callback_wrapper(|x| {
        println!("Closure callback: {}", x);
        x + 100
    });
    
    unsafe {
        set_callback(callback);
        let result = run_with_callback(5);
        println!("Result: {}", result); // 105
    }
}
```

### 6. Export Rust sang C

**Tạo thư viện static/dynamic từ Rust:**

```rust
// lib.rs
use std::ffi::{CStr, CString};
use std::os::raw::c_char;

#[no_mangle]
pub extern "C" fn rust_hello() {
    println!("Hello from Rust!");
}

#[no_mangle]
pub extern "C" fn rust_add(a: i32, b: i32) -> i32 {
    a + b
}

#[no_mangle]
pub extern "C" fn rust_to_uppercase(input: *const c_char) -> *mut c_char {
    let c_str = unsafe { CStr::from_ptr(input) };
    let rust_str = c_str.to_str().unwrap();
    let uppercase = rust_str.to_uppercase();
    CString::new(uppercase).unwrap().into_raw()
}

#[no_mangle]
pub extern "C" fn rust_free_string(ptr: *mut c_char) {
    unsafe {
        if !ptr.is_null() {
            drop(CString::from_raw(ptr));
        }
    }
}

// Cargo.toml
// [lib]
// crate-type = ["cdylib", "staticlib"]
```

**C code sử dụng Rust:**

```c
// main.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Declare Rust functions
extern void rust_hello(void);
extern int rust_add(int a, int b);
extern char* rust_to_uppercase(const char* input);
extern void rust_free_string(char* ptr);

int main() {
    // Call Rust functions
    rust_hello();
    
    int sum = rust_add(10, 20);
    printf("Sum: %d\n", sum);
    
    char* upper = rust_to_uppercase("hello world");
    printf("Uppercase: %s\n", upper);
    rust_free_string(upper);
    
    return 0;
}
```

```bash
# Compile C with Rust library
# Build Rust library
cargo build --release

# Compile C
gcc -o myapp main.c -Ltarget/release -lmyapp -lpthread -ldl
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án: `cargo new ffi_example`**

**Cargo.toml:**
```toml
[package]
name = "ffi_example"
version = "0.1.0"

[dependencies]
libc = "0.2"

[build-dependencies]
cc = "1.0"

[lib]
crate-type = ["cdylib", "staticlib"]
```

**build.rs:**
```rust
fn main() {
    cc::Build::new()
        .file("src/math.c")
        .compile("math");
}
```

**src/math.c:**
```c
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

int32_t add_int32(int32_t a, int32_t b) {
    return a + b;
}

int32_t multiply_int32(int32_t a, int32_t b) {
    return a * b;
}

typedef struct {
    int32_t x;
    int32_t y;
} Point;

Point* point_new(int32_t x, int32_t y) {
    Point* p = (Point*)malloc(sizeof(Point));
    p->x = x;
    p->y = y;
    return p;
}

void point_free(Point* p) {
    free(p);
}

int32_t point_distance_squared(const Point* p) {
    return p->x * p->x + p->y * p->y;
}

char* reverse_string(const char* input) {
    size_t len = strlen(input);
    char* result = (char*)malloc(len + 1);
    for (size_t i = 0; i < len; i++) {
        result[i] = input[len - 1 - i];
    }
    result[len] = '\0';
    return result;
}

void free_string(char* ptr) {
    free(ptr);
}
```

**src/lib.rs:**
```rust
use std::ffi::{CStr, CString};
use std::os::raw::{c_int, c_char};
use libc::c_void;

// C functions
extern "C" {
    fn add_int32(a: c_int, b: c_int) -> c_int;
    fn multiply_int32(a: c_int, b: c_int) -> c_int;
    
    fn point_new(x: c_int, y: c_int) -> *mut c_void;
    fn point_free(p: *mut c_void);
    fn point_distance_squared(p: *const c_void) -> c_int;
    
    fn reverse_string(input: *const c_char) -> *mut c_char;
    fn free_string(ptr: *mut c_char);
}

// Rust wrapper functions
pub fn add(a: i32, b: i32) -> i32 {
    unsafe { add_int32(a, b) as i32 }
}

pub fn multiply(a: i32, b: i32) -> i32 {
    unsafe { multiply_int32(a, b) as i32 }
}

pub struct Point {
    ptr: *mut c_void,
}

impl Point {
    pub fn new(x: i32, y: i32) -> Self {
        Point {
            ptr: unsafe { point_new(x as c_int, y as c_int) },
        }
    }
    
    pub fn distance_squared(&self) -> i32 {
        unsafe { point_distance_squared(self.ptr) as i32 }
    }
}

impl Drop for Point {
    fn drop(&mut self) {
        unsafe { point_free(self.ptr) }
    }
}

pub fn reverse_string(s: &str) -> String {
    let c_str = CString::new(s).unwrap();
    unsafe {
        let ptr = reverse_string(c_str.as_ptr());
        let result = CStr::from_ptr(ptr).to_str().unwrap().to_string();
        free_string(ptr);
        result
    }
}

// Export Rust functions for C
#[no_mangle]
pub extern "C" fn rust_add(a: c_int, b: c_int) -> c_int {
    add(a, b)
}

#[no_mangle]
pub extern "C" fn rust_multiply(a: c_int, b: c_int) -> c_int {
    multiply(a, b)
}

#[no_mangle]
pub extern "C" fn rust_reverse(input: *const c_char) -> *mut c_char {
    let c_str = unsafe { CStr::from_ptr(input) };
    let rust_str = c_str.to_str().unwrap();
    let reversed = rust_str.chars().rev().collect::<String>();
    CString::new(reversed).unwrap().into_raw()
}

#[no_mangle]
pub extern "C" fn rust_free_string(ptr: *mut c_char) {
    unsafe {
        if !ptr.is_null() {
            drop(CString::from_raw(ptr));
        }
    }
}

#[no_mangle]
pub extern "C" fn rust_hello() {
    println!("Hello from Rust!");
}
```

**src/main.rs:**
```rust
mod lib;

fn main() {
    // Call C functions
    println!("Add: {}", lib::add(10, 20));
    println!("Multiply: {}", lib::multiply(10, 20));
    
    // Use C struct
    let point = lib::Point::new(3, 4);
    println!("Distance squared: {}", point.distance_squared());
    
    // Reverse string
    let reversed = lib::reverse_string("Hello, World!");
    println!("Reversed: {}", reversed);
    
    // Call C functions directly
    println!("\nCalling C functions directly:");
    unsafe {
        use lib::add_int32;
        println!("Direct add: {}", add_int32(100, 200));
    }
}
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: Math Library
// Tạo C library với các hàm:
// - factorial, fibonacci, is_prime
// Gọi từ Rust và so sánh với Rust implementation

// Bài 2: String Processing
// Tạo C functions để:
// - Count words
// - Find substring
// - Replace substring
// Wrap trong Rust safe functions

// Bài 3: File I/O
// Sử dụng C file operations (fopen, fread, etc.)
// Wrapper Rust với error handling

// Bài 4: Custom Data Structure
// Tạo C struct: LinkedList
// Operations: create, insert, delete, find
// Wrapper trong Rust với Drop

// Bài 5: Callback from C to Rust
// C function nhận callback
// Rust truyền closure vào C
// Xử lý events
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Khái niệm | Cú pháp | Mục đích |
|-----------|---------|----------|
| **extern "C"** | `extern "C" { ... }` | Gọi C functions |
| **#[no_mangle]** | `#[no_mangle] fn ...` | Export Rust sang C |
| **repr(C)** | `#[repr(C)] struct` | C-compatible layout |
| **CString** | `CString::new()` | Rust -> C string |
| **CStr** | `CStr::from_ptr()` | C -> Rust string |

---

## ⚡ MẸO HAY

1. **`libc` crate** - cung cấp C types và constants
2. **`cc` crate** - compile C code trong build.rs
3. **`bindgen`** - tự động tạo Rust bindings từ C headers
4. **`cbindgen`** - tạo C headers từ Rust code
5. **`cxx`** - safe FFI between Rust and C++

---

## 🔥 BÀI TẬP NÂNG CAO

```rust
// 1. FFI với OpenSSL
// Gọi thư viện crypto từ Rust
// Encrypt/decrypt data

// 2. GUI với GTK
// Gọi GTK C library từ Rust
// Tạo window với buttons

// 3. Game Engine Integration
// Integrate với SDL2
// Game loop, events, rendering

// 4. Database C API
// Gọi SQLite C API
// Execute queries, transactions

// 5. FFI Generator
// Tạo tool sinh bindings từ C headers
// Parse và generate Rust code
```

---

## ✅ CHECKLIST BÀI 19

- [ ] Gọi C functions từ Rust
- [ ] Làm việc với C strings
- [ ] Sử dụng C structs
- [ ] Export Rust functions cho C
- [ ] Callbacks và closures
- [ ] Memory management (malloc/free)
- [ ] Làm xong 5 bài tập cơ bản
- [ ] Thử bài tập nâng cao

---

**Hoàn thành bài tập, chia sẻ code để tôi review!**

Bài cuối cùng: **Bài 20 - Tối ưu hiệu suất** - viết Rust code nhanh nhất có thể! ⚡