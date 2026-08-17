typing.List trong Python là công cụ dùng để gợi ý kiểu dữ liệu (type hinting), cho biết một biến hoặc một hàm nhận/trả về một danh sách chứa các phần tử thuộc một kiểu cụ thể (như List[str] hoặc List[int]). Từ Python 3.9 trở lên, bạn nên dùng kiểu list mặc định thay vì typing.List. [1, 2, 3] 
## Chi tiết về typing.List## Mục đích sử dụng

* Giúp chỉ định rõ kiểu dữ liệu bên trong danh sách.
* Hỗ trợ công cụ lập trình (IDE) kiểm tra lỗi sớm.
* Làm cho mã nguồn dễ đọc hơn. [1, 2] 

## Cách dùng cũ (Trước Python 3.9)

* Phải import từ thư viện typing: [1, 2] 

from typing import List
# Khai báo danh sách chứa các chuỗinames: List[str] = ["An", "Binh"]

## Cách dùng mới (Từ Python 3.9 trở đi)

* Dùng trực tiếp list viết thường: [4, 5] 

# Không cần import typing.Listnames: list[str] = ["An", "Binh"]

Bạn có muốn xem ví dụ cách dùng typing.List cho hàm (function) (như kiểu dữ liệu đầu vào và đầu ra) không?

[1] [https://viblo.asia](https://viblo.asia/p/gioi-thieu-ve-type-hints-trong-python-gGJ596JrKX2)
[2] [https://campus.datacamp.com](https://campus.datacamp.com/vi/courses/intermediate-object-oriented-programming-in-python/custom-class-features-and-type-hints?ex=2)
[3] [https://www.geeksforgeeks.org](https://translate.google.com/translate?u=https://www.geeksforgeeks.org/python/type-hints-in-python/&hl=vi&sl=en&tl=vi&client=sge)
[4] [https://fastapi.tiangolo.com](https://translate.google.com/translate?u=https://fastapi.tiangolo.com/python-types/&hl=vi&sl=en&tl=vi&client=sge)
[5] [https://typing.python.org](https://translate.google.com/translate?u=https://typing.python.org/en/latest/reference/generics.html&hl=vi&sl=en&tl=vi&client=sge)
