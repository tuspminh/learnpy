Để thay đổi biến ở phạm vi enclosing, bạn cần sử dụng từ khóa nonlocal. Nếu không có từ khóa này, Python sẽ tự hiểu đó là một biến cục bộ (local) mới hoàn toàn và không thay đổi gì được biến của hàm cha.
Dưới đây là chi tiết về cách dùng và cách nó tạo ra khái niệm Closure.
------------------------------
## 1. Cách dùng từ khóa nonlocal
Nếu không dùng nonlocal, code sẽ tạo biến mới hoặc báo lỗi. Hãy xem ví dụ dưới đây khi có nonlocal:

def tang_so():
    dem = 0  # Biến thuộc phạm vi Enclosing
    
    def dem_so():
        nonlocal dem  # Khai báo liên kết với biến của hàm cha
        dem += 1      # Bây giờ có thể thay đổi giá trị của nó
        print(f"Số hiện tại: {dem}")
        
    return dem_so
bo_dem = tang_so()
bo_dem()  # Kết quả: Số hiện tại: 1
bo_dem()  # Kết quả: Số hiện tại: 2

------------------------------
## 2. Khái niệm Closure (Hàm đóng)
Closure xuất hiện trực tiếp từ phạm vi enclosing. Đó là một hàm con ghi nhớ và giữ quyền truy cập vào các biến thuộc phạm vi enclosing của hàm cha, ngay cả khi hàm cha đã thực thi xong và thoát ra ngoài.
## Đặc điểm của một Closure:

* Có hàm lồng nhau (inner function).
* Hàm con tham chiếu đến biến của hàm cha (enclosing scope).
* Hàm cha trả về chính hàm con đó (return inner).

## Tại sao Closure lại hữu ích?

* Giúp bảo mật dữ liệu (data hiding) không cho code bên ngoài sửa đổi trực tiếp.
* Thay thế cho các class đơn giản chỉ có một phương thức để tối ưu bộ nhớ.

------------------------------
Nếu bạn muốn tiếp tục, tôi có thể:

* Viết một ví dụ ứng dụng closure để bảo mật mật khẩu hoặc tạo bộ lọc dữ liệu.
* Giải thích toàn bộ quy tắc LEGB để bạn nắm rõ bức tranh tổng thể về biến trong Python.

Bạn muốn đi sâu vào ví dụ thực tế của Closure hay học về quy tắc LEGB?

