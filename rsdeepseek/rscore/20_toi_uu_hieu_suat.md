Chào mừng đến **Bài 20 - Tối ưu hiệu suất**! ⚡

Đây là bài học cuối cùng trong lộ trình của chúng ta - **nghệ thuật viết Rust code cực nhanh**. Rust đã nhanh sẵn, nhưng chúng ta có thể làm cho nó nhanh hơn nữa!

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Hiểu Về Hiệu Suất trong Rust

**Các yếu tố ảnh hưởng đến hiệu suất:**

```rust
fn main() {
    // 1. Allocation (cấp phát bộ nhớ) - ĐẮT!
    let vec = Vec::new();  // Heap allocation
    
    // 2. Copy vs Move
    let x = 5;  // Copy (cheap)
    let s = String::from("hello");  // Move (cheap)
    let s2 = s.clone();  // Clone (expensive!)
    
    // 3. Bound checks
    let arr = [1, 2, 3];
    let val = arr[0];  // Bound check (safe)
    let val = unsafe { arr.get_unchecked(0) };  // No bound check (unsafe)
    
    // 4. Dynamic dispatch
    let x: Box<dyn Trait> = Box::new(Struct);  // Virtual call (slow)
    let x: impl Trait = Struct;  // Static dispatch (fast)
}
```

### 2. Zero-Cost Abstractions

**Rust abstractions không tốn chi phí runtime:**

```rust
// Iterator overhead? Không! Compiler sẽ optimize thành loop
fn sum_iter() -> i32 {
    (0..1000).filter(|x| x % 2 == 0).sum()
}

// Generic? Không overhead! Monomorphization
fn process<T: Processable>(item: T) {
    item.process();  // Inlined at compile time
}

// Async? Không có runtime overhead lớn!
async fn handle_request() {
    // Tokio runtime efficient
    let response = fetch_data().await;
}
```

### 3. Tối Ưu Collections

**Chọn collection phù hợp:**

```rust
use std::collections::*;

// 1. Vec - tốt nhất khi thêm/xóa ở cuối
let mut v = Vec::with_capacity(1000);  // Pre-allocate!

// 2. VecDeque - tốt cho thêm/xóa ở cả 2 đầu
let mut deque = VecDeque::with_capacity(1000);

// 3. HashMap - O(1) average, nhưng overhead cao
let mut map = HashMap::with_capacity_and_hasher(1000, DefaultHasher::default());

// 4. BTreeMap - O(log n), sorted keys
let mut btree = BTreeMap::new();

// 5. BinaryHeap - priority queue
let mut heap = BinaryHeap::new();

// 6. HashSet - unique items
let mut set = HashSet::with_capacity(1000);
```

**Tối ưu Vec và String:**

```rust
fn optimize_collections() {
    // 1. Pre-allocate
    let mut v = Vec::with_capacity(1000);
    for i in 0..1000 {
        v.push(i);  // No reallocation!
    }
    
    // 2. Reserve
    let mut s = String::with_capacity(1000);
    s.push_str("Hello");  // No reallocation
    
    // 3. Extend from iterator
    let mut v = Vec::new();
    v.extend(0..1000);  // Efficient
    
    // 4. collect with known size
    let v: Vec<i32> = (0..1000).collect();
    // Compiler knows size, pre-allocates!
    
    // 5. Vec::from_iter
    let v = Vec::from_iter(0..1000);
}
```

### 4. Tối Ưu Vòng Lặp và Iterator

**Iterators thường nhanh hơn loop thủ công:**

```rust
fn compare_loops(data: &[i32]) -> i32 {
    // Loop thủ công
    let mut sum = 0;
    for i in 0..data.len() {
        if data[i] % 2 == 0 {
            sum += data[i];
        }
    }
    sum
    
    // Iterator - compiler có thể auto-vectorize!
    // data.iter().filter(|&&x| x % 2 == 0).sum()
}

fn fast_iterations(data: &[i32]) {
    // 1. Use iterators - compiler optimizes better
    let _: Vec<_> = data.iter()
        .filter(|&&x| x > 0)
        .map(|&x| x * 2)
        .collect();
    
    // 2. Avoid unnecessary collect
    let sum = data.iter().sum::<i32>();  // No collect!
    
    // 3. Skip bound checks with chunks
    for chunk in data.chunks_exact(4) {
        // Process 4 elements at a time
        let [a, b, c, d] = chunk.try_into().unwrap();
        // ...
    }
    
    // 4. Use fold instead of manual loop
    let sum = data.iter().fold(0, |acc, &x| acc + x);
}
```

### 5. Memory Layout và Cache Efficiency

**Tối ưu cho CPU cache:**

```rust
#[derive(Debug)]
struct BadData {
    active: bool,      // 1 byte
    age: u32,          // 4 bytes (padding!)
    name: String,      // Heap pointer
    id: u64,           // 8 bytes
    // Total: 24 bytes + padding
}

#[repr(C, packed)]
struct GoodData {
    id: u64,           // 8 bytes
    age: u32,          // 4 bytes
    active: bool,      // 1 byte
    // Total: 13 bytes, packed
}

fn cache_efficient() {
    // 1. Use arrays for sequential access
    let data = [0u64; 1024];  // Cache-friendly!
    
    // 2. Struct of arrays vs Array of structs
    struct SoA {
        x: Vec<f64>,
        y: Vec<f64>,
        z: Vec<f64>,
    }
    struct AoS {
        points: Vec<Point>,
    }
    // SoA better for vectorized operations
    
    // 3. Use fixed-size arrays when possible
    let arr: [i32; 1000] = [0; 1000];  // On stack!
    
    // 4. Avoid Vec of small structs (many allocations)
    // Use flat arrays instead
}
```

### 6. Parallel Processing

**Sử dụng Rayon cho parallel processing:**

```toml
[dependencies]
rayon = "1.8"
```

```rust
use rayon::prelude::*;

fn parallel_operations(data: &[i32]) {
    // 1. Parallel iterator
    let sum: i32 = data.par_iter().sum();
    
    // 2. Parallel map
    let doubled: Vec<i32> = data.par_iter()
        .map(|&x| x * 2)
        .collect();
    
    // 3. Parallel filter
    let evens: Vec<i32> = data.par_iter()
        .filter(|&&x| x % 2 == 0)
        .cloned()
        .collect();
    
    // 4. Parallel fold
    let sum = data.par_iter()
        .fold(|| 0, |acc, &x| acc + x)
        .sum();
    
    // 5. Parallel sort
    let mut data = data.to_vec();
    data.par_sort_unstable();  // Faster than stable sort!
}

// Rayon với custom struct
#[derive(Debug)]
struct BigData {
    numbers: Vec<f64>,
}

impl BigData {
    fn process_parallel(&mut self) {
        self.numbers.par_iter_mut()
            .for_each(|x| *x = x.sqrt().powi(2));
    }
}
```

### 7. Profiling và Benchmarking

**Công cụ profiling:**

```bash
# 1. Linux perf
perf record --call-graph dwarf target/release/myapp
perf report

# 2. Flamegraph
cargo install flamegraph
cargo flamegraph --bin myapp

# 3. Valgrind
valgrind --tool=callgrind target/release/myapp
kcachegrind callgrind.out.*

# 4. Windows (Windows Performance Recorder)
# 5. Mac (Instruments)
```

**Benchmark với Criterion:**

```rust
use criterion::*;

fn bench_operations(c: &mut Criterion) {
    let data: Vec<i32> = (0..10000).collect();
    
    let mut group = c.benchmark_group("Sum operations");
    
    group.bench_function("loop", |b| {
        b.iter(|| {
            let mut sum = 0;
            for i in 0..data.len() {
                sum += data[i];
            }
            sum
        })
    });
    
    group.bench_function("iterator", |b| {
        b.iter(|| data.iter().sum::<i32>())
    });
    
    group.bench_function("parallel", |b| {
        b.iter(|| {
            use rayon::prelude::*;
            data.par_iter().sum::<i32>()
        })
    });
    
    group.finish();
}

criterion_group!(benches, bench_operations);
criterion_main!(benches);
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án: `cargo new optimization_workshop --bin`**

**Cargo.toml:**
```toml
[dependencies]
rayon = "1.8"
rand = "0.8"
criterion = "0.5"

[[bench]]
name = "optimization"
harness = false
```

**src/main.rs:**
```rust
use rayon::prelude::*;
use rand::Rng;
use std::time::Instant;

// 1. Bad implementation
fn bad_join_strings(words: &[String]) -> String {
    let mut result = String::new();
    for word in words {
        result.push_str(word);
    }
    result
}

// 2. Good implementation
fn good_join_strings(words: &[String]) -> String {
    let capacity = words.iter().map(|s| s.len()).sum();
    let mut result = String::with_capacity(capacity);
    for word in words {
        result.push_str(word);
    }
    result
}

// 3. Best implementation
fn best_join_strings(words: &[String]) -> String {
    words.concat()  // Uses pre-allocation internally
}

// 4. Optimized matrix multiplication
fn matrix_multiply(a: &[Vec<f64>], b: &[Vec<f64>]) -> Vec<Vec<f64>> {
    let n = a.len();
    let m = b[0].len();
    let p = b.len();
    
    // Pre-allocate
    let mut result = vec![vec![0.0; m]; n];
    
    // Optimized loop order (i, k, j) for cache efficiency
    for i in 0..n {
        for k in 0..p {
            let aik = a[i][k];
            if aik != 0.0 {
                for j in 0..m {
                    result[i][j] += aik * b[k][j];
                }
            }
        }
    }
    
    result
}

// 5. Parallel matrix multiplication
fn parallel_matrix_multiply(a: &[Vec<f64>], b: &[Vec<f64>]) -> Vec<Vec<f64>> {
    let n = a.len();
    let m = b[0].len();
    let p = b.len();
    
    let result = (0..n).into_par_iter()
        .map(|i| {
            let mut row = vec![0.0; m];
            for k in 0..p {
                let aik = a[i][k];
                if aik != 0.0 {
                    for j in 0..m {
                        row[j] += aik * b[k][j];
                    }
                }
            }
            row
        })
        .collect();
    
    result
}

fn main() {
    // Generate test data
    let words: Vec<String> = (0..1000)
        .map(|_| format!("word_{}", rand::thread_rng().gen_range(0..1000)))
        .collect();
    
    // Compare string joining methods
    let start = Instant::now();
    let _ = bad_join_strings(&words);
    println!("Bad join: {:?}", start.elapsed());
    
    let start = Instant::now();
    let _ = good_join_strings(&words);
    println!("Good join: {:?}", start.elapsed());
    
    let start = Instant::now();
    let _ = best_join_strings(&words);
    println!("Best join: {:?}", start.elapsed());
    
    // Matrix multiplication
    let size = 200;
    let mut rng = rand::thread_rng();
    let a: Vec<Vec<f64>> = (0..size)
        .map(|_| (0..size).map(|_| rng.gen()).collect())
        .collect();
    let b: Vec<Vec<f64>> = (0..size)
        .map(|_| (0..size).map(|_| rng.gen()).collect())
        .collect();
    
    let start = Instant::now();
    let _ = matrix_multiply(&a, &b);
    println!("Matrix multiply (sequential): {:?}", start.elapsed());
    
    let start = Instant::now();
    let _ = parallel_matrix_multiply(&a, &b);
    println!("Matrix multiply (parallel): {:?}", start.elapsed());
}
```

**benches/optimization.rs:**
```rust
use criterion::*;
use rand::Rng;

fn generate_data(size: usize) -> Vec<i32> {
    let mut rng = rand::thread_rng();
    (0..size).map(|_| rng.gen_range(0..1000)).collect()
}

fn bench_operations(c: &mut Criterion) {
    let data = generate_data(100000);
    
    let mut group = c.benchmark_group("Data Processing");
    
    group.bench_function("sequential", |b| {
        b.iter(|| {
            let mut sum = 0;
            for &x in &data {
                if x % 2 == 0 {
                    sum += x;
                }
            }
            sum
        })
    });
    
    group.bench_function("iterator", |b| {
        b.iter(|| {
            data.iter()
                .filter(|&&x| x % 2 == 0)
                .sum::<i32>()
        })
    });
    
    group.bench_function("parallel", |b| {
        b.iter(|| {
            use rayon::prelude::*;
            data.par_iter()
                .filter(|&&x| x % 2 == 0)
                .sum::<i32>()
        })
    });
    
    group.finish();
}

criterion_group!(benches, bench_operations);
criterion_main!(benches);
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: Optimize string builder
// Tối ưu hàm format_many nhận nhiều strings
// So sánh các approaches

// Bài 2: Optimize vector operations
// Tìm cách nhanh nhất để:
// - Sum all elements
// - Find max/min
// - Filter and transform

// Bài 3: Cache optimization
// Restructure data for cache efficiency
// Compare sequential vs random access

// Bài 4: Parallel processing
// Chọn problem phù hợp cho parallel
// Implement với Rayon

// Bài 5: Benchmarking
// Tạo benchmark suite
// So sánh các implementations
// Document performance characteristics
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Kỹ thuật | Cách áp dụng | Lợi ích |
|-----------|--------------|---------|
| **Pre-allocation** | `Vec::with_capacity()` | Giảm reallocation |
| **Iterators** | `.iter().map().filter()` | Auto-vectorization |
| **Parallel** | `rayon::par_iter()` | Đa luồng |
| **Cache-friendly** | `#[repr(C)]`, arrays | Tốc độ memory |
| **Profiling** | `perf`, `flamegraph` | Tìm bottlenecks |

---

## ⚡ MẸO HAY

1. **Release mode** - `cargo build --release`
2. **LTO** - `lto = true` trong Cargo.toml
3. **Codegen units** - `codegen-units = 1`
4. **Target CPU** - `target-cpu = native`
5. **Profiling** - đo trước khi optimize!

---

## 🔥 BÀI TẬP NÂNG CAO

```rust
// 1. SIMD Optimization
// Sử dụng packed_simd hoặc std::simd
// Vectorize operations

// 2. Lock-free Data Structures
// Implement concurrent queue
// Use atomic operations

// 3. Memory Pool
// Custom allocator
// Reuse memory for performance

// 4. Zero-copy Parsing
// Parse data without allocations
// Use bytes and slice

// 5. Custom Hash Function
// Optimize HashMap with faster hasher
// ahash or fxhash
```

---

## ✅ CHECKLIST FINAL

- [ ] Hiểu về allocations và copies
- [ ] Biết cách pre-allocate
- [ ] Sử dụng iterators hiệu quả
- [ ] Parallel processing với Rayon
- [ ] Cache-friendly data structures
- [ ] Profiling và benchmarking
- [ ] Làm xong 5 bài tập
- [ ] Thử bài tập nâng cao
- [ ] Apply vào project thực tế

---

## 🎉 CHÚC MỪNG BẠN!

Bạn đã hoàn thành toàn bộ lộ trình 20 bài học! 

**Con đường tiếp theo:**

1. **Thực hành** - Xây dựng project thực tế
2. **Contributing** - Đóng góp cho open-source
3. **Ecosystem** - Tìm hiểu các crate phổ biến
4. **Advanced** - Unsafe code, async deeper, FFI

**Always remember:**
> Rust is not just a language, it's a mindset. 
> It's about writing correct, safe, and fast code.
> Keep learning, keep building! 🦀

**Nếu có thắc mắc, đừng ngần ngại hỏi lại nhé!**