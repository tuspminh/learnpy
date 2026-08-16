Trong Python, enclosing (hoặc enclosing scope) là phạm vi bao quanh, chỉ không gian của hàm bên ngoài khi bạn có một hàm được đặt lồng bên trong một hàm khác. Đây là một phần trong quy tắc tìm kiếm biến LEGB (Local -> Enclosing -> Global -> Built-in) của Python. [1, 2, 3, 4] 
## Đặc điểm của Enclosing Scope

* Hàm lồng nhau: Xuất hiện khi một hàm con (inner function) nằm bên trong một hàm cha (outer function).
* Truy cập biến: Hàm con có thể đọc và sử dụng các biến nằm ở phạm vi của hàm cha (enclosing).
* Không thể sửa đổi trực tiếp: Mặc định hàm con chỉ đọc được biến enclosing. Nếu muốn thay đổi giá trị của biến đó, bạn phải dùng từ khóa nonlocal. [2] 

## Ví dụ về Enclosing

def ham_ngoai():
    x = "Biến ở hàm ngoài (Enclosing)"
    
    def ham_trong():
        print(x) # Truy cập được biến x từ phạm vi enclosing
        
    ham_trong()

ham_ngoai()

Nếu bạn muốn, tôi có thể giải thích chi tiết hơn về:

* Cách dùng từ khóa nonlocal để thay đổi biến enclosing.
* Sự khác biệt giữa Enclosing scope và Closure.

Hãy cho tôi biết bạn muốn tìm hiểu phần nào tiếp theo!

[1] [https://realpython.com](https://translate.google.com/translate?u=https://realpython.com/python-scope-legb-rule/&hl=vi&sl=en&tl=vi&client=sge)
[2] [https://www.laptrinhdientu.com](https://www.laptrinhdientu.com/2025/10/python-inner-function-closure.html)
[3] [https://viblo.asia](https://viblo.asia/p/scope-legb-closure-vi-sao-ham-nho-sai-gia-tri-37LdeGrMVov)
[4] [https://pythongis.org](https://translate.google.com/translate?u=https://pythongis.org/back-matter/nb/glossary.html&hl=vi&sl=en&tl=vi&client=sge)
