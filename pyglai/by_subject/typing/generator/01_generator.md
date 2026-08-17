Trong Python, Generator là một công cụ đặc biệt giúp bạn tạo ra một chuỗi dữ liệu (iterable) một cách tối ưu và tiết kiệm bộ nhớ nhất.

Thay vì tạo ra toàn bộ danh sách và lưu tất cả phần tử vào bộ nhớ RAM cùng một lúc (như cách list hoạt động), Generator chỉ tạo ra từng phần tử một tại thời điểm bạn cần đến nó (theo cơ chế gọi là Lazy Evaluation - Đánh giá lười biếng).

------------------------------

## 1. Từ khóa cốt lõi: yield là gì?

Để tạo ra một Generator, bạn viết một hàm bình thường nhưng thay vì dùng từ khóa return, bạn dùng từ khóa yield.

* return: Trả về một giá trị duy nhất và kết thúc hoàn toàn hàm đó (giải phóng mọi biến cục bộ).
* yield: Trả về một giá trị cho người gọi, nhưng tạm dừng hàm lại và ghi nhớ trạng thái hiện tại. Khi bạn yêu cầu phần tử tiếp theo, hàm sẽ chạy tiếp ngay từ vị trí nó vừa tạm dừng.

## Ví dụ so sánh trực quan:

```
# ❌ Cách thông thường dùng LIST (Tốn RAM)
def tao_danh_sach_list(n: int) -> list[int]:
    ket_qua = []
    for i in range(n):
        ket_qua.append(i) # Lưu toàn bộ vào RAM
    return ket_qua


#  Cách tối ưu dùng GENERATOR (Siêu tiết kiệm RAM)
from collections.abc import Generator

def tao_generator(n: int) -> Generator[int, None, None]:
    for i in range(n):
        yield i # Trả về từng số một rồi tạm dừng, không tốn RAM lưu trữ cả mảng
```

(Lưu ý về Type Hinting: Từ Python 3.9+, bạn nên import Generator từ thư viện collections.abc thay vì từ typing).

------------------------------

## 2. Cách lấy dữ liệu từ Generator

Vì Generator không lưu dữ liệu sẵn, bạn có thể lấy dữ liệu ra bằng 2 cách sau:

### Cách 1: Dùng vòng lặp for (Phổ biến nhất)

Vòng lặp for sẽ tự động kích hoạt Generator chạy từ đầu đến cuối cho đến khi hết dữ liệu.
```
g = tao_generator(3)
for so in g:
    print(so)

# Kết quả:
# 0
# 1
# 2
```

### Cách 2: Dùng hàm next() để lấy từng phần tử thủ công

Mỗi lần gọi next(), hàm sẽ chạy tiếp cho đến khi gặp từ khóa yield tiếp theo. Nếu hết dữ liệu, nó sẽ báo lỗi StopIteration.

```
g = tao_generator(3)

print(next(g)) # Kết quả: 0 (Hàm tạm dừng ở đây)
print(next(g)) # Kết quả: 1 (Hàm chạy tiếp từ 0 và dừng ở 1)
print(next(g)) # Kết quả: 2
# print(next(g)) # ❌ Lỗi StopIteration nếu gọi thêm lần nữa vì hết dữ liệu!
```

------------------------------

## 3. Sức mạnh thực sự của Generator: Tiết kiệm bộ nhớ (RAM)

Hãy tưởng tượng bạn cần xử lý một danh sách gồm 10 triệu số nguyên.

```
import sys
# Tạo bằng List Comprehension
list_lon = [x for x in range(10000000)]
print(f"Kích thước của List trong RAM: {sys.getsizeof(list_lon)} bytes")
# Kết quả: Khoảng ~80.000.000 bytes (gần 80MB RAM)

# Tạo bằng Generator Expression (Thay ngoặc vuông [] bằng ngoặc tròn ())
gen_lon = (x for x in range(10000000))
print(f"Kích thước của Generator trong RAM: {sys.getsizeof(gen_lon)} bytes")
# Kết quả: Chỉ 112 bytes! 
```

👉 Giải thích: Dù danh sách có tăng lên 1 tỷ phần tử, Generator vẫn chỉ tốn 112 bytes RAM vì nó không chứa bất kỳ con số nào cả, nó chỉ chứa "công thức" để tạo ra con số tiếp theo khi bạn gọi nó.

------------------------------

## 4. Khi nào bạn NÊN và KHÔNG NÊN dùng Generator?

### Nên dùng khi:

* Xử lý dữ liệu lớn (Big Data): Đọc file text dung lượng hàng chục GB, đọc dữ liệu từ Database khổng lồ theo từng dòng.
* Chuỗi dữ liệu vô hạn: Ví dụ chuỗi số Fibonacci vô hạn, luồng nhận dữ liệu liên tục từ cảm biến IoT.
* Bạn chỉ cần duyệt qua dữ liệu đúng 1 lần từ đầu đến cuối.

### ❌ Không nên dùng khi:

* Bạn cần truy cập ngẫu nhiên (Index ngẫu nhiên như data[5]). Generator không hỗ trợ index, muốn lấy phần tử thứ 5 bạn phải chạy qua 4 phần tử đầu tiên.
* Bạn cần sử dụng lại dữ liệu nhiều lần. Generator sau khi chạy qua một phần tử là phần tử đó sẽ "biến mất", bạn không thể quay lại phần tử trước đó và nếu muốn chạy lại vòng lặp for lần 2, bạn phải tạo lại Generator mới từ đầu.

------------------------------

Bạn có muốn xem một ví dụ thực tế về cách ứng dụng Generator để đọc một file log khổng lồ (dung lượng vài GB) mà không làm sập RAM của máy tính không?

