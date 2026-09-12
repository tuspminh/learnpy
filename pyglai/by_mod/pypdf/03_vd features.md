`pypdf` thực hiện đầy đủ các tác vụ cắt (split), gộp (merge) từ file hoặc thư mục, trích xuất văn bản (text) lẫn lọc và trích xuất ảnh có kích thước lớn hơn 200 pixel từ file PDF. [1, 2, 3] 

Dưới đây là bộ source code hoàn chỉnh tích hợp toàn bộ các yêu cầu của bạn bằng thư viện `pypdf` (và `Pillow` để xử lý kích thước ảnh).

* * *

## 1\. Code tổng hợp toàn bộ tính năng

Bạn cần cài đặt các thư viện trước khi chạy:
    
    
    pip install pypdf pillow
    
    
    
    import os
    from pathlib import Path
    from pypdf import PdfReader, PdfWriter
    from PIL import Image
    
    # --- 1. SPLIT: Trích xuất một số trang cụ thể thành file PDF mới ---
    def split_pdf(input_pdf, output_pdf, pages_list):
        """
        pages_list: Danh sách số trang muốn lấy (tính từ 1, ví dụ: [1, 3, 5])
        """
        reader = PdfReader(input_pdf)
        writer = PdfWriter()
        for p in pages_list:
            idx = p - 1
            if 0 <= idx < len(reader.pages):
                writer.add_page(reader.pages[idx])
        with open(output_pdf, "wb") as f:
            writer.write(f)
        print(f"[Split] Đã lưu các trang {pages_list} vào: {output_pdf}")
    
    # --- 2. MERGE: Gộp 2 file PDF hoặc toàn bộ file PDF trong một Folder ---
    def merge_two_files(file1, file2, output_pdf):
        writer = PdfWriter()
        for f in [file1, file2]:
            writer.append(f)
        with open(output_pdf, "wb") as f:
            writer.write(f)
        print(f"[Merge 2 Files] Đã gộp thành công vào: {output_pdf}")
    
    def merge_folder_pdfs(folder_path, output_pdf):
        writer = PdfWriter()
        pdf_files = sorted(Path(folder_path).glob("*.pdf"))
        for pdf_path in pdf_files:
            reader = PdfReader(pdf_path)
            if not reader.is_encrypted:
                writer.append(pdf_path)
        with open(output_pdf, "wb") as f:
            writer.write(f)
        print(f"[Merge Folder] Đã gộp {len(pdf_files)} file từ thư mục vào: {output_pdf}")
    
    # --- 3. EXTRACT TEXT: Trích xuất text trang chỉ định hoặc toàn bộ PDF ---
    def extract_text_pdf(input_pdf, page_num=None):
        """
        page_num: Nếu là số (1, 2...), chỉ lấy text trang đó. Nếu là None, lấy toàn bộ PDF.
        """
        reader = PdfReader(input_pdf)
        if page_num is not None:
            idx = page_num - 1
            if 0 <= idx < len(reader.pages):
                return f"--- Trang {page_num} ---\n" + reader.pages[idx].extract_text()
            return "Trang không tồn tại."
        
        full_text = []
        for i, page in enumerate(reader.pages):
            full_text.append(f"--- Trang {i+1} ---\n" + page.extract_text())
        return "\n".join(full_text)
    
    # --- 4. EXTRACT IMAGES: Lọc và trích xuất ảnh lớn hơn 200px (Width hoặc Height > 200) ---
    def extract_large_images(input_pdf, output_dir, min_size=200):
        os.makedirs(output_dir, exist_ok=True)
        reader = PdfReader(input_pdf)
        count = 0
        
        for page_idx, page in enumerate(reader.pages):
            for img_idx, img_file_object in enumerate(page.images):
                # Lấy ảnh dưới dạng đối tượng PIL Image từ pypdf
                pil_img = img_file_object.image
                width, height = pil_img.size
                
                # Lọc điều kiện lớn hơn 200 pixel
                if width > min_size or height > min_size:
                    out_path = os.path.join(output_dir, f"p{page_idx+1}_img{img_idx+1}_{width}x{height}.png")
                    pil_img.save(out_path)
                    print(f"[Image] Lưu ảnh lớn: {out_path} ({width}x{height}px)")
                    count += 1
                    
        print(f"Tổng số ảnh có kích thước > {min_size}px được trích xuất: {count}")
    
    # --- VÍ DỤ SỬ DỤNG THỰC TẾ ---
    if __name__ == "__main__":
        sample_pdf = "sample.pdf"
        
        # 1. Split trang 1 và 3
        # split_pdf(sample_pdf, "split_out.pdf", [1, 3])
        
        # 2. Merge 2 file
        # merge_two_files("file1.pdf", "file2.pdf", "merged_two.pdf")
        
        # 2b. Merge cả folder chứa file pdf
        # merge_folder_pdfs("./my_pdf_folder", "merged_folder.pdf")
        
        # 3. Lấy text trang 2 hoặc toàn bộ file
        # print(extract_text_pdf(sample_pdf, page_num=2))
        
        # 4. Trích xuất ảnh kích thước > 200px
        # extract_large_images(sample_pdf, "./extracted_images", min_size=200)
    

* * *

Nếu bạn cần tối ưu thêm, tôi có thể hướng dẫn bạn cách:

  *   * Tự động nhận dạng bảng (Table) kết hợp thêm thư viện `pdfplumber` cho file cấu trúc phức tạp.
  * Xử lý bất đồng bộ hoặc đa luồng (Multithreading) khi xử lý hàng trăm file PDF nặng trong thư mục.
  * 


Bạn muốn triển khai hướng nào tiếp theo?

  


[1] [https://note.nkmk.me](https://note.nkmk.me/en/python-pypdf2-pdf-merge-insert-split/)

[2] [https://products.documentprocessing.com](https://products.documentprocessing.com/merger/python/pypdf/)

[3] [https://www.freecodecamp.org](https://www.freecodecamp.org/news/how-to-work-with-pdf-files-in-python-a-pypdf-guide/)