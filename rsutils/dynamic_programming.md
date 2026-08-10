Quy hoạch động (Dynamic Programming - DP) là một phương pháp tối ưu hóa toán học và là một kỹ thuật thiết kế thuật toán trong lập trình.
Bản chất của quy hoạch động là chia một bài toán lớn thành các bài toán con nhỏ hơn, giải các bài toán con đó một lần duy nhất, rồi lưu kết quả lại để tái sử dụng khi cần, giúp tránh việc phải tính toán lặp đi lặp lại vô ích.
------------------------------
## 1. Ý tưởng cốt lõi (Ví dụ thực tế)
Để hiểu quy hoạch động một cách đơn giản nhất, hãy tưởng tượng:

* Tôi viết lên giấy: 1 + 1 + 1 + 1 + 1 = ?
* Bạn tính nhẩm và trả lời: 5.
* Bây giờ, tôi viết thêm số + 1 vào cuối: 1 + 1 + 1 + 1 + 1 + 1 = ?
* Bạn sẽ lập tức trả lời là 6 mà không cần đếm lại từ đầu.

Vì sao? Vì bạn đã nhớ kết quả của bài toán trước đó là 5, và bạn chỉ cần thực hiện phép tính mới là 5 + 1 = 6. Đó chính là tư duy của Quy hoạch động.
------------------------------
## 2. Hai điều kiện cốt lõi để áp dụng Quy hoạch động
Không phải bài toán nào cũng giải được bằng quy hoạch động. Bài toán chỉ áp dụng được kỹ thuật này nếu thỏa mãn 2 đặc điểm sau:

* Cấu trúc con tối ưu (Optimal Substructure): Nghiệm tối ưu của bài toán lớn có thể được tìm thấy bằng cách kết hợp các nghiệm tối ưu của các bài toán con.
* Ví dụ: Để tìm đường đi ngắn nhất từ A đến C (qua B), ta chỉ cần tìm đường đi ngắn nhất từ A đến B, cộng với đường đi ngắn nhất từ B đến C.
* Các bài toán con trùng lặp (Overlapping Subproblems): Khi chia nhỏ bài toán, cùng một bài toán con sẽ xuất hiện và phải tính toán nhiều lần.
* Ví dụ: Khi tính số Fibonacci thứ 5 (F₅ = F₄ + F₃), ta cần tính F₄ = F₃ + F₂. Bạn có thể thấy bài toán con F₃ bị lặp lại ở cả hai nhánh.

----------------------------- -
## 3. Hai cách tiếp cận chính trong Quy hoạch động
Khi lập trình, có hai cách để triển khai một bài toán quy hoạch động:
## Thừa lên (Bottom-Up) – Hay còn gọi là Tabulation (Lập bảng)

* Cách làm: Giải các bài toán con nhỏ nhất trước, sau đó lưu kết quả vào một mảng hoặc một bảng, rồi từ đó tính dần lên các bài toán lớn hơn cho đến khi đạt được kết quả cuối cùng cần tìm.
* Đặc điểm: Thường dùng vòng lặp (for, while), chạy rất nhanh và không sợ bị lỗi tràn bộ nhớ đệm (stack overflow).

## Từ trên xuống (Top-Down) – Hay còn gọi là Memoization (Ghi nhớ)

* Cách làm: Bắt đầu bằng việc gọi giải bài toán lớn nhất. Thuật toán sẽ dùng hàm đệ quy để chia nhỏ bài toán xuống. Tuy nhiên, trước khi tính toán một bài toán con, nó sẽ kiểm tra xem bài toán đó đã được tính trước đây chưa. Nếu có rồi, nó lấy ngay kết quả trong bộ nhớ ra dùng.
* Đặc điểm: Dùng đệ quy kèm theo một mảng/bảng băm để lưu trữ kết quả trung gian. Code thường tự nhiên và dễ viết theo công thức toán học hơn nhưng tốn tài nguyên bộ nhớ cho các hàm đệ quy.

------------------------------
## 4. Quy hoạch động khác gì với Chia để trị (Divide and Conquer)?
Nhiều người thường nhầm lẫn hai khái niệm này vì chúng đều chia nhỏ bài toán. Điểm khác biệt lớn nhất nằm ở tính chất của các bài toán con:

| Tiêu chí | Chia để trị (Divide and Conquer) | Quy hoạch động (Dynamic Programming) |
|---|---|---|
| Tính chất bài toán con | Các bài toán con độc lập, không trùng lặp nhau. | Các bài toán con trùng lặp (xuất hiện nhiều lần). |
| Hành động | Giải độc lập từng phần rồi gộp lại. | Giải một lần, lưu lại để tái sử dụng cho lần sau. |
| Ví dụ điển hình | Thuật toán sắp xếp nhanh (Quick Sort), Tìm kiếm nhị phân. | Bài toán Cái túi, Tìm đường đi ngắn nhất, Chuỗi Fibonacci. |

------------------------------
Bạn có muốn chọn một bài toán cụ thể (như dãy Fibonacci hoặc Đường đi ngắn nhất) để tôi demo trực quan sự khác biệt về tốc độ khi không dùng và có dùng Quy hoạch động bằng code không?

