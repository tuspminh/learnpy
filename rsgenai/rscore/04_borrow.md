Chào bạn! Hãy hít một hơi thật sâu, vì chúng ta đang bước vào phần **quan trọng nhất** và cũng là "trái tim" của Rust: **Ownership**. Hiểu được phần này, bạn đã vượt qua được 80% khó khăn khi học Rust.

Hầu hết các ngôn ngữ quản lý bộ nhớ theo hai cách:

1. **C/C++:** Lập trình viên tự cấp phát và giải phóng bộ nhớ thủ công (rất linh hoạt nhưng dễ gây lỗi rò rỉ bộ nhớ hoặc sập chương trình).
2. **Java/Python/C#:** Có bộ thu gom rác (Garbage Collector - GC) chạy ngầm tự động dọn dẹp (an toàn nhưng làm chậm chương trình).

Rust chọn con đường thứ 3: **Ownership**. Bộ nhớ được quản lý thông qua một hệ thống các quy tắc chặt chẽ do trình biên dịch kiểm tra tại thời điểm biên dịch (compile time). Nếu bạn vi phạm, code sẽ từ chối biên dịch. Do đó, chương trình Rust chạy nhanh như C++ nhưng lại an toàn như Java.

{/* Reason: Giải thích cơ bản về nơi dữ liệu được lưu trữ để làm tiền đề cho khái niệm Ownership. */}

---

## 1. Ba quy tắc vàng của Ownership

Bạn hãy ghi nhớ nằm lòng 3 quy tắc này, chúng là kim chỉ nam cho mọi dòng code Rust bạn sẽ viết:

1. Mỗi giá trị trong Rust đều có một biến gọi là **owner** (chủ sở hữu) của nó.
2. Tại một thời điểm, chỉ có **duy nhất một owner**.
3. Khi owner ra khỏi phạm vi hoạt động (out of scope), giá trị đó sẽ bị **xóa bỏ (dropped)**.

```rust
{
    // Biến s chưa hợp lệ ở đây vì nó chưa được khai báo
    let s = String::from("hello"); // s bắt đầu hợp lệ từ đây
    // Thực hiện các thao tác với s...
} 
// Dấu ngoặc nhọn kết thúc (end of scope), biến s ra khỏi phạm vi. 
// Rust tự động giải phóng bộ nhớ của s ngay lập tức.

```

## 2. Sự di chuyển (Move) - Cú sốc đầu tiên

Với các kiểu dữ liệu đơn giản, có kích thước cố định nằm trên Stack (như số nguyên `i32`, `bool`), khi bạn gán biến này cho biến khác, Rust sẽ tự động **copy** giá trị. Nhưng với kiểu dữ liệu phức tạp nằm trên Heap (như `String`), chuyện gì sẽ xảy ra?

```rust
let s1 = String::from("hello");
let s2 = s1;

// println!("{}, world!", s1); // NẾU CHẠY DÒNG NÀY, RUST SẼ BÁO LỖI BIÊN DỊCH!

```

**Tại sao lại lỗi?**
Vì Rust tuân thủ quy tắc số 2: "Chỉ có duy nhất một owner". Khi bạn gán `let s2 = s1`, quyền sở hữu đoạn text "hello" đã được chuyển từ `s1` sang `s2`. Thao tác này gọi là **Move** (di chuyển).

Biến `s1` ngay lập tức bị trình biên dịch "phế võ công" và trở thành một biến không hợp lệ. Điều này giúp Rust tránh được lỗi "double free" (giải phóng bộ nhớ 2 lần ở cùng một chỗ) cực kỳ nguy hiểm và phổ biến trong C/C++.

{/* Reason: Hình ảnh so sánh cực kỳ trực quan về sự khác biệt khi dữ liệu bị Move (mất luôn) và khi được Borrow (được trả lại sau khi mượn). */}

---

## 3. Borrowing (Mượn) và References (Tham chiếu)

Việc truyền một biến vào hàm cũng tuân theo quy tắc Move. Nếu mỗi lần truyền biến vào hàm mà bị mất luôn quyền sở hữu thì thật tồi tệ. Để giải quyết, Rust cung cấp cơ chế **Borrowing (Mượn)** bằng cách sử dụng các tham chiếu (References), ký hiệu là dấu `&`.

Cho mượn nghĩa là: "Tôi cấp cho anh cái quyền xem hoặc dùng tạm dữ liệu của tôi, nhưng quyền sở hữu vẫn là của tôi, dùng xong anh phải trả".

```rust
fn main() {
    let s1 = String::from("hello");
    let do_dai = tinh_do_dai(&s1); // Truyền tham chiếu của s1 (cho mượn)

    // s1 vẫn còn tồn tại và hợp lệ ở đây vì nó chỉ "cho mượn" chứ chưa bị Move
    println!("Độ dài của '{}' là {}.", s1, do_dai); 
}

// Hàm nhận vào một tham chiếu đến String (&String) thay vì lấy luôn String
fn tinh_do_dai(s: &String) -> usize {
    s.len()
} // Khi hàm kết thúc, s (tham chiếu) bị hủy. Vì nó không phải là owner gốc, nên bộ nhớ chứa chữ "hello" trên Heap không bị xóa.

```

## 4. Tham chiếu có thể thay đổi (Mutable References)

Mặc định, bạn không thể thay đổi một giá trị khi đi mượn (đã mượn đồ thì không được tự ý sơn lại màu khác). Nếu muốn sửa giá trị gốc thông qua việc mượn, bạn phải mượn bằng `&mut`.

```rust
fn main() {
    let mut s = String::from("hello");
    them_chu(&mut s); // Phải truyền bằng &mut
    println!("{}", s); // Sẽ in ra: hello world
}

// Tham số của hàm cũng phải là &mut
fn them_chu(s: &mut String) {
    s.push_str(" world");
}

```

### Quy tắc tối thượng của Borrowing (Cực kỳ quan trọng)

Để ngăn chặn lỗi **data race** (xung đột bộ nhớ khi nhiều luồng cùng truy cập và sửa dữ liệu cùng lúc), Rust đặt ra một ranh giới thép. Trong cùng một phạm vi, bạn chỉ được phép có:

* **Hoặc** là nhiều tham chiếu bất biến (`&T`) (Nhiều người có thể cùng đọc).
* **Hoặc** là duy nhất MỘT tham chiếu có thể thay đổi (`&mut T`) (Chỉ một người được phép sửa, và trong lúc đó cấm ai được đọc).
* **KHÔNG ĐƯỢC PHÉP** có cả hai cùng lúc!

```rust
let mut s = String::from("hello");

let r1 = &s; // Ổn định (người đọc 1)
let r2 = &s; // Ổn định (người đọc 2)
// let r3 = &mut s; // LỖI BIÊN DỊCH! Đang có người đọc, không ai được phép sửa!

```

Khái niệm này ban đầu sẽ khiến bạn rất "khó chịu" vì trình biên dịch liên tục báo lỗi, nhưng một khi đã quen, bạn sẽ thấy code của mình an toàn tuyệt đối.