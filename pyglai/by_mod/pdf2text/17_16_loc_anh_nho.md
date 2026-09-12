Để lọc bỏ các hình ảnh nhúng quá nhỏ (như các biểu tượng icon, đường kẻ trang trí, hoặc dấu chấm nét đứt), chúng ta sẽ dựa vào kích thước chiều rộng và chiều cao (tính bằng pixel) của hình ảnh đó trước khi lưu xuống đĩa.

Dưới đây là hàm `extract_embedded_images` được cập nhật thêm tham số `min_width` và `min_height` để lọc bỏ các file ảnh rác:

## Cập nhật mã nguồn Python

Bạn chỉ cần thay thế hàm bóc tách ảnh cũ bằng đoạn code tối ưu này:
    
    
    def extract_embedded_images(pdf_path, output_folder, min_width=50, min_height=50):
        """
        Tách riêng các tệp hình ảnh gốc từ PDF và LỌC BỎ các ảnh có kích thước nhỏ hơn cấu hình.
        :param min_width: Chiều rộng tối thiểu của ảnh (pixel) để giữ lại.
        :param min_height: Chiều cao tối thiểu của ảnh (pixel) để giữ lại.
        """
        print(f"▶️ Đang bóc tách ảnh nhúng (Kích thước tối thiểu: {min_width}x{min_height}px)...")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    
        doc = pdfium.PdfDocument(pdf_path)
        image_count = 0
        ignored_count = 0
        
        try:
            for page_idx, page in enumerate(doc):
                for obj in page.get_objects():
                    if obj.get_type() == pdfium.FPDF_PAGEOBJ_IMAGE:
                        bitmap = obj.get_bitmap()
                        try:
                            # 1. Lấy kích thước thực tế của ảnh (pixel)
                            width = bitmap.get_width()
                            height = bitmap.get_height()
                            
                            # 2. Kiểm tra điều kiện lọc kích thước
                            if width < min_width or height < min_height:
                                ignored_count += 1
                                continue # Bỏ qua ảnh này, chuyển sang ảnh tiếp theo
                            
                            image_count += 1
                            pil_img = bitmap.to_pil()
                            img_path = os.path.join(
                                output_folder, 
                                f"anh_nhung_{image_count:03d}_trang_{page_idx+1}_{width}x{height}.png"
                            )
                            pil_img.save(img_path)
                            print(f"  > Đã lưu ảnh ({width}x{height}px): {img_path}")
                        finally:
                            bitmap.close()
                page.close()
                
            print(f"✅ Hoàn thành! Đã lưu {image_count} ảnh chất lượng, bỏ qua {ignored_count} ảnh nhỏ (rác).\n")
        finally:
            doc.close()
    

## 💡 Cách sử dụng và mẹo cấu hình:

Khi gọi hàm trong block `__main__`, bạn có thể chủ động truyền kích thước bộ lọc tùy thuộc vào loại tài liệu:
    
    
    # Ví dụ: Chỉ giữ lại các ảnh lớn hơn hoặc bằng 100x100 pixel
    extract_embedded_images("input.pdf", "anh_trich_xuat", min_width=100, min_height=100)
    

  * Cấu hình 50x50 (Mặc định): Giúp loại bỏ hầu hết các icon mũi tên, dấu tích biểu mẫu, hoặc các mảnh cắt nhỏ của thanh viền trang trí.
  * Cấu hình 200x200: Thích hợp khi bạn chỉ muốn săn tìm các hình ảnh minh họa lớn như ảnh chụp chân dung, biểu đồ số liệu hoặc sơ đồ cấu trúc trong bài báo cáo.



Nếu bạn muốn nâng cấp script xử lý ảnh này lên, hãy cho tôi biết:

  * Bạn có cần lọc ảnh dựa trên dung lượng file (KB) sau khi xuất ra hay không?
  * Bạn có muốn tích hợp tính năng này vào công cụ dòng lệnh `click` để truyền tham số kích thước lọc trực tiếp từ Terminal không?