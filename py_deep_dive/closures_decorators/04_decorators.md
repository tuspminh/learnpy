*Ở bài viết này, tôi sẽ giới thiệu một kỹ thuật gọi là* ***decorator****. Nhìn chung, nếu ai đã từng làm việc với các python web framework như Django, Flask, FastAPI,… thì sẽ sử dụng kỹ thuật này thường xuyên, nhưng không phải ai cũng hiểu rõ bản chất của nó.*

*Thừa nhận rằng, khi sử dụng các* ***decorators*** *có sẵn mà các framework cung cấp, đã đủ để chúng ta làm việc như một web developer. Tuy nhiên, việc nắm được bản chất của kỹ thuật này cũng giúp cho chúng ta sử dụng* ***decorators*** *hiệu quả hơn, có thể tùy chỉnh và tạo ra các* ***decorators*** *của riêng mình, như vậy là ta đã trở thành một lập trình viên chuyên nghiệp hơn.*

## Decorators

Nhắc lại một ví dụ trong Phần 3, chúng ta đã áp dụng *Closure* để maintain một bộ đếm — đếm số lần gọi một hàm bất kỳ.

```
def counter(fn):  
    cnt = 0 # số lần chạy fn, khởi tạo là 0
    def inner(*args, **kwargs):  
        nonlocal cnt  
        cnt = cnt + 1  
        print('Hàm {0} đã được gọi {1} lần'.format(fn.__name__, cnt))  
        return fn(*args, **kwargs)  

    return inner
```

Hàm **counter** nhận một function làm đầu vào — **fn**. Trong hàm **counter**, ta khởi tạo 1 biến cục bộ **cnt** — biến này sẽ đến số lần gọi hàm **fn**, mỗi khi goị đến hàm **inner** thì biến **cnt** được tăng lên 1 đơn vị.

Việc sử dụng **args* và ***kwargs* trong hàm **inner** giúp ta có thể gọi hàm **fn** với bất kỳ sự kết hợp *positional arguments* và *keyword-only arguments* nào. Lấy ví dụ:

```
def mult(x, y=10):  
    """  
    return the products of two values  
    """  
    return x * y  

mult = counter(mult) # trả về inner function - closure
```

Nhớ rằng, ban đầu **mult** là một label trỏ đến hàm **mult** được định nghĩa ở trên. Goị hàm **counter(mult)** sẽ trả về một *closure* và gán vào một label là **mult**, thì lúc này **mult** sẽ trỏ đến *closure* đó, rõ ràng là khác so với nơi mà **mult** ban đầu trỏ đến.

Tuy nhiên, **inner** thực hiện gọi hàm **mult** ban đầu cho chúng ta và trả về kết quả của nó, chính vì vậy mà kết quả trả về khi gọi hàm **inner** không khác so với việc gọi hàm **mult** ban đầu. Nhưng thực sự, hàm **inner** đã làm thêm một số việc trước khi gọi và trả về kết quả của hàm **mult**, đó là đếm số lần hàm **mult** được gọi.

```
mult(3, 5)  
# In ra: Hàm mult đã được gọi 1 lần
# return 15
```

Chúng ta đã thực sự sửa đổi hàm **mult** ban đầu, bằng cách wrapping nó bên trong một hàm khác — bổ sung thêm chức năng cho nó –> chúng ta đã decorated hàm **mult** với hàm **counter** và chúng ta gọi **counter** là **decorator function**.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:875/1*VFUvLaCMf4A8KZ0Mir4Bwg.jpeg)

Nhìn chung, một decorator function sẽ:

- lấy 1 function như một đối số
- return một *closure*
- *closure* nói trên sẽ nhận bất kỳ sự kết hợp đầu vào nào (sử dụng *args và **kwargs)
- chạy một vài chức năng bên trong *closure*
- **closure function** sẽ gọi **original function** sử dụng các đối số được truyền vào *closure*
- return kết quả được trả về từ function call nói trên

## The @ Symbol

Như đã thấy, chúng ta hoàn toàn có thể sử dụng **decorator** function như sau:

```
def my_func(*args, **kwargs):  
    # some code here  
    # ...  
my_func = func(my_func)
```

Trong đó, **func** là **decorator function**, còn **my_func** là hàm được decorated.

Tuy nhiên, có một cách khác thanh lịch hơn:

```
@func  
def my_func(*args, **kwargs):  
    # some code here  
    # ...
```

## Introspection

Sử dụng lại counter như một **decorator** cho hàm mult:

```
import inspect  

@counter  
def mult(x, y=10):  
    """  
    return the products of two values  
    """  
    return x * y  

print(f'name = {mult.__name__}') # name = inner
```

Ta thấy rằng, câu lệnh print ở trên sẽ in ra màn hình **name = inner**. Rõ ràng, tên của hàm **mult** không phải là **mult** nữa, mà nó là **inner** — tên của một *closure*, điều này chứng tỏ một điều rằng, hàm mult lúc này chính là một **closure**.

Vì vậy, cầu lưu ý rằng, khi chúng ta decorate một function, tức là chúng ta đã làm cho function đó thay đổi (về bản chất).

Để chắc chắn hơn, hãy thử gọi:

```
print(f'signature: {inspect.signature(mult)}') # signature: (*args, **kwargs)
```

Như vậy, khi gọi **inspect.signature(mult)**, chúng ta đã nhìn thấy rõ chữ ký của hàm **inner** được trả về.

Việc decorate một function làm thay đổi *docstring, signature, name* khiến cho việc debugging trở nên khó khăn hơn rất nhiều.

## The wraps function

Để giải quyết vấn đề mới nói ở trên, functools module cung cấp một wraps function có thể fix metadata của inner function trong **decorator**. Bản thân wraps function này là một **decorator**.

Hàm wraps này sẽ decorate **inner** function để thay đổi metadata (docstring, signature, name,…) của nó. Thêm nữa, nó phải sử dụng hàm **mult** như một đối số đầu vào, để có thể thay thế metadata của **inner** function bằng metadata của **mult** function (hàm được decorated)

```
from functools import wraps  
import inspect  

def counter(fn):  
    cnt = 0  # số lần chạy fn, khởi tạo là 0  

    @wraps(fn)  
    def inner(*args, **kwargs):  
        nonlocal cnt  
        cnt = cnt + 1  
        print('Hàm {0} đã được gọi {1} lần'.format(fn.__name__, cnt))  
        return fn(*args, **kwargs)  
    return inner  

@counter  
def mult(x, y=10):  
    """  
    return the products of two values  
    """  
    return x * y  

print(f'name = {mult.__name__}') # name = mult  
print(f'signature: {inspect.signature(mult)}') # signature: (x, y=10)
```

Chúng ta không nhất thiết phải sử dụng wraps function trong khi sử dụng **decorator**, nhưng việc sử dụng nó sẽ giúp cho việc debugging trở nên dễ dàng hơn.

## Summary

1. Decorators trong Python là cú pháp cho phép một function sửa đổi một function khác tại thời gian chạy (runtime)
2. Ký pháp @ giúp cho việc sử dụng **decorator** thanh lịch hơn (mặc dù có thể không cần)
3. Hãy sử dụng wraps function giúp cho việc debugging dễ dàng hơn khi làm việc với **decorators**.

## References

[1] Fred Baptiste, *Python Deep Dive, Part 1*

[2] Brett Slatkin, *Effective Python, Item 26*
