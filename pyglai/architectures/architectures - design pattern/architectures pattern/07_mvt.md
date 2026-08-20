MVT (Model-View-Template) là một mẫu kiến trúc phần mềm được sử dụng độc quyền và làm nên tên tuổi của Django – framework phát triển web hàng đầu trong hệ sinh thái Python. [1] 

MVT thực chất là một biến thể của mô hình kiến trúc MVC kinh điển. Điểm khác biệt lớn nhất là Django đã tự đảm nhận phần việc của Controller (bộ điều khiển định tuyến URL), đồng thời đổi tên View thành Template (giao diện) và biến Controller cũ thành View (nơi xử lý logic). [2, 3, 4] 

* * *

## 🔄 So sánh trực tiếp giữa MVC và MVT

Để không bị nhầm lẫn giữa hai khái niệm này, bạn có thể tham chiếu bảng chuyển đổi vai trò dưới đây:

Thành phần MVC| Thành phần MVT trong Django| Nhiệm vụ cụ thể  
---|---|---  
Model| Model| Quản lý cấu trúc dữ liệu, bảng trong database (thông qua Django ORM).  
Controller| View| Nhận Request từ người dùng, xử lý logic, lấy dữ liệu từ Model và nạp vào Template.  
View| Template| File giao diện (HTML/CSS) chứa cú pháp Dynamic Template để hiển thị dữ liệu.  
_Cơ chế Framework_|  URL Pattern (Router)| Đóng vai trò làm Controller gốc: Ánh xạ URL người dùng gõ vào trình duyệt tới đúng hàm View cần xử lý.  
  
* * *

## 🌟 Sơ đồ hoạt động của mô hình MVT trong Django

Khi một người dùng truy cập vào một trang web Django, luồng xử lý sẽ đi qua các bước sau: [5] 
    
    
    [Người dùng] ---> (1) Gửi Request (URL) ---> [ URL Router ]
                                                        |
                                                (2) Định tuyến đến
                                                        v
    [ Template ] <--- (5) Kết hợp dữ liệu <--- [   View   ]
       (HTML)        & render thành HTML            |      ^
    
         |                                          |      |
         |                                    (3) Gọi  (4) Trả
         v                                    Dữ liệu  Dữ liệu
    [ Trình duyệt ] <--- (6) Trả về Response <------+      |
                                                           v
                                                     [  Model  ] ---> [ Database ]
    

* * *

### cau truc thu muc

Kiến trúc MVT (Model-View-Template)

Kiến trúc đặc trưng của Django. Cấu trúc thư mục dưới đây thể hiện cách Django chia một dự án lớn thành nhiều ứng dụng nhỏ (`apps`) độc lập.

📂 Cấu trúc thư mục chuẩn (Django chuẩn)

text
    
    
    my_django_project/               # Thư mục gốc của dự án
    │
    ├── manage.py                    # Công cụ dòng lệnh quản trị của Django
    │
    ├── config/                      # Thư mục cấu hình cốt lõi của toàn dự án
    │   ├── __init__.py
    │   ├── settings.py              # Cấu hình DB, bảo mật, app cài đặt
    │   ├── urls.py                  # Router gốc (Controller tối cao của hệ thống)
    │   └── wsgi.py / asgi.py        # Cấu hình cổng kết nối Server Web
    │
    └── shop_app/                    # Một ứng dụng cụ thể bên trong dự án (Ví dụ: Gian hàng)
        ├── __init__.py
        ├── admin.py                 # Cấu hình trang quản trị Admin có sẵn
        ├── apps.py
        ├── models.py                # M (Model): Định nghĩa các bảng Database
        ├── views.py                 # V (View trong MVT): Xử lý logic nghiệp vụ
        ├── urls.py                  # Router nội bộ của riêng shop_app
        │
        ├── migrations/              # Lưu lịch sử thay đổi cấu trúc Database
        │   └── 0001_initial.py
        │
        └── templates/               # T (Template): Giao diện HTML
            └── shop_app/
                ├── product_list.html
                └── product_detail.html
    

Hãy thận trọng khi sử dụng mã.

* * *

💡 Tóm tắt cách chọn cấu trúc cho dự án của bạn:

  * Nếu làm **Dự án lớn, đặt nặng việc viết Unit Test** : Hãy tạo cấu trúc thư mục theo **Clean** hoặc **Onion Architecture**.
  * Nếu ứng dụng phục vụ **Nhiều Team phát triển, cần Scale cực lớn** : Chia nhỏ dự án theo cấu trúc **Microservices**.
  * Nếu ứng dụng xử lý **Tác vụ nặng, Real-time, Chat, IoT** : Cấu trúc theo **Event-Driven**.
  * Nếu xây dựng **Web truyền thống bằng Django** : Bạn bắt buộc phải tuân theo cấu trúc **MVT**.



Bạn có muốn đi sâu vào code chi tiết của file `main.py` (Composition Root) trong **Clean Architecture** để xem các lớp kết nối với nhau như thế nào thông qua cơ chế Dependency Injection không?


* * *

## 🐍 Cách triển khai mô hình MVT thực tế trong một Project Django

Dưới đây là mã nguồn mô phỏng tính năng Hiển thị danh sách sản phẩm của một trang thương mại điện tử theo đúng chuẩn kiến trúc MVT:

## 1\. Lớp Model (`models.py`)

Định nghĩa bảng dữ liệu. Django sẽ tự động chuyển class này thành bảng SQL tương ứng.
    
    
    # correlation/models.py
    from django.db import models
    
    class Product(models.Model):
        name = models.CharField(max_length=200)
        price = models.DecimalField(max_digits=10, decimal_places=2)
        in_stock = models.BooleanField(default=True)
    
        def __str__(self):
            return self.name
    

## 2\. Lớp View (`views.py`)

Nơi tiếp nhận yêu cầu, xử lý logic nghiệp vụ và truy vấn dữ liệu từ Model. [6, 7, 8] 
    
    
    # correlation/views.py
    from django.shortcuts import render
    from .models import Product
    
    def product_list_view(request):
        # 1. Logic: Lấy toàn bộ sản phẩm còn hàng từ Database thông qua Model
        products = Product.objects.filter(in_stock=True)
        
        # 2. Đóng gói dữ liệu vào một dictionary (Context) để gửi sang giao diện
        context = {
            'products_list': products,
            'title': 'Trang danh sách sản phẩm'
        }
        
        # 3. Kết hợp dữ liệu (Context) vào file Template và render thành HTML trả về
        return render(request, 'products/list.html', context)
    

## 3\. Bộ định tuyến URL (`urls.py`)

Đóng vai trò điều phối, dẫn đường cho request tìm đến đúng View. [9, 10] 
    
    
    # correlation/urls.py
    from django.urls import path
    from .views import product_list_view
    
    urlpatterns = [
        # Khi người dùng vào đường dẫn /products/, gọi hàm product_list_view
        path('products/', product_list_view, name='product-list'),
    ]
    

## 4\. Lớp Template (`list.html`)

File HTML thuần kết hợp cú pháp riêng của Django (`{% %}` và `{{ }}`) để duyệt và hiển thị dữ liệu động.
    
    
    <!-- templates/products/list.html -->
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ title }}</title>
    </head>
    <body>
        <h1>Sản phẩm đang bán</h1>
        <ul>
            <!-- Duyệt qua danh sách sản phẩm được truyền từ View sang -->
            {% for product in products_list %}
                <li><strong>{{ product.name }}</strong> - Giá: {{ product.price }} VNĐ</li>
            {% empty %}
                <li>Hiện tại không có sản phẩm nào còn hàng.</li>
            {% endfor %}
        </ul>
    </body>
    </html>
    

* * *

## 📊 Ưu điểm và Nhược điểm của MVT

Ưu điểm 🟢| Nhược điểm 🔴  
---|---  
Phát triển cực nhanh (Rapid Development): Triết lý "Batteries Included" của Django cung cấp sẵn ORM, Admin Panel, Form Validation theo chuẩn MVT, giúp bạn tạo ứng dụng web chạy được chỉ trong vài giờ.| Ràng buộc chặt chẽ (Coupling): MVT gộp phần xử lý Backend và Frontend vào chung một mã nguồn. Nếu bạn muốn đổi giao diện sang ứng dụng Mobile, bạn gần như phải viết lại một hệ thống API mới.  
Bảo mật tuyệt vời mặc định: Django Template tự động chống lại các cuộc tấn công XSS (Cross-Site Scripting). Hệ thống MVT cũng ép buộc lập trình viên phải dùng token CSRF khi gửi dữ liệu lên Server.| Học nguyên cụm: Để làm chủ MVT, bạn bắt buộc phải học ngôn ngữ Jinja/Django Template của riêng họ, thay vì sử dụng các kỹ năng HTML/JS tiêu chuẩn.  
Quản lý Database siêu cấp: Nhờ tầng Model gắn liền với Django Migrations, việc thay đổi cấu trúc bảng dữ liệu trở nên an toàn, tự động và nhất quán.| Nặng nề (Monolithic): Kiến trúc này không phù hợp với các ứng dụng mini siêu nhẹ, xử lý thời gian thực (Real-time) hoặc các microservice phi trạng thái.  
  
* * *

## 💡 Xu hướng dịch chuyển của MVT ngày nay

Hiện nay, với sự lên ngôi của các thư viện giao diện Frontend như React, Vue, hay Angular, mô hình MVT thuần túy (khiến Server phải render toàn bộ HTML) có phần giảm bớt vị thế trong các dự án lớn. [11, 12] 

Tuy nhiên, lập trình viên Python đã biến đổi MVT rất linh hoạt bằng cách sử dụng Django REST Framework (DRF):

  * Model: Giữ nguyên.
  * View: Không trả về file HTML (`Template`) nữa, mà sử dụng lớp Serializer để biến đổi dữ liệu từ Model thành định dạng JSON thô.
  * Template: Bị loại bỏ hoàn toàn khỏi Backend Python, nhường sân chơi hiển thị giao diện lại cho Single Page Application (SPA) của Frontend. [13, 14, 15, 16] 



Để khép lại phần kiến trúc lớn và chuẩn bị chuyển sang các Design Patterns (Singleton, Factory, Decorator) hoặc các Model xử lý dữ liệu nâng cao (Pydantic, Async/Await), bạn có muốn tìm hiểu thêm về thành phần nào khác không? [17, 18, 19] 

  


[1] [https://python.plainenglish.io](https://python.plainenglish.io/the-django-framework-part-10-mvt-architecture-cfc83754b003)

[2] [https://www.linkedin.com](https://www.linkedin.com/pulse/understanding-mvt-architecture-django-aritra-pain-fpmnc)

[3] [https://python.plainenglish.io](https://python.plainenglish.io/the-django-framework-part-10-mvt-architecture-cfc83754b003)

[4] [https://medium.com](https://medium.com/@tommyraspati/exploring-the-mvt-design-pattern-in-django-with-vue-js-integration-ee8c22fc3170)

[5] [https://www.linkedin.com](https://www.linkedin.com/pulse/understanding-mvt-architecture-django-aritra-pain-fpmnc)

[6] [https://www.linkedin.com](https://www.linkedin.com/posts/aparna-s-l-507353341_understanding-mvt-architecture-in-web-activity-7311414117213384704-kq8x)

[7] [https://python.plainenglish.io](https://python.plainenglish.io/the-mvt-design-pattern-of-django-8fd47c61f582)

[8] [https://medium.com](https://medium.com/@jaychaturvedi18/a-brief-introduction-to-django-mvt-framework-8ef46cc321ab)

[9] [https://dev.to](https://dev.to/mavoochie/mvt-vs-mvc-architecture-25ma)

[10] [https://blog.stepskochi.com](https://blog.stepskochi.com/mvc-vs-django-mvt-design-patterns/)

[11] [https://python.plainenglish.io](https://python.plainenglish.io/the-django-framework-part-10-mvt-architecture-cfc83754b003)

[12] [https://medium.com](https://medium.com/@tommyraspati/exploring-the-mvt-design-pattern-in-django-with-vue-js-integration-ee8c22fc3170)

[13] [https://www.askpython.com](https://www.askpython.com/python-modules/django/django-mvt-architecture)

[14] [https://d-libro.com](https://d-libro.com/topic/djangos-mvt-framework/)

[15] [https://learn.microsoft.com](https://learn.microsoft.com/en-us/aspnet/mvc/overview/older-versions/hands-on-labs/aspnet-mvc-4-fundamentals)

[16] [https://www.geeksforgeeks.org](https://www.geeksforgeeks.org/software-engineering/difference-between-mvc-and-mvt-design-patterns/)

[17] [https://angelogentileiii.medium.com](https://angelogentileiii.medium.com/basics-of-django-model-view-template-mvt-architecture-8585aecffbf6)

[18] [https://python.plainenglish.io](https://python.plainenglish.io/the-django-framework-part-10-mvt-architecture-cfc83754b003)

[19] [https://www.codechef.com](https://www.codechef.com/learn/course/django/FVCQNC/problems/UCDMEI01G)