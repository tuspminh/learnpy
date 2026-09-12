Thư viện `pypdfium2` là lớp bọc (wrapper) Python cho PDFium — engine xử lý PDF mã nguồn mở do Foxit phát triển và được Google tinh chỉnh để tích hợp trực tiếp vào trình duyệt Google Chrome.

Điểm mạnh lớn nhất của `pypdfium2` là tính pháp lý thông thoáng (Giấy phép Apache-2.0 / BSD), cho phép bạn thoải mái sử dụng trong các dự án thương mại đóng nguồn mà không lo vi phạm bản quyền như `PyMuPDF` (giấy phép AGPL).

* * *

## 1\. Kiến trúc quản lý bộ nhớ của `pypdfium2`

Vì gọi trực tiếp xuống thư viện Core C/C++, `pypdfium2` yêu cầu bạn phải đóng (`.close()`) các đối tượng sau khi sử dụng để tránh hiện tượng rò rỉ bộ nhớ (RAM leak). Bạn có thể sử dụng cấu trúc `with` hoặc gọi `.close()` thủ công.

## 2\. Các tính năng cốt lõi và Code mẫu chi tiết

## A. Cắt, Gộp và Sắp xếp lại các trang PDF (Page Manipulation)

`pypdfium2` cho phép bạn tạo một file PDF trống hoàn toàn, sau đó import (chèn) các trang từ các file PDF khác nhau vào để gộp hoặc cắt file.
    
    
    import pypdfium2 as pdfium
    
    # 1. Tạo một tài liệu PDF trống mới
    output_doc = pdfium.PdfDocument.new()
    
    # 2. Mở file PDF gốc
    src_doc1 = pdfium.PdfDocument("file_1.pdf")
    src_doc2 = pdfium.PdfDocument("file_2.pdf")
    
    # 3. Chèn các trang từ file_1 (Ví dụ: Chỉ lấy trang 1 và trang 2)
    # Tham số: src_document, page_indices (list đếm từ 0), insert_at_index
    output_doc.import_pages(src_doc1, page_indices=[0, 1])
    
    # 4. Chèn toàn bộ trang của file_2 vào cuối file mới
    total_pages_2 = len(src_doc2)
    output_doc.import_pages(src_doc2, page_indices=list(range(total_pages_2)))
    
    # 5. Lưu lại thành file PDF mới
    output_doc.save("file_tong_hop.pdf")
    
    # 6. Giải phóng bộ nhớ cho toàn bộ các file đã mở
    src_doc1.close()
    src_doc2.close()
    output_doc.close()
    print("✅ Đã gộp file thành công!")
    

## B. Trích xuất hình ảnh nhúng (Extract Embedded Images)

Nếu một trang PDF có chèn các ảnh minh họa nhỏ bên trong, `pypdfium2` có thể bóc tách riêng các file ảnh gốc đó ra (chứ không phải chụp màn hình toàn bộ trang).
    
    
    import pypdfium2 as pdfium
    
    doc = pdfium.PdfDocument("tai_lieu.pdf")
    page = doc[0] # Lấy trang đầu tiên
    
    # Lấy danh sách tất cả các đối tượng đồ họa trên trang
    image_objects = []
    for obj in page.get_objects():
        # Kiểm tra nếu đối tượng là hình ảnh (FPDF_PAGEOBJ_IMAGE)
        if obj.get_type() == pdfium.FPDF_PAGEOBJ_IMAGE:
            image_objects.append(obj)
    
    print(f"Phát hiện {len(image_objects)} hình ảnh nhúng trong trang 1")
    
    for idx, img_obj in enumerate(image_objects):
        # Lấy dữ liệu ảnh dưới dạng bitmap
        bitmap = img_obj.get_bitmap()
        pil_img = bitmap.to_pil()
        
        # Lưu ảnh ra file
        pil_img.save(f"embedded_img_{idx + 1}.png")
        bitmap.close()
    
    page.close()
    doc.close()
    

## C. Lấy Tọa độ chi tiết của từng ký tự / từ khóa

Tính năng này cực kỳ hữu ích khi bạn cần làm các bài toán kiểm tra hộp chữ (Bounding Box) để khoanh vùng dữ liệu quan trọng hoặc vẽ đè nội dung lên PDF.
    
    
    import pypdfium2 as pdfium
    
    doc = pdfium.PdfDocument("hoa_don.pdf")
    page = doc[0]
    text_page = page.get_textpage()
    
    # Lấy tổng số ký tự trên trang
    count_chars = text_page.count_chars()
    
    for i in range(min(50, count_chars)): # Thử nghiệm với 50 ký tự đầu tiên
        char_text = text_page.get_text_bounded(left=i, right=i+1)
        # Lấy tọa độ 4 góc của ký tự đó: (left, bottom, right, top)
        rect = text_page.get_charbox(i)
        
        print(f"Ký tự: '{char_text}' | Toạ độ: {rect}")
    
    text_page.close()
    page.close()
    doc.close()
    

* * *

## 3\. Tối ưu cấu hình hiển thị khi Render ảnh (`page.render`)

Khi bạn sử dụng `pypdfium2` để chuyển PDF thành ảnh, hàm `render` cung cấp các tham số giúp bạn tùy biến chất lượng hiển thị:
    
    
    bitmap = page.render(
        scale = 3,                 # Độ phân giải (Hệ số nhân, scale=3 tương đương ~216 DPI)
        rotation = 0,              # Xoay ảnh (0, 90, 180, 270 độ)
        grayscale = False,         # Nếu True, ảnh xuất ra sẽ là ảnh trắng đen (xám) để giảm dung lượng
        optimize_mode = "lcd",     # Tối ưu nét chữ hiển thị ("none", "lcd", "print")
        draw_annots = True         # Hiển thị cả các hình vẽ ghi chú (annotations) chèn thêm trên PDF
    )
    

Nếu bạn đang xây dựng một ứng dụng chạy thực tế, bạn có cần tôi hướng dẫn cách kết hợp `pypdfium2` chạy đa tiến trình (multiprocessing) để tận dụng tối đa các lõi CPU khi cần chuyển đổi hàng ngàn file PDF cùng lúc không?