Thư viện `PyMuPDF` (được cài đặt và import thông qua tên thư viện `fitz`) là công cụ chuyển đổi trang PDF thành hình ảnh nhanh nhất hiện nay trong hệ sinh thái Python, vượt trội hơn hẳn so với `pdf2image`.

Dưới đây là đoạn code hoàn chỉnh giúp bạn chuyển toàn bộ các trang PDF thành ảnh chất lượng cao.

## 🛠️ Cài đặt thư viện

Bạn chỉ cần chạy lệnh sau trong terminal (không cần cài thêm phần mềm bên ngoài như Poppler):
    
    
    pip install pymupdf
    

## 💻 Code Python chuyển PDF thành Image
    
    
    import fitz  # PyMuPDF
    import os
    
    def pdf_to_images(pdf_path, output_folder, dpi=200):
        """
        Chuyển đổi toàn bộ các trang PDF thành hình ảnh PNG chất lượng cao.
        """
        # 1. Kiểm tra và tạo thư mục lưu ảnh nếu chưa có
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        # 2. Mở file PDF
        doc = fitz.open(pdf_path)
        print(f"Tổng số trang: {len(doc)}")
        
        # 3. Tính toán ma trận tỉ lệ (Zoom) dựa trên DPI mong muốn
        # Mặc định của PDF là 72 DPI. Để phóng to lên 200 DPI, ta nhân với tỉ lệ 200/72
        zoom = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)
        
        # 4. Lặp qua từng trang để chuyển thành ảnh
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Tạo ma trận điểm ảnh (Pix Map) với độ phân giải cao
            pix = page.get_pixmap(matrix=matrix)
            
            # Định nghĩa tên file ảnh (Ví dụ: trang_01.png, trang_02.png)
            image_name = f"trang_{page_num + 1:02d}.png"
            image_path = os.path.join(output_folder, image_name)
            
            # Lưu ảnh xuống ổ đĩa
            pix.save(image_path)
            print(f"  > Đã xuất: {image_name}")
            
        doc.close()
        print("✅ Hoàn thành chuyển đổi!")
    
    # --- CHẠY THỬ NGHIỆM ---
    if __name__ == "__main__":
        file_pdf = "tai_lieu_cua_ban.pdf"  # Đường dẫn file PDF đầu vào
        thu_muc_anh = "anh_dau_ra"         # Thư mục lưu ảnh xuất ra
        
        # DPI = 200 cho chất lượng rõ nét, phù hợp để đọc hoặc làm dữ liệu đầu vào cho OCR
        pdf_to_images(file_pdf, thu_muc_anh, dpi=200)
    

## 💡 Các mẹo cấu hình nâng cao với PyMuPDF:

  * Tăng/Giảm chất lượng ảnh (DPI):

    * `dpi=150`: Tốc độ xử lý cực nhanh, file ảnh nhẹ, thích hợp để xem trước (preview).
    * `dpi=300`: Ảnh siêu nét, phù hợp cho các tài liệu có chữ nhỏ hoặc cần mang đi in ấn.

  * Thay đổi định dạng ảnh: Bạn chỉ cần đổi đuôi file từ `.png` thành `.jpg` trong đoạn code `image_name = f"trang_{page_num + 1:02d}.jpg"`, thư viện sẽ tự động hiểu và nén ảnh sang định dạng JPEG giúp giảm dung lượng file xuống đáng kể.



Nếu bạn muốn, tôi có thể hướng dẫn bạn cách:

  * Chỉ trích xuất riêng một số trang cụ thể thay vì toàn bộ file.
  * Thay thế module `pdf2image` ở đoạn code PaddleOCR/EasyOCR phía trên bằng `PyMuPDF` để tăng tốc độ nhận diện ảnh quét lên gấp nhiều lần.



Hãy cho tôi biết bạn muốn tối ưu hệ thống theo hướng nào tiếp theo nhé!

---
# updated:

Cảnh báo này xuất hiện do từ phiên bản PyMuPDF 1.24.0 trở đi, nhà phát triển đã chính thức hỗ trợ cấu trúc import mới và khuyến nghị người dùng chuyển đổi để tránh bị lỗi trong tương lai khi họ khai tử cách viết cũ.

Để sửa cảnh báo này, bạn chỉ cần thay đổi cách `import` và cập nhật lại tên gọi class/hàm theo chuẩn mới của `pymupdf`.

Dưới đây là đoạn code đã được cập nhật chuẩn API mới nhất:
    
    
    import pymupdf  # Sử dụng trực tiếp pymupdf thay vì fitz
    import os
    
    def pdf_to_images(pdf_path, output_folder, dpi=200):
        """
        Chuyển đổi toàn bộ các trang PDF thành hình ảnh PNG bằng API mới của pymupdf
        """
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        # Thay fitz.open bằng pymupdf.open
        doc = pymupdf.open(pdf_path)
        print(f"Tổng số trang: {len(doc)}")
        
        zoom = dpi / 72
        # Thay fitz.Matrix bằng pymupdf.Matrix
        matrix = pymupdf.Matrix(zoom, zoom)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Hàm get_pixmap vẫn giữ nguyên nhưng chạy qua đối tượng của pymupdf
            pix = page.get_pixmap(matrix=matrix)
            
            image_name = f"trang_{page_num + 1:02d}.png"
            image_path = os.path.join(output_folder, image_name)
            
            pix.save(image_path)
            print(f"  > Đã xuất: {image_name}")
            
        doc.close()
        print("✅ Hoàn thành chuyển đổi!")
    
    # --- CHẠY THỬ NGHIỆM ---
    if __name__ == "__main__":
        file_pdf = "tai_lieu_cua_ban.pdf"
        thu_muc_anh = "anh_dau_ra"
        
        pdf_to_images(file_pdf, thu_muc_anh, dpi=200)
    

## 💡 Có gì thay đổi ở đây?

  1. Bạn thay thế hoàn toàn dòng chữ `import fitz` bằng `import pymupdf`.
  2. Mọi đoạn code trước đây gọi `fitz.open()` hay `fitz.Matrix()` thì nay đổi tiền tố thành `pymupdf.open()` và `pymupdf.Matrix()`.



Khi chạy đoạn code mới này, dòng cảnh báo `warning: The fitz API is deprecated...` sẽ hoàn toàn biến mất và code của bạn sẽ an toàn trước các bản cập nhật lớn tiếp theo của thư viện.

Bạn có cần tôi hỗ trợ cập nhật luôn đoạn code phân loại tự động và OCR ở phía trên sang chuẩn `import pymupdf` mới này để đồng bộ toàn bộ dự án không?