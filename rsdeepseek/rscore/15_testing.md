Chào mừng đến **Bài 15 - Testing và Benchmarking**! 🧪

Đây là bài học về **đảm bảo chất lượng code** - viết test để tìm lỗi sớm, và benchmark để đo hiệu suất. Rust có hệ thống testing tích hợp tuyệt vời!

---

## 📚 LÝ THUYẾT CỐT LÕI

### 1. Unit Testing (Test đơn vị)

**Test các hàm nhỏ, kiểm tra từng phần của code:**

```rust
// Code cần test
fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err("Cannot divide by zero".to_string())
    } else {
        Ok(a / b)
    }
}

// Unit tests
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
        assert_eq!(add(-1, 1), 0);
    }
    
    #[test]
    fn test_divide_success() {
        assert_eq!(divide(10, 2), Ok(5));
    }
    
    #[test]
    fn test_divide_by_zero() {
        assert_eq!(divide(10, 0), Err("Cannot divide by zero".to_string()));
    }
}
```

### 2. Assertions (Khẳng định)

**Các macro assert thường dùng:**

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_assertions() {
        // assert! - kiểm tra boolean
        assert!(true);
        assert!(2 + 2 == 4);
        
        // assert_eq! - kiểm tra bằng nhau
        assert_eq!(2 + 2, 4);
        assert_eq!(vec![1, 2], vec![1, 2]);
        
        // assert_ne! - kiểm tra khác nhau
        assert_ne!(2 + 2, 5);
        assert_ne!("hello", "world");
        
        // assert! với custom message
        assert!(
            2 + 2 == 4,
            "Math is broken! 2 + 2 should be 4, got {}",
            2 + 2
        );
        
        // assert_eq! với custom message
        assert_eq!(
            divide(10, 2),
            Ok(5),
            "10 / 2 should be 5"
        );
    }
}
```

### 3. Integration Testing (Test tích hợp)

**Test từ bên ngoài, test các module tương tác với nhau:**

```
// File structure:
// src/
//   lib.rs
//   calculator.rs
// tests/
//   integration_test.rs  (integration tests)
```

**src/lib.rs:**
```rust
pub mod calculator;

pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

**src/calculator.rs:**
```rust
pub fn multiply(a: i32, b: i32) -> i32 {
    a * b
}
```

**tests/integration_test.rs:**
```rust
use bai15_testing::add;
use bai15_testing::calculator::multiply;

#[test]
fn test_add_integration() {
    assert_eq!(add(2, 3), 5);
    assert_eq!(multiply(2, 3), 6);
}

#[test]
fn test_combined_operations() {
    let result = multiply(add(2, 3), add(4, 5));
    assert_eq!(result, 45);
}
```

### 4. Testing with Panic (Kiểm tra panic)

**Kiểm tra code có panic đúng lúc:**

```rust
fn divide_unwrap(a: i32, b: i32) -> i32 {
    if b == 0 {
        panic!("Cannot divide by zero!");
    }
    a / b
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    #[should_panic(expected = "Cannot divide by zero!")]
    fn test_divide_unwrap_panic() {
        divide_unwrap(10, 0);
    }
    
    #[test]
    #[should_panic]
    fn test_divide_unwrap_panic_simple() {
        divide_unwrap(10, 0);
    }
}
```

### 5. Test với Result

**Test có thể trả về Result:</strong>

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_divide_result() -> Result<(), String> {
        let result = divide(10, 2)?;
        assert_eq!(result, 5);
        Ok(())
    }
    
    #[test]
    fn test_divide_multiple() -> Result<(), String> {
        let tests = vec![
            (10, 2, 5),
            (20, 4, 5),
            (100, 10, 10),
        ];
        
        for (a, b, expected) in tests {
            let result = divide(a, b)?;
            assert_eq!(result, expected);
        }
        Ok(())
    }
}
```

### 6. Test Helpers và Setup

**Dùng helper functions để viết test DRY:**

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    // Helper function
    fn create_test_data() -> Vec<i32> {
        vec![1, 2, 3, 4, 5]
    }
    
    #[test]
    fn test_sum() {
        let data = create_test_data();
        let sum: i32 = data.iter().sum();
        assert_eq!(sum, 15);
    }
    
    #[test]
    fn test_average() {
        let data = create_test_data();
        let avg = data.iter().sum::<i32>() / data.len() as i32;
        assert_eq!(avg, 3);
    }
    
    // Shared setup - có thể dùng module
    mod test_utils {
        use super::*;
        
        pub struct TestContext {
            pub data: Vec<i32>,
            pub expected_sum: i32,
        }
        
        impl TestContext {
            pub fn new() -> Self {
                TestContext {
                    data: vec![1, 2, 3, 4, 5],
                    expected_sum: 15,
                }
            }
        }
    }
    
    #[test]
    fn test_with_context() {
        let ctx = test_utils::TestContext::new();
        let sum: i32 = ctx.data.iter().sum();
        assert_eq!(sum, ctx.expected_sum);
    }
}
```

### 7. Benchmarking (Đo hiệu suất)

**Dùng criterion để benchmark:**

```toml
[dev-dependencies]
criterion = "0.5"

[[bench]]
name = "my_benchmark"
harness = false
```

**benches/my_benchmark.rs:**
```rust
use criterion::{criterion_group, criterion_main, Criterion};

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

fn bench_fibonacci(c: &mut Criterion) {
    let mut group = c.benchmark_group("Fibonacci");
    
    group.bench_function("recursive 20", |b| {
        b.iter(|| fibonacci_recursive(20))
    });
    
    group.bench_function("iterative 20", |b| {
        b.iter(|| fibonacci_iterative(20))
    });
    
    group.finish();
}

criterion_group!(benches, bench_fibonacci);
criterion_main!(benches);
```

### 8. Documentation Tests

**Test examples trong documentation:**

```rust
/// Tính tổng của hai số
/// 
/// # Examples
/// 
/// ```
/// let result = my_crate::add(2, 3);
/// assert_eq!(result, 5);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

/// Chia hai số, trả về Result
///
/// # Examples
///
/// ```
/// use my_crate::divide;
///
/// assert_eq!(divide(10, 2), Ok(5));
/// assert_eq!(divide(10, 0), Err("Cannot divide by zero".to_string()));
/// ```
pub fn divide(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err("Cannot divide by zero".to_string())
    } else {
        Ok(a / b)
    }
}
```

---

## 💻 THỰC HÀNH NGAY

**Tạo dự án: `cargo new bai15_testing`**

```rust
// src/lib.rs

/// Calculator module for basic arithmetic
pub mod calculator {
    pub fn add(a: i32, b: i32) -> i32 {
        a + b
    }
    
    pub fn subtract(a: i32, b: i32) -> i32 {
        a - b
    }
    
    pub fn multiply(a: i32, b: i32) -> i32 {
        a * b
    }
    
    pub fn divide(a: i32, b: i32) -> Result<i32, String> {
        if b == 0 {
            Err("Division by zero".to_string())
        } else {
            Ok(a / b)
        }
    }
}

/// Process a vector of numbers
pub fn process_numbers(numbers: &[i32]) -> (i32, i32, f64) {
    let sum: i32 = numbers.iter().sum();
    let count = numbers.len();
    let avg = if count > 0 {
        sum as f64 / count as f64
    } else {
        0.0
    };
    (sum, count as i32, avg)
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::calculator::*;
    
    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
        assert_eq!(add(-1, 1), 0);
        assert_eq!(add(0, 0), 0);
    }
    
    #[test]
    fn test_subtract() {
        assert_eq!(subtract(10, 5), 5);
        assert_eq!(subtract(5, 10), -5);
    }
    
    #[test]
    fn test_multiply() {
        assert_eq!(multiply(2, 3), 6);
        assert_eq!(multiply(-2, 3), -6);
        assert_eq!(multiply(0, 5), 0);
    }
    
    #[test]
    fn test_divide_success() {
        assert_eq!(divide(10, 2), Ok(5));
        assert_eq!(divide(0, 5), Ok(0));
        assert_eq!(divide(-10, 2), Ok(-5));
    }
    
    #[test]
    fn test_divide_by_zero() {
        assert_eq!(divide(10, 0), Err("Division by zero".to_string()));
    }
    
    #[test]
    fn test_process_numbers() {
        let numbers = vec![1, 2, 3, 4, 5];
        let (sum, count, avg) = process_numbers(&numbers);
        assert_eq!(sum, 15);
        assert_eq!(count, 5);
        assert_eq!(avg, 3.0);
    }
    
    #[test]
    fn test_process_numbers_empty() {
        let numbers: Vec<i32> = vec![];
        let (sum, count, avg) = process_numbers(&numbers);
        assert_eq!(sum, 0);
        assert_eq!(count, 0);
        assert_eq!(avg, 0.0);
    }
    
    #[test]
    #[should_panic]
    fn test_panic_example() {
        let numbers = vec![1, 2, 3];
        let _ = numbers[10];  // This will panic
    }
    
    #[test]
    fn test_result_type() -> Result<(), String> {
        assert_eq!(divide(10, 2)?, 5);
        assert_eq!(divide(20, 4)?, 5);
        Ok(())
    }
}
```

**tests/integration_test.rs:**
```rust
use bai15_testing::calculator::*;
use bai15_testing::process_numbers;

#[test]
fn test_calculator_integration() {
    let result = multiply(add(2, 3), divide(10, 2).unwrap());
    assert_eq!(result, 25);
}

#[test]
fn test_process_numbers_integration() {
    let numbers = vec![1, 2, 3, 4, 5];
    let (sum, count, avg) = process_numbers(&numbers);
    assert_eq!(sum, 15);
    assert_eq!(count, 5);
    assert_eq!(avg, 3.0);
}
```

---

## 📝 BÀI TẬP BẮT BUỘC

```rust
// Bài 1: Viết test cho các hàm sau
// - factorial(n: u64) -> u64
// - is_prime(n: u64) -> bool
// - fibonacci(n: u64) -> u64

// Bài 2: Test với border cases
// Test các edge cases:
// - Số âm
// - Số 0
// - Số rất lớn
// - Số đặc biệt

// Bài 3: Test error handling
// Viết hàm validate_email(email: &str) -> Result<(), String>
// Test các trường hợp:
// - Email hợp lệ
// - Thiếu @
// - Thiếu domain
// - Có khoảng trắng

// Bài 4: Integration test
// Tạo module math với các hàm:
// - average, median, mode, standard_deviation
// Viết integration tests cho các kết hợp

// Bài 5: Documentation tests
// Thêm doc comments và examples cho các function
// Chạy `cargo test --doc` để kiểm tra
```

---

## 🎯 LƯU Ý QUAN TRỌNG

| Khái niệm            | Cú pháp                 | Sử dụng            |
| -------------------- | ----------------------- | ------------------ |
| **Unit test**        | `#[test]`               | Test từng function |
| **Integration test** | `tests/` folder         | Test từ bên ngoài  |
| **Assertion**        | `assert!`, `assert_eq!` | Kiểm tra kết quả   |
| **Should panic**     | `#[should_panic]`       | Kiểm tra panic     |
| **Test Result**      | `-> Result<(), E>`      | Test không panic   |

---

## ⚡ MẸO HAY

1. **`cargo test`** - chạy tất cả tests
2. **`cargo test test_name`** - chạy test cụ thể
3. **`cargo test -- --nocapture`** - hiển thị output
4. **`cargo test -- --test`** - chỉ chạy integration tests
5. **`cargo bench`** - chạy benchmarks
6. **`cargo test -- --ignored`** - chạy ignored tests

---

## 🔥 BÀI TẬP NÂNG CAO

```rust
// 1. Property-based testing với proptest
// Viết tests cho các properties:
// - Phép cộng có tính giao hoán
// - Phép nhân phân phối với phép cộng
// - Factorial luôn dương

// 2. Mocking và test doubles
// Tạo trait Database và mock implementation
// Test business logic với mock database

// 3. Performance testing
// So sánh các implementation khác nhau
// Test với dữ liệu lớn
// Đo memory usage

// 4. Cross-platform testing
// Chạy tests trên nhiều platform
// Test với environment variables
// Test với file system

// 5. Continuous Integration
// Tạo CI pipeline với GitHub Actions
// Auto-run tests trên mỗi PR
// Code coverage với tarpaulin
```

---

## ✅ CHECKLIST BÀI 15

- [ ] Hiểu unit testing
- [ ] Biết integration testing
- [ ] Sử dụng assertions
- [ ] Testing with panic
- [ ] Testing with Result
- [ ] Documentation tests
- [ ] Benchmark với criterion
- [ ] Làm xong 5 bài tập cơ bản
- [ ] Thử bài tập nâng cao

---

**Hoàn thành bài tập, chia sẻ code để tôi review!**

Bài tiếp theo: **Bài 16 - Xây dựng CLI App với Clap** - ứng dụng command-line thực tế! 🖥️