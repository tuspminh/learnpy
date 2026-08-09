fn fibonacci_bottom_up(n: u32) -> u128 {
    // Trường hợp cơ bản
    if n == 0 { return 0; }
    if n == 1 { return 1; }
    // if n <= 1 { return n.into(); }
    // Hai biến lưu trạng thái trước đó (tương đương bảng DP tối giản)
    let mut prev2: u128 = 0; // F(n-2)
    let mut prev1: u128 = 1; // F(n-1)
    let mut current: u128 = 0;

    // Vòng lặp tính toán từ dưới lên
    for _ in 2..=n {
        // current = F(n-1) + F(n-2)
        // Dùng checked_add để phòng tránh tràn bộ nhớ một cách an toàn
        current = match prev1.checked_add(prev2) {
            Some(val) => val,
            None => {                
                println!("tran bo nho");
                return 0; 
            }
        };
        
        // Cập nhật lại hai trạng thái trước đó cho vòng lặp tiếp theo
        prev2 = prev1;
        prev1 = current;
    }

    current
}

fn main() {
    let n = 150;
    let start_time = std::time::Instant::now();
    
    let result = fibonacci_bottom_up(n);
    
    let duration = start_time.elapsed();
    
    println!("Số Fibonacci thứ {} là: {}", n, result);
    println!("Thời gian thực thi của Rust: {:?}", duration);
}
