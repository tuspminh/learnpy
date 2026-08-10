Trong Rust, để làm việc với các đơn vị đo thời gian, bạn sẽ sử dụng module std::time từ thư viện chuẩn (hoặc thư viện ngoài chrono nếu cần xử lý lịch, múi giờ phức tạp).
Hạ tầng đo thời gian của Rust được xây dựng xung quanh hai khái niệm cốt lõi: Thời lượng (Duration) và Thời điểm (Instant / SystemTime).
------------------------------
## 1. Đo khoảng thời gian với std::time::Duration
Duration đại diện cho một khoảng thời gian (span of time). Trong bộ nhớ, nó được lưu dưới dạng một tuple gồm hai phần: số giây (u64) và số nano giây (u32) để đạt độ chính xác cực cao.
Rust hỗ trợ sẵn các đơn vị đo từ lớn đến siêu nhỏ thông qua các hàm khởi tạo:

* Duration::from_secs(u64): Giây (s)
* Duration::from_millis(u64): Miligiây (ms = 10⁻³ s)
* Duration::from_micros(u64): Microgiây (μ s = 10⁻⁶ s)
* Duration::from_nanos(u64): Nanogiây (ns = 10⁻⁹ s)

## Các hàm chuyển đổi ngược lại (Lấy giá trị số thô):
Khi đã có một biến Duration, bạn có thể trích xuất giá trị số thô của từng đơn vị bằng các hàm:

* .as_secs(): Trả về số giây nguyên.
* .as_millis() / .as_micros() / .as_nanos(): Quy đổi toàn bộ khoảng thời gian đó ra đơn vị tương ứng (trả về kiểu u128).
* .subsec_millis() / .subsec_nanos(): Chỉ lấy phần lẻ phía sau dấu phẩy của giây.

------------------------------
## 2. Hai cách đo mốc thời gian (Timestamps)
Rust tách biệt rõ ràng giữa thời gian dùng để đo hiệu năng và thời gian dùng để hiển thị đồng hồ.
## Cách A: std::time::Instant (Đo khoảng cách / Đơn điệu)
Dùng để đo thời gian chạy của code, benchmark hiệu năng.

* Đặc điểm: Nó sử dụng đồng hồ đơn điệu (monotonic clock) của hệ điều hành. Thời gian này chỉ có tiến, không bao giờ lùi và không bị ảnh hưởng bởi việc người dùng thay đổi giờ hệ thống hoặc cập nhật giờ mùa hè (DST).
* Ví dụ ứng dụng: Đo xem một hàm chạy mất bao nhiêu miligiây.

use std::time::Instant;use std::thread;
fn main() {
    let start = Instant::now(); // Lấy mốc thời gian hiện tại
    
    // Giả lập một tác vụ chạy mất 50 miligiây
    thread::sleep(std::time::Duration::from_millis(50));
    
    let duration = start.elapsed(); // Tính khoảng thời gian đã trôi qua
    println!("Tác vụ chạy mất: {} ms ({} ns)", duration.as_millis(), duration.as_nanos());
}

## Cách B: std::time::SystemTime (Thời gian hệ thống / Đồng hồ treo tường)
Dùng khi bạn cần lưu thời gian file được tạo, hoặc gửi timestamp lên server.

* Đặc điểm: Nó lấy thời gian từ đồng hồ hệ thống (Wall-clock time). Thời gian này có thể bị nhảy lùi lại nếu hệ điều hành tự động đồng bộ giờ qua Internet (NTP sync) hoặc người dùng chỉnh lại giờ máy tính.
* Ví dụ ứng dụng: Lấy thời gian Unix Epoch (số giây tính từ ngày 01/01/1970).

use std::time::{SystemTime, UNIX_EPOCH};
fn main() {
    match SystemTime::now().duration_since(UNIX_EPOCH) {
        Ok(n) => println!("Unix Timestamp hiện tại: {} giây", n.as_secs()),
        Err(_) => panic!("Đồng hồ hệ thống đang bị chỉnh lùi về trước năm 1970!"),
    }
}

------------------------------
## 3. Sử dụng thư viện ngoài chrono (Khi cần xử lý nâng cao)
Thư viện chuẩn std::time không hỗ trợ các đơn vị như Phút, Giờ, Ngày, Tháng, Năm hoặc Múi giờ (Timezone) vì chúng phụ thuộc vào lịch pháp phức tạp. Nếu cần làm việc với các đơn vị này, bạn bắt buộc phải dùng crate chuẩn công nghiệp là chrono.
Thêm vào Cargo.toml:

[dependencies]
chrono = "0.4"

Cách sử dụng:

use chrono::{Utc, Local, Duration};
fn main() {
    // 1. Lấy giờ hiện tại theo UTC hoặc Giờ địa phương
    let now_utc = Utc::now();
    let now_local = Local::now();
    println!("Giờ máy tính của bạn: {}", now_local.format("%Y-%m-%d %H:%M:%S"));

    // 2. Chrono cho phép khởi tạo khoảng thời gian bằng các đơn vị lớn hơn
    let tuân = Duration::weeks(1);
    let ngay = Duration::days(5);
    let gio = Duration::hours(2);
    
    // 3. Tính toán cộng trừ ngày giờ cực kỳ tiện lợi
    let tuong_lai = now_local + ngay + gio;
    println!("Thời gian sau 5 ngày 2 giờ nữa: {}", tuong_lai);
}

Nếu bạn đang viết code, hãy cho tôi biết:

* Bạn đang cần đo tốc độ thực thi của code (Benchmark) để tối ưu thuật toán?
* Hay bạn cần tính toán lịch pháp (ví dụ: cộng thêm 30 ngày vào ngày hiện tại, tìm ngày thứ Hai của tuần tới)?


