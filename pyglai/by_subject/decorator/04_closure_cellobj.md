Để hiểu cách Python lưu biến Closure trong bộ nhớ, chúng ta cần nhìn vào "hậu trường" của ngôn ngữ.
Thông thường, khi một hàm kết thúc, toàn bộ biến cục bộ của nó sẽ bị xóa khỏi bộ nhớ (Stack). Nhưng với Closure, Python sử dụng một cơ chế đặc biệt gọi là Cell Object để giữ các biến này tồn tại trong bộ nhớ vùng Heap.
Dưới đây là chi tiết cách Python lưu trữ và cách bạn có thể "soi" chúng.
------------------------------
## 1. Cơ chế Cell Object (Vật thể ô cờ)
Khi Python biên dịch code và phát hiện một hàm con tham chiếu đến biến của hàm cha (Enclosing), nó sẽ không lưu biến đó như một biến local thông thường.

   1. Python tạo ra một Cell Object ở vùng nhớ Heap để bọc giá trị của biến đó lại.
   2. Cả hàm cha và hàm con sẽ cùng trỏ chung vào Cell Object này.
   3. Khi hàm cha chạy xong và biến mất, Cell Object vẫn sống vì hàm con vẫn đang trỏ vào nó.

------------------------------
## 2. Cách kiểm tra các biến Closure trong bộ nhớ
Python cung cấp hai thuộc tính ẩn (dunder attributes) là __closure__ và co_freevars để bạn kiểm tra xem hàm đang giữ những biến nào từ phạm vi Enclosing.
Hãy chạy thử đoạn code dưới đây:
```
def ham_cha():
    ten = "Python"  # Biến thuộc Enclosing scope
    tuoi = 35
    
    def ham_con():
        print(f"Học {ten} ở tuổi {tuoi}")
        
    return ham_con
# Tạo một closuremy_closure = ham_cha()
# 1. Kiểm tra danh sách tên các biến đang được giữ lại
print(my_closure.__code__.co_freevars)  # Kết quả: ('ten', 'tuoi')
# 2. Kiểm tra các Cell Object trong bộ nhớ
print(my_closure.__closure__)  # Kết quả: (<cell at 0x...: str object at 0x...>, <cell at 0x...: int object at 0x...>)
# 3. Xem giá trị thực sự bên trong từng Cell
print(my_closure.__closure__[0].cell_contents)  # Kết quả: Python
print(my_closure.__closure__[1].cell_contents)  # Kết quả: 35
```
## Tóm lại

* Biến Enclosing trong closure không bị giải phóng mà được chuyển vào một Cell Object.
* Hàm con mang theo thuộc tính __closure__ chứa các Cell Object này đi khắp nơi trong chương trình.

------------------------------
Nếu bạn đã nắm chắc phần này, chúng ta có thể bước sang phần ứng dụng thực tế cao nhất của Closure:

* Tìm hiểu về Decorator (Cơ chế dùng closure để chỉnh sửa/nâng cấp tính năng của một hàm khác mà không cần sửa code của hàm đó).

Bạn đã sẵn sàng chuyển sang học Decorator chưa?

