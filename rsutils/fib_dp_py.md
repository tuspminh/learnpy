Để thấy rõ sức mạnh của Quy hoạch động, hãy cùng so sánh 3 cách tính số Fibonacci thứ $n$ ($F_n$).
Đặc biệt, ta sẽ nhìn vào sự chênh lệch khủng khiếp về mặt thời gian chạy và số bước tính toán giữa việc Đệ quy thuần túy (chưa tối ưu) và Quy hoạch động.
------------------------------
## 1. Phân tích đồ thị bài toán con trùng lặp
Khi tính số Fibonacci thứ 5 ($F_5$) bằng đệ quy thuần túy, máy tính phải vẽ ra một cây thư mục tính toán như sau:
Nhìn vào cây trên, bạn sẽ thấy hàm F(3) bị tính lại 2 lần, F(2) bị tính lại 3 lần. Khi $n$ lớn lên (ví dụ $n = 50$), số lần tính trùng lặp này sẽ lên tới hàng tỷ lần, khiến máy tính bị treo (Độ phức tạp mũ $O(2^n)$).
------------------------------
## 2. Ba cách triển khai bằng Python## Cách 1: Đệ quy thuần túy (Không tối ưu - Chạy rất chậm)
Cách này máy tính liên tục tính lại các bài toán con đã biết.

def fib_recursion(n):
    if n <= 1:
        return n
    return fib_recursion(n - 1) + fib_recursion(n - 2)
# Lưu ý: Nếu truyền n = 40, máy tính sẽ mất vài giây để chạy xong!

## Cách 2: Quy hoạch động - Từ trên xuống (Memoization)
Sử dụng một mảng memo để ghi nhớ lại các số Fibonacci đã tính. Gặp lại là lấy ra dùng luôn.

def fib_top_down(n, memo={}):
    if n in memo: 
        return memo[n]  # Lấy ngay kết quả cũ nếu đã tính
    if n <= 1:
        return n
    
    memo[n] = fib_top_down(n - 1, memo) + fib_top_down(n - 2, memo)
    return memo[n]

## Cách 3: Quy hoạch động - Từ dưới lên (Tabulation - Tối ưu nhất)
Không dùng đệ quy, tính từ $F_0, F_1$ rồi dùng vòng lặp cộng dần lên. Cách này chỉ cần dùng 2 biến để tiết kiệm bộ nhớ.

def fib_bottom_up(n):
    if n <= 1:
        return n
    prev2, prev1 = 0, 1
    for _ in range(2, n + 1):
        current = prev1 + prev2
        prev2 = prev1
        prev1 = current
    return prev1
# Cách này tính số Fibonacci thứ 1000 chỉ trong một cái chớp mắt!

------------------------------
## 3. So sánh hiệu năng thực tế
Bảng dưới đây so sánh thời gian thực thi và độ phức tạp khi tính toán:

| Tiêu chí | Cách 1: Đệ quy thuần túy | Cách 2: DP (Top-Down) | Cách 3: DP (Bottom-Up) |
|---|---|---|---|
| Độ phức tạp thời gian | $O(2^n)$ (Cực kì tệ) | $O(n)$ (Tuyến tính) | $O(n)$ (Tuyến tính) |
| Độ phức tạp bộ nhớ | $O(n)$ (Do lưu bộ nhớ Stack) | $O(n)$ (Lưu mảng memo) | $O(1)$ (Chỉ tốn vài biến) |
| Thời gian tính $F_{40}$ | Khoảng 15 - 30 giây | 0.00001 giây | 0.00001 giây |
| Khả năng tính $F_{100}$ | Bất khả thi (Treo máy) | Chạy được | Chạy cực nhanh |

------------------------------
Bạn có muốn tôi thử nghiệm triển khai bài toán Fibonacci này bằng Rust để xem tốc độ tối đa của ngôn ngữ hệ thống khi áp dụng Quy hoạch động sẽ nhanh như thế nào không?

