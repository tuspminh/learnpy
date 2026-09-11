Dưới đây là đoạn code hoàn chỉnh tích hợp toàn bộ quy trình tự động hóa: Kiểm tra loại file -> Tự động chọn giải pháp tối ưu -> Trích xuất text.

Sự kết hợp này giúp hệ thống của bạn chạy siêu nhanh với file PDF chữ (vài miligiây) và chỉ kích hoạt PaddleOCR (tốn tài nguyên hơn) khi gặp file ảnh quét.

## 🛠️ Cài đặt các thư viện cần thiết

Nếu chưa cài đặt đủ, bạn hãy chạy lệnh sau trong terminal:
    
    
    pip install pypdf paddleocr paddlepaddle pdf2image pillow
    

## 💻 Code Python Tự Động Hóa Toàn Diện
    
    
    import os
    import numpy as np
    from pypdf import PdfReader
    from pdf2image import convert_from_path
    from paddleocr import PaddleOCR
    
    def phan_biet_pdf(file_path, threshold=20):
        """
        Kiểm tra xem PDF là dạng chữ (Digital) hay dạng ảnh quét (Scanned)
        """
        try:
            reader = PdfReader(file_path)
            total_chars = 0
            pages_to_check = min(3, len(reader.pages))
            
            for i in range(pages_to_check):
                page_text = reader.pages[i].extract_text()
                if page_text:
                    total_chars += len(page_text.strip())
                    
            avg_chars = total_chars / pages_to_check
            return "scanned" if avg_chars < threshold else "digital"
        except Exception as e:
            print(f"Lỗi khi phân loại file: {e}")
            return "unknown"
    
    def trich_xuat_pdf_chu(file_path):
        """
        Trích xuất text siêu tốc từ PDF chữ bằng pypdf
        """
        print("⚡ Phát hiện PDF chữ. Đang trích xuất trực tiếp bằng pypdf...")
        reader = PdfReader(file_path)
        full_text = ""
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            full_text += f"--- TRANG {i+1} ---\n{text}\n\n"
        return full_text
    
    def ocr_pdf_quet(file_path):
        """
        Trích xuất text chuyên sâu từ PDF ảnh quét bằng PaddleOCR (Hỗ trợ Tiếng Việt)
        """
        print("🤖 Phát hiện PDF ảnh quét. Đang kích hoạt PaddleOCR (Tiếng Việt)...")
        # Khởi tạo mô hình PaddleOCR (use_gpu=True nếu máy bạn có card đồ họa NVIDIA)
        ocr = PaddleOCR(use_angle_cls=True, lang='vi', use_gpu=False, show_log=False)
        
        # Rã trang PDF thành ảnh
        pages = convert_from_path(file_path, dpi=200)
        full_text = ""
        
        for i, page_img in enumerate(pages):
            print(f"  > Đang quét trang {i+1}/{len(pages)}...")
            img_np = np.array(page_img)
            result = ocr.ocr(img_np, cls=True)
            
            page_lines = []
            if result and result[0]:
                for line in result[0]:
                    page_lines.append(line[1][0]) # Lấy chuỗi văn bản nhận diện được
                    
            page_text = "\n".join(page_lines)
            full_text += f"--- TRANG {i+1} ---\n{page_text}\n\n"
        return full_text
    
    def tu_dong_xu_ly_pdf(file_path, output_txt_path):
        """
        Hàm điều hướng chính của hệ thống
        """
        if not os.path.exists(file_path):
            print(f"❌ File không tồn tại: {file_path}")
            return
            
        # 1. Phân loại file
        loai_pdf = phan_biet_pdf(file_path)
        
        # 2. Xử lý theo từng loại cụ thể
        if loai_pdf == "digital":
            text_ket_qua = trich_xuat_pdf_chu(file_path)
        elif loai_pdf == "scanned":
            text_ket_qua = ocr_pdf_quet(file_path)
        else:
            print("❌ Không thể xác định loại file hoặc file bị lỗi.")
            return
    
        # 3. Ghi kết quả ra file txt
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(text_ket_qua)
            
        print(f"✅ Hoàn thành! Kết quả đã được lưu tại: {output_txt_path}\n")
    
    # --- CHẠY THỬ NGHIỆM ---
    if __name__ == "__main__":
        # Thay đường dẫn tới file PDF của bạn ở đây
        file_input = "tai_lieu_cua_ban.pdf" 
        file_output = "ket_qua_trich_xuat.txt"
        
        tu_dong_xu_ly_pdf(file_input, file_output)
    

## ⚙️ Điểm cộng của đoạn code này:

  1. Tiết kiệm tài nguyên: Nếu là file PDF thông thường, code chạy mất chưa tới 1 giây và không cần tải mô hình AI nặng nề của PaddleOCR lên bộ nhớ RAM.
  2. Chính xác tuyệt đối: Khi gặp file ảnh quét, `PaddleOCR` sẽ tự động sửa góc nghiêng (nhờ `use_angle_cls=True`) và quét chữ Tiếng Việt chuẩn xác.
  3. An toàn: Hàm `show_log=False` giúp ẩn các dòng log gỡ lỗi của PaddleOCR để terminal của bạn trông gọn gàng, sạch sẽ hơn.



Nếu bạn muốn nâng cấp hệ thống này lên, hãy cho tôi biết:

  * Bạn có cần quét hàng loạt file PDF trong cùng một thư mục không?
  * Bạn có muốn lưu kết quả vào file Excel thay vì file `.txt` không?