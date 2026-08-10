Dưới đây là mã nguồn Rust để tính số Fibonacci bằng phương pháp Quy hoạch động (Bottom-Up) với độ tối ưu cao nhất [tốc độ hệ thống, độ phức tạp thời gian $O(n)$ và bộ nhớ $O(1)$].
Vì số Fibonacci tăng lên rất nhanh, nếu dùng kiểu dữ liệu số nguyên thông thường như u64 sẽ sớm bị tràn bộ nhớ (chỉ tính được tối đa tới $F_{93}$). Đoạn code dưới đây sử dụng kiểu số nguyên lớn nhất mặc định của Rust là u128 giúp bạn tính được tới $F_{186}$.
------------------------------
## 1. Mã nguồn Rust (Tối ưu Quy hoạch động)

fn fibonacci_bottom_up(n: u32) -> u128 {
    // Trường hợp cơ bản
    if n == 0 { return 0; }
    if n == 1 { return 1; }

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
                println!("Cảnh báo: Bị tràn bộ nhớ ở bước thứ {}!", _);
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

------------------------------
## 2. Điểm vượt trội của Rust trong bài toán này

* Tốc độ siêu việt: Thời gian thực thi cho hàm trên trong Rust thường chỉ mất khoảng vài chục đến vài trăm nano giây (1 nano giây = 1/1.000.000.000 giây), nhanh hơn Python hàng trăm lần.
* An toàn bộ nhớ tuyệt đối: Hàm checked_add giúp chương trình tự động phát hiện nếu kết quả vượt quá giới hạn lưu trữ của kiểu u128 chứ không âm thầm trả về kết quả sai như C/C++.
* Không tốn bộ nhớ đệm: Nhờ kỹ thuật cuốn chiếu 2 biến, Rust không cần cấp phát mảng (Vector) trên bộ nhớ Heap, giúp CPU xử lý dữ liệu trực tiếp trên các thanh ghi (Registers) siêu tốc.

------------------------------
Bạn có muốn áp dụng tư duy Quy hoạch động này để giải quyết một bài toán thực tế hơn như bài toán đổi tiền (Coin Change) hay tìm đường đi ngắn nhất trên mê cung lưới bằng Python và Rust không?

