MRO (Method Resolution Order) là thứ tự giải quyết phương thức. Đây là quy tắc mà Python sử dụng để quyết định xem sẽ gọi hàm (hoặc thuộc tính) từ class cha nào khi bạn sử dụng Đa kế thừa (Multiple Inheritance).
------------------------------
## 1. Bản chất và Thuật toán C3 Linearization
Khi một class kế thừa từ nhiều class cha có cùng một hàm, Python không tìm kiếm ngẫu nhiên. Nó sử dụng một thuật toán gọi là C3 Linearization để tạo ra một danh sách thứ tự tìm kiếm phẳng (từ trái qua phải, từ dưới lên trên).
Quy tắc tìm kiếm cốt lõi của MRO:

   1. Class con luôn được tìm kiếm trước class cha (Subclass trước Superclass).
   2. Nếu kế thừa từ nhiều class, thứ tự khai báo từ trái sang phải trong cặp ngoặc () sẽ quyết định độ ưu tiên.
   3. Python đảm bảo không bao giờ duyệt qua class gốc object trước khi duyệt hết tất cả các class cha khác.

------------------------------
## 2. Vấn đề "Kim Cương" (The Diamond Problem)
Đa kế thừa rất dễ dẫn đến cấu trúc hình kim cương, nơi hai class cha cùng kế thừa từ một class gốc, và class con lại kế thừa từ cả hai class cha đó.
## Sơ đồ cấu trúc:

    A
   / \
  B   C
   \ /
    D

## Code minh họa:

class A:
    def chao(self):
        print("Chào từ A")
class B(A):
    def chao(self):
        print("Chào từ B")
class C(A):
    def chao(self):
        print("Chào từ C")
class D(B, C):
    pass
obj = D()
obj.chao()  # Kết quả sẽ gọi từ đâu: B hay C?

## Kết quả chạy thực tế:
Chương trình sẽ in ra: Chào từ B
## Cách kiểm tra MRO của một Class:
Bạn có thể xem trực tiếp danh sách thứ tự tìm kiếm của Python bằng cách truy cập thuộc tính __mro__ hoặc gọi hàm .mro() trên Class:

print(D.mro())# Kết quả: [<class '__main__.D'>, <class '__main__.B'>, <class '__main__.C'>, <class '__main__.A'>, <class 'object'>]

Thứ tự tìm kiếm của Python đối với class D sẽ là: D -> B -> C -> A -> object. Do B nằm trước C trong danh sách khai báo class D(B, C), nên hàm của B được ưu tiên chọn trước.
------------------------------
## 3. Sức mạnh của super() kết hợp với MRO
Rất nhiều lập trình viên nghĩ rằng super() luôn gọi hàm của class cha trực tiếp. Điều này chưa chính xác trong đa kế thừa.
Trong Python, super() có nghĩa là: "Hãy tìm class tiếp theo nằm ngay sau class hiện tại trong danh sách MRO".
## Ví dụ minh họa cơ chế chạy chuỗi (Chaining):

class X:
    def test(self):
        print("Chạy X")
class Y(X):
    def test(self):
        print("Chạy Y")
        super().test()  # Gọi class tiếp theo trong MRO
class Z(X):
    def test(self):
        print("Chạy Z")
        super().test()  # Gọi class tiếp theo trong MRO
class Con(Y, Z):
    def test(self):
        print("Chạy Con")
        super().test()
# Kiểm tra MRO của class Con
print([c.__name__ for c in Con.mro()])# Kết quả MRO: ['Con', 'Y', 'Z', 'X', 'object']
c = Con()
c.test()

## Kết quả in ra bất ngờ:

Chạy Con
Chạy Y
Chạy Z
Chạy X

Giải thích: Khi Y.test() gọi super().test(), Python nhìn vào danh sách MRO của đối tượng đang chạy (Con). Phía sau Y chính là Z. Vì vậy, super() trong Y đã gọi sang một class "anh em" với nó là Z chứ không phải gọi lên class cha X.
------------------------------
## 4. Lỗi vi phạm MRO (TypeError: Cannot create a consistent MRO)
Python sẽ ngăn chặn ngay từ bước biên dịch nếu bạn cố tình khai báo một cấu trúc đa kế thừa không đồng nhất, vi phạm quy tắc thuật toán C3.

class X: passclass Y(X): passclass Z(X, Y): pass # Lỗi!
# Python ném ra lỗi: TypeError: Cannot create a consistent method resolution order (MRO)

Lý do lỗi: Class Z khai báo muốn tìm ở X trước rồi mới đến Y. Nhưng bản thân Y lại là con của X (luật quy định con phải tìm trước cha). Mâu thuẫn này khiến Python từ chối tạo class.
Nếu bạn muốn, tôi có thể:

* Giải thích chi tiết cơ chế quản lý bộ nhớ của Python bao gồm Reference Counting (Đếm tham chiếu) và Garbage Collection (Bộ thu gom rác).
* Hoặc chuyển sang tìm hiểu về các tính năng bất đồng bộ nâng cao với asyncio (Coroutine & Event Loop).

Bạn muốn tìm hiểu về Quản lý bộ nhớ hay lập trình bất đồng bộ asyncio?

