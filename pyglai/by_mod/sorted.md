Nguyên lý hoạt động cốt lõi của lệnh sort() (hoặc hàm sorted()) trong Python dựa trên một thuật toán sắp xếp lai ghép xuất sắc có tên là Timsort.

Thuật toán này được phát triển bởi Tim Peters vào năm 2002 để sử dụng riêng cho Python, sau đó vì quá hiệu quả nên đã được áp dụng sang cả Java, Android và Google Chrome.

Dưới đây là cách thức vận hành chi tiết từ mã máy cho đến cơ chế so sánh chuỗi ký tự:

------------------------------

## 1. Nguyên lý thuật toán Timsort (Cách máy tính sắp xếp)

Timsort là sự kết hợp thông minh giữa hai thuật toán kinh điển: Merge Sort (Sắp xếp trộn) và Insertion Sort (Sắp xếp chèn). Nó hoạt động dựa trên việc tận dụng các dữ liệu đã được sắp xếp sẵn một phần trong thực tế.

* Bước 1: Chia nhỏ thành các "Run"
  * Máy tính quét qua danh sách và chia nó thành các đoạn nhỏ gọi là run.
  * Mỗi run là một chuỗi các phần tử đã tăng dần hoặc giảm dần sẵn.
  * Nếu đoạn đó quá ngắn, Python dùng Insertion Sort để sắp xếp nhanh đoạn đó cho đủ độ dài tiêu chuẩn (minrun, thường từ 32 đến 64 phần tử).
  
* Bước 2: Trộn các đoạn (Merge)
  
  * Sau khi có các đoạn run đã chuẩn chỉnh, Python sử dụng cơ chế của Merge Sort để trộn các đoạn này lại với nhau theo thứ tự.
   * Quá trình trộn này lặp đi lặp lại cho đến khi toàn bộ danh sách trở thành một khối duy nhất được sắp xếp hoàn chỉnh.


> Đặc tính quan trọng: Timsort là một thuật toán Stable Sort (Sắp xếp ổn định). Nghĩa là nếu hai phần tử có giá trị bằng nhau, vị trí ban đầu của chúng trước và sau khi sắp xếp sẽ không bị thay đổi.

------------------------------

## 2. Cơ chế so sánh mặc định (Lexicographical / ASCII)

Khi bạn không truyền tham số gì vào sort(), Python sẽ so sánh các phần tử theo mặc định của kiểu dữ liệu:

* Với số: So sánh giá trị toán học lớn nhỏ thông thường.
* Với chuỗi ký tự (String): So sánh từng ký tự một từ trái sang phải dựa trên số định danh của nó trong bảng mã Unicode (ASCII).
  * Ký tự nào có mã số nhỏ hơn sẽ đứng trước.
  * Ví dụ: Mã của "1" là 49, mã của "3" là 51. Vì thế chuỗi "sach2026trang10" bị xếp trước "sach2026trang3" vì tại vị trí khác biệt đầu tiên, máy tính so sánh ký tự "1" với "3" chứ không nhìn tổng thể cả số 10 và số 3.

------------------------------

## 3. Cơ chế hoạt động của tham số key (Bí quyết giải quyết Natural Sort)

Khi bạn truyền một hàm vào tham số key (ví dụ: sorted(files, key=natural_sort_key)), nguyên lý hoạt động của sort() thay đổi như sau:

   1. Tạo mảng phụ tạm thời (Decorate): Python chạy hàm key trên từng phần tử của danh sách để tạo ra một giá trị đại diện (gọi là khóa).
   2. Sắp xếp theo khóa (Sort): Thuật toán Timsort sẽ tiến hành sắp xếp danh sách dựa trên các giá trị khóa tạm thời này chứ không dùng giá trị gốc.
   3. Trả về kết quả (Undecorate): Sau khi sắp xếp xong xuôi theo thứ tự của khóa, Python trả lại danh sách chứa các phần tử gốc ban đầu.

Ví dụ trực quan về cơ chế key với hàm natural_sort_key ở câu hỏi trước:

* Đầu vào gốc: ["sach2026trang10.jpg", "sach2026trang3.jpg"]
  
* Python dịch qua hàm key thành:
  
   * "sach2026trang10.jpg" → Khóa: ['sach', 2026, 'trang', 10, '.jpg']
   * "sach2026trang3.jpg" → Khóa: ['sach', 2026, 'trang', 3, '.jpg']
  
* Quá trình so sánh: Python so sánh hai list khóa với nhau. ['sach', 2026, 'trang'] giống nhau, đến phần tử tiếp theo nó so sánh số nguyên 10 với số nguyên 3. Vì 3 < 10 nên khóa chứa số 3 đứng trước.
  
* Kết quả đầu ra: ["sach2026trang3.jpg", "sach2026trang10.jpg"]

------------------------------

Nếu bạn muốn tối ưu hiệu năng cho các danh sách cực lớn, bạn có muốn tìm hiểu sâu hơn về độ phức tạp thời gian (Time Complexity) của Timsort hay cách tự định nghĩa các quy tắc so sánh phức tạp hơn (như dùng cmp_to_key) không?

