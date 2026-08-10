Để chuyển một chuỗi tiếng Việt hoặc chuỗi có dấu thành dạng slug (ký tự thường, không dấu, ngăn cách bằng dấu gạch ngang -), bạn cần thực hiện 2 việc chính: loại bỏ dấu tiếng Việt và xóa các ký tự đặc biệt.
Trong Rust, cách tối ưu nhất là dùng thư viện có sẵn để xử lý chuẩn Unicode. Dưới đây là giải pháp dùng thư viện và giải pháp viết tay.
## Cách 1: Sử dụng thư viện slug (Khuyên dùng)
Thư viện slug xử lý cực tốt các ký tự Unicode và chữ có dấu (bao gồm cả tiếng Việt).
Bước 1: Thêm dependency vào Cargo.toml:

[dependencies]
slug = "0.1.5"

Bước 2: Viết code:

use slug::slugify;
fn main() {
    let title = "Deep Dive về String và literal string trong Rust!";
    let slug = slugify(title);
    
    println!("{}", slug); 
    // Kết quả: deep-dive-ve-string-va-literal-string-trong-rust
}

------------------------------
## Cách 2: Tự viết hàm xử lý (Không dùng thư viện ngoài)
Nếu bạn không muốn thêm dependency, bạn có thể tự viết một hàm chuyển đổi. Hàm này sẽ thay thế thủ công các chữ cái tiếng Việt có dấu, chuyển thành chữ thường, loại bỏ ký tự đặc biệt và thay khoảng trắng thành dấu -.

fn to_slug(input: &str) -> String {
    let mut result = input
        .to_lowercase()
        // 1. Thay thế thủ công các ký tự tiếng Việt phổ biến
        .chars()
        .map(|c| match c {
            'à' | 'á' | 'ạ' | 'ả' | 'ã' | 'â' | 'ầ' | 'ấ' | 'ậ' | 'ẩ' | 'ẫ' | 'ă' | 'ằ' | 'ắ' | 'ặ' | 'ẳ' | 'ẵ' => 'a',
            'è' | 'é' | 'ẹ' | 'ẻ' | 'ẽ' | 'ê' | 'ề' | 'ế' | 'ệ' | 'ể' | 'ễ' => 'e',
            'ì' | 'í' | 'ị' | 'ỉ' | 'ĩ' => 'i',
            'ò' | 'ó' | 'ọ' | 'ỏ' | 'õ' | 'ô' | 'ồ' | 'ố' | 'ộ' | 'ổ' | 'ỗ' | 'ơ' | 'ờ' | 'ớ' | 'ợ' | 'ở' | 'ỡ' => 'o',
            'ù' | 'ú' | 'ụ' | 'ủ' | 'ũ' | 'ư' | 'ừ' | 'ứ' | 'ự' | 'ử' | 'ữ' => 'u',
            'ỳ' | 'ý' | 'ỵ' | 'ỷ' | 'ỹ' => 'y',
            'đ' => 'd',
            _ => c,
        })
        .collect::<String>();

    // 2. Chỉ giữ lại chữ cái, chữ số, khoảng trắng và dấu gạch ngang
    result = result.chars()
        .filter(|c| c.is_alphanumeric() || c.is_whitespace() || *c == '-')
        .collect();

    // 3. Thay khoảng trắng thành '-', gộp nhiều dấu '-' liên tiếp thành một
    let mut slug = String::new();
    let mut last_was_dash = false;

    for c in result.chars() {
        if c.is_whitespace() || c == '-' {
            if !last_was_dash {
                slug.push('-');
                last_was_dash = true;
            }
        } else {
            slug.push(c);
            last_was_dash = false;
        }
    }

    // 4. Cắt tỉa dấu '-' thừa ở đầu và cuối chuỗi
    slug.trim_matches('-').to_string()
}
fn main() {
    let text = "Học Rust rất hay, đúng không?!";
    println!("{}", to_slug(text));
    // Kết quả: hoc-rust-rat-hay-dung-khong
}

Hãy cho tôi biết:

* Bạn muốn sử dụng thư viện ngoài cho nhanh gọn hay bắt buộc phải tự viết hàm thuần để giảm dung lượng file nhị phân?
* Bạn có cần xử lý các trường hợp đặc biệt như giữ lại dấu chấm tròn của phiên bản (ví dụ: rust-1.75) không?


