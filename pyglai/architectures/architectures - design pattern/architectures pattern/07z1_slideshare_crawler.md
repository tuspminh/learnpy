Để thiết kế ứng dụng cào sách SlideShare theo đúng chuẩn kiến trúc MVT (Model-View-Template), chúng ta sẽ sử dụng framework Django [MVT (Model-View-Template)]. Trong mô hình này, Django sẽ quản lý cơ sở dữ liệu qua Model, xử lý toàn bộ logic cào dữ liệu/tải ảnh bất đồng bộ/xuất PDF tại View, và hiển thị kết quả trực quan cho người dùng qua Template (giao diện HTML hiển thị danh sách sách đã cào và nút bấm kích hoạt) [MVT (Model-View-Template)].

* * *

## 📂 Cấu trúc thư mục ứng dụng theo chuẩn Django MVT
    
    
    slideshare_mvt_project/          # Thư mục gốc dự án Django
    │
    ├── manage.py                    # Trình quản lý dòng lệnh của Django
    │
    ├── config/                      # Thư mục cấu hình hệ thống
    │   ├── __init__.py
    │   ├── settings.py              # Cấu hình Database, Media file, Installed Apps
    │   └── urls.py                  # URL Router (Controller tối cao của Django)
    │
    └── crawler_app/                 # Ứng dụng cào sách độc lập
        ├── __init__.py
        ├── apps.py
        ├── admin.py
        ├── models.py                # M (Model): Định nghĩa bảng lưu thông tin Sách & Slide
        ├── views.py                 # V (View): Nơi xử lý logic Crawl, Async Download & Fitz PDF
        ├── urls.py                  # Bộ định tuyến cục bộ của app
        │
        ├── migrations/              # Lịch sử đồng bộ Database
        │   └── 0001_initial.py
        │
        └── templates/               # T (Template): Giao diện tương tác người dùng
            └── crawler_app/
                └── dashboard.html   # Trang web nhập URL SlideShare và xem danh sách PDF
    

* * *

## 💻 Mã nguồn chi tiết theo kiến trúc MVT

Để tích hợp tính năng tải ảnh bất đồng bộ (Async) vào môi trường đồng bộ (Sync) truyền thống của Django View, chúng ta sẽ sử dụng thư viện `asgiref.sync.async_to_sync` kết hợp với `aiohttp` để tối ưu hóa hiệu năng [Async/Await Model].

## 1\. Lớp Model (`crawler_app/models.py`)

Định nghĩa cấu trúc lưu trữ thông tin sách và các slide vào Database thông qua Django ORM [ORM (Object-Relational Mapping), MVT (Model-View-Template)].
    
    
    # crawler_app/models.py
    import os
    import re
    from django.db import models
    
    class Book(models.Model):
        title = models.CharField(max_length=255)
        source_url = models.URLField(max_length=500)
        created_at = models.DateTimeField(auto_now_add=True)
        pdf_file = models.CharField(max_length=500, blank=True, null=True)
    
        @property
        def safe_title(self):
            """Chuẩn hóa tiêu đề sách để đặt tên thư mục an toàn trên hệ điều hành"""
            return re.sub(r'[\\/*?:"<>| ]', '_', self.title).strip('_')
    
        def __str__(self):
            return self.title
    
    class Slide(models.Model):
        book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='slides')
        index = models.IntegerField()
        url = models.URLField(max_length=500)
        image_path = models.CharField(max_length=500)
    
        class Meta:
            ordering = ['index']
    

## 2\. Lớp View (`crawler_app/views.py`)

Đóng vai trò là bộ não xử lý [MVT (Model-View-Template)]. View tiếp nhận yêu cầu từ người dùng, thực hiện cào dữ liệu bằng `BeautifulSoup`, kích hoạt tải ảnh song song bằng `aiohttp` và đóng gói thành file PDF qua `Fitz` (PyMuPDF), cuối cùng lưu thông tin vào Model và chuyển hướng về Template [Async/Await Model, MVT (Model-View-Template)].
    
    
    # crawler_app/views.py
    import os
    import asyncio
    import aiohttp
    import requests
    import fitz  # Thư viện PyMuPDF
    from bs4 import BeautifulSoup
    from django.shortcuts import render, redirect
    from django.contrib import messages
    from asgiref.sync import async_to_sync
    from .models import Book, Slide
    
    # ----------------- HÀM PHỤ TRỢ ASYNC DOWNLOAD -----------------
    async def download_single_slide(session, url, save_path):
        """Tác vụ tải một trang slide bất đồng bộ"""
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                content = await response.read()
                with open(save_path, "wb") as f:
                    f.write(content)
                return save_path
        raise Exception(f"Không thể tải slide từ {url}")
    
    async def download_all_slides_async(slide_tasks):
        """Điều phối tải song song toàn bộ slide bằng aiohttp"""
        connector = aiohttp.TCPConnector(limit_per_host=10)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [
                download_single_slide(session, url, path) 
                for url, path in slide_tasks
            ]
            return await asyncio.gather(*tasks)
    
    
    # ----------------- DJANGO VIEW CHÍNH (MVT) -----------------
    def dashboard_view(request):
        """View hiển thị danh sách sách và xử lý form nhập URL (POST)"""
        
        if request.method == "POST":
            url = request.POST.get("slideshare_url", "").strip()
            if not url:
                messages.error(request, "Vui lòng nhập đường dẫn URL hợp lệ!")
                return redirect("dashboard")
    
            try:
                # 1. Cào thông tin cơ bản (Đồng bộ)
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(url, headers=headers)
                if res.status_code != 200:
                    raise Exception("Không thể truy cập SlideShare.")
    
                soup = BeautifulSoup(res.text, 'html.parser')
                title_tag = soup.find('h1') or soup.find('meta', {'property': 'og:title'})
                title = title_tag.text.strip() if title_tag else "Untitled_Book"
    
                # Tạo đối tượng Book trong Database qua Model ORM
                book = Book.objects.create(title=title, source_url=url)
                
                # Định nghĩa thư mục lưu trữ: output/book-name/
                output_dir = os.path.join("output", book.safe_title)
                os.makedirs(output_dir, exist_ok=True)
    
                # 2. Thu thập danh sách link ảnh slide
                slide_urls = []
                for img in soup.find_all('img'):
                    src = img.get('data-full') or img.get('data-normal') or img.get('src')
                    if src and "slide-" in src:
                        clean_url = src.split('?')
                        if clean_url not in slide_urls:
                            slide_urls.append(clean_url)
    
                if not slide_urls:
                    book.delete()
                    raise Exception("Không tìm thấy dữ liệu ảnh slide nào.")
    
                # 3. Chuẩn bị danh sách tác vụ tải ảnh bất đồng bộ
                slide_tasks = []
                slide_objects = []
                for index, img_url in enumerate(slide_urls, start=1):
                    file_name = f"slide_{index:03d}.jpg"
                    img_path = os.path.join(output_dir, file_name)
                    
                    slide_tasks.append((img_url, img_path))
                    slide_objects.append(Slide(book=book, index=index, url=img_url, image_path=img_path))
    
                # Thực thi tải ảnh bất đồng bộ trong môi trường đồng bộ của Django
                image_paths = async_to_sync(download_all_slides_async)(slide_tasks)
                
                # Lưu đồng loạt tất cả thông tin Slide xuống DB bằng bulk_create để tối ưu hiệu năng
                Slide.objects.bulk_create(slide_objects)
    
                # 4. Xuất file PDF bằng Fitz (PyMuPDF)
                pdf_path = os.path.join(output_dir, f"{book.safe_title}.pdf")
                doc = fitz.open()
                for img_path in image_paths:
                    img_doc = fitz.open(img_path)
                    pdf_bytes = img_doc.convert_to_pdf()
                    img_doc.close()
                    
                    page_doc = fitz.open("pdf", pdf_bytes)
                    doc.insert_pdf(page_doc)
                    page_doc.close()
                doc.save(pdf_path)
                doc.close()
    
                # Cập nhật đường dẫn file PDF vào bản ghi Book
                book.pdf_file = pdf_path
                book.save()
    
                messages.success(request, f"Đã cào và xuất PDF thành công sách: {title}")
                
            except Exception as e:
                messages.error(request, f"Có lỗi xảy ra: {str(e)}")
            
            return redirect("dashboard")
    
        # Mặc định (GET Request): Lấy toàn bộ sách từ Model đưa lên hiển thị ở Template
        all_books = Book.objects.all().order_by('-created_at')
        context = {
            "books": all_books,
            "title": "Hệ thống Crawl Sách SlideShare"
        }
        return render(request, "crawler_app/dashboard.html", context)
    

## 3\. Lớp Template (`crawler_app/templates/crawler_app/dashboard.html`)

Giao diện người dùng viết bằng HTML kết hợp với cú pháp của Django Template Engine (`{% %}`, `{{ }}`) để duyệt và hiển thị danh sách dữ liệu động nhận từ View [MVT (Model-View-Template)].
    
    
    <!-- crawler_app/templates/crawler_app/dashboard.html -->
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>{{ title }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f6f9; }
            .container { max-width: 800px; margin: auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h2 { color: #333; }
            .form-group { margin-bottom: 20px; }
            input[type="text"] { width: 80%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
            button { padding: 10px 20px; background-color: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #218838; }
            .alert { padding: 10px; margin-bottom: 20px; border-radius: 4px; }
            .alert-success { background-color: #d4edda; color: #155724; }
            .alert-danger { background-color: #f8d7da; color: #721c24; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; border: 1px solid #ddd; text-align: left; }
            th { background-color: #f8f9fa; }
        </style>
    </head>
    <body>
    
    <div class="container">
        <h2>📚 SlideShare Book Downloader (MVT Architecture)</h2>
        
        <!-- Hiển thị thông báo trạng thái (Flash Messages) -->
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }}">
                    {{ message }}
                </div>
            {% endfor %}
        {% endif %}
    
        <!-- Form nhập dữ liệu gửi lên cho View xử lý -->
        <form method="POST" class="form-group">
            {% csrf_token %} <!-- Token bảo mật bắt buộc của Django -->
            <input type="text" name="slideshare_url" placeholder="Dán link SlideShare tại đây..." required>
            <button type="submit">Cào Sách & Xuất PDF</button>
        </form>
    
        <h3>📋 Danh sách sách đã tải xuống</h3>
        <table>
            <thead>
                <tr>
                    <th>Tên Sách</th>
                    <th>Số Lượng Slide</th>
                    <th>Đường Dẫn Lưu PDF</th>
                </tr>
            </thead>
            <tbody>
                <!-- Duyệt qua danh sách đối tượng Book truyền từ View sang -->
                {% for book in books %}
                <tr>
                    <td><strong>{{ book.title }}</strong></td>
                    <td><span style="color: blue;">{{ book.slides.count }} trang</span></td>
                    <td><code>{{ book.pdf_file }}</code></td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="3" style="text-align: center; color: #666;">Chưa có cuốn sách nào được cào.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    </body>
    </html>
    

## 4\. Hệ thống định tuyến URL (`crawler_app/urls.py` & `config/urls.py`)

Đóng vai trò làm cổng ánh xạ URL, dẫn hướng các request từ trình duyệt tìm đến đúng hàm View tương ứng [MVT (Model-View-Template)].

_Cấu hình URL nội bộ của app (`crawler_app/urls.py`):_
    
    
    # crawler_app/urls.py
    from django.urls import path
    from .views import dashboard_view
    
    urlpatterns = [
        path('', dashboard_view, name='dashboard'),
    ]
    

_Cấu hình URL gốc của toàn bộ dự án (`config/urls.py`):_
    
    
    # config/urls.py
    from django.contrib import admin
    from django.urls import path, include
    
    urlpatterns = [
        path('admin/', admin.site.get_view_urls), # Trang quản trị Admin mặc định
        path('', include('crawler_app.urls')),      # Trỏ toàn bộ request trang chủ vào crawler_app
    ]
    

* * *

## 🎯 Phân tích tính chất MVT trong thiết kế này

  * Model cô lập hoàn toàn: Toàn bộ dữ liệu nằm gọn trong cấu trúc của cơ sở dữ liệu (SQLite/PostgreSQL) thông qua định nghĩa lớp `Book` và `Slide` [ORM (Object-Relational Mapping)].
  * View gánh vác toàn bộ logic (Fat View): View đóng vai trò làm trung gian thu nhận request POST từ trình duyệt, điều phối các thư viện cào (`BeautifulSoup`), thư viện tải mạng (`aiohttp`), thư viện xử lý file PDF (`Fitz`), sau đó lưu lại trạng thái qua Model và chuyển giao tập dữ liệu qua Template [MVT (Model-View-Template)].
  * Template phi trạng thái (Stateless Template): File `dashboard.html` chỉ có nhiệm vụ thuần túy là hiển thị cấu trúc UI và lặp dữ liệu bằng cú pháp vòng lặp `{% for book in books %}` [MVT (Model-View-Template)]. Nó không có bất kỳ quyền hạn nào can thiệp hay tính toán logic mạng/file.



Chúng ta đã trải qua toàn bộ chuỗi thiết kế từ Clean Architecture, Onion Architecture, MVC cho tới MVT cho cùng một bài toán thực tế. Bạn có muốn chuyển sang tổng hợp và phân tích các Design Patterns (Creational, Structural, Behavioral) phổ biến trong Python không?