Dưới đây là đoạn code Python hoàn chỉnh sử dụng `pypdfium2` (chuẩn API mới nhất) để thực hiện trọn gói 4 yêu cầu của bạn: Chuyển ảnh thành PDF, Chuyển PDF thành ảnh, Bóc tách Text, và Bóc tách Hình ảnh nhúng.

Vì `pypdfium2` yêu cầu quản lý bộ nhớ thủ công để tránh tràn RAM (leak), toàn bộ các hàm dưới đây đều đã được tối ưu hóa bằng cấu trúc `try...finally` để tự động giải phóng bộ nhớ (`.close()`) an toàn.

## 🛠️ Cài đặt thư viện

Bạn chỉ cần cài đặt `pypdfium2` và thư viện xử lý ảnh `Pillow`:
    
    
    pip install pypdfium2 pillow
    

* * *

## 💻 Code Python Toàn Diện Xử Lý PDF
    
    
    import os
    import pypdfium2 as pdfium
    from PIL import Image
    
    # ==============================================================================
    # 1. CHUYỂN ẢNH THÀNH PDF (Images to PDF)
    # ==============================================================================
    def images_to_pdf(image_paths, output_pdf_path):
        """
        Gom một hoặc nhiều file ảnh (.png, .jpg) thành một file PDF duy nhất.
        """
        print("▶️ Đang chuyển đổi ảnh thành PDF...")
        if not image_paths:
            print("❌ Danh sách ảnh trống.")
            return
    
        # Mở ảnh đầu tiên và chuyển sang hệ màu RGB (bắt buộc đối với định dạng PDF)
        first_img = Image.open(image_paths[0]).convert('RGB')
        
        # Mở các ảnh tiếp theo
        other_imgs = [Image.open(img_path).convert('RGB') for img_path in image_paths[1:]]
        
        # Lưu tất cả vào một file PDF
        first_img.save(output_pdf_path, save_all=True, append_images=other_imgs)
        print(f"✅ Đã tạo file PDF tại: {output_pdf_path}\n")
    
    
    # ==============================================================================
    # 2. CHUYỂN PDF THÀNH ẢNH (PDF to Images)
    # ==============================================================================
    def pdf_to_images(pdf_path, output_folder, dpi=200):
        """
        Chụp lại toàn bộ các trang PDF thành các file ảnh PNG.
        """
        print("▶️ Đang chuyển đổi các trang PDF thành hình ảnh...")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    
        doc = pdfium.PdfDocument(pdf_path)
        try:
            # Tỉ lệ zoom (mặc định PDF là 72 DPI, muốn 200 DPI thì scale ~ 2.77)
            scale_factor = dpi / 72
            
            for i, page in enumerate(doc):
                # Render trang thành bitmap
                bitmap = page.render(scale=scale_factor)
                try:
                    pil_img = bitmap.to_pil()
                    img_path = os.path.join(output_folder, f"trang_{i+1:03d}.png")
                    pil_img.save(img_path)
                    print(f"  > Đã xuất trang {i+1} -> {img_path}")
                finally:
                    bitmap.close()
                    page.close()
            print(f"✅ Đã hoàn thành! Ảnh được lưu tại thư mục: {output_folder}\n")
        finally:
            doc.close()
    
    
    # ==============================================================================
    # 3. BÓC TÁCH TEXT TỪ PDF (Extract Text)
    # ==============================================================================
    def extract_text_from_pdf(pdf_path, output_txt_path):
        """
        Trích xuất toàn bộ văn bản (với PDF chữ gốc) và lưu ra file .txt
        """
        print("▶️ Đang bóc tách văn bản từ PDF...")
        doc = pdfium.PdfDocument(pdf_path)
        full_text = ""
        
        try:
            for i, page in enumerate(doc):
                # Khởi tạo trang văn bản
                text_page = page.get_textpage()
                try:
                    # Lấy toàn bộ chữ trên trang hiện tại
                    page_text = text_page.get_text_bounded()
                    full_text += f"--- TRANG {i+1} ---\n{page_text}\n\n"
                finally:
                    text_page.close()
                    page.close()
                    
            with open(output_txt_path, "w", encoding="utf-8") as f:
                f.write(full_text)
            print(f"✅ Đã trích xuất văn bản vào file: {output_txt_path}\n")
        finally:
            doc.close()
    
    
    # ==============================================================================
    # 4. BÓC TÁCH HÌNH ẢNH NHÚNG TỪ PDF (Extract Embedded Images)
    # ==============================================================================
    def extract_embedded_images(pdf_path, output_folder):
        """
        Tách riêng các tệp hình ảnh gốc (logo, ảnh minh họa) được chèn bên trong PDF.
        """
        print("▶️ Đang bóc tách các hình ảnh nhúng từ PDF...")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
    
        doc = pdfium.PdfDocument(pdf_path)
        image_count = 0
        
        try:
            for page_idx, page in enumerate(doc):
                # Duyệt qua tất cả đối tượng đồ họa trên trang
                for obj in page.get_objects():
                    # Nếu đối tượng đó là một Image Object
                    if obj.get_type() == pdfium.FPDF_PAGEOBJ_IMAGE:
                        image_count += 1
                        bitmap = obj.get_bitmap()
                        try:
                            pil_img = bitmap.to_pil()
                            img_path = os.path.join(output_folder, f"anh_nhung_{image_count:03d}_trang_{page_idx+1}.png")
                            pil_img.save(img_path)
                            print(f"  > Tìm thấy ảnh nhúng: {img_path}")
                        finally:
                            bitmap.close()
                page.close()
                
            print(f"✅ Hoàn thành! Đã tách thành công {image_count} hình ảnh gốc.\n")
        finally:
            doc.close()
    
    
    # ==============================================================================
    # KHU VỰC CHẠY THỬ NGHIỆM
    # ==============================================================================
    if __name__ == "__main__":
        # Chuẩn bị file mẫu để chạy thử
        PDF_INPUT = "input.pdf"
        
        # 1. Test chuyển ảnh thành PDF
        danh_sach_anh = ["anh1.jpg", "anh2.png"]  # Tạo sẵn các file ảnh này nếu muốn test
        # images_to_pdf(danh_sach_anh, "anh_noi_thanh.pdf")
        
        # Kiểm tra nếu có file input.pdf thì chạy các hàm còn lại
        if os.path.exists(PDF_INPUT):
            # 2. Test chuyển PDF thành Ảnh trang
            pdf_to_images(PDF_INPUT, output_folder="cac_trang_anh", dpi=200)
            
            # 3. Test bóc tách văn bản
            extract_text_from_pdf(PDF_INPUT, output_txt_path="van_ban_goc.txt")
            
            # 4. Test bóc tách hình ảnh nhúng bên trong
            extract_embedded_images(PDF_INPUT, output_folder="anh_trich_xuat")
        else:
            print(f"Để chạy thử nghiệm các tính năng 2, 3, 4, vui lòng chuẩn bị sẵn file '{PDF_INPUT}'")
    

## 💡 Lưu ý quan trọng khi vận hành:

  * Hàm số 3 (Bóc tách Text): Chỉ hoạt động với PDF dạng chữ gốc (Digital PDF). Nếu file PDF của bạn là ảnh quét (Scanned PDF), văn bản xuất ra file `.txt` sẽ bị rỗng. Lúc này bạn bắt buộc phải dùng giải pháp OCR như `PaddleOCR` ở các bước trước đã hướng dẫn.
  * Hàm số 4 (Bóc tách ảnh nhúng): Khác biệt hoàn toàn với Hàm số 2. Hàm số 2 là "chụp ảnh màn hình cả trang giấy", còn hàm số 4 là "nhặt" các sticker, hình logo hoặc ảnh thẻ nguyên bản được đính bên trong trang đó ra ngoài.



Nếu bạn muốn đóng gói đoạn code này thành một công cụ dòng lệnh (CLI) bằng `click` tương tự như script cũ của bạn hoặc cần cấu hình lọc bỏ các ảnh nhúng quá nhỏ (như các đường kẻ, icon icon thừa), hãy cho tôi biết nhé!