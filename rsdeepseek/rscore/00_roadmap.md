Chào mừng bạn đến với Rust! Tôi sẽ thiết kế lộ trình **bài bản, hệ thống** cho bạn, từ cơ bản đến nâng cao.

---

## 📚 LỘ TRÌNH 8 TUẦN

### **Tuần 1-2: Nền tảng vững chắc**
1. **Cài đặt & Hello World** - `rustup`, Cargo, công cụ
2. **Biến, kiểu dữ liệu** - `let`, `mut`, kiểu nguyên/thực/bool/char
3. **Hàm & Control Flow** - `fn`, `if/else`, vòng lặp (`loop`, `while`, `for`)
4. **Ownership cốt lõi** (QUAN TRỌNG NHẤT):
   - Quy tắc sở hữu
   - Tham chiếu (`&`) và mượn (`borrowing`)
   - Vòng đời sống (`lifetimes`) cơ bản
5. **Struct & Enum** - định nghĩa, phương thức (`impl`)

### **Tuần 3-4: Quản lý bộ nhớ & dữ liệu**
6. **Vector, String, HashMap** - collection thường dùng
7. **Pattern Matching** - `match`, `if let`, `while let`
8. **Error Handling** - `Result<T,E>`, `Option<T>`, `?` operator
9. **Generic & Trait** - viết code tổng quát, `trait` như interface
10. **Closure & Iterator** - functional programming

### **Tuần 5-6: Nâng cao**
11. **Lifetime nâng cao** - elision, subtyping
12. **Smart Pointers** - `Box<T>`, `Rc<T>`, `RefCell<T>`
13. **Concurrency** - `thread`, `Mutex`, `Arc`, `channel`
14. **Async/Await** - `tokio`, `futures`
15. **Macros** - viết macro đơn giản

### **Tuần 7-8: Dự án thực tế**
16. **Xây dựng CLI app** - dùng `clap`
17. **Web API** - `axum` hoặc `actix-web`
18. **Testing & Benchmark**
19. **FFI với C** - gọi thư viện C
20. **Tối ưu hiệu suất**

---

## 🔑 NGUYÊN TẮC HỌC

**Thực hành 70% - Lý thuyết 30%**  
Sau mỗi bài, bạn **PHẢI CODE** ít nhất 5 ví dụ nhỏ.

---

## 📖 TÀI LIỆU BẮT BUỘC

- **Sách**: *"The Rust Programming Language"* (đọc miễn phí tại doc.rust-lang.org)
- **Bài tập**: **Rustlings** (github.com/rust-lang/rustlings) - quan trọng nhất!
- **Dự án mẫu**: đọc code trên docs.rs

---

## 💻 BÀI TẬP ĐẦU TIÊN

Nếu bạn đã cài Rust, hãy làm ngay:

```rust
// 1. Viết hàm tính giai thừa (dùng loop và đệ quy)
// 2. Tạo struct Rectangle {width, height}, impl phương thức area()
// 3. Dùng Option để xử lý phép chia an toàn
// 4. Đọc file và đếm số từ (dùng std::fs)
```

---

## ❌ SAI LẦM THƯỜNG GẶP

- Không hiểu ownership → học đi học lại đến khi thuộc lòng
- Sợ compiler → HÃY YÊU compiler, nó là bạn tốt nhất
- Không dùng `cargo check` thường xuyên
- Bỏ qua warning → không bao giờ bỏ qua warning

---

**Bạn đang ở trình độ nào?** (mới bắt đầu / đã biết ngôn ngữ khác / đã đọc qua Rust book)

Trả lời để tôi điều chỉnh lộ trình và giao bài tập cụ thể cho bạn! 🚀